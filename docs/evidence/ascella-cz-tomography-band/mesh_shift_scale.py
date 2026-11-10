"""The SPAM-separated process fit of spam_separated_fit.py with a free scale kappa on its realized-mesh shift, a
post-data diagnostic of whether the counts support any scale of the shift the component model predicts.

spam_separated_fit.py fixes the shift beta_j (p'(s, o) - p(s, o)) at kappa = 1, and the admitted two-photon shift
raises the Poisson negative log-likelihood (NLL) of the eligible counts by 4,229 on the band pair
(spam-separated-fit.json). Here the shift is kappa beta_j (p' - p), with beta_j as that file computes it, and the NLL
is profiled over kappa: every point refits the positive Choi matrix (and, in the ``all`` variant, the free
per-setting throughputs beside the fixed per-job outcome weights) at that kappa. Two variants per component set:

* ``shift``: the shift alone, the ``mesh_shift`` fits of spam_separated_fit.py;
* ``all``: the shift with the outcome weights and the throughputs, its ``nuisance`` fit.

Component sets: each law's components cross-fitted from the other pair and in-sample, as spam_separated_fit.py
builds them, each at the overlap of the cross-pair transfer onto the pair.

Grid: KAPPAS. The best grid point and its two neighbors give a parabola, whose vertex kappa_hat is refitted; the
profile interval is where the parabola rises 1.92 above its vertex (95 % for one parameter under the Poisson law).
The model check rejects that law (the band Pearson ratio is 5.73), so the interval understates the uncertainty;
the interval at 5.73 times the NLL threshold is reported beside it.

Reading, stated before the run (post-data, it decides no preregistered conjecture): for a component set and
variant, the counts support a scale of the shift when the profile interval excludes 0 and the NLL at kappa_hat lies
more than 1.92 below the NLL at kappa = 0; kappa_hat near 0, or an interval that holds 0, reads as no supported
shift. F is reported at kappa = 0, 1 and kappa_hat. The fits are deterministic. Run from the repository root:
``"$PYTHON" docs/evidence/ascella-cz-tomography-band/mesh_shift_scale.py MESH_MODEL_JOBS.json OUT.json``.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
KAPPAS = (-1.0, -0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0)
THRESHOLD = 1.92
PEARSON_RATIO = 5.73


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


SPAM = sibling("spam_separated_fit")
UNSCALED = SPAM.prepared


def scaled_prepared(item: dict[str, Any]) -> dict[str, np.ndarray]:
    """spam_separated_fit.prepared with its shift multiplied by ``item["kappa"]``; beta_j stays at its value for the
    unscaled shift. Installed at import, so every worker process of the pool fits with it."""
    terms = UNSCALED(item)
    terms["shift"] = terms["shift"] * float(item.get("kappa", 1.0))
    return terms


SPAM.prepared = scaled_prepared


def meshes_of(model: dict[str, Any], pair: str) -> dict[str, dict[str, Any]]:
    arch, phases = SPAM.served_phases(pair)
    holdout = f"{SPAM.OTHER[pair]}_to_{pair}"
    out = {}
    for law in SPAM.LAWS:
        overlap = float(model[law][holdout]["overlap"]["transfer"])
        designed = SPAM.rail_probabilities(*SPAM.designed_amplitudes(), overlap)
        for label, trained_on in (("cross-fitted", SPAM.OTHER[pair]), ("in-sample", pair)):
            components = model["components"][law][trained_on]
            realized = SPAM.realized_probabilities(arch, phases, components, overlap)
            out[f"{law} {label}"] = {"realized": realized, "designed": designed}
    return out


def vertex(kappas: np.ndarray, nll: np.ndarray) -> tuple[float, float]:
    """The vertex and curvature of the parabola through the best grid point and its two neighbors."""
    best = int(np.clip(np.argmin(nll), 1, len(kappas) - 2))
    a, b, _ = np.polyfit(kappas[best - 1 : best + 2], nll[best - 1 : best + 2], 2)
    if a <= 0:
        return float(kappas[int(np.argmin(nll))]), 0.0
    return float(-b / (2 * a)), float(a)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: mesh_shift_scale.py MESH_MODEL_JOBS.json OUT.json")
    model = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out: dict[str, Any] = {"kappas": list(KAPPAS), "threshold": THRESHOLD, "pearson_ratio": PEARSON_RATIO}
    for pair, spec in SPAM.ANALYSIS.pairs_of_runs().items():
        data = SPAM.ANALYSIS.tallies(spec)
        fitted = SPAM.WEIGHTS.job_weights(spec["runs"])
        omega = np.array([fitted[job]["outcome_weights"] for job in SPAM.JOB])
        base = {"eligible": data["eligible"], "shots": data["shots"], "scale": data["scale"], "omega": omega}
        variants = {"shift": {"weights": False, "throughput": False}, "all": {"weights": True, "throughput": True}}
        items, keys = [], []
        for label, mesh in meshes_of(model, pair).items():
            for variant, switches in variants.items():
                for kappa in KAPPAS:
                    items.append({**base, **switches, **mesh, "kappa": kappa})
                    keys.append((label, variant))
        grid = SPAM.CASE.ordered_map(SPAM.fit, items, min_items=1)
        # A worker that fitted without scaled_prepared would ignore kappa and return one NLL per profile.
        for position in range(0, len(items), len(KAPPAS)):
            if np.ptp([entry["objective"] for entry in grid[position : position + len(KAPPAS)]]) == 0.0:
                raise RuntimeError(f"{pair} {keys[position]}: the NLL does not move with kappa")
        found: dict[str, Any] = {}
        refits, layout = [], []
        for position in range(0, len(items), len(KAPPAS)):
            label, variant = keys[position]
            nll = np.array([entry["objective"] for entry in grid[position : position + len(KAPPAS)]])
            kappa_hat, curvature = vertex(np.array(KAPPAS), nll)
            refits.append({**items[position], "kappa": kappa_hat})
            layout.append((label, variant, position, nll, kappa_hat, curvature))
        at_vertex = SPAM.CASE.ordered_map(SPAM.fit, refits, min_items=1)
        for (label, variant, position, nll, kappa_hat, curvature), best in zip(layout, at_vertex, strict=True):
            points = grid[position : position + len(KAPPAS)]
            zero, one = points[KAPPAS.index(0.0)], points[KAPPAS.index(1.0)]
            half = float(np.sqrt(THRESHOLD / curvature)) if curvature > 0 else float("inf")
            wide = float(np.sqrt(THRESHOLD * PEARSON_RATIO / curvature)) if curvature > 0 else float("inf")
            interval = [kappa_hat - half, kappa_hat + half]
            supported = bool(
                np.isfinite(half)
                and not interval[0] <= 0.0 <= interval[1]
                and zero["objective"] - best["objective"] > THRESHOLD
            )
            found.setdefault(label, {})[variant] = {
                "nll_profile": [float(v) for v in nll],
                "fidelity_profile": [entry["process_fidelity"] for entry in points],
                "kappa_hat": kappa_hat,
                "interval_95": interval if np.isfinite(half) else None,
                "interval_95_at_pearson_ratio": [kappa_hat - wide, kappa_hat + wide] if np.isfinite(wide) else None,
                "nll_at_kappa_hat_minus_nll_at_0": best["objective"] - zero["objective"],
                "nll_at_1_minus_nll_at_0": one["objective"] - zero["objective"],
                "fidelity": {
                    "kappa_0": zero["process_fidelity"],
                    "kappa_1": one["process_fidelity"],
                    "kappa_hat": best["process_fidelity"],
                },
                "supported": supported,
                "status_at_kappa_hat": best["status"],
                "grid_fits_not_ended_early": int(sum(not entry["status"]["ended_early"] for entry in points)),
            }
        out[pair] = found
    Path(argv[1]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
