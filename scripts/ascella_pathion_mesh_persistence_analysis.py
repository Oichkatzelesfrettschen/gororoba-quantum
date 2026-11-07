"""The preregistered reading of the Ascella mesh-persistence case (scripts/ascella_pathion_mesh_persistence.py).

`--mesh-gate SIM_RUN` compares the served unitary of every replay iteration of the `sim:ascella` run with the one the
original QPU job served under the same setting (largest entry modulus at most the case's mesh identity tolerance) and
exits 1 on any miss, so the QPU job is not sent. `--analyze QPU_RUN --out FILE` writes every decision of the case
docstring with its numbers.

Levels. A row's raw level a = 2 x (slot clicks) / (clicks in modes 0 to 8) carries no calibration; the calibrated
level l_hat divides by the slot efficiencies of an anchor pair (ascella_pathion_coset_block_pairs_analysis.calibrate).
The persistence and correction decisions read l_hat with the replayed anchors, the quantity whose mirror test failed;
the fresh-failing and frozen-map decisions read a, so no anchor calibration enters a comparison of meshes; the
fresh-anchor decision forms each seed's B/A from that seed's two anchor iterations and the fresh dark.

Random draws: one numpy generator seeded with the case's permutation value (draw layout "permutation") draws the
persistence relabelings first and the fresh-failing relabelings second.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "docs/evidence/pathion-kernel-map/conjectures"))
import ascella_pathion_mesh_persistence as case  # noqa: E402

an = importlib.import_module("ascella_pathion_coset_block_pairs_analysis")
SCHEMA = "ascella-pathion-mesh-persistence-analysis-v1"


def load(run: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Manifest, settings and observation rows of one run directory."""
    manifest = json.loads((run / "cases.json").read_bytes())
    results = json.loads((run / "results.json").read_bytes())
    reg = manifest["preregistered"]
    modes = {"slots": reg["slot_modes"], "failure": reg["failure_mode"], "sentinel": reg["sentinel_modes"]}
    samples = manifest["max_samples"] // manifest["iterations"]
    cap = manifest["max_shots"] // manifest["iterations"]
    settings = manifest["settings"]
    rows = [
        an.observation((i, s, e, samples, cap, modes))
        for i, (s, e) in enumerate(zip(settings, results["iterations"], strict=True))
    ]
    return manifest, settings, rows


def served_unitaries(run: Path) -> list[np.ndarray]:
    from perceval.serialization import deserialize  # noqa: PLC0415

    results = json.loads((run / "results.json").read_bytes())
    return [
        np.asarray(deserialize(e["result_fields"]["computed_circuit"]).compute_unitary()) for e in results["iterations"]
    ]


def mesh_gate(sim_run: Path) -> dict[str, Any]:
    manifest = json.loads((sim_run / "cases.json").read_bytes())
    tolerance = manifest["preregistered"]["thresholds"]["mesh_identity_tolerance"]
    original = ROOT / case.ORIGINAL_RUN
    names = [s["name"] for s in json.loads((original / "cases.json").read_bytes())["settings"]]
    reference = dict(zip(names, served_unitaries(original), strict=True))
    served = served_unitaries(sim_run)
    misses, worst = [], 0.0
    for setting, unitary in zip(manifest["settings"], served, strict=True):
        if setting["kind"] != "replay":
            continue
        gap = float(np.max(np.abs(unitary - reference[setting["original_name"]])))
        worst = max(worst, gap)
        if gap > tolerance:
            misses.append({"setting": setting["name"], "gap": gap})
    return {"replay_iterations": 52, "worst_gap": worst, "misses": misses, "passed": not misses}


def mirror(rows: list[dict[str, Any]], settings: list[dict[str, Any]], calibration: dict[str, Any] | None, key: str):
    """Signed differences l(o0) - l(o1) per (setting, item) over sign and null settings present in both orientations."""
    found: dict[tuple[str, int], dict[int, float]] = {}
    for row, setting in zip(rows, settings, strict=True):
        if not row["returned"] or setting["role"] not in ("sign", "null"):
            continue
        o = setting["orientation"]
        levels = an.slot_levels(row, calibration) if calibration else None
        for item in (0, 1):
            slot = an.SLOTS[item if o == 0 else 1 - item]
            value = levels[slot][key] if levels else 2 * row["slot"][slot] / row["total"]
            found.setdefault((setting["setting"], item), {})[o] = value
    return {k: v[0] - v[1] for k, v in sorted(found.items()) if set(v) == {0, 1}}


def permutation_p(x: np.ndarray, y: np.ndarray, rng: np.random.Generator, count: int) -> float:
    observed = float(np.corrcoef(x, y)[0, 1])
    draws = np.array([np.corrcoef(x, rng.permutation(y))[0, 1] for _ in range(count)])
    return float((1 + np.sum(draws >= observed)) / (count + 1))


def subset(rows, settings, kinds):
    picked = [(r, s) for r, s in zip(rows, settings, strict=True) if s["kind"] in kinds]
    return [r for r, _ in picked], [s for _, s in picked]


def frozen_map_prediction(run: Path, settings: list[dict[str, Any]], kinds: tuple[str, ...]) -> dict[str, Any]:
    """Raw slot levels the frozen c1_static maps predict for each iteration of the given kinds."""
    import c1_mesh  # noqa: PLC0415
    from perceval.serialization import deserialize  # noqa: PLC0415

    kinds0, lo0, _, _, _ = c1_mesh.cached(ROOT / case.ORIGINAL_RUN, "pairs")
    maps = np.load(ROOT / "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz")
    results = json.loads((run / "results.json").read_bytes())
    out: dict[str, Any] = {"gain": {}, "offset": {}}
    for i, (setting, entry) in enumerate(zip(settings, results["iterations"], strict=True)):
        if setting["kind"] not in kinds:
            continue
        circuit = deserialize(entry["result_fields"]["computed_circuit"])
        topo: list[tuple[str, int]] = []
        th: list[float] = []
        ph: list[float] = []
        for rng, comp in circuit._components:
            kind = type(comp).__name__
            topo.append((kind, rng[0]))
            (th if kind == "BS" else ph).append(float(comp.get_parameters(all_params=True)[0]))
        if [k for k, _ in topo] != list(kinds0) or [m for _, m in topo] != list(lo0):
            raise ValueError(f"{setting['name']}: the served mesh topology differs from the frozen maps'")
        th_a, ph_a = np.array(th), np.array(ph)
        for model in ("gain", "offset"):
            x, a, c = (maps[f"{part}_{model}_all"] for part in ("x", "a", "c"))
            dph = (x * ph_a)[None, :] if model == "gain" else x[None, :]
            p = c1_mesh.propagate(kinds0, lo0, th_a, ph_a, dph=dph)[0]
            w = np.exp(a) * p + 1e-4 * np.exp(c)
            q = w / w.sum()
            total = q[: case.pairs.ACTIVE].sum()
            out[model][i] = [2 * float(q[list(m)].sum()) / total for m in case.pairs.SLOT_MODES.values()]
    return out


def analyze(run: Path) -> dict[str, Any]:
    manifest, settings, rows = load(run)
    reg = manifest["preregistered"]
    th = reg["thresholds"]
    layout = manifest["seed_source"]["layout"]
    draw = json.loads((ROOT / manifest["seed_source"]["sources"][0].split(":", 1)[1].split("#")[0]).read_bytes())
    rng = np.random.default_rng(draw["values"][layout["permutation"][0]])
    report: dict[str, Any] = {"schema": SCHEMA, "run": run.relative_to(ROOT).as_posix()}
    if not all(r["returned"] for r in rows):
        report["reading"] = "partial: an iteration returned no counts; no decision is read"
        return report

    # Admission on the replayed anchors and darks.
    r_rows, r_set = subset(rows, settings, ("replay",))
    cal = an.calibrate(r_rows, r_set)
    adm = reg["admission_thresholds"]
    report["admission"] = {
        "anchor_raw": cal["anchor_raw"],
        "dark": cal["dark"],
        "max_sentinel_share": max(r["sentinel_share"] for r in rows),
        "passed": min(cal["anchor_raw"].values()) >= adm["anchor_floor"]
        and max(cal["dark"].values()) <= adm["dark_ceiling"]
        and max(r["sentinel_share"] for r in rows) <= adm["sentinel_share"],
    }

    # Persistence of the 46 calibrated mirror differences, and the raw secondary.
    _, o_set, o_rows = load(ROOT / case.ORIGINAL_RUN)
    o_cal = an.calibrate(o_rows, o_set)
    for key, label in (("l_hat", "calibrated"), ("a", "raw")):
        new = mirror(r_rows, r_set, cal if key == "l_hat" else None, key)
        old = mirror(o_rows, [{**s, "kind": "replay"} for s in o_set], o_cal if key == "l_hat" else None, key)
        keys = sorted(set(new) & set(old))
        x, y = np.array([old[k] for k in keys]), np.array([new[k] for k in keys])
        noise = 2 * case.level_se(0.6) ** 2
        bound = case.persistence_bound(list(x), noise, len(keys))
        r = float(np.corrcoef(x, y)[0, 1])
        p = permutation_p(x, y, rng, reg["permutations"]) if label == "calibrated" else None
        entry = {
            "pairs": len(keys),
            "r": r,
            "bound": bound,
            "replay_failing": int(np.sum(np.abs(y) > th["mirror_spread"])),
        }
        if p is not None:
            entry["p"] = p
            entry["reading"] = (
                "fixed per mesh"
                if p < reg["alpha"] and r >= bound["fisher_lower_99"]
                else ("partly fixed" if p < reg["alpha"] else "not reproduced")
            )
        report[f"persistence_{label}"] = entry

    # Anchor replay ratio.
    ba = cal["efficiency"]["B"] / cal["efficiency"]["A"]
    report["anchor_replay"] = {
        "ba": ba,
        "original_ba": reg["original_ba"],
        "reading": "anchor error fixed per mesh"
        if abs(ba - reg["original_ba"]) <= th["anchor_replay_band"]
        else "anchor ratio moved",
    }

    # Fresh anchors: one B/A per seed, with the fresh dark.
    darks = [(r, s) for r, s in zip(rows, settings, strict=True) if s["kind"] == "fresh-dark"]
    ratios = []
    for seed in sorted({s["compilation_seed"] for s in settings if s["kind"] == "fresh-anchor"}):
        pair = [
            (r, s)
            for r, s in zip(rows, settings, strict=True)
            if s["kind"] == "fresh-anchor" and s["compilation_seed"] == seed
        ]
        c = an.calibrate([r for r, _ in pair + darks], [s for _, s in pair + darks])
        ratios.append(c["efficiency"]["B"] / c["efficiency"]["A"])
    median, spread = float(np.median(ratios)), float(np.std(ratios, ddof=1))
    if abs(median - reg["mode_fit_ba"]) <= th["fresh_band"] and spread > th["spread_floor"]:
        fresh_reading = "anchor ratio follows the mesh"
    elif all(abs(v - reg["original_ba"]) <= th["fresh_band"] for v in ratios):
        fresh_reading = "slot efficiency"
    else:
        fresh_reading = "unresolved"
    report["fresh_anchors"] = {"ba": ratios, "median": median, "sd": spread, "reading": fresh_reading}

    # Fresh failing settings against the original, raw levels.
    f_rows, f_set = subset(rows, settings, ("fresh-failing",))
    fresh = mirror(f_rows, f_set, None, "a")
    old_raw = mirror(o_rows, [{**s, "kind": "replay"} for s in o_set], None, "a")
    items = [tuple(i) for i in reg["failing_items"]]
    x = np.array([old_raw[i] for i in items])
    y = np.array([fresh[i] for i in items])
    r_f = float(np.corrcoef(x, y)[0, 1])
    p_f = permutation_p(x, y, rng, reg["permutations"])
    report["fresh_failing"] = {
        "items": [f"{a}/{b}" for a, b in items],
        "original_raw_d": x.tolist(),
        "fresh_raw_d": y.tolist(),
        "r": r_f,
        "p": p_f,
        "reading": "failure follows the block and slot"
        if r_f >= th["block_r"] and p_f < reg["alpha"]
        else "failure follows the mesh",
    }

    # Frozen per-shifter maps on the fresh iterations, raw levels, centered within kind.
    kinds = ("fresh-anchor", "fresh-failing", "fresh-dark")
    predicted = frozen_map_prediction(run, settings, kinds)
    maps = {}
    for model, pred in predicted.items():
        obs, mod, groups = [], [], []
        for i, levels in pred.items():
            row, setting = rows[i], settings[i]
            for k, slot in enumerate(an.SLOTS):
                ideal = setting["ideal_levels"][k]
                obs.append(2 * row["slot"][slot] / row["total"] - ideal)
                mod.append(levels[k] - ideal)
                groups.append(setting["kind"])
        obs_a, mod_a, g = np.array(obs), np.array(mod), np.array(groups)
        for kind in set(groups):
            obs_a[g == kind] -= obs_a[g == kind].mean()
            mod_a[g == kind] -= mod_a[g == kind].mean()
        n, groups_n = len(obs_a), len(set(groups))
        r_m = float(np.corrcoef(obs_a, mod_a)[0, 1])
        dof = n - 1 - groups_n
        t = r_m * math.sqrt(dof / max(1e-12, 1 - r_m**2))
        p_m = float(stats.t.sf(t, dof))
        counting = case.level_se(0.6) ** 2
        ceiling = max(float(np.var(obs_a, ddof=1)) - counting, 0.0) / float(np.var(obs_a, ddof=1))
        maps[model] = {
            "n": n,
            "r": r_m,
            "p_one_sided": p_m,
            "share": (r_m**2 / ceiling) if r_m > 0 and ceiling > 0 else 0.0,
            "reading": "map carries" if p_m < reg["map_alpha"] else "map does not carry",
        }
    report["frozen_maps"] = maps

    # Per-mesh correction table from the original job applied to the replay, calibrated levels.
    table = {}
    for row, setting in zip(o_rows, o_set, strict=True):
        if setting["role"] in ("sign", "null"):
            lv = an.slot_levels(row, o_cal)
            for k, slot in enumerate(an.SLOTS):
                table[(setting["name"], slot)] = lv[slot]["l_hat"] - setting["ideal_levels"][k]
    corrected_rows = list(zip(r_rows, r_set, strict=True))
    before = mirror(r_rows, r_set, cal, "l_hat")
    found: dict[tuple[str, int], dict[int, float]] = {}
    for row, setting in corrected_rows:
        if setting["role"] not in ("sign", "null"):
            continue
        o = setting["orientation"]
        lv = an.slot_levels(row, cal)
        for item in (0, 1):
            slot = an.SLOTS[item if o == 0 else 1 - item]
            value = lv[slot]["l_hat"] - table[(setting["original_name"], slot)]
            found.setdefault((setting["setting"], item), {})[o] = value
    after = {k: v[0] - v[1] for k, v in found.items() if set(v) == {0, 1}}
    b, a_ = np.array(list(before.values())), np.array([after[k] for k in before])
    report["correction"] = {
        "failing_before": int(np.sum(np.abs(b) > th["mirror_spread"])),
        "failing_after": int(np.sum(np.abs(a_) > th["mirror_spread"])),
        "rms_before": float(np.sqrt(np.mean(b**2))),
        "rms_after": float(np.sqrt(np.mean(a_**2))),
        "passed": int(np.sum(np.abs(a_) > th["mirror_spread"])) <= th["mirror_allowance"],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--mesh-gate", type=Path)
    parser.add_argument("--analyze", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.mesh_gate:
        gate = mesh_gate(args.mesh_gate.resolve())
        print(json.dumps(gate, indent=1, sort_keys=True))
        return 0 if gate["passed"] else 1
    if args.analyze is None or args.out is None:
        parser.error("--mesh-gate RUN, or --analyze RUN with --out FILE")
    report = analyze(args.analyze.resolve())
    args.out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
