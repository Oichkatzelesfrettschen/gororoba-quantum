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
  multinomial variance v_n. R1 divides the perturbed dispersion sum_n (z_n - zbar)^2 / v_n per degree of freedom
  by the anchors' and refers the ratio to its label permutations; the ratio of a noncentral chi-square on N - 1
  degrees of freedom (noncentrality sum_n (mu_n - mubar)^2 / v_n) to a central one on ANCHORS - 1, each over its
  degrees of freedom, is noncentral F, and the power is its tail beyond the central F 0.99 quantile, the normal
  approximation of the permutation threshold;
- R3 variance ratio: the posterior Hessian H of the full-data fit, less the expected information F_k of
  configuration k's settings at the mode (the leave-one-out approximation of the training-only fold), plus the
  expected information of the design's perturbed iterations, gives the fold covariance; g C g^T over the
  counting variance of each of the 19 scored configurations, and its median per readout. The design-free value
  approximates the recorded median ratio of the training-only folds, and the record carries both.

The chosen design is the cheapest whose R1 power reaches POWER under every planted family and whose R3 median
ratio is at most 1 on both readouts for the order-1 families; detectable_x_sd is the standard deviation of the
compilation-induced X means that the anchor-ratio test detects at POWER. --check replays the record within the fit
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


def detectable_noncentrality(dof: int, anchor_dof: int, critical: float) -> float:
    """The noncentrality at which the anchor-ratio test reaches POWER, by bisection."""
    low, high = 0.0, 1.0
    while stats.ncf.sf(critical, dof, anchor_dof, high) < POWER:
        high *= 2
    for _ in range(100):
        middle = (low + high) / 2
        low, high = (middle, high) if stats.ncf.sf(critical, dof, anchor_dof, middle) < POWER else (low, middle)
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


def family_context(item: tuple[dict[str, Any], dict[str, Any], int, int]) -> dict[str, Any]:
    """The design-independent part of one family's sizing: each scored fold's reduced Hessian with its inverse and
    statistic gradients, and configuration k's per-sample block and background rates."""
    planted, data, k, job_samples = item
    _, kind, order, _ = next(f for f in FAMILIES if f[0] == planted["family"])
    b = basis(data["phases"], kind, order)
    job = data if b is None else {**data, "heater_basis": b}
    light, dlight = models.static_light(job, planted["offsets"], planted["free"])
    folds = []
    for c in models.scored_configurations(job):
        members = [int(s) for s in np.flatnonzero(job["configuration"] == c)]
        reduced = planted["hessian"] - setting_information(job, light, dlight, members)
        rows = [
            (readout, counting, gradient)
            for readout, _, _, counting, gradient in holdout.left_out_rows(job, light, dlight, c)
        ]
        folds.append((reduced, np.linalg.inv(reduced), rows))
    block_rate, background_rate = rates(job, k, job_samples)
    return {
        "kind": kind,
        "order": order,
        "mesh": {
            "couplers": job["couplers"],
            "arch": job["arch"],
            "phases": job["phases"][k : k + 1],
            "sources": job["sources"][k : k + 1],
        },
        "folds": folds,
        "block_rate": block_rate,
        "background_rate": background_rate,
    }


def design_row(item: tuple[dict[str, Any], dict[str, Any], np.ndarray, int, int]) -> dict[str, Any]:
    """R1 power and R3 median variance ratios of one family at one design (perturbed count, samples)."""
    planted, context, perturbed, count, samples = item
    mesh = context["mesh"]
    phases = np.concatenate([perturbed[:count], np.repeat(mesh["phases"], ANCHORS, axis=0)])
    design = {
        "couplers": mesh["couplers"],
        "arch": mesh["arch"],
        "phases": phases,
        "sources": np.full(len(phases), mesh["sources"][0]),
    }
    b_design = basis(phases, context["kind"], context["order"])
    if b_design is not None:
        design["heater_basis"] = b_design
    d_light, d_dlight = models.static_light(design, planted["offsets"], planted["free"])
    total = context["block_rate"] * samples
    background = context["background_rate"] * samples
    share = (total - background.sum()) / total
    expected = (total - background.sum()) * d_light + background[None, :]
    mean, variance = geometry.statistic(expected, "x")
    mu, v = mean[:count], variance[:count]
    centre = float((mu / v).sum() / (1 / v).sum())
    noncentrality = float(((mu - centre) ** 2 / v).sum())
    critical = float(stats.f.ppf(1 - ALPHA, count - 1, ANCHORS - 1))
    power = float(stats.ncf.sf(critical, count - 1, ANCHORS - 1, noncentrality))
    detectable = detectable_noncentrality(count - 1, ANCHORS - 1, critical)
    pi = expected / total
    dpi = share * d_dlight
    # R3 trains on the perturbed iterations alone; the anchors repeat a job-00 mesh and stay out.
    information = np.einsum("nmi,nmj->ij", dpi[:count] / pi[:count, :, None], dpi[:count]) * total
    ratios: dict[str, list[float]] = {"x": [], "y": []}
    baseline: dict[str, list[float]] = {"x": [], "y": []}
    for reduced, without, rows in context["folds"]:
        with_design = np.linalg.inv(reduced + information)
        for readout, counting, gradient in rows:
            ratios[readout].append(float(gradient @ with_design @ gradient) / counting)
            baseline[readout].append(float(gradient @ without @ gradient) / counting)
    iterations = count + ANCHORS
    jobs = math.ceil(iterations * SECONDS_PER_ITERATION / JOB_SECONDS)
    return {
        "family": planted["family"],
        "perturbed": count,
        "anchors": ANCHORS,
        "samples_per_iteration": samples,
        "noncentrality": noncentrality,
        "r1_power": power,
        "planted_x_spread": float(mu.max() - mu.min()),
        "detectable_x_sd": math.sqrt(detectable * float(np.mean(v)) / count),
        "r3_median_variance_ratio": {r: float(np.median(values)) for r, values in ratios.items()},
        "r3_median_variance_ratio_without_design": {r: float(np.median(values)) for r, values in baseline.items()},
        "jobs": jobs,
        "expected_seconds": iterations * SECONDS_PER_ITERATION,
        "credits": jobs * (JOB_PRICE + SHOTS_PER_SAMPLE * samples * SHOT_PRICE),
    }


def build(a_dir: Path) -> dict[str, Any]:
    data = models.job_data(a_dir)
    models.require(data["record"]["manifest"]["job"] == "job-00", "the fit run is not job-00")
    k = next(i for i, key in enumerate(data["keys"]) if SETTING in key)
    manifest = data["record"]["manifest"]
    job_samples = manifest["max_samples"] // manifest["iterations"]
    phases, tried = realize(data, k, max(PERTURBED))
    distance = np.abs(np.angle(np.exp(1j * (phases - data["phases"][k][None, :]))))
    planted = ordered_map(fit, [(*family, data) for family in FAMILIES], min_items=1)
    contexts = ordered_map(family_context, [(p, data, k, job_samples) for p in planted], min_items=1)
    designs = ordered_map(
        design_row,
        [
            (p, context, phases, count, samples)
            for p, context in zip(planted, contexts, strict=True)
            for count in PERTURBED
            for samples in SAMPLES
        ],
        min_items=1,
    )
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
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
