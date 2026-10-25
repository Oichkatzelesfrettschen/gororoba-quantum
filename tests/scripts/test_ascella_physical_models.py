"""Contracts of the Ascella physical-model fits: the batched channel, planted recovery, the static gradient, and the
training-only leave-one-configuration-out folds of scripts/ascella_configuration_holdout.py."""

from __future__ import annotations

import math
from typing import Any

import ascella_configuration_holdout as holdout
import ascella_physical_models as models
import numpy as np
import pytest
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


def test_static_light_without_slopes_is_the_offset_mesh() -> None:
    d = data()
    heaters = d["phases"].shape[1]
    widths = models.prior_widths(d, 0.3, 0.1)
    free = widths > 0
    offsets = np.array([0.01 * math.cos(h) for h in range(int(free.sum()))])
    light, dlight = models.static_light(d, offsets, free)
    p, dp = models.pure_jacobians(
        d["couplers"] + offsets[heaters:], d["arch"], d["phases"] + offsets[None, :heaters], d["sources"]
    )
    raw = np.clip(p[:, : models.LOGICAL], models.PROBABILITY_FLOOR, None)
    if not np.array_equal(light, raw / raw.sum(axis=1, keepdims=True)):
        raise AssertionError("the offset-only light differs from the offset mesh")
    if dlight.shape[2] != heaters + len(d["couplers"]):
        raise AssertionError(dlight.shape)


def test_drive_slope_jacobian_matches_finite_differences() -> None:
    d = data()
    heaters, couplers = d["phases"].shape[1], len(d["couplers"])
    widths = models.prior_widths(d, 0.3, None, 0.1)
    free = widths > 0
    if int(free.sum()) != 2 * heaters or len(widths) != 2 * heaters + couplers:
        raise AssertionError((int(free.sum()), len(widths)))
    params = np.array([0.02 * math.sin(i) for i in range(int(free.sum()))])
    light, dlight = models.static_light(d, params, free)
    # A slope k_h moves heater h by k_h phi, so it equals an offset of k_h phi on each configuration's heater.
    full = np.zeros(len(free))
    full[free] = params
    shifted = d["phases"] + full[None, :heaters] + full[None, heaters + couplers :] * d["phases"]
    p, _ = models.pure_jacobians(d["couplers"], d["arch"], shifted, d["sources"])
    raw = np.clip(p[:, : models.LOGICAL], models.PROBABILITY_FLOOR, None)
    if not np.allclose(light, raw / raw.sum(axis=1, keepdims=True), atol=1e-14):
        raise AssertionError("the sloped light differs from the shifted mesh")
    step = 1e-6
    for index in (heaters, heaters + 7, 2 * heaters - 1, 3):
        up, down = params.copy(), params.copy()
        up[index] += step
        down[index] -= step
        numeric = (models.static_light(d, up, free)[0] - models.static_light(d, down, free)[0]) / (2 * step)
        if not np.allclose(dlight[:, :, index], numeric, rtol=1e-5, atol=1e-8):
            raise AssertionError((index, np.abs(dlight[:, :, index] - numeric).max()))


def test_static_gradient_matches_finite_differences_where_cells_sit_on_the_floor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    d = data({"family": "heater_gain", "values": [0.0, 0.03]})
    widths = models.prior_widths(d, 0.3, None)
    free = widths > 0
    offsets = np.array([0.01 * math.cos(h) for h in range(int(free.sum()))])
    raw = models.pure_jacobians(d["couplers"], d["arch"], d["phases"], d["sources"])[0][:, : models.LOGICAL]
    # A floor between the smallest and largest block probabilities holds some cells and leaves the rest free.
    floor = float(np.quantile(raw, 0.25))
    monkeypatch.setattr(models, "PROBABILITY_FLOOR", floor)
    if not (raw < floor).any() or (raw < floor).all():
        raise AssertionError("the floor holds no cell or every cell")
    _, grad = models.static_objective(d, widths[free], free, offsets)
    step = 1e-7
    for h in range(int(free.sum())):
        up, down = offsets.copy(), offsets.copy()
        up[h] += step
        down[h] -= step
        numeric = (
            models.static_objective(d, widths[free], free, up)[0]
            - models.static_objective(d, widths[free], free, down)[0]
        ) / (2 * step)
        # The difference straddles the floor's kink for a heater that moves a cell across it.
        if abs(grad[h] - numeric) > 0.05 * max(1.0, abs(numeric)):
            raise AssertionError((h, grad[h], numeric))


def test_background_is_added_to_the_configuration_light() -> None:
    d = data()
    light = np.tile([0.5, 0.0, 0.0, 0.5], (CONFIGURATIONS, 1))
    pi = models.setting_probabilities(d, light)
    expected = (TOTAL - d["background"].sum(axis=1))[:, None] * light[d["configuration"]] + d["background"]
    expected = expected / TOTAL
    if not np.allclose(pi, expected) or not np.allclose(pi.sum(axis=1), 1):
        raise AssertionError(pi)


def test_fit_replay_bound_is_relative_for_small_values() -> None:
    variance = 4.92e-4
    models.replay(variance, variance * (1 + 5e-4), "phase_variance")
    with pytest.raises(ValueError, match="phase_variance"):
        models.replay(variance, 0.009, "phase_variance")
    models.replay(0.0, 5e-9, "offset")
    with pytest.raises(ValueError, match="offset"):
        models.replay(0.0, 5e-8, "offset")


def test_nominal_family_is_unfitted() -> None:
    if models.UNFITTED != ("nominal",) or models.FAMILIES["nominal"]:
        raise AssertionError(models.UNFITTED)


def test_posterior_hessian_is_the_symmetrized_column_loop() -> None:
    d = data({"family": "heater_gain", "values": [0.0, 0.03]})
    widths = models.prior_widths(d, 0.3, 0.1)
    free = widths > 0
    offsets = np.array([0.01 * math.sin(h) for h in range(int(free.sum()))])
    column = models.HessianColumn(d, widths[free], free, offsets)
    loop = np.stack([column(index) for index in range(len(offsets))], axis=1)
    hessian = models.posterior_hessian(d, widths[free], free, offsets)
    if not np.array_equal(hessian, (loop + loop.T) / 2) or not np.array_equal(hessian, hessian.T):
        raise AssertionError("the pooled Hessian differs from the column loop")


def scored(counts_from: dict[str, Any] | None = None) -> dict[str, Any]:
    """The synthetic run with settings that serve X then Y in every configuration."""
    d = data(counts_from)
    settings = len(d["configuration"])
    d["record"] = {
        "manifest": {
            "settings": [{"readout": "x" if s < CONFIGURATIONS else "y", "block": "analyzer"} for s in range(settings)]
        }
    }
    return d


def test_prediction_gradient_matches_finite_differences() -> None:
    d = scored({"family": "heater_gain", "values": [0.0, 0.03]})
    widths = models.prior_widths(d, None, 0.1)
    free = widths > 0
    offsets = np.array([0.02 * math.sin(k) for k in range(int(free.sum()))])
    light, dlight = models.static_light(d, offsets, free)
    step = 1e-6
    for (readout, _, model, _, gradient), column in zip(
        holdout.left_out_rows(d, light, dlight, 2), (0, 5), strict=False
    ):
        shifted = offsets.copy()
        shifted[column] += step
        moved = holdout.left_out_rows(d, models.static_light(d, shifted, free)[0], dlight, 2)
        numeric = (next(row[2] for row in moved if row[0] == readout) - model) / step
        if not math.isclose(gradient[column], numeric, rel_tol=1e-3, abs_tol=1e-7):
            raise AssertionError((readout, column, gradient[column], numeric))


def test_fold_fit_receives_the_training_configurations_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    d = scored({"family": "heater_gain", "values": [0.0, 0.03]})
    seen = []

    def mode(data: dict[str, Any], tau: np.ndarray, free: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        seen.append(data)
        return np.zeros(int(free.sum())), np.eye(int(free.sum()))

    monkeypatch.setattr(models, "static_mode", mode)
    fold = holdout.configuration_fold(("coupler", (None, 0.1), d, 2))
    (training,) = seen
    expected = models.without_configuration(d, 2)
    if training["keys"] != expected["keys"] or not np.array_equal(training["block"], expected["block"]):
        raise AssertionError("the fold fit saw more than the training configurations")
    if not fold["rows"]:
        raise AssertionError("the left-out configuration scored no readout")


@pytest.mark.audit
def test_left_out_counts_never_reach_the_fold_fit() -> None:
    d = scored({"family": "heater_gain", "values": [0.0, 0.03]})
    changed = scored({"family": "heater_gain", "values": [0.0, 0.03]})
    rows = changed["configuration"] == 2
    changed["block"][rows] = changed["block"][rows][:, ::-1]
    fold, moved = (holdout.configuration_fold(("coupler", (None, 0.1), run, 2)) for run in (d, changed))
    if fold["training_objective"] != moved["training_objective"]:
        raise AssertionError("the left-out configuration's counts changed the training fit")
    for a, b in zip(fold["rows"], moved["rows"], strict=True):
        if a["predicted"] != b["predicted"] or a["prediction_variance"] != b["prediction_variance"]:
            raise AssertionError((a, b))
        if a["observed"] == b["observed"]:
            raise AssertionError("the mutation left the observed statistic unchanged")
