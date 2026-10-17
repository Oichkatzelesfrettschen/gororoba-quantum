"""Measured replica score covariance against a run's declared covariance bound.

A plan that declares ``--replica-variance-bound V`` asserts, for every
contract and PUB with replicated members, that the per-replica scores of one
shot have variance at most V and are independent across replicas
(n21_exact_planning). The collector's Cantelli or Chebyshev radius rests on
that bound, so this script tests it on the shot-ordered registers a
collection retains under ``raw/<job_id>/pub_NN.json``.

For each declared bound it scores every shot of every replica register named
in the record's execution manifest and compares the variance of the
replica-average score, the only projection of the matrix the optimizer's
radius reads (weights 1/R), with the declared projection. The estimate
carries a Hoeffding allowance at tail ``TAIL``: the mean square and the mean
of a score in [-1, 1] each sit within e = 2 sqrt(ln(6/tail) / (2n)) of their
expectations, so the variance estimate sits within 3e + e^2. The bound fails
when the estimate exceeds the declared projection by more than that
allowance; the analysis then belongs to the arbitrary-dependence Hoeffding
radius. The full sample covariance matrix is reported beside it.

Usage:
    "$PYTHON" scripts/n21_replica_covariance.py --run-dir results/live/RUN
    "$PYTHON" scripts/n21_replica_covariance.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

TAIL = 1e-3


def allowance(shots: int, entries: int, tail: float = TAIL) -> float:
    """Simultaneous deviation allowance of entries sample (co)variances of [-1, 1] scores."""
    spread = 2 * math.sqrt(math.log(6 * entries / tail) / (2 * shots))
    return spread + 2 * spread + spread**2


def score_matrix(bitstrings: list[list[str]], values: tuple[float, ...]) -> np.ndarray:
    """(shots, replicas) scores from each replica register's shot-ordered bitstrings."""
    columns = [np.asarray([values[int(bits, 2)] for bits in register], dtype=float) for register in bitstrings]
    if len({column.size for column in columns}) != 1:
        raise ValueError("replica registers hold different shot counts")
    return np.stack(columns, axis=1)


def compare(scores: np.ndarray, declared: np.ndarray) -> dict[str, Any]:
    """The replica-average score variance, the projection the optimizer uses, against the declared one."""
    shots, replicas = scores.shape
    estimate = np.atleast_2d(np.cov(scores, rowvar=False, bias=True))
    weights = np.full(replicas, 1.0 / replicas)
    realized = float(np.var(scores @ weights))
    bound = float(weights @ declared @ weights)
    tolerance = allowance(shots, 1)
    return {
        "shots": shots,
        "replicas": replicas,
        "covariance_estimate": estimate.round(6).tolist(),
        "declared": declared.tolist(),
        "average_variance": realized,
        "declared_average_variance": bound,
        "allowance": tolerance,
        "holds": realized <= bound + tolerance,
    }


def check_run(run_dir: Path) -> list[dict[str, Any]]:
    record = json.loads((run_dir / "record.json").read_text())
    bounds = record.get("covariance_bounds", [])
    if not bounds:
        raise SystemExit(f"{run_dir}: the record declares no covariance bound")
    registers: dict[str, list[str]] = {}
    for pub in record["execution_pubs"]:
        for component in pub["components"]:
            registers[component["member"]] = [
                f"{component['register_prefix']}{name}" for names in component["registers_by_replica"] for name in names
            ]
    by_pub: dict[str, dict[str, Any]] = {}
    for path in sorted(run_dir.glob("raw/*/pub_*.json")):
        data = json.loads(path.read_text())
        by_pub[data["pub_name"]] = data["registers"]
    values = {
        term["member"]: tuple(term["values"])
        for contract in record["observable_contracts"]
        for term in contract["terms"]
    }
    rows = []
    for bound in bounds:
        members = []
        for label in bound["labels"]:
            member = label.rsplit("/r", 1)[0]
            if member not in members:
                members.append(member)
        if len(members) != 1:
            raise SystemExit(f"{bound['pub_name']}: one replicated member per declared bound is supported")
        raw = by_pub.get(bound["pub_name"])
        if raw is None:
            raise SystemExit(f"{run_dir}: no raw registers for {bound['pub_name']}")
        names = registers[members[0]]
        scores = score_matrix([raw[name]["bitstrings"] for name in names], values[members[0]])
        result = compare(scores, np.asarray(bound["matrix"], dtype=float))
        rows.append({"observable": bound["observable_name"], "pub": bound["pub_name"], **result})
    return rows


def self_test() -> None:
    generator = np.random.default_rng(20261017)
    values = (0.0, 1.0, 0.0, -1.0)
    law = np.array([0.28, 0.25, 0.22, 0.25])
    shots, replicas = 65536, 3
    outcomes = generator.choice(4, size=(shots, replicas), p=law)
    independent = [[format(int(o), "02b") for o in outcomes[:, r]] for r in range(replicas)]
    declared = np.diag([0.55] * replicas)
    accepted = compare(score_matrix(independent, values), declared)
    if not accepted["holds"]:
        raise AssertionError(f"independent replicas rejected: {accepted}")
    copied = outcomes.copy()
    shared = generator.random(shots) < 0.8
    copied[shared, 1] = copied[shared, 0]
    copied[shared, 2] = copied[shared, 0]
    correlated = [[format(int(o), "02b") for o in copied[:, r]] for r in range(replicas)]
    rejected = compare(score_matrix(correlated, values), declared)
    if rejected["holds"]:
        raise AssertionError("replicas sharing 0.8 of their shots passed the independence bound")
    tight = compare(score_matrix(independent, values), np.diag([0.3] * replicas))
    if tight["holds"]:
        raise AssertionError("a variance bound below the realized variance passed")
    print(
        f"n21 replica covariance: independent replicas accepted (allowance {accepted['allowance']:.4f}); "
        "shared shots and an undersized variance bound rejected"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run-dir", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    rows = check_run(args.run_dir)
    print(json.dumps(rows, indent=1))
    return 0 if all(row["holds"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
