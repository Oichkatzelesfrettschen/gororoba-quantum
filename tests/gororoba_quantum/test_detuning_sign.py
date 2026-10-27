"""The detuning-sign test reads the work superposition's relative phase with its sign and each work bit's own offset.

The orbit's two quadratures turn with the frame offset of the work bit for 16 minus that of the bit for 1, in the
sense in which each bit's Ramsey phase turns with its own offset, and the echo returns the undosed phase. The tests
evaluate the dynamic circuits exactly (dynamic_density), with a static detuning written as a Z rotation after each
delay, so no shot sampling enters.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

import diagnostic_experiments
import dynamic_density
import qpe_diagnostics
from parallel import ordered_map

ONE, SIXTEEN = 1, 3
DOSES = (0, 1752, 3504, 7008)


def _require(condition: bool, message: object = "") -> None:
    if not condition:
        raise AssertionError(message)


def _detuned_law(job: tuple[QuantumCircuit, dict[int, float]]) -> np.ndarray:
    """Exact distribution with a Z rotation of rate * duration on each qubit after each of its delays."""
    circuit, rates = job
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name != "delay":
            out.append(instruction)
            continue
        for qubit in instruction.qubits:
            index = circuit.find_bit(qubit).index
            if rates.get(index):
                out.rz(rates[index] * instruction.operation.duration, index)
    return dynamic_density.probabilities(out, NoiseModel())


def _orbit_phase(x_law: np.ndarray, y_law: np.ndarray) -> float:
    """atan2 of the sine and cosine branch contrasts of the two orbit quadratures."""

    def branch(law: np.ndarray) -> float:
        p = qpe_diagnostics.phase_marginal(law)
        return float((p[0] - p[2]) / (p[0] + p[2]) - (p[1] - p[3]) / (p[1] + p[3]))

    return math.atan2(branch(y_law), branch(x_law))


def _ramsey_phase(x_law: np.ndarray, y_law: np.ndarray) -> float:
    reads = [float(np.asarray((1.0, 0.0, -1.0, 0.0)) @ qpe_diagnostics.phase_marginal(law)) for law in (x_law, y_law)]
    return math.atan2(reads[1], reads[0])


def _orbit_jobs(variant: str, dose: int, rates: dict[int, float]) -> list[tuple[QuantumCircuit, dict[int, float]]]:
    return [
        (qpe_diagnostics.n21_orbit_diagnostic(False, name, init_herald=True, dose_dt=dose), rates)
        for name in (variant, f"{variant}_y")
    ]


@pytest.mark.parametrize(("qubit", "sign"), [(SIXTEEN, 1.0), (ONE, -1.0)])
def test_orbit_quadratures_turn_with_sixteen_minus_one(qubit: int, sign: float) -> None:
    rate = 0.6 / DOSES[-1]
    laws = ordered_map(_detuned_law, _orbit_jobs("window_dose", DOSES[-1], {qubit: rate}), min_items=1)
    phase = _orbit_phase(*laws)
    _require(phase == pytest.approx(sign * 0.6, abs=1e-9), phase)
    # Mutation: an undetuned idle leaves the phase at zero.
    flat = ordered_map(_detuned_law, _orbit_jobs("window_dose", DOSES[-1], {}), min_items=1)
    _require(abs(_orbit_phase(*flat)) < 1e-9)


@pytest.mark.parametrize("role", ["one", "sixteen"])
def test_work_ramsey_turns_with_its_own_offset(role: str) -> None:
    qubit = qpe_diagnostics.N21_WORK_RAMSEY_QUBITS[role]
    rate = 0.6 / DOSES[-1]
    jobs = [
        (qpe_diagnostics.n21_work_ramsey(role, quadrature, DOSES[-1], init_herald=True), {qubit: rate})
        for quadrature in ("x", "y")
    ]
    phase = _ramsey_phase(*ordered_map(_detuned_law, jobs, min_items=1))
    _require(phase == pytest.approx(0.6, abs=1e-9), phase)
    # Mutation: the other work bit's offset leaves this bit's Ramsey phase at zero.
    other = SIXTEEN if qubit == ONE else ONE
    still = ordered_map(_detuned_law, [(circuit, {other: rate}) for circuit, _ in jobs], min_items=1)
    _require(abs(_ramsey_phase(*still)) < 1e-9)


def test_echo_returns_the_undosed_phase() -> None:
    rate = 0.6 / DOSES[-1]
    rates = {ONE: -0.4 * rate, SIXTEEN: rate}
    echo = _orbit_phase(*ordered_map(_detuned_law, _orbit_jobs("window_dose_echo", DOSES[-1], rates), min_items=1))
    plain = _orbit_phase(*ordered_map(_detuned_law, _orbit_jobs("window_dose", DOSES[-1], rates), min_items=1))
    _require(abs(echo) < 1e-9, echo)
    _require(plain == pytest.approx(1.4 * 0.6, abs=1e-9), plain)


def test_every_member_keeps_its_ideal_law() -> None:
    group = diagnostic_experiments.n21_orbit_rca_group(415, 502, True, window_doses=DOSES, detuning_sign=True)
    laws = ordered_map(_detuned_law, [(member.circuit, {}) for member in group.members], min_items=2)
    for member, law in zip(group.members, laws, strict=True):
        _require(np.allclose(law, member.ideal, atol=1e-9), member.name)


def test_group_arms_names_and_contracts() -> None:
    group = diagnostic_experiments.n21_orbit_rca_group(415, 502, True, window_doses=DOSES, detuning_sign=True)
    names = [member.name for member in group.members]
    _require(len(names) == 2 * len(DOSES) + 2 + 4 * len(DOSES) and len(set(names)) == len(names), names)
    _require(names[0] == qpe_diagnostics.n21_dose_name("window_dose", 0, False), names[0])
    for name in names:
        dose_key = qpe_diagnostics.n21_dose_key(name)
        ramsey_key = qpe_diagnostics.n21_work_ramsey_key(name)
        if name.startswith("n21_orbit_"):
            _require(dose_key is not None and qpe_diagnostics.n21_dose_name(*dose_key) == name, name)
        else:
            _require(ramsey_key is not None and qpe_diagnostics.n21_work_ramsey_name(*ramsey_key) == name, name)
    configuration = {"init_herald": True, "window_doses": list(DOSES), "detuning_sign": True}
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.1, 0.05, 0.8, configuration)
    _require([contract.name for contract in contracts] == [f"{name}_read" for name in names])
    _require(sum(contract.alpha for contract in contracts) == pytest.approx(0.05))
    summary = group.summarize({member.name: member.ideal for member in group.members})
    _require(summary["orbit_window_dose_d0_no_feedback_read"] == pytest.approx(0.5), summary)
    _require(summary["orbit_window_dose_y_d0_no_feedback_read"] == pytest.approx(0.0), summary)
    _require(summary[f"work_ramsey_one_x_d{DOSES[-1]}_read"] == pytest.approx(1.0), summary)


def test_refusals() -> None:
    with pytest.raises(ValueError, match="requires init_herald"):
        diagnostic_experiments.n21_orbit_rca_group(415, 502, False, window_doses=DOSES, detuning_sign=True)
    with pytest.raises(ValueError, match="window_doses configuration"):
        diagnostic_experiments.n21_orbit_rca_group(415, 502, True, detuning_sign=True)
    with pytest.raises(ValueError, match="without feed-forward"):
        qpe_diagnostics.n21_orbit_diagnostic(True, "window_dose_y", dose_dt=0)
    with pytest.raises(ValueError, match="no feed-forward arm"):
        qpe_diagnostics.n21_dose_name("window_dose_y", 0, True)
    _require(qpe_diagnostics.n21_dose_key("n21_orbit_window_dose_y_d0_feedback") is None)
    for bad in ("n21_work_ramsey_four_x_d0", "n21_work_ramsey_one_z_d0", "n21_work_ramsey_one_x_d1"):
        _require(qpe_diagnostics.n21_work_ramsey_key(bad) is None, bad)
