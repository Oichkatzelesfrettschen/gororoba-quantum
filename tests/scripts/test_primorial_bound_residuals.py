"""scripts/primorial_bound_residuals.py: the numpy path simulator equals a qiskit statevector of the same timed
instructions under every error family at once, and the gate-error budgets match their closed forms.
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

import primorial_bound_residuals as br  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

# Timed instructions of a three-wire schedule with idle gaps: (name, wires, rz angle, duration in s).
OPS: list[br.Op] = [
    ("rz", (0,), 0.7, 0.0),
    ("sx", (0,), 0.0, 32e-9),
    ("sx", (1,), 0.0, 32e-9),
    ("x", (2,), 0.0, 32e-9),
    ("cz", (0, 1), 0.0, 68e-9),
    ("delay", (2,), 0.0, 100e-9),
    ("rz", (1,), -1.1, 0.0),
    ("sx", (1,), 0.0, 32e-9),
    ("cz", (1, 2), 0.0, 68e-9),
    ("sx", (2,), 0.0, 32e-9),
    ("x", (0,), 0.0, 32e-9),
    ("rz", (2,), 0.4, 0.0),
    ("cz", (0, 1), 0.0, 68e-9),
]
SPEC = {
    "tilt": (0.03, -0.02, 0.05),
    "amplitude": (0.01, -0.02, 0.015),
    "cz_phase": (0.09, -0.12),
    "detuning": (40.0, -25.0, 60.0),
    "zz": (30.0, -50.0),
    "zz_symmetric": (20.0, 45.0),
}


def reference(ops: list[br.Op], spec: dict[str, tuple[float, ...]]) -> np.ndarray:
    """The same schedule in qiskit gates, written independently of br.law."""
    khz = 1e3
    circuit = QuantumCircuit(3)
    starts = br.starts(ops)
    last: dict[int, float] = {}
    for (name, wires, angle, seconds), start in zip(ops, starts, strict=True):
        if name != "delay":
            if name != "rz":
                for c, pair in enumerate(((0, 1), (1, 2))):
                    if set(pair) & set(wires):
                        if c in last:
                            interval = start - last[c]
                            circuit.cp(-2 * math.pi * spec["zz"][c] * khz * interval, *pair)
                            circuit.rzz(math.pi * spec["zz_symmetric"][c] * khz * interval, *pair)
                        last[c] = start
            if name == "rz":
                circuit.rz(angle, wires[0])
            elif name in ("sx", "x"):
                q = wires[0]
                circuit.ry(spec["tilt"][q], q)
                circuit.rx((math.pi / 2 if name == "sx" else math.pi) * (1 + spec["amplitude"][q]), q)
                circuit.ry(-spec["tilt"][q], q)
            else:
                circuit.cz(*wires)
                circuit.cp(spec["cz_phase"][0 if wires == (0, 1) else 1], *wires)
        for q in wires:
            if seconds:
                circuit.rz(2 * math.pi * spec["detuning"][q] * khz * seconds, q)
    return np.asarray(Statevector(circuit).probabilities())


def test_numpy_law_equals_qiskit_under_every_family() -> None:
    got = np.asarray(br.law(OPS, SPEC))
    want = reference(OPS, SPEC)
    if not np.allclose(got, want, atol=1e-12):
        raise AssertionError(f"{got} against {want}")


def test_error_free_law_is_the_ideal_circuit() -> None:
    zero = {k: tuple(0.0 for _ in v) for k, v in SPEC.items()}
    got = np.asarray(br.law(OPS, {}))
    if not np.allclose(got, reference(OPS, zero), atol=1e-12):
        raise AssertionError(got)


def test_pure_tilt_budget_is_the_atlas_bound() -> None:
    r = 4e-4
    tilt, amplitude = br.scale_to_budget((1, 0), {"sx": r})
    if amplitude != 0.0 or abs(tilt - math.acos(2 * math.sqrt(1 - 1.5 * r) - 1)) > 1e-12:
        raise AssertionError(tilt)


def test_x_gate_tilt_infidelity_is_two_thirds_sine_squared() -> None:
    beta = 0.03
    got = br.infidelity(br.driven("x", beta, 0.0), br.X)
    if abs(got - (2 / 3) * math.sin(beta) ** 2) > 1e-15:
        raise AssertionError(got)
    tilt, _ = br.scale_to_budget((1, 0), {"sx": 4e-4, "x": 4e-4})
    if abs(tilt - math.asin(math.sqrt(1.5 * 4e-4))) > 1e-12:
        raise AssertionError(tilt)


def test_twirled_law_is_the_pauli_trajectory_average() -> None:
    ops = [op for op in OPS if op[0] != "delay"]
    spec = {"tilt": SPEC["tilt"], "amplitude": SPEC["amplitude"], "cz_phase": SPEC["cz_phase"]}
    cz_steps = [k for k, op in enumerate(ops) if op[0] == "cz"]
    want = np.zeros(8)
    for choice in itertools.product(range(4), repeat=len(cz_steps)):
        weight = 1.0
        trajectory: list[br.Op] = []
        inserted: dict[int, tuple[int, int]] = {}
        for step, pauli in zip(cz_steps, choice, strict=True):
            z_lo, z_hi = pauli & 1, pauli >> 1
            pair = (min(ops[step][1]), max(ops[step][1]))
            phi = spec["cz_phase"][0 if pair == (0, 1) else 1]
            d = (1.0, 1.0, 1.0, complex(math.cos(phi), math.sin(phi)))
            c = sum((-1) ** (z_lo * (b & 1) + z_hi * (b >> 1)) * d[b] for b in range(4)) / 4
            weight *= abs(c) ** 2
            inserted[step] = (z_lo, z_hi)
        for k, op in enumerate(ops):
            trajectory.append(op)
            if k in inserted:
                pair = (min(op[1]), max(op[1]))
                for wire, flag in zip(pair, inserted[k], strict=True):
                    if flag:
                        trajectory.append(("rz", (wire,), math.pi, 0.0))
        want += weight * np.asarray(br.law(trajectory, {"tilt": spec["tilt"], "amplitude": spec["amplitude"]}))
    got = np.asarray(br.twirled_law(ops, spec))
    if not np.allclose(got, want, atol=1e-12):
        raise AssertionError(f"{got} against {want}")


def test_twirled_law_without_phase_is_the_coherent_law() -> None:
    ops = [op for op in OPS if op[0] != "delay"]
    spec = {"tilt": SPEC["tilt"], "amplitude": SPEC["amplitude"]}
    if not np.allclose(br.twirled_law(ops, spec), br.law(ops, spec), atol=1e-12):
        raise AssertionError("twirled law departs at zero CZ phase")
