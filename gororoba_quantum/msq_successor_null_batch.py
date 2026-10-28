"""Batched stochastic null of the measurement-sequence envelope successor (docs/design/
measurement-sequence-envelope-successor.md, "Null calibration").

Each replicate is a device of the layout's width whose qubits draw a calibration from the rehearsal snapshot, a gamma
rate shape, the sx-error residual and the arm's truth, run through the production pipeline minus the order
conditions. The batched paths keep the bits of the scalar functions of msq_successor_analysis:

- `fit_gamma_rows` runs the gamma-rate fit (shape scan, per-shape Brent profile over log T, golden-section
  refinement in log k) for a block of series at once. The grid profile applies numpy's `exp` and array power as the
  scalar `_profiles` does, the refinement profile applies `math.exp` as `_profile` does, and every masked branch is
  an `np.where` whose arms are the scalar expressions;
- the Bloch chains, the delta-method sums and the solvers come from msq_envelope_null, whose rules (compensated
  `sum()`, `math.pow` for replicate-dependent squares, `math.exp` for replicate-dependent exponentials) they follow.

Per-replicate generators spawn from one QRNG seed by replicate index, so serial, pooled, blocked and sharded runs
write the same bytes.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
import numpy.typing as npt
from scipy.stats import beta, chi2

import diagnostic_experiments as de
import measurement_sequence_analysis as msa
import msq_envelope_analysis as ea
import msq_envelope_null as en
import msq_successor_analysis as su
from msq_envelope_null import libm_map, minimize_rows
from parallel import ordered_map

Floats = npt.NDArray[np.float64]
Ints = npt.NDArray[np.intp]

# Fits per call of the batched search: the grid profile holds SHAPE_POINTS + 1 searches per fit.
FIT_CHUNK = 2048
GRID = np.array((*su.GAMMA_SHAPES, su.EXPONENTIAL))
GRID_EXPONENTIAL = np.isinf(GRID)
GRID_SAFE = np.where(GRID_EXPONENTIAL, 1.0, GRID)
LOG_BOUNDS = (math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1]))


# --- gamma-rate fit on a replicate axis ----------------------------------------------------------------------


class FitRows(NamedTuple):
    """The gamma-rate fit of every row: T, shape (inf at the exponential edge), chi-square, lower grid edge."""

    t_s: Floats
    shape: Floats
    chi2: Floats
    lower_edge: npt.NDArray[np.bool_]


def grid_profiles(t: Floats, ys: Floats, w: Floats) -> tuple[Floats, Floats]:
    """(chi-square, T) of the per-shape profile of every row at every grid shape: su._profiles for all rows."""
    count = ys.shape[0]
    points = GRID.size
    yr, wr = np.repeat(ys, points, axis=0), np.repeat(w, points, axis=0)
    shapes, exponential = np.tile(GRID_SAFE, count), np.tile(GRID_EXPONENTIAL, count)

    def residual(u: Floats, rows: Ints) -> Floats:
        scale = np.exp(u)[:, None]
        k = shapes[rows][:, None]
        power = (1 + t[None, :] / (k * scale)) ** (-k)
        decay = np.where(exponential[rows][:, None], np.exp(-t[None, :] / scale), power)
        r = yr[rows] - (1 - 2 * decay)
        return np.asarray(np.sum(wr[rows] * r * r, axis=1))

    found = minimize_rows(residual, count * points, LOG_BOUNDS[0], LOG_BOUNDS[1], su.PROFILE_XATOL)
    values = residual(found, np.arange(count * points))
    return values.reshape(count, points), libm_map(math.exp, found).reshape(count, points)


def point_profiles(t: Floats, ys: Floats, w: Floats, shapes: Floats) -> tuple[Floats, Floats]:
    """(chi-square, T) of su._profile for every row at its own shape: the search over log T with `math.exp`."""

    def residual(u: Floats, rows: Ints) -> Floats:
        scale = libm_map(math.exp, u)[:, None]
        k = shapes[rows][:, None]
        r = ys[rows] - (1 - 2 * ((1 + t[None, :] / (k * scale)) ** (-k)))
        return np.asarray(np.sum(w[rows] * r * r, axis=1))

    found = minimize_rows(residual, ys.shape[0], LOG_BOUNDS[0], LOG_BOUNDS[1], su.PROFILE_XATOL)
    return residual(found, np.arange(ys.shape[0])), libm_map(math.exp, found)


def fit_gamma_chunk(t: Floats, ys: Floats, w: Floats) -> FitRows:
    """su._fit for every row of ys and w (rows, delays after the bracket)."""
    count = ys.shape[0]
    values, scales = grid_profiles(t, ys, w)
    best = np.argmin(values, axis=1)
    rows = np.arange(count)
    grid_chi, grid_t = values[rows, best], scales[rows, best]
    edge = best == GRID.size - 1
    out_t, out_shape, out_chi = grid_t.copy(), GRID[best].copy(), grid_chi.copy()
    lower = best == 0
    todo = np.nonzero(~edge)[0]
    if todo.size:
        shapes = np.array(su.GAMMA_SHAPES)
        low = libm_map(math.log, shapes[np.maximum(best[todo] - 1, 0)])
        high = libm_map(math.log, shapes[np.minimum(best[todo] + 1, su.SHAPE_POINTS - 1)])
        ty, tw = ys[todo], w[todo]
        a, b = high - su.GOLDEN_RATIO * (high - low), low + su.GOLDEN_RATIO * (high - low)
        fa = point_profiles(t, ty, tw, libm_map(math.exp, a))[0]
        fb = point_profiles(t, ty, tw, libm_map(math.exp, b))[0]
        for _ in range(su.GOLDEN_STEPS):
            left = fa < fb
            next_high, next_low = np.where(left, b, high), np.where(left, low, a)
            new_a = next_high - su.GOLDEN_RATIO * (next_high - next_low)
            new_b = next_low + su.GOLDEN_RATIO * (next_high - next_low)
            point = np.where(left, new_a, new_b)
            value = point_profiles(t, ty, tw, libm_map(math.exp, point))[0]
            high, low = next_high, next_low
            a, b = np.where(left, new_a, b), np.where(left, a, new_b)
            fa, fb = np.where(left, value, fb), np.where(left, fa, value)
        shape = libm_map(math.exp, (low + high) / 2)
        refined_chi, refined_t = point_profiles(t, ty, tw, shape)
        better = ~(refined_chi > grid_chi[todo])
        out_t[todo] = np.where(better, refined_t, grid_t[todo])
        out_shape[todo] = np.where(better, shape, GRID[best[todo]])
        out_chi[todo] = np.where(better, refined_chi, grid_chi[todo])
    return FitRows(out_t, out_shape, out_chi, lower)


def fit_gamma_rows(delays: Sequence[float], y: Floats, weights: Floats) -> FitRows:
    """su.fit_gamma_rate for every row of y and weights (rows, len(delays)): the bracket (delay 0) comes first and
    only the later points enter the fit."""
    t = np.array(delays[1:], dtype=float)
    ys, w = np.ascontiguousarray(y[:, 1:], dtype=float), np.ascontiguousarray(weights[:, 1:], dtype=float)
    parts = [fit_gamma_chunk(t, ys[i : i + FIT_CHUNK], w[i : i + FIT_CHUNK]) for i in range(0, ys.shape[0], FIT_CHUNK)]
    if not parts:
        empty = np.zeros(0)
        return FitRows(empty, empty, empty, np.zeros(0, dtype=bool))
    return FitRows(*(np.concatenate([part[k] for part in parts]) for k in range(4)))


def p_values(statistic: Floats, delays: Sequence[float]) -> Floats:
    """The fit's p-value at dof = delays after the bracket minus two (NaN when the dof is not positive)."""
    dof = len(delays) - 1 - 2
    if dof <= 0:
        return np.full(statistic.shape, np.nan)
    return np.asarray(chi2.sf(statistic, dof))


class FitMemo:
    """Gamma-rate fits keyed by the bytes of their series and weights, the batched counterpart of `su._fit`'s cache.

    A fit is a function of the series and weights after the bracket, so a row whose perturbation leaves them alone (a
    member group that is not part of the T1 series) shares the base fit; `ensure` fits the rows not yet held in one
    batched call.
    """

    def __init__(self, delays: Sequence[float]) -> None:
        self.delays = list(delays)
        self.table: dict[bytes, tuple[float, float, float, bool]] = {}

    def keys(self, y: Floats, w: Floats) -> list[bytes]:
        joined = np.ascontiguousarray(np.concatenate([y[:, 1:], w[:, 1:]], axis=1))
        raw, size = joined.tobytes(), joined.shape[1] * 8
        return [raw[i * size : (i + 1) * size] for i in range(joined.shape[0])]

    def ensure(self, y: Floats, w: Floats) -> list[bytes]:
        keys = self.keys(y, w)
        missing: dict[bytes, int] = {}
        for i, key in enumerate(keys):
            if key not in self.table and key not in missing:
                missing[key] = i
        if missing:
            picked = list(missing.values())
            fit = fit_gamma_rows(self.delays, y[picked], w[picked])
            for j, key in enumerate(missing):
                self.table[key] = (float(fit.t_s[j]), float(fit.shape[j]), float(fit.chi2[j]), bool(fit.lower_edge[j]))
        return keys

    def fit(self, y: Floats, w: Floats) -> FitRows:
        found = [self.table[key] for key in self.ensure(y, w)]
        return FitRows(
            np.array([f[0] for f in found]),
            np.array([f[1] for f in found]),
            np.array([f[2] for f in found]),
            np.array([f[3] for f in found], dtype=bool),
        )


# --- the successor's quantities on a replicate axis -----------------------------------------------------------


def corrected_series(p: dict[str, Floats]) -> Floats:
    """The bracket-corrected T1 series of every row: su.quantities' `series`."""
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2
    return np.stack([((1 - 2 * p[f"t1-{k}"]) - offset) / scale for k in range(msa.T1_COUNT)], axis=1)


def quantities_rows(
    p: dict[str, Floats], ctx: dict[str, Any], weights: Floats, memo: FitMemo
) -> tuple[dict[str, Floats], FitRows]:
    """su.quantities of every row (q = 1, T from the gamma-rate fit), p holding the per-row P(1) of each group,
    sx_shift and window_fraction; also the fit of every row."""
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2

    def corrected(key: str) -> Floats:
        return ((1 - 2 * p[key]) - offset) / scale

    fit = memo.fit(corrected_series(p), weights)
    t1 = fit.t_s
    q = np.ones(t1.shape[0])
    gate = en.gate_rows(ctx, p["sx_shift"])
    fraction = p["window_fraction"]
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    sx = en.damped_sx(t1, t2, gate)
    out: dict[str, Floats] = {"t1_s": t1, "scale": scale, "offset": offset}
    for arm, n in msa.group_keys():
        key = f"{arm}-{n}"
        model = (1 + en.corrected_rows(arm, n, t1, t2, en.tau_rows(arm, ctx, fraction), 0.0, gate, q, sx)) / 2
        out[f"p0:{key}"] = (1 + corrected(key)) / 2
        out[f"model:{key}"] = model
        out[f"diff:{key}"] = out[f"p0:{key}"] - model
    top = str(msa.TOP_STEPS)
    out["contrast"] = out[f"p0:measure-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing"] = out[f"p0:delay-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing_modeled"] = out[f"model:delay-{top}"] - out[f"model:unitary-{top}"]
    loss = en.implied_loss_rows(2 * out[f"p0:measure-{top}"] - 1, t1, t2, ctx, q, gate, fraction, sx)
    settle = en.corrected_rows("settle", msa.TOP_STEPS, t1, t2, en.tau_rows("settle", ctx, fraction), loss, gate, q, sx)
    out["implied_loss"] = loss
    out["gap_difference"] = out[f"p0:settle-{top}"] - (1 + settle) / 2
    return out, fit


STEP = 1e-5


def perturbed_points(x: Floats) -> tuple[Floats, Floats]:
    """The base point and the up and down point of each input of every replicate, stacked along the row axis (base
    rows first), and the step of each input: msa.propagate_many's points."""
    count, inputs = x.shape
    points = np.repeat(x[None, :, :], 1 + 2 * inputs, axis=0)
    spans = np.empty((inputs, count))
    for i in range(inputs):
        xi = x[:, i]
        small = np.abs(xi) / 10
        spans[i] = np.where(np.abs(xi) > 10 * STEP, STEP, np.where(small != 0, small, STEP))
        points[1 + 2 * i, :, i] = xi + spans[i]
        points[2 + 2 * i, :, i] = xi - spans[i]
    return points.reshape(-1, inputs), spans


class Propagated(NamedTuple):
    """msa.propagate_many for a block of replicates: base values, standard errors and shared parts per key."""

    value: dict[str, list[float]]
    se: dict[str, list[float]]
    shared: dict[str, list[float]]
    fit: FitRows


def propagate_rows(
    x: Floats,
    variances: Floats,
    weights: Floats,
    ctx: dict[str, Any],
    systematic: frozenset[int],
    keys: list[str],
    memo: FitMemo,
) -> Propagated:
    """msa.propagate_many of su.quantities for every replicate (rows of x, variances and weights)."""
    count, inputs = x.shape
    flat, spans = perturbed_points(x)
    tiled = np.tile(weights, (1 + 2 * inputs, 1))
    out, fit = quantities_rows({key: np.ascontiguousarray(flat[:, j]) for j, key in enumerate(keys)}, ctx, tiled, memo)
    names = list(out)
    table = np.stack([out[name].reshape(1 + 2 * inputs, count) for name in names], axis=1)
    totals = np.zeros((len(names), count))
    shared = np.zeros((len(names), count))
    for i in range(inputs):
        change = (table[1 + 2 * i] - table[2 + 2 * i]) / (2 * spans[i])[None, :]
        term = en.square_rows(change) * variances[:, i][None, :]
        totals = totals + term
        if i in systematic:
            shared = shared + term
    base = FitRows(fit.t_s[:count], fit.shape[:count], fit.chi2[:count], fit.lower_edge[:count])
    return Propagated(
        {name: table[0, k].tolist() for k, name in enumerate(names)},
        {name: np.sqrt(totals[k]).tolist() for k, name in enumerate(names)},
        {name: np.sqrt(shared[k]).tolist() for k, name in enumerate(names)},
        base,
    )


class Batch(NamedTuple):
    """The usable replicates of one qubit slot's batch: positions, inputs and the context with series weights."""

    usable: list[int]
    prepared: list[su.Prepared]
    x: Floats
    variances: Floats
    weights: Floats


def prepare_batch(qubits: Sequence[int], ctx: dict[str, Any], member_counts: Sequence[dict[str, Any]]) -> Batch:
    prepared = [su.prepare(q, counts, ctx) for q, counts in zip(qubits, member_counts, strict=True)]
    usable = [i for i, item in enumerate(prepared) if item.usable]
    chosen = [prepared[i] for i in usable]
    return Batch(
        usable,
        chosen,
        np.array([item.x for item in chosen]),
        np.array([item.variances for item in chosen]),
        np.array([item.ctx["weights"] for item in chosen]),
    )


def ensure_batch(batch: Batch, memo: FitMemo) -> None:
    """Fit every series the batch's perturbation points hold, in one call."""
    if not batch.usable:
        return
    flat, _ = perturbed_points(batch.x)
    keys = batch.prepared[0].keys
    p = {key: np.ascontiguousarray(flat[:, j]) for j, key in enumerate(keys)}
    memo.ensure(corrected_series(p), np.tile(batch.weights, (1 + 2 * batch.x.shape[1], 1)))


def evaluate_rows(
    qubits: Sequence[int],
    ctx: dict[str, Any],
    member_counts: Sequence[dict[str, Any]],
    memo: FitMemo,
    batch: Batch | None = None,
) -> list[dict[str, Any]]:
    """su._evaluate (descriptive False) of every replicate of one calibration, one qubit id and one counts dict per
    replicate, before the device-level steps of su.finish_rows."""
    batch = prepare_batch(qubits, ctx, member_counts) if batch is None else batch
    rows: list[dict[str, Any] | None] = [None] * len(qubits)
    for i, (qubit, counts) in enumerate(zip(qubits, member_counts, strict=True)):
        if i not in batch.usable:
            rows[i] = su.unusable_row(qubit, su.prepare(qubit, counts, ctx).readout)
    if batch.usable:
        first = batch.prepared[0]
        systematic = frozenset({first.position["sx_shift"], first.position["window_fraction"]})
        fitted = propagate_rows(batch.x, batch.variances, batch.weights, ctx, systematic, first.keys, memo)
        curve_grid = en.curve_values(
            np.array(fitted.value["t1_s"]), np.ones(len(batch.usable)), ctx, msa.WINDOW_RELAX_FRACTION
        )
        dof = len(ctx["t1_delays_s"]) - 1 - 2
        pvalue = p_values(fitted.fit.chi2, ctx["t1_delays_s"])
        for j, i in enumerate(batch.usable):
            item = batch.prepared[j]
            shape = float(fitted.fit.shape[j])
            fit = {
                "t_s": float(fitted.fit.t_s[j]),
                "shape": shape,
                "chi2": float(fitted.fit.chi2[j]),
                "dof": dof,
                "p_value": float(pvalue[j]) if dof > 0 else None,
                "exponential_edge": math.isinf(shape),
                "lower_edge": bool(fitted.fit.lower_edge[j]),
            }
            rows[i] = su.assemble_row(
                qubits[i],
                member_counts[i],
                item.ctx,
                item.readout,
                (
                    {name: column[j] for name, column in fitted.value.items()},
                    {name: column[j] for name, column in fitted.se.items()},
                    {name: column[j] for name, column in fitted.shared.items()},
                ),
                fit,
                en.curves_of(curve_grid, j),
                False,
            )
    return [row for row in rows if row is not None]


# --- shape bound on a replicate axis ---------------------------------------------------------------------------


def gamma_p0_rows(ctx: dict[str, Any], t_s: Floats, shapes: Floats) -> Floats:
    """su.gamma_measure_p0 at every (T, finite shape) pair: the measure arm's N = 16 P0 at q = 1 averaged over the
    gamma rate distribution of mean 1 / T by the weighted nodes of su.gamma_rule."""
    count = t_s.shape[0]
    rates = np.empty((count, su.GAMMA_NODES))
    weights = np.empty((count, su.GAMMA_NODES))
    for k in np.unique(shapes):
        rows = shapes == k
        nodes, found = su.gamma_rule(float(k))
        rates[rows] = nodes[None, :] / (k * t_s[rows])[:, None]
        weights[rows] = found[None, :]
    t1 = (1 / rates).T.reshape(-1)
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    gate = en.gate_rows(ctx, 0.0)
    tau = msa.tau_of("measure", ctx)
    z = en.corrected_rows("measure", msa.TOP_STEPS, t1, t2, tau, 0.0, gate, np.ones(t1.shape[0]))
    values = ((1 + z) / 2).reshape(su.GAMMA_NODES, count)
    total: Any = 0.0
    for node in range(su.GAMMA_NODES):
        total = total + weights[:, node] * values[node]
    return np.asarray(total)


def exponential_p0_rows(ctx: dict[str, Any], t_s: Floats) -> Floats:
    """The measure arm's N = 16 P0 at q = 1 on the exponential model at each T: su.gamma_measure_p0 at the edge."""
    t2 = np.minimum(ctx["t2_s"], 2 * t_s)
    z = en.corrected_rows(
        "measure",
        msa.TOP_STEPS,
        t_s,
        t2,
        msa.tau_of("measure", ctx),
        0.0,
        en.gate_rows(ctx, 0.0),
        np.ones(t_s.shape[0]),
    )
    return np.asarray((1 + z) / 2)


def shape_bound_rows(ctx: dict[str, Any], t_s: Floats, shapes: Sequence[float] = su.SHAPE_DOMAIN_SHAPES) -> Floats:
    """su._shape_bound for every lifetime in t_s at one context: the largest |rate-averaged - exponential| over the
    shapes."""
    grid = np.array([float(k) for k in shapes])
    count = t_s.shape[0]
    exponential = exponential_p0_rows(ctx, t_s)
    pairs_t, pairs_k = np.tile(t_s, grid.size), np.repeat(grid, count)
    gamma = gamma_p0_rows(ctx, pairs_t, pairs_k).reshape(grid.size, count)
    best = np.zeros(count)
    for k in range(grid.size):
        best = np.maximum(best, np.abs(gamma[k] - exponential))
    return best


# --- snapshot, layout and per-calibration constants ----------------------------------------------------------

SCHEMA = "msq-successor-null-v1"
# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json, index 0.
SUCCESSOR_NULL_SEED = 35417
SHOTS = 8192
# Replicates per mapped block; a block shares one batched evaluation per calibration.
NULL_BLOCK = 25
CONFIDENCE = 0.95
FALSE_FIRE_CEILING = 0.01
ISSUANCE_FLOOR = 0.8
CARRYOVER_VERDICTS = 299
# The single-outlier detectable settle gap is (SETTLE_Z + SETTLE_POWER_Z) times the per-qubit test's denominator
# (`sparse_gap`): 1.28 is the one-sided normal quantile of power 0.9.
SETTLE_POWER_Z = 1.28
SPARSE_TARGET_POWER = 0.9
COMMON_GAP_FACTOR = 4.0
# The sparse and minority arms plant their truth on this many leading slots; the rest stay healthy.
PLANTED_QUBITS = 2
MINORITY_ARMS = ("q-minority", "plateau-minority")
# The measured detectable gap of each pool size, as a multiple of `sparse_gap`: the scale at which the per-qubit
# settle veto withholds SPARSE_TARGET_POWER of PLANTED_QUBITS planted gaps (`calibrate_sparse_scale`).
SPARSE_SCALE_EVIDENCE = "docs/evidence/measurement_sequence/successor-sparse-scale.json"
# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json, index 2: the calibration draws apart from the null's.
SPARSE_CALIBRATION_SEED = 26209
# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-27T231303Z.json, index 3: the settle-sparse null that decides the
# family power target (`--arm settle-sparse --seed qrng:...#3`), drawn after SUCCESSOR_NULL_SEED's counts were read.
SPARSE_CONFIRMATION_SEED = 15296
# Replicates per calibration point (per-qubit power standard error about 0.01), the second point's scale and the
# secant steps before the calibration gives up.
SPARSE_CALIBRATION_REPLICATES = 500
SPARSE_CALIBRATION_STEP = 1.25
SPARSE_CALIBRATION_STEPS = 6
# The measure-arm loss per step that probes the gap's slope, and the secant steps that solve for the planted size.
SPARSE_LOSS_PROBE = 0.005
SPARSE_ITERATIONS = 3
# Fixed-point steps of the q arm's planted value, whose q_hat and standard error depend on q.
Q_ITERATIONS = 4
BOUNDARY_OFFSETS = (0, 1, 2)
# Standard errors inside the boundary that the carryover arms solve for, and the fixed-point steps of the solve.
CARRIED_OFFSETS = (0.0, 1.0, 2.0, 3.0)
CARRIED_ITERATIONS = 8
SETTLE_POOLS = (8, 9, None)
# The settle-sparse power target holds for every pool of SETTLE_POOLS at once, so each pool's one-sided bound takes a
# Bonferroni share of 1 - CONFIDENCE.
SPARSE_FAMILY_CONFIDENCE = 1 - (1 - CONFIDENCE) / len(SETTLE_POOLS)
READERS = len(de.MSQR_READER_STEPS) * len(de.MSQ_SIGNED)
PLATEAU_EVIDENCE = "docs/evidence/measurement_sequence/envelope-run-exploratory.json"
ARMS = (
    "carryover-positive",
    "carryover-negative",
    "carryover-boundary",
    "q-tolerance",
    "q-minority",
    "settle-common",
    "settle-sparse",
    "plateau-low",
    "plateau-retained",
    "plateau-minority",
    "gamma",
)
ROOT = Path(__file__).resolve().parents[1]


class Setup(NamedTuple):
    """Everything a replicate needs from the rehearsal snapshot, fixed before any draw."""

    qubits: tuple[int, ...]
    width: int
    contexts: tuple[dict[str, Any], ...]
    floor: float
    equilibrium_s: float
    pattern_bits: tuple[tuple[int, ...], ...]
    slopes: tuple[float, ...]
    allocation: tuple[float, ...]
    positive: tuple[tuple[str, ...], ...]
    negative: tuple[tuple[str, ...], ...]
    carried: tuple[dict[float, float], ...]
    tolerance: tuple[float, ...]
    q_planted: tuple[float, ...]
    settle_se: float
    sparse_scale: dict[int, float]
    sparse_loss: tuple[dict[int, float], ...]
    vertex_base: tuple[dict[str, tuple[int, int]], ...]
    vertex_probed: tuple[dict[str, tuple[int, int]], ...]
    plateau: tuple[tuple[float, float], ...]
    plateau_low: tuple[int, ...]
    digests: dict[str, str]


def snapshot_executed(record: dict[str, Any], properties: dict[str, Any]) -> dict[str, Any]:
    """The execution-evidence entries `msa.contexts_from_record` reads, from the snapshot's backend properties:
    per layout qubit its sx error and duration and measure duration in seconds, T1 and T2 in microseconds and the
    assignment errors."""
    gates = {
        gate["qubits"][0]: {item["name"]: item["value"] for item in gate["parameters"]}
        for gate in properties["gates"]
        if gate["gate"] == "sx"
    }
    executed: dict[str, Any] = {}
    for qubit in (int(q) for q in record["family_configuration"]["qubits"]):
        values = {item["name"]: item["value"] for item in properties["qubits"][qubit]}
        sx = gates[qubit]
        executed[msa.ro0_name(qubit)] = {
            "placed_gate_calibration": {
                str(qubit): {
                    "sx_error": float(sx["gate_error"]),
                    "sx_duration_s": float(sx["gate_length"]) * 1e-9,
                    "measure_duration_s": float(values["readout_length"]) * 1e-9,
                }
            },
            "placed_qubit_calibration": {
                str(qubit): {name: float(values[name]) for name in ("T1", "T2", "prob_meas1_prep0", "prob_meas0_prep1")}
            },
        }
    return executed


def load_snapshot(record_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    """(record, snapshot properties, snapshot sha256) of a dry-run record directory; the snapshot is the file the
    record's envelope names, checked against its digest."""
    record = json.loads((record_dir / "record.json").read_text())
    digest = str(record["envelope"]["planning_snapshot_sha256"])
    data = (record_dir / "envelope-snapshots" / f"{digest}.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"the snapshot of {record_dir} differs from its digest {digest}")
    return record, json.loads(data)["properties"], digest


def residual_slope(ctx: dict[str, Any]) -> float:
    """d(unitary N = 16 residual) / d(sx error factor) at one planned context, from the noise-free model at factors
    1 and 3 through the successor's rows."""
    residuals = []
    for factor in (1.0, 3.0):
        model = msa.device_model(ctx, p_init=0.0, sx_error=factor * ctx["sx_error"])
        counts = msa.device_counts({0: model}, {0: ctx}, SHOTS)[0]
        row = su._evaluate((0, counts, ctx), False)
        residuals.append(float(row["gate_systematic_n16"]["unitary_residual"]))
    return (residuals[1] - residuals[0]) / 2.0


def reader_stems() -> list[tuple[int, int]]:
    """(steps, signed index) of the measure row each reader follows, in reader order."""
    return [(steps, s) for steps in de.MSQR_READER_STEPS for s in range(len(de.MSQ_SIGNED))]


def predecessor_name(index: int, qubit: int) -> str:
    steps, s = reader_stems()[index]
    return msa.member_names("measure", steps, qubit)[s]


def reader_standard_error(ctx: dict[str, Any], predecessor_ones: Sequence[int], excitation: float) -> float:
    """The standard error of the reader statistic's estimate of D for a carried excitation: each reader's conditional
    difference has the variance of two conditioning classes (the predecessor read 1 or 0) at the reader P1 pooled over
    all readers and both classes, as `su.carryover_reader` weights them, and the twelve combine by inverse variance
    and divide by the squared readout contrast."""
    e01, e10 = ctx["e01"], ctx["e10"]
    contrast = 1 - e01 - e10
    survive = math.exp(-ctx["prereadout_s"] / ctx["t1_cal_s"])
    classes = []
    for ones in predecessor_ones:
        n1, n0 = ones, SHOTS - ones
        latent = min(max((ones / SHOTS - e01) / contrast, 0.0), 1.0)
        after_one = latent * (1 - e10) / (latent * (1 - e10) + (1 - latent) * e01)
        after_zero = latent * e10 / (latent * e10 + (1 - latent) * (1 - e01))
        classes.append(
            (
                n1,
                n0,
                e01 + contrast * excitation * survive * after_one,
                e01 + contrast * excitation * survive * after_zero,
            )
        )
    shots = sum(n1 + n0 for n1, n0, _, _ in classes)
    pooled = sum(n1 * p1 + n0 * p0 for n1, n0, p1, p0 in classes) / shots
    spread = max(pooled * (1 - pooled), 1.0 / shots)
    inverse = sum(1.0 / (spread * (1 / n1 + 1 / n0)) for n1, n0, _, _ in classes)
    return 1.0 / math.sqrt(inverse) / contrast**2


def calibration_constants(ctx: dict[str, Any]) -> dict[str, Any]:
    """The noise-free constants of one planned context: the residual slope, the carryover allocation and its vertex
    classes, the standard error of the reader statistic, the q tolerance bound and the settle gap's standard error."""
    qubit = 0
    model = msa.device_model(ctx, p_init=0.0)
    counts = msa.device_counts({qubit: model}, {qubit: ctx}, SHOTS)[qubit]
    row = su._evaluate((qubit, counts, ctx), False)
    allocation = su.carryover_allocation((qubit, counts, ctx, 1e-3))
    predecessor_ones = [counts["final"][predecessor_name(index, qubit)][0] for index in range(READERS)]
    margin = su.SCREEN_FRACTION * su.BOUND_FLOOR
    carried_by_offset = {}
    for offset in CARRIED_OFFSETS:
        excitation = margin / allocation["allocation"]
        for _ in range(CARRIED_ITERATIONS):
            excitation = max(
                margin / allocation["allocation"] - offset * reader_standard_error(ctx, predecessor_ones, excitation),
                0.0,
            )
        carried_by_offset[offset] = excitation
    sensitivity = su.q_sensitivity(ctx, ctx["t1_cal_s"])
    return {
        "slope": residual_slope(ctx),
        "allocation": float(allocation["allocation"]),
        "positive": tuple(allocation["positive_classes"]),
        "negative": tuple(allocation["negative_classes"]),
        "carried": carried_by_offset,
        "tolerance": 1 - su.SCREEN_FRACTION * su.BOUND_FLOOR / sensitivity,
        "settle_se": float(row["settle_n16"]["se"]),
        "base": dict(
            msa.device_counts({qubit: msa.device_model(ctx, p_init=0.0)}, {qubit: ctx}, su.VERTEX_SHOTS)[qubit]["final"]
        ),
        "probed": dict(
            msa.device_counts({qubit: msa.device_model(ctx, p_init=su.VERTEX_PROBE)}, {qubit: ctx}, su.VERTEX_SHOTS)[
                qubit
            ]["final"]
        ),
    }


def plateau_pairs() -> tuple[tuple[tuple[float, float], ...], str]:
    """The retained run's (T1, q) of its informative qubits from the committed exploratory analysis, and the file's
    sha256."""
    data = (ROOT / PLATEAU_EVIDENCE).read_bytes()
    analysis = json.loads(data)["analysis"]
    pairs = tuple(
        (float(analysis["qubits"][str(q)]["fitted"]["t1_s"]), float(analysis["qubits"][str(q)]["fitted"]["q"]))
        for q in analysis["device"]["informative_qubits"]
    )
    return pairs, hashlib.sha256(data).hexdigest()


def sparse_scales() -> tuple[dict[int, float], str]:
    """The measured detectable-gap scale of each calibrated pool size from SPARSE_SCALE_EVIDENCE, and the file's
    sha256; empty before the first calibration."""
    path = ROOT / SPARSE_SCALE_EVIDENCE
    if not path.exists():
        return {}, ""
    data = path.read_bytes()
    pools = json.loads(data)["pools"]
    return {int(pool): float(entry["scale"]) for pool, entry in pools.items()}, hashlib.sha256(data).hexdigest()


def with_sparse_scale(setup: Setup, scale: dict[int, float]) -> Setup:
    """`setup` with the sparse arm's planted losses solved at `scale` times `sparse_gap` for each pool size."""
    items = [
        (ctx, setup.equilibrium_s, {pool: factor * sparse_gap(setup.settle_se, pool) for pool, factor in scale.items()})
        for ctx in setup.contexts
    ]
    return setup._replace(sparse_scale=dict(scale), sparse_loss=tuple(ordered_map(sparse_losses, items, min_items=2)))


def build_setup(record_dir: Path) -> Setup:
    """The null's fixed inputs from a dry-run record directory."""
    record, properties, digest = load_snapshot(record_dir)
    configuration = record["family_configuration"]
    floor, reason = msa.bound_floor(msa.record_backends(record))
    if floor is None:
        raise msa.AnalysisError(f"no registered floor: {reason}")
    contexts = msa.contexts_from_record(record, snapshot_executed(record, properties))
    qubits = tuple(int(q) for q in configuration["qubits"])
    planned = su.with_planning(contexts, floor)
    pool = tuple(planned[q] for q in qubits)
    constants = list(ordered_map(calibration_constants, list(pool), min_items=2))
    plateau, plateau_digest = plateau_pairs()
    dt = float(configuration["dt_seconds"])
    width = int(configuration["layout_width"])
    equilibrium_s = int(configuration["equilibrium_delay_dt"]) * dt
    tolerance = tuple(c["tolerance"] for c in constants)
    settle_se = float(np.median([c["settle_se"] for c in constants]))
    scale, scale_digest = sparse_scales()
    q_items = [(ctx, bound, equilibrium_s, width) for ctx, bound in zip(pool, tolerance, strict=True)]
    setup = Setup(
        qubits=qubits,
        width=width,
        contexts=pool,
        floor=floor,
        equilibrium_s=equilibrium_s,
        pattern_bits=tuple(tuple(int(b) for b in row) for row in configuration["pattern_bits"]),
        slopes=tuple(c["slope"] for c in constants),
        allocation=tuple(c["allocation"] for c in constants),
        positive=tuple(c["positive"] for c in constants),
        negative=tuple(c["negative"] for c in constants),
        carried=tuple(c["carried"] for c in constants),
        tolerance=tolerance,
        q_planted=tuple(ordered_map(planted_q, q_items, min_items=2)),
        settle_se=settle_se,
        sparse_scale={},
        sparse_loss=tuple({} for _ in pool),
        vertex_base=tuple(c["base"] for c in constants),
        vertex_probed=tuple(c["probed"] for c in constants),
        plateau=plateau,
        plateau_low=tuple(i for i, (_, q) in enumerate(plateau) if q < min(tolerance)),
        digests={"snapshot_sha256": digest, "plateau_sha256": plateau_digest, "sparse_scale_sha256": scale_digest},
    )
    return with_sparse_scale(setup, scale)


# --- truth of one qubit --------------------------------------------------------------------------------------


class Truth(NamedTuple):
    """One qubit's truth in a replicate: the mean lifetime and the rate shape (inf: exponential), the relaxation
    target q, the sx-error factor, the carried excitation of each member class, the reader's carried excitation, the
    settle arm's planted gap in corrected P0 and the z lost per pinch in the measure arm alone (a post-measurement
    tail that the settle arm's idles let decay, `msa.device_model` with eps_settle = 0)."""

    t_s: float
    shape: float
    q: float
    sx_factor: float
    excitation: dict[str, float]
    reader: float
    gap: float
    loss: float = 0.0


def lifetimes(t_s: float, shape: float) -> tuple[Floats, Floats]:
    """(lifetimes, weights) of the rate nodes of su.gamma_rule for a gamma rate distribution of mean 1 / t_s; one
    node of weight 1 at the exponential limit."""
    if math.isinf(shape):
        return np.array([t_s]), np.array([1.0])
    nodes, weights = su.gamma_rule(shape)
    return 1 / (nodes / (shape * t_s)), weights


def member_probabilities(ctx: dict[str, Any], qubit: int, truth: Truth, equilibrium_s: float) -> dict[str, float]:
    """P(final = 1) of every member of the qubit, its equilibrium row ("eq") included, on the Bloch model averaged
    over the lifetime nodes: the chain at z_eq = 1 gives z = M[2, 2] z0 + M[2, 3] q, the pre-readout wait relaxes
    each node toward q, and the assignment errors read the mean."""
    t1, weights = lifetimes(truth.t_s, truth.shape)
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    shaped = {**ctx, "sx_error": truth.sx_factor * ctx["sx_error"]}
    gate = en.gate_rows(shaped, 0.0)
    sx = en.damped_sx(t1, t2, gate)
    contrast = 1 - ctx["e01"] - ctx["e10"]
    relax = np.exp(-ctx["prereadout_s"] / t1)
    q = truth.q
    nodes = t1.shape[0]

    def observe(z: Floats, shift: float = 0.0) -> float:
        waited = float(np.sum(weights * (q - (q - z) * relax)))
        observed = contrast * waited + ctx["e10"] - ctx["e01"]
        return float(min(max((1 - observed) / 2 + shift, 0.0), 1.0))

    out: dict[str, float] = {}
    for arm, n in msa.group_keys():
        excitation = truth.excitation.get(f"{arm}-{n}", 0.0)
        tau = np.full(nodes, msa.tau_of(arm, shaped))
        shift = -contrast * truth.gap if arm == "settle" else 0.0
        loss = np.full(nodes, truth.loss if arm == "measure" else 0.0)
        for sign in (1, -1):
            chain = en.chain_rows(arm, n, t1, t2, tau, loss, gate, sx, sign)
            p1 = observe(chain[:, 2, 2] * (1 - 2 * excitation) + chain[:, 2, 3] * q, shift)
            for tag, name in zip(msa.SIGNED, msa.member_names(arm, n, qubit), strict=True):
                if (1 if tag[0] == "p" else -1) == sign:
                    out[name] = p1
    out[msa.ro0_name(qubit)] = observe(np.full(nodes, 1 - 2 * truth.excitation.get("ro0", 0.0)))
    for k, name in enumerate(msa.t1_names(qubit)):
        start = q + 1 - 2 * truth.excitation.get(f"t1-{k}", 0.0)
        out[name] = observe(q - start * np.exp(-ctx["t1_delays_s"][k] / t1))
    out[de.msqr_equilibrium_member(qubit)] = observe(q - (q - 1) * np.exp(-equilibrium_s / t1))
    return out


def expected_counts(ctx: dict[str, Any], truth: Truth, equilibrium_s: float, shots: int) -> dict[str, tuple[int, int]]:
    """The rounded expected (ones, shots) of every member of qubit 0 under `truth`, the equilibrium row included."""
    probabilities = member_probabilities(ctx, 0, truth, equilibrium_s)
    return {name: (round(p * shots), shots) for name, p in probabilities.items()}


def planted_q(item: tuple[dict[str, Any], float, float, int]) -> float:
    """The q arm's planted relaxation target at one calibration: the q at which the screen (`su.q_screen`, Bonferroni
    over the width, tolerance at the fitted T) puts the lower confidence bound of the expected counts at SHOTS on its
    tolerance, so about half the draws pass it. Each fixed-point step moves q by the tolerance less the lower
    confidence bound, which also absorbs q_hat's offset from the planted q. item = (context, the tolerance at the
    calibrated T1 as the start, equilibrium idle, width)."""
    ctx, bound, equilibrium_s, width = item
    keys = {"ro0": msa.ro0_name(0), "eq": de.msqr_equilibrium_member(0)}
    keys.update({f"t1-{k}": name for k, name in enumerate(msa.t1_names(0))})
    q = bound
    for _ in range(Q_ITERATIONS):
        counts = expected_counts(ctx, Truth(ctx["t1_cal_s"], math.inf, q, 1.0, {}, 0.0, 0.0), equilibrium_s, SHOTS)
        estimate = su.equilibrium_estimate({key: counts[name] for key, name in keys.items()}, ctx, equilibrium_s)
        screen = su.q_screen(estimate, su.q_sensitivity(ctx, estimate["t1_s"]), width)
        q += screen["tolerance"] - screen["lower_bound"]
    return q


def sparse_gap(settle_se: float, pool: int) -> float:
    """The single-outlier detectable settle gap at `pool` qubits: (SETTLE_Z + SETTLE_POWER_Z) times the per-qubit
    test's denominator sqrt(s^2 + tau^2 + se^2), tau at its floor and se the median standard error of the pool - 1
    others (`su._robust_others`). A second planted qubit among the others moves their median and MAD, which this
    size leaves out; the sparse arm plants it times the pool's measured scale (`calibrate_sparse_scale`)."""
    spread = settle_se**2 + su.SETTLE_TAU_FLOOR**2
    return (su.SETTLE_Z + SETTLE_POWER_Z) * math.sqrt(spread + math.pi / 2 * spread / (pool - 1))


def tail_gap(ctx: dict[str, Any], loss: float, equilibrium_s: float) -> float:
    """The noise-free settle gap of one calibration under a measure-arm loss per pinch: the expected counts at
    su.VERTEX_SHOTS through su._evaluate."""
    counts = expected_counts(
        ctx, Truth(ctx["t1_cal_s"], math.inf, 1.0, 1.0, {}, 0.0, 0.0, loss), equilibrium_s, su.VERTEX_SHOTS
    )
    del counts[de.msqr_equilibrium_member(0)]
    row = su._evaluate((0, {"final": counts}, ctx), False)
    return float(row["settle_n16"]["gap_difference"])


def sparse_losses(item: tuple[dict[str, Any], float, dict[int, float]]) -> dict[int, float]:
    """The measure-arm loss per pinch whose noise-free settle gap, less the gap at no loss, has the target size of
    each pool width: a secant from SPARSE_LOSS_PROBE, then SPARSE_ITERATIONS secant steps. item = (context,
    equilibrium idle, {pool width: target gap})."""
    ctx, equilibrium_s, targets = item
    if not targets:
        return {}
    base = tail_gap(ctx, 0.0, equilibrium_s)
    slope = abs(tail_gap(ctx, SPARSE_LOSS_PROBE, equilibrium_s) - base) / SPARSE_LOSS_PROBE
    out = {}
    for pool, target in sorted(targets.items()):
        loss = target / slope
        for _ in range(SPARSE_ITERATIONS):
            loss *= target / abs(tail_gap(ctx, loss, equilibrium_s) - base)
        out[pool] = loss
    return out


# --- arms and the replicate generator ------------------------------------------------------------------------


class Case(NamedTuple):
    """One configuration of an arm: `active` qubits enter the selection (the rest are withheld before it), and
    `param` is the arm's free number (standard errors inside the carryover boundary)."""

    arm: str
    label: str
    active: int
    param: float


def arm_cases(arm: str, width: int) -> list[Case]:
    """The configurations an arm runs, each on the same replicate draws."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}; the arms are {', '.join(ARMS)}")
    if arm == "carryover-boundary":
        return [Case(arm, f"{m}-se-inside", width, float(m)) for m in BOUNDARY_OFFSETS]
    if arm in ("settle-common", "settle-sparse"):
        return [Case(arm, f"{m or width}-qubits", m or width, 0.0) for m in SETTLE_POOLS]
    return [Case(arm, "all", width, 3.0 if arm.startswith("carryover") else 0.0)]


def minimum_verdicts(arm: str) -> int:
    """The verdicts an arm runs to: issued verdicts for the carryover arms and plateau-retained, verdicts that select
    a planted qubit (`summarize`, "counted") for the minority arms."""
    counted = ("carryover-positive", "carryover-negative", "plateau-retained", *MINORITY_ARMS)
    return CARRYOVER_VERDICTS if arm in counted else 0


def planted_count(arm: str, active: int) -> int:
    """The leading slots that carry the arm's planted truth in the sparse and minority arms; zero elsewhere."""
    return min(PLANTED_QUBITS, active) if arm in ("settle-sparse", *MINORITY_ARMS) else 0


def sparse_loss(setup: Setup, j: int, pool: int) -> float:
    """The sparse arm's planted measure-arm loss at calibration j and pool size `pool`."""
    if pool not in setup.sparse_scale:
        raise ValueError(
            f"pool size {pool} has no measured sparse gap scale in {SPARSE_SCALE_EVIDENCE}; "
            "run scripts/msq_successor_null.py RECORD_DIR --calibrate-sparse"
        )
    return setup.sparse_loss[j][pool]


def carried(setup: Setup, case: Case, j: int) -> float:
    """The carried excitation of a carryover arm at calibration j: D = 0.0047 / A_q less `param` reader standard
    errors, with the standard error taken at D itself."""
    return setup.carried[j][case.param]


def slot_truth(setup: Setup, case: Case, j: int, slot: int, shape: float, residual: float, pair: float) -> Truth:
    """The truth of slot `slot` at calibration j in one case. A carryover arm plants the excitation on the member
    classes of the allocation vertex whose shift has the arm's sign; the reader carries the same excitation. The
    sparse settle arm plants a measure-arm loss on its first PLANTED_QUBITS slots; the plateau arms take the retained
    pair at the uniform draw `pair`, plateau-low among the pairs below every tolerance bound. The minority arms plant
    the q arm's value or a retained pair on their first PLANTED_QUBITS slots alone."""
    ctx = setup.contexts[j]
    t_s, q, excitation, reader, gap, loss = ctx["t1_cal_s"], 1.0, {}, 0.0, 0.0, 0.0
    planted = slot < planted_count(case.arm, case.active)
    if case.arm in ("carryover-positive", "carryover-negative", "carryover-boundary"):
        reader = carried(setup, case, j)
        labels = setup.negative[j] if case.arm == "carryover-negative" else setup.positive[j]
        excitation = dict.fromkeys(labels, reader)
    elif case.arm == "q-tolerance" or (case.arm == "q-minority" and planted):
        q = setup.q_planted[j]
    elif case.arm == "settle-common":
        gap = COMMON_GAP_FACTOR * su.SETTLE_TAU_FLOOR
    elif case.arm == "settle-sparse" and planted:
        loss = sparse_loss(setup, j, case.active)
    elif case.arm == "plateau-low":
        (t_s, q), shape = setup.plateau[setup.plateau_low[int(pair * len(setup.plateau_low))]], math.inf
    elif case.arm == "plateau-retained" or (case.arm == "plateau-minority" and planted):
        (t_s, q), shape = setup.plateau[int(pair * len(setup.plateau))], math.inf
    factor = max(0.0, 1.0 + residual / setup.slopes[j])
    return Truth(t_s, shape, q, factor, excitation, reader, gap, loss)


class Drawn(NamedTuple):
    """One replicate's draws in one case: per slot the calibration, truth, member counts, equilibrium count,
    pattern counts and the reader and predecessor bits."""

    replicate: int
    calibration: list[int]
    truths: list[Truth]
    counts: list[dict[str, Any]]
    equilibrium: list[tuple[int, int]]
    patterns: list[list[tuple[int, int]]]
    predecessors: list[list[np.ndarray]]
    readers: list[list[np.ndarray]]


def replicate_generator(seed: int, index: int) -> np.random.Generator:
    """The generator of replicate `index`: the child of SeedSequence(seed) at that spawn position."""
    return np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(index,)))


def draw_bits(
    generator: np.random.Generator, ctx: dict[str, Any], truth: Truth, probabilities: dict[str, float], qubit: int
) -> tuple[list[np.ndarray], list[np.ndarray], list[int]]:
    """Shot-ordered predecessor and reader bits of one qubit. A predecessor's latent end state is excited with the
    member's excited probability and is read through the assignment errors; the reader starts in the ground state
    plus the carried excitation times the latent end state, which relaxes over the pre-readout wait, and is read
    through the assignment errors. Returns the predecessors' bits, the readers' bits and the predecessors' ones."""
    e01, e10 = ctx["e01"], ctx["e10"]
    contrast = 1 - e01 - e10
    t1, weights = lifetimes(truth.t_s, truth.shape)
    survive = float(np.sum(weights * np.exp(-ctx["prereadout_s"] / t1)))
    names = [predecessor_name(i, qubit) for i in range(READERS)]
    p1 = np.array([probabilities[name] for name in names])
    p_latent = np.clip((p1 - e01) / contrast, 0.0, 1.0)
    uniform = generator.random((3, READERS, SHOTS))
    latent = uniform[0] < p_latent[:, None]
    predecessor = (uniform[1] < np.where(latent, 1 - e10, e01)).astype(np.int8)
    reader = (uniform[2] < e01 + contrast * truth.reader * survive * latent).astype(np.int8)
    return list(predecessor), list(reader), [int(row.sum()) for row in predecessor]


def draw_replicate(setup: Setup, case: Case, seed: int, index: int) -> Drawn:
    """Replicate `index` of a case: the draws follow one fixed order whatever the arm, so the cases of an arm and the
    arms of a seed share their noise. Per qubit: a calibration resampled from the layout's, a rate shape log-uniform
    over the admitted shapes, the sx-error residual (common +0.011 and independent SD 0.0105), a uniform draw that
    picks the plateau arms' retained (T1, q) pair; then binomial member, equilibrium and pattern counts and the
    shot-ordered bits."""
    generator = replicate_generator(seed, index)
    width = len(setup.qubits)
    calibration = generator.integers(0, width, size=width)
    low, high = math.log(su.SHAPE_DOMAIN_SHAPES[0]), math.log(su.SHAPE_DOMAIN_SHAPES[-1])
    shapes = np.exp(low + (high - low) * generator.random(width))
    residuals = en.COMMON_RESIDUAL + en.INDEPENDENT_RESIDUAL_SD * generator.standard_normal(width)
    pairs = generator.random(width)
    out = Drawn(index, [], [], [], [], [], [], [])
    for slot in range(case.active):
        j, qubit = int(calibration[slot]), setup.qubits[slot]
        ctx = setup.contexts[j]
        truth = slot_truth(setup, case, j, slot, float(shapes[slot]), float(residuals[slot]), float(pairs[slot]))
        probabilities = member_probabilities(ctx, qubit, truth, setup.equilibrium_s)
        names = sorted(name for name in probabilities if name != de.msqr_equilibrium_member(qubit))
        ones = generator.binomial(SHOTS, [probabilities[name] for name in names])
        eq = int(generator.binomial(SHOTS, probabilities[de.msqr_equilibrium_member(qubit)]))
        patterns = generator.binomial(
            SHOTS, [1 - ctx["e10"] if row[slot] else ctx["e01"] for row in setup.pattern_bits]
        )
        predecessors, readers, predecessor_ones = draw_bits(generator, ctx, truth, probabilities, qubit)
        counts = {name: (int(k), SHOTS) for name, k in zip(names, ones, strict=True)}
        for i, k in enumerate(predecessor_ones):
            counts[predecessor_name(i, qubit)] = (k, SHOTS)
        out.calibration.append(j)
        out.truths.append(truth)
        out.counts.append({"final": counts})
        out.equilibrium.append((eq, SHOTS))
        out.patterns.append([(int(k), SHOTS) for k in patterns])
        out.predecessors.append(predecessors)
        out.readers.append(readers)
    return out


# --- carryover allocation and equilibrium estimate on a replicate axis ---------------------------------------


def departure_inputs(qubit: int, final: dict[str, Any]) -> tuple[list[str], list[float], list[float]]:
    """The keys, observations and series weights su._departure builds from the counts of one qubit."""
    obs = msa.observations({name: tuple(value) for name, value in final.items()}, qubit)
    keys = [*obs, "sx_shift", "window_fraction"]
    x = [*(k / n for k, n in obs.values()), 0.0, msa.WINDOW_RELAX_FRACTION]
    index = {key: i for i, key in enumerate(keys)}
    scale = x[index["t1-0"]] - x[index["ro0"]]
    if not scale >= msa.READOUT_CONTRAST_FLOOR:
        raise msa.AnalysisError(f"readout scale {scale:.4f} lies below the {msa.READOUT_CONTRAST_FLOOR} floor")
    weights = su.series_weights(scale, [msa.var(*obs[f"t1-{k}"]) for k in range(msa.T1_COUNT)])
    return keys, x, weights


def departures(
    requests: Sequence[tuple[int, int, dict[str, Any]]], contexts: Sequence[dict[str, Any]], memo: FitMemo
) -> list[float]:
    """su._departure of every (calibration index, qubit, counts) request: the N = 16 measure residual from the
    counts alone. Requests of one calibration share one pass of quantities_rows, and every series of every
    calibration is fitted in one call."""
    grouped: dict[int, list[int]] = {}
    built = []
    for position, (j, qubit, final) in enumerate(requests):
        grouped.setdefault(j, []).append(position)
        built.append(departure_inputs(qubit, final))
    arrays = {}
    for j, positions in grouped.items():
        keys = built[positions[0]][0]
        x = np.array([built[p][1] for p in positions])
        weights = np.array([built[p][2] for p in positions])
        arrays[j] = ({key: np.ascontiguousarray(x[:, i]) for i, key in enumerate(keys)}, weights)
    if arrays:
        memo.ensure(
            np.concatenate([corrected_series(p) for p, _ in arrays.values()]),
            np.concatenate([w for _, w in arrays.values()]),
        )
    out = [0.0] * len(requests)
    for j, positions in grouped.items():
        p, weights = arrays[j]
        values, _ = quantities_rows(p, contexts[j], weights, memo)
        for k, position in enumerate(positions):
            out[position] = float(values[f"diff:measure-{msa.TOP_STEPS}"][k])
    return out


def planted_counts(
    final: dict[str, Any], names: Sequence[str], excitation: float, base: dict[str, Any], probed: dict[str, Any]
) -> dict[str, Any]:
    """su.carryover_allocation's `planted`: the named members move by the model's response to `excitation`."""
    out = dict(final)
    for name in names:
        ones, shots = final[name]
        key = f"{name.rpartition('_q')[0]}_q0"
        moved = (probed[key][0] - base[key][0]) / su.VERTEX_SHOTS * (excitation / su.VERTEX_PROBE)
        out[name] = (ones + moved * shots, shots)
    return out


def allocations(
    items: Sequence[tuple[int, int, dict[str, Any], float]], setup: Setup, memo: FitMemo
) -> list[dict[str, Any]]:
    """su.carryover_allocation of every (calibration index, qubit, member counts, bound U) item, in two batched
    rounds: the reference and the single-class probes, then the two vertices."""
    classes = [su._class_members(qubit) for _, qubit, _, _ in items]
    first: list[tuple[int, int, dict[str, Any]]] = []
    for (j, qubit, counts, _), table in zip(items, classes, strict=True):
        final = counts["final"]
        first.append((j, qubit, final))
        first.extend(
            (j, qubit, planted_counts(final, names, su.VERTEX_PROBE, setup.vertex_base[j], setup.vertex_probed[j]))
            for names in table.values()
        )
    values = departures(first, setup.contexts, memo)
    cursor = 0
    vertices = []
    for table in classes:
        reference = values[cursor]
        response = {label: (values[cursor + 1 + k] - reference) / su.VERTEX_PROBE for k, label in enumerate(table)}
        cursor += 1 + len(table)
        vertices.append(
            (
                reference,
                response,
                {
                    "positive": [n for label, names in table.items() if response[label] > 0 for n in names],
                    "negative": [n for label, names in table.items() if response[label] < 0 for n in names],
                },
            )
        )
    second: list[tuple[int, int, dict[str, Any]]] = []
    for (j, qubit, counts, bound), (_, _, sides) in zip(items, vertices, strict=True):
        for side in ("positive", "negative"):
            if sides[side]:
                second.append(
                    (
                        j,
                        qubit,
                        planted_counts(
                            counts["final"], sides[side], bound, setup.vertex_base[j], setup.vertex_probed[j]
                        ),
                    )
                )
    planted_values = iter(departures(second, setup.contexts, memo))
    out = []
    for (_, _, _, bound), table, (reference, response, sides) in zip(items, classes, vertices, strict=True):
        shifts = {side: next(planted_values) - reference if sides[side] else 0.0 for side in ("positive", "negative")}
        out.append(
            {
                "allocation": max(abs(v) for v in shifts.values()) / bound,
                "bound": bound,
                "shifts": shifts,
                "positive_classes": sorted(label for label in table if response[label] > 0),
                "negative_classes": sorted(label for label in table if response[label] < 0),
            }
        )
    return out


def carryover_rows(
    items: Sequence[tuple[Any, ...]], setup: Setup, memo: FitMemo, index_of: dict[int, int]
) -> list[dict[str, Any]]:
    """su.carryover_screen of every item (qubit, counts, planned context, predecessor bits, reader bits, readout
    scale, width): the reader statistic, the vertex allocation at its bound, then the screen."""
    firsts = [su.carryover_reader(item[3], item[4], item[5], 1.0, item[6]) for item in items]
    todo = [k for k, first in enumerate(firsts) if first["evaluable"]]
    vertex = allocations(
        [(index_of[id(items[k][2])], items[k][0], items[k][1], firsts[k]["upper_bound"]) for k in todo], setup, memo
    )
    out: list[dict[str, Any]] = list(firsts)
    for k, found in zip(todo, vertex, strict=True):
        item = items[k]
        screened = su.carryover_reader(item[3], item[4], item[5], found["allocation"], item[6])
        screened["vertex"] = found
        out[k] = screened
    return out


def equilibrium_rows(
    items: Sequence[tuple[Any, ...]], memo: FitMemo, index_of: dict[int, int], contexts: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    """su.equilibrium_screen of every item (observations incl. "eq", planned context, fitted T, idle, width): the
    q estimate with its delta-method standard error through the batched gamma-rate fit, then the withhold rule."""
    keys = ["ro0", *(f"t1-{k}" for k in range(msa.T1_COUNT)), "eq"]
    out: list[dict[str, Any] | None] = [None] * len(items)
    grouped: dict[int, list[int]] = {}
    prepared: dict[int, tuple[list[float], list[float], list[float]]] = {}
    for position, (obs, ctx, _, _, _) in enumerate(items):
        x = [obs[k][0] / obs[k][1] for k in keys]
        variances = [msa.var(*obs[k]) for k in keys]
        scale = x[1] - x[0]
        if not scale >= msa.READOUT_CONTRAST_FLOOR:
            out[position] = {
                "passes": False,
                "reason": f"readout scale {scale:.4f} lies below the {msa.READOUT_CONTRAST_FLOOR} floor",
            }
            continue
        weights = su.series_weights(scale, [variances[1 + k] for k in range(msa.T1_COUNT)])
        prepared[position] = (x, variances, weights)
        grouped.setdefault(index_of[id(ctx)], []).append(position)
    points = {}
    for j, positions in grouped.items():
        xs = np.array([prepared[p][0] for p in positions])
        flat, spans = perturbed_points(xs)
        p = {key: np.ascontiguousarray(flat[:, i]) for i, key in enumerate(keys)}
        tiled = np.tile(np.array([prepared[p_][2] for p_ in positions]), (1 + 2 * len(keys), 1))
        points[j] = (p, spans, tiled)
    if points:
        memo.ensure(
            np.concatenate([corrected_series(p) for p, _, _ in points.values()]),
            np.concatenate([w for _, _, w in points.values()]),
        )
    for j, positions in grouped.items():
        p, spans, tiled = points[j]
        fit = memo.fit(corrected_series(p), tiled)
        z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
        s, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2
        k = np.where(np.isinf(fit.shape), 1.0, fit.shape)
        delay = items[positions[0]][3]
        decay = np.where(np.isinf(fit.shape), np.exp(-delay / fit.t_s), (1 + delay / (k * fit.t_s)) ** (-k))
        excitation = (1 - ((1 - 2 * p["eq"]) - offset) / s) / 2
        q_hat = 1 - 2 * excitation / (1 - decay)
        count = len(positions)
        table = {
            "q_hat": q_hat.reshape(1 + 2 * len(keys), count),
            "excitation": excitation.reshape(1 + 2 * len(keys), count),
            "t1_s": fit.t_s.reshape(1 + 2 * len(keys), count),
        }
        spread = np.array([prepared[p_][1] for p_ in positions])
        totals = {name: np.zeros(count) for name in table}
        for i in range(len(keys)):
            for name, values in table.items():
                change = (values[1 + 2 * i] - values[2 + 2 * i]) / (2 * spans[i])
                totals[name] = totals[name] + en.square_rows(change) * spread[:, i]
        for c, position in enumerate(positions):
            _, ctx, fitted_t, delay_s, width = items[position]
            estimate = {
                "q_hat": float(table["q_hat"][0, c]),
                "se": math.sqrt(float(totals["q_hat"][c])),
                "excitation": float(table["excitation"][0, c]),
                "excitation_se": math.sqrt(float(totals["excitation"][c])),
                "t1_s": float(table["t1_s"][0, c]),
                "delay_s": delay_s,
            }
            out[position] = {**estimate, **su.q_screen(estimate, su.q_sensitivity(ctx, fitted_t), width)}
    return [row for row in out if row is not None]


# --- one block of replicates ---------------------------------------------------------------------------------


class State:
    """One replicate's inputs to the post-order pipeline and its figures as the block computes them."""

    def __init__(self, setup: Setup, case: Case, drawn: Drawn) -> None:
        self.drawn = drawn
        slots = range(case.active)
        self.slots = list(slots)
        self.qubits = [setup.qubits[s] for s in slots]
        self.planned = {setup.qubits[s]: setup.contexts[drawn.calibration[s]] for s in slots}
        self.counts = {setup.qubits[s]: drawn.counts[s] for s in slots}
        self.screens: dict[str, dict[str, Any]] = {}
        self.passing: list[int] = []
        for s in slots:
            qubit = setup.qubits[s]
            patterns = ea.pattern_screen([row[s] for row in setup.pattern_bits], drawn.patterns[s], setup.width)
            self.screens[str(qubit)] = {
                "execution_eligibility": None,
                "patterns": patterns,
                "carryover": None,
                "equilibrium": None,
            }
            if patterns["passes"]:
                self.passing.append(qubit)
        self.rows: dict[int, dict[str, Any]] = {}
        self.work: list[int] = []


def select_replicate(setup: Setup, state: State, carryover: Any, equilibrium: Any, bounds: Any) -> dict[str, Any]:
    slot_of = {setup.qubits[s]: s for s in state.slots}
    drawn = state.drawn
    return su.select_and_decide(
        state.qubits,
        setup.width,
        state.rows,
        state.planned,
        state.counts,
        state.screens,
        state.work,
        {q: drawn.predecessors[slot_of[q]] for q in state.work},
        {q: drawn.readers[slot_of[q]] for q in state.work},
        {q: drawn.equilibrium[slot_of[q]] for q in state.work},
        setup.equilibrium_s,
        carryover=carryover,
        equilibrium=equilibrium,
        bounds=bounds,
    )


def summarize(setup: Setup, case: Case, state: State, selection: dict[str, Any]) -> dict[str, Any]:
    """The replicate's record row: whether a verdict was issued, which device verdicts fired and the figures the
    arm's targets read, all integers and booleans. A minority arm's verdict counts toward its requirement only when
    it selects a planted qubit."""
    decision = selection["decision"]
    verdict = decision["device"]
    issued = verdict is not None and verdict["status"] == "informative"
    fired = sorted(name for name, flag in msa.device_flags(verdict).items() if flag) if verdict is not None else []
    veto = decision["settle_veto"]
    withheld_qubits = set(veto.get("withheld_qubits", []))
    planted = [setup.qubits[s] for s in range(planted_count(case.arm, case.active))]
    screens = state.screens
    planted_selected = sum(1 for q in planted if q in decision["selected"])
    return {
        "i": state.drawn.replicate,
        "issued": issued,
        "fired": fired if issued else [],
        "work": len(state.work),
        "carryover_failed": sum(1 for q in state.work if not screens[str(q)]["carryover"]["passes"]),
        "equilibrium_failed": sum(1 for q in state.work if not screens[str(q)]["equilibrium"]["passes"]),
        "eligible": len(selection["eligible"]),
        "pool": len(decision["pool"]),
        "selected": len(decision["selected"]),
        "common_veto": bool(veto.get("common_veto", False)),
        "planted_in_pool": sum(1 for q in planted if q in decision["pool"]),
        "planted_withheld": sum(1 for q in planted if q in withheld_qubits),
        "planted_equilibrium_failed": sum(
            1 for q in planted if q in state.work and not screens[str(q)]["equilibrium"]["passes"]
        ),
        "planted_selected": planted_selected,
        "counted": issued and (planted_selected > 0 or case.arm not in MINORITY_ARMS),
    }


def analyse_block(item: tuple[Setup, Case, int, list[int]]) -> list[dict[str, Any]]:
    """The record row of every replicate index of a block in one case, from batched evaluations."""
    return [row for row, _, _ in analyse_detail(item)]


def analyse_detail(
    item: tuple[Setup, Case, int, list[int]],
) -> list[tuple[dict[str, Any], dict[str, Any], State]]:
    """analyse_block with each replicate's selection (screens, decision) and state."""
    setup, case, seed, indices = item
    memo = FitMemo(setup.contexts[0]["t1_delays_s"])
    index_of = {id(c): j for j, c in enumerate(setup.contexts)}
    states = [State(setup, case, draw_replicate(setup, case, seed, i)) for i in indices]
    # Rows of every active qubit, one batch per calibration.
    groups: dict[int, list[tuple[int, int]]] = {}
    for r, state in enumerate(states):
        for s in state.slots:
            groups.setdefault(state.drawn.calibration[s], []).append((r, s))
    batches = {}
    for j, members in groups.items():
        qubits = [setup.qubits[s] for _, s in members]
        batches[j] = prepare_batch(qubits, setup.contexts[j], [states[r].drawn.counts[s] for r, s in members])
    ensure_many(list(batches.values()), memo)
    done: dict[tuple[int, int], dict[str, Any]] = {}
    for j, members in groups.items():
        qubits = [setup.qubits[s] for _, s in members]
        rows = evaluate_rows(
            qubits, setup.contexts[j], [states[r].drawn.counts[s] for r, s in members], memo, batches[j]
        )
        done.update(zip(members, rows, strict=True))
    for r, state in enumerate(states):
        state.rows = su.finish_rows({setup.qubits[s]: done[(r, s)] for s in state.slots}, state.planned, setup.width)
        state.work = [q for q in state.passing if state.rows[q]["usable"]]
    # Pass 1 records the carryover and equilibrium items; pass 2 the shape-bound requests; pass 3 is final.
    recorded: list[dict[str, list[Any]]] = [{"carryover": [], "equilibrium": []} for _ in states]

    def recorder(r: int, kind: str) -> Any:
        def record(items: list[Any]) -> list[dict[str, Any]]:
            recorded[r][kind] = items
            return [{"passes": True}] * len(items)

        return record

    for r, state in enumerate(states):
        select_replicate(
            setup,
            state,
            recorder(r, "carryover"),
            recorder(r, "equilibrium"),
            lambda rows, planned: dict.fromkeys(rows, 0.0),
        )
    carry_items = [(r, it) for r in range(len(states)) for it in recorded[r]["carryover"]]
    eq_items = [(r, it) for r in range(len(states)) for it in recorded[r]["equilibrium"]]
    carry_out = carryover_rows([it for _, it in carry_items], setup, memo, index_of)
    eq_out = equilibrium_rows([it for _, it in eq_items], memo, index_of, setup.contexts)
    carry_by: list[list[dict[str, Any]]] = [[] for _ in states]
    eq_by: list[list[dict[str, Any]]] = [[] for _ in states]
    for (r, _), outcome in zip(carry_items, carry_out, strict=True):
        carry_by[r].append(outcome)
    for (r, _), outcome in zip(eq_items, eq_out, strict=True):
        eq_by[r].append(outcome)
    requests: list[tuple[int, int, float, int]] = []

    def bounds_recorder(r: int) -> Any:
        def record(rows: dict[int, dict[str, Any]], planned: dict[int, dict[str, Any]]) -> dict[Any, float]:
            requests.extend((r, q, float(row["fitted"]["t1_s"]), index_of[id(planned[q])]) for q, row in rows.items())
            return dict.fromkeys(rows, 0.0)

        return record

    for r, state in enumerate(states):
        select_replicate(setup, state, lambda items, r=r: carry_by[r], lambda items, r=r: eq_by[r], bounds_recorder(r))
    shape_by: dict[tuple[int, int], float] = {}
    by_calibration: dict[int, list[tuple[int, int, float]]] = {}
    for r, q, t_s, j in requests:
        by_calibration.setdefault(j, []).append((r, q, t_s))
    for j, found in by_calibration.items():
        values = shape_bound_rows(setup.contexts[j], np.array([t for _, _, t in found]))
        for (r, q, _), value in zip(found, values.tolist(), strict=True):
            shape_by[(r, q)] = value
    out = []
    for r, state in enumerate(states):
        selection = select_replicate(
            setup,
            state,
            lambda items, r=r: carry_by[r],
            lambda items, r=r: eq_by[r],
            lambda rows, planned, r=r: {q: shape_by[(r, q)] for q in rows},
        )
        out.append((summarize(setup, case, state, selection), selection, state))
    return out


def reference_replicate(
    setup: Setup, case: Case, seed: int, index: int
) -> tuple[dict[str, Any], dict[str, Any], State]:
    """One replicate through the scalar functions of msq_successor_analysis: the reference the block must equal."""
    state = State(setup, case, draw_replicate(setup, case, seed, index))
    rows = {q: su._evaluate((q, state.counts[q], state.planned[q]), False) for q in state.qubits}
    state.rows = su.finish_rows(rows, state.planned, setup.width)
    state.work = [q for q in state.passing if state.rows[q]["usable"]]
    selection = select_replicate(setup, state, su.map_carryover, su.map_equilibrium, su.shape_bounds)
    return summarize(setup, case, state, selection), selection, state


def ensure_many(batches: Sequence[Batch], memo: FitMemo) -> None:
    """Fit every series the perturbation points of all batches hold, in one call."""
    series, weights = [], []
    for batch in batches:
        if not batch.usable:
            continue
        flat, _ = perturbed_points(batch.x)
        keys = batch.prepared[0].keys
        p = {key: np.ascontiguousarray(flat[:, j]) for j, key in enumerate(keys)}
        series.append(corrected_series(p))
        weights.append(np.tile(batch.weights, (1 + 2 * batch.x.shape[1], 1)))
    if series:
        memo.ensure(np.concatenate(series), np.concatenate(weights))


# --- arms, shards and the record -----------------------------------------------------------------------------

# Replicates per round of an unsharded run that stops at its verdict count.
ROUND = 4 * NULL_BLOCK


def upper_bound(fires: int, replicates: int, confidence: float = CONFIDENCE) -> float:
    """The one-sided Clopper-Pearson upper confidence bound on a binomial rate."""
    if fires >= replicates:
        return 1.0
    return float(beta.ppf(confidence, fires + 1, replicates - fires))


def run_arm(
    setup: Setup,
    arm: str,
    seed: int,
    cap: int,
    shard: int = 0,
    shards: int = 1,
    seed_source: Any = None,
    record_name: str = "",
    cases: Sequence[Case] | None = None,
    needed: int | None = None,
) -> dict[str, Any]:
    """The rows of replicates 0 to cap - 1 whose index is congruent to `shard` modulo `shards`, for every case of the
    arm, as a shard record. An unsharded run of an arm with a verdict requirement stops after the round that reaches
    it in counted verdicts; `merge_records` applies the same cut to every record, so the bytes do not depend on the
    sharding."""
    if not 0 <= shard < shards or cap < 1:
        raise ValueError(f"shard {shard} of {shards} with {cap} replicates")
    cases = list(arm_cases(arm, setup.width) if cases is None else cases)
    needed = minimum_verdicts(arm) if needed is None else needed
    indices = [i for i in range(cap) if i % shards == shard]
    rows: dict[str, list[dict[str, Any]]] = {case.label: [] for case in cases}
    rounds = [indices] if shards > 1 or not needed else [indices[k : k + ROUND] for k in range(0, len(indices), ROUND)]
    for chunk in rounds:
        items = [
            (setup, case, seed, chunk[k : k + NULL_BLOCK]) for case in cases for k in range(0, len(chunk), NULL_BLOCK)
        ]
        for (_, case, _, _), block in zip(items, ordered_map(analyse_block, items, min_items=2), strict=True):
            rows[case.label].extend(block)
        if needed and sum(row["counted"] for row in rows[cases[0].label]) >= needed:
            break
    return {
        "schema": SCHEMA,
        "arm": arm,
        "seed": seed,
        "seed_source": seed_source,
        "record": record_name,
        "layout_width": setup.width,
        "snapshot_sha256": setup.digests["snapshot_sha256"],
        "plateau_sha256": setup.digests["plateau_sha256"],
        "sparse_scale": {str(pool): factor for pool, factor in sorted(setup.sparse_scale.items())},
        "sparse_scale_sha256": setup.digests["sparse_scale_sha256"],
        "cap": cap,
        "minimum_verdicts": needed,
        "shard": {"index": shard, "count": shards},
        "cases": {label: {"rows": sorted(found, key=lambda row: row["i"])} for label, found in rows.items()},
    }


IDENTITY = (
    "schema",
    "arm",
    "seed",
    "seed_source",
    "record",
    "layout_width",
    "snapshot_sha256",
    "plateau_sha256",
    "sparse_scale",
    "sparse_scale_sha256",
    "cap",
    "minimum_verdicts",
)


def case_statistics(arm: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts, rates and the one-sided 95 % bounds of one case's rows, with the arm's targets as booleans (the
    targets judge a full run; a short run reports them as measured)."""
    n = len(rows)
    issued = sum(1 for row in rows if row["issued"])
    fires = sum(1 for row in rows if row["fired"])
    work = sum(row["work"] for row in rows)
    unconditional = upper_bound(fires, n) if n else 1.0
    conditional = upper_bound(fires, issued) if issued else 1.0
    planted = sum(row["planted_in_pool"] for row in rows)
    sparse = sum(row["planted_withheld"] for row in rows)
    both = sum(1 for row in rows if row["planted_in_pool"] == PLANTED_QUBITS)
    both_withheld = sum(1 for row in rows if row["planted_withheld"] == PLANTED_QUBITS)
    planted_total = n * PLANTED_QUBITS if arm in ("settle-sparse", *MINORITY_ARMS) else 0
    exposed = [row for row in rows if row["issued"] and row["planted_selected"] > 0]
    exposed_fires = sum(1 for row in exposed if row["fired"])
    stats: dict[str, Any] = {
        "replicates": n,
        "issued": issued,
        "fires": fires,
        "fired_verdicts": {
            name: sum(1 for row in rows if name in row["fired"])
            for name in sorted({x for r in rows for x in r["fired"]})
        },
        "false_fire_rate": fires / n if n else None,
        "false_fire_upper_95": unconditional,
        "false_fire_rate_given_issued": fires / issued if issued else None,
        "false_fire_upper_95_given_issued": conditional,
        "informative_device_rate": issued / n if n else None,
        "mean_selected": sum(row["selected"] for row in rows) / n if n else None,
        "selection_failure_rate": sum(row["carryover_failed"] for row in rows) / work if work else None,
        "equilibrium_failure_rate": sum(row["equilibrium_failed"] for row in rows) / work if work else None,
        "common_veto_rate": sum(1 for row in rows if row["common_veto"]) / n if n else None,
        "sparse_gap_withheld_rate": sparse / planted if planted else None,
        "sparse_gap_both_withheld_rate": both_withheld / both if both else None,
        "planted_in_pool": planted,
        "planted_withheld": sparse,
        "per_qubit_veto_power_upper_95": upper_bound(sparse, planted) if planted else None,
        "per_qubit_veto_power_upper_family": upper_bound(sparse, planted, SPARSE_FAMILY_CONFIDENCE)
        if planted
        else None,
        "planted_equilibrium_withheld_rate": (
            sum(row["planted_equilibrium_failed"] for row in rows) / planted_total if planted_total else None
        ),
        "planted_selected_rate": sum(row["planted_selected"] for row in rows) / planted_total
        if planted_total
        else None,
        "exposed": len(exposed),
        "exposed_fires": exposed_fires,
        "false_fire_upper_95_given_exposed": upper_bound(exposed_fires, len(exposed)) if exposed else 1.0,
    }
    targets: dict[str, bool] = {}
    if arm in ("carryover-positive", "carryover-negative", "plateau-retained"):
        targets = {
            "verdicts_at_least_299": issued >= CARRYOVER_VERDICTS,
            "false_fire_bound_given_issued_below_ceiling": conditional < FALSE_FIRE_CEILING,
            "false_fire_bound_below_ceiling": unconditional < FALSE_FIRE_CEILING,
        }
    elif arm in MINORITY_ARMS:
        targets = {
            "exposed_verdicts_at_least_299": len(exposed) >= CARRYOVER_VERDICTS,
            "false_fire_bound_given_exposed_below_ceiling": stats["false_fire_upper_95_given_exposed"]
            < FALSE_FIRE_CEILING,
            "false_fire_bound_below_ceiling": unconditional < FALSE_FIRE_CEILING,
        }
    elif arm in ("settle-common", "q-tolerance"):
        targets = {"common_veto_power_at_least_90_percent": n > 0 and stats["common_veto_rate"] >= 0.9}
        if arm == "q-tolerance":
            targets["false_fire_bound_below_ceiling"] = unconditional < FALSE_FIRE_CEILING
    elif arm == "settle-sparse":
        # One-sided: the arm fails when any pool's per-qubit power is shown below SPARSE_TARGET_POWER at the family's
        # 95 %.
        targets = {
            "per_qubit_veto_power_not_below_90_percent_family": planted > 0
            and stats["per_qubit_veto_power_upper_family"] >= SPARSE_TARGET_POWER,
            "false_fire_bound_below_ceiling": unconditional < FALSE_FIRE_CEILING,
        }
    elif arm == "plateau-low":
        targets = {"departure_verdict_withheld": issued == 0}
    elif arm == "gamma":
        targets = {"informative_rate_at_least_80_percent": n > 0 and issued >= ISSUANCE_FLOOR * n}
    stats["targets"] = targets
    return stats


def merge_records(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The arm's record from its shard records (one record is an unsharded run): rows in replicate order, the cut at
    the verdict requirement, then the statistics."""
    if not records:
        raise ValueError("no records to merge")
    first = records[0]
    for record in records:
        if any(record[key] != first[key] for key in IDENTITY):
            raise ValueError("shard records disagree on the arm, seed, snapshot or replicate cap")
    count = first["shard"]["count"]
    found = sorted(record["shard"]["index"] for record in records)
    if any(record["shard"]["count"] != count for record in records) or found != list(range(count)):
        raise ValueError(f"shard indices {found} do not cover {count} shards exactly once")
    arm, needed = first["arm"], first["minimum_verdicts"]
    cases: dict[str, Any] = {}
    for label in first["cases"]:
        rows = sorted((row for record in records for row in record["cases"][label]["rows"]), key=lambda r: r["i"])
        if [row["i"] for row in rows] != list(range(len(rows))):
            raise ValueError(f"case {label}: the replicate indices are not a prefix of 0 to cap - 1")
        if needed:
            total = 0
            for k, row in enumerate(rows):
                total += int(row["counted"])
                if total >= needed:
                    rows = rows[: k + 1]
                    break
        cases[label] = {"rows": rows, **case_statistics(arm, rows)}
    out = {key: first[key] for key in IDENTITY}
    out["cases"] = cases
    out["replicates"] = {label: len(case["rows"]) for label, case in cases.items()}
    return out


def sparse_power(setup: Setup, pool: int, scale: float, seed: int, replicates: int) -> tuple[int, int]:
    """(planted gaps the per-qubit veto withheld, planted gaps in the pool) of the sparse arm at `pool` qubits with
    the planted gap at `scale` times `sparse_gap`."""
    trial = with_sparse_scale(setup, {pool: scale})
    case = Case("settle-sparse", f"{pool}-qubits", pool, 0.0)
    stats = merge_records([run_arm(trial, "settle-sparse", seed, replicates, cases=[case])])["cases"][case.label]
    return int(stats["planted_withheld"]), int(stats["planted_in_pool"])


def calibrate_sparse_scale(setup: Setup, pool: int, seed: int, replicates: int) -> dict[str, Any]:
    """The scale of `sparse_gap` at which the per-qubit settle veto withholds SPARSE_TARGET_POWER of the planted gaps
    at `pool` qubits, measured on `seed`, which differs from the null's. The scale starts at 1 and
    SPARSE_CALIBRATION_STEP, then steps along the secant through the two points that bracket the target (the two
    latest before a bracket exists), and ends at the first point within one binomial standard error of the target.
    A planted loss changes how many uniforms the binomial draws take, so the power is a noisy step function of the
    scale and each point runs `replicates` replicates."""
    if seed == SUCCESSOR_NULL_SEED:
        raise ValueError("the sparse calibration draws from the null's own seed")
    points: list[dict[str, float]] = []
    scale = 1.0
    for step in range(SPARSE_CALIBRATION_STEPS):
        withheld, planted = sparse_power(setup, pool, scale, seed, replicates)
        if planted == 0:
            raise ValueError(f"pool {pool}: no planted gap reached the pool at scale {scale}")
        power = withheld / planted
        se = math.sqrt(max(power * (1 - power), 1.0 / planted) / planted)
        points.append({"scale": scale, "withheld": withheld, "planted": planted, "power": power, "se": se})
        if abs(power - SPARSE_TARGET_POWER) <= se:
            return {"scale": scale, "gap": scale * sparse_gap(setup.settle_se, pool), "points": points}
        if step == 0:
            scale = SPARSE_CALIBRATION_STEP
            continue
        below = [p for p in points if p["power"] < SPARSE_TARGET_POWER]
        above = [p for p in points if p["power"] > SPARSE_TARGET_POWER]
        if below and above:
            a = max(below, key=lambda p: p["power"])
            b = min(above, key=lambda p: p["power"])
        else:
            a, b = points[-2], points[-1]
        if (b["power"] - a["power"]) * (b["scale"] - a["scale"]) <= 0:
            raise ValueError(f"pool {pool}: the measured power does not rise with the scale: {points}")
        scale = a["scale"] + (SPARSE_TARGET_POWER - a["power"]) * (b["scale"] - a["scale"]) / (b["power"] - a["power"])
    raise ValueError(f"pool {pool}: no scale within one standard error after {SPARSE_CALIBRATION_STEPS} points")


def sparse_calibration_record(
    setup: Setup, seed: int, seed_source: Any, record_name: str, replicates: int = SPARSE_CALIBRATION_REPLICATES
) -> dict[str, Any]:
    """The measured scale of every pool size the sparse arm runs at the setup's layout width, as the record
    SPARSE_SCALE_EVIDENCE holds."""
    pools = sorted({m or setup.width for m in SETTLE_POOLS})
    return {
        "schema": "msq-successor-sparse-scale-v1",
        "record": record_name,
        "snapshot_sha256": setup.digests["snapshot_sha256"],
        "layout_width": setup.width,
        "seed": seed,
        "seed_source": seed_source,
        "replicates": replicates,
        "target_power": SPARSE_TARGET_POWER,
        "settle_se": setup.settle_se,
        "pools": {
            str(pool): {"formula_gap": sparse_gap(setup.settle_se, pool)}
            | calibrate_sparse_scale(setup, pool, seed, replicates)
            for pool in pools
        },
    }


def dumps(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"
