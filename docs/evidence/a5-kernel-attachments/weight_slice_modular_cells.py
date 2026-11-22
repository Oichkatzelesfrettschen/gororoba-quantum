"""Modular weight-slice cells that the weight-slice record leaves out: E8-bar -> N+ and Iso -> N- at (32009, 10754).

    $PYTHON docs/evidence/a5-kernel-attachments/weight_slice_modular_cells.py OUT.json

weight_slice_fiber_relations.py writes modular cells for W8 and E8-bar at N- only. This successor record runs the
producer's own functions (orbit_task, fiber_script, run_singular, summarize_fiber_run, hilbert_script) on the two
cells whose relation lines the Rees runs of ledger rows A5-573 and A5-574 print, and requires the relation digests
of those runs. The E8-bar -> N- cell is regenerated first as the known-good calibration and must equal the digest of
the weight-slice record; the relation lines of each cell without their first line must read another digest (the
known-bad control).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RECORD = HERE / "weight-slice-fiber-relations-result.json"
PRIME, ROOT = 32009, 10754
# (orbit, source, relation digest that the cell must reproduce, origin of the digest)
CALIBRATION = (
    "N-",
    "e8",
    "42b1d8ff03d4c505597b39fe303c52ac45fcdc4d35bbf01d0b8e7e23a97367d0",
    "weight-slice record cell",
)
CELLS = [
    ("N+", "e8", "b9b7372bce35e7ce286aa572f9b1ebf656d1ac04ba0e63349c640efed88658ee", "REL lines of the run of A5-573"),
    ("N-", "iso", "4b9f84948f9ffa00f5e735ccc8943b6be0b7afc4a932f8a3c600b92b6e3e99c5", "REL lines of the run of A5-574"),
]


def load_producer() -> Any:
    path = HERE / "weight_slice_fiber_relations.py"
    spec = importlib.util.spec_from_file_location("weight_slice_fiber_relations", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["weight_slice_fiber_relations"] = module
    spec.loader.exec_module(module)
    return module


def cell(producer: Any, orbit: str, source: str, want: str, origin: str) -> dict[str, Any]:
    piece = producer.orbit_task(orbit)
    run = producer.run_singular(producer.fiber_script(piece, source, PRIME, ROOT))
    summary = producer.summarize_fiber_run(run)
    hilbert = producer.hilbert_item(producer.hilbert_script(run["relations"], summary["generator_count"], PRIME, ROOT))
    lines = sorted(str(line) for line in run["relations"])
    dropped = hashlib.sha256(("\n".join(lines[1:]) + "\n").encode("utf-8")).hexdigest()
    return {
        "orbit": orbit,
        "source": source,
        "incidence": producer.incidence_name(orbit, source),
        "field": producer.field_name(PRIME, ROOT),
        "characteristic": PRIME,
        "i_root": ROOT,
        **summary,
        "hilbert": hilbert,
        "expected_relations_sha256": want,
        "expected_digest_origin": origin,
        "digest_equal": summary["relations_sha256"] == want,
        "control_without_first_relation_differs": dropped != want,
    }


def main() -> int:
    producer = load_producer()
    version = producer.singular_version()
    calibration = cell(producer, *CALIBRATION)
    in_record = calibration["relations_sha256"] in RECORD.read_text(encoding="utf-8")
    cells = [cell(producer, *spec) for spec in CELLS]
    good = in_record and all(
        c["digest_equal"] and c["control_without_first_relation_differs"] for c in [calibration, *cells]
    )
    record = {
        "schema": "weight-slice-modular-cells-v1",
        "prime": PRIME,
        "i_root": ROOT,
        "singular_version": list(version),
        "calibration": calibration | {"digest_in_weight_slice_record": in_record},
        "cells": cells,
        "pass": good,
    }
    Path(sys.argv[1]).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for c in [calibration, *cells]:
        print(
            "CELL",
            c["incidence"],
            "generators",
            c["generator_count"],
            "relations",
            c["relation_count"],
            "sha256",
            c["relations_sha256"],
            "equal",
            int(c["digest_equal"]),
            "dim",
            c["hilbert"]["affine_dimension"],
            "mult",
            c["hilbert"]["multiplicity"],
        )
    print("verdict:", "PASS" if good else "FAIL")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
