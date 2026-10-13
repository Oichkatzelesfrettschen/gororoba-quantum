"""Qualified local simulation policy and ordered batch evidence.

CPU density matrices provide the qualified execution path. GPU and hybrid requests
remain explicit capability errors until a pinned Aer GPU build passes the
same circuit, noise, numerical, and memory qualification. Local preparation
time stays separate from the QPU charge ledger.
"""

from __future__ import annotations

import hashlib
import io
import json
import time
from typing import Any

import numpy as np
from qiskit import qpy
from qiskit_aer import AerSimulator

import aer_identity
import aer_resources
import parallel

# Density matrices below this active width stay on CPU threads, where shot
# parallelism outruns per-shot GPU kernel launches (LOCAL_COMPUTE.md).
GPU_MIN_ACTIVE_QUBITS = 11


def requested_settings(args: Any = None) -> dict[str, Any]:
    """Describe CLI policy even when native provenance cannot be established."""
    return {
        "mode": getattr(args, "local_compute", "auto"),
        "threads": getattr(args, "simulation_threads", parallel.default_threads()),
        "memory_mb": getattr(args, "simulation_memory_mb", 512),
        "shot_branching": False,
        "method": "density_matrix",
        "precision": "double",
        "shot_branching_sampling": False,
        "parallel_experiments": 1,
    }


def settings(args: Any = None) -> dict[str, Any]:
    return requested_settings(args) | {"aer_native": aer_identity.identity()}


def validate(policy: dict[str, Any], devices: tuple[str, ...] | None = None) -> None:
    """Reject unavailable or unqualified execution before service construction."""
    defaults = settings()
    if set(policy) != set(defaults):
        raise ValueError("local compute policy fields differ from the supported contract")
    if policy["mode"] not in ("cpu", "gpu", "auto"):
        raise ValueError("local compute mode must be cpu, gpu, or auto")
    for key in ("threads", "memory_mb"):
        if type(policy[key]) is not int or policy[key] <= 0:
            raise ValueError(f"local compute {key} must be a positive integer")
    if type(policy["shot_branching"]) is not bool:
        raise ValueError("shot_branching must be Boolean")
    if policy["shot_branching"]:
        raise ValueError("shot branching fails noisy folded-circuit qualification and remains disabled")
    for key in ("method", "precision", "shot_branching_sampling", "parallel_experiments"):
        if type(policy[key]) is not type(defaults[key]) or policy[key] != defaults[key]:
            raise ValueError(f"local compute {key} differs from the qualified configuration")
    aer_identity.validate_contract(policy["aer_native"])
    if policy["aer_native"] != defaults["aer_native"]:
        raise ValueError("local compute policy identifies a different native Aer build")
    available = tuple(AerSimulator().available_devices()) if devices is None else devices
    if policy["mode"] == "gpu" and "GPU" not in available:
        raise ValueError(f"local compute gpu requires Aer GPU; available devices: {available}")
    if "CPU" not in available:
        raise ValueError("the qualified CPU simulation device is unavailable")


def _json_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_value(value.tolist())
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


def configure(simulator: Any, policy: dict[str, Any]) -> None:
    validate(policy)
    simulator.set_options(
        device="CPU",
        method=policy["method"],
        precision=policy["precision"],
        max_parallel_threads=policy["threads"],
        max_parallel_experiments=policy["parallel_experiments"],
        max_parallel_shots=policy["threads"],
        max_memory_mb=policy["memory_mb"],
        shot_branching_enable=policy["shot_branching"],
        shot_branching_sampling_enable=policy["shot_branching_sampling"],
    )
    noise = _json_value(simulator.options.noise_model.to_dict())
    # QuantumError IDs are generated UUIDs; channel instructions/probabilities
    # carry the semantics and remain in the digest.
    for error in noise.get("errors", []):
        error.pop("id", None)
    noise["errors"] = sorted(
        noise.get("errors", []), key=lambda error: json.dumps(error, sort_keys=True, separators=(",", ":"))
    )
    simulator._gororoba_noise_digest = hashlib.sha256(
        json.dumps(noise, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    simulator._gororoba_compute_policy = dict(policy)
    simulator._gororoba_simulation_batches = []


def batches(simulator: Any) -> list[dict[str, Any]]:
    return list(getattr(simulator, "_gororoba_simulation_batches", []))


def route(policy: dict[str, Any], circuits: list[Any]) -> tuple[str, dict[str, Any] | None]:
    """Choose the Aer device for one batch from its widest active register.

    auto sends batches of GPU_MIN_ACTIVE_QUBITS or more active qubits to the
    GPU when Aer reports one and aer_resources admits the batch against a
    fresh CUDA memory reading; a rejected admission keeps the batch on CPU
    and records the reason. gpu requires admission; cpu never routes.
    """
    if policy["mode"] == "cpu":
        return "CPU", None
    width = max(aer_resources.active_support(circuit) for circuit in circuits)
    if policy["mode"] == "auto" and (width < GPU_MIN_ACTIVE_QUBITS or "GPU" not in AerSimulator().available_devices()):
        return "CPU", None
    try:
        admission = aer_resources.admit_gpu(circuits, policy["memory_mb"], aer_resources.gpu_snapshot())
        admission["runtime"] = aer_identity.gpu_runtime_identity()
        # Aer 0.17.2 exposes no device selector, so admission of device zero
        # covers execution only on a host with exactly one GPU.
        if admission["runtime"].get("device_count") != 1:
            raise ValueError("GPU admission requires a single-GPU host")
    except ValueError as error:
        if policy["mode"] == "gpu":
            raise
        return "CPU", {"rejected": str(error), "active_qubits": width}
    return "GPU", admission


def run(simulator: Any, circuits: list[Any], shots: int, seed: int) -> Any:
    """Preserve declared order and retain actual Aer device/kernel evidence."""
    policy = getattr(simulator, "_gororoba_compute_policy", None)
    device, admission = "CPU", None
    if policy is not None:
        validate(policy)
        device, admission = route(policy, circuits)
        # One GPU shot state at a time keeps execution within the two-state
        # admission floor; CPU batches parallelize shots across threads.
        simulator.set_options(device=device, max_parallel_shots=1 if device == "GPU" else policy["threads"])
    start = time.perf_counter()
    result = simulator.run(circuits, shots=shots, seed_simulator=seed).result()
    elapsed = time.perf_counter() - start
    if not result.success:
        raise RuntimeError(f"local Aer simulation failed: {result.status}")
    if policy is not None:
        validate(policy)
        for experiment in result.results:
            if not experiment.success:
                raise RuntimeError(f"local Aer experiment failed: {experiment.status}")
            metadata = experiment.metadata
            if metadata.get("device") != device or metadata.get("method") != policy["method"]:
                raise RuntimeError("Aer result device/method differs from the admitted local compute policy")
        buffer = io.BytesIO()
        qpy.dump(circuits, buffer)
        simulator._gororoba_simulation_batches.append(
            {
                "policy": dict(policy),
                "device": device,
                "gpu_admission": admission,
                "ordered_circuit_names": [circuit.name for circuit in circuits],
                "ordered_qpy_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
                "noise_serialized_channels_sha256": simulator._gororoba_noise_digest,
                "noise_digest_scope": (
                    "UUID-free sorted serialized gate/readout channels; delay RelaxationNoisePass is excluded "
                    "by Aer serialization and depends on the run's Target T1/T2/dt calibration"
                ),
                "shots": shots,
                "seed_simulator": seed,
                "wall_seconds": elapsed,
                "experiment_metadata": [_json_value(experiment.metadata) for experiment in result.results],
            }
        )
    return result


def _verify() -> None:
    from qiskit import QuantumCircuit
    from qiskit_aer.noise import NoiseModel

    policy = settings()
    validate(policy, ("CPU",))
    changed_identity = dict(policy["aer_native"])
    changed_identity["extension"] = dict(changed_identity["extension"]) | {"sha256": "0" * 64}
    for bad in (
        policy | {"aer_native": changed_identity},
        policy | {"shot_branching_sampling": 0},
        policy | {"parallel_experiments": True},
        policy | {"mode": "hybrid"},
        policy | {"threads": 0},
        policy | {"memory_mb": True},
        policy | {"precision": "single"},
        policy | {"shot_branching": 1},
    ):
        try:
            validate(bad, ("CPU", "GPU"))
        except ValueError:
            pass
        else:
            raise AssertionError(f"unqualified local compute policy passes: {bad}")
    circuit = QuantumCircuit(1, 2, name="reset_feed_forward")
    circuit.x(0)
    circuit.measure(0, 0)
    circuit.reset(0)
    with circuit.if_test((circuit.clbits[0], True)):
        circuit.x(0)
    circuit.measure(0, 1)
    simulator = AerSimulator(noise_model=NoiseModel())
    configure(simulator, policy)
    result = run(simulator, [circuit], 64, 20261012)
    assert result.get_counts(0) == {"11": 64}
    assert batches(simulator)[0]["ordered_circuit_names"] == [circuit.name]
    assert not batches(simulator)[0]["experiment_metadata"][0].get("shot_branching_enabled", False)
    _verify_routing(policy)
    print("local compute policy, capability rejection, routing, and CPU dynamic batch checks pass")


def _verify_routing(policy: dict[str, Any]) -> None:
    from unittest.mock import patch

    from qiskit import QuantumCircuit

    narrow, wide = QuantumCircuit(5), QuantumCircuit(GPU_MIN_ACTIVE_QUBITS)
    narrow.h(range(5))
    wide.h(range(GPU_MIN_ACTIVE_QUBITS))
    snapshot = {
        "device_ordinal": 0,
        "free_bytes": 8 * 1024 * aer_resources.MEBIBYTE,
        "total_bytes": 12 * 1024 * aer_resources.MEBIBYTE,
        "runtime_version": 13040,
        "driver_version": 13040,
        "compute_capability_major": 8,
        "compute_capability_minor": 9,
    }
    starved = snapshot | {"free_bytes": aer_resources.MINIMUM_GPU_FREE_BYTES - 1}

    def routed(mode: str, circuit: Any, devices: tuple[str, ...], reading: dict[str, int], count: int) -> Any:
        with (
            patch.object(AerSimulator, "available_devices", return_value=devices),
            patch.object(aer_resources, "gpu_snapshot", return_value=reading),
            patch.object(aer_identity, "gpu_runtime_identity", return_value={"device_count": count}),
        ):
            return route(policy | {"mode": mode}, [circuit])

    both = ("CPU", "GPU")
    assert routed("cpu", wide, both, snapshot, 1) == ("CPU", None)
    assert routed("auto", narrow, both, snapshot, 1) == ("CPU", None)
    assert routed("auto", wide, ("CPU",), snapshot, 1) == ("CPU", None)
    device, admission = routed("auto", wide, both, snapshot, 1)
    assert device == "GPU" and admission is not None and admission["active_qubits"] == [GPU_MIN_ACTIVE_QUBITS]
    for reading, count in ((starved, 1), (snapshot, 2)):
        device, admission = routed("auto", wide, both, reading, count)
        assert device == "CPU" and admission is not None and "rejected" in admission
        try:
            routed("gpu", wide, both, reading, count)
        except ValueError:
            pass
        else:
            raise AssertionError("gpu mode accepted a rejected admission")


if __name__ == "__main__":
    _verify()
