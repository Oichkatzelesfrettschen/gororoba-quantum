"""Heron r2 guard-banded tiling, wide-circuit composition and Target duration arithmetic.

HeronLattice reads one backend of the retained Target snapshot
(docs/evidence/heron_platform/targets.json): CZ, RZZ, SX and readout errors and
durations, the coupling graph, the default repetition delay and its legal
range. find_disjoint_tiles packs connected k-qubit tiles whose pairwise graph
distance is at least min_buffer_distance, and build_multiplexed_pub composes
one circuit per tile into one wide circuit, rejecting any two-qubit gate that
lands off its tile's induced edges. Duration and shot-rate figures are
arithmetic on Target values; nothing here schedules a circuit on a backend
or measures a throughput.

Primary research literature grounding:
- Spatial multiprogramming & crosstalk guard bands: Sarovar et al. (2020, arXiv:1908.09855),
  Niu & Todri-Sanial (2021, arXiv:2102.05321; 2023, arXiv:2112.00387), Gambetta et al.
  (2012, arXiv:1204.6308), Das et al. (2019, ASPLOS).
- Non-associative Cayley-Dickson witnesses & singular sectors: Freedman et al. (2019,
  arXiv:1811.08580), Biss et al. (2009, arXiv:0905.2987), Moreno (1998, math/9710228).
- Octonionic Fano-plane CSS & active vs coherent stabilizers: Levratti (2026, fano-css &
  active-stabilizers), Corcoles et al. (2021, arXiv:2102.01682), Rudinger et al. (2021,
  arXiv:2103.03008).
- Bounded model discrimination: Hoeffding (1963, JASA 58:13-30), Bretagnolle-Huber-Carol
  multinomial total variation bound (Bretagnolle, Huber & Carol 1979; van der Vaart & Wellner
  1996, Proposition A.6.6; Devroye 1987, Theorem 2.1; Devroye, Gyorfi & Lugosi 1996, Theorem 3.1).
- Boolean bent hidden shifts & polar rank: Roetteler (2008, arXiv:0811.3208; 2009,
  arXiv:0911.4724), Gavinsky, Ito & Roetteler (2011, arXiv:1103.3017).
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
import rustworkx as rx
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.circuit import Clbit, Parameter, Qubit
from qiskit.transpiler import CouplingMap

from boolean_anf import quadratic_polar_rank
from cd_core import basis, cd_multiply, triple_sign
from designs import design_c_associator_spectrum, lcu_witness, left_mult_gate

HERON_BASIS = ("cz", "rz", "sx", "x")
ROUTING_SEED = 20261015


@dataclass
class DisjointTile:
    """Connected k-qubit placement with its induced couplers and guard qubits.

    `serial_duration_ns` is one SX layer, every internal CZ in series, then the
    slowest readout, all from Target durations: a serial bound for one round,
    not a scheduled circuit.
    """

    tile_id: int
    qubits: list[int]
    internal_edges: list[tuple[int, int]]
    buffer_qubits: list[int]
    avg_cz_error: float
    avg_readout_error: float
    avg_sx_error: float
    esp: float
    serial_duration_ns: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "tile_id": self.tile_id,
            "qubits": self.qubits,
            "internal_edges": [list(e) for e in self.internal_edges],
            "buffer_qubits": self.buffer_qubits,
            "avg_cz_error": round(self.avg_cz_error, 6),
            "avg_readout_error": round(self.avg_readout_error, 6),
            "avg_sx_error": round(self.avg_sx_error, 6),
            "esp": round(self.esp, 6),
            "serial_duration_ns": round(self.serial_duration_ns, 2),
        }


@dataclass
class TilePlan:
    """Tiles of one size packed at one guard distance on one backend."""

    name: str
    qubits_per_tile: int
    requested_tiles: int
    min_buffer_distance: int
    tiles: list[DisjointTile]

    @property
    def active_qubits(self) -> int:
        return sum(len(t.qubits) for t in self.tiles)

    def to_dict(self, total_qubits: int) -> dict[str, Any]:
        return {
            "name": self.name,
            "qubits_per_tile": self.qubits_per_tile,
            "requested_tiles": self.requested_tiles,
            "packed_tiles": len(self.tiles),
            "min_buffer_distance": self.min_buffer_distance,
            "active_qubits": self.active_qubits,
            "chip_active_fraction": round(self.active_qubits / total_qubits, 4),
            "tiles": [t.to_dict() for t in self.tiles],
        }


@dataclass
class SubsequenceFlag:
    """An rz, cz, sx-or-x run on one qubit line of a coupler above the CZ error threshold."""

    qubits: list[int]
    gate_sequence: list[str]
    cz_error: float

    def to_dict(self) -> dict[str, Any]:
        return {"qubits": self.qubits, "gate_sequence": self.gate_sequence, "cz_error": round(self.cz_error, 6)}


def _edge(a: int, b: int) -> tuple[int, int]:
    return (min(a, b), max(a, b))


def _two_qubit_pairs(circuit: QuantumCircuit, qubit_map: dict[Qubit, int]) -> Iterator[tuple[str, int, int]]:
    """Local index pairs of every two-qubit operation, control-flow bodies included.

    A control-flow instruction's body circuits bind their qubits positionally to
    the instruction's qubits. An operation on three or more qubits other than a
    barrier raises, since it has no single coupler to land on.
    """
    for inst in circuit.data:
        op = inst.operation
        if op.name == "barrier":
            continue
        local = [qubit_map[q] for q in inst.qubits]
        blocks = getattr(op, "blocks", ())
        if blocks:
            for block in blocks:
                yield from _two_qubit_pairs(block, dict(zip(block.qubits, local, strict=True)))
            continue
        if len(local) == 2:
            yield op.name, local[0], local[1]
        elif len(local) > 2:
            raise ValueError(f"{op.name} acts on {len(local)} qubits; route the circuit to its tile first")


class HeronLattice:
    """Coupling graph and calibration of one Heron r2 backend from the Target snapshot."""

    def __init__(self, backend_name: str, target_dict: dict[str, Any]) -> None:
        self.backend_name = backend_name
        self.num_qubits = int(target_dict["num_qubits"])
        self.default_rep_delay_s = float(target_dict["default_rep_delay"])
        low, high = target_dict["rep_delay_range"]
        self.rep_delay_range_s = (float(low), float(high))
        instructions = target_dict["instructions"]
        fractional = target_dict.get("fractional_instructions", {})
        self.cz_errors, self.cz_durations = self._edge_table(instructions["cz"])
        self.rzz_errors, self.rzz_durations = self._edge_table(fractional["rzz"]) if "rzz" in fractional else ({}, {})
        self.sx_errors, self.sx_durations = self._qubit_table(instructions["sx"])
        self.x_durations = self._qubit_durations(instructions["x"])
        self.readout_errors, self.readout_durations = self._qubit_table(instructions["measure"])
        self.durations = {
            name: self._qubit_durations(instructions[name])
            for name in ("measure", "measure_2", "reset", "reset_2")
            if name in instructions
        }
        self.graph = rx.PyGraph()
        self.graph.add_nodes_from(range(self.num_qubits))
        self.graph.add_edges_from_no_data(sorted(self.cz_errors))
        self._distance: np.ndarray | None = None

    @classmethod
    def from_snapshot(cls, snapshot_path: Path | str, backend_name: str = "ibm_fez") -> HeronLattice:
        data = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
        if backend_name not in data["backends"]:
            raise ValueError(f"Backend {backend_name} not found in snapshot {snapshot_path}")
        return cls(backend_name, data["backends"][backend_name])

    @staticmethod
    def _edge_table(entry: dict[str, list[Any]]) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], float]]:
        """Worst of the two directions of each undirected coupler, error and duration."""
        errors: dict[tuple[int, int], float] = {}
        durations: dict[tuple[int, int], float] = {}
        for qargs, dur, err in zip(entry["qargs"], entry["duration"], entry["error"], strict=True):
            edge = _edge(*qargs)
            errors[edge] = max(errors.get(edge, 0.0), float(err))
            durations[edge] = max(durations.get(edge, 0.0), float(dur))
        return errors, durations

    @staticmethod
    def _qubit_durations(entry: dict[str, list[Any]]) -> dict[int, float]:
        return {int(q[0]): float(d) for q, d in zip(entry["qargs"], entry["duration"], strict=True)}

    @classmethod
    def _qubit_table(cls, entry: dict[str, list[Any]]) -> tuple[dict[int, float], dict[int, float]]:
        errors = {int(q[0]): float(e) for q, e in zip(entry["qargs"], entry["error"], strict=True)}
        return errors, cls._qubit_durations(entry)

    def distance_matrix(self) -> np.ndarray:
        if self._distance is None:
            self._distance = np.asarray(rx.distance_matrix(self.graph), dtype=np.int64)
        return self._distance

    def tile_esp(self, qubits: Sequence[int], edges: Sequence[tuple[int, int]]) -> float:
        """Product of (1 - readout error)(1 - SX error) over qubits and (1 - CZ error) over edges."""
        prob = 1.0
        for q in qubits:
            prob *= (1.0 - self.readout_errors[q]) * (1.0 - self.sx_errors[q])
        for e in edges:
            prob *= 1.0 - self.cz_errors[e]
        return prob

    def buffer_qubits(self, qubits: Sequence[int], min_buffer_distance: int) -> list[int]:
        """Qubits outside the tile closer to it than min_buffer_distance: the guard band."""
        dist = self.distance_matrix()
        inside = set(qubits)
        near = np.min(dist[list(qubits)], axis=0) < min_buffer_distance
        return [int(q) for q in np.flatnonzero(near) if int(q) not in inside]

    def induced_edges(self, qubits: Sequence[int]) -> list[tuple[int, int]]:
        inside = set(qubits)
        return sorted({_edge(u, v) for u in qubits for v in self.graph.neighbors(u) if v in inside})

    def find_disjoint_tiles(
        self,
        k: int,
        min_buffer_distance: int = 2,
        max_tiles: int | None = None,
        min_esp_floor: float = 0.5,
    ) -> list[DisjointTile]:
        """Greedy best-ESP packing of connected k-qubit tiles at pairwise graph distance >= min_buffer_distance.

        A breadth-first tree from every qubit, widening through its lowest-error
        couplers, gives one candidate per start; candidates below min_esp_floor
        drop out unless none remain. A candidate is accepted when none of its
        qubits lies within min_buffer_distance - 1 hops of an accepted tile, so
        distance 2 leaves one idle qubit between tiles and distance 3 leaves two.
        """
        if k < 1:
            raise ValueError(f"tile size must be positive, got {k}")
        if min_buffer_distance < 1:
            raise ValueError(f"min_buffer_distance must be at least 1, got {min_buffer_distance}")
        dist = self.distance_matrix()
        all_candidates: list[tuple[float, list[int]]] = []
        for start in range(self.num_qubits):
            comp = [start]
            tree_edges: list[tuple[int, int]] = []
            frontier = [start]
            seen = {start}
            while frontier and len(comp) < k:
                curr = frontier.pop(0)
                for n in sorted(self.graph.neighbors(curr), key=lambda n: self.cz_errors[_edge(curr, n)]):
                    if n not in seen:
                        seen.add(n)
                        comp.append(n)
                        tree_edges.append(_edge(curr, n))
                        frontier.append(n)
                        if len(comp) == k:
                            break
            if len(comp) == k:
                all_candidates.append((self.tile_esp(comp, tree_edges), comp))
        pool = [c for c in all_candidates if c[0] >= min_esp_floor] or all_candidates
        pool.sort(key=lambda item: -item[0])

        tiles: list[DisjointTile] = []
        blocked = np.zeros(self.num_qubits, dtype=bool)
        for esp, comp in pool:
            if max_tiles is not None and len(tiles) >= max_tiles:
                break
            if blocked[comp].any():
                continue
            qubits = sorted(comp)
            edges = self.induced_edges(qubits)
            serial_s = (
                max(self.sx_durations[q] for q in qubits)
                + sum(self.cz_durations[e] for e in edges)
                + max(self.readout_durations[q] for q in qubits)
            )
            tiles.append(
                DisjointTile(
                    tile_id=len(tiles),
                    qubits=qubits,
                    internal_edges=edges,
                    buffer_qubits=self.buffer_qubits(qubits, min_buffer_distance),
                    avg_cz_error=sum(self.cz_errors[e] for e in edges) / len(edges) if edges else 0.0,
                    avg_readout_error=sum(self.readout_errors[q] for q in qubits) / len(qubits),
                    avg_sx_error=sum(self.sx_errors[q] for q in qubits) / len(qubits),
                    esp=esp,
                    serial_duration_ns=serial_s * 1e9,
                )
            )
            blocked |= np.min(dist[qubits], axis=0) < min_buffer_distance
        return tiles

    def plan_tiles(self, name: str, k: int, requested_tiles: int, min_buffer_distance: int = 2) -> TilePlan:
        tiles = self.find_disjoint_tiles(k, min_buffer_distance=min_buffer_distance, max_tiles=requested_tiles)
        return TilePlan(name, k, requested_tiles, min_buffer_distance, tiles)

    def min_tile_distance(self, tiles: Sequence[DisjointTile]) -> int | None:
        """Smallest graph distance between qubits of different tiles; 0 when two tiles share a qubit."""
        dist = self.distance_matrix()
        best: int | None = None
        for i, a in enumerate(tiles):
            for b in tiles[i + 1 :]:
                d = int(dist[np.ix_(a.qubits, b.qubits)].min())
                best = d if best is None else min(best, d)
        return best

    def rzz_duration_summary(self) -> dict[str, Any]:
        """Native RZZ against its CZ-basis decomposition on every coupler, from Target durations.

        The decomposition is the preset transpiler's synthesis of RZZ(0.3) into
        cz, rz, sx and x on one coupler; its duration is the ASAP critical path
        with each coupler's CZ duration and each qubit's SX and X durations, rz
        being a frame change of zero duration. Logical qubit 0 of the synthesis
        sits on the coupler's lower-index qubit.
        """
        ratios: list[float] = []
        decomposed: list[float] = []
        native_equals_cz = 0
        for edge in sorted(self.rzz_durations):
            native = self.rzz_durations[edge]
            native_equals_cz += math.isclose(native, self.cz_durations[edge])
            finish = {0: 0.0, 1: 0.0}
            for name, qargs in _rzz_template():
                physical = [edge[q] for q in qargs]
                if name == "cz":
                    step = self.cz_durations[_edge(*physical)]
                elif name == "sx":
                    step = self.sx_durations[physical[0]]
                elif name == "x":
                    step = self.x_durations[physical[0]]
                else:
                    step = 0.0
                start = max(finish[q] for q in qargs)
                for q in qargs:
                    finish[q] = start + step
            total = max(finish.values())
            decomposed.append(total * 1e9)
            ratios.append(total / native)
        counts: dict[str, int] = {}
        for name, _ in _rzz_template():
            counts[name] = counts.get(name, 0) + 1
        return {
            "couplers": len(ratios),
            "rzz_duration_equals_cz": native_equals_cz,
            "decomposition_ops": dict(sorted(counts.items())),
            "sx_duration_ns": sorted({round(v * 1e9, 3) for v in self.sx_durations.values()}),
            "decomposed_ns": {
                "min": round(min(decomposed), 3),
                "median": round(median(decomposed), 3),
                "max": round(max(decomposed), 3),
            },
            "decomposed_over_native": {
                "min": round(min(ratios), 4),
                "median": round(median(ratios), 4),
                "max": round(max(ratios), 4),
            },
        }

    def shot_rate_ratio(self, circuit_duration_s: float, rep_delay_s: float) -> dict[str, float]:
        """Shot-rate ratio of rep_delay_s against the default delay at one assumed circuit duration.

        One shot cycle is the circuit duration plus the repetition delay. A delay
        inside rep_delay_range but below the default raises the state-preparation
        error (docs/notes/ibm_quantum/repetition-rate-execution.md), so the ratio is
        a rate at an unqualified operating point, never a yield.
        """
        low, high = self.rep_delay_range_s
        if not low <= rep_delay_s <= high:
            raise ValueError(f"rep_delay {rep_delay_s} outside {self.backend_name} range [{low}, {high}]")
        if circuit_duration_s <= 0:
            raise ValueError(f"circuit duration must be positive, got {circuit_duration_s}")
        default_hz = 1.0 / (circuit_duration_s + self.default_rep_delay_s)
        hz = 1.0 / (circuit_duration_s + rep_delay_s)
        return {
            "shot_rate_hz": round(hz, 1),
            "default_shot_rate_hz": round(default_hz, 1),
            "ratio": round(hz / default_hz, 4),
        }

    def high_error_couplers(self, cz_error_threshold: float) -> list[tuple[int, int]]:
        return sorted(e for e, err in self.cz_errors.items() if err > cz_error_threshold)

    def flag_rz_cz_sx(
        self,
        circuit_ops: QuantumCircuit | Sequence[tuple[str, tuple[int, ...]]],
        cz_error_threshold: float = 0.004,
    ) -> list[SubsequenceFlag]:
        """Flag rz, cz, sx-or-x runs on one qubit line of a coupler above cz_error_threshold.

        This is a pattern match with an explicit threshold, not a characterized
        Heron mechanism: no source in docs/ establishes an error for the pattern.
        Each qubit's line is its operations in circuit order; a barrier is
        skipped and a delay ends the run, since it separates the gates in time.
        """
        if isinstance(circuit_ops, QuantumCircuit):
            ops = [
                (inst.operation.name, tuple(circuit_ops.find_bit(q).index for q in inst.qubits))
                for inst in circuit_ops.data
            ]
        else:
            ops = list(circuit_ops)
        high = set(self.high_error_couplers(cz_error_threshold))
        lines: dict[int, list[tuple[str, int]]] = {}
        for idx, (name, qargs) in enumerate(ops):
            if name == "barrier":
                continue
            for q in qargs:
                lines.setdefault(q, []).append((name, idx))
        flags: list[SubsequenceFlag] = []
        seen: set[tuple[int, tuple[int, int]]] = set()
        for idx, (name, qargs) in enumerate(ops):
            if name != "cz" or len(qargs) != 2 or _edge(*qargs) not in high:
                continue
            edge = _edge(*qargs)
            for q in qargs:
                line = lines[q]
                pos = next(i for i, entry in enumerate(line) if entry[1] == idx)
                if 0 < pos < len(line) - 1 and line[pos - 1][0] == "rz" and line[pos + 1][0] in ("sx", "x"):
                    if (q, edge) not in seen:
                        seen.add((q, edge))
                        flags.append(SubsequenceFlag(list(edge), ["rz", "cz", line[pos + 1][0]], self.cz_errors[edge]))
        return flags

    def tile_coupling_map(self, tile: DisjointTile) -> CouplingMap:
        """The tile's induced couplers, both directions, relabeled to positions in tile.qubits."""
        position = {q: i for i, q in enumerate(tile.qubits)}
        pairs = [(position[a], position[b]) for a, b in tile.internal_edges]
        return CouplingMap(pairs + [(b, a) for a, b in pairs])

    def route_to_tile(self, circuit: QuantumCircuit, tile: DisjointTile, seed: int = ROUTING_SEED) -> QuantumCircuit:
        """Compile a circuit to cz, rz, sx and x with layout and routing confined to one tile.

        The result has one qubit per tile qubit, in tile.qubits order, and every
        two-qubit gate on an induced coupler, so build_multiplexed_pub places it
        without touching a guard qubit.
        """
        if circuit.num_qubits > len(tile.qubits):
            raise ValueError(
                f"{circuit.num_qubits}-qubit circuit exceeds the {len(tile.qubits)}-qubit tile {tile.tile_id}"
            )
        return transpile(
            circuit,
            coupling_map=self.tile_coupling_map(tile),
            basis_gates=list(HERON_BASIS),
            optimization_level=1,
            seed_transpiler=seed,
        )

    def build_multiplexed_pub(
        self,
        tile_circuits: Sequence[QuantumCircuit],
        tiles: Sequence[DisjointTile],
        min_buffer_distance: int = 2,
    ) -> QuantumCircuit:
        """Compose one circuit per tile into one wide circuit, each tile register renamed tile_<k>_<name>.

        Circuit qubit i lands on tile.qubits[i]. The composer rejects tiles that
        overlap or sit closer than min_buffer_distance, and any two-qubit
        operation, control-flow bodies included, that lands off its tile's
        induced couplers; route_to_tile produces circuits that pass. A
        parameter whose name another tile already uses for a different
        Parameter object is renamed tile_<k>_<name>; one Parameter object shared
        across tiles stays one parameter.
        """
        if min_buffer_distance < 1:
            raise ValueError(f"min_buffer_distance must be at least 1, got {min_buffer_distance}")
        if len(tile_circuits) != len(tiles):
            raise ValueError(f"Circuit count {len(tile_circuits)} must match tile count {len(tiles)}")
        closest = self.min_tile_distance(tiles)
        if closest is not None and closest < min_buffer_distance:
            raise ValueError(f"tiles sit at graph distance {closest}, below the guard distance {min_buffer_distance}")
        wide = QuantumCircuit(QuantumRegister(self.num_qubits, "q"), name="heron_multiplexed_pub")
        names: dict[str, Parameter] = {}
        for tile_idx, (circ, tile) in enumerate(zip(tile_circuits, tiles, strict=True)):
            if circ.num_qubits > len(tile.qubits):
                raise ValueError(
                    f"Tile circuit {tile_idx} requires {circ.num_qubits} qubits, "
                    f"but tile {tile.tile_id} has only {len(tile.qubits)}"
                )
            physical = tile.qubits[: circ.num_qubits]
            allowed = set(tile.internal_edges)
            for name, a, b in _two_qubit_pairs(circ, {q: i for i, q in enumerate(circ.qubits)}):
                if _edge(physical[a], physical[b]) not in allowed:
                    raise ValueError(
                        f"tile {tile.tile_id}: {name} on {physical[a]}, {physical[b]} is not an induced coupler"
                    )
            renames: dict[Parameter, Parameter] = {}
            for param in circ.parameters:
                owner = names.get(param.name)
                if owner is not None and owner != param:
                    candidate = f"tile_{tile_idx}_{param.name}"
                    suffix = 1
                    while candidate in names and names[candidate] != param:
                        candidate = f"tile_{tile_idx}_{param.name}_{suffix}"
                        suffix += 1
                    renames[param] = Parameter(candidate)
            placed = circ.assign_parameters(renames) if renames else circ
            for param in placed.parameters:
                names.setdefault(param.name, param)
            if placed.num_clbits == 0:
                wide.compose(placed, qubits=physical, inplace=True)
                continue
            owned = [bit for creg in placed.cregs for bit in creg]
            if len(owned) == placed.num_clbits and set(owned) == set(placed.clbits):
                sources = [(creg.name, list(creg)) for creg in placed.cregs]
            else:
                sources = [("c", list(placed.clbits))]
            clbit_map: dict[Clbit, Clbit] = {}
            for name, bits in sources:
                creg = ClassicalRegister(len(bits), f"tile_{tile_idx}_{name}")
                wide.add_register(creg)
                clbit_map.update(zip(bits, creg, strict=True))
            wide.compose(placed, qubits=physical, clbits=[clbit_map[bit] for bit in placed.clbits], inplace=True)
        return wide

    @staticmethod
    def pack_parameter_sweep_pub(
        circuit: QuantumCircuit,
        parameter_values: np.ndarray | Sequence[Sequence[float]] | Sequence[float],
        shots: int = 4096,
    ) -> tuple[QuantumCircuit, np.ndarray, int]:
        """Pack a circuit, its finite parameter values and a shot count as a Sampler PUB tuple.

        parameter_values is (N_params,) for one point or (N_sweeps, N_params) for a
        sweep with at least one row.
        """
        arr = np.asarray(parameter_values, dtype=np.float64)
        n_params = circuit.num_parameters
        if n_params == 0 and arr.size > 0:
            raise ValueError("Circuit has 0 parameters but non-empty parameter values were provided")
        if n_params > 0:
            if arr.ndim == 1:
                if len(arr) != n_params:
                    raise ValueError(f"Expected {n_params} parameter values, got shape {arr.shape}")
            elif arr.ndim == 2:
                if arr.shape[1] != n_params or arr.shape[0] == 0:
                    raise ValueError(
                        f"Expected a non-empty parameter array with second dimension {n_params}, got {arr.shape}"
                    )
            else:
                raise ValueError(f"Parameter values must be 1D or 2D array, got ndim={arr.ndim}")
        if not np.all(np.isfinite(arr)):
            raise ValueError("Parameter values must be finite")
        if shots <= 0:
            raise ValueError(f"Shot count must be positive, got {shots}")
        return (circuit, arr, shots)

    @staticmethod
    def append_basis_rotations(circuit: QuantumCircuit, bases: dict[int, str] | Sequence[str] | str) -> QuantumCircuit:
        """Rotate qubits into the X or Y basis before their terminal measurement.

        'X' inserts H, 'Y' inserts Sdg then H, 'Z' and 'I' insert nothing. Only a
        measurement with no later operation on its qubit is rotated, so a
        mid-circuit measurement stays in the Z basis. A circuit without
        measurements gets the rotations appended at the end.
        """
        n_q = circuit.num_qubits
        if isinstance(bases, str) and len(bases) == 1:
            basis_map = {q: bases.upper() for q in range(n_q)}
        elif isinstance(bases, dict):
            basis_map = {int(q): b.upper() for q, b in bases.items()}
        else:
            if len(bases) != n_q:
                raise ValueError(f"Basis length {len(bases)} does not match qubit count {n_q}")
            basis_map = {q: b.upper() for q, b in enumerate(bases)}
        for q_idx, b in basis_map.items():
            if not 0 <= q_idx < n_q:
                raise ValueError(f"Qubit index {q_idx} out of range [0, {n_q - 1}]")
            if b not in ("X", "Y", "Z", "I"):
                raise ValueError(f"Unsupported basis '{b}' on qubit {q_idx}")

        def rotate(target: QuantumCircuit, q: int) -> None:
            if basis_map.get(q, "Z") == "Y":
                target.sdg(q)
            if basis_map.get(q, "Z") in ("X", "Y"):
                target.h(q)

        last_use: dict[int, int] = {}
        for idx, inst in enumerate(circuit.data):
            if inst.operation.name != "barrier":
                for q in inst.qubits:
                    last_use[circuit.find_bit(q).index] = idx
        if not any(inst.operation.name == "measure" for inst in circuit.data):
            out = circuit.copy()
            for q in range(n_q):
                rotate(out, q)
            return out
        out = circuit.copy_empty_like()
        for idx, inst in enumerate(circuit.data):
            if inst.operation.name == "measure":
                for q in inst.qubits:
                    q_idx = circuit.find_bit(q).index
                    if last_use[q_idx] == idx:
                        rotate(out, q_idx)
            out.append(inst.operation, inst.qubits, inst.clbits)
        return out

    @staticmethod
    def tile_parity_covariance(
        bitstrings: Sequence[str] | dict[str, Sequence[str]],
        tile_clbit_slices: Sequence[slice] | None = None,
        tile_coords: Sequence[tuple[float, float]] | None = None,
        endianness: str = "big",
        unbiased: bool = False,
    ) -> dict[str, Any]:
        """Covariance of tile parities, E[P_i P_j] - E[P_i] E[P_j], with P = (-1)^(number of ones).

        Input is either one bit string per shot with one slice per tile
        ('little' reads slices from the right, Qiskit's clbit order) or one
        string list per classical register. Every string has the same length
        and every slice selects at least one bit inside it. If tile_coords is
        provided, pairwise Euclidean distance is computed alongside covariance.
        """
        if endianness not in ("big", "little"):
            raise ValueError(f"endianness must be 'big' or 'little', got '{endianness}'")
        tile_strings: list[list[str]] = []
        if isinstance(bitstrings, dict):
            if not bitstrings:
                raise ValueError("Empty dictionary provided for bitstrings")
            columns = [list(bitstrings[name]) for name in sorted(bitstrings)]
            n_shots = len(columns[0])
            for name, column in zip(sorted(bitstrings), columns, strict=True):
                if len(column) != n_shots:
                    raise ValueError(f"Shot count mismatch in register {name}")
                if not column or len({len(s) for s in column}) != 1 or not column[0]:
                    raise ValueError(f"register {name} needs non-empty strings of one length")
            tile_strings = columns
        else:
            n_shots = len(bitstrings)
            if tile_clbit_slices is None:
                raise ValueError("tile_clbit_slices is required when bitstrings is a list")
            widths = {len(s) for s in bitstrings}
            if len(widths) > 1:
                raise ValueError(f"bit strings differ in length: {sorted(widths)}")
            width = widths.pop() if widths else 0
            for sl in tile_clbit_slices:
                start, stop, _ = sl.indices(width)
                inside = (sl.start is None or 0 <= sl.start) and (sl.stop is None or 0 <= sl.stop <= width)
                if sl.step not in (None, 1) or not inside or stop <= start:
                    raise ValueError(f"slice {sl} selects no contiguous bits inside width {width}")
                if endianness == "little":
                    tile_strings.append([s[width - stop : width - start] for s in bitstrings])
                else:
                    tile_strings.append([s[start:stop] for s in bitstrings])
        if not tile_strings:
            raise ValueError("At least one tile is required")
        if n_shots < 2:
            raise ValueError("Need at least 2 shots to compute covariance")
        n_tiles = len(tile_strings)
        if tile_coords is not None and len(tile_coords) != n_tiles:
            raise ValueError(f"tile_coords length {len(tile_coords)} does not match tile count {n_tiles}")
        parity = np.array([[1.0 if s.count("1") % 2 == 0 else -1.0 for s in column] for column in tile_strings])
        means = parity.mean(axis=1)
        joint = parity @ parity.T / n_shots
        cov = (joint - np.outer(means, means)) * (n_shots / (n_shots - 1) if unbiased else 1.0)
        res: dict[str, Any] = {
            "num_shots": n_shots,
            "num_tiles": n_tiles,
            "means": [round(float(m), 4) for m in means],
            "covariance_matrix": [[round(float(v), 6) for v in row] for row in cov],
        }
        if tile_coords is not None:
            dist_matrix = [
                [round(math.hypot(c1[0] - c2[0], c1[1] - c2[1]), 4) for c2 in tile_coords] for c1 in tile_coords
            ]
            res["distance_matrix"] = dist_matrix
        return res


@cache
def _rzz_template() -> tuple[tuple[str, tuple[int, ...]], ...]:
    """Operations of RZZ(0.3) compiled to cz, rz, sx and x on one coupler."""
    qc = QuantumCircuit(2)
    qc.rzz(0.3, 0, 1)
    out = transpile(
        qc,
        coupling_map=CouplingMap([(0, 1), (1, 0)]),
        basis_gates=list(HERON_BASIS),
        optimization_level=1,
        seed_transpiler=1,
    )
    return tuple((inst.operation.name, tuple(out.find_bit(q).index for q in inst.qubits)) for inst in out.data)


def lcu_zero_product_witness(
    a_pair: tuple[int, int] = (1, 10),
    b_pair: tuple[int, int] = (4, 15),
    sign: int = -1,
) -> QuantumCircuit:
    """Design B's fixed-operand LCU for x = (e_i + e_j)/sqrt2 on y = (e_k + sign e_l)/sqrt2.

    designs.lcu_witness builds the circuit with phase 0 for sign +1 and pi for
    sign -1. cd_core.cd_multiply certifies the pair: the circuit metadata
    carries P(s = 0) = ||x y||^2 / 2, which is 0 for the default dark pair
    (e1 + e10)(e4 - e15) = 0 and 1 for its bright control at sign +1.
    """
    if sign not in (1, -1):
        raise ValueError(f"sign must be +1 or -1, got {sign}")
    (i, j), (k, el) = a_pair, b_pair
    x = [u + v for u, v in zip(basis(16, i, 1 / math.sqrt(2)), basis(16, j, 1 / math.sqrt(2)), strict=True)]
    y = [u + v for u, v in zip(basis(16, k, 1 / math.sqrt(2)), basis(16, el, sign / math.sqrt(2)), strict=True)]
    product = cd_multiply(16, x, y)
    qc = lcu_witness(a_pair, b_pair, 0.0 if sign > 0 else math.pi)
    qc.metadata = {
        "a_pair": list(a_pair),
        "b_pair": list(b_pair),
        "sign": sign,
        "p_success": sum(c * c for c in product) / 2,
    }
    return qc


def sedenion_associator_witness(i: int = 1, j: int = 2, k: int = 4) -> QuantumCircuit:
    """Hadamard associator test on sedenions, 4 data qubits + 1 control ancilla.

    Evaluates the associator defect [e_i, e_j, e_k] = (e_i e_j) e_k - e_i (e_j e_k).
    Control qubit 4 prepares |+>. Branch 0 applies L_{(e_i e_j) e_k} and branch 1
    applies L_{e_i} L_{e_j} L_{e_k}. The ancilla expectation <Z_c> after the final H
    reads Re <psi_L | psi_R> = +1 for associating triples and -1 for anti-associating
    triples, certified by cd_core.triple_sign.
    """
    for idx, name in ((i, "i"), (j, "j"), (k, "k")):
        if not 0 <= idx < 16:
            raise ValueError(f"Sedenion index {name} must be in range 0..15, got {idx}")
    left_sign, right_sign = triple_sign(16, i, j, k)
    ijk_idx = (i ^ j) ^ k

    qc = QuantumCircuit(5, 1, name=f"sedenion_associator_{i}_{j}_{k}")
    qc.h(4)

    u_left = left_mult_gate(16, ijk_idx)
    c_u_left = u_left.control(1, ctrl_state=0)
    qc.append(c_u_left, [4, 0, 1, 2, 3])
    if left_sign < 0:
        qc.x(4)
        qc.z(4)
        qc.x(4)

    c_k = left_mult_gate(16, k).control(1, ctrl_state=1)
    c_j = left_mult_gate(16, j).control(1, ctrl_state=1)
    c_i = left_mult_gate(16, i).control(1, ctrl_state=1)
    qc.append(c_k, [4, 0, 1, 2, 3])
    qc.append(c_j, [4, 0, 1, 2, 3])
    qc.append(c_i, [4, 0, 1, 2, 3])

    qc.h(4)
    qc.measure(4, 0)
    qc.metadata = {
        "triple": [i, j, k],
        "left_sign": left_sign,
        "right_sign": right_sign,
        "associates": bool(left_sign == right_sign),
        "ijk_sign": left_sign,
        "ijk_index": ijk_idx,
    }
    return qc


def pathion_associator_spectrum_witness(dim: int = 32, i: int = 1, j: int = 16) -> QuantumCircuit:
    """Design C's Walsh spectrum of W = L_{e_i e_j}^dagger L_{e_i} L_{e_j} on log2(dim) qubits.

    Applies the three left-multiplication blocks of W on a uniform superposition
    H^n |0>^n, followed by H^n before measurement to turn W's diagonal phase into
    a bitstring distribution. For dim=32, (1, 16) is the five-qubit pathion
    exemplar from designs.SPECTRUM_EXEMPLARS.
    """
    if dim <= 0 or (dim & (dim - 1)) != 0:
        raise ValueError(f"dim must be a positive power of 2, got {dim}")
    if not 0 <= i < dim:
        raise ValueError(f"Basis index i must be in range 0..{dim - 1}, got {i}")
    if not 0 <= j < dim:
        raise ValueError(f"Basis index j must be in range 0..{dim - 1}, got {j}")
    return design_c_associator_spectrum(dim, i, j)


STEANE_Z_CHECKS = ((0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6))


def fano_plane_incidence_matrix() -> np.ndarray:
    """Return the 7x7 binary incidence matrix of the projective Fano plane PG(2, 2).

    Rows are the 7 Fano lines (octonionic associative sub-triples), columns are the 7
    points corresponding to the 7 data qubits of the Steane [[7,1,3]] code.
    """
    lines = (
        (0, 1, 2),
        (0, 3, 4),
        (0, 5, 6),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 4, 5),
    )
    matrix = np.zeros((7, 7), dtype=int)
    for row_idx, line in enumerate(lines):
        for pt in line:
            matrix[row_idx, pt] = 1
    return matrix


def steane_z_syndrome_patch(
    error_qubit: int | None = None,
    mid_circuit_measure: bool = False,
    dd_sequence: str | None = None,
    idle_delay_dt: int = 0,
) -> QuantumCircuit:
    """Three Steane Z checks on 7 data qubits with feed-forward X correction, 10 qubits.

    Check b is CX from each data qubit in STEANE_Z_CHECKS[b] onto ancilla 7 + b,
    the supports {1,3,5,7}, {2,3,6,7} and {4,5,6,7} in 1-based positions, so an
    X error on data qubit d reads syndrome d + 1 in register `syn`. Seven
    unnested if_test blocks on the 3-bit register apply the X correction, and
    register `data` reads the 7 data qubits at the end.

    An optional dd_sequence ('CPMG2', 'Hahn', or 'XY4') applies dynamical decoupling to
    the data qubits bracketing idle_delay_dt during syndrome extraction to suppress
    physical dephasing drift without transversal logical perturbation. Note that
    an even number of X rotations (CPMG-2: tau/4 -> X -> tau/2 -> X -> tau/4) or
    XY4 (tau/8 -> X -> tau/4 -> Y -> tau/4 -> X -> tau/4 -> Y -> rem) is required
    because an odd number of X pulses on all 7 data qubits acts as a transversal logical
    X flip on the Steane [[7,1,3]] code, transforming |0_L> into |1_L>.
    """
    if idle_delay_dt < 0:
        raise ValueError(f"idle_delay_dt must be non-negative, got {idle_delay_dt}")
    if dd_sequence not in (None, "CPMG2", "Hahn", "XY4"):
        raise ValueError(f"Unsupported dd_sequence '{dd_sequence}'")
    syn = ClassicalRegister(3, "syn")
    data = ClassicalRegister(7, "data")
    qc = QuantumCircuit(QuantumRegister(10, "q"), syn, data, name="steane_z_syndrome_patch")
    if error_qubit is not None:
        if not 0 <= error_qubit < 7:
            raise ValueError(f"error_qubit must be a data qubit 0..6, got {error_qubit}")
        qc.x(error_qubit)
    for bit, support in enumerate(STEANE_Z_CHECKS):
        for q in support:
            qc.cx(q, 7 + bit)

    # Delay window on data qubits during syndrome extraction
    if idle_delay_dt > 0:
        if dd_sequence in ("CPMG2", "Hahn"):
            tau_4 = idle_delay_dt // 4
            tau_2 = idle_delay_dt // 2
            rem = idle_delay_dt - (2 * tau_4 + tau_2)
            for q in range(7):
                qc.delay(tau_4, q)
                qc.x(q)
                qc.delay(tau_2, q)
                qc.x(q)
                qc.delay(tau_4 + rem, q)
        elif dd_sequence == "XY4":
            tau_8 = idle_delay_dt // 8
            tau_4 = idle_delay_dt // 4
            rem = idle_delay_dt - (tau_8 + 3 * tau_4)
            for q in range(7):
                qc.delay(tau_8, q)
                qc.x(q)
                qc.delay(tau_4, q)
                qc.y(q)
                qc.delay(tau_4, q)
                qc.x(q)
                qc.delay(tau_4, q)
                qc.y(q)
                qc.delay(rem, q)
        elif dd_sequence is None:
            for q in range(7):
                qc.delay(idle_delay_dt, q)

    if mid_circuit_measure:
        from qiskit_ibm_runtime.circuit import MidCircuitMeasure

        for bit in range(3):
            qc.append(MidCircuitMeasure(), [7 + bit], [syn[bit]])
    else:
        qc.measure([7, 8, 9], syn)
    for value in range(1, 8):
        with qc.if_test((syn, value)):
            qc.x(value - 1)
    qc.measure(range(7), data)
    return qc


def steane_coherent_syndrome_patch(error_qubit: int | None = None) -> QuantumCircuit:
    """Coherent Steane Z-syndrome extraction and correction on 10 qubits (7 data, 3 ancilla).

    Applies the 3 Steane Z parity checks onto ancillas 7, 8, 9 via CX. Then, instead
    of destructive mid-circuit measurement and classical feed-forward, applies coherent
    multi-controlled X corrections on the data qubits conditioned on ancilla states via
    mcx([7, 8, 9], value - 1, ctrl_state=value).

    Corrects single X errors on data state |0>^7 coherently without mid-circuit readout
    or reset. Conceptually motivated by comparing coherent multi-control vs dynamic
    feed-forward studied in separate QPE ladder acquisitions (CAMPAIGN_FINDINGS.md Section 2).
    """
    data = ClassicalRegister(7, "data")
    qc = QuantumCircuit(QuantumRegister(10, "q"), data, name="steane_coherent_syndrome_patch")
    if error_qubit is not None:
        if not 0 <= error_qubit < 7:
            raise ValueError(f"error_qubit must be a data qubit 0..6, got {error_qubit}")
        qc.x(error_qubit)
    for bit, support in enumerate(STEANE_Z_CHECKS):
        for q in support:
            qc.cx(q, 7 + bit)
    for value in range(1, 8):
        qc.mcx([7, 8, 9], value - 1, ctrl_state=value)
    qc.measure(range(7), data)
    return qc


def bell_delay_probe(delay_dt: int = 100, dd_sequence: str | None = None) -> QuantumCircuit:
    """Bell pair with optional gap-aware dynamical decoupling, then inverse preparation, 2 qubits.

    dd_sequence supports None (plain delay), 'Hahn' (X echo at midpoint), or 'XY4'
    (symmetric CPMG-style tau/8 -> X -> tau/4 -> Y -> tau/4 -> X -> tau/4 -> Y -> rem),
    serving as an echo testbed to measure and mitigate dephasing drift during idle gaps.
    """
    if delay_dt < 0:
        raise ValueError(f"delay_dt must be non-negative, got {delay_dt}")
    if dd_sequence not in (None, "Hahn", "XY4"):
        raise ValueError(f"Unsupported dd_sequence '{dd_sequence}'")
    qc = QuantumCircuit(2, 2, name="bell_delay_probe")
    qc.h(0)
    qc.cx(0, 1)
    if delay_dt > 0:
        if dd_sequence is None:
            qc.delay(delay_dt, 0)
            qc.delay(delay_dt, 1)
        elif dd_sequence == "Hahn":
            half = delay_dt // 2
            rem = delay_dt - half
            qc.delay(half, 0)
            qc.delay(half, 1)
            qc.x(0)
            qc.x(1)
            qc.delay(rem, 0)
            qc.delay(rem, 1)
        elif dd_sequence == "XY4":
            tau_8 = delay_dt // 8
            tau_4 = delay_dt // 4
            rem = delay_dt - (tau_8 + 3 * tau_4)
            for q in (0, 1):
                qc.delay(tau_8, q)
                qc.x(q)
                qc.delay(tau_4, q)
                qc.y(q)
                qc.delay(tau_4, q)
                qc.x(q)
                qc.delay(tau_4, q)
                qc.y(q)
                qc.delay(rem, q)
        else:
            raise ValueError(f"Unsupported dd_sequence '{dd_sequence}'")
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def hoeffding_model_discrimination(
    counts_p: dict[str, int],
    counts_q: dict[str, int],
    *,
    alphabet_size: int,
    alpha: float = 0.01,
) -> dict[str, Any]:
    """Empirical Total Variation distance and JS divergence under finite-sample Hoeffding and multinomial TV bounds.

    Given two empirical count distributions over identical outcomes, computes D_TV and D_JS.
    Computes both:
    1. Single-observable Hoeffding confidence radius: r_obs = sqrt(ln(2/alpha) / (2*N_eff))
       for any fixed binary partition or parity observable in [0, 1].
    2. Simultaneous multinomial Total Variation confidence radius via Bretagnolle-Huber-Carol (1979) /
       Devroye (1987) bound over K bins:
       eps_p = sqrt(2 * (K*ln(2) + ln(4/alpha)) / n_p)
       eps_q = sqrt(2 * (K*ln(2) + ln(4/alpha)) / n_q)
       radius_tv = 0.5 * (eps_p + eps_q)
    where K is the required size of the complete outcome alphabet, including outcomes with
    zero observed counts. This prevents omitted outcomes from understating the bound.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    if not counts_p or not counts_q:
        raise ValueError("Count distributions must be non-empty")
    if any(c < 0 for c in counts_p.values()) or any(c < 0 for c in counts_q.values()):
        raise ValueError("Counts must be non-negative")
    n_p = sum(counts_p.values())
    n_q = sum(counts_q.values())
    if n_p == 0 or n_q == 0:
        raise ValueError("Total shots must be positive in both distributions")
    all_keys = sorted(set(counts_p) | set(counts_q))
    if alphabet_size <= 0:
        raise ValueError(f"alphabet_size must be positive, got {alphabet_size}")
    if alphabet_size < len(all_keys):
        raise ValueError(
            f"alphabet_size ({alphabet_size}) cannot be smaller than observed distinct outcomes ({len(all_keys)})"
        )
    k_bins = alphabet_size
    p = np.array([counts_p.get(k, 0) / n_p for k in all_keys], dtype=np.float64)
    q = np.array([counts_q.get(k, 0) / n_q for k in all_keys], dtype=np.float64)

    d_tv = float(0.5 * np.sum(np.abs(p - q)))
    m = 0.5 * (p + q)
    kl_pm = float(np.sum(p[p > 0] * np.log(p[p > 0] / m[p > 0])))
    kl_qm = float(np.sum(q[q > 0] * np.log(q[q > 0] / m[q > 0])))
    d_js = float(0.5 * (kl_pm + kl_qm))

    n_eff = min(n_p, n_q)
    radius_hoeffding = float(math.sqrt(math.log(2.0 / alpha) / (2.0 * n_eff)))

    # Simultaneous multinomial TV confidence radius (Bretagnolle-Huber-Carol / Devroye bound)
    eps_p = math.sqrt(2.0 * (k_bins * math.log(2.0) + math.log(4.0 / alpha)) / n_p)
    eps_q = math.sqrt(2.0 * (k_bins * math.log(2.0) + math.log(4.0 / alpha)) / n_q)
    radius_tv = float(0.5 * (eps_p + eps_q))

    ci_lower = max(0.0, d_tv - radius_tv)
    ci_upper = min(1.0, d_tv + radius_tv)

    return {
        "num_shots_p": n_p,
        "num_shots_q": n_q,
        "k_bins": k_bins,
        "alpha": alpha,
        "total_variation_distance": round(d_tv, 6),
        "jensen_shannon_divergence": round(d_js, 6),
        "hoeffding_radius": round(radius_hoeffding, 6),
        "multinomial_tv_radius": round(radius_tv, 6),
        "tv_confidence_interval": [round(ci_lower, 6), round(ci_upper, 6)],
        "models_distinguishable": bool(ci_lower > 0.0),
    }


def bent_hidden_shift_circuit(
    n: int = 6,
    shift: Sequence[int] | None = None,
) -> QuantumCircuit:
    """Rotteler (2010) hidden shift algorithm for quadratic Boolean bent functions.

    n must be even. Evaluates f(x) = x0*x1 ^ x2*x3 ^ ... and shifted g(x) = f(x ^ s).
    Circuit sequence H^n -> O_g -> H^n -> O_f -> H^n -> Measure deterministically
    measures the hidden shift string s with probability 1.0 in ideal execution.
    The ideal circuit is constructed from {H, CZ, Z}, compiling to native Heron ISA
    instructions {cz, rz, sx, x} after transpilation.
    """

    if n <= 0 or n % 2 != 0:
        raise ValueError(f"Qubit count n must be a positive even integer, got {n}")
    if shift is None:
        s = [1 if i % 2 == 0 else 0 for i in range(n)]
    else:
        if len(shift) != n:
            raise ValueError(f"Shift length {len(shift)} does not match n={n}")
        if any(b not in (0, 1) for b in shift):
            raise ValueError("Shift entries must be 0 or 1")
        s = list(shift)

    # Check quadratic bent rank
    monomial_masks = tuple((1 << (2 * k)) | (1 << (2 * k + 1)) for k in range(n // 2))
    polar_rank = quadratic_polar_rank(monomial_masks, n)
    if polar_rank != n:
        raise RuntimeError(f"Quadratic form is not bent: rank {polar_rank} != {n}")

    qc = QuantumCircuit(n, n, name=f"bent_hidden_shift_{n}q")
    qc.h(range(n))

    # Oracle for g(x) = f(x ^ s)
    for k in range(n // 2):
        q0 = 2 * k
        q1 = 2 * k + 1
        qc.cz(q0, q1)
        if s[q1]:
            qc.z(q0)
        if s[q0]:
            qc.z(q1)
        if s[q0] and s[q1]:
            qc.global_phase += math.pi

    qc.h(range(n))

    # Dual oracle O_f~ = O_f
    for k in range(n // 2):
        qc.cz(2 * k, 2 * k + 1)

    qc.h(range(n))
    qc.measure(range(n), range(n))

    qc.metadata = {
        "n_qubits": n,
        "shift": s,
        "expected_bitstring": "".join(str(s[i]) for i in reversed(range(n))),
        "polar_rank": polar_rank,
    }
    return qc
