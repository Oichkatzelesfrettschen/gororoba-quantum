"""The preregistered model-check reference of the Ascella CZ tomography reference case, rebuilt with a per-seed mesh
term, to test whether that term accounts for the failed check (2026-11-09 band pair) and the passed one (2026-10-31
retained pair).

``overdispersion`` in scripts/ascella_cz_tomography_reference_case.py draws OVERDISPERSION_DRAWS synthetic pairs
under the linear-inversion fit and the acquisition law. Here each synthetic setting's four conditional eligible
shares first receive independent Gaussian errors of standard deviation sigma (clipped at zero and renormalized to
the setting's eligible probability), drawn afresh for every setting and every synthetic pair, because every setting
runs on its own compilation seed. Everything else, including the refit and the clipped Pearson score, is the case's
own code. The sigma values come from records outside this case: 0.011, the per-mesh signed-coherence error of the
Ascella signed-coherence anchors, and 0.0177, the qpu:belenos per-seed share spread of extreme blocks
(docs/notes/quandela/strategy.md section 7).

Rule, fixed before the run (the observed statistics are those of the band analysis and the retained verdicts):

* supported: at sigma 0.011 or at sigma 0.0177, both pairs' observed Pearson statistics lie inside the central 95 %
  of the rebuilt reference;
* partial: otherwise, when at least one sigma value places one pair's statistic inside;
* falsified: neither sigma value places either pair's statistic inside.

Descriptive, deciding nothing: the reference mean on a sigma grid, and per pair the sigma whose reference mean
equals the observed statistic (linear interpolation on the grid). A single per-seed term predicts similar values
for the two pairs.

Random draws take their seeds from docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json, index 212 for the decision
references and index 213 for the grid. Run from the repository root:
``"$PYTHON" docs/evidence/ascella-cz-tomography-band/mesh_variance_reference.py OUT.json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAW = "docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json"
DECISION_SIGMAS = (0.011, 0.0177)
GRID = (0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04)
GRID_DRAWS = 60
OBSERVED = {
    "retained": "results/quandela/cases/ascella_cz_tomography_reference/retained-conjecture-verdicts.json",
    "band": "results/quandela/ascella-cz-tomography-reference-analysis.json",
}


def analysis_module() -> Any:
    spec = importlib.util.spec_from_file_location("band_analysis", HERE / "analyze.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("analyze.py not found beside this script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ANALYSIS = analysis_module()
CASE, TOMO = ANALYSIS.CASE, ANALYSIS.TOMO


def draw_seed(index: int) -> int:
    return int(json.loads((ROOT / DRAW).read_text(encoding="utf-8"))["values"][index])


def per_sample_law(data: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """The per-sample eligible probabilities and any-click rate per shot that ``overdispersion`` draws from."""
    eligible, samples, shots, scale = data["eligible"], data["samples"], data["shots"], data["scale"]
    rates = TOMO.absolute_rates(eligible, shots, scale)
    predicted = (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(eligible.shape)
    per_shot = np.clip(predicted, 0.0, None) / scale[:, None]
    sample_rate = samples / shots
    within = per_shot / sample_rate[:, None]
    within = within / np.maximum(within.sum(axis=1), 1.0)[:, None]
    return within, sample_rate


def perturbed(within: np.ndarray, sigma: float, generator: np.random.Generator) -> np.ndarray:
    total = within.sum(axis=1, keepdims=True)
    shares = within / total
    shares = np.clip(shares + sigma * generator.standard_normal(shares.shape), 0.0, None)
    return shares / shares.sum(axis=1, keepdims=True) * total


def reference(data: dict[str, np.ndarray], sigma: float, draws: int, generator: np.random.Generator) -> np.ndarray:
    within, sample_rate = per_sample_law(data)
    samples, scale = data["samples"], data["scale"]
    items = []
    for _ in range(draws):
        arrays = {
            "eligible": perturbed(within, sigma, generator),
            "samples": np.ones(len(samples)),
            "any": 1.0 / sample_rate,
        }
        drawn, _, drawn_shots = CASE.sampled_dataset(arrays, samples, generator)
        items.append((drawn.astype(float), drawn_shots.astype(float), scale))
    return np.array(CASE.ordered_map(CASE.pearson_of, items, min_items=1))


def crossing(grid: list[float], means: list[float], observed: float) -> float | None:
    for k in range(len(grid) - 1):
        lo, hi = means[k], means[k + 1]
        if (lo - observed) * (hi - observed) <= 0 and hi != lo:
            return grid[k] + (observed - lo) / (hi - lo) * (grid[k + 1] - grid[k])
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: mesh_variance_reference.py OUT.json")
    pairs = ANALYSIS.pairs_of_runs()
    out: dict[str, Any] = {"decision_sigmas": list(DECISION_SIGMAS), "draws": CASE.OVERDISPERSION_DRAWS}
    decide = np.random.default_rng(draw_seed(212))
    sweep = np.random.default_rng(draw_seed(213))
    inside: dict[float, dict[str, bool]] = {s: {} for s in DECISION_SIGMAS}
    for name, spec in pairs.items():
        data = ANALYSIS.tallies(spec)
        observed = float(
            json.loads((ROOT / OBSERVED[name]).read_text(encoding="utf-8"))["overlap_estimates"]["overdispersion"][
                "pearson"
            ]
        )
        recomputed = CASE.pearson(data["eligible"], data["shots"], data["scale"])
        if abs(recomputed - observed) > 1e-6 * observed:
            raise RuntimeError(f"{name}: recomputed Pearson {recomputed} differs from the recorded {observed}")
        entry: dict[str, Any] = {"observed_pearson": observed, "decision": {}}
        for sigma in DECISION_SIGMAS:
            ref = reference(data, sigma, CASE.OVERDISPERSION_DRAWS, decide)
            low, high = (float(v) for v in np.percentile(ref, [2.5, 97.5]))
            inside[sigma][name] = low <= observed <= high
            entry["decision"][str(sigma)] = {
                "reference_mean": float(ref.mean()),
                "reference_95": [low, high],
                "ratio": observed / float(ref.mean()),
                "inside": inside[sigma][name],
            }
        means = [float(reference(data, s, GRID_DRAWS, sweep).mean()) for s in GRID]
        entry["grid"] = {"sigma": list(GRID), "reference_mean": means, "draws": GRID_DRAWS}
        entry["sigma_matching_observed_mean"] = crossing(list(GRID), means, observed)
        out[name] = entry
    counts = [sum(inside[s].values()) for s in DECISION_SIGMAS]
    out["verdict"] = "supported" if 2 in counts else "partial" if 1 in counts else "falsified"
    Path(argv[0]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
