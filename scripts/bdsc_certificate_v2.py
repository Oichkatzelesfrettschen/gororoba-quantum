"""Versioned successor of scripts/bdsc_certificate.py that states the qd_platform.job_billing rule.

bdsc_certificate.py keeps its bytes because evidence records pin its sha256. This producer builds the same eight
bdsc records and replaces the two billing statements that
docs/evidence/quandela-billing-rule-successor/README.md supersedes, planning.json
/resources_historical/rates/credits and qualification_case.json /resources/billing_rule, with the rule in
billing_rule_v2.RULE. Every number stays: each credit figure is the ceiling at the frozen max_shots. bdsc_cases.py
builds job manifests from the retained docs/evidence/bdsc/qualification_case.json only, so the successor records are
derivations, and the writer refuses a directory under billing_rule_v2.RECORD_ROOTS.

Usage:
  "$PYTHON" scripts/bdsc_certificate_v2.py --write DIR
  "$PYTHON" scripts/bdsc_certificate_v2.py --check DIR
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_certificate as cert  # noqa: E402
from billing_rule_v2 import RULE, outside_records, supersede  # noqa: E402

# Each SUPERSEDED row names a record, the JSON path of its billing field, the wording bdsc_certificate.py emits there
# and the successor wording that replaces it.
SUPERSEDED = (
    (
        "planning.json",
        ("resources_historical", "rates", "credits"),
        "1 per job plus 1e-6 per shot of the largest iteration, max_shots = 2 x samples",
        f"{RULE}; max_shots = 2 x samples",
    ),
    (
        "qualification_case.json",
        ("resources", "billing_rule"),
        "1 credit per job plus 1e-6 per shot of the job's largest iteration max_shots, measured on every retained "
        "qpu:belenos job (docs/runbooks/quandela-credit-optimization.md)",
        RULE,
    ),
)


def documents() -> dict[str, str]:
    """bdsc_certificate.documents() with the superseded billing fields replaced, serialized as the original."""
    out = cert.documents()
    for name, path, old, new in SUPERSEDED:
        record = json.loads(out[name])
        supersede(record, path, old, new)
        out[name] = json.dumps(record, indent=1, sort_keys=True) + "\n"
    return out


def write(directory: Path) -> None:
    """Write the records, refusing an output directory or file that resolves under a retained record root, so a
    symbolic link in an allowed directory cannot redirect a write onto a pinned record."""
    records = documents()
    for name in [None, *records]:
        outside_records(ROOT, directory if name is None else directory / name)
    directory.mkdir(parents=True, exist_ok=True)
    for name, content in records.items():
        (directory / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(cert.FILES)} bdsc records under {directory}")


def check(directory: Path) -> None:
    """The records under `directory` match a fresh build within cert.CHECK_TOLERANCE on floats."""
    fresh = documents()
    retained = sorted(p.name for p in directory.glob("*.json"))
    cert.require(retained == sorted(cert.FILES), f"record set differs: {retained}")
    for name in cert.FILES:
        cert.close(json.loads(fresh[name]), json.loads((directory / name).read_text(encoding="utf-8")), name)
    # cert.close admits floats within CHECK_TOLERANCE, so the target identity is recomputed exactly, as
    # bdsc_certificate.check does; every other record binds target_sha256.
    target = json.loads((directory / "target.json").read_text(encoding="utf-8"))
    core = {
        key: target[key]
        for key in target
        if key not in ("schema", "record", "target_sha256", "assignment", "exact_checks")
    }
    cert.require(cert.digest(core) == target["target_sha256"], "target_sha256 does not match the retained target")
    print(f"bdsc records (billing successor): {len(cert.FILES)} files match")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, metavar="DIR")
    group.add_argument("--check", type=Path, metavar="DIR")
    args = parser.parse_args()
    if args.write is not None:
        write(args.write)
    else:
        check(args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
