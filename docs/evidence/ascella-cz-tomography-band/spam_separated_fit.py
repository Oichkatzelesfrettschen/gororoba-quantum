"""Constrained process fit of the Ascella CZ tomography pairs with the preparation-and-readout error of every
setting separated from the process (the nuisance-parameter fit of van Enk and Blume-Kohout 2013, priv 01508c79f85b,
Sec. IV), the realized-mesh model serving as the readout.

The case's estimator inverts absolute rates linearly at ideal preparations and readouts, so each setting's own
mesh error, output weights and throughput enter the process. Here the rate of setting s and outcome o is

    r(s, o) = t_s w_j(o) [ Tr((rho_s^T x E_o) J) + beta_j (p'(s, o) - p(s, o)) ],

with J the Choi matrix of one process for all 144 settings, constrained positive (J = L L^dagger), and three
nuisance terms, none of which one Choi matrix at ideal readouts holds:

* w_j(o), the outcome weight of job j: job_weight_reference.py ``job_weights``, fitted to the off-rail window
  patterns, so the eligible counts do not enter it. Fixed in the fit.
* p'(s, o) - p(s, o), the realized-mesh shift: the two-photon coincidence probability of the outcome's rail pair
  on the served mesh of setting s with the component errors of mesh-model-jobs.json, less that of the designed
  unitary, both at the overlap the component model's transfer fit gave this pair. It is exact when the process is
  the designed gate at that overlap and first order otherwise; the multiphoton and dark-click terms of the g2 law
  are taken as equal on the two meshes. beta_j converts a coincidence probability into this job's rate units: the
  job's summed weight-corrected rates over its summed p'. Fixed in the fit. Cross-fitted: a pair takes the
  components trained on the other pair. A law's components are admitted for a pair only when the cross-pair
  hold-out onto that pair survives under that law in mesh-model-jobs.json, the g2 law first, then the two-photon
  law; with neither, the decision fit carries no mesh shift.
* t_s, a free throughput per setting, normalized to geometric mean 1 over the nine readouts of each input. The
  nine readouts of one input measure one output state, whose trace fixes their common eligible rate, so the
  variation of the rate across them is readout error; the input's mean rate stays with the process. 128 free
  parameters beside the 256 of J, against 576 rates.

Fits, each by maximum Poisson likelihood of the eligible counts at the recorded shots (the sample-quota stopping
rule leaves the likelihood of the rates unchanged): ``process_only`` (no nuisance term), each term alone, and
``nuisance`` (every admitted term). F is the case's trace-normalized process fidelity <Phi_CZ| J |Phi_CZ> /
(4 Tr J). Beside each stands the case's unconstrained linear inversion of the rates with the same terms divided or
subtracted out. Descriptive mesh-shift fits take the components of each law, cross-fitted and in-sample.

Rule, fixed before the first fit of this file to measured counts (the commit that adds this file precedes the
commit that adds its output). Per pair, d = F(nuisance) - F(process_only) of the constrained fits, with the central
95 % of d over BOOTSTRAP parametric resamples of the acquisition (each resample refits both):

* agree: the interval lies inside -0.005 to 0.005. The separated terms do not move the fidelity;
* differ: the interval lies outside it, and F(nuisance) is the fidelity with those terms separated;
* undecided: the interval crosses a bound.

The model check of the case rejects the acquisition law the resamples follow, so the interval understates the
scatter and an ``undecided`` or a bare ``differ`` is read with that. The quantities of both pairs are reported; the
band pair is the subject.

--self-test draws a synthetic pair on the band pair's served meshes with planted component errors, per-job
weights and per-setting throughputs around the designed gate at overlap 0.93, and requires the nuisance fit and its
linear companion within 0.003 of the planted fidelity while the process-only fit misses it by more than that.

Seeds, docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json: index 222 the resamples, index 223 the self-test. Run
from the repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/spam_separated_fit.py --self-test``
or ``... spam_separated_fit.py MESH_MODEL_JOBS.json OUT.json``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sibling(name: str) -> Any:
    found = sys.modules.get(f"band_{name}")
    if found is not None:
        return found
    spec = importlib.util.spec_from_file_location(f"band_{name}", HERE / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"{name}.py not found beside this script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"band_{name}"] = module
    spec.loader.exec_module(module)
    return module


WEIGHTS = sibling("job_weight_reference")
MM = sibling("mesh_model")
ANALYSIS = WEIGHTS.ANALYSIS
CASE, TOMO = ANALYSIS.CASE, ANALYSIS.TOMO
ROWS, JOB = ANALYSIS.ROWS, WEIGHTS.JOB
LAWS = ("g2", "two-photon")  # admission order
OTHER = {"retained": "band", "band": "retained"}
MARGIN = 0.005
BOOTSTRAP = 100
BOOTSTRAP_INDEX = 222
SELF_TEST_INDEX = 223
ROUND_ITERATIONS = 500
ROUND_EVALUATIONS = 1000
ROUNDS = 10
RAIL_MODES = [(c, t) for c in (TOMO.C0, TOMO.C1) for t in (TOMO.T0, TOMO.T1)]
INPUTS = sorted({row["input"] for row in ROWS})
GROUP = np.array([[1.0 / 9.0 if a["input"] == b["input"] else 0.0 for b in ROWS] for a in ROWS])
torch.set_default_dtype(torch.float64)


# ---------------------------------------------------------------- the readout model


def rail_probabilities(a: np.ndarray, b: np.ndarray, overlap: float) -> np.ndarray:
    """(settings, 4) two-photon coincidence probability of each eligible outcome from the amplitudes of the two
    source modes, at one overlap."""
    out = np.empty((a.shape[0], 4))
    for o, (i, j) in enumerate(RAIL_MODES):
        ind = np.abs(a[:, i] * b[:, j] + a[:, j] * b[:, i]) ** 2
        dis = np.abs(a[:, i] * b[:, j]) ** 2 + np.abs(a[:, j] * b[:, i]) ** 2
        out[:, o] = overlap * ind + (1.0 - overlap) * dis
    return out


@cache
def designed_amplitudes() -> tuple[np.ndarray, np.ndarray]:
    unitaries = np.array([TOMO.setting_unitary(row) for row in ROWS])
    return unitaries[:, :, TOMO.C0], unitaries[:, :, TOMO.T0]


def served_phases(pair: str) -> tuple[list[Any], np.ndarray]:
    """The architecture and the (144, heaters) commanded phases of a pair in schedule order."""
    runs = ANALYSIS.pairs_of_runs()[pair]["runs"]
    seeds = ANALYSIS.seeds_by_setting(runs)
    loaded = [MM.load(run) for run in runs]
    by_seed = {seed: row for part in loaded for seed, row in zip(part["seeds"], part["phases"], strict=True)}
    return loaded[0]["arch"], np.array([by_seed[seeds[row["name"]]] for row in ROWS])


def realized_probabilities(
    arch: list[Any], phases: np.ndarray, components: dict[str, Any], overlap: float
) -> np.ndarray:
    mesh = MM.Mesh(arch)
    with torch.no_grad():
        u = mesh.columns(
            torch.tensor(phases),
            torch.tensor(np.asarray(components["d"], dtype=float)),
            torch.tensor(np.asarray(components["o"], dtype=float)),
            torch.tensor(float(components["g"])),
            torch.tensor(float(components["k"])),
        ).numpy()
    return rail_probabilities(u[:, :, 0], u[:, :, 1], overlap)


# ---------------------------------------------------------------- the fits


@cache
def design_tensor() -> torch.Tensor:
    """(576, 16, 16): the operator rho^T x E of every setting and outcome, so a rate is Re Tr(A J)."""
    return torch.tensor(np.einsum("rk,kij->rij", TOMO.design_matrix(), TOMO.hermitian_stack()))


def fidelity_of(choi: np.ndarray) -> float:
    return float(TOMO.trace_normalized_fidelity(choi))


def prepared(item: dict[str, Any]) -> dict[str, np.ndarray]:
    """The fixed terms of one fit: outcome weights, the scaled mesh shift and the weight-corrected rates."""
    eligible, shots, scale = item["eligible"], item["shots"], item["scale"]
    omega = item["omega"] if item["weights"] else np.ones_like(eligible)
    rates = eligible / shots[:, None] * scale[:, None] / omega
    shift = np.zeros_like(eligible)
    if item["realized"] is not None:
        beta = np.array([rates[JOB == j].sum() / item["realized"][JOB == j].sum() for j in (0, 1)])
        shift = beta[JOB][:, None] * (item["realized"] - item["designed"])
    return {"omega": omega, "rates": rates, "shift": shift}


def fit(item: dict[str, Any]) -> dict[str, Any]:
    """One constrained fit and its linear companion. ``item`` holds the counts, shots and scales, the outcome
    weights, the realized and designed rail probabilities (None for no mesh shift) and the switches ``weights``
    and ``throughput``. The unit parallel.ordered_map maps."""
    terms = prepared(item)
    n = torch.tensor(item["eligible"])
    exposure = torch.tensor(item["shots"] / item["scale"])[:, None] * torch.tensor(terms["omega"])
    shift = torch.tensor(terms["shift"])
    group = torch.tensor(GROUP)
    design = design_tensor()
    linear = terms["rates"] - terms["shift"]
    if item["throughput"]:
        totals = np.log(linear.sum(1))
        linear = linear / np.exp(totals - GROUP @ totals)[:, None]
    flat = linear.reshape(-1)
    raw = TOMO.linear_inversion(flat)
    start = item.get("start")
    if start is None:
        values, vectors = np.linalg.eigh(TOMO.project_positive_fixed_trace(raw))
        floor = 1e-6 * float(values.sum()) / len(values)
        start = vectors * np.sqrt(np.maximum(values, floor))
    real = torch.tensor(np.real(start), requires_grad=True)
    imag = torch.tensor(np.imag(start), requires_grad=True)
    tau = torch.zeros(len(ROWS), requires_grad=bool(item["throughput"]))
    params = [real, imag] + ([tau] if item["throughput"] else [])
    opt = torch.optim.LBFGS(
        params,
        max_iter=ROUND_ITERATIONS,
        max_eval=ROUND_EVALUATIONS,
        line_search_fn="strong_wolfe",
        tolerance_grad=1e-10,
        tolerance_change=1e-13,
    )

    def choi() -> torch.Tensor:
        factor = torch.complex(real, imag)
        return factor @ factor.conj().T

    def objective() -> torch.Tensor:
        rate = torch.real(torch.einsum("rij,ji->r", design, choi())).reshape(n.shape)
        mean = exposure * torch.exp(tau - group @ tau)[:, None] * (rate + shift)
        return (mean.clamp_min(1e-12) - n * torch.log(mean.clamp_min(1e-12))).sum()

    def closure() -> torch.Tensor:
        opt.zero_grad()
        value = objective()
        value.backward()
        return value

    done, evaluated, ended_early = 0, 0, False
    for _ in range(ROUNDS):
        opt.step(closure)
        state = opt.state[params[0]]
        ended_early = state["n_iter"] - done < ROUND_ITERATIONS and state["func_evals"] - evaluated < ROUND_EVALUATIONS
        done, evaluated = state["n_iter"], state["func_evals"]
        if ended_early:
            break
    final = closure()
    gradient = max(float(p.grad.abs().max()) for p in params if p.grad is not None)
    fitted = choi().detach().numpy()
    log_t = (tau - group @ tau).detach().numpy()
    return {
        "process_fidelity": fidelity_of(fitted),
        "linear_inversion_process_fidelity": float(TOMO.batch_fidelity(flat[None, :])[0]),
        "objective": float(final.detach()),
        "throughput_log_rms": float(np.sqrt(np.mean(log_t**2))),
        "factor": torch.complex(real, imag).detach().numpy(),
        "status": {
            "iterations": int(done),
            "function_evaluations": int(evaluated),
            "largest_gradient_entry": gradient,
            "ended_early": bool(ended_early),
        },
    }


def resample(data: dict[str, np.ndarray], generator: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """One parametric resample of the acquisition, drawn as TOMO.resampled_rates draws it."""
    eligible, samples, shots = data["eligible"], data["samples"], data["shots"]
    rest = samples - eligible.sum(axis=1)
    probabilities = np.concatenate([eligible, rest[:, None]], axis=1) / samples[:, None]
    drawn = np.empty_like(eligible)
    drawn_shots = np.empty_like(shots)
    for s in range(len(samples)):
        drawn[s] = generator.multinomial(int(samples[s]), probabilities[s])[:4]
        drawn_shots[s] = samples[s] + generator.negative_binomial(int(samples[s]), samples[s] / shots[s])
    return drawn, drawn_shots


def report(found: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in found.items() if key != "factor"}


def decide(low: float, high: float) -> str:
    if -MARGIN <= low and high <= MARGIN:
        return "agree"
    if high < -MARGIN or low > MARGIN:
        return "differ"
    return "undecided"


def analyze_pair(
    data: dict[str, np.ndarray],
    omega: np.ndarray,
    meshes: dict[str, np.ndarray],
    admitted: str | None,
    generator: np.random.Generator,
    replicates: int,
) -> dict[str, Any]:
    """Every fit of one pair. ``meshes`` maps a label to the realized rail probabilities of one component set;
    ``admitted`` names the label the decision fit takes, or None."""
    base = {"eligible": data["eligible"], "shots": data["shots"], "scale": data["scale"], "omega": omega}
    plain = {**base, "weights": False, "throughput": False, "realized": None, "designed": None}
    variants: dict[str, dict[str, Any]] = {
        "process_only": plain,
        "job_weights": {**plain, "weights": True},
        "throughput": {**plain, "throughput": True},
    }
    for label, entry in meshes.items():
        variants[f"mesh_shift {label}"] = {**plain, "realized": entry["realized"], "designed": entry["designed"]}
    nuisance = {**plain, "weights": True, "throughput": True}
    if admitted is not None:
        nuisance = {**nuisance, "realized": meshes[admitted]["realized"], "designed": meshes[admitted]["designed"]}
    variants["nuisance"] = nuisance
    names = list(variants)
    fitted = dict(zip(names, CASE.ordered_map(fit, [variants[name] for name in names], min_items=1), strict=True))
    items = []
    for _ in range(replicates):
        drawn, drawn_shots = resample(data, generator)
        for name in ("process_only", "nuisance"):
            items.append({**variants[name], "eligible": drawn, "shots": drawn_shots, "start": fitted[name]["factor"]})
    replicated = CASE.ordered_map(fit, items, min_items=1)
    free = np.array([entry["process_fidelity"] for entry in replicated[0::2]])
    held = np.array([entry["process_fidelity"] for entry in replicated[1::2]])
    low, high = (float(v) for v in np.percentile(held - free, [2.5, 97.5])) if replicates else (float("nan"),) * 2
    difference = fitted["nuisance"]["process_fidelity"] - fitted["process_only"]["process_fidelity"]
    return {
        "fits": {name: report(fitted[name]) for name in names},
        "admitted_mesh": admitted,
        "difference": difference,
        "difference_95": [low, high],
        "nuisance_fidelity_95": [float(v) for v in np.percentile(held, [2.5, 97.5])] if replicates else None,
        "process_only_fidelity_95": [float(v) for v in np.percentile(free, [2.5, 97.5])] if replicates else None,
        "resample_fits_not_ended_early": int(sum(not entry["status"]["ended_early"] for entry in replicated)),
        "verdict": decide(low, high) if replicates else None,
    }


# ---------------------------------------------------------------- self-test and main


def self_test() -> int:
    rng = np.random.default_rng(MM.draw_seed(SELF_TEST_INDEX))
    arch, phases = served_phases("band")
    mesh = MM.Mesh(arch)
    overlap, brightness, shots = 0.93, 0.03, 2.0e7
    planted = {"d": rng.normal(0.0, 0.03, mesh.nb), "o": rng.normal(0.0, 0.05, mesh.np_), "g": 0.0, "k": 0.0}
    realized = realized_probabilities(arch, phases, planted, overlap)
    designed = rail_probabilities(*designed_amplitudes(), overlap)
    mode = np.exp(rng.normal(0.0, 0.08, (2, 4)))
    omega = np.array([[mode[j][c] * mode[j][2 + t] for c in (0, 1) for t in (0, 1)] for j in (0, 1)])
    omega = (omega / np.exp(np.log(omega).mean(1, keepdims=True)))[JOB]
    log_t = rng.normal(0.0, 0.04, len(ROWS))
    throughput = np.exp(log_t - GROUP @ log_t)
    truth = float(TOMO.batch_fidelity((brightness * designed).reshape(1, -1))[0])
    eligible = rng.poisson(shots * brightness * throughput[:, None] * omega * realized).astype(float)
    data = {
        "eligible": eligible,
        "samples": np.full(len(ROWS), 0.0),
        "shots": np.full(len(ROWS), shots),
        "scale": np.ones(len(ROWS)),
    }
    meshes = {"planted": {"realized": realized, "designed": designed}}
    found = analyze_pair(data, omega, meshes, "planted", rng, 0)["fits"]
    out = {
        "planted_fidelity": truth,
        "process_only": found["process_only"]["process_fidelity"],
        "nuisance": found["nuisance"]["process_fidelity"],
        "nuisance_linear": found["nuisance"]["linear_inversion_process_fidelity"],
        "process_only_linear": found["process_only"]["linear_inversion_process_fidelity"],
        "nuisance_throughput_log_rms": found["nuisance"]["throughput_log_rms"],
        "planted_throughput_log_rms": float(np.sqrt(np.mean((log_t - GROUP @ log_t) ** 2))),
        "status": {name: found[name]["status"] for name in ("process_only", "nuisance")},
    }
    print(json.dumps(out, indent=1))
    if abs(out["nuisance"] - truth) > 0.003 or abs(out["nuisance_linear"] - truth) > 0.003:
        raise SystemExit("self-test: the nuisance fit does not recover the planted fidelity")
    if abs(out["process_only"] - truth) <= 0.003:
        raise SystemExit("self-test: the planted nuisance terms do not move the process-only fit")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if len(args.paths) != 2:
        raise SystemExit("usage: spam_separated_fit.py --self-test | MESH_MODEL_JOBS.json OUT.json")
    model = json.loads(Path(args.paths[0]).read_text(encoding="utf-8"))
    generator = np.random.default_rng(MM.draw_seed(BOOTSTRAP_INDEX))
    out: dict[str, Any] = {"margin": MARGIN, "resamples": BOOTSTRAP, "seed_index": BOOTSTRAP_INDEX}
    for pair, spec in ANALYSIS.pairs_of_runs().items():
        data = ANALYSIS.tallies(spec)
        fitted = WEIGHTS.job_weights(spec["runs"])
        omega = np.array([fitted[job]["outcome_weights"] for job in JOB])
        arch, phases = served_phases(pair)
        holdout = f"{OTHER[pair]}_to_{pair}"
        meshes: dict[str, Any] = {}
        admitted = None
        for law in LAWS:
            overlap = float(model[law][holdout]["overlap"]["transfer"])
            designed = rail_probabilities(*designed_amplitudes(), overlap)
            for label, trained_on in (("cross-fitted", OTHER[pair]), ("in-sample", pair)):
                components = model["components"][law][trained_on]
                meshes[f"{law} {label}"] = {
                    "realized": realized_probabilities(arch, phases, components, overlap),
                    "designed": designed,
                    "overlap": overlap,
                }
            if admitted is None and model[law][holdout]["survives"]:
                admitted = f"{law} cross-fitted"
        found = analyze_pair(data, omega, meshes, admitted, generator, BOOTSTRAP)
        found["job_weights"] = fitted
        found["mesh_overlaps"] = {label: entry["overlap"] for label, entry in meshes.items()}
        found["case_linear_inversion_process_fidelity"] = float(
            TOMO.batch_fidelity(TOMO.absolute_rates(data["eligible"], data["shots"], data["scale"])[None, :])[0]
        )
        out[pair] = found
    Path(args.paths[1]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
