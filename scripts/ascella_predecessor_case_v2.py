"""Versioned successor of scripts/ascella_predecessor_case.py that states the qd_platform.job_billing rule.

ascella_predecessor_case.py keeps its bytes because admission records pin its sha256. This producer builds the
same request and replaces the /preregistered/credit_basis field that
docs/evidence/quandela-billing-rule-successor/README.md supersedes with billing_rule_v2.RULE, and records its own
sha256 as `preregistered.builder_sha256`, where the target-slot successor records its own; `analysis_sources` keeps
the set qd_platform.acquisition_sources verifies. `max_credits` and `expected_credits` keep their values, the
ceiling at the largest iteration's max_shots; `credit_ceiling` names that figure, which the original calls `charge`.
ascella_predecessor_analysis.analyze admits only the original request, so the manifest carries
`acquisition_admission` billing_rule_v2.ADMISSION, which qd_platform.submit refuses, and --build refuses a
directory under billing_rule_v2.RECORD_ROOTS.

Usage:
  "$PYTHON" scripts/ascella_predecessor_case_v2.py --build DIR
  "$PYTHON" scripts/ascella_predecessor_case_v2.py --check DIR
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import ascella_predecessor_case as original
from billing_rule_v2 import RULE, admit_none, outside_records, supersede

BUILDER = "scripts/ascella_predecessor_case_v2.py"
OLD_CREDIT_BASIS = "1 + 1e-6 times the largest iteration max_shots, once per job"


def credit_ceiling(max_shots: int) -> float:
    """The most one iterated job bills: the per-job price plus the largest iteration's max_shots."""
    return original.charge(max_shots)


def documents() -> dict[str, bytes]:
    payload = original.documents()
    manifest = json.loads(payload["cases.json"])
    supersede(manifest, ("preregistered", "credit_basis"), OLD_CREDIT_BASIS, RULE)
    manifest["preregistered"]["builder_sha256"] = original.sha256_bytes((original.ROOT / BUILDER).read_bytes())
    admit_none(manifest)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": payload["circuit.json"]}


def check(directory: Path) -> dict:
    rebuilt = documents()
    for name, data in rebuilt.items():
        retained = directory / name
        original.require(retained.is_file(), f"{retained} is missing; build the case first")
        original.require(retained.read_bytes() == data, f"{retained} differs from the builder")
    return json.loads(rebuilt["cases.json"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", type=Path, metavar="DIR", help="new request directory; retained bytes are refused")
    group.add_argument("--check", type=Path, metavar="DIR")
    args = parser.parse_args()
    directory = args.build if args.build is not None else args.check
    if args.build is not None:
        original.publish_case(outside_records(original.ROOT, directory), documents())
    sys.stdout.write(original.summary(check(directory)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
