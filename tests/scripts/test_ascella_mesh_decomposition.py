"""Contracts of the Ascella mesh decomposition: the background-subtracted block fractions' counting covariance."""

from __future__ import annotations

from typing import Any

import ascella_mesh_decomposition as decomposition
import numpy as np


def run(block: np.ndarray, outside: np.ndarray, dark: np.ndarray) -> dict[str, Any]:
    share = dark[:4] / dark[4:].sum()
    return {"record": {"dark": dark}, "block": block, "background": outside[:, None] * share[None, :]}


def test_without_outside_clicks_the_covariance_is_the_block_multinomial() -> None:
    dark = np.array([3, 4, 2, 1, 5, 8, 2, 9, 30, 25, 10, 4], dtype=float)
    block = np.array([[7400.0, 390.0, 4.0, 200.0]])
    covariance = decomposition.light_fraction_covariance(run(block, np.zeros(1), dark))[0]
    f = block[0] / block[0].sum()
    if not np.allclose(covariance, (np.diag(f) - np.outer(f, f)) / block[0].sum(), rtol=1e-12, atol=0):
        raise AssertionError(covariance)


def test_delta_method_matches_the_sampled_subtracted_fractions() -> None:
    dark = np.array([3, 4, 2, 1, 5, 8, 2, 9, 30, 25, 10, 4], dtype=float)
    share = dark[:4] / dark[4:].sum()
    probabilities = np.array([0.88, 0.05, 0.004, 0.025, 0.041])
    total = 8192
    expected = probabilities * total
    predicted = decomposition.light_fraction_covariance(run(expected[None, :4], expected[4:], dark))[0]
    # A fixed generator seed reproduces a contract test; it draws synthetic counts, never a scientific seed.
    generator = np.random.default_rng(np.random.SeedSequence(entropy=[int(x) for x in expected.astype(int)]))
    samples = generator.multinomial(total, probabilities, size=40000)
    light = samples[:, :4] - samples[:, 4:5] * share[None, :]
    fractions = light / light.sum(axis=1, keepdims=True)
    sampled = np.cov(fractions.T)
    if not np.allclose(sampled, predicted, rtol=0.05, atol=2e-8):
        raise AssertionError((sampled, predicted))
