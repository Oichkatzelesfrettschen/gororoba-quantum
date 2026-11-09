"""The float64 producer's own tomography prediction, recorded from a checkout of its commit, as one JSON object.

The float64 producer is `tomography_prediction` of scripts/ascella_cz_ensemble_case.py before the certified
rewrite: `numpy.linalg.pinv` of the design, then a Choi matrix and Tr[(rho^T x E) J] per setting for the point fit
and each bootstrap replicate. This script imports that function from the checkout ROOT and records its output with
the commit and the OpenBLAS thread count it ran under, so fp_backends.py scores the producer's arithmetic itself.

usage: OPENBLAS_NUM_THREADS=N python producer_record.py ROOT OUT.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    sys.path.insert(0, str(root / "gororoba_quantum"))
    sys.path.insert(0, str(root / "scripts"))
    import ascella_cz_ensemble_case as case

    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    record = {
        "commit": commit,
        "openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS"),
        "workers": os.environ.get("GOROROBA_WORKERS"),
        "tomography_prediction": case.tomography_prediction(),
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
