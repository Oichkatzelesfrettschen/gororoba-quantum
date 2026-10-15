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
linear in the selector-success probabilities p. The contrasts are the tile
effect T (weak minus reference tile, averaged over templates), the template
effect L (sector 4 minus sector 7, averaged over tiles) and the interaction
I = (y_w4 - y_w7) - (y_r4 - y_r7). Their intervals come from Clopper-Pearson
bounds on every (member, tile) success count, Bonferroni-split over all 80
cells and carried through the linear contrasts by interval arithmetic: the
bounds hold simultaneously for every contrast, need no independence between
the tiles, which share shots, and keep a positive width when a cell observes
no error.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.stats import beta

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
FAMILY_ALPHA = 0.05

Fault = Callable[[int, QuantumCircuit], None]


def science_members(sector: int) -> tuple[tuple[str, str, Fraction], ...]:
    return tuple(
        (member_name(sector, probe.name, parameter), probe.name, Fraction(parameter))
        for probe in sector_probes(sector)
        for parameter in PARAMETERS
    )


@cache
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


def endpoint_weights(sector: int) -> dict[str, float]:
    """Coefficients of y on each member's success p: y = offset + sum w p."""
    bright, dark = endpoint_members(sector)
    weights = dict.fromkeys(bright, -0.5 / len(bright))
    weights.update(dict.fromkeys(dark, 0.5 / len(dark)))
    return weights


def endpoint_error(successes: Mapping[str, float], sector: int) -> float:
    """y = (mean of 1 - p over ideal-one members + mean of p over ideal-zero members) / 2."""
    return 0.5 + sum(weight * successes[name] for name, weight in endpoint_weights(sector).items())


def summarize_tile(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    """One tile's per-member success, both endpoint errors and the within-tile template difference.

    Point estimates only: live_run also summarizes unclipped readout-inverted
    distributions, and the intervals belong to crossed_contrasts on counts.
    """
    successes = {name: float(np.asarray(dist)[0]) for name, dist in distributions.items()}
    summary = {f"{name}_success": value for name, value in successes.items()}
    for sector in TEMPLATES:
        summary[f"sector_{sector}_endpoint_error"] = endpoint_error(successes, sector)
    summary["template_difference"] = (
        summary[f"sector_{AFFECTED_SECTOR}_endpoint_error"] - summary[f"sector_{REFERENCE_SECTOR}_endpoint_error"]
    )
    return summary


@cache
def clopper_pearson(successes: int, shots: int, alpha: float) -> tuple[float, float]:
    lower = 0.0 if successes == 0 else float(beta.ppf(alpha / 2.0, successes, shots - successes + 1))
    upper = 1.0 if successes == shots else float(beta.ppf(1.0 - alpha / 2.0, successes + 1, shots - successes))
    return lower, upper


CONTRAST_COEFFICIENTS = {
    # Coefficient of y(tile, sector) in each contrast.
    "tile_effect": {
        ("weak", AFFECTED_SECTOR): 0.5,
        ("weak", REFERENCE_SECTOR): 0.5,
        ("reference", AFFECTED_SECTOR): -0.5,
        ("reference", REFERENCE_SECTOR): -0.5,
    },
    "template_effect": {
        ("weak", AFFECTED_SECTOR): 0.5,
        ("weak", REFERENCE_SECTOR): -0.5,
        ("reference", AFFECTED_SECTOR): 0.5,
        ("reference", REFERENCE_SECTOR): -0.5,
    },
    "interaction": {
        ("weak", AFFECTED_SECTOR): 1.0,
        ("weak", REFERENCE_SECTOR): -1.0,
        ("reference", AFFECTED_SECTOR): -1.0,
        ("reference", REFERENCE_SECTOR): 1.0,
    },
}


def crossed_contrasts(weak: Mapping[str, float], reference: Mapping[str, float], shots: int) -> dict[str, float]:
    """T, L and I with simultaneous family-wise intervals from the success counts of both tiles."""
    tiles = {"weak": weak, "reference": reference}
    cells = sum(len(endpoint_weights(sector)) for sector in TEMPLATES) * len(tiles)
    alpha = FAMILY_ALPHA / cells
    out: dict[str, float] = {}
    for contrast, coefficients in CONTRAST_COEFFICIENTS.items():
        value = lower = upper = 0.0
        for (tile, sector), coefficient in coefficients.items():
            for name, weight in endpoint_weights(sector).items():
                p = tiles[tile][f"{name}_success"]
                count = round(p * shots)
                if abs(count - p * shots) > 1e-6 * shots:
                    raise ValueError(f"{name} success {p} is not a count out of {shots} shots")
                low, high = clopper_pearson(count, shots, alpha)
                factor = coefficient * weight
                value += factor * p
                lower += factor * (low if factor > 0 else high)
                upper += factor * (high if factor > 0 else low)
            # The constant 0.5 of each endpoint error cancels in every contrast.
        out[contrast] = value
        out[f"{contrast}_lower"] = lower
        out[f"{contrast}_upper"] = upper
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

    shots = 512

    def tile(faulted: dict[int, dict[str, np.ndarray]]) -> dict[str, float]:
        """Summary of expected counts: each law rounded to a whole number of the 512 shots."""
        merged = {
            name: np.round(np.asarray(law) * shots) / shots
            for sector in TEMPLATES
            for name, law in faulted[sector].items()
        }
        return summarize_tile(merged)

    clean = tile(ideal)
    _require(all(abs(clean[f"sector_{s}_endpoint_error"]) < 1e-12 for s in TEMPLATES), "ideal endpoint error is zero")

    # The corner baseline's qubit 0 flips, applied to both selector bits of the weak tile.
    readout = {sector: selector_channel(ideal[sector], 0.388, 0.144) for sector in TEMPLATES}
    tile_fault = crossed_contrasts(tile(readout), clean, shots)
    _require(tile_fault["tile_effect_lower"] > 0.0, "a weak-tile readout fault must resolve a tile effect")
    _require(
        abs(tile_fault["template_effect"]) < 1e-12 and abs(tile_fault["interaction"]) < 1e-12,
        "a channel fault must leave L and I at zero",
    )

    def over_rotation(sector: int, circuit: QuantumCircuit) -> None:
        if sector == AFFECTED_SECTOR:
            circuit.ry(0.6, 2)

    rotated = {sector: member_laws(sector, over_rotation) for sector in TEMPLATES}
    template_fault = crossed_contrasts(tile(rotated), tile(rotated), shots)
    _require(
        template_fault["template_effect_lower"] > 0.0, "a template fault on both tiles must resolve a template effect"
    )
    _require(abs(template_fault["tile_effect"]) < 1e-12, "a template fault on both tiles leaves T at zero")
    both = crossed_contrasts(tile(rotated), clean, shots)
    _require(both["interaction_lower"] > 0.0, "a template fault on the weak tile only must resolve an interaction")

    _require(placement_violation(BACKEND, [list(WEAK_TILE), list(REFERENCE_TILE)]) is None, "the crossing is admitted")
    _require(placement_violation(BACKEND, [list(WEAK_TILE)]) is not None, "a one-tile plan is refused")
    _require(
        placement_violation(BACKEND, [list(WEAK_TILE), [4, 5, 6, 7]]) is not None,
        "a plan off the reference tile is refused",
    )
    _require(placement_violation("ibm_fez", [list(WEAK_TILE), list(REFERENCE_TILE)]) is not None, "Fez is refused")

    # A weak-tile bright member with true error 0.001 shows no error in 512
    # shots about 60 percent of the time; the intervals must keep a positive
    # width and still contain the true contrasts.
    perfect = crossed_contrasts(clean, clean, shots)
    bright = endpoint_members(AFFECTED_SECTOR)[0][0]
    true_tile = 0.5 * 0.5 * 0.001 / len(endpoint_members(AFFECTED_SECTOR)[0])
    for key, truth in (("tile_effect", true_tile), ("template_effect", true_tile), ("interaction", 2 * true_tile)):
        _require(
            perfect[f"{key}_lower"] < truth < perfect[f"{key}_upper"]
            and perfect[f"{key}_upper"] - perfect[f"{key}_lower"] > 0.0,
            f"{key}: a zero-error sample must keep a positive-width interval covering {truth} ({bright})",
        )
    return (
        f"crossed tile x template: {len(group.members)} members, matched exact laws; readout fault T = "
        f"{tile_fault['tile_effect']:.3f} with L = I = 0; template fault L = {template_fault['template_effect']:.3f}; "
        f"weak-tile-only template fault I = {both['interaction']:.3f}"
    )


def placement_violation(backend: str, replica_qubits: list[list[int]]) -> str | None:
    """Why a plan is not the crossing: one replica on each prescribed ibm_kingston tile, nothing else."""
    if backend != BACKEND:
        return f"crossed_tile_template runs on {BACKEND}, not {backend}"
    tiles = sorted(tuple(sorted(qubits)) for qubits in replica_qubits)
    if tiles != sorted((WEAK_TILE, REFERENCE_TILE)):
        return f"crossed_tile_template needs one replica on each of {WEAK_TILE} and {REFERENCE_TILE}, got {tiles}"
    return None


def _by_tile(
    replicas: list[dict[str, Any]], summaries: list[dict[str, float]]
) -> dict[tuple[int, ...], dict[str, float]]:
    violation = placement_violation(BACKEND, [replica["physical_qubits"] for replica in replicas])
    if violation is not None:
        raise SystemExit(violation)
    return {tuple(sorted(r["physical_qubits"])): summary for r, summary in zip(replicas, summaries, strict=True)}


def record_contrasts(path: Path) -> dict[str, Any]:
    """Noise-model contrasts from a dry-run record.json, labeled as simulation."""
    data = json.loads(path.read_text())
    group = next(entry for entry in data["groups"] if entry["group"] == "crossed_tile_template")
    by_tile = _by_tile(group["replicas"], group["summary_per_replica"])
    return {
        "source": "noise_model_simulation",
        **crossed_contrasts(by_tile[WEAK_TILE], by_tile[REFERENCE_TILE], int(data["shots"])),
    }


def collection_contrasts(path: Path) -> dict[str, Any]:
    """Measured contrasts from a collect.json, with placement and shots from its sibling record.json.

    The collector writes a list of entries; the group's measured per-replica
    summaries follow the record's replica order. A member whose PUB spans a
    recalibration or lacks its execution window is refused, never replaced
    by the simulated summary.
    """
    entries = json.loads(path.read_text())
    record = json.loads((path.parent / "record.json").read_text())
    if not isinstance(entries, list):
        raise SystemExit(f"{path} is not a collection")
    entry = next((item for item in entries if item.get("group") == "crossed_tile_template"), None)
    if entry is None or "measured_statistics" not in entry:
        raise SystemExit("the collection carries no measured crossed_tile_template statistics")
    for member, executed in entry.get("executed", {}).items():
        if executed.get("calibration_changed_during_shots") or executed.get("window_unavailable_reason"):
            raise SystemExit(f"{member} spans a recalibration or lacks its window; the crossing is withheld")
    group = next(item for item in record["groups"] if item["group"] == "crossed_tile_template")
    by_tile = _by_tile(group["replicas"], entry["measured_statistics"]["summary_per_replica"])
    return {
        "source": "measured",
        **crossed_contrasts(by_tile[WEAK_TILE], by_tile[REFERENCE_TILE], int(record["shots"])),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--record", type=Path, help="noise-model contrasts of a dry-run record.json")
    source.add_argument("--collection", type=Path, help="measured contrasts of a collect.json")
    arguments = parser.parse_args()
    if arguments.record is not None:
        print(json.dumps(record_contrasts(arguments.record), indent=2, sort_keys=True))
    elif arguments.collection is not None:
        print(json.dumps(collection_contrasts(arguments.collection), indent=2, sort_keys=True))
    else:
        print(self_check())
