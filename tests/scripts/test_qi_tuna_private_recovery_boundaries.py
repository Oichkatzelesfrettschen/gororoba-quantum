"""Exercise private capture recovery without treating reload as admission."""

import hashlib
import os
from pathlib import Path
from typing import Any

import pytest
from qi_tuna_readback_transport import Readback


def _receipts() -> tuple[Readback, ...]:
    body = b"{}"
    digest = hashlib.sha256(body).hexdigest()
    return (
        Readback("/jobs/11", (), 200, "application/json", body, digest),
        Readback("/batch_jobs", (("id", 14), ("page", 1), ("size", 100)), 200, "application/json", body, digest),
        Readback("/files/12", (), 200, "application/json", body, digest),
        Readback("/results/job/11", (("page", 1), ("size", 100)), 200, "application/json", body, digest),
    )


@pytest.mark.parametrize("failed_sync", [15, 16])
def test_last_metadata_sync_failure_can_leave_readable_complete_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failed_sync: int
) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    checkpoint = b'{"job":11,"file":12,"batch":14,"result":21}'
    receipts = _receipts()
    original_fsync = os.fsync
    calls = 0

    def fault_sync(descriptor: int) -> None:
        nonlocal calls
        calls += 1
        if calls == failed_sync:
            raise OSError("fixture final sync failure")
        original_fsync(descriptor)

    try:
        with PrivateReadbackStore(directory) as store:
            store.retain_checkpoint(checkpoint)
            monkeypatch.setattr(os, "fsync", fault_sync)
            for receipt in receipts[:-1]:
                store.retain_readback(receipt)
            # The counter starts after the checkpoint. Three receipt pairs
            # consume twelve calls; the last metadata sync is call 15 or 16.
            with pytest.raises(OSError, match="fixture final sync failure"):
                store.retain_readback(receipts[-1])
        capture = load_private_readbacks(directory)
        if capture.checkpoint_bytes != checkpoint or capture.readbacks != receipts:
            raise AssertionError("fixture did not expose a complete-looking capture after failed sync")
    finally:
        os.close(directory)


@pytest.mark.parametrize("substitution", ["symlink", "hardlink", "fifo", "public_mode"])
def test_reload_rejects_replaced_or_public_body(tmp_path: Path, substitution: str) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    body_path = directory_path / "job.body"
    try:
        with PrivateReadbackStore(directory) as store:
            store.retain_checkpoint(b'{"job":11,"file":12,"batch":14,"result":21}')
            for receipt in _receipts():
                store.retain_readback(receipt)
        if substitution == "public_mode":
            body_path.chmod(0o644)
        else:
            body_path.unlink()
            if substitution == "symlink":
                body_path.symlink_to("batch.body")
            elif substitution == "hardlink":
                os.link(directory_path / "batch.body", body_path)
            else:
                os.mkfifo(body_path, 0o600)
        with pytest.raises((ValueError, OSError)):
            load_private_readbacks(directory)
    finally:
        os.close(directory)


def test_final_receipt_at_expiry_can_reload_without_proving_timeliness(tmp_path: Path) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks
    from qi_tuna_readback_collection import capture_complete_readbacks

    expired = False

    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def __init__(self, position: int) -> None:
            self.position = position

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [b"{}"]

        def close(self) -> None:
            nonlocal expired
            if self.position == 3:
                expired = True

    class Session:
        def __init__(self) -> None:
            self.count = 0

        def request(self, method: str, url: str, **options: Any) -> Response:
            response = Response(self.count)
            self.count += 1
            return response

    def check_clock() -> None:
        if expired:
            raise TimeoutError("fixture observation boundary expired")

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with PrivateReadbackStore(directory) as store:
            with pytest.raises(TimeoutError, match="fixture observation boundary expired"):
                capture_complete_readbacks(
                    b'{"job":11,"file":12,"batch":14,"result":21}',
                    Session(),
                    lambda _force: None,
                    check_clock,
                    store.retain_checkpoint,
                    store.retain_readback,
                    timeout_seconds=1.0,
                )
        if len(load_private_readbacks(directory).readbacks) != 4:
            raise AssertionError("fixture did not retain the final receipt after the clock expired")
    finally:
        os.close(directory)
