"""The preregistered reading of the Ascella mesh-persistence case (scripts/ascella_pathion_mesh_persistence.py).

`--mesh-gate SIM_RUN` checks the `sim:ascella` run against the frozen sim-00 case (manifest bytes, result count, echoed
requests, the 52 replay names once each) and the served unitary of every replay iteration against the one the original
QPU job served under the same setting; it exits 1 on any miss, so the QPU job is not sent. `--analyze QPU_RUN --out
FILE` writes every decision of the case docstring with its numbers. `--persistence-plan OUT` writes the fixed-mesh
distribution of the persistence statistic and the fresh-anchor classification rates that freeze the case's cutoffs.

Levels. A row's raw level a = 2 x (slot clicks) / (clicks in modes 0 to 8) carries no calibration; the calibrated
level l_hat divides by the slot efficiencies of an anchor pair (ascella_pathion_coset_block_pairs_analysis.calibrate).
The persistence and correction decisions read l_hat with the replayed anchors, the quantity whose mirror test failed;
the fresh-failing and frozen-map decisions read a, so no anchor calibration enters a comparison of meshes; each
fresh-anchor B/A comes from that seed's two anchor iterations and the fresh dark.

Random draws. The case's draw value "permutation" seeds one generator that draws the persistence relabelings; value
"map_permutation" seeds the seed-block relabelings of the two frozen maps, gain first. The persistence plan uses its
own draw (PLAN_DRAW in the builder): value 0 the fixed-mesh resampling, value 1 the fresh-anchor classification.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "docs/evidence/pathion-kernel-map/conjectures"))
import ascella_pathion_mesh_persistence as case  # noqa: E402

an = importlib.import_module("ascella_pathion_coset_block_pairs_analysis")
SCHEMA = "ascella-pathion-mesh-persistence-analysis-v2"
NOT_READ = "not read"


def modes_of(manifest: dict[str, Any]) -> dict[str, Any]:
    reg = manifest["preregistered"]
    return {"slots": reg["slot_modes"], "failure": reg["failure_mode"], "sentinel": reg["sentinel_modes"]}


def load(run: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Manifest, settings and observation rows of one run directory."""
    manifest = json.loads((run / "cases.json").read_bytes())
    results = json.loads((run / "results.json").read_bytes())
    samples = manifest["max_samples"] // manifest["iterations"]
    cap = manifest["max_shots"] // manifest["iterations"]
    settings = manifest["settings"]
    if len(results["iterations"]) != len(settings):
        raise ValueError(f"{run.name}: {len(results['iterations'])} results for {len(settings)} settings")
    rows = [
        an.observation((i, s, e, samples, cap, modes_of(manifest)))
        for i, (s, e) in enumerate(zip(settings, results["iterations"], strict=True))
    ]
    return manifest, settings, rows


def original() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    manifest, settings, rows = load(ROOT / case.ORIGINAL_RUN)
    return manifest, [{**s, "kind": "replay", "original_name": s["name"]} for s in settings], rows


def served_unitaries(run: Path) -> list[np.ndarray]:
    from perceval.serialization import deserialize  # noqa: PLC0415

    results = json.loads((run / "results.json").read_bytes())
    return [
        np.asarray(deserialize(e["result_fields"]["computed_circuit"]).compute_unitary()) for e in results["iterations"]
    ]


def mesh_gate(sim_run: Path, frozen: Path | None = None) -> dict[str, Any]:
    frozen = frozen or ROOT / "results/quandela/cases/ascella_pathion_mesh_persistence/sim-00"
    problems: list[str] = []
    data = (sim_run / "cases.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != hashlib.sha256((frozen / "cases.json").read_bytes()).hexdigest():
        problems.append("cases.json differs from the frozen sim-00 case")
    manifest = json.loads(data)
    results = json.loads((sim_run / "results.json").read_bytes())["iterations"]
    settings = manifest["settings"]
    if len(results) != case.ITERATIONS or len(settings) != case.ITERATIONS:
        problems.append(f"{len(results)} results and {len(settings)} settings, {case.ITERATIONS} required")
    for setting, entry in zip(settings, results, strict=False):
        echoed = entry.get("iteration", {})
        if any(echoed.get(k) != setting[k] for k in ("compilation_seed", "circuit_params")):
            problems.append(f"{setting['name']}: the echoed request differs")
    names = [s["original_name"] for s in settings if s.get("kind") == "replay"]
    expected = [s["name"] for s in json.loads((ROOT / case.ORIGINAL_RUN / "cases.json").read_bytes())["settings"]]
    if sorted(names) != sorted(expected):
        problems.append(f"replay names: {len(names)} present, {len(set(names))} distinct, {len(expected)} required")
    misses, worst, compared = [], 0.0, 0
    if not problems:
        tolerance = manifest["preregistered"]["thresholds"]["mesh_identity_tolerance"]
        reference = dict(zip(expected, served_unitaries(ROOT / case.ORIGINAL_RUN), strict=True))
        for setting, unitary in zip(settings, served_unitaries(sim_run), strict=True):
            if setting["kind"] != "replay":
                continue
            compared += 1
            gap = float(np.max(np.abs(unitary - reference[setting["original_name"]])))
            worst = max(worst, gap)
            if gap > tolerance:
                misses.append({"setting": setting["name"], "gap": gap})
    return {
        "replay_compared": compared,
        "worst_gap": worst,
        "misses": misses,
        "problems": problems,
        "passed": not problems and not misses and compared == 52,
    }


def finite_r(x: np.ndarray, y: np.ndarray) -> float | None:
    """Pearson r, or None when an input is non-finite, too short or constant (an identifiability failure)."""
    if len(x) < 3 or not (np.all(np.isfinite(x)) and np.all(np.isfinite(y))) or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def mirror(rows: list[dict[str, Any]], settings: list[dict[str, Any]], calibration: dict[str, Any] | None, key: str):
    """Signed differences l(o0) - l(o1) per (setting, item) over sign and null settings read in both orientations."""
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


def row_from_counts(index: int, setting: dict[str, Any], counts: np.ndarray, modes: dict[str, Any]) -> dict[str, Any]:
    slot = {name: float(sum(counts[m] for m in modes["slots"][name])) for name in an.SLOTS}
    failure = float(counts[modes["failure"]])
    sentinel = float(sum(counts[m] for m in modes["sentinel"]))
    return {
        "index": index,
        "name": setting["name"],
        "returned": True,
        "port_counts": [float(c) for c in counts],
        "slot": slot,
        "failure": failure,
        "sentinel": sentinel,
        "total": sum(slot.values()) + failure,
        "sentinel_share": sentinel / max(1.0, float(counts.sum())),
    }


def persistence_r(
    old_rows: list[dict[str, Any]],
    old_set: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
    new_set: list[dict[str, Any]],
) -> tuple[float | None, np.ndarray, np.ndarray]:
    old = mirror(old_rows, old_set, an.calibrate(old_rows, old_set), "l_hat")
    new = mirror(new_rows, new_set, an.calibrate(new_rows, new_set), "l_hat")
    keys = sorted(set(old) & set(new))
    x, y = np.array([old[k] for k in keys]), np.array([new[k] for k in keys])
    return finite_r(x, y), x, y


def fresh_anchor_reading(ratios: list[float], th: dict[str, Any]) -> str:
    median, spread = float(np.median(ratios)), float(np.std(ratios, ddof=1))
    if abs(median - case.MODE_FIT_BA) <= th["fresh_band"] and spread > th["spread_floor"]:
        return "anchor ratio follows the mesh"
    if all(abs(v - case.ORIGINAL_BA) <= th["fresh_band"] for v in ratios):
        return "slot efficiency"
    return "unresolved"


def aligned_power() -> dict[str, float]:
    """Error rates of the aligned-mean rule under the two readings, normal with the preregistered spread."""
    th = {
        k: float(case.PREREGISTERED[k])
        for k in ("per_mesh_raw_sd", "original_failing_raw_mean", "aligned_block", "aligned_mesh")
    }
    se = th["per_mesh_raw_sd"] / math.sqrt(len(case.FAILING_ITEMS))

    def phi(z: float) -> float:
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))

    design = th["original_failing_raw_mean"]
    return {
        "standard_error": se,
        "design_reads_follows_design": 1 - phi((th["aligned_block"] - design) / se),
        "design_reads_follows_mesh": phi((th["aligned_mesh"] - design) / se),
        "mesh_reads_follows_mesh": phi(th["aligned_mesh"] / se),
        "mesh_reads_follows_design": 1 - phi(th["aligned_block"] / se),
    }


def persistence_plan(replicates: int = 2000) -> dict[str, Any]:
    """Fixed-mesh distribution of the persistence r, and fresh-anchor classification rates.

    Fixed-mesh model: the original job's per-iteration click law (its observed port shares) is each mesh's true law;
    the original and the replay are two independent multinomial draws at SAMPLES from those laws, each calibrated with
    its own anchor and dark rows, so the statistic carries heteroskedastic counting noise and both runs' calibration
    noise. The cutoff is the first percentile of r. Fresh anchors: seven B/A drawn normal around the per-mesh reading
    (0.992, sd 0.025 from the original no-division mirror rms) and around the slot reading (1.082, the counting sd
    sqrt(2) x level_se(1)), each classified by the preregistered rule."""
    manifest, settings, rows = original()
    draw = json.loads((ROOT / case.PLAN_DRAW).read_bytes())["values"]
    rng = np.random.default_rng(draw[0])
    modes = modes_of(manifest)
    laws = [np.array(r["port_counts"], float) / sum(r["port_counts"]) for r in rows]
    values = []
    for _ in range(replicates):
        pair = [
            [
                row_from_counts(i, s, rng.multinomial(case.SAMPLES, p), modes)
                for i, (s, p) in enumerate(zip(settings, laws, strict=True))
            ]
            for _ in range(2)
        ]
        r, _, _ = persistence_r(pair[0], settings, pair[1], settings)
        values.append(np.nan if r is None else r)
    v = np.array(values)
    rng2 = np.random.default_rng(draw[1])
    th = case.PREREGISTERED
    rates: dict[str, dict[str, float]] = {}
    models = {"per_mesh": (case.MODE_FIT_BA, 0.025), "slot": (case.ORIGINAL_BA, math.sqrt(2) * case.level_se(1.0))}
    for truth, (centre, sd) in models.items():
        counts = {"anchor ratio follows the mesh": 0, "slot efficiency": 0, "unresolved": 0}
        for _ in range(20000):
            counts[fresh_anchor_reading(list(rng2.normal(centre, sd, case.FRESH_ANCHOR_SEEDS)), th)] += 1
        rates[truth] = {k: c / 20000 for k, c in counts.items()}
    return {
        "replicates": replicates,
        "plan_draw": case.PLAN_DRAW,
        "r_quantiles": {str(q): float(np.nanquantile(v, q)) for q in (0.001, 0.01, 0.05, 0.5)},
        "non_finite": int(np.sum(~np.isfinite(v))),
        "persistence_cutoff": round(float(np.nanquantile(v, 0.01)), 4),
        "fresh_anchor_classification": rates,
        "aligned_mean": aligned_power(),
    }


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
            if kind == "BS" and comp._convention.name != "Rx":
                raise ValueError(f"{setting['name']}: a served beam splitter is not BS.Rx")
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


def map_score(
    rows: list[dict[str, Any]],
    settings: list[dict[str, Any]],
    pred: dict[int, list[float]],
    rng: np.random.Generator,
    permutations: int,
    alpha: float,
) -> dict[str, Any]:
    """Seed-block permutation test of one frozen map on raw slot-level departures, centered within kind.

    Each compilation seed contributes the readings of both its orientations and both slots; a relabeling moves the
    predictions of whole seed blocks of equal size, so the readings that share a seed or an iteration stay together."""
    obs, mod, kind, block, var = [], [], [], [], []
    for i, levels in pred.items():
        row, setting = rows[i], settings[i]
        for k, slot in enumerate(an.SLOTS):
            ideal = setting["ideal_levels"][k]
            a = 2 * row["slot"][slot] / row["total"]
            obs.append(a - ideal)
            mod.append(levels[k] - ideal)
            kind.append(setting["kind"])
            block.append(setting["compilation_seed"])
            share = a / 2
            var.append(4 * share * (1 - share) / row["total"])
    o, m, g, b = np.array(obs), np.array(mod), np.array(kind), np.array(block)
    for k in set(kind):
        o[g == k] -= o[g == k].mean()
        m[g == k] -= m[g == k].mean()
    r = finite_r(o, m)
    if r is None:
        return {"reading": NOT_READ}
    seeds = sorted(set(block))
    members = {s: np.flatnonzero(b == s) for s in seeds}
    sizes = {len(v) for v in members.values()}
    if len(sizes) != 1:
        raise ValueError(f"seed blocks of unequal size {sorted(sizes)}")
    hits = 0
    for _ in range(permutations):
        order = rng.permutation(len(seeds))
        shuffled = np.empty_like(m)
        for s, j in zip(seeds, order, strict=True):
            shuffled[members[s]] = m[members[seeds[j]]]
        hits += int(float(np.corrcoef(o, shuffled)[0, 1]) >= r)
    p = (1 + hits) / (permutations + 1)
    ceiling = 1 - float(np.mean(var)) / float(np.var(o, ddof=1))
    return {
        "n_readings": len(o),
        "n_seed_blocks": len(seeds),
        "r": r,
        "p_one_sided": p,
        "ceiling": ceiling,
        "share": (r**2 / ceiling) if r > 0 and ceiling > 0 else 0.0,
        "reading": "map carries" if p < alpha else "map does not carry",
    }


def analyze(run: Path) -> dict[str, Any]:
    manifest, settings, rows = load(run)
    reg = manifest["preregistered"]
    th = reg["thresholds"]
    layout = manifest["seed_source"]["layout"]
    draw_path = ROOT / manifest["seed_source"]["sources"][0].split(":", 1)[1].split("#")[0]
    draw = json.loads(draw_path.read_bytes())["values"]
    rng = np.random.default_rng(draw[layout["permutation"][0]])
    rng_map = np.random.default_rng(draw[layout["map_permutation"][0]])
    report: dict[str, Any] = {"schema": SCHEMA, "run": run.relative_to(ROOT).as_posix()}
    if not all(r["returned"] for r in rows):
        report["reading"] = "partial: an iteration returned no counts; no decision is read"
        return report

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

    _, o_set, o_rows = original()
    o_cal = an.calibrate(o_rows, o_set)
    r_value, x, y = persistence_r(o_rows, o_set, r_rows, r_set)
    entry: dict[str, Any] = {"pairs": len(x), "cutoff": th["persistence_cutoff"]}
    if r_value is None:
        entry["reading"] = NOT_READ
    else:
        draws = [finite_r(x, rng.permutation(y)) for _ in range(reg["permutations"])]
        p = (1 + sum(1 for d in draws if d is not None and d >= r_value)) / (reg["permutations"] + 1)
        entry.update({"r": r_value, "p": p, "replay_failing": int(np.sum(np.abs(y) > th["mirror_spread"]))})
        if r_value >= th["persistence_cutoff"]:
            entry["reading"] = "fixed per mesh"
        else:
            entry["reading"] = "partly fixed" if p < reg["alpha"] else "not reproduced"
    raw_old = mirror(o_rows, o_set, None, "a")
    raw_new = mirror(r_rows, r_set, None, "a")
    keys = sorted(set(raw_old) & set(raw_new))
    entry["raw_r"] = finite_r(np.array([raw_old[k] for k in keys]), np.array([raw_new[k] for k in keys]))
    report["persistence"] = entry

    # Time-ordered control inside the job: early and late replay halves, early and late replayed anchors.
    positions = sorted(s["observation_index"] for s in r_set)
    middle = positions[len(positions) // 2]
    old_cal_d = mirror(o_rows, o_set, o_cal, "l_hat")
    halves: dict[str, float | None] = {}
    for label, late in (("early", False), ("late", True)):
        hr = [(r, s) for r, s in zip(r_rows, r_set, strict=True) if (s["observation_index"] >= middle) == late]
        new = mirror([r for r, _ in hr], [s for _, s in hr], cal, "l_hat")
        ks = sorted(set(new) & set(old_cal_d))
        halves[label] = finite_r(np.array([old_cal_d[k] for k in ks]), np.array([new[k] for k in ks]))
    anchors = sorted(
        (s["observation_index"], 2 * r["slot"][an.SLOTS[s["orientation"]]] / r["total"])
        for r, s in zip(r_rows, r_set, strict=True)
        if s["role"] == "anchor"
    )
    early = float(np.mean([a for _, a in anchors[:2]]))
    late_level = float(np.mean([a for _, a in anchors[-2:]]))
    report["within_job_control"] = {
        "early_half_r": halves["early"],
        "late_half_r": halves["late"],
        "anchor_early": early,
        "anchor_late": late_level,
        "drift_within_job": bool(abs(early - late_level) > th["anchor_drift"]),
    }

    ba = cal["efficiency"]["B"] / cal["efficiency"]["A"]
    report["anchor_replay"] = {
        "ba": ba,
        "reading": "anchor error unchanged"
        if abs(ba - case.ORIGINAL_BA) <= th["anchor_replay_band"]
        else "anchor ratio moved",
    }

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
    report["fresh_anchors"] = {
        "ba": ratios,
        "median": float(np.median(ratios)),
        "sd": float(np.std(ratios, ddof=1)),
        "reading": fresh_anchor_reading(ratios, th) if all(math.isfinite(v) for v in ratios) else NOT_READ,
    }

    f_rows, f_set = subset(rows, settings, ("fresh-failing",))
    fresh = mirror(f_rows, f_set, None, "a")
    items = [tuple(i) for i in reg["failing_items"]]
    d_old = np.array([raw_old[i] for i in items])
    d_new = np.array([fresh[i] for i in items])
    aligned = float(np.mean(np.sign(d_old) * d_new))
    se = th["per_mesh_raw_sd"] / math.sqrt(len(items))
    fraction = aligned / th["original_failing_raw_mean"]
    half = 2.576 * se / th["original_failing_raw_mean"]
    if not math.isfinite(aligned):
        reading = NOT_READ
    elif aligned >= th["aligned_block"]:
        reading = "follows the design"
    elif aligned < th["aligned_mesh"]:
        reading = "follows the mesh"
    else:
        reading = "unresolved"
    report["fresh_failing"] = {
        "items": [f"{a}/{b}" for a, b in items],
        "original_raw_d": d_old.tolist(),
        "fresh_raw_d": d_new.tolist(),
        "aligned_mean": aligned,
        "carried_fraction": fraction,
        "carried_fraction_99": [fraction - half, fraction + half],
        "empirical_sd": float(np.std(np.sign(d_old) * d_new, ddof=1)),
        "reading": reading,
    }

    kinds = ("fresh-anchor", "fresh-failing", "fresh-dark")
    predicted = frozen_map_prediction(run, settings, kinds)
    report["frozen_maps"] = {
        model: map_score(rows, settings, predicted[model], rng_map, reg["permutations"], reg["map_alpha"])
        for model in ("gain", "offset")
    }

    table = {}
    for row, setting in zip(o_rows, o_set, strict=True):
        if setting["role"] in ("sign", "null"):
            lv = an.slot_levels(row, o_cal)
            for k, slot in enumerate(an.SLOTS):
                table[(setting["name"], slot)] = lv[slot]["l_hat"] - setting["ideal_levels"][k]
    before = mirror(r_rows, r_set, cal, "l_hat")
    found: dict[tuple[str, int], dict[int, float]] = {}
    for row, setting in zip(r_rows, r_set, strict=True):
        if setting["role"] not in ("sign", "null"):
            continue
        o = setting["orientation"]
        lv = an.slot_levels(row, cal)
        for item in (0, 1):
            slot = an.SLOTS[item if o == 0 else 1 - item]
            found.setdefault((setting["setting"], item), {})[o] = (
                lv[slot]["l_hat"] - table[(setting["original_name"], slot)]
            )
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
    parser.add_argument("--persistence-plan", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.mesh_gate:
        gate = mesh_gate(args.mesh_gate.resolve())
        print(json.dumps(gate, indent=1, sort_keys=True))
        return 0 if gate["passed"] else 1
    if args.persistence_plan:
        args.persistence_plan.write_text(json.dumps(persistence_plan(), indent=1, sort_keys=True) + "\n")
        print(args.persistence_plan)
        return 0
    if args.analyze is None or args.out is None:
        parser.error("--mesh-gate RUN, --persistence-plan OUT, or --analyze RUN with --out FILE")
    report = analyze(args.analyze.resolve())
    args.out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
