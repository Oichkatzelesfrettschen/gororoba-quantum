"""truncation_check: --timeout is one deadline shared by the Singular calls, so each call receives the time left and a
call with none left is blocked without starting."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAR0 = ROOT / "docs/evidence/a5-char0-transfer"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(CHAR0))

import truncation_check as tc  # noqa: E402

PRIMES = ((32009, 10754), (32029, 9115))


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


class _Clock:
    """A clock that a fake Singular advances by the seconds each call costs; `calls` holds each call's allowance."""

    def __init__(self, costs: list[float]) -> None:
        self.now = 1000.0
        self.costs = costs
        self.calls: list[tuple[str, int]] = []

    def __call__(self) -> float:
        return self.now

    def run(self, _script: str, stage: str, timeout_seconds: int) -> Any:
        cost = self.costs[len(self.calls)]
        self.calls.append((stage, timeout_seconds))
        if cost > timeout_seconds:
            self.now += timeout_seconds
            return tc.rees.SingularOutcome("blocked_timeout", stage, {}, 0, None, f"exceeded {timeout_seconds}")
        self.now += cost
        results = {"rj_count": "1", "rj_1": "t1+t2"}
        return tc.rees.SingularOutcome("completed", stage, results, int(cost * 10**9), None, None)


def _install(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, clock: _Clock) -> None:
    for prime, root in PRIMES:
        directory = tmp_path / f"p{prime}-r{root}"
        directory.mkdir()
        (directory / "xm-nm.sing").write_text(f"ring r={prime},(t1,t2),dp;\nideal J=t1+t2;\nquit;\n")
    monkeypatch.setattr(tc.rc, "HEADERS", tmp_path)
    monkeypatch.setattr(tc.rc, "PRIMES", PRIMES)
    monkeypatch.setattr(tc.rc, "_script", lambda *_args, **_kwargs: "ring r=0,(t1,t2),dp;\nquit;\n")
    monkeypatch.setattr(tc.rees, "_run_singular", clock.run)
    monkeypatch.setattr(tc, "_now", clock)


def test_each_call_receives_the_time_left_on_the_shared_deadline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    clock = _Clock([700, 200, 50])
    _install(monkeypatch, tmp_path, clock)
    result = tc.check("xm-nm", 4, 1000)
    _check(result["verdict"] == "survives")
    _check(clock.calls == [("truncation_qi", 1000), ("truncation_32009", 300), ("truncation_32029", 100)])


def test_a_call_with_no_time_left_is_blocked_without_starting(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clock = _Clock([500, 500, 1])
    _install(monkeypatch, tmp_path, clock)
    with pytest.raises(SystemExit, match=r"truncation_32029: blocked_timeout"):
        tc.check("xm-nm", 4, 1000)
    # The third call finds the deadline reached and never reaches Singular.
    _check([stage for stage, _ in clock.calls] == ["truncation_qi", "truncation_32009"])


def test_two_calls_cannot_each_take_the_whole_inner_limit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # 39,500 s then 600 s each fit a 39,700 s limit alone; together they exceed it, so the second call is cut to 200 s.
    clock = _Clock([39_500, 600, 1])
    _install(monkeypatch, tmp_path, clock)
    with pytest.raises(SystemExit, match=r"truncation_32009: blocked_timeout"):
        tc.check("xm-nm", 4, 39_700)
    _check(clock.calls == [("truncation_qi", 39_700), ("truncation_32009", 200)])
    _check(clock.now - 1000.0 <= 39_700)


def test_a_fraction_of_a_second_left_does_not_start_a_call(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    clock = _Clock([9.5, 1, 1])
    _install(monkeypatch, tmp_path, clock)
    with pytest.raises(SystemExit, match="blocked_timeout"):
        tc.check("xm-nm", 4, 10)
    _check(len(clock.calls) == 1)
