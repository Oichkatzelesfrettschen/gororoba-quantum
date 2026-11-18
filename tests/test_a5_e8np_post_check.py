"""The control verdict of the post-check of the E8-bar -> N+ degree-2 receipt at p = 32009.

No Singular runs. `control_rejects` accepts a control only when Singular printed exactly one pair of nonnegative
integer remainder counts for it and one count is positive. The default tests feed constructed Singular output; the
test that reads the retained post.log carries the audit marker and runs through `pytest -m audit`.
"""

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
    / "e8np-d2-receipt-p32009"
)


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("e8np_post_check", RUN / "post_check.py")
    if spec is None or spec.loader is None:
        raise AssertionError("post_check.py does not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


post_check = _load()


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_a_control_with_one_pair_of_counts_and_a_positive_count_rejects() -> None:
    for line in ("RESULT control_direct 1 1", "RESULT control_direct 0 3", "RESULT control_direct 12 0"):
        _same(post_check.control_rejects(line + "\n", "control_direct"), True)


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "RESULT direct 0 0\n",
        "RESULT control_transport 1 1\n",
        "RESULT control_direct\n",
        "RESULT control_direct 1\n",
        "RESULT control_direct 1 1 1\n",
        "RESULT control_direct 0 0\n",
        "RESULT control_direct x 1\n",
        "RESULT control_direct -1 1\n",
        "RESULT control_direct 1.0 1\n",
        "RESULT control_direct 1 1\nRESULT control_direct 1 1\n",
    ],
)
def test_a_control_that_is_missing_repeated_malformed_or_zero_fails(stdout: str) -> None:
    _same(post_check.control_rejects(stdout, "control_direct"), False)


def test_a_control_is_read_only_under_its_own_tag() -> None:
    stdout = "RESULT control_direct 1 1\nRESULT control_transport 0 0\n"
    _same(post_check.control_rejects(stdout, "control_direct"), True)
    _same(post_check.control_rejects(stdout, "control_transport"), False)
    _same(post_check.result_rows(stdout, "direct"), [])


@pytest.mark.audit
def test_the_retained_post_log_passes_both_controls() -> None:
    log = (RUN / "post.log").read_text(encoding="utf-8")
    _same(post_check.control_rejects(log, "control_direct"), True)
    _same(post_check.control_rejects(log, "control_transport"), True)
    _same(post_check.result_rows(log, "direct"), [["0", "0"]])
    _same(post_check.result_rows(log, "transport"), [["0", "0"]])
