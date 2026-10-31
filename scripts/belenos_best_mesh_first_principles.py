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

Usage: belenos_best_mesh_first_principles.py --out PATH --seed qrng:<draw>#<index>
"""

from __future__ import annotations

import argparse
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


def compiled_section() -> list[dict[str, Any]]:
    items = []
    for run, name in RUN_NAMES.items():
        cases = json.loads((RUNS / name / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        circuits = mesh.computed_circuits(RUNS / name)
        if len(circuits) != len(cases["settings"]):
            raise ValueError(f"{run}: {len(circuits)} computed circuits for {len(cases['settings'])} settings")
        for index, (setting, text) in enumerate(zip(cases["settings"], circuits, strict=True)):
            items.append((run, index, setting, text, layout))
    return ordered_map(compiled_row, items, min_items=1)


LABELS = ("+Z", "-Z", "+X", "-X", "+Y", "-Y")
BLOCKS = {"job-02": "A", "job-02-replay": "A", "job-03": "B"}
TAU_GRID = np.linspace(0.0, 0.25, 1001)
FDR_Q = 0.10
ALPHA_ONE_SIDED = 0.05
Z_ONE_SIDED = 1.6448536269514722
REPLAY_SAMPLES = 1200
TRIALS = 200_000
DROPOUTS = (0, 1, 2, 3)
JOB_COUNTS = (2, 4)


def iterations() -> list[dict[str, Any]]:
    """Every retained iteration with its run and block."""
    rows: list[dict[str, Any]] = []
    for run, name in RUN_NAMES.items():
        analysis = json.loads((RUNS / name / "analysis.json").read_text(encoding="utf-8"))
        rows.extend({**row, "run": run, "block_of_seed": BLOCKS[run]} for row in analysis["iterations"])
    return rows


def block_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    """Per input and block: correct, accepted, samples and shots summed over the block's runs (job-02 pools with its
    exact replay, which returned the same six meshes)."""
    out: dict[str, dict[str, dict[str, float]]] = {label: {} for label in LABELS}
    for row in rows:
        cell = out[row["label"]].setdefault(
            row["block_of_seed"],
            {"correct": 0, "accepted": 0, "samples": 0, "shots": 0, "seed": row["compilation_seed"]},
        )
        if cell["seed"] != row["compilation_seed"]:
            raise ValueError(f"{row['label']} block {row['block_of_seed']} mixes compilation seeds")
        for key, field in (("correct", "correct"), ("accepted", "accepted"), ("samples", "samples")):
            cell[key] += row[field]
        cell["shots"] += row["nb_shots_used"]
        for reason in tr.REJECTIONS:
            cell[f"rejected_{reason}"] = cell.get(f"rejected_{reason}", 0) + row["rejected"][reason]
    return out


def exact_permutation_r(x: np.ndarray, y: np.ndarray, negative: bool) -> tuple[float, float]:
    """Pearson r of paired values and its exact one-sided permutation p-value over all pairings: P(r_perm <= r) for a
    predicted negative association, P(r_perm >= r) for a positive one."""
    import itertools

    def pearson(a: np.ndarray, b: np.ndarray) -> float:
        a, b = a - a.mean(), b - b.mean()
        return float(a @ b / np.sqrt((a @ a) * (b @ b)))

    observed = pearson(x, y)
    values = [pearson(x, np.asarray(perm)) for perm in itertools.permutations(y)]
    if negative:
        return observed, float(np.mean([v <= observed + 1e-12 for v in values]))
    return observed, float(np.mean([v >= observed - 1e-12 for v in values]))


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
    winner_block = {label: "A" if deltas_f[i] < 0 else "B" for i, label in enumerate(LABELS)}
    winners = [counts[label][winner_block[label]] for label in LABELS]
    losers = [counts[label]["B" if winner_block[label] == "A" else "A"] for label in LABELS]
    return {
        "inputs": rows,
        "acceptance_correctness_r": r_af,
        "acceptance_correctness_one_sided_permutation_p": p_af,
        "herald_correctness_r": r_hf,
        "herald_correctness_one_sided_permutation_p": p_hf,
        "winner_mean_acceptance_per_sample": float(np.mean([c["accepted"] / c["samples"] for c in winners])),
        "loser_mean_acceptance_per_sample": float(np.mean([c["accepted"] / c["samples"] for c in losers])),
        "status": (
            "exploratory: the acceptance direction was stated before the computation, the herald direction follows"
            " from it, and neither test was preregistered"
        ),
    }


def normal_cdf(x: Any) -> Any:
    from scipy.special import ndtr

    return ndtr(x)


def shrinkage(counts: Mapping[str, Mapping[str, Mapping[str, float]]]) -> dict[str, Any]:
    """Normal-normal hierarchical shrinkage of the six block A minus block B correctness differences.

    The A and B seeds of an input are exchangeable draws of the transpiler, so the prior on the true difference is
    centered at zero: mu_i ~ N(0, tau^2), d_i | mu_i ~ N(mu_i, s_i^2) with s_i the binomial standard error. Tweedie's
    formula for this prior gives E[mu_i | d_i, tau] = C_i d_i with C_i = tau^2 / (tau^2 + s_i^2) (Efron 2011, Eqs. 3.7
    and 3.8). tau carries a uniform prior on TAU_GRID, so its estimation error enters every posterior moment, the
    hierarchical counterpart of Efron's Eq. 7.26 regret term. The expected winner-minus-loser gap of input i is
    E[sign(d_i) mu_i | data] = |d_i| E[C_i | data]."""
    d = np.empty(len(LABELS))
    s = np.empty(len(LABELS))
    for i, label in enumerate(LABELS):
        a, b = counts[label]["A"], counts[label]["B"]
        pa, pb = a["correct"] / a["accepted"], b["correct"] / b["accepted"]
        d[i] = pa - pb
        s[i] = np.sqrt(pa * (1 - pa) / a["accepted"] + pb * (1 - pb) / b["accepted"])
    z = d / s
    n = len(LABELS)
    variance = TAU_GRID[:, None] ** 2 + s[None, :] ** 2
    log_post = np.sum(-0.5 * np.log(variance) - d[None, :] ** 2 / (2 * variance), axis=1)
    weights = np.exp(log_post - log_post.max())
    weights /= weights.sum()
    factor = TAU_GRID[:, None] ** 2 / variance
    mean_factor = weights @ factor
    gap = np.abs(d) * mean_factor
    gap_second = weights @ (factor * s**2 + factor**2 * d**2)
    sign_right = weights @ normal_cdf(np.sqrt(factor) * np.abs(d) / s)
    cdf = np.cumsum(weights)
    p_values = 2 * (1 - normal_cdf(np.abs(z)))
    order = np.argsort(p_values)
    passed = [p_values[k] <= FDR_Q * (rank + 1) / n for rank, k in enumerate(order)]
    determined = max((rank + 1 for rank, ok in enumerate(passed) if ok), default=0)
    return {
        "prior": "mu_i ~ N(0, tau^2), tau uniform on [0, 0.25]",
        "inputs": {
            label: {
                "block_a": dict(counts[label]["A"]),
                "block_b": dict(counts[label]["B"]),
                "difference": float(d[i]),
                "standard_error": float(s[i]),
                "z": float(z[i]),
                "two_sided_p": float(p_values[i]),
                "winner_block": "A" if d[i] > 0 else "B",
                "shrinkage_factor": float(mean_factor[i]),
                "expected_gap": float(gap[i]),
                "gap_posterior_sd": float(np.sqrt(gap_second[i] - gap[i] ** 2)),
                "probability_winner_is_better": float(sign_right[i]),
                "sign_determined_directional_bh": bool(i in {int(k) for k in order[:determined]}),
            }
            for i, label in enumerate(LABELS)
        },
        "chi_square_on_6": float(np.sum(z**2)),
        "james_stein_factor": float(max(0.0, 1 - (n - 2) / np.sum(z**2))),
        "tau_mle": float(TAU_GRID[np.argmax(log_post)]),
        "tau_posterior_mean": float(weights @ TAU_GRID),
        "tau_90_interval": [float(TAU_GRID[np.searchsorted(cdf, 0.05)]), float(TAU_GRID[np.searchsorted(cdf, 0.95)])],
        "mean_expected_gap": float(gap.mean()),
        "directional_bh_q": FDR_Q,
        "signs_determined": determined,
        "_draw": {"d": d, "s": s, "weights": weights},
    }


def replay_power(counts: Mapping[str, Any], shrink: Mapping[str, Any], seed: np.random.SeedSequence) -> dict[str, Any]:
    """Posterior-predictive power of the winner-and-loser replay.

    Each trial draws tau from its posterior, each input's true A-minus-B difference from its conditional posterior
    N(C d, C s^2), and sets the winner and loser correctness at the input's observed two-block mean plus and minus
    half the signed gap. Each mesh runs REPLAY_SAMPLES samples per job pair at its observed acceptance per sample, so
    accepted counts and correct counts are binomial. The primary statistic is the summed contrast over the kept
    inputs divided by its binomial standard error, one-sided at ALPHA_ONE_SIDED. A dropout removes inputs whose seed
    returns a different mesh after the recalibration, as the preregistered mismatch branch does. Trials draw every
    input first and evaluate as numpy arrays, so the record depends only on the seed."""
    rng = np.random.default_rng(seed)
    draw = shrink["_draw"]
    d, s, weights = draw["d"], draw["s"], draw["weights"]
    sign = np.sign(d)
    mean_level = np.empty(len(LABELS))
    accept = np.empty((2, len(LABELS)))
    for i, label in enumerate(LABELS):
        a, b = counts[label]["A"], counts[label]["B"]
        mean_level[i] = 0.5 * (a["correct"] / a["accepted"] + b["correct"] / b["accepted"])
        winner, loser = (a, b) if d[i] > 0 else (b, a)
        accept[0, i] = winner["accepted"] / winner["samples"]
        accept[1, i] = loser["accepted"] / loser["samples"]
    tau = TAU_GRID[rng.choice(len(TAU_GRID), size=TRIALS, p=weights)]
    factor = tau[:, None] ** 2 / (tau[:, None] ** 2 + s[None, :] ** 2)
    true_difference = factor * d + np.sqrt(factor) * s * rng.standard_normal((TRIALS, len(LABELS)))
    gap = sign * true_difference
    tau_mle = TAU_GRID[int(np.argmax(weights))]
    factor_mle = tau_mle**2 / (tau_mle**2 + s**2)
    gap_mle = sign * (factor_mle * d + np.sqrt(factor_mle) * s * rng.standard_normal((TRIALS, len(LABELS))))
    order = rng.random((TRIALS, len(LABELS))).argsort(axis=1)
    uniforms = [rng.random((TRIALS, len(LABELS))) for _ in range(4 * len(JOB_COUNTS))]
    out: dict[str, Any] = {
        "seed_spawn_key": list(seed.spawn_key),
        "trials": TRIALS,
        "samples_per_iteration": REPLAY_SAMPLES,
        "designs": [],
    }
    for j, jobs in enumerate(JOB_COUNTS):
        samples = REPLAY_SAMPLES * jobs // 2
        u = uniforms[4 * j : 4 * j + 4]
        from scipy.stats import binom

        scenarios = (
            ("persistent mesh error", gap),
            ("persistent mesh error, tau fixed at its maximum", gap_mle),
            ("no persistent mesh error", 0.0 * gap),
        )
        for scenario, effect in scenarios:
            p_win = np.clip(mean_level + effect / 2, 0.0, 1.0)
            p_lose = np.clip(mean_level - effect / 2, 0.0, 1.0)
            n_win = np.maximum(binom.ppf(u[0], samples, accept[0]), 1)
            n_lose = np.maximum(binom.ppf(u[1], samples, accept[1]), 1)
            c_win = binom.ppf(u[2], n_win, p_win)
            c_lose = binom.ppf(u[3], n_lose, p_lose)
            f_win, f_lose = c_win / n_win, c_lose / n_lose
            contrast = f_win - f_lose
            variance = f_win * (1 - f_win) / n_win + f_lose * (1 - f_lose) / n_lose
            for dropped in DROPOUTS:
                keep = order >= dropped
                total = np.where(keep, contrast, 0.0).sum(axis=1)
                spread = np.sqrt(np.where(keep, variance, 0.0).sum(axis=1))
                statistic = np.divide(total, spread, out=np.zeros_like(total), where=spread > 0)
                kept = len(LABELS) - dropped
                out["designs"].append(
                    {
                        "jobs": jobs,
                        "scenario": scenario,
                        "pairs_dropped": dropped,
                        "power": float(np.mean(statistic > Z_ONE_SIDED)),
                        "mean_true_gap_kept": float(np.mean(np.where(keep, effect, 0.0).sum(axis=1) / kept)),
                    }
                )
    return out


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


def source_shift_section() -> dict[str, Any]:
    """Predicted conditional fidelity of the six teleportation inputs at each calibration read, from the source model
    alone (no mesh error), under two readings of the processor record's HOM field: Perceval's own convention, which
    maps it to the source-model overlap (perceval.utils.noise_model, perfs "HOM (%)" / 100), and a raw HOM visibility,
    inverted through the same source model at the read's g2 (Ollivier et al. 2021, Eq. 1, separate the overlap from the
    multiphoton term). The spread between reads bounds the chip-wide correctness change the source explains."""
    name = RUN_NAMES["job-02"]
    cases = json.loads((RUNS / name / "cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((RUNS / name / "circuit.json").read_text(encoding="utf-8"))
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


def robustness_row(
    item: tuple[str, str, str, Mapping[str, Any], tuple[int, ...], np.ndarray, np.ndarray],
) -> dict[str, Any]:
    """Mean conditional fidelity and accepted probability of one mesh under replicate error draws of one class."""
    label, run, circuit_text, _, layout, dphi, dtheta = item
    elements = mesh.decode(circuit_text)
    arch = mesh.run_architecture(elements)
    phases = np.asarray(mesh.mesh_phases(arch, elements))
    source = tr.source_state(layout)
    fidelity, accepted = [], []
    for k in range(dphi.shape[0]):
        acc, cor = tr.scored(label, clicks_of(noisy_unitary(arch, phases, dphi[k], dtheta[k]), source), layout)
        accepted.append(acc)
        fidelity.append(cor / acc if acc > 0 else 0.0)
    return {"label": label, "run": run, "fidelity": float(np.mean(fidelity)), "accepted": float(np.mean(accepted))}


def structural_section(seed_sequence: np.random.SeedSequence) -> dict[str, Any]:
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
    for run in ("job-02", "job-03"):
        name = RUN_NAMES[run]
        cases = json.loads((RUNS / name / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        for setting, text in zip(cases["settings"], mesh.computed_circuits(RUNS / name), strict=True):
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
    for name, (dphi, dtheta) in (("heater", heater), ("coupler", coupler)):
        rows = ordered_map(robustness_row, [(*meta, dphi, dtheta) for meta in items_meta], min_items=1)
        out[name] = rows
    return out


def structural_test(
    structural: Mapping[str, Any], counts: Mapping[str, Any], compiled: Sequence[Mapping[str, Any]]
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
        delta = np.asarray([by[(label, "job-03")]["fidelity"] - by[(label, "job-02")]["fidelity"] for label in LABELS])
        r, p = exact_permutation_r(delta, observed, negative=False)
        result[f"{name}_noise_fidelity"] = {"delta_b_minus_a": delta.tolist(), "r": r, "one_sided_p": p}
    power = {(row["label"], row["run"]): row["heater_phase_rad"] for row in compiled}
    delta = np.asarray([power[(label, "job-03")] - power[(label, "job-02")] for label in LABELS])
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
    args = parser.parse_args()
    if args.seed is None:
        parser.error("--seed is required")
    counts = block_counts(iterations())
    shift = source_shift_section()
    shrink = shrinkage(counts)
    power_seed, noise_seed = np.random.SeedSequence(args.seed).spawn(2)
    power = replay_power(counts, shrink, power_seed)
    compiled = compiled_section()
    structural = structural_section(noise_seed)
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
        "structural_test": structural_test(structural, counts, compiled),
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
