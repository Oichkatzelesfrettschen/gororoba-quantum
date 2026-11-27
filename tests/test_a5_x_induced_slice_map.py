"""The retained induced slice map of same-sign X: its tables, records, reduction logs and digest list.

The Singular runs replay through run_x_induced.sh in the directory of the records.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

DIRECTORY = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map"
CHECKS = [
    (source, prime, root) for source in ("xm", "xp") for prime, root in ((32009, 10754), (32029, 9115), (32057, 8059))
]


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_x_induced_slice_map", DIRECTORY / "x_induced_slice_map.py")
    if spec is None or spec.loader is None:
        raise ImportError(DIRECTORY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("source", ["xm", "xp"])
def test_the_tables_give_fifteen_generators_and_a_cone_of_dimension_four(source: str) -> None:
    mod = load()
    selected = mod.header_selected(source)
    if mod.counts(source) != (15, 69) or mod.cone(source) != (4, 12) or len(set(selected)) != 15:
        raise AssertionError((mod.counts(source), mod.cone(source), selected))


@pytest.mark.parametrize("source", ["xm", "xp"])
def test_the_retained_record_passes_and_is_bound_to_the_weight_slice_digest(source: str) -> None:
    mod = load()
    record = json.loads((DIRECTORY / f"induced-{source}.json").read_text(encoding="utf-8"))
    values = record["values"]
    if (
        record["pass"] is not True
        or record["problems"]
        or record["relations_sha256"] != record["relations_sha256_retained"]
        or record["selected_weight"] != record["selected_weight_retained"]
        or record["selected_header"] != mod.header_selected(source)
        or len(record["relations"]) != 69
        or [len(row) for row in record["map"]] != [15] * 15
        or values["header_outside_span"] != ["0"]
        or values["lift_shape"] != ["15 15 0"]
        or values["control_nonmember_residual"] == ["0"]
    ):
        raise AssertionError(record["problems"])
    high = (DIRECTORY / f"high-{source}-qi.log").read_text(encoding="utf-8").splitlines()
    if "RESULT header_high_weight_outside 0" not in high or "RESULT done 1" not in high:
        raise AssertionError(f"high-{source}-qi.log")


@pytest.mark.parametrize(("source", "prime", "root"), CHECKS)
def test_each_reduction_passes_and_its_conjugate_root_fails(source: str, prime: int, root: int) -> None:
    log = (DIRECTORY / f"check-{source}-p{prime}-r{root}.log").read_text(encoding="utf-8").splitlines()
    wanted = [
        "RESULT transported modulo header 0 header modulo transported 0",
        "RESULT generators 69 dim 4 mult 12 det nonzero 1",
        f"INDUCED VERDICT p {prime} root {root} PASS",
    ]
    if any(line not in log for line in wanted):
        raise AssertionError(log)
    other = prime - root
    control = (DIRECTORY / f"control-{source}-p{prime}-r{other}.log").read_text(encoding="utf-8").splitlines()
    if f"INDUCED VERDICT p {prime} root {other} FAIL" not in control or wanted[0] in control:
        raise AssertionError(control)


def test_the_check_script_states_the_counts_of_the_retained_tables() -> None:
    mod = load()
    record = json.loads((DIRECTORY / "induced-xm.json").read_text(encoding="utf-8"))
    header = DIRECTORY.parents[1] / "distribute/out/a5-xm-d4/xm_p1/d2/relations-upto-d2.rel"
    text = mod.check_script(record, 32009, 10754, header)
    if not text.startswith("ring r=32009,(y(1..15)),dp;") or "size(minbase(fK))==69 and dim(sF)==4" not in text:
        raise AssertionError(text[:200])
    if "mult(sF)==12" not in text:
        raise AssertionError("multiplicity")
    with pytest.raises(RuntimeError):
        mod.check_script(record, 32009, 10755, header)


def test_the_digest_list_names_every_other_file() -> None:
    listed = {}
    for line in (DIRECTORY / "sha256.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        listed[name] = digest
    present = {path.name for path in DIRECTORY.iterdir() if path.is_file() and path.name != "sha256.txt"}
    if set(listed) != present:
        raise AssertionError(sorted(set(listed) ^ present))
    for name, digest in listed.items():
        if hashlib.sha256((DIRECTORY / name).read_bytes()).hexdigest() != digest:
            raise AssertionError(name)


def test_the_run_lists_six_checks_and_six_controls_at_the_other_root() -> None:
    mod = load()
    items = mod.reductions()
    checks = [item[1:] for item in items if item[0] == "check"]
    controls = [item[1:] for item in items if item[0] == "control"]
    if checks != CHECKS or controls != [(source, prime, prime - root) for source, prime, root in CHECKS]:
        raise AssertionError(items)
    for source, prime, _root in CHECKS:
        if not (mod.FIBERS / mod.HEADERS[(source, prime)]).is_file():
            raise AssertionError((source, prime))


def test_the_two_basepoints_give_equal_reduction_logs() -> None:
    for kind, prime, root in [("check", p, r) for p, r in ((32009, 10754), (32029, 9115), (32057, 8059))] + [
        ("control", p, p - r) for p, r in ((32009, 10754), (32029, 9115), (32057, 8059))
    ]:
        logs = [(DIRECTORY / f"{kind}-{source}-p{prime}-r{root}.log").read_bytes() for source in ("xm", "xp")]
        scripts = [(DIRECTORY / f"{kind}-{source}-p{prime}-r{root}.sing").read_bytes() for source in ("xm", "xp")]
        if logs[0] != logs[1] or scripts[0] == scripts[1]:
            raise AssertionError((kind, prime, root))
