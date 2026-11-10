"""Chip-level component model of the qpu:ascella interferometer, fitted to the two-click patterns of the CZ
tomography runs and tested by held-out prediction.

Every computed_circuit the service returned for the four tomography jobs (2026-10-31 retained pair, 2026-11-09 band
pair) decodes to one fixed 12-mode topology: 132 Rx couplers at calibrated angles that are identical in all 288
meshes, and 126 phase shifters whose values the transpiler sets per iteration. A setting is therefore the vector of
126 commanded phases, and a hardware error that belongs to a component is shared by every setting. The model:

* realized coupler angle theta_b + d_b (d_b per coupler, 132 parameters);
* realized phase phi_p + o_p + g phi_p + k sum of the commanded phases of the heaters on modes m - 1 and m + 1 in
  the neighbouring element columns (static offset o_p per heater, 126 parameters; global gain g and crosstalk k);
* one overlap M and twelve relative output-mode efficiencies w (w_0 = 1) per pair of runs, refitted on every pair
  of runs because they belong to the source and detectors of one acquisition window;
* photons on chip modes 0 and 2; the conditional law of the 66 two-click patterns over all twelve modes,
  q_ij proportional to w_i w_j (M |U_iA U_jB + U_jA U_iB|^2 + (1 - M)(|U_iA U_jB|^2 + |U_jA U_iB|^2)).
  Multiphoton emission and dark counts are omitted (g2 of 2 % moves an eligible share by about 1 %).

The per-component parameters carry a ridge penalty RIDGE * (sum d^2 / D_SCALE^2 + sum o^2 / O_SCALE^2) in units of
the negative log-likelihood. Fits run on all settings of the training runs; scores are deviances of held-out counts.

Preregistered test, fixed before the first fit to measured counts (the commit that adds this file precedes the
commit that adds its output):

* Baseline B: the ideal served mesh with M and w fitted on the held-out runs.
* Transfer T: the component errors fitted on the training runs, with M and w refitted on the held-out runs.
* Gain = (dev_B - dev_T) / (dev_B - dev_I), where I fits the component errors on the held-out runs themselves (the
  in-sample ceiling of the model class).
* Null: NULL_DRAWS draws of component errors with the fitted errors' RMS per class and random signs and order, scored
  like T.
* Within-calibration hold-out: train on retained job-00, test on retained job-01 (each setting appears in one job,
  so the test settings and meshes are new). Cross-pair hold-out: train on the retained pair, test on the band pair,
  and the reverse.
* Reading: a hold-out passes when Gain >= 0.3 and dev_T is below every null draw. Within passes and cross passes:
  static component errors carry the per-setting misfit across 2026-10-31 to 2026-11-09. Within passes and cross
  fails: the components moved between the pairs (recalibration). Within fails: the component model class does not
  carry the misfit, and the per-setting error is not a function of the commanded phases through these classes.

--self-test plants known component errors (coupler RMS 0.03 rad, heater offset RMS 0.05 rad, gain 0.01, crosstalk
0.004) in the served meshes of both pairs, draws counts with each setting's measured two-click total (seed:
draw-2026-11-09T020604Z.json index 210) and runs the retained-to-band hold-out on them. It requires gain and
crosstalk within 0.003 and 0.0015 of the planted values and a synthetic hold-out that passes with Gain >= 0.8, and
reports the correlation of planted and fitted per-component errors. That correlation stays below 1 because the
patterns of two photons entering modes 0 and 2 do not identify every component (a phase after the last coupler of a
mode, or on a mode no amplitude reaches, moves no pattern), and the ridge shrinks such components to zero; the
hold-out Gain is the quantity the measured test reads, so the self-test calibrates it.

Run from the repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/mesh_model.py --self-test`` or
``... mesh_model.py OUT.json``.
"""

from __future__ import annotations

import argparse
import importlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
for _path in ("scripts", "gororoba_quantum"):
    if str(ROOT / _path) not in sys.path:
        sys.path.insert(0, str(ROOT / _path))
AUDIT = importlib.import_module("photonic_compilation_audit")
RECORDS = importlib.import_module("qd_records")
TOMO = importlib.import_module("ascella_cz_tomography_case")
ordered_map = importlib.import_module("parallel").ordered_map

RUNS = {
    "retained-00": "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-00",
    "retained-01": "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-01",
    "band-00": "results/quandela/runs/2026-11-09T174125Z-qpu_ascella-ascella_cz_tomography_reference-job-00",
    "band-01": "results/quandela/runs/2026-11-09T175201Z-qpu_ascella-ascella_cz_tomography_reference-job-01",
}
MODES = 12
SOURCES = (0, 2)
PAIRS = list(itertools.combinations(range(MODES), 2))
RIDGE = 1.0
D_SCALE = 0.05  # rad: prior scale of a coupler angle error
O_SCALE = 0.10  # rad: prior scale of a heater offset
NULL_DRAWS = 20
DRAW = "docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json"
SELF_TEST_INDEX = 210
NULL_INDEX = 211
torch.set_default_dtype(torch.float64)


def draw_seed(index: int) -> int:
    return int(json.loads((ROOT / DRAW).read_text(encoding="utf-8"))["values"][index])


def load(run: str) -> dict[str, Any]:
    """Commanded phases, architecture and 66-pattern two-click counts of every iteration of one run."""
    raw = json.loads(json.loads((ROOT / run / "raw/result.json").read_text(encoding="utf-8"))["results"])
    record = RECORDS.read_run(ROOT / run)
    counts_by_seed = {}
    for entry in record.collected.get("iterations") or []:
        c = np.zeros(len(PAIRS))
        for key, count in (entry.get("counts") or {}).items():
            on = [m for m, v in enumerate(TOMO.parse_state(key)) if v]
            if len(on) == 2:
                c[PAIRS.index((on[0], on[1]))] += count
        counts_by_seed[entry["iteration"]["compilation_seed"]] = c
    arch, phases, counts, seeds = None, [], [], []
    for item in raw["results_list"]:
        elements = AUDIT._elements(item["computed_circuit"])
        shape = [(k, m, v if k == "bs" else None) for k, m, v in elements]
        if arch is None:
            arch = shape
        elif shape != arch:
            raise RuntimeError(f"{run}: a mesh departs from the fixed architecture")
        seed = item["iteration"]["compilation_seed"]
        phases.append([v for k, _, v in elements if k == "ps"])
        counts.append(counts_by_seed[seed])
        seeds.append(seed)
    return {"arch": arch, "phases": np.array(phases), "counts": np.array(counts), "seeds": seeds}


def neighbours(arch: list[Any]) -> np.ndarray:
    """Crosstalk matrix: heater q contributes to heater p when q sits on mode m(p) +- 1 in the same or an adjacent
    as-soon-as-possible element column."""
    depth = [0] * MODES
    where = []
    for kind, m, _ in arch:
        span = (m, m + 1) if kind == "bs" else (m,)
        column = max(depth[x] for x in span)
        for x in span:
            depth[x] = column + 1
        if kind == "ps":
            where.append((m, column))
    n = len(where)
    a = np.zeros((n, n))
    for p, (mp, cp) in enumerate(where):
        for q, (mq, cq) in enumerate(where):
            if abs(mp - mq) == 1 and abs(cp - cq) <= 1:
                a[p, q] = 1.0
    return a


class Mesh:
    def __init__(self, arch: list[Any]) -> None:
        self.arch = arch
        self.theta = torch.tensor([v[0] for k, _, v in arch if k == "bs"])
        if any(any(x != 0.0 for x in v[1:]) for k, _, v in arch if k == "bs"):
            raise RuntimeError("a coupler carries phases outside the Rx angle")
        self.cross = torch.tensor(neighbours(arch))
        self.nb = len(self.theta)
        self.np_ = sum(1 for k, _, _ in arch if k == "ps")

    def columns(self, phases: torch.Tensor, d: torch.Tensor, o: torch.Tensor, g: torch.Tensor, k: torch.Tensor):
        """Realized amplitudes U[:, A] and U[:, B] of the two source modes, shape (settings, modes, 2)."""
        s = phases.shape[0]
        realized = phases + o + g * phases + k * phases @ self.cross.T
        psi = torch.zeros((s, MODES, 2), dtype=torch.complex128)
        psi[:, SOURCES[0], 0] = 1.0
        psi[:, SOURCES[1], 1] = 1.0
        rows = list(psi.unbind(1))
        ib = ip = 0
        theta = self.theta + d
        for kind, m, _ in self.arch:
            if kind == "bs":
                c, sn = torch.cos(theta[ib] / 2), torch.sin(theta[ib] / 2)
                top, bottom = rows[m], rows[m + 1]
                rows[m] = c * top + 1j * sn * bottom
                rows[m + 1] = 1j * sn * top + c * bottom
                ib += 1
            else:
                rows[m] = rows[m] * torch.exp(1j * realized[:, ip])[:, None]
                ip += 1
        return torch.stack(rows, 1)


I_IDX = torch.tensor([i for i, _ in PAIRS])
J_IDX = torch.tensor([j for _, j in PAIRS])


def pattern_law(u: torch.Tensor, overlap: torch.Tensor, log_w: torch.Tensor) -> torch.Tensor:
    a, b = u[:, :, 0], u[:, :, 1]
    ai, aj, bi, bj = a[:, I_IDX], a[:, J_IDX], b[:, I_IDX], b[:, J_IDX]
    ind = (ai * bj + aj * bi).abs() ** 2
    dis = (ai * bj).abs() ** 2 + (aj * bi).abs() ** 2
    w = torch.exp(torch.cat([torch.zeros(1), log_w]))
    p = (overlap * ind + (1 - overlap) * dis) * w[I_IDX] * w[J_IDX]
    return p / p.sum(1, keepdim=True)


def nll(counts: torch.Tensor, law: torch.Tensor) -> torch.Tensor:
    return -(counts * torch.log(law.clamp_min(1e-300))).sum()


def deviance(counts: np.ndarray, law: np.ndarray) -> float:
    """2 sum n log(n / (N q)) over observed cells: the likelihood-ratio statistic against the saturated law."""
    n = counts
    expected = law * n.sum(1, keepdims=True)
    mask = n > 0
    return float(2.0 * (n[mask] * np.log(n[mask] / np.maximum(expected[mask], 1e-300))).sum())


def fit(
    mesh: Mesh,
    phases: np.ndarray,
    counts: np.ndarray,
    components: dict[str, torch.Tensor] | None = None,
    free_components: bool = True,
    iterations: int = 300,
) -> dict[str, Any]:
    """Maximum penalized likelihood. With free_components false, the component errors stay at ``components`` (zero
    when None) and only M and w move."""
    ph = torch.tensor(phases)
    n = torch.tensor(counts)
    zero = {"d": torch.zeros(mesh.nb), "o": torch.zeros(mesh.np_), "g": torch.zeros(()), "k": torch.zeros(())}
    start = {key: (components or zero)[key].detach().clone() for key in zero}
    comp = {key: value.requires_grad_(free_components) for key, value in start.items()}
    logit_m = torch.tensor(2.0, requires_grad=True)
    log_w = torch.zeros(MODES - 1, requires_grad=True)
    params = [logit_m, log_w] + (list(comp.values()) if free_components else [])
    opt = torch.optim.LBFGS(params, max_iter=iterations, line_search_fn="strong_wolfe", tolerance_grad=1e-9)

    def objective() -> torch.Tensor:
        u = mesh.columns(ph, comp["d"], comp["o"], comp["g"], comp["k"])
        value = nll(n, pattern_law(u, torch.sigmoid(logit_m), log_w))
        if free_components:
            value = value + RIDGE * ((comp["d"] / D_SCALE) ** 2).sum() + RIDGE * ((comp["o"] / O_SCALE) ** 2).sum()
        return value

    def closure() -> torch.Tensor:
        opt.zero_grad()
        value = objective()
        value.backward()
        return value

    opt.step(closure)
    with torch.no_grad():
        u = mesh.columns(ph, comp["d"], comp["o"], comp["g"], comp["k"])
        law = pattern_law(u, torch.sigmoid(logit_m), log_w).numpy()
    return {
        "overlap": float(torch.sigmoid(logit_m).detach()),
        "efficiency": [1.0] + [float(x) for x in torch.exp(log_w).detach()],
        "components": {key: value.detach() for key, value in comp.items()},
        "deviance": deviance(counts, law),
        "law": law,
    }


def summary(components: dict[str, torch.Tensor]) -> dict[str, Any]:
    return {
        "coupler_rms": float(components["d"].pow(2).mean().sqrt()),
        "heater_offset_rms": float(components["o"].pow(2).mean().sqrt()),
        "heater_gain": float(components["g"]),
        "crosstalk": float(components["k"]),
    }


def null_components(fitted: dict[str, torch.Tensor], rng: np.random.Generator) -> dict[str, torch.Tensor]:
    out = {}
    for key in ("d", "o"):
        v = fitted[key].numpy()
        out[key] = torch.tensor(rng.permutation(v) * rng.choice([-1.0, 1.0], size=v.shape))
    out["g"] = fitted["g"].clone()
    out["k"] = fitted["k"].clone()
    return out


def null_deviance(item: tuple[Mesh, np.ndarray, np.ndarray, dict[str, torch.Tensor]]) -> float:
    """The held-out deviance of one null draw of component errors, scored like the transfer fit. The unit
    parallel.ordered_map maps."""
    mesh, phases, counts, components = item
    return float(fit(mesh, phases, counts, components, free_components=False)["deviance"])


def holdout(mesh: Mesh, train: dict[str, Any], test: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    trained = fit(mesh, train["phases"], train["counts"])
    baseline = fit(mesh, test["phases"], test["counts"], free_components=False)
    transfer = fit(mesh, test["phases"], test["counts"], trained["components"], free_components=False)
    ceiling = fit(mesh, test["phases"], test["counts"])
    # The shared generator draws every null in order; the refits then map. The four hold-outs of main stay in
    # sequence because each one's draws follow its own trained fit.
    draws = [null_components(trained["components"], rng) for _ in range(NULL_DRAWS)]
    nulls = ordered_map(null_deviance, [(mesh, test["phases"], test["counts"], d) for d in draws], min_items=1)
    span = baseline["deviance"] - ceiling["deviance"]
    gain = (baseline["deviance"] - transfer["deviance"]) / span if span > 0 else float("nan")
    resid = {}
    for name, f in (("baseline", baseline), ("transfer", transfer)):
        resid[name] = (test["counts"] - f["law"] * test["counts"].sum(1, keepdims=True)) / np.sqrt(
            np.maximum(f["law"] * test["counts"].sum(1, keepdims=True), 1.0)
        )
    ceiling_resid = (test["counts"] - ceiling["law"] * test["counts"].sum(1, keepdims=True)) / np.sqrt(
        np.maximum(ceiling["law"] * test["counts"].sum(1, keepdims=True), 1.0)
    )
    predicted_shift = (transfer["law"] - baseline["law"]).ravel()
    observed_shift = (test["counts"] / test["counts"].sum(1, keepdims=True) - baseline["law"]).ravel()
    return {
        "train_settings": int(len(train["counts"])),
        "test_settings": int(len(test["counts"])),
        "train": {"overlap": trained["overlap"], "deviance": trained["deviance"], **summary(trained["components"])},
        "deviance_baseline": baseline["deviance"],
        "deviance_transfer": transfer["deviance"],
        "deviance_in_sample_ceiling": ceiling["deviance"],
        "deviance_null": {"min": float(min(nulls)), "median": float(np.median(nulls)), "max": float(max(nulls))},
        "gain": gain,
        "passes": bool(gain >= 0.3 and transfer["deviance"] < min(nulls)),
        "overlap": {"baseline": baseline["overlap"], "transfer": transfer["overlap"], "ceiling": ceiling["overlap"]},
        "ceiling_components": summary(ceiling["components"]),
        "shift_correlation": float(np.corrcoef(predicted_shift, observed_shift)[0, 1]),
        "pearson": {
            "baseline": float((resid["baseline"] ** 2).sum()),
            "transfer": float((resid["transfer"] ** 2).sum()),
            "ceiling": float((ceiling_resid**2).sum()),
        },
        "cells": int(test["counts"].size),
    }


def stack(parts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "phases": np.concatenate([p["phases"] for p in parts]),
        "counts": np.concatenate([p["counts"] for p in parts]),
    }


def self_test() -> int:
    data = {key: load(run) for key, run in RUNS.items()}
    mesh = Mesh(data["retained-00"]["arch"])
    rng = np.random.default_rng(draw_seed(SELF_TEST_INDEX))
    truth = {
        "d": torch.tensor(rng.normal(0.0, 0.03, mesh.nb)),
        "o": torch.tensor(rng.normal(0.0, 0.05, mesh.np_)),
        "g": torch.tensor(0.01),
        "k": torch.tensor(0.004),
    }

    def synthetic(parts: list[dict[str, Any]], overlap: float) -> dict[str, Any]:
        both = stack(parts)
        with torch.no_grad():
            u = mesh.columns(torch.tensor(both["phases"]), truth["d"], truth["o"], truth["g"], truth["k"])
            law = pattern_law(u, torch.tensor(overlap), torch.tensor(rng.normal(0.0, 0.1, MODES - 1))).numpy()
        totals = both["counts"].sum(1).astype(int)
        drawn = np.array([rng.multinomial(t, p / p.sum()) for t, p in zip(totals, law, strict=True)], dtype=float)
        return {"phases": both["phases"], "counts": drawn}

    train = synthetic([data["retained-00"], data["retained-01"]], 0.93)
    test = synthetic([data["band-00"], data["band-01"]], 0.92)
    fitted = fit(mesh, train["phases"], train["counts"])
    result = holdout(mesh, train, test, rng)
    report = {
        "coupler_correlation": float(np.corrcoef(truth["d"].numpy(), fitted["components"]["d"].numpy())[0, 1]),
        "heater_offset_correlation": float(np.corrcoef(truth["o"].numpy(), fitted["components"]["o"].numpy())[0, 1]),
        "fitted": summary(fitted["components"]),
        "overlap": fitted["overlap"],
        "holdout": result,
    }
    print(json.dumps(report, indent=1))
    if abs(report["fitted"]["heater_gain"] - 0.01) > 0.003 or abs(report["fitted"]["crosstalk"] - 0.004) > 0.0015:
        raise SystemExit("self-test: the fit does not recover the planted gain and crosstalk")
    if not (result["passes"] and result["gain"] >= 0.8):
        raise SystemExit("self-test: planted static components do not pass the hold-out")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.out:
        raise SystemExit("usage: mesh_model.py --self-test | OUT.json")
    data = {key: load(run) for key, run in RUNS.items()}
    archs = {json.dumps(d["arch"]) for d in data.values()}
    if len(archs) != 1:
        raise RuntimeError("the four runs do not share one architecture")
    mesh = Mesh(data["retained-00"]["arch"])
    rng = np.random.default_rng(draw_seed(NULL_INDEX))
    retained = stack([data["retained-00"], data["retained-01"]])
    band = stack([data["band-00"], data["band-01"]])
    out = {
        "schema": "ascella-mesh-component-model-v1",
        "architecture": {"couplers": mesh.nb, "heaters": mesh.np_, "crosstalk_links": int(mesh.cross.sum())},
        "within_retained": holdout(mesh, data["retained-00"], data["retained-01"], rng),
        "within_band": holdout(mesh, data["band-00"], data["band-01"], rng),
        "retained_to_band": holdout(mesh, retained, band, rng),
        "band_to_retained": holdout(mesh, band, retained, rng),
        "seeds": draw_seed(NULL_INDEX),
    }
    Path(args.out).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
