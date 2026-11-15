"""The real nullity of left multiplication by a doubly pure element, through the bordered matrix A(z, conjugate(z)).

A doubly pure element y of the 32-dimensional Cayley-Dickson algebra (no e_0 and no e_16 component) has complex
coordinates z_k = y_k + i y_(16 + k), k = 1..15. Two modules build the bordered 16 x 16 skew matrix A(z, conjugate(z)):
`bordered_matrix` of scripts/a5_stiefel_pfaffian_germs.py, on which A5-364 proves the transport
phi(y x) = A(z, conjugate(z)) conjugate(phi(x)), phi(r, s) = r + i conj(s), and `_bordered_matrix` of
docs/evidence/a5-kernel-bundles/kernel_frames.py, whose lower 15 x 15 block is the M(z) of the kernel-plane records.

Checked exactly:

1. constructors: the two matrices are equal entry by entry over Z[z_1..z_15, conjugates], the conjugate of z_k a free
   symbol.
2. left_matrices: `left_matrix` of the first module equals `cd_core.left_mult_matrix_exact` at the 32 basis elements;
   both are linear in y, so they agree at every y.
3. transport: the identity of A5-364 holds at the 30 doubly pure basis elements y and the 32 basis vectors x; y -> L_y
   and y -> A(z, conjugate(z)) are real-linear, so it holds at every doubly pure y.

Consequence (argument). x -> conjugate(phi(x)) is a real-linear bijection of R^32 onto C^16, so the real kernel of
L_y is carried onto the complex subspace ker A(z, conjugate(z)) and has twice its complex dimension. For nonzero y,
conjugate(z).z is positive and ker A(z, conjugate(z)) = {0} x (ker M(z) n conjugate(z)-perp) has dimension
nullity M(z) - 1 (A5-550), so the real nullity of L_y is 2 (nullity M(z) - 1). A real kernel vector x of L_y is
doubly pure, because the first coordinate of conjugate(phi(x)) vanishes, so the statement applies to the kernel
vectors too; M has real coefficients, so nullity M(conjugate(p)) = nullity M(p) and the choice of conjugate in the
coordinates of a kernel vector does not matter.

Falsifier: an entry where the two constructors differ, a basis element where the two left matrices differ, or a failed
transport case.

Run from the repository root:
"$PYTHON" docs/evidence/a5-kernel-bundles-residuals/real_nullity_bordered_matrix.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLES = HERE.parent / "a5-kernel-bundles"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(BUNDLES))

import a5_stiefel_pfaffian_germs as germs  # noqa: E402
import kernel_frames as frames  # noqa: E402

import parallel  # noqa: E402
from cd_core import left_mult_matrix_exact  # noqa: E402

SCHEMA = "a5-kernel-bundles-residuals-real-nullity-bordered-matrix-v1"
RECORD = HERE / "real-nullity-bordered-matrix-result.json"
SOURCE_PATHS = (
    HERE / "real_nullity_bordered_matrix.py",
    ROOT / "scripts" / "a5_stiefel_pfaffian_germs.py",
    BUNDLES / "kernel_frames.py",
    ROOT / "gororoba_quantum" / "cd_core.py",
)
IDENTITIES = ("constructors", "left_matrices", "transport")
TRANSPORT_CASES = 30


def constructors_agree() -> bool:
    """The two bordered matrices at symbolic z, with the conjugate of z_k the symbol w_k."""
    z = sp.symbols(f"z1:{germs.HALF}")
    w = sp.symbols(f"w1:{germs.HALF}")
    conjugates = dict(zip([sp.conjugate(value) for value in z], w, strict=True))
    first = frames._bordered_matrix(z).xreplace(conjugates)
    second = germs.bordered_matrix(z, w, germs.SIGNS16)
    rows: list[tuple[list[Any], list[Any]]] = []
    for row in range(germs.HALF):
        # The corner and the diagonal of the second matrix hold that module's own zero.
        values = [sp.Integer(0) if isinstance(e, germs.GQ) and e == germs.ZERO else e for e in second[row]]
        if any(isinstance(value, germs.GQ) for value in values):
            return False
        rows.append((list(first[row, :]), values))
    return all(parallel.ordered_map(_rows_agree, rows, min_items=2))


def _rows_agree(pair: tuple[list[Any], list[Any]]) -> bool:
    return all(sp.expand(a - b) == 0 for a, b in zip(*pair, strict=True))


def left_matrix_agrees(index: int) -> bool:
    y = [int(position == index) for position in range(germs.DIM)]
    return [list(row) for row in left_mult_matrix_exact(germs.DIM, y)] == germs.left_matrix(y)


def identity(name: str) -> Any:
    if name == "constructors":
        return constructors_agree()
    if name == "left_matrices":
        return all(parallel.ordered_map(left_matrix_agrees, list(range(germs.DIM)), min_items=2))
    if name == "transport":
        moved = germs.transport()
        return [moved["imaginary_basis_elements"], moved["agreeing"]]
    raise ValueError(name)


def _inputs() -> dict[str, str]:
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in SOURCE_PATHS}


def compute() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": _inputs(),
        "identities": {name: identity(name) for name in IDENTITIES},
        "pass": True,
    }
    record["pass"] = verdict(record) == []
    return record


def expected_record() -> dict[str, Any]:
    """The record that the constants of this module determine, with the digests of the files as they are."""
    return {
        "schema": SCHEMA,
        "inputs": _inputs(),
        "identities": {
            "constructors": True,
            "left_matrices": True,
            "transport": [TRANSPORT_CASES, TRANSPORT_CASES],
        },
        "pass": True,
    }


def verdict(record: dict[str, Any]) -> list[str]:
    """The reasons the record fails its own rules; empty when it passes. The comparison is on serialized text."""
    expected = expected_record()
    problems = []
    if json.dumps(record.get("inputs"), sort_keys=True) != json.dumps(expected["inputs"], sort_keys=True):
        problems.append("the input digests differ from the files")
    messages = {
        "constructors": "the two bordered-matrix constructors differ",
        "left_matrices": "the two left-multiplication matrices differ at a basis element",
        "transport": "the transport identity fails at a doubly pure basis element",
    }
    identities = record.get("identities")
    for name, message in messages.items():
        found = identities.get(name) if isinstance(identities, dict) else None
        if json.dumps(found) != json.dumps(expected["identities"][name]):
            problems.append(message)
    if record.get("pass") is not True:
        problems.append("the record states that it fails")
    if not problems and _serialized(record) != _serialized(expected):
        problems.append("the record differs from the record the constants determine")
    return problems


def _serialized(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = compute()
    if args.write:
        RECORD.write_text(_serialized(record), encoding="utf-8")
    elif RECORD.read_text(encoding="utf-8") != _serialized(record):
        raise SystemExit(f"{RECORD.name} differs from the recomputation")
    problems = verdict(record)
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"pass: {len(record['identities'])} identities, {record['identities']['transport'][1]} transport cases")


if __name__ == "__main__":
    main()
