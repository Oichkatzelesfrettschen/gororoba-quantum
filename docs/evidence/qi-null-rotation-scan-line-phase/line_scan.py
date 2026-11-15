"""Exploratory: the repository's shot-order line scan (primary and secondary band) on every job of the new series."""

# ruff: noqa: E402  (the scan worker is imported after the path insertion that locates it)
import json
import sys

from scan_forward import HERE, ROOT

import parallel

sys.path.insert(0, str(ROOT / "docs/evidence/hardware-residuals/tuna-quandela"))
from worker1 import scan_file

S = "2026-11-15T001929Z"


def main() -> None:
    items = [
        (d.name, f.name.removesuffix(".json"), 7 if "tuna_17" in d.name else 1)
        for d in sorted((ROOT / "results/quantum_inspire/runs").glob(f"{S}-pathion_null_rotation_scan_*"))
        for f in sorted((d / "raw").iterdir())
    ]
    rows = parallel.ordered_map(scan_file, items, min_items=2)
    for (run, name, _backend), r in zip(items, rows, strict=True):
        s, p = r["secondary"], r["primary"]
        hz = (
            None
            if not (s.get("cycles_per_shot") and r["exec_seconds_per_shot"])
            else round(s["cycles_per_shot"] / r["exec_seconds_per_shot"], 2)
        )
        print(run.split("scan_")[1], name[:-3].ljust(16), "prim", p.get("detected"), "sec", s.get("detected"), "Hz", hz)
    (HERE / "line_scan.json").write_text(json.dumps(rows, indent=1, default=str))


if __name__ == "__main__":
    main()
