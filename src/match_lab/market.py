# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Synthetic two-sided market generator (ingestion layer; protocol section 2.1).

Everything here is synthetic. Agents are rows of arrays, not people.

Units and conventions
---------------------
- Side A has ``n_a`` agents, side B has ``n_b = floor(r * n_a + 0.5)`` agents.
- ``u_a[i, j]`` is the utility of A-agent i for B-agent j (unitless, real).
  ``u_b[j, i]`` is the utility of B-agent j for A-agent i.
- ``sat_a[i, j]`` is the rank-percentile satisfaction of i with j, in [0, 1]:
  ``1 - (rank - 1) / (m - 1)`` with rank 1 the best of the m agents on the other
  side; if m == 1 the single candidate has satisfaction 1.
- ``acc_a[i, j]`` is True iff ``u_a[i, j] >= tau_i`` where tau_i is the
  theta-quantile (numpy "linear" method) of row i of ``u_a``.
- Ties in utility have probability zero; ranks break them by the lower index.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .errors import InvalidInputError


@dataclass(frozen=True)
class MarketParams:
    """Parameters of one synthetic market (validated on construction)."""

    n_a: int
    r: float
    rho: float
    theta: float

    def __post_init__(self) -> None:
        if isinstance(self.n_a, bool) or not isinstance(self.n_a, (int, np.integer)):
            raise InvalidInputError(f"n_a must be an integer, got {self.n_a!r}")
        if self.n_a < 0:
            raise InvalidInputError(f"n_a must be >= 0, got {self.n_a}")
        for name in ("r", "rho", "theta"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float, np.floating)):
                raise InvalidInputError(f"{name} must be a real number, got {value!r}")
            if not math.isfinite(float(value)):
                raise InvalidInputError(f"{name} must be finite, got {value!r}")
        if self.r < 1.0:
            raise InvalidInputError(f"r must be >= 1 (B is the long side), got {self.r}")
        if not 0.0 <= self.rho <= 1.0:
            raise InvalidInputError(f"rho must be in [0, 1], got {self.rho}")
        if not 0.0 <= self.theta <= 1.0:
            raise InvalidInputError(f"theta must be in [0, 1], got {self.theta}")

    @property
    def n_b(self) -> int:
        return side_size(self.n_a, self.r)


def side_size(n_a: int, r: float) -> int:
    """n_B = round half up of r * n_A (protocol 2.1; explicit to avoid banker's rounding)."""
    return int(math.floor(r * n_a + 0.5))


@dataclass(frozen=True)
class Market:
    params: MarketParams
    q_a: np.ndarray  # (n_a,) latent quality of A agents
    q_b: np.ndarray  # (n_b,)
    u_a: np.ndarray  # (n_a, n_b)
    u_b: np.ndarray  # (n_b, n_a)
    sat_a: np.ndarray  # (n_a, n_b) in [0, 1]
    sat_b: np.ndarray  # (n_b, n_a)
    acc_a: np.ndarray  # (n_a, n_b) bool
    acc_b: np.ndarray  # (n_b, n_a) bool

    @property
    def n_a(self) -> int:
        return int(self.u_a.shape[0])

    @property
    def n_b(self) -> int:
        return int(self.u_b.shape[0])


def satisfaction_from_utilities(u: np.ndarray) -> np.ndarray:
    """Rank-percentile satisfaction per row; ties broken by the lower column index."""
    u = np.asarray(u, dtype=float)
    if u.ndim != 2:
        raise InvalidInputError("utility matrix must be 2-D")
    if not np.all(np.isfinite(u)):
        raise InvalidInputError("utility matrix must be finite")
    n, m = u.shape
    sat = np.zeros((n, m), dtype=float)
    if n == 0 or m == 0:
        return sat
    if m == 1:
        sat[:, 0] = 1.0
        return sat
    order = np.argsort(-u, axis=1, kind="stable")  # best first; stable keeps lower index first on ties
    ranks = np.empty((n, m), dtype=np.int64)
    rows = np.arange(n)[:, None]
    ranks[rows, order] = np.arange(1, m + 1)[None, :]
    return 1.0 - (ranks - 1) / (m - 1)


def acceptability_from_utilities(u: np.ndarray, theta: float) -> np.ndarray:
    """acc[i, j] = u[i, j] >= theta-quantile of row i (numpy 'linear' quantile)."""
    u = np.asarray(u, dtype=float)
    if u.ndim != 2:
        raise InvalidInputError("utility matrix must be 2-D")
    if not 0.0 <= theta <= 1.0:
        raise InvalidInputError(f"theta must be in [0, 1], got {theta}")
    n, m = u.shape
    if n == 0 or m == 0:
        return np.zeros((n, m), dtype=bool)
    tau = np.quantile(u, theta, axis=1, method="linear", keepdims=True)
    return u >= tau


def build_market(
    params: MarketParams, q_a: np.ndarray, q_b: np.ndarray, u_a: np.ndarray, u_b: np.ndarray
) -> Market:
    """Assemble a market from explicit utilities (used by the generator and by hand-made tests)."""
    u_a = np.asarray(u_a, dtype=float).reshape(len(q_a), len(q_b))
    u_b = np.asarray(u_b, dtype=float).reshape(len(q_b), len(q_a))
    return Market(
        params=params,
        q_a=np.asarray(q_a, dtype=float),
        q_b=np.asarray(q_b, dtype=float),
        u_a=u_a,
        u_b=u_b,
        sat_a=satisfaction_from_utilities(u_a),
        sat_b=satisfaction_from_utilities(u_b),
        acc_a=acceptability_from_utilities(u_a, params.theta),
        acc_b=acceptability_from_utilities(u_b, params.theta),
    )


def generate_market(params: MarketParams, seed: np.random.SeedSequence) -> Market:
    """Draw q and idiosyncratic terms in a fixed order from one seeded stream.

    Draw order (part of the generator contract, GEN-match-market v1):
    q_a (n_a), q_b (n_b), e_a (n_a x n_b), e_b (n_b x n_a), all standard normal.
    theta does not consume randomness, so changing theta keeps the same utilities.
    """
    if not isinstance(seed, np.random.SeedSequence):
        raise InvalidInputError("seed must be a numpy SeedSequence")
    rng = np.random.default_rng(seed)
    n_a, n_b = params.n_a, params.n_b
    q_a = rng.standard_normal(n_a)
    q_b = rng.standard_normal(n_b)
    e_a = rng.standard_normal((n_a, n_b))
    e_b = rng.standard_normal((n_b, n_a))
    a, b = math.sqrt(params.rho), math.sqrt(1.0 - params.rho)
    u_a = a * q_b[None, :] + b * e_a
    u_b = a * q_a[None, :] + b * e_b
    return build_market(params, q_a, q_b, u_a, u_b)


GENERATOR_VERSION = "GEN-match-market v1"
