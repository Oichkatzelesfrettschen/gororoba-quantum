"""Snapshot of the Heron Targets the account reaches, and the docs/notes/ibm_heron_platform.md facts derived from them.

--out FILE (local, network, reads only) lists the account's hardware backends through
QiskitRuntimeService and reads each one twice, plainly and with
use_fractional_gates=True. It writes the backend version and processor type
the configuration reports, calibration stamp, dt, timing constraints,
repetition-delay default and range, basis gates, supported instructions,
per-qubit durations and errors of the instructions in INSTRUCTIONS and
FRACTIONAL, and a transpile probe that counts xslow in a
circuit of X, SX, RX and CX gates at optimization levels 1 to 3. A snapshot
also carries the configuration limits and features, the service status,
the vendor's faulty qubit and gate lists, per-qubit T1, T2 and readout
assignment values (calibration_values), the CZ coupling graph, order
statistics (summary), the health block (dead qubits and couplers, usable
components) and the account's usage (instance only as the first 12 hex digits
of the SHA-256 of its CRN). No credential or account identifier enters the file.

--check FILE... (CI, offline) takes each snapshot in turn; targets.json, read 2026-10-14, predates the
calibration blocks and carries the facts only. Each check requires the snapshot's backends to be exactly
ROSTER, recomputes every fact from the retained per-qubit values, requires each to hold on every backend, and
requires the retained "facts" block to equal the recomputation, so a refreshed snapshot that contradicts
docs/notes/ibm_heron_platform.md fails until the text changes with it. Where the calibration blocks are
present, it also recomputes summary, coupling and health and verifies the dead-error gap. Each backend's
backend_version, when present, is a nonempty string and its processor_type a string dictionary with family and
revision; a snapshot without backend_version passes.

Usage: "$PYTHON" scripts/heron_target_snapshot.py (--out FILE | --check FILE [FILE ...])
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
FRACTIONAL = ("rzz", "rx", "cz", "sx")
TIMING = {"granularity": 1, "min_length": 2, "pulse_alignment": 1, "acquire_alignment": 1}
BASIS = ["cz", "id", "rz", "sx", "x", "xslow"]
# The backends the Execution facts section of docs/notes/ibm_heron_platform.md names; a refreshed
# snapshot with another roster fails until the section and this tuple change together.
ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
# rzz reports its own error, not the cz value, on more than this fraction of pairs.
RZZ_OWN_ERROR_FRACTION = 0.9
# A coupler counts as high-error when its CZ error exceeds this multiple of the backend median.
HIGH_ERROR_FACTOR = 3.0
# The Target reports exactly this error for a qubit or coupler that calibration could not fit. The vendor's
# own lists (BackendProperties.faulty_qubits and faulty_gates, which read the "operational" flags) read empty
# on all three backends while the Target carries these values, so the repository counts a reported error equal
# to the sentinel as dead (our rule, not IBM's flag), and the check requires every other sx and cz error to lie
# below SENTINEL_GAP_CEILING, the measured gap, so a refreshed read with intermediate values fails until
# the rule is rejustified.
DEAD_ERROR_SENTINEL = 1.0
SENTINEL_GAP_CEILING = 0.5
STAT_KEYS = ("n", "min", "p10", "median", "mean", "p90", "max")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def table(target: Any, name: str) -> dict[str, list[Any]]:
    """Per-qargs duration and error of one Target instruction, ordered by qargs."""
    rows = sorted((tuple(q), p) for q, p in target[name].items() if p is not None)
    return {
        "qargs": [list(q) for q, _ in rows],
        "duration": [p.duration for _, p in rows],
        "error": [p.error for _, p in rows],
    }


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
    cal = backend["calibration_values"]
    ins = backend["instructions"]
    return {
        "t1_us": stats([v * 1e6 for v in cal["t1"] if v is not None]),
        "t2_us": stats([v * 1e6 for v in cal["t2"] if v is not None]),
        "readout_error": stats(ins["measure"]["error"]),
        "sx_error": stats(ins["sx"]["error"]),
        "cz_error": stats(ins["cz"]["error"]),
        "cz_duration_ns": stats([v * 1e9 for v in ins["cz"]["duration"]]),
        "measure_2_error": stats(ins["measure_2"]["error"]),
        "measure_duration_ns": stats([v * 1e9 for v in ins["measure"]["duration"]]),
        "measure_2_duration_ns": stats([v * 1e9 for v in ins["measure_2"]["duration"]]),
        "sx_duration_ns": stats([v * 1e9 for v in ins["sx"]["duration"]]),
    }


def health(backend: dict[str, Any]) -> dict[str, Any]:
    """Dead qubits and couplers, and the usable-graph components.

    A qubit is dead when the vendor lists it faulty, its sx error equals DEAD_ERROR_SENTINEL, or the
    calibration reports no T1 or T2; a coupler is dead when the vendor lists a cz on it faulty or its cz error
    equals the sentinel. The largest error below the sentinel is retained so the check can verify the gap.
    """
    ins = backend["instructions"]
    cal = backend["calibration_values"]
    n = backend["num_qubits"]
    sx = {q[0]: e for q, e in zip(ins["sx"]["qargs"], ins["sx"]["error"], strict=True)}
    errors = {tuple(sorted(q)): e for q, e in zip(ins["cz"]["qargs"], ins["cz"]["error"], strict=True)}
    vendor_gates = {tuple(sorted(q)) for gate, q in backend["faulty_gates"] if gate == "cz"}
    dead_qubits = sorted(
        {q for q in range(n) if sx[q] >= DEAD_ERROR_SENTINEL or cal["t1"][q] is None or cal["t2"][q] is None}
        | set(backend["faulty_qubits"])
    )
    dead_couplers = sorted(list(k) for k, e in errors.items() if e >= DEAD_ERROR_SENTINEL or k in vendor_gates)
    dead_pairs = {tuple(p) for p in dead_couplers}
    live = {k for k in errors if k not in dead_pairs and k[0] not in dead_qubits and k[1] not in dead_qubits}
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
        "dead_error_sentinel": DEAD_ERROR_SENTINEL,
        "vendor_faulty_qubits": sorted(backend["faulty_qubits"]),
        "vendor_faulty_gates": sorted(backend["faulty_gates"]),
        "largest_sx_error_below_sentinel": max((e for e in sx.values() if e < DEAD_ERROR_SENTINEL), default=0.0),
        "largest_cz_error_below_sentinel": max((e for e in errors.values() if e < DEAD_ERROR_SENTINEL), default=0.0),
        "dead_qubits": dead_qubits,
        "dead_couplers": dead_couplers,
        "healthy_qubits": n - len(dead_qubits),
        "usable_couplers": len(live),
        "component_sizes": sorted(sizes, reverse=True),
        "readout_error_at_least_0.1": sorted(q for q, e in readout.items() if e >= 0.1),
        "cz_error_at_least_0.05": sorted(list(k) for k, e in errors.items() if e >= 0.05),
    }


def probe(backend: Any) -> dict[str, int]:
    from qiskit import QuantumCircuit, transpile

    circuit = QuantumCircuit(5)
    for _ in range(6):
        for q in range(5):
            circuit.x(q)
        for q in range(4):
            circuit.cx(q, q + 1)
        for q in range(5):
            circuit.sx(q)
            circuit.rx(0.3, q)
    circuit.measure_all()
    return {
        str(level): int(
            transpile(circuit, backend=backend, optimization_level=level, seed_transpiler=7).count_ops().get("xslow", 0)
        )
        for level in (1, 2, 3)
    }


def snapshot() -> dict[str, Any]:
    import qiskit
    import qiskit_ibm_runtime
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = ibm_account.open_service(QiskitRuntimeService)
    names = sorted(b.name for b in service.backends(simulator=False))
    fractional = sorted(b.name for b in service.backends(simulator=False, use_fractional_gates=True))
    backends = {}
    for name in names:
        plain = service.backend(name)
        frac = service.backend(name, use_fractional_gates=True)
        config = plain.configuration()
        target = plain.target
        constraints = target.timing_constraints()
        properties = plain.properties()
        status = plain.status()
        qubits = range(config.n_qubits)
        t1 = [prop(properties, q, "T1") for q in qubits]
        t2 = [prop(properties, q, "T2") for q in qubits]
        backends[name] = {
            "backend_version": config.backend_version,
            "processor_type": config.processor_type,
            "num_qubits": config.n_qubits,
            "calibration": plain.properties().last_update_date.isoformat(),
            "dt": target.dt,
            "timing_constraints": {k: getattr(constraints, k) for k in TIMING},
            "default_rep_delay": config.default_rep_delay,
            "rep_delay_range": list(config.rep_delay_range),
            "basis_gates": sorted(config.basis_gates),
            "supported_instructions": sorted(config.supported_instructions),
            "instructions": {op: table(target, op) for op in INSTRUCTIONS if op in target.operation_names},
            "fractional_instructions": {op: table(frac.target, op) for op in FRACTIONAL},
            "xslow_in_transpiled_probe": probe(plain),
            "limits": {
                "max_shots": config.max_shots,
                "max_experiments": config.max_experiments,
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
                "target_operations": sorted(target.operation_names),
                "fractional_operations": sorted(frac.target.operation_names),
            },
            "status": {
                "operational": status.operational,
                "pending_jobs": status.pending_jobs,
                "message": status.status_msg,
            },
            # BackendProperties.is_qubit_operational and is_gate_operational answer True where the property is
            # absent, so an empty faulty list is informative only with the count of rows that carry the flag.
            "operational_property_rows": {
                "qubits": sum(1 for q in qubits if "operational" in properties.qubit_property(q)),
                "gates": sum(
                    1 for g in properties.gates if "operational" in properties.gate_property(g.gate, g.qubits)
                ),
            },
            "faulty_qubits": sorted(int(q) for q in properties.faulty_qubits()),
            "faulty_gates": sorted([g.gate, [int(q) for q in g.qubits]] for g in properties.faulty_gates()),
            "calibration_values": {
                "t1": t1,
                "t2": t2,
                "frequency_hz": [prop(properties, q, "frequency") for q in qubits],
                "missing_t1": [q for q in qubits if t1[q] is None],
                "missing_t2": [q for q in qubits if t2[q] is None],
                "prob_meas0_prep1": [prop(properties, q, "prob_meas0_prep1") for q in qubits],
                "prob_meas1_prep0": [prop(properties, q, "prob_meas1_prep0") for q in qubits],
            },
        }
        backends[name]["coupling"] = coupling(backends[name]["instructions"]["cz"])
        backends[name]["summary"] = summarize(backends[name])
        backends[name]["health"] = health(backends[name])
    usage = service.usage()
    data = {
        "usage": {
            "instance_sha256_12": hashlib.sha256(str(usage["instance_id"]).encode()).hexdigest()[:12],
            "consumed_seconds": usage["usage_consumed_seconds"],
            "limit_seconds": usage["usage_limit_seconds"],
            "remaining_seconds": usage["usage_remaining_seconds"],
            "period": usage["usage_period"],
        },
        "retrieved": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
        "versions": {"qiskit": qiskit.__version__, "qiskit-ibm-runtime": qiskit_ibm_runtime.__version__},
        "accessible_backends": names,
        "fractional_backends": fractional,
        "backends": backends,
    }
    data["facts"] = facts(data)
    return data


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def matching(a: dict[str, list[Any]], b: dict[str, list[Any]]) -> tuple[int, int]:
    """Count of qargs where a's error equals b's, and a's qargs count."""
    errors = {tuple(q): e for q, e in zip(b["qargs"], b["error"], strict=True)}
    same = sum(1 for q, e in zip(a["qargs"], a["error"], strict=True) if errors.get(tuple(q)) == e)
    return same, len(a["qargs"])


def facts(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Each docs/notes/ibm_heron_platform.md Heron fact, evaluated per backend from the retained values."""
    out: dict[str, dict[str, Any]] = {}
    for name, b in sorted(data["backends"].items()):
        ins, frac = b["instructions"], b["fractional_instructions"]
        xslow_x, n_xslow = matching(ins["xslow"], ins["x"])
        xslow_sx, _ = matching(ins["xslow"], ins["sx"])
        rx_sx, n_rx = matching(frac["rx"], frac["sx"])
        rzz_cz, n_rzz = matching(frac["rzz"], frac["cz"])
        out[name] = {
            "heron_r2_156": b["processor_type"] == {"family": "Heron", "revision": "2"} and b["num_qubits"] == 156,
            "dt_4ns": b["dt"] == 4e-9,
            "alignment_1": b["timing_constraints"] == TIMING,
            "rep_delay_default_250us": b["default_rep_delay"] == 250e-6,
            "rep_delay_range_0_to_2ms": b["rep_delay_range"] == [0.0, 0.002],
            "basis": b["basis_gates"] == BASIS,
            "store_supported": "store" in b["supported_instructions"],
            "measure_2_shorter": median(ins["measure_2"]["duration"]) < median(ins["measure"]["duration"]),
            "measure_2_higher_error": median(ins["measure_2"]["error"]) > median(ins["measure"]["error"]),
            "reset_lasts_as_long_as_measure_reset": ins["reset"]["duration"] == ins["measure_reset"]["duration"]
            and ins["reset_2"]["duration"] == ins["measure_reset_2"]["duration"]
            and ins["reset"]["qargs"] == ins["measure_reset"]["qargs"],
            "xslow_1us": set(ins["xslow"]["duration"]) == {1e-6},
            "xslow_error_shared_with_x_and_sx": xslow_x == xslow_sx == n_xslow,
            "xslow_not_emitted_by_transpiler": set(b["xslow_in_transpiled_probe"].values()) == {0},
            "rx_error_copies_sx": rx_sx == n_rx,
            "rzz_own_error_on_most_pairs": (n_rzz - rzz_cz) > RZZ_OWN_ERROR_FRACTION * n_rzz,
            "fractional_supported": name in data["fractional_backends"],
        }
        if "health" in b:
            # measure_2 against measure is a calibration-dependent comparison (higher on all three at 2026-10-14,
            # lower on two at 2026-11-28); a snapshot with the calibration blocks reports it in summary.
            out[name].pop("measure_2_higher_error")
    return out


def check_calibration(name: str, b: dict[str, Any]) -> None:
    """Recompute summary, coupling and health from the retained values and verify the sentinel gap."""
    require(b["summary"] == summarize(b), f"{name}: retained summary differs from the recomputation")
    for key in ("t1", "t2", "frequency_hz"):
        require(len(b["calibration_values"][key]) == b["num_qubits"], f"{name}: {key} length")
    require(b["health"] == health(b), f"{name}: retained health differs from the recomputation")
    require(all(set(STAT_KEYS) == set(v) for v in b["summary"].values()), f"{name}: summary keys")
    require(b["coupling"] == coupling(b["instructions"]["cz"]), f"{name}: retained coupling differs from the CZ rows")
    require(max(int(d) for d in b["coupling"]["degree_histogram"]) <= 3, f"{name}: a qubit has more than 3 couplers")
    for gate in ("sx", "cz"):
        value = b["health"][f"largest_{gate}_error_below_sentinel"]
        require(value < SENTINEL_GAP_CEILING, f"{name}: {gate} error {value} below the sentinel breaks the gap")


def check(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data["accessible_backends"] == sorted(data["backends"]), "backend list and tables differ")
    require(
        data["accessible_backends"] == list(ROSTER) and data["fractional_backends"] == list(ROSTER),
        f"snapshot roster {data['accessible_backends']} differs from the documented {list(ROSTER)}",
    )
    for name, b in sorted(data["backends"].items()):
        if "backend_version" in b:
            version = b["backend_version"]
            require(isinstance(version, str) and bool(version), f"{name}: backend_version {version!r}")
        processor = b["processor_type"]
        require(
            isinstance(processor, dict)
            and {"family", "revision"} <= set(processor)
            and all(isinstance(v, str) for v in processor.values()),
            f"{name}: processor_type {processor!r}",
        )
    for name, b in sorted(data["backends"].items()):
        if "health" in b:
            check_calibration(name, b)
    recomputed = facts(data)
    require(data["facts"] == recomputed, "retained facts differ from the recomputation")
    failing = [f"{name}:{fact}" for name, values in recomputed.items() for fact, holds in values.items() if not holds]
    require(not failing, f"facts that no longer hold: {failing}")
    print(f"heron facts: {len(next(iter(recomputed.values())))} facts hold on {', '.join(recomputed)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="read the live Targets and write the snapshot")
    mode.add_argument("--check", type=Path, nargs="+", help="recompute every fact from each retained snapshot")
    args = parser.parse_args(argv)
    if args.out:
        args.out.write_text(json.dumps(snapshot(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        check(args.out)
    else:
        for path in args.check:
            check(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
