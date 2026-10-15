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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import rustworkx as rx
from qiskit import ClassicalRegister, QuantumCircuit


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
                if esp >= min_esp_floor:
                    candidates.append((esp, comp, tree_edges))

        # Rank candidates by descending ESP score
        candidates.sort(key=lambda item: -item[0])

        chosen_tiles: list[DisjointTile] = []
        blocked: set[int] = set()

        for esp, comp, edges in candidates:
            if max_tiles is not None and len(chosen_tiles) >= max_tiles:
                break
            comp_set = set(comp)
            if comp_set & blocked:
                continue

            buffers = self.get_buffer_qubits(comp)
            avg_cz = sum(self.cz_errors[e] for e in edges) / len(edges) if edges else 0.0
            avg_ro = sum(self.readout_errors[q] for q in comp) / len(comp)
            avg_sx = sum(self.sx_errors[q] for q in comp) / len(comp)

            # Approximated single-round duration: max readout + depth*cz + sx
            dur_ns = max(self.readout_durations[q] for q in comp) * 1e9 + len(edges) * 68.0 + 32.0

            tile = DisjointTile(
                tile_id=len(chosen_tiles),
                qubits=sorted(comp),
                internal_edges=sorted(edges),
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
        self, circuits_ops: list[tuple[str, tuple[int, ...]]] | None = None
    ) -> list[SubsequenceAnomaly]:
        """Detect known abnormal gate subsequences (e.g. rz -> cz -> sx) on sensitive couplers.

        Heron r2 characterization demonstrates that consecutive rz -> cz -> sx sequences
        on couplers with elevated CZ error (> 0.005) or residual ZZ coupling trigger
        unmodeled coherent phase error and excess spectator leakage.
        """
        anomalies: list[SubsequenceAnomaly] = []
        high_error_couplers = {edge for edge, err in self.cz_errors.items() if err > 0.004}

        if circuits_ops is None:
            # Audit highest-error couplers in target
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

        # Scan specific circuit instructions
        for i in range(len(circuits_ops) - 2):
            op1, q1 = circuits_ops[i]
            op2, q2 = circuits_ops[i + 1]
            op3, q3 = circuits_ops[i + 2]
            if op1 == "rz" and op2 == "cz" and op3 in ("sx", "x"):
                edge = (min(q2), max(q2))
                if edge in high_error_couplers and (q1[0] in edge or q3[0] in edge):
                    anomalies.append(
                        SubsequenceAnomaly(
                            qubits=list(edge),
                            gate_sequence=[op1, op2, op3],
                            cz_error=self.cz_errors.get(edge, 0.0),
                            description=f"Instruction sequence rz({q1}) -> cz({q2}) -> {op3}({q3}) "
                            f"on coupler {edge} with elevated CZ error {self.cz_errors.get(edge, 0.0):.4e}.",
                            remedy="Reorder commuting rz past cz, or schedule echo pulse.",
                        )
                    )
        return anomalies

    def build_multiplexed_pub(
        self,
        tile_circuits: list[QuantumCircuit],
        tiles: list[DisjointTile],
    ) -> QuantumCircuit:
        """Combine disjoint tile circuits into a single wide 156-qubit QuantumCircuit for SamplerV2."""
        if len(tile_circuits) != len(tiles):
            raise ValueError(f"Circuit count {len(tile_circuits)} must match tile count {len(tiles)}")

        wide_qc = QuantumCircuit(self.TOTAL_QUBITS, name="heron_multiplexed_pub")

        for tile_idx, (circ, tile) in enumerate(zip(tile_circuits, tiles, strict=True)):
            if circ.num_qubits > len(tile.qubits):
                raise ValueError(
                    f"Tile circuit {tile_idx} requires {circ.num_qubits} qubits, "
                    f"but tile {tile.tile_id} has only {len(tile.qubits)}"
                )

            creg = ClassicalRegister(circ.num_clbits, f"tile_{tile_idx}_c")
            wide_qc.add_register(creg)

            # Map circuit qubits to physical tile qubits
            qubit_map = {q_circ: tile.qubits[idx] for idx, q_circ in enumerate(circ.qubits[: circ.num_qubits])}

            for instruction in circ.data:
                target_qubits = [qubit_map[q] for q in instruction.qubits]
                target_clbits = [creg[circ.find_bit(c).index] for c in instruction.clbits]
                wide_qc.append(instruction.operation, target_qubits, target_clbits)

        return wide_qc

    def compute_spatial_cross_covariance(
        self,
        bitstrings: list[str],
        tile_clbit_slices: list[slice],
    ) -> dict[str, Any]:
        """Compute spatial cross-covariance between multiplexed tiles across chip coordinates.

        C(tile_i, tile_j) = <Z_i Z_j> - <Z_i> <Z_j>.
        For disjoint tiles separated by guard bands, C should vanish unless chip-wide
        vacuum fluctuations, common supply line noise, or bath modes induce correlations.
        """
        n_shots = len(bitstrings)
        if n_shots < 2:
            raise ValueError("Need at least 2 shots to compute covariance")

        n_tiles = len(tile_clbit_slices)
        # Compute parity Z = (-1)^(parity of tile bits) for each shot and tile
        tile_z: list[list[float]] = []
        for bs in bitstrings:
            row: list[float] = []
            for sl in tile_clbit_slices:
                sub = bs[sl]
                parity = sub.count("1") % 2
                row.append(1.0 if parity == 0 else -1.0)
            tile_z.append(row)

        means = [sum(tile_z[s][t] for s in range(n_shots)) / n_shots for t in range(n_tiles)]

        cov_matrix: list[list[float]] = []
        for i in range(n_tiles):
            row_cov: list[float] = []
            for j in range(n_tiles):
                joint_exp = sum(tile_z[s][i] * tile_z[s][j] for s in range(n_shots)) / n_shots
                cov = joint_exp - means[i] * means[j]
                row_cov.append(round(cov, 6))
            cov_matrix.append(row_cov)

        return {
            "num_shots": n_shots,
            "num_tiles": n_tiles,
            "means": [round(m, 4) for m in means],
            "covariance_matrix": cov_matrix,
        }
