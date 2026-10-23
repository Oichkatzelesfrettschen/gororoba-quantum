"""Generate submission-free wide Pauli-response reference programs and schedules.

Only four-qubit cells are checked with a local statevector. Wide programs are
tensor compositions with disjoint cells, not wide simulations or admitted native
circuits. Physical maps come from the retained packing witnesses; a native
compiler must apply and verify those maps before execution approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import tempfile
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit, qasm2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel  # noqa: E402

SEED = 20261022
SENTINELS = (("kernel", "X"), ("bright", "X"), ("kernel", "Y"), ("bright", "Y"))


def prepare_cell(state: str) -> QuantumCircuit:
    circuit = QuantumCircuit(4)
    if state == "middle":
        return circuit
    if state not in ("kernel", "bright"):
        raise ValueError("unknown cell state")
    circuit.x(0)
    circuit.x(1)
    circuit.x(2)
    circuit.h(3)
    circuit.cx(3, 1)
    circuit.cx(3, 0)
    circuit.s(3)
    circuit.rz(-math.pi / 2 if state == "kernel" else math.pi / 2, 3)
    return circuit


def readout_cell(axis: str) -> QuantumCircuit:
    if axis not in ("X", "Y"):
        raise ValueError("quadrature must be X or Y")
    circuit = QuantumCircuit(4)
    circuit.sdg(0)
    circuit.h(0)
    circuit.h(1)
    if axis == "Y":
        circuit.sdg(3)
    circuit.h(3)
    return circuit


def score(label: int) -> float:
    if not (label >> 2) & 1:
        return 0.5
    parity = ((label >> 3) ^ (label >> 1) ^ label) & 1
    return float(parity)


def program(cells: int, dense: bool, reference: int | None = None) -> QuantumCircuit:
    if cells < len(SENTINELS):
        raise ValueError("four sentinel cells are required")
    width = 4 * cells
    circuit = QuantumCircuit(width, width)
    if reference is not None:
        if reference not in (0, 1):
            raise ValueError("reference must prepare zero or one")
        if reference:
            circuit.x(range(width))
    else:
        for cell in range(cells):
            state = SENTINELS[cell][0] if cell < 4 else ("kernel" if cell % 2 == 0 else "bright")
            if cell < 4 or dense:
                circuit.compose(prepare_cell(state), range(4 * cell, 4 * cell + 4), inplace=True)
        circuit.barrier()
        for cell in range(cells):
            axis = SENTINELS[cell][1] if cell < 4 else "Y"
            circuit.compose(readout_cell(axis), range(4 * cell, 4 * cell + 4), inplace=True)
    circuit.measure(range(width), range(width))
    return circuit


def schedule(backend: str) -> list[dict[str, Any]]:
    if backend.startswith("iqm:"):
        pairs, references = 16, True
    elif backend == "ionq:forte-1":
        pairs, references = 2, False
    elif backend == "rigetti:cepheus-1-108q":
        pairs, references = 8, True
    else:
        raise ValueError("backend has no current-balance design")
    generator = random.Random(SEED)
    rows: list[dict[str, Any]] = []
    if references:
        rows.extend({"kind": "reference", "reference": value} for value in (0, 1))
    for pair in range(pairs):
        first = bool(generator.getrandbits(1)) if pairs > 2 else bool(pair % 2)
        rows.extend({"kind": "science", "pair": pair, "dense": value} for value in (first, not first))
    if references:
        rows.extend({"kind": "reference", "reference": value} for value in (0, 1))
    return rows


def compile_reference(task: tuple[int, int, dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
    index, cells, row = task
    circuit = program(cells, row.get("dense", False), row.get("reference"))
    body = qasm2.dumps(circuit) + "\n"
    name = f"circuit-{index:03d}.qasm"
    return (
        name,
        body,
        {
            **row,
            "file": name,
            "sha256": hashlib.sha256(body.encode()).hexdigest(),
            "qubits": circuit.num_qubits,
            "measurement_bits": circuit.num_clbits,
            "operations": dict(circuit.count_ops()),
        },
    )


def propose(audit: Path, backend: str, out: Path) -> None:
    if out.exists():
        raise ValueError("proposal generation requires a new directory")
    source = audit / "packing.json"
    rows = json.loads(source.read_text())["rows"]
    row = next(row for row in rows if row["backend"] == backend)
    patches = row["patches"]
    cases = schedule(backend)
    compiled = parallel.ordered_map(compile_reference, [(i, len(patches), case) for i, case in enumerate(cases)])
    out.mkdir(parents=True)
    for name, body, _ in compiled:
        (out / name).write_text(body)
    shots = 100 if backend == "ionq:forte-1" else (3215 if backend.startswith("rigetti:") else 2000)
    physical_map = {
        str(4 * index + bit): patch["roles"]["q" + str(bit)] for index, patch in enumerate(patches) for bit in range(4)
    }
    record = {
        "schema": "packed-pauli-reference-proposal-v1",
        "backend": backend,
        "provider_execution_authorized": False,
        "native_compilation_admitted": False,
        "randomization_seed": SEED,
        "cells": len(patches),
        "sentinel_cells": 4,
        "physical_map_to_be_applied_by_native_compiler": physical_map,
        "shots_per_circuit": shots,
        "circuits": [case for _, _, case in compiled],
        "total_register_shots": shots * len(cases),
        "register_shots_are_independent_by_assumption_only": True,
        "packing_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "analysis_sha256": hashlib.sha256(
            Path(__file__).with_name("packed_pauli_analysis.py").read_bytes()
        ).hexdigest(),
        "audit_manifest_sha256": hashlib.sha256((audit / "index.json").read_bytes()).hexdigest(),
        "budget": {
            "maximum_planned_credits": 24 if backend.startswith("iqm:") else 20,
            "reserve_credits": 6 if backend.startswith("iqm:") else 5,
            "cost_admitted": False,
            "shared_open_quantum_balance_alternative": not backend.startswith("iqm:"),
        },
        "primary_scope": "randomized density intervention"
        if backend != "ionq:forte-1"
        else "descriptive ion qualification",
        "remaining_admission": [
            "native map and gate conformance",
            "execution ordering and timing",
            "cost bound or exact quotes",
            "result identity and raw joint outcomes",
            "analysis and review",
            "user approval",
        ],
    }
    (out / "proposal.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")


def check(audit: Path, backend: str, proposal: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="packed-pauli-replay-") as directory:
        replay = Path(directory) / "proposal"
        propose(audit, backend, replay)
        if (proposal / "proposal.json").read_bytes() != (replay / "proposal.json").read_bytes():
            raise ValueError("proposal identity, schedule or source closure differs from replay")
        expected = {path.name for path in replay.iterdir()}
        if {path.name for path in proposal.iterdir()} != expected:
            raise ValueError("proposal file set differs from replay")
        for name in expected:
            if (proposal / name).read_bytes() != (replay / name).read_bytes():
                raise ValueError(f"proposal circuit differs from replay: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("backend")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--out", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.out is not None:
        propose(args.audit, args.backend, args.out)
    else:
        check(args.audit, args.backend, args.check)


if __name__ == "__main__":
    main()
