"""Exact selected-array model for the memory-bounded W8 N=19 route."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, cast

PRODUCER = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/memory-bounded/w8_n19_memory_model.py"
SPEC = importlib.util.spec_from_file_location("a5_w8_memory_model_test", PRODUCER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {PRODUCER}")
memory_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory_model)


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_stage_bounds_fit_16_gib_but_full_operator_does_not() -> None:
    record = cast(dict[str, Any], memory_model.model())
    derived = cast(dict[str, int], record["derived"])
    stages = cast(dict[str, int], record["stage_peaks"])
    _check(derived["maximum_block_size_upper_bound"] == 59_123)
    _check(derived["maximum_adjacent_degree_rows"] == 78_674)
    _check(derived["full_uint16_generator_operator_bytes"] > 16 * 2**30)
    _check(stages["selected_array_peak_bytes"] == 13_041_282_092)
    _check(stages["selected_array_headroom_at_16_gib_bytes"] == 4_138_587_092)
