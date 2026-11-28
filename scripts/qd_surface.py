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
  or changed in class against the baseline, the policy items that changed
  (sha256 of a long string such as specs.architecture and specs.commands, the
  short lists available_commands, connected_input_modes, default_mitigations
  and known_mitigations, the Explorer price_per_shot, max_duration, locked,
  bookable, status and kind, version figures, and the surface schema) and the
  figures that changed. A baseline of schema qd-surface-v1 lacks the policy
  items, so each reads as new against it until a baseline is re-read with
  read --out. The live surface comes from the network unless --live names a
  surface file. The exit status is 0 when the field surface and the policy
  items equal the baseline and 1 otherwise; a performance figure change alone
  exits 0.

Usage: QUANDELA_TOKEN_FILE=... "$PYTHON" scripts/qd_surface.py diff
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

import qd_platform

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "qd-surface-v2"
READABLE = ("qd-surface-v1", SCHEMA)
BASELINE = ROOT / "docs/evidence/quandela/platform-surface-2026-11-27.json"
# A scalar longer than this many characters is a document or a serialized chip, not a figure.
FIGURE_CHARS = 40
# Short lists whose members are policy (commands, input modes, mitigations): kept whole, by the last path component.
SHORT_LISTS = ("available_commands", "connected_input_modes", "default_mitigations", "known_mitigations")
# Explorer row fields that carry price, limits, availability and class.
EXPLORER_FIELDS = ("price_per_shot", "max_duration", "locked", "bookable", "status")


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
    digests = {
        path: hashlib.sha256(leaf.encode()).hexdigest()
        for path, leaf in leaves.items()
        if isinstance(leaf, str) and len(leaf) > FIGURE_CHARS
    }
    lists = {
        path: leaf for path, leaf in leaves.items() if path.rsplit(".", 1)[-1] in SHORT_LISTS and isinstance(leaf, list)
    }
    numeric = {
        path: {
            "n": len(leaf),
            "min": min(leaf),
            "max": max(leaf),
            "mean": round(statistics.fmean(leaf), 9),
            "sha256": hashlib.sha256(json.dumps(leaf).encode()).hexdigest(),
        }
        for path, leaf in leaves.items()
        if isinstance(leaf, list)
        and leaf
        and path not in lists
        and all(isinstance(x, int | float) and not isinstance(x, bool) for x in leaf)
    }
    return {
        "fields": {path: classify(leaf) for path, leaf in leaves.items()},
        "figures": figures,
        "digests": digests,
        "lists": lists,
        "numeric": numeric,
    }


def build(rows: list[dict[str, Any]], records: dict[str, Any], stamp: str) -> dict[str, Any]:
    """A surface from the Explorer rows and each platform's processor record."""
    platforms = {}
    for row in sorted(rows, key=lambda r: r["name"]):
        name = row["name"]
        explorer = {"kind": row.get("type"), **{field: row.get(field) for field in EXPLORER_FIELDS}}
        platforms[name] = {
            "kind": row.get("type"),
            "explorer": explorer,
            **surface_of(qd_platform.scrub(records[name])),
        }
    return {"schema": SCHEMA, "retrieved_utc": stamp, "platforms": platforms}


def read_live() -> dict[str, Any]:
    """The live surface: one Explorer read and one processor read per platform."""
    rows = qd_platform.get("/api/platforms/public/explorer", auth=False)
    records = {row["name"]: qd_platform.get(qd_platform.platform_route(row["name"])) for row in rows}
    return build(rows, records, qd_platform.now())


def policy_rows(name: str, old: dict[str, Any], new: dict[str, Any]) -> list[tuple[str, ...]]:
    """Rows (platform, item, baseline, live) for each policy item that differs: the digest of a long string
    (architecture, commands), a short policy list, an Explorer field (price, limits, lock, status, kind) and a
    version figure. An item a baseline of the first schema lacks reads `-` there, so a baseline that predates the
    item reports it as new."""
    rows: list[tuple[str, ...]] = []
    for section in ("digests", "lists", "explorer"):
        was, now = old.get(section, {}), new.get(section, {})
        for key in sorted(set(was) | set(now)):
            if was.get(key) != now.get(key):
                rows.append((name, f"{section}.{key}", short(was.get(key)), short(now.get(key))))
    for path in sorted(set(old["figures"]) | set(new["figures"])):
        if "version" in path and old["figures"].get(path) != new["figures"].get(path):
            rows.append((name, f"figures.{path}", short(old["figures"].get(path)), short(new["figures"].get(path))))
    return rows


def short(value: Any) -> str:
    """A table cell: `-` for a missing value, the first 12 characters of a digest, else the JSON text."""
    if value is None:
        return "-"
    text = value if isinstance(value, str) else json.dumps(value)
    return text[:12] if len(text) == 64 and isinstance(value, str) else text


def diff(baseline: dict[str, Any], live: dict[str, Any]) -> dict[str, list[tuple[str, ...]]]:
    """Field rows (platform, path, state, baseline class, live class), figure rows (platform, path, old, new) and
    policy rows (platform, item, old, new). Fields and policy rows decide the exit status; figures do not."""
    fields: list[tuple[str, ...]] = []
    figures: list[tuple[str, ...]] = []
    policy: list[tuple[str, ...]] = []
    if baseline.get("schema") != live.get("schema"):
        policy.append(("(surface)", "schema", str(baseline.get("schema")), str(live.get("schema"))))
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
            if was != now and path in old["fields"] and path in new["fields"] and "version" not in path:
                figures.append((name, path, str(was), str(now)))
        for path in sorted(set(old.get("numeric", {})) | set(new.get("numeric", {}))):
            was, now = old.get("numeric", {}).get(path), new.get("numeric", {}).get(path)
            if was != now and was is not None and now is not None:
                figures.append(
                    (name, path, short(was["sha256"]), f"{short(now['sha256'])} n={now['n']} mean={now['mean']}")
                )
        if old.get("kind") != new.get("kind"):
            policy.append((name, "kind", short(old.get("kind")), short(new.get("kind"))))
        policy += policy_rows(name, old, new)
    return {"fields": fields, "figures": figures, "policy": policy}


def render(result: dict[str, list[tuple[str, ...]]]) -> str:
    """The diff as two Markdown tables."""
    lines = ["| platform | field | state | baseline class | live class |", "|---|---|---|---|---|"]
    lines += [f"| `{r[0]}` | `{r[1]}` | {r[2]} | {r[3]} | {r[4]} |" for r in result["fields"]]
    if not result["fields"]:
        lines.append("| (none) | | the field surface equals the baseline | | |")
    lines += ["", "| platform | policy item | baseline | live |", "|---|---|---|---|"]
    lines += [f"| `{r[0]}` | `{r[1]}` | {r[2]} | {r[3]} |" for r in result["policy"]]
    if not result["policy"]:
        lines.append("| (none) | | | |")
    lines += ["", "| platform | figure | baseline | live |", "|---|---|---|---|"]
    lines += [f"| `{r[0]}` | `{r[1]}` | {r[2]} | {r[3]} |" for r in result["figures"]]
    if not result["figures"]:
        lines.append("| (none) | | | |")
    return "\n".join(lines)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") not in READABLE:
        raise SystemExit(f"{path}: not a {' or '.join(READABLE)} surface")
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
    return 1 if result["fields"] or result["policy"] else 0


if __name__ == "__main__":
    sys.exit(main())
