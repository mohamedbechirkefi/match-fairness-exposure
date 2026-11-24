<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Claims audit (checklist)

Status at M0: the claims register is empty; nothing to audit.

- [ ] Every row of `research/claims_register.csv` has a type (observed, inferred, simulated, external), an evidence path or verified source, a scope and limitations.
- [ ] Every numerical claim maps to experiment ID, run IDs, config hash and a figure or table in `artifact_manifest.json`.
- [ ] Every number in reports, manuscript, demo and articles matches the raw outputs (denominators, units, precision, uncertainty, sample counts).
- [ ] Every external claim maps to a source actually opened, with the verification level stated.
- [ ] No causal or universal claim beyond the synthetic model; no claim about real people or platforms.
- [ ] Exploratory results are labelled exploratory everywhere.
- [ ] Second review pass challenging the preferred hypothesis completed and recorded.
- [ ] Unsupported claims removed or qualified.
