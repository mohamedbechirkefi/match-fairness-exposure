# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Experiment runner and result serialization.

For each cell (r, rho), instance and setting (theta, T), one market is generated and every
configured arm runs on it (paired design, common random numbers). Seeds are derived as
``SeedSequence(entropy=root_seed, spawn_key=(round(1000 r), round(1000 rho), instance))``,
so an instance is identified by its cell values and index, not by its position in a matrix.
The instance's sequence spawns two children: the market stream and the parent of the three
sequential-discovery streams. theta does not consume randomness and T only truncates the
same streams, so settings of one instance share their market draws.
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import os
import platform
import resource
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

import numpy as np
import scipy

from . import __version__
from .config import ExperimentConfig, check_protocol_frozen
from .errors import MatchLabError, SchemaError
from .market import GENERATOR_VERSION, MarketParams, generate_market
from .matching import da_a, da_b, max_weight, validate_matching
from .metrics import METRIC_NAMES, compute_metrics, metric_failures
from .schema import MANIFEST_SCHEMA, RESULT_SCHEMA, validate_manifest, validate_result
from .sequential import Policy, SequentialSeeds, SequentialSettings, simulate_sequential


def instance_seed(root_seed: int, r: float, rho: float, instance: int) -> tuple[np.random.SeedSequence, list[int]]:
    key = [int(round(r * 1000)), int(round(rho * 1000)), int(instance)]
    return np.random.SeedSequence(entropy=root_seed, spawn_key=tuple(key)), key


def run_arm(market, arm: str, settings: SequentialSettings, seq_seeds: SequentialSeeds) -> tuple[dict, dict, list[str]]:
    """Run one arm on one market. Returns (metrics, diagnostics without timing, failures)."""
    diag: dict[str, Any] = {"n_slates": None, "short_slates": None, "cap_short_slates": None,
                            "matches_by_round": None}
    if arm in ("RANDOM", "POPULARITY", "EXPOSURE_BALANCED"):
        out = simulate_sequential(market, Policy(arm), settings, seq_seeds)
        ma, mb, ea, eb = out.match_a, out.match_b, out.exposure_a, out.exposure_b
        diag.update(n_slates=out.n_slates, short_slates=out.short_slates,
                    cap_short_slates=out.cap_short_slates, matches_by_round=out.matches_by_round)
    elif arm == "DA_A":
        (ma, mb), ea, eb = da_a(market), None, None
    elif arm == "DA_B":
        (ma, mb), ea, eb = da_b(market), None, None
    elif arm == "MAXW":
        (ma, mb), ea, eb = max_weight(market), None, None
    else:  # unreachable after config validation
        raise MatchLabError(f"unknown arm {arm}")
    failures = validate_matching(ma, mb, market.acc_a, market.acc_b)
    metrics = compute_metrics(market, ma, mb, ea, eb)
    failures += metric_failures(metrics)
    if arm in ("DA_A", "DA_B") and metrics["blocking_pairs"]:
        failures.append(f"{arm} output has {metrics['blocking_pairs']} blocking pairs (implementation error)")
    return metrics, diag, failures


def git_state(repo_root: Path) -> tuple[str, bool]:
    try:
        rev = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(repo_root), "status", "--porcelain", "--", "src"],
                                    capture_output=True, text=True, check=True).stdout.strip())
        return rev, dirty
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True


def cpu_name() -> str:
    try:
        return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return platform.processor() or "unknown"


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_experiment(cfg: ExperimentConfig, repo_root: str | Path, *, overwrite: bool = False,
                   progress: bool = False) -> Path:
    """Run every (cell, instance, setting, arm) of ``cfg`` and write results, manifest and CSV.

    Refuses a confirmatory config unless the registry records a matching protocol freeze.
    Returns the output directory.
    """
    root = Path(repo_root).resolve()
    if cfg.mode == "confirmatory":
        check_protocol_frozen(cfg.experiment_id, root)  # raises ProtocolNotFrozenError
    if cfg.root_seed is None:
        raise SchemaError("root_seed is null; a run needs an explicit root seed")
    out_dir = (root / cfg.output_dir).resolve()
    if root not in out_dir.parents:
        raise SchemaError("output_dir must stay inside the repository")
    if (out_dir / "results.json").exists() and not overwrite:
        raise MatchLabError(f"{out_dir / 'results.json'} exists; refusing to overwrite raw results")
    rev, dirty = git_state(root)
    start, t0 = _utc(), time.perf_counter()
    runs: list[dict] = []
    exclusions: dict[str, str] = {}
    n_done = 0
    for r in cfg.r_values:
        for rho in cfg.rho_values:
            for inst in range(cfg.instances_per_cell):
                for st in cfg.settings:
                    ss, key = instance_seed(cfg.root_seed, r, rho, inst)
                    market_ss, seq_parent = ss.spawn(2)
                    seq_seeds = SequentialSeeds.from_parent(seq_parent)
                    params = MarketParams(n_a=cfg.n_a, r=r, rho=rho, theta=st.theta)
                    tg = time.perf_counter()
                    market = generate_market(params, market_ss)
                    gen_s = time.perf_counter() - tg
                    seq_settings = SequentialSettings(T=st.T, k=cfg.k, delta=cfg.delta)
                    inst_key = f"r{r:g}-rho{rho:g}-i{inst:03d}-{st.setting_id}"
                    for arm in cfg.arms:
                        run_id = f"{cfg.experiment_id}/{inst_key}/{arm}"
                        ta = time.perf_counter()
                        try:
                            metrics, diag, failures = run_arm(market, arm, seq_settings, seq_seeds)
                        except Exception as exc:  # recorded, never silently dropped
                            metrics = {name: None for name in METRIC_NAMES}
                            diag = {"n_slates": None, "short_slates": None, "cap_short_slates": None,
                                    "matches_by_round": None}
                            failures = [f"exception: {type(exc).__name__}: {exc}"]
                        runtime = time.perf_counter() - ta
                        peak = None
                        if cfg.trace_memory and inst == 0 and not failures:
                            # tracemalloc slows numpy code several-fold, so timing is never traced.
                            # The first instance of each (cell, setting, arm) is re-run under
                            # tracemalloc for its peak; the re-run must reproduce the metrics.
                            tracemalloc.start()
                            try:
                                metrics2, _, _ = run_arm(market, arm, seq_settings, seq_seeds)
                                peak = int(tracemalloc.get_traced_memory()[1])
                            finally:
                                tracemalloc.stop()
                            if metrics2 != metrics:
                                failures.append("non-deterministic: traced re-run changed the metrics")
                        if failures:
                            exclusions.setdefault(inst_key, f"{arm}: {'; '.join(failures)}")
                        runs.append({
                            "run_id": run_id, "instance_key": inst_key, "arm": arm,
                            "cell": {"r": r, "rho": rho, "n_a": market.n_a, "n_b": market.n_b},
                            "setting": {"setting_id": st.setting_id, "theta": st.theta, "T": st.T,
                                        "k": cfg.k, "delta": cfg.delta},
                            "instance": inst, "seed": {"root_seed": cfg.root_seed, "spawn_key": key},
                            "valid": not failures, "failures": failures, "metrics": metrics,
                            "diagnostics": {"runtime_s": runtime, "market_generation_s": gen_s,
                                            "peak_traced_bytes": peak, **diag},
                        })
                        n_done += 1
                        if progress and n_done % 50 == 0:
                            print(f"  {n_done}/{cfg.n_runs} runs", file=sys.stderr)
    wall = time.perf_counter() - t0
    result = {
        "schema_version": RESULT_SCHEMA, "experiment_id": cfg.experiment_id, "mode": cfg.mode,
        "label": cfg.label, "created_utc": _utc(), "config": cfg.raw, "config_sha256": cfg.sha256,
        "code_revision": rev + ("+dirty" if dirty else ""), "generator_version": GENERATOR_VERSION,
        "runs": runs,
        "exclusions": [{"instance_key": k, "reason": v} for k, v in sorted(exclusions.items())],
    }
    validate_result(result)  # validate at export
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    manifest = {
        "manifest_schema": MANIFEST_SCHEMA, "experiment_id": cfg.experiment_id, "mode": cfg.mode,
        "label": cfg.label, "config_sha256": cfg.sha256, "root_seed": cfg.root_seed,
        "git_revision": rev, "git_dirty": dirty, "match_lab_version": __version__,
        "python": sys.version.split()[0],
        "packages": {"numpy": np.__version__, "scipy": scipy.__version__},
        "platform": platform.platform(), "cpu": cpu_name(), "cpu_count": os.cpu_count(),
        "start_utc": start, "end_utc": _utc(), "wall_clock_s": wall,
        # ru_maxrss is bytes on macOS and kilobytes on Linux
        "peak_rss_bytes": int(rss if sys.platform == "darwin" else rss * 1024),
        "peak_memory_method": ("per run: tracemalloc peak of a deterministic re-run, first instance of each "
                               "(cell, setting, arm) only, null otherwise; process: ru_maxrss; runtime_s is never traced"),
        "n_runs": len(runs), "n_invalid": sum(not r["valid"] for r in runs),
        "runs": [{"run_id": r["run_id"], "spawn_key": r["seed"]["spawn_key"],
                  "runtime_s": r["diagnostics"]["runtime_s"],
                  "peak_traced_bytes": r["diagnostics"]["peak_traced_bytes"]} for r in runs],
    }
    validate_manifest(manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(out_dir / "results.json", result)
    _write_json(out_dir / "run_manifest.json", manifest)
    write_metrics_csv(result, out_dir / "metrics.csv")
    return out_dir


def _write_json(path: Path, doc: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def load_result(path: str | Path) -> dict:
    """Load and validate a result document (validate at import; fail closed)."""
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    validate_result(doc)
    return doc


CSV_FIELDS = ["run_id", "instance_key", "arm", "r", "rho", "n_a", "n_b", "setting_id", "theta", "T",
              "instance", "valid", *METRIC_NAMES, "runtime_s", "peak_traced_bytes", "short_slates",
              "cap_short_slates"]


def write_metrics_csv(result: dict, path: Path) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for run in result["runs"]:
            row = {"run_id": run["run_id"], "instance_key": run["instance_key"], "arm": run["arm"],
                   **run["cell"], "setting_id": run["setting"]["setting_id"], "theta": run["setting"]["theta"],
                   "T": run["setting"]["T"], "instance": run["instance"], "valid": run["valid"],
                   **{k: ("" if v is None else v) for k, v in run["metrics"].items()},
                   "runtime_s": run["diagnostics"]["runtime_s"],
                   "peak_traced_bytes": run["diagnostics"]["peak_traced_bytes"],
                   "short_slates": run["diagnostics"]["short_slates"],
                   "cap_short_slates": run["diagnostics"]["cap_short_slates"]}
            w.writerow({k: ("" if v is None else v) for k, v in row.items()})
