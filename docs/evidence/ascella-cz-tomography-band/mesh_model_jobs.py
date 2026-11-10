"""The chip-level component model of mesh_model.py with output weights per job, under two pattern laws, with a
wider null and a recorded optimizer status.

mesh_model.py fits one overlap M and one set of twelve output weights per pair of runs. ``schedule`` assigns a
setting to job-00 or job-01 by the parity of its input labels, so a weight that differs between the two jobs of a
pair is a function of the commanded phases, and the per-component errors can absorb it. Here every job of a fit
carries its own eleven free output weights (mode 0 fixed at 1) while M stays one value per fit, so the component
errors no longer stand in for a job-to-job weight change. The four hold-outs, the ridge penalty and the deviance
score are those of mesh_model.py. A within-pair hold-out trains and tests on one job each, so there only the null,
the restarts and the optimizer rounds differ from mesh_model.py.

Two pattern laws:

* ``two-photon``: mesh_model.py's law, q_ij proportional to w_i w_j (M ind_ij + (1 - M) dis_ij).
* ``g2``: Perceval's source model as ``photon_distribution`` and ``detected_clicks`` of
  scripts/ascella_cz_tomography_case.py compose it, evaluated on the realized mesh. Each source emits one photon
  with probability 1 - p2 and a second, fully distinguishable noise photon with probability p2, where
  g2 = 2 p2 / (1 + p2)^2. Every photon is detected with the plan read's transmittance T, a mode clicks when it
  holds a detected photon, and each mode adds a dark click with its per-attempt probability (first order). A
  two-click pattern then collects: two photons both detected; three photons with one lost, or all detected on two
  modes; four photons with two lost (the terms of order p2^2 T^3 and beyond are dropped); and a one-click pattern
  with one dark click. g2, T and the dark rates are the plan read of the pair a fit runs on and are not fitted.

Null: NULL_DRAWS draws. Each permutes and sign-flips the coupler and heater vectors, as mesh_model.py does, and
also applies the fitted heater gain to the commanded phase of a randomly permuted heater and the fitted crosstalk
coefficient to a randomly permuted neighbourhood sum, each with a random sign.

Optimizer: L-BFGS in rounds of ROUND_ITERATIONS iterations and ROUND_EVALUATIONS function evaluations until a round
stops below both limits, at most ROUNDS rounds (mesh_model.py runs one round of 300 iterations and 375
evaluations); every fit records its iterations, function evaluations, final objective, largest gradient entry and
whether its last round stopped below both limits. Every component fit runs from RESTARTS starts (zero, then
Gaussian starts of 0.01 rad on the couplers and 0.02 rad on the heaters); the lowest objective is kept and the
record holds every start's objective and the largest component difference between the kept solution and the
others.

Preregistered test, fixed before the first fit of this file to measured counts (the commit that adds this file
precedes the commit that adds its output). Per law and hold-out, with B the ideal-mesh baseline, T the transfer, C
the in-sample ceiling and N the null draws, all with M and per-job weights refitted on the held-out runs:

* Gain = (dev_B - dev_T) / (dev_B - dev_C), the quantity of mesh_model.py;
* Gain over the null median = (median dev_N - dev_T) / (median dev_N - dev_C);
* rank p = (1 + number of null draws with dev_N <= dev_T) / (1 + NULL_DRAWS).

A hold-out survives when Gain >= 0.3, Gain over the null median >= 0.3 and p <= 0.05. The first condition is kept
beside the second because the second is a ratio of two small numbers when the trained components carry nothing.
Reading per law: all four hold-outs survive, the transferable commanded-phase content survives per-job weights;
the cross-pair hold-outs fail while the within-pair ones survive, the cross-date content of mesh_model.py was a
job-to-job weight change; a within-pair hold-out fails, the wider null removes the within-calibration claim. The
g2 law decides the same question with the source's multiphoton events and dark clicks in the law; it adds, as
description, the share of the ideal-mesh deviance that the source terms remove, 1 - dev_B(g2) / dev_B(two-photon),
beside the share the transferred components remove under each law.

--self-test checks, in order: the g2 law against Perceval on every sixth designed setting (largest difference of
a conditional pattern probability below 2e-5); the g2 law at g2 = 0 and no dark counts against the two-photon law
(1e-12); this file's fixed-component fit with one job against mesh_model.py's on retained job-00 (relative deviance
difference below 1e-6); a synthetic pair of dates drawn from the ideal mesh with one planted job-to-job weight
pattern common to both dates, which must not survive under per-job weights (its result under one weight set per
pair is reported); and a synthetic pair drawn with planted component errors and per-job weights, which must
survive with Gain >= 0.8.

Before the commit that adds this file, a timing run fitted the band pair's ideal-mesh baseline under both laws
(deviance 477,207 and 36,964) and twenty iterations of a component fit; it computed no hold-out quantity.

Seeds, docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json: index 217 the null draws, 218 the restarts, 219 the
self-test.

Run from the repository root, ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/mesh_model_jobs.py`` with:

* ``--self-test``;
* ``--extract INPUT.json``: the architecture, every run's commanded phases and pattern counts, each pair's plan
  read and the seed values, read from the retained records;
* ``--input INPUT.json OUT.json``: the fits. This mode imports numpy, torch, parallel.py and mesh_model.py only,
  so a Kaggle CPU kernel runs it without the repository's Quandela modules; mesh_model.py names three of them at
  import and calls them only in its ``load``, which this mode never reaches, so empty modules stand in for
  whichever of the three the interpreter cannot import;
* ``--check INPUT.json OUT.json``: refits the baseline and the transfer of every law and hold-out from the
  recorded components and requires each deviance within 1e-5 of the recorded one, the replay that admits a
  kernel's output on another host.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import sys
import types
from pathlib import Path
from typing import Any

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for _path in ("scripts", "gororoba_quantum"):
    if str(ROOT / _path) not in sys.path:
        sys.path.insert(0, str(ROOT / _path))

from parallel import ordered_map  # noqa: E402

RECORD_MODULES = ("photonic_compilation_audit", "qd_records", "ascella_cz_tomography_case")
ABSENT = []
for _name in RECORD_MODULES:
    try:
        importlib.import_module(_name)
    except ImportError:
        sys.modules[_name] = types.ModuleType(_name)
        ABSENT.append(_name)


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


MM = sibling("mesh_model")


def records() -> Any:
    """analyze.py, with the case and tomography modules the retained records are read through."""
    if ABSENT:
        raise RuntimeError(f"reading the retained records needs {', '.join(ABSENT)}; run --input on an extract")
    return sibling("analyze")


LAWS = ("two-photon", "g2")
HOLDOUTS = {
    "within_retained": ("retained-00", "retained-01"),
    "within_band": ("band-00", "band-01"),
    "retained_to_band": ("retained", "band"),
    "band_to_retained": ("band", "retained"),
}
NULL_DRAWS = 100
RESTARTS = 3
START_SCALE = {"d": 0.01, "o": 0.02}
ROUND_ITERATIONS = 300
ROUND_EVALUATIONS = 600
ROUNDS = 10
GAIN_FLOOR = 0.3
RANK_CEILING = 0.05
NULL_INDEX = 217
RESTART_INDEX = 218
SELF_TEST_INDEX = 219
I_IDX, J_IDX = MM.I_IDX, MM.J_IDX
torch.set_default_dtype(torch.float64)


# ---------------------------------------------------------------- data


def source_figures(pair: str) -> dict[str, Any]:
    """g2, transmittance and the twelve per-attempt dark-click probabilities of a pair's plan read."""
    case = records().CASE
    loader = {"retained": case.tomo.load_run, "band": case.load_run}[pair]
    runs = [run for key, run in MM.RUNS.items() if key.startswith(pair)]
    perfs = case.plan_reads([loader(ROOT / run) for run in runs])
    clock = float(perfs["Clock (MHz)"]) * 1e6
    dark = [float(rate) / clock for rate in perfs["Dark counts (detection/s)"]]
    return {
        "g2": float(perfs["g2 (%)"]) / 100.0,
        "transmittance": float(perfs["Transmittance (%)"]) / 100.0,
        "dark": dark,
    }


def extract() -> dict[str, Any]:
    """Everything the fits read, from the retained records: the fixed architecture, each run's commanded phases and
    66-pattern counts, each pair's source figures and the values of the three seed indices."""
    loaded = {key: MM.load(run) for key, run in MM.RUNS.items()}
    if len({json.dumps(entry["arch"]) for entry in loaded.values()}) != 1:
        raise RuntimeError("the four runs do not share one architecture")
    return {
        "schema": "ascella-mesh-component-model-input-v1",
        "arch": json.loads(json.dumps(loaded["retained-00"]["arch"])),
        "runs": {
            key: {"record": MM.RUNS[key], "phases": entry["phases"].tolist(), "counts": entry["counts"].tolist()}
            for key, entry in loaded.items()
        },
        "source": {pair: source_figures(pair) for pair in ("retained", "band")},
        "seeds": {str(index): MM.draw_seed(index) for index in (NULL_INDEX, RESTART_INDEX, SELF_TEST_INDEX)},
    }


def assemble(found: dict[str, Any]) -> tuple[list[Any], dict[str, dict[str, Any]]]:
    """The fixed architecture and the six fitting sets: the four runs with one job each, the two pairs with two."""
    sets: dict[str, dict[str, Any]] = {}
    for pair in ("retained", "band"):
        source = found["source"][pair]
        if len(source["dark"]) != MM.MODES:
            raise RuntimeError(f"{pair}: the plan read holds {len(source['dark'])} dark rates, not {MM.MODES}")
        parts = [
            {key: np.array(found["runs"][f"{pair}-{job}"][key], dtype=float) for key in ("phases", "counts")}
            for job in ("00", "01")
        ]
        for name, part in zip((f"{pair}-00", f"{pair}-01"), parts, strict=True):
            sets[name] = {**part, "job": np.zeros(len(part["counts"]), dtype=int), "source": source}
        sets[pair] = {
            "phases": np.concatenate([p["phases"] for p in parts]),
            "counts": np.concatenate([p["counts"] for p in parts]),
            "job": np.concatenate([np.full(len(p["counts"]), k) for k, p in enumerate(parts)]),
            "source": source,
        }
    return found["arch"], sets


# ---------------------------------------------------------------- model


def emission(g2: float) -> float:
    """p2 of a source with g2 = 2 p2 / (1 + p2)^2 at unit brightness."""
    return ((1.0 - g2) - math.sqrt(1.0 - 2.0 * g2)) / g2 if g2 > 0.0 else 0.0


def columns(
    mesh: Any, phases: torch.Tensor, comp: dict[str, torch.Tensor], perms: dict[str, Any] | None
) -> torch.Tensor:
    """mesh_model.Mesh.columns with the gain and crosstalk terms read through optional heater permutations (the
    identity for a fitted model, random for a null draw)."""
    own, near = phases, phases @ mesh.cross.T
    if perms is not None:
        own, near = own[:, torch.as_tensor(perms["g"])], near[:, torch.as_tensor(perms["k"])]
    realized = phases + comp["o"] + comp["g"] * own + comp["k"] * near
    nothing = torch.zeros(())
    return mesh.columns(realized, comp["d"], torch.zeros(mesh.np_), nothing, nothing)


def cross(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Probability that two independent photons with mode marginals x and y occupy the pattern's two modes."""
    return x[:, I_IDX] * y[:, J_IDX] + x[:, J_IDX] * y[:, I_IDX]


def pattern_law(
    u: torch.Tensor, overlap: torch.Tensor, log_w: torch.Tensor, job: torch.Tensor, source: dict[str, Any] | None
) -> torch.Tensor:
    """Conditional law of the 66 two-click patterns; ``source`` None gives the two-photon law, else the g2 law."""
    a, b = u[:, :, 0], u[:, :, 1]
    a2, b2 = a.abs() ** 2, b.abs() ** 2
    ind = (a[:, I_IDX] * b[:, J_IDX] + a[:, J_IDX] * b[:, I_IDX]).abs() ** 2
    pair = overlap * ind + (1 - overlap) * cross(a2, b2)
    if source is None:
        p = pair
    else:
        t = float(source["transmittance"])
        lost = 1.0 - t
        p2 = emission(float(source["g2"]))
        p1 = 1.0 - p2
        dark = torch.tensor(source["dark"])
        same = (1 + overlap) * a2 * b2  # both signal photons on one mode
        two = p1 * p1 * t * t * pair
        one = p1 * p1 * (t * lost * (a2 + b2) + t * t * same)
        for n in (a2, b2):  # the noise photon leaves the first or the second source
            kept = pair + cross(a2, n) + cross(b2, n)
            full = pair * (n[:, I_IDX] + n[:, J_IDX]) + same[:, I_IDX] * n[:, J_IDX] + same[:, J_IDX] * n[:, I_IDX]
            two = two + p1 * p2 * (t * t * lost * kept + t**3 * full)
            one = one + p1 * p2 * (
                t * lost * lost * (a2 + b2 + n) + t * t * lost * (same + a2 * n + b2 * n) + t**3 * same * n
            )
        four = pair + cross(a2, a2) + cross(b2, b2) + 3.0 * cross(a2, b2)
        two = two + p2 * p2 * t * t * lost * lost * four
        one = one + p2 * p2 * t * lost**3 * 2.0 * (a2 + b2)
        quiet = 1.0 - (dark.sum() - dark[I_IDX] - dark[J_IDX])
        p = two * quiet + one[:, I_IDX] * dark[J_IDX] + one[:, J_IDX] * dark[I_IDX]
    w = torch.exp(torch.cat([torch.zeros((log_w.shape[0], 1)), log_w], dim=1))[job]
    p = p * w[:, I_IDX] * w[:, J_IDX]
    return p / p.sum(1, keepdim=True)


def fit(item: dict[str, Any]) -> dict[str, Any]:
    """Maximum penalized likelihood of one fitting set under one law. ``free`` moves the component errors from
    ``start`` (zero when None); otherwise they stay at ``components`` (zero when None) and only M and the per-job
    weights move. The unit parallel.ordered_map maps."""
    mesh = MM.Mesh(item["arch"])
    data, free, perms = item["data"], item["free"], item.get("perms")
    ph, n = torch.tensor(data["phases"]), torch.tensor(data["counts"])
    job = torch.as_tensor(data["job"])
    jobs = int(job.max()) + 1
    source = data["source"] if item["law"] == "g2" else None
    given = item.get("start") if free else item.get("components")
    zero = {"d": np.zeros(mesh.nb), "o": np.zeros(mesh.np_), "g": 0.0, "k": 0.0}
    comp = {key: torch.tensor((given or zero)[key], dtype=torch.float64).requires_grad_(free) for key in zero}
    logit_m = torch.tensor(2.0, requires_grad=True)
    log_w = torch.zeros((jobs, MM.MODES - 1), requires_grad=True)
    params = [logit_m, log_w] + (list(comp.values()) if free else [])
    opt = torch.optim.LBFGS(
        params,
        max_iter=ROUND_ITERATIONS,
        max_eval=ROUND_EVALUATIONS,
        line_search_fn="strong_wolfe",
        tolerance_grad=1e-9,
    )

    def objective() -> torch.Tensor:
        law = pattern_law(columns(mesh, ph, comp, perms), torch.sigmoid(logit_m), log_w, job, source)
        value = MM.nll(n, law)
        if free:
            value = value + MM.RIDGE * ((comp["d"] / MM.D_SCALE) ** 2).sum()
            value = value + MM.RIDGE * ((comp["o"] / MM.O_SCALE) ** 2).sum()
        return value

    def closure() -> torch.Tensor:
        opt.zero_grad()
        value = objective()
        value.backward()
        return value

    done, evaluated, ended_early = 0, 0, False
    for _ in range(ROUNDS):
        opt.step(closure)
        state = opt.state[params[0]]
        # A round that stops below both of its limits stopped on L-BFGS's own gradient or change tolerance.
        ended_early = state["n_iter"] - done < ROUND_ITERATIONS and state["func_evals"] - evaluated < ROUND_EVALUATIONS
        done, evaluated = state["n_iter"], state["func_evals"]
        if ended_early:
            break
    final = closure()
    gradient = max(float(p.grad.abs().max()) for p in params if p.grad is not None)
    with torch.no_grad():
        law = pattern_law(columns(mesh, ph, comp, perms), torch.sigmoid(logit_m), log_w, job, source).numpy()
    out = {
        "overlap": float(torch.sigmoid(logit_m).detach()),
        "weights": [[1.0] + [float(x) for x in row] for row in torch.exp(log_w).detach()],
        "components": {key: value.detach().numpy().copy() for key, value in comp.items()},
        "objective": float(final.detach()),
        "deviance": MM.deviance(data["counts"], law),
        "status": {
            "iterations": int(done),
            "function_evaluations": int(opt.state[params[0]]["func_evals"]),
            "largest_gradient_entry": gradient,
            "ended_early": bool(ended_early),
        },
    }
    if item.get("keep_law"):
        out["law"] = law
    return out


# ---------------------------------------------------------------- hold-outs


def summary(components: dict[str, Any]) -> dict[str, float]:
    return {
        "coupler_rms": float(np.sqrt(np.mean(np.square(components["d"])))),
        "heater_offset_rms": float(np.sqrt(np.mean(np.square(components["o"])))),
        "heater_gain": float(components["g"]),
        "crosstalk": float(components["k"]),
    }


def null_draw(fitted: dict[str, Any], rng: np.random.Generator) -> tuple[dict[str, Any], dict[str, Any]]:
    components: dict[str, Any] = {}
    for key in ("d", "o"):
        v = np.asarray(fitted[key])
        components[key] = rng.permutation(v) * rng.choice([-1.0, 1.0], size=v.shape)
    heaters = len(components["o"])
    for key in ("g", "k"):
        components[key] = float(fitted[key]) * float(rng.choice([-1.0, 1.0]))
    return components, {"g": rng.permutation(heaters), "k": rng.permutation(heaters)}


def pearson(counts: np.ndarray, law: np.ndarray) -> float:
    expected = law * counts.sum(1, keepdims=True)
    return float(((counts - expected) ** 2 / np.maximum(expected, 1.0)).sum())


def component_fits(
    arch: list[Any],
    sets: dict[str, dict[str, Any]],
    laws: tuple[str, ...],
    restarts: int,
    rng: np.random.Generator,
) -> dict[tuple[str, str], dict[str, Any]]:
    """The component fit of every set under every law: the best of ``restarts`` starts, with every start's
    objective and status."""
    mesh = MM.Mesh(arch)
    starts: list[dict[str, Any] | None] = [None]
    for _ in range(restarts - 1):
        starts.append(
            {
                "d": rng.normal(0.0, START_SCALE["d"], mesh.nb),
                "o": rng.normal(0.0, START_SCALE["o"], mesh.np_),
                "g": 0.0,
                "k": 0.0,
            }
        )
    keys = [(law, name) for law in laws for name in sets]
    items = [
        {"arch": arch, "data": sets[name], "law": law, "free": True, "start": start, "keep_law": True}
        for law, name in keys
        for start in starts
    ]
    fitted = ordered_map(fit, items, min_items=1)
    out = {}
    for position, key in enumerate(keys):
        group = fitted[position * restarts : (position + 1) * restarts]
        best = min(group, key=lambda entry: float(entry["objective"]))
        gaps = [
            max(float(np.abs(np.asarray(best["components"][c]) - np.asarray(g["components"][c])).max()) for c in "do")
            for g in group
            if g is not best
        ]
        best["starts"] = {
            "objectives": [float(g["objective"]) for g in group],
            "deviances": [float(g["deviance"]) for g in group],
            "statuses": [g["status"] for g in group],
            "largest_component_difference_from_kept": max(gaps) if gaps else 0.0,
        }
        out[key] = best
    return out


def evaluate(
    arch: list[Any],
    sets: dict[str, dict[str, Any]],
    holdouts: dict[str, tuple[str, str]],
    laws: tuple[str, ...],
    null_draws: int,
    restarts: int,
    null_rng: np.random.Generator,
    restart_rng: np.random.Generator,
) -> dict[str, Any]:
    needed = {name for pair in holdouts.values() for name in pair}
    trained = component_fits(arch, {name: sets[name] for name in sets if name in needed}, laws, restarts, restart_rng)
    items, layout = [], []
    for law in laws:
        for name, (train, test) in holdouts.items():
            base = {"arch": arch, "data": sets[test], "law": law, "free": False}
            fitted = trained[(law, train)]["components"]
            items.append({**base, "components": None, "keep_law": True})
            items.append({**base, "components": fitted, "keep_law": True})
            for _ in range(null_draws):
                components, perms = null_draw(fitted, null_rng)
                items.append({**base, "components": components, "perms": perms})
            layout.append((law, name, train, test))
    scored = ordered_map(fit, items, min_items=1)
    out: dict[str, Any] = {law: {} for law in laws}
    width = 2 + null_draws
    for position, (law, name, train, test) in enumerate(layout):
        baseline, transfer, *nulls = scored[position * width : (position + 1) * width]
        ceiling, source = trained[(law, test)], trained[(law, train)]
        counts = sets[test]["counts"]
        null_dev = np.array([entry["deviance"] for entry in nulls])
        dev_b, dev_t, dev_c = baseline["deviance"], transfer["deviance"], ceiling["deviance"]
        median = float(np.median(null_dev))
        # A span that is not positive leaves its ratio undefined; the hold-out then does not survive.
        gain = (dev_b - dev_t) / (dev_b - dev_c) if dev_b > dev_c else None
        gain_null = (median - dev_t) / (median - dev_c) if median > dev_c else None
        rank = float((1 + int((null_dev <= dev_t).sum())) / (1 + null_draws))
        shares = counts / counts.sum(1, keepdims=True)
        shift = np.corrcoef((transfer["law"] - baseline["law"]).ravel(), (shares - baseline["law"]).ravel())[0, 1]
        out[law][name] = {
            "train_settings": int(len(sets[train]["counts"])),
            "test_settings": int(len(counts)),
            "train": {
                "overlap": source["overlap"],
                "deviance": source["deviance"],
                **summary(source["components"]),
                "starts": source["starts"],
            },
            "deviance_baseline": dev_b,
            "deviance_transfer": dev_t,
            "deviance_in_sample_ceiling": dev_c,
            "deviance_null": {
                "min": float(null_dev.min()),
                "percentile_2.5": float(np.percentile(null_dev, 2.5)),
                "median": median,
                "max": float(null_dev.max()),
                "draws": null_draws,
            },
            "gain": gain,
            "gain_over_null_median": gain_null,
            "rank_p": rank,
            "survives": bool(
                gain is not None
                and gain_null is not None
                and gain >= GAIN_FLOOR
                and gain_null >= GAIN_FLOOR
                and rank <= RANK_CEILING
            ),
            "below_every_null": bool(dev_t < null_dev.min()),
            "overlap": {
                "baseline": baseline["overlap"],
                "transfer": transfer["overlap"],
                "ceiling": ceiling["overlap"],
            },
            "weights_per_job": {"baseline": baseline["weights"], "transfer": transfer["weights"]},
            "ceiling_components": summary(ceiling["components"]),
            "ceiling_starts": ceiling["starts"],
            "shift_correlation": float(shift),
            "pearson": {
                "baseline": pearson(counts, baseline["law"]),
                "transfer": pearson(counts, transfer["law"]),
                "ceiling": pearson(counts, ceiling["law"]),
            },
            "status": {
                "baseline": baseline["status"],
                "transfer": transfer["status"],
                "null_fits_not_ended_early": int(sum(not entry["status"]["ended_early"] for entry in nulls)),
            },
            "cells": int(counts.size),
        }
    out["components"] = {
        law: {
            name: {
                "d": [float(v) for v in trained[(law, name)]["components"]["d"]],
                "o": [float(v) for v in trained[(law, name)]["components"]["o"]],
                "g": float(trained[(law, name)]["components"]["g"]),
                "k": float(trained[(law, name)]["components"]["k"]),
                "overlap": trained[(law, name)]["overlap"],
                "weights_per_job": trained[(law, name)]["weights"],
            }
            for name in sorted(needed)
        }
        for law in laws
    }
    return out


def reading(result: dict[str, Any]) -> str:
    within = [result[name]["survives"] for name in HOLDOUTS if name.startswith("within")]
    across = [result[name]["survives"] for name in HOLDOUTS if not name.startswith("within")]
    if all(within) and all(across):
        return "the transferable commanded-phase content survives per-job output weights"
    if all(within):
        return "the within-pair hold-outs survive and a cross-pair hold-out fails"
    return "a within-pair hold-out fails"


# ---------------------------------------------------------------- self-test


def check_g2_law(source: dict[str, Any]) -> float:
    analysis = records()
    TOMO = analysis.TOMO  # noqa: N806
    rows = analysis.ROWS[::6]
    overlap = 0.93
    u = torch.zeros((len(rows), MM.MODES, 2), dtype=torch.complex128)
    reference = np.zeros((len(rows), len(MM.PAIRS)))
    for s, row in enumerate(rows):
        unitary = TOMO.setting_unitary(row)
        u[s, : TOMO.WINDOW, 0] = torch.tensor(unitary[:, TOMO.C0])
        u[s, : TOMO.WINDOW, 1] = torch.tensor(unitary[:, TOMO.T0])
        photons = TOMO.photon_distribution(unitary, overlap, source["g2"])
        for key, p in TOMO.detected_clicks(photons, source["transmittance"], source["dark"]).items():
            on = [m for m, v in enumerate(key) if v]
            if len(on) == 2:
                reference[s, MM.PAIRS.index((on[0], on[1]))] += p
    reference = reference / reference.sum(1, keepdims=True)
    job = torch.zeros(len(rows), dtype=torch.long)
    flat = torch.zeros((1, MM.MODES - 1))
    law = pattern_law(u, torch.tensor(overlap), flat, job, source).numpy()
    gap = float(np.abs(law - reference).max())
    bare = {"g2": 0.0, "transmittance": source["transmittance"], "dark": [0.0] * MM.MODES}
    reduced = pattern_law(u, torch.tensor(overlap), flat, job, bare).numpy()
    plain = pattern_law(u, torch.tensor(overlap), flat, job, None).numpy()
    if float(np.abs(reduced - plain).max()) > 1e-12:
        raise SystemExit("self-test: the g2 law at g2 = 0 without dark counts departs from the two-photon law")
    if (TOMO.C0, TOMO.T0) != tuple(MM.SOURCES):
        raise SystemExit("self-test: the window's source modes are not the chip's source modes")
    return gap


def synthetic(
    arch: list[Any],
    template: dict[str, Any],
    components: dict[str, Any],
    log_w: np.ndarray,
    overlap: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    mesh = MM.Mesh(arch)
    comp = {key: torch.tensor(value, dtype=torch.float64) for key, value in components.items()}
    with torch.no_grad():
        u = columns(mesh, torch.tensor(template["phases"]), comp, None)
        law = pattern_law(u, torch.tensor(overlap), torch.tensor(log_w), torch.as_tensor(template["job"]), None).numpy()
    totals = template["counts"].sum(1).astype(int)
    drawn = np.array([rng.multinomial(t, p / p.sum()) for t, p in zip(totals, law, strict=True)], dtype=float)
    return {**template, "counts": drawn}


def self_test() -> int:
    arch, sets = assemble(extract())
    report: dict[str, Any] = {"g2_law_largest_difference_from_perceval": check_g2_law(sets["band"]["source"])}
    if report["g2_law_largest_difference_from_perceval"] > 2e-5:
        print(json.dumps(report, indent=1))
        raise SystemExit("self-test: the g2 law departs from Perceval's source model")
    mesh = MM.Mesh(arch)
    own = fit({"arch": arch, "data": sets["retained-00"], "law": "two-photon", "free": False, "components": None})
    theirs = MM.fit(mesh, sets["retained-00"]["phases"], sets["retained-00"]["counts"], free_components=False)
    report["baseline_deviance"] = {"this_file": own["deviance"], "mesh_model": theirs["deviance"]}
    if abs(own["deviance"] - theirs["deviance"]) > 1e-6 * theirs["deviance"]:
        print(json.dumps(report, indent=1))
        raise SystemExit("self-test: the one-job fit departs from mesh_model.py")
    rng = np.random.default_rng(MM.draw_seed(SELF_TEST_INDEX))
    nothing = {"d": np.zeros(mesh.nb), "o": np.zeros(mesh.np_), "g": 0.0, "k": 0.0}
    planted = {"d": rng.normal(0.0, 0.03, mesh.nb), "o": rng.normal(0.0, 0.05, mesh.np_), "g": 0.01, "k": 0.004}
    job_pattern = rng.normal(0.0, 0.15, (2, MM.MODES - 1))
    holdouts = {"synthetic": ("retained", "band")}

    def run(components: dict[str, Any], weights: list[np.ndarray], per_job: bool) -> dict[str, Any]:
        drawn = {
            name: synthetic(arch, sets[name], components, w, m, rng)
            for name, w, m in (("retained", weights[0], 0.93), ("band", weights[1], 0.92))
        }
        if not per_job:
            drawn = {name: {**entry, "job": np.zeros_like(entry["job"])} for name, entry in drawn.items()}
        result = evaluate(arch, drawn, holdouts, ("two-photon",), 20, 1, rng, rng)["two-photon"]["synthetic"]
        keys = ("gain", "gain_over_null_median", "rank_p", "survives", "deviance_baseline", "deviance_transfer")
        return {key: result[key] for key in keys} | {"deviance_ceiling": result["deviance_in_sample_ceiling"]}

    trap = [job_pattern, job_pattern]
    report["job_weight_trap_one_weight_set_per_pair"] = run(nothing, trap, per_job=False)
    report["job_weight_trap_per_job_weights"] = run(nothing, trap, per_job=True)
    free = [rng.normal(0.0, 0.15, (2, MM.MODES - 1)) for _ in range(2)]
    report["planted_components_per_job_weights"] = run(planted, free, per_job=True)
    print(json.dumps(report, indent=1))
    if report["job_weight_trap_per_job_weights"]["survives"]:
        raise SystemExit("self-test: a planted job-to-job weight pattern survives under per-job weights")
    found = report["planted_components_per_job_weights"]
    if not (found["survives"] and found["gain"] >= 0.8):  # survives implies a defined gain
        raise SystemExit("self-test: planted static components do not survive the hold-out")
    return 0


def run(found: dict[str, Any], digest: str) -> dict[str, Any]:
    arch, sets = assemble(found)
    null_rng = np.random.default_rng(int(found["seeds"][str(NULL_INDEX)]))
    restart_rng = np.random.default_rng(int(found["seeds"][str(RESTART_INDEX)]))
    fitted = evaluate(arch, sets, HOLDOUTS, LAWS, NULL_DRAWS, RESTARTS, null_rng, restart_rng)
    out: dict[str, Any] = {
        "schema": "ascella-mesh-component-model-per-job-v1",
        "input_sha256": digest,
        "rule": {"gain_floor": GAIN_FLOOR, "rank_ceiling": RANK_CEILING, "null_draws": NULL_DRAWS},
        "source": found["source"],
        "seed_indices": {"null": NULL_INDEX, "restarts": RESTART_INDEX},
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "torch": torch.__version__},
    }
    for law in LAWS:
        out[law] = {**fitted[law], "reading": reading(fitted[law])}
    two, g2 = fitted["two-photon"], fitted["g2"]
    out["source_share"] = {
        name: {
            "ideal_mesh_deviance_removed_by_source_terms": 1.0
            - g2[name]["deviance_baseline"] / two[name]["deviance_baseline"],
            "ideal_mesh_deviance_removed_by_transfer_two_photon": 1.0
            - two[name]["deviance_transfer"] / two[name]["deviance_baseline"],
            "ideal_mesh_deviance_removed_by_transfer_g2": 1.0
            - g2[name]["deviance_transfer"] / g2[name]["deviance_baseline"],
        }
        for name in HOLDOUTS
    }
    out["components"] = fitted["components"]
    return out


def check(found: dict[str, Any], digest: str, recorded: dict[str, Any]) -> int:
    """Refit the baseline and the transfer of every law and hold-out from the recorded components."""
    if recorded["input_sha256"] != digest:
        raise SystemExit("the output names another input file")
    arch, sets = assemble(found)
    items, keys = [], []
    for law in LAWS:
        for name, (train, test) in HOLDOUTS.items():
            base = {"arch": arch, "data": sets[test], "law": law, "free": False}
            stored = recorded["components"][law][train]
            components = {"d": np.array(stored["d"]), "o": np.array(stored["o"]), "g": stored["g"], "k": stored["k"]}
            items += [{**base, "components": None}, {**base, "components": components}]
            keys += [(law, name, "deviance_baseline"), (law, name, "deviance_transfer")]
    worst = 0.0
    for (law, name, key), refit in zip(keys, ordered_map(fit, items, min_items=1), strict=True):
        gap = abs(refit["deviance"] / recorded[law][name][key] - 1.0)
        worst = max(worst, gap)
        print(f"{law} {name} {key}: recorded {recorded[law][name][key]:.6f}, refit {refit['deviance']:.6f}")
    print(f"largest relative difference {worst:.3e}")
    if worst > 1e-5:
        raise SystemExit("a refit deviance departs from the recorded one")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    mode = parser.add_mutually_exclusive_group(required=True)
    for flag in ("--self-test", "--extract", "--input", "--check"):
        mode.add_argument(flag, action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.extract:
        if len(args.paths) != 1:
            raise SystemExit("usage: mesh_model_jobs.py --extract INPUT.json")
        Path(args.paths[0]).write_text(json.dumps(extract(), allow_nan=False) + "\n", encoding="utf-8")
        return 0
    if len(args.paths) != 2:
        raise SystemExit("usage: mesh_model_jobs.py --input | --check INPUT.json OUT.json")
    content = Path(args.paths[0]).read_bytes()
    found, digest = json.loads(content), hashlib.sha256(content).hexdigest()
    if args.check:
        return check(found, digest, json.loads(Path(args.paths[1]).read_text(encoding="utf-8")))
    Path(args.paths[1]).write_text(json.dumps(run(found, digest), indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
