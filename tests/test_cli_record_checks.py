"""Each script's ``--check`` of its retained record, run in process through the script's own ``main``.

A test calls ``main`` with sys.argv set to ``SCRIPT ARGS`` and the working directory the script runs
from, the code path of ``"$PYTHON" -B -W error SCRIPT ARGS``; the module imports once per gate process
instead of once per interpreter. ``main``'s result follows the entry point ``SystemExit(main())``: None
or an integer 0 passes, and any other value or SystemExit code fails, as it fails the interpreter.

A check stays on its own gate in ci/gates.json when a claim in docs/state/research_state.json cites
that gate, when a script or a retained file names the gate (scripts/research_state.py --check, core-270;
scripts/n21_exact_model_validation.py --check, core-485, named in retained case addenda), when it
belongs to the sources suite, when its command carries more than one script invocation, or when its gate
declares a runtime or a requirement (scripts/compare_submitted_circuits.py --check, core-281, recomputes QPY
digests under the historical qiskit-2.5 runtime; scripts/qi_toolchain_check.py --check, core-368, needs the
Quantum Inspire stack that `--requires qi` selects).
scripts/aer_blocking_probe.py keeps its gates for the reason tests/test_cli_self_tests.py states.

Each row names a group, and gate ``core-record-check-NN`` of ci/gates.json runs group NN alone with
``-k groupNN`` in one process. Gate core-615 skips this module; the groups pack each check's measured
gate time to at most 27 s, under the 30 s pr wall budget of ci/AGENTS.md.
tests/ci/test_self_test_gates.py requires one gate per group and one group per gate.
"""

from __future__ import annotations

import importlib
import inspect
import shlex
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (script, working directory relative to the repository root, arguments, gate group).
RECORD_CHECKS = (
    ("gororoba_quantum/calibration_snapshot.py", ".", "--check docs/evidence/calibration/ibm_kingston.json", 1),
    ("scripts/ghost_idle_budget.py", ".", "--check docs/evidence/ghost_error_scale/idle_budget.json", 1),
    ("scripts/qi_walsh_exemplar_cases.py", ".", "--check results/quantum_inspire/cases", 2),
    ("scripts/box_kite_census.py", ".", "--check docs/evidence/box_kite_census/census.json", 2),
    ("scripts/rank_locus_gap_directions.py", ".", "--check docs/evidence/rank_locus_gap_directions/result.json", 3),
    (
        "scripts/qi_ladder_line_bins.py",
        ".",
        "--check results/quantum_inspire/box_kite_tuna_17_ladder_line_bins.json",
        3,
    ),
    ("scripts/bdsc_certificate.py", ".", "--check docs/evidence/bdsc-principal-angle-svd", 4),
    ("scripts/calibration_median_drift.py", ".", "--check docs/evidence/calibration_median_drift/result.json", 4),
    (
        "scripts/aer_gpu_probe.py",
        ".",
        "--check results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config/output/output/aer_gpu_probe.json"
        " --workloads toy,width --widths 7,10",
        4,
    ),
    ("scripts/aer_gpu_probe.py", ".", "--check docs/evidence/aer_gpu_configuration/result.json", 4),
    (
        "scripts/aer_gpu_probe.py",
        ".",
        "--check results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config/output/output/aer_gpu_probe.json"
        " --workloads toy,width --widths 7,10 --compare-counts"
        " results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config/output/output/aer_gpu_probe.json",
        3,
    ),
    ("scripts/cd_two_blade_blocks.py", ".", "--check docs/evidence/box_kite_census/two_blade_blocks.json", 5),
    ("scripts/bdsc_diagnostic.py", ".", "--check", 5),
    ("scripts/cd_star_lattice.py", ".", "--check docs/evidence/cd-star-lattice/census.json", 6),
    ("scripts/box_kite_follow_design.py", ".", "--check docs/evidence/box_kite_follow_design/design.json", 5),
    ("scripts/bdsc_ascella_control.py", ".", "--check", 5),
    ("scripts/bdsc_pauli.py", ".", "--check docs/evidence/bdsc/pauli/pauli_form.json", 5),
    ("scripts/capture_iqm_docs.py", ".", "--check", 5),
    ("scripts/bdsc_packages.py", ".", "--check docs/evidence/bdsc/packages/packages.json", 5),
    (
        "scripts/ghost_branching_benchmark.py",
        ".",
        "--check docs/evidence/ghost_error_scale_branching/benchmark-host.json"
        " results/kaggle/2026-10-18T041945Z-gororoba-ghost-branching-t4/output/output/ghost_branching_benchmark.json",
        5,
    ),
    ("scripts/capture_qi_docs.py", ".", "--check", 5),
    ("scripts/capture_qd_docs.py", ".", "--check", 5),
    ("scripts/qi_crosstalk_teleport_cases.py", ".", "--check results/quantum_inspire/cases", 5),
    ("scripts/validate_measured_explorer.py", ".", "--check", 5),
    ("scripts/capture_oq_docs.py", ".", "--check", 5),
    ("scripts/capture_kaggle_docs.py", ".", "--check", 5),
)


@pytest.mark.parametrize(
    ("script", "cwd", "arguments", "group"),
    RECORD_CHECKS,
    ids=[f"group{group:02d}:{script}:{index}" for index, (script, _, _, group) in enumerate(RECORD_CHECKS)],
)
def test_record_check(script: str, cwd: str, arguments: str, group: int, monkeypatch: pytest.MonkeyPatch) -> None:
    argv = shlex.split(arguments)
    monkeypatch.chdir(ROOT / cwd)
    monkeypatch.setattr(sys, "argv", [str(ROOT / script), *argv])
    main = importlib.import_module(Path(script).stem).main
    try:
        result = main(argv) if inspect.signature(main).parameters else main()
    except SystemExit as exit_:
        result = exit_.code
    # The interpreter exits 0 only for a None or integer-zero code (bool is an int); 0.0 or a string exits 1.
    if not (result is None or (isinstance(result, int) and result == 0)):
        raise AssertionError(f"{script} {arguments} exited with {result!r}")
