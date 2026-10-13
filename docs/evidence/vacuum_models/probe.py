"""Replay finite pair-field, rate-identifiability and programmed-bath checks."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any, TypeAlias

import numpy as np
import scipy
import sympy as sp
from numpy.typing import NDArray
from scipy.linalg import expm

Record: TypeAlias = dict[str, Any]
ComplexArray: TypeAlias = NDArray[np.complex128]
RealArray: TypeAlias = NDArray[np.float64]
ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILES = ("docs/evidence/vacuum_models/probe.py",)
SOURCE_INPUTS = (
    {"sha256": "5359c18f4f6c1e4381dc43a657033a872ccf37309f1a55addc51f03fc7f261ee", "bytes": 23807},
    {"sha256": "c090fac04fa1c40bbaa03509b7bd901e65c42d9c13d67996bab036675710924e", "bytes": 27194},
)
VERSION_KEYS = frozenset(("python", "numpy", "scipy", "sympy"))
ABSOLUTE_TOLERANCE = 1e-12
RELATIVE_TOLERANCE = 1e-10


def require(condition: bool | np.bool_, description: str) -> None:
    if not condition:
        raise RuntimeError(description)


def annihilation(cutoff: int) -> ComplexArray:
    matrix = np.zeros((cutoff, cutoff), dtype=complex)
    for occupation in range(1, cutoff):
        matrix[occupation - 1, occupation] = math.sqrt(occupation)
    return matrix


def reduced_pair(cutoff: int) -> ComplexArray:
    matrix = np.zeros((cutoff, cutoff), dtype=complex)
    for occupation in range(1, cutoff):
        matrix[occupation - 1, occupation] = occupation
    return matrix


def generator(pair: ComplexArray, phase: float) -> ComplexArray:
    return 1j * (np.exp(1j * phase) * pair.conj().T - np.exp(-1j * phase) * pair)


def max_residual(matrix: ComplexArray | RealArray) -> float:
    return float(np.max(np.abs(matrix)))


PAULIS: dict[str, ComplexArray] = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.diag([1, -1]).astype(complex),
}


def two_qubit_expansion(matrix: ComplexArray) -> dict[str, list[float]]:
    coefficients: dict[str, list[float]] = {}
    reconstructed = np.zeros_like(matrix)
    for left_label, right_label in itertools.product(PAULIS, repeat=2):
        label = left_label + right_label
        pauli = np.kron(PAULIS[left_label], PAULIS[right_label])
        coefficient = np.trace(pauli @ matrix) / 4
        if abs(coefficient) > 1e-12:
            coefficients[label] = [float(coefficient.real), float(coefficient.imag)]
            reconstructed += coefficient * pauli
    require(max_residual(reconstructed - matrix) < 1e-12, "Pauli reconstruction")
    return coefficients


def check_cutoff(cutoff: int) -> tuple[Record, list[Record]]:
    cutoff_results: list[Record] = []
    single_annihilation = annihilation(cutoff)
    full_pair = np.kron(single_annihilation, single_annihilation)
    pair = reduced_pair(cutoff)
    embedding = np.zeros((cutoff**2, cutoff), dtype=complex)
    for occupation in range(cutoff):
        embedding[occupation * cutoff + occupation, occupation] = 1
    number = np.diag(np.arange(cutoff)).astype(complex)
    number_difference = np.kron(number, np.eye(cutoff)) - np.kron(np.eye(cutoff), number)
    expected_commutator = np.eye(cutoff)
    expected_commutator[-1, -1] -= cutoff
    observed_commutator = (
        single_annihilation @ single_annihilation.conj().T - single_annihilation.conj().T @ single_annihilation
    )
    commutator_residual = max_residual(observed_commutator - expected_commutator)
    require(commutator_residual < 1e-12, "Cutoff commutator")
    cutoff_check: Record = {
        "cutoff": cutoff,
        "commutator_residual": commutator_residual,
        "trace_commutator": float(np.trace(observed_commutator).real),
        "phases": [],
    }
    vacuum = np.eye(cutoff, dtype=complex)[:, 0]
    for phase in (0.0, math.pi, 0.37):
        full_generator = generator(full_pair, phase)
        reduced_generator = generator(np.asarray(pair, dtype=np.complex128), phase)
        embedding_residual = max_residual(full_generator @ embedding - embedding @ reduced_generator)
        conservation_residual = max_residual(full_generator @ number_difference - number_difference @ full_generator)
        evolution_residual = max_residual(
            expm(-0.4j * full_generator) @ embedding - embedding @ expm(-0.4j * reduced_generator)
        )
        require(
            embedding_residual < 1e-12 and conservation_residual < 1e-12 and evolution_residual < 1e-12,
            "Invariant-sector identity",
        )
        cutoff_check["phases"].append(
            {
                "phase": phase,
                "embedding_residual": embedding_residual,
                "number_difference_conservation_residual": conservation_residual,
                "evolution_residual": evolution_residual,
            }
        )
    for strength in (0.2, 0.4, 0.6):
        state = expm(-1j * strength * generator(pair, 0.0)) @ vacuum
        reversed_state = expm(-1j * strength * generator(pair, math.pi)) @ vacuum
        pair_expectation = np.vdot(state, pair @ state)
        reversed_pair = np.vdot(reversed_state, pair @ reversed_state)
        phase_state = expm(-1j * strength * generator(pair, 0.37)) @ vacuum
        phase_expected = np.vdot(phase_state, pair @ phase_state)
        predicted_phase = np.exp(0.37j) * pair_expectation
        phase_probability_residual = max_residual(np.abs(state) ** 2 - np.abs(reversed_state) ** 2)
        phase_odd_residual = float(abs(pair_expectation + reversed_pair))
        phase_general_residual = float(abs(phase_expected - predicted_phase))
        diagonal_mixture = np.diag(np.abs(state) ** 2)
        incoherent_pair_expectation = abs(np.trace(diagonal_mixture @ pair))
        require(
            max(phase_probability_residual, phase_odd_residual, phase_general_residual, incoherent_pair_expectation)
            < 1e-12,
            "Phase/coherence controls",
        )
        infinite_pair = math.sinh(strength) * math.cosh(strength)
        cutoff_results.append(
            {
                "cutoff": cutoff,
                "r": strength,
                "finite_re_ab": float(pair_expectation.real),
                "infinite_re_ab": infinite_pair,
                "relative_pair_error": float(abs(pair_expectation - infinite_pair) / infinite_pair),
                "infinite_discarded_probability": math.tanh(strength) ** (2 * cutoff),
                "top_probability": float(abs(state[-1]) ** 2),
                "single_mode_commutator_expectation": float(1 - cutoff * abs(state[-1]) ** 2),
                "phase_probability_residual": phase_probability_residual,
                "phase_odd_residual": phase_odd_residual,
                "phase_general_residual": phase_general_residual,
            }
        )
    return cutoff_check, cutoff_results


def check_pauli_expansions() -> Record:
    pair = reduced_pair(4)
    hamiltonian = generator(pair, 0.0)
    real_pair = (pair + pair.conj().T) / 2
    imaginary_pair = (pair - pair.conj().T) / (2j)
    pauli_record = {
        "H_over_hbar_g": two_qubit_expansion(hamiltonian),
        "Re_ab": two_qubit_expansion(real_pair),
        "Im_ab": two_qubit_expansion(imaginary_pair),
        "pair_number": two_qubit_expansion(np.diag(np.arange(4)).astype(complex)),
        "occupation_and_real_pair_settings": ["ZZ", "ZX", "XX", "YY"],
    }
    expected_generator = {"IY": [2.0, 0.0], "XY": [-1.0, 0.0], "YX": [1.0, 0.0], "ZY": [-1.0, 0.0]}
    require(pauli_record["H_over_hbar_g"] == expected_generator, "Supplied Hamiltonian Pauli expansion")

    return pauli_record


def check_product_formula() -> list[Record]:
    hamiltonian = generator(reduced_pair(4), 0.0)
    expected_generator = check_pauli_expansions()["H_over_hbar_g"]
    first_order_results = []
    for strength in (0.2, 0.4):
        exact_unitary = expm(-1j * strength * hamiltonian)
        for repetitions in (1, 2, 4, 8):
            step_unitary = np.eye(4, dtype=complex)
            for label, coefficient in expected_generator.items():
                pauli = np.kron(PAULIS[label[0]], PAULIS[label[1]])
                step_unitary = expm(-1j * strength * coefficient[0] * pauli / repetitions) @ step_unitary
            approximate_unitary = np.linalg.matrix_power(step_unitary, repetitions)
            first_order_results.append(
                {
                    "r": strength,
                    "repetitions": repetitions,
                    "applied_first_to_last": list(expected_generator),
                    "operator_norm_error": float(np.linalg.norm(approximate_unitary - exact_unitary, ord=2)),
                }
            )
    return first_order_results


def thermal_and_binomial_examples() -> Record:
    planck = 6.62607015e-34
    boltzmann = 1.380649e-23
    return {
        "five_ghz_hf_over_k_kelvin": planck * 5e9 / boltzmann,
        "five_ghz_15mk_occupation": 1 / math.expm1(planck * 5e9 / (boltzmann * 0.015)),
        "five_ghz_50mk_occupation": 1 / math.expm1(planck * 5e9 / (boltzmann * 0.050)),
        "one_mhz_15mk_occupation": 1 / math.expm1(planck * 1e6 / (boltzmann * 0.015)),
        "zero_events_4096_upper_95": -math.expm1(math.log(0.05) / 4096),
    }


def check_rate_identifiability() -> Record:
    decay_rate = 10000.0
    up_rate = 500.0
    equilibrium = up_rate / (up_rate + decay_rate)
    initial_populations = (0.03, 0.97)
    times = np.array([0.0, 1e-5, 3e-5, 7e-5, 1.5e-4, 3e-4])
    readout_zero = 0.02
    readout_one = 0.04
    response_scale = 1 - readout_zero - readout_one
    offset = 0.01
    population_scale = 0.98
    alternative_readout_zero = readout_zero - response_scale * offset / population_scale
    alternative_response_scale = response_scale / population_scale
    alternative_readout_one = 1 - alternative_readout_zero - alternative_response_scale
    alternative_equilibrium = offset + population_scale * equilibrium
    observed_residuals = []
    for initial_population in initial_populations:
        population = equilibrium + (initial_population - equilibrium) * np.exp(-(up_rate + decay_rate) * times)
        observed = readout_zero + response_scale * population
        alternative_population = alternative_equilibrium + (
            offset + population_scale * initial_population - alternative_equilibrium
        ) * np.exp(-(up_rate + decay_rate) * times)
        alternative_observed = alternative_readout_zero + alternative_response_scale * alternative_population
        observed_residuals.append(max_residual(observed - alternative_observed))
    require(max(observed_residuals) < 1e-14, "Exact SPAM population affine degeneracy")
    require(min(alternative_readout_zero, alternative_readout_one) >= 0, "Physical alternative readout probabilities")
    return {
        "delay_seconds": times.tolist(),
        "same_rate_sum": up_rate + decay_rate,
        "original": {
            "equilibrium": equilibrium,
            "readout_zero": readout_zero,
            "readout_one": readout_one,
            "preparations": list(initial_populations),
        },
        "alternative": {
            "equilibrium": alternative_equilibrium,
            "readout_zero": alternative_readout_zero,
            "readout_one": alternative_readout_one,
            "preparations": [offset + population_scale * value for value in initial_populations],
        },
        "max_observed_population_residual": max(observed_residuals),
    }


def check_symbolic_models() -> Record:
    separation, hbar, lightspeed = sp.symbols("d hbar c", positive=True)
    energy_density = -(sp.pi**2) * hbar * lightspeed / (720 * separation**3)
    expected_pressure = -(sp.pi**2) * hbar * lightspeed / (240 * separation**4)
    require(sp.simplify(-sp.diff(energy_density, separation) - expected_pressure) == 0, "Ideal Casimir derivative")
    parameter, crossing, slope, regulator, reference_frequency = sp.symbols(
        "lambda lambda_star a epsilon omega_star", real=True
    )
    mode_energy = hbar * reference_frequency * sp.sqrt(regulator**2 + slope**2 * (parameter - crossing) ** 2) / 2
    curvature = sp.simplify(sp.diff(mode_energy, parameter, 2).subs(parameter, crossing))
    positive_regulator = sp.symbols("epsilon_positive", positive=True)
    require(
        sp.simplify(
            curvature.subs(regulator, positive_regulator)
            - hbar * reference_frequency * slope**2 / (2 * positive_regulator)
        )
        == 0,
        "Regularized oscillator susceptibility",
    )
    return {
        "ideal_Casimir_pressure_derivative": "exact",
        "regularized_mode_crossing_curvature": str(curvature),
        "length_chain_rule": "F_d = -(d lambda/d d) partial_lambda E_0",
    }


def check_collision_model() -> tuple[Record, Record]:
    bath_population = 0.2
    pure_bath = np.array([math.sqrt(1 - bath_population), math.sqrt(bath_population)])
    coherent_bath = np.outer(pure_bath, pure_bath)
    thermal_bath = np.diag([1 - bath_population, bath_population])
    mixture_record = {
        "p": bath_population,
        "coherent_off_diagonal": float(coherent_bath[0, 1]),
        "thermal_off_diagonal": float(thermal_bath[0, 1]),
    }

    exchange_angle = 0.3
    exchange_generator = (np.kron(PAULIS["X"], PAULIS["X"]) + np.kron(PAULIS["Y"], PAULIS["Y"])) / 2
    exchange_unitary = expm(-1j * exchange_angle * exchange_generator)
    collision_results = []
    for system_population in (0.0, 0.3, 1.0):
        system_density = np.diag([1 - system_population, system_population])
        joint_density = np.kron(system_density, thermal_bath)
        evolved_density = exchange_unitary @ joint_density @ exchange_unitary.conj().T
        system_after = np.trace(evolved_density.reshape(2, 2, 2, 2), axis1=1, axis2=3)
        expected_population = (
            system_population * math.cos(exchange_angle) ** 2 + bath_population * math.sin(exchange_angle) ** 2
        )
        require(abs(system_after[1, 1] - expected_population) < 1e-12, "Thermal collision population law")
        require(abs(system_after[0, 1]) < 1e-12, "Thermal collision coherence")
        collision_results.append(
            {
                "system_population_before": system_population,
                "system_population_after": float(system_after[1, 1].real),
                "expected_population": expected_population,
            }
        )
    ground_system = np.diag([1, 0])
    pure_joint = np.kron(ground_system, coherent_bath)
    pure_after = exchange_unitary @ pure_joint @ exchange_unitary.conj().T
    pure_system_after = np.trace(pure_after.reshape(2, 2, 2, 2), axis1=1, axis2=3)
    collision_record = {
        "exchange_angle": exchange_angle,
        "population_law": "p_system_next = cos(theta)^2 p_system + sin(theta)^2 p_bath",
        "thermal_results": collision_results,
        "pure_bath_induced_system_coherence_magnitude": float(abs(pure_system_after[0, 1])),
    }

    return mixture_record, collision_record


def source_hashes() -> dict[str, str]:
    return {filename: hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() for filename in SOURCE_FILES}


def build_record() -> Record:
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    require(Path(parallel.__file__).resolve() == ROOT / "gororoba_quantum/parallel.py", "Unexpected pool module")
    before = source_hashes()
    cutoff_checks = parallel.ordered_map(check_cutoff, (4, 8), min_items=2)
    mixture, collision = check_collision_model()
    record: Record = {
        "schema_version": 1,
        "boundary": (
            "Finite CPU model checks; hardware, physical coupling and infinite-cutoff convergence "
            "require separate evidence"
        ),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sympy": sp.__version__,
        "inputs": [dict(identity) for identity in SOURCE_INPUTS],
        "input_role": (
            "Provenance identities of the two supplied proposals; equations are explicit in probe.py "
            "and prose bytes are not parsed"
        ),
        "historical_audit": {
            "probe_sha256": "22c1c130a42440074b66aa93f990e0920ff91e08c7b04e9bb63df718d5a834a5",
            "result_sha256": "6147433302a506c33f5a9c9367b7f67b6d22d2398f82577a179bb503cdf7207b",
        },
        "invariant_sector_checks": [row[0] for row in cutoff_checks],
        "cutoff_results": [result for row in cutoff_checks for result in row[1]],
        "q1q0_paulis": check_pauli_expansions(),
        "first_order_product_formula": check_product_formula(),
        "thermal_and_binomial_examples": thermal_and_binomial_examples(),
        "spam_identifiability_counterexample": check_rate_identifiability(),
        "symbolic_checks": check_symbolic_models(),
        "bath_mixture_correction": mixture,
        "collision_model": collision,
        "status": "CPU checks passed",
    }
    require(source_hashes() == before, "Replay source changed during computation")
    return record


def compare_records(observed: Any, retained: Any, location: str = "record") -> None:
    """Check structure and categories exactly; compare finite floats within tolerance."""
    require(type(observed) is type(retained), f"{location}: value type differs")
    if isinstance(observed, dict):
        require(observed.keys() == retained.keys(), f"{location}: keys differ")
        for key, value in observed.items():
            compare_records(value, retained[key], f"{location}.{key}")
    elif isinstance(observed, list):
        require(len(observed) == len(retained), f"{location}: length differs")
        for index, (value, expected) in enumerate(zip(observed, retained, strict=True)):
            compare_records(value, expected, f"{location}[{index}]")
    elif isinstance(observed, float):
        require(math.isfinite(observed) and math.isfinite(retained), f"{location}: nonfinite value")
        require(
            math.isclose(observed, retained, rel_tol=RELATIVE_TOLERANCE, abs_tol=ABSOLUTE_TOLERANCE),
            f"{location}: numeric result differs ({observed!r}, {retained!r})",
        )
    else:
        require(observed == retained, f"{location}: categorical result differs")


def check_comparator() -> None:
    """Reject corrupted evidence and retain tolerance for floating point replay."""
    compare_records({"value": [1.0, "exact", 4]}, {"value": [1.0 + 1e-13, "exact", 4]})
    for observed, retained in (
        ({"value": 1.0}, {"value": 1.01}),
        ({"status": "passed"}, {"status": "failed"}),
        ({"cutoff": 4}, {"cutoff": 8}),
        ({"value": 1.0}, {"value": 1}),
        ({"value": 1.0}, {"value": True}),
        ({"value": float("nan")}, {"value": float("nan")}),
        ({"value": float("inf")}, {"value": float("inf")}),
        ({"value": 1.0}, {"value": 1.0, "extra": 2}),
        ([1.0], [1.0, 2.0]),
    ):
        try:
            compare_records(observed, retained)
        except RuntimeError:
            continue
        raise RuntimeError("Comparator accepted a corrupted fixture")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the adjacent retained result.json")
    arguments = parser.parse_args()
    check_comparator()
    record = build_record()
    if arguments.check:
        retained = json.loads(Path(__file__).with_name("result.json").read_text())
        require(isinstance(retained, dict), "Retained record must be an object")
        versions = {key: {"observed": record[key], "retained": retained.get(key)} for key in sorted(VERSION_KEYS)}
        for key in VERSION_KEYS:
            require(isinstance(retained.get(key), str) and bool(retained[key]), f"Missing retained version: {key}")
        compare_records(
            {key: value for key, value in record.items() if key not in VERSION_KEYS},
            {key: value for key, value in retained.items() if key not in VERSION_KEYS},
        )
        print(json.dumps({"status": "CPU replay matches retained evidence", "versions": versions}, sort_keys=True))
    else:
        print(json.dumps(record, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
