"""Affine-skeleton extraction with a target-flip residual.

The degree-zero and degree-one ANF terms of a register permutation f give
``f(x) = A x XOR b XOR q(x)``, with q collecting the terms of degree two and
higher. When A is invertible over GF(2), ``r(x) = A^-1 (f(x) XOR b)`` is a
register permutation whose own affine part is the identity, and
``f(x) = A r(x) XOR b``. Exact target flips synthesize r; Gauss-Jordan
elimination synthesizes A as an in-place CNOT network. A singular A has no
in-place reversible linear factor, so the decomposition is inapplicable.

Every gate of the composed network is a target-flip cube: an in-place CNOT
from bit c to bit t flips t under the one-literal predicate ``x_c``, and an X
on bit i flips i under the empty predicate. Phase-control emission adds the
outer control to every cube, which promotes each CNOT to a Toffoli and each X
to a CX.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from boolean_anf import _gf2_rank, anf_coefficients
from target_flip import CONTROLLED_CX_COST, TargetCube, apply_network, target_flip_network


@dataclass(frozen=True)
class AffineSkeleton:
    """Degree-zero and degree-one ANF terms of one register permutation.

    Bit j of ``linear_rows[i]`` is the coefficient of input bit j in output
    bit i, and bit i of ``constant`` is the constant term of output bit i.
    """

    width: int
    constant: int
    linear_rows: tuple[int, ...]
    rank: int

    @property
    def invertible(self) -> bool:
        return self.rank == self.width


@dataclass(frozen=True)
class AffineResidualSynthesis:
    """Exact factorization ``f = X_b o A o r`` with its target-flip gate words.

    ``linear_cnots`` lists ``(control_bit, target_bit)`` pairs in circuit
    order. ``network`` applies the residual cubes, then the linear CNOTs, then
    the constant X flips, so its integer action is f.
    """

    skeleton: AffineSkeleton
    inverse_rows: tuple[int, ...]
    residual: tuple[int, ...]
    residual_network: tuple[TargetCube, ...]
    linear_cnots: tuple[tuple[int, int], ...]
    network: tuple[TargetCube, ...]


def _register_width(permutation: tuple[int, ...]) -> int:
    size = len(permutation)
    if size < 2 or size & (size - 1) or set(permutation) != set(range(size)):
        raise ValueError("affine-skeleton extraction requires a complete power-of-two permutation")
    return size.bit_length() - 1


def apply_linear(rows: tuple[int, ...], input_value: int) -> int:
    """Evaluate ``A x`` over GF(2) with packed rows and a packed input."""
    return sum(((row & input_value).bit_count() & 1) << output_bit for output_bit, row in enumerate(rows))


def affine_skeleton(permutation: tuple[int, ...]) -> AffineSkeleton:
    """Read the constant vector and linear matrix from the output-bit ANFs."""
    width = _register_width(permutation)
    constant = 0
    rows: list[int] = []
    for output_bit in range(width):
        coefficients = anf_coefficients([(output_value >> output_bit) & 1 for output_value in permutation])
        if 0 in coefficients:
            constant |= 1 << output_bit
        rows.append(sum(1 << input_bit for input_bit in range(width) if (1 << input_bit) in coefficients))
    return AffineSkeleton(width, constant, tuple(rows), _gf2_rank(rows, width))


def gf2_inverse(rows: tuple[int, ...], width: int) -> tuple[int, ...]:
    """Return the packed rows of ``A^-1`` by Gauss-Jordan elimination over GF(2)."""
    reduced = list(rows)
    inverse = [1 << row_index for row_index in range(width)]
    for column in range(width):
        column_mask = 1 << column
        pivot = next((row for row in range(column, width) if reduced[row] & column_mask), None)
        if pivot is None:
            raise ValueError(f"GF(2) matrix is singular at column {column}")
        reduced[column], reduced[pivot] = reduced[pivot], reduced[column]
        inverse[column], inverse[pivot] = inverse[pivot], inverse[column]
        for row in range(width):
            if row != column and reduced[row] & column_mask:
                reduced[row] ^= reduced[column]
                inverse[row] ^= inverse[column]
    return tuple(inverse)


def apply_cnots(cnots: tuple[tuple[int, int], ...], input_value: int) -> int:
    """Evaluate in-place ``(control_bit, target_bit)`` CNOTs in circuit order."""
    for control_bit, target_bit in cnots:
        input_value ^= ((input_value >> control_bit) & 1) << target_bit
    return input_value


def linear_cnot_network(rows: tuple[int, ...], width: int) -> tuple[tuple[int, int], ...]:
    """Synthesize ``x -> A x`` in place as CNOTs from swap-free Gauss-Jordan elimination.

    Each row operation ``row_t ^= row_c`` left-multiplies by the self-inverse
    elementary matrix ``E = I + e_t e_c^T``, which is the action of a CNOT with
    control c and target t. Reducing ``E_m ... E_1 A = I`` gives
    ``A = E_1 ... E_m``, so the circuit applies the recorded row operations in
    reverse order. A missing pivot is filled by adding a lower row that holds
    it, one CNOT where a row swap costs three.
    """
    reduced = list(rows)
    operations: list[tuple[int, int]] = []
    for column in range(width):
        column_mask = 1 << column
        if not reduced[column] & column_mask:
            donor = next((row for row in range(column + 1, width) if reduced[row] & column_mask), None)
            if donor is None:
                raise ValueError(f"GF(2) matrix is singular at column {column}")
            reduced[column] ^= reduced[donor]
            operations.append((donor, column))
        for row in range(width):
            if row != column and reduced[row] & column_mask:
                reduced[row] ^= reduced[column]
                operations.append((column, row))
    if reduced != [1 << row for row in range(width)]:
        raise RuntimeError("Gauss-Jordan elimination left a non-identity matrix")
    cnots = tuple(reversed(operations))
    if any(apply_cnots(cnots, value) != apply_linear(rows, value) for value in range(1 << width)):
        raise RuntimeError("CNOT network disagrees with its GF(2) matrix on the complete register")
    return cnots


def minimum_cnot_count(rows: tuple[int, ...], width: int) -> int:
    """Return the fewest in-place CNOTs realizing ``A`` by bidirectional breadth-first search.

    Vertices are packed GL(width, 2) matrices and each edge is one row
    operation, so the graph distance from the identity to A is the minimum
    CNOT count. Each round expands a complete level of the smaller frontier;
    the first level that meets the other search yields the shortest distance.
    """
    if not 1 <= width <= 5:
        raise ValueError(f"minimum CNOT search supports widths one through five, got {width}")
    if _gf2_rank(list(rows), width) != width:
        raise ValueError("minimum CNOT search requires an invertible matrix")

    def pack(matrix_rows: list[int] | tuple[int, ...]) -> int:
        return sum(row << (width * index) for index, row in enumerate(matrix_rows))

    row_mask = (1 << width) - 1
    generators = tuple((control, target) for control in range(width) for target in range(width) if control != target)
    identity = pack([1 << row for row in range(width)])
    goal = pack(rows)
    distances = ({identity: 0}, {goal: 0})
    frontiers: tuple[list[int], list[int]] = ([identity], [goal])
    while identity not in distances[1]:
        side = 0 if len(frontiers[0]) <= len(frontiers[1]) else 1
        if not frontiers[side]:
            raise RuntimeError("CNOT search exhausted a frontier inside a connected group")
        seen, other = distances[side], distances[1 - side]
        next_frontier: list[int] = []
        meeting: int | None = None
        for matrix in frontiers[side]:
            for control, target in generators:
                source_row = (matrix >> (width * control)) & row_mask
                neighbor = matrix ^ (source_row << (width * target))
                if neighbor in seen:
                    continue
                seen[neighbor] = seen[matrix] + 1
                next_frontier.append(neighbor)
                if neighbor in other:
                    total = seen[neighbor] + other[neighbor]
                    meeting = total if meeting is None else min(meeting, total)
        if meeting is not None:
            return meeting
        frontiers = (next_frontier, frontiers[1]) if side == 0 else (frontiers[0], next_frontier)
    return 0


def affine_residual_synthesis(permutation: tuple[int, ...]) -> AffineResidualSynthesis:
    """Factor a full-rank permutation into a target-flip residual, CNOTs, and X flips.

    A linear part below full GF(2) rank raises ValueError naming the rank.
    """
    skeleton = affine_skeleton(permutation)
    width = skeleton.width
    if not skeleton.invertible:
        raise ValueError(
            f"affine residual synthesis needs an invertible linear part; GF(2) rank is {skeleton.rank} "
            f"below register width {width}"
        )
    inverse_rows = gf2_inverse(skeleton.linear_rows, width)
    residual = tuple(apply_linear(inverse_rows, output_value ^ skeleton.constant) for output_value in permutation)
    if sorted(residual) != list(range(1 << width)):
        raise RuntimeError("affine residual is not a permutation of the complete register")
    residual_skeleton = affine_skeleton(residual)
    if residual_skeleton.constant or residual_skeleton.linear_rows != tuple(1 << bit for bit in range(width)):
        raise RuntimeError("affine residual retains a nonidentity affine part")
    residual_network = target_flip_network(residual)
    linear_cnots = linear_cnot_network(skeleton.linear_rows, width)
    linear_cubes = tuple(TargetCube(target, 1 << control, 1 << control) for control, target in linear_cnots)
    constant_cubes = tuple(TargetCube(bit, 0, 0) for bit in range(width) if skeleton.constant & (1 << bit))
    network = residual_network + linear_cubes + constant_cubes
    if tuple(apply_network(network, value) for value in range(1 << width)) != permutation:
        raise RuntimeError("affine-residual network disagrees with the complete permutation")
    return AffineResidualSynthesis(
        skeleton=skeleton,
        inverse_rows=inverse_rows,
        residual=residual,
        residual_network=residual_network,
        linear_cnots=linear_cnots,
        network=network,
    )


def network_cx_surrogate(network: tuple[TargetCube, ...]) -> int:
    """Count phase-controlled CX equivalents with the target-flip cube weights."""
    return sum(CONTROLLED_CX_COST[cube.control_mask.bit_count()] for cube in network)


def verification_record(modulus: int = 21, multipliers: tuple[int, ...] = (2, 4, 16)) -> dict[str, Any]:
    """Run the exhaustive integer and Operator checks and return their census.

    Every unit modulo ``modulus`` contributes its linear rank. Each multiplier
    in ``multipliers`` must have full rank; its residual and composed network
    are checked on every register state, and its phase-controlled circuit is
    checked by ``_verify_multiplier`` on both control branches with a clean
    workspace. Two mutations must fail: the reversed composition ``r o A`` and
    linear CNOTs left outside the phase control.
    """
    import math

    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator

    from modular_arithmetic import (
        AFFINE_RESIDUAL_STRATEGY,
        _append_controlled_target_flips,
        _verify_multiplier,
        modular_permutation,
    )

    swap_rows = (2, 1, 4)
    if minimum_cnot_count(swap_rows, 3) != 3 or minimum_cnot_count((1, 3, 4), 3) != 1:
        raise RuntimeError("minimum CNOT search failed its swap and single-CNOT witnesses")
    rank_census = []
    for multiplier in range(2, modulus):
        if math.gcd(multiplier, modulus) != 1:
            continue
        skeleton = affine_skeleton(modular_permutation(modulus, multiplier))
        if skeleton.constant:
            raise RuntimeError(f"{multiplier} mod {modulus} has nonzero affine constant {skeleton.constant}")
        applicable = True
        try:
            affine_residual_synthesis(modular_permutation(modulus, multiplier))
        except ValueError as error:
            if skeleton.invertible or f"rank is {skeleton.rank}" not in str(error):
                raise
            applicable = False
        if applicable != skeleton.invertible:
            raise RuntimeError(f"{multiplier} mod {modulus} applicability disagrees with rank {skeleton.rank}")
        rank_census.append(
            {
                "multiplier": multiplier,
                "inverse_multiplier": pow(multiplier, -1, modulus),
                "constant": skeleton.constant,
                "linear_rank": skeleton.rank,
                "applicable": applicable,
            }
        )

    multiplier_records = []
    for multiplier in multipliers:
        permutation = modular_permutation(modulus, multiplier)
        synthesis = affine_residual_synthesis(permutation)
        width = synthesis.skeleton.width
        states = range(1 << width)
        if tuple(apply_network(synthesis.residual_network, value) for value in states) != synthesis.residual:
            raise RuntimeError(f"residual network for {multiplier} mod {modulus} disagrees with r")
        constant = synthesis.skeleton.constant
        composed = tuple(
            apply_cnots(synthesis.linear_cnots, apply_network(synthesis.residual_network, value)) ^ constant
            for value in states
        )
        if composed != permutation:
            raise RuntimeError(f"A o r for {multiplier} mod {modulus} disagrees with f")
        reversed_order = tuple(
            apply_network(synthesis.residual_network, apply_cnots(synthesis.linear_cnots, value)) for value in states
        )
        if reversed_order == permutation:
            raise RuntimeError(f"reversed composition r o A escaped the exhaustive check for {multiplier}")
        for deleted in range(len(synthesis.linear_cnots)):
            mutation = synthesis.linear_cnots[:deleted] + synthesis.linear_cnots[deleted + 1 :]
            linear_rows = synthesis.skeleton.linear_rows
            if all(apply_cnots(mutation, value) == apply_linear(linear_rows, value) for value in states):
                raise RuntimeError(f"deleting linear CNOT {deleted} escaped the GF(2) matrix check for {multiplier}")

        _verify_multiplier(modulus, multiplier, AFFINE_RESIDUAL_STRATEGY)

        qubit_count = width + 2
        control = qubit_count - 1
        data = list(range(width))
        uncontrolled = QuantumCircuit(qubit_count)
        _append_controlled_target_flips(uncontrolled, control, data, [width], synthesis.residual_network)
        for control_bit, target_bit in synthesis.linear_cnots:
            uncontrolled.cx(data[control_bit], data[target_bit])
        matrix = Operator(uncontrolled).data
        disabled_moves = sum(int(np.argmax(np.abs(matrix[:, value]))) != value for value in states)
        if disabled_moves == 0:
            raise RuntimeError(f"uncontrolled linear CNOTs left the disabled branch fixed for {multiplier}")

        minimum_cnots = minimum_cnot_count(synthesis.skeleton.linear_rows, width)
        if minimum_cnots > len(synthesis.linear_cnots):
            raise RuntimeError(f"minimum CNOT search exceeded the Gauss-Jordan witness for {multiplier}")
        baseline_network = target_flip_network(permutation)
        multiplier_records.append(
            {
                "multiplier": multiplier,
                "register_states_per_branch": 1 << width,
                "constant": synthesis.skeleton.constant,
                "linear_rows": list(synthesis.skeleton.linear_rows),
                "inverse_rows": list(synthesis.inverse_rows),
                "linear_rank": synthesis.skeleton.rank,
                "linear_cnots": [list(pair) for pair in synthesis.linear_cnots],
                "linear_cnot_count": len(synthesis.linear_cnots),
                "minimum_linear_cnot_count": minimum_cnots,
                "residual": list(synthesis.residual),
                "residual_cube_count": len(synthesis.residual_network),
                "residual_cx_surrogate": network_cx_surrogate(synthesis.residual_network),
                "challenger_cube_count": len(synthesis.network),
                "challenger_cx_surrogate": network_cx_surrogate(synthesis.network),
                "baseline_cube_count": len(baseline_network),
                "baseline_cx_surrogate": network_cx_surrogate(baseline_network),
                "checks": {
                    "residual_is_register_permutation": True,
                    "residual_affine_part_is_identity": True,
                    "composition_a_after_r_equals_f": True,
                    "reversed_composition_rejected": True,
                    "single_cnot_deletions_rejected": len(synthesis.linear_cnots),
                    "controlled_operator_both_branches_clean_workspace": True,
                    "uncontrolled_linear_disabled_branch_moved_states": disabled_moves,
                },
            }
        )
    return {
        "modulus": modulus,
        "rank_census": rank_census,
        "multipliers": multiplier_records,
    }


def _verify() -> None:
    record = verification_record()
    census = {entry["multiplier"]: entry for entry in record["rank_census"]}
    singular = sorted(multiplier for multiplier, entry in census.items() if not entry["applicable"])
    if 11 not in singular or any(not census[multiplier]["applicable"] for multiplier in (2, 4, 16)):
        raise RuntimeError(f"N=21 rank census changed: singular multipliers {singular}")
    for entry in record["multipliers"]:
        print(
            f"affine residual {entry['multiplier']} mod 21: rank={entry['linear_rank']} "
            f"linear_cnots={entry['linear_cnot_count']} minimum={entry['minimum_linear_cnot_count']} "
            f"residual_cubes={entry['residual_cube_count']} "
            f"cx_surrogate={entry['challenger_cx_surrogate']} baseline={entry['baseline_cx_surrogate']}"
        )
    print(
        f"affine residual: rank-deficient N=21 multipliers {singular}; "
        f"11, the inverse of 2, has rank {census[11]['linear_rank']}"
    )


if __name__ == "__main__":
    _verify()
