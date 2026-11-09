"""Probe exqalibur 1.4.1's Gurvits permanent estimator and its Ryser and Glynn exact routines.

Writes permanent_probe.json beside this file. Seeds come from the ANU QRNG record
docs/evidence/anu_qrng/draw-2026-11-09T060635Z.json, values 0 to 4, allocated in
docs/evidence/qrng_seeds/allocations.json. Every timing runs on one exqalibur thread.

Run: "$PYTHON" docs/evidence/quandela/permanent-estimators/permanent_probe.py
with perceval-quandela 1.3.0 and exqalibur 1.4.1 installed.
"""

from __future__ import annotations

import json
import math
import platform
import time
from collections.abc import Callable
from functools import partial
from pathlib import Path

import exqalibur as xq
import numpy as np

matrix_seed = 64823
estimator_seed = 56785
timing_seed = 28446
crossover_matrix_seed = 4632
crossover_estimator_seed = 53907

ASCELLA_INPUT_MODES = [0, 2, 4, 6, 8, 10]
DEFAULT_ITERATIONS = 10000  # NaiveApproxBackend(gurvits_iterations=10000) in perceval-quandela 1.3.0


def haar(m: int, rng: np.random.Generator) -> np.ndarray:
    z = (rng.standard_normal((m, m)) + 1j * rng.standard_normal((m, m))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    return np.ascontiguousarray(q * (np.diag(r) / np.abs(np.diag(r))))


def best_time(call: Callable[[], object], repeats: int = 3) -> float:
    best = math.inf
    for _ in range(repeats):
        t0 = time.perf_counter()
        call()
        best = min(best, time.perf_counter() - t0)
    return best


def main() -> dict[str, object]:
    xq.Config.compute_max_thread_count = 1
    out: dict[str, object] = {
        "exqalibur": "1.4.1",
        "numpy": np.__version__,
        "python": platform.python_version(),
        "machine": f"{platform.system()} {platform.machine()}",
    }

    # Glynn's +-1 estimator is exact on a diagonal matrix; a Gaussian estimator is not.
    xq.set_seed(estimator_seed)
    diagonal = np.ascontiguousarray(np.diag(np.array([2, 0.5, 1j, -1, 3, 1, 1, 0.25], dtype=complex)))
    estimate, halfwidth = xq.estimate_permanent_cx(diagonal, 1000)
    out["diagonal_8"] = {
        "exact": str(complex(np.prod(np.diag(diagonal)))),
        "estimate": str(estimate),
        "halfwidth": halfwidth,
    }

    # Coverage at Ascella scale: rows on the six input modes of 12x12 Haar unitaries, six output columns.
    rng = np.random.default_rng(matrix_seed)
    trials = 300
    inside_complex = inside_modulus = 0
    moduli, halfwidths = [], []
    for _ in range(trials):
        unitary = haar(12, rng)
        columns = rng.choice(12, 6, replace=False)
        sub = np.ascontiguousarray(unitary[np.ix_(ASCELLA_INPUT_MODES, columns)])
        exact = xq.permanent_cx(sub, "ryser")
        estimate, halfwidth = xq.estimate_permanent_cx(sub, DEFAULT_ITERATIONS)
        inside_complex += abs(estimate - exact) <= halfwidth
        inside_modulus += abs(abs(estimate) - abs(exact)) <= halfwidth
        moduli.append(abs(exact))
        halfwidths.append(halfwidth)
    out["coverage_6x6"] = {
        "trials": trials,
        "iterations": DEFAULT_ITERATIONS,
        "complex_distance_within_halfwidth": inside_complex / trials,
        "modulus_distance_within_halfwidth": inside_modulus / trials,
        "median_abs_permanent": float(np.median(moduli)),
        "median_halfwidth": float(np.median(halfwidths)),
        "hoeffding_99pc_halfwidth_at_unit_norm": math.sqrt(2 * math.log(2 / 0.01) / DEFAULT_ITERATIONS),
    }

    unitary = haar(12, rng)
    fixed = np.ascontiguousarray(unitary[:6, :6])
    out["halfwidth_vs_iterations"] = {str(n): xq.estimate_permanent_cx(fixed, n)[1] for n in (1000, 10000, 100000)}

    # Exact cost: fit log2(T) - n = c + k log2(n); Gray-code subset order gives k = 1, a plain subset sum k = 2.
    timing_rng = np.random.default_rng(timing_seed)
    timing: dict[str, dict[str, float]] = {"ryser": {}, "glynn": {}}
    for n in (14, 16, 18, 20, 22, 24):
        square = haar(n, timing_rng)
        for kind, table in timing.items():
            table[str(n)] = best_time(partial(xq.permanent_cx, square, kind))
    fits = {}
    for kind, table in timing.items():
        sizes = np.array([int(k) for k in table])
        excess = np.log2(np.array(list(table.values()))) - sizes
        slope, _ = np.polyfit(np.log2(sizes), excess, 1)
        fits[kind] = float(slope)
    out["exact_seconds"] = timing
    out["exact_fit_k"] = fits

    # Gurvits at the default iteration count against exact Glynn on n x n Haar unitaries.
    xq.set_seed(crossover_estimator_seed)
    crossover_rng = np.random.default_rng(crossover_matrix_seed)
    crossover = {}
    for n in (12, 16, 20, 24, 26):
        square = haar(n, crossover_rng)
        estimate, halfwidth = xq.estimate_permanent_cx(square, DEFAULT_ITERATIONS)
        crossover[str(n)] = {
            "gurvits_seconds": best_time(partial(xq.estimate_permanent_cx, square, DEFAULT_ITERATIONS), 1),
            "glynn_seconds": best_time(partial(xq.permanent_cx, square, "glynn"), 1),
            "abs_permanent": abs(xq.permanent_cx(square, "glynn")),
            "gurvits_halfwidth": halfwidth,
        }
    out["crossover"] = crossover
    return out


if __name__ == "__main__":
    target = Path(__file__).with_name("permanent_probe.json")
    target.write_text(json.dumps(main(), indent=1) + "\n", encoding="utf-8")
