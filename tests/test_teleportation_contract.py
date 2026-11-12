"""Bounded fixtures; no retained acquisition, provider, random draw or renderer."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock

import numpy as np
import qi_teleportation_design
from qi_teleportation_design import analyze, write_bundle

from teleportation_contract import (
    ALIGN,
    BY_LABEL,
    STATES,
    Basis,
    circuit,
    decode,
    make_plan,
    score_histogram,
    six_state_estimate,
    validate_plan,
    validate_roles,
    validate_route,
)

H = np.array([[1, 1], [1, -1]], complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
S = np.diag([1, 1j]).astype(complex)
GATES = {"H": H, "X": X, "S": S, "Sdag": S.conj().T}


def logical_state(label: str, reverse_bell: bool = False) -> np.ndarray:
    """Independent 16-amplitude reference with logical qubit zero least significant."""
    initial = {
        "0": [1, 0],
        "1": [0, 1],
        "+": np.array([1, 1]) / math.sqrt(2),
        "-": np.array([1, -1]) / math.sqrt(2),
        "+i": np.array([1, 1j]) / math.sqrt(2),
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
    return {
        "input": label,
        "shots": n,
        "correct": round(n * fraction),
        "route": [0, 1, 2, 3],
        "channel_id": "fixture-channel",
        "calibration_id": "fixture-epoch",
        "selection": "all_shots",
    }


def fixture_plan() -> tuple[dict, dict[str, str]]:
    # Deliberate counterbalanced fixture, not a sampled or acquired record.
    return make_plan(
        "fixture",
        1,
        8,
        [[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7]],
        [[0, 1, 2, 3], [4, 5, 6, 7]],
        16,
        [list(range(12)), list(reversed(range(12)))],
        3,
    )


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


def placed_counts(label: str, route: list[int], nqubits: int, shots: int, reverse_bell: bool = False) -> dict[str, int]:
    """Full-register histogram of the ideal circuit with logical qubit q on register qubit route[q].

    Register qubits outside the route read zero; Q0 is the rightmost character.
    """
    counts: dict[str, int] = {}
    probability = abs(logical_state(label, reverse_bell)) ** 2
    for index, p in enumerate(probability):
        if p < 1e-12:
            continue
        bits = ["0"] * nqubits
        for logical, physical in enumerate(route):
            bits[nqubits - 1 - physical] = str((index >> logical) & 1)
        counts["".join(bits)] = round(p * shots)
    return counts


class RouteScoringTests(unittest.TestCase):
    def test_score_reads_the_roles_from_the_route(self) -> None:
        # A route-ignoring parser reads register qubits 0, 1, 3 and sees only zeros on these routes.
        for route in ([5, 4, 3, 2], [7, 0, 6, 2], [3, 6, 1, 5]):
            for spec in STATES:
                counts = placed_counts(spec.label, route, 8, 1600)
                self.assertEqual(sum(counts.values()), 1600)
                score = score_histogram(counts, 8, route, spec.label)
                self.assertEqual((score["shots"], score["correct"]), (1600, 1600))
                self.assertEqual(
                    {k: v["shots"] for k, v in score["branches"].items()}, dict.fromkeys(score["branches"], 400)
                )
                self.assertEqual(
                    {k: v["correct"] for k, v in score["branches"].items()}, dict.fromkeys(score["branches"], 400)
                )

    def test_a_wrong_route_scores_the_wrong_qubits(self) -> None:
        counts = placed_counts("1", [5, 4, 3, 2], 8, 1600)
        for wrong in ([0, 1, 2, 3], [4, 5, 3, 2], [5, 4, 2, 3]):
            score = score_histogram(counts, 8, wrong, "1")
            self.assertLess(score["correct"], score["shots"])

    def test_branch_labels_follow_the_route_roles(self) -> None:
        # One shot with I=1, P1=0, D=0 on route [5, 4, 3, 2] lands in branch "10" and decodes Z as d xor b = 0.
        outcome = "00100000"
        score = score_histogram({outcome: 3}, 8, [5, 4, 3, 2], "0")
        self.assertEqual(score["branches"]["10"], {"shots": 3, "correct": 3})
        self.assertEqual(score["branches"]["00"], {"shots": 0, "correct": 0})

    def test_coupling_graph_is_checked_when_supplied(self) -> None:
        edges = [[0, 1], [1, 2], [2, 3]]
        counts = {"0000": 1}
        score_histogram(counts, 4, [0, 1, 2, 3], "0", edges)
        with self.assertRaises(ValueError):
            score_histogram(counts, 4, [0, 1, 3, 2], "0", edges)
        with self.assertRaises(ValueError):
            circuit(4, [0, 1, 3, 2], "0", edges)
        self.assertIn("CNOT q[1], q[2]", circuit(4, [0, 1, 2, 3], "0", edges))

    def test_role_check_claims_only_shape_and_range(self) -> None:
        self.assertEqual(validate_roles([3, 1, 2, 0]), (3, 1, 2, 0))
        self.assertEqual(validate_roles([3, 1, 2, 0], 4), (3, 1, 2, 0))
        for route, width in (([0, 0, 1, 2], None), ([0, 1, 2], None), ([0, 1, 2, 4], 4), ([0, 1, 2, True], None)):
            with self.assertRaises(ValueError):
                validate_roles(cast(Any, route), width)
        # Distinct in-range qubits pass although no coupling joins them.
        self.assertEqual(validate_roles([0, 2, 1, 3], 4), (0, 2, 1, 3))
        with self.assertRaises(ValueError):
            validate_route([0, 2, 1, 3], 4, [[0, 1], [1, 2], [2, 3]])


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
        mutations = [
            ("shots", 0),
            ("orders", [[0] * 12]),
            ("postselection", True),
            ("routes", [[0, 0, 2, 3]]),
            ("readout", "postselected"),
        ]
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


def sha(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def collect_case(
    case: Path,
    plan: dict,
    *,
    skip_batches: tuple[str, ...] = (),
    shots_done: int | None = None,
    failed_job: bool = False,
) -> list[Path]:
    """Add the submission receipt, collection and raw shots that qi_records reads to each prepared batch.

    Every circuit returns its ideal histogram on its own route, so a faithful analysis scores every group
    perfectly. The synthetic job identifiers and receipts stand for no provider job.
    """
    shots = plan["shots"]
    directories = []
    job_id = 100
    for batch in plan["batches"]:
        directory = case / batch["batch"]
        if batch["batch"] in skip_batches:
            continue
        directory.mkdir(exist_ok=True)
        (directory / "raw").mkdir()
        cases_text = (directory / "cases.json").read_text()
        receipt_jobs: list[dict[str, Any]] = []
        collected: list[dict[str, Any]] = []
        for row in batch["circuits"]:
            job_id += 1
            route = plan["routes"][row["route_index"]]
            histogram = placed_counts(row["input"], route, plan["nqubits"], shots)
            if shots_done is not None:
                histogram = {key: value * shots_done // shots for key, value in histogram.items()}
            done = sum(histogram.values())
            failed = failed_job and not collected
            receipt_jobs.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
            collected.append(
                {
                    "file": row["file"],
                    "job": {
                        "id": job_id,
                        "batch_job_id": 7,
                        "created_on": "2026-01-01T00:00:00Z",
                        "number_of_shots": shots,
                        "status": "failed" if failed else "completed",
                    },
                    "results": []
                    if failed
                    else [{"job_id": job_id, "shots_requested": shots, "shots_done": done, "results": histogram}],
                }
            )
            if not failed:
                raw = [key for key, count in histogram.items() for _ in range(count)]
                (directory / "raw" / f"{row['file']}.json").write_text(json.dumps(raw))
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "approval": "synthetic fixture",
            "batch_job": 7,
            "backend": plan["backend"],
            "backend_type_id": plan["backend_type_id"],
            "shots": shots,
            "cases_sha256": sha(cases_text),
            "jobs": receipt_jobs,
        }
        (directory / "submission.json").write_text(json.dumps(receipt))
        (directory / "results.json").write_text(
            json.dumps({"schema": "qi-collection-v1", "transactions": [], "jobs": collected})
        )
        directories.append(directory)
    return directories


class AnalyzeCliTests(unittest.TestCase):
    """The analyze path on a constructed run: no seed, provider call or retained record."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.plan, files = fixture_plan()
        self.case = self.root / "case"
        write_bundle(self.case, self.plan, files)
        self.plan_path = self.case / "plan.json"
        self.calibration = self.root / "calibration.json"
        self.calibration.write_text("{}\n")

    def collect(self, **options: Any) -> list[Path]:
        return collect_case(self.case, self.plan, **options)

    def test_complete_run_reports_every_group_with_family_alpha(self) -> None:
        result = analyze(self.plan_path, self.collect(), self.calibration, 0.05)
        self.assertEqual(result["family_alpha"], 0.05)
        self.assertEqual(result["plan_sha256"], hashlib.sha256(self.plan_path.read_bytes()).hexdigest())
        self.assertEqual([(g["block"], g["route_index"]) for g in result["groups"]], [(0, 0), (0, 1), (1, 0), (1, 1)])
        # Bonferroni over the 2 blocks x 2 routes planned groups: alpha / 4 enters the radius.
        radius = math.sqrt(-math.log(0.05 / 4) * math.fsum([1 / 16] * 6) / 72)
        for group in result["groups"]:
            self.assertEqual(len(group["rows"]), 6)
            self.assertEqual(group["estimate"]["mean"], 1)
            self.assertAlmostEqual(group["estimate"]["sampling_radius"], radius)
            self.assertEqual({r["selection"] for r in group["rows"]}, {"all_shots"})
        self.assertEqual(result["instrument_admission"], "not_independently_certified_by_this_analysis")
        self.assertEqual(
            [p["batch"] for p in result["acquisition_provenance"]], [b["batch"] for b in self.plan["batches"]]
        )

    def test_group_rows_carry_their_own_route_and_channel(self) -> None:
        result = analyze(self.plan_path, self.collect(), self.calibration, 0.05)
        for group in result["groups"]:
            route = self.plan["routes"][group["route_index"]]
            self.assertEqual({tuple(r["route"]) for r in group["rows"]}, {tuple(route)})
            self.assertEqual(
                {r["channel_id"].rsplit(":", 1)[1] for r in group["rows"]}, {f"route-{group['route_index']}"}
            )

    def test_cli_main_prints_the_analysis_and_rejects_through_the_parser(self) -> None:
        directories = [str(path) for path in self.collect()]
        argv = ["qi_teleportation_design.py", "analyze", "--plan", str(self.plan_path)]
        argv += ["--calibration-record", str(self.calibration), *directories]
        out = io.StringIO()
        with mock.patch("sys.argv", argv), contextlib.redirect_stdout(out):
            self.assertEqual(qi_teleportation_design.main(), 0)
        self.assertEqual(json.loads(out.getvalue())["schema"], "qi-fixed-route-six-state-analysis-v1")
        with (
            mock.patch("sys.argv", [*argv, directories[0]]),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as raised,
        ):
            qi_teleportation_design.main()
        self.assertEqual(raised.exception.code, 2)

    def rejected(self, message: str, directories: list[Path], plan_path: Path | None = None) -> None:
        with self.assertRaisesRegex(ValueError, message):
            analyze(plan_path or self.plan_path, directories, self.calibration, 0.05)

    def test_missing_batch_is_rejected(self) -> None:
        directories = self.collect(skip_batches=("batch-0007",))
        self.rejected("every scheduled batch must be present", directories)

    def test_repeated_batch_directory_is_rejected(self) -> None:
        directories = self.collect()
        self.rejected("unknown or duplicate acquisition batch", [*directories, directories[0]])

    def test_repeated_job_identifiers_are_rejected(self) -> None:
        # qi_records rejects a repeat inside one batch; the same id across batches reaches the analyzer's own check.
        directories = self.collect()
        first = json.loads((directories[1] / "submission.json").read_text())
        results = json.loads((directories[1] / "results.json").read_text())
        for index, (row, collected) in enumerate(zip(first["jobs"], results["jobs"], strict=True)):
            row["job"] = collected["job"]["id"] = collected["results"][0]["job_id"] = 101 + index
        (directories[1] / "submission.json").write_text(json.dumps(first))
        (directories[1] / "results.json").write_text(json.dumps(results))
        self.rejected("same provider job appears twice", directories)

    def test_run_bound_to_another_plan_is_rejected(self) -> None:
        directories = self.collect()
        other = self.root / "other-plan.json"
        other.write_text(self.plan_path.read_text() + "\n")
        self.rejected("acquisition is not bound to this plan", directories, other)

    def test_short_shot_count_is_rejected_not_renormalized(self) -> None:
        self.rejected("missing shots", self.collect(shots_done=12))

    def test_incomplete_job_is_rejected(self) -> None:
        self.rejected("incomplete acquisition cannot be scored", self.collect(failed_job=True))

    def test_circuit_rows_that_differ_from_the_plan_are_rejected(self) -> None:
        directories = self.collect()
        cases = json.loads((directories[0] / "cases.json").read_text())
        cases["circuits"][0]["input"] = "1" if cases["circuits"][0]["input"] == "0" else "0"
        text = json.dumps(cases)
        (directories[0] / "cases.json").write_text(text)
        receipt = json.loads((directories[0] / "submission.json").read_text())
        receipt["cases_sha256"] = sha(text)
        (directories[0] / "submission.json").write_text(json.dumps(receipt))
        self.rejected("acquisition circuit rows differ from plan", directories)

    def test_histogram_laid_out_on_another_route_scores_below_perfect(self) -> None:
        # The other route's qubits read zero on this route, so an input whose expected bit is 1 mismatches.
        directories = self.collect()
        directory = directories[0]
        index, spec = next(
            (i, r) for i, r in enumerate(self.plan["batches"][0]["circuits"]) if BY_LABEL[r["input"]].expected
        )
        results = json.loads((directory / "results.json").read_text())
        histogram = placed_counts(spec["input"], self.plan["routes"][1 - spec["route_index"]], 8, self.plan["shots"])
        results["jobs"][index]["results"][0]["results"] = histogram
        (directory / "results.json").write_text(json.dumps(results))
        raw = [key for key, count in histogram.items() for _ in range(count)]
        (directory / "raw" / f"{spec['file']}.json").write_text(json.dumps(raw))
        result = analyze(self.plan_path, directories, self.calibration, 0.05)
        group = next(
            g for g in result["groups"] if (g["block"], g["route_index"]) == (spec["block"], spec["route_index"])
        )
        scored = next(r for r in group["rows"] if r["input"] == spec["input"])
        self.assertLess(scored["match"], 1)
        self.assertLess(group["estimate"]["mean"], 1)


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
        rows = [row(s.label, 1 if index == 0 else 0, 10000 if index == 0 else 10) for index, s in enumerate(STATES)]
        self.assertAlmostEqual(six_state_estimate(rows)["mean"], 1 / 6)

    def test_no_cross_route_epoch_or_selection_pooling(self) -> None:
        for key, value in (
            ("route", [4, 5, 6, 7]),
            ("channel_id", "other"),
            ("calibration_id", "other"),
            ("selection", "postselected"),
        ):
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
