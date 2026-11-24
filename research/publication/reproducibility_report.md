<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Reproducibility report (checklist)

Status at M0: nothing to reproduce yet. To be completed at M6 with actual command outputs.

- [ ] Clean clone into a separate directory.
- [ ] `uv sync --frozen` succeeds with the committed `uv.lock`.
- [ ] Full test suite runs; actual pass/fail counts recorded.
- [ ] Smoke reproduction matches committed smoke results within the documented tolerance.
- [ ] Reports and figures regenerate from raw results with one command.
- [ ] Demo builds offline.
- [ ] Data manifest checks: synthetic generator version, parameters, seeds; no external data bundled.
- [ ] Environment recorded: OS, CPU, Python and package versions, git revision.
