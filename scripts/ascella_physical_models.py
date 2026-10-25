"""Restricted physical models of the Ascella analyzer response, fitted on job-00 and scored on job-01.

docs/design/ascella-signed-coherence-conformance.md#restricted-physical-models-of-the-analyzer-response
preregisters the families, the fit, the held-out score and the decision. Each family perturbs every setting's
returned 12-mode mesh (fixed characterized couplers, 126 heater phases) by one shared parameter set:

- nominal: the returned circuit;
- dephasing: independent Gaussian heater phase noise of variance s, the exact density-matrix channel;
- heater gain: every returned phase in [0, 2 pi) scales to (1 + kappa) phi, with dephasing;
- thermal crosstalk: every phase gains c times the sum of its mesh neighbors' phases, with dephasing;
- coupler offset: every coupler angle shifts by delta, with dephasing;
- coupler noise: independent Gaussian coupler-angle noise of variance t, with dephasing;
- static heater offsets: one offset per heater, maximum a posteriori under a N(0, tau^2) prior, pure state;
- supplementary families, fitted after the preregistered table and deciding nothing: relative detection
  efficiencies of modes 1..3 against mode 0, with dephasing; one static angle offset per coupler under a
  N(0, 0.1^2) prior; and heater offsets (tau 0.3) with coupler offsets (tau 0.1) together.

Variances rather than widths are the fitted noise parameters, because a width's likelihood gradient vanishes at
zero and the zero-perturbation start would never move. The block-conditioned four-mode multinomial of every
setting carries a fixed in-block background: the setting's outside-block count shared over modes 0..3 by the
plan-time catalogue dark rates, B_m = outside * d_m / sum_{k >= 4} d_k. Every family carries the same term, so it
decides nothing between them.

Leave-one-configuration-out, fitted after the preregistered table and deciding nothing, refits each static
family on job-00 without one configuration and scores that configuration's X and Y statistics against the
prediction in their multinomial variances alone. Each of the 30 configurations is left out in turn; the 19 that
serve the X or Y readout (one serves both) are scored, and the nominal mesh gives the reference. Each fold starts
from the full-data mode, so this score is descriptive; scripts/ascella_configuration_holdout.py refits the folds
from the training configurations alone and scores them in the fitted-prediction variance.

The held-out statistic of each readout is r^T (diag(v) + J C J^T)^{-1} r over job-01's pooled configuration
statistics, with v job-01's multinomial variances, C the inverse Fisher information of the job-00 fit (plus the
prior precision for the static family) and J the prediction Jacobian.

Usage:
  "$PYTHON" scripts/ascella_physical_models.py A B OUT [--check]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_coherence_analysis as analysis  # noqa: E402
import ascella_coherence_repeat as repeat  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402
import qd_belenos_mesh as mesh  # noqa: E402
from bdsc_certificate import close  # noqa: E402
from photonic_compilation_audit import _elements  # noqa: E402

from parallel import ordered_map  # noqa: E402

LOGICAL = repeat.LOGICAL
MODES = analysis.MODES
READOUTS = ("x", "y", "direct")
SCORED = ("x", "y")
DECISION_P = 0.01
RELATION = "X0 + Xc2"
# Parameter order and bounds of each low-dimensional family.
FAMILIES: dict[str, tuple[tuple[str, float, float], ...]] = {
    "nominal": (),
    "dephasing": (("phase_variance", 0.0, 1.0),),
    "heater_gain": (("phase_variance", 0.0, 1.0), ("kappa", -0.2, 0.2)),
    "thermal_crosstalk": (("phase_variance", 0.0, 1.0), ("crosstalk", -0.1, 0.1)),
    "coupler_offset": (("phase_variance", 0.0, 1.0), ("delta", -0.2, 0.2)),
    "coupler_noise": (("phase_variance", 0.0, 1.0), ("coupler_variance", 0.0, 0.25)),
    "detector_efficiency": (
        ("phase_variance", 0.0, 1.0),
        ("log_efficiency_1", -0.5, 0.5),
        ("log_efficiency_2", -0.5, 0.5),
        ("log_efficiency_3", -0.5, 0.5),
    ),
}
# Families fitted beside the preregistered table; their verdicts are reported and decide nothing.
# Families with no fitted parameter, whose numbers no optimizer touches.
UNFITTED = ("nominal",)
SUPPLEMENTARY = ("detector_efficiency", "static_coupler_offsets_tau_0.1", "static_heater_0.3_coupler_0.1_offsets")
# Static families: (name, heater prior width, coupler prior width); a width of None leaves that kind at zero.
STATIC_FAMILIES: tuple[tuple[str, float | None, float | None], ...] = (
    ("static_heater_offsets_tau_0.1", 0.1, None),
    ("static_heater_offsets_tau_0.3", 0.3, None),
    ("static_coupler_offsets_tau_0.1", None, 0.1),
    ("static_heater_0.3_coupler_0.1_offsets", 0.3, 0.1),
)
STEP = 1e-5
# Optimizer endpoints round differently under each BLAS build: a fitted family's float replays within the relative
# bound plus the absolute one, which covers offsets near zero. A tail p-value moves by about its statistic's
# change, so the relative bound sits above the statistics' own. The nominal family, the observed relation, keys,
# counts and verdicts replay at the certificate tolerance.
FIT_REPLAY_RELATIVE = 1e-3
FIT_REPLAY_ABSOLUTE = 1e-8
# A model probability never falls below this floor, so a count in a cell the mesh leaves dark stays finite.
PROBABILITY_FLOOR = 1e-9
FIT_TOLERANCE = 1e-12
FIT_ITERATIONS = 20000
STATIC_GRADIENT_TOLERANCE = 1e-8
REFINE_STEPS = 50
REFINE_TOLERANCE = 1e-8
REFINE_DAMPING = 1e-6
HESSIAN_STEP = 1e-6
ROUNDING = 64 * float(np.finfo(float).eps)
LINE_SEARCH_FLOOR = 1e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def chi_square(statistic: float, dof: int) -> dict[str, float]:
    return {"statistic": float(statistic), "dof": int(dof), "p": float(chi2.sf(statistic, dof))}


def channel(
    couplers: np.ndarray,
    arch: list[Any],
    phases: np.ndarray,
    sources: np.ndarray,
    phase_variance: float,
    coupler_variance: float,
) -> np.ndarray:
    """Detection probabilities (C x 12) of C one-photon meshes under independent Gaussian heater and coupler noise.

    The batch form of qd_belenos_mesh.channel on 12 modes: a phase shifter on mode q with noise variance s
    multiplies every coherence rho_qk (k != q) by e^{i phi} e^{-s/2}; a coupler B = c I + i s X with angle noise
    variance t maps the pair block M to E[c^2] M + E[s^2] X M X + i E[cs] (X M - M X) and the pair-to-rest
    blocks by E[B], with E[c^2] = (1 + cos(theta) e^{-t/2}) / 2, E[cs] = sin(theta) e^{-t/2} / 2 and
    E[c] = cos(theta / 2) e^{-t/8}."""
    count = len(sources)
    rho = np.zeros((count, MODES, MODES), dtype=complex)
    rho[np.arange(count), sources, sources] = 1
    damp = math.exp(-phase_variance / 2)
    fade, fade8 = math.exp(-coupler_variance / 2), math.exp(-coupler_variance / 8)
    flip = np.array([[0, 1], [1, 0]], dtype=complex)
    ib = it = 0
    for kind, m, _ in arch:
        if kind == "bs":
            theta = float(couplers[ib])
            ib += 1
            ec2, es2 = (1 + math.cos(theta) * fade) / 2, (1 - math.cos(theta) * fade) / 2
            ecs = math.sin(theta) * fade / 2
            c, s = math.cos(theta / 2) * fade8, math.sin(theta / 2) * fade8
            mean = np.array([[c, 1j * s], [1j * s, c]])
            rest = np.r_[0:m, m + 2 : MODES]
            rho[:, m : m + 2, rest] = np.einsum("ij,cjk->cik", mean, rho[:, m : m + 2, rest])
            rho[:, rest, m : m + 2] = np.einsum("ckj,ij->cki", rho[:, rest, m : m + 2], mean.conj())
            block = rho[:, m : m + 2, m : m + 2].copy()
            rho[:, m : m + 2, m : m + 2] = (
                ec2 * block + es2 * (flip @ block @ flip) + 1j * ecs * (flip @ block - block @ flip)
            )
        else:
            phase = np.exp(1j * phases[:, it]) * damp
            it += 1
            diagonal = rho[:, m, m].copy()
            rho[:, m, :] *= phase[:, None]
            rho[:, :, m] *= np.conj(phase)[:, None]
            rho[:, m, m] = diagonal
    return np.real(np.einsum("cii->ci", rho)).clip(0)


def job_data(directory: Path) -> dict[str, Any]:
    """Per-configuration meshes and per-setting block counts and in-block background of one run."""
    record = repeat.run_record(directory)
    record["results"] = repeat.load(directory / "results.json")
    iterations = record["results"]["iterations"]
    groups = list(geometry.configurations(record).values())
    meshes = [_elements(iterations[members[0]]["result_fields"]["computed_circuit"]) for members in groups]
    arch = meshes[0]
    for elements in meshes:
        require(len(elements) == len(arch), f"{directory.name}: the configurations differ in mesh layout")
        for (kind, m, value), (kind0, m0, value0) in zip(elements, arch, strict=True):
            require(kind == kind0 and m == m0 and m < MODES, f"{directory.name}: the mesh layouts differ")
            if kind == "bs":
                require(tuple(value) == tuple(value0), f"{directory.name}: the couplers differ between configurations")
                require(not any(value[1:]), f"{directory.name}: a coupler carries a phase term")
    sources = []
    for members in groups:
        occupation = iterations[members[0]]["result_fields"]["computed_input"]
        sources.append(occupation[len(":PCVL:BasicState:|") : -1].split(",").index("1"))
    counts = record["counts"]
    dark = record["dark"]
    share = dark[:LOGICAL] / dark[LOGICAL:].sum()
    configuration = np.empty(len(counts), dtype=int)
    for index, members in enumerate(groups):
        configuration[members] = index
    return {
        "directory": directory,
        "record": record,
        "keys": [tuple(sorted(record["manifest"]["settings"][i]["name"] for i in members)) for members in groups],
        "arch": arch,
        "couplers": np.array([value[0] for kind, _, value in arch if kind == "bs"]),
        "phases": np.array([[value for kind, _, value in elements if kind == "ps"] for elements in meshes]),
        "sources": np.array(sources),
        "configuration": configuration,
        "block": counts[:, :LOGICAL],
        "background": counts[:, LOGICAL:].sum(axis=1)[:, None] * share[None, :],
    }


def family_probabilities(data: dict[str, Any], family: str, values: np.ndarray) -> np.ndarray:
    """Block-conditioned light probabilities (configurations x 4) of a low-dimensional family at its parameters."""
    names = [name for name, _, _ in FAMILIES[family]]
    get = dict(zip(names, values, strict=True))
    phases = data["phases"] % (2 * math.pi)
    couplers = data["couplers"]
    if family == "heater_gain":
        phases = phases * (1 + get["kappa"])
    elif family == "thermal_crosstalk":
        neighbours = data.setdefault("neighbours", mesh.neighbours(data["arch"]))
        heat = np.stack([phases[:, n].sum(axis=1) for n in neighbours], axis=1)
        phases = phases + get["crosstalk"] * heat
    elif family == "coupler_offset":
        couplers = couplers + get["delta"]
    p = channel(
        couplers,
        data["arch"],
        phases,
        data["sources"],
        get.get("phase_variance", 0.0),
        get.get("coupler_variance", 0.0),
    )
    light = np.clip(p[:, :LOGICAL], PROBABILITY_FLOOR, None)
    if family == "detector_efficiency":
        light = light * np.exp([0.0, get["log_efficiency_1"], get["log_efficiency_2"], get["log_efficiency_3"]])
    return light / light.sum(axis=1, keepdims=True)


def setting_probabilities(data: dict[str, Any], light: np.ndarray) -> np.ndarray:
    """Per-setting block-conditioned probabilities: the configuration's light plus the fixed in-block background."""
    total = data["block"].sum(axis=1)
    background = data["background"]
    return ((total - background.sum(axis=1))[:, None] * light[data["configuration"]] + background) / total[:, None]


def log_likelihood(data: dict[str, Any], light: np.ndarray) -> float:
    return float((data["block"] * np.log(setting_probabilities(data, light))).sum())


def fisher(data: dict[str, Any], jacobian: np.ndarray, light: np.ndarray) -> np.ndarray:
    """Expected information sum_s N_s sum_m dpi_sm dpi_sm^T / pi_sm of the per-setting multinomials."""
    total = data["block"].sum(axis=1)
    pi = setting_probabilities(data, light)
    light_share = (total - data["background"].sum(axis=1)) / total
    dpi = light_share[:, None, None] * jacobian[data["configuration"]]
    return np.einsum("s,smi,smj->ij", total, dpi / pi[:, :, None], dpi)


def finite_jacobian(data: dict[str, Any], family: str, values: np.ndarray) -> np.ndarray:
    """d light / d parameters (configurations x 4 x k): central differences, forward ones at a lower bound."""
    out = []
    for index, (_, low, high) in enumerate(FAMILIES[family]):
        up, down = values.copy(), values.copy()
        up[index] = min(values[index] + STEP, high)
        down[index] = max(values[index] - STEP, low)
        width = up[index] - down[index]
        out.append((family_probabilities(data, family, up) - family_probabilities(data, family, down)) / width)
    if not out:
        return np.zeros((len(data["keys"]), LOGICAL, 0))
    return np.stack(out, axis=-1)


def pooled_prediction(data: dict[str, Any], light: np.ndarray, readout: str) -> dict[tuple[str, ...], float]:
    """Each configuration's pooled statistic under the model, keyed like geometry.pooled."""
    settings = data["record"]["manifest"]["settings"]
    expected = setting_probabilities(data, light) * data["block"].sum(axis=1)[:, None]
    out = {}
    for index in range(len(data["keys"])):
        chosen = [
            i
            for i in np.flatnonzero(data["configuration"] == index)
            if settings[i]["readout"] == readout and settings[i]["block"] != "mutation"
        ]
        if chosen:
            name = tuple(sorted(settings[i]["name"] for i in chosen))
            out[name] = float(geometry.statistic(expected[chosen].sum(axis=0), readout)[0])
    return out


def relation_value(data: dict[str, Any], light: np.ndarray) -> float:
    """The model's block-conditioned X0 + Xc2 under the registered estimators."""
    counts = np.zeros((len(data["block"]), MODES))
    counts[:, :LOGICAL] = setting_probabilities(data, light) * data["block"].sum(axis=1)[:, None]
    endpoints = analysis.analyze(data["record"]["manifest"], counts.tolist())["endpoints"]
    return next(row["value"] for row in geometry.gain_relations(endpoints) if row["relation"] == RELATION)


def observed_relation(data: dict[str, Any]) -> dict[str, Any]:
    counts = data["record"]["counts"].copy()
    counts[:, LOGICAL:] = 0
    endpoints = analysis.analyze(data["record"]["manifest"], counts.tolist())["endpoints"]
    return next(row for row in geometry.gain_relations(endpoints) if row["relation"] == RELATION)


def held_out(b: dict[str, Any], light: np.ndarray, jacobian: np.ndarray, covariance: np.ndarray) -> dict[str, Any]:
    """A run's pooled configuration statistics against the job-00 fit, in the full residual covariance; a zero
    covariance gives the multinomial-only statistic of job-00 against its own fit."""
    out: dict[str, Any] = {}
    record = b["record"]
    for readout in READOUTS:
        observed = geometry.pooled(record, readout)
        predicted = pooled_prediction(b, light, readout)
        keys = sorted(observed)
        require(sorted(predicted) == keys, f"{readout}: the prediction covers other configurations")
        z = np.array([observed[k][0] for k in keys])
        variance = np.array([observed[k][1] for k in keys])
        model = np.array([predicted[k] for k in keys])
        # d statistic / d parameter of each configuration by the same finite differences as the light Jacobian.
        grad = np.zeros((len(keys), covariance.shape[0]))
        for column in range(covariance.shape[0]):
            shifted = pooled_prediction(b, light + STEP * jacobian[..., column], readout)
            grad[:, column] = (np.array([shifted[k] for k in keys]) - model) / STEP
        residual = z - model
        full = np.diag(variance) + grad @ covariance @ grad.T
        settings = {s["name"]: s for s in record["manifest"]["settings"]}
        ideal = np.array([analysis.registered_ideals([settings[k[0]]])[0] for k in keys])
        out[readout] = {
            **chi_square(float(residual @ np.linalg.solve(full, residual)), len(keys)),
            "residual_correlation": float(np.corrcoef(model - ideal, z - ideal)[0, 1]),
        }
    return out


def fit_parameters(data: dict[str, Any], family: str) -> np.ndarray:
    """Maximum-likelihood parameters of a low-dimensional family from the zero-perturbation start."""
    spec = FAMILIES[family]
    if not spec:
        return np.zeros(0)
    result = minimize(
        lambda v: -log_likelihood(data, family_probabilities(data, family, v)),
        np.zeros(len(spec)),
        method="L-BFGS-B",
        bounds=[(low, high) for _, low, high in spec],
        options={"ftol": FIT_TOLERANCE, "gtol": FIT_TOLERANCE, "maxiter": FIT_ITERATIONS},
    )
    require(bool(result.success), f"{family}: the fit did not converge: {result.message}")
    return np.asarray(result.x)


def fit_family(item: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    family, a, b = item
    values = fit_parameters(a, family)
    light_a = family_probabilities(a, family, values)
    jacobian_a = finite_jacobian(a, family, values)
    covariance = np.linalg.inv(fisher(a, jacobian_a, light_a)) if len(values) else np.zeros((0, 0))
    light_b = family_probabilities(b, family, values)
    out = summarize(family, a, b, covariance, light_a, light_b, finite_jacobian(b, family, values))
    out["parameters"] = {
        name: {"value": float(values[i]), "se": float(math.sqrt(covariance[i, i]))}
        for i, (name, _, _) in enumerate(FAMILIES[family])
    }
    return out


def pure_jacobians(
    couplers: np.ndarray, arch: list[Any], phases: np.ndarray, sources: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Detection probabilities (C x 12) and their derivatives (C x 12 x (heaters + couplers)) by adjoint.

    The forward pass keeps each element's input amplitude; the backward pass carries G, the product of the
    elements after the current one, so d psi_out = G[:, :, pair] dB psi_pair for a coupler with
    dB/dtheta = (1/2) [[-sin, i cos], [i cos, -sin]](theta / 2), and G[:, :, q] i psi_q for a heater on mode q."""
    count = len(sources)
    psi = np.zeros((count, MODES), dtype=complex)
    psi[np.arange(count), sources] = 1
    before = []
    ib = it = 0
    for kind, m, _ in arch:
        if kind == "bs":
            c, s = math.cos(couplers[ib] / 2), math.sin(couplers[ib] / 2)
            before.append(psi[:, m : m + 2].copy())
            psi[:, m : m + 2] = psi[:, m : m + 2] @ np.array([[c, 1j * s], [1j * s, c]]).T
            ib += 1
        else:
            psi[:, m] *= np.exp(1j * phases[:, it])
            before.append(psi[:, m].copy())
            it += 1
    heaters, count_b = it, ib
    g = np.broadcast_to(np.eye(MODES, dtype=complex), (count, MODES, MODES)).copy()
    d = np.zeros((count, MODES, heaters + count_b), dtype=complex)
    for index in range(len(arch) - 1, -1, -1):
        kind, m, _ = arch[index]
        if kind == "bs":
            ib -= 1
            c, s = math.cos(couplers[ib] / 2), math.sin(couplers[ib] / 2)
            local = before[index] @ (0.5 * np.array([[-s, 1j * c], [1j * c, -s]])).T
            d[:, :, heaters + ib] = np.einsum("cij,cj->ci", g[:, :, m : m + 2], local)
            g[:, :, m : m + 2] = g[:, :, m : m + 2] @ np.array([[c, 1j * s], [1j * s, c]])
        else:
            it -= 1
            d[:, :, it] = g[:, :, m] * (1j * before[index])[:, None]
            g[:, :, m] *= np.exp(1j * phases[:, it])[:, None]
    return np.abs(psi) ** 2, 2 * np.real(np.conj(psi)[:, :, None] * d)


def prior_widths(data: dict[str, Any], heater_tau: float | None, coupler_tau: float | None) -> np.ndarray:
    """Per-parameter prior widths over (heaters, couplers); a family without one kind gives it width zero."""
    heaters, couplers = data["phases"].shape[1], len(data["couplers"])
    return np.concatenate([np.full(heaters, heater_tau or 0.0), np.full(couplers, coupler_tau or 0.0)])


def static_light(data: dict[str, Any], offsets: np.ndarray, free: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pure-state block-conditioned light and its Jacobian over the free offsets (configurations x 4 x free)."""
    heaters = data["phases"].shape[1]
    full = np.zeros(len(free))
    full[free] = offsets
    p, dp = pure_jacobians(
        data["couplers"] + full[heaters:], data["arch"], data["phases"] + full[None, :heaters], data["sources"]
    )
    raw = np.clip(p[:, :LOGICAL], PROBABILITY_FLOOR, None)
    total = raw.sum(axis=1)
    light = raw / total[:, None]
    # A cell held at the floor does not move with the offsets, so its derivative is zero.
    block = dp[:, :LOGICAL, :][:, :, free] * (p[:, :LOGICAL] > PROBABILITY_FLOOR)[:, :, None]
    dlight = (block - light[:, :, None] * block.sum(axis=1)[:, None, :]) / total[:, None, None]
    return light, dlight


def static_objective(
    data: dict[str, Any], tau: np.ndarray, free: np.ndarray, offsets: np.ndarray
) -> tuple[float, np.ndarray]:
    """Negative log posterior of shared static offsets under independent N(0, tau^2) priors, and its gradient."""
    total = data["block"].sum(axis=1)
    light_share = (total - data["background"].sum(axis=1)) / total
    light, dlight = static_light(data, offsets, free)
    pi = setting_probabilities(data, light)
    dpi = light_share[:, None, None] * dlight[data["configuration"]]
    precision = 1 / (tau * tau)
    value = -float((data["block"] * np.log(pi)).sum()) + float((precision * offsets * offsets).sum()) / 2
    grad = -np.einsum("sm,smh->h", data["block"] / pi, dpi) + precision * offsets
    return value, grad


def static_mode(data: dict[str, Any], tau: np.ndarray, free: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Maximum a posteriori static offsets from zero, and the posterior Hessian there."""
    result = minimize(
        lambda offsets: static_objective(data, tau, free, offsets),
        np.zeros(int(free.sum())),
        jac=True,
        method="L-BFGS-B",
        options={"ftol": FIT_TOLERANCE, "gtol": STATIC_GRADIENT_TOLERANCE, "maxiter": FIT_ITERATIONS},
    )
    require(bool(result.success), f"static fit: the fit did not converge: {result.message}")
    return refine(data, tau, free, np.asarray(result.x))


class HessianColumn:
    """One column of the posterior Hessian: the central difference of the analytic gradient along one offset."""

    def __init__(self, data: dict[str, Any], tau: np.ndarray, free: np.ndarray, offsets: np.ndarray) -> None:
        self.data, self.tau, self.free, self.offsets = data, tau, free, offsets

    def __call__(self, index: int) -> np.ndarray:
        up, down = self.offsets.copy(), self.offsets.copy()
        up[index] += HESSIAN_STEP
        down[index] -= HESSIAN_STEP
        gradient_up = static_objective(self.data, self.tau, self.free, up)[1]
        gradient_down = static_objective(self.data, self.tau, self.free, down)[1]
        column: np.ndarray = (gradient_up - gradient_down) / (2 * HESSIAN_STEP)
        return column


def posterior_hessian(data: dict[str, Any], tau: np.ndarray, free: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """Exact Hessian of the negative log posterior (observed information plus prior precision), by central
    differences of the analytic gradient, symmetrized. The columns are independent and go through the pool,
    which runs them serially inside a worker that already holds one slot."""
    columns = ordered_map(HessianColumn(data, tau, free, offsets), list(range(len(offsets))))
    hessian = np.stack(columns, axis=1)
    return (hessian + hessian.T) / 2


def refine(
    data: dict[str, Any], tau: np.ndarray, free: np.ndarray, offsets: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Newton steps from the L-BFGS endpoint to the posterior mode, and the Hessian there.

    L-BFGS stops on its relative function tolerance with the gradient still large along directions the data
    barely constrain, where only the prior curves the posterior, so its endpoint follows the BLAS build. Exact
    Newton steps, damped to positive definiteness and halved until the posterior does not rise, converge
    quadratically on the mode, and the mode's Hessian must be positive definite."""
    value, grad = static_objective(data, tau, free, offsets)
    for _ in range(REFINE_STEPS):
        hessian = posterior_hessian(data, tau, free, offsets)
        lowest = float(np.linalg.eigvalsh(hessian).min())
        damping = 0.0 if lowest > 0 else REFINE_DAMPING - lowest
        step = np.linalg.solve(hessian + damping * np.eye(len(offsets)), grad)
        if float(np.abs(step).max()) < REFINE_TOLERANCE:
            require(lowest > 0, "static fit: the converged point is not a posterior mode")
            return offsets, hessian
        scale = 1.0
        while True:
            trial = offsets - scale * step
            trial_value, trial_grad = static_objective(data, tau, free, trial)
            # Near the mode a Newton step changes the posterior by less than its rounding, so a step within
            # that rounding of the current value is accepted.
            if trial_value <= value + ROUNDING * abs(value):
                break
            scale /= 2
            # A damped step on an indefinite Hessian can be far longer than the basin, so the search halves until
            # the step itself, not its scale, falls below the line-search floor.
            require(
                scale * float(np.abs(step).max()) > LINE_SEARCH_FLOOR, "static fit: no Newton step lowers the posterior"
            )
        offsets, value, grad = trial, trial_value, trial_grad
    raise ValueError(f"static fit: the Newton refinement did not converge in {REFINE_STEPS} steps")


def fit_static(item: tuple[str, float | None, float | None, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    family, heater_tau, coupler_tau, a, b = item
    widths = prior_widths(a, heater_tau, coupler_tau)
    free = widths > 0
    tau = widths[free]
    offsets, hessian = static_mode(a, tau, free)
    light_a, _ = static_light(a, offsets, free)
    covariance = np.linalg.inv(hessian)
    light_b, jacobian_b = static_light(b, offsets, free)
    out = summarize(family, a, b, covariance, light_a, light_b, jacobian_b)
    out["mode"] = offsets
    # Element positions as (mode, mesh column) of the returned layout, heaters then couplers in layout order.
    column = mesh.column_index(a["arch"])
    heaters = [j for j, (kind, _, _) in enumerate(a["arch"]) if kind == "ps"]
    couplers = [j for j, (kind, _, _) in enumerate(a["arch"]) if kind == "bs"]
    se = np.sqrt(np.diag(covariance))
    rows = iter(zip(offsets, se, strict=True))
    for kind, slots, width in (("heater", heaters, heater_tau), ("coupler", couplers, coupler_tau)):
        if width is None:
            continue
        values = [next(rows) for _ in slots]
        out[f"{kind}_offsets"] = {
            "tau": width,
            "rms": float(math.sqrt(sum(v * v for v, _ in values) / len(values))),
            "rows": [
                {"mode": int(a["arch"][j][1]), "column": int(column[j]), "value": float(v), "se": float(e)}
                for j, (v, e) in zip(slots, values, strict=True)
            ],
        }
    return out


def without_configuration(data: dict[str, Any], left_out: int) -> dict[str, Any]:
    """The run with one configuration's settings removed, configurations renumbered in order."""
    kept = [c for c in range(len(data["keys"])) if c != left_out]
    renumber = {c: i for i, c in enumerate(kept)}
    rows = data["configuration"] != left_out
    out = dict(data)
    out["phases"], out["sources"] = data["phases"][kept], data["sources"][kept]
    out["keys"] = [data["keys"][c] for c in kept]
    out["configuration"] = np.array([renumber[int(c)] for c in data["configuration"][rows]])
    out["block"], out["background"] = data["block"][rows], data["background"][rows]
    return out


def left_out_statistics(
    data: dict[str, Any], light: np.ndarray, left_out: int
) -> list[tuple[str, float, float, float]]:
    """(readout, observed, predicted, variance) of each analyzer readout the left-out configuration serves."""
    settings = data["record"]["manifest"]["settings"]
    expected = setting_probabilities(data, light) * data["block"].sum(axis=1)[:, None]
    out = []
    for readout in SCORED:
        chosen = [
            i
            for i in np.flatnonzero(data["configuration"] == left_out)
            if settings[i]["readout"] == readout and settings[i]["block"] != "mutation"
        ]
        if chosen:
            z, variance = geometry.statistic(data["block"][chosen].sum(axis=0), readout)
            model = geometry.statistic(expected[chosen].sum(axis=0), readout)[0]
            out.append((readout, float(z), float(model), float(variance)))
    return out


def configuration_fold(
    item: tuple[str, float | None, float | None, dict[str, Any], int, np.ndarray],
) -> list[Any]:
    """Static offsets fitted on job-00 without one configuration, scored on that configuration.

    Newton steps from the full-data mode reach the fold mode in that basin, so the left-out configuration's
    counts choose the basin; scripts/ascella_configuration_holdout.py fits the folds from the zero start."""
    _, heater_tau, coupler_tau, data, left_out, start = item
    widths = prior_widths(data, heater_tau, coupler_tau)
    free = widths > 0
    offsets = refine(without_configuration(data, left_out), widths[free], free, start)[0]
    return left_out_statistics(data, static_light(data, offsets, free)[0], left_out)


def configuration_score(rows: list[tuple[str, float, float, float]]) -> dict[str, Any]:
    """Per readout, the multinomial-only statistic of every configuration against its left-out prediction."""
    return {
        readout: chi_square(
            sum((z - model) ** 2 / variance for r, z, model, variance in rows if r == readout),
            sum(1 for r, *_ in rows if r == readout),
        )
        for readout in SCORED
    }


def summarize(
    family: str,
    a: dict[str, Any],
    b: dict[str, Any],
    covariance: np.ndarray,
    light_a: np.ndarray,
    light_b: np.ndarray,
    jacobian_b: np.ndarray,
) -> dict[str, Any]:
    scored = held_out(b, light_b, jacobian_b, covariance)
    # The fit used job-00's counts, so its statistic has no chi-square reference and carries no p.
    in_sample = {
        readout: {"statistic": row["statistic"], "configurations": row["dof"]}
        for readout, row in held_out(a, light_a, np.zeros((*light_a.shape, 0)), np.zeros((0, 0))).items()
    }
    relation_b = relation_value(b, light_b)
    interval = observed_relation(b)["interval"]
    passes = all(scored[r]["p"] > DECISION_P for r in SCORED) and interval[0] <= relation_b <= interval[1]
    return {
        "family": family,
        "preregistered": family not in SUPPLEMENTARY,
        "job_00_log_likelihood": log_likelihood(a, light_a),
        "job_00_relation": relation_value(a, light_a),
        "job_00_in_sample": in_sample,
        "job_01_relation": relation_b,
        "held_out": scored,
        "explains_analyzer_response": bool(passes),
    }


def build(a_dir: Path, b_dir: Path) -> dict[str, Any]:
    a, b = job_data(a_dir), job_data(b_dir)
    require(a["record"]["manifest"]["job"] == "job-00" and b["record"]["manifest"]["job"] == "job-01", "job order")
    require(np.array_equal(a["couplers"], b["couplers"]), "the jobs report other couplers")
    require(sorted(a["keys"]) == sorted(b["keys"]), "the jobs group settings into other configurations")
    order = [b["keys"].index(key) for key in a["keys"]]
    require(bool(np.allclose(a["phases"], b["phases"][order], atol=0, rtol=0)), "the jobs compile other heater phases")
    low = ordered_map(fit_family, [(family, a, b) for family in FAMILIES], min_items=1)
    static = ordered_map(fit_static, [(*spec, a, b) for spec in STATIC_FAMILIES], min_items=1)
    modes = [row.pop("mode") for row in static]
    folds = ordered_map(
        configuration_fold,
        [(*spec, a, k, mode) for spec, mode in zip(STATIC_FAMILIES, modes, strict=True) for k in range(len(a["keys"]))],
        min_items=1,
    )
    count = len(a["keys"])
    for index, row in enumerate(static):
        row["leave_configuration_out"] = configuration_score(
            [entry for fold in folds[index * count : (index + 1) * count] for entry in fold]
        )
    nominal_light = family_probabilities(a, "nominal", np.zeros(0))
    low[0]["leave_configuration_out"] = configuration_score(
        [entry for k in range(count) for entry in left_out_statistics(a, nominal_light, k)]
    )
    nominal = low[0]["job_00_log_likelihood"]
    rows = []
    for row in [*low, *static]:
        row["job_00_gain_over_nominal"] = row["job_00_log_likelihood"] - nominal
        rows.append(row)
    observed = {job: observed_relation(data) for job, data in (("job-00", a), ("job-01", b))}
    return {
        "schema": "ascella-signed-coherence-physical-models-v1",
        "runs": [a_dir.relative_to(ROOT).as_posix(), b_dir.relative_to(ROOT).as_posix()],
        "configurations": len(a["keys"]),
        "heaters": int(a["phases"].shape[1]),
        "couplers": int(len(a["couplers"])),
        "observed_block_conditioned_relation": observed,
        "families": rows,
        "explaining_families": [
            row["family"] for row in rows if row["explains_analyzer_response"] and row["preregistered"]
        ],
    }


def replay(a: Any, b: Any, path: str) -> None:
    """Every fitted-family float within the fit replay bounds of the retained value; every other field exact."""
    if isinstance(a, float) and not isinstance(b, bool):
        require(isinstance(b, int | float), f"{path}: {a!r} against {b!r}")
        bound = FIT_REPLAY_RELATIVE * max(abs(a), abs(b)) + FIT_REPLAY_ABSOLUTE
        require(abs(a - b) <= bound, f"{path}: {a} against {b}")
    elif isinstance(a, dict):
        require(isinstance(b, dict) and sorted(a) == sorted(b), f"{path}: keys differ")
        for key in a:
            replay(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, list):
        require(isinstance(b, list) and len(a) == len(b), f"{path}: lengths differ")
        for index, (x, y) in enumerate(zip(a, b, strict=True)):
            replay(x, y, f"{path}[{index}]")
    else:
        require(a == b, f"{path}: {a!r} against {b!r}")


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
        (close if row["family"] in UNFITTED else replay)(row, kept, where)


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    emit(build(Path(args[0]).resolve(), Path(args[1]).resolve()), Path(args[2]).resolve(), check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
