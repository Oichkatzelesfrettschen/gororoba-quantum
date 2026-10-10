"""Disjoint replica placement and packing of compiled circuits.

A compiled group occupies a pattern: the physical qubits its ISA circuits touch
and the CZ edges between them. Every subgraph-isomorphic embedding of that
pattern in the backend's CZ coupling graph runs the identical gate sequence on
other hardware, so a replica differs from the compiled original only in the
qubits it occupies. Replicas sit on disjoint qubit sets separated by at least
one qubit, which leaves no CZ coupler between two replicas; each carries its
own classical registers, named by a replica prefix, so one shot yields one
independent sample per replica and the registers split the result back into
per-replica distributions.
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
    small = rx.PyGraph()
    small.add_nodes_from(used)
    index = {q: i for i, q in enumerate(used)}
    small.add_edges_from_no_data([(index[a], index[b]) for a, b in sorted(edges)])
    candidates: list[tuple[float, tuple[tuple[int, int], ...]]] = []
    for found in rx.vf2_mapping(graph, small, subgraph=True, induced=False, id_order=True):
        mapping = {used[small_node]: big_node for big_node, small_node in found.items()}
        if admissible(mapping):
            candidates.append((score(mapping), tuple(sorted(mapping.items()))))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    chosen: list[Replica] = []
    blocked: set[int] = set()
    for value, items in candidates:
        if max_replicas is not None and len(chosen) >= max_replicas:
            break
        if value < floor * candidates[0][0]:
            break
        mapping = dict(items)
        qubits = set(mapping.values())
        if qubits & blocked:
            continue
        chosen.append(Replica(len(chosen), mapping, value))
        blocked |= qubits | {n for q in qubits for n in graph.neighbors(q)}
    return chosen


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
    """One circuit running isa once per replica, each on its own qubits and registers."""
    out = QuantumCircuit(*isa.qregs, name=name)
    for replica in replicas:
        moved = relabel(isa, replica.mapping, replica.prefix)
        for register in moved.cregs:
            out.add_register(register)
        out.compose(moved, qubits=range(isa.num_qubits), clbits=moved.clbits, inplace=True)
    return out


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
