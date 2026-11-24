<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-003 protocol: sensitivity of the exposure-policy effect

- **Status:** FROZEN v1.0 (owner-approved 2026-11-24). Drafted as v0.1; amended before the freeze as listed in the final section. Protocol hash: recorded in `research/freeze.json` and `research/experiment_registry.csv` (a file cannot contain its own hash).
- **Role:** sensitivity analysis that can invalidate the main interpretation of EXP-001.
- **Shared definitions:** `research/protocol.md` sections 2, 4 and 7.
- **Dependency:** EXP-001 frozen and run (S3 reanalyses its raw outputs).

## 1. Precise question
Does the sign of theta_P (EXP-001) survive changes in pickiness (theta), horizon (T) and the welfare definition?

## 2. Mechanism and rationale
A policy can look better within a fixed horizon only because it produces matches faster (truncation is not a final outcome). A rank-percentile welfare with unmatched scored 0 rewards matching anyone acceptable; a different but defensible metric could reverse the ranking of policies. Pickiness changes how many likes become mutual.

## 3. Competing explanations
The policy effect in EXP-001 is (a) a speed effect, (b) a scale artefact, (c) specific to theta = 0.5.

## 4. Hypotheses
For each setting s and policy P, theta_P(s) is estimated as in EXP-001 on the 4 corner cells (r in {1.0, 1.5}, rho in {0.0, 0.9}).
- Invalidation criterion (fixed in advance): if theta_P(s) has the opposite sign of the EXP-001 estimate with a 95% CI excluding 0, for any s in S2 or S3, the EXP-001 result for P is reported as not robust and the claim is restated accordingly.
- No new confirmatory hypothesis; EXP-003 estimates are secondary.

## 5. Settings
- S1: theta in {0.3, 0.7} at the primary T = 40 (new runs).
- S2: T in {10, 20} versus the primary T = 40 (new runs).
- S3: reanalysis of EXP-001 raw outputs: (a) welfare from standardized raw utility; (b) unmatched value equal to the acceptability threshold's satisfaction instead of 0. No new runs.

## 6. Unit, sampling, seeds
Market instance; 30 instances per corner cell, using the EXP-001 instances of those cells (same seeds) so that comparisons to EXP-001 are paired. S1 and S2: 4 cells x 30 instances x 3 arms x 4 settings = 1,440 runs. S3: 0 new runs.

## 7. Uncertainty
As EXP-001 (stratified bootstrap over instances, 10,000 resamples). No multiplicity correction; results are sensitivity evidence, not tests.

## 8. Budget, exclusion, stopping
At most 30 minutes wall clock (measured need about 6 minutes at the draft horizons in the pre-freeze planning run). Exclusion and stopping as EXP-001.

## 9. Anticipated failure modes
theta = 0.7 at short horizons, or T = 10, may yield few matches, making W differences tiny and dominated by unmatched agents; this is reported as is.

## 10. Reproducibility commands
```
uv run --frozen python -m match_lab run --config experiments/configs/EXP-003.json
uv run --frozen python -m match_lab report --results results/confirmatory/EXP-003/results.json --out results/confirmatory/EXP-003/report
```
`run` refuses this config unless the freeze record and the registry match the protocol and config files on disk. S3 is a reanalysis of the EXP-001 raw results and needs no run.

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 (proposals A1 to A6, M2; see `research/protocol.md` section 10). Only approved items were applied.

- **F1:** with the primary horizon at T = 40, S1 runs at T = 40 (was 20) and S2 compares T in {10, 20} (was {10, 40}) with the primary 40: section 5. The horizons studied remain {10, 20, 40}; the run count is unchanged (1,440).
- **F4:** compute budget 30 minutes (was 2 hours): section 8.
- **F6:** implemented reproduction commands: section 10.
- Root seed 20261124, shared with EXP-001 (fixed at the freeze).
