"""Tuna-17 case for the null block's selector offset (row A5-186): an injected X-rotation scan of the retained b0.

The null block b0 = e1 + e17 (21 routed CZ, 49 X90 pulses: 34 on q8, 8 on q4, 5 on q12, 1 on q2, 1 on q11) reads a
raw selector contrast above zero on Tuna-17 (+0.0164 in the coin series; +0.0162 and +0.0393 in the two base batches
of scripts/qi_pathion_one_cz_null_cases.py), where every arm-symmetric readout and both contractions of contract()
give 0 and the gate-noise families of GATE_KINDS at most 0.0001 in size. That case's 6-CZ blocks read zero, which
a coherent pulse error and a selector flip conditioned on q12 both predict, so it left the two apart.
This module builds the case that separates them on b0 itself.

Mechanism. Tuna-17 runs X90 and Rx as native single-qubit operations of one 20 ns duration and quantizes a rotation
angle to a pi/36 grid (cqasm.md; site/kbase_tuna-operational-specifics.md), so replacing an X90 by
Rx(pi/2 + k pi/36) adds a known rotation k pi/36 about the pulse axis and leaves the schedule, the CZ count and every
other instruction unchanged. A pulse that already over-rotates by theta then rotates by
pi/2 + theta + k pi/36, so the selector contrast as a function of k is the pulse-error response curve shifted by
theta. A readout mechanism (a selector flip conditioned on q12, a selector dropout conditioned on the coin) leaves
the curve of an exact pulse in place and adds its offset. hypothesis: Rx(pi/2 + k pi/36) is the X90 pulse at a scaled
amplitude; the bridge batches test the k = 0 case, Rx(pi/2) against X90, inside one batch.

Circuits. Every circuit is the retained b0 text (COIN_PINS of the one-CZ case pins its bytes; emit() reproduces them
from the parsed instruction list) with pulses rewritten: "b0" keeps X90, "b0-rx" replaces every X90 by Rx(pi/2), and
"b0-rx-SCOPE-mK" / "-pK" add -K or +K degrees on the pulses of SCOPE (all five region qubits, q8 alone, q4 alone)
and keep Rx(pi/2) elsewhere; the note line names the arm. forward_law() simulates any of them under a pulse-error
world on the five region qubits.

Series. A scan batch holds [minus arm, b0-rx, plus arm], so each batch carries its own center and a drift between
batches changes no within-batch comparison. Scan batches (SCANS): +-10 and +-20 degrees on all pulses, +-10 on q4's
and on q8's, each in a forward round and a mirror round with the arm order reversed. Two bridge batches hold b0 and
b0-rx. A readout batch
[readout-0, readout-1] sits before and after every data batch; it supplies the assignment matrix of the neighboring
data batch and the readout admission (e01 and e10 of the qubits of GUARD_ROLES steady across the two brackets).

Decision. fit_batch() fits each world's one parameter to the three raw selector contrasts of a batch at the retention
or noise strength that reproduces the center arm's visibility, for each noise model: the contraction shares
(MIX_GRID: how much of the visibility loss depolarizes the data bits alone and so spares the selector contrast) and
the gate-noise families of GATE_KINDS, whose laws gate_table() tabulates. decide() sums the batch chi-squares per
world over the admitted batches at the one noise model that makes the sum least and compares the best worlds of the
x, y-or-z and readout classes; every label is a preference among these worlds and noise models; a deciding label on
the hardware
series also needs the bridge to hold. preregistered(), OUTCOMES and decide() state and apply the rules;
operating_characteristics() simulates the decision under each world. The chi-square bound and the separation are
design thresholds whose error rates the operating characteristics measure: the retention is plugged in from the
center arm, and each class enters by its least chi-square over several worlds.

Usage: "$PYTHON" scripts/qi_pathion_null_rotation_scan_cases.py
       (--write DIR | --check DIR | --operating-characteristics | --sanity RUN_DIR...
        | --analyze RUN_DIR... --out FILE | --self-test)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2 as chi2_law

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402
import qi_zero_divisor_cases as zd  # noqa: E402

import pathion_coset_analysis as pca  # noqa: E402
from parallel import ordered_map  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_null_rotation_scan_tuna_17"
QX_SERIES = "pathion_null_rotation_scan_qx"
SCHEMA = "qi-pathion-null-rotation-scan-cases-v1"
SERIES_SCHEMA = "qi-pathion-null-rotation-scan-series-v1"
ANALYSIS_SCHEMA = "qi-pathion-null-rotation-scan-analysis-v1"
KEYS = cc.KEYS
NOUT = cc.NOUT
HALF = cc.HALF
SELECTOR = KEYS.index("selector")
COIN = KEYS.index("coin")
Z_RESOLVE = pca.Z_RESOLVE

# Tuna-17 quantizes a rotation angle to this grid (cqasm.md, "Rotation angles quantize on hardware").
STEP = math.pi / 36
RETAINED = "b0"
CENTER = "b0-rx"
# Scopes of a pulse-error world: the physical qubits whose pulses carry the error.
SCOPES: dict[str, tuple[int, ...]] = {"all": (2, 4, 8, 11, 12), "q8": (8,), "q4": (4,)}
# Scan kinds: (injection scope, grid steps of the injected angle).
# Among five candidate sets, this one alone read every sized truth of every modeled world in its class at expected
# values under each noise model of the fit, also with the truth's own gate-noise family left out of the fit
# (docs/notes/quantum_inspire/tuna17-null-rotation-scan-noise-simulation.md, "Scan set").
SCANS: dict[str, tuple[str, int]] = {"all10": ("all", 2), "q4-10": ("q4", 2), "q8-10": ("q8", 2), "all20": ("all", 4)}


def arm_name(scope: str, steps: int) -> str:
    return f"{CENTER}-{scope}-{'m' if steps < 0 else 'p'}{abs(steps) * 5}"


# Arm -> (pulse gate, injection scope or None, grid steps). The retained arm keeps X90; every other arm runs Rx.
ARMS: dict[str, tuple[str, str | None, int]] = {RETAINED: ("X90", None, 0), CENTER: ("Rx", None, 0)} | {
    arm_name(scope, sign * steps): ("Rx", scope, sign * steps) for scope, steps in SCANS.values() for sign in (-1, 1)
}
ARM_NAMES = tuple(ARMS)

SCAN_SHOTS = 131072
READOUT_SHOTS = 32768
QX_SHOTS = 2048
QX_QUBITS = 10
# The QX twin keeps the three circuits per batch that qi_platform.py allows a hardware batch
# (docs/notes/quantum_inspire/usage.md, "Queue rules: the FAQ governs"), so one size rule covers every generated batch.
QX_BATCH_CIRCUITS = 3
REPLICATES = 2
# Wall-time budget of the pause before each batch after the first: the top step of the pause ladder of
# scripts/qi_platform.py (docs/notes/quantum_inspire/usage.md, "Pause escalation"), so a series run at any step stays
# inside the budget.
PAUSE_CEILING = 120

# Design values of the forward model: the retention that takes b0's ideal visibility to the 0.44 the coin series read
# (docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.py, RHO ** 21) and the selector contrast b0 read there.
DESIGN_RETENTION = 0.505
DESIGN_CONTRAST = 0.0164
# The larger of the two base contrasts the one-CZ series read; the drift rows of the operating characteristics size
# one replicate round to it.
DRIFT_CONTRAST = 0.0393

# Pulse-error worlds: a rotation by theta about `axis` added to every pulse (X90 or Rx) on the qubits of `scope`,
# before or after the pulse in time; Rz is exact. About x the two orders coincide. About z they give one law, and
# about y the "after" law at theta is the "before" law at -theta (tests/scripts/test_qi_pathion_null_rotation_scan.py),
# so on the symmetric grid each "after" world repeats its "before" world's least chi-square.
THETA_FINE = np.linspace(-0.30, 0.30, 601)
PULSE_WORLDS: dict[str, tuple[str, str, str]] = {
    f"pulse_{axis}_{order}_{scope}": (axis, order, scope)
    for axis in "xyz"
    for order in (("before",) if axis == "x" else ("before", "after"))
    for scope in SCOPES
}
# Readout worlds: a stochastic map on the selector read, conditioned on a logical bit; x is its probability.
X_FINE = np.linspace(0.0, 0.20, 401)
READOUT_WORLDS: dict[str, tuple[str, str, int]] = {
    "selector_flip_q12_0": ("flip", "d0", 0),
    "selector_dropout_coin_1": ("dropout", "coin", 1),
}
WORLDS = (*PULSE_WORLDS, *READOUT_WORLDS)
X_PULSE = tuple(w for w, (axis, _, _) in PULSE_WORLDS.items() if axis == "x")
# World classes of the decision: a rotation about x on the pulses (the mechanism A5-186 names), a rotation about y or
# z on the pulses, and a readout map on the selector.
CLASSES: dict[str, tuple[str, ...]] = {
    "x": X_PULSE,
    "other": tuple(w for w in PULSE_WORLDS if w not in X_PULSE),
    "readout": tuple(READOUT_WORLDS),
}
CLASS_LABEL = {"x": "pulse_x", "other": "pulse_other", "readout": "readout"}

ADEQUACY_ALPHA = 0.001
# Chi-square separation between the best worlds of two classes at which one class is preferred. A design threshold:
# the classes are non-nested and each enters by its best world, so 25 carries no significance level of its own; the
# operating characteristics state the error rates it gives.
SEPARATION = 25.0
# Readout admission: the largest change of e01 or e10 of a guarded qubit between the brackets around a data batch.
GUARD_LIMIT = pcs.DRIFT_STOP
# Logical bits whose qubits the admission guards: the bits the selector contrast and visibility() read. Both sum d2
# out, so the assignment rates of d2's qubit leave them unchanged
# (tests/scripts/test_qi_pathion_null_rotation_scan.py), and d2 is read on q11, whose e10 moved by up to 0.34 between
# consecutive brackets of the one-CZ series (results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json),
# above GUARD_LIMIT in 4 of its 15 steps.
GUARD_ROLES = tuple(k for k in KEYS if k != "d2")

OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-13T172143Z.json"
OC_SEED_INDEX = 0
OC_DRAWS = 10000
# Gate-noise families whose truths the operating characteristics simulate beside the two contractions: the two that
# carry amplitude damping, the loss the contractions lack.
OC_FAMILIES = ("cz_damping", "damping_and_dephasing")

PAULI = {
    "x": np.array([[0, 1], [1, 0]], dtype=complex),
    "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "z": np.array([[1, 0], [0, -1]], dtype=complex),
}
LINE = re.compile(r"(Rz|X90|CZ)(?:\(([-+0-9.e]+)\))? q\[(\d+)\](?:, q\[(\d+)\])?")


# Circuits ---------------------------------------------------------------------------------------------------------


@cache
def retained() -> dict[str, Any]:
    """The retained b0 of the coin series: its text, note line, instruction list, region, roles and ideal law."""
    oc.verify_pins()
    text = (oc.COIN_BATCH / "b0.cq").read_text(encoding="utf-8")
    lines = text.split("\n")
    head = zd.header(cc.NQUBITS)
    if lines[: len(head)] != head or lines[-4:] != ["", "barrier q", "b = measure q", ""]:
        raise ValueError("the retained b0.cq does not carry the header and measurement the emitter writes")
    note, body = lines[len(head)], lines[len(head) + 1 : -4]
    ops: list[tuple[str, str | None, tuple[int, ...]]] = []
    for line in body:
        match = LINE.fullmatch(line)
        if match is None:
            raise ValueError(f"the retained b0.cq holds an instruction the parser does not read: {line!r}")
        gate, angle, first, second = match.groups()
        ops.append((gate, angle, (int(first),) if second is None else (int(first), int(second))))
    manifest = oc.coin_manifest()
    row = next(c for c in manifest["circuits"] if c["file"] == "b0.cq")
    template = manifest["templates"]["b0"]
    return {
        "text": text,
        "note": note,
        "ops": tuple(ops),
        "region": tuple(int(q) for q in manifest["region"]),
        "roles": {k: int(v) for k, v in template["roles"].items()},
        "cz": int(template["cz"]),
        "ideal": [float(x) for x in row["ideal"]],
        "ideal_c": [float(x) for x in template["ideal_c"]],
    }


def rx_text(steps: int) -> str:
    return f"Rx({math.pi / 2 + steps * STEP!r})"


def arm_lines(arm: str, place: dict[int, int]) -> list[str]:
    """Instruction lines of an arm with physical qubit q written as place[q]."""
    pulse, scope, steps = ARMS[arm]
    injected = () if scope is None else SCOPES[scope]
    lines = []
    for gate, angle, qubits in retained()["ops"]:
        where = ", ".join(f"q[{place[q]}]" for q in qubits)
        if gate == "X90":
            name = "X90" if pulse == "X90" else rx_text(steps if qubits[0] in injected else 0)
        else:
            name = gate if angle is None else f"{gate}({angle})"
        lines.append(f"{name} {where}")
    return lines


def arm_note(arm: str) -> str:
    pulse, scope, steps = ARMS[arm]
    if pulse == "X90":
        return retained()["note"]
    tail = "" if scope is None else f", {steps * 5:+d} degrees on {scope}"
    return f"{retained()['note']} every X90 as Rx(pi/2){tail}"


def arm_text(arm: str, place: dict[int, int], nqubits: int) -> str:
    lines = zd.header(nqubits) + [arm_note(arm)]
    return "\n".join(lines + arm_lines(arm, place) + ["", "barrier q", "b = measure q", ""])


def replay_check() -> str:
    """The emitter reproduces the retained b0.cq byte for byte; returns its sha256."""
    region = retained()["region"]
    text = arm_text(RETAINED, {q: q for q in region}, cc.NQUBITS)
    if text != retained()["text"]:
        raise ValueError("the emitter does not reproduce the retained b0.cq")
    return hashlib.sha256(text.encode()).hexdigest()


# Forward model ----------------------------------------------------------------------------------------------------


def rotation(axis: str, angle: float) -> np.ndarray:
    return math.cos(angle / 2) * np.eye(2, dtype=complex) - 1j * math.sin(angle / 2) * PAULI[axis]


def forward_laws(arm: str, world: str | None, thetas: np.ndarray, cz_phase: float = 0.0) -> np.ndarray:
    """Laws over the logical outcome index (bit v of the index is KEYS[v]) of an arm under a pulse-error world, one
    row per value of `thetas`.

    A state vector over the five region qubits per theta; every pulse on a qubit of the world's scope is preceded or
    followed by a rotation of theta about the world's axis. `world` None is the exact circuit. Every CZ applies the
    conditional phase pi + `cz_phase`."""
    ref = retained()
    region = ref["region"]
    axis_of = {q: i for i, q in enumerate(region)}
    pulse, scope, steps = ARMS[arm]
    injected = () if scope is None else SCOPES[scope]
    error_axis, order, error_scope = ("x", "before", None) if world is None else PULSE_WORLDS[world]
    faulty = () if error_scope is None else SCOPES[error_scope]
    errors = np.stack([rotation(error_axis, float(t)) for t in thetas])
    shape = (2,) * len(region)
    psi = np.zeros((len(thetas), *shape), dtype=complex)
    psi.reshape(len(thetas), -1)[:, 0] = 1.0
    index = np.indices(shape)
    for gate, angle, qubits in ref["ops"]:
        if gate == "CZ":
            both = index[axis_of[qubits[0]]] * index[axis_of[qubits[1]]]
            psi = psi * np.where(both == 1, -np.exp(1j * cz_phase), 1.0)
            continue
        q = qubits[0]
        if gate == "Rz":
            unitary = rotation("z", float(angle or 0.0))[None]
        else:
            exact = rotation("x", math.pi / 2 + (steps * STEP if pulse == "Rx" and q in injected else 0.0))
            if q in faulty:
                unitary = exact @ errors if order == "before" else errors @ exact
            else:
                unitary = exact[None]
        moved = np.moveaxis(psi, axis_of[q] + 1, -1)
        low, high = moved[..., 0], moved[..., 1]
        u = unitary[:, :, :, None, None, None, None]
        psi = np.moveaxis(
            np.stack([u[:, 0, 0] * low + u[:, 0, 1] * high, u[:, 1, 0] * low + u[:, 1, 1] * high], axis=-1),
            -1,
            axis_of[q] + 1,
        )
    prob = np.abs(psi) ** 2
    order_axes = [0, *(axis_of[ref["roles"][key]] + 1 for key in reversed(KEYS))]
    return np.asarray(prob.transpose(order_axes).reshape(len(thetas), NOUT), dtype=float)


def forward_law(arm: str, world: str | None = None, theta: float = 0.0) -> np.ndarray:
    """Law of an arm under a pulse-error world at one theta; `world` None is the exact circuit."""
    return np.asarray(forward_laws(arm, world, np.array([theta]))[0])


# Gate-noise families: one-parameter Kraus noise on the instruction list. Kind -> (amplitude damping per pulse, phase
# damping per pulse, two-qubit depolarizing per CZ, amplitude damping per CZ qubit, phase damping per CZ qubit) as
# multiples of the family's strength. hypothesis: Tuna-17's loss on b0 lies near the span of these families and of
# the two contractions of contract(); the retained b0 runs read each bit's excitation between 0.43 and 0.53 where a
# unital channel gives 0.48 to 0.50, which the damping families reproduce in sign.
GATE_KINDS: dict[str, tuple[float, float, float, float, float]] = {
    "cz_depolarizing": (0.0, 0.0, 1.0, 0.0, 0.0),
    "pulse_dephasing": (0.0, 1.0, 0.0, 0.0, 0.0),
    "cz_dephasing": (0.0, 0.0, 0.0, 0.0, 1.0),
    "cz_damping": (0.0, 0.0, 0.0, 1.0, 0.0),
    "damping_and_dephasing": (1 / 3, 1 / 3, 0.0, 1.0, 1.0),
}


def gate_noise(kind: str, strength: float) -> tuple[float, float, float, float, float]:
    a, b, c, d, e = (strength * m for m in GATE_KINDS[kind])
    return a, b, c, d, e


def damping_kraus(amplitude: float, phase: float) -> list[np.ndarray]:
    """Kraus operators of amplitude damping `amplitude` followed by phase damping `phase` on one qubit."""
    a0 = np.array([[1, 0], [0, math.sqrt(1 - amplitude)]], dtype=complex)
    a1 = np.array([[0, math.sqrt(amplitude)], [0, 0]], dtype=complex)
    p0 = np.array([[1, 0], [0, math.sqrt(1 - phase)]], dtype=complex)
    p1 = np.array([[0, 0], [0, math.sqrt(phase)]], dtype=complex)
    return [p @ a for p in (p0, p1) for a in (a0, a1) if np.any(p @ a)]


def channel_matrix(kraus: list[np.ndarray]) -> np.ndarray:
    """The channel rho -> sum K rho K^dagger as a matrix on the row-major vectorization (ket index, bra index)."""
    return np.asarray(sum(np.kron(k, k.conj()) for k in kraus))


def cz_matrix(cz_phase: float, depolarizing: float, amplitude: float, phase: float) -> np.ndarray:
    """A CZ of conditional phase pi + `cz_phase`, then two-qubit depolarizing, then damping on both qubits, as a
    16 x 16 matrix on the vectorization (ket a, ket b, bra a, bra b)."""
    identity = np.eye(2, dtype=complex)
    gate = np.diag([1, 1, 1, -np.exp(1j * cz_phase)]).astype(complex)
    out = np.kron(gate, gate.conj())
    if depolarizing:
        paulis = (identity, PAULI["x"], PAULI["y"], PAULI["z"])
        mixed = sum(np.kron(np.kron(s, t), np.kron(s, t).conj()) for s in paulis for t in paulis) / 16
        out = ((1 - depolarizing) * np.eye(16) + depolarizing * mixed) @ out
    if amplitude or phase:
        kraus = damping_kraus(amplitude, phase)
        out = (
            channel_matrix([np.kron(identity, k) for k in kraus])
            @ channel_matrix([np.kron(k, identity) for k in kraus])
            @ out
        )
    return np.asarray(out)


def gate_noise_laws(
    arm: str,
    world: str | None,
    thetas: np.ndarray,
    noise: tuple[float, float, float, float, float],
    cz_phase: float = 0.0,
    scale: float = 0.0,
) -> np.ndarray:
    """Laws over the logical outcome index of an arm under a pulse-error world and gate noise, one row per value of
    `thetas`: a density matrix over the five region qubits per theta, each pulse followed by its damping channel and
    each CZ by its depolarizing and damping channels. `scale` multiplies every pulse angle by 1 + scale."""
    pulse_amplitude, pulse_phase, cz_depolarizing, cz_amplitude, cz_phase_damping = noise
    ref = retained()
    region = ref["region"]
    n = len(region)
    axis_of = {q: i for i, q in enumerate(region)}
    pulse, scope, steps = ARMS[arm]
    injected = () if scope is None else SCOPES[scope]
    error_axis, order, error_scope = ("x", "before", None) if world is None else PULSE_WORLDS[world]
    faulty = () if error_scope is None else SCOPES[error_scope]
    errors = np.stack([rotation(error_axis, float(t)) for t in thetas])
    batch = len(thetas)
    pulse_noise = channel_matrix(damping_kraus(pulse_amplitude, pulse_phase))
    two = cz_matrix(cz_phase, cz_depolarizing, cz_amplitude, cz_phase_damping)
    rho = np.zeros((batch, *(2,) * (2 * n)), dtype=complex)
    rho.reshape(batch, -1)[:, 0] = 1.0
    for gate, angle, qubits in ref["ops"]:
        if gate == "CZ":
            a, b = axis_of[qubits[0]], axis_of[qubits[1]]
            source = (1 + a, 1 + b, 1 + n + a, 1 + n + b)
            moved = np.moveaxis(rho, source, (-4, -3, -2, -1))
            shape = moved.shape
            rho = np.moveaxis((moved.reshape(batch, -1, 16) @ two.T).reshape(shape), (-4, -3, -2, -1), source)
            continue
        q = qubits[0]
        a = axis_of[q]
        if gate == "Rz":
            unitary = rotation("z", float(angle or 0.0))[None]
        else:
            exact = rotation(
                "x", (1 + scale) * (math.pi / 2 + (steps * STEP if pulse == "Rx" and q in injected else 0.0))
            )
            if q in faulty:
                unitary = exact @ errors if order == "before" else errors @ exact
            else:
                unitary = exact[None]
        acting = np.einsum("bij,bkl->bikjl", unitary, unitary.conj()).reshape(-1, 4, 4)
        if gate != "Rz":
            acting = pulse_noise @ acting
        moved = np.moveaxis(rho, (1 + a, 1 + n + a), (-2, -1))
        shape = moved.shape
        flat = moved.reshape(batch, -1, 4)
        flat = flat @ acting[0].T if len(acting) == 1 else np.einsum("brj,bij->bri", flat, acting)
        rho = np.moveaxis(flat.reshape(shape), (-2, -1), (1 + a, 1 + n + a))
    prob = np.real(np.einsum("bijklmijklm->bijklm", rho))
    order_axes = [0, *(axis_of[ref["roles"][key]] + 1 for key in reversed(KEYS))]
    return np.asarray(prob.transpose(order_axes).reshape(batch, NOUT), dtype=float)


@cache
def pulse_table(world: str) -> np.ndarray:
    """Laws of every arm under a pulse world on THETA_FINE, shape (theta, arm, outcome)."""
    return np.stack([forward_laws(arm, world, THETA_FINE) for arm in ARM_NAMES], axis=1)


@cache
def exact_laws() -> np.ndarray:
    """Laws of every arm of the exact circuit, shape (arm, outcome)."""
    return np.stack([forward_law(arm) for arm in ARM_NAMES])


@cache
def readout_maps(world: str) -> np.ndarray:
    """The stochastic maps of a readout world on X_FINE, shape (x, outcome, outcome)."""
    family, key, state = READOUT_WORLDS[world]
    make = oc.selector_flip if family == "flip" else oc.selector_dropout
    return np.stack([make(KEYS.index(key), state, float(x)) for x in X_FINE])


def parameter_grid(world: str) -> np.ndarray:
    return THETA_FINE if world in PULSE_WORLDS else X_FINE


DATA_OUTCOMES = 8
# Share of a batch's visibility loss that depolarizes the three data bits and leaves the law of the selector and the
# coin: 0 contracts the whole law toward uniform, 1 contracts the data bits alone. A selector contrast survives the
# second kind of loss and shrinks under the first, so the share sets how far the offset and its response to an
# injected rotation shrink with the visibility. Models are computed on MIX_GRID and fitted on MIX_FINE by linear
# interpolation of the model contrasts; one share serves every batch of a series.
MIX_GRID = np.linspace(0.0, 1.0, 5)
MIX_FINE = np.linspace(0.0, 1.0, 13)
# Gate-noise families the fit carries beside the contraction shares; a caller that needs the contraction fit alone
# (a test of the decision logic) empties it before the first fit of the process.
FIT_KINDS: list[str] = list(GATE_KINDS)


def noise_models() -> tuple[str, ...]:
    """Names of the fit's noise models in the order of the leading axis of design_model and fit_batch."""
    return (*(f"contraction share {m:.4f}" for m in MIX_FINE), *FIT_KINDS)


def contract(laws: np.ndarray, retention: np.ndarray | float, mix: float) -> np.ndarray:
    """`laws`, shape (row, arm, outcome), contracted by `retention` (a scalar or one value per row): the factor
    retention ** mix mixes the law of the data bits toward uniform at fixed selector and coin, and the factor
    retention ** (1 - mix) mixes the whole law toward uniform."""
    keep = np.asarray(retention, dtype=float).reshape(-1, 1, 1)
    data, whole = keep**mix, keep ** (1.0 - mix)
    shaped = laws.reshape(*laws.shape[:-1], NOUT // DATA_OUTCOMES, DATA_OUTCOMES)
    spread = shaped.sum(-1, keepdims=True) / DATA_OUTCOMES
    mixed = (data[..., None] * shaped + (1 - data[..., None]) * spread).reshape(laws.shape)
    return np.asarray(whole * mixed + (1 - whole) / NOUT)


def fine_mix(models: np.ndarray) -> np.ndarray:
    """Values on MIX_FINE of an array whose leading axis runs over MIX_GRID, by linear interpolation."""
    position = MIX_FINE * (len(MIX_GRID) - 1)
    low = np.minimum(position.astype(int), len(MIX_GRID) - 2)
    weight = (position - low).reshape(-1, *([1] * (models.ndim - 1)))
    return np.asarray((1 - weight) * models[low] + weight * models[low + 1])


def world_laws(world: str, retention: np.ndarray | float, arms: tuple[str, ...], mix: float = 0.0) -> np.ndarray:
    """Device laws of `arms` on the world's parameter grid before the assignment readout, shape (parameter, arm,
    outcome): the world's law under contract() at `retention` (a scalar or one value per parameter) and `mix`."""
    picked = [ARM_NAMES.index(a) for a in arms]
    if world in PULSE_WORLDS:
        return contract(pulse_table(world)[:, picked], retention, mix)
    exact = np.broadcast_to(exact_laws()[picked][None], (len(X_FINE), len(picked), NOUT))
    return np.asarray(np.einsum("xij,xaj->xai", readout_maps(world), contract(exact, retention, mix)))


def selector_contrast(laws: np.ndarray) -> np.ndarray:
    """P(selector 0 | coin 1) - P(selector 0 | coin 0) along the last axis."""
    plus, minus = laws[..., HALF:], laws[..., :HALF]
    return np.asarray(plus[..., :8].sum(-1) / plus.sum(-1) - minus[..., :8].sum(-1) / minus.sum(-1))


def visibility(laws: np.ndarray) -> np.ndarray:
    """Signed mean over the four bins y = (d0, d1) of c(y) = P(s = 0 | y, coin 1) - P(s = 0 | y, coin 0) along b0's
    ideal signs, with d2 summed out along the last axis (laws or counts).

    b0's ideal c depends on d0 and d1 alone, and d2 is read on q11, whose e10 moved between 0.03 and 0.43 over the
    retained brackets of the one-CZ series; summed over d2, an assignment error of q11 that is independent of the
    other bits leaves this statistic and the selector contrast unchanged."""
    ideal = np.array(retained()["ideal_c"]).reshape(2, 4)
    if not np.all(np.sign(ideal[0]) == np.sign(ideal[1])):
        raise ValueError("b0's ideal contrast changes sign with d2")
    sign = np.sign(ideal[0])
    # Last axis: coin, selector, d2, (d1, d0); the d2 axis is summed.
    piles = np.asarray(laws, dtype=float).reshape(*np.shape(laws)[:-1], 2, 2, 2, 4).sum(-2)

    def conditional(pile: np.ndarray) -> np.ndarray:
        total = pile[..., 0, :] + pile[..., 1, :]
        return np.divide(pile[..., 0, :], total, out=np.zeros_like(total), where=total > 0)

    return np.asarray(((conditional(piles[..., 1, :, :]) - conditional(piles[..., 0, :, :])) * sign).mean(-1))


def d2_split(laws: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The selector contrast among outcomes with d2 = 1 less the one among d2 = 0, along the last axis (laws or
    counts), and its binomial standard error when the entries are counts.

    Reported beside the decision and outside it: at the design visibility an over-rotation about x of every pulse
    gives a larger contrast at d2 = 1, an under-rotation about x and a rotation about y or z a larger one at
    d2 = 0, and a selector readout map the same contrast at both under a contraction and within 0.004 of it under
    the gate-noise families (tests/scripts/test_qi_pathion_null_rotation_scan.py). An assignment error of d2's
    qubit mixes the two groups and shrinks the difference toward zero."""
    # Last axis: coin, selector, d2, (d1, d0); the (d1, d0) axis is summed.
    piles = np.asarray(laws, dtype=float).reshape(*np.shape(laws)[:-1], 2, 2, 2, 4).sum(-1)
    total = piles.sum(-2)
    share = np.divide(piles[..., 0, :], total, out=np.zeros_like(total), where=total > 0)
    variance = np.divide(share * (1 - share), total, out=np.zeros_like(total), where=total > 0)
    contrast = share[..., 1, :] - share[..., 0, :]
    return np.asarray(contrast[..., 1] - contrast[..., 0]), np.asarray(np.sqrt(variance.sum((-1, -2))))


def design_matrix() -> np.ndarray:
    """Assignment matrix of the five logical bits at the retained readout rates of the coin series' region."""
    return cc.readout_matrix(cc.retained_readout(retained()["region"]), retained()["roles"])


def read(laws: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return np.asarray(laws @ matrix.T)


RETENTION_GRID = np.linspace(0.05, 1.0, 20)


def retention_for(world: str, matrix: np.ndarray, center_visibility: float, mix: float) -> np.ndarray:
    """Per parameter value, the retention at which the world's center arm reads `center_visibility` at the
    contraction share `mix`; a value the retention grid does not reach clips to its end."""
    seen = np.stack(
        [visibility(read(world_laws(world, float(r), (CENTER,), mix), matrix))[:, 0] for r in RETENTION_GRID]
    )
    out = np.empty(seen.shape[1])
    for j in range(seen.shape[1]):
        column = seen[:, j]
        order = np.argsort(column)
        out[j] = float(np.interp(center_visibility, column[order], RETENTION_GRID[order]))
    return out


# Gate-noise tables. A family's strength grid spans the exact circuit's center visibility VISIBILITY_SPAN through the
# design readout in STRENGTH_POINTS equal visibility steps; a batch takes the strength that reproduces its center
# arm's visibility by linear interpolation of the model contrasts between grid strengths, clipped at the grid ends.
STRENGTH_POINTS = 12
VISIBILITY_SPAN = (0.75, 0.20)
TABLE_VERSION = 1


def exact_gate_visibility(kind: str, strength: float) -> float:
    law = gate_noise_laws(CENTER, None, np.zeros(1), gate_noise(kind, strength))[0]
    return float(visibility(read(law, design_matrix())))


def strength_at(kind: str, target: float) -> float:
    return float(brentq(lambda s: exact_gate_visibility(kind, s) - target, 1e-7, 0.6, xtol=1e-12))


@cache
def strength_grid(kind: str) -> np.ndarray:
    return np.array([strength_at(kind, v) for v in np.linspace(*VISIBILITY_SPAN, STRENGTH_POINTS)])


@cache
def design_strength(kind: str) -> float:
    """The strength at which the exact circuit's center arm reads the visibility of contract() at DESIGN_RETENTION."""
    center = exact_laws()[ARM_NAMES.index(CENTER)][None, None]
    target = float(visibility(read(contract(center, DESIGN_RETENTION, 0.0)[0, 0], design_matrix())))
    return strength_at(kind, target)


@cache
def table_directory() -> Path:
    """Scratch directory of the gate-noise tables, keyed by every input a table depends on."""
    key = json.dumps(
        [
            TABLE_VERSION,
            hashlib.sha256(retained()["text"].encode()).hexdigest(),
            GATE_KINDS,
            ARMS,
            SCOPES,
            PULSE_WORLDS,
            [float(THETA_FINE[0]), float(THETA_FINE[-1]), len(THETA_FINE)],
            [float(X_FINE[0]), float(X_FINE[-1]), len(X_FINE)],
            [STRENGTH_POINTS, *VISIBILITY_SPAN, DESIGN_RETENTION],
            [float(v) for v in design_matrix().ravel()],
        ],
        sort_keys=True,
    )
    root = Path(os.environ.get("GOROROBA_SCAN_TABLES") or Path(tempfile.gettempdir()) / "gororoba-quantum-scan-tables")
    path = root / hashlib.sha256(key.encode()).hexdigest()[:20]
    path.mkdir(parents=True, exist_ok=True)
    return path


def compute_gate_table(kind: str, world: str | None, design: bool) -> np.ndarray:
    """Laws of every arm under a family: shape (strength, parameter, arm, outcome) on the strength grid, or
    (parameter, arm, outcome) at the design strength; `world` None is the exact circuit, one parameter row."""
    thetas = np.zeros(1) if world is None else THETA_FINE
    strengths = [design_strength(kind)] if design else list(strength_grid(kind))
    table = np.stack(
        [
            np.stack([gate_noise_laws(arm, world, thetas, gate_noise(kind, float(s))) for arm in ARM_NAMES], axis=1)
            for s in strengths
        ]
    )
    return np.asarray(table[0] if design else table.astype(np.float32))


@cache
def gate_table(kind: str, world: str | None, design: bool = False) -> np.ndarray:
    """compute_gate_table from the scratch directory, computed and stored there on first use."""
    path = table_directory() / f"{kind}-{world or 'exact'}-{'design' if design else 'grid'}.npy"
    if path.is_file():
        return np.asarray(np.load(path))
    table = compute_gate_table(kind, world, design)
    scratch = path.with_name(f".{path.name}.{os.getpid()}.npy")
    np.save(scratch, table)
    os.replace(scratch, path)
    return table


def table_item(item: tuple[str, str | None, bool]) -> tuple[int, ...]:
    return tuple(gate_table(*item).shape)


def build_gate_tables(kinds: list[str] | None = None, grid: bool = True) -> int:
    """Fill the scratch directory with every table of `kinds` (the fit's families by default) over the worker pool;
    `grid` False builds the design tables alone, which the operating characteristics read."""
    worlds: list[str | None] = [None, *(w for w in SIMULATED_WORLDS if w in PULSE_WORLDS)]
    items = [
        (kind, world, design)
        for kind in (FIT_KINDS if kinds is None else kinds)
        for world in worlds
        for design in ((True, False) if grid else (True,))
    ]
    return len(ordered_map(table_item, items, min_items=1))


def gate_world_laws(world: str, kind: str, arms: tuple[str, ...], design: bool = False) -> np.ndarray:
    """world_laws under a gate-noise family: shape (parameter, arm, outcome) at the design strength, or (strength,
    parameter, arm, outcome) on the strength grid."""
    picked = [ARM_NAMES.index(a) for a in arms]
    if world in PULSE_WORLDS:
        axis, order, scope = PULSE_WORLDS[world]
        source = world if order == "before" else f"pulse_{axis}_before_{scope}"
        table = gate_table(kind, source, design)[..., picked, :]
        # An "after" world about z is its "before" world; about y it is the "before" world at the opposite angle.
        return np.asarray(table[..., ::-1, :, :] if order == "after" and axis == "y" else table)
    exact = gate_table(kind, None, design)[..., 0, picked, :]
    maps = readout_maps(world)
    return np.asarray(np.einsum("xij,...aj->...xai", maps, exact))


def gate_fit_model(
    world: str, kind: str, arms: tuple[str, ...], matrix: np.ndarray, center_visibility: float
) -> tuple[np.ndarray, np.ndarray]:
    """Per parameter value, the family's model contrasts of `arms` (parameter, arm) and strength (parameter) at
    which the world's center arm reads `center_visibility` through `matrix`."""
    seen = read(gate_world_laws(world, kind, (*arms, CENTER)).astype(float), matrix)
    visible = visibility(seen[:, :, -1])
    contrast = selector_contrast(seen[:, :, :-1])
    grid = strength_grid(kind)
    count = len(grid)
    low = np.clip((visible > center_visibility).sum(0) - 1, 0, count - 2)
    column = np.arange(visible.shape[1])
    upper, lower = visible[low, column], visible[low + 1, column]
    span = np.where(upper != lower, upper - lower, 1.0)
    weight = np.clip((upper - center_visibility) / span, 0.0, 1.0)
    model = (1 - weight)[:, None] * contrast[low, column] + weight[:, None] * contrast[low + 1, column]
    return np.asarray(model), np.asarray((1 - weight) * grid[low] + weight * grid[low + 1])


# Model contrasts at the design retention and readout, keyed (world, arms, fitted families); design_model fills it.
DESIGN_MODELS: dict[tuple[str, tuple[str, ...], tuple[str, ...]], np.ndarray] = {}


def design_model(world: str, arms: tuple[str, ...]) -> np.ndarray:
    """Raw selector contrasts of `arms` at the design visibility and readout, shape (noise model of noise_models(),
    parameter, arm): the contraction shares at DESIGN_RETENTION, then each family of FIT_KINDS at its design
    strength."""
    key = (world, arms, tuple(FIT_KINDS))
    if key not in DESIGN_MODELS:
        matrix = design_matrix()
        shares = fine_mix(
            np.stack(
                [selector_contrast(read(world_laws(world, DESIGN_RETENTION, arms, float(m)), matrix)) for m in MIX_GRID]
            )
        )
        families = [
            selector_contrast(read(gate_world_laws(world, kind, arms, design=True), matrix))[None] for kind in FIT_KINDS
        ]
        DESIGN_MODELS[key] = np.concatenate([shares, *families])
    return DESIGN_MODELS[key]


def fit_batch(
    arms: tuple[str, ...],
    contrasts: np.ndarray,
    errors: np.ndarray,
    matrix: np.ndarray | None,
    center_visibility: float | None,
) -> dict[str, dict[str, np.ndarray]]:
    """Per world and noise model of noise_models(), the least chi-square of a batch's raw selector contrasts over
    the world's parameter: arrays "chi2", "parameter", "retention" (one value per noise model; a gate-noise family
    reports its strength there) and "predicted" (noise model, arm).

    With an assignment `matrix` and the center arm's visibility, each parameter value and noise model takes the
    retention or strength at which the world reproduces that visibility. `matrix` None fits at the design visibility
    and readout (the operating characteristics and the calibration)."""
    rows: dict[str, dict[str, np.ndarray]] = {}
    take = np.arange(len(noise_models()))
    for world in WORLDS:
        grid = parameter_grid(world)
        if matrix is None or center_visibility is None:
            keep = np.concatenate(
                [
                    np.full((len(MIX_FINE), len(grid)), DESIGN_RETENTION),
                    *(np.full((1, len(grid)), design_strength(kind)) for kind in FIT_KINDS),
                ]
            )
            model = design_model(world, arms)
        else:
            kept = np.stack([retention_for(world, matrix, center_visibility, float(m)) for m in MIX_GRID])
            model = fine_mix(
                np.stack(
                    [
                        selector_contrast(read(world_laws(world, kept[i], arms, float(m)), matrix))
                        for i, m in enumerate(MIX_GRID)
                    ]
                )
            )
            keep = fine_mix(kept)
            for kind in FIT_KINDS:
                family, strength = gate_fit_model(world, kind, arms, matrix, center_visibility)
                model = np.concatenate([model, family[None]])
                keep = np.concatenate([keep, strength[None]])
        curve = (((model - contrasts) / errors) ** 2).sum(-1)
        best = curve.argmin(1)
        rows[world] = {
            "chi2": curve[take, best],
            "parameter": grid[best],
            "retention": keep[take, best],
            "predicted": model[take, best],
        }
    return rows


# Series -----------------------------------------------------------------------------------------------------------


def scan_arms(kind: str, replicate: int) -> list[str]:
    scope, steps = SCANS[kind]
    first, last = arm_name(scope, -steps), arm_name(scope, steps)
    return [first, CENTER, last] if replicate == 0 else [last, CENTER, first]


def batch_order() -> list[tuple[str, int]]:
    """(kind, replicate) of the ten data batches: the four scans and the bridge, then the same list backwards, so the
    replicates of one kind sit at mirrored positions."""
    first = [*((kind, 0) for kind in SCANS), ("bridge", 0)]
    return first + [(kind, 1) for kind, _ in reversed(first)]


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: a readout batch, then each data batch of batch_order followed by a readout
    batch, so every data batch sits between two brackets. QX: every arm, three to a batch."""
    rows: list[dict[str, Any]] = []

    def data(arm: str) -> dict[str, Any]:
        pulse, scope, steps = ARMS[arm]
        return {
            "file": f"{arm}.cq",
            "kind": "data",
            "template": "b0",
            "arm": {"pulse": pulse, "scope": scope, "steps": steps},
        }

    def add(kind: str, replicate: int | None, circuits: list[dict[str, Any]]) -> None:
        rows.append({"batch": f"batch-{len(rows):02d}", "kind": kind, "replicate": replicate, "circuits": circuits})

    if series_name == QX_SERIES:
        for start in range(0, len(ARM_NAMES), QX_BATCH_CIRCUITS):
            add("control", None, [data(a) for a in ARM_NAMES[start : start + QX_BATCH_CIRCUITS]])
        return rows
    brackets = [{"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"}]
    add("readout", None, brackets)
    for position, (kind, replicate) in enumerate(batch_order()):
        if kind == "bridge":
            names = [RETAINED, CENTER, RETAINED] if replicate == 0 else [CENTER, RETAINED, CENTER]
            circuits = []
            for n, arm in enumerate(names):
                record = data(arm)
                # A batch holds one file per name, so the arm that runs twice gets a second file of the same bytes.
                if names.index(arm) != n:
                    record["file"] = f"{arm}-repeat.cq"
                circuits.append(record)
        else:
            circuits = [data(arm) for arm in scan_arms(kind, replicate)]
        add(kind, replicate, circuits)
        add("readout", None, brackets if position % 2 else list(reversed(brackets)))
    return rows


def row_shots(row: dict[str, Any]) -> int:
    return READOUT_SHOTS if row["kind"] == "readout" else SCAN_SHOTS


# Fields of a batch's cases.json that differ between batches of one series.
BATCH_FIELDS = ("batch", "circuits", "shots", "kind", "replicate")


def arm_of(file: str) -> str:
    return file.removesuffix(".cq").removesuffix("-repeat")


def adequacy_limit(batches: int) -> float:
    """Chi-square bound of a world over `batches` batches: three contrasts and one fitted parameter per batch, and
    one noise model for the series."""
    return float(chi2_law.ppf(1 - ADEQUACY_ALPHA, 2 * batches - 1))


def preregistered() -> dict[str, str]:
    z = Z_RESOLVE
    return {
        "estimates": "per data circuit, the raw selector contrast P(s=0 | coin read 1) - P(s=0 | coin read 0) with its "
        "binomial standard error, and the visibility of the center arm of each scan batch",
        "guard": "a data batch is admitted when e01 and e10 of each qubit the statistics read (d0, d1, the selector "
        f"and the coin) change by at most {GUARD_LIMIT} between the readout batch before it and the one after; d2 is "
        "summed out of both statistics and its qubit's rates are reported unguarded; the decision needs at least one "
        "admitted batch of every scan kind, otherwise it reads unresolved_guard",
        "control": f"the inverse-variance mean of the center arm's contrast over the admitted scan batches exceeds {z} "
        f"standard errors; within {z} standard errors of zero the offset is absent, below that it is reversed, and "
        "either way no mechanism is decided",
        "fit": "per admitted scan batch, world and noise model, the least chi-square of the batch's three "
        "contrasts over the world's one parameter, at the retention or noise strength that reproduces the center "
        "arm's visibility through the mean assignment matrix of the two brackets; the noise models are "
        f"{len(MIX_FINE)} contraction shares (the part of the visibility loss that depolarizes the data bits alone, "
        f"0 to 1) and the gate-noise families {', '.join(GATE_KINDS)}; a world's chi-square is the sum over the "
        "admitted scan batches at the one noise model that makes the sum least",
        "adequate": f"a world is adequate when its chi-square is at most the {1 - ADEQUACY_ALPHA} quantile of the "
        "chi-square law with two degrees of freedom per admitted batch less one for the noise model",
        "class": "three classes of worlds: a rotation about x added to the pulses (on all pulses, on q8's or on q4's), "
        "a rotation about y or z added before or after them (same scopes), and the two selector readout worlds; a "
        f"class is preferred when its best world is adequate and the best world of each other class sits at least "
        f"{SEPARATION} above it; the x class is excluded when the two other classes lead, the leader is adequate, the "
        f"best x world is inadequate and it sits at least {SEPARATION} above the leader; every label is a preference "
        "among the modeled worlds and noise models",
        "bridge": "Rx(pi/2) and X90 read the same selector contrast when both bridge batches are admitted, their "
        f"within-batch differences of the b0-rx and b0 contrasts agree within {z} standard errors of each other, and "
        f"the pooled difference is within {z} standard errors of zero; a class label stands only when the bridge "
        "holds, otherwise the series reads unresolved_bridge and reports the class of the Rx circuits. The bridge "
        "compares the two gates at zero injected angle and leaves untested that an injected Rx angle acts as a "
        "scaled X90 pulse",
        "qx": "every circuit within twice the sampling floor of its ideal law",
    }


OUTCOMES: dict[str, tuple[str, str]] = {
    "unresolved_guard": (
        "unresolved: a scan kind holds no batch that passes the readout admission",
        "unchanged; the numbers are reported",
    ),
    "unresolved_bridge": (
        "unresolved: the scan classes the Rx circuits (numbers.rx_label) and the bridge does not show that Rx(pi/2) "
        "reads as X90, because the two read different contrasts, the two bridge batches disagree or a bridge batch "
        "failed the readout admission",
        "unchanged; the numbers are reported",
    ),
    "offset_absent": (
        "offset absent: the center arm's contrast reads within the resolution of zero; nothing about the mechanism "
        "is decided",
        "unchanged",
    ),
    "offset_reversed": (
        "offset reversed: the center arm's contrast reads below zero, where the retained runs read above it; nothing "
        "about the mechanism is decided",
        "unchanged; the numbers are reported",
    ),
    "pulse_x": (
        "the x class is preferred among the modeled worlds: the selector offset follows the injected rotation as a "
        "coherent over- or under-rotation of the pulses predicts",
        "see X_ROW: the effect depends on the sign and scope of the fit",
    ),
    "pulse_other": (
        "the y-or-z class is preferred among the modeled worlds: the scan follows a pulse rotation about y or z. A "
        "conditional-phase error of the CZ gates can read here as well (prediction.json, unmodeled)",
        "not supported as stated: the scan prefers a coherent gate error other than a rotation about x, a pulse "
        "rotation about y or z or a CZ phase error, which it leaves apart",
    ),
    "readout": (
        "the readout class is preferred among the modeled worlds: the response curve of an exact pulse stays in "
        "place and the offset adds to it",
        f"not supported: each modeled pulse rotation sits at least {SEPARATION} in chi-square above a selector "
        "readout map; a mechanism outside the modeled worlds stays open",
    ),
    "x_excluded": (
        "the x class is excluded among the modeled worlds and the scan leaves a selector readout map and a pulse "
        "rotation about y or z apart by less than the separation",
        "not supported: no modeled rotation about x is adequate under any noise model of the fit; the surviving "
        "mechanism is undecided",
    ),
    "unresolved_both": (
        "unresolved: no class is preferred by the separation and the x class is not excluded",
        "unchanged; the numbers are reported",
    ),
    "unresolved_none": (
        "unresolved: the best world is not adequate; the scan matches no modeled mechanism",
        "unchanged; the numbers are reported",
    ),
}
DECIDING = ("pulse_x", "pulse_other", "readout", "x_excluded")
# Effect of a pulse_x label on A5-186, which names one over-rotation of the X90 pulse: True when the best x world
# rotates every pulse and every admitted batch fits a positive angle.
X_ROW = {
    True: "survives as an over-rotation of every pulse: its falsifier, a response curve that stays in place under "
    "the injected rotation, is unmet. The fitted angle and noise model are reported beside the row's +0.03 "
    "rad, which the row took from a model that contracts nothing; angles that differ between qubits are outside "
    "the model",
    False: "amended: a rotation about x on the pulses stands, and its sign or scope differs from the single "
    "over-rotation the row names (an under-rotation, q8's pulses alone, or signs that differ between batches); "
    "numbers.best_world, best_parameters and x_scope_margin state the fit",
}
TRANSFER = {
    True: "Rx(pi/2) and X90 read the same selector contrast inside both bridge batches, so the class of the Rx "
    "circuits is read as the class of the retained X90 circuit at zero injected angle",
    False: "Rx(pi/2) and X90 read different contrasts inside the bridge batches, the two bridge batches disagree, or "
    "a bridge batch failed the readout admission: the scan classes the Rx circuits and decides nothing about the "
    "retained X90 circuit",
}


def series(backend: dict[str, Any], series_name: str, nqubits: int, place: dict[int, int]) -> dict[str, str]:
    ref = retained()
    region = ref["region"]
    register = [place[q] for q in region]
    files: dict[str, str] = {}
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "region": list(region),
        "placement": {str(q): place[q] for q in region},
        "register": register,
        "qrng_draw": OC_DRAW,
        "guard_qubits": [place[ref["roles"][k]] for k in GUARD_ROLES],
        "templates": {
            "b0": {
                "block": "b0",
                "operand": list(oc.OPERAND),
                "basis": list(oc.BASIS_VECTORS),
                "coset": 0,
                "cz": ref["cz"],
                "roles": {k: place[q] for k, q in ref["roles"].items()},
                "ideal_c": ref["ideal_c"],
            }
        },
        "retained_b0": {"cases_sha256": oc.COIN_PINS["cases.json"], "circuit_sha256": oc.COIN_PINS["b0.cq"]},
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_rows(series_name):
        shots = QX_SHOTS if series_name == QX_SERIES else row_shots(row)
        circuits: list[dict[str, Any]] = []
        for spec in row["circuits"]:
            record = dict(spec)
            if spec["kind"] == "readout":
                text = cc.readout_text(nqubits, spec["file"] == "readout-1.cq", register)
            else:
                arm = arm_of(spec["file"])
                text = arm_text(arm, place, nqubits)
                record["ideal"] = [round(float(x), 12) for x in forward_law(arm)]
            record["sha256"] = hashlib.sha256(text.encode()).hexdigest()
            circuits.append(record)
            files[f"{row['batch']}/{spec['file']}"] = text
        manifest = {
            "schema": SCHEMA,
            **common,
            "shots": shots,
            "batch": row["batch"],
            "kind": row["kind"],
            "replicate": row["replicate"],
            "circuits": circuits,
        }
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "kind": row["kind"], "files": [c["file"] for c in circuits]})
    files["cases.json"] = (
        json.dumps({"schema": SERIES_SCHEMA, "backend": backend["identifier"], "batches": batches}, indent=1) + "\n"
    )
    return files


def build() -> dict[str, dict[str, str]]:
    tuna, qx = zd.catalogue_check()
    region = retained()["region"]
    replay_check()
    return {
        TUNA_SERIES: series(tuna, TUNA_SERIES, cc.NQUBITS, {q: q for q in region}),
        QX_SERIES: series(qx, QX_SERIES, QX_QUBITS, {q: i for i, q in enumerate(region)}),
    }


def design() -> dict[str, Any]:
    """Jobs, shots, standard errors and seconds of the Tuna-17 series."""
    timing = oc.coin_timing()
    rows = batch_rows(TUNA_SERIES)
    jobs = sum(len(r["circuits"]) for r in rows)
    shots_total = sum(row_shots(r) * len(r["circuits"]) for r in rows)
    return {
        "contrast_se": round(1.0 / math.sqrt(SCAN_SHOTS), 6),
        "jobs": jobs,
        "batches": len(rows),
        "data_batches": sum(1 for r in rows if r["kind"] != "readout"),
        "shots_total": shots_total,
        "execution_seconds_range": [
            round(jobs * 2.6 + shots_total * 0.53e-3, 1),
            round(jobs * 2.6 + shots_total * timing["seconds_per_shot_max"], 1),
        ],
        "longest_job_seconds": round(2.6 + SCAN_SHOTS * timing["seconds_per_shot_max"], 1),
        "job_seconds_limit": 300,
        "pause_seconds_per_batch": PAUSE_CEILING,
        "pause_seconds_total": PAUSE_CEILING * (len(rows) - 1),
        "coin_series_timing": timing,
    }


# Decisions --------------------------------------------------------------------------------------------------------


def classify(best: dict[str, float], limit: float) -> str:
    """Decision label from the chi-square of each class's best world and the adequacy bound."""
    order = sorted(best, key=lambda k: best[k])
    lead, second = order[0], order[1]
    if best[lead] > limit:
        return "unresolved_none"
    if best[second] - best[lead] >= SEPARATION:
        return CLASS_LABEL[lead]
    if "x" not in (lead, second) and best["x"] > limit and best["x"] - best[lead] >= SEPARATION:
        return "x_excluded"
    return "unresolved_both"


def decide(
    batches: list[dict[str, Any]],
    bridge: list[tuple[float, float]] | None,
    matrix_of: Any | None,
    transfer: bool = False,
) -> dict[str, Any]:
    """The preregistered decision from the scan batches.

    Each batch: {"kind", "arms", "contrasts", "errors", "center_visibility", "admitted", "name"}; `matrix_of(batch)`
    gives its assignment matrix, and `matrix_of` None fits every batch at the design retention and readout; `bridge`
    lists the within-batch difference of b0-rx and b0 of each bridge batch (value, se), None unless every bridge
    batch was admitted. `transfer` True (the hardware analysis) lets a class label stand only when the bridge holds;
    False (the operating characteristics and the calibration) leaves the bridge out."""
    admitted = [b for b in batches if b["admitted"]]
    numbers: dict[str, Any] = {"admitted_batches": [b["name"] for b in admitted]}
    if {b["kind"] for b in admitted} != set(SCANS):
        return {"label": "unresolved_guard", "numbers": numbers}
    center = oc.pooled([(float(b["contrasts"][1]), float(b["errors"][1])) for b in admitted])
    numbers["center_contrast"] = list(center)
    holds = False
    if bridge is not None:
        joint = oc.pooled(bridge)
        agree = all(
            abs(a[0] - b[0]) <= Z_RESOLVE * math.hypot(a[1], b[1]) for i, a in enumerate(bridge) for b in bridge[:i]
        )
        holds = agree and abs(joint[0]) <= Z_RESOLVE * joint[1]
        numbers |= {
            "bridge_difference": list(joint),
            "bridge_batch_differences": [list(d) for d in bridge],
            "bridge_batches_agree": agree,
        }
    if transfer:
        numbers["bridge_holds"] = holds
        numbers["transfer"] = TRANSFER[holds]
    if abs(center[0]) <= Z_RESOLVE * center[1]:
        return {"label": "offset_absent", "numbers": numbers}
    if center[0] < 0:
        return {"label": "offset_reversed", "numbers": numbers}
    by_share = {world: np.zeros(len(noise_models())) for world in WORLDS}
    rows_of: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    for b in admitted:
        rows_of[b["name"]] = fit_batch(
            tuple(b["arms"]),
            np.array(b["contrasts"]),
            np.array(b["errors"]),
            None if matrix_of is None else matrix_of(b),
            b["center_visibility"],
        )
        for world, row in rows_of[b["name"]].items():
            by_share[world] += row["chi2"]
    share = {world: int(np.argmin(curve)) for world, curve in by_share.items()}
    totals = {world: float(by_share[world][share[world]]) for world in WORLDS}
    fits = {
        name: {
            world: {
                "chi2": float(row["chi2"][share[world]]),
                "parameter": float(row["parameter"][share[world]]),
                "retention": float(row["retention"][share[world]]),
                "predicted": [float(v) for v in row["predicted"][share[world]]],
            }
            for world, row in rows.items()
        }
        for name, rows in rows_of.items()
    }
    limit = adequacy_limit(len(admitted))
    leaders = {name: min(worlds, key=lambda w: totals[w]) for name, worlds in CLASSES.items()}
    scopes = sorted(totals[w] for w in CLASSES["x"])
    numbers |= {
        "chi2": {w: round(v, 3) for w, v in totals.items()},
        "noise_model": {w: noise_models()[i] for w, i in share.items()},
        "adequacy_limit": round(limit, 3),
        "best_world": leaders,
        "best_parameters": {name: {b: fits[b][w]["parameter"] for b in fits} for name, w in leaders.items()},
        "x_scope_margin": round(scopes[1] - scopes[0], 3),
        "fits": fits,
    }
    label = classify({name: totals[w] for name, w in leaders.items()}, limit)
    if transfer and not holds and label in DECIDING:
        numbers["rx_label"] = label
        label = "unresolved_bridge"
    return {"label": label, "numbers": numbers}


def outcome(decision: dict[str, Any]) -> dict[str, Any]:
    text, row = OUTCOMES[decision["label"]]
    out = {**decision, "outcome": text, "a5_186": row, "decided": decision["label"] in DECIDING}
    if decision["label"] == "pulse_x":
        numbers = decision["numbers"]
        every_pulse = PULSE_WORLDS[numbers["best_world"]["x"]][2] == "all"
        over = every_pulse and all(v > 0 for v in numbers["best_parameters"]["x"].values())
        out |= {"a5_186": X_ROW[over], "x_over_rotation_of_every_pulse": over}
    return out


# Predictions ------------------------------------------------------------------------------------------------------


def sized(world: str, contrast: float = DESIGN_CONTRAST, mix: float = 0.0, family: str | None = None) -> list[float]:
    """Parameter values at which the world's center arm reads `contrast` at the design visibility and readout, under
    the contraction share `mix` or, when named, the gate-noise `family` at its design strength."""
    grid = parameter_grid(world)
    if family is None:
        laws = world_laws(world, DESIGN_RETENTION, (CENTER,), mix)
    else:
        laws = gate_world_laws(world, family, (CENTER,), design=True)
    curve = selector_contrast(read(laws, design_matrix()))[:, 0] - contrast
    roots = []
    for j in range(len(grid) - 1):
        if curve[j] == 0.0 or curve[j] * curve[j + 1] < 0:
            roots.append(float(brentq(lambda t: float(np.interp(t, grid, curve)), grid[j], grid[j + 1])))
    return roots


def predicted_contrasts(
    world: str | None, parameter: float, mix: float = 0.0, family: str | None = None
) -> dict[str, float]:
    """Raw selector contrast of every arm at the design visibility and readout, under the contraction share `mix`
    or the gate-noise `family`; `world` None is the exact circuit."""
    matrix = design_matrix()
    if world is None:
        if family is None:
            laws = contract(exact_laws()[None], DESIGN_RETENTION, mix)[0]
        else:
            laws = gate_table(family, None, True)[0].astype(float)
    else:
        grid = parameter_grid(world)
        if family is None:
            table = world_laws(world, DESIGN_RETENTION, ARM_NAMES, mix)
        else:
            table = gate_world_laws(world, family, ARM_NAMES, design=True)
        j = int(np.clip(np.searchsorted(grid, parameter) - 1, 0, len(grid) - 2))
        weight = (parameter - grid[j]) / (grid[j + 1] - grid[j])
        laws = (1 - weight) * table[j] + weight * table[j + 1]
    return {arm: round(float(v), 5) for arm, v in zip(ARM_NAMES, selector_contrast(read(laws, matrix)), strict=True)}


# Truth worlds of the operating characteristics: (label, world or None, branch index into sized() or None, sign of
# the parameter the label names).
TRUTHS: tuple[tuple[str, str | None, int | None, int], ...] = (
    ("no offset", None, None, 0),
    ("x over-rotation, all pulses", "pulse_x_before_all", 1, 1),
    ("x under-rotation, all pulses", "pulse_x_before_all", 0, -1),
    ("x over-rotation, q8 pulses", "pulse_x_before_q8", 1, 1),
    ("x over-rotation, q8 pulses, upper root", "pulse_x_before_q8", 2, 1),
    ("x under-rotation, q8 pulses", "pulse_x_before_q8", 0, -1),
    ("y rotation before, all pulses", "pulse_y_before_all", 1, 1),
    ("z rotation before, all pulses", "pulse_z_before_all", 0, -1),
    ("selector flip when q12 reads 0", "selector_flip_q12_0", 0, 1),
    ("selector dropout when the coin reads 1", "selector_dropout_coin_1", 0, 1),
)
# Label of a truth one of whose rounds has no parameter of the named branch and sign at the round's center contrast.
UNREACHABLE = "truth_unreachable"


class UnreachableTruth(ValueError):
    """A world has no parameter on the requested branch at the requested center contrast."""


def truth_parameter(
    world: str | None,
    branch: int | None,
    contrast: float,
    mix: float = 0.0,
    family: str | None = None,
    sign: int = 0,
) -> float:
    """The parameter of a truth: root `branch` of sized(), which carries `sign` when a sign is named. A center
    contrast the branch does not reach raises UnreachableTruth; another root never stands in for it."""
    if world is None or branch is None:
        return 0.0
    roots = sized(world, contrast, mix, family)
    if branch >= len(roots) or (sign and math.copysign(1, roots[branch]) != sign):
        raise UnreachableTruth(f"{world} has roots {roots} at a center contrast of {contrast}, none on branch {branch}")
    return roots[branch]


# An "after" world repeats its "before" world's least chi-square (PULSE_WORLDS), so the simulation fits one of each.
SIMULATED_WORLDS = tuple(w for w in WORLDS if "_after_" not in w)


def simulated_labels(noise: np.ndarray, means: np.ndarray) -> list[str]:
    """Decision labels of simulated series at the design retention and readout: `noise` holds standard normal draws,
    shape (series, scan batch, 3), and `means` the true contrasts, shape (scan batch, 3).

    The arithmetic is decide()'s with every batch admitted, taken over all series at once: the chi-square of a world
    on its parameter grid is |c|^2 - 2 c.m + |m|^2 over the three contrasts, summed over the batches per contraction
    share and then least over the shares."""
    error = 1.0 / math.sqrt(SCAN_SHOTS)
    contrasts = means[None] + error * noise
    scans = [(k, r) for k, r in batch_order() if k != "bridge"]
    totals: dict[str, np.ndarray] = {}
    for world in SIMULATED_WORLDS:
        by_share = np.zeros((len(noise), len(noise_models())))
        for n, (kind, replicate) in enumerate(scans):
            seen = contrasts[:, n, :]
            norm = (seen**2).sum(1)[:, None]
            for i, model in enumerate(design_model(world, tuple(scan_arms(kind, replicate)))):
                by_share[:, i] += (norm - 2.0 * seen @ model.T + (model**2).sum(1)[None]).min(1)
        totals[world] = by_share.min(1) / error**2
    center = contrasts[:, :, 1].mean(1)
    resolution = Z_RESOLVE * error / math.sqrt(len(scans))
    best = {name: np.min([totals[w] for w in worlds if w in totals], axis=0) for name, worlds in CLASSES.items()}
    limit = adequacy_limit(len(scans))
    labels = []
    for i in range(len(noise)):
        if abs(center[i]) <= resolution:
            labels.append("offset_absent")
        elif center[i] < 0:
            labels.append("offset_reversed")
        else:
            labels.append(classify({name: float(v[i]) for name, v in best.items()}, limit))
    return labels


def label_counts(item: tuple[np.ndarray, np.ndarray]) -> dict[str, int]:
    """Count of each decision label over the simulated series of one truth: item is (noise, means)."""
    counts: dict[str, int] = {}
    for label in simulated_labels(*item):
        counts[label] = counts.get(label, 0) + 1
    return counts


def operating_characteristics(
    draws: int = OC_DRAWS, drift: bool = False, mix: float = 0.0, family: str | None = None
) -> dict[str, dict[str, float]]:
    """Share of each decision label per truth world, from `draws` simulated series of Gaussian contrasts at the design
    standard error, retention and readout, seeded from QRNG value OC_SEED_INDEX of OC_DRAW.

    `drift` sizes the mirror round of every truth to DRIFT_CONTRAST instead of DESIGN_CONTRAST, the change between
    the two base batches of the one-CZ series; `mix` is the truth's contraction share, and `family` replaces the
    contraction by a gate-noise family at its design strength. A truth that does not reach a round's center contrast
    on its branch reads UNREACHABLE; its draws still leave the generator."""
    rng = np.random.default_rng(int(read_record(OC_DRAW)["values"][OC_SEED_INDEX]))
    scans = [(k, r) for k, r in batch_order() if k != "bridge"]
    # Every truth's draws leave the one generator in TRUTHS order before the truths are mapped over the pool.
    items = []
    reached = []
    for _, world, branch, sign in TRUTHS:
        noise = rng.normal(size=(draws, len(scans), 3))
        try:
            rows = {
                contrast: predicted_contrasts(
                    world, truth_parameter(world, branch, contrast, mix, family, sign), mix, family
                )
                for contrast in ((DESIGN_CONTRAST, DRIFT_CONTRAST) if drift else (DESIGN_CONTRAST,))
            }
        except UnreachableTruth:
            reached.append(False)
            continue
        means = [
            [
                rows[DRIFT_CONTRAST if drift and replicate == 1 else DESIGN_CONTRAST][a]
                for a in scan_arms(kind, replicate)
            ]
            for kind, replicate in scans
        ]
        reached.append(True)
        items.append((noise, np.array(means)))
    counted = iter(ordered_map(label_counts, items, min_items=1))
    out: dict[str, dict[str, float]] = {}
    for (label, _, _, _), found in zip(TRUTHS, reached, strict=True):
        counts = next(counted) if found else {UNREACHABLE: draws}
        out[label] = {k: round(n / draws, 4) for k, n in sorted(counts.items())}
    return out


def predictions(operating: bool = True) -> dict[str, Any]:
    """The prediction record; `operating` adds the operating characteristics, OC_DRAWS simulated series per truth."""
    build_gate_tables(grid=False)
    table: dict[str, Any] = {"exact circuit": {"parameter": None, "contrast": predicted_contrasts(None, 0.0)}}
    for world in WORLDS:
        for value in sized(world):
            table[f"{world} at {value:+.4f}"] = {
                "parameter": round(value, 4),
                "contrast": predicted_contrasts(world, value),
            }
    record: dict[str, Any] = {
        "model": "raw selector contrast of every arm under each world sized to the center contrast "
        f"{DESIGN_CONTRAST} at retention {DESIGN_RETENTION} and the retained readout rates of the coin series",
        "predicted_contrast": table,
        "unmodeled": unmodeled(),
        "design": design(),
        "preregistered": preregistered(),
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in OUTCOMES.items()},
    }
    if operating:
        record["operating_characteristics"] = {
            "qrng_draw": OC_DRAW,
            "seed_index": OC_SEED_INDEX,
            "draws_per_world": OC_DRAWS,
            "stationary": operating_characteristics(),
            "stationary_data_only_contraction": operating_characteristics(mix=1.0),
            **{f"stationary_{kind}": operating_characteristics(family=kind) for kind in OC_FAMILIES},
            f"mirror_round_at_{DRIFT_CONTRAST}": operating_characteristics(drift=True),
        }
    return record


def write(directory: Path) -> None:
    for name, files in build().items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    (directory / TUNA_SERIES / "prediction.json").write_text(
        json.dumps(predictions(), indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path, operating: bool = True) -> None:
    """The case directories hold exactly the built files; CASE.md, the hand-written case, is the one extra file.

    `operating` False leaves the operating characteristics of prediction.json unreplayed and compares the rest."""
    built = build()
    prediction = directory / TUNA_SERIES / "prediction.json"
    if operating:
        built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(), indent=1, sort_keys=True) + "\n"
    else:
        stored = json.loads(prediction.read_text(encoding="utf-8"))
        fresh = predictions(operating=False)
        if stored.pop("operating_characteristics", None) is None or stored != fresh:
            keys = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
            raise ValueError(f"{prediction} differs from the prediction record under {keys}")
        built[TUNA_SERIES]["prediction.json"] = prediction.read_text(encoding="utf-8")
    for name, files in built.items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and not p.name.startswith(".") and p.name != "CASE.md"
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    if not (directory / TUNA_SERIES / "CASE.md").is_file():
        raise ValueError(f"{directory / TUNA_SERIES}/CASE.md is missing")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


# Analysis ---------------------------------------------------------------------------------------------------------


def series_of(run_dir: Path) -> str:
    """The series a run directory `<stamp>-<series>-batch-NN` belongs to."""
    stem = run_dir.name.rpartition("-batch-")[0]
    for name in (TUNA_SERIES, QX_SERIES):
        if stem.endswith(f"-{name}"):
            return name
    raise SystemExit(f"{run_dir.name} is not a run directory of {TUNA_SERIES} or {QX_SERIES}")


def circuit_statistics(listed: list[str], roles: dict[str, int]) -> dict[str, float]:
    """Raw selector contrast, its standard error and the visibility of one data circuit's shots."""
    return count_statistics(cc.coin_counts(listed, roles))


def count_statistics(counts: np.ndarray) -> dict[str, float]:
    """Raw selector contrast, its standard error, the visibility and the d2 split with its standard error of counts
    over the logical outcome index."""
    plus, minus = cc.piles(counts)
    value, error = pca.selector_stat(plus, minus)
    split, split_error = d2_split(np.asarray(counts))
    return {
        "contrast": float(value),
        "se": float(error),
        "visibility": float(visibility(np.asarray(counts))),
        "d2_split": float(split),
        "d2_split_se": float(split_error),
    }


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """Preregistered decision from shot lists keyed "batch/file"; `manifest` is any batch's cases.json."""
    roles = {k: int(v) for k, v in manifest["templates"]["b0"]["roles"].items()}
    register = [int(q) for q in manifest["register"]]
    guard = [int(q) for q in manifest["guard_qubits"]]
    plan = {row["batch"]: row for row in batch_rows(TUNA_SERIES)}
    names = sorted(plan)
    brackets = {b: cc.batch_assignment(shots, b, register) for b in names if plan[b]["kind"] == "readout"}
    if any(v is None for v in brackets.values()):
        raise ValueError("a readout batch lacks one of its two circuits")
    batches: list[dict[str, Any]] = []
    matrices: dict[str, np.ndarray] = {}
    bridge_differences: list[tuple[float, float]] = []
    rows: dict[str, Any] = {}
    for n, batch in enumerate(names):
        row = plan[batch]
        if row["kind"] == "readout":
            continue
        before, after = brackets[names[n - 1]], brackets[names[n + 1]]
        if before is None or after is None:
            raise ValueError(f"{batch} lacks a bracket")
        change = {
            str(q): {kind: abs(after[q][i] - before[q][i]) for i, kind in enumerate(("e01", "e10"))} for q in guard
        }
        admitted = all(v <= GUARD_LIMIT for rates in change.values() for v in rates.values())
        mean = {q: ((before[q][0] + after[q][0]) / 2, (before[q][1] + after[q][1]) / 2) for q in register}
        matrices[batch] = cc.readout_matrix(mean, roles)
        stats = [circuit_statistics(shots[f"{batch}/{c['file']}"], roles) for c in row["circuits"]]
        arms = [arm_of(c["file"]) for c in row["circuits"]]
        rows[batch] = {
            "kind": row["kind"],
            "replicate": row["replicate"],
            "arms": arms,
            "statistics": stats,
            "guard": {
                "change": change,
                "admitted": admitted,
                "before": {str(q): before[q] for q in register},
                "after": {str(q): after[q] for q in register},
            },
        }
        if row["kind"] == "bridge":
            rx = oc.pooled([(s["contrast"], s["se"]) for a, s in zip(arms, stats, strict=True) if a == CENTER])
            x90 = oc.pooled([(s["contrast"], s["se"]) for a, s in zip(arms, stats, strict=True) if a == RETAINED])
            rows[batch]["bridge_difference"] = [rx[0] - x90[0], math.hypot(rx[1], x90[1])]
            if admitted:
                bridge_differences.append((rx[0] - x90[0], math.hypot(rx[1], x90[1])))
            continue
        batches.append(
            {
                "name": batch,
                "kind": row["kind"],
                "arms": arms,
                "contrasts": [s["contrast"] for s in stats],
                "errors": [s["se"] for s in stats],
                "center_visibility": stats[arms.index(CENTER)]["visibility"],
                "admitted": admitted,
            }
        )
    bridges = sum(1 for row in plan.values() if row["kind"] == "bridge")
    bridge = bridge_differences if len(bridge_differences) == bridges else None
    decision = outcome(decide(batches, bridge, lambda b: matrices[b["name"]], transfer=True))
    drift = pcs.reference_drift(
        [(k.split("/")[0], k.split("/")[1], v) for k, v in shots.items() if k.split("/")[1] in pcs.READOUT_KIND],
        register,
    )
    order: dict[str, str] | None = None
    if executed is not None:
        order = {}
        for key in sorted(executed, key=lambda k: executed[k]):
            batch, fname = key.split("/")
            order[batch] = order.get(batch, "") + fname.removesuffix(".cq") + " "
    centers = [
        (s["d2_split"], s["d2_split_se"])
        for row in rows.values()
        if row["guard"]["admitted"]
        for arm, s in zip(row["arms"], row["statistics"], strict=True)
        if arm == CENTER
    ]
    return {
        "batch_rows": rows,
        "decision": decision,
        "center_d2_split": list(oc.pooled(centers)) if centers else None,
        "drift_covariate": {"references": drift},
        "executed_order": order,
    }


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series. A Tuna-17 series that holds fewer batches than the case reports its
    batch list only; a QX series reports the control verdict a Tuna-17 submission needs."""
    data = pca.read_series(run_dirs, case_root, series_of, "data", BATCH_FIELDS, pcs.load_run)
    shared, shots, executed = data["shared"], data["shots"], data["executed"]
    emulator = shared["backend_type_id"] == 1
    expected = sorted(r["batch"] for r in batch_rows(QX_SERIES if emulator else TUNA_SERIES))
    held = sorted({k.split("/")[0] for k in shots})
    head: dict[str, Any] = {
        "schema": ANALYSIS_SCHEMA,
        "claim_kind": pcs.CONTROL_KIND if emulator else "hardware acquisition",
        "backend": shared["backend"],
        "batch_cases_sha256": data["digests"],
    }
    if emulator:
        head["qx_control"] = pca.control_report(data["arms"], cc.coin_counts)
    if held != expected:
        return {**head, "complete": False, "batches": held}
    if emulator:
        return {**head, "complete": True}
    build_gate_tables()
    return {**head, "complete": True, **evaluate(shots, shared, executed)}


def sanity(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Bind each collected batch to the series case and report the readout drift between the brackets it is given.
    The readout admission of a data batch needs the bracket after it and is applied by analyze() on the series."""
    loaded = []
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        case_batch = None if case_root is None else case_root / series_of(run_dir) / cases["batch"]
        loaded.append(pcs.load_run(run_dir, case_batch))
    batches = [r["cases"]["batch"] for r in loaded]
    if len(set(batches)) != len(batches):
        raise SystemExit(f"a batch appears twice in {batches}")
    paired = [r for r in loaded if any(row["kind"] == "readout" for row in r["cases"]["circuits"])]
    return {"batches": batches, "drift": pcs.runs_drift(paired) if paired else None}


# Self-test --------------------------------------------------------------------------------------------------------


def cz_phase_contrasts(delta: float) -> dict[str, float]:
    """Raw selector contrast of every arm, at the design retention and readout, when every CZ applies the conditional
    phase pi + delta and every pulse is exact. The decision models no such world."""
    laws = np.stack([forward_laws(arm, None, np.array([0.0]), cz_phase=delta)[0] for arm in ARM_NAMES])
    laws = DESIGN_RETENTION * laws + (1 - DESIGN_RETENTION) / NOUT
    seen = selector_contrast(read(laws, design_matrix()))
    return {arm: round(float(v), 5) for arm, v in zip(ARM_NAMES, seen, strict=True)}


# Conditional-phase errors of the CZ gates whose noiseless decision the prediction record states.
CZ_PHASES = (-0.12, -0.08, 0.08, 0.12)


def unmodeled() -> dict[str, Any]:
    """Noiseless decision label of each mechanism outside the decision's worlds, with every batch admitted."""
    out: dict[str, Any] = {}
    for delta in CZ_PHASES:
        row = cz_phase_contrasts(delta)
        decision = decide(planted_batches(None, 0.0, row=row), None, None)
        out[f"cz conditional phase {delta:+.2f} rad"] = {
            "contrast": row,
            "label": decision["label"],
            "best_world": decision["numbers"].get("best_world"),
        }
    return out


def planted_batches(
    world: str | None,
    parameter: float,
    guard_fails: tuple[str, ...] = (),
    row: dict[str, float] | None = None,
    mix: float = 0.0,
) -> list[dict[str, Any]]:
    """Noiseless scan batches at the design retention and readout, for the calibration of decide(): the contrasts of
    a world at a parameter and contraction share, or the contrasts `row` gives per arm."""
    if row is None:
        row = predicted_contrasts(world, parameter, mix)
    batches = []
    for kind, replicate in batch_order():
        if kind == "bridge":
            continue
        arms = scan_arms(kind, replicate)
        batches.append(
            {
                "name": f"{kind}-{replicate}",
                "kind": kind,
                "arms": tuple(arms),
                "contrasts": [row[a] for a in arms],
                "errors": [1.0 / math.sqrt(SCAN_SHOTS)] * 3,
                "center_visibility": None,
                "admitted": kind not in guard_fails,
            }
        )
    return batches


def self_test() -> str:
    """The emitter and simulator against the retained record, then decide() on a planted world of each class."""
    build_gate_tables(grid=False)
    digest = replay_check()
    if digest != oc.COIN_PINS["b0.cq"]:
        raise AssertionError("the emitter's b0 does not carry the pinned digest")
    gap = float(np.abs(forward_law(RETAINED) - np.array(retained()["ideal"])).max())
    if gap > 1e-9:
        raise AssertionError(f"the simulator differs from the retained ideal law of b0 by {gap}")
    if float(np.abs(forward_law(CENTER) - forward_law(RETAINED)).max()) > 1e-12:
        raise AssertionError("Rx(pi/2) and X90 give different exact laws")
    expected = (
        ("pulse_x_before_all", 1, (), "pulse_x"),
        ("pulse_x_before_q8", 1, (), "pulse_x"),
        ("pulse_y_before_all", 1, (), "pulse_other"),
        ("selector_flip_q12_0", 0, (), "readout"),
        ("selector_dropout_coin_1", 0, (), "readout"),
        ("pulse_z_before_all", 0, (), "pulse_other"),
        (None, None, (), "offset_absent"),
        ("pulse_x_before_all", 1, ("q8-10",), "unresolved_guard"),
    )
    lines = [f"emitter reproduces the retained b0.cq ({digest[:12]}); simulator within {gap:.1e} of its ideal law"]
    for world, branch, fails, label in expected:
        value = truth_parameter(world, branch, DESIGN_CONTRAST)
        got = decide(planted_batches(world, value, fails), None, None)["label"]
        if got != label:
            raise AssertionError(f"planted {world} at {value:+.4f} reads {got}, not {label}")
        lines.append(f"planted {world} at {value:+.4f}: {got}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--operating-characteristics", action="store_true")
    mode.add_argument("--sanity", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.operating_characteristics:
        print(json.dumps(predictions()["operating_characteristics"], indent=1, sort_keys=True))
    elif args.sanity:
        print(json.dumps(sanity(args.sanity), indent=1, sort_keys=True))
    elif args.analyze:
        if args.out is None:
            parser.error("--analyze needs --out")
        report = analyze(args.analyze)
        args.out.write_text(json.dumps(report, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
        if "qx_control" in report and not (report["complete"] and report["qx_control"]["pass"]):
            print("the QX control is incomplete or missed its ideal: no Tuna-17 batch follows", file=sys.stderr)
            return 1
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    sys.exit(main())
