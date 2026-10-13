"""Native CUDA telemetry and bounded Aer density-matrix resource admission.

CUDA calls inspect runtime resources. Qiskit Aer owns all state evolution.
The memory estimate is a state-size lower bound, not a device allocation cap.
"""

from __future__ import annotations

import ctypes
from typing import Any

from qiskit import QuantumCircuit

MEBIBYTE = 1024 * 1024
MINIMUM_GPU_FREE_BYTES = 384 * MEBIBYTE


def active_support(circuit: QuantumCircuit) -> int:
    """Count physical wires, respecting nested control-flow wire mappings."""
    support: set[int] = set()

    def visit(block: QuantumCircuit, mapping: list[int]) -> None:
        for instruction in block.data:
            qubits = [mapping[block.find_bit(qubit).index] for qubit in instruction.qubits]
            operation = instruction.operation
            if hasattr(operation, "blocks"):
                for child in operation.blocks:
                    visit(child, qubits)
            elif operation.name != "barrier":
                support.update(qubits)

    visit(circuit, list(range(circuit.num_qubits)))
    return len(support)


def gpu_snapshot() -> dict[str, int]:
    """Inspect CUDA logical device zero through the installed native runtime."""
    try:
        runtime = ctypes.CDLL("libcudart.so")
    except OSError as error:
        raise ValueError("the native CUDA runtime is unavailable") from error
    runtime.cudaGetErrorString.argtypes = [ctypes.c_int]
    runtime.cudaGetErrorString.restype = ctypes.c_char_p

    def check(status: int, operation: str) -> None:
        if status:
            message = runtime.cudaGetErrorString(status)
            explanation = message.decode("utf-8", errors="replace") if message else "unknown CUDA error"
            raise ValueError(f"{operation} failed ({status}: {explanation})")

    runtime.cudaSetDevice.argtypes = [ctypes.c_int]
    runtime.cudaSetDevice.restype = ctypes.c_int
    check(runtime.cudaSetDevice(0), "cudaSetDevice(0)")
    runtime.cudaMemGetInfo.argtypes = [ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
    runtime.cudaMemGetInfo.restype = ctypes.c_int
    free_bytes, total_bytes = ctypes.c_size_t(), ctypes.c_size_t()
    check(runtime.cudaMemGetInfo(ctypes.byref(free_bytes), ctypes.byref(total_bytes)), "cudaMemGetInfo")
    record = {"device_ordinal": 0, "free_bytes": free_bytes.value, "total_bytes": total_bytes.value}
    for operation, key in (("cudaRuntimeGetVersion", "runtime_version"), ("cudaDriverGetVersion", "driver_version")):
        function = getattr(runtime, operation)
        function.argtypes = [ctypes.POINTER(ctypes.c_int)]
        function.restype = ctypes.c_int
        value = ctypes.c_int()
        check(function(ctypes.byref(value)), operation)
        record[key] = value.value
    runtime.cudaDeviceGetAttribute.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
    runtime.cudaDeviceGetAttribute.restype = ctypes.c_int
    # CUDA driver_types.h defines the compute-capability attribute identifiers.
    for attribute, key in ((75, "compute_capability_major"), (76, "compute_capability_minor")):
        value = ctypes.c_int()
        check(runtime.cudaDeviceGetAttribute(ctypes.byref(value), attribute, 0), "cudaDeviceGetAttribute")
        record[key] = value.value
    return record


def admit_gpu(circuits: list[QuantumCircuit], memory_mb: int, snapshot: dict[str, int]) -> dict[str, Any]:
    """Require the qualified width and reserve against a fresh memory reading."""
    if type(memory_mb) is not int or memory_mb <= 0:
        raise ValueError("GPU admission needs a positive integer memory budget")
    required = {
        "device_ordinal",
        "free_bytes",
        "total_bytes",
        "runtime_version",
        "driver_version",
        "compute_capability_major",
        "compute_capability_minor",
    }
    if set(snapshot) != required or any(type(value) is not int for value in snapshot.values()):
        raise ValueError("GPU admission needs a complete integer CUDA snapshot")
    if snapshot["device_ordinal"] != 0:
        raise ValueError("native GPU qualification covers logical device zero")
    if (snapshot["compute_capability_major"], snapshot["compute_capability_minor"]) != (8, 9):
        raise ValueError("native GPU qualification requires compute capability 8.9")
    if snapshot["runtime_version"] // 1000 != 13 or snapshot["driver_version"] < snapshot["runtime_version"]:
        raise ValueError("native GPU qualification requires CUDA 13 and a compatible driver API")
    if not 0 <= snapshot["free_bytes"] <= snapshot["total_bytes"]:
        raise ValueError("CUDA memory accounting is inconsistent")
    if snapshot["free_bytes"] < MINIMUM_GPU_FREE_BYTES:
        raise ValueError("GPU free memory is below the qualified admission reserve")
    if not circuits:
        raise ValueError("GPU admission needs a nonempty circuit batch")
    widths = [active_support(circuit) for circuit in circuits]
    state_bytes = [16 * 4**width for width in widths]
    admission_budget = min(memory_mb * MEBIBYTE, snapshot["free_bytes"] // 2)
    # local_compute.run executes GPU batches with one shot state at a time;
    # two states supply only a lower bound, since native workspace and other
    # processes can consume additional memory after admission.
    state_floor = 2 * max(state_bytes)
    if state_floor > admission_budget:
        raise ValueError("density states exceed the declared GPU memory admission budget")
    return {
        "snapshot": dict(snapshot),
        "active_qubits": widths,
        "density_state_bytes": state_bytes,
        "two_shot_state_floor_bytes": state_floor,
        "admission_budget_bytes": admission_budget,
        "minimum_free_bytes": MINIMUM_GPU_FREE_BYTES,
        "scope": "pre-run resource admission; Aer max_memory_mb is not a hard VRAM cap",
    }


def _verify() -> None:
    narrow = QuantumCircuit(156, 1)
    narrow.barrier()
    narrow.x(150)
    narrow.measure(150, 0)
    with narrow.if_test((narrow.clbits[0], True)):
        narrow.x(151)
    assert active_support(narrow) == 2
    wide = QuantumCircuit(9)
    wide.h(range(9))
    snapshot = {
        "device_ordinal": 0,
        "free_bytes": 768 * MEBIBYTE,
        "total_bytes": 12 * 1024 * MEBIBYTE,
        "runtime_version": 13040,
        "driver_version": 13040,
        "compute_capability_major": 8,
        "compute_capability_minor": 9,
    }
    assert admit_gpu([wide], 512, snapshot)["active_qubits"] == [9]
    admitted = admit_gpu([narrow], 512, snapshot)
    assert admitted["density_state_bytes"] == [256]
    assert admitted["admission_budget_bytes"] == 384 * MEBIBYTE
    for circuits, memory_mb, reading in (
        ([], 512, snapshot),
        ([narrow], 0, snapshot),
        ([narrow], True, snapshot),
        ([narrow], 512, snapshot | {"free_bytes": MINIMUM_GPU_FREE_BYTES - 1}),
        ([narrow], 512, snapshot | {"free_bytes": snapshot["total_bytes"] + 1}),
        ([narrow], 512, snapshot | {"compute_capability_minor": 0}),
        ([narrow], 512, snapshot | {"driver_version": 12090}),
        ([narrow], 512, snapshot | {"device_ordinal": 1}),
        ([narrow], 512, snapshot | {"runtime_version": True}),
    ):
        try:
            admit_gpu(circuits, memory_mb, reading)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid GPU resources passed admission")
    full_width = QuantumCircuit(8)
    full_width.h(range(8))
    try:
        admit_gpu([full_width], 1, snapshot)
    except ValueError:
        pass
    else:
        raise AssertionError("two density states exceeded the declared admission budget")
    print("native Aer support mapping and GPU resource rejection checks pass")


if __name__ == "__main__":
    _verify()
