# ruff: noqa: S101
"""Memory-bounded products in fiber_rank_v14 agree with the retained dense-operator route."""

from __future__ import annotations

import contextlib
import importlib.util
import inspect
import io
import json
import math
import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ENGINE_DIR = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine"


def _load(version: int) -> Any:
    path = ENGINE_DIR / f"fiber_rank_v{version}.py"
    spec = importlib.util.spec_from_file_location(f"fiber_rank_v{version}_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v14 = _load(14)
v13 = _load(13)

P = 32009
SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")
# Four character blocks, three generators of mixed degree; the closure needs four rounds at degree 2, order 7.
MIXED = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^4-t2^4,t3^3-t1^2*t2^2;\nideal G=t1+t2,t1-t2,t3^2;\n"


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


def test_sign_mask_checks_run_in_the_process_pool(monkeypatch: pytest.MonkeyPatch, forced_pool: Any) -> None:
    """The engine module imported by its own name is picklable into spawned workers; `forced_pool` reports two
    workers and records that `parallel.ordered_map` mapped every mask check."""
    monkeypatch.syspath_prepend(str(ENGINE_DIR))
    monkeypatch.delitem(sys.modules, "fiber_rank_v14", raising=False)
    engine = importlib.import_module("fiber_rank_v14")
    x2_plus_y2 = {(2, 0): 1, (0, 2): 1}
    xy = {(1, 1): 1}
    _check(engine.sign_group([[x2_plus_y2], [xy]], 2, P) == [(0,), (1,), (0, 1)])
    _check(forced_pool.maps == [("SignMaskCheck", 3)])
    _check(forced_pool.pools == [2])


def test_compact_preflight_uses_stage_peaks() -> None:
    terms = {
        "streamed_operator_layers": 9,
        "uint16_product_rows": 4,
        "compact_echelon_ceiling": 7,
        "closure_chunk_temporaries": 1,
    }
    _check(v14.compact_stage_peaks(terms) == {"products": 13, "closure": 12})
    terms |= {"streamed_loop_arrays": 20, "streamed_chunk_temporaries": 30, "compact_insert_panels": 100}
    _check(v14.compact_stage_peaks(terms) == {"products": 63, "closure": 112})
    cached = {"uint16_generator_operator": 9, "uint16_product_rows": 4, "compact_echelon_ceiling": 7}
    cached |= {"closure_chunk_temporaries": 1, "tiled_product_temporaries": 5}
    _check(v14.compact_stage_peaks(cached) == {"products": 18, "closure": 12})


def test_streamed_prefix_peak_counts_the_rows_of_the_largest_generator_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """The observed row count of every `streamed_generator_product` call never exceeds, and here equals, the bound."""
    basis = [(0, 0), (1, 0), (0, 1), (1, 1)]
    index = {monomial: i for i, monomial in enumerate(basis)}
    tables = [
        [{(1, 0): 1}, {}, {(1, 1): 1}, {}],
        [{(0, 1): 1}, {(1, 1): 1}, {}, {}],
    ]
    lay = v14.block_tables(tables, index, np.zeros(len(basis), dtype=np.int64), [0, 0], [0])
    generators = np.array([[0, 1, 1, 0], [0, 0, 0, 1], [0, 1, 0, 1]], dtype=np.float64)
    seen: list[int] = []
    real = v14.streamed_generator_product

    def spy(inputs: dict[int, np.ndarray], *args: Any) -> dict[int, np.ndarray]:
        seen.append(sum(len(rows) for rows in inputs.values()))
        return real(inputs, *args)

    monkeypatch.setattr(v14, "streamed_generator_product", spy)
    levels = v14.order_walk_levels(basis, lay)
    wanted = {1: {(0,), (1,), (2,)}, 2: {(0, 0), (0, 1), (1, 1), (0, 2)}, 3: {(0, 0, 0), (0, 0, 1), (0, 1, 2)}}
    for subset in (None, wanted):
        seen.clear()
        v14.block_products_streamed(generators, [0, 0, 0], 0, levels, lay, 3, P, 2, subset)
        _check(max(seen) == v14.streamed_prefix_peak(3, 3, subset))
    _check(v14.streamed_prefix_peak(3, 3, None) == 6)
    _check(v14.streamed_prefix_peak(1, 5, None) == 0)


def test_streamed_loop_and_chunk_terms_follow_the_accumulate_line() -> None:
    """Contribution (2 bytes) plus two uint32 temporaries (8 bytes) per prefix row element."""
    _check(v14.streamed_loop_bytes(5, 1000) == 10 * 5 * 1000)
    _check(v14.tiled_product_bytes(64) == 8 * (64 * 4096 + 4096 * 1024 + 3 * 64 * 1024))
    _check(v14.streamed_chunk_bytes(64, 1000) == 4 * 8 * 64 * 1000 + v14.tiled_product_bytes(64))


def _next_prime(n: int) -> int:
    while not v14.is_odd_prime(n):
        n += 1
    return n


def _exact_product(left: np.ndarray, right: np.ndarray, p: int) -> np.ndarray:
    return ((left.astype(np.int64) @ right.astype(np.int64)) % p).astype(np.uint16)


def _fixed_residues(rows: int, cols: int, salt: int) -> np.ndarray:
    """Deterministic residues spread over [0, P) without a random generator."""
    index = np.arange(rows * cols, dtype=np.int64).reshape(rows, cols)
    return ((index * 40503 + salt * 7919 + index // 3 * 104729) % P).astype(np.uint16)


@pytest.mark.parametrize(("inner", "inner_tile"), [(4100, 4096), (20, 3)])
def test_tiled_product_accumulates_every_inner_tile(inner: int, inner_tile: int) -> None:
    """The default tile leaves a 4-term remainder tile at inner 4,100; width 3 leaves seven tiles at inner 20."""
    left, right = _fixed_residues(5, inner, 1), _fixed_residues(inner, 4, 2)
    got = v14.tiled_mod_product(left, right, P, 2, 3, inner_tile)
    assert np.array_equal(got, _exact_product(left, right, P))


def test_default_tile_width_is_exact_for_every_accepted_prime() -> None:
    tile = inspect.signature(v14.tiled_mod_product).parameters["inner_tile"].default
    assert v14.modular_matmul_exact_bound(tile, v14.PMAX - 1)


def test_tiled_product_refuses_a_prime_that_breaks_float64_exactness() -> None:
    p = _next_prime(1_482_912)
    assert 4096 * (1_482_911 - 1) ** 2 < 2**53 <= 4096 * (p - 1) ** 2
    left = np.zeros((1, 4096), dtype=np.uint16)
    with pytest.raises(RuntimeError, match="exact float64 range"):
        v14.tiled_mod_product(left, left.T.copy(), p, 1)


def test_tiled_product_refuses_a_prime_outside_the_uint16_range() -> None:
    p = _next_prime(v14.PMAX)
    left = np.ones((1, 4), dtype=np.uint16)
    with pytest.raises(ValueError, match="uint16"):
        v14.tiled_mod_product(left, left.T.copy(), p, 1)
    largest = 32749
    assert v14.is_odd_prime(largest) and largest < v14.PMAX
    assert np.array_equal(v14.tiled_mod_product(left, left.T.copy(), largest, 1), np.array([[4]], dtype=np.uint16))


@pytest.mark.parametrize("extra", [["--stream-products"], ["--echelon", "compact"]])
def test_engine_rejects_a_prime_the_uint16_routes_cannot_hold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, extra: list[str]
) -> None:
    p = _next_prime(v14.PMAX)
    header = tmp_path / "h.sing"
    header.write_text(f"ring r={p},(t1),dp;\nideal J=t1^2;\nideal G=t1;\n")
    monkeypatch.setattr(sys, "argv", ["v14", str(header), "1", "4", "--quotient", *extra])
    with pytest.raises(SystemExit, match="need an odd prime below"):
        v14.main()


# Generators of x^a y^b with x odd: the first and third are odd in x, the second even. The product generators keep a
# constant term and a degree-3 tail; the closure generators lie in the maximal ideal.
PRODUCT_GENERATORS = (
    {(1, 0): 1, (1, 2): P - 1, (3, 0): 5},
    {(0, 0): 1, (0, 1): 17, (2, 0): 1, (0, 2): 3},
    {(1, 1): 1, (1, 2): 32000, (3, 0): 2},
)
CLOSURE_GENERATORS = (PRODUCT_GENERATORS[0], {(0, 1): 17, (2, 0): 1, (0, 2): 3}, PRODUCT_GENERATORS[2])


ROUTES = (
    ("streamed", ["--stream-products", "--echelon", "compact", "--chunk", "3"]),
    ("cached", ["--stream-products", "--echelon", "compact", "--chunk", "5", "--operator-cache-gb", "1"]),
    ("flint", ["--stream-products", "--chunk", "4"]),
)


def _truncated_monomial_cell(order: int) -> tuple[list, list]:
    """Monomials x^a y^b below total degree `order` and the multiplication tables of x and y on them."""
    basis = [(a, deg - a) for deg in range(order) for a in range(deg, -1, -1)]
    tables = [[{(a + (k == 0), b + (k == 1)): 1} if a + b + 1 < order else {} for a, b in basis] for k in range(2)]
    return basis, tables


def test_products_cross_character_blocks_like_engine_v13() -> None:
    """Block = parity of the x exponent, so x moves a parent row across blocks and y keeps it; a degree-3 tail and a
    constant term make every degree layer of the operator walk contribute."""
    basis, tables = _truncated_monomial_cell(4)
    index = {monomial: i for i, monomial in enumerate(basis)}
    generators = np.zeros((3, len(basis)))
    for f, terms in enumerate(PRODUCT_GENERATORS):
        for monomial, coefficient in terms.items():
            generators[f, index[monomial]] = coefficient
    chars, var_char = [1, 0, 1], [1, 0]
    block_of = np.array([a % 2 for a, _ in basis], dtype=np.int64)
    old = v13.block_tables(tables, index, block_of, var_char, [0, 1])
    new = v14.block_tables(tables, index, block_of, var_char, [0, 1])
    one_pos = int(old.pos[index[(0, 0)]])
    reference = v13.block_products(generators, chars, one_pos, v13.order_walk(basis, old), old, 3, P)
    assert {block for block, _ in reference.values()} == {0, 1}
    assert any(row[1].any() for row in reference.values())
    levels = v14.order_walk_levels(basis, new)
    for chunk in (1, 3):
        for route in (v14.block_products_streamed, v14.block_products_compact_operator):
            got = route(generators, chars, one_pos, levels, new, 3, P, chunk)
            assert got.keys() == reference.keys()
            for key, (block, row) in reference.items():
                assert got[key][0] == block
                assert np.array_equal(got[key][1], row), (route.__name__, chunk, key)


def _record(module: Any, tmp_path: Path, name: str, extra: list[str], monkeypatch, capsys) -> dict:
    header = tmp_path / "h.sing"
    header.write_text(MIXED)
    argv = [
        name,
        str(header),
        "2",
        "7",
        "--quotient",
        "--export-dir",
        str(tmp_path / name),
        "--singular",
        str(SINGULAR),
    ]
    monkeypatch.setattr(sys, "argv", [*argv, *extra])
    module.main()
    return json.loads(capsys.readouterr().out)


@needs_singular
def test_lazy_closure_frontier_reaches_engine_v13_block_ranks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Degree 2, order 7 of the mixed header closes in four rounds over four blocks; the lazy row-index frontier, the
    compact echelon and both product routes reach v13's per-block closure ranks and r_N."""
    want = _record(v13, tmp_path, "v13", [], monkeypatch, capsys)
    assert want["closure_rounds"] >= 3 and len(want["per_block"]) == 4
    for name, extra in ROUTES:
        got = _record(v14, tmp_path, name, extra, monkeypatch, capsys)
        assert got["per_block"] == want["per_block"], name
        assert got["r_N"] == want["r_N"] and got["closure_rounds"] == want["closure_rounds"], name


def test_lazy_closure_frontier_on_an_in_memory_two_block_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The Singular-free twin of the closure test: the truncated monomial cell of order 7 closes in four rounds over
    two character blocks, and every v14 route reaches v13's per-block ranks and round count."""
    basis, tables = _truncated_monomial_cell(7)
    gens = [dict(g) for g in CLOSURE_GENERATORS]
    header = tmp_path / "h.sing"
    terms = ",".join("+".join(f"{c}*x^{a}*y^{b}" for (a, b), c in g.items()) for g in gens)
    header.write_text(f"ring r={P},(x,y),dp;\nideal J=x^9,y^9;\nideal G={terms};\n")

    def run(module: Any, extra: list[str]) -> dict:
        monkeypatch.setattr(
            module, "quotient_data", lambda *args, **kwargs: (basis, tables, [dict(g) for g in gens], {})
        )
        monkeypatch.setattr(sys, "argv", ["engine", str(header), "2", "7", "--quotient", *extra])
        module.main()
        return json.loads(capsys.readouterr().out)

    want = run(v13, [])
    assert want["closure_rounds"] >= 3 and len(want["per_block"]) == 2
    for name, extra in ROUTES:
        got = run(v14, extra)
        assert got["per_block"] == want["per_block"], name
        assert got["r_N"] == want["r_N"] and got["closure_rounds"] == want["closure_rounds"], name


def _in_memory_cell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[[list[str]], dict]:
    """Run v14's quotient route on the order-7 monomial cell with the given engine options, without Singular."""
    basis, tables = _truncated_monomial_cell(7)
    gens = [dict(g) for g in CLOSURE_GENERATORS]
    header = tmp_path / "h.sing"
    terms = ",".join("+".join(f"{c}*x^{a}*y^{b}" for (a, b), c in g.items()) for g in gens)
    header.write_text(f"ring r={P},(x,y),dp;\nideal J=x^9,y^9;\nideal G={terms};\n")
    monkeypatch.setattr(v14, "quotient_data", lambda *args, **kwargs: (basis, tables, [dict(g) for g in gens], {}))

    def run(extra: list[str]) -> dict:
        monkeypatch.setattr(sys, "argv", ["engine", str(header), "2", "7", "--quotient", *extra])
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            v14.main()
        return json.loads(stdout.getvalue())

    return run


def test_initial_closure_multiplication_is_sliced_by_chunk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first closure pass multiplies the product rows of a block through `table_mul` one `--chunk` slice at a time,
    so its float64 result and modulo temporaries stay inside the `closure_chunk_temporaries` budget; the ranks do not
    depend on the slice width."""
    run = _in_memory_cell(tmp_path, monkeypatch)
    rows: list[int] = []
    for name in ("exact_mod_matmul", "sparse_mod_matmul"):
        real = getattr(v14, name)

        def spy(x: np.ndarray, table: Any, p: int, real: Callable = real) -> np.ndarray:
            if sys._getframe(1).f_code.co_name == "table_mul":
                rows.append(x.shape[0])
            return real(x, table, p)

        monkeypatch.setattr(v14, name, spy)
    for dense_gib in ("0", "1"):
        common = ["--stream-products", "--echelon", "compact", "--dense-tables-gb", dense_gib]
        wide = run([*common, "--chunk", "64"])
        products = wide["products"]
        assert products > 2 and max(rows) > 2, "the cell must hold more product rows than the narrow chunk"
        rows.clear()
        narrow = run([*common, "--chunk", "2"])
        assert rows and max(rows) <= 2
        assert narrow["closure_tables"] == wide["closure_tables"] == ("dense" if dense_gib == "1" else "sparse")
        for field in ("r_N", "per_block", "closure_rounds", "products"):
            assert narrow[field] == wide[field], (dense_gib, field)
        rows.clear()


@needs_singular
def test_compact_preflight_counts_the_character_components(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A header generator that spans several character blocks becomes one product generator per component, so the
    retained product rows and the accumulation temporaries follow the component count, not the header's."""
    got = _record(
        v14, tmp_path, "components", ["--stream-products", "--echelon", "compact", "--chunk", "2"], monkeypatch, capsys
    )
    ngens = 3
    components = got["generator_components"]
    assert components > ngens
    widest = max(block["cols"] for block in got["per_block"].values())
    rows = sum(math.comb(components + degree - 1, degree) for degree in range(1, 3))
    terms = got["preflight_terms"]
    assert terms["uint16_product_rows"] == 4 * rows * widest
    assert terms["streamed_loop_arrays"] == v14.streamed_loop_bytes(
        v14.streamed_prefix_peak(2, components, None), widest
    )
