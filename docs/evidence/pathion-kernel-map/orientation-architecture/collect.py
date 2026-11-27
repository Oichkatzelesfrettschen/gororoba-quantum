"""Collection half of the orientation-architecture analysis: device calibrations and compiled-pattern op lists.

Network and QPY reads only; nothing is submitted. Offline analysis reads the JSON files this half writes
(orientation_architecture.py).

  collect-device BACKEND [--at ISO]   read properties (historical when --at is given) into device_*.json
  collect-pattern                     read the three dry-run records and their isa.qpy archives into patterns.json
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

RUNS = {
    "ibm_fez": "2026-11-27T225727.770557Z",
    "ibm_kingston": "2026-11-27T225850.191883Z",
    "ibm_marrakesh": "2026-11-27T230015.212103Z",
}


def device_json(backend: str, props: object, num_qubits: int, coupling: list[list[int]]) -> dict:
    from qiskit_ibm_runtime.models import BackendProperties

    if not isinstance(props, BackendProperties):
        raise TypeError("properties of an IBM backend expected")

    def gate(name: str, qubits: list[int]) -> tuple[float, float] | None:
        try:
            return float(props.gate_error(name, qubits)), float(props.gate_length(name, qubits))
        except Exception:
            return None

    qubits: dict[str, dict] = {}
    for q in range(num_qubits):
        entry: dict = {}
        for key, fn in (
            ("t1", lambda q=q: props.t1(q)),
            ("t2", lambda q=q: props.t2(q)),
            ("readout_error", lambda q=q: props.readout_error(q)),
            ("readout_length", lambda q=q: props.readout_length(q)),
        ):
            try:
                entry[key] = float(fn())
            except Exception:
                entry[key] = None
        for name in ("sx", "x", "rz"):
            got = gate(name, [q])
            entry[name] = None if got is None else {"error": got[0], "length": got[1]}
        qubits[str(q)] = entry
    edges: dict[str, dict | None] = {}
    for a, b in coupling:
        got = gate("cz", [a, b])
        edges[f"{a}-{b}"] = None if got is None else {"error": got[0], "length": got[1]}
    return {
        "backend": backend,
        "calibration": props.last_update_date.isoformat(),
        "num_qubits": num_qubits,
        "faulty_qubits": sorted(props.faulty_qubits()),
        "faulty_cz": sorted([list(g.qubits) for g in props.faulty_gates() if g.gate == "cz"]),
        "faulty_other": sorted([[g.gate, *g.qubits] for g in props.faulty_gates() if g.gate != "cz"]),
        "qubits": qubits,
        "cz": edges,
    }


def collect_device(backend: str, at: str | None, out: Path) -> None:
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    be = service.backend(backend)
    coupling = [list(map(int, qargs)) for qargs in be.target["cz"]]
    if at is None:
        props = be.properties(refresh=True)
    else:
        props = be.properties(datetime=dt.datetime.fromisoformat(at))
    data = device_json(backend, props, be.num_qubits, sorted(coupling))
    out.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"{out.name}: {backend} calibration {data['calibration']}")


def collect_pattern(out: Path) -> None:
    """Per backend: the replica-0 op lists of every member, in the replica-0 physical labels."""
    from qiskit import qpy

    patterns: dict = {}
    for backend, run in RUNS.items():
        rdir = ROOT / "results" / "live" / run
        record = json.loads((rdir / "record.json").read_text())
        digest = (rdir / "isa.qpy.sha256").read_text().strip()
        circuits = {c.name: c for c in qpy.load(open(ROOT / "results" / "live" / "archives" / f"{digest}.qpy", "rb"))}
        group = record["groups"][0]
        r0 = group["replicas"][0]["physical_qubits"]
        pub_of = {}
        for pub in record["execution_pubs"]:
            for comp in pub["components"]:
                pub_of[comp["member"]] = pub["name"]
        members: dict = {}
        for member in group["members"]:
            name = member["name"]
            circ = circuits[pub_of[name]]
            ops = []
            for inst in circ.data:
                qs = [circ.find_bit(q).index for q in inst.qubits]
                if not set(qs) <= set(r0):
                    continue
                op = inst.operation
                ops.append([op.name, qs])
            members[name] = {
                "cz_record": member["cz"],
                "depth_record": member["depth"],
                "ops": ops,
            }
        patterns[backend] = {
            "run": run,
            "calibration": group["calibration"],
            "seed_transpiler": group["seed_transpiler"],
            "replica0": r0,
            "layout0": group["replicas"][0]["initial_layout"],
            "layout_logical": group["initial_layout"],
            "replicas_record": [
                {
                    "qubits": r["physical_qubits"],
                    "score": r["score"],
                    "mapping": r["mapping"],
                }
                for r in group["replicas"]
            ],
            "member_replicas_record": {
                m["name"]: [
                    {
                        "qubits": x["physical_qubits"],
                        "esp": x["esp"],
                        "coherence": x["coherence"],
                        "duration_s": x["duration_s"],
                    }
                    for x in m.get("replicas", [])
                ]
                for m in group["members"]
            },
            "excluded_qubits": record["backends"][backend]["excluded_qubits"],
            "excluded_edges": record["backends"][backend]["excluded_edges"],
            "pub_dt_record": {
                c["member"]: pub["target_gate_lower_bound_dt"]
                for pub in record["execution_pubs"]
                for c in pub["components"]
            },
            "shots": record["shots"],
            "rep_delay": record["policy"]["rep_delay_seconds"],
            "floor_candidates": record["fusion_placement"]["clusters"][0]["groups"][0]["floor_candidates"],
            "policy": {
                k: record["policy"][k]
                for k in (
                    "max_readout_error",
                    "max_cz_error",
                    "max_sx_error",
                    "min_t1_us",
                    "min_t2_us",
                    "replica_floor",
                    "operator_excluded_qubits",
                )
            },
            "members": members,
        }
    out.write_text(json.dumps(patterns, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"{out.name}: {sum(len(p['members']) for p in patterns.values())} members")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "collect-device":
        backend = sys.argv[2]
        at = sys.argv[sys.argv.index("--at") + 1] if "--at" in sys.argv else None
        out = Path(sys.argv[sys.argv.index("--out") + 1])
        collect_device(backend, at, out)
    elif mode == "collect-pattern":
        collect_pattern(Path(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
