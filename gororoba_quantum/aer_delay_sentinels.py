"""Qualify installed native Aer delay channels against independent analytic laws.

The density-matrix saves describe quantum probabilities before terminal readout.
Synthetic relaxation parameters exercise physical wires; they describe neither
IBM calibration nor hardware performance. Every circuit runs on the CPU.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Delay
from qiskit.quantum_info import SuperOp
from qiskit.transpiler import PassManager
from qiskit_aer import AerSimulator
from qiskit_aer.library import SaveProbabilities
from qiskit_aer.noise import NoiseModel, ReadoutError, thermal_relaxation_error
from qiskit_aer.noise.passes import LocalNoisePass, RelaxationNoisePass


@dataclass(frozen=True)
class Calibration:
    """Bind synthetic relaxation parameters to an actual circuit wire index."""

    physical_wire: int
    t1_seconds: float
    t2_seconds: float
    equilibrium_population: float


DEFAULT_CALIBRATIONS = (
    Calibration(2, 200e-6, 250e-6, 0.30),
    Calibration(0, 80e-6, 60e-6, 0.0),
    Calibration(1, 120e-6, 180e-6, 0.12),
)
DEFAULT_DELAY_TICKS = (0, 1, 17, 64, 256)
VARIANTS = ("nominal", "omitted_relaxation", "doubled_dt", "rotated_wire_calibrations")
FAMILIES = ("t1_ground", "t1_excited", "ramsey_zero_phase", "ramsey_pi_over_three")


def _validate(
    calibrations: tuple[Calibration, ...], delay_ticks: tuple[int, ...], dt_seconds: float, tolerance: float
) -> None:
    if not math.isfinite(dt_seconds) or dt_seconds <= 0:
        raise ValueError("dt_seconds must be finite and positive")
    if not math.isfinite(tolerance) or not 0 < tolerance < 1e-6:
        raise ValueError("tolerance must be finite and lie between zero and 1e-6")
    if not 2 <= len(calibrations) <= 8:
        raise ValueError("qualification requires between two and eight physical wires")
    wires = [calibration.physical_wire for calibration in calibrations]
    if any(type(wire) is not int for wire in wires) or sorted(wires) != list(range(len(wires))):
        raise ValueError("physical wires must cover each circuit index exactly once")
    for calibration in calibrations:
        if not all(math.isfinite(value) and value > 0 for value in (calibration.t1_seconds, calibration.t2_seconds)):
            raise ValueError("T1 and T2 must be finite and positive")
        if calibration.t2_seconds > 2 * calibration.t1_seconds:
            raise ValueError("T2 must be at most twice T1; qualification never clips T2")
        if not math.isfinite(calibration.equilibrium_population) or not 0 <= calibration.equilibrium_population <= 1:
            raise ValueError("equilibrium population must lie between zero and one")
    if (
        not delay_ticks
        or any(type(ticks) is not int or ticks < 0 for ticks in delay_ticks)
        or len(set(delay_ticks)) != len(delay_ticks)
        or 0 not in delay_ticks
        or sum(ticks > 0 for ticks in delay_ticks) < 2
    ):
        raise ValueError("delay_ticks must contain zero and at least two distinct positive integers")
    if any(not math.isfinite(ticks * dt_seconds) for ticks in delay_ticks):
        raise ValueError("all dt-derived durations must be finite")


def _simulator(noise_model: NoiseModel | None = None) -> AerSimulator:
    return AerSimulator(
        method="density_matrix",
        device="CPU",
        precision="double",
        max_parallel_threads=1,
        max_parallel_experiments=1,
        max_parallel_shots=1,
        max_memory_mb=256,
        shot_branching_enable=False,
        shot_branching_sampling_enable=False,
        noise_model=noise_model,
    )


def _materialize(
    circuit: QuantumCircuit,
    calibrations: tuple[Calibration, ...],
    dt_seconds: float,
    variant: str,
    channel_catalog: dict[str, Any],
) -> tuple[QuantumCircuit, list[dict[str, Any]]]:
    ordered = sorted(calibrations, key=lambda calibration: calibration.physical_wire)
    if variant == "rotated_wire_calibrations":
        ordered = ordered[1:] + ordered[:1]
    effective_dt = dt_seconds * (2 if variant == "doubled_dt" else 1)
    if variant == "omitted_relaxation":
        materialized = circuit.copy()
    else:
        materialized = PassManager(
            RelaxationNoisePass(
                t1s=[calibration.t1_seconds for calibration in ordered],
                t2s=[calibration.t2_seconds for calibration in ordered],
                dt=effective_dt,
                op_types=[Delay],
                excited_state_populations=[calibration.equilibrium_population for calibration in ordered],
            )
        ).run(circuit)
    channels: list[dict[str, Any]] = []
    for instruction in materialized.data:
        if instruction.operation.name != "quantum_channel":
            continue
        matrix = np.asarray(SuperOp(instruction.operation).data, dtype=complex)
        payload = {
            "representation": "Qiskit SuperOp; column-vectorized density matrix",
            "real": matrix.real.tolist(),
            "imag": matrix.imag.tolist(),
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        channel_catalog[digest] = payload
        channels.append(
            {
                "superop_sha256": digest,
                "physical_wires": [materialized.find_bit(qubit).index for qubit in instruction.qubits],
            }
        )
    expected_channels = 0 if variant == "omitted_relaxation" else circuit.count_ops().get("delay", 0)
    if len(channels) != expected_channels:
        raise RuntimeError("RelaxationNoisePass materialized an unexpected number of channels")
    return materialized, channels


def _run_probabilities(circuits: list[QuantumCircuit], tolerance: float) -> list[dict[str, Any]]:
    result = _simulator().run(circuits, shots=1, seed_simulator=739).result()
    if not result.success or len(result.results) != len(circuits):
        raise RuntimeError("native Aer failed the deterministic delay batch")
    observations: list[dict[str, Any]] = []
    for index, experiment in enumerate(result.results):
        metadata = experiment.metadata
        if not experiment.success or metadata.get("device") != "CPU" or metadata.get("method") != "density_matrix":
            raise RuntimeError("native Aer result differs from the required CPU density-matrix policy")
        probabilities = np.asarray(result.data(index)["quantum_probabilities"], dtype=float)
        if (
            probabilities.ndim != 1
            or not np.isfinite(probabilities).all()
            or np.min(probabilities) < -tolerance
            or abs(float(probabilities.sum()) - 1) > tolerance
        ):
            raise RuntimeError("native Aer returned invalid normalized probabilities")
        observations.append(
            {
                "observed_probabilities": probabilities.tolist(),
                "native_metadata": {
                    key: metadata.get(key)
                    for key in (
                        "method",
                        "device",
                        "num_qubits",
                        "active_input_qubits",
                        "input_qubit_map",
                        "remapped_qubits",
                        "noise",
                        "result_types",
                        "result_subtypes",
                    )
                },
            }
        )
    return observations


def _sentinel(width: int, calibration: Calibration, ticks: int, family: str) -> QuantumCircuit:
    circuit = QuantumCircuit(width)
    wire = calibration.physical_wire
    if family == "t1_excited":
        circuit.x(wire)
    elif family.startswith("ramsey"):
        circuit.h(wire)
    circuit.delay(ticks, wire, unit="dt")
    if family.startswith("ramsey"):
        if family == "ramsey_pi_over_three":
            circuit.rz(math.pi / 3, wire)
        circuit.h(wire)
    return circuit


def _expected(calibration: Calibration, seconds: float, family: str) -> list[float]:
    if family.startswith("t1"):
        initial_population = 1.0 if family == "t1_excited" else 0.0
        population = calibration.equilibrium_population + (initial_population - calibration.equilibrium_population) * (
            math.exp(-seconds / calibration.t1_seconds)
        )
        return [1 - population, population]
    phase = math.pi / 3 if family == "ramsey_pi_over_three" else 0.0
    probability_zero = (1 + math.exp(-seconds / calibration.t2_seconds) * math.cos(phase)) / 2
    return [probability_zero, 1 - probability_zero]


def _basis_rotation(circuit: QuantumCircuit, wire: int, basis: str) -> None:
    if basis == "Y":
        circuit.sdg(wire)
    if basis in ("X", "Y"):
        circuit.h(wire)


def _bell_cases(
    calibrations: tuple[Calibration, ...], dt_seconds: float, ticks: int, channel_catalog: dict[str, Any]
) -> tuple[list[QuantumCircuit], list[dict[str, Any]]]:
    control, work = calibrations[:2]
    circuits: list[QuantumCircuit] = []
    records: list[dict[str, Any]] = []
    for variant in VARIANTS[:3]:
        before_reset = QuantumCircuit(len(calibrations))
        before_reset.h(control.physical_wire)
        before_reset.cx(control.physical_wire, work.physical_wire)
        before_reset.delay(ticks, control.physical_wire, unit="dt")
        before_reset, channels = _materialize(before_reset, calibrations, dt_seconds, variant, channel_catalog)
        before_reset.append(
            SaveProbabilities(2, label="quantum_probabilities"), [control.physical_wire, work.physical_wire]
        )
        before_reset.name = f"bell_before_reset_control{control.physical_wire}_work{work.physical_wire}_{variant}"
        duration = (
            0.0 if variant == "omitted_relaxation" else ticks * dt_seconds * (2 if variant == "doubled_dt" else 1)
        )
        decay = math.exp(-duration / control.t1_seconds)
        population = control.equilibrium_population
        circuits.append(before_reset)
        records.append(
            {
                "circuit_label": before_reset.name,
                "observation_stage": "before_control_reset",
                "variant": variant,
                "control_physical_wire": control.physical_wire,
                "work_physical_wire": work.physical_wire,
                "control_basis": "Z",
                "work_basis": "Z",
                "delay_ticks": ticks,
                "expected_probabilities": [
                    0.5 * (1 - population * (1 - decay)),
                    0.5 * population * (1 - decay),
                    0.5 * (1 - population) * (1 - decay),
                    0.5 * (population + (1 - population) * decay),
                ],
                "channels": channels,
            }
        )
        for control_basis in ("X", "Y", "Z"):
            for work_basis in ("X", "Y", "Z"):
                circuit = QuantumCircuit(len(calibrations))
                circuit.h(control.physical_wire)
                circuit.cx(control.physical_wire, work.physical_wire)
                circuit.delay(ticks, control.physical_wire, unit="dt")
                circuit.reset(control.physical_wire)
                _basis_rotation(circuit, control.physical_wire, control_basis)
                _basis_rotation(circuit, work.physical_wire, work_basis)
                circuit, channels = _materialize(circuit, calibrations, dt_seconds, variant, channel_catalog)
                circuit.append(
                    SaveProbabilities(2, label="quantum_probabilities"), [control.physical_wire, work.physical_wire]
                )
                circuit.name = (
                    f"bell_reset_control{control.physical_wire}{control_basis}"
                    f"_work{work.physical_wire}{work_basis}_{variant}"
                )
                circuits.append(circuit)
                records.append(
                    {
                        "circuit_label": circuit.name,
                        "observation_stage": "after_control_reset",
                        "variant": variant,
                        "control_physical_wire": control.physical_wire,
                        "work_physical_wire": work.physical_wire,
                        "control_basis": control_basis,
                        "work_basis": work_basis,
                        "delay_ticks": ticks,
                        "expected_probabilities": [0.5, 0.0, 0.5, 0.0] if control_basis == "Z" else [0.25] * 4,
                        "channels": channels,
                    }
                )
    return circuits, records


def _readout_boundary(tolerance: float) -> dict[str, Any]:
    circuit = QuantumCircuit(1, 1)
    circuit.append(SaveProbabilities(1, label="quantum_probabilities"), [0])
    circuit.measure(0, 0)
    noise = NoiseModel()
    noise.add_readout_error(ReadoutError([[0, 1], [1, 0]]), [0])
    result = _simulator(noise).run(circuit, shots=8, seed_simulator=739).result()
    if not result.success:
        raise RuntimeError("native Aer failed the terminal readout boundary check")
    observed = np.asarray(result.data(0)["quantum_probabilities"], dtype=float)
    counts = result.get_counts(0)
    return {
        "quantum_probabilities_before_measurement": observed.tolist(),
        "classical_counts_after_deterministic_bit_flip_readout": counts,
        "shots": 8,
        "passed": bool(np.max(np.abs(observed - [1.0, 0.0])) <= tolerance and counts == {"1": 8}),
    }


def qualify(
    *,
    calibrations: tuple[Calibration, ...] = DEFAULT_CALIBRATIONS,
    delay_ticks: tuple[int, ...] = DEFAULT_DELAY_TICKS,
    dt_seconds: float = 1e-6,
    tolerance: float = 1e-11,
) -> dict[str, Any]:
    """Return exact-probability evidence and explicit fault-detection outcomes.

    A passed record requires each nominal law, the entangled reset negative
    control, and the readout boundary to pass. Every prescribed mutation must
    exceed the declared detection threshold on at least one independent delay
    sentinel. Custom parameters with insufficient sensitivity fail that gate.
    """
    _validate(calibrations, delay_ticks, dt_seconds, tolerance)
    channel_catalog: dict[str, Any] = {}
    circuits: list[QuantumCircuit] = []
    records: list[dict[str, Any]] = []
    for variant in VARIANTS:
        for calibration in calibrations:
            for ticks in delay_ticks:
                for family in FAMILIES:
                    circuit = _sentinel(len(calibrations), calibration, ticks, family)
                    circuit, channels = _materialize(circuit, calibrations, dt_seconds, variant, channel_catalog)
                    circuit.append(SaveProbabilities(1, label="quantum_probabilities"), [calibration.physical_wire])
                    circuit.name = f"delay_{family}_wire{calibration.physical_wire}_ticks{ticks}_{variant}"
                    circuits.append(circuit)
                    records.append(
                        {
                            "circuit_label": circuit.name,
                            "variant": variant,
                            "family": family,
                            "physical_wire": calibration.physical_wire,
                            "delay_ticks": ticks,
                            "nominal_delay_seconds": ticks * dt_seconds,
                            "expected_probabilities": _expected(calibration, ticks * dt_seconds, family),
                            "channels": channels,
                        }
                    )
    observations = _run_probabilities(circuits, tolerance)
    for record, observation in zip(records, observations, strict=True):
        record.update(observation)
        record["max_absolute_error"] = max(
            abs(actual - expected)
            for actual, expected in zip(record["observed_probabilities"], record["expected_probabilities"], strict=True)
        )
    nominal = [record for record in records if record["variant"] == "nominal"]
    detection_threshold = max(100 * tolerance, 1e-7)
    mutations: dict[str, dict[str, Any]] = {}
    for variant in VARIANTS[1:]:
        witness = max(
            (record for record in records if record["variant"] == variant),
            key=lambda record: record["max_absolute_error"],
        )
        mutations[variant] = {
            "detected": witness["max_absolute_error"] > detection_threshold,
            "max_absolute_error": witness["max_absolute_error"],
            "witness": {key: witness[key] for key in ("family", "physical_wire", "delay_ticks")},
        }
    bell_circuits, bell_records = _bell_cases(calibrations, dt_seconds, max(delay_ticks), channel_catalog)
    for record, observation in zip(bell_records, _run_probabilities(bell_circuits, tolerance), strict=True):
        record.update(observation)
        record["max_absolute_error"] = max(
            abs(actual - expected)
            for actual, expected in zip(record["observed_probabilities"], record["expected_probabilities"], strict=True)
        )
    pre_reset = [record for record in bell_records if record["observation_stage"] == "before_control_reset"]
    post_reset = [record for record in bell_records if record["observation_stage"] == "after_control_reset"]
    pre_reset_displacement = max(
        abs(actual - omitted)
        for actual, omitted in zip(
            pre_reset[0]["observed_probabilities"], pre_reset[1]["observed_probabilities"], strict=True
        )
    )
    readout = _readout_boundary(tolerance)
    checks = {
        "nominal_analytic_laws": all(record["max_absolute_error"] <= tolerance for record in nominal),
        "all_prescribed_mutations_detected": all(mutation["detected"] for mutation in mutations.values()),
        "entangled_delay_before_reset_invariance": all(
            record["max_absolute_error"] <= tolerance for record in bell_records
        ),
        "entangled_pre_reset_channel_visible": pre_reset_displacement > detection_threshold,
        "terminal_readout_boundary": readout["passed"],
    }
    return {
        "schema": "native-aer-cpu-delay-qualification-v1",
        "passed": all(checks.values()),
        "versions": {name: importlib.metadata.version(name) for name in ("numpy", "qiskit", "qiskit-aer")},
        "sources": [
            {"basename": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            for source in (
                Path(__file__),
                Path(inspect.getfile(RelaxationNoisePass)),
                Path(inspect.getfile(LocalNoisePass)),
                Path(inspect.getfile(thermal_relaxation_error)),
            )
        ],
        "parameters": {
            "calibrations": [asdict(calibration) for calibration in calibrations],
            "calibration_source": "synthetic analytic fixtures; physical_wire is the circuit/DAG index",
            "dt_seconds": dt_seconds,
            "delay_ticks": list(delay_ticks),
            "absolute_tolerance": tolerance,
            "mutation_detection_threshold": detection_threshold,
        },
        "execution": {
            "device": "CPU",
            "method": "density_matrix",
            "precision": "double",
            "threads": 1,
            "shots_for_deterministic_saves": 1,
            "noise_pass": "qiskit_aer.noise.passes.RelaxationNoisePass via qiskit.transpiler.PassManager",
            "noise_scope": "explicit Delay operations only; ideal preparation, gates, and reset",
            "probability_scope": "save_probabilities quantum state before terminal readout; first saved qarg is bit 0",
        },
        "checks": checks,
        "nominal_max_absolute_error": max(record["max_absolute_error"] for record in nominal),
        "mutations": mutations,
        "sentinels": records,
        "reset_negative_control": {
            "scope": "Bell pair; nine local Pauli measurement settings; unconditional ideal control reset",
            "expected_state": "control |0><0| tensor work I/2; omitted and doubled delay remain indistinguishable",
            "records": post_reset,
            "before_reset_records": pre_reset,
            "before_reset_max_nominal_vs_omitted_difference": pre_reset_displacement,
            "probability_order": "control is bit 0 and work is bit 1, independent of their physical wire indices",
        },
        "terminal_readout_boundary": readout,
        "materialized_channels": channel_catalog,
        "limitations": [
            "Finite synthetic qualification does not establish calibration accuracy or hardware behavior.",
            "Pre-materialized PassManager channels do not test NoiseModel.from_backend delay-pass installation "
            "or the AerBackend automatic custom-pass trigger path.",
            "Deterministic saves do not qualify finite-shot sampling or general dynamic branch handling.",
            "The reset identity excludes work idle noise, correlated channels, "
            "recorded environments, and imperfect reset.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = qualify()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
