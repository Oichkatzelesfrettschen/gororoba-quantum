"""Leave-one-configuration-out prediction of the Ascella analyzer response by the static offset families, with each
fold fitted from the training configurations alone and scored in the counting plus fitted-prediction variance.

For every static family of scripts/ascella_physical_models.py and every one of job-00's 30 configurations, the fold
removes that configuration's settings, fits the shared offsets at the maximum a posteriori point from the zero start
(L-BFGS, then the Newton refinement of `static_mode`), and predicts the removed configuration's X and Y statistics.
Neither the start nor the mode selection reads the left-out counts. The prediction variance of a statistic is
g C g^T, with C the inverse posterior Hessian of the fold fit and g the statistic's gradient over the free offsets,
so each scored row carries its standardized residual r / sqrt(v + g C g^T) beside the counting-only one r / sqrt(v).

With --drive the script fits, in place of the static families, the drive-dependent heater family
preregistered in docs/state/plans/ascella-configuration-holdout-training-only.json: each heater realizes
phi + a_h + k_h phi, phi the returned phase in [0, 2 pi), with the offset a_h under N(0, 0.3^2) and the drive
slope k_h under N(0, 0.1^2), as the heater basis (1, phi) of `static_light`, under the same folds and score.
Under the phase-voltage map phi = A V^2 + b the heater power V^2 is linear in phi, so k_h is a per-heater error
of the fitted slope.

The folds share 28 or 29 of their training configurations, so their residuals are dependent and a sum over folds
has no chi-square reference: the record reports the sums and per-row residuals descriptively and no p-value.
docs/design/ascella-signed-coherence-conformance.md#leave-one-configuration-out-from-training-data names the
reading each outcome supports.

Usage:
  "$PYTHON" scripts/ascella_configuration_holdout.py JOB_00 OUT [--drive] [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_coherence_repeat as repeat  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402
from bdsc_certificate import close  # noqa: E402

from parallel import ordered_map  # noqa: E402

# (name, (heater widths per basis function (offset, drive slope), coupler width)) of the drive-dependent family;
# the slope width 0.1 spreads the realized phase by 0.31 rad at the mid drive pi, the offset prior's width.
DRIVE_FAMILIES: tuple[tuple[str, tuple[Any, ...]], ...] = (("static_heater_0.3_drive_slope_0.1", ((0.3, 0.1), None)),)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def left_out_rows(
    data: dict[str, Any], light: np.ndarray, dlight: np.ndarray, left_out: int
) -> list[tuple[str, float, float, float, np.ndarray]]:
    """(readout, observed, predicted, counting variance, gradient over the free offsets) of each scored readout the
    left-out configuration serves. The statistic (E0 - E3) / sum_m E_m of the expected block counts E has the
    gradient ((dE0 - dE3) - z dS) / S, with dE_m = N_s (1 - b_s / N_s) dlight_m of each setting s."""
    settings = data["record"]["manifest"]["settings"]
    total = data["block"].sum(axis=1)
    share = (total - data["background"].sum(axis=1)) / total
    expected = models.setting_probabilities(data, light) * total[:, None]
    out = []
    for readout in models.SCORED:
        chosen = [
            i
            for i in np.flatnonzero(data["configuration"] == left_out)
            if settings[i]["readout"] == readout and settings[i]["block"] != "mutation"
        ]
        if not chosen:
            continue
        z, variance = geometry.statistic(data["block"][chosen].sum(axis=0), readout)
        counts = expected[chosen].sum(axis=0)
        model = geometry.statistic(counts, readout)[0]
        d_counts = sum(total[i] * share[i] * dlight[left_out] for i in chosen)
        s = float(counts.sum())
        gradient = ((d_counts[0] - d_counts[3]) - float(model) * d_counts.sum(axis=0)) / s
        out.append((readout, float(z), float(model), float(variance), np.asarray(gradient)))
    return out


def configuration_fold(item: tuple[str, tuple[Any, ...], dict[str, Any], int]) -> dict[str, Any]:
    """One family's fit on job-00 without one configuration, from the zero start, scored on that configuration."""
    family, taus, data, left_out = item
    widths = models.prior_widths(data, *taus)
    free = widths > 0
    training = models.without_configuration(data, left_out)
    offsets, hessian = models.static_mode(training, widths[free], free)
    covariance = np.linalg.inv(hessian)
    light, dlight = models.static_light(data, offsets, free)
    rows = []
    for readout, z, model, variance, gradient in left_out_rows(data, light, dlight, left_out):
        prediction = float(gradient @ covariance @ gradient)
        rows.append(
            {
                "readout": readout,
                "configuration": list(data["keys"][left_out]),
                "observed": z,
                "predicted": model,
                "counting_variance": variance,
                "prediction_variance": prediction,
                "counting_residual": (z - model) / variance**0.5,
                "standardized_residual": (z - model) / (variance + prediction) ** 0.5,
            }
        )
    return {
        "family": family,
        "left_out": left_out,
        "training_objective": models.static_objective(training, widths[free], free, offsets)[0],
        "lowest_hessian_eigenvalue": float(np.linalg.eigvalsh(hessian).min()),
        "rows": rows,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per readout, the descriptive sums of squared residuals and the median prediction-to-counting variance."""
    out = {}
    for readout in models.SCORED:
        chosen = [row for row in rows if row["readout"] == readout]
        ratios = sorted(row["prediction_variance"] / row["counting_variance"] for row in chosen)
        out[readout] = {
            "configurations": len(chosen),
            "counting_sum": sum(row["counting_residual"] ** 2 for row in chosen),
            "standardized_sum": sum(row["standardized_residual"] ** 2 for row in chosen),
            "median_variance_ratio": float(np.median(ratios)) if ratios else None,
        }
    return out


def nominal_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    """The returned mesh's rows: no fitted parameter, so the prediction variance is zero."""
    light = models.family_probabilities(data, "nominal", np.zeros(0))
    rows = []
    for k in range(len(data["keys"])):
        for readout, z, model, variance in models.left_out_statistics(data, light, k):
            rows.append(
                {
                    "readout": readout,
                    "configuration": list(data["keys"][k]),
                    "observed": z,
                    "predicted": model,
                    "counting_variance": variance,
                    "prediction_variance": 0.0,
                    "counting_residual": (z - model) / variance**0.5,
                    "standardized_residual": (z - model) / variance**0.5,
                }
            )
    return rows


def build(a_dir: Path, drive: bool) -> dict[str, Any]:
    a = models.job_data(a_dir)
    require(a["record"]["manifest"]["job"] == "job-00", "the fit run is not job-00")
    count = len(a["keys"])
    if drive:
        a = {**a, "heater_basis": np.stack([np.ones_like(a["phases"]), a["phases"] % (2 * np.pi)], axis=-1)}
    specs = DRIVE_FAMILIES if drive else tuple((name, tuple(taus)) for name, *taus in models.STATIC_FAMILIES)
    folds = ordered_map(
        configuration_fold,
        [(family, taus, a, k) for family, taus in specs for k in range(count)],
        min_items=1,
    )
    families = [{"family": "nominal", "folds": [], "summary": summarize(nominal_rows(a))}]
    for index, (family, _) in enumerate(specs):
        chosen = folds[index * count : (index + 1) * count]
        rows = [row for fold in chosen for row in fold["rows"]]
        families.append({"family": family, "folds": chosen, "summary": summarize(rows)})
    return {
        "schema": "ascella-configuration-holdout-v1",
        "run": a_dir.relative_to(ROOT).as_posix(),
        "configurations": count,
        "start": "zero, training configurations only",
        "families": families,
    }


def emit(record: dict[str, Any], out: Path, check: bool) -> None:
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if not check:
        require(
            not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed record"
        )
        out.write_text(text, encoding="utf-8")
        return
    fresh, retained = json.loads(text), repeat.load(out)
    name = out.relative_to(ROOT).as_posix()
    close(
        {k: v for k, v in fresh.items() if k != "families"},
        {k: v for k, v in retained.items() if k != "families"},
        name,
    )
    require(len(fresh["families"]) == len(retained["families"]), f"{name}: the family lists differ")
    for index, (row, kept) in enumerate(zip(fresh["families"], retained["families"], strict=True)):
        where = f"{name}.families[{index}]"
        (close if row["family"] in models.UNFITTED else models.replay)(row, kept, where)


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    drive = args[-1:] == ["--drive"]
    args = args[:-1] if drive else args
    if len(args) != 2:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    emit(build(Path(args[0]).resolve(), drive), Path(args[1]).resolve(), check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
