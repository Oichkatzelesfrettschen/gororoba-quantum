"""Coherent-error probes on a three-qubit path: drive-axis tilt, CZ conditional phase, detuning and static ZZ.

The path is wired 0-1-2 with couplers (0, 1) and (1, 2), and every circuit measures wire k into clbit k
(little-endian outcome index). The probes estimate the parameters of the coherent families of
scripts/primorial_bound_residuals.py in that script's conventions:

- **x tilt.** The cell x, rz(pi), x, rz(pi) is the identity. A drive-axis tilt beta of the x pulse,
  RY(-beta) X RY(beta), leaves the cell a rotation RY(4 beta) to first order, while a fractional amplitude
  error and a post-pulse frame drift leave it unchanged to first order. Cells repeated n times from |0>
  rotate the Bloch vector by 4 n beta in the X-Z plane: theta(n) = atan2(<X>, <Z>) has slope
  ``TILT_X_SLOPE`` beta per cell. The outer wires run their cells together and the middle wire alone.
- **sx tilt.** The cell rz(pi), sx, sx, rz(pi), sx, sx is the identity and turns an sx tilt into a
  rotation about Y alone, theta(n) slope ``TILT_SX_SLOPE`` beta per cell, with no first-order amplitude
  response. A cell whose tilt generator also has a Z part would move the Bloch vector on a cone, and
  atan2(<X>, <Z>) would stop being linear in n.
- **CZ conditional phase.** The middle wire is the Ramsey target and an outer wire the control. Each pair
  CZ, CZ is the identity; a conditional phase phi after every CZ, CPhase(phi), winds the target by 2 phi per
  pair when the control is 1 and not when it is 0. The difference of the two target phase slopes over
  pairs is ``CZ_PAIR_SLOPE`` phi, and local Z errors of the target, its detuning during the pairs and the
  preparation and readout pulses cancel in the difference. The control is read with the target and each
  arm keeps only the shots whose control reads as prepared, so a control that decays during the pairs
  carries no unconditioned phase.
- **Detuning and ZZ.** Ramsey arms idle over ``RAMSEY_DELAYS_DT``. The outer wires precess together
  with the middle in 0; the middle precesses with the outers in 00, 10 and 01, keeping only shots whose
  outers read as prepared. A static detuning delta
  (Hz) appears as the phase slope ``2 pi delta`` per second in primorial_bound_residuals' frame
  RZ(2 pi delta t); the partner-in-0 ZZ rate zeta of a coupler moves the middle's slope by ``-2 pi zeta``
  when that partner is 1.

Every ladder grows by at most a factor 4 per step after its first nonzero point, so
conditional_ramsey.unwrap places each phase on the branch its shorter points predict. Two calibration
circuits read all wires prepared in 0 and in 1; each expectation is inverted through its wire's
measured assignment channel before any phase is taken. Each estimate carries a delta-method standard
error at one shot per circuit (divide by sqrt(shots)).

The circuits are written in the native gates of a Heron r2 Target (rz, sx, x, cz, delay) and carry the
compilation contract ``STRUCTURE_PRESERVING_CONTRACT``: live_run compiles them at optimization level 0 on
their pinned layout, because single-qubit fusion would collapse each identity cell and CZ cancellation
would remove each pair.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np
from qiskit import QuantumCircuit

from conditional_ramsey import corrected_expectation, unwrap

STRUCTURE_PRESERVING_CONTRACT = "structure-preserving-native-v1"
WIRES = 3
COUPLERS = ((0, 1), (1, 2))
# Cells per tilt arm and CZ pairs per CZ arm: a first step of 4 keeps 4 n beta below 0.6 rad at the sx
# gate-error tilt bound (0.036 rad) and 2 n phi below 0.9 rad at the CZ-phase bound (0.104 rad).
TILT_CELLS = (0, 4, 16, 64)
CZ_PAIRS = (0, 2, 8, 32)
# Idle delays in dt (4 ns): the first nonzero point keeps |2 pi delta| * 1 us below pi up to 500 kHz.
RAMSEY_DELAYS_DT = (0, 250, 1000, 4000)
DT_SECONDS = 4e-9
# The Heron r2 CZ duration on every coupler of the snapshot (docs/notes/ibm_heron_platform.md, 68 ns).
CZ_SECONDS = 68e-9
TILT_X_SLOPE = 4.0
TILT_SX_SLOPE = -4.0
CZ_PAIR_SLOPE = 2.0
TILT_QUADRATURES = ("z", "x")
PHASE_QUADRATURES = ("x", "y")
READOUT_MEMBERS = ("cp_readout_0", "cp_readout_1")
MIDDLE_STATES = ((0, 0), (1, 0), (0, 1))
TILT_SUBSETS = {"outer": (0, 2), "middle": (1,)}


def _circuit(name: str) -> QuantumCircuit:
    circuit = QuantumCircuit(WIRES, WIRES, name=name)
    circuit.metadata = {"compilation_contract": STRUCTURE_PRESERVING_CONTRACT}
    return circuit


def _hadamard(circuit: QuantumCircuit, wire: int) -> None:
    """H up to a global phase in native gates."""
    circuit.rz(math.pi / 2, wire)
    circuit.sx(wire)
    circuit.rz(math.pi / 2, wire)


def _read(circuit: QuantumCircuit, wire: int, quadrature: str) -> None:
    """Rotate ``wire`` so its Z readout reports the named Pauli: z unchanged, x by H, y by S^dagger then H."""
    if quadrature == "y":
        circuit.rz(-math.pi / 2, wire)
    if quadrature in ("x", "y"):
        _hadamard(circuit, wire)


def tilt_circuit(gate: str, subset: str, cells: int, quadrature: str) -> QuantumCircuit:
    """Identity cells of ``gate`` (x or sx) from |0> on the wires of ``subset``, read in ``quadrature`` (z or x).

    ``outer`` drives wires 0 and 2, which share no coupler, and ``middle`` wire 1 alone, so no two driven
    wires flip together across a coupler, where static ZZ would add a conditional phase to the cells.
    """
    circuit = _circuit(f"cp_tilt_{gate}_{subset}_{cells}_{quadrature}")
    driven = TILT_SUBSETS[subset]
    for wire in driven:
        for _ in range(cells):
            if gate == "x":
                circuit.x(wire)
                circuit.rz(math.pi, wire)
                circuit.x(wire)
                circuit.rz(math.pi, wire)
            else:
                circuit.rz(math.pi, wire)
                circuit.sx(wire)
                circuit.sx(wire)
                circuit.rz(math.pi, wire)
                circuit.sx(wire)
                circuit.sx(wire)
    for wire in driven:
        _read(circuit, wire, quadrature)
    circuit.measure(range(WIRES), range(WIRES))
    return circuit


def cz_circuit(control: int, state: int, pairs: int, quadrature: str) -> QuantumCircuit:
    """Target wire 1 on the equator, control ``control`` in |state>, ``pairs`` CZ pairs, target read."""
    circuit = _circuit(f"cp_cz_{control}_{state}_{pairs}_{quadrature}")
    if state:
        circuit.x(control)
    _hadamard(circuit, 1)
    for _ in range(pairs):
        circuit.cz(control, 1)
        circuit.cz(control, 1)
    _read(circuit, 1, quadrature)
    circuit.measure(range(WIRES), range(WIRES))
    return circuit


def ramsey_circuit(arm: str, delay: int, quadrature: str) -> QuantumCircuit:
    """``outer``: wires 0 and 2 precess with the middle in 0; ``middle_ab``: wire 1 with the outers in a, b."""
    circuit = _circuit(f"cp_ramsey_{arm}_{delay}_{quadrature}")
    targets: tuple[int, ...]
    if arm == "outer":
        targets = (0, 2)
    else:
        targets = (1,)
        for wire, bit in zip((0, 2), (int(arm[-2]), int(arm[-1])), strict=True):
            if bit:
                circuit.x(wire)
    for wire in targets:
        _hadamard(circuit, wire)
    if delay:
        for wire in range(WIRES):
            circuit.delay(delay, wire, unit="dt")
    for wire in targets:
        _read(circuit, wire, quadrature)
    circuit.measure(range(WIRES), range(WIRES))
    return circuit


def readout_circuit(prepared: int) -> QuantumCircuit:
    circuit = _circuit(f"cp_readout_{prepared}")
    if prepared:
        circuit.x(range(WIRES))
    circuit.measure(range(WIRES), range(WIRES))
    return circuit


# The case's voiding rule: a wire whose in-job readout calibration gives 1 - e10 - e01 below this floor voids every
# estimate that reads or postselects on it.
READOUT_FLOOR = 0.8


def readout_summary(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    """The readout preflight: each wire's e10, e01 and 1 - e10 - e01 from the two calibration circuits.

    ``passed`` is 1 when every wire's fidelity reaches READOUT_FLOOR and 0 otherwise.
    """
    out: dict[str, float] = {}
    for wire, (e10, e01) in enumerate(assignment(distributions)):
        out[f"e10_q{wire}"] = e10
        out[f"e01_q{wire}"] = e01
        out[f"fidelity_q{wire}"] = 1.0 - e10 - e01
    out["passed"] = float(all(out[f"fidelity_q{wire}"] >= READOUT_FLOOR for wire in range(WIRES)))
    return out


def ramsey_arms() -> tuple[str, ...]:
    return ("outer", *(f"middle_{a}{b}" for a, b in MIDDLE_STATES))


def circuits() -> tuple[tuple[str, QuantumCircuit], ...]:
    """Every probe circuit in a fixed order, the two readout calibrations last."""
    out: list[tuple[str, QuantumCircuit]] = []
    for gate in ("x", "sx"):
        for subset in TILT_SUBSETS:
            for cells in TILT_CELLS:
                for quadrature in TILT_QUADRATURES:
                    circuit = tilt_circuit(gate, subset, cells, quadrature)
                    out.append((circuit.name, circuit))
    for control in (0, 2):
        for state in (0, 1):
            for pairs in CZ_PAIRS:
                for quadrature in PHASE_QUADRATURES:
                    circuit = cz_circuit(control, state, pairs, quadrature)
                    out.append((circuit.name, circuit))
    for arm in ramsey_arms():
        for delay in RAMSEY_DELAYS_DT:
            for quadrature in PHASE_QUADRATURES:
                circuit = ramsey_circuit(arm, delay, quadrature)
                out.append((circuit.name, circuit))
    for prepared in (0, 1):
        circuit = readout_circuit(prepared)
        out.append((circuit.name, circuit))
    return tuple(out)


# --------------------------------------------------------------- estimators


def _bit(index: int, wire: int) -> int:
    return index >> wire & 1


def assignment(distributions: Mapping[str, np.ndarray]) -> list[tuple[float, float]]:
    """Per wire (e10, e01): P(read 1 | prepared 0) and P(read 0 | prepared 1)."""
    zero, one = distributions[READOUT_MEMBERS[0]], distributions[READOUT_MEMBERS[1]]
    return [
        (
            float(sum(p for k, p in enumerate(zero) if _bit(k, wire))),
            float(sum(p for k, p in enumerate(one) if not _bit(k, wire))),
        )
        for wire in range(WIRES)
    ]


Keep = tuple[tuple[int, int], ...]


def _expectation(
    distribution: np.ndarray, wire: int, keep: Keep = (), covariance: np.ndarray | None = None
) -> tuple[float, float]:
    """<Z> of ``wire`` over outcomes whose every (wire, bit) of ``keep`` holds, and its one-shot variance.

    The kept-outcome mean is a ratio of linear functions of the law, so its variance is g^T C g for the gradient
    g_k = (s_k - z) / P_K on kept outcomes; C is the multinomial covariance diag(p) - p p^T of a raw law, where
    g^T C g = (1 - z^2) / P_K, or the covariance live_run.corrected_summary supplies for a readout-inverted law.
    """
    law = np.asarray(distribution, dtype=float)
    kept = np.asarray([all(_bit(k, w) == bit for w, bit in keep) for k in range(len(law))])
    signs = np.asarray([1 - 2 * _bit(k, wire) for k in range(len(law))], dtype=float)
    total = float(law[kept].sum())
    if total <= 0.0:
        raise ValueError("no outcome survives the control postselection")
    z = float(signs[kept] @ law[kept]) / total
    gradient = np.where(kept, (signs - z) / total, 0.0)
    matrix = np.diag(law) - np.outer(law, law) if covariance is None else np.asarray(covariance, dtype=float)
    return z, float(gradient @ matrix @ gradient)


def _point(
    distributions: Mapping[str, np.ndarray],
    names: tuple[str, str],
    wire: int,
    flips: tuple[float, float],
    keep: Keep = (),
    covariances: Mapping[str, np.ndarray] | None = None,
) -> tuple[float, float]:
    """Phase atan2(second, first) of two corrected quadratures and its one-shot variance."""
    values = []
    variances = []
    e10, e01 = flips
    scale = (1.0 - e10 - e01) ** 2
    for name in names:
        covariance = None if covariances is None else covariances[name]
        raw, variance = _expectation(distributions[name], wire, keep, covariance)
        values.append(corrected_expectation(raw, e10, e01))
        variances.append(variance / scale)
    first, second = values
    norm = first**2 + second**2
    if norm <= 0.0:
        raise ValueError(f"{names}: zero visibility")
    variance = (second**2 * variances[0] + first**2 * variances[1]) / norm**2
    return math.atan2(second, first), variance


def _slope(steps: tuple[int, ...], phases: list[float], variances: list[float]) -> tuple[float, float]:
    """Unweighted least-squares slope of the unwrapped phases and its variance from per-point variances."""
    unwrapped = unwrap(steps, phases)
    x = np.asarray(steps, dtype=float)
    weights = (x - x.mean()) / float(np.sum((x - x.mean()) ** 2))
    return float(weights @ np.asarray(unwrapped)), float(np.sum(weights**2 * np.asarray(variances)))


# Independent components: each comes from its own circuits, so their quadrature noises are independent. The
# reported estimates are linear in them; the assignment flips of the two readout calibrations are shared.
COMPONENTS = (
    *(f"tilt_{gate}_q{w}" for gate in ("x", "sx") for w in range(WIRES)),
    "cz_raw_c0",
    "cz_raw_c1",
    "detuning_q0",
    "detuning_q1",
    "detuning_q2",
    "rate_middle_10",
    "rate_middle_01",
)
FLIPS = tuple((w, j) for w in range(WIRES) for j in ("e10", "e01"))
FLIP_STEP = 1e-6
# The pair probe winds by phi - 2 pi zeta tau per CZ, the partner-in-0 ZZ acting over each CZ of duration tau;
# the conditional phase is the raw estimate plus that ZZ share.
ZZ_SHARE = 2 * math.pi * CZ_SECONDS


def derived(components: Mapping[str, float]) -> dict[str, float]:
    """zz_c* (Hz) and cz_phase_c* (rad) from the components: a conditioned rate minus the middle qubit's own."""
    out: dict[str, float] = {}
    for index, arm in enumerate(("rate_middle_10", "rate_middle_01")):
        out[f"zz_c{index}"] = -(components[arm] - components["detuning_q1"])
        out[f"cz_phase_c{index}"] = components[f"cz_raw_c{index}"] + ZZ_SHARE * out[f"zz_c{index}"]
    return out


def _components(
    distributions: Mapping[str, np.ndarray],
    flips: list[tuple[float, float]],
    covariances: Mapping[str, np.ndarray] | None,
) -> tuple[dict[str, float], dict[str, float]]:
    """Every component and its one-shot quadrature variance at the given assignment flips."""
    value: dict[str, float] = {}
    variance: dict[str, float] = {}
    for gate, gain in (("x", TILT_X_SLOPE), ("sx", TILT_SX_SLOPE)):
        for wire in range(WIRES):
            subset = "middle" if wire == 1 else "outer"
            points = [
                _point(
                    distributions,
                    (f"cp_tilt_{gate}_{subset}_{cells}_z", f"cp_tilt_{gate}_{subset}_{cells}_x"),
                    wire,
                    flips[wire],
                    covariances=covariances,
                )
                for cells in TILT_CELLS
            ]
            slope, slope_var = _slope(TILT_CELLS, [p for p, _ in points], [v for _, v in points])
            value[f"tilt_{gate}_q{wire}"] = slope / gain
            variance[f"tilt_{gate}_q{wire}"] = slope_var / gain**2
    for index, control in enumerate((0, 2)):
        slopes = []
        for state in (0, 1):
            points = [
                _point(
                    distributions,
                    (f"cp_cz_{control}_{state}_{pairs}_x", f"cp_cz_{control}_{state}_{pairs}_y"),
                    1,
                    flips[1],
                    keep=((control, state),),
                    covariances=covariances,
                )
                for pairs in CZ_PAIRS
            ]
            slopes.append(_slope(CZ_PAIRS, [p for p, _ in points], [v for _, v in points]))
        value[f"cz_raw_c{index}"] = (slopes[1][0] - slopes[0][0]) / CZ_PAIR_SLOPE
        variance[f"cz_raw_c{index}"] = (slopes[0][1] + slopes[1][1]) / CZ_PAIR_SLOPE**2
    hertz = 2 * math.pi * DT_SECONDS
    for arm in ramsey_arms():
        for wire in (0, 2) if arm == "outer" else (1,):
            points = [
                _point(
                    distributions,
                    (f"cp_ramsey_{arm}_{delay}_x", f"cp_ramsey_{arm}_{delay}_y"),
                    wire,
                    flips[wire],
                    keep=() if arm == "outer" else ((0, int(arm[-2])), (2, int(arm[-1]))),
                    covariances=covariances,
                )
                for delay in RAMSEY_DELAYS_DT
            ]
            slope, slope_var = _slope(RAMSEY_DELAYS_DT, [p for p, _ in points], [v for _, v in points])
            key = f"detuning_q{wire}" if arm in ("outer", "middle_00") else f"rate_{arm}"
            value[key] = slope / hertz
            variance[key] = slope_var / hertz**2
    return value, variance


def _flip_variances(
    distributions: Mapping[str, np.ndarray], covariances: Mapping[str, np.ndarray] | None
) -> dict[tuple[int, str], float]:
    """One-shot variance of each wire's e10 (from cp_readout_0) and e01 (from cp_readout_1)."""
    out: dict[tuple[int, str], float] = {}
    for wire in range(WIRES):
        for flip, name, wrong in (("e10", READOUT_MEMBERS[0], 1), ("e01", READOUT_MEMBERS[1], 0)):
            law = np.asarray(distributions[name], dtype=float)
            indicator = np.asarray([float(_bit(k, wire) == wrong) for k in range(len(law))])
            matrix = np.diag(law) - np.outer(law, law) if covariances is None else np.asarray(covariances[name])
            out[wire, flip] = float(indicator @ matrix @ indicator)
    return out


def summarize(
    distributions: Mapping[str, np.ndarray], covariances: Mapping[str, np.ndarray] | None = None
) -> dict[str, float]:
    """Every estimate and its one-shot standard error (key ``se_<estimate>``), with the inputs a joint decision needs.

    Keys: ``tilt_x_q<w>`` and ``tilt_sx_q<w>`` (rad), ``cz_phase_c<k>`` (rad, coupler index k of COUPLERS;
    ``cz_raw_c<k>`` before the ZZ share), ``detuning_q<w>`` (Hz), ``zz_c<k>`` (Hz, partner-in-0 frame) and the
    conditioned middle-qubit rates ``rate_middle_10`` and ``rate_middle_01`` (Hz). Each ``se_`` combines the
    quadrature noise of the estimate's circuits with the finite-shot noise of the in-job readout calibration,
    which every point of a ladder shares: ``qse_<component>`` is the quadrature part, ``d_<component>__<flip>_q<w>``
    the component's derivative with respect to that assignment flip and ``var_<flip>_q<w>`` the flip's one-shot
    variance, so a decision can sample the components and flips jointly and keep their correlations.
    """
    flips = assignment(distributions)
    value, quadrature = _components(distributions, flips, covariances)
    flip_var = _flip_variances(distributions, covariances)
    slope: dict[tuple[int, str], dict[str, float]] = {}
    for wire, flip in FLIPS:
        shifted = []
        for sign in (1.0, -1.0):
            moved = list(flips)
            e10, e01 = moved[wire]
            moved[wire] = (e10 + sign * FLIP_STEP, e01) if flip == "e10" else (e10, e01 + sign * FLIP_STEP)
            shifted.append(_components(distributions, moved, covariances)[0])
        slope[wire, flip] = {c: (shifted[0][c] - shifted[1][c]) / (2 * FLIP_STEP) for c in COMPONENTS}
    out: dict[str, float] = dict(value)
    for c in COMPONENTS:
        out[f"qse_{c}"] = math.sqrt(quadrature[c])
        for wire, flip in FLIPS:
            out[f"d_{c}__{flip}_q{wire}"] = slope[wire, flip][c]
    for wire, flip in FLIPS:
        out[f"var_{flip}_q{wire}"] = flip_var[wire, flip]
    out.update(derived(value))
    # Each reported quantity is linear in the components; its variance adds the independent quadrature terms
    # and the shared flip terms through that linear map.
    linear: dict[str, dict[str, float]] = {c: {c: 1.0} for c in COMPONENTS}
    for index, arm in enumerate(("rate_middle_10", "rate_middle_01")):
        linear[f"zz_c{index}"] = {arm: -1.0, "detuning_q1": 1.0}
        linear[f"cz_phase_c{index}"] = {f"cz_raw_c{index}": 1.0, arm: -ZZ_SHARE, "detuning_q1": ZZ_SHARE}
    for key, weights in linear.items():
        total = sum(w**2 * quadrature[c] for c, w in weights.items())
        for wire, flip in FLIPS:
            total += sum(w * slope[wire, flip][c] for c, w in weights.items()) ** 2 * flip_var[wire, flip]
        out[f"se_{key}"] = math.sqrt(total)
    return out


def ideal_distribution(circuit: QuantumCircuit) -> np.ndarray:
    """Noise-free outcome law of a probe circuit."""
    from qiskit.quantum_info import Statevector

    return np.asarray(Statevector(circuit.remove_final_measurements(inplace=False)).probabilities(), dtype=float)


def summarize_with_covariance(
    distributions: Mapping[str, np.ndarray], covariances: Mapping[str, np.ndarray]
) -> dict[str, float]:
    """summarize on readout-inverted laws, every variance propagated through the supplied covariances."""
    return summarize(distributions, covariances)
