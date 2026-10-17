"""Capture Quandela Cloud's guides, terms, API descriptions, offer strings and Perceval docs for the Quandela guide.

Six sources, each retained with its identity:

- ``--guide`` reads the webide single-page bundle that https://cloud.quandela.com/webide/
  loads and extracts every English guide it embeds as a Vite Markdown module
  (``/src/docs/guide/<page>.en.md``: the user guide, the entity-management
  guide and the Quantum Toolbox guides). The fixed tuple GUIDE_PAGES is the
  page set; a bundle embedding another set fails the capture. Site-relative
  links resolve under https://cloud.quandela.com/webide/.
- ``--legal`` extracts the English Quandela Cloud terms of service and
  privacy policy, which the portal bundle carries as static HTML, and fetches
  the www.quandela.com privacy policy and legal terms pages.
- ``--perceval`` fetches the Perceval 1.3 documentation pages that cover
  remote computing (PERCEVAL_PAGES) and keeps each Sphinx article body.
- ``--api`` retains the OpenAPI descriptions the cloud and account services
  publish without authentication, as sorted JSON beside the sha256 of the
  served bytes.
- ``--offer`` retains, in offer/sources.json, the portal and webide strings
  that define plans and credits (monthly quota, job concurrency, per-job
  duration, the per-shot, per-job, per-block, per-byte and per-second
  notebook prices an offer can carry, the monthly reset of free credit) with
  the bundle each was found in, and the status of the public offer-list route
  the pricing page calls.
- ``--pypi`` retains the PyPI JSON metadata of each pinned release
  (PYPI_RELEASES): requirements, project URLs and every distribution file's
  name, upload time, size and sha256.

Pages render through pandoc as in capture_oq_docs.py, whose fetch, conversion
and manifest helpers this script reuses. Each kind writes MANIFEST.json and
prunes files its new rows no longer name. ``--check`` verifies offline that
each kind's file set equals its manifest rows, that the rows equal the fixed
inventory with their pinned sources, and that every file matches its sha256.
``--self-test`` proves on a temporary copy that the check rejects a removed
page, a removed page with its row, an unlisted file, an altered file, a moved
source and an unreachable entry outside the inventory.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from capture_oq_docs import (
    absolute_links,
    captured_files,
    fetch,
    fetch_status,
    manifest_path,
    now,
    prune_capture,
    rel,
    sha256,
    site_fragment,
    to_markdown,
)

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/quandela"
KINDS = ("guide", "legal", "perceval", "api", "offer", "pypi")
CLOUD = "https://cloud.quandela.com/"
WEBIDE = CLOUD + "webide/"
WWW = "https://www.quandela.com/"
PERCEVAL = "https://perceval.quandela.net/docs/v1.3/"
PYPI = "https://pypi.org/pypi/"
BUNDLE = re.compile(r'src="(/[^"]*assets/index-[^"]+\.js)"')

GUIDE_PAGES = (
    "entity-manage-guide/00-introduction",
    "entity-manage-guide/01-cloud-entity-management",
    "quantum-toolbox-guide/chemistryvqe/01-api-documentation",
    "quantum-toolbox-guide/chemistryvqe/02-job-creation",
    "quantum-toolbox-guide/chemistryvqe/03-job-estimator",
    "quantum-toolbox-guide/chemistryvqe/04-job-results",
    "quantum-toolbox-guide/customvqe/01-api-documentation",
    "quantum-toolbox-guide/customvqe/02-job-creation",
    "quantum-toolbox-guide/customvqe/03-job-estimator",
    "quantum-toolbox-guide/customvqe/04-job-results",
    "quantum-toolbox-guide/cvarvqe/01-api-documentation",
    "quantum-toolbox-guide/cvarvqe/02-qubo-problem-formulation",
    "quantum-toolbox-guide/cvarvqe/03-job-creation",
    "quantum-toolbox-guide/cvarvqe/04-job-estimator",
    "quantum-toolbox-guide/cvarvqe/05-job-results",
    "quantum-toolbox-guide/graphdsi/01-api-documentation",
    "quantum-toolbox-guide/graphdsi/02-job-creation",
    "quantum-toolbox-guide/graphdsi/03-job-estimator",
    "quantum-toolbox-guide/graphdsi/04-job-results",
    "quantum-toolbox-guide/graphisomorphism/01-api-documentation",
    "quantum-toolbox-guide/graphisomorphism/02-job-creation",
    "quantum-toolbox-guide/graphisomorphism/03-job-estimator",
    "quantum-toolbox-guide/graphisomorphism/04-job-results",
    "quantum-toolbox-guide/vqe/01-api-documentation",
    "quantum-toolbox-guide/vqe/02-algorithm-explanation",
    "quantum-toolbox-guide/vqe/03-job-creation",
    "quantum-toolbox-guide/vqe/04-job-estimator",
    "quantum-toolbox-guide/vqe/05-job-results",
    "user-guide/01-product-tour",
    "user-guide/02-understanding-platforms",
    "user-guide/03-token-and-job-management",
    "user-guide/04-compilation",
)

# Each portal legal page: the text its English static HTML block opens with,
# the page that serves it and the retained file stem.
LEGAL_BUNDLED = (
    ("By using any QUANDELA Services", CLOUD + "terms-of-service", "cloud_terms-of-service"),
    ("Introduction Protecting the privacy and Personal Data", CLOUD + "privacy-policy", "cloud_privacy-policy"),
)
LEGAL_PAGES = ((WWW + "privacy-policy/", "www_privacy-policy"), (WWW + "legal-terms/", "www_legal-terms"))
STATIC_HTML = re.compile(r"Ws\('(<.*?)',\d+\)", re.S)

PERCEVAL_PAGES = (
    "getting_started.html",
    "notebooks/Remote_Computation_Tutorial.html",
    "reference/providers/index.html",
    "reference/providers/quandela.html",
    "reference/runtime/command.html",
    "reference/runtime/communication_layer.html",
    "reference/runtime/computation.html",
    "reference/runtime/computer.html",
    "reference/runtime/error_mitigation/index.html",
    "reference/runtime/execution.html",
    "reference/runtime/execution_factory.html",
    "reference/runtime/execution_group.html",
    "reference/runtime/execution_status.html",
    "reference/runtime/legacy/job.html",
    "reference/runtime/legacy/remote_processor.html",
    "reference/runtime/legacy/rpchandler.html",
    "reference/runtime/platform_specs.html",
)

API_DOCUMENTS = (
    ("https://api.cloud.quandela.com/openapi.json", "cloud-openapi.json"),
    ("https://api.cloud.quandela.com/qt-openapi.json", "cloud-qt-openapi.json"),
    ("https://api.account.quandela.com/openapi.json", "account-openapi.json"),
)

# Strings of the portal (www) and webide bundles that define offers and credits.
OFFER_STATEMENTS = (
    '"monthly-quota-is":"Monthly quota is $credit credits"',
    '"One-waiting-job-at-a-time":"One waiting job at a time"',
    '"One-running-job-at-a-time":"One running job at a time"',
    '"Access-jupyter-notebook":"Access to embedded Jupyter Notebook"',
    '"Access-quantum-toolbox":"Access to the Quantum Toolbox"',
    '"access-to-free-simulators":"Access to the free simulator and free time slots on QPU"',
    '"max-duration":"Max $max_duration per job"',
    '"credits-for-one-second":"credits for 1 second of usage"',
    '"credits-for-one-shot":"credits for using 1 shot"',
    '"credits-for-one-job":"credits for using 1 job"',
    '"credit-for-one-byte":"credits for using 1 byte"',
    '"note-book":"Jupyter Notebook"',
    '"free-credit-tooltip":"Free credit is only available when using $offer_name offer. '
    'It will be automatically reset at the beginning of the month."',
    '"credit-tooltip":"These credits are unavailable when using $offer_name offer."',
    '"is-explorer-token":"Is Explorer Token"',
    'priorityTooltip:"Priority value from 0 to 3 ~ ascending priority"',
)
OFFER_CODE = (
    'e.offer.price_notebook_per_sec>0?e.offer.price_notebook_per_sec:n.$t("billing-offer.free")',
    'e.offer.price_per_job>0?e.offer.price_per_job:n.$t("billing-offer.free")',
    'a.price_per_shot>0?a.price_per_shot:n.$t("billing-offer.free")',
    'list(){return Wo.get("api/public/offer/list")}',
)
OFFER_LIST = "https://api.cloud.quandela.com/api/public/offer/list"

PYPI_RELEASES = (
    ("perceval-quandela", "1.3.1"),
    ("exqalibur", "1.4.2"),
    ("perceval-interop", "1.3.0"),
    ("scmver", "1.10"),
)
PYPI_INFO = ("name", "version", "summary", "license", "requires_python", "requires_dist", "project_urls")


def header(url: str, stamp: str, flag: str, origin: str) -> str:
    return f"> Full piece: [{url}]({url})\n> Retrieved {stamp} by scripts/capture_qd_docs.py {flag} {origin}.\n\n"


def bundle(page_url: str) -> tuple[str, bytes]:
    """URL and bytes of the index script a single-page app's HTML loads."""
    match = BUNDLE.search(fetch(page_url).decode("utf-8"))
    if not match:
        raise SystemExit(f"{page_url}: no index bundle")
    url = CLOUD.rstrip("/") + match.group(1)
    return url, fetch(url)


JS_ESCAPE = re.compile(r"\\(x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|.)", re.S)
JS_CHARS = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def js_unescape(text: str) -> str:
    """Value of a JavaScript string or template literal body."""

    def value(match: re.Match[str]) -> str:
        escape = match.group(1)
        if escape[0] in "xu" and len(escape) > 1:
            return chr(int(escape.strip("xu{}"), 16))
        return JS_CHARS.get(escape, escape)

    return JS_ESCAPE.sub(value, text)


def template_literal(source: str, start: int) -> str:
    """Value of the JavaScript template literal whose opening backtick sits at start."""
    end = start + 1
    while source[end] != "`":
        end += 2 if source[end] == "\\" else 1
    return js_unescape(source[start + 1 : end])


def guide_modules(source: str) -> dict[str, str]:
    """English guide Markdown keyed by page, from the bundle's Vite glob table."""
    names = dict(re.findall(r'"/src/docs/guide/([^"]+)\.en\.md":(__vite_glob_\w+)', source))
    pages = {}
    for page, name in names.items():
        start = source.index(f"{name}=`") + len(name) + 1
        pages[page] = template_literal(source, start)
    return pages


def webide_links(markdown: str, page_url: str) -> str:
    """Site-relative targets resolve under the webide root, others against the page."""
    markdown = re.sub(r"\]\(/(?!/)", "](" + WEBIDE, markdown)
    return absolute_links(markdown, page_url)


def guide_path(page: str, base: Path = BASE) -> Path:
    return base / "guide" / f"{page}.md"


def write_row(path: Path, text: str, source: str, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    rows.append({"path": rel(path), "source": source, "sha256": sha256(path.read_bytes())})


def capture_guide() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    url, data = bundle(WEBIDE)
    pages = guide_modules(data.decode("utf-8"))
    if sorted(pages) != sorted(GUIDE_PAGES):
        added, removed = sorted(set(pages) - set(GUIDE_PAGES)), sorted(set(GUIDE_PAGES) - set(pages))
        raise SystemExit(f"webide guides differ from GUIDE_PAGES: added {added}, removed {removed}")
    rows: list[dict[str, Any]] = []
    for page in GUIDE_PAGES:
        source = WEBIDE + "guide/" + page
        origin = f"from the module /src/docs/guide/{page}.en.md of {url} (sha256 {sha256(data)})"
        text = header(source, stamp, "--guide", origin) + webide_links(pages[page], source)
        write_row(guide_path(page), text, source, rows)
    return rows, {"unreachable": [], "bundle": url, "bundle_sha256": sha256(data)}


def static_block(source: str, opening: str) -> str:
    """First static HTML block of the bundle whose text opens with the given words."""
    for match in STATIC_HTML.finditer(source):
        text = " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())
        if text.startswith(opening):
            return js_unescape(match.group(1))
    raise SystemExit(f"portal bundle carries no static block opening {opening!r}")


def capture_legal() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    url, data = bundle(CLOUD)
    source = data.decode("utf-8")
    updated = re.search(r'"terms-of-service":\{title:"[^"]*",time:"([^"]*)"', source)
    rows: list[dict[str, Any]] = []
    for opening, page, stem in LEGAL_BUNDLED:
        origin = f"from the English static HTML of {url} (sha256 {sha256(data)})"
        body = absolute_links(to_markdown(re.sub(r" data-v-[0-9a-f]+", "", static_block(source, opening))), page)
        write_row(BASE / "legal" / f"{stem}.md", header(page, stamp, "--legal", origin) + body, page, rows)
    unreachable = []
    for page, stem in LEGAL_PAGES:
        status, html_bytes = fetch_status(page)
        if status != 200:
            unreachable.append({"url": page, "status": status})
            continue
        origin = f"(urllib, pandoc); fetched HTML sha256 {sha256(html_bytes)}"
        body = absolute_links(to_markdown(site_fragment(html_bytes.decode("utf-8"))), page)
        write_row(BASE / "legal" / f"{stem}.md", header(page, stamp, "--legal", origin) + body, page, rows)
    extra = {
        "unreachable": unreachable,
        "bundle": url,
        "bundle_sha256": sha256(data),
        "terms_last_updated": updated.group(1) if updated else None,
    }
    return rows, extra


SPHINX_CODE = re.compile(
    r'<div class="[^"]*highlight-([\w+-]+)[^"]*"><div class="highlight"><pre>(.*?)</pre></div>', re.S
)


def plain_code(match: re.Match[str]) -> str:
    """A Pygments block as one <pre><code> of its source text, which pandoc writes as a fence."""
    source = html.unescape(re.sub(r"<[^>]+>", "", match.group(2)))
    return f'<pre><code class="{match.group(1)}">{html.escape(source)}</code></pre>'


def perceval_fragment(page: str) -> str:
    match = re.search(r'<div itemprop="articleBody">(.*?)<footer', page, re.S)
    if not match:
        raise SystemExit("Perceval page carries no articleBody")
    # Sphinx permalink anchors render as a pilcrow after every heading.
    fragment = re.sub(r'<a class="headerlink"[^>]*>.*?</a>', "", match.group(1), flags=re.S)
    return SPHINX_CODE.sub(plain_code, fragment)


def perceval_path(page: str, base: Path = BASE) -> Path:
    return base / "perceval" / page.replace(".html", ".md")


def capture_perceval() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stamp = now()
    rows: list[dict[str, Any]] = []
    unreachable = []
    for page in PERCEVAL_PAGES:
        url = PERCEVAL + page
        status, data = fetch_status(url)
        if status != 200:
            unreachable.append({"url": url, "status": status})
            continue
        origin = f"(urllib, pandoc); fetched HTML sha256 {sha256(data)}"
        body = absolute_links(to_markdown(perceval_fragment(data.decode("utf-8"))), url)
        write_row(perceval_path(page), header(url, stamp, "--perceval", origin) + body, url, rows)
    return rows, {"unreachable": unreachable}


def capture_api() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    served = {}
    for url, name in API_DOCUMENTS:
        data = fetch(url)
        served[url] = sha256(data)
        text = json.dumps(json.loads(data), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        write_row(BASE / "api" / name, text, url, rows)
    return rows, {"unreachable": [], "served_sha256": served}


def capture_offer() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bodies = {url: data.decode("utf-8") for url, data in (bundle(CLOUD), bundle(WEBIDE))}

    def locate(fragment: str) -> list[str]:
        return [url for url, body in bodies.items() if fragment in body]

    statements = [{"text": text, "found_in": locate(text)} for text in OFFER_STATEMENTS]
    code = [{"text": text, "found_in": locate(text)} for text in OFFER_CODE]
    for item in (*statements, *code):
        if not item["found_in"]:
            raise SystemExit(f"offer source fragment not found: {item['text']!r}")
    status, _ = fetch_status(OFFER_LIST)
    record = {
        "schema": "qd-offer-sources-v1",
        "retrieved_utc": now(),
        "bundles": [{"url": url, "sha256": sha256(body.encode("utf-8"))} for url, body in bodies.items()],
        "statements": statements,
        "offer_code": code,
        "public_offer_list": {"url": OFFER_LIST, "status": status},
    }
    rows: list[dict[str, Any]] = []
    write_row(BASE / "offer" / "sources.json", json.dumps(record, indent=1) + "\n", CLOUD + "pricing", rows)
    return rows, {"unreachable": []}


def pypi_url(name: str, version: str) -> str:
    return f"{PYPI}{name}/{version}/json"


def capture_pypi() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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
        write_row(BASE / "pypi" / f"{name}.json", json.dumps(record, indent=1) + "\n", url, rows)
    return rows, {"unreachable": []}


def write_manifest(kind: str, rows: list[dict[str, Any]], extra: dict[str, Any]) -> None:
    prune_capture(kind, rows, BASE, ROOT)
    doc: dict[str, Any] = {"schema": "qd-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    doc.update(extra)
    manifest_path(kind, BASE).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def inventory(kind: str, base: Path, root: Path) -> dict[str, str]:
    """Root-relative path to pinned source URL for every file a kind can capture."""
    if kind == "guide":
        return {rel(guide_path(page, base), root): WEBIDE + "guide/" + page for page in GUIDE_PAGES}
    if kind == "legal":
        pages = [(page, stem) for _, page, stem in LEGAL_BUNDLED] + list(LEGAL_PAGES)
        return {rel(base / "legal" / f"{stem}.md", root): page for page, stem in pages}
    if kind == "perceval":
        return {rel(perceval_path(page, base), root): PERCEVAL + page for page in PERCEVAL_PAGES}
    if kind == "api":
        return {rel(base / "api" / name, root): url for url, name in API_DOCUMENTS}
    if kind == "offer":
        return {rel(base / "offer" / "sources.json", root): CLOUD + "pricing"}
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
        present = captured_files(kind, base, root)
        if unlisted := sorted(present - listed):
            raise SystemExit(f"{kind}: file {unlisted[0]} is not listed in its manifest")
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
    print(f"quandela docs: {count} captured files match their manifests")
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
            ("guide", guide_path("user-guide/03-token-and-job-management", base)),
            ("legal", base / "legal" / "cloud_terms-of-service.md"),
            ("perceval", perceval_path("reference/providers/quandela.html", base)),
            ("api", base / "api" / "cloud-openapi.json"),
            ("offer", base / "offer" / "sources.json"),
            ("pypi", base / "pypi" / "exqalibur.json"),
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
        original = edit_manifest(
            "perceval", lambda doc: doc["unreachable"].append({"url": "https://example.invalid/", "status": 404})
        )
        expect("unreachable entry outside the inventory", "outside the captured inventory")
        manifest_path("perceval", base).write_bytes(original)
        check_tree(root)
    print(f"capture_qd_docs self-test: {cases} mutations rejected")
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
        parser.error("give a capture kind, --check or --self-test")
    capture: dict[str, Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]]] = {
        "guide": capture_guide,
        "legal": capture_legal,
        "perceval": capture_perceval,
        "api": capture_api,
        "offer": capture_offer,
        "pypi": capture_pypi,
    }
    for kind in chosen:
        rows, extra = capture[kind]()
        write_manifest(kind, rows, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
