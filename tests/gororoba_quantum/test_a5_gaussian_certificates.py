"""The Gaussian-integer certificates of docs/evidence/a5-gaussian-certificates/ against their records.

The generators render three Rocq sources of gororoba-math (CdTowerG2Derivations.v, A5W8ArcMatrixRanks.v and
CdTowerG2DerivationSpan.v) from tracked records. These tests need neither Rocq nor a gororoba-math checkout. They
check, in Python integers with a Gaussian integer as a pair (real part, imaginary part):

- the exact left inverses L M = d I of the derivation certificate and of the eight arc matrices, and the splitting
  identity P M + d V C = d I of the span record, each against a known-bad perturbation;
- that every rendered table equals the record it came from, read back from the rendered text;
- that the readers reject malformed records (floats, booleans, fractions, wrong counts, extra or missing keys,
  swapped cases, repeated or out-of-range indices);
- that each mutant script changes the one intended line, ahead of the lemma that must reject it;
- that scripts/math_source_generators.py reads and writes the two producers through the digest-checked sources of a
  gororoba-math checkout built in tmp_path.

python-flint (the pin of requirements.txt) recomputes the span record once.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "docs/evidence/a5-gaussian-certificates"
sys.path.insert(0, str(BUNDLE))

import gaussian_certificates as gc  # noqa: E402
import make_mutants  # noqa: E402
import make_span_mutants  # noqa: E402
import math_source_generators as runner  # noqa: E402
import render_span  # noqa: E402
import span_certificate as sc  # noqa: E402

Entry = tuple[int, int]
Mutation = Callable[[Any], None]

G2_JSON = json.loads(gc.G2_RECORD.read_text(encoding="utf-8"))
ARC_JSON = json.loads(gc.ARC_RECORD.read_text(encoding="utf-8"))
LEFT_JSON = json.loads(gc.LEFT_INVERSES.read_text(encoding="utf-8"))
SPAN_JSON = json.loads(render_span.SPAN_RECORD.read_text(encoding="utf-8"))
SOURCES = {
    "CdTowerG2Derivations.v": gc.G2_FILE,
    "A5W8ArcMatrixRanks.v": gc.ARC_FILE,
    "CdTowerG2DerivationSpan.v": render_span.ROCQ_NAME,
}


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


# ---------------------------------------------------------------- rendered tables equal the records


def block(text: str, name: str) -> str:
    """The text of `Definition name` up to the closing of its list."""
    start = text.index(f"Definition {name} ")
    return text[start : text.index("\n  ].\n", start)]


def pairs(row: str) -> list[Entry]:
    return [(int(a), int(b)) for a, b in re.findall(r"\((-?\d+), (-?\d+)\)", row)]


def sparse_lines(body: str) -> list[list[tuple[int, Entry]]]:
    lines = []
    for row in re.findall(r"\[([^\[\]]*)\]", body[body.index("[\n") + 2 :]):
        lines.append(
            [(int(c), (int(a), int(b))) for c, a, b in re.findall(r"\((\d+)%nat, \((-?\d+), (-?\d+)\)\)", row)]
        )
    return lines


def dense_rows(body: str) -> list[list[Entry]]:
    return [pairs(row) for row in re.findall(r"\[([^\[\]]*)\]", body[body.index("[\n") + 2 :])]


def scalar_of(text: str, name: str) -> Entry:
    found = re.search(rf"Definition {name} : Z \* Z := \((-?\d+), (-?\d+)\)\.", text)
    if found is None:
        raise AssertionError(f"no scalar {name}")
    return (int(found.group(1)), int(found.group(2)))


def test_the_rendered_derivation_tables_equal_the_record() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    certificate = gc.derivation_certificate(tables)
    text = gc.render_g2(tables, certificate)
    for number, derivation in enumerate(G2_JSON["derivations"], start=1):
        start = text.index(f"Definition images_{number} (m : nat)")
        body = text[start : text.index("  | _ => TA.zero 4", start)]
        found: dict[int, dict[int, Entry]] = {}
        for match in re.finditer(r"  \| (\d+) => vec \[([^\]]*)\]", body):
            found[int(match.group(1))] = {
                int(c): (int(a), int(b))
                for c, a, b in re.findall(r"\((\d+)%nat, \((-?\d+), (-?\d+)\)%Z\)", match.group(2))
            }
        expected = {
            m: {c: (v[0], v[1]) for c, v in enumerate(image) if tuple(v) != (0, 0)}
            for m, image in enumerate(derivation["images"])
            if any(tuple(v) != (0, 0) for v in image)
        }
        if found != expected:
            raise AssertionError(f"images_{number} differs from the record")
    left = sparse_lines(block(text, "independence_left"))
    if left != gc.derivation_left_inverse(fresh(LEFT_JSON)) or scalar_of(text, "independence_d") != (1, 0):
        raise AssertionError("independence_left or independence_d differs from left-inverses.json")


def test_the_rendered_arc_tables_equal_the_records() -> None:
    certificates = gc.arc_matrices(fresh(ARC_JSON))
    text = gc.render_arcs(certificates)
    for certificate, matrix, recorded in zip(
        certificates, ARC_JSON["matrices"], LEFT_JSON["arc_matrices"], strict=True
    ):
        name = certificate["id"].replace("-", "_")
        if dense_rows(block(text, f"{name}_matrix")) != arc_matrix(matrix):
            raise AssertionError(f"{name}_matrix differs from the arc record")
        left = [[(column, (entry[0], entry[1])) for column, entry in line] for line in recorded["left_sparse"]]
        if sparse_lines(block(text, f"{name}_left")) != left:
            raise AssertionError(f"{name}_left differs from left-inverses.json")
        if scalar_of(text, f"{name}_d") != (recorded["d"][0], recorded["d"][1]):
            raise AssertionError(f"{name}_d differs from left-inverses.json")


def test_the_rendered_span_tables_equal_the_record() -> None:
    record = render_span.read_span(fresh(SPAN_JSON))
    text = render_span.render(record)
    found = [
        tuple(int(v) for v in item) for item in re.findall(r"\((\d+), (\d+), (\d+)\)%nat", block(text, "equations"))
    ]
    if found != [tuple(triple) for triple in record["equations"]]:
        raise AssertionError("equations differs from span.json")
    expected = [[(column, (v[0], v[1])) for column, v in line] for line in record["p_sparse"]]
    if sparse_lines(block(text, "back")) != expected or scalar_of(text, "scalar") != (record["d"], 0):
        raise AssertionError("back or scalar differs from span.json")
    if not text.isascii():
        raise AssertionError("the rendered Rocq text holds a non-ASCII character")


def test_every_rendering_is_ascii_and_names_its_generator() -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    texts = {
        gc.G2_FILE: gc.render_g2(tables, gc.derivation_certificate(tables)),
        gc.ARC_FILE: gc.render_arcs(gc.arc_matrices(fresh(ARC_JSON))),
        render_span.ROCQ_NAME: render_span.render(render_span.read_span(fresh(SPAN_JSON))),
    }
    for name, text in texts.items():
        if not text.isascii() or "docs/evidence/a5-gaussian-certificates/" not in text:
            raise AssertionError(f"{name}: non-ASCII text or no generator path")


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


# ---------------------------------------------------------------- mutants


def changed_lines(original: str, mutant: str) -> list[int]:
    """The 1-based numbers of the lines of `original` that differ in `mutant` (same line count required)."""
    before, after = original.splitlines(), mutant.splitlines()
    if len(before) != len(after):
        raise AssertionError("a mutant changed the number of lines")
    return [number for number, (a, b) in enumerate(zip(before, after, strict=True), start=1) if a != b]


def line_of(text: str, start: str) -> int:
    return next(number for number, line in enumerate(text.splitlines(), start=1) if line.startswith(start))


def definition_lines(text: str, name: str) -> range:
    """The line numbers of `Definition name` up to the line before the next `Definition`."""
    first = line_of(text, f"Definition {name} ")
    lines = text.splitlines()
    last = next((n for n in range(first + 1, len(lines) + 1) if lines[n - 1].startswith("Definition ")), len(lines))
    return range(first, last)


def test_the_derivation_and_arc_mutants_change_one_line_ahead_of_the_rejecting_lemma(tmp_path: Path) -> None:
    tables = gc.derivation_tables(fresh(G2_JSON))
    g2 = gc.render_g2(tables, gc.derivation_certificate(tables))
    arcs = gc.render_arcs(gc.arc_matrices(fresh(ARC_JSON)))
    source = tmp_path / "rocq"
    source.mkdir()
    (source / gc.G2_FILE).write_text(g2, encoding="utf-8")
    (source / gc.ARC_FILE).write_text(arcs, encoding="utf-8")
    if make_mutants.main([str(source), str(tmp_path / "out")]) != 0:
        raise AssertionError("make_mutants.py failed")
    region = {
        "ArcEntry": (arcs, "w8_nm_linear_point1_matrix", "(-44, -2290)"),
        "ArcScalar": (arcs, "w8_nm_series_point1_d", "(3600, 0)"),
        "ArcShortRow": (arcs, "w8_nm_series_point1_matrix", None),
        "ArcDuplicateKey": (arcs, "w8_nm_series_point1_left", None),
        "G2Sign": (g2, "images_1", "(5%nat, (0, -1)%Z)"),
        "G2Left": (g2, "independence_left", None),
    }
    if set(region) != set(make_mutants.EXPECTED):
        raise AssertionError("the mutants and the expectations of the test differ")
    for name, (original, definition, token) in region.items():
        mutant = (tmp_path / "out" / f"{name}.v").read_text(encoding="utf-8")
        changed = changed_lines(original, mutant)
        if len(changed) != 1 or changed[0] not in definition_lines(original, definition):
            raise AssertionError(f"{name}: changed lines {changed}, expected one inside {definition}")
        if token is not None and token not in mutant.splitlines()[changed[0] - 1]:
            raise AssertionError(f"{name}: the changed line lacks {token}")
        lemma = make_mutants.EXPECTED[name]
        if changed[0] >= line_of(original, f"Lemma {lemma} "):
            raise AssertionError(f"{name}: the change does not precede Lemma {lemma}")


def test_the_span_mutants_change_one_line_ahead_of_the_rejecting_lemma(tmp_path: Path) -> None:
    text = render_span.render(render_span.read_span(fresh(SPAN_JSON)))
    source = tmp_path / render_span.ROCQ_NAME
    source.write_text(text, encoding="ascii")
    if make_span_mutants.main([str(source), str(tmp_path / "out")]) != 0:
        raise AssertionError("make_span_mutants.py failed")
    if sorted(make_span_mutants.MUTANTS) != sorted(entry.name for entry in (tmp_path / "out").iterdir()):
        raise AssertionError("a mutant directory is missing")
    for name, (_old, _new, lemma) in make_span_mutants.MUTANTS.items():
        directory = tmp_path / "out" / name
        mutant = (directory / render_span.ROCQ_NAME).read_text(encoding="ascii")
        changed = changed_lines(text, mutant)
        if len(changed) != 1:
            raise AssertionError(f"{name}: changed lines {changed}")
        if (directory / "expected-lemma.txt").read_text(encoding="ascii") != lemma + "\n":
            raise AssertionError(f"{name}: the expected lemma differs from the table")
        if changed[0] >= line_of(text, f"Lemma {lemma} "):
            raise AssertionError(f"{name}: the change does not precede Lemma {lemma}")


def test_a_span_mutant_anchor_must_occur_exactly_once() -> None:
    with pytest.raises(RuntimeError, match="anchor occurs 0 times"):
        make_span_mutants.mutate("Definition scalar : Z * Z := (6, 0).\n")


# ---------------------------------------------------------------- the runner reaches both producers


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(
        [
            "git",
            "-C",
            str(directory),
            "-c",
            "core.fsmonitor=false",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@e.invalid",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def renderings() -> dict[str, str]:
    tables = gc.derivation_tables(fresh(G2_JSON))
    return {
        gc.G2_FILE: gc.render_g2(tables, gc.derivation_certificate(tables)),
        gc.ARC_FILE: gc.render_arcs(gc.arc_matrices(fresh(ARC_JSON))),
        render_span.ROCQ_NAME: render_span.render(render_span.read_span(fresh(SPAN_JSON))),
    }


def build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, texts: dict[str, str], bound: set[str]) -> tuple[Path, Path]:
    """A gororoba-math checkout holding `texts`, a root whose ledger binds the digests of `bound`, and the pin."""
    math = tmp_path / "math"
    (math / "rocq/quantum").mkdir(parents=True)
    (math / "rocq/quantum/_RocqProject").write_text(
        '-Q . ""\n' + "".join(f"{name}\n" for name in texts), encoding="utf-8"
    )
    for name, text in texts.items():
        (math / "rocq/quantum" / name).write_text(text, encoding="utf-8")
    git(math, "init", "-q")
    git(math, "add", ".")
    git(math, "commit", "-q", "-m", "sources")
    root = tmp_path / "root"
    (root / "docs/state").mkdir(parents=True)
    (root / "docs/state/research_state.json").write_text(json.dumps({"claims": []}), encoding="utf-8")
    (root / "docs/evidence/bundle").mkdir(parents=True)
    (root / "ci").mkdir()
    (root / "ci/gororoba_math.pin").write_text(git(math, "rev-parse", "HEAD") + "\n", encoding="utf-8")
    rows = "".join(
        f"{hashlib.sha256(texts[name].encode('utf-8')).hexdigest()}  proofs/{name}\n"
        for name in sorted(texts)
        if name in bound
    )
    (root / "docs/evidence/bundle/source_hashes.sha256").write_text(rows, encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setenv("GOROROBA_MATH", str(math))
    # Restore the module constants and the writer that the runner sets on a producer.
    for module, constants in (
        (gc, ("G2_ROCQ_FILE", "ARC_ROCQ_FILE", "replace_text")),
        (render_span, ("ROCQ_FILE", "replace_text")),
    ):
        for constant in constants:
            monkeypatch.setattr(module, constant, getattr(module, constant))
    return root, math


def test_the_runner_registers_both_producers_with_constants_that_exist() -> None:
    for name, module in (("gaussian_certificates", gc), ("render_span", render_span)):
        constants, sources, _flag, directory = runner.GENERATORS[name]
        constants = (constants,) if isinstance(constants, str) else constants
        sources = (sources,) if isinstance(sources, str) else sources
        if len(constants) != len(sources) or directory != "docs/evidence/a5-gaussian-certificates":
            raise AssertionError(f"{name}: constants, sources or directory are not registered consistently")
        for constant, source in zip(constants, sources, strict=True):
            if source not in SOURCES or getattr(module, constant) is not None:
                raise AssertionError(f"{name}: {constant} is not an unset module constant for {source}")


def test_the_runner_checks_both_producers_against_the_digest_checked_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build(tmp_path, monkeypatch, renderings(), set(SOURCES))
    if runner.main(["gaussian_certificates", "--check"]) != 0:
        raise AssertionError("gaussian_certificates --check fails on its own rendering")
    if runner.main(["render_span", "--check"]) != 0:
        raise AssertionError("render_span --check fails on its own rendering")


def test_the_runner_check_fails_where_a_source_differs_from_the_rendering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    texts = renderings()
    texts[gc.ARC_FILE] = texts[gc.ARC_FILE].replace("(-44, -2291)", "(-44, -2290)", 1)
    build(tmp_path, monkeypatch, texts, set(SOURCES))
    if (
        runner.main(["gaussian_certificates", "--check"]) != 1
        or "DIFFERS A5W8ArcMatrixRanks.v" not in capsys.readouterr().out
    ):
        raise AssertionError("a source that differs from the rendering passed --check")


@pytest.mark.parametrize("producer", ["gaussian_certificates", "render_span"])
@pytest.mark.parametrize("edited", sorted(SOURCES))
def test_the_runner_refuses_a_source_off_its_retained_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], producer: str, edited: str
) -> None:
    _root, math = build(tmp_path, monkeypatch, renderings(), set(SOURCES))
    path = math / "rocq/quantum" / edited
    path.write_text(path.read_text(encoding="utf-8") + "(* edited *)\n", encoding="utf-8")
    owns = {"gaussian_certificates": {gc.G2_FILE, gc.ARC_FILE}, "render_span": {render_span.ROCQ_NAME}}[producer]
    status = runner.main([producer, "--check"])
    err = capsys.readouterr().err
    if edited in owns and (status != 2 or "differs from the retained digest" not in err):
        raise AssertionError(f"{producer} compared an edited {edited}")
    if edited not in owns and status != 0:
        raise AssertionError(f"{producer} read a source it does not render")


def test_the_runner_refuses_a_source_without_a_retained_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    build(tmp_path, monkeypatch, renderings(), {gc.G2_FILE})
    if (
        runner.main(["gaussian_certificates", "--check"]) != 2
        or "no retained record holds a digest" not in capsys.readouterr().err
    ):
        raise AssertionError("a producer of two sources ran with one source unbound")


def test_the_runner_write_replaces_both_sources_and_refuses_a_linked_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale = {name: "(* stale *)\n" for name in SOURCES}
    _root, math = build(tmp_path, monkeypatch, stale, set())
    record = tmp_path / "left-inverses.json"
    monkeypatch.setattr(gc, "LEFT_INVERSES", record)
    if runner.main(["gaussian_certificates", "--write"]) != 0:
        raise AssertionError("gaussian_certificates --write failed")
    texts = renderings()
    for name in (gc.G2_FILE, gc.ARC_FILE):
        if (math / "rocq/quantum" / name).read_text(encoding="utf-8") != texts[name]:
            raise AssertionError(f"{name} is not the rendering after --write")
    if record.read_text(encoding="utf-8") != gc.LEFT_INVERSES.read_text(encoding="utf-8"):
        raise AssertionError("--write did not write the left-inverse record")
    outside = tmp_path / "outside.v"
    outside.write_text("kept\n", encoding="utf-8")
    target = math / "rocq/quantum" / gc.ARC_FILE
    target.unlink()
    target.symlink_to(outside)
    if runner.main(["gaussian_certificates", "--write"]) != 2 or outside.read_text(encoding="utf-8") != "kept\n":
        raise AssertionError("--write went through a symbolic link")


def test_the_runner_rejects_an_entry_whose_constants_and_sources_differ_in_number(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(runner.GENERATORS, "gaussian_certificates", (("A", "B"), ("X.v",), "--write", None))
    if runner.main(["gaussian_certificates", "--check"]) != 2 or "constants for" not in capsys.readouterr().err:
        raise AssertionError("an entry with unequal tuples reached the producer")


def test_a_producer_without_the_runner_needs_its_rocq_directory(capsys: pytest.CaptureFixture[str]) -> None:
    for module in (gc, render_span):
        if module.main(["--check"]) != 2 or "--rocq" not in capsys.readouterr().err:
            raise AssertionError(f"{module.__name__} ran without a Rocq directory")


# ---------------------------------------------------------------- registration


def test_the_generators_are_registered_in_the_lint_and_type_lists_and_the_gates() -> None:
    script = (ROOT / "ci/pr_checks.sh").read_text(encoding="utf-8")
    for name in ("gaussian_certificates", "make_mutants", "span_certificate", "render_span", "make_span_mutants"):
        for prefix in ("docs/", "../docs/"):
            if f"{prefix}evidence/a5-gaussian-certificates/{name}.py" not in script:
                raise AssertionError(f"ci/pr_checks.sh lacks {prefix}evidence/a5-gaussian-certificates/{name}.py")
    gates = {gate["name"]: gate for gate in json.loads((ROOT / "ci/gates.json").read_text(encoding="utf-8"))["gates"]}
    for name, command in (
        ("sources-a5-gaussian-certificates-check", "gaussian_certificates --check"),
        ("sources-a5-gaussian-certificates-span-check", "render_span --check"),
    ):
        gate = gates[name]
        if not gate["cmd"].endswith(f"scripts/math_source_generators.py {command}") or gate.get("requires") != [
            "gororoba-math"
        ]:
            raise AssertionError(f"{name} does not run the runner on {command} with requires gororoba-math")
    driver = gates["sources-a5-gaussian-certificates-span-driver-shellcheck"]
    if not driver["cmd"].endswith("docs/evidence/a5-gaussian-certificates/run_span_checks.sh") or "requires" in driver:
        raise AssertionError("the shellcheck gate of the span driver is not registered")
