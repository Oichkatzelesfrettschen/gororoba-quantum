"""First-principles controls on the persistent per-mesh X error of job-02's seeded meshes (job-02, job-03, job-08).

The long-horizon reading (scripts/ascella_long_horizon_reading.py) finds the per-mesh deviation of the
block-conditioned X statistic z = (n0 - n3) / N persistent across twelve days. This record separates the three sources
a persistent deviation can have and tests the use the persistence offers:

- Compiler: each served unitary's own ideal z, from its computed_circuit and computed_input, against the logical
  ideal and against the observed deviations. A served circuit that missed the target would carry a deterministic,
  perfectly persistent error that the chip never caused.
- Analysis: the echoed compilation seed and circuit parameters of every iteration against its setting; the
  correlation of the two jobs' perturbed z paired by setting name against the pairing by position; the rank
  correlation of each mesh's positions in the two jobs; the within-job position trend and the correlation after
  removing each job's linear position trend.
- Chip: the persistence of each mesh's dark-port (mode 2) share of block counts between the jobs.
- Correction: a per-seed offset table fitted on job-02 and job-03 alone (the slope of job-03's centered z on job-02's
  times the mean of the two runs' centered z) applied to job-08, out of sample; the record gives the variance of
  job-08's centered perturbed z before and after the correction and the counting variance that bounds it.

Usage:
  "$PYTHON" scripts/ascella_mesh_error_controls.py JOB_02 JOB_03 JOB_08 OUT [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_physical_models as models  # noqa: E402

from parallel import ordered_map  # noqa: E402

JOBS = ("job-02", "job-03", "job-08")


def served_ideal(fields: dict[str, Any]) -> float:
    """The ideal z of one served circuit: (p0 - p3) / (p0 + p1 + p2 + p3) from its unitary's input column."""
    from perceval.serialization import deserialize

    unitary = np.asarray(deserialize(fields["computed_circuit"]).compute_unitary(), dtype=np.complex128)
    occupation = list(deserialize(fields["computed_input"]))
    sources = [mode for mode, count in enumerate(occupation) if count]
    models.require(len(sources) == 1, f"computed_input occupies {sources}")
    p = np.abs(unitary[:, sources[0]]) ** 2
    return float((p[0] - p[3]) / p[:4].sum())


def job(directory: Path) -> dict[str, Any]:
    data = models.job_data(directory)
    manifest = data["record"]["manifest"]
    rows = data["record"]["results"]["iterations"]
    settings = manifest["settings"]
    z, v = reading.x_statistics(data)
    block = data["block"]
    return {
        "name": manifest["job"],
        "names": [s["name"] for s in settings],
        "echo": sum(
            int(r["iteration"]["compilation_seed"] == s["compilation_seed"])
            * int(r["iteration"]["circuit_params"] == s["circuit_params"])
            for r, s in zip(rows, settings, strict=True)
        ),
        "served": np.array(ordered_map(served_ideal, [r["result_fields"] for r in rows])),
        "ideal": float(settings[0]["ideal"]["z"]),
        "z": z,
        "v": v,
        "anchor": reading.anchors_of(data),
        "dark": block[:, 2] / block.sum(axis=1),
    }


def centered(values: np.ndarray) -> np.ndarray:
    out: np.ndarray = values - values.mean()
    return out


def detrended(values: np.ndarray, positions: np.ndarray) -> np.ndarray:
    out: np.ndarray = values - np.polyval(np.polyfit(positions, values, 1), positions)
    return out


def build(directories: list[Path]) -> dict[str, Any]:
    runs = [job(directory) for directory in directories]
    models.require([run["name"] for run in runs] == list(JOBS), f"the runs are {[run['name'] for run in runs]}")
    order = [name for name, anchor in zip(runs[2]["names"], runs[2]["anchor"], strict=True) if not anchor]
    index = [{name: i for i, name in enumerate(run["names"])} for run in runs]
    position = [np.array([index[k][name] for name in order], dtype=float) for k in range(3)]
    z = [run["z"][position[k].astype(int)] for k, run in enumerate(runs)]
    dark = [run["dark"][position[k].astype(int)] for k, run in enumerate(runs)]
    served = runs[2]["served"][position[2].astype(int)]
    deviation = centered(z[2])
    by_position = np.corrcoef(z[1], runs[2]["z"][position[1].astype(int)])[0, 1]
    slope = float(centered(z[0]) @ centered(z[1]) / (centered(z[0]) @ centered(z[0])))
    table = slope * 0.5 * (centered(z[0]) + centered(z[1]))
    corrected = deviation - table
    counting = float(runs[2]["v"][position[2].astype(int)].mean())
    return {
        "schema": "ascella-mesh-error-controls-v1",
        "runs": [directory.relative_to(ROOT).as_posix() for directory in directories],
        "perturbed_meshes": len(order),
        "compiler": {
            "logical_ideal": runs[2]["ideal"],
            "served_ideal_mean": float(served.mean()),
            "served_ideal_sd": float(served.std(ddof=1)),
            "served_ideal_identical_across_jobs": bool(
                all(np.array_equal(run["served"][position[k].astype(int)], served) for k, run in enumerate(runs))
            ),
            "observed_sd": [float(values.std(ddof=1)) for values in z],
            "counting_sd": [float(np.sqrt(run["v"].mean())) for run in runs],
            "served_against_observed_r": float(np.corrcoef(centered(served), deviation)[0, 1]),
        },
        "analysis": {
            "echoed_seed_and_parameters": [run["echo"] for run in runs],
            "iterations": [len(run["names"]) for run in runs],
            "r_by_name_03_08": float(np.corrcoef(z[1], z[2])[0, 1]),
            "r_by_position_03_08": float(by_position),
            "position_rank_correlation_03_08": float(stats.spearmanr(position[1], position[2]).statistic),
            "position_trend_spearman": [float(stats.spearmanr(position[k], z[k]).statistic) for k in range(3)],
            "r_detrended_03_08": float(np.corrcoef(detrended(z[1], position[1]), detrended(z[2], position[2]))[0, 1]),
        },
        "chip": {
            "dark_share_mean": [float(values.mean()) for values in dark],
            "dark_share_r_03_08": float(np.corrcoef(dark[1], dark[2])[0, 1]),
            "dark_share_r_02_08": float(np.corrcoef(dark[0], dark[2])[0, 1]),
        },
        "correction": {
            "slope_02_to_03": slope,
            "variance_before": float(deviation.var(ddof=1)),
            "variance_after": float(corrected.var(ddof=1)),
            "counting_variance": counting,
            "sd_before": float(deviation.std(ddof=1)),
            "sd_after": float(corrected.std(ddof=1)),
        },
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 4:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build([Path(arg).resolve() for arg in args[:3]])
    out = Path(args[3]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
