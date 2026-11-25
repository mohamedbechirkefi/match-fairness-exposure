<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# results/

Machine-readable outputs of runs: `results.json` (schema `match-result/1.0.0`), `run_manifest.json` (`match-manifest/1.0.0`), `metrics.csv`, and a generated `report/` (Markdown, CSV tables, SVG figures, PDF).

- `results/exploratory/`: **exploratory outputs only**. Pre-freeze runs (smoke, pilot, pilot-S, tie-key probe; J-0002 to J-0005), the M3 pipeline check (`m3_smoke`, J-0009) and the M4 diagnostics (`m4_confounders`, J-0014; `m4_horizon_probe`, J-0015). They test no hypothesis and change no frozen verdict.
- `results/confirmatory/`: the frozen EXP-001, EXP-002 and EXP-003 runs (M3; J-0010 to J-0012), with `SHA256SUMS`, generated reports, analysis tables and run logs.
- `results/quarantine/`: empty (J-0008, D-016).
- `results/raw/` is git-ignored for any large regenerated output.
