"""Contracts of the served-mesh record of the Ascella CZ tomography: the decoder against Perceval and the
distinguishable-photon law."""

from __future__ import annotations

import json
from functools import cache
from typing import Any

import ascella_cz_served_mesh as served
import ascella_cz_tomography_case as case
import numpy as np
import pytest

DECODER_TOLERANCE = 1e-12
LAW_TOLERANCE = 2e-3


@cache
def retained() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for run in served.RUNS:
        settings = json.loads((served.ROOT / run / "cases.json").read_text(encoding="utf-8"))["settings"]
        raw = json.loads((served.ROOT / run / "raw/result.json").read_text(encoding="utf-8"))
        pairs += list(zip(settings, json.loads(raw["results"])["results_list"], strict=True))
    return pairs


def decoder_deviation(step: int) -> float:
    """Largest deviation of the decoder from Perceval's deserializer over every `step`-th retained mesh."""
    from perceval.serialization import deserialize

    worst = 0.0
    for _, entry in retained()[::step]:
        reference = np.asarray(deserialize(entry["computed_circuit"]).compute_unitary(), dtype=complex)
        decoded = served.served_unitary(entry["computed_circuit"])
        if reference.shape != decoded.shape:
            raise AssertionError(f"Perceval spans {reference.shape}, the decoder {decoded.shape}")
        worst = max(worst, float(np.abs(decoded - reference).max()))
    return worst


@pytest.mark.audit
def test_decoder_matches_perceval_on_every_retained_mesh() -> None:
    worst = decoder_deviation(1)
    if len(retained()) != 144 or worst > DECODER_TOLERANCE:
        raise AssertionError(f"{len(retained())} meshes, largest decoder deviation {worst:.2e}")


def test_decoder_matches_perceval_on_eight_spread_meshes() -> None:
    worst = decoder_deviation(18)
    if worst > DECODER_TOLERANCE:
        raise AssertionError(f"largest decoder deviation {worst:.2e} over every 18th mesh")


def test_decoder_comparison_detects_a_changed_phase() -> None:
    from perceval.serialization import deserialize

    _, entry = retained()[0]
    elements = served.audit._elements(entry["computed_circuit"])
    phases = [
        value + (0.01 if index == 0 else 0.0) for index, value in enumerate(v for k, _, v in elements if k == "ps")
    ]
    changed = np.asarray(served.mesh.unitary(elements, phases)[: case.MODES, : case.MODES])
    reference = np.asarray(deserialize(entry["computed_circuit"]).compute_unitary(), dtype=complex)
    if float(np.abs(changed - reference).max()) <= DECODER_TOLERANCE:
        raise AssertionError("a 0.01 rad phase change passes the decoder comparison")


def distinguishable_law(unitary: np.ndarray) -> np.ndarray:
    a, b = served.SOURCES
    return np.array(
        [abs(unitary[c, a] * unitary[t, b]) ** 2 + abs(unitary[c, b] * unitary[t, a]) ** 2 for c, t in served.ELIGIBLE]
    )


def test_distinguishable_photon_law_matches_the_design() -> None:
    worst_tvd = worst_ratio = 0.0
    for setting, entry in retained():
        got = distinguishable_law(served.served_unitary(entry["computed_circuit"]))
        want = distinguishable_law(case.embed(case.setting_unitary(setting)))
        worst_tvd = max(worst_tvd, float(np.abs(got / got.sum() - want / want.sum()).sum() / 2))
        worst_ratio = max(worst_ratio, abs(float(got.sum() / want.sum()) - 1))
    if worst_tvd > LAW_TOLERANCE or worst_ratio > 5e-3:
        raise AssertionError(f"distinguishable law: TVD {worst_tvd:.2e}, success ratio deviation {worst_ratio:.2e}")
