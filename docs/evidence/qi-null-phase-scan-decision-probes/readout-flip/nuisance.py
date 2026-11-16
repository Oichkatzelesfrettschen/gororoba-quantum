"""Exploratory: the decision of qi_pathion_null_phase_scan_cases.decide() with the selector flip (probability f that
the selector read flips when d0 reads 0) as one nuisance parameter per series, shared by every batch and minimized
jointly per world over FLIPS. The label logic reimplements decide() on top of fit_batch(); the current rule is the
flip-0 slice of the same fits (checked against ps.decide() with the flip fixed at 0 by `--check`). Seed: index 0 of
the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json. Written against the generator of rule R5 (no
flip in decide()); the generator of rule R6 fits the flip itself, and decide(..., flips=(0.0,)) is R5
(r6_regression.py). Part files go to docs/local/rebuild/nuisance/parts (ignored); the logs beside this file hold
the counts of the recorded run.

Usage: nuisance.py --check | --time | --run SERIES [--out FILE] [--only SUBSTRING]"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time

import numpy as np
from scipy.stats import chi2 as chi2_law

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

SEED = 47387  # index 0 of docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json
_MATCHED = ps.matched
_RETENTION: dict = {}


def matched_shared(table, arms, matrix, center_visibility, mix, center=None):
    """ps.matched() with the retention search (which reads the center arm alone) kept per (table, matrix, center
    visibility, mix) instead of repeated for every arm tuple; `--check` compares it with ps.matched() bit for bit. A
    caller that supplies `center` (the R6 generator's own retention cache) reaches ps.matched() unchanged."""
    if center is not None:
        return _MATCHED(table, arms, matrix, center_visibility, mix, center)
    key = (id(table), matrix.tobytes(), float(center_visibility), float(mix))
    if key not in _RETENTION:
        center = table[:, [ps.ARM_NAMES.index(ps.CENTER)]]
        seen = np.stack(
            [
                ps.rs.visibility(ps.rs.read(ps.rs.contract(center, float(r), mix), matrix))[:, 0]
                for r in ps.rs.RETENTION_GRID
            ]
        )
        retention = np.empty(seen.shape[1])
        for j in range(seen.shape[1]):
            order = np.argsort(seen[:, j])
            retention[j] = float(np.interp(center_visibility, seen[order, j], ps.rs.RETENTION_GRID[order]))
        miss = np.maximum(0.0, np.maximum(center_visibility - seen.max(0), seen.min(0) - center_visibility))
        _RETENTION[key] = (retention, miss, table)
    retention, miss, _ = _RETENTION[key]
    outer = [n for n, a in enumerate(arms) if a != ps.CENTER]
    picked = [ps.ARM_NAMES.index(ps.arm_of(a)) for a in arms]
    read = ps.rs.read(ps.rs.contract(table[:, picked], retention, mix), matrix)
    split = ps.rs.d2_split(read)[0]
    relative = split[..., outer] - split[..., [arms.index(ps.CENTER)]]
    return np.concatenate([ps.rs.selector_contrast(read), relative], axis=-1), retention, miss


ps.matched = matched_shared
FLIPS = [round(0.0025 * k, 6) for k in range(25)]  # 0 to 0.06
D0 = ps.KEYS.index("d0")
WORLDS = tuple(ps.WORLDS)
NULL_FLIPS = (0.0166, 0.025, 0.036, 0.05)
NULL_NOISES = (
    ("CZ phase damping 0.10", (0, 0, 0, 0.10)),
    ("CZ phase damping 0.13", (0, 0, 0, 0.13)),
    ("CZ phase damping 0.16", (0, 0, 0, 0.16)),
    ("pulse phase damping 0.10", (0, 0.10, 0, 0)),
)


def scenarios() -> dict[str, tuple[str, float, float, tuple]]:
    """name -> (world, theta, flip, noise), in the fixed order that sets each scenario's generator position."""
    out: dict[str, tuple[str, float, float, tuple]] = {}
    for f in NULL_FLIPS:
        for label, noise in NULL_NOISES:
            out[f"null: flip {f}, {label}"] = ("exact", 0.0, f, noise)
    for name, (world, theta, flip, noise, _) in ps.TRUTHS.items():
        out[f"TRUTHS: {name}"] = (world, theta, flip, noise)
    out["true: q12 phase -0.18 rad, flip 0.0166"] = ("q12_phase", -0.18, 0.0166, ps.NO_NOISE)
    out["true: coupler 8-12 phase -0.25 rad, flip 0.0166"] = ("coupler_phase", -0.25, 0.0166, ps.NO_NOISE)
    out["flip only: flip 0.025, no gate noise"] = ("exact", 0.0, 0.025, ps.NO_NOISE)
    out["flip only: flip 0.05, no gate noise"] = ("exact", 0.0, 0.05, ps.NO_NOISE)
    return out


def base_batches(name: str, spec: tuple[str, float, float, tuple], matrix: np.ndarray) -> list[dict]:
    if name.startswith("MIXED: "):
        return ps.scenario_batches(name[len("MIXED: ") :])
    if len(spec) == 6:
        return drift_batches(spec, matrix)
    world, theta, flip, noise = spec
    return ps.planted_batches(ps.truth_row(world, theta, matrix, flip, noise=noise))


def drift_batches(spec, matrix: np.ndarray) -> list[dict]:
    """Batch k of n in series order takes the truth at fraction k/(n-1) between the start and end theta and flip."""
    world, theta, flip, noise, theta_end, flip_end = spec
    n = len(ps.batch_order())
    out = []
    for k in range(n):
        f = k / (n - 1)
        th = theta + f * (theta_end - theta)
        fl = flip + f * (flip_end - flip)
        out.append(ps.planted_batches(ps.truth_row(world, th, matrix, fl, noise=noise))[k])
    return out


def gap_scenarios() -> dict[str, tuple]:
    """Appended after MIXED so earlier positions and part files keep their generator streams."""
    out: dict[str, tuple] = {}
    for f in (0.036, 0.042):
        out[f"gap: q12 phase -0.18 rad, flip {f}"] = ("q12_phase", -0.18, f, ps.NO_NOISE, -0.18, f)
        out[f"gap: q12 phase +0.18 rad, flip {f}"] = ("q12_phase", 0.18, f, ps.NO_NOISE, 0.18, f)
        out[f"gap: coupler phase -0.25 rad, flip {f}"] = ("coupler_phase", -0.25, f, ps.NO_NOISE, -0.25, f)
        out[f"gap: q8 phase -0.25 rad, flip {f}"] = (ps.Q8_PHASE, -0.25, f, ps.NO_NOISE, -0.25, f)
    out["gap: drift null flip 0 to 0.036"] = ("exact", 0.0, 0.0, ps.NO_NOISE, 0.0, 0.036)
    out["gap: drift null flip 0 to 0.05"] = ("exact", 0.0, 0.0, ps.NO_NOISE, 0.0, 0.05)
    out["gap: drift null flip 0.0166 to 0.036, CZ phase damping 0.13"] = (
        "exact",
        0.0,
        0.0166,
        (0, 0, 0, 0.13),
        0.0,
        0.036,
    )
    out["gap: drift null flip 0.036 to 0.0166, pulse phase damping 0.10"] = (
        "exact",
        0.0,
        0.036,
        (0, 0.10, 0, 0),
        0.0,
        0.0166,
    )
    out["gap: drift q12 phase -0.18 rad, flip 0 to 0.036"] = ("q12_phase", -0.18, 0.0, ps.NO_NOISE, -0.18, 0.036)
    out["gap: drift coupler phase -0.25 rad, flip 0 to 0.036"] = (
        "coupler_phase",
        -0.25,
        0.0,
        ps.NO_NOISE,
        -0.25,
        0.036,
    )
    return out


def all_scenarios() -> dict[str, tuple[str, float, float, tuple] | None]:
    sc: dict = scenarios()
    for m in ps.MIXED:
        sc[f"MIXED: {m}"] = None
    sc.update(gap_scenarios())
    return sc


def flip_matrix(matrix: np.ndarray, f: float) -> np.ndarray:
    return matrix if f == 0 else matrix @ ps.oc.selector_flip(D0, 0, float(f))


def noisy(base: list[dict], draws: np.ndarray) -> list[dict]:
    err = 1 / math.sqrt(ps.SCAN_SHOTS)
    return [
        {
            **b,
            "contrasts": [v + err * draws[n, j] for j, v in enumerate(b["contrasts"])],
            "splits": [v + ps.OC_SPLIT_OFFSET + 2 * err * draws[n, 3 + j] for j, v in enumerate(b["splits"])],
        }
        for n, b in enumerate(base)
    ]


def prelude(batches: list[dict]):
    """The guard and center tests of decide(); returns (label or None, deciding batches, numbers)."""
    admitted = [b for b in batches if b["admitted"]]
    numbers: dict = {}
    z12 = [b for b in admitted if b["kind"] in ps.DECIDING_KINDS]
    if {b["kind"] for b in z12} != set(ps.DECIDING_KINDS):
        return "unresolved_guard", z12, numbers
    center = ps.pooled(
        [(b["contrasts"][b["arms"].index(ps.CENTER)], b["errors"][b["arms"].index(ps.CENTER)]) for b in admitted]
    )
    if center[0] <= ps.Z_RESOLVE * center[1]:
        return ("offset_reversed" if center[0] < -ps.Z_RESOLVE * center[1] else "offset_absent"), z12, numbers
    return None, z12, numbers


class Best:
    """Per world, the least summed chi-square over (flip, noise model) and the per-batch chi-squares there."""

    def __init__(self) -> None:
        self.total = {w: math.inf for w in WORLDS}
        self.flip = {w: None for w in WORLDS}
        self.model = {w: None for w in WORLDS}
        self.per_batch = {w: None for w in WORLDS}
        self.param = {w: None for w in WORLDS}

    def update(self, f: float, w: str, chi: np.ndarray, par: np.ndarray) -> None:
        total = chi.sum(0)
        j = int(total.argmin())
        if total[j] < self.total[w]:
            self.total[w], self.flip[w], self.model[w] = float(total[j]), f, j
            self.per_batch[w], self.param[w] = chi[:, j].copy(), par[:, j].copy()


def fit_flip(z12: list[dict], matrix: np.ndarray, models: str = "all"):
    """Per world, per-batch chi-square (batch, model) and parameter at one assignment matrix."""
    fits = [
        ps.fit_batch(
            tuple(b["arms"]),
            np.array([*b["contrasts"], *ps.relative_splits(b)[0]]),
            np.array([*b["errors"], *ps.relative_splits(b)[1]]),
            matrix,
            b["center_visibility"],
            models,
        )
        for b in z12
    ]
    return {w: (np.stack([f[w]["chi2"] for f in fits]), np.stack([f[w]["parameter"] for f in fits])) for w in WORLDS}


def finish(z12: list[dict], best: Best, extra: int, margin: float = ps.KIND_MARGIN, separation: float = ps.SEPARATION):
    """The label logic of decide() with `extra` further degrees of freedom removed from every world's adequacy limit
    and from the separation scale (extra 0 reproduces decide())."""
    values = [ps.batch_values(b) for b in z12]
    names = [b["name"] for b in z12]
    kinds = [b["kind"] for b in z12]
    bests = dict(best.total)
    free = {w: ps.freedom(w, values) - extra for w in WORLDS}
    limit = {w: float(chi2_law.ppf(1 - ps.ADEQUACY_ALPHA, free[w])) for w in WORLDS}
    adequate = {w: bests[w] <= limit[w] for w in WORLDS}
    per_batch = {w: dict(zip(names, best.per_batch[w], strict=True)) for w in ps.ERROR_WORLDS}
    kind_chi2 = {
        w: {k: sum(per_batch[w][n] for n, kk in zip(names, kinds, strict=True) if kk == k) for k in ps.DECIDING_KINDS}
        for w in per_batch
    }
    bound = {
        k: float(chi2_law.ppf(1 - ps.ADEQUACY_ALPHA, sum(ps.batch_values(b) - 1 for b in z12 if b["kind"] == k)))
        for k in ps.DECIDING_KINDS
    }

    def homogeneous(world: str) -> bool:
        return all(
            v <= bound[k] and all(v <= kind_chi2[o][k] + margin for o in ps.ERROR_WORLDS if o != world)
            for k, v in kind_chi2[world].items()
        )

    lead = min(ps.ERROR_WORLDS, key=lambda w: bests[w])
    scale = max(1.0, bests[lead] / free[lead])
    needed = separation * scale
    if adequate["exact"]:
        label = "exact_parabola"
    elif adequate[lead] and all(bests[lead] <= bests[w] - needed for w in ps.ERROR_WORLDS if w != lead):
        label = lead if homogeneous(lead) else "phase_mixed"
    elif any(adequate[w] for w in ps.ERROR_WORLDS):
        label = "phase_unresolved"
    else:
        label = "none_adequate"
    return label, {"chi2": bests, "limit": limit, "flip": dict(best.flip), "lead": lead, "needed": needed}


def series_labels(series: list[list[dict]], matrix: np.ndarray, flips: list[float], keep_cache: bool = False):
    """For each series, (label with the flip fixed at 0, label with the nuisance, numbers of the nuisance fit,
    state of the flip-0 fit, state of the nuisance fit); the states are Best objects, None for a series that
    decide() ends before fitting."""
    pre = [prelude(bs) for bs in series]
    best0 = [Best() for _ in series]
    bestn = [Best() for _ in series]
    for f in flips:
        m = flip_matrix(matrix, f)
        for i, (lab, z12, _) in enumerate(pre):
            if lab is not None:
                continue
            fit = fit_flip(z12, m)
            for w in WORLDS:
                bestn[i].update(f, w, *fit[w])
                if f == 0:
                    best0[i].update(f, w, *fit[w])
        if not keep_cache:
            ps.SEEN_CACHE.clear()
    out = []
    for i, (lab, z12, _) in enumerate(pre):
        if lab is not None:
            out.append((lab, lab, {}, None, None))
            continue
        l0, n0 = finish(z12, best0[i], 0)
        ln, num = finish(z12, bestn[i], 1)
        out.append(
            (l0, ln, {"current": n0, "nuisance": num} | {"flip": num["flip"], "lead": num["lead"]}, best0[i], bestn[i])
        )
    return out


def pack(best: Best | None):
    """Plain-number state of a fit: per world the sum, flip, noise-model index, and per-batch chi-squares."""
    if best is None:
        return None
    return {
        w: [round(best.total[w], 4), best.flip[w], best.model[w], [round(float(x), 4) for x in best.per_batch[w]]]
        for w in WORLDS
    }


def unpack(state) -> Best:
    b = Best()
    for w, (total, f, model, per) in state.items():
        b.total[w], b.flip[w], b.model[w], b.per_batch[w] = total, f, model, np.array(per)
    return b


def summarize(res0, resn, num):
    """Compact record of one series for both rules."""
    if not num:
        return {"current": res0, "nuisance": resn}
    return {
        "current": res0,
        "nuisance": resn,
        "lead_current": num["current"]["lead"],
        "lead_nuisance": num["nuisance"]["lead"],
        "needed_current": round(num["current"]["needed"], 3),
        "needed_nuisance": round(num["nuisance"]["needed"], 3),
    }


PARTS = "docs/local/rebuild/nuisance/parts"


def run_scenario(item):
    position, name, spec, n_series = item
    import os
    import re

    path = f"{PARTS}/{position:02d}-{re.sub('[^A-Za-z0-9.+-]+', '_', name)}-{n_series}.json"
    if os.path.exists(path):
        return json.load(open(path))
    t0 = time.time()
    matrix = ps.predecessor_matrix()
    base = base_batches(name, spec, matrix)
    rng = np.random.default_rng([SEED, position])
    draws = rng.standard_normal((n_series, len(base), 6))
    series = [base, *(noisy(base, draws[i]) for i in range(n_series))]  # series 0 is the expected-value series
    res = series_labels(series, matrix, FLIPS)
    ps.SEEN_CACHE.clear()
    pairs: dict[str, int] = {}
    cur: dict[str, int] = {}
    nui: dict[str, int] = {}
    lead_flips: dict[str, list[float]] = {}
    exact_flips: list[float] = []
    per_series = []
    for k, (l0, ln, num, b0, bn) in enumerate(res):
        per_series.append(summarize(l0, ln, num) | {"state_current": pack(b0), "state_nuisance": pack(bn)})
        if k == 0:
            continue
        cur[l0] = cur.get(l0, 0) + 1
        nui[ln] = nui.get(ln, 0) + 1
        pairs[f"{l0} -> {ln}"] = pairs.get(f"{l0} -> {ln}", 0) + 1
        if num:
            lead_flips.setdefault(ln, []).append(num["flip"][num["lead"]])
            exact_flips.append(num["flip"]["exact"])
    out = {
        "name": name,
        "position": position,
        "series": n_series,
        "expected": per_series[0],
        "current": dict(sorted(cur.items())),
        "nuisance": dict(sorted(nui.items())),
        "transitions": dict(sorted(pairs.items())),
        "lead_flip_by_label": {
            k: [round(float(np.mean(v)), 5), round(float(np.min(v)), 5), round(float(np.max(v)), 5)]
            for k, v in lead_flips.items()
        },
        "exact_world_flip": (
            [
                round(float(np.mean(exact_flips)), 5),
                round(float(np.min(exact_flips)), 5),
                round(float(np.max(exact_flips)), 5),
            ]
            if exact_flips
            else None
        ),
        "seconds": round(time.time() - t0, 2),
        "per_series": per_series,
    }
    os.makedirs(PARTS, exist_ok=True)
    json.dump(out, open(path + ".tmp", "w"))
    os.replace(path + ".tmp", path)
    print(
        f"done {name} {n_series} series {out['seconds']}s current {out['current']} nuisance {out['nuisance']}",
        flush=True,
    )
    return out


def check() -> None:
    """(1) matched_shared equals ps.matched bit for bit; (2) the flip-0 slice equals ps.decide() on noisy series;
    (3) known-good: a flip-only truth on the grid reads exact_parabola with exact-world chi-square near 0 at its
    own flip."""
    ps.build_tables()
    matrix = ps.predecessor_matrix()
    for world in WORLDS:
        for k in (0.0, 1.25):
            table = ps.world_table(world, k)
            for arms in (
                ("b0-rxz-z12-m10", ps.CENTER, "b0-rxz-z12-p10"),
                ("b0-rxz-z8c-p10", ps.CENTER, "b0-rxz-z8c-m10"),
            ):
                for f in (0.0, 0.025):
                    m = flip_matrix(matrix, f)
                    for mix in (0.0, 0.5):
                        got, ref = matched_shared(table, arms, m, 0.4, mix), _MATCHED(table, arms, m, 0.4, mix)
                        if not all(np.array_equal(x, y) for x, y in zip(got, ref, strict=True)):
                            raise ValueError(f"matched_shared differs from ps.matched: {world} {k} {arms} {f} {mix}")
    print(
        "check ok: matched_shared == ps.matched (bitwise) on 4 worlds x 2 tables x 2 arm sets x 2 flips x 2 mixes",
        flush=True,
    )
    sc = all_scenarios()
    for pos in (0, 6, 20, 26, 40, 41):
        name = list(sc)[pos]
        base = base_batches(name, sc[name], matrix)
        rng = np.random.default_rng([SEED, pos])
        draws = rng.standard_normal((6, len(base), 6))
        series = [base, *(noisy(base, draws[i]) for i in range(5))]
        mine = series_labels(series, matrix, [0.0])
        for bs, (l0, _ln, _num, b0, _bn) in zip(series, mine, strict=True):
            d = ps.decide(bs, lambda _b: matrix, flips=(0.0,))
            if d["label"] != l0:
                raise ValueError(f"{name}: decide reads {d['label']}, slice reads {l0}")
            if b0 is not None:
                for w in WORLDS:
                    if abs(round(b0.total[w], 3) - d["numbers"]["chi2"][w]) > 1e-9:
                        raise ValueError(f"{name}: chi2 differs for {w}")
        print(f"check ok: {name}: decide() == flip-0 slice on 6 series: {[x[0] for x in mine]}", flush=True)
        ps.SEEN_CACHE.clear()
    for f in (0.025,):
        pb = ps.planted_batches(ps.truth_row("exact", 0.0, matrix, f))
        ((l0, ln, num, b0, bn),) = series_labels([pb], matrix, FLIPS)
        print(
            f"known-good flip-only {f}: current {l0}, nuisance {ln}, exact chi2 {bn.total['exact']:.4f} "
            f"at flip {bn.flip['exact']}, exact chi2 at flip 0 {b0.total['exact']:.3f}",
            flush=True,
        )
        if ln != "exact_parabola" or bn.flip["exact"] != f or bn.total["exact"] > 1e-3:
            raise ValueError("known-good flip-only truth is not recovered")


def timing() -> None:
    """Cold cost of the nuisance fit (one series, empty caches) and the marginal cost per further series on the
    warm cache, against decide() on the same series, for one scenario."""
    ps.build_tables()
    matrix = ps.predecessor_matrix()
    sc = all_scenarios()
    name = "null: flip 0.025, CZ phase damping 0.13"
    base = base_batches(name, sc[name], matrix)
    rng = np.random.default_rng([SEED, 999])
    draws = rng.standard_normal((20, len(base), 6))
    series = [noisy(base, draws[i]) for i in range(20)]
    ps.SEEN_CACHE.clear()
    _RETENTION.clear()
    t = time.time()
    ps.decide(series[0], lambda _b: matrix, flips=(0.0,))
    cold = time.time() - t
    t = time.time()
    for bs in series:
        ps.decide(bs, lambda _b: matrix, flips=(0.0,))
    warm = (time.time() - t) / len(series)
    ps.SEEN_CACHE.clear()
    _RETENTION.clear()
    t = time.time()
    series_labels(series[:1], matrix, FLIPS, keep_cache=True)
    nui1 = time.time() - t
    t = time.time()
    series_labels(series, matrix, FLIPS, keep_cache=True)
    nui20 = time.time() - t
    print(
        json.dumps(
            {
                "scenario": name,
                "load_average": list(__import__("os").getloadavg()),
                "current_cold_first_series_s": round(cold, 3),
                "current_warm_per_series_s": round(warm, 4),
                "nuisance_cold_1_series_s": round(nui1, 2),
                "nuisance_warm_20_series_s": round(nui20, 2),
                "nuisance_warm_per_series_s": round(nui20 / 20, 3),
            }
        ),
        flush=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--run", type=int)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.time:
        timing()
    elif a.run:
        ps.build_tables()
        sc = all_scenarios()
        items = [(n, name, spec, a.run) for n, (name, spec) in enumerate(sc.items()) if a.only in name]
        ordered_map(run_scenario, items, min_items=2)


if __name__ == "__main__":
    main()
