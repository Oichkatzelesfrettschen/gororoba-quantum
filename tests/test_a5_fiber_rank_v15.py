"""Three-copy stack accounting preserves bounded quotient arithmetic and controls."""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ENGINE_DIR = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine"
PRIME = 32009


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _load(version: int) -> Any:
    path = ENGINE_DIR / f"fiber_rank_v{version}.py"
    spec = importlib.util.spec_from_file_location(f"fiber_rank_v{version}_stack_test", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _WithoutDocstrings(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr) -> ast.AST | None:
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return None
        return node


def _arithmetic_tree(source: str, successor: bool) -> str:
    if successor:
        old = '"uint16_product_rows": 6 * rows * widest'
        _check(source.count(old) == 1)
        source = source.replace(old, '"uint16_product_rows": 4 * rows * widest')
    return ast.dump(_WithoutDocstrings().visit(ast.parse(source)), include_attributes=False)


@pytest.mark.parametrize("mutated", [False, True])
def test_only_product_row_accounting_changes_executable_source(mutated: bool) -> None:
    predecessor = (ENGINE_DIR / "fiber_rank_v14.py").read_text()
    successor = (ENGINE_DIR / "fiber_rank_v15.py").read_text()
    if mutated:
        successor = successor.replace("return 10 * prefixes * widest", "return 11 * prefixes * widest")
    equivalent = _arithmetic_tree(predecessor, False) == _arithmetic_tree(successor, True)
    _check(equivalent == (not mutated))


@pytest.fixture
def cell(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Callable[..., dict[str, Any]]:
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
    generators = [{(1, 0): 1}, {(0, 1): 1}, {(1, 0): 1}]
    header = tmp_path / "duplicate-generator.sing"
    header.write_text(f"ring r={PRIME},(x,y),dp;\nideal J=x^9,y^9;\nideal G=x,y,x;\n")

    def run(
        module: Any,
        options: list[str],
        receipt: bool = False,
        preflight_only: bool = False,
        bad_control: bool = False,
    ) -> dict[str, Any]:
        def quotient_data(*args: Any, **kwargs: Any) -> tuple[Any, ...]:
            # The production exporter invokes preflight before constructing quotient multiplication tables.
            args[-1](basis)
            if preflight_only:
                raise AssertionError("preflight admitted tables that the memory limit should reject")
            return basis, tables, [dict(generator) for generator in generators], {}

        monkeypatch.setattr(module, "quotient_data", quotient_data)
        if receipt:
            representatives = [(0, 0), (0, 1), (1, 1)]
            controls = [(0, 2), (1, 2), (2, 2)]
            if bad_control:
                representatives.remove((0, 1))
                controls.append((0, 1))
            wanted = {1: {(0,), (1,), (2,)}, 2: set(representatives + controls)}
            record = {"fixture": "duplicate x generator", "checks_targeted": 3, "standard_counts": {"2": 3}}
            monkeypatch.setattr(
                module,
                "representatives",
                lambda *args: module.Representatives(wanted, representatives, controls, record),
            )
        extra = ["--k2-receipt", "synthetic-receipt.json"] if receipt else []
        monkeypatch.setattr(sys, "argv", ["engine", str(header), "2", str(order), "--quotient", *extra, *options])
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            module.main()
        return json.loads(stdout.getvalue())

    return run


@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("receipt", [False, True])
def test_three_copy_term_preserves_ranks_and_nonstandard_controls(
    cell: Callable[..., dict[str, Any]], cached: bool, receipt: bool
) -> None:
    options = ["--stream-products", "--echelon", "compact", "--chunk", "3"]
    if cached:
        options += ["--operator-cache-gb", "1"]
    old = cell(_load(14), options, receipt)
    new = cell(_load(15), options, receipt)
    excluded = {"engine_sha256_16", "seconds", "preflight_bytes", "preflight_terms", "preflight_stages"}
    _check(
        {key: value for key, value in old.items() if key not in excluded}
        == {key: value for key, value in new.items() if key not in excluded}
    )
    _check(new["r_N"] == 3 and new["closure_rounds"] >= 1)
    _check(new["product_operator"] == ("uint16-cached" if cached else "uint16-streamed"))
    if receipt:
        _check(new["checks"] == {"count": 3, "rank_growth": {}})
        _check(new["representatives"]["checks_targeted"] == 3)
    widest = max(block["cols"] for block in new["per_block"].values())
    rows = sum(math.comb(new["generator_components"] + degree - 1, degree) for degree in (1, 2))
    if receipt:
        rows = 9
    _check(old["preflight_terms"]["uint16_product_rows"] == 4 * rows * widest)
    _check(new["preflight_terms"]["uint16_product_rows"] == 6 * rows * widest)
    _check(
        {key: value for key, value in old["preflight_terms"].items() if key != "uint16_product_rows"}
        == {key: value for key, value in new["preflight_terms"].items() if key != "uint16_product_rows"}
    )
    for stage in ("products", "closure"):
        _check(new["preflight_stages"][stage] - old["preflight_stages"][stage] == 2 * rows * widest)


@pytest.mark.parametrize("cached", [False, True])
def test_nonstandard_controls_reject_a_missing_independent_product(
    cell: Callable[..., dict[str, Any]], cached: bool
) -> None:
    options = ["--stream-products", "--echelon", "compact", "--chunk", "3"]
    if cached:
        options += ["--operator-cache-gb", "1"]
    with pytest.raises(SystemExit, match="nonstandard products raise the rank"):
        cell(_load(15), options, receipt=True, bad_control=True)


@pytest.mark.parametrize("cached", [False, True])
def test_limit_between_estimates_rejects_before_table_construction(
    cell: Callable[..., dict[str, Any]], monkeypatch: pytest.MonkeyPatch, cached: bool
) -> None:
    old, new = _load(14), _load(15)
    for module in (old, new):
        # Remove the fixed tile scratch so this tiny cell isolates the row-copy budget.
        monkeypatch.setattr(module, "tiled_product_bytes", lambda chunk: 0)
        monkeypatch.setattr(module, "insert_panel_bytes", lambda block, chunk: 0)
    options = ["--stream-products", "--echelon", "compact", "--chunk", "3"]
    if cached:
        options += ["--operator-cache-gb", "1"]
    old_record = cell(old, options)
    new_record = cell(new, options)
    _check(old_record["preflight_bytes"] < new_record["preflight_bytes"])
    limit = (old_record["preflight_bytes"] + new_record["preflight_bytes"]) / 2 / 2**30
    constrained = [*options, "--max-gb", str(limit)]
    cell(old, constrained)
    with pytest.raises(SystemExit, match="preflight .* exceeds --max-gb"):
        cell(new, constrained, preflight_only=True)
    cell(new, [*options, "--max-gb", str((new_record["preflight_bytes"] + 1) / 2**30)])
