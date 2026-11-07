"""C1 post-hoc diagnostic: how much of the frozen-map result on the mesh-persistence job comes from the shifter map.

Each frozen model of c1_static.npz carries its own per-mode efficiencies (a_) and backgrounds (c_) beside its shifter
vector (x_). The preregistered frozen-map decision scored the full model on the fresh iterations' raw slot departures,
so its r mixes the efficiency fit with the shifter map. This script scores the efficiency-only model (x = 0) on the same
64 centered readings and the increment of each shifter map over it: r of (observed - efficiency-only) with (map -
efficiency-only), and the joint least-squares coefficients. It reports r values only (no new p, which would need a
fresh draw); the preregistered reading stays the recorded outcome. Falsifier of "the shifter map carries beyond the
efficiencies": an increment r near 0 while the efficiency-only r matches the full model's."""

import json
import sys
from pathlib import Path

import numpy as np
from c1_mesh import ROOT, cached, propagate
from perceval.serialization import deserialize

sys.path.insert(0, str(ROOT / "scripts"))
import ascella_pathion_mesh_persistence_analysis as reading  # noqa: E402

RUN = ROOT / "results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00"
FRESH = ("fresh-anchor", "fresh-failing", "fresh-dark")


def predictions(settings, entries, maps, kinds0, lo0):
    out = {model: {} for model in ("none", "gain", "offset")}
    for i, (setting, entry) in enumerate(zip(settings, entries, strict=True)):
        if setting["kind"] not in FRESH:
            continue
        theta, phi = [], []
        for _, comp in deserialize(entry["result_fields"]["computed_circuit"])._components:
            (theta if type(comp).__name__ == "BS" else phi).append(float(comp.get_parameters(all_params=True)[0]))
        th, ph = np.array(theta), np.array(phi)
        for model in out:
            a, c = maps[f"a_{model}_all"], maps[f"c_{model}_all"]
            if model == "none":
                dph = np.zeros((1, len(ph)))
            else:
                x = maps[f"x_{model}_all"]
                dph = (x * ph)[None, :] if model == "gain" else x[None, :]
            p = propagate(kinds0, lo0, th, ph, dph=dph)[0]
            w = np.exp(a) * p + 1e-4 * np.exp(c)
            q = w / w.sum()
            total = q[:9].sum()
            out[model][i] = [2 * q[list(m)].sum() / total for m in reading.case.pairs.SLOT_MODES.values()]
    return out


def centered(rows, settings, pred):
    obs, mod, kind = [], [], []
    for i, levels in pred.items():
        for k, slot in enumerate(reading.an.SLOTS):
            ideal = settings[i]["ideal_levels"][k]
            obs.append(2 * rows[i]["slot"][slot] / rows[i]["total"] - ideal)
            mod.append(levels[k] - ideal)
            kind.append(settings[i]["kind"])
    o, m, g = np.array(obs), np.array(mod), np.array(kind)
    for k in set(kind):
        o[g == k] -= o[g == k].mean()
        m[g == k] -= m[g == k].mean()
    return o, m


def main():
    _, settings, rows = reading.load(RUN)
    entries = json.loads((RUN / "results.json").read_bytes())["iterations"]
    maps = np.load(Path(__file__).resolve().parent / "c1_static.npz")
    kinds0, lo0, _, _, _ = cached(ROOT / reading.case.ORIGINAL_RUN, "pairs")
    pred = predictions(settings, entries, maps, kinds0, lo0)
    obs, none = centered(rows, settings, pred["none"])
    print(f"fresh readings {len(obs)}; efficiency-only model r {np.corrcoef(obs, none)[0, 1]:.3f}")
    for model in ("gain", "offset"):
        _, full = centered(rows, settings, pred[model])
        increment = np.corrcoef(obs - none, full - none)[0, 1]
        beta = np.linalg.lstsq(np.column_stack([none, full]), obs, rcond=None)[0]
        print(
            f"{model:6s} full model r {np.corrcoef(obs, full)[0, 1]:.3f}; increment over efficiencies r {increment:.3f}; "
            f"joint coefficients efficiency-only {beta[0]:.2f}, {model} {beta[1]:.2f}"
        )


if __name__ == "__main__":
    main()
