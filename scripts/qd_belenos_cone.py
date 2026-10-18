"""Light-cone reading of Q1's circuit on qpu:belenos: in-cone retention, off-cone background and acquisition time.

Every mode of the full mesh is topologically reachable from source s, so the
cone is defined by amplitude: every mode whose peak occupancy along the ideal
propagation (qd_belenos_mesh.peak_occupancy) exceeds CONE_FLOOR, joined with
every mode the exact dephasing channel at CONE_SIGMA heater and
CONE_SIGMA_THETA coupler noise detects at NOISY_FLOOR or more. Routing error
within that bound stays inside the cone, so in_block over in-cone samples
reads the mesh's retention and an off-cone click needs an error far larger
than any seeded cell shows, or a source other than the mesh's routing. The
ideal cone alone is kept beside it as in_block_ideal_cone, the statistic
case job-13 preregistered. The reading is a second
analysis of the retained runs; each run's preregistered verdict stays in its
own record.

Per cell (a single job, or one iteration of an iterated job) the record holds:

- in_block over every one-click sample and over in-cone samples, each with its
  Wilson 95 % interval, and the in-cone total variation from the served
  mesh's ideal propagation beside its multinomial shot floor;
- the off-cone one-click counts by mode, and the two-click samples that pair an
  off-cone click with an in-cone click beside the count that independent clicks
  gated to the source pulses would give, off-cone total x physical_perf /
  (1 - physical_perf);
- an acquisition-time estimate, samples / (physical_perf x clock): Perceval
  defines physical_perf as the share of trials that pass the detected-photon
  filter, and reading one trial per source pulse at the catalogue clock is a
  model no Quandela document confirms; the job's status.duration, shared
  among iterations by sample count, is the measured wall time;
- the receipt's dark expectation on off-cone modes under both time bases.

Groups of cells of one job with one mesh and one budget give each off-cone
mode's dispersion index (variance over mean of its counts); a stationary
rate reads 1.

--write OUT RUN... writes the record, --check OUT RUN... recomputes it and
requires equal bytes, --readout OUT RUN reads a single-job case against the
in-cone thresholds its manifest preregisters (case job-13) and
--check-readout OUT RUN replays that reading, and --self-test requires off-cone background to leave
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
# The exact dephasing channel at these heater and coupler noise levels drops Q1's in_block to about 0.5 on its
# served meshes, far beyond any seeded cell (0.98 to 0.995); a mode it detects at NOISY_FLOOR or more joins the
# cone, so routing error inside that bound never lands off the cone.
CONE_SIGMA, CONE_SIGMA_THETA, NOISY_FLOOR = 0.5, 0.1, 1e-3
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
    samples: int,
    arch: list[Any],
    phases: list[float],
    source: int,
    low: int,
    width: int,
    physical_perf: float,
    clock_mhz: float,
) -> dict[str, Any]:
    """The cone reading of one served mesh (its architecture and phases), its one-click histogram and its
    sample count over every outcome."""
    import numpy as np

    peak = mesh_lib.peak_occupancy(arch, phases, source)
    ideal_cone = [q for q in range(MODES) if peak[q] > CONE_FLOOR]
    noisy = mesh_lib.channel(arch, phases, source, sigma=CONE_SIGMA, sigma_theta=CONE_SIGMA_THETA)
    cone = sorted(set(ideal_cone) | {q for q in range(MODES) if noisy[q] >= NOISY_FLOOR})
    ideal = mesh_lib.propagate(arch, phases, source)[0]
    block = sum(single[low : low + width])
    total = sum(single)
    inside = sum(single[q] for q in cone)
    inside_ideal = sum(single[q] for q in ideal_cone)
    observed = np.zeros(MODES)
    for q in cone:
        observed[q] = single[q]
    distance = 0.5 * float(abs(observed / inside - ideal).sum()) if inside else None
    return {
        "cone_modes": cone,
        "ideal_cone_modes": ideal_cone,
        "samples": samples,
        "one_click_samples": total,
        "in_block": round(block / total, 6) if total else None,
        "in_block_wilson95": wilson(block, total),
        "in_cone_samples": inside,
        "in_block_cone": round(block / inside, 6) if inside else None,
        "in_block_cone_wilson95": wilson(block, inside),
        "in_block_ideal_cone": round(block / inside_ideal, 6) if inside_ideal else None,
        "in_block_ideal_cone_wilson95": wilson(block, inside_ideal),
        "tvd_cone_from_ideal": round(distance, 6) if distance is not None else None,
        "shot_floor": mesh_lib.shot_floor(ideal, inside) if inside else None,
        "off_cone_by_mode": {str(q): single[q] for q in range(MODES) if q not in cone and single[q]},
        "physical_perf": round(physical_perf, 9),
        "acquisition_s_estimate": round(samples / (physical_perf * clock_mhz * 1e6), 6) if physical_perf else None,
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
    job_samples = sum(sum(mesh_lib.bscount(e["results"]).values()) for e in inner.get("results_list") or [inner])
    if "results_list" in inner:
        entries = inner["results_list"]
        settings = manifest["settings"]
        seeds = [s.get("compilation_seed") for s in settings]
        names = [s["name"] for s in settings]
        budgets = [s.get("max_samples", manifest["max_samples"] // len(settings)) for s in settings]
        form = "iterated"
    else:
        entries = [inner]
        seeds = [manifest.get("compilation_seed")]
        names = [manifest["job"]]
        budgets = [manifest["max_samples"]]
        form = "single"
    out = []
    for name, seed, budget, entry in zip(names, seeds, budgets, entries, strict=True):
        counts = mesh_lib.bscount(entry["results"])
        samples = sum(counts.values())
        single = [0] * MODES
        pairs: list[tuple[tuple[int, ...], int]] = []
        for state, n in counts.items():
            if sum(state) == 1:
                single[state.index(1)] += n
            else:
                pairs.append((tuple(k for k, v in enumerate(state) if v), n))
        elements = mesh_lib.decode(entry["computed_circuit"])
        arch = mesh_lib.run_architecture(elements)
        row = cell(
            single,
            samples,
            arch,
            mesh_lib.mesh_phases(arch, elements),
            source_mode(entry["computed_input"]),
            low,
            width,
            float(entry["physical_perf"]),
            clock,
        )
        off = [q for q in range(MODES) if q not in row["cone_modes"]]
        acquisition = row["acquisition_s_estimate"] or 0.0
        wall = duration * samples / job_samples
        off_total = sum(row["off_cone_by_mode"].values())
        perf = row["physical_perf"]
        mixed = sum(n for clicks, n in pairs if any(q in off for q in clicks) and any(q not in off for q in clicks))
        out.append(
            {
                "run": run.name,
                "name": name,
                "form": form,
                "compilation_seed": seed,
                "max_samples": budget,
                "mesh_sha256": mesh_lib.mesh_sha(entry["computed_circuit"]),
                **row,
                "job_duration_s": duration,
                "wall_share_s": round(wall, 6),
                "receipt_dark_off_cone_wall": round(sum(rates[q] for q in off) * wall, 3),
                "receipt_dark_off_cone_acquisition": round(sum(rates[q] for q in off) * acquisition, 3),
                "off_cone_total": off_total,
                "off_cone_with_in_cone_click": mixed,
                "independent_gated_expectation": round(off_total * perf / (1 - perf), 3),
            }
        )
    return out


def dispersion(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Variance over mean of each off-cone mode's counts in every group of two or more cells of one job that share
    a served mesh and a sample budget, so drift between jobs stays out of the index."""
    groups: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for c in cells:
        groups.setdefault((c["run"], c["mesh_sha256"], c["max_samples"]), []).append(c)
    rows = []
    for (_, mesh, _), members in sorted(groups.items()):
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


READOUT_SCHEMA = "qd-belenos-seeded-single-readout-v1"


def reading(rule: dict[str, Any], row: dict[str, Any]) -> str:
    """The preregistered reading of one cell: void off the named mesh, else by in_block over the ideal cone, the
    cone the case was preregistered on."""
    if not row["mesh_sha256"].startswith(rule["void_unless_mesh_sha256_prefix"]):
        return "void"
    if row["in_block_ideal_cone"] >= rule["unseeded_path_at_least"]:
        return "unseeded path"
    if row["in_block_ideal_cone"] <= rule["single_job_budget_at_most"]:
        return "single-job form at Q1's budget"
    return "intermediate"


def readout(run: Path) -> dict[str, Any]:
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    rule = manifest["preregistered"]
    (row,) = run_cells(run)
    return {
        "schema": READOUT_SCHEMA,
        "run": run.name,
        "cases_sha256": mesh_lib.sha256(run / "cases.json"),
        "rule": rule,
        "cell": row,
        "verdict": reading(rule, row),
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
    clean = [int(round(10000 * float(p))) for p in ideal]
    low = 20
    base = cell(clean, sum(clean), arch, phases, 20, low, 4, 0.01, 4.94)
    cone = base["cone_modes"]
    outside = [q for q in range(MODES) if q not in cone]
    if not outside:
        raise SystemExit("cone self-test: the synthetic mesh's bounded cone covers every mode")
    noisy = list(clean)
    noisy[outside[0]] += 900
    with_noise = cell(noisy, sum(noisy), arch, phases, 20, low, 4, 0.01, 4.94)
    if with_noise["in_block_cone"] != base["in_block_cone"] or with_noise["in_block"] >= base["in_block"]:
        raise SystemExit(f"cone self-test: off-cone background moved the cone reading {base} -> {with_noise}")
    lossy = list(clean)
    inside_off_block = [q for q in cone if not low <= q < low + 4]
    lossy[inside_off_block[0]] += 900
    if cell(lossy, sum(lossy), arch, phases, 20, low, 4, 0.01, 4.94)["in_block_cone"] >= base["in_block_cone"]:
        raise SystemExit("cone self-test: in-cone loss left the cone reading unchanged")
    rule = {"void_unless_mesh_sha256_prefix": "q1", "unseeded_path_at_least": 0.95, "single_job_budget_at_most": 0.65}
    for mesh, value, want in (
        ("q1x", 0.97, "unseeded path"),
        ("q1x", 0.39, "single-job form at Q1's budget"),
        ("q1x", 0.8, "intermediate"),
        ("f", 0.39, "void"),
    ):
        if reading(rule, {"mesh_sha256": mesh, "in_block_ideal_cone": value}) != want:
            raise SystemExit(f"cone self-test: {mesh} at {value} did not read {want}")
    poisson = np.random.default_rng(7).poisson(50, 400).tolist()
    fake = [
        {"mesh_sha256": "m", "max_samples": 1500, "run": "r", "name": f"i{k}", "off_cone_by_mode": {"5": v}}
        for k, v in enumerate(poisson)
    ]
    (row,) = dispersion(fake)
    if not 0.8 <= row["dispersion_index"] <= 1.2:
        raise SystemExit(f"cone self-test: a Poisson background read dispersion {row['dispersion_index']}")
    print("cone self-test: off-cone clicks excluded, in-cone loss read, four readings, Poisson dispersion near 1")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--check", type=Path, nargs="+", metavar=("OUT", "RUN"))
    group.add_argument("--readout", type=Path, nargs=2, metavar=("OUT", "RUN"))
    group.add_argument("--check-readout", type=Path, nargs=2, metavar=("OUT", "RUN"))
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.readout or args.check_readout:
        out, run = args.readout or args.check_readout
        text = dump(readout(run))
        if args.readout:
            out.write_text(text, encoding="utf-8")
        elif out.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{out}: the readout differs from its retained run")
        print(f"{out}: {'written' if args.readout else 'replays'}, {json.loads(text)['verdict']}")
        return 0
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
