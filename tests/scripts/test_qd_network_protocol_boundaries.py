"""Physical negative controls and the boundary between a numerical score and admitted evidence.

Terminal laws come from the optical unitary with receiver basis rotations,
independently of receiver_states and its projector-based scoring fixtures.
The side-information controls deliberately violate the common-instrument
assumptions: their large numerical scores establish why record admission
must check those assumptions before interpreting a score.
"""

from __future__ import annotations

from collections import Counter
from functools import partial
from typing import TypeAlias

import numpy as np
import pytest
import qd_network_protocol as protocol

from parallel import ordered_map

JointKey: TypeAlias = tuple[str, str, str, int]
Histogram: TypeAlias = dict[JointKey, int]
Resource: TypeAlias = tuple[tuple[float, protocol.FockState], ...]

FRAMES = {"1100": (1, 0), "0011": (1, 0), "1001": (1, 1), "0110": (1, 1)}
ATTEMPTS_PER_CELL = 256
READOUT = {
    "X": np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2.0),
    "Y": np.array([[1, -1j], [1, 1j]], dtype=complex) / np.sqrt(2.0),
    "Z": np.eye(2, dtype=complex),
}


def terminal_cell(task: tuple[str, tuple[complex, complex], str], resource: Resource) -> Histogram:
    """Integer expected counts after the Bell optics and an independent receiver basis rotation."""
    label, amplitudes, basis = task
    unitary = protocol.embed([(protocol.analyzer_unitary(), (0, 1, 2, 3)), (READOUT[basis], (4, 5))], 6)
    probabilities: dict[JointKey, float] = {}
    for mixture_weight, component in resource:
        output = protocol.propagate(unitary, protocol.tensor(protocol.dual_rail_qubit(*amplitudes), component))
        for occupation, amplitude in output.items():
            pattern = protocol.click(occupation[:4])
            if pattern not in FRAMES:
                continue
            receiver = occupation[4:]
            if receiver not in ((1, 0), (0, 1)):
                raise AssertionError(f"the reference optical model leaves dual rail: {receiver}")
            key = (label, basis, pattern, 0 if receiver == (1, 0) else 1)
            probabilities[key] = probabilities.get(key, 0.0) + mixture_weight * abs(amplitude) ** 2
    counts = {}
    for key, probability in probabilities.items():
        expected = ATTEMPTS_PER_CELL * probability
        if abs(expected - round(expected)) > 1e-9:
            raise AssertionError(f"the finite control has a noninteger expected count: {expected}")
        if round(expected):
            counts[key] = round(expected)
    return counts


def terminal_histogram(resource: Resource) -> Histogram:
    tasks = [(label, amplitudes, basis) for label, amplitudes, _, _ in protocol.SIX_STATES for basis in "XYZ"]
    cells = ordered_map(partial(terminal_cell, resource=resource), tasks)
    return {key: count for cell in cells for key, count in cell.items()}


@pytest.fixture(scope="module")
def ideal_joint() -> Histogram:
    return terminal_histogram(((1.0, protocol.dual_rail_pair("phi+")),))


def marginals(histogram: Histogram) -> tuple[Counter[tuple[str, str, str]], Counter[tuple[str, str, int]]]:
    bells: Counter[tuple[str, str, str]] = Counter()
    receivers: Counter[tuple[str, str, int]] = Counter()
    for (label, basis, pattern, raw), count in histogram.items():
        bells[(label, basis, pattern)] += count
        receivers[(label, basis, raw)] += count
    return bells, receivers


@pytest.mark.parametrize("resource_kind, preserved_axis", [("product-plus", "X"), ("dephased-bell", "Z")])
def test_separable_optical_resources_reach_only_the_classical_bound(resource_kind: str, preserved_axis: str) -> None:
    if resource_kind == "product-plus":
        plus = protocol.dual_rail_qubit(protocol.SQRT_HALF, protocol.SQRT_HALF)
        resource: Resource = ((1.0, protocol.tensor(plus, plus)),)
    else:
        zero = protocol.dual_rail_qubit(1.0, 0.0)
        one = protocol.dual_rail_qubit(0.0, 1.0)
        resource = ((0.5, protocol.tensor(zero, zero)), (0.5, protocol.tensor(one, one)))
    histogram = terminal_histogram(resource)
    attempts = {label: 3 * ATTEMPTS_PER_CELL for label, _, _, _ in protocol.SIX_STATES}
    scores = protocol.joint_teleportation_scores(histogram, FRAMES, attempts)
    expected = {label: 1.0 if axis == preserved_axis else 0.5 for label, _, axis, _ in protocol.SIX_STATES}
    if scores["conditional_fidelity"] != expected:
        raise AssertionError((resource_kind, scores["conditional_fidelity"]))
    if scores["pooled_conditional_fidelity"] != pytest.approx(2.0 / 3.0):
        raise AssertionError((resource_kind, scores["pooled_conditional_fidelity"]))
    if scores["success_rate"] != dict.fromkeys(attempts, 0.5):
        raise AssertionError((resource_kind, scores["success_rate"]))


def test_destroying_joint_association_preserves_both_marginals_but_removes_advantage(ideal_joint: Histogram) -> None:
    bells, receivers = marginals(ideal_joint)
    independent = {}
    for label, _, _, _ in protocol.SIX_STATES:
        for basis in "XYZ":
            total = sum(receivers[(label, basis, raw)] for raw in (0, 1))
            for pattern in FRAMES:
                for raw in (0, 1):
                    numerator = bells[(label, basis, pattern)] * receivers[(label, basis, raw)]
                    count, remainder = divmod(numerator, total)
                    if remainder != 0:
                        raise AssertionError("factorization does not give integer control counts")
                    if count:
                        independent[(label, basis, pattern, raw)] = count
    if marginals(independent) != marginals(ideal_joint):
        raise AssertionError("factorization changes the Bell or receiver marginals")
    original = protocol.joint_teleportation_scores(ideal_joint, FRAMES)
    shuffled = protocol.joint_teleportation_scores(independent, FRAMES)
    if original["pooled_conditional_fidelity"] != 1.0:
        raise AssertionError(original)
    if shuffled["conditional_fidelity"] != {"+Z": 1.0, "-Z": 1.0, "+X": 0.5, "-X": 0.5, "+Y": 0.5, "-Y": 0.5}:
        raise AssertionError(shuffled)
    if shuffled["pooled_conditional_fidelity"] != pytest.approx(2.0 / 3.0):
        raise AssertionError(shuffled)


def test_missing_phase_correction_changes_y_as_well_as_x(ideal_joint: Histogram) -> None:
    without_z = {pattern: (x, 0) for pattern, (x, _) in FRAMES.items()}
    correct = protocol.joint_teleportation_scores(ideal_joint, FRAMES)
    wrong = protocol.joint_teleportation_scores(ideal_joint, without_z)
    if correct["conditional_fidelity"] != dict.fromkeys((label for label, _, _, _ in protocol.SIX_STATES), 1.0):
        raise AssertionError(correct)
    if wrong["conditional_fidelity"] != {"+Z": 1.0, "-Z": 1.0, "+X": 0.5, "-X": 0.5, "+Y": 0.5, "-Y": 0.5}:
        raise AssertionError(wrong)


def test_zero_success_input_has_a_pooled_model_but_no_six_conditional_scores() -> None:
    zero = protocol.dual_rail_qubit(1.0, 0.0)
    histogram = terminal_histogram(((1.0, protocol.tensor(zero, zero)),))
    if any(label == "+Z" for label, _, _, _ in histogram):
        raise AssertionError("the product resource accepts the impossible +Z input")
    minus_z = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
    fidelity, success = protocol.success_weighted_fidelity([(minus_z, minus_z)])
    if (fidelity, success) != pytest.approx((2.0 / 3.0, 0.5)):
        raise AssertionError((fidelity, success))
    with pytest.raises(protocol.ProtocolError, match="no matching-basis trials"):
        protocol.joint_teleportation_scores(histogram, FRAMES)


def test_input_label_side_information_can_forge_a_perfect_arithmetic_score() -> None:
    # A classical program knows the input label and writes the raw bit that the declared frame decodes to it.
    # This fixture carries no distributed resource or quantum-state transfer; its score cannot certify either.
    fabricated: Histogram = {}
    for label, _, matching_axis, sign in protocol.SIX_STATES:
        for basis in "XYZ":
            if basis == matching_axis:
                raw = (0 if sign == 1 else 1) ^ (1 if basis in ("Y", "Z") else 0)
                fabricated[(label, basis, "1100", raw)] = ATTEMPTS_PER_CELL
            else:
                for raw in (0, 1):
                    fabricated[(label, basis, "1100", raw)] = ATTEMPTS_PER_CELL // 2
    scores = protocol.joint_teleportation_scores(fabricated, FRAMES)
    if scores["pooled_conditional_fidelity"] != 1.0:
        raise AssertionError(scores)
    if scores["success_rate"] is not None:
        raise AssertionError("a sample-only fabricated record supplies a physical success rate")


def test_basis_conditioned_product_preparation_can_forge_the_witness() -> None:
    # Three different product states supply XX=+1, YY=-1 and ZZ=+1. No single resource supplies the tuple.
    directions = {"X": ((1, 0, 0), (1, 0, 0)), "Y": ((0, 1, 0), (0, -1, 0)), "Z": ((0, 0, 1), (0, 0, 1))}
    selected = {}
    for basis, (left, right) in directions.items():
        product = np.kron(protocol.bloch_projector(left), protocol.bloch_projector(right))
        correlators = {
            axis: float(np.trace(product @ np.kron(protocol.PAULI[axis], protocol.PAULI[axis])).real) for axis in "XYZ"
        }
        if protocol.bell_fidelity(correlators["X"], correlators["Y"], correlators["Z"]) != pytest.approx(0.5):
            raise AssertionError((basis, correlators))
        selected[basis] = correlators[basis]
    if protocol.bell_fidelity(selected["X"], selected["Y"], selected["Z"]) != 1.0:
        raise AssertionError(selected)
