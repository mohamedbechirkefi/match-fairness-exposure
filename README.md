<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# MATCH: matching algorithms and fairness

**Question.** How do ranking and exposure policies alter match outcomes under heterogeneous preferences?

**Status: M2 (core implementation), 2026-11-24.** The engine, metrics, runner and report generator are implemented and tested. Only exploratory pilot runs exist (`results/exploratory/`); they test no hypothesis and are not findings. The protocol is a draft awaiting the owner's freeze; confirmatory runs are refused until then.

## Why it matters

Platforms that help people find partners or counterparts decide who sees whom. That exposure choice can change who gets matched, how good matches are, and how unequally attention is spread. MATCH studies this question in fully synthetic markets, where every assumption is explicit and every run is reproducible.

## Design

- Synthetic two-sided markets with reciprocal preferences, varying side imbalance and preference correlation.
- Sequential discovery with three slate policies: random exposure (baseline), popularity ranking, exposure-balanced ranking.
- Centralized references: deferred acceptance (both sides proposing) and a utilitarian assignment.
- Metrics: mean agent welfare (primary), unmatched fraction, mutual satisfaction, exposure inequality, blocking pairs, subgroup outcomes.
- A static interactive page and a formal manuscript with one report per experiment.

See `research/protocol.md` and `research/experiment_registry.csv` (EXP-001 to EXP-003, planned).

## What is implemented

- Package `match_lab` (see `src/README.md`): market generator, the three slate policies, deferred acceptance, utilitarian assignment, all protocol metrics, uncertainty machinery, versioned result and manifest schemas, run manifests, report generator (Markdown, CSV, SVG, PDF through pandoc and Typst).
- CLI: `python -m match_lab {smoke,run,report,test}`.
- Test suite (`tests/README.md`), including Gale and Shapley stability on hand-computed examples and brute-force differential tests.
- Not implemented yet: the interactive page (M5), the manuscript content (M4).

## Quick start (development)

```
/Users/bechir/research/labs/.tools/py/bin/uv sync --frozen
/Users/bechir/research/labs/.tools/py/bin/uv run --frozen pytest -q
/Users/bechir/research/labs/.tools/py/bin/uv run --frozen python -m match_lab smoke   # exploratory
```

## Data

No external data. All data will be synthetic, generated from code, parameters and seeds (`data/manifest.json`). Public datasets examined and excluded are listed in `research/literature_review.md`.

## Limitations

Synthetic agents only; no claim about real people or any real platform. See `research/limitations.md`.

## Licence

Source-available, non-commercial research licence: MATCH Source-Available Non-Commercial Research License v1.0 (`LICENSE`, `NOTICE.md`). It is not an OSI-approved open-source licence. Contributions require the CLA (`CLA.md`, `CONTRIBUTING.md`).

## Citation

See `CITATION.cff`.
