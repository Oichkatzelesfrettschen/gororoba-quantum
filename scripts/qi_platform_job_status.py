#!/usr/bin/env python3
"""Provider status of the jobs of one submitted Quantum Inspire run directory, read before collection.

    "$QI_PYTHON" scripts/qi_platform_job_status.py status RUN_DIR

Reads GET /jobs/{id} for every job of RUN_DIR/submission.json through qi_platform.Client and exits

- 0 when no job reads "failed" (a job still queued or running is not a failure; collection waits for it);
- 3 when a job reads "failed": RUN_DIR/provider-failure.json then holds the job records and the first failed job's
  message, truncated to MESSAGE_LIMIT characters with whitespace runs collapsed, and stdout names that message;
- 1 when a status read fails.

GET /jobs/{id}/logs of a failed job can exceed the client's 60 s read timeout every time, while GET /jobs/{id}
answers within seconds with the failure message, so a series reads this status first and stops on a failed job
instead of entering qi_platform.py collect. The route changes no file of qi_platform.py and sends only GET requests.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

SCHEMA = "qi-provider-failure-v1"
FAILURE_FILE = "provider-failure.json"
MESSAGE_LIMIT = 300
EXIT_FAILED = 3


def failure_message(job: dict[str, Any]) -> str:
    """The job's failure message on one line, at most MESSAGE_LIMIT characters."""
    text = re.sub(r"\s+", " ", str(job.get("message") or "no message")).strip()
    return text[:MESSAGE_LIMIT]


def report(run: Path, read_job: Callable[[int], dict[str, Any]]) -> int:
    """Read every job of the run's receipt through read_job; write FAILURE_FILE when one failed."""
    record = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    jobs = [read_job(int(row["job"])) for row in record["jobs"]]
    failed = [job for job in jobs if job.get("status") == "failed"]
    if not failed:
        return 0
    message = failure_message(failed[0])
    body = {
        "schema": SCHEMA,
        "read_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "batch_job": record.get("batch_job"),
        "message": message,
        "jobs": jobs,
    }
    temporary = run / (FAILURE_FILE + ".tmp")
    temporary.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8")
    os.replace(temporary, run / FAILURE_FILE)
    print(f"failed: {message}")
    return EXIT_FAILED


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("status")
    p.add_argument("run", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import qi_platform

    try:
        client = qi_platform.Client()
        return report(args.run, lambda job: client.get(f"/jobs/{job}"))
    except (qi_platform.PlatformError, OSError, KeyError, ValueError) as error:
        print(f"the job status read failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
