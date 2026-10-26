"""Contract of the rehearsal's secondary analyses: the record-state classes, the grid fit, the declared
Cayley-Dickson map onto cd_core and the deterministic controls of the exploratory lens."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pytest
import qd_rehearsal_secondary as secondary
import qd_teleportation_rehearsal as rehearsal

import cd_core
from parallel import ordered_map

CASE = rehearsal.CASES / "job-00"
# Indices 0 to 4, in index order, of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-26T021218Z.json,
# registered in docs/evidence/qrng_seeds/allocations.json: the synthetic tables and vectors of these tests.
TEST_SEEDS = (57403, 35698, 22313, 39335, 24314)
# Index 0 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-26T021247Z.json, registered beside TEST_SEEDS.
LENS_SEED = 44477


def manifest() -> dict[str, Any]:
    return json.loads((CASE / "cases.json").read_text(encoding="utf-8"))


def results_with(samples: list[int | None], partial: bool = False) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for setting, count in zip(manifest()["settings"], samples, strict=True):
        if count is None:
            entries.append({"missing": True})
        else:
            entries.append({"iteration": {"circuit_params": setting["circuit_params"]}, "counts": {}, "samples": count})
    return {"partial": partial, "iterations": entries}


@pytest.mark.parametrize(
    ("samples", "partial", "state"),
    [
        ([900] * 6, False, "near-anchor"),
        ([450] * 6, False, "near-anchor"),
        ([0] * 6, False, "degraded-as-recorded"),
        ([9, 9, 9, 9, 9, 9], False, "degraded-as-recorded"),
        ([100] * 6, False, "intermediate"),
        ([900, 900, 900, None, None, None], True, "near-anchor"),
        ([30, None, None, None, None, None], True, "degraded-as-recorded"),
    ],
)
def test_record_state_follows_the_preregistered_classes(samples: list[int | None], partial: bool, state: str) -> None:
    record = secondary.record_state(manifest(), results_with(samples, partial))
    if record["state"] != state or record["returned_samples"] != sum(n or 0 for n in samples):
        raise AssertionError(record)


def test_fit_recovers_the_generating_grid_cell() -> None:
    generator = np.random.default_rng(TEST_SEEDS[0])
    homs, g2s, scales = (0.8, 0.85, 0.9), (0.0, 0.05, 0.1), (0.001, 0.01, 0.1)
    table = generator.dirichlet(np.ones(len(secondary.CATEGORIES)), size=(6, 3, 3, 3))
    truth = (2, 1, 0)
    counts = np.rint(1e6 * table[:, truth[0], truth[1], truth[2], :]).astype(np.int64)
    fit = secondary.fit_from_table(counts, table, homs, g2s, scales)
    parameters = fit["parameters"]
    got = (parameters["hom"]["estimate"], parameters["g2"]["estimate"], parameters["transmittance"]["estimate"])
    if got != (0.9, 0.05, 0.001) or fit["deviance"] > 1e-3 or fit["degrees_of_freedom"] != 6 * 6 - 3:
        raise AssertionError(fit)
    if parameters["hom"]["interval"] != [0.9, 0.9] or not parameters["hom"]["at_grid_edge"]:
        raise AssertionError(parameters["hom"])


def test_fit_reports_a_grid_without_support() -> None:
    table = np.zeros((6, 1, 1, 1, len(secondary.CATEGORIES)))
    table[..., 0] = 1.0
    counts = np.zeros((6, len(secondary.CATEGORIES)), dtype=np.int64)
    counts[:, 1] = 5
    fit = secondary.fit_from_table(counts, table, (0.9,), (0.0,), (0.01,))
    if fit["status"] == "fitted":
        raise AssertionError(fit)


def test_category_table_reproduces_the_variant_scores() -> None:
    settings, circuit = rehearsal.request_parts()
    anchor = json.loads((rehearsal.ROOT / rehearsal.ANCHOR_READ).read_text(encoding="utf-8"))
    t_out, _, figures = rehearsal.read_perfs(anchor)
    table = secondary.category_table(settings, circuit, [t_out], (0.888,), (0.011,), (figures["transmittance"],))
    variant = rehearsal.Variant("check", 0.888, 0.011, tuple(rehearsal.detection_efficiency(t_out, 0.055)))
    rows = ordered_map(rehearsal.variant_scores, [(variant, s["label"], s, circuit) for s in settings], min_items=1)
    for k, row in enumerate(rows):
        cell = table[k, 0, 0, 0, 0]
        accepted = cell[0] + cell[1]
        if abs(accepted - row["accepted_share"]) > 1e-9 or abs(cell[0] / accepted - row["conditional_fidelity"]) > 1e-9:
            raise AssertionError((k, cell, row))


def test_cd_signs_are_the_declared_cd_core_map() -> None:
    signs = secondary.cd_signs(64)
    xor = np.bitwise_xor.outer(np.arange(64), np.arange(64))
    generator = np.random.default_rng(TEST_SEEDS[1])
    u, v = generator.normal(size=64), generator.normal(size=64)
    expected = np.asarray(cd_core.cd_multiply(64, list(u), list(v)))
    if np.max(np.abs(secondary.product(u, v, signs, xor) - expected)) > 1e-12:
        raise AssertionError("the sign-table product departs from cd_core.cd_multiply")


def test_controls_are_deterministic_support_matched_tables() -> None:
    first = secondary.control_tables(TEST_SEEDS[3], (64, 128), 5)
    second = secondary.control_tables(TEST_SEEDS[3], (64, 128), 5)
    for dim, tables in first.items():
        if not np.array_equal(tables, second[dim]):
            raise AssertionError(f"control tables of dimension {dim} differ between draws")
        if not (tables[:, 0, :] == 1).all() or not (tables[:, :, 0] == 1).all():
            raise AssertionError("a control table moves the identity")
        if not (tables[:, np.arange(1, dim), np.arange(1, dim)] == -1).all():
            raise AssertionError("a control unit squares to +1")
        imaginary = tables[:, 1:, 1:]
        off = ~np.eye(dim - 1, dtype=bool)
        if (imaginary + imaginary.transpose(0, 2, 1))[:, off].any():
            raise AssertionError("distinct control units commute")
        algebra = secondary.cd_signs(dim)[1:, 1:]
        if not ((algebra + algebra.T)[off] == 0).all():
            raise AssertionError("distinct Cayley-Dickson units commute")
        if any(np.array_equal(table, secondary.cd_signs(dim)) for table in tables):
            raise AssertionError("a control equals the Cayley-Dickson table")


def test_lens_of_the_model_against_itself_ranks_at_one() -> None:
    event = tuple(1 if mode == rehearsal.LAYOUT[rehearsal.Q0] else 0 for mode in range(rehearsal.MODES))
    model: list[dict[tuple[int, ...], float]] = [{event: 1.0}] * 6
    record = secondary.cd_lens(model, model, seed=LENS_SEED, count=9, dims=(64,))
    if record["dimensions"]["64"]["percentile"] != 1.0 or record["flag"] != "no algebra-specific separation":
        raise AssertionError(record)


def test_lens_pooled_separations_equal_the_serial_ones() -> None:
    generator = np.random.default_rng(TEST_SEEDS[2])
    x, y = generator.dirichlet(np.ones(64), size=6), generator.dirichlet(np.ones(64), size=6)
    tables = secondary.control_tables(TEST_SEEDS[4], (64,), 40)[64]
    chunks = [(tables[k : k + 7], x, y) for k in range(0, 40, 7)]
    pooled = [value for chunk in ordered_map(secondary.separation, chunks, min_items=1) for value in chunk]
    serial = [value for chunk in map(secondary.separation, chunks) for value in chunk]
    if pooled != serial:
        raise AssertionError("pooled and serial separations differ")


def test_basis_index_places_logical_mode_b_on_bit_b() -> None:
    clicks = [0] * rehearsal.MODES
    for mode in (rehearsal.Q0, rehearsal.A1, rehearsal.H1):
        clicks[rehearsal.LAYOUT[mode]] = 1
    index = (1 << rehearsal.Q0) | (1 << rehearsal.A1) | (1 << rehearsal.H1)
    if secondary.basis_index(clicks, 256) != index or secondary.basis_index(clicks, 128) is not None:
        raise AssertionError(secondary.basis_index(clicks, 256))
    outside = [0] * rehearsal.MODES
    outside[0] = 1
    if secondary.basis_index(outside, 256) is not None:
        raise AssertionError("a click off the logical modes maps into the algebra")


def test_fitted_pooled_fidelity_weights_inputs_by_their_samples() -> None:
    table = np.zeros((2, 1, 1, 1, len(secondary.CATEGORIES)))
    table[0, ..., 0], table[0, ..., 1] = 0.9, 0.1
    table[1, ..., 0], table[1, ..., 1] = 0.1, 0.9
    counts = np.zeros((2, len(secondary.CATEGORIES)), dtype=np.int64)
    counts[0, :2] = (810, 90)
    counts[1, :2] = (10, 90)
    fit = secondary.fit_from_table(counts, table, (0.9,), (0.0,), (0.01,))
    if abs(fit["model_pooled_fidelity"] - fit["observed_pooled_fidelity"]) > 1e-12:
        raise AssertionError(fit)


def test_in_situ_fit_of_a_simulated_run_uses_the_anchor_profile(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def table(settings: Any, circuit: Any, profiles: Any, *args: Any) -> np.ndarray:
        calls.append(len(profiles))
        cells = np.zeros((6, 1, 1, len(profiles), 1, len(secondary.CATEGORIES)))
        cells[..., 0] = 1.0
        return cells

    monkeypatch.setattr(secondary, "category_table", table)
    monkeypatch.setattr(secondary, "fit_from_table", lambda counts, cells: {"status": "fitted"})
    counts = {
        ",".join(
            "1" if m in (rehearsal.LAYOUT[0], rehearsal.LAYOUT[2], rehearsal.LAYOUT[4]) else "0"
            for m in range(rehearsal.MODES)
        ): 200
    }
    results = {
        "iterations": [
            {"iteration": {"circuit_params": s["circuit_params"]}, "counts": counts, "samples": 200}
            for s in manifest()["settings"]
        ]
    }
    record = secondary.in_situ_fit(manifest(), results, tmp_path)
    if calls != [1] or list(record["fits"]) != ["anchor"] or "absent" not in record["platform_before"]:
        raise AssertionError(record)
