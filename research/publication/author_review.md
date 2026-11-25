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

The M6 session prepared a release candidate; nothing was pushed, tagged, released or published. For each box above, what to read:

1. **Authorship and affiliation metadata.** Read `research/paper/manuscript.md` section "Author and affiliation metadata" (line 10), the "Author" row of each `research/experiments/EXP-00N/report.md` (line 12), `CITATION.cff` (`authors`, line 11) and `pyproject.toml` (`authors`, line 9). The line reads "Mohamed Bechir Kefi. Independent researcher; no institutional affiliation", as recorded at the freeze (decision C3 in `research/freeze.json`); D-023 and D-028 leave its confirmation to the owner, and M6 did not change it.
2. **Protocols frozen by the owner.** Read `research/freeze.json` and `research/decision_log.md` (the freeze entries and D-017 to D-019).
3. **AI assistance disclosure.** Read manuscript section 11 and the author metadata paragraph, and the "Author" rows of the three reports.
4. **Licence statement.** Read `README.md` section "Licence", `LICENSE`, `NOTICE.md` and `research/publication/dependency_licences.md` (flag 1).
5. **Claims audit and reproducibility report.** Read `research/publication/claims_audit.md`, `research/publication/evidence_audit.md` (section 6, the M6 addendum) and `research/publication/reproducibility_report.md`.
6. **Manuscript status.** Read the "Status" line at the top of `research/paper/manuscript.md`, and the PDF `research/paper/manuscript.pdf`.
7. **Publication target, eligibility and fees.** No target has been chosen; nothing has been checked.
8. **Approval to push or publish.** No approval is recorded; G-PUBLIC applies.

Open decisions for this repository, each the owner's:

- Whether the author line "Mohamed Bechir Kefi. Independent researcher; no institutional affiliation" is confirmed as it stands (open between the freeze decision C3 and D-023/D-028; listed as open in `owner-approvals-2026-11-25e.md`).
- Whether the affiliation statement ("no institutional affiliation") is correct.
- Which public repository URL and which demo URL will replace the placeholders, once publication is approved.
- Whether the approved funding ("No funding was received") and competing-interest ("The author declares no competing interests") statements still hold at publication (approved as wording in D-024; the facts stay owner-only).
- Whether and when to push, tag or publish anything (G-PUBLIC), and whether to re-add `date-released` to `CITATION.cff` at that time (removed in M6 under the coordinator default of `owner-approvals-2026-11-25e.md`).
- Whether the `CITATION.cff` choices made in M6 are accepted: version "0.1.0-rc1" and the manuscript title as the citation title (D-031).
- Whether the M6 correction of the Hitsch, Hortacsu and Ariely (2010) paraphrase in manuscript section 2 and the EXP-002 report is accepted (D-030).
- Whether the 17 absolute home-directory paths that remain in `CLAUDE.md`, `research/feasibility.md`, `research/experiment_journal.jsonl` and the three confirmatory run logs may stay in a public repository (`research/publication/reproducibility_report.md`, section 5).
- Whether the bundled GCC runtime (GPL-3.0-or-later with the GCC runtime exception) and libquadmath (LGPL-2.1-or-later) in the numpy and scipy wheels need any statement (`research/publication/dependency_licences.md`, flag 1).
- Which publication target, if any, is chosen, after eligibility and fees are checked (paid venues are out of scope).
- The owner's full-text review of the manuscript, which has not happened yet.

Remaining owner placeholders (file and line):

- `research/paper/manuscript.md`, line 250: "public URL: to be added after the owner's approval" (also `research/paper/manuscript.tex`, the generated copy).
- `README.md`, line 6: "Repository and demo URL: to be added after the owner's approval."
- `demo/README.md`, line 30: "Repository and demo URL: to be added after the owner's approval."
- `demo/src/App.tsx`, lines 58 and 59: author and affiliation "owner confirmation pending in the M6 review checklist"; "Repository and demo URL: to be added after the owner's approval." (also visible in `docs/demo.png`).
- `articles/medium.md`, lines 46 and 47: repository URL and demo URL placeholders.
- `articles/linkedin.md`, line 12: repository URL and demo URL placeholders.
- The author line itself (item 1 above) awaits the owner's confirmation in the manuscript (line 10), the three reports (line 12), `CITATION.cff` (line 11) and `pyproject.toml` (line 9).
