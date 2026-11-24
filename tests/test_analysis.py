# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Frozen EXP-002 and EXP-003 analyses (written before any confirmatory output, session M3)."""

import json

import pytest

from match_lab import cli
from match_lab.analysis import exp002_analysis, exp003_analysis, paired_contrast, write_analysis
from match_lab.config import parse_config
from match_lab.runner import load_result, run_experiment

from test_pipeline import tiny_raw


def _run(eid, sid_T, arms, cells, w, block=0, excl=()):
    """Fake run with only the fields the analysis reads."""
    r, rho = cells
    return {"instance_key": f"r{r:g}-rho{rho:g}-i{sid_T[2]:03d}-{sid_T[0]}", "arm": arms,
            "cell": {"r": r, "rho": rho}, "setting": {"setting_id": sid_T[0], "T": sid_T[1]},
            "metrics": {"W": w, "blocking_pairs": block, "blocking_per_100": float(block),
                        "U": 0.1, "U_A": 0.1, "U_B": 0.1, "W_A": w, "W_B": w}}


def _doc(eid, runs, excl=()):
    return {"experiment_id": eid, "config": {"root_seed": 7}, "runs": runs,
            "exclusions": [{"instance_key": k, "reason": "test"} for k in excl]}


def test_paired_contrast_hand_values():
    import numpy as np
    res = paired_contrast({"a": [1.0, 1.0], "b": [3.0, 3.0]}, np.random.default_rng(0))
    assert res["pooled"]["estimate"] == pytest.approx(2.0)
    assert res["pooled"]["ci95_lo"] == pytest.approx(2.0) and res["pooled"]["ci_excludes_0"]
    assert [c["mean_diff"] for c in res["cells"]] == [1.0, 3.0]


def test_exp002_merges_random_and_drops_exclusions():
    d1 = _doc("EXP-001", [_run("", ("base", 40, i), "RANDOM", (1.0, 0.0), 0.5) for i in range(3)],
              excl=["r1-rho0-i002-base"])
    d2 = _doc("EXP-002", [_run("", ("base", 40, i), a, (1.0, 0.0), w, b) for i in range(3)
                          for a, w, b in (("DA_A", 0.7, 0), ("DA_B", 0.6, 0), ("MAXW", 0.8, 4))])
    res = exp002_analysis(d1, d2)
    h_a = res["H_a_W_DA_A_minus_RANDOM"]["pooled"]
    assert h_a["n_pairs"] == 2 and h_a["estimate"] == pytest.approx(0.2)
    assert res["H_b_block100_MAXW_minus_DA_A"]["pooled"]["estimate"] == pytest.approx(4.0)
    assert res["invariant_instances_with_DA_blocking_pairs"] == {"DA_A": 0, "DA_B": 0}
    with pytest.raises(ValueError):
        exp002_analysis(d2, d1)


def test_exp003_invalidation_rule():
    cells = [(1.0, 0.0), (1.0, 0.9), (1.5, 0.0), (1.5, 0.9), (1.1, 0.5)]
    r1 = []
    for c in cells:
        for i in range(3):
            r1 += [_run("", ("base", 40, i), "RANDOM", c, 0.5), _run("", ("base", 40, i), "POPULARITY", c, 0.52 + 0.001 * i),
                   _run("", ("base", 40, i), "EXPOSURE_BALANCED", c, 0.49 - 0.001 * i)]
    r3 = []
    for c in cells[:4]:
        for i in range(3):
            for sid, T, dp, de in (("S2-T10", 10, -0.1, -0.01), ("S1-theta0.3", 40, -0.1, 0.0)):
                r3 += [_run("", (sid, T, i), "RANDOM", c, 0.5), _run("", (sid, T, i), "POPULARITY", c, 0.5 + dp + 0.001 * i),
                       _run("", (sid, T, i), "EXPOSURE_BALANCED", c, 0.5 + de + 0.001 * i)]
    res = exp003_analysis(_doc("EXP-001", r1), _doc("EXP-003", r3))
    assert res["exp001_reference_9_cells"]["POPULARITY"]["n_cells"] == 5
    by = {(r["setting"], r["arm"]): r for r in res["rows"]}
    assert by[("S2-T10", "POPULARITY")]["invalidates"] is True
    assert by[("S1-theta0.3", "POPULARITY")]["invalidates"] is None  # S1 is not a criterion
    assert by[("S1-theta0.3", "POPULARITY")]["opposite_sign_ci_excludes_0"] is True
    assert by[("S2-T10", "EXPOSURE_BALANCED")]["invalidates"] is False  # same sign as EXP-001
    assert res["verdict_by_arm"]["POPULARITY"].startswith("not robust")
    assert by[("EXP-001 base (T 40, theta 0.5), corner cells", "POPULARITY")]["n_cells"] == 4


def test_analyze_end_to_end(tmp_path):
    base = dict(r_values=[1.0, 1.5], rho_values=[0.0, 0.9])
    docs = {}
    for eid, arms, settings in (
            ("EXP-001", ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"], [{"setting_id": "base", "theta": 0.5, "T": 4}]),
            ("EXP-002", ["DA_A", "DA_B", "MAXW"], [{"setting_id": "base", "theta": 0.5, "T": 4}]),
            ("EXP-003", ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"], [{"setting_id": "S2-T10", "theta": 0.5, "T": 2}])):
        cfg = parse_config(tiny_raw(experiment_id=eid, arms=arms, settings=settings,
                                    output_dir=f"results/exploratory/{eid}", **base))
        docs[eid] = run_experiment(cfg, tmp_path) / "results.json"
    for eid in ("EXP-002", "EXP-003"):
        assert cli.main(["analyze", "--experiment", eid, "--exp001", str(docs["EXP-001"]),
                         "--results", str(docs[eid]), "--out", str(tmp_path / eid)]) == 0
        js = json.loads((tmp_path / eid / f"{eid}_analysis.json").read_text())
        assert js and list((tmp_path / eid / "figures").glob("*.svg"))
    res = exp002_analysis(load_result(docs["EXP-001"]), load_result(docs["EXP-002"]))
    assert res["invariant_instances_with_DA_blocking_pairs"] == {"DA_A": 0, "DA_B": 0}
    assert res["H_a_W_DA_A_minus_RANDOM"]["pooled"]["n_cells"] == 4
