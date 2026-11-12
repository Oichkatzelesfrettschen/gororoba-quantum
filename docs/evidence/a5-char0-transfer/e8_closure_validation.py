"""Check the retained closure-replay receipt's record, cofactor, source and diagnostic bindings.

The on-demand gate pins the receipt's complete bytes before invoking this reader. Exact arithmetic belongs to
e8_closure_certificate.py --check; wall_seconds records operational telemetry and enters no scientific decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "docs/evidence/a5-char0-transfer"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(path: Path, root: Path = ROOT) -> dict[str, int]:
    validation: dict[str, Any] = json.loads(path.read_bytes())
    _require(validation["schema"] == "a5-e8-closure-exact-check-validation/1", "unexpected validation schema")
    producer = _sha256(root / PREFIX / "e8_closure_certificate.py")
    _require(validation["certificate_producer_sha256"] == producer, "certificate producer binding differs")
    checks = validation["checks"]
    _require(len(checks) == 2 and {row["slug"] for row in checks} == {"e8-nm", "e8-np"}, "the two signs differ")
    diagnostics = 0
    for row in checks:
        slug = row["slug"]
        record_name = f"{PREFIX}/e8-closure-certificate-{slug}.json"
        _require(row["certificate"] == record_name, "certificate path differs from its sign")
        _require(_sha256(root / record_name) == row["certificate_sha256"], "certificate record binding differs")
        record = json.loads((root / record_name).read_bytes())
        _require(record["slug"] == slug and record["verdict"] == "i_equals_is", "certificate identity/verdict differs")
        for key, filename in (
            ("certificate_producer", "e8_closure_certificate.py"),
            ("slice_rings_qi", "slice_rings_qi.py"),
            ("reduction_check", "reduction_check.py"),
        ):
            _require(record["sha256"][key] == _sha256(root / PREFIX / filename), "certificate source binding differs")
        cofactor = _sha256(root / PREFIX / f"cofactors/e8-closure-{slug}.json.xz")
        _require(cofactor == row["cofactor_sha256"] == record["sha256"]["cofactor_file"], "cofactor binding differs")
        _require(row["result"]["slug"] == slug, "check result sign differs")
        _require(row["result"]["verdict"] == "i_equals_is", "exact check verdict differs")
        for kind, count in (("cofactor", 1), ("generator", 42)):
            mutation = row["result"]["mutations"][kind]
            _require(
                mutation["status"] == "completed"
                and mutation["verdict"] == "failed"
                and mutation["bad_identities"] == count,
                "completed mutation outcome differs",
            )
        _require(row["retained_generation_diagnostics_equal_before_and_after"] is True, "diagnostics changed")
        hashes = row["retained_generation_diagnostic_sha256"]
        _require(bool(hashes), "generation-diagnostic denominator is empty")
        for name, expected in hashes.items():
            candidate = Path(name)
            _require(
                candidate.parent.as_posix() == PREFIX + "/logs"
                and candidate.name.startswith("e8-closure-")
                and (f"-{slug}." in candidate.name or f"-{slug}-" in candidate.name)
                and candidate.suffix in {".log", ".time"},
                "generation-diagnostic path leaves the selected sign",
            )
            _require(_sha256(root / candidate) == expected, "generation-diagnostic binding differs")
            diagnostics += 1
    return {"checks": len(checks), "generation_diagnostics": diagnostics}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check(HERE / "e8-closure-check-validation.json"), sort_keys=True))


if __name__ == "__main__":
    main()
