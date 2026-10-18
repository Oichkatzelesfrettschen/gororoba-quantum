"""Qualified local simulation policy and ordered batch evidence.

Under the default method a batch containing a dynamic circuit runs
statevector trajectories on CPU shot threads, and every other batch runs a
density matrix. auto routes density-matrix batches of GPU_MIN_ACTIVE_QUBITS
or more active qubits to an admitted single GPU and keeps trajectories on
CPU; gpu requires admission for every batch; cpu never routes. Local
preparation time stays separate from the QPU charge ledger.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import threading
import time
from collections import OrderedDict
from typing import Any

import numpy as np
from qiskit import qpy
from qiskit.circuit import ControlFlowOp, Delay
from qiskit_aer import AerSimulator
from qiskit_aer.noise.errors.base_quantum_error import QuantumChannelInstruction

import aer_identity
import aer_resources
import parallel

# Under DYNAMIC_STATEVECTOR, a batch with mid-circuit measurement, reset or
# control flow runs statevector trajectories: Aer evolves such circuits shot by
# shot, and a 2**n statevector trajectory samples the same noise channels as a
# 4**n density matrix at a fraction of the cost. Static batches keep the
# density matrix, which yields their exact final distribution in one pass.
DYNAMIC_STATEVECTOR = "density_matrix_dynamic_statevector"
QUALIFIED_METHODS = ("density_matrix", DYNAMIC_STATEVECTOR)


def is_dynamic(circuit: Any) -> bool:
    """Control flow, reset, or any measurement followed by later quantum work.

    live_run binds _is_dynamic to this function, so the IBM job kind and the
    Aer method read one rule: a later gate on any qubit counts, since Aer then
    samples the circuit shot by shot. Every ControlFlowOp counts, box included.
    The rule reads circuit.data order, so a source circuit can classify
    dynamic while its routed ISA, which serializes the same DAG in another
    order, classifies static.
    """
    measurement_seen = False
    for instruction in circuit.data:
        name = instruction.operation.name
        if isinstance(instruction.operation, ControlFlowOp) or name == "reset":
            return True
        if measurement_seen and name not in ("measure", "barrier", "delay"):
            return True
        if name == "measure":
            measurement_seen = True
    return False


def batch_method(policy: dict[str, Any], circuits: list[Any]) -> str:
    """The Aer method one batch runs under the policy."""
    if policy["method"] == DYNAMIC_STATEVECTOR:
        return "statevector" if any(is_dynamic(circuit) for circuit in circuits) else "density_matrix"
    return str(policy["method"])


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
        "method": getattr(args, "local_compute_method", DYNAMIC_STATEVECTOR),
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
    if policy["method"] not in QUALIFIED_METHODS:
        raise ValueError("local compute method differs from the qualified configurations")
    for key in ("precision", "shot_branching_sampling", "parallel_experiments"):
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


_GPU_LOCK = threading.Lock()

# NoiseModel serialization dominates planning time; a model is built once per
# backend snapshot and never mutated afterward, so its digest is computed once.
_NOISE_DIGESTS: OrderedDict[int, tuple[Any, str]] = OrderedDict()
# A planning or collection phase touches a few snapshots at a time; the bound
# keeps a long replay from retaining every historical noise model.
CACHE_ENTRIES = 8


def noise_digest(model: Any) -> str:
    """UUID-free digest of a noise model's sorted serialized channels."""
    cached = _NOISE_DIGESTS.get(id(model))
    if cached is not None and cached[0] is model:
        return cached[1]
    noise = _json_value(model.to_dict())
    # QuantumError IDs are generated UUIDs; channel instructions/probabilities
    # carry the semantics and remain in the digest.
    for error in noise.get("errors", []):
        error.pop("id", None)
    noise["errors"] = sorted(
        noise.get("errors", []), key=lambda error: json.dumps(error, sort_keys=True, separators=(",", ":"))
    )
    digest = hashlib.sha256(
        json.dumps(noise, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    _NOISE_DIGESTS[id(model)] = (model, digest)
    while len(_NOISE_DIGESTS) > CACHE_ENTRIES:
        _NOISE_DIGESTS.popitem(last=False)
    return digest


_SERIALIZED_NOISE: OrderedDict[int, tuple[Any, dict[str, Any]]] = OrderedDict()
_SERIALIZED_NOISE_LOCK = threading.Lock()


def serialized_noise(model: Any) -> dict[str, Any]:
    """model.to_dict(serializable=True), computed once per model object.

    The dictionary is the native controller's only noise input. A model that
    noise_simulator builds is never mutated afterward, so one serialization
    equals every later one; the controller converts the dictionary to its
    own representation and leaves the Python object unchanged.
    """
    with _SERIALIZED_NOISE_LOCK:
        cached = _SERIALIZED_NOISE.get(id(model))
        if cached is not None and cached[0] is model:
            return cached[1]
        serialized = model.to_dict(serializable=True)
        _SERIALIZED_NOISE[id(model)] = (model, serialized)
        while len(_SERIALIZED_NOISE) > CACHE_ENTRIES:
            _SERIALIZED_NOISE.popitem(last=False)
        return serialized


class _SerializedNoise:
    """Noise argument of cpp_execute_circuits carrying a retained serialization."""

    def __init__(self, serialized: dict[str, Any]) -> None:
        self._serialized = serialized

    def to_dict(self, serializable: bool = False) -> dict[str, Any]:
        del serializable
        return self._serialized


class SerializedNoiseSimulator(AerSimulator):
    """AerSimulator that passes its configured noise model to the controller from one serialization.

    qiskit_aer's cpp_execute_circuits serializes the noise model with
    NoiseModel.to_dict(serializable=True) on every run: a walk over every
    QuantumError of the whole device plus a JSON round trip. A run whose
    noise model is the configured object hands the controller the retained
    serialized_noise dictionary, which equals that walk's output, so the
    controller receives the same input. AerBackend._assemble_noise_model
    deep-copies the model before it adds a circuit's QuantumChannelInstruction
    errors, and a run_options noise_model replaces it; either object differs
    from the configured one and serializes afresh.
    """

    def _assemble_noise_model(self, circuits: Any, optypes: Any, **run_options: Any) -> Any:
        """AerBackend._assemble_noise_model without its PassManager call on an empty circuit list.

        The stock method runs the model's noise passes on the circuits that
        hold a Delay and moves QuantumChannelInstruction errors into a copied
        model. A batch with neither leaves circuits and model unchanged, yet
        the stock call still hands qiskit's PassManager.run an empty list,
        which dill-serializes the RelaxationNoisePass and its whole-device
        Target for a process map. Such a batch returns the stock method's
        unchanged result directly.
        """
        if any(Delay in types or QuantumChannelInstruction in types for types in optypes):
            return super()._assemble_noise_model(circuits, optypes, **run_options)
        return (
            copy.copy(circuits),
            run_options.get("noise_model", getattr(self.options, "noise_model", None)),
            run_options,
        )

    def _execute_circuits(self, aer_circuits: Any, noise_model: Any, config: Any) -> Any:
        if noise_model is not None and noise_model is getattr(self.options, "noise_model", None):
            noise_model = _SerializedNoise(serialized_noise(noise_model))
        return super()._execute_circuits(aer_circuits, noise_model, config)


def configure(simulator: Any, policy: dict[str, Any]) -> None:
    validate(policy)
    simulator.set_options(
        device="CPU",
        method="density_matrix" if policy["method"] == DYNAMIC_STATEVECTOR else policy["method"],
        precision=policy["precision"],
        max_parallel_threads=policy["threads"],
        max_parallel_experiments=policy["parallel_experiments"],
        max_parallel_shots=policy["threads"],
        max_memory_mb=policy["memory_mb"],
        shot_branching_enable=policy["shot_branching"],
        shot_branching_sampling_enable=policy["shot_branching_sampling"],
    )
    simulator._gororoba_noise_digest = noise_digest(simulator.options.noise_model)
    if isinstance(simulator, SerializedNoiseSimulator) and simulator.options.noise_model is not None:
        # The first serialization runs on the configuring thread, so
        # concurrent runs on one snapshot read one retained dictionary.
        serialized_noise(simulator.options.noise_model)
    simulator._gororoba_compute_policy = dict(policy)
    simulator._gororoba_simulation_batches = []


def batches(simulator: Any) -> list[dict[str, Any]]:
    return list(getattr(simulator, "_gororoba_simulation_batches", []))


def merge_batches(target: Any, source: Any) -> None:
    """Append source's batch evidence to target's, in order; a simulator without evidence contributes nothing."""
    evidence = batches(source)
    if evidence:
        target._gororoba_simulation_batches = batches(target) + evidence


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


def batch_route(policy: dict[str, Any], method: str, circuits: list[Any]) -> tuple[str, dict[str, Any] | None]:
    """Device for one batch under its method.

    Statevector trajectories of the qualified widths run fastest on CPU shot
    threads, so auto keeps them there. An explicit gpu mode routes them
    through the same admission, whose density-state sizing bounds a
    statevector from above, and fails rather than falls back.
    """
    if method == "density_matrix" or policy["mode"] == "gpu":
        return route(policy, circuits)
    return "CPU", None


def run(simulator: Any, circuits: list[Any], shots: int, seed: int) -> Any:
    """Preserve declared order and retain actual Aer device/kernel evidence."""
    policy = getattr(simulator, "_gororoba_compute_policy", None)
    device, admission = "CPU", None
    method = batch_method(policy, circuits) if policy is not None else None
    # GPU admission reads free device memory for one simulator, so admission
    # and the GPU run share one single-device lock; a CPU-routed batch
    # releases it before running so CPU batches stay parallel.
    holding = policy is not None and policy["mode"] != "cpu"
    if holding:
        _GPU_LOCK.acquire()
    try:
        if policy is not None:
            validate(policy)
            assert method is not None
            device, admission = batch_route(policy, method, circuits)
            # One GPU shot state at a time keeps execution within the two-state
            # admission floor; CPU batches parallelize shots across threads.
            simulator.set_options(
                device=device, method=method, max_parallel_shots=1 if device == "GPU" else policy["threads"]
            )
        if holding and device != "GPU":
            _GPU_LOCK.release()
            holding = False
        start = time.perf_counter()
        result = simulator.run(circuits, shots=shots, seed_simulator=seed).result()
        elapsed = time.perf_counter() - start
    finally:
        if holding:
            _GPU_LOCK.release()
    if not result.success:
        raise RuntimeError(f"local Aer simulation failed: {result.status}")
    if policy is not None:
        validate(policy)
        for experiment in result.results:
            if not experiment.success:
                raise RuntimeError(f"local Aer experiment failed: {experiment.status}")
            metadata = experiment.metadata
            if metadata.get("device") != device or metadata.get("method") != method:
                raise RuntimeError("Aer result device/method differs from the admitted local compute policy")
        buffer = io.BytesIO()
        qpy.dump(circuits, buffer)
        simulator._gororoba_simulation_batches.append(
            {
                "policy": dict(policy),
                "device": device,
                "method": method,
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


def _verify_trajectory_noise(policy: dict[str, Any]) -> None:
    """Trajectories and the density matrix sample one noisy dynamic law within shot noise.

    Gate depolarizing and asymmetric readout error move the law far from the
    noiseless one, so a trajectory kernel that dropped either channel fails.
    """
    from qiskit import QuantumCircuit
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

    circuit = QuantumCircuit(2, 3, name="noisy_feed_forward")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure(0, 0)
    circuit.reset(0)
    with circuit.if_test((circuit.clbits[0], True)):
        circuit.x(0)
    circuit.measure(0, 1)
    circuit.measure(1, 2)
    noise = NoiseModel(basis_gates=["h", "cx", "x"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.08, 1), ["h", "x"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.15, 2), ["cx"])
    noise.add_all_qubit_readout_error(ReadoutError([[0.95, 0.05], [0.10, 0.90]]))
    shots = 40000
    laws = {}
    for label, method, model in (
        ("trajectories", DYNAMIC_STATEVECTOR, noise),
        ("density", "density_matrix", noise),
        ("noiseless", DYNAMIC_STATEVECTOR, NoiseModel()),
    ):
        simulator = AerSimulator(noise_model=model)
        configure(simulator, policy | {"method": method})
        counts = run(simulator, [circuit], shots, 20261013).get_counts(0)
        laws[label] = {key: value / shots for key, value in counts.items()}

    def distance(left: dict[str, float], right: dict[str, float]) -> float:
        return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))

    if distance(laws["trajectories"], laws["density"]) > 0.02:
        raise RuntimeError(f"trajectory and density-matrix noisy laws differ: {laws}")
    if distance(laws["trajectories"], laws["noiseless"]) < 0.1:
        raise RuntimeError("the trajectory kernel dropped the gate or readout noise channels")


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
    assert batches(simulator)[0]["method"] == "statevector", "dynamic batch did not run statevector trajectories"
    _verify_trajectory_noise(policy)
    static = QuantumCircuit(2, 2, name="static")
    static.h(0)
    static.cx(0, 1)
    static.measure([0, 1], [0, 1])
    static.barrier()
    reset_only = QuantumCircuit(1, name="reset_only")
    reset_only.reset(0)
    branch_only = QuantumCircuit(1, 1, name="branch_only")
    with branch_only.if_test((branch_only.clbits[0], True)):
        branch_only.x(0)
    later_work = QuantumCircuit(2, 1, name="later_work")
    later_work.measure(0, 0)
    later_work.x(1)
    boxed = QuantumCircuit(1, name="boxed")
    with boxed.box():
        boxed.x(0)
    cases = ((static, False), (reset_only, True), (branch_only, True), (later_work, True), (boxed, True))
    for candidate, expected in cases:
        if is_dynamic(candidate) != expected:
            raise RuntimeError(f"{candidate.name}: dynamic classification differs from {expected}")
    if (
        batch_method(policy, [static]) != "density_matrix"
        or batch_method(policy, [static, later_work]) != "statevector"
    ):
        raise RuntimeError("a batch with any dynamic circuit must run statevector trajectories")
    if batch_method(policy | {"method": "density_matrix"}, [circuit]) != "density_matrix":
        raise RuntimeError("the retained density_matrix policy changed its method")
    from unittest.mock import patch

    with patch(f"{__name__}.route", return_value=("GPU", {"admitted": True})) as admitted:
        if batch_route(policy | {"mode": "gpu"}, "statevector", [later_work])[0] != "GPU" or not admitted.called:
            raise RuntimeError("explicit gpu mode bypassed GPU admission for a dynamic batch")
        admitted.reset_mock()
        if batch_route(policy | {"mode": "auto"}, "statevector", [later_work]) != ("CPU", None) or admitted.called:
            raise RuntimeError("auto mode left CPU routing for statevector trajectories")
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
