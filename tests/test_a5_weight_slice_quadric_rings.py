"""The retained Q(i) quadric-ring record of the weight slice, re-derived from its stored numbers.

No Singular runs. `audit` recomputes every verdict from the dimension, degree, length and radical fields of the
retained record, so a field edited to flip a verdict is reported; the mutations below prove it. The record replays
under Singular on demand through the gate `core-a5-weight-slice-quadric-rings` of ci/gates.json.
"""

import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACH = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACH))

import weight_slice_quadric_rings as wsqr  # noqa: E402

RECORD = ATTACH / "weight-slice-quadric-rings-result.json"
WEIGHT_SLICE = ATTACH / "weight-slice-fiber-relations-result.json"

# ring -> (Krull dimension, degree, Artinian length of the linear section, Cohen-Macaulay, reduced): the predictions
# of weight-slice-quadric-rings-case.md, written before the run.
PREDICTED: dict[str, tuple[int, int, int, bool, bool]] = {
    "X-->N-": (4, 12, 15, False, False),
    "X+->N+": (4, 12, 15, False, False),
    "Iso->N-": (5, 23, 23, True, True),
    "Iso->N+": (5, 23, 23, True, True),
    "W8->N-": (6, 50, 50, True, True),
    "W8->N+": (6, 50, 50, True, True),
    "E8bar->N-": (5, 11, 20, False, False),
    "E8bar->N+": (5, 11, 20, False, False),
}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    record: dict[str, Any] = json.loads(RECORD.read_text(encoding="utf-8"))
    return record


def _retained_digests() -> dict[str, str]:
    record = json.loads(WEIGHT_SLICE.read_text(encoding="utf-8"))
    return {c["incidence"]: c["relations_sha256"] for c in record["cells"] if c["characteristic"] == 0}


def audit_row(row: dict[str, Any]) -> list[str]:
    """Problems of one ring, from its stored numbers and never from its stored verdict booleans."""
    name = row["ring"]
    found: list[str] = []
    if row["length"] < row["degree"]:
        found.append(f"{name}: length {row['length']} below degree {row['degree']}")
    if row["cohen_macaulay"] is not (row["length"] == row["degree"]):
        found.append(f"{name}: Cohen-Macaulay flag contradicts length and degree")
    radical = row["radical"]
    chart = row["chart"]
    chart_radical = (
        row["cohen_macaulay"]
        and chart["dim"] == 0
        and chart["length"] == row["degree"]
        and chart["squarefree_eliminants"] == chart["variables"]
    )
    if chart_radical:
        reduced: bool | None = True
    elif radical is None:
        reduced = None
    else:
        reduced = bool(radical["radical_equal"])
        pure = radical["linear_forms"] == 0 and radical["radical_degree"] == row["degree"]
        if radical["radical_equal"] is not pure:
            found.append(f"{name}: radical flag contradicts the radical's linear part and degree")
        if radical["radical_dim"] != row["krull_dim"]:
            found.append(f"{name}: the radical has dimension {radical['radical_dim']}, not {row['krull_dim']}")
        nilpotent = radical["linear_forms"] > 0 and radical["linear_square_in_K"] and radical["linear_outside_K"]
        if not reduced and not nilpotent:
            found.append(f"{name}: a nonreduced ring needs a nilpotent linear form outside K whose square lies in K")
    if reduced is None:
        found.append(f"{name}: reducedness is undecided")
    elif row["reduced"] is not reduced:
        found.append(f"{name}: reduced flag contradicts the certificate")
    if reduced is not None and row["hypothesis_holds"] is not (row["cohen_macaulay"] is reduced):
        found.append(f"{name}: hypothesis flag contradicts Cohen-Macaulay and reduced")
    return found


def audit(record: dict[str, Any], retained: dict[str, str]) -> list[str]:
    """Every problem of a record: schema, ring order, calibration, digests, predictions and each ring's numbers."""
    found: list[str] = []
    if record.get("schema") != wsqr.SCHEMA or record.get("field") != "Q(i)":
        found.append("schema or field")
    if [row["ring"] for row in record["calibration"]] != list(wsqr.CALIBRATION):
        found.append("calibration rings")
    for row in record["calibration"]:
        known = wsqr.CALIBRATION[row["ring"]]
        if (row["cohen_macaulay"], row["reduced"]) != (known[2], known[3]) or row["reproduced"] is not True:
            found.append(f"calibration {row['ring']}: answer departs from the known one")
        found += audit_row(row)
    if [row["ring"] for row in record["cells"]] != [wsqr.ws.incidence_name(o, s) for s, o in wsqr.CELLS]:
        found.append("cell order or names")
    for row in record["cells"]:
        found += audit_row(row)
        if row["relations_sha256"] != retained.get(row["ring"]) or row["relations_match_retained"] is not True:
            found.append(f"{row['ring']}: relations digest differs from the weight-slice record")
        want = PREDICTED.get(row["ring"])
        shape = (row["krull_dim"], row["degree"], row["length"], row["cohen_macaulay"], row["reduced"])
        if want is None or shape != want:
            found.append(f"{row['ring']}: departs from the recorded prediction")
    summary = (record["problems"], record["complete"], record["hypothesis_holds_on_every_cell"])
    if summary != ([], True, True):
        found.append("summary flags")
    return found


def test_the_retained_record_passes_the_audit_and_the_producer_check() -> None:
    record = _record()
    _same(audit(record, _retained_digests()), [])
    _same(wsqr.problems(record), [])


def test_the_record_is_the_bytes_the_program_writes_for_it() -> None:
    record = _record()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    _same(RECORD.read_text(encoding="utf-8"), text)
    _same(all("measurements" not in row for row in wsqr.comparable(record)["cells"]), True)


def test_the_two_nonreduced_families_carry_nilpotent_linear_forms_and_the_reduced_ones_none() -> None:
    cells = {row["ring"]: row for row in _record()["cells"]}
    for name in ("X-->N-", "X+->N+"):
        _same(cells[name]["radical"]["linear_forms"], 3)
    for name in ("E8bar->N-", "E8bar->N+"):
        _same(cells[name]["radical"]["linear_forms"], 5)
    for name in ("Iso->N-", "Iso->N+", "W8->N-", "W8->N+"):
        _same(cells[name]["radical"]["linear_forms"], 0)


def _set(path: tuple[Any, ...], value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(record: dict[str, Any]) -> None:
        target: Any = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


def _drop_cell(record: dict[str, Any]) -> None:
    record["cells"].pop()


def _swap_cells(record: dict[str, Any]) -> None:
    record["cells"][0], record["cells"][1] = record["cells"][1], record["cells"][0]


MUTATIONS: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
    ("length of X-", _set(("cells", 0, "length"), 12)),
    ("length of Iso", _set(("cells", 2, "length"), 24)),
    ("CM flag of E8bar", _set(("cells", 6, "cohen_macaulay"), True)),
    ("CM flag of W8", _set(("cells", 4, "cohen_macaulay"), False)),
    ("reduced flag of X-", _set(("cells", 0, "reduced"), True)),
    ("reduced flag of W8", _set(("cells", 4, "reduced"), False)),
    ("radical flag of W8", _set(("cells", 4, "radical", "radical_equal"), False)),
    ("radical flag of E8bar", _set(("cells", 6, "radical", "radical_equal"), True)),
    ("linear forms of X-", _set(("cells", 0, "radical", "linear_forms"), 0)),
    ("square of the linear forms", _set(("cells", 6, "radical", "linear_square_in_K"), False)),
    ("radical dimension", _set(("cells", 2, "radical", "radical_dim"), 4)),
    ("hypothesis flag", _set(("cells", 6, "hypothesis_holds"), False)),
    ("relations digest", _set(("cells", 3, "relations_sha256"), "0" * 64)),
    ("digest match flag", _set(("cells", 3, "relations_match_retained"), False)),
    ("degree of Iso", _set(("cells", 2, "degree"), 22)),
    ("dimension of W8", _set(("cells", 4, "krull_dim"), 5)),
    ("radical missing", _set(("cells", 2, "radical"), None)),
    ("calibration reproduced", _set(("calibration", 1, "reproduced"), False)),
    ("calibration answer", _set(("calibration", 1, "cohen_macaulay"), False)),
    ("calibration reduced", _set(("calibration", 2, "reduced"), False)),
    ("complete flag", _set(("complete",), False)),
    ("problems list", _set(("problems",), ["a problem"])),
    ("summary flag", _set(("hypothesis_holds_on_every_cell",), False)),
    ("schema", _set(("schema",), "other/1")),
    ("field", _set(("field",), "Q")),
    ("dropped cell", _drop_cell),
    ("swapped cells", _swap_cells),
]


@pytest.mark.parametrize(("label", "mutate"), MUTATIONS, ids=[label for label, _ in MUTATIONS])
def test_every_mutation_of_a_deciding_field_is_reported(label: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    record = _record()
    mutate(record)
    if not audit(record, _retained_digests()):
        raise AssertionError(f"the mutation {label} passed")


def test_the_producer_verdict_follows_the_chart_then_the_radical() -> None:
    chart: dict[str, Any] = {"dim": 0, "length": 7, "squarefree_eliminants": 4, "variables": 4}
    cm: dict[str, Any] = {"cohen_macaulay": True, "degree": 7, "chart": chart}
    _same(wsqr.chart_decides(cm), True)
    chart_verdict = wsqr.verdict(cm, None)
    _same((chart_verdict["reduced"], chart_verdict["hypothesis_holds"]), (True, True))
    short = {**cm, "chart": {**cm["chart"], "squarefree_eliminants": 3}}
    _same(wsqr.chart_decides(short), False)
    _same(wsqr.verdict(short, None)["reduced"], None)
    _same(wsqr.verdict(short, None)["hypothesis_holds"], None)
    _same(wsqr.verdict(short, {"radical_equal": False})["hypothesis_holds"], False)
    _same(wsqr.verdict({**short, "cohen_macaulay": False}, {"radical_equal": False})["hypothesis_holds"], True)
    _same(wsqr.verdict({**short, "cohen_macaulay": False}, {"radical_equal": True})["hypothesis_holds"], False)
    _same(wsqr.chart_decides({**cm, "cohen_macaulay": False}), False)


def test_the_cohen_macaulay_step_rejects_a_section_that_is_not_a_system_of_parameters() -> None:
    values = {"cm": ["4 12 0 15"], "chart": ["0 13 4 15"], "forms": ["y(1)"]}
    _same(wsqr.cm_row(values)["cohen_macaulay"], False)
    with pytest.raises(RuntimeError):
        wsqr.cm_row({**values, "cm": ["4 12 1 15"]})
    with pytest.raises(RuntimeError):
        wsqr.cm_row({**values, "cm": ["4 12 0 11"]})


def test_the_producer_reports_an_undecided_ring_and_a_falsifying_ring() -> None:
    record = _record()
    undecided = copy.deepcopy(record)
    undecided["cells"][0]["hypothesis_holds"] = None
    _same(any("undecided" in line for line in wsqr.problems(undecided)), True)
    falsified = copy.deepcopy(record)
    falsified["cells"][0]["hypothesis_holds"] = False
    _same(any("reduced" in line for line in wsqr.problems(falsified)), True)
    differing = copy.deepcopy(record)
    differing["cells"][0]["relations_match_retained"] = False
    _same(any("retained" in line for line in wsqr.problems(differing)), True)
