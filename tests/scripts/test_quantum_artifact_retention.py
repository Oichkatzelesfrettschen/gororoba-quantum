"""Temporary research evidence is retained with explicit, sanitized provenance."""

import io
import json
import tarfile
from pathlib import Path

import pytest
from quantum_artifact_retention import ROOT, capture, check, digest, sanitize


def test_sanitizer_removes_identifiers_and_local_paths() -> None:
    value = json.dumps(
        {
            "token_value": "secret-value",
            "user_id": 42,
            "job_id": "public-job",
            "text": "/home/alice/project /tmp/example Bearer secret-token alice@example.org",
        }
    )
    result = sanitize(value.encode())
    if any(
        secret in result for secret in (b"secret-value", b"secret-token", b"alice@example.org", b"/home/", b"/tmp/")
    ):
        raise AssertionError("private source text escaped redaction")
    if json.loads(result)["job_id"] != "public-job":
        raise AssertionError("a public job identity was erased")


def test_capture_preserves_sources_and_rejects_retained_mutation(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "analysis.json").write_text('{"result": 3, "path": "/tmp/analysis"}')
    (source / "notes.md").write_text("unique finding")
    output = tmp_path / "retained"
    capture({"research": source}, output)
    check(output)
    record = json.loads((output / "inventory.json").read_text())
    rows = record["artifacts"]
    if len(rows) != 2 or any(row["classification"] != "retained-sanitized" for row in rows):
        raise AssertionError("the retained denominator differs")
    if (source / "notes.md").read_text() != "unique finding":
        raise AssertionError("capture changed its source")
    path = output / rows[0]["retained"]
    path.write_text("corrupted")
    with pytest.raises(ValueError, match="digest"):
        check(output)


def test_capture_expands_regular_archive_members_and_rejects_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "input.tar"
    with tarfile.open(archive, "w") as stream:
        content = b"retained finding"
        member = tarfile.TarInfo("notes.txt")
        member.size = len(content)
        stream.addfile(member, io.BytesIO(content))
    capture({"archive": archive}, tmp_path / "safe")
    check(tmp_path / "safe")
    with tarfile.open(archive, "w") as stream:
        member = tarfile.TarInfo("../escape")
        member.size = 0
        stream.addfile(member, io.BytesIO())
    with pytest.raises(ValueError, match="archive"):
        capture({"archive": archive}, tmp_path / "unsafe")


def test_generated_environment_and_reading_copy_get_explicit_dispositions(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "validation" / "environment").mkdir(parents=True)
    (source / "validation" / "environment" / "binary").write_bytes(b"\0compiled")
    (source / "2409.17948v2.txt").write_text("third-party reading text")
    output = tmp_path / "retained"
    capture({"research": source}, output)
    check(output)
    rows = json.loads((output / "inventory.json").read_text())["artifacts"]
    classes = {row["classification"] for row in rows}
    if classes != {"derived-regenerable", "external-reading-copy"}:
        raise AssertionError(classes)
    if any("retained" in row for row in rows):
        raise AssertionError("an environment or reading copy was silently published")


def test_tracked_bytes_link_to_checkout_without_historical_object_dependency(tmp_path: Path) -> None:
    output = tmp_path / "retained"
    capture({"readme": ROOT / "README.md"}, output, ROOT)
    row = json.loads((output / "inventory.json").read_text())["artifacts"][0]
    if row["classification"] != "already-retained":
        raise AssertionError("tracked bytes were duplicated")
    check(output)


def test_privacy_verifier_rejects_private_json_even_with_matching_hashes(tmp_path: Path) -> None:
    source = tmp_path / "analysis.json"
    source.write_text('{"result": 1}')
    output = tmp_path / "retained"
    capture({"analysis": source}, output)
    inventory = output / "inventory.json"
    record = json.loads(inventory.read_text())
    row = record["artifacts"][0]
    blob = b'{"token_value": "private"}\n'
    (output / row["retained"]).write_bytes(blob)
    row.update(retained_sha256=digest(blob), retained_bytes=len(blob))
    data = json.dumps(record).encode()
    inventory.write_bytes(data)
    (output / "inventory.sha256").write_text(digest(data))
    with pytest.raises(ValueError, match="unsanitized"):
        check(output)


def test_changed_path_list_preserves_original_identity(tmp_path: Path) -> None:
    source = tmp_path / "changed-files"
    original = b"first.py\0second.py\0"
    source.write_bytes(original)
    output = tmp_path / "retained"
    capture({"changed-files": source}, output)
    row = json.loads((output / "inventory.json").read_text())["artifacts"][0]
    if row["source_sha256"] != digest(original) or row["content_changed"] is not True:
        raise AssertionError("a transformed path list lost its original identity")
