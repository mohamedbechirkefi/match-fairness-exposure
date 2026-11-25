// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Differential test: the TypeScript port against the Python engine (match_lab)
// on a golden fixture written by scripts/make_sandbox_fixture.py. The port gets
// the Python engine's exact inputs and random draws. Tolerance: matchings,
// exposures, slate counts, per-round match counts, acceptability and blocking
// pairs must be identical; real-valued quantities (satisfaction and metrics)
// must agree within an absolute 1e-12 (summation order may differ from numpy's).
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  buildMarket, computeMetrics, deferredAcceptanceA, POLICIES, sandboxDraws, sandboxMarket, simulateSequential,
  type Metrics, type RoundDraws,
} from "./engine";

const TOL = 1e-12;
const fixture = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8"));

function expectClose(actual: Metrics, expected: Record<string, number | null>) {
  for (const [key, want] of Object.entries(expected)) {
    const got = actual[key as keyof Metrics];
    if (want === null) {
      expect(got, key).toBeNull();
    } else {
      expect(got, key).not.toBeNull();
      expect(Math.abs((got as number) - want), key).toBeLessThanOrEqual(TOL);
    }
  }
}

describe.each(fixture.cases.map((c: { case: { name: string } }) => [c.case.name, c]))("port vs Python engine: %s", (_name, c) => {
  const p = c.case;
  const market = buildMarket(c.q_a, c.q_b, c.e_a, c.e_b, p.rho, p.theta);
  const draws = (t: number): RoundDraws => {
    const d = c.rounds[t];
    return { perm: d.perm, randA: d.rand_a, randB: d.rand_b, tieA: d.tie_a, tieB: d.tie_b };
  };

  it("builds the same satisfaction and acceptability", () => {
    expect(market.nB).toBe(c.n_b);
    market.satA.forEach((row, i) => row.forEach((v, j) => expect(Math.abs(v - c.sat_a[i][j])).toBeLessThanOrEqual(TOL)));
    market.satB.forEach((row, i) => row.forEach((v, j) => expect(Math.abs(v - c.sat_b[i][j])).toBeLessThanOrEqual(TOL)));
    expect(market.accA.map((r) => r.map(Number))).toEqual(c.acc_a);
    expect(market.accB.map((r) => r.map(Number))).toEqual(c.acc_b);
  });

  it.each(POLICIES)("reproduces the %s outcome exactly", (policy) => {
    const want = c.outcomes[policy];
    const out = simulateSequential(market, policy, { T: p.T, k: p.k, delta: 0.5 }, draws);
    expect(out.matchA).toEqual(want.match_a);
    expect(out.matchB).toEqual(want.match_b);
    expect(out.exposureA).toEqual(want.exposure_a);
    expect(out.exposureB).toEqual(want.exposure_b);
    expect(out.nSlates).toBe(want.n_slates);
    expect(out.shortSlates).toBe(want.short_slates);
    expect(out.capShortSlates).toBe(want.cap_short_slates);
    expect(out.matchesByRound).toEqual(want.matches_by_round);
    expectClose(computeMetrics(market, out.matchA, out.matchB, out.exposureA, out.exposureB), want.metrics);
  });

  it("reproduces deferred acceptance (A proposing) and its zero blocking pairs", () => {
    const want = c.outcomes.DA_A;
    const da = deferredAcceptanceA(market);
    expect(da.matchA).toEqual(want.match_a);
    expect(da.matchB).toEqual(want.match_b);
    const m = computeMetrics(market, da.matchA, da.matchB);
    expectClose(m, want.metrics);
    expect(m.blocking_pairs).toBe(0);
  });
});

describe("sandbox generator", () => {
  it("is deterministic for a seed and differs across seeds", () => {
    const a = sandboxMarket(3, 10, 1.5, 0.5, 0.5);
    const b = sandboxMarket(3, 10, 1.5, 0.5, 0.5);
    const c = sandboxMarket(4, 10, 1.5, 0.5, 0.5);
    expect(a).toEqual(b);
    expect(a.qA).not.toEqual(c.qA);
    expect(a.nB).toBe(15);
  });
  it("gives valid capacity-one matchings for every policy", () => {
    const m = sandboxMarket(11, 20, 1.1, 0.9, 0.5);
    const d = sandboxDraws(11, m.nA, m.nB, 8);
    for (const policy of POLICIES) {
      const out = simulateSequential(m, policy, { T: 8, k: 5, delta: 0.5 }, (t) => d[t]);
      const partners = out.matchA.filter((j) => j >= 0);
      expect(new Set(partners).size).toBe(partners.length);
      out.matchA.forEach((j, i) => {
        if (j >= 0) {
          expect(out.matchB[j]).toBe(i);
          expect(m.accA[i][j] && m.accB[j][i]).toBe(true);
        }
      });
    }
  });
});
