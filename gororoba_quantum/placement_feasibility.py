"""Bounded infeasibility certificates for the placement search's finite domain.

The solver only rejects a domain that HiGHS certifies infeasible. Feasible,
limited, and oversized domains continue through the existing ordered search,
which remains responsible for choosing the result and validating its circuits.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_array

MAX_VARIABLES = 1000
SOLVER_SECONDS = 5.0


@dataclass(frozen=True)
class PlacementFootprint:
    """Occupied qubits and closed neighborhoods in the two routing graphs.

    admitted contains qubits plus their neighbors in the pool's admitted
    undirected graph. physical contains qubits plus their neighbors in the
    shared physical undirected graph, including quality-excluded couplers.
    """

    qubits: frozenset[int]
    admitted: frozenset[int]
    physical: frozenset[int]


@dataclass(frozen=True)
class PlacementDomain:
    """One pool's candidate footprints and pre-existing blocked/foreign set."""

    candidates: tuple[PlacementFootprint, ...]
    blocked: frozenset[int] = frozenset()


def _validate(footprint: PlacementFootprint) -> None:
    if not footprint.qubits:
        raise ValueError("placement candidate must occupy at least one qubit")
    if not footprint.qubits <= footprint.admitted or not footprint.qubits <= footprint.physical:
        raise ValueError("closed placement neighborhoods must contain the occupied qubits")
    if any(type(qubit) is not int or qubit < 0 for qubit in footprint.admitted | footprint.physical):
        raise ValueError("placement neighborhoods require non-negative integer qubits")


def certified_infeasible(
    domains: Sequence[PlacementDomain],
    occupied: frozenset[int],
    replicas_per_pool: int = 1,
    cross_group_buffer: bool = True,
) -> bool:
    """Return True only for a bounded HiGHS infeasibility certificate.

    The caller supplies the same initial occupied, blocked, and foreign sets
    used by its ordered search. One binary variable selects each distinct
    occupied-qubit set per pool; identical sets have identical neighborhoods
    because each pool uses fixed undirected graphs. Exactly replicas_per_pool
    variables must be selected in every pool. Pairwise conflicts use occupied
    versus admitted neighborhoods within a pool, and occupied versus physical
    neighborhoods across pools when buffering is enabled. Buffer-buffer
    overlap remains allowed. Candidate scores and ordering remain untouched.
    """
    if type(replicas_per_pool) is not int or replicas_per_pool < 1:
        raise ValueError("replicas_per_pool must be a positive integer")
    if not domains:
        return False
    candidates: list[tuple[int, PlacementFootprint]] = []
    pool_columns: list[list[int]] = []
    for pool_index, domain in enumerate(domains):
        blocked = occupied | domain.blocked
        unique: dict[frozenset[int], PlacementFootprint] = {}
        for footprint in domain.candidates:
            _validate(footprint)
            if footprint.qubits & blocked:
                continue
            previous = unique.setdefault(footprint.qubits, footprint)
            if previous != footprint:
                raise ValueError("same-pool identical qubit sets have inconsistent graph neighborhoods")
        # The ordered search detects these empty/undersized domains directly.
        if len(unique) < replicas_per_pool:
            return False
        start = len(candidates)
        candidates.extend((pool_index, footprint) for footprint in unique.values())
        pool_columns.append(list(range(start, len(candidates))))
        if len(candidates) > MAX_VARIABLES:
            return False

    row_indices: list[int] = []
    column_indices: list[int] = []
    lower_bounds: list[float] = []
    upper_bounds: list[float] = []

    def constraint(columns: Sequence[int], lower: float, upper: float) -> None:
        row = len(lower_bounds)
        row_indices.extend([row] * len(columns))
        column_indices.extend(columns)
        lower_bounds.append(lower)
        upper_bounds.append(upper)

    for columns in pool_columns:
        constraint(columns, float(replicas_per_pool), float(replicas_per_pool))
    for first_index, second_index in combinations(range(len(candidates)), 2):
        first_pool, first = candidates[first_index]
        second_pool, second = candidates[second_index]
        if first_pool == second_pool:
            conflict = bool(first.qubits & second.admitted or second.qubits & first.admitted)
        elif cross_group_buffer:
            conflict = bool(first.qubits & second.physical or second.qubits & first.physical)
        else:
            conflict = bool(first.qubits & second.qubits)
        if conflict:
            constraint((first_index, second_index), 0.0, 1.0)

    variable_count = len(candidates)
    matrix = coo_array(
        (np.ones(len(row_indices)), (row_indices, column_indices)),
        shape=(len(lower_bounds), variable_count),
    ).tocsc()
    result = milp(
        np.zeros(variable_count),
        integrality=np.ones(variable_count),
        bounds=Bounds(0.0, 1.0),
        constraints=LinearConstraint(matrix, np.asarray(lower_bounds), np.asarray(upper_bounds)),
        options={"time_limit": SOLVER_SECONDS, "mip_rel_gap": 0.0, "presolve": True},
    )
    return bool(result.status == 2)
