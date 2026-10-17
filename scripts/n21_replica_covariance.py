"""Replay of a collected run's replica covariance falsifier from its retained raw registers.

A plan that declares ``--replica-variance-bound V`` asserts, for every
contract and PUB with replicated members, that the replica scores of one shot
have variance at most V and are independent across replicas
(n21_exact_planning). The collector tests that assertion before it applies
the bound: qpu_planning.measured_family runs
n21_exact_planning.covariance_falsifier on the shot-ordered registers
raw/<job_id>/pub_NN.json retains and records the branch it took under
collect.json's ``family_analysis.replica_covariance``.

``--run-dir`` reruns the same falsifier from the run directory alone: it reads
record.json and the raw files (each checked against its index digest),
recomputes every bound's statistic and threshold, and, when collect.json
exists, requires the collector's verdict, branch and per-bound statistics to
match. It prints the replayed rows and exits 1 on a disagreement.

Usage:
    "$PYTHON" scripts/n21_replica_covariance.py --run-dir results/live/RUN
    "$PYTHON" scripts/n21_replica_covariance.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import n21_exact_planning  # noqa: E402

COMPARED = ("statistic", "declared_projection", "allowance", "threshold")


def replay(run_dir: Path) -> dict[str, Any]:
    record = json.loads((run_dir / "record.json").read_text())
    bounds = record.get("covariance_bounds", [])
    if not bounds:
        raise SystemExit(f"{run_dir}: the record declares no covariance bound")
    registers = n21_exact_planning.retained_registers(run_dir, {bound["pub_name"] for bound in bounds})
    return n21_exact_planning.covariance_falsifier(record, registers)


def disagreements(replayed: dict[str, Any], collected: dict[str, Any]) -> list[str]:
    """Differences between the replayed falsifier and the collector's recorded one."""
    problems = []
    branch = "declared_covariance" if replayed["holds"] else "hoeffding_fallback"
    if collected.get("holds") != replayed["holds"] or collected.get("branch") != branch:
        problems.append(f"verdict: collected {collected.get('holds')}/{collected.get('branch')}, replayed {branch}")
    rows = collected.get("bounds", [])
    if len(rows) != len(replayed["bounds"]):
        return [*problems, "the collected and replayed bound lists differ in length"]
    for mine, theirs in zip(replayed["bounds"], rows, strict=True):
        label = f"{mine['observable']}/{mine['pub']}"
        if (mine["observable"], mine["pub"], mine["holds"]) != (theirs["observable"], theirs["pub"], theirs["holds"]):
            problems.append(f"{label}: identity or verdict differs")
            continue
        for key in COMPARED:
            if key in mine and not math.isclose(mine[key], theirs.get(key, math.nan), rel_tol=1e-12, abs_tol=1e-15):
                problems.append(f"{label} {key}: collected {theirs.get(key)}, replayed {mine[key]}")
    return problems


def check_run(run_dir: Path) -> tuple[dict[str, Any], list[str]]:
    replayed = replay(run_dir)
    collect_path = run_dir / "collect.json"
    if not collect_path.exists():
        return replayed, []
    collected = json.loads(collect_path.read_text())[0].get("family_analysis", {}).get("replica_covariance")
    if collected is None:
        return replayed, ["collect.json carries no replica_covariance analysis"]
    return replayed, disagreements(replayed, collected)


# ---------------------------------------------------------------- self-test


def _bits(outcomes: np.ndarray, width: int) -> list[str]:
    return [format(int(value), f"0{width}b") for value in outcomes]


def _fixture_run(directory: Path, outcomes: np.ndarray) -> dict[str, Any]:
    """A two-replica single-PUB run whose replica r1 splits its two bits over two registers."""
    signed = [0.0, 1.0, 0.0, -1.0]
    record = {
        "observable_contracts": [
            {"name": "contrast", "terms": [{"member": "m", "values": signed, "sign": 1}], "minimum_effect": 0.0}
        ],
        "execution_pubs": [
            {
                "name": "pub_a",
                "components": [
                    {"member": "m", "registers_by_replica": [["g0_r0_phase"], ["g0_r1_low", "g0_r1_high"]]},
                ],
            }
        ],
        "covariance_bounds": [
            {
                "observable_name": "contrast",
                "pub_name": "pub_a",
                "labels": ["m/r0", "m/r1"],
                "matrix": [[0.55, 0.0], [0.0, 0.55]],
                "assumption": "fixture",
            }
        ],
    }
    replica1 = _bits(outcomes[:, 1], 2)
    registers = {
        "g0_r0_phase": _bits(outcomes[:, 0], 2),
        # join_data reads registers right to left: the later register holds the high bit.
        "g0_r1_low": [bits[1] for bits in replica1],
        "g0_r1_high": [bits[0] for bits in replica1],
    }
    raw = directory / "raw" / "job0"
    raw.mkdir(parents=True)
    payload = {
        "pub_index": 0,
        "pub_name": "pub_a",
        "registers": {
            name: {"bitstrings": bits, "num_bits": len(bits[0]), "num_shots": len(bits)}
            for name, bits in registers.items()
        },
    }
    text = json.dumps(payload, indent=1, sort_keys=True) + "\n"
    (raw / "pub_00.json").write_text(text)
    index = {"job_id": "job0", "files": {"pub_00.json": hashlib.sha256(text.encode()).hexdigest()}}
    (raw / "index.json").write_text(json.dumps(index, indent=1, sort_keys=True) + "\n")
    (directory / "record.json").write_text(json.dumps(record))
    return record


def _write_collected(run: Path, collected: dict[str, Any]) -> None:
    (run / "collect.json").write_text(json.dumps([{"family_analysis": {"replica_covariance": collected}}]))


def self_test() -> None:
    generator = np.random.default_rng(20261017)
    law = np.array([0.28, 0.25, 0.22, 0.25])
    shots = 65536
    independent = generator.choice(4, size=(shots, 2), p=law)
    correlated = independent.copy()
    shared = generator.random(shots) < 0.8
    correlated[shared, 1] = correlated[shared, 0]
    verdicts = {}
    with tempfile.TemporaryDirectory() as scratch:
        for label, outcomes in (("independent", independent), ("correlated", correlated)):
            run = Path(scratch) / label
            run.mkdir()
            record = _fixture_run(run, outcomes)
            replayed, problems = check_run(run)
            if problems:
                raise AssertionError(f"{label}: replay without collect.json reported {problems}")
            verdicts[label] = replayed
            marginals = {"m": [np.bincount(outcomes[:, k], minlength=4) / shots for k in range(2)]}
            registers = n21_exact_planning.retained_registers(run, {"pub_a"})
            joined = n21_exact_planning.covariance_falsifier(record, registers, marginals)
            if joined["holds"] != replayed["holds"] or "differ from the collected marginal" in joined["reason"]:
                raise AssertionError(f"{label}: register join order disagrees with the replica marginals: {joined}")
            branch = "declared_covariance" if replayed["holds"] else "hoeffding_fallback"
            collected = copy.deepcopy(replayed) | {"branch": branch}
            _write_collected(run, collected)
            if check_run(run)[1]:
                raise AssertionError(f"{label}: replay disagrees with an identical collected verdict")
            collected["bounds"][0]["statistic"] += 1e-3
            _write_collected(run, collected)
            if not check_run(run)[1]:
                raise AssertionError(f"{label}: replay accepted an altered collected statistic")
        if not verdicts["independent"]["holds"]:
            raise AssertionError(f"independent replicas rejected: {verdicts['independent']}")
        if verdicts["correlated"]["holds"]:
            raise AssertionError("replicas sharing 0.8 of their shots passed the declared bound")
        pub = Path(scratch) / "independent" / "raw" / "job0" / "pub_00.json"
        pub.write_text(pub.read_text().replace('"pub_a"', '"pub_b"', 1))
        try:
            replay(Path(scratch) / "independent")
        except ValueError:
            pass
        else:
            raise AssertionError("a raw PUB file that differs from its index digest was read")
    row = verdicts["independent"]["bounds"][0]
    print(
        f"n21 replica covariance: independent replicas pass (statistic {row['statistic']:.4f} <= threshold "
        f"{row['threshold']:.4f}); shared shots fail; the replay matches an identical collected verdict, "
        "rejects an altered one and refuses a raw file off its index digest"
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
    replayed, problems = check_run(args.run_dir)
    print(json.dumps(replayed, indent=1))
    for problem in problems:
        print(f"disagreement: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
