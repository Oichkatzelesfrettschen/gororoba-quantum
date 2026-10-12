"""Disjoint replica placement and packing of compiled circuits.

A compiled group occupies a pattern: the physical qubits its ISA circuits touch
and the CZ edges between them. Every subgraph-isomorphic embedding of that
pattern in the backend's CZ coupling graph runs the identical gate sequence on
other hardware, so a replica differs from the compiled original only in the
qubits it occupies. The placement policy separates same-group replicas by one
hop in the admitted routing graph; cross-group buffering also follows the
physical couplers, including excluded edges. Each replica carries its own
classical registers, named by a replica prefix, so one shot yields a labeled
outcome per replica and the registers recover per-replica distributions.
Disjoint registers and separated qubits do not establish statistical
independence; inference must state its dependence assumptions.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

import rustworkx as rx
from qiskit import ClassicalRegister, QuantumCircuit

Op = tuple[str, tuple[int, ...]]


@dataclass(frozen=True)
class Replica:
    """One placement: base physical qubit -> replica physical qubit, its score, and its register prefix."""

    index: int
    mapping: dict[int, int]
    score: float

    @property
    def prefix(self) -> str:
        return f"r{self.index}_"

    @property
    def qubits(self) -> list[int]:
        return sorted(self.mapping.values())


def coupling_graph(target: object, num_qubits: int) -> rx.PyGraph:
    """Undirected graph of the target's CZ couplers over every physical qubit."""
    graph = rx.PyGraph()
    graph.add_nodes_from(range(num_qubits))
    edges = {tuple(sorted(qargs)) for qargs in target["cz"]}  # type: ignore[index]
    graph.add_edges_from_no_data(sorted(edges))
    return graph


def pattern(ops: Iterable[Op]) -> tuple[list[int], set[tuple[int, int]]]:
    """Qubits and undirected two-qubit edges the operations touch."""
    qubits: set[int] = set()
    edges: set[tuple[int, int]] = set()
    for _, qargs in ops:
        qubits.update(qargs)
        if len(qargs) == 2:
            a, b = sorted(qargs)
            edges.add((a, b))
    return sorted(qubits), edges


def place(
    used: list[int],
    edges: set[tuple[int, int]],
    graph: rx.PyGraph,
    admissible: Callable[[dict[int, int]], bool],
    score: Callable[[dict[int, int]], float],
    floor: float,
    max_replicas: int | None,
) -> list[Replica]:
    """Best-first disjoint embeddings of the pattern, each scoring at least floor times the best.

    Every embedding is a candidate, the identity included, so replica 0 is the
    best-scoring placement of the compiled pattern rather than the transpiler's
    own. Candidates rank by score, ties broken by mapping, and a candidate is
    taken when its qubits avoid every taken replica and its neighbors. The
    floor stops placement at the first candidate below floor times the best
    score, so an added replica never sits on hardware much worse than the best.
    """
    candidates = candidate_replicas(
        used, edges, graph, lambda mapping: score(mapping) if admissible(mapping) else None, floor
    )
    chosen: list[Replica] = []
    blocked: set[int] = set()
    for candidate in candidates:
        if max_replicas is not None and len(chosen) >= max_replicas:
            break
        qubits = set(candidate.qubits)
        if qubits & blocked:
            continue
        chosen.append(Replica(len(chosen), candidate.mapping, candidate.score))
        blocked |= qubits | {neighbor for qubit in qubits for neighbor in graph.neighbors(qubit)}
    return chosen


def candidate_replicas(
    used: list[int],
    edges: set[tuple[int, int]],
    graph: rx.PyGraph,
    evaluate: Callable[[dict[int, int]], float | None],
    floor: float,
    mapper: Callable[[Callable[[dict[int, int]], float | None], list[dict[int, int]]], list[float | None]]
    | None = None,
) -> list[Replica]:
    """Every admissible embedding at the score floor, in deterministic best-first order.

    evaluate returns an embedding's score, or None when the embedding is
    inadmissible. mapper applies evaluate to every embedding in order; an
    order-preserving parallel map leaves the result unchanged.
    """
    small = rx.PyGraph()
    small.add_nodes_from(used)
    pattern_index = {qubit: index for index, qubit in enumerate(used)}
    small.add_edges_from_no_data([(pattern_index[first], pattern_index[second]) for first, second in sorted(edges)])
    mappings = [
        {used[small_node]: big_node for big_node, small_node in found.items()}
        for found in rx.vf2_mapping(graph, small, subgraph=True, induced=False, id_order=True)
    ]
    scores = mapper(evaluate, mappings) if mapper is not None else [evaluate(mapping) for mapping in mappings]
    candidates = [
        (value, tuple(sorted(mapping.items())))
        for mapping, value in zip(mappings, scores, strict=True)
        if value is not None
    ]
    candidates.sort(key=lambda item: (-item[0], item[1]))
    if not candidates:
        return []
    threshold = floor * candidates[0][0]
    return [Replica(index, dict(items), value) for index, (value, items) in enumerate(candidates) if value >= threshold]


def relabel(isa: QuantumCircuit, mapping: dict[int, int], prefix: str, name: str | None = None) -> QuantumCircuit:
    """isa moved onto mapping's qubits, its classical registers renamed with prefix.

    Barriers keep only the qubits in mapping, so a barrier spanning the full
    width never couples a replica to the others. compose carries each
    control-flow condition to the renamed registers.
    """
    width = isa.num_qubits
    trimmed = isa.copy_empty_like()
    for inst in isa.data:
        if inst.operation.name == "barrier":
            kept = [q for q in inst.qubits if isa.find_bit(q).index in mapping]
            if kept:
                trimmed.barrier(kept)
            continue
        trimmed.append(inst)
    targets = set(mapping.values())
    spare_sources = [q for q in range(width) if q not in mapping]
    spare_targets = [q for q in range(width) if q not in targets]
    perm = [0] * width
    for source, target in mapping.items():
        perm[source] = target
    for source, target in zip(spare_sources, spare_targets, strict=True):
        perm[source] = target
    out = QuantumCircuit(*isa.qregs, name=name or isa.name)
    registers = [ClassicalRegister(register.size, prefix + register.name) for register in isa.cregs]
    for register in registers:
        out.add_register(register)
    out.compose(trimmed, qubits=perm, clbits=[bit for register in registers for bit in register], inplace=True)
    return out


def pack(isa: QuantumCircuit, replicas: Sequence[Replica], name: str) -> QuantumCircuit:
    """One circuit running isa once per replica, each on its own qubits and registers.

    Every replica's body precedes every replica's terminal measurements -- the
    trailing run of measurements and barriers of isa's instruction list -- so
    a packed static circuit keeps all its measurements after all its gates and
    stays static; replicas share no qubit or clbit, so the reordering leaves
    each replica's computation unchanged.
    """
    tail_start = _measurement_tail_start(isa)
    out = QuantumCircuit(*isa.qregs, name=name)
    moved = [relabel(isa, replica.mapping, replica.prefix) for replica in replicas]
    for circuit in moved:
        out.global_phase += circuit.global_phase
        for register in circuit.cregs:
            out.add_register(register)
    for part in (slice(0, tail_start), slice(tail_start, None)):
        for circuit in moved:
            piece = circuit.copy_empty_like()
            # The output owns each replica's phase once across both slices.
            piece.global_phase = 0
            for inst in circuit.data[part]:
                piece.append(inst)
            out.compose(piece, qubits=range(isa.num_qubits), clbits=circuit.clbits, inplace=True)
    return out


def fuse(circuits: Sequence[QuantumCircuit], prefixes: Sequence[str], name: str) -> QuantumCircuit:
    """Compose disjoint packed circuits into one PUB with namespaced result registers.

    Every component keeps its physical qubit indices. Classical register names
    receive the corresponding prefix, which makes every result field unique.
    All component bodies precede all terminal measurements so fusing static
    circuits cannot turn the PUB into a dynamic circuit.
    """
    if not circuits or len(circuits) != len(prefixes):
        raise ValueError("PUB fusion needs equally many non-empty circuits and prefixes")
    if len(set(prefixes)) != len(prefixes) or any(not prefix for prefix in prefixes):
        raise ValueError(f"PUB fusion prefixes must be unique and non-empty: {list(prefixes)}")
    width = circuits[0].num_qubits
    occupied: set[int] = set()
    namespaced: list[QuantumCircuit] = []
    for circuit, prefix in zip(circuits, prefixes, strict=True):
        if circuit.num_qubits != width:
            raise ValueError(f"{name}: component {circuit.name} has width {circuit.num_qubits}, expected {width}")
        physical = {circuit.find_bit(qubit).index for instruction in circuit.data for qubit in instruction.qubits}
        overlap = occupied.intersection(physical)
        if overlap:
            raise ValueError(f"{name}: component {circuit.name} overlaps fused qubits {sorted(overlap)}")
        occupied.update(physical)
        if sum(register.size for register in circuit.cregs) != circuit.num_clbits:
            raise ValueError(f"{name}: component {circuit.name} has classical bits outside named registers")
        renamed = QuantumCircuit(*circuit.qregs, name=circuit.name)
        registers = [ClassicalRegister(register.size, prefix + register.name) for register in circuit.cregs]
        for register in registers:
            renamed.add_register(register)
        renamed.compose(
            circuit,
            qubits=range(width),
            clbits=[bit for register in registers for bit in register],
            inplace=True,
        )
        namespaced.append(renamed)

    out = QuantumCircuit(*circuits[0].qregs, name=name)
    for circuit in namespaced:
        out.global_phase += circuit.global_phase
        for register in circuit.cregs:
            out.add_register(register)
    tail_starts = [_measurement_tail_start(circuit) for circuit in namespaced]
    for tail in (False, True):
        for circuit, tail_start in zip(namespaced, tail_starts, strict=True):
            part = slice(tail_start, None) if tail else slice(0, tail_start)
            piece = circuit.copy_empty_like()
            # The output owns each component's phase once across both slices.
            piece.global_phase = 0
            for instruction in circuit.data[part]:
                piece.append(instruction)
            out.compose(piece, qubits=range(width), clbits=circuit.clbits, inplace=True)
    return out


def extract(circuit: QuantumCircuit, prefix: str, qubits: Iterable[int], name: str) -> QuantumCircuit:
    """Extract one namespaced fusion component while retaining its register objects."""
    own = set(qubits)
    kept = [register for register in circuit.cregs if register.name.startswith(prefix)]
    if not kept:
        raise ValueError(f"{circuit.name}: no classical register carries component prefix {prefix!r}")
    out = QuantumCircuit(*circuit.qregs, *kept, name=name)
    allowed = {bit for register in kept for bit in register}
    for instruction in circuit.data:
        indices = {circuit.find_bit(qubit).index for qubit in instruction.qubits}
        if not indices or not indices <= own:
            continue
        if any(bit not in allowed for bit in instruction.clbits):
            raise ValueError(f"{circuit.name}: component {prefix} writes another component's bits")
        out.append(instruction.operation, instruction.qubits, instruction.clbits)
    return out


def _measurement_tail_start(circuit: QuantumCircuit) -> int:
    """Index of the trailing measurement-and-barrier run."""
    tail_start = len(circuit.data)
    while tail_start > 0 and circuit.data[tail_start - 1].operation.name in ("measure", "barrier"):
        tail_start -= 1
    return tail_start


def registers(circuit: QuantumCircuit, prefix: str) -> list[str]:
    """Names of circuit's classical registers carrying prefix, in circuit order."""
    return [register.name for register in circuit.cregs if register.name.startswith(prefix)]


def split(packed: QuantumCircuit, prefix: str, qubits: Iterable[int], name: str | None = None) -> QuantumCircuit:
    """The single replica of packed on qubits whose registers carry prefix.

    The result holds every instruction confined to those qubits and only that
    replica's registers, so its clbit order is the replica's register order and
    its distribution has the width of one replica.
    """
    own = set(qubits)
    kept = [register for register in packed.cregs if register.name.startswith(prefix)]
    if not kept:
        raise ValueError(f"{packed.name}: no classical register carries prefix {prefix!r}")
    out = QuantumCircuit(*packed.qregs, *kept, name=name or packed.name)
    allowed = {bit for register in kept for bit in register}
    for inst in packed.data:
        indices = {packed.find_bit(q).index for q in inst.qubits}
        if not indices or not indices <= own:
            continue
        if any(bit not in allowed for bit in inst.clbits):
            raise ValueError(f"{packed.name}: instruction on replica {prefix} writes another replica's bits")
        out.append(inst.operation, inst.qubits, inst.clbits)
    return out
