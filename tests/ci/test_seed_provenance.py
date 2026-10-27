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


def test_owned_draws_and_reserved_rows_validate() -> None:
    seed_provenance.check_tree_once()


def test_reproduction_seeds_only_shrink() -> None:
    seed_provenance.check_shrink()


def test_retained_qrng_references_match_the_runtime_ledger() -> None:
    seed_provenance.check_runtime_tree()


@pytest.mark.audit
def test_tracked_docs_probes_enter_the_scan() -> None:
    probe = "docs/evidence/c5_zero_divisor_code/replay.py"
    if probe not in seed_provenance.tracked_files():
        raise AssertionError(f"{probe} is not tracked")
    keys, _ = seed_provenance.file_literals(probe)
    if (probe, "SEED", 314) not in keys:
        raise AssertionError(f"the scan reads {keys} in {probe}")


RECORD = "docs/evidence/anu_qrng/draw-2026-10-25T095947Z.json"
SYNTHETIC = {"values": [11, 22, 33]}
ROW = {"path": "p.py", "value": 22, "record": RECORD, "index": 1, "reason": "RNG alias"}
TEXT = f"# {RECORD.rsplit('/', 1)[1]}\nrng = RNG(22)\n"


def admit_synthetic(record: dict[str, object]) -> None:
    del record


def run_reserved(
    allocations: list[dict[str, object]], files: dict[str, tuple[str, frozenset[int]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(seed_provenance.SOURCES, "docs/evidence/anu_qrng", admit_synthetic)
    seed_provenance.check_reserved([ROW], allocations, [], set(), lambda path: SYNTHETIC, files)


def test_reserved_value_the_scan_detects_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    run_reserved([], {"p.py": (TEXT, frozenset())}, monkeypatch)
    with pytest.raises(seed_provenance.SeedError, match="the scan detects"):
        run_reserved([], {"p.py": (TEXT, frozenset({22}))}, monkeypatch)


def test_allocated_index_reused_by_a_reserved_row_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(seed_provenance.SeedError, match="already taken in allocations"):
        run_reserved([{"record": RECORD, "index": 1}], {"p.py": (TEXT, frozenset())}, monkeypatch)


def test_base_tree_literal_admits_a_baseline_row() -> None:
    key = ("docs/x.py", "SEED", 314)
    head = [{"path": key[0], "name": key[1], "value": key[2], "count": 1}]
    if seed_provenance.shrink_problems([], head, {key[0]: seed_provenance.Counter({key: 1})}):
        raise AssertionError("a literal the base tree holds was refused")
    if not seed_provenance.shrink_problems([], head, {}):
        raise AssertionError("a literal the base tree lacks was admitted")


def test_base_allocated_literal_stays_out_of_the_baseline() -> None:
    key = ("scripts/x.py", "SEED", 314)
    head = [{"path": key[0], "name": key[1], "value": key[2], "count": 1}]
    held = seed_provenance.unaccounted({key[0]: seed_provenance.Counter({key: 1})}, seed_provenance.Counter({key: 1}))
    if not seed_provenance.shrink_problems([], head, held):
        raise AssertionError("a QRNG literal allocated on the base entered the reproduction baseline")
