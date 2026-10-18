"""Light-cone reading of Q1's circuit on qpu:belenos: in-cone retention, off-cone background and acquisition time.

A photon entering source s reaches only the modes its served mesh couples to
s: the cone is every mode whose peak occupancy along the propagation
(qd_belenos_mesh.peak_occupancy) exceeds CONE_FLOOR. A one-click sample on a
mode outside the cone carries no light of this circuit, so it is detector
background by construction, and in_block over in-cone samples reads the
mesh's retention without any background model. The reading is a second
analysis of the retained runs; each run's preregistered verdict stays in its
own record.

Per cell (a single job, or one iteration of an iterated job) the record holds:

- in_block over every one-click sample and over in-cone samples, each with its
  Wilson 95 % interval, and the in-cone total variation from the served
  mesh's ideal propagation beside its multinomial shot floor;
- the off-cone one-click counts by mode;
- the acquisition time samples / (physical_perf x clock): physical_perf is
  the share of source pulses that pass the one-photon filter, so this is the
  time the detectors were read, while status.duration is the job's wall time;
- the receipt's dark expectation on off-cone modes under both time bases.

Groups of cells with one mesh and one budget give each background mode's
dispersion index (variance over mean of its counts); a stationary dark rate
reads 1.

--write OUT RUN... writes the record, --check OUT RUN... recomputes it and
requires equal bytes, and --self-test requires off-cone background to leave
the in-cone reading unchanged, in-cone loss to lower it, and a stationary
background to read a dispersion index near 1.

Usage: "$PYTHON" scripts/qd_belenos_cone.py (--write OUT RUN... | --check OUT RUN... | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qd_belenos_mesh as mesh_lib  # noqa: E402
from qd_box_kite_analysis import wilson  # noqa: E402

SCHEMA = "qd-belenos-cone-reading-v1"
CONE_FLOOR = 1e-6
MODES = mesh_lib.MODES


def one_click(counts: dict[str, int]) -> list[int]:
    single = [0] * MODES
    for state, n in counts.items():
        clicks = [k for k, v in enumerate(state.split(",")) if int(v)]
        if len(clicks) == 1:
            single[clicks[0]] += n
    return single


def source_mode(computed_input: str) -> int:
    occupation = computed_input.rsplit("|", 1)[1].rstrip(">").split(",")
    (source,) = [k for k, v in enumerate(occupation) if int(v)]
    return source


def cell(
    single: list[int],
    arch: list[Any],
    phases: list[float],
    source: int,
    low: int,
    width: int,
    physical_perf: float,
    clock_mhz: float,
) -> dict[str, Any]:
    """The cone reading of one served mesh (its architecture and phases) and its one-click histogram."""
    import numpy as np

    peak = mesh_lib.peak_occupancy(arch, phases, source)
    cone = [q for q in range(MODES) if peak[q] > CONE_FLOOR]
    ideal = mesh_lib.propagate(arch, phases, source)[0]
    block = sum(single[low : low + width])
    total = sum(single)
    inside = sum(single[q] for q in cone)
    observed = np.zeros(MODES)
    for q in cone:
        observed[q] = single[q]
    distance = 0.5 * float(abs(observed / inside - ideal).sum()) if inside else None
    return {
        "cone_modes": cone,
        "one_click_samples": total,
        "in_block": round(block / total, 6) if total else None,
        "in_block_wilson95": wilson(block, total),
        "in_cone_samples": inside,
        "in_block_cone": round(block / inside, 6) if inside else None,
        "in_block_cone_wilson95": wilson(block, inside),
        "tvd_cone_from_ideal": round(distance, 6) if distance is not None else None,
        "shot_floor": mesh_lib.shot_floor(ideal, inside) if inside else None,
        "off_cone_by_mode": {str(q): single[q] for q in range(MODES) if q not in cone and single[q]},
        "physical_perf": round(physical_perf, 9),
        "acquisition_s": round(total / (physical_perf * clock_mhz * 1e6), 6) if physical_perf else None,
    }


def run_cells(run: Path) -> list[dict[str, Any]]:
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    (block,) = manifest["blocks"]
    low, width = block["offset"], len(block["roles"])
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    perfs = submission["perfs_at_plan"]
    clock = float(perfs["Clock (MHz)"])
    rates = [float(r) for r in perfs["Dark counts (detection/s)"]]
    outer = json.loads((run / "raw/result.json").read_text(encoding="utf-8"))
    inner = mesh_lib.raw_result(run)
    duration = float(outer["duration"])
    if "results_list" in inner:
        entries = inner["results_list"]
        settings = manifest["settings"]
        seeds = [s.get("compilation_seed") for s in settings]
        names = [s["name"] for s in settings]
        form = "iterated"
    else:
        entries = [inner]
        seeds = [manifest.get("compilation_seed")]
        names = [manifest["job"]]
        form = "single"
    out = []
    for name, seed, entry in zip(names, seeds, entries, strict=True):
        counts = mesh_lib.bscount(entry["results"])
        single = [0] * MODES
        for state, n in counts.items():
            if sum(state) == 1:
                single[state.index(1)] += n
        elements = mesh_lib.decode(entry["computed_circuit"])
        arch = mesh_lib.run_architecture(elements)
        row = cell(
            single,
            arch,
            mesh_lib.mesh_phases(arch, elements),
            source_mode(entry["computed_input"]),
            low,
            width,
            float(entry["physical_perf"]),
            clock,
        )
        off = [q for q in range(MODES) if q not in row["cone_modes"]]
        acquisition = row["acquisition_s"] or 0.0
        out.append(
            {
                "run": run.name,
                "name": name,
                "form": form,
                "compilation_seed": seed,
                "mesh_sha256": mesh_lib.mesh_sha(entry["computed_circuit"]),
                **row,
                "job_duration_s": duration,
                "receipt_dark_off_cone_wall": round(sum(rates[q] for q in off) * duration, 3),
                "receipt_dark_off_cone_acquisition": round(sum(rates[q] for q in off) * acquisition, 3),
                "off_cone_total": sum(row["off_cone_by_mode"].values()),
            }
        )
    return out


def dispersion(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Variance over mean of each background mode's counts in every group of two or more cells sharing a mesh
    and a budget."""
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for c in cells:
        groups.setdefault((c["mesh_sha256"], c["one_click_samples"] // 100), []).append(c)
    rows = []
    for (mesh, _), members in sorted(groups.items()):
        if len(members) < 2:
            continue
        modes = sorted({int(q) for c in members for q in c["off_cone_by_mode"]})
        for q in modes:
            values = [c["off_cone_by_mode"].get(str(q), 0) for c in members]
            mean = statistics.fmean(values)
            rows.append(
                {
                    "mesh_sha256": mesh,
                    "cells": [f"{c['run'][-6:]}:{c['name']}" for c in members],
                    "mode": q,
                    "counts": values,
                    "dispersion_index": round(statistics.variance(values) / mean, 3) if mean else None,
                }
            )
    return rows


def record(runs: list[Path]) -> dict[str, Any]:
    cells = [c for run in runs for c in run_cells(run)]
    return {
        "schema": SCHEMA,
        "cone_floor": CONE_FLOOR,
        "runs": [run.name for run in runs],
        "cells": cells,
        "background_dispersion": dispersion(cells),
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def self_test() -> int:
    """Background off the cone leaves in_block_cone unchanged; light lost inside the cone lowers it."""
    import random

    catalogue = mesh_lib.load_catalogue()
    arch = mesh_lib.architecture(catalogue)
    # Bar on every MZI but random phases on modes 16 to 23 confines source 20's light to modes 13 to 23.
    rng = random.Random(20261018)
    bar = mesh_lib.baseline(arch, None)
    modes = [arch[j][1] for j in mesh_lib.phase_slots(arch)]
    phases = [rng.uniform(0, 2 * math.pi) if m >= 16 else b for m, b in zip(modes, bar, strict=True)]
    import numpy as np

    ideal = mesh_lib.propagate(arch, phases, 20)[0]
    peak = mesh_lib.peak_occupancy(arch, phases, 20)
    cone = [q for q in range(MODES) if peak[q] > CONE_FLOOR]
    outside = [q for q in range(MODES) if q not in cone]
    clean = [int(round(10000 * float(p))) for p in ideal]
    low = 20
    base = cell(clean, arch, phases, 20, low, 4, 0.01, 4.94)
    noisy = list(clean)
    noisy[outside[0]] += 900
    with_noise = cell(noisy, arch, phases, 20, low, 4, 0.01, 4.94)
    if with_noise["in_block_cone"] != base["in_block_cone"] or with_noise["in_block"] >= base["in_block"]:
        raise SystemExit(f"cone self-test: off-cone background moved the cone reading {base} -> {with_noise}")
    lossy = list(clean)
    inside_off_block = [q for q in cone if not low <= q < low + 4]
    lossy[inside_off_block[0]] += 900
    if cell(lossy, arch, phases, 20, low, 4, 0.01, 4.94)["in_block_cone"] >= base["in_block_cone"]:
        raise SystemExit("cone self-test: in-cone loss left the cone reading unchanged")
    poisson = np.random.default_rng(7).poisson(50, 400).tolist()
    fake = [
        {"mesh_sha256": "m", "one_click_samples": 1500, "run": "r", "name": f"i{k}", "off_cone_by_mode": {"5": v}}
        for k, v in enumerate(poisson)
    ]
    (row,) = dispersion(fake)
    if not 0.8 <= row["dispersion_index"] <= 1.2:
        raise SystemExit(f"cone self-test: a Poisson background read dispersion {row['dispersion_index']}")
    print("cone self-test: off-cone background excluded, in-cone loss read, Poisson dispersion near 1")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--check", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    out, *runs = args.write or args.check
    text = dump(record(runs))
    if args.write:
        out.write_text(text, encoding="utf-8")
        print(f"{out}: {len(json.loads(text)['cells'])} cells written")
        return 0
    if out.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{out}: the cone reading differs from its retained runs")
    print(f"{out}: cone reading replays")
    return 0


if __name__ == "__main__":
    sys.exit(main())
