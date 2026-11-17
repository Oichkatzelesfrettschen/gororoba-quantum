"""Regressions of rule R6 (the readout flip fitted inside decide()), run before the value-12 record.

1. With the flip fixed at 0, the chunked flip-outer oc_worker reproduces the value-11 label counts of every scenario
   that existed at value 11 (same seed, same positions; a 5,000-series draw begins with the 500-series draw).
2. On the full FLIP_GRID, decide() reproduces the labels nuisance.py's finish() stored per series in
   docs/local/rebuild/nuisance/parts for the first SERIES noisy series of four scenarios.
Prints one line per check and "regression=pass" or raises."""

import json
import sys

import numpy as np

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

HERE = "docs/evidence/qi-null-phase-scan-decision-probes/readout-flip"
VALUE11 = f"{HERE}/prediction_value11.json"
NEW = {
    "q12 phase -0.18 rad, selector flip 0.036",
    "coupler 8-12 phase -0.25 rad, selector flip 0.036",
    "q8 phase at coupler 8-12 -0.25 rad, selector flip 0.042",
}
PARTS = "docs/local/rebuild/nuisance/parts"
SERIES = 20
CHECKED = (
    "true: q12 phase -0.18 rad, flip 0.0166",
    "null: flip 0.025, CZ phase damping 0.13",
    "TRUTHS: q8 phase at coupler 8-12 -0.25 rad",
    "gap: drift null flip 0.0166 to 0.036, CZ phase damping 0.13",
)


def nuisance_series(name: str):
    """The scenario's base and first SERIES noisy series exactly as nuisance.py drew them, and its stored labels."""
    import glob

    path = [p for p in glob.glob(f"{PARTS}/*.json") if json.load(open(p))["name"] == name][0]
    part = json.load(open(path))
    sys.path.insert(0, HERE)
    import nuisance as nu

    spec = nu.all_scenarios()[name]
    matrix = ps.predecessor_matrix()
    base = nu.base_batches(name, spec, matrix)
    rng = np.random.default_rng([nu.SEED, part["position"]])
    draws = rng.standard_normal((part["series"], len(base), 6))
    series = [nu.noisy(base, draws[i]) for i in range(SERIES)]
    stored = [part["per_series"][i + 1]["nuisance"] for i in range(SERIES)]
    return series, stored


def nuisance_check(name: str):
    series, stored = nuisance_series(name)
    matrix = ps.predecessor_matrix()
    screened = [ps.screen(s) for s in series]
    fits = [{} for _ in series]
    for flip in ps.FLIP_GRID:
        for (label, z12, _), fit in zip(screened, fits, strict=True):
            if label is None:
                ps.absorb(fit, flip, z12, lambda b: matrix, "all")
        ps.clear_caches()
    got = [ps.decide(s, lambda b: matrix, fitted=f)["label"] for s, f in zip(series, fits, strict=True)]
    return name, got, stored


def main():
    ps.build_tables()
    old = json.load(open(VALUE11))["operating_characteristics"]
    names = [] if "--nuisance-only" in sys.argv else [n for n in ps.TRUTHS if n not in NEW] + list(ps.MIXED)
    if names and set(names) != set(old["label_counts"]):
        raise ValueError(f"scenario sets differ: {sorted(set(names) ^ set(old['label_counts']))}")
    seed = ps.oc_seed(11)
    items = [
        (seed, name, pos, start, start + 250, old["kind_margin"], old["separation"], (0.0,))
        for pos, name in enumerate(names)
        for start in (0, 250)
    ]
    counts: dict[str, dict[str, int]] = {n: {} for n in names}
    for item, tally in zip(items, ordered_map(ps.oc_worker, items, min_items=2), strict=True):
        for label, k in tally.items():
            counts[item[1]][label] = counts[item[1]].get(label, 0) + k
    bad = {n: (counts[n], old["label_counts"][n]) for n in names if counts[n] != old["label_counts"][n]}
    if bad:
        raise ValueError(f"the flip-0 slice differs from value 11: {bad}")
    print(f"flip-0 slice reproduces value 11 in all {len(names)} scenarios", flush=True)
    for name, got, stored in ordered_map(nuisance_check, list(CHECKED), min_items=2):
        if got != stored:
            raise ValueError(f"{name}: decide() {got} against nuisance.py {stored}")
        print(f"decide() reproduces nuisance.py on {SERIES} series of {name}: {sorted(set(got))}", flush=True)
    print("regression=pass")


if __name__ == "__main__":
    main()
