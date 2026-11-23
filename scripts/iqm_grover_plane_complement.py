"""The retained Garnet Grover acquisitions read with all eight outcome cells, under a uniform and under nonuniform
fixed points of the excess contraction (grover_plane_complement), written to
docs/evidence/iqm-garnet-grover-plane/complement.json.

The plane family of fits.json reads only the marked cell and sends the leaked weight to the uniform state. The unmarked
cells of the same circuits reject that (the retained depth run: unmarked-uniformity Wald statistic 95.7 on 6 degrees of
freedom). Here every depth's readout-corrected eight-cell distribution
(grover_line_analysis.Readout.corrected_covariance,
delta-method covariance of the counts and the assignment matrix, the depths independent) is fitted with a per group
(run, mark) offset a, a per mark contraction s and a per mark plane rotation eps, and the fixed point Sigma of the
contraction is the uniform state, the S3-invariant sector of the marked vertex (three weights per mark) or a product of
per-qubit populations (three, shared by both marks). The marked-cell-only fit with the uniform state reproduces the
plane family of fits.json and calibrates this reader.

Usage: "$PYTHON" scripts/iqm_grover_plane_complement.py --out docs/evidence/iqm-garnet-grover-plane/complement.json
       "$PYTHON" scripts/iqm_grover_plane_complement.py --check docs/evidence/iqm-garnet-grover-plane/complement.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize, stats

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402

import grover_line_analysis as gla  # noqa: E402
import grover_plane_complement as cx  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "iqm-grover-plane-complement-v1"
RUNS = {
    "line-ccz": ROOT / "results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover",
    "depth": ROOT / "results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover",
}
MARKS = ("101", "011")
BOX = {"a": (0.3, 1.3), "s": (0.3, 1.3), "eps": (-0.3, 0.3)}
# fixed-point models: none is the uniform state; shells and qubits are the nonuniform forms; free is every cell
MODELS = {
    "marked_uniform": {"sigma": "uniform", "cells": "marked"},
    "marked_uniform_eps": {"sigma": "uniform", "cells": "marked", "eps": True},
    "uniform": {"sigma": "uniform", "cells": "all"},
    "uniform_eps": {"sigma": "uniform", "cells": "all", "eps": True},
    "shells": {"sigma": "shells", "cells": "all"},
    "shells_eps": {"sigma": "shells", "cells": "all", "eps": True},
    "qubits": {"sigma": "qubits", "cells": "all"},
    "qubits_eps": {"sigma": "qubits", "cells": "all", "eps": True},
    "free": {"sigma": "free", "cells": "all"},
    "free_eps": {"sigma": "free", "cells": "all", "eps": True},
}
STARTS = (-0.03, 0.0, 0.04)
PHI = 1.54  # the 95 % upper bound of the retained copies' dispersion (grover_plane_decision.PHI)


def load_groups() -> list[dict[str, Any]]:
    """One group per (run, mark): the FullResponse of the run's circuits and calibration copy and, per depth, the
    corrected eight-cell frequencies with their covariance."""
    groups = []
    for run, directory in RUNS.items():
        acquisition = gla.read_acquisition(directory)
        readout = gla.Readout(acquisition)
        cal = iqm_sim.Calibration.from_directory(directory / "calibration")
        path = [
            str(q) for q in (acquisition.prediction.get("path") or acquisition.prediction.get("forward_path") or [])
        ]
        for mark in MARKS:
            circuits, arms = {}, []
            for k in (1, 2, 3):
                base = f"m{mark}-k{k}"
                names = readout.copies(base)
                if not names:
                    continue
                circuits[k] = json.loads(
                    (directory / "circuits" / f"{sorted(names)[0]}.json").read_text(encoding="utf-8")
                )
                q, cov = readout.corrected_covariance(base)
                arms.append({"k": k, "q": q, "cov": cov, "copies": len(names)})
            response = cx.FullResponse(circuits, cal, path, mark)
            groups.append({"run": run, "mark": mark, "response": response, "arms": arms})
    return groups


def whiteners(groups: list[dict[str, Any]], cells: str) -> None:
    """Attach to every arm the cells it fits (the marked cell, or seven of the eight: the eighth is their complement)
    and the inverse Cholesky factor of their covariance."""
    for g in groups:
        m = g["response"].marked
        for arm in g["arms"]:
            idx = [m] if cells == "marked" else [i for i in range(8) if i != 7]
            arm[f"idx_{cells}"] = idx
            sub = arm["cov"][np.ix_(idx, idx)]
            arm[f"white_{cells}"] = np.linalg.inv(np.linalg.cholesky(sub))


class Layout:
    """The parameter vector of a model: names, bounds, starts and the map to (a, s, eps, Sigma) per group."""

    def __init__(self, groups: list[dict[str, Any]], spec: dict[str, Any], eps0: float) -> None:
        self.groups, self.spec = groups, spec
        self.names: list[str] = []
        self.low: list[float] = []
        self.high: list[float] = []
        self.start: list[float] = []

        def add(name: str, lo: float, hi: float, x0: float) -> None:
            self.names.append(name)
            self.low.append(lo)
            self.high.append(hi)
            self.start.append(x0)

        for g in groups:
            add(f"a:{g['run']}:{g['mark']}", *BOX["a"], 1.0)
        for mark in MARKS:
            add(f"s:{mark}", *BOX["s"], 0.97)
        if spec.get("eps"):
            for mark in MARKS:
                add(f"eps:{mark}", *BOX["eps"], eps0)
        kind = spec["sigma"]
        if kind == "shells":
            for mark in MARKS:
                for i, x0 in enumerate((0.0, math.log(3.0), math.log(3.0))):
                    add(f"shell:{mark}:{i}", -8.0, 8.0, x0)
        elif kind == "qubits":
            for q in range(3):
                add(f"qubit:{q}", -4.0, 4.0, 0.0)
        elif kind == "free":
            for mark in MARKS:
                for i in range(7):
                    add(f"free:{mark}:{i}", -8.0, 8.0, 0.0)

    def sigma(self, x: np.ndarray, mark: str, marked: int) -> np.ndarray:
        kind = self.spec["sigma"]
        val = dict(zip(self.names, x, strict=True))
        if kind == "uniform":
            return cx.sigma_uniform()
        if kind == "qubits":
            return cx.sigma_qubits(tuple(1 / (1 + math.exp(-val[f"qubit:{q}"])) for q in range(3)))  # type: ignore[arg-type]
        count = 3 if kind == "shells" else 7
        logits = np.array([val[f"{kind[:5] if kind == 'shells' else 'free'}:{mark}:{i}"] for i in range(count)] + [0.0])
        w = np.exp(logits - logits.max())
        w /= w.sum()
        if kind == "free":
            return np.asarray(w)
        return cx.sigma_shells((float(w[0]), float(w[1]), float(w[2])), marked)

    def residual(self, x: np.ndarray) -> np.ndarray:
        val = dict(zip(self.names, x, strict=True))
        cells = self.spec["cells"]
        out = []
        for g in self.groups:
            mark, resp = g["mark"], g["response"]
            dist = resp.distributions(
                val[f"s:{mark}"],
                val.get(f"eps:{mark}", 0.0),
                self.sigma(x, mark, resp.marked),
                val[f"a:{g['run']}:{mark}"],
            )
            for arm in g["arms"]:
                idx = arm[f"idx_{cells}"]
                out.append(arm[f"white_{cells}"] @ (arm["q"][idx] - dist[arm["k"]][idx]))
        return np.concatenate(out)


def fit_one(item: tuple[Any, ...]) -> dict[str, Any]:
    name, groups, spec, eps0 = item
    layout = Layout(groups, spec, eps0)
    result = optimize.least_squares(
        layout.residual, layout.start, bounds=(layout.low, layout.high), xtol=1e-12, ftol=1e-12, gtol=1e-12
    )
    jac = result.jac
    try:
        sd = np.sqrt(np.diag(np.linalg.inv(jac.T @ jac)))
    except np.linalg.LinAlgError:
        sd = np.full(len(layout.names), float("nan"))
    return {
        "model": name,
        "start": eps0,
        "chi2": 2 * float(result.cost),
        "points": len(result.fun),
        "names": layout.names,
        "x": [float(v) for v in result.x],
        "sd": [float(v) for v in sd],
    }


def fit_all(groups: list[dict[str, Any]]) -> dict[str, Any]:
    for cells in ("marked", "all"):
        whiteners(groups, cells)
    items = [(name, groups, spec, e0) for name, spec in MODELS.items() for e0 in STARTS]
    runs = ordered_map(fit_one, items, min_items=1)
    best: dict[str, dict[str, Any]] = {}
    for r in runs:
        if r["model"] not in best or r["chi2"] < best[r["model"]]["chi2"]:
            best[r["model"]] = r
    out: dict[str, Any] = {}
    for name, r in best.items():
        params = dict(zip(r["names"], r["x"], strict=True))
        sds = dict(zip(r["names"], r["sd"], strict=True))
        keep = [n for n in r["names"] if n.split(":")[0] in ("a", "s", "eps")]
        dof = r["points"] - len(r["names"])
        out[name] = {
            "chi2": r["chi2"],
            "points": r["points"],
            "parameters": len(r["names"]),
            "dof": dof,
            "chi2_over_phi": r["chi2"] / PHI,
            "p_value": float(stats.chi2.sf(r["chi2"], dof)) if dof > 0 else float("nan"),
            "params": {n: params[n] for n in keep},
            "sd": {n: sds[n] for n in keep},
            "all_params": params,
        }
    return out


def contrasts(fits: dict[str, Any]) -> dict[str, Any]:
    """Likelihood-ratio statistics of the rotation (two parameters) inside each fixed-point form, the gain of each
    nonuniform form over the uniform state, and eps of mark 101 with its z."""
    out: dict[str, Any] = {}
    for sigma in ("uniform", "shells", "qubits", "free"):
        base, rot = fits[sigma], fits[f"{sigma}_eps"]
        e, sd = rot["params"]["eps:101"], rot["sd"]["eps:101"]
        out[f"rotation_in_{sigma}"] = {
            "T": base["chi2"] - rot["chi2"],
            "dof": 2,
            "p_value": float(stats.chi2.sf(base["chi2"] - rot["chi2"], 2)),
            "eps_101": e,
            "eps_101_se": sd,
            "z_101": e / sd if sd > 0 else float("nan"),
            "eps_011": rot["params"]["eps:011"],
            "eps_011_se": rot["sd"]["eps:011"],
        }
    for sigma in ("shells", "qubits", "free"):
        for tag in ("", "_eps"):
            gain = fits[f"uniform{tag}"]["chi2"] - fits[f"{sigma}{tag}"]["chi2"]
            extra = fits[f"{sigma}{tag}"]["parameters"] - fits[f"uniform{tag}"]["parameters"]
            out[f"{sigma}{tag}_over_uniform{tag}"] = {
                "gain": gain,
                "extra_parameters": extra,
                "p_value": float(stats.chi2.sf(gain, extra)),
            }
    return out


def record() -> dict[str, Any]:
    groups = load_groups()
    fits = fit_all(groups)
    marked_check = []
    for g in groups:
        for arm in g["arms"]:
            m = g["response"].marked
            marked_check.append(
                {
                    "run": g["run"],
                    "mark": g["mark"],
                    "k": arm["k"],
                    "marked_frequency": float(arm["q"][m]),
                    "marked_se": float(math.sqrt(arm["cov"][m, m])),
                }
            )
    return {
        "schema": SCHEMA,
        "data": marked_check,
        "fits": fits,
        "contrasts": contrasts(fits),
        "note": (
            "The arms of a group are independent (the shared assignment-matrix errors of different circuits are not "
            "propagated across arms), as in fits.json; the eight cells of an arm carry their delta-method covariance."
        ),
    }


def close(a: Any, b: Any, tol: float = 1e-4) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a if k != "all_params")
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b, strict=True))
    if isinstance(a, float) or isinstance(b, float):
        if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
            return True
        return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
    return bool(a == b)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path, help="recompute and compare with this record to 1e-4 relative")
    args = parser.parse_args()
    text = json.dumps(record(), indent=1, sort_keys=True, default=float)
    if args.check is not None:
        if not close(json.loads(text), json.loads(args.check.read_text(encoding="utf-8"))):
            raise SystemExit(f"{args.check}: differs from the recomputed record")
        print(f"{args.check}: matches the recomputed record")
        return 0
    args.out.write_text(text + "\n", encoding="utf-8")
    print(json.dumps(record_summary(json.loads(text)), indent=1))
    return 0


def record_summary(rec: dict[str, Any]) -> dict[str, Any]:
    return {
        "chi2": {k: [round(v["chi2"], 3), v["dof"]] for k, v in rec["fits"].items()},
        "contrasts": rec["contrasts"],
        "eps": {k: v["params"] for k, v in rec["fits"].items() if "eps" in k},
    }


if __name__ == "__main__":
    raise SystemExit(main())
