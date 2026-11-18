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
import math
import sys
from functools import cache, partial
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_one_cz_null_analysis as ana  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402

import parallel  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

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


@cache
def gated(batch_chi2: float) -> Any:
    """The v3 decision with the batch heterogeneity bound `batch_chi2` in place of oc.BATCH_CHI2."""
    return ana.rebound(ana.decide_estimates, BATCH_CHI2=batch_chi2)


def decide_estimates(
    rows: dict[str, dict[str, list[tuple[float, float]]]],
    b0_like_z: float | None = None,
    batch_chi2: float | None = None,
) -> dict[str, Any]:
    """The v3 decision of per-batch estimates with the v2 twin control: a superposition-only reading needs
    t0 >= -Z_RESOLVE se, and a t0 below that relabels it `unresolved_negative_twin`. `batch_chi2` is the bound of the
    replicate-batch heterogeneity gate for a case whose replicate count differs from the predecessor's two
    (oc.BATCH_CHI2 when None)."""
    decide = ana.decide_estimates if batch_chi2 is None else gated(batch_chi2)
    decision: dict[str, Any] = decide(rows, b0_like_z)
    t0, se = decision["numbers"]["t_b0"]
    if decision["label"] == "superposition_only" and t0 < -oc.Z_RESOLVE * se:
        outcome, effect = OUTCOMES[NEGATIVE_TWIN]
        return {**decision, "label": NEGATIVE_TWIN, "outcome": outcome, "a5_186": effect, "decided": False}
    return decision


def _series_label(
    draw: tuple[np.ndarray, np.ndarray],
    mean: dict[str, float],
    se_base: dict[str, float],
    se_twin: float,
    b0_like_z: float,
) -> str:
    """The v2 label of one simulated series from its noise and drift draws, shape (templates, 2, REPLICATES). The rows
    are those of the predecessor's simulation, so the draws of a shared world give the same estimates."""
    noise, drift = draw
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for j, name in enumerate(oc.TEMPLATES):
        key = "b0" if name == "b0" else "k"
        rows[name] = {
            "base": [
                (mean[f"s_{key}"] + se_base[name] * noise[j, 0, r] + drift[j, 0, r], se_base[name])
                for r in range(oc.REPLICATES)
            ],
            "twin": [
                (mean[f"t_{key}"] + se_twin * noise[j, 1, r] + drift[j, 1, r], se_twin) for r in range(oc.REPLICATES)
            ],
        }
    return str(decide_estimates(rows, b0_like_z)["label"])


def simulated_shares(
    draws: int = oc.OC_DRAWS,
    drift_sd: float = 0.0,
    b0_like_z: float | None = None,
    worlds: dict[str, dict[str, float]] | None = None,
) -> dict[str, dict[str, float]]:
    """Frequency of each v2 label per world (WORLDS when None) from `draws` simulated series, seeded from QRNG value
    oc.OC_SEED_INDEX of oc.OC_DRAW as oc.operating_characteristics is.

    Worlds draw in dict order from one generator, so the worlds of oc.WORLDS_SIZED listed first reproduce the
    predecessor's draws. The labels come from parallel.ordered_map in series order; `_series_label` is a module-level
    function, so spawned workers unpickle it and its v2 decision by reference."""
    band = oc.B0_LIKE_Z if b0_like_z is None else b0_like_z
    seed = int(read_record(oc.OC_DRAW)["values"][oc.OC_SEED_INDEX])
    rng = np.random.default_rng(seed)
    se_base = {t: 1.0 / math.sqrt(oc.CONTROL_SHOTS if t == "b0" else oc.BATCH_SHOTS) for t in oc.TEMPLATES}
    se_twin = math.sqrt(0.5 / oc.BATCH_SHOTS)
    out: dict[str, dict[str, float]] = {}
    for world, mean in (WORLDS if worlds is None else worlds).items():
        noise = rng.normal(size=(draws, len(oc.TEMPLATES), 2, oc.REPLICATES))
        drift = rng.normal(scale=drift_sd, size=(draws, len(oc.TEMPLATES), 2, oc.REPLICATES))
        labels = parallel.ordered_map(
            partial(_series_label, mean=mean, se_base=se_base, se_twin=se_twin, b0_like_z=band),
            list(zip(noise, drift, strict=True)),
        )
        counts: dict[str, int] = {}
        for label in labels:
            counts[label] = counts.get(label, 0) + 1
        out[world] = {label: round(n / draws, 4) for label, n in sorted(counts.items())}
    return out


def operating_characteristics() -> dict[str, Any]:
    """Shares of each v2 label per world, stationary and under the preregistered batch drift."""
    return {
        "qrng_draw": oc.OC_DRAW,
        "seed_index": oc.OC_SEED_INDEX,
        "draws_per_world": oc.OC_DRAWS,
        "stationary": simulated_shares(),
        f"batch_drift_sd_{oc.OC_DRIFT_SD}": simulated_shares(drift_sd=oc.OC_DRIFT_SD),
    }


def ten_thousandths(value: float) -> int:
    """10000 x a value that carries four decimals (a share or a contrast), as an integer, so the record holds no
    float and a replay of it needs no numeric binding."""
    return round(value * 10000)


def record() -> dict[str, Any]:
    ocs = operating_characteristics()
    tables = {
        key: {w: {label: ten_thousandths(share) for label, share in row.items()} for w, row in table.items()}
        for key, table in ocs.items()
        if isinstance(table, dict)
    }
    return {
        "rule": RULE,
        "supersedes": "the twin control (item 4) of the preregistered rule in scripts/qi_pathion_one_cz_null_cases.py",
        "twin_control": TWIN_CONTROL,
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in OUTCOMES.items()},
        "unit": "worlds and operating characteristics in ten-thousandths: 164 is 0.0164, 9706 is a share of 0.9706",
        "worlds": {w: {k: ten_thousandths(v) for k, v in mean.items()} for w, mean in WORLDS.items()},
        "operating_characteristics": {
            **{key: value for key, value in ocs.items() if not isinstance(value, dict)},
            **tables,
        },
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
