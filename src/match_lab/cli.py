# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Command line: ``python -m match_lab {smoke,run,report,test}``.

- ``smoke``: run the exploratory smoke config and build its report.
- ``run --config PATH``: run a config; refuses a confirmatory config unless its protocol, the
  main protocol and the config itself match the freeze record and the registry (G-FREEZE).
- ``report --results PATH [PATH ...] --out DIR``: tables, figures and PDF from result files.
- ``analyze --experiment EXP-00N --exp001 PATH --results PATH --out DIR``: the frozen EXP-002 or
  EXP-003 cross-experiment analysis (tables, figure, JSON).
- ``test``: run the pytest suite.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .config import load_config
from .errors import MatchLabError, ProtocolNotFrozenError
from .report import build_report
from .runner import run_experiment

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_CONFIG = "experiments/configs/smoke.json"
PLAN_CONFIGS = ("experiments/configs/EXP-001.json", "experiments/configs/EXP-002.json",
                "experiments/configs/EXP-003.json")


def _plans(paths):
    return [load_config(REPO_ROOT / p) for p in paths]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="match_lab", description="MATCH research runner (synthetic simulations)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_smoke = sub.add_parser("smoke", help="exploratory smoke run and report")
    p_smoke.add_argument("--config", default=SMOKE_CONFIG)
    p_smoke.add_argument("--overwrite", action="store_true")
    p_smoke.add_argument("--no-pdf", action="store_true")
    p_run = sub.add_parser("run", help="run one experiment config")
    p_run.add_argument("--config", required=True)
    p_run.add_argument("--overwrite", action="store_true")
    p_rep = sub.add_parser("report", help="build a report from result files")
    p_rep.add_argument("--results", nargs="+", required=True)
    p_rep.add_argument("--out", required=True)
    p_rep.add_argument("--plans", nargs="*", default=list(PLAN_CONFIGS),
                       help="configs whose runtime is projected from the measured runs")
    p_rep.add_argument("--no-pdf", action="store_true")
    p_an = sub.add_parser("analyze", help="frozen cross-experiment analysis (EXP-002 or EXP-003)")
    p_an.add_argument("--experiment", required=True, choices=["EXP-002", "EXP-003"])
    p_an.add_argument("--exp001", required=True, help="EXP-001 results.json")
    p_an.add_argument("--results", required=True, help="EXP-002 or EXP-003 results.json")
    p_an.add_argument("--out", required=True)
    p_test = sub.add_parser("test", help="run the test suite")
    p_test.add_argument("pytest_args", nargs="*")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", "-q", *args.pytest_args], cwd=REPO_ROOT)
        if args.cmd == "run":
            cfg = load_config(REPO_ROOT / args.config if not Path(args.config).is_absolute() else args.config)
            print(f"{cfg.experiment_id}: {cfg.mode} run, {cfg.n_runs} runs", file=sys.stderr)
            out = run_experiment(cfg, REPO_ROOT, overwrite=args.overwrite, progress=True)
            print(out / "results.json")
            return 0
        if args.cmd == "smoke":
            cfg = load_config(REPO_ROOT / args.config)
            if cfg.mode != "exploratory":
                print("smoke only runs exploratory configs", file=sys.stderr)
                return 2
            out = run_experiment(cfg, REPO_ROOT, overwrite=args.overwrite, progress=True)
            info = build_report([out / "results.json"], out / "report", plans=_plans(PLAN_CONFIGS),
                                pdf=not args.no_pdf, repo_root=REPO_ROOT)
            print(info)
            return 0
        if args.cmd == "analyze":
            from .analysis import write_analysis
            from .runner import load_result
            print(write_analysis(args.experiment, load_result(args.exp001), load_result(args.results), args.out))
            return 0
        if args.cmd == "report":
            info = build_report([Path(p) for p in args.results], Path(args.out), plans=_plans(args.plans),
                                pdf=not args.no_pdf, repo_root=REPO_ROOT)
            print(info)
            return 0
    except ProtocolNotFrozenError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    except MatchLabError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2
