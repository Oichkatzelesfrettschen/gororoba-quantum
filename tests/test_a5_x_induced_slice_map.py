"""The checks of the induced slice map of same-sign X, on constructed lines, records and directories.

The retained records, logs and digest list are read on demand by the gate core-a5-x-induced-slice-map-records of
ci/gates.json (x_induced_slice_map.py --verify), and the Singular runs replay through run_x_induced.sh.
"""

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/x_induced_slice_map.py"
)
CELLS = [
    (source, prime, root) for source in ("xm", "xp") for prime, root in ((32009, 10754), (32029, 9115), (32057, 8059))
]


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_x_induced_slice_map", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lines(first: int, second: int, verdict: str, prime: int = 32009, root: int = 10754) -> list[str]:
    return [
        f"RESULT transported modulo header {first} header modulo transported {second}",
        "RESULT generators 69 dim 4 mult 12 det nonzero 1",
        f"INDUCED VERDICT p {prime} root {root} {verdict}",
        "EXIT 0",
    ]


def test_a_check_needs_zero_remainders_and_the_pass_verdict() -> None:
    mod = load()
    if not mod.reduction_good("check", 32009, 10754, lines(0, 0, "PASS")):
        raise AssertionError("a passing check is rejected")
    for bad in (lines(0, 3, "PASS"), lines(0, 0, "FAIL"), lines(0, 0, "PASS", root=21255), lines(0, 0, "PASS")[1:]):
        if mod.reduction_good("check", 32009, 10754, bad):
            raise AssertionError(bad)
    if mod.reduction_good("check", 32009, 10754, lines(0, 0, "PASS") + lines(0, 0, "PASS")):
        raise AssertionError("two lines of remainders are accepted")


def test_a_control_needs_nonzero_remainders_in_both_directions_and_the_fail_verdict() -> None:
    mod = load()
    if not mod.reduction_good("control", 32009, 21255, lines(35, 31, "FAIL", root=21255)):
        raise AssertionError("a failing control is rejected")
    for bad in (
        lines(0, 31, "FAIL", root=21255),
        lines(35, 0, "FAIL", root=21255),
        lines(0, 0, "FAIL", root=21255),
        lines(35, 31, "PASS", root=21255),
    ):
        if mod.reduction_good("control", 32009, 21255, bad):
            raise AssertionError(bad)
    if mod.reduction_good("other", 32009, 21255, lines(35, 31, "FAIL", root=21255)):
        raise AssertionError("an unknown kind is accepted")


def test_the_run_lists_six_checks_and_six_controls_at_the_other_root() -> None:
    mod = load()
    items = mod.reductions()
    checks = [item[1:] for item in items if item[0] == "check"]
    controls = [item[1:] for item in items if item[0] == "control"]
    if checks != CELLS or controls != [(source, prime, prime - root) for source, prime, root in CELLS]:
        raise AssertionError(items)
    if any(pow(root, 2, prime) != prime - 1 for _kind, _source, prime, root in items):
        raise AssertionError("an entry is not a root of -1")
    if sorted(mod.HEADERS) != sorted((source, prime) for source, prime, _root in CELLS):
        raise AssertionError(sorted(mod.HEADERS))


def record() -> dict[str, Any]:
    return {
        "pass": True,
        "problems": [],
        "relations_sha256": "aa",
        "relations_sha256_retained": "aa",
        "selected_weight": [1, 2, 3],
        "selected_weight_retained": [1, 2, 3],
        "selected_header": [4, 5, 6],
        "relations": ["RELATION 1,1:1", "RELATION 1,2:1"],
        "map": [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
        "values": {
            "header_outside_span": ["0"],
            "lift_shape": ["3 3 0"],
            "control_nonmember_residual": ["1"],
        },
    }


RECORD_MUTATIONS = {
    "the record does not pass": lambda r: r.update({"pass": False}),
    "the relation digest differs from the retained weight-slice record": lambda r: r.update(relations_sha256="bb"),
    "the weight-slice selection differs from the retained record": lambda r: r.update(selected_weight=[1, 2, 4]),
    "the header selection differs from the header record": lambda r: r.update(selected_header=[4, 5, 7]),
    "the relation count differs": lambda r: r["relations"].pop(),
    "the map has another shape": lambda r: r["map"][0].pop(),
    "a header Pfaffian lies outside the span": lambda r: r["values"].update(header_outside_span=["2"]),
    "the lift has another shape or degree": lambda r: r["values"].update(lift_shape=["3 3 1"]),
    "the non-member control was accepted": lambda r: r["values"].update(control_nonmember_residual=["0"]),
}


def test_a_constructed_record_passes() -> None:
    mod = load()
    if mod.record_problems(record(), 3, 2, [4, 5, 6]):
        raise AssertionError(mod.record_problems(record(), 3, 2, [4, 5, 6]))


@pytest.mark.parametrize("name", sorted(RECORD_MUTATIONS))
def test_a_changed_record_is_reported_for_its_one_reason(name: str) -> None:
    mod = load()
    changed = record()
    RECORD_MUTATIONS[name](changed)
    if mod.record_problems(changed, 3, 2, [4, 5, 6]) != [name]:
        raise AssertionError(mod.record_problems(changed, 3, 2, [4, 5, 6]))


def test_a_record_with_stored_problems_does_not_pass() -> None:
    mod = load()
    changed = record()
    changed["problems"] = ["x"]
    if mod.record_problems(changed, 3, 2, [4, 5, 6]) != ["the record does not pass"]:
        raise AssertionError("stored problems are accepted")


def test_the_digest_list_reports_a_changed_an_extra_and_a_missing_file(tmp_path: Path) -> None:
    mod = load()
    for name, text in (("a.log", "one\n"), ("b.json", "two\n")):
        (tmp_path / name).write_text(text, encoding="utf-8")
    listing = "".join(
        f"{hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()}  {name}\n" for name in ("a.log", "b.json")
    )
    (tmp_path / "sha256.txt").write_text(listing, encoding="utf-8")
    if mod.digest_problems(tmp_path):
        raise AssertionError(mod.digest_problems(tmp_path))
    (tmp_path / "a.log").write_text("changed\n", encoding="utf-8")
    if mod.digest_problems(tmp_path) != ["a.log: the digest differs from sha256.txt"]:
        raise AssertionError(mod.digest_problems(tmp_path))
    (tmp_path / "a.log").write_text("one\n", encoding="utf-8")
    (tmp_path / "c.sing").write_text("extra\n", encoding="utf-8")
    if mod.digest_problems(tmp_path) != ["c.sing: listed and absent, or present and unlisted"]:
        raise AssertionError(mod.digest_problems(tmp_path))
    (tmp_path / "c.sing").unlink()
    (tmp_path / "b.json").unlink()
    if mod.digest_problems(tmp_path) != ["b.json: listed and absent, or present and unlisted"]:
        raise AssertionError(mod.digest_problems(tmp_path))
