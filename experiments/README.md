<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# experiments/

Run configurations (`configs/*.json`, schema `match-config/1.0.0`) consumed by `python -m match_lab run --config ...`. The authoritative protocols and reports live in `research/experiments/EXP-NNN/`.

- Exploratory: `smoke.json` (protocol section 5), `pilot.json`, `pilot_sensitivity.json`, `probe_tie_scope.json` (pre-freeze planning run), `m3_smoke.json` (M3 pipeline check) and `m4_horizon_probe.json` (M4 horizon-extension probe, J-0015). Outputs go to `results/exploratory/`.
- Confirmatory: `EXP-001.json`, `EXP-002.json`, `EXP-003.json`, frozen by the owner on 2026-11-24 (root seed 20261124; hashes in `research/freeze.json`). The runner refuses any change to them (D-013). They were run in M3.
- `exploratory/`: M4 exploratory analysis scripts (`m4_confounders.py`, J-0014; `m4_horizon_probe_analysis.py`, J-0015). They read committed outputs and change no frozen verdict.
