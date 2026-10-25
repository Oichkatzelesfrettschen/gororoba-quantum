"""Identifiability of the Ascella perturbed-compilation case, sized before any acquisition.

docs/state/plans/ascella-perturbed-compilation-case.json fixes the case: one logical setting (SETTING, the largest
X residual of the drive-linear training-only folds) submitted at many compilation seeds. The service fits the
occupied input column from seeded random starts (docs/notes/quandela/form-dwell-decomposition.md), so each seed
serves another mesh with the same ideal output, and seed 0 returns job-00's mesh.

The served meshes are unknown before the job returns, so this script stands in for them with phase vectors of the
returned mesh layout that reproduce the setting's twelve output intensities: damped minimum-norm steps over the
126 heaters from starts spread over the torus by the additive recurrence of the plastic-number generalization
(no seed). Each family of scripts/ascella_drive_response.py and the static heater
family, fitted on all of job-00, is planted as the device's response, and two quantities are computed in closed
form for each design (perturbed compilations N, anchors at the returned compilation, samples M per iteration):

- R1 power: the block-conditioned X statistic of each perturbed compilation has the planted mean mu_n and the
  multinomial variance v_n; the dispersion sum_n (z_n - zbar)^2 / v_n is noncentral chi-square on N - 1 degrees
  of freedom with noncentrality sum_n (mu_n - mubar)^2 / v_n, and the power is its tail beyond the central
  0.99 quantile;
- R3 variance ratio: the posterior Hessian H of the full-data fit, less the expected information F_k of
  configuration k's settings at the mode (the leave-one-out approximation of the training-only fold), plus the
  expected information of the design, gives the fold covariance; g C g^T over the counting variance of each of
  the 19 scored configurations, and its median per readout. The design-free value approximates the recorded
  median ratio of the training-only folds, and the record carries both.

The chosen design is the cheapest whose R1 power reaches POWER under every planted family and whose R3 median
ratio is at most 1 on both readouts for the order-1 families; detectable_x_sd is the standard deviation of the
compilation-induced X means that the dispersion test detects at POWER. --check replays the record within the fit
replay bounds of scripts/ascella_physical_models.py, under the kernel pair the gate runner sets.

Usage:
  "$PYTHON" scripts/ascella_compilation_design.py JOB_00 OUT [--check]
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

import ascella_configuration_holdout as holdout  # noqa: E402
import ascella_drive_response as drive  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402

from parallel import ordered_map  # noqa: E402

SETTING = "theta2-x-arm0"
# (name, basis kind or None for one offset per heater, order, heater widths per basis function).
FAMILIES: tuple[tuple[str, str | None, int, Any], ...] = (
    ("static_heater_0.3", None, 0, 0.3),
    ("static_heater_0.3_drive_slope_0.1", "linear", 1, (0.3, 0.1)),
    ("drive_polynomial_1_tau_0.3", "polynomial", 1, 0.3),
    ("drive_harmonic_1_tau_0.3", "harmonic", 1, 0.3),
)
PERTURBED = (24, 56, 120, 248)
ANCHORS = 8
SAMPLES = (8192, 16384, 32768)
ALPHA = 0.01
# The dark outputs' intensities are quadratic in their amplitudes, so the damped minimum-norm steps approach them
# linearly; 1e-6 per intensity sits three orders below the X statistic's counting standard error.
REALIZE_TOLERANCE = 1e-6
REALIZE_STEPS = 400
REALIZE_DAMPING = 1e-9
# job-00 spent 186 s on 64 iterations; the per-sample share of that time is unresolved, so a design's seconds
# scale with its iterations alone.
SECONDS_PER_ITERATION = 186.0 / 64
JOB_SECONDS = 300.0
# A job bills 1 + 1e-6 max_iteration_shots credits (docs/design/ascella-signed-coherence-conformance.md, budget
# table), with max_shots twice the samples per iteration as in job-00 and job-01.
JOB_PRICE = 1.0
SHOT_PRICE = 1e-6
SHOTS_PER_SAMPLE = 2
POWER = 0.9
# The plan's R3 acceptance: the order-1 families' median variance ratio at most this on both readouts.
RATIO_LIMIT = 1.0
ORDER_ONE = ("static_heater_0.3_drive_slope_0.1", "drive_polynomial_1_tau_0.3", "drive_harmonic_1_tau_0.3")


def basis(phases: np.ndarray, kind: str | None, order: int) -> np.ndarray | None:
    if kind is None:
        return None
    if kind == "linear":
        return np.stack([np.ones_like(phases), phases % (2 * math.pi)], axis=-1)
    return drive.heater_basis(phases, kind, order)


def starts(phases: np.ndarray, count: int) -> np.ndarray:
    """count points of the additive recurrence with the generalized plastic-number steps, one row per start."""
    dimension = len(phases)
    root = 2.0
    for _ in range(64):
        root = (1 + root) ** (1 / (dimension + 1))
    steps = np.array([root ** -(h + 1) for h in range(dimension)])
    n = np.arange(1, count + 1)[:, None]
    return 2 * math.pi * ((0.5 + n * steps[None, :]) % 1)


def realize(data: dict[str, Any], k: int, count: int) -> tuple[np.ndarray, int]:
    """The first count heater-phase vectors, in start order, of the returned layout that reach configuration k's
    twelve output intensities, and the number of starts tried."""
    source = data["sources"][k : k + 1]
    target = models.pure_jacobians(data["couplers"], data["arch"], data["phases"][k : k + 1], source)[0][0]
    tried = 2 * count
    phases = starts(data["phases"][k], tried)
    heaters = phases.shape[1]
    for _ in range(REALIZE_STEPS):
        p, dp = models.pure_jacobians(data["couplers"], data["arch"], phases, np.repeat(source, tried))
        residual = p - target[None, :]
        jacobian = dp[:, :, :heaters]
        normal = jacobian @ jacobian.transpose(0, 2, 1) + REALIZE_DAMPING * np.eye(len(target))[None]
        phases -= np.einsum("cmh,cm->ch", jacobian, np.linalg.solve(normal, residual[:, :, None])[:, :, 0])
    p = models.pure_jacobians(data["couplers"], data["arch"], phases, np.repeat(source, tried))[0]
    reached = np.flatnonzero(np.abs(p - target[None, :]).max(axis=1) < REALIZE_TOLERANCE)
    models.require(len(reached) >= count, f"realize: {len(reached)} of {tried} starts reached the target")
    return phases[reached[:count]], tried


def design_data(data: dict[str, Any], phases: np.ndarray, k: int) -> dict[str, Any]:
    return {
        "couplers": data["couplers"],
        "arch": data["arch"],
        "phases": phases,
        "sources": np.full(len(phases), data["sources"][k]),
    }


def fit(item: tuple[str, str | None, int, Any, dict[str, Any]]) -> dict[str, Any]:
    """The family's full-data posterior mode on job-00 and the posterior Hessian there."""
    name, kind, order, tau, data = item
    b = basis(data["phases"], kind, order)
    data = data if b is None else {**data, "heater_basis": b}
    widths = models.prior_widths(data, tau, None)
    free = widths > 0
    offsets, hessian = models.static_mode(data, widths[free], free)
    return {"family": name, "offsets": offsets, "hessian": hessian, "free": free}


def setting_information(data: dict[str, Any], light: np.ndarray, dlight: np.ndarray, rows: list[int]) -> np.ndarray:
    """Expected multinomial information of the listed settings at the mode."""
    total = data["block"].sum(axis=1)
    pi = models.setting_probabilities(data, light)
    share = (total - data["background"].sum(axis=1)) / total
    out = np.zeros((dlight.shape[2], dlight.shape[2]))
    for s in rows:
        dpi = share[s] * dlight[data["configuration"][s]]
        out += total[s] * (dpi / pi[s][:, None]).T @ dpi
    return out


def rates(data: dict[str, Any], k: int, samples: int) -> tuple[float, np.ndarray]:
    """Per-sample block events and in-block background of configuration k's X settings."""
    settings = data["record"]["manifest"]["settings"]
    chosen = [i for i in np.flatnonzero(data["configuration"] == k) if settings[i]["readout"] == "x"]
    block = float(data["block"][chosen].sum()) / (len(chosen) * samples)
    return block, data["background"][chosen].sum(axis=0) / (len(chosen) * samples)


def detectable_noncentrality(dof: int, critical: float) -> float:
    """The noncentrality at which the dispersion test reaches POWER, by bisection."""
    low, high = 0.0, 1.0
    while stats.ncx2.sf(critical, dof, high) < POWER:
        high *= 2
    for _ in range(100):
        middle = (low + high) / 2
        low, high = (middle, high) if stats.ncx2.sf(critical, dof, middle) < POWER else (low, middle)
    return high


def chosen_design(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """The cheapest design, then the fewest iterations, at which every order-1 family meets the R3 acceptance and
    R1 reaches POWER under every planted family."""
    designs = sorted(
        {(row["credits"], row["perturbed"], row["samples_per_iteration"]) for row in rows},
        key=lambda d: (d[0], d[1], d[2]),
    )
    for credits, count, samples in designs:
        same = [r for r in rows if r["perturbed"] == count and r["samples_per_iteration"] == samples]
        if all(r["r1_power"] >= POWER for r in same) and all(
            max(r["r3_median_variance_ratio"].values()) <= RATIO_LIMIT for r in same if r["family"] in ORDER_ONE
        ):
            return {"perturbed": count, "anchors": ANCHORS, "samples_per_iteration": samples, "credits": credits}
    raise ValueError("no design meets the acceptance")


def design_rows(item: tuple[dict[str, Any], dict[str, Any], dict[str, Any], int, int]) -> list[dict[str, Any]]:
    """R1 power and R3 median variance ratios of one family over every design."""
    planted, data, perturbed, k, job_samples = item
    family = next(f for f in FAMILIES if f[0] == planted["family"])
    _, kind, order, _ = family
    free = planted["free"]
    b = basis(data["phases"], kind, order)
    job = data if b is None else {**data, "heater_basis": b}
    light, dlight = models.static_light(job, planted["offsets"], free)
    scored = models.scored_configurations(job)
    folds = []
    for c in scored:
        members = [int(s) for s in np.flatnonzero(job["configuration"] == c)]
        reduced = planted["hessian"] - setting_information(job, light, dlight, members)
        folds.append((c, reduced, holdout.left_out_rows(job, light, dlight, c)))
    block_rate, background_rate = rates(job, k, job_samples)
    out = []
    for count in PERTURBED:
        phases = np.concatenate([perturbed["phases"][:count], np.repeat(job["phases"][k : k + 1], ANCHORS, axis=0)])
        design = design_data(job, phases, k)
        b_design = basis(phases, kind, order)
        if b_design is not None:
            design["heater_basis"] = b_design
        d_light, d_dlight = models.static_light(design, planted["offsets"], free)
        for samples in SAMPLES:
            total = block_rate * samples
            background = background_rate * samples
            share = (total - background.sum()) / total
            expected = (total - background.sum()) * d_light + background[None, :]
            mean, variance = geometry.statistic(expected, "x")
            mu, v = mean[:count], variance[:count]
            centre = float((mu / v).sum() / (1 / v).sum())
            noncentrality = float(((mu - centre) ** 2 / v).sum())
            critical = float(stats.chi2.ppf(1 - ALPHA, count - 1))
            power = float(stats.ncx2.sf(critical, count - 1, noncentrality))
            detectable = detectable_noncentrality(count - 1, critical)
            pi = expected / total
            dpi = share * d_dlight
            information = np.einsum("nmi,nmj->ij", dpi / pi[:, :, None], dpi) * total
            ratios: dict[str, list[float]] = {"x": [], "y": []}
            baseline: dict[str, list[float]] = {"x": [], "y": []}
            for _, reduced, scored_rows in folds:
                with_design = np.linalg.inv(reduced + information)
                without = np.linalg.inv(reduced)
                for readout, _, _, counting, gradient in scored_rows:
                    ratios[readout].append(float(gradient @ with_design @ gradient) / counting)
                    baseline[readout].append(float(gradient @ without @ gradient) / counting)
            iterations = count + ANCHORS
            jobs = math.ceil(iterations * SECONDS_PER_ITERATION / JOB_SECONDS)
            out.append(
                {
                    "family": planted["family"],
                    "perturbed": count,
                    "anchors": ANCHORS,
                    "samples_per_iteration": samples,
                    "noncentrality": noncentrality,
                    "r1_power": power,
                    "planted_x_spread": float(mu.max() - mu.min()),
                    "detectable_x_sd": math.sqrt(detectable * float(np.mean(v)) / count),
                    "r3_median_variance_ratio": {r: float(np.median(v)) for r, v in ratios.items()},
                    "r3_median_variance_ratio_without_design": {r: float(np.median(v)) for r, v in baseline.items()},
                    "jobs": jobs,
                    "expected_seconds": iterations * SECONDS_PER_ITERATION,
                    "credits": jobs * (JOB_PRICE + SHOTS_PER_SAMPLE * samples * SHOT_PRICE),
                }
            )
    return out


def build(a_dir: Path) -> dict[str, Any]:
    data = models.job_data(a_dir)
    models.require(data["record"]["manifest"]["job"] == "job-00", "the fit run is not job-00")
    k = next(i for i, key in enumerate(data["keys"]) if SETTING in key)
    manifest = data["record"]["manifest"]
    job_samples = manifest["max_samples"] // manifest["iterations"]
    phases, tried = realize(data, k, max(PERTURBED))
    distance = np.abs(np.angle(np.exp(1j * (phases - data["phases"][k][None, :]))))
    planted = ordered_map(fit, [(*family, data) for family in FAMILIES], min_items=1)
    rows = ordered_map(design_rows, [(p, data, {"phases": phases}, k, job_samples) for p in planted], min_items=1)
    designs = [row for family in rows for row in family]
    return {
        "schema": "ascella-perturbed-compilation-design-v1",
        "run": a_dir.relative_to(ROOT).as_posix(),
        "setting": SETTING,
        "configuration": list(data["keys"][k]),
        "realized": {
            "count": len(phases),
            "starts_tried": tried,
            "median_heater_distance": float(np.median(distance)),
            "heaters_moved_over_0.5": float(np.mean(distance > 0.5)),
        },
        "alpha": ALPHA,
        "power": POWER,
        "designs": designs,
        "chosen": chosen_design(designs),
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 2:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve())
    out = Path(args[1]).resolve()
    if check:
        models.replay(json.loads(json.dumps(record)), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
