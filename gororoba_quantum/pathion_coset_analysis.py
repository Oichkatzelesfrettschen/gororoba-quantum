"""Scoring of a Tuna-17 coset-block series: contrast statistics, the preregistered decision rules and the series reader.

A coset-block acquisition returns shot lists for arm pairs (plus and minus orientation of one routed circuit) whose
outcome index y + 8 s carries the three data bits d0, d1, d2 and the selector s. This module turns those shots into
c(y), the ratio c(y) / V, the visibility V and the nullity estimate N_hat with delta-method standard errors, and
applies the decision rules to them. Every function takes its inputs explicitly (counts, ideal contrast signs, design
standard errors, reference tables, template names, the series reader's `load_run`); the experiment definitions, the
shot budgets and the retained IBM records stay in the case scripts that call it
(scripts/qi_pathion_coset_block_cases.py and scripts/qi_pathion_coset_coin_cases.py).

Rule constants. Z_RESOLVE is the resolution in standard errors. A null "holds" and a cross-platform bin "within"
accept a departure from zero up to Z_RESOLVE standard errors, so a noisier run accepts a wider departure; each such
verdict therefore also requires the measured standard error to stay within PRECISION_FACTOR times the design standard
error (the precision floor), and a verdict whose precision fails reads "uninformative". CROSS_BINS_MIN of the 8 bins
must lie within Z_RESOLVE combined standard errors of the measured IBM ratio for the cross-platform rule to hold, and
CROSS_STATISTIC names the Tuna statistic it decides on. CONTROL_FLOOR_FACTOR bounds an emulator control arm's total
variation distance in units of the sampling floor.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import numpy as np

import pathion_coset_block as pcb
import pathion_kernel_map as pkm
import qi_records

Z_RESOLVE = 3.0
PRECISION_FACTOR = 2.0
# The cross-platform rule decides on the readout-corrected Tuna ratio c(y) / V: a device that contracts every bin
# alike and then misassigns each bit reads a raw ratio that departs from the ideal sign by its assignment asymmetry,
# which the correction from the series' own readout circuits removes.
CROSS_STATISTIC = "readout_corrected"
CROSS_BINS_MIN = 7
# A control arm passes when its total variation distance to the ideal law of record stays within this factor of the
# sampling floor expected under that law.
CONTROL_FLOOR_FACTOR = 2.0
Z_EXACT = 1.0e6
DETERMINISTIC_MIN_COUNT = math.ceil(-math.log(0.5 * math.erfc(Z_RESOLVE / math.sqrt(2.0))) / math.log(4.0))


def bit(shot: str, qubit: int) -> int:
    """Bit of `qubit` in a shot string that puts qubit 0 at the rightmost character."""
    return int(shot[len(shot) - 1 - qubit])


def confusion(readout: list[tuple[float, float]]) -> np.ndarray:
    """Joint assignment matrix over the logical bits: row = measured, column = true, bit v of the index."""
    matrix = np.ones((1, 1))
    for e01, e10 in reversed(readout):
        matrix = np.kron(matrix, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    return matrix


def contrast_vector(c: np.ndarray, sign: np.ndarray) -> np.ndarray:
    """c(y), c / V, V and N_hat = (sum of c) / (2 V) of the 8 per-bin contrasts, V the mean of c times the ideal sign.

    A zero V leaves c / V and N_hat undefined; they read as non-finite numbers here and as null in the record."""
    v = float(np.mean(c * sign))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.concatenate([c, c / v, [v, c.sum() / 2.0 / v]])


def visibility_gap(c: np.ndarray, sign: np.ndarray) -> dict[str, Any]:
    """Split N_hat - N of contrast_vector's estimator into a bin-count weight and a measured visibility gap.

    With B+ and B- the bins whose ideal sign is +1 and -1, V+ the mean of c over B+, V- the mean of -c over B-, and
    V the signed mean of c, N_hat - N = (|B+| |B-| / |B|) (V+ - V-) / V exactly for any c with V != 0, where
    N = (|B+| - |B-|) / 2 is the ideal half-sum. The gap V+ - V- is the measured difference between the visibilities
    of the bins whose pairs are aligned and those whose pairs are not. A block whose bins all carry one sign (every
    pair aligned, |B-| = 0) has weight 0, so its N_hat equals N whatever the device returned, and only its V and bin
    signs carry measurement."""
    if sign.size == 0 or c.shape != sign.shape:
        raise ValueError("contrasts and ideal signs need one entry per bin and at least one bin")
    if not np.all(np.abs(sign) == 1.0):
        raise ValueError("every bin needs an ideal sign of +1 or -1")
    plus, minus = sign > 0, sign < 0
    n_plus, n_minus = int(plus.sum()), int(minus.sum())
    v = float(np.mean(c * sign))
    v_plus = float(np.mean(c[plus])) if n_plus else math.nan
    v_minus = float(np.mean(-c[minus])) if n_minus else math.nan
    weight = n_plus * n_minus / sign.size
    gap = v_plus - v_minus if n_plus and n_minus else 0.0
    return {
        "nullity_ideal": (n_plus - n_minus) / 2.0,
        "nullity_estimate": float(c.sum()) / 2.0 / v if v else math.nan,
        "visibility": v,
        "visibility_bright": v_plus,
        "visibility_dark": v_minus,
        "weight": weight,
        "bias": weight * gap / v if v else math.nan,
        "fixed_by_signs": n_plus == 0 or n_minus == 0,
    }


def pile_vector(plus: np.ndarray, minus: np.ndarray, sign: np.ndarray) -> np.ndarray:
    """contrast_vector of two 16-outcome piles of counts; an empty pile leaves every statistic undefined."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return contrast_vector(pcb.output_contrast(plus / plus.sum(), minus / minus.sum()), sign)


def finite_or_none(value: Any) -> float | None:
    """A float for a finite number and None for nan or an infinity, so a record stays RFC 8259 JSON."""
    number = float(value)
    return number if math.isfinite(number) else None


def pack_statistics(base: np.ndarray, se: np.ndarray) -> dict[str, Any]:
    """The statistics record of a contrast vector and its delta-method errors; a value that is not finite and the
    error of such a value are null."""
    error = [finite_or_none(e) if math.isfinite(b) else None for b, e in zip(base, se, strict=True)]
    return {
        "c": [finite_or_none(v) for v in base[:8]],
        "c_se": error[:8],
        "ratio": [finite_or_none(v) for v in base[8:16]],
        "ratio_se": error[8:16],
        "visibility": finite_or_none(base[16]),
        "visibility_se": error[16],
        "nullity_estimate": finite_or_none(base[17]),
        "nullity_se": error[17],
    }


def contrast_outputs(counts: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None) -> np.ndarray:
    """c(y) of the 8 bins, c / V, V and the nullity estimate N_hat from stacked [plus, minus] counts of 16 outcomes.

    V is the mean of c times the ideal sign and N_hat = (sum of c) / (2 V); `matrix`, when given, is the joint
    assignment matrix the counts are corrected with first."""
    plus, minus = counts[:16], counts[16:]
    if matrix is not None:
        plus, minus = np.linalg.solve(matrix, plus), np.linalg.solve(matrix, minus)
    return pile_vector(plus, minus, sign)


def contrast_statistics(
    plus: np.ndarray, minus: np.ndarray, sign: np.ndarray, matrix: np.ndarray | None = None
) -> dict[str, Any]:
    """c(y), c / V, V and N_hat of an arm pair with standard errors by the delta method.

    The counts of each arm are multinomial, so the covariance is N (diag p - p p^T) per arm; the Jacobian of
    contrast_outputs is a central difference of one count, which is deterministic and needs no random draw."""
    x = np.concatenate([plus, minus]).astype(float)
    base = contrast_outputs(x, sign, matrix)
    jac = np.empty((base.size, x.size))
    for i in range(x.size):
        up, down = x.copy(), x.copy()
        up[i] += 1.0
        down[i] -= 1.0
        jac[:, i] = (contrast_outputs(up, sign, matrix) - contrast_outputs(down, sign, matrix)) / 2.0
    cov = np.zeros((x.size, x.size))
    for low, arm in ((0, plus), (16, minus)):
        p = arm / arm.sum()
        cov[low : low + 16, low : low + 16] = arm.sum() * (np.diag(p) - np.outer(p, p))
    with np.errstate(invalid="ignore"):
        se = np.sqrt(np.einsum("ij,jk,ik->i", jac, cov, jac))
    return pack_statistics(base, se)


class ContrastTask:
    """contrast_statistics of one (plus, minus, sign, matrix) tuple; a module-level callable for the pool."""

    def __call__(self, item: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray | None]) -> dict[str, Any]:
        plus, minus, sign, matrix = item
        return contrast_statistics(plus, minus, sign, matrix)


def cross_platform(
    statistics: dict[str, Any],
    labels: list[int],
    reference: dict[str, Any],
    z_limit: float = Z_RESOLVE,
    design_se: list[float] | None = None,
) -> dict[str, Any]:
    """D(y) = c_T(y) / V_T - c_I(label(y)) / V_I on the 8 bins of a Tuna block, against one IBM device.

    `labels` is the block's algebra index of each bin (the case's label table), `reference` one operand's entry of
    an IBM reference table; the Tuna side carries its delta-method error, the IBM side the replica spread, and the
    bins are compared at the quadrature sum. A bin whose Tuna ratio or error is undefined (null) is never within.
    The prediction is D = 0 within z_limit combined standard errors on at least CROSS_BINS_MIN of the 8 bins;
    `z_of_mean` reports the same difference against the standard error of the IBM mean instead of its spread.

    `design_se`, when given, is the design combined standard error of each bin: a bin then counts as within only
    when its combined standard error is at most PRECISION_FACTOR times its design value (the precision floor of
    the module docstring), `precise` lists that test per bin and `bins_within_unfloored` the count without it."""
    ibm = [reference["labels"][label] for label in labels]
    tuna = statistics["ratio"]
    difference: list[float | None] = []
    se: list[float | None] = []
    z: list[float | None] = []
    z_mean: list[float | None] = []
    for t, t_se, i in zip(tuna, statistics["ratio_se"], ibm, strict=True):
        if t is None or t_se is None:
            difference.append(None)
            se.append(None)
            z.append(None)
            z_mean.append(None)
            continue
        d, combined = t - i["ratio"], math.hypot(t_se, i["se"])
        difference.append(d)
        se.append(combined)
        z.append(float(z_score(d, combined)))
        z_mean.append(float(z_score(d, math.hypot(t_se, i["se_mean"]))))
    inside = [v is not None and abs(v) <= z_limit for v in z]
    out: dict[str, Any] = {
        "labels": list(labels),
        "tuna_ratio": list(tuna),
        "ibm_ratio": [i["ratio"] for i in ibm],
        "ibm_coset": [i["coset"] for i in ibm],
        "difference": difference,
        "se": se,
        "z": z,
        "z_of_mean": z_mean,
        "bins_within": int(sum(inside)),
    }
    if design_se is not None:
        precise = [e is not None and e <= PRECISION_FACTOR * d for e, d in zip(se, design_se, strict=True)]
        out["design_se"] = [float(d) for d in design_se]
        out["precise"] = precise
        out["bins_within_unfloored"] = out["bins_within"]
        out["bins_within"] = int(sum(a and b for a, b in zip(inside, precise, strict=True)))
    return out


def refutation_probability(difference: list[float], se: list[float], tuna_se: list[float]) -> float:
    """Probability that a device obeying the model reads fewer than CROSS_BINS_MIN of 8 bins inside Z_RESOLVE
    combined standard errors, by exact enumeration of the independent bins.

    Each bin reads D ~ Normal(difference, tuna_se) around the predicted difference, because the IBM ratio is a
    fixed measured number; a bin fails when |D| exceeds Z_RESOLVE * se."""

    def cdf(x: float) -> float:
        return 0.5 * math.erfc(-x / math.sqrt(2.0))

    fail = [
        cdf((-Z_RESOLVE * s - d) / t) + cdf((-Z_RESOLVE * s + d) / t)
        for d, s, t in zip(difference, se, tuna_se, strict=True)
    ]
    # Poisson-binomial law of the number of failing bins; the rule holds up to len(fail) - CROSS_BINS_MIN of them.
    law = np.array([1.0])
    for q in fail:
        law = np.convolve(law, [1.0 - q, q])
    return float(law[len(fail) - CROSS_BINS_MIN + 1 :].sum())


def outcome_counts(shots: list[str], roles: dict[str, int]) -> np.ndarray:
    """Counts over the logical outcome index y + 8 s read from the physical qubits of `roles`."""
    counts = np.zeros(16)
    keys = ("d0", "d1", "d2", "selector")
    for shot in shots:
        counts[sum(bit(shot, roles[k]) << v for v, k in enumerate(keys))] += 1
    return counts


def bin_contrast(plus: np.ndarray, minus: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """c(y) and its standard error from counts (conditional P(s = 0 | y) of each arm, binomial error)."""
    values = np.zeros(8)
    errors = np.zeros(8)
    for y in range(8):
        var = 0.0
        for counts, sign in ((plus, 1.0), (minus, -1.0)):
            n = counts[y] + counts[y + 8]
            p = counts[y] / n if n else 0.5
            values[y] += sign * p
            var += p * (1 - p) / max(n, 1.0)
        errors[y] = math.sqrt(var)
    return values, errors


def selector_stat(plus: np.ndarray, minus: np.ndarray) -> tuple[float, float]:
    n_plus, n_minus = plus.sum(), minus.sum()
    p, m = float(plus[:8].sum() / n_plus), float(minus[:8].sum() / n_minus)
    return p - m, math.sqrt(p * (1 - p) / n_plus + m * (1 - m) / n_minus)


def z_score(value: Any, error: Any) -> Any:
    """value / error, elementwise; a statistic with no sampling variance (an emulator bin whose counts are all one
    outcome) reads +-Z_EXACT in the direction of its sign and 0 at zero, so a record stays finite JSON."""
    value, error = np.asarray(value, dtype=float), np.asarray(error, dtype=float)
    safe = np.where(error > 0, error, 1.0)
    return np.where(error > 0, value / safe, np.sign(value) * Z_EXACT)


def signed_z(c: float, se: float, sign: float, n_min: float = math.inf) -> float:
    """Contrast c along the ideal sign in standard errors.

    A bin whose sampled selector outcomes are deterministic in both arms has se 0 and decides by an exact sign
    match: +inf when c carries the ideal sign, -inf when it carries the opposite sign, 0 when c or the ideal sign
    is zero. A deterministic bin counts only when each arm holds at least DETERMINISTIC_MIN_COUNT shots in it
    (`n_min` is the smaller arm count): two arms that share one selector probability q give a matching
    deterministic pair with probability at most max_q q^n (1 - q)^n = 4^-n, and n = DETERMINISTIC_MIN_COUNT is
    the least n at which that bound falls to the one-sided normal tail of Z_RESOLVE. A deterministic bin below
    that count decides nothing (0), since a chance run of one outcome is not a resolved contrast."""
    along = c * sign
    if se > 0:
        return along / se
    if n_min < DETERMINISTIC_MIN_COUNT:
        return 0.0
    return math.inf if along > 0 else -math.inf if along < 0 else 0.0


def ratio_or_none(value: float, se: float) -> float | None:
    """value / se for a report, None when se is 0 (a deterministic statistic has no finite z)."""
    return value / se if se > 0 else None


def pattern_bins(ideal_a: np.ndarray, ideal_b: np.ndarray) -> list[int]:
    """The preregistered pattern bins: those where the two templates' ideal contrasts carry opposite signs."""
    return [y for y in range(len(ideal_a)) if np.sign(ideal_a[y]) * np.sign(ideal_b[y]) < 0]


def bin_scores(plus: np.ndarray, minus: np.ndarray, ideal_c: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """c(y), its standard error and the signed z of each of the 8 bins of one template's pooled arm counts.

    `plus` and `minus` are 16-outcome counts indexed y + 8 s; the signed z is signed_z along the sign of the
    template's ideal contrast with the smaller arm count of the bin as the deterministic-bin floor."""
    c, se = bin_contrast(plus, minus)
    sign = np.sign(ideal_c)
    z = [
        signed_z(float(c[y]), float(se[y]), float(sign[y]), float(min(plus[y] + plus[y + 8], minus[y] + minus[y + 8])))
        for y in range(8)
    ]
    return c, se, z


def pattern_decision(ideal_a: np.ndarray, ideal_b: np.ndarray, z_a: list[float], z_b: list[float]) -> dict[str, Any]:
    """The pattern rule: the two blocks read opposite signs in every bin where their ideal contrasts do, each at
    Z_RESOLVE along its own ideal sign (z_a and z_b are the templates' signed z per bin)."""
    differing = pattern_bins(ideal_a, ideal_b)
    z = [max(min(z_a[y], z_b[y]), 0.0) for y in differing]
    return {
        "bins": differing,
        "z": [None if math.isinf(v) else v for v in z],
        "resolved": bool(differing) and all(v >= Z_RESOLVE for v in z),
    }


def null_decision(contrast: float, se: float, design_se: float) -> dict[str, Any]:
    """The null rule: the contrast lies within Z_RESOLVE standard errors of zero at a standard error no worse than
    PRECISION_FACTOR times `design_se`. A contrast within the limit at a coarser standard error is "uninformative",
    which holds nothing; "outcome" is holds, fails or uninformative."""
    informative = se <= PRECISION_FACTOR * design_se
    within = bool(abs(contrast) <= Z_RESOLVE * se)
    return {
        "z": ratio_or_none(contrast, se),
        "se": se,
        "design_se": design_se,
        "informative": informative,
        "outcome": "uninformative" if not informative else "holds" if within else "fails",
        "holds": informative and within,
    }


def cocycle_free_decision(xor_contrast: float, xor_se: float, ba_contrast: float, ba_se: float) -> dict[str, Any]:
    """The cocycle-free rule: the xor_ba selector contrast is negative and the ba selector contrast positive, each
    at Z_RESOLVE standard errors. Both signs are strict, so a zero contrast with zero standard error resolves
    nothing."""
    return {
        "xor_z": ratio_or_none(xor_contrast, xor_se),
        "ba_z": ratio_or_none(ba_contrast, ba_se),
        "resolved": bool(
            xor_contrast < 0
            and ba_contrast > 0
            and xor_contrast <= -Z_RESOLVE * xor_se
            and ba_contrast >= Z_RESOLVE * ba_se
        ),
    }


def cell_outcome(cell: dict[str, Any]) -> str:
    """holds, uninformative or fails for one template against one device; "not read" without readout circuits.

    A cell is uninformative when the bins within Z_RESOLVE would reach CROSS_BINS_MIN but too few meet the
    precision floor."""
    if not cell["read"]:
        return "not read"
    ratio = cell[CROSS_STATISTIC]
    if ratio["bins_within"] >= CROSS_BINS_MIN:
        return "holds"
    return "uninformative" if ratio["bins_within_unfloored"] >= CROSS_BINS_MIN else "fails"


def combined_outcome(outcomes: list[str]) -> str:
    """not read if any member is unread, else fails if any fails, else uninformative if any is, else holds."""
    for name in ("not read", "fails", "uninformative"):
        if name in outcomes:
            return name
    return "holds" if outcomes else "not read"


def cross_decision(
    templates: dict[str, Any],
    labels: dict[str, Any],
    ibm: dict[str, dict[str, Any]],
    statistic: Any,
    design: dict[str, Any],
    scale: dict[str, float],
    primary: tuple[str, ...],
) -> dict[str, Any]:
    """The cross-platform rule over the `primary` templates against each IBM device.

    `statistic(name)` supplies a template's statistics (raw and readout-corrected ratio tables) or None when it
    cannot be read, `labels` is the manifest's label table, and the CROSS_STATISTIC ratio meets its precision floor
    against `design` scaled per template by `scale`."""
    devices: dict[str, Any] = {}
    for device, reference in ibm.items():
        per_template: dict[str, Any] = {}
        for name in primary:
            stats = statistic(name)
            if stats is None:
                per_template[name] = {"read": False}
                continue
            bins = labels[templates[name]["block"]]["ibm_data_index_of_bin"]
            tag = pkm.operand_tag(tuple(templates[name]["operand"]))
            floor = [v * scale[name] for v in design["cross_se"][device][name]]
            per_template[name] = {
                "read": True,
                **{
                    s: cross_platform(v, bins, reference[tag], design_se=floor if s == CROSS_STATISTIC else None)
                    for s, v in stats.items()
                },
            }
        for cell in per_template.values():
            cell["outcome"] = cell_outcome(cell)
        devices[device] = {
            "templates": per_template,
            "holds": all(
                v["read"] and v[CROSS_STATISTIC]["bins_within"] >= CROSS_BINS_MIN for v in per_template.values()
            ),
            "outcome": combined_outcome([c["outcome"] for c in per_template.values()]),
        }
    return {
        "statistic": CROSS_STATISTIC,
        "bins_min": CROSS_BINS_MIN,
        "precision_factor": PRECISION_FACTOR,
        "devices": devices,
        "holds": bool(devices) and all(d["holds"] for d in devices.values()),
        "outcome": combined_outcome([d["outcome"] for d in devices.values()]),
    }


def design_from_prediction(
    prediction: dict[str, Any], rho_band: tuple[float, float], devices: Iterable[str]
) -> dict[str, Any]:
    """Design standard errors of a case's prediction.json: per template the selector error and per `devices` entry
    and primary template the combined error of each of the 8 bins, each the larger of the two `rho_band` ends.

    The values hold at the forecast's shots; design_scale gives the factor for a run of other length."""
    rho_keys = [f"rho_{rho}" for rho in rho_band]
    cross = prediction["cross_platform"]["templates"]
    return {
        "selector_se": {
            name: max(cell[k]["selector_se"] for k in rho_keys) for name, cell in prediction["templates"].items()
        },
        "cross_se": {
            device: {
                name: [max(cell[device][k][CROSS_STATISTIC]["se"][y] for k in rho_keys) for y in range(8)]
                for name, cell in cross.items()
            }
            for device in devices
        },
    }


def scale_design(design: dict[str, Any], factor: float) -> dict[str, Any]:
    """`design` with every standard error multiplied by `factor` (a run's design at other shots, or a test's)."""
    return {
        "selector_se": {name: v * factor for name, v in design["selector_se"].items()},
        "cross_se": {
            device: {name: [v * factor for v in values] for name, values in per.items()}
            for device, per in design["cross_se"].items()
        },
    }


def design_scale(forecast_shots: int, run_shots: int) -> float:
    """Factor from the design standard errors of a forecast at `forecast_shots` to a run of `run_shots`: sampling
    errors scale with the inverse root of the shots (an upper bound on the combined error, whose IBM replica
    spread does not shrink with the run)."""
    return math.sqrt(forecast_shots / run_shots)


def read_series(
    run_dirs: list[Path],
    case_root: Path | None,
    series_of: Any,
    data_kind: str,
    ignored: tuple[str, ...],
    load_run: Callable[[Path, Path | None], dict[str, Any]],
) -> dict[str, Any]:
    """The collected batches of one series, each read through qi_records (receipt, circuit, batch and job
    identities, raw shots against the recorded histogram) and then through `load_run(run_dir, case_batch)`, which
    binds the batch to the series case (qi_pathion_coset_block_series.load_run).

    A job that did not complete, a batch listed twice or run directories that describe different series raise
    ValueError. Returns the series fields shared by every batch (`ignored` are the per-batch keys left out of that
    comparison), the shot lists and provider start times keyed "batch/file", the sha256 of each batch's cases.json,
    and the (shots, roles, ideal law) of every circuit of kind `data_kind`."""
    shared: dict[str, Any] | None = None
    shots: dict[str, list[str]] = {}
    executed: dict[str, str] = {}
    digests: dict[str, str] = {}
    arms: dict[str, tuple[list[str], dict[str, int], list[float]]] = {}
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        acquisition = qi_records.read_run(run_dir, str(run_dir))
        if not acquisition.completed:
            raise ValueError(f"{run_dir}: a job did not complete: {dict(acquisition.statuses)}")
        case_batch = None if case_root is None else case_root / series_of(run_dir) / f"batch-{run_dir.name[-2:]}"
        run = load_run(run_dir, case_batch)
        cases = run["cases"]
        fields = {k: v for k, v in cases.items() if k not in ignored}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise ValueError(f"{run_dir}/cases.json describes a different series")
        if cases["batch"] in digests:
            raise ValueError(f"{run_dir}: batch {cases['batch']} appears twice")
        digests[cases["batch"]] = hashlib.sha256((run_dir / "cases.json").read_bytes()).hexdigest()
        for row in cases["circuits"]:
            key = f"{cases['batch']}/{row['file']}"
            shots[key] = run["shots"][row["file"]]
            executed[key] = run["jobs"][row["file"]]["queued_at"]
            if row["kind"] == data_kind:
                arms[key] = (shots[key], cases["templates"][row["template"]]["roles"], row["ideal"])
    if shared is None:
        raise ValueError("an analysis needs its run directories")
    return {"shared": shared, "shots": shots, "executed": executed, "digests": digests, "arms": arms}


def control_floor(law: np.ndarray, shots: int) -> float:
    """Expected total variation distance of `shots` draws from `law`: the sum of the mean absolute deviations
    sqrt(2 p (1 - p) / (pi N)) of each outcome, halved."""
    return float(0.5 * np.sum(np.sqrt(2.0 * law * (1.0 - law) / (math.pi * shots))))


def control_report(
    arms: dict[str, tuple[list[str], dict[str, int], list[float]]],
    counts_of: Callable[[list[str], dict[str, int]], np.ndarray],
) -> dict[str, Any]:
    """Each arm's observed law against its ideal law of record at CONTROL_FLOOR_FACTOR times the sampling floor.

    `arms` maps "batch/file" to (shots, roles, ideal law) and `counts_of(shots, roles)` counts the shots over the
    outcomes of the ideal law (outcome_counts for the 16-outcome block arms); the verdict is the emulator dry run's
    preregistered pass."""
    report: dict[str, Any] = {}
    for key, (listed, roles, ideal) in sorted(arms.items()):
        counts = counts_of(listed, roles)
        law = np.array(ideal)
        tvd = 0.5 * float(np.abs(counts / counts.sum() - law).sum())
        floor = control_floor(law, len(listed))
        report[key] = {"tvd": tvd, "floor": floor, "ok": tvd <= CONTROL_FLOOR_FACTOR * floor}
    return {
        "arms": report,
        "factor": CONTROL_FLOOR_FACTOR,
        "pass": bool(report) and all(v["ok"] for v in report.values()),
    }
