"""Drive-dependent heater response of the Ascella analyzer: fitted on job-00, scored on job-01 and on configurations
left out of training.

docs/design/ascella-signed-coherence-conformance.md#polynomial-and-harmonic-drive-responses states the families and the
reading. The Ascella phase shifters follow phi = A V^2 + b (arXiv:2306.00874, SI S-IV), so a heater's drive is
fixed by its returned phase, and an error in that heater's phase-voltage map is a function of the returned phase
rather than one offset shared by every configuration. Each family shifts heater h of configuration c by
sum_k b_k(phi_ch) w_hk, with independent N(0, tau^2) priors on the coefficients:

- polynomial: shifted Legendre polynomials of the drive u = (phi mod 2 pi) / (2 pi) up to the order, which place
  every heater's wrap at phi = 0;
- harmonic: 1, cos(j phi), sin(j phi) for j up to the order. The offsets b of the phase-voltage map spread over
  about a radian, so each heater wraps at its own unreported phase; any per-heater response to the drive is a
  2 pi-periodic function of the returned phase whatever its wrap, and the harmonics expand it without one.

Order 0 is the static heater-offset family of scripts/ascella_physical_models.py. Each family is fitted on all of
job-00 and scored on job-01's pooled configurations by summarize of that script. The left-out folds are those of
scripts/ascella_configuration_holdout.py: each of the 19 configurations that serve the X or Y readout is removed,
the family is fitted from the zero start on the training configurations alone and the removed configuration is
scored in its counting variance plus the fit's prediction variance. The folds share their training data, so the
sums are descriptive and carry no chi-square reference; READING applies the criterion that script's section fixed
before its run.

Usage:
  "$PYTHON" scripts/ascella_drive_response.py JOB_00 JOB_01 OUT [--check]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_configuration_holdout as holdout  # noqa: E402
import ascella_physical_models as models  # noqa: E402

from parallel import ordered_map  # noqa: E402

# (name, basis kind, order, heater prior width).
DRIVE_FAMILIES: tuple[tuple[str, str, int, float], ...] = (
    ("drive_polynomial_1_tau_0.3", "polynomial", 1, 0.3),
    ("drive_polynomial_2_tau_0.3", "polynomial", 2, 0.3),
    ("drive_harmonic_1_tau_0.3", "harmonic", 1, 0.3),
    ("drive_harmonic_1_tau_0.1", "harmonic", 1, 0.1),
    ("drive_harmonic_2_tau_0.3", "harmonic", 2, 0.3),
)
# The training-only reading of docs/design/ascella-signed-coherence-conformance.md, per readout over its ten
# configurations: a standardized sum at or above SHORTFALL keeps the shortfall with the prediction variance
# included, and one below WEAK with a median prediction-to-counting variance ratio above 1 reads as weakly
# identified predictions.
SHORTFALL = 30.0
WEAK = 20.0


def heater_basis(phases: np.ndarray, kind: str, order: int) -> np.ndarray:
    """Basis functions (configurations x heaters x K) of each heater's returned phase."""
    if kind == "polynomial":
        u = (phases % (2 * math.pi)) / (2 * math.pi)
        legendre = (np.ones_like(u), 2 * u - 1, 6 * u * u - 6 * u + 1)
        models.require(order < len(legendre), f"polynomial order {order} has no shifted Legendre polynomial here")
        return np.stack(legendre[: order + 1], axis=-1)
    models.require(kind == "harmonic", f"unknown basis {kind}")
    columns = [np.ones_like(phases)]
    for j in range(1, order + 1):
        columns += [np.cos(j * phases), np.sin(j * phases)]
    return np.stack(columns, axis=-1)


def with_basis(data: dict[str, Any], kind: str, order: int) -> dict[str, Any]:
    return {**data, "heater_basis": heater_basis(data["phases"], kind, order)}


def fit_drive(item: tuple[str, str, int, float, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """The family's posterior mode on all of job-00 from the zero start, and its job-01 held-out score."""
    family, kind, order, tau, a, b = item
    a, b = with_basis(a, kind, order), with_basis(b, kind, order)
    widths = models.prior_widths(a, tau, None)
    free = widths > 0
    offsets, hessian = models.static_mode(a, widths[free], free)
    light_a, _ = models.static_light(a, offsets, free)
    light_b, jacobian_b = models.static_light(b, offsets, free)
    out = models.summarize(family, a, b, np.linalg.inv(hessian), light_a, light_b, jacobian_b)
    out["preregistered"] = False
    coefficients = offsets[: models.heater_parameters(a)].reshape(a["phases"].shape[1], -1)
    out["basis"] = {"kind": kind, "order": order, "tau": tau, "parameters": int(free.sum())}
    out["coefficient_rms"] = [float(math.sqrt(float(np.mean(column * column)))) for column in coefficients.T]
    return out


def drive_fold(item: tuple[str, str, int, float, dict[str, Any], int]) -> dict[str, Any]:
    """The training-only fold of scripts/ascella_configuration_holdout.py on the family's basis."""
    family, kind, order, tau, data, left_out = item
    return holdout.configuration_fold((family, (tau, None), with_basis(data, kind, order), left_out))


def reading(summary: dict[str, Any]) -> dict[str, str]:
    """Per readout, the training-only reading of its standardized sum and median variance ratio."""
    out = {}
    for readout, row in summary.items():
        if row["standardized_sum"] >= SHORTFALL:
            out[readout] = "shortfall"
        elif row["standardized_sum"] < WEAK and row["median_variance_ratio"] > 1:
            out[readout] = "weakly identified"
        elif row["standardized_sum"] < WEAK:
            out[readout] = "within prediction variance"
        else:
            out[readout] = "between the thresholds"
    return out


def build(a_dir: Path, b_dir: Path) -> dict[str, Any]:
    a, b = models.job_data(a_dir), models.job_data(b_dir)
    models.require(
        a["record"]["manifest"]["job"] == "job-00" and b["record"]["manifest"]["job"] == "job-01", "job order"
    )
    models.require(sorted(a["keys"]) == sorted(b["keys"]), "the jobs group settings into other configurations")
    rows = ordered_map(fit_drive, [(*spec, a, b) for spec in DRIVE_FAMILIES], min_items=1)
    scored = models.scored_configurations(a)
    folds = ordered_map(drive_fold, [(*spec, a, k) for spec in DRIVE_FAMILIES for k in scored], min_items=1)
    nominal = models.log_likelihood(a, models.family_probabilities(a, "nominal", np.zeros(0)))
    for index, row in enumerate(rows):
        row["job_00_gain_over_nominal"] = row["job_00_log_likelihood"] - nominal
        chosen = folds[index * len(scored) : (index + 1) * len(scored)]
        summary = holdout.summarize([entry for fold in chosen for entry in fold["rows"]])
        row["folds"] = chosen
        row["summary"] = summary
        row["reading"] = reading(summary)
    return {
        "schema": "ascella-signed-coherence-drive-response-v1",
        "runs": [a_dir.relative_to(ROOT).as_posix(), b_dir.relative_to(ROOT).as_posix()],
        "configurations": len(a["keys"]),
        "scored_configurations": [list(a["keys"][k]) for k in scored],
        "heaters": int(a["phases"].shape[1]),
        "start": "zero, training configurations only",
        "families": rows,
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    holdout.emit(build(Path(args[0]).resolve(), Path(args[1]).resolve()), Path(args[2]).resolve(), check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
