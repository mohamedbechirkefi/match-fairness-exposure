<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Limitations (living document, M0)

No results exist yet. These are the limitations known from the design.

1. **Synthetic agents only.** Preferences are Gaussian common-plus-idiosyncratic utilities. Findings hold only within this model; they are not evidence about real people, real dating or job platforms, or any proprietary ranking system.
2. **Stylized behaviour.** Agents like a candidate if utility exceeds a fixed quantile threshold; there is no strategic behaviour, learning, fatigue, messaging, or leaving the platform. These omissions may change policy rankings.
3. **Stylized policies.** POPULARITY and EXPOSURE_BALANCED are simple, interpretable rules, not reproductions of any deployed algorithm.
4. **Metric dependence.** The primary metric (rank-percentile welfare with unmatched = 0) is one defensible choice among several; EXP-003 S3 checks the main alternative.
5. **Fixed horizon.** Sequential outcomes after T rounds conflate speed and final allocation; EXP-003 S2 checks this.
6. **No real-data calibration.** Candidate public datasets have unclear redistribution rights and are excluded (D-003).
7. **Subgroups are synthetic.** Subgroup analyses use side and latent-quality strata, never protected attributes; no fairness claim about demographic groups is possible.
8. **Toolchain.** No TeX distribution; `manuscript.tex` is generated but not compiled locally (D-002).
9. **Literature coverage.** The M0 review is a short, non-systematic search; several entries are verified only at metadata or abstract level.
