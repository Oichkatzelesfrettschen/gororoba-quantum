"""Capture Quantum Inspire's documentation into docs/notes/quantum_inspire/ as the reference the QI guides cite.

Three sources, each retained with its identity:

- quantum-inspire.com renders its knowledge base on the server, so ``--site``
  fetches each page in SITE_PAGES, keeps the ``page-layout__content`` element
  (the page title and body without the site navigation; LANDING_CLASS on the
  backend landing pages, which lack it), converts it to
  GitHub Markdown with pandoc, and writes site/<page>.md under a header naming
  the URL, the retrieval time and the sha256 of the fetched HTML.
- The quantuminspire SDK documents its CLI in its README; ``--sdk`` downloads
  README.md at SDK_COMMIT (release 4.1.0) verbatim into sdk/.
- The compute job manager publishes its OpenAPI description; ``--api``
  retains openapi.json verbatim in api/.

Each writes MANIFEST.json beside the files (path, source URL, sha256), and
``--check`` verifies every retained file against it without network access.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/quantum_inspire"
SITE = "https://www.quantum-inspire.com"
SITE_PAGES = (
    "kbase/hardware-backends",
    "kbase/tuna-operational-specifics",
    "kbase/starmon-7-operational-specifics",
    "kbase/spin-2-plus-operational-specifics",
    "kbase/ry-emulator-operational-specifics",
    "kbase/emulator-backends",
    "kbase/code-example-getting-started-with-transmons",
    "kbase/code-example-getting-started-with-the-neutral-atom-platform",
    "kbase/software-development-kit",
    "kbase/qi-tool",
    "kbase/low-level-api",
    "kbase/compilation",
    "kbase/opensquirrel",
    "kbase/cqasm",
    "kbase/cqasm-single-gate-multiple-qubits",
    "kbase/executing-your-algorithm",
    "kbase/displaying-and-downloading-your-results",
    "kbase/managing-your-account",
    "kbase/managing-your-projects",
    "kbase/qubit-register",
    "kbase/binary-register",
    "backends/transmons",
    "backends/spin-2-plus",
    "faq",
    "release-notes",
    "terms-and-conditions",
)
SDK_COMMIT = "054a4f0be22983a5d515c31a24881bc0d875463d"
SDK_FILES = ("README.md",)
OPENAPI = "https://api.quantum-inspire.com/openapi.json"
CONTENT_CLASS = "page-layout__content"
LANDING_CLASS = "layout-container"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Subtree(HTMLParser):
    """Collects the raw HTML of the first element whose class list holds klass."""

    def __init__(self, klass: str) -> None:
        super().__init__(convert_charrefs=False)
        self.klass = klass
        self.depth = 0
        self.parts: list[str] = []
        self.done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        classes = (dict(attrs).get("class") or "").split()
        if self.depth == 0 and self.klass not in classes:
            return
        self.parts.append(self.get_starttag_text() or "")
        if tag not in VOID:
            self.depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.depth:
            self.parts.append(self.get_starttag_text() or "")

    def handle_endtag(self, tag: str) -> None:
        if self.depth and not self.done:
            self.parts.append(f"</{tag}>")
            self.depth -= 1
            self.done = self.depth == 0

    def handle_data(self, data: str) -> None:
        if self.depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.depth:
            self.parts.append(f"&#{name};")


def absolute_links(markdown: str, page: str) -> str:
    """Resolve every Markdown link target against the page URL.

    The captured copy lives outside quantum-inspire.com, so a root-relative,
    page-relative or bare-host target (`quantify-os.org`) would resolve inside
    the repository; each becomes an absolute URL. Fragments stay local.
    """

    def resolve(match: re.Match[str]) -> str:
        target = match.group(1)
        if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            return match.group(0)
        if re.match(r"(www\.)?[a-z0-9-]+(\.[a-z0-9-]+)+(/|$)", target):
            return f"](https://{target})"
        return f"]({urllib.parse.urljoin(page, target)})"

    return re.sub(r"\]\(([^)\s]+)\)", resolve, markdown)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (capture_qi_docs)"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data: bytes = response.read()
    return data


def capture_site() -> list[dict[str, Any]]:
    out = BASE / "site"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    stamp = now()
    for page in SITE_PAGES:
        url = f"{SITE}/{page}/"
        html = fetch(url)
        # Knowledge-base pages hold their body in CONTENT_CLASS; the backend
        # landing pages have no such element and keep theirs in LANDING_CLASS.
        parser = Subtree(klass=CONTENT_CLASS)
        parser.feed(html.decode("utf-8"))
        if not parser.done:
            parser = Subtree(klass=LANDING_CLASS)
            parser.feed(html.decode("utf-8"))
        if not parser.done:
            raise SystemExit(f"{url}: neither a {CONTENT_CLASS} nor a {LANDING_CLASS} element")
        markdown = subprocess.run(
            ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
            input="".join(parser.parts),
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        # Inline SVG icons arrive as base64 data URIs and carry no text.
        markdown = re.sub(r"!\[\]\(data:image/[^)]*\)", "", markdown)
        markdown = absolute_links(markdown, url)
        header = (
            f"> Full piece: [{url}]({url})\n"
            f"> Retrieved {stamp} by scripts/capture_qi_docs.py --site (urllib, pandoc);\n"
            f"> fetched HTML sha256 {sha256(html)}.\n\n"
        )
        path = out / f"{page.replace('/', '_')}.md"
        path.write_text(header + markdown, encoding="utf-8")
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(path.read_bytes())})
        print(f"{page}: {len(markdown)} characters")
    return rows


def capture_sdk() -> list[dict[str, Any]]:
    out = BASE / "sdk"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in SDK_FILES:
        url = f"https://raw.githubusercontent.com/QuTech-Delft/quantuminspire/{SDK_COMMIT}/{name}"
        data = fetch(url)
        path = out / name
        path.write_bytes(data)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(data)})
        print(f"sdk/{name}: {len(data)} bytes")
    return rows


def capture_api() -> list[dict[str, Any]]:
    out = BASE / "api"
    out.mkdir(parents=True, exist_ok=True)
    data = fetch(OPENAPI)
    path = out / "openapi.json"
    path.write_bytes(data)
    print(f"api/openapi.json: {len(data)} bytes")
    return [{"path": path.relative_to(ROOT).as_posix(), "source": OPENAPI, "sha256": sha256(data)}]


def manifest_path(kind: str) -> Path:
    return BASE / kind / "MANIFEST.json"


def write_manifest(kind: str, rows: list[dict[str, Any]]) -> None:
    doc: dict[str, Any] = {"schema": "qi-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    if kind == "sdk":
        doc["commit"] = SDK_COMMIT
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def check() -> int:
    count = 0
    for kind in ("site", "sdk", "api"):
        doc = json.loads(manifest_path(kind).read_text(encoding="utf-8"))
        for row in doc["files"]:
            data = (ROOT / row["path"]).read_bytes()
            if sha256(data) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            count += 1
    print(f"quantum inspire docs: {count} captured files match their manifests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", action="store_true")
    parser.add_argument("--sdk", action="store_true")
    parser.add_argument("--api", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    if not (args.site or args.sdk or args.api):
        parser.error("give --site, --sdk, --api or --check")
    if args.site:
        write_manifest("site", capture_site())
    if args.sdk:
        write_manifest("sdk", capture_sdk())
    if args.api:
        write_manifest("api", capture_api())
    return 0


if __name__ == "__main__":
    sys.exit(main())
