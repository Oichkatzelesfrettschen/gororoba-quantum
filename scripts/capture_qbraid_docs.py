"""Capture qBraid's documentation, REST API specification and package metadata as the reference the qBraid guide cites.

Three sources, each retained with its identity:

- ``--docs`` fetches every page that docs.qbraid.com/llms.txt lists (the fixed
  tuple DOCS_PAGES; an index naming another set fails the capture), requests
  the page's Markdown source at the page URL plus ``.md``, and writes
  docs/<path>.md under a header naming the URL, the retrieval time and the
  sha256 of the fetched bytes. The body is the served Markdown, unmodified.
  The index itself and its concatenation, llms.txt and llms-full.txt, are
  retained verbatim beside the pages.
- ``--api`` fetches the OpenAPI document of the REST API that llms.txt names
  (https://docs.qbraid.com/openapi-v2.json) and retains it verbatim as
  api/openapi-v2.json.
- ``--pypi`` retains the PyPI JSON metadata of each pinned package release
  (PYPI_RELEASES): requirements, classifiers, project URLs and every
  distribution file's name, upload time, size and sha256, as pypi/<name>.json.

Each kind writes MANIFEST.json (path, source URL, sha256, and every page that
answered with an error) and prunes files its new rows no longer name.
``--check`` verifies, without network access, that each kind's file set equals
its manifest rows, that the rows equal the fixed inventory, that each row
names its pinned source, that every file matches its sha256 and that each
page's header digest equals the digest of the body below it.
``--self-test`` proves on a temporary copy that the check rejects a removed
page, a removed page with its row, an unlisted file, an altered record, a
moved source, a body that differs from its header digest and an unreachable
entry outside the inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "docs/notes/qbraid"
KINDS = ("docs", "api", "pypi")
DOCS = "https://docs.qbraid.com/"
INDEX_FILES = ("llms.txt", "llms-full.txt")
API_FILE = "openapi-v2.json"
PYPI = "https://pypi.org/pypi/"
USER_AGENT = "Mozilla/5.0 (capture_qbraid_docs)"
PAGE_LINK = re.compile(r"\]\(" + re.escape(DOCS) + r"(v2/[^)\s]+)\.md\)")
HEADER = re.compile(rb"> Full piece: [^\n]*\n> Retrieved [^\n]*\n> fetched bytes sha256 ([0-9a-f]{64})\.\n\n")

DOCS_PAGES = (
    "v2/account/api-keys",
    "v2/account/chat",
    "v2/account/composer",
    "v2/account/dashboard",
    "v2/account/explore",
    "v2/account/explore-catalog",
    "v2/account/integrations/openquantum",
    "v2/account/models",
    "v2/account/organizations/audit-logs",
    "v2/account/organizations/creating-an-organization",
    "v2/account/organizations/credit-requests",
    "v2/account/organizations/credits",
    "v2/account/organizations/invitations",
    "v2/account/organizations/invite-codes",
    "v2/account/organizations/members",
    "v2/account/organizations/overview",
    "v2/account/organizations/seats",
    "v2/account/organizations/settings",
    "v2/account/organizations/subscriptions",
    "v2/account/organizations/transactions",
    "v2/account/organizations/usage",
    "v2/account/overview",
    "v2/account/profile",
    "v2/account/quantum-jobs",
    "v2/account/refresh",
    "v2/account/sign-in",
    "v2/account/support",
    "v2/account/usage",
    "v2/account/wallet/buy-credits",
    "v2/account/wallet/overview",
    "v2/account/wallet/payment-history",
    "v2/account/wallet/subscriptions",
    "v2/ai/integrations/ai-gateway",
    "v2/ai/integrations/mcp-server",
    "v2/ai/user-guide/agent-mode",
    "v2/ai/user-guide/ai-chat",
    "v2/ai/user-guide/overview",
    "v2/ai/user-guide/usage-quotas",
    "v2/algorithms/user-guide/cli",
    "v2/algorithms/user-guide/examples",
    "v2/algorithms/user-guide/overview",
    "v2/api-reference/rest/cancel-job-group",
    "v2/api-reference/rest/cancel-quantum-job",
    "v2/api-reference/rest/close-job-group",
    "v2/api-reference/rest/create-job-group",
    "v2/api-reference/rest/delete-quantum-job",
    "v2/api-reference/rest/delete-quantum-jobs",
    "v2/api-reference/rest/get-credit-balance",
    "v2/api-reference/rest/get-credit-pricing",
    "v2/api-reference/rest/get-device",
    "v2/api-reference/rest/get-device-calibrations",
    "v2/api-reference/rest/get-job-compiled-program",
    "v2/api-reference/rest/get-job-group",
    "v2/api-reference/rest/get-job-group-jobs",
    "v2/api-reference/rest/get-job-program",
    "v2/api-reference/rest/get-job-program-ascii",
    "v2/api-reference/rest/get-jobs-statuses",
    "v2/api-reference/rest/get-jobs-summary",
    "v2/api-reference/rest/get-quantum-devices",
    "v2/api-reference/rest/get-quantum-jobs",
    "v2/api-reference/rest/get-quantum-jobs-cost-estimate",
    "v2/api-reference/rest/get-quantum-jobs-list",
    "v2/api-reference/rest/get-quantum-jobs-result",
    "v2/api-reference/rest/get-simulator-usage",
    "v2/api-reference/rest/get-simulator-usage-series",
    "v2/api-reference/rest/list-job-groups",
    "v2/api-reference/rest/migration",
    "v2/api-reference/rest/post-quantum-jobs",
    "v2/api-reference/rest/update-simulator-usage-settings",
    "v2/api-reference/user-guide/overview",
    "v2/cli/api-reference/qbraid",
    "v2/cli/api-reference/qbraid_account",
    "v2/cli/api-reference/qbraid_admin",
    "v2/cli/api-reference/qbraid_agents",
    "v2/cli/api-reference/qbraid_compute",
    "v2/cli/api-reference/qbraid_configure",
    "v2/cli/api-reference/qbraid_devices",
    "v2/cli/api-reference/qbraid_envs",
    "v2/cli/api-reference/qbraid_jobs",
    "v2/cli/api-reference/qbraid_kernels",
    "v2/cli/api-reference/qbraid_lab",
    "v2/cli/api-reference/qbraid_pip",
    "v2/cli/api-reference/qbraid_projects",
    "v2/cli/api-reference/qbraid_skills",
    "v2/cli/api-reference/qbraid_troubleshoot",
    "v2/cli/user-guide/config-files",
    "v2/cli/user-guide/environments",
    "v2/cli/user-guide/magic-commands",
    "v2/cli/user-guide/overview",
    "v2/core/user-guide/overview",
    "v2/home/faq",
    "v2/home/introduction",
    "v2/home/learning",
    "v2/home/legacy-jobs",
    "v2/home/migration",
    "v2/home/pricing",
    "v2/lab/user-guide/environments",
    "v2/lab/user-guide/featured-environments/intel-quantum-sdk",
    "v2/lab/user-guide/files",
    "v2/lab/user-guide/getting-started",
    "v2/lab/user-guide/gpus",
    "v2/lab/user-guide/guidelines",
    "v2/lab/user-guide/kernels",
    "v2/lab/user-guide/notebooks",
    "v2/lab/user-guide/on-demand-instances",
    "v2/lab/user-guide/overview",
    "v2/lab/user-guide/quantum-devices",
    "v2/lab/user-guide/quantum-jobs",
    "v2/lab/user-guide/settings",
    "v2/lab/user-guide/troubleshooting",
    "v2/lab/user-guide/usage-limits",
    "v2/pyqasm/user-guide/advanced-features",
    "v2/pyqasm/user-guide/circuit-drawer",
    "v2/pyqasm/user-guide/cli",
    "v2/pyqasm/user-guide/examples",
    "v2/pyqasm/user-guide/openpulse",
    "v2/pyqasm/user-guide/overview",
    "v2/qir/user-guide/cirq-qir",
    "v2/qir/user-guide/overview",
    "v2/qir/user-guide/profiles",
    "v2/qir/user-guide/qasm3-qir",
    "v2/qir/user-guide/qir-squin",
    "v2/qir/user-guide/qiskit-qir",
    "v2/sdk/user-guide/interface",
    "v2/sdk/user-guide/overview",
    "v2/sdk/user-guide/programs",
    "v2/sdk/user-guide/providers/aqt",
    "v2/sdk/user-guide/providers/aws",
    "v2/sdk/user-guide/providers/calibrations",
    "v2/sdk/user-guide/providers/getting-started",
    "v2/sdk/user-guide/providers/gpu-simulators",
    "v2/sdk/user-guide/providers/ionq",
    "v2/sdk/user-guide/providers/iqm",
    "v2/sdk/user-guide/providers/jobs",
    "v2/sdk/user-guide/providers/managing-jobs",
    "v2/sdk/user-guide/providers/open-quantum",
    "v2/sdk/user-guide/providers/quera",
    "v2/sdk/user-guide/providers/quobly",
    "v2/sdk/user-guide/providers/rigetti",
    "v2/sdk/user-guide/providers/self-managed",
    "v2/sdk/user-guide/providers/self-managed/aqt",
    "v2/sdk/user-guide/providers/self-managed/aws",
    "v2/sdk/user-guide/providers/self-managed/azure",
    "v2/sdk/user-guide/providers/self-managed/ibm",
    "v2/sdk/user-guide/providers/self-managed/ionq",
    "v2/sdk/user-guide/providers/self-managed/openquantum",
    "v2/sdk/user-guide/providers/self-managed/oqc",
    "v2/sdk/user-guide/providers/self-managed/origin",
    "v2/sdk/user-guide/providers/self-managed/pasqal",
    "v2/sdk/user-guide/providers/self-managed/qperfect",
    "v2/sdk/user-guide/providers/self-managed/quantinuum",
    "v2/sdk/user-guide/providers/self-managed/qudora",
    "v2/sdk/user-guide/providers/self-managed/rigetti",
    "v2/sdk/user-guide/runtime/components",
    "v2/sdk/user-guide/runtime/new-provider",
    "v2/sdk/user-guide/runtime/options",
    "v2/sdk/user-guide/transforms",
    "v2/sdk/user-guide/transpiler",
    "v2/sdk/user-guide/visualization",
    "v2/vscode/user-guide/code-editor",
    "v2/vscode/user-guide/environment-manager",
    "v2/vscode/user-guide/overview",
    "v2/vscode/user-guide/quantum-console",
)

PYPI_RELEASES = (
    ("qbraid", "0.13.0"),
    ("qbraid-core", "0.6.36"),
)
PYPI_INFO = ("name", "version", "summary", "requires_python", "requires_dist", "classifiers", "project_urls")


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


def header(url: str, stamp: str, data: bytes) -> str:
    return (
        f"> Full piece: [{url}]({url})\n"
        f"> Retrieved {stamp} by scripts/capture_qbraid_docs.py --docs (urllib);\n"
        f"> fetched bytes sha256 {sha256(data)}.\n\n"
    )


def rel(path: Path, root: Path = ROOT) -> str:
    return path.relative_to(root).as_posix()


def page_url(page: str) -> str:
    return f"{DOCS}{page}.md"


def docs_path(page: str, base: Path = BASE) -> Path:
    return base / "docs" / f"{page}.md"


def pypi_url(name: str, version: str) -> str:
    return f"{PYPI}{name}/{version}/json"


def capture_docs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    index = fetch(DOCS + "llms.txt")
    listed = PAGE_LINK.findall(index.decode("utf-8"))
    if sorted(listed) != sorted(DOCS_PAGES):
        added, removed = sorted(set(listed) - set(DOCS_PAGES)), sorted(set(DOCS_PAGES) - set(listed))
        raise SystemExit(f"docs llms.txt differs from DOCS_PAGES: added {added}, removed {removed}")
    stamp = now()
    rows: list[dict[str, Any]] = []
    unreachable: list[dict[str, Any]] = []
    for page in DOCS_PAGES:
        url = page_url(page)
        status, data = fetch_status(url)
        if status != 200:
            unreachable.append({"url": url, "status": status})
            continue
        path = docs_path(page)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(header(url, stamp, data).encode("utf-8") + data)
        rows.append({"path": rel(path), "source": url, "sha256": sha256(path.read_bytes())})
    for name in INDEX_FILES:
        data = index if name == "llms.txt" else fetch(DOCS + name)
        path = BASE / "docs" / name
        path.write_bytes(data)
        rows.append({"path": rel(path), "source": DOCS + name, "sha256": sha256(data)})
    return rows, {"unreachable": unreachable}


def capture_api() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = fetch(DOCS + API_FILE)
    json.loads(data)
    path = BASE / "api" / API_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return [{"path": rel(path), "source": DOCS + API_FILE, "sha256": sha256(data)}], {"unreachable": []}


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
    doc: dict[str, Any] = {"schema": "qbraid-docs-capture-v1", "kind": kind, "retrieved_utc": now(), "files": rows}
    doc.update(extra)
    manifest_path(kind).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")


def inventory(kind: str, base: Path, root: Path) -> dict[str, str]:
    """Root-relative path to pinned source URL for every file a kind can capture."""
    if kind == "docs":
        pinned = {rel(docs_path(page, base), root): page_url(page) for page in DOCS_PAGES}
        pinned.update({rel(base / "docs" / name, root): DOCS + name for name in INDEX_FILES})
        return pinned
    if kind == "api":
        return {rel(base / "api" / API_FILE, root): DOCS + API_FILE}
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
            data = path.read_bytes()
            if sha256(data) != row["sha256"]:
                raise SystemExit(f"{row['path']} differs from its captured sha256")
            if kind == "docs" and path.suffix == ".md":
                match = HEADER.match(data)
                if match is None:
                    raise SystemExit(f"{row['path']}: page carries no capture header")
                if sha256(data[match.end() :]) != match.group(1).decode("ascii"):
                    raise SystemExit(f"{row['path']}: body differs from the header's fetched-bytes sha256")
            count += 1
    return count


def check() -> int:
    count = check_tree(ROOT)
    print(f"qbraid docs: {count} captured files match their manifests")
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
            ("docs", base / "docs" / "v2" / "home" / "pricing.md"),
            ("docs", base / "docs" / "llms.txt"),
            ("api", base / "api" / API_FILE),
            ("pypi", base / "pypi" / "qbraid-core.json"),
        ):
            name = rel(victim, root)
            victim_bytes = victim.read_bytes()
            victim.unlink()
            expect(f"{name} removed", "has no captured file")
            original = edit_manifest(kind, partial(drop_row, name))
            expect(f"{name} and manifest row removed", "has no manifest row")
            manifest_path(kind, base).write_bytes(original)
            victim.write_bytes(victim_bytes)
            unlisted = victim.parent / "unlisted.md"
            unlisted.write_text("x\n", encoding="utf-8")
            expect(f"{name} neighbor unlisted", "is not listed in its manifest")
            unlisted.unlink()
            victim.write_bytes(victim_bytes + b"!")
            expect(f"{name} altered", "differs from its captured sha256")
            victim.write_bytes(victim_bytes)
            original = edit_manifest(kind, partial(move_source, name))
            expect(f"{name} row with another source", "differs from the pinned")
            manifest_path(kind, base).write_bytes(original)
        victim = base / "docs" / "v2" / "home" / "pricing.md"
        victim_bytes = victim.read_bytes()
        altered = victim_bytes + b"!"
        victim.write_bytes(altered)

        def rehash(doc: dict[str, Any]) -> None:
            next(row for row in doc["files"] if row["path"] == rel(victim, root))["sha256"] = sha256(altered)

        original = edit_manifest("docs", rehash)
        expect("page body differs from its header digest", "body differs from the header")
        manifest_path("docs", base).write_bytes(original)
        victim.write_bytes(victim_bytes)
        original = edit_manifest(
            "docs", lambda doc: doc["unreachable"].append({"url": "https://example.invalid/", "status": 404})
        )
        expect("unreachable entry outside the inventory", "outside the captured inventory")
        manifest_path("docs", base).write_bytes(original)
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
    print(f"capture_qbraid_docs self-test: {cases} mutations rejected")
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
        parser.error("give --docs, --api, --pypi, --check or --self-test")
    capture: dict[str, Callable[[], tuple[list[dict[str, Any]], dict[str, Any]]]] = {
        "docs": capture_docs,
        "api": capture_api,
        "pypi": capture_pypi,
    }
    for kind in chosen:
        rows, extra = capture[kind]()
        write_manifest(kind, rows, extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
