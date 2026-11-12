"""Admit retained E8 standard-monomial bases through payload, producer and exact-export checks.

The digest-bound e8_target_basis_v2.py remains the arithmetic producer. Its replay subcommand is a historical
interface. Current admission verifies the successor producer, its e8_target_rank.py predecessor, the registered
field and complete data-source bindings before replaying the standard monomials and radical normal forms through
the predecessor's exact Singular export. The verifier changes no retained basis or arc-jet record.

    "$PYTHON" docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_target_basis_verify.py \
        docs/evidence/a5-exceptional-fibers/monomial-ladder/target-records/e8nm-p32009-d7-basis.json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e8_target_basis_v2 as producer  # noqa: E402

base_producer = producer.T


def replay(record: dict[str, Any], singular: str, timeout: int, scratch: Path) -> dict[str, Any]:
    """Reject changed payload/source identities before the exact retained-ideal export reaches the solver."""
    base_producer.validate_basis(record)
    target = producer.targets.TARGETS.get(record["target"])
    if target is None:
        raise ValueError("the record names an unregistered target")
    if (record["prime"], record["root"], record["nvars"]) != (
        target.prime,
        target.root,
        producer.targets.NGEN,
    ):
        raise ValueError("the record field or coordinates differ from the registered target")
    if record.get("producer_sha256") != base_producer.digest(Path(producer.__file__)):
        raise ValueError("the successor producer digest differs from the record")
    if record.get("base_producer_sha256") != base_producer.digest(Path(base_producer.__file__)):
        raise ValueError("the base producer digest differs from the record")
    if record["sources"] != base_producer.bound_inputs(target):
        raise ValueError("the complete bound inputs differ from the record")
    base_producer.verify_export(record, singular, timeout, scratch)
    return {
        "target": record["target"],
        "degree": record["degree"],
        "monomials": len(record["monomials"]),
        "status": "replayed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("basis", type=Path)
    parser.add_argument("--singular", default="Singular")
    parser.add_argument("--timeout", type=int, default=300)
    arguments = parser.parse_args()
    with tempfile.TemporaryDirectory() as scratch:
        summary = replay(
            json.loads(arguments.basis.read_text(encoding="utf-8")),
            arguments.singular,
            arguments.timeout,
            Path(scratch) / "replayed-basis.json",
        )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
