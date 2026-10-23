"""Each script's ``--self-test`` mode, run in process through the script's own ``main``.

A test calls ``main`` with sys.argv set to ``SCRIPT --self-test`` and the working directory the
script runs from, which is the code path of ``"$PYTHON" -W error SCRIPT --self-test``; the module
imports once per worker instead of once per interpreter. ``main``'s result follows the entry point
``SystemExit(main())``: None or 0 passes, and any other value or SystemExit code fails, as it fails
the interpreter. A self-test that a claim in docs/state/research_state.json cites, or whose command
carries more than ``--self-test``, stays on its own gate in ci/gates.json, as do
scripts/aer_blocking_probe.py (core-452) and gororoba_quantum/parallel.py (core-520), whose gate
names appear in files whose bytes a retained record binds.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# (script, working directory), both relative to the repository root.
SELF_TESTS = (
    ("scripts/review_wide_control_job.py", "."),
    ("scripts/qpu_runtime_levers.py", "."),
    ("scripts/heron_spatial_multiprogramming.py", "."),
    ("scripts/local_member_cz_conformance.py", "."),
    ("scripts/capture_qi_docs.py", "."),
    ("scripts/capture_oq_docs.py", "."),
    ("scripts/oq_platform.py", "."),
    ("scripts/capture_qd_docs.py", "."),
    ("scripts/qd_platform.py", "."),
    ("scripts/qd_box_kite_cases.py", "."),
    ("scripts/cd_two_blade_blocks.py", "."),
    ("scripts/qd_box_kite_analysis.py", "."),
    ("scripts/qd_belenos_mesh.py", "."),
    ("scripts/materialize_gororoba_csv.py", "."),
    ("scripts/rank_locus_gap_directions.py", "."),
    ("scripts/exact_rank.py", "."),
    ("scripts/box_kite_follow_design.py", "."),
    ("scripts/ghost_event_scale.py", "."),
    ("scripts/ghost_error_scale.py", "."),
    ("scripts/kaggle_sessions.py", "."),
    ("scripts/box_kite_census.py", "."),
    ("scripts/box_kite_cases.py", "."),
    ("scripts/box_kite_qx_sweep.py", "."),
    ("scripts/qi_shot_record_line.py", "."),
    ("scripts/qi_walsh_exemplar_cases.py", "."),
    ("scripts/qi_walsh_exemplar_analysis.py", "."),
    ("gororoba_quantum/dynamic_density.py", "gororoba_quantum"),
    ("scripts/n21_exact_model_validation.py", "."),
    ("scripts/n21_replica_covariance.py", "."),
    ("scripts/n21_exact_crosscheck.py", "."),
    ("scripts/lsq_conditioning_study.py", "."),
    ("gororoba_quantum/wheel_algebra.py", "gororoba_quantum"),
    ("scripts/wheel_zero_divisors.py", "."),
    ("gororoba_quantum/gaussian_wheel.py", "gororoba_quantum"),
    ("scripts/wheel_rust_audit.py", "."),
    ("scripts/walk_scaffold_channels.py", "."),
    ("scripts/state_prep_excess.py", "."),
    ("scripts/ghost_calibrations.py", "."),
    ("scripts/ghost_run.py", "."),
    ("gororoba_quantum/ibm_account.py", "gororoba_quantum"),
    ("scripts/state_prep_control_parameters.py", "."),
    ("scripts/capture_iqm_docs.py", "."),
    ("scripts/iqm_platform.py", "."),
    ("scripts/bdsc_diagnostic.py", "."),
    ("scripts/bdsc_certificate.py", "."),
    ("scripts/check_markdown_links.py", "."),
)


@pytest.mark.parametrize(("script", "cwd"), SELF_TESTS, ids=[script for script, _ in SELF_TESTS])
def test_self_test(script: str, cwd: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT / cwd)
    monkeypatch.setattr(sys, "argv", [str(ROOT / script), "--self-test"])
    main = importlib.import_module(Path(script).stem).main
    try:
        result = main(["--self-test"]) if inspect.signature(main).parameters else main()
    except SystemExit as exit_:
        result = exit_.code
    if result not in (None, 0):
        raise AssertionError(f"{script} --self-test exited with {result!r}")
