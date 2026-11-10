"""The g2 component model of mesh_model_jobs.py with the source figures fitted, a post-data diagnostic of whether a
source law that fits its own figures leaves a transferable component error.

mesh_model_jobs.py's g2 law holds g2, the transmittance T and the twelve per-attempt dark-click probabilities at the
pair's plan read. Under it the transferred components predict nothing beyond the ideal mesh (mesh-model-jobs.json:
Gain -0.39 to 0.04), while the two-photon law's transfer survives every hold-out. A plan read that misstates the
source would leave the g2 law's residual to the components and could hide or fake a transfer either way. Here every
fit, component and fixed-component alike, also fits the multiphoton probability p2 (0.4 times a logistic; g2 =
2 p2 / (1 + p2)^2) and one multiplier per mode on the plan read's dark rates, started at the plan read; one set of
figures per fitting set, shared by its jobs. T stays at the plan read: the conditional pattern law sees it only
through the ratio of dark clicks to detected photons and through 1 - T, about 0.94, so a free T trades with the dark
rates (measured in this file's self-test with T free: the refit drove T to 4e-12 and most dark rates to zero at a
likelihood above the drawn figures'). The law is mesh_model_jobs.pattern_law with those
figures as tensors, and every other part of the fit, the four hold-outs, the 100 null draws, the three starts, the
optimizer rounds and Gain, Gain over the null median and rank p, are mesh_model_jobs.py's, run under the g2 law
alone. Beside them, an ideal-mesh fit of every set records its fitted figures against the plan read.

Reading, stated before the run (post-data, it decides no preregistered conjecture): mesh_model_jobs.py's survive rule
applied per hold-out. All four survive, a transferable component error exists under a source law that fits its own
figures, and the g2 null of mesh-model-jobs.json came from the plan read; none survives with the within-pair
transfers at or above their baselines, the null transfer stands with the source figures free.

--self-test checks this law at the plan figures against mesh_model_jobs.pattern_law on the retained pair's
commanded phases with random component errors (largest difference 1e-12), and refits counts drawn from the
ideal-mesh law at shifted figures (g2 0.03, dark 2 times the band read), requiring the refit's NLL at or below the
NLL at the drawn figures and its g2 within 0.005 of 0.03.

Seeds, docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json: index 224 the null draws, 225 the restarts, 226 the
self-test. Run from the repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/g2_free_source.py
--self-test`` or ``... g2_free_source.py INPUT.json OUT.json`` with INPUT.json mesh-model-jobs-input.json.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
NULL_INDEX = 224
RESTART_INDEX = 225
SELF_TEST_INDEX = 226
P2_CEILING = 0.4


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


MJ = sibling("mesh_model_jobs")
MM = MJ.MM
I_IDX, J_IDX, cross = MJ.I_IDX, MJ.J_IDX, MJ.cross
torch.set_default_dtype(torch.float64)


def free_law(
    u: torch.Tensor,
    overlap: torch.Tensor,
    log_w: torch.Tensor,
    job: torch.Tensor,
    t: torch.Tensor,
    p2: torch.Tensor,
    dark: torch.Tensor,
) -> torch.Tensor:
    """mesh_model_jobs.pattern_law's g2 branch with T, p2 and the dark rates as tensors."""
    a, b = u[:, :, 0], u[:, :, 1]
    a2, b2 = a.abs() ** 2, b.abs() ** 2
    ind = (a[:, I_IDX] * b[:, J_IDX] + a[:, J_IDX] * b[:, I_IDX]).abs() ** 2
    pair = overlap * ind + (1 - overlap) * cross(a2, b2)
    lost = 1.0 - t
    p1 = 1.0 - p2
    same = (1 + overlap) * a2 * b2
    two = p1 * p1 * t * t * pair
    one = p1 * p1 * (t * lost * (a2 + b2) + t * t * same)
    for n in (a2, b2):
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


def figures(raw: dict[str, torch.Tensor], plan: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    t = torch.tensor(float(plan["transmittance"]))
    p2 = P2_CEILING * torch.sigmoid(raw["p2"])
    dark = torch.tensor(plan["dark"]) * torch.exp(raw["dark"])
    return t, p2, dark


def start_figures(plan: dict[str, Any]) -> dict[str, torch.Tensor]:
    p2 = MJ.emission(float(plan["g2"]))
    return {
        "p2": torch.tensor(float(np.log(p2 / (P2_CEILING - p2))), requires_grad=True),
        "dark": torch.zeros(MM.MODES, requires_grad=True),
    }


def free_fit(item: dict[str, Any]) -> dict[str, Any]:
    """mesh_model_jobs.fit under the g2 law with the source figures free. Installed as mesh_model_jobs.fit at
    import, so mesh_model_jobs.evaluate and every worker of its pool fit with it."""
    if item["law"] != "g2":
        raise RuntimeError("g2_free_source.py fits the g2 law only")
    mesh = MM.Mesh(item["arch"])
    data, free, perms = item["data"], item["free"], item.get("perms")
    ph, n = torch.tensor(data["phases"]), torch.tensor(data["counts"])
    job = torch.as_tensor(data["job"])
    jobs = int(job.max()) + 1
    plan = data["source"]
    given = item.get("start") if free else item.get("components")
    zero = {"d": np.zeros(mesh.nb), "o": np.zeros(mesh.np_), "g": 0.0, "k": 0.0}
    comp = {key: torch.tensor((given or zero)[key], dtype=torch.float64).requires_grad_(free) for key in zero}
    logit_m = torch.tensor(2.0, requires_grad=True)
    log_w = torch.zeros((jobs, MM.MODES - 1), requires_grad=True)
    raw = start_figures(plan)
    params = [logit_m, log_w, *raw.values()] + (list(comp.values()) if free else [])
    opt = torch.optim.LBFGS(
        params,
        max_iter=MJ.ROUND_ITERATIONS,
        max_eval=MJ.ROUND_EVALUATIONS,
        line_search_fn="strong_wolfe",
        tolerance_grad=1e-9,
    )

    def law_now() -> torch.Tensor:
        return free_law(MJ.columns(mesh, ph, comp, perms), torch.sigmoid(logit_m), log_w, job, *figures(raw, plan))

    def objective() -> torch.Tensor:
        value = MM.nll(n, law_now())
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
    for _ in range(MJ.ROUNDS):
        opt.step(closure)
        state = opt.state[params[0]]
        ended_early = (
            state["n_iter"] - done < MJ.ROUND_ITERATIONS and state["func_evals"] - evaluated < MJ.ROUND_EVALUATIONS
        )
        done, evaluated = state["n_iter"], state["func_evals"]
        if ended_early:
            break
    final = closure()
    gradient = max(float(p.grad.abs().max()) for p in params if p.grad is not None)
    with torch.no_grad():
        law = law_now().numpy()
        t, p2, dark = figures(raw, plan)
    out = {
        "overlap": float(torch.sigmoid(logit_m).detach()),
        "weights": [[1.0] + [float(x) for x in row] for row in torch.exp(log_w).detach()],
        "components": {key: value.detach().numpy().copy() for key, value in comp.items()},
        "objective": float(final.detach()),
        "deviance": MM.deviance(data["counts"], law),
        "source_fit": {
            "transmittance": float(t),
            "p2": float(p2),
            "g2": float(2 * p2 / (1 + p2) ** 2),
            "dark_over_plan": [float(v) for v in torch.exp(raw["dark"]).detach()],
            "dark": [float(v) for v in dark],
        },
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


MJ.fit = free_fit


def self_test() -> int:
    rng = np.random.default_rng(MM.draw_seed(SELF_TEST_INDEX))
    found = json.loads((HERE / "mesh-model-jobs-input.json").read_text(encoding="utf-8"))
    arch, sets = MJ.assemble(found)
    mesh = MM.Mesh(arch)
    data = sets["retained"]
    comp = {
        "d": torch.tensor(rng.normal(0.0, 0.03, mesh.nb)),
        "o": torch.tensor(rng.normal(0.0, 0.05, mesh.np_)),
        "g": torch.tensor(0.003),
        "k": torch.tensor(0.001),
    }
    with torch.no_grad():
        u = MJ.columns(mesh, torch.tensor(data["phases"]), comp, None)
        job = torch.as_tensor(data["job"])
        log_w = torch.tensor(rng.normal(0.0, 0.05, (2, MM.MODES - 1)))
        overlap = torch.tensor(0.93)
        plan = data["source"]
        raw = start_figures(plan)
        mine = free_law(u, overlap, log_w, job, *figures(raw, plan))
        theirs = MJ.pattern_law(u, overlap, log_w, job, plan)
    gap = float((mine - theirs).abs().max())
    print(f"law at the plan figures: largest difference {gap:.3e}")
    if gap > 1e-12:
        raise SystemExit("self-test: the free-figure law departs from mesh_model_jobs.pattern_law")
    band = sets["band-00"]
    plan = band["source"]
    shifted = {
        "transmittance": float(plan["transmittance"]),
        "g2": 0.03,
        "dark": [2.0 * v for v in plan["dark"]],
    }
    with torch.no_grad():
        u = MJ.columns(mesh, torch.tensor(band["phases"]), {k: torch.zeros_like(v) for k, v in comp.items()}, None)
        job = torch.as_tensor(band["job"])
        truth = MJ.pattern_law(u, overlap, torch.zeros((1, MM.MODES - 1)), job, shifted).numpy()
    totals = band["counts"].sum(1).astype(int)
    drawn = np.array([rng.multinomial(total, row / row.sum()) for total, row in zip(totals, truth, strict=True)])
    synthetic = {**band, "counts": drawn.astype(float)}
    refit = free_fit({"arch": arch, "data": synthetic, "law": "g2", "free": False, "components": None})
    at_truth = float(MM.nll(torch.tensor(drawn, dtype=torch.float64), torch.tensor(truth)))
    print(
        json.dumps(
            {
                "drawn": shifted | {"dark": "2 x plan"},
                "refit": refit["source_fit"] | {"dark": None},
                "nll_refit": refit["objective"],
                "nll_at_drawn_figures": at_truth,
                "status": refit["status"],
            },
            indent=1,
        )
    )
    if refit["objective"] > at_truth + 1e-6:
        raise SystemExit("self-test: the refit does not reach the likelihood of the drawn figures")
    if abs(refit["source_fit"]["g2"] - 0.03) > 0.005:
        raise SystemExit("self-test: the refit does not recover the drawn g2")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        raise SystemExit("usage: g2_free_source.py --self-test | INPUT.json OUT.json")
    content = Path(argv[0]).read_bytes()
    found = json.loads(content)
    arch, sets = MJ.assemble(found)
    null_rng = np.random.default_rng(MM.draw_seed(NULL_INDEX))
    restart_rng = np.random.default_rng(MM.draw_seed(RESTART_INDEX))
    out = MJ.evaluate(arch, sets, MJ.HOLDOUTS, ("g2",), MJ.NULL_DRAWS, MJ.RESTARTS, null_rng, restart_rng)
    names = sorted(sets)
    ideal = MJ.ordered_map(
        free_fit, [{"arch": arch, "data": sets[name], "law": "g2", "free": False} for name in names], min_items=1
    )
    out["ideal_mesh_source_fit"] = {
        name: {"plan": sets[name]["source"], "fit": entry["source_fit"], "deviance": entry["deviance"]}
        for name, entry in zip(names, ideal, strict=True)
    }
    out["input_sha256"] = hashlib.sha256(content).hexdigest()
    out["seed_indices"] = {"nulls": NULL_INDEX, "restarts": RESTART_INDEX}
    out["versions"] = {"numpy": np.__version__, "torch": torch.__version__}
    Path(argv[1]).write_text(json.dumps(out, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
