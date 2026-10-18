"""Exploratory line-phase-bin analysis of the retained Tuna-17 ladder series.

box_kite_analysis.analyze_ladder reads each Latin job's shots as one block,
so a 50 Hz modulation of the selectors enters the job-averaged rho = r_coh /
r_pop. This script reads the same raw shots and the same estimators
(box_kite_analysis.follow_items, follow_sample, follow_values with the
bracket readout correction) after splitting every Latin job into line-phase
bins, and answers two questions the ladder analysis leaves open. Every rule
here was chosen after the data were read; the record is exploratory and binds
only a future run.

rho per bin:
- binning: a job's line frequency f is the scan peak in the manifest's band
  (box_kite_analysis.LineScan), or half the peak in the doubled band when only
  that band detects, since a selector at an extremum of its response follows
  the line at 2 f alone; each band is tested at line_detection_p / 2, so the
  two searches keep the manifest's level. The phase is the depth-9 selector's
  first-harmonic lock-in phase (box_kite_analysis.lockin), and shot t falls in
  bin box_kite_analysis.line_phase_bin_index, bin 0 at the depth-9 selector's
  P1 peak. The ladder's phase_binned_contrast uses the same bins.
- cells: for every X-setting replica, the joint (a, d) counts of each bin and
  of all shots. Each cell enters follow_sample as an LCU item whose
  multinomial has the cell's own shot count, so the bracket draws stay shared
  and the cell draws stay independent. The stationary bins 0 and bins / 2 are
  the extrema of the fitted line, where the first-order modulation of a
  selector's P1 vanishes within a bin; their estimates average in ln rho,
  since pooling the counts of a peak and a trough mixes two states and
  restores the covariance of the modulation with the decay that the job
  average carries.
- estimator: per pair and X batch, rho = exp(slope ln J - slope ln C) over CZ
  depths 1, 5, 9 with J = Pc |E_0| and C = 2 Pc - 1, the ladder's estimator.
  The pair's combined value averages ln rho over the X batches row by row, so
  the shared bracket draws correlate the batches.
- readings: a stationary interval above 1 at the manifest's 99% percentiles
  leaves averaging over the line unable to explain rho > 1; an interval
  holding 1 where the job average lies above 1 puts the excess in the
  modulation's covariance with the decay. The "bin_mean" cell averages ln rho
  over all bins, the phase-resolved counterpart of the job average. A batch
  whose job's depth-9 selector carries no significant first harmonic takes its
  bin reference from noise, so its stationary cells average over random
  phases, and a job whose scan peak misses line_detection_p takes its
  frequency from noise. The other depths' selectors share the reference
  phase only up to their own response: harmonic h of a selector with phase
  phi_h puts its extrema at line phase offset wrap(phi_h - h phi_ref) / h,
  wrapped to [-pi/2, pi/2) before the division, and a significant harmonic
  whose offset exceeds a quarter bin, pi / (2 bins), by more than
  amplitude_sigmas phase standard errors moves that selector's P1 to first
  order inside the stationary bins. "reference_significant" marks the
  pair-batches free of all three. The stationary verdict and the job-average verdict the reading
  compares it with combine those batches alone, so both read the same
  observations; the all-batch combinations are reported as
  stationary_all_verdict and job_average_all_verdict. An undetected job's
  harmonic rules read undetermined.
- intervals: conditional on each job's fitted line frequency and phase. The
  bootstrap redraws the cells' counts with the bins fixed; it does not
  repeat the scan or the lock-in, so the uncertainty of the bin reference
  is outside the intervals.
- streams: numpy seed [bootstrap_seed, LINE_BINS_SEED], distinct from the
  ladder's [bootstrap_seed] and [bootstrap_seed, LADDER_LINE_SEED]; the
  readout-iso-x alternative uses [bootstrap_seed, LINE_BINS_SEED,
  LADDER_LINE_SEED].

Harmonics at 2 f:
- per Latin job and depth, the first-harmonic (at f) and second-harmonic (at
  2 f) amplitudes of the depth's selector with the lock-in standard error
  sqrt(2 p (1 - p) / n) of box_kite_analysis.lockin.
- the statistic max(A1, A2) at depth 9 over depth 1, tested like the ladder's
  depth_growth: the difference exceeds amplitude_sigmas times the quadrature
  sum of the two standard errors. A selector at an extremum of its response
  carries a vanishing A1 and a second harmonic, so the maximum keeps it. The
  max rule's standard error is the bootstrap standard deviation of the
  depth difference of max(A1, A2), each draw repeating the selection on
  coefficients drawn jointly (numpy seed [bootstrap_seed, LINE_BINS_SEED,
  MAX_RULE_SEED]): the depth-9 and depth-1 selectors read the same shot rows,
  so their eight lock-in coefficients (cos and sin at f and 2 f) come from
  one multivariate normal whose covariance is the residual shot covariance of
  the two selectors times the centered Gram matrix of the lock-in weights.
  The maximum of two amplitudes is biased upward by the Rice law of a noisy
  amplitude; the margin test compares depth 9 with depth 1 on the same
  statistic, so the bias enters both terms.

--out FILE writes the record, --check FILE recomputes it from its listed runs
and compares bytes, --self-test first checks the joint coefficient draw (two
selectors with the same shot noise give a max-rule SD of 0, and a correlated
pair with a strong line reproduces the SD of independent realizations, which
the draw with the selectors' noise made independent misses) and the matched
verdicts (an excluded batch that flips the all-batch job average leaves the
reading on the clean one), then runs synthetic ladders: a line that modulates
the selector population with rho = 1 in the stationary bins, a coherent
population error that raises rho in every bin, and a selector at an extremum of
its response, a line that only the doubled band carries, a depth-5 selector a
quarter period off the reference phase, and a series without a line, whose
phase rules read undetermined; it then rejects a corrupted raw digest, an altered bin count and
an altered raw file.

Usage: "$PYTHON" scripts/qi_ladder_line_bins.py (--out FILE | --check FILE | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import box_kite_analysis as box  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "qi-ladder-line-bins-v1"
LINE_BINS_SEED = 2
MAX_RULE_SEED = 3
LADDER_RECORD = ROOT / "results/quantum_inspire/box_kite_tuna_17_ladder_analysis.json"
LINE_BINS_RECORD = ROOT / "results/quantum_inspire/box_kite_tuna_17_ladder_line_bins.json"
FAMILY = "tuna_ladder"
POST_HOC = [
    "the line-phase-bin cells (every bin, and the stationary pair of bins 0 and bins / 2 combined in ln rho) were "
    "chosen after the ladder analysis showed rho above 1 on every pair",
    "the max(A1, A2) rule and its depth-9 over depth-1 margin test were chosen after the first-harmonic test "
    "read zero at an extremum of a selector's response in batches 4 and 5",
    "the clean-reference restriction was chosen after the depth-9 first harmonic of (12,14) fell to noise in batch 4",
    "the doubled-band scan and the quarter-bin phase alignment of every significant harmonic were added after the "
    "record was read; on the retained jobs neither moves a detection or a clean batch",
]


# ---------------------------------------------------------------- loading


def rel(path: Path, base: Path) -> str:
    return box.relative(path, base)


def load(runs: list[Path], base: Path, cases_root: Path) -> tuple[dict[str, Any], dict[str, Any], list[Path]]:
    """The tuna_ladder batches among the runs, their thresholds and the run directories kept."""
    loaded = [box.load_batch(run, base, cases_root) for run in runs]
    kept = [(run, b) for run, b in zip(runs, loaded, strict=True) if b["family"] == FAMILY]
    if not kept:
        box.fail("no tuna_ladder run among the listed runs")
    batches, missing = box.stage_batches([b for _, b in kept], FAMILY, cases_root)
    if missing:
        box.fail(f"the ladder series lacks {missing}")
    return batches, box.thresholds_of(batches), [run for run, _ in kept]


def input_digests(runs: list[Path], base: Path) -> dict[str, Any]:
    out = {}
    for run in runs:
        raw = {p.name: box.sha256(p.read_bytes()) for p in sorted((run / "raw").glob("*.json"))}
        out[rel(run, base)] = {"cases_sha256": box.sha256((run / "cases.json").read_bytes()), "raw_sha256": raw}
    return out


# ---------------------------------------------------------------- per-job work


class JobWork:
    """One Latin job: harmonics of each depth's selector at f and 2 f, and per-replica joint counts by bin."""

    def __init__(self, bins: int, depths: list[int]):
        self.bins, self.depths = bins, depths

    def __call__(self, job: dict[str, Any]) -> dict[str, Any]:
        bits, f = job["bits"], job["frequency"]
        selectors = [job["selector"][n] for n in self.depths]
        first = dict(zip(self.depths, box.lockin(bits, f, selectors), strict=True))
        second = dict(zip(self.depths, box.lockin(bits, 2 * f, selectors), strict=True))
        index = box.line_phase_bin_index(bits.shape[0], f, first[max(self.depths)]["phase"], self.bins)
        counts = []
        for a, d in job["pairs"]:
            code = 2 * bits[:, a].astype(np.int64) + bits[:, d]
            counts.append(np.bincount(index * 4 + code, minlength=self.bins * 4).reshape(self.bins, 4))
        rule_depths = (max(self.depths), min(self.depths))
        joint = coefficient_model(bits[:, [job["selector"][n] for n in rule_depths]], f)
        for j, n in enumerate(rule_depths):
            for h, lock in ((0, first[n]), (1, second[n])):
                if abs(math.hypot(*joint["coefficients"][j][2 * h : 2 * h + 2]) - lock["amplitude"]) > 1e-9:
                    box.fail(f"depth {n}: the joint coefficients differ from box_kite_analysis.lockin")
        return {"first": first, "second": second, "counts": counts, "joint": joint}


def coefficient_model(x: np.ndarray, f: float) -> dict[str, Any]:
    """Lock-in coefficients (cos f, sin f, cos 2f, sin 2f) of each column and their joint shot-noise covariance.

    Each coefficient is P_k (x - mean x) with P the per-harmonic least-squares rows of box_kite_analysis.lockin,
    so for shots independent in time with a per-shot column covariance S the covariance of coefficient k of
    column j and coefficient l of column i is S_ji K_kl, K = P P^T - (P 1)(P 1)^T / n. S is the residual
    covariance after both harmonics are removed, so a line shared by the columns enters the coefficients and
    leaves the noise. Sums run elementwise, independent of the BLAS build.
    """
    x = x.astype(np.float64)
    n = x.shape[0]
    t = np.arange(n) - (n - 1) / 2
    rows, design = [], []
    for frequency in (f, 2 * f):
        c, s = np.cos(2 * np.pi * frequency * t), np.sin(2 * np.pi * frequency * t)
        cc, cs, ss = float(np.sum(c * c)), float(np.sum(c * s)), float(np.sum(s * s))
        det = cc * ss - cs * cs
        rows += [(ss * c - cs * s) / det, (cc * s - cs * c) / det]
        design += [c, s]
    xc = x - x.mean(axis=0)
    coefficients = [[float(np.sum(p * xc[:, j])) for p in rows] for j in range(x.shape[1])]
    residual = [xc[:, j] - sum(coefficients[j][k] * design[k] for k in range(4)) for j in range(x.shape[1])]
    sigma = [[float(np.sum(residual[i] * residual[j])) / n for j in range(x.shape[1])] for i in range(x.shape[1])]
    totals = [float(np.sum(p)) for p in rows]
    kernel = [[float(np.sum(rows[k] * rows[m])) - totals[k] * totals[m] / n for m in range(4)] for k in range(4)]
    return {"coefficients": coefficients, "sigma": sigma, "kernel": kernel}


def cholesky_psd(a: list[list[float]]) -> list[list[float]]:
    """Lower Cholesky factor of a positive semidefinite matrix.

    A pivot within 1e-12 of its diagonal entry is a singular direction to the precision of the sums, so it
    and the column below it are zero.
    """
    m = len(a)
    low = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1):
            rest = a[i][j] - sum(low[i][k] * low[j][k] for k in range(j))
            if i == j:
                low[i][i] = math.sqrt(rest) if rest > 1e-12 * a[i][i] else 0.0
            else:
                low[i][j] = rest / low[j][j] if low[j][j] > 0 else 0.0
    return low


def joint_max_draws(model: dict[str, Any], rng: np.random.Generator, draws: int) -> np.ndarray:
    """max(A1, A2) per draw and column with every column's four coefficients drawn jointly.

    The draw is coefficients + (chol S kron chol K) z with one standard normal 4-vector per column; the Kronecker
    factor keeps a singular S, two columns with the same shot noise, exact.
    """
    columns = len(model["coefficients"])
    z = rng.standard_normal((draws, columns * 4)).reshape(draws, columns, 4)
    low_s, low_k = cholesky_psd(model["sigma"]), cholesky_psd(model["kernel"])
    by_kernel = np.zeros((4, draws, columns))
    for k in range(4):
        for m in range(4):
            by_kernel[k] += low_k[k][m] * z[:, :, m]
    out = []
    for j in range(columns):
        drawn = []
        for k in range(4):
            noise = np.zeros(draws)
            for i in range(columns):
                noise += low_s[j][i] * by_kernel[k][:, i]
            drawn.append(model["coefficients"][j][k] + noise)
        out.append(np.maximum(np.hypot(drawn[0], drawn[1]), np.hypot(drawn[2], drawn[3])))
    return np.stack(out, axis=1)


def line_of(fundamental: dict[str, Any], doubled: dict[str, Any]) -> dict[str, Any]:
    """The job's line: the band's peak when the band detects, else half the doubled band's detected peak."""
    band: str | None
    if doubled["detected"] and not fundamental["detected"]:
        frequency, band, log10_p = doubled["cycles_per_shot"] / 2, "second", doubled["log10_p"]
    else:
        frequency, log10_p = fundamental.get("cycles_per_shot"), fundamental.get("log10_p")
        band = "first" if fundamental["detected"] else None
    return {
        "detected": band is not None,
        "line_band": band,
        "cycles_per_shot": frequency,
        "log10_p": log10_p,
        "log10_p_doubled_band": doubled.get("log10_p"),
    }


def phase_alignment(per_depth: dict[str, dict[str, Any]], reference_depth: int, sigmas: float, bins: int) -> None:
    """Each depth's significant harmonics' extremum offsets from the reference phase, and whether they align.

    Harmonic h of phase phi_h is extremal at line phase offset wrap(phi_h - h phi_ref) / h; the selector is
    aligned when every such offset lies within a quarter bin, pi / (2 bins), up to sigmas phase standard errors
    sqrt((se / A_h)^2 / h^2 + (se_ref / A_ref)^2). The reference's own first harmonic carries offset 0.
    """
    reference = per_depth[str(reference_depth)]
    tolerance = math.pi / (2 * bins)
    amplitude = reference["first"]["amplitude"]
    ref_phase_se = reference["se"] / amplitude if amplitude > 0 else math.inf
    for n, row in per_depth.items():
        offsets = []
        for h, key in ((1, "first"), (2, "second")):
            if (int(n), h) == (reference_depth, 1) or not row[key]["significant"]:
                continue
            psi = row[key]["phase"] - h * reference["first"]["phase"]
            offset = (psi + math.pi / 2) % math.pi - math.pi / 2
            se = math.sqrt((row["se"] / row[key]["amplitude"]) ** 2 / h**2 + ref_phase_se**2)
            offsets.append({"harmonic": h, "offset": offset / h, "se": se})
        row["phase_offsets"] = offsets
        row["aligned"] = None if not offsets else all(abs(o["offset"]) <= tolerance + sigmas * o["se"] for o in offsets)


def harmonic_entry(
    depths: list[int],
    selector: dict[int, int],
    work: dict[str, Any],
    sigmas: float,
    rng: np.random.Generator,
    draws: int,
    bins: int,
) -> dict[str, Any]:
    per_depth = {}
    for n in depths:
        a1, a2 = work["first"][n], work["second"][n]
        se = a1["se"]
        top = max(a1["amplitude"], a2["amplitude"])
        a1_row = {"amplitude": a1["amplitude"], "phase": a1["phase"]}
        a2_row = {"amplitude": a2["amplitude"], "phase": a2["phase"]}
        per_depth[str(n)] = {
            "qubit": selector[n],
            "first": {**a1_row, "significant": a1["amplitude"] > sigmas * se},
            "second": {**a2_row, "significant": a2["amplitude"] > sigmas * se},
            "se": se,
            "max_amplitude": top,
            "dominant": "first" if a1["amplitude"] >= a2["amplitude"] else "second",
        }  # fmt: skip
    phase_alignment(per_depth, max(depths), sigmas, bins)
    deep, shallow = per_depth[str(max(depths))], per_depth[str(min(depths))]
    margin_se = math.sqrt(deep["se"] ** 2 + shallow["se"] ** 2)

    def rule(deep_value: float, shallow_value: float, se: float) -> dict[str, Any]:
        difference = deep_value - shallow_value
        return {"difference": difference, "se": se, "holds": bool(difference > sigmas * se)}

    # The maximum of two Rice-distributed amplitudes has no closed-form error; its SE is the bootstrap
    # standard deviation of the depth difference with the harmonic selection repeated in every draw. Both
    # depths' selectors read the job's shot rows, so their eight coefficients are drawn jointly.
    boot = joint_max_draws(work["joint"], rng, draws)
    max_se = float(np.std(boot[:, 0] - boot[:, 1], ddof=1))
    return {
        "depths": per_depth,
        "first_harmonic_rule": rule(deep["first"]["amplitude"], shallow["first"]["amplitude"], margin_se),
        "max_rule": rule(deep["max_amplitude"], shallow["max_amplitude"], max_se),
    }


# ---------------------------------------------------------------- rho cells


def rho_log(v: box.Values, cell: dict[int, int], depths: list[int]) -> Any:
    """ln rho = slope ln J - slope ln C over the depths, per sample row, for the ladder's J and C."""

    def contrast(n: int) -> Any:
        return 2 * v["pc"][cell[n]] - 1

    def joint(n: int) -> Any:
        return v["pc"][cell[n]] * np.abs(v["e"][(cell[n], 0)])

    def slope(fn: Any) -> Any:
        return box.ols_slope(depths, [np.log(fn(n)) for n in depths])

    return slope(joint) - slope(contrast)


def verdict_of(interval: list[float] | None) -> str:
    if interval is None:
        return "undetermined"
    if interval[1] < 1:
        return "below 1"
    if interval[0] > 1:
        return "above 1"
    return "consistent with 1"


def combine(per_batch: list[Any], which: list[int], pct: list[float]) -> dict[str, Any]:
    """rho from ln rho averaged over the listed batches, row by row over the bootstrap draws."""
    with np.errstate(all="ignore"):
        lp = np.mean([per_batch[i][0] for i in which], axis=0)
        lb = np.mean([per_batch[i][1] for i in which], axis=0)
        return box.summary(np.exp(lp), np.exp(lb), pct)


def verdicts(job_average: list[Any], stationary: list[Any], clean: list[int], pct: list[float]) -> dict[str, Any]:
    """The job-average and stationary verdicts over the clean batches and over every batch, and the reading.

    The reading compares the two clean verdicts, so both rest on the same observations.
    """
    every = list(range(len(job_average)))
    clean_job = combine(job_average, clean, pct) if clean else None
    clean_stationary = combine(stationary, clean, pct) if clean else None
    out = {
        "job_average_clean": clean_job,
        "stationary_clean": clean_stationary,
        "job_average_verdict": verdict_of(None if clean_job is None else clean_job["interval"]),
        "job_average_all_verdict": verdict_of(combine(job_average, every, pct)["interval"]),
        "stationary_verdict": verdict_of(None if clean_stationary is None else clean_stationary["interval"]),
        "stationary_all_verdict": verdict_of(combine(stationary, every, pct)["interval"]),
    }
    if out["stationary_verdict"] == "above 1":
        out["reading"] = "averaging over the line does not explain rho above 1"
    elif out["stationary_verdict"] == "consistent with 1" and out["job_average_verdict"] == "above 1":
        out["reading"] = "averaging over the line explains the rho excess"
    else:
        out["reading"] = "undecided"
    return out


def iso_items(
    batches: dict[str, Any], brackets: list[dict[str, Any]], items: list[Any], iso: list[int]
) -> tuple[list[dict[str, Any]], list[Any]] | None:
    """The bracket list with the readout-iso-x brackets appended, and items whose iso qubits read their e10 there."""
    alternative = box.iso_brackets(batches, brackets, iso)
    if len(alternative) < 2:
        return None
    times = [b["time_e10"] for b in alternative]
    moved = []
    for item in items:
        near, far, weight = box.bracket_weight(box.job_time(batches[item["batch"]], item["file"]), times)
        e10 = (near + len(brackets), far + len(brackets), weight)
        roles = (item["replica"]["roles"]["selector"], item["replica"]["roles"]["data"][0])
        moved.append(
            {**item, "qubit_weights": {q: {"e01": item["weights"]["e01"], "e10": e10} for q in roles if q in iso}}
        )
    return brackets + alternative, moved


def sampled(brackets: list[Any], items: list[Any], seed: list[int], draws: int) -> tuple[box.Values, box.Values]:
    point = box.follow_values(box.follow_sample(brackets, items, []), items, [])
    rng = np.random.default_rng(seed)
    boot = box.pooled_follow_values(box.follow_sample(brackets, items, [], rng, draws), items, [])
    return point, boot


def analyze_bins(
    batches: dict[str, Any], t: dict[str, Any], ladder: dict[str, Any] | None, bins: int | None = None
) -> dict[str, Any]:
    bins = t["line_phase_bins"] if bins is None else bins
    if bins < 2 or bins % 2:
        box.fail(f"{bins} line-phase bins: the stationary pair bin 0 and bins / 2 needs an even count")
    depths = list(t["depths"])
    pct, sigmas, draws = t["interval_percentiles"], t["amplitude_sigmas"], t["bootstrap_draws"]
    iso = list(t["iso_qubits"])
    brackets = box.follow_brackets(batches)
    lcu, walks = box.follow_items(batches, brackets)
    if walks:
        box.fail("the ladder design holds no walk")

    jobs = [(name, batch, row) for name, batch in batches.items() for row in box.witness_rows(batch)]
    columns = [batch["bits"][row["file"]][:, box.replica_columns(row)] for _, batch, row in jobs]
    low, high = t["line_band"]
    half = t["line_detection_p"] / 2
    fundamental = parallel.ordered_map(box.LineScan((low, high), half), columns)
    doubled = parallel.ordered_map(box.LineScan((2 * low, 2 * high), half), columns)
    scans = [line_of(f, d) for f, d in zip(fundamental, doubled, strict=True)]
    work_items = []
    for (_, batch, witness), scanned in zip(jobs, scans, strict=True):
        by_depth = {r["cz_depth"]: r for r in witness["replicas"]}
        if scanned.get("cycles_per_shot") is None:
            box.fail(f"{witness['file']}: no line frequency to bin by")
        work_items.append({
            "bits": batch["bits"][witness["file"]], "frequency": scanned["cycles_per_shot"],
            "selector": {n: by_depth[n]["roles"]["selector"] for n in depths},
            "pairs": [(r["roles"]["selector"], r["roles"]["data"][0]) for r in witness["replicas"]],
        })  # fmt: skip
    works = parallel.ordered_map(JobWork(bins, depths), work_items, min_items=1)

    harmonics, reference = [], {}
    counts: dict[tuple[str, str, int], np.ndarray] = {}
    max_rng = np.random.default_rng([t["bootstrap_seed"], LINE_BINS_SEED, MAX_RULE_SEED])
    for (name, _, witness), scanned, item, work in zip(jobs, scans, work_items, works, strict=True):
        entry = harmonic_entry(depths, item["selector"], work, sigmas, max_rng, draws, bins)
        entry |= {"batch": name, "file": witness["file"], "detected": scanned["detected"],
                  "line_band": scanned["line_band"], "cycles_per_shot": scanned["cycles_per_shot"],
                  "log10_p": scanned["log10_p"], "log10_p_doubled_band": scanned["log10_p_doubled_band"]}  # fmt: skip
        # A scan peak below line_detection_p is a noise frequency: the job's phase rules are undetermined
        # and its bins carry no phase reference.
        if not scanned["detected"]:
            for key in ("first_harmonic_rule", "max_rule"):
                entry[key]["holds"] = None
        entry["reference_significant"] = bool(
            scanned["detected"] and entry["depths"][str(max(depths))]["first"]["significant"]
        )
        for depth_row in entry["depths"].values():
            reference[(name, witness["file"], depth_row["qubit"])] = (
                entry["reference_significant"] and depth_row["aligned"] is not False
            )
        harmonics.append(entry)
        for r, c in zip(witness["replicas"], work["counts"], strict=True):
            counts[(name, witness["file"], r["slot"])] = c

    # Cells: X-setting replicas in the ladder's replica order, each cut into all shots and the bins.
    cell_names = ["all", *(f"bin-{b}" for b in range(bins))]
    stationary_cells = [1, 1 + bins // 2]
    items: list[Any] = []
    cells: dict[str, dict[int, dict[int, int]]] = {}
    files_of: dict[str, dict[int, list[str]]] = {}
    for item in lcu:
        r = item["replica"]
        if r["setting"] != "X":
            continue
        c = counts[(item["batch"], item["file"], r["slot"])]
        if int(c.sum()) != item["shots"]:
            box.fail(f"{item['file']}: binned counts differ from the shots")
        parts = [c.sum(axis=0), *c]
        base = len(items)
        for part in parts:
            if int(part.sum()) == 0:
                box.fail(f"{item['file']}: an empty line-phase cell")
            items.append({**item, "joint": [int(x) for x in part], "shots": int(part.sum())})
        cells.setdefault(item["batch"], {}).setdefault(r["roles"]["selector"], {})[r["cz_depth"]] = base
        files_of.setdefault(item["batch"], {}).setdefault(r["roles"]["selector"], []).append(item["file"])
    for name, per_selector in cells.items():
        for selector, cell in per_selector.items():
            if sorted(cell) != sorted(depths):
                box.fail(f"{name} q{selector} holds depths {sorted(cell)}, not {depths}")

    seed = t["bootstrap_seed"]
    point, boot = sampled(brackets, items, [seed, LINE_BINS_SEED], draws)
    iso_pack = iso_items(batches, brackets, items, iso)
    iso_values = (
        None
        if iso_pack is None
        else sampled(iso_pack[0], iso_pack[1], [seed, LINE_BINS_SEED, box.LADDER_LINE_SEED], draws)
    )

    def estimates(values: tuple[box.Values, box.Values], selector: int, c: int) -> Any:
        """(ln rho point, ln rho draws) per batch for the pair's cell number c."""
        out = []
        with np.errstate(all="ignore"):
            for batch in names:
                cell = {n: base + c for n, base in cells[batch][selector].items()}
                out.append((rho_log(values[0], cell, depths), rho_log(values[1], cell, depths)))
        return out

    names = sorted(cells)
    pairs = sorted({s for per in cells.values() for s in per})
    partner = {r["roles"]["selector"]: r["roles"]["data"][0] for item in lcu for r in [item["replica"]]}
    rho_rows = []
    for selector in pairs:
        row: dict[str, Any] = {"pair": [selector, partner[selector]], "batches": names, "cells": {}}
        clean = [
            i for i, name in enumerate(names)
            if all(reference[(name, f, selector)] for f in files_of[name][selector])
        ]  # fmt: skip
        row["reference_significant"] = {name: i in clean for i, name in enumerate(names)}
        lr = {c: estimates((point, boot), selector, c) for c in range(len(cell_names))}
        iso_lr = None if iso_values is None else {c: estimates(iso_values, selector, c) for c in (0, *stationary_cells)}
        every = list(range(len(names)))

        def entry_of(per_batch: list[Any], which: list[int]) -> dict[str, Any]:
            return {
                "per_batch": {
                    name: box.summary(np.exp(per_batch[i][0]), np.exp(per_batch[i][1]), pct)
                    for i, name in enumerate(names)
                },
                "combined": combine(per_batch, which, pct),
            }

        def stationary(
            rates: dict[int, Any], batches: list[int] = every, cells_of: list[int] = stationary_cells
        ) -> list[Any]:
            """Per batch, ln rho averaged over the listed bins' own estimates (the stationary pair by default)."""
            with np.errstate(all="ignore"):
                return [tuple(np.mean([rates[c][i][k] for c in cells_of], axis=0) for k in (0, 1)) for i in batches]

        for c, cell_name in enumerate(cell_names):
            row["cells"][cell_name] = entry_of(lr[c], every)
        row["cells"]["all"]["combined_iso"] = None if iso_lr is None else combine(iso_lr[0], every, pct)
        merged = stationary(lr)
        row["cells"]["stationary"] = entry_of(merged, every)
        row["cells"]["stationary"]["combined_iso"] = None if iso_lr is None else combine(stationary(iso_lr), every, pct)
        row["cells"]["bin_mean"] = entry_of(stationary(lr, every, list(range(1, bins + 1))), every)
        row["bin_verdicts"] = {
            name: verdict_of(row["cells"][name]["combined"]["interval"]) for name in cell_names if name != "all"
        }
        # Bins 0 and bins / 2 are extrema of the line only where the reference phase is the line's, so the
        # stationary verdict combines the batches whose jobs all carry a detected line and a significant A1,
        # and the job-average verdict the reading compares it with combines the same batches.
        matched = verdicts(lr[0], merged, clean, pct)
        row["cells"]["all"]["clean"] = matched.pop("job_average_clean")
        row["cells"]["stationary"]["clean"] = matched.pop("stationary_clean")
        row |= matched
        rho_rows.append(row)

    if ladder is not None:
        check_against_ladder(ladder, harmonics, rho_rows, names, sigmas)

    return {
        "line_phase_bins": bins,
        "stationary_bins": [0, bins // 2],
        "cells": cell_names,
        "rho": rho_rows,
        "harmonics": harmonics,
        "harmonic_rules": {
            "first_harmonic_rule_holds": sum(h["first_harmonic_rule"]["holds"] is True for h in harmonics),
            "max_rule_holds": sum(h["max_rule"]["holds"] is True for h in harmonics),
            "jobs": len(harmonics),
            "first_rule_fails": [
                f"{h['batch']} {h['file']}" for h in harmonics if h["first_harmonic_rule"]["holds"] is False
            ],
            "max_rule_fails": [f"{h['batch']} {h['file']}" for h in harmonics if h["max_rule"]["holds"] is False],
            "undetermined": [f"{h['batch']} {h['file']}" for h in harmonics if not h["detected"]],
        },
    }


def check_against_ladder(
    ladder: dict[str, Any],
    harmonics: list[dict[str, Any]],
    rho_rows: list[dict[str, Any]],
    names: list[str],
    sigmas: float,
) -> None:
    """The all-shots cell must equal the ladder's rho and the first harmonic its lock-in, or the reuse is wrong."""
    stage = ladder["stages"][FAMILY]
    by_key = {(e["batch"], tuple(e["pair"])): e for e in stage["within_batch_ladder"] if e["setting"] == "X"}
    for row in rho_rows:
        for name in names:
            want = by_key[(name, tuple(row["pair"]))]["rho"]["value"]
            got = row["cells"]["all"]["per_batch"][name]["value"]
            if want is None or got is None or abs(want - got) > 1e-9:
                box.fail(f"pair {row['pair']} {name}: all-shots rho {got} differs from the ladder record's {want}")
    for entry in stage["line"]:
        mine = next(h for h in harmonics if (h["batch"], h["file"]) == (entry["batch"], entry["file"]))
        # The ladder scans the band alone; a line found through the doubled band has its own frequency.
        if mine["line_band"] == "second":
            continue
        for n, selector in entry["selectors"].items():
            if abs(selector["amplitude"] - mine["depths"][n]["first"]["amplitude"]) > 1e-9:
                box.fail(f"{entry['file']} depth {n}: first-harmonic amplitude differs from the ladder record")
        if mine["line_band"] == "first" and entry["depth_growth"]["holds"] != mine["first_harmonic_rule"]["holds"]:
            box.fail(f"{entry['file']}: first-harmonic rule differs from the ladder record")


# ---------------------------------------------------------------- record


def build(
    runs: list[Path], base: Path, cases_root: Path, ladder_path: Path | None, bins: int | None = None
) -> dict[str, Any]:
    batches, t, kept = load(runs, base, cases_root)
    ladder = None if ladder_path is None else json.loads(ladder_path.read_text(encoding="utf-8"))
    body = analyze_bins(batches, t, ladder, bins)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "exploratory": True,
        "post_hoc_rules": POST_HOC,
        "binds": "a future run only; the preregistered ladder record is analyze_ladder's",
        "runs": [rel(run, base) for run in kept],
        "inputs": input_digests(kept, base),
        "ladder_record": None
        if ladder_path is None
        else {"path": rel(ladder_path, base), "sha256": box.sha256(ladder_path.read_bytes())},
        "thresholds": t,
        "streams": {
            "line_bins": [t["bootstrap_seed"], LINE_BINS_SEED],
            "line_bins_iso": [t["bootstrap_seed"], LINE_BINS_SEED, box.LADDER_LINE_SEED],
            "max_rule": [t["bootstrap_seed"], LINE_BINS_SEED, MAX_RULE_SEED],
            "ladder": [t["bootstrap_seed"]],
            "ladder_iso": [t["bootstrap_seed"], box.LADDER_LINE_SEED],
        },
        **body,
        "uncertainty": f"intervals are the {t['interval_percentiles'][0]} and {t['interval_percentiles'][1]} "
        f"percentiles of a parametric bootstrap ({t['bootstrap_draws']} draws): every bracket's readout counts "
        "once per draw, shared by all cells, and each cell's joint (a, d) counts from a multinomial on the cell's "
        "own shots; they are conditional on each job's fitted line frequency and phase, which fix the bins and "
        "are not refitted per draw; harmonic errors are the lock-in standard error sqrt(2 p (1 - p) / n), and the "
        "max rule's error is the standard deviation of the depth difference of max(A1, A2) over draws of the "
        "depth-9 and depth-1 selectors' eight lock-in coefficients from their joint shot-noise covariance",
    }
    record["analysis_sha256"] = digest_of(record)
    return record


def digest_of(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "analysis_sha256"}
    return box.sha256(box.dump(body).encode("utf-8"))


def write(runs: list[Path], out: Path, ladder_path: Path) -> None:
    out.write_text(box.dump(build(runs, ROOT, box.CASES, ladder_path)), encoding="utf-8")


def check_record(path: Path, base: Path = ROOT, cases_root: Path = box.CASES) -> int:
    text = path.read_text(encoding="utf-8")
    stored = json.loads(text)
    if stored.get("schema") != SCHEMA:
        box.fail(f"{path}: schema {stored.get('schema')!r}, not {SCHEMA}")
    if stored.get("analysis_sha256") != digest_of(stored):
        box.fail(f"{path}: analysis_sha256 differs from the record's own body")
    ladder = stored["ladder_record"]
    ladder_path = None if ladder is None else base / ladder["path"]
    runs = [base / run for run in stored["runs"]]
    fresh = box.dump(build(runs, base, cases_root, ladder_path))
    if text != fresh:
        box.fail(f"{path} differs from its recomputation over {len(runs)} runs")
    return len(runs)


# ---------------------------------------------------------------- self-test


def synth_shots(item: Any) -> list[str]:
    """Shots whose decay, selector population and harmonic content follow a line of known shape.

    Per job one phase is drawn; per replica group (a, d, ideal, decay, depth) the decay is
    decay (1 + m_n cos(h theta)) with m_n = modulation depth / 9 (or modulation when scale_depth is false) and h
    the depth's harmonic (none when 0), and the selector population is p0 - p_slope depth + p_line cos(theta)
    with the ideal branch weights rescaled to it; a depth listed in phase_offset reads theta shifted by it.
    Readout flips follow the scenario's per-qubit rates.
    """
    _, seed, width, n, groups, readout, params = item
    rng = np.random.default_rng(seed)
    line = 2 * np.pi * params["frequency"] * np.arange(n) + rng.uniform(0, 2 * np.pi)
    true = np.zeros((n, width), dtype=np.uint8)
    for a, d, ideal, decay, depth in groups:
        theta = line + params.get("phase_offset", {}).get(depth, 0.0)
        harmonic = params.get("harmonic", {}).get(depth, 1)
        m = params["modulation"] * (depth / 9 if params.get("scale_depth", True) else 1.0)
        lam = np.clip(decay * (1 + m * (np.cos(harmonic * theta) if harmonic else np.zeros(n))), 0.0, 1.0)
        p0 = params.get("p0", 1.0) - params.get("p_slope", 0.0) * depth
        pz = np.clip(p0 + params.get("p_line", 0.0) * np.cos(theta), 0.0, 1.0)
        branch0, branch1 = np.asarray(ideal[:2]), np.asarray(ideal[2:])
        mass0 = branch0.sum()
        shape0 = branch0 / mass0
        shape1 = branch1 / branch1.sum() if branch1.sum() > 0 else np.array([0.5, 0.5])
        state = np.concatenate([pz[:, None] * shape0[None, :], (1 - pz)[:, None] * shape1[None, :]], axis=1)
        joint = lam[:, None] * state + (1 - lam[:, None]) / 4
        outcome = np.minimum((np.cumsum(joint, axis=1) < rng.random(n)[:, None]).sum(axis=1), 3)
        true[:, a], true[:, d] = outcome >> 1, outcome & 1
    rates = np.array([readout.get(q, (box.SYN_E01, box.SYN_E10)) for q in range(width)])
    flip = rng.random((n, width)) < np.where(true == 0, rates[:, 0], rates[:, 1])
    text = ((true ^ flip)[:, ::-1] + 48).astype(np.uint8).tobytes().decode("ascii")
    return [text[s * width : (s + 1) * width] for s in range(n)]


def synthesize(item: Any) -> list[str]:
    return synth_shots(item) if item[0] == "line" else box.synthesize(item)


def build_runs(root: Path, name: str, params: dict[str, Any], seed: int) -> list[Path]:
    scenario = {**box.LADDER_ONLY, "line": params}
    jobs = box.scenario_jobs(name, scenario, seed)
    shots = parallel.ordered_map(synthesize, [job[3] for job in jobs], min_items=1)
    grouped: dict[tuple[str, str], dict[str, list[str]]] = {}
    for (family, batch, file, _, _), values in zip(jobs, shots, strict=True):
        grouped.setdefault((family, batch), {})[file] = values
    return [box.write_run(root / name, family, batch, files, {}) for (family, batch), files in grouped.items()]


FREQUENCY = 0.020036
SCENARIOS: dict[str, dict[str, Any]] = {
    # rho = 1 in every bin up to the bin width; the line moves the selector population against the decay.
    "population_line": {"frequency": FREQUENCY, "modulation": 0.9, "p0": 0.85, "p_line": -0.12},
    # The population falls with depth, which raises rho in every bin.
    "population_error": {"frequency": FREQUENCY, "modulation": 0.3, "p0": 0.97, "p_slope": 0.02},
    # Depth 5 carries the line at f, depth 9 at 2 f only, depth 1 none.
    "extremum": {"frequency": FREQUENCY, "modulation": 0.2, "scale_depth": False, "harmonic": {1: 0, 5: 1, 9: 2}},
    # Depths 5 and 9 follow the line at 2 f alone, so only the doubled band detects it.
    "second_only": {"frequency": FREQUENCY, "modulation": 0.2, "scale_depth": False, "harmonic": {1: 0, 5: 2, 9: 2}},
    # The population line with depth 5 a quarter period behind depth 9's reference.
    "offset": {
        "frequency": FREQUENCY,
        "modulation": 0.9,
        "p0": 0.85,
        "p_line": -0.12,
        "phase_offset": {5: math.pi / 2},
    },
    # No line: the scan peak is noise, so every phase rule and the stationary verdict are undetermined.
    "no_line": {"frequency": FREQUENCY, "modulation": 0.0, "p0": 0.9},
}


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def independent(model: dict[str, Any]) -> dict[str, Any]:
    """The model with the columns' shot noise made independent: S off its diagonal set to 0."""
    sigma = [[v if i == j else 0.0 for j, v in enumerate(row)] for i, row in enumerate(model["sigma"])]
    return {**model, "sigma": sigma}


def max_rule_sd(model: dict[str, Any], seed: int, draws: int) -> float:
    boot = joint_max_draws(model, np.random.default_rng(seed), draws)
    return float(np.std(boot[:, 0] - boot[:, 1], ddof=1))


def self_test_joint_draw() -> None:
    rng = np.random.default_rng(5101)
    n, draws = 8192, 4000
    t = np.arange(n) - (n - 1) / 2

    # Two selector columns with the same shots: every draw's depth difference is exactly 0.
    same = np.repeat((rng.random(n) < 0.3).astype(np.uint8)[:, None], 2, axis=1)
    model = coefficient_model(same, FREQUENCY)
    se = box.lockin(same, FREQUENCY, [0])[0]["se"]
    for k in range(4):
        ratio = math.sqrt(model["sigma"][0][0] * model["kernel"][k][k]) / se
        require(abs(ratio - 1) < 0.02, f"coefficient {k} SE over the lock-in SE {ratio}")
    require(max_rule_sd(model, 1, draws) < 1e-12, "identical selectors give a max-rule SD of 0")
    require(max_rule_sd(independent(model), 1, draws) > 1e-3, "the independent draw spreads identical selectors")

    # A strong line on two selectors whose shots share their uniform deviate with probability 0.8: the joint
    # draw's SD of the depth difference matches the spread over independent realizations of the same law.
    realizations = 400
    theta = 2 * np.pi * FREQUENCY * t + 0.7
    p_deep, p_shallow = 0.5 + 0.25 * np.cos(theta), 0.5 + 0.15 * np.cos(theta)
    u = rng.random((n, realizations))
    u_shallow = np.where(rng.random((n, realizations)) < 0.8, u, rng.random((n, realizations)))
    bits = np.concatenate([u < p_deep[:, None], u_shallow < p_shallow[:, None]], axis=1).astype(np.uint8)
    columns = list(range(2 * realizations))
    tops = np.maximum(
        [a["amplitude"] for a in box.lockin(bits, FREQUENCY, columns)],
        [a["amplitude"] for a in box.lockin(bits, 2 * FREQUENCY, columns)],
    )
    spread = float(np.std(tops[:realizations] - tops[realizations:], ddof=1))
    model = coefficient_model(bits[:, [0, realizations]], FREQUENCY)
    joint, apart = max_rule_sd(model, 2, draws), max_rule_sd(independent(model), 2, draws)
    require(abs(joint / spread - 1) < 0.15, f"joint SD {joint} against the realizations' {spread}")
    require(apart / spread > 1.3, f"independent SD {apart} against the realizations' {spread}")


def self_test_matched_verdicts() -> None:
    rng = np.random.default_rng(5102)
    pct = [0.5, 99.5]

    def batch(ln_rho: float) -> tuple[np.ndarray, np.ndarray]:
        return np.array([ln_rho]), ln_rho + 0.01 * rng.standard_normal(4000)

    # The excluded batch 1 lifts the all-batch job average above 1; the clean batch 0 reads 1 throughout.
    flat, high = batch(0.0), batch(0.2)
    out = verdicts([flat, high], [flat, high], [0], pct)
    require(out["job_average_all_verdict"] == "above 1", f"all-batch job average {out}")
    require(out["job_average_verdict"] == "consistent with 1", f"clean job average {out}")
    require(out["reading"] == "undecided", f"reading on the clean batches {out['reading']}")
    # The excluded batch pulls the all-batch job average to 1 under a clean job average above 1.
    lifted, low = batch(0.05), batch(-0.05)
    out = verdicts([lifted, low], [flat, flat], [0], pct)
    require(out["job_average_all_verdict"] == "consistent with 1", f"all-batch job average {out}")
    require(out["reading"] == "averaging over the line explains the rho excess", out["reading"])
    require(verdicts([flat], [flat], [], pct)["reading"] == "undecided", "no clean batch")


def self_test() -> str:
    self_test_joint_draw()
    self_test_matched_verdicts()
    with tempfile.TemporaryDirectory(prefix="ladder-line-bins-") as scratch:
        root = Path(scratch)
        built = {
            name: build_runs(root, name, params, 7000 + 1000 * n) for n, (name, params) in enumerate(SCENARIOS.items())
        }

        def analysis(name: str) -> dict[str, Any]:
            return build(built[name], root / name, box.CASES, None)

        line = analysis("population_line")
        for row in line["rho"]:
            require(
                row["job_average_verdict"] == "above 1",
                f"job-averaged rho of {row['pair']}: {row['cells']['all']['combined']}",
            )
            require(
                row["stationary_verdict"] == "consistent with 1",
                f"stationary rho of {row['pair']}: {row['cells']['stationary']['combined']}",
            )
            require(row["reading"] == "averaging over the line explains the rho excess", row["reading"])
            require(all(row["reference_significant"].values()), "the depth-9 selector carries the line")
        for h in line["harmonics"]:
            require(h["line_band"] == "first", f"{h['file']} line band {h['line_band']}")
            require(all(d["aligned"] is not False for d in h["depths"].values()), f"{h['file']} aligned depths")
        require(
            line["harmonic_rules"]["first_harmonic_rule_holds"] == line["harmonic_rules"]["jobs"],
            "first rule on a first-harmonic line",
        )

        error = analysis("population_error")
        for row in error["rho"]:
            for name, cell in row["cells"].items():
                require(cell["combined"]["interval"][0] > 1, f"{row['pair']} {name}: {cell['combined']}")
            require(row["reading"] == "averaging over the line does not explain rho above 1", row["reading"])

        extremum = analysis("extremum")
        for h in extremum["harmonics"]:
            deep, shallow = h["depths"]["9"], h["depths"]["1"]
            require(h["detected"], f"{h['file']} line detected through depth 5")
            require(
                not deep["first"]["significant"] and deep["second"]["significant"],
                f"{h['file']} depth 9 A1 {deep['first']} A2 {deep['second']}",
            )
            require(deep["first"]["amplitude"] < 0.2 * deep["second"]["amplitude"], "A1 near 0 beside A2")
            require(
                not shallow["first"]["significant"] and not shallow["second"]["significant"], f"{h['file']} depth 1"
            )
            require(h["max_rule"]["holds"] and not h["first_harmonic_rule"]["holds"], f"{h['file']} rules")
            require(h["depths"]["5"]["first"]["significant"], f"{h['file']} depth 5 first harmonic")

        second = analysis("second_only")
        for h in second["harmonics"]:
            require(h["detected"] and h["line_band"] == "second", f"{h['file']} doubled band ({h['log10_p']})")
            require(abs(h["cycles_per_shot"] - FREQUENCY) < 1e-4, f"{h['file']} frequency {h['cycles_per_shot']}")
            require(h["max_rule"]["holds"] is True, f"{h['file']} max rule {h['max_rule']}")
            require(h["first_harmonic_rule"]["holds"] is False, f"{h['file']} first rule {h['first_harmonic_rule']}")
        for row in second["rho"]:
            require(row["stationary_verdict"] == "undetermined", f"{row['pair']}: {row['stationary_verdict']}")

        shifted = analysis("offset")
        for h in shifted["harmonics"]:
            require(h["reference_significant"], f"{h['file']} reference")
            require(h["depths"]["5"]["aligned"] is False, f"{h['file']} depth 5 {h['depths']['5']['phase_offsets']}")
            require(
                h["depths"]["9"]["aligned"] is not False, f"{h['file']} depth 9 {h['depths']['9']['phase_offsets']}"
            )
        for row in shifted["rho"]:
            require(not any(row["reference_significant"].values()), f"{row['pair']} clean batches")
            require(row["stationary_verdict"] == "undetermined", f"{row['pair']}: {row['stationary_verdict']}")

        quiet = analysis("no_line")
        for h in quiet["harmonics"]:
            require(not h["detected"], f"{h['file']} line detected without a line (log10 p {h['log10_p']})")
            require(h["max_rule"]["holds"] is None and h["first_harmonic_rule"]["holds"] is None, "undetermined")
        require(len(quiet["harmonic_rules"]["undetermined"]) == len(quiet["harmonics"]), "every rule undetermined")
        for row in quiet["rho"]:
            require(row["stationary_verdict"] == "undetermined", f"{row['pair']}: {row['stationary_verdict']}")

        # A record verifies, and a corrupted raw digest, an altered bin count or an altered raw file does not.
        runs = built["population_line"]
        base = root / "population_line"
        record = base / "line_bins.json"
        record.write_text(box.dump(line), encoding="utf-8")
        require(check_record(record, base) == len(runs), "synthetic record checks")
        stored = json.loads(record.read_text(encoding="utf-8"))

        def refused(label: str, mutated: dict[str, Any], reason: str, resign: bool = True) -> None:
            if resign:
                mutated["analysis_sha256"] = digest_of(mutated)
            record.write_text(box.dump(mutated), encoding="utf-8")
            box.expect_exit(label, lambda: check_record(record, base), reason)

        digest_run = next(iter(stored["inputs"]))
        digest_file = next(iter(stored["inputs"][digest_run]["raw_sha256"]))
        altered = json.loads(json.dumps(stored))
        altered["inputs"][digest_run]["raw_sha256"][digest_file] = "0" * 64
        unsigned = json.loads(json.dumps(altered))
        refused("an unsigned raw digest edit", unsigned, "analysis_sha256 differs", resign=False)
        refused("a corrupted raw digest", altered, "differs from its recomputation")
        rebinned = json.loads(json.dumps(stored))
        rebinned["line_phase_bins"] = 6
        refused("an altered bin count", rebinned, "differs from its recomputation")
        box.expect_exit("odd bins", lambda: build(runs, base, box.CASES, None, 5), "needs an even count")
        record.write_text(box.dump(stored), encoding="utf-8")
        witness = base / stored["runs"][1]
        raw = next((witness / "raw").glob("latin-*.json"))
        shots = json.loads(raw.read_text(encoding="utf-8"))
        flipped = "1" if shots[0][0] == "0" else "0"
        shots[0] = flipped + shots[0][1:]
        raw.write_text(json.dumps(shots), encoding="utf-8")
        box.expect_exit("an altered raw file", lambda: check_record(record, base), "differs from its recomputation")
    return (
        "self-test: the joint coefficient draw gives identical selectors a max-rule SD of 0 and a correlated pair "
        "its realizations' SD, the reading follows the clean-batch job average, a population line gives "
        "stationary rho 1 beside job-averaged rho above 1, a population error raises rho in every bin, an extremum "
        "response keeps A1 near 0 with A2 detected by max(A1, A2), a line seen only at 2 f is found through the "
        "doubled band and decides the max rule, a depth-5 selector a quarter period off the reference leaves "
        "every batch out of the stationary verdict, a "
        "series without a line leaves every phase rule undetermined, and a corrupted digest, bin count and raw "
        "file are refused"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.check:
        count = check_record(args.check)
        print(f"{args.check}: {count} runs reproduce the line-bin analysis")
        return 0
    ladder = json.loads(LADDER_RECORD.read_text(encoding="utf-8"))
    write([ROOT / run for run in ladder["runs"]], args.out, LADDER_RECORD)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
