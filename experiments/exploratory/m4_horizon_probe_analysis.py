# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""M4 EXPLORATORY analysis of the horizon-extension probe (journal J-0015).

Reads ``results/exploratory/m4_horizon_probe/results.json`` (config
``experiments/configs/m4_horizon_probe.json``, exploratory root seed 505, 10 instances per cell,
T in {40, 80, 160}) and writes, per setting: theta_P (equal-weight mean over the 9 cells of
W_P - W_RANDOM) with a 95% stratified bootstrap CI, the per-cell means, and the horizon
saturation of each arm. Exploratory only: it tests no hypothesis and changes no frozen verdict.

Usage (from the repository root):
    .venv/bin/python experiments/exploratory/m4_horizon_probe_analysis.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from match_lab.stats import stratified_bootstrap_ci, stratified_mean

SEED = 20261125
SRC = Path("results/exploratory/m4_horizon_probe/results.json")
OUT = Path("results/exploratory/m4_horizon_probe/analysis")


def main() -> None:
    doc = json.loads(SRC.read_text())
    rng = np.random.default_rng(SEED)
    idx: dict = defaultdict(dict)
    for run in doc["runs"]:
        if run["valid"]:
            cell = f"r={run['cell']['r']:g}, rho={run['cell']['rho']:g}"
            idx[(run["setting"]["setting_id"], run["setting"]["T"], cell, run["instance"])][run["arm"]] = run
    pooled, cells_rows, sat_rows = [], [], []
    settings = sorted({(k[0], k[1]) for k in idx}, key=lambda s: s[1])
    for sid, T in settings:
        for arm in ("POPULARITY", "EXPOSURE_BALANCED"):
            by: dict[str, list[float]] = defaultdict(list)
            du: dict[str, list[float]] = defaultdict(list)
            for (s, _t, cell, _i), arms in sorted(idx.items()):
                if s == sid and arm in arms and "RANDOM" in arms:
                    by[cell].append(arms[arm]["metrics"]["W"] - arms["RANDOM"]["metrics"]["W"])
                    du[cell].append(arms[arm]["metrics"]["U"] - arms["RANDOM"]["metrics"]["U"])
            lo, hi = stratified_bootstrap_ci(by, n_resamples=10_000, rng=rng)
            pooled.append({"setting": sid, "T": T, "arm": arm, "n_cells": len(by),
                           "n_pairs": sum(map(len, by.values())), "theta": stratified_mean(by),
                           "ci95_lo": lo, "ci95_hi": hi, "delta_U": stratified_mean(du)})
            for cell, d in sorted(by.items()):
                cells_rows.append({"setting": sid, "T": T, "arm": arm, "cell": cell, "n_pairs": len(d),
                                   "mean_diff": float(np.mean(d)), "min_diff": float(np.min(d)),
                                   "max_diff": float(np.max(d))})
        for arm in ("RANDOM", "POPULARITY", "EXPOSURE_BALANCED"):
            per_cell: dict[str, list] = defaultdict(list)
            for (s, _t, cell, _i), arms in idx.items():
                if s == sid and arm in arms:
                    per_cell[cell].append(arms[arm])
            for cell, runs in sorted(per_cell.items()):
                mbr = [r["diagnostics"]["matches_by_round"] for r in runs]
                sat_rows.append({"setting": sid, "T": T, "arm": arm, "cell": cell, "n_instances": len(runs),
                                 "share_instances_with_match_in_last_10_rounds":
                                     float(np.mean([sum(m[-10:]) > 0 for m in mbr])),
                                 "mean_last_round_with_a_match":
                                     float(np.mean([max((i + 1 for i, x in enumerate(m) if x > 0), default=0)
                                                    for m in mbr])),
                                 "W_mean": float(np.mean([r["metrics"]["W"] for r in runs])),
                                 "U_mean": float(np.mean([r["metrics"]["U"] for r in runs]))})
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"label": "EXPLORATORY (M4, J-0015); not a frozen analysis; no verdict changes",
            "source": str(SRC), "config_sha256": doc["config_sha256"], "code_revision": doc["code_revision"],
            "analysis_seed": SEED}
    (OUT / "analysis.json").write_text(json.dumps({"meta": meta, "pooled": pooled, "cells": cells_rows,
                                                   "saturation": sat_rows}, indent=1) + "\n")
    for name, rows in (("pooled", pooled), ("cells", cells_rows), ("saturation", sat_rows)):
        with (OUT / f"{name}.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
