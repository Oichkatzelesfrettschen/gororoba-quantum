"""The content-addressed archive store resolves, deduplicates and verifies a run's compiled circuits."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import run_archive


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _run(root: Path, name: str) -> Path:
    run_dir = root / name
    run_dir.mkdir()
    return run_dir


def test_dry_run_keeps_a_pointer_and_shares_one_stored_copy(tmp_path: Path) -> None:
    data = b"qpy bytes of one compiled circuit set"
    digest = hashlib.sha256(data).hexdigest()
    first, second = _run(tmp_path, "first"), _run(tmp_path, "second")
    _require(run_archive.write_archive(first, data) == digest, "the first write returns the sha256")
    _require(run_archive.write_archive(second, data) == digest, "the second write returns the same sha256")
    store = tmp_path / run_archive.STORE_DIRECTORY
    _require(sorted(path.name for path in store.iterdir()) == [f"{digest}.qpy"], "the store holds one copy")
    for run_dir in (first, second):
        _require(not (run_dir / run_archive.ARCHIVE_FILE).exists(), f"{run_dir.name}: a dry run writes no isa.qpy")
        _require((run_dir / run_archive.POINTER_FILE).read_text() == digest + "\n", "the pointer names the digest")
        _require(run_archive.archive_path(run_dir) == store / f"{digest}.qpy", "the pointer resolves into the store")
        _require(run_archive.read_archive(run_dir) == data, "the stored bytes read back")
        _require(run_archive.archive_sha256(run_dir) == digest, "the digest reads back")
        _require(run_archive.has_archive(run_dir), "the run has an archive")


def test_submission_materializes_the_archive_beside_the_record(tmp_path: Path) -> None:
    data = b"submitted circuits"
    run_dir = _run(tmp_path, "run")
    run_archive.write_archive(run_dir, data, materialize=True)
    _require((run_dir / run_archive.ARCHIVE_FILE).read_bytes() == data, "a submission writes isa.qpy")
    _require(run_archive.archive_path(run_dir) == run_dir / run_archive.ARCHIVE_FILE, "the local file wins")
    run_archive.write_archive(run_dir, b"recompiled")
    _require(
        (run_dir / run_archive.ARCHIVE_FILE).read_bytes() == b"recompiled",
        "a later write of a materialized run keeps the local shape",
    )


def test_materialize_copies_the_stored_archive_into_the_run(tmp_path: Path) -> None:
    data = b"stored first"
    run_dir = _run(tmp_path, "run")
    run_archive.write_archive(run_dir, data)
    _require(run_archive.materialize(run_dir) == run_dir / run_archive.ARCHIVE_FILE, "materialize returns isa.qpy")
    _require((run_dir / run_archive.ARCHIVE_FILE).read_bytes() == data, "materialize copies the stored bytes")


def test_a_retained_run_with_only_isa_qpy_resolves_locally(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, "legacy")
    (run_dir / run_archive.ARCHIVE_FILE).write_bytes(b"legacy archive")
    _require(run_archive.read_archive(run_dir) == b"legacy archive", "a retained run reads its own isa.qpy")
    _require(run_archive.archive_path(run_dir) == run_dir / run_archive.ARCHIVE_FILE, "the local path resolves")


def test_tampered_store_entry_and_wrong_expected_digest_raise(tmp_path: Path) -> None:
    data = b"original"
    run_dir = _run(tmp_path, "run")
    digest = run_archive.write_archive(run_dir, data)
    stored = tmp_path / run_archive.STORE_DIRECTORY / f"{digest}.qpy"
    with pytest.raises(run_archive.ArchiveError, match="differs from the recorded"):
        run_archive.read_archive(run_dir, expected_sha256="0" * 64)
    stored.write_bytes(b"altered")
    with pytest.raises(run_archive.ArchiveError, match="differs from the pointer"):
        run_archive.read_archive(run_dir)
    with pytest.raises(run_archive.ArchiveError, match="stored archive differs"):
        run_archive.write_archive(_run(tmp_path, "other"), data)


def test_missing_archive_and_malformed_pointer_raise(tmp_path: Path) -> None:
    run_dir = _run(tmp_path, "bare")
    _require(not run_archive.has_archive(run_dir), "a bare directory has no archive")
    with pytest.raises(run_archive.ArchiveError, match="no isa.qpy and no isa.qpy.sha256"):
        run_archive.archive_path(run_dir)
    (run_dir / run_archive.POINTER_FILE).write_text("not-a-digest\n")
    with pytest.raises(run_archive.ArchiveError, match="not a sha256 hex digest"):
        run_archive.archive_path(run_dir)
    (run_dir / run_archive.POINTER_FILE).write_text("a" * 64 + "\n")
    with pytest.raises(run_archive.ArchiveError, match="is absent from"):
        run_archive.archive_path(run_dir)
