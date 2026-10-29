"""Compare the prospective decoder with retained nominal-zero shot lists."""

from __future__ import annotations

import json
from pathlib import Path

from qi_tuna_sequential_score import decode_counts

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/quantum_inspire/runs/2026-10-27T194754Z-tuna-destination-response"


def test_retained_nominal_zero_q6_counts() -> None:
    """Catch an early-destination or terminal-bit regression on retained shots."""
    cases = (
        ("prepared-zero-baseline-before", "baseline-before.cq", "baseline", 1442, 938),
        ("prepared-zero-rotated-destinations", "rotated-destinations.cq", "rotated", 3419, 2525),
        ("prepared-zero-baseline-after", "baseline-after.cq", "baseline", 1449, 969),
    )
    for directory, source, arm, early, terminal in cases:
        raw = RUN / directory / "raw" / f"{source}.json"
        counts = decode_counts(arm, json.loads(raw.read_bytes()))
        if counts != {"early_ones": early, "terminal_ones": terminal}:
            raise AssertionError(f"retained q6 counts differ for {directory}: {counts}")
