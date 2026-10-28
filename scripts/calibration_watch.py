"""One read of a backend's published calibration against a baseline, for scripts/wait_calibration.sh.

The read is BackendProperties fetched with refresh=True: last_update_date is the stamp live_run.py records as a
run's calibration, and t1/t2 are the reported values a run normalizes against. The first poll writes the baseline
file and reports no change. A later poll reports a change when the stamp names another instant than the baseline's
(last_update_date carries the reading host's UTC offset, so a baseline read elsewhere compares by instant) and, with
--qubits, when the reported T1 and the reported T2 each differ on at least --min-moved of those qubits (default:
half of them, rounded up). Kingston republishes its stamp every 15 to 60 minutes while T1 and T2 refresh together
once a day, so a case that waits on the daily refresh names its qubits; a stamp change alone serves a case that
needs any fresh calibration.

Usage (from the repository root, GOROROBA_IBM_ACCOUNT selecting the account):
    "$PYTHON" scripts/calibration_watch.py BACKEND --baseline FILE [--qubits 0,1,5-9] [--min-moved N]
Exit 0 changed, 1 unchanged or baseline written, 2 usage, 3 the service read failed.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import ibm_account  # noqa: E402
from live_run import same_calibration_instant  # noqa: E402

CHANGED, UNCHANGED, READ_FAILED = 0, 1, 3


def qubit_list(spec: str) -> list[int]:
    """Qubits from a comma list of indices and inclusive ranges, 0,1,5-9."""
    out: set[int] = set()
    for part in spec.split(","):
        low, _, high = part.strip().partition("-")
        out.update(range(int(low), int(high or low) + 1))
    return sorted(out)


def reading(props: Any, qubits: list[int]) -> dict[str, Any]:
    """The stamp and the reported T1 and T2 in microseconds of each named qubit."""
    return {
        "stamp": props.last_update_date.isoformat(),
        "t1_us": {str(q): props.t1(q) * 1e6 for q in qubits},
        "t2_us": {str(q): props.t2(q) * 1e6 for q in qubits},
    }


def moved(baseline: dict[str, Any], now: dict[str, Any], key: str) -> int:
    """Qubits whose reported value under KEY differs from the baseline's by more than 1e-6 us."""
    return sum(1 for q, value in now[key].items() if abs(value - baseline[key].get(q, math.inf)) > 1e-6)


def decide(baseline: dict[str, Any], now: dict[str, Any], min_moved: int) -> tuple[bool, str]:
    """Whether NOW is a new calibration in the sense the watch asks for, and a one-line summary."""
    t1, t2, n = moved(baseline, now, "t1_us"), moved(baseline, now, "t2_us"), len(now["t1_us"])
    new_stamp = not same_calibration_instant(now["stamp"], baseline["stamp"])
    changed = new_stamp and (n == 0 or (t1 >= min_moved and t2 >= min_moved))
    return changed, f"stamp={now['stamp']} t1_moved={t1} t2_moved={t2} n={n} min_moved={min_moved}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("backend")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--qubits", type=qubit_list, default=[])
    parser.add_argument("--min-moved", type=int)
    args = parser.parse_args(argv)
    min_moved = args.min_moved if args.min_moved is not None else math.ceil(len(args.qubits) / 2)
    try:
        props = ibm_account.open_service().backend(args.backend).properties(refresh=True)
        now = reading(props, args.qubits)
    except Exception as exc:  # noqa: BLE001 - any service failure is one failed poll
        print(f"read failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return READ_FAILED
    if not args.baseline.exists():
        args.baseline.write_text(json.dumps(now, indent=1, sort_keys=True) + "\n")
        print(f"baseline stamp={now['stamp']} n={len(args.qubits)}")
        return UNCHANGED
    changed, summary = decide(json.loads(args.baseline.read_text()), now, min_moved)
    print(("changed " if changed else "unchanged ") + summary)
    return CHANGED if changed else UNCHANGED


if __name__ == "__main__":
    sys.exit(main())
