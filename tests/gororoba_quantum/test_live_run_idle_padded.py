"""Idle-padded predictions: ALAP delays per replica, recorded beside the unpadded law and outside the approval."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Measure
from qiskit.circuit.library import CZGate, SXGate
from qiskit.transpiler import InstructionProperties, Target

import live_run


def _target() -> Target:
    target = Target(num_qubits=3, dt=4e-9)
    target.add_instruction(SXGate(), {(q,): InstructionProperties(duration=32e-9) for q in range(3)})
    target.add_instruction(CZGate(), {pair: InstructionProperties(duration=68e-9) for pair in ((0, 1), (1, 2))})
    target.add_instruction(Measure(), {(q,): InstructionProperties(duration=400e-9) for q in range(3)})
    return target


def _choice(replica: QuantumCircuit) -> live_run.Choice:
    entry = live_run.Entry(
        name="member",
        base=replica,
        ideal=np.zeros(2**replica.num_clbits),
        packed=replica,
        replicas=[replica],
        prefixes=[""],
        replica_qubits=[[0, 1, 2]],
    )
    snap = SimpleNamespace(backend=SimpleNamespace(target=_target()))
    return live_run.Choice(
        group=SimpleNamespace(name="group"),  # type: ignore[arg-type]
        snap=snap,  # type: ignore[arg-type]
        seed=0,
        layout=[0, 1, 2],
        isas=[replica],
        member_scores=[0.0],
        joint_score=0.0,
        entries=[entry],
    )


def test_idle_padded_choice_writes_alap_waits_and_leaves_the_choice_unchanged() -> None:
    replica = QuantumCircuit(3)
    replica.sx(0)
    replica.sx(1)
    replica.cz(1, 2)
    replica.cz(1, 2)
    replica.cz(0, 1)
    choice = _choice(replica)
    padded, idle = live_run.idle_padded_choice(choice)
    # ASAP plays qubit 0's sx at 0 and leaves it waiting 34 dt for the CZ chain on 1 and 2; ALAP moves the sx to
    # end where cz(0, 1) starts, so the planner's placement inserts no wait.
    _, early = live_run.idle_padding.pad(replica, live_run.idle_padding.target_duration(_target()))
    if early != {0: 34} or idle != {"member": [{"placement": "alap", "inserted_dt": {}}]}:
        raise AssertionError(f"asap {early}, planner idle {idle}")
    if choice.entries[0].replicas[0] is not replica or padded.entries[0].replicas[0] is replica:
        raise AssertionError("padding replaced the input choice's replica or skipped the copy")


def test_idle_padded_choice_names_a_replica_the_target_cannot_time() -> None:
    replica = QuantumCircuit(3, 3)
    replica.x(0)
    replica.sx(0)
    _, idle = live_run.idle_padded_choice(_choice(replica))
    if "refused" not in idle["member"][0]:
        raise AssertionError(f"an untimed instruction was padded: {idle}")


def test_approved_structure_ignores_the_idle_padded_prediction() -> None:
    replica = {"physical_qubits": [0, 1], "noisy": "x", "tvd_noisy_to_ideal": 0.1, "idle_padded": {"noisy": "y"}}
    group = {"group": "g", "members": [{"name": "m", "replicas": [replica]}]}
    projected = live_run._approved_structure(group)
    if projected["members"][0]["replicas"] != [{"physical_qubits": [0, 1]}]:
        raise AssertionError(f"projection kept prediction fields: {projected['members'][0]['replicas']}")
