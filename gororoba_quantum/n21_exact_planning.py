"""Exact model predictions and declared replica covariance for the N=21 feedback families.

qpu_planning.prepare calls two functions here when a dry run of an N21 family
asks for them; every other family plans as before.

- ``exact_predictions`` replaces each replica's sampled noisy marginal with
  the exact branch-resolved law dynamic_density computes under the same Aer
  noise model, so the optimizer receives ``simulation_shots=None`` and the
  finite-simulation allowance vanishes. The sampled marginals stay the
  falsifier: every exact probability must lie within the simultaneous
  Hoeffding radius of its sampled frequency at total tail simulation_alpha,
  or planning stops.
- ``replica_covariance_bounds`` declares, for each contract and PUB with two
  or more replicas of a member, the PSD bound diag(V) on the per-replica
  score covariance. The diagonal V bounds each replica's score variance;
  the zero off-diagonal is the replica-independence assumption: disjoint
  placements one CZ hop apart on the admitted graph (live_run.place_replicas)
  and a noise model without inter-replica crosstalk. A declared V below a
  replica's modeled score variance stops planning.

The collector applies the same bound (qpu_planning.measured_family), and
scripts/n21_replica_covariance.py tests it against the shot-ordered raw
registers of a collected run.
"""

from __future__ import annotations

import io
import math
from typing import Any

import numpy as np
from qiskit import qpy

import dynamic_density
import parallel
from experiment_optimizer import CovarianceBound, ObservableContract

MODEL_METHODS = ("sampled", "exact")
INDEPENDENCE_ASSUMPTION = (
    "per-replica score variance at most {bound}; replicas independent: disjoint placements one CZ hop apart "
    "on the admitted graph and no inter-replica crosstalk in the noise model; "
    "falsifier scripts/n21_replica_covariance.py on the collected raw registers"
)


def _exact_law(item: tuple[bytes, Any]) -> list[float]:
    payload, noise_model = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    return [float(value) for value in dynamic_density.probabilities(circuit, noise_model)]


def _serialized(circuit: Any) -> bytes:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


def exact_predictions(
    choices: list[Any],
    noise_models: dict[int, Any],
    sampled: dict[str, tuple[tuple[float, ...], ...]],
    model_shots: int,
    simulation_alpha: float,
) -> tuple[dict[str, tuple[tuple[float, ...], ...]], dict[str, Any]]:
    """Exact replica laws of every entry in choices, validated against their sampled marginals.

    noise_models maps id(choice.snap) to the Aer noise model the sampled
    simulation used. Returns the exact predictions keyed like sampled and the
    validation evidence the record retains.
    """
    keys: list[tuple[str, int]] = []
    items: list[tuple[bytes, Any]] = []
    for choice in choices:
        noise = noise_models[id(choice.snap)]
        for entry in choice.entries:
            for index, replica in enumerate(entry.replicas):
                keys.append((entry.name, index))
                items.append((_serialized(replica), noise))
    laws = parallel.ordered_map(_exact_law, items, min_items=2)
    outcomes = sum(len(law) for law in laws)
    radius = dynamic_density.hoeffding_radius(model_shots, outcomes, simulation_alpha)
    exact: dict[str, list[tuple[float, ...]]] = {}
    rows = []
    worst = 0.0
    for (name, index), law in zip(keys, laws, strict=True):
        frequency = np.asarray(sampled[name][index], dtype=float)
        gap = float(np.max(np.abs(frequency - np.asarray(law))))
        worst = max(worst, gap)
        exact.setdefault(name, []).append(tuple(law))
        rows.append({"entry": name, "replica": index, "exact": law, "max_gap": gap})
    evidence = {
        "method": "dynamic_density branch-resolved density matrix under the sampled run's Aer noise model",
        "validation": "every exact probability within the simultaneous Hoeffding radius of its sampled frequency",
        "model_shots": model_shots,
        "tail": simulation_alpha,
        "radius": radius,
        "max_gap": worst,
        "replicas": rows,
    }
    if worst > radius:
        raise ValueError(f"exact model leaves the sampled radius: max gap {worst} > {radius}")
    return {name: tuple(values) for name, values in exact.items()}, evidence


def score_variance(distribution: tuple[float, ...], values: tuple[float, ...]) -> float:
    """Variance of one replica's bounded score under its predicted outcome law."""
    mean = math.fsum(p * v for p, v in zip(distribution, values, strict=True))
    return math.fsum(p * (v - mean) ** 2 for p, v in zip(distribution, values, strict=True))


def replica_covariance_bounds(
    pubs: list[Any], contracts: tuple[ObservableContract, ...], variance_bound: float
) -> tuple[CovarianceBound, ...]:
    """diag(variance_bound) for every contract/PUB pair whose terms carry two or more replicas.

    pubs are PubPrediction objects; labels follow the optimizer's member/rK
    order (term order, then replica order).
    """
    if not 0 < variance_bound <= 1:
        raise ValueError("the replica variance bound must lie in (0, 1]")
    bounds = []
    for contract in contracts:
        for pub in pubs:
            labels: list[str] = []
            for term in contract.terms:
                replicas = pub.member_distributions.get(term.member)
                if replicas is None:
                    continue
                for index, distribution in enumerate(replicas):
                    modeled = score_variance(distribution, term.values)
                    if modeled > variance_bound:
                        raise ValueError(
                            f"{term.member}/r{index}: modeled score variance {modeled} exceeds the declared "
                            f"bound {variance_bound}"
                        )
                    labels.append(f"{term.member}/r{index}")
            if len(labels) < 2:
                continue
            matrix = tuple(
                tuple(variance_bound if row == column else 0.0 for column in range(len(labels)))
                for row in range(len(labels))
            )
            bounds.append(
                CovarianceBound(
                    contract.name,
                    pub.name,
                    tuple(labels),
                    matrix,
                    INDEPENDENCE_ASSUMPTION.format(bound=variance_bound),
                )
            )
    return tuple(bounds)


def self_test() -> None:
    """Covariance construction rules and exact-law validation on dynamic_density's fixture."""
    from types import SimpleNamespace

    from qiskit_aer import AerSimulator

    from experiment_optimizer import ObservableTerm, PubPrediction

    signed = (0.0, 1.0, 0.0, -1.0)
    contract = ObservableContract("contrast", (ObservableTerm("a", signed), ObservableTerm("b", signed, sign=-1)))
    law = (0.25, 0.25, 0.25, 0.25)

    def pub(name: str, member: str, replicas: int) -> PubPrediction:
        return PubPrediction(name, {member: (law,) * replicas}, 1e-4, 2.5e-4, "fixture")

    bounds = replica_covariance_bounds([pub("p1", "a", 3), pub("p2", "b", 1)], (contract,), 0.55)
    if len(bounds) != 1 or bounds[0].labels != ("a/r0", "a/r1", "a/r2") or bounds[0].matrix[1] != (0.0, 0.55, 0.0):
        raise AssertionError(f"unexpected covariance bounds {bounds}")
    for invalid in (0.0, 1.5, 0.4):
        try:
            replica_covariance_bounds([pub("p1", "a", 2)], (contract,), invalid)
        except ValueError:
            continue
        raise AssertionError(f"variance bound {invalid} must be refused (modeled variance 0.5)")

    circuit, noise = dynamic_density._fixture()
    shots = 200_000
    counts = AerSimulator(method="density_matrix", noise_model=noise, seed_simulator=11).run(circuit, shots=shots)
    frequency = np.zeros(2**circuit.num_clbits)
    for bits, count in counts.result().get_counts().items():
        frequency[int(bits.replace(" ", ""), 2)] += count / shots
    snap = object()
    choice = SimpleNamespace(snap=snap, entries=[SimpleNamespace(name="fixture", replicas=[circuit])])
    sampled = {"fixture": (tuple(frequency),)}
    exact, evidence = exact_predictions([choice], {id(snap): noise}, sampled, shots, 0.01)
    if evidence["max_gap"] > evidence["radius"] or len(exact["fixture"]) != 1:
        raise AssertionError(f"fixture validation failed: {evidence}")
    shifted = frequency.copy()
    shifted[0] += 0.05
    shifted[1] -= 0.05
    try:
        exact_predictions([choice], {id(snap): noise}, {"fixture": (tuple(shifted),)}, shots, 0.01)
    except ValueError:
        pass
    else:
        raise AssertionError("a 0.05 shift of the sampled law must stop planning")
    print(
        f"n21 exact planning: covariance rules hold; fixture exact law within {evidence['max_gap']:.5f} "
        f"of {shots} sampled shots (radius {evidence['radius']:.5f}); shifted law refused"
    )


if __name__ == "__main__":
    self_test()
