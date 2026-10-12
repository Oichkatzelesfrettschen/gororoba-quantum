"""Matched four-qubit LCU norm experiments along the certified rank path.

Each sector uses a single parametrized circuit for every probe, parameter,
and isolated reference. Binding follows compilation, so conditional state
preparation and selector readout retain the same routed gate topology.
Scientific contrasts compare conditions within one sector's physical patch.
Cross-sector differences carry layout effects and supply no causal comparison.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

import parallel
from cd_core import cd_sign
from experiment_optimizer import ObservableContract, ObservableTerm
from experiments import Group, Member, tvd
from rank_attachments import COSET_SUBGROUP, path_coefficients, path_matrix
from select_lcu import phase_oracle_from_truth_table

PARAMETERS = (Fraction(0), Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2))
SUPPORT = (1, 10, 18, 25)
SCIENCE_ROWS = 20
TOTAL_ROWS = 36
SELECTOR_SUCCESS = (1.0, 0.0, 0.0, 0.0)
SOURCE_FILES = (
    "rank_sector_experiments.py",
    "rank_sector_contracts.py",
    "rank_attachments.py",
    "rank_charts.py",
    "rank_polynomials.py",
    "rank_path_topology.py",
    "cd_core.py",
    "select_lcu.py",
    "boolean_anf.py",
)


@dataclass(frozen=True)
class SectorProbe:
    name: str
    coordinates: tuple[int, int, int, int]


def _sector(sector: int) -> int:
    if type(sector) is not int or not 0 <= sector < 8:
        raise ValueError("sector must be an integer from zero through seven")
    return sector


def _parameter(parameter: int | Fraction) -> Fraction:
    if isinstance(parameter, bool) or not isinstance(parameter, int | Fraction):
        raise ValueError("parameter must be an exact integer or Fraction")
    value = Fraction(parameter)
    if not 0 <= value <= 2:
        raise ValueError("rank-sector experiment parameter must lie in [0, 2]")
    return value


def sector_probes(sector: int) -> tuple[SectorProbe, ...]:
    """Fixed real probes, normalized by their Euclidean norm when prepared."""
    _sector(sector)
    if sector < 4:
        endpoint_one = (0, 1 if sector % 2 == 0 else -1, 0, 1)
        endpoint_two = ((0, -1, 1, 0), (1, -1, 1, 1), (1, 1, -1, 1), (1, 0, 0, 1))[sector]
        return (
            SectorProbe("basis", (1, 0, 0, 0)),
            SectorProbe("kernel_at_one", endpoint_one),
            SectorProbe("kernel_at_two", endpoint_two),
            SectorProbe("bright_at_one", (0, -endpoint_one[1], 0, 1)),
        )
    frame = (
        SectorProbe("persistent_kernel", (1, -1, -1, -1)),
        SectorProbe("pulse_zero_two", (1, -1, 1, 1)),
        SectorProbe("pulse_one_two", (1, 1, -1, 1)),
        SectorProbe("bright", (1, 1, 1, -1)),
    )
    if sector % 2 == 0:
        return frame
    return tuple(
        SectorProbe(
            probe.name, (probe.coordinates[0], -probe.coordinates[1], -probe.coordinates[2], probe.coordinates[3])
        )
        for probe in frame
    )


def _probe(sector: int, probe_name: str) -> SectorProbe:
    for probe in sector_probes(sector):
        if probe.name == probe_name:
            return probe
    raise ValueError(f"unsupported probe {probe_name!r} in sector {sector}")


def member_name(sector: int, probe_name: str, parameter: int | Fraction, *, reference: bool = False) -> str:
    _probe(sector, probe_name)
    value = _parameter(parameter)
    if type(reference) is not bool:
        raise ValueError("reference flag must be Boolean")
    suffix = "_reference" if reference else ""
    return f"rank_sector_{sector}_{probe_name}_t{value.numerator}d{value.denominator}{suffix}"


def sector_coefficients(parameter: int | Fraction) -> tuple[Fraction, ...]:
    coefficients = path_coefficients(_parameter(parameter))
    return tuple(Fraction(int(coefficients[index].p), int(coefficients[index].q)) for index in SUPPORT)


def sector_alpha(parameter: int | Fraction) -> Fraction:
    return sum((abs(coefficient) for coefficient in sector_coefficients(parameter)), Fraction(0))


def sector_terms(sector: int) -> tuple[np.ndarray, ...]:
    """Four signed-permutation matrices in the input/output coset coordinates."""
    _sector(sector)
    matrices = []
    for support_index in SUPPORT:
        matrix = np.zeros((4, 4), dtype=int)
        for column, input_offset in enumerate(COSET_SUBGROUP):
            input_basis = sector ^ input_offset
            output_basis = support_index ^ input_basis
            output_offset = output_basis ^ 1 ^ sector
            row = COSET_SUBGROUP.index(output_offset)
            matrix[row, column] = cd_sign(32, support_index, input_basis)
        matrices.append(matrix)
    return tuple(matrices)


def preparation_angles(amplitudes: tuple[float, ...]) -> tuple[float, float, float]:
    """Binary-tree real state preparation, including signed amplitudes."""
    if len(amplitudes) != 4 or any(not math.isfinite(value) for value in amplitudes):
        raise ValueError("two-qubit preparation requires four finite real amplitudes")
    lower_norm = math.hypot(amplitudes[0], amplitudes[1])
    upper_norm = math.hypot(amplitudes[2], amplitudes[3])
    if math.hypot(lower_norm, upper_norm) == 0:
        raise ValueError("state preparation requires a nonzero vector")
    parent = 2 * math.atan2(upper_norm, lower_norm)
    lower = 2 * math.atan2(amplitudes[1], amplitudes[0]) if lower_norm else 0.0
    upper = 2 * math.atan2(amplitudes[3], amplitudes[2]) if upper_norm else 0.0
    return parent, (lower + upper) / 2, (lower - upper) / 2


def preparation_matrix(angles: tuple[float, float, float]) -> np.ndarray:
    """Independent real matrix of the binary-tree preparation convention."""
    parent, average, difference = angles

    def rotation(angle: float) -> np.ndarray:
        cosine, sine = math.cos(angle / 2), math.sin(angle / 2)
        return np.asarray(((cosine, -sine), (sine, cosine)))

    conditional = np.zeros((4, 4))
    conditional[:2, :2] = rotation(average + difference)
    conditional[2:, 2:] = rotation(average - difference)
    return conditional @ np.kron(rotation(parent), np.eye(2))


def _preparation_template(prefix: str) -> tuple[QuantumCircuit, tuple[Parameter, ...]]:
    angles = tuple(Parameter(f"{prefix}_{name}") for name in ("parent", "average", "difference"))
    circuit = QuantumCircuit(2)
    circuit.ry(angles[0], 1)
    circuit.ry(angles[1], 0)
    circuit.cx(1, 0)
    circuit.ry(angles[2], 0)
    circuit.cx(1, 0)
    return circuit, angles


def sector_template(sector: int) -> tuple[QuantumCircuit, tuple[Parameter, ...]]:
    """One circuit object supplies all coefficient/probe bindings in a sector."""
    _sector(sector)
    probe_prepare, probe_angles = _preparation_template("probe")
    selector_prepare, selector_angles = _preparation_template("selector")
    coefficient_phase = Parameter("coefficient_phase")
    circuit = QuantumCircuit(4, 2, name=f"rank_sector_{sector}")
    circuit.compose(probe_prepare, (0, 1), inplace=True)
    circuit.compose(selector_prepare, (2, 3), inplace=True)
    circuit.cp(coefficient_phase, 2, 3)
    truth = [
        int(cd_sign(32, support_index, sector ^ input_offset) < 0)
        for support_index in SUPPORT
        for input_offset in COSET_SUBGROUP
    ]
    circuit.compose(phase_oracle_from_truth_table(truth), inplace=True)
    circuit.cx(2, 0)
    circuit.cx(3, 1)
    circuit.compose(selector_prepare.inverse(), (2, 3), inplace=True)
    circuit.measure((2, 3), (0, 1))
    return circuit, (*probe_angles, *selector_angles, coefficient_phase)


def sector_binding(
    sector: int, probe_name: str, parameter: int | Fraction, parameters: tuple[Parameter, ...]
) -> dict[Parameter, float]:
    probe = _probe(sector, probe_name)
    coefficients = sector_coefficients(parameter)
    alpha = sector_alpha(parameter)
    if len(parameters) != 7 or len(set(parameters)) != 7:
        raise ValueError("rank-sector binding requires the seven distinct template parameters")
    probe_angles = preparation_angles(tuple(float(value) for value in probe.coordinates))
    selector_angles = preparation_angles(tuple(math.sqrt(float(abs(value) / alpha)) for value in coefficients))
    phase = math.pi if coefficients[3] < 0 else 0.0
    return dict(zip(parameters, (*probe_angles, *selector_angles, phase), strict=True))


def exact_success_probability(sector: int, probe_name: str, parameter: int | Fraction) -> Fraction:
    """Predict the selected norm from the complete exact 32-dimensional matrix."""
    probe = _probe(sector, probe_name)
    value = _parameter(parameter)
    columns = [sector ^ offset for offset in COSET_SUBGROUP]
    matrix = path_matrix(value)
    norm_squared = sum(coordinate**2 for coordinate in probe.coordinates)
    image = [
        sum(matrix[row, column] * coordinate for column, coordinate in zip(columns, probe.coordinates, strict=True))
        for row in range(32)
    ]
    numerator = sum(coordinate**2 for coordinate in image)
    exact_norm = Fraction(int(numerator.p), int(numerator.q))
    probability = exact_norm / (norm_squared * sector_alpha(value) ** 2)
    if not 0 <= probability <= 1:
        raise RuntimeError("exact LCU probability escaped [0,1]")
    return probability


def selector_distribution(sector: int, probe_name: str, parameter: int | Fraction) -> np.ndarray:
    """Compute all selector outcomes using independent dense real matrices."""
    probe = _probe(sector, probe_name)
    coefficients = sector_coefficients(parameter)
    alpha = sector_alpha(parameter)
    amplitudes = tuple(math.sqrt(float(abs(value) / alpha)) for value in coefficients)
    prepare = preparation_matrix(preparation_angles(amplitudes))
    normalized_probe = np.asarray(probe.coordinates, dtype=float) / math.sqrt(
        sum(value**2 for value in probe.coordinates)
    )
    selected = np.asarray(
        [
            amplitude * (-1 if coefficient < 0 else 1) * (matrix @ normalized_probe)
            for amplitude, coefficient, matrix in zip(amplitudes, coefficients, sector_terms(sector), strict=True)
        ]
    )
    output = prepare.T @ selected
    distribution = np.sum(output**2, axis=1)
    exact = exact_success_probability(sector, probe_name, parameter)
    if abs(float(distribution[0]) - float(exact)) > 1e-12 or abs(float(np.sum(distribution)) - 1) > 1e-12:
        raise RuntimeError("selector law disagrees with the exact full-dimensional selected norm")
    return distribution


def reference_probes(sector: int) -> tuple[str, str]:
    _sector(sector)
    return ("kernel_at_one", "bright_at_one") if sector < 4 else ("persistent_kernel", "bright")


@dataclass(frozen=True)
class SectorSummary:
    sector: int
    members: tuple[Member, ...]

    def __call__(self, distributions: dict[str, np.ndarray]) -> dict[str, float]:
        result: dict[str, float] = {}
        for member in self.members:
            distribution = distributions[member.name]
            result[member.name + "_success"] = float(distribution[0])
            result[member.name + "_tvd"] = tvd(distribution, member.ideal)
        for probe_name in reference_probes(self.sector):
            packed = member_name(self.sector, probe_name, 1)
            reference = member_name(self.sector, probe_name, 1, reference=True)
            result[packed + "_packed_minus_reference"] = float(distributions[packed][0] - distributions[reference][0])
        return result


def _sector_group(sector: int) -> Group:
    template, parameters = sector_template(sector)
    members: list[Member] = []
    for probe in sector_probes(sector):
        for parameter in PARAMETERS:
            members.append(
                Member(
                    member_name(sector, probe.name, parameter),
                    template,
                    selector_distribution(sector, probe.name, parameter),
                    binding=sector_binding(sector, probe.name, parameter, parameters),
                    weights=np.asarray(SELECTOR_SUCCESS),
                )
            )
    for probe_name in reference_probes(sector):
        members.append(
            Member(
                member_name(sector, probe_name, 1, reference=True),
                template,
                selector_distribution(sector, probe_name, 1),
                binding=sector_binding(sector, probe_name, 1, parameters),
                weights=np.asarray(SELECTOR_SUCCESS),
            )
        )

    return Group(
        f"rank_sector_{sector}",
        tuple(members),
        SectorSummary(sector, tuple(members)),
        rate_keys=frozenset(member.name + "_success" for member in members),
        execution_rows=(*range(SCIENCE_ROWS), SCIENCE_ROWS + 2 * sector, SCIENCE_ROWS + 2 * sector + 1),
    )


def sector_groups() -> list[Group]:
    """Eight fixed patches, twenty packed rows, and sixteen isolated rows."""
    return parallel.ordered_map(_sector_group, list(range(8)), min_items=2)


def sector_contracts(precision: float, alpha: float, power: float) -> tuple[ObservableContract, ...]:
    """Simultaneous means, matched packing residuals, and directional controls."""
    for name, value in (("precision", precision), ("alpha", alpha), ("power", power)):
        if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be positive and finite")
    if alpha >= 1 or power >= 1:
        raise ValueError("alpha and power must lie in (0,1)")
    specifications: list[tuple[str, tuple[ObservableTerm, ...], bool]] = []
    for sector in range(8):
        for probe in sector_probes(sector):
            for parameter in PARAMETERS:
                name = member_name(sector, probe.name, parameter)
                specifications.append((name + "_success", (ObservableTerm(name, SELECTOR_SUCCESS),), False))
        dark, bright = reference_probes(sector)
        specifications.append(
            (
                f"rank_sector_{sector}_bright_minus_dark_at_one",
                (
                    ObservableTerm(member_name(sector, bright, 1), SELECTOR_SUCCESS),
                    ObservableTerm(member_name(sector, dark, 1), SELECTOR_SUCCESS, sign=-1),
                ),
                True,
            )
        )
        for probe_name in (dark, bright):
            packed = member_name(sector, probe_name, 1)
            reference = member_name(sector, probe_name, 1, reference=True)
            specifications.append(
                (
                    packed + "_packed_minus_reference",
                    (ObservableTerm(packed, SELECTOR_SUCCESS), ObservableTerm(reference, SELECTOR_SUCCESS, sign=-1)),
                    False,
                )
            )
        if sector >= 4:
            for probe_name, first, second in (
                ("pulse_zero_two", Fraction(1, 2), Fraction(0)),
                ("pulse_one_two", Fraction(1, 2), Fraction(1)),
                ("pulse_zero_two", Fraction(3, 2), Fraction(2)),
            ):
                positive = member_name(sector, probe_name, first)
                negative = member_name(sector, probe_name, second)
                specifications.append(
                    (
                        positive + "_minus_" + negative,
                        (
                            ObservableTerm(positive, SELECTOR_SUCCESS),
                            ObservableTerm(negative, SELECTOR_SUCCESS, sign=-1),
                        ),
                        True,
                    )
                )
    per_endpoint_alpha = alpha / len(specifications)
    return tuple(
        ObservableContract(
            name,
            terms,
            minimum_effect=0.0 if directional else None,
            precision_half_width=None if directional else precision,
            alpha=per_endpoint_alpha,
            power=power,
        )
        for name, terms, directional in specifications
    )


def sector_configuration() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    return {
        "name": "rank-sector",
        "schema": "rank-sector-four-qubit-lcu-v1",
        "dimension": 32,
        "logical_qubits_per_lane": 4,
        "logical_qubits": 32,
        "lanes": 8,
        "execution_row_count": TOTAL_ROWS,
        "science_rows": SCIENCE_ROWS,
        "isolated_rows": TOTAL_ROWS - SCIENCE_ROWS,
        "parameters": [str(parameter) for parameter in PARAMETERS],
        "support": list(SUPPORT),
        "coset_subgroup": list(COSET_SUBGROUP),
        "input_index": "sector XOR subgroup[data]",
        "output_index": "1 XOR sector XOR subgroup[data]",
        "alpha": "sum(abs(a_s(t))); 2 for 0<=t<=1, t^2-t+2 for 1<=t<=2",
        "observable": "P(selector=00)=||L_a(t) probe||^2/(alpha(t)^2 ||probe||^2)",
        "sectors": [
            {
                "sector": sector,
                "probes": [
                    {"name": probe.name, "coordinates": list(probe.coordinates)} for probe in sector_probes(sector)
                ],
                "reference_probes_at_one": list(reference_probes(sector)),
                "execution_rows": [*range(SCIENCE_ROWS), SCIENCE_ROWS + 2 * sector, SCIENCE_ROWS + 2 * sector + 1],
                "exact_probabilities": [
                    {
                        "member": member_name(sector, probe.name, parameter),
                        "probability": str(exact_success_probability(sector, probe.name, parameter)),
                    }
                    for probe in sector_probes(sector)
                    for parameter in PARAMETERS
                ],
            }
            for sector in range(8)
        ],
        "source_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in SOURCE_FILES},
        "routing_contract": "all members of each sector bind one parametrized template after compilation",
        "comparison_scope": "within-sector conditions and same-patch packed-minus-isolated residuals",
        "cross_sector_scope": (
            "sector and physical patch remain confounded; cross-sector causal effects are outside the contract"
        ),
        "inference_boundary": (
            "finite noisy norm predictions with declared precision; "
            "exact rank and topology remain mathematical certificates"
        ),
    }
