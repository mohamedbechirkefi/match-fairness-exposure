# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Uncertainty machinery of protocol section 4 (paired, instance-level, stratified by cell).

Inputs are per-instance paired differences D (one value per market instance). Agents are
never treated as independent units.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np

from .errors import InvalidInputError

Z_80_POWER = 0.8416212335729143  # Phi^-1(0.80)
Z_975 = 1.959963984540054  # Phi^-1(0.975)


def _arr(x: Sequence[float]) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    if a.ndim != 1 or a.size == 0 or not np.all(np.isfinite(a)):
        raise InvalidInputError("need a non-empty 1-D array of finite values")
    return a


def mean_sd_dz(d: Sequence[float]) -> tuple[float, float | None, float | None]:
    """Mean, sample SD (ddof=1) and standardized paired effect dz = mean / SD."""
    a = _arr(d)
    m = float(a.mean())
    if a.size < 2:
        return m, None, None
    sd = float(a.std(ddof=1))
    return m, sd, (m / sd if sd > 0 else None)


def bootstrap_ci(d: Sequence[float], *, n_resamples: int = 10_000, level: float = 0.95,
                 rng: np.random.Generator) -> tuple[float, float]:
    """Percentile bootstrap CI of the mean, resampling instances with replacement."""
    a = _arr(d)
    idx = rng.integers(0, a.size, size=(n_resamples, a.size))
    means = a[idx].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def stratified_mean(by_cell: Mapping[str, Sequence[float]]) -> float:
    """Equal-weight mean over cells of the per-cell mean (the estimand theta_P)."""
    if not by_cell:
        raise InvalidInputError("no cells")
    return float(np.mean([_arr(v).mean() for v in by_cell.values()]))


def stratified_bootstrap_ci(by_cell: Mapping[str, Sequence[float]], *, n_resamples: int = 10_000,
                            level: float = 0.95, rng: np.random.Generator) -> tuple[float, float]:
    """Resample instances within each cell, then take the equal-weight mean over cells."""
    if not by_cell:
        raise InvalidInputError("no cells")
    acc = np.zeros(n_resamples)
    for v in by_cell.values():
        a = _arr(v)
        idx = rng.integers(0, a.size, size=(n_resamples, a.size))
        acc += a[idx].mean(axis=1)
    acc /= len(by_cell)
    lo, hi = np.quantile(acc, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def sign_flip_pvalue(by_cell: Mapping[str, Sequence[float]], *, n_draws: int = 10_000,
                     rng: np.random.Generator) -> float:
    """Two-sided stratified paired sign-flip randomization test of theta = 0.

    Under H0 each paired difference is symmetric about 0; signs are flipped independently.
    Returns (1 + #{|T*| >= |T_obs|}) / (1 + n_draws).
    """
    obs = abs(stratified_mean(by_cell))
    acc = np.zeros(n_draws)
    for v in by_cell.values():
        a = _arr(v)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(n_draws, a.size))
        acc += (signs * a).mean(axis=1)
    acc /= len(by_cell)
    return float((1 + np.sum(np.abs(acc) >= obs - 1e-15)) / (1 + n_draws))


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values (monotone, capped at 1), in input order."""
    p = np.asarray(pvalues, dtype=float)
    if p.ndim != 1 or np.any((p < 0) | (p > 1)) or not np.all(np.isfinite(p)):
        raise InvalidInputError("p-values must be finite and in [0, 1]")
    m = p.size
    order = np.argsort(p, kind="stable")
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def n_for_power(sd: float, effect: float, *, alpha_z: float = Z_975, power_z: float = Z_80_POWER) -> int:
    """Normal-approximation paired sample size: n = ((z_a + z_b) * sd / effect)^2, rounded up."""
    if sd < 0 or effect <= 0:
        raise InvalidInputError("sd >= 0 and effect > 0 required")
    return int(math.ceil(((alpha_z + power_z) * sd / effect) ** 2))
