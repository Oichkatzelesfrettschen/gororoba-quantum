"""Compiled two-qubit load per member and the exposure of every retained run to flagged qubits.

For each retained run directory with a record.json and isa.qpy, the script
counts the CZ gates each fused-PUB component executes on its own physical
qubits, groups members into kinds by their names, and lists which groups'
replicas touch a qubit set that a later acquisition flagged. It also tabulates
the ripple walk readout controls, which compile from the shared symbolic walk
template and execute its full CZ scaffold although their bound angles make
them logically the identity, and the per-replica zero-divisor fringe fit.

The output (docs/evidence/walk-control-scaffolding/exposure.json) is
descriptive: an overlap marks a run whose result may carry a flagged qubit's
defect, not a demonstrated effect. --check re-derives it and compares keys,
strings and integers exactly and floats to 1e-9.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Any

from qiskit import qpy

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "results/live/qpu-job-retention-audit.json"
OUTPUT = ROOT / "docs/evidence/walk-control-scaffolding/exposure.json"
FRINGE_RUN = "results/live/2026-10-15T070853.550532Z"
PILOT_RUN = "results/live/2026-10-11T152922.787095Z"
PILOT_MEMBER = "hybrid_shor_N15_a2"
# Qubit sets a measurement flagged, with the claim that carries the flag.
FLAGS: dict[str, dict[str, dict[str, Any]]] = {
    "ibm_kingston": {
        "readout_fault": {"qubits": [0, 1], "claim": "hw-corner-readout-fault"},
        "short_relaxation": {"qubits": [2, 3, 16], "claim": "hw-corner-readout-fault"},
        "first_bit_correlation": {"qubits": [79], "claim": "hw-first-bit-disagreement"},
    },
    "ibm_fez": {
        "rank_weak_sector": {"qubits": [2, 3, 4, 16], "claim": "hw-rank-endpoint-decomposition"},
        "walk_lane0_tile": {"qubits": [1, 2, 3, 4], "claim": "hw-fez-walk-control-discrepancy"},
    },
}


def member_kind(name: str) -> str:
    return re.sub(r"lane\d+|_t\d+d\d+|\d+", "#", name)


def runs() -> list[str]:
    jobs = json.loads(AUDIT.read_text())["jobs"]
    return sorted({job["run"] for job in jobs if (ROOT / job["run"] / "record.json").is_file()})


def run_exposure(run: str) -> dict[str, Any]:
    record = json.loads((ROOT / run / "record.json").read_text())
    with (ROOT / run / "isa.qpy").open("rb") as stream:
        circuits = qpy.load(stream)
    pubs = record["execution_pubs"]
    if len(circuits) != len(pubs):
        raise ValueError(f"{run}: {len(circuits)} circuits for {len(pubs)} PUBs")
    kinds: dict[str, list[int]] = {}
    member_cz: dict[str, int] = {}
    for circuit, pub in zip(circuits, pubs, strict=True):
        pairs = [
            {circuit.find_bit(qubit).index for qubit in instruction.qubits}
            for instruction in circuit.data
            if instruction.operation.name == "cz"
        ]
        for component in pub["components"]:
            qubits = set(component["physical_qubits"])
            inside = sum(1 for pair in pairs if pair <= qubits)
            if any(len(pair & qubits) == 1 for pair in pairs):
                raise ValueError(f"{run}: a CZ crosses the boundary of {component['member']}")
            kinds.setdefault(member_kind(component["member"]), []).append(inside)
            member_cz[component["member"]] = inside
    groups = []
    for group in record["groups"]:
        backend = group["backend"]
        replicas = [sorted(replica["physical_qubits"]) for replica in group["replicas"]]
        flagged = {}
        for flag, spec in FLAGS.get(backend, {}).items():
            touched = [sorted(set(replica) & set(spec["qubits"])) for replica in replicas]
            if any(touched):
                flagged[flag] = touched
        groups.append({"group": group["group"], "backend": backend, "replicas": replicas, "flagged": flagged})
    return {
        "run": run,
        "groups": groups,
        "member_kinds": {
            kind: {
                "members": len(values),
                "cz_min": min(values),
                "cz_median": statistics.median_low(values),
                "cz_max": max(values),
            }
            for kind, values in sorted(kinds.items())
        },
        "member_cz": member_cz,
    }


def walk_readouts(exposures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Walk readout controls: hardware and calibrated-replay P(0000) against their executed CZ load."""
    rows = []
    for exposure in exposures:
        run = exposure["run"]
        if not any(group["group"].startswith("ripple_walk") for group in exposure["groups"]):
            continue
        collection = json.loads((ROOT / run / "collect.json").read_text())
        measurements = collection[0]["family_measurements"]
        record = json.loads((ROOT / run / "record.json").read_text())
        backend = record["groups"][0]["backend"]
        for pub in record["execution_pubs"]:
            for component in pub["components"]:
                member = component["member"]
                if not re.fullmatch(r"ripple_walk_lane\d+_readout0", member):
                    continue
                hardware = float(measurements[member]["replica_probabilities"][0][0])
                replay = float(measurements[member]["replayed_replica_probabilities"][0][0])
                cz = exposure["member_cz"][member]
                rows.append(
                    {
                        "run": run,
                        "backend": backend,
                        "member": member,
                        "qubits": sorted(component["physical_qubits"]),
                        "cz": cz,
                        "hardware_p0000": hardware,
                        "replay_p0000": replay,
                        "hardware_retention_per_cz": hardware ** (1.0 / cz),
                        "replay_retention_per_cz": replay ** (1.0 / cz),
                    }
                )
    return rows


def fringe_replicas() -> list[dict[str, Any]]:
    record = json.loads((ROOT / FRINGE_RUN / "record.json").read_text())
    collection = json.loads((ROOT / FRINGE_RUN / "collect.json").read_text())
    entry = next(item for item in collection if item.get("group") == "zero_divisor_fringe")
    group = next(item for item in record["groups"] if item["group"] == "zero_divisor_fringe")
    return [
        {
            "qubits": sorted(replica["physical_qubits"]),
            "visibility": summary["visibility"],
            "phase": summary["phase"],
            "p0_dark": summary["p0_dark"],
        }
        for replica, summary in zip(group["replicas"], entry["measured_statistics"]["summary_per_replica"], strict=True)
    ]


def pilot_bit_marginals() -> list[dict[str, Any]]:
    """P(bit = 1) of every measured output bit of every pilot replica, with the qubit that wrote it.

    The replicas share one ideal law, so a replica whose bit departs from the
    others carries a readout or state fault on that bit's qubit.
    """
    record = json.loads((ROOT / PILOT_RUN / "record.json").read_text())
    collection = json.loads((ROOT / PILOT_RUN / "collect.json").read_text())
    entry = next(item for item in collection if isinstance(item, dict) and item.get("group") == "hybrid_shor_mod15")
    with (ROOT / PILOT_RUN / "isa.qpy").open("rb") as stream:
        circuits = qpy.load(stream)
    for circuit, pub in zip(circuits, record["execution_pubs"], strict=True):
        component = next((item for item in pub["components"] if item["member"] == PILOT_MEMBER), None)
        if component is None:
            continue
        writer = {}
        for instruction in circuit.data:
            if instruction.operation.name == "measure":
                clbit = instruction.clbits[0]
                register = next(reg for reg in circuit.cregs if clbit in reg)
                writer[(register.name, list(register).index(clbit))] = circuit.find_bit(instruction.qubits[0]).index
        rows = []
        for replica, names in enumerate(component["registers_by_replica"]):
            distribution = entry["measured"][PILOT_MEMBER][replica]
            for (register, bit), qubit in sorted(writer.items()):
                if register == names[0]:
                    marginal = sum(value for outcome, value in enumerate(distribution) if outcome >> bit & 1)
                    rows.append({"replica": replica, "bit": bit, "qubit": qubit, "p_one": float(marginal)})
        return rows
    raise ValueError(f"{PILOT_MEMBER} is not in {PILOT_RUN}")


def evidence() -> dict[str, Any]:
    exposures = [run_exposure(run) for run in runs()]
    phases = [row["phase"] for row in fringe_replicas()]
    return {
        "schema": "scaffolding-exposure-v1",
        "flags": FLAGS,
        "runs": [{key: value for key, value in exposure.items() if key != "member_cz"} for exposure in exposures],
        "walk_readout_controls": walk_readouts(exposures),
        "fringe_replicas": fringe_replicas(),
        "pilot_bit_marginals": pilot_bit_marginals(),
        "fringe_phase_spread": {"min": min(phases), "max": max(phases), "stdev": statistics.stdev(phases)},
    }


def _matches(retained: Any, derived: Any, where: str = "$") -> list[str]:
    if isinstance(retained, dict) and isinstance(derived, dict):
        if retained.keys() != derived.keys():
            return [f"{where}: keys differ"]
        return [problem for key in retained for problem in _matches(retained[key], derived[key], f"{where}.{key}")]
    if isinstance(retained, list) and isinstance(derived, list):
        if len(retained) != len(derived):
            return [f"{where}: length differs"]
        pairs = zip(retained, derived, strict=True)
        return [problem for index, pair in enumerate(pairs) for problem in _matches(*pair, f"{where}[{index}]")]
    if isinstance(retained, float) or isinstance(derived, float):
        same = math.isclose(float(retained), float(derived), rel_tol=1e-9, abs_tol=1e-12)
        return [] if same else [f"{where}: {retained} != {derived}"]
    return [] if retained == derived else [f"{where}: {retained!r} != {derived!r}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    data = evidence()
    if arguments.write:
        OUTPUT.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
        return 0
    problems = _matches(json.loads(OUTPUT.read_text()), data)
    if problems:
        print("scaffolding exposure: retained evidence differs:", *problems[:20], sep="\n  ", file=sys.stderr)
        return 1
    print(f"scaffolding exposure: {len(data['runs'])} runs, {len(data['walk_readout_controls'])} walk readout controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
