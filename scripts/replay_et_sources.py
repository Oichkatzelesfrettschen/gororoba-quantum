"""Replay exact ET fixtures and unchanged pinned Rust sources in temporary storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

from exact_rank import rank_mod, rational_kernel

import parallel
from cd_core import cd_sign
from et_reference import ETSpec

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "docs/evidence/et_rows"


def check_native_qualification(bundle: Path = BUNDLE) -> None:
    """Bind the readable qualification receipt to its exact submit-free artifacts."""
    receipt = json.loads((bundle / "native_qualification.json").read_text())
    with zipfile.ZipFile(bundle / "native_qualification.zip") as archive:
        if set(archive.namelist()) != {"record.json", "isa.qpy"}:
            raise ValueError("native qualification archive inventory differs")
        artifacts = {name: archive.read(name) for name in archive.namelist()}
    record = json.loads(artifacts["record.json"])
    expected = {
        "schema": "et-native-qualification-v1",
        "quantum_execution": False,
        "source_commit": record["code_commit"],
        "started": record["started"],
        "state": record["state"],
        "artifact_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()},
        "executions": sum(record["pub_shots"].values()),
        "pubs": len(record["execution_pubs"]),
        "selected": record["optimization"]["selected"],
        "retained_candidate": record["optimization"]["retained_candidate"],
        "budget": {key: value for key, value in record["budget_plan"].items() if key != "jobs"},
        "job_tiers": [
            {key: value for key, value in job.items() if key != "pub_names"} for job in record["budget_plan"]["jobs"]
        ],
        "backends": record["backends"],
        "candidates": [
            {key: value for key, value in candidate.items() if key not in ("jobs", "cost_scenarios")}
            for candidate in record["optimization"]["candidates"]
        ],
        "calibrated_screens": record["optimization"]["et_calibrated_candidates"],
        "native_operator_check": record["family_configuration"]["native_operator_check"],
        "compiled_ideal_validation": record["compiled_ideal_validation"],
        "compilation_contract": record["family_configuration"]["compilation_contract"],
        "interpretation": (
            "Current-Target compilation and local noise-model admission; hardware acquisition remains held"
        ),
    }
    if receipt != expected:
        raise ValueError("native qualification receipt differs from its archived record")
    if (
        record["code_commit"]["sources_modified"]
        or record["state"] not in ("planned", "budget_infeasible", "design_infeasible")
        or expected["executions"] != 466944
        or expected["pubs"] != 4656
    ):
        raise ValueError("native qualification violates the frozen-source submit-free acquisition contract")


def verify_native_receipt_guard() -> None:
    """Reject altered execution, selection and acquisition claims even with a new checksum ledger."""
    receipt = json.loads((BUNDLE / "native_qualification.json").read_text())
    with tempfile.TemporaryDirectory(prefix="et-native-receipt-") as temporary:
        bundle = Path(temporary)
        (bundle / "native_qualification.zip").write_bytes((BUNDLE / "native_qualification.zip").read_bytes())
        for key, value in (("quantum_execution", True), ("selected", "invented"), ("executions", 1), ("pubs", 1)):
            (bundle / "native_qualification.json").write_text(json.dumps(receipt | {key: value}))
            try:
                check_native_qualification(bundle)
            except ValueError:
                continue
            raise ValueError(f"altered native receipt passed validation: {key}")


def check_exact_kernel(arguments: tuple[int, int, int]) -> dict[str, int]:
    """Cross-check ET nullity using exact FLINT elimination on the full multiplier."""
    dimension, strut, row = arguments
    spec = ETSpec(dimension, strut, row)
    matrix = [[0] * dimension for _ in range(dimension)]
    for source in range(dimension):
        for left in (spec.row, spec.high):
            matrix[left ^ source][source] += cd_sign(dimension, left, source)
    basis = rational_kernel(matrix)
    rank = rank_mod(matrix, 2147483647)
    if len(basis) != spec.degree or rank + len(basis) != dimension:
        raise ValueError(f"FLINT multiplier rank/nullity differs at {arguments}")
    for vector in basis:
        if any(sum(entry * coefficient for entry, coefficient in zip(image, vector, strict=True)) for image in matrix):
            raise ValueError(f"FLINT kernel vector fails exact substitution at {arguments}")
    return {"dimension": dimension, "strut": strut, "row": row, "rank": rank, "nullity": len(basis)}


def check_table(table: dict) -> tuple[int, int, int, int]:
    dimension, strut = table["dimension"], table["strut"]
    spec = ETSpec(dimension, strut, table["labels"][0])
    if list(spec.tone_row) != table["labels"]:
        raise ValueError("pilot tone-row ordering differs")
    for row, values in zip(table["labels"], table["values"], strict=True):
        reference = ETSpec(dimension, strut, row)
        if [reference.cell(column).value for column in table["labels"]] != values:
            raise ValueError(f"pilot signed cells differ at {dimension}/{strut}/{row}")
        for column in range(reference.generator):
            first, second = reference.block_signs(column)
            occupied = first == second
            if occupied != reference.cell(column).occupied:
                raise ValueError("paired-block occupancy differs, including excluded labels")
            partner = column ^ reference.xor_label
            images = [
                {left ^ source: cd_sign(dimension, left, source) for left in (row, reference.high)}
                for source in (column, partner)
            ]
            diagonal = [sum(value * value for value in image.values()) for image in images]
            off_diagonal = sum(value * images[1].get(label, 0) for label, value in images[0].items())
            if diagonal != [2, 2] or off_diagonal != first + second:
                raise ValueError("exact multiplier-column Gram block differs")
            if occupied and any(
                images[0].get(label, 0) - first * images[1].get(label, 0)
                for label in images[0].keys() | images[1].keys()
            ):
                raise ValueError("occupied block's exact annihilator vector differs")
    return 1, len(table["labels"]) ** 2, table["ordered_addressable"], len(table["labels"]) * dimension // 2


def replay() -> dict:
    integrity = json.loads((BUNDLE / "integrity.json").read_text())
    actual_files = {
        path.relative_to(BUNDLE).as_posix()
        for path in BUNDLE.rglob("*")
        if path.is_file() and path.name != "integrity.json"
    }
    if set(integrity) != actual_files:
        raise ValueError("ET evidence inventory differs from its checksum ledger")
    for name, digest in integrity.items():
        if hashlib.sha256((BUNDLE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"ET evidence checksum differs: {name}")
    check_native_qualification()
    verify_native_receipt_guard()
    pins = json.loads((BUNDLE / "rust_sources.json").read_text())
    for name, record in pins["files"].items():
        if hashlib.sha256((BUNDLE / "rust" / name).read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"immutable canonical source changed: {name}")
    tables = json.loads((BUNDLE / "pilot_et_fixtures.json").read_text())["tables"]
    totals = parallel.ordered_map(check_table, tables, min_items=2)
    counts = {
        "tables": sum(row[0] for row in totals),
        "full_grid": sum(row[1] for row in totals),
        "addressable": sum(row[2] for row in totals),
        "paired_blocks": sum(row[3] for row in totals),
        "basis_products": 0,
        "rust_cells": 0,
    }
    with tempfile.TemporaryDirectory(prefix="et-canonical-") as temporary:
        binary = Path(temporary) / "et-reference"
        subprocess.run(
            ["rustc", "--edition=2021", "-D", "warnings", "-O", str(BUNDLE / "rust/harness.rs"), "-o", str(binary)],
            check=True,
            capture_output=True,
        )
        result = subprocess.run([str(binary)], check=True, capture_output=True)
    for line in result.stdout.decode().splitlines():
        kind, *numbers = line.split("\t")
        values = [int(value) for value in numbers]
        if kind == "B":
            dimension, left, right, index, sign = values
            if index != left ^ right or sign != cd_sign(dimension, left, right):
                raise ValueError(f"canonical basis disagreement: {line}")
            counts["basis_products"] += 1
        elif kind == "L":
            dimension, strut, position, label = values
            if ETSpec(dimension, strut, label).tone_row[position] != label:
                raise ValueError(f"canonical ordering disagreement: {line}")
        elif kind == "C":
            dimension, strut, row, column, occupied, value = values
            expected = ETSpec(dimension, strut, row).cell(column)
            if occupied != expected.occupied or value != expected.value:
                raise ValueError(f"canonical signed grid disagreement: {line}")
            counts["rust_cells"] += 1
        else:
            raise ValueError("unknown canonical export row")
    if counts != {
        "tables": 116,
        "full_grid": 273264,
        "addressable": 263088,
        "paired_blocks": 283440,
        "basis_products": 21760,
        "rust_cells": 273264,
    }:
        raise ValueError(f"canonical coverage changed: {counts}")
    return {
        "counts": counts,
        "flint_kernels": parallel.ordered_map(
            check_exact_kernel,
            [(dimension, strut, row) for dimension in (32, 64, 128) for strut, row in ((1, 2), (9, 2), (9, 8))]
            + [(dimension, 15, row) for dimension in (64, 128) for row in (1, dimension // 4, dimension // 4 ^ 1)],
            min_items=2,
        ),
        "canonical_commit": pins["commit"],
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "scope": "unchanged isolated Rust modules; Python fixture and paired-block comparison",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = replay()
    receipt = BUNDLE / "canonical_replay.json"
    if args.check:
        if report != json.loads(receipt.read_text()):
            raise ValueError("canonical replay differs from retained receipt")
    else:
        receipt.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
