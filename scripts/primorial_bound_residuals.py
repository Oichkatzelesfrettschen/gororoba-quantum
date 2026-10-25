"""Coherent errors at their gate-error bounds, jointly and per coefficient, against the primorial null-subtracted fit.

scripts/primorial_null_residuals.py tests static ZZ and drive-axis tilt, one family at a time, against one
standard deviation of the worst-variance coefficient. This script extends that test on the same compiled gap88
phase-gradient and zero-angle null arms of the ibm_kingston snapshot:

1. **Simulator identity.** A numpy statevector of the three path qubits replays the timed compiled arms. It must
   reproduce every retained scenario of docs/evidence/primorial_cover/null_residuals.json and every coherent
   sensitivity of docs/evidence/primorial_cover/noise.json to 1e-9 before any new scenario is read.
2. **Per-coefficient criterion.** Each coefficient c_S of the null-subtracted fit has its own per-shot variance
   v_S in noise.json; at the retained budget N its standard deviation is sqrt(v_S / N). A scenario's
   ``max_z`` is max_S |bias_S| / sqrt(v_S / N), beside the worst-variance reading ``max_bias / sd`` of the
   earlier record.
3. **Joint gate-error bounds.** The average gate infidelity of a unitary U against its target V is
   (4 - |Tr(V^dagger U)|^2) / 6. Each path qubit's sx error r bounds a coherent sx and x error that is a
   drive-axis tilt beta (RY(-beta) R RY(beta)), a fractional amplitude error eta (RX(theta (1 + eta)) for a
   rotation by theta), or a mixture in eight directions (signs of tilt, amplitude, and both at equal weight); the
   direction is scaled until the sx infidelity equals r (``sx`` budget) or until the larger of the sx and x
   infidelities equals the snapshot's sx and x errors (``sx_and_x`` budget, the tighter). Each coupler's CZ
   error bounds a conditional phase phi, CPhase(phi) after the CZ, at acos(1 - 10 r / 3). Every combination of
   the 8^3 qubit directions and the 4 coupler signs is evaluated; a 5^5 grid over the tilt and CZ-phase
   magnitudes (-1, -1/2, 0, 1/2, 1 of each bound) tests interior points of the box.
   The same tilt and CZ-phase vertices are repeated with each CZ's conditional phase replaced by its Pauli
   twirl (``twirled_law``), the channel gate twirling turns a coherent CZ error into.
   Pairs with the unbounded families: static detuning on all three path qubits (DETUNING_KHZ, every sign) alone,
   with the atlas-fitted CZ phase, with the CZ-phase bound and with the sx-budget tilt bound; static ZZ in both
   frames (ZZ_KHZ) with the tilt bound and with the CZ-phase bound.
4. **Arm mismatch.** Null subtraction cancels a coherent error only when the signal and null arms see the same
   error. Each family applied to the signal arm alone (tilt and amplitude per qubit, CZ phase per coupler, static
   detuning per qubit, static ZZ per coupler) gives the mismatch at which max_z crosses 1 (``Mismatch``).
   A coherent-fraction scan scales the worst joint tilt and CZ-phase vertex by f and g in steps of 0.1.
5. **Path sweep.** Every three-qubit path of primorial_cover_noise.path_costs is compiled as the retained paths
   are; tilt and CZ phase at the path's bounds (``sx`` budget) give its worst joint residual over the 32 sign
   patterns, reported against the best path's per-coefficient standard deviations. A path's own budget scales
   them by (1/16 - b) / (1/16 - b_best) for its incoherent bias b, which this sweep does not simulate.

Falsifier: the gap88 cost leaves a device question when any bounded scenario of a retained path reaches
max_z >= 1. Order of analysis: an exploratory build-host run of the single-family and joint scenarios came first
and showed joint tilt and CZ phase above max_z = 1; the per-coefficient reading, the sx-and-x budget, the twirled
rows, the coherent-fraction scan, the refinement and the identification-shot endpoint were added after it, and
the retained Kaggle run followed. The detuning and ZZ pairs were added after a review of that retained run
asked which other pairs each cancelled to first order survive subtraction together. Each scenario also reports ``shots_identify_all``, the budget rule of
primorial_cover_noise.phase_fit (simultaneous z for seven coefficients, worst variance, margin 1/16 minus the
largest bias) with the scenario's bias in place of the incoherent one; None means the bias leaves no margin.

``--out FILE`` writes the record; ``--check FILE --run DIR`` requires FILE to be byte-identical to the collected
output of Kaggle run DIR, recomputes the record and requires every verdict to match and every bias to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import primorial_cover_noise as noise  # noqa: E402
import primorial_null_residuals as nr  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402

NULL_RECORD = ROOT / "docs/evidence/primorial_cover/null_residuals.json"
OUTPUT = "results/kaggle_out/primorial_bound_residuals.json"
KHZ = 1e3
TOLERANCE = 1e-9
# Sign-mirror scenarios give equal residuals up to rounding that differs between hosts; values within TIE of the
# maximum count as tied, and the first of them is the worst case.
TIE = 1e-9
DRIVEN = {"sx": math.pi / 2, "x": math.pi}
# Per-qubit coherent sx/x error directions (tilt sign, amplitude sign) before scaling to the gate-error budget.
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
GRID = (-1.0, -0.5, 0.0, 0.5, 1.0)
# Signal-arm-only families, each with the largest mismatch searched: tilt and CZ phase (rad), amplitude
# (fraction), detuning and ZZ (kHz). The caps sit above every gate-error bound and atlas-fitted rate of the
# Fez and Kingston fringes.
MISMATCH = (
    *(("tilt", (q,), 0.5) for q in range(3)),
    *(("amplitude", (q,), 0.2) for q in range(3)),
    *(("cz_phase", (c,), 0.5) for c in range(2)),
    *(("detuning", (q,), 300.0) for q in range(3)),
    *(("zz", (c,), 300.0) for c in range(2)),
)
# Fractions of the worst joint tilt and CZ-phase vertex; the coherent share of a gate's infidelity is the square.
FRACTIONS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
# Static detuning on every path qubit at the low and high ends of the Fez atlas lane fits
# (docs/evidence/atlas_detuning_map), static ZZ at the atlas self-test scale and ten times it (kHz), and the
# calibration-consistent CZ phase the atlas fits on Fez couplers (rad, coherent-error-families-report.md).
DETUNING_KHZ = (5.0, 30.0)
ZZ_KHZ = (2.0, 20.0)
MEASURED_CZ_PHASE = 0.04

Op = tuple[str, tuple[int, ...], float, float]


# ------------------------------------------------------------------ gates


def rx(theta: float) -> np.ndarray:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.asarray([[c, -1j * s], [-1j * s, c]])


def ry(theta: float) -> np.ndarray:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.asarray([[c, -s], [s, c]], dtype=complex)


def rz(theta: float) -> np.ndarray:
    return np.diag([np.exp(-0.5j * theta), np.exp(0.5j * theta)])


SX = 0.5 * np.asarray([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])
X = np.asarray([[0, 1], [1, 0]], dtype=complex)
TARGET = {"sx": SX, "x": X}


def driven(name: str, tilt: float, amplitude: float) -> np.ndarray:
    """The sx or x pulse under a drive-axis tilt and a fractional amplitude error, up to a global phase."""
    pulse = TARGET[name] if amplitude == 0.0 else rx(DRIVEN[name] * (1.0 + amplitude))
    return pulse if tilt == 0.0 else ry(-tilt) @ pulse @ ry(tilt)


def infidelity(u: np.ndarray, v: np.ndarray) -> float:
    """Average gate infidelity of a single-qubit unitary u against the target v."""
    return float((4.0 - abs(np.trace(v.conj().T @ u)) ** 2) / 6.0)


def scale_to_budget(direction: tuple[int, int], errors: dict[str, float]) -> tuple[float, float]:
    """(tilt, amplitude) along ``direction`` whose largest infidelity over ``errors``' gates equals its error."""

    def worst(s: float) -> float:
        tilt, amplitude = s * direction[0], s * direction[1]
        return max(infidelity(driven(name, tilt, amplitude), TARGET[name]) / r for name, r in errors.items())

    low, high = 0.0, 0.5
    if worst(high) < 1.0:
        raise SystemExit(f"direction {direction} never reaches the budget {errors}")
    for _ in range(80):
        mid = 0.5 * (low + high)
        low, high = (mid, high) if worst(mid) < 1.0 else (low, mid)
    return low * direction[0], low * direction[1]


# -------------------------------------------------------------- simulator


def compact(
    arm: nr.Timed, layout: list[int], durations: dict[tuple[str, tuple[int, ...]], float], dt: float
) -> list[Op]:
    """(name, wires, rz angle, duration in s) for every timed instruction, in schedule order."""
    out: list[Op] = []
    for operation, local, _start in arm:
        if operation.name == "delay":
            seconds = float(operation.duration) * (dt if operation.unit == "dt" else 1.0)
        else:
            seconds = durations.get((operation.name, tuple(layout[k] for k in local)), 0.0)
        angle = float(operation.params[0]) if operation.name == "rz" else 0.0
        if operation.name not in ("rz", "sx", "x", "cz", "delay"):
            raise SystemExit(f"unexpected compiled instruction {operation.name}")
        out.append((operation.name, tuple(local), angle, seconds))
    return out


def starts(ops: list[Op]) -> list[float]:
    """Start of every op from per-wire cursors; ops arrive in schedule order."""
    cursor = [0.0, 0.0, 0.0]
    out = []
    for _name, wires, _angle, seconds in ops:
        start = max(cursor[k] for k in wires)
        for k in wires:
            cursor[k] = start + seconds
        out.append(start)
    return out


def apply1(state: np.ndarray, gate: np.ndarray, wire: int) -> np.ndarray:
    """Apply a single-qubit gate; axis 2 - wire of the (2, 2, 2) tensor is qubit ``wire`` (little-endian)."""
    return np.moveaxis(np.tensordot(gate, state, axes=([1], [2 - wire])), 0, 2 - wire)


def diagonal2(
    state: np.ndarray, pair: tuple[int, int], phases: tuple[complex, complex, complex, complex]
) -> np.ndarray:
    """Multiply each |b_hi b_lo> component of ``pair`` = (lo, hi) by phases[2 b_hi + b_lo]."""
    out = state.copy()
    for k, phase in enumerate(phases):
        if phase == 1.0:
            continue
        index: list[Any] = [slice(None)] * 3
        index[2 - pair[0]] = k & 1
        index[2 - pair[1]] = k >> 1
        out[tuple(index)] *= phase
    return out


def law(ops: list[Op], spec: dict[str, Any]) -> list[float]:
    """Noise-free outcome law of the timed arm under ``spec``.

    spec keys, each optional: ``tilt`` and ``amplitude`` (per wire, on the gates named by ``amplitude_gates``,
    default sx and x), ``cz_phase`` (per coupler of primorial_null_residuals.COUPLERS), ``detuning`` (kHz per
    wire, RZ(2 pi delta t) after every instruction of duration t on the wire, as in
    primorial_cover_noise.CoherentLaw), ``zz`` and ``zz_symmetric`` (kHz per coupler, CPhase(-2 pi zeta t) and
    RZZ(pi zeta t) before every non-rz instruction on either qubit over the interval since the previous one, as
    in primorial_null_residuals.ScenarioLaw). ``cz_twirl`` true replaces the coherent CZ phase by its Pauli twirl
    (``twirled_law``).
    """
    if spec.get("cz_twirl"):
        return twirled_law(ops, spec)
    tilt, amplitude = spec.get("tilt", (0.0,) * 3), spec.get("amplitude", (0.0,) * 3)
    amplitude_gates = spec.get("amplitude_gates", ("sx", "x"))
    cz_phase, detuning = spec.get("cz_phase", (0.0, 0.0)), spec.get("detuning", (0.0,) * 3)
    zz, zz_sym = spec.get("zz", (0.0, 0.0)), spec.get("zz_symmetric", (0.0, 0.0))
    coupled = any(zz) or any(zz_sym)
    state = np.zeros((2, 2, 2), dtype=complex)
    state[0, 0, 0] = 1.0
    last: dict[int, float] = {}
    for (name, wires, angle, seconds), start in zip(ops, starts(ops), strict=True):
        if name != "delay":
            if coupled and name != "rz":
                for c, pair in enumerate(nr.COUPLERS):
                    if pair[0] in wires or pair[1] in wires:
                        if c in last:
                            interval = start - last[c]
                            if zz[c]:
                                phase = np.exp(-2j * math.pi * zz[c] * KHZ * interval)
                                state = diagonal2(state, pair, (1.0, 1.0, 1.0, phase))
                            if zz_sym[c]:
                                half = 0.5 * math.pi * zz_sym[c] * KHZ * interval
                                even, odd = np.exp(-1j * half), np.exp(1j * half)
                                state = diagonal2(state, pair, (even, odd, odd, even))
                        last[c] = start
            if name == "rz":
                state = apply1(state, rz(angle), wires[0])
            elif name in DRIVEN:
                eta = amplitude[wires[0]] if name in amplitude_gates else 0.0
                state = apply1(state, driven(name, tilt[wires[0]], eta), wires[0])
            else:
                pair = (min(wires), max(wires))
                phi = cz_phase[nr.COUPLERS.index(pair)]
                state = diagonal2(state, pair, (1.0, 1.0, 1.0, -np.exp(1j * phi)))
        if seconds:
            for wire in wires:
                if detuning[wire]:
                    state = apply1(state, rz(2.0 * math.pi * detuning[wire] * KHZ * seconds), wire)
    return [float(v) for v in np.abs(state.reshape(8)) ** 2]


def lift1(gate: np.ndarray, wire: int) -> np.ndarray:
    """8 x 8 operator of a single-qubit gate on ``wire``; the basis index is 4 q2 + 2 q1 + q0."""
    factors = [np.eye(2, dtype=complex)] * 3
    factors[2 - wire] = gate
    out: np.ndarray = np.kron(np.kron(factors[0], factors[1]), factors[2])
    return out


def pair_diagonal(pair: tuple[int, int], phases: tuple[complex, ...]) -> np.ndarray:
    """Diagonal of the 8 x 8 operator multiplying |b_hi b_lo> of ``pair`` = (lo, hi) by phases[2 b_hi + b_lo]."""
    return np.asarray([phases[2 * (k >> pair[1] & 1) + (k >> pair[0] & 1)] for k in range(8)])


def twirled_law(ops: list[Op], spec: dict[str, Any]) -> list[float]:
    """Outcome law with coherent sx and x errors and the Pauli twirl of each CZ's conditional phase.

    Pauli twirling the CZ maps its error D = CPhase(phi) to the channel rho -> sum_P |c_P|^2 P rho P over
    P in {II, Z_lo, Z_hi, Z_lo Z_hi}, with c_P = Tr(P D) / 4: the diagonal of the error's chi matrix. The
    twirl Paulis are taken as ideal and the sx and x errors stay coherent, so the model isolates what the
    twirl removes from the CZ error alone.
    """
    if any(spec.get(k) for k in ("detuning", "zz", "zz_symmetric")):
        raise SystemExit("twirled_law models tilt, amplitude and CZ phase only")
    tilt, amplitude = spec.get("tilt", (0.0,) * 3), spec.get("amplitude", (0.0,) * 3)
    amplitude_gates = spec.get("amplitude_gates", ("sx", "x"))
    cz_phase = spec.get("cz_phase", (0.0, 0.0))
    rho = np.zeros((8, 8), dtype=complex)
    rho[0, 0] = 1.0
    for name, wires, angle, _seconds in ops:
        if name == "delay":
            continue
        if name == "rz":
            u = lift1(rz(angle), wires[0])
            rho = u @ rho @ u.conj().T
        elif name in DRIVEN:
            eta = amplitude[wires[0]] if name in amplitude_gates else 0.0
            u = lift1(driven(name, tilt[wires[0]], eta), wires[0])
            rho = u @ rho @ u.conj().T
        else:
            pair = (min(wires), max(wires))
            cz = pair_diagonal(pair, (1.0, 1.0, 1.0, -1.0))
            rho = rho * np.outer(cz, cz.conj())
            d = (1.0, 1.0, 1.0, np.exp(1j * cz_phase[nr.COUPLERS.index(pair)]))
            mixed = np.zeros_like(rho)
            for z_lo, z_hi in ((0, 0), (1, 0), (0, 1), (1, 1)):
                signs = [(-1) ** (z_lo * (b & 1) + z_hi * (b >> 1)) for b in range(4)]
                weight = abs(sum(s * v for s, v in zip(signs, d, strict=True)) / 4.0) ** 2
                pauli = pair_diagonal(pair, tuple(complex(s) for s in signs))
                mixed += weight * rho * np.outer(pauli, pauli)
            rho = mixed
    return [float(v) for v in np.real(np.diag(rho))]


# --------------------------------------------------------------- analysis


def first_max(values: list[float]) -> int:
    """Index of the first value within TIE of the maximum."""
    top = max(values)
    return next(k for k, v in enumerate(values) if v >= top - TIE)


Arm = tuple[dict[str, Any], list[Op]]


class Fit:
    """Picklable worker: (signal spec, null spec) -> raw and null-subtracted gap88 fits on one path.

    The signal spec acts on the gap88 arms and the null spec on the zero-angle arms; equal specs model an error
    both arms share, a null spec of {} an error the signal arm alone sees.
    """

    def __init__(self, arms: list[Arm], variance: dict[str, float], shots: int) -> None:
        self.arms = arms
        self.variance = variance
        self.sd = {k: math.sqrt(v / shots) for k, v in variance.items()}
        self.table = noise.cost_table("gap88")
        self.exact = noise.coefficients(self.table)

    def __call__(self, item: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
        signal, null_spec = item
        rows = [{**meta, "law": law(ops, signal if meta["cost"] == "gap88" else null_spec)} for meta, ops in self.arms]
        readings = noise.gradient_readings(rows, "gap88")
        null = noise.gradient_readings(rows, "null")
        raw = noise.phase_fit(self.table, *readings, noise.raw_phase_variance(*readings))
        sub = noise.null_subtracted(
            self.table, *readings, null, noise.raw_phase_variance(*readings), noise.raw_phase_variance(*null)
        )
        shift = {k: v - self.exact[k] for k, v in sub["recovered_coefficients"].items()}
        z = {k: abs(v) / self.sd[k] for k, v in shift.items()}
        keys = sorted(z)
        worst = keys[first_max([z[k] for k in keys])]
        # primorial_cover_noise.phase_fit's budget rule with this bias in place of the incoherent one.
        margin = noise.IDENTIFY_RADIUS - max(abs(v) for v in shift.values())
        identify = math.ceil(noise.SIMULTANEOUS_Z**2 * max(self.variance.values()) / margin**2) if margin > 0 else None
        return {
            "max_coefficient_bias": raw["max_coefficient_bias"],
            "null_subtracted_max_bias": sub["max_coefficient_bias"],
            "null_subtracted_shift": shift,
            "max_z": z[worst],
            "max_z_coefficient": worst,
            "shots_identify_all": identify,
        }


def path_arms(
    snapshot: dict[str, Any], view: Any, layout: list[int], logical: list[tuple[dict[str, Any], Any]]
) -> list[Arm]:
    durations = {
        (name, tuple(qargs)): float(props.duration)
        for name in view.target.operation_names
        for qargs, props in view.target[name].items()
        if qargs is not None and props is not None and props.duration and set(qargs) <= set(layout)
    }
    dt = float(view.target.dt)
    compiled = parallel.ordered_map(noise.ArmCompile(snapshot), [(c, layout) for _, c in logical], min_items=1)
    return [
        (meta, compact(nr.timed(circuit, layout, durations, dt), layout, durations, dt))
        for (meta, _), circuit in zip(logical, compiled, strict=True)
    ]


def gate_errors(snapshot: dict[str, Any], layout: list[int]) -> tuple[list[dict[str, float]], list[float]]:
    """Per path qubit {sx, x} errors and per coupler CZ errors."""
    table = {op: {tuple(r["qargs"]): r["error"] for r in snapshot["instructions"][op]} for op in ("sx", "x", "cz")}
    gates = [{"sx": table["sx"][(q,)], "x": table["x"][(q,)]} for q in layout]
    cz = []
    for a, b in nr.COUPLERS:
        pair = (layout[a], layout[b])
        cz.append(table["cz"][pair] if pair in table["cz"] else table["cz"][pair[::-1]])
    return gates, cz


def cz_bound(r: float) -> float:
    return math.acos(1.0 - 10.0 * r / 3.0)


def budget(record: dict[str, Any], patch: str) -> tuple[int, dict[str, float]]:
    """noise.json's null-subtracted gap88 shots per setting and per-shot variance of every coefficient."""
    fit = record["patches"][patch]["summary"]["gradient"]["gap88"]["null_subtracted"]
    return int(fit["shots_identify_all"]), {k: float(v) for k, v in fit["per_shot_coefficient_variance"].items()}


def validate(patch: str, fit: Fit, null_record: dict[str, Any], noise_record: dict[str, Any]) -> dict[str, Any]:
    """Replay the retained scenarios through the numpy simulator; a departure above TOLERANCE stops the run."""
    items: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in null_record["patches"][patch]["scenarios"]:
        family, qubits, value = row["family"], row["qubits"], row["value"]
        if family.startswith("axis_tilt"):
            per = value if isinstance(value, list) else [value if q in qubits else 0.0 for q in range(3)]
            items.append((row, {"tilt": tuple(per)}))
        else:
            items.append((row, {family: (value, value)}))
    if patch == "best":
        for row in noise_record["coherent_sensitivity"]:
            family, value = row["family"], row["value"]
            if family == "cz_phase":
                spec: dict[str, Any] = {"cz_phase": (value, value)}
            elif family == "sx_amplitude":
                spec = {"amplitude": (value,) * 3, "amplitude_gates": ("sx",)}
            else:
                q = int(family.removeprefix("detuning_q"))
                spec = {"detuning": tuple(value if k == q else 0.0 for k in range(3))}
            items.append((row, spec))
    got = parallel.ordered_map(fit, [(spec, spec) for _, spec in items], min_items=1)
    worst = max(
        abs(g[key] - row[key])
        for (row, _), g in zip(items, got, strict=True)
        for key in ("max_coefficient_bias", "null_subtracted_max_bias")
    )
    if worst > TOLERANCE:
        raise SystemExit(f"{patch}: numpy simulator departs from the retained records by {worst}")
    return {"scenarios_replayed": len(items), "max_departure": worst}


def summary(rows: list[dict[str, Any]], specs: list[dict[str, Any]]) -> dict[str, Any]:
    """Worst scenario by max_z and by the worst-variance reading, with the count reaching max_z >= 1."""
    by_z = first_max([r["max_z"] for r in rows])
    by_bias = first_max([r["null_subtracted_max_bias"] for r in rows])
    return {
        "scenarios": len(rows),
        "reaching_max_z_1": sum(1 for r in rows if r["max_z"] >= 1.0),
        "worst_max_z": {**rows[by_z], "spec": specs[by_z]},
        "worst_null_subtracted_bias": {**rows[by_bias], "spec": specs[by_bias]},
    }


def bounded(gates: list[dict[str, float]], cz: list[float]) -> dict[str, Any]:
    """Per-qubit (tilt, amplitude) of every direction under both budgets, and the CZ-phase bounds."""
    out: dict[str, Any] = {"cz_phase": [cz_bound(r) for r in cz]}
    for budget in ("sx", "sx_and_x"):
        out[budget] = [
            [
                scale_to_budget(d, {"sx": g["sx"]} if budget == "sx" else {"sx": g["sx"], "x": g["x"]})
                for d in DIRECTIONS
            ]
            for g in gates
        ]
    pure = [math.acos(2.0 * math.sqrt(1.0 - 1.5 * g["sx"]) - 1.0) for g in gates]
    departure = max(abs(a - b[0][0]) for a, b in zip(pure, out["sx"], strict=True))
    if departure > 1e-12:
        raise SystemExit(f"pure-tilt budget departs from atlas_coherent_families.gate_bounds by {departure}")
    return out


def round_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        k: [round(float(x), 12) for x in v] if isinstance(v, tuple) and k != "amplitude_gates" else v
        for k, v in spec.items()
    }


def patch_record(fit: Fit, gates: list[dict[str, float]], cz: list[float]) -> dict[str, Any]:
    bounds = bounded(gates, cz)
    phi = bounds["cz_phase"]
    signs2 = list(itertools.product((1.0, -1.0), repeat=2))
    signs3 = list(itertools.product((1.0, -1.0), repeat=3))
    families: dict[str, list[dict[str, Any]]] = {}
    for budget in ("sx", "sx_and_x"):
        tilt = [b[0][0] for b in bounds[budget]]
        amp = [b[2][1] for b in bounds[budget]]
        families[f"tilt_{budget}"] = [{"tilt": tuple(s * t for s, t in zip(p, tilt, strict=True))} for p in signs3]
        families[f"amplitude_{budget}"] = [
            {"amplitude": tuple(s * a for s, a in zip(p, amp, strict=True))} for p in signs3
        ]
    families["cz_phase"] = [{"cz_phase": tuple(s * f for s, f in zip(p, phi, strict=True))} for p in signs2]
    for budget in ("sx", "sx_and_x"):
        joint = []
        for choice in itertools.product(range(len(DIRECTIONS)), repeat=3):
            per = [bounds[budget][q][d] for q, d in enumerate(choice)]
            for p in signs2:
                joint.append(
                    {
                        "tilt": tuple(t for t, _ in per),
                        "amplitude": tuple(a for _, a in per),
                        "cz_phase": tuple(s * f for s, f in zip(p, phi, strict=True)),
                    }
                )
        families[f"joint_{budget}"] = joint
    tilt = [b[0][0] for b in bounds["sx"]]
    families["cz_phase_twirled"] = [{**spec, "cz_twirl": True} for spec in families["cz_phase"]]
    families["joint_tilt_sx_cz_twirled"] = [
        {
            "tilt": tuple(s * t for s, t in zip(p[:3], tilt, strict=True)),
            "cz_phase": tuple(s * f for s, f in zip(p[3:], phi, strict=True)),
            "cz_twirl": True,
        }
        for p in itertools.product((1.0, -1.0), repeat=5)
    ]
    s2 = signs2
    for det in DETUNING_KHZ:
        detuned = [tuple(det * a for a in p) for p in signs3]
        families[f"detuning_{det:g}"] = [{"detuning": d} for d in detuned]
        families[f"detuning_{det:g}_cz_measured"] = [
            {"detuning": d, "cz_phase": tuple(MEASURED_CZ_PHASE * a for a in p)} for d in detuned for p in s2
        ]
        families[f"detuning_{det:g}_cz_bound"] = [
            {"detuning": d, "cz_phase": tuple(a * f for a, f in zip(p, phi, strict=True))} for d in detuned for p in s2
        ]
        families[f"detuning_{det:g}_tilt_sx"] = [
            {"detuning": d, "tilt": tuple(a * t for a, t in zip(p, tilt, strict=True))} for d in detuned for p in signs3
        ]
    for rate in ZZ_KHZ:
        for frame in ("zz", "zz_symmetric"):
            coupled = [tuple(rate * a for a in p) for p in s2]
            families[f"{frame}_{rate:g}_tilt_sx"] = [
                {frame: c, "tilt": tuple(a * t for a, t in zip(p, tilt, strict=True))} for c in coupled for p in signs3
            ]
            families[f"{frame}_{rate:g}_cz_bound"] = [
                {frame: c, "cz_phase": tuple(a * f for a, f in zip(p, phi, strict=True))} for c in coupled for p in s2
            ]
    families["grid_tilt_cz_sx"] = [
        {"tilt": tuple(g * t for g, t in zip(v[:3], tilt, strict=True)), "cz_phase": (v[3] * phi[0], v[4] * phi[1])}
        for v in itertools.product(GRID, repeat=5)
    ]
    order = list(families)
    flat = [spec for name in order for spec in families[name]]
    rows = parallel.ordered_map(fit, [(spec, spec) for spec in flat], min_items=1)
    out: dict[str, Any] = {
        "gate_errors": {"sx_x": gates, "cz": cz},
        "bounds": {
            "cz_phase": phi,
            **{
                budget: [{"tilt": bounds[budget][q][0][0], "amplitude": bounds[budget][q][2][1]} for q in range(3)]
                for budget in ("sx", "sx_and_x")
            },
        },
        "families": {},
    }
    start = 0
    for name in order:
        count = len(families[name])
        chunk = [{k: v for k, v in r.items() if k != "null_subtracted_shift"} for r in rows[start : start + count]]
        out["families"][name] = summary(chunk, [round_spec(s) for s in families[name]])
        start += count
    out["arm_mismatch"] = parallel.ordered_map(Mismatch(fit), list(MISMATCH), min_items=1)
    signs5 = list(itertools.product((1.0, -1.0), repeat=5))
    fractions = [
        tilt_cz(tilt, phi, tuple(f * x for x in p[:3]) + tuple(g * x for x in p[3:]))
        for f in FRACTIONS
        for g in FRACTIONS
        for p in signs5
    ]
    scan = parallel.ordered_map(fit, [(spec, spec) for spec in fractions], min_items=1)
    cells = [scan[k : k + len(signs5)] for k in range(0, len(scan), len(signs5))]
    out["coherent_fraction_scan"] = {
        "rows": "tilt fraction f of each qubit's sx-budget tilt bound",
        "columns": "CZ-phase fraction g of each coupler's bound",
        "fractions": list(FRACTIONS),
        "max_z": [
            [max(r["max_z"] for r in cells[a * len(FRACTIONS) + b]) for b in range(len(FRACTIONS))]
            for a in range(len(FRACTIONS))
        ],
        "shots_identify_all": [
            [worst_shots(cells[a * len(FRACTIONS) + b]) for b in range(len(FRACTIONS))] for a in range(len(FRACTIONS))
        ],
    }
    out["refined_tilt_cz_sx"] = refine(fit, tilt, phi, out["families"]["grid_tilt_cz_sx"]["worst_max_z"]["spec"])
    return out


def tilt_cz(tilt: list[float], phi: list[float], scale: tuple[float, ...]) -> dict[str, Any]:
    """Tilt and CZ phase at ``scale`` (five signed fractions) of the path's sx-budget tilt and CZ-phase bounds."""
    return {
        "tilt": tuple(x * t for x, t in zip(scale[:3], tilt, strict=True)),
        "cz_phase": tuple(x * f for x, f in zip(scale[3:], phi, strict=True)),
    }


def worst_shots(rows: list[dict[str, Any]]) -> int | None:
    """The largest shots_identify_all over rows; None when any bias leaves no identification margin."""
    values = [r["shots_identify_all"] for r in rows]
    return None if any(v is None for v in values) else max(values)


def refine(fit: Fit, tilt: list[float], phi: list[float], start: dict[str, Any]) -> dict[str, Any]:
    """Coordinate ascent of max_z inside the tilt and CZ-phase box from the best grid point.

    Each round evaluates every single-coordinate move of the current step, clipped to [-1, 1], and takes the best
    improvement; the step halves from 1/4 to 1/32 when no move improves. The result is a local maximum, a lower
    bound on the box's worst case.
    """
    point = [a / t for a, t in zip(start["tilt"], tilt, strict=True)] + [
        a / f for a, f in zip(start["cz_phase"], phi, strict=True)
    ]
    best = fit((tilt_cz(tilt, phi, tuple(point)), tilt_cz(tilt, phi, tuple(point))))
    step = 0.25
    evaluations = 1
    while step >= 1 / 32:
        moves = []
        for k in range(5):
            for sign in (1.0, -1.0):
                moved = list(point)
                moved[k] = min(1.0, max(-1.0, moved[k] + sign * step))
                if moved != point:
                    moves.append(moved)
        specs = [tilt_cz(tilt, phi, tuple(m)) for m in moves]
        rows = parallel.ordered_map(fit, [(spec, spec) for spec in specs], min_items=1)
        evaluations += len(rows)
        k = first_max([r["max_z"] for r in rows])
        if rows[k]["max_z"] > best["max_z"] + TIE:
            point, best = moves[k], rows[k]
        else:
            step /= 2
    return {
        "fractions": [round(x, 12) for x in point],
        "spec": round_spec(tilt_cz(tilt, phi, tuple(point))),
        "evaluations": evaluations,
        **{k: v for k, v in best.items() if k != "null_subtracted_shift"},
    }


class Mismatch:
    """Picklable worker: a signal-arm-only error of one family and target at which max_z crosses 1.

    The search doubles from cap / 2^20 to the first value reaching max_z = 1 and bisects that octave 40 times,
    so it returns the first crossing on the doubling grid; a family below max_z = 1 up to its cap reports None.
    """

    def __init__(self, fit: Fit) -> None:
        self.fit = fit

    def z(self, family: str, where: tuple[int, ...], value: float) -> dict[str, Any]:
        size = 2 if family in ("cz_phase", "zz") else 3
        spec = {family: tuple(value if k in where else 0.0 for k in range(size))}
        return self.fit((spec, {}))

    def __call__(self, item: tuple[str, tuple[int, ...], float]) -> dict[str, Any]:
        family, where, cap = item
        high = cap / 2**20
        while self.z(family, where, high)["max_z"] < 1.0:
            if high >= cap:
                return {"family": family, "target": list(where), "cap": cap, "mismatch_for_max_z_1": None}
            high = min(cap, 2.0 * high)
        low = high / 2.0 if high > cap / 2**20 else 0.0
        for _ in range(40):
            mid = 0.5 * (low + high)
            low, high = (mid, high) if self.z(family, where, mid)["max_z"] < 1.0 else (low, mid)
        at = self.z(family, where, high)
        return {
            "family": family,
            "target": list(where),
            "cap": cap,
            "mismatch_for_max_z_1": high,
            "max_z_coefficient": at["max_z_coefficient"],
        }


def sweep(
    snapshot: dict[str, Any], view: Any, logical: list[Any], variance: dict[str, float], shots: int
) -> dict[str, Any]:
    """Worst joint tilt and CZ-phase residual over the 32 sign patterns on every three-qubit path.

    A gate error of 1.0 marks a non-working gate in the snapshot; primorial_cover_noise.path_costs drops such CZ
    edges, and the sweep also drops every path holding a qubit whose sx or x error is 1.0.
    """
    broken = {row["qargs"][0] for op in ("sx", "x") for row in snapshot["instructions"][op] if row["error"] >= 1.0}
    every = noise.path_costs(snapshot, 3)
    ranked = [(rank, cost, layout) for rank, (cost, layout) in enumerate(every) if not broken & set(layout)]
    signs = list(itertools.product((1.0, -1.0), repeat=5))
    paths = []
    streams: set[str] = set()
    for rank, cost, layout in ranked:
        arms = path_arms(snapshot, view, layout, logical)
        stream = json.dumps(
            [
                [meta["cost"], meta["j"], meta["x"], meta["basis"], [(n, w, a) for n, w, a, _ in ops]]
                for meta, ops in arms
            ]
        )
        streams.add(hashlib.sha256(stream.encode()).hexdigest())
        gates, cz = gate_errors(snapshot, layout)
        tilt = [math.acos(2.0 * math.sqrt(1.0 - 1.5 * g["sx"]) - 1.0) for g in gates]
        phi = [cz_bound(r) for r in cz]
        specs = [
            {
                "tilt": tuple(s * t for s, t in zip(p[:3], tilt, strict=True)),
                "cz_phase": tuple(s * f for s, f in zip(p[3:], phi, strict=True)),
            }
            for p in signs
        ]
        rows = parallel.ordered_map(Fit(arms, variance, shots), [(s, s) for s in specs], min_items=1)
        worst = first_max([r["max_z"] for r in rows])
        paths.append(
            {
                "rank": rank,
                "layout": layout,
                "cost": cost,
                "sx_error": [g["sx"] for g in gates],
                "cz_error": cz,
                "worst_max_z": rows[worst]["max_z"],
                "worst_max_z_coefficient": rows[worst]["max_z_coefficient"],
                "worst_null_subtracted_bias": max(r["null_subtracted_max_bias"] for r in rows),
                "worst_shots_identify_all": worst_shots(rows),
            }
        )
    values = sorted(p["worst_max_z"] for p in paths)
    return {
        "paths": len(paths),
        "rank": "position in primorial_cover_noise.path_costs, whose index 0 is the best path",
        "paths_dropped_for_non_working_qubits": len(every) - len(ranked),
        "non_working_qubits": sorted(broken),
        "distinct_gate_streams": len(streams),
        "reaching_max_z_1": sum(1 for v in values if v >= 1.0),
        "unidentifiable": sum(1 for p in paths if p["worst_shots_identify_all"] is None),
        "max_z_quantiles": {q: values[min(len(values) - 1, int(q * len(values)))] for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
        "max_z_max": values[-1],
        "rows": paths,
    }


def evaluate(
    snapshot: dict[str, Any], noise_record: dict[str, Any], null_record: dict[str, Any], with_sweep: bool
) -> dict[str, Any]:
    view = calibration_snapshot.snapshot_backend(snapshot)
    logical = [(m, c) for m, c in noise.arms() if m["family"] == "gradient" and m["cost"] in ("gap88", "null")]
    out: dict[str, Any] = {"patches": {}}
    for patch in nr.PATCHES:
        layout = noise_record["layouts"]["3"][patch]
        if null_record["layouts"][patch] != layout:
            raise SystemExit(f"{patch}: null_residuals layout {null_record['layouts'][patch]} against {layout}")
        shots, variance = budget(noise_record, patch)
        fit = Fit(path_arms(snapshot, view, layout, logical), variance, shots)
        if abs(max(fit.sd.values()) - null_record["patches"][patch]["budget_coefficient_sd"]) > 1e-15:
            raise SystemExit(f"{patch}: worst-variance SD differs from null_residuals.json")
        gates, cz = gate_errors(snapshot, layout)
        record = {
            "layout": layout,
            "budget_shots_per_setting": shots,
            "coefficient_sd": fit.sd,
            "simulator_replay": validate(patch, fit, null_record, noise_record),
            **patch_record(fit, gates, cz),
        }
        record["device_question"] = any(f["reaching_max_z_1"] > 0 for name, f in record["families"].items())
        out["patches"][patch] = record
    if with_sweep:
        shots, variance = budget(noise_record, "best")
        out["path_sweep"] = sweep(snapshot, view, logical, variance, shots)
    return out


def run(with_sweep: bool = True) -> dict[str, Any]:
    snapshot = json.loads(noise.SNAPSHOT.read_text(encoding="utf-8"))
    noise_record = json.loads(nr.NOISE_RECORD.read_text(encoding="utf-8"))
    null_record = json.loads(NULL_RECORD.read_text(encoding="utf-8"))
    started = time.time()
    result = evaluate(snapshot, noise_record, null_record, with_sweep)
    return {
        "schema": "gororoba-primorial-bound-residuals-v1",
        "snapshot": str(noise.SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(noise.SNAPSHOT.read_bytes()).hexdigest(),
        "noise_record_sha256": hashlib.sha256(nr.NOISE_RECORD.read_bytes()).hexdigest(),
        "null_record_sha256": hashlib.sha256(NULL_RECORD.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "environment": {k: v for k, v in noise.environment("CPU").items() if k != "device"},
        "seconds": round(time.time() - started, 1),
        **result,
    }


def compare(fresh: Any, kept: Any, path: str, failures: list[str]) -> None:
    """Every bool, int and string equal; every float to 1e-8 relative; the run's seconds and environment skipped."""
    if isinstance(fresh, dict) and isinstance(kept, dict):
        if set(fresh) != set(kept):
            failures.append(f"{path}: keys {sorted(set(fresh) ^ set(kept))}")
            return
        for key in fresh:
            if path == "" and key in ("seconds", "environment"):
                continue
            compare(fresh[key], kept[key], f"{path}/{key}", failures)
    elif isinstance(fresh, list) and isinstance(kept, list):
        if len(fresh) != len(kept):
            failures.append(f"{path}: length {len(fresh)} against {len(kept)}")
            return
        for k, (a, b) in enumerate(zip(fresh, kept, strict=True)):
            compare(a, b, f"{path}/{k}", failures)
    elif isinstance(fresh, float) and isinstance(kept, (int, float)) and not isinstance(kept, bool):
        if not math.isclose(fresh, kept, rel_tol=1e-8, abs_tol=1e-10):
            failures.append(f"{path}: {fresh} against {kept}")
    elif fresh != kept:
        failures.append(f"{path}: {fresh} against {kept}")


def check(path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    recorded = ledger["files"].get(f"output/repo/{OUTPUT}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    failures = [] if digest == recorded else [f"{path} sha256 {digest} against the collected {recorded}"]
    compare(json.loads(json.dumps(run(with_sweep="path_sweep" in retained))), retained, "", failures)
    for failure in failures[:50]:
        print(failure)
    print(f"primorial bound residual replay: {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    parser.add_argument("--no-sweep", action="store_true", help="skip the every-path sweep")
    args = parser.parse_args()
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    result = run(with_sweep=not args.no_sweep)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
