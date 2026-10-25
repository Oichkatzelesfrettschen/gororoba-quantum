"""gororoba_quantum/primorial_cover.py and scripts/primorial_cover_noise.py: the retained certificates reproduce, the
exhaustive search finds covers where gaps exist, the eight-CNOT block implements exp(-i gamma H), and the gap-86
repair leaves every compiled circuit unchanged.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

import primorial_cover as pc

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/evidence/primorial_cover/certificates.json"


def _noise_module() -> Any:
    spec = importlib.util.spec_from_file_location("primorial_cover_noise", ROOT / "scripts/primorial_cover_noise.py")
    if spec is None or spec.loader is None:
        raise AssertionError("scripts/primorial_cover_noise.py does not load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_retained_certificates_reproduce() -> None:
    if RECORD.read_text(encoding="utf-8") != pc.render(pc.certificates()):
        raise AssertionError(f"{RECORD} departs from primorial_cover.certificates()")


def test_search_finds_existing_gaps_and_misses_none() -> None:
    for k, half in pc.POSITIVE_CONTROLS:
        if not pc.cover_exists(half, pc.odd_primes(k)):
            raise AssertionError(f"gap {2 * half} exists at k = {k} but the search finds no cover")
    if pc.cover_exists(10, pc.odd_primes(6)) or pc.cover_exists(16, pc.odd_primes(8)):
        raise AssertionError("the search covers a certified missing gap")


def test_crt_start_survives_with_the_witness_gaps() -> None:
    for (k, half), residues in pc.WITNESSES.items():
        x, modulus = pc.crt_start(pc.odd_primes(k), residues)
        if math.gcd(x, modulus) != 1 or sum(pc.wheel_gaps(x, modulus, half)) != 2 * half:
            raise AssertionError((k, half, x))


def test_cost_block_is_the_hamiltonian_evolution() -> None:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    noise = _noise_module()
    gamma = 2 * math.pi / 9
    for name in ("gap86", "gap88", "gap88_repaired"):
        table = noise.cost_table(name)
        circuit = QuantumCircuit(3)
        noise.cost_block(circuit, table, gamma)
        unitary = Operator(circuit).data
        target = np.diag(np.exp(-1j * gamma * np.asarray(table, dtype=float)))
        phase = unitary[0, 0] / target[0, 0]
        if not np.allclose(unitary, phase * target, atol=1e-10):
            raise AssertionError(f"{name}: the parity network departs from exp(-i gamma H)")
        if sum(1 for instruction in circuit.data if instruction.operation.name == "cx") != 8:
            raise AssertionError(f"{name}: the cost block does not use eight CNOTs")


def test_gap86_repair_changes_no_circuit() -> None:
    noise = _noise_module()
    plain, fixed = noise.cost_table("gap86"), noise.cost_table("gap86_repaired")
    for j, x in noise.edges():
        for basis in ("X", "Y"):
            if noise.gradient_arm(plain, j, x, basis) != noise.gradient_arm(fixed, j, x, basis):
                raise AssertionError(f"gap86 repair changes the edge ({j}, {x}) {basis} arm")
