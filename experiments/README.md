<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# experiments/

Run configurations (`configs/*.json`, schema `match-config/1.0.0`) consumed by `python -m match_lab run --config ...`. The authoritative protocols and reports live in `research/experiments/EXP-NNN/`.

- Exploratory: `smoke.json` (protocol section 5), `pilot.json`, `pilot_sensitivity.json`, `probe_tie_scope.json`. Outputs go to `results/exploratory/`.
- Confirmatory drafts: `EXP-001.json`, `EXP-002.json`, `EXP-003.json` mirror protocol v0.1 with `root_seed: null`. The runner refuses them until the owner freezes the protocol and records its hash in the registry; the root seed is set at the freeze and must differ from the exploratory seeds (D-009).
