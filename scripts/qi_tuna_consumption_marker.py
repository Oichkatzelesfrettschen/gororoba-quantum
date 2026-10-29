"""Create a local single-use marker for an already authenticated approval.

The caller authenticates the account, approval event, packet and directory, and
coordinates every account user in one namespace. The borrowed directory descriptor
must remain stable until duplication. This module grants no approval.
After any persistence error, the caller must quarantine the attempt even across
restart; a failed sync does not prove that a marker will survive a crash.
"""

import hashlib
import json
import os
import stat

DOMAIN = b"gororoba-qi-approval-consumption-v1\0"


def consume(directory: int, account_digest: bytes, approval_digest: bytes, packet_digest: bytes) -> str:
    """Exclusively publish and sync a marker keyed by account and approval event."""
    if type(directory) is not int or directory < 0:
        raise ValueError("marker directory descriptor is invalid")
    if any(type(value) is not bytes or len(value) != 32 for value in (account_digest, approval_digest, packet_digest)):
        raise ValueError("account, approval and packet digests must be 32 bytes")
    owned_directory = os.dup(directory)
    try:
        if not stat.S_ISDIR(os.fstat(owned_directory).st_mode):
            raise ValueError("marker directory descriptor must name a directory")
        return _consume_owned(owned_directory, account_digest, approval_digest, packet_digest)
    finally:
        os.close(owned_directory)


def _consume_owned(directory: int, account_digest: bytes, approval_digest: bytes, packet_digest: bytes) -> str:
    """Create and sync the marker relative to the privately held directory."""
    name = hashlib.sha256(DOMAIN + account_digest + approval_digest).hexdigest() + ".json"
    payload = (
        json.dumps(
            {
                "schema": "qi-approval-consumption-v1",
                "account_sha256": account_digest.hex(),
                "approval_sha256": approval_digest.hex(),
                "packet_sha256": packet_digest.hex(),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW
    descriptor = os.open(name, flags, 0o600, dir_fd=directory)
    try:
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0:
                raise OSError("marker write made no progress")
            written += count
        os.fsync(descriptor)
        os.fsync(directory)
    finally:
        os.close(descriptor)
    return name
