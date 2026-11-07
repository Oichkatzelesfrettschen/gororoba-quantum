"""Prospective score of a per-seed correction table, frozen from job-02 and job-03, on a fresh repeat of their meshes.

docs/state/plans/ascella-prospective-correction-case.json fixes the estimator, the score and the decision before the
acquisition, and docs/design/ascella-signed-coherence-conformance.md#prospective-correction-case-job-09 states them.
The estimator is the one docs/evidence/ascella-order-coefficients/long-horizon-controls.json applied retrospectively
to job-08, keyed by setting name so a repeat in another order reads it unchanged:

- Table (--freeze): over job-02's 56 perturbed (off-stride) settings, c2 and c3 are job-02's and job-03's
  block-conditioned X statistic z (ascella_compilation_reading.x_statistics) centered on their perturbed mean,
  the slope is c2.c3 / c2.c2, and each setting's offset is slope x (c2 + c3) / 2. The record carries the offsets by
  name, the digests of both runs' results.json, the counting variances and the table's own noise variance
  slope^2 (v2 + v3) / 4, and the decision rule below.
- Score (--score): the repeat's settings whose served unitary lies within ascella_long_horizon_reading.MESH_TOLERANCE
  of job-02's under the same name are read, perturbed ones only; with fewer than MIN_MESHES nothing is read. d is
  the repeat's z centered on those meshes and t the table's offsets centered on the same meshes. The statistic is
  the variance ratio R = var(d) / var(d - t). BOOTSTRAP resamples of the meshes with replacement give its two-sided
  1 - 2 ALPHA percentile interval; the reading is "correction holds" when the lower end reaches USEFUL_RATIO (the
  frozen table removes at least half the per-mesh variance), "correction fails" when the upper end stays below it,
  and "indeterminate" otherwise. Beside it: the Pearson r of d and t, the repeat's counting variance, and the ratio
  a correction limited only by counting and table noise would reach, var(d) / (counting + table noise).
- Mesh gate (--mesh-gate): exits nonzero unless every one of the run's served unitaries lies within MESH_TOLERANCE
  of job-02's under the same name; the sim:ascella rehearsal of the repeat passes it before the QPU request is sent,
  since a redrawn compilation would score other meshes than the table's. It reads no draw value.
- Power (--power): POWER_REPLICATES Gaussian replicates per scenario of the frozen table's meshes. The true error
  is S = t - n with n of the table's noise variance; a persistent scenario scales it, d = a S + c, and a redrawn
  scenario keeps the variance of S, d = rho S + f + c with f of variance (1 - rho^2) var(S); c is counting noise at
  the repeat's samples, scaled from job-02's (heater-coupling.json). Each replicate is read with POWER_BOOTSTRAP
  resamples.

The ANU QRNG draw PROSPECTIVE_ORDER_DRAW of ascella_coherence_request.py orders the repeat with values 0..55; value
BOOTSTRAP_INDEX seeds the score's resamples and value POWER_INDEX the power record, whose replicates take generators
spawned before the map.

Usage:
  "$PYTHON" scripts/ascella_correction_score.py --freeze JOB_02 JOB_03 OUT [--check]
  "$PYTHON" scripts/ascella_correction_score.py --power TABLE OUT [--check]
  "$PYTHON" scripts/ascella_correction_score.py --score TABLE JOB_02 REPEAT OUT [--check]
  "$PYTHON" scripts/ascella_correction_score.py --mesh-gate JOB_02 RUN
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_long_horizon_reading as long_horizon  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_seed_repeat_reading as seed_repeat  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLAN = "docs/state/plans/ascella-prospective-correction-case.json"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T040400Z.json"
BOOTSTRAP_INDEX = 56
POWER_INDEX = 57
ALPHA = 0.01
USEFUL_RATIO = 2.0
BOOTSTRAP = 20000
MIN_MESHES = 16
POWER_REPLICATES = 400
POWER_BOOTSTRAP = 2000
POWER_SAMPLES = 32768
# (family, parameter): "persistent" scales the true error by a, "redrawn" correlates it with the true error at rho.
POWER_SCENARIOS = (
    ("persistent", 1.0),
    ("persistent", 0.88),
    ("persistent", 0.75),
    ("redrawn", 0.9),
    ("redrawn", 0.75),
    ("redrawn", 0.5),
    ("redrawn", 0.0),
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_value(index: int) -> int:
    return int(json.loads((ROOT / DRAW).read_text(encoding="utf-8"))["values"][index])


def results_sha256(directory: Path) -> str:
    return sha256_file(directory / "results.json")


def perturbed_statistics(directory: Path) -> tuple[str, dict[str, float], dict[str, float], int]:
    """The run's job name, z and multinomial variance by perturbed setting name, and its samples per iteration."""
    data = models.job_data(directory)
    names = seed_repeat.names(data)
    anchors = reading.anchors_of(data)
    z, v = reading.x_statistics(data)
    keep = [i for i in range(len(names)) if not anchors[i]]
    return (
        str(data["record"]["manifest"]["job"]),
        {names[i]: float(z[i]) for i in keep},
        {names[i]: float(v[i]) for i in keep},
        long_horizon.samples_of(data),
    )


def freeze(job_02: Path, job_03: Path) -> dict[str, Any]:
    name_2, z_2, v_2, _ = perturbed_statistics(job_02)
    name_3, z_3, v_3, _ = perturbed_statistics(job_03)
    models.require((name_2, name_3) == ("job-02", "job-03"), f"the table reads job-02 and job-03, not {name_2, name_3}")
    models.require(sorted(z_2) == sorted(z_3), "job-03 does not hold job-02's perturbed settings")
    names = sorted(z_2)
    c_2 = np.array([z_2[n] for n in names]) - np.mean([z_2[n] for n in names])
    c_3 = np.array([z_3[n] for n in names]) - np.mean([z_3[n] for n in names])
    slope = float(c_2 @ c_3 / (c_2 @ c_2))
    offsets = slope * 0.5 * (c_2 + c_3)
    counting = [float(np.mean([v_2[n] for n in names])), float(np.mean([v_3[n] for n in names]))]
    return {
        "schema": "ascella-correction-table-v1",
        "plan": PLAN,
        "runs": [job_02.relative_to(ROOT).as_posix(), job_03.relative_to(ROOT).as_posix()],
        "results_sha256": [results_sha256(job_02), results_sha256(job_03)],
        "estimator": "offset = slope x (c2 + c3) / 2 with c the perturbed-centered X statistic and slope c2.c3 / c2.c2",
        "meshes": len(names),
        "slope": slope,
        "counting_variance": counting,
        "table_noise_variance": slope * slope * 0.25 * sum(counting),
        "offsets": {name: float(value) for name, value in zip(names, offsets, strict=True)},
        "decision": {
            "statistic": "R = var(d) / var(d - t) over the repeat's perturbed meshes identical to job-02's",
            "alpha": ALPHA,
            "useful_ratio": USEFUL_RATIO,
            "bootstrap": BOOTSTRAP,
            "min_meshes": MIN_MESHES,
            "seed_draw": DRAW,
            "seed_index": BOOTSTRAP_INDEX,
        },
    }


def ratios(d: np.ndarray, t: np.ndarray, generator: np.random.Generator, resamples: int) -> np.ndarray:
    """The variance ratio of `resamples` bootstrap resamples of the meshes."""
    picks = generator.integers(0, len(d), size=(resamples, len(d)))
    before = d[picks].var(axis=1, ddof=1)
    after = (d - t)[picks].var(axis=1, ddof=1)
    out: np.ndarray = before / after
    return out


def ratio_reading(d: np.ndarray, t: np.ndarray, generator: np.random.Generator, resamples: int) -> dict[str, Any]:
    """R, its bootstrap interval and the reading against USEFUL_RATIO (module docstring)."""
    observed = float(d.var(ddof=1) / (d - t).var(ddof=1))
    sampled = ratios(d, t, generator, resamples)
    lower, upper = (float(q) for q in np.quantile(sampled, [ALPHA, 1.0 - ALPHA]))
    if lower >= USEFUL_RATIO:
        verdict = "correction holds"
    elif upper < USEFUL_RATIO:
        verdict = "correction fails"
    else:
        verdict = "indeterminate"
    return {"ratio": observed, "lower": lower, "upper": upper, "reading": verdict}


def table_of(path: Path) -> dict[str, Any]:
    table: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    models.require(table.get("schema") == "ascella-correction-table-v1", f"{path} is not a correction table")
    return table


def distances_to_job_02(reference: dict[str, Any], repeat: dict[str, Any]) -> tuple[list[str], list[float]]:
    """The repeat's setting names and each served unitary's largest entry distance from job-02's of the same name."""
    names_ref, names_new = seed_repeat.names(reference), seed_repeat.names(repeat)
    models.require(sorted(names_ref) == sorted(names_new), "the repeat does not hold job-02's settings")
    index_ref = {name: i for i, name in enumerate(names_ref)}
    served_ref, served_new = seed_repeat.served(reference), seed_repeat.served(repeat)
    distances = ordered_map(
        long_horizon.mesh_distance, [(served_new[i], served_ref[index_ref[name]]) for i, name in enumerate(names_new)]
    )
    return names_new, [float(d) for d in distances]


def served_record(directory: Path) -> dict[str, Any]:
    """The run's manifest and collected results in job_data's record layout; a simulator run carries no dark-count
    figure, so the gate reads only the files that name and serve each setting."""
    return {
        "record": {
            "manifest": json.loads((directory / "cases.json").read_text(encoding="utf-8")),
            "results": json.loads((directory / "results.json").read_text(encoding="utf-8")),
        }
    }


def mesh_gate(job_02: Path, run: Path) -> str:
    """Refuse a run, the sim:ascella rehearsal of the repeat, whose served meshes left job-02's."""
    names, distances = distances_to_job_02(served_record(job_02), served_record(run))
    moved = [name for name, distance in zip(names, distances, strict=True) if distance > long_horizon.MESH_TOLERANCE]
    models.require(not moved, f"{len(moved)} of {len(names)} served meshes left job-02's: {moved[:4]}")
    return (
        f"all {len(names)} served meshes within {long_horizon.MESH_TOLERANCE} of job-02's, largest {max(distances):.2e}"
    )


def score(table_path: Path, job_02: Path, repeat_dir: Path) -> dict[str, Any]:
    table = table_of(table_path)
    models.require(
        job_02.relative_to(ROOT).as_posix() == table["runs"][0]
        and results_sha256(job_02) == table["results_sha256"][0],
        "the mesh reference is not the table's job-02 run",
    )
    repeat = models.job_data(repeat_dir)
    names_new, distances = distances_to_job_02(models.job_data(job_02), repeat)
    anchors = reading.anchors_of(repeat)
    z, v = reading.x_statistics(repeat)
    offsets = table["offsets"]
    kept = [
        i
        for i, name in enumerate(names_new)
        if not anchors[i] and name in offsets and distances[i] <= long_horizon.MESH_TOLERANCE
    ]
    record: dict[str, Any] = {
        "schema": "ascella-correction-score-v1",
        "plan": PLAN,
        "table": table_path.relative_to(ROOT).as_posix(),
        "table_sha256": sha256_file(table_path),
        "runs": [job_02.relative_to(ROOT).as_posix(), repeat_dir.relative_to(ROOT).as_posix()],
        "job": str(repeat["record"]["manifest"]["job"]),
        "samples": long_horizon.samples_of(repeat),
        "mesh_identity": {
            "tolerance": long_horizon.MESH_TOLERANCE,
            "perturbed": int((~anchors).sum()),
            "perturbed_identical": len(kept),
            "anchors_identical": int(
                sum(1 for i in range(len(names_new)) if anchors[i] and distances[i] <= long_horizon.MESH_TOLERANCE)
            ),
            "anchors": int(anchors.sum()),
        },
        "decision": table["decision"],
    }
    if len(kept) < MIN_MESHES:
        record["reading"] = f"not read: fewer than {MIN_MESHES} perturbed meshes match job-02's"
        return record
    d = z[kept] - z[kept].mean()
    t = np.array([offsets[names_new[i]] for i in kept])
    t = t - t.mean()
    generator = np.random.default_rng(draw_value(BOOTSTRAP_INDEX))
    result = ratio_reading(d, t, generator, BOOTSTRAP)
    counting = float(v[kept].mean())
    record["score"] = {
        **result,
        "meshes": len(kept),
        "sd_before": float(d.std(ddof=1)),
        "sd_after": float((d - t).std(ddof=1)),
        "r": float(np.corrcoef(d, t)[0, 1]),
        "counting_variance": counting,
        "noise_limited_ratio": float(d.var(ddof=1) / (counting + table["table_noise_variance"])),
    }
    record["reading"] = result["reading"]
    return record


def power_replicate(item: tuple[str, float, np.ndarray, float, float, np.random.SeedSequence]) -> str:
    """The reading of one Gaussian replicate of a scenario (module docstring, --power)."""
    family, parameter, offsets, noise, counting, seed = item
    generator = np.random.default_rng(seed)
    true = offsets - generator.normal(0.0, math.sqrt(noise), len(offsets))
    counts = generator.normal(0.0, math.sqrt(counting), len(offsets))
    if family == "persistent":
        repeat = parameter * true + counts
    else:
        fresh = generator.normal(0.0, math.sqrt(max(float(true.var(ddof=1)), 0.0) * (1.0 - parameter**2)), len(offsets))
        repeat = parameter * true + fresh + counts
    d = repeat - repeat.mean()
    return str(ratio_reading(d, offsets - offsets.mean(), generator, POWER_BOOTSTRAP)["reading"])


def power(table_path: Path) -> dict[str, Any]:
    table = table_of(table_path)
    offsets = np.array([table["offsets"][name] for name in sorted(table["offsets"])])
    _, counting_8192 = long_horizon.spread()
    counting = counting_8192 * long_horizon.SPREAD_SAMPLES / POWER_SAMPLES
    children = np.random.SeedSequence(draw_value(POWER_INDEX)).spawn(len(POWER_SCENARIOS) * POWER_REPLICATES)
    items = [
        (family, parameter, offsets, float(table["table_noise_variance"]), counting, children[k * POWER_REPLICATES + j])
        for k, (family, parameter) in enumerate(POWER_SCENARIOS)
        for j in range(POWER_REPLICATES)
    ]
    readings = ordered_map(power_replicate, items)
    rows = []
    for k, (family, parameter) in enumerate(POWER_SCENARIOS):
        chunk = readings[k * POWER_REPLICATES : (k + 1) * POWER_REPLICATES]
        rows.append(
            {
                "family": family,
                "parameter": parameter,
                "shares": {name: chunk.count(name) / POWER_REPLICATES for name in sorted(set(chunk))},
            }
        )
    return {
        "schema": "ascella-correction-power-v1",
        "plan": PLAN,
        "table": table_path.relative_to(ROOT).as_posix(),
        "table_sha256": sha256_file(table_path),
        "seed_draw": DRAW,
        "seed_index": POWER_INDEX,
        "replicates": POWER_REPLICATES,
        "bootstrap": POWER_BOOTSTRAP,
        "samples": POWER_SAMPLES,
        "counting_variance": counting,
        "alpha": ALPHA,
        "useful_ratio": USEFUL_RATIO,
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "--mesh-gate":
        print(mesh_gate(Path(argv[1]).resolve(), Path(argv[2]).resolve()))
        return 0
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    paths = [Path(arg).resolve() for arg in args[1:]]
    if len(args) == 4 and args[0] == "--freeze":
        record = freeze(paths[0], paths[1])
    elif len(args) == 3 and args[0] == "--power":
        record = power(paths[0])
    elif len(args) == 5 and args[0] == "--score":
        record = score(paths[0], paths[1], paths[2])
    else:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    out = paths[-1]
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
