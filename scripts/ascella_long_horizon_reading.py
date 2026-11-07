"""The preregistered reading of a repeat of job-02's seeded settings against an earlier run of the same settings.

docs/state/plans/ascella-long-horizon-seed-repeat-case.json fixes the readings before the acquisition, and
docs/design/ascella-signed-coherence-conformance.md#long-horizon-seed-repeat-case-job-08 states them. The decisive
pair is job-03 (reference) and job-08 (repeat); job-02 against job-08 is the secondary pair, and job-02 against
job-03 is the retrospective rehearsal of the same rule on the retained nine-hour repeat. Settings match by name, so a
name fixes the compilation seed. Per iteration the block-conditioned X statistic z and its multinomial variance v
come from ascella_compilation_reading.x_statistics, as in scripts/ascella_seed_repeat_reading.py.

- M, mesh identity: the settings whose served unitary (the deserialized computed_circuit) lies within
  MESH_TOLERANCE of the reference's under the same name in largest entry modulus, anchors and perturbed counted
  apart, with the byte-equal count beside it. The serialized phases of one mesh differ in their low bits between
  compile stacks (the sim:ascella replay of job-02 lies within 2.4e-7 of the QPU's job-02 unitaries and equals none
  of their strings), so a byte comparison would read float jitter as a redrawn mesh. Every other reading uses the
  identical subset; with fewer than four identical perturbed meshes nothing else is read.
- A, anchor control: the difference of the runs' inverse-variance anchor means of z over its standard error; at or
  above the two-sided ALPHA normal quantile it reads "moved".
- S, persistence (primary): mesh_selection.persistence on the identical perturbed meshes as one block, the
  reference's z as the retained deviations and the repeat's as the new ones, over the identity and RELABELINGS
  sampled relabelings. The slope regresses the repeat's centered z on the reference's through the origin; its
  one-sided 1 - ALPHA upper bound inverts the relabeling test, and mesh_selection.persistence_reading reads it at
  ALPHA and USEFUL_SLOPE (persists, recurs below the useful slope, redrawn, indeterminate), the rule of the Belenos
  mesh-persistence case. The reference's counting noise attenuates a fully persistent error's slope to the
  reliability s_c^2 / (s_c^2 + s_n^2(reference)), recorded beside it.
- P1, reproduction (secondary): the Pearson r of the identical perturbed meshes' z, its p-value the share of
  RELABELINGS relabelings whose r reaches the observed one, read as in the seed-repeat reading against the
  attenuation ceiling s_c^2 / sqrt((s_c^2 + s_n^2(reference))(s_c^2 + s_n^2(repeat))) and its Fisher-z ALPHA lower
  bound, with job-02's compilation-induced SD s_c and the counting variance s_n^2 at 8,192 samples of
  heater-coupling.json (`observed_spread`), scaled by 8,192 over each run's samples per iteration.
- P2, replicated compilation dependence: job-02's R1 anchor-ratio statistic on the repeat alone.

Exploratory, outside the decision: the Spearman correlation of the identical perturbed meshes' block mode-2 fractions
between the runs, and that of each mesh's z change with the change of its predecessor's L1 heater-phase distance.

One numpy generator per pair, seeded with the draw value PAIR_SEED names, draws the S relabelings, then the P1
relabelings, then the P2 labelings. The pairs with job-08 and the rehearsal take values of LONG_REPEAT_ORDER_DRAW,
whose request consumes values 0..55 and whose power record takes value POWER_INDEX; job-08 against job-09, the
secondary reading of docs/state/plans/ascella-prospective-correction-case.json, takes value 58 of
PROSPECTIVE_ORDER_DRAW, whose request consumes values 0..55 and whose correction score takes 56 and 57. Every value
seeds one use.

--power OUT [--check] writes the design's power record: POWER_REPLICATES Gaussian replicates per true slope in
POWER_SLOPES of 56 meshes whose reference z is a true error of variance s_c^2 plus counting noise at the reference's
16,384 samples, and whose repeat z is the slope times the true error plus a fresh error of variance
s_c^2 (1 - slope^2) plus counting noise at 32,768 samples, each read with POWER_RELABELINGS relabelings. Every
replicate takes its own generator spawned, before the map, from value POWER_INDEX of LONG_REPEAT_ORDER_DRAW.

Usage:
  "$PYTHON" scripts/ascella_long_horizon_reading.py REFERENCE REPEAT OUT [--check]
  "$PYTHON" scripts/ascella_long_horizon_reading.py --power OUT [--check]
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
import ascella_seed_repeat_reading as seed_repeat  # noqa: E402

import mesh_selection  # noqa: E402
from parallel import ordered_map  # noqa: E402

ALPHA = 0.01
USEFUL_SLOPE = 0.5
RELABELINGS = 20000
# A served unitary within this largest entry modulus of the reference's is the same mesh: above the 2.4e-7 jitter
# between compile stacks and far below one heater step.
MESH_TOLERANCE = 1e-6
SPREAD_RECORD = "docs/evidence/ascella-order-coefficients/heater-coupling.json"
SPREAD_SAMPLES = 8192
PLAN = "docs/state/plans/ascella-long-horizon-seed-repeat-case.json"
LONG_REPEAT_ORDER_DRAW = "docs/evidence/anu_qrng/draw-2026-11-06T175610Z.json"
PROSPECTIVE_PLAN = "docs/state/plans/ascella-prospective-correction-case.json"
PROSPECTIVE_ORDER_DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T040400Z.json"
POWER_INDEX = 57
# Each pair's plan, and the draw and value that seed its generator.
PAIR_SEED = {
    ("job-03", "job-08"): (PLAN, LONG_REPEAT_ORDER_DRAW, 56),
    ("job-02", "job-08"): (PLAN, LONG_REPEAT_ORDER_DRAW, 58),
    ("job-02", "job-03"): (PLAN, LONG_REPEAT_ORDER_DRAW, 59),
    ("job-08", "job-09"): (PROSPECTIVE_PLAN, PROSPECTIVE_ORDER_DRAW, 58),
}
POWER_SLOPES = (0.0, 0.25, 0.5, 0.75, 1.0)
POWER_REPLICATES = 400
POWER_RELABELINGS = 2000
POWER_MESHES = 56


def served_unitary(text: str) -> np.ndarray:
    """The unitary of one serialized computed_circuit."""
    from perceval.serialization import deserialize

    return np.asarray(deserialize(text).compute_unitary(), dtype=np.complex128)


def mesh_distance(item: tuple[str, str]) -> float:
    """Largest entry modulus of the difference of two served unitaries; zero for equal strings."""
    left, right = item
    return 0.0 if left == right else float(np.max(np.abs(served_unitary(left) - served_unitary(right))))


def samples_of(data: dict[str, Any]) -> int:
    manifest = data["record"]["manifest"]
    return int(manifest["max_samples"]) // int(manifest["iterations"])


def spread() -> tuple[float, float]:
    """job-02's compilation-induced variance and its counting variance at SPREAD_SAMPLES samples per iteration."""
    record = json.loads((ROOT / SPREAD_RECORD).read_text(encoding="utf-8"))["observed_spread"]
    return float(record["compilation_sd"]) ** 2, float(record["mean_counting_variance"])


def ceiling(samples_old: int, samples_new: int, meshes: int) -> dict[str, float]:
    """The attenuation ceiling of a fully fixed per-mesh error between two runs and its Fisher-z ALPHA lower bound."""
    compilation, counting = spread()
    noise_old, noise_new = counting * SPREAD_SAMPLES / samples_old, counting * SPREAD_SAMPLES / samples_new
    value = compilation / math.sqrt((compilation + noise_old) * (compilation + noise_new))
    bound = math.tanh(math.atanh(value) - float(stats.norm.ppf(1 - ALPHA)) / math.sqrt(meshes - 3))
    return {"ceiling": value, "bound": bound, "reliability_reference": compilation / (compilation + noise_old)}


def anchor_control(z_old: np.ndarray, v_old: np.ndarray, z_new: np.ndarray, v_new: np.ndarray) -> dict[str, Any]:
    shift = seed_repeat.anchor_shift(z_old, v_old, z_new, v_new)
    return {"reference_mean": shift.pop("mean_old"), "repeat_mean": shift.pop("mean_new"), **shift}


def relabelings(meshes: int, generator: np.random.Generator) -> np.ndarray:
    """The identity followed by RELABELINGS uniform relabelings of the meshes."""
    sampled = generator.permuted(np.tile(np.arange(meshes), (RELABELINGS, 1)), axis=1)
    return np.vstack([np.arange(meshes)[None, :], sampled])


def persistence(
    z_old: np.ndarray, z_new: np.ndarray, generator: np.random.Generator, reliability: float
) -> dict[str, Any]:
    result = mesh_selection.persistence(
        z_old[None, :], z_new[None, :], ALPHA, USEFUL_SLOPE, relabelings=relabelings(len(z_old), generator)
    )
    return {
        **result,
        "meshes": len(z_old),
        "relabelings": RELABELINGS,
        "alpha": ALPHA,
        "useful_slope": USEFUL_SLOPE,
        "attenuated_full_persistence": reliability,
        "reading": mesh_selection.persistence_reading(result, ALPHA, USEFUL_SLOPE),
    }


def reproduction(
    z_old: np.ndarray, z_new: np.ndarray, limits: dict[str, float], generator: np.random.Generator
) -> dict[str, Any]:
    observed = float(seed_repeat.correlations(z_old, z_new[None, :])[0])
    shuffled = generator.permuted(np.tile(z_new, (RELABELINGS, 1)), axis=1)
    p = float((1 + (seed_repeat.correlations(z_old, shuffled) >= observed).sum()) / (1 + RELABELINGS))
    if p >= ALPHA:
        verdict = "not reproduced"
    else:
        verdict = "fixed per mesh" if observed >= limits["bound"] else "partly fixed"
    return {
        "meshes": len(z_old),
        "r": observed,
        "p": p,
        "ceiling": limits["ceiling"],
        "bound": limits["bound"],
        "relabelings": RELABELINGS,
        "reading": verdict,
    }


def build(old_dir: Path, new_dir: Path) -> dict[str, Any]:
    old, new = models.job_data(old_dir), models.job_data(new_dir)
    pair = (old["record"]["manifest"]["job"], new["record"]["manifest"]["job"])
    models.require(pair in PAIR_SEED, f"the pair {pair} is not one of {sorted(PAIR_SEED)}")
    names_old, names_new = seed_repeat.names(old), seed_repeat.names(new)
    models.require(sorted(names_old) == sorted(names_new), f"{pair[1]} does not hold {pair[0]}'s settings")
    index_old = {name: i for i, name in enumerate(names_old)}
    anchor_new = reading.anchors_of(new)
    served_old, served_new = seed_repeat.served(old), seed_repeat.served(new)
    pairs = [(served_new[i], served_old[index_old[name]]) for i, name in enumerate(names_new)]
    distances = ordered_map(mesh_distance, pairs)
    identical = [distance <= MESH_TOLERANCE for distance in distances]
    byte_equal = [left == right for left, right in pairs]
    z_old, v_old = reading.x_statistics(old)
    z_new, v_new = reading.x_statistics(new)
    plan, draw, seed_index = PAIR_SEED[pair]
    generator = np.random.default_rng(int(json.loads((ROOT / draw).read_text(encoding="utf-8"))["values"][seed_index]))
    keep = np.array(identical)
    anchors = [i for i in range(len(names_new)) if anchor_new[i] and identical[i]]
    perturbed = [i for i in range(len(names_new)) if not anchor_new[i] and identical[i]]
    paired = [index_old[names_new[i]] for i in perturbed]
    record: dict[str, Any] = {
        "schema": "ascella-long-horizon-reading-v1",
        "plan": plan,
        "jobs": list(pair),
        "runs": [old_dir.relative_to(ROOT).as_posix(), new_dir.relative_to(ROOT).as_posix()],
        "samples": [samples_of(old), samples_of(new)],
        "alpha": ALPHA,
        "seed_draw": draw,
        "seed_index": seed_index,
        "mesh_identity": {
            "tolerance": MESH_TOLERANCE,
            "anchors_identical": len(anchors),
            "anchors": int(anchor_new.sum()),
            "perturbed_identical": len(perturbed),
            "perturbed": int((~anchor_new).sum()),
            "byte_equal": int(sum(byte_equal)),
            "largest_identical_distance": max((d for d in distances if d <= MESH_TOLERANCE), default=0.0),
        },
    }
    if len(perturbed) < 4:
        record["reading"] = "not read: fewer than four perturbed meshes repeat"
        return record
    record["anchor_control"] = (
        anchor_control(
            z_old[[index_old[names_new[i]] for i in anchors]],
            v_old[[index_old[names_new[i]] for i in anchors]],
            z_new[anchors],
            v_new[anchors],
        )
        if anchors
        else {"reading": "not read: no anchor mesh repeats"}
    )
    limits = ceiling(samples_of(old), samples_of(new), len(perturbed))
    record["persistence"] = persistence(z_old[paired], z_new[perturbed], generator, limits["reliability_reference"])
    record["reproduction"] = reproduction(z_old[paired], z_new[perturbed], limits, generator)
    # The dispersion ratio needs two members on each side.
    if len(anchors) >= 2:
        record["dependence"] = seed_repeat.dependence(z_new[keep], v_new[keep], anchor_new[keep], generator)
    else:
        record["dependence"] = {"reading": "not read: fewer than two identical anchors"}
    block_old = old["block"] / old["block"].sum(axis=1, keepdims=True)
    block_new = new["block"] / new["block"].sum(axis=1, keepdims=True)
    distance_old, distance_new = seed_repeat.predecessor_distance(old), seed_repeat.predecessor_distance(new)
    moved = [i for i in perturbed if names_new[i] in distance_old and names_new[i] in distance_new]
    dark = stats.spearmanr(block_old[paired, 2], block_new[perturbed, 2])
    transition = stats.spearmanr(
        [distance_new[names_new[i]] - distance_old[names_new[i]] for i in moved],
        [z_new[i] - z_old[index_old[names_new[i]]] for i in moved],
    )
    record["exploratory"] = {
        "dark_output_spearman": {"rho": float(dark.statistic), "p": float(dark.pvalue)},
        "predecessor_transition_spearman": {"rho": float(transition.statistic), "p": float(transition.pvalue)},
        "x_means": {
            "reference_perturbed": float(z_old[paired].mean()),
            "repeat_perturbed": float(z_new[perturbed].mean()),
        },
    }
    record["reading"] = record["persistence"]["reading"]
    return record


def power_replicate(item: tuple[float, np.random.SeedSequence]) -> str:
    """The reading of one Gaussian replicate at a true slope (module docstring, --power)."""
    slope, seed = item
    compilation, counting = spread()
    generator = np.random.default_rng(seed)
    true = generator.normal(0.0, math.sqrt(compilation), POWER_MESHES)
    old = true + generator.normal(0.0, math.sqrt(counting * SPREAD_SAMPLES / 16384), POWER_MESHES)
    fresh = generator.normal(0.0, math.sqrt(compilation * (1.0 - slope * slope)), POWER_MESHES)
    new = slope * true + fresh + generator.normal(0.0, math.sqrt(counting * SPREAD_SAMPLES / 32768), POWER_MESHES)
    sampled = generator.permuted(np.tile(np.arange(POWER_MESHES), (POWER_RELABELINGS, 1)), axis=1)
    labels = np.vstack([np.arange(POWER_MESHES)[None, :], sampled])
    result = mesh_selection.persistence(
        old[None, :], new[None, :], ALPHA, USEFUL_SLOPE, bound=False, relabelings=labels
    )
    return mesh_selection.persistence_reading(result, ALPHA, USEFUL_SLOPE)


def power() -> dict[str, Any]:
    value = int(json.loads((ROOT / LONG_REPEAT_ORDER_DRAW).read_text(encoding="utf-8"))["values"][POWER_INDEX])
    children = np.random.SeedSequence(value).spawn(len(POWER_SLOPES) * POWER_REPLICATES)
    items = [
        (slope, children[k * POWER_REPLICATES + j])
        for k, slope in enumerate(POWER_SLOPES)
        for j in range(POWER_REPLICATES)
    ]
    readings = ordered_map(power_replicate, items)
    rows = []
    for k, slope in enumerate(POWER_SLOPES):
        chunk = readings[k * POWER_REPLICATES : (k + 1) * POWER_REPLICATES]
        rows.append(
            {"true_slope": slope, "shares": {name: chunk.count(name) / POWER_REPLICATES for name in sorted(set(chunk))}}
        )
    return {
        "schema": "ascella-long-horizon-power-v1",
        "plan": PLAN,
        "seed_draw": LONG_REPEAT_ORDER_DRAW,
        "seed_index": POWER_INDEX,
        "replicates": POWER_REPLICATES,
        "relabelings": POWER_RELABELINGS,
        "meshes": POWER_MESHES,
        "alpha": ALPHA,
        "useful_slope": USEFUL_SLOPE,
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) == 2 and args[0] == "--power":
        record = power()
    elif len(args) == 3:
        record = build(Path(args[0]).resolve(), Path(args[1]).resolve())
    else:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    out = Path(args[-1]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
