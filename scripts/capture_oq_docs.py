"""Capture Open Quantum's documentation, site pages, pricing and package metadata as the reference the OQ guides cite.

Four sources, each retained with its identity:

- ``--docs`` fetches every page of docs.openquantum.com that its sitemap lists
  (the fixed tuple DOCS_PAGES; a sitemap naming another set fails the capture),
  keeps the MkDocs ``md-content__inner`` article, converts it to GitHub
  Markdown with pandoc, and writes docs/<path>.md under a header naming the
  URL, the retrieval time and the sha256 of the fetched HTML.
- ``--site`` fetches the www.openquantum.com pages that state account,
  credit, pricing, hardware and attribution facts, plus the Quantum Rings
  terms and privacy pages the site footer links (SITE_PAGES), keeps the
  page body without its navigation, header and footer, and writes
  site/<slug>.md the same way.
- ``--pricing`` decodes the pricing page's Next.js flight data into
  docs/evidence/open_quantum/pricing.json (per-task and per-shot USD
  equivalents for Public and Private Compute per backend) and retains, in
  pricing/sources.json, the page statements and calculator source fragments
  that define what those figures mean: the USD-equivalent notice, the Spark
  allocation, and the authenticated ``/v1/pricing/estimate`` call whose
  quote supplies credits and queue-priority increases. The page publishes no
  credit-to-USD rate; the record states that absence.
- ``--pypi`` retains the PyPI JSON metadata of each pinned package release
  (PYPI_RELEASES): requirements, classifiers, project URLs and every
  distribution file's name, upload time, size and sha256, as pypi/<name>.json.

Each kind writes MANIFEST.json (path, source URL, sha256, and every page that
answered with an error) and prunes files its new rows no longer name.
``--check`` verifies, without network access, that each kind's file set equals
its manifest rows, that the rows equal the fixed inventory, that each row
names its pinned source, and that every file matches its sha256.
``--self-test`` proves on a temporary copy that the check rejects a removed
page, a removed page with its row, an unlisted file, an altered record, a
moved source and an unreachable entry outside the inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/open_quantum"
EVIDENCE = ROOT / "docs/evidence/open_quantum"
KINDS = ("docs", "site", "pricing", "pypi")
DOCS = "https://docs.openquantum.com/"
SITE = "https://www.openquantum.com/"
TERMS_HOST = "https://www.quantumrings.com/"
PYPI = "https://pypi.org/pypi/"
USER_AGENT = "Mozilla/5.0 (capture_oq_docs)"

DOCS_PAGES = (
    "",
    "api-reference/",
    "cirq-plugin/examples/",
    "cirq-plugin/getting-started/",
    "cirq-plugin/overview/",
    "cirq-plugin/supported-operations/",
    "cirq-plugin/troubleshooting/",
    "concepts/backends/",
    "concepts/credits/",
    "concepts/job-lifecycle/",
    "concepts/overview/",
    "core-sdk/authentication/",
    "core-sdk/backend-discovery/",
    "core-sdk/examples/",
    "core-sdk/installation/",
    "core-sdk/job-submission/",
    "core-sdk/overview/",
    "core-sdk/quickstart/",
    "getting-started/resources/",
    "integrations/",
    "mcp/client-setup/",
    "mcp/installation/",
    "mcp/overview/",
    "mcp/tools/",
    "pennylane-plugin/device-options/",
    "pennylane-plugin/overview/",
    "pennylane-plugin/supported-operations/",
    "pennylane-plugin/troubleshooting/",
    "pennylane-plugin/examples/backend-selection/",
    "pennylane-plugin/examples/basic-circuits/",
    "pennylane-plugin/examples/qml-workflow/",
    "pennylane-plugin/examples/vqe/",
    "portal/account/",
    "portal/credits-billing/",
    "portal/monitoring-jobs/",
    "portal/organizations/",
    "portal/overview/",
    "portal/sdk-keys/",
    "portal/submitting-jobs/",
    "qbraid/backends-targets/",
    "qbraid/examples/",
    "qbraid/installation/",
    "qbraid/overview/",
    "qiskit-plugin/backends-targets/",
    "qiskit-plugin/examples/",
    "qiskit-plugin/getting-started/",
    "qiskit-plugin/overview/",
    "qiskit-plugin/sampler-estimator/",
    "qrisp-plugin/examples/",
    "qrisp-plugin/getting-started/",
    "qrisp-plugin/overview/",
    "qrisp-plugin/supported-operations/",
    "qrisp-plugin/troubleshooting/",
    "vscode/features/",
    "vscode/installation/",
    "vscode/overview/",
)

# The footer of every www.openquantum.com page links its legal terms and
# privacy policy on www.quantumrings.com.
SITE_PAGES = (
    SITE,
    SITE + "pricing",
    SITE + "free-credits",
    SITE + "citation",
    SITE + "compliance",
    SITE + "mcp",
    SITE + "providers",
    SITE + "providers/aqt",
    SITE + "providers/aqt/ibex-q1",
    SITE + "providers/ionq",
    SITE + "providers/ionq/forte-1",
    SITE + "providers/ionq/forte-ent",
    SITE + "providers/iqm",
    SITE + "providers/iqm/emerald",
    SITE + "providers/iqm/garnet",
    SITE + "providers/rigetti",
    SITE + "providers/rigetti/cepheus-1-108q",
    SITE + "use-cases/professors",
    SITE + "use-cases/students",
    TERMS_HOST + "terms",
    TERMS_HOST + "privacy",
)

PYPI_RELEASES = (
    ("openquantum-sdk", "1.0.0"),
    ("openquantum-mcp", "0.2.0"),
    ("openquantum-sdk-qiskit", "1.0.0"),
    ("openquantum-sdk-pennylane", "1.0.0"),
    ("openquantum-sdk-cirq", "0.5.0"),
    ("openquantum-sdk-qrisp", "0.5.0"),
)
PYPI_INFO = ("name", "version", "summary", "requires_python", "requires_dist", "classifiers", "project_urls")

# Fragments of the pricing page and its calculator bundle that define the
# units of the published table and the source of a live quote.
PRICING_STATEMENTS = (
    "All prices shown in USD equivalent are for reference; actual deduction uses your Spark or Full Credits.",
    "Claim $50 of free compute every 90 days (25 Spark Credits)",
    "Can only be used for Public Compute executions (routed through qBitTensor Labs).",
    "Public Compute with Full Credits is the same lower price.",
)
PRICING_CODE = (
    'estimatePricing:async e=>i("/v1/pricing/estimate",{method:"POST",body:JSON.stringify(e)})',
    "estimatePricing({backend_class_id:E,shots:L})",
    "Y=(0,r.useMemo)(()=>K&&W?Number(K.price)+Number(W.price_increase):null,[K,W])",
    '["Your job will cost"," ",Y," ",V?"spark":"full"," ","credit",1!==Y?"s":""]',
)
CREDIT_RATE = re.compile(r"(\$\s?\d+(\.\d+)?\s*(per|/|=)\s*(1\s*)?credit)|(1\s*credit\s*(=|is)\s*\$)", re.I)
TABLE_FIELDS = (
    "short_code",
    "name",
    "provider_name",
    "modality",
    "active",
    "per_task_public",
    "per_shot_public",
    "per_task_private",
    "per_shot_private",
)

STRIP_ELEMENTS = ("script", "style", "svg", "noscript", "template", "head")
CHROME_ELEMENTS = ("nav", "header", "footer")
MARKDOWN_LINK = re.compile(r'(\]\()([^\s)]+)((?:\s+"[^"]*")?\))')
PICTOGRAPH = re.compile("[\U0001f000-\U0001faff\u2600-\u27bf\ufe0f\u200d] ?")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def fetch_status(url: str) -> tuple[int, bytes]:
    """GET url, retrying a 5xx answer once; returns the final status and body."""
    status = 0
    for _ in range(2):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return 200, response.read()
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            if status < 500:
                break
    return status, b""


def fetch(url: str) -> bytes:
    status, data = fetch_status(url)
    if status != 200:
        raise SystemExit(f"{url}: HTTP {status}")
    return data


def drop_elements(page: str, names: tuple[str, ...]) -> str:
    for name in names:
        page = re.sub(rf"<{name}\b.*?</{name}>", "", page, flags=re.S | re.I)
    return page


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


def docs_fragment(page: str) -> str:
    match = re.search(r'<article class="md-content__inner md-typeset">(.*)</article>', page, re.S)
    if not match:
        raise SystemExit("docs page carries no md-content__inner article")
    # MkDocs permalink anchors render as a pilcrow after every heading.
    return re.sub(r'<a class="headerlink"[^>]*>.*?</a>', "", match.group(1), flags=re.S)


def site_fragment(page: str) -> str:
    page = drop_elements(page, STRIP_ELEMENTS)
    match = re.search(r"<main\b[^>]*>(.*)</main>", page, re.S) or re.search(r"<body\b[^>]*>(.*)</body>", page, re.S)
    if not match:
        raise SystemExit("site page carries no body")
    return drop_elements(match.group(1), CHROME_ELEMENTS)


def header(url: str, stamp: str, flag: str, data: bytes) -> str:
    return (
        f"> Full piece: [{url}]({url})\n"
        f"> Retrieved {stamp} by scripts/capture_oq_docs.py {flag} (urllib, pandoc);\n"
        f"> fetched HTML sha256 {sha256(data)}.\n\n"
    )


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def docs_path(page: str, base: Path = BASE) -> Path:
    return base / "docs" / ((page.rstrip("/") or "index") + ".md")


def site_path(url: str, base: Path = BASE) -> Path:
    if url.startswith(TERMS_HOST):
        stem = "quantumrings_" + url[len(TERMS_HOST) :].replace("/", "_")
    else:
        stem = url[len(SITE) :].replace("/", "_") or "home"
    return base / "site" / f"{stem}.md"


def pypi_url(name: str, version: str) -> str:
    return f"{PYPI}{name}/{version}/json"


def capture_pages(
    flag: str, urls: list[tuple[str, Path]], fragment: Callable[[str], str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    rows: list[dict[str, Any]] = []
    unreachable: list[dict[str, Any]] = []
    for url, path in urls:
        status, data = fetch_status(url)
        if status != 200:
            unreachable.append({"url": url, "status": status})
            continue
        text = header(url, stamp, flag, data) + absolute_links(to_markdown(fragment(data.decode("utf-8"))), url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        rows.append({"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())})
    return rows, {"unreachable": unreachable}


def capture_docs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sitemap = fetch(DOCS + "sitemap.xml")
    listed = [loc[len(DOCS) :] for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap.decode("utf-8"))]
    if sorted(listed) != sorted(DOCS_PAGES):
        added, removed = sorted(set(listed) - set(DOCS_PAGES)), sorted(set(DOCS_PAGES) - set(listed))
        raise SystemExit(f"docs sitemap differs from DOCS_PAGES: added {added}, removed {removed}")
    rows, extra = capture_pages("--docs", [(DOCS + page, docs_path(page)) for page in DOCS_PAGES], docs_fragment)
    extra["sitemap_sha256"] = sha256(sitemap)
    return rows, extra


def capture_site() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    return capture_pages("--site", [(url, site_path(url)) for url in SITE_PAGES], site_fragment)


def flight_text(page: str) -> str:
    """Concatenated string payloads of the page's ``self.__next_f.push`` records."""
    out = []
    for record in re.findall(r"self\.__next_f\.push\((\[.*?\])\)</script>", page, re.S):
        value = json.loads(record)
        if len(value) > 1 and isinstance(value[1], str):
            out.append(value[1])
    return "".join(out)


def pricing_sources(page: str, stamp: str) -> tuple[dict[str, Any], dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    bodies: dict[str, str] = {}
    for path in sorted(set(re.findall(r"/_next/static/[^\"']+\.js", page))):
        data = fetch(SITE.rstrip("/") + path)
        bodies[path] = data.decode("utf-8", errors="replace")
        chunks.append({"url": SITE.rstrip("/") + path, "sha256": sha256(data)})

    def locate(fragment: str) -> list[str]:
        where = ["page"] if fragment in page else []
        return where + [SITE.rstrip("/") + path for path, body in bodies.items() if fragment in body]

    statements = [{"text": text, "found_in": locate(text)} for text in PRICING_STATEMENTS]
    code = [{"text": text, "found_in": locate(text)} for text in PRICING_CODE]
    for item in (*statements, *code):
        if not item["found_in"]:
            raise SystemExit(f"pricing source fragment not found: {item['text']!r}")
    rate_hits = sorted({m.group(0) for body in (page, *bodies.values()) for m in CREDIT_RATE.finditer(body)})
    sources = {
        "schema": "oq-pricing-sources-v1",
        "retrieved_utc": stamp,
        "chunks": chunks,
        "statements": statements,
        "calculator_code": code,
        "credit_rate_matches": rate_hits,
    }
    findings = {
        "credit_to_usd_rate": {
            "published": bool(rate_hits),
            "matches": rate_hits,
            "nearest_statement": PRICING_STATEMENTS[1],
        },
        "queue_priority_surcharge": {
            "published_in_page": False,
            "source": "authenticated POST /v1/pricing/estimate with backend_class_id and shots; the quote lists "
            "execution plans, each with a price and queue_priorities carrying price_increase, all in credits",
        },
    }
    return sources, findings


def capture_pricing() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    url = SITE + "pricing"
    data = fetch(url)
    page = data.decode("utf-8")
    flight = flight_text(page)
    start = flight.find('{"summary":')
    if start < 0:
        raise SystemExit("pricing flight data carries no summary record")
    summary = json.JSONDecoder().raw_decode(flight, start)[0]["summary"]
    rows = [{field: row[field] for field in TABLE_FIELDS} for row in summary["tableRows"]]
    sources, findings = pricing_sources(page, stamp)
    record = {
        "schema": "oq-pricing-v1",
        "source": url,
        "retrieved_utc": stamp,
        "html_sha256": sha256(data),
        "units": "USD equivalent: " + PRICING_STATEMENTS[0],
        "cost_model": "per_task + shots * per_shot, before any queue-priority increase",
        "backends": sorted(rows, key=lambda row: row["short_code"]),
        **findings,
    }
    outputs = ((EVIDENCE / "pricing.json", record), (BASE / "pricing" / "sources.json", sources))
    rows_out = []
    for path, doc in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
        rows_out.append({"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())})
    return rows_out, {"unreachable": []}


def capture_pypi() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for name, version in PYPI_RELEASES:
        url = pypi_url(name, version)
        doc = json.loads(fetch(url))
        record = {key: doc["info"].get(key) for key in PYPI_INFO}
        record["files"] = [
            {
                "filename": item["filename"],
                "packagetype": item["packagetype"],
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


def manifest_path(kind: str, base: Path = BASE) -> Path:
    return base / kind / "MANIFEST.json"


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
    prune_capture(kind, rows)
    doc: dict[str, Any] = {"schema": "oq-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    doc.update(extra)
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def inventory(kind: str, base: Path, root: Path) -> dict[str, str]:
    """Root-relative path to pinned source URL for every file a kind can capture."""
    evidence = root / EVIDENCE.relative_to(ROOT)
    if kind == "docs":
        return {rel(docs_path(page, base), root): DOCS + page for page in DOCS_PAGES}
    if kind == "site":
        return {rel(site_path(url, base), root): url for url in SITE_PAGES}
    if kind == "pricing":
        url = SITE + "pricing"
        return {rel(evidence / "pricing.json", root): url, rel(base / "pricing" / "sources.json", root): url}
    return {rel(base / "pypi" / f"{name}.json", root): pypi_url(name, version) for name, version in PYPI_RELEASES}


def check_tree(root: Path) -> int:
    """Verifies every kind under root: file set, manifest rows, fixed inventory, sources and sha256."""
    base = root / BASE.relative_to(ROOT)
    count = 0
    for kind in KINDS:
        doc = json.loads(manifest_path(kind, base).read_text(encoding="utf-8"))
        rows = [row["path"] for row in doc["files"]]
        listed = set(rows)
        if len(listed) != len(rows):
            raise SystemExit(f"{kind} manifest lists a path twice")
        prefix = rel(manifest_path(kind, base).parent, root) + "/"
        present = captured_files(kind, base, root)
        if unlisted := sorted(present - listed):
            raise SystemExit(f"{kind}: file {unlisted[0]} is not listed in its manifest")
        if absent := sorted(name for name in listed - present if name.startswith(prefix)):
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
            path = root / row["path"]
            if not path.is_file():
                raise SystemExit(f"{kind}: manifest row {row['path']} has no captured file")
            if sha256(path.read_bytes()) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            count += 1
    return count


def check() -> int:
    count = check_tree(ROOT)
    print(f"open quantum docs: {count} captured files match their manifests")
    return 0


def self_test() -> int:
    """Runs check_tree on a temporary copy of the retained capture and requires each mutation to fail."""
    cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = root / BASE.relative_to(ROOT)
        evidence = root / EVIDENCE.relative_to(ROOT)
        shutil.copytree(BASE, base)
        evidence.mkdir(parents=True)
        shutil.copy2(EVIDENCE / "pricing.json", evidence / "pricing.json")
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
            ("docs", base / "docs" / "concepts" / "credits.md"),
            ("site", base / "site" / "pricing.md"),
            ("pypi", base / "pypi" / "openquantum-mcp.json"),
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
        pricing = evidence / "pricing.json"
        pricing_bytes = pricing.read_bytes()
        pricing.write_bytes(pricing_bytes.replace(b"0.18", b"0.19", 1))
        expect("pricing record altered", "differs from its captured sha256")
        pricing.write_bytes(pricing_bytes)
        original = edit_manifest(
            "site", lambda doc: doc["unreachable"].append({"url": "https://example.invalid/", "status": 404})
        )
        expect("unreachable entry outside the inventory", "outside the captured inventory")
        manifest_path("site", base).write_bytes(original)
        stray = base / "docs" / "stray" / "gone.md"
        stray.parent.mkdir()
        stray.write_text("x\n", encoding="utf-8")
        expect("stray docs file", "is not listed in its manifest")
        rows = json.loads(manifest_path("docs", base).read_text(encoding="utf-8"))["files"]
        prune_capture("docs", rows, base, root)
        if stray.exists() or stray.parent.exists():
            raise SystemExit("self-test prune: stray file survived")
        check_tree(root)
        cases += 1
    print(f"capture_oq_docs self-test: {cases} mutations rejected")
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
        parser.error("give --docs, --site, --pricing, --pypi, --check or --self-test")
    capture: dict[str, Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]]] = {
        "docs": capture_docs,
        "site": capture_site,
        "pricing": capture_pricing,
        "pypi": capture_pypi,
    }
    for kind in chosen:
        rows, extra = capture[kind]()
        write_manifest(kind, rows, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
