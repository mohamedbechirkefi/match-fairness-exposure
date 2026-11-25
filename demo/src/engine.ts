// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// TypeScript port of the MATCH research engine for the in-browser sandbox:
// market construction (src/match_lab/market.py), sequential discovery with the
// three slate policies (sequential.py, tie_scope "global" as frozen), deferred
// acceptance with A proposing (matching.py) and the metrics (metrics.py).
// The logic is a line-by-line port and is tested against a golden fixture from
// the Python engine (engine.test.ts). The random number generator is NOT
// numpy's: the sandbox draws its own numbers (mulberry32, Box-Muller), so a
// sandbox seed never reproduces a research seed. Everything here is synthetic.

export type Policy = "RANDOM" | "POPULARITY" | "EXPOSURE_BALANCED";
export const POLICIES: Policy[] = ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"];

export interface Market {
  nA: number;
  nB: number;
  qA: number[];
  qB: number[];
  satA: number[][]; // satA[i][j]: satisfaction of A-agent i with B-agent j, in [0, 1]
  satB: number[][];
  accA: boolean[][];
  accB: boolean[][];
}

/** Random numbers consumed by one round, with the shapes the Python engine draws. */
export interface RoundDraws {
  perm: number[]; // permutation of 0..nA+nB-1 (viewer order)
  randA: number[][]; // (nA, nB) RANDOM slate keys for A viewers
  randB: number[][]; // (nB, nA)
  tieA: number[]; // (nA) popularity tie key per A candidate (shared by all viewers)
  tieB: number[]; // (nB)
}

export interface SeqSettings {
  T: number;
  k: number;
  delta: number;
}

export interface SeqOutcome {
  matchA: number[];
  matchB: number[];
  exposureA: number[];
  exposureB: number[];
  nSlates: number;
  shortSlates: number;
  capShortSlates: number;
  matchesByRound: number[];
}

export interface Metrics {
  W: number | null;
  W_A: number | null;
  W_B: number | null;
  U: number | null;
  M: number | null;
  n_matched: number;
  blocking_pairs: number;
  blocking_per_100: number | null;
  gini_exposure_A: number | null;
  gini_exposure_B: number | null;
}

// ---- market ------------------------------------------------------------------

export function sideSize(nA: number, r: number): number {
  return Math.floor(r * nA + 0.5);
}

/** Rank-percentile satisfaction per row; ties broken by the lower column index. */
export function satisfaction(u: number[][]): number[][] {
  return u.map((row) => {
    const m = row.length;
    if (m === 0) return [];
    if (m === 1) return [1];
    const order = row.map((_, j) => j).sort((a, b) => (row[b] - row[a]) || (a - b));
    const s = new Array<number>(m);
    order.forEach((j, idx) => {
      s[j] = 1.0 - idx / (m - 1); // rank - 1 = idx
    });
    return s;
  });
}

/** numpy.quantile(row, q, method="linear"), including numpy's two-sided lerp. */
export function quantileLinear(row: number[], q: number): number {
  const v = [...row].sort((a, b) => a - b);
  const n = v.length;
  const virt = (n - 1) * q;
  if (virt >= n - 1) return v[n - 1];
  if (virt < 0) return v[0];
  const prev = Math.floor(virt);
  const a = v[prev];
  const b = v[prev + 1];
  const t = virt - prev;
  const diff = b - a;
  return t >= 0.5 ? b - diff * (1 - t) : a + diff * t;
}

export function acceptability(u: number[][], theta: number): boolean[][] {
  return u.map((row) => {
    if (row.length === 0) return [];
    const tau = quantileLinear(row, theta);
    return row.map((x) => x >= tau);
  });
}

/** Build a market from qualities and idiosyncratic terms: u_ij = sqrt(rho) q_j + sqrt(1 - rho) e_ij. */
export function buildMarket(qA: number[], qB: number[], eA: number[][], eB: number[][], rho: number, theta: number): Market {
  const a = Math.sqrt(rho);
  const b = Math.sqrt(1.0 - rho);
  const uA = eA.map((row) => row.map((e, j) => a * qB[j] + b * e));
  const uB = eB.map((row) => row.map((e, i) => a * qA[i] + b * e));
  return {
    nA: qA.length,
    nB: qB.length,
    qA,
    qB,
    satA: satisfaction(uA),
    satB: satisfaction(uB),
    accA: acceptability(uA, theta),
    accB: acceptability(uB, theta),
  };
}

// ---- sequential discovery ----------------------------------------------------

export function exposureCap(k: number, delta: number, nViewers: number, nCandidates: number): number {
  if (nCandidates <= 0) return 0;
  return Math.ceil(((1.0 + delta) * k * nViewers) / nCandidates);
}

function select(policy: Policy, eligible: number[], k: number, randRow: number[], score: number[], tie: number[]): number[] {
  if (eligible.length === 0) return eligible;
  const pos = eligible.map((_, p) => p);
  if (policy === "RANDOM") {
    pos.sort((x, y) => (randRow[eligible[x]] - randRow[eligible[y]]) || (x - y));
  } else {
    pos.sort((x, y) => {
      const ex = eligible[x];
      const ey = eligible[y];
      return (-score[ex] - -score[ey]) || (tie[ex] - tie[ey]) || (x - y);
    });
  }
  return pos.slice(0, k).map((p) => eligible[p]);
}

const zeros = (n: number) => new Array<number>(n).fill(0);
const grid = <T>(n: number, m: number, v: T) => Array.from({ length: n }, () => new Array<T>(m).fill(v));

export function simulateSequential(market: Market, policy: Policy, s: SeqSettings, draws: (t: number) => RoundDraws): SeqOutcome {
  const n = [market.nA, market.nB];
  const acc = [market.accA, market.accB];
  const sat = [market.satA, market.satB];
  const seen = [grid(n[0], n[1], false), grid(n[1], n[0], false)];
  const like = [grid(n[0], n[1], false), grid(n[1], n[0], false)];
  const likes = [zeros(n[0]), zeros(n[1])];
  const exposure = [zeros(n[0]), zeros(n[1])];
  const match = [new Array<number>(n[0]).fill(-1), new Array<number>(n[1]).fill(-1)];
  const out: SeqOutcome = {
    matchA: match[0], matchB: match[1], exposureA: exposure[0], exposureB: exposure[1],
    nSlates: 0, shortSlates: 0, capShortSlates: 0, matchesByRound: [],
  };
  const k = s.k;
  for (let t = 0; t < s.T; t++) {
    const d = draws(t);
    const rand = [d.randA, d.randB];
    const tieKeys = [d.tieA, d.tieB];
    const unmatched = [match[0].map((x) => x < 0), match[1].map((x) => x < 0)];
    const count = (b: boolean[]) => b.reduce((acc0, x) => acc0 + (x ? 1 : 0), 0);
    const score = [0, 1].map((side) => likes[side].map((l, j) => (l + 1) / (exposure[side][j] + 2)));
    const cap = [
      exposureCap(k, s.delta, count(unmatched[0]), count(unmatched[1])),
      exposureCap(k, s.delta, count(unmatched[1]), count(unmatched[0])),
    ];
    const roundCount = [zeros(n[0]), zeros(n[1])];

    for (const v of d.perm) {
      const side = v < n[0] ? 0 : 1;
      const i = side === 0 ? v : v - n[0];
      const o = 1 - side;
      if (!unmatched[side][i]) continue;
      const base: number[] = [];
      for (let j = 0; j < n[o]; j++) if (unmatched[o][j] && !seen[side][i][j]) base.push(j);
      const eligible = policy === "EXPOSURE_BALANCED" ? base.filter((j) => roundCount[o][j] < cap[side]) : base;
      const chosen = select(policy, eligible, k, rand[side][i], score[o], tieKeys[o]);
      out.nSlates += 1;
      if (chosen.length < k) {
        out.shortSlates += 1;
        if (policy === "EXPOSURE_BALANCED" && chosen.length < Math.min(k, base.length)) out.capShortSlates += 1;
      }
      for (const j of chosen) {
        seen[side][i][j] = true;
        exposure[o][j] += 1;
        roundCount[o][j] += 1;
        if (acc[side][i][j]) {
          like[side][i][j] = true;
          likes[o][j] += 1;
        }
      }
    }

    // End-of-round greedy resolution of mutual likes among agents unmatched at the round start.
    const pairs: [number, number, number][] = [];
    for (let a = 0; a < n[0]; a++) {
      if (!unmatched[0][a]) continue;
      for (let b = 0; b < n[1]; b++) {
        if (unmatched[1][b] && like[0][a][b] && like[1][b][a]) pairs.push([a, b, sat[0][a][b] + sat[1][b][a]]);
      }
    }
    pairs.sort((x, y) => (y[2] - x[2]) || (x[0] - y[0]) || (x[1] - y[1]));
    let created = 0;
    for (const [a, b] of pairs) {
      if (match[0][a] < 0 && match[1][b] < 0) {
        match[0][a] = b;
        match[1][b] = a;
        created += 1;
      }
    }
    out.matchesByRound.push(created);
  }
  return out;
}

// ---- deferred acceptance (A proposing) ---------------------------------------

function preferenceLists(sat: number[][], acc: boolean[][]): number[][] {
  return sat.map((row, i) => {
    const idx: number[] = [];
    row.forEach((_, j) => {
      if (acc[i][j]) idx.push(j);
    });
    return idx.sort((x, y) => (row[y] - row[x]) || (x - y));
  });
}

export function deferredAcceptanceA(market: Market): { matchA: number[]; matchB: number[] } {
  const prefsP = preferenceLists(market.satA, market.accA);
  const prefsR = preferenceLists(market.satB, market.accB);
  const rankR = prefsR.map((lst) => new Map(lst.map((p, idx) => [p, idx])));
  const next = zeros(market.nA);
  const matchA = new Array<number>(market.nA).fill(-1);
  const matchB = new Array<number>(market.nB).fill(-1);
  const free: number[] = [...Array(market.nA).keys()];
  while (free.length > 0) {
    const p = free.shift() as number;
    const lst = prefsP[p];
    while (next[p] < lst.length) {
      const r = lst[next[p]];
      next[p] += 1;
      const rp = rankR[r].get(p);
      if (rp === undefined) continue;
      const cur = matchB[r];
      if (cur === -1) {
        matchB[r] = p;
        matchA[p] = r;
        break;
      }
      if (rp < (rankR[r].get(cur) as number)) {
        matchB[r] = p;
        matchA[p] = r;
        matchA[cur] = -1;
        free.push(cur);
        break;
      }
    }
  }
  return { matchA, matchB };
}

// ---- metrics -----------------------------------------------------------------

export function gini(x: number[]): number | null {
  if (x.length === 0) return null;
  const total = x.reduce((a, b) => a + b, 0);
  if (total === 0) return 0;
  const xs = [...x].sort((a, b) => a - b);
  const n = xs.length;
  let acc = 0;
  xs.forEach((v, idx) => {
    acc += (idx + 1) * v;
  });
  return (2.0 * acc) / (n * total) - (n + 1.0) / n;
}

const mean = (x: number[]) => (x.length ? x.reduce((a, b) => a + b, 0) / x.length : null);

export function computeMetrics(m: Market, matchA: number[], matchB: number[], exposureA?: number[], exposureB?: number[]): Metrics {
  const sA = matchA.map((j, i) => (j >= 0 ? m.satA[i][j] : 0));
  const sB = matchB.map((i, j) => (i >= 0 ? m.satB[j][i] : 0));
  const nTotal = m.nA + m.nB;
  const mutual: number[] = [];
  matchA.forEach((j, i) => {
    if (j >= 0) mutual.push(Math.min(m.satA[i][j], m.satB[j][i]));
  });
  const nMatched = mutual.length;
  const curA = matchA.map((j, i) => (j >= 0 ? m.satA[i][j] : -Infinity));
  const curB = matchB.map((i, j) => (i >= 0 ? m.satB[j][i] : -Infinity));
  let bp = 0;
  for (let i = 0; i < m.nA; i++) {
    for (let j = 0; j < m.nB; j++) {
      if (m.accA[i][j] && m.accB[j][i] && m.satA[i][j] > curA[i] && m.satB[j][i] > curB[j]) bp += 1;
    }
  }
  return {
    W: mean([...sA, ...sB]),
    W_A: mean(sA),
    W_B: mean(sB),
    U: nTotal ? (nTotal - 2 * nMatched) / nTotal : null,
    M: mean(mutual),
    n_matched: nMatched,
    blocking_pairs: bp,
    blocking_per_100: nTotal ? (100.0 * bp) / nTotal : null,
    gini_exposure_A: exposureA ? gini(exposureA) : null,
    gini_exposure_B: exposureB ? gini(exposureB) : null,
  };
}

// ---- sandbox random numbers (not numpy's) -------------------------------------

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(u: () => number): () => number {
  return () => {
    let x = u();
    while (x <= 0) x = u();
    return Math.sqrt(-2 * Math.log(x)) * Math.cos(2 * Math.PI * u());
  };
}

/** Four independent sandbox streams derived from one visitor seed. */
export function sandboxStreams(seed: number) {
  const root = mulberry32(seed);
  const sub = () => mulberry32(Math.floor(root() * 4294967296));
  return { market: sub(), order: sub(), keys: sub(), ties: sub() };
}

export function sandboxMarket(seed: number, nA: number, r: number, rho: number, theta: number): Market {
  const st = sandboxStreams(seed);
  const z = normal(st.market);
  const nB = sideSize(nA, r);
  const qA = Array.from({ length: nA }, z);
  const qB = Array.from({ length: nB }, z);
  const eA = Array.from({ length: nA }, () => Array.from({ length: nB }, z));
  const eB = Array.from({ length: nB }, () => Array.from({ length: nA }, z));
  return buildMarket(qA, qB, eA, eB, rho, theta);
}

/** Round draws for the sandbox: identical for every policy on the same seed (common random numbers). */
export function sandboxDraws(seed: number, nA: number, nB: number, T: number): RoundDraws[] {
  const st = sandboxStreams(seed);
  const out: RoundDraws[] = [];
  for (let t = 0; t < T; t++) {
    const perm = [...Array(nA + nB).keys()];
    for (let i = perm.length - 1; i > 0; i--) {
      const j = Math.floor(st.order() * (i + 1));
      [perm[i], perm[j]] = [perm[j], perm[i]];
    }
    out.push({
      perm,
      randA: Array.from({ length: nA }, () => Array.from({ length: nB }, st.keys)),
      randB: Array.from({ length: nB }, () => Array.from({ length: nA }, st.keys)),
      tieA: Array.from({ length: nA }, st.ties),
      tieB: Array.from({ length: nB }, st.ties),
    });
  }
  return out;
}
