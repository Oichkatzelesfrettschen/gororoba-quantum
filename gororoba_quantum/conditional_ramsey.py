"""Conditional Ramsey on a coupled pair: a rank-three design for the diagonal pair Hamiltonian.

The reduced model is H / hbar = (omega_A Z_A + omega_B Z_B + J Z_A Z_B) / 2
on the basis |ab> with Z|0> = |0>. A coherence between basis states x and y
winds as rho_xy(t) = exp(-i nu t) rho_xy(0) with nu = E_x - E_y, so the four
sectors read

    Bell even  (|00>, |11>):  nu = omega_A + omega_B
    Bell odd   (|01>, |10>):  nu = omega_A - omega_B
    A | B = 0  (|00>, |10>):  nu = omega_A + J
    A | B = 1  (|01>, |11>):  nu = omega_A - J

Both Bell sectors are blind to J, because the two states of each sector
share one Z_A Z_B eigenvalue: the Bell-only design matrix has rank two with
null direction J. The conditional sectors raise the rank to three and give
J = (nu_A|0 - nu_A|1) / 2, and the overdetermined fourth row is the
falsifier nu_odd + nu_even = nu_A|0 + nu_A|1 of the reduced, static,
diagonal model.

Each sector is a two-qubit circuit, A on qubit 0 and B on qubit 1, measured
into the clbit of the same index. A Bell arm prepares the sector state with
H and CX, idles, undoes the CX and reads A in the X or Y basis; a
conditional arm prepares B in |b>, puts A on the equator, idles and reads A.
Either way A ends in (|0> + exp(i nu t)|1>) / sqrt2 times a fixed phase, so
<X_A> = V cos(nu t + phi0) and <Y_A> = V sin(nu t + phi0). The delays are
integer dt on both qubits; the fitted slope over delays is the rate, and
fixed gate durations and preparation phases fall into the intercept.
Consecutive delays differ by at most DELAY_STEP_DT, so a rate below
pi / DELAY_STEP_DT rad per dt unwraps without ambiguity; dynamical
decoupling would refocus the free evolution these arms measure.

Two calibration circuits read both qubits prepared in |0> and in |1>. The
summary inverts A's measured assignment channel before taking phases,
because an asymmetric channel adds a common offset to both quadratures that
the slope would absorb as a delay-dependent phase error. It reports each
rate, parameter and the falsifier residual with a delta-method standard
error at one shot per circuit (divide by sqrt(shots)), propagated through
the calibration, the phase fits and the reconstruction.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from fractions import Fraction

import numpy as np
from qiskit import QuantumCircuit

from experiments import Group, Member

SECTORS = ("even", "odd", "a_given_b0", "a_given_b1")
# Rows of the design matrix over (omega_A, omega_B, J).
DESIGN_ROWS: dict[str, tuple[int, int, int]] = {
    "even": (1, 1, 0),
    "odd": (1, -1, 0),
    "a_given_b0": (1, 0, 1),
    "a_given_b1": (1, 0, -1),
}
DELAYS_DT = (0, 1250, 2500, 5000, 7500, 10000)
DELAY_STEP_DT = max(b - a for a, b in zip(DELAYS_DT, DELAYS_DT[1:], strict=False))
QUADRATURES = ("x", "y")
B_PREPARED = {"even": 0, "odd": 1, "a_given_b0": 0, "a_given_b1": 1}
# In-job assignment calibration: both qubits prepared in |0>, and both in |1>.
READOUT_MEMBERS = ("cr_readout_0", "cr_readout_1")
SE_KEYS = (
    *(f"{sector}_rate_rad_per_dt" for sector in ("even", "odd", "a_given_b0", "a_given_b1")),
    "omega_a_bell",
    "omega_a_conditional",
    "omega_b",
    "zz_j",
    "falsifier_residual",
)

Evolution = Callable[[QuantumCircuit, str, int], None]


def member_name(sector: str, quadrature: str, delay: int) -> str:
    return f"cr_{sector}_{quadrature}_{delay}dt"


def idle(circuit: QuantumCircuit, sector: str, delay: int) -> None:
    if delay:
        circuit.delay(delay, [0, 1], unit="dt")


def sector_circuit(sector: str, quadrature: str, delay: int, evolve: Evolution = idle) -> QuantumCircuit:
    circuit = QuantumCircuit(2, 2, name=member_name(sector, quadrature, delay))
    if B_PREPARED[sector]:
        circuit.x(1)
    circuit.h(0)
    bell = sector in {"even", "odd"}
    if bell:
        circuit.cx(0, 1)
    circuit.barrier()
    evolve(circuit, sector, delay)
    circuit.barrier()
    if bell:
        circuit.cx(0, 1)
    if quadrature == "y":
        circuit.sdg(0)
    circuit.h(0)
    circuit.measure([0, 1], [0, 1])
    return circuit


def ideal_distribution(sector: str, quadrature: str) -> np.ndarray:
    """Outcome law of an ideal idle: A reads 0 in X and is uniform in Y; B keeps its preparation."""
    ideal = np.zeros(4)
    b = B_PREPARED[sector] << 1
    if quadrature == "x":
        ideal[b] = 1.0
    else:
        ideal[b] = ideal[b | 1] = 0.5
    return ideal


def readout_circuit(prepared: int) -> QuantumCircuit:
    circuit = QuantumCircuit(2, 2, name=READOUT_MEMBERS[prepared])
    if prepared:
        circuit.x([0, 1])
    circuit.measure([0, 1], [0, 1])
    return circuit


def circuits(evolve: Evolution = idle) -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    sectors = tuple(
        (
            member_name(sector, quadrature, delay),
            sector_circuit(sector, quadrature, delay, evolve),
            ideal_distribution(sector, quadrature),
        )
        for sector in SECTORS
        for delay in DELAYS_DT
        for quadrature in QUADRATURES
    )
    calibration = tuple(
        (READOUT_MEMBERS[prepared], readout_circuit(prepared), np.eye(4)[3 * prepared]) for prepared in (0, 1)
    )
    return sectors + calibration


def a_expectation(distribution: np.ndarray) -> float:
    """<Z> of the rotated A readout, 1 - 2 P(A = 1), from a four-outcome distribution."""
    return float(1.0 - 2.0 * (distribution[1] + distribution[3]))


def a_assignment(distributions: Mapping[str, np.ndarray]) -> tuple[float, float]:
    """A's flips from the in-job calibration: e10 = P(1 | prepared 0), e01 = P(0 | prepared 1).

    The channel maps a true expectation q to (1 - e10 - e01) q + (e01 - e10)
    in both quadratures. The common offset moves the centre of the Ramsey
    circle, so atan2 of raw expectations carries a phase error that changes
    with the true phase and therefore with delay; inverting the channel
    removes it.
    """
    zero, one = distributions[READOUT_MEMBERS[0]], distributions[READOUT_MEMBERS[1]]
    return float(zero[1] + zero[3]), float(one[0] + one[2])


def corrected_expectation(raw: float, e10: float, e01: float) -> float:
    return (raw - (e01 - e10)) / (1.0 - e10 - e01)


def b_preparation_error(distribution: np.ndarray, sector: str) -> float:
    b = B_PREPARED[sector]
    return float(distribution[(1 - b) << 1] + distribution[((1 - b) << 1) | 1])


def unwrap(phases: list[float]) -> list[float]:
    """Unwrap consecutive phases whose true increments lie in (-pi, pi]."""
    out = [phases[0]]
    for phase in phases[1:]:
        step = math.remainder(phase - out[-1], 2.0 * math.pi)
        out.append(out[-1] + step)
    return out


def fit_rate(delays: tuple[int, ...], phases: list[float]) -> tuple[float, float]:
    """Least-squares slope (rad per dt) and intercept of unwrapped phase against delay."""
    unwrapped = unwrap(phases)
    slope, intercept = np.polyfit(np.asarray(delays, dtype=float), np.asarray(unwrapped), 1)
    return float(slope), float(intercept)


def reconstruct(rates: Mapping[str, float]) -> dict[str, float]:
    """omega_A, omega_B and J from the four sector rates, with the falsifier residual."""
    even, odd = rates["even"], rates["odd"]
    given0, given1 = rates["a_given_b0"], rates["a_given_b1"]
    return {
        "omega_a_bell": (odd + even) / 2.0,
        "omega_a_conditional": (given0 + given1) / 2.0,
        "omega_b": (even - odd) / 2.0,
        "zz_j": (given0 - given1) / 2.0,
        "falsifier_residual": odd + even - given0 - given1,
    }


def design_rank(sectors: tuple[str, ...]) -> int:
    """Exact rank over Q of the design rows of the named sectors."""
    rows = [[Fraction(value) for value in DESIGN_ROWS[sector]] for sector in sectors]
    rank = 0
    for column in range(3):
        pivot = next((index for index in range(rank, len(rows)) if rows[index][column] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][column] != 0:
                factor = rows[index][column] / rows[rank][column]
                rows[index] = [a - factor * b for a, b in zip(rows[index], rows[rank], strict=True)]
        rank += 1
    return rank


def unambiguous_rate_bound() -> float:
    """Largest |nu| in rad per dt whose phase step between consecutive delays stays inside pi."""
    return math.pi / DELAY_STEP_DT


def rate_hz(rate_rad_per_dt: float, dt_seconds: float) -> float:
    return rate_rad_per_dt / (2.0 * math.pi * dt_seconds)


def point_summary(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    """Phases, fitted rates and reconstructed parameters on assignment-corrected expectations."""
    e10, e01 = a_assignment(distributions)
    summary: dict[str, float] = {"a_assignment_e10": e10, "a_assignment_e01": e01}
    rates: dict[str, float] = {}
    for sector in SECTORS:
        phases = []
        for delay in DELAYS_DT:
            x = corrected_expectation(a_expectation(distributions[member_name(sector, "x", delay)]), e10, e01)
            y = corrected_expectation(a_expectation(distributions[member_name(sector, "y", delay)]), e10, e01)
            phases.append(math.atan2(y, x))
            summary[f"{sector}_{delay}dt_phase"] = phases[-1]
            summary[f"{sector}_{delay}dt_visibility"] = math.hypot(x, y)
        rates[sector], intercept = fit_rate(DELAYS_DT, phases)
        summary[f"{sector}_rate_rad_per_dt"] = rates[sector]
        summary[f"{sector}_intercept"] = intercept
        summary[f"{sector}_b_preparation_error"] = float(
            np.mean(
                [
                    b_preparation_error(distributions[member_name(sector, quadrature, delay)], sector)
                    for delay in DELAYS_DT
                    for quadrature in QUADRATURES
                ]
            )
        )
    summary.update(reconstruct(rates))
    return summary


def one_shot_standard_errors(distributions: Mapping[str, np.ndarray], step: float = 1e-6) -> dict[str, float]:
    """Delta-method standard errors at one shot per circuit; divide by sqrt(shots).

    Every circuit is an independent multinomial with covariance
    (diag(p) - p p^T) / N. Central differences give the gradient of each
    SE_KEYS output with respect to every outcome probability, the in-job
    calibration circuits included, so the error budget carries the
    assignment correction as well as the Ramsey arms.
    """
    base = {name: np.asarray(dist, dtype=float) for name, dist in distributions.items()}
    variance = dict.fromkeys(SE_KEYS, 0.0)
    for name, dist in base.items():
        gradient = np.zeros((len(SE_KEYS), len(dist)))
        for outcome in range(len(dist)):
            shifted = []
            for sign in (1.0, -1.0):
                moved = dict(base)
                moved[name] = dist.copy()
                moved[name][outcome] += sign * step
                values = point_summary(moved)
                shifted.append([values[key] for key in SE_KEYS])
            gradient[:, outcome] = (np.asarray(shifted[0]) - np.asarray(shifted[1])) / (2.0 * step)
        covariance = np.diag(dist) - np.outer(dist, dist)
        for index, key in enumerate(SE_KEYS):
            variance[key] += float(gradient[index] @ covariance @ gradient[index])
    return {f"{key}_se_one_shot": math.sqrt(max(value, 0.0)) for key, value in variance.items()}


def standard_error(summary: Mapping[str, float], key: str, shots: int) -> float:
    return summary[f"{key}_se_one_shot"] / math.sqrt(shots)


def summarize_distributions(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    summary = point_summary(distributions)
    summary.update(one_shot_standard_errors(distributions))
    return summary


def conditional_ramsey_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in circuits())
    return Group("conditional_ramsey", members, summarize_distributions)


def hamiltonian_evolution(omega_a: float, omega_b: float, zz: float, stark_conditional: float = 0.0) -> Evolution:
    """Replace each idle by exp(-i H t) of the reduced model, rates in rad per dt.

    RZ(theta) = exp(-i theta Z / 2) and RZZ(theta) = exp(-i theta Z Z / 2), so
    exp(-i H t) = RZ_A(omega_A t) RZ_B(omega_B t) RZZ(J t). stark_conditional
    adds an A detuning on the conditional arms only, a planted departure from
    one static Hamiltonian that the falsifier must see.
    """

    def evolve(circuit: QuantumCircuit, sector: str, delay: int) -> None:
        extra = stark_conditional if sector.startswith("a_given") else 0.0
        circuit.rz((omega_a + extra) * delay, 0)
        circuit.rz(omega_b * delay, 1)
        circuit.rzz(zz * delay, 0, 1)

    return evolve


def exact_distributions(evolve: Evolution) -> dict[str, np.ndarray]:
    from qiskit.quantum_info import Statevector

    return {
        name: Statevector(circuit.remove_final_measurements(inplace=False)).probabilities()
        for name, circuit, _ in circuits(evolve)
    }


def with_assignment(
    distributions: Mapping[str, np.ndarray], a_flips: tuple[float, float], b_flips: tuple[float, float]
) -> dict[str, np.ndarray]:
    """Pass every outcome law through per-qubit channels [[1 - e10, e01], [e10, 1 - e01]]."""

    def channel(e10: float, e01: float) -> np.ndarray:
        return np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])

    joint = np.kron(channel(*b_flips), channel(*a_flips))
    return {name: joint @ np.asarray(dist) for name, dist in distributions.items()}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def self_check() -> str:
    idle_laws = exact_distributions(idle)
    for name, _, ideal in circuits():
        _require(np.allclose(idle_laws[name], ideal, atol=1e-12), f"{name}: statevector law differs from its ideal")

    _require(design_rank(("even", "odd")) == 2, "the Bell-only design must have rank two")
    _require(design_rank(SECTORS) == 3, "the conditional design must have rank three")
    _require(
        all(DESIGN_ROWS[sector][2] == 0 for sector in ("even", "odd")),
        "both Bell rows must be blind to J",
    )

    dt = 4e-9
    to_rad = 2.0 * math.pi * dt
    omega_a, omega_b, zz = 30e3 * to_rad, -12e3 * to_rad, 8e3 * to_rad
    exact = summarize_distributions(exact_distributions(hamiltonian_evolution(omega_a, omega_b, zz)))
    for key, value in (("omega_a_bell", omega_a), ("omega_a_conditional", omega_a), ("omega_b", omega_b), ("zz_j", zz)):
        _require(abs(exact[key] - value) < 1e-12, f"exact recovery of {key} failed: {exact[key]} against {value}")
    _require(abs(exact["falsifier_residual"]) < 1e-12, "the static diagonal model must satisfy the falsifier")

    stark = 3e3 * to_rad
    shifted = summarize_distributions(exact_distributions(hamiltonian_evolution(omega_a, omega_b, zz, stark)))
    _require(
        abs(shifted["falsifier_residual"] + 2.0 * stark) < 1e-12,
        "a conditional-arm detuning must appear as falsifier residual -2 delta",
    )

    beyond = 1.2 * unambiguous_rate_bound()
    aliased = summarize_distributions(exact_distributions(hamiltonian_evolution(beyond, 0.0, 0.0)))
    _require(abs(aliased["a_given_b0_rate_rad_per_dt"] - beyond) > 1e-6, "a rate past the unwrap bound must alias")

    laws = exact_distributions(hamiltonian_evolution(omega_a, omega_b, zz))
    misread = with_assignment(laws, (0.04, 0.12), (0.02, 0.08))
    corrected = point_summary(misread)
    _require(abs(corrected["zz_j"] - zz) < 1e-10, "the in-job calibration must undo an asymmetric assignment")
    uncalibrated = dict(misread)
    uncalibrated.update({name: laws[name] for name in READOUT_MEMBERS})
    raw_bias = abs(point_summary(uncalibrated)["omega_a_conditional"] - omega_a)
    _require(raw_bias > 1e-7, "an asymmetric assignment must bias the uncorrected rates")

    rng = np.random.default_rng(20261015)
    shots = 1024
    propagated = summarize_distributions(laws)
    samples: dict[str, list[float]] = {"zz_j": [], "falsifier_residual": []}
    for _ in range(40):
        sampled = {
            name: rng.multinomial(shots, np.clip(law, 0.0, None) / law.sum()) / shots for name, law in laws.items()
        }
        values = point_summary(sampled)
        for key in samples:
            samples[key].append(values[key])
    for key, truth in (("zz_j", zz), ("falsifier_residual", 0.0)):
        spread = float(np.std(samples[key], ddof=1))
        predicted = standard_error(propagated, key, shots)
        _require(
            0.7 * predicted < spread < 1.4 * predicted, f"{key} spread {spread} departs from propagated {predicted}"
        )
        _require(
            abs(float(np.mean(samples[key])) - truth) < 4.0 * predicted / math.sqrt(len(samples[key])),
            f"{key} estimate is biased",
        )
    spread = standard_error(propagated, "zz_j", shots)
    return (
        f"conditional Ramsey: {len(circuits())} circuits; design rank 2 -> 3; J recovered exactly, "
        f"assignment bias {rate_hz(raw_bias, dt):.0f} Hz removed by the in-job calibration, "
        f"propagated J error {rate_hz(spread, dt):.0f} Hz at {shots} shots; "
        f"unwrap bound {rate_hz(unambiguous_rate_bound(), dt) / 1e3:.0f} kHz"
    )


if __name__ == "__main__":
    print(self_check())
