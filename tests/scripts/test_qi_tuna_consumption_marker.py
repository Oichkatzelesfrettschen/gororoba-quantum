"""A local attempt marker must remain single-use across failures."""

import os
import stat
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest


def test_same_approval_and_packet_cannot_be_consumed_twice(tmp_path: Path) -> None:
    from qi_tuna_consumption_marker import consume

    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        with pytest.raises(FileExistsError):
            consume(directory, b"a" * 32, b"b" * 32, b"d" * 32)
    finally:
        os.close(directory)


def test_concurrent_consumers_cannot_both_create_the_marker(tmp_path: Path) -> None:
    from qi_tuna_consumption_marker import consume

    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    barrier = threading.Barrier(2)

    def contender() -> str:
        barrier.wait()
        try:
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
            return "created"
        except FileExistsError:
            return "consumed"

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _index: contender(), range(2)))
        if sorted(outcomes) != ["consumed", "created"]:
            raise AssertionError("one approval event admitted more than one local attempt")
    finally:
        os.close(directory)


def test_failed_marker_sync_does_not_restore_approval(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from qi_tuna_consumption_marker import consume

    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:

        def fail_sync(_descriptor: int) -> None:
            raise OSError("fixture sync failure")

        monkeypatch.setattr(os, "fsync", fail_sync)
        with pytest.raises(OSError):
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        with pytest.raises(FileExistsError):
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
    finally:
        os.close(directory)


def test_failed_directory_sync_leaves_marker_consumed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from qi_tuna_consumption_marker import consume

    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    real_sync = os.fsync

    def fail_directory_sync(descriptor: int) -> None:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError("fixture directory sync failure")
        real_sync(descriptor)

    try:
        monkeypatch.setattr(os, "fsync", fail_directory_sync)
        with pytest.raises(OSError):
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        with pytest.raises(FileExistsError):
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
    finally:
        os.close(directory)


def test_directory_descriptor_reuse_cannot_redirect_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from qi_tuna_consumption_marker import consume

    intended = tmp_path / "intended"
    alternate = tmp_path / "alternate"
    intended.mkdir()
    alternate.mkdir()
    directory = os.open(intended, os.O_RDONLY | os.O_DIRECTORY)
    other = os.open(alternate, os.O_RDONLY | os.O_DIRECTORY)
    original_fstat = os.fstat
    replaced = False

    def replace_after_validation(descriptor: int) -> os.stat_result:
        nonlocal replaced
        observed = original_fstat(descriptor)
        if not replaced:
            os.dup2(other, directory)
            replaced = True
        return observed

    try:
        monkeypatch.setattr(os, "fstat", replace_after_validation)
        name = consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        if not (intended / name).is_file() or (alternate / name).exists():
            raise AssertionError("marker was redirected after descriptor validation")
    finally:
        os.close(directory)
        os.close(other)


def test_marker_has_stable_identity_and_private_bound_payload(tmp_path: Path) -> None:
    from qi_tuna_consumption_marker import consume

    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        name = consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        if name != "f955883890d80ba053eaba0de45fe34c66350e8010b432068ced51271c71e341.json":
            raise AssertionError("approval consumption key changed")
        marker = tmp_path / name
        expected = (
            b'{"account_sha256":"'
            + b"61" * 32
            + b'","approval_sha256":"'
            + b"62" * 32
            + b'","packet_sha256":"'
            + b"63" * 32
            + b'","schema":"qi-approval-consumption-v1"}\n'
        )
        if marker.read_bytes() != expected or not stat.S_ISREG(marker.stat().st_mode) or marker.stat().st_mode & 0o077:
            raise AssertionError("marker content, file type or privacy differs")
    finally:
        os.close(directory)


def test_existing_symlink_consumes_the_name_without_following_it(tmp_path: Path) -> None:
    from qi_tuna_consumption_marker import consume

    target = tmp_path / "target"
    target.write_bytes(b"retained")
    marker = tmp_path / "f955883890d80ba053eaba0de45fe34c66350e8010b432068ced51271c71e341.json"
    marker.symlink_to(target.name)
    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(FileExistsError):
            consume(directory, b"a" * 32, b"b" * 32, b"c" * 32)
        if target.read_bytes() != b"retained":
            raise AssertionError("marker creation followed an existing link")
    finally:
        os.close(directory)
