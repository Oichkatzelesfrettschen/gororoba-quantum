"""Import of the nullity-8 fiber cones into the nullity-16 limit-set table: source agreement and its mutations."""

from __future__ import annotations

import copy
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


def test_each_incidence_belongs_to_the_fiber_of_its_source_orbit_and_sign_relation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Fiber assignments swapped between fibers keep the slug and incidence sets but change the source orbit.
    for fiber in fi.FIBER_TABLE:
        for slug in fiber.slugs:
            source, target = fi.fiber_inputs.SPEC_BY_SLUG[slug].incidence.split("->")
            label_sources = {label.split(" ->")[0].replace("-bar", "bar") for label in fiber.hilbert_labels}
            if label_sources:
                _same(source.replace("-bar", "bar") in label_sources, True)
            if fiber.name.startswith("X"):
                same_sign = source[-1] == target[-1]
                _same(same_sign, fiber.name == "X same sign")
    _same(fi.SLUG_FIBER["xp-np"].name, fi.SLUG_FIBER["xm-nm"].name)
    _same(fi.SLUG_FIBER["xp-nm"].name, fi.SLUG_FIBER["xm-np"].name)
    swapped = {
        slug: (FIBER["W8"] if slug.startswith("iso") else FIBER["Iso"] if slug.startswith("w8") else fiber)
        for slug, fiber in fi.SLUG_FIBER.items()
    }
    for slug in ("iso-nm", "w8-nm"):
        cells = _retained_cells(slug)
        good = fi.incidence_row(slug, regenerated=cells, nullity16=_nullity16_rows())
        _same(good["generator_count_matches_fiber"], True)
        monkeypatch.setattr(fi, "SLUG_FIBER", swapped)
        bad = fi.incidence_row(slug, regenerated=cells, nullity16=_nullity16_rows())
        monkeypatch.undo()
        _same((bad["generator_count_matches_fiber"], bad["record_agrees"]), (False, False))


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


def _without(rows: list[dict[str, Any]], fiber: str, prime: int, position: int = 0) -> list[dict[str, Any]]:
    """The rows with the `position`-th row of the (fiber label, prime) cell removed."""
    matching = [index for index, row in enumerate(rows) if (row["fiber"], int(row["prime"])) == (fiber, prime)]
    return [row for index, row in enumerate(rows) if index != matching[position]]


def test_a_missing_hilbert_or_cohen_macaulay_row_fails_the_cell_comparison() -> None:
    rows, cm = fi._jsonl(fi.HILBERT), fi._jsonl(fi.COHEN_MACAULAY)
    for fiber in fi.FIBER_TABLE:
        block = fi.hilbert_block(fiber, rows, cm)
        _same((block["rows_match_declared_values"], block["cohen_macaulay_rows_match"]), (True, True))
        for label, prime in fiber.hilbert_cells:
            fewer = _without(rows, label, prime)
            _same(fi.hilbert_block(fiber, fewer, cm)["rows_match_declared_values"], False)
            _same(fi.hilbert_block(fiber, fewer, cm)["cohen_macaulay_rows_match"], True)
            fewer_cm = _without(cm, label, prime)
            _same(fi.hilbert_block(fiber, rows, fewer_cm)["cohen_macaulay_rows_match"], False)
            _same(fi.hilbert_block(fiber, rows, fewer_cm)["rows_match_declared_values"], True)
    for fiber in fi.FIBER_TABLE[1:]:
        labels = fiber.hilbert_labels
        no_hilbert = [row for row in rows if row["fiber"] not in labels]
        no_cm = [row for row in cm if row["fiber"] not in labels]
        _same(fi.hilbert_block(fiber, no_hilbert, cm)["rows_match_declared_values"], False)
        _same(fi.hilbert_block(fiber, rows, no_cm)["cohen_macaulay_rows_match"], False)


def test_a_duplicated_or_extra_row_fails_the_cell_comparison() -> None:
    rows, cm = fi._jsonl(fi.HILBERT), fi._jsonl(fi.COHEN_MACAULAY)
    iso = FIBER["Iso"]
    # Iso carries two rows at 32009; dropping one of them leaves a different cell multiset.
    _same(fi.hilbert_block(iso, _without(rows, "Iso", 32009, 1), cm)["rows_match_declared_values"], False)
    extra = next(row for row in rows if row["fiber"] == "Iso" and int(row["prime"]) == 32029)
    _same(fi.hilbert_block(iso, [*rows, extra], cm)["rows_match_declared_values"], False)
    extra_cm = next(row for row in cm if row["fiber"] == "Iso" and int(row["prime"]) == 32029)
    _same(fi.hilbert_block(iso, rows, [*cm, extra_cm])["cohen_macaulay_rows_match"], False)
    wrong_prime = [
        {**row, "prime": 32003} if row["fiber"] == "Iso" and int(row["prime"]) == 32029 else row for row in rows
    ]
    _same(fi.hilbert_block(iso, wrong_prime, cm)["rows_match_declared_values"], False)


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
    # The selection order fixes the generator order of the header: a permutation with the same set is a mutation.
    order = cells[first]["iso-nm"]["selected_indices_one_based"]
    permuted = [order[1], order[0], *order[2:]]
    reordered = {**cells, first: {"iso-nm": {**cells[first]["iso-nm"], "selected_indices_one_based": permuted}}}
    row = fi.incidence_row("iso-nm", regenerated=reordered, nullity16=nullity16)
    _same((row["one_selection_at_every_cell"], row["record_agrees"]), (False, False))
    chosen = nullity16["Iso->N-"]["chosen_coordinate_indices_one_based"]
    shuffled = {**nullity16, "Iso->N-": {**nullity16["Iso->N-"], "chosen_coordinate_indices_one_based": chosen[::-1]}}
    _same(fi.incidence_row("iso-nm", regenerated=cells, nullity16=shuffled)["record_agrees"], False)


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


def test_self_test_rejects_a_field_outside_the_pass_and_mutation_flags() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    fi._self_test(record)
    for mutate in (
        lambda r: r["incidences"][0]["cells"][0].update(regenerated_sha256="0" * 64),
        lambda r: r["incidences"][0].update(record_agrees=False),
        lambda r: r["fibers"][0]["modular_rows"][0].update(match=False),
        lambda r: r["fibers"][1]["hilbert"].update(rows_match_declared_values=False),
        lambda r: r["stalled_elimination_row"].update(match=False),
        lambda r: r["mutation_control"]["headers_that_differ"].pop(),
    ):
        broken = copy.deepcopy(record)
        mutate(broken)
        with pytest.raises(RuntimeError, match="disagrees"):
            fi._self_test(broken)


@pytest.mark.audit
def test_the_retained_record_binds_the_current_producer_and_input_digests() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    own = (Path(fi.__file__).resolve().relative_to(ROOT)).as_posix()
    _same(own in record["inputs"], True)
    _same([path for path, digest in record["inputs"].items() if fi._sha256(ROOT / path) != digest], [])
    _same(all(cell["identical"] for row in record["incidences"] for cell in row["cells"]), True)


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(fi._record_bytes(fi.build_record()), RECORD.read_bytes())
