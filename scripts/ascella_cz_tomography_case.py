"""Ascella postselected CZ process tomography: two qpu:ascella jobs of 72 template iterations on twelve modes.

docs/design/ascella-cz-process-tomography-case.md fixes the request. Two photons carry two dual-rail qubits through the
postselected Ralph CZ of Perceval's catalog ("postprocessed cz"): control rails (0, 1), target rails (2, 3), vacuum
ancillas (4, 5), the chip window at chip modes 0..5. The two-click subspace with one photon on each rail pair
implements diag(1, 1, 1, -1) / 3, a success probability of 1/9.

Process tomography uses the four Pauli eigenstates |0>, |1>, |+>, |+i> on each qubit (16 inputs) and the 9 product
Pauli readouts (3 x 3), 144 settings. Each setting folds its input preparations and its readout rotations into one
6 x 6 unitary around the CZ block, and photonic_template (hypercomplex_cases) decomposes it into the same
nearest-neighbor Rx/phase mesh. The service re-transpiles every iteration under its own compilation_seed, so the
estimate is the average over 144 service-compiled meshes, not one fixed gate. The 144 settings split into two jobs by
the parity of the input pair, 72 iterations each, in input-major order.

An event is eligible when it carries exactly two threshold clicks across all twelve returned modes, one on a control
rail and one on a target rail. The four eligible rail pairs of a setting give that setting's readout outcomes. The
estimator normalizes each setting to its eligible events (a trace-preserving conditional process), inverts the
144 x 4 outcome frequencies linearly onto the 16 x 16 Choi matrix, and projects the result onto the nearest
completely positive trace-preserving map. It reports the process fidelity to the ideal CZ and the average gate
fidelity (4 F + 1) / 5 with a bootstrap interval whose seed is a value of a retained QRNG draw.

--check rebuilds both jobs in memory and compares them with the retained files, proves the CZ block and the folded
settings by permanents and by Perceval's SLOS backend, binds every iteration through qd_platform.template_experiment,
and requires the noiseless process fidelity 1. --forecast recomputes the retained noise forecast under Perceval's
NoiseModel at the platform read in the case directory. --estimate retains Perceval's shot estimate (a read-only
platform call). --analyze OUT.json RUN... pools collected runs into the process estimate. Submission uses the generic
runner, scripts/qd_platform.py plan/submit/collect, with the written case's arguments.

Usage:
  "$PYTHON" scripts/ascella_cz_tomography_case.py [--check | --build | --forecast | --estimate]
  "$PYTHON" scripts/ascella_cz_tomography_case.py --analyze OUT.json RUN [RUN ...]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections.abc import Mapping, Sequence
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import PlatformError, load_case, payload, sha256_bytes, template_experiment  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLATFORM = "qpu:ascella"
FAMILY = "ascella_cz_tomography"
FAMILY_DIR = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/ascella-cz-process-tomography-case.md"
READ = "platform-read/ascella-perfs.json"
FORECAST = "forecast.json"
ESTIMATE = "shot-estimate.json"
MODES = 12
WINDOW = 6
# Logical modes c0 c1 t0 t1 h0 h1 sit on chip modes 0..5; the photons enter chip modes 0 and 2, both connected
# source modes of qpu:ascella. choose_window requires the read's darkest connected window to start at 0.
CONNECTED = (0, 2, 4, 6, 8, 10)
C0, C1, T0, T1, H0, H1 = range(WINDOW)
SOURCES = (C0, T0)
JOBS = ("job-00", "job-01")
MIN_CLICKS = 2
MAX_DURATION = 300
TOLERANCE = 1e-12
BODY_TOLERANCE = 1e-9
SQRT_HALF = math.sqrt(0.5)
# The ANU QRNG draw whose values seed every compilation and the bootstrap; the manifests name it without an index
# and so own it whole (ci/seed_provenance.py).
DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T034409Z.json"
SEED_RULE = (
    "nonzero draw values in index order, repeats skipped; 144 compilation seeds in schedule order, "
    "then the bootstrap seed"
)
# Per-iteration budgets of one job (docs/design/ascella-cz-process-tomography-case.md, written case).
SAMPLES_PER_ITERATION = 6000
# max_shots per iteration of each job: the largest Perceval estimate of the job's settings (shot-estimate.json) times
# SHOT_MARGIN, rounded up to SHOT_QUANTUM. A job bills its largest iteration's max_shots.
JOB_SHOTS = {"job-00": 500000, "job-01": 2300000}
SHOT_MARGIN = 1.25
SHOT_QUANTUM = 100000
PER_JOB_CREDITS = 1.0
PRICE_PER_SHOT = 1e-6
EXPECTED_SECONDS = 240
BOOTSTRAP_REPLICATES = 500
BOOTSTRAP_LEVEL = 0.95
# The interval type the analysis reports. The coverage study of forecast.json decides it: the percentile interval of a
# fidelity estimated under a positivity projection sits below the estimand by the projection's bias, and the basic
# interval reflects that bias.
INTERVAL_KIND = "basic"
COVERAGE_DATASETS = 40
# The reported interval type must cover the estimand in at least this share of the synthetic datasets.
COVERAGE_FLOOR = 0.9
COVERAGE_REPLICATES = 200
COVERAGE_VARIANT = "source, loss and dark counts"
SAMPLED_KEYS = (
    "process_fidelity",
    "process_fidelity_interval",
    "process_fidelity_intervals",
    "process_fidelity_bootstrap_median",
    "average_gate_fidelity",
    "average_gate_fidelity_interval",
    "linear_inversion_fidelity",
    "events",
)
# Pauli eigenstates prepared on each qubit: label -> (theta, phi) of cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>.
INPUT_STATES = {"0": (0.0, 0.0), "1": (math.pi, 0.0), "+": (math.pi / 2, 0.0), "i": (math.pi / 2, math.pi / 2)}
BASES = ("X", "Y", "Z")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------- the gate and the settings


@cache
def cz_unitary() -> np.ndarray:
    """The 6-mode unitary of Perceval's catalog "postprocessed cz": control (0, 1), target (2, 3), vacuum ancillas."""
    import perceval as pcvl

    experiment = pcvl.catalog["postprocessed cz"].build_experiment()
    matrix = np.asarray(experiment.unitary_circuit().compute_unitary(), dtype=complex)
    require(matrix.shape == (WINDOW, WINDOW), f"the CZ circuit spans {matrix.shape}, not six modes")
    require(dict(experiment.heralds) == {4: 0, 5: 0}, f"the CZ heralds are {dict(experiment.heralds)}")
    return matrix


def hadamard_on_target() -> np.ndarray:
    full = np.eye(WINDOW, dtype=complex)
    full[T0 : T1 + 1, T0 : T1 + 1] = np.array([[1, 1], [1, -1]], dtype=complex) * SQRT_HALF
    return full


def preparation(theta: float, phi: float) -> np.ndarray:
    """Unitary on one rail pair whose first column is (cos(theta/2), e^{i phi} sin(theta/2))."""
    rotation = np.array([[math.cos(theta / 2), -math.sin(theta / 2)], [math.sin(theta / 2), math.cos(theta / 2)]])
    return np.asarray(np.diag([1.0, np.exp(1j * phi)]) @ rotation, dtype=complex)


def readout(basis: str) -> np.ndarray:
    """Rotation ahead of the click: identity for Z, a balanced beam splitter for X, a -pi/2 phase on rail 1 ahead of it
    for Y."""
    hadamard = np.array([[1, 1], [1, -1]], dtype=complex) * SQRT_HALF
    if basis == "Z":
        return np.eye(2, dtype=complex)
    if basis == "X":
        return hadamard
    if basis == "Y":
        return np.asarray(hadamard @ np.diag([1.0, -1j]), dtype=complex)
    raise ValueError(f"unknown readout basis {basis}")


def pair_block(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """The 6 x 6 unitary that applies `first` to the control rails, `second` to the target rails and the identity to
    the ancillas."""
    full = np.eye(WINDOW, dtype=complex)
    full[C0 : C1 + 1, C0 : C1 + 1] = first
    full[T0 : T1 + 1, T0 : T1 + 1] = second
    return full


def coincidence_block(unitary: np.ndarray) -> np.ndarray:
    """4 x 4 amplitudes (output row, input column) of the one-photon-per-pair subspace, in the order (c, t) = 00, 01,
    10, 11 with c, t the rail index, by the permanent of the 2 x 2 submatrix of each input and output pair."""
    block = np.zeros((4, 4), dtype=complex)
    for out, inp in itertools.product(range(4), repeat=2):
        o = (C0 + out // 2, T0 + out % 2)
        i = (C0 + inp // 2, T0 + inp % 2)
        block[out, inp] = unitary[o[0], i[0]] * unitary[o[1], i[1]] + unitary[o[0], i[1]] * unitary[o[1], i[0]]
    return block


def setting_unitary(row: Mapping[str, Any]) -> np.ndarray:
    """The 6 x 6 unitary of one setting: readout rotations after the CZ after the input preparations."""
    prepare = pair_block(preparation(*INPUT_STATES[row["input"][0]]), preparation(*INPUT_STATES[row["input"][1]]))
    read = pair_block(readout(row["basis"][0]), readout(row["basis"][1]))
    return np.asarray(read @ cz_unitary() @ prepare, dtype=complex)


def schedule() -> list[dict[str, Any]]:
    """The 144 settings in schedule order (input-major, then readout basis), each naming its job.

    A setting belongs to job-00 when the indices of its two input labels have an even sum, so each job holds all four
    states on each qubit and the full nine readouts of eight inputs."""
    rows: list[dict[str, Any]] = []
    labels = tuple(INPUT_STATES)
    for input_pair in itertools.product(labels, repeat=2):
        parity = sum(labels.index(label) for label in input_pair) % 2
        for basis_pair in itertools.product(BASES, repeat=2):
            rows.append(
                {
                    "name": f"in-{''.join(input_pair)}-{''.join(basis_pair)}",
                    "input": "".join(input_pair),
                    "basis": "".join(basis_pair),
                    "job": JOBS[parity],
                    "schedule_index": len(rows),
                }
            )
    return rows


def job_rows(job: str) -> list[dict[str, Any]]:
    return [row for row in schedule() if row["job"] == job]


def readout_vectors(basis: str) -> list[np.ndarray]:
    """The state a click on rail 0 and on rail 1 projects onto: the conjugate of the rotation's row."""
    rotation = readout(basis)
    return [rotation[rail].conj() for rail in range(2)]


def outcome_projector(basis: str, outcome: int) -> np.ndarray:
    """The 4 x 4 projector of outcome `outcome` (2 * control rail + target rail) in the readout basis pair."""
    control = readout_vectors(basis[0])[outcome // 2]
    target = readout_vectors(basis[1])[outcome % 2]
    vector = np.kron(control, target)
    return np.asarray(np.outer(vector, vector.conj()), dtype=complex)


def input_density(label: str) -> np.ndarray:
    vector = np.kron(preparation(*INPUT_STATES[label[0]])[:, 0], preparation(*INPUT_STATES[label[1]])[:, 0]).astype(
        complex
    )
    return np.asarray(np.outer(vector, vector.conj()), dtype=complex)


def ideal_cz() -> np.ndarray:
    return np.diag([1.0, 1.0, 1.0, -1.0]).astype(complex)


def ideal_outcomes(row: Mapping[str, Any]) -> list[float]:
    """The ideal conditional probability of each of the four readout outcomes of a setting."""
    first, second = (preparation(*INPUT_STATES[label])[:, 0] for label in row["input"])
    state = ideal_cz() @ np.kron(first, second)
    return [float(np.real(state.conj() @ outcome_projector(row["basis"], o) @ state)) for o in range(4)]


def exact_outcomes(row: Mapping[str, Any]) -> tuple[list[float], float]:
    """(conditional probabilities, accepted probability per two-photon attempt) of a setting from the permanents of
    its 6 x 6 unitary, for indistinguishable photons without loss."""
    block = coincidence_block(setting_unitary(row))
    # Input rails (0, 0): the photons enter the first rail of each pair.
    amplitudes = block[:, 0]
    probabilities = np.abs(amplitudes) ** 2
    total = float(probabilities.sum())
    return [float(p / total) for p in probabilities], total


# ---------------------------------------------------------------- seeds


def draw_values() -> list[int]:
    record = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    values = record["values"]
    require(isinstance(values, list) and all(type(v) is int for v in values), f"{DRAW} holds no integer values")
    return list(values)


def usable_draw() -> list[tuple[int, int]]:
    """(index, value) of the draw's usable values in index order: nonzero, not yet taken."""
    taken: set[int] = set()
    usable = []
    for index, value in enumerate(draw_values()):
        if value == 0 or value in taken:
            continue
        taken.add(value)
        usable.append((index, value))
    return usable


def seed_plan() -> tuple[list[tuple[int, int]], tuple[int, int]]:
    """(compilation seed (index, value) of every schedule position, bootstrap seed (index, value))."""
    usable = usable_draw()
    count = len(schedule())
    require(len(usable) > count, f"{DRAW} holds {len(usable)} usable values, not {count + 1}")
    return usable[:count], usable[count]


# ---------------------------------------------------------------- the retained request


def read_perfs() -> dict[str, Any]:
    document = json.loads((FAMILY_DIR / READ).read_text(encoding="utf-8"))
    perfs: dict[str, Any] = document["perfs"]
    return perfs


def choose_window(perfs: Mapping[str, Any]) -> int:
    """The first chip mode of the darkest window of six modes whose two photon inputs (its first and third modes)
    are connected source modes."""
    dark = perfs["Dark counts (detection/s)"]
    starts = [s for s in range(MODES - WINDOW + 1) if s in CONNECTED and s + 2 in CONNECTED]
    return min(starts, key=lambda s: (sum(dark[s : s + WINDOW]), s))


def source_state() -> list[int]:
    state = [0] * MODES
    for logical in SOURCES:
        state[logical] = 1
    return state


def embed(window: np.ndarray) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    full[:WINDOW, :WINDOW] = window
    return full


def build_setting(item: tuple[int, dict[str, Any], int]) -> tuple[dict[str, Any], dict[str, Any]]:
    """The template mesh and the manifest setting of one schedule row, at `seed` as its compilation seed."""
    position, row, seed = item
    unitary = setting_unitary(row)
    mesh, parameters = photonic_template(unitary)
    full = embed(unitary)
    conditional, accepted = exact_outcomes(row)
    setting = {
        **row,
        "observation_index": position,
        "ideal": {
            "outcome_probabilities": [round(p, 12) for p in conditional],
            "accepted_probability": round(accepted, 12),
        },
        "circuit_params": parameters,
        "compilation_seed": seed,
        "column": [[float(value.real), float(value.imag)] for value in full[:, SOURCES[0]]],
        "operator": encoded(full),
    }
    return mesh, setting


def request_parts(job: str) -> tuple[list[dict[str, Any]], dict[str, Any], list[int]]:
    """The manifest settings of a job, the one template circuit they share and the draw index of each seed."""
    seeds, _ = seed_plan()
    rows = job_rows(job)
    items = [(position, row, seeds[row["schedule_index"]][1]) for position, row in enumerate(rows)]
    built = ordered_map(build_setting, items, min_items=1)
    template = built[0][0]
    for position, (mesh, _) in enumerate(built):
        require(mesh == template, f"setting {position} needs another mesh than setting 0")
    circuit = {**template, "modes": MODES, "input_state": source_state()}
    return [setting for _, setting in built], circuit, [seeds[row["schedule_index"]][0] for row in rows]


def documents(job: str) -> dict[str, bytes]:
    settings, circuit, indices = request_parts(job)
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    count = len(settings)
    _, bootstrap = seed_plan()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": count,
        "min_detected_photons": MIN_CLICKS,
        "max_samples": SAMPLES_PER_ITERATION * count,
        "max_shots": JOB_SHOTS[job] * count,
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(WINDOW)),
        "layout": {"logical": ["c0", "c1", "t0", "t1", "h0", "h1"], "chip_modes": list(range(WINDOW))},
        "eligibility": "exactly two threshold clicks across all twelve returned modes, one on a control rail "
        "(modes 0, 1) and one on a target rail (modes 2, 3)",
        "outcomes": {"order": ["00", "01", "10", "11"], "meaning": "control rail then target rail of the click"},
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "compilation_seeds": {"draw": DRAW, "indices": indices, "rule": SEED_RULE},
        "preregistered": {
            "estimator": "linear inversion of the 144 x 4 outcome frequencies onto the 16 x 16 Choi matrix, then the "
            "nearest completely positive trace-preserving map by Dykstra alternating projections",
            "process_fidelity": "F_pro = <Phi_CZ| J |Phi_CZ> / 16 for the Choi matrix J of trace 4",
            "average_gate_fidelity": "F_avg = (4 F_pro + 1) / 5",
            "bootstrap": {
                "replicates": BOOTSTRAP_REPLICATES,
                "level": BOOTSTRAP_LEVEL,
                "kind": "parametric multinomial resample of every setting's eligible events; the "
                + INTERVAL_KIND
                + " interval, chosen by the coverage study in forecast.json",
                "seed_draw": DRAW,
                "seed_index": bootstrap[0],
            },
            "pooling": "both jobs; a missing setting leaves the estimate undecided and its subset descriptive",
            "descriptive": [
                "linear-inversion fidelity before the projection",
                "per-setting eligible share of the two-click samples",
                "exclusions by cause",
                "comparison with the retained noise forecast",
            ],
            "vendor_comparison": "93.8 +- 0.6 % CNOT fidelity of the vendor chip, descriptive only: a different gate "
            "on a calibrated, uncompiled-per-setting chip",
            "interpretation": "service-compiled average postselected CZ; preparation, readout and gate errors are "
            "not separable because every setting compiles to its own mesh",
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


# ---------------------------------------------------------------- process estimation


def hermitian_basis() -> list[np.ndarray]:
    """The 256 Hilbert-Schmidt-orthonormal Hermitian 16 x 16 matrices."""
    size = 16
    basis = []
    for i in range(size):
        matrix = np.zeros((size, size), dtype=complex)
        matrix[i, i] = 1.0
        basis.append(matrix)
    for i, j in itertools.combinations(range(size), 2):
        symmetric = np.zeros((size, size), dtype=complex)
        symmetric[i, j] = symmetric[j, i] = SQRT_HALF
        antisymmetric = np.zeros((size, size), dtype=complex)
        antisymmetric[i, j] = 1j * SQRT_HALF
        antisymmetric[j, i] = -1j * SQRT_HALF
        basis.extend([symmetric, antisymmetric])
    return basis


@cache
def design_matrix() -> np.ndarray:
    """Rows (schedule setting, outcome): Tr[(rho_in^T x E_outcome) H_k] over the Hermitian basis H_k of the Choi matrix.

    The Choi matrix is J = sum_ij |i><j| x Lambda(|i><j|) with the input factor first, so the probability of outcome
    E on input rho is Tr[(rho^T x E) J]."""
    basis = hermitian_basis()
    rows = []
    for row in schedule():
        density = input_density(row["input"]).T
        for outcome in range(4):
            observable = np.kron(density, outcome_projector(row["basis"], outcome))
            rows.append([float(np.real(np.trace(observable @ element))) for element in basis])
    return np.asarray(rows)


@cache
def design_pseudoinverse() -> np.ndarray:
    matrix = design_matrix()
    rank = int(np.linalg.matrix_rank(matrix))
    require(rank == 256, f"the 144 settings give rank {rank} of the 256 Choi parameters")
    return np.asarray(np.linalg.pinv(matrix))


def choi_of(coefficients: np.ndarray) -> np.ndarray:
    total = np.zeros((16, 16), dtype=complex)
    for coefficient, element in zip(coefficients, hermitian_basis(), strict=True):
        total += coefficient * element
    return total


def linear_inversion(frequencies: np.ndarray) -> np.ndarray:
    """The Choi matrix whose predicted outcome frequencies are closest in least squares to the (576,) observed ones."""
    return choi_of(design_pseudoinverse() @ frequencies)


def partial_trace_output(choi: np.ndarray) -> np.ndarray:
    return np.asarray(np.einsum("iojo->ij", choi.reshape(4, 4, 4, 4)))


def project_trace_preserving(choi: np.ndarray) -> np.ndarray:
    residual = partial_trace_output(choi) - np.eye(4)
    return choi - np.kron(residual, np.eye(4)) / 4


def project_positive(choi: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((choi + choi.conj().T) / 2)
    return np.asarray((vectors * np.clip(values, 0.0, None)) @ vectors.conj().T)


def normalize_trace_preserving(choi: np.ndarray) -> np.ndarray:
    """(T^-1/2 x I) J (T^-1/2 x I) with T the input marginal: positive stays positive and the marginal becomes I."""
    values, vectors = np.linalg.eigh(partial_trace_output(choi))
    require(float(values.min()) > 0.0, "the projected process has a rank-deficient input marginal")
    root = (vectors / np.sqrt(values)) @ vectors.conj().T
    scale = np.kron(root, np.eye(4))
    return np.asarray(scale @ choi @ scale.conj().T)


def cptp_projection(choi: np.ndarray, sweeps: int = 5000, tolerance: float = 1e-12) -> np.ndarray:
    """The Frobenius-nearest completely positive trace-preserving Choi matrix (Dykstra's alternating projections onto
    the positive cone and the trace-preserving hyperplane), made exactly trace preserving by input renormalization."""
    x = choi
    p = np.zeros_like(choi)
    q = np.zeros_like(choi)
    for _ in range(sweeps):
        y = project_trace_preserving(x + p)
        p = x + p - y
        z = project_positive(y + q)
        q = y + q - z
        change = float(np.max(np.abs(z - x)))
        x = z
        if change < tolerance:
            break
    return normalize_trace_preserving(x)


@cache
def ideal_choi_vector() -> np.ndarray:
    vector = np.zeros(16, dtype=complex)
    cz = ideal_cz()
    for i in range(4):
        basis = np.zeros(4, dtype=complex)
        basis[i] = 1.0
        vector += np.kron(basis, cz @ basis)
    return vector


def process_fidelity(choi: np.ndarray) -> float:
    vector = ideal_choi_vector()
    return float(np.real(vector.conj() @ choi @ vector) / 16)


def average_gate_fidelity(fidelity: float) -> float:
    return (4 * fidelity + 1) / 5


def estimate(frequencies: np.ndarray) -> dict[str, Any]:
    raw = linear_inversion(frequencies)
    projected = cptp_projection(raw)
    fidelity = process_fidelity(projected)
    return {
        "process_fidelity": fidelity,
        "average_gate_fidelity": average_gate_fidelity(fidelity),
        "linear_inversion_fidelity": process_fidelity(raw),
        "choi": projected,
    }


def replicate_fidelity(frequencies: np.ndarray) -> float:
    return float(estimate(frequencies)["process_fidelity"])


def resampled_frequencies(counts: np.ndarray, generator: np.random.Generator, replicates: int) -> np.ndarray:
    """(replicates, 576) outcome frequencies of multinomial resamples of the (144, 4) counts.

    One generator draws every replicate before the estimator maps over them, so the result does not depend on the
    pool size."""
    totals = counts.sum(axis=1)
    probabilities = counts / totals[:, None]
    draws = np.empty((replicates, counts.shape[0], 4))
    for k in range(replicates):
        for s in range(counts.shape[0]):
            draws[k, s] = generator.multinomial(int(totals[s]), probabilities[s])
    return np.asarray((draws / totals[None, :, None]).reshape(replicates, -1))


def intervals(point: float, replicate_values: Sequence[float], level: float) -> dict[str, list[float]]:
    """The percentile interval of the replicates and the basic interval (2 point - q_high, 2 point - q_low), which
    reflects the replicates' bias about the point and stops at 1, the bound of both fidelities."""
    low, high = (float(q) for q in np.percentile(replicate_values, [50 * (1 - level), 50 * (1 + level)]))
    return {"percentile": [low, high], "basic": [min(1.0, 2 * point - high), min(1.0, 2 * point - low)]}


def tomography(
    counts: np.ndarray, generator: np.random.Generator, replicates: int = BOOTSTRAP_REPLICATES
) -> dict[str, Any]:
    """The process estimate of (144, 4) eligible counts in schedule order, with its bootstrap intervals; the headline
    interval is INTERVAL_KIND."""
    frequencies = (counts / counts.sum(axis=1)[:, None]).reshape(-1)
    point = estimate(frequencies)
    fidelities = ordered_map(
        replicate_fidelity, list(resampled_frequencies(counts, generator, replicates)), min_items=8
    )
    process = intervals(point["process_fidelity"], fidelities, BOOTSTRAP_LEVEL)
    gate = intervals(point["average_gate_fidelity"], [average_gate_fidelity(f) for f in fidelities], BOOTSTRAP_LEVEL)
    return {
        "process_fidelity": point["process_fidelity"],
        "process_fidelity_interval": process[INTERVAL_KIND],
        "process_fidelity_intervals": process,
        "process_fidelity_bootstrap_median": float(np.median(fidelities)),
        "average_gate_fidelity": point["average_gate_fidelity"],
        "average_gate_fidelity_interval": gate[INTERVAL_KIND],
        "average_gate_fidelity_intervals": gate,
        "linear_inversion_fidelity": point["linear_inversion_fidelity"],
        "bootstrap": {"replicates": replicates, "level": BOOTSTRAP_LEVEL, "interval": INTERVAL_KIND},
        "events": int(counts.sum()),
    }


def ideal_frequencies() -> np.ndarray:
    return np.asarray([p for row in schedule() for p in ideal_outcomes(row)])


# ---------------------------------------------------------------- noise forecast


def photon_distribution(unitary: np.ndarray, hom: float, g2: float) -> dict[tuple[int, ...], float]:
    """Photon-number distribution over the six window modes under Perceval's source model (indistinguishability, g2)."""
    import perceval as pcvl

    noise = pcvl.NoiseModel(indistinguishability=hom, g2=g2)
    processor = pcvl.Processor("SLOS", pcvl.Unitary(pcvl.Matrix(unitary)), noise=noise)
    processor.min_detected_photons_filter(1)
    processor.with_input(pcvl.BasicState([1, 0, 1, 0, 0, 0]))
    results = processor.probs()["results"]
    return {tuple(int(count) for count in state): float(probability) for state, probability in results.items()}


def detected_clicks(
    photons: Mapping[tuple[int, ...], float], efficiency: float, dark: Sequence[float]
) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution over twelve modes: each photon is detected with probability `efficiency`, a mode
    with n photons clicks with probability 1 - (1 - efficiency)^n, and each mode adds one dark click with the
    per-attempt probability dark[mode] (first order: at most one dark click per attempt)."""
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, probability in photons.items():
        padded = tuple(occupation) + (0,) * (MODES - len(occupation))
        modes = [mode for mode, count in enumerate(padded) if count]
        chance = [1.0 - (1.0 - efficiency) ** padded[mode] for mode in modes]
        for pattern in itertools.product((0, 1), repeat=len(modes)):
            weight = probability
            vector = [0] * MODES
            for mode, clicked, p in zip(modes, pattern, chance, strict=True):
                weight *= p if clicked else 1.0 - p
                vector[mode] = clicked
            if weight > 0.0:
                key = tuple(vector)
                clicks[key] = clicks.get(key, 0.0) + weight
    if not any(dark):
        return clicks
    with_dark: dict[tuple[int, ...], float] = {}
    for pattern, weight in clicks.items():
        quiet = 1.0 - sum(dark[mode] for mode in range(MODES) if not pattern[mode])
        with_dark[pattern] = with_dark.get(pattern, 0.0) + weight * quiet
        for mode in range(MODES):
            if not pattern[mode]:
                bumped = pattern[:mode] + (1,) + pattern[mode + 1 :]
                with_dark[bumped] = with_dark.get(bumped, 0.0) + weight * dark[mode]
    return with_dark


def outcome_of(vector: Sequence[int]) -> int | None:
    """The readout outcome (2 * control rail + target rail) of an eligible click vector, else None."""
    if sum(vector) != MIN_CLICKS or vector[C0] + vector[C1] != 1 or vector[T0] + vector[T1] != 1:
        return None
    return 2 * (0 if vector[C0] else 1) + (0 if vector[T0] else 1)


FORECAST_VARIANTS = (
    "source only",
    "source and loss",
    "source, loss and dark counts",
    "g2-corrected overlap, loss and dark counts",
)


def corrected_overlap(hom: float, g2: float) -> float:
    """First-order photon overlap behind a HOM visibility read under multiphoton emission: (V + g2) / (1 - g2)
    (Ollivier et al., PRL 126, 063602 (2021), the relation docs/design/ascella-two-photon-associator-case.md cites)."""
    return min(1.0, (hom + g2) / (1.0 - g2))


def forecast_setting(item: tuple[dict[str, Any], dict[str, float], list[float]]) -> dict[str, Any]:
    """Per variant: the eligible share of the two-click samples and the conditional outcome probabilities."""
    row, figures, dark_rates = item
    unitary = setting_unitary(row)
    photons = photon_distribution(unitary, figures["hom"], figures["g2"])
    corrected = photon_distribution(unitary, corrected_overlap(figures["hom"], figures["g2"]), figures["g2"])
    dark_probability = [rate / (figures["clock_mhz"] * 1e6) for rate in dark_rates]
    quiet = [0.0] * MODES
    configurations = {
        "source only": (photons, 1.0, quiet),
        "source and loss": (photons, figures["transmittance"], quiet),
        "source, loss and dark counts": (photons, figures["transmittance"], dark_probability),
        "g2-corrected overlap, loss and dark counts": (corrected, figures["transmittance"], dark_probability),
    }
    out: dict[str, Any] = {}
    for name, (distribution, efficiency, dark) in configurations.items():
        clicks = detected_clicks(distribution, efficiency, dark)
        sampled = sum(p for vector, p in clicks.items() if sum(vector) >= MIN_CLICKS)
        eligible = [0.0] * 4
        for vector, p in clicks.items():
            outcome = outcome_of(vector)
            if outcome is not None:
                eligible[outcome] += p
        total = sum(eligible)
        out[name] = {
            "sample_probability": sampled,
            "eligible_share": total / sampled,
            "outcome_probabilities": [e / total for e in eligible],
        }
    return out


def perf_figures(perfs: Mapping[str, Any]) -> dict[str, float]:
    return {
        "hom": perfs["HOM (%)"] / 100.0,
        "g2": perfs["g2 (%)"] / 100.0,
        "transmittance": perfs["Transmittance (%)"] / 100.0,
        "clock_mhz": float(perfs["Clock (MHz)"]),
    }


def expected_counts(per_setting: Sequence[Mapping[str, Any]], name: str) -> np.ndarray:
    """(144, 4) expected eligible counts of a variant at the case's samples per iteration."""
    return np.asarray(
        [
            [SAMPLES_PER_ITERATION * entry[name]["eligible_share"] * p for p in entry[name]["outcome_probabilities"]]
            for entry in per_setting
        ]
    )


def sampled_counts(expected: np.ndarray, generator: np.random.Generator) -> np.ndarray:
    """One synthetic dataset: every setting's rounded eligible total drawn multinomially from its outcome law."""
    totals = np.rint(expected.sum(axis=1)).astype(int)
    probabilities = expected / expected.sum(axis=1)[:, None]
    return np.asarray([generator.multinomial(int(n), p) for n, p in zip(totals, probabilities, strict=True)])


def dataset_streams(value: int) -> tuple[np.random.Generator, np.random.Generator]:
    """The sampling and bootstrap generators of one synthetic dataset: the two children of one draw value."""
    sampling, resampling = np.random.SeedSequence(value).spawn(2)
    return np.random.default_rng(sampling), np.random.default_rng(resampling)


def forecast_seeds() -> list[tuple[int, int]]:
    """(index, value) of the draw's usable values after the compilation and bootstrap seeds: one per forecast variant,
    then one per coverage dataset. The device analysis keeps its bootstrap seed to itself."""
    usable = usable_draw()
    start = len(schedule()) + 1
    need = len(FORECAST_VARIANTS) + COVERAGE_DATASETS
    require(len(usable) >= start + need, f"{DRAW} holds {len(usable)} usable values, not {start + need}")
    return usable[start : start + need]


def coverage_study(expected: np.ndarray, seeds: Sequence[tuple[int, int]]) -> dict[str, Any]:
    """How often each interval type covers the estimator's value at the expected counts across synthetic datasets.

    Every dataset takes one draw value; its replicates are drawn before one pool maps the estimator over all of them."""
    truth = estimate((expected / expected.sum(axis=1)[:, None]).reshape(-1))["process_fidelity"]
    datasets = []
    batches = []
    for _, value in seeds:
        sampling, resampling = dataset_streams(value)
        counts = sampled_counts(expected, sampling)
        datasets.append(counts)
        batches.append(resampled_frequencies(counts, resampling, COVERAGE_REPLICATES))
    flat = [row for batch in batches for row in batch]
    fidelities = ordered_map(replicate_fidelity, flat, min_items=8)
    hits = {"percentile": 0, "basic": 0}
    points = []
    for k, counts in enumerate(datasets):
        point = estimate((counts / counts.sum(axis=1)[:, None]).reshape(-1))["process_fidelity"]
        points.append(point)
        chunk = fidelities[k * COVERAGE_REPLICATES : (k + 1) * COVERAGE_REPLICATES]
        for kind, (low, high) in intervals(point, chunk, BOOTSTRAP_LEVEL).items():
            hits[kind] += low <= truth <= high
    return {
        "variant": COVERAGE_VARIANT,
        "estimand": truth,
        "datasets": len(datasets),
        "replicates": COVERAGE_REPLICATES,
        "level": BOOTSTRAP_LEVEL,
        "coverage": {kind: count / len(datasets) for kind, count in hits.items()},
        "mean_point_bias": float(np.mean(points) - truth),
        "seed_indices": [index for index, _ in seeds],
    }


def forecast() -> dict[str, Any]:
    """The noise forecast. Per variant: the estimator's value at the expected eligible counts of the case's budget
    (the estimand), and the point and interval of one synthetic dataset sampled from those counts, as a run returns
    them. The coverage study checks the preregistered interval type on the third variant."""
    perfs = read_perfs()
    figures = perf_figures(perfs)
    dark = list(perfs["Dark counts (detection/s)"])
    rows = schedule()
    per_setting = ordered_map(forecast_setting, [(row, figures, dark) for row in rows], min_items=1)
    seeds = forecast_seeds()
    result: dict[str, Any] = {}
    for k, name in enumerate(FORECAST_VARIANTS):
        expected = expected_counts(per_setting, name)
        shares = [entry[name]["eligible_share"] for entry in per_setting]
        estimand = estimate((expected / expected.sum(axis=1)[:, None]).reshape(-1))
        sampling, resampling = dataset_streams(seeds[k][1])
        sampled = tomography(sampled_counts(expected, sampling), resampling)
        result[name] = {
            "least_eligible_share": min(shares),
            "mean_eligible_share": sum(shares) / len(shares),
            "expected_eligible_events": float(expected.sum()),
            "estimand_process_fidelity": estimand["process_fidelity"],
            "estimand_average_gate_fidelity": estimand["average_gate_fidelity"],
            "estimand_linear_inversion_fidelity": estimand["linear_inversion_fidelity"],
            "sampled_dataset": {key: sampled[key] for key in SAMPLED_KEYS},
            "seed_index": seeds[k][0],
        }
    study = coverage_study(expected_counts(per_setting, COVERAGE_VARIANT), seeds[len(FORECAST_VARIANTS) :])
    return {
        "schema": "qd-cz-tomography-forecast-v2",
        "read": {"path": READ, "sha256": sha256_bytes((FAMILY_DIR / READ).read_bytes()), **figures},
        "samples_per_iteration": SAMPLES_PER_ITERATION,
        "seed_draw": DRAW,
        "interval": INTERVAL_KIND,
        "variants": result,
        "coverage_study": study,
        "settings": [
            {"name": row["name"], **{name: entry[name] for name in FORECAST_VARIANTS}}
            for row, entry in zip(rows, per_setting, strict=True)
        ],
    }


def forecast_bytes() -> bytes:
    return (json.dumps(forecast(), indent=1, sort_keys=True) + "\n").encode()


# ---------------------------------------------------------------- checks


def slos_outcomes(unitary: np.ndarray) -> list[float]:
    """Conditional readout probabilities from Perceval's SLOS backend for indistinguishable photons, postselected on
    one photon per rail pair and none on the ancillas."""
    import perceval as pcvl

    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(unitary)))
    backend.set_input_state(pcvl.BasicState([1, 0, 1, 0, 0, 0]))
    eligible = [0.0] * 4
    for state, probability in backend.prob_distribution().items():
        outcome = outcome_of([1 if state[m] else 0 for m in range(WINDOW)] + [0] * (MODES - WINDOW))
        if outcome is not None:
            eligible[outcome] += float(probability)
    total = sum(eligible)
    return [p / total for p in eligible]


def check_gate() -> None:
    """The CZ block is diag(1, 1, 1, -1) / 3, and equals the Hadamard-conjugated CNOT of the teleportation rehearsal."""
    block = coincidence_block(cz_unitary())
    expected = np.diag([1.0, 1.0, 1.0, -1.0]) / 3
    deviation = float(np.max(np.abs(block - expected)))
    require(
        deviation < BODY_TOLERANCE, f"the CZ coincidence block departs from diag(1, 1, 1, -1) / 3 by {deviation:.2e}"
    )
    from qd_teleportation_rehearsal import cnot_unitary

    hadamard = hadamard_on_target()
    derived = hadamard @ cnot_unitary() @ hadamard
    gap = float(np.max(np.abs(coincidence_block(derived) - expected)))
    require(gap < BODY_TOLERANCE, f"H CNOT H departs from the CZ block by {gap:.2e}")
    require(float(np.max(np.abs(derived - cz_unitary()))) < BODY_TOLERANCE, "H CNOT H is not the catalog CZ unitary")
    gram = float(np.max(np.abs(cz_unitary().conj().T @ cz_unitary() - np.eye(WINDOW))))
    require(gram < BODY_TOLERANCE, f"the CZ unitary is not unitary ({gram:.2e})")


def check_settings() -> None:
    """Every setting's coincidence block is (R x R) CZ/3 (P x P), the exact outcome law is the ideal one, and one
    setting per readout pair agrees with Perceval's SLOS backend."""
    rows = schedule()
    for row in rows:
        unitary = setting_unitary(row)
        prepare = np.kron(preparation(*INPUT_STATES[row["input"][0]]), preparation(*INPUT_STATES[row["input"][1]]))
        read = np.kron(readout(row["basis"][0]), readout(row["basis"][1]))
        composed = read @ (ideal_cz() / 3) @ prepare
        gap = float(np.max(np.abs(coincidence_block(unitary) - composed)))
        require(gap < BODY_TOLERANCE, f"{row['name']}: the coincidence block departs from R CZ/3 P by {gap:.2e}")
        conditional, accepted = exact_outcomes(row)
        require(abs(accepted - 1 / 9) < BODY_TOLERANCE, f"{row['name']}: accepted probability {accepted}")
        gap = max(abs(a - b) for a, b in zip(conditional, ideal_outcomes(row), strict=True))
        require(gap < BODY_TOLERANCE, f"{row['name']}: the permanent law departs from the ideal by {gap:.2e}")
    seen: set[str] = set()
    for row in rows:
        if row["basis"] in seen:
            continue
        seen.add(row["basis"])
        slos = slos_outcomes(setting_unitary(row))
        gap = max(abs(a - b) for a, b in zip(slos, ideal_outcomes(row), strict=True))
        require(gap < BODY_TOLERANCE, f"{row['name']}: SLOS departs from the ideal law by {gap:.2e}")


def check_noise_limit() -> None:
    """The forecast pipeline at perfect indistinguishability, no multiphoton emission, no loss and no dark counts
    reproduces the exact law of a setting, so the forecast's departures from the ideal come from the noise alone."""
    perfect = {"hom": 1.0, "g2": 0.0, "transmittance": 1.0, "clock_mhz": 1.0}
    seen: set[str] = set()
    for row in schedule():
        if row["basis"] in seen:
            continue
        seen.add(row["basis"])
        photons = photon_distribution(setting_unitary(row), perfect["hom"], perfect["g2"])
        clicks = detected_clicks(photons, perfect["transmittance"], [0.0] * MODES)
        eligible = [0.0] * 4
        for pattern, probability in clicks.items():
            outcome = outcome_of(pattern)
            if outcome is not None:
                eligible[outcome] += probability
        total = sum(eligible)
        require(abs(total - 1 / 9) < BODY_TOLERANCE, f"{row['name']}: noiseless eligible probability {total}")
        gap = max(abs(e / total - i) for e, i in zip(eligible, ideal_outcomes(row), strict=True))
        require(gap < BODY_TOLERANCE, f"{row['name']}: the noiseless forecast departs from the ideal by {gap:.2e}")


def check_estimator() -> float:
    """The noiseless frequencies of all 144 settings reproduce the ideal CZ Choi matrix and process fidelity 1."""
    point = estimate(ideal_frequencies())
    require(
        abs(point["process_fidelity"] - 1.0) < BODY_TOLERANCE, f"ideal process fidelity {point['process_fidelity']}"
    )
    require(
        abs(point["linear_inversion_fidelity"] - 1.0) < BODY_TOLERANCE,
        f"ideal linear-inversion fidelity {point['linear_inversion_fidelity']}",
    )
    require(abs(point["average_gate_fidelity"] - 1.0) < BODY_TOLERANCE, "ideal average gate fidelity")
    gram = float(np.max(np.abs(partial_trace_output(point["choi"]) - np.eye(4))))
    require(gram < BODY_TOLERANCE, f"the ideal Choi matrix is not trace preserving ({gram:.2e})")
    return float(point["process_fidelity"])


def check_job(job: str) -> str:
    out = FAMILY_DIR / job
    rebuilt = documents(job)
    require(documents(job) == rebuilt, f"{job}: a second build differs from the first")
    for name, data in rebuilt.items():
        require((out / name).read_bytes() == data, f"{out}/{name} differs from the builder's bytes")
    manifest, circuit, _ = load_case(out)
    experiment, settings = template_experiment(manifest, circuit)
    require(experiment is not None and len(settings) == len(job_rows(job)), f"{job}: the template did not bind")
    require(manifest["compilation_seeds"]["draw"] == DRAW, f"{job}: the manifest names another seed draw")
    require(
        all(setting["compilation_seed"] != 0 and type(setting["compilation_seed"]) is int for setting in settings),
        f"{job}: a compilation seed is zero or not an integer",
    )
    require(len({s["compilation_seed"] for s in settings}) == len(settings), f"{job}: a compilation seed repeats")
    require(manifest["max_samples"] == SAMPLES_PER_ITERATION * len(settings), f"{job}: max_samples")
    require(manifest["max_shots"] == JOB_SHOTS[job] * len(settings), f"{job}: max_shots")
    plan = json.loads((out / "plan-read.json").read_text(encoding="utf-8"))
    require(plan["cases_sha256"] == sha256_bytes((out / "cases.json").read_bytes()), f"{job}: plan-read.json is stale")
    ceiling = PER_JOB_CREDITS + JOB_SHOTS[job] * PRICE_PER_SHOT
    require(abs(plan["credit_ceiling"] - ceiling) < TOLERANCE, f"{job}: the plan's credit ceiling is not {ceiling}")
    return f"{FAMILY}/{job}: {len(settings)} iterations bound, credit ceiling {ceiling:g}"


def check() -> int:
    check_gate()
    check_settings()
    check_noise_limit()
    fidelity = check_estimator()
    window = choose_window(read_perfs())
    require(window == 0, f"the darkest connected window of the retained read starts at chip mode {window}, not 0")
    seeds, bootstrap = seed_plan()
    values = [value for _, value in seeds] + [bootstrap[1]]
    require(len(set(values)) == len(values) and 0 not in values, "a seed repeats or is zero")
    for line in ordered_map(check_job, list(JOBS), min_items=1):
        print(line)
    estimates = json.loads((FAMILY_DIR / ESTIMATE).read_text(encoding="utf-8"))["jobs"]
    for job in JOBS:
        require(estimates[job]["samples"] == SAMPLES_PER_ITERATION, f"{ESTIMATE} predates the sample budget of {job}")
        require(
            estimates[job]["shots_per_iteration"] == JOB_SHOTS[job],
            f"{job}: max_shots per iteration is {JOB_SHOTS[job]}, "
            f"the estimate gives {estimates[job]['shots_per_iteration']}",
        )
    retained = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))
    require(
        retained["read"]["sha256"] == sha256_bytes((FAMILY_DIR / READ).read_bytes()),
        "forecast.json predates the retained platform read",
    )
    require(retained["samples_per_iteration"] == SAMPLES_PER_ITERATION, "forecast.json predates the sample budget")
    require(retained["interval"] == INTERVAL_KIND, "forecast.json was built for another interval type")
    coverage = retained["coverage_study"]["coverage"][INTERVAL_KIND]
    require(coverage >= COVERAGE_FLOOR, f"the {INTERVAL_KIND} interval covers {coverage} of the synthetic datasets")
    print(f"{FAMILY}: 144 settings, ideal process fidelity {fidelity:.12f}")
    return 0


def check_forecast() -> int:
    retained = (FAMILY_DIR / FORECAST).read_bytes()
    require(forecast_bytes() == retained, f"{FORECAST} differs from the recomputed forecast")
    variants = json.loads(retained)["variants"]
    for name, row in variants.items():
        print(
            f"{name}: estimand {row['estimand_process_fidelity']:.4f}, eligible share {row['mean_eligible_share']:.4f}"
        )
    return 0


# ---------------------------------------------------------------- shot estimate


def shot_estimate(job: str) -> dict[str, Any]:
    """Perceval's estimate_required_shots for each iteration's max_samples at the live performance figures.

    The recorder keeps every estimate that payload computes (a read-only platform call: nothing is sent)."""
    from perceval import RemoteComputer

    estimates: list[tuple[int, int | None]] = []
    original = RemoteComputer.estimate_required_shots

    def recorded(self: Any, computation: Any, nsamples: int, param_values: dict[str, float] | None = None) -> Any:
        value = original(self, computation, nsamples, param_values)
        estimates.append((nsamples, value))
        return value

    RemoteComputer.estimate_required_shots = recorded
    manifest, circuit, _ = load_case(FAMILY_DIR / job)
    try:
        payload(FAMILY_DIR / job, manifest, circuit, PLATFORM)
    except PlatformError:
        pass  # an estimate above max_shots stops payload only after the recorder holds it
    finally:
        RemoteComputer.estimate_required_shots = original
    require(len(estimates) == len(manifest["settings"]), f"{len(estimates)} estimates were recorded")
    require(all(value is not None for _, value in estimates), "Perceval estimates no sample of interest")
    values = [int(value) for _, value in estimates if value is not None]
    return {
        "samples": estimates[0][0],
        "smallest": min(values),
        "largest": max(values),
        "mean": sum(values) / len(values),
        "shots_per_iteration": math.ceil(max(values) * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM,
        "inputs": {s["name"]: v for s, v in zip(manifest["settings"], values, strict=True)},
    }


def estimate_command() -> int:
    jobs = {job: shot_estimate(job) for job in JOBS}
    record = {
        "schema": "qd-cz-tomography-shot-estimate-v1",
        "basis": "RemoteComputer.estimate_required_shots under the live perfs of qpu:ascella, per iteration",
        "jobs": jobs,
    }
    (FAMILY_DIR / ESTIMATE).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for job, row in jobs.items():
        print(f"{job}: {row['samples']} samples need up to {row['largest']} shots (cap {JOB_SHOTS[job]})")
    return 0


# ---------------------------------------------------------------- analysis


def parse_state(key: str) -> list[int]:
    return [int(part) for part in key.strip("|>").split(",")]


def eligible_counts(run: Path, manifest: Mapping[str, Any]) -> tuple[dict[str, list[int]], dict[str, int]]:
    """({setting name: four eligible outcome counts}, exclusions by cause) of one collected run."""
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    entries = results.get("iterations") or []
    tallies: dict[str, list[int]] = {}
    excluded = {"three_or_more_clicks": 0, "fewer_than_two_clicks": 0, "two_clicks_off_the_rails": 0}
    for setting, entry in zip(manifest["settings"], entries, strict=False):
        counts = entry.get("counts") if isinstance(entry, dict) else None
        if not counts:
            continue
        tally = [0, 0, 0, 0]
        for key, count in counts.items():
            vector = parse_state(key)
            clicks = [1 if n else 0 for n in vector]
            outcome = outcome_of(clicks)
            if outcome is not None:
                tally[outcome] += count
            elif sum(clicks) > MIN_CLICKS:
                excluded["three_or_more_clicks"] += count
            elif sum(clicks) < MIN_CLICKS:
                excluded["fewer_than_two_clicks"] += count
            else:
                excluded["two_clicks_off_the_rails"] += count
        tallies[setting["name"]] = tally
    return tallies, excluded


def analyze(runs: Sequence[Path], replicates: int = BOOTSTRAP_REPLICATES) -> dict[str, Any]:
    """Pool collected runs: the process estimate when all 144 settings returned eligible events, else counts only."""
    tallies: dict[str, list[int]] = {}
    excluded = {"three_or_more_clicks": 0, "fewer_than_two_clicks": 0, "two_clicks_off_the_rails": 0}
    for run in runs:
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        require(manifest["family"] == FAMILY, f"{run}: not an {FAMILY} run")
        found, lost = eligible_counts(run, manifest)
        tallies.update(found)
        for cause, count in lost.items():
            excluded[cause] += count
    rows = schedule()
    record: dict[str, Any] = {
        "schema": "qd-cz-tomography-analysis-v1",
        "settings_with_counts": len(tallies),
        "settings_expected": len(rows),
        "excluded_by_cause": excluded,
        "eligible_events": sum(sum(t) for t in tallies.values()),
        "eligible_events_by_setting": {name: sum(t) for name, t in tallies.items()},
    }
    complete = len(tallies) == len(rows) and all(sum(tallies[row["name"]]) > 0 for row in rows)
    if not complete:
        record["process"] = "undecided"
        return record
    counts = np.asarray([tallies[row["name"]] for row in rows], dtype=float)
    seed = bootstrap_seed_of(runs[0])
    record["process"] = tomography(counts, np.random.default_rng(seed), replicates)
    record["process"]["bootstrap"]["seed"] = seed
    forecast_row = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))["variants"]
    record["forecast_process_fidelity"] = {name: v["estimand_process_fidelity"] for name, v in forecast_row.items()}
    return record


def bootstrap_seed_of(run: Path) -> int:
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    spec = manifest["preregistered"]["bootstrap"]
    require(spec["seed_draw"] == DRAW, f"{run}: the bootstrap draw is {spec['seed_draw']}")
    _, bootstrap = seed_plan()
    require(spec["seed_index"] == bootstrap[0], f"{run}: the bootstrap index is {spec['seed_index']}")
    return bootstrap[1]


def build() -> int:
    for job in JOBS:
        out = FAMILY_DIR / job
        out.mkdir(parents=True, exist_ok=True)
        for name, data in documents(job).items():
            (out / name).write_bytes(data)
    (FAMILY_DIR / FORECAST).write_bytes(forecast_bytes())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", action="store_true")
    group.add_argument("--forecast", action="store_true")
    group.add_argument("--estimate", action="store_true")
    group.add_argument("--analyze", nargs="+", metavar=("OUT.json", "RUN"))
    args = parser.parse_args()
    if args.build:
        return build()
    if args.forecast:
        return check_forecast()
    if args.estimate:
        return estimate_command()
    if args.analyze:
        out, runs = Path(args.analyze[0]), [Path(r) for r in args.analyze[1:]]
        require(bool(runs), "--analyze OUT.json RUN [RUN ...] needs a run")
        out.write_text(json.dumps(analyze(runs), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
