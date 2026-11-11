"""Emit or replay exact A5 LCU, kernel-projector and finite-field falsifiers.

This is a deterministic classical check. It submits no provider job and makes
no circuit-depth, exact finite-field rank speedup or physical nullity claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import cd_core  # noqa: E402
import parallel  # noqa: E402
from cd_quantum_contracts import (  # noqa: E402
    NaturalLCU,
    basis_unit_properties,
    isotropy_counterexample,
    kernel_projector,
    modular_rank_counterexample,
)

SOURCES = (
    "gororoba_quantum/cd_core.py",
    "gororoba_quantum/cd_quantum_contracts.py",
    "scripts/check_a5_quantum_contracts.py",
)
WITNESSES = (("e1+e10", 1, 10, 1), ("e1-e10", 1, 10, -1), ("e25+e8", 25, 8, 1), ("e25-e8", 25, 8, -1))


def _basis(index: int) -> dict[str, int | bool]:
    return basis_unit_properties(32, index)


def _witness(task: tuple[str, int, int, int]) -> dict[str, Any]:
    name, first, second, sign = task
    coefficients = tuple(int(index == first) + sign * int(index == second) for index in range(32))
    matrix = cd_core.left_mult_matrix_exact(32, coefficients)
    encoding = NaturalLCU(32, coefficients)
    if encoding.selected_block() != tuple(tuple(value / encoding.alpha for value in row) for row in matrix):
        raise ValueError(f"{name}: SELECT does not encode the direct left action")
    certificate = kernel_projector(matrix, (2, 4))
    projector = [[str(value) for value in row] for row in certificate.projector]
    return {
        "name": name,
        "coefficients": list(coefficients),
        "alpha": str(encoding.alpha),
        "data_qubits": encoding.data_qubits,
        "selector_qubits": encoding.selector_qubits,
        "selected_block_matches_left_action": True,
        "gram_polynomial_roots": ["0", "2", "4"],
        "projector_polynomial_in_gram": ["1", "-3/4", "1/8"],
        "projector": projector,
        "projector_symmetric": True,
        "projector_idempotent": True,
        "left_action_times_projector_zero": True,
        "rank_over_Q": certificate.rank,
        "nullity_over_Q": certificate.nullity,
    }


def _isotropy(modulus: int) -> dict[str, object]:
    return isotropy_counterexample(32, 1, modulus)


def record() -> dict[str, Any]:
    """Recompute the finite exact witnesses and bind the producer identities."""
    basis = parallel.ordered_map(_basis, list(range(32)))
    if not all(row["skew_symmetric"] == (row["basis_index"] != 0) for row in basis):
        raise ValueError("an A5 imaginary basis left action failed skew symmetry")
    dense = NaturalLCU(32, tuple(range(1, 33)))
    if dense.normalization_ratio_upper_squared > 32:
        raise ValueError("the coefficient-norm LCU bound failed")
    small = ((1, 1, 0), (0, 0, 2))
    try:
        kernel_projector(small, (2, 3))
    except ValueError:
        wrong_root_rejected = True
    else:
        raise ValueError("an incorrect nonzero Gram root passed the projector certificate")
    return {
        "schema": "a5-quantum-contracts-v1",
        "arithmetic": "exact rational; modular residues only in the stated finite-field falsifiers",
        "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES},
        "basis_actions": basis,
        "dense_lcu": {
            "coefficients": [str(value) for value in dense.coefficients],
            "terms": len(dense.terms),
            "data_qubits": dense.data_qubits,
            "selector_qubits": dense.selector_qubits,
            "alpha": str(dense.alpha),
            "normalization_ratio_upper_squared": str(dense.normalization_ratio_upper_squared),
            "support_size_upper_bound_squared": len(dense.terms),
        },
        "kernel_filters": parallel.ordered_map(_witness, list(WITNESSES)),
        "isotropy_counterexamples": parallel.ordered_map(_isotropy, [32009, 32029]),
        "modular_rank_counterexamples": parallel.ordered_map(modular_rank_counterexample, [32009, 32029]),
        "wrong_gram_root_rejected": wrong_root_rejected,
        "boundary": (
            "Finite exact encoding and projector certificates; no QSVT compilation, gate budget, "
            "hardware run, universal A5 spectral theorem or finite-field rank speedup is established."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="require the retained JSON to equal the recomputed certificate")
    args = parser.parse_args()
    output = json.dumps(record(), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check is not None:
        if args.check.read_text() != output:
            raise ValueError("the retained A5 quantum-contract certificate differs from exact recomputation")
        print("A5 signed-permutation LCU, kernel filters and finite-field falsifiers agree exactly.")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
