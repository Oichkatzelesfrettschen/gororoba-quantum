"""Check selected A5 rank witnesses and a dimension-six basis construction exactly."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import sympy as sym
from flint import fmpz_mat

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import cd_core  # noqa: E402
import parallel  # noqa: E402

RECORD = Path(__file__).with_name("result.json")
WITNESSES = (
    (((1, 1), (9, 1)), 0, "2", "0", "4"),
    (((1, 1), (10, 1)), 8, "2", "1", "0"),
    (((1, 1), (18, 1)), 12, "0", "0", "0"),
    (((1, 1), (10, -1), (18, 1), (25, 1)), 16, "0", "0", "0"),
)


def rank_witness(item: tuple) -> dict:
    terms, expected, q_expected, delta_expected, g_expected = item
    vector = [0] * 32
    for index, coefficient in terms:
        vector[index] = coefficient
    matrix = cd_core.left_mult_matrix_exact(32, vector)
    integers = [[int(value) for value in row] for row in matrix]
    if any(value != integers[i][j] for i, row in enumerate(matrix) for j, value in enumerate(row)):
        raise ValueError("the integral basis witness has a nonintegral multiplication matrix")
    rank = fmpz_mat(integers).rank()
    if rank != sym.Matrix(integers).rank() or 32 - rank != expected:
        raise ValueError("the independent exact rank checks differ")
    z = [sym.Integer(vector[k]) + sym.I * vector[16 + k] for k in range(1, 16)]
    u, mu, v = z[:7], z[7], z[8:]

    def inner(first: list, second: list) -> sym.Expr:
        return sum((x * y for x, y in zip(first, second, strict=True)), sym.Integer(0))

    U, V, W = inner(u, u), inner(v, v), inner(u, v)
    Q = sym.expand(U + mu**2 + V)
    delta = sym.expand(U * V - W**2)
    G = sym.expand(Q**2 - 4 * delta)
    if (str(Q), str(delta), str(G)) != (q_expected, delta_expected, g_expected):
        raise ValueError("the witness does not match the recorded polynomial invariants")
    return {
        "terms": list(terms),
        "nullity": expected,
        "U": str(U),
        "V": str(V),
        "W": str(W),
        "mu": str(mu),
        "Q": str(Q),
        "delta": str(delta),
        "G": str(G),
    }


def basis_checks(mutation: bool = False) -> list[dict]:
    omega = (-1 + sym.I * sym.sqrt(3)) / 2
    hadamard = sym.Matrix([[1, 1], [1, -1]]) / sym.sqrt(2)
    fourier = sym.Matrix([[omega ** (j * k) for k in range(3)] for j in range(3)]) / sym.sqrt(3)
    qubit_phase = sym.diag(1, sym.I)
    qutrit_phase = sym.eye(3) if mutation else sym.diag(1, omega, omega)
    bases = (
        sym.eye(6),
        sym.kronecker_product(hadamard, fourier),
        sym.kronecker_product(qubit_phase * hadamard, qutrit_phase * fourier),
    )
    output = []
    for first in range(3):
        for second in range(first, 3):
            transition = bases[first].conjugate().T * bases[second]
            actual = transition.applyfunc(lambda z: sym.simplify(sym.expand_complex(z * sym.conjugate(z))))
            expected = sym.eye(6) if first == second else sym.ones(6) / 6
            if actual != expected:
                raise ValueError(f"basis overlap fails for {first}, {second}")
            output.append({"bases": [first, second], "squared_overlap": "identity" if first == second else "1/6"})
    return output


def result() -> dict:
    rows = parallel.ordered_map(rank_witness, list(WITNESSES), min_items=1)
    overlaps = basis_checks()
    try:
        basis_checks(mutation=True)
    except ValueError:
        mutation_detected = True
    else:
        raise ValueError("the qutrit phase mutation escaped the basis check")
    return {
        "schema": "a5-photonic-crosschecks-v1",
        "cd_core_sha256": hashlib.sha256((ROOT / "gororoba_quantum/cd_core.py").read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "witnesses": rows,
        "basis_overlaps": overlaps,
        "qutrit_phase_mutation_detected": mutation_detected,
        "boundary": "Four exact witnesses and one explicit basis triple; no universal rank or hardware inference.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(result(), indent=2, sort_keys=True) + "\n"
    if args.write:
        if RECORD.exists() and RECORD.read_text() != encoded:
            raise ValueError("the retained record differs; use a successor rather than replacing it")
        RECORD.write_text(encoded)
    elif RECORD.read_text() != encoded:
        raise ValueError("the retained record differs from exact replay")
    print("Four A5 witnesses, three dimension-six bases and a phase mutation pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
