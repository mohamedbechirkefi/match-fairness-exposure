<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
<!-- Draft for the owner (M5). Not published. Every number is copied from research/paper/manuscript.md v1.0 and checked by tests/test_demo_export.py. Publication is the owner's decision (G-PUBLIC). -->

# Showing people the popular profiles first: a simulation where the answer depends on how long everyone searches

*By Mohamed Bechir Kefi, independent researcher.*

*Draft. A summary of an independent research manuscript (preprint draft, not peer-reviewed). Everything below comes from a simulation of synthetic participants; nothing describes real people, real dating apps or any real platform.*

## The question

Apps that help people find partners, collaborators or counterparts rarely assign matches. They decide who sees whom, and people then choose among what they are shown. Attention is scarce and each person can match only once, so the rule that decides exposure can matter. This project asks a narrow version of that question: *how do ranking and exposure policies alter match outcomes under heterogeneous preferences?*

## The simulation

Two sides of synthetic agents (200 on the short side, with the other side 1.0 to 1.5 times larger) each rate everyone on the other side. Part of each rating is shared ("quality" everyone agrees on) and part is personal taste, with a preference correlation of 0, 0.5 or 0.9. Each round, every unmatched agent sees a slate of five candidates:

- **RANDOM** (the baseline): five candidates drawn at random;
- **POPULARITY**: the candidates liked most often so far;
- **EXPOSURE_BALANCED**: the same popularity order, with a cap on how often any candidate can be shown in a round.

When two agents have liked each other they match and leave. The outcome is mean agent welfare W, between 0 and 1: each agent's satisfaction with their partner (0 if unmatched), averaged over everyone. For comparison, the same markets are also matched centrally by deferred acceptance (the Gale and Shapley algorithm) and by a welfare-maximizing assignment.

The protocol, including the rule that would count the main result as fragile, was frozen by the owner before the confirmatory runs. The primary horizon of 40 rounds was chosen with pilot values already seen, and the manuscript says so.

## What happened

**At 40 rounds, popularity ranking helped.** Over nine market types and 270 paired market instances, POPULARITY raised mean welfare by +0.0219 (95% CI +0.0207 to +0.0231; Holm-adjusted p = 0.0002) compared with RANDOM.

**At shorter horizons it hurt badly.** The pre-registered sensitivity analysis reran the comparison at 10 and 20 rounds. The sign reversed: -0.4081 at 10 rounds and -0.2824 at 20 rounds, with intervals far from zero. Under the frozen rule, the popularity result is therefore reported as *not robust to the horizon*. Exploratory diagnostics added afterwards suggest why: popularity ranking forms matches slowly, and it was still forming matches at round 40 when random exposure had almost always stopped. One untested explanation is that viewers see nearly the same slates, so mutual likes form late.

**Exposure balancing changed nothing measurable.** EXPOSURE_BALANCED was equivalent to RANDOM within the pre-registered margin of 0.01 (estimate +0.0004, 90% CI -0.0005 to +0.0013). Its cap did not even make exposure more equal than random exposure in four of nine market types, so this is a result about one cap rule, not about exposure balancing as a goal.

**Centralized matching was far ahead.** Deferred acceptance exceeded random discovery by +0.0963 in welfare. The welfare-maximizing assignment reached higher welfare still, but left +231.06 more blocking pairs per 100 agents than deferred acceptance: pairs who would both rather be with each other.

## What was not done

A registered check of whether the conclusions depend on how welfare is defined (sensitivity setting S3) was **not run**: the stored outputs did not contain what it needed and the frozen text did not fully specify it. The owner recorded it as a documented failure rather than choosing its parameters after seeing the data. So the dependence of these results on the welfare definition is untested.

## Limits

This is a stylized model: Gaussian preferences, a fixed acceptability threshold, no strategy, messaging or fatigue, one market size. Intervals reflect only sampling variation between synthetic markets, not uncertainty about the model. Horizons mean something only relative to the rounds a participant needs to see the whole other side (40 to 60 here), so no number here transfers to real search durations.

## Explore it

An offline interactive page shows the published estimates with their intervals, the fairness and satisfaction trade-off per market type, and a small sandbox where you can generate a 20-agent market and watch the matching graph under each policy. The sandbox runs a port of the research engine in your browser and is labelled as sandbox output.

- Manuscript, experiment reports and code: https://github.com/mohamedbechirkefi/match-fairness-exposure
- Interactive page: https://match-fairness-exposure.kefimohamedbechir.workers.dev

*An AI system (Claude, Anthropic) assisted with code, analysis and drafting under the author's direction; it is not an author.*
