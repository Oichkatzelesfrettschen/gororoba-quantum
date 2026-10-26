"""Window-dose circuits keep the labeled law, charge their idle, and separate decay from detuning.

window_dose idles every qubit after the control's reset and window_dose_echo spends the same idle around two X
pulses on the work bits that hold the superposition. The tests evaluate the dynamic circuits exactly
(dynamic_density) after materializing Aer's relaxation channels on the delays, so no shot sampling enters.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Delay
from qiskit.transpiler import PassManager
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.passes import RelaxationNoisePass
from qiskit_ibm_runtime.fake_provider import FakeFez

import diagnostic_experiments
import dynamic_density
import qpe_diagnostics
from parallel import ordered_map

DT = 4e-9
DOSES = (0, 2000, 4000, 8000)
ONE, SIXTEEN = 1, 3


def _require(condition: bool, message: object = "") -> None:
    if not condition:
        raise AssertionError(message)


def _law(circuit: QuantumCircuit) -> np.ndarray:
    """Exact recorded distribution; a delay is the identity, so its relaxation channel (if any) alone acts."""
    bare = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name != "delay":
            bare.append(instruction)
    return dynamic_density.probabilities(bare, NoiseModel())


def _phase_contrast(distribution: np.ndarray) -> float:
    return float(distribution[1] - distribution[3])


def _relax(circuit: QuantumCircuit, t1_seconds: float, t2_seconds: float) -> QuantumCircuit:
    """The circuit with a relaxation channel after each top-level delay, as Aer's RelaxationNoisePass places it."""
    width = circuit.num_qubits
    return PassManager(
        RelaxationNoisePass(t1s=[t1_seconds] * width, t2s=[t2_seconds] * width, dt=DT, op_types=[Delay])
    ).run(circuit)


def _detune(circuit: QuantumCircuit, qubit: int, rate_per_dt: float) -> QuantumCircuit:
    """The circuit with a static Z rotation rate_per_dt * duration on qubit after each of its delays."""
    detuned = circuit.copy_empty_like()
    for instruction in circuit.data:
        detuned.append(instruction)
        if instruction.operation.name == "delay" and circuit.find_bit(instruction.qubits[0]).index == qubit:
            detuned.rz(rate_per_dt * instruction.operation.duration, qubit)
    return detuned


def _pair_contrast(job: tuple[str, int, float, float, float, bool]) -> float:
    """contrast_difference of one dose pair under relaxation (T1, T2) and a detuning rate on the work bit for 1."""
    variant, dose, t1, t2, rate, echo_pulses = job
    arms = []
    for feedback in (True, False):
        circuit = qpe_diagnostics.n21_orbit_diagnostic(feedback, variant, dose_dt=dose)
        if not echo_pulses:
            circuit = _without_window_pulses(circuit)
        if rate:
            circuit = _detune(circuit, ONE, rate)
        if t1 and t2:
            circuit = _relax(circuit, t1, t2)
        arms.append(_phase_contrast(_law(circuit)))
    return arms[0] - arms[1]


def _without_window_pulses(circuit: QuantumCircuit) -> QuantumCircuit:
    """The circuit without the dose window's X pulses; the one X that prepares the work register stays."""
    stripped = circuit.copy_empty_like()
    kept_preparation = False
    for instruction in circuit.data:
        if instruction.operation.name == "x":
            if not kept_preparation:
                kept_preparation = True
            else:
                continue
        stripped.append(instruction)
    return stripped


def _members(init_herald: bool) -> list[Any]:
    return list(diagnostic_experiments.n21_orbit_rca_group(415, 502, init_herald, window_doses=(0, 2000, 4000)).members)


def _ideal(member: Any) -> np.ndarray:
    return _law(member.circuit)


@pytest.mark.parametrize("init_herald", [False, True])
def test_every_member_keeps_the_labeled_law(init_herald: bool) -> None:
    members = _members(init_herald)
    _require(len(members) == 10)
    laws = ordered_map(_ideal, members, min_items=1)
    for member, law in zip(members, laws, strict=True):
        _require(np.allclose(law, member.ideal, atol=1e-12), member.name)
        key = qpe_diagnostics.n21_dose_key(member.name)
        _require(key is not None and qpe_diagnostics.n21_dose_name(*key) == member.name, member.name)


@pytest.mark.parametrize("init_herald", [False, True])
@pytest.mark.parametrize("variant", qpe_diagnostics.N21_DOSE_VARIANTS)
@pytest.mark.parametrize("feedback", [True, False])
def test_dose_zero_is_the_nominal_bracketed_program(init_herald: bool, variant: str, feedback: bool) -> None:
    dosed = qpe_diagnostics.n21_orbit_diagnostic(feedback, variant, dose_dt=0, init_herald=init_herald)
    nominal = qpe_diagnostics.n21_orbit_diagnostic(feedback, "nominal", init_herald=init_herald)
    _require(dosed.data == nominal.data)
    _require(not any(instruction.operation.name == "delay" for instruction in dosed.data))


@pytest.mark.parametrize("variant", qpe_diagnostics.N21_DOSE_VARIANTS)
def test_dose_delays_sit_at_the_top_level_of_every_qubit(variant: str) -> None:
    dose = 3500
    circuit = qpe_diagnostics.n21_orbit_diagnostic(True, variant, dose_dt=dose)
    per_qubit: dict[int, list[int]] = {qubit: [] for qubit in range(circuit.num_qubits)}
    for instruction in circuit.data:
        if instruction.operation.name == "delay":
            per_qubit[circuit.find_bit(instruction.qubits[0]).index].append(int(instruction.operation.duration))
        for block in getattr(instruction.operation, "blocks", ()):
            _require(not any(inner.operation.name == "delay" for inner in block.data))
    total = {qubit: sum(durations) for qubit, durations in per_qubit.items()}
    _require(total == {qubit: dose for qubit in range(circuit.num_qubits)})
    if variant == "window_dose":
        _require(all(durations == [dose] for durations in per_qubit.values()))
    else:
        _require(per_qubit[0] == per_qubit[2] == [dose])
        _require(per_qubit[ONE] == per_qubit[SIXTEEN] == [dose // 4, dose // 2, dose // 4])


def test_noise_model_relaxation_pass_charges_every_dose_delay() -> None:
    passes = NoiseModel.from_backend(FakeFez(), readout_error=False)._pass_manager()
    _require(passes is not None)
    for variant in qpe_diagnostics.N21_DOSE_VARIANTS:
        circuit = qpe_diagnostics.n21_orbit_diagnostic(True, variant, dose_dt=3500)
        delays = [circuit.find_bit(i.qubits[0]).index for i in circuit.data if i.operation.name == "delay"]
        relaxed = passes.run(circuit)
        charged = [relaxed.find_bit(i.qubits[0]).index for i in relaxed.data if i.operation.name == "quantum_channel"]
        _require(sorted(charged) == sorted(delays), (variant, charged, delays))
        _require(set(charged) == set(range(circuit.num_qubits)), (variant, charged))
        uncharged = passes.run(qpe_diagnostics.n21_orbit_diagnostic(True, variant, dose_dt=0))
        _require(not any(i.operation.name == "quantum_channel" for i in uncharged.data), variant)


def test_invalid_doses_and_conflicts_raise() -> None:
    for variant in qpe_diagnostics.N21_DOSE_VARIANTS:
        for bad in (-1, 1, 2.0, True, None):
            with pytest.raises(ValueError):
                qpe_diagnostics.n21_orbit_diagnostic(True, variant, dose_dt=bad)  # type: ignore[arg-type]
    for bad in (6, 4):
        with pytest.raises(ValueError):
            qpe_diagnostics.n21_orbit_diagnostic(True, "window_dose_echo", dose_dt=bad)
    with pytest.raises(ValueError):
        qpe_diagnostics.n21_orbit_diagnostic(True, "nominal", dose_dt=8)
    for bad_doses in ((0, 2000), (2000, 4000, 8000), (0, 1, 2000), (0, 2000, 2000), (0, -4, 2000), (0, 2000.0, 4000)):
        with pytest.raises(ValueError):
            diagnostic_experiments.n21_window_doses(bad_doses)
    _require(diagnostic_experiments.n21_window_doses((4000, 0, 2000)) == (0, 2000, 4000))
    configurations: dict[str, dict[str, Any]]
    for conflict in ("window_sweep", "overlap_split", "ground_control_split", "ramsey_windows", "segmented"):
        configurations = {
            "window_sweep": {"window_sweep": True},
            "overlap_split": {"overlap_split": True, "reset_dt": 520},
            "ground_control_split": {"ground_control_split": True, "reset_dt": 520},
            "ramsey_windows": {"ramsey_windows": (1, 2)},
            "segmented": {"segmented": {"delays_dt": [0, 2]}},
        }
        options = configurations[conflict]
        with pytest.raises(ValueError, match=f"window_doses excludes .*{conflict}"):
            diagnostic_experiments.n21_orbit_rca_group(415, 502, window_doses=(0, 2000, 4000), **options)
    _require(qpe_diagnostics.n21_dose_violations([0, 4096, 8192], 16, 2) == [])
    _require(len(qpe_diagnostics.n21_dose_violations([0, 4100], 16, 2)) == 1)
    _require(len(qpe_diagnostics.n21_dose_violations([0, 4112], 16, 2)) == 1)  # echo quarter off the grid


def test_group_summary_reports_contrast_difference_and_echo_gain() -> None:
    group = diagnostic_experiments.n21_orbit_rca_group(415, 502, window_doses=(0, 2000, 4000))
    laws = {member.name: np.asarray(member.ideal, dtype=float) for member in group.members}
    summary = group.summarize(laws)
    nominal = group.summarize(laws)["window_dose_d0_contrast_difference"]
    _require(
        math.isclose(
            nominal,
            _phase_contrast(laws["n21_orbit_window_dose_d0_feedback"])
            - _phase_contrast(laws["n21_orbit_window_dose_d0_no_feedback"]),
        )
    )
    _require(summary["window_dose_echo_gain_d2000"] == pytest.approx(0.0, abs=1e-12))
    _require("window_dose_echo_gain_d0" not in summary)
    _require("window_dose_echo_d0_contrast_difference" not in summary)


def test_relaxation_makes_the_contrast_decay_monotonically_with_dose() -> None:
    # T2 = 60 us, T1 = 10 ms: nearly pure dephasing of the work superposition, so the contrast difference decays
    # without the amplitude-damping sign change of a short T1.
    jobs = [("window_dose", dose, 10e-3, 60e-6, 0.0, True) for dose in DOSES]
    contrasts = ordered_map(_pair_contrast, jobs, min_items=1)
    _require(all(later < earlier - 1e-3 for earlier, later in zip(contrasts, contrasts[1:], strict=False)), contrasts)
    # Mutation: without relaxation the contrast does not move with the dose.
    flat = ordered_map(_pair_contrast, [("window_dose", dose, 0.0, 0.0, 0.0, True) for dose in DOSES], min_items=1)
    _require(max(flat) - min(flat) < 1e-9, flat)


def test_echo_restores_the_contrast_that_static_detuning_removes() -> None:
    # The nominal contrast difference is 0.354 sin(pi/4 - phi) for a relative phase phi between the |1> and |16>
    # branches, so a quarter turn of detuning of the bit for 1 over the longest dose drives it from 0.25 to -0.25.
    rate = -(math.pi / 2) / max(DOSES)
    nonzero = DOSES[1:]
    plain = ordered_map(_pair_contrast, [("window_dose", dose, 0.0, 0.0, rate, True) for dose in DOSES], min_items=1)
    echo = ordered_map(
        _pair_contrast, [("window_dose_echo", dose, 0.0, 0.0, rate, True) for dose in nonzero], min_items=1
    )
    # Mutation 1: the echo pulses removed leave the same detuning as the plain idle.
    unpulsed = ordered_map(
        _pair_contrast, [("window_dose_echo", dose, 0.0, 0.0, rate, False) for dose in nonzero], min_items=1
    )
    # Mutation 2: no detuning leaves the plain contrast at its dose-0 value.
    undetuned = ordered_map(_pair_contrast, [("window_dose", dose, 0.0, 0.0, 0.0, True) for dose in DOSES], min_items=1)
    _require(all(later < earlier - 1e-3 for earlier, later in zip(plain, plain[1:], strict=False)), plain)
    _require(all(abs(value - plain[0]) < 1e-9 for value in echo), (echo, plain))
    _require(all(abs(value - plain_value) < 1e-9 for value, plain_value in zip(unpulsed, plain[1:], strict=True)))
    _require(max(undetuned) - min(undetuned) < 1e-9, undetuned)


def _asap_starts(circuit: QuantumCircuit, durations: dict[str, int]) -> list[tuple[str, list[int], int]]:
    """(name, qubits, start) of every top-level instruction under an ASAP schedule whose barriers align their qubits."""
    cursor = dict.fromkeys(range(circuit.num_qubits), 0)
    out = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        start = max(cursor[q] for q in qubits)
        span = int(instruction.operation.duration) if name == "delay" else durations.get(name, 1)
        span = 0 if name == "barrier" else span
        for q in qubits:
            cursor[q] = start + span
        out.append((name, qubits, start))
    return out


@pytest.mark.parametrize("variant", ["window_dose", "window_dose_echo"])
def test_every_dose_delay_starts_after_the_control_reset_ends(variant: str) -> None:
    """Under ASAP with a long readout and reset, no work-wire dose delay or echo pulse starts before the reset ends."""
    circuit = qpe_diagnostics.n21_orbit_diagnostic(True, variant, window_delay_dt=416, echo_half_dt=512, dose_dt=3500)
    durations = {"measure": 1000, "reset": 1000}
    starts = _asap_starts(circuit, durations)
    reset_index = next(i for i, (name, _, _) in enumerate(starts) if name == "reset")
    reset_end = starts[reset_index][2] + durations["reset"]
    closing = next(i for i in range(len(starts) - 1, reset_index, -1) if starts[i][0] == "barrier")
    dose_ops = [entry for entry in starts[reset_index + 1 : closing] if entry[0] in ("delay", "x")]
    if not dose_ops:
        raise AssertionError("no dose instruction after the reset")
    early = [entry for entry in dose_ops if entry[2] < reset_end]
    if early:
        raise AssertionError(f"dose instructions start before the reset ends at {reset_end}: {early}")
