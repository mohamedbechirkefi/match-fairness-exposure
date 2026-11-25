// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Bounded, cancellable sandbox: one small synthetic market, the three slate
// policies on identical draws (common random numbers) and deferred acceptance,
// all computed by the engine port in engine.ts. At most 30 agents per side and
// 12 rounds, so a run takes milliseconds; the cancel check runs between arms.
import { computeMetrics, deferredAcceptanceA, POLICIES, sandboxDraws, sandboxMarket, simulateSequential } from "./engine";
import { checkParams, SANDBOX_K, SANDBOX_N_A, type ArmResult, type SandboxParams, type WorkerReply, type WorkerRequest } from "./sandboxCore";

let cancelled = false;

async function run(p: SandboxParams): Promise<WorkerReply> {
  const bad = checkParams(p);
  if (bad) return { type: "error", message: bad };
  const market = sandboxMarket(p.seed, SANDBOX_N_A, p.r, p.rho, p.theta);
  const draws = sandboxDraws(p.seed, market.nA, market.nB, p.T);
  const arms: ArmResult[] = [];
  const mutualOf = (matchA: number[]) => matchA.map((j, i) => (j >= 0 ? Math.min(market.satA[i][j], market.satB[j][i]) : -1));
  for (const [idx, policy] of POLICIES.entries()) {
    await new Promise((r) => setTimeout(r, 0)); // let a cancel message in
    if (cancelled) return { type: "cancelled" };
    const out = simulateSequential(market, policy, { T: p.T, k: SANDBOX_K, delta: 0.5 }, (t) => draws[t]);
    let last: number | null = null;
    out.matchesByRound.forEach((c, t) => {
      if (c > 0) last = t + 1;
    });
    arms.push({
      arm: policy,
      matchA: out.matchA,
      mutual: mutualOf(out.matchA),
      exposureA: out.exposureA,
      exposureB: out.exposureB,
      metrics: computeMetrics(market, out.matchA, out.matchB, out.exposureA, out.exposureB),
      lastMatchRound: last,
    });
    postMessage({ type: "progress", fraction: (idx + 1) / 4 } satisfies WorkerReply);
  }
  const da = deferredAcceptanceA(market);
  arms.push({ arm: "DA_A", matchA: da.matchA, mutual: mutualOf(da.matchA), exposureA: null, exposureB: null, metrics: computeMetrics(market, da.matchA, da.matchB), lastMatchRound: null });
  return { type: "done", params: p, nB: market.nB, qA: market.qA, qB: market.qB, arms };
}

onmessage = async (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  cancelled = false;
  try {
    postMessage(await run(m.params));
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
