#!/usr/bin/env python3
"""First-principles checks behind the Belenos best-mesh teleportation replay.

The script reads the retained teleportation rehearsal runs (job-02, its exact replay and job-03) and computes, per
served mesh, the quantities that decide how a winner-and-loser replay of the job-02 and job-03 compilation seeds
reads:

- compiled: the noiseless three-photon propagation through each returned ``computed_circuit`` unitary, scored by the
  rehearsal classifier, against the target operator of its setting. A compiled-mesh shortfall that differs by seed
  places the per-seed error in the compiler; equal unit scores place it on the chip.
- shrinkage: the normal-normal hierarchical estimate of each input's true block A minus block B difference and the
  expected winner-minus-loser gap, with the directional Benjamini-Hochberg sign decisions.
- replay_power: the posterior-predictive power of a winner-and-loser replay at two and four jobs, with inputs dropped
  when a seed returns a new mesh, and its size when no mesh error persists.
- replay_budget: the shot cap and credits per replay job from the lossiest retained mesh.
- acceptance: acceptance per sample against correctness between the two meshes of each input.
- source_shift: the source model's predicted conditional fidelity at each calibration read of the day.
- structural: each mesh's conditional fidelity under unmodeled heater and coupler errors, tested within input.

One QRNG value seeds a SeedSequence whose two children drive the power simulation and the mesh-error draws.

Usage: belenos_best_mesh_first_principles.py --out PATH --seed qrng:<draw>#<index> [--run KEY RUN_DIR BLOCK ...]

The estimators live in gororoba_quantum/mesh_selection.py with explicit inputs; this script selects the runs.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qd_belenos_mesh as mesh  # noqa: E402
import qd_teleportation_rehearsal as tr  # noqa: E402
from qd_network_protocol import propagate  # noqa: E402

import mesh_selection as ms  # noqa: E402
import qrng_seeds  # noqa: E402
from parallel import ordered_map  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
RUN_NAMES = {
    "job-02": "2026-10-31T035736Z-qpu_belenos-teleportation_rehearsal-job-02",
    "job-02-replay": "2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay",
    "job-03": "2026-10-31T040337Z-qpu_belenos-teleportation_rehearsal-job-03",
}


def clicks_of(unitary: np.ndarray, source: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution of the noiseless three-photon propagation through ``unitary``."""
    output = propagate(unitary, {tuple(source): 1.0 + 0.0j})
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, amplitude in output.items():
        key = tuple(1 if count else 0 for count in occupation)
        clicks[key] = clicks.get(key, 0.0) + abs(amplitude) ** 2
    return clicks


def total_variation(left: Mapping[tuple[int, ...], float], right: Mapping[tuple[int, ...], float]) -> float:
    """Total variation distance of two click distributions: the complete observable of threshold detection, blind to
    the input-photon and output-mode phases that a column comparison would count."""
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def compiled_row(item: tuple[str, int, Mapping[str, Any], str, Sequence[int]]) -> dict[str, Any]:
    run, index, setting, circuit_text, layout = item
    elements = mesh.decode(circuit_text)
    arch = mesh.run_architecture(elements)
    phases = mesh.mesh_phases(arch, elements)
    compiled = mesh.unitary(arch, phases)
    target = tr.operator_of(dict(setting))
    source = tr.source_state(layout)
    occupied = [mode for mode, count in enumerate(source) if count]
    label = setting["label"]
    target_clicks, compiled_clicks = clicks_of(target, source), clicks_of(compiled, source)
    ideal_acc, ideal_cor = tr.scored(label, target_clicks, layout)
    comp_acc, comp_cor = tr.scored(label, compiled_clicks, layout)
    power = np.abs(compiled[:, occupied]) ** 2 - np.abs(target[:, occupied]) ** 2
    return {
        "run": run,
        "index": index,
        "label": label,
        "compilation_seed": setting["compilation_seed"],
        "mesh_sha": hashlib.sha256(mesh.unzip(circuit_text).encode()).hexdigest()[:8],
        "heater_phase_rad": float(sum(phases)),
        "click_total_variation": total_variation(compiled_clicks, target_clicks),
        "max_column_power_difference": float(np.max(np.abs(power))),
        "target_accepted_probability": ideal_acc,
        "target_conditional_fidelity": ideal_cor / ideal_acc,
        "compiled_accepted_probability": comp_acc,
        "compiled_conditional_fidelity": comp_cor / comp_acc,
    }


def compiled_section(runs: Mapping[str, tuple[Path, str]]) -> list[dict[str, Any]]:
    items = []
    for run, (directory, _) in runs.items():
        cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        circuits = mesh.computed_circuits(directory)
        if len(circuits) != len(cases["settings"]):
            raise ValueError(f"{run}: {len(circuits)} computed circuits for {len(cases['settings'])} settings")
        for index, (setting, text) in enumerate(zip(cases["settings"], circuits, strict=True)):
            items.append((run, index, setting, text, layout))
    return ordered_map(compiled_row, items, min_items=1)


LABELS = ("+Z", "-Z", "+X", "-X", "+Y", "-Y")
BLOCKS = {"job-02": "A", "job-02-replay": "A", "job-03": "B"}
DEFAULT_RUNS = {run: (RUNS / name, BLOCKS[run]) for run, name in RUN_NAMES.items()}


def representatives(runs: Mapping[str, tuple[Path, str]]) -> dict[str, str]:
    """The first run of each block, whose returned meshes stand for the block (a block's other runs replay its
    seeds)."""
    out: dict[str, str] = {}
    for run, (_, block) in runs.items():
        out.setdefault(block, run)
    if sorted(out) != ["A", "B"]:
        raise ValueError(f"the selected runs form blocks {sorted(out)}, not A and B")
    return out


TAU_GRID = np.linspace(0.0, 0.25, 1001)
FDR_Q = 0.10
ALPHA_ONE_SIDED = 0.05
Z_ONE_SIDED = 1.6448536269514722
REPLAY_SAMPLES = 1200
TRIALS = 200_000
DROPOUTS = (0, 1, 2, 3)
JOB_COUNTS = (2, 4)


def iterations(runs: Mapping[str, tuple[Path, str]]) -> list[dict[str, Any]]:
    """Every retained iteration of the selected runs with its run key and block."""
    rows: list[dict[str, Any]] = []
    for run, (directory, block) in runs.items():
        analysis = json.loads((directory / "analysis.json").read_text(encoding="utf-8"))
        rows.extend({**row, "run": run, "block_of_seed": block} for row in analysis["iterations"])
    return rows


def block_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    return ms.block_counts(rows, LABELS, tr.REJECTIONS)


exact_permutation_r = ms.exact_permutation_r


def acceptance_section(counts: Mapping[str, Mapping[str, Mapping[str, float]]]) -> dict[str, Any]:
    """Acceptance per sample against correctness, between the two meshes of each input.

    Every mesh of one input implements the same logical unitary on the same chip modes, so the ideal accepted share
    is common to both; a difference in acceptance per sample is mesh error. Calsamiglia and Lutkenhaus bound a passive
    linear Bell analyzer at one half, so the ideal analyzer accepts exactly its two separable patterns and excess
    acceptance means events from outside them (a misidentified Bell outcome, a herald photon routed into an accepted
    pattern). The chance model scores such excess events at correctness one half: the higher-acceptance mesh then
    reads (a_lo f_lo + (a_hi - a_lo) / 2) / a_hi."""
    rows = {}
    deltas_a, deltas_f, deltas_h = [], [], []
    for label in LABELS:
        a, b = counts[label]["A"], counts[label]["B"]
        acc = {k: c["accepted"] / c["samples"] for k, c in (("A", a), ("B", b))}
        cor = {k: c["correct"] / c["accepted"] for k, c in (("A", a), ("B", b))}
        herald = {k: c["rejected_herald"] / c["samples"] for k, c in (("A", a), ("B", b))}
        low, high = sorted(("A", "B"), key=lambda k: acc[k])
        chance = (acc[low] * cor[low] + (acc[high] - acc[low]) / 2) / acc[high]
        rows[label] = {
            "acceptance_per_sample": acc,
            "correctness": cor,
            "herald_rejections_per_sample": herald,
            "acceptance_se_of_difference": float(
                np.sqrt(sum(acc[k] * (1 - acc[k]) / counts[label][k]["samples"] for k in ("A", "B")))
            ),
            "higher_acceptance_block": high,
            "observed_correctness_change_low_to_high": cor[high] - cor[low],
            "chance_model_correctness_change_low_to_high": chance - cor[low],
        }
        deltas_a.append(acc["B"] - acc["A"])
        deltas_f.append(cor["B"] - cor["A"])
        deltas_h.append(herald["B"] - herald["A"])
    r_af, p_af = exact_permutation_r(np.asarray(deltas_a), np.asarray(deltas_f), negative=True)
    r_hf, p_hf = exact_permutation_r(np.asarray(deltas_h), np.asarray(deltas_f), negative=False)
    # The permutation r above depends on which mesh of an input is called A; the sign-flip cross product does not.
    x_af, q_af = ms.sign_flip_cross_product(np.asarray(deltas_a), np.asarray(deltas_f), negative=True)
    x_hf, q_hf = ms.sign_flip_cross_product(np.asarray(deltas_h), np.asarray(deltas_f), negative=False)
    winner_block = {label: "A" if deltas_f[i] < 0 else "B" for i, label in enumerate(LABELS)}
    winners = [counts[label][winner_block[label]] for label in LABELS]
    losers = [counts[label]["B" if winner_block[label] == "A" else "A"] for label in LABELS]
    return {
        "inputs": rows,
        "acceptance_correctness_r": r_af,
        "acceptance_correctness_one_sided_permutation_p": p_af,
        "acceptance_correctness_cross_product": x_af,
        "acceptance_correctness_one_sided_sign_flip_p": q_af,
        "herald_correctness_r": r_hf,
        "herald_correctness_one_sided_permutation_p": p_hf,
        "herald_correctness_cross_product": x_hf,
        "herald_correctness_one_sided_sign_flip_p": q_hf,
        "winner_mean_acceptance_per_sample": float(np.mean([c["accepted"] / c["samples"] for c in winners])),
        "loser_mean_acceptance_per_sample": float(np.mean([c["accepted"] / c["samples"] for c in losers])),
        "winner_mean_correct_per_sample": float(np.mean([c["correct"] / c["samples"] for c in winners])),
        "loser_mean_correct_per_sample": float(np.mean([c["correct"] / c["samples"] for c in losers])),
        "status": (
            "exploratory: the acceptance direction was stated before the computation, the herald direction follows"
            " from it, and neither test was preregistered"
        ),
    }


def shrinkage(counts: Mapping[str, Mapping[str, Mapping[str, float]]]) -> dict[str, Any]:
    return ms.contrast_shrinkage(counts, LABELS, TAU_GRID, FDR_Q)


def replay_power(counts: Mapping[str, Any], shrink: Mapping[str, Any], seed: np.random.SeedSequence) -> dict[str, Any]:
    return ms.replay_power(
        counts,
        shrink,
        seed,
        labels=LABELS,
        tau_grid=TAU_GRID,
        trials=TRIALS,
        samples_per_iteration=REPLAY_SAMPLES,
        job_counts=JOB_COUNTS,
        dropouts=DROPOUTS,
        z_critical=Z_ONE_SIDED,
    )


def replay_budget(counts: Mapping[str, Any]) -> dict[str, Any]:
    """Shot cap and credits per replay job: the lossiest retained mesh's shots per sample sets max_shots."""
    shots_per_sample = max(cell["shots"] / cell["samples"] for row in counts.values() for cell in row.values())
    raw = REPLAY_SAMPLES * shots_per_sample * tr.SHOT_MARGIN
    max_shots = int(-(-raw // tr.SHOT_QUANTUM) * tr.SHOT_QUANTUM)
    return {
        "max_shots_per_sample_retained": shots_per_sample,
        "max_shots_per_iteration": max_shots,
        "credits_per_job": tr.PER_JOB_CREDITS + max_shots * tr.PRICE_PER_SHOT,
        "credits": {str(jobs): jobs * (tr.PER_JOB_CREDITS + max_shots * tr.PRICE_PER_SHOT) for jobs in JOB_COUNTS},
    }


CALIBRATION_READS = {
    "2026-10-31T04:27Z": {"hom": 0.879, "g2": 0.014, "transmittance": 0.0537},
    "2026-10-31T05:02Z": {"hom": 0.886, "g2": 0.014, "transmittance": 0.0489},
    "2026-10-31T09:52Z": {"hom": 0.875, "g2": 0.012, "transmittance": 0.0542},
}
READ_SOURCES = {
    "2026-10-31T04:27Z": "2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay",
    "2026-10-31T05:02Z": "2026-10-31T050044Z-qpu_belenos-belenos_associator_visibility-job-00",
    "2026-10-31T09:52Z": "2026-10-31T095141Z-qpu_belenos-belenos_mode_swap_interleaved-job-03",
}


def perceval_hom_visibility(overlap: float, g2: float) -> float:
    """HOM visibility of Perceval's source model on a balanced beam splitter: 1 - P_c(overlap) / P_c(0) at fixed g2."""
    import perceval as pcvl

    def coincidence(m: float) -> float:
        processor = pcvl.Processor("SLOS", pcvl.BS(), noise=pcvl.NoiseModel(indistinguishability=m, g2=g2))
        processor.min_detected_photons_filter(0)
        processor.with_input(pcvl.BasicState([1, 1]))
        return float(sum(v for state, v in processor.probs()["results"].items() if state[0] and state[1]))

    return 1.0 - coincidence(overlap) / coincidence(0.0)


def overlap_for_visibility(visibility: float, g2: float) -> float:
    """The source-model overlap whose simulated HOM visibility equals ``visibility`` at ``g2`` (bisection)."""
    low, high = visibility, 1.0
    for _ in range(40):
        mid = 0.5 * (low + high)
        low, high = (mid, high) if perceval_hom_visibility(mid, g2) < visibility else (low, mid)
    return 0.5 * (low + high)


def source_score(
    item: tuple[str, str, float, float, float, Mapping[str, Any], Mapping[str, Any], tuple[int, ...]],
) -> dict[str, Any]:
    read, reading, overlap, g2, transmittance, setting, circuit, layout = item
    variant = tr.Variant(reading, overlap, g2, (transmittance,) * tr.MODES)
    scores = tr.variant_scores((variant, setting["label"], dict(setting), dict(circuit), layout))
    return {"read": read, "reading": reading, "label": setting["label"], "overlap": overlap, **scores}


def source_shift_section(directory: Path) -> dict[str, Any]:
    """Predicted conditional fidelity of the six teleportation inputs at each calibration read, from the source model
    alone (no mesh error), under two readings of the processor record's HOM field: Perceval's own convention, which
    maps it to the source-model overlap (perceval.utils.noise_model, perfs "HOM (%)" / 100), and a raw HOM visibility,
    inverted through the same source model at the read's g2 (Ollivier et al. 2021, Eq. 1, separate the overlap from the
    multiphoton term). The spread between reads bounds the chip-wide correctness change the source explains."""
    cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((directory / "circuit.json").read_text(encoding="utf-8"))
    layout = tuple(cases["layout"]["chip_modes"])
    overlaps = {
        read: {"provider convention": f["hom"], "raw visibility": overlap_for_visibility(f["hom"], f["g2"])}
        for read, f in CALIBRATION_READS.items()
    }
    items = [
        (read, reading, overlap, f["g2"], f["transmittance"], setting, circuit, layout)
        for read, f in CALIBRATION_READS.items()
        for reading, overlap in overlaps[read].items()
        for setting in cases["settings"]
    ]
    rows = ordered_map(source_score, items, min_items=1)
    summary: dict[str, dict[str, float]] = {}
    for row in rows:
        summary.setdefault(row["reading"], {}).setdefault(row["read"], 0.0)
        summary[row["reading"]][row["read"]] += row["conditional_fidelity"] / len(LABELS)
    return {
        "reads": CALIBRATION_READS,
        "read_runs": READ_SOURCES,
        "overlaps": overlaps,
        "rows": rows,
        "mean_conditional_fidelity": summary,
        "largest_shift_between_reads": {
            reading: max(values.values()) - min(values.values()) for reading, values in summary.items()
        },
    }


HEATER_SIGMA = 0.1
COUPLER_SIGMA = 0.05
NOISE_REPLICATES = 200


def noisy_unitary(arch: Sequence[Any], phases: np.ndarray, dphi: np.ndarray, dtheta: np.ndarray) -> np.ndarray:
    """The 24-mode unitary of a returned mesh with heater phase errors dphi and coupler angle errors dtheta."""
    u = np.eye(tr.MODES, dtype=complex)
    ip = ib = 0
    for kind, m, p in arch:
        if kind == "bs":
            u[m : m + 2, :] = mesh.coupler(p[0] + dtheta[ib], *p[1:]) @ u[m : m + 2, :]
            ib += 1
        else:
            u[m, :] *= np.exp(1j * (phases[ip] + dphi[ip]))
            ip += 1
    return u


@functools.lru_cache(maxsize=64)
def decoded_mesh(circuit_text: str) -> tuple[Any, np.ndarray]:
    """A returned mesh's architecture and heater phases, decoded once per worker process."""
    elements = mesh.decode(circuit_text)
    arch = mesh.run_architecture(elements)
    return arch, np.asarray(mesh.mesh_phases(arch, elements))


def robustness_replicate(item: tuple[str, str, tuple[int, ...], np.ndarray, np.ndarray]) -> tuple[float, float]:
    """Accepted probability and conditional fidelity of one mesh under one replicate draw of one error class."""
    label, circuit_text, layout, dphi, dtheta = item
    arch, phases = decoded_mesh(circuit_text)
    acc, cor = tr.scored(label, clicks_of(noisy_unitary(arch, phases, dphi, dtheta), tr.source_state(layout)), layout)
    return acc, cor / acc if acc > 0 else 0.0


def structural_section(
    seed_sequence: np.random.SeedSequence, runs: Mapping[str, tuple[Path, str]], blocks: Mapping[str, str]
) -> dict[str, Any]:
    """Each mesh's sensitivity to the error classes the compiler does not model.

    The returned meshes are exact against the compiler's own coupler angles (the compiled section), so the
    transmission floor of an imperfect coupler pair (Kumar et al. 2021, imperfect MZI reflectivity between
    cos^2(2 theta) and 1) is already inside every mesh. What separates meshes is their response to deviations of
    the chip from that model: residual heater phases, including crosstalk-induced phases on bare waveguides
    (Fyrillas et al. 2025), and coupler angle errors. Each mesh is scored under the same replicate draws (common
    random numbers) at HEATER_SIGMA rad of independent heater error and, separately, COUPLER_SIGMA rad of coupler
    error. The predictors have no parameter fitted to correctness; the analyst had seen the retained correctness
    before defining them, so their test on these meshes is not blind, and the replay is their first fresh test."""
    rng = np.random.default_rng(seed_sequence)
    items_meta = []
    for run in (blocks["A"], blocks["B"]):
        directory = runs[run][0]
        cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        for setting, text in zip(cases["settings"], mesh.computed_circuits(directory), strict=True):
            items_meta.append((setting["label"], run, text, setting, layout))
    arch0 = mesh.run_architecture(mesh.decode(items_meta[0][2]))
    n_phase = sum(1 for kind, _, _ in arch0 if kind == "ps")
    n_bs = sum(1 for kind, _, _ in arch0 if kind == "bs")
    heater = (HEATER_SIGMA * rng.standard_normal((NOISE_REPLICATES, n_phase)), np.zeros((NOISE_REPLICATES, n_bs)))
    coupler = (np.zeros((NOISE_REPLICATES, n_phase)), COUPLER_SIGMA * rng.standard_normal((NOISE_REPLICATES, n_bs)))
    out: dict[str, Any] = {
        "heater_sigma_rad": HEATER_SIGMA,
        "coupler_sigma_rad": COUPLER_SIGMA,
        "replicates": NOISE_REPLICATES,
    }
    # Every (mesh, replicate) pair is independent, so the pool maps over all of them; each mesh's replicate scores
    # then average in replicate order.
    for name, (dphi, dtheta) in (("heater", heater), ("coupler", coupler)):
        work = [
            (label, text, layout, dphi[k], dtheta[k])
            for label, _, text, _, layout in items_meta
            for k in range(NOISE_REPLICATES)
        ]
        scores = ordered_map(robustness_replicate, work, min_items=1)
        rows = []
        for m, (label, run, *_rest) in enumerate(items_meta):
            block = scores[m * NOISE_REPLICATES : (m + 1) * NOISE_REPLICATES]
            rows.append(
                {
                    "label": label,
                    "run": run,
                    "fidelity": float(np.mean([f for _, f in block])),
                    "accepted": float(np.mean([a for a, _ in block])),
                }
            )
        out[name] = rows
    return out


def structural_test(
    structural: Mapping[str, Any],
    counts: Mapping[str, Any],
    compiled: Sequence[Mapping[str, Any]],
    blocks: Mapping[str, str],
) -> dict[str, Any]:
    """Within each input, block B minus block A of each predictor against B minus A of observed correctness, with
    the exact one-sided permutation p in each predictor's physical direction: predicted fidelity up means observed
    correctness up; heater phase (drive power, the crosstalk source) up means observed correctness down."""
    observed = np.asarray(
        [
            counts[label]["B"]["correct"] / counts[label]["B"]["accepted"]
            - counts[label]["A"]["correct"] / counts[label]["A"]["accepted"]
            for label in LABELS
        ]
    )
    result: dict[str, Any] = {}
    for name in ("heater", "coupler"):
        by = {(row["label"], row["run"]): row for row in structural[name]}
        delta = np.asarray(
            [by[(label, blocks["B"])]["fidelity"] - by[(label, blocks["A"])]["fidelity"] for label in LABELS]
        )
        r, p = exact_permutation_r(delta, observed, negative=False)
        result[f"{name}_noise_fidelity"] = {"delta_b_minus_a": delta.tolist(), "r": r, "one_sided_p": p}
    power = {(row["label"], row["run"]): row["heater_phase_rad"] for row in compiled}
    delta = np.asarray([power[(label, blocks["B"])] - power[(label, blocks["A"])] for label in LABELS])
    r, p = exact_permutation_r(delta, observed, negative=True)
    result["heater_phase_sum"] = {"delta_b_minus_a": delta.tolist(), "r": r, "one_sided_p": p}
    result["observed_delta_b_minus_a"] = observed.tolist()
    return result


def mesh_against_source(counts: Mapping[str, Any], shift: Mapping[str, Any]) -> dict[str, Any]:
    """Each retained mesh's correctness minus the source-only prediction at the 04:27 read, which both blocks ran
    under. A positive excess on an input with a pessimistic source prediction shows the source model is no ceiling for
    a postselected mesh, and the mesh-to-mesh spread is measured about each input's own source prediction."""
    read = "2026-10-31T04:27Z"
    predicted = {
        (row["reading"], row["label"]): row["conditional_fidelity"] for row in shift["rows"] if row["read"] == read
    }
    out: dict[str, Any] = {}
    for label in LABELS:
        for block in ("A", "B"):
            cell = counts[label][block]
            f = cell["correct"] / cell["accepted"]
            out[f"{label} {block}"] = {
                "observed": f,
                "standard_error": float(np.sqrt(f * (1 - f) / cell["accepted"])),
                **{
                    f"observed_minus_{reading.replace(' ', '_')}": f - predicted[(reading, label)]
                    for reading in ("provider convention", "raw visibility")
                },
            }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    qrng_seeds.add_seed_argument(parser, "--seed", help="power-simulation seed, qrng:<draw>#<index>")
    parser.add_argument(
        "--run",
        nargs=3,
        action="append",
        metavar=("KEY", "RUN_DIR", "BLOCK"),
        help="a retained run, its key in the record and its block (A or B); repeat per run. The first run of each "
        "block stands for its meshes. Default: the job-02, job-02 replay and job-03 teleportation runs",
    )
    args = parser.parse_args()
    if args.seed is None:
        parser.error("--seed is required")
    runs = {key: (Path(directory), block) for key, directory, block in args.run} if args.run else DEFAULT_RUNS
    blocks = representatives(runs)
    counts = block_counts(iterations(runs))
    shift = source_shift_section(runs[blocks["A"]][0])
    shrink = shrinkage(counts)
    power_seed, noise_seed = np.random.SeedSequence(args.seed).spawn(2)
    power = replay_power(counts, shrink, power_seed)
    compiled = compiled_section(runs)
    structural = structural_section(noise_seed, runs, blocks)
    shrink.pop("_draw")
    record = {
        "schema": "belenos-best-mesh-first-principles-v1",
        "seed_source": qrng_seeds.seed_record(
            "scripts/belenos_best_mesh_first_principles.py",
            "--seed",
            "belenos-best-mesh-replay-power",
            args.seed_source,
        ),
        "compiled": compiled,
        "structural": structural,
        "structural_test": structural_test(structural, counts, compiled, blocks),
        "shrinkage": shrink,
        "replay_power": power,
        "acceptance": acceptance_section(counts),
        "source_shift": shift,
        "mesh_against_source": mesh_against_source(counts, shift),
        "replay_budget": replay_budget(counts),
    }
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
