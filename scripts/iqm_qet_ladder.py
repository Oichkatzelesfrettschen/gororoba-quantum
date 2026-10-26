"""IQM Garnet case of the phase-compensated QET ladder, its exact noise prediction and its analysis.

gororoba_quantum/qet_ladder.py specifies the arms (compensated_arms), their exact laws over r + 2a + 4b
(compensated_ideal, bob_angle) and the estimator (summarize_compensated); this module lowers each arm to
Garnet's native operations, predicts the laws under the calibration noise model and analyzes a retained run
with that estimator. Alice is the qubit whose X or Z record steers Bob; a circuit packs P disjoint
Alice-Bob pairs, each on a calibrated CZ coupler, with keys alice<p>, afinal<p> and bob<p> per pair p.

Lowering. Every 1q gate factors as RZ(lambda) after prx(theta, phi), and the lambda joins a per-qubit virtual
frame f: a later gate U on the qubit emits prx(theta, phi + f) and then f -= lambda. CZ and Z measurements
commute with frames. The ground-state preparation is RY(2t) on Alice and H CZ H on Bob with Alice's Z a frame
change; Alice's measure carries key and feedback_key; Bob's record-independent rotations are an unconditional
prx and a cc_prx whose condition is Alice's bit. The feedback rule is RY(-phi*) unconditionally and cc_prx RY(+2
phi*); every idle-rule arm carries a cc_prx too, so all arms wait the same feedback delay. cc_prx applies the
default prx when the stored bit is 1 and a wait of equal duration when it is 0
(docs/notes/iqm/docs/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite.md). The idle arms' cc_prx
angle is IDLE_CC_ANGLE = 0; a server refusal of a zero angle surfaces in the garnet:mock acceptance job, and
the build option --idle-cc-angle two-pi switches the arms to IDLE_CC_ANGLE_FALLBACK = 2 pi, the same unitary
up to a global phase. The qualification arms prepare a source qubit in |1> or |0>, measure it with a
feedback_key and apply cc_prx(2 phi*) or cc_prx(pi) to a target read in Z; the ideal P(1) is sin^2(phi*) = 1/10
for |1> and 0 for |0>, and 1 and 0 for pi.

Exactness. --self-test and tests/scripts/test_iqm_qet_ladder.py evolve every lowered arm over the two
feedback branches with Qiskit's RGate and CZ matrices and require the law over r + 2a + 4b to equal
qet_ladder.compensated_ideal to 1e-12, for every arm and every alpha of GARNET_ALPHAS, with the window phase
injected at the preparation barrier and after Alice's readout window; a flipped frame
sign fails it.

Prediction. predict_pair propagates the pair's 4x4 density matrix through the ASAP schedule (Garnet
runs circuit gates as soon as possible, claim iqm-garnet-idle-schedule) with the scripts/iqm_sim.py model:
depolarizing prx from RB (p = 2(1 - F)), depolarizing CZ from interleaved RB (p = 4(1 - F)/3), per-qubit
asymmetric readout, and idle T1/T2 relaxation (T2 capped at 2 T1) between operations, with no sampling and no
seed. Alice's measurement splits the state into the four (recorded bit, true bit) branches; the recorded
bit drives Bob's cc_prx. Calibration values: prx and CZ duration, measure duration and acquisition_delay,
control_delays (290 ns), RB and IRB fidelities, readout errors, T1, T2 and the herald-conditioned initial
excitation (characterization.model.QBn.init_error). Inferences with no calibration value: a measure occupies
its qubit for duration + acquisition_delay and the feedback bit reaches Bob's drive control_delay after that;
Alice's second measure follows the first immediately; no relaxation acts inside a measure window (the readout
errors carry it); a cc_prx of angle 0 is an idle in both branches (no gate error); the initial excitation is
zero after passive reset, whose initialization error the unheralded readout errors carry (measured on QB1
only; the initial_excitation_sensitivity row starts every qubit at the calibrated init_error instead), and
ACTIVE_RESET_INIT_ERROR after one unheralded active-reset cycle; the heralded keep fraction is
HERALD_KEEP_PER_QUBIT per qubit; qubits of different pairs are
independent (no crosstalk, no measurement-induced dephasing of neighbors, no leakage, no coherent phase, no
non-QND readout); per-shot time is SHOT_BASE_SECONDS (PASSIVE_SHOT_SECONDS under passive reset) plus the
circuit beyond one measure window. A cc_prx case runs passive reset: a drive AWG admits one feedback signal
label per segment, and active reset puts a second one on every Bob drive. The
retained idle-schedule case found apparent T1 a median 0.53 of the calibrated value, so the sensitivity
rows rerun the prediction with every idle time scaled by RELAXATION_SENSITIVITY.
T2 is the Ramsey t2_time (the echo time is longer); the calibrated qndness of the readout (0.97 on QB1) is not modeled.

Usage: "$PYTHON" scripts/iqm_qet_ladder.py (build DIR [--calibration-dir D] [--pairs N] [--herald auto|zeros|none]
       [--shots N] [--shot-seconds S] [--idle-cc-angle zero|two-pi] [--reset active|passive] [--max-credits C]
       | check DIR | plan --calibration-dir D
       | predict DIR --calibration-dir D | analyze RUN_DIR --out FILE [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import base64
import functools
import json
import math
import shutil
import sys
import tempfile
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np
from qiskit.circuit.library import CZGate, RGate
from qiskit.quantum_info import Operator, Statevector
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_jobs  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import relaxation as aer_relaxation  # noqa: E402

import qet_ladder as ql  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "qet-compensated-ladder"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
GROUP = ql.COMPENSATED_GROUP_NAME
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
# Each qubit's readout probe line (chip-design-records.json) and the probe lines its drive AWG accepts fast feedback
# from (channel-properties.json fast_feedback_sources); the station refuses a cc_prx whose feedback qubit sits on
# another probe line (garnet:mock job 01a17675-111d-731e-9c6f-2132756f1686: "QB8 does not support fast feedback
# from QB3 (probe line: PL-2). Valid source probe lines are ['PL-3']").
FEEDBACK_FILE = "feedback.json"
TIMING_FILE = "timing.json"
EVIDENCE_CALIBRATION = iqm_sim.EVIDENCE / QC / "calibration"
ANALYSIS_SCHEMA = "iqm-qet-ladder-analysis-v1"

# Rounding of angles in the circuit files and of reals in prediction.json keeps the bytes stable across
# platforms whose libm differ in the last bit; a 1e-14 rad angle moves a law by far less than the 1e-12 check.
ANGLE_DECIMALS = 14
VALUE_DECIMALS = 9
FACTOR_EPS = 1e-12

IDLE_CC_ANGLE = 0.0
IDLE_CC_ANGLE_FALLBACK = 2 * math.pi
QUAL_ARMS = ("qual_src1_phi", "qual_src0_phi", "qual_src1_pi", "qual_src0_pi")

# Credit plan. One Garnet job under MAX_CREDITS at the platform price; collect cancels a run within
# CANCEL_MARGIN of the billed seconds the ceiling buys, and the retained estimates ran up to 1.5 s from the
# runtime, so the shot schedule plus JOB_SECONDS stays PLAN_HEADROOM_SECONDS below them (iqm_jobs).
MAX_CREDITS = {"garnet": 4.0, "garnet:mock": 0.0}
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
PLAN_HEADROOM_SECONDS = 2.0
SHOT_STEP = 100
MOCK_SHOTS = 200
MOCK_JOB = "accept"
JOB = "ladder"
# One active-reset shot of a bare one-measure circuit ran 16.04 to 17.23 us on the retained Garnet jobs
# (results/iqm/runs/*-garnet-*: calibrate 16.04, kernel cancellation 17.23, idle schedule 16.34).
SHOT_BASE_SECONDS = 16.0e-6
# A passive-reset shot of the same bare circuit ran 316.158 us (results/iqm/reset_billing_pilot_analysis.json,
# per_shot_seconds of p-2x2000-passive). The station control limits each drive AWG to one feedback signal
# label per playlist segment, and active reset conditions every qubit's drive on its own readout, so Bob's
# cc_prx from Alice needs passive reset (garnet:mock job 01a17621-1452-701f-8874-ba08a138aec4).
PASSIVE_SHOT_SECONDS = 316.158e-6
# Active reset leaves QB1 at P(1) = 0.068 against 0.0065 passive (results/iqm/reset_billing_pilot_analysis.json).
ACTIVE_RESET_INIT_ERROR = 0.068 - 0.0065
# All-zeros heralding kept 0.920 to 0.936 per qubit on the retained seven-qubit jobs (shots kept ** (1 / 7)).
HERALD_KEEP_PER_QUBIT = 0.93
# Apparent T1 of the idle-schedule case, a median fraction of the calibrated T1 (docs/notes/iqm/README.md).
RELAXATION_SENSITIVITY = 0.53
INIT_ERROR_FIELD = "characterization.model.{q}.init_error:herald=measure.constant:measure=measure.constant"

ENDPOINTS = ("selected_excess", "selected_margin", "unitary_floor", "uncompensated_margin")
# Kingston's pooled values over 14 pairs (results/live/2026-10-25T233207.284563Z/FINDINGS.md).
KINGSTON = {
    "selected_excess": {"measured": 0.107, "half_width": 0.006, "model": 0.129},
    "selected_margin": {"measured": -0.073, "half_width": 0.015, "model": 0.063},
    "unitary_floor": {"measured": 0.177, "half_width": 0.013, "model": 0.063},
    "uncompensated_margin": {"measured": -0.157, "half_width": 0.059, "model": 0.063},
}
Z95 = 1.959963984540054
Z99 = 2.5758293035489004
# Preregistered decision constants (docs/design/iqm-garnet-qet-compensated-ladder.md, H1-H4).
DECISION_LEVEL = 0.95
H3_ANGLE_TOLERANCE = 0.15
H3_SOURCE0_LIMIT = 0.03
H4_PHASE_SCALE = 0.2
# Every phase within this distance of zero lies within half a GARNET_ALPHAS step of a grid point.
COMPENSATION_REACH = 1.05


# ---------------------------------------------------------------------------------------------------------
# Gates and lowering
# ---------------------------------------------------------------------------------------------------------


def rgate(theta: float, phi: float) -> np.ndarray:
    """prx(theta, phi) = exp(-i theta (cos(phi) X + sin(phi) Y) / 2), Qiskit's RGate(theta, phi)."""
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -1j * np.exp(-1j * phi) * s], [-1j * np.exp(1j * phi) * s, c]])


def rz_gate(lam: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * lam), np.exp(0.5j * lam)])


HADAMARD = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
SDG = np.diag([1, -1j])
PAULI_X = np.array([[0, 1], [1, 0]], dtype=complex)
PAULI_Z = np.diag([1.0, -1.0]).astype(complex)
IDENTITY = np.eye(2, dtype=complex)
PAULIS = (IDENTITY, PAULI_X, np.array([[0, -1j], [1j, 0]]), PAULI_Z)


def factor(u: np.ndarray) -> tuple[float, float, float]:
    """(theta, phi, lambda) with u = exp(i g) RZ(lambda) prx(theta, phi), theta in [0, pi]."""
    a00, a01, a10, a11 = u[0, 0], u[0, 1], u[1, 0], u[1, 1]
    c, s = abs(a00), abs(a01)
    theta = 2 * math.atan2(s, c)
    if s < FACTOR_EPS:
        return 0.0, 0.0, float(np.angle(a11) - np.angle(a00))
    if c < FACTOR_EPS:
        return theta, float(-np.angle(a01 / a10) / 2), 0.0
    lam = float(np.angle(a11 / a00))
    return theta, float(np.angle(1j * np.exp(-1j * lam) * a10 / a00)), lam


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def num(value: float) -> float:
    """A JSON real: wrapped angles keep 14 decimals, and -0.0 is 0.0."""
    return round(float(value), ANGLE_DECIMALS) + 0.0


class Pair(NamedTuple):
    number: int
    alice: str
    bob: str
    cz: tuple[str, str]

    def as_dict(self) -> dict[str, Any]:
        return {"index": self.number, "alice": self.alice, "bob": self.bob, "cz": list(self.cz)}


def pair_of(row: Mapping[str, Any]) -> Pair:
    return Pair(int(row["index"]), str(row["alice"]), str(row["bob"]), (str(row["cz"][0]), str(row["cz"][1])))


def op(name: str, locus: Sequence[str], **args: Any) -> dict[str, Any]:
    return {"name": name, "locus": list(locus), "args": args}


class Lowering:
    """Native operations of one pair with a virtual-Z frame per qubit; frame_sign -1 is the mutation of the check."""

    def __init__(self, pair: Pair, frame_sign: float = 1.0) -> None:
        self.pair = pair
        self.ops: list[dict[str, Any]] = []
        self.frame = {pair.alice: 0.0, pair.bob: 0.0}
        self.frame_sign = frame_sign

    def prx(self, qubit: str, angle: float, phase: float) -> None:
        self.ops.append(op("prx", [qubit], angle=num(angle), phase=num(wrap(phase))))

    def unitary(self, qubit: str, u: np.ndarray) -> None:
        theta, phi, lam = factor(u)
        if theta > FACTOR_EPS:
            self.prx(qubit, theta, phi + self.frame[qubit])
        self.frame[qubit] -= self.frame_sign * lam

    def virtual_rz(self, qubit: str, alpha: float) -> None:
        self.frame[qubit] -= self.frame_sign * alpha

    def ry_phase(self, qubit: str) -> float:
        return math.pi / 2 + self.frame[qubit]

    def cz(self) -> None:
        self.ops.append(op("cz", self.pair.cz))

    def barrier(self) -> None:
        self.ops.append(op("barrier", [self.pair.alice, self.pair.bob]))

    def measure(self, qubit: str, key: str, feedback_key: str | None = None) -> None:
        args: dict[str, Any] = {"key": key}
        if feedback_key is not None:
            args["feedback_key"] = feedback_key
        self.ops.append(op("measure", [qubit], **args))

    def cc_prx(self, qubit: str, angle: float, phase: float) -> None:
        index = self.pair.number
        self.ops.append(
            op(
                "cc_prx",
                [qubit],
                angle=num(angle),
                phase=num(wrap(phase)),
                feedback_qubit=self.pair.alice,
                feedback_key=f"fb{index}",
            )
        )


def pair_ladder_ops(
    arm: tuple[str, str, str, str, str, float],
    pair: Pair,
    idle_angle: float = IDLE_CC_ANGLE,
    frame_sign: float = 1.0,
) -> list[dict[str, Any]]:
    """Native operations of one compensated arm (name, prep, Alice basis, Bob rule, Bob basis, alpha)."""
    _, prep, alice_basis, rule, bob_basis, alpha = arm
    low = Lowering(pair, frame_sign)
    a, b, p = pair.alice, pair.bob, pair.number
    if prep == "ground":
        low.unitary(a, rgate(2 * ql.THETA, math.pi / 2))
        low.unitary(b, HADAMARD)
        low.cz()
        low.unitary(b, HADAMARD)
        low.unitary(a, PAULI_Z)
    elif prep == "ones":
        low.unitary(a, PAULI_X)
        low.unitary(b, PAULI_X)
    low.barrier()
    if alice_basis == "x":
        low.unitary(a, HADAMARD)
    low.measure(a, f"alice{p}", f"fb{p}")
    if alpha:
        low.virtual_rz(b, alpha)
    first, second = ql.bob_angle(rule, 0), ql.bob_angle(rule, 1)
    if first is not None and second is not None:
        # The conditional half precedes the unconditional one: under ASAP scheduling a prx listed first would
        # play before Alice's readout, splitting Bob's rotation around the window phase that rz(alpha) undoes.
        # Both halves rotate about the same axis in the same frame, so they commute and the law is unchanged.
        low.cc_prx(b, second - first, low.ry_phase(b))
        low.prx(b, first, low.ry_phase(b))
    else:
        low.cc_prx(b, idle_angle, low.ry_phase(b))
    low.measure(a, f"afinal{p}")
    if bob_basis == "x":
        low.unitary(b, HADAMARD)
    elif bob_basis == "y":
        low.unitary(b, HADAMARD @ SDG)
    low.measure(b, f"bob{p}")
    return low.ops


def pair_qual_ops(arm: str, pair: Pair) -> list[dict[str, Any]]:
    """Source Alice in |1> or |0>, measured with a feedback_key, then cc_prx on Bob read in Z."""
    low = Lowering(pair)
    angle = 2 * ql.PHI_STAR if arm.endswith("_phi") else math.pi
    if arm.startswith("qual_src1"):
        low.prx(pair.alice, math.pi, 0.0)
    low.measure(pair.alice, f"alice{pair.number}", f"fb{pair.number}")
    low.cc_prx(pair.bob, angle, math.pi / 2)
    low.measure(pair.bob, f"bob{pair.number}")
    return low.ops


# Garnet's window phase is unmeasured, so its compensation grid is symmetric about zero: every phase within
# 1.05 rad of zero lies within 0.15 rad of a grid point. qet_ladder.COMPENSATION_ALPHAS spans Kingston's phases.
GARNET_ALPHAS = (-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9)


def compensated_arms() -> tuple[tuple[str, str, str, str, str, float], ...]:
    """qet_ladder.compensated_arms with its feedback arms over GARNET_ALPHAS."""
    kept = [arm for arm in ql.compensated_arms() if arm[3] != "feedback"]
    feedback = [
        (f"fb_{ql._alpha_label(alpha)}_{basis}", "ground", "x", "feedback", basis, alpha)
        for alpha in GARNET_ALPHAS
        for basis in "xz"
    ]
    return (*kept[:4], *feedback, *kept[4:])


def summarize(dist: Mapping[str, np.ndarray]) -> dict[str, float]:
    """qet_ladder.summarize_compensated over GARNET_ALPHAS: the same reference phase, floors and margins."""

    def law(arm: str) -> np.ndarray:
        return np.asarray(dist[f"{GROUP}_{arm}"], dtype=float)

    xx, xy = ql._moments(law("ref_x"))[2], ql._moments(law("ref_y"))[2]
    phase = math.atan2(-xy, -xx)
    floor = ql.H_FIELD * ql._moments(law("za"))[3] - ql.H_FIELD**2 / ql.RADIUS
    s = np.array([ql._moments(law(f"ref_{b}"))[1] for b in "xyz"])
    c = np.array([ql._moments(law(f"ref_{b}"))[2] for b in "xyz"])
    out: dict[str, float] = {"reference_phase": phase, "channel_floor": floor, "unitary_floor": ql.kabsch_floor(s, c)}
    for alpha in GARNET_ALPHAS:
        label = ql._alpha_label(alpha)
        feedback = ql.local_energy(law(f"fb_{label}_z"), law(f"fb_{label}_x"))
        out[f"margin_{label}"] = floor - feedback
        out[f"excess_{label}"] = out["unitary_floor"] - feedback
    selected = min(GARNET_ALPHAS, key=lambda alpha: abs(alpha + phase))
    out["selected_alpha"] = selected
    out["selected_margin"] = out[f"margin_{ql._alpha_label(selected)}"]
    out["selected_excess"] = out[f"excess_{ql._alpha_label(selected)}"]
    out["uncompensated_margin"] = out[f"margin_{ql._alpha_label(0.0)}"]
    zeros, ones = law("cal_00") / law("cal_00").sum(), law("cal_11") / law("cal_11").sum()
    for bit, label in enumerate(("r", "a", "b")):
        mask = [index for index in range(8) if (index >> bit) & 1]
        out[f"assignment_{label}_p1_given_0"] = float(zeros[mask].sum())
        out[f"assignment_{label}_p0_given_1"] = float(1 - ones[mask].sum())
    return out


def arm_table() -> dict[str, tuple[str, str, str, str, str, float]]:
    return {arm[0]: arm for arm in compensated_arms()}


def circuit_ops(arm: str, pairs: Sequence[Pair], idle_angle: float = IDLE_CC_ANGLE) -> list[dict[str, Any]]:
    table = arm_table()
    ops: list[dict[str, Any]] = []
    for pair in pairs:
        ops += pair_qual_ops(arm, pair) if arm in QUAL_ARMS else pair_ladder_ops(table[arm], pair, idle_angle)
    return ops


def circuit_json(arm: str, pairs: Sequence[Pair], idle_angle: float = IDLE_CC_ANGLE) -> dict[str, Any]:
    return {"name": f"{GROUP}_{arm}", "instructions": circuit_ops(arm, pairs, idle_angle)}


def arm_names() -> list[str]:
    return [*arm_table(), *QUAL_ARMS]


# ---------------------------------------------------------------------------------------------------------
# Device: calibration, timing and the ASAP schedule
# ---------------------------------------------------------------------------------------------------------


class Timing(NamedTuple):
    set_id: str
    prx: dict[str, float]
    cz: dict[frozenset[str], float]
    measure: dict[str, tuple[float, float]]
    control: dict[str, float]


def derive_timing(folder: Path) -> dict[str, Any]:
    """timing.json from a calibration folder's set.json: the durations and delays the schedule needs."""
    observation = json.loads((folder / "set.json").read_text(encoding="utf-8"))
    values = {o["dut_field"]: o["value"] for o in observation["observations"] if not o.get("invalid")}
    architecture = json.loads((folder / "dynamic-quantum-architecture.json").read_text(encoding="utf-8"))
    qubits = architecture["qubits"]

    def delay_of(q: str) -> float:
        raw = values[f"gates.cc_prx.prx_composite.{q}.control_delays"]
        return float(np.frombuffer(base64.b64decode(raw["data"]), dtype="<f8").max())

    loci = architecture["gates"]["cz"]["implementations"]["slepian_crf"]["loci"]
    return {
        "calibration_set": architecture["calibration_set_id"],
        "source": "set.json of the calibration set",
        "prx": {q: values[f"gates.prx.drag_crf_sx.{q}.duration"] for q in qubits},
        "cz": {f"{a}__{b}": values[f"gates.cz.slepian_crf.{a}__{b}.duration"] for a, b in loci},
        "measure": {
            q: [
                values[f"gates.measure.constant.{q}.duration"],
                values[f"gates.measure.constant.{q}.acquisition_delay"],
            ]
            for q in qubits
        },
        "control_delay": {q: delay_of(q) for q in qubits},
    }


def prepare_calibration(source: Path, target: Path) -> None:
    """Copy a calibration folder's metrics and architecture and derive timing.json from its set.json; a case's
    own calibration copy, which keeps timing.json in place of set.json, copies it."""
    target.mkdir(parents=True, exist_ok=True)
    for name in CALIBRATION_FILES:
        shutil.copyfile(source / name, target / name)
    if not (source / "set.json").exists() and (source / TIMING_FILE).exists():
        shutil.copyfile(source / TIMING_FILE, target / TIMING_FILE)
        shutil.copyfile(source / FEEDBACK_FILE, target / FEEDBACK_FILE)
        return
    (target / TIMING_FILE).write_text(dump(derive_timing(source)), encoding="utf-8")
    (target / FEEDBACK_FILE).write_text(dump(derive_feedback(source.parent / "artifacts")), encoding="utf-8")


def timing_of(record: Mapping[str, Any]) -> Timing:
    return Timing(
        record["calibration_set"],
        dict(record["prx"]),
        {frozenset(key.split("__")): float(value) for key, value in record["cz"].items()},
        {q: (float(v[0]), float(v[1])) for q, v in record["measure"].items()},
        dict(record["control_delay"]),
    )


class Device(NamedTuple):
    calibration: iqm_sim.Calibration
    timing: Timing
    loci: dict[frozenset[str], tuple[str, str]]
    feedback: dict[str, dict[str, Any]]


def feedback_allowed(device: Device, source: str, target: str) -> bool:
    """Whether target's drive accepts fast feedback from source's readout probe line."""
    return device.feedback[source]["probe_line"] in device.feedback[target]["drive_feedback_sources"]


def derive_feedback(artifacts: Path) -> dict[str, dict[str, Any]]:
    """{qubit: probe_line, drive_feedback_sources} from a snapshot's chip design record and channel properties."""
    design = json.loads((artifacts / "chip-design-records.json").read_text(encoding="utf-8"))
    channels = json.loads((artifacts / "channel-properties.json").read_text(encoding="utf-8"))

    def components(node: Any) -> Any:
        if isinstance(node, dict):
            if "components" in node:
                return node["components"]
            for value in node.values():
                found = components(value)
                if found is not None:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = components(value)
                if found is not None:
                    return found
        return None

    found = components(design)
    if found is None:
        raise ValueError(f"{artifacts}: the chip design record lists no components")
    out: dict[str, dict[str, Any]] = {}
    for qubit in found["qubit"]:
        lines = [c for c in qubit["connections"] if c.startswith("PL-")]
        if len(lines) != 1:
            raise ValueError(f"{qubit['name']}: {len(lines)} probe lines")
        sources = channels.get(f"{qubit['name']}__drive.awg", {}).get("fast_feedback_sources")
        if sources is None:
            raise ValueError(f"{qubit['name']}: the channel properties state no drive fast_feedback_sources")
        out[qubit["name"]] = {
            "probe_line": lines[0],
            "drive_feedback_sources": sorted(s.split("__")[0] for s in sources),
        }
    return dict(sorted(out.items(), key=lambda kv: qubit_number(kv[0])))


@functools.lru_cache(maxsize=8)
def load_device(folder: str) -> Device:
    path = Path(folder)
    calibration = iqm_sim.Calibration.from_directory(path)
    architecture = json.loads((path / "dynamic-quantum-architecture.json").read_text(encoding="utf-8"))
    loci = {frozenset((a, b)): (a, b) for a, b in architecture["gates"]["cz"]["implementations"]["slepian_crf"]["loci"]}
    timing = timing_of(json.loads((path / TIMING_FILE).read_text(encoding="utf-8")))
    if timing.set_id != calibration.set_id:
        raise ValueError(f"{path}: timing.json describes set {timing.set_id}, the architecture is {calibration.set_id}")
    feedback = json.loads((path / FEEDBACK_FILE).read_text(encoding="utf-8"))
    return Device(calibration, timing, loci, feedback)


def schedule(ops: Sequence[Mapping[str, Any]], timing: Timing) -> tuple[list[float], list[float]]:
    """ASAP start and end of each operation: a qubit's next operation starts when its last one ends, a CZ and a
    barrier when every qubit they touch is free, and a cc_prx also control_delay after the bit's measure box
    (measure duration + acquisition_delay) ends."""
    cursor: dict[str, float] = {}
    ready: dict[str, float] = {}
    starts: list[float] = []
    ends: list[float] = []
    for item in ops:
        name, locus, args = item["name"], item["locus"], item["args"]
        start = max(cursor.get(q, 0.0) for q in locus)
        if name == "prx":
            end = start + timing.prx[locus[0]]
        elif name == "cz":
            end = start + timing.cz[frozenset(locus)]
        elif name == "barrier":
            end = start
        elif name == "measure":
            duration, acquisition = timing.measure[locus[0]]
            end = start + duration + acquisition
            if "feedback_key" in args:
                ready[args["feedback_key"]] = end
        elif name == "cc_prx":
            start = max(start, ready[args["feedback_key"]] + timing.control[locus[0]])
            end = start + timing.prx[locus[0]]
        else:
            raise ValueError(f"{name} is not scheduled")
        for q in locus:
            cursor[q] = end
        starts.append(start)
        ends.append(end)
    return starts, ends


def circuit_seconds(ops: Sequence[Mapping[str, Any]], timing: Timing) -> float:
    return max(schedule(ops, timing)[1])


# ---------------------------------------------------------------------------------------------------------
# Exact density-matrix prediction
# ---------------------------------------------------------------------------------------------------------


class Noise(NamedTuple):
    """Per-qubit and per-coupler noise of one pair; ideal() has none."""

    prx_p: dict[str, float]
    cz_p: float
    t1: dict[str, float]
    t2: dict[str, float]
    init: dict[str, float]
    readout: dict[str, tuple[float, float]]

    @staticmethod
    def ideal(pair: Pair) -> Noise:
        q = (pair.alice, pair.bob)
        return Noise(
            dict.fromkeys(q, 0.0),
            0.0,
            dict.fromkeys(q, math.inf),
            dict.fromkeys(q, math.inf),
            dict.fromkeys(q, 0.0),
            dict.fromkeys(q, (0.0, 0.0)),
        )


def noise_of(
    device: Device, pair: Pair, herald: bool, scale: float = 1.0, passive: bool = False, excited: bool = False
) -> Noise:
    """The pair's noise; idle T1 and T2 scale by scale. The initial excitation is the herald-conditioned
    calibration value when herald, zero after passive reset (the unheralded readout errors carry the
    initialization error: the passive pilot read QB1 at P(1) 0.0065 against 0.0046 predicted from them), and
    ACTIVE_RESET_INIT_ERROR after one active-reset cycle otherwise; excited starts a passive reset at the
    calibrated herald-conditioned init_error instead, the sensitivity row for an excitation the gates propagate."""
    cal = device.calibration
    qubits = (pair.alice, pair.bob)
    t1 = {q: float(cal.values[f"characterization.model.{q}.t1_time"]) for q in qubits}
    t2 = {q: min(float(cal.values[f"characterization.model.{q}.t2_time"]), 2 * t1[q]) for q in qubits}
    init = {
        q: float(cal.values[INIT_ERROR_FIELD.format(q=q)])
        if herald or (passive and excited)
        else 0.0
        if passive
        else ACTIVE_RESET_INIT_ERROR
        for q in qubits
    }
    return Noise(
        {q: cal.prx_p(q) for q in qubits},
        4 * (1 - cal.cz[frozenset(qubits)]) / 3,
        {q: t1[q] * scale for q in qubits},
        {q: t2[q] * scale for q in qubits},
        init,
        {q: cal.readout(q, herald) for q in qubits},
    )


def _embed(matrix: np.ndarray, which: int, n: int) -> np.ndarray:
    if n == 1:
        return matrix
    return np.kron(matrix, IDENTITY) if which == 0 else np.kron(IDENTITY, matrix)


def _kraus(rho: np.ndarray, operators: Sequence[np.ndarray], which: int, n: int) -> np.ndarray:
    out = np.zeros_like(rho)
    for k in operators:
        full = _embed(k, which, n)
        out = out + full @ rho @ full.conj().T
    return out


def relaxation_kraus(t: float, t1: float, t2: float) -> list[np.ndarray]:
    """Amplitude damping gamma = 1 - exp(-t/T1) then phase damping to the coherence exp(-t/T2) (T2 <= 2 T1)."""
    gamma = 1 - math.exp(-t / t1)
    coherence = math.exp(-t / t2) / math.sqrt(1 - gamma) if gamma < 1 else 0.0
    flip = (1 - min(coherence, 1.0)) / 2
    k0 = np.array([[1, 0], [0, math.sqrt(1 - gamma)]], dtype=complex)
    k1 = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    out = []
    for k in (k0, k1):
        out.append(math.sqrt(1 - flip) * k)
        out.append(math.sqrt(flip) * (PAULI_Z @ k))
    return out


def confusion(readout: tuple[float, float]) -> np.ndarray:
    """C[observed][true] from (P(read 1 | 0), P(read 0 | 1))."""
    e01, e10 = readout
    return np.array([[1 - e01, e10], [e01, 1 - e10]])


class PairState:
    """The pair's state: a 4x4 density matrix (Alice, Bob) until Alice's feedback measure, then one 2x2 Bob
    state per (recorded bit r, true bit m) with its probability as the trace."""

    def __init__(self, pair: Pair, noise: Noise) -> None:
        self.pair, self.noise = pair, noise
        pa, pb = noise.init[pair.alice], noise.init[pair.bob]
        self.rho = np.kron(np.diag([1 - pa, pa]), np.diag([1 - pb, pb])).astype(complex)
        self.branches: dict[tuple[int, int], np.ndarray] | None = None
        self.last = dict.fromkeys((pair.alice, pair.bob), 0.0)

    def _which(self, qubit: str) -> int:
        return 0 if qubit == self.pair.alice else 1

    def _apply(self, kraus: Sequence[np.ndarray], qubit: str) -> None:
        if self.branches is None:
            self.rho = _kraus(self.rho, kraus, self._which(qubit), 2)
        elif qubit == self.pair.bob:
            self.branches = {k: _kraus(v, kraus, 0, 1) for k, v in self.branches.items()}
        else:
            raise ValueError("an Alice operation after her feedback measure has no model")

    def idle(self, qubit: str, until: float) -> None:
        t = until - self.last[qubit]
        t1, t2 = self.noise.t1[qubit], self.noise.t2[qubit]
        if t > 0 and math.isfinite(t1):
            self._apply(relaxation_kraus(t, t1, t2), qubit)
        self.last[qubit] = max(until, self.last[qubit])

    def depolarize(self, qubit: str, p: float) -> None:
        if p > 0:
            self._apply([math.sqrt(1 - 3 * p / 4) * IDENTITY, *(math.sqrt(p / 4) * m for m in PAULIS[1:])], qubit)

    def prx(self, qubit: str, angle: float, phase: float, p: float) -> None:
        self._apply([rgate(angle, phase)], qubit)
        self.depolarize(qubit, p)

    def unitary_only(self, qubit: str, u: np.ndarray) -> None:
        self._apply([u], qubit)

    def cz(self, p: float) -> None:
        if self.branches is not None:
            raise ValueError("a CZ after Alice's feedback measure has no model")
        self.rho = np.diag([1, 1, 1, -1]) @ self.rho @ np.diag([1, 1, 1, -1])
        self.rho = (1 - p) * self.rho + p * np.trace(self.rho) * np.eye(4) / 4

    def split(self, c_alice: np.ndarray) -> None:
        """Alice's measure: true bit m with probability from rho, recorded bit r with P(r | m) = c_alice[r][m]."""
        blocks = self.rho.reshape(2, 2, 2, 2)
        self.branches = {(r, m): c_alice[r][m] * blocks[m, :, m, :] for r in (0, 1) for m in (0, 1)}

    def conditional_prx(self, qubit: str, angle: float, phase: float, p: float, duration: float) -> None:
        """cc_prx on Bob: the prx where the recorded bit is 1, a wait of equal duration where it is 0; at angle 0 the
        pulse is an idle too, so both branches take the wait's relaxation."""
        if self.branches is None:
            raise ValueError("cc_prx precedes the feedback measure")
        kraus_wait = relaxation_kraus(duration, self.noise.t1[qubit], self.noise.t2[qubit])
        gate = [rgate(angle, phase)]
        depolarizing = [math.sqrt(1 - 3 * p / 4) * IDENTITY, *(math.sqrt(p / 4) * m for m in PAULIS[1:])]
        out = {}
        for (r, m), sigma in self.branches.items():
            if r == 1 and angle != 0.0:
                moved = _kraus(sigma, gate, 0, 1)
                out[(r, m)] = _kraus(moved, depolarizing, 0, 1) if p > 0 else moved
            elif math.isfinite(self.noise.t1[qubit]):
                out[(r, m)] = _kraus(sigma, kraus_wait, 0, 1)
            else:
                out[(r, m)] = sigma
        self.branches = out

    def outcome(self, c_alice: np.ndarray, c_bob: np.ndarray, with_final: bool) -> np.ndarray:
        """Probabilities over (r, [a,] b): a is Alice's second reading of her true bit m."""
        if self.branches is None:
            raise ValueError("no feedback measure preceded the readout")
        out = np.zeros((2, 2, 2) if with_final else (2, 2))
        for (r, m), sigma in self.branches.items():
            true_b = np.array([sigma[0, 0].real, sigma[1, 1].real])
            observed_b = c_bob @ true_b
            if with_final:
                for a in (0, 1):
                    out[r, a, :] += c_alice[a][m] * observed_b
            else:
                out[r, :] += observed_b
        return out


def simulate_pair(
    ops: Sequence[Mapping[str, Any]],
    pair: Pair,
    timing: Timing,
    noise: Noise,
    window_phase: float = 0.0,
    window_at: str = "barrier",
) -> np.ndarray:
    """Exact joint law of the pair's measured bits (r, [a,] b) for its operations, ASAP-scheduled; a nonzero
    window_phase is a physical rz on Bob, the coherent phase the alpha grid undoes, applied at the preparation
    barrier or (window_at="feedback") just before Bob's cc_prx, after Alice's readout window."""
    starts, ends = schedule(ops, timing)
    state = PairState(pair, noise)
    alice = pair.alice
    c = {q: confusion(noise.readout[q]) for q in (alice, pair.bob)}
    with_final = sum(item["name"] == "measure" for item in ops) == 3
    for item, start, end in zip(ops, starts, ends, strict=True):
        name, locus, args = item["name"], item["locus"], item["args"]
        for q in locus:
            if state.branches is None or q != alice:
                state.idle(q, start)
        if name == "prx":
            state.prx(locus[0], args["angle"], args["phase"], noise.prx_p[locus[0]])
        elif name == "cz":
            state.cz(noise.cz_p)
        elif name == "measure" and locus[0] == alice and state.branches is None:
            state.split(c[alice])
        elif name == "cc_prx":
            if window_phase and window_at == "feedback":
                state.unitary_only(pair.bob, rz_gate(window_phase))
            pulsed = noise.prx_p[locus[0]] if args["angle"] != 0.0 else 0.0
            state.conditional_prx(locus[0], args["angle"], args["phase"], pulsed, end - start)
        elif name == "barrier" and window_phase and window_at == "barrier":
            state.unitary_only(pair.bob, rz_gate(window_phase))
        elif name not in ("barrier", "measure"):
            raise ValueError(f"{name} has no model")
        for q in locus:
            state.last[q] = max(state.last[q], end)
    return state.outcome(c[alice], c[pair.bob], with_final)


def flat_law(joint: np.ndarray) -> list[float]:
    """The ladder's law over r + 2a + 4b from the joint array indexed [r, a, b]."""
    return [float(joint[r, a, b]) for b in (0, 1) for a in (0, 1) for r in (0, 1)]


def pair_arm_ops(arm: str, pair: Pair, idle_angle: float = IDLE_CC_ANGLE) -> list[dict[str, Any]]:
    return pair_qual_ops(arm, pair) if arm in QUAL_ARMS else pair_ladder_ops(arm_table()[arm], pair, idle_angle)


def dist_of(laws: Mapping[str, Sequence[float] | np.ndarray]) -> dict[str, np.ndarray]:
    return {f"{GROUP}_{name}": np.asarray(laws[name], dtype=float) for name in arm_table()}


def endpoint_variance(dist: Mapping[str, np.ndarray], shots: float | Mapping[str, float] = 1.0) -> dict[str, float]:
    """Shot-noise variance of ENDPOINTS from each arm's multinomial law at shots per arm (delta method).

    Every endpoint is a function of the normalized laws, so Var = sum_arm (sum_i p_i g_i^2 - (sum_i p_i g_i)^2) /
    shots with g_i the central difference of the endpoint in cell i of that arm's law; shots is one count for
    every arm or a count per dist key.
    """
    variance = dict.fromkeys(ENDPOINTS, 0.0)
    step = 1e-6
    table = arm_table()
    alphas = {0.0, summarize(dist)["selected_alpha"]}
    for key, law in dist.items():
        _, prep, _, rule, _, alpha = table[key[len(GROUP) + 1 :]]
        # The calibration arms feed only the assignment fields and a feedback arm only the margins at its own
        # alpha, so every other arm has a zero gradient in ENDPOINTS.
        if prep != "ground" or (rule == "feedback" and alpha not in alphas):
            continue
        p = law / law.sum()
        grads = {name: np.zeros(len(law)) for name in ENDPOINTS}
        for i in range(len(law)):
            if p[i] <= 0:
                continue
            low = min(step, float(law[i]))
            up_law, down_law = np.array(law, dtype=float), np.array(law, dtype=float)
            up_law[i] += step
            down_law[i] -= low
            up = summarize({**dist, key: up_law})
            down = summarize({**dist, key: down_law})
            for name in ENDPOINTS:
                grads[name][i] = (up[name] - down[name]) / (step + low)
        for name in ENDPOINTS:
            g = grads[name]
            n = shots[key] if isinstance(shots, Mapping) else shots
            variance[name] += float(p @ (g * g) - (p @ g) ** 2) / n
    return variance


def predict_pair(item: tuple[Any, ...]) -> dict[str, Any]:
    """Every arm's exact law for one pair under a calibration folder, and the endpoints with their variance
    at one shot per arm. item = (folder, pair, herald, relaxation scale, idle cc_prx angle, passive reset[,
    excited passive start])."""
    folder, row, herald, scale, idle_angle, passive, *rest = item
    device = load_device(folder)
    pair = pair_of(row)
    noise = noise_of(device, pair, herald, scale, passive, bool(rest and rest[0]))
    laws: dict[str, list[float]] = {}
    qual: dict[str, list[float]] = {}
    for arm in arm_names():
        joint = simulate_pair(pair_arm_ops(arm, pair, idle_angle), pair, device.timing, noise)
        if arm in QUAL_ARMS:
            qual[arm] = [float(joint[:, 1].sum()), float(joint[1, :].sum())]
        else:
            laws[arm] = flat_law(joint)
    dist = dist_of(laws)
    return {
        "pair": pair.as_dict(),
        "laws": laws,
        "qualification": qual,
        "endpoints": summarize(dist),
        "variance_one_shot": endpoint_variance(dist),
    }


# ---------------------------------------------------------------------------------------------------------
# Pair selection, shots and cost
# ---------------------------------------------------------------------------------------------------------


def induced_matchings(
    edges: Sequence[tuple[str, str]], couplers: Sequence[tuple[str, str]] | None = None
) -> Iterator[tuple[int, ...]]:
    """Every nonempty set of edges, as index tuples, that share no qubit and whose qubits share no coupler of
    couplers (default: the edges themselves), so a subset of the device's couplers still sees every coupler."""
    couplers_set = {frozenset(edge) for edge in (edges if couplers is None else couplers)}

    def conflict(i: int, j: int) -> bool:
        if set(edges[i]) & set(edges[j]):
            return True
        return any(frozenset((u, v)) in couplers_set for u in edges[i] for v in edges[j])

    clash = [[conflict(i, j) for j in range(len(edges))] for i in range(len(edges))]

    def extend(chosen: tuple[int, ...], start: int) -> Iterator[tuple[int, ...]]:
        for i in range(start, len(edges)):
            if all(not clash[i][j] for j in chosen):
                grown = (*chosen, i)
                yield grown
                yield from extend(grown, i + 1)

    yield from extend((), 0)


def qubit_number(name: str) -> int:
    return int(name[2:])


def measure_window(device: Device, pairs: Sequence[Pair]) -> float:
    return max(sum(device.timing.measure[q]) for p in pairs for q in (p.alice, p.bob))


def shot_seconds_of(
    device: Device, pairs: Sequence[Pair], herald: bool, idle_angle: float, passive: bool = False
) -> float:
    """Seconds per shot: the retained bare-circuit shot under the reset mode plus the circuit beyond one measure
    window, and one more window for the herald measurement."""
    window = measure_window(device, pairs)
    longest = max(circuit_seconds(circuit_ops(arm, pairs, idle_angle), device.timing) for arm in arm_names())
    base = PASSIVE_SHOT_SECONDS if passive else SHOT_BASE_SECONDS
    return base + longest - window + (window if herald else 0.0)


def plan_seconds(credits: float) -> float:
    return credits / PRICE[QC] - PLAN_HEADROOM_SECONDS


def shots_for(shot_seconds: float, circuits: int, credits: float) -> int:
    """The largest multiple of SHOT_STEP that keeps JOB_SECONDS plus the shot schedule within the plan."""
    shots = math.floor((plan_seconds(credits) - JOB_SECONDS) / (circuits * shot_seconds) / SHOT_STEP) * SHOT_STEP
    return min(shots, 20000)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def pooled(results: Sequence[Mapping[str, Any]], kept: float) -> dict[str, dict[str, float]]:
    """Mean of each endpoint over the pairs and its shot-noise standard error at kept shots per arm."""
    out = {}
    for name in ENDPOINTS:
        values = [r["endpoints"][name] for r in results]
        variance = sum(r["variance_one_shot"][name] for r in results)
        out[name] = {"mean": mean(values), "shot_se": math.sqrt(variance / kept) / len(results)}
    return out


def plan(
    folder: str,
    herald_option: str,
    pairs_option: int | None,
    scale: float,
    idle_angle: float,
    passive: bool = False,
    credits: float = MAX_CREDITS[QC],
) -> dict[str, Any]:
    """Select pairs, P and heralding from the calibration at folder; passive reset admits no herald.

    Each coupler takes the orientation of the larger predicted selected margin. For each size P the induced
    matching of the largest mean margin is scored by its pooled shot-noise standard errors at the shots its
    time budget allows (kept shots times HERALD_KEEP_PER_QUBIT ** 2P when heralded). The size minimizes the
    standard error of the pooled selected margin, and the heralding mode maximizes the pooled margin over that
    standard error, the margin being the endpoint Kingston failed.
    """
    device = load_device(folder)
    loci = sorted(device.loci.values(), key=lambda e: (qubit_number(e[0]), qubit_number(e[1])))
    options = {"auto": [True, False], "zeros": [True], "none": [False]}[herald_option]
    if passive:
        if True in options and herald_option == "zeros":
            raise ValueError("passive reset runs unheralded")
        options = [False]
    rows: dict[bool, list[dict[str, Any]]] = {}
    for herald in options:
        items = [
            (folder, Pair(0, a, b, locus).as_dict(), herald, scale, idle_angle, passive)
            for locus in loci
            for a, b in (locus, locus[::-1])
        ]
        # One exact prediction per coupler orientation is CPU-heavy, and Garnet has 30 couplers: pool from 2 items.
        results = ordered_map(predict_pair, items, min_items=2)
        # Each coupler takes its better orientation among those whose Alice the Bob drive accepts fast feedback from;
        # a coupler with neither orientation allowed is left out of every matching.
        best: list[dict[str, Any]] = []
        usable: list[int] = []
        for k, locus in enumerate(loci):
            allowed = [
                results[2 * k + j] for j, (a, b) in enumerate((locus, locus[::-1])) if feedback_allowed(device, a, b)
            ]
            best.append(max(allowed, key=lambda r: r["endpoints"]["selected_margin"]) if allowed else results[2 * k])
            if allowed:
                usable.append(k)
        top: dict[int, tuple[float, tuple[int, ...]]] = {}
        for local in induced_matchings([loci[k] for k in usable], loci):
            chosen = tuple(usable[i] for i in local)
            score = sum(best[i]["endpoints"]["selected_margin"] for i in chosen)
            size = len(chosen)
            if size not in top or score > top[size][0] + 1e-12:
                top[size] = (score, chosen)
        table = []
        for size in sorted(top):
            if pairs_option is not None and size != pairs_option:
                continue
            members = sorted(top[size][1], key=lambda i: qubit_number(best[i]["pair"]["alice"]))
            chosen_pairs = []
            for index, i in enumerate(members):
                row = dict(best[i]["pair"])
                row["index"] = index
                chosen_pairs.append(pair_of(row))
            shot_seconds = shot_seconds_of(device, chosen_pairs, herald, idle_angle, passive)
            shots = shots_for(shot_seconds, len(arm_names()), credits)
            kept = shots * (HERALD_KEEP_PER_QUBIT ** (2 * size) if herald else 1.0)
            results_for = [best[i] for i in members]
            table.append(
                {
                    "herald": herald,
                    "pairs": [p.as_dict() for p in chosen_pairs],
                    "size": size,
                    "shot_seconds": shot_seconds,
                    "shots": shots,
                    "kept_shots": kept,
                    "pooled": pooled(results_for, kept),
                    "members": results_for,
                }
            )
        rows[herald] = table
    all_rows = [row for herald in options for row in rows[herald]]
    if not all_rows:
        raise ValueError(f"no induced matching of {pairs_option} pairs exists")

    def precision(row: dict[str, Any]) -> float:
        return float(row["pooled"]["selected_margin"]["shot_se"])

    def detectability(row: dict[str, Any]) -> float:
        p = row["pooled"]["selected_margin"]
        return float(p["mean"] / p["shot_se"])

    best_by_mode = {h: min(rows[h], key=precision) for h in options if rows[h]}
    mode = max(best_by_mode, key=lambda h: detectability(best_by_mode[h]))
    return {"chosen": best_by_mode[mode], "by_herald": best_by_mode, "table": all_rows}


def rounded(value: Any) -> Any:
    if isinstance(value, float | np.floating):
        return round(float(value), VALUE_DECIMALS) + 0.0
    if isinstance(value, Mapping):
        return {str(k): rounded(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [rounded(v) for v in value]
    return value


def idle_angle_of(name: str) -> float:
    return {"zero": IDLE_CC_ANGLE, "two-pi": IDLE_CC_ANGLE_FALLBACK}[name]


def ideal_endpoints() -> dict[str, Any]:
    laws = {name: ql.compensated_ideal(*arm[1:]) for name, arm in arm_table().items()}
    out = summarize(dist_of(laws))
    qual = {
        "qual_src1_phi": math.sin(ql.PHI_STAR) ** 2,
        "qual_src0_phi": 0.0,
        "qual_src1_pi": 1.0,
        "qual_src0_pi": 0.0,
    }
    return {"endpoints": {k: float(v) for k, v in out.items()}, "qualification_p1": qual}


class BuildArgs(NamedTuple):
    pairs: int | None = None
    herald: str = "auto"
    shots: int | None = None
    shot_seconds: float | None = None
    idle_cc_angle: str = "zero"
    reset: str = "passive"
    max_credits: float = MAX_CREDITS[QC]

    def as_dict(self) -> dict[str, Any]:
        return self._asdict()


def sensitivity(
    folder: str, chosen: Mapping[str, Any], idle_angle: float, passive: bool, excited: bool = False
) -> dict[str, Any]:
    """The chosen pairs' pooled endpoints with every idle time scaled by RELAXATION_SENSITIVITY, or, with excited,
    at calibrated relaxation from the calibrated initial excitation."""
    herald = bool(chosen["herald"])
    scale = 1.0 if excited else RELAXATION_SENSITIVITY
    items = [(folder, row, herald, scale, idle_angle, passive, excited) for row in chosen["pairs"]]
    return pooled(ordered_map(predict_pair, items, min_items=2), float(chosen["kept_shots"]))


def build_from(folder: Path, args: BuildArgs) -> dict[str, str]:
    """Relative path -> text of the case, planned and predicted from the calibration folder."""
    device = load_device(str(folder))
    idle_angle = idle_angle_of(args.idle_cc_angle)
    if args.reset != "passive":
        raise ValueError(
            f"reset mode {args.reset!r}: every ladder arm feeds Bob's drive from Alice's readout, and active reset "
            "adds a second feedback label to that drive, which the station refuses; a case runs passive reset"
        )
    passive = True
    if not args.max_credits > 0:
        raise ValueError(f"a Garnet credit ceiling must be positive, not {args.max_credits}")
    selected = plan(str(folder), args.herald, args.pairs, 1.0, idle_angle, passive, args.max_credits)
    chosen = selected["chosen"]
    herald = bool(chosen["herald"])
    pairs = [pair_of(row) for row in chosen["pairs"]]
    names = arm_names()
    shot_seconds = args.shot_seconds if args.shot_seconds is not None else float(chosen["shot_seconds"])
    shots = args.shots if args.shots is not None else shots_for(shot_seconds, len(names), args.max_credits)
    keep = HERALD_KEEP_PER_QUBIT ** (2 * len(pairs)) if herald else 1.0
    kept = shots * keep
    files: dict[str, str] = {}
    entries = []
    for name in names:
        rel = f"circuits/{name}.json"
        files[rel] = dump(circuit_json(name, pairs, idle_angle))
        entries.append({"file": rel, "sha256": sha256(files[rel].encode())})
    options: dict[str, Any] = {
        "heralding_mode": "zeros" if herald else "none",
        "active_reset_cycles": None if passive else 1,
        "calibration_set_id": {QC: device.calibration.set_id},
    }
    expected = round(len(names) * shots * shot_seconds, 3)
    mock_options = {**options, "calibration_set_id": {}}
    jobs = [
        {
            "job": JOB,
            "circuits": entries,
            "shots": shots,
            "options": options,
            "expected_seconds": expected,
            "expected_seconds_by_qc": {
                QC: expected,
                "garnet:mock": round(len(names) * shots * shot_seconds, 3),
            },
            "max_credits": {QC: args.max_credits, "garnet:mock": 0.0},
        },
        {
            "job": MOCK_JOB,
            "circuits": entries,
            "shots": MOCK_SHOTS,
            "options": mock_options,
            "expected_seconds": round(len(names) * MOCK_SHOTS * shot_seconds, 3),
            "expected_seconds_by_qc": {"garnet:mock": round(len(names) * MOCK_SHOTS * shot_seconds, 3)},
            "max_credits": {"garnet:mock": 0.0},
        },
    ]
    pair_rows = []
    for member, pair in zip(chosen["members"], pairs, strict=True):
        variance = member["variance_one_shot"]
        pair_rows.append(
            {
                "pair": pair.as_dict(),
                "endpoints": member["endpoints"],
                "shot_se": {k: math.sqrt(v / kept) for k, v in variance.items()},
                "laws": member["laws"],
                "qualification": member["qualification"],
            }
        )
    other = {
        str(h): {"pairs": r["pairs"], "pooled": r["pooled"], "shots": r["shots"], "kept_shots": r["kept_shots"]}
        for h, r in selected["by_herald"].items()
    }
    prediction = {
        "calibration_set": device.calibration.set_id,
        "metrics_set": device.calibration.metrics_id,
        "model": (
            "iqm_sim depolarizing prx and CZ, per-qubit readout, idle T1/T2 over the ASAP schedule with the "
            "measure window and control delay as Bob's wait; exact density-matrix law, no sampling; no coherent "
            "phase, crosstalk, leakage or non-QND readout"
        ),
        "herald": herald,
        "pairs": pair_rows,
        "pooled": pooled(chosen["members"], kept),
        "shots": {"per_circuit": shots, "kept_per_circuit": kept, "shot_seconds": shot_seconds},
        "size_table": [
            {
                "herald": r["herald"],
                "size": r["size"],
                "shots": r["shots"],
                "kept_shots": r["kept_shots"],
                "shot_seconds": r["shot_seconds"],
                "qubits": [[p["alice"], p["bob"]] for p in r["pairs"]],
                "pooled": r["pooled"],
            }
            for r in selected["table"]
        ],
        "best_by_herald": other,
        "relaxation_sensitivity": {
            "scale": RELAXATION_SENSITIVITY,
            "pooled": sensitivity(str(folder), chosen, idle_angle, passive),
        },
        "initial_excitation_sensitivity": {
            "field": INIT_ERROR_FIELD,
            "pooled": sensitivity(str(folder), chosen, idle_angle, passive, excited=True) if passive else None,
        },
        "ideal": ideal_endpoints(),
    }
    files["prediction.json"] = dump(rounded(prediction))
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does the phase-compensated QET ladder that ran on ibm_kingston replicate on Garnet: does Bob's "
                "record-steered rotation lower his energy below the best record-independent unitary (information "
                "excess), and below the vacuum floor (channel floor margin), and does cc_prx at the non-pi angle "
                "2 phi* reach its ideal P(1)?"
            ),
            "ideal": ideal_endpoints(),
            "build": args.as_dict(),
            "pairs": [p.as_dict() for p in pairs],
            "qcs": QCS,
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "jobs": jobs,
        }
    )
    return files


def write(directory: Path, source: Path, args: BuildArgs) -> None:
    """Build the case from source into directory, replacing its calibration copy and circuit files.

    The build reads a temporary copy of source, so source may be the case's own calibration folder, and the
    circuits folder is cleared first, so an arm the build no longer emits leaves no file behind.
    """
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "calibration"
        prepare_calibration(source, staged)
        files = build_from(staged, args)
        for folder in (directory / "calibration", directory / "circuits"):
            if folder.exists():
                shutil.rmtree(folder)
        shutil.copytree(staged, directory / "calibration")
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def check(directory: Path) -> None:
    case = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    files = build_from(directory / "calibration", BuildArgs(**case["build"]))
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{n}" for n in (*CALIBRATION_FILES, TIMING_FILE, FEEDBACK_FILE)}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")


# ---------------------------------------------------------------------------------------------------------
# Independent exact check of the lowering
# ---------------------------------------------------------------------------------------------------------


def qiskit_law(
    ops: Sequence[Mapping[str, Any]], pair: Pair, window_phase: float = 0.0, window_at: str = "barrier"
) -> np.ndarray:
    """The ideal law over r + 2a + 4b of one pair's native operations, evolved over the two feedback branches
    with Qiskit's RGate and CZ matrices; a nonzero window_phase is an rz on Bob at the barrier or, with
    window_at="feedback", just before Bob's cc_prx."""
    index = {pair.alice: 0, pair.bob: 1}
    state = Statevector.from_label("00")
    split = next(i for i, o in enumerate(ops) if o["name"] == "measure" and o["locus"] == [pair.alice])
    for o in ops[:split]:
        if o["name"] == "barrier":
            if window_phase and window_at == "barrier":
                state = state.evolve(Operator(rz_gate(window_phase)), qargs=[index[pair.bob]])
        elif o["name"] == "prx":
            state = state.evolve(Operator(RGate(o["args"]["angle"], o["args"]["phase"])), qargs=[index[o["locus"][0]]])
        elif o["name"] == "cz":
            state = state.evolve(Operator(CZGate()), qargs=[index[q] for q in o["locus"]])
        else:
            raise ValueError(f"{o['name']} before the feedback measure")
    amplitudes = np.asarray(state.data).reshape(2, 2)
    law = np.zeros(8)
    for r in (0, 1):
        branch = amplitudes[:, r]
        weight = float(np.vdot(branch, branch).real)
        if weight < 1e-300:
            continue
        data = np.zeros(4, dtype=complex)
        data[[r, r + 2]] = branch / math.sqrt(weight)
        bob = Statevector(data)
        for o in ops[split + 1 :]:
            if o["name"] == "cc_prx" and window_phase and window_at == "feedback":
                bob = bob.evolve(Operator(rz_gate(window_phase)), qargs=[1])
            if o["name"] == "prx" and o["locus"] == [pair.bob]:
                bob = bob.evolve(Operator(RGate(o["args"]["angle"], o["args"]["phase"])), qargs=[1])
            elif o["name"] == "cc_prx" and r == 1:
                bob = bob.evolve(Operator(RGate(o["args"]["angle"], o["args"]["phase"])), qargs=[1])
            elif o["name"] not in ("measure", "cc_prx"):
                raise ValueError(f"{o['name']} after the feedback measure")
        probabilities = bob.probabilities([1])
        for b in (0, 1):
            law[r + 2 * r + 4 * b] = weight * probabilities[b]
    return law


def lowering_deviation(
    pair: Pair,
    timing: Timing,
    window_phases: Sequence[float],
    frame_sign: float = 1.0,
    ops_of: Any = None,
) -> float:
    """Largest departure from qet_ladder.compensated_ideal over every arm, both simulators, each window phase at
    the barrier and after Alice's readout window; ops_of(arm, pair, frame_sign) replaces pair_ladder_ops."""
    lower = pair_ladder_ops if ops_of is None else ops_of
    worst = 0.0
    for phase in window_phases:
        for where in ("barrier", "feedback"):
            for arm in arm_table().values():
                ops = lower(arm, pair, frame_sign=frame_sign)
                ideal = ql.compensated_ideal(*arm[1:], window_phase=phase)
                direct = qiskit_law(ops, pair, phase, where)
                joint = simulate_pair(ops, pair, timing, Noise.ideal(pair), phase, where)
                worst = max(worst, float(np.abs(direct - ideal).max()), float(np.abs(flat_law(joint) - ideal).max()))
    return worst


def validate_circuit(circuit: Mapping[str, Any], device: Device, pairs: Sequence[Pair]) -> None:
    """The circuit holds Garnet native operations only, on calibrated couplers in their listed order, with unique
    measure keys and each cc_prx naming an earlier feedback_key measured on its feedback_qubit."""
    keys: set[str] = set()
    feedback: dict[str, str] = {}
    allowed = {"prx", "cz", "measure", "cc_prx", "barrier"}
    qubits = {q for p in pairs for q in (p.alice, p.bob)}
    for item in circuit["instructions"]:
        name, locus, args = item["name"], item["locus"], item["args"]
        if name not in allowed or not set(locus) <= qubits:
            raise ValueError(f"{circuit['name']}: {name} on {locus} is not allowed")
        if name == "cz" and device.loci.get(frozenset(locus)) != tuple(locus):
            raise ValueError(f"{circuit['name']}: cz {locus} is not a calibrated coupler in its listed order")
        if name in ("prx", "cc_prx") and not all(math.isfinite(args[k]) for k in ("angle", "phase")):
            raise ValueError(f"{circuit['name']}: a non-finite angle")
        if name == "measure":
            if args["key"] in keys:
                raise ValueError(f"{circuit['name']}: key {args['key']} repeats")
            keys.add(args["key"])
            if "feedback_key" in args:
                feedback[args["feedback_key"]] = locus[0]
        if name == "cc_prx" and feedback.get(args["feedback_key"]) != args["feedback_qubit"]:
            raise ValueError(f"{circuit['name']}: cc_prx reads a feedback_key no earlier measure holds")
        if name == "cc_prx" and not feedback_allowed(device, args["feedback_qubit"], locus[0]):
            raise ValueError(
                f"{circuit['name']}: {locus[0]} takes no fast feedback from {args['feedback_qubit']}'s probe line"
            )
    for i, p in enumerate(pairs):
        for q in pairs[i + 1 :]:
            near = {frozenset((u, v)) for u in (p.alice, p.bob) for v in (q.alice, q.bob)}
            if any(edge in device.loci for edge in near):
                raise ValueError(f"pairs {p.number} and {q.number} share a coupler")
    if len(qubits) != 2 * len(pairs):
        raise ValueError(f"{circuit['name']}: the pairs overlap")


# ---------------------------------------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------------------------------------


def wilson(ones: int, n: int, z: float = Z95) -> tuple[float, float]:
    p = ones / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def shot_bits(circuit: Mapping[str, Any], key: str) -> np.ndarray:
    return np.asarray(circuit[key], dtype=int).reshape(len(circuit[key]), -1)[:, 0]


def ladder_counts(circuit: Mapping[str, Any], index: int) -> np.ndarray:
    """Counts over r + 2a + 4b of pair index from a circuit's per-key shot lists."""
    r, a, b = (shot_bits(circuit, f"{key}{index}") for key in ("alice", "afinal", "bob"))
    if not len(r) == len(a) == len(b):
        raise ValueError(f"pair {index}: the keys hold different shot counts")
    return np.bincount(r + 2 * a + 4 * b, minlength=8).astype(float)


def endpoints_of_run(case: Mapping[str, Any], measurements: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Per-pair and pooled endpoints and the qualification P(1) of a run's measurement artifact.

    The artifact lists a circuit per case circuit in order, each mapping a key to shot-ordered bit lists; a
    heralded job returns only the kept shots, so every count is of kept shots.
    """
    row = next(r for r in case["jobs"] if r["job"] == JOB)
    names = [Path(c["file"]).stem for c in row["circuits"]]
    if len(measurements) != len(names):
        raise ValueError(f"{len(measurements)} circuits returned for {len(names)} in the case")
    by_name = dict(zip(names, measurements, strict=True))
    per_pair = []
    for pair in case["pairs"]:
        index = int(pair["index"])
        counts = {name: ladder_counts(by_name[name], index) for name in arm_table()}
        dist = {f"{GROUP}_{name}": c / c.sum() for name, c in counts.items()}
        shots = {f"{GROUP}_{name}": float(c.sum()) for name, c in counts.items()}
        endpoints = summarize(dist)
        variance = endpoint_variance(dist, shots)
        qualification = {}
        for name in QUAL_ARMS:
            target, source = shot_bits(by_name[name], f"bob{index}"), shot_bits(by_name[name], f"alice{index}")
            # cc_prx reads Alice's recorded bit, so the conditional rotation is the target's response on the shots
            # whose record matches the prepared source.
            prepared = 1 if name.startswith("qual_src1") else 0
            matched = source == prepared
            qualification[name] = {
                "target_ones": int(target.sum()),
                "source_ones": int(source.sum()),
                "shots": int(len(target)),
                "matched_target_ones": int(target[matched].sum()),
                "matched_shots": int(matched.sum()),
            }
        per_pair.append(
            {
                "pair": pair,
                "kept_shots_min": int(min(c.sum() for c in counts.values())),
                "endpoints": {
                    k: float(endpoints[k]) for k in (*ENDPOINTS, "reference_phase", "selected_alpha", "channel_floor")
                },
                "shot_se": {k: math.sqrt(v) for k, v in variance.items()},
                "qualification": qualification,
            }
        )
    count = len(per_pair)
    pooled_out: dict[str, Any] = {}
    for name in (*ENDPOINTS, "compensation_gain"):
        values = [
            row_["endpoints"]["selected_margin"] - row_["endpoints"]["uncompensated_margin"]
            if name == "compensation_gain"
            else row_["endpoints"][name]
            for row_ in per_pair
        ]
        centre = mean(values)
        spread = math.sqrt(sum((v - centre) ** 2 for v in values) / (count - 1)) if count > 1 else float("nan")
        half = float(stats.t.ppf(0.975, count - 1)) * spread / math.sqrt(count) if count > 1 else float("nan")
        entry = {"mean": centre, "t95_half_width": half, "pairs": count}
        if name in ENDPOINTS:
            entry["shot_se"] = math.sqrt(sum(r_["shot_se"][name] ** 2 for r_ in per_pair)) / count
        pooled_out[name] = entry
    qualification_pooled = {}
    for name in QUAL_ARMS:
        ones = sum(r_["qualification"][name]["target_ones"] for r_ in per_pair)
        n = sum(r_["qualification"][name]["shots"] for r_ in per_pair)
        low, high = wilson(ones, n)
        qualification_pooled[name] = {"p1": ones / n, "wilson95": [low, high], "shots": n}
        for r_ in per_pair:
            q_ = r_["qualification"][name]
            q_["p1"] = q_["target_ones"] / q_["shots"]
            q_["wilson95"] = list(wilson(q_["target_ones"], q_["shots"]))
    for r_, pair in zip(per_pair, case["pairs"], strict=True):
        r_["h3"] = angle_qualification(r_["qualification"], counts_of_pair(by_name, int(pair["index"])))
    return {
        "pairs": per_pair,
        "pooled": pooled_out,
        "qualification": qualification_pooled,
        "decisions": decisions(per_pair),
    }


def counts_of_pair(by_name: Mapping[str, Mapping[str, Any]], index: int) -> dict[str, np.ndarray]:
    return {name: ladder_counts(by_name[name], index) for name in ("cal_00", "cal_11")}


class Readout(NamedTuple):
    """A target's assignment errors P(1|0) = e0 and P(0|1) = e1 with the shot counts that estimated them."""

    e0: float
    n0: float
    e1: float
    n1: float


def corrected_probability(ones: int, shots: int, readout: Readout, z: float) -> dict[str, float]:
    """The readout-corrected P(1) (p - e0)/(1 - e0 - e1) of a target and its interval at z.

    The raw P(1)'s Wilson interval is mapped through the correction, and each side is widened in quadrature by the
    delta-method uncertainty of the two assignment errors, d/de0 = -(1 - q)/D and d/de1 = q/D at the bound's q with
    D = 1 - e0 - e1, so the interval carries the calibration arms' binomial noise as well as the target's.
    """
    e0, e1 = readout.e0, readout.e1
    scale = 1 - e0 - e1

    def correct(p1: float) -> float:
        return (p1 - e0) / scale

    def nuisance(q: float) -> float:
        var0 = e0 * (1 - e0) / readout.n0
        var1 = e1 * (1 - e1) / readout.n1
        return z * math.sqrt(var0 * (1 - q) ** 2 + var1 * q**2) / scale

    point = correct(ones / shots)
    raw_low, raw_high = wilson(ones, shots, z)
    low, high = correct(raw_low), correct(raw_high)
    return {
        "p1": point,
        "low": point - math.hypot(point - low, nuisance(low)),
        "high": point + math.hypot(high - point, nuisance(high)),
    }


def corrected_angle(ones: int, shots: int, readout: Readout, z: float) -> dict[str, float]:
    """The conditional rotation angle 2 asin(sqrt q) of the corrected P(1) q, with its interval mapped through."""

    def angle(q: float) -> float:
        return 2 * math.asin(math.sqrt(min(max(q, 0.0), 1.0)))

    q = corrected_probability(ones, shots, readout, z)
    return {"angle": angle(q["p1"]), "low": angle(q["low"]), "high": angle(q["high"])}


def angle_qualification(qualification: Mapping[str, Any], cal: Mapping[str, np.ndarray]) -> dict[str, Any]:
    """H3 for one pair: Bob's readout-corrected cc_prx angle from a |1> source and P(1) from a |0> source.

    The pair's own cal_00 and cal_11 arms give Bob's assignment errors in the same job (bit b, index >> 2), so a
    |0>-source reading is compared with readout error rather than with zero. Both read only the shots whose
    recorded Alice bit matches the prepared source, the bit cc_prx conditions on.
    """
    zeros, ones = cal["cal_00"] / cal["cal_00"].sum(), cal["cal_11"] / cal["cal_11"].sum()
    bob = [i for i in range(8) if (i >> 2) & 1]
    readout = Readout(
        float(zeros[bob].sum()), float(cal["cal_00"].sum()), float(1 - ones[bob].sum()), float(cal["cal_11"].sum())
    )
    e0, e1 = readout.e0, readout.e1
    src1 = qualification["qual_src1_phi"]
    fitted = corrected_angle(src1["matched_target_ones"], src1["matched_shots"], readout, Z99)
    src0 = qualification["qual_src0_phi"]
    src0_corrected_high = corrected_probability(src0["matched_target_ones"], src0["matched_shots"], readout, Z99)[
        "high"
    ]
    pi = qualification["qual_src1_pi"]
    target = 2 * ql.PHI_STAR
    passes = (
        target - H3_ANGLE_TOLERANCE <= fitted["low"]
        and fitted["high"] <= target + H3_ANGLE_TOLERANCE
        and src0_corrected_high < H3_SOURCE0_LIMIT
    )
    return {
        "bob_p1_given_0": e0,
        "bob_p0_given_1": e1,
        "fitted_angle": fitted,
        "target_angle": target,
        "pi_arm_angle": corrected_angle(pi["matched_target_ones"], pi["matched_shots"], readout, Z99),
        "source0_corrected_p1_upper99": src0_corrected_high,
        "scored": passes,
    }


def one_sided(values: Sequence[float]) -> tuple[float, float, float]:
    """(mean, lower, upper) one-sided DECISION_LEVEL t bounds across pairs."""
    n = len(values)
    if n < 2:
        return (values[0] if values else float("nan")), float("nan"), float("nan")
    centre = mean(values)
    spread = math.sqrt(sum((v - centre) ** 2 for v in values) / (n - 1))
    half = float(stats.t.ppf(DECISION_LEVEL, n - 1)) * spread / math.sqrt(n)
    return centre, centre - half, centre + half


def decisions(per_pair: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """H1, H2 and H4 over every pair (primary) and over the pairs H3 scores (secondary); each is its own one-sided
    test at DECISION_LEVEL.

    Every cc_prx failure (never firing, firing on the wrong bit, under-rotating) lowers a pair's excess toward or
    below zero, since the unitary floor minimizes over every record-independent unitary on Bob, so the primary
    tests keep every pair rather than drop the ones H3 flags. H1 (information excess) and H2 (channel floor margin)
    read the selected-alpha endpoints; H4 reads the mean magnitude of the per-pair reference phase against
    H4_PHASE_SCALE. A verdict needs two pairs.
    """
    scored = [r for r in per_pair if r["h3"]["scored"]]
    out: dict[str, Any] = {
        "scored_pairs": [[r["pair"]["alice"], r["pair"]["bob"]] for r in scored],
        "h3_all_pairs_scored": len(scored) == len(per_pair),
    }

    def verdict(values: Sequence[float], threshold: float, above: str, below: str) -> dict[str, Any]:
        centre, low, high = one_sided(values)
        if len(values) < 2:
            state = "insufficient pairs"
        elif low > threshold:
            state = above
        elif high < threshold:
            state = below
        else:
            state = "unresolved"
        return {"mean": centre, "lower": low, "upper": high, "pairs": len(values), "verdict": state}

    # A reference phase beyond COMPENSATION_REACH leaves that pair's selected alpha at the grid edge, so a low
    # excess there measures the finite grid, not feed-forward: a refuting H1 or failing H2 verdict with such a
    # pair present is inconclusive about the mechanism.
    out_of_reach = [r for r in per_pair if abs(r["endpoints"]["reference_phase"]) > COMPENSATION_REACH]
    out["phase_out_of_reach_pairs"] = [[r["pair"]["alice"], r["pair"]["bob"]] for r in out_of_reach]

    def guarded(entry: dict[str, Any], rows: Sequence[Mapping[str, Any]], negative: str) -> dict[str, Any]:
        if entry["verdict"] == negative and any(r in out_of_reach for r in rows):
            entry["verdict"] = "inconclusive: a phase lies outside the compensation reach"
        return entry

    for label, rows in (("all_pairs", per_pair), ("h3_scored", scored)):
        out[label] = {
            "h1_information_excess": guarded(
                verdict([r["endpoints"]["selected_excess"] for r in rows], 0.0, "reproduced", "refuted"),
                rows,
                "refuted",
            ),
            "h2_channel_floor_margin": guarded(
                verdict([r["endpoints"]["selected_margin"] for r in rows], 0.0, "passes", "fails"), rows, "fails"
            ),
            "h4_window_phase": verdict(
                [abs(r["endpoints"]["reference_phase"]) for r in rows],
                H4_PHASE_SCALE,
                "coherent phase of Kingston's order",
                "below Kingston's order",
            ),
        }
    return out


def analyze(run_dirs: Sequence[Path]) -> dict[str, Any]:
    """Endpoints of the one retained Garnet run of this case, beside the case's prediction."""
    if len(run_dirs) != 1:
        raise ValueError("the analysis reads exactly one run")
    run_dir = run_dirs[0]
    facts = iqm_jobs.run_facts(run_dir)
    submission = json.loads((run_dir / "submission.json").read_text(encoding="utf-8"))
    if submission["qc"] != QC or submission["job"] != JOB:
        raise ValueError(
            f"{run_dir}: the analysis reads the {JOB} job on {QC}, not {submission['job']} on {submission['qc']}"
        )
    case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    record = json.loads((run_dir / "raw/job.json").read_bytes())
    compiled = record["compilation"]["calibration_set_id"]
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    if sha256((run_dir / "prediction.json").read_bytes()) != case["prediction_sha256"]:
        raise ValueError(f"{run_dir}/prediction.json is not the prediction cases.json binds")
    measurements = json.loads((run_dir / "raw/measurements.json").read_bytes())
    out = endpoints_of_run(case, measurements)
    row = next(r for r in case["jobs"] if r["job"] == JOB)
    planned = row["shots"]
    out.update(
        {
            "schema": ANALYSIS_SCHEMA,
            "run": run_dir.name,
            "qc": submission["qc"],
            "compiled_calibration_set": compiled,
            "predicted_calibration_set": prediction["calibration_set"],
            "heralding_retention": out["pairs"][0]["kept_shots_min"] / planned,
            "estimate_seconds": record["compilation"]["execution_runtime_estimate_seconds"],
            "runtime_seconds": record["metrics"]["runtime_seconds"],
            "billed_seconds": record["metrics"]["billed_seconds"],
            "charge": facts["charge"],
            "predicted_pooled": prediction["pooled"],
            "kingston": KINGSTON,
        }
    )
    return dict(rounded(out))


# ---------------------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------------------


def quantize(law: Sequence[float] | np.ndarray, n: int) -> list[int]:
    """Counts summing to n closest to law by largest remainder; no random draw."""
    raw = np.asarray(law, dtype=float) * n
    base = np.floor(raw).astype(int)
    order = np.argsort(-(raw - base), kind="stable")[: n - int(base.sum())]
    base[order] += 1
    return [int(x) for x in base]


def synthetic_measurements(
    case: Mapping[str, Any],
    n: int,
    laws: Sequence[Mapping[str, Sequence[float]]] | None = None,
    qual_p1: Sequence[Mapping[str, float]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    """The artifact of a run whose pairs follow the ideal laws (or laws[pair index], each arm's law over
    r + 2a + 4b, and qual_p1[pair index], each qualification arm's target P(1)) at n shots, with the quantized
    counts of the last pair."""
    row = next(r for r in case["jobs"] if r["job"] == JOB)
    table = arm_table()
    ideal_p1 = case["ideal"]["qualification_p1"]
    out = []
    quantized: dict[str, np.ndarray] = {}
    for entry in row["circuits"]:
        name = Path(entry["file"]).stem
        circuit: dict[str, Any] = {}
        for pair in case["pairs"]:
            i = pair["index"]
            if name in QUAL_ARMS:
                target_p1 = ideal_p1[name] if qual_p1 is None else qual_p1[i][name]
                ones = quantize([1 - target_p1, target_p1], n)[1]
                source = 1 if name.startswith("qual_src1") else 0
                circuit[f"alice{i}"] = [[source]] * n
                circuit[f"bob{i}"] = [[1]] * ones + [[0]] * (n - ones)
                continue
            source_law = ql.compensated_ideal(*table[name][1:]) if laws is None else laws[i][name]
            counts = quantize(source_law, n)
            quantized[name] = np.asarray(counts, dtype=float)
            cells = [cell for cell, c in enumerate(counts) for _ in range(c)]
            circuit[f"alice{i}"] = [[cell & 1] for cell in cells]
            circuit[f"afinal{i}"] = [[(cell >> 1) & 1] for cell in cells]
            circuit[f"bob{i}"] = [[(cell >> 2) & 1] for cell in cells]
        out.append(circuit)
    return out, quantized


def aer_relaxation_error(device: Device) -> float:
    """Largest entry difference between relaxation_kraus and iqm_signed_probe.relaxation's Aer pass (QB1)."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    cal = device.calibration
    seconds = 1.7e-6
    prepare = QuantumCircuit(1)
    prepare.u(1.1, 0.4, 0.9, 0)
    circuit = prepare.copy()
    circuit.delay(round(seconds * 1e9), 0, unit="dt")
    noisy = aer_relaxation(cal, {"QB1"})(circuit)
    noisy.save_density_matrix()
    aer = np.asarray(AerSimulator(method="density_matrix").run(noisy).result().data()["density_matrix"])
    psi = np.asarray(Statevector.from_instruction(prepare).data)
    mine = _kraus(np.outer(psi, psi.conj()), relaxation_kraus(seconds, *_t1t2(cal, "QB1")), 0, 1)
    return float(np.abs(aer - mine).max())


def _t1t2(cal: iqm_sim.Calibration, qubit: str) -> tuple[float, float]:
    t1 = float(cal.values[f"characterization.model.{qubit}.t1_time"])
    return t1, min(float(cal.values[f"characterization.model.{qubit}.t2_time"]), 2 * t1)


def self_test() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "calibration"
        prepare_calibration(EVIDENCE_CALIBRATION, folder)
        device = load_device(str(folder))
        for theta, phi in ((0.3, 0.7), (math.pi, -1.1), (2.2, 3.0)):
            if np.abs(rgate(theta, phi) - Operator(RGate(theta, phi)).data).max() > 1e-14:
                raise RuntimeError(f"prx({theta}, {phi}) is not RGate")
        pair = Pair(0, "QB1", "QB2", device.loci[frozenset(("QB1", "QB2"))])
        phases = (0.0, 0.7, -0.4)
        deviation = lowering_deviation(pair, device.timing, phases)
        if deviation > 1e-12:
            raise RuntimeError(f"the lowered arms depart from compensated_ideal by {deviation}")
        mutated = lowering_deviation(pair, device.timing, phases, frame_sign=-1.0)
        if mutated < 1e-3:
            raise RuntimeError(f"a flipped frame sign passes the check ({mutated})")
        relax = aer_relaxation_error(device)
        if relax > 1e-9:
            raise RuntimeError(f"relaxation_kraus differs from the Aer pass by {relax}")
        pairs = [
            Pair(0, "QB1", "QB2", device.loci[frozenset(("QB1", "QB2"))]),
            Pair(1, "QB19", "QB15", device.loci[frozenset(("QB15", "QB19"))]),
        ]
        for arm in arm_names():
            validate_circuit(circuit_json(arm, pairs), device, pairs)
        case_dir = Path(tmp) / CASE
        write(case_dir, EVIDENCE_CALIBRATION, BuildArgs(pairs=2, herald="none"))
        check(case_dir)
        case = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
        row = case["jobs"][0]
        ceiling = iqm_jobs.ceiling_credits(row["expected_seconds"], PRICE[QC])
        if ceiling > MAX_CREDITS[QC]:
            raise RuntimeError(f"the plan ceiling {ceiling} exceeds {MAX_CREDITS[QC]} credits")
        measurements, quantized = synthetic_measurements(case, 4000)
        result = endpoints_of_run(case, measurements)
        ideal = case["ideal"]["endpoints"]
        exact = summarize({f"{GROUP}_{k}": v / v.sum() for k, v in quantized.items()})
        for entry in result["pairs"]:
            for name in ENDPOINTS:
                if abs(entry["endpoints"][name] - exact[name]) > 1e-12:
                    raise RuntimeError(f"{name}: counts map to {entry['endpoints'][name]}, not {exact[name]}")
                if abs(entry["endpoints"][name] - ideal[name]) > 2e-3:
                    raise RuntimeError(f"{name}: recovered {entry['endpoints'][name]} against ideal {ideal[name]}")
        for name, p1 in case["ideal"]["qualification_p1"].items():
            low, high = result["qualification"][name]["wilson95"]
            if not low - 1e-9 <= p1 <= high + 1e-9:
                raise RuntimeError(f"{name}: P(1) {p1} outside {low}..{high}")
    return (
        f"iqm qet ladder: lowering matches compensated_ideal to {deviation:.1e} over {len(arm_table())} arms x "
        f"{len(phases)} window phases (flipped frame sign {mutated:.2f}); Aer relaxation {relax:.1e}; "
        "case check, native validity, ceiling and synthetic analysis pass"
    )


# ---------------------------------------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------------------------------------


def with_calibration(source: Path, tmp: str) -> Path:
    """A calibration folder holding timing.json: source itself, or a prepared copy of a snapshot folder."""
    if (source / TIMING_FILE).exists():
        return source
    folder = Path(tmp) / "calibration"
    prepare_calibration(source, folder)
    return folder


def predict_case(directory: Path, source: Path) -> dict[str, Any]:
    """The case's pairs and options predicted under another calibration."""
    case = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    row = case["jobs"][0]
    herald = row["options"]["heralding_mode"] == "zeros"
    passive = row["options"]["active_reset_cycles"] is None
    idle_angle = idle_angle_of(case["build"]["idle_cc_angle"])
    kept = row["shots"] * (HERALD_KEEP_PER_QUBIT ** (2 * len(case["pairs"])) if herald else 1.0)
    out: dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as tmp:
        folder = str(with_calibration(source, tmp))
        for label, scale in (("calibrated", 1.0), ("relaxation_scaled", RELAXATION_SENSITIVITY)):
            results = ordered_map(
                predict_pair, [(folder, p, herald, scale, idle_angle, passive) for p in case["pairs"]], min_items=2
            )
            out[label] = {
                "calibration_set": load_device(folder).calibration.set_id,
                "pooled": pooled(results, kept),
                "pairs": [
                    {"pair": r["pair"], "endpoints": r["endpoints"], "qualification": r["qualification"]}
                    for r in results
                ],
            }
    return dict(rounded(out))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    build = sub.add_parser("build")
    build.add_argument("directory", type=Path)
    build.add_argument("--calibration-dir", type=Path, default=EVIDENCE_CALIBRATION)
    build.add_argument("--pairs", type=int)
    build.add_argument("--herald", choices=("auto", "zeros", "none"), default="auto")
    build.add_argument("--shots", type=int)
    build.add_argument("--shot-seconds", type=float)
    build.add_argument("--idle-cc-angle", choices=("zero", "two-pi"), default="zero")
    build.add_argument("--reset", choices=("passive",), default="passive")
    build.add_argument("--max-credits", type=float, default=MAX_CREDITS[QC])
    sub.add_parser("check").add_argument("directory", type=Path)
    planner = sub.add_parser("plan")
    planner.add_argument("--calibration-dir", type=Path, default=EVIDENCE_CALIBRATION)
    planner.add_argument("--herald", choices=("auto", "zeros", "none"), default="auto")
    planner.add_argument("--pairs", type=int)
    planner.add_argument("--reset", choices=("passive",), default="passive")
    predictor = sub.add_parser("predict")
    predictor.add_argument("directory", type=Path)
    predictor.add_argument("--calibration-dir", type=Path, required=True)
    an = sub.add_parser("analyze")
    an.add_argument("run_dirs", type=Path, nargs="+")
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true", help="compare --out with the recomputation")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(
            args.directory,
            args.calibration_dir,
            BuildArgs(
                args.pairs, args.herald, args.shots, args.shot_seconds, args.idle_cc_angle, args.reset, args.max_credits
            ),
        )
        print(f"{args.directory}: written")
    elif args.command == "check":
        check(args.directory)
        print(f"{args.directory}: matches the build from its retained calibration")
    elif args.command == "plan":
        with tempfile.TemporaryDirectory() as tmp:
            result = plan(
                str(with_calibration(args.calibration_dir, tmp)),
                args.herald,
                args.pairs,
                1.0,
                IDLE_CC_ANGLE,
                args.reset == "passive",
            )
        for row in result["table"]:
            row.pop("members")
        print(dump(rounded(result["table"])), end="")
    elif args.command == "predict":
        print(dump(predict_case(args.directory, args.calibration_dir)), end="")
    elif args.command == "analyze":
        text = dump(analyze(args.run_dirs))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
