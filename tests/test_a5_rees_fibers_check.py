"""The verdict of the modular Rees fiber certificates of E8-bar and Iso at p = 32009.

No Singular runs. The default tests feed a constructed toy log (the ideal (y1^2) in two variables) to the verdict
of `check_rees_fibers.py` and require each known-bad variant to fail; the test that reads the retained logs carries
the audit marker and runs through `pytest -m audit`.
"""

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

RUN = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "evidence"
    / "a5-exceptional-fibers"
    / "working"
    / "runs"
    / "e8-rees-fibers-v2-p32009"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_rees_fibers", RUN / "check_rees_fibers.py")
    if spec is None or spec.loader is None:
        raise AssertionError("check_rees_fibers.py does not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_rees_fibers = _load()
SCRIPT_DIGEST = hashlib.sha256(b"toy script").hexdigest()
TOY = "\n".join(
    [
        check_rees_fibers.SINGULAR_VERSION,
        f"{SCRIPT_DIGEST}  toy.sing",
        "CERT unit_identity_bad 0 all_positive_degree 1",
        "CERT pivot_nonzerodivisor_mod_J 1",
        "CERT satstd_isSB 1 leading_u_bad 0",
        "K quadrics 1 dim 1 mult 2",
        "RELATIONS 1 of 3",
        "REL 1,1:1",
        "FIBER bound 0 minimal generators 1 dim 1 mult 2",
        "generator degrees 2",
        "FIBER outside_K 0 K_outside_fiber 0",
        "hilb",
        "1,0,-1,0",
        "STAGE rees_done 3",
        "EXIT 0",
        "",
    ]
)


_RESULT_TAIL = (
    "FIBER bound 0 minimal generators 1 dim 1 mult 2\n"
    "generator degrees 2\n"
    "FIBER outside_K 0 K_outside_fiber 0\n"
    "hilb\n"
    "1,0,-1,0\n"
    "STAGE rees_done 3\n"
)


@pytest.fixture
def _toy_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(check_rees_fibers.RUNS, "toy", (2, 0, 1, 1, 2))


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.usefixtures("_toy_run")
def test_a_complete_log_passes() -> None:
    _same(check_rees_fibers.log_verdict("toy", TOY, SCRIPT_DIGEST), [])


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("FIBER outside_K 0 K_outside_fiber 0", "FIBER outside_K 1 K_outside_fiber 0"),
        ("FIBER outside_K 0 K_outside_fiber 0", "FIBER outside_K 0 K_outside_fiber 2"),
        ("EXIT 0", "EXIT 1"),
        ("CERT pivot_nonzerodivisor_mod_J 1", "CERT pivot_nonzerodivisor_mod_J 0"),
        ("CERT unit_identity_bad 0", "CERT unit_identity_bad 1"),
        ("CERT satstd_isSB 1", "CERT satstd_isSB 0"),
        ("leading_u_bad 0", "leading_u_bad 4"),
        ("mult 2\nRELATIONS", "mult 3\nRELATIONS"),
        ("generators 1 dim 1 mult 2", "generators 1 dim 1 mult 3"),
        ("generator degrees 2", "generator degrees 3"),
        ("1,0,-1,0", "1,0,-1,1,0"),
        ("1,0,-1,0", "1,0,-2,0"),
        ("REL 1,1:1\n", ""),
        ("REL 1,1:1\n", "REL 1,1:0\n"),
        (SCRIPT_DIGEST, "0" * 64),
        ("EXIT 0", "CERT FAIL saturation\nEXIT 0"),
        (_RESULT_TAIL, ""),
        (_RESULT_TAIL + "EXIT 0\n", ""),
        ("FIBER outside_K 0 K_outside_fiber 0\n", ""),
        ("EXIT 0", "   ? `y(3)` is undefined\nEXIT 0"),
    ],
)
@pytest.mark.usefixtures("_toy_run")
def test_each_known_bad_variant_fails(old: str, new: str) -> None:
    if old not in TOY:
        raise AssertionError(old)
    if not check_rees_fibers.log_verdict("toy", TOY.replace(old, new), SCRIPT_DIGEST):
        raise AssertionError(f"accepted {new!r}")


def test_hilbert_valuation_reads_dimension_and_multiplicity() -> None:
    _same(check_rees_fibers.hilbert_valuation([1, 0, -1]), (1, 2))
    _same(check_rees_fibers.hilbert_valuation([1, -2, 1]), (2, 1))


def test_the_span_form_is_independent_of_row_choice() -> None:
    rows = [{(1, 1): 1, (1, 2): 5}, {(1, 2): 1}]
    mixed = [{(1, 1): 1}, {(1, 2): 3}]
    _same(check_rees_fibers.reduced_rows(rows), check_rees_fibers.reduced_rows(mixed))


@pytest.mark.audit
def test_the_retained_logs_pass_the_verdict_and_the_known_bad_variants_fail() -> None:
    _same(check_rees_fibers.check(), [])
    _same(check_rees_fibers.self_test(), [])
