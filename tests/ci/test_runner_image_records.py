"""Contract for ci/runner_image_records.py: the image digest follows the installed requirement lines and every
other input byte, the ledger check names each record to rewrite once the digest moves, and add binds only
bytes that a runner-image write receipted.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest
import runner_image_records as records

ROOT = Path(__file__).resolve().parents[2]


def copy_inputs(target: Path) -> None:
    for name in records.IMAGE_INPUTS:
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target / name)
    shutil.copytree(ROOT / "ci" / "patches", target / "ci" / "patches", dirs_exist_ok=True)


@pytest.mark.audit
def test_digest_ignores_requirement_comments_and_follows_pins() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        copy_inputs(root)
        before = records.image_id(root)
        requirements = root / "ci" / "requirements-ci.txt"
        requirements.write_text("# a rewritten comment\n\n" + requirements.read_text().replace("\n", "  # note\n"))
        if records.image_id(root) != before:
            raise AssertionError("a comment edit moved the image digest")
        requirements.write_text(requirements.read_text() + "extra-package==1.0\n")
        if records.image_id(root) == before:
            raise AssertionError("an added pin left the image digest unchanged")
        containerfile = root / "ci" / "runner-image" / "Containerfile"
        copy_inputs(root)
        containerfile.write_text(containerfile.read_text() + "# trailing comment\n")
        if records.image_id(root) == before:
            raise AssertionError("a Containerfile edit left the image digest unchanged")


@pytest.mark.audit
def test_check_names_records_after_the_digest_moves() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        copy_inputs(root)
        record = root / "results" / "record.json"
        record.parent.mkdir()
        record.write_text("{}\n")
        ledger = {
            "schema": records.SCHEMA,
            "image": records.image_id(root),
            "records": {"results/record.json": hashlib.sha256(record.read_bytes()).hexdigest()},
        }
        if records.problems(ledger, root):
            raise AssertionError(records.problems(ledger, root))
        record.write_text('{"changed": true}\n')
        if records.problems(ledger, root) != ["results/record.json: bytes differ from the ledger"]:
            raise AssertionError(records.problems(ledger, root))
        record.write_text("{}\n")
        moved = json.loads(json.dumps(ledger)) | {"image": "0" * 64}
        found = records.problems(moved, root)
        if len(found) != 2 or not found[1].startswith("results/record.json: written under"):
            raise AssertionError(found)


def test_add_rebinds_only_the_complete_record_set() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "ci").mkdir()
        first, second = root / "first.json", root / "second.json"
        first.write_text("{}\n")
        second.write_text("[]\n")
        ledger = root / "ci" / "runner_image_records.json"
        receipts = root / "receipts.jsonl"
        receipts.write_text(
            "".join(
                json.dumps({"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "image": image})
                + "\n"
                for image in ("old", "new")
                for path in (first, second)
            )
        )
        with (
            mock.patch.object(records, "ROOT", root),
            mock.patch.object(records, "LEDGER", ledger),
            mock.patch.object(records, "RECEIPTS", receipts),
            mock.patch.object(records, "image_id", lambda _root=root: "old"),
        ):
            if records.main(["add", str(first), str(second)]) != 0:
                raise AssertionError("binding two records failed")
        with (
            mock.patch.object(records, "ROOT", root),
            mock.patch.object(records, "LEDGER", ledger),
            mock.patch.object(records, "RECEIPTS", receipts),
            mock.patch.object(records, "image_id", lambda _root=root: "new"),
        ):
            try:
                records.main(["add", str(first)])
            except SystemExit as error:
                if "second.json" not in str(error):
                    raise AssertionError(f"a partial rebind named {error}") from error
            else:
                raise AssertionError("a partial rebind under a new image passed")
            if records.main(["add", str(first), str(second)]) != 0:
                raise AssertionError("a complete rebind under a new image failed")
        bound = json.loads(ledger.read_text())
        if bound["image"] != "new" or sorted(bound["records"]) != ["first.json", "second.json"]:
            raise AssertionError(bound)


@pytest.mark.audit
def test_check_fails_on_an_empty_or_foreign_ledger() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        copy_inputs(root)
        empty = {"schema": records.SCHEMA, "image": records.image_id(root), "records": {}}
        if records.problems(empty, root) != ["the ledger binds no record; bind each runner-image record with `add`"]:
            raise AssertionError(records.problems(empty, root))
        if not records.problems({}, root)[0].startswith("the ledger's schema is None"):
            raise AssertionError(records.problems({}, root))
        ledger = root / "ci" / "runner_image_records.json"
        with mock.patch.object(records, "ROOT", root), mock.patch.object(records, "LEDGER", ledger):
            if records.main(["check"]) != 1:
                raise AssertionError("check passed with the ledger missing")


def test_add_refuses_bytes_without_a_matching_receipt(tmp_path: Path) -> None:
    record = tmp_path / "record.json"
    record.write_text("{}\n")
    digest = hashlib.sha256(record.read_bytes()).hexdigest()
    receipts = tmp_path / "receipts.jsonl"
    ledger = tmp_path / "ci" / "runner_image_records.json"
    (tmp_path / "ci").mkdir()
    # A host-written record, a receipt for other bytes, and a receipt under another image all stay unbound.
    for rows in (
        [],
        [{"path": "record.json", "sha256": "0" * 64, "image": "now"}],
        [{"path": "record.json", "sha256": digest, "image": "before"}],
    ):
        receipts.write_text("".join(json.dumps(row) + "\n" for row in rows))
        with (
            mock.patch.object(records, "ROOT", tmp_path),
            mock.patch.object(records, "LEDGER", ledger),
            mock.patch.object(records, "RECEIPTS", receipts),
            mock.patch.object(records, "image_id", lambda _root=tmp_path: "now"),
            pytest.raises(SystemExit, match="no runner-image receipt"),
        ):
            records.main(["add", str(record)])
        if ledger.exists():
            raise AssertionError(f"an unreceipted record entered the ledger: {rows}")


def test_write_receipts_only_the_files_the_container_wrote(tmp_path: Path) -> None:
    root, cache = tmp_path / "tree", tmp_path / "cache"
    (root / "ci").mkdir(parents=True)
    (root / "ci" / "runner_image.sh").write_text("")
    (root / ".git").mkdir()
    untouched = root / "untouched.json"
    untouched.write_text("{}\n")
    receipts = cache / "receipts.jsonl"
    host = root / "host.json"

    def runner(arguments: list[str], cwd: Path, check: bool) -> subprocess.CompletedProcess[bytes]:
        if cwd == root or arguments[1] != str(cwd / "ci" / "runner_image.sh") or arguments[2:] != ["producer"]:
            raise AssertionError(f"the command ran outside a snapshot: {arguments} in {cwd}")
        if (cwd / ".git").exists():
            raise AssertionError("the snapshot carries .git")
        (cwd / "results").mkdir()
        (cwd / "results" / "record.json").write_text('{"fit": 0.5}\n')
        # A host process writing into the tree during the run leaves the snapshot alone.
        host.write_text('{"host": true}\n')
        return subprocess.CompletedProcess(arguments, 0)

    patches = (
        mock.patch.object(records, "ROOT", root),
        mock.patch.object(records, "RECEIPTS", receipts),
        mock.patch.object(records, "image_id", lambda _root=root: "now"),
    )
    with patches[0], patches[1], patches[2], mock.patch.object(records.subprocess, "run", runner):
        if records.main(["write", "producer"]) != 0:
            raise AssertionError("write failed")
    written = root / "results" / "record.json"
    rows = [json.loads(line) for line in receipts.read_text().splitlines()]
    expected = {
        "path": "results/record.json",
        "sha256": hashlib.sha256(written.read_bytes()).hexdigest(),
        "image": "now",
    }
    if rows != [expected]:
        raise AssertionError(rows)
    if [path.name for path in cache.iterdir()] != ["receipts.jsonl"]:
        raise AssertionError("the snapshot outlived the run")
    failed: subprocess.CompletedProcess[bytes] = subprocess.CompletedProcess([], 3)
    with patches[0], patches[1], patches[2], mock.patch.object(records.subprocess, "run", lambda *_a, **_k: failed):
        if records.main(["write", "producer"]) != 3:
            raise AssertionError("a failed command's status was lost")
    if len(receipts.read_text().splitlines()) != 1 or [path.name for path in cache.iterdir()] != ["receipts.jsonl"]:
        raise AssertionError("a failed command left receipts or its snapshot")
