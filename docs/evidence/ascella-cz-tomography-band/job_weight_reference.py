"""The model-check reference of the Ascella CZ tomography reference case with a per-seed share term and an output
weight per rail mode and job, to test whether job-to-job output weights carry the band pair's Pearson excess beyond
the recorded per-seed scale.

An output weight on a rail mode multiplies the rate of every outcome that clicks on it, in every readout basis. A
filter that is diagonal in the click basis of each readout is a different map in each basis, so one Choi matrix
does not hold it and the case's unweighted linear inversion scores it as scatter. mesh_variance_reference.py and
calibrated_reference.py draw their synthetic pairs under the linear-inversion fit with a per-seed share error and
no such filter.

Weights. Per job, a maximum-likelihood fit of one overlap and five relative mode weights (window mode C0 fixed at
1) to that job's two-click patterns on the designed unitaries (analyze.py ``pattern_laws``), over the eleven window
patterns that are not eligible outcomes. The eligible counts the Pearson statistic scores therefore do not enter
the weights. An outcome with control rail c and target rail t carries w(C_c) w(T_t); the four products of a job
are divided by their geometric mean, so a job's throughput stays in its shots and pooling scale.

Reference. The eligible counts are divided by their outcome weights, the case's linear inversion predicts the
rate of every cell, negative predictions are clipped to zero and the prediction is multiplied by the outcome
weights again. From that law onward the reference is mesh_variance_reference.py's: independent Gaussian share
errors of standard deviation sigma per setting and synthetic pair, the case's acquisition draw, and the case's own
unweighted refit and clipped Pearson score of every synthetic pair.

Rule, fixed before the run (the commit that adds this file precedes the commit that adds its output). The decision
inputs are 0.0124 and 0.0202, which realize the recorded per-seed share errors 0.011 and 0.0177
(reference_low_cell_share.py ``input_sigma_for_recorded_rms``), with the per-job weights, on the band pair:

* carried: the band statistic lies inside the central 95 % of the reference at either input;
* not carried: it lies outside at both.

Descriptive, deciding nothing: the same references at sigma 0; the references with every weight set to 1, which
repeat the case's reference (sigma 0) and calibrated_reference.py (the two inputs) on new draws; and all of them on
the retained pair, whose statistic passes the case's reference without any term.

Random draws take their seeds from docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json: index 220 for the decision
references, index 221 for the descriptive ones. Run from the repository root:
``"$PYTHON" docs/evidence/ascella-cz-tomography-band/job_weight_reference.py OUT.json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
DECISION_INPUTS = {"0.011": 0.0124, "0.0177": 0.0202}
DECISION_INDEX = 220
DESCRIPTIVE_INDEX = 221


def sibling(name: str) -> Any:
    found = sys.modules.get(f"band_{name}")
    if found is not None:
        return found
    spec = importlib.util.spec_from_file_location(f"band_{name}", HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{name}.py not found beside this script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"band_{name}"] = module
    spec.loader.exec_module(module)
    return module


REF = sibling("mesh_variance_reference")
ANALYSIS = REF.ANALYSIS
CASE, TOMO = ANALYSIS.CASE, ANALYSIS.TOMO
ROWS = ANALYSIS.ROWS
JOB = np.array([TOMO.JOBS.index(row["job"]) for row in ROWS])
RAILS = [ANALYSIS.PAIRS.index((c, t)) for c in (TOMO.C0, TOMO.C1) for t in (TOMO.T0, TOMO.T1)]
OFF_RAIL = [k for k in range(len(ANALYSIS.PAIRS)) if k not in RAILS]


def job_weights(runs: list[str]) -> list[dict[str, Any]]:
    """Per run of a pair, in job order: the off-rail pattern fit's overlap, six relative mode weights and the four
    outcome weights (outcome 2 c + t), the last divided by their geometric mean."""
    laws = ANALYSIS.pattern_laws()
    first = np.array([i for i, _ in ANALYSIS.PAIRS])[OFF_RAIL]
    second = np.array([j for _, j in ANALYSIS.PAIRS])[OFF_RAIL]
    out = []
    for position, run in enumerate(sorted(runs)):
        counts, _ = ANALYSIS.pattern_counts([run])
        rows = counts.sum(1) > 0
        if not np.array_equal(rows, JOB == position):
            raise RuntimeError(f"{run}: its settings are not those of {TOMO.JOBS[position]}")
        n = counts[rows][:, OFF_RAIL]
        ind, dis = laws[0][rows][:, OFF_RAIL], laws[1][rows][:, OFF_RAIL]

        def objective(x: np.ndarray, n: np.ndarray = n, ind: np.ndarray = ind, dis: np.ndarray = dis) -> float:
            overlap = 1.0 / (1.0 + np.exp(-x[0]))
            weight = np.concatenate([[1.0], np.exp(x[1:])])
            p = (overlap * ind + (1.0 - overlap) * dis) * weight[first] * weight[second]
            return -float((n * np.log(np.maximum(p / p.sum(1, keepdims=True), 1e-300))).sum())

        coarse = minimize(objective, np.zeros(TOMO.WINDOW), method="Nelder-Mead", options={"maxiter": 20000})
        fine = minimize(objective, coarse.x, method="BFGS")
        best = fine if fine.fun <= coarse.fun else coarse
        mode = np.concatenate([[1.0], np.exp(best.x[1:])])
        outcome = np.array([mode[c] * mode[t] for c in (TOMO.C0, TOMO.C1) for t in (TOMO.T0, TOMO.T1)])
        outcome = outcome / float(np.exp(np.log(outcome).mean()))
        out.append(
            {
                "run": run,
                "off_rail_events": float(n.sum()),
                "overlap": float(1.0 / (1.0 + np.exp(-best.x[0]))),
                "mode_weights_relative_to_C0": [float(v) for v in mode],
                "outcome_weights": [float(v) for v in outcome],
                "optimizer": {"nelder_mead": bool(coarse.success), "bfgs": bool(fine.success), "kept": best is fine},
            }
        )
    return out


def weighted_law(data: dict[str, np.ndarray], weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """mesh_variance_reference.per_sample_law with the (144, 4) outcome weights divided out before the linear
    inversion and multiplied back onto its clipped prediction."""
    eligible, samples, shots, scale = data["eligible"], data["samples"], data["shots"], data["scale"]
    rates = TOMO.absolute_rates(eligible / weights, shots, scale)
    predicted = (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(eligible.shape)
    per_shot = np.clip(predicted, 0.0, None) * weights / scale[:, None]
    sample_rate = samples / shots
    within = per_shot / sample_rate[:, None]
    within = within / np.maximum(within.sum(axis=1), 1.0)[:, None]
    return within, sample_rate


def reference(
    data: dict[str, np.ndarray], weights: np.ndarray, sigma: float, generator: np.random.Generator
) -> np.ndarray:
    within, sample_rate = weighted_law(data, weights)
    samples, scale = data["samples"], data["scale"]
    items = []
    for _ in range(CASE.OVERDISPERSION_DRAWS):
        arrays = {
            "eligible": REF.perturbed(within, sigma, generator),
            "samples": np.ones(len(samples)),
            "any": 1.0 / sample_rate,
        }
        drawn, _, drawn_shots = CASE.sampled_dataset(arrays, samples, generator)
        items.append((drawn.astype(float), drawn_shots.astype(float), scale))
    return np.array(CASE.ordered_map(CASE.pearson_of, items, min_items=1))


def entry(observed: float, ref: np.ndarray, sigma: float) -> dict[str, Any]:
    low, high = (float(v) for v in np.percentile(ref, [2.5, 97.5]))
    return {
        "input_sigma": sigma,
        "reference_mean": float(ref.mean()),
        "reference_95": [low, high],
        "ratio": observed / float(ref.mean()),
        "inside": bool(low <= observed <= high),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: job_weight_reference.py OUT.json")
    decide = np.random.default_rng(REF.draw_seed(DECISION_INDEX))
    describe = np.random.default_rng(REF.draw_seed(DESCRIPTIVE_INDEX))
    out: dict[str, Any] = {"draws": CASE.OVERDISPERSION_DRAWS, "decision_inputs": DECISION_INPUTS}
    for name, spec in ANALYSIS.pairs_of_runs().items():
        data = ANALYSIS.tallies(spec)
        fitted = job_weights(spec["runs"])
        weights = np.array([fitted[job]["outcome_weights"] for job in JOB])
        flat = np.ones_like(weights)
        observed = float(CASE.pearson(data["eligible"], data["shots"], data["scale"]))
        found: dict[str, Any] = {"observed_pearson": observed, "job_weights": fitted}
        if name == "band":
            found["decision"] = {
                recorded: entry(observed, reference(data, weights, sigma, decide), sigma)
                for recorded, sigma in DECISION_INPUTS.items()
            }
            inside = [value["inside"] for value in found["decision"].values()]
            out["verdict"] = "carried" if any(inside) else "not carried"
        sigmas = [0.0, *DECISION_INPUTS.values()]
        found["descriptive"] = {
            "per_job_weights": {
                str(sigma): entry(observed, reference(data, weights, sigma, describe), sigma)
                for sigma in (sigmas if name != "band" else sigmas[:1])
            },
            "weights_of_one": {
                str(sigma): entry(observed, reference(data, flat, sigma, describe), sigma) for sigma in sigmas
            },
        }
        out[name] = found
    Path(argv[0]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
