"""Capture Quantum Inspire's documentation into docs/notes/quantum_inspire/ as the reference the QI guides cite.

Five sources, each retained with its identity:

- quantum-inspire.com renders its pages on the server, so ``--site`` crawls
  the site from SITE_SEEDS through every internal link of every fetched page
  (sidebar, footer and body), keeps the content element of each page (the
  first of CONTENT_CLASSES that holds text), converts it to GitHub Markdown with
  pandoc, and writes site/<page>.md under a header naming the URL, the
  retrieval time and the sha256 of the fetched HTML. Code examples sit in the
  ``initial-doc`` attribute of ``code-preview`` elements and become fenced
  blocks in their ``language``; the circuit-export widget
  (``code-visualizer``) is dropped; lazily loaded figures take their image
  URLs from the page's ``__NUXT_DATA__`` ImageRecords when the counts agree.
  Every link a page body carries is requested once and its status recorded.
- The cQASM 3.0 specification is a MkDocs site; ``--spec`` crawls every page
  under SPEC_BASE from its navigation, keeps ``md-content__inner``, renders
  arithmatex math as GFM math and line-numbered code as plain fences, and
  writes cqasm-spec/<path>.md; the manifest names the gh-pages commit.
- ``--sdk`` downloads the documentation sources of the quantuminspire,
  qiskit-quantuminspire and pennylane-quantuminspire repositories at the
  commits their release tags resolve to (SDK_REPOS) verbatim into sdk/.
- The compute job manager publishes its OpenAPI description; ``--api``
  retains openapi.json verbatim in api/.
- ``--releases`` retains the release list (name, tag, date, body) of every
  component the release-notes page links, from the GitHub REST API and the
  GitLab releases API, as releases/<component>.json plus a rendered
  releases/<component>.md, newest first. Rendered Markdown drops pictographs
  (PICTOGRAPH); the JSON keeps them as escapes.

Each writes MANIFEST.json beside the files (path, source URL, sha256); the
site and spec manifests also list every unreachable URL with the pages that
link it, and ``--check`` verifies every retained file against its manifest
without network access. It also requires each captured directory's file set to equal its
manifest's path set and that set to equal the inventory the capture defines (SDK_REPOS, the
API and release lists, the site crawl set the manifest records, the spec rows' source URLs);
``--self-test`` proves the check rejects a removed page with its row and an unlisted file on a
temporary copy.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from functools import partial
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/quantum_inspire"
KINDS = ("site", "spec", "sdk", "api", "releases")
SITE = "https://www.quantum-inspire.com"
# Crawl seeds; the crawl adds every further page an internal link reaches.
SITE_SEEDS = (
    "",
    "kbase",
    "backends",
    "about-qi",
    "contact",
    "faq",
    "partners",
    "reference",
    "release-notes",
    "release-notes-old",
    "terms-and-conditions",
    "backends/transmons",
    "backends/spin-2-plus",
    "kbase/introduction-to-quantum-computing",
    "kbase/what-is-a-qubit",
    "kbase/superposition-and-entanglement",
    "kbase/what-is-a-quantum-algorithm",
    "kbase/hello-quantum-world",
    "kbase/quick-guide",
    "kbase/creating-a-new-project",
    "kbase/managing-your-projects",
    "kbase/working-with-the-editor",
    "kbase/executing-your-algorithm",
    "kbase/displaying-and-downloading-your-results",
    "kbase/managing-your-account",
    "kbase/qubit-register",
    "kbase/binary-register",
    "kbase/qubit-basis-states",
    "kbase/cqasm",
    "kbase/cqasm-single-gate-multiple-qubits",
    "kbase/three-qubit-gates",
    "kbase/advanced-guide",
    "kbase/software-development-kit",
    "kbase/compilation",
    "kbase/opensquirrel",
    "kbase/low-level-api",
    "kbase/libket",
    "kbase/deutsch-jozsa-algorithm",
    "kbase/full-adder",
    "kbase/grover-algorithm",
    "kbase/repetition-code",
    "kbase/code-example-getting-started-with-transmons",
    "kbase/code-example-getting-started-with-the-neutral-atom-platform",
    "kbase/code-example-the-maximum-independent-set",
    "kbase/quantum-classification",
    "kbase/hardware-backends",
    "kbase/tuna-operational-specifics",
    "kbase/starmon-7-operational-specifics",
    "kbase/spin-2-plus-operational-specifics",
    "kbase/ry-emulator-operational-specifics",
    "kbase/emulator-backends",
    "kbase/qi-tool",
    "kbase/number-of-shots",
)
# Content elements in priority order: knowledge-base pages hold their body in
# page-layout__content, the backend landing pages in layout-container, the
# home page in page-content, and the kbase index, whose content element is
# empty, only in its sidebar menu.
CONTENT_CLASSES = ("page-layout__content", "layout-container", "page-content", "page-layout__sidebar")
SITE_ASSET = re.compile(r"^(_nuxt|images|logos|icon-sprite|site\.webmanifest)|\.(png|svg|js|css|ico|wasm|pdf|jpg)$")
ASSET_HOST = "https://www.datocms-assets.com/"
SPEC_BASE = "https://qutech-delft.github.io/cQASM-spec/latest/"
SPEC_REPO = "QuTech-Delft/cQASM-spec"
# repository -> (release tag, commit the tag resolves to through
# GET /repos/QuTech-Delft/{repo}/git/ref/tags/{tag}, documentation sources).
SDK_REPOS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "quantuminspire": ("4.1.0", "054a4f0be22983a5d515c31a24881bc0d875463d", ("README.md",)),
    "qiskit-quantuminspire": (
        "0.18.5",
        "fbe5256e6671a45cf2fc6557a111f0dc705cf6ac",
        (
            "README.md",
            "docs/index.rst",
            "docs/contributing.md",
            "docs/api/modules.rst",
            "docs/getting_started/index.rst",
            "docs/getting_started/installation.md",
            "docs/getting_started/submitting.md",
            "docs/hybrid/index.rst",
            "docs/hybrid/basics.md",
            "docs/hybrid/leveraging_qiskit.md",
            "docs/hybrid/hqca_circuit.py",
            "docs/hybrid/hydrogen.py",
            "docs/notebooks/index.rst",
            "docs/notebooks/basic_circuit_execution.ipynb",
            "docs/notebooks/Super Dense Coding.ipynb",
            "docs/notebooks/QI2 Performance Test.ipynb",
        ),
    ),
    "pennylane-quantuminspire": (
        "0.15.5",
        "0f7a6fffd39613bc9e14f6a735cc81cb667803ad",
        (
            "README.md",
            "docs/index.rst",
            "docs/contributing.md",
            "docs/api/modules.rst",
            "docs/getting_started/index.rst",
            "docs/getting_started/installation.md",
            "docs/getting_started/submitting.rst",
            "docs/hybrid/index.rst",
            "docs/hybrid/basics.md",
            "docs/hybrid/leveraging_pennylane.md",
            "docs/hybrid/simple.py",
            "docs/notebooks/index.rst",
            "docs/notebooks/basic_circuit_execution.ipynb",
        ),
    ),
}
OPENAPI = "https://api.quantum-inspire.com/openapi.json"
# Components the release-notes page links, in its order.
GITHUB_RELEASES = (
    "quantuminspire",
    "cQASM-spec",
    "libqasm",
    "OpenSquirrel",
    "OpenQL",
    "qx-simulator",
    "qiskit-quantuminspire",
    "pennylane-quantuminspire",
)
GITLAB_RELEASES = ("quantify-os/quantify-scheduler",)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_CLASSES = {"code-visualizer", "headerlink", "linenos"}
# 403, 429 and 999 come from bot filters, which answer before the resource.
BLOCKED = {403, 429, 999}
USER_AGENT = "Mozilla/5.0 (capture_qi_docs)"
# Pictographs (and their variation selector and joiner) carry no text; the
# rendered Markdown drops them, and the release JSON keeps the escaped originals.
PICTOGRAPH = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f\u200d] ?")


# A scheme-less target whose first segment ends in one of these TLDs names a
# host ("quantify-os.org"), which a browser would wrongly resolve as a path.
BARE_HOST = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.(com|org|net|nl|eu|io|edu|gov|de|uk|ai|dev)([/:?#]|$)")
MARKDOWN_LINK = re.compile(r"(\[[^\]]*\]\()([^\s)]+)(\))")


def absolute(base: str, target: str) -> str:
    """Absolute URL of a link target: a bare host gains https://, a relative path resolves against base."""
    if BARE_HOST.match(target):
        return "https://" + target
    return urllib.parse.urljoin(base, target)


def absolute_links(markdown: str, base: str) -> str:
    """Rewrites every Markdown link target that has no scheme and is not a fragment to an absolute URL."""

    def rewrite(match: re.Match[str]) -> str:
        target = match.group(2)
        if ":" in target or target.startswith("#"):
            return match.group(0)
        return match.group(1) + absolute(base, target) + match.group(3)

    return MARKDOWN_LINK.sub(rewrite, markdown)


class Extract(HTMLParser):
    """Rebuilds the first element whose class list holds one of roots as pandoc-ready HTML.

    Links become absolute against base. Code previews become <pre> blocks
    preceded by a QICODE<lang>Z marker; arithmatex spans become QIMATH<n>Z
    markers whose TeX sits in math; the n-th figure with class
    responsive-image gets images[n] as an <img>.
    """

    def __init__(self, roots: tuple[str, ...], base: str, images: list[tuple[str, str]] | None = None) -> None:
        super().__init__(convert_charrefs=False)
        self.roots = roots
        self.base = base
        self.images = images
        self.figures = 0
        self.parts: list[str] = []
        self.links: list[str] = []
        self.bare: list[str] = []
        self.math: list[tuple[bool, str]] = []
        self.stack: list[str] = []
        self.started = False
        self.done = False
        self.mute = 0
        self.pre = 0
        self.tex: list[str] | None = None

    def emit(self, text: str) -> None:
        if self.tex is not None:
            self.tex.append(text)
        elif not self.mute:
            self.parts.append(text)

    def opening(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        out = [f"<{tag}"]
        for key, value in attrs:
            if value is None:
                continue
            if key in ("href", "src") and not value.startswith(("#", "data:", "mailto:", "javascript:")):
                if BARE_HOST.match(value):
                    self.bare.append(value)
                value = absolute(self.base, value)
                if key == "href":
                    self.links.append(value.split("#")[0])
            out.append(f' {key}="{html.escape(value)}"')
        return "".join(out) + ">"

    def action(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if self.mute or self.tex is not None or classes & SKIP_CLASSES:
            return "mute"
        if "code-preview" in classes:
            lang = values.get("language") or "text"
            code = values.get("initial-doc") or ""
            self.emit(f'<p>QICODE{lang}Z</p><pre><code class="text">{html.escape(code)}</code></pre>')
            return "mute"
        if "arithmatex" in classes:
            return "math-display" if tag == "div" else "math-inline"
        # Line anchors and highlight spans inside <pre> would turn pandoc's
        # code block into inline code; only the text and <code> remain.
        if tag == "pre":
            return "pre"
        if self.pre and tag != "code":
            return "transparent"
        # Pygments line-number tables: the code cell stands alone as a block.
        if tag == "table" and "highlighttable" in classes:
            return "transparent"
        if tag in ("tbody", "tr", "td") and self.stack[-1:] == ["transparent"]:
            return "transparent"
        if tag == "figure" and "responsive-image" in classes and self.images is not None:
            if self.figures < len(self.images):
                url, alt = self.images[self.figures]
                self.emit(f'<p><img src="{html.escape(url)}" alt="{html.escape(alt)}"></p>')
            self.figures += 1
        return "emit"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        if not self.started:
            classes = (dict(attrs).get("class") or "").split()
            if not any(root in classes for root in self.roots):
                return
            self.started = True
            self.parts.append(self.opening(tag, attrs))
            self.stack.append("emit")
            return
        kind = self.action(tag, attrs)
        if kind == "emit" and tag == "code" and self.pre:
            # The class "text" makes pandoc fence the block rather than indent it.
            self.emit('<code class="text">')
        elif kind in ("emit", "pre"):
            self.emit(self.opening(tag, attrs))
        if tag in VOID:
            return
        if kind == "mute":
            self.mute += 1
        elif kind == "pre":
            self.pre += 1
        elif kind.startswith("math"):
            self.tex = []
        self.stack.append(kind)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.started and not self.done and self.action(tag, attrs) == "emit":
            self.emit(self.opening(tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        if not self.started or self.done or tag in VOID or not self.stack:
            return
        kind = self.stack.pop()
        if kind == "mute":
            self.mute -= 1
        elif kind.startswith("math") and self.tex is not None:
            tex = html.unescape("".join(self.tex)).strip()
            for opener, closer in (("\\(", "\\)"), ("\\[", "\\]")):
                if tex.startswith(opener) and tex.endswith(closer):
                    tex = tex[2:-2].strip()
            self.tex = None
            display = kind == "math-display"
            self.math.append((display, tex))
            marker = f"QIMATH{len(self.math) - 1}Z"
            self.emit(f"<p>{marker}</p>" if display else marker)
        elif kind in ("emit", "pre"):
            self.pre -= kind == "pre"
            self.emit(f"</{tag}>")
        self.done = not self.stack

    def handle_data(self, data: str) -> None:
        if self.started and not self.done:
            self.emit(data)

    def handle_entityref(self, name: str) -> None:
        if self.started and not self.done:
            self.emit(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.started and not self.done:
            self.emit(f"&#{name};")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def request(url: str, method: str = "GET", accept: str | None = None) -> urllib.request.Request:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers, method=method)


def fetch(url: str, accept: str | None = None) -> bytes:
    with urllib.request.urlopen(request(url, accept=accept), timeout=60) as response:
        data: bytes = response.read()
    return data


def fetch_status(url: str) -> tuple[int, bytes]:
    """GET url, retrying a 5xx answer once; returns the final status and body."""
    status = 0
    for _ in range(2):
        try:
            return 200, fetch(url)
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            if status < 500:
                break
    return status, b""


# compute.quantum-inspire.com redirects through a cookie-setting login hop,
# which loops for a client that drops cookies.
LINK_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())


def link_status(url: str) -> str:
    """Status of one link: the HTTP code, blocked:<code> for a bot filter, or error:<reason>.

    HEAD comes first; a GET follows any HEAD failure, and a 5xx GET is retried once.
    """
    last = "error:unreached"
    for method in ("HEAD", "GET", "GET"):
        try:
            with LINK_OPENER.open(request(url, method=method), timeout=30) as response:
                return str(response.status)
        except urllib.error.HTTPError as error:
            last = f"blocked:{error.code}" if error.code in BLOCKED else str(error.code)
            error.close()
            if method == "GET" and error.code < 500:
                return last
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last = f"error:{getattr(error, 'reason', error)}"
    return last


def to_markdown(fragment: str, math: list[tuple[bool, str]]) -> str:
    markdown = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
        input=fragment,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # Inline SVG icons arrive as base64 data URIs and carry no text.
    markdown = re.sub(r"!\[\]\(data:image/[^)]*\)", "", markdown)
    markdown = PICTOGRAPH.sub("", markdown)
    # pandoc's GFM writer drops a fence language it cannot highlight, so the
    # language travels in a marker paragraph ahead of the block.
    markdown = re.sub(r"QICODE([\w-]+)Z\n\n(`{3,}|~{3,})[^\n]*\n", r"\2\1\n", markdown)

    def display(match: re.Match[str]) -> str:
        return f"```math\n{math[int(match.group(1))][1]}\n```"

    def inline(match: re.Match[str]) -> str:
        return f"$`{math[int(match.group(1))][1]}`$"

    markdown = re.sub(r"^QIMATH(\d+)Z$", display, markdown, flags=re.M)
    return re.sub(r"QIMATH(\d+)Z", inline, markdown)


def header(url: str, stamp: str, flag: str, data: bytes, extra: str = "") -> str:
    return (
        f"> Full piece: [{url}]({url})\n"
        f"> Retrieved {stamp} by scripts/capture_qi_docs.py {flag} (urllib, pandoc);\n"
        f"> fetched HTML sha256 {sha256(data)}{extra}.\n\n"
    )


def nuxt_images(page: str) -> list[tuple[str, str]]:
    """(url, title or alt) of every ImageRecord in the page's __NUXT_DATA__ payload, in payload order."""
    match = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    if not match:
        return []
    payload = json.loads(match.group(1))

    def value(index: Any) -> Any:
        return payload[index] if isinstance(index, int) and 0 <= index < len(payload) else None

    images = []
    for item in payload:
        if not isinstance(item, dict) or value(item.get("__typename")) != "ImageRecord":
            continue
        image = value(item.get("image"))
        if not isinstance(image, dict):
            continue
        url = value(image.get("url"))
        text = value(image.get("title")) or value(image.get("alt")) or ""
        if isinstance(url, str):
            images.append((url, str(text)))
    return images


def page_url(page: str) -> str:
    return f"{SITE}/{page}/" if page else f"{SITE}/"


def site_targets(base: str, page: str) -> set[str]:
    """Site paths every href of a page reaches, static assets excluded."""
    out = set()
    for href in re.findall(r'href="([^"]*)"', page):
        url = absolute(base, html.unescape(href))
        if not url.startswith(SITE + "/"):
            continue
        path = url[len(SITE) :].split("#")[0].split("?")[0].strip("/")
        if not SITE_ASSET.search(path):
            out.add(path)
    return out


def audit_links(referrers: dict[str, set[str]], known: dict[str, int]) -> list[dict[str, Any]]:
    rows = []
    for url in sorted(referrers):
        if not url.startswith("http"):
            continue
        status = str(known[url]) if url in known else link_status(url)
        rows.append({"url": url, "status": status, "referrers": sorted(referrers[url])})
    return rows


def unreachable(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if not row["status"].startswith(("2", "blocked"))]


def dead_pages(statuses: dict[str, int], nav: dict[str, set[str]]) -> list[dict[str, Any]]:
    return [
        {"url": url, "status": str(statuses[url]), "referrers": sorted(nav.get(url, set()))}
        for url in sorted(statuses)
        if statuses[url] != 200
    ]


def capture_site() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = BASE / "site"
    out.mkdir(parents=True, exist_ok=True)
    stamp = now()
    queue = list(SITE_SEEDS)
    seen: set[str] = set()
    nav: dict[str, set[str]] = {}
    statuses: dict[str, int] = {}
    pages: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    body_links: dict[str, set[str]] = {}
    while queue:
        page = queue.pop(0)
        if page in seen:
            continue
        seen.add(page)
        url = page_url(page)
        status, data = fetch_status(url)
        statuses[url] = status
        record: dict[str, Any] = {"page": page, "url": url, "status": status}
        pages.append(record)
        if status != 200:
            print(f"{page or '/'}: HTTP {status}")
            continue
        text = data.decode("utf-8")
        for target in sorted(site_targets(url, text)):
            nav.setdefault(page_url(target), set()).add(url)
            if target not in seen:
                queue.append(target)
        images = nuxt_images(text)
        figures = len(re.findall(r'<figure class="responsive-image[" ]', text))
        for root in CONTENT_CLASSES:
            parser = Extract((root,), url, images if images and len(images) == figures else None)
            parser.feed(text)
            if parser.done and re.sub(r"<[^>]*>|\s", "", "".join(parser.parts)):
                break
        else:
            record["uncaptured"] = "no content element with text"
            continue
        record["content_class"] = root
        if figures:
            record["figures"] = figures
            if parser.images is not None:
                record["figure_images"] = "mapped"
            else:
                record["figure_images"] = f"unmapped ({len(images)} ImageRecords)"
                record["payload_assets"] = sorted(set(re.findall(r'"(https://www\.datocms-assets\.com/[^"?]+)', text)))
        markdown = to_markdown("".join(parser.parts), parser.math)
        path = out / f"{(page or 'home').replace('/', '_')}.md"
        path.write_text(header(url, stamp, "--site", data) + markdown, encoding="utf-8")
        record["path"] = path.relative_to(ROOT).as_posix()
        for link in parser.links:
            body_links.setdefault(link, set()).add(url)
        if parser.bare:
            record["bare_host_links"] = sorted(set(parser.bare))
        rows.append({"path": record["path"], "source": url, "sha256": sha256(path.read_bytes())})
        print(f"{page or '/'}: {len(markdown)} characters")
    # Documents Quantum Inspire hosts itself (the conditions of use, fact
    # sheets) are identified by digest and size; their bytes stay with the
    # publisher, since the source library admits a retained PDF only with
    # rights evidence.
    documents = []
    for link in sorted(body_links):
        if link.startswith(ASSET_HOST) and link.endswith(".pdf"):
            data = fetch(link)
            documents.append(
                {"url": link, "sha256": sha256(data), "bytes": len(data), "referrers": sorted(body_links[link])}
            )
            print(f"document {link.rsplit('/', 1)[1]}: {len(data)} bytes")
    links = audit_links(body_links, statuses)
    rows.sort(key=lambda row: row["path"])
    return rows, {
        "seeds": len(SITE_SEEDS),
        "hosted_documents": documents,
        "discovered_beyond_seed": sorted(p for p in seen if p not in SITE_SEEDS),
        "pages": sorted(pages, key=lambda p: p["page"]),
        "unreachable": dead_pages(statuses, nav),
        "body_links": links,
        "body_links_unreachable": unreachable(links),
    }


def spec_page(url: str) -> str | None:
    """Canonical spec page URL for a link, or None outside SPEC_BASE."""
    url = url.split("#")[0].split("?")[0]
    if not url.startswith(SPEC_BASE):
        return None
    if url.endswith("/"):
        url += "index.html"
    return url if url.endswith(".html") else None


def capture_spec() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = BASE / "cqasm-spec"
    stamp = now()
    pages_commit = json.loads(fetch(f"https://api.github.com/repos/{SPEC_REPO}/branches/gh-pages"))["commit"]["sha"]
    queue = [SPEC_BASE + "index.html"]
    seen: set[str] = set()
    statuses: dict[str, int] = {}
    nav: dict[str, set[str]] = {}
    body_links: dict[str, set[str]] = {}
    rows: list[dict[str, Any]] = []
    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        status, data = fetch_status(url)
        statuses[url] = status
        if status != 200:
            print(f"spec {url}: HTTP {status}")
            continue
        text = data.decode("utf-8")
        for href in re.findall(r'href="([^"]*)"', text):
            target = spec_page(urllib.parse.urljoin(url, html.unescape(href)))
            if target:
                nav.setdefault(target, set()).add(url)
                if target not in seen:
                    queue.append(target)
        parser = Extract(("md-content__inner",), url)
        parser.feed(text)
        if not parser.done:
            raise SystemExit(f"{url}: no md-content__inner element")
        markdown = to_markdown("".join(parser.parts), parser.math)
        relative = url[len(SPEC_BASE) :].removesuffix(".html") + ".md"
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        built = f";\n> site built from {SPEC_REPO} gh-pages commit {pages_commit}"
        path.write_text(header(url, stamp, "--spec", data, built) + markdown, encoding="utf-8")
        for link in parser.links:
            if not spec_page(link):
                body_links.setdefault(link, set()).add(url)
        rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(path.read_bytes())})
        print(f"spec {relative}: {len(markdown)} characters")
    links = audit_links(body_links, statuses)
    rows.sort(key=lambda row: row["path"])
    return rows, {
        "gh_pages_commit": pages_commit,
        "unreachable": dead_pages(statuses, nav),
        "external_links": links,
        "external_links_unreachable": unreachable(links),
    }


def capture_sdk() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = BASE / "sdk"
    rows = []
    for repo, (_, commit, files) in SDK_REPOS.items():
        for name in files:
            url = f"https://raw.githubusercontent.com/QuTech-Delft/{repo}/{commit}/{urllib.parse.quote(name)}"
            data = fetch(url)
            # The quantuminspire README keeps the path guides already cite.
            path = out / name if repo == "quantuminspire" else out / repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            rows.append({"path": path.relative_to(ROOT).as_posix(), "source": url, "sha256": sha256(data)})
            print(f"sdk {repo}/{name}: {len(data)} bytes")
    repos = {repo: {"tag": tag, "commit": commit} for repo, (tag, commit, _) in SDK_REPOS.items()}
    return rows, {"repos": repos}


def capture_api() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = BASE / "api"
    out.mkdir(parents=True, exist_ok=True)
    data = fetch(OPENAPI)
    path = out / "openapi.json"
    path.write_bytes(data)
    print(f"api/openapi.json: {len(data)} bytes")
    return [{"path": path.relative_to(ROOT).as_posix(), "source": OPENAPI, "sha256": sha256(data)}], {}


def github_releases(repo: str) -> list[dict[str, Any]]:
    releases: list[dict[str, Any]] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/QuTech-Delft/{repo}/releases?per_page=100&page={page}"
        batch = json.loads(fetch(url, accept="application/vnd.github+json"))
        releases.extend(
            {
                "name": item.get("name") or item["tag_name"],
                "tag": item["tag_name"],
                "date": item.get("published_at") or item.get("created_at") or "",
                "prerelease": bool(item.get("prerelease")),
                "url": item["html_url"],
                "body": item.get("body") or "",
            }
            for item in batch
        )
        if len(batch) < 100:
            return releases
        page += 1


def gitlab_releases(project: str) -> list[dict[str, Any]]:
    releases: list[dict[str, Any]] = []
    page = 1
    quoted = urllib.parse.quote(project, safe="")
    while True:
        url = f"https://gitlab.com/api/v4/projects/{quoted}/releases?per_page=100&page={page}"
        batch = json.loads(fetch(url))
        releases.extend(
            {
                "name": item.get("name") or item["tag_name"],
                "tag": item["tag_name"],
                "date": item.get("released_at") or item.get("created_at") or "",
                "prerelease": bool(item.get("upcoming_release")),
                "url": f"https://gitlab.com/{project}/-/releases/{urllib.parse.quote(item['tag_name'])}",
                "body": item.get("description") or "",
            }
            for item in batch
        )
        if len(batch) < 100:
            return releases
        page += 1


def render_releases(name: str, page: str, stamp: str, releases: list[dict[str, Any]], tree: str) -> str:
    """Release bodies verbatim except relative links, which resolve against tree/<tag>/, and pictographs."""
    lines = [
        f"> Full piece: [{page}]({page})\n"
        f"> Retrieved {stamp} by scripts/capture_qi_docs.py --releases (urllib, REST API);\n"
        f"> {len(releases)} releases, newest first, bodies verbatim; data in [{name}.json]({name}.json).\n",
        f"# {name} releases\n",
    ]
    for item in releases:
        flag = " (pre-release)" if item["prerelease"] else ""
        lines.append(f"## {item['name']}\n\nTag `{item['tag']}`, {item['date']}{flag}: <{item['url']}>\n")
        if item["body"].strip():
            body = item["body"].replace("\r\n", "\n").strip()
            body = PICTOGRAPH.sub("", absolute_links(body, f"{tree}/{urllib.parse.quote(item['tag'])}/"))
            lines.append(body + "\n")
    return "\n".join(lines)


def capture_releases() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = BASE / "releases"
    out.mkdir(parents=True, exist_ok=True)
    stamp = now()
    rows = []
    sources: list[tuple[str, str, str, Callable[[], list[dict[str, Any]]]]] = []
    for repo in GITHUB_RELEASES:
        home = f"https://github.com/QuTech-Delft/{repo}"
        sources.append((repo, f"{home}/releases", f"{home}/blob", partial(github_releases, repo)))
    for project in GITLAB_RELEASES:
        home = f"https://gitlab.com/{project}"
        sources.append(
            (project.split("/")[-1], f"{home}/-/releases", f"{home}/-/blob", partial(gitlab_releases, project))
        )
    for name, page, tree, read in sources:
        releases = sorted(read(), key=lambda item: (item["date"], item["tag"]), reverse=True)
        doc = {"component": name, "source": page, "retrieved_utc": stamp, "releases": releases}
        json_path = out / f"{name}.json"
        json_path.write_bytes((json.dumps(doc, indent=1) + "\n").encode("ascii"))
        md_path = out / f"{name}.md"
        md_path.write_text(render_releases(name, page, stamp, releases, tree), encoding="utf-8")
        for path in (json_path, md_path):
            rows.append(
                {"path": path.relative_to(ROOT).as_posix(), "source": page, "sha256": sha256(path.read_bytes())}
            )
        print(f"releases {name}: {len(releases)}")
    return rows, {}


def manifest_path(kind: str, base: Path = BASE) -> Path:
    return base / ("cqasm-spec" if kind == "spec" else kind) / "MANIFEST.json"


def write_manifest(kind: str, rows: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    doc: dict[str, Any] = {"schema": "qi-docs-capture-v2", "kind": kind, "retrieved_utc": now(), "files": rows}
    doc.update(extra)
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def captured_files(base: Path, kind: str, root: Path) -> set[str]:
    """Root-relative path of every file under a kind's directory except its manifest."""
    manifest = manifest_path(kind, base)
    directory = manifest.parent
    return {path.relative_to(root).as_posix() for path in directory.rglob("*") if path.is_file() and path != manifest}


def expected_paths(kind: str, doc: dict[str, Any], base: Path, root: Path) -> set[str]:
    """Paths the capture defines for a kind, from the fixed lists or the crawl the manifest records."""
    prefix = base.relative_to(root).as_posix()
    if kind == "sdk":
        repos = {repo: {"tag": tag, "commit": commit} for repo, (tag, commit, _) in SDK_REPOS.items()}
        if doc.get("repos") != repos:
            raise SystemExit("sdk manifest repos differ from SDK_REPOS")
        return {
            f"{prefix}/sdk/{name}" if repo == "quantuminspire" else f"{prefix}/sdk/{repo}/{name}"
            for repo, (_, _, files) in SDK_REPOS.items()
            for name in files
        }
    if kind == "api":
        return {f"{prefix}/api/openapi.json"}
    if kind == "releases":
        names = [*GITHUB_RELEASES, *(project.split("/")[-1] for project in GITLAB_RELEASES)]
        return {f"{prefix}/releases/{name}.{ext}" for name in names for ext in ("json", "md")}
    if kind == "spec":
        # The crawl follows navigation links, so the page set is the one the manifest rows name;
        # each row's path must be the one its source URL maps to.
        out = set()
        for row in doc["files"]:
            if not row["source"].startswith(SPEC_BASE):
                raise SystemExit(f"{row['path']}: source {row['source']} lies outside the spec site")
            relative = row["source"][len(SPEC_BASE) :].removesuffix(".html") + ".md"
            if row["path"] != f"{prefix}/cqasm-spec/{relative}":
                raise SystemExit(f"{row['path']} does not match its source {row['source']}")
            out.add(row["path"])
        listed = {row["source"] for row in doc["files"]}
        for item in (*doc["unreachable"], *doc["external_links"]):
            for referrer in item["referrers"]:
                if referrer not in listed:
                    raise SystemExit(f"spec referrer {referrer} has no captured page")
        return out
    pages = doc["pages"]
    names = [record["page"] for record in pages]
    if doc["seeds"] != len(SITE_SEEDS) or set(names) != set(SITE_SEEDS) | set(doc["discovered_beyond_seed"]):
        raise SystemExit("site manifest crawl set differs from SITE_SEEDS and its discovered pages")
    if len(set(names)) != len(names):
        raise SystemExit("site manifest lists a crawled page twice")
    out = set()
    for record in pages:
        page = record["page"]
        if record["status"] != 200 or "uncaptured" in record:
            if "path" in record:
                raise SystemExit(f"site page {page or '/'} records a failed capture with a path")
            continue
        if "path" not in record:
            raise SystemExit(f"site page {page or '/'} records a successful capture without a path")
        stem = (page or "home").replace("/", "_")
        if record["url"] != page_url(page) or record["path"] != f"{prefix}/site/{stem}.md":
            raise SystemExit(f"site page {page or '/'} records an inconsistent url or path")
        out.add(record["path"])
    return out


def check_tree(root: Path) -> int:
    """Verifies every kind under root: file set, manifest paths, defined inventory and sha256."""
    base = root / BASE.relative_to(ROOT)
    count = 0
    for kind in KINDS:
        doc = json.loads(manifest_path(kind, base).read_text(encoding="utf-8"))
        rows = [row["path"] for row in doc["files"]]
        listed = set(rows)
        if len(listed) != len(rows):
            raise SystemExit(f"{kind} manifest lists a path twice")
        present = captured_files(base, kind, root)
        if unlisted := sorted(present - listed):
            raise SystemExit(f"{kind}: file {unlisted[0]} is not listed in its manifest")
        if absent := sorted(listed - present):
            raise SystemExit(f"{kind}: manifest row {absent[0]} has no captured file")
        expected = expected_paths(kind, doc, base, root)
        if missing := sorted(expected - listed):
            raise SystemExit(f"{kind}: captured inventory path {missing[0]} has no manifest row")
        if extra := sorted(listed - expected):
            raise SystemExit(f"{kind}: manifest row {extra[0]} is outside the captured inventory")
        for row in doc["files"]:
            data = (root / row["path"]).read_bytes()
            if sha256(data) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            count += 1
    return count


def check() -> int:
    count = check_tree(ROOT)
    print(f"quantum inspire docs: {count} captured files match their manifests")
    return 0


def self_test() -> int:
    """Runs check_tree on a temporary copy of the retained capture and requires each mutation to fail."""
    cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = root / BASE.relative_to(ROOT)
        shutil.copytree(BASE, base)
        check_tree(root)

        def expect(label: str, fragment: str) -> None:
            nonlocal cases
            try:
                check_tree(root)
            except SystemExit as error:
                if fragment not in str(error):
                    raise SystemExit(f"self-test {label}: rejected with {error!s}, wanted {fragment!r}") from error
            else:
                raise SystemExit(f"self-test {label}: mutation passed")
            cases += 1

        def drop_row(kind: str, suffix: str) -> None:
            path = manifest_path(kind, base)
            doc = json.loads(path.read_text(encoding="utf-8"))
            doc["files"] = [row for row in doc["files"] if not row["path"].endswith(suffix)]
            path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")

        for kind, name in (("site", "site/about-qi.md"), ("sdk", "sdk/README.md")):
            victim = base / name
            victim_bytes = victim.read_bytes()
            manifest = manifest_path(kind, base)
            manifest_bytes = manifest.read_bytes()
            victim.unlink()
            expect(f"{kind} file removed", "has no captured file")
            drop_row(kind, "/" + name)
            expect(f"{kind} file and manifest row removed", "has no manifest row")
            manifest.write_bytes(manifest_bytes)
            victim.write_bytes(victim_bytes)
            unlisted = victim.parent / "unlisted.md"
            unlisted.write_text("x\n", encoding="utf-8")
            expect(f"{kind} unlisted file added", "is not listed in its manifest")
            unlisted.unlink()
            victim.write_bytes(victim_bytes + b"!")
            expect(f"{kind} file altered", "differs from its captured sha256")
            victim.write_bytes(victim_bytes)
        manifest = manifest_path("site", base)
        manifest_bytes = manifest.read_bytes()
        doc = json.loads(manifest_bytes)
        record = next(record for record in doc["pages"] if "path" in record)
        del record["path"]
        manifest.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        expect("site page record without its path", "successful capture without a path")
        manifest.write_bytes(manifest_bytes)
        nested = base / "site" / "nested" / "MANIFEST.json"
        nested.parent.mkdir()
        nested.write_text("{}\n", encoding="utf-8")
        expect("unlisted nested manifest", "is not listed in its manifest")
        shutil.rmtree(nested.parent)
        check_tree(root)
    print(f"capture_qi_docs self-test: {cases} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    for kind in KINDS:
        parser.add_argument(f"--{kind}", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    if args.self_test:
        return self_test()
    chosen = [kind for kind in KINDS if getattr(args, kind)]
    if not chosen:
        parser.error("give --site, --spec, --sdk, --api, --releases, --check or --self-test")
    capture: dict[str, Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]]] = {
        "site": capture_site,
        "spec": capture_spec,
        "sdk": capture_sdk,
        "api": capture_api,
        "releases": capture_releases,
    }
    for kind in chosen:
        rows, extra = capture[kind]()
        write_manifest(kind, rows, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
