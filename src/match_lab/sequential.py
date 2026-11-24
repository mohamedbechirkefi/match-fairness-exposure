# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Sequential discovery with slate policies (simulation layer; protocol section 2.2).

Round structure (t = 1..T):
1. Each still-unmatched agent on either side, in a seeded random order over all agents,
   receives a slate of up to k unmatched candidates from the other side that it has not
   been shown before. Candidate eligibility uses the unmatched set at the start of the round
   (matches only happen at the end of a round).
2. The viewer likes each shown candidate it finds acceptable.
3. At the end of the round, all mutual likes between unmatched agents are resolved greedily
   by decreasing s_ij + s_ji (ties by A index, then B index); matched agents leave.
4. Popularity scores p = (likes received + 1) / (exposure + 2) are recomputed.

Common random numbers: three independent streams (viewer order, RANDOM slate keys,
popularity tie keys) are drawn in full every round whatever the policy, so all arms consume
identical random numbers on the same instance.

Implementation choice recorded as D-007: the popularity tie key is one uniform draw per
candidate per round, shared by all viewers in that round (the protocol says "a seeded random
key" without fixing its granularity).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from .errors import InvalidInputError
from .market import Market


class Policy(str, Enum):
    RANDOM = "RANDOM"
    POPULARITY = "POPULARITY"
    EXPOSURE_BALANCED = "EXPOSURE_BALANCED"


@dataclass(frozen=True)
class SequentialSettings:
    T: int = 20  # rounds
    k: int = 5  # slate length (candidates)
    delta: float = 0.5  # exposure cap slack (EXPOSURE_BALANCED only)

    def __post_init__(self) -> None:
        for name in ("T", "k"):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, (int, np.integer)):
                raise InvalidInputError(f"{name} must be an integer, got {v!r}")
        if self.T < 0:
            raise InvalidInputError(f"T must be >= 0, got {self.T}")
        if self.k < 1:
            raise InvalidInputError(f"k must be >= 1, got {self.k}")
        if isinstance(self.delta, bool) or not math.isfinite(float(self.delta)) or self.delta < 0:
            raise InvalidInputError(f"delta must be a finite number >= 0, got {self.delta!r}")


@dataclass(frozen=True)
class SequentialSeeds:
    """Seed sequences for the three per-instance streams; shared by all sequential arms."""

    viewer_order: np.random.SeedSequence
    slate_keys: np.random.SeedSequence
    tie_keys: np.random.SeedSequence

    @staticmethod
    def from_parent(parent: np.random.SeedSequence) -> "SequentialSeeds":
        a, b, c = parent.spawn(3)
        return SequentialSeeds(a, b, c)


@dataclass
class SequentialOutcome:
    match_a: np.ndarray
    match_b: np.ndarray
    exposure_a: np.ndarray  # number of slates in which each A agent appeared
    exposure_b: np.ndarray
    n_slates: int = 0  # slates served (including empty ones)
    short_slates: int = 0  # slates with fewer than k candidates, any cause
    cap_short_slates: int = 0  # slates shortened by the exposure cap (EXPOSURE_BALANCED only)
    matches_by_round: list[int] = field(default_factory=list)


def exposure_cap(k: int, delta: float, n_viewers: int, n_candidates: int) -> int:
    """c = ceil((1 + delta) * k * V / C); 0 when there is no candidate."""
    if n_candidates <= 0:
        return 0
    return int(math.ceil((1.0 + delta) * k * n_viewers / n_candidates))


def _select(
    policy: Policy,
    eligible: np.ndarray,
    k: int,
    random_keys_row: np.ndarray,
    score: np.ndarray,
    tie: np.ndarray,
) -> np.ndarray:
    if eligible.size == 0:
        return eligible
    if policy is Policy.RANDOM:
        order = np.argsort(random_keys_row[eligible], kind="stable")
    else:
        order = np.lexsort((tie[eligible], -score[eligible]))
    return eligible[order[:k]]


def simulate_sequential(
    market: Market, policy: Policy | str, settings: SequentialSettings, seeds: SequentialSeeds
) -> SequentialOutcome:
    policy = Policy(policy)
    n = (market.n_a, market.n_b)
    acc = (market.acc_a, market.acc_b)
    sat = (market.sat_a, market.sat_b)
    seen = [np.zeros((n[0], n[1]), dtype=bool), np.zeros((n[1], n[0]), dtype=bool)]
    like = [np.zeros((n[0], n[1]), dtype=bool), np.zeros((n[1], n[0]), dtype=bool)]
    likes_received = [np.zeros(n[0], dtype=np.int64), np.zeros(n[1], dtype=np.int64)]
    exposure = [np.zeros(n[0], dtype=np.int64), np.zeros(n[1], dtype=np.int64)]
    match = [np.full(n[0], -1, dtype=np.int64), np.full(n[1], -1, dtype=np.int64)]
    out = SequentialOutcome(match[0], match[1], exposure[0], exposure[1])

    order_rng = np.random.default_rng(seeds.viewer_order)
    key_rng = np.random.default_rng(seeds.slate_keys)
    tie_rng = np.random.default_rng(seeds.tie_keys)
    k = settings.k

    for _t in range(settings.T):
        perm = order_rng.permutation(n[0] + n[1])
        rand_keys = (key_rng.random((n[0], n[1])), key_rng.random((n[1], n[0])))
        tie_keys = (tie_rng.random(n[0]), tie_rng.random(n[1]))  # per candidate on each side
        unmatched = (match[0] < 0, match[1] < 0)
        score = tuple((likes_received[s] + 1) / (exposure[s] + 2) for s in (0, 1))
        cap = (
            exposure_cap(k, settings.delta, int(unmatched[0].sum()), int(unmatched[1].sum())),
            exposure_cap(k, settings.delta, int(unmatched[1].sum()), int(unmatched[0].sum())),
        )  # cap[s]: per-candidate cap on side 1-s when side s views
        round_count = [np.zeros(n[0], dtype=np.int64), np.zeros(n[1], dtype=np.int64)]

        for v in perm:
            s = 0 if v < n[0] else 1
            i = int(v) if s == 0 else int(v) - n[0]
            o = 1 - s
            if not unmatched[s][i]:
                continue
            base = np.flatnonzero(unmatched[o] & ~seen[s][i])
            if policy is Policy.EXPOSURE_BALANCED:
                eligible = base[round_count[o][base] < cap[s]]
            else:
                eligible = base
            chosen = _select(policy, eligible, k, rand_keys[s][i], score[o], tie_keys[o])
            out.n_slates += 1
            if len(chosen) < k:
                out.short_slates += 1
                if policy is Policy.EXPOSURE_BALANCED and len(chosen) < min(k, len(base)):
                    out.cap_short_slates += 1
            if len(chosen) == 0:
                continue
            seen[s][i, chosen] = True
            exposure[o][chosen] += 1
            round_count[o][chosen] += 1
            liked = chosen[acc[s][i, chosen]]
            like[s][i, liked] = True
            likes_received[o][liked] += 1

        # end-of-round resolution of mutual likes among unmatched agents
        mutual = like[0] & like[1].T & unmatched[0][:, None] & unmatched[1][None, :]
        ii, jj = np.nonzero(mutual)
        new = 0
        if ii.size:
            w = sat[0][ii, jj] + sat[1][jj, ii]
            order = np.lexsort((jj, ii, -w))
            for idx in order:
                a, b = int(ii[idx]), int(jj[idx])
                if match[0][a] < 0 and match[1][b] < 0:
                    match[0][a], match[1][b] = b, a
                    new += 1
        out.matches_by_round.append(new)
    return out
