"""Deterministic binary-label diagnostics for retained Tuna repeated readout."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from qi_tuna_qualification import FILES, ROOT, digest
from qi_tuna_qualification import replay as qualification_replay

sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna"
EARLY = (17, 18, 19)
FINAL = (4, 11, 6)
BLOCK_SIZE = 256


def joint_counts(first: NDArray[np.int64], second: NDArray[np.int64]) -> list[list[int]]:
    """Rows index the first binary label, columns the second label."""
    return np.bincount(2 * first + second, minlength=4).reshape(2, 2).tolist()


def arm_diagnostics(arguments: tuple[str, list[str], int]) -> dict[str, Any]:
    filename, shots, block_size = arguments
    if not shots or block_size < 1 or len(shots) % block_size:
        raise ValueError("positive whole blocks of shots are required")
    if any(type(shot) is not str or len(shot) != 20 or set(shot) - {"0", "1"} for shot in shots):
        raise ValueError("raw shots must be width-20 binary strings")
    bits = np.array([list(shot[::-1]) for shot in shots], dtype=np.int64)
    count = len(shots)
    ones = bits.sum(axis=0)
    both_one = bits.T @ bits
    block_bits = bits.reshape(-1, block_size, 20)
    repeated = []
    for early, final in zip(EARLY, FINAL, strict=True):
        joint = joint_counts(bits[:, early], bits[:, final])
        repeated.append(
            {
                "early_bit": early,
                "terminal_bit": final,
                "joint_counts": joint,
                "final_one_given_early_zero": [joint[0][1], sum(joint[0])],
                "final_one_given_early_one": [joint[1][1], sum(joint[1])],
                "disagreement_count": joint[0][1] + joint[1][0],
                "block_disagreement_counts": (block_bits[:, :, early] != block_bits[:, :, final]).sum(axis=1).tolist(),
            }
        )
    lag_rows = []
    for lag in (1, 2, 4, 8, 16, 32, 64):
        if lag >= count:
            continue
        first = bits[:-lag]
        second = bits[lag:]
        pair_count = count - lag
        first_ones = first.sum(axis=0)
        second_ones = second.sum(axis=0)
        paired_ones = (first * second).sum(axis=0)
        lag_rows.append(
            {
                "lag_shots": lag,
                "pairs": pair_count,
                "first_one_counts": first_ones.tolist(),
                "second_one_counts": second_ones.tolist(),
                "both_one_counts": paired_ones.tolist(),
                "covariance_numerators": (pair_count * paired_ones - first_ones * second_ones).tolist(),
                "covariance_denominator": pair_count * pair_count,
            }
        )
    return {
        "file": filename,
        "shots": count,
        "one_counts_by_classical_bit": ones.tolist(),
        "block_size": block_size,
        "block_one_counts_by_classical_bit": block_bits.sum(axis=1).tolist(),
        "early_final": repeated,
        "lag_statistics": lag_rows,
        "within_shot_both_one_counts": both_one.tolist(),
        "within_shot_covariance_numerators": (count * both_one - np.outer(ones, ones)).tolist(),
        "within_shot_covariance_denominator": count * count,
        "early_to_terminal_disagreements": (bits[:, EARLY, None] != bits[:, None, FINAL]).sum(axis=0).tolist(),
    }


def label_reassignment(arguments: tuple[tuple[int, ...], tuple[int, ...], list[dict[str, Any]]]) -> dict[str, Any]:
    permutation, flips, arms = arguments
    zero, one = arms[:2]
    contrasts = [
        (1 - 2 * flips[target])
        * (one["one_counts_by_classical_bit"][EARLY[source]] - zero["one_counts_by_classical_bit"][EARLY[source]])
        for target, source in enumerate(permutation)
    ]
    mismatches = [
        [
            arm["shots"] - arm["early_to_terminal_disagreements"][source][target]
            if flips[target]
            else arm["early_to_terminal_disagreements"][source][target]
            for target, source in enumerate(permutation)
        ]
        for arm in arms
    ]
    shots = zero["shots"]
    return {
        "source_early_bits_for_q4_q11_q6": [EARLY[source] for source in permutation],
        "invert_for_q4_q11_q6": list(flips),
        "contrast_numerators": contrasts,
        "minimum_contrast_numerator": min(contrasts),
        "contrast_denominator": shots,
        "disagreement_counts_by_arm": mismatches,
        "maximum_disagreement_count": max(max(row) for row in mismatches),
        "assignment_threshold_passes": all(2 * value >= shots for value in contrasts),
        "disagreement_threshold_passes": all(10 * value <= shots for row in mismatches for value in row),
    }


def summarize(arms: list[dict[str, Any]]) -> dict[str, Any]:
    if [arm["file"] for arm in arms] != list(FILES) or len({arm["shots"] for arm in arms}) != 1:
        raise ValueError("three equal-shot arms in zero, one, geometry order are required")
    zero, one = arms[:2]
    differences = np.array(one["block_one_counts_by_classical_bit"]) - np.array(
        zero["block_one_counts_by_classical_bit"]
    )
    candidates = ordered_map(
        label_reassignment,
        [
            (permutation, flips, arms)
            for permutation in itertools.permutations(range(3))
            for flips in itertools.product((0, 1), repeat=3)
        ],
    )
    return {
        "contrast_numerators_by_classical_bit": [
            right - left
            for left, right in zip(zero["one_counts_by_classical_bit"], one["one_counts_by_classical_bit"], strict=True)
        ],
        "contrast_denominator": zero["shots"],
        "block_contrast_numerators_by_classical_bit": differences.tolist(),
        "block_contrast_denominator": zero["block_size"],
        "block_contrast_minimum_numerators": differences.min(axis=0).tolist(),
        "block_contrast_maximum_numerators": differences.max(axis=0).tolist(),
        "block_pairing_boundary": "Equal-index blocks belong to separate jobs rather than paired measurements.",
        "signed_permutation_candidates": candidates,
        "signed_permutation_count": len(candidates),
        "any_signed_permutation_passes_assignment": any(row["assignment_threshold_passes"] for row in candidates),
        "any_signed_permutation_passes_disagreement": any(row["disagreement_threshold_passes"] for row in candidates),
        "best_minimum_contrast_numerator": max(row["minimum_contrast_numerator"] for row in candidates),
        "best_maximum_disagreement_count": min(row["maximum_disagreement_count"] for row in candidates),
    }


def audit(run: Path = RUN) -> dict[str, Any]:
    qualification = qualification_replay(run)
    arms = ordered_map(
        arm_diagnostics,
        [(filename, json.loads((run / "raw" / f"{filename}.json").read_text()), BLOCK_SIZE) for filename in FILES],
    )
    sources = [Path(__file__), ROOT / "scripts/qi_tuna_qualification.py", ROOT / "gororoba_quantum/parallel.py"]
    return {
        "schema": "qi-tuna-binary-readout-diagnostics-v1",
        "arms": arms,
        "comparison": summarize(arms),
        "frozen_qualification_passed": qualification["passed"],
        "inputs_relative_to_run": qualification["inputs"],
        "source_sha256": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
        "interpretation": [
            "Bits are provider-reported thresholded measurement labels, not independently calibrated populations.",
            "The retained API records contain neither IQ samples nor discriminator thresholds.",
            "Joint counts cannot separate assignment, preparation, dynamics and acquisition defects.",
            "Covariances and contiguous blocks are descriptive; no IID, significance or stationarity claim follows.",
            "Signed permutations test only fixed relabeling of the three early bits, not arbitrary packing corruption.",
            "All counts retain the frozen qualification decision; post-hoc relabeling cannot approve acquisition.",
        ],
        "array_conventions": {
            "bits": "Indices ascend b0 through b19; raw b0 is rightmost.",
            "joint": "Rows early label 0,1; columns terminal label 0,1.",
            "conditional": "Each conditional is [one-count, conditioning-count]; zero denominator means undefined.",
            "covariance": "Numerator divided by stated denominator is the empirical centered product mean.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=RUN)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json.dumps(audit(arguments.run), indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("retained readout diagnostics differ from replay")
        print("Tuna readout diagnostics: byte-exact replay matches")
    else:
        with arguments.out.open("x") as destination:
            destination.write(content)


if __name__ == "__main__":
    main()
