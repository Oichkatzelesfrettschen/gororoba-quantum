"""Validate the complete retained-case successor without changing receipt-bound compiler sources.

The matched-proposal compiler receipt binds qi_toolchain_check.py byte for
byte. A separate checker selects the complete record while retaining that
producer's source and its local compilation procedure.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from qi_toolchain_check import ROOT, SCHEMA, case_files, compiler_configs, config_digest, generate

import qi_stack

RECORD = ROOT / "docs/evidence/quantum_inspire/toolchain-complete-retained-cases.json"


def check() -> int:
    record = json.loads(RECORD.read_text())
    if record.get("schema") != SCHEMA:
        raise ValueError("the complete toolchain receipt schema differs")
    configs = {name: config_digest(config) for name, config in compiler_configs().items()}
    current = {path: (digest, backend, configs.get(backend)) for path, (digest, backend) in case_files().items()}
    rows = record["circuits"]
    recorded = {row["case"]: (row["sha256"], row["backend"], row.get("compiler_config_sha256")) for row in rows}
    if len(recorded) != len(rows) or recorded != current:
        raise ValueError("complete toolchain coverage, circuit bytes, backend or compiler configuration differs")
    if any(row["libqasm"] != "ok" or row["compiled"] != "ok" for row in rows):
        raise ValueError("the complete toolchain receipt contains failed analysis or compilation")
    print(f"complete toolchain: {len(rows)} retained circuits match their source and compiler configuration")
    if qi_stack.live("complete retained-case compiler", "checked the complete retained receipt without recompiling"):
        with tempfile.TemporaryDirectory(prefix="qi-complete-toolchain-") as temporary:
            fresh = Path(temporary) / RECORD.name
            qi_stack.run(["-B", "-W", "error", str(ROOT / "scripts/qi_toolchain_check.py"), "--out", str(fresh)])
            if fresh.read_bytes() != RECORD.read_bytes():
                raise ValueError("the complete receipt differs from the pinned local compiler replay")
        print("complete toolchain: pinned local replay matches the retained bytes")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=RECORD)
    arguments = parser.parse_args()
    if arguments.check:
        return check()
    if arguments.out.exists():
        raise ValueError("choose a new output path rather than overwrite a retained compiler receipt")
    return generate(arguments.out)


if __name__ == "__main__":
    raise SystemExit(main())
