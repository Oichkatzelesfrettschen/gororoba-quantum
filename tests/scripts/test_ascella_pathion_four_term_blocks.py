"""Check the pathion-only four-term block case against direct A5 multiplication and the D = 16 class census."""

from __future__ import annotations

import math

import ascella_pathion_four_term_blocks as case
import numpy as np

from parallel import ordered_map


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_block(task: tuple[str, int]) -> None:
    name, ordinal = task
    block = case.operand_blocks(case.DIM, case.OPERANDS[name], name)[ordinal]
    case.check_against_cd_core(block, case.OPERANDS[name])


def test_every_block_column_matches_direct_cd_core_multiplication() -> None:
    tasks = [(name, ordinal) for name in case.OPERANDS for ordinal in range(8)]
    ordered_map(check_block, tasks, min_items=1)


def test_pathion_only_blocks_lie_in_classes_absent_at_dimension_16() -> None:
    result = case.verify_classes()
    counts = (result["classes_d16"], result["classes_d32"], result["classes_only_d32"])
    require(counts == (5, 9, 4), f"class counts {counts}")
    require(len(set(result["pathion_only_classes"].values())) == 3, "the pathion-only classes are not three")


def test_each_arm_has_its_ideal_level() -> None:
    for segment in case.SEGMENTS:
        block = case.operand_blocks(case.DIM, case.OPERANDS[segment.operand], segment.operand)[segment.ordinal]
        true = case.ideal_level(block.matrix, case.top_vector(block.matrix))
        for arm in sorted(set(segment.arms)):
            programmed, vector, _ = case.arm_program(block, arm)
            level = case.ideal_level(programmed, vector)
            if arm in ("F", "C", "N"):
                require(abs(level - true) >= case.SEPARATION, f"{segment.name} {arm}: separation {abs(level - true)}")
            elif arm == "D":
                require(math.isclose(level, 0, abs_tol=1e-12), f"{segment.name}: dark level {level}")
            elif arm in ("E0", "E1"):
                require(math.isclose(level, 0.25, abs_tol=1e-12), f"{segment.name} {arm}: null level {level}")


def test_top_levels_of_the_pathion_only_blocks_and_the_anchor() -> None:
    cases = (
        ("B12", (2, 3, 6, 7), 0.75),
        ("C8", (4, 5, 6, 7), (3 + math.sqrt(5)) / 8),
        ("A16", (4, 5, 6, 7), 1.0),
    )
    for name, ordinals, level in cases:
        for ordinal in ordinals:
            block = case.operand_blocks(case.DIM, case.OPERANDS[name], name)[ordinal]
            top = case.ideal_level(block.matrix, case.top_vector(block.matrix))
            require(math.isclose(top, level, abs_tol=1e-12), f"{name} block {ordinal}: top level {top}")


def test_slos_law_equals_the_analytic_block_law_for_each_arm_kind() -> None:
    tasks = [
        (0, "A16", 4, 0, "T", 0, 0),
        (1, "B12", 2, 1, "N", 0, 1),
        (2, "B12", 6, 2, "C", 0, 2),
        (3, "C8", 4, 3, "F", 0, 3),
        (4, "C8", 5, 4, "D", 0, 4),
        (5, "B12", 2, 5, "E1", 0, 5),
    ]
    for setting in ordered_map(case.build_setting, tasks, min_items=1):
        law = np.array(setting["ideal_label_law"])
        column = np.array([complex(re, im) for re, im in setting["column"]])
        require(float(np.max(np.abs(law - np.abs(column[:8]) ** 2))) < 1e-9, f"{setting['name']}: law differs")
        require(math.isclose(float(law[:4].sum()), setting["ideal_success"], abs_tol=1e-9), "success level differs")


def test_job_fits_the_packing_margin() -> None:
    require(case.ITERATIONS == 88, f"{case.ITERATIONS} iterations")
    require(case.check_duration() == 264.0, "expected seconds")


def test_decision_chain_passes_at_small_mesh_spread_and_degrades_monotonically() -> None:
    powers = [case.decision_chain_power(sigma) for sigma in (0.005, 0.01, 0.02, 0.03, 0.04)]
    require(powers[1]["all"] > 0.99, f"power at 0.01: {powers[1]['all']}")
    require(all(low["all"] >= high["all"] for low, high in zip(powers, powers[1:], strict=False)), "power rises")
    require(powers[-1]["all"] < 0.5, f"power at 0.04: {powers[-1]['all']}")
