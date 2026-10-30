"""Replay a posthoc control-response mixture sensitivity analysis of Tuna raw shots.

The fitted segment coordinate is not a population estimate without transferable
control-response assumptions. It neither repairs qualification nor identifies a
physical mechanism, assignment channel, shot independence, or context transfer.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from qi_tuna_qualification import FILES, SHOTS, digest
from qi_tuna_qualification import replay as qualification_replay

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna"
QUBITS = (4, 11, 6)
EARLY_BITS = (17, 18, 19)
CELL_ORDER = ("00", "01", "10", "11")


def rational(value: Fraction | None) -> dict[str, Any] | None:
    """Retain exact arithmetic and a deterministic twelve-place display string."""
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 50
        decimal = format(Decimal(value.numerator) / Decimal(value.denominator), ".12f")
    return {"numerator": value.numerator, "denominator": value.denominator, "decimal": decimal}


def probabilities(counts: list[int]) -> list[Fraction]:
    if len(counts) != 4 or any(type(count) is not int or count < 0 for count in counts) or sum(counts) == 0:
        raise ValueError("joint counts require four nonnegative integers with positive total")
    total = sum(counts)
    return [Fraction(count, total) for count in counts]


def residual(observed: list[Fraction], predicted: list[Fraction]) -> dict[str, Any]:
    differences = [actual - expected for actual, expected in zip(observed, predicted, strict=True)]
    return {
        "signed_cell_residuals": [rational(value) for value in differences],
        "total_variation": rational(sum(map(abs, differences), Fraction(0)) / 2),
        "max_cell_absolute_residual": rational(max(map(abs, differences))),
        "squared_l2_residual": rational(sum((value * value for value in differences), Fraction(0))),
    }


def fit_response(zero_counts: list[int], one_counts: list[int], geometry_counts: list[int]) -> dict[str, Any]:
    """Project the empirical geometry table onto the empirical control segment."""
    zero, one, geometry = map(probabilities, (zero_counts, one_counts, geometry_counts))
    direction = [high - low for low, high in zip(zero, one, strict=True)]
    offset = [observed - low for low, observed in zip(zero, geometry, strict=True)]
    denominator = sum((value * value for value in direction), Fraction(0))
    numerator = sum((left * right for left, right in zip(offset, direction, strict=True)), Fraction(0))
    unconstrained = numerator / denominator if denominator else None
    fitted = min(Fraction(1), max(Fraction(0), unconstrained)) if unconstrained is not None else None
    predicted = [low + (fitted or Fraction(0)) * delta for low, delta in zip(zero, direction, strict=True)]
    half = [(low + high) / 2 for low, high in zip(zero, one, strict=True)]
    marginal_weights = {}
    for name, selected in (("early", (2, 3)), ("terminal", (1, 3))):
        low = sum((zero[index] for index in selected), Fraction(0))
        high = sum((one[index] for index in selected), Fraction(0))
        observed = sum((geometry[index] for index in selected), Fraction(0))
        marginal_weights[name] = {
            "zero_control_one_rate": rational(low),
            "one_control_one_rate": rational(high),
            "geometry_one_rate": rational(observed),
            "control_contrast": rational(high - low),
            "affine_weight_unclipped": rational((observed - low) / (high - low)) if high != low else None,
            "status": "defined" if high != low else "undefined_zero_control_contrast",
        }
    return {
        "counts": {"prepared_zero": zero_counts, "prepared_one": one_counts, "geometry": geometry_counts},
        "probabilities": {
            "prepared_zero": [rational(value) for value in zero],
            "prepared_one": [rational(value) for value in one],
            "geometry": [rational(value) for value in geometry],
        },
        "projection_numerator": rational(numerator),
        "projection_denominator": rational(denominator),
        "unconstrained_segment_coordinate": rational(unconstrained),
        "fitted_segment_coordinate": rational(fitted),
        "fit_status": "unique_segment_projection" if denominator else "unidentified_identical_control_tables",
        "clipped_to_segment": fitted != unconstrained,
        "fitted_joint_probabilities": [rational(value) for value in predicted],
        "fitted_residual": residual(geometry, predicted),
        "half_mixture_joint_probabilities": [rational(value) for value in half],
        "half_mixture_residual": residual(geometry, half),
        "marginal_affine_weights": marginal_weights,
    }


def joint_tables(shot_groups: list[list[str]]) -> list[list[list[int]]]:
    """Count all three arms and ancillas together; cells encode early then terminal."""
    if len(shot_groups) != 3 or any(len(shots) != SHOTS for shots in shot_groups):
        raise ValueError("joint tables require three arms of 4096 shots")
    if any(type(shot) is not str or len(shot) != 20 for shots in shot_groups for shot in shots):
        raise ValueError("joint tables require width-20 strings")
    encoded = "".join("".join(shots) for shots in shot_groups).encode("ascii")
    bits = np.frombuffer(encoded, dtype=np.uint8).reshape(3, SHOTS, 20)
    if np.any((bits != ord("0")) & (bits != ord("1"))):
        raise ValueError("joint tables require binary strings")
    bits = bits - ord("0")
    early = bits[:, :, [19 - bit for bit in EARLY_BITS]]
    terminal = bits[:, :, [19 - qubit for qubit in QUBITS]]
    cells = 2 * early + terminal
    counts = (cells[:, :, :, None] == np.arange(4)).sum(axis=1)
    return counts.tolist()


def fit_qubit(arguments: tuple[int, int, list[int], list[int], list[int]]) -> dict[str, Any]:
    qubit, early_bit, zero, one, geometry = arguments
    return {
        "physical_qubit": qubit,
        "early_classical_bit": early_bit,
        "terminal_classical_bit": qubit,
        **fit_response(zero, one, geometry),
    }


def replay(run: Path = RUN) -> dict[str, Any]:
    qualification = qualification_replay(run)
    retained_qualification = json.loads((run / "qualification.json").read_text())
    if qualification != retained_qualification:
        raise ValueError("frozen qualification differs from its replay")
    groups = [json.loads((run / "raw" / f"{name}.json").read_text()) for name in FILES]
    tables = joint_tables(groups)
    arguments = [
        (qubit, early_bit, tables[0][index], tables[1][index], tables[2][index])
        for index, (qubit, early_bit) in enumerate(zip(QUBITS, EARLY_BITS, strict=True))
    ]
    extra_inputs = ("qualification.json", "approval.json", "backend.json", "live-admission.json")
    return {
        "schema": "qi-tuna-readout-response-mixture-v1",
        "analysis_class": "POSTHOC sensitivity analysis; empirical control-response segment fit",
        "interpretation": (
            "The fitted parameter is a segment coordinate, not an identified population. Small descriptive residuals "
            "do not establish context transfer, shot independence, a physical mechanism, or qualification. "
            "Prepared-zero and prepared-one controls differ on all spectators; geometry includes gates and B-plus "
            "preparation. Interpreting the coordinate as population requires additional unverified response-transfer "
            "assumptions. This analysis cannot repair or replace the frozen qualification verdict."
        ),
        "arithmetic": "Exact Fraction arithmetic; twelve-place Decimal strings are display values only",
        "fit_rule": "L2 projection onto zero-to-one empirical response line, clipped to the closed interval [0,1]",
        "residual_rule": "TV is one half the sum of absolute differences of normalized four-cell tables",
        "cell_order": list(CELL_ORDER),
        "cell_bit_order": "early outcome first, terminal outcome second",
        "shots_per_arm": SHOTS,
        "frozen_qualification_passed": qualification["passed"],
        "statistical_boundary": (
            "Descriptive fitted residuals only; no uncertainty intervals, IID claim, or test verdict"
        ),
        "inputs": qualification["inputs"] | {name: digest(run / name) for name in extra_inputs},
        "producer_sha256": digest(Path(__file__)),
        "qualification_validator_sha256": digest(ROOT / "scripts/qi_tuna_qualification.py"),
        "qubits": ordered_map(fit_qubit, arguments, min_items=1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?", default=RUN)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    content = json.dumps(replay(args.run), indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.check.read_bytes() != content.encode("utf-8"):
            raise SystemExit("retained response-mixture analysis differs from replay")
        print("posthoc response-mixture sensitivity matches; frozen qualification verdict is unchanged")
    else:
        with args.out.open("x", encoding="utf-8") as output:
            output.write(content)


if __name__ == "__main__":
    main()
