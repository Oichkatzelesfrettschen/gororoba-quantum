"""Inspect a proposed network case or normalized joint record without provider access.

The command reads bounded local byte snapshots. A matching raw digest binds
source identity; it does not prove a provider-to-normalized-count conversion.
Every report leaves execution and physical-claim admission false. Exit 0
means a report was produced, 1 means --require-review-ready found an unresolved
record, and 2 means the input, binding, or output path is invalid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import qd_network_records as records  # noqa: E402


def bounded_bytes(path: Path) -> bytes:
    """Read at most the record limit plus one byte; oversized inputs fail before parsing."""
    with path.open("rb") as stream:
        data = stream.read(records.MAX_JSON_BYTES + 1)
    if len(data) > records.MAX_JSON_BYTES:
        raise records.NetworkRecordError(f"{path.name}: input exceeds {records.MAX_JSON_BYTES} bytes")
    return data


def write_report(path: Path, report: dict[str, Any]) -> None:
    """Replace a derived report atomically after the complete record validates."""
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(encoded)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("record", type=Path, help="qd-network-case-v1 or qd-network-joint-v1 JSON")
    parser.add_argument("--case", type=Path, help="exact case bytes bound by a joint record")
    parser.add_argument("--raw-result", type=Path, help="exact raw source bytes; identity check only")
    parser.add_argument("--payload", type=Path, help="exact submitted payload bytes, when available")
    parser.add_argument("--out", type=Path, help="write the derived JSON report atomically")
    parser.add_argument(
        "--require-review-ready",
        action="store_true",
        help="exit 1 if declarations remain incomplete for review; this never approves execution",
    )
    args = parser.parse_args(argv)
    try:
        sources = [path for path in (args.record, args.case, args.raw_result, args.payload) if path is not None]
        if args.out is not None and args.out.resolve() in {path.resolve() for path in sources}:
            raise records.NetworkRecordError("the report path must differ from every input and bound source")
        data = bounded_bytes(args.record)
        record = records.decode_json(data)
        schema = record.get("schema")
        report: dict[str, Any] = {
            "schema": "qd-network-analysis-report-v1",
            "input_schema": schema,
            "input_sha256": hashlib.sha256(data).hexdigest(),
            "execution_admitted": False,
            "physical_claim_admitted": False,
        }
        if schema == records.CASE_SCHEMA:
            if any(path is not None for path in (args.case, args.raw_result, args.payload)):
                raise records.NetworkRecordError("--case, --raw-result and --payload apply only to a joint record")
            assessment = records.assess_case(record)
            report["assessment"] = assessment
        elif schema == records.JOINT_SCHEMA:
            assessment = records.analyze_joint(record)
            report["analysis"] = assessment
            report["bindings"] = records.verify_bindings(
                record,
                case_bytes=bounded_bytes(args.case) if args.case is not None else None,
                raw_result_bytes=bounded_bytes(args.raw_result) if args.raw_result is not None else None,
                payload_bytes=bounded_bytes(args.payload) if args.payload is not None else None,
            )
        else:
            raise records.NetworkRecordError("unsupported network record schema")
        if args.out is None:
            sys.stdout.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
        else:
            write_report(args.out, report)
        return int(args.require_review_ready and not assessment.get("review_ready", False))
    except (OSError, records.NetworkRecordError) as error:
        print(f"network record refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
