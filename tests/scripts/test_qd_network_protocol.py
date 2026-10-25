"""Contract for qd_network_protocol: the ideal dual-rail instrument reproduces the design's analyzer, frame,
reference and sequential tables from the bosonic transform, the decision counts follow their formulas, and the
scoring path refuses evidence that cannot support a teleportation statement.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable
from typing import Any

import numpy as np
import pytest
import qd_network_protocol as protocol

# Design table: accepted threshold patterns in output order [c0, c1, d0, d1] and the receiver frame (x, z).
DESIGN_PATTERNS = {"1100": "psi+", "0011": "psi+", "1001": "psi-", "0110": "psi-"}
DESIGN_FRAMES = {"1100": (1, 0), "0011": (1, 0), "1001": (1, 1), "0110": (1, 1)}


def fixed_unitary(modes: int) -> np.ndarray:
    """A dense non-symmetric unitary: the discrete Fourier matrix with unequal input and output phases."""
    index = np.arange(modes)
    fourier = np.exp(2j * math.pi * np.outer(index, index) / modes) / math.sqrt(modes)
    return np.diag(np.exp(0.3j * index)) @ fourier @ np.diag(np.exp(0.7j * index**2))


def close(left: dict, right: dict) -> bool:
    return set(left) == set(right) and all(abs(left[key] - right[key]) < 1e-10 for key in left)


def test_sparse_propagation_matches_permanents() -> None:
    for modes, photons in ((4, 2), (6, 3), (8, 4)):
        unitary = fixed_unitary(modes)
        state = {
            occupation: complex(1 + rank) for rank, occupation in enumerate(protocol.occupations(modes, photons)[:3])
        }
        norm = math.sqrt(sum(abs(value) ** 2 for value in state.values()))
        state = {key: value / norm for key, value in state.items()}
        sparse = protocol.propagate(unitary, state)
        dense = protocol.propagate_by_permanents(unitary, state)
        if not close(sparse, dense):
            raise AssertionError((modes, photons))
        if abs(sum(abs(value) ** 2 for value in sparse.values()) - 1.0) > 1e-12:
            raise AssertionError("propagation does not preserve the norm")


def test_propagation_matches_perceval_slos() -> None:
    pcvl = pytest.importorskip("perceval")
    unitary = fixed_unitary(6)
    backend = pcvl.SLOSBackend()
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    for source in ((1, 0, 1, 0, 1, 0), (2, 0, 0, 1, 0, 0), (0, 1, 1, 0, 0, 1)):
        backend.set_input_state(pcvl.BasicState(list(source)))
        ours = protocol.propagate(unitary, {source: 1.0 + 0.0j})
        for target in protocol.occupations(6, 3):
            theirs = complex(backend.prob_amplitude(pcvl.BasicState(list(target))))
            if abs(theirs - ours.get(target, 0.0)) > 1e-10:
                raise AssertionError((source, target, theirs, ours.get(target)))


def test_bell_analyzer_reproduces_design_table() -> None:
    table = protocol.bell_pattern_table()
    accepted = {pattern: row["label"] for pattern, row in table.items() if row["accepted"]}
    if accepted != DESIGN_PATTERNS:
        raise AssertionError(accepted)
    for pattern, row in table.items():
        if not row["accepted"] and set(row["bell_inputs"]) != {"phi+", "phi-"}:
            raise AssertionError((pattern, row))


def test_teleportation_frames_success_and_fidelity() -> None:
    teleport = protocol.teleportation_frames()
    if teleport.frames != DESIGN_FRAMES:
        raise AssertionError(teleport.frames)
    for label, probability in teleport.success_probability.items():
        if abs(probability - 0.5) > 1e-12:
            raise AssertionError((label, probability))
    if any(abs(value - 1.0) > 1e-12 for value in teleport.fidelity.values()):
        raise AssertionError(teleport.fidelity)


def test_decoder_table() -> None:
    for raw, x, z in itertools.product((0, 1), repeat=3):
        expected = {"Z": raw ^ x, "X": raw ^ z, "Y": raw ^ x ^ z}
        for basis, bit in expected.items():
            if protocol.decode_bit(basis, raw, x, z) != bit:
                raise AssertionError((basis, raw, x, z))
    with pytest.raises(protocol.ProtocolError):
        protocol.decode_bit("W", 0, 0, 0)


def test_reference_entanglement_survives_the_transfer() -> None:
    fidelity = protocol.reference_preservation()
    if set(fidelity) != set(DESIGN_FRAMES) or any(abs(value - 1.0) > 1e-12 for value in fidelity.values()):
        raise AssertionError(fidelity)


def test_sequential_frames_compose_by_xor() -> None:
    composed = protocol.sequential_frames()
    if len(composed) != 16:
        raise AssertionError(len(composed))
    for (first, second), frame in composed.items():
        x1, z1 = DESIGN_FRAMES[first]
        x2, z2 = DESIGN_FRAMES[second]
        if frame != (x1 ^ x2, z1 ^ z2):
            raise AssertionError((first, second, frame))


def test_design_counts_follow_their_formulas() -> None:
    if (protocol.pairs_per_axis(0.01, 0.03), protocol.pairs_per_axis(0.002, 0.03)) != (1919, 2590):
        raise AssertionError("witness pair counts")
    if (
        protocol.witness_radius(0.002, 2590, 2590, 2590) > 0.03
        or protocol.witness_radius(0.002, 2589, 2589, 2589) <= 0.03
    ):
        raise AssertionError("2590 is not the smallest equal count at radius 0.03")
    counts = [protocol.bernoulli_decision_count(0.01, 0.10, score, 2.0 / 3.0, 0.02) for score in (0.75, 0.80, 0.90)]
    if counts != [1673, 523, 148]:
        raise AssertionError(counts)
    if (
        abs(protocol.two_hop_depolarizing(0.80) - 0.68) > 1e-12
        or abs(protocol.two_hop_depolarizing(0.75) - 0.625) > 1e-12
    ):
        raise AssertionError("two-hop composition")
    if abs(protocol.two_hop_depolarizing(protocol.TWO_HOP_CLASSICAL_THRESHOLD) - 2.0 / 3.0) > 1e-12:
        raise AssertionError("two-hop threshold")
    dimensions = [protocol.fock_dimension(2 * n, n) for n in (3, 4, 5, 6)] + [protocol.fock_dimension(24, 12)]
    if dimensions != [56, 330, 2002, 12376, 834451800]:
        raise AssertionError(dimensions)
    if (protocol.click_pattern_count(12, 6), protocol.click_pattern_count(24, 12)) != (2509, 9740685):
        raise AssertionError("click pattern counts")
    with pytest.raises(protocol.ProtocolError):
        protocol.bernoulli_decision_count(0.01, 0.10, 0.68, 2.0 / 3.0, 0.02)


def test_measure_and_prepare_instruments_stay_at_or_below_two_thirds() -> None:
    results = protocol.measure_and_prepare_grid()
    if len(results) != 26 * 26 * 3:
        raise AssertionError(len(results))
    for fidelity, success in results:
        if success <= 0.0 or fidelity > 2.0 / 3.0 + 1e-12:
            raise AssertionError((fidelity, success))
    if abs(max(fidelity for fidelity, _ in results) - 2.0 / 3.0) > 1e-12:
        raise AssertionError("the grid does not reach the 2/3 bound")


def ideal_histogram(resource: str, trials_per_cell: int) -> dict[tuple[str, str, str, int], int]:
    """Expected joint counts of the ideal instrument; every probability is a multiple of 1/8, so they are integers."""
    histogram = {}
    for label, per_pattern in protocol.receiver_states(resource).items():
        for basis in ("X", "Y", "Z"):
            projector = protocol.bloch_projector(np.array([basis == axis for axis in "XYZ"], dtype=float))
            for pattern, (probability, vector) in per_pattern.items():
                plus = float(np.vdot(vector, projector @ vector).real)
                for raw, weight in ((0, plus), (1, 1.0 - plus)):
                    count = trials_per_cell * probability * weight
                    if abs(count - round(count)) > 1e-6:
                        raise AssertionError(count)
                    if round(count):
                        histogram[(label, basis, pattern, raw)] = round(count)
    return histogram


def test_joint_scores_of_the_ideal_instrument() -> None:
    histogram = ideal_histogram("phi+", 800)
    scores = protocol.joint_teleportation_scores(histogram, DESIGN_FRAMES)
    if (
        scores["mean_conditional_fidelity"] != 1.0
        or scores["pooled_conditional_fidelity"] != 1.0
        or scores["success_rate"] is not None
    ):
        raise AssertionError(scores)
    # 800 attempts in each of the three receiver bases of every input.
    attempts = {label: 3 * 800 for label, _, _, _ in protocol.SIX_STATES}
    with_rate = protocol.joint_teleportation_scores(histogram, DESIGN_FRAMES, attempts)
    if with_rate["success_rate"] != {label: 0.5 for label in attempts}:
        raise AssertionError(with_rate["success_rate"])


def test_wrong_resource_and_swapped_frames_fail_on_the_predicted_inputs() -> None:
    wrong_resource = protocol.joint_teleportation_scores(ideal_histogram("phi-", 800), DESIGN_FRAMES)[
        "conditional_fidelity"
    ]
    if wrong_resource != {"+Z": 1.0, "-Z": 1.0, "+X": 0.0, "-X": 0.0, "+Y": 0.0, "-Y": 0.0}:
        raise AssertionError(wrong_resource)
    swapped = {pattern: (z, x) for pattern, (x, z) in DESIGN_FRAMES.items()}
    scores = protocol.joint_teleportation_scores(ideal_histogram("phi+", 800), swapped)["conditional_fidelity"]
    # psi+ (1, 0) read as (0, 1) flips Z and X inputs; psi- (1, 1) is symmetric, so each of those inputs scores 1/2.
    if scores != {"+Z": 0.5, "-Z": 0.5, "+X": 0.5, "-X": 0.5, "+Y": 1.0, "-Y": 1.0}:
        raise AssertionError(scores)


def correlator(state: np.ndarray, axis: str) -> float:
    return float(np.trace(state @ np.kron(protocol.PAULI[axis], protocol.PAULI[axis])).real)


def test_separable_resources_do_not_pass_the_witness() -> None:
    # Product pure states on a grid of Bloch directions stay at or below 1/2, and an equal mixture of two does too.
    fidelities = protocol.product_witness_grid()
    if len(fidelities) != 26 * 26 or abs(max(fidelities) - 0.5) > 1e-12:
        raise AssertionError(max(fidelities))
    first, last = protocol.BLOCH_GRID[0], protocol.BLOCH_GRID[-1]
    mixture = (
        np.kron(protocol.bloch_projector(first), protocol.bloch_projector(first))
        + np.kron(protocol.bloch_projector(last), protocol.bloch_projector(last))
    ) / 2.0
    if (
        protocol.bell_fidelity(correlator(mixture, "X"), correlator(mixture, "Y"), correlator(mixture, "Z"))
        > 0.5 + 1e-12
    ):
        raise AssertionError("mixture")
    if protocol.bell_fidelity(0.0, 0.0, 1.0) != 0.5 or protocol.bell_fidelity(1.0, -1.0, 1.0) != 1.0:
        raise AssertionError("classically correlated mixture or Phi+")
    radius = math.sqrt(math.log(1.0 / 0.002) / 8.0 * 3.0 / 2590)
    if abs(protocol.witness_lower_bound(0.9, 0.002, (2590, 2590, 2590), 0.01) - (0.9 - radius - 0.01)) > 1e-15:
        raise AssertionError("witness lower bound")
    if protocol.witness_lower_bound(0.5, 0.002, (2590, 2590, 2590), 0.0) >= 0.5:
        raise AssertionError("a separable estimate certifies")


@pytest.mark.parametrize(
    "call",
    [
        lambda: protocol.witness_radius(0.01, 0, 10, 10),
        lambda: protocol.witness_radius(1.0, 10, 10, 10),
        lambda: protocol.witness_lower_bound(0.9, 0.01, (10, 10, 10), -0.1),
        lambda: protocol.pairs_per_axis(0.01, -0.03),
        lambda: protocol.pairs_per_axis(0.01, 0.0),
        lambda: protocol.pairs_per_axis(2.0, 0.03),
        lambda: protocol.bernoulli_decision_count(0.01, 1.0, 0.8, 2.0 / 3.0, 0.0),
        lambda: protocol.bernoulli_decision_count(0.01, 0.1, 0.8, 2.0 / 3.0, -0.5),
        lambda: protocol.success_weighted_fidelity(
            [(1.2 * protocol.I2, protocol.bloch_projector(np.array([0.0, 0.0, 1.0])))]
        ),
        lambda: protocol.success_weighted_fidelity(
            [(-0.4 * protocol.I2, protocol.bloch_projector(np.array([0.0, 0.0, 1.0])))]
        ),
        lambda: protocol.success_weighted_fidelity(
            [(0.5 * protocol.I2, 1.5 * protocol.bloch_projector(np.array([0.0, 0.0, 1.0])))]
        ),
        lambda: protocol.success_weighted_fidelity([(np.zeros((2, 2), dtype=complex), protocol.I2 / 2.0)]),
        lambda: protocol.propagate(np.eye(2, dtype=complex), {(1, 0): 1.0, (1, 1): 1.0}),
        lambda: protocol.dual_rail_pair("product"),
    ],
)
def test_domain_refusals(call: Callable[[], object]) -> None:
    with pytest.raises(protocol.ProtocolError):
        call()


def test_scoring_refuses_unsupported_evidence() -> None:
    histogram = ideal_histogram("phi+", 800)
    marginal = {(label, basis, "", raw): count for (label, basis, _, raw), count in histogram.items()}
    with pytest.raises(protocol.ProtocolError):
        protocol.joint_teleportation_scores(marginal, DESIGN_FRAMES)
    unknown = dict(histogram)
    unknown[("+Z", "Z", "0001", 0)] = 1
    with pytest.raises(protocol.ProtocolError):
        protocol.joint_teleportation_scores(unknown, DESIGN_FRAMES)
    missing = {key: count for key, count in histogram.items() if key[0] != "-Y"}
    with pytest.raises(protocol.ProtocolError):
        protocol.joint_teleportation_scores(missing, DESIGN_FRAMES)
    # Fixtures outside the declared key and count types are built as Any-typed records.
    bad_keys: list[Any] = [("+Z", "Z", 0), ("+Z", "W", "1100", 0), ("+Z", "Z", "1100", 2), ("+W", "Z", "1100", 0)]
    for bad_key in bad_keys:
        with_key: dict[Any, Any] = {**histogram, bad_key: 1}
        with pytest.raises(protocol.ProtocolError):
            protocol.joint_teleportation_scores(with_key, DESIGN_FRAMES)
    bad_counts: list[Any] = [-1, 1.5]
    for bad_count in bad_counts:
        with_count: dict[Any, Any] = {**histogram, ("+Z", "Z", "1100", 0): bad_count}
        with pytest.raises(protocol.ProtocolError):
            protocol.joint_teleportation_scores(with_count, DESIGN_FRAMES)
    with pytest.raises(protocol.ProtocolError):
        protocol.joint_teleportation_scores(histogram, {**DESIGN_FRAMES, "1100": (2, 0)})
    full = {label: 3 * 800 for label, _, _, _ in protocol.SIX_STATES}
    bad_attempts_list: list[dict[str, Any]] = [
        {"+Z": 800},
        {**full, "+Z": 1},
        {**full, "+Z": 0},
        {**full, "+Z": 2400.0},
    ]
    for bad_attempts in bad_attempts_list:
        with pytest.raises(protocol.ProtocolError):
            protocol.joint_teleportation_scores(histogram, DESIGN_FRAMES, bad_attempts)


def test_receiver_and_byproduct_guards() -> None:
    with pytest.raises(protocol.ProtocolError):
        protocol._conditional_receiver({(1, 1, 0, 0, 2, 0): 1.0}, (0, 1, 2, 3), (4, 5))
    with pytest.raises(protocol.ProtocolError):
        protocol._match_byproduct(
            {label: np.array([1.0, 0.0], dtype=complex) for label, _, _, _ in protocol.SIX_STATES}
        )
