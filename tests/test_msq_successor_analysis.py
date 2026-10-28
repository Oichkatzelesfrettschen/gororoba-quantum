"""The measurement-sequence successor's analysis core: gamma-rate fit, admission, shape bound, equilibrium estimator,
settle veto, carryover reader and order sentinel."""

from __future__ import annotations

import itertools
import math
from typing import Any

import numpy as np
import pytest

import diagnostic_experiments as de
import live_run
import measurement_sequence_analysis as msa
import msq_successor_analysis as su
import qpu_planning

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


@pytest.mark.parametrize("shape", [0.25, 1.0, 64.0, 1000.0])
def test_gamma_rule_integrates_the_moments_of_the_gamma_distribution_exactly(shape: float) -> None:
    nodes, weights = su.gamma_rule(shape)
    check(len(nodes) == su.GAMMA_NODES and abs(float(weights.sum()) - 1) < 1e-14, f"weights sum {weights.sum()}")
    for degree in (1, 2, 3):
        moment = math.prod(shape + k for k in range(degree))
        got = float(np.sum(weights * nodes**degree))
        check(abs(got / moment - 1) < 1e-13, f"shape {shape} degree {degree}: {got} against {moment}")


@pytest.mark.parametrize("shape", [0.25, 1.0, 4.0])
@pytest.mark.parametrize("lifetime", [100e-6, 250e-6])
def test_gamma_measure_p0_agrees_with_a_finer_rule(shape: float, lifetime: float) -> None:
    ctx = contexts((msa.FIXTURE_QUBITS[0],))[msa.FIXTURE_QUBITS[0]]
    i = np.arange(256)
    n = np.arange(1, 256)
    nodes, vectors = su.eigh_tridiagonal(2 * i + shape, np.sqrt(n * (n + shape - 1)))
    gate = msa.sx_gate(ctx, 0.0)
    tau = msa.tau_of("measure", ctx)
    total = 0.0
    for x, w in zip(nodes.tolist(), (vectors[0] ** 2).tolist(), strict=True):
        t1 = shape * lifetime / x
        total += (
            w * (1 + msa.corrected_z("measure", msa.TOP_STEPS, t1, min(ctx["t2_s"], 2 * t1), tau, 0.0, gate, 1.0)) / 2
        )
    got = su.gamma_measure_p0(ctx, lifetime, shape)
    # min(T2, 2 T1) kinks the integrand at the rate 2 / T2, so 64 nodes leave up to 5e-6 (T = 100 us, shape 0.25)
    # against the 256-node value, a tenth of the 64-node midpoint rule's error there and 1 % of the shape bound.
    check(abs(got - total) < 1e-5, f"shape {shape}, T {lifetime}: {got} against {total}")


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
        after = adjusted[q]["departure_n16"]
        check(abs(after["se_systematic"] - before - 0.002) < 1e-15)
        check(abs(after["se"] - math.hypot(after["se_statistical"], after["se_systematic"])) < 1e-15, "total se")
        z = adjusted[q]["decisions"]["departure"]["z"]
        check(abs(z - after["difference"] / after["se"]) < 1e-12, f"q{q}: the decision reads the unwidened se")
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


def test_the_count_rule_reads_the_shape_widened_decisions() -> None:
    """Eight rows at difference 0.0062 with statistical and systematic errors 0.001 each depart at z 4.4; a shape bound
    of 0.002 widens every z to 1.96 and the pooled z to about 2.05, so no device verdict may fire through either the
    pooled z or the count rule."""
    rows = eight_rows()
    planted: dict[int, dict[str, Any]] = {}
    for q, row in rows.items():
        departure = {
            **row["departure_n16"],
            "difference": 0.0062,
            "se_statistical": 0.001,
            "se_systematic": 0.001,
            "se": math.hypot(0.001, 0.001),
        }
        contrast = row["contrast_n16"]
        decisions = msa.decide(contrast["contrast"], contrast["se"], 0.0062, departure["se"])
        planted[q] = {**row, "departure_n16": departure, "decisions": decisions}
    adjusted = su.shape_adjusted(planted, dict.fromkeys(planted, 0.002))
    check(all(abs(r["decisions"]["departure"]["z"] - 1.96) < 0.01 for r in adjusted.values()), "adjusted z")
    flags = msa.device_flags(msa.device_verdict(adjusted))
    check(not any(flags.values()), f"a device verdict fired on shape-widened rows: {flags}")


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
    carry: float,
    readers: int = 12,
    shots: int = 8192,
    e01: float = 0.006,
    e10: float = 0.014,
    shuffle: bool = False,
    baselines: tuple[float, ...] = (),
    stream: int = 0,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Predecessor bits and reader bits from a latent end state: the predecessor's recorded bit reads the latent state
    through the assignment errors (discrimination overlap), and the reader's excitation `carry` follows the latent
    state, not the recorded bit. `baselines[i]` adds a bit-independent excitation to reader i."""
    generator = np.random.default_rng([TEST_SEED, stream])
    contrast = 1 - e01 - e10
    previous, read = [], []
    for i in range(readers):
        p_latent = (0.47, 0.31, 0.18)[3 * i // readers]
        latent = generator.random(shots) < p_latent
        bit = np.where(latent, generator.random(shots) >= e10, generator.random(shots) < e01).astype(np.int8)
        extra = baselines[i] if i < len(baselines) else 0.0
        p1 = e01 + contrast * (carry * latent + extra)
        draw = (generator.random(shots) < p1).astype(np.int8)
        previous.append(bit)
        read.append(generator.permutation(draw) if shuffle else draw)
    return previous, read


def readout(e01: float = 0.006, e10: float = 0.014) -> dict[str, float]:
    """The in-job readout record of a qubit with these assignment errors (prepare's scale and offset)."""
    return {"scale": 1 - e01 - e10, "offset": e10 - e01}


def test_carryover_reader_recovers_a_planted_carryover() -> None:
    previous, read = shot_arrays(0.01)
    result = su.carryover_reader(previous, read, readout(), 1.59, 32)
    check(abs(result["d"] - 0.01) < 4 * result["se"], f"{result}")
    check(0.0003 < result["se"] < 0.001 and result["readers"] == 12, f"standard error {result['se']}")
    check(not result["passes"], f"{result}")


def test_carryover_reader_reads_zero_without_carryover_and_passes_the_screen() -> None:
    previous, read = shot_arrays(0.0)
    result = su.carryover_reader(previous, read, readout(), 1.59, 32)
    check(abs(result["d"]) < 4 * result["se"] and 0.0003 < result["se"] < 0.0007, f"{result}")
    check(result["passes"] and result["bias_bound"] < 0.25 * 0.0188, f"{result}")
    check(abs(result["upper_bound"] - (abs(result["d"]) + result["z"] * result["se"])) < 1e-15)


def test_carryover_reader_reads_about_zero_under_shuffled_order() -> None:
    previous, read = shot_arrays(0.01, shuffle=True)
    result = su.carryover_reader(previous, read, readout(), 1.59, 32)
    check(abs(result["d"]) < 4 * result["se"], f"{result}")


def test_carryover_reader_refuses_misaligned_input() -> None:
    previous, read = shot_arrays(0.0, readers=2)
    with pytest.raises(msa.AnalysisError):
        su.carryover_reader(previous, read[:1], readout(), 1.59, 32)
    with pytest.raises(msa.AnalysisError):
        su.carryover_reader(previous, read, {"scale": 0.0, "offset": 0.0}, 1.59, 32)


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


def test_device_decision_fires_a_planted_departure_through_the_settle_reclassification() -> None:
    """A loss common to the measure and settle arms is a departure, and settle_descriptive keeps its device flag."""
    ctx_map = bare_contexts(msa.FIXTURE_QUBITS)
    rows = su.evaluate(ground_counts(ctx_map, eps=0.01, eps_settle=0.01), ctx_map)
    decision = su.device_decision(rows, list(rows), 2, dict.fromkeys(rows, 0.002))
    check(decision["withheld"] is None, f"{decision['withheld']}")
    check(msa.device_flags(decision["device"])["departs_below"], f"{msa.device_flags(decision['device'])}")


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


# --- the collected record of the relaxation family ----------------------------------------------------------

DT = 4e-9
EQUILIBRIUM_DT = 100000
RUN_SHOTS = 8192
RUN_WIDTH = 16


class Run:
    """A synthetic collected run of the relaxation family: model-device probabilities realized shot by shot."""

    def __init__(self, record: dict[str, Any], distributions: dict[str, Any], executed: dict[str, Any]) -> None:
        self.record, self.distributions, self.executed = record, distributions, executed
        self.registers: dict[str, dict[str, list[str]]] = {}
        self.chunks: list[list[int]] = []
        self.contexts: dict[int, dict[str, Any]] = {}


def build_run(
    carry: float = 0.0002,
    shuffle: bool = False,
    correlation: float = 0.3,
    thermal: float = 0.0,
    width: int = RUN_WIDTH,
) -> Run:
    """Column-wise shot order: consecutive sentinel rows share a per-shot uniform with probability `correlation`. A
    reader row's final bit reads its latent end state through the assignment errors and its reader bit carries
    `carry` times the readout contrast on that latent state, in the same shot. `shuffle` permutes every row's shots
    independently (a reader row's two registers together), which removes the cross-row same-shot structure."""
    generator = np.random.default_rng(TEST_SEED)
    # Shuffles draw from their own stream, so a shuffled run realizes the same shots in another row order.
    orderer = np.random.default_rng([TEST_SEED, 1])
    qubits = [3 * k + 1 for k in range(width)]
    base: dict[int, dict[str, Any]] = {}
    for part in (qubits[:8], qubits[8:16]):
        if part:
            base.update(base_contexts(tuple(part)))
    stems = de.msqr_row_stems(width)
    models = {q: msa.device_model(base[q], p_init=0.0, p_thermal=thermal) for q in base}
    final = {q: c["final"] for q, c in msa.device_counts(models, base, RUN_SHOTS).items()}
    pairs = {second: first for segment in de.msqr_sentinel_pairs() for first, second in segment}
    pattern_bits = [[int(b) for b in row] for row in de.msqe_pattern_bits(width)]
    pubs = [f"pub_{k:03d}" for k in range(len(stems))]
    bits: dict[tuple[int, int], np.ndarray] = {}
    reads: dict[tuple[int, int], np.ndarray] = {}
    uniform: dict[tuple[int, int], np.ndarray] = {}
    for k, stem in enumerate(stems):
        for rank, q in enumerate(qubits):
            ctx = base[q]
            contrast = 1 - ctx["e01"] - ctx["e10"]
            fresh = generator.random(RUN_SHOTS)
            if stem in pairs:
                shared = generator.random(RUN_SHOTS) < correlation
                fresh = np.where(shared, uniform[(k - 1, rank)], fresh)
            uniform[(k, rank)] = fresh
            member = f"{stem}_q{q}"
            if stem.startswith("msqr_reader"):
                steps, signed = de.msqr_reader_stem(int(stem.removeprefix("msqr_reader")))
                p1 = np.full(RUN_SHOTS, final[q][de.msq_member("measure", steps, signed, q)][0] / RUN_SHOTS)
            elif stem == "msqr_eq":
                excited = thermal * (1 - math.exp(-EQUILIBRIUM_DT * DT / ctx["t1_cal_s"]))
                p1 = np.full(RUN_SHOTS, ctx["e01"] + contrast * excited)
            elif stem.startswith("msqr_sent"):
                steps, signed = sentinel_template(stem)
                template = de.msq_member("delay", steps, signed, q)
                p1 = np.full(RUN_SHOTS, final[q][template][0] / RUN_SHOTS)
            elif stem.startswith("msqe_rc"):
                p1 = np.full(RUN_SHOTS, ctx["e01"])
            elif stem.startswith("msqe_pat"):
                bit = pattern_bits[int(stem.removeprefix("msqe_pat"))][rank]
                p1 = np.full(RUN_SHOTS, 1 - ctx["e10"] if bit else ctx["e01"])
            else:
                p1 = np.full(RUN_SHOTS, final[q][member][0] / RUN_SHOTS)
            if stem.startswith("msqr_reader"):
                # The predecessor's end state is latent; its recorded bit reads it through the assignment errors and
                # the in-circuit reader carries the excitation it leaves.
                latent = fresh < np.clip((p1 - ctx["e01"]) / contrast, 0.0, 1.0)
                row = np.where(
                    latent, generator.random(RUN_SHOTS) >= ctx["e10"], generator.random(RUN_SHOTS) < ctx["e01"]
                ).astype(np.int8)
                read = (generator.random(RUN_SHOTS) < ctx["e01"] + contrast * carry * latent).astype(np.int8)
                order = orderer.permutation(RUN_SHOTS) if shuffle else np.arange(RUN_SHOTS)
                bits[(k, rank)], reads[(k, rank)] = row[order], read[order]
                continue
            row = (fresh < p1).astype(np.int8)
            bits[(k, rank)] = orderer.permutation(row) if shuffle else row
    distributions: dict[str, Any] = {}
    executed: dict[str, Any] = {}
    components: list[list[dict[str, Any]]] = [[] for _ in stems]
    registers: dict[str, dict[str, list[str]]] = {}
    for k, stem in enumerate(stems):
        registers[pubs[k]] = {}
        for rank, q in enumerate(qubits):
            ctx = base[q]
            member = f"{stem}_q{q}"
            register = f"g{rank}_r0_final"
            line = bits[(k, rank)]
            registers[pubs[k]][register] = [str(int(b)) for b in line]
            names = [register]
            if (k, rank) in reads:
                # The reader member's law over final, its N mcm bits (all 0 here) and the reader bit on top.
                read = reads[(k, rank)]
                names.append(f"g{rank}_r0_reader")
                registers[pubs[k]][names[-1]] = [str(int(b)) for b in read]
                law = np.zeros(2 ** (member_steps(stem) + 1))
                top = law.size // 2
                for f, r in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    law[f + top * r] = float(np.sum((line == f) & (read == r))) / RUN_SHOTS
            else:
                ones = int(line.sum())
                law = np.zeros(2 ** (member_steps(stem) + 1))
                law[0], law[1] = 1 - ones / RUN_SHOTS, ones / RUN_SHOTS
            distributions[member] = [law]
            executed[member] = {
                "shots": RUN_SHOTS,
                "pub": pubs[k],
                "calibration": "run",
                "calibration_changed_during_shots": False,
                "placed_qubit_calibration": {
                    str(q): {
                        "T1": ctx["t1_cal_s"] * 1e6,
                        "T2": ctx["t2_s"] * 1e6,
                        "prob_meas1_prep0": ctx["e01"],
                        "prob_meas0_prep1": ctx["e10"],
                        "readout_error": (ctx["e01"] + ctx["e10"]) / 2,
                    }
                },
                "placed_gate_calibration": {
                    str(q): {
                        "sx_error": ctx["sx_error"],
                        "sx_duration_s": ctx["sx_duration_s"],
                        "measure_duration_s": ctx["window_s"],
                    }
                },
            }
            components[k].append(
                {
                    "member": member,
                    "physical_qubits": [q],
                    "registers_by_replica": [names],
                }
            )
    in_dt = {str(q): round(base[q]["delay_s"] / DT) for q in qubits}
    record = {
        "family_configuration": {
            "name": de.MSQR_FAMILY,
            "qubits": qubits,
            "layout_width": width,
            "dt_seconds": DT,
            "measurement_delay_dt": in_dt,
            "settle_delay_dt": {str(q): round(base[q]["settle_s"] / DT) for q in qubits},
            "prereadout_delay_dt": {str(q): round(base[q]["prereadout_s"] / DT) for q in qubits},
            "t1_delays_dt": [round(d / DT) for d in base[qubits[0]]["t1_delays_s"]],
            "equilibrium_delay_dt": EQUILIBRIUM_DT,
            "reader_idle_delay_dt": 5000,
            "pattern_bits": pattern_bits,
        },
        "execution_pubs": [{"name": pubs[k], "components": components[k]} for k in range(len(stems))],
        "groups": [{"backend": "ibm_kingston"}],
    }
    run = Run(record, distributions, executed)
    run.registers, run.chunks, run.contexts = registers, [list(range(len(stems)))], base
    return run


def sentinel_template(stem: str) -> tuple[int, tuple[str, str, int]]:
    """(N, signed member) of the delay-arm row a sentinel row copies."""
    index = int(stem.removeprefix("msqr_sent")[1])
    steps, signed = de.MSQR_SENTINEL_ROWS[index]
    return steps, signed


def member_steps(stem: str) -> int:
    """The clbits of a member's law beyond final: the measure and settle arms hold N bits, a reader its predecessor's N
    and the reader bit, a reset control one, the rest none."""
    if stem.startswith(("msq_measure_n", "msq_settle_n")):
        return int(stem.split("_n")[1].split("_")[0])
    if stem.startswith("msqr_reader"):
        return de.msqr_reader_stem(int(stem.removeprefix("msqr_reader")))[0] + 1
    return 1 if stem.startswith("msqe_rc") else 0


# One worker builds the planted run and its analysis.
pytestmark = pytest.mark.xdist_group("msq-successor-analysis")


@pytest.fixture(scope="module")
def run() -> Run:
    return build_run()


@pytest.fixture(scope="module")
def verdict(run: Run) -> dict[str, Any]:
    """The family analysis through measured_family, as live_run.collect calls it, at the registered scatter floor."""
    shot_order = {"registers": run.registers, "chunks": run.chunks}
    analysis = qpu_planning.measured_family(
        run.record, run.distributions, run.executed, live_run, shot_order=shot_order
    )
    result: dict[str, Any] = analysis["relaxation"]
    return result


def test_collected_reaches_a_verdict_on_a_planted_ground_state_run(verdict: dict[str, Any]) -> None:
    check("withheld" not in verdict, f"{verdict.get('withheld')}")
    check(verdict["order"]["passes"] and verdict["order"]["chunk"]["passes"], f"{verdict['order']}")
    for segment, result in verdict["order"]["sentinels"]["segments"].items():
        check(result["passes"] and result["z"] > 3, f"segment {segment}: {result}")
    check(len(verdict["selected"]) >= 8, f"{len(verdict['selected'])} selected: {verdict['decision']['withheld']}")
    decision = verdict["decision"]
    check(decision["withheld"] is None and decision["device"] is not None, f"{decision['withheld']}")
    check(decision["device"]["status"] == "informative", f"{decision['device']}")
    check(decision["settle_veto"]["common_veto"] is False, "a null run trips the common settle veto")
    kept = [verdict["screens"][str(q)] for q in verdict["selected"]]
    check(all(s["carryover"]["passes"] and s["equilibrium"]["passes"] for s in kept), "a selected qubit fails a gate")
    check(all(abs(s["equilibrium"]["q_hat"] - 1) < 0.05 for s in kept), "q_hat misses the planted q = 1")
    check(all(abs(s["carryover"]["d"]) < 4 * s["carryover"]["se"] + 5e-4 for s in kept), "carryover misses 0.0002")
    check(all(s["carryover"]["vertex"]["allocation"] > 0 for s in kept), "no vertex allocation")


def test_collected_record_serializes_to_plain_json(verdict: dict[str, Any]) -> None:
    import json

    text = json.dumps(verdict, allow_nan=False)
    check(0 < len(text) < 5_000_000, f"{len(text)} bytes")


def test_collected_reports_the_delay_arm_beside_the_echo_time(verdict: dict[str, Any]) -> None:
    for q in verdict["selected"]:
        entry = verdict["delay_descriptive"][str(q)]
        check(entry["t2_echo_s"] > 0 and "measured_minus_modeled" in entry, f"q{q}: {entry}")


@pytest.fixture(scope="module")
def narrow() -> tuple[Run, dict[str, Any]]:
    """A width-4 run and its analysis, the reference the order tests compare against."""
    small = build_run(width=4)
    return small, su.collected(small.record, small.distributions, small.executed, small.registers, small.chunks, FLOOR)


def test_collected_reports_a_lost_shot_order_and_still_decides(narrow: tuple[Run, dict[str, Any]]) -> None:
    """The readers read inside one circuit, so a shuffled row order fails the sentinels as a report and leaves the
    carryover screen and the selection as they are on the ordered run."""
    _, reference = narrow
    lost = build_run(shuffle=True, width=4)
    result = su.collected(lost.record, lost.distributions, lost.executed, lost.registers, lost.chunks, FLOOR)
    check("withheld" not in result and "decision" in result, f"{result.get('withheld')}")
    check(not result["order"]["sentinels"]["passes"] and result["order"]["chunk"]["passes"], f"{result['order']}")
    check(any(not s["passes"] for s in result["order"]["sentinels"]["segments"].values()), "no sentinel failed")
    evaluated = 0
    for q, screen in result["screens"].items():
        if screen["carryover"] is not None:
            evaluated += 1
            check(screen["carryover"]["d"] == reference["screens"][q]["carryover"]["d"], f"q{q}: the shuffle moved D")
    check(evaluated > 0 and result["selected"] == reference["selected"], "a shuffled order changed the selection")


def test_collected_reports_an_unreadable_chunk_timing_and_still_decides(narrow: tuple[Run, dict[str, Any]]) -> None:
    small, reference = narrow
    result = su.collected(
        small.record, small.distributions, small.executed, small.registers, None, FLOOR, chunk_reason="unreadable: x"
    )
    check(result["order"]["chunk"] == {"passes": False, "reason": "unreadable: x"}, f"{result['order']['chunk']}")
    check(result["selected"] == reference["selected"], "an unreadable chunk_timing changed the selection")


def test_pattern_crosscheck_compares_the_magnitude_with_the_reader_bound(verdict: dict[str, Any]) -> None:
    """U bounds |D|, so a carryover of either sign beyond U is the falsifier."""
    compared = 0
    for q, entry in verdict["pattern_crosscheck"]["per_qubit"].items():
        carryover = verdict["screens"][q]["carryover"]
        if "exceeds_reader_bound_z" not in entry:
            continue
        compared += 1
        expected = (abs(entry["d"]) - carryover["upper_bound"]) / entry["se"]
        check(entry["exceeds_reader_bound_z"] == expected, f"q{q}: {entry} against U {carryover['upper_bound']}")
    check(
        compared > 0 and any(e["d"] < 0 for e in verdict["pattern_crosscheck"]["per_qubit"].values()), "no negative D"
    )


def test_collected_reports_a_split_job_and_still_decides(narrow: tuple[Run, dict[str, Any]]) -> None:
    small, reference = narrow
    count = len(small.record["execution_pubs"])
    split = [list(range(40)), list(range(40, count))]
    result = su.collected(small.record, small.distributions, small.executed, small.registers, split, FLOOR)
    check(not result["order"]["chunk"]["passes"] and result["order"]["sentinels"]["passes"], f"{result['order']}")
    check(result["selected"] == reference["selected"], "a reported split changed the selection")
    layout = su.job_layout(small.record)
    for chunks in (None, [list(range(count - 1))]):
        order = su.order_conditions(layout, small.registers, chunks, small.distributions, small.executed)
        check(not order["chunk"]["passes"], f"chunks {chunks} must fail the report")


def test_collected_fails_closed_on_absent_registers_and_a_reordered_job(run: Run) -> None:
    absent = su.collected(run.record, run.distributions, run.executed, None, run.chunks, FLOOR)
    check("unavailable" in absent["withheld"], f"absent registers: {absent.get('withheld')}")
    layout = su.job_layout(run.record)
    reader = layout["names"][layout["stems"].index("msqr_reader3")]
    registers = {name: bits for name, bits in run.registers.items() if name != reader}
    result = su.collected(run.record, run.distributions, run.executed, registers, run.chunks, FLOOR)
    check(result["withheld"].startswith("AnalysisError") and reader in result["withheld"], f"{result['withheld']}")
    reordered = {**run.record, "execution_pubs": list(reversed(run.record["execution_pubs"]))}
    result = su.collected(reordered, run.distributions, run.executed, run.registers, run.chunks, FLOOR)
    check("row layout" in result["withheld"], f"{result['withheld']}")
    mismatch = {
        **run.distributions,
        f"msqr_reader3_q{layout['qubits'][0]}": [np.array([0.5, 0.5])],
    }
    result = su.collected(run.record, mismatch, run.executed, run.registers, run.chunks, FLOOR)
    check("differ from the collector's counts" in result["withheld"], f"{result['withheld']}")
    # A law whose final bit matches but whose reader bit does not.
    name = f"msqr_reader3_q{layout['qubits'][0]}"
    law = np.asarray(run.distributions[name][0], dtype=float)
    top = law.size // 2
    moved = law.copy()
    moved[0], moved[top] = law[0] + law[top], 0.0
    result = su.collected(
        run.record, {**run.distributions, name: [moved]}, run.executed, run.registers, run.chunks, FLOOR
    )
    check("differ from the collector's counts" in result["withheld"], f"{result['withheld']}")


def test_required_pubs_name_the_sentinel_and_reader_rows(run: Run) -> None:
    names = su.required_pubs(run.record)
    check(len(names) == 12 + 12, f"{len(names)} PUBs")
    layout = su.job_layout(run.record)
    for k in range(12):
        row = layout["stems"].index(f"msqr_reader{k}")
        check(layout["names"][row] in names and (row, layout["qubits"][0]) in layout["reader_registers"], f"{k}")


def test_collected_withholds_every_qubit_under_a_planted_carryover() -> None:
    hot = build_run(carry=0.01, width=4)
    result = su.collected(hot.record, hot.distributions, hot.executed, hot.registers, hot.chunks, FLOOR)
    check(result["order"]["passes"], f"{result['order']}")
    flagged = [s["carryover"] for s in result["screens"].values() if s["carryover"] is not None]
    check(bool(flagged) and not any(c["passes"] for c in flagged), "a planted carryover of 0.01 passed the screen")
    check(result["selected"] == [] and result["decision"]["withheld"], f"{result['decision']['withheld']}")


def test_collected_withholds_every_qubit_when_the_relaxation_target_is_far_from_one() -> None:
    warm = build_run(thermal=0.14, width=4)
    result = su.collected(warm.record, warm.distributions, warm.executed, warm.registers, warm.chunks, FLOOR)
    check(result["order"]["passes"], f"{result['order']}")
    rows = [s["equilibrium"] for s in result["screens"].values() if s["equilibrium"] is not None]
    check(bool(rows) and not any(r["passes"] for r in rows), "a 14 % equilibrium excitation passed the q bound")
    check(all(r["q_hat"] < 0.85 for r in rows if "q_hat" in r), f"{[r.get('q_hat') for r in rows]}")
    check(result["selected"] == [], "qubits selected under q near 0.7")


def test_measured_family_hands_the_order_evidence_to_the_analysis(run: Run, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[Any, ...]] = []
    reasons: list[Any] = []

    def stub(*arguments: Any, chunk_reason: Any = None) -> dict[str, Any]:
        seen.append(arguments)
        reasons.append(chunk_reason)
        return {"schema": "stub"}

    monkeypatch.setattr(qpu_planning.msq_successor_analysis, "collected", stub)
    ready = {"registers": run.registers, "chunks": run.chunks}
    analysis = qpu_planning.measured_family(run.record, run.distributions, run.executed, live_run, shot_order=ready)
    check(analysis["relaxation"] == {"schema": "stub"}, f"{analysis}")
    check(seen[0][3] is run.registers and seen[0][4] is run.chunks, "registers and chunks must reach the analysis")
    qpu_planning.measured_family(run.record, run.distributions, run.executed, live_run)
    check(seen[1][3] is None and seen[1][4] is None, "absent evidence must reach the analysis as None")
    lost = {"registers": run.registers, "chunks": None, "chunk_reason": "the chunk_timing is unreadable"}
    qpu_planning.measured_family(run.record, run.distributions, run.executed, live_run, shot_order=lost)
    check(seen[2][3] is run.registers and seen[2][4] is None, "an unreadable chunk_timing must still analyse")
    check(reasons == [None, None, "the chunk_timing is unreadable"], f"{reasons}")
    unreadable = qpu_planning.measured_family(
        run.record, run.distributions, run.executed, live_run, shot_order={"reason": "digest differs"}
    )
    check(unreadable["relaxation"]["withheld"] == "digest differs" and len(seen) == 3, f"{unreadable['relaxation']}")
    first = next(iter(run.executed))
    changed = {**run.executed, first: {**run.executed[first], "calibration": "other"}}
    withheld = qpu_planning.measured_family(run.record, run.distributions, changed, live_run, shot_order=ready)
    check("did not all run under one calibration" in withheld["relaxation"]["withheld"], f"{withheld['relaxation']}")
    check(len(seen) == 3, "a split calibration must stop before the analysis")


def test_retained_chunks_read_the_digest_checked_metadata(tmp_path: Any) -> None:
    import hashlib
    import json

    raw = tmp_path / "raw" / "job"
    raw.mkdir(parents=True)
    metadata = json.dumps({"executor": {"chunk_timing": [{"parts": [{"idx_item": 0}, {"idx_item": 1}]}]}}).encode()
    (raw / su.RESULT_METADATA).write_bytes(metadata)
    index = {"files": {su.RESULT_METADATA: hashlib.sha256(metadata).hexdigest()}}
    (raw / "index.json").write_text(json.dumps(index))
    check(su.retained_chunks(tmp_path) == [[0, 1]], "chunks")
    (raw / su.RESULT_METADATA).write_bytes(metadata + b" ")
    with pytest.raises(ValueError):
        su.retained_chunks(tmp_path)
    (tmp_path / "raw" / "second").mkdir()
    with pytest.raises(ValueError):
        su.retained_chunks(tmp_path)


def test_carryover_allocation_bounds_every_same_sign_mixture_of_classes() -> None:
    """Every allocation in the box [0, U] on the positive-response classes, and in [-U, 0] on the negative ones (corners
    and a grid of interior mixtures), shifts the departure by at most A * U."""
    ctx_map = contexts((msa.FIXTURE_QUBITS[0],))
    q = msa.FIXTURE_QUBITS[0]
    counts = ground_counts(ctx_map)[q]
    bound = 0.002
    result = su.carryover_allocation((q, {"final": counts["final"]}, ctx_map[q], bound))
    check(result["allocation"] > 0.3, f"{result}")
    check(bool(result["positive_classes"]) and bool(result["negative_classes"]), f"{result}")
    final = counts["final"]
    reference = su._departure(q, final, ctx_map[q])
    base = msa.device_counts({q: msa.device_model(ctx_map[q], p_init=0.0)}, ctx_map, su.VERTEX_SHOTS)[q]["final"]
    moved = msa.device_counts({q: msa.device_model(ctx_map[q], p_init=bound)}, ctx_map, su.VERTEX_SHOTS)[q]["final"]
    classes = su._class_members(q)
    limit = result["allocation"] * bound * (1 + 1e-3)

    def shift(weights: dict[str, float]) -> float:
        planted = dict(final)
        for label, weight in weights.items():
            for name in classes[label]:
                ones, n = final[name]
                planted[name] = (ones + weight * (moved[name][0] - base[name][0]) / su.VERTEX_SHOTS * n, n)
        return abs(su._departure(q, planted, ctx_map[q]) - reference)

    # The planted excitation moves a class by its single-class response times its allocation weight in [0, 1].
    for side in ("positive_classes", "negative_classes"):
        labels = result[side]
        corners = itertools.product((0.0, 1.0), repeat=min(len(labels), 5))
        for corner in corners:
            check(shift(dict(zip(labels, corner, strict=False))) <= limit, f"{side} corner {corner} exceeds A * U")
        for level in (0.25, 0.5, 0.75):
            check(shift(dict.fromkeys(labels, level)) <= limit, f"{side} uniform {level} exceeds A * U")
        graded = {label: (i + 1) / (len(labels) + 1) for i, label in enumerate(labels)}
        check(shift(graded) <= limit, f"{side} graded allocation exceeds A * U")
    with pytest.raises(msa.AnalysisError):
        su.carryover_allocation((q, {"final": counts["final"]}, ctx_map[q], 0.0))


def test_delay_descriptive_recovers_a_planted_free_evolution_time() -> None:
    q = msa.FIXTURE_QUBITS[0]
    ctx_map = bare_contexts((q,))
    planted = 0.5 * ctx_map[q]["t2_s"]
    counts = msa.device_counts({q: msa.device_model(ctx_map[q], p_init=0.0, t2_s=planted)}, ctx_map, SHOTS)
    rows = su.evaluate(counts, ctx_map)
    entry = su.delay_descriptive((q, rows[q], ctx_map[q]))
    free = entry["t2_free_s"]
    check(free is not None and abs(free / planted - 1) < 0.1, f"{free} vs {planted}")
    check(entry["t2_echo_s"] == ctx_map[q]["t2_s"] and abs(entry["measured_minus_modeled"]) > 0.01, f"{entry}")
    nominal = su.evaluate(ground_counts(ctx_map), ctx_map)
    same = su.delay_descriptive((q, nominal[q], ctx_map[q]))
    check(same["t2_free_s"] is not None and abs(same["t2_free_s"] / ctx_map[q]["t2_s"] - 1) < 0.1, f"{same}")


def test_departure_value_equals_the_row_residual_bit_for_bit() -> None:
    ctx_map = contexts((msa.FIXTURE_QUBITS[0],))
    q = msa.FIXTURE_QUBITS[0]
    counts = ground_counts(ctx_map, eps=0.004)[q]
    row = su.evaluate(ground_counts(ctx_map, eps=0.004), ctx_map)[q]
    check(su._departure(q, counts["final"], ctx_map[q]) == row["departure_n16"]["difference"], "residual differs")


def test_carryover_reader_recovers_the_planted_excitation_under_overlap_readout_error() -> None:
    """At contrast 0.9 the reader divisor returns D within noise under discrimination overlap."""
    d = 0.01
    previous, read = shot_arrays(d, e01=0.04, e10=0.06)
    result = su.carryover_reader(previous, read, readout(0.04, 0.06), 1.0, 32)
    check(abs(result["d"] - d) < 3 * result["se"], f"estimate {result['d']} against {d}: {result}")
    single = su.carryover_reader(previous, read, readout(0.04, 0.06), 1.0, 32)
    check(single["d"] == result["d"], "deterministic")


def expected_strata(
    d: float, e01: float, e10: float, latent: tuple[float, ...], shots: int
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Predecessor and reader bits whose cell counts are the overlap model's expectations at `shots` per stratum:
    latent end state p, recorded bit through (e01, e10), reader excitation d on the latent state alone."""
    contrast = 1 - e01 - e10
    previous, read = [], []
    for p in latent:
        bits: list[int] = []
        reads: list[int] = []
        for state, p_state in ((1, p), (0, 1 - p)):
            p_bit = 1 - e10 if state else e01
            p_read = e01 + contrast * d * state
            for bit, p_b in ((1, p_bit), (0, 1 - p_bit)):
                for value, p_r in ((1, p_read), (0, 1 - p_read)):
                    n = round(shots * p_state * p_b * p_r)
                    bits += [bit] * n
                    reads += [value] * n
        previous.append(np.asarray(bits, dtype=np.int8))
        read.append(np.asarray(reads, dtype=np.int8))
    return previous, read


def test_the_reader_divisor_is_the_posterior_separation_of_the_overlap_model() -> None:
    """At e01 = 0.019, e10 = 0.005 and latent excitation 0.47, 0.31 and 0.18 the squared contrast reads D about 2 %
    low (the posterior separation falls below c away from p = 0.5); the stratum divisor returns D."""
    e01, e10, d = 0.019, 0.005, 0.01
    contrast = 1 - e01 - e10
    for p in (0.47, 0.31, 0.18):
        m = e01 + contrast * p
        separation = p * (1 - e10) / m - p * e10 / (1 - m)
        check(abs(su.reader_divisor(m, e01, e10) - contrast * separation) < 1e-12, f"divisor at p {p}")
    previous, read = expected_strata(d, e01, e10, (0.47,) * 4 + (0.31,) * 4 + (0.18,) * 4, 400_000)
    result = su.carryover_reader(previous, read, readout(e01, e10), 1.0, 32)
    check(abs(result["d"] / d - 1) < 2e-3, f"the divisor reads {result['d']} against {d}")
    strata = [su.conditional_difference(after, before) for before, after in zip(previous, read, strict=True)]
    old = sum(stratum[0] for stratum in strata if stratum is not None) / len(strata) / contrast**2
    check(old / d < 0.99, f"the squared contrast reads {old} against {d}")
    # Readout errors taken from above lower the divisor and raise the estimate.
    high = su.carryover_reader(previous, read, readout(e01 + 0.005, e10 + 0.01), 1.0, 32)
    check(high["d"] > result["d"], "errors from above must not lower D")


def test_the_reader_standard_error_carries_each_stratum_s_own_variance() -> None:
    """A reader baseline 0.02 higher in the N = 2 block, at 8192 shots, latent excitation 0.47, 0.31 and 0.18 and
    errors 0.006 / 0.014: the reported standard error matches the binomial one at the class sizes, which the spread
    pooled over every stratum puts about 7 % low."""
    e01, e10, d, shots = 0.006, 0.014, 0.002, 8192
    contrast = 1 - e01 - e10
    previous: list[np.ndarray] = []
    read: list[np.ndarray] = []
    exact = []
    for p, base in [(0.47, 0.02)] * 4 + [(0.31, 0.0)] * 4 + [(0.18, 0.0)] * 4:
        bits: list[int] = []
        reads: list[int] = []
        for state, p_state in ((1, p), (0, 1 - p)):
            p_bit = 1 - e10 if state else e01
            p_read = e01 + base + contrast * d * state
            for bit, p_b in ((1, p_bit), (0, 1 - p_bit)):
                for value, p_r in ((1, p_read), (0, 1 - p_read)):
                    n = round(shots * p_state * p_b * p_r)
                    bits += [bit] * n
                    reads += [value] * n
        before, after = np.asarray(bits, dtype=np.int8), np.asarray(reads, dtype=np.int8)
        previous.append(before)
        read.append(after)
        ones, zeros = after[before == 1], after[before == 0]
        p1, p0 = float(ones.mean()), float(zeros.mean())
        exact.append((ones.size, zeros.size, p1 * (1 - p1) / ones.size + p0 * (1 - p0) / zeros.size))
    result = su.carryover_reader(previous, read, readout(e01, e10), 1.0, 32)
    divisors = result["divisors"]
    pooled = sum(float(r.sum()) for r in read) / sum(r.size for r in read)
    weights = [
        g**2 / (pooled * (1 - pooled) * (1 / n1 + 1 / n0)) for g, (n1, n0, _) in zip(divisors, exact, strict=True)
    ]
    binomial = math.sqrt(sum(w**2 * v / g**2 for w, g, (_, _, v) in zip(weights, divisors, exact, strict=True))) / sum(
        weights
    )
    check(abs(result["se"] / binomial - 1) < 0.01, f"se {result['se']} against the binomial {binomial}")
    check(1 / math.sqrt(sum(weights)) < 0.95 * binomial, "the pooled spread no longer understates this case")


def test_carryover_reader_is_free_of_block_baselines_through_stratification() -> None:
    """A bit-independent baseline that differs between the measure blocks moves a pooled difference by Simpson
    weighting; per-reader strata leave it out."""
    baselines = (0.001,) * 4 + (0.0,) * 8
    previous, read = shot_arrays(0.0, baselines=baselines)
    result = su.carryover_reader(previous, read, readout(), 1.0, 32)
    check(abs(result["d"]) < 4 * result["se"], f"{result}")
    pooled = su.conditional_difference(np.concatenate(read), np.concatenate(previous))
    check(pooled is not None and pooled[0] > 0.0001, f"the pooled estimate should carry the composition term: {pooled}")
    thin = [np.zeros(10, dtype=np.int8)] * 2
    dropped = su.carryover_reader([*previous, *thin], [*read, *thin], readout(), 1.0, 32)
    check(dropped["readers"] == 12 and dropped["d"] == result["d"], "an under-populated reader must drop out")
    empty = su.carryover_reader(thin, thin, readout(), 1.0, 32)
    check(not empty["evaluable"] and not empty["passes"], f"{empty}")


def test_relaxation_shot_order_reads_a_run_and_reports_a_malformed_one(tmp_path: Any, run: Run) -> None:
    import hashlib
    import json

    check(live_run.relaxation_shot_order({"family_configuration": {"name": de.MSQE_FAMILY}}, tmp_path) is None, "other")
    raw = tmp_path / "raw" / "job"
    raw.mkdir(parents=True)
    needed = sorted(su.required_pubs(run.record))
    index_files: dict[str, str] = {}
    for position, name in enumerate(needed):
        payload = json.dumps(
            {"pub_name": name, "registers": {r: {"bitstrings": b} for r, b in run.registers[name].items()}}
        ).encode()
        (raw / f"pub_{position:02d}.json").write_bytes(payload)
        index_files[f"pub_{position:02d}.json"] = hashlib.sha256(payload).hexdigest()

    def write_metadata(document: Any) -> None:
        data = json.dumps(document).encode()
        (raw / su.RESULT_METADATA).write_bytes(data)
        index_files[su.RESULT_METADATA] = hashlib.sha256(data).hexdigest()
        (raw / "index.json").write_text(json.dumps({"files": index_files}))

    chunk = {"parts": [{"idx_item": k} for k in range(len(run.record["execution_pubs"]))]}
    write_metadata({"executor": {"chunk_timing": [chunk]}})
    ready = live_run.relaxation_shot_order(run.record, tmp_path)
    check(ready is not None and "reason" not in ready, f"{ready}")
    if ready is None:
        raise AssertionError("no order evidence")
    check(ready["chunks"] == run.chunks and set(ready["registers"]) == set(needed), "chunks and registers")
    for bad in (
        {"executor": None},
        {"executor": "text"},
        {"executor": {"chunk_timing": None}},
        {"executor": {"chunk_timing": [{"parts": [{"idx_item": "0"}]}]}},
        {"executor": {"chunk_timing": ["x"]}},
        [1],
    ):
        write_metadata(bad)
        lost = live_run.relaxation_shot_order(run.record, tmp_path)
        check(lost is not None and "reason" not in lost, f"{bad}: an unreadable chunk_timing withheld the run")
        if lost is None:
            raise AssertionError("no order evidence")
        check(lost["chunks"] is None and "unreadable" in lost["chunk_reason"], f"{bad}: {lost}")
        check(set(lost["registers"]) == set(needed), f"{bad}: the registers were dropped")
    (raw / "pub_00.json").write_bytes(b"{}")
    reason = live_run.relaxation_shot_order(run.record, tmp_path)
    check(reason is not None and "unreadable" in reason["reason"], f"a register file off its digest: {reason}")


def per_stratum_estimate(previous: list[np.ndarray], read: list[np.ndarray], contrast: float) -> float:
    """The combined difference over contrast squared with each stratum weighted by the inverse of its own estimated
    variance, the weighting that read D low."""
    strata = [su.conditional_difference(after, before) for before, after in zip(previous, read, strict=True)]
    weights = [1 / s[1] ** 2 for s in strata if s]
    values = [s[0] for s in strata if s]
    return sum(w * v for w, v in zip(weights, values, strict=True)) / sum(weights) / contrast**2


REPLICATES = 200


@pytest.mark.parametrize(("e01", "e10", "contrast"), [(0.004, 0.014, 0.982), (0.004, 0.096, 0.9)])
def test_carryover_reader_is_unbiased_over_replicates_and_the_per_stratum_weights_are_not(
    e01: float, e10: float, contrast: float
) -> None:
    d = 0.004
    new = np.array(
        [
            su.carryover_reader(*shot_arrays(d, e01=e01, e10=e10, stream=k), readout(e01, e10), 1.0, 32)["d"]
            for k in range(REPLICATES)
        ]
    )
    old = np.array(
        [per_stratum_estimate(*shot_arrays(d, e01=e01, e10=e10, stream=k), contrast) for k in range(REPLICATES)]
    )
    spread = float(new.std(ddof=1)) / math.sqrt(REPLICATES)
    # Each stratum divides by its own posterior separation times the contrast, so the estimate is unbiased.
    check(abs(float(new.mean()) - d) < 2.5 * spread, f"mean {new.mean()} against {d}: {spread}")
    check(float(old.mean()) < d - 2 * spread, f"the per-stratum weights read {old.mean()} against {d}, spread {spread}")


def test_settle_gap_is_reported_and_never_a_device_verdict() -> None:
    """The successor preregisters the departure, the count rule and the mutation test; a settle gap the pooled test
    attributes appears under settle_descriptive and never as a device flag."""
    attributed = {"qubits": [1, 2], "pooled_z": 4.2, "status": "attributed", "device": True}
    quiet = {"qubits": [], "pooled_z": 0.1, "status": "none", "device": False}
    verdict = {
        "status": "informative",
        "departs_below": quiet,
        "exceeds_prediction": quiet,
        "settle_reduced_by_gap": attributed,
        "settle_deepened_by_gap": quiet,
    }
    out = su.settle_descriptive(verdict)
    check(set(msa.device_flags(out)) == {"departs_below", "exceeds_prediction"}, f"{msa.device_flags(out)}")
    check(not any(msa.device_flags(out).values()), f"{msa.device_flags(out)}")
    reported = out["settle_descriptive"]["settle_reduced_by_gap"]
    check(reported["status"] == "attributed" and "device" not in reported, f"{reported}")
