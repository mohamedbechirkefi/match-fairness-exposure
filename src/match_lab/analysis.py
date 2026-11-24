# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Cross-experiment analyses fixed by the frozen protocols (EXP-002 and EXP-003).

Written in session M3 before any confirmatory output existed; it implements only what the
frozen protocols specify and adds no new test:

- EXP-002 (protocol sections 4 and 12): the secondary contrasts H_a (W of DA_A minus W of the
  EXP-001 RANDOM arm on the same instance) and H_b (blocking pairs per 100 agents of MAXW minus
  DA_A), each as an equal-weight mean over the 9 cells with a 95% stratified paired bootstrap CI
  (10,000 resamples); "not supported" when the CI contains 0. The invariant B = 0 for DA_A and
  DA_B. Descriptive per-cell tables: W, U and W by side for DA_A, DA_B, MAXW and RANDOM.
- EXP-003 (protocol section 4): theta_P(s) on the 4 corner cells per setting with a 95%
  stratified bootstrap CI, and the invalidation criterion: opposite sign to the EXP-001
  estimate with a 95% CI excluding 0, for any setting of S2 (S3 is not covered here).

No p-value is computed: protocol section 8 limits tests to the EXP-001 family.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .report import REPORT_SEED, _cell_label
from .stats import bootstrap_ci, mean_sd_dz, stratified_bootstrap_ci, stratified_mean

N_RESAMPLES = 10_000
CORNER_CELLS = ("r=1, rho=0", "r=1, rho=0.9", "r=1.5, rho=0", "r=1.5, rho=0.9")


def _valid_index(doc: dict, excluded: set[str]) -> dict[str, dict[str, dict]]:
    """instance_key -> arm -> run, dropping instances excluded in any contributing document."""
    idx: dict[str, dict[str, dict]] = defaultdict(dict)
    for run in doc["runs"]:
        if run["instance_key"] not in excluded:
            idx[run["instance_key"]][run["arm"]] = run
    return idx


def _excluded(*docs: dict) -> set[str]:
    return {e["instance_key"] for d in docs for e in d["exclusions"]}


def paired_contrast(pairs_by_cell: dict[str, list[float]], rng: np.random.Generator) -> dict:
    """Per-cell rows and the pooled (equal-weight) contrast with a stratified bootstrap CI."""
    cells = []
    for cell, d in sorted(pairs_by_cell.items()):
        m, sd, dz = mean_sd_dz(d)
        lo, hi = bootstrap_ci(d, n_resamples=N_RESAMPLES, rng=rng)
        cells.append({"cell": cell, "n_pairs": len(d), "mean_diff": m, "sd_diff": sd, "dz": dz,
                      "ci95_lo": lo, "ci95_hi": hi, "values": list(d)})
    lo, hi = stratified_bootstrap_ci(pairs_by_cell, n_resamples=N_RESAMPLES, rng=rng)
    pooled = {"n_cells": len(pairs_by_cell), "n_pairs": sum(len(v) for v in pairs_by_cell.values()),
              "estimate": stratified_mean(pairs_by_cell), "ci95_lo": lo, "ci95_hi": hi,
              "ci_excludes_0": bool(lo > 0 or hi < 0)}
    return {"cells": cells, "pooled": pooled}


def _diffs(idx, treat: str, base: str, metric: str) -> dict[str, list[float]]:
    by: dict[str, list[float]] = defaultdict(list)
    for key in sorted(idx):
        arms = idx[key]
        if treat in arms and base in arms:
            a, b = arms[treat]["metrics"][metric], arms[base]["metrics"][metric]
            if a is not None and b is not None:
                by[_cell_label(arms[treat])].append(a - b)
    return dict(by)


def exp002_analysis(doc001: dict, doc002: dict) -> dict:
    """Frozen EXP-002 analysis on the merged EXP-001 RANDOM arm and the EXP-002 arms."""
    if doc001["experiment_id"] != "EXP-001" or doc002["experiment_id"] != "EXP-002":
        raise ValueError("need the EXP-001 and EXP-002 result documents")
    if doc001["config"]["root_seed"] != doc002["config"]["root_seed"]:
        raise ValueError("EXP-002 must share the EXP-001 root seed (same instances)")
    excluded = _excluded(doc001, doc002)
    idx = _valid_index(doc002, excluded)
    for key, arms in _valid_index(doc001, excluded).items():
        if "RANDOM" in arms:
            idx[key]["RANDOM"] = arms["RANDOM"]
    rng = np.random.default_rng(REPORT_SEED + 2)
    h_a = paired_contrast(_diffs(idx, "DA_A", "RANDOM", "W"), rng)
    h_b = paired_contrast(_diffs(idx, "MAXW", "DA_A", "blocking_per_100"), rng)
    invariant = {arm: sum(1 for arms in idx.values() if arm in arms and arms[arm]["metrics"]["blocking_pairs"])
                 for arm in ("DA_A", "DA_B")}
    descriptive = []
    by_cell_arm: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for arms in idx.values():
        for arm, run in arms.items():
            by_cell_arm[(_cell_label(run), arm)].append(run["metrics"])
    for (cell, arm), ms in sorted(by_cell_arm.items()):
        row = {"cell": cell, "arm": arm, "n_instances": len(ms)}
        for name in ("W", "U", "U_A", "U_B", "W_A", "W_B", "blocking_per_100"):
            xs = [m[name] for m in ms if m[name] is not None]
            row[f"{name}_mean"] = float(np.mean(xs)) if xs else None
        row["side_gap_W_A_minus_W_B"] = (row["W_A_mean"] - row["W_B_mean"]
                                         if row["W_A_mean"] is not None and row["W_B_mean"] is not None else None)
        descriptive.append(row)
    return {"H_a_W_DA_A_minus_RANDOM": h_a, "H_b_block100_MAXW_minus_DA_A": h_b,
            "invariant_instances_with_DA_blocking_pairs": invariant,
            "excluded_instances": sorted(excluded), "descriptive": descriptive}


def _theta_by_setting(doc: dict, excluded: set[str], cells: tuple[str, ...] | None) -> dict:
    idx = _valid_index(doc, excluded)
    out: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for key in sorted(idx):
        arms = idx[key]
        if "RANDOM" not in arms:
            continue
        base = arms["RANDOM"]
        cell = _cell_label(base)
        if cells is not None and cell not in cells:
            continue
        for arm in ("POPULARITY", "EXPOSURE_BALANCED"):
            if arm in arms and arms[arm]["metrics"]["W"] is not None and base["metrics"]["W"] is not None:
                out[(base["setting"]["setting_id"], arm)][cell].append(arms[arm]["metrics"]["W"] - base["metrics"]["W"])
    return {k: dict(v) for k, v in out.items()}


def exp003_analysis(doc001: dict, doc003: dict) -> dict:
    """Frozen EXP-003 analysis for the S1 and S2 settings (S3 is not covered)."""
    if doc001["experiment_id"] != "EXP-001" or doc003["experiment_id"] != "EXP-003":
        raise ValueError("need the EXP-001 and EXP-003 result documents")
    if doc001["config"]["root_seed"] != doc003["config"]["root_seed"]:
        raise ValueError("EXP-003 must share the EXP-001 root seed (same instances)")
    rng = np.random.default_rng(REPORT_SEED + 3)
    ref_all = _theta_by_setting(doc001, _excluded(doc001), None)
    reference = {}
    for (sid, arm), cells in sorted(ref_all.items()):
        lo, hi = stratified_bootstrap_ci(cells, n_resamples=N_RESAMPLES, rng=rng)
        reference[arm] = {"setting": sid, "n_cells": len(cells), "theta": stratified_mean(cells),
                          "ci95_lo": lo, "ci95_hi": hi}
    rows = []
    corner_ref = _theta_by_setting(doc001, _excluded(doc001), CORNER_CELLS)
    for (sid, arm), cells in sorted(corner_ref.items()):
        lo, hi = stratified_bootstrap_ci(cells, n_resamples=N_RESAMPLES, rng=rng)
        rows.append({"setting": "EXP-001 base (T 40, theta 0.5), corner cells", "group": "reference",
                     "arm": arm, "n_cells": len(cells), "n_pairs": sum(map(len, cells.values())),
                     "theta": stratified_mean(cells), "ci95_lo": lo, "ci95_hi": hi,
                     "exp001_sign": None, "opposite_sign_ci_excludes_0": None, "invalidates": None})
    for (sid, arm), cells in sorted(_theta_by_setting(doc003, _excluded(doc003), CORNER_CELLS).items()):
        lo, hi = stratified_bootstrap_ci(cells, n_resamples=N_RESAMPLES, rng=rng)
        theta = stratified_mean(cells)
        ref_sign = int(np.sign(reference[arm]["theta"])) if arm in reference else 0
        opposite = bool(ref_sign != 0 and ((ref_sign > 0 and hi < 0) or (ref_sign < 0 and lo > 0)))
        group = "S2" if sid.startswith("S2") else "S1" if sid.startswith("S1") else "other"
        rows.append({"setting": sid, "group": group, "arm": arm, "n_cells": len(cells),
                     "n_pairs": sum(map(len, cells.values())), "theta": theta, "ci95_lo": lo, "ci95_hi": hi,
                     "exp001_sign": ref_sign, "opposite_sign_ci_excludes_0": opposite,
                     # the frozen criterion covers S2 and S3 only; S1 is reported, not a criterion
                     "invalidates": opposite if group == "S2" else None})
    verdict = {arm: ("not robust (S2 invalidation criterion met)"
                     if any(r["invalidates"] for r in rows if r["arm"] == arm)
                     else "S2 criterion not met; S3 not executed")
               for arm in ("POPULARITY", "EXPOSURE_BALANCED")}
    return {"exp001_reference_9_cells": reference, "rows": rows, "verdict_by_arm": verdict,
            "excluded_instances": sorted(_excluded(doc003))}


# ---------------------------------------------------------------- output (tables, figure, Markdown)

def _strip_values(obj):
    if isinstance(obj, dict):
        return {k: _strip_values(v) for k, v in obj.items() if k != "values"}
    if isinstance(obj, list):
        return [_strip_values(v) for v in obj]
    return obj


def fig_forest(rows: list[dict], title: str, xlabel: str) -> str:
    """Forest plot: one row per estimate with its 95% CI; dashed line at 0."""
    import html as _html

    from .report import _svg

    ext = max(1e-3, max(max(abs(r["ci95_lo"]), abs(r["ci95_hi"]), abs(r["est"])) for r in rows)) * 1.1
    left, right, row_h = 330, 650, 18
    xs = lambda v: left + (v + ext) / (2 * ext) * (right - left)  # noqa: E731
    height = 70 + len(rows) * row_h
    body = [f'<line x1="{xs(0):.1f}" x2="{xs(0):.1f}" y1="20" y2="{height - 45}" stroke="#999" stroke-dasharray="3,3"/>']
    y = 30
    for r in rows:
        body.append(f'<text x="8" y="{y + 4}">{_html.escape(r["label"])}</text>'
                    f'<line x1="{xs(r["ci95_lo"]):.1f}" x2="{xs(r["ci95_hi"]):.1f}" y1="{y}" y2="{y}" stroke="#2f6fb5" stroke-width="2"/>'
                    f'<circle cx="{xs(r["est"]):.1f}" cy="{y}" r="3.5" fill="#2f6fb5"/>')
        y += row_h
    ya = y + 2
    body.append(f'<line x1="{left}" x2="{right}" y1="{ya}" y2="{ya}" stroke="#000"/>')
    for t in np.linspace(-ext, ext, 5):
        body.append(f'<line x1="{xs(t):.1f}" x2="{xs(t):.1f}" y1="{ya}" y2="{ya + 4}" stroke="#000"/>'
                    f'<text x="{xs(t):.1f}" y="{ya + 16}" text-anchor="middle">{t:+.3f}</text>')
    body.append(f'<text x="{(left + right) / 2}" y="{ya + 32}" text-anchor="middle">{_html.escape(xlabel)}</text>')
    return _svg(660, int(ya + 45), body, title, title + ". Dot = estimate, bar = 95% bootstrap CI over market instances.")


def write_analysis(kind: str, doc001: dict, other: dict, out_dir) -> dict:
    """Run the frozen EXP-002 or EXP-003 analysis and write JSON, CSV, an SVG and a Markdown summary."""
    import csv
    import json
    from pathlib import Path

    out = Path(out_dir)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    if kind == "EXP-002":
        res = exp002_analysis(doc001, other)
        rows = []
        for name, key in (("H_a: W(DA_A) - W(RANDOM)", "H_a_W_DA_A_minus_RANDOM"),
                          ("H_b: block/100(MAXW) - block/100(DA_A)", "H_b_block100_MAXW_minus_DA_A")):
            c = res[key]
            for cell in c["cells"]:
                rows.append({"contrast": name, "scope": cell["cell"], **{k: v for k, v in cell.items() if k not in ("cell", "values")}})
            rows.append({"contrast": name, "scope": "pooled (equal-weight, 9 cells)", "n_pairs": c["pooled"]["n_pairs"],
                         "mean_diff": c["pooled"]["estimate"], "ci95_lo": c["pooled"]["ci95_lo"],
                         "ci95_hi": c["pooled"]["ci95_hi"], "ci_excludes_0": c["pooled"]["ci_excludes_0"]})
        tables = {"EXP-002_contrasts.csv": rows, "EXP-002_descriptive.csv": res["descriptive"]}
        figs = {}
        for key, xl in (("H_a_W_DA_A_minus_RANDOM", "W(DA_A) - W(RANDOM), welfare units"),
                        ("H_b_block100_MAXW_minus_DA_A", "Blocking pairs per 100 agents, MAXW - DA_A")):
            c = res[key]
            fr = [{"label": x["cell"], "est": x["mean_diff"], "ci95_lo": x["ci95_lo"], "ci95_hi": x["ci95_hi"]} for x in c["cells"]]
            fr.append({"label": "pooled (equal-weight)", "est": c["pooled"]["estimate"],
                       "ci95_lo": c["pooled"]["ci95_lo"], "ci95_hi": c["pooled"]["ci95_hi"]})
            figs[f"FIG-EXP-002-{key.split('_')[0]}{key.split('_')[1]}-forest.svg"] = fig_forest(fr, f"EXP-002 {key}", xl)
    elif kind == "EXP-003":
        res = exp003_analysis(doc001, other)
        tables = {"EXP-003_sensitivity.csv": res["rows"],
                  "EXP-003_exp001_reference.csv": [{"arm": a, **v} for a, v in res["exp001_reference_9_cells"].items()]}
        fr = [{"label": f"{r['arm'][:3]} {r['setting'][:28]}", "est": r["theta"], "ci95_lo": r["ci95_lo"],
               "ci95_hi": r["ci95_hi"]} for r in res["rows"]]
        figs = {"FIG-EXP-003-theta-forest.svg": fig_forest(fr, "EXP-003 theta_P by setting (corner cells)",
                                                           "theta_P: W(P) - W(RANDOM), equal-weight mean over 4 corner cells")}
    else:
        raise ValueError("kind must be EXP-002 or EXP-003")
    (out / f"{kind}_analysis.json").write_text(json.dumps(_strip_values(res), indent=1, sort_keys=True) + "\n")
    for name, trs in tables.items():
        keys: list[str] = []
        for r in trs:
            keys += [k for k in r if k not in keys and k != "values"]
        with open(out / "tables" / name, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for r in trs:
                w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})
    for name, svg in figs.items():
        (out / "figures" / name).write_text(svg, encoding="utf-8")
    return {"analysis": str(out / f"{kind}_analysis.json"), "tables": sorted(tables), "figures": sorted(figs)}
