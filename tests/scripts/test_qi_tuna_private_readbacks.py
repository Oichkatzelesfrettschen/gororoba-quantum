"""Private readback storage must retain exact bytes and refuse reuse."""

import hashlib
import os
from pathlib import Path

import pytest


def test_private_store_replays_exact_checkpoint_and_readbacks(tmp_path: Path) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks
    from qi_tuna_readback_transport import Readback

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    checkpoint = b'{"job":11,"file":12,"batch":14,"result":21}'
    bodies = [b'{"id":11}', b'{"items":[]}', b'{"id":12}', b'{"items":[]}']
    locators = [
        ("/jobs/11", ()),
        ("/batch_jobs", (("id", 14), ("page", 1), ("size", 100))),
        ("/files/12", ()),
        ("/results/job/11", (("page", 1), ("size", 100))),
    ]
    receipts = tuple(
        Readback(path, query, 200, "application/json", body, hashlib.sha256(body).hexdigest())
        for (path, query), body in zip(locators, bodies, strict=True)
    )
    try:
        with PrivateReadbackStore(directory) as store:
            store.retain_checkpoint(checkpoint)
            for receipt in receipts:
                store.retain_readback(receipt)
        capture = load_private_readbacks(directory)
        if capture.checkpoint_bytes != checkpoint or capture.readbacks != receipts:
            raise AssertionError("private capture did not replay exact inputs")
        with pytest.raises(ValueError):
            PrivateReadbackStore(directory)
        for path in directory_path.iterdir():
            if path.stat().st_mode & 0o077:
                raise AssertionError("private capture exposed an artifact to other users")
        (directory_path / "job.body").write_bytes(b"{}")
        with pytest.raises(ValueError):
            load_private_readbacks(directory)
    finally:
        os.close(directory)


def test_insecure_directory_is_rejected(tmp_path: Path) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore

    directory_path = tmp_path / "public"
    directory_path.mkdir(mode=0o700)
    directory_path.chmod(0o755)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(ValueError):
            PrivateReadbackStore(directory)
    finally:
        os.close(directory)


def test_sync_failure_latches_store_and_partial_capture_cannot_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)

    def fail_sync(_descriptor: int) -> None:
        raise OSError("fixture sync failure")

    try:
        with PrivateReadbackStore(directory) as store:
            monkeypatch.setattr(os, "fsync", fail_sync)
            with pytest.raises(OSError):
                store.retain_checkpoint(b'{"job":11,"file":12,"batch":14,"result":21}')
            with pytest.raises(ValueError):
                store.retain_checkpoint(b'{"job":11,"file":12,"batch":14,"result":21}')
        with pytest.raises(ValueError):
            load_private_readbacks(directory)
    finally:
        os.close(directory)


def test_out_of_order_retention_latches_the_store(tmp_path: Path) -> None:
    from qi_tuna_private_readbacks import PrivateReadbackStore
    from qi_tuna_readback_transport import Readback

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    body = b"{}"
    receipt = Readback("/jobs/11", (), 200, "application/json", body, hashlib.sha256(body).hexdigest())
    try:
        with PrivateReadbackStore(directory) as store:
            with pytest.raises(ValueError):
                store.retain_readback(receipt)
            with pytest.raises(ValueError):
                store.retain_checkpoint(b'{"job":11,"file":12,"batch":14,"result":21}')
    finally:
        os.close(directory)
