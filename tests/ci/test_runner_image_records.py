"""Contract for ci/runner_image_records.py: the image digest follows the installed requirement lines and every
other input byte, and the ledger check names each record to rewrite once the digest moves.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

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
