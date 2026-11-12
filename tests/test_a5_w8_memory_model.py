"""Selected-array model for the memory-bounded W8 N=19 route."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, cast

import modular_echelon_compact as mec

ROOT = Path(__file__).parents[1]
EVIDENCE = ROOT / "docs/evidence/a5-exceptional-fibers"
PRODUCER = EVIDENCE / "memory-bounded/w8_n19_memory_model.py"
SPEC = importlib.util.spec_from_file_location("a5_w8_memory_model_test", PRODUCER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {PRODUCER}")
memory_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory_model)

ENGINE = EVIDENCE / "replay/engine/fiber_rank_v14.py"


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
    _check(stages["products_selected_arrays_bytes"] == 13_199_590_444)
    _check(stages["closure_selected_arrays_bytes"] == 11_183_722_492)
    _check(stages["selected_array_peak_bytes"] == 13_199_590_444)
    _check(stages["selected_array_headroom_at_16_gib_bytes"] == 3_980_278_740)
    _check(derived["max_prefix_rows_that_fit"] == 6_732)


def test_retained_json_is_the_regenerated_model() -> None:
    retained = json.loads((EVIDENCE / "memory-bounded/w8-n19-memory-model.json").read_text())
    _check(retained == memory_model.model())


def test_known_prefix_peak_adds_ten_bytes_per_element_to_the_products_stage() -> None:
    base = cast(dict[str, Any], memory_model.model())
    known = cast(dict[str, Any], memory_model.model(prefix_peak_rows=1_000))
    block = base["derived"]["maximum_block_size_upper_bound"]
    gain = (
        known["stage_peaks"]["products_selected_arrays_bytes"] - base["stage_peaks"]["products_selected_arrays_bytes"]
    )
    _check(gain == 10 * 1_000 * block)
    _check(known["streamed_loop_arrays_status"] == "included")
    # At the largest count that fits, one more row leaves the 16 GiB limit.
    fit = base["derived"]["max_prefix_rows_that_fit"]
    limit = 16 * 2**30
    at = memory_model.model(prefix_peak_rows=fit)["stage_peaks"]["products_selected_arrays_bytes"]
    over = memory_model.model(prefix_peak_rows=fit + 1)["stage_peaks"]["products_selected_arrays_bytes"]
    _check(at <= limit < over)


def test_model_transient_terms_equal_the_code_that_defines_them() -> None:
    spec = importlib.util.spec_from_file_location("a5_w8_memory_model_engine", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {ENGINE}")
    engine = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = engine
    spec.loader.exec_module(engine)
    _check(memory_model.COMPACT_COLS == mec.COMPACT_COLS and memory_model.COMPACT_INNER == mec.COMPACT_INNER)
    for block, chunk in ((59_123, 64), (1_000, 7), (10, 1)):
        _check(memory_model.insert_panel_bytes(block, chunk) == mec.insert_panel_bytes(block, chunk))
        _check(memory_model.streamed_chunk_bytes(chunk, block) == engine.streamed_chunk_bytes(chunk, block))
