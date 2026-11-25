<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Reproducibility report (M6, 2026-11-25)

Status at M0: nothing to reproduce yet. Completed in session M6 (release candidate) with the actual command outputs below. Nothing was pushed or published.

## Checklist

- [x] Clean clone into a separate directory (local clone of commit 2a3f55c into the session scratchpad; no network).
- [x] `uv sync --frozen` succeeds with the committed `uv.lock`.
- [x] Full test suite runs; actual pass/fail counts recorded (clone: 112 passed, 0 failed).
- [x] Smoke reproduction matches committed smoke results within the documented tolerance (all metric columns identical; only `runtime_s` differs, as documented).
- [x] Reports and figures regenerate from raw results with one command (all 15 committed report tables and all 9 committed analysis files, figures included, byte-identical).
- [ ] Demo builds offline. The demo was installed with `npm ci --prefer-offline` from the local npm cache and built without error, and the built page passed the offline-after-load check; the network was not disabled during the install, so a strictly offline install was not proven.
- [x] Data manifest checks: synthetic generator version, parameters, seeds; no external data bundled.
- [x] Environment recorded: OS, CPU, Python and package versions, git revision.

## Environment

| Item | Value |
|---|---|
| Machine | Apple M1 Pro, 10 cores, arm64, macOS 15.3.1 |
| Python | 3.12.1; numpy 2.3.5, scipy 1.16.3, pytest 8.4.2, hypothesis 6.170.15 (from `uv.lock`) |
| uv | 0.9.5 (d5f39331a 2025-10-21) |
| Node | v22.23.3 (shared read-only installation) |
| PDF toolchain | pandoc 3.6.3; `typst` Python package 0.15.0; pypdf 6.20.0 (metadata check) |
| Clean-clone revision | 2a3f55cabb0bd50080a5bd358181755215f197c8 (M5 commit) |

## 1. Clean clone (commit 2a3f55c)

Commands run in `<scratch>/clone`, a local `git clone` of the working repository at its HEAD. The clone was deleted at the end of the session.

| Step | Command | Actual output |
|---|---|---|
| Clone | `git clone -q <repo> <scratch>/clone` | HEAD 2a3f55c |
| Install | `uv sync --frozen --all-groups --all-extras` | resolved from `uv.lock`; numpy 2.3.5, scipy 1.16.3, pytest 8.4.2 and the other locked packages installed |
| Tests | `.venv/bin/python -m pytest -q` | 112 passed in 56.72 s |
| Smoke | `nice -n 10 .venv/bin/python -m match_lab smoke --overwrite --no-pdf` | 120 runs, 2.5 s wall clock; compared with the committed `results/exploratory/smoke/metrics.csv`: 120 rows each, every column identical except `runtime_s` |
| Report tables | `match_lab report` for EXP-001, EXP-002 (with the EXP-001 results, as in `research/experiments/EXP-002/reproduction.md`) and EXP-003, into the scratchpad, `--no-pdf` | 15 committed report tables compared, 0 differ |
| Frozen analyses | `match_lab analyze --experiment EXP-002` and `EXP-003` into the scratchpad | `diff -rq` against the committed `analysis/` folders: identical (5 and 4 files, figures included) |
| Demo install | `cd demo && npm ci --prefer-offline` | added 53 packages |
| Demo tests | `npm test` | Test Files 2 passed (2); Tests 26 passed (26) |
| Demo build | `npm run build` | built; index JS 252.10 kB, worker 6.26 kB, CSS 8.28 kB |
| Demo check | `node tools/a11y_check.mjs dist` | 9 PASS lines, then `A11Y-CHECK PASS` |
| Export determinism | `python scripts/export_demo_data.py`, then `--check`, then `python scripts/make_sandbox_fixture.py` | "wrote demo/public/data/results.json (34173 bytes)"; "results.json up to date"; "wrote demo/src/fixtures/engine_fixture.json (52231 bytes)"; `git status --short` empty (0 lines) |

The smoke run's report Markdown and the arm-summary table differ from the committed ones only in the recorded code revision and in runtime columns, which the reproduction records document as varying between executions.

The `a11y_check` output in the clone:

    PASS results render (no fail-closed panel): 5 experiment panels
    PASS text contrast, light scheme (WCAG AA)
    PASS text contrast, dark scheme (WCAG AA)
    PASS keyboard reaches every focusable element: 24 reached of 24
    PASS visible focus indicator
    PASS no horizontal page scroll at 360 px: overflow 0px
    PASS reduced motion: no running animations: 0 running
    PASS no request leaves the local origin
    PASS offline after first load: results stay, sandbox runs: Sandbox output (seed 1, r = 1.0, rho = 0.5, theta = 0.5, T = 4): mean welfare W
    A11Y-CHECK PASS

No step failed in the clean clone, so no fix had to be re-checked in a fresh clone. The M6 changes made afterwards in the working repository (PDF builder, check scripts, text fixes) were verified there; see section 4.

## 2. Data and artifact manifests

- `data/manifest.json`: SHA-256 506b2c412984c7a41c436b889c159c5a139744c4a1ccdf7396a7a88427f216cf, equal to the value recorded in the run logs and reports of EXP-001 to EXP-003, so the manifest is unchanged since the confirmatory runs. One synthetic generator (GEN-match-market v1, parameters n_A, r, rho, theta, root_seed, draw order recorded). Two external datasets are listed as examined, not downloaded and not used (`sha256` null). No external data file is in the repository.
- `results/confirmatory/EXP-00N/SHA256SUMS`: `shasum -a 256 -c` gives 11, 21 and 21 "OK" lines for EXP-001, EXP-002 and EXP-003, and no failure.
- Config hashes: the canonical SHA-256 of `experiments/configs/EXP-001.json`, `EXP-002.json`, `EXP-003.json` and `m4_horizon_probe.json`, computed with `match_lab.config.canonical_json`, equal the values in `research/publication/artifact_manifest.json`.
- `research/publication/artifact_manifest.json`: 29 entries; 32 file paths named in `result_path` all resolve (abbreviated names such as `cells.csv` resolve within the folder of the entry's first path); 7 further items are descriptions, not paths (for example "run manifests", "qualitative"). Every code revision named exists in the git history (cfc90d0, e1050b2, cff9d7c).
- `research/publication/evidence_audit.py`: 36 PASS, 0 FAIL.

## 3. PDFs

Built with `python scripts/build_pdfs.py` (the repository builder `match_lab.report.build_pdf`: pandoc 3.6.3 to Typst, compiled by the `typst` Python package 0.15.0, Typst root `research/`).

| File | Pages | Size (bytes) | PDF title metadata |
|---|---|---|---|
| `research/paper/manuscript.pdf` | 15 | about 246,000 | the manuscript title |
| `research/paper/supplementary.pdf` | 8 | about 156,000 | "MATCH: Supplementary material" |
| `research/experiments/EXP-001/report.pdf` | 9 | about 272,000 | "EXP-001 report: exposure policies in sequential discovery" |
| `research/experiments/EXP-002/report.pdf` | 8 | about 219,000 | "EXP-002 report: centralized two-sided matching versus sequential discovery" |
| `research/experiments/EXP-003/report.pdf` | 8 | about 217,000 | "EXP-003 report: sensitivity of the exposure-policy effect" |

Every page of the manuscript, the supplementary file and the three reports was rendered to PNG (60 ppi; figure pages also at 150 ppi) and inspected. pypdf: every PDF has a title, no e-mail address and no local path in its metadata or text. Each file is under 5 MB. Exact sizes change with each build because Typst records the build time.

Fixes made in the builder or the Markdown source during inspection, never in a PDF:

1. A wrapped Typst source line starting with "80." became a numbered list ("80. It was identical ..."); fixed with `--wrap=none`.
2. Tables had equal-width columns, so labels such as "EXPOSURE_BALANCED - RANDOM" overflowed into the next column; fixed with natural widths (`--columns=10000`), left-aligned 9 pt cells, unjustified cell text and line breaks allowed after "_".
3. SHA-256 and git hashes overflowed the supplementary S3 table and the text width; they may now break every 8 characters.
4. Figure captions read "Figure 1: Figure 1 (FIG-...)"; figures are no longer auto-numbered, because the captions carry their own label.
5. The PDF title metadata was empty (the pandoc template sets it to none); the builder now sets it after the template's set-up.
6. In the three experiment reports, 10 lists that followed a paragraph line without a blank line printed as raw "- " text; a blank line was inserted (no wording changed).
7. The manuscript embeds figures from `research/experiments/`, outside its folder; the Typst root is now `research/`.

Not fixed, recorded: in FIG-EXP-003-theta-forest the first two row labels are truncated by the figure generator ("EXP EXP-001 base (T 40, theta 0."). The figure is a committed generated artifact of the frozen analysis and was not regenerated.

`research/paper/manuscript.tex` was regenerated with `pandoc manuscript.md -s -t latex` (pandoc 3.6.3), keeping its two header comment lines. It is not compiled (no TeX distribution, D-002).

## 4. Checks in the working repository after the M6 changes

| Command | Actual output |
|---|---|
| `python scripts/check_references.py` | PASS references: 36 author-year citations, 8 bib entries, 0 unresolved, 0 uncited |
| `python scripts/check_links.py` | PASS links: 48 relative links in 47 Markdown files, 0 broken |
| `python research/publication/evidence_audit.py` | 36 PASS, 0 FAIL |
| `python scripts/export_demo_data.py` | rewritten after the manuscript and claims-register edits (two input hashes and the section 7 limitation text changed); `tests/test_demo_export.py` passes |
| `.venv/bin/python -m pytest -q` | 116 passed (112 before M6, plus 4 in `tests/test_references_links.py`) |
| `npm ci --prefer-offline`, `npm test`, `npm run build`, `node tools/a11y_check.mjs dist` | added 53 packages; Tests 26 passed (26); built; A11Y-CHECK PASS |

A scan of the 277 repository paths written in code spans in tracked Markdown files found every in-repository path present; the only non-resolving ones point to the coordinator's `_shared/` folder outside the repository (decision log and progress journal), by design.

## 5. Secret, identifier and licence scan

Scope: the 276 files tracked or newly added in M6 (`git ls-files` plus new files), PDFs included through their extracted text and metadata. A final re-run before the commit covered 277 files (with `dependency_licences.md`) and gave the same counts, with 17 home-directory path lines in 6 files.

| Pattern | Hits |
|---|---|
| E-mail addresses | 0 |
| Private key headers | 0 |
| Tokens or keys (AWS, GitHub, OpenAI-style, Slack, Google, GitLab patterns) | 0 |
| Secret assignments (api key, secret, password, token with a literal value) | 0 |
| `.env` files | 0 |
| Absolute home-directory paths | 23 lines in 9 files before M6; 6 removed (README quick start, `demo/README.md`, the two builder defaults in `src/match_lab/report.py`); 17 remain in 6 files |

The remaining 17 are kept on purpose: `CLAUDE.md` (4, the session rules that name the workspace and tools), `research/feasibility.md` (5, the M0 toolchain audit record), `research/experiment_journal.jsonl` (5, append-only journal), and `results/confirmatory/logs/EXP-00N.log` (3, raw run logs of the frozen runs). Changing them would rewrite records or raw results. They are listed for the owner, who decides whether they may be public.

Dependency licences: `research/publication/dependency_licences.md`. One flag: the numpy and scipy wheels bundle the GCC runtime library (GPL-3.0-or-later WITH GCC-exception-3.1) and libquadmath (LGPL-2.1-or-later); the repository does not redistribute them.

SPDX headers: every text file added since M0 carries the header except the owner's initial-commit files (`master_prompt.md`, `NOTICE.md`, `CLA.md`, `LICENSE_HISTORY.md`, `LICENSE`, `.gitignore`), which are not edited, and `demo/.npmrc`, which received the header in M6. The 47 generated SVG figures carry no header; `NOTICE.md` covers generated figures and images.
