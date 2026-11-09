"""Tests whose outcome depends on the platform, each a strict expected failure where its cause holds.

tests/conftest.py marks every node ID below with ``pytest.mark.xfail(strict=True)`` on the platforms it names, so a
listed test that starts passing there fails the run and its entry comes out. A platform is ``sys.platform`` and
``platform.machine()`` joined by a hyphen: ``linux-aarch64`` for the ubuntu-26.04-arm runner (numpy on OpenBLAS),
``darwin-arm64`` for macos-15 (numpy on Accelerate). The x64 runners and the build host match no entry.

Two causes recur. A Linux interface (``/proc``, ``time.CLOCK_BOOTTIME``) is absent on macOS. A retained record or
a byte-identity check holds the bits of the x64 numeric identity that wrote it, while another identity rounds
differently: a photonic-template phase pair (alpha, beta) whose negative-real entry carries a signed zero on x64 and
fused multiply-add residue on arm64 lands on the other branch of np.angle, a gauge-equivalent setting of the same
unitary; an optimizer or root finder takes another sequence of points. Retained bytes stay immutable, so these wait
for the cross-identity comparator of docs/design/native-numeric-replay.md (plan step semantic-comparator).
"""

from __future__ import annotations

LINUX_ARM = "linux-aarch64"
MACOS_ARM = "darwin-arm64"
ARM = frozenset({LINUX_ARM, MACOS_ARM})
MACOS = frozenset({MACOS_ARM})

GAUGE = "the retained request's photonic-template phase pair sits on the other np.angle branch on arm64"
IDENTITY = "the retained bytes hold the x64 numeric identity; arm64 rounds differently"
PROC = "reads /proc, a Linux interface macOS lacks"
BOOTTIME = "the bounded lock times its expiry with time.CLOCK_BOOTTIME, a Linux clock macOS lacks"

EXPECTED: dict[str, tuple[frozenset[str], str]] = {
    "tests/scripts/test_qd_teleportation_rehearsal.py::test_request_is_byte_stable_and_validates": (ARM, GAUGE),
    "tests/scripts/test_qd_teleportation_rehearsal.py::"
    "test_check_rederives_the_noise_model_and_accepts_the_retained_case[job-00]": (ARM, GAUGE),
    "tests/scripts/test_belenos_mode_swap_interleaved.py::"
    "test_retained_requests_rebuild_and_bind_to_the_packed_and_swapped_unitaries": (MACOS, IDENTITY),
    "tests/scripts/test_qi_pathion_one_cz_null.py::test_b0_replay_is_byte_equal_to_the_retained_circuit": (
        MACOS,
        IDENTITY,
    ),
    "tests/scripts/test_iqm_cancellation_probe.py::test_retained_garnet_analysis_replays": (MACOS, IDENTITY),
    "tests/gororoba_quantum/test_composite_placement.py::"
    "test_groups_without_per_placement_laws_plan_byte_identically[design_a]": (MACOS, IDENTITY),
    "tests/gororoba_quantum/test_composite_placement.py::"
    "test_groups_without_per_placement_laws_plan_byte_identically[design_c_8_1_4]": (MACOS, IDENTITY),
    "tests/scripts/test_ascella_physical_models.py::test_planted_heater_gain_is_recovered": (
        MACOS,
        "L-BFGS-B ends ABNORMAL on the planted heater-gain fit under Accelerate",
    ),
    "tests/test_msq_envelope.py::test_batched_brentq_replays_scipy_brentq": (
        MACOS,
        "the batched root finder's points depart from SciPy's brentq sequence under Accelerate",
    ),
    "tests/scripts/test_bdsc_null_calibration.py::"
    "test_a_mutated_batched_path_differs_from_the_scalar_analyse[square-numpy_square]": (
        MACOS,
        "under Accelerate the numpy_square mutant computes the same bits as the scalar analysis, so it goes unseen",
    ),
    "tests/gororoba_quantum/test_readout_actor_family.py::"
    "test_full_width_collection_includes_input_and_parsing_memory": (MACOS, PROC),
    "tests/gororoba_quantum/test_readout_actor_family.py::test_approval_registry_parent_is_synced_before_marker": (
        MACOS,
        PROC,
    ),
    "tests/test_a5_fiber_rank_v9.py::test_singular_inherits_the_directory_lock": (MACOS, PROC),
    "tests/scripts/test_qi_tuna_bounded_lock.py::test_acquired_lock_excludes_a_second_descriptor_and_releases": (
        MACOS,
        BOOTTIME,
    ),
    "tests/scripts/test_qi_tuna_bounded_lock.py::test_real_lock_contention_expires_before_entering_guard": (
        MACOS,
        BOOTTIME,
    ),
    "tests/scripts/test_qi_tuna_bounded_lock.py::test_exception_inside_guard_releases_the_lock": (MACOS, BOOTTIME),
    "tests/scripts/test_qi_tuna_bounded_lock.py::test_expiry_immediately_after_acquisition_releases_the_lock": (
        MACOS,
        BOOTTIME,
    ),
}
