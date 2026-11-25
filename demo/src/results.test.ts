// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects an experiment without components (MATCH extension)", () => {
    const r = good();
    delete r.experiments[2].components;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed component status", () => {
    const r = good();
    r.experiments[2].components[2].status = "";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects missing per-cell estimates", () => {
    const r = good();
    r.exp001_cells.pop();
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a per-cell estimate with an inverted interval", () => {
    const r = good();
    r.exp001_cells[0].ci_low = 1;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a trade-off point with an unknown arm or an out-of-range mean", () => {
    const a = good();
    a.tradeoff[0].arm = "OTHER";
    expect(() => validateResults(a)).toThrow(ResultsError);
    const b = good();
    b.tradeoff[0].W_mean = 1.2;
    expect(() => validateResults(b)).toThrow(ResultsError);
  });
  it("rejects interval text without bounds", () => {
    const r = good();
    r.experiments[0].estimates[0].ci_low = null;
    r.experiments[0].estimates[0].ci_high = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("keeps EXP-003 S3 as not run", () => {
    const s3 = validateResults(good()).experiments.find((e) => e.id === "EXP-003")!.components.find((c) => c.id === "S3")!;
    expect(s3.status).toMatch(/^not run/);
  });
});
