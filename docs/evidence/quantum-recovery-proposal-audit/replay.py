"""Recompute the computational claims of the quantum recovery proposal.

Usage: replay.py REPO_ROOT POCKELS_CSV > result.json

REPO_ROOT supplies gororoba_quantum/cd_core.py, the sedenion specification.
POCKELS_CSV is Fig4a_pockels.csv of Zenodo record 15653571; the replay
refuses a file whose MD5 differs from the record's published checksum.
"""

import csv
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

POCKELS_MD5 = "9f29ac811cd48bd68556939497cb4dbe"

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
PAULI = {"I": I2, "X": X, "Y": 1j * X @ Z, "Z": Z}


def kron(ops):
    out = np.ones((1, 1), dtype=complex)
    for op in ops:
        out = np.kron(out, op)
    return out


def five_qubit_isometry():
    """Encoding isometry of the [[5,1,3]] code with stabilizers XZZXI and its cyclic shifts."""
    proj = np.eye(32, dtype=complex)
    for word in ("XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"):
        proj = proj @ (np.eye(32) + kron(PAULI[c] for c in word)) / 2
    weights, vectors = np.linalg.eigh(proj)
    code = vectors[:, weights > 0.5]
    z_logical = kron([Z] * 5)
    zw, zv = np.linalg.eigh(code.conj().T @ z_logical @ code)
    zero = code @ zv[:, np.argmax(zw)]
    one = kron([X] * 5) @ zero
    return np.stack([zero, one], axis=1)


def erasure_kl_deviation(iso, erased):
    """Largest deviation of E_a^dag E_b from delta_ab 2^-m I over the erased register basis."""
    m = len(erased)
    order = [q for q in range(5) if q not in erased] + list(erased)
    ops = iso.reshape([2] * 5 + [2]).transpose(order + [5]).reshape(2 ** (5 - m), 2**m, 2)
    deviation = 0.0
    for a, b in itertools.product(range(2**m), repeat=2):
        target = 2.0**-m * I2 if a == b else np.zeros((2, 2))
        deviation = max(deviation, float(np.abs(ops[:, a, :].conj().T @ ops[:, b, :] - target).max()))
    return deviation


def region_distinguishability(iso, region):
    """Largest trace distance between reduced states of the logical Pauli eigenstates on a region."""
    rest = [q for q in range(5) if q not in region]
    s = 1 / math.sqrt(2)
    logical = [np.array([1, 0]), np.array([0, 1]), np.array([s, s]), np.array([s, 1j * s])]
    reduced = []
    for state in logical:
        psi = (iso @ state).reshape([2] * 5).transpose(list(region) + rest).reshape(2 ** len(region), -1)
        reduced.append(psi @ psi.conj().T)
    return max(0.5 * float(np.abs(np.linalg.eigvalsh(a - b)).sum()) for a, b in itertools.combinations(reduced, 2))


def queue_optimum(mean, delta, laplace):
    """Analytic and grid optima of R(lambda) = lambda E[exp(-delta T)] for a stationary M/G/1 queue."""
    c = (1 - laplace) / (delta * mean)
    grid = np.linspace(1e-6, 1 / mean - 1e-6, 2_000_001)
    reward = grid * (1 - grid * mean) * delta * laplace / (delta - grid * (1 - laplace))
    return {
        "c": c,
        "lambda_star_analytic": 1 / (mean * (1 + math.sqrt(1 - c))),
        "lambda_star_grid": float(grid[np.argmax(reward)]),
        "reward_star": float(reward.max()),
    }


def h3_jordan_witness(dim, limit):
    """First Hermitian 3x3 pair over the dim-algebra, units descending, that breaks the Jordan identity."""
    from cd_core import cd_multiply_exact

    zero = [Fraction(0)] * dim

    def unit(index):
        vector = list(zero)
        vector[index] = Fraction(1)
        return vector

    def conj(a):
        return [a[0]] + [-v for v in a[1:]]

    def herm(units):
        a, b, c = (unit(u) for u in units)
        return [[zero, a, b], [conj(a), zero, c], [conj(b), conj(c), zero]]

    def matmul(left, right):
        return [
            [
                [sum(t) for t in zip(*[cd_multiply_exact(dim, left[i][k], right[k][j]) for k in range(3)], strict=True)]
                for j in range(3)
            ]
            for i in range(3)
        ]

    def jordan(left, right):
        lr, rl = matmul(left, right), matmul(right, left)
        return [[[(x + y) / 2 for x, y in zip(lr[i][j], rl[i][j], strict=True)] for j in range(3)] for i in range(3)]

    tried = 0
    descending = list(range(dim - 1, 0, -1))
    for units_a in itertools.product(descending, repeat=3):
        a = herm(units_a)
        a2 = jordan(a, a)
        for units_b in itertools.product(descending, repeat=3):
            tried += 1
            if tried > limit:
                return {"found": False, "pairs_tried": limit}
            b = herm(units_b)
            lhs, rhs = jordan(jordan(a, b), a2), jordan(a, jordan(b, a2))
            residual = [
                [i, j, n, str(lhs[i][j][n] - rhs[i][j][n])]
                for i in range(3)
                for j in range(3)
                for n in range(dim)
                if lhs[i][j][n] != rhs[i][j][n]
            ]
            if residual:
                return {"found": True, "a_offdiag_units": units_a, "b_offdiag_units": units_b, "residual": residual}
    return {"found": False, "pairs_tried": tried}


def pockels_sweeps(path):
    with open(path, newline="") as handle:
        rows = list(csv.reader(handle))
    sweeps = []
    for col in range(0, len(rows[0]), 2):
        points = [(float(r[col]), float(r[col + 1])) for r in rows[1:] if len(r) > col + 1 and r[col] and r[col + 1]]
        field, response = np.array(points).T
        order = np.argsort(field, kind="stable")
        sweeps.append((field[order], response[order]))
    return sweeps


def landau_response(params, field):
    """|r| = A |z| / (1 + 3 z^2) with z the real root of z^3 + z = (E - E_off) / E_s."""
    amplitude, scale, offset = params
    u = (field - offset) / scale
    root = np.sqrt(u**2 / 4 + 1 / 27)
    z = np.cbrt(u / 2 + root) + np.cbrt(u / 2 - root)
    return amplitude * np.abs(z) / (1 + 3 * z**2)


def landau_fit(field, response):
    best = None
    for a0, s0, o0 in itertools.product(
        (300.0, 1000.0, 2000.0, 4000.0, 8000.0), (0.003, 0.01, 0.03, 0.1, 0.3), (-0.01, 0.0, 0.01)
    ):
        fit = least_squares(lambda p: landau_response(p, field) - response, (a0, s0, o0), x_scale=[1000, 0.1, 0.01])
        if best is None or fit.cost < best.cost:
            best = fit
    params = best.x.copy()
    params[1] = abs(params[1])
    return params


def rmse(params, field, response):
    return float(np.sqrt(np.mean((landau_response(params, field) - response) ** 2)))


def blocked_rmse(field, response, blocks=5):
    squared = []
    for test in np.array_split(np.arange(len(field)), blocks):
        train = np.setdiff1d(np.arange(len(field)), test)
        params = landau_fit(field[train], response[train])
        squared.extend((landau_response(params, field[test]) - response[test]) ** 2)
    return float(np.sqrt(np.mean(squared)))


def main():
    repo, csv_path = Path(sys.argv[1]), Path(sys.argv[2])
    sys.path.insert(0, str(repo / "gororoba_quantum"))
    from cd_core import cd_multiply_exact

    digest = hashlib.md5(csv_path.read_bytes(), usedforsecurity=False).hexdigest()
    if digest != POCKELS_MD5:
        raise SystemExit(f"Fig4a_pockels.csv md5 {digest} differs from the record's {POCKELS_MD5}")

    iso = five_qubit_isometry()
    subsets = [s for m in range(6) for s in itertools.combinations(range(5), m)]
    deviations = {s: erasure_kl_deviation(iso, s) for s in subsets}
    u, v = [0] * 16, [0] * 16
    u[1], u[10], v[4], v[15] = 1, 1, 1, -1

    sweeps = pockels_sweeps(csv_path)
    params = [landau_fit(f, r) for f, r in sweeps]
    result = {
        "five_qubit_code": {
            "isometry_residual": float(np.abs(iso.conj().T @ iso - I2).max()),
            "erasure_subsets": len(subsets),
            "max_kl_deviation_at_most_two_erasures": max(d for s, d in deviations.items() if len(s) <= 2),
            "min_kl_deviation_three_or_more_erasures": min(d for s, d in deviations.items() if len(s) >= 3),
            "region_trace_distance": {
                str(r): region_distinguishability(iso, list(r)) for r in ((0, 1, 2), (2, 3, 4), (2,), (3, 4))
            },
        },
        "queue_exponential_service": queue_optimum(1.0, 0.5, 1 / 1.5),
        "queue_deterministic_service": queue_optimum(1.0, 0.5, math.exp(-0.5)),
        "pinching_population_p0_t1": 0.5 * (1 + math.exp(-2)),
        "pinching_sequence_p0": {n: 0.5 * (1 + math.cos(2 / n) ** n) for n in (1, 2, 4, 8, 16)},
        "zero_divisor_e1_plus_e10_times_e4_minus_e15": [int(x) for x in cd_multiply_exact(16, u, v)],
        "h3_jordan_sedenion": h3_jordan_witness(16, 4000),
        "h3_jordan_octonion": h3_jordan_witness(8, 4000),
        "pockels": {
            "md5": digest,
            "sweeps": [
                {
                    "column_pair": i,
                    "points": len(f),
                    "field_range_mv_per_m": [float(f.min()), float(f.max())],
                    "peak_field_and_response": [float(f[np.argmax(r)]), float(r.max())],
                    "amplitude_scale_offset": params[i].tolist(),
                    "rmse_pm_per_v": rmse(params[i], f, r),
                    "r2": float(1 - np.sum((landau_response(params[i], f) - r) ** 2) / np.sum((r - r.mean()) ** 2)),
                    "blocked5_rmse_pm_per_v": blocked_rmse(f, r),
                }
                for i, (f, r) in enumerate(sweeps)
            ],
            "cross_sweep_rmse_fit_row_predict_column": [[rmse(p, f, r) for f, r in sweeps] for p in params],
        },
    }
    json.dump(result, sys.stdout, indent=1, default=list)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
