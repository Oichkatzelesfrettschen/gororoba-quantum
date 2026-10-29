"""Retain and reload a single private, non-overwriting readback capture.

The caller authenticates the checkpoint and responses, owns one serialized
store, places the directory outside every checkout, and verifies the parent
path, filesystem and cross-restart quarantine semantics. Mode and ownership
checks do not isolate processes with the same user identity. This module does
not establish provider truth, observation timing or scientific admissibility.
"""

import hashlib
import json
import os
import stat
from types import TracebackType

from qi_tuna_readback_collection import ReadbackCapture
from qi_tuna_readback_transport import MAX_BODY, Readback
from qi_tuna_source_association import _json_object, _positive_integer

NAMES = ("job", "batch", "file", "result")


def _private_directory(directory: int) -> int:
    if type(directory) is not int or directory < 0:
        raise ValueError("private directory descriptor is invalid")
    owned = os.dup(directory)
    try:
        info = os.fstat(owned)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
            raise ValueError("private directory must belong to the caller and deny group/other access")
        return owned
    except BaseException:
        os.close(owned)
        raise


def _locators(checkpoint_bytes: bytes) -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    checkpoint = _json_object(checkpoint_bytes)
    job = _positive_integer(checkpoint, "job")
    file = _positive_integer(checkpoint, "file")
    batch = _positive_integer(checkpoint, "batch")
    _positive_integer(checkpoint, "result")
    return (
        (f"/jobs/{job}", ()),
        ("/batch_jobs", (("id", batch), ("page", 1), ("size", 100))),
        (f"/files/{file}", ()),
        (f"/results/job/{job}", (("page", 1), ("size", 100))),
    )


def _validate_receipt(receipt: Readback, expected: tuple[str, tuple[tuple[str, int], ...]]) -> None:
    if type(receipt) is not Readback or type(receipt.path) is not str or receipt.path != expected[0]:
        raise ValueError("readback path differs from the checkpoint")
    if (
        type(receipt.query) is not tuple
        or any(
            type(item) is not tuple or len(item) != 2 or type(item[0]) is not str or type(item[1]) is not int
            for item in receipt.query
        )
        or receipt.query != expected[1]
        or type(receipt.status) is not int
        or receipt.status != 200
        or type(receipt.content_type) is not str
        or receipt.content_type.split(";", 1)[0].strip().lower() != "application/json"
        or type(receipt.body) is not bytes
        or not 0 < len(receipt.body) <= MAX_BODY
        or type(receipt.body_sha256) is not str
        or hashlib.sha256(receipt.body).hexdigest() != receipt.body_sha256
    ):
        raise ValueError("readback metadata or body differs")


def _write_exclusive(directory: int, name: str, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        written = 0
        while written < len(data):
            count = os.write(descriptor, data[written:])
            if count <= 0:
                raise OSError("private readback write made no progress")
            written += count
        os.fsync(descriptor)
        os.fsync(directory)
    finally:
        os.close(descriptor)


class PrivateReadbackStore:
    """Write one sequential capture to an initially empty private directory."""

    def __init__(self, directory: int) -> None:
        self._directory = _private_directory(directory)
        try:
            if os.listdir(self._directory):
                raise ValueError("private capture directory must be empty")
        except BaseException:
            os.close(self._directory)
            raise
        self._locators: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] | None = None
        self._next = 0
        self._failed = False
        self._closed = False

    def __enter__(self) -> "PrivateReadbackStore":
        return self

    def __exit__(
        self, _kind: type[BaseException] | None, _value: BaseException | None, _trace: TracebackType | None
    ) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            os.close(self._directory)

    def retain_checkpoint(self, checkpoint_bytes: bytes) -> None:
        if self._closed or self._failed or self._locators is not None:
            self._failed = True
            raise ValueError("private capture cannot accept a checkpoint")
        try:
            locators = _locators(checkpoint_bytes)
            _write_exclusive(self._directory, "checkpoint.json", checkpoint_bytes)
            self._locators = locators
        except BaseException:
            self._failed = True
            raise

    def retain_readback(self, receipt: Readback) -> None:
        if self._closed or self._failed or self._locators is None or self._next >= len(NAMES):
            self._failed = True
            raise ValueError("private capture cannot accept another readback")
        try:
            _validate_receipt(receipt, self._locators[self._next])
            name = NAMES[self._next]
            metadata = (
                json.dumps(
                    {
                        "schema": "qi-private-readback-v1",
                        "path": receipt.path,
                        "query": receipt.query,
                        "status": receipt.status,
                        "content_type": receipt.content_type,
                        "body_sha256": receipt.body_sha256,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
                + b"\n"
            )
            _write_exclusive(self._directory, f"{name}.body", receipt.body)
            _write_exclusive(self._directory, f"{name}.json", metadata)
            self._next += 1
        except BaseException:
            self._failed = True
            raise


def _read_private(directory: int, name: str) -> bytes:
    descriptor = os.open(name, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_uid != os.geteuid()
            or before.st_mode & 0o077
            or before.st_nlink != 1
            or not 0 < before.st_size <= MAX_BODY
        ):
            raise ValueError("private capture file metadata is invalid")
        contents = bytearray()
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            contents.extend(chunk)
            if len(contents) > MAX_BODY:
                raise ValueError("private capture file is oversized")
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or len(contents) != before.st_size:
            raise ValueError("private capture changed while reading")
        return bytes(contents)
    finally:
        os.close(descriptor)


def load_private_readbacks(directory: int) -> ReadbackCapture:
    """Reload a complete private capture; authenticate provenance separately."""
    owned = _private_directory(directory)
    try:
        expected_names = {"checkpoint.json"} | {f"{name}.{suffix}" for name in NAMES for suffix in ("body", "json")}
        if set(os.listdir(owned)) != expected_names:
            raise ValueError("private capture is incomplete or contains unexpected entries")
        checkpoint_bytes = _read_private(owned, "checkpoint.json")
        locators = _locators(checkpoint_bytes)
        receipts: list[Readback] = []
        for name, expected in zip(NAMES, locators, strict=True):
            metadata = _json_object(_read_private(owned, f"{name}.json"))
            if set(metadata) != {"schema", "path", "query", "status", "content_type", "body_sha256"}:
                raise ValueError("private readback metadata shape differs")
            if metadata["schema"] != "qi-private-readback-v1" or type(metadata["query"]) is not list:
                raise ValueError("private readback metadata is invalid")
            query = metadata["query"]
            if any(type(item) is not list or len(item) != 2 for item in query):
                raise ValueError("private readback query is invalid")
            receipt = Readback(
                metadata["path"],
                tuple(tuple(item) for item in query),
                metadata["status"],
                metadata["content_type"],
                _read_private(owned, f"{name}.body"),
                metadata["body_sha256"],
            )
            _validate_receipt(receipt, expected)
            receipts.append(receipt)
        return ReadbackCapture(checkpoint_bytes, tuple(receipts))
    finally:
        os.close(owned)
