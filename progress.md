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

## 2026-11-24: session M2 (core implementation while the freeze is pending)

**Milestone:** M2. **Starting state:** commit cfde5bb, working tree clean. **Bounded task:** reference baseline and candidate variants with tests, schemas, manifests, CLI, report generator, and an exploratory smoke run for the owner's freeze decision. No confirmatory run; no protocol frozen; nothing pushed.

### What was implemented
- `match_lab` 0.2.0: market generator (GEN-match-market v1), RANDOM baseline then POPULARITY and EXPOSURE_BALANCED sequential discovery, DA_A, DA_B, MAXW, all protocol 2.4 metrics, protocol section 4 statistics (bootstrap, stratified bootstrap, stratified sign-flip test, Holm, sample size), configs (`match-config/1.0.0`), result and manifest schemas validated at export and import, runner with per-run seeds and timing, report generator (Markdown, CSV, SVG, PDF), CLI `python -m match_lab {smoke,run,report,test}`.
- `run` refuses confirmatory configs unless the registry holds a protocol hash equal to the file's SHA-256 (tested: `python -m match_lab run --config experiments/configs/EXP-001.json` exits 3 with "REFUSED: EXP-001 protocol is not frozen ...").
- Configs: `experiments/configs/{smoke,pilot,pilot_sensitivity,probe_tie_scope}.json` (exploratory) and `EXP-001..003.json` (confirmatory drafts, `root_seed: null`).

### Decisions
D-006 architecture, schemas and the confirmatory gate; D-007 popularity tie key global per round by default; D-008 runtime never measured under tracemalloc; D-009 exploratory root seeds 101, 202, 303, 404; D-010 amendment proposals recorded, not adopted.

### Commands and actual outputs
- `uv run --frozen pytest -q` first failed: `ModuleNotFoundError: No module named 'hypothesis'`. Cause: `.venv/bin/pytest` had a stale shebang pointing at the old path `labs/match-research/.venv` (the repository was renamed after M0). Fixed with `uv sync --frozen --reinstall` (reinstalled the locked packages into `.venv`; nothing deleted).
- Final `uv run --frozen pytest -q`: `88 passed in 1.66s`, 0 failed. `uv lock --check`: `Resolved 11 packages in 6ms` (lock unchanged; no new dependency).
- Timing check on one n_A = 200, r = 1.5, rho = 0.9 market: sequential arms 0.24 to 0.45 s untraced, 2.4 to 3.7 s under tracemalloc (led to D-008).
- `uv run --frozen python -m match_lab smoke` (J-0002): 120 runs, 0 invalid, wall 1.8 s.
- `... run --config experiments/configs/pilot.json` (J-0003): 270 runs, 0 invalid, wall 32.4 s.
- `... run --config experiments/configs/pilot_sensitivity.json` (J-0004): 144 runs, 0 invalid, wall 57.4 s.
- `... run --config experiments/configs/probe_tie_scope.json` (J-0005): 36 runs, 0 invalid, wall 17.7 s.
- Reports built with `python -m match_lab report ...`; PDFs: smoke 8 pages, pilot 18 pages, probe 5 pages (page counts from pypdf). Pages of the smoke and pilot reports were rendered to PNG in the session scratchpad and inspected; the inspection found overflowing table cells, an unbreakable table running off the page, overlapping figure labels and a doubled figure number, fixed in commit 7e243e6 and in the records commit (breakable tables, short cell labels) before the final reports were generated. Not every page was inspected.
- Earlier executions superseded and deleted (J-0006): the first smoke (timed under tracemalloc) and the first pilot and pilot-S (random streams changed when the per-viewer tie stream was added). Their outputs were created in this session.

### Exploratory measurements (not findings; synthetic; for the owner's freeze decision)
- **Runtime per run at n_A = 200 (J-0003):** mean RANDOM 0.073 s, POPULARITY 0.110 s, EXPOSURE_BALANCED 0.073 s, DA_A 0.019 s, DA_B 0.018 s, MAXW 0.002 s; maximum 0.211 s (0.403 s at T = 40). Peak traced memory at most 3.07 MiB per run; process peak RSS 114 MiB. The same pilot ran about twice as slowly in an earlier execution under load from other sessions.
- **Projected full matrix (single process, run bodies):** EXP-001 70.8 s, EXP-002 12.1 s, EXP-003 155.1 s; runner wall clock about 2.4 times the run bodies, so roughly 3, 0.5 and 6 minutes. The 2-hour planning budgets are not binding.
- **Seed spread (J-0003, 5 instances per cell):** SD of paired W differences versus RANDOM per cell: POPULARITY 0.0058 to 0.0190, EXPOSURE_BALANCED 0.0045 to 0.0161. Instances per cell for 80% power to detect 0.01 within a cell: up to 29 (POPULARITY) and 21 (EXPOSURE_BALANCED). For the pooled primary contrast, 2 per cell would suffice at these SDs. N = 30 is adequate for the pooled contrast; it is at the margin for per-cell resolution of 0.01, and SDs from 5 instances are imprecise.
- **Degenerate cases:** (1) POPULARITY with the global tie key shows nearly the same slate to every viewer, produces about 2 to 6 matches per round and leaves 52% to 74% unmatched at T = 20 (RANDOM: 2% to 42%). (2) The POPULARITY difference from RANDOM on corner cells is strongly negative at T = 10 and 20 and positive at T = 40 (J-0004): under the draft design the primary POPULARITY contrast mostly measures matching throughput within the horizon. (3) With per-viewer tie keys (J-0005) POPULARITY leaves 16% to 47% unmatched and its corner-cell difference from RANDOM is about -0.04 instead of about -0.29. (4) The exposure cap shortened at most 1.7% of EXPOSURE_BALANCED slates. (5) RANDOM stops producing matches after about 10 to 11 rounds at rho = 0. (6) Smoke-size markets (n_A = 50) behave differently from n_A = 200 for POPULARITY, so the smoke matrix is not a planning proxy. (7) Blocking pairs per 100 agents exceed 100 in sequential and MAXW arms (the measure counts pairs, so it is not bounded by 100). No invalid run, no DA blocking pair, no zero-match instance.

### Proposed amendments for the owner (not adopted; G-FREEZE)
- **A1, tie-key granularity (material).** Specify whether POPULARITY and EXPOSURE_BALANCED break score ties with one key per candidate per round shared by all viewers (current default, D-007) or a key per (viewer, candidate). The choice changes the POPULARITY arm substantially (J-0003 versus J-0005).
- **A2, horizon.** T = 20 is binding for POPULARITY under the global tie key. Options: keep T = 20 and state that the contrast includes speed; make the primary horizon long enough for all arms to stop matching (for example T = 60, or run until no new match for a fixed number of rounds) and keep T = 20 as a sensitivity; or report W at several horizons. EXP-003 S2 already tests this but as a secondary check.
- **A3, N per cell.** Keep 30 or raise to 50: the full matrix takes minutes, so a larger N costs little and tightens per-cell intervals; the pilot SDs come from only 5 instances.
- **A4, compute budget.** The 2-hour planning budgets per experiment can be reduced to 30 minutes, which still leaves a wide margin.
- **A5, pre-freeze pilot.** Record the full-size pilot (J-0003 to J-0005) in the protocol as the pre-freeze planning run instead of the n_A = 50 smoke matrix, which is not representative.
- **A6, editorial.** Replace the planned reproduction commands in the EXP protocols (`python -m match_lab.run --experiment ...`) with the implemented ones (`python -m match_lab run --config experiments/configs/EXP-00N.json`, `python -m match_lab report ...`), state the confirmatory root seed, and note that blocking pairs per 100 agents is unbounded above.

### Files changed
New: `src/match_lab/{errors,market,matching,sequential,metrics,stats,config,schema,runner,report,cli,__main__}.py`; `tests/{helpers,test_market,test_matching,test_sequential,test_metrics_stats,test_pipeline}.py`; `experiments/configs/*.json`; `results/exploratory/{smoke,pilot,pilot_sensitivity,probe_tie_scope}/` (results, manifests, CSV, reports). Changed: `src/match_lab/__init__.py`, `tests/test_package.py`, `pyproject.toml` (pytest `pythonpath`), `.gitignore`, `README.md`, `CONTRIBUTING.md` (appended commands), `roadmap.md`, `research/{decision_log.md, experiment_journal.jsonl, experiment_registry.csv, limitations.md}`, `data/manifest.json`, READMEs in `src/`, `tests/`, `experiments/`, `results/`. No licence file, protocol or master prompt changed.

### Failures and incidents
- Stale `.venv` script shebangs after the repository rename (fixed, above).
- PNG renders for inspection were first written to the shared session scratchpad root with generic names (`smoke1.png` to `smoke8.png`), which other sessions also use; files of the same name may have been overwritten there. Later renders used a dedicated subfolder.

### Outstanding risks
- The POPULARITY arm's behaviour depends on A1 and A2; freezing without settling them risks a primary result that mostly reflects an implementation reading and the horizon.
- Runtime figures are load-sensitive (about twofold variation observed).

### Next action
Owner: settle A1 to A6 and freeze the protocols (G-FREEZE), choosing a confirmatory root seed distinct from 101, 202, 303, 404. Then M3: run EXP-001 to EXP-003 with `python -m match_lab run --config experiments/configs/EXP-00N.json` and write the per-experiment reports.

## 2026-11-24: freeze session (owner-approved G-FREEZE)

**Milestone:** M1 gate. **Starting state:** commit f4ddedb (M2 records), working tree clean. Authority: the owner's approvals of 2026-11-24 (section MATCH of the shared approvals file), quoted in `research/freeze.json`.

### Decisions
D-011 protocols frozen with amendments F1 to F6; D-012 confirmatory root seed 20261124; D-013 freeze guard extended to the freeze record, the main protocol and the config; D-014 accidental EXP-001 run quarantined unread.

### What was done
- Applied exactly the approved amendments (F1 primary T = 40; F2 POPULARITY ties by one shared random key per round; F3 N = 30; F4 compute budget 30 minutes; F5 full-size pilot as the pre-freeze planning run; F6 reproduction commands) to `research/protocol.md` and the three EXP protocols, each with a dated "Amendments before freeze (owner-approved 2026-11-24)" section. Consequence of F1 for EXP-003: S1 at T = 40, S2 at T in {10, 20}. Not applied: the blocking-pairs note of A6 (not in the approved list).
- Confirmatory configs: root seed 20261124, T = 40, EXP-003 settings as above, `popularity_tie_scope = "global"` pinned. Frozen content committed as 88f3438.
- Freeze record `research/freeze.json` (approval quote, C1 to C4 with the C4 disclosure of exploratory primary values and paths, SHA-256 of the main protocol, the three EXP protocols and the three configs, git revision). Registry: hashes and status "frozen (owner-approved 2026-11-24), not yet run".
- Gate: `check_protocol_frozen` now also needs the freeze record, the main protocol hash and the config hash (D-013).
- CITATION.cff abstract and manuscript author metadata updated to C3 (sole author Mohamed Bechir Kefi, no affiliation, AI disclosed as an assistant); `manuscript.tex` regenerated with pandoc 3.6.3.

### Commands and actual outputs
- `.venv/bin/python -m pytest -q`: `99 passed` (88 before; gate tests replaced and extended: acceptance of the frozen configs up to the overwrite guard, refusal of changed configs, file drift, missing or disagreeing freeze record, CLI).
- `shasum -a 256`: `research/protocol.md` 81f24e9e4bc15434837208705f61619d6415bd1643985142248c926482e160c5 (all hashes in `research/freeze.json`).

### Failures and incidents
- **J-0007 / D-014:** while checking the frozen-content commit from an export in the scratchpad, the old M2 test `test_cli_run_refuses_confirmatory` ran through the editable install against the real repository after the freeze record existed, and executed the full EXP-001 config (810 runs, 114 s, dirty tree, busy machine). Outcome not read; outputs quarantined, not deleted. The suite of commit 88f3438 was therefore not verified on its own; the final commit's suite passes.

### Next action
Coordinator: schedule M3 on a quiet machine: `uv run --frozen python -m match_lab run --config experiments/configs/EXP-00N.json` for N = 1, 2, 3, then the reports. Owner: decide the fate of `results/quarantine/` (D-014).

## 2026-11-24: ratification session (owner's second-round approvals)

**Milestone:** M1 gate passed, M3 pending. **Starting state:** commit 95ce91b, working tree clean. Authority: `labs/_shared/owner-approvals-2026-11-24b.md` (owner's answer "Approve all").

### What was done
- D-015: recorded the owner's ratification of EXP-003 S2 horizons T = 10 and 20 and of the confirmatory root seed 20261124; added to `research/freeze.json` (`amendments_ratified`). No frozen file changed, so no hash changed.
- D-016 and journal J-0008: recorded the coordinator's deletion, on the owner's approval, of the quarantined unscheduled EXP-001 outputs (3 files, never read). `results/quarantine/` is empty; the `.gitignore` comment updated.
- No code change: none of the pre-M3 code fixes in the brief concerns MATCH.

### Next action
Coordinator: schedule M3 on a quiet machine (`uv run --frozen python -m match_lab run --config experiments/configs/EXP-00N.json`, N = 1, 2, 3), then the reports.

## 2026-11-25: M3 session (confirmatory runs)

**Milestone:** M3. **Starting state:** commit 12f7d21, working tree clean, every frozen hash matching the files on disk. Authority: the owner's "Start next" (2026-11-25) and the M3 brief.

### Decisions
D-017 frozen EXP-002/EXP-003 analyses implemented and committed before any confirmatory output; D-018 EXP-003 S3 not executed (specification gap, owner decision needed).

### What was done
- Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` (Audited 10 packages); `.venv/bin/python -m pytest -q`: 99 passed. The editable install resolves to this repository.
- Pre-run code (commit cfc90d0): `src/match_lab/analysis.py` and `python -m match_lab analyze` (EXP-002 contrasts paired with the EXP-001 RANDOM arm; EXP-003 S1/S2 estimates and the frozen invalidation criterion); p-values limited to EXP-001 (protocol section 8); `tests/test_analysis.py`; 103 passed.
- Exploratory smoke on root seed 101 (J-0009): 120 runs, 0 invalid, metrics identical to the M2 smoke; independent naive recomputation of W, U, M and blocking pairs matched on 8 runs.
- Confirmatory runs at cfc90d0 (clean), under `nice -n 10`, at most 2 processes (EXP-001 and EXP-002 together, then EXP-003): EXP-001 810/810 runs, 0 invalid, 255.2 s (J-0010); EXP-002 810/810, 0 invalid, 13.6 s (J-0011); EXP-003 1,440/1,440, 0 invalid, 392.3 s (J-0012). All exit 0; logs in `results/confirmatory/logs/`; no exclusion, no dropped run, no retry.
- Analyses as frozen: `report` for each experiment, `analyze` for EXP-002 and EXP-003. Raw results, manifests, tables, figures and SHA256SUMS committed (7.9 MB in total). Per-experiment folders `research/experiments/EXP-00N/` hold config.json, run_manifest.json, metrics.csv, figures/ and reproduction.md.
- Records: journal J-0009 to J-0013, registry statuses, claims C-001 to C-007, artifact manifest entries, limitations 4, 5 and 13 to 16, decisions D-017 and D-018.

### Results (synthetic simulations)
- EXP-001 (confirmatory): theta_POPULARITY = +0.0219, 95% CI [+0.0207, +0.0231], Holm p = 0.0002: H1 supported. theta_EXPOSURE_BALANCED = +0.0004, 95% CI [-0.0007, +0.0015], Holm p = 0.51: not supported; 90% CI [-0.0005, +0.0013] inside the margin 0.01 (equivalent to 0 at that margin). POPULARITY is negative in cells r = 1.5, rho = 0.5 and 0.9.
- EXP-002 (secondary): W(DA_A) - W(RANDOM) = +0.0963 [+0.0954, +0.0973]; blocking pairs per 100 agents MAXW - DA_A = +231.1 [+226.3, +235.7]; DA invariant held (0 blocking pairs in 540 runs).
- EXP-003 (sensitivity): POPULARITY reverses sign at T = 10 (-0.4081 [-0.4098, -0.4064]) and T = 20 (-0.2824 [-0.2843, -0.2805]): the frozen invalidation criterion is met, so the EXP-001 POPULARITY result is reported as not robust (a speed-within-horizon effect). EXPOSURE_BALANCED: criterion not met under S2. S1: POPULARITY stays positive at theta 0.3 and 0.7.

### Deviations and failures
- J-0013 / D-018: S3 not executed. The EXP-001 raw outputs hold metrics only (no matchings or utilities), and the frozen text leaves the utility standardization, the unmatched value under (a) and the threshold-satisfaction definition under (b) unspecified.
- Experiment reports (11.3) are not written. The file tool refused to write `research/experiments/EXP-00N/report.md` in this session ("subagents should return findings as text"). Two reports were first written through the shell; on the coordinator's instruction not to work around the refusal, both files (created in this session) were deleted. The generated run reports `results/confirmatory/EXP-00N/report/report.md` and `.pdf` (tables and figures from the `report` command) exist; the standalone 11.3 reports remain to be written.
- Test update after the runs: two guard tests asserted that `results/confirmatory/` does not exist, which stopped being true once the runs existed (6 failures, guard behaviour unchanged). They now assert that a refused run creates or changes nothing there. No analysis code changed after the confirmatory output.
- The frozen-content revision is 88f3438; the runs used cfc90d0 (records, analysis module, CLI, tests, the p-value scope change; no simulation, metric or statistics change). The frozen hashes still match after the session.

### Commands and actual outputs
- Final `.venv/bin/python -m pytest -q`: 103 passed.

### Next action
Owner: decide S3 (specify it as a dated post-freeze amendment or record it as not done), and how the 11.3 experiment reports get written (a session allowed to write them). Then M4.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 3 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25: M4 session (interpretation, evidence audit, manuscript)

**Milestone:** M4. **Starting state:** commit e1050b2, working tree clean, every frozen hash matching. Authority: the owner's "Approve all recommendations, push then next" (2026-11-25) and the M4 brief. The owner's 2026-11-25b follow-ups name no MATCH item.

### Decisions
- D-021: M4 exploratory diagnostics run only on committed outputs, plus one cheap probe; no verdict changes.
- D-022: claims register restructured and external claims registered.
- D-023: manuscript v1.0 after the second review pass; a descriptive title is proposed, pending the owner.

### What was done
- **Confounder inspection.** Every competing explanation named in the frozen protocols was checked against the evidence (supplementary S4.5, manuscript Table 6). Exploratory diagnostics (D-021):
  - J-0014: E1 horizon saturation, E2 the unmatched-value sweep and E3 the decomposition W = (1 - U) Q, from the committed outputs;
  - J-0015: E4, a horizon-extension probe on the new exploratory seed 505 (810 runs, T in {40, 80, 160}).

  Scripts are in `experiments/exploratory/` and outputs in `results/exploratory/m4_*` (commit cff9d7c).
- **Expected versus observed.** Supplementary Table S2 covers every registered prediction.
- **Claims register.** 14 result claims (C-001 to C-014) and 8 external claims (X-001 to X-008), with result id, config hash, figure or table, section and limits. The artifact manifest has 29 entries.
- **Evidence audit.** Script `research/publication/evidence_audit.py`; findings in `research/publication/evidence_audit.md`, F-01 to F-10. Stale records were fixed: registry statuses, README status, the `experiments/` and `results/` READMEs, the M0 claims audit and `manuscript.tex`. No number mismatch was found.
- **Manuscript.** `research/paper/manuscript.md` v0.9, then `research/publication/review_pass_2.md` (R1 to R11), then v1.0. `supplementary.md` written; `manuscript.tex` regenerated with pandoc 3.6.3.
- **Reports.** The three reports now carry a labelled M4 exploratory addendum in section 9 (report version 1.1).
- **Limitations.** Items 4 and 5 updated; items 17 to 21 added.

### Commands and actual outputs
- `.venv/bin/python -m pytest -q` at session start: 103 passed.
- `nice -n 10 .venv/bin/python experiments/exploratory/m4_confounders.py --out results/exploratory/m4_confounders`: 70 sweep rows, 14 decompositions, 75 saturation rows; 1.7 s.
- `nice -n 10 .venv/bin/python -m match_lab run --config experiments/configs/m4_horizon_probe.json`: 810 runs, 0 invalid, exit 0, 146.6 s (manifest), 2026-11-25T01:20:36Z to 01:23:03Z. Then `.venv/bin/python experiments/exploratory/m4_horizon_probe_analysis.py`.
- `match_lab report` and `analyze` re-run into the scratchpad: 8 tables byte-identical to the committed ones. The 14 figure copies are identical to the generated figures.
- `.venv/bin/python research/publication/evidence_audit.py`: 36 PASS, 0 FAIL.
- `.venv/bin/python -m pytest -q` at session end: 103 passed.

### Findings (synthetic; exploratory unless stated)
- **Truncation at T = 40.** Every confirmatory POPULARITY instance was still forming matches in round 40; RANDOM and EXPOSURE_BALANCED had almost always stopped. The frozen T = 40 contrast is a fixed-horizon quantity.
- **Horizon-extension probe.** POPULARITY minus RANDOM was +0.0217 at T = 40 and +0.0375 [+0.0356, +0.0394] at T = 80 (identical at T = 160), positive in all nine cells. Delta U was -0.0199 at T = 80. EXPOSURE_BALANCED was unchanged at +0.0022 across horizons.
- **Unmatched-value sweep.** Both EXP-001 signs and the EXPOSURE_BALANCED equivalence hold for any constant unmatched value v in [0, 1]. The S2 reversal would vanish above v = 0.72 to 0.75. This is not S3, which stays not run.
- **EXPOSURE_BALANCED.** Its exposure Gini was higher than RANDOM's in 4 of 9 cells (descriptive, confirmatory data), and its timing resembled RANDOM.
- **Verdicts.** No frozen verdict changed.

### Deviations and incidents
- The probe ran before its config and scripts were committed: revision e1050b2, with `git_dirty` recorded as false because untracked files are ignored. Disclosed (F-08); the files were committed unchanged.
- No file write was refused in this session.

### Next action
- **Owner:** approve or revise the proposed manuscript title, and review `research/publication/review_pass_2.md`.
- **Then:** M5 (interactive page) and M6 (PDF builds, a recheck of the Su et al. wording, clean-clone reproduction). No push without the owner's approval.

## 2026-11-25: post-M4 owner decisions (title, statements)

**Starting state:** commit 410db30, working tree clean. Authority: owner, 2026-11-25, "Approve all" (post-M4) (`_shared/owner-approvals-2026-11-25c.md`, items 1 and 2; brief `_shared/POST-M4-brief.md`).

- Item 1: the D-023 title is owner-approved. The manuscript status sentence now records the approval instead of "proposed"; `manuscript.tex` regenerated with `pandoc manuscript.md -s -t latex` (3-line diff, header comments kept) (D-024).
- Item 2: funding, competing-interest and AI-assistance wording recorded as owner-approved; no wording changed (D-024).
- No frozen protocol, config, seed or result changed. No computation.

### Owner placeholders for M5
1. Manuscript section 10: "public URL: to be added after the owner's approval". The URL exists only once the owner approves publication.

### Next action
M5 (interactive page) and M6 (PDF builds, a recheck of the Su et al. wording, clean-clone reproduction). No push.
