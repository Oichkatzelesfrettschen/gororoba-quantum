"""Star Ramsey on a center and three leaves: a rank-seven design for the diagonal star Hamiltonian.

The reduced model is H / hbar = (sum_q omega_q Z_q + sum_j J_j Z_C Z_Lj) / 2
over the center C (qubit 0) and the leaves L1, L2, L3 (qubits 1, 2, 3), with
Z|0> = |0>, and generalizes conditional_ramsey.py from one coupled pair to a
star. A coherence between basis states x and y winds at nu = E_x - E_y. Every
sector holds C's coherence between a C = 0 branch x and a C = 1 branch y, so
its design row over (omega_C, omega_L1, omega_L2, omega_L3, J1, J2, J3) is the
difference of the two branches' energy coefficients; DESIGN_ROWS derives each
row from SECTOR_STATES, and the self-check confirms every row against exact
evolution:

    all0, leafj, all1 (leaves fixed):  nu = omega_C + sum_j s_j J_j,
                                       s_j = +1 for a leaf in |0>, -1 in |1>
    even_j (|0 0>, |1 1> on C, Lj):    nu = omega_C + omega_Lj + sum_(k != j) J_k
    odd_j  (|0 1>, |1 0> on C, Lj):    nu = omega_C - omega_Lj + sum_(k != j) J_k
    ghz    (|0000>, |1111>):           nu = omega_C + omega_L1 + omega_L2 + omega_L3

The five conditional rows carry no leaf frequency and have rank four over
(omega_C, J); the Bell pairs supply each omega_Lj. Twelve rows over seven
unknowns leave five falsifiers of the reduced, static, diagonal model, each
the exact relation of one dependent row to the rows before it in SECTORS
(FALSIFIERS):

    all1 - leaf1 - leaf2 - leaf3 + 2 all0   additivity of the leaf ZZ shifts on C
    odd_j + even_j - all0 - leafj           each Bell pair against the conditional rows
    ghz - even1 - even2 - even3 + 2 all0    additivity of the leaf frequencies

Each omega_Lj is an effective frequency: the leaf's physical neighbors outside
the star idle in |0> and add a static ZZ shift to it. On the Heron r2
heavy-hex graph a qubit has at most three couplers, so a center placed on a
degree-three qubit has every neighbor inside its star, and each leaf of such
a center has at most one neighbor outside it (docs/evidence/heron_platform/targets.json);
C's rates carry no outside shift.

live_run compiles the group's first member alone to choose the layout and
compiles every other member onto that layout (live_run.select_candidates);
placement then embeds every CZ edge the compiled members touch
(packing.pattern). The GHZ arm is the first member and applies CX from C to
all three leaves, so its layout puts C on a degree-three qubit with the leaves
on its couplers, and each Bell arm's CX compiles onto one of those couplers
without routing, so the pattern is the star C-L1, C-L2, C-L3 and every
replica lands on three real couplers. A member that touched only one coupler
would leave the other leaves free to land off the star. When Sabre panics on
a fragmented admission Target, live_run._compile_primary falls back to a
breadth-first layout (component_layouts), which routing can extend with SWAPs
into a pattern other than the star.

Each sector is a four-qubit circuit measured into the clbit of the same index.
A conditional arm prepares the leaves in its bit pattern, puts C on the
equator, idles and reads C in the X or Y basis. A Bell or GHZ arm prepares its
state with H on C and CX from C to its entangled leaves, idles, undoes the CX
and reads C. Either way C ends in (|0> + exp(i nu t)|1>) / sqrt2 times a fixed
phase, the delays are integer dt on all four qubits, and the fitted slope over
DELAYS_DT is the rate, with fixed gate durations in the intercept. The first
nonzero delay sets the unambiguous range |nu| < pi / FIRST_DELAY_DT; the GHZ
rate sums all four frequencies and is the largest rate of the design.
Dynamical decoupling would refocus the free evolution these arms measure.

A conditional arm keeps only the shots in which all three leaves read their
prepared bits. A leaf in |1> that relaxes during the idle moves C to another
sector's rate from the jump onward, and the leaf's own readout heralds the
jump. A Bell or GHZ arm keeps every shot, as conditional_ramsey's Bell arms
do: a relaxed branch is orthogonal to the coherent pair and lowers C's
visibility without moving its phase.

Two calibration circuits read all four qubits prepared in |0> and in |1>. The
summary inverts C's measured assignment channel before taking phases and
reports every rate, parameter and falsifier with a delta-method standard
error at one shot per circuit (divide by sqrt(shots)), propagated through the
calibration, the phase fits and the exact least-squares reconstruction.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from fractions import Fraction

import numpy as np
from qiskit import QuantumCircuit

import parallel
from conditional_ramsey import (
    DELAYS_DT,
    FIRST_DELAY_DT,
    QUADRATURES,
    Evolution,
    corrected_expectation,
    fit_rate,
    rate_hz,
    unambiguous_rate_bound,
)
from experiments import Group, Member

QUBITS = 4
LEAVES = (1, 2, 3)
PARAMETERS = ("omega_c", "omega_l1", "omega_l2", "omega_l3", "zz_j1", "zz_j2", "zz_j3")
# Each sector: the leaves' prepared bits (L1, L2, L3) and the leaves that CX
# from C entangles with it. The C = 0 branch carries the prepared bits; the
# C = 1 branch flips the entangled leaves.
SECTOR_STATES: dict[str, tuple[tuple[int, int, int], tuple[int, ...]]] = {
    "all0": ((0, 0, 0), ()),
    "leaf1": ((1, 0, 0), ()),
    "leaf2": ((0, 1, 0), ()),
    "leaf3": ((0, 0, 1), ()),
    "all1": ((1, 1, 1), ()),
    "even1": ((0, 0, 0), (1,)),
    "odd1": ((1, 0, 0), (1,)),
    "even2": ((0, 0, 0), (2,)),
    "odd2": ((0, 1, 0), (2,)),
    "even3": ((0, 0, 0), (3,)),
    "odd3": ((0, 0, 1), (3,)),
    "ghz": ((0, 0, 0), LEAVES),
}
SECTORS = tuple(SECTOR_STATES)
CONDITIONAL_SECTORS = tuple(sector for sector in SECTORS if not SECTOR_STATES[sector][1])
# The GHZ arm compiles first and fixes the layout for every other member.
MEMBER_SECTORS = ("ghz", *(sector for sector in SECTORS if sector != "ghz"))
READOUT_MEMBERS = ("sr_readout_0", "sr_readout_1")


def member_name(sector: str, quadrature: str, delay: int) -> str:
    return f"sr_{sector}_{quadrature}_{delay}dt"


def branches(sector: str) -> tuple[int, int]:
    """Basis indices (bit q is qubit q) of the C = 0 and C = 1 branches of a sector's coherence."""
    bits, entangled = SECTOR_STATES[sector]
    leaves = sum(bit << leaf for leaf, bit in zip(LEAVES, bits, strict=True))
    return leaves, (leaves ^ sum(1 << leaf for leaf in entangled)) | 1


def _spin(index: int, qubit: int) -> int:
    """Z eigenvalue of a qubit in a basis state: +1 for |0>, -1 for |1>."""
    return 1 - 2 * ((index >> qubit) & 1)


def energy_coefficients(index: int) -> tuple[Fraction, ...]:
    """E / hbar of a basis state as coefficients of PARAMETERS."""
    center = _spin(index, 0)
    return (
        Fraction(center, 2),
        *(Fraction(_spin(index, leaf), 2) for leaf in LEAVES),
        *(Fraction(center * _spin(index, leaf), 2) for leaf in LEAVES),
    )


def branch_difference(sector: str, energy: Callable[[int], Fraction]) -> Fraction:
    """nu = E_x - E_y of one energy term between a sector's C = 0 and C = 1 branches."""
    x, y = branches(sector)
    return energy(x) - energy(y)


def design_row(sector: str) -> tuple[Fraction, ...]:
    """The sector's row over PARAMETERS: energy coefficients of its C = 0 branch minus its C = 1 branch."""
    x, y = branches(sector)
    return tuple(a - b for a, b in zip(energy_coefficients(x), energy_coefficients(y), strict=True))


DESIGN_ROWS = {sector: design_row(sector) for sector in SECTORS}


def _eliminate(rows: list[tuple[Fraction, ...]]) -> tuple[list[int], list[list[Fraction]]]:
    """Independent rows in order, and for each dependent row its exact relation to the rows before it.

    Each relation has coefficient 1 on its dependent row and vanishes against
    every row of the design, so applied to measured rates it is a falsifier.
    """
    basis: list[tuple[int, list[Fraction], list[Fraction]]] = []
    independent: list[int] = []
    relations: list[list[Fraction]] = []
    for index, row in enumerate(rows):
        reduced = list(row)
        combination = [Fraction(int(other == index)) for other in range(len(rows))]
        for column, pivot_row, pivot_combination in basis:
            factor = reduced[column] / pivot_row[column]
            if factor:
                reduced = [a - factor * b for a, b in zip(reduced, pivot_row, strict=True)]
                combination = [a - factor * b for a, b in zip(combination, pivot_combination, strict=True)]
        lead = next((position for position, value in enumerate(reduced) if value != 0), None)
        if lead is None:
            relations.append(combination)
        else:
            basis.append((lead, reduced, combination))
            independent.append(index)
    return independent, relations


def design_rank(sectors: tuple[str, ...], columns: tuple[str, ...] = PARAMETERS) -> int:
    """Exact rank over Q of the named sectors' design rows restricted to the named parameters."""
    picks = [PARAMETERS.index(column) for column in columns]
    rows = [tuple(DESIGN_ROWS[sector][pick] for pick in picks) for sector in sectors]
    return len(_eliminate(rows)[0])


def _exact_pseudo_inverse(rows: list[tuple[Fraction, ...]]) -> list[list[Fraction]]:
    """(D^T D)^-1 D^T over Q by Gauss-Jordan, so the reconstruction carries no BLAS rounding."""
    width = len(rows[0])
    normal = [[sum((row[a] * row[b] for row in rows), Fraction(0)) for b in range(width)] for a in range(width)]
    augmented = [normal[a] + [Fraction(int(a == b)) for b in range(width)] for a in range(width)]
    for column in range(width):
        pivot = next((index for index in range(column, width) if augmented[index][column] != 0), None)
        if pivot is None:
            raise ValueError("the design does not determine every parameter")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for index in range(width):
            if index != column and augmented[index][column] != 0:
                factor = augmented[index][column]
                augmented[index] = [a - factor * b for a, b in zip(augmented[index], augmented[column], strict=True)]
    inverse = [line[width:] for line in augmented]
    return [[sum((inverse[a][k] * row[k] for k in range(width)), Fraction(0)) for row in rows] for a in range(width)]


_INDEPENDENT, _RELATIONS = _eliminate([DESIGN_ROWS[sector] for sector in SECTORS])
# Each relation is named after its dependent row, its last nonzero entry.
FALSIFIERS: dict[str, tuple[Fraction, ...]] = {
    f"falsifier_{SECTORS[max(index for index, weight in enumerate(relation) if weight)]}": tuple(relation)
    for relation in _RELATIONS
}
PSEUDO_INVERSE = _exact_pseudo_inverse([DESIGN_ROWS[sector] for sector in SECTORS])
RATE_KEYS = tuple(f"{sector}_rate_rad_per_dt" for sector in SECTORS)
SE_KEYS = (*RATE_KEYS, *PARAMETERS, *FALSIFIERS)
# Every SE_KEYS value is linear in the sector rates through this map.
OUTPUT_MAP = np.vstack(
    [
        np.eye(len(SECTORS)),
        np.array(PSEUDO_INVERSE, dtype=float),
        np.array(list(FALSIFIERS.values()), dtype=float),
    ]
)


def predicted_rates(parameters: Mapping[str, float]) -> dict[str, float]:
    return {
        sector: sum(float(coefficient) * parameters[name] for coefficient, name in zip(row, PARAMETERS, strict=True))
        for sector, row in DESIGN_ROWS.items()
    }


def idle(circuit: QuantumCircuit, sector: str, delay: int) -> None:
    if delay:
        circuit.delay(delay, range(QUBITS), unit="dt")


def _arm_circuit(
    name: str,
    bits: tuple[int, ...],
    entangled: tuple[int, ...],
    sector: str,
    quadrature: str,
    delay: int,
    evolve: Evolution,
) -> QuantumCircuit:
    circuit = QuantumCircuit(QUBITS, QUBITS, name=name)
    for leaf, bit in zip(LEAVES, bits, strict=True):
        if bit:
            circuit.x(leaf)
    circuit.h(0)
    for leaf in entangled:
        circuit.cx(0, leaf)
    circuit.barrier()
    evolve(circuit, sector, delay)
    circuit.barrier()
    for leaf in reversed(entangled):
        circuit.cx(0, leaf)
    if quadrature == "y":
        circuit.sdg(0)
    circuit.h(0)
    circuit.measure(range(QUBITS), range(QUBITS))
    return circuit


def sector_circuit(sector: str, quadrature: str, delay: int, evolve: Evolution = idle) -> QuantumCircuit:
    bits, entangled = SECTOR_STATES[sector]
    return _arm_circuit(member_name(sector, quadrature, delay), bits, entangled, sector, quadrature, delay, evolve)


def leaf_readout(sector: str) -> int:
    """Outcome index of the leaves' expected readout (C's bit clear): the prepared bits."""
    return branches(sector)[0]


def ideal_distribution(sector: str, quadrature: str) -> np.ndarray:
    """Outcome law of an ideal idle: C reads 0 in X and is uniform in Y; the leaves read their prepared bits."""
    ideal = np.zeros(1 << QUBITS)
    leaves = leaf_readout(sector)
    if quadrature == "x":
        ideal[leaves] = 1.0
    else:
        ideal[leaves] = ideal[leaves | 1] = 0.5
    return ideal


def readout_circuit(prepared: int) -> QuantumCircuit:
    circuit = QuantumCircuit(QUBITS, QUBITS, name=READOUT_MEMBERS[prepared])
    if prepared:
        circuit.x(range(QUBITS))
    circuit.measure(range(QUBITS), range(QUBITS))
    return circuit


def circuits(evolve: Evolution = idle) -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    sectors = tuple(
        (
            member_name(sector, quadrature, delay),
            sector_circuit(sector, quadrature, delay, evolve),
            ideal_distribution(sector, quadrature),
        )
        for sector in MEMBER_SECTORS
        for delay in DELAYS_DT
        for quadrature in QUADRATURES
    )
    full = (1 << QUBITS) - 1
    calibration = tuple(
        (READOUT_MEMBERS[prepared], readout_circuit(prepared), np.eye(1 << QUBITS)[full * prepared])
        for prepared in (0, 1)
    )
    return sectors + calibration


SECTOR_OF = {
    member_name(sector, quadrature, delay): sector
    for sector in SECTORS
    for delay in DELAYS_DT
    for quadrature in QUADRATURES
}


def c_expectation(distribution: np.ndarray) -> float:
    """<Z> of the rotated C readout, 1 - 2 P(C = 1), from a sixteen-outcome distribution."""
    return float(1.0 - 2.0 * np.sum(distribution[1::2]))


def c_assignment(distributions: Mapping[str, np.ndarray]) -> tuple[float, float]:
    """C's flips from the in-job calibration: e10 = P(1 | prepared 0), e01 = P(0 | prepared 1).

    The channel maps a true expectation q to (1 - e10 - e01) q + (e01 - e10)
    in both quadratures; the common offset moves the center of the Ramsey
    circle, so the summary inverts it before taking phases.
    """
    zero, one = distributions[READOUT_MEMBERS[0]], distributions[READOUT_MEMBERS[1]]
    return float(np.sum(zero[1::2])), float(np.sum(one[0::2]))


def conditioned(distribution: np.ndarray, sector: str) -> np.ndarray:
    """A conditional arm's law restricted to all leaves read as prepared and renormalized; others unchanged.

    The assignment channels are per-qubit, so discarding on the leaves'
    outcomes leaves C's assignment channel, and the in-job correction of it,
    as they were.
    """
    if sector not in CONDITIONAL_SECTORS:
        return distribution
    leaves = leaf_readout(sector)
    kept = np.zeros(len(distribution))
    kept[leaves], kept[leaves | 1] = distribution[leaves], distribution[leaves | 1]
    return kept / kept.sum()


def leaf_preparation_error(distribution: np.ndarray, sector: str) -> float:
    """Probability that the leaves read anything but their expected bits."""
    leaves = leaf_readout(sector)
    return float(1.0 - distribution[leaves] - distribution[leaves | 1])


def sector_phases(
    distributions: Mapping[str, np.ndarray], sector: str, e10: float, e01: float, postselect: bool = True
) -> tuple[list[float], list[float]]:
    """C's phase and visibility at every delay from assignment-corrected X and Y expectations."""
    phases, visibilities = [], []
    for delay in DELAYS_DT:
        quadratures = []
        for quadrature in QUADRATURES:
            law = distributions[member_name(sector, quadrature, delay)]
            if postselect:
                law = conditioned(law, sector)
            quadratures.append(corrected_expectation(c_expectation(law), e10, e01))
        x, y = quadratures
        phases.append(math.atan2(y, x))
        visibilities.append(math.hypot(x, y))
    return phases, visibilities


def sector_rate(distributions: Mapping[str, np.ndarray], sector: str, e10: float, e01: float) -> float:
    return fit_rate(DELAYS_DT, sector_phases(distributions, sector, e10, e01)[0])[0]


def reconstruct(rates: Mapping[str, float]) -> dict[str, float]:
    """Least-squares parameters over all sector rows and the falsifier residuals."""
    vector = [rates[sector] for sector in SECTORS]
    out = {
        name: sum(float(weight) * rate for weight, rate in zip(row, vector, strict=True))
        for name, row in zip(PARAMETERS, PSEUDO_INVERSE, strict=True)
    }
    out.update(
        {
            name: sum(float(weight) * rate for weight, rate in zip(relation, vector, strict=True))
            for name, relation in FALSIFIERS.items()
        }
    )
    return out


def point_summary(distributions: Mapping[str, np.ndarray], postselect: bool = True) -> dict[str, float]:
    """Phases, fitted rates and reconstructed parameters on assignment-corrected expectations.

    ``postselect=False`` reads the conditional arms without discarding on the
    leaves, the estimator that leaf relaxation biases.
    """
    e10, e01 = c_assignment(distributions)
    summary: dict[str, float] = {"c_assignment_e10": e10, "c_assignment_e01": e01}
    rates: dict[str, float] = {}
    for sector in SECTORS:
        phases, visibilities = sector_phases(distributions, sector, e10, e01, postselect)
        for delay, phase, visibility in zip(DELAYS_DT, phases, visibilities, strict=True):
            summary[f"{sector}_{delay}dt_phase"] = phase
            summary[f"{sector}_{delay}dt_visibility"] = visibility
        rates[sector], intercept = fit_rate(DELAYS_DT, phases)
        summary[f"{sector}_rate_rad_per_dt"] = rates[sector]
        summary[f"{sector}_intercept"] = intercept
        summary[f"{sector}_leaf_preparation_error"] = float(
            np.mean(
                [
                    leaf_preparation_error(distributions[member_name(sector, quadrature, delay)], sector)
                    for delay in DELAYS_DT
                    for quadrature in QUADRATURES
                ]
            )
        )
    summary.update(reconstruct(rates))
    return summary


class RateGradient:
    """Central-difference gradient of every sector rate with respect to one circuit's outcome probabilities.

    A sector member moves only its own sector's rate; a calibration member
    moves every rate through C's assignment correction. Outcomes of zero
    probability carry zero multinomial covariance and are skipped.
    """

    def __init__(self, distributions: Mapping[str, np.ndarray], step: float) -> None:
        self.base = dict(distributions)
        self.step = step

    def __call__(self, name: str) -> np.ndarray:
        dist = self.base[name]
        if name in READOUT_MEMBERS:
            sectors: tuple[str, ...] = SECTORS
        elif name in SECTOR_OF:
            sectors = (SECTOR_OF[name],)
        else:
            sectors = ()
        rows = [SECTORS.index(sector) for sector in sectors]
        gradient = np.zeros((len(SECTORS), len(dist)))
        for outcome in np.flatnonzero(dist):
            shifted = []
            for sign in (1.0, -1.0):
                moved = dict(self.base)
                moved[name] = dist.copy()
                moved[name][outcome] += sign * self.step
                e10, e01 = c_assignment(moved)
                shifted.append([sector_rate(moved, sector, e10, e01) for sector in sectors])
            gradient[rows, outcome] = (np.asarray(shifted[0]) - np.asarray(shifted[1])) / (2.0 * self.step)
        return gradient


def one_shot_standard_errors(distributions: Mapping[str, np.ndarray], step: float = 1e-6) -> dict[str, float]:
    """Delta-method standard errors at one shot per circuit; divide by sqrt(shots).

    Every circuit is an independent multinomial with covariance
    (diag(p) - p p^T) / N. Each output is linear in the sector rates
    (OUTPUT_MAP), so the per-circuit rate gradients, the calibration circuits
    included, carry the whole error budget; parallel.ordered_map computes
    them circuit by circuit.
    """
    base = {name: np.asarray(dist, dtype=float) for name, dist in distributions.items()}
    names = list(base)
    gradients = parallel.ordered_map(RateGradient(base, step), names)
    variance = np.zeros(len(SE_KEYS))
    for name, gradient in zip(names, gradients, strict=True):
        dist = base[name]
        covariance = np.diag(dist) - np.outer(dist, dist)
        projected = OUTPUT_MAP @ gradient
        variance += np.einsum("ko,op,kp->k", projected, covariance, projected)
    return {
        f"{key}_se_one_shot": math.sqrt(max(float(value), 0.0)) for key, value in zip(SE_KEYS, variance, strict=True)
    }


def standard_error(summary: Mapping[str, float], key: str, shots: int) -> float:
    return summary[f"{key}_se_one_shot"] / math.sqrt(shots)


def summarize_distributions(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    summary = point_summary(distributions)
    summary.update(one_shot_standard_errors(distributions))
    return summary


def star_ramsey_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in circuits())
    return Group("star_ramsey", members, summarize_distributions)


def hamiltonian_evolution(
    omega_c: float,
    omega_leaves: tuple[float, float, float],
    zz: tuple[float, float, float],
    stark_conditional: float = 0.0,
    three_body: float = 0.0,
) -> Evolution:
    """Replace each idle by exp(-i H t) of the reduced model, rates in rad per dt.

    RZ(theta) = exp(-i theta Z / 2) and RZZ(theta) = exp(-i theta Z Z / 2), so
    the model is RZ on every qubit and RZZ on every coupler. stark_conditional
    adds a C detuning on the conditional arms only, a departure from one
    static Hamiltonian; three_body adds K Z_C Z_L1 Z_L2 / 2 through a parity
    computed onto C, a departure from pairwise coupling. The falsifiers must
    see both.
    """

    def evolve(circuit: QuantumCircuit, sector: str, delay: int) -> None:
        extra = stark_conditional if sector in CONDITIONAL_SECTORS else 0.0
        circuit.rz((omega_c + extra) * delay, 0)
        for leaf, omega in zip(LEAVES, omega_leaves, strict=True):
            circuit.rz(omega * delay, leaf)
        for leaf, coupling in zip(LEAVES, zz, strict=True):
            circuit.rzz(coupling * delay, 0, leaf)
        if three_body:
            circuit.cx(1, 0)
            circuit.cx(2, 0)
            circuit.rz(three_body * delay, 0)
            circuit.cx(2, 0)
            circuit.cx(1, 0)

    return evolve


def _probabilities(circuit: QuantumCircuit) -> np.ndarray:
    from qiskit.quantum_info import Statevector

    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities())


def exact_distributions(evolve: Evolution) -> dict[str, np.ndarray]:
    return {name: _probabilities(circuit) for name, circuit, _ in circuits(evolve)}


def with_assignment(
    distributions: Mapping[str, np.ndarray],
    c_flips: tuple[float, float],
    leaf_flips: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
) -> dict[str, np.ndarray]:
    """Pass every outcome law through per-qubit channels [[1 - e10, e01], [e10, 1 - e01]]."""

    def channel(e10: float, e01: float) -> np.ndarray:
        return np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])

    joint = np.ones((1, 1))
    for flips in (c_flips, *leaf_flips):
        joint = np.kron(channel(*flips), joint)
    return {name: joint @ np.asarray(dist) for name, dist in distributions.items()}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _two_qubit_pairs(circuit: QuantumCircuit) -> set[tuple[int, int]]:
    return {
        tuple(sorted(circuit.find_bit(qubit).index for qubit in instruction.qubits))
        for instruction in circuit.data
        if instruction.operation.num_qubits == 2 and instruction.operation.name != "barrier"
    }


def self_check() -> str:
    star = {(0, leaf) for leaf in LEAVES}
    members = circuits()
    idle_laws = exact_distributions(idle)
    for name, _, ideal in members:
        _require(np.allclose(idle_laws[name], ideal, atol=1e-12), f"{name}: statevector law differs from its ideal")

    # Placement: the first member fixes the layout, and the union is the pattern.
    _require(members[0][0] == member_name("ghz", "x", DELAYS_DT[0]), "the GHZ arm must be the first member")
    _require(_two_qubit_pairs(members[0][1]) == star, "the first member must touch all three couplers")
    _require(
        set().union(*(_two_qubit_pairs(circuit) for _, circuit, _ in members)) == star,
        "the members' two-qubit gates must cover exactly the couplers (0,1), (0,2), (0,3)",
    )
    for leaf in LEAVES:
        for parity in ("even", "odd"):
            pairs = _two_qubit_pairs(sector_circuit(f"{parity}{leaf}", "x", DELAYS_DT[1]))
            _require(pairs == {(0, leaf)}, f"{parity}{leaf} must touch only the coupler (0, {leaf})")

    leaf_columns = ("omega_l1", "omega_l2", "omega_l3")
    center_columns = tuple(name for name in PARAMETERS if name not in leaf_columns)
    _require(design_rank(SECTORS) == len(PARAMETERS) == 7, "the full design must have rank seven")
    _require(design_rank(CONDITIONAL_SECTORS) == 4, "the conditional rows must have rank four")
    _require(
        design_rank(CONDITIONAL_SECTORS, center_columns) == 4 and design_rank(CONDITIONAL_SECTORS, leaf_columns) == 0,
        "the conditional rows must span (omega_C, J) and carry no leaf frequency",
    )
    _require(
        len(FALSIFIERS) == len(SECTORS) - 7 == 5
        and set(FALSIFIERS) == {f"falsifier_{sector}" for sector in ("all1", "odd1", "odd2", "odd3", "ghz")},
        "the twelve rows must leave five falsifiers on all1, the odd arms and the GHZ arm",
    )

    dt = 4e-9
    to_rad = 2.0 * math.pi * dt
    truth = {
        "omega_c": 30e3 * to_rad,
        "omega_l1": -12e3 * to_rad,
        "omega_l2": 21e3 * to_rad,
        "omega_l3": -7e3 * to_rad,
        "zz_j1": 8e3 * to_rad,
        "zz_j2": -5e3 * to_rad,
        "zz_j3": 3e3 * to_rad,
    }
    leaves = (truth["omega_l1"], truth["omega_l2"], truth["omega_l3"])
    zz = (truth["zz_j1"], truth["zz_j2"], truth["zz_j3"])
    scale = max(abs(value) for value in truth.values())
    tolerance = 1e-9 * scale
    expected = predicted_rates(truth)
    laws = exact_distributions(hamiltonian_evolution(truth["omega_c"], leaves, zz))
    exact = summarize_distributions(laws)
    for sector, rate in expected.items():
        measured = exact[f"{sector}_rate_rad_per_dt"]
        _require(abs(measured - rate) < 1e-9 * abs(rate), f"{sector}: exact rate {measured} against row {rate}")
    for name, value in truth.items():
        _require(abs(exact[name] - value) < tolerance, f"exact recovery of {name}: {exact[name]} against {value}")
    for name in FALSIFIERS:
        _require(abs(exact[name]) < tolerance, f"the static diagonal model must satisfy {name}")

    bound = unambiguous_rate_bound()
    _require(bound == math.pi / FIRST_DELAY_DT, "the unwrap bound is pi over the first nonzero delay")
    _require(
        max(later / earlier for earlier, later in zip(DELAYS_DT[1:-1], DELAYS_DT[2:], strict=True)) <= 4,
        "each delay may exceed the one before it by at most four times",
    )
    _require(max(abs(rate) for rate in expected.values()) < bound, "every test rate must lie inside the unwrap bound")

    def planted_residuals(contribution: Mapping[str, Fraction | float]) -> dict[str, float]:
        return {
            name: sum(
                float(weight) * float(contribution[sector]) for weight, sector in zip(relation, SECTORS, strict=True)
            )
            for name, relation in FALSIFIERS.items()
        }

    stark = 3e3 * to_rad
    three_body = 2e3 * to_rad
    for label, evolution, contribution in (
        (
            "conditional-arm detuning",
            hamiltonian_evolution(truth["omega_c"], leaves, zz, stark_conditional=stark),
            {sector: stark if sector in CONDITIONAL_SECTORS else 0.0 for sector in SECTORS},
        ),
        (
            "three-body Z_C Z_L1 Z_L2",
            hamiltonian_evolution(truth["omega_c"], leaves, zz, three_body=three_body),
            {
                sector: three_body
                * float(
                    branch_difference(
                        sector, lambda index: Fraction(_spin(index, 0) * _spin(index, 1) * _spin(index, 2), 2)
                    )
                )
                for sector in SECTORS
            },
        ),
    ):
        planted = point_summary(exact_distributions(evolution))
        predicted = planted_residuals(contribution)
        for name, value in predicted.items():
            _require(abs(planted[name] - value) < tolerance, f"{label}: {name} {planted[name]} against {value}")
        _require(
            max(abs(value) for value in predicted.values()) > 1e3 * tolerance,
            f"the {label} must move a falsifier away from zero",
        )

    # A 268.6 kHz center detuning, past the 227.7 kHz alias of a 4.392 us
    # window, must unwrap exactly in every sector, the GHZ sum included.
    fast_center = -(40.9e3 + 1.0 / 4.392e-6) * to_rad
    fast_leaves = (-40.9e3 * to_rad, 100e3 * to_rad, -50e3 * to_rad)
    fast = point_summary(exact_distributions(hamiltonian_evolution(fast_center, fast_leaves, zz)))
    fast_truth = dict(zip(PARAMETERS, (fast_center, *fast_leaves, *zz), strict=True))
    _require(
        all(abs(fast[name] - value) < 1e-9 for name, value in fast_truth.items()),
        "a fast detuning inside the unwrap bound must unwrap exactly",
    )
    aliased = point_summary(exact_distributions(hamiltonian_evolution(1.2 * bound, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))))
    _require(abs(aliased["all0_rate_rad_per_dt"] - 1.2 * bound) > 1e-6, "a rate past the unwrap bound must alias")

    c_flips = (0.04, 0.12)
    leaf_flips = ((0.02, 0.08), (0.05, 0.03), (0.01, 0.10))
    misread = with_assignment(laws, c_flips, leaf_flips)
    corrected = point_summary(misread)
    _require(
        all(abs(corrected[name] - value) < 1e-10 for name, value in truth.items())
        and all(abs(corrected[name]) < 1e-10 for name in FALSIFIERS),
        "the in-job calibration and postselection must undo asymmetric per-qubit assignment",
    )
    uncalibrated = dict(misread)
    uncalibrated.update({name: laws[name] for name in READOUT_MEMBERS})
    raw_bias = abs(point_summary(uncalibrated)["omega_c"] - truth["omega_c"])
    _require(raw_bias > 1e-7, "an asymmetric assignment must bias the uncorrected rates")

    # L2 relaxing from |1> to |0> during the all1 idle: a fraction of the
    # shots evolves under the leaf pattern (1, 0, 1) and reads L2 = 0.
    model = hamiltonian_evolution(truth["omega_c"], leaves, zz)
    relaxed = dict(laws)
    decayed = 0.1
    for delay in DELAYS_DT:
        for quadrature in QUADRATURES:
            name = member_name("all1", quadrature, delay)
            jumped = _probabilities(_arm_circuit(name, (1, 0, 1), (), "all1", quadrature, delay, model))
            relaxed[name] = (1.0 - decayed) * laws[name] + decayed * jumped
    recovered = point_summary(relaxed)
    _require(
        abs(recovered["all1_rate_rad_per_dt"] - expected["all1"]) < tolerance
        and abs(recovered["falsifier_all1"]) < tolerance,
        "postselecting the leaves on their preparation must remove leaf relaxation from the all1 row",
    )
    unconditioned = point_summary(relaxed, postselect=False)
    _require(
        abs(unconditioned["falsifier_all1"]) > 1e3 * tolerance,
        "leaf relaxation must move the unconditioned all1 falsifier",
    )

    rng = np.random.default_rng(20261016)
    shots = 1024
    samples: dict[str, list[float]] = {"zz_j1": [], "omega_l2": [], "falsifier_ghz": []}
    for _ in range(40):
        sampled = {
            name: rng.multinomial(shots, np.clip(law, 0.0, None) / law.sum()) / shots for name, law in laws.items()
        }
        values = point_summary(sampled)
        for key in samples:
            samples[key].append(values[key])
    for key, draws in samples.items():
        spread = float(np.std(draws, ddof=1))
        predicted_se = standard_error(exact, key, shots)
        _require(
            0.7 * predicted_se < spread < 1.4 * predicted_se,
            f"{key} spread {spread} departs from propagated {predicted_se}",
        )
        _require(
            abs(float(np.mean(draws)) - truth.get(key, 0.0)) < 4.0 * predicted_se / math.sqrt(len(draws)),
            f"{key} estimate is biased",
        )
    return (
        f"star Ramsey: {len(members)} circuits; GHZ arm first on couplers (0,1), (0,2), (0,3); "
        f"conditional rank 4 -> design rank 7 over {len(SECTORS)} rows, {len(FALSIFIERS)} falsifiers at 0; "
        f"assignment bias {rate_hz(raw_bias, dt):.0f} Hz removed by the in-job calibration; "
        f"propagated J1 error {rate_hz(standard_error(exact, 'zz_j1', shots), dt):.0f} Hz at {shots} shots; "
        f"unwrap bound {rate_hz(bound, dt) / 1e3:.0f} kHz"
    )


if __name__ == "__main__":
    print(self_check())
