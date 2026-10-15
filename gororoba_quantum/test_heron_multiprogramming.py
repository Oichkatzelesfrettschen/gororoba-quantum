"""Tests for Heron r2 spatial multiprogramming and temporal ISA compression."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from heron_multiprogramming import (  # noqa: E402
    HeronLattice,
    build_run1_sedenion_witness,
    build_run2_fano_stabilizer_patch,
    build_run3_vacuum_probe,
    build_run4_hidden_shift_circuit,
)

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"


class TestHeronMultiprogramming(unittest.TestCase):
    """Test suite for HeronLattice spatial tiling, temporal ISA compression, and execution mechanics."""

    lattice: HeronLattice

    @classmethod
    def setUpClass(cls) -> None:
        if not SNAPSHOT.exists():
            raise unittest.SkipTest(f"Snapshot {SNAPSHOT} does not exist")
        cls.lattice = HeronLattice.from_snapshot(SNAPSHOT, "ibm_fez")

    def test_missing_backend_raises(self) -> None:
        with self.assertRaises(ValueError):
            HeronLattice.from_snapshot(SNAPSHOT, "nonexistent_backend")

    def test_lattice_graph_properties(self) -> None:
        self.assertEqual(self.lattice.TOTAL_QUBITS, 156)
        self.assertEqual(self.lattice.graph.num_nodes(), 156)
        self.assertEqual(self.lattice.graph.num_edges(), 176)

    def test_distance_matrix(self) -> None:
        dist = self.lattice.distance_matrix()
        self.assertEqual(len(dist), 156)
        self.assertEqual(len(dist[0]), 156)
        # Reflexive distance is 0
        for i in range(156):
            self.assertEqual(dist[i][i], 0)
        # Symmetry
        for i in range(20):
            for j in range(20):
                self.assertEqual(dist[i][j], dist[j][i])

    def test_tile_esp_bounds(self) -> None:
        esp = self.lattice.tile_esp([0, 1], [(0, 1)])
        self.assertGreaterEqual(esp, 0.0)
        self.assertLessEqual(esp, 1.0)

    def test_disjoint_tiles_guard_band(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, min_buffer_distance=2, max_tiles=16)
        self.assertGreaterEqual(len(tiles), 12)
        self.assertLessEqual(len(tiles), 16)

        # Check disjointness of active qubits
        used_qubits: set[int] = set()
        for t in tiles:
            q_set = set(t.qubits)
            self.assertEqual(len(q_set & used_qubits), 0, f"Tile {t.tile_id} overlaps existing qubits")
            used_qubits.update(q_set)

        # Check guard band distance >= 2
        dist = self.lattice.distance_matrix()
        for i, t1 in enumerate(tiles):
            for j, t2 in enumerate(tiles):
                if i < j:
                    min_d = min(dist[q1][q2] for q1 in t1.qubits for q2 in t2.qubits)
                    self.assertGreaterEqual(
                        min_d,
                        2,
                        f"Tiles {t1.tile_id} and {t2.tile_id} violate guard band: dist={min_d} < 2",
                    )

    def test_plan_run_all_profiles(self) -> None:
        # Run 1: 5q tiles, 16 target
        p1 = self.lattice.plan_run("Run 1", 5, 16, "Sedenion", "RZZ", "Defects")
        self.assertEqual(p1.target_tiles, 16)
        self.assertEqual(p1.active_qubits, 80)
        self.assertAlmostEqual(p1.chip_active_fraction, 80 / 156)

        # Run 2: 10q tiles, 8 target
        p2 = self.lattice.plan_run("Run 2", 10, 8, "Fano CSS", "Dynamic", "Parity")
        self.assertGreaterEqual(p2.target_tiles, 6)
        self.assertLessEqual(p2.target_tiles, 8)

        # Run 3: 2q tiles, 20 target
        p3 = self.lattice.plan_run("Run 3", 2, 20, "Vacuum", "Stretch", "Discrimination")
        self.assertEqual(p3.target_tiles, 20)
        self.assertEqual(p3.active_qubits, 40)

        # Run 4: 7q tiles, 12 target
        p4 = self.lattice.plan_run("Run 4", 7, 12, "Hidden Shift", "PassManager", "Rocq")
        self.assertEqual(p4.target_tiles, 12)
        self.assertEqual(p4.active_qubits, 84)

    def test_temporal_compression_calculations(self) -> None:
        tc = self.lattice.evaluate_temporal_compression(
            circuit_duration_s=5e-6,
            rep_delay_compressed_s=50e-6,
            tile_count=16,
        )
        self.assertAlmostEqual(tc.rep_delay_default_s, 250e-6)
        self.assertAlmostEqual(tc.rep_delay_compressed_s, 50e-6)
        self.assertGreater(tc.shot_rate_multiplier, 4.0)
        self.assertAlmostEqual(tc.fractional_rzz_duration_ns, 68.0)
        self.assertAlmostEqual(tc.decomposed_cz_duration_ns, 264.0)
        self.assertGreater(tc.rzz_duration_reduction_ratio, 3.8)
        self.assertAlmostEqual(tc.total_scientific_yield_multiplier, 16 * tc.shot_rate_multiplier)

    def test_abnormal_subsequence_detection(self) -> None:
        # Coupler audit mode
        anomalies = self.lattice.detect_anomalies()
        self.assertIsInstance(anomalies, list)
        self.assertGreater(len(anomalies), 0)

        # Circuit instructions scan mode
        high_coupler = anomalies[0].qubits
        ops = [
            ("rz", (high_coupler[0],)),
            ("cz", (high_coupler[0], high_coupler[1])),
            ("sx", (high_coupler[0],)),
        ]
        detected = self.lattice.detect_anomalies(ops)
        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0].gate_sequence, ["rz", "cz", "sx"])

    def test_anomaly_detection_per_qubit_accuracy(self) -> None:
        anomalies = self.lattice.detect_anomalies()
        high_coupler = anomalies[0].qubits
        qA, qB = high_coupler[0], high_coupler[1]

        # 1. False alarm rejection: rz on independent qubit 99 must NOT trigger anomaly on coupler (qA, qB)
        ops_false_alarm = [
            ("rz", (99,)),
            ("cz", (qA, qB)),
            ("sx", (qA,)),
        ]
        det_false = self.lattice.detect_anomalies(ops_false_alarm)
        self.assertEqual(len(det_false), 0, "Independent qubit rz must not trigger anomaly")

        # 2. Interleaved gate on independent qubit 99 must NOT hide genuine anomaly on qA
        ops_interleaved = [
            ("rz", (qA,)),
            ("x", (99,)),
            ("cz", (qA, qB)),
            ("sx", (qA,)),
        ]
        det_interleaved = self.lattice.detect_anomalies(ops_interleaved)
        self.assertEqual(len(det_interleaved), 1, "Genuine sequence with interleaved gate must be detected")

        # 3. Direct QuantumCircuit input test
        qc = QuantumCircuit(156)
        qc.rz(0.5, qA)
        qc.x(99)
        qc.cz(qA, qB)
        qc.sx(qA)
        det_circuit = self.lattice.detect_anomalies(qc)
        self.assertEqual(len(det_circuit), 1, "Direct QuantumCircuit scanning must detect anomaly")

    def test_build_multiplexed_pub(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)
        circuits = []
        for _ in range(2):
            qc = QuantumCircuit(5, 1)
            qc.h(0)
            qc.cx(0, 1)
            qc.measure(0, 0)
            circuits.append(qc)

        multiplexed = self.lattice.build_multiplexed_pub(circuits, tiles)
        self.assertEqual(multiplexed.num_qubits, 156)
        self.assertEqual(len(multiplexed.cregs), 2)
        self.assertEqual(multiplexed.cregs[0].name, "tile_0_c")
        self.assertEqual(multiplexed.cregs[1].name, "tile_1_c")

    def test_build_multiplexed_pub_mismatch_raises(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=1)
        circuits = [QuantumCircuit(6, 1)]  # requires 6 qubits, tile has 5
        with self.assertRaises(ValueError):
            self.lattice.build_multiplexed_pub(circuits, tiles)

    def test_dynamic_circuits_multiplexing_aer_execution(self) -> None:
        # Test that multiple tiles with dynamic if_test control flow can be multiplexed
        # and executed in AerSimulator without register collisions or KeyError
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)

        def make_dynamic_tile(flip_initial: bool) -> QuantumCircuit:
            qc = QuantumCircuit(5, 1)
            if flip_initial:
                qc.x(0)
            qc.measure(0, 0)
            with qc.if_test((qc.clbits[0], 1)):
                qc.x(1)
            return qc

        c0 = make_dynamic_tile(False)  # outcome 0
        c1 = make_dynamic_tile(True)  # outcome 1

        wide_pub = self.lattice.build_multiplexed_pub([c0, c1], tiles)
        sim = AerSimulator()
        res = sim.run(wide_pub, shots=20).result()
        counts = res.get_counts()
        # Qiskit space-separates multiple classical registers: 'tile_1_c tile_0_c'
        self.assertIn("1 0", counts)
        self.assertEqual(counts["1 0"], 20)

    def test_parameterized_pub_and_sweep_packing(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)
        p0 = Parameter("theta_0")
        p1 = Parameter("theta_1")

        qc0 = QuantumCircuit(5)
        qc0.rx(p0, 0)
        qc1 = QuantumCircuit(5)
        qc1.rx(p1, 0)

        wide = self.lattice.build_parameterized_multiplexed_pub([qc0, qc1], tiles)
        self.assertEqual(wide.num_parameters, 2)

        # Pack parameter sweep with shape (N_sweeps, 2)
        param_grid = [[0.0, 0.5], [0.5, 1.0], [1.0, 1.5]]
        pub = HeronLattice.pack_parameter_sweep_pub(wide, param_grid, shots=2048)
        self.assertEqual(pub[0], wide)
        self.assertEqual(pub[1].shape, (3, 2))
        self.assertEqual(pub[2], 2048)

        # Test validation on mismatched shape
        with self.assertRaises(ValueError):
            HeronLattice.pack_parameter_sweep_pub(wide, [[0.0, 0.5, 1.0]])

    def test_append_basis_rotations(self) -> None:
        # Test X basis rotation: H prepares |0> from |+>
        qc_plus = QuantumCircuit(1)
        qc_plus.h(0)
        qc_x_rot = HeronLattice.append_basis_rotations(qc_plus, "X")
        sv_x = Statevector(qc_x_rot)
        self.assertAlmostEqual(sv_x.probabilities()[0], 1.0)

        # Test Y basis rotation: Sdg then H prepares |0> from |+i>
        qc_y_state = QuantumCircuit(1)
        qc_y_state.h(0)
        qc_y_state.s(0)
        qc_y_rot = HeronLattice.append_basis_rotations(qc_y_state, "Y")
        sv_y = Statevector(qc_y_rot)
        self.assertAlmostEqual(sv_y.probabilities()[0], 1.0)

    def test_run1_run2_run3_run4_circuit_builders(self) -> None:
        # Run 1
        r1 = build_run1_sedenion_witness((1, 10), (4, 15), 0.0)
        self.assertEqual(r1.num_qubits, 5)
        self.assertEqual(r1.num_clbits, 1)

        # Run 2
        r2 = build_run2_fano_stabilizer_patch(error_qubit=0)
        self.assertEqual(r2.num_qubits, 10)
        self.assertEqual(r2.num_clbits, 3)

        # Run 3
        r3 = build_run3_vacuum_probe(delay_dt=50)
        self.assertEqual(r3.num_qubits, 2)
        self.assertEqual(r3.num_clbits, 2)

        # Run 4
        r4 = build_run4_hidden_shift_circuit(dim=8, i=1, j=4)
        self.assertEqual(r4.num_qubits, 7)
        self.assertEqual(r4.num_clbits, 7)

    def test_spatial_cross_covariance(self) -> None:
        # Synthetic bitstrings for 2 tiles
        bitstrings = ["00", "01", "10", "11"] * 25
        slices = [slice(0, 1), slice(1, 2)]
        res = self.lattice.compute_spatial_cross_covariance(bitstrings, slices)
        self.assertEqual(res["num_shots"], 100)
        self.assertEqual(res["num_tiles"], 2)
        cov = res["covariance_matrix"]
        self.assertEqual(len(cov), 2)
        self.assertEqual(len(cov[0]), 2)
        # Symmetry
        self.assertAlmostEqual(cov[0][1], cov[1][0])

    def test_spatial_cross_covariance_dict_input(self) -> None:
        reg_dict = {
            "tile_0_c": ["0", "1", "0", "1"] * 25,
            "tile_1_c": ["1", "0", "1", "0"] * 25,
        }
        res = self.lattice.compute_spatial_cross_covariance(reg_dict)
        self.assertEqual(res["num_shots"], 100)
        self.assertEqual(res["num_tiles"], 2)
        cov = res["covariance_matrix"]
        self.assertAlmostEqual(cov[0][1], cov[1][0])

    def test_spatial_cross_covariance_insufficient_shots_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.lattice.compute_spatial_cross_covariance(["00"], [slice(0, 1)])


if __name__ == "__main__":
    unittest.main()
