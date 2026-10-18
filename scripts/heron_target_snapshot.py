"""Snapshot of the Heron Targets the account reaches, and the AGENTS.md facts derived from them.

--out FILE (local, network) lists the account's hardware backends through
QiskitRuntimeService and reads each one twice, plainly and with
use_fractional_gates=True. It writes the backend version and processor type
the configuration reports, calibration stamp, dt, timing constraints,
repetition-delay default and range, basis gates, supported instructions,
per-qubit durations and errors of the instructions in INSTRUCTIONS and
FRACTIONAL, and a transpile probe that counts xslow in a
circuit of X, SX, RX and CX gates at optimization levels 1 to 3. No
credential, instance or account identifier enters the file.

--check FILE (CI, offline) requires the snapshot's backends to be exactly
ROSTER, recomputes every fact from the retained per-qubit values, requires
each to hold on every backend, and requires the retained "facts" block to
equal the recomputation, so a refreshed snapshot that contradicts AGENTS.md
fails until the text changes with it. Each backend's backend_version, when
present, is a nonempty string and its processor_type a string dictionary with
family and revision; a snapshot without backend_version passes.

Usage: "$PYTHON" scripts/heron_target_snapshot.py (--out FILE | --check FILE)
"""

from __future__ import annotations

import argparse
import datetime
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
)
FRACTIONAL = ("rzz", "rx", "cz", "sx")
TIMING = {"granularity": 1, "min_length": 2, "pulse_alignment": 1, "acquire_alignment": 1}
BASIS = ["cz", "id", "rz", "sx", "x", "xslow"]
# The backends the Heron execution facts section of AGENTS.md names; a refreshed
# snapshot with another roster fails until the section and this tuple change together.
ROSTER = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
# rzz reports its own error, not the cz value, on more than this fraction of pairs.
RZZ_OWN_ERROR_FRACTION = 0.9


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
            "instructions": {op: table(target, op) for op in INSTRUCTIONS},
            "fractional_instructions": {op: table(frac.target, op) for op in FRACTIONAL},
            "xslow_in_transpiled_probe": probe(plain),
        }
    data = {
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
    """Each AGENTS.md Heron fact, evaluated per backend from the retained values."""
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
    return out


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
    recomputed = facts(data)
    require(data["facts"] == recomputed, "retained facts differ from the recomputation")
    failing = [f"{name}:{fact}" for name, values in recomputed.items() for fact, holds in values.items() if not holds]
    require(not failing, f"facts that no longer hold: {failing}")
    print(f"heron facts: {len(next(iter(recomputed.values())))} facts hold on {', '.join(recomputed)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="read the live Targets and write the snapshot")
    mode.add_argument("--check", type=Path, help="recompute every fact from a retained snapshot")
    args = parser.parse_args(argv)
    if args.out:
        args.out.write_text(json.dumps(snapshot(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        check(args.out)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    sys.exit(main())
