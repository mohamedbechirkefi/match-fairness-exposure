// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.
// MATCH extensions (also validated, also fail closed): per-experiment "role" and
// "components" (EXP-003 S1, S2, S3), "exp001_cells" (manuscript Table 3) and
// "tradeoff" (EXP-001 arm means for the fairness and satisfaction chart).

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export const ARMS = ["RANDOM", "POPULARITY", "EXPOSURE_BALANCED"] as const;
export type Arm = (typeof ARMS)[number];

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
}

export interface Component {
  id: string;
  title: string;
  status: string;
  verdict: string;
}

export interface Experiment {
  id: string;
  title: string;
  role: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
  components: Component[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

export interface CellEstimate {
  cell: string;
  r: number;
  rho: number;
  arm: Arm;
  estimate: number;
  ci_low: number;
  ci_high: number;
  ci_level: number;
  n_pairs: number;
  display: string;
  interval_display: string;
}

export interface TradeoffPoint {
  cell: string;
  r: number;
  rho: number;
  arm: Arm;
  n_instances: number;
  W_mean: number;
  W_sd: number;
  gini_B_mean: number;
  gini_B_sd: number;
  W_display: string;
  gini_B_display: string;
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  exp001_cells: CellEstimate[];
  tradeoff: TradeoffPoint[];
  tradeoff_note: string;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function arm(o: Obj, where: string): Arm {
  const a = str(o, "arm", where);
  if (!(ARMS as readonly string[]).includes(a)) throw new ResultsError(`${where}.arm: unknown arm ${a}`);
  return a as Arm;
}

function checkInterval(lo: number | null, hi: number | null, where: string) {
  if ((lo === null) !== (hi === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (lo !== null && hi !== null && lo > hi) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
  };
  checkInterval(e.ci_low, e.ci_high, where);
  if ((e.ci_low === null) !== (e.ci_level === null)) {
    throw new ResultsError(`${where}: an interval needs a level and a level needs an interval`);
  }
  if (e.ci_low === null && e.interval_display !== null) {
    throw new ResultsError(`${where}: interval text without interval bounds`);
  }
  return e;
}

function component(v: unknown, where: string): Component {
  const o = obj(v, where);
  return { id: str(o, "id", where), title: str(o, "title", where), status: str(o, "status", where), verdict: str(o, "verdict", where) };
}

function cellEstimate(v: unknown, where: string): CellEstimate {
  const o = obj(v, where);
  const c: CellEstimate = {
    cell: str(o, "cell", where),
    r: num(o, "r", where) as number,
    rho: num(o, "rho", where) as number,
    arm: arm(o, where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where) as number,
    ci_high: num(o, "ci_high", where) as number,
    ci_level: num(o, "ci_level", where) as number,
    n_pairs: num(o, "n_pairs", where) as number,
    display: str(o, "display", where),
    interval_display: str(o, "interval_display", where),
  };
  checkInterval(c.ci_low, c.ci_high, where);
  if (c.arm === "RANDOM") throw new ResultsError(`${where}: RANDOM is the comparator, not a contrast`);
  return c;
}

function tradeoffPoint(v: unknown, where: string): TradeoffPoint {
  const o = obj(v, where);
  const t: TradeoffPoint = {
    cell: str(o, "cell", where),
    r: num(o, "r", where) as number,
    rho: num(o, "rho", where) as number,
    arm: arm(o, where),
    n_instances: num(o, "n_instances", where) as number,
    W_mean: num(o, "W_mean", where) as number,
    W_sd: num(o, "W_sd", where) as number,
    gini_B_mean: num(o, "gini_B_mean", where) as number,
    gini_B_sd: num(o, "gini_B_sd", where) as number,
    W_display: str(o, "W_display", where),
    gini_B_display: str(o, "gini_B_display", where),
  };
  for (const k of ["W_mean", "gini_B_mean"] as const) {
    if (t[k] < 0 || t[k] > 1) throw new ResultsError(`${where}.${k}: outside [0, 1]`);
  }
  if (t.W_sd < 0 || t.gini_B_sd < 0) throw new ResultsError(`${where}: negative standard deviation`);
  return t;
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      role: str(e, "role", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
      components: arr(e, "components", w).map((x, j) => component(x, `${w}.components[${j}]`)),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  const exp001_cells = arr(o, "exp001_cells", "results").map((v, i) => cellEstimate(v, `exp001_cells[${i}]`));
  if (exp001_cells.length !== 18) throw new ResultsError("results.exp001_cells: expected 9 cells x 2 policies");
  const tradeoff = arr(o, "tradeoff", "results").map((v, i) => tradeoffPoint(v, `tradeoff[${i}]`));
  if (tradeoff.length !== 27) throw new ResultsError("results.tradeoff: expected 9 cells x 3 arms");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    exp001_cells,
    tradeoff,
    tradeoff_note: str(o, "tradeoff_note", "results"),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) {
    return e.ci_level === null ? e.interval_display : `${Math.round(e.ci_level * 100)}% CI ${e.interval_display}`;
  }
  if (e.ci_low === null || e.ci_high === null) return "no interval exists for this quantity";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
