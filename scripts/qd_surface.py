"""Read-only watch of the field surface the Quandela server presents for each platform.

The retained catalogue answers which fields a processor record carried at one
snapshot; this script answers which fields the live server presents now and
how they differ from a retained surface. A surface holds, per Explorer
platform, the value class of every field of /api/platforms/{name}/processor
(`str`, `int`, `float`, `bool`, `list`, `object`, `null`, `empty`) and the
short scalar figures (status, performance figures, limits, software
versions). A field the server stops sending leaves the surface and reads
`absent` in a diff. No value of a long field (architecture, documentation)
and no account identifier enters a surface.

Subcommands, all read-only (the network read uses the job token that
QUANDELA_TOKEN_FILE names, as qd_platform.py does, and creates, cancels and
submits nothing):

- read --out FILE  writes the live surface to FILE.
- diff [--baseline FILE] [--live FILE]  prints the fields that are absent, new
  or changed in class against the baseline, and the figures that changed. The
  live surface comes from the network unless --live names a surface file. The
  exit status is 0 when the field surface equals the baseline and 1 when a
  field is absent, new or changed in class; a figure change alone exits 0.

Usage: QUANDELA_TOKEN_FILE=... "$PYTHON" scripts/qd_surface.py diff
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import qd_platform

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "qd-surface-v1"
BASELINE = ROOT / "docs/evidence/quandela/platform-surface-2026-11-27.json"
# A scalar longer than this many characters is a document or a serialized chip, not a figure.
FIGURE_CHARS = 40


def classify(value: Any) -> str:
    """The value class of one field: null, empty (an empty string, list or object), or its type."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    kinds = {str: "str", list: "list", dict: "object"}
    for kind, name in kinds.items():
        if isinstance(value, kind):
            return name if value else "empty"
    return type(value).__name__


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    """Each leaf of a record under its dotted path; a list and an empty object are leaves."""
    if isinstance(value, dict) and value:
        out: dict[str, Any] = {}
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}.{key}" if prefix else str(key)))
        return out
    return {prefix: value}


def surface_of(record: Any) -> dict[str, Any]:
    """The field classes and the scalar figures of one processor record."""
    leaves = flatten(record if isinstance(record, dict) else {})
    figures = {
        path: leaf
        for path, leaf in leaves.items()
        if isinstance(leaf, int | float | bool) or (isinstance(leaf, str) and 0 < len(leaf) <= FIGURE_CHARS)
    }
    return {"fields": {path: classify(leaf) for path, leaf in leaves.items()}, "figures": figures}


def build(rows: list[dict[str, Any]], records: dict[str, Any], stamp: str) -> dict[str, Any]:
    """A surface from the Explorer rows and each platform's processor record."""
    platforms = {}
    for row in sorted(rows, key=lambda r: r["name"]):
        name = row["name"]
        platforms[name] = {"kind": row.get("type"), **surface_of(qd_platform.scrub(records[name]))}
    return {"schema": SCHEMA, "retrieved_utc": stamp, "platforms": platforms}


def read_live() -> dict[str, Any]:
    """The live surface: one Explorer read and one processor read per platform."""
    rows = qd_platform.get("/api/platforms/public/explorer", auth=False)
    records = {row["name"]: qd_platform.get(qd_platform.platform_route(row["name"])) for row in rows}
    return build(rows, records, qd_platform.now())


def diff(baseline: dict[str, Any], live: dict[str, Any]) -> dict[str, list[tuple[str, ...]]]:
    """Field rows (platform, path, state, baseline class, live class) and figure rows (platform, path, old, new)."""
    fields: list[tuple[str, ...]] = []
    figures: list[tuple[str, ...]] = []
    old_platforms, new_platforms = baseline["platforms"], live["platforms"]
    for name in sorted(set(old_platforms) | set(new_platforms)):
        if name not in new_platforms:
            fields.append((name, "(platform)", "absent", "listed", "-"))
            continue
        if name not in old_platforms:
            fields.append((name, "(platform)", "new", "-", "listed"))
            continue
        old, new = old_platforms[name], new_platforms[name]
        for path in sorted(set(old["fields"]) | set(new["fields"])):
            was, now = old["fields"].get(path), new["fields"].get(path)
            if was == now:
                continue
            state = "absent" if now is None else "new" if was is None else "changed"
            fields.append((name, path, state, was or "-", now or "-"))
        for path in sorted(set(old["figures"]) | set(new["figures"])):
            was, now = old["figures"].get(path), new["figures"].get(path)
            if was != now and path in old["fields"] and path in new["fields"]:
                figures.append((name, path, str(was), str(now)))
    return {"fields": fields, "figures": figures}


def render(result: dict[str, list[tuple[str, ...]]]) -> str:
    """The diff as two Markdown tables."""
    lines = ["| platform | field | state | baseline class | live class |", "|---|---|---|---|---|"]
    lines += [f"| `{r[0]}` | `{r[1]}` | {r[2]} | {r[3]} | {r[4]} |" for r in result["fields"]]
    if not result["fields"]:
        lines.append("| (none) | | the field surface equals the baseline | | |")
    lines += ["", "| platform | figure | baseline | live |", "|---|---|---|---|"]
    lines += [f"| `{r[0]}` | `{r[1]}` | {r[2]} | {r[3]} |" for r in result["figures"]]
    if not result["figures"]:
        lines.append("| (none) | | | |")
    return "\n".join(lines)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise SystemExit(f"{path}: not a {SCHEMA} surface")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    reader = commands.add_parser("read", help="write the live surface to a file")
    reader.add_argument("--out", type=Path, required=True)
    differ = commands.add_parser("diff", help="print the live surface against a baseline")
    differ.add_argument("--baseline", type=Path, default=BASELINE)
    differ.add_argument("--live", type=Path, help="a surface file in place of the network read")
    args = parser.parse_args(argv)
    try:
        if args.command == "read":
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(read_live(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
            return 0
        live = load(args.live) if args.live else read_live()
        result = diff(load(args.baseline), live)
    except qd_platform.PlatformError as error:
        raise SystemExit(str(error)) from None
    print(f"live surface retrieved {live['retrieved_utc']}\n")
    print(render(result))
    return 1 if result["fields"] else 0


if __name__ == "__main__":
    sys.exit(main())
