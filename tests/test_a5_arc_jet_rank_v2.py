"""Bounded checks of degree-seven admission, stall evidence and successor replay."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

EVIDENCE = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers"
sys.path.insert(0, str(EVIDENCE / "arc-jets"))
sys.path.insert(0, str(EVIDENCE / "monomial-ladder"))

import jet_rank_v2 as successor  # noqa: E402


@pytest.mark.parametrize(
    "degree,arcs,step,stall",
    [
        (0, 1, 1, None),
        (8, 1, 1, None),
        (1, 0, 1, None),
        (1, -1, 1, None),
        (1, 1, 0, None),
        (1, 1, -1, None),
        (1, 1, 1, 0),
    ],
)
def test_invalid_campaign_arguments_are_rejected_before_computation(
    degree: int, arcs: int, step: int, stall: int | None
) -> None:
    """Dropping admission allows empty campaigns or unsupported degrees to look like evidence."""
    with pytest.raises(ValueError, match="degree|arc count|step|stall"):
        successor.compute("e8nm-p32009", degree, arcs, step, None, stall)


def test_degree_seven_uses_the_basis_radical_dimension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Falling back to degree six would subtract 1526 instead of the degree-seven radical dimension 2514."""
    basis = tmp_path / "basis.json"
    basis.write_text(json.dumps({"base_dimension": 2514}))
    monkeypatch.setattr(successor.J, "ROOT", tmp_path)
    dimension, source = successor.radical_hf(successor.J.TARGETS["e8nm-p32009"], 7, {"path": "basis.json"})
    if dimension != 2514 or source != "base_dimension of the column basis record":
        raise AssertionError((dimension, source))
    with pytest.raises(ValueError, match="no radical Hilbert function"):
        successor.radical_hf(successor.J.TARGETS["e8nm-p32009"], 7, {})
    basis.write_text(json.dumps({"base_dimension": 2514}))
    with pytest.raises(ValueError, match="differs from RADICAL_HF"):
        successor.radical_hf(successor.J.TARGETS["e8nm-p32009"], 6, {"path": "basis.json"})


def test_stall_requires_consecutive_zero_gains_after_a_predecessor() -> None:
    """An early or interrupted plateau must not satisfy the declared consecutive-step criterion."""
    if successor.stalled([{"rank": 3}, {"rank": 3}], 2):
        raise AssertionError("missing predecessor admitted")
    if not successor.stalled([{"rank": 1}, {"rank": 3}, {"rank": 3}, {"rank": 3}], 2):
        raise AssertionError("two zero gains omitted")
    if successor.stalled([{"rank": 3}, {"rank": 3}, {"rank": 4}], 2):
        raise AssertionError("positive gain admitted")
    if successor.stalled([{"rank": 3}, {"rank": 3}], None):
        raise AssertionError("disabled stall admitted")


def _synthetic_slice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two degree-seven columns evaluate to (1+3s)^7 and 5^7 on an exact affine slice."""
    old = successor.J
    prime = 32009
    first = (7,) + (0,) * (old.A.NGEN - 1)
    second = (0, 7) + (0,) * (old.A.NGEN - 2)
    origin = (0,) * old.A.NVAR
    t1 = (1,) + origin[1:]
    t2 = (0, 1) + origin[2:]
    generators: list[dict[tuple[int, ...], int]] = [{t1: 1}, {t2: 1}] + [{} for _ in range(old.A.NGEN - 2)]
    monkeypatch.setattr(old, "slice_ideals", lambda _name: ([], generators, []))
    monkeypatch.setattr(old, "columns", lambda _target, _degree: ([first, second], {}))
    monkeypatch.setattr(old, "k2_hilbert_function", lambda _target: {"7": 3})
    monkeypatch.setattr(successor, "radical_hf", lambda _target, _degree, _source: (2, "synthetic affine slice"))

    def arc(_target: Any, _index: int) -> list[Any]:
        zero = old.Lm.L([], 0, old.TOP, prime)
        return [
            old.Lm.L.mono(1, 2, old.TOP, prime) + old.Lm.L.mono(3, 3, old.TOP, prime),
            old.Lm.L.mono(5, 2, old.TOP, prime),
        ] + [zero for _ in range(old.A.NVAR - 2)]

    monkeypatch.setattr(old, "arc", arc)


def test_stall_retains_a_lower_bound_and_check_rejects_mutated_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The synthetic rank is 2: a stalled campaign cannot claim the prescribed upper bound 3."""
    _synthetic_slice(monkeypatch)
    path = tmp_path / "record.json"
    record = successor.compute("e8nm-p32009", 7, 8, 1, path, 2)
    if (record["rank"], record["status"], len(record["arcs"]), record["bound"]) != (
        2,
        "stalled_below_k2_bound",
        3,
        "2 <= h_7 <= 3",
    ):
        raise AssertionError(record)
    monkeypatch.setattr(sys, "argv", ["jet_rank_v2.py", "--check", str(path)])
    successor.main()
    record["checkpoints"][1]["rank"] = 1
    path.write_text(json.dumps(record))
    with pytest.raises(SystemExit, match="recomputed record differs"):
        successor.main()
    capsys.readouterr()


def test_successor_control_detects_an_altered_v1_arc(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A control that compares only final ranks would admit altered arc coefficients."""
    _synthetic_slice(monkeypatch)
    record = successor.compute("e8nm-p32009", 7, 1, 1, None)
    record["schema"] = successor.J.SCHEMA
    record["inputs"].pop(successor.J.relative(Path(successor.__file__)))
    path = tmp_path / "v1.json"
    path.write_text(json.dumps(record))
    if successor.control(path)["control"] != "identical":
        raise AssertionError("valid v1 control failed")
    record["arcs"][0]["coefficients"]["w"][0] += 1
    path.write_text(json.dumps(record))
    with pytest.raises(SystemExit, match="arcs"):
        successor.control(path)


@pytest.mark.parametrize(
    "upper,failed_check,expected",
    [(2, "", "equal_to_k2_bound"), (1, "", "inconsistent"), (3, "j", "inconsistent"), (3, "k2", "inconsistent")],
)
def test_successor_stops_on_the_bound_and_rejects_failed_premises(
    upper: int, failed_check: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dropping a failed-J/K2 guard or weakening the stopping comparison corrupts terminal evidence."""
    _synthetic_slice(monkeypatch)
    old = successor.J
    monkeypatch.setattr(old, "k2_hilbert_function", lambda _target: {"7": upper})
    _, generators, _ = old.slice_ideals("e8nm-p32009")
    if failed_check == "j":
        monkeypatch.setattr(old, "slice_ideals", lambda _name: ([generators[0]], generators, []))
    elif failed_check == "k2":
        polynomial = {(1,) + (0,) * (old.A.NGEN - 1): 1}
        monkeypatch.setattr(old, "slice_ideals", lambda _name: ([], generators, [polynomial]))
    record = successor.compute("e8nm-p32009", 7, 3, 1, None)
    if record["rank"] != 2 or record["status"] != expected:
        raise AssertionError(record)
    if upper <= 2 and len(record["arcs"]) != 1:
        raise AssertionError("bound reached without stopping")
    if failed_check and record["arcs_with_failed_check"] != [0, 1, 2]:
        raise AssertionError(record["arcs_with_failed_check"])
