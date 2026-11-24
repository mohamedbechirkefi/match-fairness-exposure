<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-002 reproduction record

Executed in session M3 (2026-11-24 UTC). Commands run from the repository root; the confirmatory run passes the freeze guard only while the freeze record, registry, protocols and config are unchanged. Re-running into the same output directory is refused unless `--overwrite` is given; to reproduce, copy the config with a new `output_dir` or run in a clean clone.

## Commands as executed

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q                      # 103 passed before the run
nice -n 10 .venv/bin/python -m match_lab run --config experiments/configs/EXP-002.json
.venv/bin/python -m match_lab report --results results/confirmatory/EXP-001/results.json results/confirmatory/EXP-002/results.json --out results/confirmatory/EXP-002/report
.venv/bin/python -m match_lab analyze --experiment EXP-002 --exp001 results/confirmatory/EXP-001/results.json --results results/confirmatory/EXP-002/results.json --out results/confirmatory/EXP-002/analysis
```

(All were run under `nice -n 10`. Equivalent to the protocol's `uv run --frozen python -m match_lab ...` commands.)

## Provenance

| Item | Value |
|---|---|
| Code revision | cfc90d0dfa9aa9058ee780a8d8fe3abdc77343d3 (clean) |
| Config file SHA-256 | 105c89cc03e8d613cdc593e79775116f0bb38bfa0d55802768c6ac2823c77ac3 |
| Config canonical SHA-256 | 2bd7ee667eaadef716496cff55bf2a343743f0984e4c1f44552279dea1a540b7 |
| Data manifest SHA-256 | 506b2c412984c7a41c436b889c159c5a139744c4a1ccdf7396a7a88427f216cf (synthetic data only) |
| Root seed | 20261124 |
| Start, end (UTC) | 2026-11-24T23:33:51Z, 2026-11-24T23:34:06Z |
| Wall clock | 13.6 s |
| Exit status | 0 |
| Runs | 810 planned, 810 executed, 0 invalid, 0 excluded |
| Hardware | Apple M1 Pro, 10 cores, macOS 15.3.1; Python 3.12.1, numpy 2.3.5, scipy 1.16.3 |
| Log | results/confirmatory/logs/EXP-002.log |
| Raw results checksums | results/confirmatory/EXP-002/SHA256SUMS |

Per-run ids, spawn keys and runtimes: `run_manifest.json` in this folder (copy of `results/confirmatory/EXP-002/run_manifest.json`). Per-run start and end times are not recorded; the runner records each run's duration and the experiment's start and end.

## Expected outputs

Metric columns of `metrics.csv` reproduce exactly for the same config and seed (deterministic; checked in-run by a traced re-run of the first instance per cell and arm). Runtimes differ between executions.
