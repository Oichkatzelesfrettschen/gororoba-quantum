"""Preregistered stochastic null of the measurement-sequence envelope's complete decision pipeline.

Each replicate is a device with no pinching departure (eps = 0, no readout history) whose qubits carry a gate-model
error: an sx error scaled so the unitary N = 16 residual is a common +0.011 plus an independent normal part of SD
0.0105 (the 250 us diagnostic's mean and spread, docs/evidence/measurement_sequence/scatter-floor.json). Every member,
reset control and pattern draws binomial shot noise; the reset and pattern screens, the informative filter, the
same-run rms floor and both directions of the pooled test and the count rule then run as on a collected record. A
replicate fires when any device verdict fires. The family-wise false-fire rate's one-sided 95 % Clopper-Pearson upper
bound must lie below FALSE_FIRE_CEILING.

Each replicate runs the scalar pipeline itself, and the replicates map through parallel.ordered_map with
per-replicate generators spawned up front from one QRNG seed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta

import measurement_sequence_analysis as msa
import msq_envelope_analysis as ea
from diagnostic_experiments import MSQE_RESET_CONTROLS, msqe_pattern_bits
from parallel import ordered_map

SCHEMA = "msq-envelope-null-v1"
# ANU QRNG docs/evidence/anu_qrng/draw-2026-10-26T220128Z.json, index 1.
NULL_SEED = 56182
COMMON_RESIDUAL = 0.011
INDEPENDENT_RESIDUAL_SD = 0.0105
FALSE_FIRE_CEILING = 0.01
CONFIDENCE = 0.95
SHOTS = 8192


def upper_bound(fires: int, replicates: int) -> float:
    """The one-sided Clopper-Pearson upper confidence bound on a binomial rate."""
    if fires >= replicates:
        return 1.0
    return float(beta.ppf(CONFIDENCE, fires + 1, replicates - fires))


def residual_slope(context: dict[str, Any]) -> float:
    """d(unitary residual) / d(sx error factor) of one qubit context, from the noise-free model at factors 1 and 3."""
    contexts = msa.with_planning({0: context}, msa.DEMONSTRATION_SCATTER_FLOOR)
    residuals = []
    for factor in (1.0, 3.0):
        model = msa.device_model(contexts[0], sx_error=factor * contexts[0]["sx_error"])
        row = msa.evaluate(msa.device_counts({0: model}, contexts, SHOTS), contexts)[0]
        residuals.append(float(row["gate_systematic_n16"]["unitary_residual"]))
    return (residuals[1] - residuals[0]) / 2.0


def null_contexts(width: int) -> dict[int, dict[str, Any]]:
    """width qubit contexts cycling the analysis fixture's eight distinct calibrations."""
    base = msa.fixture_contexts(tuple(range(len(msa.FIXTURE_SCALES))), None)
    return {q: dict(base[q % len(base)]) for q in range(width)}


def binomial(generator: np.random.Generator, ones: int, shots: int) -> tuple[int, int]:
    return int(generator.binomial(shots, min(max(ones / shots, 0.0), 1.0))), shots


def replicate(item: tuple[int, dict[int, dict[str, Any]], dict[int, float], float, np.random.SeedSequence]) -> dict:
    """One null device through the screens and the pinching analysis; which device verdicts fired."""
    width, contexts, slopes, floor, seed = item
    generator = np.random.default_rng(seed)
    residuals = COMMON_RESIDUAL + INDEPENDENT_RESIDUAL_SD * generator.standard_normal(width)
    models = {
        q: msa.device_model(ctx, sx_error=max(0.0, 1.0 + float(residuals[q]) / slopes[q]) * ctx["sx_error"])
        for q, ctx in contexts.items()
    }
    expected = msa.device_counts(models, contexts, SHOTS)
    counts = {
        q: {"final": {name: binomial(generator, k, n) for name, (k, n) in sorted(expected[q]["final"].items())}}
        for q in contexts
    }
    bits = msqe_pattern_bits(width)
    kept = []
    for q in contexts:
        p_ground = models[q]["e01"]
        controls = {c: binomial(generator, round(p_ground * SHOTS), SHOTS) for c in MSQE_RESET_CONTROLS}
        ro0 = counts[q]["final"][msa.ro0_name(q)]
        ro1 = counts[q]["final"][msa.t1_names(q)[0]]
        reset = ea.reset_screen(controls["rc1"], controls["rc0"], ro0, ro1, width)
        own = [row[q] for row in bits]
        ones = [
            binomial(generator, round((p_ground if b == 0 else 1.0 - models[q]["e10"]) * SHOTS), SHOTS) for b in own
        ]
        if reset["passes"] and ea.pattern_screen(own, ones, width)["passes"]:
            kept.append(q)
    if len(kept) < ea.MIN_KEPT:
        return {"kept": len(kept), "fired": [], "withheld": True}
    planned = msa.with_planning({q: contexts[q] for q in kept}, floor)
    verdict = msa.device_verdict(msa.evaluate({q: counts[q] for q in kept}, planned), ea.count_rule(width))
    fired = sorted(name for name, flag in msa.device_flags(verdict).items() if flag)
    return {"kept": len(kept), "fired": fired, "withheld": False}


def run(width: int, replicates: int, seed: int = NULL_SEED) -> dict[str, Any]:
    """The null calibration at one layout width."""
    contexts = null_contexts(width)
    slope_items = ordered_map(residual_slope, [contexts[q] for q in contexts], min_items=2)
    slopes = dict(zip(contexts, slope_items, strict=True))
    floor, reason = msa.bound_floor({"ibm_kingston"})
    if floor is None:
        raise msa.AnalysisError(f"no registered floor: {reason}")
    children = np.random.SeedSequence(seed).spawn(replicates)
    rows = ordered_map(replicate, [(width, contexts, slopes, floor, child) for child in children], min_items=2)
    fires = sum(1 for row in rows if row["fired"])
    bound = upper_bound(fires, replicates)
    return {
        "schema": SCHEMA,
        "width": width,
        "replicates": replicates,
        "seed": seed,
        "common_residual": COMMON_RESIDUAL,
        "independent_residual_sd": INDEPENDENT_RESIDUAL_SD,
        "count_rule": ea.count_rule(width),
        "floor": floor,
        "fires": fires,
        "fired_verdicts": {
            name: sum(1 for row in rows if name in row["fired"])
            for name in sorted({n for r in rows for n in r["fired"]})
        },
        "withheld_replicates": sum(1 for row in rows if row["withheld"]),
        "mean_kept": float(np.mean([row["kept"] for row in rows])),
        "upper_bound_95": bound,
        "ceiling": FALSE_FIRE_CEILING,
        "passes": bound < FALSE_FIRE_CEILING,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--width", type=int, choices=(16, 24, 32), required=True)
    parser.add_argument("--replicates", type=int, default=400)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = run(args.width, args.replicates)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0 if result["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
