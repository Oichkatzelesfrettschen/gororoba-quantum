"""Shot-counter census of the retained simulator outputs: every count histogram against its declared shots.

A simulated gate-model shot is one sampled execution that writes one classical record, so a supported histogram
sums to the shots its record declares. The census reads every JSON and gzipped JSON file under results/kaggle/,
results/local_compute/ and results/local-simulation/, finds each count histogram (a nonempty mapping from bit
strings to nonnegative integers), and takes as its declared shots the integer `shots` or `shots_per_pub` of the
nearest enclosing mapping or of that mapping's `options` or `metadata`. A histogram whose record declares no shots
is listed with its totals, because its analysis takes the sample size from the histogram itself. Each file is one
item of parallel.ordered_map. The output records its inventory of files, the audit's frozen surface; `--check`
recomputes that inventory and compares the retained output, so a file retained later leaves the check valid.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

OUT = Path(__file__).with_name("simulator_counter_census.json")
SCHEMA = "simulator-counter-census-v1"
ROOTS = ("results/kaggle", "results/local_compute", "results/local-simulation")
DECLARATIONS = ("shots", "shots_per_pub")
BITS = frozenset("01 ")


def histogram(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and bool(value)
        and all(isinstance(k, str) and k != "" and (set(k) <= BITS or k.startswith("0x")) for k in value)
        and all(type(v) is int and v >= 0 for v in value.values())
    )


def declared(stack: list[dict[str, Any]]) -> int | None:
    for mapping in reversed(stack):
        for holder in (mapping, mapping.get("options"), mapping.get("metadata")):
            if isinstance(holder, dict):
                for key in DECLARATIONS:
                    if type(holder.get(key)) is int:
                        return int(holder[key])
    return None


def load(path: Path) -> Any:
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.name.endswith(".gz") else data)


def census(path: str) -> dict[str, Any]:
    try:
        tree = load(ROOT / path)
    except (ValueError, UnicodeDecodeError, OSError) as error:
        return {"file": path, "unparsed": type(error).__name__}
    matched, mismatches, undeclared = 0, [], []

    def walk(value: Any, stack: list[dict[str, Any]], where: str) -> None:
        nonlocal matched
        if histogram(value):
            total, shots = sum(value.values()), declared(stack)
            if shots is None:
                undeclared.append(total)
            elif shots == total:
                matched += 1
            else:
                mismatches.append({"file": path, "path": where, "declared": shots, "histogram_total": total})
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, [*stack, value], f"{where}/{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, stack, f"{where}[{index}]")

    walk(tree, [], "")
    return {"file": path, "matched": matched, "mismatches": mismatches, "undeclared": undeclared}


def record(inventory: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """The census over inventory (root -> repository-relative files), or over every retained file when None."""
    if inventory is None:
        inventory = {
            root: sorted(
                str(p.relative_to(ROOT))
                for p in (ROOT / root).rglob("*")
                if p.is_file() and p.name.endswith((".json", ".json.gz"))
            )
            for root in ROOTS
        }
    items = [path for root in ROOTS for path in inventory[root]]
    parts = ordered_map(census, items, min_items=1)
    summary: dict[str, Any] = {}
    for root in ROOTS:
        mine = [p for p in parts if p["file"].startswith(f"{root}/")]
        parsed = [p for p in mine if "unparsed" not in p]
        summary[root] = {
            "files": len(mine),
            "files_with_histograms": sum(1 for p in parsed if p["matched"] or p["mismatches"] or p["undeclared"]),
            "histograms_matching_declared_shots": sum(p["matched"] for p in parsed),
            "mismatches": [m for p in parsed for m in p["mismatches"]],
            "undeclared": [
                {"file": p["file"], "histograms": len(p["undeclared"]), "totals": sorted(set(p["undeclared"]))}
                for p in parsed
                if p["undeclared"]
            ],
            "unparsed": [{"file": p["file"], "error": p["unparsed"]} for p in mine if "unparsed" in p],
        }
    return {"schema": SCHEMA, "inventory": inventory, "declarations": list(DECLARATIONS), **summary}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inventory = json.loads(OUT.read_text(encoding="utf-8"))["inventory"] if args.check else None
    text = json.dumps(record(inventory), indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} differs from the recomputed census", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
