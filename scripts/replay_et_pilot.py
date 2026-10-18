"""Verify original pilot member bytes and replay all QPY operators under Qiskit 2.6."""

from __future__ import annotations

import hashlib
import importlib
import io
import json
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

import parallel

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


def main() -> None:
    if version("qiskit") != "2.6.0":
        raise ValueError("ET pilot QPY replay requires current Qiskit 2.6.0, separate from historical replay")
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
    print(
        json.dumps(
            {
                "manifest_members": len(manifest["files"]),
                "operators": len(rows),
                "max_error": max(row["operator_max_error"] for row in rows),
                "circuits": rows,
            }
        )
    )


if __name__ == "__main__":
    main()
