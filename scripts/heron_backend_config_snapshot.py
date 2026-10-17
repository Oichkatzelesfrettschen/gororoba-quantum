"""Snapshot of the backend configuration fields the Heron r2 readout note cites.

--out FILE (local, network) reads ibm_fez, ibm_kingston and ibm_marrakesh through
QiskitRuntimeService, read-only, and writes each backend's name, backend_version,
processor_type, the sorted key names of configuration().to_dict() and the
subset of those keys whose value is None, the public attributes of
target.qubit_properties with their non-None counts, and the per-qubit parameter
names of properties() with the count of qubits carrying each name and each
non-None value. Names and counts only; no calibration value, credential,
instance or account identifier enters the file.

--check FILE (CI, offline) requires the roster, the Heron r2 processor type,
the absence of hamiltonian, meas_lo_range, qubit_lo_range and rep_times, the presence of
the repetition-delay and measurement-map fields, meas_kernels and meas_levels
among the keys whose value is None, zero frequency and anharmonicity in both
target.qubit_properties and properties(), the note quoting each properties()
parameter name, and requires
docs/notes/ibm_quantum/heron-r2-readout-resonator.md to quote each retained
backend_version and to name the snapshot file.

Usage: "$PYTHON" scripts/heron_backend_config_snapshot.py (--out FILE | --check FILE)
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
PROCESSOR_TYPE = {"family": "Heron", "revision": "2"}
ABSENT = ("hamiltonian", "meas_lo_range", "qubit_lo_range", "rep_times")
PRESENT = ("default_rep_delay", "rep_delay_range", "meas_map", "meas_kernels", "meas_levels")
NONE_VALUED = ("meas_kernels", "meas_levels")
NOT_EXPOSED = ("frequency", "anharmonicity")
NOTE = Path("docs/notes/ibm_quantum/heron-r2-readout-resonator.md")
SNAPSHOT = "docs/evidence/heron_platform/backend_configuration.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def inventory(backend: Any) -> dict[str, Any]:
    """Names and counts of the qubit parameters a backend exposes; no values."""
    qubit_properties = backend.target.qubit_properties
    target: dict[str, Any] = {"present": qubit_properties is not None, "qubits": 0, "attribute_non_none_counts": {}}
    if qubit_properties:
        attributes = sorted(a for a in dir(qubit_properties[0]) if not a.startswith("_"))
        target["qubits"] = len(qubit_properties)
        target["attribute_non_none_counts"] = {
            a: sum(1 for q in qubit_properties if getattr(q, a, None) is not None) for a in attributes
        }
    present: dict[str, int] = {}
    non_none: dict[str, int] = {}
    for items in backend.properties().qubits:
        for item in items:
            present[item.name] = present.get(item.name, 0) + 1
            if item.value is not None:
                non_none[item.name] = non_none.get(item.name, 0) + 1
    return {
        "target_qubit_properties": target,
        "properties_qubit_parameters": {
            "names": sorted(present),
            "qubits_with_name": dict(sorted(present.items())),
            "qubits_with_non_none_value": dict(sorted(non_none.items())),
        },
    }


def snapshot() -> dict[str, Any]:
    import qiskit_ibm_runtime
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    backends = {}
    for name in ROSTER:
        backend = service.backend(name)
        config = backend.configuration().to_dict()
        backends[name] = {
            "backend_version": str(backend.backend_version),
            "processor_type": dict(backend.processor_type),
            "configuration_keys": sorted(config),
            "configuration_keys_with_none": sorted(k for k, v in config.items() if v is None),
            **inventory(backend),
        }
    return {
        "retrieved": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
        "versions": {"qiskit-ibm-runtime": qiskit_ibm_runtime.__version__},
        "backends": backends,
    }


def check(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    backends = data["backends"]
    require(tuple(sorted(backends)) == tuple(sorted(ROSTER)), f"roster {sorted(backends)} differs from {ROSTER}")
    note = NOTE.read_text(encoding="utf-8")
    require(SNAPSHOT in note, f"{NOTE} does not name {SNAPSHOT}")
    for name in ROSTER:
        entry = backends[name]
        require(entry["processor_type"] == PROCESSOR_TYPE, f"{name} processor_type {entry['processor_type']}")
        keys = entry["configuration_keys"]
        require(keys == sorted(keys), f"{name} keys unsorted")
        for field in ABSENT:
            require(field not in keys, f"{name} exposes {field}")
        for field in PRESENT:
            require(field in keys, f"{name} lacks {field}")
        nones = entry["configuration_keys_with_none"]
        for field in NONE_VALUED:
            require(field in nones, f"{name} {field} is not None-valued")
        target = entry["target_qubit_properties"]["attribute_non_none_counts"]
        parameters = entry["properties_qubit_parameters"]
        for field in NOT_EXPOSED:
            require(target.get(field, 0) == 0, f"{name} target.qubit_properties carries {field}")
            require(field not in parameters["names"], f"{name} properties() exposes {field}")
            require(parameters["qubits_with_non_none_value"].get(field, 0) == 0, f"{name} {field} has values")
        for parameter in parameters["names"]:
            require(parameter in note, f"{NOTE} does not name properties() parameter {parameter}")
        version = entry["backend_version"]
        quoted = re.search(rf"{re.escape(name)}\W+(?:backend_version\s+)?{re.escape(version)}(?![\w.])", note)
        require(quoted is not None, f"{NOTE} does not quote {name} backend_version {version}")
    for field in ABSENT:
        require(field in note, f"{NOTE} does not name {field}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="read the live configurations and write the snapshot")
    mode.add_argument("--check", type=Path, help="verify a retained snapshot against the note")
    args = parser.parse_args(argv)
    if args.out:
        args.out.write_text(json.dumps(snapshot(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        check(args.out)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
