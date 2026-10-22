"""The records written in the runner image (ci/runner_image.sh), bound to that image and its pins.

A fitted float byte-replays only under the arithmetic that wrote it: the
libm, Python build, numpy, scipy and OpenBLAS of ci/runner-image/Containerfile
and ci/install_pins.sh. ci/runner_image_records.json binds each such record's
sha256 to IMAGE_INPUTS' digest; ``check`` (a pr gate) fails once a pin, the
image or a record changes, naming the records to rewrite through
ci/runner_image.sh, before their replay gates report float differences.

``"$PYTHON" ci/runner_image_records.py add PATH...`` binds records just
written; ``check`` verifies the ledger; ``id`` prints the current digest.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ci" / "runner_image_records.json"
SCHEMA = "runner-image-records-v1"
IMAGE_INPUTS = ("ci/runner-image/Containerfile", "requirements.txt", "ci/requirements-ci.txt", "ci/install_pins.sh")


def image_id(root: Path = ROOT) -> str:
    """sha256 over each image input's path and bytes, the patches of ci/patches/ in name order last."""
    paths = [root / name for name in IMAGE_INPUTS] + sorted((root / "ci" / "patches").iterdir())
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def read(root: Path = ROOT) -> dict[str, Any]:
    path = root / LEDGER.relative_to(ROOT)
    if not path.exists():
        return {"schema": SCHEMA, "image": None, "records": {}}
    return dict(json.loads(path.read_text()))


def problems(ledger: dict[str, Any], root: Path = ROOT) -> list[str]:
    records = ledger.get("records", {})
    if not isinstance(records, dict):
        return ["the ledger's records is not a map"]
    found = []
    current = image_id(root)
    if records and ledger.get("image") != current:
        found.append(
            f"the runner image or pins changed ({ledger.get('image')} -> {current}); rewrite every record "
            "below with ci/runner_image.sh and bind them again with `add`"
        )
    for name, digest in sorted(records.items()):
        path = root / name
        if not path.is_file():
            found.append(f"{name}: missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            found.append(f"{name}: bytes differ from the ledger")
        elif found and found[0].startswith("the runner image"):
            found.append(f"{name}: written under {ledger.get('image')}")
    return found


def main(argv: list[str]) -> int:
    command, paths = (argv[0], argv[1:]) if argv else ("", [])
    if command == "id":
        print(image_id())
        return 0
    ledger = read()
    if command == "check":
        found = problems(ledger)
        for line in found:
            print(line)
        return 1 if found else 0
    if command == "add" and paths:
        records = dict(ledger.get("records", {}))
        current = image_id()
        if records and ledger.get("image") != current:
            raise SystemExit("\n".join(problems(ledger)))
        for name in paths:
            path = (Path.cwd() / name).resolve()
            records[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        text = json.dumps({"schema": SCHEMA, "image": current, "records": dict(sorted(records.items()))}, indent=1)
        LEDGER.write_text(text + "\n")
        return 0
    raise SystemExit("usage: runner_image_records.py id | check | add PATH...")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
