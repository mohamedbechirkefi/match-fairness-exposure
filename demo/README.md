<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# demo/: MATCH interactive page (M5)

A static, offline research page for the manuscript *Popularity ranking, exposure balancing and the length of search* (preprint draft, not peer-reviewed). Everything on it is synthetic: no real people, profiles or platforms. No visitor data is collected, stored or sent anywhere, and the page makes no request outside its own origin.

## What it shows

- **Overview** with the status label and the verdict of each experiment under its frozen rule.
- **Published results** (labelled *Measured*): forest charts of the POPULARITY and EXPOSURE_BALANCED contrasts across EXP-001, EXP-003 S1 and S2, and the not-run EXP-003 S3 row at the same size and weight as the measured rows; one panel per experiment (EXP-001, EXP-002, EXP-003) and per M4 exploratory diagnostic (labelled *Exploratory, not confirmatory*); the manuscript's Table 3 per cell. Every number is printed exactly as in the manuscript, with its interval where one exists: for example POPULARITY - RANDOM +0.0219 (95% CI +0.0207 to +0.0231), not robust to the horizon (-0.4081 at T 10, -0.2824 at T 20).
- **Fairness and satisfaction trade-off** (EXP-001, descriptive): mean welfare W against the Gini coefficient of side-B exposure per design cell, with one-standard-deviation whiskers.
- **Assumptions** (labelled *Model assumption*) and **method and limitations** (the manuscript's section 7).
- **Sandbox** (labelled *Sandbox output*): a population and matching graph for a 20-agent market, with seed, imbalance, preference correlation, pickiness, rounds, reset and cancel controls, run in a Web Worker.

## The sandbox engine

`src/engine.ts` is a line-by-line port of the Python engine (`src/match_lab/market.py`, `sequential.py`, `matching.py` for DA_A, `metrics.py`). `src/engine.test.ts` feeds it the exact inputs and random draws of the Python engine on two small markets (fixture `src/fixtures/engine_fixture.json`, written by `scripts/make_sandbox_fixture.py`) and requires identical matchings, exposures and counts, and metrics within an absolute 1e-12. The random number generator differs from numpy's, so a sandbox seed never reproduces a research run, and the sandbox market (20 agents on side A, at most 12 rounds) is much smaller than the study's. MAXW is not in the sandbox.

## Data

`public/data/results.json` (schema `lab-demo-results` 1.0.0, plus the MATCH keys `components`, `exp001_cells` and `tradeoff`) is written by `../scripts/export_demo_data.py` from committed results only, with the SHA-256 of every input. The loader in `src/results.ts` fails closed: a missing or malformed field shows an error panel and no numbers. `../tests/test_demo_export.py` re-runs the export and checks that every displayed string is printed in the manuscript.

## Commands

Node from `/Users/bechir/research/helix/.tools/node/bin`.

    cd demo && npm ci && npm run build && npm run preview
    npm test                                   # vitest: loader and engine port
    node tools/a11y_check.mjs dist --screenshots <dir>   # offline and accessibility check

Repository and demo URL: to be added after the owner's approval.
