"""Contracts of the Ascella physical-model fits: the batched channel, planted recovery and the static gradient."""

from __future__ import annotations

import math
from typing import Any

import ascella_physical_models as models
import numpy as np
import qd_belenos_mesh as mesh

CONFIGURATIONS = 6
COLUMNS = 6
TOTAL = 1e6


def arch() -> list[tuple[str, int, Any]]:
    """A rectangular 12-mode mesh of two-coupler cells with one heater after each coupler."""
    out: list[tuple[str, int, Any]] = []
    for column in range(COLUMNS):
        for m in range(column % 2, models.MODES - 1, 2):
            for k in range(2):
                out.append(("bs", m, (1.45 + 0.01 * math.sin(column + m + k), 0.0, 0.0, 0.0, 0.0)))
                out.append(("ps", m + 1, 0.0))
    return out


def data(counts_from: dict[str, Any] | None = None) -> dict[str, Any]:
    layout = arch()
    heaters = sum(1 for kind, _, _ in layout if kind == "ps")
    phases = np.array(
        [[(1.7 * c + 0.9 * h + math.sin(c * h)) % (2 * math.pi) for h in range(heaters)] for c in range(CONFIGURATIONS)]
    )
    settings = 2 * CONFIGURATIONS
    out: dict[str, Any] = {
        "arch": layout,
        "couplers": np.array([value[0] for kind, _, value in layout if kind == "bs"]),
        "phases": phases,
        "sources": np.zeros(CONFIGURATIONS, dtype=int),
        "configuration": np.arange(settings) % CONFIGURATIONS,
        "keys": [(f"c{c}",) for c in range(CONFIGURATIONS)],
        "block": np.full((settings, models.LOGICAL), TOTAL / models.LOGICAL),
        "background": np.outer(np.arange(settings) % 3, [0.3, 0.3, 0.3, 0.1]),
    }
    if counts_from is not None:
        light = models.family_probabilities(out, str(counts_from["family"]), np.asarray(counts_from["values"]))
        # The background scales with the block total, so the expected counts keep the total they were built at.
        out["block"] = models.setting_probabilities(out, light) * TOTAL
    return out


def test_channel_matches_the_belenos_reference() -> None:
    d = data()
    p = models.channel(d["couplers"], d["arch"], d["phases"], d["sources"], 0.04, 0.0025)
    for c in range(CONFIGURATIONS):
        ref = mesh.channel(d["arch"], list(d["phases"][c]), 0, sigma=0.2, sigma_theta=0.05)[: models.MODES]
        if not np.allclose(p[c], ref, atol=1e-13):
            raise AssertionError((c, np.abs(p[c] - ref).max()))
    pure = models.channel(d["couplers"], d["arch"], d["phases"], d["sources"], 0.0, 0.0)
    ref = np.array([mesh.propagate(d["arch"], list(row), 0)[0][: models.MODES] for row in d["phases"]])
    if not np.allclose(pure, ref, atol=1e-13):
        raise AssertionError(np.abs(pure - ref).max())


def test_planted_heater_gain_is_recovered() -> None:
    planted = np.array([0.002, 0.02])
    values = models.fit_parameters(data({"family": "heater_gain", "values": planted}), "heater_gain")
    if not np.allclose(values, planted, atol=2e-4):
        raise AssertionError(values)


def test_nominal_counts_leave_every_noise_family_at_zero() -> None:
    d = data({"family": "nominal", "values": []})
    for family in ("dephasing", "coupler_noise"):
        values = models.fit_parameters(d, family)
        if np.abs(values).max() > 1e-6:
            raise AssertionError((family, values))


def test_adjoint_jacobian_matches_the_reference_and_finite_differences() -> None:
    d = data()
    p, dp = models.pure_jacobians(d["couplers"], d["arch"], d["phases"], d["sources"])
    ref_p, ref_dp = mesh.jacobians(d["arch"], d["phases"], list(d["sources"]))
    heaters = d["phases"].shape[1]
    if not np.allclose(p, ref_p[:, : models.MODES]) or not np.allclose(dp[:, :, :heaters], ref_dp[:, : models.MODES]):
        raise AssertionError("heater derivatives differ from qd_belenos_mesh.jacobians")
    step = 1e-6
    for b in (0, 9, len(d["couplers"]) - 1):
        up, down = d["couplers"].copy(), d["couplers"].copy()
        up[b] += step
        down[b] -= step
        numeric = (
            models.pure_jacobians(up, d["arch"], d["phases"], d["sources"])[0]
            - models.pure_jacobians(down, d["arch"], d["phases"], d["sources"])[0]
        ) / (2 * step)
        if not np.allclose(dp[:, :, heaters + b], numeric, atol=1e-8):
            raise AssertionError((b, np.abs(dp[:, :, heaters + b] - numeric).max()))


def test_static_gradient_matches_finite_differences() -> None:
    d = data({"family": "heater_gain", "values": [0.0, 0.03]})
    widths = models.prior_widths(d, 0.3, 0.1)
    free = widths > 0
    offsets = np.array([0.01 * math.cos(h) for h in range(int(free.sum()))])
    _, grad = models.static_objective(d, widths[free], free, offsets)
    step = 1e-6
    for h in (0, 7, 19, int(free.sum()) - 1):
        up, down = offsets.copy(), offsets.copy()
        up[h] += step
        down[h] -= step
        numeric = (
            models.static_objective(d, widths[free], free, up)[0]
            - models.static_objective(d, widths[free], free, down)[0]
        ) / (2 * step)
        if not math.isclose(grad[h], numeric, rel_tol=1e-4, abs_tol=1e-3):
            raise AssertionError((h, grad[h], numeric))


def test_background_is_added_to_the_configuration_light() -> None:
    d = data()
    light = np.tile([0.5, 0.0, 0.0, 0.5], (CONFIGURATIONS, 1))
    pi = models.setting_probabilities(d, light)
    expected = (TOTAL - d["background"].sum(axis=1))[:, None] * light[d["configuration"]] + d["background"]
    expected = expected / TOTAL
    if not np.allclose(pi, expected) or not np.allclose(pi.sum(axis=1), 1):
        raise AssertionError(pi)
