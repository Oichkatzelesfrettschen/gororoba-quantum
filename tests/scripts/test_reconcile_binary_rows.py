"""scripts/reconcile_qpu_inventory.py: the joined-text register check accepts exactly what a per-shot match does."""

from __future__ import annotations

import itertools
import re

import pytest
import reconcile_qpu_inventory as reconcile


def _per_shot(bits: list[str], width: int) -> bool:
    return all(re.fullmatch(r"[01]+", value) and len(value) == width for value in bits)


@pytest.mark.parametrize(
    ("bits", "width"),
    [
        (["01", "10"], 2),
        (["01", "1"], 2),
        (["012", "101"], 3),
        (["0 1", "101"], 3),
        (["01\n", "101"], 3),
        (["", ""], 0),
        (["0110"], 4),
        (["0110"], 3),
        (["01", "10"], 1),
    ],
)
def test_binary_rows_matches_the_per_shot_rule(bits: list[str], width: int) -> None:
    if width > 0 and reconcile.binary_rows(bits, width) != _per_shot(bits, width):
        raise AssertionError(f"{bits} at width {width}")


def test_binary_rows_matches_every_short_register_over_a_mixed_alphabet() -> None:
    for width in (1, 2, 3):
        words = ["".join(chars) for length in range(width + 2) for chars in itertools.product("01x", repeat=length)]
        for pair in itertools.product(words, repeat=2):
            bits = list(pair)
            if reconcile.binary_rows(bits, width) != _per_shot(bits, width):
                raise AssertionError(f"{bits} at width {width}")
