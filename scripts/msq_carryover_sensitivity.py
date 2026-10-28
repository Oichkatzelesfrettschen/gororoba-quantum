"""How an initial excitation carried over from the previous shot moves the pinching departure, per member class.

The pinching analysis (measurement_sequence_analysis) corrects every arm through the ro0 and t1 readout brackets and
fits an initialization excitation from the in-job T1 series. This sizing probe plants an extra initial excitation
delta through the analysis's own device model, on every member at once and on one member class at a time, and
reports the signed departure shift per unit delta for each qubit. It runs on two sets of execution contexts: the
analysis's eight fixture qubits, where the model generates every count, and the retained width-32 envelope run
(`results/live/2026-10-27T014422.881898Z`), where the planted shift is added to the measured counts at that run's
contexts and the analysis refits the device.

Each circuit of a job has one predecessor in the execution order, which the service does not fix, so each member class
can inherit any carried-over excitation in [eps0, eps0 + D], with D the spread between an |1> end state and an |0>
end state. The departure bias is then bounded per qubit by D times the allocation coefficient max(sum of the positive
class coefficients, |sum of the negative ones|). Counts use 10^7 shots so whole-shot rounding hides no first-order
shift. It is a sizing input for the successor's design, not a test of a device.
"""

from __future__ import annotations

import argparse
import functools
import json
import statistics
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import msq_envelope_exploratory as exploratory  # noqa: E402

import measurement_sequence_analysis as msa  # noqa: E402

SCHEMA = "msq-carryover-sensitivity-v2"
SHOTS = 10**7
DELTA = 0.01
RUN = ROOT / "results/live/2026-10-27T014422.881898Z"
# The run's departure standard errors on these qubits exceed twice the planning value, so the analysis marks them
# uninformative (envelope-run-exploratory.json).
RUN_UNINFORMATIVE = (149, 154)


def classes() -> dict[str, Callable[[int], list[str]]]:
    """Every member class that enters the departure: each arm and step count, ro0, and each t1 delay."""
    table: dict[str, Callable[[int], list[str]]] = {
        f"{arm}{n}": functools.partial(arm_members, arm, n) for arm, n in msa.group_keys()
    }
    table["ro0"] = ro0_member
    for k in range(msa.T1_COUNT):
        table[f"t1_d{k}"] = functools.partial(t1_member, k)
    return table


def arm_members(arm: str, n: int, qubit: int) -> list[str]:
    return list(msa.member_names(arm, n, qubit))


def ro0_member(qubit: int) -> list[str]:
    return [msa.ro0_name(qubit)]


def t1_member(k: int, qubit: int) -> list[str]:
    return [msa.t1_names(qubit)[k]]


def departures(counts: dict[int, Any], planned: dict[int, Any]) -> dict[int, float]:
    return {q: float(r["departure_n16"]["difference"]) for q, r in msa.evaluate(counts, planned).items()}


def planted(
    counts: dict[int, Any], base: dict[int, Any], shifted: dict[int, Any], names: Callable[[int], list[str]]
) -> dict[int, Any]:
    """counts with each named member moved by the model's shift in its P1 at the planted excitation."""
    out = {q: {**counts[q], "final": dict(counts[q]["final"])} for q in counts}
    for q in out:
        for name in names(q):
            ones, n = counts[q]["final"][name]
            moved = (shifted[q][name][0] - base[q][name][0]) / SHOTS
            out[q]["final"][name] = (ones + round(moved * n), n)
    return out


def section(contexts: dict[int, Any], counts: dict[int, Any] | None, floor: float) -> dict[str, Any]:
    models = {q: msa.device_model(ctx) for q, ctx in contexts.items()}
    base = {q: c["final"] for q, c in msa.device_counts(models, contexts, SHOTS).items()}
    shifted_models = {q: msa.device_model(ctx, p_init=models[q]["p_init"] + DELTA) for q, ctx in contexts.items()}
    shifted = {q: c["final"] for q, c in msa.device_counts(shifted_models, contexts, SHOTS).items()}
    measured = counts if counts is not None else {q: {"final": dict(base[q])} for q in contexts}
    planned = msa.with_planning(contexts, floor)
    reference = departures(measured, planned)

    def coefficients(names: Callable[[int], list[str]]) -> dict[int, float]:
        moved = departures(planted(measured, base, shifted, names), planned)
        return {q: (moved[q] - reference[q]) / DELTA for q in contexts}

    every = coefficients(lambda q: [n for n in measured[q]["final"] if n in base[q]])
    per_class = {label: coefficients(names) for label, names in classes().items()}
    allocation = {
        q: max(
            sum(max(0.0, c[q]) for c in per_class.values()),
            -sum(min(0.0, c[q]) for c in per_class.values()),
        )
        for q in contexts
    }

    def summary(values: dict[int, float]) -> dict[str, float]:
        return {"median": statistics.median(values.values()), "min": min(values.values()), "max": max(values.values())}

    return {
        "qubits": sorted(contexts),
        "every_member": {"per_qubit": {str(q): v for q, v in sorted(every.items())}, **summary(every)},
        "classes": {
            label: {"per_qubit": {str(q): v for q, v in sorted(c.items())}, **summary(c)}
            for label, c in per_class.items()
        },
        "allocation_coefficient": {
            "per_qubit": {str(q): v for q, v in sorted(allocation.items())},
            **summary(allocation),
        },
    }


def run() -> dict[str, Any]:
    fixture = msa.fixture_contexts(tuple(range(len(msa.FIXTURE_SCALES))), None)
    record, _collected, distributions, executed = exploratory.counts(RUN)
    qubits = [int(q) for q in record["family_configuration"]["qubits"] if int(q) not in RUN_UNINFORMATIVE]
    every_context = msa.contexts_from_record(record, executed)
    contexts = {q: every_context[q] for q in qubits}
    counts = msa.member_counts_from_distributions(distributions, executed, qubits)
    return {
        "schema": SCHEMA,
        "shots": SHOTS,
        "delta": DELTA,
        "fixture": section(fixture, None, msa.DEMONSTRATION_SCATTER_FLOOR),
        "run": {
            "directory": RUN.relative_to(ROOT).as_posix(),
            **section(contexts, counts, msa.DEMONSTRATION_SCATTER_FLOOR),
        },
    }


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
