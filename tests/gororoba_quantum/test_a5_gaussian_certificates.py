"""The Gaussian-integer certificates kept in docs/evidence/a5-gaussian-certificates/ against their records.

gaussian_certificates.py, span_certificate.py and render_span.py stay here as the files that ledger row A5-500
cites (gaussian_certificates.py because render_span.py imports it); the live generators that render the Rocq sources
of gororoba-math are in its ci/quantum-sources/. These tests need neither Rocq nor a gororoba-math checkout. They
check, in Python integers with a Gaussian integer as a pair (real part, imaginary part):

- the exact left inverses L M = d I of the derivation certificate and of the eight arc matrices, and the splitting
  identity P M + d V C = d I of the span record, each against a known-bad perturbation;
- that the readers reject malformed records (floats, booleans, fractions, wrong counts, extra or missing keys,
  swapped cases, repeated or out-of-range indices).

The cases that render or mutate a Rocq source (the rendered tables read back against the records, the six plus six
mutants and their anchors, the runner over a gororoba-math checkout) belong to gororoba-math, where
ci/check_quantum_sources.sh renders the three sources again and calibrates the comparison on a changed digit.
python-flint (the pin of requirements.txt) recomputes the span record once.
"""

from __future__ import annotations

import copy
import json
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "docs/evidence/a5-gaussian-certificates"
sys.path.insert(0, str(BUNDLE))

import gaussian_certificates as gc  # noqa: E402
import render_span  # noqa: E402
import span_certificate as sc  # noqa: E402

Entry = tuple[int, int]
Mutation = Callable[[Any], None]

G2_JSON = json.loads(gc.G2_RECORD.read_text(encoding="utf-8"))
ARC_JSON = json.loads(gc.ARC_RECORD.read_text(encoding="utf-8"))
LEFT_JSON = json.loads(gc.LEFT_INVERSES.read_text(encoding="utf-8"))
SPAN_JSON = json.loads(render_span.SPAN_RECORD.read_text(encoding="utf-8"))


def fresh(record: Any) -> Any:
    return copy.deepcopy(record)


def times(left: Entry, right: Entry) -> Entry:
    return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])


def product_defects(left_sparse: list[list[Any]], matrix: list[list[Entry]], scalar: Entry) -> list[tuple[int, int]]:
    """Positions where (L M)[l][j] differs from d (l = j) or 0, with L given by (column, entry) lines."""
    found = []
    for line, items in enumerate(left_sparse):
        for column in range(len(matrix[0])):
            total = (0, 0)
            for row, entry in items:
                value = times((entry[0], entry[1]), matrix[row][column])
                total = (total[0] + value[0], total[1] + value[1])
            if total != (scalar if line == column else (0, 0)):
                found.append((line, column))
    return found


def derivation_matrix() -> list[list[Entry]]:
    """Row 16 m + c holds coordinate c of D_n(e_m) for n = 1 to 14."""
    tables = [d["images"] for d in G2_JSON["derivations"]]
    return [[(table[m][c][0], table[m][c][1]) for table in tables] for m in range(16) for c in range(16)]


def arc_matrix(matrix: dict[str, Any]) -> list[list[Entry]]:
    return [[(int(entry["re"]), int(entry["im"])) for entry in row] for row in matrix["entries"]]


# ---------------------------------------------------------------- exact left inverses


def test_the_derivation_left_inverse_is_exact_with_scalar_one() -> None:
    section = LEFT_JSON["g2_derivations"]
    if section["d"] != [1, 0]:
        raise AssertionError(f"the scalar is {section['d']}")
    found = product_defects(section["left_sparse"], derivation_matrix(), (1, 0))
    if found:
        raise AssertionError(f"L M differs from I at {found[:3]}")


def test_the_eight_arc_left_inverses_are_exact() -> None:
    certificates = LEFT_JSON["arc_matrices"]
    if [c["id"] for c in certificates] != list(gc.ARC_IDS) or [m["id"] for m in ARC_JSON["matrices"]] != list(
        gc.ARC_IDS
    ):
        raise AssertionError("the eight matrices are not those of ARC_IDS in order")
    for certificate, matrix in zip(certificates, ARC_JSON["matrices"], strict=True):
        scalar = (certificate["d"][0], certificate["d"][1])
        found = product_defects(certificate["left_sparse"], arc_matrix(matrix), scalar)
        if found:
            raise AssertionError(f"{certificate['id']}: L M differs from d I at {found[:3]}")
        if certificate["norm_of_d"] != scalar[0] ** 2 + scalar[1] ** 2 or scalar == (0, 0):
            raise AssertionError(f"{certificate['id']}: norm_of_d is not the norm of d = {scalar}")
        if scalar[0] ** 2 + scalar[1] ** 2 == 1:
            raise AssertionError(f"{certificate['id']}: a unit scalar must be normalized to 1")


def test_a_perturbed_left_inverse_or_matrix_or_scalar_is_detected() -> None:
    section = fresh(LEFT_JSON["g2_derivations"])
    section["left_sparse"][0][0][1][0] += 1
    if not product_defects(section["left_sparse"], derivation_matrix(), (1, 0)):
        raise AssertionError("a changed left-inverse entry passed")
    certificate = LEFT_JSON["arc_matrices"][4]
    matrix = arc_matrix(ARC_JSON["matrices"][4])
    scalar = (certificate["d"][0], certificate["d"][1])
    matrix[3][2] = (matrix[3][2][0] + 1, matrix[3][2][1])
    if not product_defects(certificate["left_sparse"], matrix, scalar):
        raise AssertionError("a changed matrix entry passed")
    if not product_defects(certificate["left_sparse"], arc_matrix(ARC_JSON["matrices"][4]), (-scalar[0], scalar[1])):
        raise AssertionError("a changed scalar passed")


@pytest.mark.audit
def test_the_generator_rebuilds_the_tracked_left_inverse_record() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    certificates = gc.arc_matrices(fresh(ARC_JSON))
    record = gc.left_inverse_record(gc.derivation_certificate(tables), certificates)
    if json.dumps(record, indent=1) + "\n" != gc.LEFT_INVERSES.read_text(encoding="utf-8"):
        raise AssertionError("left-inverses.json is not what gaussian_certificates.py writes")
    if gc.derivation_left_inverse(fresh(LEFT_JSON)) != [
        [(column, (entry[0], entry[1])) for column, entry in line]
        for line in LEFT_JSON["g2_derivations"]["left_sparse"]
    ]:
        raise AssertionError("the strict reader changed the left inverse")


# ---------------------------------------------------------------- the span record


def test_the_span_record_satisfies_the_splitting_identity() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    left = gc.derivation_left_inverse(fresh(LEFT_JSON))
    record = render_span.read_span(fresh(SPAN_JSON))
    if record["d"] != 6 or len(record["equations"]) != 242:
        raise AssertionError(f"d = {record['d']} with {len(record['equations'])} equations")
    rows = sc.equations(sc.sign_table())
    if sc.left_inverse_defects(tables, left):
        raise AssertionError("C V differs from I")
    found = sc.splitting_defects(record, tables, left, rows)
    if found:
        raise AssertionError(f"P M + d V C differs from d I at {found[:3]}")


def test_the_splitting_identity_rejects_a_changed_entry_scalar_or_equation() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    left = gc.derivation_left_inverse(fresh(LEFT_JSON))
    rows = sc.equations(sc.sign_table())
    entry = fresh(SPAN_JSON)
    entry["p_sparse"][0][0][1][0] += 1
    scalar = fresh(SPAN_JSON)
    scalar["d"] = 3
    equation = fresh(SPAN_JSON)
    equation["equations"][0] = [0, 0, 1]
    for name, record in (("entry", entry), ("scalar", scalar), ("equation", equation)):
        if not sc.splitting_defects(record, tables, left, rows):
            raise AssertionError(f"a changed {name} passed the splitting identity")


def test_the_leibniz_equations_vanish_on_the_tables_and_not_on_a_perturbed_one() -> None:
    """The equations of cd_core.cd_sign annihilate the flattened table of each derivation (unknown 16 m + c)."""
    rows = sc.equations(sc.sign_table())
    for derivation in G2_JSON["derivations"]:
        flat = [tuple(derivation["images"][m][c]) for m in range(16) for c in range(16)]
        for key, row in rows.items():
            for part in (0, 1):
                if sum(coefficient * flat[index][part] for index, coefficient in row.items()):
                    raise AssertionError(f"{derivation['id']}: the equation {key} fails on part {part}")
    flat = [tuple(G2_JSON["derivations"][0]["images"][m][c]) for m in range(16) for c in range(16)]
    flat[17] = (flat[17][0] + 1, flat[17][1])
    if not any(sum(coefficient * flat[index][0] for index, coefficient in row.items()) for row in rows.values()):
        raise AssertionError("a perturbed table satisfied every equation")


@pytest.mark.audit
def test_flint_recomputes_the_smith_invariants() -> None:
    found = sc.smith_invariants(sc.equations(sc.sign_table()))
    if found != sc.SMITH_INVARIANTS:
        raise AssertionError(found)


def test_the_recorded_smith_invariants_give_the_finite_field_nullities() -> None:
    recorded = sc.SMITH_INVARIANTS
    if recorded != {1: 192, 2: 49, 6: 1} or sum(recorded.values()) != 242:
        raise AssertionError(recorded)
    if [sc.nullity_modulo(recorded, prime) for prime in (2, 3, 5)] != [64, 15, 14]:
        raise AssertionError("the invariants do not give nullities 64, 15 and 14 modulo 2, 3 and 5")
    if sc.nullity_modulo({1: 193, 2: 48, 6: 1}, 2) == 64:
        raise AssertionError("a changed multiplicity leaves the nullity modulo 2")


def test_the_row_basis_and_the_exact_solve_recover_known_rational_coefficients() -> None:
    rows: sc.Rows = {(0, 0, 0): {0: 2}, (0, 0, 1): {1: 3, 2: 1}, (0, 0, 2): {0: 2, 1: 3, 2: 1}, (0, 0, 3): {5: 4}}
    chosen = sc.independent(rows, sorted(rows))
    if chosen != [(0, 0, 0), (0, 0, 1), (0, 0, 3)]:
        raise AssertionError(f"the dependent third row was not skipped: {chosen}")

    def target(entries: dict[int, int]) -> list[int]:
        return [entries.get(index, 0) for index in range(sc.UNKNOWNS)]

    solution = sc.solve(rows, chosen, [target({0: 1}), target({0: 2, 1: 3, 2: 1, 5: 1}), target({})])
    found = [[Fraction(int(solution[i, j].p), int(solution[i, j].q)) for j in range(3)] for i in range(3)]
    expected = [[Fraction(1, 2), 0, 0], [1, 1, Fraction(1, 4)], [0, 0, 0]]
    if found != expected:
        raise AssertionError(found)
    with pytest.raises(RuntimeError, match="row space"):
        sc.solve(rows, chosen, [target({1: 1})])
    with pytest.raises(RuntimeError, match="dependent"):
        sc.solve(rows, sorted(rows), [target({0: 1})])


@pytest.mark.audit
def test_flint_recomputes_the_tracked_span_record() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    left = gc.derivation_left_inverse(fresh(LEFT_JSON))
    record = sc.span_record(tables, left, [0])
    if sc.record_text(record) != render_span.SPAN_RECORD.read_text(encoding="utf-8"):
        raise AssertionError("span.json is not what span_certificate.py computes at seed 0")


def test_the_span_computation_refuses_a_left_inverse_that_is_not_one() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    left = gc.derivation_left_inverse(fresh(LEFT_JSON))
    left[0][0] = (left[0][0][0], (left[0][0][1][0] + 1, left[0][0][1][1]))
    with pytest.raises(RuntimeError, match="C V = I"):
        sc.span_record(tables, left, [0])


# ---------------------------------------------------------------- malformed records


def mutate(record: Any, change: Mutation) -> Any:
    candidate = fresh(record)
    change(candidate)
    return candidate


def set_at(path: list[Any], value: Any) -> Mutation:
    def change(record: Any) -> None:
        for step in path[:-1]:
            record = record[step]
        record[path[-1]] = value

    return change


def delete_at(path: list[Any]) -> Mutation:
    def change(record: Any) -> None:
        for step in path[:-1]:
            record = record[step]
        del record[path[-1]]

    return change


def swap_first_two(path: list[Any]) -> Mutation:
    def change(record: Any) -> None:
        for step in path:
            record = record[step]
        record[0], record[1] = record[1], record[0]

    return change


def reverse_a_long_line(lines: list[list[Any]]) -> None:
    """Reverse the first line that holds at least two items, so that its columns decrease."""
    next(line for line in lines if len(line) >= 2).reverse()


G2_CASES: dict[str, Mutation] = {
    "float coordinate": set_at(["derivations", 0, "images", 2, 5, 0], 1.9),
    "boolean coordinate": set_at(["derivations", 0, "images", 2, 5, 0], True),
    "string coordinate": set_at(["derivations", 0, "images", 2, 5, 1], "1"),
    "coordinate that is no pair": set_at(["derivations", 0, "images", 2, 5], [1, 2, 3]),
    "13 tables": delete_at(["derivations", 13]),
    "15 tables": lambda record: record["derivations"].append(fresh(record["derivations"][0])),
    "swapped tables": swap_first_two(["derivations"]),
    "extra record key": set_at(["note"], "x"),
    "missing record key": delete_at(["convention"]),
    "extra derivation key": set_at(["derivations", 3, "note"], "x"),
    "missing derivation key": delete_at(["derivations", 3, "real"]),
    "float dimension": set_at(["dimension"], 16.0),
    "other dimension": set_at(["dimension"], 8),
    "record that does not pass": set_at(["pass"], False),
    "other schema": set_at(["schema"], "gororoba.a5.g2-derivation-tables/2"),
    "other ring": set_at(["ring"], "Z"),
    "short image table": delete_at(["derivations", 0, "images", 15]),
    "short image": delete_at(["derivations", 0, "images", 0, 15]),
    "images that are no list": set_at(["derivations", 0, "images"], None),
    "derivations that are no list": set_at(["derivations"], None),
}

ARC_CASES: dict[str, Mutation] = {
    "fraction": set_at(["matrices", 0, "entries", 0, 0, "re"], "3/2"),
    "decimal point": set_at(["matrices", 0, "entries", 0, 0, "re"], "1.0"),
    "plus sign": set_at(["matrices", 0, "entries", 0, 0, "re"], "+1"),
    "leading zero": set_at(["matrices", 0, "entries", 0, 0, "im"], "01"),
    "padded entry": set_at(["matrices", 0, "entries", 0, 0, "im"], " 1"),
    "integer entry": set_at(["matrices", 0, "entries", 0, 0, "re"], 5),
    "float entry": set_at(["matrices", 0, "entries", 0, 0, "re"], 1.5),
    "seven matrices": delete_at(["matrices", 7]),
    "nine matrices": lambda record: record["matrices"].append(fresh(record["matrices"][0])),
    "swapped matrices": swap_first_two(["matrices"]),
    "matrices that are no list": set_at(["matrices"], None),
    "extra entry key": set_at(["matrices", 0, "entries", 0, 0, "note"], "1"),
    "missing entry key": delete_at(["matrices", 0, "entries", 0, 0, "im"]),
    "extra matrix key": set_at(["matrices", 2, "note"], "x"),
    "missing matrix key": delete_at(["matrices", 2, "slug"]),
    "float rows": set_at(["matrices", 0, "rows"], 24.0),
    "float columns": set_at(["matrices", 0, "columns"], 6.0),
    "claimed rank 5": set_at(["matrices", 0, "claimed_rank"], 5),
    "float claimed rank": set_at(["matrices", 0, "claimed_rank"], 6.0),
    "boolean rows": set_at(["matrices", 0, "rows"], True),
    "short row": delete_at(["matrices", 0, "entries", 0, 5]),
    "23 rows": delete_at(["matrices", 0, "entries", 23]),
    "entries that are no list": set_at(["matrices", 0, "entries"], None),
    "extra record key": set_at(["note"], "x"),
    "record that does not pass": set_at(["pass"], False),
    "other schema": set_at(["schema"], "gororoba.a5.w8-component-arc-matrices-qi/2"),
    "other field": set_at(["field"], "Q"),
}

LEFT_CASES: dict[str, Mutation] = {
    "extra record key": set_at(["note"], "x"),
    "missing record key": delete_at(["arc_matrices"]),
    "other schema": set_at(["schema"], "gororoba.a5.gaussian-left-inverses/2"),
    "extra section key": set_at(["g2_derivations", "note"], "x"),
    "scalar 2": set_at(["g2_derivations", "d"], [2, 0]),
    "float scalar": set_at(["g2_derivations", "d"], [1.0, 0]),
    "float columns": set_at(["g2_derivations", "columns"], 14.0),
    "13 lines": delete_at(["g2_derivations", "left_sparse", 13]),
    "repeated column": lambda record: record["g2_derivations"]["left_sparse"][0].insert(
        1, fresh(record["g2_derivations"]["left_sparse"][0][0])
    ),
    "column 256": set_at(["g2_derivations", "left_sparse", 0, 0, 0], 256),
    "negative column": set_at(["g2_derivations", "left_sparse", 0, 0, 0], -1),
    "boolean column": set_at(["g2_derivations", "left_sparse", 0, 0, 0], True),
    "float entry": set_at(["g2_derivations", "left_sparse", 0, 0, 1, 0], 1.0),
    "item that is no pair": set_at(["g2_derivations", "left_sparse", 0, 0], [18]),
    "line that is no list": set_at(["g2_derivations", "left_sparse", 0], None),
    "out of order": lambda record: reverse_a_long_line(record["g2_derivations"]["left_sparse"]),
    "convention that is no string": set_at(["convention"], 7),
    "arc matrices that are no list": set_at(["arc_matrices"], "x"),
    "repeated selected row": lambda record: record["g2_derivations"]["selected_rows"].__setitem__(
        1, record["g2_derivations"]["selected_rows"][0]
    ),
    "13 selected rows": delete_at(["g2_derivations", "selected_rows", 13]),
    "selected row 256": set_at(["g2_derivations", "selected_rows", 13], 256),
    "float norm": set_at(["g2_derivations", "norm_of_d"], 1.0),
    "norm 2": set_at(["g2_derivations", "norm_of_d"], 2),
    "row meaning that is no string": set_at(["g2_derivations", "row_meaning"], None),
    "column outside the selected rows": set_at(["g2_derivations", "selected_rows", 0], 0),
}

SPAN_CASES: dict[str, Mutation] = {
    "other schema": set_at(["schema"], "gororoba.a5.g2-derivation-span/2"),
    "extra key": set_at(["note"], "x"),
    "missing key": delete_at(["seed"]),
    "scalar 0": set_at(["d"], 0),
    "float scalar": set_at(["d"], 6.0),
    "boolean scalar": set_at(["d"], True),
    "negative seed": set_at(["seed"], -1),
    "string seed": set_at(["seed"], "0"),
    "241 equations": delete_at(["equations", 241]),
    "243 equations": lambda record: record["equations"].append([15, 15, 15]),
    "pair as equation": set_at(["equations", 0], [0, 0]),
    "equation entry 16": set_at(["equations", 0, 2], 16),
    "negative equation entry": set_at(["equations", 0, 0], -1),
    "float equation entry": set_at(["equations", 0, 1], 1.0),
    "repeated equation": set_at(["equations", 1], [0, 0, 0]),
    "255 lines": delete_at(["p_sparse", 255]),
    "257 lines": lambda record: record["p_sparse"].append([]),
    "line that is no list": set_at(["p_sparse", 0], None),
    "column 242": set_at(["p_sparse", 0, 0, 0], 242),
    "negative column": set_at(["p_sparse", 0, 0, 0], -1),
    "repeated column": lambda record: record["p_sparse"][0].insert(1, fresh(record["p_sparse"][0][0])),
    "out of order": lambda record: reverse_a_long_line(record["p_sparse"]),
    "float entry": set_at(["p_sparse", 0, 0, 1, 0], 1.0),
    "short entry": set_at(["p_sparse", 0, 0, 1], [1]),
    "item that is no pair": set_at(["p_sparse", 0, 0], [0]),
}


@pytest.mark.parametrize("case", sorted(G2_CASES))
def test_the_derivation_reader_rejects_a_malformed_record(case: str) -> None:
    with pytest.raises(RuntimeError):
        gc.derivation_tables(mutate(G2_JSON, G2_CASES[case]))


@pytest.mark.parametrize("case", sorted(ARC_CASES))
def test_the_arc_reader_rejects_a_malformed_record(case: str) -> None:
    with pytest.raises(RuntimeError):
        gc.arc_matrices(mutate(ARC_JSON, ARC_CASES[case]))


@pytest.mark.parametrize("case", sorted(LEFT_CASES))
def test_the_left_inverse_reader_rejects_a_malformed_record(case: str) -> None:
    with pytest.raises(RuntimeError):
        gc.derivation_left_inverse(mutate(LEFT_JSON, LEFT_CASES[case]))


@pytest.mark.parametrize("case", sorted(SPAN_CASES))
def test_the_span_reader_rejects_a_malformed_record(case: str) -> None:
    with pytest.raises(RuntimeError):
        render_span.read_span(mutate(SPAN_JSON, SPAN_CASES[case]))


def test_the_readers_accept_the_tracked_records() -> None:
    if len(gc.derivation_tables(fresh(G2_JSON))) != 14 or len(gc.arc_matrices(fresh(ARC_JSON))) != 8:
        raise AssertionError("a tracked record changed its case count")
    gc.derivation_left_inverse(fresh(LEFT_JSON))
    render_span.read_span(fresh(SPAN_JSON))


def test_a_certificate_needs_a_matrix_of_full_column_rank() -> None:
    with pytest.raises(RuntimeError, match="rank"):
        gc.left_inverse([[(1, 0), (2, 0)], [(2, 0), (4, 0)], [(3, 0), (6, 0)]])
