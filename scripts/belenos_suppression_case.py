"""Belenos three-photon suppression-law request: two qpu:belenos jobs of four template iterations each.

docs/design/belenos-suppression-law-case.md fixes the request. Three photons enter three connected source modes of a
six-mode window of the 24-mode chip. The periodic setting programs the six-mode Fourier matrix with the photons on
Fourier ports 0, 2 and 4 (a cyclic input of period m/n = 2). The zero-transmission law of Tichy et al. forbids every
collision-free output whose mode labels do not sum to a multiple of three: 12 of the 20 collision-free outputs, the
suppressed set. The control setting programs the same matrix with the photons on Fourier ports 0, 1 and 2, where every
collision-free output has a nonzero permanent, so its suppressed set is empty. Both settings use the same three chip
input modes and the same six detectors and differ in the columns of the programmed matrix alone, so distinguishable
photons produce one output law in both (every Fourier entry has modulus 1/sqrt(6)).

The statistic is the suppressed-outcome fraction s, the share of collision-free three-click events inside the window
that lie in the suppressed set, scored for both arms against the periodic arm's set. Three models forecast it at the
platform's performance figures with the per-mode detection of detection_efficiency: genuine photons under Perceval's
NoiseModel(indistinguishability = HOM, g2), distinguishable photons (indistinguishability 0, same g2) and the
random-phase mean-field sampler of Tichy et al. (2014), whose phase average is exact on a uniform grid. The ideal
indistinguishable fraction is zero; the distinguishable and mean-field fractions lie far above the indistinguishable
forecast; the control fraction separates the three only weakly, which is its purpose, since it checks that the
detectors and the event selection leave the suppressed set undepleted.

--check rebuilds both jobs in memory and compares them with the retained files, binds every iteration through
qd_platform.template_experiment, recomputes the suppressed set from permanents and the label-sum rule, compares the
compiled unitary with Perceval's SLOS backend and compares the retained forecast. --build writes the case files.
--forecast writes noise-model.json from the case's platform read. --estimate writes shot-estimate.json from a live
processor read under the platform read's figures. --analyze RUN [RUN ...] reads collected runs and writes the
preregistered endpoints beside each.

Usage:
  "$PYTHON" scripts/belenos_suppression_case.py [--check|--build|--forecast|--estimate|--analyze RUN [RUN ...]]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLATFORM = "qpu:belenos"
FAMILY = "belenos_suppression_law"
CASES = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/belenos-suppression-law-case.md"
# The platform read, the retained forecast and the shot estimate serve both jobs and sit in the family directory.
READ = "platform-read/catalogue.json"
MODES = 24
WINDOW = 6
PHOTONS = 3
MIN_CLICKS = 3
MAX_DURATION = 300
PER_JOB_CREDITS = 1.0
PRICE_PER_SHOT = 1e-6
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9
# The platform record's connected_input_modes: a photon on any other mode makes the service re-route and re-transpile.
CONNECTED = (0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22)
# A window mode whose dark rate exceeds DARK_LIMIT per second adds a spurious click per 1 / (clock * DARK_LIMIT) pulses.
DARK_LIMIT = 100.0
# The largest ratio of t_out across the six detectors of the window; a larger imbalance moves the distinguishable null
# away from the uniform value 12/20 and makes the forecasts lean on the per-mode detection model.
SPREAD_LIMIT = 2.0
# Photon ports of the two programmed settings on the Fourier matrix, ascending; the periodic input has period m/n = 2.
PERIODIC_PORTS = (0, 2, 4)
CONTROL_PORTS = (0, 1, 2)
ARMS = {"periodic": PERIODIC_PORTS, "control": CONTROL_PORTS}
# Submission order of the arms in each job: an ABBA block and its reverse, so each job balances drift in the arm order.
JOB_INDEX = {"job-00": 0, "job-01": 4}
JOB_ORDER = {
    "job-00": ("periodic", "control", "control", "periodic"),
    "job-01": ("control", "periodic", "periodic", "control"),
}
# The compilation_seed of each iteration in submission order, job-00 then job-01: indices 0 to 7, in index order, of the
# ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-31T034820Z.json, registered in
# docs/evidence/qrng_seeds/allocations.json.
DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T034820Z.json"
COMPILATION_SEEDS = (63889, 65328, 18934, 51115, 51480, 31486, 50307, 51095)
# Provider seconds of one template iteration on qpu:belenos: a fixed part plus the shots it runs times a per-shot cost.
# Fitted over the retained qpu:belenos runs of the BDSC stationarity and qualification cases (fixed part 6.6 to 6.9 s)
# and the teleportation rehearsal (per shot 9 to 12.8 microseconds on a healthy chip, about 35 microseconds degraded).
FIXED_ITERATION_SECONDS = 6.9
SECONDS_PER_SHOT = 12.8e-6
DEGRADED_SECONDS_PER_SHOT = 35e-6
SECONDS_MARGIN = 1.25
SECONDS_QUANTUM = 60
SAMPLES_PER_ITERATION = 400
# max_shots exceeds the Perceval estimate_required_shots of an iteration by this factor, in multiples of SHOT_QUANTUM.
SHOT_MARGIN = 1.25
SHOT_QUANTUM = 50_000
SHOTS_PER_ITERATION = 1_500_000
ESTIMATE = "shot-estimate.json"
FORECAST = "noise-model.json"
# Preregistered decision constants (design document, "Decision rule").
ALPHA = 0.01
NULL_MARGIN = 0.10
FORECAST_TOLERANCE = 0.05
CONTROL_TOLERANCE = 0.10
MIN_ITERATIONS = 4
# An iteration counts toward its arm only with at least this many accepted events (half of SAMPLES_PER_ITERATION).
MIN_EVENTS = 200
# The lower 1 - ALPHA bound of s_control - s_periodic must reach this margin; the contrast is 0 for distinguishable
# photons whatever the detector efficiencies, since every Fourier entry has modulus 1/sqrt(6).
CONTRAST_MARGIN = 0.10
# job-01 is submitted only after job-00 is collected with at least this many accepted events (half of 1600).
MIN_JOB_YIELD = 800
# The entry kinds qd_platform.result_summary writes for an iteration of a partial job that carries no counts.
UNCOUNTED = ("missing", "malformed", "error")
# The mean-field phase average is exact when the grid has more points than the largest photon-number degree.
PHASE_GRID = 7
MAX_EMITTED = 6


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------- the interferometer and its suppression law


def fourier(size: int) -> np.ndarray:
    """The unitary Fourier matrix F[j, k] = exp(2 pi i j k / size) / sqrt(size)."""
    omega = np.exp(2j * np.pi / size)
    return np.asarray([[omega ** (j * k) for k in range(size)] for j in range(size)]) / math.sqrt(size)


def permanent(matrix: np.ndarray) -> complex:
    size = matrix.shape[0]
    return complex(sum(np.prod([matrix[i, p[i]] for i in range(size)]) for p in itertools.permutations(range(size))))


def triples() -> list[tuple[int, ...]]:
    """The collision-free output sets of three photons over the window slots, lexicographic."""
    return list(itertools.combinations(range(WINDOW), PHOTONS))


def indistinguishable_law(unitary: np.ndarray, ports: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Probability of each collision-free output for identical photons on the given input ports: |perm|^2."""
    return {out: float(abs(permanent(unitary[np.ix_(out, ports)])) ** 2) for out in triples()}


def distinguishable_law(unitary: np.ndarray, ports: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Probability of each collision-free output for fully distinguishable photons: the sum of |product|^2."""
    law = {}
    for out in triples():
        sub = unitary[np.ix_(out, ports)]
        law[out] = float(
            sum(
                abs(np.prod([sub[i, p[i]] for i in range(PHOTONS)])) ** 2
                for p in itertools.permutations(range(PHOTONS))
            )
        )
    return law


def suppressed_set(unitary: np.ndarray, ports: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """The collision-free outputs whose permanent vanishes."""
    law = indistinguishable_law(unitary, ports)
    return tuple(out for out in triples() if law[out] < TOLERANCE)


def label_sum_rule() -> tuple[tuple[int, ...], ...]:
    """Tichy et al.: the cyclic input 0, 2, 4 of the six-mode Fourier matrix allows only outputs whose labels sum to a
    multiple of n = 3; the suppressed set is every collision-free output with another residue."""
    return tuple(out for out in triples() if sum(out) % PHOTONS != 0)


# ---------------------------------------------------------------- the window layout


def platform_read(case_dir: Path) -> dict[str, Any]:
    return dict(json.loads((case_dir / READ).read_text(encoding="utf-8")))


def processor(catalogue: Mapping[str, Any]) -> Mapping[str, Any]:
    return dict(catalogue["processors"][PLATFORM])


def read_perfs(perfs: Mapping[str, Any]) -> tuple[list[float], list[float], list[float], dict[str, float]]:
    """(t_out, t_in, dark counts per second, scalar figures) of a qpu:belenos performance record."""
    figures = {
        "hom": perfs["HOM (%)"] / 100.0,
        "g2": perfs["g2 (%)"] / 100.0,
        "transmittance": perfs["Transmittance (%)"] / 100.0,
        "clock_mhz": perfs["Clock (MHz)"],
    }
    per_mode = perfs["Transmission per mode (%)"]
    return list(per_mode["t_out"]), list(per_mode["t_in"]), list(perfs["Dark counts (detection/s)"]), figures


def detection_efficiency(t_out: Sequence[float], transmittance: float) -> list[float]:
    """Per-mode detection probability: the platform's Transmittance times t_out relative to its largest mode, the
    normalization remote_computer.update_detectors_from_perfs applies."""
    peak = max(t_out)
    return [transmittance * value / peak for value in t_out]


def window_key(
    item: tuple[int, list[float], list[float], list[float], list[float], list[int]],
) -> tuple[Any, ...] | None:
    """(-score, start, sources) of the window starting at `start`, or None when the window fails a constraint.

    A window needs three connected modes, a dark rate at or below DARK_LIMIT on all six modes and a t_out ratio at or
    below SPREAD_LIMIT. The score is the product of the three source t_in values times the distinguishable
    three-click probability per pulse, 3! / 6^3 times the sum over output triples of the product of their detection
    efficiencies: the modeled relative rate of a three-photon event. The sources are the three connected modes of the
    window with the largest t_in product."""
    start, t_out, t_in, dark, eta, connected = item
    slots = list(range(start, start + WINDOW))
    linked = [mode for mode in slots if mode in connected]
    if len(linked) < PHOTONS or any(dark[mode] > DARK_LIMIT for mode in slots):
        return None
    if max(t_out[m] for m in slots) / min(t_out[m] for m in slots) > SPREAD_LIMIT:
        return None
    sources = max(itertools.combinations(linked, PHOTONS), key=lambda trio: math.prod(t_in[m] for m in trio))
    rate = (
        math.factorial(PHOTONS)
        / WINDOW**PHOTONS
        * sum(math.prod(eta[start + k] for k in out) for out in itertools.combinations(range(WINDOW), PHOTONS))
    )
    return (-round(math.prod(t_in[m] for m in sources) * rate, 12), start, tuple(sources))


def choose_window(catalogue: Mapping[str, Any]) -> tuple[int, tuple[int, ...]]:
    """(first chip mode of the window, the three source chip modes), the best-scoring window of the platform read."""
    t_out, t_in, dark, figures = read_perfs(processor(catalogue)["perfs"])
    eta = detection_efficiency(t_out, figures["transmittance"])
    connected = list(processor(catalogue)["specs"]["connected_input_modes"])
    require(tuple(connected) == CONNECTED, f"connected input modes {connected} differ from CONNECTED")
    keys = ordered_map(
        window_key,
        [(s, t_out, t_in, dark, eta, connected) for s in range(MODES - WINDOW + 1)],
        min_items=1,
    )
    found = [key for key in keys if key is not None]
    require(bool(found), "no window of six modes meets the source, dark-count and balance constraints")
    best = min(found)
    return int(best[1]), tuple(best[2])


def source_slots(start: int, sources: Sequence[int]) -> tuple[int, ...]:
    return tuple(mode - start for mode in sources)


def window_unitary(arm: str, slots: Sequence[int]) -> np.ndarray:
    """The 6 x 6 unitary of an arm in window coordinates: column slot c holds the Fourier column assigned to c.

    The arm's photon ports take the source slots in ascending order and the remaining Fourier columns fill the other
    slots in ascending order, so the same three chip modes carry the photons in both arms. Output slot k is Fourier
    output k."""
    ports = sorted(ARMS[arm])
    rest = [column for column in range(WINDOW) if column not in ports]
    assigned: dict[int, int] = dict(zip(sorted(slots), ports, strict=True))
    for slot in range(WINDOW):
        if slot not in assigned:
            assigned[slot] = rest.pop(0)
    transform = fourier(WINDOW)
    return np.asarray(transform[:, [assigned[slot] for slot in range(WINDOW)]], dtype=complex)


# ---------------------------------------------------------------- the circuit and the case documents


def chip_operator(window: np.ndarray, start: int) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    full[start : start + WINDOW, start : start + WINDOW] = window
    return full


def source_state(sources: Sequence[int]) -> list[int]:
    state = [0] * MODES
    for mode in sources:
        state[mode] = 1
    return state


def build_setting(item: tuple[int, str, str, int, tuple[int, ...]]) -> tuple[dict[str, Any], dict[str, Any]]:
    index, job, arm, start, sources = item
    slots = source_slots(start, sources)
    window = window_unitary(arm, slots)
    mesh, parameters = photonic_template(window)
    mesh = {**mesh, "ops": [[kind, mode + start, k] for kind, mode, k in mesh["ops"]]}
    full = chip_operator(window, start)
    ports = sorted(ARMS[arm])
    law = indistinguishable_law(window, slots)
    flat = distinguishable_law(window, slots)
    setting = {
        "name": f"{arm}-{job}-position{index - JOB_INDEX[job]}",
        "observation_index": index,
        "arm": arm,
        "fourier_ports": list(ports),
        "ideal": {
            "suppressed_outputs": [list(out) for out in suppressed_set(window, slots)],
            "probability_indistinguishable": {"".join(map(str, o)): round(v, 12) for o, v in law.items()},
            "probability_distinguishable": {"".join(map(str, o)): round(v, 12) for o, v in flat.items()},
        },
        "compilation_seed": COMPILATION_SEEDS[index],
        "circuit_params": parameters,
        "column": [[float(value.real), float(value.imag)] for value in full[:, sources[0]]],
        "operator": encoded(full),
    }
    return mesh, setting


def job_documents(job: str, start: int, sources: tuple[int, ...]) -> dict[str, bytes]:
    order = JOB_ORDER[job]
    items = [(JOB_INDEX[job] + k, job, arm, start, sources) for k, arm in enumerate(order)]
    built = ordered_map(build_setting, items, min_items=1)
    template = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == template, f"{job}: iteration {index} needs another mesh than iteration 0")
    settings = [setting for _, setting in built]
    circuit = {**template, "modes": MODES, "input_state": source_state(sources)}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    samples = SAMPLES_PER_ITERATION * len(settings)
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": MIN_CLICKS,
        "max_samples": samples,
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(start, start + WINDOW)),
        "layout": {
            "window_start": start,
            "source_modes": list(sources),
            "slot_of_source": list(source_slots(start, sources)),
        },
        "arm_order": list(order),
        "eligibility": "exactly three threshold clicks, all inside the six window modes, one per mode",
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": preregistration(),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def preregistration() -> dict[str, Any]:
    return {
        "statistic": "s = events in the suppressed set / collision-free three-click events inside the window",
        "suppressed_set": "the 12 collision-free outputs whose slot labels do not sum to a multiple of 3",
        "models": [
            "indistinguishable (Perceval NoiseModel at the HOM and g2 of the plan)",
            "distinguishable",
            "mean-field",
        ],
        "alpha": ALPHA,
        "null_margin": NULL_MARGIN,
        "forecast_tolerance": FORECAST_TOLERANCE,
        "control_tolerance": CONTROL_TOLERANCE,
        "min_iterations_per_arm": MIN_ITERATIONS,
        "min_accepted_events_per_iteration": MIN_EVENTS,
        "contrast_margin": CONTRAST_MARGIN,
        "min_job_yield_before_next_job": MIN_JOB_YIELD,
        "interval": "one-sided Student t interval over the per-iteration fractions of an arm, pooled over both jobs",
        "runs": "one run per job name and every compilation seed once; a repeat of a failed job supersedes it with "
        "fresh QRNG seeds and is never pooled with it",
        "uncounted": "missing, malformed and error iterations are tallied and skipped; the decision is undecided "
        "when an arm keeps fewer than min_iterations_per_arm iterations of at least min_accepted_events_per_iteration "
        "accepted events",
        "suppression_observed": "both: upper 1 - alpha bound of s_periodic <= min(s_distinguishable, s_mean_field) "
        "- null_margin, and lower 1 - alpha bound of s_control - s_periodic >= contrast_margin",
        "control_valid": "|mean s_control - s_control forecast of the indistinguishable model| <= control_tolerance",
        "level": "|mean s_periodic - s_indistinguishable forecast| <= max(forecast_tolerance, 3 se); compile error "
        "and g2 raise s, so a deviation above the forecast is not evidence of partial distinguishability",
        "hom_lower_bound": "the HOM at which the indistinguishable forecast equals the periodic mean; compile error "
        "raises s, so it bounds the effective HOM from below",
        "forecast_source": "perfs_at_plan of submission.json, per-mode detection from t_out",
    }


def documents(start: int, sources: tuple[int, ...]) -> dict[str, dict[str, bytes]]:
    return {job: job_documents(job, start, sources) for job in JOB_ORDER}


# ---------------------------------------------------------------- the forecast models


def perceval_distribution(circuit: Any, slots: Sequence[int], hom: float, g2: float) -> dict[tuple[int, ...], float]:
    """Photon-number distribution over the window under Perceval's source model (indistinguishability, g2)."""
    import perceval as pcvl

    noise = pcvl.NoiseModel(indistinguishability=hom, g2=g2)
    chip = pcvl.Processor("SLOS", circuit, noise=noise)
    chip.min_detected_photons_filter(1)
    state = [0] * WINDOW
    for slot in slots:
        state[slot] = 1
    chip.with_input(pcvl.BasicState(state))
    results = chip.probs()["results"]
    return {tuple(int(count) for count in occupation): float(p) for occupation, p in results.items()}


def window_circuit(unitary: np.ndarray | None) -> Any:
    import perceval as pcvl

    if unitary is None:
        return pcvl.Circuit(WINDOW)
    return pcvl.Unitary(pcvl.Matrix(unitary))


def detected_clicks(
    photons: Mapping[tuple[int, ...], float], efficiency: Sequence[float]
) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution when each photon on mode m is detected with probability efficiency[m].

    A mode with n photons clicks with probability 1 - (1 - eta)^n; modes act independently."""
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, probability in photons.items():
        modes = [mode for mode, count in enumerate(occupation) if count]
        click_probability = [1.0 - (1.0 - efficiency[mode]) ** occupation[mode] for mode in modes]
        for pattern in itertools.product((0, 1), repeat=len(modes)):
            weight = probability
            vector = [0] * len(occupation)
            for mode, clicked, chance in zip(modes, pattern, click_probability, strict=True):
                weight *= chance if clicked else 1.0 - chance
                vector[mode] = clicked
            if weight > 0.0:
                key = tuple(vector)
                clicks[key] = clicks.get(key, 0.0) + weight
    return clicks


def collision_free_clicks(clicks: Mapping[tuple[int, ...], float]) -> dict[tuple[int, ...], float]:
    """The three-click events by their set of clicking slots; a threshold vector is collision-free by construction."""
    law: dict[tuple[int, ...], float] = {}
    for vector, weight in clicks.items():
        if sum(vector) == PHOTONS:
            key = tuple(slot for slot, clicked in enumerate(vector) if clicked)
            law[key] = law.get(key, 0.0) + weight
    return law


def compositions(total: int) -> list[tuple[int, ...]]:
    """Every occupation of the window by `total` photons."""
    return [occ for occ in itertools.product(range(total + 1), repeat=WINDOW) if sum(occ) == total]


def mean_field_distribution(
    unitary: np.ndarray, emission: Mapping[tuple[int, ...], float], grid: int = PHASE_GRID
) -> dict[tuple[int, ...], float]:
    """Photon-number distribution of the random-phase mean-field sampler of Tichy et al. (2014).

    For an emission pattern with n_j photons on input slot j and N photons in all, each photon independently occupies
    output k with probability |sum_j U[k, j] sqrt(n_j) e^{i phi_j}|^2 / N, and the distribution averages over the
    phases phi_j. The first occupied input carries the global phase. |amplitude|^2 has degree at most one in each
    e^{+-i phi_j}, so a product of N <= MAX_EMITTED of them averages exactly on a uniform grid of more than N points per
    free phase."""
    out: dict[tuple[int, ...], float] = {}
    phases = np.exp(2j * np.pi * np.arange(grid) / grid)
    for pattern, weight in emission.items():
        inputs = [slot for slot, count in enumerate(pattern) if count]
        total = sum(pattern)
        require(total <= MAX_EMITTED, f"emission pattern {pattern} exceeds {MAX_EMITTED} photons")
        free = len(inputs) - 1
        mixtures: dict[tuple[int, ...], float] = {}
        cells = list(itertools.product(range(grid), repeat=free))
        outputs = compositions(total)
        factor = np.asarray(
            [math.factorial(total) / math.prod(math.factorial(c) for c in occ) for occ in outputs], dtype=float
        )
        counts = np.asarray(outputs, dtype=int)
        for cell in cells:
            phi = np.concatenate(([1.0 + 0j], phases[list(cell)])) if free else np.asarray([1.0 + 0j])
            amplitude = unitary[:, inputs] @ (np.sqrt([pattern[j] for j in inputs]) * phi)
            probability = np.abs(amplitude) ** 2 / total
            terms = factor * np.prod(probability[None, :] ** counts, axis=1)
            for occ, value in zip(outputs, terms, strict=True):
                mixtures[occ] = mixtures.get(occ, 0.0) + float(value) / len(cells)
        for occ, value in mixtures.items():
            out[occ] = out.get(occ, 0.0) + weight * value
    return out


def model_row(item: tuple[str, str, tuple[int, ...], Mapping[str, Any]]) -> dict[str, Any]:
    """Suppressed fraction and three-click probability per pulse of one (arm, model) under the given figures.

    figures holds hom, g2, efficiency (the six window detectors), each arm's window unitary and the suppressed set."""
    arm, model, slots, figures = item
    unitary = np.asarray(figures["unitary"][arm])
    efficiency = list(figures["efficiency"])
    suppressed = {tuple(out) for out in figures["suppressed"]}
    g2 = figures["g2"]
    if model == "indistinguishable":
        photons = perceval_distribution(window_circuit(unitary), slots, figures["hom"], g2)
    elif model == "distinguishable":
        photons = perceval_distribution(window_circuit(unitary), slots, 0.0, g2)
    elif model == "mean-field":
        emission = perceval_distribution(window_circuit(None), slots, 1.0, g2)
        photons = mean_field_distribution(unitary, emission)
    elif model == "ideal indistinguishable":
        photons = perceval_distribution(window_circuit(unitary), slots, 1.0, 0.0)
    else:
        raise ValueError(f"unknown model {model}")
    law = collision_free_clicks(detected_clicks(photons, efficiency))
    total = sum(law.values())
    inside = sum(value for out, value in law.items() if out in suppressed)
    return {"fraction": inside / total, "three_click_probability": total}


def forecast_figures(perfs: Mapping[str, Any], start: int, sources: tuple[int, ...]) -> dict[str, Any]:
    t_out, _, _, figures = read_perfs(perfs)
    slots = source_slots(start, sources)
    efficiency = detection_efficiency(t_out, figures["transmittance"])[start : start + WINDOW]
    unitary = {arm: window_unitary(arm, slots) for arm in ARMS}
    suppressed = suppressed_set(unitary["periodic"], slots)
    return {
        "hom": figures["hom"],
        "g2": figures["g2"],
        "clock_mhz": figures["clock_mhz"],
        "efficiency": efficiency,
        "unitary": {arm: matrix.tolist() for arm, matrix in unitary.items()},
        "suppressed": [list(out) for out in suppressed],
    }


MODEL_NAMES = ("ideal indistinguishable", "indistinguishable", "distinguishable", "mean-field")
HOM_GRID = (0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00)


def forecast(perfs: Mapping[str, Any], start: int, sources: tuple[int, ...]) -> dict[str, Any]:
    """Every model's fraction and three-click probability per arm at the performance figures, with the sensitivity of
    the indistinguishable forecast to g2 and HOM."""
    figures = forecast_figures(perfs, start, sources)
    slots = source_slots(start, sources)
    items = [(arm, model, slots, figures) for arm in ARMS for model in MODEL_NAMES]
    for scale in (0.5, 2.0):
        items.append(("periodic", "indistinguishable", slots, {**figures, "g2": figures["g2"] * scale}))
    items += [("periodic", "indistinguishable", slots, {**figures, "hom": hom}) for hom in HOM_GRID]
    rows = ordered_map(model_row, items, min_items=1)
    count = len(ARMS) * len(MODEL_NAMES)
    models = {
        arm: {model: rows[a * len(MODEL_NAMES) + m] for m, model in enumerate(MODEL_NAMES)}
        for a, arm in enumerate(ARMS)
    }
    g2_rows = rows[count : count + 2]
    hom_rows = rows[count + 2 :]
    return {
        "schema": "qd-belenos-suppression-forecast-v1",
        "figures": {"hom": figures["hom"], "g2": figures["g2"], "clock_mhz": figures["clock_mhz"]},
        "window_efficiency": [round(e, 6) for e in figures["efficiency"]],
        "models": models,
        "sensitivity": {
            "g2_half": g2_rows[0]["fraction"],
            "g2_double": g2_rows[1]["fraction"],
            "hom_curve": {f"{h:.2f}": r["fraction"] for h, r in zip(HOM_GRID, hom_rows, strict=True)},
        },
        "paired_contrast": {
            model: models["control"][model]["fraction"] - models["periodic"][model]["fraction"] for model in MODEL_NAMES
        },
    }


# ---------------------------------------------------------------- budgets: seconds, shots, credits


def modeled_seconds(shots: int, iterations: int, per_shot: float = SECONDS_PER_SHOT) -> float:
    """Provider seconds of a job whose every iteration runs `shots` shots: the fixed part plus the shot cost."""
    return iterations * (FIXED_ITERATION_SECONDS + shots * per_shot)


def expected_seconds(shots: int, iterations: int) -> float:
    """The written case's seconds for one job: the healthy-chip model at the iteration shot cap, scaled by
    SECONDS_MARGIN and rounded up to SECONDS_QUANTUM."""
    return float(math.ceil(modeled_seconds(shots, iterations) * SECONDS_MARGIN / SECONDS_QUANTUM) * SECONDS_QUANTUM)


def shot_estimate() -> dict[str, Any]:
    """Perceval's estimate_required_shots for each iteration's samples under the platform read's performance figures.

    The live processor record supplies the architecture and constraints, and the read's perfs replace the live ones, so
    the estimate is the one qd_platform.plan computes in the read's state. The recorder keeps every estimate payload
    computes; an estimate above the case's max_shots stops payload only after it is recorded."""
    from perceval import RemoteComputer
    from qd_platform import PlatformError, load_case, payload
    from qd_teleportation_rehearsal import anchor_perfs

    original = RemoteComputer.estimate_required_shots
    jobs: dict[str, Any] = {}
    for job in JOB_ORDER:
        estimates: list[tuple[int, int | None]] = []

        def recorded(
            self: Any,
            computation: Any,
            nsamples: int,
            param_values: dict[str, float] | None = None,
            sink: list[tuple[int, int | None]] = estimates,
        ) -> Any:
            value = original(self, computation, nsamples, param_values)
            sink.append((nsamples, value))
            return value

        RemoteComputer.estimate_required_shots = recorded
        manifest, circuit, _ = load_case(CASES / job)
        try:
            with anchor_perfs(str((CASES / READ).relative_to(ROOT))):
                payload(CASES / job, manifest, circuit, PLATFORM)
        except PlatformError:
            pass
        finally:
            RemoteComputer.estimate_required_shots = original
        require(len(estimates) == len(manifest["settings"]), f"{job}: {len(estimates)} estimates were recorded")
        require(all(value is not None for _, value in estimates), f"{job}: Perceval estimates no sample of interest")
        jobs[job] = {
            "settings": {s["name"]: value for s, (_, value) in zip(manifest["settings"], estimates, strict=True)},
            "samples": estimates[0][0],
            "total": sum(value for _, value in estimates if value is not None),
        }
    largest = max(value for job in jobs.values() for value in job["settings"].values())
    return {
        "schema": "qd-belenos-suppression-shot-estimate-v1",
        "basis": "estimate_required_shots under the perfs of " + str((CASES / READ).relative_to(ROOT)),
        "jobs": jobs,
        "largest": largest,
        "shots_per_iteration": math.ceil(largest * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM,
    }


def credits(shots: int) -> float:
    """Ceiling of one job: the per-job price plus the largest iteration's max_shots at the per-shot price."""
    return PER_JOB_CREDITS + PRICE_PER_SHOT * shots


# ---------------------------------------------------------------- writing and checking


def write_files() -> None:
    catalogue = platform_read(CASES)
    start, sources = choose_window(catalogue)
    for job, files in documents(start, sources).items():
        (CASES / job).mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (CASES / job / name).write_bytes(data)


def write_forecast() -> None:
    catalogue = platform_read(CASES)
    start, sources = choose_window(catalogue)
    record = forecast(processor(catalogue)["perfs"], start, sources)
    record["window"] = {"start": start, "sources": list(sources)}
    record["budget"] = {
        job: {
            "samples_per_iteration": SAMPLES_PER_ITERATION,
            "max_shots_per_iteration": SHOTS_PER_ITERATION,
            "modeled_seconds_healthy": modeled_seconds(SHOTS_PER_ITERATION, len(JOB_ORDER[job])),
            "modeled_seconds_degraded": modeled_seconds(
                SHOTS_PER_ITERATION, len(JOB_ORDER[job]), DEGRADED_SECONDS_PER_SHOT
            ),
            "expected_seconds": expected_seconds(SHOTS_PER_ITERATION, len(JOB_ORDER[job])),
            "credit_ceiling": credits(SHOTS_PER_ITERATION),
        }
        for job in JOB_ORDER
    }
    (CASES / FORECAST).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def same_numbers(left: Any, right: Any, path: str = "") -> str | None:
    """The path of the first difference between two parsed JSON values, numbers compared to 1e-9, else None."""
    if isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            return path or "."
        for key in left:
            found = same_numbers(left[key], right[key], f"{path}/{key}")
            if found is not None:
                return found
        return None
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return path
        for index, (a, b) in enumerate(zip(left, right, strict=True)):
            found = same_numbers(a, b, f"{path}[{index}]")
            if found is not None:
                return found
        return None
    if isinstance(left, int | float) and isinstance(right, int | float) and not isinstance(left, bool):
        return None if abs(left - right) <= BODY_TOLERANCE * max(1.0, abs(right)) else path
    return None if left == right else path


def compiled_unitary(circuit: Mapping[str, Any], params: Mapping[str, float]) -> np.ndarray:
    """Perceval's unitary of the template circuit at one setting's parameters."""
    import perceval as pcvl

    chip = pcvl.Circuit(circuit["modes"])
    for kind, mode, index in circuit["ops"]:
        value = math.pi if index is None else params[f"x{index}"]
        chip.add(mode, pcvl.BS.Rx(theta=value) if kind == "BS" else pcvl.PS(value))
    return np.asarray(chip.compute_unitary())


def slos_probabilities(unitary: np.ndarray, state: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Output distribution of identical photons over all modes from Perceval's SLOS backend."""
    import perceval as pcvl

    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    backend.set_input_state(pcvl.BasicState(list(state)))
    return {tuple(int(c) for c in s): float(p) for s, p in backend.prob_distribution().items()}


def check_slos(setting: Mapping[str, Any], circuit: Mapping[str, Any], start: int) -> dict[str, float]:
    """The threshold fact the analysis rests on, read from SLOS on the compiled 24-mode unitary: all probability stays
    in the window, the collision-free probability of each output equals its permanent, a suppressed output has zero
    probability, and outputs with a collision carry the remaining probability that a threshold detector merges."""
    unitary = compiled_unitary(circuit, setting["circuit_params"])
    sources = [mode for mode, count in enumerate(circuit["input_state"]) if count]
    distribution = slos_probabilities(unitary, circuit["input_state"])
    window = range(start, start + WINDOW)
    outside = sum(p for state, p in distribution.items() if any(state[m] for m in range(MODES) if m not in window))
    require(outside < BODY_TOLERANCE, f"{setting['name']}: {outside} of the probability leaves the window")
    block = unitary[start : start + WINDOW, start : start + WINDOW]
    slots = source_slots(start, sources)
    law = indistinguishable_law(block, slots)
    suppressed = {tuple(out) for out in setting["ideal"]["suppressed_outputs"]}
    free = 0.0
    for out, expected in law.items():
        state = [0] * MODES
        for slot in out:
            state[start + slot] = 1
        got = distribution.get(tuple(state), 0.0)
        require(
            abs(got - expected) < BODY_TOLERANCE,
            f"{setting['name']}: SLOS {got} differs from the permanent {expected} at {out}",
        )
        require(
            out not in suppressed or got < TOLERANCE,
            f"{setting['name']}: suppressed output {out} has probability {got}",
        )
        free += got
    require(abs(sum(distribution.values()) - 1.0) < BODY_TOLERANCE, f"{setting['name']}: SLOS is not normalized")
    return {"collision_free": free, "with_collision": 1.0 - free}


def check_models(start: int, sources: tuple[int, ...]) -> None:
    """The click model reduces to the permanent law without loss and noise, and the distinguishable model to the
    sum of squared products."""
    slots = source_slots(start, sources)
    for arm in ARMS:
        unitary = window_unitary(arm, slots)
        for model, law in (
            ("ideal indistinguishable", indistinguishable_law(unitary, slots)),
            ("distinguishable", distinguishable_law(unitary, slots)),
        ):
            hom = 1.0 if model == "ideal indistinguishable" else 0.0
            photons = perceval_distribution(window_circuit(unitary), slots, hom, 0.0)
            clicks = collision_free_clicks(detected_clicks(photons, [1.0] * WINDOW))
            for out, value in law.items():
                require(
                    abs(clicks.get(out, 0.0) - value) < BODY_TOLERANCE,
                    f"{arm} {model}: click model {clicks.get(out, 0.0)} differs from {value} at {out}",
                )
    # The mean-field average is exact: a finer grid returns the same distribution.
    emission = perceval_distribution(window_circuit(None), slots, 1.0, 0.014)
    unitary = window_unitary("periodic", slots)
    coarse = mean_field_distribution(unitary, emission)
    fine = mean_field_distribution(unitary, emission, PHASE_GRID + 2)
    for occupation, value in coarse.items():
        require(abs(fine.get(occupation, 0.0) - value) < BODY_TOLERANCE, f"mean-field grid not exact at {occupation}")


def check() -> int:
    catalogue = platform_read(CASES)
    start, sources = choose_window(catalogue)
    rebuilt = documents(start, sources)
    require(tuple(sources) == (16, 18, 20) and start == 16, f"layout {start} {sources} differs from the frozen window")
    require(len(set(COMPILATION_SEEDS)) == len(COMPILATION_SEEDS), "a compilation seed repeats")
    draw = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    require(
        list(COMPILATION_SEEDS) == draw["values"][: len(COMPILATION_SEEDS)],
        f"COMPILATION_SEEDS differ from the first {len(COMPILATION_SEEDS)} values of {DRAW}",
    )
    require(
        tuple(label_sum_rule())
        == suppressed_set(window_unitary("periodic", source_slots(start, sources)), source_slots(start, sources)),
        "label-sum rule differs from the permanents",
    )
    summary = []
    for job, files in rebuilt.items():
        for name, data in files.items():
            retained = (CASES / job / name).read_bytes()
            require(retained == data, f"{CASES / job}/{name} differs from the builder's bytes")
        manifest = json.loads(files["cases.json"])
        circuit = json.loads(files["circuit.json"])
        experiment, settings = template_experiment(manifest, circuit)
        require(experiment is not None and len(settings) == len(JOB_ORDER[job]), f"{job}: template binding failed")
        require(tuple(s["arm"] for s in settings) == JOB_ORDER[job], f"{job}: arm order differs from JOB_ORDER")
        for setting in settings:
            suppressed = setting["ideal"]["suppressed_outputs"]
            expected = [list(out) for out in label_sum_rule()] if setting["arm"] == "periodic" else []
            require(suppressed == expected, f"{setting['name']}: suppressed set {suppressed}")
        if job == "job-00":
            for arm in ARMS:
                setting = next(s for s in settings if s["arm"] == arm)
                summary.append(check_slos(setting, circuit, start))
        require(manifest["max_shots"] == SHOTS_PER_ITERATION * len(settings), f"{job}: max_shots")
    check_models(start, sources)
    retained_forecast = json.loads((CASES / FORECAST).read_text(encoding="utf-8"))
    fresh = forecast(processor(catalogue)["perfs"], start, sources)
    different = same_numbers({k: retained_forecast[k] for k in fresh}, fresh)
    require(different is None, f"{FORECAST} differs from the recomputed forecast at {different}")
    estimate = json.loads((CASES / ESTIMATE).read_text(encoding="utf-8"))
    require(
        estimate["shots_per_iteration"] == SHOTS_PER_ITERATION,
        f"{ESTIMATE} shots_per_iteration differs from SHOTS_PER_ITERATION",
    )
    require(
        estimate["shots_per_iteration"] == math.ceil(estimate["largest"] * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM,
        f"{ESTIMATE} shots_per_iteration is not the margin rule of its largest estimate",
    )
    print(
        f"{FAMILY}: {len(rebuilt)} jobs bound; suppressed set of {len(label_sum_rule())} outputs equals the "
        f"label-sum rule; collision-free mass {summary[0]['collision_free']:.6f} (periodic), "
        f"{summary[1]['collision_free']:.6f} (control)"
    )
    return 0


# ---------------------------------------------------------------- analysis


def state_vector(key: str) -> list[int]:
    return [int(c) for c in key.strip("|>").split(",")]


def tally_iteration(counts: Mapping[str, int], start: int, suppressed: set[tuple[int, ...]]) -> dict[str, Any]:
    """Counts of one iteration by cause: accepted events inside the suppressed set or outside it, and the rest."""
    window = range(start, start + WINDOW)
    out = {
        "suppressed": 0,
        "allowed": 0,
        "outside_window": 0,
        "collision": 0,
        "more_than_three": 0,
        "fewer_than_three": 0,
    }
    for key, count in counts.items():
        vector = state_vector(key)
        occupied = [mode for mode, n in enumerate(vector) if n > 0]
        if any(mode not in window for mode in occupied):
            out["outside_window"] += count
        elif any(vector[mode] > 1 for mode in occupied):
            out["collision"] += count
        elif len(occupied) > PHOTONS:
            out["more_than_three"] += count
        elif len(occupied) < PHOTONS:
            out["fewer_than_three"] += count
        elif tuple(mode - start for mode in occupied) in suppressed:
            out["suppressed"] += count
        else:
            out["allowed"] += count
    return out


def arm_summary(fractions: Sequence[float]) -> dict[str, Any]:
    """Mean, between-iteration standard error and one-sided upper bound of per-iteration fractions."""
    k = len(fractions)
    if k == 0:
        return {"iterations": 0, "mean": None, "sd": None, "se": None, "upper": None}
    mean = sum(fractions) / k
    if k == 1:
        return {"iterations": 1, "mean": mean, "sd": None, "se": None, "upper": None}
    sd = math.sqrt(sum((f - mean) ** 2 for f in fractions) / (k - 1))
    se = sd / math.sqrt(k)
    upper = mean + float(stats.t.ppf(1.0 - ALPHA, k - 1)) * se
    lower = mean - float(stats.t.ppf(1.0 - ALPHA, k - 1)) * se
    return {"iterations": k, "mean": mean, "sd": sd, "se": se, "upper": upper, "lower": lower}


def heterogeneity(rows: Sequence[tuple[int, int]]) -> dict[str, Any] | None:
    """Pearson chi-square of homogeneity of the per-iteration (suppressed, total) counts of one arm."""
    rows = [(a, n) for a, n in rows if n > 0]
    if len(rows) < 2:
        return None
    pooled = sum(a for a, _ in rows) / sum(n for _, n in rows)
    if pooled in (0.0, 1.0):
        return None
    chi = sum((a - n * pooled) ** 2 / (n * pooled * (1 - pooled)) for a, n in rows)
    return {"chi_square": chi, "degrees": len(rows) - 1, "p": float(stats.chi2.sf(chi, len(rows) - 1))}


def run_forecast(run: Path, retained: Mapping[str, Any]) -> dict[str, Any]:
    """The forecast at the run's perfs_at_plan when submission.json holds a full performance record, else the retained
    forecast of the case."""
    path = run / "submission.json"
    if path.exists():
        perfs = json.loads(path.read_text(encoding="utf-8")).get("perfs_at_plan")
        if isinstance(perfs, dict) and "Transmission per mode (%)" in perfs:
            manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
            layout = manifest["layout"]
            return forecast(perfs, int(layout["window_start"]), tuple(layout["source_modes"]))
    return dict(retained)


def mean_over(forecasts: Sequence[Mapping[str, Any]], arm: str, model: str) -> float:
    return sum(f["models"][arm][model]["fraction"] for f in forecasts) / len(forecasts)


def interpolated_hom(fraction: float, forecasts: Sequence[Mapping[str, Any]]) -> float | None:
    """The HOM visibility at which the indistinguishable forecast of the periodic arm equals `fraction`, by linear
    interpolation of the forecast's hom_curve at the other figures of the run; None outside the curve's range."""
    curves = [f["sensitivity"]["hom_curve"] for f in forecasts]
    homs = sorted(curves[0], key=float)
    values = [sum(c[h] for c in curves) / len(curves) for h in homs]
    if not min(values) <= fraction <= max(values):
        return None
    return float(np.interp(fraction, values[::-1], [float(h) for h in homs][::-1]))


# The causes tally_iteration excludes from the accepted events.
EXCLUSIONS = ("outside_window", "collision", "more_than_three", "fewer_than_three")


def bound_setting(settings: Sequence[Mapping[str, Any]], entry: Any) -> int:
    """The index of the one setting a result iteration binds to by its compilation_seed, which the case makes unique.

    A result iteration that names no seed, names a seed no setting holds, or carries circuit_params that differ from
    its setting's raises, so a dropped or reordered iteration never moves counts between arms."""
    iteration = entry.get("iteration") if isinstance(entry, dict) else None
    seed = iteration.get("compilation_seed") if isinstance(iteration, dict) else None
    matches = [i for i, setting in enumerate(settings) if seed is not None and setting["compilation_seed"] == seed]
    require(len(matches) == 1, f"a result iteration with compilation_seed {seed!r} binds to {len(matches)} settings")
    values = iteration.get("circuit_params") if isinstance(iteration, dict) else None
    if values is not None:
        expected = settings[matches[0]]["circuit_params"]
        require(
            sorted(values) == sorted(expected) and all(abs(values[k] - expected[k]) < BODY_TOLERANCE for k in expected),
            f"{settings[matches[0]]['name']}: the result iteration's circuit_params differ from the setting's",
        )
    return matches[0]


def analyze(runs: Sequence[Path], retained: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Preregistered endpoints of the collected runs of both jobs: per-arm suppressed fractions with their
    between-iteration intervals, the three models' forecasts and the decision.

    Each job name appears once and every compilation seed once across the runs, so a repeat of a failed job
    supersedes the original and never pools with it. Iterations that carry no counts (missing, malformed, error) and
    iterations below MIN_EVENTS accepted events are tallied and do not count toward their arm."""
    if retained is None:
        retained = json.loads((CASES / FORECAST).read_text(encoding="utf-8"))
    per_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    below_floor: list[dict[str, Any]] = []
    uncounted = dict.fromkeys(UNCOUNTED, 0)
    forecasts = []
    jobs: dict[str, str] = {}
    seeds: set[int] = set()
    yields: dict[str, int] = {}
    for run in runs:
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        job = manifest["job"]
        require(job not in jobs, f"{run.name} repeats job {job} already read from {jobs.get(job)}")
        jobs[job] = run.name
        run_seeds = {setting["compilation_seed"] for setting in manifest["settings"]}
        require(not run_seeds & seeds, f"{run.name} reuses compilation seeds of another run")
        seeds |= run_seeds
        start = int(manifest["layout"]["window_start"])
        forecasts.append(run_forecast(run, retained))
        # Both arms score the periodic setting's suppressed set; the control's own set is empty.
        suppressed = {
            tuple(out)
            for setting in manifest["settings"]
            if setting["arm"] == "periodic"
            for out in setting["ideal"]["suppressed_outputs"]
        }
        bound: set[int] = set()
        yields[job] = 0
        for entry in results.get("iterations") or []:
            kind = next(
                (k for k in UNCOUNTED if isinstance(entry, dict) and entry.get(k)),
                None if isinstance(entry, dict) else "malformed",
            )
            if kind is not None:
                uncounted[kind] += 1
                continue
            index = bound_setting(manifest["settings"], entry)
            require(
                index not in bound, f"{run.name}: two result iterations bind to {manifest['settings'][index]['name']}"
            )
            bound.add(index)
            setting = manifest["settings"][index]
            counts = entry.get("counts")
            if not counts:
                uncounted["missing"] += 1
                continue
            tally = tally_iteration(counts, start, suppressed)
            accepted = tally["suppressed"] + tally["allowed"]
            yields[job] += accepted
            row = {
                "name": setting["name"],
                "job": job,
                "suppressed": tally["suppressed"],
                "accepted": accepted,
                "fraction": tally["suppressed"] / accepted if accepted else None,
                "excluded": {cause: tally[cause] for cause in EXCLUSIONS},
            }
            if accepted >= MIN_EVENTS:
                per_arm[setting["arm"]].append(row)
            else:
                below_floor.append({**row, "arm": setting["arm"]})
    summary = {arm: arm_summary([row["fraction"] for row in rows]) for arm, rows in per_arm.items()}
    pooled = {}
    for arm, rows in per_arm.items():
        events = sum(row["accepted"] for row in rows)
        hits = sum(row["suppressed"] for row in rows)
        pooled[arm] = {"events": events, "suppressed": hits, "fraction": hits / events if events else None}
    record: dict[str, Any] = {
        "schema": "qd-belenos-suppression-analysis-v1",
        "runs": [run.name for run in runs],
        "iterations": per_arm,
        "below_event_floor": below_floor,
        "uncounted_iterations": uncounted,
        "job_yield": yields,
        "summary": summary,
        "pooled": pooled,
        "heterogeneity": {
            arm: heterogeneity([(row["suppressed"], row["accepted"]) for row in rows]) for arm, rows in per_arm.items()
        },
        "excluded_events": {
            arm: {cause: sum(row["excluded"][cause] for row in rows) for cause in EXCLUSIONS}
            for arm, rows in per_arm.items()
        },
        "forecast": {arm: {model: mean_over(forecasts, arm, model) for model in MODEL_NAMES} for arm in ARMS},
    }
    record["decision"] = decide(record, forecasts)
    return record


def paired_contrast(control: Mapping[str, Any], periodic: Mapping[str, Any]) -> dict[str, float]:
    """s_control - s_periodic with its between-iteration standard error and one-sided lower 1 - ALPHA bound; the
    interval takes the smaller arm's degrees of freedom."""
    contrast = control["mean"] - periodic["mean"]
    se = math.hypot(control["se"], periodic["se"])
    degrees = min(control["iterations"], periodic["iterations"]) - 1
    return {"observed": contrast, "se": se, "lower": contrast - float(stats.t.ppf(1.0 - ALPHA, degrees)) * se}


def decide(record: Mapping[str, Any], forecasts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The preregistered decision. Both arms need MIN_ITERATIONS counted iterations; otherwise it is undecided.

    suppression observed needs both rules: the upper 1 - ALPHA bound of the periodic fraction lies at least
    NULL_MARGIN below the smaller of the distinguishable and mean-field forecasts, and the lower 1 - ALPHA bound of
    the paired contrast s_control - s_periodic reaches CONTRAST_MARGIN (the contrast is 0 for distinguishable photons
    at any detector efficiencies). control valid: the control fraction lies within CONTROL_TOLERANCE of the
    indistinguishable forecast of the control. level: the periodic fraction lies within max(FORECAST_TOLERANCE, 3 se)
    of the indistinguishable forecast; compile error and g2 raise s, so only a fraction below the forecast is
    unambiguous."""
    periodic, control = record["summary"]["periodic"], record["summary"]["control"]
    forecast_row = record["forecast"]
    out: dict[str, Any] = {
        "complete": periodic["iterations"] >= MIN_ITERATIONS and control["iterations"] >= MIN_ITERATIONS,
    }
    if not out["complete"]:
        out["verdict"] = "undecided"
        return out
    null = min(forecast_row["periodic"]["distinguishable"], forecast_row["periodic"]["mean-field"])
    out["null_forecast"] = null
    out["absolute_rule"] = bool(periodic["upper"] <= null - NULL_MARGIN)
    out["paired_contrast"] = {
        **paired_contrast(control, periodic),
        "indistinguishable": forecast_row["control"]["indistinguishable"]
        - forecast_row["periodic"]["indistinguishable"],
        "distinguishable": forecast_row["control"]["distinguishable"] - forecast_row["periodic"]["distinguishable"],
        "mean-field": forecast_row["control"]["mean-field"] - forecast_row["periodic"]["mean-field"],
    }
    out["contrast_rule"] = bool(out["paired_contrast"]["lower"] >= CONTRAST_MARGIN)
    out["suppression_observed"] = out["absolute_rule"] and out["contrast_rule"]
    out["control_deviation"] = control["mean"] - forecast_row["control"]["indistinguishable"]
    out["control_valid"] = bool(abs(out["control_deviation"]) <= CONTROL_TOLERANCE)
    tolerance = max(FORECAST_TOLERANCE, 3 * periodic["se"])
    deviation = periodic["mean"] - forecast_row["periodic"]["indistinguishable"]
    out["level_deviation"] = deviation
    out["level_tolerance"] = tolerance
    out["level"] = "at" if abs(deviation) <= tolerance else ("above" if deviation > 0 else "below")
    out["hom_lower_bound"] = interpolated_hom(periodic["mean"], forecasts)
    if not out["control_valid"]:
        out["verdict"] = "invalid control: the detectors or the selection deplete or inflate the suppressed set"
    elif not out["suppression_observed"]:
        out["verdict"] = "no suppression beyond the distinguishable and mean-field forecasts"
    else:
        wording = {
            "at": "suppression at the level the indistinguishable forecast predicts",
            "above": "suppression weaker than the indistinguishable forecast",
            "below": "suppression stronger than the indistinguishable forecast",
        }
        out["verdict"] = wording[out["level"]]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", action="store_true")
    group.add_argument("--forecast", action="store_true")
    group.add_argument("--estimate", action="store_true")
    group.add_argument("--analyze", type=Path, nargs="+")
    args = parser.parse_args()
    if args.build:
        write_files()
        return 0
    if args.forecast:
        write_forecast()
        return 0
    if args.estimate:
        (CASES / ESTIMATE).write_text(json.dumps(shot_estimate(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    if args.analyze:
        record = analyze(args.analyze)
        for run in args.analyze:
            (run / "analysis.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(record["decision"]["verdict"])
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
