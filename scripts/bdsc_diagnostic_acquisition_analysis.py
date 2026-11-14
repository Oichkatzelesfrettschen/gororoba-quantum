"""Read collected runs of a Belenos diagnostic request built by scripts/bdsc_diagnostic_acquisition_case.py.

bdsc_diagnostic.readout admits only the runs of docs/evidence/bdsc/diagnostic/case.json and qpu:belenos. This reader
takes the successor case record as its input and admits a run only when every check of `bdsc_diagnostic.admit_run`
passes against that record:

- the record equals a fresh build for the platform it names, so its sha256 is the admission key;
- the run's manifest names that sha256 as `diagnostic_case_sha256` and equals the frozen rebuild of its job for the
  record's QRNG draw (`documents`, with `draw_claims` bound to the record);
- the submission and the service report the record's platform.

`admit_run` and `readout` are rebound (gororoba_quantum/rebound.py) to the record and the platform, so the integrity
checks, the nine components of the analysis and the branch rule stay in bdsc_diagnostic.py. The report adds the
platform and the record's sha256.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_acquisition_analysis.py --case DIR/case.json RUN...
  "$PYTHON" scripts/bdsc_diagnostic_acquisition_analysis.py --case DIR/case.json --matched-check B1J2_RUN B2J1_RUN
  "$PYTHON" scripts/bdsc_diagnostic_acquisition_analysis.py --case DIR/case.json --admit-only RUN...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import bdsc_diagnostic as diag
import bdsc_diagnostic_acquisition_case as acquisition
import qd_platform as qd

from rebound import rebound


def source_verified(admit_run: Callable[..., Any], root: Path) -> Callable[..., Any]:
    """`admit_run` after the run's manifest binds the digests of the files under `root`, refusing another tree."""

    def admit(run: Path, validate: bool, context: dict[str, Any]) -> Any:
        manifest = json.loads((run / "cases.json").read_bytes())
        if "successor_sources" not in manifest:
            raise ValueError(f"{run}: the manifest binds no successor sources")
        qd.verify_successor_sources(manifest, root)
        return admit_run(run, validate, context)

    return admit


def admitted(
    case: Path, roots: tuple[Path, ...] | None = None, root: Path = acquisition.ROOT
) -> tuple[str, str, Callable[..., Any]]:
    """(platform, sha256 of the record, admit_run bound to it) for a case record that equals a fresh build.

    `root` is the source tree whose digests a run's `successor_sources` must equal; a test passes a copy."""
    record = case.read_bytes()
    named = json.loads(record).get("acquisition", {}).get("platform")
    platform = acquisition.platform_of(named if isinstance(named, str) else "")
    if record != (json.dumps(acquisition.case_record(platform), indent=1) + "\n").encode():
        raise ValueError(f"{case} differs from a fresh build of the successor case record for {platform}")
    bound = rebound(
        diag.admit_run,
        CASE=case,
        bdsc_cases=acquisition.cases_namespace(platform, roots),
        documents=acquisition.frozen_documents(platform, roots),
    )
    return platform, hashlib.sha256(record).hexdigest(), source_verified(bound, root)


def admit(
    runs: list[Path],
    case: Path,
    validate: bool = True,
    roots: tuple[Path, ...] | None = None,
    root: Path = acquisition.ROOT,
) -> list[str]:
    """The job of each run that passes every integrity check, for a rehearsal that holds fewer than every job."""
    _, _, admit_run = admitted(case, roots, root)
    context: dict[str, Any] = {}
    return [admit_run(run, validate, context)[0]["job"] for run in runs]


def readout(
    runs: list[Path],
    case: Path,
    validate: bool = True,
    roots: tuple[Path, ...] | None = None,
    root: Path = acquisition.ROOT,
) -> dict[str, Any]:
    """The diagnostic analysis of the collected runs of every job, admitted against the successor case record."""
    platform, digest, admit = admitted(case, roots, root)
    report: dict[str, Any] = rebound(diag.readout, admit_run=admit)(runs, validate)
    return {"platform": platform, "case_sha256": digest, **report}


def matched_check(
    b1j2: Path,
    b2j1: Path,
    case: Path,
    validate: bool = True,
    roots: tuple[Path, ...] | None = None,
    root: Path = acquisition.ROOT,
) -> list[str]:
    """The matched instances of b1-j2 and b2-j1 whose returned circuits differ, after the same admission."""
    _, _, admit = admitted(case, roots, root)
    mismatches: list[str] = rebound(diag.matched_check, admit_run=admit)(b1j2, b2j1, validate)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--case", type=Path, required=True, help="the successor case record, DIR/case.json")
    parser.add_argument("--matched-check", action="store_true", help="compare b1-j2 and b2-j1 returned circuits")
    parser.add_argument("--admit-only", action="store_true", help="print the job of each admitted run; read nothing")
    args = parser.parse_args()
    if args.matched_check:
        if len(args.runs) != 2:
            parser.error("--matched-check takes the b1-j2 run and the b2-j1 run")
        lines = matched_check(args.runs[0], args.runs[1], args.case)
        for line in lines:
            print(line, file=sys.stderr)
        return 1 if lines else 0
    if args.admit_only:
        print("\n".join(admit(args.runs, args.case)))
        return 0
    print(json.dumps(readout(args.runs, args.case), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
