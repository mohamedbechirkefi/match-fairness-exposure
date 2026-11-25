// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Fairness and satisfaction trade-off: mean agent welfare W (satisfaction, up is
// better) against the Gini coefficient of side-B exposure (inequality of
// attention, left is more equal). Hand-written SVG drawn at the container's
// pixel width, so text stays legible on a phone.
import { useEffect, useRef, useState } from "react";

export interface TPoint {
  key: string;
  arm: string;
  label: string;
  x: number;
  y: number;
  xErr?: number;
  yErr?: number;
}

export const ARM_SHORT: Record<string, string> = {
  RANDOM: "RANDOM",
  POPULARITY: "POPULARITY",
  EXPOSURE_BALANCED: "EXPOSURE_BALANCED",
  DA_A: "DA_A",
};

export function useWidth<T extends HTMLElement>(fallback = 640) {
  const ref = useRef<T | null>(null);
  const [w, setW] = useState(fallback);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const update = () => setW(Math.max(260, Math.floor(el.getBoundingClientRect().width)));
    update();
    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

export function Marker({ arm, cx, cy, size = 7 }: { arm: string; cx: number; cy: number; size?: number }) {
  const cls = `mk mk-${arm}`;
  if (arm === "POPULARITY") {
    const h = size * 1.15;
    return <polygon className={cls} points={`${cx},${cy - h} ${cx + h},${cy + h * 0.8} ${cx - h},${cy + h * 0.8}`} />;
  }
  if (arm === "EXPOSURE_BALANCED") return <rect className={cls} x={cx - size} y={cy - size} width={size * 2} height={size * 2} />;
  if (arm === "DA_A") return <polygon className={cls} points={`${cx},${cy - size * 1.2} ${cx + size * 1.2},${cy} ${cx},${cy + size * 1.2} ${cx - size * 1.2},${cy}`} />;
  return <circle className={cls} cx={cx} cy={cy} r={size} />;
}

function ticks(lo: number, hi: number, n = 4): number[] {
  const step0 = (hi - lo) / n;
  const mag = 10 ** Math.floor(Math.log10(step0));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= step0) ?? step0;
  const out: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + 1e-12; t += step) out.push(Number(t.toPrecision(6)));
  return out;
}

export function TradeoffChart({ points, title, desc, xLabel, yLabel }: { points: TPoint[]; title: string; desc: string; xLabel: string; yLabel: string }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const height = Math.round(Math.min(380, Math.max(260, width * 0.6)));
  const m = { l: 56, r: 16, t: 14, b: 46 };
  const xs = points.flatMap((p) => [p.x - (p.xErr ?? 0), p.x + (p.xErr ?? 0)]);
  const ys = points.flatMap((p) => [p.y - (p.yErr ?? 0), p.y + (p.yErr ?? 0)]);
  const pad = (a: number, b: number) => Math.max((b - a) * 0.12, 0.005);
  let [x0, x1] = [Math.min(...xs), Math.max(...xs)];
  let [y0, y1] = [Math.min(...ys), Math.max(...ys)];
  const px = pad(x0, x1), py = pad(y0, y1);
  x0 = Math.max(0, x0 - px); x1 = Math.min(1, x1 + px);
  y0 = Math.max(0, y0 - py); y1 = Math.min(1, y1 + py);
  const sx = (x: number) => m.l + ((x - x0) / (x1 - x0)) * (width - m.l - m.r);
  const sy = (y: number) => m.t + (1 - (y - y0) / (y1 - y0)) * (height - m.t - m.b);
  const id = title.replace(/\W+/g, "-").toLowerCase();
  return (
    <div ref={ref} className="chart">
      <svg width={width} height={height} role="img" aria-labelledby={`${id}-t ${id}-d`}>
        <title id={`${id}-t`}>{title}</title>
        <desc id={`${id}-d`}>{desc}</desc>
        {ticks(x0, x1).map((t) => (
          <g key={`x${t}`}>
            <line className="grid" x1={sx(t)} x2={sx(t)} y1={m.t} y2={height - m.b} />
            <text className="axis-text" x={sx(t)} y={height - m.b + 16} textAnchor="middle">{t}</text>
          </g>
        ))}
        {ticks(y0, y1).map((t) => (
          <g key={`y${t}`}>
            <line className="grid" x1={m.l} x2={width - m.r} y1={sy(t)} y2={sy(t)} />
            <text className="axis-text" x={m.l - 6} y={sy(t) + 4} textAnchor="end">{t}</text>
          </g>
        ))}
        <text className="axis-label" x={(m.l + width - m.r) / 2} y={height - 8} textAnchor="middle">{xLabel}</text>
        <text className="axis-label" transform={`translate(14 ${(m.t + height - m.b) / 2}) rotate(-90)`} textAnchor="middle">{yLabel}</text>
        {points.map((p) => (
          <g key={p.key}>
            {p.xErr != null && <line className={`err err-${p.arm}`} x1={sx(p.x - p.xErr)} x2={sx(p.x + p.xErr)} y1={sy(p.y)} y2={sy(p.y)} />}
            {p.yErr != null && <line className={`err err-${p.arm}`} x1={sx(p.x)} x2={sx(p.x)} y1={sy(p.y - p.yErr)} y2={sy(p.y + p.yErr)} />}
            <Marker arm={p.arm} cx={sx(p.x)} cy={sy(p.y)} />
          </g>
        ))}
      </svg>
    </div>
  );
}

export function Legend({ arms }: { arms: string[] }) {
  return (
    <ul className="legend" aria-label="Legend">
      {arms.map((a) => (
        <li key={a}>
          <svg width="18" height="18" aria-hidden="true">
            <Marker arm={a} cx={9} cy={9} size={5.5} />
          </svg>
          {ARM_SHORT[a] ?? a}
        </li>
      ))}
    </ul>
  );
}
