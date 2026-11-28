"""Mechanical admission check of a pathion_kernel_map_orientation_merged plan, the --check of scripts/approved_run.sh.

Successor of scripts/pathion_kernel_map_orientation_check.py, whose approved constants stay. The merged case
(docs/design/pathion-kernel-map-orientation-merged.md) admits a fresh plan only when the group places on ibm_kingston at
replica floor 0.5, both arms of every unit route to one CZ count, the moved, exchanged and swap members of each operand
route within 20 percent of that operand's control, at least MIN_REGIONS disjoint regions are placed, no region touches
the excluded qubits, and the estimated charge stays within CEILING_SECONDS. The arm, exclusion and charge rules are
those of scripts/pathion_kernel_map_check.py; the ratio rule is that of the retained orientation check.

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


def failures(record: dict, min_regions: int, ceiling: float) -> list[str]:
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
    return found


def main() -> int:
    min_regions = int(sys.argv[1]) if len(sys.argv) > 1 else MIN_REGIONS
    ceiling = float(sys.argv[2]) if len(sys.argv) > 2 else CEILING_SECONDS
    record = json.loads((Path(os.environ["RUN"]) / "record.json").read_text())
    found = failures(record, min_regions, ceiling)
    for line in found:
        print(f"{GROUP} check: {line}", file=sys.stderr)
    if not found:
        print(f"{GROUP} check: plan admitted")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
