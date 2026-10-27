"""The measurement-sequence successor's analysis core: gamma-rate fit, admission, shape bound, equilibrium estimator,
settle veto, carryover reader and order sentinel."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pytest

import measurement_sequence_analysis as msa
import msq_successor_analysis as su

# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-27T200026Z.json, index 0.
TEST_SEED = 585


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


DELAYS = [0.0, 20e-6, 50e-6, 100e-6, 200e-6]
WEIGHTS = [1e4] * 5
FEW = msa.FIXTURE_QUBITS[:3]
FLOOR = msa.DEMONSTRATION_SCATTER_FLOOR
SHOTS = msa.FIXTURE_SHOTS


def series(lifetime: float, shape: float) -> list[float]:
    return [float(v) for v in 1 - 2 * su.survival(np.array(DELAYS), lifetime, shape)]


def base_contexts(qubits: tuple[int, ...]) -> dict[int, dict[str, Any]]:
    planned = msa.fixture_contexts(qubits)
    return {
        q: {k: v for k, v in c.items() if k not in ("planning", "planning_se", "model_scatter_floor")}
        for q, c in planned.items()
    }


def contexts(qubits: tuple[int, ...] = FEW) -> dict[int, dict[str, Any]]:
    return su.with_planning(base_contexts(qubits), FLOOR)


def bare_contexts(qubits: tuple[int, ...] = FEW) -> dict[int, dict[str, Any]]:
    """Contexts with the planning tables and the floor but no planning standard error, so the informative filter
    keeps the analysis cheap for tests that read the rows and not the planning bound."""
    base = base_contexts(qubits)
    tables = su.planning_tables(base)
    return {q: {**c, "planning": tables[q], "model_scatter_floor": FLOOR} for q, c in base.items()}


# --- gamma-rate fit -----------------------------------------------------------------------------------------


@pytest.mark.parametrize(("lifetime", "shape"), [(250e-6, 3.0), (250e-6, 0.5), (150e-6, 40.0), (400e-6, 0.25)])
def test_fit_recovers_a_planted_gamma_truth(lifetime: float, shape: float) -> None:
    fit = su.fit_gamma_rate(DELAYS, series(lifetime, shape), WEIGHTS)
    check(abs(fit["t_s"] / lifetime - 1) < 1e-5, f"T {fit['t_s']} against {lifetime}")
    check(abs(fit["shape"] / shape - 1) < 1e-3, f"shape {fit['shape']} against {shape}")
    check(fit["chi2"] < 1e-8 and fit["dof"] == 2 and fit["p_value"] > 0.99, f"{fit}")


def test_fit_puts_an_exponential_truth_at_the_edge() -> None:
    fit = su.fit_gamma_rate(DELAYS, series(250e-6, su.EXPONENTIAL), WEIGHTS)
    check(math.isinf(fit["shape"]) and fit["exponential_edge"], f"shape {fit['shape']}")
    check(abs(fit["t_s"] / 250e-6 - 1) < 1e-5, f"T {fit['t_s']}")


def test_fit_fixes_the_initial_slope_across_shapes() -> None:
    # S'(0) = -1 / T for every shape: a series generated at T keeps T within a few percent when the shape is wrong.
    for shape in (0.5, 2.0, 16.0):
        fit = su.fit_gamma_rate(DELAYS, series(250e-6, shape), WEIGHTS)
        check(abs(fit["t_s"] / 250e-6 - 1) < 1e-4, f"shape {shape}: T {fit['t_s']}")


def test_fit_is_continuous_in_the_series() -> None:
    y0 = np.array(series(250e-6, 3.0)) + np.array([0.0, 0.002, -0.0015, 0.001, -0.002])
    for j in (1, 2, 3, 4):
        slopes = []
        for h in (1e-4, 1e-5, 1e-6):
            up, down = y0.copy(), y0.copy()
            up[j] += h
            down[j] -= h
            high = su.fit_gamma_rate(DELAYS, up.tolist(), WEIGHTS)["t_s"]
            low = su.fit_gamma_rate(DELAYS, down.tolist(), WEIGHTS)["t_s"]
            slopes.append((high - low) / (2 * h))
        spread = max(slopes) - min(slopes)
        check(spread < 0.01 * abs(slopes[1]), f"point {j}: finite differences {slopes}")


def test_masked_profile_search_follows_the_scalar_search() -> None:
    y = np.array(series(250e-6, 2.0)) + np.array([0.0, 0.001, -0.002, 0.0015, 0.0])
    t, ys, w = np.array(DELAYS[1:]), y[1:], np.array(WEIGHTS[1:])
    shapes = (*su.GAMMA_SHAPES[::12], su.EXPONENTIAL)
    for shape, (chi, lifetime) in zip(shapes, su._profiles(t, ys, w, shapes), strict=True):
        scalar_chi, scalar_t = su._profile(t, ys, w, shape)
        check(
            abs(chi - scalar_chi) <= 1e-12 * max(chi, 1e-30) + 1e-18, f"shape {shape}: chi2 {chi} against {scalar_chi}"
        )
        check(abs(lifetime / scalar_t - 1) < 1e-8, f"shape {shape}: T {lifetime} against {scalar_t}")


def test_fit_is_deterministic() -> None:
    y = (np.array(series(250e-6, 2.0)) + np.array([0.0, 0.001, -0.002, 0.0015, 0.0])).tolist()
    first = su.fit_gamma_rate(DELAYS, y, WEIGHTS)
    su._fit.cache_clear()
    second = su.fit_gamma_rate(DELAYS, y, WEIGHTS)
    check(first == second and first["t_s"].hex() == second["t_s"].hex(), "two fits of one series differ")


def test_fit_rejects_a_fast_decay_component() -> None:
    fast = [-1.0, 1 - 2 * 0.3, 1 - 2 * 0.05, 1.0, 1.0 - 0.01]
    fit = su.fit_gamma_rate(DELAYS, fast, [1e6] * 5)
    check(not su.admitted(fit["p_value"], 32), f"admitted {fit}")


def test_admission_threshold_scales_with_the_width() -> None:
    check(su.admitted(0.01 / 32, 32) and not su.admitted(0.01 / 32 * 0.99, 32))
    check(not su.admitted(None, 32))


# --- successor rows -----------------------------------------------------------------------------------------


def ground_counts(ctx_map: dict[int, dict[str, Any]], **over: Any) -> dict[int, dict[str, Any]]:
    models = {q: msa.device_model(c, p_init=0.0, **over) for q, c in ctx_map.items()}
    return msa.device_counts(models, ctx_map, SHOTS)


def test_rows_fit_a_ground_state_device_and_drop_the_q_fields() -> None:
    ctx_map = contexts()
    rows = su.evaluate(ground_counts(ctx_map), ctx_map)
    for q, row in rows.items():
        fitted = row["fitted"]
        check(row["usable"] and row["informative"], f"q{q}: {row.get('uninformative_reason')}")
        check(not {"q", "p_init", "p_init_se"} & set(fitted), f"q{q}: {sorted(fitted)}")
        check({"shape", "chi2", "dof", "p_value"} <= set(fitted), f"q{q}: {sorted(fitted)}")
        check(abs(fitted["t1_s"] / ctx_map[q]["t1_cal_s"] - 1) < 0.1, f"q{q}: T {fitted['t1_s']}")
        check(row["admission"]["passes"], f"q{q}: {row['admission']}")
        check(row["decisions"]["departure"]["outcome"] == "consistent", f"q{q}: {row['departure_n16']}")


def test_rows_detect_a_planted_departure() -> None:
    ctx_map = bare_contexts()
    rows = su.evaluate(ground_counts(ctx_map, eps=0.03, eps_settle=0.03), ctx_map)
    for q, row in rows.items():
        check(row["decisions"]["departure"]["outcome"] == "departs_below", f"q{q}: {row['departure_n16']}")
        check(row["decisions"]["mutation_test"]["passes"], f"q{q}: mutation")


def test_rows_leave_the_registered_analysis_alone() -> None:
    check(msa.MODEL_SCATTER_DIAGNOSTIC_SHA256 == "c39c5b7202fd6d2cd44629a86eed1402a0d234e95502540f37c8216bccc3c080")
    check("fit_t1" in msa.quantities.__code__.co_names, "the registered quantities keep the (T1, q) fit")
    check("fit_gamma_rate" in su.quantities.__code__.co_names and "fit_t1" not in su.quantities.__code__.co_names)


# --- shape systematic ---------------------------------------------------------------------------------------


def test_shape_systematic_is_single_signed_and_grows_toward_low_shape() -> None:
    ctx_map = contexts((msa.FIXTURE_QUBITS[0],))
    wide = su.shape_systematic({"contexts": ctx_map, "shapes": [0.25, 4.0], "t_points": 2})
    narrow = su.shape_systematic({"contexts": ctx_map, "shapes": [64.0], "t_points": 2})
    check(wide["single_signed"] and narrow["single_signed"], f"{wide}")
    check(0 < narrow["bound"] < wide["bound"] < 0.01, f"{narrow['bound']} {wide['bound']}")
    check(wide["maximum"] * wide["minimum"] >= 0, f"one sign over the domain: {wide['minimum']} {wide['maximum']}")


def test_shape_systematic_per_qubit_scope_reads_the_calibrated_lifetime() -> None:
    ctx_map = contexts((msa.FIXTURE_QUBITS[0],))
    ctx = ctx_map[msa.FIXTURE_QUBITS[0]]
    scoped = su.shape_systematic(
        {"contexts": ctx_map, "shapes": [0.25], "t_factor": 1.0, "t_points": 1, "t_scope": "qubit"}
    )
    direct = su.gamma_measure_p0(ctx, ctx["t1_cal_s"], 0.25) - su.gamma_measure_p0(ctx, ctx["t1_cal_s"], su.EXPONENTIAL)
    check(abs(scoped["bound"] - abs(direct)) < 1e-15 and scoped["t_scope"] == "qubit", f"{scoped} {direct}")
    with pytest.raises(msa.AnalysisError):
        su.shape_systematic({"contexts": ctx_map, "t_scope": "device"})


def test_shape_bounds_read_each_qubit_at_its_fitted_lifetime() -> None:
    ctx_map = bare_contexts(msa.FIXTURE_QUBITS[:2])
    rows = su.evaluate(ground_counts(ctx_map), ctx_map)
    bounds = su.shape_bounds(rows, ctx_map, (0.25, 4.0))
    for q, row in rows.items():
        t_s = row["fitted"]["t1_s"]
        exponential = su.gamma_measure_p0(ctx_map[q], t_s, su.EXPONENTIAL)
        direct = max(abs(su.gamma_measure_p0(ctx_map[q], t_s, k) - exponential) for k in (0.25, 4.0))
        check(abs(bounds[q] - direct) < 1e-15 and 0 < bounds[q] < 0.01, f"{q}: {bounds[q]} {direct}")
    with pytest.raises(msa.AnalysisError):
        su.shape_bounds(rows, ctx_map, (0.25, math.inf))


def test_shape_adjusted_adds_the_bound_to_the_shared_systematic_linearly() -> None:
    ctx_map = bare_contexts()
    rows = su.evaluate(ground_counts(ctx_map), ctx_map)
    adjusted = su.shape_adjusted(rows, dict.fromkeys(rows, 0.002))
    for q, row in rows.items():
        before = row["departure_n16"]["se_systematic"]
        check(abs(adjusted[q]["departure_n16"]["se_systematic"] - before - 0.002) < 1e-15)
        check(adjusted[q]["departure_n16"]["se"] == row["departure_n16"]["se"], "the per-qubit se moves")
    z0 = msa.pooled_z(
        [
            (
                r["departure_n16"]["difference"],
                r["departure_n16"]["se_statistical"],
                r["departure_n16"]["se_systematic"],
            )
            for r in rows.values()
        ]
    )
    z1 = msa.pooled_z(
        [
            (
                r["departure_n16"]["difference"],
                r["departure_n16"]["se_statistical"],
                r["departure_n16"]["se_systematic"],
            )
            for r in adjusted.values()
        ]
    )
    check(z0 is not None and z1 is not None and abs(z1) < abs(z0), f"{z0} {z1}")


# --- equilibrium estimator ----------------------------------------------------------------------------------


def equilibrium_obs(
    ctx: dict[str, Any], q: float, lifetime: float, shape: float = su.EXPONENTIAL
) -> dict[str, tuple[int, int]]:
    """Expected counts of a device that relaxes to z_eq = q from the ground state with the gamma survival S."""
    model = msa.device_model(ctx, p_init=0.0, p_thermal=(1 - q) / 2)
    wait = ctx["prereadout_s"]

    def ones(z: float) -> tuple[int, int]:
        return msa.expected_ones(z, 0.0, model, wait, SHOTS)

    def decay(t: float) -> float:
        return float(su.survival(np.array([t]), lifetime, shape)[0])

    obs = {"ro0": ones(1.0)}
    for k, t in enumerate(ctx["t1_delays_s"]):
        obs[f"t1-{k}"] = ones(q - (q + 1) * decay(t))
    obs["eq"] = ones(q + (1 - q) * decay(su.EQUILIBRIUM_DELAY_S))
    return obs


@pytest.mark.parametrize(("q", "shape"), [(1.0, su.EXPONENTIAL), (1.0, 3.0), (0.7, su.EXPONENTIAL), (0.7, 3.0)])
def test_equilibrium_estimate_recovers_the_planted_target(q: float, shape: float) -> None:
    ctx = contexts((msa.FIXTURE_QUBITS[0],))[msa.FIXTURE_QUBITS[0]]
    estimate = su.equilibrium_estimate(equilibrium_obs(ctx, q, 250e-6, shape), ctx)
    check(abs(estimate["q_hat"] - q) < 4 * estimate["se"] + 2e-3, f"{estimate}")
    check(0 < estimate["se"] < 0.02, f"{estimate}")
    screen = su.q_screen(estimate, su.q_sensitivity(ctx, estimate["t1_s"]), 32)
    check(screen["passes"] == (q == 1.0), f"q {q}: {screen}")


def test_q_hat_is_not_clipped_and_the_tolerance_follows_the_sensitivity() -> None:
    ctx = contexts((msa.FIXTURE_QUBITS[0],))[msa.FIXTURE_QUBITS[0]]
    sensitivity = su.q_sensitivity(ctx)
    check(0.02 < sensitivity < 0.07, f"|dP0/dq| {sensitivity}")
    estimate = {"q_hat": 1.004, "se": 0.001}
    screen = su.q_screen(estimate, sensitivity, 32)
    check(screen["lower_bound"] > 1 - 0.01 and screen["passes"], f"{screen}")
    check(abs(screen["tolerance"] - (1 - 0.25 * 0.0188 / sensitivity)) < 1e-15)
    steep = su.q_screen({"q_hat": 0.85, "se": 0.001}, 0.065, 32)
    flat = su.q_screen({"q_hat": 0.85, "se": 0.001}, 0.021, 32)
    check(not steep["passes"] and flat["passes"], "a qubit with the larger sensitivity has the tighter tolerance")


# --- settle veto --------------------------------------------------------------------------------------------


def gaps(count: int, shift: float, scatter: float = 0.0, se: float = 0.003) -> dict[int, tuple[float, float]]:
    generator = np.random.default_rng(TEST_SEED)
    noise = generator.standard_normal(count)
    return {q: (shift + scatter * float(noise[q]) + se * float(generator.standard_normal()), se) for q in range(count)}


def test_settle_veto_leaves_a_null_device_alone() -> None:
    veto = su.settle_veto(gaps(24, 0.0))
    check(not veto["common_veto"] and not veto["withheld_qubits"], f"{veto['z_common']} {veto['withheld_qubits']}")
    check(veto["tau"] >= su.SETTLE_TAU_FLOOR and veto["tau_floor"] == 0.0019)


@pytest.mark.parametrize("count", [8, 9, 16])
def test_settle_veto_fires_on_a_common_gap(count: int) -> None:
    shift = 4 * su.SETTLE_TAU_FLOOR
    veto = su.settle_veto({q: (shift, 0.003) for q in range(count)})
    check(veto["common_veto"], f"n = {count}: z {veto['z_common']}, tau {veto['tau']}")
    noisy = su.settle_veto(gaps(count, shift))
    check(noisy["common_veto"], f"n = {count} with noise: z {noisy['z_common']}")


def test_settle_veto_withholds_an_isolated_gap() -> None:
    data = gaps(16, 0.0)
    data[5] = (0.05, 0.003)
    veto = su.settle_veto(data)
    check(veto["withheld_qubits"] == [5], f"{veto['withheld_qubits']}")


def test_settle_veto_judges_each_qubit_against_the_others() -> None:
    # A moment fit of tau over the tested qubit and the other outliers caps their z near sqrt(n / k - 1); the median
    # and MAD of the other qubits ignore a minority of outliers.
    for count in (8, 9, 16):
        data = {q: (0.0, 0.0023) for q in range(count)}
        for q in (3, 5):
            data[q] = (0.1, 0.0023)
        check(set(su.settle_veto(data)["withheld_qubits"]) == {3, 5}, f"two outliers among {count}")


def test_settle_veto_sparse_gap_at_the_detectable_size() -> None:
    # Per-qubit sensitivity: (SETTLE_Z + z_0.9) * sqrt(s^2 + floor^2) at s = 0.0023 is about 0.0129.
    detectable = (su.SETTLE_Z + 1.2816) * math.sqrt(0.0023**2 + su.SETTLE_TAU_FLOOR**2)
    data = {q: (0.0, 0.0023) for q in range(16)}
    for q in (3, 5):
        data[q] = (detectable * 1.05, 0.0023)
    check(set(su.settle_veto(data)["withheld_qubits"]) == {3, 5}, f"{su.settle_veto(data)['per_qubit']}")
    single = su.settle_veto({0: (0.05, 0.0023)})
    check(single["per_qubit"]["0"]["z"] is None and not single["withheld_qubits"])


def test_settle_veto_estimates_tau_about_the_weighted_mean() -> None:
    data = {q: (0.01 + 0.02 * (q % 2), 0.001) for q in range(10)}
    veto = su.settle_veto(data)
    check(abs(veto["mu"] - 0.02) < 1e-9, f"mu {veto['mu']}")
    check(abs(veto["tau_dl"] - 0.01) < 1.5e-3, f"tau {veto['tau_dl']}")
    check(su.settle_veto({})["evaluable"] is False)


# --- carryover reader and order sentinel --------------------------------------------------------------------


def shot_arrays(
    carry: float, readers: int = 12, shots: int = 8192, contrast: float = 0.98, shuffle: bool = False
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    generator = np.random.default_rng(TEST_SEED)
    previous = [(generator.random(shots) < 0.3).astype(np.int8) for _ in range(readers)]
    read = []
    for bits in previous:
        p1 = 0.006 + contrast * carry * bits
        draw = (generator.random(shots) < p1).astype(np.int8)
        read.append(generator.permutation(draw) if shuffle else draw)
    return previous, read


def test_carryover_reader_recovers_a_planted_carryover() -> None:
    previous, read = shot_arrays(0.01)
    result = su.carryover_reader(previous, read, 0.98, 1.59, 32)
    check(abs(result["d"] - 0.01) < 4 * result["se"], f"{result}")
    check(0.0003 < result["se"] < 0.001, f"standard error {result['se']}")
    check(not result["passes"], f"{result}")


def test_carryover_reader_reads_zero_without_carryover_and_passes_the_screen() -> None:
    previous, read = shot_arrays(0.0)
    result = su.carryover_reader(previous, read, 0.98, 1.59, 32)
    check(abs(result["d"]) < 4 * result["se"] and 0.0003 < result["se"] < 0.0007, f"{result}")
    check(result["passes"] and result["bias_bound"] < 0.25 * 0.0188, f"{result}")
    check(abs(result["upper_bound"] - (abs(result["d"]) + result["z"] * result["se"])) < 1e-15)


def test_carryover_reader_reads_about_zero_under_shuffled_order() -> None:
    previous, read = shot_arrays(0.01, shuffle=True)
    result = su.carryover_reader(previous, read, 0.98, 1.59, 32)
    check(abs(result["d"]) < 4 * result["se"], f"{result}")


def test_carryover_reader_refuses_misaligned_input() -> None:
    previous, read = shot_arrays(0.0, readers=2)
    with pytest.raises(msa.AnalysisError):
        su.carryover_reader(previous, read[:1], 0.98, 1.59, 32)
    with pytest.raises(msa.AnalysisError):
        su.carryover_reader(previous, read, 0.0, 1.59, 32)


def correlated_pairs(
    shuffle: bool, pairs: int = 2, qubits: int = 8, shots: int = 8192
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Consecutive rows that share a per-shot latent phase: the same shot index correlates, a shifted one does not."""
    generator = np.random.default_rng(TEST_SEED)
    out = []
    for _ in range(pairs):
        latent = generator.standard_normal((qubits, shots))
        first = (latent + 2 * generator.standard_normal((qubits, shots)) > 0).astype(np.int8)
        second = (latent + 2 * generator.standard_normal((qubits, shots)) > 0).astype(np.int8)
        if shuffle:
            second = np.array([generator.permutation(row) for row in second])
        out.append((first, second))
    return out


def test_order_sentinel_passes_on_column_wise_order() -> None:
    result = su.order_sentinel(correlated_pairs(False))
    check(result["passes"] and result["z"] > 10, f"{result}")
    check(result["cells"] == 16)


def test_order_sentinel_fails_on_shuffled_order() -> None:
    result = su.order_sentinel(correlated_pairs(True))
    check(not result["passes"] and abs(result["z"]) < 3, f"{result}")
    check(su.order_sentinel([])["passes"] is False)


# --- device decision ----------------------------------------------------------------------------------------


def eight_rows() -> dict[int, dict[str, Any]]:
    ctx_map = bare_contexts(msa.FIXTURE_QUBITS)
    return su.evaluate(ground_counts(ctx_map), ctx_map)


def test_device_decision_reports_a_clean_null_and_adds_the_shape_bound() -> None:
    rows = eight_rows()
    decision = su.device_decision(rows, list(rows), 2, dict.fromkeys(rows, 0.002))
    check(decision["withheld"] is None and decision["device"]["status"] == "informative", f"{decision['withheld']}")
    check(not decision["device"]["departs_below"]["device"], f"{decision['device']['departs_below']}")
    check(len(decision["selected"]) == 8 and not decision["settle_veto"]["common_veto"])


def test_device_decision_withholds_below_eight_qubits_and_on_a_common_gap() -> None:
    rows = eight_rows()
    few = su.device_decision(rows, list(rows)[:7], 2, dict.fromkeys(rows, 0.0))
    check(few["device"] is None and "fewer than 8" in few["withheld"][0], f"{few['withheld']}")
    shifted = {
        q: {**r, "settle_n16": {**r["settle_n16"], "gap_difference": r["settle_n16"]["gap_difference"] + 0.02}}
        for q, r in rows.items()
    }
    veto = su.device_decision(shifted, list(rows), 2, dict.fromkeys(rows, 0.0))
    check(veto["settle_veto"]["common_veto"] and veto["device"] is None, f"{veto['withheld']}")
