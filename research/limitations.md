<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Limitations (living document, updated M2)

No confirmatory result exists yet. These are the limitations known from the design and from the M2 implementation.

1. **Synthetic agents only.** Preferences are Gaussian common-plus-idiosyncratic utilities. Findings hold only within this model; they are not evidence about real people, real dating or job platforms, or any proprietary ranking system.
2. **Stylized behaviour.** Agents like a candidate if utility exceeds a fixed quantile threshold; there is no strategic behaviour, learning, fatigue, messaging, or leaving the platform. These omissions may change policy rankings.
3. **Stylized policies.** POPULARITY and EXPOSURE_BALANCED are simple, interpretable rules, not reproductions of any deployed algorithm.
4. **Metric dependence.** The primary metric (rank-percentile welfare with unmatched = 0) is one defensible choice among several; EXP-003 S3 checks the main alternative.
5. **Fixed horizon.** Sequential outcomes after T rounds conflate speed and final allocation; EXP-003 S2 checks this.
6. **No real-data calibration.** Candidate public datasets have unclear redistribution rights and are excluded (D-003).
7. **Subgroups are synthetic.** Subgroup analyses use side and latent-quality strata, never protected attributes; no fairness claim about demographic groups is possible.
8. **Toolchain.** No TeX distribution; `manuscript.tex` is generated but not compiled locally (D-002).
9. **Literature coverage.** The M0 review is a short, non-systematic search; several entries are verified only at metadata or abstract level.
10. **Implementation readings of the draft protocol (M2).** The popularity tie key is global per round by default (D-007); exploratory runs show this choice materially changes the POPULARITY arm. Acceptability uses numpy's linear quantile per agent. n_B rounds half up.
11. **Runtime measurements are load-sensitive.** Runs share a machine with other sessions; the same pilot took about twice as long in one execution as in another (J-0006). Runtimes are planning figures, not benchmarks.
12. **Peak memory is sampled.** It is measured with tracemalloc on a re-run of the first instance per (cell, setting, arm) only, and covers Python and numpy allocations, not the whole process (D-008).
