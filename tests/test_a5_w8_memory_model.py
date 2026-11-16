"""Selected-array model for the memory-bounded W8 N=19 route."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, cast

import pytest

import modular_echelon_compact as mec

ROOT = Path(__file__).parents[1]
EVIDENCE = ROOT / "docs/evidence/a5-exceptional-fibers"
PRODUCER = EVIDENCE / "memory-bounded/w8_n19_memory_model.py"
SPEC = importlib.util.spec_from_file_location("a5_w8_memory_model_test", PRODUCER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {PRODUCER}")
memory_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory_model)

ENGINE = EVIDENCE / "replay/engine/fiber_rank_v15.py"


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_stage_bounds_fit_16_gib_but_full_operator_does_not() -> None:
    record = cast(dict[str, Any], memory_model.model())
    derived = cast(dict[str, int], record["derived"])
    stages = cast(dict[str, int], record["stage_peaks"])
    _check(record["schema"] == "a5-w8-n19-memory-model-v2")
    _check(record["inputs"]["engine"] == "fiber_rank_v15.py")
    _check(record["inputs"]["uint16_product_row_copies"] == 3)
    _check(derived["uint16_product_rows_bytes"] == 5_607_594_432)
    _check(derived["maximum_block_size_upper_bound"] == 59_123)
    _check(derived["maximum_adjacent_degree_rows"] == 78_674)
    _check(derived["full_uint16_generator_operator_bytes"] > 16 * 2**30)
    _check(stages["products_selected_arrays_bytes"] == 15_068_788_588)
    _check(stages["closure_selected_arrays_bytes"] == 13_052_920_636)
    _check(stages["selected_array_peak_bytes"] == 15_068_788_588)
    _check(stages["selected_array_headroom_at_16_gib_bytes"] == 2_111_080_596)
    _check(derived["max_prefix_rows_that_fit"] == 3_570)


@pytest.mark.parametrize("altered", [False, True])
def test_model_check_rejects_changed_selected_array_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, altered: bool
) -> None:
    record = memory_model.model()
    if altered:
        record["stage_peaks"]["selected_array_peak_bytes"] += 1
    destination = tmp_path / "model.json"
    destination.write_text(json.dumps(record, indent=1) + "\n")
    monkeypatch.setattr(sys, "argv", [str(PRODUCER), "--check", str(destination)])
    if altered:
        with pytest.raises(SystemExit, match="model differs"):
            memory_model.main()
    else:
        memory_model.main()


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
