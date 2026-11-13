"""Fibers of the incidences from nullity 8 into nullity 16 and of E8bar->VB, imported from the exceptional-fiber record.

The nullity-16 Rees record completes the Nakayama count and the embedding of ten incidences from the nullity-8 sources
and stops at the elimination of the modular special fiber. The special fiber of the Rees algebra of the Nakayama
generator ideal (G) on the germ V(J) is Proj F, F = sum_d (G)^d / m (G)^d, the fiber cone that
`../a5-exceptional-fibers` determines degree by degree from the headers `fiber_inputs.py` emits. Both computations
read one phase-one script (`nullity16_rees_fibers._phase_one_script`), so the header is the identification: this
producer regenerates every header at three (prime, root of -1) cells, compares it byte for byte with the file the
exceptional-fiber record computed from, checks that the selected coordinates are those of the nullity-16 record, and
binds the Hilbert data, the Cohen-Macaulay data and the deciding ledger rows of each fiber. The record states for
each incidence the fiber, the degrees in which F = k[y]/K2 is decided, and the characteristics that carry it; it
decides no new degree and no new characteristic.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import fiber_inputs  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-nullity8-fiber-import-v1"
FIBERS = ROOT / "docs" / "evidence" / "a5-exceptional-fibers"
HEADERS = FIBERS / "working" / "build" / "inputs"
LEDGER = FIBERS / "ledger.tsv"
HILBERT = FIBERS / "k2-hilbert.jsonl"
COHEN_MACAULAY = FIBERS / "k2-cm.jsonl"
NULLITY16_RESULT = HERE / "nullity16-rees-fibers-result.json"
# The (prime, root of -1) cells with retained headers; 21255 = -10754 modulo 32009 is the conjugate embedding.
CELLS = ((32009, 10754), (32009, 21255), (32029, 9115))
MUTATION_CELLS = ((32009, 10754), (32009, 21255))
HILBERT_DEGREES = tuple(str(degree) for degree in range(1, 8))


@dataclass(frozen=True)
class Fiber:
    """One fiber cone and the incidences that carry it, with the values the retained records must reproduce."""

    name: str
    slugs: tuple[str, ...]
    hilbert_labels: tuple[str, ...]  # `fiber` values of k2-hilbert.jsonl; empty where the ring is polynomial
    generators: int
    quadrics: int
    projective_dimension: int
    degree: int
    components: tuple[tuple[int, int], ...]  # (projective dimension, degree) of the reduced components
    cohen_macaulay: bool | None
    decided_degrees: str
    modular_rows: tuple[tuple[str, str], ...]  # (ledger id, status) that decide F = k[y]/K2 over F_p
    geometry_rows: tuple[tuple[str, str], ...]
    sign_rows: tuple[tuple[str, str], ...]
    characteristic_zero: str
    characteristic_zero_rows: tuple[tuple[str, str], ...]
    open_items: tuple[str, ...]
    # (`fiber` label, prime) of every retained row of k2-hilbert.jsonl and of k2-cm.jsonl, a repeated cell once per row.
    hilbert_cells: tuple[tuple[str, int], ...] = ()


FIBER_TABLE = (
    Fiber(
        "X opposite sign",
        ("xp-nm", "xm-np"),
        (),
        3,
        0,
        2,
        1,
        ((2, 1),),
        True,
        "every degree",
        (("A5-001", "proved"),),
        (),
        (("A5-023", "proved"),),
        "decided: F = Q(i)[y1, y2, y3]",
        (("A5-270", "proved"),),
        (),
    ),
    Fiber(
        "X same sign",
        ("xp-np", "xm-nm"),
        ("X+", "X-"),
        15,
        69,
        3,
        12,
        ((3, 12),),
        False,
        "every degree",
        (("A5-304", "proved"),),
        (("A5-022", "proved"), ("A5-303", "proved"), ("A5-297", "survives")),
        (("A5-013", "proved"),),
        "decided: F = Q(i)[y]/L with L of 69 quadrics reducing to K2",
        (("A5-305", "proved"), ("A5-306", "proved"), ("A5-314", "proved")),
        (
            "no retained K2 of X+->N+ at 32009; the sign map carries X-->N- there",
            "irreducibility and degree 12 of the reduced fiber are proved at 32009 for X-->N- (A5-022) and survive "
            "elsewhere (A5-297)",
        ),
        (("X+", 32029), ("X-", 32009), ("X-", 32029)),
    ),
    Fiber(
        "Iso",
        ("iso-np", "iso-nm"),
        ("Iso",),
        17,
        68,
        4,
        23,
        ((4, 23),),
        True,
        "every degree",
        (("A5-007", "proved"), ("A5-067", "proved")),
        (("A5-058", "proved"), ("A5-059", "proved"), ("A5-060", "proved")),
        (("A5-013", "proved"),),
        "open: dimension at least 5 and the 68 quadrics over Q(i); equality of the fiber with V(K2) undecided",
        (("A5-293", "survives"), ("A5-294", "survives")),
        ("the fiber cone over Q(i) in every degree",),
        (("Iso", 32009), ("Iso", 32009), ("Iso", 32029)),
    ),
    Fiber(
        "W8",
        ("w8-np", "w8-nm"),
        ("W8 -> N-",),
        24,
        144,
        5,
        50,
        ((5, 20), (5, 30)),
        True,
        "every degree",
        (("A5-008", "proved"), ("A5-066", "proved")),
        (("A5-061", "proved"), ("A5-062", "proved")),
        (("A5-013", "proved"), ("A5-025", "proved")),
        "open: dimension at least 6; the quadrics over Q(i) are not computed",
        (("A5-293", "survives"), ("A5-277", "survives")),
        ("the fiber cone over Q(i), starting with its quadrics",),
        (("W8 -> N-", 32009), ("W8 -> N-", 32029)),
    ),
    Fiber(
        "E8bar into N",
        ("e8-np", "e8-nm"),
        ("E8-bar -> N+", "E8-bar -> N-"),
        21,
        148,
        4,
        11,
        ((3, 4), (4, 11)),
        False,
        "degrees 1 to 7",
        (("A5-009", "survives"), ("A5-335", "proved"), ("A5-339", "proved")),
        (("A5-252", "proved"), ("A5-312", "proved")),
        (("A5-013", "proved"), ("A5-326", "proved")),
        "open: h_d is bounded below by the modular values for d at most 7",
        (("A5-346", "proved"),),
        (
            "a generator of the defining ideal in degree 8 or above",
            "the 148 quadrics over Q(i)",
        ),
        (("E8-bar -> N+", 32009), ("E8-bar -> N+", 32029), ("E8-bar -> N-", 32009), ("E8-bar -> N-", 32029)),
    ),
    Fiber(
        "E8bar into VB",
        ("e8-vb",),
        ("E8-bar -> VB",),
        10,
        21,
        3,
        7,
        ((3, 3), (3, 4)),
        True,
        "every degree",
        (("A5-005", "proved"), ("A5-015", "proved"), ("A5-016", "proved")),
        (("A5-017", "proved"), ("A5-010", "proved")),
        (),
        "open: the 21 quadrics over Q(i) reduce to K2 at 32029",
        (("A5-315", "survives"),),
        ("the fiber cone over Q(i) in every degree",),
        (("E8-bar -> VB", 32009), ("E8-bar -> VB", 32029)),
    ),
)
SLUG_FIBER = {slug: fiber for fiber in FIBER_TABLE for slug in fiber.slugs}
STALLED_ROW = ("A5-409", "stalled")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _cell_directory(cell: tuple[int, int]) -> Path:
    return HEADERS / f"p{cell[0]}-r{cell[1]}"


def retained_slugs(cell: tuple[int, int]) -> tuple[str, ...]:
    directory = _cell_directory(cell)
    return tuple(spec.slug for spec in fiber_inputs.SPECS if (directory / f"{spec.slug}.sing").exists())


def regenerate_cell(cell: tuple[int, int]) -> dict[str, dict[str, Any]]:
    """Emit every retained header of one cell from the producer and return its digest and selection per slug."""
    prime, root = cell
    with tempfile.TemporaryDirectory() as scratch:
        receipt = fiber_inputs.run(prime, root, retained_slugs(cell), Path(scratch), do_compare=False)
    return {
        str(row["slug"]): {
            "header_sha256": str(row["header_sha256"]),
            "generator_count": int(row["generator_count"]),
            "selected_indices_one_based": [int(value) for value in row["selected_indices_one_based"]],
        }
        for row in receipt["incidences"]
    }


def ledger_statuses() -> dict[str, str]:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return {row["id"]: row["status"] for row in csv.DictReader(handle, delimiter="\t", quoting=csv.QUOTE_NONE)}


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def hilbert_block(fiber: Fiber, rows: list[dict[str, Any]], cm_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The retained Hilbert and Cohen-Macaulay rows of a fiber, with their agreement with the declared values."""
    mine = [row for row in rows if row["fiber"] in fiber.hilbert_labels]
    cm = [row for row in cm_rows if row["fiber"] in fiber.hilbert_labels]
    expected_cells = sorted(fiber.hilbert_cells)
    functions = {tuple(int(row["h"][degree]) for degree in HILBERT_DEGREES) for row in mine}
    values_match = all(
        (int(row["generators"]), int(row["quadrics"]), int(row["projdim"]), int(row["degree"]))
        == (fiber.generators, fiber.quadrics, fiber.projective_dimension, fiber.degree)
        for row in mine
    )
    top_degree = sum(degree for dimension, degree in fiber.components if dimension == fiber.projective_dimension)
    return {
        "cells": sorted([str(row["fiber"]), int(row["prime"]), str(row["relations_sha256"])] for row in mine),
        "hilbert_function_degrees_1_to_7": [list(function) for function in sorted(functions)],
        "rows_match_declared_values": values_match
        and len(functions) <= 1
        and sorted((str(row["fiber"]), int(row["prime"])) for row in mine) == expected_cells,
        "cohen_macaulay_rows": sorted(
            [str(row["fiber"]), int(row["prime"]), bool(row["cohen_macaulay"])] for row in cm
        ),
        "cohen_macaulay_rows_match": sorted((str(row["fiber"]), int(row["prime"])) for row in cm) == expected_cells
        and all(bool(row["cohen_macaulay"]) == fiber.cohen_macaulay for row in cm),
        "top_dimensional_component_degrees_sum_to_the_degree": top_degree == fiber.degree,
    }


def _status_block(pairs: tuple[tuple[str, str], ...], statuses: dict[str, str]) -> list[dict[str, Any]]:
    return [
        {"id": row, "declared_status": status, "ledger_status": statuses.get(row), "match": statuses.get(row) == status}
        for row, status in pairs
    ]


def incidence_row(
    slug: str,
    *,
    regenerated: dict[tuple[int, int], dict[str, dict[str, Any]]],
    nullity16: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Header identity of one incidence at every cell, and its agreement with the nullity-16 record."""
    spec = fiber_inputs.SPEC_BY_SLUG[slug]
    fiber = SLUG_FIBER[slug]
    cells = []
    for cell in CELLS:
        path = _cell_directory(cell) / f"{slug}.sing"
        if not path.exists():
            continue
        emitted = regenerated[cell][slug]
        cells.append(
            {
                "prime": cell[0],
                "i_root": cell[1],
                "header": _relative(path),
                "header_sha256": _sha256(path),
                "regenerated_sha256": emitted["header_sha256"],
                "identical": emitted["header_sha256"] == _sha256(path),
                "generator_count": emitted["generator_count"],
                "selected_indices_one_based": emitted["selected_indices_one_based"],
            }
        )
    # The selection order fixes the generator order of the header, so cells are compared as ordered lists.
    selections = {tuple(cell["selected_indices_one_based"]) for cell in cells}
    counts = {int(cell["generator_count"]) for cell in cells}
    blocked = nullity16.get(spec.incidence)
    row: dict[str, Any] = {
        "incidence": spec.incidence,
        "slug": slug,
        "fiber": fiber.name,
        "cells": cells,
        "all_cells_identical": bool(cells) and all(bool(cell["identical"]) for cell in cells),
        "one_selection_at_every_cell": len(selections) == 1,
        "generator_count_matches_fiber": counts == {fiber.generators},
    }
    if blocked is None:
        # E8bar->VB is a nullity-12 boundary: its header comes from the Nakayama route and has no nullity-16 row.
        row["nullity16_record"] = None
        row["record_agrees"] = spec.route == "nakayama"
        return row
    chosen = [int(value) for value in blocked["chosen_coordinate_indices_one_based"]]
    row["nullity16_record"] = {
        "status": blocked["status"],
        "blocked_stage": blocked.get("blocked_stage"),
        "nakayama_generator_count": int(blocked["nakayama_generator_count"]),
        "embedding_rank": int(blocked["embedding_rank"]),
        "chosen_coordinate_indices_one_based": chosen,
    }
    row["record_agrees"] = (
        blocked["status"] == "blocked_timeout"
        and blocked.get("blocked_stage") == "modular_rees_fiber"
        and int(blocked["nakayama_generator_count"]) == fiber.generators == int(blocked["embedding_rank"])
        and selections == {tuple(chosen)}
    )
    return row


BLOCKS = ("modular_rows", "geometry_rows", "sign_rows", "characteristic_zero_rows")


def fiber_row(fiber: Fiber, statuses: dict[str, str], rows: list[dict[str, Any]], cm: list[dict[str, Any]]) -> dict:
    blocks = {key: _status_block(getattr(fiber, key), statuses) for key in BLOCKS}
    hilbert = hilbert_block(fiber, rows, cm)
    return {
        "fiber": fiber.name,
        "incidences": [fiber_inputs.SPEC_BY_SLUG[slug].incidence for slug in fiber.slugs],
        "generators": fiber.generators,
        "quadrics": fiber.quadrics,
        "projective_dimension": fiber.projective_dimension,
        "degree": fiber.degree,
        "reduced_components_projective_dimension_degree": [list(pair) for pair in fiber.components],
        "cohen_macaulay": fiber.cohen_macaulay,
        "fiber_cone_equals_quotient_by_quadrics_in": fiber.decided_degrees,
        "modular_primes": [32009, 32029],
        "characteristic_zero": fiber.characteristic_zero,
        "open_items": list(fiber.open_items),
        "hilbert": hilbert,
        **blocks,
        "sources_agree": all(bool(entry["match"]) for block in blocks.values() for entry in block)
        and bool(hilbert["rows_match_declared_values"])
        and bool(hilbert["cohen_macaulay_rows_match"])
        and bool(hilbert["top_dimensional_component_degrees_sum_to_the_degree"]),
    }


def static_blocks() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The fiber rows and the stalled-row check: the part of the record that reads retained files only."""
    statuses = ledger_statuses()
    rows = _jsonl(HILBERT)
    cm = _jsonl(COHEN_MACAULAY)
    fibers = [fiber_row(fiber, statuses, rows, cm) for fiber in FIBER_TABLE]
    return fibers, _status_block((STALLED_ROW,), statuses)[0]


def build_record() -> dict[str, Any]:
    regenerated = dict(zip(CELLS, parallel.ordered_map(regenerate_cell, CELLS, min_items=len(CELLS) + 1), strict=True))
    record16 = json.loads(NULLITY16_RESULT.read_text(encoding="utf-8"))
    nullity16 = {str(row["incidence"]): row for row in record16["incidences"] if row["status"] != "completed"}
    slugs = tuple(spec.slug for spec in fiber_inputs.SPECS)
    incidences = [incidence_row(slug, regenerated=regenerated, nullity16=nullity16) for slug in slugs]
    fibers, stalled = static_blocks()
    first, conjugate = MUTATION_CELLS
    shared = sorted(set(regenerated[first]) & set(regenerated[conjugate]))
    # The conjugate embedding of Q(i) is a different header at every incidence whose G involves the root.
    conjugate_differs = [
        slug
        for slug in shared
        if regenerated[conjugate][slug]["header_sha256"] != _sha256(_cell_directory(first) / f"{slug}.sing")
    ]
    covered = {row["incidence"] for row in incidences}
    baseline = (
        all(bool(row["all_cells_identical"]) for row in incidences)
        and all(bool(row["one_selection_at_every_cell"]) for row in incidences)
        and all(bool(row["generator_count_matches_fiber"]) for row in incidences)
        and all(bool(row["record_agrees"]) for row in incidences)
        and set(nullity16) <= covered
        and len(nullity16) == 10
        and all(bool(row["sources_agree"]) for row in fibers)
        and bool(stalled["match"])
    )
    inputs = (
        Path(fiber_inputs.__file__),
        Path(fiber_inputs.rees.__file__),
        Path(fiber_inputs.nakayama.__file__),
        Path(fiber_inputs.basepoints.__file__),
        NULLITY16_RESULT,
        HILBERT,
        COHEN_MACAULAY,
        Path(__file__),
    )
    return {
        "schema": SCHEMA,
        "inputs": {_relative(path.resolve()): _sha256(path) for path in inputs},
        "scope": {
            "statement": (
                "For each of the ten incidences from a nullity-8 source into N+ or N-, and for E8bar->VB, the special "
                "fiber of the Nakayama-reduced Rees algebra is Proj of the fiber cone the exceptional-fiber record "
                "determines from the same header; the fiber, the degrees decided and the characteristics are those "
                "of the ledger rows named in each fiber row."
            ),
            "claim_boundary": (
                "The record regenerates headers and reads retained Hilbert rows and ledger statuses. It recomputes "
                "no quadric ideal, no Hilbert function and no decomposition, decides no degree and no "
                "characteristic beyond the named rows, and computes no kernel-plane map."
            ),
        },
        "incidences": incidences,
        "fibers": fibers,
        "stalled_elimination_row": stalled,
        "summary": {
            "incidence_count": len(incidences),
            "header_cells_regenerated": sum(len(row["cells"]) for row in incidences),
            "header_cells_identical": sum(bool(cell["identical"]) for row in incidences for cell in row["cells"]),
            "fibers_decided_in_every_degree_at_both_primes": [
                row["fiber"] for row in fibers if row["fiber_cone_equals_quotient_by_quadrics_in"] == "every degree"
            ],
            "fibers_decided_in_characteristic_zero": [
                row["fiber"] for row in fibers if str(row["characteristic_zero"]).startswith("decided")
            ],
        },
        "mutation_control": {
            "name": "conjugate_root_of_minus_one",
            "input_change": "regenerate at i = 21255 and compare with the retained header at i = 10754",
            "headers_compared": len(shared),
            "headers_that_differ": conjugate_differs,
            "detected": len(conjugate_differs) == len(shared) > 0,
        },
        "falsifier": (
            "A regenerated header that differs from the retained file; a selected coordinate set that differs "
            "between cells or from the nullity-16 record; a Hilbert or Cohen-Macaulay row that differs from the "
            "declared fiber; a deciding ledger row whose status has changed; or a header that the conjugate root "
            "reproduces."
        ),
        "pass": baseline and len(conjugate_differs) == len(shared) > 0,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _verdict(record: dict[str, Any]) -> bool:
    """The pass flag recomputed from the cells, flags and blocks the record stores."""
    incidences = record["incidences"]
    control = record["mutation_control"]
    return (
        all(
            bool(cell["identical"]) and cell["regenerated_sha256"] == cell["header_sha256"]
            for row in incidences
            for cell in row["cells"]
        )
        and all(
            bool(row["cells"])
            and len({tuple(cell["selected_indices_one_based"]) for cell in row["cells"]}) == 1
            and bool(row["one_selection_at_every_cell"])
            and bool(row["all_cells_identical"])
            and bool(row["generator_count_matches_fiber"])
            and bool(row["record_agrees"])
            for row in incidences
        )
        and all(
            bool(row["sources_agree"])
            and all(bool(entry["match"]) for key in BLOCKS for entry in row[key])
            and bool(row["hilbert"]["rows_match_declared_values"])
            and bool(row["hilbert"]["cohen_macaulay_rows_match"])
            and bool(row["hilbert"]["top_dimensional_component_degrees_sum_to_the_degree"])
            for row in record["fibers"]
        )
        and bool(record["stalled_elimination_row"]["match"])
        and bool(control["detected"])
        and len(control["headers_that_differ"]) == control["headers_compared"] > 0
    )


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the fiber import record failed")
    _require(bool(record["mutation_control"]["detected"]), "the conjugate-root mutation survived")
    _require(_verdict(record), "the fiber import record disagrees with its own cells and blocks")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        _require(arguments.check.read_bytes() == rendered, f"{arguments.check} differs from the regenerated record")


if __name__ == "__main__":
    main()
