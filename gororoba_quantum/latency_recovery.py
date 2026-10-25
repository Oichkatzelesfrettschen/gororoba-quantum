"""Latency-recovery family: a bit-flip code's feed-forward correction against a Pauli frame.

A reference qubit r and a three-qubit repetition code d0 d1 d2 hold a Bell
pair. Two syndrome ancillas a0 and a1 are measured into the 2-bit register s,
and a single conditional X on d0 (s == 1) corrects an X error on d0. The
arms differ in the idle window after the syndrome readout and in whether the
correction is the conditional or a Pauli frame applied to the readout of d0
(docs/design/heron-latency-logical-recovery.md). Clbit order is s[0], s[1],
o[0] = r, o[1] = d0, so an outcome index is s + 4 * o and an expectation is
the parity of o[0] xor o[1].
"""

from __future__ import annotations

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer.noise import NoiseModel

import dynamic_density
from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member

LATENCY_RECOVERY_FAMILY = "latency-recovery"
GROUP_NAME = "latency_recovery"
# L in dt on ibm_kingston: the 208-cycle two-capture broadcast plus its 7
# cycles of scheduled overhead (docs/evidence/heron_platform/feedforward-latency.json).
# W, 10 us, is long enough that the T1/T2 loss of the four-qubit block exceeds the
# Hoeffding half-width at 16384 shots, so the window cost resolves delta. Another
# backend supplies its own L through --latency-dt and W through --window-dt.
DEFAULT_LATENCY_DT = 215
DEFAULT_WINDOW_DT = 2500

REFERENCE, DATA, ANCILLAS = 0, (1, 2, 3), (4, 5)
FF_ARMS = ("ff_0", "ff_w")
FRAME_ARMS = ("frame_0", "frame_l", "frame_lw")
UNENCODED_ARM = "ff_0_unencoded"
ENCODED_ARMS = (*FF_ARMS, *FRAME_ARMS)
ARMS = (*ENCODED_ARMS, UNENCODED_ARM)
# The Pauli letters on r and on d0 of each basis. XX, YY and ZZ give F; XY and
# YX add the quadrature that separates a coherent phase from a decay.
BASES = {"XX": ("X", "X"), "YY": ("Y", "Y"), "ZZ": ("Z", "Z"), "XY": ("X", "Y"), "YX": ("Y", "X")}
FIDELITY_BASES = ("XX", "YY", "ZZ")
# The syndrome value s = a0 + 2 a1 an X error on d0 produces.
ERROR_SYNDROME = 1
# The inferential tests sharing the family alpha: recovery, code_property,
# latency_cost, latency_is_idle, window_cost_ff, window_cost_frame and window_slope.
INFERENTIAL_TESTS = 7
# Two-sided half-widths the planner must reach on the difference endpoints. The
# analysis decides latency_cost and both window costs (lower bound above 0),
# latency_is_idle and window_slope (interval inside +-0.01) on the retained
# intervals; the +-0.01 margin lies below any interval the Hoeffding radii at
# the listed shot tiers admit, so the contracts price resolution only.
LATENCY_PRECISION = 0.05
WINDOW_SLOPE_PRECISION = 0.1
_OUTCOMES = 16


def arm_has_window(arm: str) -> bool:
    """Whether the arm idles r, d0, d1 and d2 after the syndrome readout."""
    return arm in ("ff_w", "frame_l", "frame_lw")


def arm_window_dt(arm: str, latency_dt: int, window_dt: int) -> int:
    """The delay an arm inserts after the syndrome barrier, in dt; 0 for an arm without one."""
    return {"ff_w": window_dt, "frame_l": latency_dt, "frame_lw": latency_dt + window_dt}.get(arm, 0)


def member_arms() -> tuple[tuple[str, bool, str], ...]:
    """(arm, error, basis) of every member in group order: 25 encoded error, 6 error-free, 3 unencoded."""
    members = [(arm, True, basis) for arm in ENCODED_ARMS for basis in BASES]
    members += [(arm, False, basis) for arm in ("ff_0", "frame_0") for basis in FIDELITY_BASES]
    members += [(UNENCODED_ARM, True, basis) for basis in FIDELITY_BASES]
    return tuple(members)


def member_name(arm: str, error: bool, basis: str) -> str:
    return f"lr_{arm}_{'err' if error else 'ok'}_{basis}"


def check_window_dt(latency_dt: object, window_dt: object) -> tuple[int, int]:
    """L and W as positive integer dt; anything else raises."""
    for label, value in (("latency_dt", latency_dt), ("window_dt", window_dt)):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{label} must be a positive integer dt, not {value!r}")
    return int(latency_dt), int(window_dt)  # type: ignore[call-overload]


def latency_recovery_circuit(arm: str, error: bool, basis: str, latency_dt: int, window_dt: int) -> QuantumCircuit:
    """One member: prepare, optionally err, read the syndrome, idle or correct, decode and measure in a basis.

    Barriers over every qubit bracket the two ancilla measurements, so r and
    the data qubits idle through the readout in every arm. The conditional is
    one X on d0 that tests s == 1.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown latency-recovery arm {arm!r}")
    if basis not in BASES:
        raise ValueError(f"unknown latency-recovery basis {basis!r}")
    if arm == UNENCODED_ARM and not error:
        raise ValueError("the unencoded arm runs with the error only")
    latency_dt, window_dt = check_window_dt(latency_dt, window_dt)
    qubits = QuantumRegister(6, "q")
    syndrome = ClassicalRegister(2, "s")
    output = ClassicalRegister(2, "o")
    circuit = QuantumCircuit(qubits, syndrome, output, name=member_name(arm, error, basis))
    r, d0, d1, d2 = (qubits[REFERENCE], *(qubits[i] for i in DATA))
    a0, a1 = (qubits[i] for i in ANCILLAS)
    encoded = arm != UNENCODED_ARM
    circuit.h(r)
    circuit.cx(r, d0)
    if encoded:
        circuit.cx(d0, d1)
        circuit.cx(d0, d2)
    if error:
        circuit.x(d0)
    circuit.cx(d0, a0)
    circuit.cx(d1, a0)
    circuit.cx(d1, a1)
    circuit.cx(d2, a1)
    circuit.barrier(label="syndrome_open")
    circuit.measure(a0, syndrome[0])
    circuit.measure(a1, syndrome[1])
    circuit.barrier(label="syndrome_close")
    delay = arm_window_dt(arm, latency_dt, window_dt)
    if delay:
        for qubit in (r, d0, d1, d2):
            circuit.delay(delay, qubit)
    if arm in (*FF_ARMS, UNENCODED_ARM):
        with circuit.if_test((syndrome, ERROR_SYNDROME)):
            circuit.x(d0)
    if encoded:
        circuit.cx(d0, d2)
        circuit.cx(d0, d1)
    for qubit, letter in zip((r, d0), BASES[basis], strict=True):
        if letter == "Y":
            circuit.sdg(qubit)
        if letter != "Z":
            circuit.h(qubit)
    circuit.measure(r, output[0])
    circuit.measure(d0, output[1])
    return circuit


def syndrome_window_violations(circuit: QuantumCircuit) -> list[str]:
    """Operations other than measurements between the barriers that bracket the syndrome readout.

    The window opens at the last barrier before the first measurement into s
    (clbits 0 and 1) and closes at the first barrier after the last, so the
    check reads a source circuit and a compiled ISA circuit alike. A circuit
    without a bracketed syndrome readout raises.
    """
    data = list(circuit.data)
    measured = [
        index
        for index, item in enumerate(data)
        if item.operation.name == "measure" and circuit.find_bit(item.clbits[0]).index in (0, 1)
    ]
    if len(measured) != 2:
        raise ValueError(f"{circuit.name}: expected two syndrome measurements, found {len(measured)}")
    opening = max((i for i in range(measured[0]) if data[i].operation.name == "barrier"), default=None)
    closing = min((i for i in range(measured[-1] + 1, len(data)) if data[i].operation.name == "barrier"), default=None)
    if opening is None or closing is None:
        raise ValueError(f"{circuit.name}: the syndrome measurements are not bracketed by barriers")
    return [
        f"{item.operation.name} on {[circuit.find_bit(qubit).index for qubit in item.qubits]}"
        for item in data[opening + 1 : closing]
        if item.operation.name not in ("measure", "barrier")
    ]


def outcome_scores(basis: str, framed: bool) -> np.ndarray:
    """The +-1 parity of o[0] xor o[1] at each of the 16 outcomes, with the Pauli-frame flip when framed.

    The frame flips the d0 bit of a basis whose d0 factor is Z or Y when
    s == ERROR_SYNDROME, because the uncorrected X on d0 anticommutes with
    those factors and commutes with X.
    """
    flips = framed and BASES[basis][1] in ("Y", "Z")
    scores = np.empty(_OUTCOMES)
    for outcome in range(_OUTCOMES):
        syndrome, output = outcome & 3, outcome >> 2
        flip = int(flips and syndrome == ERROR_SYNDROME)
        scores[outcome] = -1.0 if (output ^ (output >> 1) ^ flip) & 1 else 1.0
    return scores


def expectation(distribution: np.ndarray, basis: str, framed: bool = False) -> float:
    return float(np.asarray(distribution, dtype=float) @ outcome_scores(basis, framed))


def fidelity(expectations: dict[str, float]) -> float:
    """Entanglement fidelity with the Bell state, (1 + <XX> - <YY> + <ZZ>) / 4."""
    return (1.0 + expectations["XX"] - expectations["YY"] + expectations["ZZ"]) / 4.0


def coherence_and_phase(expectations: dict[str, float]) -> tuple[float, float]:
    """C = sqrt(((XX - YY)/2)^2 + ((XY + YX)/2)^2) and phi = atan2((XY + YX)/2, (XX - YY)/2)."""
    real = (expectations["XX"] - expectations["YY"]) / 2.0
    imaginary = (expectations["XY"] + expectations["YX"]) / 2.0
    return float(np.hypot(real, imaginary)), float(np.arctan2(imaginary, real))


def ideal_law(circuit: QuantumCircuit) -> np.ndarray:
    """The exact noiseless distribution over the 4 clbits; delays are the identity and the model omits them."""
    stripped = circuit.copy_empty_like()
    for item in circuit.data:
        if item.operation.name != "delay":
            stripped.append(item)
    return dynamic_density.probabilities(stripped, NoiseModel())


def latency_recovery_group(latency_dt: int, window_dt: int) -> Group:
    """The 34 members as one dynamic group, with F, C and phi per arm and the uncorrected frame arms.

    A frame arm's primary values apply the Pauli-frame flip; its
    uncorrected_ values read the same distributions without it, and the
    frame_0 uncorrected fidelity is the no-correction null.
    """
    latency_dt, window_dt = check_window_dt(latency_dt, window_dt)
    members = []
    for arm, error, basis in member_arms():
        circuit = latency_recovery_circuit(arm, error, basis, latency_dt, window_dt)
        scores = outcome_scores(basis, arm in FRAME_ARMS)
        members.append(
            Member(
                circuit.name,
                circuit,
                ideal_law(circuit),
                weights=(1.0 + scores) / 2.0,
            )
        )

    def arm_values(
        distributions: dict[str, np.ndarray], arm: str, error: bool, framed: bool
    ) -> dict[str, float] | None:
        bases = [basis for basis in BASES if member_name(arm, error, basis) in distributions]
        if not set(FIDELITY_BASES) <= set(bases):
            return None
        return {basis: expectation(distributions[member_name(arm, error, basis)], basis, framed) for basis in bases}

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result: dict[str, float] = {}
        values: dict[tuple[str, bool], dict[str, float]] = {}
        for arm in ARMS:
            for error in (True, False):
                framed = arm in FRAME_ARMS
                expectations = arm_values(distributions, arm, error, framed)
                if expectations is None:
                    continue
                values[(arm, error)] = expectations
                stem = f"{arm}_{'err' if error else 'ok'}"
                result.update({f"{stem}_{basis}_expectation": value for basis, value in expectations.items()})
                result[f"{stem}_F"] = fidelity(expectations)
                if len(expectations) == len(BASES):
                    result[f"{stem}_C"], result[f"{stem}_phi"] = coherence_and_phase(expectations)
                if framed:
                    raw = arm_values(distributions, arm, error, False)
                    if raw is None:
                        raise ValueError(f"{stem}: uncorrected expectations are missing")
                    result.update({f"{stem}_uncorrected_{basis}_expectation": value for basis, value in raw.items()})
                    result[f"{stem}_uncorrected_F"] = fidelity(raw)
        # Differences the contracts bound, and the descriptive decay_not_phase pair.
        keys = ("ff_0_err_C", "frame_0_err_C", "ff_0_err_phi", "frame_0_err_phi")
        if all(key in result for key in keys):
            result["decay_not_phase_C_loss"] = result["frame_0_err_C"] - result["ff_0_err_C"]
            result["decay_not_phase_phi_shift"] = result["ff_0_err_phi"] - result["frame_0_err_phi"]
        if all(key in result for key in ("ff_0_err_F", "frame_0_err_F", "frame_l_err_F")):
            result["latency_cost"] = result["frame_0_err_F"] - result["ff_0_err_F"]
            result["latency_is_idle_difference"] = result["frame_l_err_F"] - result["ff_0_err_F"]
        slope = ("ff_0_err_F", "ff_w_err_F", "frame_l_err_F", "frame_lw_err_F")
        if all(key in result for key in slope):
            result["window_slope_ff"] = result["ff_0_err_F"] - result["ff_w_err_F"]
            result["window_slope_frame"] = result["frame_l_err_F"] - result["frame_lw_err_F"]
            result["window_slope_difference"] = result["window_slope_ff"] - result["window_slope_frame"]
        return result

    return Group(GROUP_NAME, tuple(members), summarize)


def _fidelity_terms(arm: str, sign: int, framed: bool | None = None) -> tuple[ObservableTerm, ...]:
    """The three terms whose signed sum is sign * F of an arm's error members.

    The 1/4 of F scales each score vector and YY enters negatively. framed
    defaults to the arm's own correction; False reads a frame arm as the
    no-correction null.
    """
    framed = arm in FRAME_ARMS if framed is None else framed
    return tuple(
        ObservableTerm(
            member_name(arm, True, basis),
            tuple(float(v) for v in (-0.25 if basis == "YY" else 0.25) * outcome_scores(basis, framed)),
            sign=sign,
        )
        for basis in FIDELITY_BASES
    )


def latency_recovery_contracts(alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """The planner's contracts at alpha split equally over INFERENTIAL_TESTS.

    recovery and code_property are one-sided differences of F against
    thresholds 0.5 and 0.25 (the modeled gap is the alternative). The model
    predicts no latency cost, since Aer applies the conditional instantly, so
    latency_cost, latency_is_idle, the two window costs (ff_0 - ff_w and
    frame_l - frame_lw, the decay over W that measures delta) and window_slope
    are two-sided precision endpoints on their differences, so admission does
    not rest on the model's decay; the analysis applies the preregistered rules
    to the intervals. decay_not_phase is descriptive and has no
    contract; the group's summary reports it.
    """
    share = alpha / INFERENTIAL_TESTS

    def directional(name: str, terms: tuple[ObservableTerm, ...], null: float) -> ObservableContract:
        return ObservableContract(name, terms, null_value=null, minimum_effect=0.0, alpha=share, power=power)

    def precision(name: str, terms: tuple[ObservableTerm, ...], half_width: float) -> ObservableContract:
        return ObservableContract(name, terms, alpha=share, power=power, precision_half_width=half_width)

    slope = (
        _fidelity_terms("ff_0", 1)
        + _fidelity_terms("ff_w", -1)
        + _fidelity_terms("frame_l", -1)
        + _fidelity_terms("frame_lw", 1)
    )
    return (
        directional("lr_recovery", _fidelity_terms("ff_0", 1) + _fidelity_terms("frame_0", -1, framed=False), 0.5),
        directional("lr_code_property", _fidelity_terms("ff_0", 1) + _fidelity_terms(UNENCODED_ARM, -1), 0.25),
        precision("lr_latency_cost", _fidelity_terms("frame_0", 1) + _fidelity_terms("ff_0", -1), LATENCY_PRECISION),
        precision("lr_latency_is_idle", _fidelity_terms("frame_l", 1) + _fidelity_terms("ff_0", -1), LATENCY_PRECISION),
        precision("lr_window_cost_ff", _fidelity_terms("ff_0", 1) + _fidelity_terms("ff_w", -1), LATENCY_PRECISION),
        precision(
            "lr_window_cost_frame", _fidelity_terms("frame_l", 1) + _fidelity_terms("frame_lw", -1), LATENCY_PRECISION
        ),
        precision("lr_window_slope", slope, WINDOW_SLOPE_PRECISION),
    )
