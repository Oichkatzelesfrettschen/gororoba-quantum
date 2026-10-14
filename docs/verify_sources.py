"""Verify retained source identities, provenance coverage, and historical aliases."""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import tarfile
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# The allowlist records reviewed grants and evidence routes, not inferred permissions.
LICENSE_URLS = {
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "LicenseRef-arXiv-nonexclusive-distrib-1.0": "https://arxiv.org/licenses/nonexclusive-distrib/1.0/",
    "LicenseRef-arXiv-assumed-1991-2003": "https://arxiv.org/licenses/assumed-1991-2003/",
    "CC-BY-NC-SA-3.0": "https://creativecommons.org/licenses/by-nc-sa/3.0/",
}
PUBLIC_LICENSES = {"CC-BY-4.0", "CC0-1.0"}
ARXIV_VERSION = r"(?:\d{4}\.\d{4,5}|[a-zA-Z][a-zA-Z0-9.-]*/\d{7})v[1-9]\d*"


def require_mapping(value: Any, message: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(message)
    return value


def require_text(value: Any, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(message)
    return value


def require_digest(value: Any, message: str) -> None:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, message)


def require_url(value: Any, message: str) -> str:
    value = require_text(value, message)
    parsed = urlsplit(value)
    require(parsed.scheme in {"https", "http"} and bool(parsed.netloc), message)
    return value


def require_timestamp(value: Any, message: str) -> None:
    require_text(value, message)
    try:
        observed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(message) from error
    require(observed.utcoffset() == timedelta(0), message)


def verify_license_document(registry: dict[str, Any], identifier: str) -> None:
    documents = require_mapping(registry.get("license_documents"), "operative license documents")
    document = require_mapping(documents.get(identifier), "operative license document")
    expected_url = LICENSE_URLS[identifier]
    if identifier in PUBLIC_LICENSES:
        expected_url += "legalcode.en"
    require(document.get("url") == expected_url, "operative license URL")
    require_digest(document.get("sha256"), "operative license SHA-256")
    require_text(document.get("reading_scope"), "operative license reading scope")
    require_timestamp(document.get("verified_at_utc"), "operative license timestamp")


class ArxivRightsParser(HTMLParser):
    """Read paper-specific rights and identity fields without using footer licenses."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.license_sections = 0
        self.license_urls: list[str] = []
        self.download_urls: list[str] = []
        self.citation_ids: list[str] = []
        self.license_stack: list[str] = []
        self.download_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = {name for key, value in attrs if key == "class" and value for name in value.split()}
        is_license = tag == "div" and "abs-license" in classes
        is_download = tag == "a" and "download-pdf" in classes
        is_citation = tag == "meta" and ("name", "citation_arxiv_id") in attrs
        if is_license or is_download or is_citation or self.license_stack or self.download_stack:
            require(len({key for key, _ in attrs}) == len(attrs), "captured arXiv duplicate attributes")
        attributes = dict(attrs)
        if is_citation:
            self.citation_ids.append(require_text(attributes.get("content"), "captured arXiv citation metadata"))
        if is_download:
            require(not self.download_stack, "captured arXiv download nesting")
            self.download_urls.append(require_text(attributes.get("href"), "captured arXiv download URL"))
            self.download_stack.append(tag)
        elif self.download_stack and tag not in self.VOID_TAGS:
            self.download_stack.append(tag)
        if is_license:
            require(not self.license_stack, "captured arXiv license nesting")
            self.license_sections += 1
            self.license_stack.append(tag)
        elif self.license_stack:
            if tag == "a":
                require(
                    "has_license" in classes or attributes.get("title") == "Rights to this article",
                    "captured arXiv license anchor",
                )
                self.license_urls.append(require_text(attributes.get("href"), "captured arXiv license URL"))
            if tag not in self.VOID_TAGS:
                self.license_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        for stack in (self.license_stack, self.download_stack):
            if stack:
                require(stack[-1] == tag, "captured arXiv evidence nesting")
                stack.pop()

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def close(self) -> None:
        super().close()
        require(not self.license_stack and not self.download_stack, "captured arXiv unclosed evidence")


def verify_arxiv_evidence(root: Path, rights: dict[str, Any], version: str) -> None:
    """Bind the declared article license and version to the retained abstract page."""
    relative = f"docs/evidence/source_rights/arxiv-{version.replace('/', '-')}.html"
    require(rights.get("evidence_path") == relative, "captured arXiv evidence path")
    source = root / relative
    require(
        source.is_file() and not source.is_symlink() and source.resolve() == root.resolve() / relative,
        "captured arXiv evidence file",
    )
    require_timestamp(rights.get("evidence_retrieved_at_utc"), "captured arXiv retrieval timestamp")
    raw_response = source.read_bytes()
    require(hashlib.sha256(raw_response).hexdigest() == rights["evidence_sha256"], "captured arXiv evidence SHA-256")
    try:
        html = raw_response.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("captured arXiv HTML encoding") from error
    parser = ArxivRightsParser()
    parser.feed(html)
    parser.close()
    require(parser.citation_ids == [version.rsplit("v", 1)[0]], "captured arXiv citation identity")
    require(len(parser.download_urls) == 1, "captured arXiv download count")
    require(
        urljoin(rights["evidence_url"], parser.download_urls[0]) == f"https://arxiv.org/pdf/{version}",
        "captured arXiv download version",
    )
    require(parser.license_sections == 1 and len(parser.license_urls) == 1, "captured arXiv license count")
    observed = require_url(parser.license_urls[0], "captured arXiv license URL")
    require(
        observed.replace("http://", "https://", 1) == rights["license_url"].replace("http://", "https://", 1),
        "captured arXiv license identity",
    )
    if "observed_license_url" in rights:
        require(observed == rights["observed_license_url"], "captured arXiv observed license identity")


class ExternalArticleParser(HTMLParser):
    """Read article identity metadata; rights interpretation remains a manual audit."""

    FIELD_NAMES = {"citation_doi", "citation_title", "citation_pdf_url"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fields: dict[str, list[str]] = {name: [] for name in self.FIELD_NAMES}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta" or not any(key == "name" and value in self.FIELD_NAMES for key, value in attrs):
            return
        require(len({key for key, _ in attrs}) == len(attrs), "captured external article duplicate attributes")
        attributes = dict(attrs)
        field = require_text(attributes.get("name"), "captured external article field name")
        self.fields[field].append(require_text(attributes.get("content"), "captured external article field value"))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def capture_relative_path(rights: dict[str, Any]) -> str:
    relative = require_text(rights.get("evidence_path"), "source capture path")
    require(
        re.fullmatch(r"docs/evidence/source_rights/[A-Za-z0-9][A-Za-z0-9_.-]*\.(?:html|json)", relative) is not None,
        "source capture path",
    )
    return relative


def verify_external_article_evidence(root: Path, entry: dict[str, Any], rights: dict[str, Any]) -> None:
    """Bind a retained external article capture to its bytes and publisher identity."""
    relative = capture_relative_path(rights)
    source = root / relative
    require(
        source.is_file() and not source.is_symlink() and source.resolve() == root.resolve() / relative,
        "captured external evidence file",
    )
    require_timestamp(rights.get("evidence_retrieved_at_utc"), "captured external retrieval timestamp")
    raw_response = source.read_bytes()
    require(hashlib.sha256(raw_response).hexdigest() == rights["evidence_sha256"], "captured external evidence SHA-256")
    article = re.fullmatch(
        r"https://pmihes\.centre-mersenne\.org/item/(10\.1007/[A-Za-z0-9_.-]+)\.pdf", entry["source_url"]
    )
    if article is None:
        raise ValueError("captured external article source route")
    require(
        rights["evidence_url"] == f"https://pmihes.centre-mersenne.org/articles/{article[1]}/",
        "captured external article evidence identity",
    )
    try:
        html = raw_response.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("captured external HTML encoding") from error
    parser = ExternalArticleParser()
    parser.feed(html)
    parser.close()
    require(parser.fields["citation_doi"] == [article[1]], "captured external article DOI identity")
    require(parser.fields["citation_pdf_url"] == [entry["source_url"]], "captured external article PDF identity")
    title = require_text(entry.get("title"), "captured external article registered title")
    require(parser.fields["citation_title"] == [title], "captured external article title identity")


class DagstuhlRightsParser(HTMLParser):
    """Read article-specific publisher metadata independently of footer notices."""

    FIELD_NAMES = {"DC.Rights", "citation_doi", "citation_title", "citation_pdf_url", "citation_abstract_html_url"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fields: dict[str, list[str]] = {name: [] for name in self.FIELD_NAMES}
        self.canonical_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        names = [value for key, value in attrs if key == "name" and value in self.FIELD_NAMES]
        canonical = tag == "link" and ("rel", "canonical") in attrs
        if (tag == "meta" and names) or canonical:
            require(len({key for key, _ in attrs}) == len(attrs), "captured Dagstuhl duplicate attributes")
            attributes = dict(attrs)
            if canonical:
                self.canonical_urls.append(require_text(attributes.get("href"), "captured Dagstuhl canonical URL"))
            else:
                field = require_text(attributes.get("name"), "captured Dagstuhl field name")
                self.fields[field].append(require_text(attributes.get("content"), "captured Dagstuhl field value"))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def verify_dagstuhl_evidence(root: Path, entry: dict[str, Any], identifier: str) -> None:
    """Bind a publisher PDF to its exact DOI, download link and article license."""
    rights = require_mapping(entry.get("rights"), "source rights object")
    relative = f"docs/evidence/source_rights/dagstuhl-{identifier}.html"
    require(rights.get("evidence_path") == relative, "captured Dagstuhl evidence path")
    source = root / relative
    require(
        source.is_file() and not source.is_symlink() and source.resolve() == root.resolve() / relative,
        "captured Dagstuhl evidence file",
    )
    require_timestamp(rights.get("evidence_retrieved_at_utc"), "captured Dagstuhl retrieval timestamp")
    raw_response = source.read_bytes()
    require(hashlib.sha256(raw_response).hexdigest() == rights["evidence_sha256"], "captured Dagstuhl evidence SHA-256")
    try:
        html = raw_response.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("captured Dagstuhl HTML encoding") from error
    parser = DagstuhlRightsParser()
    parser.feed(html)
    parser.close()
    require(rights.get("license_identifier") == "CC-BY-4.0", "captured Dagstuhl supported license")
    license_url = "https://creativecommons.org/licenses/by/4.0/legalcode"
    require(parser.fields["DC.Rights"] == [license_url], "captured Dagstuhl license identity")
    require(rights.get("observed_license_url") == license_url, "captured Dagstuhl observed license identity")
    require(parser.fields["citation_doi"] == [f"10.4230/{identifier}"], "captured Dagstuhl DOI identity")
    title = require_text(rights.get("publisher_title"), "captured Dagstuhl registered title")
    require(parser.fields["citation_title"] == [title], "captured Dagstuhl title identity")
    require(parser.canonical_urls == [rights["evidence_url"]], "captured Dagstuhl canonical identity")
    require(
        parser.fields["citation_abstract_html_url"] == [rights["evidence_url"]],
        "captured Dagstuhl abstract identity",
    )
    download = urlsplit(entry["source_url"])
    require(
        download.scheme == "https"
        and download.netloc == "drops.dagstuhl.de"
        and download.path.startswith("/storage/")
        and download.path.endswith(f"/{identifier}/{identifier}.pdf")
        and not download.query
        and not download.fragment,
        "captured Dagstuhl publisher download route",
    )
    require(parser.fields["citation_pdf_url"] == [entry["source_url"]], "captured Dagstuhl PDF identity")


def verify_zenodo_evidence(root: Path, rights: dict[str, Any], licensed_file: dict[str, Any], record_id: str) -> None:
    """Bind the declared license and deposit identity to the retained endpoint response."""
    relative = f"docs/evidence/source_rights/zenodo-record-{record_id}.json"
    require(rights.get("evidence_path") == relative, "captured Zenodo evidence path")
    source = root / relative
    require(
        source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(root.resolve()),
        "captured Zenodo evidence file",
    )
    require_timestamp(rights.get("evidence_retrieved_at_utc"), "captured Zenodo retrieval timestamp")
    raw_response = source.read_bytes()
    require(hashlib.sha256(raw_response).hexdigest() == rights["evidence_sha256"], "captured Zenodo evidence SHA-256")
    try:
        decoded = json.loads(raw_response)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("captured Zenodo JSON") from error
    captured = require_mapping(decoded, "captured Zenodo record")
    require(type(captured.get("id")) is int and captured["id"] == int(record_id), "captured Zenodo record identity")
    links = require_mapping(captured.get("links"), "captured Zenodo record links")
    require(links.get("self") == rights["evidence_url"], "captured Zenodo record URL")
    metadata = require_mapping(captured.get("metadata"), "captured Zenodo metadata")
    license_metadata = require_mapping(metadata.get("license"), "captured Zenodo license")
    require(
        license_metadata.get("id") == rights["license_identifier"].lower(),
        "captured Zenodo license identity",
    )
    files = captured.get("files")
    if not isinstance(files, list):
        raise ValueError("captured Zenodo file inventory")
    matching_files = []
    for candidate in files:
        candidate = require_mapping(candidate, "captured Zenodo file")
        candidate_links = require_mapping(candidate.get("links"), "captured Zenodo file links")
        if candidate_links.get("self") == licensed_file["url"]:
            matching_files.append(candidate)
    require(len(matching_files) == 1, "captured Zenodo matching file")
    deposited_file = matching_files[0]
    filename = unquote(urlsplit(licensed_file["url"]).path.split("/files/", 1)[1].removesuffix("/content"))
    require(deposited_file.get("key") == filename, "captured Zenodo file key")
    require(
        type(deposited_file.get("size")) is int and deposited_file["size"] == licensed_file["bytes"],
        "captured Zenodo file size",
    )
    require(deposited_file.get("checksum") == f"md5:{licensed_file['md5']}", "captured Zenodo file checksum")


def verify_source_rights(
    entry: dict[str, Any], registry: dict[str, Any], *, root: Path, published: bool, payload: bytes = b""
) -> None:
    """Check recorded rights consistency; primary-source inspection supplies the judgment."""
    rights = require_mapping(entry.get("rights"), "source rights object")
    require(rights.get("verified") is True, "source rights verification")
    require_digest(rights.get("pdf_sha256"), "rights PDF SHA-256")
    require(rights["pdf_sha256"] == entry["sha256"], "rights PDF identity")
    require_digest(rights.get("evidence_sha256"), "rights evidence SHA-256")
    require_url(rights.get("evidence_url"), "rights evidence URL")
    require_timestamp(rights.get("verified_at_utc"), "rights verification timestamp")
    for field in ("evidence_locator", "reading_scope", "evidence_summary", "license_identifier"):
        require_text(rights.get(field), f"rights {field}")
    identifier = rights["license_identifier"]
    if published:
        require(entry.get("status") == "retained", "published retention status")
        require(entry.get("redistribution") == "explicit_license_verified", "published redistribution status")
        require(rights.get("decision") == "publish_under_explicit_license", "published rights decision")
        require(identifier in PUBLIC_LICENSES, "published license allowlist")
        require(rights.get("copy_status") == "unchanged", "published copy status")
        require_text(rights.get("conditions"), "published license conditions")
        require(rights.get("license_url") == LICENSE_URLS[identifier], "published license URL")
        require(bool(payload), "published PDF payload")
        require(hashlib.sha256(payload).hexdigest() == entry["sha256"], "published rights payload identity")
    else:
        require(rights.get("decision") == "external_only", "external-only rights decision")
        if rights.get("license_url") is not None:
            require_url(rights["license_url"], "external-only license URL")
    if identifier in LICENSE_URLS:
        verify_license_document(registry, identifier)
    source_url = entry["source_url"]
    require_url(source_url, "rights source URL")
    if urlsplit(source_url).netloc == "arxiv.org":
        source = re.fullmatch(rf"https://arxiv\.org/pdf/({ARXIV_VERSION})(?:\.pdf)?", source_url)
        if source is None:
            raise ValueError("arXiv source version")
        require(rights["evidence_url"] == f"https://arxiv.org/abs/{source[1]}", "arXiv evidence version")
        allowed_identifiers = PUBLIC_LICENSES if published else set(LICENSE_URLS) - PUBLIC_LICENSES
        require(identifier in allowed_identifiers, "arXiv rights classification")
        observed_url = rights.get("observed_license_url") if published else rights.get("license_url")
        observed_url = require_url(observed_url, "arXiv observed license URL")
        require(observed_url.replace("http://", "https://", 1) == LICENSE_URLS[identifier], "arXiv license identity")
        if published or "evidence_path" in rights or "evidence_retrieved_at_utc" in rights:
            verify_arxiv_evidence(root, rights, source[1])
    elif published and urlsplit(rights["evidence_url"]).netloc == "drops.dagstuhl.de":
        document = re.fullmatch(
            r"https://drops\.dagstuhl\.de/entities/document/10\.4230/(LIPIcs\.[A-Za-z0-9.]+)",
            rights["evidence_url"],
        )
        if document is None:
            raise ValueError("published Dagstuhl evidence route")
        verify_dagstuhl_evidence(root, entry, document[1])
    elif published:
        record = re.fullmatch(r"https://zenodo\.org/api/records/([1-9]\d*)", rights["evidence_url"])
        if record is None:
            raise ValueError("published license evidence route")
        licensed_file = require_mapping(rights.get("licensed_file"), "licensed deposit file")
        require_url(licensed_file.get("url"), "licensed deposit file URL")
        require(
            re.fullmatch(rf"https://zenodo\.org/api/records/{record[1]}/files/[^/?#]+/content", licensed_file["url"])
            is not None,
            "licensed deposit record identity",
        )
        require(licensed_file.get("sha256") == entry["sha256"], "licensed deposit SHA-256")
        require(
            type(licensed_file.get("bytes")) is int and licensed_file["bytes"] == len(payload),
            "licensed deposit size",
        )
        require(
            licensed_file.get("md5") == hashlib.md5(payload, usedforsecurity=False).hexdigest(),
            "licensed deposit MD5",
        )
        verify_zenodo_evidence(root, rights, licensed_file, record[1])
    elif "evidence_path" in rights or "evidence_retrieved_at_utc" in rights:
        verify_external_article_evidence(root, entry, rights)


def verify_capture_inventory(root: Path, registry: dict[str, Any]) -> tuple[int, int]:
    """Close retained capture paths and count uncaptured external manual-audit records."""
    capture_root = root / "docs/evidence/source_rights"
    require(
        capture_root.is_dir()
        and not capture_root.is_symlink()
        and capture_root.resolve() == root.resolve() / "docs/evidence/source_rights",
        "source capture directory",
    )
    readme = capture_root / "README.md"
    require(readme.is_file() and not readme.is_symlink(), "source capture README")
    registered: set[str] = set()
    manual_audits = 0
    for section in ("pdfs", "external_pdfs"):
        for entry in registry[section]:
            rights = require_mapping(entry.get("rights"), "source rights object")
            if section == "external_pdfs" and not {"evidence_path", "evidence_retrieved_at_utc"}.intersection(rights):
                manual_audits += 1
                continue
            relative = capture_relative_path(rights)
            require(relative not in registered, "duplicate source capture path")
            registered.add(relative)
            source = root / relative
            require(source.is_file() and not source.is_symlink(), "source capture file")
    actual = {path.relative_to(root).as_posix() for path in capture_root.iterdir() if path.name != "README.md"}
    require(actual == registered, "source capture inventory differs from registry")
    return len(registered), manual_audits


def verify_external_sources(root: Path, registry: dict[str, Any], published_digests: set[str]) -> int:
    """Keep external-only sources verifiable without publishing local reading copies."""
    cache_root = root / "docs" / "local_source_cache"
    require(not cache_root.is_symlink(), "local source cache must not be a symlink")
    require(not cache_root.exists() or cache_root.is_dir(), "local source cache must be a directory")
    require("/docs/local_source_cache/" in (root / ".gitignore").read_text().splitlines(), "local cache ignore rule")
    if (root / ".git").exists():
        tracked_cache = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "ls-files", "-z", "--", "docs/local_source_cache"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        require(not tracked_cache, "local source cache contains Git-tracked files")
    cache_paths: set[str] = set()
    external_digests: set[str] = set()
    for entry in registry["external_pdfs"]:
        require("path" not in entry, "external-only PDF must not carry a published path")
        require(entry["status"] == "external_only", "external-only PDF status")
        require(entry["redistribution"] == "excluded_without_permission", "external-only redistribution status")
        require(bool(entry["rights_locator"]) and bool(entry["rights_reason"]), "external-only rights provenance")
        require(entry["source_url"].startswith(("https://", "http://")), "external-only source URL")
        digest = entry["sha256"]
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "external-only SHA-256")
        require(digest not in external_digests, "duplicate external-only PDF digest")
        require(digest not in published_digests, "external-only PDF appears in the published inventory")
        external_digests.add(digest)
        verify_source_rights(entry, registry, root=root, published=False)
        for size_field in ("bytes", "pages"):
            require(type(entry[size_field]) is int and entry[size_field] > 0, f"external-only {size_field}")
        note = root / entry["note"]
        require(note.is_file(), "external-only owning note")
        note_text = note.read_text()
        require(digest in note_text and entry["source_url"] in note_text, "external-only note identity")
        excluded_source = root / entry["excluded_published_path"]
        require(excluded_source.parent == root / "docs" / "pdf", "external-only excluded path")
        require(
            not excluded_source.exists() and not excluded_source.is_symlink(), "external-only published file exists"
        )
        relative_cache = entry["local_cache_path"]
        source = root / relative_cache
        require(source.parent == cache_root and source.suffix == ".pdf", "external-only cache path")
        require(relative_cache not in cache_paths, "duplicate external-only cache path")
        cache_paths.add(relative_cache)
        require(not source.is_symlink(), "external-only cache file must not be a symlink")
        if source.exists():
            require(source.is_file(), "external-only cache entry must be a file")
            payload = source.read_bytes()
            require(payload.startswith(b"%PDF-"), "external-only cached PDF header")
            require(len(payload) == entry["bytes"], "external-only cached PDF size")
            require(hashlib.sha256(payload).hexdigest() == digest, "external-only cached PDF digest")
    for manifest in ("PDF_SHA256SUMS", "parallel_experiment_pdfs.sha256"):
        for line in (root / "docs" / manifest).read_text().splitlines():
            digest, relative = line.split(maxsplit=1)
            source = (root / relative.lstrip("*")).resolve()
            require(digest not in external_digests, f"external-only digest in {manifest}")
            require(not source.is_relative_to(cache_root.resolve()), f"local cache path in {manifest}")
    return len(external_digests)


def source_archive_prefix(entry: dict[str, Any]) -> str:
    """Bind the inspected archive root to a pinned source retrieval route."""
    source_url = require_url(entry.get("source_url"), "archive source URL")
    version = require_text(entry.get("version"), "archive version")
    github = re.fullmatch(
        r"https://codeload\.github\.com/[A-Za-z0-9_.-]+/([A-Za-z0-9_.-]+)/tar\.gz/([0-9a-f]{40})",
        source_url,
    )
    if github is not None:
        require(version.split(" ", 1)[0] == github[2], "archive pinned version")
        return f"{github[1]}-{github[2]}"
    interval = re.fullmatch(
        r"https://coqinterval\.gitlabpages\.inria\.fr/releases/interval-([0-9]+\.[0-9]+\.[0-9]+)\.tar\.gz",
        source_url,
    )
    if interval is None:
        raise ValueError("archive source route")
    require(version == interval[1], "archive pinned version")
    return f"interval-{interval[1]}"


def archive_member_bytes(
    archive: tarfile.TarFile, members: dict[str, tarfile.TarInfo], name: Any, size: Any, digest: Any
) -> bytes:
    """Read a regular member into memory; never extract archives to the filesystem."""
    name = require_text(name, "archive member name")
    require(type(size) is int and size >= 0, "archive member size")
    require_digest(digest, "archive member SHA-256")
    require(name in members, "archive member missing")
    member = members[name]
    require(member.isfile(), "archive inspected member must be regular")
    require(member.size == size, "archive member size identity")
    stream = archive.extractfile(member)
    if stream is None:
        raise ValueError("archive member stream")
    with stream:
        payload = stream.read()
    require(len(payload) == size, "archive member payload size")
    require(hashlib.sha256(payload).hexdigest() == digest, "archive member digest identity")
    return payload


def verify_archive_members(payload: bytes, entry: dict[str, Any], prefix: str) -> None:
    """Check inspected source and license bytes inside an unchanged archive."""
    identifier = require_text(entry.get("license_identifier"), "archive license identifier")
    require(identifier in {"MIT", "CECILL-B", "CECILL-C"}, "archive license allowlist")
    inspected = entry.get("inspected_files")
    if not isinstance(inspected, list) or not inspected:
        raise ValueError("archive inspected files")
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            members: dict[str, tarfile.TarInfo] = {}
            for member in archive.getmembers():
                path = PurePosixPath(member.name)
                require(
                    not path.is_absolute()
                    and ".." not in path.parts
                    and path.as_posix() == member.name.rstrip("/")
                    and bool(path.parts)
                    and path.parts[0] == prefix,
                    "archive member path",
                )
                require(member.name not in members, "duplicate archive member")
                members[member.name] = member
            license_payload = archive_member_bytes(
                archive, members, entry.get("license_member"), entry.get("license_bytes"), entry.get("license_sha256")
            )
            normalized = b" ".join(license_payload.split())
            if identifier == "MIT":
                require(
                    normalized.startswith((b"MIT License ", b"The MIT License (MIT) "))
                    and b"Permission is hereby granted, free of charge" in normalized
                    and b"The above copyright notice and this permission notice shall be included" in normalized,
                    "archive license text identity",
                )
            else:
                marker = identifier.replace("CECILL", "CeCILL").encode("ascii")
                require(
                    normalized.startswith(marker + b" FREE SOFTWARE LICENSE AGREEMENT"),
                    "archive license text identity",
                )
            inspected_names: set[str] = set()
            for candidate in inspected:
                record = require_mapping(candidate, "archive inspected file record")
                name = require_text(record.get("file"), "archive inspected file name")
                require(name not in inspected_names, "duplicate archive inspected file")
                inspected_names.add(name)
                archive_member_bytes(archive, members, name, record.get("bytes"), record.get("sha256"))
    except (tarfile.TarError, OSError, EOFError) as error:
        raise ValueError("invalid source archive") from error


def verify_source_archives(root: Path, registry: dict[str, Any]) -> int:
    """Close the retained archive inventory and bind provenance to inspected bytes."""
    entries = registry.get("source_archives")
    if not isinstance(entries, list):
        raise ValueError("source archive registry")
    archive_root = root / "docs/source_archives"
    require(not archive_root.is_symlink(), "source archive directory symlink")
    require(not archive_root.exists() or archive_root.is_dir(), "source archive directory")
    require(archive_root.resolve() == root.resolve() / "docs/source_archives", "source archive directory boundary")
    registered: set[str] = set()
    digests: set[str] = set()
    for candidate in entries:
        entry = require_mapping(candidate, "source archive entry")
        relative = require_text(entry.get("path"), "source archive path")
        require(
            re.fullmatch(r"docs/source_archives/[A-Za-z0-9][A-Za-z0-9_.-]*\.tar\.gz", relative) is not None,
            "source archive path",
        )
        require(relative not in registered, "duplicate source archive path")
        registered.add(relative)
        source = root / relative
        require(source.is_file() and not source.is_symlink(), "source archive file")
        payload = source.read_bytes()
        require(type(entry.get("bytes")) is int and entry["bytes"] > 0, "source archive size")
        require(len(payload) == entry["bytes"], "source archive size identity")
        digest = require_text(entry.get("sha256"), "source archive SHA-256")
        require_digest(digest, "source archive SHA-256")
        require(hashlib.sha256(payload).hexdigest() == digest, "source archive digest identity")
        require(digest not in digests, "duplicate source archive digest")
        digests.add(digest)
        for field in ("title", "reading_scope", "compatibility", "conditions"):
            require_text(entry.get(field), f"archive {field}")
        authors = entry.get("authors")
        if not isinstance(authors, list) or not authors:
            raise ValueError("archive authors")
        for author in authors:
            require_text(author, "archive author")
        require_timestamp(entry.get("retrieved_at_utc"), "archive retrieval timestamp")
        require(entry.get("copy_status") == "unchanged", "archive copy status")
        prefix = source_archive_prefix(entry)
        relative_note = require_text(entry.get("note"), "archive owning note")
        require(re.fullmatch(r"docs/notes/[A-Za-z0-9_.-]+\.md", relative_note) is not None, "archive owning note path")
        note = root / relative_note
        require(
            note.is_file() and not note.is_symlink() and note.resolve() == root.resolve() / relative_note,
            "archive owning note file",
        )
        note_text = note.read_text(encoding="utf-8")
        require(entry["source_url"] in note_text and digest in note_text, "archive owning note identity")
        verify_archive_members(payload, entry, prefix)
    actual = {path.relative_to(root).as_posix() for path in archive_root.iterdir()} if archive_root.exists() else set()
    require(actual == registered, "source archive inventory differs from registry")
    return len(registered)


def verify() -> None:
    root = Path(__file__).resolve().parents[1]
    library = root / "docs"
    registry: dict[str, Any] = json.loads((library / "SOURCES.json").read_text())
    require(registry["schema"] == "primary-source-library-v1", "unsupported source registry")
    checksum_lines: list[str] = []
    registered_paths: set[str] = set()
    published_digests: set[str] = set()
    for entry in registry["pdfs"]:
        relative = entry["path"]
        require(relative not in registered_paths, f"duplicate PDF: {relative}")
        registered_paths.add(relative)
        source = root / relative
        require(source.parent == library / "pdf" and not source.is_symlink(), f"PDF path: {relative}")
        payload = source.read_bytes()
        require(payload.startswith(b"%PDF-"), f"PDF header: {relative}")
        require(len(payload) == entry["bytes"], f"PDF size: {relative}")
        digest = hashlib.sha256(payload).hexdigest()
        published_digests.add(digest)
        require(digest == entry["sha256"], f"PDF digest: {relative}")
        require(entry["pages"] > 0, f"recorded page count: {relative}")
        require(entry["source_url"].startswith(("https://", "http://")), f"retrieval URL: {relative}")
        require((root / entry["note"]).is_file(), f"owning note: {relative}")
        verify_source_rights(entry, registry, root=root, published=True, payload=payload)
        note_text = (root / entry["note"]).read_text()
        for identity in (entry["source_url"], entry["rights"]["license_url"], entry["rights"]["evidence_url"]):
            require(identity in note_text, f"published note rights links: {relative}")
        checksum_lines.append(f"{digest}  {relative}\n")
    actual_paths = {
        path.relative_to(root).as_posix() for path in (library / "pdf").glob("*.pdf") if not path.is_symlink()
    }
    require(actual_paths == registered_paths, "PDF inventory differs from registry")
    require((library / "PDF_SHA256SUMS").read_text() == "".join(checksum_lines), "PDF checksum inventory")
    external_count = verify_external_sources(root, registry, published_digests)
    capture_count, manual_audit_count = verify_capture_inventory(root, registry)
    archive_count = verify_source_archives(root, registry)
    alias_paths: set[str] = set()
    for entry in registry["aliases"] + [registry["historical_path_alias"]]:
        alias = root / entry["path"]
        require(alias.is_symlink() and alias.readlink().as_posix() == entry["target"], f"alias: {alias.name}")
        require(alias.resolve().is_relative_to(root) and alias.exists(), f"alias target: {alias.name}")
        if alias.parent == library / "pdf":
            alias_paths.add(alias.relative_to(root).as_posix())
    actual_aliases = {path.relative_to(root).as_posix() for path in (library / "pdf").iterdir() if path.is_symlink()}
    require(actual_aliases == alias_paths, "PDF alias inventory differs from registry")
    for entry in registry["immutable_documentation"]:
        payload = (root / entry["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == entry["sha256"], f"historical digest: {entry['path']}")
        record = json.loads((root / entry["record"]).read_text())
        recorded_hashes = record.get("source_sha256", {}) | record.get("documentation_sha256", {})
        require(recorded_hashes[entry["path"]] == entry["sha256"], "historical manifest identity")
    link_count = 0
    for note in library.rglob("*.md"):
        if library / "local_source_cache" in note.parents:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", note.read_text()):
            if ":" in target or target.startswith("#"):
                continue
            relative_target = target.split("#", 1)[0]
            require((note.parent / relative_target).exists(), f"broken link: {note.relative_to(root)} -> {target}")
            link_count += 1
    print(
        f"Verified {len(registered_paths)} published PDFs, {external_count} external-only PDFs, "
        f"{capture_count} rights captures ({manual_audit_count} external manual-audit records without captures), "
        f"{archive_count} source archives, "
        f"{len(alias_paths)} PDF aliases, "
        f"historical identities, and {link_count} local links"
    )


if __name__ == "__main__":
    verify()
