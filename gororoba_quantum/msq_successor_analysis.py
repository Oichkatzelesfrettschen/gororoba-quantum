"""Per-qubit analysis and gates of the measurement-sequence envelope successor that need no new circuits.

The module composes the primitives of measurement_sequence_analysis (Bloch chains, readout correction, the gate-model
systematic, the delta-method propagation and the device verdict), whose bytes the registered scatter floor binds, with
the successor's relaxation model (docs/design/measurement-sequence-envelope-successor.md):

- every chain runs with q fixed at 1 and T1 replaced by T, the inverse-mean-rate time of a gamma-rate fit of the
  in-job T1 series (`fit_gamma_rate`); the record carries the shape, the chi-square and its p-value in place of q,
  p_init and p_init_se;
- `shape_bounds` bounds, at each qubit's fitted T, the difference between the rate-averaged and the exponential
  measure prediction over the admitted shapes, and `shape_adjusted` adds each bound linearly to that qubit's shared
  systematic, the term `pooled_z` sums linearly across qubits; `shape_systematic` evaluates the same difference over
  a calibration domain for the dry run's report;
- the admission gate keeps a qubit whose gamma-rate fit has p-value at or above 0.01 / W;
- `equilibrium_estimate` and `q_screen` estimate the job-local relaxation target from a ground-start row and withhold
  a qubit whose lower bound falls below its own tolerance;
- `settle_veto` fits a DerSimonian-Laird random-effects model to the settle gaps about their weighted mean and tests
  each qubit against the fit of the others;
- `carryover_reader` and `order_sentinel` are pure statistics over shot-ordered bit arrays.
"""

from __future__ import annotations

import functools
import json
import math
from collections.abc import Callable, Sequence
from statistics import NormalDist
from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import chi2
from scipy.stats import gamma as gamma_distribution

import measurement_sequence_analysis as msa
from parallel import ordered_map

SCHEMA = "msq-successor-analysis-v1"
# The gamma-rate shape grid: geometric from 0.25 to 1000. The exponential limit (infinite shape) is the upper edge.
SHAPE_LOW = 0.25
SHAPE_HIGH = 1000.0
SHAPE_POINTS = 97
GAMMA_SHAPES = tuple(float(k) for k in np.geomspace(SHAPE_LOW, SHAPE_HIGH, SHAPE_POINTS))
EXPONENTIAL = math.inf
# fit_t1's absolute tolerance on log T, shared by the per-shape profile.
PROFILE_XATOL = 1e-10
# Golden-section steps in log k over two grid intervals (about 0.17 wide) leave a bracket below float resolution.
GOLDEN_STEPS = 40
GOLDEN_RATIO = (math.sqrt(5) - 1) / 2
# Equal-probability midpoint quantiles of the gamma rate distribution that the rate-averaged chain averages over.
GAMMA_NODES = 64
ADMISSION_ALPHA = 0.01
# The registered departure bound floor; the q tolerance, the carryover screen and the shape domain take fractions of it.
BOUND_FLOOR = 0.0188
SCREEN_FRACTION = 0.25
FAMILY_ALPHA = 0.05
# Equilibrium row: a ground-start member that idles this long from the initialized state and reads.
EQUILIBRIUM_DELAY_S = 400e-6
# Between-qubit scatter of the settle gap: the retained run's value on the qubits that pass its pattern screen.
SETTLE_TAU_FLOOR = 0.0019
SETTLE_Z = 3.0
MAD_NORMAL = 1.4826
# Shape-systematic domain: T over the layout's calibrated range with this factor on either side.
SHAPE_T_FACTOR = 2.5
SHAPE_DOMAIN_SHAPES = (0.25, 0.5, 1.0, 2.0, 4.0, 16.0, 64.0)
SHAPE_DOMAIN_T_POINTS = 3
# A signed difference smaller than this is round-off and carries no sign.
SIGN_TOLERANCE = 1e-12
# A conditional difference needs this many shots on each side of its conditioning bit.
MIN_SIDE = 50
ORDER_Z = 3.0
MIN_KEPT = 8


# --- gamma-rate fit -----------------------------------------------------------------------------------------


def survival(t: np.ndarray, scale: float, shape: float) -> np.ndarray:
    """S(t) = (1 + t / (k T))^(-k) for a gamma-distributed decay rate of mean 1 / T and shape k; exp(-t / T) at the
    exponential limit."""
    if math.isinf(shape):
        return np.asarray(np.exp(-t / scale))
    return np.asarray((1 + t / (shape * scale)) ** (-shape))


def _profile(t: np.ndarray, ys: np.ndarray, w: np.ndarray, shape: float) -> tuple[float, float]:
    """(chi-square, T) of the weighted least squares y = 1 - 2 S(t; T, k) at a fixed shape, by the bounded Brent
    search over log T that fit_t1 uses."""

    def residual(u: float) -> float:
        r = ys - (1 - 2 * survival(t, math.exp(u), shape))
        return float(np.sum(w * r * r))

    found = minimize_scalar(
        residual,
        bounds=(math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1])),
        method="bounded",
        options={"xatol": PROFILE_XATOL},
    )
    return float(found.fun), math.exp(float(found.x))


def _minimize_rows(
    func: Callable[[np.ndarray, np.ndarray], np.ndarray], count: int, lower: float, upper: float, xatol: float
) -> np.ndarray:
    """The minimizer of every row from SciPy's bounded scalar search (`_minimize_scalar_bounded`, maxiter 500), step
    for step: parabolic interpolation with golden-section fallback. func(x, rows) returns the objective of the live
    rows `rows` at the points x; a row stops when its own convergence test fails."""
    sqrt_eps = math.sqrt(2.2e-16)
    golden_mean = 0.5 * (3.0 - math.sqrt(5.0))
    a, b = np.full(count, float(lower)), np.full(count, float(upper))
    fulc = a + golden_mean * (b - a)
    nfc, xf = fulc.copy(), fulc.copy()
    rat, e = np.zeros(count), np.zeros(count)
    fx = func(xf, np.arange(count))
    ffulc, fnfc = fx.copy(), fx.copy()
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
        with np.errstate(all="ignore"):
            sign = np.sign(new_rat) + (new_rat == 0)
            x = lxf + sign * np.maximum(np.abs(new_rat), ltol1)
        fu = func(x, rows)
        better = fu <= lfx
        worse = ~better
        up, down = x >= lxf, x < lxf
        keep_near = (fu <= lfnfc) | (lnfc == lxf)
        keep_far = (fu <= lffulc) | (lfulc == lxf) | (lfulc == lnfc)
        shift = better | (worse & keep_near)
        far = worse & ~keep_near & keep_far
        a[rows] = np.where(better & up, lxf, np.where(worse & down, x, la))
        b[rows] = np.where(better & ~up, lxf, np.where(worse & ~down, x, lb))
        fulc[rows] = np.where(shift, lnfc, np.where(far, x, lfulc))
        ffulc[rows] = np.where(shift, lfnfc, np.where(far, fu, lffulc))
        nfc[rows] = np.where(better, lxf, np.where(worse & keep_near, x, lnfc))
        fnfc[rows] = np.where(better, lfx, np.where(worse & keep_near, fu, lfnfc))
        xf[rows] = np.where(better, x, lxf)
        fx[rows] = np.where(better, fu, lfx)
        e[rows], rat[rows] = new_e, new_rat
        xm[rows] = 0.5 * (a[rows] + b[rows])
        tol1[rows] = sqrt_eps * np.abs(xf[rows]) + xatol / 3.0
        tol2[rows] = 2.0 * tol1[rows]
        num[rows] += 1
        live[rows[num[rows] >= 500]] = False


def _profiles(t: np.ndarray, ys: np.ndarray, w: np.ndarray, shapes: Sequence[float]) -> list[tuple[float, float]]:
    """(chi-square, T) of the per-shape profile for every shape at once: the bounded search over log T of each shape
    runs as one masked array iteration."""
    k = np.array(shapes, dtype=float)
    exponential = np.isinf(k)
    safe = np.where(exponential, 1.0, k)

    def residual(u: np.ndarray, rows: np.ndarray) -> np.ndarray:
        scale = np.exp(u)[:, None]
        power = (1 + t[None, :] / (safe[rows][:, None] * scale)) ** (-safe[rows][:, None])
        decay = np.where(exponential[rows][:, None], np.exp(-t[None, :] / scale), power)
        r = ys[None, :] - (1 - 2 * decay)
        return np.asarray(np.sum(w[None, :] * r * r, axis=1))

    found = _minimize_rows(residual, len(k), math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1]), PROFILE_XATOL)
    values = residual(found, np.arange(len(k)))
    return [(float(v), math.exp(float(u))) for v, u in zip(values, found, strict=True)]


@functools.lru_cache(maxsize=1024)
def _fit(
    delays: tuple[float, ...], y: tuple[float, ...], weights: tuple[float, ...]
) -> tuple[float, float, float, bool]:
    """(T, shape, chi-square, at the lower grid edge) of the gamma-rate fit over the delays after the bracket."""
    t, ys, w = np.array(delays[1:]), np.array(y[1:]), np.array(weights[1:])
    grid = (*GAMMA_SHAPES, EXPONENTIAL)
    profiles = _profiles(t, ys, w, grid)
    best = min(range(len(grid)), key=lambda i: profiles[i][0])
    if best == len(grid) - 1:
        return profiles[best][1], EXPONENTIAL, profiles[best][0], False
    low, high = math.log(GAMMA_SHAPES[max(best - 1, 0)]), math.log(GAMMA_SHAPES[min(best + 1, SHAPE_POINTS - 1)])
    a, b = high - GOLDEN_RATIO * (high - low), low + GOLDEN_RATIO * (high - low)
    fa, fb = _profile(t, ys, w, math.exp(a))[0], _profile(t, ys, w, math.exp(b))[0]
    for _ in range(GOLDEN_STEPS):
        if fa < fb:
            high, b, fb = b, a, fa
            a = high - GOLDEN_RATIO * (high - low)
            fa = _profile(t, ys, w, math.exp(a))[0]
        else:
            low, a, fa = a, b, fb
            b = low + GOLDEN_RATIO * (high - low)
            fb = _profile(t, ys, w, math.exp(b))[0]
    shape = math.exp((low + high) / 2)
    refined = _profile(t, ys, w, shape)
    if refined[0] > profiles[best][0]:
        return profiles[best][1], GAMMA_SHAPES[best], profiles[best][0], best == 0
    return refined[1], shape, refined[0], best == 0


def fit_gamma_rate(delays: Sequence[float], y: Sequence[float], weights: Sequence[float]) -> dict[str, Any]:
    """T, k, chi-square, dof and p-value of y_k = 1 - 2 S(t_k; T, k) over the corrected T1 series.

    The series lists the bracket (delay 0) first; its residual is zero by construction, so the fit and its dof (the
    delays after the bracket minus the two parameters) use the later points. The shape grid, the per-shape Brent
    profile and the golden-section refinement in log k are fixed, so the fit is a deterministic function of its inputs
    and continuous in them. A best grid shape at the exponential edge returns shape = math.inf and the exponential T.
    """
    if not len(delays) == len(y) == len(weights):
        raise msa.AnalysisError("the delays, series and weights differ in length")
    t_s, shape, statistic, lower_edge = _fit(
        tuple(float(d) for d in delays), tuple(float(v) for v in y), tuple(float(v) for v in weights)
    )
    dof = len(delays) - 1 - 2
    return {
        "t_s": t_s,
        "shape": shape,
        "chi2": statistic,
        "dof": dof,
        "p_value": float(chi2.sf(statistic, dof)) if dof > 0 else None,
        "exponential_edge": math.isinf(shape),
        "lower_edge": lower_edge,
    }


def admitted(p_value: float | None, width: int) -> bool:
    """The admission gate: the fit's p-value reaches ADMISSION_ALPHA / W. A fit with no degrees of freedom fails."""
    return p_value is not None and p_value >= ADMISSION_ALPHA / width


# --- shape systematic ---------------------------------------------------------------------------------------


def gamma_measure_p0(ctx: dict[str, Any], t_s: float, shape: float, fraction: float | None = None) -> float:
    """The measure arm's N = 16 P0 at q = 1 averaged over a gamma-distributed decay rate of mean 1 / t_s."""
    if math.isinf(shape):
        return float(msa.model_tables(t_s, 1.0, ctx, 0.0, fraction)["measure"][str(msa.TOP_STEPS)])
    quantiles = (np.arange(GAMMA_NODES) + 0.5) / GAMMA_NODES
    rates = gamma_distribution.ppf(quantiles, shape, scale=1 / (shape * t_s))
    gate = msa.sx_gate(ctx, 0.0)
    tau = msa.tau_of("measure", ctx, fraction)
    total = 0.0
    for rate in rates.tolist():
        t1 = 1 / rate
        total += (1 + msa.corrected_z("measure", msa.TOP_STEPS, t1, min(ctx["t2_s"], 2 * t1), tau, 0.0, gate, 1.0)) / 2
    return total / GAMMA_NODES


def _shape_row(item: tuple[dict[str, Any], tuple[float, ...], tuple[float, ...]]) -> list[float]:
    ctx, shapes, lifetimes = item
    out: list[float] = []
    for t_s in lifetimes:
        exponential = gamma_measure_p0(ctx, t_s, EXPONENTIAL)
        out.extend(gamma_measure_p0(ctx, t_s, shape) - exponential for shape in shapes)
    return out


def shape_systematic(domain: dict[str, Any]) -> dict[str, Any]:
    """The bound on the shape's effect on the N = 16 measure prediction over an admitted domain.

    domain["contexts"] maps each layout qubit to its context (the live arm durations, T2 and sx data) and may carry
    "shapes" (default SHAPE_DOMAIN_SHAPES), "t_factor" (default SHAPE_T_FACTOR) and "t_points" (default
    SHAPE_DOMAIN_T_POINTS) and "t_scope". T runs geometrically over [min T1_cal / t_factor, max T1_cal * t_factor] of
    the layout, or of each qubit's own calibrated T1 when t_scope is "qubit". A single point sits at the middle of the
    range (the calibrated T1 itself at t_factor 1). At
    every (qubit, T, shape) the signed difference is the rate-averaged minus the exponential measure P0 at the same T.
    The bound is the largest absolute difference; `single_signed` reports that every difference shares one sign, which
    Jensen's inequality gives wherever the prediction rises with survival, and the dry run checks it over the domain.
    """
    contexts: dict[Any, dict[str, Any]] = domain["contexts"]
    shapes = tuple(float(s) for s in domain.get("shapes", SHAPE_DOMAIN_SHAPES))
    factor = float(domain.get("t_factor", SHAPE_T_FACTOR))
    points = int(domain.get("t_points", SHAPE_DOMAIN_T_POINTS))
    if not contexts or not shapes or points < 1 or any(not 0 < s < math.inf for s in shapes):
        raise msa.AnalysisError("the shape domain needs contexts, finite positive shapes and a T grid")
    scope = domain.get("t_scope", "layout")
    if scope not in ("layout", "qubit"):
        raise msa.AnalysisError(f"unknown T scope {scope}")

    def lifetimes(calibrated: Sequence[float]) -> tuple[float, ...]:
        low, high = min(calibrated) / factor, max(calibrated) * factor
        if points == 1:
            return (math.sqrt(low * high),)
        return tuple(float(v) for v in np.geomspace(low, high, points))

    layout = lifetimes([float(ctx["t1_cal_s"]) for ctx in contexts.values()])
    grids = [layout if scope == "layout" else lifetimes([float(ctx["t1_cal_s"])]) for ctx in contexts.values()]
    rows = ordered_map(
        _shape_row, [(ctx, shapes, grid) for ctx, grid in zip(contexts.values(), grids, strict=True)], min_items=2
    )
    values = [v for row in rows for v in row]
    largest, smallest = max(values), min(values)
    single = largest <= SIGN_TOLERANCE or smallest >= -SIGN_TOLERANCE
    return {
        "bound": max(abs(largest), abs(smallest)),
        "maximum": largest,
        "minimum": smallest,
        "single_signed": single,
        "shapes": list(shapes),
        "lifetimes_s": list(layout) if scope == "layout" else None,
        "t_scope": scope,
        "t_factor": factor,
        "qubits": len(contexts),
    }


def _shape_bound(item: tuple[dict[str, Any], float, tuple[float, ...]]) -> float:
    ctx, t_s, shapes = item
    return max(abs(v) for v in _shape_row((ctx, shapes, (t_s,))))


def shape_bounds(
    rows: dict[Any, dict[str, Any]], contexts: dict[Any, dict[str, Any]], shapes: Sequence[float] = SHAPE_DOMAIN_SHAPES
) -> dict[Any, float]:
    """Each qubit's largest |rate-averaged - exponential| N = 16 measure P0 at its own fitted T over the shapes.

    The chains run exponential at the fitted inverse-mean-rate time, and the fit leaves the shape loosely determined,
    so the bound takes the worst admitted shape at the T the chains use; it is a function of the qubit's fit and
    context alone, fixed before the departure is read.
    """
    grid = tuple(float(k) for k in shapes)
    if not grid or any(not 0 < k < math.inf for k in grid):
        raise msa.AnalysisError("the shape bound needs finite positive shapes")
    qubits = [q for q in rows if q in contexts]
    values = ordered_map(
        _shape_bound, [(contexts[q], float(rows[q]["fitted"]["t1_s"]), grid) for q in qubits], min_items=2
    )
    return dict(zip(qubits, values, strict=True))


def shape_adjusted(rows: dict[Any, dict[str, Any]], bounds: dict[Any, float]) -> dict[Any, dict[str, Any]]:
    """Rows whose departure systematic carries each qubit's shape bound linearly: pooled_z sums each qubit's
    systematic across qubits without quadrature, so the bounds stay a device-shared term."""
    out: dict[Any, dict[str, Any]] = {}
    for qubit, row in rows.items():
        if not row.get("usable"):
            out[qubit] = row
            continue
        bound = bounds[qubit]
        departure = {**row["departure_n16"], "se_systematic": row["departure_n16"]["se_systematic"] + bound}
        out[qubit] = {**row, "departure_n16": departure, "shape_systematic": bound}
    return out


# --- per-qubit analysis -------------------------------------------------------------------------------------


def series_weights(scale: float, variances: Sequence[float]) -> list[float]:
    """Weights of the corrected T1 series: the inverse of the variance of y = ((1 - 2 p) - offset) / scale."""
    return [scale**2 / (4 * v) for v in variances]


def quantities(p: dict[str, float], ctx: dict[str, Any]) -> dict[str, float]:
    """Every figure the decisions and reports use, as a function of the P(1) of each group and the sx error.

    ro0 and ro1 (t1-0) fix the readout offset and scale; the gamma-rate fit of the T1 series fixes T; every chain then
    runs at q = 1 with T1 = T, so the fit's uncertainty propagates with the measurement's.
    """
    z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
    scale, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2

    def corrected(key: str) -> float:
        return ((1 - 2 * p[key]) - offset) / scale

    series = [corrected(f"t1-{k}") for k in range(msa.T1_COUNT)]
    t1 = fit_gamma_rate(ctx["t1_delays_s"], series, ctx["weights"])["t_s"]
    gate = msa.sx_gate(ctx, p["sx_shift"])
    t2 = min(ctx["t2_s"], 2 * t1)
    tables = msa.model_tables(t1, 1.0, ctx, p["sx_shift"], p["window_fraction"])
    out: dict[str, float] = {"t1_s": t1, "scale": scale, "offset": offset}
    for arm, n in msa.group_keys():
        key = f"{arm}-{n}"
        out[f"p0:{key}"] = (1 + corrected(key)) / 2
        out[f"model:{key}"] = tables[arm][str(n)]
        out[f"diff:{key}"] = out[f"p0:{key}"] - out[f"model:{key}"]
    top = str(msa.TOP_STEPS)
    out["contrast"] = out[f"p0:measure-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing"] = out[f"p0:delay-{top}"] - out[f"p0:unitary-{top}"]
    out["dephasing_modeled"] = out[f"model:delay-{top}"] - out[f"model:unitary-{top}"]
    loss = msa.implied_loss(2 * out[f"p0:measure-{top}"] - 1, t1, t2, ctx, 1.0, gate, p["window_fraction"])
    settle = msa.corrected_z(
        "settle", msa.TOP_STEPS, t1, t2, msa.tau_of("settle", ctx, p["window_fraction"]), loss, gate, 1.0
    )
    out["implied_loss"] = loss
    out["gap_difference"] = out[f"p0:settle-{top}"] - (1 + settle) / 2
    return out


def evaluate_qubit(item: tuple[int, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The decisions and descriptive outputs of one qubit from its member counts and context, at q = 1 and T1 = T."""
    return _evaluate(item, True)


def _evaluate(item: tuple[int, dict[str, Any], dict[str, Any]], descriptive: bool) -> dict[str, Any]:
    """evaluate_qubit; `descriptive` False leaves out the relaxed-loss fit, the transitions and the repeat read, which
    no decision reads (the planning standard error needs the decisions only)."""
    qubit, member_counts, ctx = item
    counts = {name: tuple(value) for name, value in member_counts["final"].items()}
    obs = msa.observations(counts, qubit)
    keys = [*obs, "sx_shift", "window_fraction"]
    x = [*(k / n for k, n in obs.values()), 0.0, msa.WINDOW_RELAX_FRACTION]
    variances = [
        *(msa.var(k, n) for k, n in obs.values()),
        (msa.SX_SYSTEMATIC * ctx["sx_error"]) ** 2,
        msa.WINDOW_RELAX_VARIANCE,
    ]
    index = {key: i for i, key in enumerate(keys)}
    scale = x[index["t1-0"]] - x[index["ro0"]]
    ctx = {
        **ctx,
        "weights": series_weights(scale, [variances[index[f"t1-{k}"]] for k in range(msa.T1_COUNT)]),
    }
    readout = {"scale": scale, "offset": 1 - x[index["ro0"]] - x[index["t1-0"]]}
    if not scale >= msa.READOUT_CONTRAST_FLOOR:
        return {
            "qubit": qubit,
            "readout": readout,
            "usable": False,
            "reason": f"readout scale {scale:.4f} lies below the {msa.READOUT_CONTRAST_FLOOR} floor",
        }
    value, se, shared = msa.propagate_many(
        lambda xs: quantities(dict(zip(keys, xs, strict=True)), ctx),
        x,
        variances,
        frozenset({index["sx_shift"], index["window_fraction"]}),
    )
    fit = fit_gamma_rate(
        ctx["t1_delays_s"],
        [((1 - 2 * x[index[f"t1-{k}"]]) - value["offset"]) / value["scale"] for k in range(msa.T1_COUNT)],
        ctx["weights"],
    )
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
    curves = msa.gate_curves(value["t1_s"], 1.0, ctx, msa.WINDOW_RELAX_FRACTION)
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
    t1 = value["t1_s"]
    t2 = min(ctx["t2_s"], 2 * t1)
    tau = msa.tau_of("measure", ctx, msa.WINDOW_RELAX_FRACTION)
    gate = msa.sx_gate(ctx)
    relaxed: dict[str, Any] | None = None
    transitions: dict[str, Any] = {}
    repeat_read = None
    if descriptive:
        relaxed = msa.fit_eps(
            [(n, value[f"p0:measure-{n}"], se[f"p0:measure-{n}"]) for n in msa.MEASURE_STEPS],
            lambda n, eps: (1 + msa.corrected_z("measure", n, t1, t2, tau, eps, gate, 1.0)) / 2,
        )
        for n in msa.MEASURE_STEPS:
            flips = member_counts.get("flips", {})
            names = msa.member_names("measure", n, qubit)
            if all(name in flips for name in names):
                k = sum(flips[name][0] for name in names)
                pairs = sum(flips[name][1] for name in names)
                transitions[str(n)] = {
                    "rate": k / pairs,
                    "se": math.sqrt(msa.var(k, pairs)),
                    "ideal": msa.ideal_flip(n),
                }
        repeat = member_counts.get("repeat_read", {})
        names = msa.member_names("measure", msa.TOP_STEPS, qubit)
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
            "shape": msa.finite(fit["shape"]),
            "exponential_edge": fit["exponential_edge"],
            "chi2": fit["chi2"],
            "dof": fit["dof"],
            "p_value": fit["p_value"],
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


# --- planning and the whole-device evaluation ---------------------------------------------------------------


def planning_tables(contexts: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """P0 per arm and N at each qubit's calibrated T1 and q = 1."""
    return {q: msa.model_tables(ctx["t1_cal_s"], 1.0, ctx) for q, ctx in contexts.items()}


def planning_departure_se(item: tuple[int, dict[str, Any]]) -> float:
    """The departure standard error of one qubit at the planning model (calibrated T1, ground-state decay): the
    analysis run on its expected counts, widened by the scatter floor when one is set."""
    q, ctx = item
    counts = msa.device_counts({q: msa.device_model(ctx, p_init=0.0)}, {q: ctx}, msa.PLANNING_SHOTS)[q]
    row = _evaluate((q, counts, ctx), False)
    floor = ctx.get("model_scatter_floor")
    if floor is not None:
        msa.widen_for_device_scatter(row, floor)
    return float(row["departure_n16"]["se"])


_PLANNING_SE: dict[str, float] = {}


def with_planning(
    contexts: dict[int, dict[str, Any]], floor: float | None = msa.MODEL_SCATTER_FLOOR
) -> dict[int, dict[str, Any]]:
    """Contexts with the q = 1 planning tables, the scatter floor and the planning departure standard error."""
    tables = planning_tables(contexts)
    planned = {q: {**ctx, "planning": tables[q], "model_scatter_floor": floor} for q, ctx in contexts.items()}
    keys = {
        q: json.dumps({k: v for k, v in ctx.items() if k != "planning"}, sort_keys=True) for q, ctx in planned.items()
    }
    todo = [(q, planned[q]) for q in planned if keys[q] not in _PLANNING_SE]
    for (q, _), se in zip(todo, ordered_map(planning_departure_se, todo, min_items=2), strict=True):
        _PLANNING_SE[keys[q]] = se
    return {q: {**ctx, "planning_se": _PLANNING_SE[keys[q]]} for q, ctx in planned.items()}


def evaluate(
    counts: dict[int, dict[str, Any]], contexts: dict[int, dict[str, Any]], width: int | None = None
) -> dict[int, dict[str, Any]]:
    """Every qubit's row (contexts carry the planning fields of with_planning), widened by the device's unitary
    scatter, with the admission gate at layout width `width` (default: the number of contexts)."""
    width = len(contexts) if width is None else width
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
            msa.widen_for_device_scatter(rows[q], scatter)
    for row in rows.values():
        row.pop("_gate_curves", None)
        row["model_scatter_floor"] = contexts[row["qubit"]].get("model_scatter_floor")
        ok, reason = msa.informative(row, contexts[row["qubit"]])
        row["informative_before_admission"] = ok
        if row["usable"]:
            p_value = row["fitted"]["p_value"]
            row["admission"] = {
                "p_value": p_value,
                "threshold": ADMISSION_ALPHA / width,
                "passes": admitted(p_value, width),
            }
            if ok and not row["admission"]["passes"]:
                ok, reason = False, "the gamma-rate fit fails the admission gate"
        row["informative"], row["uninformative_reason"] = ok, reason
    return rows


def analyze_members(
    member_counts: dict[int, dict[str, Any]],
    contexts: dict[int, dict[str, Any]],
    floor: float | None = msa.MODEL_SCATTER_FLOOR,
    width: int | None = None,
) -> dict[int, dict[str, Any]]:
    """The successor rows from whole-shot member counts and per-qubit contexts."""
    return evaluate(member_counts, with_planning(contexts, floor), width)


# --- equilibrium row and the relaxation-target screen -------------------------------------------------------


def q_sensitivity(ctx: dict[str, Any], t_s: float | None = None) -> float:
    """|dP0/dq| of the N = 16 measure prediction at the qubit's context and lifetime T (default: calibrated T1).

    corrected_z is linear in q, so the difference between q = 1 and q = 0 is the derivative exactly.
    """
    t1 = ctx["t1_cal_s"] if t_s is None else t_s
    gate = msa.sx_gate(ctx)
    t2 = min(ctx["t2_s"], 2 * t1)
    tau = msa.tau_of("measure", ctx, msa.WINDOW_RELAX_FRACTION)
    high = msa.corrected_z("measure", msa.TOP_STEPS, t1, t2, tau, 0.0, gate, 1.0)
    low = msa.corrected_z("measure", msa.TOP_STEPS, t1, t2, tau, 0.0, gate, 0.0)
    return abs(high - low) / 2


def equilibrium_estimate(
    obs: dict[str, tuple[int, int]], ctx: dict[str, Any], delay_s: float = EQUILIBRIUM_DELAY_S
) -> dict[str, Any]:
    """q_hat = 1 - 2 e / (1 - S(t)) from the bracket-corrected excitation e of a ground-start row read at `delay_s`.

    obs holds (ones, shots) for "ro0", "t1-0" through "t1-4" and "eq". A ground-start row at time t reads the
    corrected z = q + (1 - q) S(t), so e = (1 - z) / 2 = (1 - q)(1 - S) / 2 with S the qubit's fitted gamma survival.
    The standard error propagates the binomial variance of every count through the brackets and the gamma-rate fit.
    q_hat is not clipped.
    """
    keys = ["ro0", *(f"t1-{k}" for k in range(msa.T1_COUNT)), "eq"]
    x = [obs[k][0] / obs[k][1] for k in keys]
    variances = [msa.var(*obs[k]) for k in keys]
    index = {key: i for i, key in enumerate(keys)}
    scale = x[index["t1-0"]] - x[index["ro0"]]
    if not scale >= msa.READOUT_CONTRAST_FLOOR:
        raise msa.AnalysisError(f"readout scale {scale:.4f} lies below the {msa.READOUT_CONTRAST_FLOOR} floor")
    weights = series_weights(scale, [variances[index[f"t1-{k}"]] for k in range(msa.T1_COUNT)])
    delays = ctx["t1_delays_s"]

    def estimate(xs: list[float]) -> dict[str, float]:
        p = dict(zip(keys, xs, strict=True))
        z0obs, z1obs = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
        s, offset = (z0obs - z1obs) / 2, (z0obs + z1obs) / 2
        series = [((1 - 2 * p[f"t1-{k}"]) - offset) / s for k in range(msa.T1_COUNT)]
        fit = fit_gamma_rate(delays, series, weights)
        decay = float(survival(np.array([delay_s]), fit["t_s"], fit["shape"])[0])
        excitation = (1 - ((1 - 2 * p["eq"]) - offset) / s) / 2
        return {"q_hat": 1 - 2 * excitation / (1 - decay), "t1_s": fit["t_s"], "excitation": excitation}

    value, se, _ = msa.propagate_many(estimate, x, variances)
    return {
        "q_hat": value["q_hat"],
        "se": se["q_hat"],
        "excitation": value["excitation"],
        "excitation_se": se["excitation"],
        "t1_s": value["t1_s"],
        "delay_s": delay_s,
    }


def q_screen(estimate: dict[str, Any], sensitivity: float, width: int, alpha: float = FAMILY_ALPHA) -> dict[str, Any]:
    """The withhold rule: a qubit whose q_hat lower confidence bound (one-sided, Bonferroni over W) lies below
    1 - SCREEN_FRACTION * BOUND_FLOOR / |dP0/dq| is withheld."""
    if not sensitivity > 0:
        raise msa.AnalysisError("the q sensitivity must be positive")
    tolerance = 1 - SCREEN_FRACTION * BOUND_FLOOR / sensitivity
    z = NormalDist().inv_cdf(1 - alpha / width)
    lower = estimate["q_hat"] - z * estimate["se"]
    return {
        "lower_bound": lower,
        "tolerance": tolerance,
        "sensitivity": sensitivity,
        "z": z,
        "passes": lower >= tolerance,
    }


# --- settle veto --------------------------------------------------------------------------------------------


def _random_effects(g: np.ndarray, s2: np.ndarray) -> tuple[float, float, float, float]:
    """(mu, se of mu, DerSimonian-Laird tau, floored tau) of gaps g with variances s2."""
    w0 = 1 / s2
    mean0 = float(np.sum(w0 * g) / np.sum(w0))
    q_statistic = float(np.sum(w0 * (g - mean0) ** 2))
    n = len(g)
    denominator = float(np.sum(w0) - np.sum(w0**2) / np.sum(w0))
    tau2 = max((q_statistic - (n - 1)) / denominator, 0.0) if n > 1 and denominator > 0 else 0.0
    tau = max(math.sqrt(tau2), SETTLE_TAU_FLOOR)
    w = 1 / (s2 + tau**2)
    return float(np.sum(w * g) / np.sum(w)), 1 / math.sqrt(float(np.sum(w))), math.sqrt(tau2), tau


def _robust_others(g: np.ndarray, s2: np.ndarray) -> tuple[float, float, float]:
    """(center, se of center, floored tau) of the other qubits' gaps by median and MAD.

    The median and the normal-consistent MAD (1.4826 x the median absolute deviation) stay put while fewer than half
    the gaps are outliers, so a second outlier among the others does not widen the scatter a qubit is judged against;
    tau^2 is the MAD variance minus the median sampling variance, floored at SETTLE_TAU_FLOOR. The median's standard
    error is sqrt(pi / 2) sqrt(s^2 + tau^2) / sqrt(n) at the median s^2.
    """
    center = float(np.median(g))
    spread = MAD_NORMAL * float(np.median(np.abs(g - center)))
    sampling = float(np.median(s2))
    tau = max(math.sqrt(max(spread**2 - sampling, 0.0)), SETTLE_TAU_FLOOR)
    return center, math.sqrt(math.pi / 2 * (sampling + tau**2) / len(g)), tau


def settle_veto(gaps: dict[Any, tuple[float, float]]) -> dict[str, Any]:
    """Random-effects veto over the settle gaps (gap, standard error) of the qubits that pass every other gate.

    The between-qubit scatter tau comes from the DerSimonian-Laird moments about the inverse-variance weighted mean
    and is floored at SETTLE_TAU_FLOOR. With weights 1 / (s^2 + tau^2) the common mean mu has standard error
    1 / sqrt(sum of weights); |mu / se| beyond SETTLE_Z withholds the device-level departure verdict. Because tau is
    fitted about the weighted mean, a gap common to the qubits moves mu and leaves the scatter alone. Each qubit is
    tested against the other qubits by a robust center and scale (`_robust_others`): with mu_-i, se_-i and tau_-i
    taken without it, a qubit with |g - mu_-i| / sqrt(s^2 + tau_-i^2 + se_-i^2) beyond SETTLE_Z is withheld, so
    neither its own gap nor a minority of other outliers widens the scatter it is judged against. With one qubit the
    per-qubit test is not evaluated.
    """
    if not gaps:
        return {"evaluable": False, "reason": "no qubit reaches the settle veto", "common_veto": False}
    qubits = list(gaps)
    g = np.array([gaps[q][0] for q in qubits])
    s2 = np.array([gaps[q][1] ** 2 for q in qubits])
    if not np.all(s2 > 0):
        raise msa.AnalysisError("a settle gap needs a positive standard error")
    n = len(qubits)
    mu, se_mu, tau_dl, tau = _random_effects(g, s2)
    z_common = mu / se_mu
    per_qubit = {}
    for i, q in enumerate(qubits):
        if n < 2:
            per_qubit[str(q)] = {"gap": float(g[i]), "z": None, "withheld": False}
            continue
        others = np.arange(n) != i
        mu_i, se_i, tau_i = _robust_others(g[others], s2[others])
        z = (float(g[i]) - mu_i) / math.sqrt(float(s2[i]) + tau_i**2 + se_i**2)
        per_qubit[str(q)] = {
            "gap": float(g[i]),
            "z": z,
            "mu_others": mu_i,
            "tau_others": tau_i,
            "withheld": abs(z) > SETTLE_Z,
        }
    return {
        "evaluable": True,
        "qubits": n,
        "mu": mu,
        "se_mu": se_mu,
        "z_common": z_common,
        "common_veto": abs(z_common) > SETTLE_Z,
        "tau_dl": tau_dl,
        "tau": tau,
        "tau_floor": SETTLE_TAU_FLOOR,
        "per_qubit": per_qubit,
        "withheld_qubits": [q for q in qubits if per_qubit[str(q)]["withheld"]],
    }


# --- carryover readers and the order sentinel ---------------------------------------------------------------


def conditional_difference(current: np.ndarray, previous: np.ndarray) -> tuple[float, float] | None:
    """P(current = 1 | previous = 1) - P(current = 1 | previous = 0) and its binomial standard error, or None when a
    side holds fewer than MIN_SIDE shots. Each side's variance is at least that of one count, so a side that reads
    all zeros keeps a spread."""
    ones, zeros = current[previous == 1], current[previous == 0]
    if ones.size < MIN_SIDE or zeros.size < MIN_SIDE:
        return None
    p1, p0 = float(ones.mean()), float(zeros.mean())
    se = math.sqrt(max(p1 * (1 - p1), 1.0 / ones.size) / ones.size + max(p0 * (1 - p0), 1.0 / zeros.size) / zeros.size)
    return p1 - p0, se


def carryover_reader(
    predecessors: Sequence[np.ndarray],
    readers: Sequence[np.ndarray],
    contrast: float,
    allocation: float,
    width: int,
    alpha: float = FAMILY_ALPHA,
) -> dict[str, Any]:
    """The excitation an |1> end state leaves at the next shot, from reader members that read ground only.

    predecessors[i] holds the final bits of the member row that reader i follows and readers[i] the reader's bits,
    both indexed by shot: under column-wise execution reader shot j follows predecessor shot j. D is the reader's P1
    after a predecessor 1 minus after a predecessor 0, pooled over the readers' shots and divided by the readout
    contrast (the readers read ground in both classes, so no crosstalk enters the contrast). The contrast is taken as
    fixed: D sits near zero, so the contrast's own error moves it negligibly. U is the one-sided upper confidence
    bound of |D| (Bonferroni over `width`), and the screen keeps the qubit when allocation * U lies below
    SCREEN_FRACTION * BOUND_FLOOR.
    """
    if len(predecessors) != len(readers) or not readers:
        raise msa.AnalysisError("each reader needs one predecessor row")
    if not contrast > 0:
        raise msa.AnalysisError("the readout contrast must be positive")
    previous = np.concatenate([np.asarray(p).ravel() for p in predecessors])
    current = np.concatenate([np.asarray(r).ravel() for r in readers])
    if previous.shape != current.shape:
        raise msa.AnalysisError("a reader and its predecessor differ in shots")
    margin = SCREEN_FRACTION * BOUND_FLOOR
    value = conditional_difference(current, previous)
    if value is None:
        return {
            "evaluable": False,
            "reason": f"a conditioning class holds fewer than {MIN_SIDE} shots",
            "passes": False,
        }
    difference, se = value[0] / contrast, value[1] / contrast
    z = NormalDist().inv_cdf(1 - alpha / width)
    upper = abs(difference) + z * se
    bias = allocation * upper
    return {
        "evaluable": True,
        "d": difference,
        "se": se,
        "upper_bound": upper,
        "z": z,
        "allocation": allocation,
        "bias_bound": bias,
        "margin": margin,
        "shots": int(previous.size),
        "passes": bias < margin,
    }


def order_sentinel(pairs: Sequence[tuple[np.ndarray, np.ndarray]], z_min: float = ORDER_Z) -> dict[str, Any]:
    """Whether consecutive rows correlate at the same shot index and not one column away.

    Each pair holds the shot-ordered final bits of a row and its successor, one line per qubit. Per qubit the cell
    statistic is the same-shot conditional difference minus the mean of the two one-column-misaligned ones, over its
    standard error; the pooled one-sided z is the sum of the cell statistics over the square root of their count. The
    sentinel passes when the pooled z exceeds z_min. A shuffled shot order leaves no same-shot structure and a
    pooled z near zero.
    """
    cells: list[float] = []
    for previous, current in pairs:
        prev, cur = np.atleast_2d(np.asarray(previous)), np.atleast_2d(np.asarray(current))
        if prev.shape != cur.shape:
            raise msa.AnalysisError("a sentinel pair differs in shape")
        for a, b in zip(prev, cur, strict=True):
            same = conditional_difference(b, a)
            behind = conditional_difference(b[1:], a[:-1])
            ahead = conditional_difference(b[:-1], a[1:])
            if same is None or behind is None or ahead is None:
                continue
            delta = same[0] - (behind[0] + ahead[0]) / 2
            se = math.sqrt(same[1] ** 2 + (behind[1] ** 2 + ahead[1] ** 2) / 4)
            cells.append(delta / se)
    if not cells:
        return {"evaluable": False, "cells": 0, "z": None, "passes": False}
    z = sum(cells) / math.sqrt(len(cells))
    return {"evaluable": True, "cells": len(cells), "z": z, "z_min": z_min, "passes": z > z_min}


# --- device decision ----------------------------------------------------------------------------------------


def device_decision(
    rows: dict[int, dict[str, Any]],
    eligible: Sequence[int],
    count: int,
    shape_bounds_by_qubit: dict[Any, float],
    device_count: int = MIN_KEPT,
) -> dict[str, Any]:
    """The settle veto, the departure and the count rule over the qubits that pass every gate independent of settle.

    `eligible` lists the qubits that passed the gates outside this module (execution eligibility, the pattern screen,
    the carryover screen, the equilibrium bound); a row also needs to be informative, which includes the admission
    gate. A common-mean settle veto, or fewer than `device_count` qualifying qubits, withholds the device verdict and
    leaves every kept qubit's row; `count` is the count rule's size, and each kept qubit's entry of
    `shape_bounds_by_qubit` (`shape_bounds`) enters its departure's shared systematic linearly.
    """
    pool = {q: r for q, r in rows.items() if q in set(eligible) and r.get("usable") and r.get("informative")}
    veto = settle_veto({q: (r["settle_n16"]["gap_difference"], r["settle_n16"]["se"]) for q, r in pool.items()})
    withheld_qubits = set(veto.get("withheld_qubits", []))
    kept = {q: r for q, r in pool.items() if q not in withheld_qubits}
    reasons = []
    if veto["common_veto"]:
        reasons.append(f"common settle gap z {veto['z_common']:.3g} beyond {SETTLE_Z}")
    if len(kept) < device_count:
        reasons.append(f"{len(kept)} qualifying qubits, fewer than {device_count}")
    verdict = None
    if not reasons:
        verdict = msa.device_verdict(shape_adjusted(kept, shape_bounds_by_qubit), count)
    return {
        "eligible": sorted(eligible),
        "pool": sorted(pool),
        "selected": sorted(kept),
        "settle_veto": veto,
        "shape_bounds": {str(q): shape_bounds_by_qubit[q] for q in sorted(kept)},
        "count_rule": count,
        "withheld": reasons or None,
        "device": verdict,
    }
