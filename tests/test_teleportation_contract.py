"""Bounded fixtures; no retained acquisition, provider, random draw or renderer."""

from __future__ import annotations

import copy
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

import numpy as np

from teleportation_contract import (
    ALIGN, BY_LABEL, STATES, Basis, circuit, decode, make_plan, score_histogram,
    six_state_estimate, validate_plan, validate_route,
)
from qi_teleportation_design import analyze, write_bundle

H = np.array([[1, 1], [1, -1]], complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
S = np.diag([1, 1j]).astype(complex)
GATES = {"H": H, "X": X, "S": S, "Sdag": S.conj().T}


def logical_state(label: str, reverse_bell: bool = False) -> np.ndarray:
    """Independent 16-amplitude reference with logical qubit zero least significant."""
    initial = {
        "0": [1, 0], "1": [0, 1], "+": np.array([1, 1]) / math.sqrt(2),
        "-": np.array([1, -1]) / math.sqrt(2), "+i": np.array([1, 1j]) / math.sqrt(2),
        "-i": np.array([1, -1j]) / math.sqrt(2),
    }
    state = np.zeros(16, complex)
    state[:2] = initial[label]

    def single(matrix: np.ndarray, q: int) -> None:
        nonlocal state
        out = np.zeros_like(state)
        for index, amplitude in enumerate(state):
            for target in (0, 1):
                out[(index & ~(1 << q)) | (target << q)] += matrix[target, (index >> q) & 1] * amplitude
        state = out

    def cx(control: int, target: int) -> None:
        nonlocal state
        out = np.zeros_like(state)
        for index, amplitude in enumerate(state):
            out[index ^ ((1 << target) if (index >> control) & 1 else 0)] = amplitude
        state = out

    single(H, 1)
    cx(1, 2)
    # Independent SWAP decomposition, not the emitter's SWAP instruction.
    cx(2, 3)
    cx(3, 2)
    cx(2, 3)
    if reverse_bell:
        single(H, 0)
        cx(0, 1)
    else:
        cx(0, 1)
        single(H, 0)
    for gate in ALIGN[BY_LABEL[label].basis]:
        single(GATES[gate], 3)
    return state


def row(label: str, fraction: float = 1.0, n: int = 1000) -> dict:
    return {"input": label, "shots": n, "correct": round(n * fraction), "route": [0, 1, 2, 3],
            "channel_id": "fixture-channel", "calibration_id": "fixture-epoch", "selection": "all_shots"}


def fixture_plan() -> tuple[dict, dict[str, str]]:
    # Deliberate counterbalanced fixture, not a sampled or acquired record.
    return make_plan("fixture", 1, 8, [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]],
                     [[0, 1, 2, 3], [4, 5, 6, 7]], 16,
                     [list(range(12)), list(reversed(range(12)))], 3)


class FrameTests(unittest.TestCase):
    def test_every_basis_branch_and_bit(self) -> None:
        for basis, flip in (("Z", lambda a, b: b), ("X", lambda a, b: a), ("Y", lambda a, b: a ^ b)):
            for a in (0, 1):
                for b in (0, 1):
                    for d in (0, 1):
                        self.assertEqual(decode(cast(Basis, basis), d, a, b), d ^ flip(a, b))

    def test_invalid_bits_are_not_coerced(self) -> None:
        for bad in (-1, 2, True, 0.0, "0", None):
            for index in range(3):
                args: list[Any] = [0, 0, 0]
                args[index] = bad
                with self.assertRaises(ValueError):
                    decode("Y", *args)
        with self.assertRaises(ValueError):
            decode(cast(Any, "Q"), 0, 0, 0)

    def test_six_states_all_bell_branches(self) -> None:
        for spec in STATES:
            state = logical_state(spec.label)
            probability = abs(state) ** 2
            self.assertAlmostEqual(float(probability.sum()), 1)
            branches = [0.0] * 4
            raw = [0.0, 0.0]
            for index, p in enumerate(probability):
                a, b, p2, d = [(index >> q) & 1 for q in range(4)]
                branches[a + 2 * b] += p
                raw[d] += p
                if p > 1e-12:
                    self.assertEqual(p2, 0)
                    self.assertEqual(decode(spec.basis, d, a, b), spec.expected)
            np.testing.assert_allclose(branches, [0.25] * 4, atol=1e-12)
            np.testing.assert_allclose(raw, [0.5, 0.5], atol=1e-12)

    def test_y_global_phase_does_not_invert(self) -> None:
        plus_i = np.array([1, 1j]) / math.sqrt(2)
        basis = H @ S.conj().T
        for a in (0, 1):
            for b in (0, 1):
                state = basis @ np.linalg.matrix_power(X, b) @ np.linalg.matrix_power(Z, a) @ plus_i
                self.assertAlmostEqual(float(abs(state[a ^ b]) ** 2), 1)
                self.assertAlmostEqual(float(abs(state[a ^ b ^ 1]) ** 2), 0)

    def test_reversed_bell_gate_mutation_is_detected(self) -> None:
        score = 0.0
        spec = BY_LABEL["+i"]
        for index, p in enumerate(abs(logical_state(spec.label, reverse_bell=True)) ** 2):
            a, b, _, d = [(index >> q) & 1 for q in range(4)]
            score += p * (decode(spec.basis, d, a, b) == spec.expected)
        self.assertLess(score, 0.999)

    def test_parser_bit_order_and_branch_denominators(self) -> None:
        for spec in STATES:
            counts = {format(i, "04b"): 8 for i, p in enumerate(abs(logical_state(spec.label)) ** 2) if p > 1e-12}
            score = score_histogram(counts, 4, [0, 1, 2, 3], spec.label)
            self.assertEqual(score["shots"], 32)
            self.assertEqual(score["correct"], 32)
            self.assertEqual([r["shots"] for r in score["branches"].values()], [8] * 4)

    def test_histogram_rejects_invalid_records(self) -> None:
        for counts in ({}, {"001": 1}, {"000x": 1}, {"0000": -1}, {"0000": True}, {"0000": 1.5}):
            with self.assertRaises(ValueError):
                score_histogram(cast(Any, counts), 4, [0, 1, 2, 3], "0")


class DesignTests(unittest.TestCase):
    def test_every_input_crosses_every_route_and_block(self) -> None:
        plan, files = fixture_plan()
        self.assertEqual(validate_plan(plan), files)
        cells = [(r["block"], r["route_index"], r["input"]) for b in plan["batches"] for r in b["circuits"]]
        self.assertEqual(len(cells), 24)
        self.assertEqual(len(set(cells)), 24)
        self.assertFalse(plan["postselection"])
        self.assertFalse(plan["live_output_demonstrated"])
        self.assertTrue(all(len(b["circuits"]) <= 3 for b in plan["batches"]))

    def test_gate_order_and_alignment(self) -> None:
        text = circuit(4, [0, 1, 2, 3], "+i")
        self.assertLess(text.index("CNOT q[0], q[1]"), text.index("H q[0]", text.index("SWAP")))
        self.assertIn("Sdag q[3]\nH q[3]\nbarrier q\nb = measure q", text)
        self.assertNotIn("X q[3]", circuit(4, [0, 1, 2, 3], "1"))
        self.assertEqual(circuit(4, [0, 1, 2, 3], "1").splitlines()[5], "X q[0]")

    def test_plan_mutations_fail_closed(self) -> None:
        plan, _ = fixture_plan()
        mutations = [("shots", 0), ("orders", [[0] * 12]), ("postselection", True),
                     ("routes", [[0, 0, 2, 3]]), ("readout", "postselected")]
        for key, value in mutations:
            bad = copy.deepcopy(plan)
            bad[key] = value
            with self.assertRaises(ValueError):
                validate_plan(bad)
        bad = copy.deepcopy(plan)
        bad["batches"][0]["circuits"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_plan(bad)

    def test_topology_checks(self) -> None:
        for route in ([0, 0, 1, 2], [0, 1, 2], [0, 1, 2, 9]):
            with self.assertRaises(ValueError):
                validate_route(route, 4, [[0, 1], [1, 2], [2, 3]])
        with self.assertRaises(ValueError):
            validate_route([0, 1, 2, 3], 4, [[0, 1], [1, 2]])

    def test_bundle_is_complete_and_never_overwrites(self) -> None:
        plan, files = fixture_plan()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case"
            write_bundle(target, plan, files)
            self.assertTrue((target / "plan.json").is_file())
            for name, data in files.items():
                self.assertEqual((target / name).read_text(), data)
            before = (target / "plan.json").read_bytes()
            with self.assertRaises(ValueError):
                write_bundle(target, plan, files)
            self.assertEqual((target / "plan.json").read_bytes(), before)


class StatisticsTests(unittest.TestCase):
    def test_perfect_six_state_fixture(self) -> None:
        result = six_state_estimate([row(s.label) for s in STATES])
        self.assertEqual(result["mean"], 1)
        self.assertTrue(result["lower_exceeds_classical_bound"])
        self.assertFalse(result["live_output_demonstrated"])
        self.assertAlmostEqual(result["sampling_radius"], math.sqrt(math.log(20) / 12000))

    def test_measure_prepare_boundary_is_not_promoted(self) -> None:
        rows = [row(s.label, 1 if s.basis == "Z" else 0.5) for s in STATES]
        result = six_state_estimate(rows)
        self.assertAlmostEqual(result["mean"], 2 / 3)
        self.assertFalse(result["lower_exceeds_classical_bound"])

    def test_equal_input_weights_not_shot_weights(self) -> None:
        rows = [row(s.label, 1 if index == 0 else 0, 10000 if index == 0 else 10)
                for index, s in enumerate(STATES)]
        self.assertAlmostEqual(six_state_estimate(rows)["mean"], 1 / 6)

    def test_no_cross_route_epoch_or_selection_pooling(self) -> None:
        for key, value in (("route", [4, 5, 6, 7]), ("channel_id", "other"),
                           ("calibration_id", "other"), ("selection", "postselected")):
            rows = [row(s.label) for s in STATES]
            rows[0][key] = value
            with self.assertRaises(ValueError):
                six_state_estimate(rows)

    def test_family_alpha_is_checked_before_allocation_or_io(self) -> None:
        for alpha in (0, 1, 2, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                analyze(Path("absent-plan"), [], Path("absent-calibration"), alpha)

    def test_missing_duplicate_and_bad_counts(self) -> None:
        rows = [row(s.label) for s in STATES]
        for bad in (rows[:4], rows[:5] + [rows[0]]):
            with self.assertRaises(ValueError):
                six_state_estimate(bad)
        for key, value in (("shots", 0), ("correct", 1001), ("shots", True), ("calibration_id", "")):
            bad = copy.deepcopy(rows)
            bad[0][key] = value
            with self.assertRaises(ValueError):
                six_state_estimate(bad)
        for alpha in (0, 1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                six_state_estimate(rows, alpha)


if __name__ == "__main__":
    unittest.main()
