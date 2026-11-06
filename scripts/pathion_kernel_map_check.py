"""Mechanical admission check of a pathion_kernel_map plan, the --check of scripts/approved_run.sh.

The approval covers a rule and bounds, and the submit plans afresh on the calibration in force, so this check binds
the fresh plan in $RUN (the dry run's directory) to the case: both orientations of every operand route to the same
two-qubit gate count (they are one parametrized circuit), no replica touches the excluded qubits, at least
MIN_REPLICAS replicas are placed, and the estimated charge 2 + shots * sum(rep_delay + scheduled duration) stays within
the per-job ceiling. Exit 0 admits the plan; any failure exits 1 and names it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

GROUP = "pathion_kernel_map"
MIN_REPLICAS = 5
CEILING_SECONDS = 30.0
DT_SECONDS = 4e-9
EXCLUDED = {"ibm_fez": {2, 3, 4, 16}, "ibm_kingston": {0, 1, 2, 3, 4, 16}}


def failures(record: dict) -> list[str]:
    found: list[str] = []
    groups = [g for g in record["groups"] if g["group"] == GROUP]
    if len(groups) != 1:
        return [f"expected one {GROUP} group, found {len(groups)}"]
    group = groups[0]
    backend = group["backend"]
    cz = {m["name"]: m["cz"] for m in group["members"]}
    for name, count in cz.items():
        if name.endswith("_minus") and cz.get(name[: -len("minus")] + "plus") != count:
            found.append(f"{name}: {count} CZ against {cz.get(name[: -len('minus')] + 'plus')} for its plus arm")
    if len(group["replicas"]) < MIN_REPLICAS:
        found.append(f"{len(group['replicas'])} replicas, fewer than {MIN_REPLICAS}")
    used = {q for replica in group["replicas"] for q in replica["physical_qubits"]}
    if used & EXCLUDED.get(backend, set()):
        found.append(f"{backend}: replicas use excluded qubits {sorted(used & EXCLUDED[backend])}")
    shots, rep = record["shots"], record["policy"]["rep_delay_seconds"]
    charge = 2 + sum(shots * (rep + p["target_gate_lower_bound_dt"] * DT_SECONDS) for p in record["execution_pubs"])
    if charge > CEILING_SECONDS:
        found.append(f"estimated charge {charge:.1f} s exceeds {CEILING_SECONDS} s")
    return found


def main() -> int:
    run = Path(os.environ["RUN"])
    found = failures(json.loads((run / "record.json").read_text()))
    for line in found:
        print(f"pathion_kernel_map check: {line}", file=sys.stderr)
    if not found:
        print("pathion_kernel_map check: plan admitted")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
