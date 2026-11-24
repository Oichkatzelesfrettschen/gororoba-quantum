"""Offline stand-in for the Quantum Inspire submit and collect routes of the replicated Tuna-17 series.

    "$PYTHON" scripts/qi_replicated_series_fake.py submit RUN_DIR [--backend-type-id N] [--approval TEXT]
    "$PYTHON" scripts/qi_replicated_series_fake.py collect RUN_DIR [--poll S] [--timeout S]

qi_replicated_series_run.sh --dry-run drives these two commands where a real series drives qi_platform_leased.py
submit and qi_platform.py collect, so the control flow (copy, submit, collect, binding check, stage gate, restart)
runs without a provider. build_run writes the files of a retained run directory (submission-state.json,
submission.json of schema qi-submission-v2, results.json of schema qi-collection-v1 and raw/<file>.json) for one
replicate of the proposal. The shot lists are exact counts, with no random draw: the selector-zero frequencies
of a replicate are chosen so that its raw residual F_R2 - B_R1 + F_R1 - D_R2 equals residual_of(index, sigma,
effect), the alternating pattern +-a * sigma whose first twelve values have sample standard deviation sigma.

Environment: FAKE_LOG (file that receives one line per call), FAKE_SIGMA, FAKE_EFFECT, FAKE_FAIL_REP (submit exits
1 for that replicate), FAKE_COLLECT_FAIL_REP (collect exits 1 for that replicate), FAKE_BAD_READOUT_REP (that
replicate's readout circuit reads 0.5), FAKE_REFUSE (the first N submits answer a pause refusal),
FAKE_SKEW_REP, FAKE_SKEW_FILE and FAKE_SKEW_SECONDS (collecting that replicate writes the seconds to the file, which a
test's clock shim adds to the time the runner reads). No call reaches a network or reads a credential.

Every record this module writes is fabricated and says so: submission.json and results.json carry the field
"fabricated" (FABRICATION_MARK) that the real submit and collect routes never write, and the run directory holds an
empty file .fabricated. qi_replicated_response_analysis.py refuses such a directory unless it runs with
--allow-fabricated, and an armed series refuses one, so a dry run never enters a real analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_matched_response import SELECTORS  # noqa: E402
from qi_replicated_response import READOUT_ONE, READOUT_ZERO, WITNESS_A, WITNESS_B  # noqa: E402

FABRICATION_MARK = "qi-replicated-series-fake-v1"
BATCH_BASE = 800000
JOB_BASE = 1000000
AMPLITUDE = math.sqrt(11 / 12)
RUN_NAME = re.compile(r"rep-(\d{2})$")


def residual_of(index: int, sigma: float, effect: float) -> float:
    """Residual of replicate index: effect plus sigma times +-sqrt(11/12), so twelve values have SD sigma."""
    return effect + sigma * AMPLITUDE * (1 if index % 2 == 0 else -1)


def _histogram(read1: tuple[float, float], shots: int) -> dict[str, int]:
    """Exact joint counts of the two selector bits with the given marginal read-1 frequencies."""
    ones = [round(read1[0] * shots), round(read1[1] * shots)]
    both = round(ones[0] * ones[1] / shots)
    cells = {(1, 1): both, (1, 0): ones[0] - both, (0, 1): ones[1] - both, (0, 0): shots - ones[0] - ones[1] + both}
    out: dict[str, int] = {}
    for (first, second), count in cells.items():
        bits = ["0"] * 17
        bits[16 - SELECTORS[0]] = str(first)
        bits[16 - SELECTORS[1]] = str(second)
        out["".join(bits)] = count
    return out


def read1_of(file: str, residual: float, bad_readout: bool = False) -> tuple[float, float]:
    """Selector read-1 frequencies of a circuit; the witness-a region-2 zero frequency carries the residual."""
    if file == READOUT_ZERO:
        return (0.5, 0.5) if bad_readout else (0.0, 0.0)
    if file == READOUT_ONE:
        return (0.5, 0.5) if bad_readout else (1.0, 1.0)
    if file == WITNESS_A:
        zero = (1.0, 0.5 + residual)
    elif file == WITNESS_B:
        zero = (0.5, 0.0)
    else:
        raise ValueError(f"unknown circuit {file}")
    return (1 - zero[0], 1 - zero[1])


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=1) + "\n", encoding="utf-8")


def submit_run(run: Path, approval: str, index: int) -> None:
    """Write the checkpoint and the qi-submission-v2 receipt of one replicate."""
    cases = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    (run / ".fabricated").write_text("", encoding="utf-8")
    _write(run / "submission-state.json", {"schema": "qi-submission-state-v1", "phase": "creating"})
    _write(
        run / "submission.json",
        {
            "schema": "qi-submission-v2",
            "fabricated": FABRICATION_MARK,
            "state": "enqueued",
            "created_utc": "2026-01-01T00:00:00+00:00",
            "approval": approval,
            "backend": cases["backend"],
            "backend_type_id": cases["backend_type_id"],
            "cases_sha256": hashlib.sha256((run / "cases.json").read_bytes()).hexdigest(),
            "batch_job": BATCH_BASE + index,
            "shots": cases["shots"],
            "jobs": [
                {"file": row["file"], "job": JOB_BASE + 10 * index + k, "sha256": row["sha256"]}
                for k, row in enumerate(cases["circuits"])
            ],
        },
    )


def collect_run(run: Path, index: int, sigma: float, effect: float, bad_readout: bool = False) -> None:
    """Write results.json and raw/ of one submitted replicate."""
    cases = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    receipt = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    residual = residual_of(index, sigma, effect)
    (run / "raw").mkdir(exist_ok=True)
    rows = []
    for row, sent in zip(cases["circuits"], receipt["jobs"], strict=True):
        file = row["file"]
        histogram = _histogram(read1_of(file, residual, bad_readout), cases["shots"])
        shots = [string for string, count in sorted(histogram.items()) for _ in range(count)]
        _write(run / "raw" / f"{file}.json", shots)
        job = {
            "id": sent["job"],
            "created_on": "2026-01-01T00:00:00Z",
            "status": "completed",
            "batch_job_id": receipt["batch_job"],
            "number_of_shots": cases["shots"],
        }
        result = {
            "job_id": sent["job"],
            "shots_requested": cases["shots"],
            "shots_done": len(shots),
            "results": dict(Counter(shots)),
        }
        rows.append({"file": file, "job": job, "results": [result]})
    _write(
        run / "results.json",
        {
            "schema": "qi-collection-v1",
            "fabricated": FABRICATION_MARK,
            "collected_utc": "2026-01-01T00:00:00+00:00",
            "jobs": rows,
            "transactions": [],
        },
    )


def _log(line: str) -> None:
    path = os.environ.get("FAKE_LOG")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("submit")
    p.add_argument("run", type=Path)
    p.add_argument("--backend-type-id", type=int)
    p.add_argument("--approval", default="dry-run")
    p = sub.add_parser("collect")
    p.add_argument("run", type=Path)
    p.add_argument("--poll", type=float, default=0)
    p.add_argument("--timeout", type=float, default=0)
    args = parser.parse_args()
    match = RUN_NAME.search(args.run.name)
    if match is None:
        raise SystemExit(f"{args.run.name}: not a replicate run directory")
    index = int(match.group(1))
    name = f"rep-{index:02d}"
    env = os.environ
    if args.command == "submit":
        _log(f"submit {name}")
        refused = 0
        if env.get("FAKE_LOG") and Path(env["FAKE_LOG"]).exists():
            refused = sum(1 for line in Path(env["FAKE_LOG"]).read_text().splitlines() if line.startswith("refused"))
        if refused < int(env.get("FAKE_REFUSE", "0")):
            _log(f"refused {name}")
            raise SystemExit("the account's last hardware job finished less than 120 s ago; wait 5 more seconds")
        if env.get("FAKE_FAIL_REP") == name:
            raise SystemExit("Quantum backend error")
        submit_run(args.run, args.approval, index)
        print(f"batch {BATCH_BASE + index}")
        return 0
    _log(f"collect {name}")
    if env.get("FAKE_COLLECT_FAIL_REP") == name:
        raise SystemExit("collection timed out")
    collect_run(
        args.run,
        index,
        float(env.get("FAKE_SIGMA", "0.01")),
        float(env.get("FAKE_EFFECT", "0")),
        env.get("FAKE_BAD_READOUT_REP") == name,
    )
    if env.get("FAKE_SKEW_REP") == name and env.get("FAKE_SKEW_FILE"):
        Path(env["FAKE_SKEW_FILE"]).write_text(env.get("FAKE_SKEW_SECONDS", "0") + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
