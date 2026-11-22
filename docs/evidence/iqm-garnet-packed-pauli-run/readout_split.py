"""Per-qubit and per-cell readings of the retained packed Pauli Garnet run, written after the analysis.

The registered analysis (scripts/iqm_packed_pauli_case.py analyze) reports the buffer carryover for the four sentinel
cells and the register mean, and pools each reference circuit's assignment error over twenty qubits. This split reads
the same raw bytes per cell (the load cell 4 included) and per qubit: each reference circuit's excited fraction per
qubit, and each cell's buffer excited population after a dense predecessor minus after a sparse one with Welch's
standard error over buffers, the analysis's own definition. It decides nothing.

Usage: python3 docs/evidence/iqm-garnet-packed-pauli-run/readout_split.py RUN_DIR OUT.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import iqm_records  # noqa: E402
from parallel import ordered_map  # noqa: E402

CELL = 4


def welch(a: list[float], b: list[float]) -> dict[str, float]:
    x, y = np.array(a), np.array(b)
    return {
        "dense_predecessor_mean": float(x.mean()),
        "sparse_predecessor_mean": float(y.mean()),
        "difference": float(x.mean() - y.mean()),
        "standard_error": float(math.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))),
    }


class Columns:
    """Buffer carryover of one group of qubit columns; holds only its inputs so it pickles for ordered_map."""

    def __init__(self, roles: list[dict[str, Any]], bits: list[np.ndarray]) -> None:
        self.roles = roles
        self.bits = bits

    def __call__(self, columns: tuple[int, ...]) -> dict[str, float]:
        arms: dict[bool, list[float]] = {True: [], False: []}
        for number, role in enumerate(self.roles):
            predecessor = self.roles[number - 1]
            if role["kind"] == "buffer" and predecessor["kind"] == "science":
                arms[bool(predecessor["dense"])].append(float(self.bits[number][:, list(columns)].mean()))
        return welch(arms[True], arms[False])


def main(run_dir: Path, out: Path) -> None:
    run = iqm_records.read_run(run_dir)
    if run.submission["qc"] != "garnet":
        raise SystemExit(f"{run_dir}: not a garnet run")
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    roles = prediction["circuits"]
    bits = [np.asarray(result["c"], dtype=np.int64) for result in run.completed_measurements()]
    first = json.loads((run_dir / roles[0]["file"]).read_text(encoding="utf-8"))
    locus = next(i for i in first["instructions"] if i["name"] == "measure")["locus"]
    references = {
        role["name"]: {
            "reference": role["reference"],
            "excited_fraction": {q: round(float(bits[n][:, k].mean()), 6) for k, q in enumerate(locus)},
        }
        for n, role in enumerate(roles)
        if role["kind"] == "reference"
    }
    groups = [tuple(range(CELL * c, CELL * c + CELL)) for c in range(len(locus) // CELL)]
    qb12 = (locus.index("QB12"),)
    rows = ordered_map(Columns(roles, bits), [*groups, qb12])
    seconds = (run.job.get("metrics") or {}).get("execution_seconds")
    circuit_shots = len(roles) * run.row["shots"]
    record = {
        "schema": "iqm-packed-pauli-readout-split-v1",
        "run": run_dir.name,
        "locus": locus,
        "references": references,
        "carryover_per_cell": {str(c): rows[c] for c in range(len(groups))},
        "carryover_qb12": rows[-1],
        "execution_seconds": seconds,
        "circuit_shots": circuit_shots,
        "execution_seconds_per_circuit_shot": seconds / circuit_shots if seconds else None,
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
