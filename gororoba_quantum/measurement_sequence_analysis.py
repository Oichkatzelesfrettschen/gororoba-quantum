"""Preregistered analysis of the measurement-sequence pinching family on a Heron r2 backend.

The family (diagnostic_experiments.MSQ_*) drives each named qubit with N rotations of THETA / N about X,
THETA = 8 pi / 9, and reads a final Z measurement. The measure arm follows each rotation with a discarded
mid-circuit measurement, the delay arm with an idle of the Target's measure duration, the unitary arm (N = 16) with
a barrier, and the settle arm (N = 16) with the measurement and a further 2 us idle. A pinched qubit's Bloch z
shrinks by cos(THETA / N) per step, so the ideal measure-arm P0 is (1 + cos(THETA / N) ** N) / 2.

Readout. The family runs with no twirling and no dynamical decoupling, so the static job (ro0, the t1 series with
the x member at idle 0 as ro1, the delay and unitary arms) and the dynamic job (measure and settle arms) read
through the same unsymmetrized `measure` after the same 2 us pre-readout idle. ro0 and ro1 fix the readout offset
and scale of that channel, the correction (Zobs - o) / s returns the true z before the wait, and the t1 series fits
T1 and q = z_eq / (1 - 2 p) in the job. The correction transfers to the dynamic job only when both jobs executed
under one calibration (qpu_planning.measured_family withholds the analysis otherwise). The final read that follows
a mid-circuit measurement can carry a readout history that ro0 and ro1 do not; the family has no N = 1 measure
member, so no in-job diagnostic separates that bias from a pinching departure.

Model. The Bloch iteration plays each RX step as the compiled rz(pi/2) sx rz(THETA/N + pi) sx rz(pi/2) with T1 and T2
acting during each sx and a depolarizing remainder of the Target's sx error after it (e_sx is read at execution), so
the state crosses the equator inside every step and T2 decays what a pinched qubit holds in z. The arm then pinches
(measure and settle arms) or stays coherent (delay and unitary arms) and relaxes with T1 and T2 over its idle. The
pre-readout idle relaxation is affine in z, so ro0 and ro1, which wait as long, calibrate it away.

Decisions, per qubit, from the readout-corrected final P0 pooled over the four signed members:

- the mutation test passes when the N = 16 contrast measure minus unitary exceeds CONTRAST_MIN by Z_DECIDE
  standard errors;
- the departure test compares the measure arm's N = 16 P0 with the ideal-projective prediction at the fitted T1
  and q, with two systematics: SX_SYSTEMATIC times the Target's sx error, and the gate-model systematic below, and
  names `departs_below`, `consistent` or `exceeds_prediction` at Z_DECIDE standard errors;
- the settle test compares the settle arm's N = 16 P0 with the prediction at the per-step z loss the measure arm
  implies. The gap is an experimental hypothesis (the repository's Heron r2 sources report no ring-down time), so
  the test asks only whether lengthening the gap after each measurement from zero to 2 us changes the deficit:
  `reduced_by_gap` (z >= Z_DECIDE), `unchanged_by_gap` or `deepened_by_gap`. `unchanged_by_gap` bounds only a
  tail component that decays within 2 us; a slower tail stays unexcluded;
- a qubit whose readout scale lies below READOUT_CONTRAST_FLOOR makes no decision.

Device verdicts (device_verdict) are the decisions. Only informative qubits count: usable, mutation test passed and
widened departure standard error within PLANNING_SE_FACTOR times the planning value. With fewer than DEVICE_QUBITS
informative qubits every verdict reads `uninformative`, so `none` always means a clean null. Otherwise a verdict
fires when at least DEVICE_QUBITS informative qubits return the per-qubit verdict or the pooled z reaches Z_DECIDE;
the pooled z adds the shared systematics linearly (pooled_z).

Gate-model systematic. The unitary arm (thirty-two sx, no measurement, no idle) tests the gate model in the job. Its
measured-minus-modeled N = 16 residual does not veto a run; it bounds what a gate-model error can do to the measure
arm. For each error class (GATE_CLASSES: depolarizing error, dephasing during the drive, a relative tilt between the
two sx of a pair, an over-rotation of the pi / 2 pulse) gate_propagation finds the class magnitude that reproduces
the residual and the shift that magnitude produces in the measure arm's N = 16 P0 (the propagation ratio is that
shift over the residual). The largest shift over the classes adds in quadrature to the departure standard error,
and so does the shift a residual equal to the root-mean-square of the usable qubits' residuals, floored at
MODEL_SCATTER_FLOOR, would carry (widen_for_device_scatter), which keeps two errors that cancel in one qubit's
unitary arm from hiding. Pooling uses the inflated variances, so a badly modeled qubit down-weights itself.

The module draws no random number; its sweep runs on expected counts rounded to whole shots.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import sys
from collections.abc import Callable
from typing import Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq, minimize_scalar

from parallel import ordered_map

FAMILY = "measurement-sequence"
SCHEMA = "measurement-sequence-analysis-v1"
THETA = 8.0 * math.pi / 9.0
STEPS = (1, 2, 4, 8, 16)
MEASURE_STEPS = (2, 4, 8, 16)
TOP_STEPS = 16
ARMS = ("measure", "delay", "unitary", "settle")
ARM_STEPS = {"measure": MEASURE_STEPS, "delay": STEPS, "unitary": (TOP_STEPS,), "settle": (TOP_STEPS,)}
PINCHED_ARMS = ("measure", "settle")
SIGNED = ("pa", "ma", "mb", "pb")
T1_COUNT = 5

Z_DECIDE = 3.0
# Correction divides by the fitted readout scale, so a scale near zero diverges the corrected P0 and its errors.
READOUT_CONTRAST_FLOOR = 0.5
CONTRAST_MIN = 0.5
# The sx error is a randomized-benchmarking average over other sequences, so its relative one-sigma uncertainty
# enters every standard error as a systematic.
SX_SYSTEMATIC = 1.0
DEVICE_QUBITS = 2
# Shots per PUB of the smallest admitted tier, the shots the planning standard error assumes.
PLANNING_SHOTS = 8192
# The floor on the unitary-arm residual scale (in P0) that widens every informative qubit's departure standard error.
# Two gate-model errors of opposite unitary sign cancel in the unitary arm and add in the measure arm, so the residual
# observed on a few qubits can sit at zero while the measure arm moves; the floor is the model scatter that a
# population of qubits shows. No retained Kingston run holds a single-qubit sx sequence with a known ideal outcome, so
# no measured scatter exists and the floor stays None: with it unset, a fired departure or exceedance verdict reads
# `gate_model_unbounded` and nothing is attributed. A small Heron diagnostic (the unitary arm on many qubits) would
# measure it; the value then replaces None here, with the run and the computation cited in docs/design.
MODEL_SCATTER_FLOOR: float | None = None
# An illustrative floor for the sweeps and the Aer validation, which exercise the mechanism. It is not a measurement
# of any device: the largest floor for which PLANNING_SE_FACTOR still leaves a qubit informative at the fixture is
# about 0.0175, and 0.015 keeps an axis tilt of -0.016 rad against an sx error of three times the Target's unattributed.
DEMONSTRATION_SCATTER_FLOOR = 0.015
# A qubit whose widened departure standard error exceeds this multiple of the planning standard error (the standard
# error at the planning model including the scatter floor, when one is set) is uninformative.
PLANNING_SE_FACTOR = 2.0
# Initial excitation bound after the implicit reset at the 250 us repetition delay: eps250 = 0.015745 at q125, the
# largest of 447 simultaneous Clopper-Pearson bounds over 149 qubits on ibm_kingston
# (results/live/N21_STATE_PREP_AND_FEEDBACK_FINDINGS.md, "Initialization bound that set the plan"). Only the
# planning tables assume it; the analysis fits q from the t1 series.
PLANNING_P_INIT = 0.015745
# Fraction of the mid-circuit measure duration during which the post-measurement state relaxes. The Target's
# measure duration spans the readout pulse and integration, and the projection falls somewhere inside it, so the
# fraction lies in [0, 1] with no calibrated value; the analysis takes the midpoint with the variance of a uniform
# distribution on [0, 1] as a systematic. The Aer noise model of a backend (NoiseModel.from_backend) charges no
# relaxation during a measure instruction, the fraction 0.
WINDOW_RELAX_FRACTION = 0.5
WINDOW_RELAX_VARIANCE = 1 / 12
P_INIT_SENSITIVITY = (0.0, 0.01, 0.02, 0.05, 0.1)
T1_BOUNDS = (1e-6, 1e-2)
FIT_GRID = [-0.05 + 0.005 * i for i in range(101)]


class AnalysisError(ValueError):
    pass


def check(condition: bool, message: str) -> None:
    """Raise on a false condition; python -O strips assert, so every check raises explicitly."""
    if not condition:
        raise AnalysisError(message)


# --- ideal laws ---------------------------------------------------------------------------------------------


def ideal_measure(n: int) -> float:
    """Final P0 of the pinched chain of n rotations of THETA / n."""
    return (1 + math.cos(THETA / n) ** n) / 2


def ideal_delay() -> float:
    """Final P0 of the coherent chain, which composes to one rotation of THETA."""
    return (1 + math.cos(THETA)) / 2


def ideal_arm(arm: str, n: int) -> float:
    return ideal_measure(n) if arm in PINCHED_ARMS else ideal_delay()


def ideal_flip(n: int) -> float:
    """Probability that consecutive mid-circuit outcomes differ: a pinched qubit rotates by THETA / n."""
    return math.sin(THETA / (2 * n)) ** 2


def member_names(arm: str, n: int, qubit: int) -> list[str]:
    return [f"msq_{arm}_n{n}_{tag}_q{qubit}" for tag in SIGNED]


def group_keys() -> list[tuple[str, int]]:
    return [(arm, n) for arm in ARMS for n in ARM_STEPS[arm]]


def t1_names(qubit: int) -> list[str]:
    return [f"msq_t1_d{k}_q{qubit}" for k in range(T1_COUNT)]


def ro0_name(qubit: int) -> str:
    return f"msq_ro0_q{qubit}"


# --- Bloch model --------------------------------------------------------------------------------------------


def sx_depolarizing_error(ctx: dict[str, Any]) -> float:
    """The part of the Target's average sx error that relaxation during the gate does not explain.

    A gate that relaxes with T1 and T2 for its duration t has average infidelity t / (3 T2) + t / (6 T1) to first
    order. The Bloch iteration evolves each sx with T1 and T2 acting during the gate, so the depolarizing
    remainder is the reported error less this, never below zero. The reported error is a randomized-benchmarking
    average that can sit below the relaxation limit (a short Ramsey T2), so the clipped remainder carries no
    sensitivity to the reported error; the sx systematic therefore enters as an absolute shift of the remainder,
    SX_SYSTEMATIC times the reported error, which stays active when the remainder is zero.
    """
    relaxation = ctx["sx_duration_s"] / (3 * ctx["t2_s"]) + ctx["sx_duration_s"] / (6 * ctx["t1_cal_s"])
    return max(ctx["sx_error"] - relaxation, 0.0)


Gate = tuple[float, float, float, float, float]


def sx_gate(
    ctx: dict[str, Any],
    shift: float = 0.0,
    dephasing_scale: float = 1.0,
    axis_phase: float = 0.0,
    angle_error: float = 0.0,
) -> Gate:
    """(depolarizing parameter, duration in seconds, dephasing scale, axis phase, angle error) of one sx.

    lambda = 2 (e + shift), because a depolarizing channel of parameter lambda has average infidelity lambda / 2.
    The other three describe gate-model error classes at their nominal values 1, 0 and 0: a factor on the
    transverse decay rate during the drive, the tilt of the second sx's rotation axis from the first's in the
    equatorial plane, and an
    over-rotation of the pi / 2 pulse.
    """
    return 2 * (sx_depolarizing_error(ctx) + shift), ctx["sx_duration_s"], dephasing_scale, axis_phase, angle_error


def tau_of(arm: str, ctx: dict[str, Any], fraction: float | None = None) -> float:
    """Idle relaxation time per step after the sx pair: the relaxing part of the measure window, that part and the
    settle idle, the delay arm's idle, or none."""
    window = ctx["window_s"] * (ctx.get("window_fraction", WINDOW_RELAX_FRACTION) if fraction is None else fraction)
    return {
        "measure": window,
        "settle": window + ctx["settle_s"],
        "delay": ctx["delay_s"],
        "unitary": 0.0,
    }[arm]


@functools.lru_cache(maxsize=4096)
def sx_map(
    t1: float, t2: float, duration: float, z_eq: float, dephasing_scale: float = 1.0, angle_error: float = 0.0
) -> np.ndarray:
    """The affine map on (x, y, z, 1) of an sx held for `duration` with T1 relaxation toward z_eq and T2 decay of
    the transverse part: exp(A t) for dx/dt = -x / T2, dy/dt = -Omega z - y / T2,
    dz/dt = Omega y - (z - z_eq) / T1, with Omega t = pi / 2 + angle_error (SX is a rotation of pi / 2 about X) and
    the transverse rate 1 / T2 scaled by dephasing_scale."""
    omega = (math.pi / 2 + angle_error) / duration
    rate = dephasing_scale / t2
    generator = np.array(
        [[-rate, 0, 0, 0], [0, -rate, -omega, 0], [0, omega, -1 / t1, z_eq / t1], [0, 0, 0, 0]], dtype=float
    )
    return np.asarray(expm(generator * duration))


def rz_map(angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)


def chain_matrix(
    arm: str,
    n: int,
    t1: float,
    t2: float,
    tau: float,
    eps: float,
    gate: Gate,
    z_eq: float = 1.0,
) -> np.ndarray:
    """The affine map on (x, y, z, 1) of the n steps of an arm, just before the pre-readout idle.

    Each step plays the compiled form of RX(THETA / n), rz(pi/2) sx rz(THETA / n + pi) sx rz(pi/2), with T1 and T2
    acting during each sx and a depolarizing shrink 1 - lambda after it (gate = (lambda, duration)); the sx pair
    carries the state through the equator, so T2 decays the information a pinched qubit holds in z. Then the arm
    pinches (the pinched arms zero the transverse part and lose a fraction eps of z to transitions) or stays
    coherent, then relaxes for tau with T1 toward z_eq and T2 on the transverse part.
    """
    lam, duration, dephasing_scale, axis_phase, angle_error = gate
    sx = sx_map(t1, t2, duration, z_eq, dephasing_scale, angle_error).copy()
    sx[:3, :] *= 1 - lam
    # The second sx of a pair rotates about an axis tilted by axis_phase from the first's. A tilt common to every
    # sx is a change of frame about Z and leaves each z population unchanged, so only the relative tilt acts.
    second = rz_map(axis_phase) @ sx @ rz_map(-axis_phase) if axis_phase else sx
    pair_rz = rz_map(math.pi / 2)
    step = pair_rz @ second @ rz_map(THETA / n + math.pi) @ sx @ pair_rz
    idle = np.diag([math.exp(-tau / t2), math.exp(-tau / t2), math.exp(-tau / t1), 1.0])
    idle[2, 3] = z_eq * (1 - math.exp(-tau / t1))
    cycle = idle @ step
    if arm in PINCHED_ARMS:
        cycle = idle @ np.diag([0.0, 0.0, 1 - 2 * eps, 1.0]) @ step
    return np.asarray(np.linalg.matrix_power(cycle, n))


def bloch_z(
    arm: str,
    n: int,
    t1: float,
    t2: float,
    tau: float,
    eps: float = 0.0,
    z0: float = 1.0,
    gate: Gate = (0.0, 32e-9, 1.0, 0.0, 0.0),
    z_eq: float = 1.0,
) -> float:
    """Bloch z after n steps of an arm from (0, 0, z0), just before the pre-readout idle (chain_matrix)."""
    return float((chain_matrix(arm, n, t1, t2, tau, eps, gate, z_eq) @ np.array([0.0, 0.0, z0, 1.0]))[2])


def corrected_z(arm: str, n: int, t1: float, t2: float, tau: float, eps: float, gate: Gate, q: float) -> float:
    """The z that ro0/ro1 correction recovers: a + b q, with a the chain's response to the initial z and b its
    response to the relaxation source, both at unit strength.

    A true z of 1 - 2 p before the wait is divided by the scale (1 - 2 p) that ro0 and ro1 measure, so the initial
    state enters through q = z_eq / (1 - 2 p) alone, the single combination the t1 series fixes.
    """
    chain = chain_matrix(arm, n, t1, t2, tau, eps, gate)
    b = chain[2, 3]
    return float(chain[2, 2] + b * q)


def model_tables(
    t1: float, q: float, ctx: dict[str, Any], sx_shift: float = 0.0, fraction: float | None = None
) -> dict[str, Any]:
    """P0 per arm and N on the ideal-projective relaxing model for the series parameter q."""
    t2 = min(ctx["t2_s"], 2 * t1)
    gate = sx_gate(ctx, sx_shift)
    return {
        arm: {
            str(n): (1 + corrected_z(arm, n, t1, t2, tau_of(arm, ctx, fraction), 0.0, gate, q)) / 2
            for n in ARM_STEPS[arm]
        }
        for arm in ARMS
    }


def implied_loss(
    z_corrected: float, t1: float, t2: float, ctx: dict[str, Any], q: float, gate: Gate, fraction: float
) -> float:
    """The per-step z loss eps at which the measure arm's modeled corrected z at N = 16 equals z_corrected."""
    tau = tau_of("measure", ctx, fraction)

    def gap(eps: float) -> float:
        return corrected_z("measure", TOP_STEPS, t1, t2, tau, eps, gate, q) - z_corrected

    low, high = -0.05, 0.5
    # corrected z falls as eps grows; a target outside the bracket returns the nearer end.
    if gap(low) <= 0:
        return low
    if gap(high) >= 0:
        return high
    return float(brentq(gap, low, high, xtol=1e-13, rtol=1e-13))


# --- gate-model error classes -------------------------------------------------------------------------------

# Each class perturbs the sx model one way: its nominal magnitude and the bounds of the magnitudes considered.
# depolarizing is an absolute shift of the depolarizing error per sx, drive_dephasing a factor on the transverse decay
# rate during the drive, axis_phase the tilt of the second sx of a pair relative to the first in radians, and
# angle_error an over-rotation of the pi / 2 pulse in radians.
GATE_CLASSES: dict[str, tuple[float, float, float]] = {
    "depolarizing": (0.0, -0.001, 0.01),
    "drive_dephasing": (1.0, 0.0, 6.0),
    "axis_phase": (0.0, -0.3, 0.3),
    "angle_error": (0.0, -0.05, 0.05),
}
GATE_GRID_POINTS = 31


def class_gate(ctx: dict[str, Any], name: str, magnitude: float) -> Gate:
    keyword = {
        "depolarizing": "shift",
        "drive_dephasing": "dephasing_scale",
        "axis_phase": "axis_phase",
        "angle_error": "angle_error",
    }[name]
    return sx_gate(ctx, **{keyword: magnitude})


def gate_curves(t1: float, q: float, ctx: dict[str, Any], fraction: float) -> dict[str, list[dict[str, Any]]]:
    """Per class and side of the nominal magnitude, the unitary-arm and measure-arm N = 16 P0 shifts on a grid.

    Each curve runs from the nominal magnitude to the class bound and stops where the unitary shift turns round: past
    a turning point the coherent error wraps around, which is a different device, not a small error of the class.
    """
    t2 = min(ctx["t2_s"], 2 * t1)

    def p0(arm: str, gate: Gate) -> float:
        tau = tau_of(arm, ctx, fraction)
        return (1 + corrected_z(arm, TOP_STEPS, t1, t2, tau, 0.0, gate, q)) / 2

    nominal = sx_gate(ctx)
    base = {arm: p0(arm, nominal) for arm in ("unitary", "measure")}
    curves: dict[str, list[dict[str, Any]]] = {}
    for name, (center, low, high) in GATE_CLASSES.items():
        curves[name] = []
        for end in (low, high):
            grid = np.linspace(center, end, GATE_GRID_POINTS)
            gates = [class_gate(ctx, name, float(m)) for m in grid]
            unitary = np.array([p0("unitary", g) - base["unitary"] for g in gates])
            direction = next((float(np.sign(d)) for d in np.diff(unitary) if abs(d) > 1e-12), 0.0)
            stop = len(grid)
            for k, d in enumerate(np.diff(unitary)):
                if direction * d < -1e-12:
                    stop = k + 1
                    break
            measure = np.array([p0("measure", g) - base["measure"] for g in gates[:stop]])
            curves[name].append({"magnitude": grid[:stop], "unitary": unitary[:stop], "measure": measure})
    return curves


def gate_propagation(curves: dict[str, list[dict[str, Any]]], residual: float) -> dict[str, dict[str, Any]]:
    """What each gate-model error class would do to the measure arm if it alone produced the unitary residual.

    On each side of the nominal magnitude the class takes the smallest magnitude whose unitary-arm shift equals the
    observed residual (measured minus modeled P0), found by linear interpolation on its curve; where the curve does
    not reach the residual, its nearest point. The side with the larger measure-arm shift stands. The ratio is the
    measure-arm shift over the unitary-arm shift there. At the fixture calibration it is about -0.8 for depolarizing
    error (more depolarization raises the unitary P0 and lowers the measure P0), about -0.5 for dephasing during the
    drive, about +0.3 for a relative tilt between the two sx of a pair, and near 0 for an over-rotation of the
    pi / 2 pulse.
    """
    out: dict[str, dict[str, Any]] = {}
    for name, sides in curves.items():
        best: tuple[float, float, float, bool] | None = None
        for curve in sides:
            grid, unitary, measure = curve["magnitude"], curve["unitary"], curve["measure"]
            gap = unitary - residual
            hits = [k for k in range(len(grid) - 1) if gap[k] == 0.0 or gap[k] * gap[k + 1] < 0]
            if hits:
                k = hits[0]
                weight = 0.0 if gap[k + 1] == gap[k] else -gap[k] / (gap[k + 1] - gap[k])
                row = (
                    float(grid[k] + weight * (grid[k + 1] - grid[k])),
                    float(unitary[k] + weight * (unitary[k + 1] - unitary[k])),
                    float(measure[k] + weight * (measure[k + 1] - measure[k])),
                    True,
                )
            else:
                k = int(np.argmin(np.abs(gap)))
                row = (float(grid[k]), float(unitary[k]), float(measure[k]), False)
            if best is None or abs(row[2]) > abs(best[2]):
                best = row
        if best is None:
            raise AnalysisError(f"no gate curve for class {name}")
        magnitude, unitary_shift, measure_shift, reached = best
        out[name] = {
            "magnitude": magnitude,
            "unitary_shift": unitary_shift,
            "measure_shift": measure_shift,
            "ratio": measure_shift / unitary_shift if abs(unitary_shift) > 1e-12 else None,
            "reaches_residual": reached,
        }
    return out


# --- statistics ---------------------------------------------------------------------------------------------


def var(k: float, n: int) -> float:
    """Binomial variance of k / n from the Agresti-Coull-shifted proportion, so k = 0 or k = n keeps a spread."""
    p = (k + 1) / (n + 2)
    return p * (1 - p) / n


def fit_t1(delays: list[float], y: list[float], weights: list[float]) -> tuple[float, float]:
    """T1 and q from the corrected series y_k at the delays: y_k = q (1 - e_k) - e_k with e_k = exp(-t_k / T1).

    At a given T1 the weighted least squares for q is closed, and a bounded search over log T1 minimizes the
    residual.
    """
    t = np.array(delays)
    ys = np.array(y)
    w = np.array(weights)

    def solve(u: float) -> tuple[float, float]:
        e = np.exp(-t / math.exp(u))
        q = float(np.sum(w * (1 - e) * (ys + e)) / np.sum(w * (1 - e) ** 2))
        return q, float(np.sum(w * (ys + e - q * (1 - e)) ** 2))

    best = minimize_scalar(
        lambda u: solve(u)[1],
        bounds=(math.log(T1_BOUNDS[0]), math.log(T1_BOUNDS[1])),
        method="bounded",
        options={"xatol": 1e-10},
    )
    return math.exp(float(best.x)), solve(float(best.x))[0]


def propagate_many(
    f: Callable[[list[float]], dict[str, float]],
    x: list[float],
    variances: list[float],
    systematic: frozenset[int] = frozenset(),
    step: float = 1e-5,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """f(x), the standard error of each output from independent input variances by the delta method, and the part of
    that error that the inputs at the indices `systematic` contribute (they are shared by every qubit of a device)."""
    base = f(x)
    totals = dict.fromkeys(base, 0.0)
    shared = dict.fromkeys(base, 0.0)
    for i, v in enumerate(variances):
        h = step if abs(x[i]) > 10 * step else abs(x[i]) / 10 or step
        up, down = list(x), list(x)
        up[i] += h
        down[i] -= h
        high, low = f(up), f(down)
        for key in totals:
            term = ((high[key] - low[key]) / (2 * h)) ** 2 * v
            totals[key] += term
            if i in systematic:
                shared[key] += term
    return base, {key: math.sqrt(t) for key, t in totals.items()}, {key: math.sqrt(t) for key, t in shared.items()}


def finite(x: float) -> float | None:
    return x if math.isfinite(x) else None


def fit_eps(points: list[tuple[int, float, float]], law: Callable[[int, float], float]) -> dict[str, Any]:
    """Weighted least squares of P0(N) = law(N, eps) over (N, P0, se): grid, golden section, curvature."""

    def chi2(eps: float) -> float:
        return sum(((p - law(n, eps)) / se) ** 2 for n, p, se in points)

    best = min(range(len(FIT_GRID)), key=lambda i: chi2(FIT_GRID[i]))
    low, high = FIT_GRID[max(best - 1, 0)], FIT_GRID[min(best + 1, len(FIT_GRID) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        a, b = high - ratio * (high - low), low + ratio * (high - low)
        low, high = (low, b) if chi2(a) < chi2(b) else (a, high)
    eps = (low + high) / 2
    h = 1e-4
    curvature = (chi2(eps + h) - 2 * chi2(eps) + chi2(eps - h)) / h**2
    return {
        "eps": eps,
        "eps_se": finite(math.sqrt(2 / curvature)) if curvature > 0 else None,
        "chi2": chi2(eps),
        "dof": len(points) - 1,
        "at_grid_edge": best in (0, len(FIT_GRID) - 1),
    }


def classify_departure(z: float) -> str:
    if z <= -Z_DECIDE:
        return "departs_below"
    if z >= Z_DECIDE:
        return "exceeds_prediction"
    return "consistent"


def classify_gap(z: float) -> str:
    """The settle test's three outcomes from z = (measured - predicted) / SE of the settle arm's N = 16 P0."""
    if z >= Z_DECIDE:
        return "reduced_by_gap"
    if z <= -Z_DECIDE:
        return "deepened_by_gap"
    return "unchanged_by_gap"


def decide(contrast: float, contrast_se: float, difference: float, difference_se: float) -> dict[str, Any]:
    """The mutation test (measure minus unitary against CONTRAST_MIN) and the departure test of one qubit."""
    if contrast_se <= 0 or difference_se <= 0:
        raise AnalysisError("a decision needs positive standard errors")
    z_mutation = (contrast - CONTRAST_MIN) / contrast_se
    z_departure = difference / difference_se
    return {
        "mutation_test": {"z": z_mutation, "passes": z_mutation >= Z_DECIDE},
        "departure": {"z": z_departure, "outcome": classify_departure(z_departure)},
    }


# --- per-qubit analysis -------------------------------------------------------------------------------------


def pooled_obs(counts: dict[str, tuple[int, int]], names: list[str]) -> tuple[int, int]:
    """(ones, shots) summed over the named members."""
    return sum(counts[name][0] for name in names), sum(counts[name][1] for name in names)


def observations(counts: dict[str, tuple[int, int]], qubit: int) -> dict[str, tuple[int, int]]:
    """(ones, shots) per group of one qubit: each arm and N pooled over its signed members, ro0 and the t1 series."""
    obs = {f"{arm}-{n}": pooled_obs(counts, member_names(arm, n, qubit)) for arm, n in group_keys()}
    obs["ro0"] = pooled_obs(counts, [ro0_name(qubit)])
    for k, name in enumerate(t1_names(qubit)):
        obs[f"t1-{k}"] = pooled_obs(counts, [name])
    return obs


def quantities(p: dict[str, float], ctx: dict[str, Any]) -> dict[str, float]:
    """Every figure the decisions and reports use, as a function of the P(1) of each group and the sx error.

    ro0 and ro1 (t1-0, after the same pre-readout wait) fix the readout offset and scale; the t1 series then fixes
    T1 and q; the model tables are recomputed at the fitted values, so their uncertainty propagates with the
    measurement's.
    """
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2

    def corrected(key: str) -> float:
        return ((1 - 2 * p[key]) - offset) / scale

    series = [f"t1-{k}" for k in range(T1_COUNT)]
    t1, q = fit_t1(ctx["t1_delays_s"], [corrected(key) for key in series], ctx["weights"])
    p_init = (1 - 1 / q) / 2
    gate = sx_gate(ctx, p["sx_shift"])
    t2 = min(ctx["t2_s"], 2 * t1)
    tables = model_tables(t1, q, ctx, p["sx_shift"], p["window_fraction"])
    out: dict[str, float] = {"t1_s": t1, "q": q, "p_init": p_init, "scale": scale, "offset": offset}
    for arm, n in group_keys():
        key = f"{arm}-{n}"
        out[f"p0:{key}"] = (1 + corrected(key)) / 2
        out[f"model:{key}"] = tables[arm][str(n)]
        out[f"diff:{key}"] = out[f"p0:{key}"] - out[f"model:{key}"]
    top = str(TOP_STEPS)
    out["contrast"] = out[f"p0:measure-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing"] = out[f"p0:delay-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing_modeled"] = out[f"model:delay-{top}"] - out[f"model:unitary-{top}"]
    loss = implied_loss(2 * out[f"p0:measure-{top}"] - 1, t1, t2, ctx, q, gate, p["window_fraction"])
    settle = corrected_z("settle", TOP_STEPS, t1, t2, tau_of("settle", ctx, p["window_fraction"]), loss, gate, q)
    out["implied_loss"] = loss
    out["gap_difference"] = out[f"p0:settle-{top}"] - (1 + settle) / 2
    return out


def evaluate_qubit(item: tuple[int, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The decisions and descriptive outputs of one qubit from its member counts and context."""
    qubit, member_counts, ctx = item
    counts = {name: tuple(value) for name, value in member_counts["final"].items()}
    obs = observations(counts, qubit)
    keys = [*obs, "sx_shift", "window_fraction"]
    x = [*(k / n for k, n in obs.values()), 0.0, WINDOW_RELAX_FRACTION]
    variances = [
        *(var(k, n) for k, n in obs.values()),
        (SX_SYSTEMATIC * ctx["sx_error"]) ** 2,
        WINDOW_RELAX_VARIANCE,
    ]
    index = {key: i for i, key in enumerate(keys)}
    scale = x[index["t1-0"]] - x[index["ro0"]]
    ctx = {**ctx, "weights": [scale**2 / (4 * variances[index[f"t1-{k}"]]) for k in range(T1_COUNT)]}
    readout = {"scale": scale, "offset": 1 - x[index["ro0"]] - x[index["t1-0"]]}
    if not scale >= READOUT_CONTRAST_FLOOR:
        return {
            "qubit": qubit,
            "readout": readout,
            "usable": False,
            "reason": f"readout scale {scale:.4f} lies below the {READOUT_CONTRAST_FLOOR} floor",
        }
    value, se, shared = propagate_many(
        lambda xs: quantities(dict(zip(keys, xs, strict=True)), ctx),
        x,
        variances,
        frozenset({index["sx_shift"], index["window_fraction"]}),
    )
    top = str(TOP_STEPS)
    p0: dict[str, dict[str, Any]] = {arm: {} for arm in ARMS}
    for arm, n in group_keys():
        key = f"{arm}-{n}"
        p0[arm][str(n)] = {
            "p0": value[f"p0:{key}"],
            "se": se[f"p0:{key}"],
            "ideal": ideal_arm(arm, n),
            "modeled": value[f"model:{key}"],
            "measured_minus_modeled": value[f"diff:{key}"],
            "measured_minus_modeled_se": se[f"diff:{key}"],
            "planning": ctx["planning"][arm][str(n)],
        }
    # Gate-model systematic: the measure-arm shift that any one error class, consistent with the unitary arm's
    # observed residual, could produce. It adds in quadrature to the departure's standard error, so a qubit whose
    # unitary arm misses its model down-weights itself in the pooled z instead of vetoing the run.
    unitary_key = f"unitary-{top}"
    curves = gate_curves(value["t1_s"], value["q"], ctx, WINDOW_RELAX_FRACTION)
    propagation = gate_propagation(curves, value[f"diff:{unitary_key}"])
    gate_sigma = max(abs(row["measure_shift"]) for row in propagation.values())
    departure_se = math.sqrt(se[f"diff:measure-{top}"] ** 2 + gate_sigma**2)
    shared_se = shared[f"diff:measure-{top}"]
    gate_systematic = {
        "shared_se": shared_se,
        "unitary_residual": value[f"diff:{unitary_key}"],
        "unitary_residual_se": se[f"diff:{unitary_key}"],
        "classes": propagation,
        "propagated_se": gate_sigma,
        "departure_se_before": se[f"diff:measure-{top}"],
    }
    key = f"measure-{top}"
    decisions = decide(value["contrast"], se["contrast"], value[f"diff:{key}"], departure_se)
    gap_z = value["gap_difference"] / se["gap_difference"]
    t1, p_init, q = value["t1_s"], value["p_init"], value["q"]
    t2 = min(ctx["t2_s"], 2 * t1)
    tau = tau_of("measure", ctx, WINDOW_RELAX_FRACTION)
    gate = sx_gate(ctx)
    relaxed = fit_eps(
        [(n, value[f"p0:measure-{n}"], se[f"p0:measure-{n}"]) for n in MEASURE_STEPS],
        lambda n, eps: (1 + corrected_z("measure", n, t1, t2, tau, eps, gate, q)) / 2,
    )
    transitions: dict[str, Any] = {}
    for n in MEASURE_STEPS:
        flips = member_counts.get("flips", {})
        names = member_names("measure", n, qubit)
        if all(name in flips for name in names):
            k = sum(flips[name][0] for name in names)
            pairs = sum(flips[name][1] for name in names)
            transitions[str(n)] = {"rate": k / pairs, "se": math.sqrt(var(k, pairs)), "ideal": ideal_flip(n)}
    repeat = member_counts.get("repeat_read", {})
    names = member_names("measure", TOP_STEPS, qubit)
    repeat_read = None
    if all(name in repeat for name in names):
        k = sum(repeat[name][0] for name in names)
        total = sum(repeat[name][1] for name in names)
        repeat_read = {"agreement": k / total, "se": math.sqrt(var(k, total))}
    return {
        "qubit": qubit,
        "readout": readout,
        "usable": True,
        "fitted": {
            "t1_s": t1,
            "t1_se": se["t1_s"],
            "q": q,
            "p_init": p_init,
            "p_init_se": se["p_init"],
            "scale": value["scale"],
            "scale_se": se["scale"],
            "offset": value["offset"],
        },
        "p0": p0,
        "contrast_n16": {
            "contrast": value["contrast"],
            "se": se["contrast"],
            "ideal": ideal_measure(TOP_STEPS) - ideal_delay(),
        },
        "departure_n16": {
            "prediction": value[f"model:{key}"],
            "measured": value[f"p0:{key}"],
            "difference": value[f"diff:{key}"],
            "se": departure_se,
            "se_statistical": math.sqrt(max(se[f"diff:measure-{top}"] ** 2 - shared_se**2, 0.0)),
            "se_systematic": math.sqrt(shared_se**2 + gate_sigma**2),
        },
        "decisions": decisions,
        "gate_systematic_n16": gate_systematic,
        "_gate_curves": curves,
        "settle_n16": {
            "raw_difference": value[f"p0:settle-{top}"] - value[f"p0:measure-{top}"],
            "measure_implied_loss": value["implied_loss"],
            "gap_difference": value["gap_difference"],
            "se": se["gap_difference"],
            "se_statistical": math.sqrt(max(se["gap_difference"] ** 2 - shared["gap_difference"] ** 2, 0.0)),
            "se_systematic": shared["gap_difference"],
            "z": gap_z,
            "verdict": classify_gap(gap_z),
            "bounds": "an unchanged deficit bounds only a tail component that decays within 2 us",
        },
        "delay_arm": {
            "dephasing_zeno_n16": {
                "measured": value["dephasing"],
                "se": se["dephasing"],
                "modeled": value["dephasing_modeled"],
            }
        },
        "fit_relaxed": relaxed,
        "transitions": transitions,
        "repeat_read_n16": repeat_read,
    }


def widen_for_device_scatter(row: dict[str, Any], scatter: float) -> None:
    """Raise the qubit's propagated gate systematic to what the device-wide unitary scatter allows.

    A qubit's own residual can sit near zero while two gate-model errors cancel in the unitary arm and add in the
    measure arm. The root-mean-square of the usable qubits' residuals, floored at the scatter floor when one is set,
    bounds the model error the device shows, so the qubit's systematic also takes the shifts that a residual of
    +scatter and of -scatter would carry, and the
    departure test and its standard error use the larger.
    """
    gate = row["gate_systematic_n16"]
    widest = gate["propagated_se"]
    for sign in (1.0, -1.0):
        classes = gate_propagation(row["_gate_curves"], sign * scatter)
        widest = max(widest, max(abs(c["measure_shift"]) for c in classes.values()))
    gate["device_scatter"] = scatter
    gate["propagated_se"] = widest
    departure = row["departure_n16"]
    departure["se"] = math.sqrt(gate["departure_se_before"] ** 2 + widest**2)
    departure["se_systematic"] = math.sqrt(gate["shared_se"] ** 2 + widest**2)
    contrast = row["contrast_n16"]
    row["decisions"] = decide(contrast["contrast"], contrast["se"], departure["difference"], departure["se"])


def informative(row: dict[str, Any], ctx: dict[str, Any]) -> tuple[bool, str | None]:
    """Whether a qubit can test for a departure: it is usable, its mutation test passes and its widened departure
    standard error stays within PLANNING_SE_FACTOR times the standard error the planning model carries."""
    if not row["usable"]:
        return False, row["reason"]
    if not row["decisions"]["mutation_test"]["passes"]:
        return False, "the mutation test fails"
    planned = ctx.get("planning_se")
    se = row["departure_n16"]["se"]
    if planned is not None and se > PLANNING_SE_FACTOR * planned:
        return False, f"departure standard error {se:.4f} exceeds {PLANNING_SE_FACTOR} times the planning {planned:.4f}"
    return True, None


def evaluate(counts: dict[int, dict[str, Any]], contexts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    qubits = list(contexts)
    results = ordered_map(evaluate_qubit, [(q, counts[q], contexts[q]) for q in qubits], min_items=2)
    rows = dict(zip(qubits, results, strict=True))
    usable = [q for q, r in rows.items() if r["usable"]]
    if usable:
        residuals = [rows[q]["gate_systematic_n16"]["unitary_residual"] for q in usable]
        scatter = math.sqrt(sum(r * r for r in residuals) / len(residuals))
        floor = contexts[usable[0]].get("model_scatter_floor")
        if floor is not None:
            scatter = max(scatter, floor)
        for q in usable:
            widen_for_device_scatter(rows[q], scatter)
    for row in rows.values():
        row.pop("_gate_curves", None)
        row["model_scatter_floor"] = contexts[row["qubit"]].get("model_scatter_floor")
        row["informative"], row["uninformative_reason"] = informative(row, contexts[row["qubit"]])
    return rows


# --- device verdicts ----------------------------------------------------------------------------------------


def pooled_z(estimates: list[tuple[float, float, float]]) -> float | None:
    """The pooled estimate over its standard error, from (estimate, statistical se, systematic se) triples.

    Weights are inverse total variances. The statistical errors are independent across qubits, so they add in
    quadrature. The systematic errors (the sx error, the relaxing fraction of the measure window, the gate-model
    propagation) belong to the device and move every qubit the same way, so they add linearly: a pooled estimate
    keeps the weighted mean of them rather than shrinking it by the square root of the qubit count.
    """
    if not estimates:
        return None
    weights = [1 / (stat**2 + sys**2) for _, stat, sys in estimates]
    total = sum(weights)
    mean = sum(w * e for w, (e, _, _) in zip(weights, estimates, strict=True)) / total
    variance = (
        sum((w * stat) ** 2 for w, (_, stat, _) in zip(weights, estimates, strict=True))
        + sum(w * sys for w, (_, _, sys) in zip(weights, estimates, strict=True)) ** 2
    ) / total**2
    return mean / math.sqrt(variance)


def device_verdict(qubits: dict[Any, dict[str, Any]]) -> dict[str, Any]:
    """The preregistered device-level verdicts.

    Only informative qubits count (a usable qubit whose mutation test passes and whose widened departure standard
    error stays within PLANNING_SE_FACTOR times its planning value). Fewer than DEVICE_QUBITS informative qubits
    give every verdict the status `uninformative`, so `none` always means a clean null. A verdict fires when at
    least DEVICE_QUBITS informative qubits return the per-qubit outcome, or the pooled z over them
    (pooled_z) reaches Z_DECIDE in the verdict's direction. Eight qubits with
    about four two-sided 3-SE per-qubit tests would raise a per-qubit flag in about 8 % of pure-noise runs, so the
    per-qubit outcomes stay descriptive; a device verdict fires in about 0.14 % of pure-noise runs through the
    pooled z and 0.005 % through the count rule, each direction.

    The gate-model systematic enters before this function: each qubit's departure standard error already carries
    the measure-arm shift that a gate-model error consistent with its unitary-arm residual could produce
    (gate_propagation), so a badly modeled qubit down-weights itself in the pooled z and no veto remains. A
    depolarizing error shared by all qubits shifts each departure by at most its own propagated systematic, so its
    z stays below 1 and the pooled z below the square root of the usable-qubit count.
    """
    usable = {q: r for q, r in qubits.items() if r["usable"]}
    informed = {q: r for q, r in usable.items() if r.get("informative", True)}
    uninformative = {q: r.get("uninformative_reason") for q, r in qubits.items() if q not in informed}
    mutation = [q for q, r in usable.items() if not r["decisions"]["mutation_test"]["passes"]]
    common = {
        "usable_qubits": sorted(usable),
        "informative_qubits": sorted(informed),
        "uninformative_qubits": uninformative,
        "mutation_test_failed_qubits": sorted(mutation),
        "mutation_test_passes": bool(usable) and not mutation,
    }
    names = ("departs_below", "exceeds_prediction", "settle_reduced_by_gap", "settle_deepened_by_gap")
    if len(informed) < DEVICE_QUBITS:
        # Fewer than two informative qubits cannot support a null: `none` is reserved for a clean null.
        silent: dict[str, Any] = {"qubits": [], "pooled_z": None, "status": "uninformative", "device": False}
        return {**common, "status": "uninformative", **dict.fromkeys(names, silent)}
    departure = [
        (r["departure_n16"]["difference"], r["departure_n16"]["se_statistical"], r["departure_n16"]["se_systematic"])
        for r in informed.values()
    ]
    gap = [
        (r["settle_n16"]["gap_difference"], r["settle_n16"]["se_statistical"], r["settle_n16"]["se_systematic"])
        for r in informed.values()
    ]
    z_departure, z_gap = pooled_z(departure), pooled_z(gap)

    def named(field: Callable[[dict[str, Any]], str], outcome: str) -> list[Any]:
        return sorted(q for q, r in informed.items() if field(r) == outcome)

    below = named(lambda r: r["decisions"]["departure"]["outcome"], "departs_below")
    above = named(lambda r: r["decisions"]["departure"]["outcome"], "exceeds_prediction")
    reduced = named(lambda r: r["settle_n16"]["verdict"], "reduced_by_gap")
    deepened = named(lambda r: r["settle_n16"]["verdict"], "deepened_by_gap")

    bounded = all(r.get("model_scatter_floor") is not None for r in informed.values())

    def verdict(members: list[Any], z: float | None, sign: int, gate_dependent: bool = True) -> dict[str, Any]:
        pooled_fired = z is not None and sign * z >= Z_DECIDE
        fired = len(members) >= DEVICE_QUBITS or pooled_fired
        if fired and gate_dependent and not bounded:
            # Errors that cancel in the unitary arm are unbounded without a measured model scatter.
            return {"qubits": members, "pooled_z": z, "status": "gate_model_unbounded", "device": False}
        return {"qubits": members, "pooled_z": z, "status": "attributed" if fired else "none", "device": fired}

    return {
        **common,
        "status": "informative",
        "departs_below": verdict(below, z_departure, -1),
        "exceeds_prediction": verdict(above, z_departure, 1),
        "settle_reduced_by_gap": verdict(reduced, z_gap, 1, gate_dependent=False),
        "settle_deepened_by_gap": verdict(deepened, z_gap, -1, gate_dependent=False),
        "model_scatter_floor_measured": bounded,
    }


def device_flags(verdict: dict[str, Any]) -> dict[str, bool]:
    return {k: v["device"] for k, v in verdict.items() if isinstance(v, dict) and "device" in v}


# --- synthetic model devices --------------------------------------------------------------------------------


def device_model(ctx: dict[str, Any], **over: Any) -> dict[str, Any]:
    """A model device from one qubit's context, with fields overridden: t1_s, t2_s, p_init, p_thermal, eps (z lost per
    step to measurement transitions), eps_settle (None follows eps), sx_error, e01, e10, window_s and
    window_fraction (the true relaxing fraction of the measure duration), readout_history (the shift added to
    the final read of the pinched arms' P(1)) and the gate-model error classes gate_dephasing (a factor on the
    transverse decay rate during the drive), axis_phase and angle_error (radians per sx)."""
    model = {
        "t1_s": ctx["t1_cal_s"],
        "t2_s": ctx["t2_s"],
        "sx_error": ctx["sx_error"],
        "e01": ctx["e01"],
        "e10": ctx["e10"],
        "p_init": PLANNING_P_INIT,
        "p_thermal": 0.0,
        "eps": 0.0,
        "eps_settle": None,
        "window_s": ctx["window_s"],
        "window_fraction": WINDOW_RELAX_FRACTION,
        "readout_history": 0.0,
        "gate_dephasing": 1.0,
        "axis_phase": 0.0,
        "angle_error": 0.0,
    }
    model.update(over)
    return model


def expected_ones(z: float, shift: float, m: dict[str, Any], prereadout_s: float, shots: int) -> tuple[int, int]:
    """(ones, shots) a model device returns for a member whose true Bloch z is z before the pre-readout idle."""
    z_eq = 1 - 2 * m["p_thermal"]
    waited = z_eq - (z_eq - z) * math.exp(-prereadout_s / m["t1_s"])
    observed = (1 - m["e01"] - m["e10"]) * waited + m["e10"] - m["e01"]
    return round(shots * min(max((1 - observed) / 2 + shift, 0.0), 1.0)), shots


def device_counts(
    models: dict[int, dict[str, Any]], contexts: dict[int, dict[str, Any]], shots: int
) -> dict[int, dict[str, Any]]:
    """Expected final-bit counts of model devices, rounded to whole shots, per member.

    Each member's true Bloch z comes from the Bloch model (T1, T2, an initialization excitation p_init, the true
    sx error and window), relaxes over the pre-readout idle and reads through the qubit's assignment errors.
    """
    out: dict[int, dict[str, Any]] = {}
    for q, m in models.items():
        ctx = {
            **contexts[q],
            "window_s": m["window_s"],
            "sx_error": m["sx_error"],
            "window_fraction": m["window_fraction"],
        }
        z_eq = 1 - 2 * m["p_thermal"]
        wait = ctx["prereadout_s"]
        final: dict[str, tuple[int, int]] = {}
        for arm, n in group_keys():
            eps = m["eps_settle"] if arm == "settle" and m["eps_settle"] is not None else m["eps"]
            z = bloch_z(
                arm,
                n,
                m["t1_s"],
                min(m["t2_s"], 2 * m["t1_s"]),
                tau_of(arm, ctx),
                eps,
                1 - 2 * m["p_init"],
                sx_gate(
                    ctx,
                    dephasing_scale=m["gate_dephasing"],
                    axis_phase=m["axis_phase"],
                    angle_error=m["angle_error"],
                ),
                z_eq,
            )
            shift = m["readout_history"] if arm in PINCHED_ARMS else 0.0
            for name in member_names(arm, n, q):
                final[name] = expected_ones(z, shift, m, wait, shots)
        final[ro0_name(q)] = expected_ones(1 - 2 * m["p_init"], 0.0, m, wait, shots)
        for k, name in enumerate(t1_names(q)):
            decayed = z_eq - (z_eq + 1 - 2 * m["p_init"]) * math.exp(-ctx["t1_delays_s"][k] / m["t1_s"])
            final[name] = expected_ones(decayed, 0.0, m, wait, shots)
        out[q] = {"final": final}
    return out


def planning_tables(contexts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {q: model_tables(ctx["t1_cal_s"], 1 / (1 - 2 * PLANNING_P_INIT), ctx) for q, ctx in contexts.items()}


def planning_departure_se(item: tuple[int, dict[str, Any]]) -> float:
    """The departure standard error of one qubit at the planning model: the analysis run on its expected counts,
    widened by the scatter floor when one is set, so the planning value is what a well-modeled qubit reports."""
    q, ctx = item
    counts = device_counts({q: device_model(ctx)}, {q: ctx}, PLANNING_SHOTS)[q]
    row = evaluate_qubit((q, counts, ctx))
    floor = ctx.get("model_scatter_floor")
    if floor is not None:
        widen_for_device_scatter(row, floor)
    return float(row["departure_n16"]["se"])


_PLANNING_SE: dict[str, float] = {}


def with_planning(
    contexts: dict[int, dict[str, Any]], floor: float | None = MODEL_SCATTER_FLOOR
) -> dict[int, dict[str, Any]]:
    """Contexts with the planning P0 tables, the scatter floor and the planning departure standard error added.

    The standard error depends on the calibration alone, so a qubit whose context repeats one already analyzed in
    this process reuses it.
    """
    tables = planning_tables(contexts)
    planned = {q: {**ctx, "planning": tables[q], "model_scatter_floor": floor} for q, ctx in contexts.items()}
    keys = {
        q: json.dumps({k: v for k, v in ctx.items() if k != "planning"}, sort_keys=True) for q, ctx in planned.items()
    }
    todo = [(q, planned[q]) for q in planned if keys[q] not in _PLANNING_SE]
    for (q, _), se in zip(todo, ordered_map(planning_departure_se, todo, min_items=2), strict=True):
        _PLANNING_SE[keys[q]] = se
    return {q: {**ctx, "planning_se": _PLANNING_SE[keys[q]]} for q, ctx in planned.items()}


# --- sweep --------------------------------------------------------------------------------------------------


# Per-qubit gate-model error injected by a model-error row, cycled over the qubits. "specified" is a factor of 0.5 and
# 1.5 on the transverse decay rate during the drive. "large" reaches a unitary-arm residual of about +-0.03 at the
# fixture calibration: a factor of 12 on that rate (+0.033) and a relative axis tilt of +-0.0085 rad between the two sx
# of a pair (+-0.030, +-0.009 in the measure arm).
MODEL_ERRORS = {
    "specified": ({"gate_dephasing": 0.5}, {"gate_dephasing": 1.5}),
    "medium": ({"gate_dephasing": 5.0}, {"axis_phase": 0.0035}, {"axis_phase": -0.0035}),
    "large": ({"gate_dephasing": 12.0}, {"axis_phase": 0.0085}, {"axis_phase": -0.0085}),
}


def sweep_cases(reduced: bool) -> list[dict[str, Any]]:
    """True devices off the planning point: one axis at a time, then a corner with all moved, then the gate-model
    rows. Each row names the outcome `expect` that sweep_failures requires. The reduced grid keeps the planning point
    and the corner."""
    base = {
        "label": "planning",
        "expect": "clean",
        "p_init": PLANNING_P_INIT,
        "p_thermal": 0.0,
        "t1_scale": 1.0,
        "sx_scale": 1.0,
        "window_scale": 1.0,
    }
    corner = {
        **base,
        "label": "corner",
        "p_init": 0.04,
        "p_thermal": 0.01,
        "t1_scale": 0.8,
        "sx_scale": 2.0,
        "window_scale": 1.05,
    }
    if reduced:
        return [base, corner]
    specified = {**base, "model_error": "specified"}
    medium = {**base, "model_error": "medium"}
    large = {**base, "model_error": "large"}
    axes = [
        {**base, "label": "p=0", "p_init": 0.0},
        {**base, "label": "p=0.04", "p_init": 0.04},
        {**base, "label": "thermal 0.01", "p_thermal": 0.01},
        {**base, "label": "T1 x0.8", "t1_scale": 0.8},
        {**base, "label": "T1 x1.2", "t1_scale": 1.2},
        {**base, "label": "window x1.05", "window_scale": 1.05},
        {**base, "label": "no relaxation in the window", "window_fraction": 0.0},
        {**base, "label": "full relaxation in the window", "window_fraction": 1.0},
        {**base, "label": "sx x2", "sx_scale": 2.0, "expect": "none"},
        {**base, "label": "sx x3", "sx_scale": 3.0, "expect": "not_attributed"},
        {**base, "label": "sx x4", "sx_scale": 4.0, "expect": "not_attributed"},
        {**base, "label": "measure eps 0.01", "eps": 0.01, "eps_settle": 0.01, "expect": "departure"},
        {**base, "label": "tail eps 0.01 (measure arm only)", "eps": 0.01, "eps_settle": 0.0, "expect": "tail"},
        {**specified, "label": "model error, drive dephasing x0.5 and x1.5", "expect": "none"},
        {
            **specified,
            "label": "model error x0.5 and x1.5 + measure eps 0.02",
            "eps": 0.02,
            "eps_settle": 0.02,
            "expect": "departure",
        },
        {**medium, "label": "model error, residual about +-0.01", "expect": "none"},
        {**medium, "label": "model error +-0.01 + sx x3", "sx_scale": 3.0, "expect": "not_attributed"},
        {
            **medium,
            "label": "model error +-0.01 + measure eps 0.02",
            "eps": 0.02,
            "eps_settle": 0.02,
            "expect": "departure",
        },
        {**large, "label": "model error, residual about +-0.03", "expect": "none"},
        {**large, "label": "model error +-0.03 + sx x3", "sx_scale": 3.0, "expect": "uninformative"},
        {
            **large,
            "label": "model error +-0.03 + measure eps 0.02",
            "eps": 0.02,
            "eps_settle": 0.02,
            "expect": "departure",
        },
        {
            **base,
            "label": "axis tilt -0.016 + sx x3",
            "axis_phase": -0.016,
            "sx_scale": 3.0,
            "expect": "not_attributed",
        },
        {
            **base,
            "label": "axis tilt -0.022 + sx x4",
            "axis_phase": -0.022,
            "sx_scale": 4.0,
            "expect": "not_attributed",
        },
    ]
    return [base, *axes, corner]


def device_informative(verdict: dict[str, Any]) -> list[Any]:
    return list(verdict["informative_qubits"])


def run_row(item: tuple[dict[str, Any], dict[int, dict[str, Any]], int]) -> dict[str, Any]:
    """One true device (a sweep spec) analyzed over its qubits through the same evaluate path as a run."""
    spec, contexts, shots = item
    models = {
        q: device_model(
            ctx,
            t1_s=spec["t1_scale"] * ctx["t1_cal_s"],
            p_init=spec["p_init"],
            p_thermal=spec["p_thermal"],
            sx_error=spec["sx_scale"] * ctx["sx_error"],
            window_s=spec["window_scale"] * ctx["window_s"],
            window_fraction=spec.get("window_fraction", WINDOW_RELAX_FRACTION),
            eps=spec.get("eps", 0.0),
            eps_settle=spec.get("eps_settle"),
            **{key: spec[key] for key in ("gate_dephasing", "axis_phase", "angle_error") if key in spec},
            **(
                MODEL_ERRORS[spec["model_error"]][position % len(MODEL_ERRORS[spec["model_error"]])]
                if spec.get("model_error")
                else {}
            ),
        )
        for position, (q, ctx) in enumerate(contexts.items())
    }
    result = evaluate(device_counts(models, contexts, shots), contexts)
    verdict = device_verdict(result)
    usable = {q: r for q, r in result.items() if r["usable"]}
    return {
        **spec,
        "usable": len(usable),
        "informative": len(device_informative(verdict)),
        "device_overall": verdict["status"],
        "departure_z": {q: r["decisions"]["departure"]["z"] for q, r in usable.items()},
        "settle": {q: r["settle_n16"]["verdict"] for q, r in usable.items()},
        "settle_z": {q: r["settle_n16"]["z"] for q, r in usable.items()},
        "mutation_z": {q: r["decisions"]["mutation_test"]["z"] for q, r in usable.items()},
        "mutation_passes": verdict["mutation_test_passes"],
        "unitary_residual": {q: r["gate_systematic_n16"]["unitary_residual"] for q, r in usable.items()},
        "propagated_se": {q: r["gate_systematic_n16"]["propagated_se"] for q, r in usable.items()},
        "departure_difference": {q: r["departure_n16"]["difference"] for q, r in usable.items()},
        "departure_se": {q: r["departure_n16"]["se"] for q, r in usable.items()},
        "t1_error": {q: r["fitted"]["t1_s"] / models[q]["t1_s"] - 1 for q, r in usable.items()},
        "device": device_flags(verdict),
        "device_status": {k: v["status"] for k, v in verdict.items() if isinstance(v, dict) and "status" in v},
        "pooled_departure_z": verdict["departs_below"]["pooled_z"],
        "pooled_gap_z": verdict["settle_reduced_by_gap"]["pooled_z"],
    }


def run_sweep(contexts: dict[int, dict[str, Any]], cases: list[dict[str, Any]], shots: int) -> list[dict[str, Any]]:
    return ordered_map(run_row, [(spec, contexts, shots) for spec in cases], min_items=2)


def minimum_detectable(contexts: dict[int, dict[str, Any]], spec: dict[str, Any], shots: int) -> dict[str, Any]:
    """The smallest departure the device rule detects on the row `spec`, by the per-step z loss eps injected in both
    pinched arms (the settle gap does not remove a transition the measurement induces).

    The pooled threshold is the eps at which the pooled departure z reaches -Z_DECIDE (bisection on run_row). The
    per-qubit thresholds scale each qubit's z at eps = 0.01 linearly to Z_DECIDE, a first-order figure. Each reports
    the departure it produces: the mean measured-minus-modeled P0 of the N = 16 measure arm.
    """

    def row(eps: float) -> dict[str, Any]:
        return run_row(({**spec, "eps": eps, "eps_settle": eps}, contexts, shots))

    low, high = 0.0, 0.05
    for _ in range(14):
        middle = (low + high) / 2
        z = row(middle)["pooled_departure_z"]
        if z is None or z > -Z_DECIDE:
            low = middle
        else:
            high = middle
    pooled = row(high)
    probe = row(0.01)
    per_qubit = {q: Z_DECIDE * 0.01 / -z for q, z in probe["departure_z"].items() if z < 0}
    return {
        "label": spec["label"],
        "pooled_eps": high,
        "pooled_departure_p0": sum(pooled["departure_difference"].values()) / len(pooled["departure_difference"]),
        "per_qubit_eps": per_qubit,
        "per_qubit_eps_min": min(per_qubit.values()),
        "per_qubit_eps_median": float(np.median(list(per_qubit.values()))),
        "per_qubit_eps_max": max(per_qubit.values()),
        "mean_departure_se": sum(probe["departure_se"].values()) / len(probe["departure_se"]),
    }


def sweep_failures(rows: list[dict[str, Any]], qubits: int) -> list[str]:
    """The pass rule, by the `expect` of each row.

    - clean: every informative qubit at |departure z| < 1, the gap verdict `unchanged_by_gap`, every device verdict
      `none`.
    - none: every device verdict reads `none`, never `uninformative`, and none fires.
    - not_attributed: no departure verdict is attributed (a gate error scaled up must never read as pinching); a
      device that reads `uninformative` satisfies it.
    - departure: `departs_below` is attributed with the gap verdict `unchanged_by_gap` on every qubit.
    - tail: `settle_reduced_by_gap` is attributed.
    - uninformative: the device reads `uninformative` and nothing fires.
    - either: no requirement beyond the mutation test.
    Every row needs all qubits usable and the mutation test passing."""
    failures = []
    for row in rows:
        label, expect = row["label"], row.get("expect", "clean")
        flags, status = row["device"], row["device_status"]
        if row["usable"] != qubits:
            failures.append(f"{label}: {row['usable']} usable qubits")
        if not row["mutation_passes"]:
            failures.append(f"{label}: the mutation test fails")
        if expect == "clean":
            failures.extend(f"{label} q{q}: departure z {z:.2f}" for q, z in row["departure_z"].items() if abs(z) >= 1)
            failures.extend(f"{label} q{q}: settle {v}" for q, v in row["settle"].items() if v != "unchanged_by_gap")
        if expect in ("clean", "none") and (any(flags.values()) or any(v != "none" for v in status.values())):
            failures.append(f"{label}: the device does not read a clean null: {status}")
        if expect == "uninformative" and (row["device_overall"] != "uninformative" or any(flags.values())):
            failures.append(f"{label}: expected an uninformative device, read {row['device_overall']} {flags}")
        if expect == "not_attributed" and (flags["departs_below"] or flags["exceeds_prediction"]):
            failures.append(f"{label}: a departure was attributed to a gate error: {flags}")
        if expect == "departure":
            if not flags["departs_below"]:
                failures.append(f"{label}: an injected departure is not attributed: {status}")
            if any(v != "unchanged_by_gap" for v in row["settle"].values()):
                failures.append(f"{label}: the settle verdict moved: {row['settle']}")
        if expect == "tail" and not flags["settle_reduced_by_gap"]:
            failures.append(f"{label}: an injected tail is not caught: {status}")
    return failures


# --- collection glue ----------------------------------------------------------------------------------------


def contexts_from_record(record: dict[str, Any], executed: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Per-qubit analysis context from the record's family configuration and the execution evidence.

    Durations in dt come from family_configuration (the values the circuits carry); the sx error and duration, the
    measure duration, T1, T2 and the readout errors are the values in force at the qubit's PUB execution start
    (executed[member]["placed_gate_calibration"], ["placed_qubit_calibration"]). Backend properties report T1 and
    T2 in microseconds.
    """
    configuration = record["family_configuration"]
    dt = float(configuration["dt_seconds"])
    contexts: dict[int, dict[str, Any]] = {}
    for qubit in (int(q) for q in configuration["qubits"]):
        anchor = executed.get(ro0_name(qubit))
        if anchor is None:
            raise AnalysisError(f"missing execution evidence for {ro0_name(qubit)}")
        gate = anchor.get("placed_gate_calibration", {}).get(str(qubit))
        coherence = anchor.get("placed_qubit_calibration", {}).get(str(qubit))
        check(gate is not None and coherence is not None, f"q{qubit}: no execution-time calibration values")
        contexts[qubit] = {
            "sx_error": float(gate["sx_error"]),
            "sx_duration_s": float(gate["sx_duration_s"]),
            "window_s": float(gate["measure_duration_s"]),
            "delay_s": int(configuration["measurement_delay_dt"][str(qubit)]) * dt,
            "settle_s": int(configuration["settle_delay_dt"][str(qubit)]) * dt,
            "prereadout_s": int(configuration["prereadout_delay_dt"][str(qubit)]) * dt,
            "t1_delays_s": [int(d) * dt for d in configuration["t1_delays_dt"]],
            "t1_cal_s": float(coherence["T1"]) * 1e-6,
            "t2_s": float(coherence["T2"]) * 1e-6,
            "e01": float(coherence["prob_meas1_prep0"]),
            "e10": float(coherence["prob_meas0_prep1"]),
        }
    return contexts


def member_counts_from_distributions(
    distributions: dict[str, list[np.ndarray]], executed: dict[str, Any], qubits: list[int]
) -> dict[int, dict[str, Any]]:
    """Whole-shot counts per member: the final bit (clbit 0) and, for the measure and settle arms, flips between
    consecutive mid-circuit bits and agreement of the last mid-circuit bit with the final bit, from the joint law
    over the member's clbits (index = final + 2 * mcm bits, step k at bit k)."""
    out: dict[int, dict[str, Any]] = {q: {"final": {}, "flips": {}, "repeat_read": {}} for q in qubits}
    for q in qubits:
        for name in distributions:
            if not name.endswith(f"_q{q}") or not name.startswith("msq_"):
                continue
            check(len(distributions[name]) == 1, f"{name}: the analysis reads one replica per member")
            law = np.asarray(distributions[name][0], dtype=float)
            shots = int(executed[name]["shots"])
            index = np.arange(law.size)
            ones = shots * float(law[(index & 1) == 1].sum())
            check(abs(ones - round(ones)) < 1e-2 * max(1.0, shots / 1e4), f"{name}: P(1) is not a whole-shot count")
            out[q]["final"][name] = (round(ones), shots)
            if law.size > 2:
                bits = law.size.bit_length() - 1
                flips = 0.0
                for k in range(1, bits - 1):
                    differ = ((index >> k) & 1) != ((index >> (k + 1)) & 1)
                    flips += shots * float(law[differ].sum())
                out[q]["flips"][name] = (round(flips), shots * (bits - 2))
                agree = ((index >> (bits - 1)) & 1) == (index & 1)
                out[q]["repeat_read"][name] = (round(shots * float(law[agree].sum())), shots)
    return out


def analyze_members(
    member_counts: dict[int, dict[str, Any]],
    contexts: dict[int, dict[str, Any]],
    floor: float | None = MODEL_SCATTER_FLOOR,
) -> dict[str, Any]:
    """The decisions from whole-shot member counts and per-qubit contexts."""
    contexts = with_planning(contexts, floor)
    qubits = evaluate(member_counts, contexts)
    return {
        "schema": SCHEMA,
        "device": device_verdict(qubits),
        "qubits": {str(q): r for q, r in qubits.items()},
    }


def collected(
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    floor: float | None = MODEL_SCATTER_FLOOR,
) -> dict[str, Any]:
    """The preregistered pinching analysis for a collected measurement-sequence record, or a withheld reason."""
    configuration = record["family_configuration"]
    qubits = [int(q) for q in configuration["qubits"]]
    needed = [ro0_name(q) for q in qubits]
    missing = sorted(name for name in needed if name not in distributions)
    if missing:
        return {"schema": SCHEMA, "withheld": f"missing measured members {missing}"}
    try:
        contexts = contexts_from_record(record, executed)
        counts = member_counts_from_distributions(distributions, executed, qubits)
        for q in qubits:
            absent = [
                n
                for n in (
                    *t1_names(q),
                    *(m for arm, n_ in group_keys() for m in member_names(arm, n_, q)),
                )
                if n not in counts[q]["final"]
            ]
            check(not absent, f"q{q}: missing measured members {absent}")
        return analyze_members(counts, contexts, floor)
    except AnalysisError as error:
        return {"schema": SCHEMA, "withheld": str(error)}


# --- self-test ----------------------------------------------------------------------------------------------

# One Heron r2 qubit's calibration as the Target reports it (ibm_kingston, q91 of the retained dry run
# results/live/2026-10-25T201344.631258Z): sx 32 ns at error 2.667e-4, measure 2.18 us, T1 274 us, T2 117.6 us.
FIXTURE_QUBIT: dict[str, Any] = {
    "sx_error": 2.6665894181091416e-4,
    "sx_duration_s": 3.2e-8,
    "window_s": 2.18e-6,
    "delay_s": 545 * 4e-9,
    "settle_s": 500 * 4e-9,
    "prereadout_s": 500 * 4e-9,
    "t1_delays_s": [0.0, 20e-6, 50e-6, 100e-6, 200e-6],
    "t1_cal_s": 274.0249716801235e-6,
    "t2_s": 117.61315908309147e-6,
    "e01": 0.000244140625,
    "e10": 0.004150390625,
}
FIXTURE_QUBITS = (91, 118, 95, 61, 147, 151, 59, 89)
FIXTURE_SHOTS = 8192


# Per-qubit multipliers of the fixture calibration (T1, T2, sx error, readout errors), so the eight fixture qubits
# are distinct devices and a pooled statistic does not repeat one qubit eight times.
FIXTURE_SCALES = (
    (1.0, 1.0, 1.0, 1.0),
    (0.7, 0.8, 1.5, 1.6),
    (1.3, 1.2, 0.8, 0.7),
    (0.9, 1.1, 1.2, 2.0),
    (1.1, 0.9, 0.9, 1.1),
    (0.8, 0.7, 2.0, 0.9),
    (1.2, 1.3, 1.0, 1.4),
    (1.0, 1.0, 1.3, 0.8),
)


def fixture_contexts(
    qubits: tuple[int, ...] = FIXTURE_QUBITS, floor: float | None = DEMONSTRATION_SCATTER_FLOOR
) -> dict[int, dict[str, Any]]:
    """Eight distinct qubits scaled from the fixture calibration; counts of different qubits are independent."""
    contexts = {}
    for q, (t1, t2, sx, readout) in zip(qubits, FIXTURE_SCALES, strict=False):
        contexts[q] = {
            **FIXTURE_QUBIT,
            "t1_cal_s": FIXTURE_QUBIT["t1_cal_s"] * t1,
            "t2_s": FIXTURE_QUBIT["t2_s"] * t2,
            "sx_error": FIXTURE_QUBIT["sx_error"] * sx,
            "e01": FIXTURE_QUBIT["e01"] * readout,
            "e10": FIXTURE_QUBIT["e10"] * readout,
        }
    return with_planning(contexts, floor)


def self_test(with_sweep: bool = True, qubit_count: int = len(FIXTURE_QUBITS)) -> str:
    check(
        [round(ideal_measure(n), 4) for n in STEPS] == [0.0302, 0.5151, 0.6722, 0.8040, 0.8914],
        "the ideal measure laws",
    )
    check(round(ideal_delay(), 4) == 0.0302, "the delay and unitary ideal is not 0.0302")
    check(round(ideal_measure(16) - ideal_delay(), 4) == 0.8612, "the N = 16 contrast ideal is not 0.8612")
    points = [(n, (1 + math.pow((1 - 2 * 0.01) * math.cos(THETA / n), n)) / 2, 0.005) for n in MEASURE_STEPS]
    fit = fit_eps(points, lambda n, eps: (1 + math.pow((1 - 2 * eps) * math.cos(THETA / n), n)) / 2)
    check(abs(fit["eps"] - 0.01) < 1e-6, "the fit does not recover its own law")
    contexts = fixture_contexts(FIXTURE_QUBITS[:qubit_count])
    qubits = list(contexts)
    # Planted devices: T1 and p differ from the planning values, eps takes both signs.
    planted = dict(zip(qubits, (0.0, 0.02, -0.015, 0.0, 0.015, -0.01, 0.0, 0.0), strict=False))
    models = {
        q: device_model(ctx, t1_s=0.8 * ctx["t1_cal_s"], p_init=0.04, eps=planted[q], eps_settle=planted[q])
        for q, ctx in contexts.items()
    }
    result = evaluate(device_counts(models, contexts, FIXTURE_SHOTS), contexts)
    for q, eps in planted.items():
        row = result[q]
        check(row["usable"], f"q{q}: not usable")
        fitted = row["fitted"]
        check(abs(fitted["t1_s"] / models[q]["t1_s"] - 1) < 0.1, f"q{q}: T1 {fitted}")
        check(row["decisions"]["mutation_test"]["passes"], f"q{q}: the mutation test fails on a pinching device")
        want = "departs_below" if eps >= 0.015 else "exceeds_prediction" if eps <= -0.015 else None
        got = row["decisions"]["departure"]["outcome"]
        check(want is None or got == want, f"q{q}: departure {got} for eps {eps}: {row['departure_n16']}")
        check(eps != 0.0 or got == "consistent", f"q{q}: departure {got} without a departure")
        check(row["settle_n16"]["verdict"] == "unchanged_by_gap", f"q{q}: settle {row['settle_n16']}")
        for arm in ("delay", "unitary"):
            for n, value in row["p0"][arm].items():
                check(abs(value["measured_minus_modeled"]) < 3e-3, f"q{q}: {arm} N = {n} departs from its model")
    # The planning table is not the fitted prediction: T1 and p moved.
    cell = result[qubits[0]]["p0"]["measure"]["16"]
    check(abs(cell["p0"] - cell["planning"]) > 1e-3, "the planned device equals the planning table")
    # A device without pinching: the measure arm follows the unitary law.
    flat = {q: {"final": dict(r["final"])} for q, r in device_counts(models, contexts, FIXTURE_SHOTS).items()}
    for q in qubits:
        for n in MEASURE_STEPS:
            for name, source in zip(member_names("measure", n, q), member_names("unitary", TOP_STEPS, q), strict=True):
                flat[q]["final"][name] = flat[q]["final"][source]
    for row in evaluate(flat, contexts).values():
        check(not row["decisions"]["mutation_test"]["passes"], "the mutation test passes without pinching")
        check(row["decisions"]["departure"]["outcome"] == "departs_below", "no departure without pinching")
    # Random readout: every member reads half 0 and half 1, so the scale is zero and no qubit decides.
    uniform = {
        q: {"final": {name: (FIXTURE_SHOTS // 2, FIXTURE_SHOTS) for name in r["final"]}}
        for q, r in device_counts(models, contexts, FIXTURE_SHOTS).items()
    }
    for row in evaluate(uniform, contexts).values():
        check(not row["usable"] and "decisions" not in row, "a zero readout scale reaches a decision")
    # Thresholds.
    check(decide(0.5301, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "3.01 standard errors above 0.5 fails")
    check(not decide(0.5299, 0.01, 0.0, 0.01)["mutation_test"]["passes"], "2.99 standard errors above 0.5 passes")
    for z, outcome in (
        (-3.01, "departs_below"),
        (-2.99, "consistent"),
        (2.99, "consistent"),
        (3.01, "exceeds_prediction"),
    ):
        check(decide(0.9, 0.01, z * 0.01, 0.01)["departure"]["outcome"] == outcome, f"z = {z} is not {outcome}")
    for z, outcome in (
        (3.01, "reduced_by_gap"),
        (2.99, "unchanged_by_gap"),
        (-2.99, "unchanged_by_gap"),
        (-3.01, "deepened_by_gap"),
    ):
        check(classify_gap(z) == outcome, f"gap z = {z} is not {outcome}")
    if with_sweep:
        rows = run_sweep(contexts, sweep_cases(True), FIXTURE_SHOTS)
        failures = sweep_failures(rows, len(qubits))
        check(not failures, "; ".join(failures))
    return (
        f"measurement-sequence pinching analysis: ideal laws, readout correction and T1 fit, two-sided departure, "
        f"gap and mutation thresholds, planted devices on {len(qubits)} qubits and the reduced sweep hold"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preregistered analysis of the measurement-sequence pinching family")
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    sw = sub.add_parser("sweep", help="the estimator sweep over model devices off the planning point")
    sw.add_argument("--reduced", action="store_true", help="the planning point and the corner only")
    sub.add_parser("detectable", help="the minimum detectable departure on the planning and large model-error rows")
    args = parser.parse_args(argv)
    if args.self_test:
        print(self_test())
    elif args.command == "sweep":
        contexts = fixture_contexts()
        rows = run_sweep(contexts, sweep_cases(args.reduced), FIXTURE_SHOTS)
        print(json.dumps(rows, indent=2, sort_keys=True))
        failures = sweep_failures(rows, len(contexts))
        if failures:
            raise AnalysisError("estimator sweep: " + "; ".join(failures))
    elif args.command == "detectable":
        contexts = fixture_contexts()
        specs = {case["label"]: case for case in sweep_cases(False)}
        labels = ("planning", "model error, residual about +-0.01")
        print(json.dumps([minimum_detectable(contexts, specs[label], FIXTURE_SHOTS) for label in labels], indent=2))
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
