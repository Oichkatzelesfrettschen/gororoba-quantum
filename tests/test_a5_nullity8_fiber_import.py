"""Import of the nullity-8 fiber cones into the nullity-16 limit-set table: source agreement and its mutations."""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import nullity8_fiber_import as fi  # noqa: E402

RECORD = ATTACHMENTS / "nullity8-fiber-import-result.json"
FIBER = {fiber.name: fiber for fiber in fi.FIBER_TABLE}


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _nullity16_rows() -> dict[str, dict[str, Any]]:
    record = json.loads(fi.NULLITY16_RESULT.read_text(encoding="utf-8"))
    return {str(row["incidence"]): row for row in record["incidences"] if row["status"] != "completed"}


def _retained_cells(slug: str) -> dict[tuple[int, int], dict[str, dict[str, Any]]]:
    """The regeneration result a matching producer returns, built from the retained record."""
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    row = next(row for row in record["incidences"] if row["slug"] == slug)
    return {
        (cell["prime"], cell["i_root"]): {
            slug: {
                "header_sha256": cell["regenerated_sha256"],
                "generator_count": cell["generator_count"],
                "selected_indices_one_based": cell["selected_indices_one_based"],
            }
        }
        for cell in row["cells"]
    }


def test_the_fiber_table_covers_the_eleven_incidences_once_and_the_ten_blocked_rows() -> None:
    slugs = [slug for fiber in fi.FIBER_TABLE for slug in fiber.slugs]
    _same(sorted(slugs), sorted(spec.slug for spec in fi.fiber_inputs.SPECS))
    incidences = {fi.fiber_inputs.SPEC_BY_SLUG[slug].incidence for slug in slugs}
    _same(set(_nullity16_rows()) <= incidences, True)
    _same(incidences - set(_nullity16_rows()), {"E8bar->VB"})


def test_every_declared_fiber_agrees_with_the_retained_hilbert_rows_and_ledger_statuses() -> None:
    fibers, stalled = fi.static_blocks()
    _same([row["fiber"] for row in fibers if not row["sources_agree"]], [])
    _same(stalled["match"], True)
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same(record["fibers"], fibers)
    _same(record["pass"], True)


def test_a_wrong_degree_a_wrong_component_and_a_wrong_cohen_macaulay_flag_are_each_rejected() -> None:
    rows, cm = fi._jsonl(fi.HILBERT), fi._jsonl(fi.COHEN_MACAULAY)
    iso = FIBER["Iso"]
    _same(fi.hilbert_block(iso, rows, cm)["rows_match_declared_values"], True)
    _same(fi.hilbert_block(dataclasses.replace(iso, degree=24), rows, cm)["rows_match_declared_values"], False)
    w8 = dataclasses.replace(FIBER["W8"], components=((5, 20), (5, 31)))
    _same(fi.hilbert_block(w8, rows, cm)["top_dimensional_component_degrees_sum_to_the_degree"], False)
    e8 = dataclasses.replace(FIBER["E8bar into N"], cohen_macaulay=True)
    _same(fi.hilbert_block(e8, rows, cm)["cohen_macaulay_rows_match"], False)
    unlabeled = dataclasses.replace(iso, hilbert_labels=("no such fiber",))
    _same(fi.hilbert_block(unlabeled, rows, cm)["rows_match_declared_values"], False)


def test_a_changed_ledger_status_fails_the_fiber_row() -> None:
    statuses = fi.ledger_statuses()
    rows, cm = fi._jsonl(fi.HILBERT), fi._jsonl(fi.COHEN_MACAULAY)
    _same(fi.fiber_row(FIBER["E8bar into N"], statuses, rows, cm)["sources_agree"], True)
    promoted = {**statuses, "A5-009": "proved"}
    _same(fi.fiber_row(FIBER["E8bar into N"], promoted, rows, cm)["sources_agree"], False)
    _same(fi._status_block((("A5-000", "proved"),), statuses)[0]["match"], False)


def test_a_header_row_rejects_a_changed_digest_a_changed_selection_and_a_changed_stage() -> None:
    nullity16 = _nullity16_rows()
    cells = _retained_cells("iso-nm")
    good = fi.incidence_row("iso-nm", regenerated=cells, nullity16=nullity16)
    _same((good["all_cells_identical"], good["one_selection_at_every_cell"], good["record_agrees"]), (True, True, True))
    first = (32009, 10754)
    digest = {**cells, first: {"iso-nm": {**cells[first]["iso-nm"], "header_sha256": "0" * 64}}}
    _same(fi.incidence_row("iso-nm", regenerated=digest, nullity16=nullity16)["all_cells_identical"], False)
    moved = [*cells[first]["iso-nm"]["selected_indices_one_based"][:-1], 126]
    selection = {**cells, first: {"iso-nm": {**cells[first]["iso-nm"], "selected_indices_one_based": moved}}}
    row = fi.incidence_row("iso-nm", regenerated=selection, nullity16=nullity16)
    _same((row["one_selection_at_every_cell"], row["record_agrees"]), (False, False))
    staged = {**nullity16, "Iso->N-": {**nullity16["Iso->N-"], "blocked_stage": "nakayama_count"}}
    _same(fi.incidence_row("iso-nm", regenerated=cells, nullity16=staged)["record_agrees"], False)
    fewer = {**nullity16, "Iso->N-": {**nullity16["Iso->N-"], "embedding_rank": 16}}
    _same(fi.incidence_row("iso-nm", regenerated=cells, nullity16=fewer)["record_agrees"], False)


def test_every_retained_header_carries_the_digest_the_record_binds() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    cells = [cell for row in record["incidences"] for cell in row["cells"]]
    _same(len(cells), 31)
    _same([cell["header"] for cell in cells if fi._sha256(ROOT / cell["header"]) != cell["header_sha256"]], [])
    _same(all(cell["identical"] for cell in cells), True)


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        fi._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="conjugate-root"):
        fi._self_test({"pass": True, "mutation_control": {"detected": False}})


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(fi._record_bytes(fi.build_record()), RECORD.read_bytes())
