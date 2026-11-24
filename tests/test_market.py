# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Market generator: shapes, units, determinism, satisfaction and acceptability, invalid inputs."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from match_lab.errors import InvalidInputError
from match_lab.market import (MarketParams, acceptability_from_utilities, generate_market, side_size,
                              satisfaction_from_utilities)


def ss(x=1):
    return np.random.SeedSequence(x)


def test_side_size_rounds_half_up():
    assert side_size(200, 1.1) == 220
    assert side_size(200, 1.5) == 300
    assert side_size(50, 1.5) == 75
    assert side_size(5, 1.1) == 6  # 5.5 rounds up, not to even
    assert side_size(0, 1.5) == 0


def test_shapes_and_ranges():
    m = generate_market(MarketParams(20, 1.5, 0.5, 0.5), ss())
    assert m.u_a.shape == (20, 30) and m.u_b.shape == (30, 20)
    for sat in (m.sat_a, m.sat_b):
        assert sat.min() == 0.0 and sat.max() == 1.0
        # each row is a permutation of the evenly spaced grid
        n = sat.shape[1]
        assert np.allclose(np.sort(sat, axis=1), np.linspace(0, 1, n)[None, :])
    # theta = 0.5 accepts exactly half of an even-sized other side
    assert np.all(m.acc_a.sum(axis=1) == 15)
    assert np.all(m.acc_b.sum(axis=1) == 10)


def test_determinism_and_seed_sensitivity():
    p = MarketParams(10, 1.0, 0.3, 0.5)
    a, b, c = generate_market(p, ss(7)), generate_market(p, ss(7)), generate_market(p, ss(8))
    assert np.array_equal(a.u_a, b.u_a) and np.array_equal(a.u_b, b.u_b)
    assert not np.array_equal(a.u_a, c.u_a)


def test_theta_does_not_change_utilities():
    a = generate_market(MarketParams(10, 1.5, 0.5, 0.3), ss(3))
    b = generate_market(MarketParams(10, 1.5, 0.5, 0.7), ss(3))
    assert np.array_equal(a.u_a, b.u_a)
    assert a.acc_a.sum() > b.acc_a.sum()


def test_rho_one_gives_consensus_rankings():
    m = generate_market(MarketParams(8, 1.0, 1.0, 0.5), ss(4))
    assert np.all(m.sat_a == m.sat_a[0])  # every A agent ranks B identically
    assert np.array_equal(np.argsort(-m.u_a[0]), np.argsort(-m.q_b))


def test_rho_zero_ignores_quality():
    m = generate_market(MarketParams(5, 1.0, 0.0, 0.5), ss(5))
    # utilities are pure idiosyncratic noise: q does not enter
    rng = np.random.default_rng(ss(5))
    rng.standard_normal(5), rng.standard_normal(5)
    assert np.allclose(m.u_a, rng.standard_normal((5, 5)))


def test_preference_correlation_matches_rho():
    m = generate_market(MarketParams(400, 1.0, 0.5, 0.5), ss(6))
    c = np.corrcoef(m.u_a[:, :].T[:, :2].T)[0, 1]  # two viewers' utilities over 400 candidates
    assert abs(c - 0.5) < 0.12


def test_satisfaction_hand_example_and_ties():
    s = satisfaction_from_utilities(np.array([[3.0, 1.0, 2.0], [1.0, 1.0, 0.0]]))
    assert np.allclose(s[0], [1.0, 0.0, 0.5])
    assert np.allclose(s[1], [1.0, 0.5, 0.0])  # tie broken by lower index
    assert np.allclose(satisfaction_from_utilities(np.array([[5.0]])), [[1.0]])
    assert satisfaction_from_utilities(np.zeros((0, 3))).shape == (0, 3)


def test_acceptability_hand_example():
    u = np.array([[4.0, 1.0, 3.0, 2.0]])
    assert acceptability_from_utilities(u, 0.5).tolist() == [[True, False, True, False]]
    assert acceptability_from_utilities(u, 0.0).all()
    assert acceptability_from_utilities(u, 1.0).tolist() == [[True, False, False, False]]


def test_empty_markets():
    m = generate_market(MarketParams(0, 1.5, 0.5, 0.5), ss())
    assert m.n_a == 0 and m.n_b == 0 and m.u_a.shape == (0, 0)
    m1 = generate_market(MarketParams(1, 1.0, 0.5, 0.5), ss())
    assert m1.sat_a.tolist() == [[1.0]] and m1.acc_a.tolist() == [[True]]


@pytest.mark.parametrize("kwargs", [
    dict(n_a=-1, r=1.0, rho=0.5, theta=0.5), dict(n_a=2.5, r=1.0, rho=0.5, theta=0.5),
    dict(n_a=True, r=1.0, rho=0.5, theta=0.5), dict(n_a=5, r=0.9, rho=0.5, theta=0.5),
    dict(n_a=5, r=1.0, rho=1.5, theta=0.5), dict(n_a=5, r=1.0, rho=-0.1, theta=0.5),
    dict(n_a=5, r=1.0, rho=0.5, theta=1.2), dict(n_a=5, r=math.nan, rho=0.5, theta=0.5),
    dict(n_a=5, r=math.inf, rho=0.5, theta=0.5), dict(n_a=5, r="1", rho=0.5, theta=0.5),
])
def test_invalid_params_rejected(kwargs):
    with pytest.raises(InvalidInputError):
        MarketParams(**kwargs)


def test_invalid_seed_and_utilities_rejected():
    with pytest.raises(InvalidInputError):
        generate_market(MarketParams(3, 1.0, 0.5, 0.5), 42)
    with pytest.raises(InvalidInputError):
        satisfaction_from_utilities(np.array([[np.nan, 1.0]]))
    with pytest.raises(InvalidInputError):
        satisfaction_from_utilities(np.array([1.0, 2.0]))
    with pytest.raises(InvalidInputError):
        acceptability_from_utilities(np.ones((2, 2)), 2.0)


@settings(max_examples=60, deadline=None)
@given(n_a=st.integers(0, 12), r=st.sampled_from([1.0, 1.1, 1.5, 2.0]), rho=st.floats(0, 1),
       theta=st.floats(0, 1), seed=st.integers(0, 2**32 - 1))
def test_generator_invariants(n_a, r, rho, theta, seed):
    m = generate_market(MarketParams(n_a, r, rho, theta), ss(seed))
    assert m.n_b == side_size(n_a, r)
    for sat, acc in ((m.sat_a, m.acc_a), (m.sat_b, m.acc_b)):
        assert np.all((sat >= 0) & (sat <= 1))
        if sat.shape[1]:
            assert np.all(acc.sum(axis=1) >= 1)  # the best partner is always acceptable
            # acceptability is upward closed in satisfaction
            for row_s, row_a in zip(sat, acc):
                if row_a.any() and (~row_a).any():
                    assert row_s[row_a].min() > row_s[~row_a].max()
