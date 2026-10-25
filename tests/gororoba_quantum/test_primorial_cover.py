"""gororoba_quantum/primorial_cover.py and scripts/primorial_cover_noise.py: the retained certificates reproduce, the
exhaustive search finds covers where gaps exist, the eight-CNOT block implements exp(-i gamma H), and the gap-86
repair leaves every compiled circuit unchanged, and the shot prices carry the variance of each phase correction.
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


def test_phase_variance_follows_the_corrections() -> None:
    """Assignment inversion scales each mean's binomial variance by 1 / (1 - a - b)^2, and null subtraction adds
    the null arm's phase variance; a finite-difference Jacobian of atan2 of the corrected means is the reference."""
    noise = _noise_module()
    x_obs, y_obs = np.asarray([0.61, -0.2]), np.asarray([-0.52, 0.83])
    a, b = np.asarray([0.01, 0.03]), np.asarray([0.04, 0.02])

    def phase(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return np.asarray(np.arctan2(noise.corrected(y, a, b), noise.corrected(x, a, b)))

    step = 1e-7
    dx = (phase(x_obs + step, y_obs) - phase(x_obs - step, y_obs)) / (2 * step)
    dy = (phase(x_obs, y_obs + step) - phase(x_obs, y_obs - step)) / (2 * step)
    reference = dx**2 * (1 - x_obs**2) + dy**2 * (1 - y_obs**2)
    got = noise.corrected_phase_variance(x_obs, y_obs, a, b)
    if not np.allclose(got, reference, rtol=1e-6):
        raise AssertionError(f"corrected phase variance {got} against the Jacobian reference {reference}")
    zero = np.zeros(2)
    if not np.allclose(
        noise.corrected_phase_variance(x_obs, y_obs, zero, zero), noise.raw_phase_variance(x_obs, y_obs)
    ):
        raise AssertionError("with no assignment error the corrected variance departs from the raw one")

    table = noise.cost_table("gap88")
    reads = [np.cos(np.arange(12) / 7.0) * 0.9, -np.sin(np.arange(12) / 7.0) * 0.9]
    null = (np.full(12, 0.95), np.full(12, 0.05))
    v_cost, v_null = noise.raw_phase_variance(*reads), noise.raw_phase_variance(*null)
    fit = noise.null_subtracted(table, *reads, null, v_cost, v_null)
    keys, w = noise.walsh_matrix()
    projector = w @ np.linalg.pinv(noise.incidence())
    expected = (projector**2) @ ((v_cost + v_null) / noise.GRADIENT_GAMMA**2)
    if not np.allclose([fit["per_shot_coefficient_variance"][k] for k in keys], expected):
        raise AssertionError("null subtraction does not add the null arm's phase variance")
