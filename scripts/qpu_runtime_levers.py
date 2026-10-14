"""Runtime levers for the retained ripple and rank-sector cases, priced from their own PUB ledgers.

The cost model is the planner's: a PUB costs shots x (scheduled duration +
repetition delay + reset + classical latency), and a job adds a declared
overhead (2.3 s nominal, 4.6 s under latency stress). The client-side Sampler
takes one shot count per job, so every shot tier is its own job, and each
invocation applies one uniform ceiling to all of its jobs. Every number below
is recomputed from the selected candidate's ledger in each record.json:

1. Baseline: the selected candidates' nominal and stress charges and their
   uniform per-job ceilings.
2. Per-job ceilings: each job's ceiling covers its own stress charge plus a
   declared scheduler residual of RESIDUAL_PER_SHOT per shot, so the cap sum
   follows the workload instead of the largest job and a job that runs a few
   microseconds per shot long is not cancelled at its ceiling.
3. Co-batching: ripple and rank PUBs of one shot tier share one Sampler job as
   separate PUBs. Circuits and placements stay as planned; only the job
   overheads of the duplicated tiers go away.
4. Cross-family fusion: each rank PUB rides in a ripple PUB of the same shot
   tier on separated qubits; the fused PUB costs its larger scheduled
   duration once. Rank PUBs above the largest ripple tier raise one ripple PUB
   to their shots. A maximum bipartite matching per tier chooses hosts whose
   current placement keeps a graph distance of at least 2 (one idle qubit
   between them) or 3 from the guest on the ibm_kingston coupling map, the
   fixed topology of the FakeKingston snapshot. "fusion_as_placed" fuses only
   those pairs and runs the other rank PUBs separately, which the current
   layouts support; "fusion" fuses all pairs and holds only after a joint
   placement of the rest, with routed durations replacing the
   maximum-of-components estimate. The saving splits into shared repetition
   delay (delay x the smaller shot count of each pair), overlapping circuit
   time, and the job overheads that fewer tiers remove.
5. Repetition delay: the same ledgers at 100 and 50 microseconds, which needs a
   state-preparation qualification before any submission uses it.
   execution.rep_delay is a Sampler-wide option, so a screening workload at
   250, 100 and 50 us is three jobs, each priced here with QUALIFICATION_PUBS
   PUBs of QUALIFICATION_SHOTS shots and a declared
   QUALIFICATION_CIRCUIT_SECONDS per shot. The price is a cost, not a
   demonstrated precision: the workload has no sensitivity map to the sector
   contrasts yet.
6. Rank tier collapse: the two 8192-shot rank PUBs priced at 4096 shots inside
   the 4096-shot job. A larger declared noise-model sample admits that design;
   its own record (RANK_4096) must reproduce the collapsed nominal and stress
   charges, which binds the arithmetic to an admitted dry run.

Job overheads are per client job. IBM bills overhead per sub-job and may split
a job, so every overhead saving here holds only when each client job runs as
one sub-job; the retained usage of an executed job decides it.

Every input is bound: each case directory's SHA256SUMS must list exactly its
case files with matching digests, record.json must carry the digest the case
names, and the output records those digests, the coupling-map edge digest and
this script's own digest. --self-test mutates a copy of the rank case (a
whitespace-only record.json change, one isa.qpy byte, one SHA256SUMS entry)
and requires each mutation to fail the binding.

Usage: "$PYTHON" scripts/qpu_runtime_levers.py [--out FILE | --check FILE | --self-test]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RIPPLE = ROOT / "results/live/2026-10-14T113012.109467Z/record.json"
RANK = ROOT / "results/live/2026-10-14T113945.518703Z/record.json"
# The rank-sector design at 1024 and 4096 shots only, admitted with 131072 noise-model samples.
RANK_4096 = ROOT / "results/live/2026-10-14T204144.526374Z/record.json"
# record.json digests the cases name for approval.
CASE_DIGESTS = {
    RIPPLE.parent.name: "c10b99918f8c68fee09746bb5351b41bc7c3a5c104cd77329ee9dbd005c845db",
    RANK.parent.name: "e39aaccec1c6cd3c64cb034602ac52089688633a4b167d1d20143f5c88c38c8b",
    RANK_4096.parent.name: "036237e0bae40cc7e65c3055a4a919300242b857f6c56d1ed5599600c7e211a1",
}
CASE_FILES = ("UNAPPROVED_CASE.md", "isa.qpy", "record.json")
NOMINAL_OVERHEAD = 2.3
STRESS_OVERHEAD = 4.6
DELAYS = (250e-6, 100e-6, 50e-6)
# Declared allowance for scheduler time the ledger does not model, per shot.
RESIDUAL_PER_SHOT = 2e-6
# Qualification design: initialization after a |1> shot, lag-1 memory, spectator Ramsey.
QUALIFICATION_PUBS = 3
QUALIFICATION_SHOTS = 2048
QUALIFICATION_CIRCUIT_SECONDS = 20e-6


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_case(directory: Path, record_digest: str) -> dict[str, str]:
    """Digests of a case whose SHA256SUMS lists exactly CASE_FILES, each matching, with the named record."""
    listed: dict[str, str] = {}
    for line in (directory / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        digest, _, name = line.partition("  ")
        require(len(digest) == 64 and name not in listed, f"{directory.name}/SHA256SUMS: malformed line")
        listed[name] = digest
    require(sorted(listed) == sorted(CASE_FILES), f"{directory.name}/SHA256SUMS: must list exactly {CASE_FILES}")
    for name, digest in listed.items():
        require(sha256(directory / name) == digest, f"{directory.name}/{name}: digest differs from SHA256SUMS")
    require(listed["record.json"] == record_digest, f"{directory.name}/record.json: not the record the case names")
    return {
        "record_sha256": listed["record.json"],
        "isa_qpy_sha256": listed["isa.qpy"],
        "case_sha256": listed["UNAPPROVED_CASE.md"],
        "sha256sums_sha256": sha256(directory / "SHA256SUMS"),
    }


def self_test() -> None:
    """Each mutation of a copied rank case fails verify_case; the unmodified copy passes."""
    source = RANK.parent
    digest = CASE_DIGESTS[source.name]

    def rejects(mutate: Any) -> bool:
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / source.name
            copy.mkdir()
            for name in (*CASE_FILES, "SHA256SUMS"):
                shutil.copyfile(source / name, copy / name)
            mutate(copy)
            try:
                verify_case(copy, digest)
            except RuntimeError:
                return True
            return False

    def whitespace(copy: Path) -> None:
        with (copy / "record.json").open("ab") as handle:
            handle.write(b" ")

    def qpy_byte(copy: Path) -> None:
        data = bytearray((copy / "isa.qpy").read_bytes())
        data[len(data) // 2] ^= 0x01
        (copy / "isa.qpy").write_bytes(bytes(data))

    def checksum_entry(copy: Path) -> None:
        text = (copy / "SHA256SUMS").read_text(encoding="ascii")
        line = next(entry for entry in text.splitlines() if entry.endswith("  isa.qpy"))
        flipped = ("0" if line[0] != "0" else "1") + line[1:]
        (copy / "SHA256SUMS").write_text(text.replace(line, flipped), encoding="ascii")

    def relisted(copy: Path) -> None:
        whitespace(copy)
        text = (copy / "SHA256SUMS").read_text(encoding="ascii")
        (copy / "SHA256SUMS").write_text(text.replace(digest, sha256(copy / "record.json")), encoding="ascii")

    require(not rejects(lambda copy: None), "self-test: the unmodified copy must pass")
    for name, mutate in (
        ("whitespace-only record.json change", whitespace),
        ("one isa.qpy byte", qpy_byte),
        ("one SHA256SUMS entry", checksum_entry),
        ("record.json change re-listed in SHA256SUMS", relisted),
    ):
        require(rejects(mutate), f"self-test: {name} passed the binding")
    print("runtime-lever input binding: 4 mutations rejected, unmodified case accepted")


def load(path: Path) -> dict[str, Any]:
    inputs = verify_case(path.parent, CASE_DIGESTS[path.parent.name])
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
        "inputs": {"directory": path.parent.name, **inputs},
    }


def jobs_by_tier(pubs: list[dict[str, Any]], delay: float | None = None) -> dict[int, tuple[float, int]]:
    """Execution seconds and total shots of each shot tier's job."""
    tiers: dict[int, tuple[float, int]] = {}
    for pub in pubs:
        d = pub["delay"] if delay is None else delay
        seconds, shots = tiers.get(pub["shots"], (0.0, 0))
        tiers[pub["shots"]] = (seconds + pub["shots"] * (pub["scheduled"] + d), shots + pub["shots"])
    return tiers


def charges(tiers: dict[int, tuple[float, int]]) -> dict[str, Any]:
    execution = sum(seconds for seconds, _ in tiers.values())
    nominal = execution + NOMINAL_OVERHEAD * len(tiers)
    stress = execution + STRESS_OVERHEAD * len(tiers)
    per_job = {
        str(tier): math.ceil(seconds + STRESS_OVERHEAD + shots * RESIDUAL_PER_SHOT)
        for tier, (seconds, shots) in sorted(tiers.items())
    }
    return {
        "jobs": len(tiers),
        "nominal_seconds": round(nominal, 6),
        "stress_seconds": round(stress, 6),
        "per_job_ceilings": per_job,
        "per_job_ceiling_sum": sum(per_job.values()),
        "uniform_ceiling_sum": max(per_job.values()) * len(tiers),
    }


def coupling_edges() -> list[tuple[int, int]]:
    """Undirected ibm_kingston coupling edges from the FakeKingston snapshot, sorted."""
    from qiskit_ibm_runtime.fake_provider import FakeKingston

    coupling = FakeKingston().coupling_map
    return sorted({(min(a, b), max(a, b)) for a, b in coupling.get_edges()})


def topology_identity(edges: list[tuple[int, int]]) -> dict[str, Any]:
    text = "".join(f"{a} {b}\n" for a, b in edges)
    return {
        "source": "qiskit_ibm_runtime.fake_provider.FakeKingston coupling map, undirected, sorted",
        "qubits": 1 + max(b for _, b in edges),
        "edges": len(edges),
        "edge_list_sha256": hashlib.sha256(text.encode("ascii")).hexdigest(),
    }


def distances(edges: list[tuple[int, int]]) -> list[list[int]]:
    """All-pairs hop distance on the coupling map."""
    size = 1 + max(b for _, b in edges)
    neighbors: list[set[int]] = [set() for _ in range(size)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    table = []
    for source in range(size):
        dist = [-1] * size
        dist[source] = 0
        frontier = [source]
        while frontier:
            following = []
            for node in frontier:
                for other in neighbors[node]:
                    if dist[other] < 0:
                        dist[other] = dist[node] + 1
                        following.append(other)
            frontier = following
        table.append(dist)
    return table


def separated(a: list[int], b: list[int], dist: list[list[int]], minimum: int) -> bool:
    """Every qubit of one placement is at least minimum hops from every qubit of the other."""
    return all(dist[p][q] >= minimum for p in a for q in b)


def max_matching(
    guests: list[dict[str, Any]], hosts: list[dict[str, Any]], dist: list[list[int]], minimum: int
) -> dict[str, str]:
    """Maximum bipartite matching of guests to hosts on already-separated placements, as host -> guest names."""
    by_name = {g["name"]: g for g in guests}
    owner: dict[str, str] = {}

    def augment(guest: dict[str, Any], seen: set[str]) -> bool:
        for host in hosts:
            if host["name"] in seen or not separated(host["qubits"], guest["qubits"], dist, minimum):
                continue
            seen.add(host["name"])
            if host["name"] not in owner or augment(by_name[owner[host["name"]]], seen):
                owner[host["name"]] = guest["name"]
                return True
        return False

    for guest in guests:
        augment(guest, set())
    return owner


def fuse(
    ripple: list[dict[str, Any]], rank: list[dict[str, Any]], dist: list[list[int]], minimum: int
) -> dict[str, Any]:
    """Same-tier fusion; a maximum matching per tier prefers hosts already separated as placed."""
    top_tier = max(p["shots"] for p in ripple)
    hosts_by_tier: dict[int, list[dict[str, Any]]] = {}
    for host in sorted(ripple, key=lambda p: p["name"]):
        hosts_by_tier.setdefault(host["shots"], []).append(host)
    guests_by_tier: dict[int, list[dict[str, Any]]] = {}
    for guest in sorted(rank, key=lambda p: p["name"]):
        guests_by_tier.setdefault(min(guest["shots"], top_tier), []).append(guest)
    chosen: dict[str, dict[str, Any]] = {}
    matched: dict[int, int] = {}
    for tier, guests in guests_by_tier.items():
        hosts = hosts_by_tier.get(tier, [])
        require(len(hosts) >= len(guests), f"{len(guests)} rank PUBs need ripple hosts at {tier} shots")
        owner = max_matching(guests, hosts, dist, minimum)
        matched[tier] = len(owner)
        assigned = {guest: host for host, guest in owner.items()}
        free = [h for h in hosts if h["name"] not in owner]
        for guest in guests:
            if guest["name"] not in assigned:
                assigned[guest["name"]] = free.pop(0)["name"]
        host_lookup = {h["name"]: h for h in hosts}
        for guest in guests:
            chosen[guest["name"]] = host_lookup[assigned[guest["name"]]]

    def merged(host: dict[str, Any], guest: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": f"{host['name']}+{guest['name']}",
            "shots": max(host["shots"], guest["shots"]),
            "scheduled": max(host["scheduled"], guest["scheduled"]),
            "delay": host["delay"],
        }

    used = {h["name"] for h in chosen.values()}
    require(len(used) == len(rank), "every rank PUB has its own ripple host")
    rest = [h for h in ripple if h["name"] not in used]
    placed = {g["name"] for g in rank if separated(chosen[g["name"]]["qubits"], g["qubits"], dist, minimum)}
    require(len(placed) == sum(matched.values()), "matched pairs are exactly the separated ones")
    as_placed = [merged(chosen[g["name"]], g) for g in rank if g["name"] in placed]
    as_placed += [g for g in rank if g["name"] not in placed]
    as_placed += rest + [chosen[g["name"]] for g in rank if g["name"] not in placed]
    lifted = sum(1 for g in rank if g["shots"] > chosen[g["name"]]["shots"])
    shared = sum(min(g["shots"], chosen[g["name"]]["shots"]) * g["delay"] for g in rank)
    return {
        "pubs": [merged(chosen[g["name"]], g) for g in rank] + rest,
        "as_placed_pubs": as_placed,
        "pairs": len(rank),
        "separated_pairs_by_tier": {str(t): n for t, n in sorted(matched.items())},
        "separated_pairs": sum(matched.values()),
        "lifted_hosts": lifted,
        "shared_repetition_delay_seconds": shared,
    }


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
    edges = coupling_edges()
    dist = distances(edges)
    fusion = fuse(ripple["pubs"], rank["pubs"], dist, 2)
    strict = fuse(ripple["pubs"], rank["pubs"], dist, 3)
    fused_tiers = jobs_by_tier(fusion["pubs"])
    separate_nominal = separate["ripple"]["nominal_seconds"] + separate["rank"]["nominal_seconds"]
    cobatched = charges(jobs_by_tier(ripple["pubs"] + rank["pubs"]))
    fused_charges = charges(fused_tiers)
    saving = separate_nominal - fused_charges["nominal_seconds"]
    overhead_saving = NOMINAL_OVERHEAD * (separate["ripple"]["jobs"] + separate["rank"]["jobs"] - fused_charges["jobs"])
    shared_delay = fusion["shared_repetition_delay_seconds"]
    as_placed = {d: charges(jobs_by_tier(f["as_placed_pubs"])) for d, f in (("2", fusion), ("3", strict))}
    shares = [p["delay"] / (p["scheduled"] + p["delay"]) for p in ripple["pubs"]]
    delays = {}
    for delay in DELAYS:
        key = f"{round(delay * 1e6)}us"
        separate_delay = (
            charges(jobs_by_tier(ripple["pubs"], delay))["nominal_seconds"]
            + charges(jobs_by_tier(rank["pubs"], delay))["nominal_seconds"]
        )
        fused_delay = charges(jobs_by_tier(fusion["pubs"], delay))["nominal_seconds"]
        delays[key] = {
            "separate_nominal_seconds": round(separate_delay, 6),
            "fused_nominal_seconds": fused_delay,
            "separate_reduction_vs_planned": round(1 - separate_delay / separate_nominal, 4),
            "fused_reduction_vs_fused_default": round(1 - fused_delay / fused_charges["nominal_seconds"], 4),
            "fused_reduction_vs_planned": round(1 - fused_delay / separate_nominal, 4),
        }
    top = max(p["shots"] for p in ripple["pubs"])
    collapsed = [{**p, "shots": min(p["shots"], top)} for p in rank["pubs"]]
    collapsed_rank = charges(jobs_by_tier(collapsed))
    collapsed_cobatched = charges(jobs_by_tier(ripple["pubs"] + collapsed))
    admitted = load(RANK_4096)
    require(abs(admitted["nominal"] - collapsed_rank["nominal_seconds"]) < 1e-6, "admitted rank nominal charge")
    require(abs(admitted["stress"] - collapsed_rank["stress_seconds"]) < 1e-6, "admitted rank stress charge")
    tier_collapse = {
        "admitted_record": admitted["inputs"],
        "admitted_uniform_ceiling_sum": admitted["uniform_ceiling"] * admitted["jobs"],
        "rank_pubs_moved": sum(1 for p in rank["pubs"] if p["shots"] > top),
        "rank": {
            **collapsed_rank,
            "saving_seconds": round(separate["rank"]["nominal_seconds"] - collapsed_rank["nominal_seconds"], 6),
        },
        "co_batched": {
            **collapsed_cobatched,
            "saving_seconds": round(separate_nominal - collapsed_cobatched["nominal_seconds"], 6),
        },
    }
    shots = QUALIFICATION_PUBS * QUALIFICATION_SHOTS
    qualification: dict[str, Any] = {"jobs": len(DELAYS), "per_job": {}}
    for delay in DELAYS:
        job = charges({shots: (shots * (QUALIFICATION_CIRCUIT_SECONDS + delay), shots)})
        qualification["per_job"][f"{round(delay * 1e6)}us"] = {
            "nominal_seconds": job["nominal_seconds"],
            "stress_seconds": job["stress_seconds"],
            "ceiling_seconds": job["per_job_ceiling_sum"],
        }
    for key in ("nominal_seconds", "stress_seconds"):
        qualification[key] = round(sum(j[key] for j in qualification["per_job"].values()), 6)
    qualification["per_job_ceiling_sum"] = sum(j["ceiling_seconds"] for j in qualification["per_job"].values())
    return {
        "qualification": qualification,
        "inputs": {
            "ripple": ripple["inputs"],
            "rank": rank["inputs"],
            "topology": topology_identity(edges),
            "analysis_source_sha256": sha256(Path(__file__)),
        },
        "rank_tier_collapse": tier_collapse,
        "separate": separate,
        "co_batched": {**cobatched, "saving_seconds": round(separate_nominal - cobatched["nominal_seconds"], 6)},
        "fusion": {
            **fused_charges,
            "pairs": fusion["pairs"],
            "lifted_hosts": fusion["lifted_hosts"],
            "saving_seconds": round(saving, 6),
            "saving_from_job_overheads_seconds": round(overhead_saving, 6),
            "saving_from_shared_repetition_delay_seconds": round(shared_delay, 6),
            "saving_from_overlapping_circuit_time_seconds": round(saving - overhead_saving - shared_delay, 6),
        },
        "fusion_as_placed": {
            f"min_distance_{d}": {
                **as_placed[d],
                "pairs": f["separated_pairs"],
                "pairs_by_tier": f["separated_pairs_by_tier"],
                "saving_seconds": round(separate_nominal - as_placed[d]["nominal_seconds"], 6),
            }
            for d, f in (("2", fusion), ("3", strict))
        },
        "residual_per_shot_seconds": RESIDUAL_PER_SHOT,
        "ripple_repetition_delay_share": {"min": round(min(shares), 4), "max": round(max(shares), 4)},
        "repetition_delay": delays,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--out", type=Path, help="write the analysis JSON")
    mode.add_argument("--check", type=Path, help="replay a retained analysis JSON")
    mode.add_argument("--self-test", action="store_true", help="mutate a copied case and require the binding to fail")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
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
