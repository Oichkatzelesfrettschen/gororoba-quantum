"""Content-addressed store for a run's compiled circuit archive.

A run directory holds its compiled Runtime PUB circuits either as the file ``isa.qpy`` beside
``record.json`` (every run retained before the store existed, and every submitted run) or as a pointer
file ``isa.qpy.sha256`` naming the archive in the sibling store ``<out>/archives/<sha256>.qpy``. The
store writes each distinct archive once, so the dry runs of one day that compile the same circuits share
one copy. Readers call :func:`read_archive`, which resolves either shape and verifies the bytes against
the digest the run recorded, so a tampered or misplaced archive raises before any circuit is decoded.

A submitted run materializes ``isa.qpy`` in its own directory: the retention audits, the inventory
reconciliation and the collection of a retained run bind that path by digest, and a retained directory
stays self-contained.
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import tempfile
from pathlib import Path

ARCHIVE_FILE = "isa.qpy"
POINTER_FILE = "isa.qpy.sha256"
STORE_DIRECTORY = "archives"
_DIGEST = re.compile(r"[0-9a-f]{64}")


class ArchiveError(ValueError):
    """The archive a run names is absent, misplaced or differs from its recorded digest."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def store_directory(run_dir: Path) -> Path:
    """The content store shared by the run directories under one output root."""
    return run_dir.parent / STORE_DIRECTORY


def store_path(run_dir: Path, digest: str) -> Path:
    if not _DIGEST.fullmatch(digest):
        raise ArchiveError(f"{run_dir}: archive pointer {digest!r} is not a sha256 hex digest")
    return store_directory(run_dir) / f"{digest}.qpy"


def _publish_once(target: Path, data: bytes) -> None:
    """Write ``data`` to ``target`` unless an identical file exists; a different existing file raises.

    A temporary file in the same directory and ``os.replace`` make the publication atomic, so a reader
    never sees a partial archive and two writers of the same digest leave one identical file.
    """
    if target.is_symlink():
        raise ArchiveError(f"archive store entry must be a regular file: {target}")
    if target.is_file():
        if target.read_bytes() != data:
            raise ArchiveError(f"{target}: stored archive differs from the bytes with its digest")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".pending-", delete=False) as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
        pending = Path(handle.name)
    # NamedTemporaryFile creates its file with mode 0600; a retained archive is readable like record.json.
    pending.chmod(0o644)
    try:
        if target.is_file():
            if target.read_bytes() != data:
                raise ArchiveError(f"{target}: stored archive differs from the bytes with its digest")
            pending.unlink()
            return
        os.replace(pending, target)
    except BaseException:
        pending.unlink(missing_ok=True)
        raise
    directory_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _replace_atomically(target: Path, data: bytes) -> None:
    """Write beside ``target``, fsync, and ``os.replace`` over it: an interruption leaves the old file whole."""
    tmp = target.with_name(target.name + ".tmp")
    with open(tmp, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, target)
    directory_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def write_archive(run_dir: Path, data: bytes, *, materialize: bool = False) -> str:
    """Store ``data`` once under its digest, point the run at it, and return the digest.

    With ``materialize``, or when the run directory already holds ``isa.qpy``, the archive is also
    written as ``isa.qpy`` beside the record, the shape every submitted run keeps.
    """
    digest = sha256_hex(data)
    _publish_once(store_path(run_dir, digest), data)
    _replace_atomically(run_dir / POINTER_FILE, (digest + "\n").encode())
    if materialize or (run_dir / ARCHIVE_FILE).is_file():
        _replace_atomically(run_dir / ARCHIVE_FILE, data)
    return digest


def materialize(run_dir: Path) -> Path:
    """Write the run's archive as ``isa.qpy`` beside its record from the store, and return that path."""
    target = run_dir / ARCHIVE_FILE
    if not target.is_file():
        _replace_atomically(target, read_archive(run_dir))
    return target


def pointer_digest(run_dir: Path) -> str | None:
    """The digest the run's pointer file names, or None when the run keeps no pointer."""
    pointer = run_dir / POINTER_FILE
    if not pointer.is_file():
        return None
    digest = pointer.read_text(encoding="utf-8").strip()
    if not _DIGEST.fullmatch(digest):
        raise ArchiveError(f"{pointer}: pointer text {digest!r} is not a sha256 hex digest")
    return digest


def archive_path(run_dir: Path) -> Path:
    """The file holding the run's archive: ``isa.qpy`` beside the record, else the store entry it points at."""
    local = run_dir / ARCHIVE_FILE
    if local.is_file():
        return local
    digest = pointer_digest(run_dir)
    if digest is None:
        raise ArchiveError(f"{run_dir}: no {ARCHIVE_FILE} and no {POINTER_FILE} pointer")
    stored = store_path(run_dir, digest)
    if not stored.is_file():
        raise ArchiveError(f"{run_dir}: archive {digest[:12]} is absent from {stored.parent}")
    return stored


def archive_link(run_dir: Path) -> str:
    """The archive's path relative to the run directory, for a document written beside the record."""
    return os.path.relpath(archive_path(run_dir), run_dir)


def has_archive(run_dir: Path) -> bool:
    try:
        return archive_path(run_dir).is_file()
    except ArchiveError:
        return False


def read_archive(run_dir: Path, *, expected_sha256: str | None = None) -> bytes:
    """The archive bytes, verified against the pointer digest and against ``expected_sha256`` when given."""
    path = archive_path(run_dir)
    data = path.read_bytes()
    digest = sha256_hex(data)
    pointer = pointer_digest(run_dir) if path.name != ARCHIVE_FILE else None
    if pointer is not None and digest != pointer:
        raise ArchiveError(f"{path}: bytes digest {digest[:12]} differs from the pointer {pointer[:12]}")
    if expected_sha256 is not None and digest != expected_sha256.lower():
        raise ArchiveError(f"{path}: bytes digest {digest[:12]} differs from the recorded {expected_sha256[:12]}")
    return data


def archive_sha256(run_dir: Path) -> str:
    """The sha256 of the run's archive bytes, read through :func:`read_archive`."""
    return sha256_hex(read_archive(run_dir))


def open_archive(run_dir: Path, *, expected_sha256: str | None = None) -> io.BytesIO:
    """A seekable stream over the verified archive bytes for ``qpy.load``."""
    return io.BytesIO(read_archive(run_dir, expected_sha256=expected_sha256))
