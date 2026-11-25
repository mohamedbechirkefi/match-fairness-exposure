<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, made by, rationale, alternatives, consequences.

## D-001: Licence is the owner's custom non-commercial licence (2026-11-24)
- **Decision:** All original material is licensed under the MATCH Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-MATCH-NC-Research-1.0`), with a CLA for contributions.
- **Made by:** the owner, on 2026-11-24, before the first commit.
- **Rationale:** the owner chose a protective licence for their own protection.
- **Alternative not taken:** the master prompt (section 2) asks for an "owner-approved permissive code license". The owner decided otherwise; the owner's decision prevails.
- **Consequences:** the project is source-available, not OSI open source. README, CITATION.cff and the manuscript must not describe it as open source. Third-party data and dependencies keep their own licences (NOTICE.md). The licence files are not changed by sessions.

## D-002: Zero-cost publication toolchain without TeX (2026-11-24)
- **Decision:** PDFs are built as Markdown, then pandoc 3.6.3 to Typst, then compiled with the `typst` Python package (0.15.0). `research/paper/manuscript.tex` is generated from Markdown with pandoc and is not compiled locally.
- **Made by:** the M0 session, following the M0 brief.
- **Rationale:** no TeX distribution is installed (`which tex pdflatex xelatex` found none); installing one is unnecessary given a working free Typst path.
- **Consequences:** an exploratory smoke conversion was run in M0 (see `progress.md`); the PDF was not committed. LaTeX output is unvalidated by compilation, which is recorded as a limitation.

## D-003: Fully synthetic design; real datasets excluded (2026-11-24)
- **Decision:** no real dataset is used. Candidate datasets (Speed Dating on OpenML, libimseti) are documented in `research/literature_review.md` with unclear rights and are not downloaded.
- **Made by:** the M0 session, within the claims boundary of master prompt section 10.
- **Consequences:** results hold only within the synthetic model; no empirical calibration. Any later calibration to real data needs the owner's decision on rights.

## D-004: Protocol proposal v0.1 drafted, not frozen (2026-11-24)
- **Decision:** primary metric mean agent welfare W; baseline RANDOM exposure; nondirectional H1 for POPULARITY and EXPOSURE_BALANCED versus RANDOM, Holm-corrected; market instance as the unit; 30 instances per cell planned; sensitivity EXP-003. Registered EXP-001 to EXP-003 as "planned (protocol draft, awaiting owner freeze)".
- **Made by:** the M0 session as a proposal. Freezing is the owner's decision (G-FREEZE).
- **Alternatives considered:** unmatched fraction as primary (rejected: ignores match quality); a directional H1 (rejected: no verified source fixes the sign for this model); including centralized arms in the primary family (rejected: different information regime; they are references in EXP-002).

## D-005: Dependency lock with a two-week release cutoff (2026-11-24)
- **Decision:** `pyproject.toml` with numpy, scipy (runtime) and pytest, hypothesis (dev); `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"`; `uv.lock` produced with uv 0.9.5.
- **Rationale:** the M0 brief requires versions released at least two weeks before 2026-11-24.

## D-006: M2 architecture, schemas and the confirmatory gate (2026-11-24)
- **Decision:** separate modules for ingestion (`market.py`), simulation (`sequential.py`, `matching.py`), metrics (`metrics.py`), statistics (`stats.py`), configuration (`config.py`, schema `match-config/1.0.0`), runner and serialization (`runner.py`), schemas (`schema.py`: `match-result/1.0.0`, `match-manifest/1.0.0`, validated at export and at import), reports (`report.py`) and CLI (`cli.py`: `smoke`, `run`, `report`, `test`). Seeds: `SeedSequence(entropy=root_seed, spawn_key=(round(1000 r), round(1000 rho), instance))`, so an instance depends on its cell values and index, not on its position in a matrix, and EXP-002 and EXP-003 reuse EXP-001 instances by construction. A confirmatory config runs only if the registry holds a 64-hex `protocol_hash` equal to the SHA-256 of the protocol file; exploratory output must live under `results/exploratory/`, confirmatory output must not. Raw results are never overwritten without `--overwrite`.
- **Made by:** the M2 session, under the M2 brief.
- **Alternatives:** a JSON Schema library (rejected: a new dependency for a small schema; a hand-written validator is tested instead); matplotlib for figures (rejected: new dependency; figures are generated as SVG directly).
- **Consequences:** no new dependency; `uv.lock` unchanged (`uv lock --check` passes). The draft protocols' reproduction commands (`python -m match_lab.run --experiment ...`) differ from the implemented CLI (`python -m match_lab run --config experiments/configs/EXP-00N.json`); the protocol text is not edited (G-FREEZE), the difference is listed as an editorial amendment proposal.

## D-007: Popularity tie key is global per round by default (2026-11-24)
- **Decision:** the protocol's "seeded random key" for popularity ties is implemented as one uniform draw per candidate per round, shared by all viewers (`popularity_tie_scope = "global"`). A per-viewer variant (`"viewer"`) is implemented for comparison. Both key sets are drawn every round so the choice does not shift other streams.
- **Made by:** the M2 session as an implementation reading of an underspecified protocol item. Not a protocol change.
- **Consequences:** exploratory runs (J-0003, J-0005) show that this choice materially changes the POPULARITY arm. The owner must choose before the freeze (amendment proposal A1 in `progress.md`).

## D-008: Runtime is never measured under tracemalloc (2026-11-24)
- **Decision:** `runtime_s` is timed without tracing. Peak memory (`peak_traced_bytes`) is measured on a deterministic re-run of the first instance of each (cell, setting, arm), which also checks that the re-run reproduces the metrics (a mismatch is recorded as a run failure). Process peak RSS is recorded in the run manifest.
- **Rationale:** measured on one n_A = 200 market: sequential runs took 0.24 to 0.45 s untraced and 2.4 to 3.7 s under tracemalloc.

## D-009: Exploratory root seeds 101, 202, 303, 404 are used (2026-11-24)
- **Decision:** the exploratory smoke, pilot, pilot-S and tie-key probe use root seeds 101, 202, 303 and 404 (recorded in `data/manifest.json`). The confirmatory root seed chosen at the freeze must differ from these.

## D-010: Amendment proposals from the exploratory pilot are recorded, not adopted (2026-11-24)
- **Decision:** the pilot measurements (J-0002 to J-0006) lead to proposals A1 to A6 in `progress.md` (M2 entry). None is applied to `research/protocol.md` or the EXP protocols; the analysis plan is unchanged. Adoption is the owner's decision at the freeze (G-FREEZE).

## D-011: Protocols frozen with the owner-approved amendments F1 to F6 (2026-11-24)
- **Decision:** `research/protocol.md` and the EXP-001 to EXP-003 protocols are frozen as v1.0 with amendments F1 to F6 (from proposals A1 to A6): primary horizon T = 40 (EXP-003: S1 at T = 40, S2 at T = 10 and 20); POPULARITY ties broken by one shared random key per round (`popularity_tie_scope = "global"`, pinned in the configs); N = 30 instances per cell kept; compute budget 30 minutes per experiment; the full-size pilot (J-0003 to J-0005) recorded as the pre-freeze planning run; implemented reproduction commands. Common decisions C1 to C4 apply (synthetic data only; pandoc and Typst PDFs; sole author Mohamed Bechir Kefi, no affiliation, AI disclosed as an assistant; disclosure of exploratory primary values).
- **Made by:** the owner (G-FREEZE), approval dated 2026-11-24, quoted in `research/freeze.json`. Applied by the freeze session.
- **Rationale:** the M2 pilot showed that the tie-key granularity and the horizon materially change the POPULARITY arm (D-007, D-010); the owner settled both before any confirmatory run.
- **Consequence for EXP-003 S2:** with 40 primary, the horizons compared stay {10, 20, 40}, so S2 becomes {10, 20}; run counts are unchanged. Not applied: the remaining part of A6 (a note that blocking pairs per 100 agents is unbounded above), which is not in the approved list; it stays a reporting note.
- **C4 disclosure:** the exploratory primary-contrast values seen before the freeze (for example POPULARITY -0.2917 at T = 20 over 9 cells, +0.0178 at T = 40 on corner cells) are listed with their paths in `research/freeze.json`.
- **Consequences:** the frozen files are those of commit 88f3438; their SHA-256 are in `research/freeze.json` and the registry. Any later change is a dated deviation. Registry status: "frozen (owner-approved 2026-11-24), not yet run".

## D-012: Confirmatory root seed 20261124 (2026-11-24)
- **Decision:** the confirmatory root seed for EXP-001 to EXP-003 is 20261124, the freeze date written as an integer.
- **Made by:** the freeze session, by a rule fixed without reference to any result, because the protocol requires the seed to be fixed at the freeze and the approval did not name one.
- **Consequences:** distinct from the exploratory roots 101, 202, 303, 404 (D-009); never used for any run. The owner may replace it only before M3 starts, which would be a recorded change of a frozen config.

## D-013: The freeze guard also checks the freeze record, the main protocol and the config (2026-11-24)
- **Decision:** `check_protocol_frozen` (D-006) now also requires `research/freeze.json` (schema `match-freeze/1.0.0`) to list the experiment with the same protocol hash as the registry, the main protocol to match its frozen hash, and the config's canonical SHA-256 to equal the frozen config hash. The runner passes the config.
- **Rationale:** the brief requires `run` to accept the frozen confirmatory configs and refuse changed ones; the M2 guard checked only the per-experiment protocol.
- **Consequences:** tests cover acceptance of the three frozen configs (up to the overwrite guard, so nothing confirmatory runs), refusal of changed configs (horizon, N, seed, tie scope, grid), drift of the main or an experiment protocol, a missing, malformed or disagreeing freeze record, and the CLI paths.

## D-014: The accidental EXP-001 run is quarantined unread, not used and not deleted (2026-11-24)
- **Decision:** the unscheduled execution of the frozen EXP-001 config (J-0007) is not a confirmatory run of record. Its outputs are moved to `results/quarantine/EXP-001-unscheduled-2026-11-24/` (git-ignored, not committed), their SHA-256 recorded in J-0007, and no metric from them was read. They are not deleted: deletion is the owner's decision.
- **Made by:** the freeze session, on discovering the incident.
- **Rationale:** the run was not scheduled, ran on a busy machine from a dirty tree, and the brief forbade confirmatory runs in this session. Reading it would expose the primary contrast before the scheduled run.
- **Consequences for the owner and the coordinator:** (1) the scheduled M3 run uses the same frozen config and seed and is deterministic in its metrics, so it is expected to reproduce the quarantined metrics exactly (runtimes will differ); this can be checked by comparing hashes of the metric columns after M3, without reading the quarantined values first. (2) Options: delete the quarantine after M3, or keep it as a reproducibility cross-check. (3) Cause: an export of an older commit was tested with the repository's editable install, which imported the working-tree code; such checks must use a separate environment. Disclosed under C4 as a fact (run exists, outcome unseen).

## D-015: The owner ratifies the EXP-003 S2 horizons and the confirmatory root seed (2026-11-24)
- **Decision:** two choices the freeze session made are now owner decisions: (R1) EXP-003 S2 horizons T = 10 and 20 (the consequence of F1, primary T = 40; D-011); (R2) confirmatory root seed 20261124 (D-012).
- **Made by:** the owner, answer "Approve all" (2026-11-24) to the coordinator's list, section 3 of `labs/_shared/owner-approvals-2026-11-24b.md` (outside this repository).
- **Consequences:** both choices are already in the frozen protocols and configs, so no frozen file changes and no hash changes. Added to `research/freeze.json` under `amendments_ratified`. D-012's provision that the owner may replace the seed before M3 is now moot.

## D-016: Quarantined unscheduled EXP-001 outputs deleted unread (2026-11-24)
- **Decision:** the outputs quarantined under D-014 (`results/quarantine/EXP-001-unscheduled-2026-11-24/`, 3 files, SHA-256 in J-0007) are deleted.
- **Made by:** the owner, answer "Approve all" (2026-11-24), section 5 of `labs/_shared/owner-approvals-2026-11-24b.md`; the deletion itself was done by the coordinator, not by this session.
- **Consequences:** recorded in journal J-0008 and in `research/freeze.json` (`c4_disclosure.quarantine_deleted`). No metric from the run was ever read. The M3 reproduction cross-check offered in D-014 option (1) is no longer available. The git-ignore rule for `results/quarantine/` is kept.

## D-017: Frozen EXP-002 and EXP-003 analyses implemented before any confirmatory output (2026-11-25)
- **Decision:** `src/match_lab/analysis.py` and the CLI command `analyze` implement the frozen EXP-002 contrasts (H_a, H_b, the DA invariant, descriptive tables) and the EXP-003 S1/S2 estimates with the frozen invalidation criterion. `report.py` computes sign-flip p-values only for EXP-001 (protocol section 8). Committed as cfc90d0 with tests (103 passed) before any confirmatory run; the confirmatory runs used that revision.
- **Made by:** the M3 session under the M3 brief (analysis must be fixed before confirmatory output exists).
- **Rationale:** the M2 report generator compares arms only within one result file, so it could not pair EXP-002 arms with the EXP-001 RANDOM arm or compare EXP-003 to EXP-001.
- **Consequences:** no simulation, metric, statistics, protocol or config change; the frozen hashes still match. Disclosed in the reproduction records.

## D-018: EXP-003 S3 not executed; specification gap reported to the owner (2026-11-25)
- **Decision:** S3 (metric-definition reanalysis) is not run and no S3 code is written.
- **Made by:** the M3 session, under the brief's rule that a missing analysis may be written only if the frozen protocol fixes every parameter.
- **Rationale:** (1) S3 is specified as a reanalysis of EXP-001 raw outputs, but those store per-run metrics only, not matchings or utilities, so S3 needs a deterministic re-simulation of the EXP-001 runs; (2) the frozen text does not fix how utility is standardized under (a), the unmatched value under (a), or how "the acceptability threshold's satisfaction" is computed under (b) given the interpolated quantile.
- **Consequences:** EXP-003 is partial (S1 and S2 complete). The POPULARITY verdict is already "not robust" from S2; the EXPOSURE_BALANCED verdict lacks S3. The owner decides whether to specify S3 (a dated post-freeze amendment, reported separately from the frozen analysis) or to record it as not done. Journal J-0013.

## D-019: EXP-003 S3 recorded as not run, a documented failure under the M3 gate (2026-11-25)
- **Decision:** EXP-003 S3 is recorded as not run, a documented failure under the M3 gate. Its parameters are not chosen after the data.
- **Made by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (section 9, MATCH, of `labs/_shared/owner-approvals-2026-11-25.md`, outside this repository).
- **Consequences:** EXP-003 stays partial (S1 and S2 complete, S3 not run); no S3 code is written and no S3 amendment follows. The metric-definition threat (limitation 4) stays open in every report and in the manuscript. Recorded in `research/freeze.json` (`post_freeze_deviations`).

## D-020: Missing experiment reports approved; shell-written reproduction records kept (2026-11-25)
- **Decision:** the owner approves writing the missing 11.3/11.6 experiment reports from committed results, tables and figures only, with no recomputation; the `reproduction.md` files written through the shell in M3 are kept.
- **Made by:** the owner, 2026-11-25, "approve all recommendations, RIGGED A" (section 4 of `labs/_shared/owner-approvals-2026-11-25.md`).
- **Consequences:** in the M3-close session the file tool still refused to write `research/experiments/EXP-001/report.md` ("subagents should return findings as text"). No shell or other workaround was used. On the coordinator's instruction (report-return note), the session composed the EXP-001, EXP-002 and EXP-003 reports from committed results only and handed their text to the coordinator, who writes and commits the files.

## D-021: M4 exploratory diagnostics are allowed only on committed outputs plus one cheap probe, and change no verdict (2026-11-25)
- **Decision:** M4 runs four exploratory diagnostics:
  - E1 horizon saturation, E2 the unmatched-value sweep and E3 the decomposition W = (1 - U) Q, all reanalyses of committed outputs (J-0014);
  - E4, one horizon-extension probe: a new exploratory seed 505, 810 runs, T in {40, 80, 160}, about 2.5 minutes on one process (J-0015).

  All are labelled exploratory, are kept in `results/exploratory/m4_*` and never change or replace a frozen verdict.
- **Made by:** the M4 session, under the M4 brief (owner, 2026-11-25, "Approve all recommendations, push then next": new computation only when cheap and clearly exploratory, at most 2 workers; one worker was used).
- **Rationale:** the frozen protocols name the horizon and the treatment of unmatched agents as the main competing explanations. The committed outputs already hold per-round match counts and U, so E1 to E3 cost nothing. E4 is the only direct check of whether T = 40 is final for every arm.
- **Not done:** E2 is not EXP-003 S3. It sweeps a constant unmatched value over the whole range [0, 1] instead of choosing parameters, and it leaves the satisfaction scale unchanged. S3 stays not run, and no S3 parameter is chosen after the data (D-019). E4 does not reuse the confirmatory seed, so that no exploratory output shares instances with a confirmatory table.
- **Consequences:** the manuscript, the supplementary file and the reports of EXP-001 to EXP-003 report these diagnostics beside the frozen verdicts, each with its label (claims C-010 to C-013).

## D-022: Claims register restructured; external claims registered (2026-11-25)
- **Decision:** `research/claims_register.csv` now has the columns claim_id, text, type, result_id, evidence_path, config_sha256, figure_or_table, manuscript_section, scope, status and limitations. The rows are 14 result claims (C-001 to C-014) and 8 external claims (X-001 to X-008, each with its verification level). The artifact manifest is extended to 29 entries.
- **Made by:** the M4 session (M4 brief, task 3; master prompt 11.5).
- **Consequences:** a claim without a row is not made. The old columns are kept in substance; the old evidence_path_or_source column is split into result_id and evidence_path.

## D-023: Manuscript v1.0 after the second review pass; proposed title (2026-11-25)
- **Decision:** the manuscript is synthesised as v0.9, challenged in `research/publication/review_pass_2.md` (R1 to R11) and revised to v1.0. The changes:
  - removed: a conclusion contradicted by the project's own probe (R1);
  - qualified: the sweep mechanism (R2), the composition of the matched set (R3), the horizon choice and the scope of the p-value (R4), horizons relative to n_B / k (R6) and the EXPOSURE_BALANCED construct (R7).

  The descriptive title "Popularity ranking, exposure balancing and the length of search: a pre-registered simulation of sequential discovery in synthetic two-sided matching markets" is proposed in place of the working title.
- **Made by:** the M4 session. The title and the author metadata remain the owner's to approve.
- **Consequences:** no frozen verdict changed. C-001 stays "supported, not robust", C-002 "equivalent at margin 0.01", C-003 and C-004 "supported (secondary)", and S3 "not run".
