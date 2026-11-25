# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Export the published results for the static demo page (M5).

Writes ``demo/public/data/results.json`` in the shared demo schema
(``lab-demo-results`` 1.0.0) from committed files only: the frozen analysis tables
under ``results/``, the M4 exploratory tables, the experiment registry, the claims
register, the artifact manifest and the canonical manuscript.

Rules:
- every ``display`` and ``interval_display`` string is formatted from the committed
  table value with the rounding the manuscript uses, and the consistency test
  (``tests/test_demo_export.py``) checks that each string appears verbatim in
  ``research/paper/manuscript.md``;
- no timestamp is written, so the output is a pure function of the inputs;
- every input file is listed with its SHA-256.

Usage: ``.venv/bin/python scripts/export_demo_data.py [--check]``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

T_EXP001_POOLED = "results/confirmatory/EXP-001/report/tables/EXP-001_pooled_W.csv"
T_EXP001_CELLS = "results/confirmatory/EXP-001/report/tables/EXP-001_paired_differences_W.csv"
T_EXP001_ARMS = "results/confirmatory/EXP-001/report/tables/EXP-001_arm_summary.csv"
T_EXP002 = "results/confirmatory/EXP-002/analysis/tables/EXP-002_contrasts.csv"
T_EXP003 = "results/confirmatory/EXP-003/analysis/tables/EXP-003_sensitivity.csv"
T_PROBE = "results/exploratory/m4_horizon_probe/analysis/pooled.csv"
T_DECOMP = "results/exploratory/m4_confounders/decomposition.csv"
MANIFEST_EXP001 = "results/confirmatory/EXP-001/run_manifest.json"
MANIFEST_PROBE = "results/exploratory/m4_horizon_probe/run_manifest.json"
REGISTRY = "research/experiment_registry.csv"
CLAIMS = "research/claims_register.csv"
ARTIFACTS = "research/publication/artifact_manifest.json"
MANUSCRIPT = "research/paper/manuscript.md"

INPUTS = (
    T_EXP001_POOLED, T_EXP001_CELLS, T_EXP001_ARMS, T_EXP002, T_EXP003, T_PROBE, T_DECOMP,
    MANIFEST_EXP001, MANIFEST_PROBE, REGISTRY, CLAIMS, ARTIFACTS, MANUSCRIPT,
)

ARMS = ("RANDOM", "POPULARITY", "EXPOSURE_BALANCED")


class ExportError(RuntimeError):
    pass


def _rows(rel: str) -> list[dict[str, str]]:
    with open(ROOT / rel, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _one(rows: list[dict[str, str]], **where: str) -> dict[str, str]:
    hit = [r for r in rows if all(r.get(k) == v for k, v in where.items())]
    if len(hit) != 1:
        raise ExportError(f"expected one row for {where}, found {len(hit)}")
    return hit[0]


def _f(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, ValueError) as exc:
        raise ExportError(f"missing or non-numeric {key!r} in {row}") from exc


def s4(x: float) -> str:
    """Signed, four decimals: the manuscript's format for welfare contrasts."""
    return f"{x:+.4f}"


def s2(x: float) -> str:
    """Signed, two decimals: the manuscript's format for blocking pairs per 100 agents."""
    return f"{x:+.2f}"


def iv(lo: float, hi: float, fmt=s4) -> str:
    return f"{fmt(lo)} to {fmt(hi)}"


def est(label: str, x: float, lo: float | None, hi: float | None, level: float | None,
        unit: str, fmt=s4, *, display: str | None = None, interval: str | None = None) -> dict:
    return {
        "label": label,
        "estimate": x,
        "ci_low": lo,
        "ci_high": hi,
        "ci_level": level,
        "unit": unit,
        "display": display if display is not None else fmt(x),
        "interval_display": interval if interval is not None else (None if lo is None else iv(lo, hi, fmt)),
    }


def _cell_label(cell: str) -> tuple[str, float, float]:
    m = re.fullmatch(r"r=([\d.]+), rho=([\d.]+)", cell)
    if not m:
        raise ExportError(f"unexpected cell label {cell!r}")
    r, rho = float(m.group(1)), float(m.group(2))
    return f"r = {r:.1f}, rho = {rho:.1f}", r, rho


def _registry() -> dict[str, dict[str, str]]:
    return {r["experiment_id"]: r for r in _rows(REGISTRY)}


def _claims() -> dict[str, dict[str, str]]:
    return {r["claim_id"]: r for r in _rows(CLAIMS)}


def _claim_ids_for(claims: dict[str, dict[str, str]], prefix: str) -> list[str]:
    return sorted(cid for cid, r in claims.items() if r["result_id"].startswith(prefix))


def _limitations() -> list[str]:
    text = (ROOT / MANUSCRIPT).read_text(encoding="utf-8")
    m = re.search(r"^## 7\. Limitations and threats to validity\n(.*?)^## ", text, re.S | re.M)
    if not m:
        raise ExportError("manuscript section 7 not found")
    items = [ln[2:].strip() for ln in m.group(1).splitlines() if ln.startswith("- ")]
    if not items:
        raise ExportError("manuscript section 7 has no bullet items")
    return [i.replace("**", "") for i in items]


def _manifest_ids() -> set[str]:
    doc = json.loads((ROOT / ARTIFACTS).read_text(encoding="utf-8"))
    return {e["id"] for e in doc["entries"]}


def build() -> dict:
    reg = _registry()
    claims = _claims()
    manifest_ids = _manifest_ids()
    for cid in claims:
        if cid.startswith("C-") and cid not in manifest_ids:
            raise ExportError(f"claim {cid} has no artifact-manifest entry")

    # ---- EXP-001 -------------------------------------------------------------
    pooled = _rows(T_EXP001_POOLED)
    pop = _one(pooled, setting="base", arm="POPULARITY")
    exb = _one(pooled, setting="base", arm="EXPOSURE_BALANCED")
    exp001 = {
        "id": "EXP-001",
        "title": reg["EXP-001"]["title"],
        "role": "primary, confirmatory",
        "status": "complete: 810 of 810 runs, 0 invalid",
        "verdict": (
            f"POPULARITY: H1 supported (Holm p = {_f(pop, 'p_holm'):.4f}), but not robust to the horizon "
            "under the frozen EXP-003 criterion. EXPOSURE_BALANCED: H1 not supported; equivalent to 0 at margin 0.01."
        ),
        "estimates": [
            est("theta, POPULARITY - RANDOM (9 cells, 270 paired instances)", _f(pop, "theta"),
                _f(pop, "ci95_lo"), _f(pop, "ci95_hi"), 0.95, "welfare units"),
            est("theta, EXPOSURE_BALANCED - RANDOM (9 cells, 270 paired instances)", _f(exb, "theta"),
                _f(exb, "ci95_lo"), _f(exb, "ci95_hi"), 0.95, "welfare units"),
            est("theta, EXPOSURE_BALANCED - RANDOM, 90% CI for the equivalence test (margin 0.01)",
                _f(exb, "theta"), _f(exb, "ci90_lo"), _f(exb, "ci90_hi"), 0.90, "welfare units"),
        ],
        "claim_ids": ["C-001", "C-002", "C-008", "C-009"],
        "report_path": reg["EXP-001"]["report_location"],
        "notes": [
            f"Holm-adjusted p: POPULARITY {_f(pop, 'p_holm'):.4f} (at the floor of the 10,000-draw test), "
            f"EXPOSURE_BALANCED {_f(exb, 'p_holm'):.4f}.",
            "T = 40 rounds, pickiness theta = 0.5, slate length k = 5, n_A = 200. Primary horizon chosen by "
            "the owner after pilot values were seen (decision C4).",
        ],
        "components": [],
    }

    # ---- EXP-002 -------------------------------------------------------------
    c2 = _rows(T_EXP002)
    ha = _one(c2, contrast="H_a: W(DA_A) - W(RANDOM)", scope="pooled (equal-weight, 9 cells)")
    hb = _one(c2, contrast="H_b: block/100(MAXW) - block/100(DA_A)", scope="pooled (equal-weight, 9 cells)")
    exp002 = {
        "id": "EXP-002",
        "title": reg["EXP-002"]["title"],
        "role": "secondary, no multiplicity protection",
        "status": "complete: 810 of 810 runs, 0 invalid",
        "verdict": "H_a supported (secondary). H_b supported (secondary). DA invariant held: no blocking pair in the 540 DA_A and DA_B runs.",
        "estimates": [
            est("H_a: W(DA_A) - W(RANDOM) (9 cells, 270 paired instances)", _f(ha, "mean_diff"),
                _f(ha, "ci95_lo"), _f(ha, "ci95_hi"), 0.95, "welfare units"),
            est("H_b: blocking pairs per 100 agents, MAXW - DA_A", _f(hb, "mean_diff"),
                _f(hb, "ci95_lo"), _f(hb, "ci95_hi"), 0.95, "blocking pairs per 100 agents", fmt=s2),
        ],
        "claim_ids": _claim_ids_for(claims, "EXP-002"),
        "report_path": reg["EXP-002"]["report_location"],
        "notes": [
            "Centralized references use full preference information, so the H_a contrast mixes information and mechanism.",
            "Blocking pairs per 100 agents is a pair count, so values above 100 are possible.",
        ],
        "components": [],
    }

    # ---- EXP-003 -------------------------------------------------------------
    sens = _rows(T_EXP003)
    ref_setting = "EXP-001 base (T 40, theta 0.5), corner cells"
    settings = [
        (ref_setting, "EXP-001 reference (T 40, theta 0.5)"),
        ("S1-theta0.3", "S1, theta 0.3 (T 40)"),
        ("S1-theta0.7", "S1, theta 0.7 (T 40)"),
        ("S2-T20", "S2, T 20"),
        ("S2-T10", "S2, T 10"),
    ]
    e3 = []
    for key, label in settings:
        for arm in ("POPULARITY", "EXPOSURE_BALANCED"):
            row = _one(sens, setting=key, arm=arm)
            e3.append(est(f"{label}: {arm} - RANDOM (4 corner cells, 120 paired instances)", _f(row, "theta"),
                          _f(row, "ci95_lo"), _f(row, "ci95_hi"), 0.95, "welfare units"))
    inval = {(_r["setting"], _r["arm"]): _r["invalidates"] for _r in sens if _r["group"] == "S2"}
    if inval[("S2-T10", "POPULARITY")] != "True" or inval[("S2-T20", "POPULARITY")] != "True":
        raise ExportError("EXP-003 table no longer shows the POPULARITY invalidation")
    if "True" in (inval[("S2-T10", "EXPOSURE_BALANCED")], inval[("S2-T20", "EXPOSURE_BALANCED")]):
        raise ExportError("EXP-003 table unexpectedly invalidates EXPOSURE_BALANCED")
    if "S3 not run" not in reg["EXP-003"]["status"]:
        raise ExportError("registry no longer records EXP-003 S3 as not run")
    exp003 = {
        "id": "EXP-003",
        "title": reg["EXP-003"]["title"],
        "role": "sensitivity, registered",
        "status": "partial: S1 and S2 complete (1,440 of 1,440 runs, 0 invalid); S3 not run, a documented failure",
        "verdict": (
            "POPULARITY meets the frozen invalidation criterion at both S2 horizons: the EXP-001 POPULARITY "
            "result is not robust to the horizon. EXPOSURE_BALANCED does not meet it. The welfare-definition "
            "check (S3) was not run, so the dependence of either verdict on the welfare definition is untested."
        ),
        "estimates": e3,
        "claim_ids": _claim_ids_for(claims, "EXP-003"),
        "report_path": reg["EXP-003"]["report_location"],
        "notes": [
            "Invalidation rule (frozen): opposite sign of the EXP-001 estimate with a 95% CI excluding 0 under any S2 or S3 setting. S1 is reported but is not part of the rule.",
        ],
        "components": [
            {"id": "S1", "title": "Pickiness theta 0.3 and 0.7 at T = 40", "status": "complete",
             "verdict": "Both policies keep the EXP-001 sign; not part of the invalidation rule."},
            {"id": "S2", "title": "Horizon T = 10 and T = 20 at theta = 0.5", "status": "complete",
             "verdict": "POPULARITY reverses sign with CIs excluding 0 (not robust); EXPOSURE_BALANCED does not."},
            {"id": "S3", "title": "Reanalysis with a different welfare definition", "status": "not run (documented failure, D-018, D-019)",
             "verdict": "Not tested. The raw outputs store per-run metrics, not matchings or utilities, and the frozen text does not fix the alternative scale; no parameters were chosen after the data."},
        ],
    }

    # ---- M4 exploratory (not registered experiments) -------------------------
    probe = _rows(T_PROBE)
    p40 = _one(probe, setting="H-T40", arm="POPULARITY")
    p80 = _one(probe, setting="H-T80", arm="POPULARITY")
    b40 = _one(probe, setting="H-T40", arm="EXPOSURE_BALANCED")
    horizon = {
        "id": "M4-HORIZON",
        "title": "Horizon-extension probe (E4)",
        "role": "exploratory, not registered, designed after the S2 result",
        "status": "exploratory: 810 runs on the new seed 505, 10 instances per cell, 0 invalid",
        "verdict": "No frozen rule applies. Hypothesis-generating only; no frozen verdict changed.",
        "estimates": [
            est("POPULARITY - RANDOM at T = 40 (9 cells, 90 paired instances)", _f(p40, "theta"),
                _f(p40, "ci95_lo"), _f(p40, "ci95_hi"), 0.95, "welfare units"),
            est("POPULARITY - RANDOM at T = 80 (identical at T = 160)", _f(p80, "theta"),
                _f(p80, "ci95_lo"), _f(p80, "ci95_hi"), 0.95, "welfare units"),
            est("Delta U, POPULARITY - RANDOM at T = 80", _f(p80, "delta_U"), None, None, None,
                "share of agents"),
            est("EXPOSURE_BALANCED - RANDOM at every horizon", _f(b40, "theta"),
                _f(b40, "ci95_lo"), _f(b40, "ci95_hi"), 0.95, "welfare units"),
        ],
        "claim_ids": ["C-011"],
        "report_path": "research/paper/manuscript.md (section 5.4); journal J-0015",
        "notes": ["The analysis computed no interval for Delta U."],
        "components": [],
    }
    dec = _rows(T_DECOMP)
    d1 = _one(dec, contrast="EXP-001", setting="base", treat="POPULARITY")
    t10 = _one(dec, contrast="EXP-003", setting="S2-T10", treat="POPULARITY")
    t20 = _one(dec, contrast="EXP-003", setting="S2-T20", treat="POPULARITY")
    confounders = {
        "id": "M4-CONFOUNDERS",
        "title": "Confounder diagnostics on committed outputs (E1 to E3)",
        "role": "exploratory, not registered, computed after the confirmatory analysis",
        "status": "exploratory: derived from the committed EXP-001 and EXP-003 outputs",
        "verdict": "No frozen rule applies. No frozen verdict changed. This is not EXP-003 S3, which stays not run.",
        "estimates": [
            est("E3: mean satisfaction of matched agents Q, POPULARITY - RANDOM (EXP-001)",
                _f(d1, "delta_Q_mean_satisfaction_of_matched"), _f(d1, "Q_ci95_lo"), _f(d1, "Q_ci95_hi"),
                0.95, "satisfaction units"),
            est("E2: unmatched value v at which the S2 POPULARITY contrast changes sign, T = 10",
                _f(t10, "break_even_v"), None, None, None, "unmatched value", display=f"{_f(t10, 'break_even_v'):.2f}"),
            est("E2: unmatched value v at which the S2 POPULARITY contrast changes sign, T = 20",
                _f(t20, "break_even_v"), None, None, None, "unmatched value", display=f"{_f(t20, 'break_even_v'):.2f}"),
        ],
        "claim_ids": ["C-010", "C-012", "C-013"],
        "report_path": "research/paper/manuscript.md (section 5.4); journal J-0014",
        "notes": [
            "E1: every POPULARITY instance was still forming matches in round 40, whereas RANDOM and EXPOSURE_BALANCED had almost always stopped; the T = 40 outcome is truncated for POPULARITY.",
            "Break-even values are point values from the committed sweep; no interval exists for them.",
        ],
        "components": [],
    }

    # ---- extensions ----------------------------------------------------------
    cells_rows = _rows(T_EXP001_CELLS)
    exp001_cells = []
    for row in cells_rows:
        label, r, rho = _cell_label(row["cell"])
        x, lo, hi = _f(row, "mean_diff"), _f(row, "ci95_lo"), _f(row, "ci95_hi")
        exp001_cells.append({
            "cell": label, "r": r, "rho": rho, "arm": row["arm"],
            "estimate": x, "ci_low": lo, "ci_high": hi, "ci_level": 0.95,
            "n_pairs": int(row["n_pairs"]), "display": s4(x), "interval_display": iv(lo, hi),
        })

    arm_rows = _rows(T_EXP001_ARMS)
    tradeoff = []
    for row in arm_rows:
        if row["setting"] != "base" or row["arm"] not in ARMS:
            raise ExportError(f"unexpected arm-summary row {row['setting']} {row['arm']}")
        label, r, rho = _cell_label(row["cell"])
        tradeoff.append({
            "cell": label, "r": r, "rho": rho, "arm": row["arm"], "n_instances": int(row["n_instances"]),
            "W_mean": _f(row, "W_mean"), "W_sd": _f(row, "W_sd"),
            "gini_B_mean": _f(row, "gini_exposure_B_mean"), "gini_B_sd": _f(row, "gini_exposure_B_sd"),
            "W_display": f"{_f(row, 'W_mean'):.4f}", "gini_B_display": f"{_f(row, 'gini_exposure_B_mean'):.4f}",
        })

    rev = json.loads((ROOT / MANIFEST_EXP001).read_text(encoding="utf-8"))["git_revision"]
    rev_probe = json.loads((ROOT / MANIFEST_PROBE).read_text(encoding="utf-8"))["git_revision"]
    horizon["notes"].append(f"Run at revision {rev_probe[:7]} (exploratory).")

    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "MATCH",
        "question": "How do ranking and exposure policies alter match outcomes under heterogeneous preferences?",
        "status_label": (
            "Independent research manuscript, preprint draft, not peer-reviewed. Synthetic simulation only: "
            "no real people, profiles or platforms. Protocols frozen 2026-11-24; confirmatory runs complete; "
            "EXP-003 S3 not run (documented failure)."
        ),
        "code_revision": rev,
        "sources": [
            {"path": p, "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in INPUTS
        ],
        "experiments": [exp001, exp002, exp003, horizon, confounders],
        "assumptions": [
            {"name": "Population", "value": "Two sides; 200 agents on the short side A; B has round(r x 200) agents, imbalance r in {1.0, 1.1, 1.5}", "source": "manuscript section 3; research/protocol.md (frozen v1.0)"},
            {"name": "Utilities", "value": "u_ij = sqrt(rho) q_j + sqrt(1 - rho) e_ij with q and e standard normal; preference correlation rho in {0, 0.5, 0.9}", "source": "manuscript section 3"},
            {"name": "Satisfaction", "value": "Rank percentile of the partner in the agent's own ordering of the whole other side, in [0, 1]; an unmatched agent has satisfaction 0", "source": "manuscript section 3"},
            {"name": "Acceptability", "value": "An agent likes a candidate whose utility is at least the theta-quantile of its utilities; primary theta = 0.5", "source": "manuscript section 3"},
            {"name": "Sequential discovery", "value": "Each round every unmatched agent sees up to k = 5 unseen unmatched candidates; mutual likes resolved greedily at the end of the round; primary horizon T = 40", "source": "manuscript section 3"},
            {"name": "Policies", "value": "RANDOM (baseline); POPULARITY (smoothed like rate, one shared tie key per round); EXPOSURE_BALANCED (same score with a per-round exposure cap, delta = 0.5)", "source": "manuscript section 3; amendment F2"},
            {"name": "Centralized references", "value": "DA_A and DA_B (deferred acceptance, A or B proposing) and MAXW (welfare-maximizing assignment), all with full preference information", "source": "manuscript section 3"},
            {"name": "Primary metric", "value": "Mean agent welfare W, unitless in [0, 1]; estimand theta_P is the equal-weight mean over nine cells of the paired difference versus RANDOM", "source": "manuscript section 3"},
            {"name": "Sampling", "value": "30 market instances per cell from the root seed 20261124, common random numbers across arms", "source": "manuscript section 4.1"},
        ],
        "limitations": _limitations(),
        "exp001_cells": exp001_cells,
        "tradeoff": tradeoff,
        "tradeoff_note": (
            "Descriptive arm means over 30 instances per cell from EXP-001_arm_summary.csv (no tests). "
            "Whiskers show one standard deviation across instances, a dispersion measure, not a confidence interval. "
            "W and the RANDOM and POPULARITY Gini values are rounded as in the EXP-001 report, section 8.3. "
            "The EXPOSURE_BALANCED Gini values are rounded the same way but are not printed in the report "
            "(documented exception; the manuscript prints only 0.3217 at r = 1.5, rho = 0)."
        ),
    }


def serialize(doc: dict) -> str:
    return json.dumps(doc, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if the committed file differs")
    args = ap.parse_args(argv)
    text = serialize(build())
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("results.json up to date" if same else "results.json differs from a fresh export")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
