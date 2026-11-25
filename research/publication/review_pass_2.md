<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Second review pass: arguing against the preferred reading (M4, 2026-11-25)

**Object.** `research/paper/manuscript.md` version 0.9 (draft before this pass), the three experiment reports and the M4 exploratory diagnostics (J-0014, J-0015).

**Nature.** Internal quality control by the AI assistant, written to challenge the draft's preferred reading, not to polish it. It is not external peer review.

**Preferred reading in draft 0.9.** The draft makes four claims:

1. Popularity ranking raises welfare at the primary horizon. The effect is not robust to shorter horizons.
2. The policy difference lies mainly in the speed and quality of matching, "rather than in the number of agents eventually matched".
3. Popularity ranking works by sweeping the long side in a common order.
4. Exposure-balanced ranking is equivalent to random exposure.

Each challenge below ends with a verdict: **holds** (the manuscript is changed), **partly holds** (the claim is qualified) or **rejected** (with the reason).

## R1. The "speed, not number" conclusion is contradicted by the project's own probe

- **Challenge.** Conclusion 9 of draft 0.9 says the main policy difference is "in the speed and quality of matching rather than in the number of agents eventually matched". The exploratory horizon probe contradicts this. At T = 80, after every arm has stopped matching, POPULARITY leaves fewer agents unmatched than RANDOM: the equal-weight Delta U is -0.0199 (`results/exploratory/m4_horizon_probe/analysis/pooled.csv`). At T = 40 the sign is the opposite (+0.0026).
- **Verdict: holds.** The sentence is removed. The conclusion now states that the probe suggests the eventual allocation under POPULARITY has both more matched agents and better matched agents. It also states that this comes from 10 exploratory instances per cell on a different seed.

## R2. The "common-order sweep" mechanism is not shown by the saturation bound

- **Challenge.** The draft cites the fact that POPULARITY's last match falls exactly at n_B / k rounds (40, 44, 60) as fitting a sweep in a common order. That bound is mechanical. Every viewer sees only candidates it has not seen before, so under any policy a viewer has seen the whole other side after at most n_other / k rounds. Reaching the bound therefore shows only that POPULARITY keeps producing new mutual likes until viewers run out of candidates. It does not show that viewers see the same order.
- **Supporting evidence.** The only support for a common order is the M2 observation that POPULARITY with the shared tie key shows "nearly the same slate to every viewer" (J-0003, exploratory). POPULARITY also has zero short slates in every cell, against 0.0822 to 0.5325 for RANDOM (`EXP-001_arm_summary.csv`). Both are consistent with the sweep reading but do not test it.
- **Verdict: holds.** The Discussion now says that the bound is mechanical and that the common-order reading is a hypothesis resting on the M2 observation. The sweep is no longer presented as fitted by the bound.

## R3. "Better-matched pairs" may be a composition effect

- **Challenge.** Q = W / (1 - U) is the mean satisfaction over matched agents. Different arms match different agents, so a higher Q can come from who gets matched rather than from better partners for the same agents. Mutual satisfaction M is subject to the same selection. The draft says POPULARITY "produces better-matched pairs, not more pairs" as if it were a within-agent effect.
- **Mitigating evidence.** At T = 10, POPULARITY matches only a fraction of agents yet keeps the same Q gain (+0.0282). That pattern is hard to explain only by selecting easy-to-satisfy agents, but it does not rule selection out.
- **Verdict: partly holds.** The manuscript now describes Q and M as averages over the matched agents. It names composition as an alternative explanation that the design cannot separate.

## R4. The primary horizon was chosen with knowledge of where POPULARITY turned positive

- **Challenge.** The pre-freeze pilot showed POPULARITY at -0.2917 at T = 20 and +0.0178 at T = 40. The owner then fixed T = 40 as primary. The confirmatory estimate (+0.0219) is close to that pilot value. A reader could see the primary horizon as selected, knowingly or not, to make POPULARITY look good.
- **Facts.** The draft discloses the C4 values. It also notes that the frozen S2 criterion caught the dependence on the horizon.
- **What the draft omits.**
  - T = 40 is exactly n / k for the balanced cells, the round at which POPULARITY's matching ends there.
  - The rationale recorded for amendment F1 was to let all arms stop matching. The M4 diagnostics show this was not achieved for POPULARITY at r > 1.
- **Verdict: holds.** Limitations and Methods now say this explicitly:
  - the horizon was chosen after exploratory values were seen;
  - it did not achieve its stated purpose for POPULARITY;
  - the confirmatory p-value tests a fixed-horizon contrast whose choice was informed by pilot data. The p-value is therefore valid for that contrast, but it is not evidence for a horizon-free effect.

## R5. The exploratory probe is being read as if it were confirmatory

- **Challenge.** The draft's abstract and conclusion lean on the probe. It is post hoc, has 10 instances per cell, uses a new seed and was designed after the S2 result was known. Its pooled value at T = 80 (+0.0375) is the most favourable number for POPULARITY in the manuscript.
- **Verdict: partly holds.** The probe is labelled exploratory everywhere, and the abstract mentions only its saturation finding. The Discussion and Conclusion now say:
  - the probe generates a hypothesis for a pre-registered horizon-free experiment;
  - it changes no verdict.
- **Rejected part.** The challenge that the probe should be removed is rejected. It is the only direct evidence on the main competing explanation, and omitting it would hide a result that qualifies the confirmatory reading.

## R6. Overgeneralization: "40 rounds" has no meaning outside n = 200 and k = 5

- **Challenge.** The draft discusses short and long horizons as if they were absolute.
- **Evidence.** The probe shows that the relevant scale is the number of rounds T k / n_B needed to show the whole long side. The study ran one market size and one slate length, so the horizon results cannot be transferred to other sizes, slate lengths or real search durations.
- **Verdict: holds.** Section 7 now states that horizons are meaningful only relative to n / k in this model. The Discussion no longer uses "short search" and "long search" without that reference.

## R7. The EXPOSURE_BALANCED null may mean that the policy is close to random, not that balancing exposure is neutral

- **Challenge.** EXPOSURE_BALANCED did not lower exposure inequality relative to RANDOM in four of nine cells. Its timing profile also resembles RANDOM:
  - short-slate share 0.0649 to 0.4910, against RANDOM's 0.0822 to 0.5325 and POPULARITY's 0;
  - last matches early, like RANDOM (`horizon_saturation.csv`).

  A plausible reading is that the per-round cap, applied when most scores are still near their prior, produces near-random slates. On that reading, the equivalence result shows that this policy behaves much like random exposure. It shows nothing about exposure balancing as a goal.
- **Verdict: holds.** The Results and Discussion now say that EXPOSURE_BALANCED behaved like RANDOM on timing and exposure diagnostics. The equivalence claim (C-002) is restricted to this cap rule.

## R8. The equivalence margin and the narrow intervals

- **Challenge 1: the margin is generous.** The margin of 0.01 is about half the POPULARITY effect, so an effect half as large as POPULARITY's would still count as "equivalent".
- **Response.** The margin was pre-registered as one percentile point of welfare. The 90% CI (-0.0005 to +0.0013) is far inside it, so the conclusion does not depend on the margin's generosity.
- **Challenge 2: the intervals are conditional on the model.** The very narrow intervals reflect common random numbers and model-internal variance only. They say nothing about model uncertainty.
- **Verdict: partly holds.** Challenge 1 is rejected for the reason given. For challenge 2, Section 7 now says that the intervals quantify only sampling variation across synthetic instances within one model.

## R9. Missing failed runs, leakage and stale artifacts

- **Missing runs.** The audit (`research/publication/evidence_audit.md`) found no run dropped. Superseded and accidental executions are listed in supplementary S1 with their journal entries. No exploratory run enters a confirmatory table.
- **Leakage.**
  - EXP-002 and EXP-003 share the EXP-001 instances by design, and the analysis code was committed before outputs existed.
  - The M4 probe uses a new seed.
  - The only leakage path is the pre-freeze pilot (R4).
- **Stale artifacts.** The audit found and fixed several stale items:
  - registry statuses ("report not written");
  - the README status line (M2);
  - the `experiments/` and `results/` READMEs, which still said confirmatory results did not exist;
  - the M0-era claims audit.

  The figures used by the manuscript are byte-identical to the generated ones.
- **Verdict: rejected for runs and leakage beyond R4.** No missing run or further leakage path was found. The stale artifacts are fixed (audit F-01 to F-05).

## R10. Is the confirmatory POPULARITY result practically meaningful?

- **Challenge.** At T = 40 the pooled gain is 0.0219 on a 0 to 1 scale. Deferred acceptance exceeds random discovery by 0.0963, about four times as much. The draft's Discussion could be read as emphasizing a small effect.
- **Verdict: partly holds.** The Discussion now compares the magnitudes explicitly.

## R11. Title and abstract

- **Challenge.** The working title "Can optimal matching leave more people unhappy?" invites a yes or no answer that the evidence does not give. The revised title is accurate. The abstract sentence on the probe must not imply a confirmed final-allocation effect.
- **Verdict: holds.**
  - The title stays descriptive and is marked as proposed, pending the owner's approval.
  - The abstract's last sentences now separate the confirmatory and exploratory evidence.

## Changes made to the manuscript (version 0.9 to 1.0)

| Id | Section | Change |
|---|---|---|
| R1 | 9, 6 | removed "rather than in the number of agents eventually matched"; reported the probe's Delta U at T = 80 |
| R2 | 6 | the saturation bound is described as mechanical; the common-order sweep is a hypothesis resting on J-0003 |
| R3 | 5.4, 6 | Q and M described as averages over matched agents; composition named as an alternative |
| R4 | 4.1, 7 | the horizon choice and its unmet purpose for POPULARITY stated; scope of the p-value stated |
| R5 | abstract, 6, 9 | the probe is described as hypothesis-generating; no verdict changed |
| R6 | 6, 7 | horizons stated relative to n / k |
| R7 | 5.1, 6, 7 | EXPOSURE_BALANCED behaves like RANDOM on timing and exposure; the null is limited to this cap rule |
| R8 | 7 | the intervals reflect only within-model sampling variation |
| R10 | 6 | magnitude compared with the DA contrast |
| R11 | title, abstract | title marked as proposed pending the owner; abstract separates confirmatory from exploratory evidence |

None of these changes alters a frozen verdict. C-001 stays "supported, not robust", C-002 stays "equivalent at margin 0.01", C-003 and C-004 stay "supported (secondary)", and S3 stays "not run".
