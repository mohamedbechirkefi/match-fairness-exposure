<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Limitations (living document, updated M4)

Confirmatory and secondary results exist since M3 (2026-11-24 runs). These are the limitations known from the design, the M2 implementation, the M3 runs and the M4 interpretation (items 17 to 21).

1. **Synthetic agents only.** Preferences are Gaussian common-plus-idiosyncratic utilities. Findings hold only within this model; they are not evidence about real people, real dating or job platforms, or any proprietary ranking system.
2. **Stylized behaviour.** Agents like a candidate if utility exceeds a fixed quantile threshold; there is no strategic behaviour, learning, fatigue, messaging, or leaving the platform. These omissions may change policy rankings.
3. **Stylized policies.** POPULARITY and EXPOSURE_BALANCED are simple, interpretable rules, not reproductions of any deployed algorithm.
4. **Metric dependence.** The primary metric (rank-percentile welfare with unmatched = 0) is one defensible choice among several; EXP-003 S3 was meant to check the main alternative but was not executed in M3 (specification gap, D-018); the owner recorded it as not run, a documented failure, with no parameters chosen after the data (D-019), so this limitation stays open. An M4 exploratory sweep (C-012) covers only a constant unmatched value, not the satisfaction scale.
5. **Fixed horizon.** Sequential outcomes after T rounds conflate speed and final allocation. EXP-003 S2 confirmed this for POPULARITY: its EXP-001 welfare gain at T = 40 reverses at T = 10 and 20 (C-005), so the POPULARITY result is not robust to the horizon. M4 exploratory diagnostics show that T = 40 itself truncates POPULARITY, which was still forming matches in every instance at round 40, but not RANDOM (C-010, C-011).
6. **No real-data calibration.** Candidate public datasets have unclear redistribution rights and are excluded (D-003).
7. **Subgroups are synthetic.** Subgroup analyses use side and latent-quality strata, never protected attributes; no fairness claim about demographic groups is possible.
8. **Toolchain.** No TeX distribution; `manuscript.tex` is generated but not compiled locally (D-002).
9. **Literature coverage.** The M0 review is a short, non-systematic search; several entries are verified only at metadata or abstract level.
10. **Implementation readings of the draft protocol (M2).** The popularity tie key is global per round by default (D-007); exploratory runs show this choice materially changes the POPULARITY arm. Acceptability uses numpy's linear quantile per agent. n_B rounds half up.
11. **Runtime measurements are load-sensitive.** Runs share a machine with other sessions; the same pilot took about twice as long in one execution as in another (J-0006). Runtimes are planning figures, not benchmarks.
12. **Peak memory is sampled.** It is measured with tracemalloc on a re-run of the first instance per (cell, setting, arm) only, and covers Python and numpy allocations, not the whole process (D-008).
13. **Heterogeneous POPULARITY effect (M3).** The pooled EXP-001 POPULARITY effect is positive but negative in the cells r = 1.5, rho = 0.5 and 0.9; the equal-weight estimand depends on the chosen cells.
14. **p-value floor (M3).** The sign-flip test uses 10,000 draws, so the smallest reportable p is 1/10,001 (Holm 0.0002 for two contrasts).
15. **Information confound in EXP-002 (M3).** Centralized arms use full preferences; the DA versus RANDOM contrast mixes information and mechanism.
16. **Per-run timing (M3).** Per-run start and end times are not recorded; each run's duration and the experiment's start and end are. EXP-001 and EXP-002 ran concurrently (2 processes); runtimes are diagnostics.
17. **Horizon chosen after pilot values were seen (M4).** The owner fixed T = 40 with the pilot values available (C4). It is the horizon at which POPULARITY had turned positive in the pilot, and it equals n_B / k in the balanced cells. Its recorded purpose, letting all arms stop matching, was not achieved for POPULARITY when r > 1. The confirmatory p-value is valid only for the fixed-horizon contrast.
18. **Horizon scale (M4).** Horizons are meaningful only relative to n_B / k, the number of rounds a viewer needs to see the whole other side (40, 44 or 60 here). With one market size and one slate length, no horizon result transfers to other sizes or to real search durations.
19. **EXPOSURE_BALANCED construct (M4).** The cap rule did not lower exposure inequality relative to RANDOM in four of nine cells, and its timing resembled RANDOM. The equivalence result (C-002) concerns this cap rule only.
20. **Composition (M4).** Mutual satisfaction M and the matched-agent satisfaction Q average over whichever agents are matched. Differences between arms mix partner quality with the composition of the matched set.
21. **Exploratory probe (M4).** The horizon-extension probe (C-011) is post hoc, uses one new seed and 10 instances per cell, and was designed after the S2 result. It motivates a pre-registered horizon-free experiment and supports no conclusion on its own.
