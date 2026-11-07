"""Build one-photon, two-coset-block optical probes of the pathion-only A5 blocks for Ascella (9 data modes)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import anu_qrng  # noqa: E402
import ascella_pathion_four_term_blocks as base  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

import cd_core  # noqa: E402
from parallel import ordered_map  # noqa: E402

Matrix = npt.NDArray[np.float64]

FAMILY = "ascella_pathion_coset_block_pairs"
PREDECESSOR_RUN = "results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
ACTIVE = 9
WIDTH = 12
SLOT_MODES = {"A": (0, 1, 2, 3), "B": (4, 5, 6, 7)}
FAILURE_MODE = 8
SENTINEL_MODES = (9, 10, 11)

# Block code -> (operand, ordinal). The codes a to i are the nine sign-carrying blocks of the predecessor case
# (the D = 16 reference, the four B12 and the four C8 pathion-only blocks); p and q are the rank-1 anchor blocks.
BLOCKS: dict[str, tuple[str, int]] = {
    "a": ("B12", 0),
    "b": ("B12", 2),
    "c": ("B12", 3),
    "d": ("B12", 6),
    "e": ("B12", 7),
    "f": ("C8", 4),
    "g": ("C8", 5),
    "h": ("C8", 6),
    "i": ("C8", 7),
    "p": ("A16", 4),
    "q": ("A16", 5),
}
SIGN_BLOCKS = "abcdefghi"
SAME_CLASS_PAIRS = (("i", "f"), ("e", "b"), ("c", "d"), ("g", "h"))
ARMS_FOR_BLOCK = ("T", "F", "C", "N")
Item = tuple[str, str]


@dataclass(frozen=True)
class Design:
    """One distinct setting: two blocks with their arms sharing one photon, under one compilation seed."""

    name: str
    role: str
    group: str
    first: Item
    second: Item


ANCHOR = Design("anchor", "anchor", "", ("p", "T"), ("q", "D"))
DARK = Design("dark", "dark", "", ("p", "D"), ("q", "D"))
# Sign settings in their first-half order. Settings that carry a block-7 item (e, i) come early, and the mirror puts
# every setting at the matching late position, so the mean job position of each block equals the job midpoint.
SIGN_DESIGNS = (
    Design("i-f-TT", "sign", "independence-c8", ("i", "T"), ("f", "T")),
    Design("i-f-TD", "sign", "independence-c8", ("i", "T"), ("f", "D")),
    Design("e-b-TT", "sign", "control-b12", ("e", "T"), ("b", "T")),
    Design("b-i-CC", "sign", "", ("b", "C"), ("i", "C")),
    Design("e-g-CN", "sign", "", ("e", "C"), ("g", "N")),
    Design("b-i-NN", "sign", "", ("b", "N"), ("i", "N")),
    Design("e-c-NN", "sign", "", ("e", "N"), ("c", "N")),
    Design("d-i-FF", "sign", "", ("d", "F"), ("i", "F")),
    Design("e-h-FT", "sign", "", ("e", "F"), ("h", "T")),
    Design("i-f-TC", "sign", "independence-c8", ("i", "T"), ("f", "C")),
    Design("i-f-TN", "sign", "independence-c8", ("i", "T"), ("f", "N")),
    Design("c-d-TT", "sign", "independence-b12", ("c", "T"), ("d", "T")),
    Design("c-d-TD", "sign", "independence-b12", ("c", "T"), ("d", "D")),
    Design("c-d-TC", "sign", "independence-b12", ("c", "T"), ("d", "C")),
    Design("c-d-TN", "sign", "independence-b12", ("c", "T"), ("d", "N")),
    Design("g-h-TT", "sign", "control-c8", ("g", "T"), ("h", "T")),
    Design("a-g-TC", "sign", "", ("a", "T"), ("g", "C")),
    Design("a-h-CC", "sign", "", ("a", "C"), ("h", "C")),
    Design("a-h-NN", "sign", "", ("a", "N"), ("h", "N")),
    Design("a-f-FF", "sign", "", ("a", "F"), ("f", "F")),
    Design("b-g-FF", "sign", "", ("b", "F"), ("g", "F")),
    Design("c-h-FF", "sign", "", ("c", "F"), ("h", "F")),
    Design("b-f-EE", "null", "", ("b", "E0"), ("f", "E1")),
)
DESIGNS = (ANCHOR, DARK, *SIGN_DESIGNS)
# Independence groups: item 0 of each design stays at T while the partner block takes the arms T, C, N and D.
INDEPENDENCE_GROUPS = ("independence-c8", "independence-b12")

SAMPLES = 131072
SHOTS = 131072
MAX_DURATION = 300
SECONDS_PER_ITERATION = 3.2
BUDGET_FRACTION = 0.9
# Retained Ascella iteration times: about 3 s per iteration at 10,000 samples (job 66331d15), 32,768 (job f3a11b5f),
# and 156,159 two-photon shots (job ae37fae6, 3.1 s); 1,206,300 shots in 25 s bound the throughput below by 48,000
# shots per second. SHOTS stays inside the measured shots-per-iteration range.
MEASURED_MAX_SHOTS = 156159
THROUGHPUT_BOUND = 48000.0
PRICE_PER_SHOT = 1e-6
MAX_CREDITS = 1.14
SEPARATION = 0.10
SIM_GATE_TOLERANCE = 0.01
CONTRAST_FRACTION = 0.5
THRESHOLDS = {
    "level_tolerance": 0.07,
    "anchor_floor": 0.90,
    "dark_ceiling": 0.05,
    "anchor_drift": 0.03,
    "dark_drift": 0.03,
    "sentinel_share": 0.05,
    "null_level_tolerance": 0.07,
    "null_pair_spread": 0.07,
    "mirror_spread": 0.07,
    "mirror_fraction": 0.10,
    "crosstalk_ceiling": 0.03,
    "bright_partner_level": 0.5,
    "independence_range": 0.07,
    "outlier_fraction": 0.10,
    "mutation_separation": SEPARATION,
    "contrast_fraction": CONTRAST_FRACTION,
}
DECISIONS = {
    "admission": (
        "per-slot anchor (A16 rank 1, ideal level 1 against a kernel partner) and per-slot dark (both blocks in "
        f"their kernels): bright raw level at least {THRESHOLDS['anchor_floor']}, dark at most "
        f"{THRESHOLDS['dark_ceiling']}; early and late anchors within {THRESHOLDS['anchor_drift']} and early and "
        f"late darks within {THRESHOLDS['dark_drift']}; sentinel clicks at most {THRESHOLDS['sentinel_share']} of "
        "every iteration's events; the two null readings within "
        f"{THRESHOLDS['null_level_tolerance']} of 1/4 and each other; at most {THRESHOLDS['mirror_fraction']} of the "
        f"block readings differ between the two slot orientations by more than {THRESHOLDS['mirror_spread']}. A "
        "failure marks the run 'instrument not admitted'."
    ),
    "conformance": (
        f"given admission, every T reading within {THRESHOLDS['level_tolerance']} of its ideal level and at most "
        f"floor({THRESHOLDS['outlier_fraction']} x readings) of the T and F readings farther away"
    ),
    "mutation": (
        f"given admission, each C and N reading within {THRESHOLDS['level_tolerance']} of its mutated ideal level; a "
        "reading within the tolerance of the block's true top level instead shows that the readout ignores that "
        "sign structure"
    ),
    "crosstalk": (
        "given admission, the dark slot beside a bright partner (ideal level at least "
        f"{THRESHOLDS['bright_partner_level']}) reads at most {THRESHOLDS['crosstalk_ceiling']} above the slot's own "
        "dark reading"
    ),
    "independence": (
        f"given admission, the calibrated level of the fixed T block ranges at most {THRESHOLDS['independence_range']} "
        "over the partner arms T, C, N and D of its group"
    ),
    "c8_spread": (
        "reported whatever the admission: the within-class contrast of the C8 T readings (block 7 minus the mean of "
        "blocks 4, 5 and 6), per slot, against contrast_fraction x the predecessor's contrast; both slots at or "
        "above it: the spread follows the block; one slot: it follows the mode slot; neither: not reproduced"
    ),
}


@dataclass(frozen=True)
class Resolved:
    """A block-arm item with its programmed contraction, input vector and ideal level."""

    code: str
    arm: str
    operand: str
    ordinal: int
    inputs: tuple[int, ...]
    outputs: tuple[int, ...]
    contraction: Matrix
    unit: Matrix
    level: float
    true_top_level: float
    mutation: dict[str, Any]


def cd_level(block: base.Block, operand: str, programmed: npt.NDArray[np.int64], unit: Matrix) -> float:
    """The level of the true block through the full 32-dimensional product, from cd_core.left_mult_matrix."""
    terms = base.OPERANDS[operand]
    left = [0.0] * base.DIM
    for term, coefficient in terms.items():
        left[term] = float(coefficient)
    matrix = np.array(cd_core.left_mult_matrix(base.DIM, left))
    vector = np.zeros(base.DIM)
    vector[list(block.inputs)] = unit
    product = matrix @ vector
    outside = np.delete(product, list(block.outputs))
    if float(np.max(np.abs(outside))) > 1e-12 or not np.array_equal(programmed, block.matrix):
        raise ValueError(f"{operand} block {block.ordinal}: the product leaves the block or the matrix differs")
    return float(np.sum(product[list(block.outputs)] ** 2) / base.SCALE**2)


def resolve(code: str, arm: str) -> Resolved:
    operand, ordinal = BLOCKS[code]
    block = base.operand_blocks(base.DIM, base.OPERANDS[operand], operand)[ordinal]
    base.check_against_cd_core(block, base.OPERANDS[operand])
    programmed, vector, detail = base.arm_program(block, arm)
    unit = vector / np.linalg.norm(vector)
    level = base.ideal_level(programmed, unit)
    if arm in ("T", "D", "F", "E0", "E1") and abs(cd_level(block, operand, programmed, unit) - level) > 1e-12:
        raise ValueError(f"{code} {arm}: the level differs from the cd_core product")
    true_top = base.ideal_level(block.matrix, base.top_vector(block.matrix))
    return Resolved(
        code,
        arm,
        operand,
        ordinal,
        block.inputs,
        block.outputs,
        programmed / base.SCALE,
        unit,
        level,
        true_top,
        detail,
    )


def householder(vector: Matrix) -> Matrix:
    """Orthogonal reflection R with R e_0 = vector (unit)."""
    size = len(vector)
    direction = vector - np.eye(size)[0]
    if np.linalg.norm(direction) < 1e-12:
        return np.eye(size)
    direction = direction / np.linalg.norm(direction)
    reflection = np.eye(size) - 2 * np.outer(direction, direction)
    if not np.allclose(reflection[:, 0], vector, atol=1e-12, rtol=0):
        raise ValueError("the preparation reflection misses its input vector")
    return np.asarray(reflection)


Task = tuple[int, str, int, int, int, str, str, str, str, str, str]


def build_iteration(task: Task) -> dict[str, Any]:
    position, name, orientation, seed_index, seed, role, code_x, arm_x, code_y, arm_y, group = task
    items = [resolve(code_x, arm_x), resolve(code_y, arm_y)]
    if orientation == 1:
        items.reverse()
    first, second = items
    psi = np.concatenate([first.contraction @ first.unit, second.contraction @ second.unit]) / math.sqrt(2)
    norm_squared = float(psi @ psi)
    if norm_squared > 1 + 1e-12:
        raise ValueError(f"{name}: the common scale 1/{base.SCALE} overfills the photon ({norm_squared})")
    vector = np.concatenate([psi, [math.sqrt(max(0.0, 1 - norm_squared))]])
    reflection = householder(vector)
    full = np.eye(WIDTH, dtype=np.complex128)
    full[:ACTIVE, :ACTIVE] = reflection
    law = base.slos_probabilities(full)
    analytic = np.abs(full[:, 0]) ** 2
    levels = [2 * float(law[list(modes)].sum()) for modes in SLOT_MODES.values()]
    expected = (first.level, second.level)
    if (
        float(np.max(np.abs(law - analytic))) > 1e-9
        or float(law[ACTIVE:].sum()) > 1e-9
        or abs(levels[0] - expected[0]) > 1e-9
        or abs(levels[1] - expected[1]) > 1e-9
        or abs(float(law[FAILURE_MODE]) - (1 - norm_squared)) > 1e-9
        or not np.allclose(law[:4], (first.contraction @ first.unit) ** 2 / 2, atol=1e-9, rtol=0)
        or not np.allclose(law[4:8], (second.contraction @ second.unit) ** 2 / 2, atol=1e-9, rtol=0)
    ):
        raise ValueError(f"{name}: the SLOS law differs from the analytic pair law")
    _, parameters = photonic_template(reflection.astype(np.complex128))
    return {
        "name": f"{name}-o{orientation}-i{position:02d}",
        "observation_index": position,
        "setting": name,
        "role": role,
        "group": group,
        "orientation": orientation,
        "seed_index": seed_index,
        "compilation_seed": seed,
        "slots": {
            slot: {
                "block": f"{item.operand}/{item.ordinal}",
                "code": item.code,
                "arm": item.arm,
                "inputs": list(item.inputs),
                "outputs": list(item.outputs),
                "ideal_level": item.level,
                "true_top_level": item.true_top_level,
                "mutation": item.mutation,
                "input_vector": [float(v) for v in item.unit],
            }
            for slot, item in zip(SLOT_MODES, (first, second), strict=True)
        },
        "ideal_levels": [first.level, second.level],
        "ideal_failure": float(law[FAILURE_MODE]),
        "ideal_label_law": [float(v) for v in law[:ACTIVE]],
        "circuit_params": parameters,
        "column": [[float(v.real), float(v.imag)] for v in full[:, 0]],
        "operator": encoded(full),
    }


def sequence() -> list[tuple[Design, int]]:
    """Setting order of the job: anchor in both slot orientations, dark, the sign settings, and the exact mirror.

    A sign setting runs in one slot orientation in the first half and in the swapped orientation at its mirror
    position, so every block item reads once in each slot and drift pools across the pair. The anchor and dark
    requests repeat unchanged at the mirror positions, so their early and late readings measure drift directly.
    """
    forward = [(design, k % 2) for k, design in enumerate(SIGN_DESIGNS)]
    backward = [(design, 1 - orientation) for design, orientation in reversed(forward)]
    return [(ANCHOR, 0), (ANCHOR, 1), (DARK, 0), *forward, *backward, (DARK, 0), (ANCHOR, 1), (ANCHOR, 0)]


def seed_index(design: Design) -> int:
    return DESIGNS.index(design)


SEED_COUNT = len(DESIGNS)
ITERATIONS = len(sequence())


def check_coverage() -> dict[str, Any]:
    """Every sign block carries the T, F, C and N arms (B12 block 3 has no C arm: its cocycle-free level equals T)."""
    present: dict[str, set[str]] = {code: set() for code in SIGN_BLOCKS}
    for design in SIGN_DESIGNS:
        for code, arm in (design.first, design.second):
            present[code].add(arm)
    for code in SIGN_BLOCKS:
        wanted = {"T", "F", "N"} | ({"C"} if code != "c" else set())
        if not wanted <= present[code]:
            raise ValueError(f"block {code} lacks arms {sorted(wanted - present[code])}")
    pairs = {
        frozenset((d.first[0], d.second[0]))
        for d in SIGN_DESIGNS
        if d.first[1] == "T" and d.second[1] == "T" and d.role == "sign"
    }
    if any(frozenset(pair) not in pairs for pair in SAME_CLASS_PAIRS):
        raise ValueError("a same-class T/T pair is missing")
    for group in INDEPENDENCE_GROUPS:
        members = [d for d in SIGN_DESIGNS if d.group == group]
        if len({d.first for d in members}) != 1 or members[0].first[1] != "T":
            raise ValueError(f"{group}: item 0 must stay at T")
        if {d.second[1] for d in members} != {"T", "C", "N", "D"} or len({d.second[0] for d in members}) != 1:
            raise ValueError(f"{group}: the partner must take T, C, N and D on one block")
    return {code: sorted(arms) for code, arms in present.items()}


def check_sequence(entries: list[tuple[Design, int]]) -> None:
    """The setting order is a palindrome and each sign setting runs in both slot orientations."""
    names = [design.name for design, _ in entries]
    if names != names[::-1]:
        raise ValueError("the setting order is not a palindrome")
    for design in SIGN_DESIGNS:
        orientations = sorted(o for d, o in entries if d is design)
        if orientations != [0, 1]:
            raise ValueError(f"{design.name} does not run once in each slot orientation")


def check_duration() -> float:
    """Expected seconds: the measured iteration time, floored by the throughput bound at this shot budget."""
    if SHOTS > MEASURED_MAX_SHOTS:
        raise ValueError(f"{SHOTS} shots per iteration exceed the measured range {MEASURED_MAX_SHOTS}")
    per = max(SECONDS_PER_ITERATION, SHOTS / THROUGHPUT_BOUND)
    if ITERATIONS > int(BUDGET_FRACTION * MAX_DURATION / per):
        raise ValueError(f"{ITERATIONS} iterations exceed the packing margin of the {MAX_DURATION} s cut")
    return ITERATIONS * per


def standard_errors() -> dict[str, float]:
    """Binomial standard error of a level read as twice a click share: sqrt(L (2 - L) / n)."""
    result = {}
    for level in (0.75, 0.6545, 0.5, 0.25):
        result[f"L={level} one iteration"] = math.sqrt(level * (2 - level) / SAMPLES)
        result[f"L={level} two iterations"] = math.sqrt(level * (2 - level) / (2 * SAMPLES))
    return result


def phi(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def contrast_power(predecessor_contrast: float, sigma_mesh: float) -> dict[str, float]:
    """Chance that a slot's block-7 contrast clears the reproduction threshold when the effect is the
    predecessor's, and when it is absent. The contrast is the block-7 cell minus the mean of three cells, each cell
    one iteration of the top C8 level with binomial variance L (2 - L) / n and mesh variance sigma_mesh squared.
    Exactly one slot clearing the threshold is the verdict "follows the mode slot", so its probability under a
    block effect (present) and under no effect (absent) is the misattribution rate of the test."""
    level = (3 + math.sqrt(5)) / 8
    cell = math.sqrt(level * (2 - level) / SAMPLES) ** 2 + sigma_mesh**2
    spread = math.sqrt(cell * (1 + 1 / 3))
    threshold = CONTRAST_FRACTION * predecessor_contrast
    present = 1 - phi((threshold - predecessor_contrast) / spread)
    absent = 1 - phi(threshold / spread)
    return {
        "sigma_mesh": sigma_mesh,
        "contrast_sd": spread,
        "threshold": threshold,
        "reproduced_when_present": present,
        "reproduced_when_absent": absent,
        "both_slots_when_present": present**2,
        "both_slots_when_absent": absent**2,
        "exactly_one_slot_when_present": 2 * present * (1 - present),
        "exactly_one_slot_when_absent": 2 * absent * (1 - absent),
    }


def predecessor_record() -> dict[str, Any]:
    """The predecessor's retained C8 T readings and the within-class contrast the new case tests."""
    path = ROOT / PREDECESSOR_RUN / "analysis.json"
    data = path.read_bytes()
    readings = json.loads(data)["readings"]
    levels = {
        r["segment"]: r["a_prime"]
        for r in readings
        if r["arm"] == "T" and r["segment"] in ("c8-4", "c8-5", "c8-6", "c8-7")
    }
    ideals = {r["segment"]: r["ideal"] for r in readings if r["arm"] == "T" and r["segment"].startswith("c8-")}
    contrast = levels["c8-7"] - (levels["c8-4"] + levels["c8-5"] + levels["c8-6"]) / 3
    return {
        "run": PREDECESSOR_RUN,
        "analysis_sha256": sha256_bytes(data),
        "c8_t_normalized_levels": levels,
        "c8_t_ideal": ideals["c8-4"],
        "c8_t_deviations": {name: levels[name] - ideals[name] for name in levels},
        "c8_contrast": contrast,
    }


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
    coverage = check_coverage()
    classes = base.verify_classes()
    entries = sequence()
    check_sequence(entries)
    seconds = check_duration()
    tasks: list[Task] = [
        (
            position,
            design.name,
            orientation,
            seed_index(design),
            seeds[seed_index(design)],
            design.role,
            design.first[0],
            design.first[1],
            design.second[0],
            design.second[1],
            design.group,
        )
        for position, (design, orientation) in enumerate(entries)
    ]
    settings = ordered_map(build_iteration, tasks, min_items=1)
    mesh, _ = photonic_template(np.eye(ACTIVE, dtype=np.complex128))
    circuit = {**mesh, "modes": WIDTH, "input_state": [1] + [0] * (WIDTH - 1)}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    predecessor = predecessor_record()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [platform],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES * len(settings),
        "max_shots": SHOTS * len(settings),
        "max_duration": MAX_DURATION,
        "max_credits": MAX_CREDITS,
        "mitigations": [],
        "output_modes": WIDTH,
        "logical_modes": list(range(ACTIVE)),
        "eligibility": (
            "single detected photon; slot A modes 0..3, slot B modes 4..7, failure mode 8, sentinel modes 9..11"
        ),
        "expected_seconds": seconds,
        "seed_source": {
            "script": "scripts/ascella_pathion_coset_block_pairs.py",
            "flag": "--draw",
            "experiment": "ascella-pathion-coset-block-pairs",
            "sources": [f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}" for index in range(SEED_COUNT)],
            "usage": (
                "one compilation seed per distinct setting, in the order anchor, dark and the sign settings; both "
                "slot orientations of a setting and the anchor and dark requests at the mirror positions share it; "
                "the same seeds serve the simulator and hardware cases"
            ),
        },
        "analysis_sources": {
            name: sha256_bytes((ROOT / name).read_bytes())
            for name in (
                "scripts/ascella_pathion_coset_block_pairs.py",
                "scripts/ascella_pathion_four_term_blocks.py",
                "scripts/hypercomplex_cases.py",
                "scripts/qd_platform.py",
                "gororoba_quantum/cd_core.py",
            )
        },
        "operands": {
            name: {str(term): coefficient for term, coefficient in terms.items()}
            for name, terms in base.OPERANDS.items()
        },
        "blocks": {code: {"operand": operand, "ordinal": ordinal} for code, (operand, ordinal) in BLOCKS.items()},
        "block_classes": classes,
        "arm_coverage": coverage,
        "arms": {**base.ARM_MEANING, "D": base.ARM_MEANING["D"] + "; beside a bright partner it is the crosstalk null"},
        "designs": [
            {
                "name": design.name,
                "role": design.role,
                "group": design.group,
                "items": [list(design.first), list(design.second)],
                "seed_index": seed_index(design),
            }
            for design in DESIGNS
        ],
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "question": (
                "Does one photon shared by two coset blocks at one common scale read each block at its programmed "
                "level, with no crosstalk between the blocks, and does the predecessor's C8 spread (blocks 4, 5 and "
                "6 low, block 7 high) follow the block or the mode slot?"
            ),
            "inference": "descriptive against numeric thresholds; report all detected modes and event denominators",
            "levels": (
                "level of a slot = 2 x (clicks in its four modes) / (clicks in modes 0..8); the calibrated level "
                "divides each slot's dark-subtracted clicks by the slot's efficiency relative to the failure mode "
                "(from its anchor reading a, r = a / (2 - a)) before forming the same ratio; a' = (a - a_dark) / "
                "(a_anchor - a_dark) with the slot's own anchor and dark is reported beside it"
            ),
            "thresholds": THRESHOLDS,
            "decisions": DECISIONS,
            "slot_modes": {slot: list(modes) for slot, modes in SLOT_MODES.items()},
            "failure_mode": FAILURE_MODE,
            "sentinel_modes": list(SENTINEL_MODES),
            "independence_groups": list(INDEPENDENCE_GROUPS),
            "same_class_pairs": [list(pair) for pair in SAME_CLASS_PAIRS],
            "predecessor": predecessor,
            "binomial_standard_error": standard_errors(),
            "contrast_power": [contrast_power(predecessor["c8_contrast"], s) for s in (0.0, 0.005, 0.01, 0.02)],
            "boundary": (
                "Conformance of programmed operator blocks to their interference law on one 12-mode mesh with two "
                "blocks per photon; the client computes every cd_core sign, so the chip does not compute the "
                "algebra, and sim:ascella is noiseless and checks the pipeline only."
            ),
        },
    }
    template_experiment(manifest, circuit)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def ideal_table() -> list[dict[str, Any]]:
    """Ideal level of every distinct block-arm item of the case."""
    rows = []
    for design in DESIGNS:
        for code, arm in (design.first, design.second):
            item = resolve(code, arm)
            rows.append(
                {"setting": design.name, "block": f"{item.operand}/{item.ordinal}", "arm": arm, "level": item.level}
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ideal", action="store_true", help="print the ideal levels, coverage and errors, no files")
    parser.add_argument("--power", action="store_true", help="print the C8 contrast power, no files")
    parser.add_argument("--draw", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--platform", choices=("sim:ascella", "qpu:ascella"))
    args = parser.parse_args()
    if args.ideal:
        check_sequence(sequence())
        summary = {
            "iterations": ITERATIONS,
            "expected_seconds": check_duration(),
            "coverage": check_coverage(),
            "standard_errors": standard_errors(),
            "levels": ideal_table(),
        }
        print(json.dumps(summary, indent=1))
        return 0
    if args.power:
        contrast = predecessor_record()["c8_contrast"]
        for sigma in (0.0, 0.005, 0.01, 0.02):
            print(json.dumps({k: round(v, 4) for k, v in contrast_power(contrast, sigma).items()}))
        return 0
    if args.draw is None or args.out is None or args.platform is None:
        parser.error("--draw, --out and --platform are required unless --ideal or --power is given")
    payload = documents(
        args.draw.resolve(), "simulator" if args.platform.startswith("sim:") else "hardware", args.platform
    )
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (args.out / name).write_bytes(data)
    print(f"{args.out}: {ITERATIONS} iterations; request sha256 {sha256_bytes(payload['cases.json'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
