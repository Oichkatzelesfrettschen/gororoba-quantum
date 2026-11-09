"""Write the float64 inputs of the ensemble's tomography prediction to OUT.npz for fp_backends.py.

The arrays are the producer's own: the 576 x 256 design matrix, the point rates and the 500 bootstrap replicates of
scripts/ascella_cz_ensemble_case.py, the 32 rate observables rho^T x E, the Hermitian basis and the ideal CZ Choi
vector.
The file also stores a `provenance` record: the exporting host's label, machine, interpreter and numpy, and the five
`arithmetic.inputs_sha256` digests computed by the producer's own functions, which fp_sweep.py compares with the
digests it rebuilds from the arrays. A host that runs this exporter itself puts its own libm and BLAS results behind
those digests; a host that receives the file from another host reports that host's.

usage: "$PYTHON" docs/evidence/least-squares-precision/fp_export.py OUT.npz [--host-label LABEL]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ascella_cz_ensemble_case as case  # noqa: E402
import ascella_cz_tomography_case as tomo  # noqa: E402
import fp_host  # noqa: E402


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--host-label", default=None, help="hostname-free label of the exporting host")
    args = ap.parse_args()
    problem = fp_host.label_error(args.host_label) if args.host_label is not None else None
    if problem:
        print(problem, file=sys.stderr)
        return 2
    arrays = case.tomography_arrays()
    _, value = case.seed_plan()["prediction"]
    generator = np.random.default_rng(value)
    batch = tomo.resampled_rates(
        arrays["eligible"], arrays["samples"], arrays["shots"], arrays["scale"], generator, case.PREDICTION_REPLICATES
    )
    names, observables, correct = [], [], []
    for table, inputs in case.TABLES.items():
        for control, target in inputs:
            row = {"name": f"in-{control}{target}-{table}", "input": control + target, "basis": table}
            correct.append(case.correct_outcome(row))
            density = case.input_density(row["input"]).T
            for outcome in range(4):
                names.append(f"{row['name']}[{outcome}]")
                observables.append(np.kron(density, tomo.outcome_projector(table, outcome)))
    point = tomo.absolute_rates(arrays["eligible"], arrays["shots"], arrays["scale"])
    inputs = case.prediction_inputs()
    provenance = {
        "exporter_host_label": args.host_label,
        "machine": platform.machine(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "producer_inputs_sha256": {
            "design_matrix": digest(inputs["design"]),
            "rate_observables": digest(inputs["observables"]),
            "hermitian_basis": digest(tomo.hermitian_stack()),
            "ideal_choi_vector": digest(tomo.ideal_choi_vector()),
            "observed_rate_columns": digest(np.column_stack([point, batch.T])),
        },
    }
    np.savez(
        args.out,
        a=tomo.design_matrix(),
        f=point,
        batch=batch,
        obs=np.asarray(observables),
        basis=tomo.hermitian_stack(),
        v=tomo.ideal_choi_vector().real,
        correct=np.asarray(correct),
        names=np.asarray(names),
        tables=np.asarray(list(case.TABLES)),
        provenance=np.asarray(json.dumps(provenance, sort_keys=True)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
