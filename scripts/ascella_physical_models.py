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
- detector efficiency (supplementary, fitted after the preregistered table): relative efficiencies of modes 1..3
  against mode 0, with dephasing.

Variances rather than widths are the fitted noise parameters, because a width's likelihood gradient vanishes at
zero and the zero-perturbation start would never move. The block-conditioned four-mode multinomial of every
setting carries a fixed in-block background: the setting's outside-block count shared over modes 0..3 by the
plan-time catalogue dark rates, B_m = outside * d_m / sum_{k >= 4} d_k. Every family carries the same term, so it
decides nothing between them.

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
# Parameter order, bounds and finite-difference step of each low-dimensional family.
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
SUPPLEMENTARY = ("detector_efficiency",)
STATIC_TAUS = (0.1, 0.3)
STEP = 1e-5
# L-BFGS endpoints of fits the data identify weakly follow the BLAS build, so every fitted family's numbers replay
# within this relative bound; the observed relation, keys, counts and verdicts replay exactly.
FIT_REPLAY_TOLERANCE = 1e-2
# A model probability never falls below this floor, so a count in a cell the mesh leaves dark stays finite.
PROBABILITY_FLOOR = 1e-9
FIT_TOLERANCE = 1e-12
FIT_ITERATIONS = 2000
STATIC_GRADIENT_TOLERANCE = 1e-8


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


def static_light(data: dict[str, Any], offsets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pure-state block-conditioned light and its offset Jacobian (configurations x 4 x heaters)."""
    p, dp = mesh.jacobians(data["arch"], data["phases"] + offsets[None, :], list(data["sources"]))
    raw = np.clip(p[:, :LOGICAL], PROBABILITY_FLOOR, None)
    total = raw.sum(axis=1)
    light = raw / total[:, None]
    dlight = (dp[:, :LOGICAL, :] - light[:, :, None] * dp[:, :LOGICAL, :].sum(axis=1)[:, None, :]) / total[
        :, None, None
    ]
    return light, dlight


def static_objective(data: dict[str, Any], tau: float, offsets: np.ndarray) -> tuple[float, np.ndarray]:
    """Negative log posterior of shared heater offsets under the N(0, tau^2) prior, and its gradient."""
    total = data["block"].sum(axis=1)
    light_share = (total - data["background"].sum(axis=1)) / total
    light, dlight = static_light(data, offsets)
    pi = setting_probabilities(data, light)
    dpi = light_share[:, None, None] * dlight[data["configuration"]]
    value = -float((data["block"] * np.log(pi)).sum()) + float(offsets @ offsets) / (2 * tau * tau)
    grad = -np.einsum("sm,smh->h", data["block"] / pi, dpi) + offsets / (tau * tau)
    return value, grad


def static_offsets(data: dict[str, Any], tau: float) -> np.ndarray:
    """Maximum a posteriori heater offsets from zero."""
    result = minimize(
        lambda offsets: static_objective(data, tau, offsets),
        np.zeros(data["phases"].shape[1]),
        jac=True,
        method="L-BFGS-B",
        options={"ftol": FIT_TOLERANCE, "gtol": STATIC_GRADIENT_TOLERANCE, "maxiter": FIT_ITERATIONS},
    )
    require(bool(result.success), f"static tau {tau}: the fit did not converge: {result.message}")
    return np.asarray(result.x)


def fit_static(item: tuple[float, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    tau, a, b = item
    heaters = a["phases"].shape[1]
    offsets = static_offsets(a, tau)
    light_a, jacobian_a = static_light(a, offsets)
    covariance = np.linalg.inv(fisher(a, jacobian_a, light_a) + np.eye(heaters) / (tau * tau))
    light_b, jacobian_b = static_light(b, offsets)
    out = summarize(f"static_heater_offsets_tau_{tau}", a, b, covariance, light_a, light_b, jacobian_b)
    out["offset_rms"] = float(math.sqrt(float(offsets @ offsets) / heaters))
    out["offset_max_abs"] = float(np.abs(offsets).max())
    # Heater positions as (mode, mesh column) of the returned layout, in heater order.
    column = mesh.column_index(a["arch"])
    where = [(a["arch"][j][1], column[j]) for j in mesh.phase_slots(a["arch"])]
    se = np.sqrt(np.diag(covariance))
    out["offsets"] = [
        {"mode": int(where[h][0]), "column": int(where[h][1]), "value": float(offsets[h]), "se": float(se[h])}
        for h in range(heaters)
    ]
    return out


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
    in_sample = held_out(a, light_a, np.zeros((*light_a.shape, 0)), np.zeros((0, 0)))
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
    static = ordered_map(fit_static, [(tau, a, b) for tau in STATIC_TAUS], min_items=1)
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
    """Every fitted-family float within FIT_REPLAY_TOLERANCE of the retained value; every other field exact."""
    if isinstance(a, float) and not isinstance(b, bool):
        require(isinstance(b, int | float), f"{path}: {a!r} against {b!r}")
        require(abs(a - b) <= FIT_REPLAY_TOLERANCE * max(1.0, abs(a), abs(b)), f"{path}: {a} against {b}")
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
    replay(fresh["families"], retained["families"], f"{name}.families")


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    emit(build(Path(args[0]).resolve(), Path(args[1]).resolve()), Path(args[2]).resolve(), check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
