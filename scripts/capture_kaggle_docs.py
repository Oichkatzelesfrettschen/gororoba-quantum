"""Capture Kaggle's documentation into docs/notes/kaggle/ as the reference the Kaggle guides cite.

Two sources, each retained with its identity:

- kaggle.com/docs pages render in the browser only, so ``--site`` loads each
  page in headless Chromium (Playwright), takes the ``#site-content``
  element, converts it to GitHub Markdown with pandoc, and writes
  docs/notes/kaggle/site/<page>.md under a header naming the URL, the
  retrieval time and the sha256 of the rendered HTML (efficient-gpu-usage
  renders navigation only and scheduling-notebooks is not found, so neither
  is in SITE_PAGES). Collapsed
  ``<details>`` blocks, which hold the MCP tool definitions, are part of the
  DOM and are captured with it.
- The Kaggle CLI documents itself in github.com/Kaggle/kaggle-cli/docs;
  ``--cli`` downloads each Markdown file at the pinned commit CLI_COMMIT
  verbatim into docs/notes/kaggle/cli/.

Both write MANIFEST.json beside the files (path, source URL, sha256), and
``--check`` verifies every retained file against it without network access.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/kaggle"
SITE_PAGES = (
    "notebooks",
    "tpu",
    "api",
    "mcp",
    "models",
    "datasets",
    "packages",
    "benchmarks",
)
CLI_COMMIT = "931014d9c50b7b073750bc45d36a872f7ef7219b"
CLI_DOCS = (
    "README.md",
    "configuration.md",
    "kernels.md",
    "kernels_metadata.md",
    "models.md",
    "models_metadata.md",
    "model_variations.md",
    "model_variations_versions.md",
    "datasets.md",
    "datasets_metadata.md",
    "output_format.md",
    "search.md",
    "tutorials.md",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


async def render(pages: tuple[str, ...]) -> dict[str, str]:
    from playwright.async_api import async_playwright

    html: dict[str, str] = {}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 2000})
        for name in pages:
            await page.goto(f"https://www.kaggle.com/docs/{name}", wait_until="networkidle", timeout=90000)
            await page.wait_for_timeout(3000)
            html[name] = await page.locator("#site-content").inner_html()
        await browser.close()
    return html


def capture_site() -> list[dict[str, Any]]:
    out = BASE / "site"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    stamp = now()
    for name, html in asyncio.run(render(SITE_PAGES)).items():
        url = f"https://www.kaggle.com/docs/{name}"
        markdown = subprocess.run(
            ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
            input=html,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        header = (
            f"> Full piece: [{url}]({url})\n"
            f"> Retrieved {stamp} by scripts/capture_kaggle_docs.py --site (headless Chromium, pandoc);\n"
            f"> rendered HTML sha256 {sha256(html.encode())}.\n\n"
        )
        path = out / f"{name}.md"
        path.write_text(header + markdown, encoding="utf-8")
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(path.read_bytes())})
        print(f"{name}: {len(markdown)} characters")
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
