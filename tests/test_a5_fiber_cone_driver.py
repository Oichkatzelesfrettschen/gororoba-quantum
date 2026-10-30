"""Exact parsing, rank and kernel, and the dense-family verdicts of the A_5 fiber tooling (no Singular needed)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-kernel-attachments"))

import fiber_certificates as cert  # noqa: E402
import fiber_cone_driver as drv  # noqa: E402

P = 32009


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def test_parse_poly_exact() -> None:
    poly = drv.parse_poly("-2*t2*t4^2+4251*t1-t3+t3+7", P)
    _check(poly == {(("t2", 1), ("t4", 2)): P - 2, (("t1", 1),): 4251, (): 7})


def test_parse_poly_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        drv.parse_poly("t1*(t2+1)", P)


def test_left_kernel_matches_dependency() -> None:
    rows = [drv.parse_poly(s, P) for s in ("t1+t2", "t2+t3", "t1-t3", "t1")]
    kernel = drv.left_kernel(rows, P)
    _check(kernel.rank == 3)
    _check(len(kernel.relations) == 1)
    for vec in kernel.relations:
        total: dict[drv.Monomial, int] = {}
        for c, row in zip(vec, rows, strict=True):
            for m, x in row.items():
                total[m] = (total.get(m, 0) + c * x) % P
        _check(not any(total.values()))


def test_admission_bound() -> None:
    _check(drv.admitted_workers(3, 3, 5) == 1)


def test_dense_family_verdicts() -> None:
    comps = [{"name": "A", "dimension": 1, "generators": ["y(1)", "y(2)"]}]
    _check(cert.dense_family([[0, 0, 5]], comps, P)["status"] == "support lower bound")
    _check(cert.dense_family([[1, 0, 5]], comps, P)["status"] == "refuted")
    _check(cert.dense_family([], comps, P)["status"] == "support lower bound")


def test_batch_timeout_reaches_each_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[int] = []

    def fake_run_degree(*args: object) -> dict[str, object]:
        seen.append(int(str(args[6])))
        return {}

    monkeypatch.setattr(drv, "run_degree", fake_run_degree)
    monkeypatch.setattr(drv.parallel, "ordered_map", lambda f, items, min_items=1: [f(i) for i in items])
    item = {"header": "h.sing", "degree": 2, "out": "o", "prime": P, "memory_gib": 4}
    drv.run_batch([item, {**item, "timeout": 7}], budget_gib=8, timeout=3600)
    _check(seen == [3600, 7])


def test_singular_errors_catch_indented_diagnostics() -> None:
    text = "RESULT h 3\n   ? `K` is undefined\n   ? error occurred in or before STDIN line 4\nRESULT std_ms 5\n"
    _check(drv.singular_errors(text) == ["? `K` is undefined", "? error occurred in or before STDIN line 4"])
    _check(drv.singular_errors("RESULT h 3\n") == [])
