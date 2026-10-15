"""Contracts for Heron r2 guard-banded tiling, wide-circuit composition and Target duration arithmetic."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from heron_multiprogramming import (  # noqa: E402
    STEANE_Z_CHECKS,
    DisjointTile,
    HeronLattice,
    bell_delay_probe,
    bent_hidden_shift_circuit,
    fano_plane_incidence_matrix,
    hoeffding_model_discrimination,
    lcu_zero_product_witness,
    pathion_associator_spectrum_witness,
    sedenion_associator_witness,
    steane_coherent_syndrome_patch,
    steane_z_syndrome_patch,
)

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"


def edge_circuit(tile: DisjointTile, flip: bool) -> QuantumCircuit:
    """Measure one end of the tile's first coupler and flip the other end on a 1 inside if_test."""
    position = {q: i for i, q in enumerate(tile.qubits)}
    a, b = tile.internal_edges[0]
    qc = QuantumCircuit(len(tile.qubits), 2)
    if flip:
        qc.x(position[a])
    qc.measure(position[a], 0)
    with qc.if_test((qc.clbits[0], 1)):
        qc.x(position[b])
    qc.measure(position[b], 1)
    return qc


class TestHeronMultiprogramming(unittest.TestCase):
    lattice: HeronLattice

    @classmethod
    def setUpClass(cls) -> None:
        cls.lattice = HeronLattice.from_snapshot(SNAPSHOT, "ibm_fez")

    def test_missing_backend_raises(self) -> None:
        with self.assertRaises(ValueError):
            HeronLattice.from_snapshot(SNAPSHOT, "nonexistent_backend")

    def test_lattice_graph_properties(self) -> None:
        self.assertEqual(self.lattice.num_qubits, 156)
        self.assertEqual(self.lattice.graph.num_edges(), 176)
        dist = self.lattice.distance_matrix()
        self.assertEqual(dist.shape, (156, 156))
        self.assertTrue((dist.diagonal() == 0).all())
        self.assertTrue((dist == dist.T).all())

    def test_guard_distance_holds_at_two_and_three(self) -> None:
        dist = self.lattice.distance_matrix()
        for distance in (2, 3):
            tiles = self.lattice.find_disjoint_tiles(k=5, min_buffer_distance=distance, max_tiles=16)
            self.assertGreaterEqual(len(tiles), 9)
            self.assertEqual(self.lattice.min_tile_distance(tiles), distance)
            for tile in tiles:
                for q in tile.buffer_qubits:
                    self.assertLess(min(int(dist[q][p]) for p in tile.qubits), distance)
        with self.assertRaises(ValueError):
            self.lattice.find_disjoint_tiles(k=5, min_buffer_distance=0)

    def test_tile_plans_pack_the_snapshot(self) -> None:
        expected = {"ibm_fez": [16, 7, 20, 12], "ibm_kingston": [16, 8, 20, 10], "ibm_marrakesh": [16, 7, 20, 12]}
        for backend, counts in expected.items():
            lattice = HeronLattice.from_snapshot(SNAPSHOT, backend)
            packed = [len(lattice.plan_tiles("k", k, n).tiles) for k, n in ((5, 16), (10, 8), (2, 20), (7, 12))]
            self.assertEqual(packed, counts, backend)

    def test_tile_duration_reads_target_durations(self) -> None:
        tile = self.lattice.find_disjoint_tiles(k=5, max_tiles=1)[0]
        expected = (
            max(self.lattice.sx_durations[q] for q in tile.qubits)
            + sum(self.lattice.cz_durations[e] for e in tile.internal_edges)
            + max(self.lattice.readout_durations[q] for q in tile.qubits)
        ) * 1e9
        self.assertAlmostEqual(tile.serial_duration_ns, expected)
        self.assertIn((146, 147), tile.internal_edges)
        self.assertAlmostEqual(self.lattice.cz_durations[(146, 147)] * 1e9, 88.0)

    def test_rzz_decomposition_uses_each_backend_durations(self) -> None:
        sx_ns = {"ibm_fez": 24.0, "ibm_kingston": 32.0, "ibm_marrakesh": 36.0}
        for backend, sx in sx_ns.items():
            summary = HeronLattice.from_snapshot(SNAPSHOT, backend).rzz_duration_summary()
            self.assertEqual(summary["sx_duration_ns"], [sx])
            self.assertEqual(summary["decomposition_ops"]["cz"], 2)
            sx_count = summary["decomposition_ops"]["sx"]
            self.assertAlmostEqual(summary["decomposed_ns"]["median"], 2 * 68.0 + sx_count * sx)

    def test_shot_rate_ratio_stays_inside_rep_delay_range(self) -> None:
        self.assertAlmostEqual(self.lattice.shot_rate_ratio(5e-6, 50e-6)["ratio"], 255 / 55, places=3)
        self.assertAlmostEqual(self.lattice.shot_rate_ratio(50e-6, 50e-6)["ratio"], 3.0)
        with self.assertRaises(ValueError):
            self.lattice.shot_rate_ratio(5e-6, 3e-3)

    def test_flag_rz_cz_sx_reads_one_qubit_line(self) -> None:
        qa, qb = self.lattice.high_error_couplers(0.004)[0]
        flagged = self.lattice.flag_rz_cz_sx([("rz", (qa,)), ("x", (99,)), ("cz", (qa, qb)), ("sx", (qa,))])
        self.assertEqual([f.gate_sequence for f in flagged], [["rz", "cz", "sx"]])
        self.assertEqual(self.lattice.flag_rz_cz_sx([("rz", (99,)), ("cz", (qa, qb)), ("sx", (qa,))]), [])
        delayed = [("rz", (qa,)), ("cz", (qa, qb)), ("delay", (qa,)), ("sx", (qa,))]
        self.assertEqual(self.lattice.flag_rz_cz_sx(delayed), [])
        qc = QuantumCircuit(156)
        qc.rz(0.5, qa)
        qc.barrier()
        qc.cz(qa, qb)
        qc.sx(qa)
        self.assertEqual(len(self.lattice.flag_rz_cz_sx(qc)), 1)

    def test_composer_rejects_overlap_and_off_tile_gates(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)
        with self.assertRaises(ValueError):
            self.lattice.build_multiplexed_pub([QuantumCircuit(5), QuantumCircuit(5)], [tiles[0], tiles[0]])
        with self.assertRaises(ValueError):
            self.lattice.build_multiplexed_pub([QuantumCircuit(6)], tiles[:1])
        qubits = tiles[0].qubits
        allowed = set(tiles[0].internal_edges)
        off = next((a, b) for a in range(5) for b in range(a + 1, 5) if (qubits[a], qubits[b]) not in allowed)
        bad = QuantumCircuit(5)
        bad.cz(*off)
        with self.assertRaises(ValueError):
            self.lattice.build_multiplexed_pub([bad], tiles[:1])
        good = QuantumCircuit(5)
        a, b = tiles[0].internal_edges[0]
        good.cz(qubits.index(a), qubits.index(b))
        self.assertEqual(self.lattice.build_multiplexed_pub([good], tiles[:1]).count_ops()["cz"], 1)
        with self.assertRaises(ValueError):
            self.lattice.build_multiplexed_pub([good], tiles[:1], min_buffer_distance=0)

    def test_routed_witnesses_compose_and_run(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=10, max_tiles=2)
        patch = self.lattice.route_to_tile(steane_z_syndrome_patch(error_qubit=2), tiles[0])
        probe = self.lattice.route_to_tile(bell_delay_probe(delay_dt=40), tiles[1])
        wide = self.lattice.build_multiplexed_pub([patch, probe], tiles)
        self.assertEqual([c.name for c in wide.cregs], ["tile_0_syn", "tile_0_data", "tile_1_c"])
        counts = AerSimulator().run(wide, shots=40, seed_simulator=7).result().get_counts()
        # Registers print last-added first: probe bits, corrected data, then syndrome 3 for X on data qubit 2.
        self.assertEqual(counts, {"00 0000000 011": 40})

    def test_feed_forward_body_is_observed(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)
        wide = self.lattice.build_multiplexed_pub([edge_circuit(tiles[0], False), edge_circuit(tiles[1], True)], tiles)
        counts = AerSimulator().run(wide, shots=20, seed_simulator=3).result().get_counts()
        self.assertEqual(counts, {"11 00": 20})

    def test_parameter_names_collide_only_across_objects(self) -> None:
        tiles = self.lattice.find_disjoint_tiles(k=5, max_tiles=2)
        circuits = []
        for _ in range(2):
            qc = QuantumCircuit(5)
            qc.rx(Parameter("theta"), 0)
            circuits.append(qc)
        wide = self.lattice.build_multiplexed_pub(circuits, tiles)
        self.assertEqual(sorted(p.name for p in wide.parameters), ["theta", "tile_1_theta"])
        shared = Parameter("phi")
        same = [QuantumCircuit(5), QuantumCircuit(5)]
        for qc in same:
            qc.rx(shared, 0)
        self.assertEqual(self.lattice.build_multiplexed_pub(same, tiles).num_parameters, 1)

        # Pre-existing generated parameter name collision avoidance
        c_pre = QuantumCircuit(5)
        c_pre.rx(Parameter("theta"), 0)
        c_pre.rx(Parameter("tile_1_theta"), 1)
        c_other = QuantumCircuit(5)
        c_other.rx(Parameter("theta"), 0)  # attempts to rename to tile_1_theta, colliding with c_pre
        wide_avoid = self.lattice.build_multiplexed_pub([c_pre, c_other], tiles)
        self.assertEqual(sorted(p.name for p in wide_avoid.parameters), ["theta", "tile_1_theta", "tile_1_theta_1"])

        pub = HeronLattice.pack_parameter_sweep_pub(wide, [[0.0, 0.5], [0.5, 1.0], [1.0, 1.5]], shots=2048)
        self.assertEqual(pub[1].shape, (3, 2))
        for values in ([[0.0, 0.5, 1.0]], [[float("nan"), 0.0]], [[0.0, 0.0]][:0]):
            with self.assertRaises(ValueError):
                HeronLattice.pack_parameter_sweep_pub(wide, values)

    def test_basis_rotations_touch_terminal_measures_only(self) -> None:
        plus = QuantumCircuit(1)
        plus.h(0)
        self.assertAlmostEqual(Statevector(HeronLattice.append_basis_rotations(plus, "X")).probabilities()[0], 1.0)
        plus_i = QuantumCircuit(1)
        plus_i.h(0)
        plus_i.s(0)
        self.assertAlmostEqual(Statevector(HeronLattice.append_basis_rotations(plus_i, "Y")).probabilities()[0], 1.0)
        qc = QuantumCircuit(2, 3)
        qc.measure(0, 0)
        qc.x(0)
        qc.measure(0, 1)
        qc.measure(1, 2)
        rotated = HeronLattice.append_basis_rotations(qc, {0: "X", 1: "Y"})
        names = [inst.operation.name for inst in rotated.data]
        self.assertEqual(names, ["measure", "x", "h", "measure", "sdg", "h", "measure"])

    def test_lcu_witness_is_certified_by_cd_core(self) -> None:
        sim = AerSimulator()
        for sign, success in ((-1, 0.0), (1, 1.0)):
            witness = lcu_zero_product_witness(sign=sign)
            self.assertAlmostEqual(witness.metadata["p_success"], success)
            counts = sim.run(transpile(witness, sim), shots=200, seed_simulator=1).result().get_counts()
            self.assertEqual(counts.get("0", 0) / 200, success)
        self.assertAlmostEqual(lcu_zero_product_witness((1, 10), (2, 13), -1).metadata["p_success"], 0.5)

    def test_steane_syndrome_names_the_flipped_qubit(self) -> None:
        sim = AerSimulator()
        for error in (None, *range(7)):
            counts = sim.run(steane_z_syndrome_patch(error), shots=20, seed_simulator=5).result().get_counts()
            syndrome = 0 if error is None else error + 1
            self.assertEqual(counts, {f"0000000 {syndrome:03b}": 20})
            if error is not None:
                fired = [bit for bit, support in enumerate(STEANE_Z_CHECKS) if error in support]
                self.assertEqual(fired, [bit for bit in range(3) if syndrome >> bit & 1])
        hardware = steane_z_syndrome_patch(1, mid_circuit_measure=True)
        self.assertEqual(hardware.count_ops()["measure_2"], 3)

    def test_parity_covariance_values_and_inputs(self) -> None:
        result = HeronLattice.tile_parity_covariance(["00", "11", "11", "00", "01", "10"], [slice(0, 1), slice(1, 2)])
        self.assertEqual(result["means"], [0.0, 0.0])
        self.assertAlmostEqual(result["covariance_matrix"][0][1], 1 / 3, places=5)
        little = HeronLattice.tile_parity_covariance(["10", "10"], [slice(0, 1)], endianness="little")
        self.assertEqual(little["means"], [1.0])
        registers = HeronLattice.tile_parity_covariance({"tile_0_c": ["0", "1"] * 5, "tile_1_c": ["1", "0"] * 5})
        self.assertAlmostEqual(registers["covariance_matrix"][0][1], -1.0)
        for strings, slices in ((["0", "0"], [slice(0, 5)]), (["00", "0"], [slice(0, 1)]), (["00"], [slice(0, 1)])):
            with self.assertRaises(ValueError):
                HeronLattice.tile_parity_covariance(strings, slices)
        with_coords = HeronLattice.tile_parity_covariance(
            ["00", "11"],
            [slice(0, 1), slice(1, 2)],
            tile_coords=[(0.0, 0.0), (3.0, 4.0)],
        )
        self.assertEqual(with_coords["distance_matrix"][0][1], 5.0)
        with self.assertRaises(ValueError):
            HeronLattice.tile_parity_covariance(["00", "11"], [slice(0, 1), slice(1, 2)], tile_coords=[(0.0, 0.0)])
        with self.assertRaises(ValueError):
            HeronLattice.tile_parity_covariance(["00", "11"], [slice(0, 1)], endianness="invalid")
        with self.assertRaises(ValueError):
            HeronLattice.tile_parity_covariance(["00", "11"], tile_clbit_slices=[])

    def test_sedenion_and_pathion_witnesses(self) -> None:
        # Non-associating triple (1, 2, 4): P(anc=1) = 1.0
        qc_nonassoc = sedenion_associator_witness(1, 2, 4)
        self.assertEqual(qc_nonassoc.num_qubits, 5)
        sv1 = Statevector(qc_nonassoc.remove_final_measurements(inplace=False))
        self.assertAlmostEqual(float(sv1.probabilities([4])[1]), 1.0)

        # Associating triple (1, 2, 3): P(anc=0) = 1.0
        qc_assoc = sedenion_associator_witness(1, 2, 3)
        sv2 = Statevector(qc_assoc.remove_final_measurements(inplace=False))
        self.assertAlmostEqual(float(sv2.probabilities([4])[0]), 1.0)

        # Pathion associator spectrum witness on 5 qubits
        qc_pathion = pathion_associator_spectrum_witness(32, 1, 16)
        self.assertEqual(qc_pathion.num_qubits, 5)

        with self.assertRaises(ValueError):
            sedenion_associator_witness(16, 2, 4)
        with self.assertRaises(ValueError):
            sedenion_associator_witness(-1, 2, 4)
        with self.assertRaises(ValueError):
            pathion_associator_spectrum_witness(dim=15, i=1, j=16)
        with self.assertRaises(ValueError):
            pathion_associator_spectrum_witness(dim=32, i=32, j=16)

    def test_steane_coherent_and_fano_plane(self) -> None:
        # All 7 single-qubit errors correctly and coherently corrected
        for err in range(7):
            qc_coh = steane_coherent_syndrome_patch(err)
            self.assertEqual(qc_coh.num_qubits, 10)
            sv_coh = Statevector(qc_coh.remove_final_measurements(inplace=False))
            self.assertAlmostEqual(float(sv_coh.probabilities(range(7))[0]), 1.0)

        qc_coh_none = steane_coherent_syndrome_patch(None)
        sv_coh_none = Statevector(qc_coh_none.remove_final_measurements(inplace=False))
        self.assertAlmostEqual(float(sv_coh_none.probabilities(range(7))[0]), 1.0)
        with self.assertRaises(ValueError):
            steane_coherent_syndrome_patch(7)
        with self.assertRaises(ValueError):
            steane_coherent_syndrome_patch(-1)
        with self.assertRaises(ValueError):
            steane_z_syndrome_patch(1, idle_delay_dt=-10)

        # Fano plane PG(2,2) incidence matrix
        fano = fano_plane_incidence_matrix()
        self.assertEqual(fano.shape, (7, 7))
        self.assertTrue((fano.sum(axis=1) == 3).all())
        self.assertTrue((fano.sum(axis=0) == 3).all())

        # Dynamical decoupling on Steane Z syndrome patch with CPMG-2 and XY4
        sim = AerSimulator()
        for dd in ("CPMG2", "XY4"):
            for err_target in (None, 1):
                qc = steane_z_syndrome_patch(err_target, dd_sequence=dd, idle_delay_dt=100)
                counts = sim.run(qc, shots=50, seed_simulator=42).result().get_counts()
                expected_syn = 0 if err_target is None else err_target + 1
                self.assertEqual(counts, {f"0000000 {expected_syn:03b}": 50})

        # Preserves idle_delay_dt=0 without forcing delay insertion
        qc_zero_delay = steane_z_syndrome_patch(1, dd_sequence="CPMG2", idle_delay_dt=0)
        self.assertEqual(qc_zero_delay.count_ops().get("delay", 0), 0)
        self.assertEqual(qc_zero_delay.count_ops().get("x", 1), 1)

        qc_cpmg = steane_z_syndrome_patch(1, dd_sequence="CPMG2", idle_delay_dt=100)
        self.assertEqual(qc_cpmg.count_ops().get("delay", 0), 21)
        self.assertEqual(qc_cpmg.count_ops().get("x", 0), 15)  # 2 X per 7 data qubits + 1 error

        qc_xy4 = steane_z_syndrome_patch(1, dd_sequence="XY4", idle_delay_dt=100)
        self.assertEqual(qc_xy4.count_ops().get("delay", 0), 35)
        self.assertEqual(qc_xy4.count_ops().get("y", 0), 14)  # 2 Y per 7 data qubits
        with self.assertRaises(ValueError):
            steane_z_syndrome_patch(1, dd_sequence="invalid_dd")
        with self.assertRaises(ValueError):
            steane_z_syndrome_patch(1, dd_sequence="Hahn")

    def test_bell_delay_probe_with_dd(self) -> None:
        for dd in (None, "Hahn", "XY4"):
            qc = bell_delay_probe(100, dd_sequence=dd)
            self.assertEqual(qc.num_qubits, 2)
            sv = Statevector(qc.remove_final_measurements(inplace=False))
            self.assertAlmostEqual(float(sv.probabilities()[0]), 1.0)
        with self.assertRaises(ValueError):
            bell_delay_probe(-1)
        with self.assertRaises(ValueError):
            bell_delay_probe(0, dd_sequence="invalid_dd")
        with self.assertRaises(ValueError):
            bell_delay_probe(100, dd_sequence="invalid_dd")

    def test_hoeffding_model_discrimination(self) -> None:
        p = {"0": 8000, "1": 192}
        q = {"0": 1000, "1": 7192}
        res = hoeffding_model_discrimination(p, q, alpha=0.01, alphabet_size=2)
        self.assertEqual(hoeffding_model_discrimination(p, q, 0.01, alphabet_size=2), res)
        self.assertTrue(res["models_distinguishable"])
        self.assertGreater(res["total_variation_distance"], 0.8)
        self.assertLess(res["hoeffding_radius"], 0.05)
        self.assertGreater(res["tv_confidence_interval"][0], 0.0)

        # Independent samples from the same underlying distribution are not distinguishable
        sample_a = {"00": 1040, "01": 1010, "10": 1030, "11": 1016}
        sample_b = {"00": 1005, "01": 1050, "10": 1015, "11": 1026}
        same_source = hoeffding_model_discrimination(sample_a, sample_b, alpha=0.01, alphabet_size=4)
        self.assertFalse(same_source["models_distinguishable"])
        self.assertEqual(same_source["tv_confidence_interval"][0], 0.0)
        self.assertGreater(same_source["multinomial_tv_radius"], same_source["total_variation_distance"])

        # alphabet_size contracts
        res_alpha = hoeffding_model_discrimination(sample_a, sample_b, alpha=0.01, alphabet_size=64)
        self.assertEqual(res_alpha["k_bins"], 64)
        self.assertGreater(res_alpha["multinomial_tv_radius"], same_source["multinomial_tv_radius"])
        sparse_counts = {"00": 4096}
        sparse_support = hoeffding_model_discrimination(sparse_counts, sparse_counts, alphabet_size=4)
        observed_only_support = hoeffding_model_discrimination(sparse_counts, sparse_counts, alphabet_size=1)
        self.assertEqual(sparse_support["k_bins"], 4)
        self.assertGreater(sparse_support["multinomial_tv_radius"], observed_only_support["multinomial_tv_radius"])
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination(sample_a, sample_b, alphabet_size=2)
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination(sample_a, sample_b, alphabet_size=0)
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination(sample_a, sample_b, alphabet_size=-5)

        with self.assertRaises(ValueError):
            hoeffding_model_discrimination({}, q, alphabet_size=2)
        with self.assertRaises(TypeError):
            hoeffding_model_discrimination(p, q)
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination(p, q, alpha=0.0, alphabet_size=2)
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination(p, q, alpha=1.0, alphabet_size=2)
        with self.assertRaises(ValueError):
            hoeffding_model_discrimination({"0": -1}, q, alphabet_size=2)

    def test_bent_hidden_shift_circuit(self) -> None:
        for n in (4, 6):
            s = [1 if i % 2 == 0 else 0 for i in range(n)]
            qc = bent_hidden_shift_circuit(n, s)
            self.assertEqual(qc.num_qubits, n)
            sv = Statevector(qc.remove_final_measurements(inplace=False))
            expected = "".join(str(s[i]) for i in reversed(range(n)))
            self.assertAlmostEqual(float(sv.probabilities_dict()[expected]), 1.0)
        with self.assertRaises(ValueError):
            bent_hidden_shift_circuit(5)  # Odd n must raise
        with self.assertRaises(ValueError):
            bent_hidden_shift_circuit(4, shift=[1, 0])  # Length mismatch


if __name__ == "__main__":
    unittest.main()
