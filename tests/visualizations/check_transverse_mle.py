"""Independently check the JavaScript transverse MLE on a deterministic grid.

This optional development check needs Node and SciPy. It reads no acquired
records, generates no random seed, and submits no remote work. The report is
printed to stdout; redirect it to a separately retained receipt when needed.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
from functools import partial
from pathlib import Path
from typing import Any

import scipy
from scipy.optimize import minimize_scalar


def log_likelihood(zeros: int, shots: int, expectation: float) -> float:
    probability = (1.0 + expectation) / 2.0
    if not 0.0 <= probability <= 1.0:
        return -math.inf
    if (zeros and probability == 0.0) or (shots > zeros and probability == 1.0):
        return -math.inf
    positive = zeros * math.log(probability) if zeros else 0.0
    negative = (shots - zeros) * math.log1p(-probability) if shots > zeros else 0.0
    return positive + negative


def boundary_objective(angle: float, *, counts: tuple[int, int, int, int]) -> float:
    kx, nx, ky, ny = counts
    sx = math.copysign(1, 2 * kx / nx - 1)
    sy = math.copysign(1, 2 * ky / ny - 1)
    return -(log_likelihood(kx, nx, sx * math.cos(angle)) + log_likelihood(ky, ny, sy * math.sin(angle)))


def check(math_source: Path) -> dict[str, Any]:
    cases = []
    for nx, ny in ((16, 16), (128, 8), (1024, 1024), (7, 193)):
        for kx in sorted({0, 1, nx // 2, nx - 1, nx}):
            for ky in sorted({0, 1, ny // 2, ny - 1, ny}):
                cases.append([kx, nx, ky, ny])
    code = (
        f"const M=require({json.dumps(str(math_source.resolve()))});"
        f"console.log(JSON.stringify({json.dumps(cases)}.map(c=>M.constrainedXY(...c))));"
    )
    completed = subprocess.run(["node", "-e", code], check=True, capture_output=True, text=True, timeout=30)
    values = json.loads(completed.stdout)
    if len(values) != len(cases):
        raise ValueError("estimator result coverage differs")
    maximum = 0.0
    outside = 0
    for counts, value in zip(cases, values, strict=True):
        kx, nx, ky, ny = counts
        rx, ry = 2 * kx / nx - 1, 2 * ky / ny - 1
        if value["z"] is not None:
            raise ValueError("estimator supplied an unmeasured Z value")
        if math.hypot(rx, ry) <= 1:
            if abs(value["x"] - rx) > 1e-14 or abs(value["y"] - ry) > 1e-14:
                raise ValueError("interior raw estimate moved")
            continue
        outside += 1
        objective = partial(boundary_objective, counts=(kx, nx, ky, ny))

        optimum = minimize_scalar(
            objective,
            bounds=(1e-12, math.pi / 2 - 1e-12),
            method="bounded",
            options={"xatol": 1e-13},
        )
        if not optimum.success:
            raise ValueError("independent optimizer did not converge")
        best = min(float(optimum.fun), objective(0), objective(math.pi / 2))
        discrepancy = abs(value["logLikelihood"] + best)
        maximum = max(maximum, discrepancy)
        if discrepancy > 1e-8 or math.hypot(value["x"], value["y"]) > 1 + 1e-14:
            raise ValueError(f"likelihood or positivity mismatch for counts {counts}")
    return {
        "passed": True,
        "method": "independent SciPy scalar boundary optimization; deterministic count grid",
        "cases": len(cases),
        "outside_disk_cases": outside,
        "maximum_log_likelihood_disagreement": maximum,
        "python": platform.python_version(),
        "scipy": scipy.__version__,
        "node": subprocess.check_output(["node", "--version"], text=True).strip(),
        "scope": "JavaScript numerical implementation, not Rust compilation or hardware evidence",
    }


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--math",
        type=Path,
        default=root / "gororoba_quantum/visualizations/evidence_workbench/math.js",
    )
    print(json.dumps(check(parser.parse_args().math), indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
