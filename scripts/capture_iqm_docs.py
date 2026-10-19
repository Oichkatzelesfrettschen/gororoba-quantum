"""Capture IQM's OS 4.7 documentation, package metadata and client changelog as the reference the IQM guide cites.

Three sources, each retained with its identity:

- ``--docs`` fetches, for each package of DOCS_PACKAGES, the Sphinx inventory
  https://docs.iqm.tech/4.7/<package>/objects.inv (retained byte for byte as
  docs/<package>/objects.inv; its header version must equal the pinned
  release) and then every page its ``std:doc`` entries name, keeps the
  ``bd-article`` (pydata theme) or ``main`` (furo theme) article without its
  permalink anchors, converts it to GitHub Markdown with pandoc, and writes
  docs/<package>/<docname>.md under a header naming the URL, the retrieval
  time and the sha256 of the fetched HTML. The unversioned docs.iqm.tech/<package>/
  path serves another release, so every URL carries the /4.7/ prefix.
- ``--pypi`` retains the PyPI JSON metadata of each pinned release of
  CONSTRAINTS (the IQM OS 4.7.0 client constraints plus the integration
  pins): requirements, classifiers, project URLs and every distribution
  file's URL, upload time, size and sha256, as pypi/<name>.json.
- ``--changelog`` downloads the iqm-client sdist named in pypi/iqm-client.json,
  verifies its sha256 against that record, and retains its CHANGELOG.md as
  changelog/iqm-client-<version>.md under a header naming the sdist URL and
  both sha256 values.

Each kind writes MANIFEST.json (path, source URL, sha256, and every page that
answered with an error) and prunes files its new rows no longer name.
``--check`` verifies, without network access, that each kind's file set equals
its manifest rows, that the rows equal the fixed inventory (for docs, the
``std:doc`` set of the retained inventories), that each row names its pinned
source, and that every file matches its sha256. ``--self-test`` proves on a
temporary copy that the check rejects a removed page, a removed page with its
row, an unlisted file, an altered file, a moved source and an inventory entry
that has no row.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/iqm"
KINDS = ("docs", "pypi", "changelog")
DOCS = "https://docs.iqm.tech/4.7/"
PYPI = "https://pypi.org/pypi/"
USER_AGENT = "Mozilla/5.0 (capture_iqm_docs)"
WORKERS = 8
ATTEMPTS = 6
CONSTRAINTS_FILE = "constraints-iqm-qccsw-4.7.0.txt"
CONSTRAINTS_HEADER = (
    "# IQM OS 4.7.0 client constraints from the IQM Resonance release notification of 2026-10-16,\n"
    "# followed by the qiskit, qiskit-aer, cirq-core, qrisp and mthree integration pins.\n"
)
CHANGELOG_PACKAGE = ("iqm-client", "36.0.0")

# Release of each package whose objects.inv header must report this version.
DOCS_PACKAGES = (
    ("iqm-client", "36.0.0"),
    ("iqm-pulla", "15.0.0"),
    ("iqm-pulse", "15.0.0"),
    ("iqm-benchmarks", "3.0.0"),
    ("iqm-qaoa", "3.0.0"),
    ("iqm-qubit-selector", "1.2.0"),
    ("iqm-error-reduction-tools", "0.3.0"),
    ("iqm-station-control-client", "14.0.0"),
    ("iqm-exa-common", "29.0.0"),
    ("iqm-data-definitions", "3.1.0"),
)
CONSTRAINTS = (
    *DOCS_PACKAGES,
    ("qiskit", "2.1.2"),
    ("qiskit-aer", "0.17.2"),
    ("cirq-core", "1.7.0"),
    ("qrisp", "0.9.10"),
    ("mthree", "3.0.0"),
)
PYPI_INFO = ("name", "version", "summary", "requires_python", "requires_dist", "classifiers", "project_urls")

INVENTORY_ENTRY = re.compile(r"^(?P<name>.+?) +std:doc +(?P<priority>-?\d+) +(?P<uri>\S+) +(?P<display>.*)$")
HEADERLINK = re.compile(r'<a class="headerlink"[^>]*>.*?</a>', re.S)
VIEWCODE = re.compile(r'<a class="reference internal" href="[^"]*_modules/[^"]*"[^>]*>.*?</a>', re.S)
CODE_BLOCK = re.compile(
    r'<div class="highlight(?:-([\w+-]+))?[^"]*">\s*<div class="highlight"><pre>(.*?)</pre></div>\s*</div>'
    r'|<div class="highlight"><pre>(.*?)</pre></div>',
    re.S,
)
SPAN = re.compile(r"</?span\b[^>]*>")
STRIP_ELEMENTS = ("script", "style", "svg", "noscript", "template", "button")
MARKDOWN_LINK = re.compile(r"(\]\()([^\s)]+)((?:\s+\"[^\"]*\")?\))")
PICTOGRAPH = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f\u200d] ?")
ARTICLES = (
    re.compile(r'<article class="bd-article">(.*?)</article>', re.S),
    re.compile(r'<article role="main"[^>]*>(.*?)</article>', re.S),
    re.compile(r'<div itemprop="articleBody">(.*?)</div>\s*<footer', re.S),
)
CODE_ARTIFACT = b"(#__codelineno-"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def fetch_status(url: str) -> tuple[int, bytes, str]:
    """GET url, retrying 429, 5xx and transport failures with backoff; returns the status, body and final URL."""
    status = 0
    for attempt in range(ATTEMPTS):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return 200, response.read(), response.geturl()
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            if status != 429 and status < 500:
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            status = 0
        time.sleep(2**attempt)
    return status, b"", url


def fetch(url: str) -> bytes:
    status, data, _ = fetch_status(url)
    if status != 200:
        raise SystemExit(f"{url}: HTTP {status}")
    return data


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def header(url: str, stamp: str, flag: str, data: bytes) -> str:
    return (
        f"> Full piece: [{url}]({url})\n"
        f"> Retrieved {stamp} by scripts/capture_iqm_docs.py {flag} (urllib, pandoc);\n"
        f"> fetched HTML sha256 {sha256(data)}.\n\n"
    )


def absolute_links(markdown: str, base: str) -> str:
    """Resolves every relative Markdown link target against the page URL."""

    def resolve(match: re.Match[str]) -> str:
        target = match.group(2)
        if re.match(r"^([a-z][a-z0-9+.-]*:|#)", target):
            return match.group(0)
        return match.group(1) + urllib.parse.urljoin(base, target) + match.group(3)

    return MARKDOWN_LINK.sub(resolve, markdown)


def to_markdown(fragment: str) -> str:
    markdown = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
        input=fragment,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    markdown = re.sub(r"!\[\]\(data:image/[^)]*\)", "", markdown)
    return PICTOGRAPH.sub("", markdown)


def plain_code(match: re.Match[str]) -> str:
    """A Pygments block as one <pre><code> of its source text, which pandoc writes as a fence."""
    language = match.group(1) or "text"
    language = "text" if language == "default" else language
    source = html.unescape(re.sub(r"<[^>]+>", "", match.group(2) or match.group(3)))
    return f'<pre><code class="{language}">{html.escape(source)}</code></pre>'


def docs_fragment(page: str) -> str:
    """The article element of a Sphinx page without permalinks, source links, scripts and highlight markup."""
    for pattern in ARTICLES:
        found = pattern.findall(page)
        if len(found) == 1:
            fragment = HEADERLINK.sub("", found[0])
            for name in STRIP_ELEMENTS:
                fragment = re.sub(rf"<{name}\b.*?</{name}>", "", fragment, flags=re.S | re.I)
            # Sphinx wraps each inline-code token in <span class="pre">; pandoc splits those into adjacent code runs.
            return SPAN.sub("", CODE_BLOCK.sub(plain_code, VIEWCODE.sub("", fragment)))
    raise SystemExit("docs page carries no single article element")


def manifest_path(kind: str, base: Path = BASE) -> Path:
    return base / kind / "MANIFEST.json"


def pypi_url(name: str, version: str) -> str:
    return f"{PYPI}{name}/{version}/json"


def parse_inventory(data: bytes) -> tuple[str, list[tuple[str, str]]]:
    """Version and (docname, uri) of every ``std:doc`` entry of a Sphinx v2 inventory."""
    lines = data.split(b"\n", 4)
    if len(lines) < 5 or lines[0] != b"# Sphinx inventory version 2":
        raise SystemExit("objects.inv is not a Sphinx version 2 inventory")
    version = lines[2].decode("utf-8").removeprefix("# Version: ").strip()
    entries = []
    for line in zlib.decompress(lines[4]).decode("utf-8").splitlines():
        match = INVENTORY_ENTRY.match(line)
        if not match:
            continue
        name = match.group("name")
        uri = match.group("uri").replace("$", name)
        if name.startswith("/") or ".." in name.split("/") or uri.startswith("/") or "#" in uri:
            raise SystemExit(f"objects.inv names an unsafe document {name!r}")
        entries.append((name, uri))
    if len({name for name, _ in entries}) != len(entries):
        raise SystemExit("objects.inv names a document twice")
    return version, entries


def package_dir(package: str, base: Path = BASE) -> Path:
    return base / "docs" / package


def page_path(package: str, docname: str, base: Path = BASE) -> Path:
    return package_dir(package, base) / f"{docname}.md"


def docs_inventory(base: Path, root: Path) -> dict[str, str]:
    """Root-relative path to pinned source URL of every docs file, from the retained inventories."""
    pinned: dict[str, str] = {}
    for package, version in DOCS_PACKAGES:
        inv = package_dir(package, base) / "objects.inv"
        if not inv.is_file():
            raise SystemExit(f"docs: {rel(inv, root)} is missing")
        found, entries = parse_inventory(inv.read_bytes())
        if found != version:
            raise SystemExit(f"docs: {package} objects.inv reports version {found}, pinned {version}")
        pinned[rel(inv, root)] = f"{DOCS}{package}/objects.inv"
        for docname, uri in entries:
            pinned[rel(page_path(package, docname, base), root)] = f"{DOCS}{package}/{uri}"
    return pinned


def render_page(flag: str, stamp: str, task: tuple[str, Path]) -> tuple[str, Path, int, str | None]:
    url, path = task
    status, data, final = fetch_status(url)
    if status != 200:
        return url, path, status, None
    # A redirect off the pinned release would file another release's page under this one.
    if not final.startswith(DOCS):
        raise SystemExit(f"{url}: redirected to {final}, outside {DOCS}")
    text = header(url, stamp, flag, data) + absolute_links(to_markdown(docs_fragment(data.decode("utf-8"))), final)
    return url, path, 200, text


def capture_docs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    rows: list[dict[str, Any]] = []
    unreachable: list[dict[str, Any]] = []
    tasks: list[tuple[str, Path]] = []
    packages = []
    for package, version in DOCS_PACKAGES:
        url = f"{DOCS}{package}/objects.inv"
        data = fetch(url)
        found, entries = parse_inventory(data)
        if found != version:
            raise SystemExit(f"{url}: reports version {found}, pinned {version}")
        inv = package_dir(package) / "objects.inv"
        inv.parent.mkdir(parents=True, exist_ok=True)
        inv.write_bytes(data)
        rows.append({"path": rel(inv), "source": url, "sha256": sha256(data)})
        packages.append({"package": package, "version": version, "pages": len(entries)})
        tasks += [(f"{DOCS}{package}/{uri}", page_path(package, docname)) for docname, uri in entries]
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for url, path, status, text in pool.map(partial(render_page, "--docs", stamp), tasks):
            if text is None:
                unreachable.append({"url": url, "status": status})
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            rows.append({"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())})
    return rows, {"unreachable": unreachable, "packages": packages}


def constraint_lines() -> list[str]:
    return [f"{name}=={version}" for name, version in CONSTRAINTS]


def write_constraints() -> None:
    (BASE / CONSTRAINTS_FILE).write_text(CONSTRAINTS_HEADER + "".join(f"{line}\n" for line in constraint_lines()))


def capture_pypi() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    write_constraints()
    rows = []
    for name, version in CONSTRAINTS:
        url = pypi_url(name, version)
        doc = json.loads(fetch(url))
        record = {key: doc["info"].get(key) for key in PYPI_INFO}
        record["files"] = [
            {
                "filename": item["filename"],
                "packagetype": item["packagetype"],
                "url": item["url"],
                "upload_time_iso_8601": item["upload_time_iso_8601"],
                "size": item["size"],
                "sha256": item["digests"]["sha256"],
            }
            for item in sorted(doc["urls"], key=lambda item: item["filename"])
        ]
        path = BASE / "pypi" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        rows.append({"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())})
    return rows, {"unreachable": []}


def sdist_record(base: Path) -> dict[str, Any]:
    """The sdist file record of the changelog package in the retained pypi/<name>.json."""
    name, version = CHANGELOG_PACKAGE
    path = base / "pypi" / f"{name}.json"
    if not path.is_file():
        raise SystemExit(f"changelog: {name} PyPI record is missing")
    sdists = [item for item in json.loads(path.read_text(encoding="utf-8"))["files"] if item["packagetype"] == "sdist"]
    if len(sdists) != 1 or version not in sdists[0]["filename"]:
        raise SystemExit(f"changelog: {name} PyPI record carries no single {version} sdist")
    return dict(sdists[0])


def changelog_path(base: Path = BASE) -> Path:
    name, version = CHANGELOG_PACKAGE
    return base / "changelog" / f"{name}-{version}.md"


def changelog_header(url: str, stamp: str, sdist_sha: str, body_sha: str) -> str:
    return (
        f"> Full piece: [{url}]({url})\n"
        f"> Retrieved {stamp} by scripts/capture_iqm_docs.py --changelog (urllib, tarfile);\n"
        f"> sdist sha256 {sdist_sha}; CHANGELOG.md sha256 {body_sha}.\n\n"
    )


def capture_changelog() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    record = sdist_record(BASE)
    url = record["url"]
    data = fetch(url)
    if sha256(data) != record["sha256"]:
        raise SystemExit(f"{url}: sdist sha256 differs from the PyPI record")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = [
            m
            for m in archive.getmembers()
            if m.isfile() and m.name.count("/") == 1 and m.name.endswith("/CHANGELOG.md")
        ]
        if len(members) != 1:
            raise SystemExit(f"{url}: sdist carries no single top-level CHANGELOG.md")
        extracted = archive.extractfile(members[0])
        if extracted is None:
            raise SystemExit(f"{url}: CHANGELOG.md is unreadable")
        body = extracted.read()
    path = changelog_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(changelog_header(url, now(), record["sha256"], sha256(body)).encode("utf-8") + body)
    return [{"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())}], {"unreachable": []}


def inventory(kind: str, base: Path, root: Path) -> dict[str, str]:
    """Root-relative path to pinned source URL for every file a kind can capture."""
    if kind == "docs":
        return docs_inventory(base, root)
    if kind == "pypi":
        return {rel(base / "pypi" / f"{name}.json", root): pypi_url(name, version) for name, version in CONSTRAINTS}
    return {rel(changelog_path(base), root): sdist_record(base)["url"]}


def captured_files(kind: str, base: Path, root: Path) -> set[str]:
    """Root-relative path of every file under a kind's directory except its manifest."""
    manifest = manifest_path(kind, base)
    return {rel(path, root) for path in manifest.parent.rglob("*") if path.is_file() and path != manifest}


def prune_capture(kind: str, rows: list[dict[str, Any]], base: Path = BASE, root: Path = ROOT) -> None:
    """Removes every file under a kind's directory that the new rows and the manifest do not name."""
    listed = {row["path"] for row in rows}
    for name in captured_files(kind, base, root) - listed:
        (root / name).unlink()
    for path in sorted(manifest_path(kind, base).parent.rglob("*"), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def write_manifest(kind: str, rows: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    rows.sort(key=lambda row: row["path"])
    prune_capture(kind, rows)
    doc: dict[str, Any] = {"schema": "iqm-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    doc.update(extra)
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def check_constraints(base: Path) -> None:
    path = base / CONSTRAINTS_FILE
    if not path.is_file():
        raise SystemExit(f"{CONSTRAINTS_FILE} is missing")
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
    if lines != constraint_lines():
        raise SystemExit(f"{CONSTRAINTS_FILE} differs from the pinned constraints")


def check_changelog(base: Path) -> None:
    """The changelog header must name the sdist sha256 of the PyPI record and the body sha256."""
    record = sdist_record(base)
    data = changelog_path(base).read_bytes()
    head, _, body = data.partition(b"\n\n")
    expected = changelog_header(record["url"], "", record["sha256"], sha256(body)).split("\n")
    lines = head.decode("utf-8").split("\n")
    if lines[0] != expected[0] or lines[2] != expected[2]:
        raise SystemExit("changelog header differs from the PyPI sdist record or the CHANGELOG.md sha256")


def check_tree(root: Path) -> int:
    """Verifies every kind under root: file set, manifest rows, fixed inventory, sources and sha256."""
    base = root / BASE.relative_to(ROOT)
    check_constraints(base)
    count = 0
    for kind in KINDS:
        doc = json.loads(manifest_path(kind, base).read_text(encoding="utf-8"))
        rows = [row["path"] for row in doc["files"]]
        listed = set(rows)
        if len(listed) != len(rows):
            raise SystemExit(f"{kind} manifest lists a path twice")
        present = captured_files(kind, base, root)
        if unlisted := sorted(present - listed):
            raise SystemExit(f"{kind}: file {unlisted[0]} is not listed in its manifest")
        if absent := sorted(listed - present):
            raise SystemExit(f"{kind}: manifest row {absent[0]} has no captured file")
        pinned = inventory(kind, base, root)
        failed = {item["url"] for item in doc["unreachable"]}
        if stray := sorted(failed - set(pinned.values())):
            raise SystemExit(f"{kind}: unreachable entry {stray[0]} is outside the captured inventory")
        expected = {path for path, url in pinned.items() if url not in failed}
        if missing := sorted(expected - listed):
            raise SystemExit(f"{kind}: captured inventory path {missing[0]} has no manifest row")
        if extra := sorted(listed - expected):
            raise SystemExit(f"{kind}: manifest row {extra[0]} is outside the captured inventory")
        for row in doc["files"]:
            if row["source"] != pinned[row["path"]]:
                raise SystemExit(f"{row['path']}: source {row['source']} differs from the pinned {pinned[row['path']]}")
            data = (root / row["path"]).read_bytes()
            if sha256(data) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            if row["path"].endswith(".md") and CODE_ARTIFACT in data:
                raise SystemExit(f"{row['path']}: a code block kept its line anchors instead of a fence")
            count += 1
        if kind == "changelog":
            check_changelog(base)
    return count


def check() -> int:
    count = check_tree(ROOT)
    print(f"iqm docs: {count} captured files match their manifests")
    return 0


def replace_inventory(data: bytes, extra_line: str) -> bytes:
    """The inventory with one more ``std:doc`` line, recompressed."""
    lines = data.split(b"\n", 4)
    body = zlib.decompress(lines[4]) + (extra_line + "\n").encode("utf-8")
    return b"\n".join([*lines[:4], zlib.compress(body)])


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

        def edit_manifest(kind: str, change: Callable[[dict[str, Any]], None]) -> bytes:
            path = manifest_path(kind, base)
            original = path.read_bytes()
            doc = json.loads(original)
            change(doc)
            path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
            return original

        def drop_row(name: str, doc: dict[str, Any]) -> None:
            doc["files"] = [row for row in doc["files"] if row["path"] != name]

        def move_source(name: str, doc: dict[str, Any]) -> None:
            next(row for row in doc["files"] if row["path"] == name)["source"] = "https://example.invalid/"

        for kind, victim in (
            ("docs", page_path("iqm-client", "user_guide_qiskit", base)),
            ("pypi", base / "pypi" / "iqm-client.json"),
            ("changelog", changelog_path(base)),
        ):
            name = rel(victim, root)
            victim_bytes = victim.read_bytes()
            victim.unlink()
            expect(f"{kind} file removed", "has no captured file")
            original = edit_manifest(kind, partial(drop_row, name))
            expect(f"{kind} file and manifest row removed", "has no manifest row")
            manifest_path(kind, base).write_bytes(original)
            victim.write_bytes(victim_bytes)
            unlisted = victim.parent / "unlisted.md"
            unlisted.write_text("x\n", encoding="utf-8")
            expect(f"{kind} unlisted file added", "is not listed in its manifest")
            unlisted.unlink()
            victim.write_bytes(victim_bytes + b"!")
            expect(f"{kind} file altered", "differs from its captured sha256")
            victim.write_bytes(victim_bytes)
            original = edit_manifest(kind, partial(move_source, name))
            expect(f"{kind} row with another source", "differs from the pinned")
            manifest_path(kind, base).write_bytes(original)
        log = changelog_path(base)
        log_bytes = log.read_bytes()
        sdist = sdist_record(base)["sha256"].encode()
        forged = log_bytes.replace(sdist, b"0" * len(sdist), 1)
        log.write_bytes(forged)

        def rehash_log(doc: dict[str, Any]) -> None:
            next(row for row in doc["files"] if row["path"] == rel(log, root))["sha256"] = sha256(forged)

        original = edit_manifest("changelog", rehash_log)
        expect("changelog header naming another sdist", "changelog header differs")
        manifest_path("changelog", base).write_bytes(original)
        log.write_bytes(log_bytes)
        inv = package_dir("iqm-pulse", base) / "objects.inv"
        inv_bytes = inv.read_bytes()
        grown = replace_inventory(inv_bytes, "added_page std:doc -1 added_page.html Added")
        inv.write_bytes(grown)

        def rehash(doc: dict[str, Any]) -> None:
            next(row for row in doc["files"] if row["path"] == rel(inv, root))["sha256"] = sha256(grown)

        original = edit_manifest("docs", rehash)
        expect("inventory entry without a row", "has no manifest row")
        manifest_path("docs", base).write_bytes(original)
        inv.write_bytes(inv_bytes.replace(b"# Version: 15.0.0", b"# Version: 15.0.1", 1))
        grown = inv.read_bytes()
        original = edit_manifest("docs", rehash)
        expect("inventory version moved", "reports version")
        manifest_path("docs", base).write_bytes(original)
        inv.write_bytes(inv_bytes)
        constraints = base / CONSTRAINTS_FILE
        constraints_bytes = constraints.read_bytes()
        constraints.write_bytes(constraints_bytes.replace(b"iqm-pulse==15.0.0", b"iqm-pulse==15.0.1", 1))
        expect("constraints moved", "differs from the pinned constraints")
        constraints.write_bytes(constraints_bytes)
        stray = package_dir("iqm-client", base) / "stray" / "gone.md"
        stray.parent.mkdir()
        stray.write_text("x\n", encoding="utf-8")
        expect("stray docs file", "is not listed in its manifest")
        rows = json.loads(manifest_path("docs", base).read_text(encoding="utf-8"))["files"]
        prune_capture("docs", rows, base, root)
        if stray.exists() or stray.parent.exists():
            raise SystemExit("self-test prune: stray file survived")
        check_tree(root)
        cases += 1
    print(f"capture_iqm_docs self-test: {cases} mutations rejected")
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
        parser.error("give --docs, --pypi, --changelog, --check or --self-test")
    capture: dict[str, Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]]] = {
        "docs": capture_docs,
        "pypi": capture_pypi,
        "changelog": capture_changelog,
    }
    for kind in chosen:
        rows, extra = capture[kind]()
        write_manifest(kind, rows, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
