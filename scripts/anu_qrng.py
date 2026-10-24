"""Quantum random draws from the ANU QRNG, retained as evidence for the seeds a case takes.

The ANU QRNG measures vacuum fluctuations of the electromagnetic field
(Symul, Assad and Lam, Appl. Phys. Lett. 98, 231103 (2011); Haw et al.,
Phys. Rev. Applied 3, 054004 (2015)). Two services answer {"success", "type",
"length", "data"} for length 1 to 1024 and type uint8 or uint16:

- aqn, the default: https://api.quantumnumbers.anu.edu.au on AWS, with the
  account's key in the x-api-key header (100 requests per calendar month and
  1 per second on the free tier); it answers length as a string. The key lives
  in the file ANU_QRNG_KEY_FILE names (default ~/.config/anu-qrng/api-key,
  mode 600) and never enters a record, a URL or a log.
- legacy: the keyless https://qrng.anu.edu.au/API/jsonI.php, one request per
  minute (a second answers HTTP 500 with the limit in its body), which ANU
  will scale back and retire.

A draw is used once: a case cites the record and the index of every value it
took, so no value seeds two cases.

Subcommands:

- draw --out DIR [--source aqn|legacy] [--length N] [--type uint16] (network)
  makes one request and
  writes DIR/draw-<UTC>.json: the request URL, the UTC time, the raw response
  bytes as text, their sha256 and the parsed values.
- check DIR (offline) requires every record's sha256 to match its raw bytes,
  the parsed values to equal the raw JSON's data, the success flag to be
  true and every value to lie in its type's range.
- --self-test requires a corrupted value, an edited raw byte, a false success
  flag and an out-of-range value to be rejected, and a string length to be
  admitted.

Usage: "$PYTHON" scripts/anu_qrng.py (draw --out DIR | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

SCHEMA = "anu-qrng-draw-v1"
ENDPOINTS = {"aqn": "https://api.quantumnumbers.anu.edu.au", "legacy": "https://qrng.anu.edu.au/API/jsonI.php"}
RANGES = {"uint8": 255, "uint16": 65535}
MAX_LENGTH = 1024


class DrawError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuses every redirect, so an API key header reaches the service's own origin alone."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def record_from(url: str, utc: str, raw: str) -> dict[str, Any]:
    answer = json.loads(raw)
    record = {
        "schema": SCHEMA,
        "source": url,
        "retrieved_utc": utc,
        "raw": raw,
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "type": answer.get("type"),
        "values": answer.get("data"),
    }
    admit(record)
    return record


def admit(record: dict[str, Any]) -> None:
    """A record whose bytes, parse, success flag and value range all hold."""
    if record.get("schema") != SCHEMA:
        raise DrawError(f"schema {record.get('schema')!r}")
    raw = record["raw"]
    if hashlib.sha256(raw.encode()).hexdigest() != record["raw_sha256"]:
        raise DrawError("raw bytes differ from their sha256")
    answer = json.loads(raw)
    if answer.get("success") is not True:
        raise DrawError("the service reported no success")
    if answer.get("data") != record["values"] or answer.get("type") != record["type"]:
        raise DrawError("parsed values differ from the raw response")
    top = RANGES.get(record["type"])
    if top is None:
        raise DrawError(f"type {record['type']!r}")
    values = record["values"]
    if not isinstance(values, list) or str(len(values)) != str(answer.get("length")):
        raise DrawError("value count differs from the answered length")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= top:
            raise DrawError(f"value {value!r} outside {record['type']}")


def api_key() -> str:
    path = Path(os.environ.get("ANU_QRNG_KEY_FILE", Path.home() / ".config/anu-qrng/api-key"))
    if not path.is_file() or path.stat().st_mode & 0o077:
        raise DrawError(f"{path} is missing or readable by group or others")
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise DrawError(f"{path} is empty")
    return key


def draw(out: Path, length: int, kind: str, source: str) -> Path:
    if not 1 <= length <= MAX_LENGTH or kind not in RANGES or source not in ENDPOINTS:
        raise DrawError(f"length {length}, type {kind!r} or source {source!r} outside the services' domain")
    url = f"{ENDPOINTS[source]}?length={length}&type={kind}"
    headers = {"x-api-key": api_key()} if source == "aqn" else {}
    utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    with OPENER.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
        raw = response.read().decode()
    record = record_from(url, utc, raw)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"draw-{utc}.json"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(record, indent=1) + "\n")
    return path


def check(directory: Path) -> int:
    paths = sorted(directory.glob("draw-*.json"))
    if not paths:
        raise DrawError(f"{directory} holds no draw")
    for path in paths:
        try:
            admit(json.loads(path.read_text(encoding="utf-8")))
        except DrawError as error:
            raise DrawError(f"{path.name}: {error}") from None
    return len(paths)


def self_test() -> int:
    raw = json.dumps({"type": "uint16", "length": 3, "data": [0, 1, 65535], "success": True})
    good = record_from(ENDPOINTS["legacy"], "2026-01-01T000000Z", raw)
    keyed = json.dumps({"success": True, "type": "uint16", "length": "3", "data": [0, 1, 65535]})
    record_from(ENDPOINTS["aqn"], "2026-01-01T000000Z", keyed)
    bad_raw = raw.replace("65535", "65534")
    mutations = [
        ("value", lambda r: r["values"].__setitem__(0, 7)),
        ("raw byte", lambda r: r.__setitem__("raw", bad_raw)),
        ("success", lambda r: r.update(raw=raw.replace("true", "false"))),
        ("range", lambda r: r.update(type="uint8")),
    ]
    for name, mutate in mutations:
        record = copy.deepcopy(good)
        mutate(record)
        if name in ("success", "raw byte"):
            record["raw_sha256"] = hashlib.sha256(record["raw"].encode()).hexdigest()
        try:
            admit(record)
        except DrawError:
            continue
        raise SystemExit(f"self-test: the {name} mutation was admitted")
    print(f"anu_qrng self-test: {len(mutations)} mutations rejected, a string length admitted")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("draw")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--length", type=int, default=MAX_LENGTH)
    p.add_argument("--type", dest="kind", default="uint16", choices=sorted(RANGES))
    p.add_argument("--source", default="aqn", choices=sorted(ENDPOINTS))
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.command == "draw":
            print(draw(args.out, args.length, args.kind, args.source))
            return 0
        if args.command == "check":
            print(f"{args.directory}: {check(args.directory)} draws admitted")
            return 0
    except DrawError as error:
        raise SystemExit(str(error)) from None
    parser.error("choose draw, check or --self-test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
