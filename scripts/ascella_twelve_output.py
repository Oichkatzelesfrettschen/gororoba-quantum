"""Twelve-output likelihood of the Ascella runs and the chip-stage families it scores.

docs/state/plans/ascella-mesh-response-decomposition.json fixes the exploration protocol. Every iteration's twelve
counts n_m are multinomial with probabilities pi_m = (1 - w) L_m + w d_m: L is the model's light over all twelve
outputs, d the catalogue dark profile over all twelve modes, and w the iteration's background weight. The
log-likelihood is concave in w, so `profile_background` maximizes it per iteration by bisection on its derivative;
light that leaves the logical block is scored where a block-conditioned likelihood would discard it.

The families factor the chip as O M I: an output stage O = exp(i H) after the mesh, H Hermitian with complex
couplings beta_m between output waveguides m and m + 1, acts on the target column M e_s that every compilation shares
and so moves every mesh alike; an input stage, the coherent admixture e_s + sum_k alpha_k e_k into the other input
waveguides, reaches the outputs through each mesh's unconstrained columns and so moves each mesh differently.

- nominal: O = I, alpha = 0;
- output_stage: the eleven couplings beta under N(0, PRIOR_WIDTH^2) on each real component;
- input_stage: the eleven amplitudes alpha under the same prior;
- output_and_input_stage: both.

Each family is fitted on job-00 alone at the posterior mode and scored on job-02's exploration meshes
(scripts/ascella_mesh_decomposition.py split): every mesh's block fractions of modes 0, 1 and 2, with the
background weight profiled on that iteration, against the observed fractions in one quadratic form over the
multinomial covariance plus G C G^T, G the fractions' gradient and C the inverse posterior Hessian. At or above the
chi-square 0.999 quantile on the coordinate count it reads shortfall; below the 0.97 quantile with median
prediction-to-counting variance ratio at most 1 it reads kept.

Usage:
  "$PYTHON" scripts/ascella_twelve_output.py JOB_00 JOB_02 SPLIT OUT [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import linalg, stats
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_physical_models as models  # noqa: E402

from parallel import ordered_map  # noqa: E402

MODES = models.MODES
COORDINATES = (0, 1, 2)
PRIOR_WIDTH = 0.1
BISECTION_STEPS = 60
LIGHT_FLOOR = 1e-15
GRADIENT_STEP = 1e-6
HESSIAN_STEP = 1e-4
FIT_TOLERANCE = 1e-10
FIT_ITERATIONS = 5000
SHORTFALL_QUANTILE = 0.999
KEPT_QUANTILE = 0.97
FAMILIES: dict[str, tuple[bool, bool]] = {
    "nominal": (False, False),
    "output_stage": (True, False),
    "input_stage": (False, True),
    "output_and_input_stage": (True, True),
}


class InputColumn:
    """Every configuration's output amplitudes for a photon entering one input mode."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.couplers, self.arch, self.phases = data["couplers"], data["arch"], data["phases"]

    def __call__(self, mode: int) -> np.ndarray:
        count = len(self.phases)
        column: np.ndarray = models.pure_amplitudes(self.couplers, self.arch, self.phases, np.full(count, mode))[0]
        return column


def unitaries(data: dict[str, Any]) -> np.ndarray:
    """Every configuration's full mesh unitary (configurations x output x input), one input mode per pool item."""
    columns = ordered_map(InputColumn(data), list(range(MODES)), min_items=1)
    out: np.ndarray = np.stack(columns, axis=2)
    return out


def output_stage(beta: np.ndarray) -> np.ndarray:
    """exp(i H), H Hermitian with H[m, m + 1] = beta_m."""
    hamiltonian = np.zeros((MODES, MODES), dtype=complex)
    index = np.arange(MODES - 1)
    hamiltonian[index, index + 1] = beta
    hamiltonian[index + 1, index] = np.conj(beta)
    out: np.ndarray = linalg.expm(1j * hamiltonian)
    return out


def light(family: str, unitary: np.ndarray, sources: np.ndarray, params: np.ndarray) -> np.ndarray:
    """Model light over the twelve outputs, normalized to one detected photon (configurations x 12)."""
    has_output, has_input = FAMILIES[family]
    vector = np.zeros((len(sources), MODES), dtype=complex)
    vector[np.arange(len(sources)), sources] = 1
    complexes = params[0::2] + 1j * params[1::2]
    cursor = 0
    stage = np.eye(MODES, dtype=complex)
    if has_output:
        stage = output_stage(complexes[: MODES - 1])
        cursor = MODES - 1
    if has_input:
        alpha = complexes[cursor : cursor + MODES - 1]
        for row, source in enumerate(sources):
            others = [k for k in range(MODES) if k != source]
            vector[row, others] += alpha
    amplitude = np.einsum("mn,cnk,ck->cm", stage, unitary, vector)
    intensity = np.abs(amplitude) ** 2
    out: np.ndarray = intensity / intensity.sum(axis=1, keepdims=True)
    return out


def parameter_count(family: str) -> int:
    has_output, has_input = FAMILIES[family]
    return 2 * (MODES - 1) * (int(has_output) + int(has_input))


def profile_background(counts: np.ndarray, model: np.ndarray, dark: np.ndarray) -> np.ndarray:
    """Per iteration, the background weight w in [0, 1] that maximizes sum_m n_m log((1 - w) L_m + w d_m).

    The derivative sum_m n_m (d_m - L_m) / pi_m falls monotonically in w, so bisection on its sign converges."""
    model = np.maximum(model, LIGHT_FLOOR)

    def slope(w: np.ndarray) -> np.ndarray:
        pi = (1 - w)[:, None] * model + w[:, None] * dark[None, :]
        out: np.ndarray = (counts * (dark[None, :] - model) / pi).sum(axis=1)
        return out

    low, high = np.zeros(len(counts)), np.ones(len(counts))
    for _ in range(BISECTION_STEPS):
        middle = (low + high) / 2
        rising = slope(middle) > 0
        low, high = np.where(rising, middle, low), np.where(rising, high, middle)
    w = (low + high) / 2
    w = np.where(slope(np.zeros(len(counts))) <= 0, 0.0, w)
    return np.where(slope(np.ones(len(counts))) >= 0, 1.0, w)


def mixture(counts: np.ndarray, model: np.ndarray, dark: np.ndarray) -> np.ndarray:
    w = profile_background(counts, model, dark)
    out: np.ndarray = (1 - w)[:, None] * np.maximum(model, LIGHT_FLOOR) + w[:, None] * dark[None, :]
    return out


class Objective:
    """Negative log posterior of a family on one run, the background weights profiled."""

    def __init__(self, family: str, data: dict[str, Any], unitary: np.ndarray) -> None:
        self.family, self.data, self.unitary = family, data, unitary
        self.counts = data["record"]["counts"]
        dark = data["record"]["dark"]
        self.dark = dark / dark.sum()

    def __call__(self, params: np.ndarray) -> float:
        model = light(self.family, self.unitary, self.data["sources"], params)[self.data["configuration"]]
        pi = mixture(self.counts, model, self.dark)
        prior = float((params * params).sum()) / (2 * PRIOR_WIDTH * PRIOR_WIDTH)
        return -float((self.counts * np.log(pi)).sum()) + prior

    def gradient(self, params: np.ndarray) -> np.ndarray:
        out = np.zeros(len(params))
        for index in range(len(params)):
            up, down = params.copy(), params.copy()
            up[index] += GRADIENT_STEP
            down[index] -= GRADIENT_STEP
            out[index] = (self(up) - self(down)) / (2 * GRADIENT_STEP)
        return out


class HessianColumn:
    def __init__(self, objective: Objective, params: np.ndarray) -> None:
        self.objective, self.params = objective, params

    def __call__(self, index: int) -> np.ndarray:
        up, down = self.params.copy(), self.params.copy()
        up[index] += HESSIAN_STEP
        down[index] -= HESSIAN_STEP
        column: np.ndarray = (self.objective.gradient(up) - self.objective.gradient(down)) / (2 * HESSIAN_STEP)
        return column


def block_fractions(family: str, data: dict[str, Any], unitary: np.ndarray, params: np.ndarray) -> np.ndarray:
    """Every iteration's model block fractions (iterations x 4), its background weight profiled."""
    dark = data["record"]["dark"] / data["record"]["dark"].sum()
    model = light(family, unitary, data["sources"], params)[data["configuration"]]
    pi = mixture(data["record"]["counts"], model, dark)[:, : models.LOGICAL]
    out: np.ndarray = pi / pi.sum(axis=1, keepdims=True)
    return out


def score(family: str, data: dict[str, Any], unitary: np.ndarray, params: np.ndarray, covariance: np.ndarray) -> dict:
    counts = data["record"]["counts"][:, : models.LOGICAL]
    total = counts.sum(axis=1)
    observed = counts / total[:, None]
    model = block_fractions(family, data, unitary, params)
    coordinates = list(COORDINATES)
    residual = (observed - model)[:, coordinates].ravel()
    blocks = [
        (np.diag(m[coordinates]) - np.outer(m[coordinates], m[coordinates])) / n
        for m, n in zip(model, total, strict=True)
    ]
    counting = linalg.block_diag(*blocks)
    gradient = np.zeros((len(residual), len(params)))
    for index in range(len(params)):
        up, down = params.copy(), params.copy()
        up[index] += GRADIENT_STEP
        down[index] -= GRADIENT_STEP
        change = block_fractions(family, data, unitary, up) - block_fractions(family, data, unitary, down)
        gradient[:, index] = (change[:, coordinates] / (2 * GRADIENT_STEP)).ravel()
    prediction = gradient @ covariance @ gradient.T
    statistic = float(residual @ np.linalg.solve(counting + prediction, residual))
    ratios = np.diag(prediction) / np.diag(counting)
    dof = len(residual)
    shortfall = float(stats.chi2.ppf(SHORTFALL_QUANTILE, dof))
    kept = float(stats.chi2.ppf(KEPT_QUANTILE, dof))
    ratio = float(np.median(ratios)) if len(params) else 0.0
    if statistic >= shortfall:
        verdict = "shortfall"
    elif statistic < kept and ratio <= 1:
        verdict = "kept"
    else:
        verdict = "between the thresholds"
    x_model = model[:, 0] - model[:, 3]
    x_observed = observed[:, 0] - observed[:, 3]
    return {
        "coordinates": dof,
        "quadratic_form": statistic,
        "median_variance_ratio": ratio,
        "shortfall_threshold": shortfall,
        "kept_threshold": kept,
        "reading": verdict,
        "x_correlation": float(np.corrcoef(x_model, x_observed)[0, 1]) if np.std(x_model) > 0 else None,
        "x_model_mean": float(x_model.mean()),
        "x_observed_mean": float(x_observed.mean()),
        "mode_2_model_mean": float(model[:, 2].mean()),
        "mode_2_observed_mean": float(observed[:, 2].mean()),
    }


def fit(item: tuple[str, dict[str, Any], dict[str, Any], np.ndarray, np.ndarray]) -> dict[str, Any]:
    family, train, test, train_unitary, test_unitary = item
    objective = Objective(family, train, train_unitary)
    count = parameter_count(family)
    params = np.zeros(count)
    if count:
        result = minimize(
            objective,
            params,
            jac=objective.gradient,
            method="L-BFGS-B",
            options={"ftol": FIT_TOLERANCE, "gtol": 1e-6, "maxiter": FIT_ITERATIONS},
        )
        models.require(bool(result.success), f"{family}: the fit did not converge: {result.message}")
        params = np.asarray(result.x)
        columns = ordered_map(HessianColumn(objective, params), list(range(count)), min_items=1)
        hessian = np.stack(columns, axis=1)
        hessian = (hessian + hessian.T) / 2
        lowest = float(np.linalg.eigvalsh(hessian).min())
        models.require(lowest > 0, f"{family}: the mode's Hessian is not positive definite ({lowest})")
        covariance = np.linalg.inv(hessian)
    else:
        lowest, covariance = 0.0, np.zeros((0, 0))
    complexes = params[0::2] + 1j * params[1::2]
    train_light = light(family, train_unitary, train["sources"], params)
    return {
        "family": family,
        "parameters": count,
        "job_00_negative_log_posterior": objective(params),
        "lowest_hessian_eigenvalue": lowest,
        "magnitudes": [float(abs(z)) for z in complexes],
        "job_00_leak_median": float(np.median(1 - train_light[:, [0, 1, 3]].sum(axis=1))),
        "exploration": score(family, test, test_unitary, params, covariance),
    }


def build(a_dir: Path, c_dir: Path, split_path: Path) -> dict[str, Any]:
    a, c = models.job_data(a_dir), models.job_data(c_dir)
    models.require(a["record"]["manifest"]["job"] == "job-00" and c["record"]["manifest"]["job"] == "job-02", "jobs")
    chosen = json.loads(split_path.read_text(encoding="utf-8"))
    seeds = np.array([int(s["compilation_seed"]) for s in c["record"]["manifest"]["settings"]])
    explore = reading.subset(c, np.flatnonzero(np.isin(seeds, chosen["exploration_seeds"])))
    explore["record"] = {
        **explore["record"],
        "counts": c["record"]["counts"][np.isin(seeds, chosen["exploration_seeds"])],
    }
    train_unitary, test_unitary = unitaries(a), unitaries(explore)
    rows = ordered_map(fit, [(family, a, explore, train_unitary, test_unitary) for family in FAMILIES], min_items=1)
    nominal = rows[0]["job_00_negative_log_posterior"]
    for row in rows:
        row["job_00_gain_over_nominal"] = nominal - row["job_00_negative_log_posterior"]
    return {
        "schema": "ascella-twelve-output-v1",
        "plan": "docs/state/plans/ascella-mesh-response-decomposition.json",
        "runs": [a_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "split": split_path.relative_to(ROOT).as_posix(),
        "exploration_meshes": len(explore["keys"]),
        "prior_width": PRIOR_WIDTH,
        "families": rows,
        "kept": [row["family"] for row in rows if row["exploration"]["reading"] == "kept"],
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 4:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve(), Path(args[1]).resolve(), Path(args[2]).resolve())
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
