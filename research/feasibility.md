<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Feasibility audit (M0, 2026-11-24)

## 1. Hardware (confirmed by commands)

| Item | Command | Output |
|---|---|---|
| CPU | `sysctl -n machdep.cpu.brand_string` | Apple M1 Pro |
| Cores | `sysctl -n hw.ncpu` | 10 |
| RAM | `sysctl -n hw.memsize` | 17179869184 bytes (16 GiB) |
| OS | `sw_vers` | macOS 15.3.1 (build 24D70) |
| Free disk | `df -h ..` (the `labs/` folder) | 128 GiB available of 460 GiB |

## 2. Tools (confirmed by commands)

Locations are relative to the repository root (2026-11-26: absolute home paths replaced by relative ones, owner, 2026-11-26, decision sheet, B9; the M0 commands were run with the absolute paths).

| Tool | Location | Version output |
|---|---|---|
| Python | `/usr/local/bin/python3` | Python 3.12.1 |
| uv | `../.tools/py/bin/uv` | uv 0.9.5 (d5f39331a 2025-10-21) |
| typst (Python package) | `../.tools/py/bin/python` | typst 0.15.0 |
| pypdf, pillow | same | pypdf 6.20.0, pillow 11.3.0 |
| pandoc | `../.tools/pandoc` (a single binary, not a folder) | pandoc 3.6.3 |
| Node | `../../helix/.tools/node/bin/node` (read-only use) | v22.23.3 |
| git | system | git version 2.42.1 |
| TeX | `which tex pdflatex xelatex typst` | none found |

## 3. Publication toolchain (decision D-002)

Markdown is canonical. PDF: `pandoc X.md -s -t typst -V mainfont="Libertinus Serif" -o X.typ`, then `typst.compile("X.typ", output="X.pdf")` with the Python package. Without `-V mainfont=...`, pandoc's default Typst template emits `font: ()` and the typst package fails with "font fallback list must not be empty" (observed in M0). LaTeX: `pandoc manuscript.md -s -t latex -o manuscript.tex`, not compiled locally.

Exploratory smoke check (M0): the manuscript skeleton converted and compiled to a 1-page PDF in the session scratchpad; pypdf extracted the headings. The PDF was not committed and was not visually inspected as an image.

## 4. Compute estimate (planning, unmeasured)

Planned matrix: 810 (EXP-001) + 810 (EXP-002) + 1,440 (EXP-003) = 3,060 runs, each on at most 200 x 300 agents. Each sequential run is at most 20 rounds of slates of 5; each centralized run is one deferred acceptance or one rectangular assignment. Expected to fit well inside the 2-hour-per-experiment budget on this machine, but this is unmeasured; the smoke run in M2/M3 will time it.

## 5. Time budget

Five focused development days (master prompt). Planned allocation: M0 and M1 drafts (day 1), M2 core and tests (day 2), M3 runs and reports (day 3), M4 interpretation and manuscript (day 4), M5 demo and M6 release candidate (day 5). If threatened, cut in this order: EXP-003 S1 (keep S2 and S3), demo features beyond the centerpiece, EXP-002 MAXW arm. Never cut controls, reports or the claims audit.

## 6. Cost

Zero. No paid service, API, dataset, compute or hosting. Dependencies are free. Installed package metadata (checked in M0): pytest "License: MIT"; hypothesis "License-Expression: MPL-2.0"; numpy and scipy embed BSD-style licence texts ("Redistribution and use in source and binary forms..."); bundled third-party components to be re-checked in the M6 licence scan.

## 7. Sources and licences

See `research/literature_review.md` (sources, verification levels) and `data/manifest.json` (datasets considered, none used).

## 8. Explicit scope and exclusions

In scope: synthetic markets, the six arms, the metrics in `research/protocol.md`, a static demo, the manuscript and per-experiment reports. Excluded: real profiles or any personal data, protected-attribute inference, claims about any platform's internals, learning-to-rank models, strategic agents, paid services.

## 9. Fallback

If the planned matrix is too slow: reduce n_A to 100 before the freeze (owner decision). If the demo cannot be built: a static HTML page of precomputed figures, still offline.
