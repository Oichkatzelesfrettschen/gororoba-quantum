"""Contracts of the QET passivity-ladder campaign: exact laws, endpoints and the deferred-measurement check."""

from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston

import qet_ladder as ladder
from parallel import ordered_map


def ideal() -> dict[str, np.ndarray]:
    return {name: law for name, _, law in ladder.circuits()}


def test_ideal_endpoints_match_the_closed_forms() -> None:
    summary = ladder.summarize(ideal())
    expected = {
        "channel_floor_margin": ladder.E_B,
        "information_excess": ladder.E_B,
        "contrast": math.sqrt(5) / 10,
        "q_eff": 0.0,
        "prod_information_excess": 0.5811388300841897,
        "prod_channel_floor_margin": -0.2472882947,
    }
    for key, value in expected.items():
        if abs(summary[key] - value) > 1e-7:
            raise AssertionError(f"{key} = {summary[key]}, expected {value}")
    signs = [math.copysign(1.0, summary[f"binned_drop_{key}"]) for key in ("++", "+-", "-+", "--")]
    if signs != [1.0, -1.0, -1.0, 1.0]:
        raise AssertionError(f"binned drops read {signs}")


def test_deferred_circuits_reproduce_every_ideal_law() -> None:
    for (name, _, law), (_, deferred, _) in zip(ladder.circuits(), ladder.circuits(deferred=True), strict=True):
        probabilities = Statevector(deferred.remove_final_measurements(inplace=False)).probabilities_dict()
        rebuilt = np.zeros(8)
        for key, p in probabilities.items():
            bob, alice = int(key[0]), int(key[1])
            rebuilt[alice + 2 * alice + 4 * bob] += p
        if np.abs(rebuilt - law).max() > 1e-12:
            raise AssertionError(f"{name}: deferred circuit departs from its ideal law")


def test_every_arm_is_dynamic_and_branches_on_alice() -> None:
    circuits = ladder.circuits()
    if len(circuits) != 19:
        raise AssertionError(f"{len(circuits)} circuits, expected 19")
    for name, circuit, _ in circuits:
        if not any(instruction.operation.name == "if_else" for instruction in circuit.data):
            raise AssertionError(f"{name} has no feed-forward branch")


def test_record_independent_feedback_mutant_is_caught() -> None:
    laws = ideal()
    for basis in "xz":
        # Bob ignores the record: the feedback law becomes the average of the two fixed-sign arms.
        laws[f"qet_ladder_fb_{basis}"] = (laws[f"qet_ladder_plus_{basis}"] + laws[f"qet_ladder_minus_{basis}"]) / 2
    summary = ladder.summarize(laws)
    if summary["channel_floor_margin"] > 0 or summary["information_excess"] > 0:
        raise AssertionError("a record-independent feedback arm kept a floor margin or an excess")


def channel(law: np.ndarray, flips: list[tuple[float, float]]) -> np.ndarray:
    """Pass a law over r + 2a + 4b through independent per-bit assignment channels (P(1|0), P(0|1))."""
    out = law.copy()
    for bit, (e0, e1) in enumerate(flips):
        mixed = np.zeros(8)
        for index, p in enumerate(out):
            stay = 1 - (e1 if (index >> bit) & 1 else e0)
            mixed[index] += stay * p
            mixed[index ^ (1 << bit)] += (1 - stay) * p
        out = mixed
    return out


def test_readout_correction_recovers_the_ideal_margin_and_raw_is_conservative() -> None:
    flips = [(0.004, 0.011), (0.006, 0.018), (0.009, 0.025)]
    noisy = {name: channel(law, flips) for name, law in ideal().items()}
    summary = ladder.summarize(noisy)
    if abs(summary["readout_corrected_channel_floor_margin"] - ladder.E_B) > 1e-9:
        raise AssertionError(f"corrected margin {summary['readout_corrected_channel_floor_margin']}")
    if not 0 < summary["channel_floor_margin"] < ladder.E_B:
        raise AssertionError(f"raw margin {summary['channel_floor_margin']} is not a conservative positive value")
    for bit, (e0, e1) in zip("rab", flips, strict=True):
        if (
            abs(summary[f"assignment_{bit}_p1_given_0"] - e0) > 1e-12
            or abs(summary[f"assignment_{bit}_p0_given_1"] - e1) > 1e-12
        ):
            raise AssertionError(f"assignment of bit {bit} not recovered")


BACKENDS = {"kingston": FakeKingston, "fez": FakeFez}
_CACHE: dict[str, object] = {}


def _backend(name: str) -> object:
    if name not in _CACHE:
        _CACHE[name] = BACKENDS[name]()
    return _CACHE[name]


def _route(item: tuple[str, QuantumCircuit]) -> QuantumCircuit:
    name, circuit = item
    backend = _backend(name)
    edge = next(iter(backend.target["cz"]))  # type: ignore[attr-defined]
    return transpile(circuit, backend=backend, initial_layout=list(edge), optimization_level=1)


def routed(name: str) -> list[QuantumCircuit]:
    return ordered_map(_route, [(name, circuit) for _, circuit, _ in ladder.circuits()])


def test_branch_durations_match_on_kingston_and_are_refused_on_fez() -> None:
    kingston, fez = _backend("kingston"), _backend("fez")
    if ladder.branch_duration_violations(routed("kingston"), kingston.target):  # type: ignore[attr-defined]
        raise AssertionError("Kingston branches should share one duration")
    if not ladder.branch_duration_violations(routed("fez"), fez.target):  # type: ignore[attr-defined]
        raise AssertionError("Fez's 6 dt sx makes the rotation branches shorter than the 16 dt idle")


def phased_law(prep_phase: float, post_phase: float, alice: str, basis: str) -> np.ndarray:
    """Ladder idle-arm law with a B phase inside the CX (prep_phase) or after it (post_phase)."""
    eye, hadamard = np.eye(2), np.array([[1, 1], [1, -1]]) / math.sqrt(2)

    def rz(angle: float) -> np.ndarray:
        return np.diag([np.exp(-0.5j * angle), np.exp(0.5j * angle)])

    psi = np.zeros(4, dtype=complex)
    psi[0] = 1.0
    psi = np.kron(ladder._ry(2 * ladder.THETA), eye) @ psi
    psi = np.diag([1, 1, 1, -1]) @ (np.kron(eye, hadamard) @ psi)
    psi = np.kron(eye, hadamard @ rz(prep_phase)) @ psi
    psi = np.kron(np.diag([1, -1]), rz(post_phase)) @ psi
    if alice == "x":
        psi = np.kron(hadamard, eye) @ psi
    change = {"x": hadamard, "y": hadamard @ np.diag([1, -1j]), "z": eye}[basis]
    law = np.zeros(8)
    for record in (0, 1):
        amplitudes = change @ psi.reshape(2, 2)[record]
        for b in (0, 1):
            law[3 * record + 4 * b] = abs(amplitudes[b]) ** 2
    return law


def frame_ideal() -> dict[str, np.ndarray]:
    return {name: law for name, _, law in ladder.frame_circuits()}


def test_frame_diagnostic_ideal_reads_full_parity_and_e_b() -> None:
    summary = ladder.summarize_frame(frame_ideal())
    for variant in (*ladder.FRAME_VARIANTS, "idle_short", "idle_long"):
        if abs(summary[f"{variant}_parity"] - 1) > 1e-12 or abs(summary[f"{variant}_window_phase"]) > 1e-9:
            raise AssertionError(f"{variant}: ideal parity or phase off")
    for variant in ("completed", "echo"):
        if abs(summary[f"{variant}_channel_floor_margin"] - ladder.E_B) > 1e-9:
            raise AssertionError(f"{variant}: ideal margin {summary[f'{variant}_channel_floor_margin']}")


def test_frame_diagnostic_recovers_a_planted_mid_cx_phase() -> None:
    laws = frame_ideal()
    for arm, alice, basis in (("za", "z", "z"), ("ref_y", "x", "y")):
        laws[f"qet_frame_diagnostic_asrun_{arm}"] = phased_law(0.92, 0.0, alice, basis)
    summary = ladder.summarize_frame(laws)
    if abs(summary["asrun_window_phase"] - 0.92) > 1e-9 or abs(summary["asrun_parity"] - math.cos(0.92)) > 1e-9:
        raise AssertionError(f"planted phase read as {summary['asrun_window_phase']}")
    if abs(summary["readout_induced_parity_loss"] - (1 - math.cos(0.92))) > 1e-9:
        raise AssertionError("idle-minus-asrun parity does not isolate the planted window phase")


def test_frame_arms_route_with_equal_branches_on_kingston() -> None:
    backend = _backend("kingston")
    isas = ordered_map(_route, [("kingston", c) for _, c, _ in ladder.frame_circuits()])
    if ladder.branch_duration_violations(isas, backend.target):  # type: ignore[attr-defined]
        raise AssertionError("frame-diagnostic branches differ in duration on Kingston")
    echo = next(isa for isa in isas if isa.name.endswith("echo_za"))
    if sum(1 for instruction in echo.data if instruction.operation.name == "x") < 2:
        raise AssertionError("transpilation cancelled the echo pulses")


def test_idle_sweep_recovers_a_planted_detuning_slope() -> None:
    laws = frame_ideal()
    slope = 0.001  # radians per dt
    for variant, wait in ladder.IDLE_SWEEP_DT.items():
        for arm, alice, basis in (("za", "z", "z"), ("ref_y", "x", "y")):
            laws[f"qet_frame_diagnostic_{variant}_{arm}"] = phased_law(slope * wait, 0.0, alice, basis)
    summary = ladder.summarize_frame(laws)
    slope_read, intercept = summary["idle_phase_slope_rad_per_dt"], summary["idle_phase_intercept_fit"]
    if abs(slope_read - slope) > 1e-9 or abs(intercept) > 1e-9:
        raise AssertionError(f"slope {slope_read}, intercept {intercept}")


def compensated_laws(window_phase: float) -> dict[str, np.ndarray]:
    return {
        f"qet_compensated_ladder_{name}": ladder.compensated_ideal(
            prep, alice, rule, basis, alpha, window_phase if prep == "ground" else 0.0
        )
        for name, prep, alice, rule, basis, alpha in ladder.compensated_arms()
    }


def test_compensated_ideal_matches_the_circuits_and_scores_e_b() -> None:
    circuits = {name: law for name, _, law in ladder.compensated_circuits()}
    for name, law in compensated_laws(0.0).items():
        if np.abs(circuits[name] - law).max() > 1e-12:
            raise AssertionError(f"{name}: compensated ideal departs from the circuit's law")
    summary = ladder.summarize_compensated(compensated_laws(0.0))
    if summary["selected_alpha"] != 0.0 or abs(summary["selected_margin"] - ladder.E_B) > 1e-9:
        raise AssertionError(f"ideal selects {summary['selected_alpha']} with margin {summary['selected_margin']}")


def test_compensation_undoes_a_planted_window_phase() -> None:
    summary = ladder.summarize_compensated(compensated_laws(-0.6))
    if abs(summary["reference_phase"] + 0.6) > 1e-9 or summary["selected_alpha"] != 0.6:
        raise AssertionError(f"phase {summary['reference_phase']} selects {summary['selected_alpha']}")
    if abs(summary["selected_margin"] - ladder.E_B) > 1e-9 or summary["uncompensated_margin"] > 0:
        raise AssertionError(
            f"compensated {summary['selected_margin']}, uncompensated {summary['uncompensated_margin']}"
        )


def test_compensated_arms_route_with_equal_branches_on_kingston() -> None:
    backend = _backend("kingston")
    isas = ordered_map(_route, [("kingston", c) for _, c, _ in ladder.compensated_circuits()])
    if ladder.branch_duration_violations(isas, backend.target):  # type: ignore[attr-defined]
        raise AssertionError("compensated branches differ in duration on Kingston")
