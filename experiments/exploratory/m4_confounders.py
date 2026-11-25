# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""M4 EXPLORATORY confounder checks on committed confirmatory outputs (journal J-0014).

This script runs no simulation. It reads the committed result documents of EXP-001, EXP-002 and
EXP-003 and derives three exploratory diagnostics. None of them is part of a frozen protocol,
none tests a hypothesis, and none changes or replaces a frozen verdict.

E1  Horizon saturation. From the per-run ``matches_by_round`` diagnostic: for each experiment,
    setting, cell and arm, the share of instances with at least one new match in the last
    10 rounds of the horizon, and the share of final matches formed in those rounds. It asks
    whether the T = 40 outcomes are close to final allocations or still truncated.

E2  Unmatched-value sweep. W counts an unmatched agent as 0. Because U is the unmatched share of
    all agents, the welfare with a constant unmatched value v is exactly W(v) = W + v * U, so
    theta_P(v) = theta_P(0) + v * Delta U. The script reports theta_P(v) over the whole feasible
    range v in {0, 0.25, 0.5, 0.75, 1} with stratified bootstrap CIs, and the break-even value
    v* at which the point estimate would change sign. It is NOT EXP-003 S3: S3 is recorded as
    not run (D-019) and its parameters are not chosen here; the sweep covers the range instead
    of choosing a value, and it uses one constant v for every agent.

E3  Match-quality decomposition. W = (1 - U) * Q, where Q = W / (1 - U) is the mean satisfaction
    of matched agents. Paired differences in Q and in the matched share (1 - U) separate
    "matches more agents" from "matches agents better".

Usage (from the repository root):
    .venv/bin/python experiments/exploratory/m4_confounders.py --out results/exploratory/m4_confounders
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from match_lab.stats import stratified_bootstrap_ci, stratified_mean

SEED = 20261125  # exploratory analysis seed (M4 session date); unrelated to any run seed
N_RESAMPLES = 10_000
V_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
LAST_ROUNDS = 10
CORNER = {(1.0, 0.0), (1.0, 0.9), (1.5, 0.0), (1.5, 0.9)}


def _load(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _cell(run: dict) -> str:
    return f"r={run['cell']['r']:g}, rho={run['cell']['rho']:g}"


def _index(doc: dict) -> dict:
    """(setting_id, instance_key) -> arm -> run (valid, non-excluded runs only)."""
    excluded = {e["instance_key"] for e in doc["exclusions"]}
    idx: dict = defaultdict(dict)
    for run in doc["runs"]:
        if run["valid"] and run["instance_key"] not in excluded:
            idx[(run["setting"]["setting_id"], run["instance"], _cell(run))][run["arm"]] = run
    return idx


# ----------------------------------------------------------------------------- E1

def horizon_saturation(docs: dict[str, dict]) -> list[dict]:
    rows = []
    for exp_id, doc in docs.items():
        groups: dict = defaultdict(list)
        for run in doc["runs"]:
            mbr = run["diagnostics"].get("matches_by_round")
            if mbr is None:
                continue  # centralized arms have no rounds
            groups[(run["setting"]["setting_id"], run["setting"]["T"], _cell(run), run["arm"])].append(mbr)
        for (sid, T, cell, arm), lists in sorted(groups.items()):
            late_any = [1.0 if sum(m[-LAST_ROUNDS:]) > 0 else 0.0 for m in lists]
            late_share = [sum(m[-LAST_ROUNDS:]) / sum(m) if sum(m) else 0.0 for m in lists]
            last_round = [max((i + 1 for i, x in enumerate(m) if x > 0), default=0) for m in lists]
            rows.append({"experiment": exp_id, "setting": sid, "T": T, "cell": cell, "arm": arm,
                         "n_instances": len(lists),
                         "share_instances_with_match_in_last_10_rounds": float(np.mean(late_any)),
                         "mean_share_of_matches_in_last_10_rounds": float(np.mean(late_share)),
                         "mean_last_round_with_a_match": float(np.mean(last_round)),
                         "max_last_round_with_a_match": int(max(last_round))})
    return rows


# ----------------------------------------------------------------------------- E2 and E3

def _paired(idx: dict, setting: str, treat: str, base: str, fn, cells=None) -> dict[str, list[float]]:
    by: dict[str, list[float]] = defaultdict(list)
    for (sid, _inst, cell), arms in sorted(idx.items()):
        if sid != setting or treat not in arms or base not in arms:
            continue
        rb = arms[base]
        if cells is not None and (rb["cell"]["r"], rb["cell"]["rho"]) not in cells:
            continue
        by[cell].append(fn(arms[treat]["metrics"]) - fn(rb["metrics"]))
    return dict(by)


def _ci(by: dict, rng, level: float) -> tuple[float, float]:
    return stratified_bootstrap_ci(by, n_resamples=N_RESAMPLES, level=level, rng=rng)


def contrasts(idx: dict, label: str, setting: str, treat: str, base: str, cells, rng) -> tuple[list, dict]:
    sweep = []
    for v in V_GRID:
        by = _paired(idx, setting, treat, base, lambda m, v=v: m["W"] + v * m["U"], cells)
        lo, hi = _ci(by, rng, 0.95)
        lo90, hi90 = _ci(by, rng, 0.90)
        sweep.append({"contrast": label, "setting": setting, "treat": treat, "base": base,
                      "n_cells": len(by), "n_pairs": sum(map(len, by.values())), "v": v,
                      "theta_v": stratified_mean(by), "ci95_lo": lo, "ci95_hi": hi,
                      "ci90_lo": lo90, "ci90_hi": hi90})
    d_w = _paired(idx, setting, treat, base, lambda m: m["W"], cells)
    d_u = _paired(idx, setting, treat, base, lambda m: m["U"], cells)
    d_q = _paired(idx, setting, treat, base, lambda m: m["W"] / (1 - m["U"]) if m["U"] < 1 else 0.0, cells)
    d_match = _paired(idx, setting, treat, base, lambda m: 1 - m["U"], cells)
    theta0, du = stratified_mean(d_w), stratified_mean(d_u)
    v_star = -theta0 / du if du != 0 else None
    qlo, qhi = _ci(d_q, rng, 0.95)
    mlo, mhi = _ci(d_match, rng, 0.95)
    summary = {"contrast": label, "setting": setting, "treat": treat, "base": base,
               "n_cells": len(d_w), "n_pairs": sum(map(len, d_w.values())),
               "theta_W": theta0, "delta_U": du,
               "break_even_v": v_star,
               "break_even_in_0_1": bool(v_star is not None and 0 <= v_star <= 1),
               "delta_matched_share": stratified_mean(d_match), "matched_share_ci95_lo": mlo,
               "matched_share_ci95_hi": mhi,
               "delta_Q_mean_satisfaction_of_matched": stratified_mean(d_q), "Q_ci95_lo": qlo,
               "Q_ci95_hi": qhi}
    return sweep, summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results/confirmatory")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    root, out = Path(args.results), Path(args.out)
    docs = {e: _load(root / e / "results.json") for e in ("EXP-001", "EXP-002", "EXP-003")}
    rng = np.random.default_rng(SEED)

    idx1, idx2, idx3 = (_index(docs[e]) for e in ("EXP-001", "EXP-002", "EXP-003"))
    # EXP-002 arms are compared with the EXP-001 RANDOM arm on the same instance (as in D-017).
    for key, arms in idx1.items():
        if "RANDOM" in arms and key in idx2:
            idx2[key]["RANDOM"] = arms["RANDOM"]

    specs = [("EXP-001", idx1, "base", "POPULARITY", "RANDOM", None),
             ("EXP-001", idx1, "base", "EXPOSURE_BALANCED", "RANDOM", None),
             ("EXP-001 corner cells", idx1, "base", "POPULARITY", "RANDOM", CORNER),
             ("EXP-001 corner cells", idx1, "base", "EXPOSURE_BALANCED", "RANDOM", CORNER),
             ("EXP-002 H_a", idx2, "base", "DA_A", "RANDOM", None),
             ("EXP-002", idx2, "base", "MAXW", "RANDOM", None)]
    for sid in ("S1-theta0.3", "S1-theta0.7", "S2-T10", "S2-T20"):
        for arm in ("POPULARITY", "EXPOSURE_BALANCED"):
            specs.append(("EXP-003", idx3, sid, arm, "RANDOM", CORNER))
    sweep_rows, summary_rows = [], []
    for label, idx, sid, treat, base, cells in specs:
        s, m = contrasts(idx, label, sid, treat, base, cells, rng)
        sweep_rows += s
        summary_rows.append(m)
    sat = horizon_saturation({"EXP-001": docs["EXP-001"], "EXP-003": docs["EXP-003"]})

    out.mkdir(parents=True, exist_ok=True)
    meta = {"label": "EXPLORATORY (M4, J-0014); not a frozen analysis; no verdict changes",
            "inputs": {e: {"path": str(root / e / "results.json"), "config_sha256": docs[e]["config_sha256"],
                           "code_revision": docs[e]["code_revision"]} for e in docs},
            "analysis_seed": SEED, "n_resamples": N_RESAMPLES, "v_grid": list(V_GRID),
            "last_rounds": LAST_ROUNDS}
    (out / "results.json").write_text(json.dumps({"meta": meta, "unmatched_value_sweep": sweep_rows,
                                                  "decomposition": summary_rows,
                                                  "horizon_saturation": sat}, indent=1) + "\n")
    for name, rows in (("unmatched_value_sweep", sweep_rows), ("decomposition", summary_rows),
                       ("horizon_saturation", sat)):
        with (out / f"{name}.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"wrote {out} ({len(sweep_rows)} sweep rows, {len(summary_rows)} decompositions, {len(sat)} saturation rows)")


if __name__ == "__main__":
    main()
