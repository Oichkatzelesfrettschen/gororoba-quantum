"""Replay exact ET fixtures and unchanged pinned Rust sources in temporary storage."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel
from cd_core import cd_sign
from et_reference import ETSpec

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "docs/evidence/et_rows"


def check_table(table: dict) -> tuple[int, int, int]:
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
    return 1, len(table["labels"]) ** 2, table["ordered_addressable"]


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
        "basis_products": 21760,
        "rust_cells": 273264,
    }:
        raise ValueError(f"canonical coverage changed: {counts}")
    return {
        "counts": counts,
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
