"""Crossed tile x template design for the Kingston rank-sector weak lane.

The rank-sector endpoint decomposition located most of Kingston's off-model
endpoints in sector 4, which ran on physical qubits 0-3, and the corner
baseline then measured a readout fault on qubits 0 and 1. Neither
acquisition separates the physical tile from the circuit template: sector 4
always ran on that tile. This campaign crosses

    {affected template (sector 4), reference template (sector 7)}
    x {candidate weak tile (Kingston 0-3), reference tile (Kingston 104-107)},

the reference tile being where sector 7 ran in the same acquisition. Both
tiles are four-qubit lines, and sectors 4 and 7 have identical exact
selector-success laws on all twenty science members, so a fault that acts
through the outcome channel of a tile moves both templates equally and the
additive model y = mu + L_template + T_tile + (LT) holds for it.

One group carries the twenty science members of both templates. Run with
only the two tiles placeable and two replicas, every PUB row executes one
member on both tiles in the same shots, so each tile sees both templates
under one calibration. The tiles were chosen after seeing the data, so only
this prospective acquisition can confirm a tile effect.

Response per (template, tile): the endpoint error
y = (mean over ideal-one members of (1 - p) + mean over ideal-zero members of p) / 2,
linear in the selector-success probabilities p, so its standard error
follows from the binomial variances. The contrasts are the tile effect T
(weak minus reference tile, averaged over templates), the template effect L
(sector 4 minus sector 7, averaged over tiles) and the interaction
I = (y_w4 - y_w7) - (y_r4 - y_r7).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from fractions import Fraction

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from experiments import Group, Member
from rank_sector_experiments import (
    PARAMETERS,
    SELECTOR_SUCCESS,
    exact_success_probability,
    member_name,
    sector_binding,
    sector_probes,
    sector_template,
    selector_distribution,
)

AFFECTED_SECTOR = 4
REFERENCE_SECTOR = 7
TEMPLATES = (AFFECTED_SECTOR, REFERENCE_SECTOR)
BACKEND = "ibm_kingston"
WEAK_TILE = (0, 1, 2, 3)
REFERENCE_TILE = (104, 105, 106, 107)
# Three contrasts at family-wise 0.05, two-sided: z = Phi^-1(1 - 0.05 / 6).
BONFERRONI_Z = 2.394

Fault = Callable[[int, QuantumCircuit], None]


def science_members(sector: int) -> tuple[tuple[str, str, Fraction], ...]:
    return tuple(
        (member_name(sector, probe.name, parameter), probe.name, Fraction(parameter))
        for probe in sector_probes(sector)
        for parameter in PARAMETERS
    )


def ideal_success(sector: int) -> dict[str, Fraction]:
    return {
        name: exact_success_probability(sector, probe, parameter) for name, probe, parameter in science_members(sector)
    }


def endpoint_members(sector: int) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Members whose exact success is one, and those whose exact success is zero."""
    law = ideal_success(sector)
    return (
        tuple(name for name, value in law.items() if value == 1),
        tuple(name for name, value in law.items() if value == 0),
    )


def crossed_group() -> Group:
    members: list[Member] = []
    for sector in TEMPLATES:
        template, parameters = sector_template(sector)
        for name, probe, parameter in science_members(sector):
            members.append(
                Member(
                    name,
                    template,
                    selector_distribution(sector, probe, parameter),
                    binding=sector_binding(sector, probe, parameter, parameters),
                    weights=np.asarray(SELECTOR_SUCCESS),
                )
            )
    return Group(
        "crossed_tile_template",
        tuple(members),
        summarize_tile,
        rate_keys=frozenset(f"{member.name}_success" for member in members),
    )


def endpoint_error(successes: Mapping[str, float], sector: int) -> tuple[float, float]:
    """The endpoint error y and its standard error at one shot per circuit."""
    bright, dark = endpoint_members(sector)
    value = (
        sum(1.0 - successes[name] for name in bright) / len(bright) + sum(successes[name] for name in dark) / len(dark)
    ) / 2.0
    variance = (
        sum(successes[name] * (1.0 - successes[name]) for name in bright) / len(bright) ** 2
        + sum(successes[name] * (1.0 - successes[name]) for name in dark) / len(dark) ** 2
    ) / 4.0
    return value, math.sqrt(variance)


def summarize_tile(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    """One tile's per-member success, both endpoint errors and the within-tile template difference."""
    successes = {name: float(np.asarray(dist)[0]) for name, dist in distributions.items()}
    summary = {f"{name}_success": value for name, value in successes.items()}
    errors = {}
    for sector in TEMPLATES:
        value, se = endpoint_error(successes, sector)
        errors[sector] = (value, se)
        summary[f"sector_{sector}_endpoint_error"] = value
        summary[f"sector_{sector}_endpoint_error_se_one_shot"] = se
    summary["template_difference"] = errors[AFFECTED_SECTOR][0] - errors[REFERENCE_SECTOR][0]
    summary["template_difference_se_one_shot"] = math.hypot(errors[AFFECTED_SECTOR][1], errors[REFERENCE_SECTOR][1])
    return summary


def crossed_contrasts(weak: Mapping[str, float], reference: Mapping[str, float], shots: int) -> dict[str, float]:
    """Tile, template and interaction contrasts with Bonferroni intervals at the given shots."""
    y = {
        (tile, sector): summary[f"sector_{sector}_endpoint_error"]
        for tile, summary in (("weak", weak), ("reference", reference))
        for sector in TEMPLATES
    }
    se = {
        (tile, sector): summary[f"sector_{sector}_endpoint_error_se_one_shot"] / math.sqrt(shots)
        for tile, summary in (("weak", weak), ("reference", reference))
        for sector in TEMPLATES
    }
    a, r = AFFECTED_SECTOR, REFERENCE_SECTOR
    pooled = math.sqrt(sum(value**2 for value in se.values()))
    contrasts = {
        "tile_effect": (y["weak", a] + y["weak", r] - y["reference", a] - y["reference", r]) / 2.0,
        "template_effect": (y["weak", a] + y["reference", a] - y["weak", r] - y["reference", r]) / 2.0,
        "interaction": (y["weak", a] - y["weak", r]) - (y["reference", a] - y["reference", r]),
    }
    errors = {"tile_effect": pooled / 2.0, "template_effect": pooled / 2.0, "interaction": pooled}
    out: dict[str, float] = {}
    for key, value in contrasts.items():
        out[key] = value
        out[f"{key}_lower"] = value - BONFERRONI_Z * errors[key]
        out[f"{key}_upper"] = value + BONFERRONI_Z * errors[key]
    return out


def member_laws(sector: int, fault: Fault | None = None) -> dict[str, np.ndarray]:
    """Selector outcome laws of a template's science members, optionally with a planted circuit fault."""
    template, parameters = sector_template(sector)
    measured = [
        template.find_bit(instruction.qubits[0]).index
        for instruction in template.data
        if instruction.operation.name == "measure"
    ]
    laws = {}
    for name, probe, parameter in science_members(sector):
        bound = template.assign_parameters(sector_binding(sector, probe, parameter, parameters))
        unitary = bound.remove_final_measurements(inplace=False)
        if fault is not None:
            fault(sector, unitary)
        laws[name] = Statevector(unitary).probabilities(measured)
    return laws


def selector_channel(laws: Mapping[str, np.ndarray], e10: float, e01: float) -> dict[str, np.ndarray]:
    """Pass both selector bits through [[1 - e10, e01], [e10, 1 - e01]], a tile readout fault."""
    single = np.array([[1.0 - e10, e01], [e10, 1.0 - e01]])
    joint = np.kron(single, single)
    return {name: joint @ law for name, law in laws.items()}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def self_check() -> str:
    laws = {sector: ideal_success(sector) for sector in TEMPLATES}
    _require(
        sorted(laws[AFFECTED_SECTOR].values()) == sorted(laws[REFERENCE_SECTOR].values())
        and [
            laws[AFFECTED_SECTOR][member_name(AFFECTED_SECTOR, p.name, t)]
            for p in sector_probes(AFFECTED_SECTOR)
            for t in PARAMETERS
        ]
        == [
            laws[REFERENCE_SECTOR][member_name(REFERENCE_SECTOR, p.name, t)]
            for p in sector_probes(REFERENCE_SECTOR)
            for t in PARAMETERS
        ],
        "the two templates must share every exact selector-success law",
    )
    group = crossed_group()
    _require(len(group.members) == 40, "the crossed group carries twenty science members per template")
    ideal = {sector: member_laws(sector) for sector in TEMPLATES}
    for sector in TEMPLATES:
        for name, law in ideal[sector].items():
            _require(abs(float(law[0]) - float(laws[sector][name])) < 1e-12, f"{name}: circuit law differs from exact")

    def tile(faulted: dict[int, dict[str, np.ndarray]]) -> dict[str, float]:
        merged = {name: law for sector in TEMPLATES for name, law in faulted[sector].items()}
        return summarize_tile(merged)

    clean = tile(ideal)
    _require(all(abs(clean[f"sector_{s}_endpoint_error"]) < 1e-12 for s in TEMPLATES), "ideal endpoint error is zero")

    # The corner baseline's qubit 0 flips, applied to both selector bits of the weak tile.
    readout = {sector: selector_channel(ideal[sector], 0.388, 0.144) for sector in TEMPLATES}
    tile_fault = crossed_contrasts(tile(readout), clean, shots=512)
    _require(tile_fault["tile_effect_lower"] > 0.0, "a weak-tile readout fault must resolve a tile effect")
    _require(
        abs(tile_fault["template_effect"]) < 1e-12 and abs(tile_fault["interaction"]) < 1e-12,
        "a channel fault must leave L and I at zero",
    )

    def over_rotation(sector: int, circuit: QuantumCircuit) -> None:
        if sector == AFFECTED_SECTOR:
            circuit.ry(0.6, 2)

    rotated = {sector: member_laws(sector, over_rotation) for sector in TEMPLATES}
    template_fault = crossed_contrasts(tile(rotated), tile(rotated), shots=512)
    _require(
        template_fault["template_effect_lower"] > 0.0, "a template fault on both tiles must resolve a template effect"
    )
    _require(abs(template_fault["tile_effect"]) < 1e-12, "a template fault on both tiles leaves T at zero")
    both = crossed_contrasts(tile(rotated), clean, shots=512)
    _require(both["interaction_lower"] > 0.0, "a template fault on the weak tile only must resolve an interaction")
    return (
        f"crossed tile x template: {len(group.members)} members, matched exact laws; readout fault T = "
        f"{tile_fault['tile_effect']:.3f} with L = I = 0; template fault L = {template_fault['template_effect']:.3f}; "
        f"weak-tile-only template fault I = {both['interaction']:.3f}"
    )


if __name__ == "__main__":
    print(self_check())
