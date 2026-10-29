"""Verify original pilot member bytes and replay all QPY operators under the current Qiskit pin."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import io
import json
import math
import re
import sys
import tempfile
import zipfile
from functools import lru_cache
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qpy
from qiskit.quantum_info import Operator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ci"))

from pins import current_pins  # noqa: E402

import parallel  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "docs/evidence/et_rows"


@lru_cache(maxsize=1)
def _pilot_modules() -> tuple[Any, Any]:
    with zipfile.ZipFile(BUNDLE / "pilot.zip") as archive, tempfile.TemporaryDirectory(prefix="et-pilot-") as temporary:
        for name in ("et_reference.py", "qiskit_et_pilot.py", "coherence_pilot.py"):
            (Path(temporary) / name).write_bytes(archive.read("et_quantum_pilot/" + name))
        sys.path.insert(0, temporary)
        try:
            return importlib.import_module("qiskit_et_pilot"), importlib.import_module("coherence_pilot")
        finally:
            sys.path.remove(temporary)


def check_operator(name: str) -> dict[str, Any]:
    pilot, coherence = _pilot_modules()
    with zipfile.ZipFile(BUNDLE / "pilot.zip") as archive:
        match = re.match(
            r"row_D(\d+)_S(\d+)_L(\d+)_(fixed_plus|fixed_minus|matched_dark|affine_dark)_(diagonal|anf)",
            Path(name).stem,
        )
        support = re.match(r"support_D(\d+)_S(\d+)_L(\d+)_uniform", Path(name).stem)
        if match is not None:
            dimension, strut, row = map(int, match.groups()[:3])
            mode, strategy = match.groups()[3:]
            source = pilot.row_circuit(dimension, strut, row, mode, strategy, column_marker=int("marker1" in name))
        elif support is not None:
            dimension, strut, row = map(int, support.groups())
            source = pilot.support_oracle(dimension, strut, row)
            from qiskit import QuantumCircuit

            preparation = QuantumCircuit(source.num_qubits)
            preparation.h(range(dimension.bit_length() - 2))
            source = preparation.compose(source)
        else:
            raise ValueError(f"unknown pilot circuit identity {name}")
        if "column_X" in name:
            source = coherence.add_coherence_readout(source, dimension, strut, row)
        circuits = qpy.load(io.BytesIO(archive.read(name)))
        if len(circuits) != 1:
            raise ValueError("pilot artifact must contain one circuit")
        error = float(np.max(abs(Operator.from_circuit(circuits[0]).data - Operator(source).data)))
        if error > 1e-10:
            raise ValueError(f"pilot full operator differs at {name}: {error}")
        return {"file": Path(name).name, "operator_max_error": error}


def check_receipt(report: dict[str, Any], path: Path) -> None:
    retained = json.loads(path.read_text())
    if set(report) != set(retained) or any(retained[key] != report[key] for key in ("manifest_members", "operators")):
        raise ValueError("retained QPY receipt coverage differs from replay")
    expected_rows, actual_rows = retained["circuits"], report["circuits"]
    if len(expected_rows) != len(actual_rows) or any(
        expected["file"] != actual["file"] for expected, actual in zip(expected_rows, actual_rows, strict=True)
    ):
        raise ValueError("retained QPY receipt circuit identities differ")
    if retained["max_error"] != max(row["operator_max_error"] for row in expected_rows):
        raise ValueError("retained QPY receipt maximum disagrees with its circuits")
    for expected, actual in zip(expected_rows, actual_rows, strict=True):
        if not math.isclose(expected["operator_max_error"], actual["operator_max_error"], rel_tol=1e-5, abs_tol=1e-14):
            raise ValueError(f"retained QPY receipt operator error differs: {actual['file']}")


def verify_receipt_guard() -> None:
    report = {
        "manifest_members": 119,
        "operators": 1,
        "max_error": 1e-13,
        "circuits": [{"file": "fixture.qpy", "operator_max_error": 1e-13}],
    }
    with tempfile.TemporaryDirectory(prefix="et-receipt-") as temporary:
        path = Path(temporary) / "receipt.json"
        path.write_text(json.dumps(report))
        check_receipt(report, path)
        for changed in (
            report | {"operators": 2},
            report | {"max_error": 0},
            report | {"max_error": 1e-8, "circuits": [{"file": "fixture.qpy", "operator_max_error": 1e-8}]},
            report | {"circuits": [{"file": "wrong.qpy", "operator_max_error": 1e-13}]},
        ):
            path.write_text(json.dumps(changed))
            try:
                check_receipt(report, path)
            except ValueError:
                continue
            raise AssertionError("stale QPY receipt passed replay validation")
    print("QPY receipt coverage, identity and numerical mutation guards pass")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        verify_receipt_guard()
        return
    pinned = current_pins()["qiskit"]
    if version("qiskit") != pinned:
        raise ValueError(f"ET pilot QPY replay requires current Qiskit {pinned}, separate from historical replay")
    with zipfile.ZipFile(BUNDLE / "pilot.zip") as archive:
        manifest = json.loads(archive.read("et_quantum_pilot/manifest.json"))
        for item in manifest["files"]:
            data = archive.read("et_quantum_pilot/" + item["path"])
            if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
                raise ValueError(f"pilot member changed: {item['path']}")
        names = sorted(name for name in archive.namelist() if name.endswith(".qpy"))
    rows = parallel.ordered_map(check_operator, names, min_items=2)
    if len(rows) != 50:
        raise ValueError(f"pilot coverage changed: {len(rows)}")
    report = {
        "manifest_members": len(manifest["files"]),
        "operators": len(rows),
        "max_error": max(row["operator_max_error"] for row in rows),
        "circuits": rows,
    }
    check_receipt(report, BUNDLE / "qpy_replay.json")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
