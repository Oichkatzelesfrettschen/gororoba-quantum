"""The unitary-arm diagnostic case: the pair product, the circuits, the model and the three decision patterns."""

import math
from pathlib import Path

import iqm_measurement_diagnostic as case
import pytest

# Tests that read the retained case, run or analysis carry `audit`; the unmarked tests build their input here.


def test_pair_product_is_the_rotation_it_replaces_up_to_a_z_rotation() -> None:
    leftover = case.pair_product() @ case.rx(16 * case.ALPHA).conj().T
    if abs(leftover[0, 1]) > 1e-12 or abs(leftover[1, 0]) > 1e-12:
        raise AssertionError(f"the pair product is not diagonal against the rotation: {leftover}")


def test_exact_driven_equation_agrees_with_layer_relaxation_after_the_rotation() -> None:
    pulses = [(math.pi / 2, 0.3 * k) for k in range(8)]
    plain = case.evolve(pulses, 4.5e-5, 1.0e-5, 1e-3, 1.0)
    exact = case.evolve(pulses, 4.5e-5, 1.0e-5, 1e-3, 1.0, drive=case.Drive(exact=True))
    if abs(plain - exact) > 5e-4:
        raise AssertionError(f"the exact driven equation moves z by {plain - exact}")
    if case.evolve(pulses, 4.5e-5, 1.0e-5, 1e-3, 1.0, drive=case.Drive(t2_scale=0.0)) <= plain:
        raise AssertionError("removing the dephasing under drive does not raise z")


@pytest.mark.audit
def test_self_test_holds() -> None:
    if "measurement diagnostic" not in case.self_test():
        raise AssertionError("the self-test summary changed")


@pytest.mark.audit
def test_retained_case_checks_and_rebuilds(tmp_path: Path) -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    case.check(retained)
    excerpt = case.seq.load_json(retained / case.EXCERPT)
    for name, text in case.build_files(excerpt).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    case.check(tmp_path)


@pytest.mark.audit
def test_drive_dephasing_scan_keeps_the_retained_model() -> None:
    run = case.ROOT / "results/iqm/runs/2026-10-25T224718Z-garnet-measurement-sequence-diagnostic-diagnostic"
    scan = case.drive_scan(
        run,
        (
            "relax after rotation",
            "exact driven equation",
            "no dephasing under drive",
            "dephasing rate x0.5",
            "dephasing rate x1.5",
        ),
    )
    analysis = case.seq.load_json(case.ROOT / "results/iqm/measurement_sequence_diagnostic_analysis.json")
    base = scan["relax after rotation"]
    for qubit, z in base["d6_z"].items():
        if abs(z - analysis["qubits"][qubit]["corrected"]["d6-pair-n16"]["z"]) > 1e-9:
            raise AssertionError(f"{qubit}: the default model differs from the retained analysis")
    exact = scan["exact driven equation"]["d6_z"]
    if any(abs(exact[q] - z) > 0.05 for q, z in base["d6_z"].items()):
        raise AssertionError("the exact driven equation moves a D6 residual")
    scaled = [
        v["sum_squares"] for k, v in scan.items() if k.startswith("dephasing rate") or k == "no dephasing under drive"
    ]
    if not all(base["sum_squares"] < value for value in scaled):
        raise AssertionError("a scaled dephasing rate fits the five corrected circuits better than the calibrated one")


def test_the_question_names_the_qubits_it_builds() -> None:
    if case.list_of(["QB1", "QB2", "QB3"]) != "QB1, QB2 and QB3":
        raise AssertionError(case.list_of(["QB1", "QB2", "QB3"]))


@pytest.mark.audit
def test_build_refuses_qubits_other_than_the_window_probes() -> None:
    retained = case.seq.load_json(case.ROOT / "results/iqm/cases" / case.CASE / case.EXCERPT)
    other = {**retained, "qubits": {q: retained["qubits"][q] for q in list(retained["qubits"])[:5]}}
    try:
        case.build_files(other)
    except ValueError as error:
        if "window probe" not in str(error):
            raise AssertionError(str(error)) from error
    else:
        raise AssertionError("a build on other qubits was accepted")
    if "QB5, QB7, QB11, QB14, QB17 and QB19" not in case.build_files(retained)["cases.json"]:
        raise AssertionError("the question lost the diagnosed qubits")
