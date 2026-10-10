"""Transpile both designs to a real backend and predict noisy outcomes.

Transpilation against ibm_fez uses the true heavy-hex coupling map, so the CZ
counts here are the routed cost, not the all-to-all lower bound. AerSimulator
.from_backend applies the backend's calibrated noise, giving the readout a design
needs to clear its falsifier. Backend properties and noise models are metadata;
nothing submits a QPU job.
"""
from __future__ import annotations

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService

from cd_core import sedenion_zero_divisors
from designs import design_a_associator, design_b_zero_divisor

SHOTS = 4096


def _p_bit0(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    zero = sum(c for k, c in counts.items() if k.replace(" ", "")[-1] == "0")
    return zero / total if total else 0.0


def main() -> None:
    service = QiskitRuntimeService()
    backend = service.backend("ibm_fez")
    print(f"backend {backend.name}: {backend.num_qubits} qubits")
    usage = service.usage()
    print(f"QPU budget: {usage['usage_remaining_seconds']} s remaining of "
          f"{usage['usage_limit_seconds']} s\n")

    noise = NoiseModel.from_backend(backend)
    sim = AerSimulator(noise_model=noise, coupling_map=backend.coupling_map)

    qc_a, k0, k1, _ = design_a_associator(1, 2)
    ta = transpile(qc_a, backend=backend, optimization_level=3)
    ca = sim.run(transpile(qc_a, sim, optimization_level=1), shots=SHOTS).result().get_counts()
    print("Design A (octonion associator, i,j=1,2):")
    print(f"  routed to ibm_fez: depth={ta.depth()} cz={ta.count_ops().get('cz', 0)}")
    print(f"  ideal readout bit = 1; noisy P1 = {1 - _p_bit0(ca):.3f}")

    (i, j), (k, el), s = sedenion_zero_divisors()[0]
    qc_zd = design_b_zero_divisor((i, j), (k, el), s)
    qc_ct = design_b_zero_divisor((i, j), (k, el), -s)
    tzd = transpile(qc_zd, backend=backend, optimization_level=3)
    czd = sim.run(transpile(qc_zd, sim, optimization_level=1), shots=SHOTS).result().get_counts()
    cct = sim.run(transpile(qc_ct, sim, optimization_level=1), shots=SHOTS).result().get_counts()
    p_zd, p_ct = _p_bit0(czd), _p_bit0(cct)
    print("\nDesign B (sedenion zero divisor):")
    print(f"  routed to ibm_fez: depth={tzd.depth()} cz={tzd.count_ops().get('cz', 0)}")
    print(f"  ideal P_zd=0 P_ct=1; noisy P_zd={p_zd:.3f} P_ct={p_ct:.3f} "
          f"ratio={p_zd / p_ct if p_ct else float('nan'):.3f}")


if __name__ == "__main__":
    main()
