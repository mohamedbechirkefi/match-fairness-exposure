// SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
// Shared sandbox definitions (main thread and worker): bounds, parameter
// checks and message types. The worker runs the computation.
import type { Metrics } from "./engine";

export const SANDBOX_N_A = 20;
export const SANDBOX_K = 5;
export const MAX_T = 12;

export interface SandboxParams {
  seed: number;
  r: number;
  rho: number;
  theta: number;
  T: number;
}

export interface ArmResult {
  arm: string;
  matchA: number[];
  mutual: number[];
  exposureA: number[] | null;
  exposureB: number[] | null;
  metrics: Metrics;
  lastMatchRound: number | null;
}

export type WorkerRequest = { type: "run"; params: SandboxParams } | { type: "cancel" };
export type WorkerReply =
  | { type: "progress"; fraction: number }
  | { type: "done"; params: SandboxParams; nB: number; qA: number[]; qB: number[]; arms: ArmResult[] }
  | { type: "cancelled" }
  | { type: "error"; message: string };

export function checkParams(p: SandboxParams): string | null {
  if (!Number.isInteger(p.seed) || p.seed < 1 || p.seed > 1_000_000) return "seed must be an integer from 1 to 1,000,000";
  if (![1.0, 1.1, 1.5].includes(p.r)) return "r must be 1.0, 1.1 or 1.5";
  if (![0, 0.5, 0.9].includes(p.rho)) return "rho must be 0, 0.5 or 0.9";
  if (![0.3, 0.5, 0.7].includes(p.theta)) return "theta must be 0.3, 0.5 or 0.7";
  if (!Number.isInteger(p.T) || p.T < 1 || p.T > MAX_T) return `T must be an integer from 1 to ${MAX_T}`;
  return null;
}

