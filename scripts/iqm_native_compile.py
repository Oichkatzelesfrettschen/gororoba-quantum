"""Compile a retained IQM case offline with the native IQM transpiler and compare it with the case's own bytes.

The case circuits already carry native instructions (prx, cz, measure) on physical qubits. The tool reads them
back into Qiskit circuits, runs iqm.qiskit_iqm transpile_to_IQM against the dynamic quantum architecture that the case
retained (calibration/dynamic-quantum-architecture.json, so no network and no account), serializes the result and
counts native gates and MOVE gates per circuit. The comparison measures what the native transpiler's single-qubit
optimization would change in bytes our case builders produced. It never replaces the retained circuits: a case keeps
its digest-bound bytes, and a native-compiled variant would be a new case.

Usage:
    "$PYTHON" scripts/iqm_native_compile.py CASE_DIR [--out FILE] [--optimization-level N]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def native_counts(instructions: list[dict[str, Any]]) -> dict[str, int]:
    """Instruction counts by name; a measure of k qubits counts k, as the native transpiler serializes one per qubit."""
    counts: Counter[str] = Counter()
    for inst in instructions:
        counts[str(inst["name"])] += len(inst["locus"]) if inst["name"] == "measure" else 1
    return {name: int(n) for name, n in sorted(counts.items())}


def expand_measures(instructions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The circuit with its measure instructions split per qubit under keys of the form creg_len_index_clbit.

    The case writes one measure key (m) for all measured qubits, in locus order; the Qiskit bridge reads a key as
    register name, register length, register index and bit index, so the m register gets one bit per measured qubit
    in that order.
    """
    width = sum(len(i["locus"]) for i in instructions if i["name"] == "measure")
    out: list[dict[str, Any]] = []
    bit = 0
    for inst in instructions:
        if inst["name"] != "measure":
            out.append(inst)
            continue
        for qubit in inst["locus"]:
            out.append({"name": "measure", "locus": [qubit], "args": {"key": f"m_{width}_0_{bit}"}})
            bit += 1
    return out


def offline_backend(architecture: dict[str, Any]) -> Any:
    """An IQMBackendBase over the retained dynamic architecture; it compiles and refuses to run."""
    from iqm.iqm_client import DynamicQuantumArchitecture
    from iqm.qiskit_iqm.iqm_backend import IQMBackendBase
    from qiskit.providers import Options

    class OfflineBackend(IQMBackendBase):
        @classmethod
        def _default_options(cls) -> Options:
            return Options(shots=1)

        @property
        def max_circuits(self) -> None:
            return None

        def run(self, run_input: Any, **options: Any) -> Any:
            raise NotImplementedError("the offline backend compiles only")

    return OfflineBackend(DynamicQuantumArchitecture.model_validate(architecture), name="offline")


def compile_circuit(circuit: dict[str, Any], backend: Any, optimization_level: int) -> dict[str, Any]:
    from iqm.pulse import CircuitOperation
    from iqm.qiskit_iqm.iqm_naive_move_pass import transpile_to_IQM
    from iqm.qiskit_iqm.qiskit_to_iqm import deserialize_instructions, serialize_instructions
    from qiskit import QuantumRegister
    from qiskit.transpiler import Layout

    operations = [
        CircuitOperation(name=i["name"], locus=tuple(i["locus"]), args=i["args"])
        for i in expand_measures(circuit["instructions"])
    ]
    names = {name: backend.qubit_name_to_index(name) for name in backend.architecture.qubits}
    layout = Layout.generate_trivial_layout(QuantumRegister(len(backend.architecture.qubits), "q"))
    logical = deserialize_instructions(operations, names, layout)
    compiled = transpile_to_IQM(logical, backend, optimization_level=optimization_level)
    serialized = serialize_instructions(compiled, {names[name]: name for name in names})
    before = native_counts(circuit["instructions"])
    after = native_counts([{"name": i.name, "locus": i.locus} for i in serialized])
    return {"before": before, "after": after, "moves": after.get("move", 0)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("case", type=Path)
    parser.add_argument("--optimization-level", type=int, default=1)
    parser.add_argument("--limit", type=int, help="compile only the first N circuits")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    cases = json.loads((args.case / "cases.json").read_text(encoding="utf-8"))
    architecture = json.loads((args.case / "calibration/dynamic-quantum-architecture.json").read_text(encoding="utf-8"))
    backend = offline_backend(architecture)
    rows: dict[str, Any] = {}
    for job in cases["jobs"]:
        for entry in job["circuits"][: args.limit]:
            circuit = json.loads((args.case / entry["file"]).read_text(encoding="utf-8"))
            rows[circuit["name"]] = compile_circuit(circuit, backend, args.optimization_level)
    totals: dict[str, Counter[str]] = {"before": Counter(), "after": Counter()}
    for row in rows.values():
        for arm in totals:
            totals[arm].update(row[arm])
    report = {
        "case": cases["case"],
        "calibration_set_id": architecture["calibration_set_id"],
        "optimization_level": args.optimization_level,
        "circuits": len(rows),
        "totals": {arm: dict(sorted(c.items())) for arm, c in totals.items()},
        "per_circuit": rows,
    }
    print(json.dumps({k: v for k, v in report.items() if k != "per_circuit"}, indent=2, sort_keys=True))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
