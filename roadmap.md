<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Roadmap

Updated 2026-11-25 (M3 session). Statuses: done, in progress, not started, blocked. Effort is a planning estimate in focused days. Section 11.6 additions are mandatory and listed per milestone.

| Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|
| M0 Bootstrap and feasibility | none | P0 | 0.5 | done (pending owner review of the gate) | none |
| M1 Research and preregistration | M0 | P0 | 0.5 | done (G-FREEZE passed: owner-approved freeze 2026-11-24) | none |
| M2 Core implementation | M1 drafts (not the freeze) | P0 | 1 | done (acceptance checks below met; exploratory pilot only) | none |
| M3 Experiments | M2; M1 freeze for confirmatory runs | P0 | 0.75 | done (EXP-001, EXP-002, EXP-003 S1/S2; S3 not run, documented failure D-019; reports written, D-020) | none |
| M4 Interpretation | M3 | P0 | 0.75 | done 2026-11-25 (gate held: evidence audit 0 FAIL, claims register C-001 to C-014 and X-001 to X-008, review pass 2, manuscript v1.0) | owner review of the proposed title |
| M5 Interactive experience | M3 results (M4 for final labels) | P1 | 1 | not started | M3 |
| M6 Release candidate | M4, M5 | P0 | 0.5 | not started | owner review; G-PUBLIC for any publication |

## M0 Bootstrap and feasibility
- Deliverables: control files (CLAUDE.md, roadmap.md, progress.md, research/*), feasibility audit, source and licence audit, budget, scope and fallback; 11.6: registry, manuscript skeleton, experiment-specific protocols, zero-cost publication toolchain confirmed.
- Acceptance: the owner can understand the question, cost (zero) and exclusions; every section 2 file exists; toolchain confirmed by an actual conversion; `uv.lock` produced; local commit.
- Status: done in this session; the gate itself is the owner's judgement.

## M1 Research and preregistration
- Deliverables: deeper literature check (full texts where accessible), formal model, baselines, final protocol and EXP-001 to EXP-003 protocols, fixture manifest; 11.6: freeze confirmatory protocols before execution.
- Acceptance: protocols complete per 11.2; owner freeze recorded with commit and SHA-256 per frozen file; exploratory results visibly separated.
- Status: done. Gate G-FREEZE passed on 2026-11-24: the owner approved amendments F1 to F6 (D-011); protocols v1.0 frozen at commit 88f3438; freeze record `research/freeze.json` (approval, C1 to C4 with the C4 disclosure, SHA-256 of the main protocol, the three EXP protocols and the three confirmatory configs, git revision). Confirmatory root seed 20261124 (D-012). Still open, not blocking: deeper reading of roth1982 and gale1962 full texts.

## M2 Core implementation
- Deliverables: market generator; RANDOM baseline first, then POPULARITY and EXPOSURE_BALANCED; DA_A, DA_B; MAXW; metrics; runner with CLI (smoke, full, report, test); 11.6: versioned JSON result schema, reproducibility manifests and report generators built alongside the algorithms.
- Acceptance: unit tests for Gale and Shapley stability on hand-computed examples, no duplicate matches, capacity one, empty pools, invalid inputs, determinism, metric bounds; property tests (DA has zero blocking pairs); differential test of MAXW against brute force on tiny markets. Correctness before any UI.
- Status: done in session M2 (2026-11-24), commits 3aeebf6, 5e8cedd, d42019e, 7e243e6 and the M2 records commit. Acceptance: hand-computed Gale and Shapley examples, no duplicate matches, capacity one, empty pools, invalid inputs, determinism, metric bounds, DA zero blocking pairs (property test against brute-force stable-matching enumeration, including proposer optimality), MAXW against brute force, a differential test across policies, the confirmatory gate; 88 tests passed, 0 failed. 11.6 M2 items: versioned schemas `match-result/1.0.0` and `match-manifest/1.0.0` validated at export and import, per-run manifest data (config hash, seed spawn key, git revision, versions, OS, CPU, runtime, sampled peak memory), report generator with PDFs (pandoc to Typst). Exploratory smoke, pilot, pilot-S and tie-key probe runs are recorded (J-0002 to J-0006). Not done: the per-experiment `reproduction.md`, `config.json` and `run_manifest.json` under `research/experiments/EXP-NNN/` (they belong to confirmatory runs, M3).

## M3 Experiments
- Deliverables: exploratory smoke run; frozen EXP-001, EXP-002, EXP-003 runs with raw machine-readable results; plots with uncertainty; 11.6: individual reports generated as each experiment finishes; all failures and deviations recorded; provenance captured at run time.
- Acceptance: complete planned matrix or documented failure; no silently dropped runs; exclusions listed.
- Freeze: done (D-011). Confirmatory runs are scheduled by the coordinator; `python -m match_lab run --config experiments/configs/EXP-00N.json` now passes the gate for the frozen configs and refuses changed ones (D-013).
- Status (2026-11-25): EXP-001 810/810 runs, EXP-002 810/810, EXP-003 1,440/1,440 (S1, S2), 0 invalid, provenance captured at run time (J-0010 to J-0012). Gate not yet met: S3 not executed (documented gap, D-018, J-0013) and the standalone 11.3 reports are not written (progress.md, M3 entry).
- Planning input from the exploratory pilot: projected run-body time EXP-001 about 71 s, EXP-002 about 12 s, EXP-003 about 155 s on one process (runner wall clock about 2.4 times that), far below the 2-hour budgets.

## M4 Interpretation
- Deliverables: confounder inspection, sensitivity (EXP-003), expected versus observed, claims register, limitations; 11.6: experiment reports finished, evidence audit, manuscript synthesis including contradictory results.
- Acceptance: every numerical claim maps to result id, config and figure; every external claim to a verified source; second review pass challenging the preferred hypothesis.
- Status (2026-11-25): done. Confounder inspection and expected versus observed in `research/paper/supplementary.md` (S2, S4.5); exploratory diagnostics J-0014, J-0015 (D-021); evidence audit `research/publication/evidence_audit.md` (J-0016); `research/publication/review_pass_2.md`; manuscript v1.0 (D-023). Open and disclosed: S3 not run; Su et al. wording to recheck in M6; no PDF built (M6).

## M5 Interactive experience
- Deliverables: static page with population and matching graph, fairness and satisfaction trade-offs, seed and scenario controls; 11.6: demo, paper, reports and articles use identical verified results, labels and scope.
- Acceptance: offline after load, responsive, keyboard usable, reduced motion, no fabricated data, no runtime service, fails closed on malformed results.

## M6 Release candidate
- Deliverables: clean-clone reproduction, locked install, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan; 11.6: compile and visually inspect manuscript and report PDFs, verify references and cross-links, complete the owner review checklist.
- Acceptance: actual command outputs recorded; only verified facts reported; no push or publication without the owner's approval.
