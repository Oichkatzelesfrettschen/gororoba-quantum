"""Post-data check, deciding nothing preregistered: mesh_variance_reference.py's band-pair reference at the input
sigma values that realize the recorded per-seed share errors (0.0124 for 0.011, 0.0202 for 0.0177;
reference_low_cell_share.py ``input_sigma_for_recorded_rms``). The preregistered rule fixed 0.011 and 0.0177 as
inputs; this check reads the band statistic against the references the recorded scales imply. The retained pair
passes the reference without the term, so it is not rerun.

Random draws take their seed from docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json index 216. Run from the
repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/calibrated_reference.py OUT.json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
INPUTS = {"0.011": 0.0124, "0.0177": 0.0202}


def reference_module() -> Any:
    spec = importlib.util.spec_from_file_location("mesh_variance_reference", HERE / "mesh_variance_reference.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("mesh_variance_reference.py not found beside this script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REF = reference_module()


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: calibrated_reference.py OUT.json")
    data = REF.ANALYSIS.tallies(REF.ANALYSIS.pairs_of_runs()["band"])
    observed = float(REF.CASE.pearson(data["eligible"], data["shots"], data["scale"]))
    generator = np.random.default_rng(REF.draw_seed(216))
    out: dict[str, Any] = {"pair": "band", "observed_pearson": observed, "draws": REF.CASE.OVERDISPERSION_DRAWS}
    for recorded, sigma in INPUTS.items():
        ref = REF.reference(data, sigma, REF.CASE.OVERDISPERSION_DRAWS, generator)
        low, high = (float(v) for v in np.percentile(ref, [2.5, 97.5]))
        out[recorded] = {
            "input_sigma": sigma,
            "reference_mean": float(ref.mean()),
            "reference_95": [low, high],
            "ratio": observed / float(ref.mean()),
            "inside": low <= observed <= high,
        }
    Path(argv[0]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
