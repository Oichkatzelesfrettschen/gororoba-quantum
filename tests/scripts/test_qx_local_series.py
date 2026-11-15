"""Contracts of the seeded local qxelarator control: circuit seeds, the manifest record and the seed range.

qxelarator is absent from the hosted environment, so a stand-in module records the arguments of each
execute_string call and returns a histogram that depends on the seed alone. The stand-in carries the one
behavior the contracts rely on, measured with qxelarator 0.10.0: equal seeds return equal counts.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any

import pytest
import qi_mcp_server
import qx_local_series as qls
from mcp.server.mcpserver.exceptions import ToolError

import parallel

DRAW = "qrng:docs/evidence/anu_qrng/draw-2026-11-15T163052Z.json#0"
SHOTS = 8
CIRCUITS = ("a.cq", "b.cq", "c.cq")
PROGRAM = "version 3.0\nqubit[1] q\nbit[1] b\nb = measure q\n"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class StandIn(types.ModuleType):
    """execute_string keyed by seed (an unseeded call varies from call to call), recording every call."""

    class SimulationError:
        pass

    def __init__(self) -> None:
        super().__init__("qxelarator")
        self.calls: list[dict[str, Any]] = []

    def execute_string(self, text: str, iterations: int, **kwargs: Any) -> Any:
        self.calls.append({"text": text, "iterations": iterations, **kwargs})
        seed = kwargs.get("seed")
        ones = (len(self.calls) if seed is None else seed) % iterations  # an unseeded call varies with each call
        results = {"0": iterations - ones, "1": ones} if ones else {"0": iterations}
        return types.SimpleNamespace(shots_done=iterations, results=results)


@pytest.fixture
def qx(monkeypatch: pytest.MonkeyPatch) -> StandIn:
    module = StandIn()
    monkeypatch.setitem(sys.modules, "qxelarator", module)
    monkeypatch.setattr(qls, "version", lambda name: "0.10.0")
    monkeypatch.setattr(parallel, "ordered_map", lambda function, items, **_: [function(item) for item in items])
    return module


def _case(root: Path, names: tuple[str, ...] = CIRCUITS) -> Path:
    batch = root / "case" / "batch-00"
    batch.mkdir(parents=True, exist_ok=True)
    for name in names:
        (batch / name).write_text(PROGRAM, encoding="utf-8")
    # the case's own generation seed, a value the run must leave alone (len keeps it out of the seed ledger's literals)
    manifest = {"seed": len(CIRCUITS), "circuits": [{"file": name} for name in names]}
    (batch / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root / "case"


def _run(root: Path, out: str) -> Path:
    target = root / out
    status = qls.main([str(_case(root)), str(target), str(SHOTS), "--seed", DRAW])
    _expect(status == 0, f"main returned {status}")
    return target / "batch-00"


def test_circuit_seeds_differ_by_circuit_and_stay_below_two_to_the_31() -> None:
    seeds = [qls.circuit_seed(7, "batch-00", name) for name in CIRCUITS]
    _expect(len(set(seeds)) == len(CIRCUITS), f"circuits of one batch share a seed: {seeds}")
    _expect(all(0 <= seed < 2**31 for seed in seeds), f"a circuit seed leaves 0..2**31 - 1: {seeds}")
    _expect(qls.circuit_seed(7, "batch-00", "a.cq") == seeds[0], "the same place gives another seed")
    _expect(qls.circuit_seed(8, "batch-00", "a.cq") != seeds[0], "the run seed does not reach the circuit seed")
    _expect(qls.circuit_seed(7, "batch-01", "a.cq") != seeds[0], "the batch does not reach the circuit seed")


def test_every_circuit_runs_with_its_recorded_seed(qx: StandIn, tmp_path: Path) -> None:
    run = _run(tmp_path, "run")
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    _expect(manifest["seed"] == len(CIRCUITS), f"the case manifest's own seed became {manifest['seed']!r}")
    _expect(manifest["seed_source"]["sources"] == [DRAW], f"seed source {manifest['seed_source']['sources']}")
    _expect(manifest["seed_source"]["flag"] == "--seed", f"seed flag {manifest['seed_source']['flag']}")
    _expect(sorted(manifest["circuit_seeds"]) == sorted(CIRCUITS), "circuit_seeds does not name every circuit")
    called = [call["seed"] for call in qx.calls]
    _expect(called == [manifest["circuit_seeds"][name] for name in CIRCUITS], f"recorded seeds differ from {called}")
    _expect(all(call["iterations"] == SHOTS for call in qx.calls), "a circuit ran at another shot count")


def test_a_second_run_with_the_same_draw_value_returns_the_same_shots(qx: StandIn, tmp_path: Path) -> None:
    first, second = _run(tmp_path, "run1"), _run(tmp_path, "run2")
    for name in CIRCUITS:
        same = (first / "raw" / f"{name}.json").read_bytes() == (second / "raw" / f"{name}.json").read_bytes()
        _expect(same, f"the replay of {name} differs")


# Measured with sha256 over "518|batch-00|NAME": these two names derive 1158210912 under the 31-bit map.
COLLIDING = ("c8869.cq", "c71149.cq")


def test_circuits_whose_derived_seeds_collide_are_refused_before_anything_runs(qx: StandIn, tmp_path: Path) -> None:
    seeds = [qls.circuit_seed(518, "batch-00", name) for name in COLLIDING]
    _expect(seeds[0] == seeds[1], f"the fixture pair no longer collides: {seeds}")
    case = _case(tmp_path, COLLIDING)
    with pytest.raises(SystemExit, match="derive the same circuit seed"):
        qls.main([str(case), str(tmp_path / "out"), str(SHOTS), "--seed", DRAW])
    _expect(qx.calls == [], "a refused series still reached qxelarator")
    _expect(not (tmp_path / "out").exists(), "a refused series still wrote a run directory")


def test_a_circuit_file_listed_twice_is_refused(qx: StandIn, tmp_path: Path) -> None:
    case = _case(tmp_path, ("a.cq", "a.cq"))
    with pytest.raises(SystemExit, match="listed twice"):
        qls.main([str(case), str(tmp_path / "out"), str(SHOTS), "--seed", DRAW])
    _expect(qx.calls == [], "a refused series still reached qxelarator")


def test_a_bare_integer_seed_and_a_missing_seed_are_refused(qx: StandIn, tmp_path: Path) -> None:
    case = _case(tmp_path)
    for flags in (["--seed", "12345"], []):
        with pytest.raises(SystemExit):
            qls.main([str(case), str(tmp_path / "out"), str(SHOTS), *flags])
    _expect(qx.calls == [], "a refused run still reached qxelarator")


def test_qi_run_local_passes_a_seed_and_refuses_a_seed_that_is_not_an_integer_in_range(qx: StandIn) -> None:
    _expect(qi_mcp_server.qi_run_local(PROGRAM, shots=4, seed=518)["shots"] == 4, "a seeded run returned no shots")
    _expect(qx.calls[-1]["seed"] == 518, "the seed did not reach qxelarator")
    qi_mcp_server.qi_run_local(PROGRAM, shots=4)
    _expect("seed" not in qx.calls[-1], "an unseeded run passed a seed")
    calls = len(qx.calls)
    for bad in (-1, 2**31, 2**63, 2**64 - 1, 1.0, 1.5, True):
        with pytest.raises(ToolError, match="seed must be an integer"):
            qi_mcp_server.qi_run_local(PROGRAM, shots=4, seed=bad)
    _expect(len(qx.calls) == calls, "a refused seed still reached qxelarator")
