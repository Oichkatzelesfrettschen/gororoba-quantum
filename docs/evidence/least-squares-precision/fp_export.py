"""Write the float64 inputs of the ensemble's tomography prediction to OUT.npz for fp_backends.py.

The arrays are the producer's own: the 576 x 256 design matrix, the point rates and the 500 bootstrap replicates of
scripts/ascella_cz_ensemble_case.py, the 32 rate observables rho^T x E, the Hermitian basis and the ideal CZ Choi
vector.

usage: "$PYTHON" docs/evidence/least-squares-precision/fp_export.py OUT.npz
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import ascella_cz_ensemble_case as case  # noqa: E402
import ascella_cz_tomography_case as tomo  # noqa: E402


def main() -> int:
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
    np.savez(
        sys.argv[1],
        a=tomo.design_matrix(),
        f=tomo.absolute_rates(arrays["eligible"], arrays["shots"], arrays["scale"]),
        batch=batch,
        obs=np.asarray(observables),
        basis=tomo.hermitian_stack(),
        v=tomo.ideal_choi_vector().real,
        correct=np.asarray(correct),
        names=np.asarray(names),
        tables=np.asarray(list(case.TABLES)),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
