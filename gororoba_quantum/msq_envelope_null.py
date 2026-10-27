"""Preregistered stochastic null of the measurement-sequence envelope's complete decision pipeline.

Each replicate is a device with no pinching departure (eps = 0, no readout history) whose qubits carry a gate-model
error: an sx error scaled so the unitary N = 16 residual is a common +0.011 plus an independent normal part of SD
0.0105 (the 250 us diagnostic's mean and spread, docs/evidence/measurement_sequence/scatter-floor.json). Every member,
reset control and pattern draws binomial shot noise; the reset and pattern screens, the informative filter, the
same-run rms floor and both directions of the pooled test and the count rule then run as on a collected record. A
replicate fires when any device verdict fires. The family-wise false-fire rate's one-sided 95 % Clopper-Pearson upper
bound must lie below FALSE_FIRE_CEILING.

`replicate` runs the scalar pipeline of one replicate and is the reference. `run` maps blocks of NULL_BLOCK
replicates through parallel.ordered_map; a block draws each replicate's counts with the scalar code and then
analyses the kept qubits of all its replicates together (`evaluate_batch`): per qubit, one array axis runs over the
replicates and the per-qubit fit of measurement_sequence_analysis.evaluate_qubit runs on it in numpy. Every
replicate-dependent value keeps the bits of the scalar code, so a replicate's rows and verdict equal the scalar ones
by `float.hex`:

- the unitary 4 x 4 products are stacked `@` and `np.linalg.matrix_power`, whose slices equal the single-matrix calls;
  the sx propagator comes from the scalar `sx_map` per distinct key, since a stacked `expm` differs in the last bits;
- the bounded Brent search of `fit_t1` and the `brentq` solves of `implied_loss` run as masked ports of SciPy
  1.18.1's `_minimize_scalar_bounded` and `brentq` (`minimize_rows`, `brentq_rows`): every branch is a per-row
  `np.where` whose arms are the scalar expressions, a finished row freezes, and only live rows reach the objective;
- `math.exp` and `math.pow` map over the arrays where the scalar code calls them on Python floats, `np.exp`,
  `** 2` and `np.sum` act on a C-contiguous (rows, 5) array where it applies them to a 5-vector, and
  `neumaier_rows` repeats builtin `sum()`;
- per-replicate tails (the gate-curve stops, `gate_propagation`, the rows of `evaluate_qubit` and the device
  verdict) run the scalar functions on the Python floats of the batched arrays.

Per-replicate generators are spawned up front from one QRNG seed, so serial, pooled and differently blocked runs
write the same bytes.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
import numpy.typing as npt
from scipy.stats import beta

import measurement_sequence_analysis as msa
import msq_envelope_analysis as ea
from diagnostic_experiments import MSQE_RESET_CONTROLS, msqe_pattern_bits
from parallel import ordered_map

SCHEMA = "msq-envelope-null-v1"
# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-26T220128Z.json, index 1.
NULL_SEED = 56182
COMMON_RESIDUAL = 0.011
INDEPENDENT_RESIDUAL_SD = 0.0105
FALSE_FIRE_CEILING = 0.01
CONFIDENCE = 0.95
SHOTS = 8192
# Replicates per mapped block; a block shares one batched evaluation per qubit.
NULL_BLOCK = 25

Floats = npt.NDArray[np.float64]
Ints = npt.NDArray[np.intp]
Gate = tuple[Any, float, Any, Any, Any]
Objective = Callable[[Floats, Ints], Floats]


def upper_bound(fires: int, replicates: int) -> float:
    """The one-sided Clopper-Pearson upper confidence bound on a binomial rate."""
    if fires >= replicates:
        return 1.0
    return float(beta.ppf(CONFIDENCE, fires + 1, replicates - fires))


def residual_slope(context: dict[str, Any]) -> float:
    """d(unitary residual) / d(sx error factor) of one qubit context, from the noise-free model at factors 1 and 3."""
    contexts = msa.with_planning({0: context}, msa.DEMONSTRATION_SCATTER_FLOOR)
    residuals = []
    for factor in (1.0, 3.0):
        model = msa.device_model(contexts[0], sx_error=factor * contexts[0]["sx_error"])
        row = msa.evaluate(msa.device_counts({0: model}, contexts, SHOTS), contexts)[0]
        residuals.append(float(row["gate_systematic_n16"]["unitary_residual"]))
    return (residuals[1] - residuals[0]) / 2.0


def null_contexts(width: int) -> dict[int, dict[str, Any]]:
    """width qubit contexts cycling the analysis fixture's eight distinct calibrations."""
    base = msa.fixture_contexts(tuple(range(len(msa.FIXTURE_SCALES))), None)
    return {q: dict(base[q % len(base)]) for q in range(width)}


def binomial(generator: np.random.Generator, ones: int, shots: int) -> tuple[int, int]:
    return int(generator.binomial(shots, min(max(ones / shots, 0.0), 1.0))), shots


# --- one replicate: the scalar reference ---------------------------------------------------------------------

Item = tuple[int, dict[int, dict[str, Any]], dict[int, float], float, np.random.SeedSequence]
Block = tuple[int, dict[int, dict[str, Any]], dict[int, float], float, list[np.random.SeedSequence]]


class Draw(NamedTuple):
    """The drawn counts of one replicate and its screens' outcome."""

    kept: list[int]
    counts: dict[int, dict[str, Any]]
    contexts: dict[int, dict[str, Any]]
    floor: float
    width: int


def draw(item: Item) -> Draw:
    """One null device's binomial counts through the reset and pattern screens."""
    width, contexts, slopes, floor, seed = item
    generator = np.random.default_rng(seed)
    residuals = COMMON_RESIDUAL + INDEPENDENT_RESIDUAL_SD * generator.standard_normal(width)
    models = {
        q: msa.device_model(ctx, sx_error=max(0.0, 1.0 + float(residuals[q]) / slopes[q]) * ctx["sx_error"])
        for q, ctx in contexts.items()
    }
    expected = msa.device_counts(models, contexts, SHOTS)
    counts = {
        q: {"final": {name: binomial(generator, k, n) for name, (k, n) in sorted(expected[q]["final"].items())}}
        for q in contexts
    }
    bits = msqe_pattern_bits(width)
    kept = []
    for q in contexts:
        p_ground = models[q]["e01"]
        controls = {c: binomial(generator, round(p_ground * SHOTS), SHOTS) for c in MSQE_RESET_CONTROLS}
        ro0 = counts[q]["final"][msa.ro0_name(q)]
        ro1 = counts[q]["final"][msa.t1_names(q)[0]]
        reset = ea.reset_screen(controls["rc1"], controls["rc0"], ro0, ro1, width)
        own = [row[q] for row in bits]
        ones = [
            binomial(generator, round((p_ground if b == 0 else 1.0 - models[q]["e10"]) * SHOTS), SHOTS) for b in own
        ]
        if reset["passes"] and ea.pattern_screen(own, ones, width)["passes"]:
            kept.append(q)
    return Draw(kept, counts, contexts, floor, width)


def planned_contexts(drawn: Draw) -> dict[int, dict[str, Any]]:
    return msa.with_planning({q: drawn.contexts[q] for q in drawn.kept}, drawn.floor)


def summarize(drawn: Draw, rows: dict[int, dict[str, Any]] | None) -> tuple[dict, dict[str, Any] | None]:
    """The replicate's record row and its device verdict, from the evaluated rows of the kept qubits."""
    if rows is None:
        return {"kept": len(drawn.kept), "fired": [], "withheld": True}, None
    verdict = msa.device_verdict(rows, ea.count_rule(drawn.width))
    fired = sorted(name for name, flag in msa.device_flags(verdict).items() if flag)
    return {"kept": len(drawn.kept), "fired": fired, "withheld": False}, verdict


def replicate_detail(item: Item) -> tuple[dict, dict[int, dict[str, Any]] | None, dict[str, Any] | None]:
    """The scalar pipeline of one replicate: its record row, per-qubit rows and device verdict."""
    drawn = draw(item)
    if len(drawn.kept) < ea.MIN_KEPT:
        return summarize(drawn, None)[0], None, None
    planned = planned_contexts(drawn)
    rows = msa.evaluate({q: drawn.counts[q] for q in drawn.kept}, planned)
    row, verdict = summarize(drawn, rows)
    return row, rows, verdict


def replicate(item: Item) -> dict:
    """One null device through the screens and the pinching analysis; which device verdicts fired."""
    return replicate_detail(item)[0]


# --- libm and compensated-sum maps ---------------------------------------------------------------------------


def libm_map(function: Callable[..., float], values: Floats, *extra: float) -> Floats:
    """function(value, *extra) for every element through the math module, the libm calls of the scalar code."""
    flat = values.ravel().tolist()
    mapped = map(function, flat, *(itertools.repeat(x) for x in extra), strict=False)
    return np.fromiter(mapped, np.float64, len(flat)).reshape(values.shape)


def exp_rows(values: Floats) -> Floats:
    return libm_map(math.exp, values)


def square_rows(values: Floats) -> Floats:
    """x ** 2 of a Python float, which CPython evaluates as libm pow(x, 2.0); numpy's x ** 2 is x * x."""
    return libm_map(math.pow, values, 2.0)


def neumaier_rows(terms: list[Floats]) -> Floats:
    """sum(terms) elementwise as builtin sum() evaluates it: 0 + the first term, then CPython's Neumaier update."""
    total = 0.0 + terms[0]
    comp = np.zeros_like(total)
    for term in terms[1:]:
        step = total + term
        comp = comp + np.where(np.abs(total) >= np.abs(term), (total - step) + term, (term - step) + total)
        total = step
    return np.where((comp != 0) & np.isfinite(comp), total + comp, total)


def take(value: Any, rows: Ints) -> Any:
    """value[rows] for a per-row array and the value itself for a shared scalar."""
    return value if np.ndim(value) == 0 else value[rows]


# --- masked ports of SciPy's scalar solvers ------------------------------------------------------------------


class SolverTrace:
    """Counts of the branches the batched solvers took; the solver tests require every branch to occur."""

    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    def add(self, name: str, mask: npt.NDArray[np.bool_]) -> None:
        self.counts[name] = self.counts.get(name, 0) + int(mask.sum())


def minimize_rows(
    func: Objective, count: int, lower: float, upper: float, xatol: float, trace: SolverTrace | None = None
) -> Floats:
    """The minimizer of every row from SciPy 1.18.1 `_minimize_scalar_bounded` (maxiter 500), step for step.

    func(x, rows) returns the objective of the rows `rows` at the points x. A row leaves the loop when its own
    convergence test fails, and func sees live rows only.
    """
    sqrt_eps = math.sqrt(2.2e-16)
    golden_mean = 0.5 * (3.0 - math.sqrt(5.0))
    maxiter = 500
    a = np.full(count, float(lower))
    b = np.full(count, float(upper))
    fulc = a + golden_mean * (b - a)
    nfc = fulc.copy()
    xf = fulc.copy()
    rat = np.zeros(count)
    e = np.zeros(count)
    fx = func(xf, np.arange(count))
    ffulc = fx.copy()
    fnfc = fx.copy()
    num = np.ones(count, dtype=np.intp)
    xm = 0.5 * (a + b)
    tol1 = sqrt_eps * np.abs(xf) + xatol / 3.0
    tol2 = 2.0 * tol1
    live = np.ones(count, dtype=bool)
    while True:
        live &= np.abs(xf - xm) > (tol2 - 0.5 * (b - a))
        rows = np.nonzero(live)[0]
        if rows.size == 0:
            return xf
        la, lb, lxf, lfx = a[rows], b[rows], xf[rows], fx[rows]
        lfulc, lffulc, lnfc, lfnfc = fulc[rows], ffulc[rows], nfc[rows], fnfc[rows]
        le, lrat, lxm, ltol1, ltol2 = e[rows], rat[rows], xm[rows], tol1[rows], tol2[rows]
        with np.errstate(all="ignore"):
            parabolic = np.abs(le) > ltol1
            r = (lxf - lnfc) * (lfx - lffulc)
            q = (lxf - lfulc) * (lfx - lfnfc)
            p = (lxf - lfulc) * q - (lxf - lnfc) * r
            q = 2.0 * (q - r)
            p = np.where(q > 0.0, -p, p)
            q = np.abs(q)
            accept = parabolic & (np.abs(p) < np.abs(0.5 * q * le)) & (p > q * (la - lxf)) & (p < q * (lb - lxf))
            step = (p + 0.0) / q
            trial = lxf + step
            clamp = ((trial - la) < ltol2) | ((lb - trial) < ltol2)
            direction = np.sign(lxm - lxf) + ((lxm - lxf) == 0)
            step = np.where(clamp, ltol1 * direction, step)
        gold = np.where(lxf >= lxm, la - lxf, lb - lxf)
        new_e = np.where(accept, lrat, gold)
        new_rat = np.where(accept, step, golden_mean * gold)
        if trace is not None:
            trace.add("parabolic", accept)
            trace.add("parabolic_clamped", accept & clamp)
            trace.add("parabolic_rejected", parabolic & ~accept)
            trace.add("golden", ~accept)
        with np.errstate(all="ignore"):
            sign = np.sign(new_rat) + (new_rat == 0)
            x = lxf + sign * np.maximum(np.abs(new_rat), ltol1)
        fu = func(x, rows)
        better = fu <= lfx
        worse = ~better
        up = x >= lxf
        down = x < lxf
        keep_near = (fu <= lfnfc) | (lnfc == lxf)
        keep_far = (fu <= lffulc) | (lfulc == lxf) | (lfulc == lnfc)
        shift = better | (worse & keep_near)
        far = worse & ~keep_near & keep_far
        if trace is not None:
            trace.add("better_up", better & up)
            trace.add("better_down", better & ~up)
            trace.add("worse_down", worse & down)
            trace.add("worse_up", worse & ~down)
            trace.add("worse_near", worse & keep_near)
            trace.add("worse_far", far)
        a[rows] = np.where(better & up, lxf, np.where(worse & down, x, la))
        b[rows] = np.where(better & ~up, lxf, np.where(worse & ~down, x, lb))
        fulc[rows] = np.where(shift, lnfc, np.where(far, x, lfulc))
        ffulc[rows] = np.where(shift, lfnfc, np.where(far, fu, lffulc))
        nfc[rows] = np.where(better, lxf, np.where(worse & keep_near, x, lnfc))
        fnfc[rows] = np.where(better, lfx, np.where(worse & keep_near, fu, lfnfc))
        xf[rows] = np.where(better, x, lxf)
        fx[rows] = np.where(better, fu, lfx)
        e[rows] = new_e
        rat[rows] = new_rat
        xm[rows] = 0.5 * (a[rows] + b[rows])
        tol1[rows] = sqrt_eps * np.abs(xf[rows]) + xatol / 3.0
        tol2[rows] = 2.0 * tol1[rows]
        num[rows] += 1
        live[rows[num[rows] >= maxiter]] = False


def brentq_rows(
    func: Objective,
    left: Floats,
    right: Floats,
    xtol: float,
    rtol: float,
    trace: SolverTrace | None = None,
    maxiter: int = 100,
) -> Floats:
    """The root of every row from SciPy 1.18.1 `brentq`, step for step; each bracket must change sign strictly.

    func(x, rows) returns the objective of the rows `rows` at the points x.
    """
    count = left.shape[0]
    everyone = np.arange(count)
    xpre, xcur = left.copy(), right.copy()
    fpre, fcur = func(xpre, everyone), func(xcur, everyone)
    if np.any((fpre == 0) | (fcur == 0) | (np.signbit(fpre) == np.signbit(fcur))):
        raise ValueError("f(a) and f(b) must have different signs")
    xblk = np.zeros(count)
    fblk = np.zeros(count)
    spre = np.zeros(count)
    scur = np.zeros(count)
    root = np.zeros(count)
    live = np.ones(count, dtype=bool)
    for _ in range(maxiter):
        rows = np.nonzero(live)[0]
        if rows.size == 0:
            return root
        lxpre, lxcur, lfpre, lfcur = xpre[rows], xcur[rows], fpre[rows], fcur[rows]
        lxblk, lfblk, lspre, lscur = xblk[rows], fblk[rows], spre[rows], scur[rows]
        with np.errstate(all="ignore"):
            bracket = (lfpre != 0) & (lfcur != 0) & (np.signbit(lfpre) != np.signbit(lfcur))
            lxblk = np.where(bracket, lxpre, lxblk)
            lfblk = np.where(bracket, lfpre, lfblk)
            lspre = np.where(bracket, lxcur - lxpre, lspre)
            lscur = np.where(bracket, lxcur - lxpre, lscur)
            swap = np.abs(lfblk) < np.abs(lfcur)
            lxpre, lxcur, lxblk = (
                np.where(swap, lxcur, lxpre),
                np.where(swap, lxblk, lxcur),
                np.where(swap, lxcur, lxblk),
            )
            lfpre, lfcur, lfblk = (
                np.where(swap, lfcur, lfpre),
                np.where(swap, lfblk, lfcur),
                np.where(swap, lfcur, lfblk),
            )
            delta = (xtol + rtol * np.abs(lxcur)) / 2
            sbis = (lxblk - lxcur) / 2
            done = (lfcur == 0) | (np.abs(sbis) < delta)
            try_step = (np.abs(lspre) > delta) & (np.abs(lfcur) < np.abs(lfpre))
            interpolate = -lfcur * (lxcur - lxpre) / (lfcur - lfpre)
            dpre = (lfpre - lfcur) / (lxpre - lxcur)
            dblk = (lfblk - lfcur) / (lxblk - lxcur)
            extrapolate = -lfcur * (lfblk * dblk - lfpre * dpre) / (dblk * dpre * (lfblk - lfpre))
            stry = np.where(lxpre == lxblk, interpolate, extrapolate)
            short = try_step & (2 * np.abs(stry) < np.minimum(np.abs(lspre), 3 * np.abs(sbis) - delta))
            lspre = np.where(short, lscur, sbis)
            lscur = np.where(short, stry, sbis)
            lxnew = np.where(np.abs(lscur) > delta, lxcur + lscur, lxcur + np.where(sbis > 0, delta, -delta))
        if trace is not None:
            trace.add("interpolate", ~done & short & (lxpre == lxblk))
            trace.add("extrapolate", ~done & short & (lxpre != lxblk))
            trace.add("bisect_rejected", ~done & try_step & ~short)
            trace.add("bisect", ~done & ~try_step)
            trace.add("swap", swap)
            trace.add("minimum_step", ~done & ~(np.abs(lscur) > delta))
        xpre[rows], xcur[rows], xblk[rows] = lxcur, lxcur, lxblk
        fpre[rows], fcur[rows], fblk[rows] = lfcur, lfcur, lfblk
        spre[rows], scur[rows] = lspre, lscur
        root[rows[done]] = lxcur[done]
        live[rows[done]] = False
        going = rows[~done]
        if going.size:
            xcur[going] = lxnew[~done]
            fcur[going] = func(xcur[going], going)
    if live.any():
        raise RuntimeError(f"Failed to converge after {maxiter} iterations.")
    return root


# --- the stacked Bloch chain ----------------------------------------------------------------------------------


def sx_rows(t1: Floats, t2: Floats, duration: float, z_eq: float, dephasing: Floats, angle: Floats) -> Floats:
    """msa.sx_map of every row: one scalar call per distinct key, whose lru_cache result is the scalar bits."""
    first: dict[tuple[float, float, float, float], int] = {}
    inverse = [
        first.setdefault(key, len(first))
        for key in zip(t1.tolist(), t2.tolist(), dephasing.tolist(), angle.tolist(), strict=True)
    ]
    maps = np.stack([msa.sx_map(a, b, duration, z_eq, c, d) for a, b, c, d in first])
    return maps[inverse]


def rz_rows(angles: Floats) -> Floats:
    unique, inverse = np.unique(angles, return_inverse=True)
    maps = np.stack([msa.rz_map(float(a)) for a in unique.tolist()])
    return maps[inverse.reshape(-1)]


def chain_rows(
    arm: str, n: int, t1: Floats, t2: Floats, tau: Floats, eps: Floats, gate: Gate, sx: Floats, sign: int
) -> Floats:
    """msa.chain_matrix of every row at z_eq = 1: the stacked products in the scalar association.

    `sx` is the damped sx map of the rows (sx_map times 1 - lambda on the three affine rows).
    """
    _, _, _, axis_phase, _ = gate
    count = t1.shape[0]
    second = sx
    tilted = np.broadcast_to(axis_phase, (count,)) != 0
    if tilted.any():
        rows = np.nonzero(tilted)[0]
        phase = np.broadcast_to(axis_phase, (count,))[rows]
        second = sx.copy()
        second[rows] = rz_rows(phase) @ sx[rows] @ rz_rows(-phase)
    pair_rz = msa.rz_map(math.pi / 2)
    step = pair_rz @ second @ msa.rz_map(sign * msa.THETA / n + math.pi) @ sx @ pair_rz
    transverse = exp_rows(-tau / t2)
    longitudinal = exp_rows(-tau / t1)
    idle = np.zeros((count, 4, 4))
    idle[:, 0, 0] = transverse
    idle[:, 1, 1] = transverse
    idle[:, 2, 2] = longitudinal
    idle[:, 3, 3] = 1.0
    idle[:, 2, 3] = 1.0 * (1 - longitudinal)
    cycle = idle @ step
    if arm in msa.PINCHED_ARMS:
        pinch = np.zeros((count, 4, 4))
        pinch[:, 2, 2] = 1 - 2 * eps
        pinch[:, 3, 3] = 1.0
        cycle = idle @ pinch @ step
    return np.asarray(np.linalg.matrix_power(cycle, n))


def damped_sx(t1: Floats, t2: Floats, gate: Gate) -> Floats:
    """The sx map of each row with the depolarizing shrink 1 - lambda applied, as chain_matrix builds it."""
    lam, duration, dephasing, _, angle = gate
    count = t1.shape[0]
    sx = sx_rows(t1, t2, duration, 1.0, np.broadcast_to(dephasing, (count,)), np.broadcast_to(angle, (count,)))
    sx[:, :3, :] *= np.broadcast_to(1 - lam, (count,))[:, None, None]
    return sx


def corrected_rows(
    arm: str, n: int, t1: Floats, t2: Floats, tau: Any, eps: Any, gate: Gate, q: Floats, sx: Floats | None = None
) -> Floats:
    """msa.corrected_z of every row: a + b q of the chain, averaged over the two rotation signs.

    `sx` is damped_sx(t1, t2, gate) of the rows when the caller holds it, which every arm of one fit shares.
    """
    count = t1.shape[0]
    tau, eps = np.broadcast_to(tau, (count,)), np.broadcast_to(eps, (count,))
    if sx is None:
        sx = damped_sx(t1, t2, gate)
    total: Any = 0.0
    for sign in (1, -1):
        chain = chain_rows(arm, n, t1, t2, tau, eps, gate, sx, sign)
        total = total + (chain[:, 2, 2] + chain[:, 2, 3] * q)
    return np.asarray(total / 2)


def tau_rows(arm: str, ctx: dict[str, Any], fraction: Any) -> Any:
    """msa.tau_of with the relaxing fraction of the measure window as a number or a per-row array."""
    window = ctx["window_s"] * fraction
    return {"measure": window, "settle": window + ctx["settle_s"], "delay": ctx["delay_s"], "unitary": 0.0}[arm]


def gate_rows(ctx: dict[str, Any], shift: Any) -> Gate:
    """msa.sx_gate(ctx, shift) for a number or a per-row array of shifts."""
    return 2 * (msa.sx_depolarizing_error(ctx) + shift), ctx["sx_duration_s"], 1.0, 0.0, 0.0


# --- the per-qubit fit on a replicate axis --------------------------------------------------------------------


def fit_t1_rows(delays: list[float], y: Floats, weights: Floats) -> tuple[Floats, Floats]:
    """msa.fit_t1 of every row of y and weights (rows, T1_COUNT): T1 and q."""
    t = np.array(delays)

    def solve(u: Floats, rows: Ints) -> tuple[Floats, Floats]:
        e = np.exp(-t / exp_rows(u)[:, None])
        w, ys = weights[rows], y[rows]
        q = np.sum(w * (1 - e) * (ys + e), axis=1) / np.sum(w * (1 - e) ** 2, axis=1)
        return q, np.sum(w * (ys + e - q[:, None] * (1 - e)) ** 2, axis=1)

    best = minimize_rows(
        lambda u, rows: solve(u, rows)[1],
        y.shape[0],
        math.log(msa.T1_BOUNDS[0]),
        math.log(msa.T1_BOUNDS[1]),
        1e-10,
    )
    return exp_rows(best), solve(best, np.arange(y.shape[0]))[0]


def implied_loss_rows(
    z_corrected: Floats, t1: Floats, t2: Floats, ctx: dict[str, Any], q: Floats, gate: Gate, fraction: Any, sx: Floats
) -> Floats:
    """msa.implied_loss of every row."""
    count = t1.shape[0]
    tau = np.broadcast_to(tau_rows("measure", ctx, fraction), (count,))

    def gap(eps: Any, rows: Ints) -> Floats:
        lam, duration, dephasing, axis_phase, angle = gate
        part = (take(lam, rows), duration, take(dephasing, rows), take(axis_phase, rows), take(angle, rows))
        z = corrected_rows("measure", msa.TOP_STEPS, t1[rows], t2[rows], tau[rows], eps, part, q[rows], sx[rows])
        return z - z_corrected[rows]

    low, high = -0.05, 0.5
    everyone = np.arange(count)
    at_low = gap(low, everyone) <= 0
    at_high = ~at_low & (gap(high, everyone) >= 0)
    out = np.where(at_low, low, high)
    solve = np.nonzero(~at_low & ~at_high)[0]
    if solve.size:
        out[solve] = brentq_rows(
            lambda x, rows: gap(x, solve[rows]),
            np.full(solve.size, low),
            np.full(solve.size, high),
            1e-13,
            1e-13,
        )
    return out


def quantities_rows(
    p: dict[str, Floats], ctx: dict[str, Any], weights: Floats, trace: SolverTrace | None = None
) -> dict[str, Floats]:
    """msa.quantities of every row, p holding the per-row P(1) of each group, sx_shift and window_fraction."""
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2

    def corrected(key: str) -> Floats:
        return ((1 - 2 * p[key]) - offset) / scale

    series = np.stack([corrected(f"t1-{k}") for k in range(msa.T1_COUNT)], axis=1)
    t1, q = fit_t1_rows(ctx["t1_delays_s"], series, weights)
    p_init = (1 - 1 / q) / 2
    gate = gate_rows(ctx, p["sx_shift"])
    fraction = p["window_fraction"]
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    sx = damped_sx(t1, t2, gate)
    out: dict[str, Floats] = {"t1_s": t1, "q": q, "p_init": p_init, "scale": scale, "offset": offset}
    for arm, n in msa.group_keys():
        key = f"{arm}-{n}"
        model = (1 + corrected_rows(arm, n, t1, t2, tau_rows(arm, ctx, fraction), 0.0, gate, q, sx)) / 2
        out[f"p0:{key}"] = (1 + corrected(key)) / 2
        out[f"model:{key}"] = model
        out[f"diff:{key}"] = out[f"p0:{key}"] - model
    top = str(msa.TOP_STEPS)
    out["contrast"] = out[f"p0:measure-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing"] = out[f"p0:delay-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing_modeled"] = out[f"model:delay-{top}"] - out[f"model:unitary-{top}"]
    loss = implied_loss_rows(2 * out[f"p0:measure-{top}"] - 1, t1, t2, ctx, q, gate, fraction, sx)
    settle = corrected_rows("settle", msa.TOP_STEPS, t1, t2, tau_rows("settle", ctx, fraction), loss, gate, q, sx)
    out["implied_loss"] = loss
    out["gap_difference"] = out[f"p0:settle-{top}"] - (1 + settle) / 2
    return out


class Propagated(NamedTuple):
    """msa.propagate_many for a block of replicates: base values, standard errors and shared parts per key."""

    value: dict[str, list[float]]
    se: dict[str, list[float]]
    shared: dict[str, list[float]]


def propagate_rows(
    x: Floats, variances: Floats, weights: Floats, ctx: dict[str, Any], systematic: frozenset[int], keys: list[str]
) -> Propagated:
    """msa.propagate_many of quantities for every replicate (rows of x, variances and weights).

    The base point and the up and down point of each of the inputs stack along the row axis, so one pass of
    quantities_rows evaluates all of them; the delta-method sums then accumulate in input order.
    """
    step = 1e-5
    count, inputs = x.shape
    points = np.repeat(x[None, :, :], 1 + 2 * inputs, axis=0)
    spans = np.empty((inputs, count))
    for i in range(inputs):
        xi = x[:, i]
        small = np.abs(xi) / 10
        spans[i] = np.where(np.abs(xi) > 10 * step, step, np.where(small != 0, small, step))
        points[1 + 2 * i, :, i] = xi + spans[i]
        points[2 + 2 * i, :, i] = xi - spans[i]
    flat = points.reshape(-1, inputs)
    tiled = np.tile(weights, (1 + 2 * inputs, 1))
    out = quantities_rows({key: np.ascontiguousarray(flat[:, j]) for j, key in enumerate(keys)}, ctx, tiled)
    names = list(out)
    table = np.stack([out[name].reshape(1 + 2 * inputs, count) for name in names], axis=1)
    totals = np.zeros((len(names), count))
    shared = np.zeros((len(names), count))
    for i in range(inputs):
        change = (table[1 + 2 * i] - table[2 + 2 * i]) / (2 * spans[i])[None, :]
        term = square_rows(change) * variances[:, i][None, :]
        totals = totals + term
        if i in systematic:
            shared = shared + term
    return Propagated(
        {name: table[0, k].tolist() for k, name in enumerate(names)},
        {name: np.sqrt(totals[k]).tolist() for k, name in enumerate(names)},
        {name: np.sqrt(shared[k]).tolist() for k, name in enumerate(names)},
    )


def curve_values(
    t1: Floats, q: Floats, ctx: dict[str, Any], fraction: float
) -> dict[str, list[tuple[Floats, Floats, Floats]]]:
    """For every gate-model class and side, the grid and the unitary and measure P0 shifts of every replicate.

    Each entry is (grid, unitary, measure) with the two shift arrays of shape (grid points, replicates); the
    scalar gate_curves stops each curve at its own turning point, which the per-replicate tail applies.
    """
    count = t1.shape[0]
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    layout = []
    gates = [msa.sx_gate(ctx)]
    for name, (center, low, high) in msa.GATE_CLASSES.items():
        for end in (low, high):
            grid = np.linspace(center, end, msa.GATE_GRID_POINTS)
            layout.append((name, grid, len(gates)))
            gates.extend(msa.class_gate(ctx, name, float(m)) for m in grid)
    points = len(gates)
    part = (
        np.repeat([g[0] for g in gates], count),
        ctx["sx_duration_s"],
        np.repeat([g[2] for g in gates], count),
        np.repeat([g[3] for g in gates], count),
        np.repeat([g[4] for g in gates], count),
    )
    t1_all, t2_all, q_all = np.tile(t1, points), np.tile(t2, points), np.tile(q, points)
    sx = damped_sx(t1_all, t2_all, part)
    p0 = {}
    for arm in ("unitary", "measure"):
        z = corrected_rows(arm, msa.TOP_STEPS, t1_all, t2_all, msa.tau_of(arm, ctx, fraction), 0.0, part, q_all, sx)
        p0[arm] = np.asarray((1 + z) / 2).reshape(points, count)
    curves: dict[str, list[tuple[Floats, Floats, Floats]]] = {name: [] for name in msa.GATE_CLASSES}
    for name, grid, start in layout:
        span = slice(start, start + msa.GATE_GRID_POINTS)
        curves[name].append((grid, p0["unitary"][span] - p0["unitary"][0], p0["measure"][span] - p0["measure"][0]))
    return curves


def fit_eps_rows(
    t1: Floats, q: Floats, ctx: dict[str, Any], points: list[tuple[int, Floats, Floats]]
) -> tuple[Floats, Floats, Floats, Ints]:
    """msa.fit_eps of every replicate: eps, chi2 at eps, the curvature of chi2 and the grid minimum.

    points holds (N, P0, se) with the P0 and se of every replicate. The grid scan, both golden-section evaluations of
    a step and the three curvature evaluations stack along the row axis.
    """
    count = t1.shape[0]
    t2 = np.minimum(ctx["t2_s"], 2 * t1)
    tau = msa.tau_of("measure", ctx, msa.WINDOW_RELAX_FRACTION)
    gate = msa.sx_gate(ctx)
    if any(np.any(se == 0) for _, _, se in points):
        raise ZeroDivisionError("float division by zero")
    sx = damped_sx(t1, t2, gate)

    def chi2(eps: Floats, replicas: Ints) -> Floats:
        terms = []
        for n, p, se in points:
            law = (
                1 + corrected_rows("measure", n, t1[replicas], t2[replicas], tau, eps, gate, q[replicas], sx[replicas])
            ) / 2
            terms.append(square_rows((p[replicas] - law) / se[replicas]))
        return neumaier_rows(terms)

    grid = np.array(msa.FIT_GRID)
    everyone = np.arange(count)
    profile = chi2(np.repeat(grid, count), np.tile(everyone, grid.size)).reshape(grid.size, count)
    best = np.argmin(profile, axis=0)
    low, high = grid[np.maximum(best - 1, 0)], grid[np.minimum(best + 1, grid.size - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(100):
        a, b = high - ratio * (high - low), low + ratio * (high - low)
        both = chi2(np.concatenate([a, b]), np.tile(everyone, 2))
        keep_low = both[:count] < both[count:]
        low, high = np.where(keep_low, low, a), np.where(keep_low, b, high)
    eps = (low + high) / 2
    h = 1e-4
    around = chi2(np.concatenate([eps, eps + h, eps - h]), np.tile(everyone, 3))
    at, above, below = around[:count], around[count : 2 * count], around[2 * count :]
    return eps, at, (above - 2 * at + below) / math.pow(h, 2.0), best


# --- per-replicate tails of evaluate_qubit --------------------------------------------------------------------

CurveValues = dict[str, list[tuple[Floats, Floats, Floats]]]


def curves_of(values: CurveValues, replica: int) -> dict[str, list[dict[str, Any]]]:
    """msa.gate_curves of one replicate: each curve stops where its unitary shift turns round."""
    curves: dict[str, list[dict[str, Any]]] = {}
    for name, sides in values.items():
        curves[name] = []
        for grid, unitary_all, measure_all in sides:
            unitary = np.ascontiguousarray(unitary_all[:, replica])
            direction = next((float(np.sign(d)) for d in np.diff(unitary) if abs(d) > 1e-12), 0.0)
            stop = len(grid)
            for k, d in enumerate(np.diff(unitary)):
                if direction * d < -1e-12:
                    stop = k + 1
                    break
            measure = np.ascontiguousarray(measure_all[:stop, replica])
            curves[name].append({"magnitude": grid[:stop], "unitary": unitary[:stop], "measure": measure})
    return curves


def qubit_row(
    qubit: int,
    member_counts: dict[str, Any],
    ctx: dict[str, Any],
    readout: dict[str, float],
    fit: tuple[dict[str, float], dict[str, float], dict[str, float]],
    curves: dict[str, list[dict[str, Any]]],
    relaxed: dict[str, Any],
) -> dict[str, Any]:
    """The usable-qubit row of msa.evaluate_qubit from the propagated fit, the gate curves and the eps fit."""
    value, se, shared = fit
    top = str(msa.TOP_STEPS)
    p0: dict[str, dict[str, Any]] = {arm: {} for arm in msa.ARMS}
    for arm, n in msa.group_keys():
        key = f"{arm}-{n}"
        p0[arm][str(n)] = {
            "p0": value[f"p0:{key}"],
            "se": se[f"p0:{key}"],
            "ideal": msa.ideal_arm(arm, n),
            "modeled": value[f"model:{key}"],
            "measured_minus_modeled": value[f"diff:{key}"],
            "measured_minus_modeled_se": se[f"diff:{key}"],
            "planning": ctx["planning"][arm][str(n)],
        }
    unitary_key = f"unitary-{top}"
    propagation = msa.gate_propagation(curves, value[f"diff:{unitary_key}"])
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
    decisions = msa.decide(value["contrast"], se["contrast"], value[f"diff:{key}"], departure_se)
    gap_z = value["gap_difference"] / se["gap_difference"]
    t1, p_init, q = value["t1_s"], value["p_init"], value["q"]
    transitions: dict[str, Any] = {}
    for n in msa.MEASURE_STEPS:
        flips = member_counts.get("flips", {})
        names = msa.member_names("measure", n, qubit)
        if all(name in flips for name in names):
            k = sum(flips[name][0] for name in names)
            pairs = sum(flips[name][1] for name in names)
            transitions[str(n)] = {"rate": k / pairs, "se": math.sqrt(msa.var(k, pairs)), "ideal": msa.ideal_flip(n)}
    repeat = member_counts.get("repeat_read", {})
    names = msa.member_names("measure", msa.TOP_STEPS, qubit)
    repeat_read = None
    if all(name in repeat for name in names):
        k = sum(repeat[name][0] for name in names)
        total = sum(repeat[name][1] for name in names)
        repeat_read = {"agreement": k / total, "se": math.sqrt(msa.var(k, total))}
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
            "ideal": msa.ideal_measure(msa.TOP_STEPS) - msa.ideal_delay(),
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
            "verdict": msa.classify_gap(gap_z),
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


def evaluate_qubit_rows(qubit: int, ctx: dict[str, Any], member_counts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """msa.evaluate_qubit of one qubit for every replicate in member_counts (same context)."""
    rows: list[dict[str, Any] | None] = [None] * len(member_counts)
    usable: list[int] = []
    inputs: list[tuple[list[float], list[float], list[float], dict[str, float], dict[str, Any]]] = []
    keys: list[str] = []
    systematic: frozenset[int] = frozenset()
    for i, counts_of in enumerate(member_counts):
        counts = {name: tuple(value) for name, value in counts_of["final"].items()}
        obs = msa.observations(counts, qubit)
        keys = [*obs, "sx_shift", "window_fraction"]
        x = [*(k / n for k, n in obs.values()), 0.0, msa.WINDOW_RELAX_FRACTION]
        variances = [
            *(msa.var(k, n) for k, n in obs.values()),
            (msa.SX_SYSTEMATIC * ctx["sx_error"]) ** 2,
            msa.WINDOW_RELAX_VARIANCE,
        ]
        index = {key: j for j, key in enumerate(keys)}
        scale = x[index["t1-0"]] - x[index["ro0"]]
        weights = [scale**2 / (4 * variances[index[f"t1-{k}"]]) for k in range(msa.T1_COUNT)]
        if not scale >= msa.READOUT_CONTRAST_FLOOR:
            rows[i] = msa.evaluate_qubit((qubit, counts_of, ctx))
            continue
        systematic = frozenset({index["sx_shift"], index["window_fraction"]})
        readout = {"scale": scale, "offset": 1 - x[index["ro0"]] - x[index["t1-0"]]}
        usable.append(i)
        inputs.append((x, variances, weights, readout, {**ctx, "weights": weights}))
    if usable:
        fitted = propagate_rows(
            np.array([item[0] for item in inputs]),
            np.array([item[1] for item in inputs]),
            np.array([item[2] for item in inputs]),
            ctx,
            systematic,
            keys,
        )
        t1, q = np.array(fitted.value["t1_s"]), np.array(fitted.value["q"])
        curve_grid = curve_values(t1, q, ctx, msa.WINDOW_RELAX_FRACTION)
        points = [
            (n, np.array(fitted.value[f"p0:measure-{n}"]), np.array(fitted.se[f"p0:measure-{n}"]))
            for n in msa.MEASURE_STEPS
        ]
        eps, chi2, curvature, best = fit_eps_rows(t1, q, ctx, points)
        edge = (0, len(msa.FIT_GRID) - 1)
        for j, i in enumerate(usable):
            fit = (
                {name: column[j] for name, column in fitted.value.items()},
                {name: column[j] for name, column in fitted.se.items()},
                {name: column[j] for name, column in fitted.shared.items()},
            )
            curvature_j = float(curvature[j])
            relaxed = {
                "eps": float(eps[j]),
                "eps_se": msa.finite(math.sqrt(2 / curvature_j)) if curvature_j > 0 else None,
                "chi2": float(chi2[j]),
                "dof": len(points) - 1,
                "at_grid_edge": int(best[j]) in edge,
            }
            rows[i] = qubit_row(
                qubit, member_counts[i], inputs[j][4], inputs[j][3], fit, curves_of(curve_grid, j), relaxed
            )
    return [row for row in rows if row is not None]


def finish_rows(rows: dict[int, dict[str, Any]], contexts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """The device-level steps of msa.evaluate once every qubit row exists: scatter widening and informativeness."""
    usable = [q for q, r in rows.items() if r["usable"]]
    if usable:
        residuals = [rows[q]["gate_systematic_n16"]["unitary_residual"] for q in usable]
        scatter = math.sqrt(sum(r * r for r in residuals) / len(residuals))
        floor = contexts[usable[0]].get("model_scatter_floor")
        if floor is not None:
            scatter = max(scatter, floor)
        for q in usable:
            msa.widen_for_device_scatter(rows[q], scatter)
    for row in rows.values():
        row.pop("_gate_curves", None)
        row["model_scatter_floor"] = contexts[row["qubit"]].get("model_scatter_floor")
        row["informative"], row["uninformative_reason"] = msa.informative(row, contexts[row["qubit"]])
    return rows


def qubit_batch(item: tuple[int, dict[str, Any], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """evaluate_qubit_rows of one qubit's batch, in the item form parallel.ordered_map passes."""
    return evaluate_qubit_rows(*item)


def evaluate_batch(
    counts: list[dict[int, dict[str, Any]]], planned: list[dict[int, dict[str, Any]]]
) -> list[dict[int, dict[str, Any]]]:
    """msa.evaluate for every replicate: counts[r] and planned[r] hold the kept qubits of replicate r.

    A qubit shares its context across replicates, so the replicates that kept it form one batch, and the qubits'
    batches map through parallel.ordered_map; inside a block mapped by `run` the pool's worker initializer leaves
    one worker, so the map runs in that worker's process.
    """
    members: dict[int, list[int]] = {}
    for r, contexts in enumerate(planned):
        for q in contexts:
            members.setdefault(q, []).append(r)
    items = []
    for q, replicas in members.items():
        ctx = planned[replicas[0]][q]
        if any(planned[r][q] != ctx for r in replicas):
            raise msa.AnalysisError(f"qubit {q} changes its context across the replicates of one block")
        items.append((q, ctx, [counts[r][q] for r in replicas]))
    done: dict[tuple[int, int], dict[str, Any]] = {}
    for (q, replicas), rows in zip(members.items(), ordered_map(qubit_batch, items, min_items=2), strict=True):
        for r, row in zip(replicas, rows, strict=True):
            done[(r, q)] = row
    return [finish_rows({q: done[(r, q)] for q in contexts}, contexts) for r, contexts in enumerate(planned)]


def analyse_block(item: Block) -> list[tuple[dict, Any, Any]]:
    """The record row, per-qubit rows and device verdict of every replicate of a block of seeds."""
    width, contexts, slopes, floor, seeds = item
    drawn = [draw((width, contexts, slopes, floor, seed)) for seed in seeds]
    full = [r for r, d in enumerate(drawn) if len(d.kept) >= ea.MIN_KEPT]
    planned = [planned_contexts(drawn[r]) for r in full]
    evaluated = evaluate_batch([{q: drawn[r].counts[q] for q in drawn[r].kept} for r in full], planned)
    rows_of = dict(zip(full, evaluated, strict=True))
    out = []
    for r, d in enumerate(drawn):
        row, verdict = summarize(d, rows_of.get(r))
        out.append((row, rows_of.get(r), verdict))
    return out


def replicate_block(item: Block) -> list[dict]:
    """replicate(...) of every seed of a block, from one batched analysis."""
    return [row for row, _, _ in analyse_block(item)]


def run(width: int, replicates: int, seed: int = NULL_SEED) -> dict[str, Any]:
    """The null calibration at one layout width."""
    contexts = null_contexts(width)
    slope_items = ordered_map(residual_slope, [contexts[q] for q in contexts], min_items=2)
    slopes = dict(zip(contexts, slope_items, strict=True))
    floor, reason = msa.bound_floor({"ibm_kingston"})
    if floor is None:
        raise msa.AnalysisError(f"no registered floor: {reason}")
    children = np.random.SeedSequence(seed).spawn(replicates)
    blocks = [
        (width, contexts, slopes, floor, children[start : start + NULL_BLOCK])
        for start in range(0, replicates, NULL_BLOCK)
    ]
    rows = [row for block in ordered_map(replicate_block, blocks, min_items=2) for row in block]
    fires = sum(1 for row in rows if row["fired"])
    bound = upper_bound(fires, replicates)
    return {
        "schema": SCHEMA,
        "width": width,
        "replicates": replicates,
        "seed": seed,
        "common_residual": COMMON_RESIDUAL,
        "independent_residual_sd": INDEPENDENT_RESIDUAL_SD,
        "count_rule": ea.count_rule(width),
        "floor": floor,
        "fires": fires,
        "fired_verdicts": {
            name: sum(1 for row in rows if name in row["fired"])
            for name in sorted({n for r in rows for n in r["fired"]})
        },
        "withheld_replicates": sum(1 for row in rows if row["withheld"]),
        "mean_kept": float(np.mean([row["kept"] for row in rows])),
        "upper_bound_95": bound,
        "ceiling": FALSE_FIRE_CEILING,
        "passes": bound < FALSE_FIRE_CEILING,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--width", type=int, choices=(16, 24, 32), required=True)
    parser.add_argument("--replicates", type=int, default=400)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = run(args.width, args.replicates)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
