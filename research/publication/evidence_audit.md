<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), session M4, 2026-11-25

**Scope.** The audit covered:
- the manuscript (`research/paper/manuscript.md` v1.0) and its supplementary file;
- the three experiment reports (`research/experiments/EXP-00N/report.md`);
- the claims register (`research/claims_register.csv`) and the artifact manifest (`research/publication/artifact_manifest.json`);
- the raw outputs in `results/confirmatory/` and the M4 exploratory outputs in `results/exploratory/m4_*`.

**Method.**
- **Script.** `.venv/bin/python research/publication/evidence_audit.py`. Its final run printed 36 PASS lines and `0 FAIL`.
- **Regeneration.** `report` and `analyze` were re-run into the session scratchpad and their tables compared byte by byte.
- **Manual checks.** The qualitative statements and the external claims were checked by hand.

This is internal quality control by the AI assistant, not external review.

## 1. Results of the automated checks

| Check | What was compared | Outcome |
|---|---|---|
| A. Frozen hashes | SHA-256 of `research/protocol.md`, the three EXP protocols and the three confirmatory configs against `research/freeze.json` | all 7 match |
| B. Checksums | `results/confirmatory/EXP-00N/SHA256SUMS` against the files | all match |
| C. Counts | runs, invalid runs and exclusions per experiment; canonical config hash stored in each `results.json` | EXP-001 810, EXP-002 810, EXP-003 1,440 runs; 0 invalid; 0 exclusions; hashes match the freeze record |
| D. Independent recomputation | point estimates recomputed with plain numpy from `results.json`, without `match_lab` code (see list below) | all equal at the printed precision |
| E. Number trace | every decimal number in the 3 reports, the manuscript, the supplementary file and the claims register, matched against the values in the committed tables, analysis JSON, freeze record and run manifests at the printed precision | 0 untraced numbers |
| Regeneration | `match_lab report` (EXP-001, EXP-003) and `match_lab analyze` (EXP-002, EXP-003) re-run into the scratchpad from the committed raw results | all 8 regenerated tables byte-identical to the committed ones |
| Figures | the 14 figure copies in `research/experiments/EXP-00N/figures/` against the generated figures in `results/confirmatory/` | all byte-identical; no stale figure |

The point estimates recomputed in check D are:
- theta_P for EXP-001 (both policies, 9 cells by 30 pairs);
- H_a and H_b for EXP-002 (270 pairs);
- the EXP-003 S1 and S2 estimates (120 pairs each);
- the corner-cell reference;
- the DA invariant (0 of 540 DA runs);
- U(DA_A) = U(DA_B) on every instance;
- the exposure-cap short-slate share per cell.

**Limits of the automated trace.**
- Check E covers decimal numbers only. Integers (run counts, instance counts) are covered by check C and by the manual checks.
- A short decimal such as 0.5 always finds a match and is therefore traced only trivially. Design values were checked by reading them against `research/protocol.md`.

## 2. Denominators, units, precision, uncertainty and sample counts

| Item | Finding |
|---|---|
| Denominators | theta_P: 9 cells by 30 paired instances (270) for EXP-001 and EXP-002; 4 corner cells by 30 (120) for EXP-003 rows. U is the unmatched share of all n_A + n_B agents (checked on a run: 6 unmatched of 400 gives U = 0.015). The DA invariant covers 540 runs (270 DA_A plus 270 DA_B). |
| Units | W, U, M and Q are unitless fractions in [0, 1]. Blocking pairs are a pair count per 100 agents and can exceed 100; this is stated wherever the metric appears. Runtimes are in seconds and are diagnostics only. |
| Precision | Four decimals for welfare quantities and two for blocking pairs per 100 agents. The claims register rounds H_b to one decimal (+231.1), consistent with +231.06. One CI bound, +14.08, is the half-up rounding of the exact value 14.075 (per-cell H_b, r = 1.0, rho = 0). |
| Uncertainty | 95% percentile or stratified bootstrap CIs with 10,000 resamples throughout. 90% CIs are reported only where the frozen equivalence rule needs them (EXP-001). The EXP-001 sign-flip p-value is at its floor of 1/10,001; this is stated. |
| Streams | The generic `report` command and the `analyze` command use different fixed bootstrap streams, so the EXP-003 generic pooled table and the frozen analysis table can differ in the last digit. The reports use the analysis tables, and the EXP-003 report discloses this. The M4 exploratory sweep reproduces the frozen point estimates exactly; three of its CI bounds differ in the last digit, as disclosed in supplementary S4.2. |
| Sample counts | No run was dropped, failed or retried in any experiment. The superseded M2 outputs and the accidental freeze-session run are listed with their journal entries (supplementary S1). None enters any table. |

## 3. External claims

Every external claim has a row in the claims register (X-001 to X-008) that names its source and verification level. The sources were opened on 2026-11-24 (`research/literature_review.md`):
- Gale and Shapley 1962 and Roth 1982: metadata only;
- the other six sources: abstract only.

No claim attributes more to a source than its verification level supports. The manuscript and the EXP-002 report say explicitly that the deferred-acceptance facts rest on standard definitions and the project's tests.

One wording difference is flagged and not changed:
- **Su et al. (2021) wording.** The EXP-001 report and the frozen EXP-001 protocol paraphrase Su et al. (2021) as concerning "one-sided" (or "one-sided or reciprocal") relevance. The literature review records the abstract as concerning "local relevance scores". The manuscript uses the literature-review wording.
- **Why not changed.** The abstract was not reopened in this session.
- **Follow-up.** The wording should be rechecked against the abstract in M6.

## 4. Findings and fixes

| Id | Finding | Fix |
|---|---|---|
| F-01 | `research/experiment_registry.csv` still said "standalone report not written in M3" for all three experiments | statuses updated to the M3 and M4 state |
| F-02 | `README.md` status line still described M2 ("only exploratory pilot runs exist") | status paragraph updated to M4; the full README is an M6 deliverable |
| F-03 | `experiments/README.md` and `results/README.md` said the confirmatory configs had `root_seed: null` and that `results/confirmatory/` did not exist | both updated, with the M4 exploratory folders listed |
| F-04 | `research/publication/claims_audit.md` was the M0 checklist ("register empty") | rewritten as the M4 claims audit |
| F-05 | The claims register had no result-id, config-hash, figure-or-table or manuscript-section column, and external claims had no rows | register restructured (11 columns); 14 result claims (C-001 to C-014) and 8 external claims (X-001 to X-008) |
| F-06 | The artifact manifest covered only C-001 to C-007 and no figure or table | extended to 29 entries: claims, the manuscript figures and tables, and the exploratory diagnostics (labelled, no protocol hash) |
| F-07 | `research/paper/manuscript.tex` was generated from the M0 skeleton | regenerated with pandoc 3.6.3 from manuscript v1.0 |
| F-08 | The M4 horizon probe ran with its config file not yet committed (revision e1050b2). The runner recorded `git_dirty: false` because it does not count untracked files. | disclosed in supplementary S3, the manifest (C-011) and journal J-0015. The config and scripts were committed unchanged in cff9d7c, and the config hash is recorded. |
| F-09 | The EXP-001 report states the cap shortened "between 0.0% and 1.0%" of slates. The values are 0.01% to 1.05%. | rounding only, not changed. The manuscript gives "at most 1.05%". |
| F-10 | Draft manuscript v0.9 contained conclusions contradicted by the project's own exploratory data (review pass 2, R1) and a mechanism presented as fitted by a mechanical bound (R2) | revised in v1.0; see `review_pass_2.md` |

No mismatch between a reported number and the raw outputs was found.

## 5. Gate assessment (M4 acceptance)

- **Numerical claims.** Every numerical claim in the manuscript, the supplementary file and the reports maps to:
  - a claim row with a result id, a config hash and a figure or table;
  - a manifest entry with a result path, a generator and a code revision.

  Exploratory numbers are labelled and map to the M4 entries.
- **External claims.** Every external claim maps to a source actually opened, with its verification level. Two sources were read at metadata level and six at abstract level only. No full text was read.
- **Second review pass.** `research/publication/review_pass_2.md` challenges the preferred reading. Its accepted challenges are applied in manuscript v1.0.

Open items do not block the M4 gate but stay disclosed:
- S3 was not run;
- the Su et al. wording is to be rechecked in M6;
- no PDF of the manuscript was built in M4. PDF builds and visual inspection belong to M6.
