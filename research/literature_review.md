<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# Literature and dataset review (M0, initial)

Access date for every entry: 2026-11-24. This is an initial, non-systematic search (WebSearch and WebFetch), not a systematic review. "Verified" states exactly what was opened. Nothing is cited as read beyond what is stated.

## 1. Sources

| Key | Reference | What was opened | Verification level | Use in MATCH |
|---|---|---|---|---|
| gale1962 | D. Gale, L. S. Shapley. College Admissions and the Stability of Marriage. *The American Mathematical Monthly* 69(1):9-15, 1962. DOI 10.1080/00029890.1962.11989827 | Crossref metadata (api.crossref.org). Publisher page returned HTTP 403. | Metadata verified; full text not read | Deferred acceptance algorithm and stability definition (standard textbook content, implemented from the definition and checked by tests) |
| roth1982 | A. E. Roth. The Economics of Matching: Stability and Incentives. *Mathematics of Operations Research* 7(4):617-628, 1982. DOI 10.1287/moor.7.4.617 | Crossref metadata | Metadata verified; full text not read | Background on stability and proposer optimality; any specific statement attributed to it must be checked against the full text before the manuscript |
| ashlagi2017 | I. Ashlagi, Y. Kanoria, J. D. Leshno. Unbalanced Random Matching Markets: The Stark Effect of Competition. *Journal of Political Economy* 125(1):69-98, 2017. DOI 10.1086/689869 | EconPapers record with abstract (econpapers.repec.org/RePEc:ucp:jpolec:doi:10.1086/689869) | Abstract verified | Motivates varying imbalance r: per the abstract, with random preferences even slight imbalance gives an essentially unique stable matching; short-side agents get top choices and long-side agents do little better than random |
| kanoria2021 | Y. Kanoria, D. Saban. Facilitating the Search for Partners on Matching Platforms. *Management Science* 67(10):5990-6029, 2021. DOI 10.1287/mnsc.2020.3794 | EconPapers record with abstract (econpapers.repec.org/RePEc:inm:ormnsc:v:67:y:2021:i:10:p:5990-6029) | Abstract verified | Platform design restricting search actions; costly search in unbalanced markets; supports distinguishing sequential discovery from centralized matching |
| hitsch2010 | G. J. Hitsch, A. Hortacsu, D. Ariely. Matching and Sorting in Online Dating. *American Economic Review* 100(1):130-163, 2010. DOI 10.1257/aer.100.1.130 | EconPapers record with abstract | Abstract verified | Empirical use of Gale and Shapley as a model of matching outcomes; search frictions as a possible explanation for discrepancies. MATCH makes no empirical claim about any platform |
| singh2018 | A. Singh, T. Joachims. Fairness of Exposure in Rankings. *Proc. 24th ACM SIGKDD*, 2219-2228, 2018. DOI 10.1145/3219819.3220088; arXiv:1802.07281 | arXiv abstract page; Crossref metadata | Abstract verified | Exposure as the quantity allocated by a ranking; fairness constraints on exposure. Motivates the EXPOSURE_BALANCED policy and exposure Gini |
| su2021 | Y. Su, M. Bayoumi, T. Joachims. Optimizing Rankings for Recommendation in Matching Markets. arXiv:2106.01941, 2021 | arXiv abstract page | Abstract verified; preprint (the abstract page did not name a peer-reviewed venue) | Ranking by local relevance scores is argued suboptimal in matching markets with capacity constraints; closest prior framing of MATCH's popularity versus balanced comparison |
| tomita2024 | Y. Tomita, T. Yokoyama. Fair Reciprocal Recommendation in Matching Markets. arXiv:2409.00720, 2024 (comments field: accepted at RecSys 2024) | arXiv abstract page | Abstract verified | Envy-freeness of recommendation opportunities in reciprocal recommendation; trade-off between expected matches and fairness on both sides |

Search results seen but not opened (unverified, not cited): Tomita and Yokoyama arXiv:2601.13609 (Nash social welfare follow-up); arXiv:2508.01867 (counterfactual reciprocal recommenders); arXiv:2507.01063 (FAIR-MATCH); Kanoria, Min and Qian on partial preferences (arXiv:2402.09667 or related); Brozovsky and Petricek 2007 (libimseti ratings).

## 2. Known work and narrow contribution (draft)

Known: stable matching theory and its imbalance results (gale1962, roth1982, ashlagi2017); platform search design (kanoria2021); exposure fairness in rankings (singh2018); welfare-aware and fair reciprocal ranking in matching markets (su2021, tomita2024).

Proposed narrow contribution (to be re-checked against a deeper search in M1 before any novelty statement): a small, fully reproducible, open simulation that places three simple, interpretable slate policies and three centralized mechanisms on the same synthetic markets, varies imbalance and preference correlation jointly, and reports welfare, unmatched fraction, exposure inequality, blocking pairs and subgroup outcomes with paired, instance-level uncertainty and a pre-registered sensitivity analysis. No novelty is claimed at M0.

## 3. Datasets considered

The research design is fully synthetic (master prompt section 10 and its claims boundary: no real profiles). Real datasets were examined only to record why they are not used.

| Dataset | Source checked | Licence found | Redistributable? | Decision |
|---|---|---|---|---|
| Speed Dating (Fisman, Iyengar et al., events 2002-2004), OpenML id 40536 | OpenML API record (openml.org/api/v1/json/data/40536), accessed 2026-11-24 | OpenML licence field: "Public". No explicit licence text found; the Columbia-hosted origin page (statmodeling.stat.columbia.edu blog post) returned HTTP 403 | Unclear | Not used. Contains responses from real people; outside the claims boundary. Any future use is an owner decision (rights unclear) |
| libimseti.cz ratings (Brozovsky and Petricek 2007) | Only a search-result summary of a survey (arXiv:2202.01711); no download page or licence found | Unknown | Unknown | Not used; rights unclear |
| Hitsch et al. replication data (openICPSR 112322) | Search result only, not opened | Unknown (not checked) | Unknown | Not used |

No dataset was downloaded. The only data in this project will be generated by the synthetic generator (version, parameters and seeds recorded in `data/manifest.json` and per run).

## M6 full-text check (2026-11-25)

In M6 a free, legal full text was sought for every source that a claim depends on. No paid access, login or shadow library was used. Each cited claim was checked against the passage named below; the remaining parts of each paper were not reviewed in depth.

| Key | Full text opened (2026-11-25) | Passage checked | Outcome |
|---|---|---|---|
| ashlagi2017 | JPE article PDF hosted on the second author's page (ykanoria.github.io/Unequalmatch-JPE.pdf) | Abstract, p. 69; introduction, pp. 69 to 71 | Claim X-003 confirmed: "even the slightest imbalance yields an essentially unique stable matching"; short-side agents matched with one of their top choices |
| kanoria2021 | Author's accepted version (SSRN 3004814), PDF hosted by Columbia Business School | Abstract, p. 1 | Claim X-004 confirmed: the platform can mitigate wasted search effort by imposing restrictions on agents, in a dynamic search model with costly screening |
| hitsch2010 | AER article PDF in the Duke University repository (DukeSpace) | Abstract, p. 130 | Claim X-005 corrected: predicted stable matches are similar to the matches achieved on the site; search frictions "may play a role" in explaining correlation patterns that the predictions underpredict in offline marriages. The earlier wording ("discrepancies" between online matches and predictions) was imprecise and was changed in the manuscript and the EXP-002 report (D-030) |
| singh2018 | arXiv:1802.07281 | Abstract; section 1 ("the scarce resource that ranking systems allocate is the exposure of items to users") | Claim X-006 confirmed |
| su2021 | arXiv:2106.01941 | Abstract; section 4, Theorem 2 | Claim X-007 confirmed. The abstract names "some local score (e.g., one-sided or reciprocal relevance)" and section 4 analyses "PRP policies that rank based on one-sided relevances", so both the manuscript wording ("local relevance") and the EXP-001 wording ("one-sided relevance") match the paper. The setting is candidates applying to employers. Still a preprint: no peer-reviewed venue is named in the full text |
| tomita2024 | arXiv:2409.00720 | Abstract; ACM reference format on p. 1 | Claim X-008 confirmed. The paper's reference format names the 18th ACM Conference on Recommender Systems (RecSys '24), DOI 10.1145/3640457.3688130. The second author's given name is Tomohiko; `references.bib` was corrected |
| gale1962 | Not opened: no free, legal full text was found in this session | none | Stays metadata verified; claim X-001 rests on the standard definition and the project's tests |
| roth1982 | Not opened: no free, legal full text was found in this session | none | Stays metadata verified; claim X-002 is standard background |
