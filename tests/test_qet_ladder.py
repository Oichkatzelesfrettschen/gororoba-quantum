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
