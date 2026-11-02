"""Fiber-rank engine v11: block-structured generator matrices and sparse closure against engine v10."""

import hashlib
import itertools
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

ENGINE_DIR = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "replay" / "engine"
sys.path.insert(0, str(ENGINE_DIR))

import fiber_rank_v10 as v10  # noqa: E402
import fiber_rank_v11 as v11  # noqa: E402

P = 32009
SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")
# G = (t1^2, t2^2, t1*t2) satisfies y1*y2 - y3^2 = 0 as polynomials, so that quadric holds in J + m * P_2.
PURE = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^3-t2*t3^2,t2^3-t1^2*t3;\nideal G=t1^2,t2^2,t1*t2;\n"
# Flipping t1 or t2 preserves span(J) and span(G), and t1 + t2, t1 - t2 each mix two characters.
MIXED = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^4-t2^4,t3^3-t1^2*t2^2;\nideal G=t1+t2,t1-t2,t3^2;\n"


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _toy() -> tuple[list[tuple[int, ...]], list[list[dict]], np.ndarray, list[int]]:
    """k[t1, t2] modulo degree 4 with t1 of character 1 and t2 of character 0: basis, tables, generators, characters."""
    basis = sorted((e for e in itertools.product(range(4), repeat=2) if sum(e) < 4), key=lambda e: (sum(e), e))
    tables = []
    for k in range(2):
        rows = []
        for m in basis:
            up = tuple(x + (j == k) for j, x in enumerate(m))
            rows.append({up: 1} if sum(up) < 4 else {})
        tables.append(rows)
    block_of = np.array([m[0] % 2 for m in basis])
    gvecs = np.zeros((3, len(basis)))
    for f, want in enumerate([0, 1, 0]):
        for i in np.flatnonzero(block_of == want):
            gvecs[f, i] = (7 * f + 3 * i + 1) % P
    return basis, tables, gvecs, [0, 1, 0]


def test_block_products_equal_the_dense_products() -> None:
    basis, tables, gvecs, gchar = _toy()
    bidx = {m: i for i, m in enumerate(basis)}
    block_of = np.array([m[0] % 2 for m in basis])
    lay = v11.block_tables(tables, bidx, block_of, [1, 0], [0, 1])
    M = [
        sp.csr_matrix(
            (
                np.ones(sum(len(r) for r in t)),
                ([i for i, r in enumerate(t) for _ in r], [bidx[m] for r in t for m in r]),
            ),
            shape=(len(basis), len(basis)),
        )
        for t in tables
    ]
    walk = v11.order_walk(basis, lay)
    one = int(lay.pos[bidx[(0, 0)]])
    for d in (1, 2, 3):
        full = v10.table_products(gvecs, basis, M, d, P, 0)
        built = v11.block_products(gvecs, gchar, one, walk, lay, d, P)
        order = list(itertools.combinations_with_replacement(range(3), d))
        _check(sorted(built) == order)
        for t, (b, row) in built.items():
            embedded = np.zeros(len(basis))
            embedded[lay.cols[b]] = row
            _check(np.array_equal(embedded, full[order.index(t)]))


def test_sparse_products_refuse_an_inexact_inner_dimension() -> None:
    S = sp.csr_matrix(np.eye(3))
    with pytest.raises(ValueError):
        v11.sparse_mod_matmul(np.ones((1, 4)), sp.csr_matrix((4, 3)), 2**26 + 1)
    _check(np.array_equal(v11.sparse_mod_matmul(np.array([[P + 1, 2, 3]], dtype=float), S, P), [[1, 2, 3]]))


def _run(engine: str, header: Path, d: int, N: int, *extra: str) -> dict:
    res = subprocess.run(
        [sys.executable, str(ENGINE_DIR / engine), str(header), str(d), str(N), "--quotient", *extra],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(Path(str(SINGULAR)).parent), "SINGULAR": str(SINGULAR)},
    )
    if res.returncode:
        return {"returncode": res.returncode, "stderr": res.stderr}
    return json.loads(res.stdout)


def _blocks(rec: dict) -> list[int]:
    return [rec["per_block"][k]["r_N"] for k in sorted(rec["per_block"])]


@needs_singular
@pytest.mark.parametrize("tables", ["sparse", "dense"])
@pytest.mark.parametrize(("text", "d", "N"), [(PURE, 2, 7), (PURE, 3, 9), (MIXED, 2, 6), (MIXED, 3, 7)])
def test_block_engine_ranks_equal_engine_v10(tmp_path: Path, text: str, d: int, N: int, tables: str) -> None:
    header = tmp_path / "h.sing"
    header.write_text(text)
    extra = ("--dense-tables-gb", "1") if tables == "dense" else ()
    a, b = _run("fiber_rank_v10.py", header, d, N), _run("fiber_rank_v11.py", header, d, N, *extra)
    _check("r_N" in a and "r_N" in b and a["r_N"] == b["r_N"] and _blocks(a) == _blocks(b))
    _check(b["generator_components"] == (3 if text == PURE else 5) and b["closure_tables"] == tables)


@needs_singular
def test_a_receipt_with_a_mixed_generator_refuses(tmp_path: Path) -> None:
    header = tmp_path / "h.sing"
    header.write_text(MIXED)
    rel = tmp_path / "relations-d2.rel"
    rel.write_text("y(1)*y(2)\n")
    receipt = tmp_path / "receipt-d2.json"
    receipt.write_text(
        json.dumps(
            {
                "status": "degree-certified",
                "degree": 2,
                "prime": P,
                "generator_count": 3,
                "input_sha256": hashlib.sha256(header.read_bytes()).hexdigest(),
                "relation_file": rel.name,
                "relation_sha256": hashlib.sha256(rel.read_bytes()).hexdigest(),
                "relation_count": 1,
                "generator_order_sha256": "0" * 64,
            }
        )
    )
    res = _run("fiber_rank_v11.py", header, 2, 6, "--k2-receipt", str(receipt))
    _check(res.get("returncode", 0) != 0 and "pure characters" in res["stderr"])


@needs_singular
def test_an_empty_character_block_runs(tmp_path: Path) -> None:
    header = tmp_path / "h.sing"
    header.write_text("ring r=32009,(t1,t2),dp;\nideal J=t1^2;\nideal G=t1;\n")
    a, b = _run("fiber_rank_v10.py", header, 1, 1), _run("fiber_rank_v11.py", header, 1, 1)
    _check("r_N" in b and a["r_N"] == b["r_N"] and _blocks(a) == _blocks(b))
    _check(any(v["cols"] == 0 for v in b["per_block"].values()))


@needs_singular
def test_the_preflight_counts_every_level_of_the_component_products(tmp_path: Path) -> None:
    header = tmp_path / "h.sing"
    header.write_text(MIXED)
    rec = _run("fiber_rank_v11.py", header, 3, 7)
    sizes = [rec["per_block"][k]["cols"] for k in sorted(rec["per_block"])]
    m = rec["generator_components"]
    rows = sum(len(list(itertools.combinations_with_replacement(range(m), e))) for e in range(1, 4))
    gen = max(sum(sizes[b] * sizes[b ^ c] for b in range(len(sizes))) for c in range(len(sizes)))
    want = 8 * gen + 2 * 8 * gen // len(sizes) + 2 * 8 * rows * max(sizes) + 2 * 8 * sum(x * x for x in sizes)
    _check(m == 5 and rec["preflight_bytes"] == want)
