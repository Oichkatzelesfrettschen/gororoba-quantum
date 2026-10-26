"""Decomposition of the Ascella job-02 response beyond the X statistic, and the split of its served meshes.

docs/state/plans/ascella-mesh-response-decomposition.json fixes the procedure.

`split` orders job-02's perturbed meshes, keyed by their compilation seeds, by values 0..55 of one ANU QRNG draw
(argsort, ties to the earlier mesh) and writes the first half as the exploration meshes and the rest as the held-out
meshes. The held-out meshes enter only the plan's confirmation step.

`decompose` describes job-02's light without fitting a new family:

- the block light: the background-subtracted block fractions of every iteration against the returned mesh's ideal,
  their mean deviation at the anchor mesh and over the perturbed meshes, and the eigenvalues of the deviations'
  covariance whitened by the mean counting covariance of the subtracted fractions, the multinomial over block and
  outside clicks carried through the background subtraction (1 is counting noise), in the three coordinates of modes 0..2,
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

`explore` runs the plan's screens on job-02's exploration meshes alone, each with its trial count and a null matched
to it:

- quantization: every returned phase rounded to o + r round((phi - o) / r) over QUANT_RESOLUTIONS resolutions r and
  QUANT_ORIGINS grid origins o, the statistic the largest correlation over that grid between the quantized mesh's
  light-only X and the observed X; the null repeats the same grid with every heater's origin drawn uniformly, from a
  numpy generator seeded with value NULL_INDEX of the split's draw, QUANT_NULLS times;
- scalar mesh features: the correlation of the observed X with each of SCALAR_FEATURES;
- the dark block output: over quiet iterations (outside total at or below the median of the anchor and exploration
  iterations), the Poisson dispersion of mode-2 counts at the anchor mesh and over
  the exploration meshes, the rank correlation of each exploration mesh's mode-2 excess with its |X - mean|, and the
  mode-2, outside and X change that uniform dephasing at DEPHASING_VARIANCES predicts, beside the observed X deficit
  and mode-2 excess. Incoherent noise fills the dark outputs at the order it lowers contrast; coherent error lowers it
  at first order and leaks at second.

Usage:
  "$PYTHON" scripts/ascella_mesh_decomposition.py split JOB_02 DRAW OUT [--check]
  "$PYTHON" scripts/ascella_mesh_decomposition.py decompose JOB_00 JOB_02 OUT [--check]
  "$PYTHON" scripts/ascella_mesh_decomposition.py explore JOB_02 SPLIT OUT [--check]
"""

from __future__ import annotations

import json
import math
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
QUANT_RESOLUTIONS = tuple(math.exp(math.log(0.005) + k * math.log(100.0) / 119) for k in range(120))
QUANT_ORIGINS = 8
QUANT_NULLS = 100
# The split consumes values 0..55 of its draw; value 56 seeds the quantization null.
NULL_INDEX = 56
SCALAR_FEATURES = ("phase_sum", "phase_square_sum", "near_wrap_count", "x_gradient_norm", "phase_weighted_x_gradient")
NEAR_WRAP = 0.3
DEPHASING_VARIANCES = (0.005, 0.01)
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


def light_fraction_covariance(c: dict[str, Any]) -> np.ndarray:
    """Per iteration, the covariance (iterations x 4 x 4) of the background-subtracted block fractions.

    The fractions f_m = (n_m - s_m O) / (N - S O) take the raw block counts n, their total N and the outside total O,
    with s the catalogue share of the outside total each block mode receives and S its sum. The block counts and
    the outside total are cells of one multinomial over T = N + O clicks, covariance T (diag(q) - q q^T) at the
    observed shares q, and the delta method carries it through the subtraction and the normalization."""
    dark = c["record"]["dark"]
    share = dark[: models.LOGICAL] / dark[models.LOGICAL :].sum()
    block = c["block"]
    outside = c["background"].sum(axis=1) / share.sum()
    out = np.zeros((len(block), models.LOGICAL, models.LOGICAL))
    for row, (counts, o) in enumerate(zip(block, outside, strict=True)):
        cells = np.append(counts, o)
        total = cells.sum()
        q = cells / total
        multinomial = total * (np.diag(q) - np.outer(q, q))
        denominator = counts.sum() - share.sum() * o
        fraction = (counts - share * o) / denominator
        jacobian = np.zeros((models.LOGICAL, models.LOGICAL + 1))
        jacobian[:, : models.LOGICAL] = (np.eye(models.LOGICAL) - fraction[:, None]) / denominator
        jacobian[:, models.LOGICAL] = (fraction * share.sum() - share) / denominator
        out[row] = jacobian @ multinomial @ jacobian.T
    return out


def block_geometry(c: dict[str, Any], anchor: np.ndarray) -> dict[str, Any]:
    light = c["block"] - c["background"]
    total = light.sum(axis=1)
    observed = light / total[:, None]
    covariance = light_fraction_covariance(c)
    p, _ = models.pure_jacobians(c["couplers"], c["arch"], c["phases"], c["sources"])
    ideal = (p[:, : models.LOGICAL] / p[:, : models.LOGICAL].sum(axis=1, keepdims=True))[c["configuration"]]
    deviation = observed - ideal
    coordinates = list(range(models.LOGICAL - 1))

    def spectrum(rows: np.ndarray) -> list[float]:
        noise = covariance[rows][:, coordinates][:, :, coordinates].mean(axis=0)
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


def exploration_data(c_dir: Path, split_path: Path) -> tuple[dict[str, Any], dict[str, Any], np.ndarray]:
    """job-02, its exploration meshes as a subset, and the per-mesh observed X of that subset."""
    c = models.job_data(c_dir)
    chosen = json.loads(split_path.read_text(encoding="utf-8"))
    seeds = np.array([int(s["compilation_seed"]) for s in c["record"]["manifest"]["settings"]])
    explore = reading.subset(c, np.flatnonzero(np.isin(seeds, chosen["exploration_seeds"])))
    models.require(len(explore["keys"]) == len(explore["block"]), "an exploration mesh carries more than one iteration")
    z = np.zeros(len(explore["keys"]))
    z[explore["configuration"]] = reading.x_statistics(explore)[0]
    return c, explore, z


def light_x(data: dict[str, Any], phases: np.ndarray) -> np.ndarray:
    p, _ = models.pure_jacobians(data["couplers"], data["arch"], phases, data["sources"])
    block = p[:, : models.LOGICAL]
    out: np.ndarray = (block[:, 0] - block[:, 3]) / block.sum(axis=1)
    return out


class QuantizedCorrelation:
    """Largest correlation over the origin sets between the observed X and the X of the mesh quantized at one
    resolution; an origin set holds one fraction per heater or one shared fraction."""

    def __init__(self, data: dict[str, Any], observed: np.ndarray, origins: np.ndarray) -> None:
        self.data, self.observed, self.origins = data, observed, origins

    def __call__(self, resolution: float) -> float:
        phases = self.data["phases"] % (2 * math.pi)
        best = -1.0
        for fraction in self.origins:
            origin = fraction * resolution
            quantized = origin + resolution * np.round((phases - origin) / resolution)
            best = max(best, float(np.corrcoef(light_x(self.data, quantized), self.observed)[0, 1]))
        return best


def quantization_screen(explore: dict[str, Any], z: np.ndarray, draw: Path) -> dict[str, Any]:
    shared = (np.arange(QUANT_ORIGINS) / QUANT_ORIGINS)[:, None] * np.ones((1, explore["phases"].shape[1]))
    observed = ordered_map(QuantizedCorrelation(explore, z, shared), list(QUANT_RESOLUTIONS), min_items=1)
    values = json.loads(draw.read_text(encoding="utf-8"))["values"]
    generator = np.random.default_rng(int(values[NULL_INDEX]))
    origin_sets = generator.random((QUANT_NULLS, QUANT_ORIGINS, explore["phases"].shape[1]))
    nulls = [
        max(ordered_map(QuantizedCorrelation(explore, z, origins), list(QUANT_RESOLUTIONS), min_items=1))
        for origins in origin_sets
    ]
    best = int(np.argmax(observed))
    statistic = float(observed[best])
    return {
        "trials": len(QUANT_RESOLUTIONS) * QUANT_ORIGINS,
        "statistic": statistic,
        "resolution": QUANT_RESOLUTIONS[best],
        "null_draws": QUANT_NULLS,
        "null_seed": {"draw": draw.relative_to(ROOT).as_posix(), "index": NULL_INDEX},
        "null_quantiles": {q: float(np.quantile(nulls, float(q))) for q in ("0.5", "0.9", "0.975")},
        "p": float((1 + sum(n >= statistic for n in nulls)) / (1 + QUANT_NULLS)),
    }


def feature_screen(explore: dict[str, Any], z: np.ndarray) -> dict[str, Any]:
    phases = explore["phases"] % (2 * math.pi)
    heaters = phases.shape[1]
    _, dp = models.pure_jacobians(explore["couplers"], explore["arch"], explore["phases"], explore["sources"])
    gradient = dp[:, 0, :heaters] - dp[:, 3, :heaters]
    features = {
        "phase_sum": phases.sum(axis=1),
        "phase_square_sum": (phases * phases).sum(axis=1),
        "near_wrap_count": ((phases < NEAR_WRAP) | (phases > 2 * math.pi - NEAR_WRAP)).sum(axis=1).astype(float),
        "x_gradient_norm": np.linalg.norm(gradient, axis=1),
        "phase_weighted_x_gradient": (phases * np.abs(gradient)).sum(axis=1),
    }
    out = {}
    for name in SCALAR_FEATURES:
        test = stats.pearsonr(features[name], z)
        out[name] = {"r": float(test.statistic), "p": float(test.pvalue)}
    return {"features": out, "trials": len(SCALAR_FEATURES)}


def dark_output(c: dict[str, Any], split_path: Path) -> dict[str, Any]:
    chosen = json.loads(split_path.read_text(encoding="utf-8"))
    seeds = np.array([int(s["compilation_seed"]) for s in c["record"]["manifest"]["settings"]])
    counts = c["record"]["counts"]
    outside = counts[:, models.LOGICAL :].sum(axis=1)
    explore = np.isin(seeds, chosen["exploration_seeds"])
    # The held-out meshes enter only the confirmation step, so the quiet cutoff reads the anchor and exploration
    # iterations alone.
    permitted = explore | (seeds == 0)
    quiet = outside <= np.median(outside[permitted])
    mode_2 = counts[:, DARK_BLOCK_MODE]
    background = c["background"][:, DARK_BLOCK_MODE]
    z = reading.x_statistics(c)[0]
    out: dict[str, Any] = {}
    for name, rows in (("anchor", (seeds == 0) & quiet), ("exploration", explore & quiet)):
        k = mode_2[rows]
        mean = float(k.mean())
        statistic = float(((k - mean) ** 2).sum() / mean)
        out[name] = {
            "iterations": int(rows.sum()),
            "mean_count": mean,
            "mean_background": float(background[rows].mean()),
            "dispersion": statistic,
            "dof": int(rows.sum()) - 1,
            "p": float(stats.chi2.sf(statistic, int(rows.sum()) - 1)),
        }
    rows = explore & quiet
    test = stats.spearmanr(np.abs(z[rows] - z[explore].mean()), mode_2[rows] - background[rows])
    out["excess_against_x_deviation"] = {"rho": float(test.statistic), "p": float(test.pvalue)}
    block_total = c["block"].sum(axis=1)
    out["observed"] = {
        "x_deficit": float(z[explore].mean() - light_x(c, c["phases"])[0]),
        "mode_2_excess": float(((mode_2 - background)[rows] / block_total[rows]).mean()),
    }
    sub = reading.subset(c, np.flatnonzero(explore))
    pure = models.channel(sub["couplers"], sub["arch"], sub["phases"], sub["sources"], 0.0, 0.0)
    out["dephasing"] = []
    for variance in DEPHASING_VARIANCES:
        p = models.channel(sub["couplers"], sub["arch"], sub["phases"], sub["sources"], variance, 0.0)
        block, base = p[:, : models.LOGICAL], pure[:, : models.LOGICAL]
        shift = (block[:, 0] - block[:, 3]) / block.sum(axis=1) - (base[:, 0] - base[:, 3]) / base.sum(axis=1)
        out["dephasing"].append(
            {
                "variance": variance,
                "mean_x_change": float(shift.mean()),
                "mode_2_light": float((block[:, DARK_BLOCK_MODE] / block.sum(axis=1)).mean()),
                "outside_light": float(p[:, models.LOGICAL :].sum(axis=1).mean()),
            }
        )
    return out


def explore(c_dir: Path, split_path: Path) -> dict[str, Any]:
    c, explore_data, z = exploration_data(c_dir, split_path)
    draw = ROOT / json.loads(split_path.read_text(encoding="utf-8"))["draw"]
    return {
        "schema": "ascella-mesh-exploration-v1",
        "plan": "docs/state/plans/ascella-mesh-response-decomposition.json",
        "run": c_dir.relative_to(ROOT).as_posix(),
        "split": split_path.relative_to(ROOT).as_posix(),
        "exploration_meshes": len(z),
        "quantization": quantization_screen(explore_data, z, draw),
        "scalar_features": feature_screen(explore_data, z),
        "dark_output": dark_output(c, split_path),
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
    if len(args) == 4 and args[0] == "explore":
        emit(explore(Path(args[1]).resolve(), Path(args[2]).resolve()), Path(args[3]).resolve(), check)
        return 0
    raise ValueError(f"usage: see the module docstring, not {argv}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
