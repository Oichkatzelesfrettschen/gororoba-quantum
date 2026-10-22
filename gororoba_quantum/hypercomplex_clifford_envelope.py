"""Exact Cl(0,8) left-operator envelope inside the standard sedenion table.

Signed permutation words and their integer Gram matrix certify a real matrix
algebra. Coefficient multiplication and operator composition remain distinct.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from cd_core import cd_sign
from parallel import ordered_map


@cache
def _generators() -> tuple[NDArray[np.int64], ...]:
    return tuple(
        np.asarray(
            [[cd_sign(16, unit, column) if row == unit ^ column else 0 for column in range(16)] for row in range(16)],
            dtype=np.int64,
        )
        for unit in range(1, 9)
    )


def _word(mask: int) -> NDArray[np.int64]:
    result = np.eye(16, dtype=np.int64)
    # Factors within a word have a fixed noncommuting order.
    for bit, operator in enumerate(_generators()):
        if mask & (1 << bit):
            result = result @ operator
    return result.reshape(-1)


def certificate() -> dict[str, Any]:
    operators = _generators()
    identity = np.eye(16, dtype=np.int64)
    stacked = np.asarray(operators, dtype=np.int64)
    squares = stacked @ stacked
    products = stacked[:, None] @ stacked[None, :]
    anticommutators = products + products.swapaxes(0, 1)
    pair_failures = np.any(anticommutators != 0, axis=(-2, -1))
    words = np.asarray(ordered_map(_word, list(range(256))), dtype=np.int64)
    # Every word is a signed permutation, so Gram entries have absolute bound 16.
    orthogonal = bool(np.array_equal(words @ words.T, 16 * np.eye(256, dtype=np.int64)))
    root = Path(__file__).resolve().parents[1]
    names = ("gororoba_quantum/cd_core.py", "gororoba_quantum/hypercomplex_clifford_envelope.py")
    return {
        "schema": "sedenion-clifford-envelope-v1",
        "evidence_kind": "exact finite integer operator certificate",
        "coefficient_dimension": 16,
        "generator_basis_indices": list(range(1, 9)),
        "square_failures": int(np.count_nonzero(np.any(squares != -identity, axis=(-2, -1)))),
        "anticommutator_failures": int(np.count_nonzero(np.triu(pair_failures, k=1))),
        "word_count": len(words),
        "hilbert_schmidt_orthogonal": orthogonal,
        "word_norm_squared": 16,
        "image_dimension": 256 if orthogonal else None,
        "left_encoding_is_product_homomorphism": bool(
            np.array_equal(operators[0] @ operators[1], cd_sign(16, 1, 2) * operators[2])
        ),
        "interpretation": "Cl(0,8) envelope M16(R); sedenion coefficients retain zero divisors and nonassociativity",
        "sources_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    record = certificate()
    if args.check:
        if json.loads(args.check.read_text()) != record:
            raise SystemExit("sedenion Clifford envelope differs from its exact source-bound replay")
        print("replayed 256 orthogonal Clifford words over exact integer matrices")
    elif args.out:
        payload = json.dumps(record, indent=1) + "\n"
        if args.out.exists() and args.out.read_text() != payload:
            raise SystemExit("refusing to replace different retained certificate bytes")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload)
    else:
        parser.error("--out or --check is required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
