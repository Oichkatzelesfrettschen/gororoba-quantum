"""Mechanical admission check of a pathion_wide_coset plan, the --check of scripts/approved_run.sh.

The fresh plan in $RUN (the dry run's directory) must keep the case's structure: every operand-arm member of the group
is planned with one body per placement, the placements number exactly REPLICAS (16 for ``pathion_wide_coset``, 17 for
``pathion_wide_coset_d32``) away from the operator's excluded qubits, the plus and minus arm of every member route to
one two-qubit gate count on every placement, and the worst-case charge stays at least RESERVE_SECONDS below the seconds
the account has left. The isolated reference PUB is optional (`--no-isolated-reference`): the case reads no crosstalk
decision from it, since its interval at these shots cannot certify the drain case's margin.

The charge is 2.3 + sum over PUBs of (shots * (rep_delay + 4 ns * target_gate_lower_bound_dt + EXTRA[backend]) +
PUB_TERM[backend]). EXTRA is the upper residual of the billed charge over the planner's bound per execution that the
drain jobs measured (7.2 us on ibm_fez, 9.2 us on ibm_kingston) and PUB_TERM the two-sigma upper bound of the billed
charge per PUB that a fit over the retained single-job runs gives (5.7 ms on ibm_fez, 2.6 ms on ibm_kingston; the fit
is consistent with zero). A fused PUB's gate bound is that of its deepest placement, so a PUB that mixes shallow and
deep blocks bills at the deepest. Billed charges are whole seconds and the job's execution ceiling equals the remainder,
so the job is killed only if its real charge passes the ceiling; the check therefore compares the unrounded worst case,
which already carries the upper residual and the two-sigma per-PUB term, with the remainder less RESERVE_SECONDS.
Arguments REPLICAS and REMAINING_SECONDS override the defaults; REMAINING_SECONDS is the account's
`usage_remaining_seconds` read just before the dry run.
Exit 0 admits the plan; any failure exits 1 and names it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

GROUPS = {"pathion_wide_coset": 16, "pathion_wide_coset_d32": 17}
REMAINING_SECONDS = 10.0
RESERVE_SECONDS = 0.4
DT_SECONDS = 4e-9
JOB_OVERHEAD_SECONDS = 2.3
EXTRA_SECONDS = {"ibm_fez": 7.2e-6, "ibm_kingston": 9.2e-6}
PUB_TERM_SECONDS = {"ibm_fez": 5.7e-3, "ibm_kingston": 2.6e-3}


def estimated_charge(record: dict, backend: str) -> float:
    shots, rep = record["shots"], record["policy"]["rep_delay_seconds"]
    extra, per_pub = EXTRA_SECONDS[backend], PUB_TERM_SECONDS[backend]
    return JOB_OVERHEAD_SECONDS + sum(
        shots * (rep + p["target_gate_lower_bound_dt"] * DT_SECONDS + extra) + per_pub for p in record["execution_pubs"]
    )


def expected_members(reference: bool = False) -> set[str]:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
    import pathion_wide_coset

    return {member.name for member in pathion_wide_coset.wide_members(reference)}


def failures(
    record: dict, remaining: float = REMAINING_SECONDS, replicas: int | None = None, wanted: set[str] | None = None
) -> list[str]:
    found: list[str] = []
    groups = [g for g in record["groups"] if g["group"] in GROUPS]
    if len(groups) != 1:
        return [f"expected one pathion_wide_coset group, found {len(groups)}"]
    group = groups[0]
    backend = group["backend"]
    if backend not in EXTRA_SECONDS:
        return [f"no measured charge residual for {backend}"]
    want = GROUPS[group["group"]] if replicas is None else replicas
    members = {m["name"]: m for m in group["members"] if not m["name"].endswith("_isolated")}
    missing = sorted((expected_members(group["group"].endswith("_d32")) if wanted is None else wanted) - set(members))
    if missing:
        found.append(f"{len(missing)} members are not planned, first {missing[0]}")
    for name, member in members.items():
        cz = member.get("replica_cz", [])
        if len(cz) != want or len(member.get("replica_bodies", [])) != want:
            found.append(
                f"{name}: {len(cz)} body CZ counts and {len(member.get('replica_bodies', []))} bodies, not {want}"
            )
        if name.endswith("_minus"):
            plus = members.get(name[: -len("minus")] + "plus")
            if plus is not None and plus.get("replica_cz") != cz:
                found.append(f"{name}: CZ per placement {cz} against {plus.get('replica_cz')} for its plus arm")
    if len(group["replicas"]) != want:
        found.append(f"{len(group['replicas'])} replicas, not {want}")
    excluded = {int(q) for q in record["policy"].get("operator_excluded_qubits", {}).get(backend, [])}
    used = {q for replica in group["replicas"] for q in replica["physical_qubits"]}
    if used & excluded:
        found.append(f"{backend}: replicas use excluded qubits {sorted(used & excluded)}")
    charge = estimated_charge(record, backend)
    if charge > remaining - RESERVE_SECONDS:
        found.append(f"worst-case charge {charge:.2f} s exceeds {remaining} s remaining less {RESERVE_SECONDS} s")
    return found


def main() -> int:
    remaining, replicas = REMAINING_SECONDS, None
    if len(sys.argv) > 1:
        replicas = int(sys.argv[1])
    if len(sys.argv) > 2:
        remaining = float(sys.argv[2])
    run = Path(os.environ["RUN"])
    record = json.loads((run / "record.json").read_text())
    found = failures(record, remaining, replicas)
    name = next((g["group"] for g in record["groups"] if g["group"] in GROUPS), "pathion_wide_coset")
    for line in found:
        print(f"{name} check: {line}", file=sys.stderr)
    if not found:
        backend = next(g["backend"] for g in record["groups"] if g["group"] == name)
        charge = estimated_charge(record, backend)
        print(f"{name} check: plan admitted, worst-case charge {charge:.2f} s of {remaining} s remaining")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
