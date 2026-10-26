"""The preregistered reading of the Ascella seed-repeat run (job-03) against the perturbed-compilation run (job-02).

docs/state/plans/ascella-seed-repeat-case.json fixes the readings before the acquisition, and
docs/design/ascella-signed-coherence-conformance.md#seed-repeat-case-job-03 states them. Settings match by name: job-03
submits job-02's 64 settings with the same compilation seeds, so a name fixes the seed. Per iteration the
block-conditioned X statistic z and its multinomial variance v come from ascella_response_geometry.statistic, as in
scripts/ascella_compilation_reading.py.

- M, mesh identity: the settings whose computed_circuit equals job-02's under the same name, anchors and perturbed
  counted apart. A, P1 and P2 read the identical subset; with no perturbed mesh repeated, P1 is not read.
- A, anchor control: the difference of the jobs' inverse-variance anchor means of z over its standard error;
  at or above the two-sided ALPHA normal quantile it reads "moved".
- P1, reproduction: the Pearson correlation of the identical perturbed meshes' z between the jobs, its p-value the
  share of PERMUTATIONS relabelings of job-03's values whose correlation reaches the observed one. At p below ALPHA
  it reads "fixed per mesh" with r at least FIXED_BOUND, "partly fixed" below; otherwise "not reproduced".
  FIXED_BOUND is the Fisher-z ALPHA lower bound, on 56 meshes, of the attenuation ceiling
  s_c^2 / sqrt((s_c^2 + s_n^2)(s_c^2 + s_n^2 / 2)) that a fully fixed per-mesh error reaches, with job-02's
  compilation-induced standard deviation s_c and counting variance s_n^2 of heater-coupling.json
  (`observed_spread`), the latter halved at job-03's doubled samples.
- P2, replicated compilation dependence: job-02's R1 anchor-ratio statistic on job-03 alone.

Exploratory, outside the decision: the Spearman correlation of the perturbed meshes' block mode-2 fractions between
the jobs, and the Spearman correlation of each perturbed mesh's z change (job-03 less job-02) with the change of the
L1 heater-phase distance to the mesh that ran before it.

One numpy generator seeded with value PERMUTATION_INDEX of the order draw that job-03's cases.json names draws the
P1 relabelings first and the P2 labelings second.

Usage:
  "$PYTHON" scripts/ascella_seed_repeat_reading.py JOB_02 JOB_03 OUT [--check]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_physical_models as models  # noqa: E402

ALPHA = 0.01
PERMUTATIONS = 20000
# The request consumes values 0..55 of its order draw; value 56 seeds the relabelings.
PERMUTATION_INDEX = 56
SPREAD_RECORD = "docs/evidence/ascella-order-coefficients/heater-coupling.json"


def names(data: dict[str, Any]) -> list[str]:
    return [setting["name"] for setting in data["record"]["manifest"]["settings"]]


def served(data: dict[str, Any]) -> list[str]:
    return [row["result_fields"]["computed_circuit"] for row in data["record"]["results"]["iterations"]]


def fixed_bound(meshes: int) -> dict[str, float]:
    """The attenuation ceiling of a fully fixed per-mesh error and its Fisher-z ALPHA lower bound."""
    spread = json.loads((ROOT / SPREAD_RECORD).read_text(encoding="utf-8"))["observed_spread"]
    compilation = spread["compilation_sd"] ** 2
    counting = spread["mean_counting_variance"]
    ceiling = compilation / math.sqrt((compilation + counting) * (compilation + counting / 2))
    error = 1 / math.sqrt(meshes - 3)
    bound = math.tanh(math.atanh(ceiling) - float(stats.norm.ppf(1 - ALPHA)) * error)
    return {"ceiling": ceiling, "bound": bound}


def anchor_control(z2: np.ndarray, v2: np.ndarray, z3: np.ndarray, v3: np.ndarray) -> dict[str, Any]:
    mean2 = float((z2 / v2).sum() / (1 / v2).sum())
    mean3 = float((z3 / v3).sum() / (1 / v3).sum())
    error = math.sqrt(1 / float((1 / v2).sum()) + 1 / float((1 / v3).sum()))
    z = (mean3 - mean2) / error
    critical = float(stats.norm.ppf(1 - ALPHA / 2))
    return {
        "job_02_mean": mean2,
        "job_03_mean": mean3,
        "difference": mean3 - mean2,
        "standard_error": error,
        "z": z,
        "reading": "moved" if abs(z) >= critical else "steady",
    }


def correlations(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Pearson r of x with each row of y."""
    xc = x - x.mean()
    yc = y - y.mean(axis=-1, keepdims=True)
    out: np.ndarray = (yc @ xc) / np.sqrt((xc @ xc) * (yc * yc).sum(axis=-1))
    return out


def reproduction(z2: np.ndarray, z3: np.ndarray, generator: np.random.Generator) -> dict[str, Any]:
    observed = float(correlations(z2, z3[None, :])[0])
    shuffled = generator.permuted(np.tile(z3, (PERMUTATIONS, 1)), axis=1)
    p = float((1 + (correlations(z2, shuffled) >= observed).sum()) / (1 + PERMUTATIONS))
    limits = fixed_bound(len(z2))
    if p >= ALPHA:
        verdict = "not reproduced"
    else:
        verdict = "fixed per mesh" if observed >= limits["bound"] else "partly fixed"
    return {"meshes": len(z2), "r": observed, "p": p, **limits, "permutations": PERMUTATIONS, "reading": verdict}


def dependence(z: np.ndarray, v: np.ndarray, anchor: np.ndarray, generator: np.random.Generator) -> dict[str, Any]:
    observed = float(reading.dispersion_ratio(z, v, anchor[None, :])[0])
    labels = np.zeros((PERMUTATIONS, len(z)), dtype=bool)
    order = generator.permuted(np.tile(np.arange(len(z)), (PERMUTATIONS, 1)), axis=1)
    np.put_along_axis(labels, order[:, : int(anchor.sum())], True, axis=1)
    p = float((1 + (reading.dispersion_ratio(z, v, labels) >= observed).sum()) / (1 + PERMUTATIONS))
    return {
        "ratio": observed,
        "p": p,
        "permutations": PERMUTATIONS,
        "reading": "compilation dependent" if p < ALPHA else "no compilation dependence detected",
    }


def predecessor_distance(data: dict[str, Any]) -> dict[str, float]:
    """Per setting name, the L1 heater-phase distance of its mesh to the mesh of the iteration before it."""
    phases = data["phases"][data["configuration"]]
    change = np.angle(np.exp(1j * (phases[1:] - phases[:-1])))
    distances = np.abs(change).sum(axis=1)
    return {name: float(value) for name, value in zip(names(data)[1:], distances, strict=True)}


def build(b_dir: Path, c_dir: Path) -> dict[str, Any]:
    b, c = models.job_data(b_dir), models.job_data(c_dir)
    models.require(b["record"]["manifest"]["job"] == "job-02" and c["record"]["manifest"]["job"] == "job-03", "jobs")
    names_b, names_c = names(b), names(c)
    models.require(sorted(names_b) == sorted(names_c), "job-03 does not hold job-02's settings")
    index_b = {name: i for i, name in enumerate(names_b)}
    anchor_c = reading.anchors_of(c)
    served_b, served_c = served(b), served(c)
    identical = [served_c[i] == served_b[index_b[name]] for i, name in enumerate(names_c)]
    z_b, v_b = reading.x_statistics(b)
    z_c, v_c = reading.x_statistics(c)
    draw = c["record"]["manifest"]["compilation_order"]["draw"]
    generator = np.random.default_rng(
        int(json.loads((ROOT / draw).read_text(encoding="utf-8"))["values"][PERMUTATION_INDEX])
    )
    keep = np.array(identical)
    anchors = [i for i in range(len(names_c)) if anchor_c[i] and identical[i]]
    perturbed = [i for i in range(len(names_c)) if not anchor_c[i] and identical[i]]
    paired = [index_b[names_c[i]] for i in perturbed]
    record: dict[str, Any] = {
        "schema": "ascella-seed-repeat-reading-v1",
        "plan": "docs/state/plans/ascella-seed-repeat-case.json",
        "runs": [b_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "alpha": ALPHA,
        "seed_draw": draw,
        "seed_index": PERMUTATION_INDEX,
        "mesh_identity": {
            "anchors_identical": len(anchors),
            "anchors": int(anchor_c.sum()),
            "perturbed_identical": len(perturbed),
            "perturbed": int((~anchor_c).sum()),
        },
    }
    record["anchor_control"] = (
        anchor_control(
            z_b[[index_b[names_c[i]] for i in anchors]],
            v_b[[index_b[names_c[i]] for i in anchors]],
            z_c[anchors],
            v_c[anchors],
        )
        if anchors
        else {"reading": "not read: no anchor mesh repeats"}
    )
    if len(perturbed) >= 4:
        record["reproduction"] = reproduction(z_b[paired], z_c[perturbed], generator)
    else:
        record["reproduction"] = {"meshes": len(perturbed), "reading": "not read: too few perturbed meshes repeat"}
    # The dispersion ratio needs two members on each side, and a rank correlation three pairs.
    if len(anchors) >= 2 and len(perturbed) >= 2:
        record["dependence"] = dependence(z_c[keep], v_c[keep], anchor_c[keep], generator)
    else:
        record["dependence"] = {"reading": "not read: fewer than two identical anchors or perturbed meshes"}
    if len(perturbed) < 3:
        record["exploratory"] = {"reading": "not read: fewer than three perturbed meshes repeat"}
        return record
    block_b = b["block"] / b["block"].sum(axis=1, keepdims=True)
    block_c = c["block"] / c["block"].sum(axis=1, keepdims=True)
    distance_b, distance_c = predecessor_distance(b), predecessor_distance(c)
    moved = [i for i in perturbed if names_c[i] in distance_b and names_c[i] in distance_c]
    dark = stats.spearmanr(block_b[paired, 2], block_c[perturbed, 2])
    transition = stats.spearmanr(
        [distance_c[names_c[i]] - distance_b[names_c[i]] for i in moved],
        [z_c[i] - z_b[index_b[names_c[i]]] for i in moved],
    )
    record["exploratory"] = {
        "dark_output_spearman": {"rho": float(dark.statistic), "p": float(dark.pvalue)},
        "predecessor_transition_spearman": {"rho": float(transition.statistic), "p": float(transition.pvalue)},
        "x_means": {
            "job_02_perturbed": float(z_b[paired].mean()),
            "job_03_perturbed": float(z_c[perturbed].mean()),
        },
    }
    return record


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve(), Path(args[1]).resolve())
    out = Path(args[2]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
