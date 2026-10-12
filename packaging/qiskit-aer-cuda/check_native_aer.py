"""Check native staged Aer CPU/CUDA loading and bounded dynamic noisy sampling."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sysconfig
from importlib.metadata import version
from pathlib import Path

import qiskit_aer
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    arguments = parser.parse_args()
    if not Path(qiskit_aer.__file__).resolve().is_relative_to(arguments.package_root.resolve()):
        raise RuntimeError("Aer import resolved outside the staged package")
    if version("qiskit-aer") != "0.17.2":
        raise RuntimeError("Aer distribution version differs from the pinned native source")
    metadata_path = Path(qiskit_aer.__file__).with_name("native_cuda_build.json")
    native_build = json.loads(metadata_path.read_text())
    if native_build["python_soabi"] != sysconfig.get_config_var("SOABI"):
        raise RuntimeError("native package metadata differs from the executing Python ABI")
    if native_build["cuda_architecture"] != "sm_89" or native_build["version"] != "0.17.2":
        raise RuntimeError("native package metadata differs from the target architecture/version")
    available = AerSimulator().available_devices()
    if "GPU" not in available or "CPU" not in available:
        raise RuntimeError(f"native CPU/CUDA devices are required, found {available}")

    circuit = QuantumCircuit(2, 2, name="reported_bit_reset_feed_forward")
    circuit.x(0)
    circuit.measure(0, 0)
    circuit.reset(0)
    with circuit.if_test((circuit.clbits[0], True)):
        circuit.x(1)
    circuit.measure(1, 1)
    noise = NoiseModel()
    noise.add_quantum_error(pauli_error([("X", 0.125), ("I", 0.875)]), "x", [0])
    noise.add_readout_error(ReadoutError([[0.9, 0.1], [0.2, 0.8]]), [0])
    shots = 2048
    alpha = 1e-9
    # Four labeled bins on each of two devices share one union-bound budget.
    radius = math.sqrt(math.log(2 * 8 / alpha) / (2 * shots))
    expected = {"00": 0.2875, "01": 0.0, "10": 0.0, "11": 0.7125}
    records = []
    for device in ("CPU", "GPU"):
        simulator = AerSimulator(
            method="density_matrix",
            device=device,
            precision="double",
            noise_model=noise,
            max_parallel_threads=2,
            max_parallel_experiments=1,
            max_parallel_shots=2,
            max_memory_mb=512,
            shot_branching_enable=False,
            shot_branching_sampling_enable=False,
            batched_shots_gpu=False,
            cuStateVec_enable=False,
        )
        result = simulator.run(circuit, shots=shots, seed_simulator=20261012).result()
        if not result.success or not result.results[0].success:
            raise RuntimeError(f"native {device} smoke circuit failed: {result.status}")
        metadata = result.results[0].metadata
        if metadata.get("device") != device or metadata.get("method") != "density_matrix":
            raise RuntimeError("native execution metadata differs from the requested device/method")
        if metadata.get("shot_branching_enabled", False):
            raise RuntimeError("native smoke test enabled prohibited shot branching")
        counts = result.get_counts(0)
        if sum(counts.values()) != shots:
            raise RuntimeError("native smoke test returned an incorrect shot total")
        maximum = max(abs(counts.get(label, 0) / shots - probability) for label, probability in expected.items())
        if maximum > radius:
            raise RuntimeError(f"native {device} noisy law differs by {maximum}, above {radius}")
        records.append({"device": device, "counts": counts, "maximum_bin_error": maximum, "metadata": metadata})
    print(
        json.dumps(
            {
                "state": "passed",
                "aer_version": version("qiskit-aer"),
                "native_build_metadata_sha256": hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
                "shots": shots,
                "familywise_alpha": alpha,
                "simultaneous_bin_radius": radius,
                "scope": "native package smoke test; full retained workload qualification remains separate",
                "records": records,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
