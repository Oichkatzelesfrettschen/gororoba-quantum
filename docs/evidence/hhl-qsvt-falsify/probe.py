"""Falsifier for a proposed HHL/QSVT pipeline on 32-dimensional Cayley-Dickson left-multiplication matrices.

Measures, for L_a of A_5 (dim 32): condition number, nonzeros per row, number of Pauli terms in the 5-qubit Pauli
expansion, the LCU subnormalization alpha (1-norm of Pauli coefficients) against the spectral norm, and the CNOT count
of exact 5-qubit state preparation after transpilation. Zero divisors give kappa = infinity.

    "$PYTHON" docs/evidence/hhl-qsvt-falsify/probe.py --seed qrng:<draw>#<index> --seed-transpiler qrng:<draw>#<index>
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

import flint
import numpy as np

sys.path.insert(0, "gororoba_quantum")
import parallel  # noqa: E402
import qrng_seeds  # noqa: E402
from cd_core import left_mult_matrix, sedenion_zero_divisors  # noqa: E402

DIM = 32
OUT = Path(__file__).resolve().parent

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1])
PAULI = [I2, X, Y, Z]


def pauli_terms(m: np.ndarray) -> np.ndarray:
    coeffs = []
    for idx in itertools.product(range(4), repeat=5):
        p = PAULI[idx[0]]
        for k in idx[1:]:
            p = np.kron(p, PAULI[k])
        coeffs.append(np.trace(p.conj().T @ m) / DIM)
    return np.array(coeffs)


def stats(name: str, v: np.ndarray) -> dict[str, object]:
    m = np.array(left_mult_matrix(DIM, list(v)), dtype=float)
    s = np.linalg.svd(m, compute_uv=False)
    c = pauli_terms(m)
    nz = np.abs(c) > 1e-12
    return {
        "case": name,
        "nnz_per_row_max": int((np.abs(m) > 1e-12).sum(axis=1).max()),
        "sigma_max": float(s[0]),
        "sigma_min": float(s[-1]),
        "kappa": float(s[0] / s[-1]) if s[-1] > 1e-12 * s[0] else "inf",
        "rank": int((s > 1e-10 * s[0]).sum()),
        # exact integer rank (python-flint fmpz_mat) when a has integer coordinates
        "rank_exact": int(flint.fmpz_mat([[int(round(x)) for x in row] for row in m]).rank())
        if np.allclose(v, np.round(v))
        else None,
        "pauli_terms": int(nz.sum()),
        "lcu_ancillas": int(np.ceil(np.log2(nz.sum()))),
        "alpha_l1": float(np.abs(c).sum()),
        "alpha_over_norm": float(np.abs(c).sum() / s[0]),
    }


def stats_case(case: tuple[str, np.ndarray]) -> dict[str, object]:
    return stats(*case)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    qrng_seeds.add_seed_argument(ap, "--seed", required=True, help="matrix and vector draws, qrng:<draw>#<index>")
    qrng_seeds.add_seed_argument(ap, "--seed-transpiler", required=True, help="transpiler seed, qrng:<draw>#<index>")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    # Every random input is drawn first, in one fixed order; the independent statistics are then mapped in parallel.
    cases: list[tuple[str, np.ndarray]] = [(f"gaussian-{t}", rng.standard_normal(DIM)) for t in range(5)]
    for _ in range(3):  # sparse: 2 basis elements, like a box-kite zero-divisor support
        v = np.zeros(DIM)
        i, j = rng.choice(DIM, 2, replace=False)
        v[i], v[j] = 1.0, rng.choice([-1.0, 1.0])
        cases.append((f"two-term-{i}-{j}", v))
    # Sedenion zero divisors embedded in A_5 (the sedenions are the first 16 coordinates of A_5)
    zd = sedenion_zero_divisors()[0]
    (za, zb), _second, _sign = zd
    for sign, label in ((1.0, "+"), (-1.0, "-")):
        v = np.zeros(DIM)
        v[za], v[zb] = 1.0, sign
        cases.append((f"sedenion-zd-{za}{label}{zb}", v))
    g = rng.standard_normal((DIM, DIM))
    b = rng.standard_normal(DIM)
    rows: list[dict[str, object]] = list(parallel.ordered_map(stats_case, cases, min_items=2))

    # random dense SPD 32x32 as in the proposal's demonstration
    spd = g @ g.T + DIM * np.eye(DIM)
    s = np.linalg.svd(spd, compute_uv=False)
    c = pauli_terms(spd)
    rows.append(
        {
            "case": "random-spd",
            "kappa": float(s[0] / s[-1]),
            "pauli_terms": int((np.abs(c) > 1e-12).sum()),
            "alpha_over_norm": float(np.abs(c).sum() / s[0]),
        }
    )

    # exact 5-qubit state preparation cost
    from qiskit import QuantumCircuit, transpile  # noqa: E402
    from qiskit.circuit.library import StatePreparation  # noqa: E402

    b /= np.linalg.norm(b)
    qc = QuantumCircuit(5)
    qc.append(StatePreparation(b), range(5))
    tq = transpile(qc, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3, seed_transpiler=args.seed_transpiler)
    ops = tq.count_ops()
    rows.append(
        {
            "case": "stateprep-5q",
            "cz": int(ops.get("cz", 0)),
            "depth": tq.depth(),
            "cz_depth": tq.depth(lambda g: g.operation.num_qubits == 2),
        }
    )
    script = qrng_seeds.repo_relative(__file__)
    record = {
        "seed_source": [
            qrng_seeds.seed_record(script, "--seed", "hhl-qsvt-falsify", args.seed_source),
            qrng_seeds.seed_record(script, "--seed-transpiler", "hhl-qsvt-falsify", args.seed_transpiler_source),
        ],
        "rows": rows,
    }
    (OUT / "probe.json").write_text(json.dumps(record, indent=1) + "\n")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
