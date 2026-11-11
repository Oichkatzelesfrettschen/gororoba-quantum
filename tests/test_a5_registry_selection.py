"""Duplicate selection and the documented scan roots of the A_5 claim registry builder."""

from __future__ import annotations

import importlib.util
import itertools
from pathlib import Path
from typing import Any

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/build_registry.py"
SPEC = importlib.util.spec_from_file_location("a5_build_registry", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"cannot load {SOURCE}")
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)

KEY = ("engine", "header", 5, 16, "raw")


def entry(source: str, products: Any = None) -> dict[str, Any]:
    record = {"r_N": 1} if products is None else {"r_N": 1, "products": products}
    return {"source": source, "record": record}


def winner(offers: list[tuple[int, dict[str, Any]]]) -> str:
    table: dict[tuple, dict] = {}
    owners: dict[tuple, int] = {}
    for root_index, item in offers:
        registry.retain(table, owners, KEY, item, root_index)
    return str(table[KEY]["source"])


def test_more_products_then_greater_path_wins_in_any_order_within_a_root() -> None:
    offers = [(0, entry("r/a.jsonl", 4116)), (0, entry("r/b.out", 98280)), (0, entry("r/c.out", 98280))]
    for order in itertools.permutations(offers):
        if winner(list(order)) != "r/c.out":
            raise AssertionError(f"selection depends on the order {[o[1]['source'] for o in order]}")


def test_first_root_keeps_the_key_against_a_more_complete_later_root() -> None:
    if winner([(0, entry("first/a.jsonl", 10)), (1, entry("second/a.jsonl", 99999))]) != "first/a.jsonl":
        raise AssertionError("a later root replaced the first root's record")


def test_first_root_owns_a_key_across_the_bound_and_unbound_tables() -> None:
    bound: dict[tuple, dict] = {}
    unbound: dict[tuple, dict] = {}
    owners: dict[tuple, int] = {}
    registry.retain(unbound, owners, KEY, entry("first/bad.jsonl"), 0)
    registry.retain(bound, owners, KEY, entry("second/good.jsonl", 5), 1)
    if bound or unbound[KEY]["source"] != "first/bad.jsonl":
        raise AssertionError("a later root certified a key the first root left unbound")


@pytest.mark.parametrize("value", [None, "98280", 3.0, True, -1, [1]])
def test_a_malformed_product_count_ranks_below_every_count(value: Any) -> None:
    if registry.ranked_products({"products": value}) != -1:
        raise AssertionError(f"products = {value!r} was read as a count")
    if winner([(0, entry("r/z.jsonl", value)), (0, entry("r/a.jsonl", 0))]) != "r/a.jsonl":
        raise AssertionError(f"products = {value!r} outranked a valid count")


def test_documented_roots_exist_and_match_the_readme() -> None:
    here = SOURCE.parent
    missing = [name for name in registry.ROOTS if not (here / name).is_dir()]
    if missing:
        raise AssertionError(f"scan roots absent from the tree: {missing}")
    if " ".join(registry.ROOTS) not in (here / "README.md").read_text(encoding="utf-8"):
        raise AssertionError("README.md does not list the scan roots in ROOTS order")
