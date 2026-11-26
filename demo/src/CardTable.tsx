// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Hero illustration: two decks dealt into facing rows (side A above, side B
// below, higher latent quality to the left), one viewer on side A and the
// slate of five side-B cards it is shown. Under "Popularity" the slate is the
// same five leftmost cards and the spotlight pools on them; under "Balanced
// exposure" the slate spreads along the row. This is a drawing of the
// mechanism, not study data: no number on it comes from a run.
import { useEffect, useState } from "react";

type Policy = "popularity" | "balanced";

const N = 9;
const VIEWER = 3;
const SLATE: Record<Policy, number[]> = {
  popularity: [0, 1, 2, 3, 4],
  balanced: [0, 2, 4, 6, 8],
};
// Exposure tallies drawn as gold pips under side-B cards (illustrative shape only).
const TALLY: Record<Policy, number[]> = {
  popularity: [4, 4, 4, 4, 4, 0, 0, 0, 0],
  balanced: [3, 2, 3, 2, 2, 2, 2, 2, 2],
};

export function CardTable() {
  const [policy, setPolicy] = useState<Policy>("popularity");
  const [dealt, setDealt] = useState(false);

  useEffect(() => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const t = window.setTimeout(() => setDealt(true), reduce ? 0 : 980);
    return () => window.clearTimeout(t);
  }, []);

  const slate = new Set(SLATE[policy]);
  return (
    <figure className="table-figure">
      <div className={`card-table policy-${policy}${dealt ? " is-dealt" : ""}`} aria-hidden="true">
        <span className="row-label row-label-a">Side A</span>
        <div className="deck-row row-a">
          {Array.from({ length: N }, (_, i) => (
            <div key={i} className="slot slot-a" style={{ animationDelay: `${i * 45}ms` }}>
              <div className={`pcard pcard-a${i === VIEWER ? " is-viewer" : ""}`}>
                <span className="pcard-suit suit-a" />
              </div>
            </div>
          ))}
        </div>
        <div className="spot-lane" />
        <div className="deck-row row-b">
          <span className="spotlight" />
          {Array.from({ length: N }, (_, i) => (
            <div key={i} className="slot slot-b" style={{ animationDelay: `${(N - 1 - i) * 45 + 90}ms` }}>
              <div className={`pcard pcard-b${slate.has(i) ? " in-slate" : ""}`} style={{ transitionDelay: dealt ? `${SLATE[policy].indexOf(i) >= 0 ? SLATE[policy].indexOf(i) * 40 : 0}ms` : "0ms" }}>
                <span className="pcard-suit suit-b" />
              </div>
              <span className="tally">
                {Array.from({ length: 4 }, (_, k) => (
                  <span key={k} className={k < TALLY[policy][i] ? "pip on" : "pip"} />
                ))}
              </span>
            </div>
          ))}
        </div>
        <span className="row-label row-label-b">Side B</span>
        <span className="quality-axis">Higher latent quality to the left</span>
      </div>
      <div className="table-controls">
        <div className="segmented" role="group" aria-label="Slate policy shown in the illustration">
          <span className={`seg-indicator at-${policy}`} aria-hidden="true" />
          <button type="button" aria-pressed={policy === "popularity"} onClick={() => setPolicy("popularity")}>
            Popularity
          </button>
          <button type="button" aria-pressed={policy === "balanced"} onClick={() => setPolicy("balanced")}>
            Balanced exposure
          </button>
        </div>
      </div>
      <figcaption>
        <span className="illus-tag">Illustration, not study data.</span>{" "}
        {policy === "popularity"
          ? "Ranked by popularity, slates keep favouring the side-B cards that have been liked most, so attention piles up on them."
          : "Under an exposure cap, the slate spreads along side B, so attention is shared more evenly."}
      </figcaption>
    </figure>
  );
}
