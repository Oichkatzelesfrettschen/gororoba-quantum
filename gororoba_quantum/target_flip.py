"""Bounded reversible switch synthesis with minimum-cost XOR cubes.

A two-color switch graph factors a permutation into single-target flips.
Factoring each predicate before emitting controlled gates avoids flattening
every moved basis state into a separately controlled transposition. The
complete truth table remains the authority; the search scales exponentially
and supplies a bounded compiler, not a polynomial modular-arithmetic theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from heapq import heappop, heappush
from itertools import permutations

MAX_TARGET_FLIP_WIDTH = 5
CONTROLLED_CX_COST = (1, 6, 12, 18, 24)


@dataclass(frozen=True)
class TargetCube:
    """Flip target when the other data bits satisfy mask and control_state."""

    target: int
    control_mask: int
    control_state: int

    def apply(self, input_value: int) -> int:
        return input_value ^ ((1 << self.target) if input_value & self.control_mask == self.control_state else 0)


def _switch_layers(permutation: tuple[int, ...]) -> tuple[tuple[int, tuple[int, ...]], ...]:
    width = len(permutation).bit_length() - 1
    if width == 1:
        return ((0, (int(permutation[0] == 1),)),)
    pair_count = len(permutation) // 2
    outgoing: list[list[int]] = [[] for _ in range(pair_count)]
    for input_value, output_value in enumerate(permutation):
        outgoing[output_value >> 1].append(input_value)
    colors = [-1] * len(permutation)
    for initial in range(len(permutation)):
        if colors[initial] >= 0:
            continue
        component: list[int] = []
        colors[initial] = 0
        frontier = [initial]
        while frontier:
            input_value = frontier.pop()
            component.append(input_value)
            neighbors = [input_value ^ 1, *outgoing[permutation[input_value] >> 1]]
            for neighbor in neighbors:
                if neighbor == input_value:
                    continue
                required_color = 1 - colors[input_value]
                if colors[neighbor] < 0:
                    colors[neighbor] = required_color
                    frontier.append(neighbor)
                elif colors[neighbor] != required_color:
                    raise RuntimeError("permutation switch graph has inconsistent alternating colors")
        direct_flips = sum(
            (colors[input_value] != (input_value & 1)) + (colors[input_value] != (permutation[input_value] & 1))
            for input_value in component
        )
        if 2 * len(component) - direct_flips < direct_flips:
            for input_value in component:
                colors[input_value] ^= 1
    inverse = [0] * len(permutation)
    for input_value, output_value in enumerate(permutation):
        inverse[output_value] = input_value
    first = tuple(colors[2 * pair] for pair in range(pair_count))
    last = tuple(colors[inverse[2 * pair]] for pair in range(pair_count))
    middle = [[0] * pair_count for _ in range(2)]
    for input_value, output_value in enumerate(permutation):
        middle[colors[input_value]][input_value >> 1] = output_value >> 1
    branches = [_switch_layers(tuple(branch)) for branch in middle]
    layers: list[tuple[int, tuple[int, ...]]] = [(0, first)]
    for first_branch, second_branch in zip(*branches, strict=True):
        if first_branch[0] != second_branch[0]:
            raise RuntimeError("recursive permutation switches disagree on target order")
        truth = tuple(value for pair in zip(first_branch[1], second_branch[1], strict=True) for value in pair)
        layers.append((first_branch[0] + 1, truth))
    layers.append((0, last))
    return tuple(layers)


@lru_cache(maxsize=5)
def _cube_distances(
    width: int,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    if not 0 <= width < MAX_TARGET_FLIP_WIDTH:
        raise ValueError("exact cube search supports zero through four predicate variables")
    predicate_size = 1 << width
    cubes = tuple(
        (mask, control_state)
        for mask in range(predicate_size)
        for control_state in range(predicate_size)
        if control_state & ~mask == 0
    )
    truth_masks = tuple(
        sum(int(input_value & mask == control_state) << input_value for input_value in range(predicate_size))
        for mask, control_state in cubes
    )
    costs = tuple(CONTROLLED_CX_COST[mask.bit_count()] for mask, _ in cubes)
    unreachable = predicate_size * CONTROLLED_CX_COST[width] + 1
    distances = [unreachable] * (1 << predicate_size)
    distances[0] = 0
    frontier = [(0, 0)]
    while frontier:
        distance, truth_mask = heappop(frontier)
        if distance != distances[truth_mask]:
            continue
        for cube_truth, cost in zip(truth_masks, costs, strict=True):
            neighbor = truth_mask ^ cube_truth
            alternative = distance + cost
            if alternative < distances[neighbor]:
                distances[neighbor] = alternative
                heappush(frontier, (alternative, neighbor))
    if unreachable in distances:
        raise RuntimeError("complete XOR-cube dictionary left an unreachable Boolean predicate")
    return cubes, truth_masks, costs, tuple(distances)


@lru_cache(maxsize=1024)
def _predicate_cubes(truth: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    """Choose a canonical shortest XOR-cube path through the full truth graph."""
    size = len(truth)
    if size == 0 or size & (size - 1) or any(value not in (0, 1) for value in truth):
        raise ValueError("cube synthesis requires a power-of-two binary truth table")
    cubes, truth_masks, costs, distances = _cube_distances(size.bit_length() - 1)
    remainder = sum(value << input_value for input_value, value in enumerate(truth))
    selected: list[tuple[int, int]] = []
    while remainder:
        for cube, cube_truth, cost in zip(cubes, truth_masks, costs, strict=True):
            reduced = remainder ^ cube_truth
            if cost + distances[reduced] == distances[remainder]:
                selected.append(cube)
                remainder = reduced
                break
        else:
            raise RuntimeError("minimum-cost cube path lost its strictly descending witness")
    reconstructed = tuple(
        sum(input_value & mask == control_state for mask, control_state in selected) % 2 for input_value in range(size)
    )
    if reconstructed != truth or selected != sorted(set(selected)):
        raise RuntimeError("canonical XOR cubes disagree with the complete switch predicate")
    return tuple(selected)


def _reencode(permutation: tuple[int, ...], ordering: tuple[int, ...]) -> tuple[int, ...]:
    encoded = [
        sum(((input_value >> local_bit) & 1) << actual_bit for local_bit, actual_bit in enumerate(ordering))
        for input_value in range(len(permutation))
    ]
    decoded = [0] * len(permutation)
    for local_value, actual_value in enumerate(encoded):
        decoded[actual_value] = local_value
    return tuple(decoded[permutation[actual_value]] for actual_value in encoded)


def _ordered_network(permutation: tuple[int, ...], ordering: tuple[int, ...]) -> tuple[TargetCube, ...]:
    result: list[TargetCube] = []
    for target, truth in _switch_layers(_reencode(permutation, ordering)):
        other_bits = [actual_bit for local_bit, actual_bit in enumerate(ordering) if local_bit != target]
        for local_mask, local_state in _predicate_cubes(truth):
            control_mask = sum(
                1 << actual_bit for index, actual_bit in enumerate(other_bits) if local_mask & (1 << index)
            )
            control_state = sum(
                1 << actual_bit for index, actual_bit in enumerate(other_bits) if local_state & (1 << index)
            )
            result.append(TargetCube(ordering[target], control_mask, control_state))
    return tuple(result)


def apply_network(network: tuple[TargetCube, ...], input_value: int) -> int:
    """Evaluate integer target flips independently of circuit gate synthesis."""
    for cube in network:
        input_value = cube.apply(input_value)
    return input_value


def _network_key(network: tuple[TargetCube, ...]) -> tuple[int, int, tuple[tuple[int, int, int], ...]]:
    return (
        sum(CONTROLLED_CX_COST[cube.control_mask.bit_count()] for cube in network),
        len(network),
        tuple((cube.target, cube.control_mask, cube.control_state) for cube in network),
    )


@lru_cache(maxsize=128)
def target_flip_network(permutation: tuple[int, ...]) -> tuple[TargetCube, ...]:
    """Choose an exact network among all bit orders and reversed inverse networks.

    The CX surrogate counts phase-controlled exact gates before routing. The
    finite search optimizes that surrogate within the chosen switch
    factorizations; the search makes no globally optimal circuit claim.
    """
    size = len(permutation)
    if size < 2 or size & (size - 1) or set(permutation) != set(range(size)):
        raise ValueError("target-flip synthesis requires a complete power-of-two permutation")
    width = size.bit_length() - 1
    if width > MAX_TARGET_FLIP_WIDTH:
        raise ValueError(f"target-flip synthesis supports at most {MAX_TARGET_FLIP_WIDTH} data qubits, got {width}")
    inverse = [0] * size
    for input_value, output_value in enumerate(permutation):
        inverse[output_value] = input_value
    candidates = (
        network
        for ordering in permutations(range(width))
        for network in (
            _ordered_network(permutation, ordering),
            tuple(reversed(_ordered_network(tuple(inverse), ordering))),
        )
    )
    selected = min(candidates, key=_network_key)
    if tuple(apply_network(selected, input_value) for input_value in range(size)) != permutation:
        raise RuntimeError("selected target-flip network disagrees with the complete permutation")
    return selected


def _verify() -> None:
    import random

    from modular_arithmetic import modular_permutation

    for width in range(MAX_TARGET_FLIP_WIDTH):
        _, truth_masks, costs, distances = _cube_distances(width)
        for truth_mask, distance in enumerate(distances):
            tight_edge = truth_mask == 0
            for cube_truth, cost in zip(truth_masks, costs, strict=True):
                neighbor_distance = distances[truth_mask ^ cube_truth]
                if distance > cost + neighbor_distance:
                    raise RuntimeError("cube-distance witness violates a shortest-path lower bound")
                tight_edge |= distance == cost + neighbor_distance
            if not tight_edge:
                raise RuntimeError("cube-distance witness lacks a descending optimum path")
    checked = 0
    for permutation in permutations(range(4)):
        network = target_flip_network(permutation)
        if tuple(apply_network(network, input_value) for input_value in range(4)) != permutation:
            raise RuntimeError("two-bit permutation witness failed")
        checked += 1
    generator = random.Random(20261010)
    for width in range(3, MAX_TARGET_FLIP_WIDTH + 1):
        for _ in range(4):
            shuffled = list(range(1 << width))
            generator.shuffle(shuffled)
            network = target_flip_network(tuple(shuffled))
            if tuple(apply_network(network, input_value) for input_value in range(1 << width)) != tuple(shuffled):
                raise RuntimeError("seeded permutation witness failed")
            checked += 1
    for multiplier in (2, 4, 16):
        permutation = modular_permutation(21, multiplier)
        network = target_flip_network(permutation)
        if tuple(apply_network(tuple(reversed(network)), output_value) for output_value in permutation) != tuple(
            range(32)
        ):
            raise RuntimeError("reversed target-flip network failed its inverse witness")
        mutation = network[1:]
        if tuple(apply_network(mutation, input_value) for input_value in range(32)) == permutation:
            raise RuntimeError("removing a required target flip escaped the exact permutation verifier")
        checked += 1
    for invalid in ((), (0,), (0, 0), (1, 2), tuple(range(64))):
        try:
            target_flip_network(invalid)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"target-flip synthesis accepted out-of-domain permutation of size {len(invalid)}")
    print(f"target flips: {checked} exact finite permutation witnesses; inverse and gate-deletion falsifiers pass")


if __name__ == "__main__":
    _verify()
