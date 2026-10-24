"""Every seed literal in the code directories is a listed reproduction seed or an allocated ANU QRNG value."""

from __future__ import annotations

import seed_provenance


def test_seed_provenance_self_test() -> None:
    if seed_provenance.self_test() != 0:
        raise AssertionError("seed_provenance self-test failed")


def test_tree_seeds_are_accounted() -> None:
    seed_provenance.check_tree()
