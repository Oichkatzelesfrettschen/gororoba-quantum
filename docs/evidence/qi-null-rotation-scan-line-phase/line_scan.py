"""Exploratory: the repository's shot-order line scan (primary and secondary band) on every job of the new series."""

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
for p in ("scripts", "gororoba_quantum", "docs/evidence/hardware-residuals/tuna-quandela"):
    sys.path.insert(0, str(ROOT / p))
from worker1 import scan_file

S = "2026-11-15T001929Z"
rows: list[dict[str, Any]] = []
for d in sorted((ROOT / "results/quantum_inspire/runs").glob(f"{S}-pathion_null_rotation_scan_*")):
    backend = 7 if "tuna_17" in d.name else 1
    for f in sorted((d / "raw").iterdir()):
        r = scan_file((d.name, f.name.removesuffix(".json"), backend))
        rows.append(r)
        s = r["secondary"]
        p = r["primary"]
        hz = (
            None
            if not (s.get("cycles_per_shot") and r["exec_seconds_per_shot"])
            else round(s["cycles_per_shot"] / r["exec_seconds_per_shot"], 2)
        )
        print(
            d.name.split("scan_")[1],
            f.name[:-8].ljust(16),
            "prim",
            p.get("detected"),
            "sec",
            s.get("detected"),
            "log10p",
            s.get("log10_p"),
            "cyc/shot",
            s.get("cycles_per_shot"),
            "Hz",
            hz,
            "s/shot",
            r["exec_seconds_per_shot"] and round(r["exec_seconds_per_shot"] * 1e3, 4),
            flush=True,
        )
(ROOT / "docs/evidence/qi-null-rotation-scan-line-phase/line_scan.json").write_text(
    json.dumps(rows, indent=1, default=str)
)
