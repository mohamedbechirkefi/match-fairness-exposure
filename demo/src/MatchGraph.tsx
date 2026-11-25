// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Population and matching graph for one sandbox market: side A on the top row,
// side B on the bottom row, each sorted by latent quality (highest on the left).
// A line joins each matched pair; its weight grows with the pair's mutual
// satisfaction. Filled nodes are matched, hollow nodes unmatched; for the
// sequential policies the node size grows with the agent's exposure (number of
// slates it appeared in). Hand-written SVG at the container's pixel width.
import { useWidth } from "./Tradeoff";

export interface GraphData {
  qA: number[];
  qB: number[];
  matchA: number[];
  mutual: number[]; // per A agent: min(s_ij, s_ji) of its pair, or -1
  exposureA: number[] | null;
  exposureB: number[] | null;
}

function order(q: number[]): number[] {
  return q.map((_, i) => i).sort((a, b) => q[b] - q[a] || a - b);
}

export function MatchGraph({ g, arm, desc }: { g: GraphData; arm: string; desc: string }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const height = 250;
  const m = { l: 14, r: 14 };
  const yA = 58;
  const yB = 200;
  const oA = order(g.qA);
  const oB = order(g.qB);
  const posA = new Map(oA.map((i, k) => [i, m.l + ((k + 0.5) / oA.length) * (width - m.l - m.r)]));
  const posB = new Map(oB.map((j, k) => [j, m.l + ((k + 0.5) / oB.length) * (width - m.l - m.r)]));
  const spacing = (width - m.l - m.r) / Math.max(oA.length, oB.length);
  const rMax = Math.max(3, Math.min(8, spacing * 0.34));
  const maxExp = Math.max(1, ...(g.exposureA ?? [1]), ...(g.exposureB ?? [1]));
  const rad = (e: number | undefined) => (e === undefined ? rMax * 0.8 : 2.2 + (rMax - 2.2) * Math.sqrt(e / maxExp));
  const matchedB = new Set(g.matchA.filter((j) => j >= 0));
  return (
    <div ref={ref} className="chart">
      <svg width={width} height={height} role="img" aria-labelledby="mg-t mg-d">
        <title id="mg-t">{`Sandbox population and matching graph, ${arm}`}</title>
        <desc id="mg-d">{desc}</desc>
        <text className="axis-label" x={m.l} y={20}>Side A, higher latent quality to the left</text>
        <text className="axis-label" x={m.l} y={height - 12}>Side B, higher latent quality to the left</text>
        {g.matchA.map((j, i) =>
          j < 0 ? null : (
            <line
              key={`e${i}`}
              className="edge"
              x1={posA.get(i)}
              y1={yA}
              x2={posB.get(j)}
              y2={yB}
              strokeWidth={0.8 + 3.2 * Math.max(0, g.mutual[i])}
            />
          ),
        )}
        {oA.map((i) => (
          <circle key={`a${i}`} className={g.matchA[i] >= 0 ? "node matched" : "node unmatched"} cx={posA.get(i)} cy={yA} r={rad(g.exposureA?.[i])} />
        ))}
        {oB.map((j) => (
          <circle key={`b${j}`} className={matchedB.has(j) ? "node matched side-b" : "node unmatched side-b"} cx={posB.get(j)} cy={yB} r={rad(g.exposureB?.[j])} />
        ))}
      </svg>
    </div>
  );
}
