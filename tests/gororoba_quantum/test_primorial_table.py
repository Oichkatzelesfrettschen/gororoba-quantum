"""gororoba_quantum/primorial_table.py: the Table 1 transcription is self-consistent, the low rows reproduce, a carried
witness covers at every later level, and the retained record holds every row up to k = 20 in agreement.
"""

from __future__ import annotations

import json
from pathlib import Path

import primorial_cover as pc
import primorial_table as pt

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/evidence/primorial_cover/ziller_table.json"


def test_transcription_rows_chain() -> None:
    for k, (p_k, h_prev, n_min, missing, h) in pt.ZILLER_TABLE_1.items():
        if pc.primes_up_to(p_k) != pc.primes_up_to(p_k)[:k] or len(pc.primes_up_to(p_k)) != k:
            raise AssertionError(f"row {k}: p_k = {p_k}")
        if k > 1 and h_prev != pt.ZILLER_TABLE_1[k - 1][4]:
            raise AssertionError(f"row {k}: h(k - 1) = {h_prev}")
        expected = missing[0] - 2 if missing else h
        if n_min != expected or any(not n_min < m < h for m in missing):
            raise AssertionError(f"row {k}: N_min {n_min}, missing {missing}, h {h}")


def test_low_rows_reproduce() -> None:
    record = pt.reproduce(top=9)
    if not record["table_agrees"] or [row["missing"] for row in record["rows"]][5:8] != [[20], [], [32]]:
        raise AssertionError(record["rows"])


def test_carried_witness_covers_at_later_levels() -> None:
    half, k_from = 10, 7
    cover, _ = pt.CellSearch()((k_from, half))
    if cover is None:
        raise AssertionError("gap 20 exists at k = 7")
    for k in (7, 8, 12):
        if pc.uncovered(half, pc.odd_primes(k), pt.extend(half, k_from, cover, k)):
            raise AssertionError(k)
    if pt.CellSearch()((6, half))[0] is not None:
        raise AssertionError("gap 20 is missing at k = 6")


def test_retained_record_agrees_through_k20() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    missing = {row["k"]: row["missing"] for row in record["rows"]}
    if not record["table_agrees"] or sorted(missing) != list(range(1, 21)):
        raise AssertionError(record["table_agrees"])
    for k, row in pt.ZILLER_TABLE_1.items():
        if missing[k] != list(row[3]):
            raise AssertionError((k, missing[k], row[3]))
