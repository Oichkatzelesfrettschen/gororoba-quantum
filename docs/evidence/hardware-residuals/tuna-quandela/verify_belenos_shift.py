"""Independent check of the Belenos per-mode share shift on 2026-10-23: raw single-click counts per output mode of
two runs that return identical compiled circuits, summed over the 24 settings, and the per-mode share ratio."""

import common  # noqa: F401  (puts the repository's gororoba_quantum/ and scripts/ on sys.path for qd_records)
import numpy as np

import qd_records as qd

PAIRS = (
    ("2026-10-23T081314Z", "2026-10-23T195000Z"),
    ("2026-10-23T073329Z", "2026-10-23T202212Z"),
    ("2026-10-23T195000Z", "2026-10-23T201808Z"),
)
runs = {}
for directory in qd.run_directories():
    stamp = directory.name[:18]
    if "qpu_belenos" in directory.name and any(stamp in pair for pair in PAIRS):
        run = qd.read_run(directory)
        its = [i for i in run.collected["iterations"] if "counts" in i]
        counts = np.zeros((len(its), 24))
        for k, it in enumerate(its):
            for state, n in it["counts"].items():
                v = [int(x) for x in state.split(",")]
                if sum(v) == 1:
                    counts[k, v.index(1)] += n
        runs[stamp] = (
            directory.name,
            [i["result_fields"]["computed_circuit"] + i["result_fields"]["computed_input"] for i in its],
            counts,
        )
for a, b in PAIRS:
    na, ca, xa = runs[a]
    nb, cb, xb = runs[b]
    print(na, "->", nb, "identical circuits:", ca == cb, "settings", len(ca), "singles", int(xa.sum()), int(xb.sum()))
    sa, sb = xa.sum(0), xb.sum(0)
    keep = [m for m in range(24) if m not in (0, 1, 5)]
    pa, pb = sa[keep] / sa[keep].sum(), sb[keep] / sb[keep].sum()
    print("  mode: share ratio B/A (stray modes 0, 1, 5 excluded from the normalization)")
    print("  " + "  ".join(f"{m}:{pb[i] / pa[i]:.2f}" for i, m in enumerate(keep)))
    print("  mode 5 share of all singles:", round(sa[5] / sa.sum(), 4), "->", round(sb[5] / sb.sum(), 4))
    # per-setting sign consistency for modes 16..23: fraction of settings (with >= 20 counts in A) where the share fell
    fa = xa[:, keep] / xa[:, keep].sum(1, keepdims=True)
    fb = xb[:, keep] / xb[:, keep].sum(1, keepdims=True)
    idx = [keep.index(m) for m in range(16, 24)]
    ok = xa[:, keep][:, idx] >= 20
    print(
        "  modes 16-23: share fell in",
        int(((fb[:, idx] < fa[:, idx]) & ok).sum()),
        "of",
        int(ok.sum()),
        "setting-mode cells with at least 20 counts",
    )
