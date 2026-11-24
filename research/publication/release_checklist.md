<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Release checklist (M6)

- [ ] All registered experiments (EXP-001 to EXP-003) have a truthful standalone report, including failed or null ones.
- [ ] Integrated manuscript complete; PDF built locally (pandoc to Typst, typst package) and visually inspected; `manuscript.tex` regenerated.
- [ ] References verified; cross-links, equations and figure readability checked.
- [ ] README: question, status, experiment table, links to paper and reports, key verified results, limitations, one-command reproduction, citation.
- [ ] Articles (`articles/medium.md`, `articles/linkedin.md`) use identical verified results and labels.
- [ ] Demo: offline after load, keyboard usable, reduced motion, mobile layout, fails closed on malformed results.
- [ ] Secret, e-mail and personal-identifier scan of committed files.
- [ ] Licence headers present; third-party licences recorded.
- [ ] Large generated files not committed; regeneration scripts present.
- [ ] Owner review completed (`author_review.md`).
- [ ] No push or publication without the owner's explicit approval (G-PUBLIC).
