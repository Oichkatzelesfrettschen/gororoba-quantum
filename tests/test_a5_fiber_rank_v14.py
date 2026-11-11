"""Memory-bounded products in fiber_rank_v14 agree with the retained dense-operator route."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ENGINE = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v14.py"
SPEC = importlib.util.spec_from_file_location("fiber_rank_v14_test", ENGINE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {ENGINE}")
v14 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = v14
SPEC.loader.exec_module(v14)

P = 32009


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_streamed_products_equal_dense_generator_operators() -> None:
    basis = [(0, 0), (1, 0), (0, 1), (1, 1)]
    index = {monomial: i for i, monomial in enumerate(basis)}
    tables = [
        [{(1, 0): 1}, {}, {(1, 1): 1}, {}],
        [{(0, 1): 1}, {(1, 1): 1}, {}, {}],
    ]
    lay = v14.block_tables(tables, index, np.zeros(len(basis), dtype=np.int64), [0, 0], [0])
    generators = np.array([[0, 1, 1, 0], [0, 0, 0, 1]], dtype=np.float64)
    chars = [0, 0]
    dense = v14.block_products(generators, chars, 0, v14.order_walk(basis, lay), lay, 3, P)
    streamed = v14.block_products_streamed(generators, chars, 0, v14.order_walk_levels(basis, lay), lay, 3, P, 2)
    cached = v14.block_products_compact_operator(generators, chars, 0, v14.order_walk_levels(basis, lay), lay, 3, P, 2)
    _check(dense.keys() == streamed.keys())
    for key in dense:
        _check(dense[key][0] == streamed[key][0])
        _check(np.array_equal(dense[key][1], streamed[key][1]))
        _check(np.array_equal(dense[key][1], cached[key][1]))


def test_streamed_products_respect_a_restricted_prefix_order_ideal() -> None:
    basis = [(0, 0), (1, 0), (0, 1), (1, 1)]
    index = {monomial: i for i, monomial in enumerate(basis)}
    tables = [
        [{(1, 0): 1}, {}, {(1, 1): 1}, {}],
        [{(0, 1): 1}, {(1, 1): 1}, {}, {}],
    ]
    lay = v14.block_tables(tables, index, np.zeros(len(basis), dtype=np.int64), [0, 0], [0])
    generators = np.array([[0, 1, 1, 0], [0, 0, 0, 1]], dtype=np.float64)
    wanted = {1: {(0,), (1,)}, 2: {(0, 0), (0, 1)}, 3: {(0, 0, 0), (0, 0, 1)}}
    dense = v14.block_products(generators, [0, 0], 0, v14.order_walk(basis, lay), lay, 3, P, wanted)
    streamed = v14.block_products_streamed(
        generators, [0, 0], 0, v14.order_walk_levels(basis, lay), lay, 3, P, 1, wanted
    )
    _check(dense.keys() == streamed.keys())
    for key in dense:
        _check(np.array_equal(dense[key][1], streamed[key][1]))


def test_sign_mask_parallel_map_preserves_the_known_group() -> None:
    x2_plus_y2 = {(2, 0): 1, (0, 2): 1}
    xy = {(1, 1): 1}
    _check(v14.sign_group([[x2_plus_y2], [xy]], 2, P) == [(0,), (1,), (0, 1)])


def test_compact_preflight_uses_stage_peaks() -> None:
    terms = {
        "streamed_operator_layers": 9,
        "uint16_product_rows": 4,
        "compact_echelon_ceiling": 7,
        "closure_chunk_temporaries": 1,
    }
    _check(v14.compact_stage_peaks(terms) == {"products": 13, "closure": 12})
