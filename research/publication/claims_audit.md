<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Claims audit (M4, 2026-11-25)

**Register.** `research/claims_register.csv` has 22 rows:
- 14 result claims (C-001 to C-014): 7 from frozen analyses, 3 secondary descriptive and 4 exploratory;
- 8 external claims (X-001 to X-008).

**Supporting evidence.** The numbers were checked in `research/publication/evidence_audit.md`, and the challenge to the preferred reading is in `review_pass_2.md`.

- [x] Every row has a type, a result id or source, an evidence path, a config hash (or "n/a" for external claims), a figure or table, a manuscript section, a scope, a status and limitations.
- [x] Every numerical claim maps to an experiment ID, run IDs, a config hash and a figure or table in `artifact_manifest.json` (entries C-001 to C-014, FIG-*, TAB-*).
- [x] Every number in the reports, the manuscript, the supplementary file and the register matches the raw outputs at its printed precision (automated trace: 0 untraced decimals; independent recomputation of the headline estimates). The demo and the articles do not exist yet (M5).
- [x] Every external claim maps to a source actually opened, with its verification level: metadata only for X-001 and X-002, abstract only for X-003 to X-008. One paraphrase (Su et al. 2021, "one-sided relevance" in the EXP-001 report) is flagged for an M6 recheck.
- [x] No causal or universal claim beyond the synthetic model and no claim about real people or platforms. Mechanisms are labelled as model-dependent inferences.
- [x] Exploratory results (C-010 to C-013) are labelled exploratory in the register, the manuscript and the supplementary file, and none changes a frozen verdict.
- [x] The second review pass challenging the preferred reading is completed and recorded (`review_pass_2.md`). Its accepted challenges are applied in manuscript v1.0.
- [x] Unsupported claims removed or qualified:
  - removed: "rather than in the number of agents eventually matched";
  - qualified: the common-order sweep is now presented as a hypothesis;
  - qualified: the matched-agent satisfaction gain may include composition;
  - qualified: the EXPOSURE_BALANCED equivalence holds only for this cap rule;
  - qualified: the confirmatory p-value is valid only for the fixed-horizon contrast.

## Strength and scope of evidence per conclusion

| Conclusion | Strength | Scope |
|---|---|---|
| C-001 POPULARITY raises W at T = 40 | confirmatory, Holm p at the test's floor; **not robust** (frozen S2 criterion met) | this model, n_A = 200, k = 5, shared tie key, T = 40, equal-weight 9 cells |
| C-002 EXPOSURE_BALANCED equivalent to RANDOM at margin 0.01 | confirmatory equivalence (90% CI inside the margin); not invalidated by S1 or S2; S3 not run | this cap rule (delta = 0.5) in this model |
| C-003, C-004 centralized references | secondary, no multiplicity protection, very large effects relative to their CIs | full-information references in this model |
| C-005 to C-007 sensitivity | registered sensitivity, no multiplicity correction | corner cells only |
| C-008, C-009, C-014 descriptive | descriptive, unadjusted | per cell |
| C-010 to C-013 diagnostics | exploratory, post hoc; hypothesis-generating | C-011 is one new seed with 10 instances per cell |
