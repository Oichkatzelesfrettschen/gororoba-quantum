"""Contracts of the pathion evidence table: row counts per retained input, one known reading per platform, the
agreement of the IBM per-output ratios with the reference reader the Tuna-17 series scored against, and the
byte-identical CSV on a rerun.

Each test reads the retained record it names (the files are read, never replayed) and compares one value with the
number printed in results/live/PATHION_KERNEL_MAP_FINDINGS.md or in a ledger row.
"""

from __future__ import annotations

import json
import math
from functools import cache
from pathlib import Path
from typing import Any

import pytest

import pathion_evidence_table as pet

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "results/live"
QI = ROOT / "results/quantum_inspire"
QUANDELA = ROOT / "results/quandela/runs"
KERNEL_MAP = "2026-11-06T183538.809814Z"
MARRAKESH_COSET = "2026-11-06T200832.558771Z"
KINGSTON_PARALLEL = "2026-11-07T042346.084449Z"
FOUR_TERM_QPU = "2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
FOUR_TERM_SIM = "2026-11-06T215025Z-sim_ascella-ascella_pathion_four_term_blocks-sim-00"
PAIRS_QPU = "2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
PAIRS_SIM = "2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00"


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _close(value: float | None, expected: float, tolerance: float, message: str) -> None:
    _check(value is not None and abs(value - expected) <= tolerance, f"{message}: {value} against {expected}")


@cache
def _ledger() -> list[dict[str, str]]:
    return pet.parse_ledger((ROOT / "docs/evidence/a5-exceptional-fibers/ledger.tsv").read_text(encoding="utf-8"))


@cache
def _classes_and_operands() -> tuple[dict[tuple[str, int], str], dict[str, str]]:
    source = QUANDELA / FOUR_TERM_QPU
    analysis = json.loads((source / "analysis.json").read_text(encoding="utf-8"))
    operands = json.loads((source / "cases.json").read_text(encoding="utf-8"))["operands"]
    return pet.class_table(analysis), {name: pet.terms_text(terms) for name, terms in operands.items()}


@cache
def _ibm(directory: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    classes, operands = _classes_and_operands()
    group = pet.find_group(json.loads((LIVE / directory / "collect.json").read_text(encoding="utf-8")))
    ideal, laws = pet.ideal_inputs(group["group"])
    run_dir = f"results/live/{directory}"
    source_file = f"{run_dir}/collect.json"
    summary = pet.ibm_summary_rows(
        group,
        ideal,
        run_dir=run_dir,
        source_file=source_file,
        four_term_operands=operands,
        block_classes=classes,
        ledger=_ledger(),
    )
    bins = pet.ibm_bin_rows(group, laws, ideal, run_dir=run_dir, source_file=source_file, ledger=_ledger())
    return summary, bins


@cache
def _quandela(name: str) -> list[dict[str, Any]]:
    classes, _ = _classes_and_operands()
    analysis = json.loads((QUANDELA / name / "analysis.json").read_text(encoding="utf-8"))
    operands = json.loads((QUANDELA / name / "cases.json").read_text(encoding="utf-8"))["operands"]
    return pet.ascella_rows(
        analysis,
        operands,
        run_dir=f"results/quandela/runs/{name}",
        source_file=f"results/quandela/runs/{name}/analysis.json",
        classes=classes,
        ledger=_ledger(),
    )


@cache
def _tuna() -> list[dict[str, Any]]:
    analysis = QI / "pathion_coset_coin_tuna_17_analysis.json"
    manifest = QI / "cases/pathion_coset_coin_tuna_17/batch-00/cases.json"
    return pet.tuna_rows(
        json.loads(analysis.read_text(encoding="utf-8")),
        json.loads(manifest.read_text(encoding="utf-8")),
        run_dir="results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json",
        source_file="results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json",
        ledger=_ledger(),
        stopped_run_dir="results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json",
    )


def _pick(rows: list[dict[str, Any]], **fields: Any) -> list[dict[str, Any]]:
    return [r for r in rows if all(r[k] == v for k, v in fields.items())]


def _one(rows: list[dict[str, Any]], **fields: Any) -> dict[str, Any]:
    found = _pick(rows, **fields)
    _check(len(found) == 1, f"{fields} matches {len(found)} rows")
    return found[0]


def test_ibm_kernel_map_rows_and_the_nullity_of_the_ledger() -> None:
    summary, bins = _ibm(KERNEL_MAP)
    _check((len(summary), len(bins)) == (214, 704), f"row counts {(len(summary), len(bins))}")
    n_hat = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="raw")
    _close(n_hat["measured"], 12.65, 0.005, "A5-180 N_hat of e1+e18")
    _check(n_hat["ideal"] == 12.0 and n_hat["ledger_row"] == "A5-179;A5-180", "ideal and ledger rows of the kernel map")
    _check(n_hat["backend"] == "ibm_fez" and n_hat["standard_error"] is not None, "backend and standard error")
    twin = _one(summary, observable="N_hat", operand="e17-e2", control="twin", block=None, calibration="raw")
    _close(twin["measured"], 11.87, 0.005, "A5-180 N_hat of the twin")
    skeleton = _one(summary, observable="skeleton_p0", calibration="raw")
    _check(
        abs(skeleton["ideal"] - 1.0) < 1e-9 and skeleton["measured"] is not None and skeleton["measured"] > 0.97,
        "skeleton",
    )
    undefined = [r for r in summary + bins if r["status"] == "undefined"]
    _check(len(undefined) == 2 and all(r["observable"] == "contrast_ratio" for r in undefined), "undefined readings")


def test_ibm_coset_map_rows_and_the_marrakesh_reading_of_the_findings() -> None:
    summary, bins = _ibm(MARRAKESH_COSET)
    _check((len(summary), len(bins)) == (306, 512), f"row counts {(len(summary), len(bins))}")
    raw = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="raw")
    corrected = _one(
        summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="readout_corrected"
    )
    _close(raw["measured"], 12.02, 0.005, "Marrakesh e1+e18 raw N_hat")
    _close(corrected["measured"], 11.99, 0.005, "Marrakesh e1+e18 corrected N_hat")
    _check(corrected["standard_error"] is None and corrected["readout_corrected"], "a corrected value carries no error")
    _check(raw["n_replicas"] == 11 and raw["ledger_row"] == "A5-182", "replica count and ledger row")
    free = _one(summary, observable="N_hat", control="cocycle-free", block=None, calibration="readout_corrected")
    _close(free["measured"], -1.85, 0.005, "Marrakesh cocycle-free corrected N_hat")
    block = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block="k0", calibration="raw")
    _check(block["block_class"].startswith("nullity-"), "a two-term block carries its nullity class")


def test_ibm_per_output_ratios_equal_the_reference_reader_of_the_tuna_series() -> None:
    import qi_pathion_coset_block_cases as cases

    _, bins = _ibm(MARRAKESH_COSET)
    reference = cases.ibm_reference("ibm_marrakesh")
    worst = 0.0
    for tag, operand in (("e1pe18", "e1+e18"), ("e1pe26", "e1+e26"), ("e1pe17", "e1+e17")):
        by_label = reference[tag]["labels"]
        rows = _pick(bins, observable="output_ratio", operand=operand, calibration="raw")
        rows = [r for r in rows if r["control"] in ("primary", "null")]
        _check(sorted(r["label"] for r in rows) == list(range(32)), f"{operand}: the blocks cover 32 labels once")
        for row in rows:
            entry = by_label[row["label"]]
            worst = max(worst, abs(entry["ratio"] - row["measured"]), abs(entry["se_mean"] - row["standard_error"]))
    _check(worst < 1e-12, f"ratio and standard error differ from ibm_reference by {worst}")


def test_ibm_parallel_coset_rows_carry_the_four_term_levels_ascella_reads() -> None:
    summary, bins = _ibm(KINGSTON_PARALLEL)
    _check((len(summary), len(bins)) == (742, 512), f"row counts {(len(summary), len(bins))}")
    level = _one(summary, observable="level", block="B12/2", arm="T", calibration="raw")
    _check(level["block_class"] == "census-13119" and level["operand"] == "e1+e10+e20+e31", "census class and operand")
    _close(level["ideal"], 0.75, 1e-12, "ideal top level of B12/2")
    _check(level["ledger_row"] is None, "the parallel-coset runs have no ledger row yet")


def test_tuna_rows_reproduce_the_coin_series_findings_and_the_stored_differences() -> None:
    rows = _tuna()
    _check(len(rows) == 226, f"{len(rows)} rows")
    selector = _one(
        rows,
        observable="selector_contrast",
        block="ba",
        run_dir="results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json",
    )
    _close(selector["measured"], 0.2350, 5e-5, "ba selector contrast")
    _close(selector["standard_error"], 0.0038, 5e-5, "ba selector standard error")
    xor = _one(rows, observable="selector_contrast", block="xor_ba")
    _close(xor["measured"], -0.7181, 5e-5, "cocycle-free selector contrast")
    _check(
        xor["control"] == "cocycle-free" and selector["ledger_row"] == "A5-184;A5-185;A5-187", "control and ledger rows"
    )
    stopped = _one(
        rows,
        observable="selector_contrast",
        run_dir="results/quantum_inspire/pathion_coset_block_tuna_17_analysis.json",
    )
    _close(stopped["measured"], 0.0167, 5e-5, "stopped series null selector contrast")
    differences = _pick(
        rows, observable="D_y", calibration="readout_corrected", block="ba", reference_backend="ibm_fez"
    )
    within = sum(abs(r["measured"]) <= 3.0 * r["standard_error"] for r in differences)
    _check(len(differences) == 8 and within == 5, f"{within} of {len(differences)} ba bins within 3 se of ibm_fez")


def test_ascella_rows_per_run_and_the_findings_readings() -> None:
    counts = {name: len(_quandela(name)) for name in (FOUR_TERM_QPU, FOUR_TERM_SIM, PAIRS_QPU, PAIRS_SIM)}
    _check(counts == {FOUR_TERM_QPU: 132, FOUR_TERM_SIM: 132, PAIRS_QPU: 184, PAIRS_SIM: 184}, f"row counts {counts}")
    top = _one(_quandela(FOUR_TERM_QPU), setting="c8-4", arm="T", calibration="anchor_dark_normalized")
    _close(top["measured"], 0.6311, 5e-5, "qpu C8 block 4 T level")
    _close(top["ideal"] - top["measured"], 0.0234, 5e-5, "the 0.0234 shortfall of C8 block 4")
    _check(top["dimension"] == 32 and top["block_class"] == "census-4415", "dimension and census class")
    _check(top["ledger_row"] == "A5-188" and top["standard_error"] is None, "ledger row; no standard error stored")
    mirrors = _pick(_quandela(PAIRS_QPU), observable="mirror_difference")
    _check(len(mirrors) == 46 and sum(r["measured"] > 0.07 for r in mirrors) == 9, "9 of 46 mirrors fail on the QPU")
    simulated = _pick(_quandela(PAIRS_SIM), observable="mirror_difference")
    _check(max(r["measured"] for r in simulated) < 0.0067, "no simulator mirror difference exceeds 0.0066")
    _check(_pick(_quandela(PAIRS_SIM), observable="level")[0]["ledger_row"] is None, "sim:ascella cites no ledger row")


def test_csv_bytes_are_deterministic_and_round_trip() -> None:
    rows = _quandela(PAIRS_QPU) + _quandela(FOUR_TERM_QPU) + _tuna()
    first = pet.render_csv(rows)
    second = pet.render_csv(list(reversed(rows)))
    _check(first == second, "the CSV depends on the order of its input rows")
    _check("\r" not in first and first.endswith("\n"), "the CSV is LF-terminated")
    parsed = pet.parse_table(first)
    _check(len(parsed) == len(rows), "a row was lost in the round trip")
    _check(pet.render_csv(parsed) == first, "the parsed table does not render to the same bytes")
    header = first.splitlines()[0].split(",")
    _check(tuple(header) == pet.COLUMNS, "the header differs from COLUMNS")
    for row in parsed:
        _check(row["measured"] is None or math.isfinite(row["measured"]), "a non-finite measured value was written")


def test_row_builder_rejects_unknown_columns_and_a_missing_ideal() -> None:
    with pytest.raises(ValueError, match="unknown columns"):
        pet.make_row(run_dir="x", colour="red")
    with pytest.raises(ValueError, match="no ideal"):
        pet.make_row(run_dir="x", observable="level", measured=0.5)
    row = pet.make_row(run_dir="x", observable="level", measured=float("nan"))
    _check(row["status"] == "undefined" and row["measured"] is None, "a non-finite reading is undefined")


def test_ledger_citation_matches_the_run_directory_and_its_files() -> None:
    ledger = [
        {"id": "A5-1", "evidence": "results/live/RUN/collect.json;docs/x.md"},
        {"id": "A5-2", "evidence": "results/live/RUN2/collect.json"},
        {"id": "A5-3", "evidence": "results/live/RUN"},
    ]
    _check(pet.ledger_cites(ledger, "results/live/RUN") == "A5-1;A5-3", "citation by directory or file")
    _check(pet.ledger_cites(ledger, "results/live/NONE") == "", "no citation")


def test_key_parser_names_every_family_and_refuses_an_unknown_key() -> None:
    nullity = {"cmap_e1pe17": 0.0}
    operands = {"B12": "e1+e10+e20+e31"}
    cases = {
        "cmap_e1pe17_k4_nullity_estimate": ("N_hat", "null", "k4"),
        "cmap_twin_e17me2_k0_visibility": ("visibility", "twin", "k0"),
        "cmap_xor_e1pe18_nullity_estimate": ("N_hat", "cocycle-free", ""),
        "cmap_e1pe18_k8_flip_selector_contrast": ("selector_contrast", "readout-flip", "k8"),
        "kmap_flip3_e1pe18_contrast": ("selector_contrast", "mutation", ""),
        "ftb_B12_c2_closure_N": ("closure", "mutation", "B12/2"),
        "ftb_B12_c2_level_E0": ("level", "null", "B12/2"),
    }
    for key, (observable, control, block) in cases.items():
        parsed = pet.parse_key(key, nullity, operands)
        if parsed is None:
            raise AssertionError(f"{key} did not parse")
        _check((parsed.observable, parsed.control, parsed.block) == (observable, control, block), f"{key}: {parsed}")
    _check(pet.parse_key("cmap_e1pe18_k8_nullity_ideal", nullity, operands) is None, "ideal-only keys are skipped")
    with pytest.raises(ValueError, match="unparsed"):
        pet.parse_key("zmap_e1pe18_contrast", nullity, operands)
