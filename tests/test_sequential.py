# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Sequential discovery: hand examples, invariants, determinism, exposure cap, common random
numbers (differential test across policies when slates are unconstrained), invalid inputs."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from helpers import market_from_prefs
from match_lab.errors import InvalidInputError
from match_lab.market import MarketParams, build_market, generate_market
from match_lab.matching import validate_matching
from match_lab.sequential import (Policy, SequentialSeeds, SequentialSettings, exposure_cap,
                                  simulate_sequential)

POLICIES = list(Policy)


def seeds(x=0):
    return SequentialSeeds.from_parent(np.random.SeedSequence(x))


def test_one_by_one_market_matches_in_round_one():
    m = market_from_prefs([[0]], [[0]])
    for p in POLICIES:
        out = simulate_sequential(m, p, SequentialSettings(T=1, k=5), seeds())
        assert out.match_a.tolist() == [0] and out.match_b.tolist() == [0]
        assert out.matches_by_round == [1]
        assert out.exposure_a.tolist() == [1] and out.exposure_b.tolist() == [1]
        assert out.n_slates == 2 and out.short_slates == 2  # each slate has 1 < k candidates


def test_greedy_resolution_prefers_higher_joint_satisfaction():
    # a0 ranks b0 > b1; each B agent has only a0, so s_b = 1. Joint: b0 -> 2, b1 -> 1.
    params = MarketParams(n_a=1, r=2.0, rho=0.0, theta=0.0)
    m = build_market(params, np.zeros(1), np.zeros(2), np.array([[2.0, 1.0]]), np.array([[1.0], [1.0]]))
    for p in POLICIES:
        out = simulate_sequential(m, p, SequentialSettings(T=1, k=5), seeds(3))
        assert out.match_a.tolist() == [0] and out.match_b.tolist() == [0, -1]


def test_no_like_without_acceptability():
    # theta = 1: each agent accepts only its top choice. a0 and a1 both want b0; b0 wants a1;
    # b1 wants a0 but a0 does not accept b1. Only a1-b0 can match.
    m = market_from_prefs([[0, 1], [0, 1]], [[1, 0], [0, 1]], theta=1.0)
    for p in POLICIES:
        out = simulate_sequential(m, p, SequentialSettings(T=5, k=5), seeds())
        assert out.match_a.tolist() == [-1, 0]


def test_zero_rounds_and_empty_market():
    m = generate_market(MarketParams(10, 1.5, 0.5, 0.5), np.random.SeedSequence(1))
    out = simulate_sequential(m, "RANDOM", SequentialSettings(T=0), seeds())
    assert (out.match_a == -1).all() and out.n_slates == 0 and out.matches_by_round == []
    empty = generate_market(MarketParams(0, 1.0, 0.5, 0.5), np.random.SeedSequence(1))
    for p in POLICIES:
        out = simulate_sequential(empty, p, SequentialSettings(T=3), seeds())
        assert out.match_a.size == 0 and out.matches_by_round == [0, 0, 0]


def test_exposure_cap_formula():
    assert exposure_cap(5, 0.5, 200, 300) == 5  # ceil(1.5 * 5 * 200 / 300) = ceil(5.0)
    assert exposure_cap(5, 0.5, 300, 200) == 12  # ceil(11.25)
    assert exposure_cap(5, 0.5, 10, 0) == 0
    assert exposure_cap(5, 0.0, 0, 10) == 0


@pytest.mark.parametrize("kw", [dict(tie_scope="row"), dict(T=-1), dict(k=0), dict(T=1.5), dict(k=True), dict(delta=-0.1),
                                dict(delta=float("nan"))])
def test_invalid_settings(kw):
    with pytest.raises(InvalidInputError):
        SequentialSettings(**kw)


def test_invalid_policy():
    m = market_from_prefs([[0]], [[0]])
    with pytest.raises(ValueError):
        simulate_sequential(m, "GREEDY", SequentialSettings(), seeds())


def test_exposure_cap_respected_in_one_round():
    m = generate_market(MarketParams(30, 1.5, 0.9, 0.5), np.random.SeedSequence(11))
    out = simulate_sequential(m, Policy.EXPOSURE_BALANCED, SequentialSettings(T=1, k=5, delta=0.0),
                              seeds(11))
    cap_b = exposure_cap(5, 0.0, 30, 45)  # A viewers -> B candidates
    cap_a = exposure_cap(5, 0.0, 45, 30)
    assert out.exposure_b.max() <= cap_b and out.exposure_a.max() <= cap_a
    pop = simulate_sequential(m, Policy.POPULARITY, SequentialSettings(T=1, k=5), seeds(11))
    # without the cap, round-one popularity slates concentrate on the same few candidates
    assert pop.exposure_b.max() == 30


@settings(max_examples=40, deadline=None)
@given(n_a=st.integers(1, 15), r=st.sampled_from([1.0, 1.1, 1.5]), rho=st.sampled_from([0.0, 0.5, 0.9]),
       theta=st.sampled_from([0.0, 0.5, 0.7]), T=st.integers(0, 6), k=st.integers(1, 6),
       seed=st.integers(0, 2**32 - 1), policy=st.sampled_from(POLICIES))
def test_sequential_invariants(n_a, r, rho, theta, T, k, seed, policy):
    m = generate_market(MarketParams(n_a, r, rho, theta), np.random.SeedSequence(seed))
    out = simulate_sequential(m, policy, SequentialSettings(T=T, k=k), seeds(seed))
    assert validate_matching(out.match_a, out.match_b, m.acc_a, m.acc_b) == []
    assert sum(out.matches_by_round) == int((out.match_a >= 0).sum())
    # each viewer sees each candidate at most once overall, so exposure <= other side size
    assert out.exposure_b.max(initial=0) <= m.n_a + 0 and out.exposure_a.max(initial=0) <= m.n_b
    # total exposure cannot exceed slates * k
    assert out.exposure_a.sum() + out.exposure_b.sum() <= out.n_slates * k
    assert out.cap_short_slates <= out.short_slates <= out.n_slates
    if policy is not Policy.EXPOSURE_BALANCED:
        assert out.cap_short_slates == 0
    again = simulate_sequential(m, policy, SequentialSettings(T=T, k=k), seeds(seed))
    assert np.array_equal(out.match_a, again.match_a) and out.matches_by_round == again.matches_by_round


@settings(max_examples=30, deadline=None)
@given(n_a=st.integers(1, 12), r=st.sampled_from([1.0, 1.5]), rho=st.sampled_from([0.0, 0.9]),
       T=st.integers(1, 4), seed=st.integers(0, 2**32 - 1))
def test_policies_coincide_when_slates_show_everything(n_a, r, rho, T, seed):
    """Differential test: with k >= other-side size, every policy shows every eligible
    candidate, so seen sets, likes and matches must be identical across policies (the cap
    c = ceil(1.5 k V / C) >= V never binds)."""
    m = generate_market(MarketParams(n_a, r, rho, 0.5), np.random.SeedSequence(seed))
    k = max(m.n_a, m.n_b)
    outs = [simulate_sequential(m, p, SequentialSettings(T=T, k=k), seeds(seed)) for p in POLICIES]
    for o in outs[1:]:
        assert np.array_equal(o.match_a, outs[0].match_a)
        assert np.array_equal(o.exposure_a, outs[0].exposure_a)
        assert np.array_equal(o.exposure_b, outs[0].exposure_b)
    assert outs[2].cap_short_slates == 0


def test_common_random_numbers_viewer_order_shared():
    """Streams are consumed identically by all arms: re-running RANDOM after POPULARITY with the
    same seeds reproduces RANDOM exactly (no hidden shared state)."""
    m = generate_market(MarketParams(20, 1.1, 0.5, 0.5), np.random.SeedSequence(5))
    a = simulate_sequential(m, "RANDOM", SequentialSettings(), seeds(5))
    simulate_sequential(m, "POPULARITY", SequentialSettings(), seeds(5))
    b = simulate_sequential(m, "RANDOM", SequentialSettings(), seeds(5))
    assert np.array_equal(a.match_a, b.match_a) and np.array_equal(a.exposure_b, b.exposure_b)


def test_horizon_truncation_is_prefix_consistent():
    """T only truncates the same streams: the first rounds of a T=10 run equal a T=5 run."""
    m = generate_market(MarketParams(25, 1.5, 0.5, 0.5), np.random.SeedSequence(9))
    for p in POLICIES:
        short = simulate_sequential(m, p, SequentialSettings(T=5), seeds(9))
        long = simulate_sequential(m, p, SequentialSettings(T=10), seeds(9))
        assert long.matches_by_round[:5] == short.matches_by_round
        matched_short = np.flatnonzero(short.match_a >= 0)
        assert np.array_equal(long.match_a[matched_short], short.match_a[matched_short])


def test_tie_scope_viewer_spreads_round_one_popularity_exposure():
    """Round one: all scores equal 0.5, so slates are decided by tie keys alone. A global key
    gives every A viewer the same k candidates; per-viewer keys spread exposure."""
    m = generate_market(MarketParams(30, 1.0, 0.5, 0.5), np.random.SeedSequence(4))
    glob = simulate_sequential(m, "POPULARITY", SequentialSettings(T=1, k=5), seeds(4))
    view = simulate_sequential(m, "POPULARITY", SequentialSettings(T=1, k=5, tie_scope="viewer"), seeds(4))
    assert int((glob.exposure_b > 0).sum()) == 5
    assert int((view.exposure_b > 0).sum()) > 5
    # RANDOM ignores the tie scope entirely
    a = simulate_sequential(m, "RANDOM", SequentialSettings(T=3), seeds(4))
    b = simulate_sequential(m, "RANDOM", SequentialSettings(T=3, tie_scope="viewer"), seeds(4))
    assert np.array_equal(a.match_a, b.match_a)
