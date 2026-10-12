"""Exhaust finite placement domains and challenge bounded solver outcomes."""

from __future__ import annotations

import itertools
import json
import random
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import patch

import parallel
import placement_feasibility as feasibility
from placement_feasibility import PlacementDomain, PlacementFootprint, certified_infeasible


@dataclass(frozen=True)
class Case:
    domains: tuple[PlacementDomain, ...]
    occupied: frozenset[int] = frozenset()
    replicas: int = 1
    buffer: bool = True


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _footprint(
    qubits: frozenset[int], admitted: frozenset[tuple[int, int]], physical: frozenset[tuple[int, int]]
) -> PlacementFootprint:
    def neighborhood(edges: frozenset[tuple[int, int]]) -> frozenset[int]:
        return qubits | frozenset(endpoint for edge in edges if qubits.intersection(edge) for endpoint in edge)

    return PlacementFootprint(qubits, neighborhood(admitted), neighborhood(physical))


def _brute_force(case: Case) -> bool:
    selections = [
        tuple(
            itertools.combinations(
                (
                    footprint
                    for footprint in domain.candidates
                    if not footprint.qubits.intersection(case.occupied | domain.blocked)
                ),
                case.replicas,
            )
        )
        for domain in case.domains
    ]
    for choices in itertools.product(*selections):
        picked = [(pool, footprint) for pool, footprints in enumerate(choices) for footprint in footprints]
        valid = True
        for (first_pool, first), (second_pool, second) in itertools.combinations(picked, 2):
            if first_pool == second_pool:
                forbidden_first, forbidden_second = first.admitted, second.admitted
            elif case.buffer:
                forbidden_first, forbidden_second = first.physical, second.physical
            else:
                forbidden_first, forbidden_second = first.qubits, second.qubits
            if first.qubits & forbidden_second or second.qubits & forbidden_first:
                valid = False
                break
        if valid:
            return True
    return False


def _check_case(case: Case) -> bool:
    feasible = _brute_force(case)
    rejected = certified_infeasible(case.domains, case.occupied, case.replicas, case.buffer)
    _require(not (feasible and rejected), "infeasibility precheck rejected a brute-force placement")
    sufficiently_large = bool(case.domains) and all(
        len(
            {
                candidate.qubits
                for candidate in domain.candidates
                if not candidate.qubits.intersection(case.occupied | domain.blocked)
            }
        )
        >= case.replicas
        for domain in case.domains
    )
    if sufficiently_large:
        _require(rejected == (not feasible), "small bounded solver domain disagrees with exhaustive enumeration")
    return rejected


def _exhaustive_cases() -> list[Case]:
    physical = frozenset(((0, 1), (1, 2)))
    cases = []
    for admitted in (physical, frozenset(((0, 1),))):
        candidates = [_footprint(frozenset((qubit,)), admitted, physical) for qubit in range(3)]
        domains = [
            PlacementDomain(tuple(candidates[qubit] for qubit in range(3) if mask & (1 << qubit)))
            for mask in range(1, 8)
        ]
        for first, second, replicas, buffer in itertools.product(domains, domains, (1, 2), (False, True)):
            cases.append(Case((first, second), replicas=replicas, buffer=buffer))
    return cases


def _random_cases() -> list[Case]:
    generator = random.Random(20261012)
    cases = []
    for _ in range(160):
        physical = frozenset(edge for edge in itertools.combinations(range(6), 2) if generator.random() < 0.3)
        domains = []
        for _ in range(generator.randrange(1, 4)):
            admitted = frozenset(edge for edge in physical if generator.random() < 0.7)
            candidates = tuple(
                _footprint(frozenset(generator.sample(range(6), generator.randrange(1, 3))), admitted, physical)
                for _ in range(generator.randrange(1, 6))
            )
            if generator.random() < 0.5:
                candidates += candidates[:1]
            blocked = frozenset(qubit for qubit in range(6) if generator.random() < 0.08)
            domains.append(PlacementDomain(candidates, blocked))
        occupied = frozenset(qubit for qubit in range(6) if generator.random() < 0.08)
        cases.append(Case(tuple(domains), occupied, generator.randrange(1, 3), bool(generator.randrange(2))))
    return cases


def _boundary_checks() -> int:
    physical = frozenset(((0, 1), (1, 2)))
    admitted: frozenset[tuple[int, int]] = frozenset()
    first = _footprint(frozenset((0,)), admitted, physical)
    second = _footprint(frozenset((1,)), admitted, physical)
    third = _footprint(frozenset((2,)), admitted, physical)
    _require(not certified_infeasible((PlacementDomain((first, second)),), frozenset(), 2), "own admitted graph")
    _require(
        certified_infeasible((PlacementDomain((first,)), PlacementDomain((second,))), frozenset()),
        "excluded physical coupler must separate different pools",
    )
    _require(
        not certified_infeasible((PlacementDomain((first,)), PlacementDomain((second,))), frozenset(), 1, False),
        "disabled cross-group buffer must retain disjoint adjacent placements",
    )
    _require(
        not certified_infeasible((PlacementDomain((first,)), PlacementDomain((third,))), frozenset()),
        "overlapping buffers must remain allowed",
    )
    _require(
        certified_infeasible((PlacementDomain((first, third)), PlacementDomain((second, third))), frozenset((2,))),
        "global occupied qubits must remove otherwise feasible alternatives",
    )
    _require(
        certified_infeasible(
            (PlacementDomain((first, third), frozenset((2,))), PlacementDomain((second,))), frozenset()
        ),
        "pool blocked and foreign qubits must remove otherwise feasible alternatives",
    )
    domain = (PlacementDomain((first, first)), PlacementDomain((third,)))
    for status in (0, 1, 2, 3, 4):
        with patch.object(feasibility, "milp", return_value=SimpleNamespace(status=status)) as solver:
            _require(certified_infeasible(domain, frozenset()) == (status == 2), "only certified status2 prunes")
            _require(len(solver.call_args.args[0]) == 2, "same-pool qubit sets must coalesce")
            _require(solver.call_args.kwargs["options"]["time_limit"] == 5.0, "solver time must remain bounded")
    oversized = PlacementDomain(
        tuple(_footprint(frozenset((qubit,)), frozenset(), frozenset()) for qubit in range(1001))
    )
    with patch.object(feasibility, "milp", side_effect=RuntimeError("oversized domain reached solver")):
        _require(not certified_infeasible((oversized,), frozenset()), "oversized domains keep existing search")
    with patch.object(feasibility, "milp", side_effect=ValueError("sentinel programming error")):
        try:
            certified_infeasible(domain, frozenset())
        except ValueError as error:
            _require(str(error) == "sentinel programming error", "unexpected solver exception")
        else:
            raise RuntimeError("precheck suppressed a programming error")
    inconsistent = PlacementFootprint(first.qubits, first.admitted, first.qubits)
    try:
        certified_infeasible((PlacementDomain((first, inconsistent)),), frozenset())
    except ValueError:
        pass
    else:
        raise RuntimeError("duplicate occupied sets accepted inconsistent graph neighborhoods")
    for replicas in (0, -1, True):
        try:
            certified_infeasible(domain, frozenset(), replicas)
        except ValueError:
            pass
        else:
            raise RuntimeError("invalid replica count accepted")
    return 17


def verify() -> dict[str, int]:
    exhaustive = _exhaustive_cases()
    random_cases = _random_cases()
    decisions = parallel.ordered_map(_check_case, exhaustive + random_cases)
    boundaries = _boundary_checks()
    return {
        "exhaustive_domains": len(exhaustive),
        "seeded_random_domains": len(random_cases),
        "certified_infeasible": sum(decisions),
        "boundary_checks": boundaries,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
