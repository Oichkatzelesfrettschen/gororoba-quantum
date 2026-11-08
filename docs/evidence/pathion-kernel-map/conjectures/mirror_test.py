"""Do per-mode efficiencies explain the mirror failures of the Ascella two-block job? In-sample and held-out."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PAIRS = ROOT / "results/quandela/runs/2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import ascella_pathion_coset_block_pairs_analysis as an
import numpy as np

from parallel import ordered_map


def main():
    run = Path(sys.argv[1]) if len(sys.argv) > 1 else PAIRS
    manifest = json.loads((run / "cases.json").read_bytes())
    results = json.loads((run / "results.json").read_bytes())
    settings = manifest["settings"]
    reg = manifest["preregistered"]
    modes = {"slots": reg["slot_modes"], "failure": reg["failure_mode"], "sentinel": reg["sentinel_modes"]}
    structure = an.layout(manifest)
    samples, cap = manifest["max_samples"] // manifest["iterations"], manifest["max_shots"] // manifest["iterations"]
    tasks = [
        (i, s, e, samples, cap, modes) for i, (s, e) in enumerate(zip(settings, results["iterations"], strict=True))
    ]
    rows = ordered_map(an.observation, tasks, min_items=1)
    tol = reg["thresholds"]["level_tolerance"]

    def mirrors(rws):
        cal = an.calibrate(rws, settings)
        rd = an.readings_of(manifest, structure, rws, cal, tol)
        return {(r["setting"], r["item"]): r for r in rd if r["complete"]}

    obs = mirrors(rows)
    # in-sample efficiencies
    eta_all = an.mode_efficiency_fit(rows, settings)
    mod_all = mirrors(an.model_rows(rows, settings, eta_all, modes))
    # held-out: fit on iterations of orientation 0 only (plus anchors/darks), predict everything
    o0 = set()
    for by in structure["by_setting"].values():
        o0.update(by[0])
    rows_o0 = [
        r if (i in o0 or settings[i]["role"] in ("anchor", "dark")) else {**r, "returned": False}
        for i, r in enumerate(rows)
    ]
    eta_o0 = an.mode_efficiency_fit(rows_o0, settings)
    mod_o0 = mirrors(an.model_rows(rows, settings, eta_o0, modes))
    keys = sorted(obs)

    def signed(m, k):
        v = list(m[k]["orientations"].values())
        return v[0]["l_hat"] - v[1]["l_hat"]

    o = np.array([signed(obs, k) for k in keys])
    a = np.array([signed(mod_all, k) for k in keys])
    h = np.array([signed(mod_o0, k) for k in keys])
    fail = np.abs(o) > reg["thresholds"]["mirror_spread"]
    print(f"mirror pairs {len(keys)}, failing {int(fail.sum())}")
    print(f"observed |diff|: median {np.median(np.abs(o)):.4f}, max {np.abs(o).max():.4f}")
    for lab, m in (("in-sample eta", a), ("held-out eta (orientation 0)", h)):
        r = np.corrcoef(o, m)[0, 1]
        resid = o - m
        flagged = np.abs(m) > reg["thresholds"]["mirror_spread"]
        print(
            f"{lab}: model |diff| median {np.median(np.abs(m)):.4f} max {np.abs(m).max():.4f}; corr(obs, model) {r:+.3f}; "
            f"residual rms {np.sqrt(np.mean(resid**2)):.4f} vs observed rms {np.sqrt(np.mean(o**2)):.4f}; "
            f"model flags {int(flagged.sum())}, of the {int(fail.sum())} failing it flags {int((flagged & fail).sum())}"
        )
    print("failing pairs (setting, item, observed, in-sample model):")
    for k, ov, av, f in zip(keys, o, a, fail, strict=True):
        if f:
            print(f"  {k} {ov:+.4f} {av:+.4f}")
    print("eta all", [round(x, 3) for x in eta_all])
    print("eta o0 ", [round(x, 3) for x in eta_o0])


if __name__ == "__main__":
    main()
