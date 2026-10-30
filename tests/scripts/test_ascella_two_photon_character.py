"""Unit tests for the Ascella 8-mode two-photon octonion associator-character interferometer."""

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from ascella_two_photon_character import (  # noqa: E402
    ALL_PAIRS,
    BODY_TOLERANCE,
    CONTROL_PAIR,
    INPUT_STATE,
    LOGICAL,
    MODES,
    PRIMARY_PAIRS,
    TOLERANCE,
    analyze,
    associator_sign,
    build_character_unitary,
    build_documents,
    build_schedule_spec,
    character_frequency,
    check,
    coset_focal_pair,
    dry_run,
    embed_12,
    hadamard_8,
)


def test_hadamard_8_orthogonality() -> None:
    h8 = hadamard_8()
    if h8.shape != (8, 8):
        raise AssertionError(f"h8 shape {h8.shape} != (8, 8)")
    if not np.allclose(h8.T @ h8, np.eye(8), atol=TOLERANCE):
        raise AssertionError("h8 is not orthogonal")


def test_two_photon_coset_partitioning_all_21_pairs() -> None:
    """Verify that F_2^3 / {0, 2} partitions all 21 pairs into 1 stabilizer triad and 3 displacing hexads."""
    coset_counts: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for a, b in combinations(range(1, 8), 2):
        s = [associator_sign(a, b, x) for x in range(8)]
        kernel = set(x for x in range(8) if s[x] == 1)
        expected_kernel = {0, a, b, a ^ b}
        if kernel != expected_kernel:
            raise AssertionError(f"pair ({a}, {b}) failed kernel check: {kernel} != {expected_kernel}")

        omega = character_frequency(a, b)
        focal = coset_focal_pair(omega)
        coset_counts.setdefault(focal, []).append((a, b))

    if len(coset_counts[CONTROL_PAIR]) != 3:
        raise AssertionError(f"stabilizer coset (0, 2) has {len(coset_counts[CONTROL_PAIR])} pairs, expected 3")
    for focal, pairs in coset_counts.items():
        if focal != CONTROL_PAIR and len(pairs) != 6:
            raise AssertionError(f"displacing coset {focal} has {len(pairs)} pairs, expected 6")


def test_non_bunching_theorem_all_21_pairs() -> None:
    """Verify that output modes are strictly distinct for all 21 pairs, preventing threshold bunching blindness."""
    for a, b in ALL_PAIRS:
        omega = character_frequency(a, b)
        focal = coset_focal_pair(omega)
        if focal[0] == focal[1]:
            raise AssertionError(f"pair ({a}, {b}) bunches into single mode {focal[0]}")


def test_character_unitaries_orthogonality() -> None:
    for a, b in PRIMARY_PAIRS:
        for arm in ("octonion", "clifford_control", "diagonal_null", "reversed"):
            u8 = build_character_unitary(a, b, arm)
            if not np.allclose(u8.T @ u8, np.eye(8), atol=TOLERANCE):
                raise AssertionError(f"pair ({a}, {b}) arm {arm} not orthogonal")


def test_all_21_pairs_schedule_spec() -> None:
    spec_16 = build_schedule_spec(all_pairs=False)
    if len(spec_16) != 16:
        raise AssertionError(f"expected 16 settings, got {len(spec_16)}")

    spec_84 = build_schedule_spec(all_pairs=True)
    if len(spec_84) != 84:
        raise AssertionError(f"expected 84 settings, got {len(spec_84)}")

    pairs_seen = set()
    for item in spec_84:
        pairs_seen.add(item["pair"])
    if pairs_seen != set(ALL_PAIRS):
        raise AssertionError(f"pairs_seen {len(pairs_seen)} != ALL_PAIRS {len(ALL_PAIRS)}")


def test_embedded_12_mode_unitary() -> None:
    u8 = build_character_unitary(1, 2, "octonion")
    u12 = embed_12(u8)
    if u12.shape != (MODES, MODES):
        raise AssertionError(f"u12 shape {u12.shape} != ({MODES}, {MODES})")
    if not np.allclose(u12.conj().T @ u12, np.eye(MODES), atol=TOLERANCE):
        raise AssertionError("u12 is not unitary")
    if not np.allclose(u12[LOGICAL:, LOGICAL:], np.eye(MODES - LOGICAL), atol=TOLERANCE):
        raise AssertionError("u12 sentinel modes are not identity")


def test_ideal_two_photon_contrasts() -> None:
    """In ideal optics: displacing pairs yield Delta = 2.0; stabilizer pairs yield P(0, 2) = 1.0."""
    for a, b in PRIMARY_PAIRS:
        omega = character_frequency(a, b)
        u_oct = build_character_unitary(a, b, "octonion")
        u_ctrl = build_character_unitary(a, b, "clifford_control")

        # Column 0 maps to omega, column 2 maps to 2 ^ omega
        col0_oct = int(np.argmax(np.abs(u_oct[:, 0])))
        col2_oct = int(np.argmax(np.abs(u_oct[:, 2])))
        out_oct = (min(col0_oct, col2_oct), max(col0_oct, col2_oct))

        col0_ctrl = int(np.argmax(np.abs(u_ctrl[:, 0])))
        col2_ctrl = int(np.argmax(np.abs(u_ctrl[:, 2])))
        out_ctrl = (min(col0_ctrl, col2_ctrl), max(col0_ctrl, col2_ctrl))

        if omega == 2:
            if out_oct != CONTROL_PAIR or out_ctrl != CONTROL_PAIR:
                raise AssertionError(f"stabilizer pair ({a}, {b}) departed (0, 2): oct={out_oct}, ctrl={out_ctrl}")
        else:
            focal = coset_focal_pair(omega)
            if out_oct != focal:
                raise AssertionError(f"displacing pair ({a}, {b}) octonion {out_oct} != {focal}")
            if out_ctrl != CONTROL_PAIR:
                raise AssertionError(f"displacing pair ({a}, {b}) clifford {out_ctrl} != {CONTROL_PAIR}")


def test_slos_two_photon_simulation() -> None:
    import perceval as pcvl

    u8 = build_character_unitary(1, 2, "octonion")
    u12 = embed_12(u8)
    backend = pcvl.BackendFactory.get_backend("SLOS")
    backend.set_circuit(pcvl.Unitary(pcvl.Matrix(u12)))
    backend.set_input_state(pcvl.BasicState(INPUT_STATE))
    dist = backend.prob_distribution()

    focal_state = [0] * MODES
    focal_state[4] = 1
    focal_state[6] = 1
    p_focal = dist.get(pcvl.BasicState(focal_state), 0.0)
    if abs(p_focal - 1.0) >= BODY_TOLERANCE:
        raise AssertionError(f"SLOS P(4, 6) {p_focal} != 1.0")


def test_exact_rational_arithmetic_flint() -> None:
    try:
        import flint
    except ImportError:
        return

    w8 = flint.fmpz_mat(8, 8, [(-1) ** (bin(i & j).count("1")) for i in range(8) for j in range(8)])
    for a, b in combinations(range(1, 8), 2):
        om = character_frequency(a, b)
        d_mat = flint.fmpz_mat(8, 8, [associator_sign(a, b, i) if i == j else 0 for i in range(8) for j in range(8)])
        prod = w8 * d_mat * w8
        if int(prod[om, 0]) != 8 or int(prod[2 ^ om, 2]) != 8:
            raise AssertionError(f"Flint exact transfer failed for ({a}, {b})")


def test_check_cli() -> None:
    ret = check()
    if ret != 0:
        raise AssertionError(f"check() returned {ret}")


def test_dry_run_pipeline_and_analysis(tmp_path: Path) -> None:
    docs = build_documents(samples_per_iteration=500, shots_factor=10, job_name="test-00")
    manifest = json.loads(docs["cases.json"].decode())
    if manifest["iterations"] != 16:
        raise AssertionError(f"expected 16 iterations, got {manifest['iterations']}")
    if manifest["credit_ceiling"] > 1.5:
        raise AssertionError(f"excessive credit ceiling {manifest['credit_ceiling']}")

    ret = dry_run(samples=200, shots_factor=5, job_name="test-dry-run", case_dir=tmp_path)
    if ret != 0:
        raise AssertionError(f"dry_run returned {ret}")


def test_adversarial_sentinel_leakage_rejection(tmp_path: Path) -> None:
    docs = build_documents(samples_per_iteration=200, shots_factor=5, job_name="job-leak")
    (tmp_path / "cases.json").write_bytes(docs["cases.json"])

    manifest = json.loads(docs["cases.json"].decode())
    settings = manifest["settings"]

    iterations = []
    for s in settings:
        # High leakage to sentinel mode 8
        state_sentinel = [0] * MODES
        state_sentinel[0] = 1
        state_sentinel[8] = 1
        counts = {f"|{','.join(str(v) for v in state_sentinel)}>": 200}
        iterations.append({"setting": s["name"], "counts": counts})

    (tmp_path / "results.json").write_text(json.dumps({"iterations": iterations}))
    report = analyze(tmp_path)
    if report["status"] != "REFUSED":
        raise AssertionError("expected REFUSED on high sentinel leakage")
    if not report["verdicts"]["admission_errors"]:
        raise AssertionError("expected admission errors on sentinel leakage")


def test_sentinel_leakage_above_the_preregistered_limit_refuses(tmp_path: Path) -> None:
    docs = build_documents(samples_per_iteration=200, shots_factor=5, job_name="job-leak-ideal")
    (tmp_path / "cases.json").write_bytes(docs["cases.json"])
    iterations = []
    for s in json.loads(docs["cases.json"].decode())["settings"]:
        ideal = [0] * MODES
        target = s["control_pair"] if s["is_stabilizer"] or s["arm"] != "octonion" else s["focal_pair"]
        ideal[target[0]] += 1
        ideal[target[1]] += 1
        leak = [0] * MODES
        leak[0] = 1
        leak[8] = 1
        counts = {f"|{','.join(map(str, ideal))}>": 100, f"|{','.join(map(str, leak))}>": 9900}
        iterations.append({"setting": s["name"], "counts": counts})
    (tmp_path / "results.json").write_text(json.dumps({"iterations": iterations}))
    report = analyze(tmp_path)
    verdicts = report["verdicts"]
    if report["status"] != "REFUSED" or verdicts["character_signal_detected"]:
        raise AssertionError(f"99 % sentinel leakage admitted: {verdicts}")
    if not any("sentinel leakage" in error for error in verdicts["admission_errors"]):
        raise AssertionError(f"{verdicts['admission_errors']}")
    if verdicts["mean_displacing_contrast"] is not None or verdicts["mean_stabilizer_persistence"] is not None:
        raise AssertionError("a refused report carries admitted-only metrics")
