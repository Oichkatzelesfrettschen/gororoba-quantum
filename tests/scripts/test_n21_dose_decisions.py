"""Contracts of the N=21 window-dose decisions."""

from __future__ import annotations

import n21_dose_decisions as dose


def test_self_test_cases_decide_as_stated() -> None:
    message = dose.self_test()
    if "decide as stated" not in message:
        raise AssertionError(message)


def test_measured_contrast_and_sigma_follow_the_score_vector() -> None:
    contracts = [
        {
            "name": "c",
            "terms": [
                {"member": "fb", "sign": 1, "values": [0.0, 1.0, 0.0, -1.0]},
                {"member": "nf", "sign": -1, "values": [0.0, 1.0, 0.0, -1.0]},
            ],
        }
    ]
    laws = {"fb": [0.25, 0.5, 0.0, 0.25], "nf": [0.25, 0.25, 0.25, 0.25]}
    value, sigma = dose.measured(contracts, laws, 100)["c"]
    if abs(value - 0.25) > 1e-12:
        raise AssertionError(f"contrast {value}")
    expected = ((0.75 - 0.25**2) + (0.5 - 0.0)) / 100
    if abs(sigma**2 - expected) > 1e-12:
        raise AssertionError(f"variance {sigma**2} against {expected}")
