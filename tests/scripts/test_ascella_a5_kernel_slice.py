"""Check the optical isometry against direct A5 multiplication."""

from __future__ import annotations

import math

import ascella_a5_kernel_slice as case
import sympy as sym

import cd_core
from parallel import ordered_map


def check_setting(index: int) -> None:
    _, second, coefficient, preparation = case.SETTINGS[index]
    left = [0] * 32
    right = [0] * 32
    left[1], left[second] = 1, coefficient
    right[4], right[15] = 1, preparation
    direct = cd_core.cd_multiply_exact(32, left, right)
    operator = case.exact_operator(second, coefficient, preparation)
    for row, output_index in enumerate(case.OUTPUT_BASIS):
        if sym.simplify(operator[row, 0] - direct[output_index] / (2 * sym.sqrt(2))) != 0:
            raise AssertionError(f"optical success amplitude differs at setting {index}, mode {row}")
    success = sym.simplify(sum(operator[row, 0] ** 2 for row in range(4)))
    if success != case.EXPECTED[index] or not math.isfinite(float(success)):
        raise AssertionError("the target or sign mutation differs from the exact A5 prediction")


def test_every_optical_success_amplitude_matches_direct_a5_multiplication() -> None:
    ordered_map(check_setting, list(range(len(case.SETTINGS))), min_items=1)
