<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: session M0 (bootstrap and feasibility, M1 drafts)

**Milestone:** M0. **Starting state:** commit 647e5b8 (master prompt and the owner's licence package), working tree clean.

### Decisions
D-001 licence is the owner's choice; D-002 zero-cost toolchain without TeX; D-003 fully synthetic design, real datasets excluded; D-004 protocol proposal v0.1 (not frozen); D-005 dependency lock with a two-week cutoff. Details in `research/decision_log.md`.

### Commands and actual outputs
- `git log --oneline`: `647e5b8 Initial commit: MATCH master prompt and the owner's licence package (...)`; `git status`: clean.
- Hardware: `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize` gave `Apple M1 Pro`, `10`, `17179869184`; `sw_vers` gave macOS 15.3.1 (24D70); `df -h` gave 128 GiB available.
- Tools: `python3 --version` gave Python 3.12.1; `uv --version` gave uv 0.9.5 (d5f39331a 2025-10-21); typst 0.15.0, pypdf 6.20.0, pillow 11.3.0; pandoc 3.6.3 (the path `labs/.tools/pandoc` is the binary itself); node v22.23.3; git 2.42.1; `which tex pdflatex xelatex typst` found none.
- `uv lock --python /usr/local/bin/python3`: "Resolved 11 packages in 208ms". Locked: numpy 2.3.5, scipy 1.16.3, pytest 8.4.2, hypothesis 6.170.15 (with `exclude-newer = 2026-11-10T00:00:00Z`). `uv lock --check`: "Resolved 11 packages in 7ms" (consistent).
- `uv sync --frozen`: first attempt failed with hatchling `OSError: Readme file does not exist: README.md`; after writing README.md, installed 10 packages.
- `uv run --frozen pytest -q`: `1 passed in 0.60s` (one import test; no algorithm exists).
- `pandoc manuscript.md -s -t latex -o manuscript.tex`: exit 0 (not compiled; no TeX).
- Exploratory toolchain smoke (scratchpad only): `pandoc -t typst` then `typst.compile` failed with "font fallback list must not be empty"; with `-V mainfont="Libertinus Serif"` it produced a 1-page PDF whose extracted text is the skeleton headings. Not committed; not visually inspected.
- Literature and datasets: WebSearch and WebFetch; sources opened and their verification levels are in `research/literature_review.md`. Two pages returned HTTP 403 (Taylor and Francis article page; Columbia statmodeling blog post). No dataset downloaded.

### Files created
CLAUDE.md, roadmap.md, progress.md, README.md, CITATION.cff, pyproject.toml, uv.lock; research/{protocol.md, feasibility.md, decision_log.md, literature_review.md, limitations.md, claims_register.csv (header only), experiment_journal.jsonl, experiment_registry.csv}; research/experiments/EXP-001..003/protocol.md; research/paper/{manuscript.md (headings only), manuscript.tex (generated), references.bib, supplementary.md, figures/README.md}; research/publication/{artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md}; data/manifest.json; READMEs in results/, src/, tests/, experiments/, demo/, articles/; src/match_lab/__init__.py; tests/test_package.py. Appended a development-commands section to CONTRIBUTING.md. No licence file changed.

### Failures
Two command failures, both resolved and recorded above (typst default font; uv sync before README existed). Two source pages inaccessible (HTTP 403).

### Outstanding risks
- Runtime of the full matrix is unmeasured.
- The primary contrast may be small relative to between-instance variation; N = 30 per cell is a proposal.
- Literature support is mostly at abstract level; roth1982 and gale1962 are verified at metadata level only.
- The EXPOSURE_BALANCED cap may cause many short slates in unbalanced cells (monitored).

### Owner decisions needed
1. Review and freeze (or amend) `research/protocol.md` and EXP-001 to EXP-003 protocols (G-FREEZE), including N per cell, the primary metric W and the nondirectional H1.
2. Confirm the fully synthetic scope (no real dataset; rights for the Speed Dating and libimseti data are unclear).
3. Approve authorship metadata for CITATION.cff and the manuscript.

### Next action
M2: implement the market generator, RANDOM baseline, deferred acceptance and metrics with the M2 test list (stability on hand-computed examples, no duplicates, capacity, empty pools), then the exploratory smoke run with timing. Confirmatory runs wait for the freeze.
