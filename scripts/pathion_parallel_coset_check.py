"""Mechanical admission check of a pathion_parallel_coset plan, the --check of scripts/approved_run.sh.

The fresh plan in $RUN (the dry run's directory) must keep the case's structure: both arms of every block, every flip
twin and every repeat route to the base block's two-qubit gate count, the shared-template four-term arms (T, D, F, E0,
E1) agree, no four-term circuit exceeds FOUR_TERM_CZ_BUDGET, at least MIN_REPLICAS replicas are placed, the first
member carries live_run's isolated reference, and the estimated charge stays within CHARGE_FRACTION of the per-job
ceiling. The charge is 2.3 + sum over PUBs of shots * (rep_delay + 4 ns * target_gate_lower_bound_dt +
EXTRA[backend]), with EXTRA the measured residual of the billed charge over the planner's bound per execution: ibm_fez
7.1 and 6.6 us on its two retained 20 us static jobs (8.2 us on the kernel-map job), ibm_kingston 9.0 us
(qpu_run_economy.md rule 14) and ibm_marrakesh 16.6 us. Arguments MIN_REPLICAS CEILING_SECONDS override the defaults.
Exit 0 admits the plan; any failure exits 1 and names it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

GROUP = "pathion_parallel_coset"
MIN_REPLICAS = 10
CEILING_SECONDS = 60.0
CHARGE_FRACTION = 0.92
FOUR_TERM_CZ_BUDGET = 30
DT_SECONDS = 4e-9
JOB_OVERHEAD_SECONDS = 2.3
# Billed charge minus the planner's (rep_delay + scheduled bound) per execution, upper observed value per backend.
EXTRA_SECONDS = {"ibm_fez": 8.2e-6, "ibm_kingston": 9.0e-6, "ibm_marrakesh": 17.2e-6}


def estimated_charge(record: dict, backend: str) -> float:
    shots, rep = record["shots"], record["policy"]["rep_delay_seconds"]
    extra = EXTRA_SECONDS[backend]
    return JOB_OVERHEAD_SECONDS + sum(
        shots * (rep + p["target_gate_lower_bound_dt"] * DT_SECONDS + extra) for p in record["execution_pubs"]
    )


def failures(record: dict, ceiling: float = CEILING_SECONDS, min_replicas: int = MIN_REPLICAS) -> list[str]:
    found: list[str] = []
    groups = [g for g in record["groups"] if g["group"] == GROUP]
    if len(groups) != 1:
        return [f"expected one {GROUP} group, found {len(groups)}"]
    group = groups[0]
    backend = group["backend"]
    if backend not in EXTRA_SECONDS:
        return [f"no measured charge residual for {backend}"]
    cz = {m["name"]: m["cz"] for m in group["members"]}
    for name, count in cz.items():
        if name.endswith("_minus") and cz.get(name[: -len("minus")] + "plus") != count:
            found.append(f"{name}: {count} CZ against {cz.get(name[: -len('minus')] + 'plus')} for its plus arm")
        if name.startswith("cflip_") and cz.get(name.replace("cflip_", "cmap_", 1)) != count:
            found.append(f"{name}: {count} CZ against {cz.get(name.replace('cflip_', 'cmap_', 1))} for its base block")
        if name.startswith("crep_") and cz.get(name.replace("crep_", "cmap_", 1)) != count:
            found.append(f"{name}: {count} CZ against {cz.get(name.replace('crep_', 'cmap_', 1))} for its base block")
        if name.startswith("ftb_") and count > FOUR_TERM_CZ_BUDGET:
            found.append(f"{name}: {count} CZ above the four-term budget {FOUR_TERM_CZ_BUDGET}")
    shared: dict[str, set[int]] = {}
    for name, count in cz.items():
        if name.startswith("ftb_") and name.rsplit("_", 1)[1] in ("T", "D", "F", "E0", "E1"):
            shared.setdefault(name.rsplit("_", 1)[0], set()).add(count)
    for block, counts in shared.items():
        if len(counts) != 1:
            found.append(f"{block}: shared-template arms route to {sorted(counts)} CZ")
    if len(group["replicas"]) < min_replicas:
        found.append(f"{len(group['replicas'])} replicas, fewer than {min_replicas}")
    excluded = set()
    for qubits in record["policy"].get("operator_excluded_qubits", {}).get(backend, []):
        excluded.add(int(qubits))
    used = {q for replica in group["replicas"] for q in replica["physical_qubits"]}
    if used & excluded:
        found.append(f"{backend}: replicas use excluded qubits {sorted(used & excluded)}")
    if not any(m["name"].endswith("_isolated") for m in group["members"]):
        found.append("the first member has no isolated reference")
    charge = estimated_charge(record, backend)
    if charge > CHARGE_FRACTION * ceiling:
        found.append(f"estimated charge {charge:.1f} s exceeds {CHARGE_FRACTION} x {ceiling} s")
    return found


def main() -> int:
    ceiling, min_replicas = CEILING_SECONDS, MIN_REPLICAS
    if len(sys.argv) > 1:
        min_replicas = int(sys.argv[1])
    if len(sys.argv) > 2:
        ceiling = float(sys.argv[2])
    run = Path(os.environ["RUN"])
    record = json.loads((run / "record.json").read_text())
    found = failures(record, ceiling, min_replicas)
    for line in found:
        print(f"{GROUP} check: {line}", file=sys.stderr)
    if not found:
        backend = next(g["backend"] for g in record["groups"] if g["group"] == GROUP)
        print(f"{GROUP} check: plan admitted, estimated charge {estimated_charge(record, backend):.1f} s")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
