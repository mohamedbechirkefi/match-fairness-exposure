<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# CLAUDE.md: how every session works in MATCH

MATCH is an independent research project on matching algorithms and fairness. Research question: *How do ranking and exposure policies alter match outcomes under heterogeneous preferences?* Everything is synthetic. `master_prompt.md` is the authority and is never edited.

## 1. Reading order (before modifying anything)

1. `master_prompt.md` (authority; sections 1 to 11).
2. `roadmap.md` (milestones, gates, status, blockers).
3. `progress.md` (append-only journal; read the last entry and its "next action").
4. `research/protocol.md` (current protocol status: DRAFT until the owner freezes it).
5. `research/claims_register.csv` (every claim made so far).
6. Then, as needed: `research/decision_log.md`, `research/experiment_registry.csv`, `research/experiments/EXP-NNN/protocol.md`, `research/limitations.md`, `data/manifest.json`.

If resuming, run `git status` first and inspect existing files. Never overwrite the owner's changes.

At the start of each session, state the current milestone and the next bounded task.

## 2. Mandatory requirements (master prompt section 11)

- **Publication tree (11.1).** Maintain `research/experiment_registry.csv`, `research/protocol.md`, `research/claims_register.csv`, `research/paper/` (manuscript.md canonical, manuscript.tex generated, references.bib, figures/, supplementary.md, manuscript.pdf only when actually built), `research/experiments/EXP-NNN/` (protocol.md, report.md, report.pdf when built, config.json, run_manifest.json, metrics.csv, figures/, reproduction.md) and `research/publication/` (artifact_manifest.json, claims_audit.md, reproducibility_report.md, author_review.md, release_checklist.md).
- **Stable identifiers.** EXP-NNN for experiments, RUN-ids for runs, FIG-ids for figures, C-ids for claims. A seed is a run, not a new experiment. A new question or a materially different protocol gets a new EXP id.
- **Before each experiment (11.2).** A complete `EXP-NNN/protocol.md` exists, covering every 11.2 item, including what result would contradict the hypothesis. Confirmatory runs only after the owner freezes it (hash recorded, approval recorded). Post-hoc changes are exploratory, dated and justified.
- **Reports (11.3).** Every registered experiment gets a standalone report with the 12 mandatory sections, including failed, null, abandoned and exploratory ones. Tables and figures are generated from actual outputs, never copied by hand.
- **Manuscript (11.4).** One integrated manuscript, 3,000 to 6,000 words where the evidence justifies it, with the required structure. Status: independent research manuscript / preprint draft, not peer-reviewed. No invented affiliation, funding, ethics approval or citations.
- **Evidence pipeline (11.5).** A local report-generation command; figures and tables generated once from versioned results and reused everywhere; a manifest mapping every number to experiment, run ids, metric, result path, generator, config/protocol hash and code revision. A second review pass challenges the preferred hypothesis.
- **Milestones (11.6).** M0/M1: registry, manuscript skeleton, per-experiment protocols, zero-cost toolchain confirmed, protocols frozen before execution. M2: output schemas, reproducibility manifests and report generators built alongside the core algorithms. M3: individual reports written as experiments finish; failures and deviations recorded; provenance captured at run time. M4: reports finished, evidence audit, manuscript synthesis with contradictory results and sensitivity. M5: demo, paper, reports and articles use identical verified results. M6: compile and inspect PDFs, verify references, reproduce smoke results in a clean clone, owner review checklist.
- **Publication gate.** Satisfied only when every registered experiment has a truthful standalone report, the manuscript is complete, all artifacts are traceable and blockers are disclosed. If time runs short, cut optional experiments or UI, never reporting or evidence controls.

## 3. Rules (all sessions)

### Gates
- **G-PUBLIC.** Never push, add a remote, create a GitHub repository or publish anything without the owner's explicit approval.
- **G-SPEND.** No paid service of any kind: no paid API, inference, dataset, cloud compute, hosting, domain, analytics or recruitment. The coding subscription is never an inference backend.
- **G-FREEZE.** Never freeze a protocol yourself. Freezing, and any later change to a frozen protocol, is the owner's decision.
- No confirmatory experiment before the owner freezes its protocol. Exploratory runs are allowed and must be labelled exploratory everywhere they appear.

### Scope
- Work only inside `/Users/bechir/research/labs/match-fairness-exposure/`.
- Read-only use of the shared tools: `/Users/bechir/research/labs/.tools/py/bin/` (uv, python with typst, pypdf, pillow), `/Users/bechir/research/labs/.tools/pandoc`, and Node at `/Users/bechir/research/helix/.tools/node/bin` (never modify that folder).
- Do not touch any other folder under `/Users/bechir/research` (hive, helix, cogkt, trading, the other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record commands and their actual outputs in `progress.md`.
- Anything not verified is labelled unverified. Cite only sources actually opened, with URL or DOI and access date.
- Simulated results are labelled as simulations. No claim about real people, real dating platforms or proprietary systems (claims boundary, master prompt section 10).

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0` as a comment where the format allows. JSON and CSV are covered by `NOTICE.md`.
- The licence is the owner's decision (decision D-001). Do not change `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`. Development commands may be appended to `CONTRIBUTING.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner" (they/them).
- Commits are local only, made with the owner's git identity as given in the session brief (passed with `git -c user.name=... -c user.email=...`; the address is not recorded in any file), with a message ending in a blank line and the Claude co-author trailer given in the session instructions. Run `git status` before and after.

## 4. Toolchain (zero cost, decision D-002)

- Python 3.12.1 (`/usr/local/bin/python3`), dependencies locked in `uv.lock` via `/Users/bechir/research/labs/.tools/py/bin/uv lock` (`exclude-newer` set two weeks before the lock date).
- No TeX distribution. PDFs: Markdown, then `pandoc -t typst`, then the `typst` Python package. `manuscript.tex` is generated from Markdown with pandoc and is not compiled locally.

## 5. Session end

Update `progress.md` (dated entry: decisions, commands, actual outputs, failures, changed files, risks, next action) and `roadmap.md` statuses. Append decisions to `research/decision_log.md`. Never mark incomplete work as done.
