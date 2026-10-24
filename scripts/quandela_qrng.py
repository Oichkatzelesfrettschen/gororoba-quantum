"""Quantum random draws from the Quandela Cloud QRNG, retained as evidence for the seeds a case takes.

GET https://api.cloud.quandela.com/qt/qrng/ints?type=T&count=N (the QRNG tag of
docs/notes/quandela/api/cloud-qt-openapi.json) takes type uint8, uint16,
uint32 or uint64 and a count the specification describes as random bytes, and
authenticates by the job token as a bearer header. It answers {"jobs": [{"id",
"chsh", "min_entropy", "ints"}]}: each generating job reports its CHSH value
(between 0 and 2 sqrt 2; a value above 2 violates the local bound) and its
min-entropy. The service prices QRNG bytes through the account's offer and
charges entity credits, so every draw is a provider QRNG read that waits for
the user's approval of a written case (AGENTS.md, Hardware services): draw
refuses before any request unless --approved-case names that case's file, and
the record binds the file's path and sha256. The token comes from the file
QUANDELA_TOKEN_FILE names through qd_platform.request, which refuses
redirects, and never enters a record or a log.

A draw is used once: a case cites the record and the index of every value it
took, so no value seeds two cases.

Subcommands:

- draw --out DIR --approved-case FILE [--type uint16] [--count N] (network,
  credits) makes one request and writes DIR/draw-<UTC>.json: the route, the
  UTC time, the approved case's path and sha256, the raw response bytes as
  text, their sha256 and the values of every job in answer order.
- check DIR (offline) requires every record's sha256 to match its raw bytes,
  every job to report a CHSH value above 2 and at most 2 sqrt 2 and a
  min-entropy in (0, 1], every value to lie in its type's range, and the
  parsed values to equal the jobs' ints in order.
- --self-test requires a local-bound CHSH value, an out-of-range value, an
  edited raw byte and an edited value to be rejected.

Usage: QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/quandela_qrng.py
       (draw --out DIR --approved-case FILE | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import datetime
import functools
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel  # noqa: E402

SCHEMA = "quandela-qrng-draw-v1"
ROUTE = "/qt/qrng/ints"
RANGES = {"uint8": 2**8 - 1, "uint16": 2**16 - 1, "uint32": 2**32 - 1, "uint64": 2**64 - 1}
TSIRELSON = 2 * math.sqrt(2)
ROOT = Path(__file__).resolve().parents[1]


class DrawError(ValueError):
    pass


def record_from(route: str, utc: str, case: dict[str, str], kind: str, raw: str) -> dict[str, Any]:
    answer = json.loads(raw)
    record = {
        "schema": SCHEMA,
        "source": route,
        "retrieved_utc": utc,
        "approved_case": case,
        "type": kind,
        "raw": raw,
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "values": [value for job in answer.get("jobs", []) for value in job.get("ints", [])],
    }
    admit(record)
    return record


def job_values(job: dict[str, Any], kind: str) -> list[int]:
    """One generating job's integers, after its Bell violation, min-entropy and value range hold."""
    chsh, entropy = job.get("chsh"), job.get("min_entropy")
    if not isinstance(chsh, int | float) or not 2 < chsh <= TSIRELSON:
        raise DrawError(f"job {job.get('id')}: CHSH {chsh!r} does not violate the local bound")
    if not isinstance(entropy, int | float) or not 0 < entropy <= 1:
        raise DrawError(f"job {job.get('id')}: min-entropy {entropy!r} outside (0, 1]")
    ints = job.get("ints")
    if not isinstance(ints, list):
        raise DrawError(f"job {job.get('id')}: no ints")
    for value in ints:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= RANGES[kind]:
            raise DrawError(f"value {value!r} outside {kind}")
    return ints


def admit(record: dict[str, Any]) -> None:
    """A record whose bytes, Bell violation, min-entropy, value range and order all hold."""
    if record.get("schema") != SCHEMA:
        raise DrawError(f"schema {record.get('schema')!r}")
    raw = record["raw"]
    if hashlib.sha256(raw.encode()).hexdigest() != record["raw_sha256"]:
        raise DrawError("raw bytes differ from their sha256")
    if record["type"] not in RANGES:
        raise DrawError(f"type {record['type']!r}")
    case = record.get("approved_case")
    if not isinstance(case, dict) or not case.get("path") or len(str(case.get("sha256", ""))) != 64:
        raise DrawError("the record binds no approved case")
    jobs = json.loads(raw).get("jobs")
    if not isinstance(jobs, list) or not jobs:
        raise DrawError("the response carries no jobs")
    checked = parallel.ordered_map(functools.partial(job_values, kind=record["type"]), jobs)
    values = [value for ints in checked for value in ints]
    if values != record["values"]:
        raise DrawError("parsed values differ from the raw response")


def approved_case(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise DrawError(f"approved case {path} is missing; a QRNG read waits for an approved written case")
    resolved = path.resolve()
    shown = resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else path.name
    return {"path": shown, "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest()}


def draw(out: Path, case_path: Path, kind: str, count: int) -> Path:
    if kind not in RANGES or count < 1:
        raise DrawError(f"type {kind!r} or count {count} outside the service's domain")
    case = approved_case(case_path)
    import qd_platform

    route = f"{ROUTE}?type={kind}&count={count}"
    utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    raw = qd_platform.request("GET", route, raw=True).decode()
    record = record_from(route, utc, case, kind, raw)
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
    jobs = [
        {"id": "a", "chsh": 2.6, "min_entropy": 0.4, "ints": [1, 65535]},
        {"id": "b", "chsh": 2.7, "min_entropy": 0.5, "ints": [7]},
    ]
    raw = json.dumps({"jobs": jobs})
    case = {"path": "results/example/case.md", "sha256": "0" * 64}
    good = record_from(f"{ROUTE}?type=uint16&count=6", "2026-01-01T000000Z", case, "uint16", raw)
    if good["values"] != [1, 65535, 7]:
        raise SystemExit(f"self-test: parsed {good['values']}")

    def respond(record: dict[str, Any], answer: dict[str, Any]) -> None:
        record["raw"] = json.dumps(answer)
        record["raw_sha256"] = hashlib.sha256(record["raw"].encode()).hexdigest()

    local = copy.deepcopy(jobs)
    local[1]["chsh"] = 2.0
    mutations = [
        ("local-bound CHSH", lambda r: respond(r, {"jobs": local})),
        ("range", lambda r: r.update(type="uint8")),
        ("raw byte", lambda r: r.__setitem__("raw", raw.replace("65535", "65534"))),
        ("value", lambda r: r["values"].__setitem__(2, 8)),
        ("unbound case", lambda r: r.update(approved_case={})),
    ]
    for name, mutate in mutations:
        record = copy.deepcopy(good)
        mutate(record)
        try:
            admit(record)
        except DrawError:
            continue
        raise SystemExit(f"self-test: the {name} mutation was admitted")
    try:
        draw(Path("unused"), ROOT / "no-such-approved-case.md", "uint16", 2)
    except DrawError:
        pass
    else:
        raise SystemExit("self-test: a draw without an approved case proceeded")
    print(f"quandela_qrng self-test: {len(mutations) + 1} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("draw")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--approved-case", type=Path, required=True)
    p.add_argument("--type", dest="kind", default="uint16", choices=sorted(RANGES))
    p.add_argument("--count", type=int, default=512)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.self_test:
            return self_test()
        if args.command == "draw":
            print(draw(args.out, args.approved_case, args.kind, args.count))
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
