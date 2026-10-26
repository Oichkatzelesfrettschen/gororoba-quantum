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


def test_tracked_docs_probes_enter_the_scan() -> None:
    probe = "docs/evidence/c5_zero_divisor_code/replay.py"
    if probe not in seed_provenance.tracked_files():
        raise AssertionError(f"{probe} is not tracked")
    keys, _ = seed_provenance.file_literals(probe)
    if (probe, "SEED", 314) not in keys:
        raise AssertionError(f"the scan reads {keys} in {probe}")


def test_reserved_rows_hold_their_values() -> None:
    reserved = seed_provenance.load(seed_provenance.ALLOCATIONS, "reserved")
    if not reserved:
        raise AssertionError("allocations.json lists no reserved consumer")
    for row in reserved:
        values = seed_provenance.read_tree_record(row["record"])["values"]
        if values[row["index"]] != row["value"]:
            raise AssertionError(f"{row['path']}: {row['value']} is not index {row['index']} of {row['record']}")


def test_reserved_value_the_scan_detects_is_refused() -> None:
    row = seed_provenance.load(seed_provenance.ALLOCATIONS, "reserved")[0]
    path = row["path"]
    text = (seed_provenance.ROOT / path).read_text(encoding="utf-8")
    detected = frozenset(value for _, _, value in seed_provenance.text_literals(path, text)[0])
    with pytest.raises(seed_provenance.SeedError, match="the scan detects"):
        seed_provenance.check_reserved(
            [row],
            [],
            [],
            set(),
            seed_provenance.read_tree_record,
            {path: (text, detected | {row["value"]})},
        )


def test_allocated_index_reused_by_a_reserved_row_is_refused() -> None:
    row = seed_provenance.load(seed_provenance.ALLOCATIONS, "reserved")[0]
    taken = {"record": row["record"], "index": row["index"]}
    with pytest.raises(seed_provenance.SeedError, match="already taken in allocations"):
        seed_provenance.check_reserved(
            [row], [taken], [], set(), seed_provenance.read_tree_record, {row["path"]: (row["record"], frozenset())}
        )


def test_base_tree_literal_admits_a_baseline_row() -> None:
    key = ("docs/x.py", "SEED", 314)
    head = [{"path": key[0], "name": key[1], "value": key[2], "count": 1}]
    if seed_provenance.shrink_problems([], head, {key[0]: seed_provenance.Counter({key: 1})}):
        raise AssertionError("a literal the base tree holds was refused")
    if not seed_provenance.shrink_problems([], head, {}):
        raise AssertionError("a literal the base tree lacks was admitted")
