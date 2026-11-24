# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Report generator: tables (CSV and Markdown), SVG figures and an optional PDF from result files.

Every number in the generated report is computed here from a validated result document;
nothing is typed by hand. Exploratory results get an explicit banner and no p-values.
PDFs go through pandoc to Typst with ``-V mainfont="Libertinus Serif"`` (workaround from M0)
and are compiled by the ``typst`` Python package of the shared tools interpreter.
"""

from __future__ import annotations

import csv
import html
import math
import os
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from .config import ARMS_SEQUENTIAL, ExperimentConfig
from .runner import load_result
from .stats import (bootstrap_ci, holm, mean_sd_dz, n_for_power, sign_flip_pvalue,
                    stratified_bootstrap_ci, stratified_mean)

SESOI = 0.01  # smallest effect size of interest for W (protocol section 3)
REPORT_SEED = 20261124_7  # fixed seed for bootstrap and randomization draws in reports
DEFAULT_PANDOC = "/Users/bechir/research/labs/.tools/pandoc"
DEFAULT_TYPST_PYTHON = "/Users/bechir/research/labs/.tools/py/bin/python"
ARM_COLORS = {"RANDOM": "#4a4a4a", "POPULARITY": "#b5462f", "EXPOSURE_BALANCED": "#2f6fb5",
              "DA_A": "#6a8f3a", "DA_B": "#8f7a3a", "MAXW": "#7a3a8f"}


def _fmt(x: Any, nd: int = 4) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, float) and math.isnan(x):
        return "n/a"
    return f"{x:.{nd}f}"


def _cell_label(run: dict) -> str:
    return f"r={run['cell']['r']:g}, rho={run['cell']['rho']:g}"


def _group(doc: dict):
    """Index valid runs: (setting_id, cell_label) -> arm -> instance_key -> run. Excluded instances drop."""
    excluded = {e["instance_key"] for e in doc["exclusions"]}
    idx: dict[tuple[str, str], dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
    for run in doc["runs"]:
        if run["instance_key"] in excluded:
            continue
        idx[(run["setting"]["setting_id"], _cell_label(run))][run["arm"]][run["instance_key"]] = run
    return idx


def arm_summary(doc: dict) -> list[dict]:
    rows = []
    for (sid, cell), arms in sorted(_group(doc).items()):
        for arm, runs in arms.items():
            vals = list(runs.values())
            row = {"setting": sid, "cell": cell, "arm": arm, "n_instances": len(vals)}
            for name in ("W", "U", "M", "gini_exposure_B", "blocking_per_100", "W_A", "W_B"):
                xs = [r["metrics"][name] for r in vals if r["metrics"][name] is not None]
                row[f"{name}_mean"] = float(np.mean(xs)) if xs else None
                row[f"{name}_sd"] = float(np.std(xs, ddof=1)) if len(xs) > 1 else None
            rt = [r["diagnostics"]["runtime_s"] for r in vals]
            row["runtime_mean_s"] = float(np.mean(rt))
            sl = [r["diagnostics"]["short_slates"] for r in vals if r["diagnostics"]["short_slates"] is not None]
            ns = [r["diagnostics"]["n_slates"] for r in vals if r["diagnostics"]["n_slates"] is not None]
            cs = [r["diagnostics"]["cap_short_slates"] for r in vals if r["diagnostics"]["cap_short_slates"] is not None]
            row["short_slate_share"] = (sum(sl) / sum(ns)) if ns and sum(ns) else None
            row["cap_short_slate_share"] = (sum(cs) / sum(ns)) if ns and sum(ns) else None
            row["zero_match_instances"] = sum(1 for r in vals if r["metrics"]["n_matched"] == 0)
            rows.append(row)
    return rows


def paired_differences(doc: dict, metric: str = "W", baseline: str = "RANDOM") -> list[dict]:
    rng = np.random.default_rng(REPORT_SEED)
    rows = []
    for (sid, cell), arms in sorted(_group(doc).items()):
        if baseline not in arms:
            continue
        base = arms[baseline]
        for arm, runs in arms.items():
            if arm == baseline:
                continue
            keys = sorted(set(base) & set(runs))
            d = [runs[k]["metrics"][metric] - base[k]["metrics"][metric] for k in keys
                 if runs[k]["metrics"][metric] is not None and base[k]["metrics"][metric] is not None]
            if not d:
                continue
            m, sd, dz = mean_sd_dz(d)
            lo, hi = bootstrap_ci(d, rng=rng)
            rows.append({"setting": sid, "cell": cell, "contrast": f"{arm} - {baseline}", "arm": arm,
                         "n_pairs": len(d), "mean_diff": m, "sd_diff": sd, "dz": dz, "ci95_lo": lo,
                         "ci95_hi": hi, "n_exact_zero": int(sum(1 for x in d if x == 0.0)),
                         "n_for_sesoi_80pct_per_cell": n_for_power(sd, SESOI) if sd else None,
                         "values": d})
    return rows


def pooled_contrasts(doc: dict, diffs: list[dict], confirmatory: bool) -> list[dict]:
    """theta_P per setting and arm: equal-weight mean over cells, stratified bootstrap CI.

    p-values (stratified sign-flip, Holm over the sequential contrasts) only for confirmatory
    documents; exploratory reports never carry p-values.
    """
    rng = np.random.default_rng(REPORT_SEED + 1)
    by = defaultdict(dict)
    for row in diffs:
        by[(row["setting"], row["arm"])][row["cell"]] = row["values"]
    out = []
    for (sid, arm), cells in sorted(by.items()):
        lo, hi = stratified_bootstrap_ci(cells, rng=rng)
        lo90, hi90 = stratified_bootstrap_ci(cells, rng=rng, level=0.90)
        sds = [np.std(v, ddof=1) for v in cells.values() if len(v) > 1]
        n_pooled = None
        if len(sds) == len(cells) and sds:
            # var(theta_hat) = sum_c sd_c^2 / (C^2 N); solve for N at 80% power and effect SESOI
            var_unit = float(np.sum(np.square(sds))) / len(cells) ** 2
            n_pooled = n_for_power(math.sqrt(var_unit), SESOI)
        row = {"setting": sid, "arm": arm, "n_cells": len(cells), "theta": stratified_mean(cells),
               "ci95_lo": lo, "ci95_hi": hi, "ci90_lo": lo90, "ci90_hi": hi90,
               "n_per_cell_for_sesoi_80pct_pooled": n_pooled, "p_signflip": None, "p_holm": None}
        if confirmatory and arm in ARMS_SEQUENTIAL:
            row["p_signflip"] = sign_flip_pvalue(cells, rng=rng)
        out.append(row)
    if confirmatory:
        for sid in {r["setting"] for r in out}:
            fam = [r for r in out if r["setting"] == sid and r["p_signflip"] is not None]
            for r, p in zip(fam, holm([r["p_signflip"] for r in fam])):
                r["p_holm"] = p
    return out


def degenerate_checks(doc: dict, summary: list[dict], diffs: list[dict]) -> list[str]:
    notes = []
    inv = [r for r in doc["runs"] if not r["valid"]]
    notes.append(f"Invalid runs: {len(inv)} of {len(doc['runs'])}; excluded instances: {len(doc['exclusions'])}.")
    for e in doc["exclusions"]:
        notes.append(f"Excluded {e['instance_key']}: {e['reason']}")
    for row in summary:
        if row["zero_match_instances"]:
            notes.append(f"{row['setting']} {row['cell']} {row['arm']}: {row['zero_match_instances']} "
                         f"instance(s) with zero matches.")
        if row["cap_short_slate_share"]:
            notes.append(f"{row['setting']} {row['cell']} {row['arm']}: {row['cap_short_slate_share']:.1%} "
                         f"of slates shortened by the exposure cap.")
    for row in diffs:
        if row["n_exact_zero"] == row["n_pairs"]:
            notes.append(f"{row['setting']} {row['cell']} {row['contrast']}: all paired differences are exactly 0.")
        elif row["sd_diff"] == 0:
            notes.append(f"{row['setting']} {row['cell']} {row['contrast']}: paired SD is 0.")
    return notes


# ---------------------------------------------------------------- runtime projection

def project_runtime(docs: list[dict], plans: list[ExperimentConfig]) -> list[dict]:
    """Project the wall-clock of planned configs from measured mean runtimes.

    Lookup order for a planned (n_a, r, rho, theta, T, arm): exact match; else the same
    (n_a, r, rho, arm) at another T, scaled linearly by T (sequential arms only; centralized
    arms do not depend on T); else unmeasured. Market generation time is added per instance.
    """
    exact: dict[tuple, list[float]] = defaultdict(list)
    loose: dict[tuple, list[tuple[float, int]]] = defaultdict(list)
    gen: dict[tuple, list[float]] = defaultdict(list)
    for doc in docs:
        for run in doc["runs"]:
            c, s = run["cell"], run["setting"]
            rt = run["diagnostics"]["runtime_s"]
            exact[(c["n_a"], c["r"], c["rho"], s["theta"], s["T"], run["arm"])].append(rt)
            loose[(c["n_a"], c["r"], c["rho"], run["arm"])].append((rt, s["T"]))
            g = run["diagnostics"].get("market_generation_s")
            if g is not None:
                gen[(c["n_a"], c["r"], c["rho"])].append(g)
    out = []
    for plan in plans:
        total, unmeasured, scaled = 0.0, 0, 0
        for r in plan.r_values:
            for rho in plan.rho_values:
                g = gen.get((plan.n_a, r, rho))
                per_inst_gen = float(np.mean(g)) if g else 0.0
                for st in plan.settings:
                    total += per_inst_gen * plan.instances_per_cell
                    for arm in plan.arms:
                        e = exact.get((plan.n_a, r, rho, st.theta, st.T, arm))
                        if e:
                            per = float(np.mean(e))
                        elif loose.get((plan.n_a, r, rho, arm)):
                            vals = loose[(plan.n_a, r, rho, arm)]
                            if arm in ARMS_SEQUENTIAL:
                                per = float(np.mean([rt * st.T / t for rt, t in vals if t > 0]))
                            else:
                                per = float(np.mean([rt for rt, _ in vals]))
                            scaled += plan.instances_per_cell
                        else:
                            unmeasured += plan.instances_per_cell
                            continue
                        total += per * plan.instances_per_cell
        out.append({"experiment_id": plan.experiment_id, "planned_runs": plan.n_runs,
                    "projected_seconds_single_process": total, "runs_by_T_scaling": scaled,
                    "runs_unmeasured": unmeasured})
    return out


# ---------------------------------------------------------------- SVG figures

def _svg(width: int, height: int, body: list[str], title: str, desc: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif" font-size="11">'
            f'<title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc>'
            f'<rect width="100%" height="100%" fill="#ffffff"/>' + "".join(body) + "</svg>\n")


def fig_welfare_by_arm(doc: dict, setting: str) -> str:
    grp = {k: v for k, v in _group(doc).items() if k[0] == setting}
    cells = sorted({k[1] for k in grp})
    arms = [a for a in ("RANDOM", "POPULARITY", "EXPOSURE_BALANCED", "DA_A", "DA_B", "MAXW")
            if any(a in grp[(setting, c)] for c in cells)]
    vals = [r["metrics"]["W"] for k in grp for a in grp[k] for r in grp[k][a].values() if r["metrics"]["W"] is not None]
    if not vals:
        return _svg(400, 60, ['<text x="10" y="30">No data</text>'], "No data", "No valid runs.")
    lo, hi = min(vals), max(vals)
    pad = max(1e-3, 0.05 * (hi - lo))
    lo, hi = max(0.0, lo - pad), min(1.0, hi + pad)
    left, right, row_h = 190, 640, 14
    body = []
    xs = lambda v: left + (v - lo) / (hi - lo) * (right - left)  # noqa: E731
    y = 30
    for c in cells:
        body.append(f'<text x="8" y="{y + 10}" font-weight="bold">{html.escape(c)}</text>')
        y += 26
        for a in arms:
            runs = grp[(setting, c)].get(a, {})
            body.append(f'<text x="24" y="{y + 4}" fill="{ARM_COLORS[a]}">{a}</text>')
            ws = [r["metrics"]["W"] for r in runs.values() if r["metrics"]["W"] is not None]
            for w in ws:
                body.append(f'<circle cx="{xs(w):.1f}" cy="{y}" r="2.6" fill="{ARM_COLORS[a]}" fill-opacity="0.6"/>')
            if ws:
                mx = xs(float(np.mean(ws)))
                body.append(f'<line x1="{mx:.1f}" x2="{mx:.1f}" y1="{y - 5}" y2="{y + 5}" stroke="#000" stroke-width="1.5"/>')
            y += row_h
    ya = y + 4
    body.append(f'<line x1="{left}" x2="{right}" y1="{ya}" y2="{ya}" stroke="#000"/>')
    for t in np.linspace(lo, hi, 5):
        body.append(f'<line x1="{xs(t):.1f}" x2="{xs(t):.1f}" y1="{ya}" y2="{ya + 4}" stroke="#000"/>'
                    f'<text x="{xs(t):.1f}" y="{ya + 16}" text-anchor="middle">{t:.3f}</text>')
    body.append(f'<text x="{(left + right) / 2}" y="{ya + 30}" text-anchor="middle">Mean agent welfare W (unitless, 0 to 1); dot = one market instance, bar = mean</text>')
    title = f"Welfare by arm, setting {setting}"
    desc = ("Strip plot of mean agent welfare W per market instance for each arm and design cell. "
            f"{doc['mode'].capitalize()} simulation results; each dot is one synthetic market instance.")
    return _svg(660, int(ya + 40), body, title, desc)


def fig_paired_differences(diffs: list[dict], setting: str) -> str:
    rows = [d for d in diffs if d["setting"] == setting]
    if not rows:
        return _svg(400, 60, ['<text x="10" y="30">No data</text>'], "No data", "No paired differences.")
    ext = max(1e-3, max(max(abs(d["ci95_lo"]), abs(d["ci95_hi"]), *map(abs, d["values"])) for d in rows))
    lo, hi = -ext * 1.05, ext * 1.05
    left, right, row_h = 290, 650, 16
    height = 60 + len(rows) * row_h
    xs = lambda v: left + (v - lo) / (hi - lo) * (right - left)  # noqa: E731
    body = [f'<line x1="{xs(0):.1f}" x2="{xs(0):.1f}" y1="20" y2="{height - 40}" stroke="#999" stroke-dasharray="3,3"/>']
    y = 30
    for d in rows:
        col = ARM_COLORS.get(d["arm"], "#000")
        body.append(f'<text x="8" y="{y + 4}">{html.escape(d["cell"])}: {html.escape(d["contrast"])}</text>')
        for v in d["values"]:
            body.append(f'<circle cx="{xs(v):.1f}" cy="{y}" r="2" fill="{col}" fill-opacity="0.35"/>')
        body.append(f'<line x1="{xs(d["ci95_lo"]):.1f}" x2="{xs(d["ci95_hi"]):.1f}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="2"/>'
                    f'<circle cx="{xs(d["mean_diff"]):.1f}" cy="{y}" r="3.5" fill="{col}"/>')
        y += row_h
    ya = y + 2
    body.append(f'<line x1="{left}" x2="{right}" y1="{ya}" y2="{ya}" stroke="#000"/>')
    for t in np.linspace(lo, hi, 5):
        body.append(f'<line x1="{xs(t):.1f}" x2="{xs(t):.1f}" y1="{ya}" y2="{ya + 4}" stroke="#000"/>'
                    f'<text x="{xs(t):.1f}" y="{ya + 16}" text-anchor="middle">{t:+.3f}</text>')
    body.append(f'<text x="{(left + right) / 2}" y="{ya + 30}" text-anchor="middle">Paired difference in W versus RANDOM; large dot = mean, bar = 95% percentile bootstrap CI over instances</text>')
    desc = ("Per-cell paired differences in mean agent welfare versus the RANDOM sequential baseline, "
            "with per-instance values as small dots and 95% bootstrap intervals over market instances.")
    return _svg(660, int(ya + 40), body, f"Paired differences, setting {setting}", desc)


# ---------------------------------------------------------------- Markdown assembly

ARM_SHORT = {"RANDOM": "RND", "POPULARITY": "POP", "EXPOSURE_BALANCED": "EXB", "DA_A": "DA_A",
             "DA_B": "DA_B", "MAXW": "MAXW"}
ARM_LEGEND = ("Arm abbreviations in tables: RND = RANDOM, POP = POPULARITY, EXB = EXPOSURE_BALANCED; "
              "DA_A, DA_B and MAXW as in the protocol.")


def _short(text: str) -> str:
    if text.startswith("r=") and ", rho=" in text:
        return text.replace("r=", "").replace("rho=", "")
    for long, short in ARM_SHORT.items():
        text = text.replace(long, short)
    return text


def _md_table(rows: list[dict], cols: list[tuple[str, str]], nd: int = 4) -> str:
    head = "| " + " | ".join(h for _, h in cols) + " |\n|" + "---|" * len(cols) + "\n"
    return head + "".join("| " + " | ".join(_fmt(r.get(k), nd) if not isinstance(r.get(k), str) else _short(r[k])
                                            for k, _ in cols) + " |\n" for r in rows)


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = [k for k in rows[0] if k != "values"]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


def build_report(result_paths: list[str | Path], out_dir: str | Path, *, plans: list[ExperimentConfig] = (),
                 pdf: bool = True, repo_root: str | Path = ".") -> dict:
    out = Path(out_dir)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    docs = [load_result(p) for p in result_paths]  # validated at import; fails closed
    root = Path(repo_root).resolve()
    lines: list[str] = []
    exploratory = any(d["mode"] == "exploratory" for d in docs)
    title = "MATCH exploratory run report" if exploratory else "MATCH run report"
    lines += [f"<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->", f"# {title}", ""]
    if exploratory:
        lines += ["**EXPLORATORY. Not a finding.** These are synthetic simulation results from an exploratory "
                  "run made before the protocol freeze. They exist to check the pipeline and to measure runtime, "
                  "seed spread and degenerate cases for the owner's freeze decision. They test no hypothesis, "
                  "carry no p-values and must not be cited as evidence.", ""]
    lines += ["Generated by `python -m match_lab report` from validated result files. All participants are synthetic.",
              "", ARM_LEGEND, ""]
    for d_i, doc in enumerate(docs):
        src = Path(result_paths[d_i]).resolve()
        rel = src.relative_to(root) if root in src.parents else src
        summary = arm_summary(doc)
        diffs = paired_differences(doc)
        pooled = pooled_contrasts(doc, diffs, confirmatory=doc["mode"] == "confirmatory")
        tag = doc["experiment_id"].replace("/", "_")
        _write_csv(out / "tables" / f"{tag}_arm_summary.csv", summary)
        _write_csv(out / "tables" / f"{tag}_paired_differences_W.csv", diffs)
        _write_csv(out / "tables" / f"{tag}_pooled_W.csv", pooled)
        cfg = doc["config"]
        lines += [f"## {doc['experiment_id']} ({doc['mode']}): {doc['label']}", "",
                  f"- Result file: `{rel}`", f"- Config SHA-256: `{doc['config_sha256']}`",
                  f"- Code revision: `{doc['code_revision']}`; generator: {doc['generator_version']}",
                  f"- Root seed: {cfg.get('root_seed')}; n_A = {cfg['n_a']}; r in {cfg['r_values']}; "
                  f"rho in {cfg['rho_values']}; {cfg['instances_per_cell']} instances per cell; "
                  f"settings: {', '.join(s['setting_id'] + ' (theta ' + str(s['theta']) + ', T ' + str(s['T']) + ')' for s in cfg['settings'])}",
                  f"- Runs: {len(doc['runs'])}; total runtime of runs {sum(r['diagnostics']['runtime_s'] for r in doc['runs']):.2f} s", ""]
        lines += ["### Arm summary (mean and SD over instances)", "",
                  _md_table(summary, [("setting", "setting"), ("cell", "r, rho"), ("arm", "arm"), ("n_instances", "n"),
                                      ("W_mean", "W"), ("W_sd", "SD(W)"), ("U_mean", "U"), ("M_mean", "M"),
                                      ("gini_exposure_B_mean", "Gini exp. B"), ("blocking_per_100_mean", "block/100"),
                                      ("runtime_mean_s", "runtime s")]), ""]
        lines += ["### Paired differences in W versus RANDOM, per cell", "",
                  "Mean, SD and dz of per-instance paired differences; 95% percentile bootstrap CI over instances "
                  "(10,000 resamples). `N(SESOI)` is the normal-approximation number of instances per cell for 80% "
                  "power to detect a difference of 0.01 in that cell, using this run's SD (planning only).", "",
                  _md_table(diffs, [("setting", "setting"), ("cell", "r, rho"), ("contrast", "contrast"), ("n_pairs", "n"),
                                    ("mean_diff", "mean D"), ("sd_diff", "SD(D)"), ("dz", "dz"), ("ci95_lo", "CI lo"),
                                    ("ci95_hi", "CI hi"), ("n_for_sesoi_80pct_per_cell", "N(SESOI)")]), ""]
        lines += ["### Equal-weight mean over cells (theta) of W differences versus RANDOM", "",
                  "Stratified bootstrap CIs. `N/cell pooled` is the instances per cell needed for 80% power on the "
                  "pooled contrast at effect 0.01, from this run's per-cell SDs (planning only)."
                  + ("" if doc["mode"] == "confirmatory" else " No p-values are computed for exploratory runs."), "",
                  _md_table(pooled, [("setting", "setting"), ("arm", "arm"), ("n_cells", "cells"), ("theta", "theta"),
                                     ("ci95_lo", "95% lo"), ("ci95_hi", "95% hi"), ("ci90_lo", "90% lo"),
                                     ("ci90_hi", "90% hi"), ("n_per_cell_for_sesoi_80pct_pooled", "N/cell pooled"),
                                     ("p_signflip", "p"), ("p_holm", "p Holm")]), ""]
        lines += ["### Degenerate-case checks", ""] + [f"- {n}" for n in degenerate_checks(doc, summary, diffs)] + [""]
        for s in cfg["settings"]:
            sid = s["setting_id"]
            for kind, svg in (("welfare", fig_welfare_by_arm(doc, sid)),
                              ("paired", fig_paired_differences(diffs, sid))):
                name = f"FIG-{tag}-{sid}-{kind}.svg"
                (out / "figures" / name).write_text(svg, encoding="utf-8")
                cap = ("Mean agent welfare W per synthetic market instance by arm and cell" if kind == "welfare"
                       else "Paired differences in W versus RANDOM with 95% bootstrap CIs")
                lines += [f"![{cap} ({doc['mode']} run {doc['experiment_id']}, setting {sid}, {name[:-4]}). Unitless welfare scale; "
                          f"n = {cfg['instances_per_cell']} instances per cell.](figures/{name}){{width=80%}}", ""]
    if plans:
        proj = project_runtime(docs, list(plans))
        _write_csv(out / "tables" / "runtime_projection.csv", proj)
        lines += ["## Projected runtime of the planned matrix (single process)", "",
                  "Projection from the measured mean runtime per (n_A, r, rho, theta, T, arm), plus market "
                  "generation. Runs without an exact measurement are scaled linearly in T (sequential arms) or "
                  "reused (centralized arms); the count of such runs is shown.", "",
                  _md_table(proj, [("experiment_id", "experiment"), ("planned_runs", "planned runs"),
                                   ("projected_seconds_single_process", "projected s"),
                                   ("runs_by_T_scaling", "runs scaled"), ("runs_unmeasured", "runs unmeasured")], 1), ""]
    md_path = out / "report.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    info = {"markdown": str(md_path), "pdf": None, "pdf_error": None}
    if pdf:
        try:
            info["pdf"] = str(build_pdf(md_path))
        except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
            info["pdf_error"] = f"{type(exc).__name__}: {exc}"
    return info


def build_pdf(md_path: Path) -> Path:
    """Markdown -> pandoc -> Typst -> PDF (typst Python package in the shared tools interpreter)."""
    pandoc = os.environ.get("MATCH_PANDOC", DEFAULT_PANDOC)
    tpy = os.environ.get("MATCH_TYPST_PYTHON", DEFAULT_TYPST_PYTHON)
    if not (Path(pandoc).exists() and Path(tpy).exists()):
        raise RuntimeError("pandoc or the typst Python interpreter was not found; PDF not built")
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([pandoc, str(md_path), "-s", "-t", "typst", "-V", 'mainfont=Libertinus Serif',
                    "-V", "header-includes=#show figure: set block(breakable: true)",
                    "-o", str(typ)], check=True, capture_output=True, text=True)
    code = ("import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])")
    subprocess.run([tpy, "-I", "-c", code, str(typ), str(pdf), str(md_path.parent)], check=True,
                   capture_output=True, text=True)
    typ.unlink()
    return pdf
