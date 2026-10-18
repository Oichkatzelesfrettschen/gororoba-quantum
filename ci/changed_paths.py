"""Resolve event diffs before gate installation; unavailable bases select exhaustive checks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def select(root: Path, event: str, base: str, destination: Path) -> dict[str, bool]:
    flags = {"rocq": True, "full": event != "pull_request", "limited": False}
    if event not in ("pull_request", "push") or not base or set(base) == {"0"}:
        return flags
    fetched = subprocess.run(["git", "fetch", "-q", "--depth=1", "origin", base], cwd=root, capture_output=True)
    if fetched.returncode:
        print("diff base fetch failed; selecting exhaustive checks", file=sys.stderr)
        return flags
    difference = subprocess.run(
        ["git", "diff", "--no-renames", "--name-only", "-z", base, "HEAD"], cwd=root, capture_output=True
    )
    if difference.returncode:
        print("diff base comparison failed; selecting exhaustive checks", file=sys.stderr)
        return flags
    filtered = subprocess.run(
        ["sh", "ci/rocq_changed.sh"], cwd=root, input=difference.stdout.replace(b"\0", b"\n"), capture_output=True
    )
    if filtered.returncode not in (0, 1):
        raise RuntimeError("Rocq path selector failed")
    destination.write_bytes(difference.stdout)
    flags.update(rocq=filtered.returncode == 0, limited=True)
    return flags


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    destination = Path(os.environ["RUNNER_TEMP"]) / "changed-files.bin"
    flags = select(root, os.environ["EVENT"], os.environ.get("BASE", ""), destination)
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        for name, enabled in flags.items():
            print(f"{name}={str(enabled).lower()}", file=output)


if __name__ == "__main__":
    main()
