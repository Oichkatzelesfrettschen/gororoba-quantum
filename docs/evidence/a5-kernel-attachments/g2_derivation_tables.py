"""The 14 G_2 derivations of the sedenions as tables of Gaussian integers on the basis e_0, ..., e_15.

`kernel_equivariance.py` builds the 14 derivations of G_2 as 15 x 15 matrices on the pure coordinates e_1, ..., e_15
of the sedenions with coefficients in Q(i) ("original coordinates"): the split-coordinate matrix diag(d, 0, d) of a
7 x 7 octonion derivation d, conjugated by the phase map. This producer writes each one as the images D(e_0), ...,
D(e_15), 16 coordinates each with a real and an imaginary integer part, with D(e_0) = 0, and verifies on the table
itself:

- the Leibniz rule D(e_a e_b) = D(e_a) e_b + e_a D(e_b) on all 256 pairs of basis units, for the product
  e_a e_b = cd_sign(16, a, b) e_(a xor b) of `gororoba_quantum/cd_core.py`; both sides are bilinear, so the rule
  holds on the whole algebra over every commutative ring that contains the entries;
- every entry is a Gaussian integer, D(e_0) = 0 and no image has an e_0 coordinate;
- the matrix of D is skew;
- the 14 tables are linearly independent over Q(i).

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/g2_derivation_tables.py [--check]
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import kernel_equivariance as equivariance  # noqa: E402

import parallel  # noqa: E402
from cd_core import cd_sign  # noqa: E402

RECORD = HERE / "g2-derivation-tables.json"
SCHEMA = "gororoba.a5.g2-derivation-tables/1"
INPUTS = (
    "docs/evidence/a5-kernel-attachments/g2_derivation_tables.py",
    "docs/evidence/a5-kernel-attachments/kernel_equivariance.py",
    "docs/evidence/a5-strata-regularity/verify_regularity_independent.py",
    "gororoba_quantum/cd_core.py",
)
DIMENSION = 16
COUNT = 14
CONVENTION = (
    "images[k] is D(e_k) as 16 coordinates [real part, imaginary part] on e_0, ..., e_15; "
    "e_a e_b = cd_sign(16, a, b) e_(a xor b) in gororoba_quantum/cd_core.py"
)

Entry = tuple[int, int]
Table = list[list[Entry]]


def _product(left: Entry, right: Entry) -> Entry:
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def table_of(matrix: equivariance.GaussianMatrix) -> Table:
    """Column c - 1 of the 15 x 15 matrix is the image of e_c; e_0 maps to zero."""
    table: Table = [[(0, 0)] * DIMENSION]
    for column in range(DIMENSION - 1):
        image: list[Entry] = [(0, 0)]
        for row in range(DIMENSION - 1):
            real, imaginary = matrix[row][column]
            if Fraction(real).denominator != 1 or Fraction(imaginary).denominator != 1:
                raise RuntimeError("a derivation entry is not a Gaussian integer")
            image.append((int(real), int(imaginary)))
        table.append(image)
    return table


def leibniz_failures(table: Table) -> int:
    """The pairs (a, b) of basis units with D(e_a e_b) different from D(e_a) e_b + e_a D(e_b)."""
    failures = 0
    for first in range(DIMENSION):
        for second in range(DIMENSION):
            sign = cd_sign(DIMENSION, first, second)
            expected = [(sign * real, sign * imaginary) for real, imaginary in table[first ^ second]]
            found = [[0, 0] for _ in range(DIMENSION)]
            for index, (real, imaginary) in enumerate(table[first]):
                # D(e_first) e_second
                if (real, imaginary) != (0, 0):
                    factor = cd_sign(DIMENSION, index, second)
                    found[index ^ second][0] += factor * real
                    found[index ^ second][1] += factor * imaginary
            for index, (real, imaginary) in enumerate(table[second]):
                # e_first D(e_second)
                if (real, imaginary) != (0, 0):
                    factor = cd_sign(DIMENSION, first, index)
                    found[first ^ index][0] += factor * real
                    found[first ^ index][1] += factor * imaginary
            failures += [tuple(value) for value in found] != expected
    return failures


def is_skew(table: Table) -> bool:
    return all(
        table[column][row] == (-table[row][column][0], -table[row][column][1])
        for row in range(DIMENSION)
        for column in range(DIMENSION)
    )


def span_rank(tables: list[Table]) -> int:
    vectors = [
        tuple((Fraction(real), Fraction(imaginary)) for image in table for real, imaginary in image) for table in tables
    ]
    return int(equivariance.kernel_lemma._columns_rank(vectors))


def noninteger_entries(record: dict[str, Any]) -> list[str]:
    """Derivations with a coordinate that is not a pair of integers; `int` would truncate a fraction to a table that
    passes."""
    return [
        f"{derivation.get('id')}: a coefficient is not a pair of integers"
        for derivation in record.get("derivations", [])
        if not all(
            isinstance(entry, list) and len(entry) == 2 and all(type(part) is int for part in entry)
            for image in derivation.get("images", [])
            for entry in image
        )
    ]


def tables_of(record: dict[str, Any]) -> list[Table]:
    return [
        [[(int(real), int(imaginary)) for real, imaginary in image] for image in derivation["images"]]
        for derivation in record.get("derivations", [])
    ]


def table_problems(item: tuple[str, int | None, bool | None, Table]) -> list[str]:
    """Failures of one table: shape, e_0, the Leibniz rule on 256 pairs, skewness, the entry count, the real flag."""
    label, recorded_entries, recorded_real, table = item
    if [len(image) for image in table] != [DIMENSION] * DIMENSION:
        return [f"{label}: the table is not {DIMENSION} by {DIMENSION}"]
    found: list[str] = []
    if any(entry != (0, 0) for entry in table[0]) or any(image[0] != (0, 0) for image in table):
        found.append(f"{label}: e_0 enters the table")
    failures = leibniz_failures(table)
    if failures:
        found.append(f"{label}: the Leibniz rule fails on {failures} pairs of basis units")
    if not is_skew(table):
        found.append(f"{label}: the matrix is not skew")
    if recorded_entries != sum(entry != (0, 0) for image in table for entry in image):
        found.append(f"{label}: the count of nonzero entries differs")
    if recorded_real is not all(entry[1] == 0 for image in table for entry in image):
        found.append(f"{label}: the real flag differs from the entries")
    return found


def regenerated() -> list[Table]:
    return [
        table_of(equivariance.to_original_coordinates(equivariance.split_matrix_of_derivation(derivation)))
        for derivation in equivariance.regularity.DERS
    ]


def problems(record: dict[str, Any]) -> list[str]:
    """Every way the record fails the claim; an empty list is a pass."""
    found: list[str] = []
    if record.get("schema") != SCHEMA:
        found.append("schema differs")
    if record.get("ring") != "Z[i]" or record.get("dimension") != DIMENSION:
        found.append("the ring or the dimension differs")
    if record.get("convention") != CONVENTION:
        found.append("the convention differs")
    derivations = record.get("derivations", [])
    if [derivation.get("id") for derivation in derivations] != [f"g2_derivation_{n}" for n in range(1, COUNT + 1)]:
        found.append(f"the derivations are not the {COUNT} in order")
        return found
    noninteger = noninteger_entries(record)
    if noninteger:
        return found + noninteger
    tables = tables_of(record)
    items = [
        (derivation["id"], derivation.get("nonzero_entries"), derivation.get("real"), table)
        for derivation, table in zip(derivations, tables, strict=True)
    ]
    for table_found in parallel.ordered_map(table_problems, items, min_items=2):
        found += table_found
    if not any("not 16 by 16" in problem for problem in found):
        rank = span_rank(tables)
        if rank != COUNT or record.get("span_rank") != COUNT:
            found.append(f"the span of the tables has rank {rank}, recorded {record.get('span_rank')}")
    if record.get("pass") is not (found == []):
        found.append("the pass flag differs from the verdict")
    return found


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    tables = regenerated()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "ring": "Z[i]",
        "dimension": DIMENSION,
        "convention": CONVENTION,
        "inputs": {name: _digest(ROOT / name) for name in INPUTS},
        "derivations": [
            {
                "id": f"g2_derivation_{number}",
                "nonzero_entries": sum(entry != (0, 0) for image in table for entry in image),
                "real": all(entry[1] == 0 for image in table for entry in image),
                "images": [[list(entry) for entry in image] for image in table],
            }
            for number, table in enumerate(tables, 1)
        ],
        "span_rank": span_rank(tables),
        "pass": True,
    }
    record["pass"] = problems(record) == []
    return record


def record_text(record: dict[str, Any]) -> str:
    """The record as JSON with each image D(e_k) on one line."""
    images = [image for derivation in record["derivations"] for image in derivation["images"]]
    outline = dict(record)
    outline["derivations"] = [
        {**derivation, "images": [f"@image{number * DIMENSION + index}@" for index in range(DIMENSION)]}
        for number, derivation in enumerate(record["derivations"])
    ]
    text = json.dumps(outline, indent=1)
    for position, image in enumerate(images):
        text = text.replace(f'"@image{position}@"', json.dumps(image, separators=(",", ":")))
    return text + "\n"


def main() -> None:
    if "--check" in sys.argv[1:]:
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        found = problems(record)
        for name in INPUTS:
            if record["inputs"].get(name) != _digest(ROOT / name):
                found.append(f"input digest of {name} differs")
        if tables_of(record) != regenerated():
            found.append("the tables differ from the matrices of kernel_equivariance.py")
        if found:
            raise SystemExit("\n".join(found))
        print("g2-derivation-tables.json: pass")
        return
    record = build()
    found = problems(record)
    RECORD.write_text(record_text(record), encoding="utf-8")
    print(json.dumps({"pass": record["pass"], "problems": found}, indent=1))
    if found:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
