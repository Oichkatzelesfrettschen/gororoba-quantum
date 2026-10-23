"""Exact paired assignment test for integer joint-score differences.

The test conditions on the realized pairs and requires genuinely randomized arm
order, preserved execution identity, a sharp no-effect null and absence of
carryover/interference between assigned acquisitions. It does not turn serial
shots or simultaneous cells into independent experimental units.
"""

from __future__ import annotations

import operator
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel  # noqa: E402


def tail_count(task: tuple[tuple[int, ...], int, int]) -> int:
    differences, start, stop = task
    assignments = np.arange(start, stop, dtype=np.int64)[:, None]
    bits = (assignments >> np.arange(len(differences), dtype=np.int64)) & 1
    totals = (1 - 2 * bits) @ np.asarray(differences, dtype=np.int64)
    return int(np.count_nonzero(np.abs(totals) >= abs(sum(differences))))


def paired_pvalue(differences: Sequence[int]) -> Fraction:
    try:
        values = tuple(operator.index(value) for value in differences)
    except TypeError as error:
        raise ValueError("joint-score numerators must be integers") from error
    if not 1 <= len(values) <= 20 or any(isinstance(value, bool) for value in differences):
        raise ValueError("the exact test accepts between one and twenty integer pairs")
    if sum(abs(value) for value in values) > 2**62:
        raise ValueError("the integer assignment sum exceeds its safe arithmetic bound")
    denominator = 1 << len(values)
    tasks = [(values, start, min(start + 4096, denominator)) for start in range(0, denominator, 4096)]
    return Fraction(sum(parallel.ordered_map(tail_count, tasks)), denominator)
