<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Owner review (checklist)

To be completed by the owner before any publication. Claude does not tick these boxes.

- [ ] Authorship and affiliation metadata approved (no invented affiliation, funding or endorsement).
- [ ] Protocols frozen by the owner before confirmatory runs (hashes in the decision log).
- [ ] AI assistance disclosure accurate (actual AI role, human verification performed).
- [ ] Licence statement correct (custom non-commercial source-available licence, not open source).
- [ ] Claims audit and reproducibility report reviewed.
- [ ] Manuscript status stated as independent preprint draft, not peer-reviewed.
- [ ] Publication target, eligibility and fees verified (paid venues out of scope).
- [ ] Explicit approval to push or publish recorded.

No box above was ticked by an agent as of M6 (2026-11-25); nothing had to be unticked.

## Prepared for the owner (M6, 2026-11-25)

The M6 session prepared a release candidate. At M6 nothing had been pushed; since 2026-11-25 the repository is public at https://github.com/mohamedbechirkefi/match-fairness-exposure (M6 commit included). Nothing is tagged, released or published as a release. For each box above, what to read:

1. **Authorship and affiliation metadata.** Read `research/paper/manuscript.md` section "Author and affiliation metadata" (line 10), the "Author" row of each `research/experiments/EXP-00N/report.md` (line 12), `CITATION.cff` (`authors`, line 11) and `pyproject.toml` (`authors`, line 9). The manuscript line reads "Mohamed Bechir Kefi. Independent researcher; no institutional affiliation", the form the owner chose on 2026-11-26 (B3); the reports read "Mohamed Bechir Kefi, independent researcher" and `CITATION.cff` carries `affiliation: "Independent researcher"`.
2. **Protocols frozen by the owner.** Read `research/freeze.json` and `research/decision_log.md` (the freeze entries and D-017 to D-019).
3. **AI assistance disclosure.** Read manuscript section 11 and the author metadata paragraph, and the "Author" rows of the three reports.
4. **Licence statement.** Read `README.md` section "Licence", `LICENSE`, `NOTICE.md` and `research/publication/dependency_licences.md` (flag 1).
5. **Claims audit and reproducibility report.** Read `research/publication/claims_audit.md`, `research/publication/evidence_audit.md` (section 6, the M6 addendum) and `research/publication/reproducibility_report.md`.
6. **Manuscript status.** Read the "Status" line at the top of `research/paper/manuscript.md`, and the PDF `research/paper/manuscript.pdf`.
7. **Publication target, eligibility and fees.** No target has been chosen; nothing has been checked.
8. **Approval to push or publish.** The owner approved the push of 2026-11-25 and, on 2026-11-26, the Cloudflare Workers hosting of the demo (B2, G-PUBLIC granted for that deploy). No approval of a release, tag, DOI, preprint or article posting is recorded.

## Owner answers recorded (2026-11-26)

Source: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md`, answers in `labs/_shared/owner-approvals-2026-11-26.md`). Applied in decision D-032. No box above was ticked.

- **A1.** The out-of-date "nothing pushed" sentences were corrected in this file, `release_checklist.md`, `reproducibility_report.md` and `README.md`. Append-only records (`progress.md`, `research/decision_log.md`, `research/experiment_journal.jsonl`) were not edited.
- **B1.** Repository URL https://github.com/mohamedbechirkefi/match-fairness-exposure filled in the manuscript (section 10), README, `demo/README.md`, the demo footer, both articles, and `CITATION.cff` (`repository-code`).
- **B2.** Demo URL https://match-fairness-exposure.kefimohamedbechir.workers.dev filled in the manuscript (section 10), README, `demo/README.md` and both articles; `demo/wrangler.jsonc` added (assets only, directory `./dist`); the deploy is the coordinator's.
- **B3.** Author line: "Mohamed Bechir Kefi. Independent researcher; no institutional affiliation" in the manuscript (unchanged, the form the owner chose); "Mohamed Bechir Kefi, independent researcher" in the three reports, README, `demo/README.md`, the demo footer and `articles/medium.md`; `CITATION.cff` `affiliation: "Independent researcher"`. `pyproject.toml` lists the name only (the field has no affiliation). Frozen protocols not edited.
- **B4.** Funding "No funding was received." and "The author declares no competing interests." were already in manuscript section 11; no "to be confirmed" mark existed.
- **B6, B7.** Title already approved (D-024) and already the `CITATION.cff` title; the old-title comment in `CITATION.cff` removed.
- **B8.** `0.1.0-rc1` and no `date-released` kept; the release step is recorded in `release_checklist.md`.
- **B9.** Home paths scrubbed from `CLAUDE.md` and `research/feasibility.md`; the remaining 8 lines in 4 files are listed in `reproducibility_report.md`, section 6.
- **B10, B11, B13.** PDFs kept; the truncated FIG-EXP-003-theta-forest labels and the external build tools are stated in the "Release notes (draft)" of `release_checklist.md`.
- **B14.** The source labels (Gale and Shapley 1962 and Roth 1982, metadata level only) are accepted as stated in the manuscript.
- **R-MATCH-1.** The M6 correction of the Hitsch, Hortacsu and Ariely (2010) paraphrase (D-030) is accepted.

Still open, each the owner's:

- **B15.** Read and approve `articles/medium.md` and `articles/linkedin.md` and their titles before any posting.
- **B16.** The owner's full-text review of the manuscript, the supplementary file and the three reports, then the sign-off of the checklist above.
- **B18.** Release: GitHub release with the PDFs attached, tag, and optionally a zero-cost DOI or preprint; publication target, eligibility and fees (box 7) not checked.
- **Freezes.** None pending in this repository (EXP-001 to EXP-003 frozen 2026-11-24); any new experiment needs its own freeze.

Remaining owner placeholders (file and line):

- None in the text files. `docs/demo.png` (README screenshot, made at M5) shows only the overview and results section; it carries no footer text, so it needs no change.
