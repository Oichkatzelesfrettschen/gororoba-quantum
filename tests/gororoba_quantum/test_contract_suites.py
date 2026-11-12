"""The package's self-test suites (gororoba_quantum/*_contracts.py) as pull-request tests.

Each suite builds its inputs from qiskit-ibm-runtime fake backends and exact arithmetic, mocks every provider
service and reads no retained record: the results/live/... paths in empirical_bernstein_contracts,
qpu_case_allocation_contracts and qpu_planning_contracts are argument strings for reproduction-command text and
name no file. A case calls the suite's own check function in process, from gororoba_quantum/ as the gate does, so a
failed check raises exactly where the gate command would exit non-zero. runtime_contracts contributes one case per
CONTRACT_CASES entry.

A unit that exceeds the per-case budget of tests/conftest.py runs here at a smaller size: its check function takes
the size as a keyword argument whose default is the full size, the gate commands of ci/gates.json call it without
the argument, and the table below passes the smaller one. A unit that cannot shrink without losing a check stays
on its gate, listed with its reason in ON_DEMAND and ON_DEMAND_RUNTIME_CASES. test_every_suite_is_accounted and
test_every_runtime_case_is_accounted fail when a suite or a case joins the package without a row in this file.
"""

from __future__ import annotations

import importlib
import inspect
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from qiskit_ibm_runtime.fake_provider import FakePrague

PACKAGE = Path(__file__).resolve().parents[2] / "gororoba_quantum"


def _full(_module: ModuleType) -> Mapping[str, Any]:
    return {}


@dataclass(frozen=True)
class Unit:
    """One independently runnable check: a function of a suite module and the arguments it runs with."""

    module: str
    call: str
    label: str = ""
    args: tuple[Any, ...] = ()
    size: Callable[[ModuleType], Mapping[str, Any]] = field(default=_full)
    exit_status: bool = False

    @property
    def case_id(self) -> str:
        return f"{self.module}:{self.label or self.call}"


def _runtime_case(name: str) -> Unit:
    return Unit("runtime_contracts", "_run_contract_case", name, (name,))


# The first five point tasks of kernel_determinant_contracts.audit (dimension, coordinate entries, expected nullity).
# The module's bytes are bound by SHA256SUMS ledgers under docs/evidence/kernel_determinant, so its audit cannot take
# a task list and the cases call point_control, symbolic_control and negative_controls themselves.
KERNEL_DETERMINANT_TASKS: tuple[tuple[int, dict[int, int | Fraction], int], ...] = (
    (4, {}, 4),
    (4, {1: 1}, 0),
    (16, {1: 1, 10: 1}, 4),
    (32, {1: 1, 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}, 4),
    (32, {1: 1, 10: 1}, 8),
)


# The two smallest point tasks of complex_skew_contracts.POINT_TASKS (name, coordinate entries, expected nullity).
COMPLEX_SKEW_TASKS: tuple[tuple[str, dict[int, Fraction | int], int], ...] = (
    ("nullity4", {1: 1, 10: Fraction(1, 4), 18: Fraction(5, 8), 25: Fraction(1, 8)}, 4),
    ("nullity8", {1: 1, 10: 1}, 8),
)


# The runtime_contracts cases that ci/gates.json core-074 runs as shards and that fit the per-case budget.
RUNTIME_CASES = (
    "dynamic_classification",
    "dynamic_mitigation_boundaries",
    "scheduler_timing_cases",
    "feed_forward_structure",
    "job_usage_cases",
    "packing_equivalence",
    "usage_wait",
    "raw_scrubbing",
    "nested_operations",
    "result_register_order",
    "twirling_shot_contract",
    "capability_admission",
    "target_and_bad_qubit_status",
    "pub_fusion_contracts",
    "worker_quota",
    "unchanged_since_planning",
    "replay_seed_independence",
    "joint_fusion_placement",
    "joint_fusion_candidate_backtracking",
    "required_placement_backtracking",
    "buffer_scope",
    "placement_duplicate_branch_order",
    "static_placement_judge",
    "schema_discrimination",
    "approved_backend_scope",
    "operator_qubit_exclusion",
    "compile_panic_isolation",
    "fragmented_target_layout",
    "packing_global_phase",
    "packed_static_stays_static",
    "rate_keys",
    "replica_floor_resolution",
    "experiment_source_manifest",
)

# Cases that plan or submit on the full 156-qubit FakeFez Target and take no size argument; gate core-074 of
# ci/gates.json runs them as shards (core-521 runs approval_calibration_values). Each value names what the case checks.
ON_DEMAND_RUNTIME_CASES: Mapping[str, str] = {
    "approved_record_gate": "a submission refuses unless the fresh plan equals the approved dry run",
    "approval_calibration_values": "an approval binds the consumed calibration values across six plans",
    "instance_and_ceiling": "a service without an instance is refused; a ceiling above the budget stops a batch",
    "backend_identity_records": "every planned record carries the backend version and processor type",
    "submit_refreshes_backend_identity": "a backend version change between plan and approved submit reaches the record",
    "fused_collection": "one mocked job passes fused result decoding and execution-window fan-out",
    "schema_lifecycle": "the record schema across plan, submit and collect",
    "every_job_revalidates": "every job revalidates the Target before it is sent",
    "packed_replica_split": "packed replicas of a dynamic circuit split into each replica's counts",
    "discovered_capabilities": "snapshot discovery records the capabilities of a viable FakeFez backend",
    "snapshot_and_fingerprint_coherence": "a FakeFez snapshot matches its properties and fingerprint",
    "live_reselection": "a degraded FakeFez snapshot triggers live reselection",
    "discovery_failure_isolation": "a refresh, properties, status or capabilities failure isolates its backend",
}

UNITS: tuple[Unit, ...] = (
    Unit("cd_quantum_contracts", "verify"),
    *(Unit("complex_skew_contracts", "coefficient_control", f"coefficient_control_{d}", (d,)) for d in (4, 8, 16)),
    *(
        Unit("complex_skew_contracts", "point_control", f"point_control_{task[0]}", (task,))
        for task in COMPLEX_SKEW_TASKS
    ),
    Unit("complex_skew_contracts", "polynomial_controls", "polynomial_controls_pivot_1", ((1,),)),
    Unit("complex_skew_contracts", "negative_controls"),
    Unit("complex_skew_contracts", "local_obstruction_controls"),
    Unit("correction_case_contracts", "verify"),
    Unit("correction_circuits_contracts", "verify"),
    Unit("correction_collection_contracts", "verify_cli"),
    Unit("correction_collection_contracts", "verify"),
    Unit("correction_preparation_contracts", "main"),
    Unit("correction_schedule_contracts", "verify"),
    Unit("correction_statistics_contracts", "main"),
    Unit("empirical_bernstein_contracts", "verify_coverage"),
    Unit("empirical_bernstein_contracts", "verify_methods"),
    Unit("empirical_bernstein_contracts", "verify_planner"),
    Unit("empirical_bernstein_contracts", "verify_default_identity"),
    *(
        Unit("kernel_determinant_contracts", "point_control", f"point_control_{index}", (task,))
        for index, task in enumerate(KERNEL_DETERMINANT_TASKS)
    ),
    Unit("kernel_determinant_contracts", "symbolic_control"),
    Unit("kernel_determinant_contracts", "negative_controls"),
    Unit("kernel_limit_contracts", "_toy_contracts"),
    Unit("kernel_limit_contracts", "_four_support_paths"),
    Unit("kernel_limit_contracts", "_cd_side_contracts"),
    Unit("maximal_contracts", "_verify_spectator_wavefront_circuits"),
    Unit("maximal_contracts", "_verify_spectator_wavefront_summary_and_simulation"),
    Unit("native_preflight_contracts", "verify"),
    Unit("parameter_binding_contracts", "verify"),
    Unit("placement_feasibility_contracts", "verify"),
    Unit("pub_shot_allocation_contracts", "_verify"),
    Unit("pub_shot_runtime_contracts", "_verify_local_executor", size=lambda _m: {"backend_type": FakePrague}),
    Unit("qpu_case_allocation_contracts", "verify"),
    Unit("qpu_planning_contracts", "_verify_static_admission_only"),
    Unit("qpu_planning_contracts", "_verify_pin_layout_only"),
    Unit("qpu_planning_contracts", "_verify_overlap_split_only"),
    Unit("qpu_planning_contracts", "_verify_ground_control_split_only"),
    Unit("qpu_planning_contracts", "_verify_ground_ramsey_sweep_only"),
    Unit("rank_sector_contracts", "main", exit_status=True),
    Unit("ripple_contracts", "_verify_sparse_runtime"),
    Unit("ripple_contracts", "_verify_archived_weights"),
    Unit("ripple_contracts", "_verify_native_walk_synthesis"),
    *(_runtime_case(name) for name in RUNTIME_CASES),
)

# Suites, or the parts of a suite, that stay on their ci/gates.json gate because the part takes a full-size
# 156-qubit FakeFez Target or an exact computation whose checks need every instance; each value names the part and
# its gate.
ON_DEMAND: Mapping[str, str] = {
    "algebra_planning_contracts": "the whole audit, whose rank-sector family compiles eight FakeFez lanes (core-095)",
    "complex_skew_contracts": (
        "the audit composition, coefficient dimensions 32 and 64, four larger point tasks, fourteen pivots (core-063)"
    ),
    "correction_planning_contracts": "three FakeFez Targets compiled and their discovery frontier walked (core-080)",
    "kernel_determinant_contracts": "the audit composition and the three largest point tasks (core-177, core-208)",
    "kernel_limit_contracts": "the four eight-nullity paths, whose pairwise intersections need all four (core-059)",
    "maximal_contracts": "duration-matched ISA selection for the spectator wavefront on FakeKingston (core-222)",
    "projective_kernel_contracts": "the whole audit, whose four kernel-limit certificates set its floor (core-179)",
    "pub_shot_runtime_contracts": "plan, approval, submission and collection on a FakeFez Target (core-098)",
    "qpu_planning_contracts": (
        "the default sequence (core-094), repetition delay (core-523), serialized-noise equivalence (core-548),"
        " heralded reuse in four cases (core-570), initialization herald (core-445), approved-prediction reuse"
        " (core-549), window bracket (core-446), state-prep control (core-524), the prep-excitation check and the"
        " measurement-sequence"
        " family, which no gate runs"
    ),
    "replica_covariance_contracts": "the whole verification, 3.5 s of CPU on the build host (core-486)",
    "real_frontier_contracts": "the whole audit, whose last stage doubles a dimension-256 pencil (core-190)",
    "ripple_contracts": "verify_ripple_family's member checks and 859 statevector comparisons (core-100)",
    "runtime_contracts": "the thirteen cases of ON_DEMAND_RUNTIME_CASES (core-074, core-521)",
}


@pytest.mark.parametrize("unit", [pytest.param(unit, id=unit.case_id) for unit in UNITS])
def test_contract_unit(unit: Unit, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(PACKAGE)
    module = importlib.import_module(unit.module)
    result = getattr(module, unit.call)(*unit.args, **unit.size(module))
    if unit.exit_status and result != 0:
        raise AssertionError(f"{unit.module}.{unit.call} returned {result!r}")
    if isinstance(result, dict):
        json.dumps(result, sort_keys=True)


def test_trimmed_units_leave_the_gate_size_as_the_default() -> None:
    for unit in UNITS:
        module = importlib.import_module(unit.module)
        parameters = inspect.signature(getattr(module, unit.call)).parameters
        for name in unit.size(module):
            if name not in parameters or parameters[name].default is inspect.Parameter.empty:
                raise AssertionError(f"{unit.case_id}: {name} is not a keyword argument with a full-size default")


def test_every_suite_is_accounted() -> None:
    suites = {path.stem for path in PACKAGE.glob("*_contracts.py")}
    accounted = {unit.module for unit in UNITS} | set(ON_DEMAND)
    if suites != accounted:
        raise AssertionError(
            f"suites without a row: {sorted(suites - accounted)}; rows without a suite: {sorted(accounted - suites)}"
        )


def test_every_runtime_case_is_accounted() -> None:
    import runtime_contracts

    registered = set(runtime_contracts.CONTRACT_CASES)
    accounted = set(RUNTIME_CASES) | set(ON_DEMAND_RUNTIME_CASES)
    if registered != accounted or set(RUNTIME_CASES) & set(ON_DEMAND_RUNTIME_CASES):
        raise AssertionError(
            f"cases without a row: {sorted(registered - accounted)}; unknown: {sorted(accounted - registered)}"
        )
