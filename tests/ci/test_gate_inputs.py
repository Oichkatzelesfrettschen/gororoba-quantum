"""Behavioral contracts for changed-input replay selection and timing records."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

import gate_inputs
import pytest
import run_gates

pytestmark = pytest.mark.audit

SLOW_FULL_GATES = (
    "core-339",
    "core-053",
    "sources-166",
    "core-445",
    "sources-160",
    "core-242",
    "core-444",
    "core-099",
    "core-301",
    "core-098",
    "core-549",
    "core-278",
    "core-059",
    "core-363",
    "core-271",
    "core-055",
    "core-349",
    "sources-163",
    "core-489",
    "core-070",
    "core-508",
    "core-409",
    "core-446",
    "sources-143",
    "core-494",
    "core-550",
    "sources-192",
    "core-057",
    "sources-181",
    "core-280",
    "core-177",
    "core-030",
    "core-196",
    "sources-184",
    "core-585",
    "core-521",
    "core-525",
    "core-223",
    "core-040",
    "core-336",
    "core-conjugation-target",
    "core-282",
    "core-092",
    "core-304",
    "core-behavior-03",
    "core-ascella-signed-coherence-physical-models-replay",
    "core-ascella-signed-coherence-configuration-holdout-replay",
    "core-ascella-signed-coherence-drive-response-replay",
)


class SelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Selection indexes the files git tracks or would track, so the
        # fixture is a work tree; untracked files .gitignore admits count.
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.write("ci/full_gate_inputs.json", json.dumps({"gates": {"long": ["data/**"]}}))
        self.write("entry.py", "def run():\n import helper\n")
        self.write("helper.py", "import leaf\n")
        self.write("leaf.py", "")
        self.gates: list[dict[str, Any]] = [
            {"name": "fast", "cwd": ".", "cmd": "true"},
            {"name": "long", "cwd": ".", "cmd": '"$PYTHON" entry.py', "tier": "full"},
        ]
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))

    def write(self, name: str, text: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def chosen(self, *paths: str) -> list[str]:
        return [gate["name"] for gate in run_gates.select(self.root, "pr", changed=list(paths))]

    def test_transitive_and_function_local_sources(self) -> None:
        for path in ("entry.py", "helper.py", "leaf.py", "data/new/record.json", "requirements.txt"):
            with self.subTest(path=path):
                self.assertEqual(self.chosen(path), ["fast", "long"])
        self.assertEqual(self.chosen("unrelated.md"), ["fast"])
        self.assertEqual(self.chosen(), ["fast"])

    def test_a_name_imported_from_a_module_is_no_module(self) -> None:
        self.write("helper.py", "import leaf\nfrom leaf import collect\n")
        self.write("leaf.py", "def collect():\n pass\n")
        self.write("evidence/collect.py", "")
        self.assertEqual(self.chosen("evidence/collect.py"), ["fast"])
        self.assertEqual(self.chosen("leaf.py"), ["fast", "long"])

    def test_a_name_imported_from_a_package_or_relatively_is_a_submodule(self) -> None:
        for statement in ("from pkg import sub", "from . import sub"):
            with self.subTest(statement=statement):
                self.write("helper.py", f"{statement}\n")
                self.write("pkg/__init__.py", "")
                self.write("pkg/sub.py", "")
                self.assertEqual(self.chosen("pkg/sub.py"), ["fast", "long"])

    def test_deleted_import_still_selects(self) -> None:
        self.write("helper.py", "import deleted\n")
        self.assertEqual(self.chosen("deleted.py"), ["fast", "long"])

    def test_pytest_node_selector_keeps_import_closure(self) -> None:
        self.gates[1]["cmd"] = '"$PYTHON" -m pytest entry.py::test_contract'
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        for path in ("entry.py", "helper.py", "leaf.py"):
            with self.subTest(path=path):
                self.assertEqual(self.chosen(path), ["fast", "long"])

    def test_ignored_trees_stay_out_of_the_module_index(self) -> None:
        # An ignored build tree holding a same-named module would otherwise
        # resolve `import helper` into its copy and select through its imports.
        self.write(".gitignore", "build/\n")
        self.write("build/vendor/helper.py", "import vendored\n")
        self.write("vendored.py", "")
        self.write("fresh.py", "")
        modules = gate_inputs.module_index(self.root)
        self.assertEqual(modules["helper"], {self.root / "helper.py"})
        self.assertIn(self.root / "fresh.py", modules["fresh"])
        indexed = {path.relative_to(self.root).parts[0] for paths in modules.values() for path in paths}
        self.assertNotIn("build", indexed)
        self.assertEqual(self.chosen("vendored.py"), ["fast"])
        with tempfile.TemporaryDirectory() as outside:
            ceiling = str(Path(outside).parent)
            with patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": ceiling}):
                with self.assertRaisesRegex(ValueError, "not a git work tree"):
                    gate_inputs.module_index(Path(outside))

    def test_source_digest_literal(self) -> None:
        self.write("entry.py", "SOURCES = ('helper.py',)\n")
        self.assertEqual(self.chosen("leaf.py"), ["fast", "long"])

    def test_deleted_source_digest_literal(self) -> None:
        self.write("entry.py", "SOURCES = ('deleted.py',)\n")
        self.assertEqual(self.chosen("deleted.py"), ["fast", "long"])

    def test_timing_analysis_denominators(self) -> None:
        import analyze_timings

        job = {
            "name": "gates 0/1",
            "conclusion": "success",
            "created_at": "2026-01-01T00:00:00Z",
            "started_at": "2026-01-01T00:00:02Z",
            "completed_at": "2026-01-01T00:00:12Z",
            "steps": [
                {"name": "Run shard", "started_at": "2026-01-01T00:00:04Z", "completed_at": "2026-01-01T00:00:12Z"}
            ],
        }
        report = analyze_timings.analyze(
            [job],
            "gates 0/1\tRun shard\tPASS fast 7.0s  command\ngates 0/1\tRun shard\tPASS long 8.0s  command\n"
            "gates 0/1\tRunner specs\tlogical_cpus: 4  affinity_cpus: 4  cgroup_cpu_max: none\n",
            {"gates": [dict(gate, seconds=1) for gate in self.gates]},
        )
        self.assertEqual(report["workflow_seconds"], 12)
        delayed = analyze_timings.analyze(
            [job],
            "",
            {"gates": []},
            {
                "id": 1,
                "event": "push",
                "head_sha": "abc",
                "created_at": "2025-12-31T23:59:00Z",
                "run_started_at": job["created_at"],
            },
        )
        self.assertEqual(delayed["created_to_first_job_seconds"], 60)
        self.assertEqual(delayed["workflow_seconds"], 72)
        self.assertEqual(report["runner_seconds"], 10)
        self.assertEqual(len(report["runner_specs"]["gates 0/1"]), 1)
        self.assertEqual(report["gate_elapsed_seconds"], 15)
        self.assertEqual(report["stage_runner_seconds"]["Run shard"], 8)
        manifest = {"gates": [{"name": "fast", "seconds": 1, "timing_origin": "local-four-worker-qualification"}]}
        analyze_timings.refresh(manifest, [report])
        self.assertEqual(manifest["gates"][0]["seconds"], 7)
        self.assertNotIn("timing_origin", manifest["gates"][0])

    def test_manifest_coverage_and_scope_validation(self) -> None:
        for manifest in ({}, {"long": ["../outside"]}, {"long": "data/**"}):
            self.write("ci/full_gate_inputs.json", json.dumps({"gates": manifest}))
            with self.assertRaises(ValueError):
                self.chosen("unrelated.md")

    def test_toolchain_filter_preserves_full_manifest_validation(self) -> None:
        self.gates[1]["requires"] = ["qi"]
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        selected = run_gates.select(self.root, "pr", requires="qi", changed=["helper.py"])
        self.assertEqual([gate["name"] for gate in selected], ["long"])

    def test_timing_record_and_failure_keep_going(self) -> None:
        import contextlib
        import io

        self.gates[0]["cmd"] = "exit 1"
        self.gates[1]["cmd"] = "true"
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        record = self.root / "timings.json"
        with patch.object(run_gates, "ROOT", self.root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_gates.main(["--timings", str(record)]), 1)
        result = json.loads(record.read_text())
        self.assertEqual([(row["name"], row["status"]) for row in result["gates"]], [("fast", 1), ("long", 0)])
        self.assertGreater(result["wall_seconds"], 0)
        self.assertGreaterEqual(result["cpu_capacity"], 1)
        self.assertEqual(result["gates"][0]["resources"]["workers"], 1)
        self.assertGreater(result["gates"][0]["resources"]["max_rss_kib"], 0)

    def test_resource_collection_without_external_timer(self) -> None:
        import os
        import shutil

        binary_directory = self.root / "bin"
        binary_directory.mkdir()
        shell = shutil.which("sh")
        self.assertIsNotNone(shell)
        (binary_directory / "sh").symlink_to(str(shell))
        environment = dict(os.environ, PATH=str(binary_directory))
        gate = {"name": "portable", "cwd": ".", "cmd": "printf portable-resource"}
        measured, status, _, output = run_gates._run(gate, environment, self.root)
        self.assertEqual(status, 0, output)
        self.assertEqual(output, "portable-resource")
        self.assertGreater(measured["resources"]["max_rss_kib"], 0)
        gate["cmd"] = "kill -9 $$"
        self.assertEqual(run_gates._run(gate, environment, self.root)[1], 137)

    def test_all_ci_configuration_and_dependency_pins_select_full(self) -> None:
        for path in (
            ".github/actionlint.yaml",
            ".github/workflows/ci.yml",
            "docs/notes/quantum_inspire/requirements-qi.txt",
        ):
            self.assertEqual(self.chosen(path), ["fast", "long"])

    def test_workflow_diff_failure_selects_exhaustive_checks(self) -> None:
        import subprocess

        import changed_paths

        destination = self.root / "changed.bin"
        for base in ("", "0" * 40):
            with patch.object(changed_paths.subprocess, "run") as run:
                flags = changed_paths.select(self.root, "pull_request", base, destination)
                self.assertFalse(flags["limited"])
                self.assertTrue(flags["rocq"])
                run.assert_not_called()
        passed = subprocess.CompletedProcess([], 0, stdout=b"")
        failed = subprocess.CompletedProcess([], 128, stdout=b"")
        for responses in ([failed], [passed, failed]):
            with patch.object(changed_paths.subprocess, "run", side_effect=responses):
                flags = changed_paths.select(self.root, "push", "missing", destination)
                self.assertEqual(flags, {"rocq": True, "full": True, "limited": False})
        paths = b"old.py\0new name.py\0"
        difference = subprocess.CompletedProcess([], 0, stdout=paths)
        predicate = subprocess.CompletedProcess([], 1, stdout=b"")
        with patch.object(changed_paths.subprocess, "run", side_effect=[passed, difference, predicate]):
            flags = changed_paths.select(self.root, "pull_request", "base", destination)
            self.assertEqual(flags, {"rocq": False, "full": False, "limited": True})
            self.assertEqual(destination.read_bytes(), paths)

    def test_case_expansion_coverage_and_sharding(self) -> None:
        self.write("entry.py", "CONTRACT_CASES: dict = {'first': first, 'second': second}\n")
        parent = dict(self.gates[1], case_registry="CONTRACT_CASES", seconds=10)
        expanded = gate_inputs.expand_cases(self.root, [parent])
        self.assertEqual([gate["name"] for gate in expanded], ["long--first", "long--second"])
        self.assertEqual([gate["seconds"] for gate in expanded], [5, 5])
        self.assertEqual(
            [gate["cmd"] for gate in expanded], ['"$PYTHON" entry.py --case first', '"$PYTHON" entry.py --case second']
        )
        shards = run_gates.assign(expanded, 2)
        self.assertEqual([len(shard) for shard in shards], [1, 1])
        for malformed in ("{}", "{'first': first, 'first': second}", "{**other}"):
            self.write("entry.py", f"CONTRACT_CASES: dict = {malformed}\n")
            with self.assertRaises(ValueError):
                gate_inputs.expand_cases(self.root, [parent])

    def test_detected_cpu_budget_and_full_pool_allocation(self) -> None:
        import threading

        lock = threading.Lock()
        barrier = threading.Barrier(4)
        active = 0
        maximum = 0
        observed: dict[str, int] = {}

        def fake_run(
            gate: dict[str, Any], environment: dict[str, str], root: Path
        ) -> tuple[dict[str, Any], int, float, str]:
            nonlocal active, maximum
            workers = int(environment["GOROROBA_WORKERS"])
            with lock:
                active += workers
                maximum = max(maximum, active)
                observed[gate["name"]] = workers
            if gate["name"] != "full-pool":
                barrier.wait(timeout=3)
            with lock:
                active -= workers
            return gate, 0, 0.0, ""

        gates = [{"name": "full-pool", "workers": "all"}, *({"name": str(index)} for index in range(4))]
        with patch.object(run_gates, "_cpus", return_value=4), patch.object(run_gates, "_run", fake_run):
            results = list(run_gates.run_all(gates, {}, self.root))
        self.assertEqual(len(results), 5)
        self.assertEqual(observed, {"full-pool": 4, **{str(index): 1 for index in range(4)}})
        self.assertEqual(maximum, 4)

    def test_shards_balance_reserved_cpu_slots(self) -> None:
        gates = [
            {"name": "pool", "workers": "all", "seconds": 10},
            *({"name": f"ordinary_{index}", "seconds": 15} for index in range(3)),
        ]
        shards = run_gates.assign(gates, 2, capacity=4)
        self.assertEqual([gate["name"] for gate in shards[0]], ["pool"])
        self.assertEqual(len(shards[1]), 3)
        with patch.object(run_gates, "_cpus", return_value=2):
            self.assertEqual(run_gates.assign(gates, 2, capacity=4), shards)
        with patch.object(run_gates, "_cpus", return_value=8):
            self.assertEqual(run_gates.assign(gates, 2, capacity=4), shards)

    def test_expensive_archive_replays_have_input_scopes(self) -> None:
        root = Path(__file__).resolve().parents[2]
        gates = json.loads((root / "ci/gates.json").read_text())["gates"]
        names = {
            "core-063",
            "sources-149",
            "sources-215",
            "core-287",
            "core-311",
            "core-487",
            "core-495",
            "core-526",
        }
        self.assertTrue(all(gate["tier"] == "full" for gate in gates if gate["name"] in names))
        changed = [
            "gororoba_quantum/complex_skew_contracts.py",
            "docs/evidence/schur_acceleration/SHA256SUMS",
            "docs/evidence/cd_associator_defect_census/census.json",
            "docs/evidence/ghost_runs/result.json",
            "docs/evidence/walk_scaffold_channels/members.qpy",
            "docs/evidence/n21_exact_model/crosscheck.json",
            "docs/evidence/n21_exact_model/crosscheck_prep_excitation.json",
            "results/live/2026-10-13T201757.782152Z/raw/added/counts.json",
        ]
        self.assertLessEqual(names, gate_inputs.affected_full(root, gates, changed))
        self.assertFalse(names & gate_inputs.affected_full(root, gates, ["docs/unrelated-ci-audit.md"]))

    def test_slow_pr_gates_select_on_their_own_inputs(self) -> None:
        # Gates measured over 30 s left the pr tier; each still runs on a
        # change to a declared input or to the script its command runs.
        root = Path(__file__).resolve().parents[2]
        gates = json.loads((root / "ci/gates.json").read_text())["gates"]
        declared = json.loads((root / "ci/full_gate_inputs.json").read_text())["gates"]
        by_name = {gate["name"]: gate for gate in gates}
        modules = gate_inputs.module_index(root)
        references: dict[Path, tuple[tuple[str, ...], tuple[str, ...]]] = {}
        examples = {}
        for name in SLOW_FULL_GATES:
            self.assertEqual(by_name[name]["tier"], "full", name)
            if declared[name]:
                example = declared[name][0].replace("**", "probe.json").replace("*", "probe")
                self.assertTrue(gate_inputs.matches(example, declared[name][0]), name)
            else:
                script = next(token for token in by_name[name]["cmd"].split() if token.endswith(".py"))
                example = os.path.normpath(Path(by_name[name]["cwd"]) / script)
                self.assertIn(example, gate_inputs.dependencies(root, by_name[name], modules, references), name)
            examples[name] = example
            # A file or directory the command names outside Python (cmp, a
            # shell glob, an argument) is a read the tracer never records.
            command = by_name[name]["cmd"]
            for token in command.replace("&&", " ").replace("|", " ").replace(">", " ").split():
                for part in token.strip("\"'").split(","):
                    path = os.path.normpath(Path(by_name[name]["cwd"]) / part.split("=", 1)[-1])
                    if path.startswith(("/", "..")) or path == "." or not (root / path).exists():
                        continue
                    probe = path if (root / path).is_file() else path + "/probe.json"
                    sources = gate_inputs.dependencies(root, by_name[name], modules, references)
                    covered = path in sources or any(gate_inputs.matches(probe, p) for p in declared[name])
                    self.assertTrue(covered, f"{name} reads {path} outside its declared inputs")
        self.assertLessEqual(set(SLOW_FULL_GATES), gate_inputs.affected_full(root, gates, sorted(examples.values())))
        self.assertFalse(set(SLOW_FULL_GATES) & gate_inputs.affected_full(root, gates, ["docs/unrelated-audit.md"]))

    def test_quandela_static_scopes_follow_named_fixtures(self) -> None:
        root = Path(__file__).resolve().parents[2]
        gates = json.loads((root / "ci/gates.json").read_text())["gates"]
        names = {"core-513", "core-514", "core-515"}
        fixture = "results/quandela/runs/2026-10-17T232626Z-sim_belenos-belenos_mesh-job-00/raw/result.json"
        self.assertLessEqual(names, gate_inputs.affected_full(root, gates, [fixture]))
        unrelated = "results/quandela/runs/unrelated-acquisition/raw/result.json"
        self.assertFalse(names & gate_inputs.affected_full(root, gates, [unrelated]))
        transmission = (
            "results/quandela/runs/2026-10-17T213646Z-qpu_belenos-box_kite_photonic_single-job-04/submission.json"
        )
        self.assertEqual(names & gate_inputs.affected_full(root, gates, [transmission]), {"core-515"})

    def test_simulation_defaults_share_the_process_budget(self) -> None:
        import os

        parallel = run_gates.parallel
        for capacity in (1, 2, 4):
            for cap in (None, "1", "3", "8"):
                environment = {} if cap is None else {"GOROROBA_WORKERS": cap}
                with (
                    patch.dict(os.environ, environment, clear=True),
                    patch.object(parallel, "available_cpus", return_value=capacity),
                ):
                    expected = capacity if cap is None else min(capacity, int(cap))
                    self.assertEqual(parallel.workers(), expected)
                    self.assertEqual(parallel.default_threads(), expected)
            for cap in ("0", "-1", "invalid"):
                with patch.dict(os.environ, {"GOROROBA_WORKERS": cap}), self.assertRaises(ValueError):
                    parallel.default_threads()

    def test_explicit_worker_caps_apply_to_inner_pools(self) -> None:
        observed = []

        def fake_run(
            gate: dict[str, Any], environment: dict[str, str], root: Path
        ) -> tuple[dict[str, Any], int, float, str]:
            observed.append(int(environment["GOROROBA_WORKERS"]))
            return gate, 0, 0.0, ""

        for cap, expected in ((None, 4), ("1", 1), ("2", 2)):
            environment = {} if cap is None else {"GOROROBA_WORKERS": cap}
            with patch.object(run_gates, "_cpus", return_value=4), patch.object(run_gates, "_run", fake_run):
                list(run_gates.run_all([{"name": "inner", "workers": "all"}], environment, self.root))
            self.assertEqual(observed[-1], expected)

    def test_case_estimates_require_complete_registry(self) -> None:
        import analyze_timings

        self.write("entry.py", "CONTRACT_CASES: dict = {'first': first, 'second': second}\n")
        parent = dict(self.gates[1], case_registry="CONTRACT_CASES", seconds=100)
        manifest = {"gates": [parent]}
        report = {"gates": [{"job": "gates 0/1", "status": "PASS", "name": "long--first", "seconds": 2}]}
        analyze_timings.refresh(manifest, [report], self.root)
        self.assertEqual(parent["seconds"], 100)
        report["gates"][0].update(name="long--second", seconds=3)
        analyze_timings.refresh(manifest, [report], self.root)
        self.assertEqual(parent["seconds"], 5)
        self.write("entry.py", "CONTRACT_CASES: dict = {'first': first, 'second': second, 'third': third}\n")
        analyze_timings.refresh(manifest, [report], self.root)
        self.assertEqual(parent["seconds"], 5)
        self.assertEqual(gate_inputs.expand_cases(self.root, [parent])[-1]["seconds"], 5 / 3)

    def test_historical_plan_and_interpreter_dispatch(self) -> None:
        import os
        import sys

        self.gates[0]["runtime"] = "qiskit-2.5"
        self.gates[0]["cmd"] = '"$PYTHON" -c \'print("producer-interpreter")\''
        self.write("ci/gates.json", json.dumps({"gates": self.gates}))
        plan = self.root / "plan.json"
        output = self.root / "output.txt"
        with patch.object(run_gates, "ROOT", self.root):
            self.assertEqual(run_gates.main(["--plan", str(plan), "--github-output", str(output)]), 0)
        self.assertEqual(json.loads(plan.read_text())["environments"], ["qiskit-2.5"])
        self.assertEqual(output.read_text(), "historical=true\n")
        environment = dict(os.environ, PYTHON="/missing/current", GOROROBA_WORKERS="1")
        environment.pop("REPLAY_PYTHON", None)
        self.assertEqual(run_gates._run(self.gates[0], environment, self.root)[1], 127)
        environment["REPLAY_PYTHON"] = sys.executable
        _, status, _, result = run_gates._run(self.gates[0], environment, self.root)
        self.assertEqual(status, 0, result)
        self.assertEqual(result.strip(), "producer-interpreter")
        self.assertEqual(environment["PYTHON"], "/missing/current")

    def test_synthetic_units_refuse_archive_access(self) -> None:
        import subprocess
        import sys

        root = Path(__file__).resolve().parents[2]
        program = """
import builtins
import io
import os
import runpy
import sys
from pathlib import Path
from unittest.mock import patch
root = Path(sys.argv[1])
script, option = sys.argv[2:]
sys.path[:0] = [str(root / "scripts"), str(root / "gororoba_quantum")]
forbidden = [root / "results", root / "docs/evidence"]
def guard(original):
    def checked(file, *arguments, **keywords):
        if isinstance(file, (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(file)).resolve()
            if any(path.is_relative_to(directory) for directory in forbidden):
                raise AssertionError(f"synthetic contract accessed an archive: {path}")
        return original(file, *arguments, **keywords)
    return checked
sys.argv = [str(root / script), option]
with patch("builtins.open", guard(builtins.open)), patch("io.open", guard(io.open)):
    runpy.run_path(str(root / script), run_name="__main__")
"""
        fixtures = (
            ("scripts/atlas_coherent_families.py", "--self-test-channels"),
            ("scripts/atlas_fringe_amplitudes.py", "--self-test-channels"),
            ("scripts/jax_bridge_sweep.py", "--unit-test"),
            ("scripts/n21_qx_conformance.py", "--unit-test"),
        )
        environment = dict(run_gates.environment_for(None), GOROROBA_WORKERS="1")
        for script, option in fixtures:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, "-I", "-c", program, str(root), script, option],
                    cwd=root,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_resource_and_runtime_metadata(self) -> None:
        for field, value in (("workers", 0), ("workers", True), ("workers", "four"), ("runtime", "unknown")):
            with self.subTest(field=field, value=value):
                self.write("ci/gates.json", json.dumps({"gates": [dict(self.gates[0], **{field: value})]}))
                with self.assertRaises(SystemExit):
                    run_gates.select(self.root, "full")

    def test_repository_source_manifest_closure(self) -> None:
        import ast

        root = Path(__file__).resolve().parents[2]
        gates = json.loads((root / "ci/gates.json").read_text())["gates"]
        expected = {gate["name"] for gate in gates if gate["tier"] == "full"}
        self.assertEqual(gate_inputs.affected_full(root, gates, ["requirements.txt"]), expected)
        tree = ast.parse((root / "gororoba_quantum/live_run.py").read_text())
        declaration = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "EXPERIMENT_SOURCE_MANIFEST" for target in node.targets
            )
        )
        sources = {"gororoba_quantum/" + name for name in ast.literal_eval(declaration.value)}
        modules = gate_inputs.module_index(root)
        references: dict[Path, tuple[tuple[str, ...], tuple[str, ...]]] = {}
        for gate in gates:
            if gate["name"] in {
                "core-074",
                "core-080",
                "core-089",
                "core-094",
                "core-523",
                "core-289",
                "core-329",
                "core-360",
                "core-390",
                "core-491",
            }:
                self.assertLessEqual(sources, gate_inputs.dependencies(root, gate, modules, references), gate["name"])

    def test_thread_defaults_and_explicit_override(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            environment = run_gates.environment_for(None)
            self.assertEqual(environment["OMP_NUM_THREADS"], "1")
            self.assertEqual(environment["OPENBLAS_NUM_THREADS"], "1")
            self.assertEqual(environment["GLIBC_TUNABLES"], "glibc.rtld.optional_static_tls=4096")
            self.assertEqual(environment["OPENBLAS_CORETYPE"], "Haswell")
            self.assertEqual(environment["NPY_DISABLE_CPU_FEATURES"], "X86_V4 AVX512_ICL AVX512_SPR")
        with patch.dict("os.environ", {"OMP_NUM_THREADS": "2", "OPENBLAS_CORETYPE": "Zen"}, clear=True):
            self.assertEqual(run_gates.environment_for(None)["OMP_NUM_THREADS"], "2")
            self.assertEqual(run_gates.environment_for(None)["OPENBLAS_CORETYPE"], "Zen")
        for configured, expected in (("128", "4096"), ("8192", "8192"), ("invalid", "4096")):
            original = f"glibc.malloc.arena_max=2:glibc.rtld.optional_static_tls={configured}"
            with patch.dict("os.environ", {"GLIBC_TUNABLES": original}, clear=True):
                self.assertEqual(
                    run_gates.environment_for(None)["GLIBC_TUNABLES"],
                    f"glibc.malloc.arena_max=2:glibc.rtld.optional_static_tls={expected}",
                )
