"""Four-term A_5 coset blocks as four-qubit circuits: the signed 4 x 4 block of a two-flat operand on two data qubits.

A four-term operand O = a_0 + a_1 + a_2 + a_3 (every coefficient +1) whose indices form a 2-flat, a_0 ^ a_1 ^ a_2 ^
a_3 = 0, has differences in V0 = span(u1, u2) with u1 = a_0 ^ a_1 and u2 = a_0 ^ a_2, and a_k = a_0 ^ (k1 u1 ^ k2 u2)
for the term index k = k1 + 2 k2. Left multiplication L_O maps the coset c0 + V0 onto (c0 ^ a_0) + V0, so L_O is block
diagonal with eight signed 4 x 4 blocks B_c0[y, n] = sign(e_(a_k) e_(x_n)) at k = y XOR n, x_n = c0 ^ (n1 u1 ^ n2 u2).
Every entry is +-1.

Circuit, qubits d0, d1 (data, coordinates n1, n2) and s0, s1 (selector, coordinates k1, k2): a real two-qubit input
state psi on the data qubits, H on the selector, one diagonal on all four qubits with entry f(k, n) = sign(e_(a_k)
e_(x_n)) at index n + 4 k, CX(s0 -> d0) and CX(s1 -> d1), H on the selector, and a measurement of all four qubits. The
outcome selector 00 carries the amplitude B psi / 4, so P(selector = 00) = |B psi|^2 / 16 is the level of the arm and
the data bits conditioned on 00 follow |B psi|^2 bin by bin. No outcome is postselected: the level is the observable,
and it equals lambda / 16 for an input in the Gram eigenspace of B^T B with eigenvalue lambda (lambda 0 is a kernel
vector, the largest lambda the bright vector). A basis input has level 1/4 for every block, because each column of B
holds four entries of modulus 1.

Arms: T the top Gram eigenvector, D a kernel vector, F the top vector with the sign of one component flipped, E0 and
E1 basis inputs (null level 1/4), C the cocycle-free block (every entry +1) on the true top vector, N the block with
the one entry whose negation moves the level most, on the true top vector. T, D, F, E0 and E1 are one parametrized
circuit (the input state is three Ry angles), so they share routing; C and N carry their own diagonal.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector

import cd_core
from experiments import Group, Member

DIM = 32
# Two-flat operands whose coset blocks Ascella read one block per photon (scripts/ascella_pathion_four_term_blocks.py).
OPERANDS: dict[str, tuple[int, int, int, int]] = {"B12": (1, 10, 20, 31), "C8": (1, 8, 18, 27)}
ARMS = ("T", "D", "F", "E0", "E1", "C", "N")
# Gram spectra of four-term 4 x 4 blocks absent below dimension 32 that carry a kernel and a bright eigenvalue above 10
# (docs/evidence/pathion-kernel-map/census.json, classes_new_at_32_spectra), rounded to 3 digits.
NEW_AT_32 = ((0.0, 0.0, 4.0, 12.0), (0.0, 1.528, 4.0, 10.472))
SHARED_ARMS = ("T", "D", "F", "E0", "E1")
# A mutated arm's ideal level must lie this far from the true top level for the arm to separate.
SEPARATION = 0.10
# Ideal levels are multiples of 1/64; a value below this is zero.
ZERO = 1e-9

PREP_A = Parameter("prep_a")
PREP_C0 = Parameter("prep_c0")
PREP_C1 = Parameter("prep_c1")


@dataclass(frozen=True)
class FourBlock:
    """The coset c0 + V0 of the two-flat operand with indices ``terms`` (all coefficients +1)."""

    name: str
    terms: tuple[int, int, int, int]
    coset: int

    def __post_init__(self) -> None:
        a0, a1, a2, a3 = self.terms
        if a0 ^ a1 ^ a2 ^ a3 != 0:
            raise ValueError(f"{self.name}: the indices {self.terms} do not form a 2-flat")
        if len({a0, a1, a2, a3}) != 4 or not 0 <= self.coset < DIM:
            raise ValueError(f"{self.name}: degenerate terms or coset")

    @property
    def u(self) -> tuple[int, int]:
        a0, a1, a2, _ = self.terms
        return a0 ^ a1, a0 ^ a2

    @property
    def tag(self) -> str:
        return f"{self.name}_c{self.coset}"


def input_label(block: FourBlock, n: int) -> int:
    """Algebra index of the block's input n = n1 + 2 n2."""
    u1, u2 = block.u
    return block.coset ^ ((n & 1) * u1) ^ ((n >> 1 & 1) * u2)


def output_label(block: FourBlock, y: int) -> int:
    u1, u2 = block.u
    return block.coset ^ block.terms[0] ^ ((y & 1) * u1) ^ ((y >> 1 & 1) * u2)


def sign_table(block: FourBlock) -> np.ndarray:
    """f[k, n] = sign(e_(a_k) e_(x_n)), the entry of B at row y = n XOR k and column n."""
    a0 = block.terms[0]
    u1, u2 = block.u
    table = np.zeros((4, 4))
    for k in range(4):
        a_k = a0 ^ ((k & 1) * u1) ^ ((k >> 1 & 1) * u2)
        for n in range(4):
            table[k, n] = cd_core.cd_sign(DIM, a_k, input_label(block, n))
    return table


def block_matrix(block: FourBlock, table: np.ndarray | None = None) -> np.ndarray:
    table = sign_table(block) if table is None else table
    matrix = np.zeros((4, 4))
    for k in range(4):
        for n in range(4):
            matrix[n ^ k, n] = table[k, n]
    return matrix


def core_block_matrix(block: FourBlock) -> np.ndarray:
    """The block cut from the full matrix L_O = sum_k L_(e_(a_k)) of cd_core, independent of ``sign_table``."""
    vector = [0.0] * DIM
    for a in block.terms:
        vector[a] = 1.0
    full = np.array(cd_core.left_mult_matrix(DIM, vector))
    rows = [output_label(block, y) for y in range(4)]
    cols = [input_label(block, n) for n in range(4)]
    outside = np.delete(np.arange(DIM), rows)
    if np.abs(full[np.ix_(outside, cols)]).max() != 0.0:
        raise ValueError(f"{block.tag}: L_O maps the input coset outside the output coset")
    return full[np.ix_(rows, cols)]


def gram_spectrum(matrix: np.ndarray) -> np.ndarray:
    return np.linalg.eigvalsh(matrix.T @ matrix)


def top_vector(matrix: np.ndarray) -> np.ndarray:
    """The unit Gram eigenvector of the largest eigenvalue, with its first nonzero component positive."""
    values, vectors = np.linalg.eigh(matrix.T @ matrix)
    vector = vectors[:, int(np.argmax(values))]
    first = vector[int(np.argmax(np.abs(vector) > ZERO))]
    return vector * (1.0 if first > 0 else -1.0)


def kernel_vector(matrix: np.ndarray) -> np.ndarray | None:
    """A unit kernel vector of B, else None: the projection of the first basis vector that the kernel does not
    annihilate, which depends on the kernel subspace alone (an eigensolver basis of a degenerate kernel does not)."""
    values, vectors = np.linalg.eigh(matrix.T @ matrix)
    inside = vectors[:, values < ZERO]
    if inside.shape[1] == 0:
        return None
    projector = inside @ inside.T
    for n in range(4):
        column = projector[:, n]
        if np.linalg.norm(column) > 1e-6:
            vector = column / np.linalg.norm(column)
            first = vector[int(np.argmax(np.abs(vector) > ZERO))]
            return vector * (1.0 if first > 0 else -1.0)
    return None


def level(matrix: np.ndarray, psi: np.ndarray) -> float:
    return float(np.sum((matrix @ psi) ** 2) / 16.0)


def flipped_top(matrix: np.ndarray) -> np.ndarray:
    """The top vector with one component negated, the component whose negation moves the level most."""
    top = top_vector(matrix)
    best, best_gap = top, -1.0
    for n in range(4):
        candidate = top.copy()
        candidate[n] = -candidate[n]
        gap = abs(level(matrix, candidate) - level(matrix, top))
        if gap > best_gap + ZERO:
            best, best_gap = candidate, gap
    return best


def mutated_table(block: FourBlock) -> np.ndarray:
    """The sign table with the one entry negated whose negation moves the top-vector level most."""
    table = sign_table(block)
    top = top_vector(block_matrix(block, table))
    base = level(block_matrix(block, table), top)
    best, best_gap = table, -1.0
    for k in range(4):
        for n in range(4):
            candidate = table.copy()
            candidate[k, n] = -candidate[k, n]
            gap = abs(level(block_matrix(block, candidate), top) - base)
            if gap > best_gap + ZERO:
                best, best_gap = candidate, gap
    return best


def prep_angles(psi: np.ndarray) -> tuple[float, float, float]:
    """(a, c0, c1) with Ry(a) on d1, then Ry(b_(n2)) on d0 for d1 = n2, b = (c0 + c1, c0 - c1)."""
    amplitude = np.asarray(psi, dtype=float).reshape(2, 2)  # [n2, n1]
    norms = np.linalg.norm(amplitude, axis=1)
    a = 2.0 * float(np.arctan2(norms[1], norms[0]))
    b = [2.0 * float(np.arctan2(amplitude[n2, 1], amplitude[n2, 0])) if norms[n2] > ZERO else 0.0 for n2 in range(2)]
    return a, (b[0] + b[1]) / 2.0, (b[0] - b[1]) / 2.0


def prep_layer() -> QuantumCircuit:
    """Real two-qubit input state on d0, d1 from three Ry angles: Ry(a) on d1, then a uniformly controlled Ry on d0."""
    qc = QuantumCircuit(2)
    qc.ry(PREP_A, 1)
    qc.ry(PREP_C0, 0)
    qc.cx(1, 0)
    qc.ry(PREP_C1, 0)
    qc.cx(1, 0)
    return qc


def template(block: FourBlock, table: np.ndarray | None = None, *, measure: bool = True) -> QuantumCircuit:
    """The block circuit with the input state unbound (PREP_A, PREP_C0, PREP_C1) and the given sign table."""
    table = sign_table(block) if table is None else table
    qc = QuantumCircuit(4, 4 if measure else 0)
    qc.compose(prep_layer(), [0, 1], inplace=True)
    qc.h([2, 3])
    diagonal = [table[k, n] for k in range(4) for n in range(4)]
    qc.append(DiagonalGate(diagonal), [0, 1, 2, 3])
    qc.cx(2, 0)
    qc.cx(3, 1)
    qc.h([2, 3])
    if measure:
        qc.measure(range(4), range(4))
    return qc


def binding(psi: np.ndarray) -> dict[Parameter, float]:
    a, c0, c1 = prep_angles(psi)
    return {PREP_A: a, PREP_C0: c0, PREP_C1: c1}


def law(circuit: QuantumCircuit) -> np.ndarray:
    """Outcome law indexed y + 4 s with s = s0 + 2 s1 (data clbits first, selector last)."""
    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities())


def selector_zero(distribution: np.ndarray) -> float:
    return float(distribution[:4].sum())


def arm_inputs(block: FourBlock) -> dict[str, tuple[np.ndarray | None, np.ndarray | None]]:
    """Arm -> (input vector, sign table); a None table marks the block's own table, a None vector (D) a block
    with no kernel."""
    matrix = block_matrix(block)
    top = top_vector(matrix)
    return {
        "T": (top, None),
        "D": (kernel_vector(matrix), None),
        "F": (flipped_top(matrix), None),
        "E0": (np.array([1.0, 0.0, 0.0, 0.0]), None),
        "E1": (np.array([0.0, 1.0, 0.0, 0.0]), None),
        "C": (top, np.ones((4, 4))),
        "N": (top, mutated_table(block)),
    }


def arm_levels(block: FourBlock) -> dict[str, float]:
    """Ideal level of every arm from the matrices alone, the reference the circuit laws are checked against."""
    levels: dict[str, float] = {}
    for arm, (psi, table) in arm_inputs(block).items():
        if psi is None:
            continue
        matrix = block_matrix(block, np.asarray(table) if table is not None else None)
        levels[arm] = level(matrix, psi)
    return levels


def separates(block: FourBlock) -> bool:
    """Every mutated arm (F, C, N) lies at least SEPARATION below the true top level, and the dark arm lies near 0."""
    levels = arm_levels(block)
    return "D" in levels and all(levels["T"] - levels[arm] >= SEPARATION for arm in ("F", "C", "N"))


def select_blocks() -> tuple[FourBlock, ...]:
    """One block per distinct Gram spectrum of each operand, the first coset that carries a kernel and separates."""
    chosen: list[FourBlock] = []
    for name, terms in OPERANDS.items():
        seen: set[tuple[float, ...]] = set()
        base = FourBlock(name, terms, 0)
        v0 = {0, base.u[0], base.u[1], base.u[0] ^ base.u[1]}
        reps = sorted({min(c ^ v for v in v0) for c in range(DIM)})
        for c0 in reps:
            block = FourBlock(name, terms, c0)
            spectrum = tuple(float(abs(x)) for x in np.round(gram_spectrum(block_matrix(block)), 3))
            if spectrum in seen or spectrum not in NEW_AT_32 or not separates(block):
                continue
            seen.add(spectrum)
            chosen.append(block)
    return tuple(chosen)


def four_term_members(blocks: tuple[FourBlock, ...] | None = None) -> tuple[Member, ...]:
    members: list[Member] = []
    for block in blocks if blocks is not None else select_blocks():
        base = template(block)
        base.name = f"ftb_{block.tag}"
        inputs = arm_inputs(block)
        for arm in SHARED_ARMS:
            psi = inputs[arm][0]
            if psi is None:
                continue
            bound = base.assign_parameters(binding(psi))
            members.append(Member(f"ftb_{block.tag}_{arm}", base, law(bound), binding(psi)))
        for arm in ("C", "N"):
            psi, table = inputs[arm]
            if psi is None:
                raise ValueError(f"{block.tag}: arm {arm} has no input vector")
            own = template(block, table)
            own.name = f"ftb_{block.tag}_{arm}"
            bound = own.assign_parameters(binding(psi))
            members.append(Member(f"ftb_{block.tag}_{arm}", own, law(bound), binding(psi)))
    return tuple(members)


def block_summary(prefix: str, distributions: dict[str, np.ndarray], ideal: dict[str, np.ndarray]) -> dict[str, float]:
    """Levels, the two-point visibility from T and D, and each other arm's departure from the affine prediction.

    Under a contraction of every arm toward one fixed law, P_obs(a) = P_dark + V (P_ideal(a) - P_ideal(D)) with V
    estimated from T and D, so the closure of an arm is its observed level minus that prediction."""
    summary: dict[str, float] = {}
    arms = [arm for arm in ARMS if f"{prefix}_{arm}" in distributions]
    observed = {arm: selector_zero(distributions[f"{prefix}_{arm}"]) for arm in arms}
    expected = {arm: selector_zero(ideal[f"{prefix}_{arm}"]) for arm in arms}
    for arm in arms:
        summary[f"{prefix}_level_{arm}"] = observed[arm]
        summary[f"{prefix}_level_ideal_{arm}"] = expected[arm]
    if "T" in arms and "D" in arms and abs(expected["T"] - expected["D"]) > ZERO:
        visibility = (observed["T"] - observed["D"]) / (expected["T"] - expected["D"])
        summary[f"{prefix}_visibility"] = visibility
        for arm in arms:
            if arm in ("T", "D"):
                continue
            summary[f"{prefix}_closure_{arm}"] = observed[arm] - (
                observed["D"] + visibility * (expected[arm] - expected["D"])
            )
        for arm in ("F", "C", "N"):
            if arm in arms:
                summary[f"{prefix}_separation_{arm}"] = observed["T"] - observed[arm]
    for arm in ("T", "F"):
        if arm in arms:
            conditional = distributions[f"{prefix}_{arm}"][:4]
            reference = ideal[f"{prefix}_{arm}"][:4]
            if conditional.sum() > ZERO and reference.sum() > ZERO:
                summary[f"{prefix}_bin_tvd_{arm}"] = 0.5 * float(
                    np.abs(conditional / conditional.sum() - reference / reference.sum()).sum()
                )
    return summary


def four_term_group(blocks: tuple[FourBlock, ...] | None = None) -> Group:
    members = four_term_members(blocks)
    ideal = {member.name: member.ideal for member in members}
    prefixes = sorted({member.name.rsplit("_", 1)[0] for member in members})

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        out: dict[str, float] = {}
        for prefix in prefixes:
            out |= block_summary(prefix, distributions, ideal)
        return out

    return Group("pathion_four_term", members, summarize)
