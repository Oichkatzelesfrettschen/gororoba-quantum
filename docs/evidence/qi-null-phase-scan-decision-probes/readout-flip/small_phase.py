"""Exploratory, seeded by index 1 of docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json: how often a small true
phase reads exact_parabola under rule R6, whose exact world fits a readout flip that can absorb part of a phase.
exact_parabola states the phase reading unnecessary, so a true phase that reads it is the costly error of R6; each
such series' center offset is printed in standard errors. 300 noisy series per scenario, drawn as oc_worker draws
them, every series fitted at one flip before the next.

Usage: small_phase.py [SERIES]"""

import sys

import numpy as np

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

SERIES = int(sys.argv[1]) if len(sys.argv) > 1 else 300
SEED = 9893  # index 1 of docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json
PHASES = {"q12_phase": (-0.12, -0.08, -0.05, 0.05, 0.08, 0.12), "coupler_phase": (-0.12, -0.08, 0.08)}
SCENARIOS = [(world, theta, flip) for world, thetas in PHASES.items() for theta in thetas for flip in (0.0, 0.036)]


def run(item):
    position, (world, theta, flip) = item
    rng = np.random.default_rng([SEED, position])
    matrix = ps.predecessor_matrix()
    error = 1.0 / np.sqrt(ps.SCAN_SHOTS)
    base = ps.planted_batches(ps.truth_row(world, theta, matrix, flip))
    noise = rng.standard_normal((SERIES, len(base), 6))
    drawn = [
        [
            {
                **b,
                "contrasts": [v + error * noise[i, n, j] for j, v in enumerate(b["contrasts"])],
                "splits": [v + ps.OC_SPLIT_OFFSET + 2 * error * noise[i, n, 3 + j] for j, v in enumerate(b["splits"])],
            }
            for n, b in enumerate(base)
        ]
        for i in range(SERIES)
    ]
    series = [base, *drawn]
    screened = [ps.screen(s) for s in series]
    fits = [{} for _ in series]
    for f in ps.FLIP_GRID:
        for (label, z12, _), fit in zip(screened, fits, strict=True):
            if label is None:
                ps.absorb(fit, f, z12, lambda b: matrix, "all")
        ps.clear_caches()
    decisions = [ps.decide(s, lambda b: matrix, fitted=fit) for s, fit in zip(series, fits, strict=True)]
    counts: dict[str, int] = {}
    for d in decisions[1:]:
        counts[d["label"]] = counts.get(d["label"], 0) + 1
    # Center offsets (in units of their standard error) of the series that read exact_parabola, beside the
    # expected-value center: tests whether that misreading sits near the control's threshold of 3.
    z = sorted(
        round(d["numbers"]["center_contrast"][0] / d["numbers"]["center_contrast"][1], 2)
        for d in decisions[1:]
        if d["label"] == "exact_parabola"
    )
    center = decisions[0]["numbers"].get("center_contrast", [0.0, 1.0])
    return world, theta, flip, decisions[0]["label"], dict(sorted(counts.items())), round(center[0] / center[1], 2), z


def main():
    ps.build_tables()
    for world, theta, flip, expected, counts, center_z, z in ordered_map(run, list(enumerate(SCENARIOS)), min_items=2):
        print(
            f"{world} {theta:+.2f} flip {flip}: expected {expected} (center {center_z} SE); {SERIES} series {counts}; "
            f"exact_parabola center z {z}",
            flush=True,
        )


if __name__ == "__main__":
    main()
