"""Contract for ci/runner_image_records.py: the image digest follows the installed requirement lines and every
other input byte, and the ledger check names each record to rewrite once the digest moves.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import runner_image_records as records

ROOT = Path(__file__).resolve().parents[2]


def copy_inputs(target: Path) -> None:
    for name in records.IMAGE_INPUTS:
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target / name)
    shutil.copytree(ROOT / "ci" / "patches", target / "ci" / "patches", dirs_exist_ok=True)


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
        with (
            mock.patch.object(records, "ROOT", root),
            mock.patch.object(records, "LEDGER", ledger),
            mock.patch.object(records, "image_id", lambda _root=root: "old"),
        ):
            if records.main(["add", str(first), str(second)]) != 0:
                raise AssertionError("binding two records failed")
        with (
            mock.patch.object(records, "ROOT", root),
            mock.patch.object(records, "LEDGER", ledger),
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
