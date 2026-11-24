<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# MATCH research protocol

**Status: DRAFT v0.1 (2026-11-24). Not frozen.** Written in session M0 before any experiment was run. No confirmatory run may start until the owner freezes this protocol and the per-experiment protocols (gate G-FREEZE); the freeze records the git commit and the SHA-256 of each frozen file in `research/decision_log.md` and `research/experiment_registry.csv`. Every number below is a planning proposal, not a result.

## 1. Research question

*How do ranking and exposure policies alter match outcomes under heterogeneous preferences?* (master prompt section 10)

Operational form: in synthetic two-sided markets with reciprocal preferences, when agents discover partners sequentially through slates chosen by a platform policy, does the policy (random exposure, popularity ranking, exposure-balanced ranking) change the average satisfaction of all agents, and how do these sequential outcomes compare with centralized two-sided matching (deferred acceptance, utilitarian assignment) on the same markets? Two factors are varied: side imbalance and preference correlation.

All participants are synthetic. Nothing here describes real people, protected attributes or the internals of any dating platform.

## 2. Formal model (shared by all experiments)

### 2.1 Population
- Two sides, A and B. |A| = n_A, |B| = n_B = round(r * n_A), with imbalance ratio r >= 1 (B is the long side).
- Each agent x has a latent common quality q_x ~ N(0, 1), independent.
- Utility of agent i for agent j on the other side: u_ij = sqrt(rho) * q_j + sqrt(1 - rho) * e_ij, with e_ij ~ N(0, 1) independent of everything. rho in [0, 1] is the **preference correlation**: for two different viewers i, i', corr(u_ij, u_i'j) = rho over candidates j. rho = 0 gives idiosyncratic (horizontal) tastes; rho near 1 gives near-consensus (vertical) tastes.
- Preferences are reciprocal: each side has utilities for the other side, drawn independently with the same rho.
- **Satisfaction** of i with j: s_ij = 1 - (rank_i(j) - 1) / (m_i - 1), where rank_i(j) is j's rank (1 = best) in i's strict ordering of the whole other side and m_i its size. s is unitless, in [0, 1]. Ties have probability zero; an explicit tie-break by index is applied anyway.
- **Acceptability.** i finds j acceptable iff u_ij >= tau_i, where tau_i is the theta-quantile of i's utilities over the other side. Primary theta = 0.5 (each agent accepts the better half of the other side).
- Capacity one on both sides. Unmatched agents have satisfaction 0.

### 2.2 Sequential discovery (EXP-001, EXP-003)
- Rounds t = 1..T (primary T = 20). In each round every unmatched agent, on both sides, is shown a slate of up to k = 5 unmatched candidates from the other side that it has not been shown before. Viewers are processed in a seeded random order.
- On seeing j, viewer i records a like iff j is acceptable to i.
- A pair becomes a **mutual like** once both have liked each other (in any rounds). At the end of each round, new mutual likes are resolved greedily in decreasing order of s_ij + s_ji (ties by agent indices); a pair is matched only if both agents are still unmatched. Matched agents leave the market.
- **Exposure** e_j = number of slates in which j has appeared.
- **Policies** (the platform does not observe q or u):
  - RANDOM (baseline, primary comparator): slate drawn uniformly without replacement from eligible candidates.
  - POPULARITY: eligible candidates sorted by smoothed like rate p_j = (L_j + 1) / (e_j + 2), where L_j is likes received; ties broken by a seeded random key. p_j is updated at the end of each round.
  - EXPOSURE_BALANCED: same score p_j, but in each round a candidate may appear in at most c = ceil((1 + delta) * k * V / C) slates, where V is the number of viewers and C the number of eligible candidates on the shown side at the start of the round; delta = 0.5. If fewer than k candidates remain under the cap, the slate is shorter (counted and reported).
- After T rounds, the matching is final.

### 2.3 Centralized matching (EXP-002)
- DA_A: deferred acceptance (Gale and Shapley 1962) with A proposing; DA_B: B proposing. Lists truncated to acceptable partners.
- MAXW: utilitarian assignment maximizing the sum over matched pairs of (s_ij + s_ji), restricted to mutually acceptable pairs (rectangular linear assignment, scipy).

### 2.4 Metrics (per market instance and arm)
- **Primary: mean agent welfare** W = (1 / (n_A + n_B)) * sum over all agents x of s_x, where s_x is x's satisfaction with its partner and 0 if unmatched. Unitless, [0, 1], higher is better.
- Unmatched fraction U, overall and per side.
- Mutual satisfaction M = mean over matched pairs of min(s_ij, s_ji).
- Exposure inequality: Gini coefficient of e_j per side (sequential arms only).
- Blocking pairs: count of pairs (i, j), mutually acceptable, where each is unmatched or strictly prefers the other to its partner; reported per 100 agents.
- Subgroup outcomes: W per side (short side A, long side B); W for the bottom and top quartile of q on each side; the gap between them. Subgroups are synthetic quality strata and sides, never protected attributes.
- Run diagnostics: wall-clock time, peak memory where available, number of short slates.

### 2.5 Why W is the primary metric
W combines the two outcomes the question cares about, whether an agent is matched and how good the match is for that agent, into one agent-level average, so it cannot improve by matching more agents badly or fewer agents well without that showing. Unmatched fraction, mutual satisfaction, exposure Gini, blocking pairs and subgroup gaps are secondary because each covers only one facet, and several (Gini, subgroup gaps) are fairness outcomes reported, not optimized (master prompt section 1).

## 3. Hypotheses (primary, EXP-001)

For policy P in {POPULARITY, EXPOSURE_BALANCED} and market instance m, let D_P(m) = W_P(m) - W_RANDOM(m), computed on the same instance with common random numbers.

Estimand: theta_P = (1/9) * sum over the 9 design cells of E[D_P | cell] (equal cell weights).

- **H0_P:** theta_P = 0.
- **H1_P:** theta_P != 0 (nondirectional; the literature reviewed does not fix the sign for this model).
- Family: the two contrasts, Holm correction, familywise alpha = 0.05.
- **Contradiction.** H1_P is not supported if the Holm-adjusted p-value is >= 0.05. Non-rejection is not evidence of equivalence; an equivalence statement additionally requires the 90% CI of theta_P to lie inside (-0.01, +0.01), the smallest effect size of interest (one percentile point of welfare).

## 4. Design

- **Experimental unit:** one market instance (one draw of q and e for both sides). Agents inside an instance are not independent and are never treated as units of analysis.
- **Factors:** r in {1.0, 1.1, 1.5}; rho in {0.0, 0.5, 0.9}; 9 cells. n_A = 200.
- **Arms:** RANDOM, POPULARITY, EXPOSURE_BALANCED (EXP-001); DA_A, DA_B, MAXW (EXP-002).
- **Seeds and pairing:** 30 instances per cell (planned). Instance seeds derive from a root seed via numpy `SeedSequence`; each arm runs on the same instance, and the viewer-order and tie-break streams are spawned per (instance, stream) so they are shared across arms where the arm consumes them identically. The confirmatory root seed is fixed at the freeze and has never been used for any exploratory run. Smoke and exploratory runs use a different root.
- **Sample-size rationale (planning).** With 30 paired instances per cell, a two-sided paired test at alpha 0.05 has about 80% power for a standardized paired effect dz of about 0.53 per cell (normal approximation n = (1.96 + 0.84)^2 / dz^2); the pooled 270 instances give about 80% power for dz of about 0.17. The paired standard deviation is unknown; the smoke run reports it (exploratory). Before freezing, the owner may raise N; N is never changed after the freeze. Each run is cheap, so N is not compute bound (to be confirmed by the smoke timing).
- **Uncertainty.** Per-cell mean D_P with 95% percentile bootstrap CI over instances (10,000 resamples). theta_P CI by stratified bootstrap (resample instances within each cell). p-values by a stratified paired sign-flip randomization test (10,000 draws, seeded). Effect sizes: mean difference in welfare units and dz. Raw per-instance distributions are always plotted.
- **Exclusion rule.** A run is invalid only if a validity check fails (duplicate match, capacity breach, non-finite metric, schema validation failure). An invalid run excludes that instance from all arms of the paired analysis; every exclusion is listed with its reason. If more than 5% of instances of any cell are excluded, that cell is reported as failed and the defect is fixed under a dated deviation.
- **Stopping rule.** Fixed N, no interim analysis, no optional stopping.
- **Compute budget.** Local Apple M1 Pro only. Planning budget: at most 2 hours wall clock per experiment. If exceeded, the run is stopped and reported; the matrix is reduced only by an owner-approved amendment.
- **Confounders and controls.** Common random numbers across arms; identical acceptability thresholds across arms; identical horizon T; viewer order shared across sequential arms. The welfare metric itself is a choice that could drive conclusions; see the sensitivity analyses.

## 5. Smoke matrix (exploratory, before the freeze)

n_A = 50; r in {1.0, 1.5}; rho in {0.0, 0.9}; 5 instances per cell; all six arms; T = 20, k = 5, theta = 0.5; root seed distinct from the confirmatory one. Purpose: check the pipeline, invariants, schema, metric ranges and runtime; estimate the paired SD for the sample-size check. Its results are labelled exploratory and are not used to test any hypothesis.

## 6. Full matrix (planned)

| Experiment | Cells | Instances per cell | Arms | Runs |
|---|---|---|---|---|
| EXP-001 | 9 (r x rho) | 30 | 3 sequential | 810 |
| EXP-002 | 9 (r x rho) | 30 (same instances as EXP-001) | 3 centralized | 810 |
| EXP-003 | 4 corner cells x 4 rerun settings (S1, S2); S3 is a reanalysis | 30 (EXP-001 instances) | 3 sequential | 1,440 |

## 7. Sensitivity analyses that could invalidate the main interpretation (EXP-003)

- **S1, pickiness:** theta in {0.3, 0.7} (vs 0.5).
- **S2, horizon (truncation):** T in {10, 40} (vs 20). If the sign or significance of theta_P depends on T, the policy effect is about the speed of matching within a fixed horizon, not about final outcomes, and the main interpretation must be restated.
- **S3, metric definition (reanalysis of EXP-001 data, no new runs):** welfare from standardized raw utility instead of rank percentile, and unmatched value set to the acceptability threshold (an outside option) instead of 0.

If theta_P changes sign under S2 or S3, the primary result is reported as not robust.

## 8. Exploratory versus confirmatory

Confirmatory: only the two Holm-corrected EXP-001 contrasts on the primary metric, after the freeze. Everything else (secondary metrics, per-cell patterns, interactions with r and rho, EXP-002 and EXP-003) is reported with the same uncertainty machinery but described as secondary or exploratory, with no claim of a confirmed effect.

## 9. Validity checks implemented before any run (M2)

Gale and Shapley stability on small hand-computed examples; zero blocking pairs for DA outputs; no duplicate matches; capacity one respected; empty pools (n = 0 on either side) handled without error; unbalanced markets; extreme rho (0 and 1); invalid inputs rejected with explicit errors; determinism for a fixed seed.

## 10. Amendments

None. Any change after the freeze is dated, justified, and kept separate from the frozen analysis.
