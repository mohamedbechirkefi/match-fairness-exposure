<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
<!-- Draft for the owner (M5). Not published. Numbers copied from research/paper/manuscript.md v1.0 and checked by tests/test_demo_export.py. Publication is the owner's decision (G-PUBLIC). -->

Does showing people the most popular candidates first lead to better matches? In my simulation, it depends on how long everyone keeps searching.

I built a small, pre-registered simulation of synthetic two-sided markets (no real people, no real platform) and compared three ways of choosing which five candidates each participant sees per round: random, by popularity, and by popularity with an exposure cap.

One defensible finding: after 40 rounds, popularity ranking raised mean welfare by +0.0219 (95% CI +0.0207 to +0.0231) over random exposure, but the pre-registered sensitivity check reversed the sign at 10 and 20 rounds (-0.4081 and -0.2824). Under the rule I fixed in advance, the result is not robust to the horizon. The exposure cap was equivalent to random exposure within 0.01.

Caveat: this is a stylized simulation with one market size; a registered check of the welfare definition was not run, and the manuscript is a preprint draft, not peer-reviewed.

Manuscript, reports, code and an offline interactive page: repository URL to be added after the owner's approval; demo URL to be added after the owner's approval.

#simulation #matchingmarkets #reproducibility
