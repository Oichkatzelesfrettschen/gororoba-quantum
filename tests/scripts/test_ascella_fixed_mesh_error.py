"""Contracts of the fixed per-mesh error reading: the scatter form profiles one constant off every mesh's residual."""

from __future__ import annotations

import ascella_fixed_mesh_error as fixed
import numpy as np


def held_out_score(residual: np.ndarray, variance: np.ndarray) -> dict:
    rows = [
        {"observed": float(r), "predicted": 0.0, "counting_variance": float(v)}
        for r, v in zip(residual, variance, strict=True)
    ]
    return {"rows": rows, "median_variance_ratio": 0.5}


def test_scatter_form_is_the_weighted_residual_sum_about_the_fitted_constant() -> None:
    residual = np.array([0.3, -1.2, 0.8, 2.1, -0.4, 0.05])
    variance = np.array([0.6, 1.9, 1.1, 0.7, 1.4, 1.0])
    gradients = np.zeros((6, 1))
    out = fixed.scatter_form(held_out_score(residual, variance), gradients, np.zeros((1, 1)))
    weights = 1 / variance
    constant = float((weights * residual).sum() / weights.sum())
    expected = float((weights * (residual - constant) ** 2).sum())
    if abs(out["constant"] - constant) > 1e-12 or abs(out["quadratic_form"] - expected) > 1e-12:
        raise AssertionError(f"scatter form {out} departs from the weighted sum {expected} about {constant}")
    if out["degrees_of_freedom"] != 5:
        raise AssertionError("the free constant removes one degree of freedom")


def test_scatter_form_ignores_a_common_offset() -> None:
    residual = np.sin(np.arange(8.0))
    variance = np.full(8, 1.0)
    gradients = np.cos(np.arange(24.0)).reshape(8, 3)
    covariance = np.eye(3) * 0.1
    base = fixed.scatter_form(held_out_score(residual, variance), gradients, covariance)
    shifted = fixed.scatter_form(held_out_score(residual + 0.7, variance), gradients, covariance)
    if abs(base["quadratic_form"] - shifted["quadratic_form"]) > 1e-9:
        raise AssertionError("a common offset changes the scatter form")
