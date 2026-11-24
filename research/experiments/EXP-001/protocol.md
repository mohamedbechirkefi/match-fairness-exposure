<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# EXP-001 protocol: exposure policies in sequential discovery

- **Status:** DRAFT v0.1, 2026-11-24. Not frozen; awaiting the owner (G-FREEZE). Protocol hash: recorded at freeze.
- **Role:** primary (confirmatory once frozen).
- **Shared definitions:** `research/protocol.md` sections 2 to 4 (model, metrics, design). This file restates what is specific to EXP-001.

## 1. Precise question
In synthetic two-sided markets with reciprocal preferences, does the slate policy used during sequential discovery (POPULARITY or EXPOSURE_BALANCED versus RANDOM) change mean agent welfare W after T = 20 rounds?

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
- Fixed: T = 20, k = 5, theta = 0.5, delta = 0.5.
- Dependent: primary W; secondary U (overall and per side), M, exposure Gini per side, blocking pairs per 100 agents, subgroup W by side and by q quartile, short-slate count, runtime.

## 7. Treatment, control, baseline
Control and baseline: RANDOM. Treatments: POPULARITY, EXPOSURE_BALANCED (definitions in `research/protocol.md` 2.2).

## 8. Sampling and seeds
30 instances per cell, 270 instances, 810 runs. Root seed fixed at the freeze, never used before. Per-instance and per-stream seeds via `numpy.random.SeedSequence` spawning; common random numbers across arms.

## 9. Sample-size rationale
About 80% power for dz of about 0.53 per cell and about 0.17 pooled (normal approximation). The smoke run's paired SD informs the owner's freeze decision on N; N is fixed at the freeze.

## 10. Compute budget
Local CPU only, at most 2 hours wall clock (planning estimate, to be checked against smoke timing).

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

## 16. Reproducibility commands (planned, implemented in M2)
```
uv sync --frozen
uv run python -m match_lab.run --experiment EXP-001 --smoke      # exploratory smoke
uv run python -m match_lab.run --experiment EXP-001              # confirmatory, after freeze only
uv run python -m match_lab.report --experiment EXP-001
```
These commands do not exist yet (M0). They will be recorded in `reproduction.md` once implemented and executed.
