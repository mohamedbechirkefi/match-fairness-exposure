<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, made by, rationale, alternatives, consequences.

## D-001: Licence is the owner's custom non-commercial licence (2026-11-24)
- **Decision:** All original material is licensed under the MATCH Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-MATCH-NC-Research-1.0`), with a CLA for contributions.
- **Made by:** the owner, on 2026-11-24, before the first commit.
- **Rationale:** the owner chose a protective licence for their own protection.
- **Alternative not taken:** the master prompt (section 2) asks for an "owner-approved permissive code license". The owner decided otherwise; the owner's decision prevails.
- **Consequences:** the project is source-available, not OSI open source. README, CITATION.cff and the manuscript must not describe it as open source. Third-party data and dependencies keep their own licences (NOTICE.md). The licence files are not changed by sessions.

## D-002: Zero-cost publication toolchain without TeX (2026-11-24)
- **Decision:** PDFs are built as Markdown, then pandoc 3.6.3 to Typst, then compiled with the `typst` Python package (0.15.0). `research/paper/manuscript.tex` is generated from Markdown with pandoc and is not compiled locally.
- **Made by:** the M0 session, following the M0 brief.
- **Rationale:** no TeX distribution is installed (`which tex pdflatex xelatex` found none); installing one is unnecessary given a working free Typst path.
- **Consequences:** an exploratory smoke conversion was run in M0 (see `progress.md`); the PDF was not committed. LaTeX output is unvalidated by compilation, which is recorded as a limitation.

## D-003: Fully synthetic design; real datasets excluded (2026-11-24)
- **Decision:** no real dataset is used. Candidate datasets (Speed Dating on OpenML, libimseti) are documented in `research/literature_review.md` with unclear rights and are not downloaded.
- **Made by:** the M0 session, within the claims boundary of master prompt section 10.
- **Consequences:** results hold only within the synthetic model; no empirical calibration. Any later calibration to real data needs the owner's decision on rights.

## D-004: Protocol proposal v0.1 drafted, not frozen (2026-11-24)
- **Decision:** primary metric mean agent welfare W; baseline RANDOM exposure; nondirectional H1 for POPULARITY and EXPOSURE_BALANCED versus RANDOM, Holm-corrected; market instance as the unit; 30 instances per cell planned; sensitivity EXP-003. Registered EXP-001 to EXP-003 as "planned (protocol draft, awaiting owner freeze)".
- **Made by:** the M0 session as a proposal. Freezing is the owner's decision (G-FREEZE).
- **Alternatives considered:** unmatched fraction as primary (rejected: ignores match quality); a directional H1 (rejected: no verified source fixes the sign for this model); including centralized arms in the primary family (rejected: different information regime; they are references in EXP-002).

## D-005: Dependency lock with a two-week release cutoff (2026-11-24)
- **Decision:** `pyproject.toml` with numpy, scipy (runtime) and pytest, hypothesis (dev); `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"`; `uv.lock` produced with uv 0.9.5.
- **Rationale:** the M0 brief requires versions released at least two weeks before 2026-11-24.

## D-006: M2 architecture, schemas and the confirmatory gate (2026-11-24)
- **Decision:** separate modules for ingestion (`market.py`), simulation (`sequential.py`, `matching.py`), metrics (`metrics.py`), statistics (`stats.py`), configuration (`config.py`, schema `match-config/1.0.0`), runner and serialization (`runner.py`), schemas (`schema.py`: `match-result/1.0.0`, `match-manifest/1.0.0`, validated at export and at import), reports (`report.py`) and CLI (`cli.py`: `smoke`, `run`, `report`, `test`). Seeds: `SeedSequence(entropy=root_seed, spawn_key=(round(1000 r), round(1000 rho), instance))`, so an instance depends on its cell values and index, not on its position in a matrix, and EXP-002 and EXP-003 reuse EXP-001 instances by construction. A confirmatory config runs only if the registry holds a 64-hex `protocol_hash` equal to the SHA-256 of the protocol file; exploratory output must live under `results/exploratory/`, confirmatory output must not. Raw results are never overwritten without `--overwrite`.
- **Made by:** the M2 session, under the M2 brief.
- **Alternatives:** a JSON Schema library (rejected: a new dependency for a small schema; a hand-written validator is tested instead); matplotlib for figures (rejected: new dependency; figures are generated as SVG directly).
- **Consequences:** no new dependency; `uv.lock` unchanged (`uv lock --check` passes). The draft protocols' reproduction commands (`python -m match_lab.run --experiment ...`) differ from the implemented CLI (`python -m match_lab run --config experiments/configs/EXP-00N.json`); the protocol text is not edited (G-FREEZE), the difference is listed as an editorial amendment proposal.

## D-007: Popularity tie key is global per round by default (2026-11-24)
- **Decision:** the protocol's "seeded random key" for popularity ties is implemented as one uniform draw per candidate per round, shared by all viewers (`popularity_tie_scope = "global"`). A per-viewer variant (`"viewer"`) is implemented for comparison. Both key sets are drawn every round so the choice does not shift other streams.
- **Made by:** the M2 session as an implementation reading of an underspecified protocol item. Not a protocol change.
- **Consequences:** exploratory runs (J-0003, J-0005) show that this choice materially changes the POPULARITY arm. The owner must choose before the freeze (amendment proposal A1 in `progress.md`).

## D-008: Runtime is never measured under tracemalloc (2026-11-24)
- **Decision:** `runtime_s` is timed without tracing. Peak memory (`peak_traced_bytes`) is measured on a deterministic re-run of the first instance of each (cell, setting, arm), which also checks that the re-run reproduces the metrics (a mismatch is recorded as a run failure). Process peak RSS is recorded in the run manifest.
- **Rationale:** measured on one n_A = 200 market: sequential runs took 0.24 to 0.45 s untraced and 2.4 to 3.7 s under tracemalloc.

## D-009: Exploratory root seeds 101, 202, 303, 404 are used (2026-11-24)
- **Decision:** the exploratory smoke, pilot, pilot-S and tie-key probe use root seeds 101, 202, 303 and 404 (recorded in `data/manifest.json`). The confirmatory root seed chosen at the freeze must differ from these.

## D-010: Amendment proposals from the exploratory pilot are recorded, not adopted (2026-11-24)
- **Decision:** the pilot measurements (J-0002 to J-0006) lead to proposals A1 to A6 in `progress.md` (M2 entry). None is applied to `research/protocol.md` or the EXP protocols; the analysis plan is unchanged. Adoption is the owner's decision at the freeze (G-FREEZE).
