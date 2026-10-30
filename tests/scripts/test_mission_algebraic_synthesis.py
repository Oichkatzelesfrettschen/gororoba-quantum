from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import mission_algebraic_synthesis as mas  # noqa: E402


def check(condition: bool, message: str = "check failed") -> None:
    if not condition:
        raise AssertionError(message)


def test_batched_bootstrap_returns_the_scalar_reference_bits() -> None:
    values = np.array([1.9961, 1.9993, 1.9902, 2.0, 1.9975, 1.9948, 1.9987])
    draws = mas.bootstrap_draws(len(values), mas.BOOTSTRAP_SEED, 2000)
    batched, scalar = mas.bootstrap_means(values, draws), mas.bootstrap_means_scalar(values, draws)
    check(batched.tobytes() == scalar.tobytes(), "batched and scalar bootstrap means differ in their bits")


def test_bootstrap_keeps_the_contrast_scale() -> None:
    values = np.full(21, 1.997448)
    summary = mas.bootstrap_mean_contrast(values, mas.BOOTSTRAP_SEED, 200)
    check(summary["bootstrap_mean"] == 1.997448 and summary["bootstrap_se"] == 0.0, f"{summary}")


def test_refused_reports_yield_unavailable_metrics() -> None:
    refused = {"status": "REFUSED", "verdicts": {"mean_character_contrast": 0.0, "sentinel_leakage_rate": 0.4}}
    check(mas.verdict(refused, "mean_displacing_contrast") is None)
    check(mas.verdict(None, "mean_displacing_contrast") is None)
    check(mas.leakage(refused) == 0.4)
    admitted = {"status": "ADMITTED", "verdicts": {"mean_displacing_contrast": 1.9}}
    check(mas.verdict(admitted, "mean_displacing_contrast") == 1.9)


def test_sedenion_pool_counts_the_character_pairs() -> None:
    summary = mas.evaluate_sedenion_non_alternativity()
    check(summary["total_imaginary_pairs"] == 105, f"{summary['total_imaginary_pairs']}")
    check(summary["character_homomorphism_pairs"] + summary["failed_pairs_count"] == 105)
