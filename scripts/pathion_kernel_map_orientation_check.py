"""Mechanical admission check of a pathion_kernel_map_orientation plan, the --check of scripts/approved_run.sh.

The case (docs/design/pathion-kernel-map-orientation-bit.md, "Falsifiers of the design") admits a fresh plan only
when both arms of every unit route to one CZ count, the moved, exchanged and swap members of each operand route within
20 percent of that operand's control, at least MIN_REGIONS disjoint regions are placed, no region touches the excluded
qubits, and the estimated charge stays within the per-job ceiling. The arm, exclusion and charge rules are those of
scripts/pathion_kernel_map_check.py, called with this group. Exit 0 admits the plan; any failure exits 1 and names it.

Usage: RUN=DRY_RUN_DIR "$PYTHON" scripts/pathion_kernel_map_orientation_check.py [MIN_REGIONS [CEILING_SECONDS]]
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType

GROUP = "pathion_kernel_map_orientation"
MIN_REGIONS = 14
CEILING_SECONDS = 18.0
RATIO_BOUND = 0.20
ROLES = ("move", "xtwin", "swap")


def _base_check() -> ModuleType:
    path = Path(__file__).with_name("pathion_kernel_map_check.py")
    spec = importlib.util.spec_from_file_location("pathion_kernel_map_check", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ratio_failures(members: list[dict]) -> list[str]:
    found: list[str] = []
    cz = {m["name"]: m["cz"] for m in members}
    for name, count in sorted(cz.items()):
        if not name.startswith("kmo_ctrl_") or not name.endswith("_plus"):
            continue
        tag = name[len("kmo_ctrl_") : -len("_plus")]
        for role in ROLES:
            for arm in ("plus", "minus"):
                other = cz.get(f"kmo_{role}_{tag}_{arm}")
                if other is None:
                    found.append(f"kmo_{role}_{tag}_{arm}: missing from the plan")
                elif abs(other - count) > RATIO_BOUND * count:
                    found.append(f"kmo_{role}_{tag}_{arm}: {other} CZ against {count} for its control")
    if not any(n.startswith("kmo_ctrl_") for n in cz):
        found.append("no control member in the plan")
    return found


def failures(record: dict, min_regions: int, ceiling: float) -> list[str]:
    base = _base_check()
    for attr, value in (("GROUP", GROUP), ("MIN_REPLICAS", min_regions), ("CEILING_SECONDS", ceiling)):
        setattr(base, attr, value)
    found: list[str] = list(base.failures(record))
    groups = [g for g in record["groups"] if g["group"] == GROUP]
    if len(groups) == 1:
        found += ratio_failures(groups[0]["members"])
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
