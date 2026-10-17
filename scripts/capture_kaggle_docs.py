"""Capture Kaggle's documentation into docs/notes/kaggle/ as the reference the Kaggle guides cite.

Two sources, each retained with its identity:

- kaggle.com/docs serves each page's Markdown source at
  ``https://www.kaggle.com/docs/<page>.md`` (the "Copy as Markdown" view of
  the rendered page); ``--site`` downloads every page the docs navigation
  lists, SITE_PAGES, verbatim into docs/notes/kaggle/site/<page>.md.
  Root-relative links in those files (``/settings``, ``/static/...``) are
  relative to https://www.kaggle.com/.
- The Kaggle CLI documents itself in github.com/Kaggle/kaggle-cli/docs;
  ``--cli`` downloads every Markdown file of that directory at the pinned
  commit CLI_COMMIT verbatim into docs/notes/kaggle/cli/, so its internal
  links resolve.

Both write MANIFEST.json beside the files (path, source URL, sha256), and
``--check`` verifies every retained file against it without network access.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/kaggle"
SITE_PAGES = (
    "competitions",
    "datasets",
    "efficient-gpu-usage",
    "tpu",
    "models",
    "competitions-setup",
    "organizations",
    "groups",
    "packages",
    "notebooks",
    "mcp",
    "benchmarks",
    "api",
)
CLI_COMMIT = "931014d9c50b7b073750bc45d36a872f7ef7219b"
CLI_DOCS = (
    "README.md",
    "benchmarks.md",
    "competition_creation.md",
    "competitions.md",
    "configuration.md",
    "datasets.md",
    "datasets_metadata.md",
    "forums.md",
    "kernels.md",
    "kernels_metadata.md",
    "model_variations.md",
    "model_variations_versions.md",
    "models.md",
    "models_metadata.md",
    "output_format.md",
    "search.md",
    "simulation_competitions.md",
    "tutorials.md",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def capture_site() -> list[dict[str, Any]]:
    out = BASE / "site"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in SITE_PAGES:
        url = f"https://www.kaggle.com/docs/{name}.md"
        with urllib.request.urlopen(url, timeout=60) as response:
            kind = response.headers.get_content_type()
            data = response.read()
        if kind != "text/markdown":
            raise SystemExit(f"{url} answered {kind}, not text/markdown")
        path = out / f"{name}.md"
        path.write_bytes(data)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(data)})
        print(f"site/{name}.md: {len(data)} bytes")
    return rows


def capture_cli() -> list[dict[str, Any]]:
    out = BASE / "cli"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in CLI_DOCS:
        url = f"https://raw.githubusercontent.com/Kaggle/kaggle-cli/{CLI_COMMIT}/docs/{name}"
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        path = out / name
        path.write_bytes(data)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(data)})
        print(f"cli/{name}: {len(data)} bytes")
    return rows


def manifest_path(kind: str) -> Path:
    return BASE / kind / "MANIFEST.json"


def write_manifest(kind: str, rows: list[dict[str, Any]]) -> None:
    doc = {"schema": "kaggle-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    if kind == "cli":
        doc["commit"] = CLI_COMMIT
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def check() -> int:
    count = 0
    for kind in ("site", "cli"):
        doc = json.loads(manifest_path(kind).read_text(encoding="utf-8"))
        for row in doc["files"]:
            data = (ROOT / row["path"]).read_bytes()
            if sha256(data) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            count += 1
    print(f"kaggle docs: {count} captured files match their manifests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", action="store_true")
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    if not (args.site or args.cli):
        parser.error("give --site, --cli or --check")
    if args.site:
        write_manifest("site", capture_site())
    if args.cli:
        write_manifest("cli", capture_cli())
    return 0


if __name__ == "__main__":
    sys.exit(main())
