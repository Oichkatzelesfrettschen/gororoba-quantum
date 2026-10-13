"""Exercise publication and optional-cache guards in isolated temporary fixtures."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import re
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from verify_sources import (
    LICENSE_URLS,
    PUBLIC_LICENSES,
    verify_capture_inventory,
    verify_external_sources,
    verify_source_archives,
    verify_source_rights,
)


def rights_fixture(digest: str, *, external: bool = False) -> dict[str, Any]:
    return {
        "verified": True,
        "pdf_sha256": digest,
        "verified_at_utc": "2026-10-12T07:27:16+00:00",
        "decision": "external_only" if external else "publish_under_explicit_license",
        "license_identifier": "NOASSERTION" if external else "CC-BY-4.0",
        "license_url": None if external else LICENSE_URLS["CC-BY-4.0"],
        "observed_license_url": "http://creativecommons.org/licenses/by/4.0/",
        "evidence_url": "https://arxiv.org/abs/1904.00633v2",
        "evidence_sha256": "1" * 64,
        "evidence_locator": "Exact-version abstract license link",
        "reading_scope": "Version metadata and operative grant",
        "evidence_summary": "Manually inspected primary-source license evidence",
        "copy_status": "unchanged",
        "conditions": "Preserve attribution, original notices, source and license links.",
    }


def license_documents_fixture() -> dict[str, Any]:
    return {
        identifier: {
            "url": url + ("legalcode.en" if identifier in PUBLIC_LICENSES else ""),
            "sha256": "2" * 64,
            "reading_scope": "Operative permission and recipient scope",
            "verified_at_utc": "2026-10-12T07:27:16+00:00",
        }
        for identifier, url in LICENSE_URLS.items()
    }


class ExternalSourceChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="external-source-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.payload = b"%PDF-1.7\nexternal-source-fixture\n"
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.cache = self.root / "docs/local_source_cache/external.pdf"
        self.published = self.root / "docs/pdf/external.pdf"
        (self.root / "docs/notes").mkdir(parents=True)
        self.published.parent.mkdir()
        (self.root / ".gitignore").write_text("/docs/local_source_cache/\n")
        for manifest in ("PDF_SHA256SUMS", "parallel_experiment_pdfs.sha256"):
            (self.root / "docs" / manifest).write_text("")
        source_url = "https://example.org/external.pdf"
        (self.root / "docs/notes/external.md").write_text(f"{source_url}\n{self.digest}\n")
        self.registry: dict[str, Any] = {
            "external_pdfs": [
                {
                    "rights": rights_fixture(self.digest, external=True),
                    "status": "external_only",
                    "redistribution": "excluded_without_permission",
                    "rights_locator": "PDF page 1",
                    "rights_reason": "External test fixture requires permission to redistribute.",
                    "source_url": source_url,
                    "sha256": self.digest,
                    "bytes": len(self.payload),
                    "pages": 1,
                    "note": "docs/notes/external.md",
                    "excluded_published_path": "docs/pdf/external.pdf",
                    "local_cache_path": "docs/local_source_cache/external.pdf",
                }
            ]
        }

    def retain_cache(self) -> None:
        self.cache.parent.mkdir()
        self.cache.write_bytes(self.payload)

    def reject(self, message: str, published_digests: set[str] | None = None) -> None:
        with self.assertRaisesRegex(ValueError, "^" + re.escape(message) + "$"):
            verify_external_sources(self.root, self.registry, published_digests or set())

    def test_absent_cache_is_optional(self) -> None:
        self.assertEqual(verify_external_sources(self.root, self.registry, set()), 1)
        self.assertFalse(self.cache.exists())

    def test_original_cache_is_verified(self) -> None:
        self.retain_cache()
        self.assertEqual(verify_external_sources(self.root, self.registry, set()), 1)
        self.assertEqual(self.cache.read_bytes(), self.payload)

    def test_modified_cache_digest_is_rejected(self) -> None:
        self.retain_cache()
        self.cache.write_bytes(self.payload[:-1] + b"!")
        self.reject("external-only cached PDF digest")

    def test_external_digest_in_published_inventory_is_rejected(self) -> None:
        self.reject("external-only PDF appears in the published inventory", {self.digest})

    def test_external_file_in_published_directory_is_rejected(self) -> None:
        self.published.write_bytes(self.payload)
        self.reject("external-only published file exists")

    def test_force_tracked_cache_is_rejected(self) -> None:
        self.retain_cache()
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, capture_output=True, check=True)
        subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "add", "--force", "--", "docs/local_source_cache/external.pdf"],
            cwd=self.root,
            capture_output=True,
            check=True,
        )
        self.reject("local source cache contains Git-tracked files")

    def test_external_digest_in_checksum_manifest_is_rejected(self) -> None:
        (self.root / "docs/parallel_experiment_pdfs.sha256").write_text(f"{self.digest}  docs/pdf/external.pdf\n")
        self.reject("external-only digest in parallel_experiment_pdfs.sha256")

    def test_cache_path_in_checksum_manifest_is_rejected(self) -> None:
        (self.root / "docs/parallel_experiment_pdfs.sha256").write_text(
            "0" * 64 + "  docs/local_source_cache/external.pdf\n"
        )
        self.reject("local cache path in parallel_experiment_pdfs.sha256")

    def test_missing_cache_ignore_rule_is_rejected(self) -> None:
        (self.root / ".gitignore").write_text("")
        self.reject("local cache ignore rule")


class SourceRightsChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="source-rights-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.payload = b"%PDF-1.7\nrights-source-fixture\n"
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.registry = {"license_documents": license_documents_fixture()}
        self.entry: dict[str, Any] = {
            "path": "docs/pdf/1904.00633.pdf",
            "status": "retained",
            "redistribution": "explicit_license_verified",
            "source_url": "https://arxiv.org/pdf/1904.00633v2",
            "sha256": self.digest,
            "bytes": len(self.payload),
            "rights": rights_fixture(self.digest),
        }

        self.arxiv_path = self.root / "docs/evidence/source_rights/arxiv-1904.00633v2.html"
        self.arxiv_path.parent.mkdir(parents=True)
        self.entry["rights"]["evidence_path"] = self.arxiv_path.relative_to(self.root).as_posix()
        self.entry["rights"]["evidence_retrieved_at_utc"] = "2026-10-12T08:48:37+00:00"
        self.arxiv_html = (
            '<!DOCTYPE html><html><head><meta name="citation_arxiv_id" content="1904.00633"></head><body>'
            '<a class="download-pdf" href="/pdf/1904.00633v2"><span>PDF</span></a>'
            '<div class="abs-license"><div><a class="has_license" '
            'href="http://creativecommons.org/licenses/by/4.0/"><img alt="license icon"/>'
            "<span>view license</span></a></div></div>"
            '<footer><a href="https://creativecommons.org/publicdomain/zero/1.0/">Site license</a></footer>'
            "</body></html>"
        )
        self.write_arxiv_capture()

    def write_arxiv_capture(self) -> None:
        raw_response = self.arxiv_html.encode("utf-8")
        self.arxiv_path.write_bytes(raw_response)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(raw_response).hexdigest()

    def use_external_arxiv(self, identifier: str = "LicenseRef-arXiv-nonexclusive-distrib-1.0") -> None:
        previous_url = self.entry["rights"]["observed_license_url"]
        observed_url = LICENSE_URLS[identifier].replace("https://", "http://", 1)
        self.entry["rights"].update(
            decision="external_only",
            license_identifier=identifier,
            license_url=LICENSE_URLS[identifier],
            observed_license_url=observed_url,
        )
        self.arxiv_html = self.arxiv_html.replace(previous_url, observed_url).replace(
            'class="has_license"', 'title="Rights to this article"'
        )
        self.write_arxiv_capture()

    def verify(self, *, published: bool = True) -> None:
        verify_source_rights(self.entry, self.registry, root=self.root, published=published, payload=self.payload)

    def reject(self, message: str, *, published: bool = True) -> None:
        with self.assertRaisesRegex(ValueError, "^" + re.escape(message) + "$"):
            self.verify(published=published)

    def use_zenodo(self) -> None:
        self.entry["source_url"] = "https://author.example.org/paper.pdf"
        self.entry["rights"]["evidence_url"] = "https://zenodo.org/api/records/20431754"
        self.entry["rights"]["licensed_file"] = {
            "url": "https://zenodo.org/api/records/20431754/files/paper%20name.pdf/content",
            "sha256": self.digest,
            "bytes": len(self.payload),
            "md5": hashlib.md5(self.payload, usedforsecurity=False).hexdigest(),
        }

        self.zenodo_record: dict[str, Any] = {
            "id": 20431754,
            "links": {"self": self.entry["rights"]["evidence_url"]},
            "metadata": {"license": {"id": "cc-by-4.0"}},
            "files": [
                {
                    "key": "paper name.pdf",
                    "size": len(self.payload),
                    "checksum": "md5:" + self.entry["rights"]["licensed_file"]["md5"],
                    "links": {"self": self.entry["rights"]["licensed_file"]["url"]},
                }
            ],
        }
        self.zenodo_path = self.root / "docs/evidence/source_rights/zenodo-record-20431754.json"
        self.zenodo_path.parent.mkdir(parents=True, exist_ok=True)
        self.entry["rights"]["evidence_path"] = self.zenodo_path.relative_to(self.root).as_posix()
        self.entry["rights"]["evidence_retrieved_at_utc"] = "2026-10-12T08:16:00+00:00"
        self.write_zenodo_capture()

    def write_zenodo_capture(self) -> None:
        raw_response = json.dumps(self.zenodo_record).encode()
        self.zenodo_path.write_bytes(raw_response)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(raw_response).hexdigest()

    def use_dagstuhl(self) -> None:
        self.entry["source_url"] = (
            "https://drops.dagstuhl.de/storage/00lipics/lipics-vol193-itp2021/LIPIcs.ITP.2021.21/LIPIcs.ITP.2021.21.pdf"
        )
        self.entry["rights"].update(
            evidence_url="https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2021.21",
            evidence_path="docs/evidence/source_rights/dagstuhl-LIPIcs.ITP.2021.21.html",
            observed_license_url="https://creativecommons.org/licenses/by/4.0/legalcode",
            publisher_title="Proving Quantum Programs Correct",
        )
        self.dagstuhl_path = self.root / self.entry["rights"]["evidence_path"]
        self.dagstuhl_html = (
            '<html><head><link rel="canonical" href="' + self.entry["rights"]["evidence_url"] + '">'
            '<meta name="DC.Rights" content="https://creativecommons.org/licenses/by/4.0/legalcode">'
            '<meta name="citation_doi" content="10.4230/LIPIcs.ITP.2021.21">'
            '<meta name="citation_title" content="Proving Quantum Programs Correct">'
            '<meta name="citation_abstract_html_url" content="' + self.entry["rights"]["evidence_url"] + '">'
            '<meta name="citation_pdf_url" content="' + self.entry["source_url"] + '"></head>'
            "<body><footer>CC0 site footer</footer></body></html>"
        )
        self.write_dagstuhl_capture()

    def write_dagstuhl_capture(self) -> None:
        payload = self.dagstuhl_html.encode()
        self.dagstuhl_path.write_bytes(payload)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(payload).hexdigest()

    def test_dagstuhl_source_specific_grant_passes(self) -> None:
        self.use_dagstuhl()
        self.verify()

    def test_dagstuhl_changed_capture_hash_is_rejected(self) -> None:
        self.use_dagstuhl()
        self.dagstuhl_path.write_text(self.dagstuhl_html + " ")
        self.reject("captured Dagstuhl evidence SHA-256")

    def test_dagstuhl_substituted_metadata_is_rejected(self) -> None:
        substitutions = (
            (
                "https://creativecommons.org/licenses/by/4.0/legalcode",
                "https://example.org/license",
                "license identity",
            ),
            ('content="10.4230/LIPIcs.ITP.2021.21"', 'content="10.4230/LIPIcs.ITP.2021.22"', "DOI identity"),
            ("Proving Quantum Programs Correct", "Different paper", "title identity"),
            ('name="citation_pdf_url" content="https:', 'name="citation_pdf_url" content="http:', "PDF identity"),
            ('rel="canonical" href="https:', 'rel="canonical" href="http:', "canonical identity"),
            (
                'name="citation_abstract_html_url" content="https:',
                'name="citation_abstract_html_url" content="http:',
                "abstract identity",
            ),
        )
        for original, replacement, error in substitutions:
            with self.subTest(error=error):
                self.use_dagstuhl()
                self.dagstuhl_html = self.dagstuhl_html.replace(original, replacement)
                self.write_dagstuhl_capture()
                self.reject("captured Dagstuhl " + error)

    def test_dagstuhl_duplicate_or_missing_metadata_is_rejected(self) -> None:
        for field, error in (
            ("DC.Rights", "license"),
            ("citation_doi", "DOI"),
            ("citation_title", "title"),
            ("citation_pdf_url", "PDF"),
            ("citation_abstract_html_url", "abstract"),
        ):
            for copies in (0, 2):
                with self.subTest(field=field, copies=copies):
                    self.use_dagstuhl()
                    pattern = r'<meta name="' + re.escape(field) + r'" content="[^"]*">'
                    match = re.search(pattern, self.dagstuhl_html)
                    if match is None:
                        self.fail("missing test fixture field")
                    self.dagstuhl_html = self.dagstuhl_html.replace(match[0], match[0] * copies)
                    self.write_dagstuhl_capture()
                    self.reject("captured Dagstuhl " + error + " identity")

    def test_dagstuhl_duplicate_attributes_are_rejected(self) -> None:
        self.use_dagstuhl()
        self.dagstuhl_html = self.dagstuhl_html.replace('name="DC.Rights"', 'name="DC.Rights" name="DC.Rights"')
        self.write_dagstuhl_capture()
        self.reject("captured Dagstuhl duplicate attributes")

    def test_dagstuhl_footer_license_cannot_replace_article_grant(self) -> None:
        self.use_dagstuhl()
        self.dagstuhl_html = self.dagstuhl_html.replace('name="DC.Rights"', 'name="site-license"')
        self.write_dagstuhl_capture()
        self.reject("captured Dagstuhl license identity")

    def test_dagstuhl_other_download_host_is_rejected(self) -> None:
        self.use_dagstuhl()
        original = self.entry["source_url"]
        self.entry["source_url"] = original.replace("drops.dagstuhl.de", "example.org")
        self.dagstuhl_html = self.dagstuhl_html.replace(original, self.entry["source_url"])
        self.write_dagstuhl_capture()
        self.reject("captured Dagstuhl publisher download route")

    def test_dagstuhl_path_traversal_is_rejected(self) -> None:
        self.use_dagstuhl()
        self.entry["rights"]["evidence_path"] = "docs/evidence/source_rights/../unexpected.html"
        self.reject("captured Dagstuhl evidence path")

    def test_dagstuhl_invalid_encoding_is_rejected(self) -> None:
        self.use_dagstuhl()
        payload = b"\xff"
        self.dagstuhl_path.write_bytes(payload)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(payload).hexdigest()
        self.reject("captured Dagstuhl HTML encoding")

    def test_versioned_arxiv_source_with_versionless_local_filename_passes(self) -> None:
        self.verify()

    def test_cc0_grant_passes(self) -> None:
        self.entry["rights"].update(
            license_identifier="CC0-1.0",
            license_url=LICENSE_URLS["CC0-1.0"],
            observed_license_url=LICENSE_URLS["CC0-1.0"],
        )
        self.arxiv_html = self.arxiv_html.replace(
            "http://creativecommons.org/licenses/by/4.0/", LICENSE_URLS["CC0-1.0"]
        )
        self.write_arxiv_capture()
        self.verify()

    def test_missing_or_nonobject_rights_are_rejected(self) -> None:
        values: tuple[Any, ...] = (None, [], "verified")
        for value in values:
            with self.subTest(value=value):
                self.entry["rights"] = value
                self.reject("source rights object")

    def test_unverified_or_truthy_rights_are_rejected(self) -> None:
        for value in (False, None, 1, "true"):
            with self.subTest(value=value):
                self.entry["rights"]["verified"] = value
                self.reject("source rights verification")

    def test_pdf_identity_change_is_rejected(self) -> None:
        self.entry["rights"]["pdf_sha256"] = "0" * 64
        self.reject("rights PDF identity")

    def test_required_evidence_metadata_is_checked(self) -> None:
        original = copy.deepcopy(self.entry["rights"])
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("pdf_sha256", "broken", "rights PDF SHA-256"),
            ("evidence_sha256", "broken", "rights evidence SHA-256"),
            ("evidence_url", "file:///metadata", "rights evidence URL"),
            ("verified_at_utc", "2026-10-12", "rights verification timestamp"),
            ("verified_at_utc", "invalid", "rights verification timestamp"),
            ("evidence_locator", " ", "rights evidence_locator"),
            ("reading_scope", None, "rights reading_scope"),
            ("evidence_summary", [], "rights evidence_summary"),
            ("license_identifier", False, "rights license_identifier"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field, value=value):
                self.entry["rights"] = copy.deepcopy(original)
                self.entry["rights"][field] = value
                self.reject(message)

    def test_publication_admission_mutations_are_rejected(self) -> None:
        original = copy.deepcopy(self.entry)
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("status", "external_only", "published retention status"),
            ("redistribution", "excluded_without_permission", "published redistribution status"),
            ("decision", "external_only", "published rights decision"),
            ("license_identifier", "LicenseRef-arXiv-nonexclusive-distrib-1.0", "published license allowlist"),
            ("license_url", LICENSE_URLS["CC0-1.0"], "published license URL"),
            ("copy_status", "modified", "published copy status"),
            ("conditions", "", "published license conditions"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                self.entry = copy.deepcopy(original)
                target = self.entry if field in {"status", "redistribution"} else self.entry["rights"]
                target[field] = value
                self.reject(message)

    def test_changed_payload_is_rejected(self) -> None:
        self.payload += b"changed"
        self.reject("published rights payload identity")

    def test_missing_payload_is_rejected(self) -> None:
        self.payload = b""
        self.reject("published PDF payload")

    def test_missing_operative_license_document_is_rejected(self) -> None:
        del self.registry["license_documents"]["CC-BY-4.0"]
        self.reject("operative license document")

    def test_operative_license_evidence_mutations_are_rejected(self) -> None:
        original = copy.deepcopy(self.registry["license_documents"]["CC-BY-4.0"])
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("url", "https://example.org/terms", "operative license URL"),
            ("sha256", "broken", "operative license SHA-256"),
            ("reading_scope", "", "operative license reading scope"),
            ("verified_at_utc", "2026-10-12T07:00:00", "operative license timestamp"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                document = copy.deepcopy(original)
                self.registry["license_documents"]["CC-BY-4.0"] = document
                document[field] = value
                self.reject(message)

    def test_versionless_arxiv_retrieval_url_is_rejected(self) -> None:
        self.entry["source_url"] = "https://arxiv.org/pdf/1904.00633"
        self.reject("arXiv source version")

    def test_different_arxiv_evidence_version_is_rejected(self) -> None:
        self.entry["rights"]["evidence_url"] = "https://arxiv.org/abs/1904.00633v1"
        self.reject("arXiv evidence version")

    def test_arxiv_nonexclusive_grant_cannot_be_relabelled_cc_by(self) -> None:
        self.entry["rights"]["observed_license_url"] = LICENSE_URLS["LicenseRef-arXiv-nonexclusive-distrib-1.0"]
        self.reject("arXiv license identity")

    def test_external_arxiv_grants_pass(self) -> None:
        for identifier in set(LICENSE_URLS) - PUBLIC_LICENSES:
            with self.subTest(identifier=identifier):
                self.use_external_arxiv(identifier)
                self.verify(published=False)

    def test_external_arxiv_capture_without_observed_spelling_passes(self) -> None:
        self.use_external_arxiv()
        del self.entry["rights"]["observed_license_url"]
        self.verify(published=False)

    def test_external_arxiv_capture_observed_spelling_is_checked_when_recorded(self) -> None:
        self.use_external_arxiv()
        self.entry["rights"]["observed_license_url"] = LICENSE_URLS["LicenseRef-arXiv-nonexclusive-distrib-1.0"]
        self.reject("captured arXiv observed license identity", published=False)

    def test_external_arxiv_capture_tampering_is_rejected(self) -> None:
        self.use_external_arxiv()
        self.arxiv_path.write_bytes(self.arxiv_path.read_bytes() + b" ")
        self.reject("captured arXiv evidence SHA-256", published=False)

    def test_external_arxiv_capture_missing_file_is_rejected(self) -> None:
        self.use_external_arxiv()
        self.arxiv_path.unlink()
        self.reject("captured arXiv evidence file", published=False)

    def test_external_arxiv_capture_metadata_is_required(self) -> None:
        self.use_external_arxiv()
        original = copy.deepcopy(self.entry["rights"])
        for field, value, message in (
            ("evidence_path", None, "captured arXiv evidence path"),
            ("evidence_path", "/tmp/arxiv.html", "captured arXiv evidence path"),
            ("evidence_path", "docs/evidence/source_rights/../arxiv.html", "captured arXiv evidence path"),
            ("evidence_retrieved_at_utc", "2026-10-12T16:00:00", "captured arXiv retrieval timestamp"),
            ("evidence_retrieved_at_utc", None, "captured arXiv retrieval timestamp"),
        ):
            with self.subTest(field=field, value=value):
                self.entry["rights"] = copy.deepcopy(original)
                self.entry["rights"][field] = value
                self.reject(message, published=False)

    def test_external_arxiv_capture_file_symlink_is_rejected(self) -> None:
        self.use_external_arxiv()
        target = self.root / "other.html"
        self.arxiv_path.rename(target)
        self.arxiv_path.symlink_to(target)
        self.reject("captured arXiv evidence file", published=False)

    def test_external_arxiv_capture_directory_symlink_is_rejected(self) -> None:
        self.use_external_arxiv()
        directory = self.arxiv_path.parent
        target = self.root / "other-captures"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)
        self.reject("captured arXiv evidence file", published=False)

    def test_external_arxiv_semantic_mutations_are_rejected_after_rehash(self) -> None:
        self.use_external_arxiv()
        original = self.arxiv_html
        for before, after, message in (
            ('content="1904.00633"', 'content="1908.09855"', "captured arXiv citation identity"),
            ("/pdf/1904.00633v2", "/pdf/1904.00633v1", "captured arXiv download version"),
            (
                "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
                "http://arxiv.org/licenses/assumed-1991-2003/",
                "captured arXiv license identity",
            ),
            ('title="Rights to this article"', 'title="Site rights"', "captured arXiv license anchor"),
            ('class="abs-license"', 'class="footer-license"', "captured arXiv license count"),
        ):
            with self.subTest(before=before):
                self.arxiv_html = original.replace(before, after)
                self.write_arxiv_capture()
                self.reject(message, published=False)

    def test_external_publication_decision_is_rejected(self) -> None:
        self.reject("external-only rights decision", published=False)

    def test_external_arxiv_grant_mismatch_is_rejected(self) -> None:
        self.entry["rights"].update(
            decision="external_only",
            license_identifier="LicenseRef-arXiv-nonexclusive-distrib-1.0",
            license_url=LICENSE_URLS["CC-BY-4.0"],
        )
        self.reject("arXiv license identity", published=False)

    def test_legacy_arxiv_identifier_passes(self) -> None:
        self.entry["source_url"] = "https://arxiv.org/pdf/math/0511691v1"
        self.entry["rights"].update(
            evidence_url="https://arxiv.org/abs/math/0511691v1",
            decision="external_only",
            license_identifier="LicenseRef-arXiv-assumed-1991-2003",
            license_url=LICENSE_URLS["LicenseRef-arXiv-assumed-1991-2003"],
        )
        del self.entry["rights"]["evidence_path"]
        del self.entry["rights"]["evidence_retrieved_at_utc"]
        self.verify(published=False)

    def test_matched_zenodo_deposit_passes(self) -> None:
        self.use_zenodo()
        self.verify()

    def test_unsupported_public_evidence_route_is_rejected(self) -> None:
        self.use_zenodo()
        self.entry["rights"]["evidence_url"] = "https://example.org/license"
        self.reject("published license evidence route")

    def test_missing_zenodo_file_is_rejected(self) -> None:
        self.use_zenodo()
        del self.entry["rights"]["licensed_file"]
        self.reject("licensed deposit file")

    def test_zenodo_identity_mutations_are_rejected(self) -> None:
        self.use_zenodo()
        original = copy.deepcopy(self.entry["rights"]["licensed_file"])
        mutations: tuple[tuple[str, Any, str], ...] = (
            (
                "url",
                "https://zenodo.org/api/records/20445734/files/paper.pdf/content",
                "licensed deposit record identity",
            ),
            ("sha256", "0" * 64, "licensed deposit SHA-256"),
            ("bytes", len(self.payload) + 1, "licensed deposit size"),
            ("bytes", True, "licensed deposit size"),
            ("md5", "0" * 32, "licensed deposit MD5"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                deposited_file = copy.deepcopy(original)
                self.entry["rights"]["licensed_file"] = deposited_file
                deposited_file[field] = value
                self.reject(message)

    def test_captured_zenodo_evidence_is_required(self) -> None:
        self.use_zenodo()
        del self.entry["rights"]["evidence_path"]
        self.reject("captured Zenodo evidence path")

    def test_missing_captured_zenodo_file_is_rejected(self) -> None:
        self.use_zenodo()
        self.zenodo_path.unlink()
        self.reject("captured Zenodo evidence file")

    def test_captured_zenodo_symlink_is_rejected(self) -> None:
        self.use_zenodo()
        target = self.root / "other.json"
        self.zenodo_path.rename(target)
        self.zenodo_path.symlink_to(target)
        self.reject("captured Zenodo evidence file")

    def test_captured_zenodo_tampering_is_rejected(self) -> None:
        self.use_zenodo()
        self.zenodo_path.write_bytes(self.zenodo_path.read_bytes() + b" ")
        self.reject("captured Zenodo evidence SHA-256")

    def test_captured_zenodo_malformed_json_is_rejected_after_rehash(self) -> None:
        self.use_zenodo()
        raw_response = b"{invalid-json}"
        self.zenodo_path.write_bytes(raw_response)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(raw_response).hexdigest()
        self.reject("captured Zenodo JSON")

    def test_zenodo_declared_license_relabeling_is_rejected(self) -> None:
        self.use_zenodo()
        self.entry["rights"].update(
            license_identifier="CC0-1.0",
            license_url=LICENSE_URLS["CC0-1.0"],
            observed_license_url=LICENSE_URLS["CC0-1.0"],
        )
        self.reject("captured Zenodo license identity")

    def test_zenodo_captured_license_change_is_rejected_after_rehash(self) -> None:
        self.use_zenodo()
        self.zenodo_record["metadata"]["license"]["id"] = "all-rights-reserved"
        self.write_zenodo_capture()
        self.reject("captured Zenodo license identity")

    def test_captured_zenodo_record_identity_mutations_are_rejected_after_rehash(self) -> None:
        self.use_zenodo()
        original = copy.deepcopy(self.zenodo_record)
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("id", 20445734, "captured Zenodo record identity"),
            ("id", "20431754", "captured Zenodo record identity"),
            ("links", {"self": "https://zenodo.org/api/records/20445734"}, "captured Zenodo record URL"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field, value=value):
                self.zenodo_record = copy.deepcopy(original)
                self.zenodo_record[field] = value
                self.write_zenodo_capture()
                self.reject(message)

    def test_captured_zenodo_file_mutations_are_rejected_after_rehash(self) -> None:
        self.use_zenodo()
        original = copy.deepcopy(self.zenodo_record["files"][0])
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("key", "unrelated.pdf", "captured Zenodo file key"),
            ("size", len(self.payload) + 1, "captured Zenodo file size"),
            ("size", True, "captured Zenodo file size"),
            ("checksum", "md5:" + "0" * 32, "captured Zenodo file checksum"),
            ("links", {"self": "https://example.org/unrelated.pdf"}, "captured Zenodo matching file"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field):
                deposited_file = copy.deepcopy(original)
                self.zenodo_record["files"] = [deposited_file]
                deposited_file[field] = value
                self.write_zenodo_capture()
                self.reject(message)

    def test_captured_zenodo_missing_and_duplicate_files_are_rejected(self) -> None:
        self.use_zenodo()
        original = copy.deepcopy(self.zenodo_record["files"][0])
        for files in ([], [original, copy.deepcopy(original)]):
            with self.subTest(file_count=len(files)):
                self.zenodo_record["files"] = files
                self.write_zenodo_capture()
                self.reject("captured Zenodo matching file")

    def test_captured_zenodo_unrelated_file_is_allowed(self) -> None:
        self.use_zenodo()
        unrelated = copy.deepcopy(self.zenodo_record["files"][0])
        unrelated.update(key="supplement.pdf", links={"self": "https://example.org/supplement.pdf"})
        self.zenodo_record["files"].append(unrelated)
        self.write_zenodo_capture()
        self.verify()

    def test_coordinated_pdf_and_registry_replacement_is_rejected(self) -> None:
        self.use_zenodo()
        self.payload = self.payload[:-1] + b"!"
        digest = hashlib.sha256(self.payload).hexdigest()
        self.entry["sha256"] = digest
        self.entry["rights"]["pdf_sha256"] = digest
        self.entry["rights"]["licensed_file"].update(
            sha256=digest, md5=hashlib.md5(self.payload, usedforsecurity=False).hexdigest()
        )
        self.reject("captured Zenodo file checksum")

    def test_captured_arxiv_digest_must_match(self) -> None:
        self.entry["rights"]["evidence_sha256"] = "3" * 64
        self.reject("captured arXiv evidence SHA-256")

    def test_captured_arxiv_metadata_is_required(self) -> None:
        original = copy.deepcopy(self.entry["rights"])
        mutations: tuple[tuple[str, Any, str], ...] = (
            ("evidence_path", None, "captured arXiv evidence path"),
            ("evidence_path", "/tmp/1904.00633v2.html", "captured arXiv evidence path"),
            ("evidence_path", "docs/evidence/source_rights/../1904.00633v2.html", "captured arXiv evidence path"),
            ("evidence_retrieved_at_utc", None, "captured arXiv retrieval timestamp"),
        )
        for field, value, message in mutations:
            with self.subTest(field=field, value=value):
                self.entry["rights"] = copy.deepcopy(original)
                self.entry["rights"][field] = value
                self.reject(message)

    def test_missing_captured_arxiv_file_is_rejected(self) -> None:
        self.arxiv_path.unlink()
        self.reject("captured arXiv evidence file")

    def test_captured_arxiv_symlink_is_rejected(self) -> None:
        target = self.root / "other.html"
        self.arxiv_path.rename(target)
        self.arxiv_path.symlink_to(target)
        self.reject("captured arXiv evidence file")

    def test_captured_arxiv_directory_symlink_is_rejected(self) -> None:
        directory = self.arxiv_path.parent
        target = self.root / "other-captures"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)
        self.reject("captured arXiv evidence file")

    def test_captured_arxiv_tampering_is_rejected(self) -> None:
        self.arxiv_path.write_bytes(self.arxiv_path.read_bytes() + b" ")
        self.reject("captured arXiv evidence SHA-256")

    def test_captured_arxiv_encoding_is_checked_after_rehash(self) -> None:
        raw = self.arxiv_path.read_bytes() + b"\xff"
        self.arxiv_path.write_bytes(raw)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(raw).hexdigest()
        self.reject("captured arXiv HTML encoding")

    def test_coordinated_arxiv_license_relabeling_is_rejected(self) -> None:
        self.entry["rights"].update(
            license_identifier="CC0-1.0",
            license_url=LICENSE_URLS["CC0-1.0"],
            observed_license_url=LICENSE_URLS["CC0-1.0"],
        )
        self.reject("captured arXiv license identity")

    def test_captured_arxiv_https_license_passes(self) -> None:
        self.arxiv_html = self.arxiv_html.replace("http://creativecommons.org/", "https://creativecommons.org/")
        self.entry["rights"]["observed_license_url"] = LICENSE_URLS["CC-BY-4.0"]
        self.write_arxiv_capture()
        self.verify()

    def test_captured_arxiv_observed_license_must_match(self) -> None:
        self.entry["rights"]["observed_license_url"] = LICENSE_URLS["CC-BY-4.0"]
        self.reject("captured arXiv observed license identity")

    def test_captured_arxiv_absolute_download_url_passes(self) -> None:
        self.arxiv_html = self.arxiv_html.replace('href="/pdf/', 'href="https://arxiv.org/pdf/')
        self.write_arxiv_capture()
        self.verify()

    def test_captured_arxiv_identity_mutations_are_rejected_after_rehash(self) -> None:
        original = self.arxiv_html
        citation = '<meta name="citation_arxiv_id" content="1904.00633">'
        download = '<a class="download-pdf" href="/pdf/1904.00633v2"><span>PDF</span></a>'
        mutations = (
            (citation, "", "captured arXiv citation identity"),
            (citation, citation + citation, "captured arXiv citation identity"),
            (citation, citation.replace("1904.00633", "1908.09855"), "captured arXiv citation identity"),
            (citation, citation.replace(' content="1904.00633"', ""), "captured arXiv citation metadata"),
            (download, "", "captured arXiv download count"),
            (download, download + download, "captured arXiv download count"),
            ("/pdf/1904.00633v2", "/pdf/1904.00633v1", "captured arXiv download version"),
            ("/pdf/1904.00633v2", "/pdf/1904.00633", "captured arXiv download version"),
            (' href="/pdf/1904.00633v2"', "", "captured arXiv download URL"),
        )
        for before, after, message in mutations:
            with self.subTest(after=after, message=message):
                self.arxiv_html = original.replace(before, after)
                self.write_arxiv_capture()
                self.reject(message)

    def test_captured_arxiv_license_mutations_are_rejected_after_rehash(self) -> None:
        original = self.arxiv_html
        section = original.split('<div class="abs-license">', 1)[1].split("</div></div>", 1)[0]
        section = '<div class="abs-license">' + section + "</div></div>"
        anchor = '<a class="has_license" href="http://creativecommons.org/licenses/by/4.0/">'
        mutations = (
            (section, "", "captured arXiv license count"),
            (section, section + section, "captured arXiv license count"),
            (anchor, '<a class="has_license">', "captured arXiv license URL"),
            ('class="has_license"', 'class="footer-license"', "captured arXiv license anchor"),
            (
                "http://creativecommons.org/licenses/by/4.0/",
                "https://example.org/license",
                "captured arXiv license identity",
            ),
            ("</span></a></div></div>", "</span></div></div>", "captured arXiv evidence nesting"),
            (
                "</span></a></div></div>",
                "</span></a>" + anchor + "extra</a></div></div>",
                "captured arXiv license count",
            ),
        )
        for before, after, message in mutations:
            with self.subTest(after=after, message=message):
                self.arxiv_html = original.replace(before, after)
                self.write_arxiv_capture()
                self.reject(message)

    def test_captured_arxiv_footer_cannot_supply_article_license(self) -> None:
        self.arxiv_html = self.arxiv_html.replace('class="abs-license"', 'class="unrelated"')
        self.write_arxiv_capture()
        self.reject("captured arXiv license count")

    def test_captured_arxiv_duplicate_attributes_are_rejected_after_rehash(self) -> None:
        original = self.arxiv_html
        for before, after in (
            ('name="citation_arxiv_id"', 'name="citation_arxiv_id" name="other"'),
            ('class="download-pdf"', 'class="download-pdf" class="other"'),
            ('class="abs-license"', 'class="abs-license" class="other"'),
            ('class="has_license"', 'class="has_license" href="https://example.org/license"'),
        ):
            with self.subTest(before=before):
                self.arxiv_html = original.replace(before, after)
                self.write_arxiv_capture()
                self.reject("captured arXiv duplicate attributes")

    def test_captured_arxiv_unclosed_evidence_is_rejected_after_rehash(self) -> None:
        original = self.arxiv_html
        for suffix in ("<span>PDF</span>", "<span>view license</span>"):
            with self.subTest(suffix=suffix):
                self.arxiv_html = original.split(suffix, 1)[0] + suffix
                self.write_arxiv_capture()
                self.reject("captured arXiv unclosed evidence")


class ExternalArticleCaptureChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="external-article-capture-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.capture = self.root / "docs/evidence/source_rights/greenberg-1966-article.html"
        self.capture.parent.mkdir(parents=True)
        self.entry: dict[str, Any] = {
            "title": "Rational points in henselian discrete valuation rings",
            "source_url": "https://pmihes.centre-mersenne.org/item/10.1007/BF02684802.pdf",
            "sha256": "3" * 64,
            "rights": rights_fixture("3" * 64, external=True),
        }
        self.entry["rights"].update(
            evidence_url="https://pmihes.centre-mersenne.org/articles/10.1007/BF02684802/",
            evidence_path=self.capture.relative_to(self.root).as_posix(),
            evidence_retrieved_at_utc="2026-10-12T16:21:46+00:00",
        )
        self.html = (
            '<html><head><meta name="citation_doi" content="10.1007/BF02684802">'
            '<meta name="citation_title" content="' + self.entry["title"] + '">'
            '<meta name="citation_pdf_url" content="' + self.entry["source_url"] + '"></head>'
            "<body><footer>Metadata CC0; article rights require manual inspection.</footer></body></html>"
        )
        self.write_capture()

    def write_capture(self) -> None:
        payload = self.html.encode("utf-8")
        self.capture.write_bytes(payload)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(payload).hexdigest()

    def verify(self) -> None:
        verify_source_rights(self.entry, {}, root=self.root, published=False)

    def reject(self, message: str) -> None:
        with self.assertRaisesRegex(ValueError, "^" + re.escape(message) + "$"):
            self.verify()

    def test_retained_external_article_capture_passes(self) -> None:
        self.verify()

    def test_historical_external_article_without_capture_passes(self) -> None:
        del self.entry["rights"]["evidence_path"]
        del self.entry["rights"]["evidence_retrieved_at_utc"]
        self.capture.unlink()
        self.verify()

    def test_changed_capture_bytes_are_rejected(self) -> None:
        self.capture.write_bytes(self.capture.read_bytes() + b" ")
        self.reject("captured external evidence SHA-256")

    def test_missing_capture_is_rejected(self) -> None:
        self.capture.unlink()
        self.reject("captured external evidence file")

    def test_capture_metadata_mutations_are_rejected(self) -> None:
        original = copy.deepcopy(self.entry["rights"])
        for field, value, message in (
            ("evidence_path", None, "source capture path"),
            ("evidence_path", "/tmp/article.html", "source capture path"),
            ("evidence_path", "docs/evidence/source_rights/../article.html", "source capture path"),
            ("evidence_path", "docs/evidence/source_rights/subdir/article.html", "source capture path"),
            ("evidence_retrieved_at_utc", None, "captured external retrieval timestamp"),
            ("evidence_retrieved_at_utc", "2026-10-12T16:00:00", "captured external retrieval timestamp"),
            (
                "evidence_url",
                "https://pmihes.centre-mersenne.org/articles/10.1007/OTHER/",
                "captured external article evidence identity",
            ),
        ):
            with self.subTest(field=field, value=value):
                self.entry["rights"] = copy.deepcopy(original)
                self.entry["rights"][field] = value
                self.reject(message)

    def test_capture_symlink_is_rejected(self) -> None:
        target = self.root / "other.html"
        self.capture.rename(target)
        self.capture.symlink_to(target)
        self.reject("captured external evidence file")

    def test_capture_directory_symlink_is_rejected(self) -> None:
        directory = self.capture.parent
        target = self.root / "other-captures"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)
        self.reject("captured external evidence file")

    def test_unknown_captured_publisher_requires_an_identity_route(self) -> None:
        self.entry["source_url"] = "https://example.org/article.pdf"
        self.reject("captured external article source route")

    def test_rehashed_article_metadata_substitutions_are_rejected(self) -> None:
        original = self.html
        for before, after, message in (
            ('content="10.1007/BF02684802"', 'content="10.1007/OTHER"', "captured external article DOI identity"),
            (self.entry["title"], "Unrelated article", "captured external article title identity"),
            (self.entry["source_url"], "https://example.org/article.pdf", "captured external article PDF identity"),
        ):
            with self.subTest(before=before):
                self.html = original.replace(before, after)
                self.write_capture()
                self.reject(message)

    def test_rehashed_missing_duplicate_and_footer_metadata_are_rejected(self) -> None:
        original = self.html
        for field, label in (("citation_doi", "DOI"), ("citation_pdf_url", "PDF"), ("citation_title", "title")):
            match = re.search(r'<meta name="' + field + r'" content="[^"]+">', original)
            self.assertIsNotNone(match)
            if match is None:
                raise AssertionError("Missing fixture field")
            for copies in (0, 2):
                with self.subTest(field=field, copies=copies):
                    self.html = original.replace(match[0], match[0] * copies)
                    self.write_capture()
                    self.reject(f"captured external article {label} identity")

    def test_rehashed_duplicate_attributes_are_rejected(self) -> None:
        self.html = self.html.replace('name="citation_doi"', 'name="citation_doi" name="other"')
        self.write_capture()
        self.reject("captured external article duplicate attributes")

    def test_invalid_capture_encoding_is_rejected_after_rehash(self) -> None:
        payload = b"\xff"
        self.capture.write_bytes(payload)
        self.entry["rights"]["evidence_sha256"] = hashlib.sha256(payload).hexdigest()
        self.reject("captured external HTML encoding")


class CaptureInventoryChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="source-capture-inventory-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.directory = self.root / "docs/evidence/source_rights"
        self.directory.mkdir(parents=True)
        (self.directory / "README.md").write_text("Captured evidence and manual-audit boundary\n")
        self.registry: dict[str, Any] = {"pdfs": [], "external_pdfs": []}
        for section, filename in (("pdfs", "hosted.html"), ("external_pdfs", "external.html")):
            capture = self.directory / filename
            capture.write_bytes(b"retained response")
            self.registry[section].append(
                {
                    "rights": {
                        "evidence_path": capture.relative_to(self.root).as_posix(),
                        "evidence_retrieved_at_utc": "2026-10-12T16:00:00+00:00",
                    }
                }
            )
        self.registry["external_pdfs"].append({"rights": {"evidence_url": "https://example.org/manual-audit"}})

    def reject(self, message: str) -> None:
        with self.assertRaisesRegex(ValueError, "^" + re.escape(message) + "$"):
            verify_capture_inventory(self.root, self.registry)

    def test_closed_inventory_and_manual_audit_count_pass(self) -> None:
        self.assertEqual(verify_capture_inventory(self.root, self.registry), (2, 1))

    def test_duplicate_registered_capture_is_rejected(self) -> None:
        self.registry["external_pdfs"].append(copy.deepcopy(self.registry["pdfs"][0]))
        self.reject("duplicate source capture path")

    def test_missing_registered_capture_is_rejected(self) -> None:
        (self.directory / "external.html").unlink()
        self.reject("source capture file")

    def test_registered_capture_symlink_is_rejected(self) -> None:
        source = self.directory / "external.html"
        target = self.root / "outside.html"
        source.rename(target)
        source.symlink_to(target)
        self.reject("source capture file")

    def test_unregistered_capture_file_directory_and_symlink_are_rejected(self) -> None:
        extra = self.directory / "extra.html"
        extra.write_text("unregistered")
        self.reject("source capture inventory differs from registry")
        extra.unlink()
        extra.mkdir()
        self.reject("source capture inventory differs from registry")
        extra.rmdir()
        extra.symlink_to(self.root / "missing")
        self.reject("source capture inventory differs from registry")

    def test_removing_capture_registration_leaves_an_orphan(self) -> None:
        rights = self.registry["external_pdfs"][0]["rights"]
        del rights["evidence_path"]
        self.reject("source capture path")
        del rights["evidence_retrieved_at_utc"]
        self.reject("source capture inventory differs from registry")

    def test_capture_directory_symlink_is_rejected(self) -> None:
        target = self.root / "other-captures"
        self.directory.rename(target)
        self.directory.symlink_to(target, target_is_directory=True)
        self.reject("source capture directory")

    def test_capture_ancestor_symlink_is_rejected(self) -> None:
        ancestor = self.root / "docs"
        target = self.root / "other-docs"
        ancestor.rename(target)
        ancestor.symlink_to(target, target_is_directory=True)
        self.reject("source capture directory")

    def test_capture_readme_symlink_is_rejected(self) -> None:
        readme = self.directory / "README.md"
        target = self.root / "other.md"
        readme.rename(target)
        readme.symlink_to(target)
        self.reject("source capture README")


class SourceArchiveChecks(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="source-archive-check-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "docs/source_archives/research-source.tar.gz"
        self.source.parent.mkdir(parents=True)
        self.note = self.root / "docs/notes/research-source.md"
        self.note.parent.mkdir()
        self.commit = "a" * 40
        self.prefix = f"research-{self.commit}"
        license_payload = (
            b"MIT License\nCopyright (c) Research authors\n"
            b"Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            b"of this software and associated documentation files to distribute the Software.\n"
            b"The above copyright notice and this permission notice shall be included\n"
            b"in all copies or substantial portions of the Software.\n"
        )
        source_payload = b"Theorem identity : 1 = 1. Proof. reflexivity. Qed.\n"
        self.members: list[tuple[tarfile.TarInfo, bytes]] = []
        for name, payload in (("LICENSE", license_payload), ("Identity.v", source_payload)):
            info = tarfile.TarInfo(f"{self.prefix}/{name}")
            info.size = len(payload)
            self.members.append((info, payload))
        self.entry: dict[str, Any] = {
            "path": self.source.relative_to(self.root).as_posix(),
            "source_url": f"https://codeload.github.com/author/research/tar.gz/{self.commit}",
            "version": self.commit + " (source snapshot)",
            "title": "Research source",
            "authors": ["Research authors"],
            "retrieved_at_utc": "2026-10-12T16:23:09+00:00",
            "reading_scope": "Identity theorem and license notice",
            "compatibility": "Source inspected; build untested",
            "copy_status": "unchanged",
            "conditions": "Retain original copyright and license notices.",
            "note": self.note.relative_to(self.root).as_posix(),
            "license_identifier": "MIT",
            "license_member": self.members[0][0].name,
            "license_bytes": len(license_payload),
            "license_sha256": hashlib.sha256(license_payload).hexdigest(),
            "inspected_files": [
                {
                    "file": self.members[1][0].name,
                    "bytes": len(source_payload),
                    "sha256": hashlib.sha256(source_payload).hexdigest(),
                }
            ],
        }
        self.registry: dict[str, Any] = {"source_archives": [self.entry]}
        self.write_archive()

    def write_note(self) -> None:
        self.note.write_text(f"{self.entry['source_url']}\n{self.entry['sha256']}\n")

    def seal_payload(self, payload: bytes) -> None:
        self.source.write_bytes(payload)
        self.entry.update(sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload))
        self.write_note()

    def write_archive(self) -> None:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for member, payload in self.members:
                archive.addfile(member, io.BytesIO(payload) if member.isfile() else None)
        self.seal_payload(buffer.getvalue())

    def reject(self, message: str) -> None:
        with self.assertRaisesRegex(ValueError, "^" + re.escape(message) + "$"):
            verify_source_archives(self.root, self.registry)

    def test_complete_archive_passes_without_extraction(self) -> None:
        with (
            patch.object(tarfile.TarFile, "extract", side_effect=AssertionError("filesystem extraction")),
            patch.object(tarfile.TarFile, "extractall", side_effect=AssertionError("filesystem extraction")),
        ):
            self.assertEqual(verify_source_archives(self.root, self.registry), 1)
        self.assertEqual(list(self.source.parent.iterdir()), [self.source])

    def test_uninspected_symlink_is_preserved_without_following_it(self) -> None:
        member = tarfile.TarInfo(f"{self.prefix}/uninspected-link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        self.members.append((member, b""))
        self.write_archive()
        self.assertEqual(verify_source_archives(self.root, self.registry), 1)

    def test_empty_inventory_passes(self) -> None:
        self.registry["source_archives"] = []
        self.source.unlink()
        self.source.parent.rmdir()
        self.assertEqual(verify_source_archives(self.root, self.registry), 0)

    def test_registry_shape_is_required(self) -> None:
        for value in (None, {"unexpected": True}, "archives"):
            with self.subTest(value=value):
                self.registry["source_archives"] = value
                self.reject("source archive registry")

    def test_inventory_rejects_unregistered_files_and_directories(self) -> None:
        extra = self.source.parent / "extra"
        extra.write_bytes(b"unregistered")
        self.reject("source archive inventory differs from registry")
        extra.unlink()
        extra.mkdir()
        self.reject("source archive inventory differs from registry")

    def test_archive_path_and_file_mutations_are_rejected(self) -> None:
        for path in ("/tmp/source.tar.gz", "docs/source_archives/../source.tar.gz", "docs/source_archives/x.zip"):
            with self.subTest(path=path):
                self.entry["path"] = path
                self.reject("source archive path")
        self.entry["path"] = self.source.relative_to(self.root).as_posix()
        self.source.unlink()
        self.reject("source archive file")

    def test_archive_file_symlink_is_rejected(self) -> None:
        target = self.root / "outside.tar.gz"
        self.source.rename(target)
        self.source.symlink_to(target)
        self.reject("source archive file")

    def test_archive_directory_symlink_is_rejected(self) -> None:
        directory = self.source.parent
        target = self.root / "outside"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)
        self.reject("source archive directory symlink")

    def test_ancestor_directory_symlink_is_rejected(self) -> None:
        directory = self.root / "docs"
        target = self.root / "outside"
        directory.rename(target)
        directory.symlink_to(target, target_is_directory=True)
        self.reject("source archive directory boundary")

    def test_duplicate_archive_path_and_digest_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.entry)
        self.registry["source_archives"].append(duplicate)
        self.reject("duplicate source archive path")
        duplicate["path"] = "docs/source_archives/duplicate.tar.gz"
        (self.root / duplicate["path"]).write_bytes(self.source.read_bytes())
        self.reject("duplicate source archive digest")

    def test_archive_size_and_digest_mutations_are_rejected(self) -> None:
        original = copy.deepcopy(self.entry)
        for field, value, message in (
            ("bytes", True, "source archive size"),
            ("bytes", 0, "source archive size"),
            ("bytes", original["bytes"] + 1, "source archive size identity"),
            ("sha256", "broken", "source archive SHA-256"),
            ("sha256", "0" * 64, "source archive digest identity"),
        ):
            with self.subTest(field=field, value=value):
                self.entry.update(original)
                self.entry[field] = value
                self.reject(message)

    def test_provenance_mutations_are_rejected(self) -> None:
        original = copy.deepcopy(self.entry)
        for field, value, message in (
            ("title", "", "archive title"),
            ("authors", [], "archive authors"),
            ("authors", [""], "archive author"),
            ("reading_scope", None, "archive reading_scope"),
            ("compatibility", False, "archive compatibility"),
            ("conditions", "", "archive conditions"),
            ("retrieved_at_utc", "2026-10-12T16:00:00", "archive retrieval timestamp"),
            ("copy_status", "modified", "archive copy status"),
            ("version", "main", "archive pinned version"),
            ("source_url", "https://codeload.github.com/author/research/tar.gz/main", "archive source route"),
            ("source_url", "http://codeload.github.com/author/research/tar.gz/" + self.commit, "archive source route"),
        ):
            with self.subTest(field=field, value=value):
                self.entry.update(original)
                self.entry[field] = value
                self.reject(message)

    def test_owning_note_identity_and_boundary_are_required(self) -> None:
        original = self.entry["note"]
        self.entry["note"] = "docs/notes/../elsewhere.md"
        self.reject("archive owning note path")
        self.entry["note"] = original
        self.note.write_text(self.entry["source_url"])
        self.reject("archive owning note identity")
        self.note.write_text(self.entry["sha256"])
        self.reject("archive owning note identity")
        self.note.unlink()
        self.reject("archive owning note file")

    def test_owning_note_symlink_is_rejected(self) -> None:
        target = self.root / "outside.md"
        self.note.rename(target)
        self.note.symlink_to(target)
        self.reject("archive owning note file")

    def test_invalid_tar_is_rejected_after_rehash(self) -> None:
        self.seal_payload(b"invalid archive")
        self.reject("invalid source archive")

    def test_member_path_and_duplicate_names_are_rejected_after_rehash(self) -> None:
        original = self.members[1][0].name
        for name in ("/absolute.v", "../outside.v", self.prefix + "/../outside.v", "wrong-root/Identity.v"):
            with self.subTest(name=name):
                self.members[1][0].name = name
                self.write_archive()
                self.reject("archive member path")
        self.members[1][0].name = original
        self.members.append(copy.deepcopy(self.members[1]))
        self.write_archive()
        self.reject("duplicate archive member")

    def test_license_identifier_and_text_must_agree(self) -> None:
        self.entry["license_identifier"] = "unknown"
        self.reject("archive license allowlist")
        self.entry["license_identifier"] = "CECILL-C"
        self.reject("archive license text identity")

    def test_license_member_identity_is_required(self) -> None:
        original = copy.deepcopy(self.entry)
        for field, value, message in (
            ("license_member", self.prefix + "/MISSING", "archive member missing"),
            ("license_bytes", True, "archive member size"),
            ("license_bytes", self.entry["license_bytes"] + 1, "archive member size identity"),
            ("license_sha256", "broken", "archive member SHA-256"),
            ("license_sha256", "0" * 64, "archive member digest identity"),
        ):
            with self.subTest(field=field, value=value):
                self.entry.update(original)
                self.entry[field] = value
                self.reject(message)

    def test_linked_license_member_is_rejected(self) -> None:
        for kind in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            with self.subTest(kind=kind):
                self.members[0][0].type = kind
                self.members[0][0].linkname = self.members[1][0].name
                self.write_archive()
                self.reject("archive inspected member must be regular")

    def test_inspected_file_identity_is_required(self) -> None:
        original = copy.deepcopy(self.entry["inspected_files"][0])
        for field, value, message in (
            ("file", self.prefix + "/MISSING.v", "archive member missing"),
            ("bytes", True, "archive member size"),
            ("bytes", original["bytes"] + 1, "archive member size identity"),
            ("sha256", "0" * 64, "archive member digest identity"),
        ):
            with self.subTest(field=field, value=value):
                record = copy.deepcopy(original)
                record[field] = value
                self.entry["inspected_files"] = [record]
                self.reject(message)
        self.entry["inspected_files"] = [original, original]
        self.reject("duplicate archive inspected file")
        self.entry["inspected_files"] = []
        self.reject("archive inspected files")

    def test_changed_inspected_bytes_are_rejected_after_archive_rehash(self) -> None:
        member, payload = self.members[1]
        replacement = payload.replace(b"1 = 1", b"1 = 2")
        self.members[1] = (member, replacement)
        self.write_archive()
        self.reject("archive member digest identity")

    def test_versioned_interval_route_is_bound_to_archive_root(self) -> None:
        old_prefix = self.prefix
        self.prefix = "interval-4.11.5"
        self.entry.update(
            source_url="https://coqinterval.gitlabpages.inria.fr/releases/interval-4.11.5.tar.gz",
            version="4.11.5",
        )
        for member, _ in self.members:
            member.name = member.name.replace(old_prefix, self.prefix)
        self.entry["license_member"] = self.members[0][0].name
        self.entry["inspected_files"][0]["file"] = self.members[1][0].name
        self.write_archive()
        self.assertEqual(verify_source_archives(self.root, self.registry), 1)
        self.entry["version"] = "4.11.4"
        self.reject("archive pinned version")


class HostedArxivCaptureChecks(unittest.TestCase):
    def test_all_registered_hosted_arxiv_captures(self) -> None:
        root = Path(__file__).resolve().parents[1]
        registry = json.loads((root / "docs/SOURCES.json").read_text())
        entries = [entry for entry in registry["pdfs"] if entry["source_url"].startswith("https://arxiv.org/pdf/")]
        self.assertTrue(entries)
        for entry in entries:
            with self.subTest(source=entry["source_url"]):
                verify_source_rights(
                    entry, registry, root=root, published=True, payload=(root / entry["path"]).read_bytes()
                )


if __name__ == "__main__":
    unittest.main()
