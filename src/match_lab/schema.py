# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Versioned result and manifest schemas, validated at export and at import.

Result document ``match-result/1.0.0``::

    {
      "schema_version": "match-result/1.0.0",
      "experiment_id": str, "mode": "exploratory" | "confirmatory", "label": str,
      "created_utc": str, "config": {...}, "config_sha256": hex64,
      "code_revision": str, "generator_version": str,
      "runs": [RunRecord, ...],
      "exclusions": [{"instance_key": str, "reason": str}, ...]
    }

RunRecord::

    {
      "run_id": str, "instance_key": str, "arm": str,
      "cell": {"r": num, "rho": num, "n_a": int, "n_b": int},
      "setting": {"setting_id": str, "theta": num, "T": int, "k": int, "delta": num},
      "instance": int, "seed": {"root_seed": int, "spawn_key": [int, ...]},
      "valid": bool, "failures": [str, ...],
      "metrics": {name: num | null for every name in METRIC_NAMES},
      "diagnostics": {"runtime_s": num, "peak_traced_bytes": int | null,
                      "n_slates": int | null, "short_slates": int | null,
                      "cap_short_slates": int | null, "matches_by_round": [int] | null}
    }
"""

from __future__ import annotations

import math
import re
from typing import Any

from .config import ALL_ARMS, MODES
from .errors import SchemaError
from .metrics import METRIC_NAMES

RESULT_SCHEMA = "match-result/1.0.0"
MANIFEST_SCHEMA = "match-manifest/1.0.0"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _num(x: Any) -> bool:
    return not isinstance(x, bool) and isinstance(x, (int, float)) and math.isfinite(float(x))


def _int(x: Any) -> bool:
    return not isinstance(x, bool) and isinstance(x, int)


def _need(doc: dict, key: str, pred, where: str) -> Any:
    if not isinstance(doc, dict) or key not in doc:
        raise SchemaError(f"{where}: missing '{key}'")
    if not pred(doc[key]):
        raise SchemaError(f"{where}: invalid value for '{key}': {doc[key]!r}")
    return doc[key]


def validate_run(run: Any, where: str = "run") -> None:
    if not isinstance(run, dict):
        raise SchemaError(f"{where}: not an object")
    rid = _need(run, "run_id", lambda v: isinstance(v, str) and v, where)
    where = f"run {rid}"
    _need(run, "instance_key", lambda v: isinstance(v, str) and v, where)
    _need(run, "arm", lambda v: v in ALL_ARMS, where)
    cell = _need(run, "cell", lambda v: isinstance(v, dict), where)
    _need(cell, "r", lambda v: _num(v) and v >= 1, where + ".cell")
    _need(cell, "rho", lambda v: _num(v) and 0 <= v <= 1, where + ".cell")
    _need(cell, "n_a", lambda v: _int(v) and v >= 0, where + ".cell")
    _need(cell, "n_b", lambda v: _int(v) and v >= 0, where + ".cell")
    st = _need(run, "setting", lambda v: isinstance(v, dict), where)
    _need(st, "setting_id", lambda v: isinstance(v, str), where + ".setting")
    _need(st, "theta", lambda v: _num(v) and 0 <= v <= 1, where + ".setting")
    _need(st, "T", lambda v: _int(v) and v >= 0, where + ".setting")
    _need(st, "k", lambda v: _int(v) and v >= 1, where + ".setting")
    _need(st, "delta", lambda v: _num(v) and v >= 0, where + ".setting")
    _need(run, "instance", lambda v: _int(v) and v >= 0, where)
    seed = _need(run, "seed", lambda v: isinstance(v, dict), where)
    _need(seed, "root_seed", lambda v: _int(v) and v >= 0, where + ".seed")
    _need(seed, "spawn_key", lambda v: isinstance(v, list) and all(_int(x) and x >= 0 for x in v), where + ".seed")
    valid = _need(run, "valid", lambda v: isinstance(v, bool), where)
    failures = _need(run, "failures", lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v), where)
    if valid != (len(failures) == 0):
        raise SchemaError(f"{where}: 'valid' disagrees with 'failures'")
    metrics = _need(run, "metrics", lambda v: isinstance(v, dict), where)
    if set(metrics) != set(METRIC_NAMES):
        raise SchemaError(f"{where}: metric names {sorted(metrics)} differ from schema {sorted(METRIC_NAMES)}")
    for name, v in metrics.items():
        if v is not None and not _num(v):
            raise SchemaError(f"{where}: metric {name} must be a finite number or null, got {v!r}")
    diag = _need(run, "diagnostics", lambda v: isinstance(v, dict), where)
    _need(diag, "runtime_s", lambda v: _num(v) and v >= 0, where + ".diagnostics")
    for key in ("peak_traced_bytes", "n_slates", "short_slates", "cap_short_slates"):
        _need(diag, key, lambda v: v is None or (_int(v) and v >= 0), where + ".diagnostics")
    _need(diag, "matches_by_round",
          lambda v: v is None or (isinstance(v, list) and all(_int(x) and x >= 0 for x in v)), where + ".diagnostics")


def validate_result(doc: Any) -> None:
    """Raise SchemaError unless ``doc`` is a valid ``match-result/1.0.0`` document."""
    if not isinstance(doc, dict):
        raise SchemaError("result document must be a JSON object")
    _need(doc, "schema_version", lambda v: v == RESULT_SCHEMA, "result")
    _need(doc, "experiment_id", lambda v: isinstance(v, str) and v, "result")
    _need(doc, "mode", lambda v: v in MODES, "result")
    _need(doc, "label", lambda v: isinstance(v, str), "result")
    _need(doc, "created_utc", lambda v: isinstance(v, str) and v, "result")
    _need(doc, "config", lambda v: isinstance(v, dict), "result")
    _need(doc, "config_sha256", lambda v: isinstance(v, str) and bool(_HEX64.match(v)), "result")
    _need(doc, "code_revision", lambda v: isinstance(v, str) and v, "result")
    _need(doc, "generator_version", lambda v: isinstance(v, str) and v, "result")
    runs = _need(doc, "runs", lambda v: isinstance(v, list), "result")
    ids = set()
    for k, run in enumerate(runs):
        validate_run(run, f"runs[{k}]")
        if run["run_id"] in ids:
            raise SchemaError(f"duplicate run_id {run['run_id']}")
        ids.add(run["run_id"])
    _need(doc, "exclusions", lambda v: isinstance(v, list) and all(
        isinstance(e, dict) and isinstance(e.get("instance_key"), str) and isinstance(e.get("reason"), str)
        for e in v), "result")
    if doc["config"].get("mode") != doc["mode"]:
        raise SchemaError("result mode differs from its config mode")


def validate_manifest(doc: Any) -> None:
    if not isinstance(doc, dict):
        raise SchemaError("manifest must be a JSON object")
    _need(doc, "manifest_schema", lambda v: v == MANIFEST_SCHEMA, "manifest")
    for key in ("experiment_id", "mode", "git_revision", "python", "platform", "cpu", "start_utc", "end_utc"):
        _need(doc, key, lambda v: isinstance(v, str), "manifest")
    _need(doc, "config_sha256", lambda v: isinstance(v, str) and bool(_HEX64.match(v)), "manifest")
    _need(doc, "git_dirty", lambda v: isinstance(v, bool), "manifest")
    _need(doc, "packages", lambda v: isinstance(v, dict), "manifest")
    _need(doc, "wall_clock_s", lambda v: _num(v) and v >= 0, "manifest")
    _need(doc, "peak_rss_bytes", lambda v: v is None or (_int(v) and v >= 0), "manifest")
    runs = _need(doc, "runs", lambda v: isinstance(v, list), "manifest")
    for r in runs:
        _need(r, "run_id", lambda v: isinstance(v, str), "manifest.runs")
        _need(r, "spawn_key", lambda v: isinstance(v, list), "manifest.runs")
        _need(r, "runtime_s", lambda v: _num(v) and v >= 0, "manifest.runs")
