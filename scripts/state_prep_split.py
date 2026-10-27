"""Split each controlled qubit's state-preparation excess into a history-dependent and a history-independent part.

The state-prep-control family reads every qubit's excited fraction after two shot histories at one repetition
delay: prep0 (initialize, measure) after a near-|0> history and x_history (initialize, measure, x) after an all-|1>
history, each arm in a job of its own. state_prep_excess.py folds both into one upper bound eps applied as an X
error before the circuit. This rule keeps the two parts apart:

- the history-dependent part hd = max(0, (x - p) / (1 - e01 - p)), x and p the x_history and prep0 excited
  fractions and e01 the largest prob_meas0_prep1 of the controls' execution calibrations: the population the
  previous shot leaves excited, which a circuit meets as an X error before its first gate;
- the history-independent part, prep0's excited fraction p, which a consumer sets against the calibration's own
  e10 at its decision (primorial_probe_case.split_excitation); excess the prep0 arm carries after a |0> history
  reads as a terminal readout flip, which an in-job assignment inversion absorbs.

Several controls may read one arm: the counterbalanced order prep0, x_history, x_history, prep0 pairs the k-th
prep0 job with the k-th x_history job in the order given. Counts pool over the replicates of an arm. The interval
of hd comes from one-sided Clopper-Pearson bounds on x and p, upper and lower each, simultaneous at family-wise
``alpha`` over the 4 Q bounds of Q qubits; each PUB's segment-leading shots, which follow an uncontrolled shot,
count against the upper bound as ones and leave the lower bound. hd is increasing in x and decreasing in p, so
its interval is [hd(x_lower, p_upper), hd(x_upper, p_lower)].

The replicate test reads whether job identity rather than shot history carries an arm's fraction: a qubit whose
replicates of one arm differ under a two-sided two-proportion test at ``alpha / (2 Q)`` is heterogeneous, and its
hd interval widens to the hull of the pooled interval and every replicate pair's own interval at the same level.

``--out FILE --control DIR ...`` writes the split; each control needs the state-prep-readout.json that
state_prep_excess.py --fetch-readout retains. ``--self-test`` checks the bound directions and the replicate test
on synthetic counts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_prep_excess as spe  # noqa: E402

sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import parallel  # noqa: E402

SCHEMA = "state-prep-split-v1"
ARMS = ("prep0", spe.STATE_PREP_HISTORY_ARM)


def history_dependent(x: float, p: float, e01: float) -> float:
    """hd = max(0, (x - p) / (1 - e01 - p)): the excited population a |1> history adds, inverted for e01."""
    spe.require(p < 1.0 - e01, f"prep0 fraction {p} reaches 1 - e01 = {1.0 - e01}")
    return max(0.0, (x - p) / (1.0 - e01 - p))


def bounds(ones: int, shots: int, segments: int, level: float) -> tuple[float, float]:
    """(lower, upper) one-sided Clopper-Pearson bounds at ``level`` each, segment-leading shots at their worst."""
    controlled = shots - segments
    lower = float(spe.cp_lower(np.asarray([max(ones - segments, 0)]), np.asarray([controlled]), level)[0])
    upper = float(spe.cp_upper(np.asarray([ones]), np.asarray([controlled]), level)[0])
    return lower, upper


def interval(x: list[int], p: list[int], e01: float, level: float) -> list[float]:
    """[lower, upper] of hd from x_history and prep0 count triples (ones, shots, segments)."""
    x_low, x_high = bounds(x[0], x[1], x[2], level)
    p_low, p_high = bounds(p[0], p[1], p[2], level)
    return [history_dependent(x_low, p_high, e01), history_dependent(x_high, p_low, e01)]


def homogeneous(replicates: list[list[int]], level: float) -> tuple[bool, float]:
    """Whether every replicate of an arm reads one excited fraction: a two-sided chi-square test at ``level``."""
    if len(replicates) < 2:
        return True, 1.0
    table = np.asarray([[ones, shots - ones] for ones, shots, _ in replicates], dtype=float)
    if (table.sum(axis=0) == 0).any():
        return True, 1.0
    _, p_value, _, _ = stats.chi2_contingency(table, correction=False)
    return bool(p_value >= level), float(p_value)


def qubit_split(item: tuple[Any, ...]) -> dict[str, Any]:
    """One qubit's split: its pooled hd and interval, replicate test and per-pair values.

    ``item`` is (cells, readouts, pair jobs, bound level, replicate level), cells the (ones, shots, segments) of each
    arm's replicates in order, readouts each arm's per-replicate execution readouts.
    """
    cells, readouts, jobs, level, replicate_level = item
    e01 = max(v["prob_meas0_prep1"] for arm in ARMS for replicate in readouts[arm] for v in replicate)
    pooled = {arm: [sum(cell[k] for cell in cells[arm]) for k in range(3)] for arm in ARMS}
    x, p = (pooled[arm][0] / pooled[arm][1] for arm in (spe.STATE_PREP_HISTORY_ARM, "prep0"))
    hd_interval = interval(pooled[spe.STATE_PREP_HISTORY_ARM], pooled["prep0"], e01, level)
    tests = {arm: homogeneous(cells[arm], replicate_level) for arm in ARMS}
    history = cells[spe.STATE_PREP_HISTORY_ARM]
    pairs = [
        {
            "prep0_job": prep0_job,
            "x_history_job": x_history_job,
            "hd": history_dependent(history[k][0] / history[k][1], cells["prep0"][k][0] / cells["prep0"][k][1], e01),
            "hd_interval": interval(history[k], cells["prep0"][k], e01, level),
        }
        for k, (prep0_job, x_history_job) in enumerate(jobs)
    ]
    uniform = all(ok for ok, _ in tests.values())
    if not uniform:
        hd_interval = [
            min([hd_interval[0], *(pair["hd_interval"][0] for pair in pairs)]),
            max([hd_interval[1], *(pair["hd_interval"][1] for pair in pairs)]),
        ]
    return {
        "counts": {arm: cells[arm] for arm in ARMS},
        "fractions": {"prep0": p, spe.STATE_PREP_HISTORY_ARM: x},
        "e01": e01,
        "readouts": readouts,
        "hd": history_dependent(x, p, e01),
        "hd_interval": hd_interval,
        "replicates": {
            "homogeneous": uniform,
            "p_values": {arm: tests[arm][1] for arm in ARMS},
            "pairs": pairs,
        },
    }


def split(controls: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    """The per-qubit split from read_control outputs, replicates of an arm in the order given."""
    spe.require(0.0 < alpha < 1.0, f"alpha {alpha} lies outside (0, 1)")
    spe.require(len({c["backend"] for c in controls}) == 1, "the controls span backends")
    spe.require(len({c["rep_delay_seconds"] for c in controls}) == 1, "the controls span repetition delays")
    by_arm: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    for control in controls:
        arms = set(control["counts"])
        spe.require(len(arms) == 1 and arms <= set(ARMS), f"{control['path']}: arms {sorted(arms)}")
        by_arm[next(iter(arms))].append(control)
    spe.require(
        len(by_arm["prep0"]) == len(by_arm[spe.STATE_PREP_HISTORY_ARM]) > 0,
        "the controls must pair each prep0 job with one x_history job",
    )
    qubits = sorted(set.intersection(*(set(c["counts"][arm]) for arm in ARMS for c in by_arm[arm])))
    spe.require(bool(qubits), "no qubit is read by every control")
    level = alpha / (4 * len(qubits))
    jobs = [
        (prep0["job_ids"], history["job_ids"])
        for prep0, history in zip(by_arm["prep0"], by_arm[spe.STATE_PREP_HISTORY_ARM], strict=True)
    ]
    items = [
        (
            {arm: [c["counts"][arm][qubit] for c in by_arm[arm]] for arm in ARMS},
            {arm: [c["readouts"][arm][qubit] for c in by_arm[arm]] for arm in ARMS},
            jobs,
            level,
            alpha / (2 * len(qubits)),
        )
        for qubit in qubits
    ]
    rows = parallel.ordered_map(qubit_split, items)
    out = {str(qubit): row for qubit, row in zip(qubits, rows, strict=True)}
    return {
        "schema": SCHEMA,
        "rule": {
            "alpha": alpha,
            "bound_count": 4 * len(qubits),
            "alpha_per_bound": level,
            "replicate_level": alpha / (2 * len(qubits)),
            "hd": "max(0, (x - p) / (1 - e01 - p)), e01 the largest execution prob_meas0_prep1",
        },
        "backend": controls[0]["backend"],
        "rep_delay_seconds": controls[0]["rep_delay_seconds"],
        "controls": {
            arm: [{k: c[k] for k in ("path", "record_sha256", "collect_sha256", "job_ids")} for c in by_arm[arm]]
            for arm in ARMS
        },
        "qubits": out,
    }


def self_test() -> None:
    level = 0.01 / 8
    low, high = bounds(100, 10000, 1, level)
    spe.require(low < 0.01 < high, f"bounds {low, high} miss the point 0.01")
    x, p = [500, 10000, 1], [100, 10000, 1]
    hd_low, hd_high = interval(x, p, 0.01, level)
    point = history_dependent(0.05, 0.01, 0.01)
    spe.require(hd_low < point < hd_high, f"hd interval {hd_low, hd_high} misses {point}")
    spe.require(homogeneous([[100, 10000, 1], [104, 10000, 1]], 0.01)[0], "equal replicates read heterogeneous")
    spe.require(not homogeneous([[100, 10000, 1], [400, 10000, 1]], 0.01)[0], "unequal replicates read homogeneous")
    spe.require(history_dependent(0.01, 0.02, 0.01) == 0.0, "a negative history difference must clamp to zero")
    print("state_prep_split self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--control", type=Path, action="append", default=[], help="collected control run directory")
    parser.add_argument("--alpha", type=float, default=spe.DEFAULT_ALPHA)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.out is None or not args.control:
        parser.error("--out and --control are required")
    result = split([spe.read_control(d.resolve(), ROOT) for d in args.control], args.alpha)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    widest = max(result["qubits"].items(), key=lambda item: item[1]["hd"])
    heterogeneous = sorted(int(q) for q, row in result["qubits"].items() if not row["replicates"]["homogeneous"])
    print(
        f"split over {len(result['qubits'])} qubits: largest hd {widest[1]['hd']:.4g} on q{widest[0]}, "
        f"heterogeneous replicates on {heterogeneous}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
