<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# tests/

pytest suite (M2). Run with `uv run --frozen pytest -q`.

- `test_market.py`: generator shapes, units, determinism, satisfaction and acceptability hand examples, empty pools, invalid inputs, property tests.
- `test_matching.py`: Gale and Shapley hand examples (unique stable matching, proposer optimality, truncated lists, unbalanced markets), DA stability and proposer optimality against brute-force enumeration, MAXW against brute-force optimum, a hand-computed unstable MAXW example, validity checks (duplicates, capacity, consistency), empty pools, invalid inputs.
- `test_sequential.py`: hand examples, greedy resolution order, acceptability, zero rounds, empty markets, exposure cap, invariants, determinism, a differential test (all policies coincide when slates show everything), common random numbers, horizon prefix consistency, tie-key scope.
- `test_metrics_stats.py`: hand-computed metrics and Gini values, blocking pairs against brute force, bounds, statistics hand values, invalid inputs.
- `test_pipeline.py`: config to validated results, manifest and CSV, determinism, report banner and no p-values for exploratory runs, schema rejections, the confirmatory gate, the CLI.
