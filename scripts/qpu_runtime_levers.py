"""Runtime levers for the retained ripple and rank-sector cases, priced from their own PUB ledgers.

The cost model is the planner's: a PUB costs shots x (scheduled duration +
repetition delay + reset + classical latency), and a job adds a declared
overhead (2.3 s nominal, 4.6 s under latency stress). The client-side Sampler
takes one shot count per job, so every shot tier is its own job, and each
invocation applies one uniform ceiling to all of its jobs. Every number below
is recomputed from the selected candidate's ledger in each record.json:

1. Baseline: the selected candidates' nominal and stress charges and their
   uniform per-job ceilings.
2. Per-job ceilings: each job's ceiling is the ceiling of its own stress
   charge, so the cap sum follows the workload instead of the largest job.
3. Cross-family fusion: each rank PUB rides in a ripple PUB of the same shot
   tier on disjoint qubits; the fused PUB costs its larger scheduled duration
   once. Rank PUBs above the largest ripple tier raise one ripple PUB to their
   shots. The script counts pairs whose current placements are already
   disjoint with a one-hop buffer on the ibm_kingston coupling map; the rest
   need a joint placement.
4. Repetition delay: the same ledgers at 100 and 50 microseconds, which needs a
   state-preparation qualification before any submission uses it.

Usage: "$PYTHON" scripts/qpu_runtime_levers.py [--out FILE] [--check FILE]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RIPPLE = ROOT / "results/live/2026-10-14T113012.109467Z/record.json"
RANK = ROOT / "results/live/2026-10-14T113945.518703Z/record.json"
NOMINAL_OVERHEAD = 2.3
STRESS_OVERHEAD = 4.6
DELAYS = (250e-6, 100e-6, 50e-6)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load(path: Path) -> dict[str, Any]:
    record = json.loads(path.read_text(encoding="utf-8"))
    require(record["state"] == "planned", f"{path.name}: the case must be planned")
    selected = record["optimization"]["selected"]
    candidate = next(c for c in record["optimization"]["candidates"] if c["name"] == selected)
    require(candidate["feasible"], f"{path.parent.name}: selected candidate must be feasible")
    footprint = {
        pub["name"]: sorted({q for component in pub["components"] for q in component["physical_qubits"]})
        for pub in record["execution_pubs"]
    }
    pubs = []
    for job in candidate["jobs"]:
        require(abs(job["overhead_seconds"] - NOMINAL_OVERHEAD) < 1e-12, "declared nominal overhead")
        for pub in job["pubs"]:
            per_shot = pub["scheduled_seconds"] + pub["reset_seconds"] + pub["classical_latency_seconds"]
            pubs.append(
                {
                    "name": pub["name"],
                    "shots": pub["shots"],
                    "scheduled": per_shot,
                    "delay": pub["repetition_delay_seconds"],
                    "qubits": footprint[pub["name"]],
                    "estimate": pub["estimated_execution_seconds"],
                }
            )
    for pub in pubs:
        recomputed = pub["shots"] * (pub["scheduled"] + pub["delay"])
        require(abs(recomputed - pub["estimate"]) < 1e-9, f"{pub['name']}: ledger cost model")
    total = sum(p["estimate"] for p in pubs) + NOMINAL_OVERHEAD * len(candidate["jobs"])
    require(abs(total - candidate["estimated_charge_seconds"]) < 1e-6, "selected nominal charge")
    return {
        "pubs": pubs,
        "jobs": len(candidate["jobs"]),
        "uniform_ceiling": record["policy"]["max_execution_seconds"],
        "nominal": candidate["estimated_charge_seconds"],
        "stress": candidate["worst_case_charge_seconds"],
        "sha256_name": path.parent.name,
    }


def jobs_by_tier(pubs: list[dict[str, Any]], delay: float | None = None) -> dict[int, float]:
    tiers: dict[int, float] = {}
    for pub in pubs:
        d = pub["delay"] if delay is None else delay
        tiers[pub["shots"]] = tiers.get(pub["shots"], 0.0) + pub["shots"] * (pub["scheduled"] + d)
    return tiers


def charges(tiers: dict[int, float]) -> dict[str, Any]:
    nominal = sum(tiers.values()) + NOMINAL_OVERHEAD * len(tiers)
    stress = sum(tiers.values()) + STRESS_OVERHEAD * len(tiers)
    per_job = {str(shots): math.ceil(seconds + STRESS_OVERHEAD) for shots, seconds in sorted(tiers.items())}
    return {
        "jobs": len(tiers),
        "nominal_seconds": round(nominal, 6),
        "stress_seconds": round(stress, 6),
        "per_job_ceilings": per_job,
        "per_job_ceiling_sum": sum(per_job.values()),
        "uniform_ceiling_sum": max(per_job.values()) * len(tiers),
    }


def coupling_edges() -> set[tuple[int, int]]:
    from qiskit_ibm_runtime.fake_provider import FakeKingston

    edges = set()
    for a, b in FakeKingston().coupling_map.get_edges():
        edges.add((a, b))
        edges.add((b, a))
    return edges


def fuse(ripple: list[dict[str, Any]], rank: list[dict[str, Any]], edges: set[tuple[int, int]]) -> dict[str, Any]:
    """Greedy same-tier fusion; rank PUBs above every ripple tier lift one ripple PUB."""
    hosts = sorted(ripple, key=lambda p: (p["shots"], p["name"]))
    used: set[str] = set()
    fused: list[dict[str, Any]] = []
    already_disjoint = 0
    top_tier = max(p["shots"] for p in ripple)
    for guest in sorted(rank, key=lambda p: (-p["shots"], p["name"])):
        tier = min(guest["shots"], top_tier)
        host = next((h for h in hosts if h["name"] not in used and h["shots"] == tier), None)
        if host is None:
            raise RuntimeError(f"no ripple host at {tier} shots for {guest['name']}")
        used.add(host["name"])
        a, b = set(host["qubits"]), set(guest["qubits"])
        if not a & b and not any((x, y) in edges for x in a for y in b):
            already_disjoint += 1
        require(len(a | b) <= 148, "fused footprint fits the 148 usable Kingston qubits")
        fused.append(
            {
                "name": f"{host['name']}+{guest['name']}",
                "shots": max(host["shots"], guest["shots"]),
                "scheduled": max(host["scheduled"], guest["scheduled"]),
                "delay": host["delay"],
            }
        )
    rest = [h for h in hosts if h["name"] not in used]
    return {"pubs": fused + rest, "pairs": len(fused), "already_disjoint_pairs": already_disjoint}


def analyze() -> dict[str, Any]:
    ripple, rank = load(RIPPLE), load(RANK)
    for case in (ripple, rank):
        base = charges(jobs_by_tier(case["pubs"]))
        require(abs(base["nominal_seconds"] - case["nominal"]) < 1e-6, "baseline nominal")
        require(abs(base["stress_seconds"] - case["stress"]) < 1e-6, "baseline stress")
        require(base["uniform_ceiling_sum"] <= case["uniform_ceiling"] * case["jobs"], "baseline ceilings")
    separate = {
        "ripple": charges(jobs_by_tier(ripple["pubs"])),
        "rank": charges(jobs_by_tier(rank["pubs"])),
        "uniform_ceilings_as_planned": {"ripple": 2 * ripple["uniform_ceiling"], "rank": 3 * rank["uniform_ceiling"]},
    }
    fusion = fuse(ripple["pubs"], rank["pubs"], coupling_edges())
    fused_tiers = jobs_by_tier(fusion["pubs"])
    delays = {}
    for delay in DELAYS:
        key = f"{round(delay * 1e6)}us"
        delays[key] = {
            "separate_nominal_seconds": round(
                charges(jobs_by_tier(ripple["pubs"], delay))["nominal_seconds"]
                + charges(jobs_by_tier(rank["pubs"], delay))["nominal_seconds"],
                6,
            ),
            "fused_nominal_seconds": charges(jobs_by_tier(fusion["pubs"], delay))["nominal_seconds"],
        }
    return {
        "records": {"ripple": RIPPLE.parent.name, "rank": RANK.parent.name},
        "separate": separate,
        "fusion": {
            **charges(fused_tiers),
            "pairs": fusion["pairs"],
            "pairs_disjoint_with_buffer_as_placed": fusion["already_disjoint_pairs"],
        },
        "repetition_delay": delays,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--out", type=Path, help="write the analysis JSON")
    mode.add_argument("--check", type=Path, help="replay a retained analysis JSON")
    args = parser.parse_args(argv)
    result = analyze()
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    if args.check:
        require(args.check.read_text(encoding="utf-8") == text, "runtime-lever analysis differs from the retained JSON")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
