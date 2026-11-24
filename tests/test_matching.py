# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Gale and Shapley deferred acceptance and MAXW: hand examples, stability, optimality,
differential tests against brute force, validity checks, empty pools, invalid inputs."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from helpers import all_matchings, brute_force_blocking, market_from_prefs, to_match_b
from match_lab.errors import InvalidInputError, InvalidMatchingError
from match_lab.market import MarketParams, generate_market
from match_lab.matching import (da_a, da_b, deferred_acceptance, max_weight, require_valid_matching,
                                validate_matching)
from match_lab.metrics import blocking_pairs


def test_gs_hand_example_unique_stable_matching():
    # Worked by hand in the M2 progress entry: A-proposing DA gives a0-b1, a1-b0, a2-b2.
    pa = [[0, 1, 2], [0, 2, 1], [1, 0, 2]]
    pb = [[1, 0, 2], [0, 2, 1], [0, 1, 2]]
    mp, mr = deferred_acceptance(pa, pb)
    assert mp.tolist() == [1, 0, 2] and mr.tolist() == [1, 0, 2]
    # receiver-proposing gives the same matching here (it is the unique stable matching)
    mr2, mp2 = deferred_acceptance(pb, pa)
    assert mp2.tolist() == [1, 0, 2]


def test_gs_proposer_optimality_two_by_two():
    # a0: b0 > b1, a1: b1 > b0; b0: a1 > a0, b1: a0 > a1. Two stable matchings.
    m = market_from_prefs([[0, 1], [1, 0]], [[1, 0], [0, 1]])
    ma, mb = da_a(m)
    assert ma.tolist() == [0, 1]  # A-optimal: each A agent gets its first choice
    ma2, mb2 = da_b(m)
    assert ma2.tolist() == [1, 0] and mb2.tolist() == [1, 0]  # B-optimal
    assert blocking_pairs(m, ma, mb) == 0 and blocking_pairs(m, ma2, mb2) == 0


def test_gs_truncated_lists():
    # a0 accepts only b0, but b0 does not accept a0; a1 accepts b0 and b0 accepts a1.
    mp, mr = deferred_acceptance([[0], [0]], [[1]])
    assert mp.tolist() == [-1, 0] and mr.tolist() == [1]
    # nobody acceptable
    mp, mr = deferred_acceptance([[], []], [[], [], []])
    assert mp.tolist() == [-1, -1] and mr.tolist() == [-1, -1, -1]


def test_gs_unbalanced_short_side_all_matched():
    pa = [[0, 1, 2], [0, 1, 2]]
    pb = [[0, 1], [1, 0], [0, 1]]
    mp, mr = deferred_acceptance(pa, pb)
    assert mp.tolist() == [0, 1] and sorted(mr.tolist()) == [-1, 0, 1]


def test_empty_pools():
    for n_a in (0,):
        m = generate_market(MarketParams(n_a, 1.5, 0.5, 0.5), np.random.SeedSequence(1))
        for f in (da_a, da_b, max_weight):
            ma, mb = f(m)
            assert ma.size == 0 and mb.size == 0
    assert [x.tolist() for x in deferred_acceptance([], [])] == [[], []]
    mp, mr = deferred_acceptance([[], []], [])
    assert mp.tolist() == [-1, -1] and mr.tolist() == []


@pytest.mark.parametrize("pa,pb", [
    ([[0, 0]], [[0]]),       # duplicate entry
    ([[1]], [[0]]),          # out of range
    ([[-1]], [[0]]),         # negative
    ([[0.5]], [[0]]),        # non-integer
    ([[True]], [[0]]),       # bool is not an index
])
def test_da_invalid_inputs(pa, pb):
    with pytest.raises(InvalidInputError):
        deferred_acceptance(pa, pb)


def test_validate_matching_detects_violations():
    assert validate_matching(np.array([0, 1]), np.array([0, 1])) == []
    assert any("duplicate" in f for f in validate_matching(np.array([0, 0]), np.array([0, -1])))
    assert any("inconsistent" in f for f in validate_matching(np.array([1, -1]), np.array([-1, -1])))
    assert any("out of range" in f for f in validate_matching(np.array([5]), np.array([-1])))
    assert validate_matching(np.array([0.0]), np.array([0.0])) == ["matching arrays are not integer typed"]
    acc_a = np.array([[True]]); acc_b = np.array([[False]])
    assert any("not mutually acceptable" in f for f in validate_matching(np.array([0]), np.array([0]), acc_a, acc_b))
    m = market_from_prefs([[0]], [[0]])
    with pytest.raises(InvalidMatchingError):
        require_valid_matching(np.array([0, 0][:1]), np.array([-1]), m)


def _stable_matchings(m):
    allowed = m.acc_a & m.acc_b.T
    out = []
    for ma in all_matchings(allowed):
        mb = to_match_b(ma, m.n_b)
        if brute_force_blocking(m, ma, mb) == 0:
            out.append(ma)
    return out


def _value(sat_row, j):
    return -1.0 if j < 0 else sat_row[j]


@settings(max_examples=120, deadline=None)
@given(n_a=st.integers(1, 4), r=st.sampled_from([1.0, 1.25, 1.5]), rho=st.sampled_from([0.0, 0.5, 0.9, 1.0]),
       theta=st.sampled_from([0.0, 0.3, 0.5]), seed=st.integers(0, 2**32 - 1))
def test_da_stable_and_optimal_vs_brute_force(n_a, r, rho, theta, seed):
    m = generate_market(MarketParams(n_a, r, rho, theta), np.random.SeedSequence(seed))
    stable = _stable_matchings(m)
    assert stable, "a stable matching always exists"
    for f, side in ((da_a, "A"), (da_b, "B")):
        ma, mb = f(m)
        assert validate_matching(ma, mb, m.acc_a, m.acc_b) == []
        assert blocking_pairs(m, ma, mb) == 0 == brute_force_blocking(m, ma, mb)
        assert any(np.array_equal(ma, s) for s in stable)
        # proposer optimality: each proposer weakly prefers its DA partner to any stable partner
        for s in stable:
            sb = to_match_b(s, m.n_b)
            if side == "A":
                assert all(_value(m.sat_a[i], ma[i]) >= _value(m.sat_a[i], s[i]) for i in range(m.n_a))
            else:
                assert all(_value(m.sat_b[j], mb[j]) >= _value(m.sat_b[j], sb[j]) for j in range(m.n_b))
    # rural hospitals: the set of matched agents is the same in every stable matching
    matched = {tuple(np.flatnonzero(s >= 0)) for s in stable}
    assert len(matched) == 1


@settings(max_examples=120, deadline=None)
@given(n_a=st.integers(1, 4), r=st.sampled_from([1.0, 1.25, 1.5]), rho=st.sampled_from([0.0, 0.5, 0.9]),
       theta=st.sampled_from([0.0, 0.5]), seed=st.integers(0, 2**32 - 1))
def test_maxw_equals_brute_force_optimum(n_a, r, rho, theta, seed):
    m = generate_market(MarketParams(n_a, r, rho, theta), np.random.SeedSequence(seed))
    allowed = m.acc_a & m.acc_b.T
    w = m.sat_a + m.sat_b.T
    best = max(sum(w[i, j] for i, j in enumerate(ma) if j >= 0) for ma in all_matchings(allowed))
    ma, mb = max_weight(m)
    assert validate_matching(ma, mb, m.acc_a, m.acc_b) == []
    got = sum(w[i, j] for i, j in enumerate(ma) if j >= 0)
    assert got == pytest.approx(best, abs=1e-9)


def test_maxw_unstable_hand_example():
    # Hand-computed (3 x 3, full acceptability). Every A agent ranks b0 > b1 > b2, so
    # s_A(b0, b1, b2) = (1, 0.5, 0). B lists: b0: a0 > a1 > a2; b1: a0 > a2 > a1; b2: a2 > a0 > a1.
    # Weights w_ij = s_ij + s_ji:
    #   a0: (2, 1.5, 0.5); a1: (1.5, 0.5, 0); a2: (1, 1, 1).
    # Totals over the 6 perfect matchings: (0,1,2) 3.5, (0,2,1) 3, (1,0,2) 4, (1,2,0) 2.5,
    # (2,0,1) 3, (2,1,0) 2. MAXW is the unique optimum a0-b1, a1-b0, a2-b2 (total 4), in
    # which (a0, b0) blocks. DA_A: all propose to b0, b0 keeps a0; a1 then a2 propose to b1,
    # b1 keeps a2; a1 goes to b2. DA_A = a0-b0, a1-b2, a2-b1 (total 3, stable).
    m = market_from_prefs([[0, 1, 2]] * 3, [[0, 1, 2], [0, 2, 1], [2, 0, 1]])
    w = m.sat_a + m.sat_b.T
    assert np.allclose(w, [[2, 1.5, 0.5], [1.5, 0.5, 0], [1, 1, 1]])
    ma, mb = max_weight(m)
    assert ma.tolist() == [1, 0, 2]
    assert blocking_pairs(m, ma, mb) == 1
    da, db = da_a(m)
    assert da.tolist() == [0, 2, 1] and blocking_pairs(m, da, db) == 0
