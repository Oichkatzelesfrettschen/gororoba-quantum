"""Bind the compilation-only backend to the snapshot Target without Aer channel construction."""

from __future__ import annotations

import json
from unittest.mock import patch

import n21_conjugation_noise as replay


def main() -> None:
    record = json.loads((replay.ROOT / "docs/evidence/linear_conjugation/noise.json").read_text())
    for retained in record["backends"]:
        snapshot = json.loads((replay.ROOT / retained["snapshot"]).read_text())
        expected, _ = replay.calibration_snapshot.noise_model(snapshot)
        with patch.object(replay.calibration_snapshot, "noise_model", side_effect=RuntimeError("unused Aer channels")):
            actual = replay._backend(snapshot)
        for name in expected.target.operation_names:
            if replay.calibration_snapshot._entries(actual.target, name) != replay.calibration_snapshot._entries(
                expected.target, name
            ):
                raise RuntimeError(f"{retained['backend']}: Target instruction {name} differs")
        if set(actual.target.operation_names) != set(expected.target.operation_names) | {"if_else"}:
            raise RuntimeError("compilation Target operations differ")
        for field in ("num_qubits", "dt"):
            if getattr(actual.target, field) != getattr(expected.target, field):
                raise RuntimeError(f"compilation Target {field} differs")
        attributes = ("t1", "t2", "frequency")
        actual_qubits = [tuple(getattr(qubit, name) for name in attributes) for qubit in actual.target.qubit_properties]
        expected_qubits = [
            tuple(getattr(qubit, name) for name in attributes) for qubit in expected.target.qubit_properties
        ]
        if actual_qubits != expected_qubits:
            raise RuntimeError("compilation Target qubit properties differ")
        if actual.name != expected.name:
            raise RuntimeError("compilation backend name differs")
    print("conjugation compiler: all three snapshot Targets agree; compilation skips Aer channels")


if __name__ == "__main__":
    main()
