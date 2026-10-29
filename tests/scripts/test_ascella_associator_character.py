"""Unit tests for the Ascella 8-mode octonion associator-character interferometer."""

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from ascella_associator_character import (  # noqa: E402
    BODY_TOLERANCE,
    LOGICAL,
    MODES,
    PRIMARY_PAIRS,
    TOLERANCE,
    analyze,
    associator_sign,
    build_character_unitary,
    build_documents,
    character_frequency,
    check,
    dry_run,
    embed_12,
    hadamard_8,
)


def test_hadamard_8_orthogonality():
    h8 = hadamard_8()
    if h8.shape != (8, 8):
        raise AssertionError(f"h8 shape {h8.shape} != (8, 8)")
    if not np.allclose(h8.T @ h8, np.eye(8), atol=TOLERANCE):
        raise AssertionError("h8 is not orthogonal")


def test_character_kernel_theorem_all_21_pairs():
    """Verify that ker s(x) is identically {0, a, b, a^b} across all 21 distinct imaginary pairs."""
    for a, b in combinations(range(1, 8), 2):
        s = [associator_sign(a, b, x) for x in range(8)]
        kernel = set(x for x in range(8) if s[x] == 1)
        expected_kernel = {0, a, b, a ^ b}
        if kernel != expected_kernel:
            raise AssertionError(f"pair ({a}, {b}) failed kernel check: {kernel} != {expected_kernel}")
        omega = character_frequency(a, b)
        if omega == 0:
            raise AssertionError(f"pair ({a}, {b}) omega is zero")


def test_character_unitaries_orthogonality():
    for a, b in PRIMARY_PAIRS:
        for arm in ("octonion", "clifford_control", "diagonal_null", "reversed"):
            u8 = build_character_unitary(a, b, arm)
            if not np.allclose(u8.T @ u8, np.eye(8), atol=TOLERANCE):
                raise AssertionError(f"pair ({a}, {b}) arm {arm} not orthogonal")


def test_embedded_12_mode_unitary():
    u8 = build_character_unitary(1, 2, "octonion")
    u12 = embed_12(u8)
    if u12.shape != (MODES, MODES):
        raise AssertionError(f"u12 shape {u12.shape} != ({MODES}, {MODES})")
    if not np.allclose(u12.conj().T @ u12, np.eye(MODES), atol=TOLERANCE):
        raise AssertionError("u12 is not unitary")
    if not np.allclose(u12[LOGICAL:, LOGICAL:], np.eye(MODES - LOGICAL), atol=TOLERANCE):
        raise AssertionError("u12 sentinel modes are not identity")


def test_ideal_contrast_amplitude():
    """In ideal wave optics, D_oct = +1.0, D_ctrl = -1.0, Delta = 2.0."""
    for a, b in PRIMARY_PAIRS:
        omega = character_frequency(a, b)
        u_oct = build_character_unitary(a, b, "octonion")
        u_ctrl = build_character_unitary(a, b, "clifford_control")

        p_omega_oct = abs(u_oct[omega, 0]) ** 2
        p_0_oct = abs(u_oct[0, 0]) ** 2
        d_oct = (p_omega_oct - p_0_oct) / (p_omega_oct + p_0_oct)

        p_omega_ctrl = abs(u_ctrl[omega, 0]) ** 2
        p_0_ctrl = abs(u_ctrl[0, 0]) ** 2
        d_ctrl = (p_omega_ctrl - p_0_ctrl) / (p_omega_ctrl + p_0_ctrl)

        delta = d_oct - d_ctrl
        if abs(delta - 2.0) >= BODY_TOLERANCE:
            raise AssertionError(f"pair ({a}, {b}) Delta {delta} != 2.0")


def test_check_passes():
    if check() != 0:
        raise AssertionError("check() returned non-zero")


def test_end_to_end_simulation_dry_run(tmp_path):
    ret = dry_run(samples=1000, case_dir=tmp_path)
    if ret != 0:
        raise AssertionError(f"dry_run returned {ret}")
    if not (tmp_path / "dry_run_simulation" / "cases.json").exists():
        raise AssertionError("cases.json does not exist")
    if not (tmp_path / "dry_run_simulation" / "results.json").exists():
        raise AssertionError("results.json does not exist")


def test_reversed_arm_ideal_metadata():
    """Verify that reversed arm ideal metadata matches physical unitary transfer to omega."""
    docs = build_documents()
    manifest = json.loads(docs["cases.json"].decode())
    for s in manifest["settings"]:
        if s["arm"] == "reversed":
            omega = s["omega_target"]
            if s["ideal"]["target_mode"] != omega:
                raise AssertionError(f"reversed arm target_mode {s['ideal']['target_mode']} != {omega}")
            if s["ideal"]["d_observable"] != 1.0:
                raise AssertionError(f"reversed arm d_observable {s['ideal']['d_observable']} != 1.0")


def test_empty_counts_refused(tmp_path):
    """Verify that empty counts fail closed with REFUSED rather than swallowing zero counts."""
    docs = build_documents()
    cases_file = tmp_path / "cases.json"
    cases_file.write_bytes(docs["cases.json"])
    manifest = json.loads(docs["cases.json"].decode())

    # Build empty count entries
    empty_iterations = [{"name": s["name"], "counts": {}} for s in manifest["settings"]]
    results_file = tmp_path / "results.json"
    results_file.write_text(json.dumps({"iterations": empty_iterations}))

    report = analyze(tmp_path)
    if report["status"] != "REFUSED":
        raise AssertionError(f"expected REFUSED on empty counts, got {report['status']}")
    if report["verdicts"]["execution_status"] != "REFUSED":
        raise AssertionError(f"expected execution_status REFUSED, got {report['verdicts']['execution_status']}")
