# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Evidence audit (master prompt 11.5), session M4.

Run from the repository root:
    .venv/bin/python research/publication/evidence_audit.py

Checks, each printed with PASS or FAIL:
  A. Frozen hashes in research/freeze.json match the protocol and config files on disk.
  B. Result checksums (SHA256SUMS) of the three confirmatory result folders.
  C. Run and sample counts in the raw results (runs, invalid runs, exclusions, instances per cell,
     pairs per contrast) against the counts stated in the reports.
  D. An independent recomputation (plain numpy, no match_lab code) of the point estimates used in
     the claims: theta_P for EXP-001, H_a and H_b for EXP-002, theta_P per EXP-003 setting, the DA
     invariant, the cap short-slate range, and the U(DA_A) = U(DA_B) observation.
  E. Number trace: every decimal number in the audited documents must equal, at its printed
     precision, some value in a committed result file (confirmatory or exploratory tables and
     analysis JSON, freeze record, run manifests). Untraced numbers are listed for manual review.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(".")
RES = ROOT / "results" / "confirmatory"
DOCS = ["research/experiments/EXP-001/report.md", "research/experiments/EXP-002/report.md",
        "research/experiments/EXP-003/report.md", "research/paper/manuscript.md",
        "research/paper/supplementary.md", "research/claims_register.csv"]
SOURCES = sorted([*RES.glob("*/report/tables/*.csv"), *RES.glob("*/analysis/tables/*.csv"),
                  *RES.glob("*/analysis/*.json"), *(ROOT / "results/exploratory").glob("m4_*/**/*.csv"),
                  *(ROOT / "results/exploratory").glob("*/report/tables/*.csv"),
                  ROOT / "research/freeze.json", *RES.glob("*/run_manifest.json"),
                  *(ROOT / "results/exploratory").glob("m4_*/run_manifest.json")])
fails = 0


def report(ok: bool, msg: str) -> None:
    global fails
    fails += 0 if ok else 1
    print(("PASS " if ok else "FAIL ") + msg)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------ A
fr = json.loads((ROOT / "research/freeze.json").read_text())
report(sha(ROOT / "research/protocol.md") == fr["main_protocol"]["sha256"], "A main protocol hash")
for e, rec in fr["experiments"].items():
    report(sha(ROOT / f"research/experiments/{e}/protocol.md") == rec["protocol_sha256"], f"A {e} protocol hash")
    report(sha(ROOT / f"experiments/configs/{e}.json") == rec["config_file_sha256"], f"A {e} config file hash")

# ------------------------------------------------------------------ B
for e in ("EXP-001", "EXP-002", "EXP-003"):
    ok = True
    for line in (RES / e / "SHA256SUMS").read_text().splitlines():
        h, name = line.split(None, 1)
        ok &= sha(RES / e / name.strip()) == h
    report(ok, f"B {e} SHA256SUMS")

# ------------------------------------------------------------------ C and D
docs = {e: json.loads((RES / e / "results.json").read_text()) for e in ("EXP-001", "EXP-002", "EXP-003")}
expected_runs = {"EXP-001": 810, "EXP-002": 810, "EXP-003": 1440}
for e, d in docs.items():
    n = len(d["runs"])
    inv = sum(1 for r in d["runs"] if not r["valid"])
    report(n == expected_runs[e] and inv == 0 and not d["exclusions"],
           f"C {e}: {n} runs, {inv} invalid, {len(d['exclusions'])} exclusions")
    report(d["config_sha256"] == fr["experiments"][e]["config_canonical_sha256"], f"C {e} canonical config hash in results")


def cell(r):
    return (r["cell"]["r"], r["cell"]["rho"])


def by_arm(d, setting="base"):
    out = defaultdict(dict)
    for r in d["runs"]:
        if r["setting"]["setting_id"] == setting:
            out[(cell(r), r["instance"])][r["arm"]] = r["metrics"]
    return out


def theta(idx, treat, base, metric, cells=None):
    per = defaultdict(list)
    for (c, _i), arms in idx.items():
        if (cells is None or c in cells) and treat in arms and base in arms:
            per[c].append(arms[treat][metric] - arms[base][metric])
    counts = {c: len(v) for c, v in per.items()}
    return float(np.mean([np.mean(v) for v in per.values()])), counts


i1 = by_arm(docs["EXP-001"])
tp, cnt = theta(i1, "POPULARITY", "RANDOM", "W")
report(round(tp, 4) == 0.0219 and set(cnt.values()) == {30} and len(cnt) == 9,
       f"D EXP-001 theta POPULARITY {tp:.4f} (9 cells x 30 pairs)")
te, _ = theta(i1, "EXPOSURE_BALANCED", "RANDOM", "W")
report(round(te, 4) == 0.0004, f"D EXP-001 theta EXPOSURE_BALANCED {te:.4f}")
i2 = by_arm(docs["EXP-002"])
for k, arms in i1.items():
    i2[k]["RANDOM"] = arms["RANDOM"]
ha, cnt = theta(i2, "DA_A", "RANDOM", "W")
report(round(ha, 4) == 0.0963 and sum(cnt.values()) == 270, f"D EXP-002 H_a {ha:.4f} (270 pairs)")
hb, _ = theta(i2, "MAXW", "DA_A", "blocking_per_100")
report(round(hb, 2) == 231.06, f"D EXP-002 H_b {hb:.2f}")
da_block = sum(1 for r in docs["EXP-002"]["runs"] if r["arm"] in ("DA_A", "DA_B") and r["metrics"]["blocking_pairs"])
n_da = sum(1 for r in docs["EXP-002"]["runs"] if r["arm"] in ("DA_A", "DA_B"))
report(da_block == 0 and n_da == 540, f"D DA invariant: {da_block} of {n_da} DA runs with a blocking pair")
same_u = all(abs(a["DA_A"]["U"] - a["DA_B"]["U"]) < 1e-15 for a in by_arm(docs["EXP-002"]).values())
report(same_u, "D U(DA_A) = U(DA_B) on every instance")
corner = {(1.0, 0.0), (1.0, 0.9), (1.5, 0.0), (1.5, 0.9)}
want = {("S2-T10", "POPULARITY"): -0.4081, ("S2-T20", "POPULARITY"): -0.2824,
        ("S1-theta0.3", "POPULARITY"): 0.0340, ("S1-theta0.7", "POPULARITY"): 0.0030,
        ("S2-T10", "EXPOSURE_BALANCED"): 0.0008, ("S2-T20", "EXPOSURE_BALANCED"): 0.0049}
for (s, arm), v in want.items():
    t, cnt = theta(by_arm(docs["EXP-003"], s), arm, "RANDOM", "W", corner)
    report(round(t, 4) == v and sum(cnt.values()) == 120, f"D EXP-003 {s} {arm} {t:.4f} (120 pairs)")
t, _ = theta(i1, "POPULARITY", "RANDOM", "W", corner)
report(round(t, 4) == 0.0169, f"D EXP-001 corner-cell reference POPULARITY {t:.4f}")
cap = []
for c in sorted({cell(r) for r in docs["EXP-001"]["runs"]}):
    rs = [r for r in docs["EXP-001"]["runs"] if r["arm"] == "EXPOSURE_BALANCED" and cell(r) == c]
    cap.append(sum(r["diagnostics"]["cap_short_slates"] for r in rs) / sum(r["diagnostics"]["n_slates"] for r in rs))
report(max(cap) <= 0.0105, f"D EXP-001 cap short-slate share per cell {min(cap):.4f} to {max(cap):.4f}")

# ------------------------------------------------------------------ E
pool: set[str] = set()
num_re = re.compile(r"[-+]?\d[\d,]*\.\d+(?:e-?\d+)?")
src_re = re.compile(r"[-+]?\d+\.\d+(?:e[-+]?\d+)?")
for src in SOURCES:
    for tok in src_re.findall(src.read_text()):
        x = float(tok)
        for nd in range(0, 7):
            pool.add(f"{abs(round(x, nd)):.{nd}f}")
            # half-up rounding of the decimal string (for example 14.075 printed as 14.08)
            pool.add(str(abs(Decimal(tok)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)))
        pool.add(f"{abs(x) * 100:.1f}")  # shares printed as percentages
        pool.add(f"{abs(x) * 100:.2f}")
        pool.add(f"{abs(x) * 100:.0f}")
for doc in DOCS:
    p = ROOT / doc
    if not p.exists():
        continue
    text = re.sub(r"[0-9a-f]{40,64}", "", p.read_text())  # drop hashes and revisions
    text = re.sub(r"(10\.\d{4,9}/\S+|arXiv:\d{4}\.\d{4,5}|\d{4}\.\d{5}\b)", "", text)  # DOIs, arXiv ids
    untraced = []
    for tok in num_re.findall(text):
        t = tok.replace(",", "").lstrip("+-")
        if t in pool or re.fullmatch(r"\d+\.0+", t):
            continue
        untraced.append(tok)
    report(not untraced, f"E {doc}: untraced decimals {sorted(set(untraced))[:40]}")

print(f"{fails} FAIL")
sys.exit(1 if fails else 0)
