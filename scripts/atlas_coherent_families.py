"""Fit coherent error families to the Fez and Kingston ripple atlas fringes, on the circuits and times that ran.

Both runs executed the 84 box-kite edges as 8-point phase sweeps (phase
k pi/4) on 7 lanes, each a fixed set of 5 physical qubits shared by its 12
edges: ibm_fez in results/live/2026-10-13T025444.603480Z (observations in
results/ripple/measured-ripple.json) and ibm_kingston in
results/live/2026-10-15T031229.371738Z (observations in its collect.json
family_measurements, each member's marginal required to equal its raw shot
bit strings, ideal probabilities in its record.json). Fitting
a + b cos(phi - phi0) to an edge's 8 points gives a fringe contrast b and
phase phi0. Each edge yields two observables against the execution replay,
whose noise model carries every calibrated incoherent channel and no coherent
term:

- the phase offset, phi0(hardware) - phi0(replay);
- the log contrast ratio, log(b(hardware) / b(replay)). Coherent and
  incoherent contrast loss are taken to multiply, so the ratio isolates the
  coherent factor plus any incoherent loss the calibration omits.

Every phase point is its executed replica, rebuilt from isa.qpy by
atlas_detuning_map.Executed, with each pulse at the start time IBM's
scheduler_timing reported for its PUB. Kingston plays one measurement as
several consecutive play rows; the first row's start is the measurement's.
An edge whose 8 points ran under more than one calibration is excluded from
every fit and listed, since a static per-qubit error is undefined across a
recalibration.

Error families, each entering the replica at its executed times:

- ``detuning``: frame detuning delta_q (kHz), RZ(2 pi delta_q dt) before each
  pulse on q over the interval since its previous pulse start;
- ``cz_phase``: conditional phase epsilon_c (rad), CPhase(epsilon_c) after
  every CZ on coupler c;
- ``zz``: static ZZ rate zeta_c (kHz) on each CZ coupler, the |11> energy
  shift zeta = f11 - f10 - f01 + f00, entering as CPhase(-2 pi zeta_c dt)
  before each pulse on either qubit over the interval since the previous
  pulse start on either. This is the frame of qubit frequencies calibrated
  with the partner in |0>: a partner in |0> leaves the qubit's phase
  unchanged and a partner in |1> detunes it by -zeta_c;
- ``zz_symmetric``: the same rate in the partner-averaged frame,
  RZZ(pi zeta_c dt) over the same intervals, a Hamiltonian
  (2 pi zeta_c / 4) Z Z. RZZ(pi zeta dt) equals CPhase(-2 pi zeta dt) times
  RZ(pi zeta dt) on both qubits up to a global phase, so it is ``zz`` plus a zeta_c/2 frame
  detuning on each qubit of the coupler, and the two families differ only by
  a vector in the detuning span;
- ``sx_amplitude``: drive amplitude error eta_q (fraction), RX(eta_q pi/2)
  after each sx and RX(eta_q pi) after each x on q (one drive scale for both
  pulses);
- ``axis_tilt``: polar tilt beta_q (rad) of the drive axis toward Z,
  RY(-beta_q) R RY(beta_q) for each sx or x pulse R on q, the axis
  cos(beta) X + sin(beta) Z;
- ``drive_phase``: an in-plane axis offset alpha_q, RZ(alpha_q) R RZ(-alpha_q).
  The virtual RZ and CZ gates commute with it, so the inner factors cancel and
  only RZ on |0> and RZ before a Z readout remain: its response is identically
  zero. It is computed as a gauge null and never fitted.

Each parameter is shifted by +h and -h (1 kHz, 0.01 rad, 1 kHz, 1 kHz,
0.01, 0.01 rad), giving the central slope (s+ - s-)/2h and the curvature
(s+ + s-)/2h^2 of the phase and of the log contrast. Detuning and CZ phase
fit on the forward slope s+/h, the definition of the retained
atlas_detuning_map table; the other families fit on the central slope. A
column whose largest phase curvature times h^2 exceeds its largest central
slope times h over the lane's edges has an even phase response: the
parameter shifts the phase only at second order, so no linear model exists
for it, the column is listed and left out of the fit, and its effect enters
the family's reach below. A model with no remaining column, or whose design
falls short of full numerical rank (singular values above 1e-6 of the
largest), is reported unidentified. A column whose slope and curvature both
stay below 1e-12 (a qubit the parameter never reaches) is listed as inert and
left out.

Each lane fits by least squares on the phase responses the lane mean, each
family alone, detuning paired with each other family, and each family with a
lane-constant phase term (``<family>_plus_mean``, which absorbs an offset
shared by every edge of the lane; the constant adds unchanged to the
resimulated shift). The ``_plus_mean`` models and the two ZZ frames widen the
model set, so the smallest score over it is an exploratory selection, never
a confirmed model; a confirming test scores a named model on lanes it was
not selected on. Every model is scored by
leave-one-edge-out RMS error against the shot-noise floor exactly as
atlas_detuning_map.py scores detuning and CZ phase: linearly, and by
resimulating every edge at its fitted (``nonlinear_fit``) and leave-one-out
fitted (``nonlinear_leave_one_out``) values.

The reported gate errors bound the coherent families that act inside a gate.
Taking the whole sx error r as the average infidelity of a coherent error
gives |eta| <= (4/pi) asin(sqrt(3r/2)) and |beta| <= acos(2 sqrt(1 - 3r/2) - 1);
taking the whole CZ error r gives |epsilon| <= acos(1 - 10r/3). Bounds use the
largest error over the calibrations the lane's edges ran under. A family's
reach is the largest phase shift (|slope| B + |curvature| B^2, summed over
its columns) and the largest log-contrast loss (|curvature| B^2) any edge of
the lane shows at those bounds.

The ideal fringe has the maximal contrast b = 1/2, so every coherent error
lowers the contrast at second order and the contrast slope at zero error
vanishes. The contrast is therefore scored by cross-prediction: the
resimulated held-out edge at its leave-one-out phase-fit values predicts its
log contrast ratio with no further parameter, and a held-out constant (the
mean residual over the other edges, each also at its own held-out values)
absorbs uniform incoherent loss.

Falsifiers:

- a family is refuted on a lane when its resimulated leave-one-out phase RMS
  is at or above the lane mean's leave-one-out RMS;
- it accounts for a lane's phase offsets when its linear leave-one-out RMS is
  at most 1.5 times its own leave-one-out noise floor;
- a bounded family cannot account for the offsets when its phase reach at
  the calibration bound is below the RMS of the lane's measured offsets
  (``phase_reach_covers_offset_rms``), and a fit is inconsistent with the
  calibration when a fitted value exceeds its bound;
- its phase-fitted values are refuted by the contrast when the held-out
  contrast residual RMS is at or above the lane mean's leave-one-out contrast
  RMS, and contradicted on an edge when the predicted log ratio lies more
  than 3 standard errors below the measured one (the model predicts more
  contrast loss than the hardware shows).

Self-checks in every run: with no error term each edge's simulated fringe
phase equals the fringe phase of the recorded ideal probabilities within
1e-9 rad; every drive_phase shift stays below 1e-9; on Fez the forward
detuning and CZ-phase slopes equal the retained
docs/evidence/atlas_detuning_map/result.json lane within 1e-9.

``--runs ibm_fez,ibm_kingston`` and ``--lanes all`` (or ``0,4``) select the
work, ``--edges N`` keeps the first N edges of each lane for a reduced case.
Edges are simulated through parallel.ordered_map (GOROROBA_WORKERS caps the
pool). ``--self-test`` runs the reduced contract on Fez lane 4 (6 edges) and
two Kingston edges: the self-checks, recovery of injected detuning, ZZ (both
frames), SX-amplitude and axis-tilt values on their odd columns from the
simulated phase offsets within 10 percent of the largest injected value, for
each even column a phase shift equal to its curvature times the squared
injected value within 10 percent, and the ZZ frame anchor: on a two-qubit
Ramsey fringe of one qubit, a ``zz`` term leaves the fringe phase unchanged
with the partner in |0> and shifts it as a detuning of -zeta with the partner
in |1>, while ``zz_symmetric`` shifts it as detunings of +zeta/2 and -zeta/2.
``--check FILE`` reruns every lane FILE holds (or the ``--runs``/``--lanes``
subset) and requires every number to agree within 1e-6.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import atlas_detuning_map as atlas  # noqa: E402
import ghost_calibrations  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "atlas-coherent-families-v2"
RUNS = {
    "ibm_fez": ROOT / "results/live/2026-10-13T025444.603480Z",
    "ibm_kingston": ROOT / "results/live/2026-10-15T031229.371738Z",
}
RETAINED_DETUNING = ROOT / "docs/evidence/atlas_detuning_map/result.json"
PHASES = atlas.PHASES
LANES = atlas.LANES
VIRTUAL = atlas.VIRTUAL
DRIVEN = {"sx": math.pi / 2, "x": math.pi}
# Family -> parameter unit, step h, per qubit or per coupler, fitted slope, gate-error bound.
FAMILIES: dict[str, dict[str, Any]] = {
    "detuning": {"unit": "kHz", "step": 1.0, "per": "qubit", "slope": "forward", "bound": None},
    "cz_phase": {"unit": "rad", "step": 0.01, "per": "coupler", "slope": "forward", "bound": "cz"},
    "zz": {"unit": "kHz", "step": 1.0, "per": "coupler", "slope": "central", "bound": None},
    "zz_symmetric": {"unit": "kHz", "step": 1.0, "per": "coupler", "slope": "central", "bound": None},
    "sx_amplitude": {"unit": "fraction", "step": 0.01, "per": "qubit", "slope": "central", "bound": "sx"},
    "axis_tilt": {"unit": "rad", "step": 0.01, "per": "qubit", "slope": "central", "bound": "sx"},
    "drive_phase": {"unit": "rad", "step": 0.01, "per": "qubit", "slope": "central", "bound": None},
}
GAUGE = "drive_phase"
# Model -> (families, lane-constant phase term). The models without the
# constant match the retained atlas_detuning_map table; each single family
# also fits with the constant, which absorbs a lane-uniform offset.
SINGLE = ("detuning", "cz_phase", "zz", "zz_symmetric", "sx_amplitude", "axis_tilt")
MODELS: dict[str, tuple[tuple[str, ...], bool]] = {
    "lane_mean": ((), True),
    **{family: ((family,), False) for family in SINGLE},
    "detuning_and_cz_phase": (("detuning", "cz_phase"), False),
    "detuning_and_zz": (("detuning", "zz"), False),
    "detuning_and_zz_symmetric": (("detuning", "zz_symmetric"), False),
    "detuning_and_sx_amplitude": (("detuning", "sx_amplitude"), False),
    "detuning_and_axis_tilt": (("detuning", "axis_tilt"), False),
    **{f"{family}_plus_mean": ((family,), True) for family in SINGLE},
}
INERT = 1e-12
RANK_RTOL = 1e-6
GAUGE_TOLERANCE = 1e-9
REPRODUCTION_TOLERANCE = 1e-9
CHECK_TOLERANCE = 1e-6
CONTRADICTION_SIGMA = 3.0
# A Column names one error parameter: (family, compact qubit index or coupler pair).
Column = tuple[str, Any]
# A Timed replica: compact circuit, per-instruction executed start in seconds
# (nan for virtual gates), per-instruction ordering time, measured qubit, and
# the physical qubit of each compact index.
Timed = tuple[QuantumCircuit, list[float], list[float], int, list[int]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def timed_replica(circuit: QuantumCircuit, rows: list[list[str]], dt: float) -> Timed:
    """The replica on its active qubits with executed pulse starts and a time order.

    Each qubit's play rows, in start order, pair one to one with its
    non-virtual instructions; a measurement consumes every consecutive
    measure row. A virtual gate takes the start of the next pulse on its
    qubit as its ordering time (infinity when none follows), so sorting by
    (time, circuit position) keeps every qubit's own order and places each
    non-diagonal pulse at its executed time relative to the pulses of other
    qubits.
    """
    active = sorted({circuit.find_bit(q).index for inst in circuit.data for q in inst.qubits})
    index = {q: k for k, q in enumerate(active)}
    plays: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        if row[5] != "play" or row[1].startswith(("INIT", "FINI")) or not row[2].startswith("Qubit "):
            continue
        qubit = int(row[2].split()[1])
        if qubit in index:
            plays[qubit].append((int(row[3]), row[1].split("_")[0]))
    for qubit in plays:
        plays[qubit].sort()
    cursor: dict[int, int] = defaultdict(int)
    compact = QuantumCircuit(len(active))
    starts: list[float] = []
    measured = -1
    for inst in circuit.data:
        name = inst.operation.name
        qubits = [circuit.find_bit(q).index for q in inst.qubits]
        if name in VIRTUAL:
            if name == "rz":
                compact.append(inst.operation, [index[q] for q in qubits])
                starts.append(math.nan)
            continue
        times = []
        for q in qubits:
            start, label = plays[q][cursor[q]]
            require(label == name, f"qubit {q}: executed {label} where the circuit has {name}")
            cursor[q] += 1
            if name == "measure":
                while cursor[q] < len(plays[q]) and plays[q][cursor[q]][1] == "measure":
                    cursor[q] += 1
            times.append(start)
        require(len(set(times)) == 1, f"{name} on {qubits} starts at different times {times}")
        if name == "measure":
            require(measured < 0, "replica measures more than one qubit")
            measured = index[qubits[0]]
            continue
        compact.append(inst.operation, [index[q] for q in qubits])
        starts.append(times[0] * dt)
    require(all(cursor[q] == len(plays[q]) for q in plays), "executed pulses remain unpaired")
    require(measured >= 0, "replica has no measurement")
    order = list(starts)
    following: dict[int, float] = {}
    for k in range(len(compact.data) - 1, -1, -1):
        qubits = [compact.find_bit(q).index for q in compact.data[k].qubits]
        if math.isnan(starts[k]):
            order[k] = following.get(qubits[0], math.inf)
        else:
            for q in qubits:
                following[q] = starts[k]
    return compact, starts, order, measured, active


def probability(timed: Timed, errors: dict[Column, float]) -> float:
    """P(measured qubit reads 0) of the replica with the given error parameters at its executed times."""
    compact, starts, order, measured, _ = timed
    by_family: dict[str, dict[Any, float]] = defaultdict(dict)
    for (family, key), value in errors.items():
        if value:
            by_family[family][key] = value
    detuning, cz_phase = by_family["detuning"], by_family["cz_phase"]
    amplitude, tilt, drive = by_family["sx_amplitude"], by_family["axis_tilt"], by_family[GAUGE]
    pairs = [("zz", pair, rate) for pair, rate in by_family["zz"].items()]
    pairs += [("zz_symmetric", pair, rate) for pair, rate in by_family["zz_symmetric"].items()]
    out = QuantumCircuit(compact.num_qubits)
    last: dict[int, float] = {}
    last_pair: dict[tuple[str, tuple[int, int]], float] = {}
    for k in sorted(range(len(compact.data)), key=lambda i: (order[i], i)):
        inst, start = compact.data[k], starts[k]
        name = inst.operation.name
        qubits = [compact.find_bit(q).index for q in inst.qubits]
        if not math.isnan(start):
            for family, pair, rate in pairs:
                if pair[0] in qubits or pair[1] in qubits:
                    if (family, pair) in last_pair:
                        interval = start - last_pair[family, pair]
                        if family == "zz":
                            out.cp(-2 * math.pi * rate * atlas.KHZ * interval, pair[0], pair[1])
                        else:
                            out.rzz(math.pi * rate * atlas.KHZ * interval, pair[0], pair[1])
                    last_pair[family, pair] = start
            for q in qubits:
                if q in last and q in detuning:
                    out.rz(2 * math.pi * detuning[q] * atlas.KHZ * (start - last[q]), q)
                last[q] = start
        driven = name in DRIVEN
        q0 = qubits[0]
        if driven and q0 in drive:
            out.rz(-drive[q0], q0)
        if driven and q0 in tilt:
            out.ry(tilt[q0], q0)
        out.append(inst.operation, qubits)
        if driven and q0 in amplitude:
            out.rx(amplitude[q0] * DRIVEN[name], q0)
        if driven and q0 in tilt:
            out.ry(-tilt[q0], q0)
        if driven and q0 in drive:
            out.rz(drive[q0], q0)
        if name == "cz":
            epsilon = cz_phase.get((min(qubits), max(qubits)), 0.0)
            if epsilon:
                out.cp(epsilon, qubits[0], qubits[1])
    return float(Statevector(out).probabilities([measured])[0])


def fringe_errors(points: list[float], variances: list[float]) -> tuple[float, float]:
    """Standard errors of log b and phi0, each point's variance propagated through the fit's c and s rows."""
    phi = np.arange(PHASES) * math.pi / 4
    design = np.column_stack([np.ones(PHASES), np.cos(phi), np.sin(phi)])
    rows = np.linalg.pinv(design)
    values, var = np.array(points), np.array(variances)
    c, s = rows[1] @ values, rows[2] @ values
    square = c * c + s * s
    log_contrast = (c * rows[1] + s * rows[2]) / square
    phase = (c * rows[2] - s * rows[1]) / square
    return float(math.sqrt(np.sum(np.square(log_contrast) * var))), float(math.sqrt(np.sum(np.square(phase) * var)))


def observables(series: list[dict[str, Any]]) -> dict[str, Any]:
    """Phase offset and log contrast ratio of hardware against replay, with propagated shot noise."""
    hardware = [p["hardware"] for p in series]
    replay = [p["replay"] for p in series]
    hardware_contrast, hardware_phase = atlas.fringe(hardware)
    replay_contrast, replay_phase = atlas.fringe(replay)
    _, ideal_phase = atlas.fringe([p["ideal"] for p in series])
    # live_run samples the execution replay at the run's own shots, so the
    # replay fringe carries binomial noise as the hardware fringe does.
    shots = [p["shots"] for p in series]
    hardware_noise = fringe_errors(hardware, [p * (1 - p) / n for p, n in zip(hardware, shots, strict=True)])
    replay_noise = fringe_errors(replay, [p * (1 - p) / n for p, n in zip(replay, shots, strict=True)])
    return {
        "ideal_phase": ideal_phase,
        "offset": atlas.wrap(hardware_phase - replay_phase),
        "log_contrast_ratio": math.log(hardware_contrast / replay_contrast),
        "phase_noise": math.hypot(hardware_noise[1], replay_noise[1]),
        "contrast_noise": math.hypot(hardware_noise[0], replay_noise[0]),
        "calibrations": sorted({p["calibration"] for p in series}),
    }


Series = dict[tuple[int, int, int, int], list[dict[str, Any]]]


def fez_series() -> Series:
    data = json.loads(atlas.MEASURED.read_text(encoding="utf-8"))
    points: dict[tuple[int, int, int, int], dict[int, dict[str, Any]]] = defaultdict(dict)
    for name, member in data["members"].items():
        match = atlas.MEMBER.match(name)
        if match is None:
            continue
        lane, kite, source, target, phase = (int(group) for group in match.groups())
        counts = member["counts"]
        points[lane, kite, source, target][phase] = {
            "name": name,
            "hardware": counts[0] / sum(counts),
            "shots": sum(counts),
            "replay": member["execution_replay"]["probabilities"][0],
            "ideal": member["ideal_probabilities"][0],
            "calibration": member["execution"]["calibration"],
        }
    return {key: [points[key][p] for p in range(PHASES)] for key in sorted(points)}


def raw_zero_counts(run: Path) -> dict[str, tuple[int, int]]:
    """Shots and zero outcomes of every single-register member, read from the raw shot bit strings."""
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    registers = {
        pub["name"]: {c["member"]: c["registers_by_replica"] for c in pub["components"]}
        for job in record["submission"]["planned_jobs"]
        for pub in job["pubs"]
    }
    counts: dict[str, tuple[int, int]] = {}
    for path in sorted(run.glob("raw/*/pub_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for member, by_replica in registers[data["pub_name"]].items():
            if len(by_replica) == 1 and len(by_replica[0]) == 1:
                bits = data["registers"][by_replica[0][0]]["bitstrings"]
                counts[member] = (len(bits), sum(1 for bit in bits if int(bit, 2) == 0))
    return counts


def kingston_series() -> Series:
    run = RUNS["ibm_kingston"]
    record = json.loads((run / "record.json").read_text(encoding="utf-8"))
    members = {m["name"]: m for g in record["groups"] for m in g["members"]}
    measured = json.loads((run / "collect.json").read_text(encoding="utf-8"))[0]["family_measurements"]
    raw = raw_zero_counts(run)
    points: dict[tuple[int, int, int, int], dict[int, dict[str, Any]]] = defaultdict(dict)
    for name, member in members.items():
        match = atlas.MEMBER.match(name)
        if match is None:
            continue
        lane, kite, source, target, phase = (int(group) for group in match.groups())
        item = measured[name]
        require(item["replay_status"] == "calibration_bound", f"{name}: replay {item['replay_status']}")
        shots = int(item["execution"]["shots"])
        hardware = item["replica_probabilities"][0][0]
        require(raw[name] == (shots, round(hardware * shots)), f"{name}: collected marginal differs from the raw shots")
        points[lane, kite, source, target][phase] = {
            "name": name,
            "hardware": hardware,
            "shots": shots,
            "replay": item["replayed_replica_probabilities"][0][0],
            "ideal": member["ideal"][0],
            "calibration": item["execution"]["calibration"],
        }
    return {key: [points[key][p] for p in range(PHASES)] for key in sorted(points)}


def series_for(backend: str) -> Series:
    return fez_series() if backend == "ibm_fez" else kingston_series()


def columns_for(family: str, width: int, couplers: list[tuple[int, int]]) -> list[Column]:
    if FAMILIES[family]["per"] == "qubit":
        return [(family, q) for q in range(width)]
    return [(family, c) for c in couplers]


def gate_bounds(
    backend: str, calibrations: list[str], physical: list[int], couplers: list[tuple[int, int]]
) -> dict[str, list[float]]:
    """Largest coherent sx-amplitude, axis-tilt and CZ-phase values the reported gate errors allow."""
    sx = [0.0] * len(physical)
    cz = [0.0] * len(couplers)
    for calibration in calibrations:
        path = ghost_calibrations.HISTORY / backend / ghost_calibrations.file_name(calibration)
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        require(snapshot["calibration"] == calibration, f"{path}: calibration {snapshot['calibration']}")
        errors = {tuple(r["qargs"]): r["error"] for op in ("sx", "cz") for r in snapshot["instructions"][op]}
        sx = [max(v, errors[(q,)]) for v, q in zip(sx, physical, strict=True)]
        cz = [max(v, errors[(physical[a], physical[b])]) for v, (a, b) in zip(cz, couplers, strict=True)]
    return {
        "sx_error": sx,
        "cz_error": cz,
        "sx_amplitude": [(4 / math.pi) * math.asin(math.sqrt(1.5 * r)) for r in sx],
        "axis_tilt": [math.acos(2 * math.sqrt(1 - 1.5 * r) - 1) for r in sx],
        "cz_phase": [math.acos(1 - 10 * r / 3) for r in cz],
    }


class EdgeResponse:
    """Zero-error fringe of one edge and its phase and log-contrast shifts at +h and -h of every listed column."""

    def __init__(self, columns: list[Column]) -> None:
        self.columns = columns

    def __call__(self, points: list[Timed]) -> dict[str, Any]:
        def fringe(errors: dict[Column, float]) -> tuple[float, float]:
            return atlas.fringe([probability(timed, errors) for timed in points])

        base_contrast, base_phase = fringe({})
        shifts = []
        for column in self.columns:
            step = FAMILIES[column[0]]["step"]
            row = []
            for sign in (1, -1):
                contrast, phase = fringe({column: sign * step})
                row.extend([atlas.wrap(phase - base_phase), math.log(contrast / base_contrast)])
            shifts.append(row)
        return {"contrast": base_contrast, "phase": base_phase, "shifts": shifts}


class Resimulate:
    """Phase shift and log contrast change of one edge at given error values, against its zero-error fringe."""

    def __call__(self, item: tuple[list[Timed], dict[Column, float], float, float]) -> tuple[float, float]:
        points, errors, base_contrast, base_phase = item
        contrast, phase = atlas.fringe([probability(timed, errors) for timed in points])
        return atlas.wrap(phase - base_phase), math.log(contrast / base_contrast)


def rms(values: Any) -> float:
    return float(math.sqrt(np.mean(np.square(values)))) if len(values) else 0.0


def design_rank(design: np.ndarray) -> tuple[int, float]:
    """Numerical rank (singular values above RANK_RTOL of the largest) and condition number."""
    singular = np.linalg.svd(design, compute_uv=False)
    if not len(singular) or singular[0] == 0:
        return 0, math.inf
    rank = int(np.sum(singular > RANK_RTOL * singular[0]))
    return rank, float(singular[0] / singular[-1]) if singular[-1] > 0 else math.inf


def errors_of(columns: list[Column], values: np.ndarray) -> dict[Column, float]:
    return {column: float(value) for column, value in zip(columns, values, strict=True)}


def responses_of(results: list[dict[str, Any]], families: tuple[str, ...], columns: dict[str, list[Column]]) -> dict:
    """Per family: fitted, central and curvature matrices (edges x columns) for the phase and the log contrast."""
    out: dict[str, dict[str, np.ndarray]] = {}
    start = 0
    for family in families:
        stop = start + len(columns[family])
        step = FAMILIES[family]["step"]
        shifts = np.array([r["shifts"][start:stop] for r in results]).reshape(len(results), stop - start, 4)
        plus_phase, plus_contrast, minus_phase, minus_contrast = (shifts[:, :, k] for k in range(4))
        central = (plus_phase - minus_phase) / (2 * step)
        out[family] = {
            "forward": plus_phase / step,
            "central": central,
            "curvature": (plus_phase + minus_phase) / (2 * step * step),
            "contrast_curvature": (plus_contrast + minus_contrast) / (2 * step * step),
            "contrast_central": (plus_contrast - minus_contrast) / (2 * step),
            "raw_max": np.max(np.abs(shifts)) if shifts.size else np.zeros(()),
        }
        out[family]["fitted"] = out[family][FAMILIES[family]["slope"]]
        start = stop
    return out


def fit_models(
    models: dict[str, tuple[tuple[str, ...], bool]],
    prepared: list[list[Timed]],
    bases: list[dict[str, Any]],
    responses: dict[str, dict[str, np.ndarray]],
    columns: dict[str, list[Column]],
    fitted_columns: dict[str, list[Column]],
    bounds: dict[str, list[float]],
    measured: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Least squares on the phase responses per model, scored on held-out phases and contrasts."""
    n = len(prepared)
    offsets, contrast = measured["offset"], measured["contrast"]
    phase_noise, contrast_noise = measured["phase_noise"], measured["contrast_noise"]
    plans: dict[str, dict[str, Any]] = {}
    items: list[tuple[list[Timed], dict[Column, float], float, float]] = []
    for name, (families, constant) in models.items():
        model_columns = [c for f in families for c in fitted_columns[f]]
        if families and not model_columns:
            plans[name] = {"columns": [], "rank": 0, "condition": math.inf, "constant": constant}
            plans[name]["unidentified"] = "no column has a linear phase response"
            continue
        blocks = [responses[f]["fitted"] for f in families] + ([np.ones((n, 1))] if constant else [])
        design = np.hstack(blocks)
        rank, condition = design_rank(design)
        plan: dict[str, Any] = {
            "design": design,
            "columns": model_columns,
            "rank": rank,
            "condition": condition,
            "constant": constant,
        }
        plans[name] = plan
        if rank < design.shape[1]:
            plan["unidentified"] = f"rank {rank} of {design.shape[1]} columns"
            continue
        plan["parameters"] = np.linalg.lstsq(design, offsets, rcond=None)[0]
        loo, variance, loo_parameters = [], [], []
        for held in range(n):
            keep = [k for k in range(n) if k != held]
            fit = np.linalg.lstsq(design[keep], offsets[keep], rcond=None)[0]
            loo_parameters.append(fit)
            loo.append(offsets[held] - design[held] @ fit)
            # The held-out residual carries the held-out edge's shot noise and
            # the fitted prediction's, propagated from the other edges.
            weights = design[held] @ np.linalg.pinv(design[keep])
            variance.append(phase_noise[held] ** 2 + float(np.sum(np.square(weights) * np.square(phase_noise[keep]))))
        plan["loo"], plan["loo_variance"], plan["loo_parameters"] = loo, variance, loo_parameters
        if families:
            plan["first_item"] = len(items)
            for values in [plan["parameters"]] * n + loo_parameters:
                e = (len(items) - plan["first_item"]) % n
                errors = errors_of(model_columns, values[: len(model_columns)])
                items.append((prepared[e], errors, bases[e]["contrast"], bases[e]["phase"]))
    simulated = parallel.ordered_map(Resimulate(), items, min_items=2)
    out: dict[str, Any] = {}
    for name, plan in plans.items():
        entry: dict[str, Any] = {
            "columns": [[family, key if isinstance(key, int) else list(key)] for family, key in plan["columns"]],
            "lane_constant": plan["constant"],
            "rank": plan["rank"],
            "condition": round(plan["condition"], 3) if math.isfinite(plan["condition"]) else None,
        }
        out[name] = entry
        if "unidentified" in plan:
            entry["unidentified"] = plan["unidentified"]
            continue
        design, parameters = plan["design"], plan["parameters"]
        entry.update(
            {
                "parameters": [round(float(v), 6) for v in parameters],
                "fit_rms_rad": round(rms(offsets - design @ parameters), 6),
                "leave_one_out_rms_rad": round(rms(plan["loo"]), 6),
                "leave_one_out_noise_floor_rad": round(float(math.sqrt(np.mean(plan["loo_variance"]))), 6),
            }
        )
        if any(f in bounds for f, _ in plan["columns"]):
            entry["parameters_exceeding_gate_error_bound"] = [
                [family, key if isinstance(key, int) else list(key)]
                for (family, key), value in zip(plan["columns"], parameters[: len(plan["columns"])], strict=True)
                if family in bounds and abs(value) > bounds[family][columns[family].index((family, key))]
            ]
        predicted = np.zeros(n)
        if "first_item" in plan:
            fitted = simulated[plan["first_item"] : plan["first_item"] + n]
            held_out_sims = simulated[plan["first_item"] + n : plan["first_item"] + 2 * n]
            # The lane constant adds to the resimulated phase shift unchanged.
            fit_constant = parameters[-1] if plan["constant"] else 0.0
            held_constant = [plan["loo_parameters"][e][-1] if plan["constant"] else 0.0 for e in range(n)]
            entry["nonlinear_fit_rms_rad"] = round(
                rms([atlas.wrap(offsets[e] - fitted[e][0] - fit_constant) for e in range(n)]), 6
            )
            entry["nonlinear_leave_one_out_rms_rad"] = round(
                rms([atlas.wrap(offsets[e] - held_out_sims[e][0] - held_constant[e]) for e in range(n)]), 6
            )
            predicted = np.array([held_out_sims[e][1] for e in range(n)])
        residual = contrast - predicted
        held_out = [residual[e] - np.mean(np.delete(residual, e)) for e in range(n)]
        entry["contrast"] = {
            "predicted_log_ratio": [round(float(v), 6) for v in predicted],
            "absolute_rms": round(rms(residual), 6),
            "leave_one_out_rms": round(rms(held_out), 6),
            "contradicted_edges": int(np.sum(predicted < contrast - CONTRADICTION_SIGMA * contrast_noise)),
        }
    floor = [
        contrast_noise[e] ** 2 + float(np.sum(np.square(np.delete(contrast_noise, e)))) / (n - 1) ** 2 for e in range(n)
    ]
    out["lane_mean"]["contrast"]["leave_one_out_noise_floor"] = round(float(math.sqrt(np.mean(floor))), 6)
    return out


def rounded(matrix: np.ndarray) -> list[list[float]]:
    return [[round(float(v), 9) for v in row] for row in matrix]


def lane_fit(
    backend: str,
    lane: int,
    series: Series,
    executed: atlas.Executed,
    edges: int | None,
    retained: dict[str, Any] | None,
    families: tuple[str, ...] = tuple(FAMILIES),
    fit: bool = True,
) -> dict[str, Any]:
    keys = [key for key in series if key[0] == lane][:edges]
    summaries = {key: observables(series[key]) for key in keys}
    excluded = [key for key in keys if len(summaries[key]["calibrations"]) > 1]
    included = [key for key in keys if key not in excluded]
    require(len(included) >= 3, f"{backend} lane {lane}: {len(included)} single-calibration edges")
    prepared = [[timed_replica(*executed.replica(p["name"]), executed.dt) for p in series[key]] for key in included]
    physical = sorted({q for key in keys for p in series[key] for q in executed.physical(p["name"])})
    require(len(physical) == 5, f"{backend} lane {lane} spans {len(physical)} qubits")
    require(
        all(t[4] == physical for points in prepared for t in points), f"{backend} lane {lane}: replica qubits differ"
    )
    width = len(physical)
    couplers: set[tuple[int, int]] = set()
    for points in prepared:
        for timed in points:
            for inst in timed[0].data:
                if inst.operation.name == "cz":
                    pair = [timed[0].find_bit(q).index for q in inst.qubits]
                    couplers.add((min(pair), max(pair)))
    ordered = sorted(couplers)
    columns = {family: columns_for(family, width, ordered) for family in families}
    flat = [c for family in families for c in columns[family]]
    results = parallel.ordered_map(EdgeResponse(flat), prepared, min_items=2)
    responses = responses_of(results, families, columns)
    ideal_mismatch = max(
        abs(atlas.wrap(results[e]["phase"] - summaries[key]["ideal_phase"])) for e, key in enumerate(included)
    )
    require(ideal_mismatch < 1e-9, f"{backend} lane {lane}: replicas miss the ideal fringe by {ideal_mismatch:.2e} rad")
    gauge = None
    if GAUGE in families:
        gauge = float(responses[GAUGE]["raw_max"])
        require(gauge < GAUGE_TOLERANCE, f"{backend} lane {lane}: drive_phase shift {gauge:.2e} is not a gauge null")
    reproduction = None
    if retained is not None:
        rows = len(included)
        require(retained["couplers_compact"] == [list(c) for c in ordered], f"lane {lane}: coupler order differs")
        reproduction = 0.0
        for family, key in (
            ("detuning", "detuning_response_rad_per_khz"),
            ("cz_phase", "cz_phase_response_rad_per_rad"),
        ):
            if family in families:
                difference = np.max(np.abs(responses[family]["forward"] - np.array(retained[key][:rows])))
                reproduction = max(reproduction, float(difference))
        require(
            reproduction < REPRODUCTION_TOLERANCE,
            f"lane {lane}: detuning or CZ slopes differ from the retained map by {reproduction:.2e}",
        )
    calibrations = sorted({c for key in included for c in summaries[key]["calibrations"]})
    bounds_all = gate_bounds(backend, calibrations, physical, ordered)
    bounds = {f: bounds_all[f] for f in families if FAMILIES[f]["bound"] is not None}
    offsets = np.array([summaries[key]["offset"] for key in included])
    offset_rms = rms(offsets)
    family_summary: dict[str, Any] = {}
    fitted_columns: dict[str, list[Column]] = {}
    for family in families:
        if family == GAUGE:
            continue
        r, step = responses[family], FAMILIES[family]["step"]
        odd_part = np.max(np.abs(r["central"]), axis=0) * step
        even_part = np.max(np.abs(r["curvature"]), axis=0) * step * step
        inert = [j for j in range(len(columns[family])) if odd_part[j] < INERT and even_part[j] < INERT]
        odd = [j for j in range(len(columns[family])) if j not in inert and odd_part[j] >= even_part[j]]
        fitted_columns[family] = [columns[family][j] for j in odd]
        r["fitted"] = r["fitted"][:, odd]
        summary: dict[str, Any] = {
            "linear_part_at_step_rad": [round(float(v), 9) for v in odd_part],
            "quadratic_part_at_step_rad": [round(float(v), 9) for v in even_part],
            "even_column_positions": [j for j in range(len(columns[family])) if j not in odd and j not in inert],
            "inert_column_positions": inert,
            "forward_minus_central_max": round(float(np.max(np.abs(r["forward"] - r["central"]))), 9),
            "central_slope": rounded(r["central"]),
            "phase_curvature": rounded(r["curvature"]),
            "contrast_curvature": rounded(r["contrast_curvature"]),
            "contrast_central_slope_max": round(float(np.max(np.abs(r["contrast_central"]))), 9),
        }
        if family in bounds:
            b = np.array(bounds[family])
            reach = np.abs(r["central"]) @ b + np.abs(r["curvature"]) @ np.square(b)
            summary["gate_error_bound"] = [round(float(v), 6) for v in b]
            summary["phase_reach_at_bound_rad"] = round(float(np.max(reach)), 6)
            summary["contrast_reach_at_bound"] = round(float(np.max(np.abs(r["contrast_curvature"]) @ np.square(b))), 6)
            summary["phase_reach_covers_offset_rms"] = bool(np.max(reach) >= offset_rms)
        family_summary[family] = summary
    measured = {
        "offset": offsets,
        "contrast": np.array([summaries[key]["log_contrast_ratio"] for key in included]),
        "phase_noise": np.array([summaries[key]["phase_noise"] for key in included]),
        "contrast_noise": np.array([summaries[key]["contrast_noise"] for key in included]),
    }
    result: dict[str, Any] = {
        "backend": backend,
        "lane": lane,
        "physical_qubits": physical,
        "couplers_compact": [list(c) for c in ordered],
        "calibrations": calibrations,
        "sx_error": [round(v, 9) for v in bounds_all["sx_error"]],
        "cz_error": [round(v, 9) for v in bounds_all["cz_error"]],
        "executed_cz": [int(points[0][0].count_ops().get("cz", 0)) for points in prepared],
        "edges": [{"kite": k[1], "source": k[2], "target": k[3]} for k in included],
        "excluded_edges": [
            {"kite": k[1], "source": k[2], "target": k[3], "calibrations": summaries[k]["calibrations"]}
            for k in excluded
        ],
        "ideal_mismatch_rad": ideal_mismatch,
        "gauge_null_max_shift": gauge,
        "retained_slope_max_difference": reproduction,
        "fitted_slopes": {f: rounded(responses[f]["fitted"]) for f in families if f != GAUGE},
        "fitted_columns": {
            f: [c[1] if isinstance(c[1], int) else list(c[1]) for c in cols] for f, cols in fitted_columns.items()
        },
        "families": family_summary,
        "measured_offset_rad": [round(float(v), 6) for v in measured["offset"]],
        "measured_log_contrast_ratio": [round(float(v), 6) for v in measured["contrast"]],
        "phase_noise_rad": [round(float(v), 6) for v in measured["phase_noise"]],
        "contrast_noise": [round(float(v), 6) for v in measured["contrast_noise"]],
        "offset_rms_rad": round(offset_rms, 6),
        "shot_noise_rms_rad": round(rms(measured["phase_noise"]), 6),
        "contrast_shot_noise_rms": round(rms(measured["contrast_noise"]), 6),
    }
    if fit:
        models = {name: model for name, model in MODELS.items() if set(model[0]) <= set(families)}
        result["models"] = fit_models(models, prepared, results, responses, columns, fitted_columns, bounds, measured)
    return result


def run(backends: list[str], lanes: list[int], edges: int | None) -> dict[str, Any]:
    retained = {fit["lane"]: fit for fit in json.loads(RETAINED_DETUNING.read_text(encoding="utf-8"))["lanes"]}
    fits = []
    for backend in backends:
        series = series_for(backend)
        executed = atlas.Executed(RUNS[backend])
        for lane in lanes:
            fit = lane_fit(backend, lane, series, executed, edges, retained[lane] if backend == "ibm_fez" else None)
            fits.append(fit)
            summary = {
                name: [model.get("leave_one_out_rms_rad"), model.get("nonlinear_leave_one_out_rms_rad")]
                for name, model in fit["models"].items()
            }
            line = {"backend": backend, "lane": lane, "noise": fit["shot_noise_rms_rad"], "loo": summary}
            print(json.dumps(line), flush=True)
    return {
        "schema": SCHEMA,
        "runs": {b: RUNS[b].relative_to(ROOT).as_posix() for b in backends},
        "phases": PHASES,
        "edges_per_lane": edges,
        "families": FAMILIES,
        "models": {
            name: {"families": list(fams), "lane_constant": constant} for name, (fams, constant) in MODELS.items()
        },
        "lanes": fits,
    }


# Injected magnitudes per family: alternating signs, several times below the
# calibration bounds and the shifts the fits report.
INJECTED: dict[str, list[float]] = {
    "detuning": [3.0, -2.0, 4.0, -1.5, 2.5],
    "zz": [2.0, -1.5, 1.0, -2.5],
    "zz_symmetric": [2.0, -1.5, 1.0, -2.5],
    "sx_amplitude": [0.004, -0.003, 0.002, -0.005, 0.003],
    "axis_tilt": [0.004, -0.003, 0.005, -0.002, 0.003],
}
RECOVERY_RTOL = 0.1
# ZZ frame anchor: a Ramsey fringe of qubit 0, sx - RZ(phi) - sx with the
# second sx ANCHOR_SECONDS after the first, beside a partner qubit 1 left in
# |0> or flipped to |1> by an x at the first pulse, under a ZZ rate of
# ANCHOR_KHZ (a 0.63 rad conditional phase over the interval).
ANCHOR_SECONDS = 2e-6
ANCHOR_KHZ = 50.0
ANCHOR_TOLERANCE = 1e-9


def anchor_phase(partner: int, errors: dict[Column, float]) -> float:
    """Fringe phase of the two-qubit Ramsey anchor with the partner prepared in |partner>."""
    probabilities = []
    for k in range(PHASES):
        circuit = QuantumCircuit(2)
        starts: list[float] = []
        if partner:
            circuit.x(1)
            starts.append(0.0)
        circuit.sx(0)
        starts.append(0.0)
        circuit.rz(k * math.pi / 4, 0)
        starts.append(math.nan)
        circuit.sx(0)
        starts.append(ANCHOR_SECONDS)
        order = [ANCHOR_SECONDS if math.isnan(start) else start for start in starts]
        probabilities.append(probability((circuit, starts, order, 0, [0, 1]), errors))
    return atlas.fringe(probabilities)[1]


def zz_frame_anchor() -> None:
    """A partner in |0> leaves the qubit's phase unchanged under zz; zz_symmetric adds a zeta/2 detuning."""
    for partner in (0, 1):
        base = anchor_phase(partner, {})

        def shift(errors: dict[Column, float], base: float = base, partner: int = partner) -> float:
            return atlas.wrap(anchor_phase(partner, errors) - base)

        zz = shift({("zz", (0, 1)): ANCHOR_KHZ})
        symmetric = shift({("zz_symmetric", (0, 1)): ANCHOR_KHZ})
        sign = 1 - 2 * partner
        expected_zz = shift({("detuning", 0): -ANCHOR_KHZ}) if partner else 0.0
        expected_symmetric = shift({("detuning", 0): sign * ANCHOR_KHZ / 2})
        print(
            f"ZZ frame anchor, partner |{partner}>: zz shift {zz:+.6f} rad (expected {expected_zz:+.6f}), "
            f"zz_symmetric shift {symmetric:+.6f} rad (detuning {sign * ANCHOR_KHZ / 2:+.0f} kHz gives "
            f"{expected_symmetric:+.6f})"
        )
        require(abs(zz - expected_zz) < ANCHOR_TOLERANCE, f"zz with the partner in |{partner}> shifts {zz:.3e} rad")
        require(
            abs(symmetric - expected_symmetric) < ANCHOR_TOLERANCE,
            f"zz_symmetric, partner |{partner}>: {symmetric - expected_symmetric:.3e} rad from the detuning",
        )
        require(abs(symmetric) > 0.1, f"zz_symmetric with the partner in |{partner}> leaves the phase unchanged")


def self_test() -> int:
    """Self-checks on Fez lane 4 (6 edges) and two Kingston edges; recovery of injected family values."""
    zz_frame_anchor()
    retained = {fit["lane"]: fit for fit in json.loads(RETAINED_DETUNING.read_text(encoding="utf-8"))["lanes"]}
    series = fez_series()
    executed = atlas.Executed(RUNS["ibm_fez"])
    lane, edges = 4, 6
    fit = lane_fit("ibm_fez", lane, series, executed, edges, retained[lane], fit=False)
    print(
        f"ibm_fez lane {lane}, {edges} edges: ideal mismatch {fit['ideal_mismatch_rad']:.1e} rad, gauge null "
        f"{fit['gauge_null_max_shift']:.1e}, retained slopes within {fit['retained_slope_max_difference']:.1e}"
    )
    keys = [key for key in series if key[0] == lane][:edges]
    prepared = [[timed_replica(*executed.replica(p["name"]), executed.dt) for p in series[key]] for key in keys]
    bases = parallel.ordered_map(EdgeResponse([]), prepared, min_items=2)
    width = len(fit["physical_qubits"])
    couplers = [(a, b) for a, b in fit["couplers_compact"]]
    # Odd columns are injected together and recovered by least squares on
    # their fitted slopes; each even column is injected alone, where its
    # phase shift is the curvature times the squared value.
    probes: list[tuple[str, dict[Column, float], list[int]]] = []
    for family, values in INJECTED.items():
        columns = columns_for(family, width, couplers)
        require(len(columns) == len(values), f"{family}: {len(columns)} columns, {len(values)} injected values")
        keys_fitted = [c if isinstance(c, int) else tuple(c) for c in fit["fitted_columns"][family]]
        odd = [j for j, c in enumerate(columns) if c[1] in keys_fitted]
        require(bool(odd), f"{family}: no column with a linear phase response")
        probes.append((family, {columns[j]: values[j] for j in odd}, odd))
        for j in range(len(columns)):
            if j not in odd:
                probes.append((family, {columns[j]: values[j]}, [j]))
    items = [
        (prepared[e], errors, bases[e]["contrast"], bases[e]["phase"]) for _, errors, _ in probes for e in range(edges)
    ]
    shifted = parallel.ordered_map(Resimulate(), items, min_items=2)
    for k, (family, errors, positions) in enumerate(probes):
        shift = np.array([s[0] for s in shifted[k * edges : (k + 1) * edges]])
        injected = np.array(list(errors.values()))
        if len(positions) > 1 or positions[0] not in fit["families"][family].get("even_column_positions", []):
            slope = np.array(fit["fitted_slopes"][family])
            rank, condition = design_rank(slope)
            require(rank == len(injected), f"{family}: slope rank {rank} of {len(injected)}")
            recovered = np.linalg.lstsq(slope, shift, rcond=None)[0]
            error = float(np.max(np.abs(recovered - injected)))
            print(
                f"{family} columns {positions}: condition {condition:.1f}, injected {injected.tolist()}, "
                f"recovered {np.round(recovered, 4).tolist()}"
            )
            require(error <= RECOVERY_RTOL * float(np.max(np.abs(injected))), f"{family}: recovery error {error:.3g}")
        else:
            curvature = np.array(fit["families"][family]["phase_curvature"])[:, positions[0]]
            quadratic = curvature * injected[0] ** 2
            error = float(np.max(np.abs(shift - quadratic)))
            print(
                f"{family} even column {positions[0]}: largest shift {np.max(np.abs(shift)):.2e} rad, "
                f"curvature prediction within {error:.1e}"
            )
            require(
                error <= RECOVERY_RTOL * float(np.max(np.abs(quadratic))) + 1e-9, f"{family}: shift is not quadratic"
            )
    kingston = kingston_series()
    executed = atlas.Executed(RUNS["ibm_kingston"])
    for key in [k for k in kingston if k[0] == 0][:2]:
        summary = observables(kingston[key])
        points = [timed_replica(*executed.replica(p["name"]), executed.dt) for p in kingston[key]]
        mismatch = abs(atlas.wrap(EdgeResponse([])(points)["phase"] - summary["ideal_phase"]))
        print(f"ibm_kingston edge {key}: ideal mismatch {mismatch:.1e} rad, calibrations {summary['calibrations']}")
        require(mismatch < 1e-9, f"ibm_kingston {key}: replicas miss the ideal fringe by {mismatch:.2e} rad")
    print("self-test passed")
    return 0


def compare(retained: Any, fresh: Any, path: str) -> None:
    if isinstance(retained, dict):
        require(isinstance(fresh, dict) and set(retained) == set(fresh), f"{path}: keys differ")
        for key in retained:
            compare(retained[key], fresh[key], f"{path}.{key}")
    elif isinstance(retained, list):
        require(isinstance(fresh, list) and len(retained) == len(fresh), f"{path}: lengths differ")
        for k, (a, b) in enumerate(zip(retained, fresh, strict=True)):
            compare(a, b, f"{path}[{k}]")
    elif isinstance(retained, float) and isinstance(fresh, (int, float)):
        require(abs(retained - fresh) <= CHECK_TOLERANCE, f"{path}: {retained} against {fresh}")
    else:
        require(retained == fresh, f"{path}: {retained!r} against {fresh!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="ibm_fez,ibm_kingston")
    parser.add_argument("--lanes", default="all")
    parser.add_argument("--edges", type=int)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    backends = args.runs.split(",")
    require(set(backends) <= set(RUNS), f"--runs names a backend outside {sorted(RUNS)}")
    lanes = list(range(LANES)) if args.lanes == "all" else [int(v) for v in args.lanes.split(",")]
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        require(retained.get("schema") == SCHEMA, f"{args.check}: schema {retained.get('schema')}, expected {SCHEMA}")
        named = [(fit["backend"], fit["lane"]) for fit in retained["lanes"]]
        require(len(set(named)) == len(named), f"{args.check}: a lane appears twice")
        selected = [(b, lane) for b, lane in named if b in backends and lane in lanes]
        require(bool(selected), f"{args.check}: holds none of the selected lanes")
        for backend in sorted({b for b, _ in selected}):
            fresh = run([backend], [lane for b, lane in selected if b == backend], retained["edges_per_lane"])
            by_lane = {fit["lane"]: fit for fit in fresh["lanes"]}
            for fit in retained["lanes"]:
                if fit["backend"] == backend and fit["lane"] in by_lane:
                    compare(fit, by_lane[fit["lane"]], f"{backend} lane {fit['lane']}")
        print(f"{args.check}: lanes {selected} reproduced")
        return 0
    require(args.out is not None, "--out is required")
    result = run(backends, lanes, args.edges)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
