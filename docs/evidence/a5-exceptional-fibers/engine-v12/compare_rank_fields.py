"""Compare the rank fields of fiber-rank engine records, which must be byte-equal.

A record's rank fields are every field except `seconds` (timings), `echelon` (the backend flag) and, inside `export`,
`computed_seconds` and `reused` (which export files an earlier run left); the export file digests, chunking and adoption
fields stay in the comparison. With --across-engines the engine digest `engine_sha256_16` is excluded as well, for
records of different engine versions. Each record is serialized with sorted keys and hashed.

Usage: compare_rank_fields.py [--across-engines] RECORD RECORD [RECORD ...]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

TOP_VOLATILE = ("seconds", "echelon")
EXPORT_VOLATILE = ("computed_seconds", "reused")


def rank_fields(record: dict[str, Any], across_engines: bool = False) -> str:
    skip = (*TOP_VOLATILE, "engine_sha256_16") if across_engines else TOP_VOLATILE
    kept = {k: v for k, v in record.items() if k not in skip}
    if isinstance(kept.get("export"), dict):
        kept["export"] = {k: v for k, v in kept["export"].items() if k not in EXPORT_VOLATILE}
    return json.dumps(kept, sort_keys=True)


def main(argv: list[str]) -> int:
    across = "--across-engines" in argv
    paths = [a for a in argv if a != "--across-engines"]
    if len(paths) < 2:
        raise SystemExit(__doc__)
    fields = [rank_fields(json.loads(Path(p).read_text()), across) for p in paths]
    for p, f in zip(paths, fields, strict=True):
        print(f"{hashlib.sha256(f.encode()).hexdigest()[:16]}  {len(f)} bytes  {p}")
    equal = len(set(fields)) == 1
    print("rank fields byte-equal" if equal else "rank fields DIFFER")
    return 0 if equal else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
