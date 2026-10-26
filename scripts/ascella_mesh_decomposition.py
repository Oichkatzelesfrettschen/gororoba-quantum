"""Decomposition of the Ascella job-02 response beyond the X statistic, and the split of its served meshes.

docs/state/plans/ascella-mesh-response-decomposition.json fixes the procedure.

`split` orders job-02's perturbed meshes, keyed by their compilation seeds, by values 0..55 of one ANU QRNG draw
(argsort, ties to the earlier mesh) and writes the first half as the exploration meshes and the rest as the held-out
meshes. The held-out meshes enter only the plan's confirmation step.

`decompose` describes job-02's light without fitting a new family:

- the block light: the background-subtracted block fractions of every iteration against the returned mesh's ideal,
  their mean deviation at the anchor mesh and over the perturbed meshes, and the eigenvalues of the deviations'
  covariance whitened by the mean multinomial covariance (1 is counting noise), in the three coordinates of modes 0..2,
  over every iteration and again over the iterations at or below the median outside total, because the in-block share
  of a background burst follows the catalogue dark profile only on average;
- the anchor X dispersion: chi-square of the anchors' X statistics about their inverse-variance mean;
- the outside clicks: per iteration the outside-block total, its lag-1 correlation in execution order, and the
  outside mode profile of the iterations above and below the median total beside the catalogue dark profile;
- the leakage bound: over the iterations at or below the median outside total, the median fraction of all clicks in
  the dark block output (mode 2) and in the outside modes, which bounds the light that leaves the block because it
  also counts dark clicks;
- the predicted leakage of the static families: each fitted on job-00 at the posterior mode, its light outside modes
  0, 1 and 3 at every perturbed mesh.

Usage:
  "$PYTHON" scripts/ascella_mesh_decomposition.py split JOB_02 DRAW OUT [--check]
  "$PYTHON" scripts/ascella_mesh_decomposition.py decompose JOB_00 JOB_02 OUT [--check]
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

LIGHT_MODES = (0, 1, 3)
DARK_BLOCK_MODE = 2
# (name, heater tau, coupler tau) of the static families whose leakage the record predicts.
LEAK_FAMILIES: tuple[tuple[str, float | None, float | None], ...] = (
    ("static_heater_offsets_tau_0.3", 0.3, None),
    ("static_coupler_offsets_tau_0.1", None, 0.1),
    ("static_heater_0.3_coupler_0.1_offsets", 0.3, 0.1),
)


def perturbed_seeds(c: dict[str, Any]) -> list[int]:
    """Compilation seeds of job-02's perturbed iterations in execution order, one per served mesh."""
    settings = c["record"]["manifest"]["settings"]
    seeds = [int(s["compilation_seed"]) for s in settings if int(s["compilation_seed"]) != 0]
    models.require(len(seeds) == len(set(seeds)), "a nonzero compilation seed repeats")
    return seeds


def split(c_dir: Path, draw: Path) -> dict[str, Any]:
    c = models.job_data(c_dir)
    seeds = perturbed_seeds(c)
    values = json.loads(draw.read_text(encoding="utf-8"))["values"]
    models.require(len(values) >= len(seeds), "the draw holds fewer values than meshes")
    order = np.argsort(np.array(values[: len(seeds)]), kind="stable")
    half = len(seeds) // 2
    return {
        "schema": "ascella-mesh-split-v1",
        "plan": "docs/state/plans/ascella-mesh-response-decomposition.json",
        "run": c_dir.relative_to(ROOT).as_posix(),
        "draw": draw.relative_to(ROOT).as_posix(),
        "draw_indices": [0, len(seeds) - 1],
        "rule": "argsort of the draw's values 0..55 over the perturbed seeds in execution order, ties to the earlier",
        "exploration_seeds": sorted(seeds[i] for i in order[:half]),
        "held_out_seeds": sorted(seeds[i] for i in order[half:]),
    }


def block_geometry(c: dict[str, Any], anchor: np.ndarray) -> dict[str, Any]:
    light = c["block"] - c["background"]
    total = light.sum(axis=1)
    observed = light / total[:, None]
    p, _ = models.pure_jacobians(c["couplers"], c["arch"], c["phases"], c["sources"])
    ideal = (p[:, : models.LOGICAL] / p[:, : models.LOGICAL].sum(axis=1, keepdims=True))[c["configuration"]]
    deviation = observed - ideal
    coordinates = list(range(models.LOGICAL - 1))

    def spectrum(rows: np.ndarray) -> list[float]:
        noise = np.mean(
            [
                (np.diag(f[coordinates]) - np.outer(f[coordinates], f[coordinates])) / n
                for f, n in zip(observed[rows], total[rows], strict=True)
            ],
            axis=0,
        )
        inverse = np.linalg.inv(np.linalg.cholesky(noise))
        whitened = inverse @ np.cov(deviation[rows][:, coordinates].T) @ inverse.T
        return [float(w) for w in np.linalg.eigvalsh(whitened)]

    return {
        "ideal": [float(x) for x in ideal[0]],
        "mean_deviation_anchor": [float(x) for x in deviation[anchor].mean(axis=0)],
        "mean_deviation_perturbed": [float(x) for x in deviation[~anchor].mean(axis=0)],
        "whitened_eigenvalues_anchor": spectrum(anchor),
        "whitened_eigenvalues_perturbed": spectrum(~anchor),
    }


def anchor_dispersion(c: dict[str, Any], anchor: np.ndarray) -> dict[str, float]:
    z, v = reading.x_statistics(c)
    z, v = z[anchor], v[anchor]
    centre = float((z / v).sum() / (1 / v).sum())
    statistic = float(((z - centre) ** 2 / v).sum())
    dof = int(anchor.sum()) - 1
    return {"chi_square": statistic, "dof": dof, "p": float(stats.chi2.sf(statistic, dof))}


def outside_clicks(c: dict[str, Any]) -> dict[str, Any]:
    counts = c["record"]["counts"]
    outside = counts[:, models.LOGICAL :]
    total = outside.sum(axis=1)
    profile = outside / total[:, None]
    high = total > np.median(total)
    dark = c["record"]["dark"][models.LOGICAL :]
    lag = stats.pearsonr(total[:-1], total[1:])
    quiet = ~high
    clicks = counts.sum(axis=1)
    return {
        "totals": [int(x) for x in total],
        "lag_1": {"r": float(lag.statistic), "p": float(lag.pvalue)},
        "profile_high": [float(x) for x in profile[high].mean(axis=0)],
        "profile_low": [float(x) for x in profile[quiet].mean(axis=0)],
        "profile_dark_catalogue": [float(x) for x in dark / dark.sum()],
        "quiet_iterations": int(quiet.sum()),
        "quiet_dark_block_fraction": float(np.median(counts[quiet, DARK_BLOCK_MODE] / clicks[quiet])),
        "quiet_outside_fraction": float(np.median(total[quiet] / clicks[quiet])),
    }


def family_leak(item: tuple[str, float | None, float | None, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    name, heater_tau, coupler_tau, a, perturbed = item
    widths = models.prior_widths(a, heater_tau, coupler_tau)
    free = widths > 0
    offsets, _ = models.static_mode(a, widths[free], free)
    full = np.zeros(len(free))
    full[free] = offsets
    heaters = a["phases"].shape[1]
    leak_modes = [m for m in range(models.MODES) if m not in LIGHT_MODES]

    def leak(data: dict[str, Any]) -> np.ndarray:
        p, _ = models.pure_jacobians(
            data["couplers"] + full[heaters:], data["arch"], data["phases"] + full[None, :heaters], data["sources"]
        )
        out: np.ndarray = p[:, leak_modes].sum(axis=1)
        return out

    on_job_02, on_job_00 = leak(perturbed), leak(a)
    return {
        "family": name,
        "job_02_median": float(np.median(on_job_02)),
        "job_02_max": float(on_job_02.max()),
        "job_00_median": float(np.median(on_job_00)),
    }


def decompose(a_dir: Path, c_dir: Path) -> dict[str, Any]:
    a, c = models.job_data(a_dir), models.job_data(c_dir)
    models.require(a["record"]["manifest"]["job"] == "job-00" and c["record"]["manifest"]["job"] == "job-02", "jobs")
    anchor = reading.anchors_of(c)
    meshes = reading.new_meshes(a, c, anchor)
    perturbed = reading.subset(c, np.flatnonzero([int(m) in meshes for m in c["configuration"]]))
    outside = c["record"]["counts"][:, models.LOGICAL :].sum(axis=1)
    quiet_c = reading.subset(c, np.flatnonzero(outside <= np.median(outside)))
    leaks = ordered_map(family_leak, [(*f, a, perturbed) for f in LEAK_FAMILIES], min_items=1)
    return {
        "schema": "ascella-mesh-decomposition-v1",
        "plan": "docs/state/plans/ascella-mesh-response-decomposition.json",
        "runs": [a_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "block": block_geometry(c, anchor),
        "block_quiet": block_geometry(quiet_c, reading.anchors_of(quiet_c)),
        "anchor_x_dispersion": anchor_dispersion(c, anchor),
        "outside": outside_clicks(c),
        "family_leakage": leaks,
    }


def emit(record: dict[str, Any], out: Path, check: bool) -> None:
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) == 4 and args[0] == "split":
        emit(split(Path(args[1]).resolve(), Path(args[2]).resolve()), Path(args[3]).resolve(), check)
        return 0
    if len(args) == 4 and args[0] == "decompose":
        emit(decompose(Path(args[1]).resolve(), Path(args[2]).resolve()), Path(args[3]).resolve(), check)
        return 0
    raise ValueError(f"usage: see the module docstring, not {argv}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
