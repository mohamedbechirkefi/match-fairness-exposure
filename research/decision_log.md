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
