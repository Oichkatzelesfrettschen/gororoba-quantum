"""Power and null-bound probability of the Ascella new-seed case's acquisition branches.

docs/state/plans/ascella-new-seed-meshes-case.json scores frozen predictions on n new meshes from J jobs by a
within-job-centered Pearson r, one-sided by the t distribution on n - 1 - J degrees of freedom at ALPHA_EACH. For
each branch this record states:

- the critical r, tcrit / sqrt(tcrit^2 + df);
- the attenuation ceiling c = sqrt(s_c^2 / (s_c^2 + s_n^2)), s_c^2 the compilation variance of
  fixed-mesh-confirmation.json and s_n^2 the 8,192-sample counting variance of heater-coupling.json scaled by
  8,192 / SAMPLES;
- power at latent correlation r, the noncentral t survival at tcrit with noncentrality rho sqrt(df / (1 - rho^2)),
  rho = c r;
- the marginal probability, at a true correlation of zero, that one predictor's one-sided 1 - ALPHA_EACH Fisher-z
  upper bound tanh(atanh(r) + z / sqrt(n - J - 2)) gives a plug-in share r_upper^2 / c^2 below the held-out point
  estimate of fixed-mesh-confirmation.json, with atanh(r) taken as normal with standard error 1 / sqrt(n - J - 2);
- credits, 1.0 per job plus SAMPLES max_shots at 1e-6, and the worst-case seconds 186 / 64 per iteration.

Usage:
  "$PYTHON" scripts/ascella_new_seed_sizing.py CONFIRMATION SPREAD OUT [--check]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_physical_models as models  # noqa: E402

ALPHA_EACH = 0.005
SAMPLES = 32768
SECONDS_PER_ITERATION = 186 / 64
LATENT = (0.25, 0.318, 0.437)
ANCHOR_STRIDE = 8
# (label, iterations per job); job-04 alone is the stop rule's fallback, the adaptive branches follow job-04's
# duration, and the last two are the rejected fixed alternatives.
BRANCHES: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("job-04 alone", (80,)),
    ("job-04 + job-05-i80", (80, 80)),
    ("job-04 + job-05-i88", (80, 88)),
    ("job-04 + job-05-i96", (80, 96)),
    ("two fixed jobs of 96", (96, 96)),
    ("three jobs of 80", (80, 80, 80)),
)


def branch(label: str, iterations: tuple[int, ...], compilation: float, counting: float, reference: float) -> dict:
    jobs = len(iterations)
    meshes = sum(count - count // ANCHOR_STRIDE for count in iterations)
    dof = meshes - 1 - jobs
    t_critical = float(stats.t.ppf(1 - ALPHA_EACH, dof))
    ceiling = math.sqrt(compilation / (compilation + counting))
    power = {}
    for r in LATENT:
        rho = ceiling * r
        power[f"{r}"] = float(stats.nct.sf(t_critical, dof, rho * math.sqrt(dof / (1 - rho * rho))))
    error = 1 / math.sqrt(meshes - jobs - 2)
    threshold = math.atanh(ceiling * math.sqrt(reference)) - float(stats.norm.ppf(1 - ALPHA_EACH)) * error
    return {
        "branch": label,
        "iterations": list(iterations),
        "anchors": [count // ANCHOR_STRIDE for count in iterations],
        "meshes": meshes,
        "degrees_of_freedom": dof,
        "critical_r": t_critical / math.sqrt(t_critical * t_critical + dof),
        "ceiling": ceiling,
        "power": power,
        "null_bound_probability": float(stats.norm.cdf(threshold / error)),
        "credits": round(jobs * (1 + SAMPLES * 1e-6), 6),
        "worst_case_seconds": [count * SECONDS_PER_ITERATION for count in iterations],
    }


def build(confirmation_path: Path, spread_path: Path) -> dict[str, Any]:
    confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
    spread = json.loads(spread_path.read_text(encoding="utf-8"))["observed_spread"]
    compilation = confirmation["explained_share"]["compilation_variance"]
    counting = spread["mean_counting_variance"] * 8192 / SAMPLES
    reference = confirmation["explained_share"]["share_of_ceiling"]
    return {
        "schema": "ascella-new-seed-sizing-v1",
        "plan": "docs/state/plans/ascella-new-seed-meshes-case.json",
        "inputs": [confirmation_path.relative_to(ROOT).as_posix(), spread_path.relative_to(ROOT).as_posix()],
        "alpha_each": ALPHA_EACH,
        "samples": SAMPLES,
        "compilation_variance": compilation,
        "counting_variance": counting,
        "reference_share": reference,
        "branches": [branch(label, counts, compilation, counting, reference) for label, counts in BRANCHES],
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    models.require(len(args) == 3, f"usage: see the module docstring, not {argv}")
    paths = [Path(arg).resolve() for arg in args]
    text = json.dumps(build(paths[0], paths[1]), indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(paths[2].read_text(encoding="utf-8")), paths[2].name)
        return 0
    paths[2].write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
