<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Supplementary material

Companion to `research/paper/manuscript.md` (independent research manuscript, preprint draft, not peer-reviewed). Synthesised in session M4 (2026-11-25) from committed results only. All results are synthetic simulations. Rows marked EXPLORATORY were computed after the confirmatory results were known; they test no hypothesis and change no frozen verdict.

## S1. Complete experimental matrix

Table S1. Every run set in the project, confirmatory and exploratory.

| Id | Status | Design | Root seed | Runs | Invalid | Journal | Outputs |
|---|---|---|---|---|---|---|---|
| SMOKE | exploratory (M2) | 4 corner cells, n_A = 50, 5 instances, T = 20 | 101 | 120 | 0 | J-0002 | `results/exploratory/smoke/` |
| PILOT | exploratory, pre-freeze planning run | 9 cells, 5 instances, six arms, T = 20 | 202 | 270 | 0 | J-0003 | `results/exploratory/pilot/` |
| PILOT-S | exploratory, pre-freeze planning run | 4 corner cells, 3 instances, S1 and S2 settings | 303 | 144 | 0 | J-0004 | `results/exploratory/pilot_sensitivity/` |
| PROBE-TIE | exploratory, pre-freeze planning run | 4 corner cells, 3 instances, per-viewer tie keys | 404 | 36 | 0 | J-0005 | `results/exploratory/probe_tie_scope/` |
| M3-SMOKE | exploratory pipeline check | as SMOKE | 101 | 120 | 0 | J-0009 | `results/exploratory/m3_smoke/` |
| EXP-001 | confirmatory, frozen v1.0 | 9 cells, 30 instances, three sequential arms, T = 40 | 20261124 | 810 | 0 | J-0010 | `results/confirmatory/EXP-001/` |
| EXP-002 | secondary, frozen v1.0 | 9 cells, same instances, DA_A, DA_B, MAXW | 20261124 | 810 | 0 | J-0011 | `results/confirmatory/EXP-002/` |
| EXP-003 S1, S2 | sensitivity, frozen v1.0 | 4 corner cells, 30 instances, 4 settings | 20261124 | 1,440 | 0 | J-0012 | `results/confirmatory/EXP-003/` |
| EXP-003 S3 | registered, not run (D-018, D-019) | reanalysis of EXP-001 | n/a | 0 | n/a | J-0013 | none |
| M4-CONFOUNDERS | EXPLORATORY (M4) | reanalysis of committed EXP-001 to EXP-003 outputs; no runs | n/a | 0 | n/a | J-0014 | `results/exploratory/m4_confounders/` |
| M4-HORIZON | EXPLORATORY (M4) | 9 cells, 10 instances, three sequential arms, T in {40, 80, 160} | 505 | 810 | 0 | J-0015 | `results/exploratory/m4_horizon_probe/` |

Superseded M2 executions and the accidental freeze-session run were deleted (J-0006, J-0007, J-0008); none was read for any result.

## S2. Expected versus observed

Table S2. Every registered prediction, the observation and the verdict under the frozen rule.

| Experiment, contrast | Registered expectation | Pre-freeze exploratory value (C4) | Observed (confirmatory) | Verdict under the frozen rule |
|---|---|---|---|---|
| EXP-001, POPULARITY | nondirectional H1; no sign fixed | -0.2917 at T = 20 (9 cells); +0.0178 at T = 40 (corner cells) | +0.0219, 95% CI +0.0207 to +0.0231, Holm p = 0.0002 | H1 supported; not robust (EXP-003 S2) |
| EXP-001, EXPOSURE_BALANCED | nondirectional H1; equivalence only if the 90% CI lies in (-0.01, 0.01) | +0.0034 at T = 20; +0.005 at T = 40 (corner) | +0.0004, 90% CI -0.0005 to +0.0013, Holm p = 0.5137 | H1 not supported; equivalent to 0 at margin 0.01 |
| EXP-002, H_a: W(DA_A) - W(RANDOM) | nondirectional, secondary | not tested | +0.0963, 95% CI +0.0954 to +0.0973 | supported (secondary) |
| EXP-002, H_b: blocking pairs MAXW - DA_A | nondirectional, secondary | not tested | +231.06 per 100 agents, 95% CI +226.32 to +235.70 | supported (secondary) |
| EXP-002, DA invariant | 0 blocking pairs for DA | 0 in the pilot | 0 of 540 DA runs | invariant held |
| EXP-003 S2, POPULARITY | invalidation if opposite sign with CI excluding 0 | -0.4068 at T = 10 (corner) | -0.4081 at T = 10; -0.2824 at T = 20 | criterion met: EXP-001 POPULARITY not robust |
| EXP-003 S2, EXPOSURE_BALANCED | as above | +0.0059 at T = 10 (corner) | +0.0008 at T = 10; +0.0049 at T = 20 | criterion not met |
| EXP-003 S1, both policies | reported, not a criterion | POPULARITY negative at T = 20 | POPULARITY +0.0340 and +0.0030; EXPOSURE_BALANCED +0.0052 and +0.0041 | sign kept (no verdict attached) |
| EXP-003 S3 | invalidation criterion as S2 | n/a | not run | no verdict; the threat stays open |

The pre-freeze S1 values were measured at T = 20, before amendment F1 moved S1 to T = 40, so they are not comparable with the confirmatory S1 values.

## S3. Configurations and hashes

| Config | File SHA-256 | Canonical SHA-256 | Protocol SHA-256 |
|---|---|---|---|
| `experiments/configs/EXP-001.json` | cb65e283c7d35d342e76abb9221e400a43b7603be2d1f4a510158f25531467e5 | 5e747575d51c0b0253ffcc20ca22fdb1e0f3770c7421f1546f7ff8ebc93df422 | 0d64280b9e2dcb0a3f17bf056eaf3cadf5f5a009efa88d6eed99ad05eafb3c2c |
| `experiments/configs/EXP-002.json` | 105c89cc03e8d613cdc593e79775116f0bb38bfa0d55802768c6ac2823c77ac3 | 2bd7ee667eaadef716496cff55bf2a343743f0984e4c1f44552279dea1a540b7 | 30692ad843399f50c1a1141f71b16e6fb704b2669d8ab5dd1e586de67485961c |
| `experiments/configs/EXP-003.json` | c22013c6a6799ef317890eab5784cdc4f2a5acad2cc8eafd35d5038a0ead9a1b | 91669781cf730391a79dcc6a36e3317a5c7f83202c2a603c3e393d563bc37489 | 7e37ac6ad46f9da93bd66763a7caf3f53e97a367b83d31e727e14f35ded628f6 |
| `experiments/configs/m4_horizon_probe.json` (EXPLORATORY) | b3161b76b0e25ade507a66a403c60d888553af0f74e2fb66dd6d85a8ab7a8b6d | fd266e995e7ddcc17778b48ac0f54d4afb94c0a0b2a8fa279d2675c217652886 | none (exploratory) |

Main protocol `research/protocol.md`: 81f24e9e4bc15434837208705f61619d6415bd1643985142248c926482e160c5. Confirmatory code revision: cfc90d0dfa9aa9058ee780a8d8fe3abdc77343d3. The M4 exploratory probe ran at revision e1050b29aa3d325f0811d718e33286f4c8d7b887 with its config and scripts not yet committed; they were committed unchanged in cff9d7c61ee7603dd335220314e408569457a98c.

Fixed design values: n_A = 200; k = 5; delta = 0.5; theta = 0.5 (S1: 0.3, 0.7); T = 40 (S2: 10, 20); POPULARITY tie key shared per round (`popularity_tie_scope = "global"`).

## S4. Robustness results

### S4.1 EXP-002 per cell

Table S4. Per-cell secondary contrasts (`results/confirmatory/EXP-002/analysis/tables/EXP-002_contrasts.csv`).

| r, rho | W(DA_A) - W(RANDOM) | 95% CI | Blocking pairs per 100, MAXW - DA_A | 95% CI |
|---|---|---|---|---|
| 1.0, 0.0 | +0.1714 | +0.1683 to +0.1745 | +14.87 | +14.08 to +15.65 |
| 1.0, 0.5 | +0.1124 | +0.1086 to +0.1163 | +185.69 | +177.08 to +194.05 |
| 1.0, 0.9 | +0.0449 | +0.0421 to +0.0476 | +603.61 | +578.77 to +628.41 |
| 1.1, 0.0 | +0.1355 | +0.1322 to +0.1388 | +30.69 | +29.46 to +31.97 |
| 1.1, 0.5 | +0.1114 | +0.1086 to +0.1141 | +140.05 | +132.66 to +147.41 |
| 1.1, 0.9 | +0.0453 | +0.0429 to +0.0477 | +537.06 | +510.37 to +563.30 |
| 1.5, 0.0 | +0.0978 | +0.0953 to +0.1002 | +73.75 | +71.71 to +75.91 |
| 1.5, 0.5 | +0.1001 | +0.0977 to +0.1025 | +91.28 | +87.51 to +95.57 |
| 1.5, 0.9 | +0.0481 | +0.0456 to +0.0506 | +402.55 | +385.33 to +419.23 |

### S4.2 EXPLORATORY: unmatched-value sweep (E2, J-0014)

Table S5. theta(v) = theta + v Delta U for a constant unmatched value v, 95% stratified bootstrap CIs (`results/exploratory/m4_confounders/unmatched_value_sweep.csv`, `decomposition.csv`). Break-even v is the value at which the point estimate would be 0.

| Contrast (cells) | v = 0 | v = 0.5 | v = 1 | Break-even v |
|---|---|---|---|---|
| EXP-001 POPULARITY (9) | +0.0219 [+0.0207, +0.0231] | +0.0229 [+0.0221, +0.0238] | +0.0239 [+0.0230, +0.0249] | -10.87 (outside [0, 1]) |
| EXP-001 EXPOSURE_BALANCED (9) | +0.0004 [-0.0007, +0.0015] | +0.0023 [+0.0015, +0.0032] | +0.0043 [+0.0033, +0.0052] | -0.10 (outside [0, 1]) |
| EXP-003 S2 T 10, POPULARITY (4) | -0.4081 [-0.4098, -0.4064] | -0.1349 [-0.1360, -0.1340] | +0.1382 [+0.1370, +0.1393] | 0.75 |
| EXP-003 S2 T 20, POPULARITY (4) | -0.2824 [-0.2843, -0.2804] | -0.0868 [-0.0879, -0.0856] | +0.1088 [+0.1076, +0.1102] | 0.72 |
| EXP-003 S1 theta 0.7, POPULARITY (4) | +0.0030 [+0.0009, +0.0051] | +0.0060 [+0.0050, +0.0070] | +0.0089 [+0.0080, +0.0098] | -0.52 (outside [0, 1]) |
| EXP-002 H_a, DA_A (9) | +0.0963 [+0.0953, +0.0973] | +0.0966 [+0.0959, +0.0973] | +0.0969 [+0.0960, +0.0977] | -180.49 (outside [0, 1]) |

The 90% CI of the EXP-001 EXPOSURE_BALANCED contrast stays inside (-0.01, 0.01) for every v in {0, 0.25, 0.5, 0.75, 1}; its largest upper bound is +0.0051. The v = 0 point estimates equal the frozen ones. The v = 0 intervals come from a different bootstrap stream, so three bounds differ from the frozen ones in the last digit: S2 T 20 upper bound -0.2804 (frozen -0.2805), S1 theta 0.7 upper bound +0.0051 (frozen +0.0052) and EXP-002 H_a lower bound +0.0953 (frozen +0.0954). The frozen values govern.

### S4.3 EXPLORATORY: decomposition (E3, J-0014)

Table S6. Paired differences in the matched share (1 - U) and in the mean satisfaction of matched agents Q = W/(1 - U), equal-weight (`decomposition.csv`).

| Contrast | Delta matched share | Delta Q | 95% CI of Delta Q |
|---|---|---|---|
| EXP-001 POPULARITY - RANDOM | -0.0020 | +0.0282 | +0.0272 to +0.0292 |
| EXP-001 EXPOSURE_BALANCED - RANDOM | -0.0039 | +0.0041 | +0.0030 to +0.0051 |
| EXP-003 S2 T 10, POPULARITY - RANDOM | -0.5463 | +0.0282 | +0.0254 to +0.0309 |
| EXP-003 S2 T 20, POPULARITY - RANDOM | -0.3912 | +0.0285 | +0.0263 to +0.0306 |
| EXP-002 DA_A - RANDOM | -0.0005 | +0.1167 | +0.1157 to +0.1176 |
| EXP-002 MAXW - RANDOM | +0.0535 | +0.1330 | +0.1321 to +0.1339 |

### S4.4 EXPLORATORY: horizon saturation and the horizon-extension probe (E1, E4; J-0014, J-0015)

In the committed EXP-001 runs, every POPULARITY instance had a new match in round 40 (2 to 7 matches), and 25.2% to 26.8% of its matches per cell formed in rounds 31 to 40. RANDOM had no match after round 30 except at r = 1.5, rho = 0.9 (57% of instances); EXPOSURE_BALANCED had none except at r = 1.5 with rho = 0.5 (3%) and 0.9 (7%) (`results/exploratory/m4_confounders/horizon_saturation.csv`).

Table S7. Horizon-extension probe, per-cell mean paired differences versus RANDOM, 10 instances per cell, root seed 505 (`results/exploratory/m4_horizon_probe/analysis/cells.csv`). Values at T = 160 equal those at T = 80.

| r, rho | POPULARITY, T 40 | POPULARITY, T 80 | EXPOSURE_BALANCED, T 40 and 80 |
|---|---|---|---|
| 1.0, 0.0 | +0.0366 | +0.0366 | +0.0072 |
| 1.0, 0.5 | +0.0650 | +0.0650 | -0.0058 |
| 1.0, 0.9 | +0.0349 | +0.0349 | -0.0005 |
| 1.1, 0.0 | +0.0215 | +0.0337 | +0.0105 |
| 1.1, 0.5 | +0.0341 | +0.0578 | -0.0043 |
| 1.1, 0.9 | +0.0132 | +0.0305 | -0.0011 |
| 1.5, 0.0 | +0.0181 | +0.0270 | +0.0028 |
| 1.5, 0.5 | -0.0023 | +0.0328 | +0.0081 |
| 1.5, 0.9 | -0.0257 | +0.0195 | +0.0025 |
| Pooled (95% CI) | +0.0217 (+0.0196 to +0.0238) | +0.0375 (+0.0356 to +0.0394) | +0.0022 (+0.0002 to +0.0041) |

Last round with a POPULARITY match (`m4_horizon_probe/analysis/saturation.csv` and `results.json`): 40 in every r = 1.0 instance; 41 to 44 at r = 1.1; 41 to 60 at r = 1.5. These bounds equal n_B / k = 40, 44 and 60 rounds.

### S4.5 Confounder inspection

Table S8. Competing explanations named in the frozen protocols (EXP-001 section 3, EXP-002 section 3, EXP-003 section 3) and those identified in M4.

| Conclusion | Competing explanation | Source | Evidence | Status after M4 |
|---|---|---|---|---|
| C-001 POPULARITY effect | speed within a fixed horizon | EXP-001 protocol 3; EXP-003 3(a) | S2 reversal (registered); E1 POPULARITY still matching at T = 40; E4 larger positive effect at T = 80 (exploratory) | the main explanation of the horizon dependence; the sign at T = 40 is a fixed-horizon quantity |
| C-001 | rank-percentile scale; unmatched = 0 | EXP-001 3; EXP-003 3(b) | S3 not run; E2 covers a constant unmatched value only | open (scale); unmatched value: no effect on the T = 40 sign |
| C-001 | pickiness | EXP-001 3; EXP-003 3(c) | S1 | sign kept at theta 0.3 and 0.7 |
| C-001 | heterogeneity across cells | M4 | Table 3; E4 | negative cells at T = 40 turn positive at T = 80 in the probe (exploratory) |
| C-001 | tie-key implementation | M4 (from J-0005) | pre-freeze probe only | open; results describe the shared-key implementation |
| C-002 EXPOSURE_BALANCED null | shorter slates under the cap | EXP-001 3 | cap diagnostics: at most 1.05% shortened (EXP-001), 1.62% (EXP-003) | ruled out as a driver |
| C-002 | scale; unmatched = 0 | EXP-003 3(b) | S3 not run; E2 | equivalence holds for any constant unmatched value; scale open |
| C-002 | the policy does not balance exposure relative to RANDOM | M4 | side-B Gini higher than RANDOM in 4 of 9 cells | the null concerns this cap rule, not exposure balancing in general |
| C-003 DA versus RANDOM | full information versus mechanism | EXP-002 3 | none | open by design |
| C-003 | truncation at the acceptability threshold | EXP-002 3 | none | open |
| C-003, C-004 | rank-percentile scale | EXP-002 3 | S3 not run; E2 for C-003 | H_a insensitive to a constant unmatched value; scale open |
| C-004 MAXW blocking pairs | count per pair inflates dense acceptability | EXP-002 report 9 | none | open; a per-agent instability measure was not computed |

## S5. Experiment report links

- EXP-001: `research/experiments/EXP-001/report.md`, reproduction `research/experiments/EXP-001/reproduction.md`.
- EXP-002: `research/experiments/EXP-002/report.md`, reproduction `research/experiments/EXP-002/reproduction.md`.
- EXP-003: `research/experiments/EXP-003/report.md`, reproduction `research/experiments/EXP-003/reproduction.md`.
- Generated run reports with all tables and figures: `results/confirmatory/EXP-00N/report/report.md`.
- Exploratory M4 diagnostics: journal entries J-0014 and J-0015 in `research/experiment_journal.jsonl`.

## S6. Deviations from the frozen protocols and owner decisions

| Item | Decision | Effect |
|---|---|---|
| EXP-003 S3 not run | D-018 (session), D-019 (owner, 2026-11-25) | metric-definition threat open; no S3 parameters chosen after the data |
| Provenance revision cfc90d0 instead of 88f3438 | D-017 | analysis module, CLI, tests and records only; frozen hashes match |
| Frozen contrasts of EXP-002 and EXP-003 computed by `analyze` instead of the protocol's `report` command | D-017 | analysis fixed before any confirmatory output |
| Unscheduled EXP-001 execution during the freeze session | D-014, D-016 | quarantined unread, deleted on the owner's approval |
| Reports written from committed results by the coordinator | D-020 | no recomputation |
| Pre-freeze exploratory values seen before the freeze | C4 disclosure in `research/freeze.json` | the owner chose T = 40 and the tie rule with these values available |
| M4 exploratory diagnostics (E1 to E4) | D-021 | exploratory only; no verdict changed |
| Blocking pairs per 100 agents unbounded above (rest of A6, not applied at the freeze) | reporting note | stated wherever the metric appears |
