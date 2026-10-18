"""ET compiler enforcement and native suffix/mapping regression tests."""

import unittest
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import Operator

import live_run
from et_campaign import configuration, et_group
from et_planning import bind_controls, measurement_map, operator_error
from et_reference import ETSpec
from et_rows import row_circuit
from experiments import Group


class ETRuntimeTests(unittest.TestCase):
    def test_execution_pub_build_uses_bounded_et_gc_context(self) -> None:
        import gc

        before = gc.isenabled()
        observed = []

        def build(_: Any) -> list:
            observed.append(gc.isenabled())
            return []

        with patch.object(live_run, "_execution_pubs", side_effect=build):
            live_run.execution_pubs([cast(Any, SimpleNamespace(group=SimpleNamespace(name="et_row_campaign")))])
            live_run.execution_pubs([cast(Any, SimpleNamespace(group=SimpleNamespace(name="other_family")))])
        self.assertEqual(observed, [False, before])
        self.assertEqual(gc.isenabled(), before)

    def test_complete_submit_free_case_with_ideal_model_fixture(self) -> None:
        import io
        import json
        import tempfile
        from contextlib import redirect_stdout
        from pathlib import Path

        from qiskit_ibm_runtime.fake_provider import FakeFez

        import et_planning
        import qpu_cases
        from diagnostic_experiments import record_groups
        from runtime_contracts import _ProbeBackend, _ProbeService

        service = _ProbeService([_ProbeBackend("ibm_fez", FakeFez())])

        def ideal_model(runtime: Any, choice: Any, simulator: Any, shots: int) -> dict:
            del runtime, simulator, shots
            return {entry.name: [entry.ideal] for entry in choice.entries}

        with tempfile.TemporaryDirectory(prefix="et-case-fixture-") as temporary:
            arguments = [
                "--family",
                "et-row",
                "--optimize",
                "--shot-allocation",
                "per-pub",
                "--shots",
                "8192",
                "--shot-tiers",
                "32,64,128,2048",
                "--max-replicas",
                "1",
                "--replica-tiers",
                "1",
                "--no-isolated-reference",
                "--optimizer-candidates",
                "1",
                "--seeds",
                "1",
                "--model-shots",
                "65536",
                "--simulation-threads",
                "1",
                "--max-execution-seconds",
                "90",
                "--max-total-execution-seconds",
                "600",
                "--reserve-seconds",
                "10",
                "--out",
                temporary,
            ]
            with (
                patch.object(live_run, "QiskitRuntimeService", return_value=service),
                patch.object(live_run, "noise_simulator", return_value=SimpleNamespace()),
                patch.object(et_planning, "simulate", side_effect=ideal_model),
                patch.object(live_run, "submit", side_effect=AssertionError("hardware boundary")),
                redirect_stdout(io.StringIO()),
            ):
                status = live_run.main(arguments)
            self.assertEqual(status, 0)
            (record_path,) = Path(temporary).glob("*/record.json")
            record = json.loads(record_path.read_text())
            self.assertEqual(record["state"], "planned", record["optimization"])
            self.assertEqual(sum(record["pub_shots"].values()), 466944)
            self.assertEqual(len(record_groups(record)[0].members), 4656)
            case = record_path.parent / qpu_cases.CASE_FILENAME
            self.assertTrue(case.is_file())
            _, record_digest, archive_digest = qpu_cases._case_inputs(record_path.parent, record)
            self.assertIn(record_digest, case.read_text())
            self.assertIn(archive_digest, case.read_text())
            record["family_configuration"]["compilation_contract"] = "invalid-fixture-contract"
            with self.assertRaises(ValueError):
                qpu_cases._case_inputs(record_path.parent, record)

    def test_bulk_packing_restores_gc_on_error(self) -> None:
        import gc

        from et_planning import bulk_packing

        before = gc.isenabled()
        with self.assertRaisesRegex(ValueError, "fixture"):
            with bulk_packing():
                self.assertFalse(gc.isenabled())
                raise ValueError("fixture")
        self.assertEqual(gc.isenabled(), before)

    def test_family_planning_skips_unrelated_group_construction(self) -> None:
        arguments = SimpleNamespace(family="et-row", groups=None, backends=None, max_pending=1)
        with patch.object(live_run, "all_experiment_groups", side_effect=AssertionError("unrelated groups built")):
            with patch.object(live_run, "discover_snapshots", side_effect=RuntimeError("discovery boundary")):
                with self.assertRaisesRegex(RuntimeError, "discovery boundary"):
                    live_run.plan(None, cast(Any, arguments))

    def test_contract_reaches_compiler(self) -> None:
        circuit = row_circuit(ETSpec(32, 9, 2), measured=False)
        snapshot = cast(live_run.Snapshot, SimpleNamespace(admission_target=object(), backend=object(), name="fixture"))
        with patch.object(live_run, "transpile", return_value=circuit) as compile_call:
            live_run._compile(circuit, snapshot, 230)
        self.assertIs(compile_call.call_args.kwargs.get("qubits_initially_zero"), False)
        with patch.object(live_run, "transpile", return_value=circuit) as compile_call:
            live_run._compile(QuantumCircuit(1), snapshot, 230)
        self.assertNotIn("qubits_initially_zero", compile_call.call_args.kwargs)

    def test_static_law_matches_branch_reference_and_rejects_mid_measurement(self) -> None:
        import numpy as np

        from et_planning import terminal_probabilities
        from qpe_diagnostics import ideal_compiled_probabilities

        circuit = row_circuit(ETSpec(32, 9, 2), basis="X", mask=1)
        # A full-device wrapper carries idle physical wires and permuted roles.
        native = QuantumCircuit(156, 6)
        native.compose(circuit, qubits=[83, 96, 84, 81, 82, 103], clbits=[5, 4, 3, 2, 1, 0], inplace=True)
        np.testing.assert_allclose(terminal_probabilities(native), ideal_compiled_probabilities(native), atol=1e-12)
        native.x(83)
        with self.assertRaisesRegex(ValueError, "terminal"):
            terminal_probabilities(native)

    def test_incomplete_et_case_is_refused(self) -> None:
        import tempfile
        from pathlib import Path

        import qpu_cases

        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "configuration"):
                qpu_cases._case_inputs(
                    Path(temporary),
                    {"family_configuration": {"name": "et-row"}, "et_calibrated_design": {"admitted": True}},
                )
        self.assertIn("et_calibrated_design", live_run.APPROVED_RECORD_FIELDS)
        self.assertIn("et_calibrated_design", live_run.DESIGN_RECORD_FIELDS)

    def test_arbitrary_inputs(self) -> None:
        circuit = row_circuit(ETSpec(32, 9, 2), measured=False)
        backend = GenericBackendV2(6, basis_gates=["rz", "sx", "x", "cz"], seed=230)
        snapshot = cast(
            live_run.Snapshot, SimpleNamespace(admission_target=backend.target, backend=backend, name="fixture")
        )
        compiled = live_run._compile(circuit, snapshot, 230, list(range(6)))
        self.assertTrue(Operator.from_circuit(compiled).equiv(Operator(circuit)))

    def test_native_operator_detects_phase_and_role_mutations(self) -> None:
        import math

        circuit = row_circuit(ETSpec(32, 9, 2))
        backend = GenericBackendV2(
            6,
            basis_gates=["rz", "sx", "x", "cz"],
            coupling_map=[[bit, bit + 1] for bit in range(5)] + [[bit + 1, bit] for bit in range(5)],
            seed=230,
        )
        snapshot = cast(
            live_run.Snapshot, SimpleNamespace(admission_target=backend.target, backend=backend, name="fixture")
        )
        layout = [5, 4, 3, 2, 1, 0]
        compiled = live_run._compile(circuit, snapshot, 230, layout)
        self.assertLess(operator_error(compiled, circuit, layout), 1e-10)
        changed_phase = compiled.copy()
        changed_phase.global_phase += math.pi / 2
        self.assertGreater(operator_error(changed_phase, circuit, layout), 0.1)
        changed_roles = compiled.copy()
        measurements = [
            position for position, item in enumerate(changed_roles.data) if item.operation.name == "measure"
        ]
        first, last = measurements[0], measurements[-1]
        changed_roles.data[first] = changed_roles.data[first].replace(clbits=changed_roles.data[last].clbits)
        changed_roles.data[last] = changed_roles.data[last].replace(clbits=compiled.data[first].clbits)
        self.assertGreater(operator_error(changed_roles, circuit, layout), 0.1)

    def test_native_control_suffix_and_role_maps(self) -> None:
        import numpy as np
        from qiskit.quantum_info import Statevector

        config = configuration()
        complete = et_group(config)
        names = [
            member.name
            for member in complete.members
            if config["members"][member.name]["spec"] == [32, 9, 2]
            and config["members"][member.name]["block"] == 0
            and config["members"][member.name]["basis"] == "X"
        ]
        # Include every mask and every kind; compare the copied native suffix
        # against independent logical control laws after routing on a line.
        members = tuple(member for member in complete.members if member.name in names)
        config["members"] = {name: config["members"][name] for name in names}
        backend = GenericBackendV2(
            6,
            basis_gates=["rz", "sx", "x", "cz"],
            coupling_map=[[a, a + 1] for a in range(5)] + [[a + 1, a] for a in range(5)],
            seed=230,
        )
        snapshot = cast(
            live_run.Snapshot, SimpleNamespace(admission_target=backend.target, backend=backend, name="fixture")
        )
        compiled = {}
        isas = []
        for member in members:
            if id(member.circuit) not in compiled:
                compiled[id(member.circuit)] = live_run._compile(member.circuit, snapshot, 230, list(range(6)))
            isas.append(live_run._bind(compiled[id(member.circuit)], member))
        group = Group("fixture", members, lambda _: {})
        choice = SimpleNamespace(group=group, isas=isas, snap=snapshot, layout=list(range(6)))
        bind_controls(choice, config, live_run)
        source_map = measurement_map(choice.isas[0])
        for member, native in zip(members, choice.isas, strict=True):
            self.assertEqual(measurement_map(native), source_map)
            physical_law = Statevector.from_instruction(native.remove_final_measurements(inplace=False)).probabilities()
            logical_law = np.zeros(64)
            for outcome, probability in enumerate(physical_law):
                logical = sum(((outcome >> physical) & 1) << bit for bit, physical in enumerate(source_map))
                logical_law[logical] += probability
            np.testing.assert_allclose(logical_law, member.ideal, atol=2e-12)


if __name__ == "__main__":
    unittest.main()
