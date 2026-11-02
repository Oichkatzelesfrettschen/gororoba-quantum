"""Validate one fiber_rank stdout file: one JSON record bound to the expected engine, header, d, N and rank.

Usage: gate_record.py OUT ENGINE HEADER D N EXPECTED. Exits 0 and prints the record when every field matches;
EXPECTED "any" checks the binding fields and leaves r_N to the caller.
"""

import hashlib
import json
import sys


def sha16(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def main() -> int:
    out, engine, header, d, n, expected = sys.argv[1:7]
    lines = [ln for ln in open(out).read().splitlines() if ln.strip()]
    if len(lines) != 1:
        print(f"{header} d={d} N={n}: {len(lines)} records, expected 1", file=sys.stderr)
        return 1
    try:
        rec = json.loads(lines[0])
    except json.JSONDecodeError as e:
        print(f"{header} d={d} N={n}: malformed record ({e})", file=sys.stderr)
        return 1
    want: dict[str, object] = {
        "engine_sha256_16": sha16(engine),
        "header_sha256_16": sha16(header),
        "d": int(d),
        "N": int(n),
    }
    if expected != "any":
        want["r_N"] = int(expected)
    bad = {k: (rec.get(k), v) for k, v in want.items() if rec.get(k) != v}
    if bad:
        print(f"{header} d={d} N={n}: mismatch (got, want) {bad}", file=sys.stderr)
        return 1
    print(lines[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
