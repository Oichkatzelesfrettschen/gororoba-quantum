"""The line-native Grover case: network minimality, exact compilation and the retained prediction.

Tests that read the retained case carry `audit`; the unmarked tests build their input here."""

import json

import iqm_grover_line as grover
import pytest


def test_self_test_holds() -> None:
    if "networks 8 and 7 CNOTs" not in grover.self_test():
        raise AssertionError("the self-test summary changed")


def test_the_exchanged_network_ends_in_a_swap_of_the_middle_wire() -> None:
    _, final = grover.ccz_block(grover.line_networks()["exchanged"])
    if final[0] != 1 or sorted(final[1:]) != [2, 4] or final == grover.IDENTITY_WIRES:
        raise AssertionError(f"exchanged network ends with wires {final}")


def test_a_reversed_bit_order_would_peak_at_110() -> None:
    path = ["QA", "QB", "QC"]
    circuit, _ = grover.compile_line(grover.grover_ops("011", 2), grover.line_networks()["exchanged"], path, "t")
    reversed_order = dict(circuit)
    reversed_order["instructions"] = [*circuit["instructions"][:-1], {**circuit["instructions"][-1]}]
    reversed_order["instructions"][-1]["locus"] = list(reversed(circuit["instructions"][-1]["locus"]))
    right = grover.ideal_distribution(circuit, path)
    wrong = grover.ideal_distribution(reversed_order, path)
    if not (right[int("011"[::-1], 2)] > 0.9 and wrong[int("110"[::-1], 2)] > 0.9):
        raise AssertionError("the 011 arm does not separate the two bit orders")


@pytest.mark.audit
def test_retained_run_analysis_replays() -> None:
    run = grover.ROOT / "results/iqm/runs/2026-11-20T230142Z-garnet-grover-line-ccz-grover"
    retained = (grover.ROOT / "results/iqm/grover_line_ccz_analysis.json").read_text(encoding="utf-8")
    if grover.dump(grover.analyze(run)) != retained:
        raise AssertionError("the analysis of the retained Garnet run differs from its record")


@pytest.mark.audit
def test_retained_prediction_of_one_arm_replays() -> None:
    case = grover.ROOT / "results/iqm/cases" / grover.CASE
    prediction = json.loads((case / "prediction.json").read_text(encoding="utf-8"))
    circuit = (case / "circuits/m101-k1.json").read_text(encoding="utf-8")
    replayed = grover.predicted((circuit, str(case / "calibration")))
    if replayed != prediction["arms"]["m101-k1"]["predicted"]:
        raise AssertionError(f"m101-k1 prediction {replayed} differs from the retained one")
