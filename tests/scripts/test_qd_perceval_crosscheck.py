"""Bounded fixtures for the Perceval cross-checks of the Belenos mesh and the postselected CZ."""

from __future__ import annotations

from pathlib import Path

import pytest
import qd_perceval_crosscheck as xc

ROOT = Path(__file__).resolve().parents[2]
JOB16 = ROOT / "results/quandela/runs/2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16"


def served() -> list[dict[str, object]]:
    if not (JOB16 / "raw/result.json").exists():
        pytest.skip("results/quandela job-16 is not checked out")
    return xc.served_entries(JOB16)


def test_our_mesh_unitary_equals_perceval_compute_unitary_on_two_served_meshes() -> None:
    entries = served()
    for index in (0, 2):
        row = xc.served_unitary(entries[index])
        if row["max_abs_difference"] > 1e-12 or row["unitarity_error_perceval"] > 1e-12:
            raise AssertionError((index, row))
        if (row["couplers"], row["phase_shifters"], row["mzi_cells"]) != (552, 574, 276):
            raise AssertionError(row)


def test_postselected_cz_success_equals_one_ninth_and_five_minus_four_m_over_nine() -> None:
    for overlap in xc.OVERLAPS:
        for rail_input in xc.RAIL_INPUTS:
            native = xc.cz_success("postprocessed cz", rail_input, overlap)
            if abs(native - xc.our_success(rail_input, overlap)) > 1e-12:
                raise AssertionError((overlap, rail_input, native))


def test_rate_ratio_of_the_native_cz_is_five_minus_four_m() -> None:
    for overlap in xc.OVERLAPS:
        rates = {i: xc.cz_success("postprocessed cz", i, overlap) for i in xc.RAIL_INPUTS}
        ratio = rates["10"] * rates["01"] / (rates["00"] * rates["11"])
        if abs(ratio - (5.0 - 4.0 * overlap)) > 1e-9:
            raise AssertionError((overlap, ratio))


def test_heralded_cz_succeeds_with_two_over_twenty_seven_at_unit_overlap() -> None:
    for rail_input in xc.RAIL_INPUTS:
        if abs(xc.cz_success("heralded cz", rail_input, 1.0) - 2.0 / 27.0) > 1e-12:
            raise AssertionError(rail_input)


def test_optimizer_started_at_the_served_phases_reaches_fidelity_one() -> None:
    result = xc.optimizer_check(served()[0])
    if result["variable_phases"] != 574 or result["optimized_vs_target_fidelity"] < 1 - 1e-9:
        raise AssertionError(result)


def test_native_decomposition_reaches_a_dense_control_and_the_served_unitary_is_recorded() -> None:
    control = xc.decompose(xc.fourier(8))
    if control["status"] != "circuit" or control["max_abs_error"] > 1e-6:
        raise AssertionError(control)
    plain = xc.decompose(xc.served_matrix(served()[0]))
    if plain["status"] == "circuit" and plain["max_abs_error"] > 1e-6:
        raise AssertionError(plain)
