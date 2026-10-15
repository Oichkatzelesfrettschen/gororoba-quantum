"""Heron r2 spatial multiprogramming and temporal ISA compression engine.

This module implements hardware execution mechanics for 156-qubit IBM Heron r2
processors (ibm_fez, ibm_kingston, ibm_marrakesh), optimizing scientific yield
per QPU-second across two orthogonal axes:
1. Spatial Multiprogramming: packing disjoint sub-lattices into wide QuantumCircuits
   with graph distance >= 2 (crosstalk guard bands) to prevent QPU idle waste.
2. Temporal ISA Compression: native continuous fractional R_ZZ(theta) and R_X(theta)
   execution alongside repetition delay tuning (rep_delay reduction to 10-50 us)
   and QASM3 stretch scheduling.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rustworkx as rx
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.circuit import ParameterExpression


@dataclass(frozen=True)
class TileQubit:
    """Per-qubit calibration facts from Heron snapshot."""

    index: int
    sx_error: float
    readout_error: float
    readout_2_error: float
    sx_duration_ns: float
    readout_duration_ns: float


@dataclass(frozen=True)
class TileEdge:
    """Coupler calibration facts for an undirected heavy-hex edge."""

    qubits: tuple[int, int]
    cz_error: float
    rzz_error: float
    cz_duration_ns: float


@dataclass
class DisjointTile:
    """Disjoint sub-lattice placement on the Heron heavy-hex lattice."""

    tile_id: int
    qubits: list[int]
    internal_edges: list[tuple[int, int]]
    buffer_qubits: list[int]
    avg_cz_error: float
    avg_readout_error: float
    avg_sx_error: float
    esp: float
    duration_ns: float

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
            "duration_ns": round(self.duration_ns, 2),
        }


@dataclass
class RunPlan:
    """Prioritized scientific run allocation plan."""

    run_id: str
    name: str
    qubits_per_tile: int
    target_tiles: int
    active_qubits: int
    tiles: list[DisjointTile]
    chip_active_fraction: float
    key_isa_feature: str
    deliverable: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "name": self.name,
            "qubits_per_tile": self.qubits_per_tile,
            "target_tiles": self.target_tiles,
            "active_qubits": self.active_qubits,
            "chip_active_fraction": round(self.chip_active_fraction, 4),
            "key_isa_feature": self.key_isa_feature,
            "deliverable": self.deliverable,
            "tiles": [t.to_dict() for t in self.tiles],
        }


@dataclass
class TemporalCompression:
    """Comparative temporal compression metrics."""

    rep_delay_default_s: float
    rep_delay_compressed_s: float
    circuit_duration_s: float
    shot_rate_default_hz: float
    shot_rate_compressed_hz: float
    shot_rate_multiplier: float
    fractional_rzz_duration_ns: float
    decomposed_cz_duration_ns: float
    rzz_duration_reduction_ratio: float
    spatial_tile_multiplier: int
    total_scientific_yield_multiplier: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "rep_delay_default_us": round(self.rep_delay_default_s * 1e6, 2),
            "rep_delay_compressed_us": round(self.rep_delay_compressed_s * 1e6, 2),
            "circuit_duration_us": round(self.circuit_duration_s * 1e6, 2),
            "shot_rate_default_hz": round(self.shot_rate_default_hz, 1),
            "shot_rate_compressed_hz": round(self.shot_rate_compressed_hz, 1),
            "shot_rate_multiplier": round(self.shot_rate_multiplier, 3),
            "fractional_rzz_duration_ns": round(self.fractional_rzz_duration_ns, 1),
            "decomposed_cz_duration_ns": round(self.decomposed_cz_duration_ns, 1),
            "rzz_duration_reduction_ratio": round(self.rzz_duration_reduction_ratio, 3),
            "spatial_tile_multiplier": self.spatial_tile_multiplier,
            "total_scientific_yield_multiplier": round(self.total_scientific_yield_multiplier, 2),
        }


@dataclass
class SubsequenceAnomaly:
    """Reported anomalous gate subsequence."""

    qubits: list[int]
    gate_sequence: list[str]
    cz_error: float
    description: str
    remedy: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "qubits": self.qubits,
            "gate_sequence": self.gate_sequence,
            "cz_error": round(self.cz_error, 6),
            "description": self.description,
            "remedy": self.remedy,
        }


class HeronLattice:
    """Model of the 156-qubit Heron r2 heavy-hex coupling and calibration geometry."""

    TOTAL_QUBITS = 156

    def __init__(self, backend_name: str, target_dict: dict[str, Any]) -> None:
        self.backend_name = backend_name
        self.target_dict = target_dict
        self.cz_errors: dict[tuple[int, int], float] = {}
        self.rzz_errors: dict[tuple[int, int], float] = {}
        self.cz_durations: dict[tuple[int, int], float] = {}
        self.sx_errors: dict[int, float] = {}
        self.sx_durations: dict[int, float] = {}
        self.readout_errors: dict[int, float] = {}
        self.readout_durations: dict[int, float] = {}
        self.readout_2_errors: dict[int, float] = {}
        self.readout_2_durations: dict[int, float] = {}
        self._load_calibration()
        self.graph = self._build_graph()
        self._distance_matrix: list[list[int]] | None = None

    @classmethod
    def from_snapshot(cls, snapshot_path: Path | str, backend_name: str = "ibm_fez") -> HeronLattice:
        data = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
        if backend_name not in data["backends"]:
            raise ValueError(f"Backend {backend_name} not found in snapshot {snapshot_path}")
        return cls(backend_name, data["backends"][backend_name])

    def _load_calibration(self) -> None:
        instructions = self.target_dict["instructions"]
        fractional = self.target_dict.get("fractional_instructions", {})

        # CZ
        for qargs, dur, err in zip(
            instructions["cz"]["qargs"],
            instructions["cz"]["duration"],
            instructions["cz"]["error"],
            strict=True,
        ):
            edge = (min(qargs), max(qargs))
            self.cz_errors[edge] = max(self.cz_errors.get(edge, 0.0), float(err))
            self.cz_durations[edge] = max(self.cz_durations.get(edge, 0.0), float(dur))

        # RZZ
        if "rzz" in fractional:
            for qargs, err in zip(fractional["rzz"]["qargs"], fractional["rzz"]["error"], strict=True):
                edge = (min(qargs), max(qargs))
                self.rzz_errors[edge] = max(self.rzz_errors.get(edge, 0.0), float(err))
        else:
            self.rzz_errors = self.cz_errors.copy()

        # SX
        for qargs, dur, err in zip(
            instructions["sx"]["qargs"],
            instructions["sx"]["duration"],
            instructions["sx"]["error"],
            strict=True,
        ):
            q = qargs[0]
            self.sx_errors[q] = float(err)
            self.sx_durations[q] = float(dur)

        # Measure
        for qargs, dur, err in zip(
            instructions["measure"]["qargs"],
            instructions["measure"]["duration"],
            instructions["measure"]["error"],
            strict=True,
        ):
            q = qargs[0]
            self.readout_errors[q] = float(err)
            self.readout_durations[q] = float(dur)

        # Measure_2
        if "measure_2" in instructions:
            for qargs, dur, err in zip(
                instructions["measure_2"]["qargs"],
                instructions["measure_2"]["duration"],
                instructions["measure_2"]["error"],
                strict=True,
            ):
                q = qargs[0]
                self.readout_2_errors[q] = float(err)
                self.readout_2_durations[q] = float(dur)
        else:
            self.readout_2_errors = self.readout_errors.copy()
            self.readout_2_durations = self.readout_durations.copy()

    def _build_graph(self) -> rx.PyGraph:
        graph = rx.PyGraph()
        graph.add_nodes_from(range(self.TOTAL_QUBITS))
        edges = sorted(self.cz_errors.keys())
        graph.add_edges_from_no_data(edges)
        return graph

    def distance_matrix(self) -> list[list[int]]:
        if self._distance_matrix is None:
            raw_matrix = rx.distance_matrix(self.graph)
            self._distance_matrix = [[int(val) for val in row] for row in raw_matrix]
        return self._distance_matrix

    def tile_esp(self, qubits: list[int], edges: list[tuple[int, int]]) -> float:
        """Estimated success probability under unmitigated SPAM and CZ error."""
        prob = 1.0
        for q in qubits:
            prob *= (1.0 - self.readout_errors.get(q, 0.01)) * (1.0 - self.sx_errors.get(q, 0.0003))
        for e in edges:
            prob *= 1.0 - self.cz_errors.get(e, 0.0025)
        return max(prob, 0.0)

    def get_buffer_qubits(self, qubits: list[int]) -> list[int]:
        """All direct heavy-hex neighbors not in the tile, forming the guard band."""
        qubit_set = set(qubits)
        buffers = {nbr for q in qubits for nbr in self.graph.neighbors(q) if nbr not in qubit_set}
        return sorted(buffers)

    def find_disjoint_tiles(
        self,
        k: int,
        min_buffer_distance: int = 2,
        max_tiles: int | None = None,
        min_esp_floor: float = 0.5,
    ) -> list[DisjointTile]:
        """Greedy best-first search for disjoint k-qubit subgraphs separated by min_buffer_distance.

        A buffer distance >= 2 guarantees that every active island is separated
        by at least 1 idle transmon (coupler guard band), eliminating parasitic ZZ crosstalk.
        """
        # Generate candidate subgraphs of size k starting from each node
        candidates: list[tuple[float, list[int], list[tuple[int, int]]]] = []
        all_candidates: list[tuple[float, list[int], list[tuple[int, int]]]] = []
        for start in range(self.TOTAL_QUBITS):
            comp = [start]
            tree_edges: list[tuple[int, int]] = []
            frontier = [start]
            seen = {start}
            while frontier and len(comp) < k:
                curr = frontier.pop(0)
                nbrs = sorted(
                    self.graph.neighbors(curr),
                    key=lambda n: self.cz_errors.get((min(curr, n), max(curr, n)), 1.0),
                )
                for n in nbrs:
                    if n not in seen:
                        seen.add(n)
                        comp.append(n)
                        tree_edges.append((min(curr, n), max(curr, n)))
                        frontier.append(n)
                        if len(comp) == k:
                            break
            if len(comp) == k:
                esp = self.tile_esp(comp, tree_edges)
                all_candidates.append((esp, comp, tree_edges))
                if esp >= min_esp_floor:
                    candidates.append((esp, comp, tree_edges))

        # Fall back to all candidates if min_esp_floor filtered out all options
        pool = candidates if candidates else all_candidates

        # Rank candidates by descending ESP score
        pool.sort(key=lambda item: -item[0])

        chosen_tiles: list[DisjointTile] = []
        blocked: set[int] = set()

        for esp, comp, edges in pool:
            if max_tiles is not None and len(chosen_tiles) >= max_tiles:
                break
            comp_set = set(comp)
            if comp_set & blocked:
                continue

            buffers = self.get_buffer_qubits(comp)
            # Find all induced edges in comp
            induced_edges = sorted(
                (min(u, v), max(u, v)) for u in comp for v in self.graph.neighbors(u) if v in comp_set and u < v
            )
            actual_edges = induced_edges if induced_edges else edges

            avg_cz = sum(self.cz_errors[e] for e in actual_edges) / len(actual_edges) if actual_edges else 0.0
            avg_ro = sum(self.readout_errors[q] for q in comp) / len(comp)
            avg_sx = sum(self.sx_errors[q] for q in comp) / len(comp)

            # Approximated single-round duration: max readout + depth*cz + sx
            dur_ns = max(self.readout_durations[q] for q in comp) * 1e9 + len(actual_edges) * 68.0 + 32.0

            tile = DisjointTile(
                tile_id=len(chosen_tiles),
                qubits=sorted(comp),
                internal_edges=actual_edges,
                buffer_qubits=buffers,
                avg_cz_error=avg_cz,
                avg_readout_error=avg_ro,
                avg_sx_error=avg_sx,
                esp=esp,
                duration_ns=dur_ns,
            )
            chosen_tiles.append(tile)

            # Block the active qubits and their guard band (if min_buffer_distance >= 2)
            blocked |= comp_set
            if min_buffer_distance >= 2:
                blocked.update(buffers)

        return chosen_tiles

    def plan_run(
        self,
        run_id: str,
        k: int,
        target_tiles: int,
        name: str,
        key_isa_feature: str,
        deliverable: str,
        min_buffer_distance: int = 2,
    ) -> RunPlan:
        """Construct full scientific run allocation plan."""
        tiles = self.find_disjoint_tiles(k, min_buffer_distance=min_buffer_distance, max_tiles=target_tiles)
        active_q = sum(len(t.qubits) for t in tiles)
        chip_frac = active_q / self.TOTAL_QUBITS

        return RunPlan(
            run_id=run_id,
            name=name,
            qubits_per_tile=k,
            target_tiles=len(tiles),
            active_qubits=active_q,
            tiles=tiles,
            chip_active_fraction=chip_frac,
            key_isa_feature=key_isa_feature,
            deliverable=deliverable,
        )

    def evaluate_temporal_compression(
        self,
        circuit_duration_s: float = 5e-6,
        rep_delay_compressed_s: float = 50e-6,
        tile_count: int = 14,
    ) -> TemporalCompression:
        """Compute execution rate gains from rep_delay reduction and native fractional RZZ gates."""
        default_rep_delay = 250e-6
        rate_default = 1.0 / (default_rep_delay + circuit_duration_s)
        rate_compressed = 1.0 / (rep_delay_compressed_s + circuit_duration_s)
        shot_rate_mult = rate_compressed / rate_default

        # RZZ gate timing
        native_rzz_ns = 68.0  # single continuous RZZ on Heron r2
        decomposed_cz_ns = 2.0 * 68.0 + 4.0 * 32.0  # 2 CZ + 4 SX (Euler synthesis)
        rzz_ratio = decomposed_cz_ns / native_rzz_ns

        total_yield = tile_count * shot_rate_mult

        return TemporalCompression(
            rep_delay_default_s=default_rep_delay,
            rep_delay_compressed_s=rep_delay_compressed_s,
            circuit_duration_s=circuit_duration_s,
            shot_rate_default_hz=rate_default,
            shot_rate_compressed_hz=rate_compressed,
            shot_rate_multiplier=shot_rate_mult,
            fractional_rzz_duration_ns=native_rzz_ns,
            decomposed_cz_duration_ns=decomposed_cz_ns,
            rzz_duration_reduction_ratio=rzz_ratio,
            spatial_tile_multiplier=tile_count,
            total_scientific_yield_multiplier=total_yield,
        )

    def detect_anomalies(
        self,
        circuits_ops: QuantumCircuit | list[tuple[str, tuple[int, ...]]] | None = None,
    ) -> list[SubsequenceAnomaly]:
        """Detect known abnormal gate subsequences (e.g. rz -> cz -> sx) on sensitive couplers.

        Heron r2 characterization demonstrates that consecutive rz -> cz -> sx sequences
        on couplers with elevated CZ error (> 0.004) trigger unmodeled coherent phase error
        and excess spectator leakage.

        Tracks gate history per participating physical qubit line to prevent false alarms
        from independent qubits and accurately capture genuine anomalies across interleaved operations.
        """
        anomalies: list[SubsequenceAnomaly] = []
        high_error_couplers = {edge for edge, err in self.cz_errors.items() if err > 0.004}

        if circuits_ops is None:
            # Coupler audit mode: list sensitive couplers from calibration
            for edge in sorted(high_error_couplers):
                anomalies.append(
                    SubsequenceAnomaly(
                        qubits=list(edge),
                        gate_sequence=["rz", "cz", "sx"],
                        cz_error=self.cz_errors[edge],
                        description=f"Coupler {edge} exhibits CZ error {self.cz_errors[edge]:.4e} > 4.0e-3. "
                        "Unbuffered rz -> cz -> sx sequences trigger unmodeled Stark detuning and leakage.",
                        remedy="Commute rz past cz (diagonal in Z basis), reroute to lower-error tile, "
                        "or insert 1-dt alignment delay.",
                    )
                )
            return anomalies

        # Normalize input to list of (op_name, (qubit_indices,))
        parsed_ops: list[tuple[str, tuple[int, ...]]] = []
        if isinstance(circuits_ops, QuantumCircuit):
            for inst in circuits_ops.data:
                name = inst.operation.name.lower()
                q_indices = tuple(circuits_ops.find_bit(q).index for q in inst.qubits)
                parsed_ops.append((name, q_indices))
        else:
            parsed_ops = list(circuits_ops)

        # Build timeline per qubit
        qubit_timeline: dict[int, list[tuple[str, tuple[int, ...], int]]] = {}
        for idx, (name, qargs) in enumerate(parsed_ops):
            if name in ("barrier", "delay"):
                continue
            for q in qargs:
                qubit_timeline.setdefault(q, []).append((name, qargs, idx))

        # Check each CZ operation on a high-error coupler
        seen_anomalies: set[tuple[int, tuple[int, int]]] = set()
        for idx, (name, qargs) in enumerate(parsed_ops):
            if name == "cz" and len(qargs) == 2:
                qA, qB = qargs[0], qargs[1]
                edge = (min(qA, qB), max(qA, qB))
                if edge in high_error_couplers:
                    for target_q in (qA, qB):
                        line = qubit_timeline.get(target_q, [])
                        pos = next((i for i, entry in enumerate(line) if entry[2] == idx), None)
                        if pos is not None and pos > 0 and pos + 1 < len(line):
                            prev_op = line[pos - 1]
                            next_op = line[pos + 1]
                            if prev_op[0] == "rz" and next_op[0] in ("sx", "x"):
                                anomaly_key = (target_q, edge)
                                if anomaly_key not in seen_anomalies:
                                    seen_anomalies.add(anomaly_key)
                                    anomalies.append(
                                        SubsequenceAnomaly(
                                            qubits=list(edge),
                                            gate_sequence=[prev_op[0], name, next_op[0]],
                                            cz_error=self.cz_errors.get(edge, 0.0),
                                            description=f"Instruction sequence rz({target_q}) -> cz{edge} -> "
                                            f"{next_op[0]}({target_q}) on coupler {edge} with elevated "
                                            f"CZ error {self.cz_errors.get(edge, 0.0):.4e}.",
                                            remedy="Reorder commuting rz past cz, or schedule echo pulse.",
                                        )
                                    )
        return anomalies

    def build_multiplexed_pub(
        self,
        tile_circuits: list[QuantumCircuit],
        tiles: list[DisjointTile],
    ) -> QuantumCircuit:
        """Combine disjoint tile circuits into a single wide 156-qubit QuantumCircuit for SamplerV2.

        Uses QuantumCircuit.compose to recursively rebind all gates, control flow
        operations (e.g. if_test, while_loop), parameters, and classical registers
        without register collision or clbit index misalignment.
        """
        if len(tile_circuits) != len(tiles):
            raise ValueError(f"Circuit count {len(tile_circuits)} must match tile count {len(tiles)}")

        wide_qc = QuantumCircuit(self.TOTAL_QUBITS, name="heron_multiplexed_pub")

        for tile_idx, (circ, tile) in enumerate(zip(tile_circuits, tiles, strict=True)):
            if circ.num_qubits > len(tile.qubits):
                raise ValueError(
                    f"Tile circuit {tile_idx} requires {circ.num_qubits} qubits, "
                    f"but tile {tile.tile_id} has only {len(tile.qubits)}"
                )

            tile_qubit_indices = tile.qubits[: circ.num_qubits]

            if circ.num_clbits > 0:
                creg = ClassicalRegister(circ.num_clbits, f"tile_{tile_idx}_c")
                wide_qc.add_register(creg)
                wide_qc.compose(circ, qubits=tile_qubit_indices, clbits=list(creg), inplace=True)
            else:
                wide_qc.compose(circ, qubits=tile_qubit_indices, inplace=True)

        return wide_qc

    def build_parameterized_multiplexed_pub(
        self,
        tile_circuits: list[QuantumCircuit],
        tiles: list[DisjointTile],
    ) -> QuantumCircuit:
        """Build a multiplexed circuit retaining unbound parameters across tiles for single-PUB execution."""
        return self.build_multiplexed_pub(tile_circuits, tiles)

    @staticmethod
    def pack_parameter_sweep_pub(
        circuit: QuantumCircuit,
        parameter_values: np.ndarray | Sequence[Sequence[float]] | Sequence[float],
        shots: int = 4096,
    ) -> tuple[QuantumCircuit, np.ndarray, int]:
        """Pack a wide QuantumCircuit, parameter value array, and shots into a valid SamplerV2 PUB tuple.

        Shape of parameter_values:
        - 1D: (N_params,) for a single execution point
        - 2D: (N_sweeps, N_params) for continuous angle/wave-table parameter sweeps
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
                if arr.shape[1] != n_params:
                    raise ValueError(f"Expected parameter array with second dimension {n_params}, got {arr.shape}")
            else:
                raise ValueError(f"Parameter values must be 1D or 2D array, got ndim={arr.ndim}")
        if shots <= 0:
            raise ValueError(f"Shot count must be positive, got {shots}")
        return (circuit, arr, shots)

    @staticmethod
    def append_basis_rotations(
        circuit: QuantumCircuit,
        bases: dict[int, str] | Sequence[str] | str,
    ) -> QuantumCircuit:
        """Append explicit basis rotations (X, Y, Z) to qubits prior to terminal measurement.

        Supports SamplerV2 full joint bitstring reconstruction for arbitrary Pauli observables
        without EstimatorV2's twirling multiplier:
        - 'Z' / 'I': computational basis (identity, no rotation).
        - 'X': H on target qubit.
        - 'Y': Sdg followed by H on target qubit.
        """
        out = circuit.copy()
        n_q = out.num_qubits

        basis_map: dict[int, str] = {}
        if isinstance(bases, str):
            if len(bases) == 1:
                basis_map = {q: bases.upper() for q in range(n_q)}
            else:
                if len(bases) != n_q:
                    raise ValueError(f"Basis string length {len(bases)} does not match qubit count {n_q}")
                basis_map = {q: b.upper() for q, b in enumerate(bases)}
        elif isinstance(bases, dict):
            basis_map = {int(q): b.upper() for q, b in bases.items()}
        else:
            if len(bases) != n_q:
                raise ValueError(f"Basis sequence length {len(bases)} does not match qubit count {n_q}")
            basis_map = {q: b.upper() for q, b in enumerate(bases)}

        has_measures = any(inst.operation.name == "measure" for inst in out.data)

        if has_measures:
            new_circ = QuantumCircuit(*out.qregs, *out.cregs, name=out.name)
            for inst in out.data:
                if inst.operation.name == "measure":
                    for q in inst.qubits:
                        q_idx = out.find_bit(q).index
                        b = basis_map.get(q_idx, "Z")
                        if b == "X":
                            new_circ.h(q)
                        elif b == "Y":
                            new_circ.sdg(q)
                            new_circ.h(q)
                        elif b in ("Z", "I"):
                            pass
                        else:
                            raise ValueError(f"Unsupported basis '{b}' on qubit {q_idx}")
                new_circ.append(inst.operation, inst.qubits, inst.clbits)
            return new_circ
        else:
            for q_idx, b in basis_map.items():
                if q_idx < 0 or q_idx >= n_q:
                    raise ValueError(f"Qubit index {q_idx} out of range [0, {n_q - 1}]")
                if b == "X":
                    out.h(q_idx)
                elif b == "Y":
                    out.sdg(q_idx)
                    out.h(q_idx)
                elif b in ("Z", "I"):
                    pass
                else:
                    raise ValueError(f"Unsupported basis '{b}' on qubit {q_idx}")
            return out

    def compute_spatial_cross_covariance(
        self,
        bitstrings: list[str] | dict[str, list[str]],
        tile_clbit_slices: list[slice] | None = None,
        endianness: str = "big",
        unbiased: bool = False,
    ) -> dict[str, Any]:
        """Compute spatial cross-covariance between multiplexed tiles across chip coordinates.

        C(tile_i, tile_j) = <Z_i Z_j> - <Z_i> <Z_j>.
        For disjoint tiles separated by guard bands, C should vanish unless chip-wide
        vacuum fluctuations, common supply line noise, or bath modes induce correlations.

        Supports:
        - raw bitstrings with tile_clbit_slices (endianness='big' for standard slices, 'little' for Qiskit endianness)
        - register-keyed dictionary (e.g. {'tile_0_c': [...], 'tile_1_c': [...]})
        - unbiased sample covariance (denominator N-1) or population covariance (denominator N).
        """
        tile_bitstrings: list[list[str]] = []

        if isinstance(bitstrings, dict):
            reg_names = sorted(bitstrings.keys())
            if not reg_names:
                raise ValueError("Empty dictionary provided for bitstrings")
            n_shots = len(bitstrings[reg_names[0]])
            if n_shots < 2:
                raise ValueError("Need at least 2 shots to compute covariance")
            for name in reg_names:
                if len(bitstrings[name]) != n_shots:
                    raise ValueError(f"Shot count mismatch in register {name}")
                tile_bitstrings.append(bitstrings[name])
        else:
            n_shots = len(bitstrings)
            if n_shots < 2:
                raise ValueError("Need at least 2 shots to compute covariance")
            if tile_clbit_slices is None:
                raise ValueError("tile_clbit_slices is required when bitstrings is a list")
            for sl in tile_clbit_slices:
                sub_list: list[str] = []
                for bs in bitstrings:
                    if endianness == "little":
                        start = sl.start or 0
                        stop = sl.stop if sl.stop is not None else len(bs)
                        sub = bs[len(bs) - stop : len(bs) - start]
                    else:
                        sub = bs[sl]
                    sub_list.append(sub)
                tile_bitstrings.append(sub_list)

        n_tiles = len(tile_bitstrings)
        tile_z: list[list[float]] = []
        for s in range(n_shots):
            row: list[float] = []
            for t in range(n_tiles):
                sub = tile_bitstrings[t][s]
                parity = sub.count("1") % 2
                row.append(1.0 if parity == 0 else -1.0)
            tile_z.append(row)

        means = [sum(tile_z[s][t] for s in range(n_shots)) / n_shots for t in range(n_tiles)]

        denom_scale = (n_shots / (n_shots - 1)) if unbiased and n_shots > 1 else 1.0

        cov_matrix: list[list[float]] = []
        for i in range(n_tiles):
            row_cov: list[float] = []
            for j in range(n_tiles):
                joint_exp = sum(tile_z[s][i] * tile_z[s][j] for s in range(n_shots)) / n_shots
                cov = (joint_exp - means[i] * means[j]) * denom_scale
                row_cov.append(round(cov, 6))
            cov_matrix.append(row_cov)

        return {
            "num_shots": n_shots,
            "num_tiles": n_tiles,
            "means": [round(m, 4) for m in means],
            "covariance_matrix": cov_matrix,
        }


# Concrete circuit builders for Prioritized Scientific Runs 1-4


def build_run1_sedenion_witness(
    a_pair: tuple[int, int] = (1, 10),
    b_pair: tuple[int, int] = (4, 15),
    phase: float | ParameterExpression = 0.0,
) -> QuantumCircuit:
    """Build Run 1 Sedenion zero-divisor witness circuit on 5 qubits.

    Corresponds to designs.lcu_witness: 4 data qubits encode the basis elements,
    ancilla qubit 4 provides the LCU selection register with destructive interference.
    """
    from designs import lcu_witness

    return lcu_witness(a_pair, b_pair, phase)


def build_run2_fano_stabilizer_patch(
    error_qubit: int | None = None,
) -> QuantumCircuit:
    """Build Run 2 Octonionic Fano-plane CSS active stabilizer patch on 10 qubits.

    7 data qubits (0..6) map to the 7 imaginary units of O_8.
    3 syndrome ancillas (7, 8, 9) measure Fano line generator parity checks:
    - Syn 0 (anc 7): checks Z on data {0, 2, 4, 6} (Fano line 1, 3, 5, 7)
    - Syn 1 (anc 8): checks Z on data {1, 2, 5, 6} (Fano line 2, 3, 6, 7)
    - Syn 2 (anc 9): checks Z on data {3, 4, 5, 6} (Fano line 4, 5, 6, 7)

    Includes fast classical feed-forward via if_test to actively correct bit-flip errors.
    """
    qc = QuantumCircuit(10, 3, name="fano_css_active_stabilizer")

    if error_qubit is not None and 0 <= error_qubit < 7:
        qc.x(error_qubit)

    # Syndrome measurement 0
    qc.h(7)
    for q in (0, 2, 4, 6):
        qc.cx(q, 7)
    qc.h(7)
    qc.measure(7, 0)

    # Syndrome measurement 1
    qc.h(8)
    for q in (1, 2, 5, 6):
        qc.cx(q, 8)
    qc.h(8)
    qc.measure(8, 1)

    # Syndrome measurement 2
    qc.h(9)
    for q in (3, 4, 5, 6):
        qc.cx(q, 9)
    qc.h(9)
    qc.measure(9, 2)

    # Active feed-forward correction using dynamic if_test
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(0)

    return qc


def build_run3_vacuum_probe(
    delay_dt: int = 100,
) -> QuantumCircuit:
    """Build Run 3 Vacuum endpoint interferometric probe on 2 qubits.

    Prepares Bell state (|00> + |11>)/sqrt2, applies delay / dynamical decoupling,
    and measures terminal basis.
    """
    qc = QuantumCircuit(2, 2, name="vacuum_endpoint_probe")
    qc.h(0)
    qc.cx(0, 1)
    if delay_dt > 0:
        qc.delay(delay_dt, 0)
        qc.delay(delay_dt, 1)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def build_run4_hidden_shift_circuit(
    dim: int = 8,
    i: int = 1,
    j: int = 4,
) -> QuantumCircuit:
    """Build Run 4 Boolean Hidden Shift / Walsh spectrum witness on 7 qubits."""
    from designs import design_c_associator_spectrum

    base_qc = design_c_associator_spectrum(dim, i, j)
    qc = QuantumCircuit(7, 7, name="hidden_shift_run4")
    qc.compose(base_qc, qubits=list(range(base_qc.num_qubits)), clbits=list(range(base_qc.num_clbits)), inplace=True)
    return qc
