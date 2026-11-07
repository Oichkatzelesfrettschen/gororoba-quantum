"""Mechanical admission check of a pathion_wide_coset plan, the --check of scripts/approved_run.sh.

The fresh plan in $RUN (the dry run's directory) must keep the case's structure: every member of the group is planned,
both arms of every block route to one two-qubit gate count, at least MIN_REPLICAS replicas are placed away from the
operator's excluded qubits, the first member carries live_run's isolated reference, and the worst-case billed charge
stays at least RESERVE_SECONDS below the seconds the account has left.

The charge is 2.3 + sum over PUBs of shots * (rep_delay + 4 ns * target_gate_lower_bound_dt + EXTRA[backend]), with
EXTRA the upper residual of the billed charge over the planner's bound per execution that the drain jobs measured:
7.2 us on ibm_fez and 9.2 us on ibm_kingston. Billed charges are whole seconds, so the check rounds the estimate up
before it compares. Arguments MIN_REPLICAS and REMAINING_SECONDS override the defaults; REMAINING_SECONDS is the
account's `usage_remaining_seconds` read just before the dry run.
Exit 0 admits the plan; any failure exits 1 and names it.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

GROUP = "pathion_wide_coset"
MIN_REPLICAS = 16
REMAINING_SECONDS = 10.0
RESERVE_SECONDS = 1.0
DT_SECONDS = 4e-9
JOB_OVERHEAD_SECONDS = 2.3
EXTRA_SECONDS = {"ibm_fez": 7.2e-6, "ibm_kingston": 9.2e-6}


def estimated_charge(record: dict, backend: str) -> float:
    shots, rep = record["shots"], record["policy"]["rep_delay_seconds"]
    extra = EXTRA_SECONDS[backend]
    return JOB_OVERHEAD_SECONDS + sum(
        shots * (rep + p["target_gate_lower_bound_dt"] * DT_SECONDS + extra) for p in record["execution_pubs"]
    )


def expected_members() -> set[str]:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
    import pathion_wide_coset

    return {member.name for member in pathion_wide_coset.wide_members()}


def failures(
    record: dict,
    remaining: float = REMAINING_SECONDS,
    min_replicas: int = MIN_REPLICAS,
    wanted: set[str] | None = None,
) -> list[str]:
    found: list[str] = []
    groups = [g for g in record["groups"] if g["group"] == GROUP]
    if len(groups) != 1:
        return [f"expected one {GROUP} group, found {len(groups)}"]
    group = groups[0]
    backend = group["backend"]
    if backend not in EXTRA_SECONDS:
        return [f"no measured charge residual for {backend}"]
    cz = {m["name"]: m["cz"] for m in group["members"]}
    planned = {name for name in cz if not name.endswith("_isolated")}
    missing = sorted((expected_members() if wanted is None else wanted) - planned)
    if missing:
        found.append(f"{len(missing)} members are not planned, first {missing[0]}")
    for name, count in cz.items():
        if name.endswith("_minus") and cz.get(name[: -len("minus")] + "plus") != count:
            found.append(f"{name}: {count} CZ against {cz.get(name[: -len('minus')] + 'plus')} for its plus arm")
    if len(group["replicas"]) < min_replicas:
        found.append(f"{len(group['replicas'])} replicas, fewer than {min_replicas}")
    excluded = {int(q) for q in record["policy"].get("operator_excluded_qubits", {}).get(backend, [])}
    used = {q for replica in group["replicas"] for q in replica["physical_qubits"]}
    if used & excluded:
        found.append(f"{backend}: replicas use excluded qubits {sorted(used & excluded)}")
    if not any(m["name"].endswith("_isolated") for m in group["members"]):
        found.append("the first member has no isolated reference")
    billed = math.ceil(estimated_charge(record, backend))
    if billed > remaining - RESERVE_SECONDS:
        found.append(f"worst-case billed charge {billed} s exceeds {remaining} s remaining less {RESERVE_SECONDS} s")
    return found


def main() -> int:
    remaining, min_replicas = REMAINING_SECONDS, MIN_REPLICAS
    if len(sys.argv) > 1:
        min_replicas = int(sys.argv[1])
    if len(sys.argv) > 2:
        remaining = float(sys.argv[2])
    run = Path(os.environ["RUN"])
    record = json.loads((run / "record.json").read_text())
    found = failures(record, remaining, min_replicas)
    for line in found:
        print(f"{GROUP} check: {line}", file=sys.stderr)
    if not found:
        backend = next(g["backend"] for g in record["groups"] if g["group"] == GROUP)
        charge = estimated_charge(record, backend)
        print(f"{GROUP} check: plan admitted, worst-case charge {charge:.2f} s of {remaining} s remaining")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
