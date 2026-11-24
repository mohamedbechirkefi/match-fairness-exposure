# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Shared helpers for tests: hand-built markets and brute-force reference implementations."""

from __future__ import annotations

import itertools

import numpy as np

from match_lab.market import MarketParams, build_market


def market_from_prefs(prefs_a: list[list[int]], prefs_b: list[list[int]], theta: float = 0.0):
    """Build a market whose strict orderings equal the given full preference lists (best first).

    Utilities are m - position, so satisfaction ranks match the lists. With theta = 0 every
    partner is acceptable.
    """
    n_a, n_b = len(prefs_a), len(prefs_b)
    u_a = np.zeros((n_a, n_b))
    for i, lst in enumerate(prefs_a):
        for pos, j in enumerate(lst):
            u_a[i, j] = n_b - pos
    u_b = np.zeros((n_b, n_a))
    for j, lst in enumerate(prefs_b):
        for pos, i in enumerate(lst):
            u_b[j, i] = n_a - pos
    r = n_b / n_a if n_a else 1.0
    params = MarketParams(n_a=n_a, r=max(1.0, r), rho=0.0, theta=theta)
    return build_market(params, np.zeros(n_a), np.zeros(n_b), u_a, u_b)


def all_matchings(allowed: np.ndarray):
    """Yield every matching (as match_a arrays) using only allowed[i, j] pairs. Tiny inputs only."""
    n_a, n_b = allowed.shape

    def rec(i: int, used: frozenset, cur: list[int]):
        if i == n_a:
            yield np.array(cur, dtype=np.int64)
            return
        yield from rec(i + 1, used, cur + [-1])
        for j in range(n_b):
            if allowed[i, j] and j not in used:
                yield from rec(i + 1, used | {j}, cur + [j])

    yield from rec(0, frozenset(), [])


def to_match_b(match_a: np.ndarray, n_b: int) -> np.ndarray:
    mb = np.full(n_b, -1, dtype=np.int64)
    for i, j in enumerate(match_a):
        if j >= 0:
            mb[j] = i
    return mb


def brute_force_blocking(market, match_a, match_b) -> int:
    count = 0
    for i, j in itertools.product(range(market.n_a), range(market.n_b)):
        if not (market.acc_a[i, j] and market.acc_b[j, i]):
            continue
        if match_a[i] == j:
            continue
        a_better = match_a[i] < 0 or market.sat_a[i, j] > market.sat_a[i, match_a[i]]
        b_better = match_b[j] < 0 or market.sat_b[j, i] > market.sat_b[j, match_b[j]]
        count += a_better and b_better
    return count
