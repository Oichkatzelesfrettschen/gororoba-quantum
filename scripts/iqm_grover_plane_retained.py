"""Retained Garnet Grover acquisitions read through the plane model: engine checks, per-run fits, joint fits, the
depth-4
prediction and the calibration priors, written to docs/evidence/iqm-garnet-grover-plane/fits.json.

Every fit reads the readout-corrected marked probability of an arm (grover_line_analysis.Readout, the shared reader
iqm_records.read_run underneath) against grover_plane_sim.Response of the run's own circuits and calibration copy,
with the
excess parameters of the plane family: a (depth-independent factor on P - 1/8), s (global depolarizing factor per
iteration) and eps (plane rotation per iteration, radians). A fit with as many parameters as points leaves no residual.

Usage: "$PYTHON" scripts/iqm_grover_plane_retained.py --out docs/evidence/iqm-garnet-grover-plane/fits.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402

import grover_line_analysis as gla  # noqa: E402
import grover_plane as plane  # noqa: E402
import grover_plane_calibration as calibration  # noqa: E402
import grover_plane_sim as sim  # noqa: E402

RUNS = {
    "line-ccz": ROOT / "results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover",
    "depth": ROOT / "results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover",
}
MARKS = ("101", "011")
CASE = ROOT / "results/iqm/cases/grover-plane-mirrored"
BOX = {"a": (0.3, 1.3), "s": (0.3, 1.3), "eps": (-0.3, 0.3)}


def points_of(run: str) -> tuple[Any, dict[str, list[dict[str, Any]]]]:
    d = RUNS[run]
    acquisition = gla.read_acquisition(d)
    readout = gla.Readout(acquisition)
    cal = iqm_sim.Calibration.from_directory(d / "calibration")
    path = [str(q) for q in (acquisition.prediction.get("path") or acquisition.prediction.get("forward_path") or [])]
    out: dict[str, list[dict[str, Any]]] = {}
    for mark in MARKS:
        rows = []
        circuits = {}
        for k in (1, 2, 3):
            base = f"m{mark}-k{k}"
            names = [n for n in acquisition.names if n == base or n.startswith(base + "-c")]
            if not names:
                continue
            value, grad_p, grad_a = readout.marked(base, mark)
            circuits[k] = json.loads((d / "circuits" / f"{sorted(names)[0]}.json").read_text(encoding="utf-8"))
            rows.append({"k": k, "p": value, "se": math.sqrt(readout.variance(grad_p, grad_a)), "copies": len(names)})
        response = sim.Response(circuits, cal, path, mark, readout=False)
        depths = [int(r["k"]) for r in rows]
        model = response.probabilities(1.0, 1.0, 0.0)
        for row in rows:
            row["model_p"] = float(model[depths.index(int(row["k"]))])
        out[mark] = [{**r, "response": response} for r in rows]
    return cal, out


def solve(
    groups: list[tuple[Any, list[dict[str, Any]]]], free: list[str], x0: list[float], spec: Any
) -> dict[str, Any]:
    """Least squares over the points of the groups; spec(x) returns per-group (a, s, eps)."""

    def residual(x: np.ndarray) -> np.ndarray:
        out = []
        for g, (_, rows) in enumerate(groups):
            a, s, e = spec(x, g)
            r = rows[0]["response"].probabilities(a, s, e)
            for row in rows:
                out.append((row["p"] - r[row["k"] - 1]) / row["se"])
        return np.array(out)

    lo = [BOX[n.split(":")[0]][0] for n in free]
    hi = [BOX[n.split(":")[0]][1] for n in free]
    best = None
    for start in x0:
        r = optimize.least_squares(
            residual,
            [start if n.startswith("eps") else (1.0 if n.startswith("a") else 0.97) for n in free],
            bounds=(lo, hi),
            xtol=1e-12,
            ftol=1e-12,
        )
        if best is None or r.cost < best.cost:
            best = r
    if best is None:
        raise ValueError("no start")
    try:
        sd = np.sqrt(np.diag(np.linalg.inv(best.jac.T @ best.jac)))
    except np.linalg.LinAlgError:
        sd = np.full(len(free), float("nan"))
    count = sum(len(rows) for _, rows in groups)
    return {
        "chi2": 2 * best.cost,
        "dof": count - len(free),
        "params": {n: float(v) for n, v in zip(free, best.x, strict=True)},
        "sd": {n: float(v) for n, v in zip(free, sd, strict=True)},
    }


def per_run_fits(data: dict[str, dict[str, list[dict[str, Any]]]]) -> list[dict[str, Any]]:
    rows = []
    for run, marks in data.items():
        for mark, pts in marks.items():
            group = [(None, pts)]
            n = len(pts)
            fits: dict[str, Any] = {}
            for label, free in (
                ("geometric_a_s", ["a", "s"]),
                ("rotation_a_s_eps", ["a", "s", "eps"]),
                ("rotation_s_eps", ["s", "eps"]),
                ("geometric_s", ["s"]),
            ):
                if len(free) > n:
                    continue

                def spec(x: np.ndarray, g: int, free: list[str] = free) -> tuple[float, float, float]:
                    v = dict(zip(free, x, strict=True))
                    return v.get("a", 1.0), v.get("s", 1.0), v.get("eps", 0.0)

                fits[label] = solve(group, free, [-0.03, 0.03] if "eps" in free else [0.0], spec)
            rows.append(
                {
                    "run": run,
                    "mark": mark,
                    "points": [{k: r[k] for k in ("k", "p", "se", "model_p", "copies")} for r in pts],
                    "fits": fits,
                }
            )
    return rows


def joint_fits(data: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    groups = [(f"{run}/{mark}", pts) for run, marks in data.items() for mark, pts in marks.items()]
    keys = [g[0] for g in groups]
    marks = sorted({k.split("/")[1] for k in keys})
    out: dict[str, Any] = {"groups": keys}
    for label, s_per_mark, e_mode in (
        ("a per group, s shared, no rotation", False, "none"),
        ("a per group, s per mark, no rotation", True, "none"),
        ("a per group, s shared, one rotation", False, "shared"),
        ("a per group, s shared, rotation per mark", False, "mark"),
        ("a per group, s per mark, rotation per mark", True, "mark"),
    ):
        free = [f"a:{k}" for k in keys] + ([f"s:{m}" for m in marks] if s_per_mark else ["s"])
        free += {"none": [], "shared": ["eps"], "mark": [f"eps:{m}" for m in marks]}[e_mode]

        def spec(
            x: np.ndarray, g: int, free: list[str] = free, s_per_mark: bool = s_per_mark, e_mode: str = e_mode
        ) -> tuple[float, float, float]:
            v = dict(zip(free, x, strict=True))
            mark = keys[g].split("/")[1]
            s = v[f"s:{mark}"] if s_per_mark else v["s"]
            e = 0.0 if e_mode == "none" else v["eps"] if e_mode == "shared" else v[f"eps:{mark}"]
            return v[f"a:{keys[g]}"], s, e

        out[label] = solve(groups, free, [-0.03, 0.03] if e_mode != "none" else [0.0], spec)
    return out


def continuation(data: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    """Depth-4 marked probability of the case's calibration under eps = 0 and under the fitted eps, from the retained
    depth run at mark 101 (three points), with the 64 Sobol' draws of the three retained probabilities propagated."""
    pts = data["depth"]["101"]
    cal = iqm_sim.Calibration.from_directory(CASE / "calibration")
    circuits = {
        k: json.loads(next((CASE / "circuits").glob(f"m101-k{k}-c0.json")).read_text(encoding="utf-8"))
        for k in (1, 2, 3, 4)
    }
    case_response = sim.Response(circuits, cal, ["QB20", "QB16", "QB17"], "101", readout=False)
    ideal4 = plane.ideal_probability(4)
    draws = calibration.sobol_normals(len(pts), 6)
    result: dict[str, Any] = {}
    for label, free in (("geometric", ["a", "s"]), ("rotation", ["a", "s", "eps"])):
        values = []
        for z in [np.zeros(len(pts)), *draws]:
            moved = [{**r, "p": r["p"] + zi * r["se"]} for r, zi in zip(pts, z, strict=True)]

            def spec(x: np.ndarray, g: int, free: list[str] = free) -> tuple[float, float, float]:
                v = dict(zip(free, x, strict=True))
                return v.get("a", 1.0), v.get("s", 1.0), v.get("eps", 0.0)

            fit = solve([(None, moved)], free, [-0.03, 0.03] if "eps" in free else [0.0], spec)
            a, s, e = spec(np.array([fit["params"][n] for n in free]), 0)
            values.append((case_response.probabilities(a, s, e)[3], fit["params"]))
        p = np.array([v[0] for v in values])
        lam = (p - 1 / 8) / (ideal4 - 1 / 8)
        result[label] = {
            "p4_at_retained": float(p[0]),
            "p4_mean": float(p[1:].mean()),
            "p4_sd": float(p[1:].std(ddof=1)),
            "lambda4_at_retained": float(lam[0]),
            "lambda4_mean": float(lam[1:].mean()),
            "lambda4_sd": float(lam[1:].std(ddof=1)),
            "parameters_at_retained": values[0][1],
        }
    model = case_response.probabilities(1.0, 1.0, 0.0)[3]
    result["model"] = {"p4": float(model), "lambda4": float((model - 1 / 8) / (ideal4 - 1 / 8))}
    return result


def engine_checks(data_calibrations: dict[str, Any]) -> dict[str, Any]:
    import iqm_grover_line as grover

    out: dict[str, Any] = {}
    case = json.loads(
        (ROOT / "results/iqm/cases/grover-fourth-depth-mirrored/prediction.json").read_text(encoding="utf-8")
    )
    cal = iqm_sim.Calibration.from_directory(ROOT / "results/iqm/cases/grover-fourth-depth-mirrored/calibration")
    path = ["QB20", "QB16", "QB17"]
    worst = 0.0
    for name in ("m101-k1-c0", "m101-k2-c0", "m101-k3-c0", "m101-k4-c0", "ro-101", "ro-011"):
        circuit = json.loads(
            (ROOT / "results/iqm/cases/grover-fourth-depth-mirrored/circuits" / f"{name}.json").read_text(
                encoding="utf-8"
            )
        )
        steps, measured = sim.build_steps(circuit, cal, path, True)
        rho = np.zeros((1, 8, 8), dtype=complex)
        rho[0, 0, 0] = 1
        dist = sim.outcome_distribution(sim.apply_steps(steps, rho)[0], measured, path, cal)
        worst = max(
            worst,
            max(
                abs(dist[i] - case["arms"][name]["predicted"]["".join(str((i >> q) & 1) for q in range(3))])
                for i in range(8)
            ),
        )
    out["engine_against_prediction_json_max_abs"] = worst
    circuit4 = json.loads(
        (ROOT / "results/iqm/cases/grover-fourth-depth-mirrored/circuits/m101-k4-c0.json").read_text(encoding="utf-8")
    )
    ideal = sim.logical_frame(circuit4, cal, path, "101", 4, noisy=False)
    logical = [grover.logical_unitary(grover.grover_ops("101", j)) for j in range(5)]
    g = sim.conjugation(logical[1] @ logical[0].conj().T)
    out["ideal_channel_against_G_max_abs"] = max(float(np.abs(lam - g).max()) for lam in ideal["lambda"])
    noisy = sim.logical_frame(circuit4, cal, path, "101", 4, noisy=True)
    out["channel_2_3_4_equal_max_abs"] = max(
        float(np.abs(noisy["lambda"][1] - noisy["lambda"][j]).max()) for j in (2, 3)
    )
    closure = []
    for k in (1, 2, 3, 4):
        circuit = json.loads(
            (ROOT / f"results/iqm/cases/grover-fourth-depth-mirrored/circuits/m101-k{k}-c0.json").read_text(
                encoding="utf-8"
            )
        )
        arm = plane.arm_of(circuit, cal, path, "101", k)
        closure.append(
            {
                "k": k,
                "p_exact": arm.model_probability,
                "p_plane_affine": plane.probability(arm, 1.0, 1.0, 0.0),
                "lambda_error": plane.retention(arm, plane.probability(arm, 1.0, 1.0, 0.0))
                - plane.retention(arm, arm.model_probability),
            }
        )
    out["affine_closure_of_the_model"] = closure
    circuits = {
        k: json.loads(
            (ROOT / f"results/iqm/cases/grover-fourth-depth-mirrored/circuits/m101-k{k}-c0.json").read_text(
                encoding="utf-8"
            )
        )
        for k in (1, 2, 3, 4)
    }
    rows = []
    null = sim.Response(circuits, cal, path, "101", readout=False, noisy=False)
    for kind, key, values in (
        ("cz_phase_rad", "cz_phase", (-0.015, -0.03, -0.06, -0.1)),
        ("prx_amplitude", "prx_scale", (-0.008, -0.016, -0.03, -0.06)),
    ):
        for x in values:
            exact = sim.Response(circuits, cal, path, "101", readout=False, noisy=False, **{key: x}).probabilities(
                1.0, 1.0, 0.0
            )
            best = None
            for start in (-0.03, 0.03):
                r = optimize.least_squares(
                    lambda v, exact=exact: null.probabilities(v[0], v[1], v[2]) - exact,
                    [1.0, 1.0, start],
                    bounds=([0.3, 0.3, -0.3], [1.3, 1.3, 0.3]),
                    xtol=1e-14,
                    ftol=1e-14,
                )
                if best is None or r.cost < best.cost:
                    best = r
            if best is None:
                raise ValueError("no start")
            rows.append(
                {
                    "kind": kind,
                    "x": x,
                    "eps_fit": float(best.x[2]),
                    "s_fit": float(best.x[1]),
                    "a_fit": float(best.x[0]),
                    "max_abs_p_error": float(np.abs(null.probabilities(*best.x) - exact).max()),
                }
            )
    out["noise_free_coherent_responses_against_the_plane_family"] = rows
    return out


def priors() -> dict[str, Any]:
    cal = iqm_sim.Calibration.from_directory(CASE / "calibration")
    path = ["QB20", "QB16", "QB17"]
    out: dict[str, Any] = {"calibration_set": cal.set_id}
    out["cz_infidelity"] = {
        f"{a}-{b}": 1 - cal.cz[frozenset((a, b))] for a, b in ((path[0], path[1]), (path[1], path[2]))
    }
    out["prx_infidelity"] = {q: cal.prx_p(q) / 2 for q in path}
    out["t1_t2_microseconds"] = {
        q: [
            cal.values[f"characterization.model.{q}.t1_time"] * 1e6,
            cal.values[f"characterization.model.{q}.t2_time"] * 1e6,
        ]
        for q in path
    }
    out["coherent_infidelity_per_gate"] = {
        "cz_phase": "average-fidelity loss 0.3 (1 - cos x) of one CZ conditional-phase error x",
        "prx_amplitude": "average-fidelity loss (2/3) (1 - cos^2(theta x / 2)) of one rotation by theta (1 + x)",
        "cz_at_0.0286": 0.3 * (1 - math.cos(0.0286)),
        "prx_half_pi_at_0.0102": (2 / 3) * (1 - math.cos(math.pi / 4 * 0.0102) ** 2),
    }
    return out


def retained_contrast(per_run: list[dict[str, Any]], joint: dict[str, Any]) -> dict[str, Any]:
    """The mark contrast of the retained depth run, read post hoc: the exact three-point fits of marks 101 and 011
    and the eight-parameter joint fit, against a CZ phase (eps_011 = 0) and a PRX amplitude
    (eps_011 = ratio eps_101)."""
    import grover_plane_decision as decision

    ratio = json.loads((CASE / "prediction.json").read_text(encoding="utf-8"))["decisions"]["contrast"]["ratio_prx"]
    fits = {r["mark"]: r["fits"]["rotation_a_s_eps"] for r in per_run if r["run"] == "depth"}
    out: dict[str, Any] = {"post_hoc": True, "ratio_prx": ratio}
    out["depth_run_exact_fits"] = decision.contrast(
        fits["101"]["params"]["eps"],
        fits["101"]["sd"]["eps"],
        fits["011"]["params"]["eps"],
        fits["011"]["sd"]["eps"],
        ratio,
    )
    both = joint["a per group, s per mark, rotation per mark"]
    out["joint_fit_s_and_eps_per_mark"] = decision.contrast(
        both["params"]["eps:101"], both["sd"]["eps:101"], both["params"]["eps:011"], both["sd"]["eps:011"], ratio
    )
    return out


def close(a: Any, b: Any, tol: float = 1e-6) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b, strict=True))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return bool(abs(a - b) <= tol * max(1.0, abs(b)))
    return bool(a == b)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path, help="recompute and compare with this record to 1e-6 relative")
    args = parser.parse_args()
    data = {run: points_of(run)[1] for run in RUNS}
    per_run = per_run_fits(data)
    joint = joint_fits(data)
    record = {
        "schema": "iqm-garnet-grover-plane-fits-v1",
        "per_run": per_run,
        "joint": joint,
        "mark_contrast": retained_contrast(per_run, joint),
        "continuation_to_depth_4": continuation(data),
        "engine_checks": engine_checks({}),
        "priors": priors(),
    }
    text = json.dumps(record, indent=1, sort_keys=True, default=float) + "\n"
    if args.check is not None:
        if not close(json.loads(text), json.loads(args.check.read_text(encoding="utf-8"))):
            raise SystemExit(f"{args.check}: differs from the recomputed record")
        print(f"{args.check}: matches the recomputed record")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {k: record[k] for k in ("joint", "continuation_to_depth_4", "engine_checks")}, indent=1, default=float
        )[:6000]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
