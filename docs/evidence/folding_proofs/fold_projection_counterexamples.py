"""Replay exact witnesses showing what fold-average projection discards."""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT / "gororoba_quantum"))

# The repository modules run as scripts and have no installable package.
from cd_core import cd_sign  # noqa: E402
from rank_charts import rank_certificate  # noqa: E402


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sparse(dimension: int, coefficients: dict[int, int]) -> tuple[Fraction, ...]:
    return tuple(Fraction(coefficients.get(index, 0)) for index in range(dimension))


def _multiply(left: Sequence[Fraction], right: Sequence[Fraction]) -> tuple[Fraction, ...]:
    dimension = len(left)
    if dimension < 1 or dimension & (dimension - 1) or len(right) != dimension:
        raise ValueError("multiplication requires equal positive power-of-two coordinate counts")
    result = [Fraction(0)] * dimension
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index ^ right_index] += left_value * right_value * cd_sign(dimension, left_index, right_index)
    return tuple(result)


def _fold(values: Sequence[Fraction]) -> tuple[Fraction, ...]:
    dimension = len(values)
    if dimension < 2 or dimension & (dimension - 1):
        raise ValueError("fold-average requires a power-of-two coordinate count of at least two")
    half = dimension // 2
    return tuple((values[index] + values[half + index]) / 2 for index in range(half))


def audit() -> dict[str, object]:
    left = _sparse(16, {3: 1, 10: 1})
    right = _sparse(16, {6: 1, 15: -1})
    product = _multiply(left, right)
    folded_product = _multiply(_fold(left), _fold(right))
    _require(all(value == 0 for value in product), "the declared sedenion pair fails zero-product verification")
    expected_folded_product = tuple(Fraction(1, 2) if index == 5 else Fraction(0) for index in range(8))
    _require(folded_product == expected_folded_product, "the folded product differs from e5/2")
    source_rank = rank_certificate(left).rank
    folded_rank = rank_certificate(_fold(left)).rank
    _require(source_rank == 12 and folded_rank == 8, "the certified source/folded ranks differ from 12/8")

    scalar_halves = _sparse(16, {0: 1, 9: 1})
    lower_norm = sum((value * value for value in scalar_halves[:8]), Fraction(0))
    upper_norm = sum((value * value for value in scalar_halves[8:]), Fraction(0))
    inner_product = sum(
        (lower * upper for lower, upper in zip(scalar_halves[:8], scalar_halves[8:], strict=True)), Fraction(0)
    )
    scalar_rank = rank_certificate(scalar_halves).rank
    _require(lower_norm == upper_norm == 1 and inner_product == 0, "the half-frame witness violates its premise")
    _require(scalar_rank == 16, "the scalar-half witness fails invertibility verification")
    return {
        "schema_version": 1,
        "arithmetic": "exact integers and fractions",
        "fold_average": {
            "left": {"3": "1", "10": "1"},
            "right": {"6": "1", "15": "-1"},
            "source_product": "zero",
            "source_left_rank": source_rank,
            "folded_left_rank": folded_rank,
            "folded_product": {str(index): str(value) for index, value in enumerate(folded_product) if value},
        },
        "equal_norm_orthogonal_halves": {
            "coordinates": {"0": "1", "9": "1"},
            "lower_norm_squared": str(lower_norm),
            "upper_norm_squared": str(upper_norm),
            "inner_product": str(inner_product),
            "left_rank": scalar_rank,
        },
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
