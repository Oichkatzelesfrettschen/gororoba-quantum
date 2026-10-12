"""Exercise publication and optional-cache guards in isolated temporary fixtures."""

from __future__ import annotations

import copy
import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from verify_sources import LICENSE_URLS, PUBLIC_LICENSES, verify_external_sources, verify_source_rights


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

    def verify(self, *, published: bool = True) -> None:
        verify_source_rights(self.entry, self.registry, published=published, payload=self.payload)

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

    def test_versioned_arxiv_source_with_versionless_local_filename_passes(self) -> None:
        self.verify()

    def test_cc0_grant_passes(self) -> None:
        self.entry["rights"].update(
            license_identifier="CC0-1.0",
            license_url=LICENSE_URLS["CC0-1.0"],
            observed_license_url=LICENSE_URLS["CC0-1.0"],
        )
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
                self.entry["rights"].update(
                    decision="external_only", license_identifier=identifier, license_url=LICENSE_URLS[identifier]
                )
                self.verify(published=False)

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


if __name__ == "__main__":
    unittest.main()
