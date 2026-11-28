"""Mechanical admission check of a pathion_kernel_map_orientation_merged plan, the --check of scripts/approved_run.sh.

Successor of scripts/pathion_kernel_map_orientation_check.py, whose approved constants stay. The merged case
(docs/design/pathion-kernel-map-orientation-merged.md) admits a fresh plan only when the group places on ibm_kingston at
replica floor 0.5, both arms of every unit route to one CZ count, the moved, exchanged and swap members of each operand
route within 20 percent of that operand's control, at least MIN_REGIONS disjoint regions are placed, no region touches
the excluded qubits, the estimated charge stays within CEILING_SECONDS, and the compiled xtwin member of each
operand and arm keeps the non-rz gate sequence of its control (the statistic D = control minus exchange cancels
errors that act before the frame only on equal sequences). The arm, exclusion and charge rules are those of
scripts/pathion_kernel_map_check.py; the ratio rule is that of the retained orientation check.

CEILING_SECONDS is 1.5 times the model charge of the design (11.2 s at 11 regions): the retained case set its 18 s
ceiling at 1.5 times its 12.0 s expected charge.

Usage: RUN=DRY_RUN_DIR "$PYTHON" scripts/pathion_kernel_map_orientation_merged_check.py [MIN_REGIONS [CEILING_SECONDS]]
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType

from qiskit import qpy

GROUP = "pathion_kernel_map_orientation_merged"
BACKEND = "ibm_kingston"
REPLICA_FLOOR = 0.5
MIN_REGIONS = 11
CEILING_SECONDS = 16.8


def _load(name: str) -> ModuleType:
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_sequence_failures(sequences: dict[str, list]) -> list[str]:
    """Members of an xtwin role whose non-rz gate sequence differs from, or lacks, its control's."""
    found: list[str] = []
    for name in sorted(sequences):
        if not name.startswith("kmo_ctrl_"):
            continue
        twin = "kmo_xtwin_" + name[len("kmo_ctrl_") :]
        if twin not in sequences:
            found.append(f"{twin}: missing from the compiled plan")
        elif sequences[twin] != sequences[name]:
            found.append(f"{twin}: non-rz gate sequence differs from {name}")
    if not any(name.startswith("kmo_ctrl_") for name in sequences):
        found.append("no control member in the compiled plan")
    return found


def non_rz_sequences(record: dict, run: Path) -> dict[str, list]:
    """The non-rz gate sequence of each member's packed circuit, read from the archive that isa.qpy.sha256 names.

    The archive lies in results/live/archives beside the run directory. A PUB holds one member; the isolated reference
    of the control is no member of the comparison.
    """
    digest = (run / "isa.qpy.sha256").read_text().strip()
    with (run.parent / "archives" / f"{digest}.qpy").open("rb") as handle:
        circuits = {circuit.name: circuit for circuit in qpy.load(handle)}
    sequences: dict[str, list] = {}
    for pub in record["execution_pubs"]:
        members = [c["member"] for c in pub["components"] if c["group"] == GROUP]
        if len(members) != 1 or members[0].endswith("_isolated"):
            continue
        circuit = circuits[pub["name"]]
        sequences[members[0]] = [
            (op.operation.name, tuple(circuit.find_bit(q).index for q in op.qubits))
            for op in circuit.data
            if op.operation.name != "rz"
        ]
    return sequences


def failures(record: dict, min_regions: int, ceiling: float, run: Path | None = None) -> list[str]:
    base = _load("pathion_kernel_map_check")
    for attr, value in (("GROUP", GROUP), ("MIN_REPLICAS", min_regions), ("CEILING_SECONDS", ceiling)):
        setattr(base, attr, value)
    found: list[str] = list(base.failures(record))
    groups = [g for g in record["groups"] if g["group"] == GROUP]
    if len(groups) == 1:
        group = groups[0]
        if group["backend"] != BACKEND:
            found.append(f"placed on {group['backend']}, not {BACKEND}")
        if group.get("replica_floor") != REPLICA_FLOOR:
            found.append(f"replica floor {group.get('replica_floor')}, not {REPLICA_FLOOR}")
        found += _load("pathion_kernel_map_orientation_check").ratio_failures(group["members"])
        if run is not None:
            try:
                found += gate_sequence_failures(non_rz_sequences(record, run))
            except (OSError, KeyError, ValueError) as error:
                found.append(f"compiled plan unreadable: {type(error).__name__}: {error}")
    return found


def main() -> int:
    min_regions = int(sys.argv[1]) if len(sys.argv) > 1 else MIN_REGIONS
    ceiling = float(sys.argv[2]) if len(sys.argv) > 2 else CEILING_SECONDS
    record = json.loads((Path(os.environ["RUN"]) / "record.json").read_text())
    found = failures(record, min_regions, ceiling, Path(os.environ["RUN"]))
    for line in found:
        print(f"{GROUP} check: {line}", file=sys.stderr)
    if not found:
        print(f"{GROUP} check: plan admitted")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
