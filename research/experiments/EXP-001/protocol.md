<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-001 protocol: exposure policies in sequential discovery

- **Status:** FROZEN v1.0 (owner-approved 2026-11-24). Drafted as v0.1; amended before the freeze as listed in the final section. Protocol hash: recorded in `research/freeze.json` and `research/experiment_registry.csv` (a file cannot contain its own hash).
- **Role:** primary (confirmatory once frozen).
- **Shared definitions:** `research/protocol.md` sections 2 to 4 (model, metrics, design). This file restates what is specific to EXP-001.

## 1. Precise question
In synthetic two-sided markets with reciprocal preferences, does the slate policy used during sequential discovery (POPULARITY or EXPOSURE_BALANCED versus RANDOM) change mean agent welfare W after T = 40 rounds?

## 2. Mechanism and rationale
Popularity ranking concentrates exposure on candidates whom many viewers like. Under correlated preferences (high rho) those candidates are also in high demand and can match only once, so the extra exposure may produce likes that never become matches, while less popular candidates are rarely seen. Exposure balancing spreads attention, which may raise the number of mutual likes for less popular agents at the cost of showing viewers less preferred candidates. Rankings that allocate exposure have been analysed as a fairness problem (Singh and Joachims 2018), and ranking by one-sided or reciprocal relevance has been argued to be suboptimal in matching markets with capacity limits (Su, Bayoumi and Joachims 2021, preprint). Under random preferences, small imbalance strongly favours the short side in stable outcomes (Ashlagi, Kanoria and Leshno 2017), which motivates varying r. Sources: `research/literature_review.md`.

## 3. Competing explanations
- Any welfare difference may come from matching speed under a fixed horizon rather than from final allocation (tested by S2 in EXP-003).
- Differences may be an artefact of the rank-percentile welfare scale or of scoring unmatched agents as 0 (S3).
- Differences may be driven by pickiness theta (S1).
- Policy differences may come from shorter slates under the exposure cap rather than from balancing (short-slate counts are reported).

## 4. Hypotheses
For P in {POPULARITY, EXPOSURE_BALANCED}: H0_P: theta_P = 0; H1_P: theta_P != 0, where theta_P is the equal-weight mean over the 9 cells of E[W_P - W_RANDOM]. Holm correction over the two contrasts, familywise alpha 0.05.

**Contradicting result:** Holm-adjusted p >= 0.05 for a contrast means H1_P is not supported for it. Equivalence is claimed only if the 90% CI of theta_P lies inside (-0.01, 0.01).

## 5. Estimand, unit, scope
- Estimand: theta_P (welfare units, [-1, 1] in principle).
- Experimental unit: one market instance; all three arms run on the same instance (paired).
- Scope: synthetic agents only, n_A = 200, n_B = round(r * 200), Gaussian common-plus-idiosyncratic utilities, capacity one.

## 6. Variables
- Independent: policy (3 levels); r in {1.0, 1.1, 1.5}; rho in {0.0, 0.5, 0.9}.
- Fixed: T = 40, k = 5, theta = 0.5, delta = 0.5; POPULARITY (and EXPOSURE_BALANCED, same score) ties broken by one shared random key per round.
- Dependent: primary W; secondary U (overall and per side), M, exposure Gini per side, blocking pairs per 100 agents, subgroup W by side and by q quartile, short-slate count, runtime.

## 7. Treatment, control, baseline
Control and baseline: RANDOM. Treatments: POPULARITY, EXPOSURE_BALANCED (definitions in `research/protocol.md` 2.2).

## 8. Sampling and seeds
30 instances per cell, 270 instances, 810 runs. Root seed 20261124 (fixed at the freeze, never used before). Per-instance and per-stream seeds via `numpy.random.SeedSequence` spawning; common random numbers across arms.

## 9. Sample-size rationale
About 80% power for dz of about 0.53 per cell and about 0.17 pooled (normal approximation). The pre-freeze planning run (`research/protocol.md` section 5) measured per-cell paired SDs of 0.0045 to 0.0190; the owner kept N = 30 at the freeze, and N is not changed afterwards.

## 10. Compute budget
Local CPU only, at most 30 minutes wall clock (measured need about 3 minutes at T = 20 in the pre-freeze planning run; T = 40 runs take up to about twice as long).

## 11. Metric formulas and units
As `research/protocol.md` 2.4. W, U, M are unitless fractions in [0, 1]; Gini in [0, 1]; blocking pairs per 100 agents; runtime in seconds.

## 12. Uncertainty method
Per-cell paired mean differences with 95% percentile bootstrap CIs (10,000 resamples of instances). theta_P: stratified bootstrap CI; p-value from a stratified paired sign-flip randomization test (10,000 draws); Holm adjustment. Effect sizes: mean difference and dz. Per-instance distributions plotted.

## 13. Exclusion and stopping rules
Exclusion only on failed validity checks; the instance is dropped from all arms; all exclusions listed; more than 5% excluded in a cell marks that cell failed. Fixed N; no interim looks.

## 14. Anticipated failure modes
Slow popularity learning with few impressions per round; exposure cap producing many short slates in unbalanced cells; near-zero matches when theta is high and T is short; floating-point ties in utilities at rho = 1 (not in the matrix).

## 15. Sensitivity tests
Registered separately as EXP-003 (S1 pickiness, S2 horizon, S3 metric definition).

## 16. Reproducibility commands
```
uv sync --frozen
uv run --frozen python -m match_lab smoke                                             # exploratory smoke
uv run --frozen python -m match_lab run --config experiments/configs/EXP-001.json     # confirmatory, after freeze only
uv run --frozen python -m match_lab report --results results/confirmatory/EXP-001/results.json --out results/confirmatory/EXP-001/report
```
`run` refuses this config unless the freeze record and the registry match the protocol and config files on disk. The executed commands and outputs go to `reproduction.md` when the experiment is run (M3).

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 (proposals A1 to A6, M2; see `research/protocol.md` section 10). Only approved items were applied.

- **F1:** primary horizon T = 40 (was 20): sections 1 and 6.
- **F2:** POPULARITY breaks ties with one shared random key per round: section 6.
- **F3:** N = 30 instances per cell kept: sections 8 and 9.
- **F4:** compute budget 30 minutes (was 2 hours): section 10.
- **F5:** the full-size pilot is the pre-freeze planning run: section 9.
- **F6:** implemented reproduction commands: section 16.
- Fixed at the freeze as the draft required: root seed 20261124 (section 8).
