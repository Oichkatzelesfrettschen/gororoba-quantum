"""Ideal dual-rail teleportation instrument and decision statistics for the Ascella-Belenos network design.

The module computes, from the bosonic transformation alone, every protocol
table docs/design/ascella-belenos-entanglement-teleportation.md relies on:

- the partial Bell-state analyzer. Two balanced beam splitters mix rail j of
  the input q with rail j of the sender half a under
  ``q_j^dag -> (c_j^dag + d_j^dag)/sqrt2`` and
  ``a_j^dag -> (c_j^dag - d_j^dag)/sqrt2``; threshold clicks in output order
  ``[c0, c1, d0, d1]`` identify a Bell state only where a single Bell input
  reaches the pattern (bell_pattern_table);
- the receiver byproduct ``X^x Z^z`` of every accepted pattern, found by
  propagating each of the six Pauli eigenstates through the three-photon,
  six-mode instrument with resource ``Phi+`` (teleportation_frames), its
  success probability, and the terminal decoder (decode_bit);
- reference preservation: four photons in eight modes with ``Phi+`` between
  an untouched reference R and q, so the frame-corrected R-b state after an
  accepted pattern is compared with ``Phi+`` (reference_preservation);
- two sequential teleportations, five photons in ten modes, whose composed
  byproduct is compared with ``(x1 xor x2, z1 xor z2)`` (sequential_frames).

Dual-rail encoding is ``|0_L> = |1,0>`` and ``|1_L> = |0,1>``. A Fock
amplitude through a linear-optical unitary U is
``perm(U[out, in]) / sqrt(prod n_i! prod m_j!)`` with rows and columns
repeated by occupation; the calculation is ideal (indistinguishable photons,
no loss, no multiphoton emission, no dark events) and supplies no hardware
property.

The statistics are the decision rules the design freezes: the Bell-state
fidelity witness ``F = (1 + C_XX - C_YY + C_ZZ)/4`` with its one-sided
Hoeffding lower bound, the success-weighted six-state fidelity of an accepted
instrument and its measure-and-prepare bound 2/3, the Bernoulli
benchmark-decision count, depolarizing two-hop composition, fixed-number Fock
dimensions and threshold click-pattern counts. joint_teleportation_scores
scores a joint Bell-pattern/receiver histogram and refuses records that do
not carry the Bell pattern with the receiver outcome, or a per-attempt rate
without an attempt denominator.

tests/scripts/test_qd_network_protocol.py holds the contract: the tables
equal the design's, propagation matches dense permanents and Perceval SLOS,
and every refusal fires.

Usage: "$PYTHON" scripts/qd_network_protocol.py --tables
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

Occupation = tuple[int, ...]
FockState = dict[Occupation, complex]

SQRT_HALF = 1.0 / math.sqrt(2.0)
TOLERANCE = 1e-12

I2 = np.eye(2, dtype=complex)
PAULI = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

# The six Pauli eigenstates of the uniform input ensemble: label, logical
# amplitudes (alpha, beta), matching axis and eigenvalue sign.
SIX_STATES: tuple[tuple[str, tuple[complex, complex], str, int], ...] = (
    ("+Z", (1.0, 0.0), "Z", 1),
    ("-Z", (0.0, 1.0), "Z", -1),
    ("+X", (SQRT_HALF, SQRT_HALF), "X", 1),
    ("-X", (SQRT_HALF, -SQRT_HALF), "X", -1),
    ("+Y", (SQRT_HALF, 1j * SQRT_HALF), "Y", 1),
    ("-Y", (SQRT_HALF, -1j * SQRT_HALF), "Y", -1),
)

BELL_LABELS = ("phi+", "phi-", "psi+", "psi-")


class BellRow(TypedDict):
    bell_inputs: dict[str, float]
    accepted: bool
    label: str | None


class ProtocolError(ValueError):
    """A record or request falls outside what the instrument model admits."""


def permanent(matrix: np.ndarray) -> complex:
    """Ryser's formula; matrix is square."""
    size = matrix.shape[0]
    if size == 0:
        return 1.0 + 0.0j
    total = 0.0 + 0.0j
    for subset_size in range(1, size + 1):
        for columns in itertools.combinations(range(size), subset_size):
            row_sums = matrix[:, list(columns)].sum(axis=1)
            total += (-1) ** subset_size * complex(np.prod(row_sums))
    return (-1) ** size * total


def occupations(modes: int, photons: int) -> list[Occupation]:
    """Every occupation of ``photons`` bosons over ``modes`` modes, in lexicographic order of mode lists."""
    result = []
    for placement in itertools.combinations_with_replacement(range(modes), photons):
        counts = [0] * modes
        for mode in placement:
            counts[mode] += 1
        result.append(tuple(counts))
    return result


def _repeated(occupation: Occupation) -> list[int]:
    return [mode for mode, count in enumerate(occupation) for _ in range(count)]


def propagate(unitary: np.ndarray, state: Mapping[Occupation, complex]) -> FockState:
    """Fock-basis image of ``state`` under the mode unitary (``unitary[out, in]``).

    Each input creation operator expands as ``a_i^dag -> sum_j U[j, i] b_j^dag``
    over the nonzero entries of column i; the coefficient c of the monomial
    ``prod_j b_j^dag^m_j`` from a source with amplitude s on occupation n gives
    the amplitude ``s c sqrt(prod m_j!) / sqrt(prod n_i!)`` on occupation m.
    """
    if len({sum(occupation) for occupation in state}) != 1:
        raise ProtocolError("propagate takes a fixed photon number")
    modes = unitary.shape[0]
    columns = [
        [(row, unitary[row, column]) for row in range(modes) if abs(unitary[row, column]) > TOLERANCE]
        for column in range(modes)
    ]
    output: dict[Occupation, complex] = {}
    for source, coefficient in state.items():
        terms: dict[Occupation, complex] = {
            tuple([0] * modes): coefficient / math.sqrt(math.prod(math.factorial(count) for count in source))
        }
        for column in _repeated(source):
            expanded: dict[Occupation, complex] = {}
            for monomial, weight in terms.items():
                for row, entry in columns[column]:
                    raised = list(monomial)
                    raised[row] += 1
                    key = tuple(raised)
                    expanded[key] = expanded.get(key, 0.0) + weight * entry
            terms = expanded
        for monomial, weight in terms.items():
            output[monomial] = output.get(monomial, 0.0) + weight * math.sqrt(
                math.prod(math.factorial(count) for count in monomial)
            )
    return {occupation: amplitude for occupation, amplitude in output.items() if abs(amplitude) > TOLERANCE}


@dataclass(frozen=True)
class _PermanentAmplitude:
    """Amplitude of one target occupation; module-level so parallel.ordered_map can pickle it."""

    unitary: np.ndarray
    sources: tuple[tuple[Occupation, complex], ...]

    def __call__(self, target: Occupation) -> complex:
        rows = _repeated(target)
        norm_out = math.prod(math.factorial(count) for count in target)
        amplitude = 0.0 + 0.0j
        for source, coefficient in self.sources:
            columns = _repeated(source)
            norm_in = math.prod(math.factorial(count) for count in source)
            sub = self.unitary[np.ix_(rows, columns)]
            amplitude += coefficient * permanent(sub) / math.sqrt(norm_in * norm_out)
        return amplitude


def propagate_by_permanents(unitary: np.ndarray, state: Mapping[Occupation, complex]) -> FockState:
    """Independent dense evaluation of propagate through ``perm(U[out, in]) / sqrt(prod n_i! prod m_j!)``.

    Target occupations are independent, so their amplitudes run through
    parallel.ordered_map; each keeps the serial summation order over sources.
    """
    modes = unitary.shape[0]
    photon_numbers = {sum(occupation) for occupation in state}
    if len(photon_numbers) != 1:
        raise ProtocolError("propagate takes a fixed photon number")
    targets = occupations(modes, photon_numbers.pop())
    amplitudes = ordered_map(_PermanentAmplitude(unitary, tuple(state.items())), targets)
    return {
        target: amplitude for target, amplitude in zip(targets, amplitudes, strict=True) if abs(amplitude) > TOLERANCE
    }


def tensor(*states: Mapping[Occupation, complex]) -> FockState:
    """Product state over concatenated mode registers."""
    result: FockState = {(): 1.0 + 0.0j}
    for state in states:
        result = {left + right: a * b for left, a in result.items() for right, b in state.items()}
    return result


def dual_rail_qubit(alpha: complex, beta: complex) -> FockState:
    return {occ: amp for occ, amp in (((1, 0), complex(alpha)), ((0, 1), complex(beta))) if amp != 0}


def dual_rail_pair(bell: str) -> FockState:
    """Bell state of two dual-rail qubits over modes (x0, x1, y0, y1)."""
    zero_zero, one_one = (1, 0, 1, 0), (0, 1, 0, 1)
    zero_one, one_zero = (1, 0, 0, 1), (0, 1, 1, 0)
    pairs = {
        "phi+": ((zero_zero, 1), (one_one, 1)),
        "phi-": ((zero_zero, 1), (one_one, -1)),
        "psi+": ((zero_one, 1), (one_zero, 1)),
        "psi-": ((zero_one, 1), (one_zero, -1)),
    }
    if bell not in pairs:
        raise ProtocolError(f"unknown Bell state {bell}")
    return {occ: complex(sign) * SQRT_HALF for occ, sign in pairs[bell]}


def analyzer_unitary() -> np.ndarray:
    """Inputs (q0, q1, a0, a1) to outputs (c0, c1, d0, d1)."""
    unitary = np.zeros((4, 4), dtype=complex)
    for rail in range(2):
        q, a, c, d = rail, 2 + rail, rail, 2 + rail
        unitary[c, q] = SQRT_HALF
        unitary[d, q] = SQRT_HALF
        unitary[c, a] = SQRT_HALF
        unitary[d, a] = -SQRT_HALF
    return unitary


def embed(blocks: Sequence[tuple[np.ndarray, Sequence[int]]], modes: int) -> np.ndarray:
    """Block-diagonal unitary acting on the listed mode index sets, identity elsewhere."""
    unitary = np.eye(modes, dtype=complex)
    for block, indices in blocks:
        unitary[np.ix_(list(indices), list(indices))] = block
    return unitary


def click(occupation: Occupation) -> str:
    return "".join("1" if count else "0" for count in occupation)


def bell_pattern_table() -> dict[str, BellRow]:
    """Click-pattern law of each Bell input; a pattern is accepted when exactly one Bell state reaches it."""
    unitary = analyzer_unitary()
    reach: dict[str, dict[str, float]] = {}
    for label in BELL_LABELS:
        for occupation, amplitude in propagate(unitary, dual_rail_pair(label)).items():
            pattern = click(occupation)
            bucket = reach.setdefault(pattern, {})
            bucket[label] = bucket.get(label, 0.0) + abs(amplitude) ** 2
    table: dict[str, BellRow] = {}
    for pattern in sorted(reach):
        sources = {label: round(probability, 12) for label, probability in sorted(reach[pattern].items())}
        accepted = len(sources) == 1 and pattern.count("1") == 2
        table[pattern] = {
            "bell_inputs": sources,
            "accepted": accepted,
            "label": next(iter(sources)) if accepted else None,
        }
    return table


def _pauli_word(x: int, z: int) -> np.ndarray:
    return np.linalg.matrix_power(PAULI["X"], x) @ np.linalg.matrix_power(PAULI["Z"], z)


def _match_byproduct(receiver_states: Mapping[str, np.ndarray]) -> tuple[int, int]:
    """The unique (x, z) with ``X^x Z^z psi`` equal to the receiver state up to phase on all six inputs."""
    found = []
    for x, z in itertools.product((0, 1), repeat=2):
        word = _pauli_word(x, z)
        if all(
            abs(abs(np.vdot(word @ np.array(amps, dtype=complex), receiver_states[label])) - 1.0) < 1e-9
            for label, amps, _, _ in SIX_STATES
        ):
            found.append((x, z))
    if len(found) != 1:
        raise ProtocolError(f"byproduct is not a unique Pauli word: {found}")
    return found[0]


def _conditional_receiver(
    output: FockState, analyzer_modes: Sequence[int], receiver_modes: Sequence[int]
) -> dict[str, tuple[float, np.ndarray]]:
    """Per analyzer click pattern: probability and normalized receiver dual-rail state."""
    grouped: dict[str, np.ndarray] = {}
    for occupation, amplitude in output.items():
        receiver = tuple(occupation[mode] for mode in receiver_modes)
        if receiver not in ((1, 0), (0, 1)):
            raise ProtocolError(f"receiver leaves the dual-rail space: {receiver}")
        pattern = click(tuple(occupation[mode] for mode in analyzer_modes))
        vector = grouped.setdefault(pattern, np.zeros(2, dtype=complex))
        if any(occupation[mode] > 1 for mode in analyzer_modes):
            continue
        vector[0 if receiver == (1, 0) else 1] += amplitude
    result = {}
    for pattern, vector in grouped.items():
        probability = float(np.vdot(vector, vector).real)
        if probability > TOLERANCE:
            result[pattern] = (probability, vector / math.sqrt(probability))
    return result


@dataclass(frozen=True)
class Teleportation:
    frames: dict[str, tuple[int, int]]
    success_probability: dict[str, float]
    fidelity: dict[str, float]


def receiver_states(resource: str = "phi+") -> dict[str, dict[str, tuple[float, np.ndarray]]]:
    """Per six-state input and accepted pattern: probability and receiver state; modes (q0, q1, a0, a1, b0, b1)."""
    table = bell_pattern_table()
    accepted = {pattern for pattern, row in table.items() if row["accepted"]}
    per_input = ordered_map(_SingleHop(resource), [(alpha, beta) for _, (alpha, beta), _, _ in SIX_STATES])
    return {
        label: {pattern: conditional[pattern] for pattern in sorted(accepted) if pattern in conditional}
        for (label, _, _, _), conditional in zip(SIX_STATES, per_input, strict=True)
    }


@dataclass(frozen=True)
class _SingleHop:
    """Conditional receiver states of one input through modes (q0, q1, a0, a1, b0, b1); pickled by ordered_map."""

    resource: str

    def __call__(self, amplitudes: tuple[complex, complex]) -> dict[str, tuple[float, np.ndarray]]:
        unitary = embed([(analyzer_unitary(), (0, 1, 2, 3))], 6)
        output = propagate(unitary, tensor(dual_rail_qubit(*amplitudes), dual_rail_pair(self.resource)))
        return _conditional_receiver(output, (0, 1, 2, 3), (4, 5))


def teleportation_frames(resource: str = "phi+") -> Teleportation:
    """Frames, success probability and frame-corrected fidelity of each accepted pattern."""
    states = receiver_states(resource)
    accepted = sorted({pattern for per_input in states.values() for pattern in per_input})
    receivers: dict[str, dict[str, np.ndarray]] = {}
    success: dict[str, float] = {}
    for label, per_input in states.items():
        success[label] = sum(probability for probability, _ in per_input.values())
        for pattern in accepted:
            receivers.setdefault(pattern, {})[label] = per_input[pattern][1]
    frames = {pattern: _match_byproduct(receivers[pattern]) for pattern in sorted(accepted)}
    fidelity = {}
    for pattern, (x, z) in frames.items():
        word = _pauli_word(x, z)
        values = []
        for label, amps, _, _ in SIX_STATES:
            corrected = word.conj().T @ receivers[pattern][label]
            values.append(abs(np.vdot(np.array(amps, dtype=complex), corrected)) ** 2)
        fidelity[pattern] = float(np.mean(values))
    return Teleportation(frames=frames, success_probability=success, fidelity=fidelity)


def decode_bit(basis: str, raw: int, x: int, z: int) -> int:
    """Frame-corrected terminal bit for receiver byproduct ``X^x Z^z``."""
    flips = {"Z": x, "X": z, "Y": x ^ z}
    if basis not in flips:
        raise ProtocolError(f"unknown basis {basis}")
    return raw ^ flips[basis]


def reference_preservation() -> dict[str, float]:
    """Frame-corrected ``Phi+`` fidelity of (R, b) per accepted pattern; modes (R0, R1, q0, q1, a0, a1, b0, b1)."""
    frames = teleportation_frames().frames
    unitary = embed([(analyzer_unitary(), (2, 3, 4, 5))], 8)
    output = propagate(unitary, tensor(dual_rail_pair("phi+"), dual_rail_pair("phi+")))
    target = np.array([1, 0, 0, 1], dtype=complex) * SQRT_HALF
    grouped: dict[str, np.ndarray] = {}
    for occupation, amplitude in output.items():
        pattern = click(occupation[2:6])
        if pattern not in frames or any(count > 1 for count in occupation[2:6]):
            continue
        r_bit = 0 if occupation[0:2] == (1, 0) else 1
        b_bit = 0 if occupation[6:8] == (1, 0) else 1
        grouped.setdefault(pattern, np.zeros(4, dtype=complex))[2 * r_bit + b_bit] += amplitude
    fidelity = {}
    for pattern, vector in sorted(grouped.items()):
        x, z = frames[pattern]
        correction = np.kron(I2, _pauli_word(x, z).conj().T)
        state = correction @ (vector / np.linalg.norm(vector))
        fidelity[pattern] = float(abs(np.vdot(target, state)) ** 2)
    return fidelity


def sequential_frames() -> dict[tuple[str, str], tuple[int, int]]:
    """Composed byproduct of two teleportations; modes (q0, q1, a1_0, a1_1, b1_0, b1_1, b2_0, b2_1, a2_0, a2_1).

    The first analyzer mixes q with a1; the second mixes b1 (the first
    receiver) with b2, and a2 carries the output.
    """
    frames = teleportation_frames().frames
    per_input = ordered_map(_TwoHop(tuple(sorted(frames))), [(alpha, beta) for _, (alpha, beta), _, _ in SIX_STATES])
    receivers: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for (label, _, _, _), grouped in zip(SIX_STATES, per_input, strict=True):
        for key, vector in grouped.items():
            receivers.setdefault(key, {})[label] = vector / np.linalg.norm(vector)
    return {key: _match_byproduct(states) for key, states in sorted(receivers.items())}


@dataclass(frozen=True)
class _TwoHop:
    """Unnormalized a2 states of one input per accepted pattern pair; pickled by ordered_map."""

    accepted: tuple[str, ...]

    def __call__(self, amplitudes: tuple[complex, complex]) -> dict[tuple[str, str], np.ndarray]:
        unitary = embed([(analyzer_unitary(), (0, 1, 2, 3)), (analyzer_unitary(), (4, 5, 6, 7))], 10)
        state = tensor(dual_rail_qubit(*amplitudes), dual_rail_pair("phi+"), dual_rail_pair("phi+"))
        grouped: dict[tuple[str, str], np.ndarray] = {}
        for occupation, amplitude in propagate(unitary, state).items():
            key = (click(occupation[0:4]), click(occupation[4:8]))
            if key[0] not in self.accepted or key[1] not in self.accepted:
                continue
            if any(count > 1 for count in occupation[0:8]):
                continue
            grouped.setdefault(key, np.zeros(2, dtype=complex))[0 if occupation[8:10] == (1, 0) else 1] += amplitude
        return grouped


def bell_fidelity(c_xx: float, c_yy: float, c_zz: float) -> float:
    """``Phi+`` fidelity from the three matching-axis correlators."""
    return (1.0 + c_xx - c_yy + c_zz) / 4.0


def _require_probability(name: str, value: float) -> None:
    if not 0.0 < value < 1.0:
        raise ProtocolError(f"{name} must lie strictly between 0 and 1, not {value}")


def _require_allowance(value: float) -> None:
    if not math.isfinite(value) or value < 0.0:
        raise ProtocolError(f"a systematic allowance is finite and nonnegative, not {value}")


def witness_radius(alpha: float, n_x: int, n_y: int, n_z: int) -> float:
    """One-sided Hoeffding radius of the witness: three independent +-1 means with weights +-1/4."""
    _require_probability("alpha", alpha)
    if min(n_x, n_y, n_z) <= 0:
        raise ProtocolError("witness radius needs positive counts")
    return math.sqrt(math.log(1.0 / alpha) / 8.0 * (1.0 / n_x + 1.0 / n_y + 1.0 / n_z))


def witness_lower_bound(fidelity: float, alpha: float, counts: tuple[int, int, int], systematic: float) -> float:
    _require_allowance(systematic)
    return fidelity - witness_radius(alpha, *counts) - systematic


def pairs_per_axis(alpha: float, radius: float) -> int:
    """Smallest equal per-axis count whose witness radius is at most ``radius``."""
    _require_probability("alpha", alpha)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ProtocolError(f"radius must be positive, not {radius}")
    return math.ceil(3.0 * math.log(1.0 / alpha) / (8.0 * radius * radius))


def bernoulli_decision_count(alpha: float, beta: float, mean_score: float, benchmark: float, systematic: float) -> int:
    """Independent valid outcomes for a one-sided Hoeffding benchmark decision at power ``1 - beta``."""
    _require_probability("alpha", alpha)
    _require_probability("beta", beta)
    _require_allowance(systematic)
    margin = mean_score - benchmark - systematic
    if margin <= 0.0:
        raise ProtocolError("the mean score does not exceed the benchmark plus the systematic allowance")
    numerator = (math.sqrt(math.log(1.0 / alpha)) + math.sqrt(math.log(1.0 / beta))) ** 2
    return math.ceil(numerator / (2.0 * margin * margin))


def two_hop_depolarizing(fidelity: float) -> float:
    """Average fidelity of two identical trace-preserving depolarizing qubit hops of average fidelity ``fidelity``."""
    return (1.0 + (2.0 * fidelity - 1.0) ** 2) / 2.0


TWO_HOP_CLASSICAL_THRESHOLD = (1.0 + 1.0 / math.sqrt(3.0)) / 2.0


def fock_dimension(modes: int, photons: int) -> int:
    return math.comb(modes + photons - 1, photons)


def click_pattern_count(modes: int, max_clicks: int) -> int:
    """Threshold patterns with 1 through ``max_clicks`` clicking detectors."""
    return sum(math.comb(modes, clicks) for clicks in range(1, max_clicks + 1))


def density(amplitudes: tuple[complex, complex]) -> np.ndarray:
    vector = np.array(amplitudes, dtype=complex)
    return np.outer(vector, vector.conj())


def success_weighted_fidelity(instrument: Iterable[tuple[np.ndarray, np.ndarray]]) -> tuple[float, float]:
    """(F_succ, success) on the six states of the accepted instrument ``rho -> sum_k tr(M_k rho) sigma_k``."""
    branches = list(instrument)
    for effect, prepared in branches:
        if not np.allclose(effect, effect.conj().T, atol=1e-12) or np.linalg.eigvalsh(effect).min() < -1e-12:
            raise ProtocolError("an effect is not a positive semidefinite Hermitian operator")
        if (
            not np.allclose(prepared, prepared.conj().T, atol=1e-12)
            or np.linalg.eigvalsh(prepared).min() < -1e-12
            or abs(np.trace(prepared) - 1.0) > 1e-12
        ):
            raise ProtocolError("a prepared state is not a density operator")
    total = sum((effect for effect, _ in branches), start=np.zeros((2, 2), dtype=complex))
    if np.linalg.eigvalsh(I2 - total).min() < -1e-12:
        raise ProtocolError("effects sum above the identity")
    numerator = 0.0
    success = 0.0
    for _, amps, _, _ in SIX_STATES:
        rho = density(amps)
        for effect, prepared in branches:
            weight = float(np.trace(effect @ rho).real) / 6.0
            success += weight
            numerator += weight * float(np.trace(rho @ prepared).real)
    if success <= 0.0:
        raise ProtocolError("the instrument never succeeds on the ensemble")
    return numerator / success, success


BLOCH_GRID: tuple[tuple[int, int, int], ...] = tuple(
    (x, y, z) for x, y, z in itertools.product((-1, 0, 1), repeat=3) if (x, y, z) != (0, 0, 0)
)
KEEP_MINUS_WEIGHTS = (0.0, 0.5, 1.0)


def bloch_projector(direction: Sequence[float] | np.ndarray) -> np.ndarray:
    """Pure-state projector along a nonzero Bloch direction."""
    unit = np.array(direction, dtype=float)
    unit = unit / np.linalg.norm(unit)
    return (I2 + sum(unit[k] * PAULI[axis] for k, axis in enumerate("XYZ"))) / 2.0


def _measure_and_prepare_point(point: tuple[tuple[int, int, int], tuple[int, int, int], float]) -> tuple[float, float]:
    """F_succ and success of: measure along m, prepare p on +m, and keep -m with weight w preparing -p."""
    measured, prepared, keep_minus = point
    minus_measured = tuple(-value for value in measured)
    minus_prepared = tuple(-value for value in prepared)
    instrument = [
        (bloch_projector(measured), bloch_projector(prepared)),
        (keep_minus * bloch_projector(minus_measured), bloch_projector(minus_prepared)),
    ]
    return success_weighted_fidelity(instrument)


def measure_and_prepare_grid() -> list[tuple[float, float]]:
    """(F_succ, success) of every grid instrument: 26 measured directions, 26 prepared directions, 3 weights."""
    points = [(m, p, w) for m in BLOCH_GRID for p in BLOCH_GRID for w in KEEP_MINUS_WEIGHTS]
    return ordered_map(_measure_and_prepare_point, points)


def _product_witness(pair: tuple[tuple[int, int, int], tuple[int, int, int]]) -> float:
    state = np.kron(bloch_projector(pair[0]), bloch_projector(pair[1]))
    correlators = [float(np.trace(state @ np.kron(PAULI[axis], PAULI[axis])).real) for axis in "XYZ"]
    return bell_fidelity(*correlators)


def product_witness_grid() -> list[float]:
    """Phi+ witness fidelity of every product of two grid pure states (26 x 26)."""
    return ordered_map(_product_witness, [(left, right) for left in BLOCH_GRID for right in BLOCH_GRID])


def joint_teleportation_scores(
    histogram: Mapping[tuple[str, str, str, int], int],
    frames: Mapping[str, tuple[int, int]],
    attempts: Mapping[str, int] | None = None,
) -> dict[str, object]:
    """Score a joint histogram keyed (input label, receiver basis, Bell pattern, raw receiver bit).

    Each key carries the Bell pattern and receiver bit of one trial, so a key
    that lacks the pattern, or names a pattern outside the frozen frame table,
    refuses scoring. Matching-basis cells give the conditional fidelity per
    input; the per-attempt success rate divides every accepted trial of an
    input, all receiver bases together, by ``attempts`` for that input (its
    attempts over all bases) and reads unavailable without it.
    """
    states = {label: (axis, sign) for label, _, axis, sign in SIX_STATES}
    if any(frame not in ((0, 0), (0, 1), (1, 0), (1, 1)) for frame in frames.values()):
        raise ProtocolError("a frame entry lies outside {0, 1} x {0, 1}")
    correct: dict[str, int] = {}
    accepted: dict[str, int] = {}
    heralded: dict[str, int] = {}
    for key, count in histogram.items():
        if len(key) != 4 or not isinstance(key[2], str) or key[2] == "":
            raise ProtocolError(f"histogram key {key!r} lacks the joint Bell pattern")
        label, basis, pattern, raw = key
        if label not in states:
            raise ProtocolError(f"unknown input {label}")
        if pattern not in frames:
            raise ProtocolError(f"Bell pattern {pattern} is outside the frozen frame table")
        if basis not in ("X", "Y", "Z"):
            raise ProtocolError(f"unknown receiver basis {basis}")
        if raw not in (0, 1) or isinstance(raw, bool):
            raise ProtocolError(f"raw receiver bit {raw!r} is not 0 or 1")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ProtocolError(f"count {count!r} is not a nonnegative integer")
        heralded[label] = heralded.get(label, 0) + count
        if basis != states[label][0]:
            continue
        x, z = frames[pattern]
        bit = decode_bit(basis, raw, x, z)
        expected = 0 if states[label][1] == 1 else 1
        accepted[label] = accepted.get(label, 0) + count
        correct[label] = correct.get(label, 0) + (count if bit == expected else 0)
    missing = [label for label in states if accepted.get(label, 0) == 0]
    if missing:
        raise ProtocolError(f"no matching-basis trials for {missing}")
    conditional = {label: correct[label] / accepted[label] for label in states}
    result: dict[str, object] = {
        "conditional_fidelity": conditional,
        "mean_conditional_fidelity": sum(conditional.values()) / 6.0,
        "pooled_conditional_fidelity": sum(correct.values()) / sum(accepted.values()),
    }
    if attempts is None:
        result["success_rate"] = None
        result["success_rate_reason"] = "no physical attempt denominator; retained samples do not substitute for one"
    else:
        if set(attempts) != set(states):
            raise ProtocolError("attempts needs a count for each of the six inputs")
        for label, count in attempts.items():
            if not isinstance(count, int) or isinstance(count, bool) or count < heralded[label]:
                raise ProtocolError(
                    f"attempts for {label} must be an integer of at least its {heralded[label]} accepted trials"
                )
        result["success_rate"] = {label: heralded[label] / attempts[label] for label in states}
    return result


def tables() -> dict[str, object]:
    teleport = teleportation_frames()
    return {
        "bell_pattern_table": bell_pattern_table(),
        "frames": {pattern: list(frame) for pattern, frame in teleport.frames.items()},
        "success_probability": teleport.success_probability,
        "conditional_fidelity": teleport.fidelity,
        "reference_preservation_fidelity": reference_preservation(),
        "sequential_frames": {"|".join(key): list(frame) for key, frame in sequential_frames().items()},
        "witness_pairs_per_axis": {
            "alpha_0.01_radius_0.03": pairs_per_axis(0.01, 0.03),
            "alpha_0.002_radius_0.03": pairs_per_axis(0.002, 0.03),
        },
        "bernoulli_decision_counts": {
            str(score): bernoulli_decision_count(0.01, 0.10, score, 2.0 / 3.0, 0.02) for score in (0.75, 0.80, 0.90)
        },
        "two_hop_depolarizing": {str(f): two_hop_depolarizing(f) for f in (0.75, 0.80)},
        "two_hop_classical_threshold": TWO_HOP_CLASSICAL_THRESHOLD,
        "fock_dimensions": {f"{n}x{m}": fock_dimension(m, n) for n, m in ((3, 6), (4, 8), (5, 10), (6, 12), (12, 24))},
        "click_patterns": {
            "ascella_12_modes_6_photons": click_pattern_count(12, 6),
            "belenos_24_modes_12_photons": click_pattern_count(24, 12),
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tables", action="store_true", required=True, help="print every derived table as JSON")
    parser.parse_args(argv)
    json.dump(tables(), sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
