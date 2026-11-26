<!-- SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0 -->
# MATCH demo: design plan (owner request, 2026-11-26)

## Subject, audience, job

- **Subject.** Who sees whom in a two-sided market. Each round, every unmatched participant is dealt a slate of five candidates, chosen at random, by popularity, or by popularity under an exposure cap. The study measures what that choice does to mean welfare.
- **Audience.** A curious technical reader, an admissions committee skimming for rigour, a researcher checking the intervals.
- **Primary job.** State the question and the answer in one sentence, show the horizon reversal as a forest of contrasts, then let the visitor inspect the evidence and deal a small market of their own.

## Palette (light only)

The brand is a card table seen under a reading lamp: two decks in two inks, a gold spotlight. One scheme only, because the spotlight metaphor depends on a pale table; a dark variant would turn it into a stage.

| Name | Hex | Role |
| --- | --- | --- |
| Card stock | `#F4F2F8` | Page background, a cool lilac white (never cream) |
| Ink plum | `#231B33` | Text, wordmark, matched nodes |
| Cobalt deck | `#2F47B8` | Side A: card backs, side-A nodes, links |
| Mulberry deck | `#9C2F6E` | Side B: card backs, matching edges, focus ring |
| Spotlight gold | `#E0A21B` | Attention: the popularity spotlight, the logo pip, exposure tallies (never text) |
| Felt teal | `#11756A` | Balanced exposure: the EXPOSURE_BALANCED arm and its light |

Arm colours in charts keep shape coding (circle, triangle, square, diamond) so colour is never the only carrier: RANDOM slate `#5B6478`, POPULARITY dark gold `#9A6A00` (gold darkened for 3:1 marks on card stock), EXPOSURE_BALANCED felt teal, DA_A plum.

## Type

- **Young Serif** (display, 400): a soft, heavy old-style serif that reads like the index printed in the corner of a playing card. Headings, the wordmark, the hero question. Never below 20 px.
- **Outfit** (variable, 400 to 650): a geometric sans with round bowls and flat terminals, like the pips and indices of a modern card deck; its circles echo the side-A pip and it sits quietly beside the soft heavy serif. Body, controls, tables, chart labels, with tabular figures (`tnum`) for every number.

Outfit replaced Libre Franklin on 2026-11-26 (owner request: no two lab demos share a typeface). Its x-height is lower (0.46 em against about 0.53), so the body went from 17 to 18 px with line-height 1.58, chips, ticks and the quality axis from 0.78 to 0.8 rem up to 0.82 to 0.84 rem, chart axis text to 12.5 and 13.5 px, and tables to 15.5 px; headings and the wordmark are unchanged.

Scale (about 1.25 ratio from an 18 px body): 13.4 / 18 / 21 / 26.5 / 33 / 46 (hero, fluid). Body line length capped at 68 characters; serif headings at 22 characters per line or fewer in the hero.

## Layout

```
+--------------------------------------------------------------------+
| [mark] Match      Result  Evidence  Trade-off  Sandbox  Method      |  sticky, 56 px, blurred card stock
+--------------------------------------------------------------------+
| How do ranking and exposure   |   CARD TABLE (illustration)         |
| policies alter match          |   side A  [][][][][][][][][]        |
| outcomes ...?  (Young Serif)  |            ^ viewer card            |
|                               |   side B  [][][][][][][][][]        |
| Answer in one sentence.       |   spotlight over the slate of five  |
| Author line. Status badge.    |   (Popularity | Balanced exposure)  |
|                               |   "Illustration, not study data"    |
+--------------------------------------------------------------------+
| The horizon decides the sign: forest of POPULARITY - RANDOM         |
| (key picture), EXPOSURE_BALANCED forest beside it on wide screens   |
+--------------------------------------------------------------------+
| Evidence: three experiment "hands" (panels), M4 diagnostics,        |
| Table 3 forests                                                     |
+--------------------------------------------------------------------+
| Trade-off chart with cell selector                                  |
+--------------------------------------------------------------------+
| Sandbox: controls on a felt-edged tray, graph, table                |
+--------------------------------------------------------------------+
| Assumptions | Method and limitations | Reproduce                   |
+--------------------------------------------------------------------+
| footer: lockup, links, licence, AI use, font credits                |
+--------------------------------------------------------------------+
```

Left aligned throughout; the hero is a two-column split from 960 px, stacked below it with the table first after the question. Panels are not identical cards: experiment panels carry a coloured spine by status (measured, partial, exploratory), the sandbox sits in a tray with a dashed felt border, and the assumptions are a plain definition list.

## Motion

- **One orchestrated hero moment.** Two decks are dealt into facing rows (side A from the left, side B from the right, 45 ms stagger, 520 ms each, strong ease-out), then one viewer card on side A lifts and five side-B cards rise as its slate while the gold spotlight settles over them. The segmented control switches the illustration between *Popularity* (the slate is always the same five leftmost, highest-quality cards and the light pools on them; exposure tallies pile up on the left) and *Balanced exposure* (the slate spreads across the row and the light widens). Transform and opacity only; the indicator of the segmented control slides.
- **Motion that answers the visitor.** Forest dots and interval bars draw from the zero line once when scrolled into view (IntersectionObserver, once); the sandbox run button presses (scale 0.97, 120 ms) and the result line fades in; the trade-off markers ease to their new positions when the design cell changes (CSS transition on transform).
- **Reduced motion.** Cards appear in place with an opacity fade; the spotlight changes by cross-fade; chart reveals are opacity only; no transform animation anywhere.
- Hover motion only inside `(hover: hover) and (pointer: fine)`. No `transition: all`.

## The one memorable thing

The card table: the spotlight that pools on the same five cards under popularity and spreads under balanced exposure, which is the study's mechanism in one gesture.

## Review against the generated-page tells, and what changed

- The design-system search tool proposed a rose and coral palette for "matchmaking". It reads as a dating app template and as the cream-and-terracotta tell; replaced by cobalt and mulberry decks on a cool card stock, with gold reserved for attention.
- The old page had an uppercase tracked kicker above the title. Removed; the study and status move into the byline under the answer.
- Numbering the sections 01 to 06 was considered and dropped: they are not a sequence.
- Card-shaped panels everywhere would be the SaaS-card kit. Only the hero uses cards; evidence panels use a status spine and a flat surface, and radii differ by role (cards 10 px, panels 6 px, chips 999 px).
- No mono data labels: numbers use Outfit with tabular figures.
- No fade-up on every section: the only scroll-triggered motion is the chart reveal.
- Distinct from the other labs: no departure board (FARE), no ballots (PARADOX), no network map (VIRAL), no petri dish (EVOLVE); the deck-and-spotlight metaphor belongs to MATCH alone.
