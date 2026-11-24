<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-003 protocol: sensitivity of the exposure-policy effect

- **Status:** DRAFT v0.1, 2026-11-24. Not frozen; awaiting the owner (G-FREEZE). Protocol hash: recorded at freeze.
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
- S1: theta in {0.3, 0.7} (new runs).
- S2: T in {10, 40} (new runs).
- S3: reanalysis of EXP-001 raw outputs: (a) welfare from standardized raw utility; (b) unmatched value equal to the acceptability threshold's satisfaction instead of 0. No new runs.

## 6. Unit, sampling, seeds
Market instance; 30 instances per corner cell, using the EXP-001 instances of those cells (same seeds) so that comparisons to EXP-001 are paired. S1 and S2: 4 cells x 30 instances x 3 arms x 4 settings = 1,440 runs. S3: 0 new runs.

## 7. Uncertainty
As EXP-001 (stratified bootstrap over instances, 10,000 resamples). No multiplicity correction; results are sensitivity evidence, not tests.

## 8. Budget, exclusion, stopping
At most 2 hours wall clock (planning). Exclusion and stopping as EXP-001.

## 9. Anticipated failure modes
theta = 0.7 with T = 10 may yield almost no matches, making W differences tiny and dominated by unmatched agents; this is reported as is.

## 10. Reproducibility commands (planned, M2)
```
uv run python -m match_lab.run --experiment EXP-003
uv run python -m match_lab.report --experiment EXP-003
```
Not implemented yet.
