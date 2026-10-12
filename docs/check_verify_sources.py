"""Exercise publication and optional-cache guards in isolated temporary fixtures."""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any

from verify_sources import verify_external_sources


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


if __name__ == "__main__":
    unittest.main()
