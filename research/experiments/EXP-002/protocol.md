<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-002 protocol: centralized two-sided matching versus sequential discovery

- **Status:** DRAFT v0.1, 2026-11-24. Not frozen; awaiting the owner (G-FREEZE). Protocol hash: recorded at freeze.
- **Role:** secondary. Its results are reported with uncertainty but are not part of the confirmatory family.
- **Shared definitions:** `research/protocol.md` sections 2 to 4.
- **Dependency:** uses the same market instances as EXP-001 (same root seed), so the RANDOM arm of EXP-001 is its comparator.

## 1. Precise question
On the same synthetic markets, how do centralized matchings (DA_A, DA_B, MAXW) differ from sequential random discovery (RANDOM, T = 20) in mean welfare W, unmatched fraction and the gap between the short and the long side; and does the welfare-maximizing assignment leave more agents in blocking pairs than a stable matching? (This addresses the working title "Can optimal matching leave more people unhappy?" without presupposing its answer.)

## 2. Mechanism and rationale
Deferred acceptance yields a stable matching, proposer-optimal among stable matchings (Gale and Shapley 1962; Roth 1982, metadata verified, full text not read). In unbalanced random markets stable outcomes strongly favour the short side (Ashlagi, Kanoria and Leshno 2017). A utilitarian assignment maximizes total satisfaction but need not be stable, so some agents may prefer to deviate. Sequential discovery is limited by search frictions, which Hitsch, Hortacsu and Ariely (2010) discuss as a possible reason predicted stable matches underpredict some sorting patterns (abstract only).

## 3. Competing explanations
Differences may reflect full information in the centralized arms rather than the mechanism itself; truncation at the acceptability threshold may dominate; the rank-percentile welfare scale may favour some arms (S3 reanalysis applies to EXP-002 data as exploratory).

## 4. Hypotheses (secondary)
- H0_a: mean over cells of E[W_DA_A - W_RANDOM] = 0; H1_a: != 0.
- H0_b: mean over cells of E[B_MAXW - B_DA_A] = 0, where B is blocking pairs per 100 agents; H1_b: != 0. B_DA_A = 0 by theorem; this is checked as an invariant and any non-zero value is a bug, not a result.
- Descriptive: W by side under DA_A versus DA_B, per cell.

**Contradicting result:** a 95% CI containing 0 means the contrast is not supported. Secondary contrasts are not multiplicity-protected and are labelled secondary.

## 5. Estimand, unit, scope
As EXP-001: market instance, paired across arms; equal-weight average over 9 cells.

## 6. Variables
Independent: arm (DA_A, DA_B, MAXW, plus RANDOM from EXP-001); r; rho. Fixed: theta = 0.5. Dependent: W, U (per side), M, blocking pairs, subgroup W, runtime.

## 7. Treatment, control, baseline
Baseline: RANDOM (sequential). Centralized arms are references with full information, not deployable platform policies.

## 8. Sampling and seeds
Same 270 instances as EXP-001; 810 additional runs. Centralized arms are deterministic given the instance (tie-breaks by index).

## 9. Sample-size rationale
Inherited from EXP-001.

## 10. Compute budget
At most 1 hour wall clock (planning estimate). MAXW uses scipy `linear_sum_assignment` on a 200 x 300 matrix at most.

## 11. Metric formulas
`research/protocol.md` 2.4.

## 12. Uncertainty
Per-cell and pooled paired bootstrap CIs (10,000 resamples, stratified by cell). Deterministic arms vary only across instances, so all uncertainty is between-instance.

## 13. Exclusion and stopping
As EXP-001. Any DA output with a blocking pair stops the experiment: the implementation is wrong.

## 14. Anticipated failure modes
MAXW with many unacceptable pairs (need masking with a large negative weight and post-filtering); rectangular assignment orientation errors; DA_B versus DA_A index confusion.

## 15. Sensitivity
S1 and S3 of EXP-003 may be applied to EXP-002 arms as exploratory analyses only.

## 16. Reproducibility commands (planned, M2)
```
uv run python -m match_lab.run --experiment EXP-002
uv run python -m match_lab.report --experiment EXP-002
```
Not implemented yet.
