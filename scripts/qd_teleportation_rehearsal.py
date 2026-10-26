"""Single-chip teleportation rehearsal on qpu:belenos: one job of six inputs, each read in its matching basis.

docs/design/ascella-belenos-entanglement-teleportation.md, sections "Single-chip rehearsal (job-00)" and "Recovered-chip
rehearsal (job-01)", fixes the request. Three photons enter eight logical modes q0 q1 a0 a1 b0 b1 h0 h1 of one chip:

- q carries the input on modes (q0, q1) in dual rail, one of the six Pauli eigenstates;
- a (a0, a1) is prepared in |+> and b (b0, b1) in |0>, and the postselected Ralph CNOT of
  ``pcvl.catalog['postprocessed cnot']`` (control a, target b, vacuum heralds h0 h1) turns them into the Bell pair;
- the partial Bell analyzer of qd_network_protocol.analyzer_unitary mixes q_j with a_j on balanced beam splitters;
- the receiver b is read in the basis of the input's axis, and the Pauli frame of the analyzer's click pattern
  (qd_network_protocol.teleportation_frames) is applied in analysis by decode_bit.

An event is accepted when it carries exactly three threshold clicks across all 24 returned modes, two on the
analyzer in a pattern of the frame table, one on b and none on the heralds or outside the logical modes. The ideal
instrument accepts each input with probability 1/18 (CNOT 1/9 times analyzer 1/2) at conditional fidelity 1.

The eight logical modes occupy eight consecutive chip modes. photonic_template (hypercomplex_cases) decomposes the
eight-mode unitary of every setting into the same nearest-neighbor Rx/phase mesh, and a case's layout places the
logical modes on chip modes: the three photons enter source-connected inputs, no mode of the window has a dark count
above DARK_LIMIT, and the two rails of each qubit have the closest output transmissions its platform read offers.

Each template iteration carries its own compilation_seed, the service's per-iteration compilation randomness
(qd_platform.payload sends settings[k]["compilation_seed"]). CASE_SEEDS holds each case's six values, one QRNG draw
value per input in the order of the iterations, and validation requires exactly the case's seeds. The analysis draws
nothing.

A Request is the budget-free part of a case: its layout, its seeds, its anchor read (the platform read whose
performance figures preregister the analysis, size max_shots and serve the --anchor gate), its rule and its block
count. job-00 follows the decision rule (DECISION): six iterations and a beats-classical verdict against the bound
at the modeled attempts. job-01 follows the descriptive rule (DESCRIPTIVE): two blocks of the six inputs, block B in
mirrored order, an anytime-valid lower confidence bound on the accepted events' average correctness, a block
homogeneity veto, and two classical comparisons that hold only under the assumptions each names. A Job adds the budgets
and the written case's plan arguments. job-00 takes the 2026-10-24 read ANCHOR_READ as its anchor; a later case takes
its own platform read, so its decision rule describes the chip state it is sent into and only the live gate applies.
--prepare JOB derives such a case from its retained read (CASES/JOB/platform-read/catalogue.json): the layout,
noise-model.json, shot-estimate.json, and the REQUESTS and JOBS rows it prints for the change that registers the case.

--check rebuilds every registered case in memory, requires the retained bytes (cases.json within the shared check
tolerance, circuit.json exactly), validates them through qd_platform.template_experiment and the closed form of every
setting, and requires the refusal of mutated requests. --justify retains job-00's noise-model derivation of the sample
budget, and --estimate retains Perceval's shot estimate in its anchor state. --simulate OUT [JOB] writes a results.json
of the local noise simulation of a registered case (job-00 by default) into OUT beside the staged request. --analyze RUN
parses RUN/results.json into the joint histogram of qd_network_protocol.joint_teleportation_scores. --body JOB and
--plan JOB read the live platform record and send no job; with --anchor they evaluate the request under the anchor
read's performance figures, which a case anchored at its own read refuses.

--submit RUN APPROVAL sends the written case once. RUN holds copies of the frozen cases.json and circuit.json and
nothing a submission writes; the platform catalogue and raw route answers land in RUN/platform-before first.
qd_platform.submit plans afresh under the token's submit lock and calls binding as its verify step, which refuses
the request unless the fresh body equals the retained job-body.json in every field but process_id and the noise
model's pooled fidelity at the live performance figures reaches the justified mean score F*. A refusal writes no
checkpoint and sends nothing; an accepted request leaves RUN/submit-model.json with the model it was admitted under.
With --anchor the plan, the shot estimate and the model gate read the anchor read's performance figures (the
written case's anchor approval); RUN/platform-before keeps the live record, and submit-model.json carries the live
model beside the admitting one.

Usage:
  "$PYTHON" scripts/qd_teleportation_rehearsal.py [--check | --justify | --estimate | --prepare JOB | JOB]
  "$PYTHON" scripts/qd_teleportation_rehearsal.py [--body JOB | --plan JOB] [--anchor]
  "$PYTHON" scripts/qd_teleportation_rehearsal.py [--simulate OUT [JOB] | --analyze RUN [--check]]
  "$PYTHON" scripts/qd_teleportation_rehearsal.py --submit RUN APPROVAL [--anchor]
"""

from __future__ import annotations

import copy
import itertools
import json
import math
import sys
import tempfile
import warnings
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from bdsc_certificate import close  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_classical_benchmark import attempts_benchmark  # noqa: E402
from qd_network_protocol import (  # noqa: E402
    SIX_STATES,
    SQRT_HALF,
    ProtocolError,
    analyzer_unitary,
    bernoulli_decision_count,
    decode_bit,
    embed,
    joint_teleportation_scores,
    propagate,
    teleportation_frames,
)
from qd_platform import (  # noqa: E402
    PlatformError,
    body_mitigations,
    iteration_form,
    load_case,
    observe,
    payload,
    plan,
    sha256_bytes,
    snapshot,
    submit,
    template_experiment,
    write_json,
)
from qd_schedule import body_digest  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLATFORM = "qpu:belenos"
FAMILY = "teleportation_rehearsal"
CASES = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/ascella-belenos-entanglement-teleportation.md"
MODES = 24
LOGICAL = 8
Q0, Q1, A0, A1, B0, B1, H0, H1 = range(LOGICAL)
SOURCES = (Q0, A0, B0)
MIN_CLICKS = 3
MAX_DURATION = 300
PER_JOB_CREDITS = 1.0
PRICE_PER_SHOT = 1e-6
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9
# The platform record's connected_input_modes: a photon on any other mode makes the service re-route and re-transpile.
CONNECTED = (0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22)
# A window mode whose dark rate exceeds DARK_LIMIT per second would add a spurious click per 1 / (clock * DARK_LIMIT)
# pulses; at the 4.94 MHz clock this bounds the per-pulse dark probability at 2e-5.
DARK_LIMIT = 100.0
# Chip mode of each logical mode q0 q1 a0 a1 b0 b1 h0 h1, chosen by choose_layout from the retained platform read.
WINDOW = 8
LAYOUT = (8, 14, 9, 12, 13, 11, 10, 15)
# The compilation_seed of each iteration (+Z, -Z, +X, -X, +Y, -Y): indices 0 to 5, in index order, of the ANU QRNG
# draw docs/evidence/anu_qrng/draw-2026-10-25T204252Z.json, registered in docs/evidence/qrng_seeds/allocations.json.
COMPILATION_SEEDS = (42862, 37522, 45230, 47441, 29246, 17743)
# The compilation_seed of each job-01 iteration in submission order. Block A (+Z, -Z, +X, -X, +Y, -Y) takes indices
# 0 to 5 of the Cisco Outshift QRNG draw docs/evidence/outshift_qrng/draw-2026-10-26T204106Z.json and block B (-Y,
# +Y, -X, +X, -Z, +Z) indices 0 to 5 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-26T230602Z.json, each in
# index order, registered in docs/evidence/qrng_seeds/allocations.json.
JOB_01_COMPILATION_SEEDS = (8608, 30481, 4339, 55973, 12504, 37710, 5573, 39099, 45322, 55527, 43939, 10803)
CASE_SEEDS = {"job-00": COMPILATION_SEEDS, "job-01": JOB_01_COMPILATION_SEEDS}
DECISION = "decision-v1"
DESCRIPTIVE = "descriptive-v2"
# The rule and the block count of each seeded case.
CASE_DESIGNS = {"job-00": (DECISION, 1), "job-01": (DESCRIPTIVE, 2)}
ANALYZER_MODES = (Q0, Q1, A0, A1)
RECEIVER_MODES = (B0, B1)
HERALD_MODES = (H0, H1)

# The platform read the layout and the transmission variants take: the fresh read of the case.
READ = "platform-read/catalogue.json"
# The earlier read whose figures (HOM 88.8 %, g2 1.1 %, Transmittance 5.5 %) docs/notes/quandela/calibration.md
# "Current state" tabulates; the noise anchor and the shot ceilings come from it.
ANCHOR_READ = (
    "results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/platform-after/catalogue.json"
)
ALPHA = 0.01
BETA = 0.10
# Samples exceed the decision count by this factor, so a shortfall of accepted outcomes of one fifth keeps the power.
SAMPLE_MARGIN = 1.25
# max_shots exceeds the largest Perceval estimate_required_shots of an input by this factor.
SHOT_MARGIN = 1.25
SAMPLE_QUANTUM = 100
SHOT_QUANTUM = 100_000
ESTIMATE = "shot-estimate.json"
# The allowance for what no noise variant models: compilation phase error and dark clicks (bounded in justify).
UNMODELED_ALLOWANCE = 0.02
SYSTEMATIC_QUANTUM = 0.01
# The server's compilation time of one template iteration, the figure of job-00's written case.
COMPILE_SECONDS = 10.0
# The written case's seconds exceed the modeled compile and acquisition time by this factor, in whole minutes.
SECONDS_MARGIN = 1.25
SECONDS_QUANTUM = 60
# The descriptive rule's preregistered samples per iteration.
DESCRIPTIVE_SAMPLES = 1200
# The six-state classical value of a two-copy input sector under free postselection.
TWO_COPY_BOUND = 0.75
# Each input's attempts lie within this factor of the modeled profile in the attempt-box comparison; the five noise
# variants of job-00's derivation need at most 1.0964.
BOX_RATIO = 1.1
HOMOGENEITY_ALPHA = 0.01
BREAK_EVEN_CEILING = 3.0
BREAK_EVEN_TOLERANCE = 0.005
TWO_COPY_ASSUMPTIONS = (
    "one label-blind trace-nonincreasing instrument acts on every input",
    "equal optical attempts per input (uniform priors), since unequal priors raise the six-state value",
    "the input source emits at most two copies per attempt (Perceval's truncated source model)",
    "the classical device may postselect on photon number with no acceptance constraint",
)
BOX_ASSUMPTIONS = (
    "one label-blind trace-nonincreasing instrument acts on every input",
    "single-copy inputs: acceptance blind to photon number",
    "each input's optical attempts lie within the ratio of the modeled profile",
)


@dataclass(frozen=True)
class Request:
    """The budget-free part of a case: the chip mode of each logical mode, the compilation seed of each iteration in
    submission order (schedule), the repository path of the anchor read, whose performance figures preregister the
    analysis, size max_shots and serve the --anchor gate, and the case's rule and block count."""

    name: str
    layout: tuple[int, ...]
    seeds: tuple[int, ...]
    anchor_read: str
    rule: str = DECISION
    blocks: int = 1

    @property
    def directory(self) -> Path:
        return CASES / self.name

    @property
    def own_anchor(self) -> bool:
        """True when the anchor read is the case's own platform read, so only the live gate applies."""
        return ROOT / self.anchor_read == self.directory / READ


@dataclass(frozen=True)
class Job:
    """One retained request: per-iteration budgets and the written case's plan arguments.

    The credit ceiling is the per-job price plus the largest iteration's max_shots at 1e-6 credits per shot, written
    out so the plan compares a literal; expected seconds are the written case's upper bound."""

    request: Request
    samples: int
    shots: int
    credit_ceiling: float
    expected_seconds: float

    @property
    def name(self) -> str:
        return self.request.name


REQUESTS = {"job-00": Request("job-00", LAYOUT, COMPILATION_SEEDS, ANCHOR_READ)}
JOBS = {"job-00": Job(REQUESTS["job-00"], 900, 1_200_000, 2.2, 120.0)}
STAGED = ("cases.json", "circuit.json")
# qd_platform.snapshot's catalogue and qd_platform.observe's raw route answers, read before the submission.
BEFORE = "platform-before"
SUBMIT_MODEL = "submit-model.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------- the instrument


@cache
def frames() -> dict[str, tuple[int, int]]:
    """Pauli frame (x, z) of each accepted analyzer click pattern, as qd_network_protocol propagates it."""
    return dict(teleportation_frames().frames)


@cache
def cnot_unitary() -> np.ndarray:
    """The 6-mode unitary of the postselected Ralph CNOT: control (0, 1), target (2, 3), vacuum ancillas (4, 5)."""
    import perceval as pcvl

    experiment = pcvl.catalog["postprocessed cnot"].build_experiment()
    matrix = np.asarray(experiment.unitary_circuit().compute_unitary(), dtype=complex)
    require(matrix.shape == (6, 6), f"the CNOT circuit spans {matrix.shape}, not six modes")
    require(dict(experiment.heralds) == {4: 0, 5: 0}, f"the CNOT heralds are {dict(experiment.heralds)}")
    return matrix


def preparation(theta: float, phi: float) -> np.ndarray:
    """Unitary on (q0, q1) whose first column is (cos(theta/2), e^{i phi} sin(theta/2))."""
    rotation = np.array([[math.cos(theta / 2), -math.sin(theta / 2)], [math.sin(theta / 2), math.cos(theta / 2)]])
    return np.asarray(np.diag([1.0, np.exp(1j * phi)]) @ rotation, dtype=complex)


def readout(basis: str) -> np.ndarray:
    """Receiver rotation: identity for Z, a balanced beam splitter for X, a -pi/2 phase on b1 ahead of it for Y."""
    hadamard = np.array([[1, 1], [1, -1]], dtype=complex) * SQRT_HALF
    if basis == "Z":
        return np.eye(2, dtype=complex)
    if basis == "X":
        return hadamard
    if basis == "Y":
        return np.asarray(hadamard @ np.diag([1.0, -1j]), dtype=complex)
    raise ProtocolError(f"unknown receiver basis {basis}")


def input_angles(amplitudes: tuple[complex, complex]) -> tuple[float, float]:
    """(theta, phi) of the state alpha |0> + beta |1> = cos(theta/2) |0> + e^{i phi} sin(theta/2) |1>, up to phase."""
    alpha, beta = complex(amplitudes[0]), complex(amplitudes[1])
    theta = 2.0 * math.atan2(abs(beta), abs(alpha))
    phi = 0.0 if abs(alpha) < TOLERANCE or abs(beta) < TOLERANCE else float(np.angle(beta) - np.angle(alpha))
    return theta, phi


def logical_unitary(label: str) -> np.ndarray:
    """The 8 x 8 unitary of one input: readout after analyzer after CNOT after the q and a preparations."""
    row = next((row for row in SIX_STATES if row[0] == label), None)
    if row is None:
        raise ProtocolError(f"unknown input {label}")
    _, amplitudes, basis, _ = row
    hadamard = np.array([[1, 1], [1, -1]], dtype=complex) * SQRT_HALF
    prepare = embed([(preparation(*input_angles(amplitudes)), (Q0, Q1)), (hadamard, (A0, A1))], LOGICAL)
    cnot = embed([(cnot_unitary(), (A0, A1, B0, B1, H0, H1))], LOGICAL)
    analyze = embed([(analyzer_unitary(), ANALYZER_MODES)], LOGICAL)
    receive = embed([(readout(basis), RECEIVER_MODES)], LOGICAL)
    return np.asarray(receive @ analyze @ cnot @ prepare, dtype=complex)


def window_matrix(logical: np.ndarray, layout: Sequence[int]) -> np.ndarray:
    """The logical unitary in chip-window coordinates: entry [layout[o] - w, layout[i] - w] holds [o, i]."""
    start = min(layout)
    slots = [mode - start for mode in layout]
    require(sorted(slots) == list(range(LOGICAL)), f"layout {tuple(layout)} is not eight consecutive chip modes")
    matrix = np.zeros((LOGICAL, LOGICAL), dtype=complex)
    matrix[np.ix_(slots, slots)] = logical
    return matrix


def chip_operator(logical: np.ndarray, layout: Sequence[int]) -> np.ndarray:
    """The 24-mode operator: the window block at the layout's first mode, identity elsewhere."""
    start = min(layout)
    full = np.eye(MODES, dtype=complex)
    full[start : start + LOGICAL, start : start + LOGICAL] = window_matrix(logical, layout)
    return full


def source_state(layout: Sequence[int]) -> list[int]:
    """The 24-entry input occupation: one photon on each of q0, a0 and b0."""
    state = [0] * MODES
    for logical in SOURCES:
        state[layout[logical]] = 1
    return state


def classify(clicks: Sequence[int], layout: Sequence[int]) -> tuple[str, str | None, int | None]:
    """(outcome, Bell pattern, raw receiver bit) of a 24-mode threshold click vector.

    The outcomes are "below" and "excess" for fewer or more than three clicks, "outside" for a click off the logical
    modes, "herald", "receiver" for other than one click on b, "pattern" for an analyzer pattern outside the frame
    table, and "accepted". The pattern lists the clicks of (c0, c1, d0, d1) in the analyzer's output order."""
    flags = [1 if count else 0 for count in clicks]
    total = sum(flags)
    if total < MIN_CLICKS:
        return "below", None, None
    if total > MIN_CLICKS:
        return "excess", None, None
    logical = [flags[mode] for mode in layout]
    if sum(logical) != total:
        return "outside", None, None
    if any(logical[mode] for mode in HERALD_MODES):
        return "herald", None, None
    if sum(logical[mode] for mode in RECEIVER_MODES) != 1:
        return "receiver", None, None
    pattern = "".join(str(logical[mode]) for mode in ANALYZER_MODES)
    if pattern not in frames():
        return "pattern", None, None
    return "accepted", pattern, 0 if logical[B0] else 1


def expected_bit(label: str) -> int:
    sign = next(sign for name, _, _, sign in SIX_STATES if name == label)
    return 0 if sign == 1 else 1


def scored(label: str, outcomes: Mapping[tuple[int, ...], float], layout: Sequence[int]) -> tuple[float, float]:
    """(accepted probability, correct probability) of a distribution over 24-mode click vectors."""
    basis = next(basis for name, _, basis, _ in SIX_STATES if name == label)
    accepted = correct = 0.0
    for clicks, probability in outcomes.items():
        outcome, pattern, raw = classify(clicks, layout)
        if outcome != "accepted" or pattern is None or raw is None:
            continue
        x, z = frames()[pattern]
        accepted += probability
        correct += probability if decode_bit(basis, raw, x, z) == expected_bit(label) else 0.0
    return accepted, correct


def ideal_clicks(label: str, layout: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution of the noiseless photon-number-resolving propagation of the three photons."""
    unitary = chip_operator(logical_unitary(label), layout)
    output = propagate(unitary, {tuple(source_state(layout)): 1.0 + 0.0j})
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, amplitude in output.items():
        key = tuple(1 if count else 0 for count in occupation)
        clicks[key] = clicks.get(key, 0.0) + abs(amplitude) ** 2
    return clicks


# ---------------------------------------------------------------- the template request


def inputs() -> list[dict[str, Any]]:
    """The six iterations in design order: the Pauli eigenstates, each read in its own axis."""
    rows = []
    for label, amplitudes, basis, sign in SIX_STATES:
        theta, phi = input_angles(amplitudes)
        rows.append({"label": label, "basis": basis, "sign": sign, "theta": theta, "phi": phi})
    return rows


def schedule(request: Request) -> list[dict[str, Any]]:
    """The iterations in submission order. A decision case runs the six inputs once in design order; a descriptive
    case runs block A in design order and block B in mirrored order, which balances a linear drift across inputs,
    each row naming its block."""
    rows = inputs()
    if request.rule == DECISION:
        require(request.blocks == 1, f"{request.name}: a decision case runs one block")
        return rows
    require(request.rule == DESCRIPTIVE and request.blocks == 2, f"{request.name}: rule {request.rule!r}")
    return [{**row, "block": block} for block, order in (("A", rows), ("B", rows[::-1])) for row in order]


def ideal(label: str, layout: Sequence[int]) -> dict[str, float]:
    accepted, correct = scored(label, ideal_clicks(label, layout), layout)
    return {
        "accepted_probability": round(float(accepted), 12),
        "conditional_fidelity": round(float(correct / accepted), 12),
    }


def build_setting(item: tuple[int, dict[str, Any], Request]) -> tuple[dict[str, Any], dict[str, Any]]:
    """The template mesh and the manifest setting of one input."""
    index, row, request = item
    layout = request.layout
    logical = logical_unitary(row["label"])
    window = window_matrix(logical, layout)
    mesh, parameters = photonic_template(window)
    full = chip_operator(logical, layout)
    start = min(layout)
    source = layout[Q0]
    return mesh, {
        "name": row["label"],
        "observation_index": index,
        **row,
        "ideal": ideal(row["label"], layout),
        "circuit_params": parameters,
        "compilation_seed": request.seeds[index],
        "column": [[float(value.real), float(value.imag)] for value in full[:, source]],
        "operator": encoded(full),
        "window_start": start,
    }


def circuit_document(mesh: dict[str, Any], layout: Sequence[int]) -> dict[str, Any]:
    """The 24-mode template: the window mesh shifted to the layout's first mode and the three-photon input."""
    start = min(layout)
    ops = [[kind, mode + start, index] for kind, mode, index in mesh["ops"]]
    return {
        "schema": "qd-template-circuit-v1",
        "modes": MODES,
        "input_state": source_state(layout),
        "parameters": mesh["parameters"],
        "ops": ops,
    }


def request_parts(request: Request) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The manifest settings in submission order and the one template circuit they share."""
    rows = schedule(request)
    require(len(request.seeds) == len(rows), f"{request.name}: {len(request.seeds)} seeds for {len(rows)} iterations")
    built = ordered_map(build_setting, [(index, row, request) for index, row in enumerate(rows)], min_items=1)
    template = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == template, f"input {index} needs another mesh than input 0")
    return [setting for _, setting in built], circuit_document(template, request.layout)


def documents(job: Job) -> dict[str, bytes]:
    """{"cases.json": bytes, "circuit.json": bytes} of the job's request."""
    settings, circuit = request_parts(job.request)
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    count = len(settings)
    derived = retained_derivation(job.name)
    layout = job.request.layout
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job.name,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": count,
        "min_detected_photons": MIN_CLICKS,
        "max_samples": job.samples * count,
        "max_shots": job.shots * count,
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": sorted(layout),
        "layout": {"logical": ["q0", "q1", "a0", "a1", "b0", "b1", "h0", "h1"], "chip_modes": list(layout)},
        "eligibility": "three threshold clicks across all 24 returned modes: two on the analyzer in a frame-table "
        "pattern, one on b, none on the heralds or outside the logical modes",
        "frames": {pattern: list(frame) for pattern, frame in sorted(frames().items())},
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": preregistration(job.request, derived),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def preregistration(request: Request, derived: Mapping[str, Any]) -> dict[str, Any]:
    """The manifest's preregistered analysis: the decision rule's verdict values, or the descriptive rule's planned
    count, lambda, homogeneity level and comparisons."""
    if request.rule == DECISION:
        return {
            "claim_level": "C1",
            "alpha": ALPHA,
            "beta": BETA,
            "mean_score": derived["mean_score"],
            "systematic_allowance": derived["systematic_allowance"],
            "classical_bound": derived["classical_bound"],
            "sample_probability": derived["sample_probability"],
            "decision_count": derived["decision_count"],
            "interpretation": "local conformance of the single-chip teleportation circuit family",
        }
    return {
        "rule": DESCRIPTIVE,
        "alpha": ALPHA,
        "planned_accepted": derived["planned_accepted"],
        "lambda": derived["lambda"],
        "homogeneity_alpha": HOMOGENEITY_ALPHA,
        "sample_probability": derived["sample_probability"],
        "comparisons": derived["comparisons"],
        "interpretation": "accepted-event correctness of twelve known-input compiled circuits; the comparisons hold "
        "only under the assumptions each names",
    }


def operator_of(setting: dict[str, Any]) -> np.ndarray:
    entry = setting["operator"]
    return np.asarray(entry["real"], dtype=float) + 1j * np.asarray(entry["imaginary"], dtype=float)


def validate(manifest: dict[str, Any], circuit: dict[str, Any]) -> None:
    """Require the design's request: fields, three-photon input, layout, window mesh and every setting's operator."""
    owner = f"{manifest.get('family')}/{manifest.get('job')}"
    require(manifest.get("job") in JOBS, f"{owner}: job is not registered")
    job = JOBS[manifest["job"]]
    layout = job.request.layout
    rows = schedule(job.request)
    count = len(rows)
    for key, value in (
        ("family", FAMILY),
        ("platforms", [PLATFORM]),
        ("command", "sample_count"),
        ("gate_form", "template"),
        ("iterations", count),
        ("min_detected_photons", MIN_CLICKS),
        ("max_samples", job.samples * count),
        ("max_shots", job.shots * count),
        ("max_duration", MAX_DURATION),
        ("mitigations", []),
        ("output_modes", MODES),
    ):
        require(manifest.get(key) == value, f"{owner}: {key} is {manifest.get(key)!r}, not {value!r}")
    require(manifest["layout"]["chip_modes"] == list(layout), f"{owner}: the layout is not {layout}")
    require(circuit.get("modes") == MODES, f"{owner}: the circuit spans {circuit.get('modes')} modes, not {MODES}")
    require(
        circuit.get("input_state") == source_state(layout), f"{owner}: the input occupation is not the layout's sources"
    )
    require(all(mode in CONNECTED for mode, count_ in enumerate(circuit["input_state"]) if count_), "unconnected input")
    start = min(layout)
    require(
        all(start <= op[1] and op[1] + (op[0] == "BS") < start + LOGICAL for op in circuit["ops"]),
        f"{owner}: a template op leaves the window {start}..{start + LOGICAL - 1}",
    )
    require(iteration_form(manifest) == "template", f"{owner}: the iterations do not form a template job")
    require("compilation_seed" not in manifest, f"{owner}: the manifest names one compilation_seed for all iterations")
    settings = manifest["settings"]
    require(len(settings) == len(rows), f"{owner}: {len(settings)} settings, not {len(rows)}")
    template_experiment(manifest, circuit)
    ordered_map(
        check_setting,
        [
            (owner, index, setting, row, job.request)
            for index, (setting, row) in enumerate(zip(settings, rows, strict=True))
        ],
        min_items=1,
    )


def check_setting(item: tuple[str, int, dict[str, Any], dict[str, Any], Request]) -> None:
    """One input's position, closed-form chip operator, registered ideal and unitarity."""
    owner, index, setting, row, request = item
    layout, seeds = request.layout, request.seeds
    label = f"{owner}/{setting.get('name')}"
    for key, value in row.items():
        require(setting.get(key) == value, f"{label}: {key} is {setting.get(key)!r}, not {value!r} at {index}")
    require(setting.get("observation_index") == index, f"{label}: observation_index is not {index}")
    seed = setting.get("compilation_seed")
    require(
        seed == seeds[index] and type(seed) is int,
        f"{label}: compilation_seed is {seed!r}, not the registered {seeds[index]} at {index}",
    )
    full = operator_of(setting)
    require(full.shape == (MODES, MODES), f"{label}: the operator is {full.shape}, not {MODES}-mode")
    deviation = float(np.max(np.abs(full - chip_operator(logical_unitary(row["label"]), layout))))
    require(deviation <= BODY_TOLERANCE, f"{label}: the operator departs from the closed form by {deviation:.2e}")
    gram = float(np.max(np.abs(full.conj().T @ full - np.eye(MODES))))
    require(gram <= BODY_TOLERANCE, f"{label}: the operator is not unitary ({gram:.2e})")
    require(
        setting.get("ideal") == ideal(row["label"], layout), f"{label}: the registered ideal differs from propagation"
    )


def rejections(manifest: dict[str, Any], circuit: dict[str, Any]) -> list[str]:
    """Mutated requests that validate must refuse: a perturbed unitary, an unconnected source, a photon on a herald,
    an unregistered compilation seed."""
    layout = JOBS[manifest["job"]].request.layout
    reseeded = copy.deepcopy(manifest)
    reseeded["settings"][2]["compilation_seed"] = 0
    perturbed = copy.deepcopy(manifest)
    parameter = sorted(perturbed["settings"][3]["circuit_params"])[0]
    perturbed["settings"][3]["circuit_params"][parameter] += 1e-3
    moved = copy.deepcopy(circuit)
    state = moved["input_state"]
    source = layout[Q0]
    state[source], state[source + 1] = 0, 1
    herald = copy.deepcopy(circuit)
    herald["input_state"][layout[H0]] = 1
    return ordered_map(
        refusal,
        [
            ("perturbed unitary", perturbed, circuit),
            ("shifted source", manifest, moved),
            ("herald photon", manifest, herald),
            ("unregistered compilation seed", reseeded, circuit),
        ],
        min_items=1,
    )


def refusal(item: tuple[str, dict[str, Any], dict[str, Any]]) -> str:
    """The label of a mutated request that validate refuses; a mutation it accepts raises."""
    label, candidate, mesh = item
    try:
        validate(candidate, mesh)
    except (ValueError, PlatformError):
        return label
    raise ValueError(f"validate accepts the {label}")


# ---------------------------------------------------------------- layout choice


def read_perfs(catalogue: Mapping[str, Any]) -> tuple[list[float], list[float], dict[str, float]]:
    """(t_out, dark counts per second, scalar figures) of the qpu:belenos processor record of a catalogue."""
    perfs = catalogue["processors"][PLATFORM]["perfs"]
    figures = {
        "hom": perfs["HOM (%)"] / 100.0,
        "g2": perfs["g2 (%)"] / 100.0,
        "transmittance": perfs["Transmittance (%)"] / 100.0,
        "clock_mhz": perfs["Clock (MHz)"],
    }
    return list(perfs["Transmission per mode (%)"]["t_out"]), list(perfs["Dark counts (detection/s)"]), figures


def window_layout(item: tuple[int, Sequence[float], Sequence[float], Sequence[int]]) -> tuple[Any, ...] | None:
    """The best (imbalance, inversions, start, order) key of the window starting at `start`, or None when a mode of
    the window exceeds DARK_LIMIT or no assignment places the three sources on connected modes."""
    start, t_out, dark, connected = item
    slots = range(start, start + LOGICAL)
    if any(dark[mode] > DARK_LIMIT for mode in slots):
        return None
    best: tuple[Any, ...] | None = None
    for order in itertools.permutations(slots):
        if not all(order[logical] in connected for logical in SOURCES):
            continue
        imbalance = sum(abs(math.log(t_out[order[rail]] / t_out[order[rail + 1]])) for rail in (Q0, A0, B0))
        inversions = sum(order[i] > order[j] for i in range(LOGICAL) for j in range(i + 1, LOGICAL))
        key = (round(imbalance, 2), inversions, start, order)
        if best is None or key < best:
            best = key
    return best


def choose_layout(
    t_out: Sequence[float], dark: Sequence[float], connected: Sequence[int] = CONNECTED
) -> tuple[int, ...]:
    """Chip mode of each logical mode over eight consecutive modes.

    The three source photons need connected inputs and every window mode a dark rate at or below DARK_LIMIT. The
    layout minimizes the summed log ratio of t_out over the rails (q0, q1), (a0, a1), (b0, b1), rounded to two
    decimals; fewer inversions of the logical order, then the lower window and the lexicographically smaller
    assignment break ties. Each window is searched in its own process (window_layout) and the keys, which differ in
    their start, reduce by minimum."""
    keys = ordered_map(
        window_layout,
        [(start, list(t_out), list(dark), list(connected)) for start in range(MODES - LOGICAL + 1)],
        min_items=1,
    )
    found = [key for key in keys if key is not None]
    if not found:
        raise PlatformError("no window of eight modes meets the source and dark-count constraints")
    return tuple(min(found)[3])


# ---------------------------------------------------------------- noise simulation


def perceval_circuit(circuit: Mapping[str, Any], parameters: Mapping[str, float]) -> Any:
    """The template with every parameter fixed, as the platform's BS.Rx and PS components."""
    import perceval as pcvl

    chip = pcvl.Circuit(circuit["modes"])
    for kind, mode, index in circuit["ops"]:
        value = math.pi if index is None else parameters[f"x{index}"]
        chip.add(mode, pcvl.BS.Rx(theta=value) if kind == "BS" else pcvl.PS(value))
    return chip


def photon_distribution(
    setting: Mapping[str, Any], circuit: Mapping[str, Any], hom: float, g2: float
) -> dict[tuple[int, ...], float]:
    """Photon-number distribution over the 24 modes under Perceval's source model (indistinguishability, g2)."""
    import perceval as pcvl

    noise = pcvl.NoiseModel(indistinguishability=hom, g2=g2)
    processor = pcvl.Processor("SLOS", perceval_circuit(circuit, setting["circuit_params"]), noise=noise)
    processor.min_detected_photons_filter(1)
    processor.with_input(pcvl.BasicState(circuit["input_state"]))
    results = processor.probs()["results"]
    return {tuple(int(count) for count in state): float(probability) for state, probability in results.items()}


def detected_clicks(
    photons: Mapping[tuple[int, ...], float], transmission: Sequence[float]
) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution when each photon on mode m is detected with probability transmission[m].

    A mode with n photons clicks with probability 1 - (1 - eta)^n; modes act independently."""
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, probability in photons.items():
        modes = [mode for mode, count in enumerate(occupation) if count]
        click_probability = [1.0 - (1.0 - transmission[mode]) ** occupation[mode] for mode in modes]
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


def detection_efficiency(t_out: Sequence[float], transmittance: float) -> list[float]:
    """Per-mode detection probability: the platform's Transmittance times t_out relative to its largest mode,
    the normalization remote_computer.update_detectors_from_perfs applies."""
    peak = max(t_out)
    return [transmittance * value / peak for value in t_out]


@dataclass(frozen=True)
class Variant:
    """A noise variant: the source figures and the per-mode detection probability."""

    name: str
    hom: float
    g2: float
    transmission: tuple[float, ...]


def variant_scores(item: tuple[Variant, str, dict[str, Any], dict[str, Any], tuple[int, ...]]) -> dict[str, float]:
    """Per-shot accepted probability, accepted share of the three-click samples and conditional fidelity."""
    variant, label, setting, circuit, layout = item
    clicks = detected_clicks(photon_distribution(setting, circuit, variant.hom, variant.g2), variant.transmission)
    sampled = sum(probability for vector, probability in clicks.items() if sum(vector) >= MIN_CLICKS)
    accepted, correct = scored(label, clicks, layout)
    return {
        "sample_probability": sampled,
        "accepted_probability": accepted,
        "accepted_share": accepted / sampled,
        "conditional_fidelity": correct / accepted,
    }


ANCHOR_VARIANTS = ("source only", "source and uniform loss", "anchor per-mode transmission")


def variants(request: Request) -> list[Variant]:
    """The anchor source figures with ideal detection, with the anchor loss, and with per-mode transmissions of the
    anchor read and of the case's fresh read. A case anchored at its own read makes the fresh variants repeat the
    anchor ones, so its allowance holds UNMODELED_ALLOWANCE alone."""
    anchor = json.loads((ROOT / request.anchor_read).read_text(encoding="utf-8"))
    fresh = json.loads((request.directory / READ).read_text(encoding="utf-8"))
    t_anchor, _, figures = read_perfs(anchor)
    t_fresh, _, fresh_figures = read_perfs(fresh)
    hom, g2, loss = figures["hom"], figures["g2"], figures["transmittance"]
    perfect = (1.0,) * MODES
    return [
        Variant("source only", hom, g2, perfect),
        Variant("source and uniform loss", hom, g2, (loss,) * MODES),
        Variant("anchor per-mode transmission", hom, g2, tuple(detection_efficiency(t_anchor, loss))),
        Variant("fresh per-mode transmission", hom, g2, tuple(detection_efficiency(t_fresh, loss))),
        Variant("fresh source figures", fresh_figures["hom"], fresh_figures["g2"], perfect),
    ]


def pooled(scores: Mapping[str, Mapping[str, float]]) -> float:
    """Pooled conditional fidelity at equal samples per input: sum a_j f_j over sum a_j, a_j the accepted share."""
    weights = {label: row["accepted_share"] for label, row in scores.items()}
    return sum(weights[label] * scores[label]["conditional_fidelity"] for label in scores) / sum(weights.values())


def simulation(request: Request) -> dict[str, Any]:
    """Every variant's per-input scores and pooled fidelity; the blocks of a descriptive case repeat each input's
    unitary, so each label is simulated once."""
    built, circuit = request_parts(request)
    settings = [
        setting for index, setting in enumerate(built) if setting["label"] not in {s["label"] for s in built[:index]}
    ]
    out: dict[str, Any] = {}
    for variant in variants(request):
        rows = ordered_map(
            variant_scores, [(variant, s["label"], s, circuit, request.layout) for s in settings], min_items=1
        )
        per_input = {s["label"]: row for s, row in zip(settings, rows, strict=True)}
        out[variant.name] = {"hom": variant.hom, "g2": variant.g2, "inputs": per_input, "pooled": pooled(per_input)}
    return out


def model_benchmark(probability: Mapping[str, float], samples: Mapping[str, int]) -> float:
    """Classical bound when input j has samples_j / probability_j optical attempts."""
    attempts = {label: max(1, round(1e12 * samples[label] / probability[label])) for label in probability}
    return attempts_benchmark(attempts).certified


def derive(sim: Mapping[str, Any]) -> dict[str, Any]:
    """Mean score, systematic allowance, classical bound and sample budget from the simulated variants.

    The mean score is the lowest pooled fidelity over the anchor variants, rounded down to 0.01. The allowance is the
    largest drop of a fresh-read variant below the mean score plus UNMODELED_ALLOWANCE, rounded up to 0.01. The
    service reports nb_shots_used equal to the samples it returns and no count of optical trials, so the attempts of
    an input are modeled as its samples over its three-click probability in the anchor transmission variant; the
    classical bound is attempts_benchmark of those attempts at equal samples, and the analysis takes the larger of it
    and the bound at the reported shots. bernoulli_decision_count refuses a mean score that does not exceed the bound
    plus the allowance, so a case without decision power derives no budget."""
    anchor = [sim[name]["pooled"] for name in ANCHOR_VARIANTS]
    mean_score = math.floor(min(anchor) / SYSTEMATIC_QUANTUM) * SYSTEMATIC_QUANTUM
    fresh = sim["fresh per-mode transmission"]["pooled"]
    drop = max(0.0, mean_score - fresh)
    allowance = math.ceil((drop + UNMODELED_ALLOWANCE) / SYSTEMATIC_QUANTUM - 1e-9) * SYSTEMATIC_QUANTUM
    transmitted = sim["anchor per-mode transmission"]["inputs"]
    probability = {label: float(transmitted[label]["sample_probability"]) for label, *_ in SIX_STATES}
    bound = model_benchmark(probability, {label: 1 for label in probability})
    decision = bernoulli_decision_count(ALPHA, BETA, round(mean_score, 2), bound, round(allowance, 2))
    shares = [transmitted[label]["accepted_share"] for label, *_ in SIX_STATES]
    samples = math.ceil(decision * SAMPLE_MARGIN / (len(shares) * min(shares)) / SAMPLE_QUANTUM) * SAMPLE_QUANTUM
    return {
        "mean_score": round(mean_score, 2),
        "systematic_allowance": round(allowance, 2),
        "classical_bound": round(bound, 9),
        "sample_probability": probability,
        "decision_count": decision,
        "least_accepted_share": min(shares),
        "samples_per_iteration": samples,
    }


def vertex_bound(attempts: dict[str, int]) -> float:
    """attempts_benchmark's certified bound at one attempt profile. qd_classical_benchmark._require_optimal admits an
    inaccurate optimum and _free_postselection_bound certifies the bound from the projected witness, so cvxpy's
    inaccuracy warning on an extreme profile carries no defect and is silenced here alone."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Solution may be inaccurate", category=UserWarning)
        return attempts_benchmark(attempts).certified


def box_bound(probability: Mapping[str, float], ratio: float) -> float:
    """The largest classical bound over attempt profiles whose every input lies within `ratio` of samples over its
    modeled three-click probability.

    For a fixed accepted instrument the pooled score is a linear-fractional function of the attempts, and the maximum
    over instruments of such functions is quasi-convex, so its maximum over the box lies at one of the 64 vertices;
    each vertex is solved in its own process."""
    labels = [label for label, *_ in SIX_STATES]
    vertices = [
        {label: max(1, round(1e12 * factor / probability[label])) for label, factor in zip(labels, signs, strict=True)}
        for signs in itertools.product((1.0 / ratio, ratio), repeat=len(labels))
    ]
    return round(max(ordered_map(vertex_bound, vertices, min_items=1)), 9)


def derive_descriptive(sim: Mapping[str, Any], request: Request) -> dict[str, Any]:
    """The descriptive rule's planned values: the anchor transmission variant's accepted shares and three-click
    probabilities, the planned accepted count n* at DESCRIPTIVE_SAMPLES per iteration, lambda = sqrt(8 ln(1/alpha)
    / n*), the forecast pooled correctness and lower bound, and the two comparisons with their bounds."""
    transmitted = sim["anchor per-mode transmission"]["inputs"]
    labels = [label for label, *_ in SIX_STATES]
    probability = {label: float(transmitted[label]["sample_probability"]) for label in labels}
    shares = {label: float(transmitted[label]["accepted_share"]) for label in labels}
    planned = math.floor(sum(request.blocks * DESCRIPTIVE_SAMPLES * shares[label] for label in labels))
    lam = math.sqrt(8.0 * math.log(1.0 / ALPHA) / planned)
    forecast = float(sim["anchor per-mode transmission"]["pooled"])
    lower = forecast - lam / 8.0 - math.log(1.0 / ALPHA) / (lam * planned)
    box = box_bound(probability, BOX_RATIO)
    comparisons: list[dict[str, Any]] = [
        {
            "name": "two-copy",
            "bound": TWO_COPY_BOUND,
            "assumptions": list(TWO_COPY_ASSUMPTIONS),
            "forecast_margin": lower - TWO_COPY_BOUND,
        },
        {
            "name": "attempt-box",
            "bound": box,
            "ratio": BOX_RATIO,
            "assumptions": list(BOX_ASSUMPTIONS),
            "forecast_margin": lower - box,
        },
    ]
    return {
        "rule": DESCRIPTIVE,
        "blocks": request.blocks,
        "samples_per_iteration": DESCRIPTIVE_SAMPLES,
        "sample_probability": probability,
        "accepted_share": shares,
        "least_accepted_share": min(shares.values()),
        "planned_accepted": planned,
        "lambda": lam,
        "forecast_fidelity": forecast,
        "forecast_lower_bound": lower,
        "comparisons": comparisons,
    }


def expected_seconds(derived: Mapping[str, Any], samples: int, clock_mhz: float, blocks: int = 1) -> float:
    """The written case's seconds: COMPILE_SECONDS per iteration plus each iteration's samples over the clock rate
    times its input's modeled three-click probability per pulse, times SECONDS_MARGIN, rounded up to SECONDS_QUANTUM.

    Job-00's derivation gives 120 s. The model is unverified on the chip: job-00 ran 292 s in the degraded state, in
    which every iteration ran to its max_shots."""
    probability = derived["sample_probability"]
    acquisition = blocks * sum(samples / (clock_mhz * 1e6 * probability[label]) for label, *_ in SIX_STATES)
    modeled = COMPILE_SECONDS * len(SIX_STATES) * blocks + acquisition
    return float(math.ceil(modeled * SECONDS_MARGIN / SECONDS_QUANTUM) * SECONDS_QUANTUM)


def retained_derivation(name: str) -> dict[str, Any]:
    """The derivation retained as noise-model.json, which fixes the manifest's preregistered values."""
    path = CASES / name / "noise-model.json"
    return dict(json.loads(path.read_text(encoding="utf-8"))["derived"])


@contextmanager
def anchor_perfs(read: str = ANCHOR_READ) -> Iterator[None]:
    """Serve the performance figures of the platform read at repository path `read` wherever Perceval or qd_platform
    reads the processor's perfs.

    The live record still supplies the architecture, constraints and commands; only `perfs` changes, so payload and
    plan evaluate the request in the anchor state, not the live one."""
    import qd_platform
    from perceval import QuandelaCommunicationLayer

    anchor = json.loads((ROOT / read).read_text(encoding="utf-8"))["processors"][PLATFORM]["perfs"]
    live_get = qd_platform.get
    live_perfs = QuandelaCommunicationLayer.get_performances

    def get(route: str, auth: bool = True) -> Any:
        answer = live_get(route, auth)
        if route == qd_platform.platform_route(PLATFORM) and isinstance(answer, dict):
            return {**answer, "perfs": copy.deepcopy(anchor)}
        return answer

    qd_platform.get = get
    QuandelaCommunicationLayer.get_performances = lambda self: copy.deepcopy(anchor)
    try:
        yield
    finally:
        qd_platform.get = live_get
        QuandelaCommunicationLayer.get_performances = live_perfs


def shot_estimate(request: Request, case_dir: Path) -> dict[str, Any]:
    """Perceval's estimate_required_shots for each input's max_samples under the anchor read's performance figures.

    The platform's live processor record supplies the architecture and constraints, and the anchor read's perfs
    replace the live ones, so the estimate is the one plan would compute in the anchor state. The recorder keeps every
    estimate payload computes, and an estimate above the case's max_shots stops payload only after it is recorded, so
    the max_shots of the request staged in `case_dir` does not enter the estimate."""
    from perceval import RemoteComputer

    estimates: list[tuple[int, int | None]] = []
    original = RemoteComputer.estimate_required_shots

    def recorded(self: Any, computation: Any, nsamples: int, param_values: dict[str, float] | None = None) -> Any:
        value = original(self, computation, nsamples, param_values)
        estimates.append((nsamples, value))
        return value

    RemoteComputer.estimate_required_shots = recorded
    manifest, circuit, _ = load_case(case_dir)
    try:
        with anchor_perfs(request.anchor_read):
            payload(case_dir, manifest, circuit, PLATFORM)
    except PlatformError:
        pass
    finally:
        RemoteComputer.estimate_required_shots = original
    require(len(estimates) == len(manifest["settings"]), f"{len(estimates)} estimates were recorded")
    require(all(value is not None for _, value in estimates), "Perceval estimates no sample of interest")
    largest = max(value for _, value in estimates if value is not None)
    return {
        "schema": "qd-teleportation-shot-estimate-v1",
        "basis": "estimate_required_shots under the perfs of " + request.anchor_read,
        "inputs": {s["label"]: value for s, (_, value) in zip(manifest["settings"], estimates, strict=True)},
        "samples": estimates[0][0],
        "largest": largest,
        "shots_per_iteration": math.ceil(largest * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM,
    }


def justify(request: Request) -> dict[str, Any]:
    """The simulated variants and the values derived from them; check compares them with noise-model.json."""
    sim = simulation(request)
    derived = derive(sim) if request.rule == DECISION else derive_descriptive(sim, request)
    return {"schema": "qd-teleportation-noise-model-v1", "variants": sim, "derived": derived}


# ---------------------------------------------------------------- results


def event_vector(key: str) -> tuple[int, ...]:
    """The 24-mode occupation of a results.json count key such as "0,0,1,..."."""
    try:
        vector = tuple(int(part) for part in key.split(","))
    except ValueError:
        raise ProtocolError(f"count key {key[:60]!r} is not a comma-separated occupation") from None
    if len(vector) != MODES or min(vector) < 0:
        raise ProtocolError(f"count key {key[:60]!r} is not a {MODES}-mode occupation")
    return vector


REJECTIONS = ("excess", "outside", "herald", "receiver", "pattern")
# The entry kinds qd_platform.result_summary writes for an iteration of a partial job that carries no counts.
UNCOUNTED = ("missing", "malformed", "error")


def tally(counts: Mapping[str, int], layout: Sequence[int]) -> tuple[dict[tuple[str, int], int], dict[str, int]]:
    """Accepted counts by (Bell pattern, raw bit) and rejected counts by reason under the case's layout.

    The job's three-click filter excludes events below three clicks, so one in the counts refuses the record."""
    accepted: dict[tuple[str, int], int] = {}
    rejected = dict.fromkeys(REJECTIONS, 0)
    for key, count in counts.items():
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ProtocolError(f"count {count!r} of {key[:60]!r} is not a nonnegative integer")
        outcome, pattern, raw = classify(event_vector(key), layout)
        if outcome == "below":
            raise ProtocolError(f"event {key} carries fewer than {MIN_CLICKS} clicks, below the job's filter")
        if outcome == "accepted" and pattern is not None and raw is not None:
            accepted[(pattern, raw)] = accepted.get((pattern, raw), 0) + count
        else:
            rejected[outcome] += count
    return accepted, rejected


def hoeffding_radius(alpha: float, trials: int) -> float:
    """One-sided Hoeffding radius sqrt(ln(1/alpha) / (2 n)) of a mean of n independent {0, 1} outcomes."""
    if not 0.0 < alpha < 1.0 or trials <= 0:
        raise ProtocolError(f"radius needs alpha in (0, 1) and positive trials, not {alpha}, {trials}")
    return math.sqrt(math.log(1.0 / alpha) / (2.0 * trials))


def analyze_results(
    manifest: Mapping[str, Any], results: Mapping[str, Any], table: Mapping[str, tuple[int, int]] | None = None
) -> dict[str, Any]:
    """Score a collected results.json against its manifest.

    Each result iteration binds to the setting whose circuit_params it carries, and its events classify under the
    manifest's layout (layout.chip_modes). The joint histogram keyed (input,
    basis, pattern, raw bit) scores per input and pooled; joint_teleportation_scores, which needs a matching-basis
    trial for each input, cross-checks the pooled value when every input has an accepted event. An input without one
    keeps its rejection counts, reports a null conditional fidelity with a reason, and drops out of the pooled
    statistic; the verdict is then inconclusive, because the preregistered rule pools all six inputs. The frame table
    `table` must equal the propagated one when given. An iteration ended by its sample budget reports shots equal to
    its samples and one ended by its max_shots reports that budget, neither a count of optical trials, so the
    classical bound is the larger of attempts_benchmark at the reported shots (result_fields.nb_shots_used) and at
    the modeled attempts, and `beats-classical` must clear it; `at-or-below-classical` must fall below the smaller of
    the two, so neither verdict rests on the candidate profile that favors it. A partial result (an error or canceled
    job) scores its counted iterations descriptively, lists the uncounted entry kinds and the inputs left without
    counts, and is inconclusive, since a stop the service chose may depend on the outcomes. A descriptive case
    goes to analyze_descriptive."""
    if manifest["preregistered"].get("rule") == DESCRIPTIVE:
        return analyze_descriptive(manifest, results, table)
    frame_table = frames()
    if table is not None and {k: tuple(v) for k, v in table.items()} != frame_table:
        raise ProtocolError(f"the frame table {dict(table)} differs from the propagated {frame_table}")
    settings = manifest["settings"]
    layout = tuple(manifest["layout"]["chip_modes"])
    partial = results.get("partial") is True
    iterations = results.get("iterations")
    if iterations is None and partial:
        iterations = []
    if not isinstance(iterations, list) or len(iterations) > len(settings):
        raise ProtocolError(f"results hold {None if iterations is None else len(iterations)} iterations")
    if not partial and len(iterations) != len(settings):
        raise ProtocolError(f"results hold {len(iterations)} iterations, not {len(settings)}")
    histogram: dict[tuple[str, str, str, int], int] = {}
    rows: dict[str, dict[str, Any]] = {}
    attempts: dict[str, int] = {}
    uncounted: list[str] = []
    for entry in iterations:
        if "counts" not in entry:
            if not partial:
                raise ProtocolError("an iteration carries no counts")
            uncounted.append(next((kind for kind in UNCOUNTED if kind in entry), "uncounted"))
            continue
        setting = settings[bound_setting(settings, entry)]
        if setting["label"] in rows:
            raise ProtocolError("an iteration does not bind to exactly one unused setting by its circuit_params")
        accepted, rejected = tally(entry["counts"], layout)
        shots = entry.get("result_fields", {}).get("nb_shots_used")
        samples = sum(entry["counts"].values())
        if not isinstance(shots, int) or isinstance(shots, bool) or shots < samples:
            raise ProtocolError(f"{setting['label']}: nb_shots_used {shots!r} is below its {samples} samples")
        for (pattern, raw), count in accepted.items():
            histogram[(setting["label"], setting["basis"], pattern, raw)] = count
        total = sum(accepted.values())
        attempts[setting["label"]] = shots
        rows[setting["label"]] = {
            "basis": setting["basis"],
            "shots": shots,
            "samples": samples,
            "accepted": total,
            "accepted_per_sample": total / samples if samples else None,
            "accepted_per_shot": total / shots if shots else None,
            "rejected": rejected,
        }
    successes = dict.fromkeys(rows, 0)
    for (label, basis, pattern, raw), count in histogram.items():
        x, z = frame_table[pattern]
        successes[label] += count if decode_bit(basis, raw, x, z) == expected_bit(label) else 0
    silent = [label for label, row in rows.items() if row["accepted"] == 0]
    absent = [setting["label"] for setting in settings if setting["label"] not in rows]
    total_accepted = sum(row["accepted"] for row in rows.values())
    pooled_fidelity = sum(successes.values()) / total_accepted if total_accepted else None
    if not silent and not absent:
        scores = joint_teleportation_scores(histogram, frame_table, attempts)
        shared = float(scores["pooled_conditional_fidelity"])  # type: ignore[arg-type]
        require(
            pooled_fidelity is not None and math.isclose(shared, pooled_fidelity, abs_tol=1e-12),
            "the pooled fidelity differs from joint_teleportation_scores",
        )
    preregistered = manifest["preregistered"]
    radius = hoeffding_radius(preregistered["alpha"], total_accepted) if total_accepted else None
    sample_counts = {label: row["samples"] for label, row in rows.items()}
    # attempts_benchmark needs a positive attempt count for every input, so an iteration that returned no shot
    # leaves the classical bound, and with it the verdict, unavailable.
    empty = sorted(label for label, row in rows.items() if row["shots"] == 0 or row["samples"] == 0)
    bound_reported = None if empty or absent else attempts_benchmark(attempts).certified
    bound_modeled = None if empty or absent else model_benchmark(preregistered["sample_probability"], sample_counts)
    bound = None if bound_reported is None or bound_modeled is None else max(bound_reported, bound_modeled)
    allowance = preregistered["systematic_allowance"]
    lower = None if pooled_fidelity is None or radius is None else pooled_fidelity - radius
    if partial or absent or silent or bound is None or pooled_fidelity is None or radius is None or lower is None:
        verdict = "inconclusive"
    elif lower - allowance > bound:
        verdict = "beats-classical"
    elif (
        bound_reported is not None
        and bound_modeled is not None
        and (pooled_fidelity + radius < min(bound_reported, bound_modeled))
    ):
        verdict = "at-or-below-classical"
    else:
        verdict = "inconclusive"
    for label, row in rows.items():
        row["correct"] = successes[label]
        if row["accepted"]:
            row["conditional_fidelity"] = successes[label] / row["accepted"]
        else:
            row["conditional_fidelity"] = None
            row["conditional_fidelity_reason"] = "no accepted event among the input's samples"
    return {
        "schema": "qd-teleportation-analysis-v1",
        "claim_level": preregistered["claim_level"],
        "inputs": rows,
        "partial": partial,
        "inputs_without_counts": absent,
        "uncounted_iterations": uncounted,
        "inputs_without_accepted": silent,
        "success_rate_per_reported_shot": {label: row["accepted_per_shot"] for label, row in rows.items()},
        "pooled": {
            "accepted": total_accepted,
            "inputs_pooled": len(rows) - len(silent),
            "fidelity": pooled_fidelity,
            "alpha": preregistered["alpha"],
            "radius": radius,
            "lower_bound": lower,
        },
        "benchmark": {
            "reported_attempts": attempts,
            "bound_at_reported_attempts": bound_reported,
            "modeled_attempts_basis": "samples over the preregistered three-click probability of each input",
            "bound_at_modeled_attempts": bound_modeled,
            "classical_bound": bound,
        },
        "systematic_allowance": allowance,
        "margin": None if lower is None or bound is None else lower - allowance - bound,
        "verdict": verdict,
        "verdict_reason": (
            "the job ended partial and these inputs returned no counted iteration: " + ", ".join(absent)
            if absent
            else "these iterations returned no shot or no sample, so no classical bound is defined: " + ", ".join(empty)
            if empty
            else "the preregistered rule pools all six inputs, and these have no accepted event: " + ", ".join(silent)
            if silent
            else "the job ended partial, so its counts are descriptive: a stop the service chose may depend on them"
            if partial
            else "the preregistered decision rule over all six inputs"
        ),
        "histogram": [[*key, count] for key, count in sorted(histogram.items())],
    }


def parameters_equal(left: Mapping[str, float], right: Mapping[str, float]) -> bool:
    return sorted(left) == sorted(right) and all(math.isclose(left[k], right[k], abs_tol=1e-12) for k in left)


def bound_setting(settings: Sequence[Mapping[str, Any]], entry: Mapping[str, Any]) -> int:
    """The index of the one setting a result iteration binds to: equal circuit_params, and the same compilation_seed
    whenever the iteration carries one, since the blocks of a descriptive case repeat each input's parameters."""
    iteration = entry.get("iteration", {})
    values, seed = iteration.get("circuit_params"), iteration.get("compilation_seed")
    matches = [
        index
        for index, setting in enumerate(settings)
        if values is not None
        and parameters_equal(values, setting["circuit_params"])
        and (seed is None or seed == setting.get("compilation_seed"))
    ]
    if len(matches) != 1:
        raise ProtocolError("an iteration does not bind to exactly one setting by its circuit_params and seed")
    return matches[0]


def anytime_lower_bound(correct: int, accepted: int, lam: float, alpha: float) -> float:
    """The lower confidence bound F_hat - lambda / 8 - ln(1/alpha) / (lambda n) on the average conditional correctness
    of n accepted events. prod_j exp(lambda (X_j - mu_j) - lambda^2 / 8) is a nonnegative supermartingale for any
    conditional means mu_j (Hoeffding's lemma), so Ville's inequality bounds it at every stopping time."""
    return correct / accepted - lam / 8.0 - math.log(1.0 / alpha) / (lam * accepted)


def homogeneity(table: Sequence[Sequence[int]], alpha: float) -> dict[str, Any]:
    """A chi-square test of block against outcome category for one input; empty categories are dropped, and a block
    without events leaves the test undefined."""
    from scipy.stats import chi2_contingency

    columns = [index for index in range(len(table[0])) if any(row[index] for row in table)]
    reduced = [[row[index] for index in columns] for row in table]
    if len(columns) < 2 or any(sum(row) == 0 for row in reduced):
        return {"status": "untestable", "categories": len(columns)}
    result = chi2_contingency(reduced, correction=False)
    p_value = float(result.pvalue)
    return {
        "status": "differ" if p_value < alpha else "consistent",
        "statistic": float(result.statistic),
        "dof": int(result.dof),
        "p_value": p_value,
    }


def break_even_ratio(probability: Mapping[str, float], lower: float) -> dict[str, Any]:
    """The largest attempt-box ratio r at which the lower bound still exceeds box_bound(r), by bisection to
    BREAK_EVEN_TOLERANCE on [1, BREAK_EVEN_CEILING]."""
    if box_bound(probability, 1.0) >= lower:
        return {"status": "below-one", "ratio": None}
    if box_bound(probability, BREAK_EVEN_CEILING) < lower:
        return {"status": "at-least-ceiling", "ratio": BREAK_EVEN_CEILING}
    low, high = 1.0, BREAK_EVEN_CEILING
    while high - low > BREAK_EVEN_TOLERANCE:
        middle = (low + high) / 2.0
        low, high = (middle, high) if box_bound(probability, middle) < lower else (low, middle)
    return {"status": "found", "ratio": low}


def analyze_descriptive(
    manifest: Mapping[str, Any], results: Mapping[str, Any], table: Mapping[str, tuple[int, int]] | None = None
) -> dict[str, Any]:
    """Score a descriptive case: per-iteration counts, the pooled accepted-event correctness with its anytime-valid
    lower bound, the block homogeneity veto and the two model-conditional comparisons.

    Each result iteration binds to its setting by circuit_params and compilation_seed. No provider field is read as
    optical attempts. A partial job, an input without counts or an empty pooled set keeps every count descriptive and
    evaluates no comparison; a blocks-differ flag vetoes both."""
    frame_table = frames()
    if table is not None and {k: tuple(v) for k, v in table.items()} != frame_table:
        raise ProtocolError(f"the frame table {dict(table)} differs from the propagated {frame_table}")
    settings = manifest["settings"]
    preregistered = manifest["preregistered"]
    layout = tuple(manifest["layout"]["chip_modes"])
    partial = results.get("partial") is True
    iterations = results.get("iterations")
    if iterations is None and partial:
        iterations = []
    if not isinstance(iterations, list) or len(iterations) > len(settings):
        raise ProtocolError(f"results hold {None if iterations is None else len(iterations)} iterations")
    if not partial and len(iterations) != len(settings):
        raise ProtocolError(f"results hold {len(iterations)} iterations, not {len(settings)}")
    rows: dict[int, dict[str, Any]] = {}
    uncounted: list[str] = []
    for entry in iterations:
        if "counts" not in entry:
            if not partial:
                raise ProtocolError("an iteration carries no counts")
            uncounted.append(next((kind for kind in UNCOUNTED if kind in entry), "uncounted"))
            continue
        index = bound_setting(settings, entry)
        if index in rows:
            raise ProtocolError("two result iterations bind to one setting")
        setting = settings[index]
        accepted, rejected = tally(entry["counts"], layout)
        correct = 0
        for (pattern, raw), count in accepted.items():
            x, z = frame_table[pattern]
            correct += count if decode_bit(setting["basis"], raw, x, z) == expected_bit(setting["label"]) else 0
        samples = sum(entry["counts"].values())
        total = sum(accepted.values())
        fields = entry.get("result_fields", {})
        rows[index] = {
            "label": setting["label"],
            "block": setting["block"],
            "basis": setting["basis"],
            "compilation_seed": setting["compilation_seed"],
            "samples": samples,
            "accepted": total,
            "correct": correct,
            "wrong": total - correct,
            "rejected": rejected,
            "accepted_per_sample": total / samples if samples else None,
            "nb_shots_used": fields.get("nb_shots_used"),
            "physical_perf": fields.get("physical_perf"),
        }
    absent = [f"{settings[i]['label']}/{settings[i]['block']}" for i in range(len(settings)) if i not in rows]
    accepted_total = sum(row["accepted"] for row in rows.values())
    correct_total = sum(row["correct"] for row in rows.values())
    alpha, lam = preregistered["alpha"], preregistered["lambda"]
    fidelity = correct_total / accepted_total if accepted_total else None
    lower = anytime_lower_bound(correct_total, accepted_total, lam, alpha) if accepted_total else None
    tests: dict[str, Any] = {}
    level = preregistered["homogeneity_alpha"] / len(SIX_STATES)
    for label, *_ in SIX_STATES:
        blocks = {row["block"]: row for row in rows.values() if row["label"] == label}
        if set(blocks) != {"A", "B"}:
            tests[label] = {"status": "untestable", "reason": "a block returned no counted iteration"}
            continue
        counts = [
            [blocks[name]["correct"], blocks[name]["wrong"], *(blocks[name]["rejected"][r] for r in REJECTIONS)]
            for name in ("A", "B")
        ]
        tests[label] = homogeneity(counts, level)
    differ = sorted(label for label, test in tests.items() if test["status"] == "differ")
    comparisons = []
    for comparison in preregistered["comparisons"]:
        record = {key: value for key, value in comparison.items() if key != "forecast_margin"}
        if partial or absent or lower is None:
            record["label"], record["margin"] = "not-evaluated", None
        elif differ:
            record["label"], record["margin"] = "vetoed-blocks-differ", lower - comparison["bound"]
        else:
            record["margin"] = lower - comparison["bound"]
            record["label"] = "exceeds-under-assumptions" if record["margin"] > 0 else "not-shown"
        comparisons.append(record)
    evaluated = not (partial or absent or lower is None or differ)
    break_even = (
        break_even_ratio(preregistered["sample_probability"], lower)
        if evaluated and lower is not None
        else {"status": "not-evaluated", "ratio": None}
    )
    return {
        "schema": "qd-teleportation-analysis-v2",
        "rule": DESCRIPTIVE,
        "iterations": [rows[index] for index in sorted(rows)],
        "partial": partial,
        "iterations_without_counts": absent,
        "uncounted_iterations": uncounted,
        "pooled": {
            "accepted": accepted_total,
            "correct": correct_total,
            "fidelity": fidelity,
            "alpha": alpha,
            "lambda": lam,
            "lower_bound": lower,
        },
        "homogeneity": {"alpha_per_input": level, "tests": tests, "differ": differ},
        "comparisons": comparisons,
        "break_even_ratio": break_even,
        "status": (
            "partial job: descriptive counts only"
            if partial
            else "iterations without counts: " + ", ".join(absent)
            if absent
            else "no accepted event"
            if lower is None
            else "blocks differ: " + ", ".join(differ)
            if differ
            else "complete"
        ),
    }


def simulated_iteration(item: tuple[dict[str, Any], dict[str, Any], Variant, int]) -> dict[str, Any]:
    """One results.json iteration: the setting's expected counts under the variant, by largest remainder."""
    setting, circuit, variant, samples = item
    clicks = detected_clicks(photon_distribution(setting, circuit, variant.hom, variant.g2), variant.transmission)
    sampled = {vector: p for vector, p in clicks.items() if sum(vector) >= MIN_CLICKS}
    total = sum(sampled.values())
    exact = {vector: samples * p / total for vector, p in sampled.items()}
    counts = {vector: math.floor(value) for vector, value in exact.items()}
    shortfall = samples - sum(counts.values())
    for vector in sorted(exact, key=lambda v: (counts[v] - exact[v], v))[:shortfall]:
        counts[vector] += 1
    return {
        "iteration": {"circuit_params": setting["circuit_params"], "compilation_seed": setting["compilation_seed"]},
        "counts": {",".join(str(c) for c in vector): n for vector, n in sorted(counts.items()) if n},
        "samples": samples,
        "result_fields": {"nb_shots_used": samples},
    }


def simulated_results(manifest: Mapping[str, Any], circuit: Mapping[str, Any], variant: Variant) -> dict[str, Any]:
    """A results.json of the expected counts of a noise variant, in the form qd_platform.collect retains.

    Each iteration holds its max_samples as expected counts by largest remainder, so the file is deterministic;
    nb_shots_used equals the samples, as in every retained qpu:belenos result."""
    samples = manifest["max_samples"] // manifest["iterations"]
    items = [(dict(setting), dict(circuit), variant, samples) for setting in manifest["settings"]]
    iterations = ordered_map(simulated_iteration, items)
    return {"schema": "qd-collection-v1", "partial": False, "iterations": iterations}


# ---------------------------------------------------------------- commands


def check() -> int:
    """Rebuild each job in memory, require the retained bytes, validate them and their derivation and body.

    A job's layout must be the one its own platform read selects, and its budgets those its retained derivation and
    shot estimate give."""
    for job in JOBS.values():
        out = CASES / job.name
        require((out / "cases.json").is_file(), f"{job.name} is registered, and its case directory has no cases.json")
        built = documents(job)
        require(documents(job) == built, f"{job.name}: a second build differs from the first")
        retained = {name: (out / name).read_bytes() for name in built}
        label = (out / "cases.json").relative_to(ROOT)
        close(json.loads(built["cases.json"]), json.loads(retained["cases.json"]), str(label))
        require(retained["circuit.json"] == built["circuit.json"], f"{out.relative_to(ROOT)}/circuit.json differs")
        manifest, circuit = json.loads(retained["cases.json"]), json.loads(retained["circuit.json"])
        validate(manifest, circuit)
        refused = rejections(manifest, circuit)
        t_out, dark, _ = read_perfs(json.loads((out / READ).read_text(encoding="utf-8")))
        require(
            choose_layout(t_out, dark) == job.request.layout, f"{job.name}: the retained read selects another layout"
        )
        derived = retained_derivation(job.name)
        close(
            justify(job.request),
            json.loads((out / "noise-model.json").read_text(encoding="utf-8")),
            f"{job.name}/noise-model.json",
        )
        require(
            derived["samples_per_iteration"] <= job.samples,
            f"{job.name}: {job.samples} samples per iteration are below the derived {derived['samples_per_iteration']}",
        )
        estimate = json.loads((out / ESTIMATE).read_text(encoding="utf-8"))
        require(
            estimate["samples"] == job.samples and estimate["shots_per_iteration"] == job.shots,
            f"{job.name}: max_shots {job.shots} differs from the retained estimate's {estimate['shots_per_iteration']}",
        )
        require(
            job.credit_ceiling >= PER_JOB_CREDITS + job.shots * PRICE_PER_SHOT - 1e-9,
            f"{job.name}: the credit ceiling {job.credit_ceiling} is below the per-job price plus max_shots",
        )
        clock = read_perfs(json.loads((ROOT / job.request.anchor_read).read_text(encoding="utf-8")))[2]["clock_mhz"]
        seconds = expected_seconds(derived, job.samples, clock, job.request.blocks)
        require(
            job.expected_seconds == seconds and seconds <= MAX_DURATION,
            f"{job.name}: expected {job.expected_seconds} s, derived {seconds:g} s against max_duration {MAX_DURATION}",
        )
        print(
            f"teleportation rehearsal {job.name}: {len(manifest['settings'])} inputs validated, cases.json "
            f"{sha256_bytes(retained['cases.json'])}; refused {', '.join(refused)}"
        )
    return 0


def build(job: Job) -> int:
    """Write the job's request bytes into its case directory; retained bytes are never rewritten."""
    built = documents(job)
    validate(json.loads(built["cases.json"]), json.loads(built["circuit.json"]))
    out = CASES / job.name
    out.mkdir(parents=True, exist_ok=True)
    for name, content in built.items():
        path = out / name
        require(not path.exists() or path.read_bytes() == content, f"{path.relative_to(ROOT)} differs from the rebuild")
        if not path.exists():
            path.write_bytes(content)
    print(f"teleportation rehearsal: {out.relative_to(ROOT)} cases.json {sha256_bytes(built['cases.json'])}")
    return 0


def validate_body(body: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Require the job body to carry the frozen request: name, platform, policy, budgets and six entries."""
    from perceval.serialization import deserialize

    job = JOBS[manifest["job"]]
    seeds = job.request.seeds
    for key, value in (
        ("job_name", f"{manifest['family']}/{manifest['job']}"),
        ("platform_name", PLATFORM),
        ("max_duration", MAX_DURATION),
    ):
        require(body.get(key) == value, f"job body: {key} is {body.get(key)!r}, not {value!r}")
    content = body["payload"]
    for key, value in (("command", "sample_count"), ("max_samples", job.samples), ("max_shots", job.shots)):
        require(content.get(key) == value, f"job body: payload {key} is {content.get(key)!r}, not {value!r}")
    require(body_mitigations(body) == [], "job body: the payload does not carry the empty mitigation list")
    computation = deserialize(content["computation"])
    iterations = computation.iterations
    require(len(iterations) == len(manifest["settings"]), f"job body: {len(iterations)} entries")
    experiment = computation.experiment
    require(list(experiment.input_state) == source_state(job.request.layout), "job body: the input occupation differs")
    require(experiment.min_photons_filter == MIN_CLICKS, "job body: the photon filter differs")
    circuit = experiment.unitary_circuit()
    parameters = circuit.get_parameters()
    for index, (entry, setting) in enumerate(zip(iterations, manifest["settings"], strict=True)):
        require(entry.get("circuit_params") == setting["circuit_params"], f"job body entry {index}: params differ")
        require(
            entry.get("compilation_seed") == seeds[index],
            f"job body entry {index}: compilation_seed is {entry.get('compilation_seed')!r}, not {seeds[index]}",
        )
        require(
            entry.get("max_samples") == job.samples and entry.get("max_shots") == job.shots, f"entry {index} budgets"
        )
        for parameter in parameters:
            parameter.set_value(entry["circuit_params"][parameter.name])
        unitary = np.asarray(circuit.compute_unitary(), dtype=np.complex128)
        deviation = float(np.max(np.abs(unitary - operator_of(setting))))
        require(deviation <= BODY_TOLERANCE, f"job body entry {index}: the unitary departs by {deviation:.2e}")


def freeze_body(job: Job, anchor: bool) -> int:
    """Build the job body against the live platform record without sending it, and retain it.

    With `anchor` the live processor record's performance figures give way to the anchor read's, the state in which
    payload's shot estimate admits the request; the body does not depend on them."""
    out = CASES / job.name
    manifest, circuit, cases_sha256 = load_case(out)
    validate(manifest, circuit)
    with perfs_gate(job, anchor):
        built = payload(out, manifest, circuit, PLATFORM)
    validate_body(built["body"], manifest)
    body_bytes = (json.dumps(built["body"], indent=1, sort_keys=True) + "\n").encode()
    record = {
        "platform": PLATFORM,
        "cases_sha256": cases_sha256,
        "job_body_sha256": sha256_bytes(body_bytes),
        "estimated_shots": built["estimated_shots"],
        "payload_version_basis": built["payload_version_basis"],
        "versions": built["versions"],
        "perfs_basis": job.request.anchor_read if anchor else "live processor record",
        "built_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "sent": False,
    }
    for name in ("job-body.json", "body-build.json"):
        require(not (out / name).exists(), f"{(out / name).relative_to(ROOT)} exists; the retained body is frozen")
    (out / "job-body.json").write_bytes(body_bytes)
    (out / "body-build.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(
        f"teleportation rehearsal {job.name}: job-body.json {record['job_body_sha256']}, "
        f"{built['estimated_shots']} shots"
    )
    return 0


def perfs_gate(job: Job, anchor: bool) -> Any:
    """The anchor read's performance figures with `anchor`, else the live ones; a case anchored at its own read
    refuses `anchor`, since its preregistration already describes that read and only the live gate applies."""
    if not anchor:
        return nullcontext()
    require(not job.request.own_anchor, f"{job.name} is anchored at its own platform read; the live gate applies")
    return anchor_perfs(job.request.anchor_read)


def live_model(request: Request | None = None) -> dict[str, Any]:
    """The pooled fidelity the noise model gives at the platform's live performance figures, read without a token
    write: the source figures, uniform loss and per-mode transmission of the live processor record. The case is
    job-00 unless named."""
    from qd_platform import get, platform_route, scrub

    return model_at(scrub(get(platform_route(PLATFORM)).get("perfs") or {}), request)


def model_at(perfs: Mapping[str, Any], request: Request | None = None) -> dict[str, Any]:
    """The noise model's pooled fidelity at one processor record's perfs object, against the justified mean score of
    the case `request` (job-00 unless named, the case scripts/qd_record_watch.py gates on)."""
    request = request or REQUESTS["job-00"]
    figures = {
        "hom": perfs["HOM (%)"] / 100.0,
        "g2": perfs["g2 (%)"] / 100.0,
        "transmittance": perfs["Transmittance (%)"] / 100.0,
    }
    transmission = tuple(detection_efficiency(perfs["Transmission per mode (%)"]["t_out"], figures["transmittance"]))
    variant = Variant("live read", figures["hom"], figures["g2"], transmission)
    settings, circuit = request_parts(request)
    rows = ordered_map(
        variant_scores, [(variant, s["label"], s, circuit, request.layout) for s in settings], min_items=1
    )
    pooled_fidelity = pooled({s["label"]: row for s, row in zip(settings, rows, strict=True)})
    record: dict[str, Any] = {"figures": figures, "pooled_fidelity": pooled_fidelity}
    if request.rule == DECISION:
        mean_score = retained_derivation(request.name)["mean_score"]
        record.update(mean_score=mean_score, inside_justified_range=pooled_fidelity >= mean_score)
        return record
    from qd_record_watch import digest

    prepared = json.loads((ROOT / request.anchor_read).read_text(encoding="utf-8"))["processors"][PLATFORM]["perfs"]
    record.update(perfs_sha256=digest(perfs), prepared_perfs_sha256=digest(prepared))
    record["inside_justified_range"] = record["perfs_sha256"] == record["prepared_perfs_sha256"]
    return record


def admission_failure(model: Mapping[str, Any]) -> str:
    """Why a model record refuses admission: the decision rule's pooled fidelity below its mean score, or a live
    performance record that differs from a descriptive case's prepared read."""
    if "mean_score" in model:
        return (
            f"model pooled fidelity {model['pooled_fidelity']:.4f} is below the justified mean score "
            f"{model['mean_score']}"
        )
    return (
        f"the live performance record {model['perfs_sha256'][:12]} differs from the prepared read "
        f"{model['prepared_perfs_sha256'][:12]}"
    )


def dry_run(job: Job, anchor: bool) -> int:
    """Plan the written case read-only against the live platform and retain the plan without its body.

    The record carries the noise model's pooled fidelity at the live figures. A refusal by plan (the platform
    status, the shot estimate above max_shots) or a model pooled fidelity outside the justified range is retained as
    plan-refused.json and exits 1. With `anchor` the plan
    runs under the anchor read's performance figures and lands in plan-anchor.json."""
    out = CASES / job.name
    suffix = "-anchor" if anchor else ""
    with perfs_gate(job, anchor):
        model = live_model(job.request)
        return planned(job, out, suffix, model)


def attempt_path(out: Path, stem: str) -> Path:
    """``stem.json`` for the first planning attempt, else a new ``stem-<UTC>.json``; retained records keep their bytes.

    The retained plan records carry the digests the written case quotes, so a later attempt writes beside them.
    """
    first = out / f"{stem}.json"
    if not first.exists():
        return first
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return out / f"{stem}-{stamp}.json"


def retain_refusal(job: Job, out: Path, suffix: str, model: dict[str, Any], reason: str) -> int:
    """Retain a plan<suffix>-refused record (attempt_path), which carries the model and the reason, and return 1."""
    path = attempt_path(out, f"plan{suffix}-refused")
    write_json(
        path,
        {
            "refusal": reason,
            "model": model,
            "perfs_basis": job.request.anchor_read if suffix else "live processor record",
            "planned_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "sent": False,
        },
        exclusive=True,
    )
    print(f"{job.name}: plan refused: {reason} ({path.name})", file=sys.stderr)
    return 1


def planned(job: Job, out: Path, suffix: str, model: dict[str, Any]) -> int:
    """Plan the case and retain plan<suffix>.json, or retain a refusal and return 1.

    The platform's refusal (status, shot estimate above max_shots) and a model pooled fidelity below the justified
    mean score both refuse: the preregistered budget assumes the pooled fidelity of the noise model, so a plan
    at figures below it is no admission."""
    try:
        checked = plan(out, PLATFORM, job.credit_ceiling, job.expected_seconds, PER_JOB_CREDITS)
    except PlatformError as error:
        return retain_refusal(job, out, suffix, model, str(error))
    if not model["inside_justified_range"]:
        return retain_refusal(job, out, suffix, model, admission_failure(model))
    manifest = json.loads((out / "cases.json").read_text(encoding="utf-8"))
    validate_body(checked["body"], manifest)
    record = {key: value for key, value in checked.items() if key != "body"}
    record["body_sha256_without_process_id"] = body_digest(checked["body"])
    record["model"] = model
    record["perfs_basis"] = job.request.anchor_read if suffix else "live processor record"
    record["planned_utc"] = datetime.now(UTC).isoformat(timespec="seconds")
    record["sent"] = False
    path = attempt_path(out, f"plan{suffix}")
    write_json(path, record, exclusive=True)
    print(
        f"{job.name}: {PLATFORM} {checked['platform_at_plan']['status']}, ceiling {checked['credit_ceiling']:g} "
        f"credits, estimated {checked['estimated_shots']} shots, body {record['body_sha256_without_process_id']}, "
        f"model pooled fidelity {model['pooled_fidelity']:.4f}"
        + (f" against {model['mean_score']}" if "mean_score" in model else ", live record equals the prepared read")
    )
    return 0


def staged(run: Path) -> Job:
    """The job whose frozen request bytes RUN holds; RUN may hold nothing beyond them and the platform-before read."""
    name = json.loads((run / "cases.json").read_text(encoding="utf-8")).get("job")
    require(name in JOBS, f"{run / 'cases.json'} names job {name!r}, not one of {sorted(JOBS)}")
    job = JOBS[name]
    out = CASES / job.name
    for name in STAGED:
        require((run / name).read_bytes() == (out / name).read_bytes(), f"{run / name} is not the frozen {name}")
    extra = sorted(path.name for path in run.iterdir() if path.name not in (*STAGED, BEFORE))
    require(not extra, f"{run} holds {extra}; a run directory starts from the frozen request alone")
    return job


def binding(job: Job, admitted: dict[str, Any]) -> Callable[[dict[str, Any]], None]:
    """The verify step: the planned body is the retained body beyond process_id, and the live record admits the case
    (the decision rule's pooled fidelity at the live figures reaches F*; a descriptive case's live perfs equal its
    prepared read). The model of an admitted request lands in `admitted`."""
    out = CASES / job.name

    def bound(checked: dict[str, Any]) -> None:
        manifest = json.loads((out / "cases.json").read_text(encoding="utf-8"))
        validate_body(checked["body"], manifest)
        retained = json.loads((out / "job-body.json").read_text(encoding="utf-8"))
        fresh, frozen = body_digest(checked["body"]), body_digest(retained)
        if fresh != frozen:
            raise PlatformError(f"the planned body {fresh} differs from the retained body {frozen} beyond process_id")
        model = live_model(job.request)
        if not model["inside_justified_range"]:
            raise PlatformError(f"at the live figures, {admission_failure(model)}")
        admitted.update(model)

    return bound


def send(run: Path, approval: str, anchor: bool = False) -> int:
    """Read the platform into RUN/platform-before and submit the approved case once under the binding.

    With `anchor` the plan, Perceval's shot estimate and the binding's model run under the anchor read's performance
    figures (anchor_perfs), the gate the written case's anchor approval names; the platform read, and the live
    model recorded beside the admitting one, stay on the live record."""
    job = staged(run)
    context = perfs_gate(job, anchor)
    snapshot(run / BEFORE)
    observe(run / BEFORE)
    live = live_model(job.request) if anchor else None
    admitted: dict[str, Any] = {}
    with context:
        record = submit(
            run,
            PLATFORM,
            approval,
            job.credit_ceiling,
            job.expected_seconds,
            PER_JOB_CREDITS,
            verify=binding(job, admitted),
        )
    gate = {
        "job_id": record["job_id"],
        "gate": "anchor" if anchor else "live",
        "perfs_basis": job.request.anchor_read if anchor else "live processor record",
        "model": admitted,
    }
    if live is not None:
        gate["live_model"] = live
    write_json(run / SUBMIT_MODEL, gate, exclusive=True)
    print(
        f"job {record['job_id']} on {record['platform']}, {gate['gate']} model pooled fidelity "
        f"{admitted['pooled_fidelity']:.4f}"
    )
    return 0


def write_estimate(request: Request, case_dir: Path | None = None) -> dict[str, Any]:
    """Retain the anchor-state shot estimate of the request staged in `case_dir` (the case directory by default)
    beside the case; a retained file is never rewritten."""
    path = request.directory / ESTIMATE
    require(not path.exists(), f"{path.relative_to(ROOT)} exists; the retained estimate is frozen")
    record = shot_estimate(request, case_dir or request.directory)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1, sort_keys=True))
    return record


def write_justification(request: Request, record: dict[str, Any] | None = None) -> dict[str, Any]:
    """Retain the noise-model derivation `record` (justify's by default) beside the case; a retained file is never
    rewritten."""
    path = request.directory / "noise-model.json"
    require(not path.exists(), f"{path.relative_to(ROOT)} exists; the retained derivation is frozen")
    record = record or justify(request)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record["derived"], indent=1, sort_keys=True))
    return record


def prepare(name: str) -> int:
    """Derive the case `name` from its retained platform read and print the rows that register it.

    CASES/name/platform-read/catalogue.json, written by `qd_platform.py snapshot --out` that directory, is the case's
    fresh read and its anchor read. choose_layout places the logical modes on it, justify derives the case's rule
    (CASE_DESIGNS) and its budget under its figures (noise-model.json), and estimate_required_shots under its perfs
    sizes
    max_shots (shot-estimate.json) on the request staged in a temporary directory. The job bills 1 + max_shots * 1e-6
    credits, and its expected seconds follow expected_seconds at the read's clock. A decision case without decision
    power (bernoulli_decision_count), or any case whose expected seconds exceed max_duration, retains nothing: a job
    cut off at max_duration bills its max_shots. A descriptive case prints the forecast against each comparison. The
    REQUESTS and JOBS rows printed last enter the
    script in the change that retains these files, and `JOB`, --check, --body JOB and --plan JOB follow. A rerun
    re-derives and compares a retained noise-model.json and reuses a retained shot-estimate.json, so a failed live
    estimate resumes without rewriting a retained file."""
    require(name in CASE_SEEDS and name not in JOBS, f"{name} is not a seeded case without a registered job")
    request_dir = CASES / name
    read = request_dir / READ
    require(read.is_file(), f"{read.relative_to(ROOT)} is absent; snapshot the platform into it first")
    t_out, dark, figures = read_perfs(json.loads(read.read_text(encoding="utf-8")))
    rule, blocks = CASE_DESIGNS[name]
    request = Request(name, choose_layout(t_out, dark), CASE_SEEDS[name], str(read.relative_to(ROOT)), rule, blocks)
    retained = request_dir / "noise-model.json"
    record = justify(request)
    if retained.is_file():
        close(record, json.loads(retained.read_text(encoding="utf-8")), f"{name}/noise-model.json")
    derived = record["derived"]
    samples = int(derived["samples_per_iteration"])
    seconds = expected_seconds(derived, samples, figures["clock_mhz"], blocks)
    require(
        seconds <= MAX_DURATION,
        f"{name}: {samples} samples per iteration need an expected {seconds:g} s, above max_duration {MAX_DURATION} s",
    )
    if not retained.is_file():
        write_justification(request, record)
    if (request_dir / ESTIMATE).is_file():
        estimate = json.loads((request_dir / ESTIMATE).read_text(encoding="utf-8"))
        require(estimate["samples"] == samples, f"{name}/{ESTIMATE} estimates {estimate['samples']} samples")
    else:
        with tempfile.TemporaryDirectory() as staging:
            stage = Path(staging)
            # payload records every estimate before it compares max_shots, so this staging budget leaves them as is.
            provisional = Job(request, samples, SHOT_QUANTUM, PER_JOB_CREDITS, float(MAX_DURATION))
            for file_name, content in documents(provisional).items():
                (stage / file_name).write_bytes(content)
            estimate = write_estimate(request, stage)
    shots = int(estimate["shots_per_iteration"])
    credits = round(PER_JOB_CREDITS + shots * PRICE_PER_SHOT, 6)
    if rule == DESCRIPTIVE:
        print(
            f"forecast: correctness {derived['forecast_fidelity']:.4f}, "
            f"lower bound {derived['forecast_lower_bound']:.4f} "
            f"at n* = {derived['planned_accepted']}; "
            + "; ".join(
                f"{c['name']} {c['bound']:.4f} margin {c['forecast_margin']:+.4f}" for c in derived["comparisons"]
            )
        )
    design = "" if rule == DECISION else f", DESCRIPTIVE, {blocks}"
    print(
        f'REQUESTS["{name}"] = Request("{name}", {request.layout}, {name.upper().replace("-", "_")}_COMPILATION_SEEDS, '
        f'"{request.anchor_read}"{design})'
    )
    print(f'JOBS["{name}"] = Job(REQUESTS["{name}"], {samples}, {shots:_}, {credits}, {seconds})')
    return 0


def simulate(out: Path, job: Job) -> int:
    """Stage the frozen request into OUT and write the local simulation's results.json beside it.

    OUT holds no request or result file beforehand: a run directory that carries cases.json, circuit.json,
    results.json, submission.json or raw/ belongs to a staged or collected run, and the simulation never overwrites
    it."""
    held = [name for name in (*STAGED, "results.json", "submission.json", "raw") if (out / name).exists()]
    require(not held, f"{out} already holds {', '.join(held)}; --simulate writes into a directory without a run")
    manifest, circuit, _ = load_case(CASES / job.name)
    out.mkdir(parents=True, exist_ok=True)
    for name in STAGED:
        (out / name).write_bytes((CASES / job.name / name).read_bytes())
    variant = next(v for v in variants(job.request) if v.name == "anchor per-mode transmission")
    write_json(out / "results.json", simulated_results(manifest, circuit, variant))
    print(f"teleportation rehearsal: {out / 'results.json'} from the {variant.name} variant")
    return 0


def analyze(run: Path, replay: bool = False) -> int:
    """Write RUN/analysis.json, or with `replay` require the retained one to equal a fresh analysis.

    The replay compares within bdsc_certificate.close's tolerance, since the record carries floats."""
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    record = analyze_results(manifest, results, manifest.get("frames"))
    if replay:
        retained = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
        close(json.loads(json.dumps(record)), retained, f"{run.name}/analysis.json")
        outcome = f"verdict {record['verdict']}" if "verdict" in record else record["status"]
        print(f"{run.name}: analysis.json replays, {outcome}")
        return 0
    write_json(run / "analysis.json", record)
    if record["schema"] == "qd-teleportation-analysis-v2":
        pooled_row = record["pooled"]
        print(
            f"{record['status']}: correctness {pooled_row['fidelity']} over {pooled_row['accepted']} accepted, lower "
            f"bound {pooled_row['lower_bound']}; "
            + "; ".join(f"{c['name']} {c['label']}" for c in record["comparisons"])
        )
        return 0
    pooled_row = record["pooled"]
    if pooled_row["fidelity"] is None:
        figures = "pooled conditional fidelity unavailable (no accepted event)"
    else:
        figures = (
            f"pooled conditional fidelity {pooled_row['fidelity']:.4f} over {pooled_row['accepted']} accepted, lower "
            f"bound {pooled_row['lower_bound']:.4f}"
        )
    bound = record["benchmark"]["classical_bound"]
    print(f"{figures}, classical bound {'unavailable' if bound is None else f'{bound:.4f}'}: {record['verdict']}")
    if record["inputs_without_accepted"]:
        print(f"inputs without an accepted event: {', '.join(record['inputs_without_accepted'])}", file=sys.stderr)
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--check"]:
        return check()
    if argv == ["--estimate"]:
        write_estimate(REQUESTS["job-00"])
        return 0
    if argv == ["--justify"]:
        write_justification(REQUESTS["job-00"])
        return 0
    if len(argv) == 2 and argv[0] == "--prepare":
        return prepare(argv[1])
    anchor = argv[2:] == ["--anchor"]
    if len(argv) in (2, 3) and argv[0] == "--body" and argv[1] in JOBS and (len(argv) == 2 or anchor):
        return freeze_body(JOBS[argv[1]], anchor)
    if len(argv) in (2, 3) and argv[0] == "--plan" and argv[1] in JOBS and (len(argv) == 2 or anchor):
        return dry_run(JOBS[argv[1]], anchor)
    if len(argv) in (2, 3) and argv[0] == "--simulate" and argv[2:3] in ([], *([job] for job in JOBS)):
        return simulate(Path(argv[1]), JOBS[argv[2] if len(argv) == 3 else "job-00"])
    if len(argv) in (2, 3) and argv[0] == "--analyze" and argv[2:] in ([], ["--check"]):
        return analyze(Path(argv[1]), argv[2:] == ["--check"])
    if len(argv) in (3, 4) and argv[0] == "--submit" and argv[3:] in ([], ["--anchor"]):
        return send(Path(argv[1]), argv[2], argv[3:] == ["--anchor"])
    if len(argv) == 1 and argv[0] in JOBS:
        return build(JOBS[argv[0]])
    raise ValueError(
        "usage: qd_teleportation_rehearsal.py [--check | --justify | --estimate | --prepare CASE | JOB | "
        "--body JOB [--anchor] | --plan JOB [--anchor] | "
        f"--simulate OUT [JOB] | --analyze RUN [--check] | --submit RUN APPROVAL [--anchor]], JOB in {sorted(JOBS)}, "
        f"CASE in {sorted(set(CASE_SEEDS) - set(JOBS))}, not {argv}"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
