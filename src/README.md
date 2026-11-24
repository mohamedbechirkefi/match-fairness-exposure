<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# src/

Python package `match_lab` (M2):

| Module | Layer |
|---|---|
| `market.py` | ingestion: synthetic market generator GEN-match-market v1 |
| `sequential.py` | simulation: sequential discovery with RANDOM, POPULARITY, EXPOSURE_BALANCED slates |
| `matching.py` | simulation: deferred acceptance (DA_A, DA_B), utilitarian assignment (MAXW), matching validity checks |
| `metrics.py` | metrics of protocol section 2.4 |
| `stats.py` | bootstrap, stratified bootstrap, sign-flip test, Holm, sample size |
| `config.py` | config schema `match-config/1.0.0` and the protocol-freeze gate |
| `schema.py` | result and manifest schemas, validated at export and import |
| `runner.py` | experiment runner and serialization |
| `report.py` | tables, SVG figures and PDF from result files |
| `cli.py` | `python -m match_lab {smoke,run,report,test}` |
