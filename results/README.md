<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# results/

Machine-readable outputs of runs: `results.json` (schema `match-result/1.0.0`), `run_manifest.json` (`match-manifest/1.0.0`), `metrics.csv`, and a generated `report/` (Markdown, CSV tables, SVG figures, PDF).

- `results/exploratory/`: **exploratory runs only** (smoke, pilot, pilot-S, tie-key probe; journal entries J-0002 to J-0005). They were made before the protocol freeze to measure runtime, seed spread and degenerate cases. They test no hypothesis and are not findings.
- `results/confirmatory/`: does not exist yet. Confirmatory runs need the owner's freeze (G-FREEZE); the runner refuses them until then.
- `results/raw/` is git-ignored for any large regenerated output.
