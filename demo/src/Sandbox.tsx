// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Visitor sandbox: a 20-agent synthetic market run in a Web Worker by the port
// of the research engine. Its output is labelled as sandbox output and never
// mixed with the published results. Nothing typed here leaves the page.
import { useCallback, useEffect, useRef, useState } from "react";
import { MatchGraph } from "./MatchGraph";
import { MAX_T, SANDBOX_K, SANDBOX_N_A, type ArmResult, type SandboxParams, type WorkerReply, type WorkerRequest } from "./sandboxCore";
import { Legend, TradeoffChart } from "./Tradeoff";

const DEFAULTS: SandboxParams = { seed: 1, r: 1.0, rho: 0.5, theta: 0.5, T: 4 };
const VIEWS = ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED", "DA_A"];

type Done = Extract<WorkerReply, { type: "done" }>;
const f3 = (x: number | null) => (x === null ? "undefined" : x.toFixed(3));

export function Sandbox() {
  const worker = useRef<Worker | null>(null);
  const [p, setP] = useState<SandboxParams>(DEFAULTS);
  const [view, setView] = useState("POPULARITY");
  const [running, setRunning] = useState(false);
  const [out, setOut] = useState<string>("");
  const [done, setDone] = useState<Done | null>(null);

  useEffect(() => {
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "done") {
        setDone(m);
        const q = m.params;
        const ws = m.arms.map((a) => `${a.arm} ${f3(a.metrics.W)}`).join(", ");
        setOut(`Sandbox output (seed ${q.seed}, r = ${q.r.toFixed(1)}, rho = ${q.rho}, theta = ${q.theta}, T = ${q.T}): mean welfare W ${ws}.`);
      }
      if (m.type === "error") setOut(`Sandbox run failed: ${m.message}`);
      if (m.type === "cancelled") setOut("Sandbox run cancelled.");
      if (m.type !== "progress") setRunning(false);
    };
    worker.current = w;
    w.postMessage({ type: "run", params: DEFAULTS } satisfies WorkerRequest);
    setRunning(true);
    return () => w.terminate();
  }, []);

  const run = useCallback((params: SandboxParams) => {
    setRunning(true);
    setOut("");
    worker.current?.postMessage({ type: "run", params } satisfies WorkerRequest);
  }, []);
  const cancel = () => worker.current?.postMessage({ type: "cancel" } satisfies WorkerRequest);
  const reset = () => {
    setP(DEFAULTS);
    setView("POPULARITY");
    run(DEFAULTS);
  };
  const set = <K extends keyof SandboxParams>(k: K, v: SandboxParams[K]) => setP((old) => ({ ...old, [k]: v }));

  const shown: ArmResult | undefined = done?.arms.find((a) => a.arm === view);
  const nB = done?.nB ?? 0;
  const seq = done?.arms.filter((a) => a.arm !== "DA_A") ?? [];

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <p className="label-row"><span className="badge badge-sandbox">Sandbox output</span></p>
      <h2 id="h-sandbox">Sandbox: deal your own market</h2>
      <p className="lede">A population and matching graph for a small synthetic market, computed in your browser.</p>
      <p className="note">
        Sandbox output is produced in your browser from your settings. It is not a research result and is not
        comparable to the published numbers above. The engine logic (market, slate policies, deferred acceptance,
        metrics) is a port of the Python research engine and reproduces it exactly on shared inputs (a test against
        a Python fixture); the random number generator is different, so a sandbox seed does not reproduce any
        research run. The market is much smaller than in the study: {SANDBOX_N_A} agents on side A, slates of{" "}
        {SANDBOX_K}, at most {MAX_T} rounds.
      </p>
      <p className="note">
        Horizons only mean something relative to the rounds a viewer needs to see the whole other side, n_B / k. In
        the study the primary horizon T = 40 equals n_B / k in the balanced cells; in this sandbox n_B / k is{" "}
        {Math.round((SANDBOX_N_A * 1.0) / SANDBOX_K)} at r = 1.0, and the default T = 4 matches it.
      </p>
      <form
        className="controls"
        onSubmit={(e) => {
          e.preventDefault();
          run(p);
        }}
      >
        <label>
          Seed
          <input id="sb-seed" type="number" min={1} max={1_000_000} step={1} value={p.seed} onChange={(e) => set("seed", Math.min(1_000_000, Math.max(1, Math.round(Number(e.target.value)) || 1)))} />
        </label>
        <label>
          Imbalance r
          <select id="sb-r" value={p.r} onChange={(e) => set("r", Number(e.target.value))}>
            <option value={1.0}>1.0</option>
            <option value={1.1}>1.1</option>
            <option value={1.5}>1.5</option>
          </select>
        </label>
        <label>
          Preference correlation rho
          <select id="sb-rho" value={p.rho} onChange={(e) => set("rho", Number(e.target.value))}>
            <option value={0}>0</option>
            <option value={0.5}>0.5</option>
            <option value={0.9}>0.9</option>
          </select>
        </label>
        <label>
          Pickiness theta
          <select id="sb-theta" value={p.theta} onChange={(e) => set("theta", Number(e.target.value))}>
            <option value={0.3}>0.3</option>
            <option value={0.5}>0.5</option>
            <option value={0.7}>0.7</option>
          </select>
        </label>
        <label>
          Rounds T
          <input id="sb-T" type="number" min={1} max={MAX_T} step={1} value={p.T} onChange={(e) => set("T", Math.min(MAX_T, Math.max(1, Math.round(Number(e.target.value)) || 1)))} />
        </label>
        <div className="buttons">
          <button type="submit" disabled={running}>Run sandbox</button>
          <button type="button" onClick={reset} disabled={running}>Reset</button>
          <button type="button" onClick={cancel} disabled={!running}>Cancel</button>
        </div>
      </form>
      <p aria-live="polite" className="sandbox-out">
        <span key={out} className="out-text">{out}</span>
      </p>

      {done && shown && (
        <>
          <div className="controls">
            <label>
              Matching shown in the graph
              <select id="sb-view" value={view} onChange={(e) => setView(e.target.value)}>
                {VIEWS.map((v) => (
                  <option key={v} value={v}>{v === "DA_A" ? "DA_A (centralized, full information)" : v}</option>
                ))}
              </select>
            </label>
          </div>
          <MatchGraph
            arm={view}
            g={{ qA: done.qA, qB: done.qB, matchA: shown.matchA, mutual: shown.mutual, exposureA: shown.exposureA, exposureB: shown.exposureB }}
            desc={`${view}: ${shown.metrics.n_matched} pairs matched out of ${SANDBOX_N_A} A agents and ${nB} B agents; ${SANDBOX_N_A + nB - 2 * shown.metrics.n_matched} agents unmatched. The table below lists the metrics.`}
          />
          <p className="meta">
            Lines: matched pairs, thicker for higher mutual satisfaction. Filled nodes: matched; hollow nodes:
            unmatched. {view === "DA_A" ? "DA_A uses no slates, so node size is constant." : "Node size grows with the agent's exposure (slates it appeared in)."}
          </p>
          <h3>Sandbox trade-off: welfare against exposure inequality</h3>
          <Legend arms={["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"]} />
          <TradeoffChart
            title="Sandbox trade-off"
            desc="Mean agent welfare W against the Gini coefficient of side-B exposure for the three slate policies on this sandbox market. Values are in the table below."
            xLabel="Gini of side-B exposure (lower: more equal)"
            yLabel="Mean agent welfare W"
            points={seq.map((a) => ({ key: a.arm, arm: a.arm, label: a.arm, x: a.metrics.gini_exposure_B ?? 0, y: a.metrics.W ?? 0 }))}
          />
          <div id="table-sandbox" className="table-scroll" role="region" aria-label="Sandbox metrics" tabIndex={0}>
            <table className="stack">
              <caption className="meta">Sandbox output for this market (one market, one seed: no uncertainty is estimated).</caption>
              <thead>
                <tr>
                  <th scope="col">Arm</th>
                  <th scope="col">W</th>
                  <th scope="col">Unmatched U</th>
                  <th scope="col">Mutual satisfaction M</th>
                  <th scope="col">Gini, side-B exposure</th>
                  <th scope="col">Blocking pairs per 100 agents</th>
                  <th scope="col">Last round with a new match</th>
                </tr>
              </thead>
              <tbody>
                {done.arms.map((a) => (
                  <tr key={a.arm}>
                    <th scope="row">{a.arm}</th>
                    <td data-label="W">{f3(a.metrics.W)}</td>
                    <td data-label="Unmatched U">{f3(a.metrics.U)}</td>
                    <td data-label="Mutual satisfaction M">{f3(a.metrics.M)}</td>
                    <td data-label="Gini, side-B exposure">{a.exposureB ? f3(a.metrics.gini_exposure_B) : "no slates"}</td>
                    <td data-label="Blocking pairs per 100 agents">{a.metrics.blocking_per_100 === null ? "undefined" : a.metrics.blocking_per_100.toFixed(2)}</td>
                    <td data-label="Last round with a new match">{a.arm === "DA_A" ? "not sequential" : a.lastMatchRound ?? "none"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}
