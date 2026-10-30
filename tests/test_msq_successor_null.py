"""The successor's batched null: bit identity of the batched gamma-rate fit, rows and shape bound with the scalar
functions of msq_successor_analysis, then the replicate generator, the arms and the sharded record."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest

import diagnostic_experiments as de
import measurement_sequence_analysis as msa
import msq_successor_analysis as su
import msq_successor_null_batch as nl

# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json, index 1.
TEST_SEED = 39316

DELAYS = [0.0, 20e-6, 50e-6, 100e-6, 200e-6]
SHOTS = msa.FIXTURE_SHOTS


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def canon(value: Any) -> Any:
    """A structure with floats as hex, arrays as bytes and the retained gate curves dropped."""
    if isinstance(value, float):
        return value.hex()
    if isinstance(value, dict):
        return {str(k): canon(v) for k, v in value.items() if k != "_gate_curves"}
    if isinstance(value, list | tuple):
        return [canon(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tobytes().hex()
    if isinstance(value, np.floating):
        return float(value).hex()
    if isinstance(value, np.integer):
        return int(value)
    return value


def series(lifetime: float, shape: float) -> np.ndarray:
    return 1 - 2 * su.survival(np.array(DELAYS), lifetime, shape)


def scalar_fit(y: np.ndarray, w: np.ndarray) -> dict[str, Any]:
    return su.fit_gamma_rate(DELAYS, [float(v) for v in y], [float(v) for v in w])


def assert_fits_equal(y: np.ndarray, w: np.ndarray) -> list[dict[str, Any]]:
    """The batched fit of every row against su.fit_gamma_rate by float.hex: T, shape, chi-square, p-value, flags."""
    fit = nl.fit_gamma_rows(DELAYS, y, w)
    pvalue = nl.p_values(fit.chi2, DELAYS)
    out = []
    for i in range(y.shape[0]):
        ref = scalar_fit(y[i], w[i])
        got = {
            "t_s": float(fit.t_s[i]),
            "shape": float(fit.shape[i]),
            "chi2": float(fit.chi2[i]),
            "p_value": float(pvalue[i]),
            "lower_edge": bool(fit.lower_edge[i]),
            "exponential_edge": math.isinf(float(fit.shape[i])),
        }
        for key, value in got.items():
            expected = ref[key]
            same = value.hex() == expected.hex() if isinstance(value, float) else value == expected
            check(same, f"row {i} {key}: batched {value!r}, scalar {expected!r}")
        out.append(ref)
    return out


WEIGHTS = np.full(5, 1e4)


def test_batched_fit_equals_the_scalar_fit_at_an_interior_shape() -> None:
    rows = np.array([series(250e-6, 3.0), series(150e-6, 40.0), series(400e-6, 0.6)])
    noise = np.array([[0.0, 0.001, -0.002, 0.0015, 0.0], [0.0, -0.001, 0.001, 0.0, 0.002], [0.0, 0.0, 0.0, 0.0, 0.0]])
    refs = assert_fits_equal(rows + noise, np.tile(WEIGHTS, (3, 1)))
    check(all(not r["exponential_edge"] and not r["lower_edge"] for r in refs), f"{refs}")


def test_batched_fit_equals_the_scalar_fit_at_the_lower_grid_edge() -> None:
    # A heavier tail than the lowest grid shape (0.25) puts the grid minimum on the lower edge.
    rows = np.array([series(400e-6, 0.1), series(250e-6, 0.05)])
    refs = assert_fits_equal(rows, np.tile(WEIGHTS, (2, 1)))
    check(all(r["lower_edge"] for r in refs), f"{[r['lower_edge'] for r in refs]}")


def test_batched_fit_equals_the_scalar_fit_at_the_exponential_edge() -> None:
    rows = np.array([series(250e-6, su.EXPONENTIAL), series(90e-6, su.EXPONENTIAL)])
    refs = assert_fits_equal(rows, np.tile(WEIGHTS, (2, 1)))
    check(all(r["exponential_edge"] for r in refs), f"{[r['shape'] for r in refs]}")


def test_batched_fit_equals_the_scalar_fit_on_a_block_of_drawn_replicates() -> None:
    generator = np.random.default_rng(TEST_SEED)
    count = 48
    lifetime = 10 ** generator.uniform(-4.4, -3.3, count)
    shape = np.exp(generator.uniform(math.log(0.25), math.log(64.0), count))
    y = np.array([series(t, k) for t, k in zip(lifetime, shape, strict=True)])
    y = y + generator.normal(0.0, 0.004, y.shape) * np.array([0.0, 1.0, 1.0, 1.0, 1.0])
    w = 1e4 * (1 + generator.random(y.shape))
    refs = assert_fits_equal(y, w)
    check(len({r["exponential_edge"] for r in refs} | {r["lower_edge"] for r in refs}) >= 1, "no variety")


def test_a_fit_without_the_golden_refinement_differs_from_the_scalar_fit() -> None:
    # The comparison above discriminates: dropping the refinement changes the bits of an interior fit.
    y = series(250e-6, 3.0)[None, :]
    fit = nl.fit_gamma_rows(DELAYS, y, WEIGHTS[None, :])
    values, scales = nl.grid_profiles(np.array(DELAYS[1:]), y[:, 1:], WEIGHTS[None, 1:])
    best = int(np.argmin(values[0]))
    check(float(scales[0, best]).hex() != float(fit.t_s[0]).hex(), "the grid minimum already equals the refined fit")


def test_memo_fits_each_distinct_series_once_and_reuses_it() -> None:
    memo = nl.FitMemo(DELAYS)
    y = np.array([series(250e-6, 3.0)] * 3 + [series(150e-6, 2.0)])
    w = np.tile(WEIGHTS, (4, 1))
    fit = memo.fit(y, w)
    check(len(memo.table) == 2, f"{len(memo.table)} fits for two distinct series")
    check(fit.t_s[0] == fit.t_s[1] == fit.t_s[2] and fit.t_s[0] != fit.t_s[3], "rows lost their identity")
    memo.fit(y, w)
    check(len(memo.table) == 2, "a repeated call refitted")


# --- rows and shape bound -----------------------------------------------------------------------------------


def planned(qubits: tuple[int, ...]) -> dict[int, dict[str, Any]]:
    base = msa.fixture_contexts(qubits, None)
    return su.with_planning(
        {
            q: {k: v for k, v in c.items() if k not in ("planning", "planning_se", "model_scatter_floor")}
            for q, c in base.items()
        },
        msa.DEMONSTRATION_SCATTER_FLOOR,
    )


def noisy_counts(
    generator: np.random.Generator, ctx: dict[str, Any], qubit: int, factor: float, **over: Any
) -> dict[str, Any]:
    model = msa.device_model(ctx, p_init=0.0, sx_error=factor * ctx["sx_error"], **over)
    expected = msa.device_counts({qubit: model}, {qubit: ctx}, SHOTS)[qubit]["final"]
    return {"final": {n: (int(generator.binomial(n_, k / n_)), n_) for n, (k, n_) in expected.items()}}


def test_rows_equal_the_scalar_rows_field_for_field() -> None:
    generator = np.random.default_rng(TEST_SEED)
    contexts = planned(msa.FIXTURE_QUBITS[:3])
    for qubit, ctx in contexts.items():
        counts = [noisy_counts(generator, ctx, qubit, 1.0 + 0.4 * generator.standard_normal()) for _ in range(4)]
        # A replicate whose readout contrast falls below the floor takes the unusable path.
        counts.append({"final": {n: (SHOTS // 2, SHOTS) for n in counts[0]["final"]}})
        memo = nl.FitMemo(ctx["t1_delays_s"])
        batched = nl.evaluate_rows([qubit] * len(counts), ctx, counts, memo)
        for got, item in zip(batched, counts, strict=True):
            ref = su._evaluate((qubit, item, ctx), False)
            check(canon(got) == canon(ref), f"q{qubit}: a row differs from the scalar row")
            if ref["usable"]:
                for name, curves in ref["_gate_curves"].items():
                    for side, scalar_side in zip(got["_gate_curves"][name], curves, strict=True):
                        check(
                            all(side[k].tobytes() == scalar_side[k].tobytes() for k in scalar_side),
                            f"q{qubit}: gate curve {name} differs",
                        )
    check(not batched[-1]["usable"], "the degenerate replicate was usable")


def test_shape_bound_rows_equal_the_scalar_bound() -> None:
    contexts = planned(msa.FIXTURE_QUBITS[:2])
    for ctx in contexts.values():
        lifetimes = np.array([90e-6, 150e-6, 274e-6, 400e-6])
        got = nl.shape_bound_rows(ctx, lifetimes)
        for t_s, value in zip(lifetimes.tolist(), got.tolist(), strict=True):
            ref = su._shape_bound((ctx, t_s, su.SHAPE_DOMAIN_SHAPES))
            check(value.hex() == ref.hex(), f"T {t_s}: {value!r} against {ref!r}")


def test_memo_distinguishes_weights() -> None:
    memo = nl.FitMemo(DELAYS)
    y = np.array([series(250e-6, 2.0)] * 2)
    w = np.array([WEIGHTS, WEIGHTS * np.array([1.0, 3.0, 1.0, 1.0, 1.0])])
    fit = memo.fit(y + np.array([0, 0.002, -0.001, 0.001, 0.0]), w)
    check(len(memo.table) == 2, "a weight change reused a fit")
    check(fit.t_s[0] != fit.t_s[1], "different weights gave one fit")


# --- the replicate generator, the arms and the record --------------------------------------------------------

from pathlib import Path  # noqa: E402

# The fields build_setup reads from the width-24 rehearsal record, with its snapshot cut to the layout qubits
# (tests/data/msq_successor_null/trim_record.py); the audit test below rebuilds it from the retained record.
RECORD = Path(__file__).resolve().parent / "data/msq_successor_null/record"
RETAINED_RECORD = Path(__file__).resolve().parent.parent / "results/live/2026-10-28T163139.827337Z"
# The retained sparse calibration's scale of the 8-qubit pool on RETAINED_RECORD's snapshot.
SPARSE_SCALE_8 = 1.25


# One worker builds the shared setup; the planted tests run at 8 qubits, so it solves only that pool's losses.
pytestmark = pytest.mark.xdist_group("msq-successor-null")


@pytest.fixture(scope="module")
def setup() -> nl.Setup:
    return nl.with_sparse_scale(nl.build_setup(RECORD), {8: SPARSE_SCALE_8})


def small(arm: str, active: int = 8, param: float = 3.0) -> nl.Case:
    """A case that runs `active` qubits, so a test replicate costs a second or two."""
    return nl.Case(arm, f"{active}-qubits", active, param)


def test_truth_equals_the_model_device_on_the_exponential_limit(setup: nl.Setup) -> None:
    ctx = setup.contexts[3]
    truth = nl.Truth(ctx["t1_cal_s"], math.inf, 1.0, 1.0, {}, 0.0, 0.0)
    got = nl.member_probabilities(ctx, 5, truth, setup.equilibrium_s)
    expected = msa.device_counts({5: msa.device_model(ctx, p_init=0.0)}, {5: ctx}, SHOTS)[5]["final"]
    check(set(expected) <= set(got), "a member has no probability")
    worst = max(abs(got[name] - ones / SHOTS) for name, (ones, _) in expected.items())
    check(worst < 1.0 / SHOTS, f"largest difference {worst} exceeds one shot")


def test_the_gamma_truth_departs_from_the_exponential_by_the_shape_bound(setup: nl.Setup) -> None:
    ctx = setup.contexts[3]
    exponential = nl.Truth(ctx["t1_cal_s"], math.inf, 1.0, 1.0, {}, 0.0, 0.0)
    heavy = exponential._replace(shape=0.25)
    name = msa.member_names("measure", msa.TOP_STEPS, 5)[0]
    a = nl.member_probabilities(ctx, 5, exponential, setup.equilibrium_s)[name]
    b = nl.member_probabilities(ctx, 5, heavy, setup.equilibrium_s)[name]
    bound = su._shape_bound((ctx, ctx["t1_cal_s"], su.SHAPE_DOMAIN_SHAPES))
    check(0 < abs(a - b) <= 2 * bound, f"{abs(a - b)} against the bound {bound}")


def planted_slots(setup: nl.Setup, case: nl.Case) -> tuple[nl.Drawn, list[nl.Truth]]:
    drawn = nl.draw_replicate(setup, case, TEST_SEED, 0)
    return drawn, drawn.truths


def test_carryover_arms_plant_the_boundary_less_three_standard_errors(setup: nl.Setup) -> None:
    margin = su.SCREEN_FRACTION * su.BOUND_FLOOR
    for arm, classes in (("carryover-positive", setup.positive), ("carryover-negative", setup.negative)):
        drawn, truths = planted_slots(setup, small(arm))
        for j, truth in zip(drawn.calibration, truths, strict=True):
            check(set(truth.excitation) == set(classes[j]), f"{arm}: classes {set(truth.excitation)}")
            check(all(v == truth.reader > 0 for v in truth.excitation.values()), f"{arm}: {truth.excitation}")
            ctx = setup.contexts[j]
            ones = [
                msa.device_counts({0: msa.device_model(ctx, p_init=0.0)}, {0: ctx}, SHOTS)[0]["final"][
                    nl.predecessor_name(i, 0)
                ][0]
                for i in range(nl.READERS)
            ]
            inside = setup.allocation[j] * truth.reader + 3 * setup.allocation[j] * nl.reader_standard_error(
                ctx, ones, truth.reader, setup.shots
            )
            check(abs(inside - margin) < 1e-9, f"{arm}: A D + 3 SE = {inside}, boundary {margin}")
    # The boundary arm's offsets order the carried excitation: 0, 1 and 2 standard errors inside.
    carried = [setup.carried[0][m] for m in (0.0, 1.0, 2.0)]
    check(carried[0] > carried[1] > carried[2] > 0, f"{carried}")
    check(abs(setup.allocation[0] * carried[0] - margin) < 1e-9, "offset 0 is not the boundary")


def test_q_arm_plants_the_screen_bound_plus_its_confidence_margin(setup: nl.Setup) -> None:
    drawn, truths = planted_slots(setup, small("q-tolerance"))
    for j, truth in zip(drawn.calibration, truths, strict=True):
        check(truth.q == setup.q_planted[j] and not truth.excitation, f"{truth}")
        check(setup.tolerance[j] < truth.q < min(setup.tolerance[j] + 0.05, 1.0), f"{truth.q} {setup.tolerance[j]}")
    # At the expected counts the screen's lower confidence bound sits on the tolerance bound.
    ctx = setup.contexts[0]
    counts = nl.expected_counts(
        ctx,
        nl.Truth(ctx["t1_cal_s"], math.inf, setup.q_planted[0], 1.0, {}, 0.0, 0.0),
        setup.equilibrium_s,
        setup.shots,
    )
    keys = {"ro0": msa.ro0_name(0), "eq": de.msqr_equilibrium_member(0)}
    keys.update({f"t1-{k}": name for k, name in enumerate(msa.t1_names(0))})
    estimate = su.equilibrium_estimate({key: counts[name] for key, name in keys.items()}, ctx, setup.equilibrium_s)
    screen = su.q_screen(estimate, su.q_sensitivity(ctx, estimate["t1_s"]), setup.width)
    # Whole expected counts leave the bound within a tenth of a standard error of the tolerance.
    check(abs(screen["lower_bound"] - screen["tolerance"]) < 0.1 * estimate["se"], f"{screen}")


def test_settle_arms_plant_their_gaps_at_the_stated_sizes(setup: nl.Setup) -> None:
    floor = su.SETTLE_TAU_FLOOR
    _, common = planted_slots(setup, small("settle-common"))
    check(all(t.gap == 4 * floor for t in common), f"{[t.gap for t in common]}")
    # The calibration draw precedes every truth, so the gamma case names the planted slots' calibrations; only
    # those two solve their loss.
    planted = nl.draw_replicate(setup, small("gamma"), TEST_SEED, 0).calibration[: nl.PLANTED_QUBITS]
    size = nl.sparse_gap(setup.settle_se, 8)
    solved = {j: nl.sparse_losses((setup.contexts[j], setup.equilibrium_s, {8: 1.3 * size})) for j in set(planted)}
    scaled = setup._replace(
        sparse_scale={8: 1.3}, sparse_loss=tuple(solved.get(j, {}) for j in range(len(setup.contexts)))
    )
    drawn, sparse = planted_slots(scaled, small("settle-sparse"))
    losses = [scaled.sparse_loss[j][8] for j in drawn.calibration[: nl.PLANTED_QUBITS]]
    check([t.loss for t in sparse] == [*losses, *[0.0] * (len(sparse) - 2)], f"{[t.loss for t in sparse]}")
    check(all(t.gap == 0.0 for t in sparse), "the sparse arm plants a settle-only shift")
    spread = setup.settle_se**2 + floor**2
    size = (3 + 1.28) * math.sqrt(spread * (1 + math.pi / 2 / 7))
    check(abs(nl.sparse_gap(setup.settle_se, 8) - size) < 1e-15 and 4 * floor < size < 0.02, f"sparse size {size}")
    # The planted measure-arm loss gives the scaled settle gap at the noise-free counts.
    ctx = setup.contexts[drawn.calibration[0]]
    gap = nl.tail_gap(ctx, losses[0], setup.equilibrium_s) - nl.tail_gap(ctx, 0.0, setup.equilibrium_s)
    check(abs(abs(gap) / (1.3 * size) - 1) < 0.01, f"planted gap {gap} against {1.3 * size}")
    # A pool size without a measured scale refuses to plant.
    with pytest.raises(ValueError, match="no measured sparse gap scale"):
        nl.draw_replicate(scaled, small("settle-sparse", 9), TEST_SEED, 0)
    # A planted gap shifts the settle members' P(1) by -contrast * gap and no other member.
    ctx = setup.contexts[0]
    base = nl.Truth(ctx["t1_cal_s"], 3.0, 1.0, 1.0, {}, 0.0, 0.0)
    moved = nl.member_probabilities(ctx, 5, base._replace(gap=0.01), setup.equilibrium_s)
    still = nl.member_probabilities(ctx, 5, base, setup.equilibrium_s)
    contrast = 1 - ctx["e01"] - ctx["e10"]
    for name in still:
        delta = moved[name] - still[name]
        if "_settle_" in name:
            check(abs(delta + contrast * 0.01) < 1e-12, f"{name}: {delta}")
        else:
            check(delta == 0.0, f"{name}: {delta}")
    # A measure-arm loss moves the measure members and leaves the settle members alone.
    lossy = nl.member_probabilities(ctx, 5, base._replace(loss=0.002), setup.equilibrium_s)
    for name in still:
        moved_by = lossy[name] - still[name]
        if "_settle_" in name:
            check(moved_by == 0.0, f"{name}: {moved_by}")
    check(any(lossy[n] != still[n] for n in still if "_measure_" in n), "the loss moved no measure member")


@pytest.mark.audit
def test_sparse_scale_evidence_covers_every_pool_of_the_layout(tmp_path: Path) -> None:
    import importlib.util

    record = json.loads((nl.ROOT / nl.SPARSE_SCALE_EVIDENCE).read_text())
    retained, _, digest = nl.load_snapshot(RETAINED_RECORD)
    width = int(retained["family_configuration"]["layout_width"])
    pools = {m or width for m in nl.SETTLE_POOLS}
    scales = nl.sparse_scales(record["snapshot_sha256"], width, nl.LEGACY_SHOTS)[0]
    check(set(scales) == pools and record["snapshot_sha256"] == digest, "")
    check(record["seed"] == nl.SPARSE_CALIBRATION_SEED != nl.SUCCESSOR_NULL_SEED, "the calibration seed")
    check(scales[8] == SPARSE_SCALE_8, f"{scales}")
    check(nl.sparse_scales("0" * 64, width, nl.LEGACY_SHOTS) == ({}, ""), "the scales serve another snapshot")
    check(
        nl.sparse_scales(record["snapshot_sha256"], width + 8, nl.LEGACY_SHOTS) == ({}, ""),
        "the scales serve another width",
    )
    spec = importlib.util.spec_from_file_location("trim_record", RECORD.parent / "trim_record.py")
    if spec is None or spec.loader is None:
        raise AssertionError("trim_record.py is unreadable")
    trim = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trim)
    trim.trim(RETAINED_RECORD, tmp_path)
    for path in sorted(RECORD.rglob("*.json")):
        rebuilt = tmp_path / path.relative_to(RECORD)
        check(rebuilt.read_bytes() == path.read_bytes(), f"{path.name} differs from the retained record's trim")
    for pool, entry in record["pools"].items():
        last = entry["points"][-1]
        check(last["scale"] == entry["scale"] == scales[int(pool)], f"pool {pool}")
        check(abs(last["power"] - nl.SPARSE_TARGET_POWER) <= last["se"], f"pool {pool}: {last}")


def linear_power(law: Callable[[float], float]) -> Callable[[Any, int, int], list[tuple[int, int]]]:
    """A stand-in for nl.sparse_powers whose per-qubit power is `law` of each item's scale, out of 1000 planted gaps."""

    def powers(items: Any, _seed: int, _replicates: int) -> list[tuple[int, int]]:
        return [(round(1000 * law(scale)), 1000) for _, _, scale in items]

    return powers


def test_the_sparse_calibration_steps_to_the_target_power(setup: nl.Setup, monkeypatch: pytest.MonkeyPatch) -> None:
    for seed in (nl.SUCCESSOR_NULL_SEED, nl.SPARSE_CONFIRMATION_SEED):
        with pytest.raises(ValueError, match="own seed"):
            nl.calibrate_sparse_scale(setup, 8, seed, 10)
    # A power linear in the scale, 0.70 at 1 and 0.95 at 2: the secant lands at 1.8.
    monkeypatch.setattr(nl, "sparse_powers", linear_power(lambda scale: 0.45 + 0.25 * scale))
    out = nl.calibrate_sparse_scale(setup, 8, nl.SPARSE_CALIBRATION_SEED, 10)
    check(abs(out["scale"] - 1.8) < 0.05 and len(out["points"]) == 3, f"{out}")
    monkeypatch.setattr(nl, "sparse_powers", linear_power(lambda scale: 0.9 - 0.1 * scale))
    with pytest.raises(ValueError, match="does not rise"):
        nl.calibrate_sparse_scale(setup, 8, nl.SPARSE_CALIBRATION_SEED, 10)
    # Two shallow points above the target, 0.95 at 1 and 0.96 at 1.25, extrapolate to a negative scale.
    monkeypatch.setattr(nl, "sparse_powers", linear_power(lambda scale: 0.91 + 0.04 * scale))
    with pytest.raises(ValueError, match="non-positive"):
        nl.calibrate_sparse_scale(setup, 8, nl.SPARSE_CALIBRATION_SEED, 10)


def test_the_sparse_power_target_takes_a_bonferroni_share_per_pool() -> None:
    check(abs(nl.SPARSE_FAMILY_CONFIDENCE - (1 - 0.05 / len(nl.SETTLE_POOLS))) < 1e-15, "family confidence")
    seeds = {nl.SUCCESSOR_NULL_SEED, nl.SPARSE_CALIBRATION_SEED, nl.SPARSE_CONFIRMATION_SEED}
    check(len(seeds) == 3, "the confirmation null shares a seed with the null or the calibration")
    check(nl.upper_bound(0, nl.SPARSE_EXPOSED_VERDICTS, nl.SPARSE_FAMILY_CONFIDENCE) < nl.FALSE_FIRE_CEILING, "")
    check(nl.upper_bound(0, nl.SPARSE_EXPOSED_VERDICTS - 1, nl.SPARSE_FAMILY_CONFIDENCE) >= nl.FALSE_FIRE_CEILING, "")
    check(nl.minimum_verdicts("settle-sparse") == nl.SPARSE_EXPOSED_VERDICTS, "")
    # 524 of 599 planted gaps withheld: shown below 0.9 at 95 % for one pool, not at the three-pool family's 95 %.
    withheld = [2] * 262 + [0] * 37 + [0]
    rows: list[dict[str, Any]] = [
        {
            "issued": True,
            "fired": [],
            "work": 1,
            "planted_in_pool": 1 if i == 299 else 2,
            "planted_withheld": w,
            "selected": 1,
            "carryover_failed": 0,
            "equilibrium_failed": 0,
            "common_veto": False,
            "planted_equilibrium_failed": 0,
            "planted_selected": 0,
            "counted": True,
        }
        for i, w in enumerate(withheld)
    ]
    stats = nl.case_statistics("settle-sparse", rows)
    check(stats["planted_in_pool"] == 599 and stats["planted_withheld"] == 524, f"{stats['planted_withheld']}")
    check(stats["per_qubit_veto_power_upper_95"] < nl.SPARSE_TARGET_POWER, f"{stats['per_qubit_veto_power_upper_95']}")
    check(stats["targets"]["per_qubit_veto_power_not_below_90_percent_family"], f"{stats}")
    rows[0]["planted_withheld"] = 0
    rows[1]["planted_withheld"] = 0
    check(
        not nl.case_statistics("settle-sparse", rows)["targets"]["per_qubit_veto_power_not_below_90_percent_family"], ""
    )


def test_minority_arms_plant_two_slots_and_count_verdicts_that_select_one(setup: nl.Setup) -> None:
    drawn, truths = planted_slots(setup, small("q-minority"))
    expected = [setup.q_planted[j] for j in drawn.calibration[: nl.PLANTED_QUBITS]]
    check([t.q for t in truths] == [*expected, *[1.0] * (len(truths) - 2)], f"{[t.q for t in truths]}")
    drawn, truths = planted_slots(setup, small("plateau-minority"))
    check(all(math.isinf(t.shape) and (t.t_s, t.q) in setup.plateau for t in truths[:2]), "minority plateau pairs")
    check(
        all(
            t.q == 1.0 and t.t_s == setup.contexts[j]["t1_cal_s"]
            for j, t in zip(drawn.calibration[2:], truths[2:], strict=True)
        ),
        "",
    )
    rows = nl.analyse_block((setup, small("q-minority", 10), TEST_SEED, [0, 1, 2]))
    check(all(r["counted"] == (r["issued"] and r["planted_selected"] > 0) for r in rows), f"{rows}")
    check(any(r["counted"] for r in rows), "no q-minority verdict selected a planted qubit")
    stats = nl.case_statistics("q-minority", rows)
    check(
        stats["exposed"] == sum(r["counted"] for r in rows) and "exposed_verdicts_at_least_299" in stats["targets"], ""
    )


def test_plateau_and_gamma_arms_plant_their_truth(setup: nl.Setup) -> None:
    drawn, truths = planted_slots(setup, small("plateau-retained"))
    check(all(math.isinf(t.shape) and (t.t_s, t.q) in setup.plateau for t in truths), "plateau pairs")
    check(0.6 < float(np.median([q for _, q in setup.plateau])) < 0.8, "the plateau q is not near 0.7")
    low = [setup.plateau[i] for i in setup.plateau_low]
    check(bool(low) and all(q < min(setup.tolerance) for _, q in low), f"{low}")
    check(len(low) < len(setup.plateau), "every retained pair lies below the tolerance bounds")
    drawn, truths = planted_slots(setup, small("plateau-low"))
    check(all(math.isinf(t.shape) and (t.t_s, t.q) in low for t in truths), "plateau-low pairs")
    drawn, truths = planted_slots(setup, small("gamma"))
    for j, t in zip(drawn.calibration, truths, strict=True):
        check(t.q == 1.0 and not t.excitation and t.gap == 0.0 and t.reader == 0.0, f"{t}")
        check(t.t_s == setup.contexts[j]["t1_cal_s"] and 0.25 <= t.shape <= 64.0, f"{t}")


def test_residuals_follow_the_stated_common_and_independent_parts(setup: nl.Setup) -> None:
    factors: list[float] = []
    for index in range(20):
        drawn = nl.draw_replicate(setup, small("gamma"), TEST_SEED, index)
        factors.extend(
            (t.sx_factor - 1.0) * setup.slopes[j] for j, t in zip(drawn.calibration, drawn.truths, strict=True)
        )
    check(
        abs(float(np.mean(factors)) - 0.011) < 0.004 and abs(float(np.std(factors)) - 0.0105) < 0.003,
        f"{np.mean(factors)}",
    )


def test_readers_carry_the_planted_excitation_and_read_zero_without_it(setup: nl.Setup) -> None:
    ctx = setup.contexts[2]
    generator = np.random.default_rng(TEST_SEED)
    contrast = 1 - ctx["e01"] - ctx["e10"]
    for reader in (0.0, 0.05):
        truth = nl.Truth(ctx["t1_cal_s"], math.inf, 1.0, 1.0, {}, reader, 0.0)
        probabilities = nl.member_probabilities(ctx, 5, truth, setup.equilibrium_s)
        predecessors, readers, ones = nl.draw_bits(generator, ctx, truth, probabilities, 5, setup.shots)
        readout = {"scale": contrast, "offset": ctx["e10"] - ctx["e01"]}
        out = su.carryover_reader(predecessors, readers, readout, 1.0, 32)
        check(abs(out["d"] - reader) < 4 * out["se"], f"planted {reader}: {out['d']} +- {out['se']}")
        check(
            all(
                abs(int(p.sum()) - probabilities[nl.predecessor_name(i, 5)] * SHOTS) < 6 * math.sqrt(SHOTS) / 2
                for i, p in enumerate(predecessors)
            ),
            "a predecessor row leaves its member's probability",
        )
        check(ones == [int(p.sum()) for p in predecessors], "the predecessor counts are not the bits")


def test_the_measure_rows_and_the_reader_prefixes_are_separate_draws(setup: nl.Setup) -> None:
    """Production reads the N = 2, 4 and 8 measure rows and the reader circuits' prefixes from separate PUBs, so the
    rows the fit reads share no sample with the carryover strata."""
    drawn = nl.draw_replicate(setup, small("gamma"), TEST_SEED, 0)
    for slot, qubit in enumerate(setup.qubits[: len(drawn.counts)]):
        final = drawn.counts[slot]["final"]
        prefixes = [int(p.sum()) for p in drawn.predecessors[slot]]
        rows = [final[nl.predecessor_name(i, qubit)][0] for i in range(nl.READERS)]
        check(rows != prefixes, f"q{qubit}: the measure rows are the reader prefixes")


def test_a_replicate_is_a_function_of_seed_and_index(setup: nl.Setup) -> None:
    case = small("gamma")
    a, b, c = (nl.draw_replicate(setup, case, TEST_SEED, i) for i in (0, 0, 1))
    check(a.counts == b.counts and a.calibration == b.calibration, "one index drew twice differently")
    check(a.counts != c.counts, "two indices drew the same counts")
    check(all((x == y).all() for x, y in zip(a.readers[0], b.readers[0], strict=True)), "reader bits differ")


def block_equals_reference(setup: nl.Setup, case: nl.Case, indices: list[int]) -> None:
    detail = nl.analyse_detail((setup, case, TEST_SEED, indices))
    for (summary, selection, state), index in zip(detail, indices, strict=True):
        ref_summary, ref_selection, ref_state = nl.reference_replicate(setup, case, TEST_SEED, index)
        for name, got, want in (
            ("summary", summary, ref_summary),
            ("selection", selection, ref_selection),
            ("screens", state.screens, ref_state.screens),
            ("rows", state.rows, ref_state.rows),
        ):
            check(canon(got) == canon(want), f"replicate {index}: {name} differs from the scalar pipeline")


def test_block_equals_the_scalar_pipeline_through_the_settle_veto(setup: nl.Setup) -> None:
    block_equals_reference(setup, small("settle-common", 8), [0])


def test_block_equals_the_scalar_pipeline_through_the_carryover_screen(setup: nl.Setup) -> None:
    block_equals_reference(setup, small("carryover-positive", 8), [0])


def test_block_equals_the_scalar_pipeline_through_the_equilibrium_bound(setup: nl.Setup) -> None:
    block_equals_reference(setup, small("plateau-low", 8), [0])


def test_blocking_leaves_the_rows_alone(setup: nl.Setup) -> None:
    case = small("carryover-negative")
    whole = nl.analyse_block((setup, case, TEST_SEED, [0, 1, 2, 3]))
    parts = nl.analyse_block((setup, case, TEST_SEED, [0, 1])) + nl.analyse_block((setup, case, TEST_SEED, [2, 3]))
    check(whole == parts, "a replicate depends on its block")


def test_the_healthy_arm_issues_verdicts(setup: nl.Setup) -> None:
    rows = nl.analyse_block((setup, small("gamma", 12), TEST_SEED, [0, 1, 2, 3]))
    check(sum(row["issued"] for row in rows) >= 3, f"{[row['issued'] for row in rows]}")
    check(all(row["selected"] >= 8 for row in rows if row["issued"]), "a verdict without eight selected qubits")


def test_upper_bound_of_zero_fires_crosses_the_ceiling_at_299() -> None:
    check(nl.upper_bound(0, 299) < nl.FALSE_FIRE_CEILING <= nl.upper_bound(0, 298), "299 is not the zero-fire count")
    check(nl.upper_bound(5, 5) == 1.0, "all fires bound at one")


def test_two_shards_merge_to_the_bytes_of_one_run(setup: nl.Setup) -> None:
    cases = [small("gamma", 8, 0.0)]
    whole = nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, cases=cases, record_name="r")])
    halves = [nl.run_arm(setup, "gamma", TEST_SEED, 2, k, 2, cases=cases, record_name="r") for k in (0, 1)]
    check(nl.dumps(nl.merge_records(halves)) == nl.dumps(nl.merge_records(halves[::-1])), "merge depends on order")
    check(nl.dumps(nl.merge_records(halves)) == nl.dumps(whole), "two shards differ from one run")
    check(whole["replicates"] == {"8-qubits": 2}, f"{whole['replicates']}")


def test_the_verdict_requirement_cuts_every_sharding_at_one_replicate(
    setup: nl.Setup, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One replicate a round: the 9-qubit case issues its verdict at its first replicate, below the cap of 2.
    monkeypatch.setattr(nl, "ROUND", 1)
    cases = [small("gamma", 9, 0.0)]
    whole = nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, cases=cases, needed=1)])
    halves = nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, k, 2, cases=cases, needed=1) for k in (0, 1)])
    check(nl.dumps(whole) == nl.dumps(halves), "the cut depends on the sharding")
    rows = whole["cases"]["9-qubits"]["rows"]
    check(len(rows) == 1 and rows[0]["issued"], "the 9-qubit case did not stop at its first verdict")


def test_each_case_stops_at_its_own_verdict_count(setup: nl.Setup, monkeypatch: pytest.MonkeyPatch) -> None:
    # The 6-qubit case issues no verdict and runs to the cap while the 9-qubit case stops at its first.
    monkeypatch.setattr(nl, "ROUND", 1)
    cases = [small("gamma", 9, 0.0), small("gamma", 6, 0.0)]
    whole = nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, cases=cases, needed=1)])
    check(whole["replicates"] == {"9-qubits": 1, "6-qubits": 2}, f"{whole['replicates']}")


def test_a_limit_leaves_the_merged_bytes_and_refuses_a_case_it_cuts_short(
    setup: nl.Setup, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The 9-qubit case issues its verdict at its first replicate, so a limit of 1 changes no byte of the cap-2 run,
    # while at a count of 2 the same limit stops it short of both its count and its cap.
    monkeypatch.setattr(nl, "ROUND", 1)
    cases = [small("gamma", 9, 0.0)]
    whole = nl.dumps(nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, cases=cases, needed=1)]))

    def sharded(needed: int) -> dict[str, Any]:
        run = nl.ArmRun("gamma", TEST_SEED, 2, cases=cases, needed=needed, limits={"9-qubits": 1})
        return nl.merge_records([nl.run_arms(setup, [run], k, 2)[0] for k in (0, 1)])

    check(nl.dumps(sharded(1)) == whole, "a limit at the verdict cut changed the record")
    with pytest.raises(ValueError, match="larger --limit"):
        sharded(2)
    with pytest.raises(ValueError):
        nl.run_arms(setup, [nl.ArmRun("gamma", TEST_SEED, 2, cases=cases, limits={"7-qubits": 1})])


def test_the_round_size_leaves_the_record_bytes_unchanged(setup: nl.Setup, monkeypatch: pytest.MonkeyPatch) -> None:
    # A round of one replicate stops the 9-qubit case at its first verdict; a round of two blocks runs it past.
    cases = [small("gamma", 9, 0.0)]
    records = []
    for size in (1, 2 * nl.NULL_BLOCK):
        monkeypatch.setattr(nl, "ROUND", size)
        records.append(nl.dumps(nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2, cases=cases, needed=1)])))
    check(records[0] == records[1], "the round size changed the record")


def test_a_computed_round_gives_every_worker_whole_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nl, "ROUND", None)
    monkeypatch.setattr(nl, "workers", lambda: 12)
    check(nl.round_size(1) == 24 * nl.NULL_BLOCK and nl.round_size(3) == 8 * nl.NULL_BLOCK, "worker blocks")
    check(nl.round_size(25) == nl.NULL_BLOCK, "a round holds at least one block per case")


def test_one_pool_writes_each_arm_the_bytes_of_its_own_run(setup: nl.Setup, monkeypatch: pytest.MonkeyPatch) -> None:
    # The gamma case stops at its first verdict while the settle case shares its rounds and runs to the cap.
    monkeypatch.setattr(nl, "ROUND", 1)
    gamma = nl.ArmRun("gamma", TEST_SEED, 2, cases=[small("gamma", 9, 0.0)], needed=1)
    settle = nl.ArmRun("settle-common", TEST_SEED, 2, cases=[small("settle-common", 8, 0.0)])
    joint = [nl.dumps(nl.merge_records([record])) for record in nl.run_arms(setup, [gamma, settle])]
    alone = [nl.dumps(nl.merge_records([nl.run_arms(setup, [run])[0]])) for run in (gamma, settle)]
    check(joint == alone, "an arm's record depends on the arms it shares the pool with")
    with pytest.raises(ValueError):
        nl.run_arms(setup, [gamma, gamma])


def test_an_explicit_single_shard_writes_a_shard_record(setup: nl.Setup, tmp_path: Path) -> None:
    import msq_successor_null

    run = nl.ArmRun("gamma", TEST_SEED, 1, cases=[small("gamma", 8, 0.0)])
    records = nl.run_arms(setup, [run], 0, 1)
    msq_successor_null.write_arm_records(tmp_path / "shards", records, 0)
    msq_successor_null.write_arm_records(tmp_path / "whole", records, None)
    shard = json.loads((tmp_path / "shards" / "gamma-shard0.json").read_text())
    check(sorted(path.name for path in (tmp_path / "shards").iterdir()) == ["gamma-shard0.json"], "shard name")
    check(nl.dumps(nl.merge_records([shard])) == (tmp_path / "whole" / "gamma.json").read_text(), "merge differs")


def test_the_null_plan_names_every_arm_once_at_its_seed() -> None:
    import msq_successor_null

    import qrng_seeds

    check([arm for arm, _, _ in nl.NULL_PLAN] == list(nl.ARMS), "NULL_PLAN differs from ARMS")
    spellings = {arm: spelling for arm, _, spelling in nl.NULL_PLAN if spelling is not None}
    check(set(spellings) == {"settle-sparse"}, f"{spellings}")
    seed, _ = qrng_seeds.parse_value(spellings["settle-sparse"], [])
    check(seed == nl.SPARSE_CONFIRMATION_SEED, f"the settle-sparse spelling resolves to {seed}")
    runs = msq_successor_null.plan_runs(["all"], ["gamma=37"], "r")
    check([run.arm for run in runs] == list(nl.ARMS), "--arms all runs every arm in ARMS order")
    by_arm = {run.arm: run for run in runs}
    check(by_arm["gamma"].cap == 37 and by_arm["plateau-retained"].cap == 20000, "caps")
    check(by_arm["settle-sparse"].seed == nl.SPARSE_CONFIRMATION_SEED, "the settle-sparse seed")
    check(by_arm["settle-sparse"].seed_source["sources"] == [spellings["settle-sparse"]], "the seed spelling")
    check(by_arm["gamma"].seed == nl.SUCCESSOR_NULL_SEED and by_arm["gamma"].seed_source["sources"] == ["default"], "")
    for bad in (["gamma=0"], ["gamma=x"], ["q-tolerance=5"]):
        with pytest.raises(ValueError):
            msq_successor_null.plan_runs(["gamma"], bad, "r")
    limited = msq_successor_null.plan_runs(
        ["settle-sparse"], [], "r", ["settle-sparse=50", "settle-sparse/8-qubits=90"]
    )
    labels = {"8-qubits", "9-qubits", "24-qubits"}
    check(
        msq_successor_null.expand_limits(limited[0], labels) == {"8-qubits": 90, "9-qubits": 50, "24-qubits": 50},
        "an ARM=N limit covers the cases without their own",
    )
    with pytest.raises(ValueError):
        msq_successor_null.expand_limits(limited[0]._replace(limits={"7-qubits": 5}), labels)
    for bad in (["gamma/x=0"], ["q-tolerance=5"]):
        with pytest.raises(ValueError):
            msq_successor_null.plan_runs(["gamma"], [], "r", bad)


def test_merge_refuses_incomplete_or_mismatched_shards(setup: nl.Setup) -> None:
    cases = [small("gamma", 8, 0.0)]
    one = nl.run_arm(setup, "gamma", TEST_SEED, 2, 0, 2, cases=cases)
    for bad in ([one], [one, {**one, "cap": one["cap"] + 1}]):
        with pytest.raises(ValueError):
            nl.merge_records(bad)


def test_the_record_names_its_inputs_and_reports_the_arm_statistics(setup: nl.Setup) -> None:
    cases = [small("settle-common", 8, 0.0)]
    record = nl.merge_records(
        [nl.run_arm(setup, "settle-common", TEST_SEED, 2, seed_source="default", record_name="r", cases=cases)]
    )
    check(record["schema"] == nl.SCHEMA and record["arm"] == "settle-common" and record["seed"] == TEST_SEED, "")
    check(record["snapshot_sha256"] == setup.digests["snapshot_sha256"], "snapshot digest")
    stats = record["cases"]["8-qubits"]
    check(
        stats["replicates"] == 2
        and "false_fire_upper_95" in stats
        and "common_veto_power_at_least_90_percent" in stats["targets"],
        f"{list(stats)}",
    )
    check(record["cases"]["8-qubits"]["common_veto_rate"] == 1.0, "a 4 x floor common gap escaped the veto")


def test_the_summary_keeps_each_record_digest_and_drops_the_rows(setup: nl.Setup) -> None:
    cases = [small("settle-common", 8, 0.0)]
    shard = nl.run_arm(setup, "settle-common", TEST_SEED, 2, seed_source="default", record_name="r", cases=cases)
    text = nl.dumps(nl.merge_records([shard]))
    summary = nl.null_summary([text])
    (entry,) = summary["records"]
    check(
        summary["schema"] == nl.SUMMARY_SCHEMA and entry["record_sha256"] == hashlib.sha256(text.encode()).hexdigest(),
        "",
    )
    check("rows" not in entry["cases"]["8-qubits"] and entry["cases"]["8-qubits"]["replicates"] == 2, f"{entry}")
    check(all(entry[key] == shard[key] for key in nl.IDENTITY), "identity")
    with pytest.raises(ValueError, match="shard record"):
        nl.null_summary([nl.dumps(shard)])
    stale = json.loads(text)
    stale["cases"]["8-qubits"]["targets"] = {}
    with pytest.raises(ValueError, match="merge the record again"):
        nl.null_summary([nl.dumps(stale)])


@pytest.mark.parametrize("arm", nl.ARMS)
def test_every_arm_completes_a_small_run(setup: nl.Setup, arm: str) -> None:
    cases = nl.arm_cases(arm, setup.width)
    check(len(cases) == {"carryover-boundary": 3, "settle-common": 3, "settle-sparse": 3}.get(arm, 1), arm)
    rows = nl.analyse_block((setup, cases[-1]._replace(active=8), TEST_SEED, [0]))
    check(len(rows) == 1 and rows[0]["i"] == 0, arm)


@pytest.mark.audit
def test_pooled_and_serial_runs_write_the_same_bytes(setup: nl.Setup, monkeypatch: pytest.MonkeyPatch) -> None:
    cases = [small("gamma", 8, 0.0)]
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    serial = nl.dumps(nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2 * nl.NULL_BLOCK, cases=cases)]))
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    pooled = nl.dumps(nl.merge_records([nl.run_arm(setup, "gamma", TEST_SEED, 2 * nl.NULL_BLOCK, cases=cases)]))
    check(serial == pooled, "pooled and serial runs differ")


# --- shots from the record, several records through one pool, per-calibration sparse evidence ------------------


def shots_record(target: Path, shots: int | None, width: int = 8) -> Path:
    """A copy of the fixture record directory with `shots` in place (None removes the field), cut to its first
    `width` layout qubits so a setup builds in about a second."""
    shutil.copytree(RECORD, target)
    path = target / "record.json"
    record = json.loads(path.read_text())
    configuration = record["family_configuration"]
    if shots is None:
        del record["shots"]
    else:
        record["shots"] = shots
    configuration["qubits"] = configuration["qubits"][:width]
    configuration["layout_width"] = width
    configuration["pattern_bits"] = [row[:width] for row in configuration["pattern_bits"]]
    path.write_text(json.dumps(record, sort_keys=True, indent=1) + "\n")
    return target


@pytest.fixture(scope="module")
def minis(tmp_path_factory: pytest.TempPathFactory) -> dict[int, nl.Setup]:
    """An 8-qubit setup built from a record with 4096 shots, and the same setup at 8192 shots, whose constants stay
    those of the 4096-shot build: the tests that use it read only the draws and the record fields."""
    built = nl.build_setup(shots_record(tmp_path_factory.mktemp("minis") / "s4096", 4096), ())
    return {4096: built, 8192: built._replace(shots=8192)}


def test_a_setup_draws_its_counts_out_of_the_records_shots(minis: dict[int, nl.Setup]) -> None:
    for shots, mini in minis.items():
        check(mini.shots == shots, f"{mini.shots}")
        drawn = nl.draw_replicate(mini, small("gamma"), TEST_SEED, 0)
        members = [count for counts in drawn.counts for count in counts["final"].values()]
        check(bool(members) and all(0 <= ones <= total == shots for ones, total in members), f"shots {shots}")
        check(all(total == shots and 0 <= ones <= shots for ones, total in drawn.equilibrium), "equilibrium")
        check(all(total == shots for row in drawn.patterns for _, total in row), "patterns")
        check(all(len(bits) == shots for row in drawn.readers + drawn.predecessors for bits in row), "reader bits")


def test_a_record_without_shots_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="shots"):
        nl.build_setup(shots_record(tmp_path / "bare", None))


def test_the_reader_standard_error_grows_with_the_root_of_the_shot_deficit(setup: nl.Setup) -> None:
    ctx = setup.contexts[2]
    errors = {}
    for shots in (4096, 8192):
        counts = msa.device_counts({0: msa.device_model(ctx, p_init=0.0)}, {0: ctx}, shots)[0]["final"]
        ones = [counts[nl.predecessor_name(i, 0)][0] for i in range(nl.READERS)]
        errors[shots] = nl.reader_standard_error(ctx, ones, 0.01, shots)
    ratio = errors[4096] / errors[8192]
    check(abs(ratio - math.sqrt(2)) < 0.03, f"standard error ratio {ratio} against sqrt(2)")


def test_records_carry_their_shots_and_mixed_shots_do_not_merge(minis: dict[int, nl.Setup]) -> None:
    runs = {shots: nl.run_arm(mini, "gamma", TEST_SEED, 1, 0, 2, record_name="r") for shots, mini in minis.items()}
    other = nl.run_arm(minis[8192], "gamma", TEST_SEED, 1, 1, 2, record_name="r")
    check(runs[4096]["schema"] == nl.SCHEMA == "msq-successor-null-v2", f"{runs[4096]['schema']}")
    check([runs[4096]["shots"], runs[8192]["shots"]] == [4096, 8192], "the records name their shots")
    nl.merge_records([runs[8192], other])
    with pytest.raises(ValueError, match="shots"):
        nl.merge_records([runs[4096], other])


def test_the_summary_reads_a_v1_record_and_writes_v2(minis: dict[int, nl.Setup]) -> None:
    record = nl.merge_records([nl.run_arm(minis[8192], "gamma", TEST_SEED, 1, record_name="r")])
    legacy = {key: value for key, value in record.items() if key != "shots"} | {"schema": nl.LEGACY_SCHEMA}
    text = nl.dumps(legacy)
    (entry,) = nl.null_summary([text])["records"]
    check(nl.null_summary([text])["schema"] == "msq-successor-null-summary-v2", "summary schema")
    check(entry["schema"] == nl.LEGACY_SCHEMA and entry["shots"] == nl.LEGACY_SHOTS, f"{entry['shots']}")
    check(entry["record_sha256"] == hashlib.sha256(text.encode()).hexdigest(), "digest")
    (current,) = nl.null_summary([nl.dumps(record)])["records"]
    check(current["schema"] == nl.SCHEMA and current["shots"] == 8192, "a v2 record keeps its shots")
    with pytest.raises(ValueError, match="unknown record schema"):
        nl.null_summary([nl.dumps({**legacy, "schema": "msq-successor-null-v0"})])


def test_the_per_calibration_sparse_record_is_found_before_the_legacy_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(nl, "ROOT", tmp_path)
    digest = "ab" * 32
    check(nl.sparse_scales(digest, 24, 4096) == ({}, ""), "an empty tree holds a scale")
    legacy = tmp_path / nl.SPARSE_SCALE_EVIDENCE
    legacy.parent.mkdir(parents=True)
    legacy.write_text(json.dumps({"snapshot_sha256": digest, "layout_width": 24, "pools": {"8": {"scale": 1.25}}}))
    check(nl.sparse_scales(digest, 24, 8192)[0] == {8: 1.25}, "the legacy record is the 8192-shot calibration")
    check(nl.sparse_scales(digest, 24, 4096) == ({}, ""), "the legacy record serves another shot count")
    path = nl.sparse_evidence_path(digest, 24, 4096)
    check(path.name == f"{digest[:16]}-w24-s4096.json" and path.parent.name == "successor-sparse-scale", f"{path}")
    path.parent.mkdir(parents=True)
    body = {"snapshot_sha256": digest, "layout_width": 24, "shots": 4096, "pools": {"8": {"scale": 1.5}}}
    path.write_text(json.dumps(body))
    scales, sha = nl.sparse_scales(digest, 24, 4096)
    check(scales == {8: 1.5} and sha == hashlib.sha256(path.read_bytes()).hexdigest(), f"{scales}")
    check(nl.sparse_scales(digest, 24, 8192)[0] == {8: 1.25}, "the per-calibration file shadows another shot count")
    check(nl.sparse_scales(digest, 24, 2048) == ({}, ""), "a shot count with no calibration finds nothing")
    check(nl.sparse_scales(digest, 32, 4096) == ({}, ""), "a layout width with no calibration finds nothing")
    path.write_text(json.dumps({**body, "shots": 2048}))
    with pytest.raises(ValueError, match="than its name"):
        nl.sparse_scales(digest, 24, 4096)


def pool_scaled_power(items: Any, _seed: int, _replicates: int) -> list[tuple[int, int]]:
    """A stand-in for nl.sparse_powers whose power rises with the scale and falls with the pool size."""
    return [(round(1000 * (0.3 + 0.2 * scale * 8 / pool)), 1000) for _, pool, scale in items]


def test_calibrations_in_one_pool_equal_their_own_calibrations(
    minis: dict[int, nl.Setup], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(nl, "sparse_powers", pool_scaled_power)
    jobs = [(minis[4096], 8), (minis[8192], 9), (minis[4096], 9)]
    together = nl.calibrate_sparse_many(jobs, nl.SPARSE_CALIBRATION_SEED, 10)
    alone = [nl.calibrate_sparse_scale(setup, pool, nl.SPARSE_CALIBRATION_SEED, 10) for setup, pool in jobs]
    check(together == alone and len({round(r["scale"], 6) for r in together}) > 1, f"{together}")
    records = nl.sparse_calibration_records([minis[4096], minis[8192]], nl.SPARSE_CALIBRATION_SEED, "x", ["a", "b"], 10)
    check([r["shots"] for r in records] == [4096, 8192] and all(set(r["pools"]) == {"8", "9"} for r in records), "")
    check(records[0]["pools"]["8"]["scale"] == together[0]["scale"], "the record holds the job's scale")


def test_a_calibration_record_sets_the_scales_and_digest_a_later_build_reads(minis: dict[int, nl.Setup]) -> None:
    record = {"pools": {"8": {"scale": 1.25}}}
    (applied,) = nl.with_calibrated_scales([minis[4096]], [record])
    check(applied.sparse_scale == {8: 1.25}, f"{applied.sparse_scale}")
    check(applied.digests["sparse_scale_sha256"] == hashlib.sha256(nl.dumps(record).encode()).hexdigest(), "digest")
    check(all(set(losses) == {8} and losses[8] > 0 for losses in applied.sparse_loss), f"{applied.sparse_loss}")


def test_one_call_runs_each_setup_to_the_bytes_of_its_own_run(
    minis: dict[int, nl.Setup], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(nl, "ROUND", 1)
    cases = [small("gamma", 8, 0.0)]
    runs = [
        nl.ArmRun("gamma", TEST_SEED, 2, "default", name, cases=cases, setup=minis[shots])
        for name, shots in (("narrow", 4096), ("wide", 8192))
    ]
    joint = [nl.dumps(nl.merge_records([record])) for record in nl.run_arms(None, runs)]
    alone = [nl.dumps(nl.merge_records(nl.run_arms(None, [run]))) for run in runs]
    check(joint == alone, "a record depends on the setups it shares the pool with")
    check([json.loads(text)["shots"] for text in joint] == [4096, 8192] and joint[0] != joint[1], "")
    with pytest.raises(ValueError, match="twice"):
        nl.run_arms(None, [runs[0], runs[0]._replace(record_name="again")])
    with pytest.raises(ValueError, match="names no setup"):
        nl.run_arms(None, [runs[0]._replace(setup=None)])


def test_the_command_writes_one_record_per_directory_and_a_single_record_flat(
    minis: dict[int, nl.Setup], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import msq_successor_null

    by_name = {"a": minis[4096], "b": minis[8192]}
    monkeypatch.setattr(nl, "build_setup", lambda path, _pools=None: by_name[path.name])
    many, flat = tmp_path / "many", tmp_path / "flat"
    argv = ["--arms", "gamma", "--cap", "gamma=1"]
    msq_successor_null.main(["a", "b", *argv, "--cap", "b:gamma=2", "--out-dir", str(many)])
    check(sorted(path.name for path in many.iterdir()) == ["a", "b"], "one directory per record")
    narrow, wide = (json.loads((many / name / "gamma.json").read_text()) for name in ("a", "b"))
    check(narrow["record"] == "a" and narrow["shots"] == 4096 and narrow["cap"] == 1, f"{narrow['cap']}")
    check(wide["record"] == "b" and wide["shots"] == 8192 and wide["cap"] == 2, f"{wide['cap']}")
    msq_successor_null.main(["a", *argv, "--out-dir", str(flat)])
    check(sorted(path.name for path in flat.iterdir()) == ["gamma.json"], "a single record writes DIR/ARM.json")
    check((flat / "gamma.json").read_bytes() == (many / "a" / "gamma.json").read_bytes(), "the bytes differ")
    with pytest.raises(SystemExit):
        msq_successor_null.main(["a", "b", "--arms", "gamma", "--cap", "c:gamma=1", "--out-dir", str(flat)])
    check(
        msq_successor_null.for_record(["gamma=3", "b:gamma=2", "a:q-tolerance=4"], "a", ["a", "b"])
        == [
            "gamma=3",
            "q-tolerance=4",
        ],
        "the record prefix targets one record",
    )


def test_the_command_calibrates_each_record_to_its_own_sparse_path(
    minis: dict[int, nl.Setup], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import msq_successor_null

    by_name = {"a": minis[4096], "b": minis[8192]}
    monkeypatch.setattr(nl, "build_setup", lambda path, _pools=None: by_name[path.name])
    monkeypatch.setattr(nl, "sparse_powers", pool_scaled_power)
    monkeypatch.setattr(nl, "ROOT", tmp_path)
    monkeypatch.setattr(nl, "with_calibrated_scales", lambda setups, _records: list(setups))
    msq_successor_null.main(["a", "b", "--calibrate-sparse"])
    digest = minis[4096].digests["snapshot_sha256"]
    for shots, name in ((4096, "a"), (8192, "b")):
        written = json.loads(nl.sparse_evidence_path(digest, 8, shots).read_text())
        check(written["shots"] == shots and written["record"] == name and set(written["pools"]) == {"8", "9"}, name)
    with pytest.raises(SystemExit):
        msq_successor_null.main(["a", "b", "--calibrate-sparse", "--out", str(tmp_path / "x.json")])
