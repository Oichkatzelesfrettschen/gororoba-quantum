"""Independent deterministic QX joint-law diagnostics; no post-hoc significance verdict."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/quantum_inspire/runs/2026-10-27T162203Z-projector-geometry-qx"


def local_probability(data: int, ancilla: int, other: int, angle: int, endpoint: str) -> Decimal:
    """Born probabilities from Q_theta|0,+>, independently of the circuit analyzer."""
    zero, one = Decimal(0), Decimal(1)
    axes = {0: (one, zero), 45: (Decimal(2).sqrt() / 2,) * 2, 90: (zero, one)}
    cosine, sine = axes[angle]
    parity_sign = -1 if (ancilla + other) % 2 else 1
    if endpoint == "x":
        numerator = one + parity_sign * cosine + (-1 if data else 1) * parity_sign * sine
        return numerator * numerator / 16
    if endpoint != "z":
        raise ValueError("endpoint must be z or x")
    numerator = one + parity_sign * cosine if data == 0 else parity_sign * sine
    return numerator * numerator / 8


def outcome_probability(arguments: tuple[tuple[int, ...], tuple[int, ...], str]) -> tuple[str, Decimal]:
    outcome, angles, endpoint = arguments
    with localcontext() as context:
        context.prec = 50
        probability = Decimal(1)
        for replica, angle in enumerate(angles):
            offset = 3 * replica
            probability *= local_probability(outcome[offset], outcome[offset + 1], outcome[offset + 2], angle, endpoint)
    return "".join(map(str, reversed(outcome))), probability


def audit() -> dict[str, Any]:
    rows = []
    with localcontext() as context:
        context.prec = 50
        for filename, endpoint, angles in (
            ("geometry-z.cq", "z", (0, 45, 90)),
            ("mutation-z.cq", "z", (0, 0, 0)),
            ("geometry-x.cq", "x", (0, 45, 90)),
        ):
            path = RUN / "raw" / f"{filename}.json"
            shots = json.loads(path.read_text())
            if len(shots) != 2048 or any(len(shot) != 9 or set(shot) - {"0", "1"} for shot in shots):
                raise ValueError("the QX audit requires 2048 nine-bit shots")
            counts = Counter(shots)
            probabilities: dict[str, Decimal] = dict(
                ordered_map(
                    outcome_probability,
                    [(outcome, angles, endpoint) for outcome in itertools.product((0, 1), repeat=9)],
                )
            )
            normalization = sum(probabilities.values(), Decimal(0))
            if abs(normalization - 1) > Decimal("1e-45"):
                raise ValueError("independent joint law is not normalized")
            deviations = [
                abs(Decimal(counts[key]) / len(shots) - probability) for key, probability in probabilities.items()
            ]
            rows.append(
                {
                    "file": filename,
                    "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "shots": len(shots),
                    "ideal_support_size": sum(probability > 0 for probability in probabilities.values()),
                    "observed_support_size": len(counts),
                    "impossible_outcomes": {
                        key: count for key, count in sorted(counts.items()) if probabilities[key] == 0
                    },
                    "normalization_decimal": format(normalization, ".12f"),
                    "total_variation_decimal": format(sum(deviations) / 2, ".12f"),
                    "max_cell_absolute_deviation_decimal": format(max(deviations), ".12f"),
                    "adjacent_equal_count": sum(left == right for left, right in zip(shots, shots[1:], strict=False)),
                    "adjacent_pairs": len(shots) - 1,
                    "iid_adjacent_equal_probability_decimal": format(
                        sum(p * p for p in probabilities.values()), ".12f"
                    ),
                    "shots_lexicographically_sorted": shots == sorted(shots),
                    "block_herald_counts": [
                        [
                            sum(shot[7 - 3 * replica] == "0" for shot in shots[start : start + 256])
                            for replica in range(3)
                        ]
                        for start in range(0, len(shots), 256)
                    ],
                }
            )
    return {
        "schema": "qi-projector-joint-law-audit-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "arithmetic": "deterministic Decimal at precision 50; 12-place diagnostic strings",
        "interpretation": (
            "Supplemental full-law and shot-order diagnostics, "
            "not preregistered significance tests or proof of IID shots."
        ),
        "circuits": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json.dumps(audit(), indent=2, sort_keys=True) + "\n"
    if arguments.check:
        if arguments.check.read_text() != content:
            raise SystemExit("QX full-law audit differs from retained raw data")
        print("QX full-law audit matches")
    else:
        with arguments.out.open("x") as destination:
            destination.write(content)


if __name__ == "__main__":
    main()
