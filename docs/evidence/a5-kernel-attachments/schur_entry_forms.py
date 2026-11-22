"""Every Schur-entry form of the eight first-order-resolved A_5 incidences, over Q(i) and modulo 32009.

Rows 2c (first_order_normal_cones.py) and 2i (holomorphic_gauss_fibers.py) retain only a basis of the entry forms of
the first-order Schur matrix: 7 of the 15 entries of the 6 x 6 skew effective form of 2c and 7 of the 21 entries of
the 7 x 7 skew leading Schur form of 2i. This producer imports both modules, rebuilds each skew matrix at the
retained basepoint and slice columns, and writes all 15 and all 21 entry forms of each incidence as coefficient rows
over the slice variables t1, ..., tn: pairs of rational strings (real part, imaginary part) over Q(i), and residues
modulo 32009 under i = 10754 (the residue of every Q(i) coefficient, each denominator a unit).

Checks at build time: the 2i full matrix reproduces the retained coordinate_sha256 of its numerator coordinates, each
retained basis (2i linear_coordinate_matrix, 2c coordinate_forms) reappears at its retained indices, both matrices
are skew, and every modular row is the residue of its Q(i) row. attaching_maps_resolved.py reads this record and
decides the rank-four Pfaffians of both matrices on the tangent cone.

Run from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/schur_entry_forms.py [--out PATH | --check
PATH | --self-test]
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import first_order_normal_cones as normal_cones  # noqa: E402
import holomorphic_gauss_fibers as gauss_fibers  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "gororoba.a5.schur-entry-forms/1"
PRODUCER = HERE / "schur_entry_forms.py"
FIRST_ORDER_RESULT = HERE / "first-order-normal-cones-result.json"
HOLOMORPHIC_RESULT = HERE / "holomorphic-gauss-fibers-result.json"
PRIME = 32009
SQRT_MINUS_ONE = 10754
HOLOMORPHIC_SIZE = 7
FIRST_ORDER_SIZE = 6
SOURCE_PATHS = tuple(
    dict.fromkeys(
        (
            PRODUCER,
            FIRST_ORDER_RESULT,
            HOLOMORPHIC_RESULT,
            *normal_cones.SOURCE_PATHS,
            *gauss_fibers.SOURCE_PATHS,
        )
    )
)

Row = list[Any]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path.name} does not hold a JSON object")
    return value


def _residue(value: Fraction) -> int:
    _require(value.denominator % PRIME != 0, "a coefficient denominator is divisible by the prime")
    return value.numerator * pow(value.denominator, -1, PRIME) % PRIME


def _modular(real: Fraction, imaginary: Fraction) -> int:
    return (_residue(real) + SQRT_MINUS_ONE * _residue(imaginary)) % PRIME


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _upper_pairs(size: int) -> list[list[int]]:
    return [[first, second] for first in range(size) for second in range(first + 1, size)]


def _family(size: int, rows: list[list[tuple[Fraction, Fraction]]], basis_indices: list[int]) -> dict[str, Any]:
    gaussian = [[[str(real), str(imaginary)] for real, imaginary in row] for row in rows]
    modular = [[_modular(real, imaginary) for real, imaginary in row] for row in rows]
    return {
        "matrix_size": size,
        "entry_count": len(rows),
        "entry_pairs_row_major_upper_triangle": _upper_pairs(size),
        "retained_basis_indices": basis_indices,
        "q_i_rows": gaussian,
        "f_32009_rows": modular,
        "q_i_rows_sha256": _digest(gaussian),
        "f_32009_rows_sha256": _digest(modular),
    }


def _holomorphic_rows(
    row: dict[str, Any], holomorphic_basis_indices: list[int]
) -> tuple[list[list[tuple[Fraction, Fraction]]], str]:
    data = gauss_fibers._schur_polynomials(gauss_fibers.IncidenceTask(row))
    width = len(data.slice_names)
    rows = [
        [
            gauss_fibers._gpoly_coefficient(coordinate, tuple(int(index == variable) for index in range(width)))
            for variable in range(width)
        ]
        for coordinate in data.leading_coordinates
    ]
    _require(len(rows) == HOLOMORPHIC_SIZE * (HOLOMORPHIC_SIZE - 1) // 2, f"{row['incidence']} 2i entry count changed")
    _require(
        list(data.selected_indices) == [int(index) for index in holomorphic_basis_indices],
        f"{row['incidence']} the rebuilt 2i basis indices differ from the record",
    )
    return [
        [(Fraction(real), Fraction(imaginary)) for real, imaginary in line] for line in rows
    ], data.coordinate_sha256


def _gaussian_fraction(value: sp.Expr) -> tuple[Fraction, Fraction]:
    real, imaginary = sp.expand(value).as_real_imag()
    _require(real.is_Rational and imaginary.is_Rational, "an effective-form coefficient is not in Q(i)")
    return (
        Fraction(int(real.p), int(real.q)),
        Fraction(int(imaginary.p), int(imaginary.q)),
    )


def _first_order_rows(row: dict[str, Any]) -> list[list[tuple[Fraction, Fraction]]]:
    point = tuple(Fraction(value) for value in row["boundary_point"])
    columns = tuple(int(value) for value in row["slice_columns_zero_based"])
    symbols = tuple(sp.symbols(f"t1:{len(columns) + 1}"))
    matrix = normal_cones.boundary._matrix_for_split(point)
    pivot = normal_cones.kernel_frames._find_principal_pivot(matrix, normal_cones.BOUNDARY_MATRIX_RANK)
    frame, _determinant, _pfaffian = normal_cones.kernel_frames._principal_frame(matrix, pivot)
    form = normal_cones._effective_form(frame, columns, symbols)
    _require(form.T == -form, f"{row['incidence']} the effective form is not skew")
    upper = normal_cones._upper_triangle(form)
    coefficients = upper.jacobian(symbols)
    for index in range(upper.rows):
        rebuilt = sum((coefficients[index, column] * symbols[column] for column in range(len(symbols))), sp.Integer(0))
        _require(sp.expand(upper[index] - rebuilt) == 0, f"{row['incidence']} an effective-form entry is not linear")
    _require(upper.rows == FIRST_ORDER_SIZE * (FIRST_ORDER_SIZE - 1) // 2, f"{row['incidence']} 2c entry count changed")
    return [
        [_gaussian_fraction(coefficients[index, column]) for column in range(len(symbols))]
        for index in range(upper.rows)
    ]


def _incidence_forms(task: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    first_order_row, holomorphic_row = task
    name = first_order_row["incidence"]
    _require(holomorphic_row["incidence"] == name, "the 2c and 2i rows are not paired by incidence")
    schur = holomorphic_row["c_schur_complement"]
    holomorphic_basis = [int(index) for index in schur["independent_leading_coordinate_indices"]]
    holomorphic_rows, coordinate_digest = _holomorphic_rows(first_order_row, holomorphic_basis)
    _require(
        coordinate_digest == schur["coordinate_sha256"],
        f"{name} the rebuilt 2i Schur coordinates differ from the record",
    )
    first_order_basis = [
        int(index) for index in first_order_row["effective_form"]["independent_upper_triangle_indices"]
    ]
    return {
        "incidence": name,
        "slice_dimension": len(first_order_row["slice_columns_zero_based"]),
        "slice_columns_zero_based": first_order_row["slice_columns_zero_based"],
        "holomorphic_schur_leading_form": _family(HOLOMORPHIC_SIZE, holomorphic_rows, holomorphic_basis),
        "first_order_effective_form": _family(FIRST_ORDER_SIZE, _first_order_rows(first_order_row), first_order_basis),
    }


def _hash_path(path: Path) -> tuple[str, str]:
    return str(path.relative_to(ROOT)), hashlib.sha256(path.read_bytes()).hexdigest()


def build_record() -> dict[str, Any]:
    first_order = _load_json(FIRST_ORDER_RESULT)
    holomorphic = _load_json(HOLOMORPHIC_RESULT)
    _require(first_order.get("pass") is True and holomorphic.get("pass") is True, "a retained input does not pass")
    pairs = []
    for name in gauss_fibers.RESOLVED_INCIDENCES:
        rows_2c = [row for row in first_order["incidences"] if row["incidence"] == name]
        rows_2i = [row for row in holomorphic["incidences"] if row["incidence"] == name]
        _require(len(rows_2c) == 1 and len(rows_2i) == 1, f"{name} is not a unique row of both records")
        pairs.append((rows_2c[0], rows_2i[0]))
    rows = parallel.ordered_map(_incidence_forms, tuple(pairs), min_items=1)
    inputs = dict(parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1))
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": inputs,
        "tools": {"python_flint": gauss_fibers.flint.__version__, "sympy": sp.__version__},
        "modulus": {"prime": PRIME, "square_root_of_minus_one": SQRT_MINUS_ONE},
        "layout": (
            "each family lists the upper-triangle entries a_(i,j), i < j, of a skew matrix in row-major order; a "
            "row holds the coefficients of t1, ..., tn of that entry form, as [real, imaginary] strings over Q(i) "
            "and as residues modulo 32009 (i = 10754); the matrix is the leading form of the Schur numerator of "
            "2i (7 x 7) and the effective form of 2c (6 x 6), each up to the nonzero scalar the record names"
        ),
        "incidences": rows,
        "summary": {
            "incidence_count": len(rows),
            "holomorphic_entry_forms": sum(row["holomorphic_schur_leading_form"]["entry_count"] for row in rows),
            "first_order_entry_forms": sum(row["first_order_effective_form"]["entry_count"] for row in rows),
        },
    }
    validate(record)
    record["pass"] = True
    return record


def _retained_rows() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    first_order = {row["incidence"]: row for row in _load_json(FIRST_ORDER_RESULT)["incidences"]}
    holomorphic = {row["incidence"]: row for row in _load_json(HOLOMORPHIC_RESULT)["incidences"]}
    return first_order, holomorphic


def _basis_text(row: list[list[str]], symbols: tuple[sp.Symbol, ...]) -> str:
    form = sp.Integer(0)
    for pair, symbol in zip(row, symbols, strict=True):
        coefficient = sp.Rational(Fraction(pair[0]).numerator, Fraction(pair[0]).denominator) + sp.I * sp.Rational(
            Fraction(pair[1]).numerator, Fraction(pair[1]).denominator
        )
        form += coefficient * symbol
    return str(sp.expand(form))


def validate(record: dict[str, Any]) -> None:
    """Counts, digests, the residue relation and the retained bases of a record; every failure raises."""
    _require(record["schema"] == SCHEMA, "the schema changed")
    retained_first_order, retained_holomorphic = _retained_rows()
    _require(len(record["incidences"]) == len(gauss_fibers.RESOLVED_INCIDENCES), "an incidence is missing")
    for row in record["incidences"]:
        for key, size in (
            ("holomorphic_schur_leading_form", HOLOMORPHIC_SIZE),
            ("first_order_effective_form", FIRST_ORDER_SIZE),
        ):
            family = row[key]
            count = size * (size - 1) // 2
            width = row["slice_dimension"]
            gaussian, modular = family["q_i_rows"], family["f_32009_rows"]
            _require(family["matrix_size"] == size and family["entry_count"] == count, f"{row['incidence']} {key} size")
            _require(len(gaussian) == count and len(modular) == count, f"{row['incidence']} {key} entry count")
            _require(all(len(line) == width for line in gaussian + modular), f"{row['incidence']} {key} row width")
            _require(family["q_i_rows_sha256"] == _digest(gaussian), f"{row['incidence']} {key} Q(i) digest")
            _require(family["f_32009_rows_sha256"] == _digest(modular), f"{row['incidence']} {key} residue digest")
            for gaussian_row, modular_row in zip(gaussian, modular, strict=True):
                for pair, residue in zip(gaussian_row, modular_row, strict=True):
                    _require(
                        _modular(Fraction(pair[0]), Fraction(pair[1])) == residue,
                        f"{row['incidence']} {key} a residue is not the image of its Q(i) coefficient",
                    )
            if key == "holomorphic_schur_leading_form":
                schur = retained_holomorphic[row["incidence"]]["c_schur_complement"]
                _require(
                    family["retained_basis_indices"] == schur["independent_leading_coordinate_indices"]
                    and [gaussian[index] for index in family["retained_basis_indices"]]
                    == schur["linear_coordinate_matrix"],
                    f"{row['incidence']} the 2i basis rows are not the entry forms at their retained indices",
                )
            else:
                form = retained_first_order[row["incidence"]]["effective_form"]
                symbols = tuple(sp.symbols(f"t1:{width + 1}"))
                _require(
                    family["retained_basis_indices"] == form["independent_upper_triangle_indices"]
                    and [_basis_text(gaussian[index], symbols) for index in family["retained_basis_indices"]]
                    == form["coordinate_forms"],
                    f"{row['incidence']} the 2c basis forms are not the entry forms at their retained indices",
                )
            for position, index in enumerate(family["retained_basis_indices"]):
                _require(
                    0 <= index < count and (position == 0 or index > family["retained_basis_indices"][position - 1]),
                    f"{row['incidence']} {key} basis index",
                )


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _mutations(record: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Records with one entry form dropped or altered, the digest left stale or refreshed."""
    found: list[tuple[str, dict[str, Any]]] = []
    for key in ("holomorphic_schur_leading_form", "first_order_effective_form"):
        basis = record["incidences"][0][key]["retained_basis_indices"]
        outside = next(index for index in range(record["incidences"][0][key]["entry_count"]) if index not in basis)
        dropped = copy.deepcopy(record)
        dropped["incidences"][0][key]["q_i_rows"].pop(outside)
        dropped["incidences"][0][key]["f_32009_rows"].pop(outside)
        found.append((f"{key}: a non-basis entry form dropped", dropped))
        for label, row_index in (
            ("a non-basis entry form altered", outside),
            ("a retained basis entry form altered", basis[0]),
        ):
            stale = copy.deepcopy(record)
            stale["incidences"][0][key]["q_i_rows"][row_index][0][0] = str(
                Fraction(stale["incidences"][0][key]["q_i_rows"][row_index][0][0]) + 1
            )
            found.append((f"{key}: {label}, digest stale", stale))
            refreshed = copy.deepcopy(record)
            family = refreshed["incidences"][0][key]
            family["q_i_rows"][row_index][0][0] = str(Fraction(family["q_i_rows"][row_index][0][0]) + 1)
            family["f_32009_rows"][row_index][0] = _modular(
                Fraction(family["q_i_rows"][row_index][0][0]), Fraction(family["q_i_rows"][row_index][0][1])
            )
            family["q_i_rows_sha256"] = _digest(family["q_i_rows"])
            family["f_32009_rows_sha256"] = _digest(family["f_32009_rows"])
            found.append((f"{key}: {label}, digests refreshed", refreshed))
    return found


def _self_test(record: dict[str, Any]) -> None:
    validate(record)
    fresh = _record_bytes(record)
    _require(
        sum(len(row["holomorphic_schur_leading_form"]["q_i_rows"]) for row in record["incidences"]) == 8 * 21,
        "2i count",
    )
    _require(
        sum(len(row["first_order_effective_form"]["q_i_rows"]) for row in record["incidences"]) == 8 * 15, "2c count"
    )
    for label, mutated in _mutations(record):
        try:
            validate(mutated)
            caught = False
        except RuntimeError:
            caught = True
        replay_differs = _record_bytes(mutated) != fresh
        _require(replay_differs, f"{label}: the replay comparison cannot see the change")
        refreshed_outside_basis = "digests refreshed" in label and "non-basis entry form altered" in label
        _require(caught or refreshed_outside_basis, f"{label}: validation missed the change")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument(
        "--self-test", action="store_true", help="run the baseline and the dropped and altered entry forms"
    )
    arguments = parser.parse_args()
    _require(
        sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) == 1,
        "select exactly one of --out, --check, or --self-test",
    )
    record = build_record()
    if arguments.self_test:
        _self_test(record)
        return
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    else:
        retained = arguments.check.read_bytes()
        _require(
            retained == rendered,
            "record mismatch: "
            f"retained={hashlib.sha256(retained).hexdigest()} fresh={hashlib.sha256(rendered).hexdigest()}",
        )


if __name__ == "__main__":
    main()
