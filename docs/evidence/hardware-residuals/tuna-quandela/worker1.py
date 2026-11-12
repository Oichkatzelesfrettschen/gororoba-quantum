"""Worker of the shot-order line scan: one raw shot file, primary band and the wider secondary band."""

from __future__ import annotations

import json
from typing import Any

import qi_shot_record_line as line

SECONDARY_BAND = (0.010, 0.040)


def scan_file(item: tuple[str, str, int]) -> dict[str, Any]:
    run, name, backend = item
    primary = line.job_row((run, name, backend))
    path = line.RUNS / run / "raw" / f"{name}.json"
    x = line.bits(path).astype(float)
    wide = line.scan(x, band=SECONDARY_BAND, detection_p=line.DETECTION_P)
    results = (
        json.loads((line.RUNS / run / "results.json").read_text())
        if (line.RUNS / run / "results.json").exists()
        else None
    )
    seconds_per_shot = None
    if results:
        for row in results["jobs"]:
            if row["file"] == name:
                res = row.get("results") or []
                if res and res[0].get("execution_time_in_seconds") and res[0].get("shots_done"):
                    seconds_per_shot = res[0]["execution_time_in_seconds"] / res[0]["shots_done"]
    return {
        "run": run,
        "file": name,
        "backend": primary["backend"],
        "shots": primary["shots"],
        "primary": {k: v for k, v in primary.items() if k not in ("run", "file", "backend", "shots")},
        "secondary": {
            k: wide.get(k)
            for k in ("detected", "log10_p", "cycles_per_shot", "cycles_per_shot_se", "whitened_rank", "bits")
        },
        "exec_seconds_per_shot": seconds_per_shot,
    }


def scan_secondary(item: tuple[str, str, int]) -> dict[str, Any]:
    """The secondary band alone, for the earlier corpus."""
    run, name, backend = item
    path = line.RUNS / run / "raw" / f"{name}.json"
    wide = line.scan(line.bits(path).astype(float), band=SECONDARY_BAND, detection_p=line.DETECTION_P)
    return {
        "run": run,
        "file": name,
        "backend": line.BACKENDS[backend],
        "shots": wide["shots"],
        "detected": wide["detected"],
        "log10_p": wide.get("log10_p"),
        "cycles_per_shot": wide.get("cycles_per_shot"),
    }
