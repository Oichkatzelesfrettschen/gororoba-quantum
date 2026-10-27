"""How an initial excitation carried over from the previous shot moves the pinching endpoints.

The pinching analysis (measurement_sequence_analysis) corrects every arm through the ro0 and t1 readout brackets and
fits an initialization excitation from the in-job T1 series, so an excitation common to every member divides out to
first order. An excitation that differs between members does not. This sizing probe plants an extra initial
excitation delta, on every member and on one member class at a time, through the analysis's own device model on its
eight fixture qubits, and reports the largest endpoint shift per unit delta. Counts use 10^7 shots so whole-shot
rounding hides no first-order shift. It is a sizing input for the successor's carryover screen, not a test of a
device.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import measurement_sequence_analysis as msa  # noqa: E402

SCHEMA = "msq-carryover-sensitivity-v1"
SHOTS = 10**7
DELTAS = (0.002, 0.01)
ENDPOINTS = ("departure", "settle_gap", "contrast")
CLASSES: dict[str, Callable[[int], list[str]]] = {
    "measure_n16": lambda q: msa.member_names("measure", 16, q),
    "measure_all": lambda q: [n for k in (2, 4, 8, 16) for n in msa.member_names("measure", k, q)],
    "unitary_n16": lambda q: msa.member_names("unitary", 16, q),
    "ro0": lambda q: [msa.ro0_name(q)],
    "t1_d0": lambda q: [msa.t1_names(q)[0]],
}


def endpoints(contexts: dict[int, Any], counts: dict[int, Any]) -> dict[int, dict[str, float]]:
    rows = msa.evaluate(counts, msa.with_planning(contexts, msa.DEMONSTRATION_SCATTER_FLOOR))
    return {
        q: {
            "departure": float(r["departure_n16"]["difference"]),
            "settle_gap": float(r["settle_n16"]["gap_difference"]),
            "contrast": float(r["contrast_n16"]["contrast"]),
        }
        for q, r in rows.items()
    }


def sensitivity(
    base: dict[int, dict[str, float]], other: dict[int, dict[str, float]], delta: float
) -> dict[str, float]:
    return {key: max(abs(other[q][key] - base[q][key]) for q in base) / delta for key in ENDPOINTS}


def run() -> dict[str, Any]:
    contexts = msa.fixture_contexts(tuple(range(len(msa.FIXTURE_SCALES))), None)
    base_models = {q: msa.device_model(ctx) for q, ctx in contexts.items()}
    base_counts = msa.device_counts(base_models, contexts, SHOTS)
    base = endpoints(contexts, base_counts)
    rows: dict[str, Any] = {}
    for delta in DELTAS:
        shifted_models = {
            q: msa.device_model(ctx, p_init=base_models[q]["p_init"] + delta) for q, ctx in contexts.items()
        }
        shifted_counts = msa.device_counts(shifted_models, contexts, SHOTS)
        rows[f"every_member@{delta}"] = sensitivity(base, endpoints(contexts, shifted_counts), delta)
        for label, names in CLASSES.items():
            spliced = {q: {"final": dict(base_counts[q]["final"])} for q in base_counts}
            for q in spliced:
                for name in names(q):
                    spliced[q]["final"][name] = shifted_counts[q]["final"][name]
            rows[f"{label}_only@{delta}"] = sensitivity(base, endpoints(contexts, spliced), delta)
    return {"schema": SCHEMA, "shots": SHOTS, "qubits": len(contexts), "per_unit_delta": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    text = json.dumps(run(), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
