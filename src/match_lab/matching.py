# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Centralized matching (simulation layer; protocol section 2.3) and matching validity checks.

A matching is a pair of integer arrays ``(match_a, match_b)``: ``match_a[i]`` is the
B-index of i's partner or -1, ``match_b[j]`` the A-index of j's partner or -1.
Capacity is one on both sides.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment

from .errors import InvalidInputError, InvalidMatchingError
from .market import Market


def _validate_prefs(prefs: Sequence[Sequence[int]], n_other: int, label: str) -> None:
    for x, lst in enumerate(prefs):
        seen: set[int] = set()
        for y in lst:
            if isinstance(y, bool) or not isinstance(y, (int, np.integer)):
                raise InvalidInputError(f"{label}[{x}] contains a non-integer entry {y!r}")
            if not 0 <= y < n_other:
                raise InvalidInputError(f"{label}[{x}] entry {y} out of range [0, {n_other})")
            if y in seen:
                raise InvalidInputError(f"{label}[{x}] lists {y} twice")
            seen.add(int(y))


def deferred_acceptance(
    proposer_prefs: Sequence[Sequence[int]], receiver_prefs: Sequence[Sequence[int]]
) -> tuple[np.ndarray, np.ndarray]:
    """Gale and Shapley (1962) deferred acceptance with capacity one.

    ``proposer_prefs[p]`` lists the receivers acceptable to p, best first; unlisted receivers
    are unacceptable. Likewise for ``receiver_prefs``. A receiver holds a proposal only from a
    proposer on its list. Returns ``(match_proposers, match_receivers)`` with -1 for unmatched.
    The result is the proposer-optimal stable matching and does not depend on the order in
    which free proposers are processed (here: FIFO by index).
    """
    n_p, n_r = len(proposer_prefs), len(receiver_prefs)
    _validate_prefs(proposer_prefs, n_r, "proposer_prefs")
    _validate_prefs(receiver_prefs, n_p, "receiver_prefs")
    receiver_rank = [{int(p): k for k, p in enumerate(lst)} for lst in receiver_prefs]
    next_idx = [0] * n_p
    match_p = np.full(n_p, -1, dtype=np.int64)
    match_r = np.full(n_r, -1, dtype=np.int64)
    free: deque[int] = deque(range(n_p))
    while free:
        p = free.popleft()
        lst = proposer_prefs[p]
        while next_idx[p] < len(lst):
            r = int(lst[next_idx[p]])
            next_idx[p] += 1
            rank_p = receiver_rank[r].get(p)
            if rank_p is None:
                continue  # p is unacceptable to r
            cur = int(match_r[r])
            if cur == -1:
                match_r[r], match_p[p] = p, r
                break
            if rank_p < receiver_rank[r][cur]:
                match_r[r], match_p[p] = p, r
                match_p[cur] = -1
                free.append(cur)
                break
        # if the loop ran out, p stays unmatched
    return match_p, match_r


def preference_lists(sat: np.ndarray, acc: np.ndarray) -> list[list[int]]:
    """Acceptable partners per row, best first (highest satisfaction; ties by lower index)."""
    out: list[list[int]] = []
    for i in range(sat.shape[0]):
        idx = np.flatnonzero(acc[i])
        order = np.lexsort((idx, -sat[i, idx]))
        out.append([int(j) for j in idx[order]])
    return out


def da_a(market: Market) -> tuple[np.ndarray, np.ndarray]:
    """DA_A: A proposes. Lists truncated to acceptable partners."""
    return deferred_acceptance(
        preference_lists(market.sat_a, market.acc_a), preference_lists(market.sat_b, market.acc_b)
    )


def da_b(market: Market) -> tuple[np.ndarray, np.ndarray]:
    """DA_B: B proposes. Returned in (match_a, match_b) orientation."""
    m_b, m_a = deferred_acceptance(
        preference_lists(market.sat_b, market.acc_b), preference_lists(market.sat_a, market.acc_a)
    )
    return m_a, m_b


def max_weight(market: Market) -> tuple[np.ndarray, np.ndarray]:
    """MAXW: maximize sum of (s_ij + s_ji) over matched, mutually acceptable pairs.

    Rectangular linear assignment (scipy). Non-mutually-acceptable cells get weight 0 and any
    assignment to them is discarded, which is equivalent to leaving both agents unmatched
    (an unmatched agent contributes 0 to the objective).
    """
    n_a, n_b = market.n_a, market.n_b
    match_a = np.full(n_a, -1, dtype=np.int64)
    match_b = np.full(n_b, -1, dtype=np.int64)
    if n_a == 0 or n_b == 0:
        return match_a, match_b
    allowed = market.acc_a & market.acc_b.T
    w = np.where(allowed, market.sat_a + market.sat_b.T, 0.0)
    rows, cols = linear_sum_assignment(w, maximize=True)
    for i, j in zip(rows, cols):
        if allowed[i, j]:
            match_a[i], match_b[j] = j, i
    return match_a, match_b


def validate_matching(
    match_a: np.ndarray, match_b: np.ndarray, acc_a: np.ndarray | None = None, acc_b: np.ndarray | None = None
) -> list[str]:
    """Return a list of violated invariants (empty when valid).

    Checks: integer arrays, indices in range, no duplicate partner (capacity one on both
    sides), mutual consistency, and, when acceptability is given, that every matched pair is
    mutually acceptable.
    """
    failures: list[str] = []
    match_a = np.asarray(match_a)
    match_b = np.asarray(match_b)
    n_a, n_b = len(match_a), len(match_b)
    if not (np.issubdtype(match_a.dtype, np.integer) and np.issubdtype(match_b.dtype, np.integer)):
        return ["matching arrays are not integer typed"]
    if np.any((match_a < -1) | (match_a >= n_b)):
        failures.append("match_a index out of range")
    if np.any((match_b < -1) | (match_b >= n_a)):
        failures.append("match_b index out of range")
    if failures:
        return failures
    pa = match_a[match_a >= 0]
    pb = match_b[match_b >= 0]
    if len(np.unique(pa)) != len(pa):
        failures.append("duplicate match: a B agent is the partner of several A agents (capacity breach)")
    if len(np.unique(pb)) != len(pb):
        failures.append("duplicate match: an A agent is the partner of several B agents (capacity breach)")
    for i in np.flatnonzero(match_a >= 0):
        if match_b[match_a[i]] != i:
            failures.append(f"inconsistent matching at A agent {int(i)}")
            break
    for j in np.flatnonzero(match_b >= 0):
        if match_a[match_b[j]] != j:
            failures.append(f"inconsistent matching at B agent {int(j)}")
            break
    if acc_a is not None and acc_b is not None:
        for i in np.flatnonzero(match_a >= 0):
            j = match_a[i]
            if not (acc_a[i, j] and acc_b[j, i]):
                failures.append(f"matched pair (A{int(i)}, B{int(j)}) is not mutually acceptable")
                break
    return failures


def require_valid_matching(match_a: np.ndarray, match_b: np.ndarray, market: Market) -> None:
    failures = validate_matching(match_a, match_b, market.acc_a, market.acc_b)
    if failures:
        raise InvalidMatchingError("; ".join(failures))
