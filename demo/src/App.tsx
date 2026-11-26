// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
import { useEffect, useState } from "react";
import { Mark, Wordmark } from "./Brand";
import { CardTable } from "./CardTable";
import { Forest, type ForestRow } from "./Forest";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";
import { Legend, TradeoffChart } from "./Tradeoff";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="topbar">
        <div className="wrap topbar-inner">
          <a className="brand" href="#top" aria-label="Match, back to the top">
            <Mark size={30} />
            <Wordmark height={21} />
          </a>
          <nav aria-label="Sections">
            <a href="#key">Result</a>
            <a href="#results">Evidence</a>
            <a href="#tradeoff">Trade-off</a>
            <a href="#sandbox">Sandbox</a>
            <a href="#method">Method</a>
          </nav>
        </div>
      </header>
      <main id="main">
        <section id="top" className="hero" aria-labelledby="h-hero">
          <div className="wrap hero-grid">
            <div className="hero-copy">
              <h1 id="h-hero">How do ranking and exposure policies alter match outcomes under heterogeneous preferences?</h1>
              <p className="answer">
                Ranking by popularity raised mean welfare at the pre-registered horizon of 40 rounds, but the sign
                reversed at 10 and 20 rounds, so the result is not robust to the horizon. Popularity ranking under an
                exposure cap was equivalent to random exposure within a margin of 0.01.
              </p>
              <p className="byline">A pre-registered simulation of synthetic two-sided markets by Mohamed Bechir Kefi, independent researcher. Preprint draft, not peer-reviewed; every participant is simulated.</p>
              <div className="hero-links">
                <a className="btn btn-primary" href="#key">See the result</a>
                <a className="btn" href="#sandbox">Open the sandbox</a>
              </div>
            </div>
            <CardTable />
          </div>
        </section>
        <div className="wrap">
          {state.kind === "loading" && <p role="status">Loading the published results.</p>}
          {state.kind === "error" && (
            <div role="alert" className="panel error">
              <h2>Results unavailable</h2>
              <p>The published results file failed validation, so no numbers are shown.</p>
              <p><code>{state.message}</code></p>
            </div>
          )}
          {state.kind === "ready" && <Published r={state.results} />}
          <Sandbox />
          <section id="reproduce" aria-labelledby="h-reproduce">
            <h2 id="h-reproduce">Reproduce</h2>
            <p>
              Everything on this page is rebuilt from the repository. The study runs in Python with locked
              dependencies; the page reads one exported file and checks it before showing any number.
            </p>
            <pre className="cmd"><code>{`uv sync --frozen
uv run --frozen pytest -q
uv run --frozen python -m match_lab smoke   # exploratory
python scripts/export_demo_data.py
cd demo && npm ci && npm test && npm run build`}</code></pre>
          </section>
        </div>
      </main>
      <footer className="site">
        <div className="wrap footer-grid">
          <div>
            <img className="footer-lockup" src="brand/lockup.svg" alt="Match" width="150" height="87" />
            <p>Author: Mohamed Bechir Kefi, independent researcher.</p>
          </div>
          <ul className="footer-links">
            <li><a href="https://github.com/mohamedbechirkefi/match-fairness-exposure">Repository on GitHub</a></li>
            <li><a href="https://github.com/mohamedbechirkefi/match-fairness-exposure/blob/main/research/paper/manuscript.md">Manuscript (preprint draft)</a></li>
            <li><a href="https://labs.kefimohamedbechir.workers.dev">All lab studies</a></li>
          </ul>
          <div className="footer-notes">
            <p>
              Runs offline after the first load. No data about visitors is collected, stored or sent anywhere. Every
              participant on this page is simulated; nothing here describes real people, protected attributes or any
              real platform.
            </p>
            <p>
              Licence: MATCH Source-Available Non-Commercial Research License v1.0, not an OSI-approved open-source
              licence. AI assistance: an AI system (Claude, Anthropic) was used as a research and development
              assistant for code, analysis and drafting under the author's direction; it is not an author.
            </p>
            <p>Typefaces: Young Serif and Libre Franklin, both under the SIL Open Font License 1.1, bundled with this page.</p>
          </div>
        </div>
      </footer>
    </>
  );
}

function kindOf(e: Experiment): { cls: string; text: string } {
  if (e.role.startsWith("exploratory")) return { cls: "badge-exploratory", text: "Exploratory, not confirmatory" };
  if (e.status.startsWith("partial")) return { cls: "badge-partial", text: "Measured, partly not run" };
  return { cls: "badge-measured", text: "Measured" };
}

function thetaRows(r: Results, arm: "POPULARITY" | "EXPOSURE_BALANCED"): ForestRow[] {
  const get = (id: string) => r.experiments.find((e) => e.id === id);
  const rows: ForestRow[] = [];
  const pick = (id: string, test: (label: string) => boolean, label: string, kind: ForestRow["kind"]) => {
    const e = get(id);
    const x = e?.estimates.find((s) => s.ci_level === 0.95 && s.label.includes(arm) && test(s.label));
    if (!x) return;
    rows.push({ key: `${id}-${label}`, label, kind, estimate: x.estimate, lo: x.ci_low, hi: x.ci_high, display: fmtEstimate(x), interval: x.interval_display ?? undefined });
  };
  pick("EXP-001", () => true, "EXP-001, T 40, 9 cells", "measured");
  pick("EXP-003", (l) => l.startsWith("EXP-001 reference"), "EXP-003 reference, T 40, 4 corner cells", "measured");
  pick("EXP-003", (l) => l.startsWith("S1, theta 0.3"), "S1, theta 0.3", "measured");
  pick("EXP-003", (l) => l.startsWith("S1, theta 0.7"), "S1, theta 0.7", "measured");
  pick("EXP-003", (l) => l.startsWith("S2, T 20"), "S2, T 20", "measured");
  pick("EXP-003", (l) => l.startsWith("S2, T 10"), "S2, T 10", "measured");
  const s3 = get("EXP-003")?.components.find((c) => c.id === "S3");
  if (s3) rows.push({ key: "S3", label: "S3, welfare definition", kind: "not_run", note: s3.status });
  if (arm === "POPULARITY") pick("M4-HORIZON", (l) => l.includes("T = 80"), "M4 probe, T 80, seed 505", "exploratory");
  else pick("M4-HORIZON", (l) => l.includes("every horizon"), "M4 probe, every horizon, seed 505", "exploratory");
  return rows;
}

function Published({ r }: { r: Results }) {
  const cells = [...new Set(r.tradeoff.map((t) => t.cell))];
  const [cell, setCell] = useState(cells[0]);
  const pts = r.tradeoff.filter((t) => t.cell === cell);
  const exp3 = r.experiments.find((e) => e.id === "EXP-003");
  return (
    <>
      <section id="key" aria-labelledby="h-key">
        <h2 id="h-key">The horizon decides the sign</h2>
        <p className="lede">
          Each row is one registered setting: a paired difference in mean agent welfare W against random exposure, on
          the same market instances. Popularity ranking sits right of zero at 40 rounds and far left of it at 10 and 20.
        </p>
        <p className="note">
          These numbers come from the committed results of the runs at revision <code>{r.code_revision.slice(0, 7)}</code>,
          printed exactly as in the manuscript. Contrasts are paired differences in mean agent welfare W against RANDOM
          on the same market instances (welfare units, W in [0, 1]). They are separate from anything the sandbox
          produces.
        </p>
        <div className="forest-pair">
          <Forest
            title="POPULARITY - RANDOM across registered settings"
            unit="theta_P, welfare units"
            caption="Dot: estimate; bar: 95% bootstrap CI over instances; line at 0. Where no bar is visible, the interval is narrower than the dot. The S3 row is a registered analysis that was not run."
            rows={thetaRows(r, "POPULARITY")}
          />
          <Forest
            title="EXPOSURE_BALANCED - RANDOM across registered settings"
            unit="theta_P, welfare units"
            caption="Same layout on a much smaller scale: every estimate shown is smaller than the equivalence margin of 0.01, but equivalence was tested only for EXP-001."
            rows={thetaRows(r, "EXPOSURE_BALANCED")}
          />
        </div>
      </section>

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <div id="overview" className="overview">
          <p className="status-label"><span className="badge badge-status">Status</span> {r.status_label}</p>
          <p>
            Synthetic participants on two sides hold reciprocal, partly shared preferences. In sequential discovery
            every unmatched participant sees a short slate of candidates each round, chosen at random (the baseline), by
            popularity, or by popularity under an exposure cap. The study compares mean welfare after a fixed number of
            rounds, and places centralized matching mechanisms on the same markets as references.
          </p>
          <ul className="verdicts">
            {r.experiments.map((e) => (
              <li key={e.id}>
                <strong>{e.id}</strong> <span className={`badge ${kindOf(e).cls}`}>{kindOf(e).text}</span> {e.verdict}
              </li>
            ))}
          </ul>
          <p className="legend-key">
            Labels used on this page: <span className="badge badge-measured">Measured</span> results from the committed
            runs; <span className="badge badge-exploratory">Exploratory, not confirmatory</span> diagnostics added after
            the confirmatory analysis; <span className="badge badge-notrun">Not run</span> registered analyses that were
            not executed; <span className="badge badge-assumption">Model assumption</span> inputs of the simulation;{" "}
            <span className="badge badge-sandbox">Sandbox output</span> numbers your browser computes.
          </p>
        </div>

        {r.experiments.map((e) => (
          <article key={e.id} className={`panel ${kindOf(e).cls}-panel`} aria-labelledby={`h-${e.id}`}>
            <h3 id={`h-${e.id}`}>
              {e.id}: {e.title}
            </h3>
            <p>
              <span className={`badge ${kindOf(e).cls}`}>{kindOf(e).text}</span> <span className="meta">{e.role}</span>
            </p>
            <p><strong>Status:</strong> {e.status}</p>
            <p><strong>Verdict under the frozen rule:</strong> {e.verdict}</p>
            {e.components.length > 0 && (
              <ul className="components">
                {e.components.map((c) => (
                  <li key={c.id} className={c.status.startsWith("not run") ? "component notrun" : "component"}>
                    <p className="component-head">
                      <strong>{c.id}</strong>{" "}
                      <span className={`badge ${c.status.startsWith("not run") ? "badge-notrun" : "badge-measured"}`}>{c.status}</span>
                    </p>
                    <p>{c.title}</p>
                    <p className="meta">{c.verdict}</p>
                  </li>
                ))}
              </ul>
            )}
            {e.estimates.length > 0 && (
              <div id={`table-${e.id}`} className="table-scroll" role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
                <table className="stack">
                  <thead>
                    <tr>
                      <th scope="col">Quantity</th>
                      <th scope="col">Estimate</th>
                      <th scope="col">Interval</th>
                    </tr>
                  </thead>
                  <tbody>
                    {e.estimates.map((x) => (
                      <tr key={x.label}>
                        <th scope="row">{x.label}</th>
                        <td className="num" data-label="Estimate">{fmtEstimate(x)}</td>
                        <td data-label="Interval">{fmtInterval(x)}</td>
                      </tr>
                    ))}
                    {e === exp3 && (
                      <tr className="notrun-row">
                        <th scope="row">S3, metric definition: POPULARITY and EXPOSURE_BALANCED</th>
                        <td data-label="Estimate">not run</td>
                        <td data-label="Interval">no estimate exists</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
            {e.notes.map((n, i) => (
              <p key={i} className="note">{n}</p>
            ))}
            <p className="meta">
              Report: <code>{e.report_path}</code>
              {e.claim_ids.length > 0 && <> · Claims: {e.claim_ids.join(", ")}</>}
            </p>
          </article>
        ))}

        <Forest
          title="EXP-001 per cell: POPULARITY - RANDOM (manuscript Table 3)"
          unit="paired difference in W"
          caption="30 instances per cell; 95% bootstrap CIs, unadjusted and secondary."
          rows={r.exp001_cells.filter((c) => c.arm === "POPULARITY").map((c) => ({ key: c.cell, label: c.cell, kind: "measured", estimate: c.estimate, lo: c.ci_low, hi: c.ci_high, display: c.display, interval: c.interval_display }))}
        />
        <Forest
          title="EXP-001 per cell: EXPOSURE_BALANCED - RANDOM (manuscript Table 3)"
          unit="paired difference in W"
          caption="30 instances per cell; 95% bootstrap CIs, unadjusted and secondary."
          rows={r.exp001_cells.filter((c) => c.arm === "EXPOSURE_BALANCED").map((c) => ({ key: c.cell, label: c.cell, kind: "measured", estimate: c.estimate, lo: c.ci_low, hi: c.ci_high, display: c.display, interval: c.interval_display }))}
        />
      </section>

      <section id="tradeoff" aria-labelledby="h-tradeoff">
        <p className="label-row"><span className="badge badge-measured">Measured, descriptive</span></p>
        <h2 id="h-tradeoff">Fairness and satisfaction trade-off (EXP-001)</h2>
        <p>
          For one design cell at a time, each slate policy is placed by its mean agent welfare W (vertical, higher is
          better for participants on average) and by the inequality of the attention side-B participants receive, the
          Gini coefficient of their exposure (horizontal, further left means attention is spread more equally).
        </p>
        <div className="controls">
          <label>
            Design cell (imbalance r, preference correlation rho)
            <select id="tradeoff-cell" value={cell} onChange={(e) => setCell(e.target.value)}>
              {cells.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>
        <Legend arms={["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"]} />
        <TradeoffChart
          title={`EXP-001 trade-off, ${cell}`}
          desc={`Mean welfare W against side-B exposure Gini for RANDOM, POPULARITY and EXPOSURE_BALANCED at ${cell}, T = 40. Whiskers: one standard deviation across 30 instances. Values are in the table below the chart.`}
          xLabel="Gini of side-B exposure (lower: more equal)"
          yLabel="Mean agent welfare W"
          points={pts.map((t) => ({ key: t.arm, arm: t.arm, label: t.arm, x: t.gini_B_mean, y: t.W_mean, xErr: t.gini_B_sd, yErr: t.W_sd }))}
        />
        <div id="table-tradeoff" className="table-scroll" role="region" aria-label="Trade-off values" tabIndex={0}>
          <table className="stack">
            <caption className="meta">{cell}: means over {pts[0]?.n_instances} instances (descriptive, no tests).</caption>
            <thead>
              <tr>
                <th scope="col">Arm</th>
                <th scope="col">Mean welfare W</th>
                <th scope="col">Gini, side-B exposure</th>
              </tr>
            </thead>
            <tbody>
              {pts.map((t) => (
                <tr key={t.arm}>
                  <th scope="row">{t.arm}</th>
                  <td className="num" data-label="Mean welfare W">{t.W_display}</td>
                  <td className="num" data-label="Gini, side-B exposure">{t.gini_B_display}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">{r.tradeoff_note}</p>
      </section>

      <section id="assumptions" aria-labelledby="h-assumptions">
        <p className="label-row"><span className="badge badge-assumption">Model assumption</span></p>
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="note">These are inputs of the simulation, fixed in the frozen protocol, not results.</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          The protocol and one protocol per experiment were frozen by the owner on 2026-11-24 before the confirmatory
          runs, with SHA-256 hashes recorded. Every arm runs on the same market instances with common random numbers;
          intervals are percentile bootstrap intervals over instances, stratified by cell for pooled estimates. The
          limitations below are those of the manuscript, section 7.
        </p>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
