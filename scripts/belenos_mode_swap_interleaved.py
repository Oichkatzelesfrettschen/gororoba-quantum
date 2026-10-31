"""Belenos interleaved mode swap: the packed and swapped box-kite layouts alternate inside one job.

docs/design/belenos-mode-swap-interleaved-case.md fixes the request. Registry claim qd-belenos-packed-mode-swap found
that moving a packed sign block three of six 4-mode slots changes its single-click algebra-mode share a, but the
packed and swapped series ran as separate jobs about an hour apart, so placement and drift were confounded. Here each
block set k of box_kite_photonic_packed/job-0k runs six template iterations that alternate the layouts: packed,
swapped, packed, swapped, packed, swapped for an even block set and the mirror for an odd one. Each layout runs its
primary seed at the first and last of its slots and a second, replicate seed between them. The two primary repeats
request one compiled mesh, so their difference is drift. The replicate sits at the mean time of its primary pair, so a
same-layout contrast between the replicate and the pooled primary repeats carries no linear drift and measures the
per-seed mesh variance that the packed-swapped contrast is tested against. Both layouts put the six photons on chip
modes 0, 4, 8, 12, 16 and 20, so one template circuit serves every iteration.

JOBS assigns block sets (0, 1), (2, 3) and (4,) to job-00, job-01 and job-02. Set 5 holds two photons, not six, and
stays out. The primary seed of each set-layout is, in job, set and layout order (packed, swapped), an index 0 to 9
value of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-31T043029Z.json; the replicate seed is the index 0 to 9
value of docs/evidence/anu_qrng/draw-2026-10-31T051136Z.json. docs/evidence/qrng_seeds/allocations.json registers both.

--check rebuilds the cases, compares them with the retained bytes, binds every iteration through
qd_platform.template_experiment, requires each iteration's template unitary to equal the block-diagonal unitary of
the retained packed or swapped circuit.json within 1e-9, and holds each job's duration bound inside MAX_DURATION.
--build JOB writes a case. --analyze RUN RUN RUN pools the three collected runs into one block table over all 30
blocks and writes analysis.json beside each: the within-job validity check, the mesh variance, the placement test
against it, the slot predictor of scripts/qd_packed_mode_swap_analysis.py with its sign-specific reading, the
comparison with the earlier deltas and the preregistered reading.

Usage:
  "$PYTHON" scripts/belenos_mode_swap_interleaved.py [--check | --build JOB | --analyze RUN RUN RUN]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_packed_mode_swap_analysis import collect, correlation, decide  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402
from scipy.stats import binomtest, chi2  # noqa: E402

from parallel import ordered_map  # noqa: E402

MODES = 24
SLOT_WIDTH = 4
FAMILY = "belenos_mode_swap_interleaved"
CASES = ROOT / "results/quandela/cases" / FAMILY
SOURCES = ROOT / "results/quandela/cases"
LAYOUTS = {"packed": "box_kite_photonic_packed", "swapped": "box_kite_photonic_packed_swapped"}
EARLIER = {"packed": "qpu_belenos/box_kite_photonic_packed", "swapped": "qpu_belenos/box_kite_photonic_packed_swapped"}
DESIGN = "docs/design/belenos-mode-swap-interleaved-case.md"
PLATFORM = "qpu:belenos"
JOBS = {"job-00": (0, 1), "job-01": (2, 3), "job-02": (4,)}
# The iterations of an even block set as (layout, arm, repeat); an odd block set runs the mirror with the layouts
# exchanged. Each replicate sits at the mean time of its layout's primary pair.
SEQUENCE = (
    ("packed", "primary", 0),
    ("swapped", "primary", 0),
    ("packed", "replicate", 0),
    ("swapped", "replicate", 0),
    ("packed", "primary", 1),
    ("swapped", "primary", 1),
)
MIRROR = {"packed": "swapped", "swapped": "packed"}
ITERATIONS_PER_SET = len(SEQUENCE)
SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T043029Z.json"
# One primary seed per (set, layout) in job, set and layout order; both repeats of a layout take it.
COMPILATION_SEEDS = (41251, 50785, 63940, 45911, 11390, 34773, 25508, 5306, 15866, 64854)
REPLICATE_SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T051136Z.json"
# One replicate seed per (set, layout) in the same order, indices 0 to 9 of REPLICATE_SEED_DRAW; each is used once.
REPLICATE_COMPILATION_SEEDS = (25506, 59555, 30521, 43387, 59603, 13108, 18076, 53193, 3029, 46479)
SAMPLES_PER_ITERATION = 6000
SHOTS_PER_ITERATION = 18000
MAX_DURATION = 300
# Duration bound of one job from the retained qpu:belenos runs: the largest per-iteration cost of the 12 to 32
# iteration single-photon jobs (115 s over 12 iterations), and the largest all-in cost per sample of the six-photon
# packed and swapped jobs (55 s over 60,000 samples). STRESS_FACTOR scales the sample term by the 1.8x spread that
# the retained two-photon packed and swapped jobs show for 20,000 samples (19 s against 34 s); the stressed bound
# stays within DURATION_MARGIN of MAX_DURATION.
SECONDS_PER_ITERATION = 9.6
SECONDS_PER_SAMPLE = 0.917e-3
STRESS_FACTOR = 1.8
DURATION_MARGIN = 0.8
# A block whose share moves by more than Z_CRITICAL standard errors moved, the criterion of
# qd_packed_mode_swap_analysis.
Z_CRITICAL = 4.5
DRIFT_ALPHA = 0.01
# Blocks beyond the mesh variance that place the contrast beyond it; one block in 30 crosses Z_CRITICAL against an
# estimated scale with probability near 3 percent, two with probability below 0.1 percent.
MOVED_BLOCKS_MIN = 2
# The sign-specific bound of the slot predictor's interval, and the reproduction bounds of the comparison with the
# earlier deltas.
SLOT_SIGN_BOUND = 0.3
REPRODUCE_FLOOR = 0.3
REPRODUCE_SIGN_ALPHA = 0.01
UNCORRELATED_CEILING = 0.7
TOLERANCE = 1e-9

READING = (
    "The design shows whether moving a packed block changes its algebra-mode share by more than that share varies "
    "between compiled meshes of one layout, and whether the per-block changes reproduce the changes of the earlier "
    "separate jobs. Reproduction rules out hour-scale drift as their source; changes that do not follow the earlier "
    "deltas, or that stay within the mesh variance, read as mesh-specific. The slot predictor of the pooled blocks "
    "reads the sign of the chip-mode effect. The design does not show how a chip mode changes a share."
)

# Reading of the pooled analysis by the placement class and the comparison class.
READING_TABLE = {
    ("none", "any"): "no moves: the earlier separation fails",
    ("beyond", "reproduce"): "moves beyond the mesh variance reproduce the earlier deltas: not hour-scale drift",
    ("beyond", "uncorrelated"): "moves beyond the mesh variance do not follow the earlier deltas: mesh-specific",
    ("beyond", "indeterminate"): "moves beyond the mesh variance with the earlier deltas neither reproduced nor "
    "excluded: inconclusive",
    ("within", "reproduce"): "moves within the per-block mesh variance reproduce the earlier deltas: not hour-scale "
    "drift, placement per block unresolved",
    ("within", "uncorrelated"): "moves within the mesh variance do not follow the earlier deltas: mesh-specific",
    ("within", "indeterminate"): "moves within the mesh variance with the earlier deltas neither reproduced nor "
    "excluded: inconclusive",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def q2(entry: list[str]) -> float:
    """The real number a + b sqrt(2) of a retained circuit entry [a, b]."""
    return float(Fraction(entry[0])) + float(Fraction(entry[1])) * math.sqrt(2)


def source(layout: str, block_set: int) -> tuple[dict[str, Any], dict[str, Any]]:
    directory = SOURCES / LAYOUTS[layout] / f"job-{block_set:02d}"
    manifest = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((directory / "circuit.json").read_text(encoding="utf-8"))
    return manifest, circuit


def slot_unitaries(circuit: dict[str, Any]) -> dict[int, np.ndarray]:
    """The 4 x 4 real block of each slot, keyed by its first chip mode."""
    blocks = {}
    for component in circuit["components"]:
        at = int(component["at"])
        require(at % SLOT_WIDTH == 0, f"component at {at} is not slot-aligned")
        matrix = np.array([[q2(entry) for entry in row] for row in component["unitary"]])
        require(np.allclose(matrix.T @ matrix, np.eye(SLOT_WIDTH), atol=TOLERANCE), f"slot {at} is not orthogonal")
        blocks[at] = matrix
    return blocks


def full_unitary(blocks: dict[int, np.ndarray]) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    for at, matrix in blocks.items():
        full[at : at + SLOT_WIDTH, at : at + SLOT_WIDTH] = matrix
    return full


def template(blocks: dict[int, np.ndarray]) -> tuple[dict[str, Any], dict[str, float]]:
    """Six independent 4-mode triangular meshes, one per slot, with globally numbered parameters; an empty slot takes
    the identity."""
    ops: list[list[Any]] = []
    parameters: dict[str, float] = {}
    for at in range(0, MODES, SLOT_WIDTH):
        mesh, values = photonic_template(blocks.get(at, np.eye(SLOT_WIDTH)).astype(complex))
        base = len(parameters)
        for kind, mode, index in mesh["ops"]:
            ops.append([kind, mode + at, None if index is None else index + base])
        for name, value in values.items():
            parameters[f"x{int(name[1:]) + base}"] = value
    return {"ops": ops, "parameters": len(parameters)}, parameters


def seed_index(job: str, block_set: int, layout: str) -> int:
    sets = [(name, s) for name, group in JOBS.items() for s in group]
    return 2 * sets.index((job, block_set)) + (0 if layout == "packed" else 1)


def seed_of(job: str, block_set: int, layout: str, arm: str) -> int:
    seeds = COMPILATION_SEEDS if arm == "primary" else REPLICATE_COMPILATION_SEEDS
    return seeds[seed_index(job, block_set, layout)]


def rows(job: str) -> list[dict[str, Any]]:
    out = []
    for block_set in JOBS[job]:
        for layout, arm, repeat in SEQUENCE:
            shown = layout if block_set % 2 == 0 else MIRROR[layout]
            out.append({"block_set": block_set, "layout": shown, "arm": arm, "repeat": repeat})
    return out


def iterations(job: str) -> int:
    return ITERATIONS_PER_SET * len(JOBS[job])


def bound_seconds(job: str, factor: float = 1.0) -> float:
    """Upper bound on the job's duration: SECONDS_PER_ITERATION per iteration plus factor x SECONDS_PER_SAMPLE per
    sample."""
    count = iterations(job)
    return count * SECONDS_PER_ITERATION + factor * SECONDS_PER_SAMPLE * SAMPLES_PER_ITERATION * count


def expected_seconds(job: str) -> int:
    """The written case's expected seconds: the nominal bound rounded up to ten seconds."""
    return int(math.ceil(bound_seconds(job) / 10.0)) * 10


def build_setting(item: tuple[int, dict[str, Any], str]) -> tuple[dict[str, Any], dict[str, Any]]:
    index, row, job = item
    manifest, circuit = source(row["layout"], row["block_set"])
    blocks = slot_unitaries(circuit)
    mesh, parameters = template(blocks)
    full = full_unitary(blocks)
    photons = [mode for mode, n in enumerate(circuit["input_state"]) if n]
    setting = {
        "name": f"set{row['block_set']}-{row['layout']}-{row['arm']}{row['repeat']}",
        "observation_index": index,
        **row,
        "source": f"{LAYOUTS[row['layout']]}/job-{row['block_set']:02d}",
        "blocks": [
            {key: block[key] for key in ("config", "kind", "offset", "photons", "m", "t", "roles", "p_algebra")}
            for block in manifest["blocks"]
        ],
        "circuit_params": parameters,
        "compilation_seed": seed_of(job, row["block_set"], row["layout"], row["arm"]),
        "column": [[float(value.real), float(value.imag)] for value in full[:, photons[0]]],
        "operator": encoded(full),
    }
    return {**mesh, "input_state": circuit["input_state"]}, setting


def preregistered() -> dict[str, Any]:
    return {
        "observable": "per block and iteration, a = (samples with exactly one click in the block's slot that land on "
        "an algebra mode) / (samples with exactly one click in the slot), the observable of "
        "scripts/qd_packed_mode_swap_analysis.py",
        "order": "per block set, the six iterations alternate the layouts, packed first for an even block set and "
        "swapped first for an odd one; each layout runs its primary seed at its first and last slot and its "
        "replicate seed at the slot between them, so the replicate sits at the mean time of the primary pair and "
        "the same-layout replicate contrast carries no linear drift; the mesh-averaged placement contrast then "
        "carries a linear-drift imbalance of one slot whose sign flips with the parity of the block set",
        "binding": "a result iteration binds to its setting by circuit_params and compilation_seed; the two "
        "primary repeats of one layout share both and bind in submission order; an iteration that returns no "
        "counts holds its slot",
        "analysis": "--analyze pools the three runs into one table over all 30 blocks; every statistic below is "
        "withheld unless all 30 blocks are complete, meaning all six iterations of their set returned counts",
        "mesh_identity": "the sha256 of each returned computed_circuit; the two primary repeats of a layout "
        "request one mesh, and a pair with different digests drops out of the validity statistic; the reading "
        "is withheld unless every replicate digest differs from its primary digest",
        "validity": "per job, per block and layout, z = (a_repeat1 - a_repeat0) / two-sample se of the primary "
        "repeats; D = sum z^2 over the job's mesh-identical pairs against chi-square with that many degrees of "
        f"freedom, drift detected when p < {DRIFT_ALPHA}; a job with no mesh-identical pair withholds the "
        "placement reading. D checks that the within-job contrast is internally valid and carries no statement "
        "about the earlier hour-scale drift. kappa^2 = max(1, D / dof) of the job scales every binomial variance "
        "of that job's blocks",
        "mesh_variance": "per block and layout, R = a_replicate - a_primary(pooled repeats) has variance 2 "
        "sigma^2 + kappa^2 (binomial variances); sigma^2 = max(0, mean over the 60 contrasts of (R^2 - kappa^2 "
        "binomial variance) / 2) is the per-seed mesh variance of a",
        "placement": "per block, delta = (a_swapped_primary + a_swapped_replicate) / 2 - (a_packed_primary + "
        "a_packed_replicate) / 2, which under no placement effect has variance sigma^2 plus kappa^2 (sum of the four "
        f"binomial variances) / 4; z = delta / sqrt(sigma^2 + kappa^2 binomial variance); a block moved beyond the "
        f"mesh variance when |z| > {Z_CRITICAL}; the placement lies beyond the mesh variance when at least "
        f"{MOVED_BLOCKS_MIN} blocks do; blocks moved against binomial error alone are those of decide() in "
        "scripts/qd_packed_mode_swap_analysis.py on the pooled table",
        "slot_predictor": "decide() on the pooled packed and swapped table of all iterations of each layout; the "
        f"slot predictor's r with its Fisher 95 percent interval reads a reversed-sign chip-mode effect when the "
        f"upper bound is below -{SLOT_SIGN_BOUND}, a positive-sign chip-mode effect when the lower bound is above "
        f"+{SLOT_SIGN_BOUND}, and no sign-specific chip-mode reading otherwise",
        "comparison": "per block, delta_new = a_swapped - a_packed of the pooled table against delta_old of the "
        "retained qpu_belenos box_kite_photonic_packed and box_kite_photonic_packed_swapped series; reproduce when "
        f"Pearson r has a lower bound above {REPRODUCE_FLOOR} and the blocks of equal sign beat one half with a one-"
        f"sided exact binomial p < {REPRODUCE_SIGN_ALPHA}; uncorrelated when r has a lower bound at or below "
        f"{REPRODUCE_FLOOR} and an upper bound below {UNCORRELATED_CEILING}; indeterminate otherwise",
        "reading_table": {" / ".join(key): value for key, value in READING_TABLE.items()},
        "interpretation": READING,
    }


def documents(job: str) -> dict[str, bytes]:
    built = ordered_map(build_setting, [(index, row, job) for index, row in enumerate(rows(job))], min_items=1)
    shape = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == shape, f"iteration {index} needs another mesh or input than iteration 0")
    settings = [setting for _, setting in built]
    circuit = {
        "schema": "qd-template-circuit-v1",
        "modes": MODES,
        "input_state": shape["input_state"],
        "parameters": shape["parameters"],
        "ops": shape["ops"],
    }
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM, "sim:belenos"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES_PER_ITERATION * len(settings),
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": preregistered(),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def check_job(job: str) -> str:
    case = CASES / job
    retained = {name: (case / name).read_bytes() for name in ("cases.json", "circuit.json")}
    for name, data in documents(job).items():
        require(retained[name] == data, f"{case.relative_to(ROOT)}/{name} differs from the builder's bytes")
    manifest = json.loads(retained["cases.json"])
    circuit = json.loads(retained["circuit.json"])
    _, settings = template_experiment(manifest, circuit)
    require(len(settings) == iterations(job), f"{job}: {len(settings)} settings bound")
    stressed = bound_seconds(job, STRESS_FACTOR)
    require(
        stressed <= DURATION_MARGIN * MAX_DURATION and bound_seconds(job) <= expected_seconds(job),
        f"{job}: the duration bound {stressed:.0f} s leaves no margin under {MAX_DURATION} s",
    )
    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
    for setting in settings:
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())
        _, retained_circuit = source(setting["layout"], setting["block_set"])
        expected = full_unitary(slot_unitaries(retained_circuit))
        require(np.abs(unitary - expected).max() < TOLERANCE, f"{setting['name']}: template unitary differs")
    return (
        f"{FAMILY} {job}: {len(settings)} iterations bound to the retained packed and swapped unitaries, "
        f"duration bound {bound_seconds(job):.0f} s ({stressed:.0f} s stressed) of {MAX_DURATION} s"
    )


def check() -> int:
    seeds = list(COMPILATION_SEEDS) + list(REPLICATE_COMPILATION_SEEDS)
    require(len(set(seeds)) == len(seeds), "a compilation seed repeats")
    for line in ordered_map(check_job, sorted(JOBS), min_items=1):
        print(line)
    return 0


def build(job: str) -> int:
    out = CASES / job
    out.mkdir(parents=True, exist_ok=True)
    built = documents(job)
    for name, data in built.items():
        path = out / name
        require(not path.exists() or path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        if not path.exists():
            path.write_bytes(data)
    print(f"{FAMILY} {job}: {out.relative_to(ROOT)} cases.json {sha256_bytes(built['cases.json'])}")
    return 0


def block_shares(setting: dict[str, Any], counts: dict[str, int]) -> list[dict[str, Any]]:
    parsed = [([int(v) for v in key.strip("|>").split(",")], count) for key, count in counts.items()]
    out = []
    for block in setting["blocks"]:
        offset, width = block["offset"], len(block["roles"])
        algebra = [k for k, role in enumerate(block["roles"]) if role != "dilation"]
        one = hit = 0
        for modes, count in parsed:
            window = modes[offset : offset + width]
            if sum(window) == 1:
                one += count
                hit += count if any(window[k] for k in algebra) else 0
        out.append({"key": (json.dumps(block["m"]), block["t"]), "slot": offset // SLOT_WIDTH, "n": one, "hit": hit})
    return out


def two_sample_z(first: tuple[int, int], second: tuple[int, int]) -> float | None:
    (h0, n0), (h1, n1) = first, second
    if not n0 or not n1:
        return None
    a0, a1 = h0 / n0, h1 / n1
    se = math.sqrt(a0 * (1 - a0) / n0 + a1 * (1 - a1) / n1)
    return (a1 - a0) / se if se > 0 else None


def request_key(params: Any, seed: Any) -> str:
    return json.dumps([params, seed], sort_keys=True)


def bind_iterations(settings: list[dict[str, Any]], results: dict[str, Any]) -> tuple[dict[int, dict[str, Any]], int]:
    """The counted result entries by setting index, and the number of entries without counts.

    An entry binds by its echoed circuit_params and compilation_seed; entries of one key bind in submission order. An
    entry without counts (qd_platform.result_summary writes a missing, malformed or error entry for an iteration a
    cut-short job lost) holds the slot its echo names, so a later counted repeat of the same key keeps its label.
    """
    pending: dict[str, list[int]] = {}
    for index, setting in enumerate(settings):
        pending.setdefault(request_key(setting["circuit_params"], setting["compilation_seed"]), []).append(index)
    bound: dict[int, dict[str, Any]] = {}
    uncounted = 0
    for entry in results.get("iterations") or []:
        request = entry.get("iteration") or {}
        key = request_key(request.get("circuit_params"), request.get("compilation_seed"))
        if not entry.get("counts"):
            uncounted += 1
            if pending.get(key):
                pending[key].pop(0)
            continue
        require(bool(pending.get(key)), "a result iteration binds to no remaining setting")
        bound[pending[key].pop(0)] = entry
    return bound, uncounted


def merge(cells: list[dict[str, Any]]) -> dict[str, Any]:
    return {"n": sum(c["n"] for c in cells), "hit": sum(c["hit"] for c in cells)}


def share(cell: dict[str, Any]) -> float:
    return cell["hit"] / cell["n"]


def variance(cell: dict[str, Any]) -> float:
    a = share(cell)
    return a * (1 - a) / cell["n"]


def earlier_deltas() -> dict[tuple[str, int], float]:
    """delta_old = a_swapped - a_packed per block of the retained qpu_belenos series."""
    packed, swapped = collect(EARLIER["packed"]), collect(EARLIER["swapped"])
    return {key: swapped[key]["a"] - packed[key]["a"] for key in packed if key in swapped}


def load_runs(runs: list[Path]) -> list[dict[str, Any]]:
    loaded = []
    for run in runs:
        raw = (run / "cases.json").read_bytes()
        manifest = json.loads(raw)
        job = manifest.get("job")
        require(job in JOBS, f"{run}: job {job!r} is not a job of the case")
        frozen = (CASES / job / "cases.json").read_bytes()
        require(raw == frozen, f"{run}/cases.json differs from the frozen {job} case")
        results_bytes = (run / "results.json").read_bytes()
        loaded.append(
            {
                "run": run,
                "job": job,
                "manifest": manifest,
                "results": json.loads(results_bytes),
                "results_sha256": sha256_bytes(results_bytes),
            }
        )
    require(sorted(r["job"] for r in loaded) == sorted(JOBS), f"the runs hold jobs {[r['job'] for r in loaded]}")
    return loaded


def collect_cells(loaded: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-iteration block cells keyed by (block, layout, arm, repeat), with block and set bookkeeping."""
    cells: dict[tuple[Any, ...], dict[str, Any]] = {}
    info: dict[tuple[str, int], dict[str, Any]] = {}
    sets_total: dict[int, int] = {}
    sets_counted: dict[int, int] = {}
    bound_total = uncounted_total = requested = 0
    for item in loaded:
        settings = item["manifest"]["settings"]
        bound, uncounted = bind_iterations(settings, item["results"])
        bound_total += len(bound)
        uncounted_total += uncounted
        requested += len(settings)
        for index, setting in enumerate(settings):
            sets_total[setting["block_set"]] = sets_total.get(setting["block_set"], 0) + 1
            entry = bound.get(index)
            if entry is None:
                continue
            circuit = (entry.get("result_fields") or {}).get("computed_circuit")
            digest = hashlib.sha256(json.dumps(circuit, sort_keys=True).encode()).hexdigest() if circuit else None
            shares = block_shares(setting, entry["counts"])
            if any(share_["n"] == 0 for share_ in shares):
                continue
            sets_counted[setting["block_set"]] = sets_counted.get(setting["block_set"], 0) + 1
            for share_, block in zip(shares, setting["blocks"], strict=True):
                key = share_["key"]
                cells[(key, setting["layout"], setting["arm"], setting["repeat"])] = {
                    **share_,
                    "mesh": digest,
                    "job": item["job"],
                    "set": setting["block_set"],
                }
                known = info.setdefault(
                    key, {"set": setting["block_set"], "job": item["job"], "p": float(Fraction(block["p_algebra"]))}
                )
                require(known["set"] == setting["block_set"], f"block {key} sits in two block sets")
    complete_sets = {k for k, total in sets_total.items() if sets_counted.get(k, 0) == total}
    return {
        "cells": cells,
        "info": info,
        "complete_sets": complete_sets,
        "sets": sorted(sets_total),
        "bound": bound_total,
        "uncounted": uncounted_total,
        "requested": requested,
    }


def validity(data: dict[str, Any]) -> dict[str, Any]:
    """The within-job drift statistic of the primary repeat pairs, per job and pooled."""
    jobs: dict[str, dict[str, Any]] = {job: {"statistic": 0.0, "dof": 0} for job in JOBS}
    pair_rows = []
    cells, info = data["cells"], data["info"]
    for key in sorted(info):
        job = info[key]["job"]
        for layout in ("packed", "swapped"):
            first, second = cells.get((key, layout, "primary", 0)), cells.get((key, layout, "primary", 1))
            if first is None or second is None:
                continue
            z = two_sample_z((first["hit"], first["n"]), (second["hit"], second["n"]))
            same = first["mesh"] is not None and first["mesh"] == second["mesh"]
            pair_rows.append({"block": list(key), "layout": layout, "job": job, "z": z, "same_mesh": same})
            if z is not None and same:
                jobs[job]["statistic"] += z * z
                jobs[job]["dof"] += 1
    total_statistic = sum(j["statistic"] for j in jobs.values())
    total_dof = sum(j["dof"] for j in jobs.values())
    for entry in jobs.values():
        dof = entry["dof"]
        p_value = float(chi2.sf(entry["statistic"], dof)) if dof else None
        entry["p_value"] = p_value
        entry["detected"] = None if p_value is None else p_value < DRIFT_ALPHA
        entry["inflation"] = max(1.0, entry["statistic"] / dof) if dof else None
    pooled_p = float(chi2.sf(total_statistic, total_dof)) if total_dof else None
    return {
        "rows": pair_rows,
        "jobs": jobs,
        "statistic": total_statistic,
        "dof": total_dof,
        "p_value": pooled_p,
        "detected": None if pooled_p is None else pooled_p < DRIFT_ALPHA,
    }


def mesh_cells(data: dict[str, Any], key: tuple[str, int]) -> dict[str, dict[str, Any]] | None:
    cells = data["cells"]
    parts = {
        "packed_primary": [cells.get((key, "packed", "primary", r)) for r in (0, 1)],
        "swapped_primary": [cells.get((key, "swapped", "primary", r)) for r in (0, 1)],
        "packed_replicate": [cells.get((key, "packed", "replicate", 0))],
        "swapped_replicate": [cells.get((key, "swapped", "replicate", 0))],
    }
    if any(c is None for group in parts.values() for c in group):
        return None
    return {name: merge([c for c in group if c is not None]) for name, group in parts.items()}


def replicate_meshes_distinct(data: dict[str, Any]) -> bool:
    cells = data["cells"]
    for key in data["info"]:
        for layout in ("packed", "swapped"):
            primary, replicate = cells[(key, layout, "primary", 0)], cells[(key, layout, "replicate", 0)]
            if primary["mesh"] is None or replicate["mesh"] is None or primary["mesh"] == replicate["mesh"]:
                return False
    return True


def mesh_and_placement(data: dict[str, Any], inflation: dict[str, float]) -> dict[str, Any]:
    """The per-seed mesh variance from the replicate contrasts and the placement test against it."""
    contrasts: list[dict[str, Any]] = []
    deltas: list[dict[str, Any]] = []
    for key in sorted(data["info"]):
        merged = mesh_cells(data, key)
        if merged is None:
            raise RuntimeError(f"block {key} lacks a cell")
        kappa2 = inflation[data["info"][key]["job"]]
        for layout in ("packed", "swapped"):
            primary, replicate = merged[f"{layout}_primary"], merged[f"{layout}_replicate"]
            r = share(replicate) - share(primary)
            v = kappa2 * (variance(primary) + variance(replicate))
            contrasts.append({"block": list(key), "layout": layout, "r": r, "v": v})
        delta = (share(merged["swapped_primary"]) + share(merged["swapped_replicate"])) / 2 - (
            share(merged["packed_primary"]) + share(merged["packed_replicate"])
        ) / 2
        v_delta = kappa2 * sum(variance(merged[name]) for name in merged) / 4
        deltas.append({"block": list(key), "delta": delta, "v": v_delta})
    sigma2 = max(0.0, sum((c["r"] ** 2 - c["v"]) / 2 for c in contrasts) / len(contrasts))
    ratio = sum(c["r"] ** 2 for c in contrasts) / sum(c["v"] for c in contrasts)
    moved = 0
    for row in deltas:
        scale = math.sqrt(sigma2 + row["v"])
        row["z"] = row["delta"] / scale if scale > 0 else None
        row["moved"] = row["z"] is not None and abs(row["z"]) > Z_CRITICAL
        moved += bool(row["moved"])
    return {
        "mesh_variance": {
            "sigma2": sigma2,
            "sigma": math.sqrt(sigma2),
            "excess_ratio": ratio,
            "contrasts": len(contrasts),
            "rows": contrasts,
        },
        "placement": {
            "rows": deltas,
            "blocks": len(deltas),
            "moved_beyond_mesh": moved,
            "beyond_mesh_variance": moved >= MOVED_BLOCKS_MIN,
        },
    }


def pooled_table(data: dict[str, Any]) -> dict[str, dict[tuple[str, int], dict[str, Any]]]:
    """Per layout and block, the iterations of every arm pooled: the table decide() reads."""
    table: dict[str, dict[tuple[str, int], dict[str, Any]]] = {"packed": {}, "swapped": {}}
    cells = data["cells"]
    for key, block in data["info"].items():
        for layout in table:
            parts = [c for (k, lay, _, _), c in cells.items() if k == key and lay == layout]
            pooled = merge(parts)
            table[layout][key] = {"slot": parts[0]["slot"], "p": block["p"], **pooled, "a": share(pooled)}
    return table


def moved_against_binomial(table: dict[str, dict[tuple[str, int], dict[str, Any]]]) -> int:
    """Blocks whose pooled packed-swapped contrast exceeds Z_CRITICAL binomial standard errors, as in decide()."""
    count = 0
    for key, packed in table["packed"].items():
        swapped = table["swapped"][key]
        z = two_sample_z((packed["hit"], packed["n"]), (swapped["hit"], swapped["n"]))
        count += z is not None and abs(z) > Z_CRITICAL
    return count


def slot_sign(slot_predictor: Any) -> str:
    if slot_predictor is None:
        return "undefined: a constant residual vector"
    _, lower, upper = slot_predictor
    if upper < -SLOT_SIGN_BOUND:
        return "reversed-sign chip-mode effect"
    if lower > SLOT_SIGN_BOUND:
        return "positive-sign chip-mode effect"
    return "no sign-specific chip-mode reading"


def compare_earlier(table: dict[str, dict[tuple[str, int], dict[str, Any]]], old: dict[tuple[str, int], float]) -> dict:
    keys = sorted(table["packed"])
    missing = [key for key in keys if key not in old]
    require(not missing, f"the earlier series lacks blocks {missing}")
    new = [table["swapped"][key]["a"] - table["packed"][key]["a"] for key in keys]
    earlier = [old[key] for key in keys]
    signed = [(u > 0) == (v > 0) for u, v in zip(new, earlier, strict=True) if u != 0 and v != 0]
    agree = sum(signed)
    sign_p = float(binomtest(agree, len(signed), 0.5, alternative="greater").pvalue) if signed else None
    r = correlation(new, earlier)
    if r is not None and r[1] > REPRODUCE_FLOOR and sign_p is not None and sign_p < REPRODUCE_SIGN_ALPHA:
        verdict = "reproduce"
    elif r is not None and r[1] <= REPRODUCE_FLOOR and r[2] < UNCORRELATED_CEILING:
        verdict = "uncorrelated"
    else:
        verdict = "indeterminate"
    return {
        "blocks": len(keys),
        "sign_agreement": agree,
        "sign_comparable": len(signed),
        "sign_p": sign_p,
        "pearson": None if r is None else list(r),
        "verdict": verdict,
        "rows": [{"block": list(k), "new": u, "old": v} for k, u, v in zip(keys, new, earlier, strict=True)],
    }


def read(placement: dict[str, Any], binomial_moved: int, comparison: dict[str, Any]) -> str:
    if binomial_moved == 0:
        return READING_TABLE[("none", "any")]
    placed = "beyond" if placement["beyond_mesh_variance"] else "within"
    return READING_TABLE[(placed, comparison["verdict"])]


def analyze(runs: list[Path], earlier: dict[tuple[str, int], float] | None = None) -> dict[str, Any]:
    loaded = load_runs(runs)
    data = collect_cells(loaded)
    check_ = validity(data)
    withheld: list[str] = []
    complete = len(data["info"]) == 30 and all(info["set"] in data["complete_sets"] for info in data["info"].values())
    if not complete:
        withheld.append("not every block set returned counts for all six iterations")
    dofs_ok = all(entry["dof"] > 0 for entry in check_["jobs"].values())
    if not dofs_ok:
        withheld.append("a job has no mesh-identical repeat pair (dof 0)")
    distinct = complete and replicate_meshes_distinct(data)
    if complete and not distinct:
        withheld.append("a replicate iteration returned the mesh of its primary iteration or no mesh digest")
    record: dict[str, Any] = {
        "runs": [{"run": r["run"].name, "job": r["job"], "results_sha256": r["results_sha256"]} for r in loaded],
        "iterations_bound": data["bound"],
        "iterations_uncounted": data["uncounted"],
        "iterations_requested": data["requested"],
        "validity": check_,
        "withheld": withheld,
    }
    if withheld:
        record["reading"] = "withheld: " + "; ".join(withheld)
        return record
    inflation = {job: entry["inflation"] for job, entry in check_["jobs"].items()}
    record.update(mesh_and_placement(data, inflation))
    table = pooled_table(data)
    try:
        slot = decide(table["packed"], table["swapped"])
    except ValueError as error:
        slot = {"verdict": "undetermined", "reason": str(error), "slot_predictor": None, "moved": []}
    record["slot_predictor"] = {
        "verdict": slot["verdict"],
        "block_predictor": slot.get("block_predictor"),
        "slot_predictor": slot.get("slot_predictor"),
        "reading": slot_sign(slot.get("slot_predictor")),
        "reason": slot.get("reason"),
    }
    record["moved_binomial"] = moved_against_binomial(table)
    record["comparison"] = compare_earlier(table, earlier_deltas() if earlier is None else earlier)
    record["reading"] = read(record["placement"], record["moved_binomial"], record["comparison"])
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", choices=sorted(JOBS))
    group.add_argument("--analyze", type=Path, nargs=len(JOBS), metavar="RUN")
    args = parser.parse_args()
    if args.build:
        return build(args.build)
    if args.analyze:
        record = analyze(args.analyze)
        text = json.dumps(record, indent=1, sort_keys=True) + "\n"
        for run in args.analyze:
            (run / "analysis.json").write_text(text, encoding="utf-8")
        print(record["reading"])
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
