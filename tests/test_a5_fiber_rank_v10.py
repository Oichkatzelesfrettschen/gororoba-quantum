"""Fiber-rank engine v10: products restricted to the standard monomials of k[y]/K2 against all products."""

import hashlib
import itertools
import json
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

ENGINE_DIR = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "replay" / "engine"
sys.path.insert(0, str(ENGINE_DIR))

import fiber_rank_v10 as v10  # noqa: E402

P = 32009
SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")
# G = (t1^2, t2^2, t1*t2) satisfies y1*y2 - y3^2 = 0 as polynomials, so that quadric holds in J + m * P_2.
HEADER = "ring r=32009,(t1,t2,t3),dp;\nideal J=t1^3-t2*t3^2,t2^3-t1^2*t3;\nideal G=t1^2,t2^2,t1*t2;\n"


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _fixture(tmp: Path, relation: str) -> tuple[Path, Path]:
    header = tmp / "toy.sing"
    header.write_text(HEADER)
    rel = tmp / "relations-d2.rel"
    rel.write_text(relation + "\n")
    receipt = tmp / "receipt-d2.json"
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
    return header, receipt


def _run(header: Path, d: int, N: int, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ENGINE_DIR / "fiber_rank_v10.py"), str(header), str(d), str(N), "--quotient", *extra],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(Path(str(SINGULAR)).parent), "SINGULAR": str(SINGULAR)},
    )


def _blocks(rec: dict) -> list[int]:
    return [rec["per_block"][k]["r_N"] for k in sorted(rec["per_block"])]


def test_receipt_for_another_header_refuses(tmp_path: Path) -> None:
    header, receipt = _fixture(tmp_path, "y(1)*y(2)-y(3)^2")
    other = tmp_path / "other.sing"
    other.write_text(HEADER.replace("t2^3", "t2^4"))
    with pytest.raises(SystemExit):
        v10.load_receipt(str(receipt), str(other), P, 3)
    with pytest.raises(SystemExit):
        v10.load_receipt(str(receipt), str(header), 32029, 3)
    (tmp_path / "relations-d2.rel").write_text("y(1)^2\n")
    with pytest.raises(SystemExit):
        v10.load_receipt(str(receipt), str(header), P, 3)


def test_restricted_products_equal_the_full_rows() -> None:
    basis = sorted((e for e in itertools.product(range(4), repeat=2) if sum(e) < 4), key=lambda e: (sum(e), e))
    idx = {m: i for i, m in enumerate(basis)}
    M = []
    for k in range(2):
        r_i, c_j = [], []
        for i, m in enumerate(basis):
            up = tuple(x + (j == k) for j, x in enumerate(m))
            if up in idx:
                r_i.append(i)
                c_j.append(idx[up])
        M.append(sp.csr_matrix((np.ones(len(r_i)), (r_i, c_j)), shape=(len(basis), len(basis))))
    gvecs = np.array([[(3 * f + 5 * i + 1) % P for i in range(len(basis))] for f in range(3)], dtype=np.float64)
    full = v10.table_products(gvecs, basis, M, 3, P, 0)
    order: list[tuple[int, ...]] = list(itertools.combinations_with_replacement(range(3), 3))
    wanted: dict[int, set[tuple[int, ...]]] = {
        1: {(0,), (2,)},
        2: {(0, 0), (0, 2), (2, 2)},
        3: {(0, 0, 2), (0, 2, 2), (2, 2, 2)},
    }
    part = v10.table_products(gvecs, basis, M, 3, P, 0, wanted)
    _check(np.array_equal(part, full[[order.index(t) for t in sorted(wanted[3])]]))


def test_a_kbase_outside_an_order_ideal_refuses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    header, receipt = _fixture(tmp_path, "y(1)*y(2)-y(3)^2")
    monkeypatch.setattr(v10, "standard_monomials", lambda *a: ({1: [[1, 0, 0]], 2: [[0, 1, 1]]}, []))
    a = Namespace(k2_receipt=str(receipt), header=str(header), d=2, singular="Singular", checks=4)
    with pytest.raises(RuntimeError):
        v10.representatives(a, P, 3)


@needs_singular
@pytest.mark.parametrize(("d", "N"), [(2, 7), (3, 9)])
def test_standard_products_give_the_full_rank(tmp_path: Path, d: int, N: int) -> None:
    header, receipt = _fixture(tmp_path, "y(1)*y(2)-y(3)^2")
    full = _run(header, d, N)
    part = _run(header, d, N, "--k2-receipt", str(receipt))
    _check(full.returncode == 0 and part.returncode == 0)
    a, b = json.loads(full.stdout), json.loads(part.stdout)
    _check(a["r_N"] == b["r_N"] and _blocks(a) == _blocks(b))
    _check(b["products"] < a["products"] and b["checks"] == {"count": 1 + (d == 3) * 2, "rank_growth": {}})


@needs_singular
def test_a_false_relation_raises_the_rank_of_its_check(tmp_path: Path) -> None:
    header, receipt = _fixture(tmp_path, "y(1)^2")
    res = _run(header, 2, 7, "--k2-receipt", str(receipt))
    _check(res.returncode != 0 and "raise the rank" in res.stderr)


@needs_singular
def test_the_targeted_checks_alone_catch_a_false_relation(tmp_path: Path) -> None:
    header, receipt = _fixture(tmp_path, "y(1)^2")
    res = _run(header, 2, 7, "--k2-receipt", str(receipt), "--checks", "0")
    _check(res.returncode != 0 and "raise the rank" in res.stderr)
    (tmp_path / "true").mkdir()
    true_header, true_receipt = _fixture(tmp_path / "true", "y(1)*y(2)-y(3)^2")
    ok = _run(true_header, 3, 9, "--k2-receipt", str(true_receipt), "--checks", "0")
    rec = json.loads(ok.stdout)["representatives"]
    _check(ok.returncode == 0 and rec["checks_targeted"] == 1 and rec["checks_strided"] == 0)
