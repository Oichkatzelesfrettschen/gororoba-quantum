"""Independent copies of the repository: a verified git bundle and a Software Heritage archival visit.

GitHub and the workstation clones are the only copies a checksum ledger can be
checked against; a digest detects loss but restores nothing. Two copies live
outside both:

- ``bundle --out DIR`` writes ``gororoba-quantum-<commit>.bundle`` with every
  branch, tag and remote-tracking ref (``--branches --tags --remotes``; the
  per-worktree ``HEAD`` pseudo-refs are local state a clone never restores)
  and a manifest beside it naming the bundle's
  sha256, byte length, head commit, refs and git version. DIR must lie outside
  the repository; it belongs on a different physical device or medium.
- ``verify BUNDLE`` checks the bundle against its manifest, runs ``git bundle
  verify``, then restores it: a mirror clone into a temporary directory and
  ``git fsck --full`` on the clone. A bundle passes only if that restore
  succeeds and holds the manifest's head commit.
- ``swh-save --record FILE`` (network) asks Software Heritage to archive the
  public origin (``POST /api/1/origin/save/git/url/<origin>/``) and writes the
  request URL, UTC time and response body to FILE. Software Heritage stores
  the history content-addressed, under SWHIDs, independently of GitHub.
- ``swh-status --record FILE`` (network) records the latest save requests and
  archival visits of the origin.

The origin is the public ``origin`` remote; no credential is sent or recorded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SWH_API = "https://archive.softwareheritage.org/api/1"
MANIFEST_SCHEMA = "repository-bundle-v1"


def git(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, check=True).stdout


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def public_origin() -> str:
    url = git("remote", "get-url", "origin").strip()
    if not url.startswith("https://github.com/"):
        raise SystemExit(f"origin {url} is not a public https GitHub URL")
    return url.removesuffix(".git")


def outside_repository(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        raise SystemExit(f"{resolved} lies inside the repository; an independent copy lives outside it")
    return resolved


def bundle(out: Path) -> dict[str, Any]:
    out = outside_repository(out)
    out.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "HEAD").strip()
    target = out / f"gororoba-quantum-{head[:12]}.bundle"
    if target.exists():
        raise SystemExit(f"{target} exists")
    git("bundle", "create", str(target), "--branches", "--tags", "--remotes")
    refs = sorted(line for line in git("bundle", "list-heads", str(target)).splitlines() if line)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "bundle": target.name,
        "sha256": sha256_file(target),
        "bytes": target.stat().st_size,
        "head": head,
        "refs": refs,
        "git_version": git("--version").strip(),
        "created_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ"),
    }
    target.with_suffix(".json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return manifest


def verify(path: Path) -> dict[str, Any]:
    path = path.resolve()
    manifest = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA or manifest["bundle"] != path.name:
        raise SystemExit(f"{path.with_suffix('.json')} does not describe {path.name}")
    if path.stat().st_size != manifest["bytes"] or sha256_file(path) != manifest["sha256"]:
        raise SystemExit(f"{path.name} differs from its manifest's sha256 or length")
    git("bundle", "verify", str(path))
    with tempfile.TemporaryDirectory(prefix="bundle-restore-") as scratch:
        clone = Path(scratch) / "restore.git"
        subprocess.run(["git", "clone", "--quiet", "--mirror", str(path), str(clone)], check=True)
        subprocess.run(["git", "fsck", "--full", "--no-progress"], cwd=clone, check=True, capture_output=True)
        restored = sorted(f"{sha} {ref}" for ref, sha in _refs(clone))
        if manifest["head"] not in {line.split()[0] for line in restored}:
            raise SystemExit(f"restored clone lacks head commit {manifest['head']}")
        if restored != sorted(manifest["refs"]):
            raise SystemExit("restored refs differ from the manifest")
    return {"bundle": path.name, "sha256": manifest["sha256"], "head": manifest["head"], "restored_refs": len(restored)}


def _refs(repository: Path) -> list[tuple[str, str]]:
    lines = git("for-each-ref", "--format=%(refname) %(objectname)", cwd=repository).splitlines()
    return [(ref, sha) for ref, sha in (line.split() for line in lines)]


def _request(method: str, url: str) -> tuple[int, str]:
    request = urllib.request.Request(url, method=method, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def swh(method: str, path: str, record: Path) -> dict[str, Any]:
    url = f"{SWH_API}/{path}"
    status, body = _request(method, url)
    entry = {
        "schema": "software-heritage-observation-v1",
        "method": method,
        "url": url,
        "observed_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ"),
        "status": status,
        "body": body,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }
    record.parent.mkdir(parents=True, exist_ok=True)
    with record.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, indent=1) + "\n")
    if status >= 400:
        raise SystemExit(f"{method} {url} answered {status}; {record} holds the response")
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("bundle").add_argument("--out", type=Path, required=True)
    sub.add_parser("verify").add_argument("bundle", type=Path)
    for name in ("swh-save", "swh-status"):
        sub.add_parser(name).add_argument("--record", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "bundle":
        result: dict[str, Any] = bundle(args.out)
    elif args.command == "verify":
        result = verify(args.bundle)
    else:
        origin = urllib.parse.quote(public_origin(), safe=":/")
        if args.command == "swh-save":
            result = swh("POST", f"origin/save/git/url/{origin}/", args.record)
        else:
            result = swh("GET", f"origin/save/git/url/{origin}/", args.record)
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
