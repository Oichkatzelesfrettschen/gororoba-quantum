"""The unitary-arm diagnostic case: the pair product, the circuits, the model and the three decision patterns."""

from pathlib import Path

import iqm_measurement_diagnostic as case


def test_self_test_holds() -> None:
    if "measurement diagnostic" not in case.self_test():
        raise AssertionError("the self-test summary changed")


def test_retained_case_checks_and_rebuilds(tmp_path: Path) -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    case.check(retained)
    excerpt = case.seq.load_json(retained / case.EXCERPT)
    for name, text in case.build_files(excerpt).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    case.check(tmp_path)


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
