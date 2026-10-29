"""Qubit baseline twin simulation for octonion associator-character cross-platform validation.

This module provides the exact 3-qubit circuit twin of the 8-mode linear optical
associator-character interferometer implemented on Quandela Ascella (qpu:ascella / sim:ascella).

Isomorphism:
- Physical optical mode m in {0..7} <-> 3-qubit computational basis state |b_2 b_1 b_0>, m = sum_k b_k 2^k.
- 8-mode Walsh-Hadamard transform H_8 = H_2^{ox 3} <-> 3-qubit Hadamard layer H^{ox 3}.
- Diagonal phase matrix D(a,b) = diag(s(0)..s(7)) with character s(x) = (-1)^{omega . x}
  <-> Phase layer prod_{k=0}^2 Z_k^{omega_k}, where omega_k is bit k of frequency omega(a,b).
- Octonion arm: H^{ox 3} (prod_k Z_k^{omega_k}) H^{ox 3} |000> = prod_k (H Z_k^{omega_k} H) |000>
  = prod_k X_k^{omega_k} |000> = |omega(a,b)>.
- Clifford associative control arm: H^{ox 3} I H^{ox 3} |000> = |000>.
- Primary contrast: Delta = D_oct - D_ctrl = +1.0 - (-1.0) = 2.0.

Cross-platform validation:
This script can run against:
1. Qiskit Aer (AerSimulator) locally.
2. QX emulator / Quantum Inspire when credentials and network are configured.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from cd_core import cd_sign  # noqa: E402


def associator_sign(a: int, b: int, x: int) -> int:
    """The sign s(x) such that (e_a e_b) e_x = s(x) e_a (e_b e_x) in the octonions."""
    lhs = cd_sign(8, a, b) * cd_sign(8, a ^ b, x)
    rhs = cd_sign(8, b, x) * cd_sign(8, a, b ^ x)
    return int(lhs * rhs)


def get_character_frequency(a: int, b: int) -> int:
    """Extract omega in {1..7} such that s(x) = (-1)^{omega . x}."""
    w0 = 1 if associator_sign(a, b, 1) == -1 else 0
    w1 = 1 if associator_sign(a, b, 2) == -1 else 0
    w2 = 1 if associator_sign(a, b, 4) == -1 else 0
    return w0 | (w1 << 1) | (w2 << 2)


def build_twin_circuit(a: int, b: int, arm: str = "octonion") -> QuantumCircuit:
    """Build a 3-qubit circuit matching the 8-mode character interferometer."""
    qc = QuantumCircuit(3, 3)
    qc.h(range(3))

    if arm == "octonion":
        omega = get_character_frequency(a, b)
        for k in range(3):
            if (omega >> k) & 1:
                qc.z(k)
    elif arm in ("clifford_control", "diagonal_null"):
        pass  # Identity
    elif arm == "reversed":
        omega = get_character_frequency(b, a)
        for k in range(3):
            if (omega >> k) & 1:
                qc.z(k)
    else:
        raise ValueError(f"unknown arm: {arm!r}")

    qc.h(range(3))
    qc.measure(range(3), range(3))
    return qc


def run_aer_twin(shots: int = 4096) -> dict[str, Any]:
    """Execute all 4 primary triads across arms on Qiskit AerSimulator."""
    simulator = AerSimulator()
    pairs = ((1, 2), (1, 4), (2, 4), (3, 5))
    results: dict[str, Any] = {}

    for a, b in pairs:
        pair_key = f"pair_{a}_{b}"
        omega = get_character_frequency(a, b)
        target_bitstring = f"{omega:03b}"

        # Octonion arm
        qc_oct = build_twin_circuit(a, b, "octonion")
        counts_oct = simulator.run(qc_oct, shots=shots).result().get_counts()
        c_omega = counts_oct.get(target_bitstring, 0)
        c_0 = counts_oct.get("000", 0)
        d_oct = (c_omega - c_0) / max(1, c_omega + c_0)

        # Control arm
        qc_ctrl = build_twin_circuit(a, b, "clifford_control")
        counts_ctrl = simulator.run(qc_ctrl, shots=shots).result().get_counts()
        c_omega_ctrl = counts_ctrl.get(target_bitstring, 0)
        c_0_ctrl = counts_ctrl.get("000", 0)
        d_ctrl = (c_omega_ctrl - c_0_ctrl) / max(1, c_omega_ctrl + c_0_ctrl)

        contrast = d_oct - d_ctrl

        results[pair_key] = {
            "omega": omega,
            "target_bitstring": target_bitstring,
            "d_oct": round(d_oct, 6),
            "d_ctrl": round(d_ctrl, 6),
            "delta_character": round(contrast, 6),
            "counts_oct": counts_oct,
            "counts_ctrl": counts_ctrl,
        }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--shots", type=int, default=4096, help="shots per circuit")
    args = parser.parse_args()

    results = run_aer_twin(shots=args.shots)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
