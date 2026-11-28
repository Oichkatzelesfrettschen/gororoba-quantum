"""Read-only capability snapshot of the Heron backends the account reaches.

--out FILE (local, network) lists the account's hardware backends through QiskitRuntimeService and writes, per
backend: the configuration limits (qubits, max_shots, max_experiments, supported_features, repetition delay),
the Target's gate durations and errors, the calibration distributions of T1, T2, readout, sx and cz, the
heavy-hex coupling graph with its faulty and high-error couplers, the dynamic-circuit and fractional-gate
instruction support, the queue length and the account usage. No job is created; every call is a read. The IBM Cloud
instance enters the file only as the first 12 hex digits of the SHA-256 of its CRN.

--check FILE (offline) requires the structure --out writes and recomputes the summary statistics from the retained
values.

Usage: "$PYTHON" scripts/ibm_machine_capabilities.py (--out FILE | --check FILE)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
import ibm_account  # noqa: E402

ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
INSTRUCTIONS = (
    "measure",
    "measure_2",
    "measure_reset",
    "measure_reset_2",
    "reset",
    "reset_2",
    "x",
    "sx",
    "xslow",
    "cz",
    "id",
)
FRACTIONAL = ("rzz", "rx")
# A coupler counts as high-error when its CZ error exceeds this multiple of the backend median.
HIGH_ERROR_FACTOR = 3.0
# A qubit or coupler whose reported error reaches this value is unusable (the Target reports 1.0 for a dead one).
DEAD_ERROR = 0.5
STAT_KEYS = ("n", "min", "p10", "median", "mean", "p90", "max")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def stats(values: list[float]) -> dict[str, float]:
    """Order statistics of a nonempty list; p10 and p90 use the nearest rank."""
    ordered = sorted(values)
    count = len(ordered)
    return {
        "n": float(count),
        "min": ordered[0],
        "p10": ordered[min(count - 1, int(0.1 * count))],
        "median": float(statistics.median(ordered)),
        "mean": float(statistics.fmean(ordered)),
        "p90": ordered[min(count - 1, int(0.9 * count))],
        "max": ordered[-1],
    }


def degree_histogram(edges: list[list[int]]) -> dict[str, int]:
    degree: dict[int, int] = {}
    for a, b in edges:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    histogram: dict[str, int] = {}
    for d in degree.values():
        histogram[str(d)] = histogram.get(str(d), 0) + 1
    return dict(sorted(histogram.items()))


def prop(properties: Any, qubit: int, name: str) -> float | None:
    """A qubit property, or None where the calibration omits it (a qubit that reports no value)."""
    try:
        return float(properties.qubit_property(qubit, name)[0])
    except Exception:
        return None


def instruction_rows(target: Any, name: str) -> dict[str, Any]:
    rows = sorted((tuple(q), p) for q, p in target[name].items() if p is not None)
    return {
        "qargs": [list(q) for q, _ in rows],
        "duration": [p.duration for _, p in rows],
        "error": [p.error for _, p in rows],
    }


def coupling(cz: dict[str, Any]) -> dict[str, Any]:
    """Undirected CZ graph, its degree histogram and the couplers above HIGH_ERROR_FACTOR times the median error."""
    edges = sorted({tuple(sorted(q)) for q in cz["qargs"]})
    errors = {tuple(sorted(q)): e for q, e in zip(cz["qargs"], cz["error"], strict=True)}
    median = statistics.median(errors.values())
    high = sorted((list(k), v) for k, v in errors.items() if v > HIGH_ERROR_FACTOR * median)
    return {
        "edges": [list(e) for e in edges],
        "degree_histogram": degree_histogram([list(e) for e in edges]),
        "high_error_threshold": HIGH_ERROR_FACTOR * median,
        "high_error_couplers": [{"pair": p, "error": v} for p, v in high],
    }


def summarize(backend: dict[str, Any]) -> dict[str, Any]:
    """Distributions recomputed from the retained per-qubit and per-pair values."""
    cal = backend["calibration"]
    ins = backend["instructions"]
    return {
        "t1_us": stats([v * 1e6 for v in cal["t1"] if v is not None]),
        "t2_us": stats([v * 1e6 for v in cal["t2"] if v is not None]),
        "readout_error": stats(ins["measure"]["error"]),
        "sx_error": stats(ins["sx"]["error"]),
        "cz_error": stats(ins["cz"]["error"]),
        "cz_duration_ns": stats([v * 1e9 for v in ins["cz"]["duration"]]),
        "measure_duration_ns": stats([v * 1e9 for v in ins["measure"]["duration"]]),
        "measure_2_duration_ns": stats([v * 1e9 for v in ins["measure_2"]["duration"]]),
        "sx_duration_ns": stats([v * 1e9 for v in ins["sx"]["duration"]]),
    }


def health(backend: dict[str, Any]) -> dict[str, Any]:
    """Dead qubits (sx error at or above DEAD_ERROR, or no T1 or T2), dead couplers and usable-graph components."""
    ins = backend["instructions"]
    cal = backend["calibration"]
    n = backend["num_qubits"]
    sx = {q[0]: e for q, e in zip(ins["sx"]["qargs"], ins["sx"]["error"], strict=True)}
    dead_qubits = sorted(q for q in range(n) if sx[q] >= DEAD_ERROR or cal["t1"][q] is None or cal["t2"][q] is None)
    errors = {tuple(sorted(q)): e for q, e in zip(ins["cz"]["qargs"], ins["cz"]["error"], strict=True)}
    dead_couplers = sorted(list(k) for k, e in errors.items() if e >= DEAD_ERROR)
    live = {k for k, e in errors.items() if e < DEAD_ERROR and k[0] not in dead_qubits and k[1] not in dead_qubits}
    neighbors: dict[int, list[int]] = {q: [] for q in range(n) if q not in dead_qubits}
    for a, b in live:
        neighbors[a].append(b)
        neighbors[b].append(a)
    seen: set[int] = set()
    sizes: list[int] = []
    for start in neighbors:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        size = 0
        while stack:
            q = stack.pop()
            size += 1
            for r in neighbors[q]:
                if r not in seen:
                    seen.add(r)
                    stack.append(r)
        sizes.append(size)
    readout = {q[0]: e for q, e in zip(ins["measure"]["qargs"], ins["measure"]["error"], strict=True)}
    return {
        "dead_error_threshold": DEAD_ERROR,
        "dead_qubits": dead_qubits,
        "dead_couplers": dead_couplers,
        "healthy_qubits": n - len(dead_qubits),
        "usable_couplers": len(live),
        "component_sizes": sorted(sizes, reverse=True),
        "readout_error_at_least_0.1": sorted(q for q, e in readout.items() if e >= 0.1),
        "cz_error_at_least_0.05": sorted(list(k) for k, e in errors.items() if e >= 0.05),
    }


def snapshot() -> dict[str, Any]:
    import qiskit
    import qiskit_ibm_runtime
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = ibm_account.open_service(QiskitRuntimeService)
    names = sorted(b.name for b in service.backends(simulator=False))
    backends: dict[str, Any] = {}
    for name in names:
        plain = service.backend(name)
        frac = service.backend(name, use_fractional_gates=True)
        config = plain.configuration()
        properties = plain.properties()
        target = plain.target
        status = plain.status()
        qubits = range(config.n_qubits)
        t1 = [prop(properties, q, "T1") for q in qubits]
        t2 = [prop(properties, q, "T2") for q in qubits]
        faulty_qubits = sorted(int(q) for q in properties.faulty_qubits())
        faulty_gates = sorted([g.gate, [int(q) for q in g.qubits]] for g in properties.faulty_gates())
        ins = {op: instruction_rows(target, op) for op in INSTRUCTIONS if op in target.operation_names}
        backends[name] = {
            "backend_version": config.backend_version,
            "processor_type": config.processor_type,
            "num_qubits": config.n_qubits,
            "calibration_stamp": properties.last_update_date.isoformat(),
            "dt_s": target.dt,
            "limits": {
                "max_shots": config.max_shots,
                "max_experiments": config.max_experiments,
                "rep_delay_range_reported": list(config.rep_delay_range),
                "default_rep_delay_reported": config.default_rep_delay,
                "clops_h": config.clops_h,
                "mcps": getattr(config, "mcps", None),
            },
            "features": {
                "supported_features": sorted(config.supported_features),
                "dynamic_reprate_enabled": config.dynamic_reprate_enabled,
                "multi_meas_enabled": config.multi_meas_enabled,
                "measure_esp_enabled": config.measure_esp_enabled,
                "conditional": config.conditional,
                "open_pulse": config.open_pulse,
                "basis_gates": sorted(config.basis_gates),
                "supported_instructions": sorted(config.supported_instructions),
                "target_operations": sorted(target.operation_names),
                "fractional_operations": sorted(frac.target.operation_names),
            },
            "status": {
                "operational": status.operational,
                "pending_jobs": status.pending_jobs,
                "message": status.status_msg,
            },
            "faulty_qubits": faulty_qubits,
            "faulty_gates": faulty_gates,
            "calibration": {
                "t1": t1,
                "t2": t2,
                "frequency_hz": [prop(properties, q, "frequency") for q in qubits],
                "missing_t1": [q for q in qubits if t1[q] is None],
                "missing_t2": [q for q in qubits if t2[q] is None],
                "prob_meas0_prep1": [prop(properties, q, "prob_meas0_prep1") for q in qubits],
                "prob_meas1_prep0": [prop(properties, q, "prob_meas1_prep0") for q in qubits],
            },
            "instructions": ins,
            "fractional_instructions": {op: instruction_rows(frac.target, op) for op in FRACTIONAL},
            "coupling": coupling(ins["cz"]),
        }
        backends[name]["summary"] = summarize(backends[name])
        backends[name]["health"] = health(backends[name])
    usage = service.usage()
    return {
        "retrieved": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
        "versions": {"qiskit": qiskit.__version__, "qiskit-ibm-runtime": qiskit_ibm_runtime.__version__},
        "usage": {
            "instance_sha256_12": hashlib.sha256(str(usage["instance_id"]).encode()).hexdigest()[:12],
            "consumed_seconds": usage["usage_consumed_seconds"],
            "limit_seconds": usage["usage_limit_seconds"],
            "remaining_seconds": usage["usage_remaining_seconds"],
            "period": usage["usage_period"],
        },
        "backends": backends,
    }


def check(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(sorted(data["backends"]) == list(ROSTER), f"roster {sorted(data['backends'])} differs from {list(ROSTER)}")
    for name, b in sorted(data["backends"].items()):
        require(b["summary"] == summarize(b), f"{name}: retained summary differs from the recomputation")
        for key in ("t1", "t2", "frequency_hz"):
            require(len(b["calibration"][key]) == b["num_qubits"], f"{name}: {key} length")
        require(b["health"] == health(b), f"{name}: retained health differs from the recomputation")
        require(all(set(STAT_KEYS) == set(v) for v in b["summary"].values()), f"{name}: summary keys")
        cz = b["instructions"]["cz"]
        require(b["coupling"] == coupling(cz), f"{name}: retained coupling differs from the CZ rows")
        require(
            max(int(d) for d in b["coupling"]["degree_histogram"]) <= 3, f"{name}: a qubit has more than 3 couplers"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.out:
        args.out.write_text(json.dumps(snapshot(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        check(args.out)
        print(f"wrote {args.out}")
    else:
        check(args.check)
        print(f"ok {args.check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
