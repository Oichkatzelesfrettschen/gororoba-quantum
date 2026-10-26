"""Heater-coupling error families of the Ascella mesh, fitted on job-00 alone and scored on job-02's served meshes.

docs/state/plans/ascella-heater-coupling-families.json fixes the families, priors and reading before any of them
meets job-02. Each family is fitted on job-00 from the zero start and predicts the pooled X statistic of every
distinct mesh job-02's nonzero compilation seeds served (scripts/ascella_compilation_reading.py new_meshes). All
meshes share the fitted parameters, so mesh_score takes the residuals' joint quadratic form in diag(v) + G C G^T:
at or above the chi-square 0.999 quantile on the mesh count it reads shortfall, below the 0.97 quantile with median
prediction-to-counting variance ratio at most 1 it reads predicted.

- uniform_crosstalk and uniform_coupler_offset: the low-dimensional thermal_crosstalk and coupler_offset families of
  scripts/ascella_physical_models.py, each with dephasing, covariance the inverse Fisher information;
- static coupler offsets (tau 0.1), and heater offsets (tau 0.3) with coupler offsets (tau 0.1), at the posterior
  mode with the posterior Hessian;
- crosstalk kernel: heater h's phase gains c_d sum_j phi_j over the heaters j that sit d = 0, 1, 2 modes from h within
  KERNEL_COLUMNS layout columns (j != h), phi_j the returned phase in [0, 2 pi), c_d under N(0, 0.01^2);
- drive loss: the mode under heater h transmits intensity e^{-gamma phi_h}, one gamma under N(0, 0.05^2);
- the kernel and the drive loss each again with the heater and coupler offsets.

The returned phase stands for the heater's drive power because the passive offset is absent from the returned
circuit, and the layout's (mode, column) distance stands for the physical distance between heaters.

Beside each reading the record states, descriptively, the predicted X spread over the meshes and its correlation
with the observed statistics, and the observed spread with its counting share removed. For the kernel and loss
families it also reports the training-only folds of scripts/ascella_configuration_holdout.py fitted on job-00 plus
job-02's meshes, which read identification and decide nothing.

Usage:
  "$PYTHON" scripts/ascella_heater_coupling.py JOB_00 JOB_02 OUT [--check]
"""

from __future__ import annotations

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
import ascella_configuration_holdout as holdout  # noqa: E402
import ascella_drive_response as drive  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import qd_belenos_mesh as mesh  # noqa: E402

from parallel import ordered_map  # noqa: E402

KERNEL_DISTANCES = (0, 1, 2)
KERNEL_COLUMNS = 2
# (record name, family of scripts/ascella_physical_models.py FAMILIES).
LOW_FAMILIES: tuple[tuple[str, str], ...] = (
    ("uniform_crosstalk", "thermal_crosstalk"),
    ("uniform_coupler_offset", "coupler_offset"),
)
# (record name, heater tau, coupler tau, kernel tau, loss tau); a tau of None leaves that kind out.
STATIC_FAMILIES: tuple[tuple[str, float | None, float | None, float | None, float | None], ...] = (
    ("static_coupler_offsets_tau_0.1", None, 0.1, None, None),
    ("static_heater_0.3_coupler_0.1_offsets", 0.3, 0.1, None, None),
    ("crosstalk_kernel_tau_0.01", None, None, 0.01, None),
    ("crosstalk_kernel_with_offsets", 0.3, 0.1, 0.01, None),
    ("drive_loss_tau_0.05", None, None, None, 0.05),
    ("drive_loss_with_offsets", 0.3, 0.1, None, 0.05),
)
IDENTIFIED = (
    "crosstalk_kernel_tau_0.01",
    "crosstalk_kernel_with_offsets",
    "drive_loss_tau_0.05",
    "drive_loss_with_offsets",
)


def kernel_basis(arch: list[Any], phases: np.ndarray) -> np.ndarray:
    """(configurations x heaters x distances) sums of the returned phases of each heater's kernel neighbors."""
    column = mesh.column_index(arch)
    where = [(arch[j][1], column[j]) for j in mesh.phase_slots(arch)]
    drive_phase = phases % (2 * math.pi)
    out = np.zeros((*phases.shape, len(KERNEL_DISTANCES)))
    for k, distance in enumerate(KERNEL_DISTANCES):
        adjacency = np.array(
            [
                [
                    b != a and abs(mb - ma) == distance and abs(cb - ca) <= KERNEL_COLUMNS
                    for b, (mb, cb) in enumerate(where)
                ]
                for a, (ma, ca) in enumerate(where)
            ],
            dtype=float,
        )
        out[:, :, k] = drive_phase @ adjacency.T
    return out


def with_coupling(data: dict[str, Any], kernel: bool, loss: bool) -> dict[str, Any]:
    out = dict(data)
    if kernel:
        out["shared_basis"] = kernel_basis(data["arch"], data["phases"])
    if loss:
        out["loss_drive"] = data["phases"] % (2 * math.pi)
    return out


def fit_low(item: tuple[str, str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """A low-dimensional family's job-00 maximum-likelihood fit scored on the perturbed meshes."""
    name, family, a, perturbed = item
    values = models.fit_parameters(a, family)
    fisher = models.fisher(a, models.finite_jacobian(a, family, values), models.family_probabilities(a, family, values))
    covariance = np.linalg.inv(fisher)
    light = models.family_probabilities(perturbed, family, values)
    out = reading.mesh_score(name, perturbed, light, models.finite_jacobian(perturbed, family, values), covariance)
    out["parameters"] = {
        parameter: {"value": float(values[i]), "se": float(math.sqrt(covariance[i, i]))}
        for i, (parameter, _, _) in enumerate(models.FAMILIES[family])
    }
    return out


def static_spec(name: str) -> tuple[tuple[Any, ...], bool, bool]:
    _, heater, coupler, kernel, loss = next(f for f in STATIC_FAMILIES if f[0] == name)
    return (heater, coupler, kernel, loss), kernel is not None, loss is not None


def fit_static(item: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    """A static family's job-00 posterior mode scored on the perturbed meshes, with its shared coefficients."""
    name, a, perturbed = item
    taus, kernel, loss = static_spec(name)
    train = with_coupling(a, kernel, loss)
    widths = models.prior_widths(train, *taus)
    free = widths > 0
    offsets, hessian = models.static_mode(train, widths[free], free)
    covariance = np.linalg.inv(hessian)
    light, dlight = models.static_light(with_coupling(perturbed, kernel, loss), offsets, free)
    out = reading.mesh_score(name, perturbed, light, dlight, covariance)
    full = np.zeros(len(free))
    full[free] = offsets
    se = np.zeros(len(free))
    se[free] = np.sqrt(np.diag(covariance))
    heaters, coupling = models.heater_parameters(train), models.coupling_parameters(train)
    names = [f"kernel_distance_{d}" for d in KERNEL_DISTANCES] if kernel else []
    names += ["drive_loss_gamma"] if loss else []
    out["parameters"] = {
        parameter: {"value": float(full[heaters + i]), "se": float(se[heaters + i])}
        for i, parameter in enumerate(names)
    }
    for kind, block in (("heater", slice(0, heaters)), ("coupler", slice(heaters + coupling, len(free)))):
        if free[block].any():
            values = full[block][free[block]]
            out[f"{kind}_offset_rms"] = float(math.sqrt(float((values * values).mean())))
    out["training_objective"] = models.static_objective(train, widths[free], free, offsets)[0]
    return out


def identification_fold(item: tuple[str, dict[str, Any], int]) -> dict[str, Any]:
    name, both, left_out = item
    taus, kernel, loss = static_spec(name)
    return holdout.configuration_fold((name, taus, with_coupling(both, kernel, loss), left_out))


def spread(rows: list[dict[str, Any]]) -> dict[str, float]:
    """Descriptive: the noise-free predicted X standard deviation over the meshes and its correlation with the
    observed statistics; neither enters the reading."""
    predicted = np.array([row["predicted"] for row in rows])
    observed = np.array([row["observed"] for row in rows])
    return {"predicted_sd": float(predicted.std()), "correlation": float(np.corrcoef(predicted, observed)[0, 1])}


def build(a_dir: Path, c_dir: Path) -> dict[str, Any]:
    a, c = models.job_data(a_dir), models.job_data(c_dir)
    models.require(a["record"]["manifest"]["job"] == "job-00", "the fit run is not job-00")
    models.require(c["record"]["manifest"]["job"] == "job-02", "the scored run is not job-02")
    layout = [(kind, mode) for kind, mode, _ in a["arch"]] == [(kind, mode) for kind, mode, _ in c["arch"]]
    models.require(layout and np.array_equal(a["couplers"], c["couplers"]), "the mesh layouts or couplers differ")
    meshes = reading.new_meshes(a, c, reading.anchors_of(c))
    models.require(len(meshes) > 1, "job-02 served fewer than two new meshes")
    perturbed = reading.subset(c, np.flatnonzero([int(m) in meshes for m in c["configuration"]]))
    low = ordered_map(fit_low, [(name, family, a, perturbed) for name, family in LOW_FAMILIES], min_items=1)
    static = ordered_map(fit_static, [(f[0], a, perturbed) for f in STATIC_FAMILIES], min_items=1)
    both = reading.combined(a, perturbed)
    scored = models.scored_configurations(a)
    folds = ordered_map(identification_fold, [(name, both, j) for name in IDENTIFIED for j in scored], min_items=1)
    identification = []
    for index, name in enumerate(IDENTIFIED):
        chosen = folds[index * len(scored) : (index + 1) * len(scored)]
        summary = holdout.summarize([entry for fold in chosen for entry in fold["rows"]])
        identification.append({"family": name, "summary": summary, "reading": drive.reading(summary), "folds": chosen})
    families = [*low, *static]
    for row in families:
        row["spread"] = spread(row["rows"])
    observed = np.array([r["observed"] for r in families[0]["rows"]])
    counting = float(np.mean([r["counting_variance"] for r in families[0]["rows"]]))
    return {
        "schema": "ascella-heater-coupling-reading-v1",
        "plan": "docs/state/plans/ascella-heater-coupling-families.json",
        "runs": [a_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "training": "job-00",
        "meshes": len(meshes),
        "kernel": {"distances": list(KERNEL_DISTANCES), "columns": KERNEL_COLUMNS},
        "observed_spread": {
            "sd": float(observed.std()),
            "mean_counting_variance": counting,
            "compilation_sd": float(math.sqrt(max(float(observed.var()) - counting, 0.0))),
        },
        "families": families,
        "predicting_families": [row["family"] for row in families if row["reading"] == "predicted"],
        "identification": identification,
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve(), Path(args[1]).resolve())
    out = Path(args[2]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
