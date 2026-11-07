"""Build single-photon optical probes of the pathion-only four-term A5 coset blocks for Ascella."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
import sympy as sym

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import anu_qrng  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

import cd_core  # noqa: E402
from parallel import ordered_map  # noqa: E402

Matrix = npt.NDArray[np.float64]

DIM = 32
# Four-term operands on 2-flats {i, j, k, l} with i ^ j ^ k ^ l = 0, two indices below 16 and two at or above it.
OPERANDS: dict[str, dict[int, int]] = {
    "B12": {1: 1, 10: 1, 20: 1, 31: 1},
    "C8": {1: 1, 8: 1, 18: 1, 27: 1},
    "A16": {1: 1, 10: 1, 18: 1, 25: -1},
}
SCALE = 4

ARMS_BASE = ("T", "D", "F", "F", "D", "T")
ARMS_MUTATED = ("T", "D", "F", "C", "N", "N", "C", "F", "D", "T")
ARMS_ENTRY = ("T", "D", "F", "N", "N", "F", "D", "T")
ARMS_ANCHOR = ("T", "D", "D", "T")
ARMS_NULL = ("E0", "E1", "E1", "E0")
ARM_MEANING = {
    "T": "programmed block B/4 with its top Gram eigenvector as input (bright arm, '+')",
    "D": "programmed block with a kernel vector of B as input (dark arm)",
    "F": "programmed block with one sign of the top input flipped (input-sign mutation, '-')",
    "C": "cocycle-free block (every entry +1) with the true top input (block mutation)",
    "N": "block with the entry whose negation moves the level most negated, true top input (entry mutation)",
    "E0": "programmed block with basis input 0 (null: level 1/4 for every four-term block)",
    "E1": "programmed block with basis input 1 (null: level 1/4 for every four-term block)",
}


@dataclass(frozen=True)
class Segment:
    """Consecutive iterations on one block under one compilation seed; the arms mirror about the middle."""

    name: str
    role: str
    operand: str
    ordinal: int
    arms: tuple[str, ...]
    seed_index: int


SEGMENTS = (
    Segment("anchor-early", "anchor", "A16", 4, ARMS_ANCHOR, 0),
    Segment("reference-b12-0", "reference", "B12", 0, ARMS_BASE, 1),
    Segment("b12-2", "pathion", "B12", 2, ARMS_MUTATED, 2),
    Segment("c8-4", "pathion", "C8", 4, ARMS_MUTATED, 3),
    Segment("b12-3", "pathion", "B12", 3, ARMS_ENTRY, 4),
    Segment("c8-5", "pathion", "C8", 5, ARMS_BASE, 5),
    Segment("b12-6", "pathion", "B12", 6, ARMS_MUTATED, 6),
    Segment("c8-6", "pathion", "C8", 6, ARMS_MUTATED, 7),
    Segment("b12-7", "pathion", "B12", 7, ARMS_MUTATED, 8),
    Segment("c8-7", "pathion", "C8", 7, ARMS_BASE, 9),
    Segment("null-b12-2", "null", "B12", 2, ARMS_NULL, 10),
    Segment("anchor-late", "anchor", "A16", 4, ARMS_ANCHOR, 0),
)
SEED_COUNT = 11
ITERATIONS = sum(len(segment.arms) for segment in SEGMENTS)
SAMPLES = 32768
SHOTS = 32768
MAX_DURATION = 300
SECONDS_PER_ITERATION = 3.0
BUDGET_FRACTION = 0.9
PRICE_PER_SHOT = 1e-6
SEPARATION = 0.10
THRESHOLDS = {
    "level_tolerance": 0.07,
    "anchor_floor": 0.90,
    "dark_ceiling": 0.05,
    "dark_spread": 0.03,
    "anchor_drift": 0.03,
    "sentinel_share": 0.05,
    "null_level_tolerance": 0.07,
    "null_pair_spread": 0.07,
    "repeat_spread": 0.03,
    "repeat_failures": 2,
    "outlier_fraction": 0.10,
    "mutation_separation": SEPARATION,
}
# Readout model of the decision-chain power: the dark floor and the bright leak are the retained kernel-slice
# hardware readings (dark 0.0020 to 0.0026, bright 0.9982 to 0.9997), and the branch odds ratio follows from its
# half-level readings 0.5136 and 0.5187 (odds 1.056 and 1.078).
DARK_FLOOR = 0.0023
BRIGHT_LEAK = 0.0017
BRANCH_ODDS = 1.07
DECISIONS = {
    "admission": (
        f"a_anchor >= {THRESHOLDS['anchor_floor']} and a_dark <= {THRESHOLDS['dark_ceiling']}; every segment dark "
        f"within {THRESHOLDS['dark_spread']} of a_dark; early and late anchor T readings within "
        f"{THRESHOLDS['anchor_drift']}; at most {THRESHOLDS['repeat_failures']} of 44 repeated arm pairs differ by "
        f"more than {THRESHOLDS['repeat_spread']}; sentinel clicks at most {THRESHOLDS['sentinel_share']} of every "
        f"iteration's detected events; null levels within {THRESHOLDS['null_level_tolerance']} of 1/4 and within "
        f"{THRESHOLDS['null_pair_spread']} of each other. A failure marks the run 'instrument not admitted'."
    ),
    "conformance": (
        f"given admission, every T reading of the eight pathion-only blocks within {THRESHOLDS['level_tolerance']} "
        "of its ideal level, both reference-block readings within it, and at most 1 of the 18 T and F readings "
        "(floor of outlier_fraction x 18) farther away; otherwise the compiled mesh does not realize the programmed "
        "block at that tolerance"
    ),
    "mutation": (
        f"given admission, each C and N reading within {THRESHOLDS['level_tolerance']} of its mutated ideal level; "
        "a reading within the tolerance of the block's true top level instead shows the readout ignores that "
        "sign structure"
    ),
}


def gaussian_nodes(count: int = 2401) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    nodes = np.linspace(-6.0, 6.0, count)
    weights = np.exp(-(nodes**2) / 2)
    return nodes, weights / weights.sum()


def observed_levels(ideal: float, sigma: float, nodes: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Normalized level a' of one arm over mesh errors: theta + sigma x node, then the branch odds ratio."""
    theta = np.arcsin(np.sqrt(ideal))
    mesh = np.sin(theta + sigma * nodes) ** 2
    return np.asarray(BRANCH_ODDS * mesh / (BRANCH_ODDS * mesh + 1 - mesh))


def decision_chain_power(sigma: float) -> dict[str, float]:
    """Probability that each preregistered decision passes when every distinct (segment, arm) mesh carries an
    independent angle error of standard deviation sigma (the spread of a level at 1/2, in level units).

    The readout model is affine (dark floor, bright leak) behind a branch odds ratio, so a' equals the
    odds-shifted mesh level; binomial error (at most 0.002 per pooled arm) is omitted against tolerances of 0.07.
    """
    nodes, weights = gaussian_nodes()
    tolerance = THRESHOLDS["level_tolerance"]
    probability: dict[tuple[str, str], float] = {}
    for segment in SEGMENTS:
        block = operand_blocks(DIM, OPERANDS[segment.operand], segment.operand)[segment.ordinal]
        for arm in dict.fromkeys(segment.arms):
            if arm in ("D", "E0", "E1") or segment.role == "anchor":
                continue
            programmed, vector, _ = arm_program(block, arm)
            ideal = ideal_level(programmed, vector)
            levels = observed_levels(ideal, sigma, nodes)
            probability[(segment.name, arm)] = float(weights[np.abs(levels - ideal) <= tolerance].sum())
    tops = [p for (name, arm), p in probability.items() if arm == "T" and not name.startswith("reference")]
    reference = [p for (name, _), p in probability.items() if name.startswith("reference")]
    falls = [1 - p for (name, arm), p in probability.items() if arm == "F" and not name.startswith("reference")]
    within = np.zeros(len(falls) + 1)
    within[0] = 1.0
    for fall in falls:
        within = np.append(within * (1 - fall), 0.0) + np.append(0.0, within * fall)
    mutated = [p for (_, arm), p in probability.items() if arm in ("C", "N")]
    # Null arm: raw levels of the two basis inputs near 1/4, each within the tolerance and within the pair spread.
    raw = DARK_FLOOR + (1 - DARK_FLOOR - BRIGHT_LEAK) * observed_levels(0.25, sigma, nodes)
    near = np.abs(raw - 0.25) <= THRESHOLDS["null_level_tolerance"]
    pair = np.abs(raw[:, None] - raw[None, :]) <= THRESHOLDS["null_pair_spread"]
    null = float(weights @ (pair & near[:, None] & near[None, :]).astype(float) @ weights)
    conformance = float(np.prod(tops) * np.prod(reference) * within[:2].sum())
    mutation = float(np.prod(mutated))
    return {
        "sigma": sigma,
        "admission": null,
        "conformance": conformance,
        "mutation": mutation,
        "all": null * conformance * mutation,
    }


@cache
def sign_table(dim: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(cd_core.cd_sign(dim, p, q) for q in range(dim)) for p in range(dim))


@dataclass(frozen=True)
class Block:
    """A 4 x 4 coset block of the left multiplication by a four-term operand: B[r, c] maps inputs[c] to outputs[r]."""

    operand: str
    ordinal: int
    inputs: tuple[int, ...]
    outputs: tuple[int, ...]
    matrix: npt.NDArray[np.int64]


def operand_blocks(dim: int, terms: dict[int, int], name: str = "") -> list[Block]:
    """The coset blocks of one four-term flat operand, ordered by their least input as in the design report."""
    first = min(terms)
    group = sorted({0} | {term ^ first for term in terms})
    if len(group) != 4 or len(terms) != 4:
        raise ValueError(f"{terms} is not a four-term flat")
    table = sign_table(dim)
    seen: set[int] = set()
    blocks: list[Block] = []
    for start in range(dim):
        if start in seen:
            continue
        inputs = tuple(sorted(start ^ element for element in group))
        seen.update(inputs)
        outputs = tuple(sorted(first ^ q for q in inputs))
        matrix = np.zeros((4, 4), dtype=np.int64)
        for column, q in enumerate(inputs):
            for term, coefficient in terms.items():
                matrix[outputs.index(term ^ q), column] += coefficient * table[term][q]
        blocks.append(Block(name, len(blocks), inputs, outputs, matrix))
    return blocks


def check_against_cd_core(block: Block, terms: dict[int, int]) -> None:
    """Every column of the block equals the exact cd_core product of the operand with that basis element."""
    left = [0] * DIM
    for term, coefficient in terms.items():
        left[term] = coefficient
    for column, q in enumerate(block.inputs):
        right = [0] * DIM
        right[q] = 1
        product = cd_core.cd_multiply_exact(DIM, left, right)
        for index in range(DIM):
            expected = int(block.matrix[block.outputs.index(index), column]) if index in block.outputs else 0
            if product[index] != expected:
                raise ValueError(f"{block.operand} block {block.ordinal}: column {q} differs from cd_core at {index}")


_ROW_PERMUTATIONS = np.array(list(itertools.permutations(range(4))))
_ROWS = np.repeat(_ROW_PERMUTATIONS, len(_ROW_PERMUTATIONS), axis=0)
_COLUMNS = np.tile(_ROW_PERMUTATIONS, (len(_ROW_PERMUTATIONS), 1))
_BIT = 1 << np.arange(16)


def canonical_class(matrix: npt.NDArray[np.int64]) -> int:
    """Smallest key over row and column permutations of the matrix with first row and column negated to +1."""
    stack = matrix[_ROWS[:, :, None], _COLUMNS[:, None, :]]
    stack = stack * stack[:, :1, :]
    stack = stack * stack[:, :, :1]
    keys = ((stack.reshape(len(stack), 16) > 0) * _BIT).sum(axis=1)
    return int(keys.min())


@cache
def class_census(dim: int) -> frozenset[int]:
    """Equivalence classes of the coset blocks of every four-term flat operand and sign choice in dimension dim."""
    table = sign_table(dim)
    distinct: set[bytes] = set()
    for a, b, c in itertools.combinations(range(dim), 3):
        d = a ^ b ^ c
        if d <= c or d >= dim:
            continue
        flat = (a, b, c, d)
        group = sorted({0} | {term ^ a for term in flat})
        seen: set[int] = set()
        for start in range(dim):
            if start in seen:
                continue
            inputs = tuple(sorted(start ^ element for element in group))
            seen.update(inputs)
            outputs = tuple(sorted(a ^ q for q in inputs))
            parts = np.zeros((4, 4, 4), dtype=np.int64)
            for column, q in enumerate(inputs):
                for slot, term in enumerate(flat):
                    parts[slot, outputs.index(term ^ q), column] = table[term][q]
            for signs in itertools.product((1, -1), repeat=3):
                matrix = parts[0] + sum(s * parts[k + 1] for k, s in enumerate(signs))
                distinct.add(matrix.astype(np.int8).tobytes())
    return frozenset(
        canonical_class(np.frombuffer(raw, dtype=np.int8).reshape(4, 4).astype(np.int64)) for raw in distinct
    )


def verify_classes() -> dict[str, Any]:
    """The pathion-only blocks fall in classes absent at D = 16, and B12 carries two inequivalent such classes."""
    low, high = class_census(16), class_census(DIM)
    if len(low) != 5 or len(high) != 9 or not low <= high:
        raise ValueError(f"expected 5 classes at D = 16 inside 9 at D = 32, found {len(low)} and {len(high)}")
    only_high = high - low
    classes: dict[str, dict[int, int]] = {}
    for name in ("B12", "C8", "A16"):
        classes[name] = {
            block.ordinal: canonical_class(block.matrix) for block in operand_blocks(DIM, OPERANDS[name], name)
        }
    pathion = {
        "B12": (2, 3, 6, 7),
        "C8": (4, 5, 6, 7),
    }
    for name, ordinals in pathion.items():
        for ordinal in ordinals:
            if classes[name][ordinal] not in only_high:
                raise ValueError(f"{name} block {ordinal} lies in a class that exists at D = 16")
    if classes["B12"][2] != classes["B12"][7] or classes["B12"][3] != classes["B12"][6]:
        raise ValueError("B12 blocks 2 and 7 or 3 and 6 differ in class")
    distinct = {classes["B12"][2], classes["B12"][3], classes["C8"][4]}
    if len(distinct) != 3 or len({classes["C8"][o] for o in pathion["C8"]}) != 1:
        raise ValueError("the pathion-only blocks do not form three inequivalent classes")
    for name, ordinals in (("B12", (0, 1, 4, 5)), ("C8", (0, 1, 2, 3))):
        for ordinal in ordinals:
            if classes[name][ordinal] not in low:
                raise ValueError(f"{name} block {ordinal} is expected in a class present at D = 16")
    anchor = classes["A16"][4]
    if anchor not in only_high or len({classes["A16"][o] for o in (4, 5, 6, 7)}) != 1:
        raise ValueError("the A16 anchor blocks are not one class absent at D = 16")
    return {
        "classes_d16": len(low),
        "classes_d32": len(high),
        "classes_only_d32": len(only_high),
        "pathion_only_classes": {
            "B12 blocks 2, 7": classes["B12"][2],
            "B12 blocks 3, 6": classes["B12"][3],
            "C8 blocks 4 to 7": classes["C8"][4],
        },
        "anchor_class": anchor,
    }


def sign_fixed(vector: Matrix) -> Matrix:
    """The vector with its first component above 1e-9 in magnitude made positive."""
    first = next(value for value in vector if abs(value) > 1e-9)
    return vector if first > 0 else -vector


def top_vector(matrix: npt.NDArray[np.int64]) -> Matrix:
    values, vectors = np.linalg.eigh(matrix.T @ matrix)
    if values[-1] - values[-2] < 1e-9:
        raise ValueError("the top Gram eigenvalue is degenerate")
    return sign_fixed(vectors[:, -1])


def kernel_vector(matrix: npt.NDArray[np.int64]) -> Matrix:
    """The first rational kernel vector of B, as a unit vector."""
    basis = sym.Matrix(matrix.tolist()).nullspace()
    if not basis:
        raise ValueError("the block has no kernel")
    vector = np.array([float(entry) for entry in basis[0]])
    return sign_fixed(vector / np.linalg.norm(vector))


def ideal_level(matrix: npt.NDArray[np.int64], vector: Matrix) -> float:
    return float(np.linalg.norm(matrix @ vector) ** 2 / SCALE**2)


def flipped_vector(matrix: npt.NDArray[np.int64], vector: Matrix) -> Matrix:
    """The top vector with the one component whose sign flip moves the level most (least index on a tie)."""
    true = ideal_level(matrix, vector)
    shifts = []
    for index in range(4):
        trial = vector.copy()
        trial[index] *= -1
        shifts.append(round(abs(ideal_level(matrix, trial) - true), 9))
    best = int(np.argmax(shifts))
    result = vector.copy()
    result[best] *= -1
    return result


def halmos_dilation(contraction: Matrix) -> Matrix:
    """Orthogonal 8 x 8 matrix whose upper-left 4 x 4 block is the contraction V (Halmos dilation by SVD)."""
    left, singular, right_t = np.linalg.svd(contraction)
    defect = np.sqrt(np.clip(1 - singular**2, 0, None))
    upper = left @ np.diag(defect) @ left.T
    lower = right_t.T @ np.diag(defect) @ right_t
    dilation = np.block([[contraction, upper], [lower, -contraction.T]])
    if not np.allclose(dilation @ dilation.T, np.eye(8), atol=1e-12, rtol=0):
        raise ValueError("the Halmos dilation is not orthogonal")
    return np.asarray(dilation)


def preparation(vector: Matrix) -> Matrix:
    """Householder reflection R with R e_0 = vector."""
    unit = vector / np.linalg.norm(vector)
    direction = unit - np.eye(4)[0]
    if np.linalg.norm(direction) < 1e-12:
        return np.eye(4)
    direction = direction / np.linalg.norm(direction)
    reflection = np.eye(4) - 2 * np.outer(direction, direction)
    if not np.allclose(reflection @ np.eye(4)[0], unit, atol=1e-12, rtol=0):
        raise ValueError("the preparation reflection misses its input vector")
    return np.asarray(reflection)


def negated_matrix(matrix: npt.NDArray[np.int64], vector: Matrix) -> tuple[npt.NDArray[np.int64], tuple[int, int]]:
    """The block with the one entry negated whose negation moves the level most (first in row-major order on a tie)."""
    true = ideal_level(matrix, vector)
    shifts = []
    for row, column in itertools.product(range(4), repeat=2):
        trial = matrix.copy()
        trial[row, column] *= -1
        shifts.append(round(abs(ideal_level(trial, vector) - true), 9))
    row, column = divmod(int(np.argmax(shifts)), 4)
    result = matrix.copy()
    result[row, column] *= -1
    return result, (row, column)


def arm_program(block: Block, arm: str) -> tuple[npt.NDArray[np.int64], Matrix, dict[str, Any]]:
    """The matrix whose B/4 the mesh realizes, the input vector and the mutation detail, for one arm of a block."""
    matrix = block.matrix
    top = top_vector(matrix)
    if arm == "T":
        return matrix, top, {}
    if arm == "D":
        return matrix, kernel_vector(matrix), {}
    if arm == "F":
        flipped = flipped_vector(matrix, top)
        return matrix, flipped, {"flipped_component": int(np.flatnonzero(flipped != top)[0])}
    if arm == "C":
        return np.ones((4, 4), dtype=np.int64), top, {}
    if arm == "N":
        mutated, entry = negated_matrix(matrix, top)
        return mutated, top, {"negated_entry": list(entry)}
    if arm in ("E0", "E1"):
        return matrix, np.eye(4)[int(arm[1])], {}
    raise ValueError(f"unknown arm {arm!r}")


def slos_probabilities(unitary: npt.NDArray[np.complex128]) -> npt.NDArray[np.float64]:
    """Single-photon output law of the 12-mode unitary from a local Perceval SLOS run, photon on mode 0."""
    import perceval as pcvl

    processor = pcvl.Processor("SLOS", pcvl.Unitary(pcvl.Matrix(unitary)))
    processor.with_input(pcvl.BasicState([1] + [0] * (unitary.shape[0] - 1)))
    distribution = pcvl.algorithm.Sampler(processor).probs()["results"]
    law = np.zeros(unitary.shape[0])
    for state, probability in distribution.items():
        law[list(state).index(1)] = probability
    return law


Task = tuple[int, str, int, int, str, int, int]


def build_setting(task: Task) -> dict[str, Any]:
    index, operand, ordinal, seed_index, arm, seed, position = task
    block = operand_blocks(DIM, OPERANDS[operand], operand)[ordinal]
    check_against_cd_core(block, OPERANDS[operand])
    programmed, vector, detail = arm_program(block, arm)
    contraction = programmed / SCALE
    unit = vector / np.linalg.norm(vector)
    dilation = halmos_dilation(contraction)
    prepared = np.eye(8)
    prepared[:4, :4] = preparation(unit)
    unitary = dilation @ prepared
    full = np.eye(12, dtype=np.complex128)
    full[:8, :8] = unitary
    law = slos_probabilities(full)
    analytic = np.abs(full[:, 0]) ** 2
    success = float(np.linalg.norm(contraction @ unit) ** 2)
    if (
        float(np.max(np.abs(law - analytic))) > 1e-9
        or abs(float(law[:4].sum()) - success) > 1e-9
        or not np.allclose(law[:4], (contraction @ unit) ** 2, atol=1e-9, rtol=0)
        or float(law[8:].sum()) > 1e-9
    ):
        raise ValueError(f"{operand} block {ordinal} arm {arm}: the SLOS law differs from the analytic B/4 law")
    true_level = ideal_level(block.matrix, top_vector(block.matrix))
    _, parameters = photonic_template(unitary.astype(np.complex128))
    return {
        "name": f"{operand.lower()}-b{ordinal}-i{position:02d}-{arm}",
        "observation_index": index,
        "compilation_seed": seed,
        "seed_index": seed_index,
        "operand": operand,
        "block": ordinal,
        "inputs": list(block.inputs),
        "outputs": list(block.outputs),
        "arm": arm,
        "mutation": detail,
        "input_vector": [float(v) for v in unit],
        "circuit_params": parameters,
        "column": [[float(v.real), float(v.imag)] for v in full[:, 0]],
        "operator": encoded(full),
        "ideal_success": success,
        "ideal_label_law": [float(v) for v in law[:8]],
        "true_top_level": true_level,
    }


def setting_tasks(seeds: list[int]) -> list[Task]:
    tasks: list[Task] = []
    for segment in SEGMENTS:
        for arm in segment.arms:
            tasks.append(
                (
                    len(tasks),
                    segment.operand,
                    segment.ordinal,
                    segment.seed_index,
                    arm,
                    seeds[segment.seed_index],
                    len(tasks),
                )
            )
    return tasks


def check_separations(settings: list[dict[str, Any]]) -> None:
    """Every mutation arm moves the ideal level by at least SEPARATION from the true top level of its block."""
    for setting in settings:
        if setting["arm"] in ("F", "C", "N") and abs(setting["ideal_success"] - setting["true_top_level"]) < SEPARATION:
            raise ValueError(f"{setting['name']}: the mutation moves the ideal level by less than {SEPARATION}")


def check_duration() -> float:
    """Expected seconds from the measured Ascella iteration time; the packing note admits floor(0.9 * 300 / t)."""
    if ITERATIONS > int(BUDGET_FRACTION * MAX_DURATION / SECONDS_PER_ITERATION):
        raise ValueError(f"{ITERATIONS} iterations exceed the packing margin of the {MAX_DURATION} s cut")
    return ITERATIONS * SECONDS_PER_ITERATION


def documents(draw: Path, job: str, platform: str) -> dict[str, bytes]:
    source = json.loads(draw.read_bytes())
    anu_qrng.admit(source)
    seeds = source["values"]
    if (
        source["type"] != "uint16"
        or len(seeds) != SEED_COUNT
        or any(type(seed) is not int or not 0 <= seed <= 65535 for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError(f"the case needs {SEED_COUNT} distinct uint16 QRNG values")
    classes = verify_classes()
    settings = ordered_map(build_setting, setting_tasks(seeds), min_items=1)
    check_separations(settings)
    seconds = check_duration()
    mesh, _ = photonic_template(np.eye(8, dtype=np.complex128))
    circuit = {**mesh, "modes": 12, "input_state": [1] + [0] * 11}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_pathion_four_term_blocks",
        "job": job,
        "platforms": [platform],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES * len(settings),
        "max_shots": SHOTS * len(settings),
        "max_duration": MAX_DURATION,
        "max_credits": 1.04,
        "mitigations": [],
        "output_modes": 12,
        "logical_modes": list(range(8)),
        "eligibility": "single detected photon; success modes 0..3, failure modes 4..7, sentinel modes 8..11",
        "expected_seconds": seconds,
        "seed_source": {
            "script": "scripts/ascella_pathion_four_term_blocks.py",
            "flag": "--draw",
            "experiment": "ascella-pathion-four-term-blocks",
            "sources": [f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}" for index in range(SEED_COUNT)],
            "usage": (
                "one compilation seed per segment of consecutive iterations on one block; the early and late anchor "
                "segments share seed index 0; the same seeds serve the simulator and hardware cases"
            ),
        },
        "analysis_sources": {
            name: sha256_bytes((ROOT / name).read_bytes())
            for name in (
                "scripts/ascella_pathion_four_term_blocks.py",
                "scripts/hypercomplex_cases.py",
                "scripts/qd_platform.py",
                "gororoba_quantum/cd_core.py",
            )
        },
        "operands": {
            name: {str(term): coefficient for term, coefficient in terms.items()} for name, terms in OPERANDS.items()
        },
        "block_classes": classes,
        "arms": ARM_MEANING,
        "segments": [
            {
                "name": segment.name,
                "role": segment.role,
                "operand": segment.operand,
                "block": segment.ordinal,
                "arms": list(segment.arms),
                "seed_index": segment.seed_index,
            }
            for segment in SEGMENTS
        ],
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "question": (
                "Does the compiled 12-mode mesh realize the programmed four-branch pathion block "
                "(16 independent cocycle signs, levels 3/4, 1/4 and 0.0955, 0.6545) and follow each mutation?"
            ),
            "inference": "descriptive against numeric thresholds; report all detected modes and event denominators",
            "normalization": (
                "a' = (a - a_dark) / (a_anchor - a_dark); a is the success fraction of clicks in modes 0..7"
            ),
            "thresholds": THRESHOLDS,
            "decisions": DECISIONS,
            "success_modes": [0, 1, 2, 3],
            "failure_modes": [4, 5, 6, 7],
            "sentinel_modes": [8, 9, 10, 11],
            "boundary": (
                "Conformance of programmed operator blocks to their interference law on one 12-mode mesh; "
                "the client computes every cd_core sign, so the chip does not compute the algebra."
            ),
        },
    }
    template_experiment(manifest, circuit)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def ideal_table() -> list[dict[str, Any]]:
    """Ideal level of every distinct (block, arm) of the case, from the exact block and the Halmos dilation."""
    rows = []
    for segment in SEGMENTS:
        block = operand_blocks(DIM, OPERANDS[segment.operand], segment.operand)[segment.ordinal]
        values = np.linalg.eigvalsh(block.matrix.T @ block.matrix)
        levels = {}
        for arm in dict.fromkeys(segment.arms):
            programmed, vector, _ = arm_program(block, arm)
            levels[arm] = round(ideal_level(programmed, vector), 6)
        rows.append(
            {
                "segment": segment.name,
                "operand": segment.operand,
                "block": segment.ordinal,
                "gram_spectrum": [round(float(v), 4) + 0.0 for v in values],
                "levels": levels,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ideal", action="store_true", help="print the ideal levels and the class census, no files")
    parser.add_argument("--power", action="store_true", help="print the decision-chain pass probabilities, no files")
    parser.add_argument("--draw", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--platform", choices=("sim:ascella", "qpu:ascella"))
    args = parser.parse_args()
    if args.ideal:
        print(json.dumps({"classes": verify_classes(), "levels": ideal_table()}, indent=1))
        return 0
    if args.power:
        for sigma in (0.005, 0.01, 0.02, 0.03, 0.04):
            print(json.dumps({key: round(value, 4) for key, value in decision_chain_power(sigma).items()}))
        return 0
    if args.draw is None or args.out is None or args.platform is None:
        parser.error("--draw, --out and --platform are required unless --ideal or --power is given")
    draw = args.draw.resolve()
    payload = documents(draw, "simulator" if args.platform.startswith("sim:") else "hardware", args.platform)
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (args.out / name).write_bytes(data)
    print(f"{args.out}: {ITERATIONS} settings; request sha256 {sha256_bytes(payload['cases.json'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
