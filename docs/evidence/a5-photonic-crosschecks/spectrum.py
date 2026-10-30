"""Resolve exact squared-singular spectra for the selected A5 witnesses."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import sympy as sym

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from a5_photonic_replay import WITNESSES  # noqa: E402

import cd_core  # noqa: E402
import parallel  # noqa: E402

RECORD = Path(__file__).with_name("named-source-spectrum-result.json")


def witness_spectrum(item: tuple) -> dict:
    terms, expected_nullity, *_ = item
    vector = [0] * 32
    for index, coefficient in terms:
        vector[index] = coefficient
    matrix = sym.Matrix(cd_core.left_mult_matrix_exact(32, vector))
    gram = matrix.T * matrix
    eigenvalues = gram.eigenvals()
    if any(not eigenvalue.is_Integer or eigenvalue < 0 for eigenvalue in eigenvalues):
        raise ValueError("the witness has an unexpected nonintegral squared singular value")
    counts = {str(value): int(multiplicity) for value, multiplicity in sorted(eigenvalues.items())}
    if counts.get("0", 0) != expected_nullity or sum(counts.values()) != 32:
        raise ValueError("squared singular multiplicities disagree with the exact nullity")
    alpha = sum(abs(coefficient) for _, coefficient in terms)
    expected_mean = sym.Rational(sum(coefficient**2 for _, coefficient in terms), alpha**2)
    measured_mean = sym.Rational(sym.trace(gram), 32 * alpha**2)
    if measured_mean != expected_mean:
        raise ValueError("uniform-input success does not match the coefficient identity")
    return {
        "terms": list(terms),
        "alpha": alpha,
        "squared_singular_multiplicities": counts,
        "uniform_basis_mean_success": str(measured_mean),
    }


def result() -> dict:
    return {
        "schema": "a5-witness-squared-spectra-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "replay_sha256": hashlib.sha256(Path(__file__).with_name("a5_photonic_replay.py").read_bytes()).hexdigest(),
        "cd_core_sha256": hashlib.sha256((ROOT / "gororoba_quantum/cd_core.py").read_bytes()).hexdigest(),
        "witnesses": parallel.ordered_map(witness_spectrum, list(WITNESSES), min_items=1),
        "boundary": "Exact classical matrix spectra; LCU probabilities assume the stated normalization.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group(required=True)
    options.add_argument("--write", action="store_true")
    options.add_argument("--check", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(result(), indent=2, sort_keys=True) + "\n"
    if args.write:
        if RECORD.exists() and RECORD.read_text() != encoded:
            raise ValueError("the retained spectrum differs; use a successor")
        RECORD.write_text(encoded)
    elif RECORD.read_text() != encoded:
        raise ValueError("spectrum differs from exact replay")
    print("Four exact A5 squared-singular spectra and uniform-input means pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
