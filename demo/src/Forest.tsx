// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Hand-written forest chart in HTML and CSS (no chart library). Every row has the
// same height and the same text weight whether it is measured, exploratory or not
// run, so a registered analysis that was not run is as visible as a positive one.
// Dots and interval bars draw from their place once when the chart scrolls into view.
import { useRevealOnce } from "./reveal";

export type RowKind = "measured" | "exploratory" | "not_run";

export interface ForestRow {
  key: string;
  label: string;
  kind: RowKind;
  estimate?: number;
  lo?: number | null;
  hi?: number | null;
  display?: string;
  interval?: string;
  note?: string;
}

function niceTicks(lo: number, hi: number): number[] {
  const span = hi - lo;
  const step0 = span / 4;
  const mag = 10 ** Math.floor(Math.log10(step0));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= step0) ?? step0;
  const out: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-12; t += step) out.push(Math.abs(t) < 1e-12 ? 0 : t);
  return out;
}

const tickText = (t: number) => (t === 0 ? "0" : (t > 0 ? "+" : "") + Number(t.toPrecision(3)).toString());

export function Forest({ title, rows, unit, caption }: { title: string; rows: ForestRow[]; unit: string; caption: string }) {
  const vals = rows.flatMap((r) => (r.kind === "not_run" ? [] : [r.estimate ?? 0, r.lo ?? r.estimate ?? 0, r.hi ?? r.estimate ?? 0]));
  let lo = Math.min(0, ...vals);
  let hi = Math.max(0, ...vals);
  const pad = (hi - lo) * 0.06 || 0.001;
  lo -= pad;
  hi += pad;
  const ticks = niceTicks(lo, hi);
  lo = Math.min(lo, ticks[0]);
  hi = Math.max(hi, ticks[ticks.length - 1]);
  const pct = (x: number) => `${((x - lo) / (hi - lo)) * 100}%`;
  const [ref, reveal] = useRevealOnce<HTMLElement>();
  return (
    <figure ref={ref} className={`forest${reveal}`}>
      <figcaption>
        <strong>{title}</strong> <span className="meta">{caption}</span>
      </figcaption>
      <div className="forest-rows" role="list">
        {rows.map((r, i) => (
          <div key={r.key} style={{ ["--row" as string]: i }} className={`forest-row kind-${r.kind}`} role="listitem">
            <div className="forest-label">
              {r.label}
              {r.kind === "exploratory" && <span className="tag tag-exploratory">exploratory</span>}
              {r.kind === "not_run" && <span className="tag tag-notrun">not run</span>}
            </div>
            <div className="forest-plot" aria-hidden="true">
              <span className="forest-zero" style={{ left: pct(0) }} />
              {r.kind === "not_run" ? (
                <span className="forest-notrun">not run: no estimate exists</span>
              ) : (
                <>
                  {r.lo != null && r.hi != null && (
                    <span className="forest-ci" style={{ left: pct(r.lo), width: `calc(${pct(r.hi)} - ${pct(r.lo)})` }} />
                  )}
                  <span className="forest-dot" style={{ left: pct(r.estimate ?? 0) }} />
                </>
              )}
            </div>
            <div className="forest-value">
              {r.kind === "not_run" ? (
                <span>{r.note ?? "not run"}</span>
              ) : (
                <>
                  <span className="num">{r.display}</span>{" "}
                  <span className="meta">{r.interval ? `(95% CI ${r.interval})` : "(no interval)"}</span>
                </>
              )}
            </div>
          </div>
        ))}
        <div className="forest-row forest-axis" aria-hidden="true">
          <div className="forest-label meta">{unit}</div>
          <div className="forest-plot axis">
            {ticks.map((t) => (
              <span key={t} className={`forest-tick${(t - lo) / (hi - lo) > 0.9 ? " end" : (t - lo) / (hi - lo) < 0.1 ? " start" : ""}`} style={{ left: pct(t) }}>
                {tickText(t)}
              </span>
            ))}
          </div>
          <div className="forest-value" />
        </div>
      </div>
    </figure>
  );
}
