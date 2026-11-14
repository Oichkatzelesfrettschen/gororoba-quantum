"""Twin-control rule v2 of the Tuna-17 one-CZ null series: a b0 twin contrast must be compatible with zero.

The preregistered rule (scripts/qi_pathion_one_cz_null_cases.py, `decide_estimates`, written in CASE.md under
"Preregistered decision rules", item 4) reads "the offset exists only with the coin in superposition" whenever
b0's twin contrast t0 sits below +3 standard errors and the base contrast s0 exceeds t0 by 3 combined standard
errors. That condition also holds for a large negative t0, a twin response of opposite sign that no modeled
mechanism predicts. Rule v2 keeps every other step of the rule and its numbers, and requires |t0| <= 3 standard
errors for the superposition-only row; a t0 below -3 standard errors reads `unresolved_negative_twin`, which
decides nothing. The case bytes and the retained schema-v2 and schema-v3 records keep the first rule, so this
module is the versioned successor for a case that preregisters v2. It applies the v3 analyzer's decision
(qi_pathion_one_cz_null_analysis.py, exact pooled sums) and relabels the one row.

The operating characteristics of v2 take the eight worlds of the preregistered table (`oc.WORLDS_SIZED`, first, so
they draw as the stored table does from QRNG value `oc.OC_SEED_INDEX` of `oc.OC_DRAW`) and the negative-twin world,
which no simulated mechanism produces: b0's twin contrast is the negative of its base contrast and the 6-CZ blocks
read zero (a hypothesis row that exercises the new label).

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_rule_v2.py (--write | --check) [--record FILE]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_one_cz_null_analysis as ana  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402

RULE = "qi-pathion-one-cz-null-rule-v2"
RECORD = "results/quantum_inspire/pathion_one_cz_null_tuna_17_rule_v2.json"
NEGATIVE_TWIN = "unresolved_negative_twin"
NEGATIVE_TWIN_WORLD = "twin_opposite_sign"
NEGATIVE_TWIN_MEAN = {"s_b0": 0.0164, "t_b0": -0.0164, "s_k": 0.0, "t_k": 0.0}
OUTCOMES: dict[str, tuple[str, str]] = {
    **oc.OUTCOMES,
    NEGATIVE_TWIN: (
        "unresolved: b0's classical-coin twin contrast reads below zero by more than three standard errors, a response "
        "that matches no modeled mechanism (each predicts a twin contrast at or above zero)",
        "unchanged; the numbers are reported",
    ),
}
TWIN_CONTROL = (
    f"b0 twin contrast t0 above {oc.Z_RESOLVE} se; if not, t0 within {oc.Z_RESOLVE} se of zero (|t0| <= {oc.Z_RESOLVE} "
    f"se) and s0 - t0 above {oc.Z_RESOLVE} combined se, the offset exists only with the coin in superposition; t0 "
    f"below -{oc.Z_RESOLVE} se is unresolved (negative twin); otherwise unresolved"
)
WORLDS: dict[str, dict[str, float]] = {
    **{
        w: {"s_b0": 0.0, "t_b0": 0.0, "s_k": 0.0, "t_k": 0.0} if w == "absent" else oc.PREDICTED[w]
        for w in oc.WORLDS_SIZED
    },
    NEGATIVE_TWIN_WORLD: NEGATIVE_TWIN_MEAN,
}


def decide_estimates(
    rows: dict[str, dict[str, list[tuple[float, float]]]], b0_like_z: float | None = None
) -> dict[str, Any]:
    """The v3 decision of per-batch estimates with the v2 twin control: a superposition-only reading needs
    t0 >= -Z_RESOLVE se, and a t0 below that relabels it `unresolved_negative_twin`."""
    decision: dict[str, Any] = ana.decide_estimates(rows, b0_like_z)
    t0, se = decision["numbers"]["t_b0"]
    if decision["label"] == "superposition_only" and t0 < -oc.Z_RESOLVE * se:
        outcome, effect = OUTCOMES[NEGATIVE_TWIN]
        return {**decision, "label": NEGATIVE_TWIN, "outcome": outcome, "a5_186": effect, "decided": False}
    return decision


def operating_characteristics() -> dict[str, Any]:
    """Shares of each v2 label per world, stationary and under the preregistered batch drift."""
    return {
        "qrng_draw": oc.OC_DRAW,
        "seed_index": oc.OC_SEED_INDEX,
        "draws_per_world": oc.OC_DRAWS,
        "stationary": oc.operating_characteristics(worlds=WORLDS, decide=decide_estimates),
        f"batch_drift_sd_{oc.OC_DRIFT_SD}": oc.operating_characteristics(
            drift_sd=oc.OC_DRIFT_SD, worlds=WORLDS, decide=decide_estimates
        ),
    }


def record() -> dict[str, Any]:
    return {
        "rule": RULE,
        "supersedes": "the twin control (item 4) of the preregistered rule in scripts/qi_pathion_one_cz_null_cases.py",
        "twin_control": TWIN_CONTROL,
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in OUTCOMES.items()},
        "worlds": WORLDS,
        "operating_characteristics": operating_characteristics(),
    }


def record_text() -> str:
    return json.dumps(record(), indent=1, sort_keys=True, allow_nan=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--record", type=Path, default=ROOT / RECORD)
    args = parser.parse_args()
    text = record_text()
    if args.write:
        args.record.write_text(text, encoding="utf-8")
        print(f"wrote {args.record}")
        return 0
    if text != args.record.read_text(encoding="utf-8"):
        print(f"{args.record} differs from the regenerated rule-v2 record")
        return 1
    print(f"{args.record} equals the regenerated rule-v2 record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
