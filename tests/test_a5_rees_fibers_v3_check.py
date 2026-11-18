"""The verdict of the zero-generator guard run of the Iso -> N- Rees fiber at p = 32009.

No Singular runs. The tests read the retained logs of e8-rees-fibers-v3-p32009 and feed each known-bad variant to the
verdict of `check_rees_fibers_v3.py`: the Iso log without its per-generator lines, a nonzero count of zero constant
terms, the failure marker, and the toy log of a generator that is 0 modulo J.
"""

import hashlib
import importlib.util
import re
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
    / "e8-rees-fibers-v3-p32009"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_rees_fibers_v3", RUN / "check_rees_fibers_v3.py")
    if spec is None or spec.loader is None:
        raise AssertionError("check_rees_fibers_v3.py does not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_v3 = _load()


def _digest(name: str) -> str:
    return hashlib.sha256((RUN / f"{name}.sing").read_bytes()).hexdigest()


ISO_LOG = (RUN / f"{check_v3.ISO}.log").read_text()
TOY_LOG = (RUN / f"{check_v3.TOY}.log").read_text()
CONTROL_LOG = (RUN / f"{check_v3.CONTROL}.log").read_text()
ISO_DIGEST = _digest(check_v3.ISO)


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_the_successor_script_is_the_v2_script_with_the_listed_edits() -> None:
    v2_script = (check_v3.V2_DIR / f"{check_v3.ISO_V2}.sing").read_text()
    _same(check_v3.successor_script(v2_script), (RUN / f"{check_v3.ISO}.sing").read_text())


def test_the_retained_iso_log_passes() -> None:
    _same(check_v3.log_verdict(ISO_LOG, ISO_DIGEST), [])
    for line in ("FIBER bound 0 minimal generators 68 dim 5 mult 23", "FIBER outside_K 0 K_outside_fiber 0"):
        if line not in ISO_LOG.split("\n"):
            raise AssertionError(line)


def test_the_toy_log_is_rejected_with_the_marker_named() -> None:
    problems = check_v3.log_verdict(TOY_LOG, _digest(check_v3.TOY))
    if not any(check_v3.MARKER in problem for problem in problems):
        raise AssertionError(problems)


def test_the_toy_and_control_logs_pass_their_own_verdicts() -> None:
    _same(check_v3.toy_problems(TOY_LOG, _digest(check_v3.TOY)), [])
    _same(check_v3.control_problems(CONTROL_LOG, _digest(check_v3.CONTROL)), [])
    if not check_v3.toy_problems(CONTROL_LOG, _digest(check_v3.CONTROL)):
        raise AssertionError("the control log passed the toy verdict")
    if not check_v3.control_problems(TOY_LOG, _digest(check_v3.TOY)):
        raise AssertionError("the toy log passed the control verdict")


def test_a_log_without_the_per_generator_lines_is_rejected() -> None:
    stripped = re.sub(r"^UNIT \d+ c\(0\)=.*\n", "", ISO_LOG, flags=re.MULTILINE)
    if stripped == ISO_LOG:
        raise AssertionError("no per-generator line found")
    if not check_v3.unit_problems(stripped.split("\n")):
        raise AssertionError("accepted a log without per-generator lines")
    if not check_v3.log_verdict(stripped, ISO_DIGEST):
        raise AssertionError("the verdict accepted a log without per-generator lines")


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("UNIT zero_constant_term_count 0\n", ""),
        ("UNIT zero_constant_term_count 0", "UNIT zero_constant_term_count 1"),
        ("UNIT 1 c(0)=-10754", "UNIT 1 c(0)=0"),
        ("UNIT 17 c(0)=", "UNIT 18 c(0)="),
        ("EXIT 0", "CERT FAIL unit_zero_generator\nEXIT 0"),
        ("FIBER outside_K 0 K_outside_fiber 0", "FIBER outside_K 1 K_outside_fiber 0"),
        ("dim 5 mult 23", "dim 5 mult 22"),
        ("EXIT 0", "EXIT 1"),
        (ISO_DIGEST, "0" * 64),
        ("FIBER outside_K 0 K_outside_fiber 0\n", ""),
    ],
)
def test_each_known_bad_iso_variant_fails(old: str, new: str) -> None:
    if old not in ISO_LOG:
        raise AssertionError(old)
    if not check_v3.log_verdict(ISO_LOG.replace(old, new), ISO_DIGEST):
        raise AssertionError(f"accepted {new!r}")


def test_the_unit_lines_must_agree_with_the_count() -> None:
    lines = [f"UNIT {k} c(0)=5 c=s2+5" for k in range(1, check_v3.GENERATORS + 1)]
    _same(check_v3.unit_problems([*lines, f"{check_v3.COUNT} 0"]), [])
    zero = [lines[0].replace("c(0)=5", "c(0)=0"), *lines[1:]]
    if len(check_v3.unit_problems([*zero, f"{check_v3.COUNT} 1"])) < 1:
        raise AssertionError("a generator with c(0) = 0 was accepted")
    if len(check_v3.unit_problems([*zero, f"{check_v3.COUNT} 0"])) < 2:
        raise AssertionError("a count that misses the zero constant term was accepted")


def test_the_retained_directory_passes_the_check_and_the_self_test() -> None:
    _same(check_v3.check(), [])
    _same(check_v3.self_test(), [])
