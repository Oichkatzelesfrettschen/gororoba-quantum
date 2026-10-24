"""Quantum random draws from the Cisco Outshift QRNG, retained as evidence for the seeds a case takes.

POST https://api.qrng.outshift.com/api/v1/random_numbers takes a JSON body
{"encoding", "format", "bits_per_block", "number_of_blocks"} with bits_per_block
1 to 10000 and number_of_blocks 1 to 1000, and authenticates by the
x-id-api-key header; the free tier grants 100000 bits a month. With encoding
raw and format all it answers {"encoding": "raw", "random_numbers": [{"binary",
"octal", "decimal", "hexadecimal"}, ...]}, one entry per block. The key lives
in the file OUTSHIFT_QRNG_KEY_FILE names (default
~/.config/outshift-qrng/api-key, mode 600) and never enters a record, a URL or
a log; the request refuses redirects, so the key reaches the endpoint's
origin alone.

A draw is used once: a case cites the record and the index of every value it
took, so no value seeds two cases.

Subcommands:

- draw --out DIR [--bits N] [--blocks N] (network) makes one request and
  writes DIR/draw-<UTC>.json: the endpoint, the request body, the UTC time,
  the raw response bytes as text, their sha256 and the parsed values.
- check DIR (offline) requires every record's sha256 to match its raw bytes,
  every block's four representations to name one integer below 2**bits, and
  the parsed values and block count to equal the raw response and the request.
- --self-test requires a disagreeing representation, an over-wide block, an
  edited raw byte, a short response and an edited value to be rejected.

Usage: "$PYTHON" scripts/outshift_qrng.py (draw --out DIR | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import datetime
import functools
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

from anu_qrng import OPENER

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel  # noqa: E402

SCHEMA = "outshift-qrng-draw-v1"
ENDPOINT = "https://api.qrng.outshift.com/api/v1/random_numbers"
MAX_BITS = 10000
MAX_BLOCKS = 1000
# 16-bit blocks match the uint16 values of the ANU draws; 256 of them spend 4096 of the monthly 100000 bits.
DEFAULT_BITS = 16
DEFAULT_BLOCKS = 256
BASES = {"binary": 2, "octal": 8, "decimal": 10, "hexadecimal": 16}


class DrawError(ValueError):
    pass


def request_body(bits: int, blocks: int) -> dict[str, Any]:
    if not 1 <= bits <= MAX_BITS or not 1 <= blocks <= MAX_BLOCKS:
        raise DrawError(f"bits {bits} or blocks {blocks} outside the service's domain")
    return {"encoding": "raw", "format": "all", "bits_per_block": bits, "number_of_blocks": blocks}


def block_value(block: dict[str, Any], bits: int) -> int:
    """The one integer every representation of a block names, below 2**bits."""
    if not isinstance(block, dict) or set(block) != set(BASES):
        raise DrawError(f"block {block!r} lacks the four representations")
    values = set()
    for name, base in BASES.items():
        text = block[name]
        if not isinstance(text, str) or not text:
            raise DrawError(f"block {name} {text!r} is not a numeral")
        values.add(int(text, base))
    if len(values) != 1:
        raise DrawError(f"block representations disagree: {block}")
    value = values.pop()
    if not 0 <= value < 2**bits or len(block["binary"]) > bits:
        raise DrawError(f"block {block['binary']} wider than {bits} bits")
    return value


def block_values(blocks: list[Any], bits: int) -> list[int]:
    """Each block's value in response order, through the order-preserving pool."""
    return parallel.ordered_map(functools.partial(block_value, bits=bits), blocks)


def record_from(utc: str, body: dict[str, Any], raw: str) -> dict[str, Any]:
    answer = json.loads(raw)
    record = {
        "schema": SCHEMA,
        "source": ENDPOINT,
        "request": body,
        "retrieved_utc": utc,
        "raw": raw,
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "bits": body["bits_per_block"],
        "values": block_values(answer.get("random_numbers", []), body["bits_per_block"]),
    }
    admit(record)
    return record


def admit(record: dict[str, Any]) -> None:
    """A record whose bytes, representations, widths and block count all hold."""
    if record.get("schema") != SCHEMA:
        raise DrawError(f"schema {record.get('schema')!r}")
    raw = record["raw"]
    if hashlib.sha256(raw.encode()).hexdigest() != record["raw_sha256"]:
        raise DrawError("raw bytes differ from their sha256")
    body = record["request"]
    if body != request_body(body.get("bits_per_block", 0), body.get("number_of_blocks", 0)):
        raise DrawError(f"request {body!r} is not a raw, all-format request")
    if record["bits"] != body["bits_per_block"]:
        raise DrawError("record width differs from the requested width")
    answer = json.loads(raw)
    if answer.get("encoding") != "raw" or not isinstance(answer.get("random_numbers"), list):
        raise DrawError("the response carries no raw random_numbers list")
    blocks = answer["random_numbers"]
    if len(blocks) != body["number_of_blocks"]:
        raise DrawError(f"{len(blocks)} blocks answered, {body['number_of_blocks']} requested")
    if block_values(blocks, record["bits"]) != record["values"]:
        raise DrawError("parsed values differ from the raw response")


def api_key() -> str:
    path = Path(os.environ.get("OUTSHIFT_QRNG_KEY_FILE", Path.home() / ".config/outshift-qrng/api-key"))
    if not path.is_file() or path.stat().st_mode & 0o077:
        raise DrawError(f"{path} is missing or readable by group or others")
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise DrawError(f"{path} is empty")
    return key


def draw(out: Path, bits: int, blocks: int) -> Path:
    body = request_body(bits, blocks)
    headers = {"Content-Type": "application/json", "x-id-api-key": api_key()}
    utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers=headers, method="POST")
    with OPENER.open(request, timeout=30) as response:
        raw = response.read().decode()
    record = record_from(utc, body, raw)
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
    blocks = [
        {"binary": "1110010011001110", "octal": "162316", "decimal": "58574", "hexadecimal": "e4ce"},
        {"binary": "101", "octal": "5", "decimal": "5", "hexadecimal": "5"},
    ]
    raw = json.dumps({"encoding": "raw", "random_numbers": blocks})
    good = record_from("2026-01-01T000000Z", request_body(16, 2), raw)
    if good["values"] != [58574, 5]:
        raise SystemExit(f"self-test: parsed {good['values']}")

    def respond(record: dict[str, Any], answer: dict[str, Any]) -> None:
        record["raw"] = json.dumps(answer)
        record["raw_sha256"] = hashlib.sha256(record["raw"].encode()).hexdigest()

    disagree = copy.deepcopy(blocks)
    disagree[0]["decimal"] = "58575"
    wide = copy.deepcopy(blocks)
    wide[1] = {"binary": "1" * 17, "octal": "377777", "decimal": "131071", "hexadecimal": "1ffff"}
    mutations = [
        ("disagreeing representation", lambda r: respond(r, {"encoding": "raw", "random_numbers": disagree})),
        ("over-wide block", lambda r: respond(r, {"encoding": "raw", "random_numbers": wide})),
        ("raw byte", lambda r: r.__setitem__("raw", raw.replace("58574", "58575"))),
        ("short response", lambda r: respond(r, {"encoding": "raw", "random_numbers": blocks[:1]})),
        ("value", lambda r: r["values"].__setitem__(1, 6)),
    ]
    for name, mutate in mutations:
        record = copy.deepcopy(good)
        mutate(record)
        try:
            admit(record)
        except DrawError:
            continue
        raise SystemExit(f"self-test: the {name} mutation was admitted")
    print(f"outshift_qrng self-test: {len(mutations)} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("draw")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--bits", type=int, default=DEFAULT_BITS)
    p.add_argument("--blocks", type=int, default=DEFAULT_BLOCKS)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.command == "draw":
            print(draw(args.out, args.bits, args.blocks))
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
