# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Integration: config -> runner -> validated results, manifest and CSV -> report; schema
rejections; the confirmatory gate; the CLI."""

import copy
import csv
import hashlib
import json
from pathlib import Path

import pytest

from match_lab import cli
from match_lab.config import check_protocol_frozen, config_sha256, load_config, parse_config
from match_lab.errors import MatchLabError, ProtocolNotFrozenError, SchemaError
from match_lab.report import build_report
from match_lab.runner import load_result, run_experiment
from match_lab.schema import validate_manifest, validate_result

REPO = Path(__file__).resolve().parents[1]


def tiny_raw(**over):
    raw = {"config_schema": "match-config/1.0.0", "experiment_id": "TEST", "mode": "exploratory",
           "label": "unit test", "root_seed": 5, "n_a": 6, "r_values": [1.0, 1.5], "rho_values": [0.0, 0.9],
           "instances_per_cell": 2, "arms": ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED", "DA_A", "DA_B", "MAXW"],
           "settings": [{"setting_id": "base", "theta": 0.5, "T": 4}], "k": 3, "delta": 0.5,
           "output_dir": "results/exploratory/test", "trace_memory": True}
    raw.update(over)
    return raw


def test_run_writes_valid_deterministic_outputs(tmp_path):
    cfg = parse_config(tiny_raw())
    out = run_experiment(cfg, tmp_path)
    doc = load_result(out / "results.json")
    assert len(doc["runs"]) == cfg.n_runs == 2 * 2 * 2 * 6
    assert all(r["valid"] for r in doc["runs"]) and doc["exclusions"] == []
    assert doc["config_sha256"] == config_sha256(cfg.raw)
    man = json.loads((out / "run_manifest.json").read_text())
    validate_manifest(man)
    assert man["n_runs"] == cfg.n_runs and man["root_seed"] == 5
    # peak memory is traced on a re-run of instance 0 only; timing is never traced
    peaks = {r["instance"]: r["diagnostics"]["peak_traced_bytes"] for r in doc["runs"]}
    assert all(r["diagnostics"]["peak_traced_bytes"] is not None for r in doc["runs"] if r["instance"] == 0)
    assert all(r["diagnostics"]["peak_traced_bytes"] is None for r in doc["runs"] if r["instance"] > 0)
    assert peaks
    with open(out / "metrics.csv") as fh:
        assert len(list(csv.DictReader(fh))) == cfg.n_runs
    # DA arms never have blocking pairs; arms share instances (same n_b in a cell)
    assert all(r["metrics"]["blocking_pairs"] == 0 for r in doc["runs"] if r["arm"].startswith("DA"))
    # determinism: a second run reproduces every metric exactly
    out2 = run_experiment(parse_config(tiny_raw(output_dir="results/exploratory/test2")), tmp_path)
    doc2 = load_result(out2 / "results.json")
    assert [r["metrics"] for r in doc["runs"]] == [r["metrics"] for r in doc2["runs"]]
    with pytest.raises(MatchLabError):
        run_experiment(cfg, tmp_path)  # refuses to overwrite raw results


def test_report_exploratory_has_banner_and_no_pvalues(tmp_path):
    cfg = parse_config(tiny_raw())
    out = run_experiment(cfg, tmp_path)
    plan = parse_config(tiny_raw(instances_per_cell=30))
    info = build_report([out / "results.json"], tmp_path / "rep", plans=[plan], pdf=False, repo_root=tmp_path)
    md = Path(info["markdown"]).read_text()
    assert "EXPLORATORY. Not a finding." in md
    assert "Projected runtime" in md
    with open(tmp_path / "rep" / "tables" / "TEST_pooled_W.csv") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all(r["p_signflip"] == "" and r["p_holm"] == "" for r in rows)
    svgs = list((tmp_path / "rep" / "figures").glob("*.svg"))
    assert len(svgs) == 2 and all("<desc>" in s.read_text() for s in svgs)


def test_schema_rejects_malformed(tmp_path):
    out = run_experiment(parse_config(tiny_raw(arms=["RANDOM", "DA_A"], instances_per_cell=1)), tmp_path)
    good = json.loads((out / "results.json").read_text())
    validate_result(good)
    mutations = [
        lambda d: d.update(schema_version="match-result/0.9"),
        lambda d: d.pop("runs"),
        lambda d: d["runs"][0]["metrics"].update(W=float("nan")),
        lambda d: d["runs"][0]["metrics"].pop("W"),
        lambda d: d["runs"][0].update(valid=False),
        lambda d: d["runs"].append(copy.deepcopy(d["runs"][0])),
        lambda d: d["runs"][0].update(arm="GREEDY"),
        lambda d: d.update(config_sha256="abc"),
        lambda d: d.update(mode="confirmatory"),
        lambda d: d["runs"][0]["diagnostics"].update(runtime_s=-1.0),
    ]
    for mutate in mutations:
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(SchemaError):
            validate_result(bad)
    p = tmp_path / "bad.json"
    bad = copy.deepcopy(good)
    bad["runs"][0]["metrics"]["W"] = "high"
    p.write_text(json.dumps(bad))
    with pytest.raises(SchemaError):
        load_result(p)  # fails closed at import


@pytest.mark.parametrize("over", [
    dict(config_schema="match-config/0.1"), dict(mode="pilot"), dict(root_seed=-1), dict(n_a=-2),
    dict(r_values=[]), dict(rho_values=[0.5, 0.5]), dict(arms=["GREEDY"]), dict(settings=[]),
    dict(settings=[{"setting_id": "x", "theta": 0.5}]), dict(k=0), dict(delta=-1),
    dict(output_dir="results/confirmatory/x"), dict(trace_memory="yes"), dict(n_a=True),
    dict(popularity_tie_scope="row"),
])
def test_config_rejects_invalid(over):
    with pytest.raises(SchemaError):
        parse_config(tiny_raw(**over))


def test_confirmatory_output_cannot_be_exploratory_dir():
    with pytest.raises(SchemaError):
        parse_config(tiny_raw(mode="confirmatory", output_dir="results/exploratory/x"))


def test_confirmatory_refused_while_protocol_unfrozen():
    for exp in ("EXP-001", "EXP-002", "EXP-003"):
        cfg = load_config(REPO / "experiments" / "configs" / f"{exp}.json")
        assert cfg.mode == "confirmatory"
        with pytest.raises(ProtocolNotFrozenError):
            run_experiment(cfg, REPO)
    assert not (REPO / "results" / "confirmatory").exists()


def test_freeze_check_accepts_matching_hash_and_rejects_drift(tmp_path):
    (tmp_path / "research" / "experiments" / "EXP-009").mkdir(parents=True)
    proto = tmp_path / "research" / "experiments" / "EXP-009" / "protocol.md"
    proto.write_text("frozen text\n")
    h = hashlib.sha256(proto.read_bytes()).hexdigest()
    reg = tmp_path / "research" / "experiment_registry.csv"
    reg.write_text("experiment_id,protocol_path,protocol_hash\n"
                   f"EXP-009,research/experiments/EXP-009/protocol.md,{h}\n"
                   "EXP-010,research/experiments/EXP-009/protocol.md,not frozen\n")
    assert check_protocol_frozen("EXP-009", tmp_path) == h
    with pytest.raises(ProtocolNotFrozenError):
        check_protocol_frozen("EXP-010", tmp_path)
    with pytest.raises(ProtocolNotFrozenError):
        check_protocol_frozen("EXP-404", tmp_path)
    proto.write_text("edited after freeze\n")
    with pytest.raises(ProtocolNotFrozenError):
        check_protocol_frozen("EXP-009", tmp_path)


def test_cli_run_refuses_confirmatory(capsys):
    assert cli.main(["run", "--config", "experiments/configs/EXP-001.json"]) == 3
    assert "REFUSED" in capsys.readouterr().err


def test_empty_pool_config_runs(tmp_path):
    cfg = parse_config(tiny_raw(n_a=0, instances_per_cell=1))
    doc = load_result(run_experiment(cfg, tmp_path) / "results.json")
    assert all(r["valid"] and r["metrics"]["W"] is None for r in doc["runs"])
