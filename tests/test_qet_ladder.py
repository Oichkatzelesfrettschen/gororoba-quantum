"""Contracts of the QET passivity-ladder campaign: exact laws, endpoints and the deferred-measurement check."""

from __future__ import annotations

import math

import numpy as np
from qiskit.quantum_info import Statevector

import qet_ladder as ladder


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
    if len(circuits) != 18:
        raise AssertionError(f"{len(circuits)} circuits, expected 18")
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
