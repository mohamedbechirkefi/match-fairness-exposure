# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Outcome metrics per market instance and arm (metrics layer; protocol section 2.4).

All satisfaction-based metrics are unitless in [0, 1]. A metric that is undefined for an
instance (for example mutual satisfaction with no matched pair, or anything on an empty
side) is returned as None, never as NaN.
"""

from __future__ import annotations

import numpy as np

from .market import Market


def agent_satisfaction(sat: np.ndarray, match: np.ndarray) -> np.ndarray:
    """s_x for each agent of one side: satisfaction with partner, 0 if unmatched."""
    s = np.zeros(len(match), dtype=float)
    m = match >= 0
    s[m] = sat[np.flatnonzero(m), match[m]]
    return s


def gini(x: np.ndarray) -> float | None:
    """Gini coefficient of a non-negative vector; None if empty, 0.0 if all zero."""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return None
    if np.any(x < 0) or not np.all(np.isfinite(x)):
        raise ValueError("gini requires finite non-negative values")
    total = x.sum()
    if total == 0:
        return 0.0
    xs = np.sort(x)
    n = xs.size
    ranks = np.arange(1, n + 1)
    return float((2.0 * np.sum(ranks * xs)) / (n * total) - (n + 1.0) / n)


def blocking_pairs(market: Market, match_a: np.ndarray, match_b: np.ndarray) -> int:
    """Count mutually acceptable pairs where both strictly prefer each other to their status.

    An unmatched agent prefers any acceptable partner. Current partners are excluded because
    preference is strict.
    """
    if market.n_a == 0 or market.n_b == 0:
        return 0
    cur_a = np.full(market.n_a, -np.inf)
    ma = match_a >= 0
    cur_a[ma] = market.sat_a[np.flatnonzero(ma), match_a[ma]]
    cur_b = np.full(market.n_b, -np.inf)
    mb = match_b >= 0
    cur_b[mb] = market.sat_b[np.flatnonzero(mb), match_b[mb]]
    better_a = market.sat_a > cur_a[:, None]
    better_b = market.sat_b > cur_b[:, None]
    block = market.acc_a & market.acc_b.T & better_a & better_b.T
    return int(block.sum())


def _mean_or_none(x: np.ndarray) -> float | None:
    return float(np.mean(x)) if x.size else None


def _quartile_welfare(s: np.ndarray, q: np.ndarray) -> tuple[float | None, float | None, float | None]:
    if s.size == 0:
        return None, None, None
    lo, hi = np.quantile(q, [0.25, 0.75])
    bottom = _mean_or_none(s[q <= lo])
    top = _mean_or_none(s[q >= hi])
    gap = None if bottom is None or top is None else top - bottom
    return bottom, top, gap


METRIC_NAMES = (
    "W", "W_A", "W_B", "U", "U_A", "U_B", "M", "n_matched",
    "gini_exposure_A", "gini_exposure_B", "blocking_pairs", "blocking_per_100",
    "W_A_q_bottom", "W_A_q_top", "W_A_q_gap", "W_B_q_bottom", "W_B_q_top", "W_B_q_gap",
)


def compute_metrics(
    market: Market,
    match_a: np.ndarray,
    match_b: np.ndarray,
    exposure_a: np.ndarray | None = None,
    exposure_b: np.ndarray | None = None,
) -> dict[str, float | int | None]:
    s_a = agent_satisfaction(market.sat_a, match_a)
    s_b = agent_satisfaction(market.sat_b, match_b)
    n_total = market.n_a + market.n_b
    all_s = np.concatenate([s_a, s_b])
    matched = np.flatnonzero(match_a >= 0)
    n_matched = int(matched.size)
    if n_matched:
        partners = match_a[matched]
        mutual = np.minimum(market.sat_a[matched, partners], market.sat_b[partners, matched])
        m_val: float | None = float(mutual.mean())
    else:
        m_val = None
    bp = blocking_pairs(market, match_a, match_b)
    a_bot, a_top, a_gap = _quartile_welfare(s_a, market.q_a)
    b_bot, b_top, b_gap = _quartile_welfare(s_b, market.q_b)
    return {
        "W": _mean_or_none(all_s),
        "W_A": _mean_or_none(s_a),
        "W_B": _mean_or_none(s_b),
        "U": (n_total - 2 * n_matched) / n_total if n_total else None,
        "U_A": float(np.mean(match_a < 0)) if market.n_a else None,
        "U_B": float(np.mean(match_b < 0)) if market.n_b else None,
        "M": m_val,
        "n_matched": n_matched,
        "gini_exposure_A": gini(exposure_a) if exposure_a is not None else None,
        "gini_exposure_B": gini(exposure_b) if exposure_b is not None else None,
        "blocking_pairs": bp,
        "blocking_per_100": 100.0 * bp / n_total if n_total else None,
        "W_A_q_bottom": a_bot, "W_A_q_top": a_top, "W_A_q_gap": a_gap,
        "W_B_q_bottom": b_bot, "W_B_q_top": b_top, "W_B_q_gap": b_gap,
    }


def metric_failures(metrics: dict[str, float | int | None]) -> list[str]:
    """Validity checks on metric values: finite, and in range where a range is defined."""
    failures = []
    bounded01 = {"W", "W_A", "W_B", "U", "U_A", "U_B", "M", "gini_exposure_A", "gini_exposure_B",
                 "W_A_q_bottom", "W_A_q_top", "W_B_q_bottom", "W_B_q_top"}
    for name, v in metrics.items():
        if v is None:
            continue
        if not np.isfinite(v):
            failures.append(f"non-finite metric {name}")
        elif name in bounded01 and not (-1e-12 <= v <= 1 + 1e-12):
            failures.append(f"metric {name}={v} outside [0, 1]")
        elif name.endswith("_gap") and not (-1 - 1e-12 <= v <= 1 + 1e-12):
            failures.append(f"metric {name}={v} outside [-1, 1]")
        elif name in ("blocking_pairs", "blocking_per_100", "n_matched") and v < 0:
            failures.append(f"metric {name} negative")
    return failures
