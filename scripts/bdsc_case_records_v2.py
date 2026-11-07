"""Versioned successors of the bdsc diagnostic and stationarity case builders that state qd_platform.job_billing.

scripts/bdsc_diagnostic.py and scripts/bdsc_stationarity.py keep their bytes because each `--check` compares the
retained case tree byte for byte with a fresh build. This producer rebuilds either tree, replaces the
/resources/billing_rule field that docs/evidence/quandela-billing-rule-successor/README.md supersedes with
billing_rule_v2.RULE, and rewrites each job manifest's digest of the case record (`diagnostic_case_sha256` or
`stationarity_case_sha256`) to the successor record's sha256, so every manifest names the record it ships with.
The credit figure stays: it is the ceiling at the frozen max_shots. Each job manifest carries
`acquisition_admission` billing_rule_v2.ADMISSION, which qd_platform.submit refuses, because the original readouts
admit only the original case record; the writer refuses a directory under billing_rule_v2.RECORD_ROOTS.

Usage:
  "$PYTHON" scripts/bdsc_case_records_v2.py diagnostic --write DIR [--draw DRAW_JSON]
  "$PYTHON" scripts/bdsc_case_records_v2.py stationarity --check DIR
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_diagnostic as diag  # noqa: E402
import bdsc_stationarity as st  # noqa: E402
from billing_rule_v2 import RULE, admit_none, outside_records, supersede  # noqa: E402

OLD_RULE = "1 credit per job plus 1e-6 per shot of the job's largest iteration max_shots"
# CASE_DIGEST maps each family to the job-manifest field that carries the sha256 of its case.json.
CASE_DIGEST = {"diagnostic": "diagnostic_case_sha256", "stationarity": "stationarity_case_sha256"}

Documents = dict[str, bytes | dict[str, bytes]]


def original(family: str, draw: Path | None) -> Documents:
    if family == "diagnostic":
        return diag.documents(draw)
    diag.require(draw is None, "the stationarity case takes its seeds from its source manifests, not a draw")
    return st.documents()


def documents(family: str, draw: Path | None = None) -> Documents:
    """The original builder's documents with the billing field replaced and the case digest re-bound."""
    out = original(family, draw)
    case_bytes = out["case.json"]
    if not isinstance(case_bytes, bytes):
        raise ValueError("case.json is not a record")
    record = json.loads(case_bytes)
    supersede(record, ("resources", "billing_rule"), OLD_RULE, RULE)
    record_bytes = (json.dumps(record, indent=1) + "\n").encode()
    out["case.json"] = record_bytes
    field = CASE_DIGEST[family]
    for name, files in out.items():
        if isinstance(files, dict):
            manifest: dict[str, Any] = json.loads(files["cases.json"])
            diag.require(manifest.get(field) == diag.sha256_bytes(case_bytes), f"{name}: {field} names another case")
            manifest[field] = diag.sha256_bytes(record_bytes)
            admit_none(manifest)
            files["cases.json"] = (json.dumps(manifest, indent=1) + "\n").encode()
    return out


def write(family: str, directory: Path, draw: Path | None) -> None:
    outside_records(ROOT, directory)
    for name, content in documents(family, draw).items():
        if isinstance(content, bytes):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / name).write_bytes(content)
            continue
        (directory / name).mkdir(parents=True, exist_ok=True)
        for file, data in content.items():
            (directory / name / file).write_bytes(data)
    print(f"bdsc {family} (billing successor): wrote case.json and the job directories under {directory}")


def check(family: str, directory: Path, draw: Path | None) -> None:
    """Every file under `directory` equals a fresh build byte for byte, and no job directory is extra or missing."""
    fresh = documents(family, draw)
    diag.require((directory / "case.json").read_bytes() == fresh["case.json"], "case.json differs from a fresh build")
    jobs = sorted(name for name in fresh if name != "case.json")
    present = sorted(p.name for p in directory.iterdir() if p.is_dir())
    diag.require(present == jobs, f"job directories differ: {sorted(set(present) ^ set(jobs))}")
    for job in jobs:
        files = fresh[job]
        if isinstance(files, dict):
            for name, data in files.items():
                diag.require((directory / job / name).read_bytes() == data, f"{job}/{name} differs from a fresh build")
    print(f"bdsc {family} (billing successor): case.json and {len(jobs)} job directories match a fresh build")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("family", choices=sorted(CASE_DIGEST))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, metavar="DIR")
    group.add_argument("--check", type=Path, metavar="DIR")
    parser.add_argument("--draw", type=Path, help="ANU QRNG draw record that seeds a diagnostic build")
    args = parser.parse_args()
    if args.write is not None:
        write(args.family, args.write, args.draw)
    else:
        check(args.family, args.check, args.draw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
