"""The retained Q(i) quadric-ring record of the weight slice, re-derived from its stored numbers.

No Singular runs. `audit` recomputes every verdict from the dimension, degree, length and radical fields of a
record, so a field edited to flip a verdict is reported. The default tests drive the producer and `audit_row` on
constructed rows; the tests that read the retained record, its relation digests and its recorded predictions carry the
audit marker and run through `pytest -m audit`. The record replays under Singular on demand through the gate
`core-a5-weight-slice-quadric-rings` of ci/gates.json.
"""

import json
import os
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


@pytest.mark.audit
def test_the_retained_record_passes_the_audit_and_the_producer_check() -> None:
    record = _record()
    _same(audit(record, _retained_digests()), [])
    _same(wsqr.problems(record), [])


@pytest.mark.audit
def test_the_record_is_the_bytes_the_program_writes_for_it() -> None:
    record = _record()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    _same(RECORD.read_text(encoding="utf-8"), text)
    _same(all("measurements" not in row for row in wsqr.comparable(record)["cells"]), True)


@pytest.mark.audit
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


@pytest.mark.audit
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


def _row(**fields: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "ring": "R",
        "krull_dim": 2,
        "degree": 3,
        "length": 3,
        "cohen_macaulay": True,
        "chart": {"dim": 0, "length": 3, "squarefree_eliminants": 4, "variables": 4},
        "radical": None,
        "reduced": True,
        "hypothesis_holds": True,
        "relations_sha256": "d",
        "relations_match_retained": True,
    }
    return {**row, **fields}


def _nonreduced_row() -> dict[str, Any]:
    radical = {
        "radical_equal": False,
        "linear_forms": 1,
        "linear_square_in_K": True,
        "linear_outside_K": True,
        "radical_dim": 2,
        "radical_degree": 3,
    }
    return _row(degree=4, length=5, cohen_macaulay=False, radical=radical, reduced=False)


def test_the_row_audit_accepts_constructed_rows_and_reports_each_flipped_verdict() -> None:
    _same(audit_row(_row()), [])
    _same(audit_row(_nonreduced_row()), [])
    for flipped in (_row(length=4), _row(reduced=False), _row(hypothesis_holds=False)):
        if not audit_row(flipped):
            raise AssertionError(flipped)
    for changed in ({"reduced": True}, {"cohen_macaulay": True}, {"radical": None}):
        if not audit_row({**_nonreduced_row(), **changed}):
            raise AssertionError(changed)


def test_the_producer_reports_an_undecided_ring_and_a_falsifying_ring() -> None:
    record: dict[str, Any] = {"calibration": [], "cells": [_row(ring="A")]}
    _same(wsqr.problems(record), [])
    undecided = {**record, "cells": [_row(ring="A", hypothesis_holds=None)]}
    _same(any("undecided" in line for line in wsqr.problems(undecided)), True)
    falsified = {**record, "cells": [_row(ring="A", hypothesis_holds=False)]}
    _same(any("reduced" in line for line in wsqr.problems(falsified)), True)
    differing = {**record, "cells": [_row(ring="A", relations_match_retained=False)]}
    _same(any("retained" in line for line in wsqr.problems(differing)), True)
    unreproduced = {"calibration": [_row(ring="C", reproduced=False)], "cells": []}
    _same(any("calibration" in line for line in wsqr.problems(unreproduced)), True)


def test_the_cells_run_through_the_pool_in_order_under_the_memory_cap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _same(wsqr.MAX_WORKERS, 6)
    if wsqr.MAX_WORKERS * wsqr.ws.SINGULAR_ADDRESS_SPACE_BYTES > wsqr.MEMORY_BUDGET_BYTES:
        raise AssertionError("the worker cap exceeds the memory budget")
    calls: list[tuple[str, int, int]] = []

    def serial_map(function: Callable[[Any], Any], items: list[Any], min_items: int = 64) -> list[Any]:
        calls.append((function.__name__, len(items), int(os.environ["GOROROBA_WORKERS"])))
        return [function(item) for item in items]

    def fake_decide(name: str, n: int, polys: list[str], steps: Path | None) -> dict[str, Any]:
        known = wsqr.CALIBRATION.get(name)
        cohen_macaulay, reduced = (True, True) if known is None else (known[2], known[3])
        return _row(ring=name, cohen_macaulay=cohen_macaulay, reduced=reduced)

    monkeypatch.setenv("GOROROBA_WORKERS", "64")
    monkeypatch.setattr(wsqr.parallel, "ordered_map", serial_map)
    monkeypatch.setattr(wsqr, "decide", fake_decide)
    monkeypatch.setattr(wsqr, "polynomials", lambda lines: list(lines))
    monkeypatch.setattr(wsqr.ws, "singular_version", lambda: ("banner", "4.4.1"))
    monkeypatch.setattr(wsqr.ws, "fiber_script", lambda *args: "script")
    monkeypatch.setattr(wsqr.ws, "orbit_task", lambda orbit: orbit)
    monkeypatch.setattr(wsqr.ws, "run_singular", lambda script: {"relations": ["r"]})
    monkeypatch.setattr(
        wsqr.ws, "summarize_fiber_run", lambda run: {"generator_count": 1, "relations_sha256": "digest"}
    )
    retained = {wsqr.ws.incidence_name(orbit, source): "digest" for source, orbit in wsqr.CELLS}
    monkeypatch.setattr(wsqr, "WEIGHT_SLICE", tmp_path / "weight-slice.json")
    cells = [{"incidence": name, "relations_sha256": digest, "characteristic": 0} for name, digest in retained.items()]
    (tmp_path / "weight-slice.json").write_text(json.dumps({"cells": cells}), encoding="utf-8")
    out = tmp_path / "out.json"
    monkeypatch.setattr(sys, "argv", ["weight_slice_quadric_rings.py", "--out", str(out)])
    _same(wsqr.main(), 0)
    written = json.loads(out.read_text(encoding="utf-8"))
    _same([row["ring"] for row in written["cells"]], list(retained))
    _same([row["ring"] for row in written["calibration"]], list(wsqr.CALIBRATION))
    _same(written["complete"], True)
    _same([call[:2] for call in calls], [("calibration_ring", 4), ("cell", 8)])
    _same(all(1 <= call[2] <= 6 for call in calls), True)
