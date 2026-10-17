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

- ``covariance_falsifier`` tests every declared bound on the shot-ordered
  replica registers a collection retains under raw/<job_id>/pub_NN.json.
  qpu_planning.measured_family applies the declared bounds only when every
  bound passes and otherwise analyzes every endpoint under the Hoeffding
  arbitrary-dependence radius; ``COVARIANCE_FALSIFIER`` states the
  statistic, threshold and decision, and the record carries it beside the
  bounds. scripts/n21_replica_covariance.py replays the test from a run
  directory.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
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
    "collection tests the bound on the retained shot-ordered replica registers "
    "(n21_exact_planning.COVARIANCE_FALSIFIER) and analyzes under Hoeffding when it fails"
)
FALSIFIER_TAIL = 1e-3
COVARIANCE_FALSIFIER = {
    "statistic": (
        "biased sample variance over shots of the weighted replica score sum Y = sum_k w_k s_k of one "
        "declared bound, w_k = term sign / replica count: the projection w' Sigma w the radius reads"
    ),
    "threshold": (
        "declared projection w' V w plus eps2 + D eps1, with D = sum_k |w_k| (max score - min score), "
        "s = sqrt(ln(4 / t) / (2 n)), eps1 = D s, eps2 = (D^2 / 4) s, n the PUB's shots and "
        "t = tail / number of declared bounds"
    ),
    "tail": FALSIFIER_TAIL,
    "decision": (
        "every declared bound at or below its threshold applies the declared covariance to every endpoint; "
        "any bound above its threshold, or a bound whose shot-ordered registers are absent, analyzes every "
        "endpoint under the Hoeffding arbitrary-dependence radius"
    ),
}


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
    sampled: Mapping[str, tuple[tuple[float, ...], ...]],
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


def variance_allowance(shots: int, span: float, tail: float) -> float:
    """Deviation of the biased sample variance of a score of range span from its expectation, at total tail.

    Z = Y - midpoint has |Z| <= span / 2. Hoeffding at tail / 2 each places
    mean(Z) within eps1 = span s and mean(Z^2) within eps2 = (span^2 / 4) s,
    s = sqrt(ln(4 / tail) / (2 shots)), and |mean(Z)^2 - E[Z]^2| <= span eps1,
    so the estimate lies within eps2 + span eps1 of the variance.
    """
    s = math.sqrt(math.log(4.0 / tail) / (2 * shots))
    return span * span / 4 * s + span * span * s


def replica_outcomes(registers: Mapping[str, Sequence[str]], names: Sequence[str]) -> np.ndarray:
    """Per-shot outcome index of one replica from its registers' shot-ordered bit strings.

    SamplerPubResult.join_data, which the collector's counts use, places a
    later register's bits to the left of an earlier one's, so the joined bit
    string reads the registers in reverse order.
    """
    if not names:
        raise ValueError("a replica needs at least one classical register")
    columns = [registers[name] for name in names]
    if len({len(column) for column in columns}) != 1:
        raise ValueError(f"registers {list(names)} hold different shot counts")
    return np.asarray([int("".join(reversed(bits)), 2) for bits in zip(*columns, strict=True)], dtype=np.int64)


def retained_registers(run_dir: Path, pub_names: set[str]) -> dict[str, dict[str, list[str]]]:
    """Shot-ordered registers of the named PUBs under run_dir/raw, each file checked against its index digest."""
    found: dict[str, dict[str, list[str]]] = {}
    for index_path in sorted((run_dir / "raw").glob("*/index.json")):
        index = json.loads(index_path.read_text())
        for name, digest in sorted(index["files"].items()):
            if not name.startswith("pub_"):
                continue
            payload = (index_path.parent / name).read_bytes()
            if hashlib.sha256(payload).hexdigest() != digest:
                raise ValueError(f"{index_path.parent / name} differs from its indexed digest")
            data = json.loads(payload)
            pub_name = data.get("pub_name")
            if pub_name not in pub_names:
                continue
            if pub_name in found:
                raise ValueError(f"PUB {pub_name} is retained twice under {run_dir / 'raw'}")
            found[pub_name] = {register: entry["bitstrings"] for register, entry in data["registers"].items()}
    return found


def covariance_falsifier(
    record: Mapping[str, Any],
    registers_by_pub: Mapping[str, Mapping[str, Sequence[str]]] | None,
    distributions: Mapping[str, Sequence[Any]] | None = None,
) -> dict[str, Any]:
    """COVARIANCE_FALSIFIER applied to every covariance bound record declares.

    registers_by_pub maps a PUB name to its registers' shot-ordered bit
    strings. distributions, when given, are the collector's replica marginals;
    each replica's outcome frequencies must equal them, which binds the
    register mapping to the counts the endpoints read. A bound passes when its
    statistic stays at or below its threshold; ``holds`` requires every bound
    to pass.
    """
    bounds = list(record.get("covariance_bounds", []))
    if not bounds:
        raise ValueError("the record declares no covariance bound")
    result: dict[str, Any] = {"specification": COVARIANCE_FALSIFIER, "bounds": []}
    if registers_by_pub is None:
        return result | {"holds": False, "reason": "shot-ordered replica registers are unavailable"}
    contracts = {contract["name"]: contract for contract in record["observable_contracts"]}
    components = {
        (pub["name"], component["member"]): component["registers_by_replica"]
        for pub in record["execution_pubs"]
        for component in pub["components"]
    }
    tail = FALSIFIER_TAIL / len(bounds)
    failures: list[str] = []
    for bound in bounds:
        pub_name = bound["pub_name"]
        row: dict[str, Any] = {"observable": bound["observable_name"], "pub": pub_name, "tail": tail}
        registers = registers_by_pub.get(pub_name)
        try:
            if registers is None:
                raise ValueError("no retained shot-ordered registers")
            terms = {term["member"]: term for term in contracts[bound["observable_name"]]["terms"]}
            columns: list[np.ndarray] = []
            weights: list[float] = []
            span = 0.0
            for label in bound["labels"]:
                member, _, index = label.rpartition("/r")
                replicas = components[(pub_name, member)]
                term = terms[member]
                values = np.asarray(term["values"], dtype=float)
                outcomes = replica_outcomes(registers, replicas[int(index)])
                if outcomes.size == 0 or int(outcomes.max()) >= values.size:
                    raise ValueError(f"{label}: outcomes fall outside the {values.size} scored labels")
                if distributions is not None:
                    frequency = np.bincount(outcomes, minlength=values.size) / outcomes.size
                    if not np.allclose(frequency, distributions[member][int(index)], rtol=0.0, atol=1e-12):
                        raise ValueError(f"{label}: register frequencies differ from the collected marginal")
                columns.append(values[outcomes])
                weight = term["sign"] / len(replicas)
                weights.append(weight)
                span += abs(weight) * float(values.max() - values.min())
            if len({column.size for column in columns}) != 1:
                raise ValueError("replica registers hold different shot counts")
        except (KeyError, IndexError, ValueError) as error:
            reason = str(error) if isinstance(error, ValueError) else f"missing {error}"
            failures.append(f"{pub_name}: {reason}")
            result["bounds"].append(row | {"holds": False, "reason": reason})
            continue
        scores = np.stack(columns, axis=1)
        vector = np.asarray(weights, dtype=float)
        realized = float(np.var(scores @ vector))
        declared = float(vector @ np.asarray(bound["matrix"], dtype=float) @ vector)
        allowance = variance_allowance(scores.shape[0], span, tail)
        holds = realized <= declared + allowance
        if not holds:
            failures.append(
                f"{pub_name}: weighted replica score variance {realized:.6f} exceeds {declared:.6f} + {allowance:.6f}"
            )
        result["bounds"].append(
            row
            | {
                "shots": int(scores.shape[0]),
                "labels": list(bound["labels"]),
                "weights": weights,
                "score_span": span,
                "statistic": realized,
                "declared_projection": declared,
                "allowance": allowance,
                "threshold": declared + allowance,
                "covariance_estimate": np.atleast_2d(np.cov(scores, rowvar=False, bias=True)).round(6).tolist(),
                "holds": holds,
            }
        )
    holds = not failures
    return result | {
        "holds": holds,
        "reason": "every declared bound is at or below its threshold" if holds else "; ".join(failures),
    }


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
