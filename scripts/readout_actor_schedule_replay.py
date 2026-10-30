"""Replay actor measurement timing against a restricted historical Target.

The replay uses retained x and measure durations and a synthetic delay
instruction. It makes no provider request and admits no acquisition.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import qiskit
from qiskit import transpile
from qiskit.circuit import Delay, Measure, Parameter
from qiskit.circuit.library import XGate
from qiskit.transpiler import InstructionProperties, Target

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from readout_information_circuits import actor_alternatives, padded_actor_alternatives  # noqa: E402

from parallel import ordered_map  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"


def _scheduled_row(task: tuple[dict[str, Any], bool, str, str, int]) -> dict[str, Any]:
    backend, padded, method, arm, input_bits = task
    width = backend["num_qubits"]
    dt = backend["dt"]
    if type(width) is not int or width != 156 or not isinstance(dt, int | float) or not math.isfinite(dt) or dt <= 0:
        raise ValueError("historical Kingston snapshot must contain 156 qubits and a positive dt")
    target = Target(num_qubits=width, dt=dt)
    durations: dict[str, list[float]] = {}
    for name, instruction in (("x", XGate()), ("measure", Measure())):
        entries = backend["instructions"][name]
        if entries["qargs"] != [[index] for index in range(width)] or len(entries["duration"]) != width:
            raise ValueError(f"snapshot {name} loci or durations are incomplete")
        values = entries["duration"]
        if any(not isinstance(value, int | float) or not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError(f"snapshot {name} duration is invalid")
        durations[name] = values
        target.add_instruction(
            instruction, {(index,): InstructionProperties(duration=value) for index, value in enumerate(values)}
        )
    target.add_instruction(Delay(Parameter("duration"), unit="dt"), {(index,): None for index in range(width)})
    ticks = tuple(round(value / dt) for value in durations["x"])
    if any(abs(value / dt - tick) > 1e-9 or tick <= 0 for value, tick in zip(durations["x"], ticks, strict=True)):
        raise ValueError("snapshot X duration does not align with dt")
    alternatives = (
        padded_actor_alternatives(width, (0, 1), (2,), ticks) if padded else actor_alternatives(width, (0, 1), (2,))
    )
    compiled = transpile(
        alternatives[(arm, input_bits)],
        target=target,
        initial_layout=list(range(width)),
        optimization_level=0,
        scheduling_method=method,
    )
    measured = [
        (
            compiled.find_bit(item.qubits[0]).index,
            compiled.find_bit(item.clbits[0]).index,
            compiled.op_start_times[index],
        )
        for index, item in enumerate(compiled.data)
        if item.operation.name == "measure"
    ]
    if [(qubit, classical) for qubit, classical, _start in measured] != [(index, index) for index in range(width)]:
        raise ValueError("compiled measurement mapping differs from the identity register")
    compiled_x = sorted(compiled.find_bit(item.qubits[0]).index for item in compiled.data if item.operation.name == "x")
    expected_x = [bit for bit in (0, 1) if input_bits & (1 << bit)]
    if arm == "active":
        expected_x.append(2)
    if compiled_x != expected_x:
        raise ValueError("compiled X preparations differ from the selected reporter and actor arms")
    return {
        "padded": padded,
        "method": method,
        "arm": arm,
        "input": input_bits,
        "measurement_count": len(measured),
        "measurement_start_ticks": sorted({start for _qubit, _classical, start in measured}),
        "compiled_x_qubits": compiled_x,
    }


def replay_retained_snapshot() -> dict[str, Any]:
    """Report restricted-Target schedules for all eight candidate preparations."""
    source = SNAPSHOT.read_bytes()
    backend = json.loads(source)["backends"]["ibm_kingston"]
    tasks = [
        (backend, padded, method, arm, input_bits)
        for padded in (False, True)
        for method in ("asap", "alap")
        for arm in ("idle", "active")
        for input_bits in range(4)
    ]
    return {
        "schema": "readout-actor-historical-schedule-v1",
        "target_scope": "restricted historical snapshot: x, measure and delay",
        "snapshot_sha256": hashlib.sha256(source).hexdigest(),
        "replay_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "constructor_sha256": hashlib.sha256(
            (ROOT / "scripts/readout_information_circuits.py").read_bytes()
        ).hexdigest(),
        "snapshot_calibration": backend["calibration"],
        "qiskit_version": qiskit.__version__,
        "dt_seconds": backend["dt"],
        "schedules": ordered_map(_scheduled_row, tasks),
        "boundary": (
            "Offline scheduling only; live Target, served pulses, ordering, billing and admission are unverified."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(replay_retained_snapshot(), indent=2, sort_keys=True))
