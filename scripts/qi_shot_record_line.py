"""Spectral line in the shot order of retained Quantum Inspire jobs.

qi_platform.py collect retains each job's per-shot bit strings in
raw/FILE.json in the order the service returns them. Read as a time series
over the shot index t, a bit's outcome x_t carries any periodic modulation of
the device as a line in its periodogram. This script scans every retained
Tuna-17 job and every QX job (the ideal emulator is the control: its shots
are independent draws) for a line in BAND, the band around 0.02 cycles per
shot where the follow series' CZ ladders put one.

Per job:
- parse: every shot string into a (shots, width) boolean array in one numpy
  pass, bit b at character width - 1 - b (qubit 0 rightmost on QX and Tuna);
  the Ry emulator reads leftmost and is skipped.
- scan: the bits whose variance exceeds MIN_VARIANCE are standardized and
  enter a zoom FFT over BAND (scipy.signal.zoom_fft, ZOOM_POINTS points).
  Bits of one shot are correlated (an LCU pair's selector and data, any
  readout crosstalk), so the statistic whitens them: P(f) = Z(f)^H R^+ Z(f) / n
  with Z the standardized bits' transform and R^+ the pseudo-inverse of their
  same-shot correlation matrix, rank k after dropping eigenvalues below
  EIGEN_FLOOR times the largest. Shots that are independent in time, whatever
  their within-shot correlation, give P(f) a Gamma(k, 1) law at each
  frequency; the peak's p-value takes the band's n * width independent
  frequencies into account, and a job with p below DETECTION_P carries the
  line.
- lock-in: least squares of every scanned bit on cos and sin of 2 pi f t at
  the peak f, 2 f and 3 f gives the first-harmonic amplitude, its phase at the
  middle shot (where a frequency error moves it least) and the
  third- and second-harmonic amplitudes, listed in that order; a bit is
  listed when its first- or second-harmonic amplitude exceeds
  AMPLITUDE_SIGMAS standard errors sqrt(2 var / n). A bit whose static phase
  sits at an extremum of its response carries a phase modulation at 2 f
  with a vanishing first harmonic.
- stationarity: the chi-square of BLOCKS block means of each scanned bit
  against binomial noise (BLOCKS - 1 degrees of freedom), reported as the
  smallest per-bit tail probability times the number of bits scanned, so jobs
  that scan different numbers of bits compare on one scale.

Summaries:
- wall clock against shot index: the readout ring-down arms differ only in a
  wait of tau cycles of 20 ns (qi_readout_ringdown_cases.arm_tau), so a line
  at a fixed frequency F in wall-clock time sits at F (T_shot + tau 20 ns)
  cycles per shot while a line locked to the shot index sits at one value for
  every tau. The slope of the peak frequency over tau 20 ns, with an
  intercept per batch (the jobs of a batch run back to back), estimates F in
  Hz; 0 is the shot-locked prediction.
- depth: the follow series' selector qubits (each LCU pair's first qubit)
  at CZ depths 1, 5 and 9, and the common phase of the depth-9 selectors.

--write FILE writes the record; --check FILE recomputes it and compares
bytes; --self-test recovers a synthetic line, rejects white shots, refits a
known slope, and requires the pooled scan to equal the serial one.

Usage: "$PYTHON" scripts/qi_shot_record_line.py (--write FILE | --check FILE | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from scipy.signal import zoom_fft
from scipy.special import gammaln, logsumexp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from qi_readout_ringdown_cases import arm_tau  # noqa: E402

import parallel  # noqa: E402

RUNS = ROOT / "results" / "quantum_inspire" / "runs"
# backend_type_id of the backends whose strings put bit 0 rightmost.
BACKENDS = {1: "QX", 7: "Tuna-17"}
BAND = (0.019, 0.021)
ZOOM_POINTS = 4001
MIN_VARIANCE = 0.02
DETECTION_P = 1e-6
EIGEN_FLOOR = 1e-9
AMPLITUDE_SIGMAS = 5.0
BLOCKS = 16
CYCLE_SECONDS = 20e-9
GRID_HZ = 50.0
FOLLOW = "box_kite_tuna_follow"
SELECTORS = (1, 10, 12)
ARM = re.compile(r"^(reference|tau\d{3})-[xy]-d\d{3}\.cq$")


def sig(value: float, digits: int = 6) -> float:
    return float(f"{value:.{digits}g}")


def bits(path: Path) -> np.ndarray:
    """The shots of one raw file as a (shots, width) boolean array, column b = bit b."""
    shots = json.loads(path.read_text())
    width = len(shots[0])
    if any(len(shot) != width for shot in shots):
        raise SystemExit(f"{path}: shot strings differ in width")
    flat = np.frombuffer("".join(shots).encode("ascii"), dtype=np.uint8)
    return flat.reshape(len(shots), width)[:, ::-1] == ord("1")


def gamma_log_tail(k: int, x: float) -> float:
    """log P(Gamma(k, 1) > x) for integer k: e^-x sum_{j<k} x^j / j!, summed in logs so it stays finite."""
    j = np.arange(k)
    return -x + float(logsumexp(j * math.log(x) - gammaln(j + 1)))


def chi2_log10_tail(chi: np.ndarray, dof: int) -> np.ndarray:
    """log10 P(chi2(dof) > chi), finite where scipy's logsf underflows.

    The tail is Q(a, x) with a = dof / 2 and x = chi / 2; past the underflow x far exceeds a, where the
    asymptotic series log Q = -x + (a - 1) log x - lgamma(a) + log(sum_j (a - 1)...(a - j) / x^j) holds.
    """
    direct = stats.chi2.logsf(chi, dof)
    a, x = dof / 2, np.maximum(chi / 2, 1.0)
    series = np.ones_like(x)
    term = np.ones_like(x)
    for j in range(1, 12):
        term = term * (a - j) / x
        series = series + term
    asymptotic = -x + (a - 1) * np.log(x) - math.lgamma(a) + np.log(series)
    return np.where(np.isfinite(direct), direct, asymptotic) / math.log(10)


def scan(x: np.ndarray, band: tuple[float, float] = BAND, detection_p: float = DETECTION_P) -> dict[str, Any]:
    """Band scan, lock-in and block stationarity of a (shots, width) outcome array, in band at detection_p."""
    n = x.shape[0]
    centered = x - x.mean(axis=0)
    variance = centered.var(axis=0)
    used = np.flatnonzero(variance > MIN_VARIANCE)
    row: dict[str, Any] = {"shots": n, "bits_scanned": [int(b) for b in used]}
    if used.size == 0:
        return row | {"detected": False}
    columns = centered[:, used]
    standard = columns / np.sqrt(variance[used])
    correlation = standard.T @ standard / n
    eigenvalues, vectors = np.linalg.eigh(correlation)
    kept = eigenvalues > EIGEN_FLOOR * eigenvalues.max()
    rank = int(kept.sum())
    pseudo = (vectors[:, kept] / eigenvalues[kept]) @ vectors[:, kept].T
    spectrum = zoom_fft(standard, list(band), m=ZOOM_POINTS, fs=1.0, axis=0)
    power = np.einsum("fk,kl,fl->f", spectrum.conj(), pseudo, spectrum).real / n
    peak = int(power.argmax())
    step = (band[1] - band[0]) / (ZOOM_POINTS - 1)
    offset = 0.0
    if 0 < peak < ZOOM_POINTS - 1:
        left, middle, right = power[peak - 1], power[peak], power[peak + 1]
        denominator = left - 2 * middle + right
        offset = 0.5 * (left - right) / denominator if denominator else 0.0
    frequency = band[0] + (peak + offset) * step
    independent = math.ceil((band[1] - band[0]) * n)
    log10_p = min(0.0, (math.log(independent) + gamma_log_tail(rank, float(power[peak]))) / math.log(10))
    t = np.arange(n) - (n - 1) / 2
    design = np.stack(
        [
            np.cos(2 * np.pi * frequency * t),
            np.sin(2 * np.pi * frequency * t),
            np.cos(6 * np.pi * frequency * t),
            np.sin(6 * np.pi * frequency * t),
            np.cos(4 * np.pi * frequency * t),
            np.sin(4 * np.pi * frequency * t),
        ],
        axis=1,
    )
    coefficients = np.linalg.lstsq(design, columns, rcond=None)[0]
    first = np.hypot(coefficients[0], coefficients[1])
    phase = np.arctan2(-coefficients[1], coefficients[0])
    third = np.hypot(coefficients[2], coefficients[3])
    second = np.hypot(coefficients[4], coefficients[5])
    error = np.sqrt(2 * variance[used] / n)
    listed = {
        str(int(b)): [sig(float(a), 4), sig(float(p), 4), sig(float(h), 4), sig(float(g), 4)]
        for b, a, p, h, g, e in zip(used, first, phase, third, second, error, strict=True)
        if max(a, g) > AMPLITUDE_SIGMAS * e
    }
    # Cramer-Rao bound of a real sinusoid's frequency in white noise, combined over bits through the same-shot
    # correlation: the standardized cosine and sine coefficient vectors contract with R^+, so k copies of one bit
    # carry one bit's information.
    unit = coefficients[:2] / np.sqrt(variance[used])
    contracted = float(np.einsum("ik,kl,il->", unit, pseudo, unit))
    information = contracted * (2 * np.pi) ** 2 * n * (n * n - 1) / 24
    m = n // BLOCKS
    blocks = x[: m * BLOCKS, used].reshape(BLOCKS, m, used.size).mean(axis=1)
    chi = ((blocks - x[:, used].mean(axis=0)) ** 2 / (variance[used] / m)).sum(axis=0)
    tails = chi2_log10_tail(chi, BLOCKS - 1)
    block_log10_p = min(0.0, float(tails.min()) + math.log10(used.size))
    return row | {
        "detected": log10_p < math.log10(detection_p),
        "whitened_rank": rank,
        "log10_p": sig(log10_p, 4),
        "peak_power": sig(float(power[peak]), 5),
        "cycles_per_shot": sig(frequency, 8),
        "cycles_per_shot_se": sig(1 / math.sqrt(information), 3) if information > 0 else None,
        "bits": listed,
        "block_log10_p_adjusted": sig(block_log10_p, 4),
    }


def job_row(item: tuple[str, str, int]) -> dict[str, Any]:
    run, name, backend = item
    path = RUNS / run / "raw" / f"{name}.json"
    return {"run": run, "file": name, "backend": BACKENDS[backend]} | scan(bits(path).astype(np.float64))


def inventory() -> list[tuple[str, str, int]]:
    """Every (run, circuit file, backend type) whose raw shots this scan reads, in path order."""
    items = []
    for run in sorted(path for path in RUNS.iterdir() if (path / "results.json").exists()):
        backend = json.loads((run / "submission.json").read_text())["backend_type_id"]
        if backend not in BACKENDS:
            continue
        for raw in sorted((run / "raw").glob("*.json")):
            items.append((run.name, raw.name[: -len(".json")], backend))
    return items


def batch_of(run: str) -> str:
    return run.split("Z-", 1)[1]


def wall_clock_slope(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Peak frequency over the ring-down arms' tau, one intercept per batch."""
    arms = [
        row
        for row in rows
        if row["backend"] == "Tuna-17"
        and row["detected"]
        and ARM.match(row["file"])
        and "readout_ringdown" in row["run"]
    ]
    batches = sorted({batch_of(row["run"]) for row in arms})
    design = np.zeros((len(arms), len(batches) + 1))
    for index, row in enumerate(arms):
        design[index, batches.index(batch_of(row["run"]))] = 1.0
        design[index, -1] = (arm_tau(row["file"].split("-", 1)[0]) or 0) * CYCLE_SECONDS
    target = np.array([row["cycles_per_shot"] for row in arms])
    coefficients, *_ = np.linalg.lstsq(design, target, rcond=None)
    residual = target - design @ coefficients
    dof = len(arms) - design.shape[1]
    covariance = (residual @ residual / dof) * np.linalg.inv(design.T @ design)
    slope, error = float(coefficients[-1]), float(math.sqrt(covariance[-1, -1]))
    intercepts = coefficients[:-1]
    return {
        "jobs": len(arms),
        "batches": len(batches),
        "slope_hz": sig(slope, 4),
        "slope_se_hz": sig(error, 3),
        "z_shot_locked": sig(slope / error, 3),
        "z_from_grid": sig((slope - GRID_HZ) / error, 3),
        "shot_period_us_at_grid": [sig(float(c) / GRID_HZ * 1e6, 5) for c in (intercepts.min(), intercepts.max())],
        "residual_sd": sig(float(residual.std()), 3),
    }


def follow_depths(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Selector first-harmonic amplitudes of the follow series' bright-edge circuits, and their common phase.

    An amplitude is None when it stays below AMPLITUDE_SIGMAS standard errors.
    The phase resultant |mean exp(i phase)| over one job's selectors is 1 when
    every selector oscillates in phase; each job starts at its own line phase,
    so the resultant is taken per job. The shot period at the grid frequency
    spans the follow jobs that carry the line; it depends on circuit length,
    as the ring-down slope shows.
    """
    table = {}
    resultants = {}
    for row in rows:
        if FOLLOW not in row["run"] or not re.match(r"^(depth-\d|lcu-bright)", row["file"]):
            continue
        listed = row.get("bits", {})
        table[row["file"]] = {str(b): listed[str(b)][0] if str(b) in listed else None for b in SELECTORS}
        phases = [listed[str(b)][1] for b in SELECTORS if str(b) in listed]
        if len(phases) == len(SELECTORS):
            resultants[row["file"]] = sig(float(abs(np.exp(1j * np.array(phases)).mean())), 4)
    follow = [row["cycles_per_shot"] for row in rows if FOLLOW in row["run"] and row["detected"]]
    return {
        "selector_amplitudes": table,
        "selector_phase_resultant": resultants,
        "shot_period_us_at_grid": [sig(min(follow) / GRID_HZ * 1e6, 5), sig(max(follow) / GRID_HZ * 1e6, 5)],
    }


def stationarity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per run family: the median adjusted block log10 p and the fraction of jobs below 0.01 (log10 -2)."""
    families: dict[str, list[float]] = {}
    for row in rows:
        if "block_log10_p_adjusted" in row and row["backend"] == "Tuna-17":
            family = re.sub(r"-(batch|recal|rerun).*$", "", batch_of(row["run"]))
            families.setdefault(family, []).append(row["block_log10_p_adjusted"])
    return {
        family: {
            "jobs": len(values),
            "median_log10_p_adjusted": sig(float(np.median(values)), 4),
            "fraction_below_0_01": sig(float(np.mean(np.array(values) < -2)), 4),
        }
        for family, values in sorted(families.items())
    }


def record() -> dict[str, Any]:
    rows = parallel.ordered_map(job_row, inventory())
    counts = {
        name: {
            "jobs": sum(row["backend"] == name for row in rows),
            "detected": sum(row["backend"] == name and row["detected"] for row in rows),
        }
        for name in BACKENDS.values()
    }
    return {
        "schema": "qi-shot-record-line-v1",
        "band_cycles_per_shot": list(BAND),
        "detection_p": DETECTION_P,
        "block_chi2_dof": BLOCKS - 1,
        "counts": counts,
        "wall_clock": wall_clock_slope(rows),
        "follow": follow_depths(rows),
        "stationarity": stationarity(rows),
        "jobs": rows,
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def require(condition: bool, detail: object) -> None:
    if not condition:
        raise SystemExit(f"self-test failed: {detail}")


def synthetic(n: int, frequency: float, amplitude: float, phase: float, seed: int) -> np.ndarray:
    """n shots of five bits: three carry the line at one phase, two are white at P = 0.3."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    p = 0.5 + amplitude * np.cos(2 * np.pi * frequency * t + phase)
    line = rng.random((n, 3)) < p[:, None]
    white = rng.random((n, 2)) < 0.3
    return np.concatenate([line, white], axis=1).astype(np.float64)


def self_test() -> str:
    for k, x in ((1, 3.0), (4, 2.5), (9, 30.0)):
        require(abs(gamma_log_tail(k, x) - float(stats.gamma.logsf(x, k))) < 1e-9, (k, x))
    require(math.isfinite(gamma_log_tail(3, 5000.0)), "tail underflow")
    row = scan(synthetic(16384, 0.020037, 0.1, 0.7, 11))
    require(row["detected"], row)
    error = row["cycles_per_shot_se"]
    require(abs(row["cycles_per_shot"] - 0.020037) < 5 * error, (row["cycles_per_shot"], error))
    middle = 0.7 + 2 * np.pi * 0.020037 * (16384 - 1) / 2
    for b in ("0", "1", "2"):
        amplitude, phase, _, _ = row["bits"][b]
        require(abs(amplitude - 0.1) < 5 * math.sqrt(2 * 0.25 / 16384), amplitude)
        require(abs(np.angle(np.exp(1j * (phase - middle)))) < 5 * math.sqrt(2 * 0.25 / 16384) / 0.1, phase)
    require("3" not in row["bits"] and "4" not in row["bits"], row["bits"])
    white = scan(synthetic(16384, 0.020037, 0.0, 0.0, 12))
    require(not white["detected"], white)
    # Twelve copies of one white bit: summing their powers as independent would detect a line; whitening sees rank 1.
    copies = np.repeat(synthetic(16384, 0.020037, 0.0, 0.0, 13)[:, :1], 12, axis=1)
    copied = scan(copies)
    require(not copied["detected"] and copied["whitened_rank"] == 1, copied)
    # The copies of a bit carrying the line carry one bit's frequency information.
    single = scan(synthetic(16384, 0.020037, 0.1, 0.7, 11)[:, :1])
    stacked = scan(np.repeat(synthetic(16384, 0.020037, 0.1, 0.7, 11)[:, :1], 12, axis=1))
    require(abs(stacked["cycles_per_shot_se"] / single["cycles_per_shot_se"] - 1) < 1e-6, (single, stacked))
    for chi in (40.0, 400.0, 4000.0):
        tail = float(chi2_log10_tail(np.array([chi]), 15)[0])
        require(math.isfinite(tail) and tail < 0, (chi, tail))
    near = float(chi2_log10_tail(np.array([1400.0]), 15)[0])
    require(abs(near - float(stats.chi2.logsf(1400.0, 15)) / math.log(10)) < 1e-6, near)
    # A shot-locked line keeps one frequency for every tau; a wall-clock line moves by F tau.
    rows = []
    for batch, base in enumerate((0.0202, 0.02021)):
        for tau in (0, 5, 15, 40, 100):
            rows.append(
                {
                    "backend": "Tuna-17",
                    "detected": True,
                    "run": f"2026-01-01T000000Z-readout_ringdown_tuna_17_P-batch-0{batch}",
                    "file": f"tau{tau:03d}-x-d002.cq",
                    "cycles_per_shot": base + GRID_HZ * tau * CYCLE_SECONDS + 1e-7 * ((tau * 7) % 3 - 1),
                }
            )
    fit = wall_clock_slope(rows)
    require(abs(fit["slope_hz"] - GRID_HZ) < 4 * fit["slope_se_hz"], fit)
    items = inventory()[:6]
    serial = [job_row(item) for item in items]
    require(parallel.ordered_map(job_row, items, min_items=1) == serial, "pooled scan differs from serial")
    return "self-test: synthetic line recovered, white shots rejected, slope refit, pooled scan equals serial"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    text = dump(record())
    if args.write:
        args.write.write_text(text)
        print(f"wrote {args.write}")
        return 0
    if args.check.read_text() != text:
        print(f"{args.check} differs from the recomputed record", file=sys.stderr)
        return 1
    print(f"{args.check} matches the recomputed record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
