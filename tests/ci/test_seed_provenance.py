"""Every seed literal in the code directories is a listed reproduction seed or an allocated ANU QRNG value."""

from __future__ import annotations

import pytest
import seed_provenance


def test_seed_provenance_self_test() -> None:
    if seed_provenance.self_test() != 0:
        raise AssertionError("seed_provenance self-test failed")


@pytest.mark.parametrize("shard", range(seed_provenance.SHARDS))
def test_tree_seeds_are_accounted(shard: int) -> None:
    seed_provenance.check_tree(shard)


def test_reproduction_seeds_only_shrink() -> None:
    seed_provenance.check_shrink()


def test_retained_qrng_references_match_the_runtime_ledger() -> None:
    seed_provenance.check_runtime_tree()
