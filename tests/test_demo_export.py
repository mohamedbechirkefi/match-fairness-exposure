# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo shows the manuscript's numbers.

1. Re-running the export in memory reproduces the committed results.json byte for byte.
2. Every ``display`` and ``interval_display`` string appears verbatim in the manuscript.
   Documented exceptions: the trade-off table's rounded arm means, which are checked
   against the EXP-001 report (section 8.3) instead; the EXPOSURE_BALANCED Gini values,
   which neither document prints in full (only 0.3217 appears) and are checked as the
   four-decimal rounding of the committed arm-summary table.
3. The page's limitations are the manuscript's section 7 items.
4. The engine fixture used by the demo's vitest is what the Python engine produces now.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


export = _load("export_demo_data")
MANUSCRIPT = (ROOT / "research/paper/manuscript.md").read_text(encoding="utf-8")
REPORT1 = (ROOT / "research/experiments/EXP-001/report.md").read_text(encoding="utf-8")


def _displays(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("display", "interval_display"):
                if v is not None:
                    yield f"{path}.{k}", v
            else:
                yield from _displays(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _displays(v, f"{path}[{i}]")


def test_committed_results_json_matches_a_fresh_export() -> None:
    committed = (ROOT / "demo/public/data/results.json").read_text(encoding="utf-8")
    assert export.serialize(export.build()) == committed


def test_export_is_deterministic_and_has_no_timestamp() -> None:
    a, b = export.serialize(export.build()), export.serialize(export.build())
    assert a == b
    doc = json.loads(a)
    assert "generated" not in json.dumps(list(doc.keys()))
    assert doc["code_revision"] == json.loads(
        (ROOT / "results/confirmatory/EXP-001/run_manifest.json").read_text())["git_revision"]


def test_every_display_string_is_printed_in_the_manuscript() -> None:
    doc = export.build()
    missing = [(p, s) for p, s in _displays(doc) if s not in MANUSCRIPT]
    assert not missing, missing
    assert sum(1 for _ in _displays(doc)) >= 60


def test_tradeoff_values_match_the_report_or_the_documented_exception() -> None:
    doc = export.build()
    with open(ROOT / export.T_EXP001_ARMS, newline="") as fh:
        rows = {(export._cell_label(r["cell"])[0], r["arm"]): r for r in csv.DictReader(fh)}
    for t in doc["tradeoff"]:
        assert t["W_display"] in REPORT1, t
        if t["arm"] == "EXPOSURE_BALANCED":  # documented exception
            raw = rows[(t["cell"], t["arm"])]
            assert t["gini_B_display"] == f"{float(raw['gini_exposure_B_mean']):.4f}"
        else:
            assert t["gini_B_display"] in REPORT1, t
    assert "0.3217" in MANUSCRIPT


def test_exp003_s3_is_exported_as_not_run_with_its_own_component() -> None:
    exp3 = next(e for e in export.build()["experiments"] if e["id"] == "EXP-003")
    s3 = next(c for c in exp3["components"] if c["id"] == "S3")
    assert s3["status"].startswith("not run")
    assert "S3 not run" in exp3["status"]


def test_limitations_are_the_manuscript_section_7_items() -> None:
    for item in export.build()["limitations"]:
        assert item.split(".")[0] in MANUSCRIPT.replace("**", "")
        assert item in MANUSCRIPT.replace("**", "")


def test_every_claim_id_on_the_page_is_registered() -> None:
    with open(ROOT / "research/claims_register.csv", newline="") as fh:
        ids = {r["claim_id"] for r in csv.DictReader(fh)}
    for e in export.build()["experiments"]:
        assert set(e["claim_ids"]) <= ids, e["id"]


def test_engine_fixture_matches_the_python_engine() -> None:
    fx = _load("make_sandbox_fixture")
    committed = json.loads((ROOT / "demo/src/fixtures/engine_fixture.json").read_text())
    fresh = json.loads(json.dumps({"cases": [fx.make_case(c) for c in fx.CASES]}, allow_nan=False))
    assert committed["cases"] == fresh["cases"]


PUBLIC_TEXTS = ("README.md", "CITATION.cff", "articles/medium.md", "articles/linkedin.md", "demo/README.md")


def test_public_texts_only_use_numbers_printed_in_the_manuscript() -> None:
    import re

    pat = re.compile(r"(?<![\w.])[+-]?\d+\.\d{2,}(?![\d.])")
    bad = []
    for rel in PUBLIC_TEXTS:
        for tok in pat.findall((ROOT / rel).read_text(encoding="utf-8")):
            if tok not in MANUSCRIPT:
                bad.append((rel, tok))
    assert not bad, bad
