"""Scratch probe: cuStateVec on/off, CPU parity hashes, ms/shot. Prints one JSON line per task."""
import hashlib
import json
import sys
import time

import qiskit_aer
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.random import random_circuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

SEED = 20261016


def noisy():
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(0.002, 1), ["u", "u1", "u2", "u3", "rz", "sx", "x", "h"])
    nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ["cx", "cz"])
    return nm


def rand_circuit(n, depth=8):
    qc = random_circuit(n, depth, max_operands=2, seed=1234)
    qc.measure_all()
    return qc


def ifelse_circuit():
    qc = QuantumCircuit(1, 2)
    qc.h(0)
    qc.measure(0, 0)
    with qc.if_test((qc.clbits[0], 1)):
        qc.x(0)
    qc.measure(0, 1)
    return qc


def digest(counts):
    return hashlib.sha256(json.dumps(sorted(counts.items())).encode()).hexdigest()[:16]


def run(label, sim, qc, shots):
    tqc = transpile(qc, sim, optimization_level=0, seed_transpiler=7)
    t0 = time.perf_counter()
    res = sim.run(tqc, shots=shots, seed_simulator=SEED).result()
    dt = time.perf_counter() - t0
    md = res.results[0].metadata
    out = {
        "label": label,
        "success": res.success,
        "status": res.status,
        "shots": shots,
        "seconds": round(dt, 3),
        "ms_per_shot": round(1e3 * dt / shots, 3),
        "digest": digest(res.get_counts()) if res.success else None,
        "meta": {k: md.get(k) for k in ("method", "device", "cuStateVec_enable", "batched_shots_optimization", "parallel_shots")},
    }
    print(json.dumps(out), flush=True)


def main():
    task = sys.argv[1]
    print(json.dumps({"aer_file": qiskit_aer.__file__, "version": qiskit_aer.__version__}), flush=True)
    if task == "parity":
        # CPU parity: seeded noisy circuits on every CPU method.
        for method in ("statevector", "density_matrix", "matrix_product_state", "stabilizer_not"):
            if method == "stabilizer_not":
                continue
            sim = AerSimulator(method=method, device="CPU", noise_model=noisy())
            run(f"cpu_{method}_noisy_8q", sim, rand_circuit(8, 6), 512)
        sim = AerSimulator(method="statevector", device="CPU")
        run("cpu_statevector_ifelse", sim, ifelse_circuit(), 2048)
        sim = AerSimulator(method="matrix_product_state", device="CPU")
        run("cpu_mps_ideal_12q", sim, rand_circuit(12, 8), 1024)
    else:
        n = int(sys.argv[2])
        shots = int(sys.argv[3])
        cus = task == "gpu_custatevec"
        dev = "CPU" if task == "cpu" else "GPU"
        opts = {"cuStateVec_enable": True} if cus else {}
        sim = AerSimulator(method="statevector", device=dev, noise_model=noisy(), **opts)
        run(f"{task}_noisy_{n}q", sim, rand_circuit(n), shots)
        sim = AerSimulator(method="statevector", device=dev, **opts)
        run(f"{task}_ideal_{n}q", sim, rand_circuit(n), 1024)
        sim = AerSimulator(method="statevector", device=dev, **opts)
        run(f"{task}_ifelse_1q", sim, ifelse_circuit(), 1024)


main()
