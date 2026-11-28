"""ibm_dd_compare: the baseline carries no pulses, and DD refocuses a modeled quasi-static detuning."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("qiskit_ibm_runtime")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import ibm_dd_compare as dd  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def reports() -> dict[str, dict[str, dict[str, float]]]:
    """Arms of the idle fixture without and with the modeled detuning, simulated once for the module."""
    name, target, props = dd.load_target("fake:fez")
    out = {}
    for label, hz in (("still", 0.0), ("moving", dd.QUARTER_TURN_HZ)):
        report = dd.compare([dd.idle_fixture()], name, target, props, shots=4000, detuning_hz=hz, layout=[0, 1])
        out[label] = report["cases"]["idle_ramsey"]["arms"]
    return out


def test_baseline_has_idle_and_no_pulses() -> None:
    _, target, _ = dd.load_target("fake:fez")
    isa = dd.compile_cases([dd.idle_fixture()], target, None, [0, 1])
    arms = dd.schedule_arms(isa, "fake_fez", target, dd.SEQUENCES, 0.0)
    active = dd.active_qubits(isa[0])
    base = dd.pulse_and_delay_counts(arms[(0, "baseline")], active)
    require(base["x"] == 0, "baseline plays no pulse")
    require(base["delay_dt"] >= 20000, "baseline keeps the idle window")
    for sequence in dd.SEQUENCES:
        require(dd.pulse_and_delay_counts(arms[(0, sequence)], active)["x"] >= 2, sequence + " inserts pulses")
        durations = {arms[(0, a)].estimate_duration(target, unit="dt") for a in ("baseline", sequence)}
        require(len(durations) == 1, sequence + " keeps the duration")


@pytest.mark.audit
def test_dd_refocuses_modeled_detuning(reports: dict[str, dict[str, dict[str, float]]]) -> None:
    still, moving = reports["still"], reports["moving"]
    # The detuning costs the baseline its remaining contrast; DD restores the undetuned distance.
    require(
        moving["baseline"]["tvd_to_ideal"] - still["baseline"]["tvd_to_ideal"] > 0.04,
        'moving["baseline"]["tvd_to_ideal"] - still["baseline"]["tvd_',
    )
    for sequence in dd.SEQUENCES:
        require(
            abs(moving[sequence]["tvd_to_ideal"] - still[sequence]["tvd_to_ideal"]) < 0.04,
            'abs(moving[sequence]["tvd_to_ideal"] - still[sequence]["tvd_',
        )
        require(moving[sequence]["tvd_gain_over_baseline"] > 0.03, 'moving[sequence]["tvd_gain_over_baseline"] > 0.03')


@pytest.mark.audit
def test_markovian_noise_alone_gives_dd_no_credit(reports: dict[str, dict[str, dict[str, float]]]) -> None:
    for row in reports["still"].values():
        require(row["tvd_gain_over_baseline"] < 0.06, 'row["tvd_gain_over_baseline"] < 0.06')


def test_control_flow_is_refused() -> None:
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(1, 1)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.x(0)
    require(dd.refusal(circuit) is not None, "dd.refusal(circuit) is not None")


def test_tvd_standard_error_is_the_binomial_error_fraction_for_a_deterministic_ideal() -> None:
    import math

    import numpy as np

    law = np.array([0.276, 0.724])
    ideal = np.array([0.0, 1.0])
    expected = 0.5 * math.sqrt(4.0 * 0.276 * 0.724 / 4000)
    require(abs(dd.tvd_standard_error(law, ideal, 4000) - expected) < 1e-12, "the multinomial covariance is used")
    require(abs(expected - 0.00707) < 1e-4, "the retained 0.276 case gives 0.00707, not 0.00500")
