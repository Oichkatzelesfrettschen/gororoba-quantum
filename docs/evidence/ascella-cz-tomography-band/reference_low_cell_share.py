"""Post-data check, deciding nothing: the share of the model-check Pearson statistic that falls in cells the
linear-inversion fit predicts below one event, measured and under mesh_variance_reference.py's synthetic pairs at
sigma 0, 0.011 and 0.034 (30 pairs each). It asks whether an isotropic per-seed share error already concentrates
the statistic in those cells, as the measured pairs do.

It also reads the realized per-cell share error of mesh_variance_reference.py's perturbation: sigma is added before
clipping and renormalization, so the RMS share error it produces differs from sigma. For each pair it reports the
realized RMS at the decision values and at the band's matching value 0.034, and the input sigma whose realized RMS
equals the recorded scales 0.011 and 0.0177 (bisection, 200 perturbations per evaluation, no refit).

Random draws take their seeds from docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json index 214 (cell shares) and
index 215 (realized share error). Run from the
repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/reference_low_cell_share.py OUT.json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
SIGMAS = (0.0, 0.011, 0.034)
DRAWS = 30
RMS_SIGMAS = (0.011, 0.0177, 0.034)
RECORDED = (0.011, 0.0177)
RMS_DRAWS = 200


def reference_module() -> Any:
    spec = importlib.util.spec_from_file_location("mesh_variance_reference", HERE / "mesh_variance_reference.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("mesh_variance_reference.py not found beside this script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REF = reference_module()
TOMO, CASE, ANALYSIS = REF.TOMO, REF.CASE, REF.ANALYSIS


def low_share(n: np.ndarray, shots: np.ndarray, scale: np.ndarray) -> float:
    rates = TOMO.absolute_rates(n, shots, scale)
    e = (
        (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(n.shape)
        * shots[:, None]
        / scale[:, None]
    )
    cells = (n - e) ** 2 / np.maximum(e, 1.0)
    return float(cells[e < 1.0].sum() / cells.sum())


def realized_rms(within: np.ndarray, sigma: float, seed: int) -> float:
    generator = np.random.default_rng(seed)
    total = within.sum(axis=1, keepdims=True)
    shares = within / total
    errors = [REF.perturbed(within, sigma, generator) / total - shares for _ in range(RMS_DRAWS)]
    return float(np.sqrt(np.mean(np.square(errors))))


def input_for(within: np.ndarray, target: float, seed: int) -> float:
    low, high = 0.5 * target, 3.0 * target
    for _ in range(30):
        middle = 0.5 * (low + high)
        low, high = (middle, high) if realized_rms(within, middle, seed) < target else (low, middle)
    return 0.5 * (low + high)


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: reference_low_cell_share.py OUT.json")
    generator = np.random.default_rng(REF.draw_seed(214))
    out: dict[str, Any] = {"draws": DRAWS}
    for name, spec in ANALYSIS.pairs_of_runs().items():
        data = ANALYSIS.tallies(spec)
        within, sample_rate = REF.per_sample_law(data)
        entry: dict[str, Any] = {"measured": low_share(data["eligible"], data["shots"], data["scale"])}
        for sigma in SIGMAS:
            # Serial by measurement: the whole script takes 4 s on a 10-thread host, and mapping these 30 evaluations
            # through parallel.ordered_map took 18 s and moved the shares by 1e-13 relative (single-thread BLAS in
            # the workers).
            shares = []
            for _ in range(DRAWS):
                arrays = {
                    "eligible": REF.perturbed(within, sigma, generator),
                    "samples": np.ones(len(data["samples"])),
                    "any": 1.0 / sample_rate,
                }
                drawn, _, drawn_shots = CASE.sampled_dataset(arrays, data["samples"], generator)
                shares.append(low_share(drawn.astype(float), drawn_shots.astype(float), data["scale"]))
            entry[str(sigma)] = {"mean": float(np.mean(shares)), "min": float(min(shares)), "max": float(max(shares))}
        seed = REF.draw_seed(215)
        entry["realized_share_rms"] = {str(s): realized_rms(within, s, seed) for s in RMS_SIGMAS}
        entry["input_sigma_for_recorded_rms"] = {str(t): input_for(within, t, seed) for t in RECORDED}
        out[name] = entry
    Path(argv[0]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
