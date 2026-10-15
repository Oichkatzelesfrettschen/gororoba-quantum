"""Bind the imported Ramsey viewer to its build manifest and to the record's patch analysis.

Every file the build manifest lists and the directory retains matches its
sha256 (the manifest's README.md is retained as README.upstream.md); the
omitted files are the regenerable previews and browser log. Every plotted
point's X and Y counts and shot totals equal the patch-analysis point at the
same condition, work register and executed idle, and every patch-analysis
point is plotted exactly once.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENAMED = {"README.md": "README.upstream.md"}
OMITTED_PREFIXES = ("previews/", "browser_validation.log")
CONDITIONS = {"plain": "ramsey_plain", "echo": "ramsey_echo", "window c0": "window_c0", "window c1": "window_c1"}
ROLES = {"A": "work_a", "B": "work_b"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"viewer binding: {message}")


def check_manifest() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    checked = 0
    for entry in manifest["files"]:
        path = HERE / RENAMED.get(entry["path"], entry["path"])
        if not path.exists():
            require(entry["path"].startswith(OMITTED_PREFIXES), f"{entry['path']} is missing")
            continue
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], f"{path.name} differs from the build")
        checked += 1
    return checked


def check_counts() -> int:
    series = json.loads((HERE / "data/measurements_4d.json").read_text(encoding="utf-8"))["series"]
    analysis = json.loads((HERE.parent / "patch-analysis.json").read_text(encoding="utf-8"))["conditions"]
    expected = {(key, round(point["t_us"], 6)): point for key, entry in analysis.items() for point in entry["points"]}
    seen: set[tuple[str, float]] = set()
    for trace in series:
        key = f"{CONDITIONS[trace['condition']]}/{ROLES[trace['role']]}"
        for point in trace["points"]:
            slot = (key, round(point["t"], 6))
            require(slot in expected and slot not in seen, f"{slot} is not a unique patch-analysis point")
            source = expected[slot]
            counts = (point["kx"], point["nx"], point["ky"], point["ny"])
            truth = (source["x_zero"], source["x_shots"], source["y_zero"], source["y_shots"])
            require(counts == truth, f"{slot} plots {counts}, patch analysis holds {truth}")
            seen.add(slot)
    require(seen == set(expected), f"unplotted patch-analysis points: {sorted(set(expected) - seen)}")
    return len(seen)


def main() -> int:
    files = check_manifest()
    points = check_counts()
    print(f"viewer binding: {files} build files match the manifest; {points} of {points} plotted points match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
