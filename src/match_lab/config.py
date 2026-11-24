# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Experiment configuration (versioned schema ``match-config/1.0.0``) and protocol-freeze gate."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ProtocolNotFrozenError, SchemaError

CONFIG_SCHEMA = "match-config/1.0.0"
ARMS_SEQUENTIAL = ("RANDOM", "POPULARITY", "EXPOSURE_BALANCED")
ARMS_CENTRAL = ("DA_A", "DA_B", "MAXW")
ALL_ARMS = ARMS_SEQUENTIAL + ARMS_CENTRAL
MODES = ("exploratory", "confirmatory")
_REQUIRED = {
    "config_schema": str, "experiment_id": str, "mode": str, "label": str, "n_a": int,
    "r_values": list, "rho_values": list, "instances_per_cell": int, "arms": list,
    "settings": list, "k": int, "delta": (int, float), "output_dir": str,
}


@dataclass(frozen=True)
class Setting:
    setting_id: str
    theta: float
    T: int


@dataclass(frozen=True)
class ExperimentConfig:
    raw: dict[str, Any]
    experiment_id: str
    mode: str
    label: str
    root_seed: int | None
    n_a: int
    r_values: tuple[float, ...]
    rho_values: tuple[float, ...]
    instances_per_cell: int
    arms: tuple[str, ...]
    settings: tuple[Setting, ...]
    k: int
    delta: float
    output_dir: str
    trace_memory: bool
    tie_scope: str = "global"

    @property
    def sha256(self) -> str:
        return config_sha256(self.raw)

    @property
    def n_runs(self) -> int:
        return (len(self.r_values) * len(self.rho_values) * self.instances_per_cell
                * len(self.settings) * len(self.arms))


def canonical_json(doc: Any) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def config_sha256(raw: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(raw)).hexdigest()


def _is_num(x: Any) -> bool:
    return not isinstance(x, bool) and isinstance(x, (int, float)) and math.isfinite(float(x))


def parse_config(raw: dict[str, Any]) -> ExperimentConfig:
    if not isinstance(raw, dict):
        raise SchemaError("config must be a JSON object")
    for key, typ in _REQUIRED.items():
        if key not in raw:
            raise SchemaError(f"config missing required key '{key}'")
        if isinstance(raw[key], bool) or not isinstance(raw[key], typ):
            raise SchemaError(f"config key '{key}' has wrong type {type(raw[key]).__name__}")
    if raw["config_schema"] != CONFIG_SCHEMA:
        raise SchemaError(f"unsupported config_schema {raw['config_schema']!r}, expected {CONFIG_SCHEMA}")
    if raw["mode"] not in MODES:
        raise SchemaError(f"mode must be one of {MODES}")
    seed = raw.get("root_seed")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or seed < 0):
        raise SchemaError("root_seed must be a non-negative integer or null")
    if raw["n_a"] < 0 or raw["instances_per_cell"] < 1 or raw["k"] < 1:
        raise SchemaError("n_a >= 0, instances_per_cell >= 1 and k >= 1 are required")
    if not _is_num(raw["delta"]) or raw["delta"] < 0:
        raise SchemaError("delta must be a finite number >= 0")
    for key in ("r_values", "rho_values"):
        if not raw[key] or not all(_is_num(v) for v in raw[key]) or len(set(raw[key])) != len(raw[key]):
            raise SchemaError(f"{key} must be a non-empty list of distinct finite numbers")
    if not raw["arms"] or any(a not in ALL_ARMS for a in raw["arms"]) or len(set(raw["arms"])) != len(raw["arms"]):
        raise SchemaError(f"arms must be distinct values from {ALL_ARMS}")
    settings = []
    for s in raw["settings"]:
        if not isinstance(s, dict) or set(s) != {"setting_id", "theta", "T"}:
            raise SchemaError("each setting needs exactly setting_id, theta, T")
        if not isinstance(s["setting_id"], str) or not _is_num(s["theta"]) or isinstance(s["T"], bool) \
                or not isinstance(s["T"], int) or s["T"] < 0:
            raise SchemaError(f"invalid setting {s!r}")
        settings.append(Setting(s["setting_id"], float(s["theta"]), int(s["T"])))
    if not settings or len({s.setting_id for s in settings}) != len(settings):
        raise SchemaError("settings must be non-empty with distinct setting_id")
    out = raw["output_dir"]
    if raw["mode"] == "exploratory" and not out.startswith("results/exploratory/"):
        raise SchemaError("exploratory output_dir must be under results/exploratory/")
    if raw["mode"] == "confirmatory" and out.startswith("results/exploratory"):
        raise SchemaError("confirmatory output_dir must not be under results/exploratory/")
    trace = raw.get("trace_memory", True)
    if not isinstance(trace, bool):
        raise SchemaError("trace_memory must be a boolean")
    tie_scope = raw.get("popularity_tie_scope", "global")
    if tie_scope not in ("global", "viewer"):
        raise SchemaError("popularity_tie_scope must be 'global' or 'viewer'")
    return ExperimentConfig(
        raw=raw, experiment_id=raw["experiment_id"], mode=raw["mode"], label=raw["label"],
        root_seed=seed, n_a=raw["n_a"], r_values=tuple(float(v) for v in raw["r_values"]),
        rho_values=tuple(float(v) for v in raw["rho_values"]),
        instances_per_cell=raw["instances_per_cell"], arms=tuple(raw["arms"]),
        settings=tuple(settings), k=raw["k"], delta=float(raw["delta"]), output_dir=out,
        trace_memory=trace, tie_scope=tie_scope,
    )


def load_config(path: str | Path) -> ExperimentConfig:
    with open(path, encoding="utf-8") as fh:
        return parse_config(json.load(fh))


_HEX64 = re.compile(r"^[0-9a-f]{64}$")


FREEZE_SCHEMA = "match-freeze/1.0.0"
FREEZE_RECORD = Path("research") / "freeze.json"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_freeze_record(repo_root: str | Path) -> dict[str, Any]:
    """Read ``research/freeze.json`` (schema ``match-freeze/1.0.0``); raise ProtocolNotFrozenError if absent or malformed."""
    path = Path(repo_root) / FREEZE_RECORD
    if not path.exists():
        raise ProtocolNotFrozenError(f"freeze record not found at {path}; confirmatory runs require the owner's freeze (G-FREEZE)")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProtocolNotFrozenError(f"freeze record {path} is not valid JSON: {exc}") from exc
    if not isinstance(doc, dict) or doc.get("freeze_schema") != FREEZE_SCHEMA:
        raise ProtocolNotFrozenError(f"freeze record {path} lacks freeze_schema {FREEZE_SCHEMA!r}")
    if not isinstance(doc.get("main_protocol"), dict) or not isinstance(doc.get("experiments"), dict):
        raise ProtocolNotFrozenError(f"freeze record {path} lacks main_protocol or experiments")
    return doc


def check_protocol_frozen(experiment_id: str, repo_root: str | Path,
                          cfg: "ExperimentConfig | None" = None) -> str:
    """Return the protocol hash if the experiment is frozen and nothing frozen has drifted.

    Checks, in order: the registry holds a 64-hex ``protocol_hash`` equal to the SHA-256 of the
    protocol file; the freeze record ``research/freeze.json`` lists the experiment with the same
    protocol hash; the main protocol ``research/protocol.md`` matches its frozen hash; and, when
    ``cfg`` is given, the config's canonical SHA-256 equals the frozen config hash. Raises
    ProtocolNotFrozenError otherwise. The freeze itself is the owner's act (G-FREEZE); this
    function only reads the registry and the freeze record and never writes them.
    """
    root = Path(repo_root)
    registry = root / "research" / "experiment_registry.csv"
    if not registry.exists():
        raise ProtocolNotFrozenError(f"registry not found at {registry}")
    with open(registry, encoding="utf-8", newline="") as fh:
        rows = {row["experiment_id"]: row for row in csv.DictReader(fh)}
    row = rows.get(experiment_id)
    if row is None:
        raise ProtocolNotFrozenError(f"{experiment_id} is not registered")
    recorded = (row.get("protocol_hash") or "").strip().lower()
    if not _HEX64.match(recorded):
        raise ProtocolNotFrozenError(
            f"{experiment_id} protocol is not frozen (registry protocol_hash = {row.get('protocol_hash')!r}); "
            "confirmatory runs require the owner's freeze (G-FREEZE)")
    protocol = root / row["protocol_path"]
    actual = _sha256_file(protocol)
    if actual != recorded:
        raise ProtocolNotFrozenError(
            f"{experiment_id} protocol file hash {actual} differs from the frozen hash {recorded}")
    freeze = load_freeze_record(root)
    entry = freeze["experiments"].get(experiment_id)
    if not isinstance(entry, dict):
        raise ProtocolNotFrozenError(f"{experiment_id} is not listed in the freeze record")
    if entry.get("protocol_sha256") != recorded or entry.get("protocol_path") != row["protocol_path"]:
        raise ProtocolNotFrozenError(
            f"{experiment_id}: registry and freeze record disagree on the frozen protocol")
    main = freeze["main_protocol"]
    main_path = root / str(main.get("path", ""))
    if not main.get("path") or not main_path.is_file() or _sha256_file(main_path) != main.get("sha256"):
        raise ProtocolNotFrozenError(
            f"main protocol {main.get('path')!r} is missing or differs from its frozen hash")
    if cfg is not None:
        if cfg.experiment_id != experiment_id:
            raise ProtocolNotFrozenError(f"config is for {cfg.experiment_id}, not {experiment_id}")
        frozen_cfg = entry.get("config_canonical_sha256")
        if cfg.sha256 != frozen_cfg:
            raise ProtocolNotFrozenError(
                f"{experiment_id} config hash {cfg.sha256} differs from the frozen config hash {frozen_cfg}")
    return recorded
