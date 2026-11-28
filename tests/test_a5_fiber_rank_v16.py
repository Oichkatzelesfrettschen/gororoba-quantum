"""Engine v16 skips the structural zero levels of the generator operator and keeps every rank of v15."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ENGINE_DIR = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine"
PRIME = 32009


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _load(version: int) -> Any:
    path = ENGINE_DIR / f"fiber_rank_v{version}.py"
    spec = importlib.util.spec_from_file_location(f"fiber_rank_v{version}_zero_rows_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_level_cut_follows_the_least_degree_of_the_normal_form() -> None:
    v16 = _load(16)
    degree = np.array([0, 1, 1, 2, 2, 2, 3])
    _check(v16.structural_level_cut(np.array([0, 1, 0, 0, 0, 0, 0]), degree, 5) == 3)
    _check(v16.structural_level_cut(np.array([0, 0, 0, 0, 0, 1, 1]), degree, 5) == 2)
    _check(v16.structural_level_cut(np.array([0, 0, 0, 0, 0, 0, 0]), degree, 5) == 0)
    _check(v16.structural_level_cut(np.array([0, 0, 0, 0, 0, 0, 1]), degree, 3) == 0)


def _run(module: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, options: list[str]) -> dict[str, Any]:
    order = 7
    basis = [(x, degree - x) for degree in range(order) for x in range(degree + 1)]
    tables = [
        [
            {tuple(exponent + int(axis == variable) for axis, exponent in enumerate(monomial)): 1}
            if sum(monomial) + 1 < order
            else {}
            for monomial in basis
        ]
        for variable in range(2)
    ]
    generators = [{(1, 0): 1}, {(0, 1): 1}, {(1, 1): 1}]
    header = tmp_path / "zero-rows.sing"
    header.write_text(f"ring r={PRIME},(x,y),dp;\nideal J=x^9,y^9;\nideal G=x,y,x*y;\n")

    def quotient_data(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
        args[-1](basis)
        return basis, tables, [dict(g) for g in generators], {}

    monkeypatch.setattr(module, "quotient_data", quotient_data)
    monkeypatch.setattr(sys, "argv", ["engine", str(header), "2", str(order), "--quotient", *options])
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        module.main()
    return json.loads(stdout.getvalue())


@pytest.mark.parametrize("cached", [False, True])
def test_v16_ranks_equal_v15(cached: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    options = ["--stream-products", "--echelon", "compact", "--chunk", "3"]
    if cached:
        options += ["--operator-cache-gb", "1"]
    old = _run(_load(15), tmp_path, monkeypatch, options)
    new = _run(_load(16), tmp_path, monkeypatch, options)
    _check(old["r_N"] == new["r_N"] and old["per_block"] == new["per_block"])
    _check(old["product_operator"] == new["product_operator"])
