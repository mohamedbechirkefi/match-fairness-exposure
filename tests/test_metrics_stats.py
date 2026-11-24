# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Metrics and statistics: hand-computed values, bounds, edge cases, invalid inputs."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from helpers import brute_force_blocking, market_from_prefs
from match_lab.errors import InvalidInputError
from match_lab.market import MarketParams, generate_market
from match_lab.matching import da_a, max_weight
from match_lab.metrics import METRIC_NAMES, blocking_pairs, compute_metrics, gini, metric_failures
from match_lab.sequential import SequentialSeeds, SequentialSettings, simulate_sequential
from match_lab.stats import (bootstrap_ci, holm, mean_sd_dz, n_for_power, sign_flip_pvalue,
                             stratified_bootstrap_ci, stratified_mean)


def test_gini_hand_values():
    assert gini(np.array([1, 1, 1])) == pytest.approx(0.0)
    assert gini(np.array([0, 0, 3])) == pytest.approx(2 / 3)
    assert gini(np.array([1, 3])) == pytest.approx(0.25)  # sum|xi-xj| = 4, / (2 * 4 * 2)
    assert gini(np.array([0, 0])) == 0.0
    assert gini(np.array([])) is None
    with pytest.raises(ValueError):
        gini(np.array([-1, 2]))


def test_metrics_hand_example():
    # 2 x 3 market, full acceptability. a0: b0 > b1 > b2; a1: b1 > b0 > b2.
    # b0: a0 > a1; b1: a0 > a1; b2: a1 > a0. Matching a0-b1, a1-b0, b2 unmatched.
    m = market_from_prefs([[0, 1, 2], [1, 0, 2]], [[0, 1], [0, 1], [1, 0]])
    ma, mb = np.array([1, 0]), np.array([1, 0, -1])
    met = compute_metrics(m, ma, mb, np.array([2, 0]), np.array([1, 1, 0]))
    # s: a0 with b1 = 0.5; a1 with b0 = 0.5; b0 with a1 = 0; b1 with a0 = 1; b2 = 0.
    assert met["W"] == pytest.approx((0.5 + 0.5 + 0 + 1 + 0) / 5)
    assert met["W_A"] == pytest.approx(0.5) and met["W_B"] == pytest.approx(1 / 3)
    assert met["U"] == pytest.approx(1 / 5) and met["U_A"] == 0.0 and met["U_B"] == pytest.approx(1 / 3)
    assert met["M"] == pytest.approx((min(0.5, 1) + min(0.5, 0)) / 2)
    assert met["n_matched"] == 2
    # blocking pairs: (a0, b0): a0 prefers b0 (1 > 0.5), b0 prefers a0 (1 > 0) -> blocks.
    # (a1, b1): a1 prefers b1 (1 > 0.5), b1 has a0 (its first) -> no. (a1, b2): a1 0 < 0.5 -> no.
    # (a0, b2): a0 0 < 0.5 -> no.
    assert met["blocking_pairs"] == 1 == brute_force_blocking(m, ma, mb)
    assert met["blocking_per_100"] == pytest.approx(20.0)
    assert met["gini_exposure_A"] == pytest.approx(0.5) and met["gini_exposure_B"] == pytest.approx(1 / 3)
    assert metric_failures(met) == []


def test_metrics_empty_and_unmatched():
    m = generate_market(MarketParams(0, 1.0, 0.5, 0.5), np.random.SeedSequence(0))
    met = compute_metrics(m, np.array([], dtype=np.int64), np.array([], dtype=np.int64))
    assert set(met) == set(METRIC_NAMES)
    assert met["W"] is None and met["U"] is None and met["M"] is None and met["blocking_pairs"] == 0
    m2 = generate_market(MarketParams(4, 1.0, 0.5, 0.5), np.random.SeedSequence(0))
    met2 = compute_metrics(m2, np.full(4, -1), np.full(4, -1))
    assert met2["W"] == 0.0 and met2["U"] == 1.0 and met2["M"] is None
    assert met2["blocking_pairs"] == int((m2.acc_a & m2.acc_b.T).sum())


def test_metric_failures_flags_bad_values():
    assert metric_failures({"W": float("nan")}) == ["non-finite metric W"]
    assert metric_failures({"U": 1.5}) and metric_failures({"blocking_pairs": -1})
    assert metric_failures({"W_A_q_gap": -2.0})


@settings(max_examples=40, deadline=None)
@given(n_a=st.integers(1, 12), r=st.sampled_from([1.0, 1.5]), rho=st.floats(0, 1), seed=st.integers(0, 2**32 - 1))
def test_metric_bounds_and_blocking_vs_brute_force(n_a, r, rho, seed):
    m = generate_market(MarketParams(n_a, r, rho, 0.5), np.random.SeedSequence(seed))
    out = simulate_sequential(m, "POPULARITY", SequentialSettings(T=3), SequentialSeeds.from_parent(np.random.SeedSequence(seed)))
    for ma, mb, ea, eb in ((out.match_a, out.match_b, out.exposure_a, out.exposure_b), (*da_a(m), None, None),
                           (*max_weight(m), None, None)):
        met = compute_metrics(m, ma, mb, ea, eb)
        assert metric_failures(met) == []
        assert met["blocking_pairs"] == brute_force_blocking(m, ma, mb)
        assert met["U"] == pytest.approx(1 - 2 * met["n_matched"] / (m.n_a + m.n_b))
        n = m.n_a + m.n_b
        assert met["W"] == pytest.approx((met["W_A"] * m.n_a + met["W_B"] * m.n_b) / n)


def test_stats_hand_values():
    m, sd, dz = mean_sd_dz([1.0, 2.0, 3.0])
    assert (m, sd, dz) == (2.0, 1.0, 2.0)
    assert mean_sd_dz([5.0]) == (5.0, None, None)
    assert mean_sd_dz([1.0, 1.0])[2] is None
    rng = np.random.default_rng(0)
    assert bootstrap_ci([0.3] * 10, rng=rng) == pytest.approx((0.3, 0.3))
    assert stratified_mean({"a": [1.0, 3.0], "b": [10.0]}) == pytest.approx(6.0)  # equal cell weights
    assert stratified_bootstrap_ci({"a": [2.0, 2.0], "b": [4.0]}, rng=rng) == pytest.approx((3.0, 3.0))
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert holm([0.5, 0.9]) == pytest.approx([1.0, 1.0])
    assert n_for_power(1.0, 0.53) == 28  # ((1.96 + 0.8416) / 0.53)^2 = 27.94
    assert n_for_power(0.0, 0.01) == 0


def test_sign_flip_pvalue_behaviour():
    rng = np.random.default_rng(1)
    assert sign_flip_pvalue({"a": [0.0] * 5}, rng=rng, n_draws=200) == 1.0
    # 12 positive differences in one cell: only the all-positive and all-negative sign
    # vectors reach |mean| = 1, probability 2 / 4096, so p is about 0.0005
    p = sign_flip_pvalue({"a": [1.0] * 12}, rng=rng, n_draws=20_000)
    assert p < 0.005
    p_null = sign_flip_pvalue({"a": list(np.random.default_rng(2).standard_normal(40))}, rng=rng, n_draws=2000)
    assert 0.0 < p_null <= 1.0


def test_stats_invalid_inputs():
    rng = np.random.default_rng(0)
    for bad in ([], [math.nan], [[1.0]]):
        with pytest.raises(InvalidInputError):
            mean_sd_dz(bad)
    with pytest.raises(InvalidInputError):
        stratified_mean({})
    with pytest.raises(InvalidInputError):
        stratified_bootstrap_ci({}, rng=rng)
    with pytest.raises(InvalidInputError):
        holm([1.2])
    with pytest.raises(InvalidInputError):
        n_for_power(1.0, 0.0)


def test_blocking_pairs_after_da_is_zero_on_moderate_market():
    m = generate_market(MarketParams(60, 1.5, 0.5, 0.5), np.random.SeedSequence(42))
    ma, mb = da_a(m)
    assert blocking_pairs(m, ma, mb) == 0
