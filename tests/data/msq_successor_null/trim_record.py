"""Write the successor null's test record: the fields `msq_successor_null_batch.build_setup` reads from a dry-run
record directory (including its `shots`), with its snapshot cut to the layout qubits' properties and sx gates.

    "$PYTHON" tests/data/msq_successor_null/trim_record.py results/live/RECORD tests/data/msq_successor_null/record
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CONFIGURATION = (
    "dt_seconds",
    "equilibrium_delay_dt",
    "layout_width",
    "measurement_delay_dt",
    "pattern_bits",
    "prereadout_delay_dt",
    "qubits",
    "settle_delay_dt",
    "t1_delays_dt",
)
QUBIT_PROPERTIES = ("T1", "T2", "prob_meas1_prep0", "prob_meas0_prep1", "readout_length")


def trim(source: Path, target: Path) -> str:
    """Write target/record.json and its snapshot from the record directory `source`; return the snapshot sha256."""
    record = json.loads((source / "record.json").read_text())
    digest = record["envelope"]["planning_snapshot_sha256"]
    properties = json.loads((source / "envelope-snapshots" / f"{digest}.json").read_text())["properties"]
    configuration = record["family_configuration"]
    layout = {int(q) for q in configuration["qubits"]}
    qubits: list[list[dict[str, Any]]] = [
        [item for item in entries if item["name"] in QUBIT_PROPERTIES] if index in layout else []
        for index, entries in enumerate(properties["qubits"])
    ]
    gates = [gate for gate in properties["gates"] if gate["gate"] == "sx" and gate["qubits"][0] in layout]
    data = json.dumps({"properties": {"qubits": qubits, "gates": gates}}, sort_keys=True, indent=1).encode() + b"\n"
    trimmed = hashlib.sha256(data).hexdigest()
    (target / "envelope-snapshots").mkdir(parents=True, exist_ok=True)
    (target / "envelope-snapshots" / f"{trimmed}.json").write_bytes(data)
    kept = {
        "family_configuration": {key: configuration[key] for key in CONFIGURATION},
        "groups": [{"backend": group["backend"]} for group in record["groups"]],
        "shots": record["shots"],
        "envelope": {"planning_snapshot_sha256": trimmed},
        "source": {"record": source.name, "planning_snapshot_sha256": digest},
    }
    (target / "record.json").write_text(json.dumps(kept, sort_keys=True, indent=1) + "\n")
    return trimmed


if __name__ == "__main__":
    print(trim(Path(sys.argv[1]), Path(sys.argv[2])))
