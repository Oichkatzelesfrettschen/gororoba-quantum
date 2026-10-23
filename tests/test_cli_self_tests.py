"""Each script's ``--self-test`` mode, run in process through the script's own ``main``.

A test calls ``main`` with sys.argv set to ``SCRIPT --self-test`` and the working directory the
script runs from, which is the code path of ``"$PYTHON" -W error SCRIPT --self-test``; the module
imports once per gate process instead of once per interpreter. ``main``'s result follows the entry point
``SystemExit(main())``: None or 0 passes, and any other value or SystemExit code fails, as it fails
the interpreter. A self-test that a claim in docs/state/research_state.json cites, or whose command
carries more than ``--self-test``, stays on its own gate in ci/gates.json, as do
scripts/aer_blocking_probe.py (core-452) and gororoba_quantum/parallel.py (core-520), whose gate
names appear in files whose bytes a retained record binds.

Each row names a group, and gate ``core-self-test-NN`` of ci/gates.json runs group NN alone with
``-k groupNN`` in one process. Gate core-615 skips this module, so a pr gate stays under the 30 s
wall budget of ci/AGENTS.md; the groups pack each script's measured self-test time to at most 25 s.
tests/ci/test_self_test_gates.py requires one gate per group and one group per gate.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (script, working directory relative to the repository root, gate group).
SELF_TESTS = (
    ("scripts/review_wide_control_job.py", ".", 3),
    ("scripts/qpu_runtime_levers.py", ".", 6),
    ("scripts/heron_spatial_multiprogramming.py", ".", 8),
    ("scripts/local_member_cz_conformance.py", ".", 8),
    ("scripts/capture_qi_docs.py", ".", 9),
    ("scripts/capture_oq_docs.py", ".", 4),
    ("scripts/oq_platform.py", ".", 9),
    ("scripts/capture_qd_docs.py", ".", 9),
    ("scripts/qd_platform.py", ".", 7),
    ("scripts/qd_box_kite_cases.py", ".", 7),
    ("scripts/cd_two_blade_blocks.py", ".", 2),
    ("scripts/qd_box_kite_analysis.py", ".", 9),
    ("scripts/qd_belenos_mesh.py", ".", 8),
    ("scripts/materialize_gororoba_csv.py", ".", 2),
    ("scripts/rank_locus_gap_directions.py", ".", 4),
    ("scripts/exact_rank.py", ".", 9),
    ("scripts/box_kite_follow_design.py", ".", 9),
    ("scripts/ghost_event_scale.py", ".", 6),
    ("scripts/ghost_error_scale.py", ".", 9),
    ("scripts/kaggle_sessions.py", ".", 9),
    ("scripts/box_kite_census.py", ".", 5),
    ("scripts/box_kite_cases.py", ".", 7),
    ("scripts/box_kite_qx_sweep.py", ".", 7),
    ("scripts/qi_shot_record_line.py", ".", 9),
    ("scripts/qi_walsh_exemplar_cases.py", ".", 3),
    ("scripts/qi_walsh_exemplar_analysis.py", ".", 3),
    ("gororoba_quantum/dynamic_density.py", "gororoba_quantum", 2),
    ("scripts/n21_exact_model_validation.py", ".", 1),
    ("scripts/n21_replica_covariance.py", ".", 8),
    ("scripts/n21_exact_crosscheck.py", ".", 9),
    ("scripts/lsq_conditioning_study.py", ".", 8),
    ("gororoba_quantum/wheel_algebra.py", "gororoba_quantum", 8),
    ("scripts/wheel_zero_divisors.py", ".", 4),
    ("gororoba_quantum/gaussian_wheel.py", "gororoba_quantum", 5),
    ("scripts/wheel_rust_audit.py", ".", 9),
    ("scripts/walk_scaffold_channels.py", ".", 8),
    ("scripts/state_prep_excess.py", ".", 6),
    ("scripts/ghost_calibrations.py", ".", 9),
    ("scripts/ghost_run.py", ".", 9),
    ("gororoba_quantum/ibm_account.py", "gororoba_quantum", 5),
    ("scripts/state_prep_control_parameters.py", ".", 8),
    ("scripts/capture_iqm_docs.py", ".", 6),
    ("scripts/iqm_platform.py", ".", 7),
    ("scripts/bdsc_diagnostic.py", ".", 8),
    ("scripts/bdsc_certificate.py", ".", 9),
    ("scripts/check_markdown_links.py", ".", 3),
)


@pytest.mark.parametrize(
    ("script", "cwd", "group"), SELF_TESTS, ids=[f"group{group:02d}:{script}" for script, _, group in SELF_TESTS]
)
def test_self_test(script: str, cwd: str, group: int, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT / cwd)
    monkeypatch.setattr(sys, "argv", [str(ROOT / script), "--self-test"])
    main = importlib.import_module(Path(script).stem).main
    try:
        result = main(["--self-test"]) if inspect.signature(main).parameters else main()
    except SystemExit as exit_:
        result = exit_.code
    if result not in (None, 0):
        raise AssertionError(f"{script} --self-test exited with {result!r}")
