"""Analyze the Tuna-17 one-CZ null series with exact arithmetic: the byte-reproducible successor of `--analyze`.

scripts/qi_pathion_one_cz_null_cases.py stays the pinned producer of the series' circuits, its preregistered
decision rule and its schema-v2 record. Its readout-corrected statistics call np.linalg.solve, whose last bits
follow the OpenBLAS build and core: regenerating the record under the distribution's OpenBLAS, or under a forced
Sandybridge or Nehalem core of the pinned wheel, moves 152 to 209 floats by up to 1.8e-14 absolute (about 1e-12
relative), all in `statistics/readout_corrected` or in its copy, the `visibility_readout_corrected` leaf of a row;
every string, boolean, integer and the decision stay equal. This module keeps the predecessor's selection, shot
reading, twin contrasts, joint calibration, drift covariate and
decision rule by import (a rebound copy of a predecessor function resolves its module-level names through
`rebound`'s overrides, so the predecessor module is never modified) and replaces the arithmetic that depends on the
numeric identity:

- gororoba_quantum/exact_contrast_statistics.py evaluates, for the 16 evaluations (raw and readout-corrected) of the
  eight 32-outcome coin jobs, the readout correction, the contrasts and the central-difference delta approximation of
  the errors in exact rational arithmetic on the integer counts and the integer-ratio assignment rates of the batch's
  readout pair, and rounds each reported float once (value: float(Fraction); error: the correctly rounded square
  root of the exact variance). The evaluations are independent, so they run through parallel.ordered_map.
- `pooled` and `heterogeneity` multiply where the predecessor squares with the libm pow call, whose result is not
  always the correctly rounded square.
- `contraction_per_cz_implied` is the correctly rounded `cz`-th root of the stored corrected visibility.

No decimal rounding enters: a rounding grid cannot absorb a drift of 1e-12 relative and still has values that
straddle a cell boundary under some numeric identity. The record names the predecessor record by sha256 and states
the rule (docs/design/native-numeric-replay.md, contract item 7). A QX control record keeps the predecessor.

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_analysis.py --analyze RUN_DIR... --out NEWFILE
       "$PYTHON" scripts/qi_pathion_one_cz_null_analysis.py --check RUN_DIR... [--record FILE] [--predecessor FILE]
--check regenerates the record, refuses any byte that differs from the retained one and, with --predecessor, also
refuses a difference between the two records beyond FLOAT_ABSOLUTE + FLOAT_RELATIVE x magnitude in a float or any
difference in another leaf."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import types
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402

import exact_contrast_statistics as ecs  # noqa: E402
import parallel  # noqa: E402
import pathion_coset_analysis as pca  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402

SCHEMA = "qi-pathion-one-cz-null-analysis-v3"
PREDECESSOR_RECORD = "results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.json"
PREDECESSOR_SHA256 = "e39956c54bd79740a94785712c398ba5fe65b33a9e03c58c2ca179374a0cc693"
SUCCESSOR_RECORD = "results/quantum_inspire/pathion_one_cz_null_tuna_17_analysis.v3.json"
ZERO_WEIGHT = Fraction(pkm.ZERO)
# The exact value and the predecessor's float path (a central difference of floats that cancels, then LAPACK and
# einsum) agree within this bound per float; the retained record differs from the exact value by at most 4.1e-14
# absolute and 2.0e-12 relative.
FLOAT_ABSOLUTE = 1.0e-12
FLOAT_RELATIVE = 1.0e-9
ARITHMETIC = {
    "rule": (
        "Each float of template_rows.*.*.statistics (and its copy visibility_readout_corrected) is float(Fraction) of "
        "an exact rational of the integer shot counts and integer-ratio readout rates, and each of its errors is the "
        "correctly rounded square root of the exact-rational evaluation of the central-difference delta "
        "approximation of the variance; contraction_per_cz_implied is the correctly rounded cz-th root of the stored "
        "corrected visibility; pooled and chi-square sums multiply where the predecessor called pow. Every other float "
        "(bin, selector and batch contrasts, calibration, drift covariate, decision numbers) comes from IEEE basic "
        "operations, math.sqrt, math.hypot, CPython's float sum and numpy sums of at most 32 values, the 32-value ones "
        "over integer shot counts. No decimal rounding applies, and no BLAS, LAPACK, einsum or libm pow call enters "
        "a float."
    ),
    "authority": "docs/design/native-numeric-replay.md, contract item 7",
    "implementation": "gororoba_quantum/exact_contrast_statistics.py",
}


def rebound(function: Callable[..., Any], **overrides: Any) -> Any:
    """A copy of a predecessor `function` whose module-level names resolve through `overrides` first.

    The copy shares the code and defaults of the original, so the preregistered rule it implements keeps one
    home, and its calls to other module-level functions reach the overrides."""
    if not isinstance(function, types.FunctionType):
        raise TypeError(f"{function!r} is not a plain function")
    clone = types.FunctionType(
        function.__code__, {**function.__globals__, **overrides}, function.__name__, function.__defaults__
    )
    clone.__kwdefaults__ = function.__kwdefaults__
    return clone


def pooled(values: list[tuple[float, float]]) -> tuple[float, float]:
    """Inverse-variance mean and its standard error of (value, se) pairs, with products where pow would square."""
    weights = [1.0 / (se * se) for _, se in values]
    mean = sum(w * v for w, (v, _) in zip(weights, values, strict=True)) / sum(weights)
    return mean, math.sqrt(1.0 / sum(weights))


def heterogeneity(values: list[tuple[float, float]]) -> float:
    """Chi-square of (value, se) pairs about their inverse-variance mean."""
    mean, _ = pooled(values)
    return sum(((v - mean) / se) * ((v - mean) / se) for v, se in values)


decide_estimates = rebound(oc.decide_estimates, pooled=pooled, heterogeneity=heterogeneity)
joint_statistics = rebound(oc.joint_statistics, pooled=pooled)


def exact_assignment(
    shots: dict[str, list[str]], batch: str, qubits: list[int]
) -> dict[int, tuple[Fraction, Fraction]] | None:
    """(e01, e10) of the register qubits from the readout pair of one batch as exact ratios of shot counts."""
    zero = shots.get(f"{batch}/readout-0.cq")
    one = shots.get(f"{batch}/readout-1.cq")
    if zero is None or one is None:
        return None
    return {
        q: (
            Fraction(sum(pca.bit(s, q) for s in zero), len(zero)),
            1 - Fraction(sum(pca.bit(s, q) for s in one), len(one)),
        )
        for q in qubits
    }


def statistics_record(result: ecs.ContrastResult) -> dict[str, Any]:
    """The statistics record of pca.pack_statistics for an exact result (None reads as not finite)."""
    undefined = float("nan")
    return pca.pack_statistics(
        np.array([undefined if v is None else v for v in result.values]),
        np.array([undefined if e is None else e for e in result.errors]),
    )


def template_row(
    name: str,
    template: dict[str, Any],
    counts: np.ndarray,
    raw: dict[str, Any],
    corrected: dict[str, Any] | None,
) -> dict[str, Any]:
    """The predecessor's template row with its statistics replaced by the exact ones.

    cc.template_row builds every field that is not a coin-job statistic (bin contrasts, signed z, selector
    contrast, visibility of the raw bins); the fields that follow from the statistics are redone here."""
    row = cc.template_row(name, template, counts, None, np.array(template["ideal_c"]))
    row["statistics"] = {"raw": raw} if corrected is None else {"raw": raw, "readout_corrected": corrected}
    if corrected is not None:
        visibility = corrected["visibility"]
        row["visibility_readout_corrected"] = visibility
        if visibility is not None and visibility > 0:
            implied = ecs.correctly_rounded_root(Fraction(visibility), template["cz"])
            row["contraction_per_cz_implied"] = implied
            low, high = cc.RHO_BAND
            row["against_rho_band"] = "below" if implied < low else "above" if implied > high else "inside"
    return row


def batch_estimates(
    shots: dict[str, list[str]], manifest: dict[str, Any]
) -> tuple[dict[str, dict[str, list[tuple[float, float]]]], dict[str, dict[str, dict[str, Any]]]]:
    """oc.batch_estimates with the 16 evaluations (raw and readout-corrected) of the eight 32-outcome coin jobs
    computed exactly, in parallel over the evaluations."""
    templates = manifest["templates"]
    register = [int(q) for q in manifest["register"]]
    brackets = {
        batch: asg
        for batch in sorted({k.split("/")[0] for k in shots})
        if (asg := exact_assignment(shots, batch, register)) is not None
    }
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {t: {"base": [], "twin": []} for t in templates}
    detail: dict[str, dict[str, dict[str, Any]]] = {t: {} for t in templates}
    bases: list[tuple[str, str, np.ndarray]] = []
    twins: dict[tuple[str, str], dict[int, list[str]]] = {}
    for key in sorted(shots):
        batch, name = key.split("/")
        kind, template, coin = oc.parse_file(name)
        if kind == "base" and template is not None:
            bases.append((batch, template, cc.coin_counts(shots[key], templates[template]["roles"])))
        elif kind == "twin" and template is not None and coin is not None:
            twins.setdefault((batch, template), {})[coin] = shots[key]
    jobs: list[ecs.ContrastJob] = []
    for batch, template, counts in bases:
        t = templates[template]
        sign = tuple(int(s) for s in np.sign(np.array(t["ideal_c"])))
        tally = tuple(int(n) for n in counts)
        jobs.append(ecs.ContrastJob(tally, sign, None, ZERO_WEIGHT))
        if batch in brackets:
            readout = tuple(brackets[batch][t["roles"][k]] for k in cc.KEYS)
            jobs.append(ecs.ContrastJob(tally, sign, readout, ZERO_WEIGHT))
    results = iter(parallel.ordered_map(ecs.contrast_statistics, jobs, min_items=1))
    for batch, template, counts in bases:
        raw = statistics_record(next(results))
        corrected = statistics_record(next(results)) if batch in brackets else None
        plus, minus = cc.piles(counts)
        rows[template]["base"].append(pca.selector_stat(plus, minus))
        detail[template][batch] = template_row(template, templates[template], counts, raw, corrected)
    for (batch, template), pair in sorted(twins.items()):
        if set(pair) != {0, 1}:
            raise ValueError(f"{batch} holds one coin twin of {template}")
        qubit = templates[template]["roles"]["selector"]
        rates, variances = [], []
        for coin in (1, 0):
            n = len(pair[coin])
            p = sum(1 for s in pair[coin] if pca.bit(s, qubit) == 0) / n
            rates.append(p)
            variances.append(p * (1 - p) / n)
        rows[template]["twin"].append((rates[0] - rates[1], math.sqrt(sum(variances))))
    return rows, detail


evaluate = rebound(
    oc.evaluate, batch_estimates=batch_estimates, decide_estimates=decide_estimates, joint_statistics=joint_statistics
)
analyze_series = rebound(oc.analyze, evaluate=evaluate, ANALYSIS_SCHEMA=SCHEMA)


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """The schema-v3 record of the collected Tuna-17 batches."""
    record = analyze_series(run_dirs)
    if record["claim_kind"] != "hardware acquisition":
        raise SystemExit("a QX control record keeps the predecessor producer's schema-v2 analysis")
    return {
        **record,
        "arithmetic": ARITHMETIC,
        "succeeds": {
            "schema": oc.ANALYSIS_SCHEMA,
            "producer": "scripts/qi_pathion_one_cz_null_cases.py --analyze",
            "record": PREDECESSOR_RECORD,
            "record_sha256": PREDECESSOR_SHA256,
        },
    }


def record_text(record: dict[str, Any]) -> str:
    """The retained form of a record: sorted keys, one-space indent, shortest round-trip floats, no NaN."""
    return json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n"


def compare_records(predecessor: Any, successor: Any, floats: list[tuple[float, float]], path: str = "") -> list[str]:
    """The differences between two records' leaves, and in `floats` the (absolute, relative) difference of each
    float pair.

    A float pair differs when its absolute difference exceeds FLOAT_ABSOLUTE + FLOAT_RELATIVE times the larger
    magnitude; every other leaf (string, boolean, integer, null, key set, list length) must be equal."""
    found: list[str] = []
    if isinstance(predecessor, dict) and isinstance(successor, dict):
        for key in sorted(predecessor.keys() | successor.keys()):
            if key in predecessor and key in successor:
                found += compare_records(predecessor[key], successor[key], floats, f"{path}/{key}")
            else:
                found.append(f"{path}/{key} is present in one record only")
    elif isinstance(predecessor, list) and isinstance(successor, list):
        if len(predecessor) != len(successor):
            return [f"{path} holds {len(predecessor)} and {len(successor)} entries"]
        for index, (a, b) in enumerate(zip(predecessor, successor, strict=True)):
            found += compare_records(a, b, floats, f"{path}[{index}]")
    elif isinstance(predecessor, float) and isinstance(successor, float):
        difference = abs(predecessor - successor)
        magnitude = max(abs(predecessor), abs(successor))
        floats.append((difference, difference / magnitude if magnitude else 0.0))
        if difference > FLOAT_ABSOLUTE + FLOAT_RELATIVE * magnitude:
            found.append(f"{path} is {predecessor!r} and {successor!r}")
    elif type(predecessor) is not type(successor) or predecessor != successor:
        found.append(f"{path} is {predecessor!r} and {successor!r}")
    return found


def check(run_dirs: list[Path], record: Path, predecessor: Path | None) -> int:
    """Regenerate the record from `run_dirs`; return 1 on a byte or a predecessor mismatch."""
    text = record_text(analyze(run_dirs))
    retained = record.read_text(encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    shown = record.relative_to(ROOT) if record.is_relative_to(ROOT) else record
    if text != retained:
        first = next(
            (i for i, (a, b) in enumerate(zip(text, retained, strict=False)) if a != b), min(len(text), len(retained))
        )
        print(f"regenerated record (sha256 {digest}) differs from {shown} at byte {first}")
        return 1
    print(f"regenerated record equals {shown} byte for byte: sha256 {digest}")
    if predecessor is None:
        return 0
    if hashlib.sha256(predecessor.read_bytes()).hexdigest() != PREDECESSOR_SHA256:
        print(f"{predecessor} is not the predecessor record that PREDECESSOR_SHA256 names")
        return 1
    floats: list[tuple[float, float]] = []
    differences = compare_records(json.loads(predecessor.read_text(encoding="utf-8")), json.loads(text), floats)
    # The successor adds the schema, arithmetic and succeeds keys; every other path must agree.
    differences = [d for d in differences if not d.startswith(("/schema ", "/arithmetic ", "/succeeds "))]
    if differences:
        print("\n".join(differences[:20]))
        return 1
    print(
        f"predecessor and successor agree: {len(floats)} floats within {FLOAT_ABSOLUTE:g} absolute plus "
        f"{FLOAT_RELATIVE:g} relative (largest {max(d for d, _ in floats):.3e} absolute, "
        f"{max(r for _, r in floats):.3e} relative), every other leaf equal"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--check", type=Path, nargs="+", metavar="RUN_DIR")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--record", type=Path, default=ROOT / SUCCESSOR_RECORD)
    parser.add_argument("--predecessor", type=Path)
    args = parser.parse_args()
    if args.check:
        return check(args.check, args.record, args.predecessor)
    if args.out is None:
        parser.error("--analyze needs --out")
    with args.out.open("x", encoding="utf-8") as handle:
        handle.write(record_text(analyze(args.analyze)))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
