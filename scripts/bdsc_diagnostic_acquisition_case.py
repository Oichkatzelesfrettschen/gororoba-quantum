"""Build the Belenos diagnostic request for a chosen platform under the qd_platform.job_billing rule.

scripts/bdsc_diagnostic.py keeps its bytes: its `--check` compares the retained case tree with a fresh build, and its
readout admits only docs/evidence/bdsc/diagnostic/case.json. This builder reuses `draw_claims` and `documents` of that
module through gororoba_quantum/rebound.py, bound to a successor case record, so the rule that orders the 96 instances,
solves the parameters and claims a QRNG draw stays in one place:

- the successor case record states billing_rule_v2.RULE in `/resources/billing_rule` and names its platform in
  `/acquisition`; its sha256 is the `diagnostic_case_sha256` of every job manifest and the admission key of
  scripts/bdsc_diagnostic_acquisition_analysis.py;
- `draw_claims` compares a draw's retained manifests with the successor record's sha256, so a rebuild of the
  successor's own jobs never claims its draw and a manifest of any other case, the original diagnostic included, does;
- every manifest admits the one platform and carries `acquisition_admission` billing_rule_v2.READY.

The tree goes outside results/quandela/cases/bdsc_diagnostic, because the original `--check` requires exactly the
original job directories there. qpu:belenos qualifies the diagnostic; sim:belenos carries the same request as a
rehearsal of the record, the receipt and the analyzer (docs/design/quandela-successor-acquisition-rehearsal.md). The
24-mode circuit does not fit sim:ascella, so a build for any platform outside PLATFORMS is refused.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_acquisition_case.py --build --platform sim:belenos --out DIR [--draw FILE]
  "$PYTHON" scripts/bdsc_diagnostic_acquisition_case.py --check DIR [--draw FILE]
"""

from __future__ import annotations

import argparse
import json
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_case_records_v2 as records_v2  # noqa: E402
import bdsc_cases  # noqa: E402
import bdsc_certificate as cert  # noqa: E402
import bdsc_diagnostic as diag  # noqa: E402
from billing_rule_v2 import RULE, admit_ready, supersede  # noqa: E402

from rebound import rebound  # noqa: E402

PLATFORMS = ("qpu:belenos", "sim:belenos")
BUILDER = "scripts/bdsc_diagnostic_acquisition_case.py"
ANALYZER = "scripts/bdsc_diagnostic_acquisition_analysis.py"
ORIGINAL_TREE = diag.CASES_DIR

Documents = dict[str, bytes | dict[str, bytes]]


def platform_of(platform: str) -> str:
    if platform not in PLATFORMS:
        raise ValueError(f"{platform!r} is not an admitted platform of this request: {PLATFORMS}")
    return platform


def case_record(platform: str) -> dict[str, Any]:
    """The original case record with the current billing rule and the platform the successor request admits."""
    record = diag.case_record()
    supersede(record, ("resources", "billing_rule"), records_v2.OLD_RULE, RULE)
    record["acquisition"] = {"platform": platform_of(platform), "builder": BUILDER, "analyzer": ANALYZER}
    return record


def cases_namespace(platform: str, roots: tuple[Path, ...] | None = None) -> types.SimpleNamespace:
    """bdsc_cases with the request's platform as the only admitted and qualifying platform.

    `roots` replaces the retained-manifest roots that `draw_claims` scans; a test passes a scratch tree there."""
    return types.SimpleNamespace(
        **{
            **vars(bdsc_cases),
            "PLATFORMS": [platform_of(platform)],
            "QUALIFYING_PLATFORM": platform,
            "MANIFEST_ROOTS": bdsc_cases.MANIFEST_ROOTS if roots is None else roots,
        }
    )


def documents(platform: str, draw: Path | None = None, roots: tuple[Path, ...] | None = None) -> Documents:
    """{"case.json": bytes, job: {"cases.json": bytes, "circuit.json": bytes}} of the successor request."""
    namespace = cases_namespace(platform, roots)

    def record() -> dict[str, Any]:
        return case_record(platform)

    claims = rebound(diag.draw_claims, case_record=record, bdsc_cases=namespace)
    build = rebound(diag.documents, case_record=record, draw_claims=claims, bdsc_cases=namespace)
    out: Documents = build(draw)
    for files in out.values():
        if isinstance(files, dict):
            manifest = json.loads(files["cases.json"])
            admit_ready(manifest)
            files["cases.json"] = (json.dumps(manifest, indent=1) + "\n").encode()
    return out


def frozen_documents(platform: str, roots: tuple[Path, ...] | None = None) -> Callable[[Path | None], Documents]:
    """`documents` of one platform as the one-argument rebuild that bdsc_diagnostic.admit_run calls."""

    def rebuild(draw: Path | None) -> Documents:
        return documents(platform, draw, roots)

    return rebuild


def write(directory: Path, platform: str, draw: Path | None) -> None:
    """Write case.json and the job directories, refusing a retained file whose bytes differ."""
    if directory.resolve().is_relative_to(ORIGINAL_TREE.resolve()):
        raise ValueError(f"{directory} lies under the original diagnostic tree, whose --check admits its own jobs only")
    tree = documents(platform, draw)
    for name, content in tree.items():
        files = (
            {name: content}
            if isinstance(content, bytes)
            else {f"{name}/{file}": data for file, data in content.items()}
        )
        for relative, data in files.items():
            target = directory / relative
            if target.exists() and target.read_bytes() != data:
                raise ValueError(f"retained file differs: {target}; choose a new directory")
    for name, content in tree.items():
        if isinstance(content, bytes):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / name).write_bytes(content)
            continue
        (directory / name).mkdir(parents=True, exist_ok=True)
        for file, data in content.items():
            (directory / name / file).write_bytes(data)
    print(f"bdsc diagnostic ({platform}): wrote case.json and the job directories under {directory}")


def platform_of_record(directory: Path) -> str:
    named = json.loads((directory / "case.json").read_bytes()).get("acquisition", {}).get("platform")
    return platform_of(named if isinstance(named, str) else "")


def check(directory: Path, draw: Path | None, roots: tuple[Path, ...] | None = None) -> None:
    """The record and circuits equal a fresh build exactly, and the manifests within cert.CHECK_TOLERANCE on floats."""
    platform = platform_of_record(directory)
    if draw is None:
        named = json.loads((directory / "b1-j1" / "cases.json").read_bytes()).get("draw")
        draw = ROOT / named["record"] if isinstance(named, dict) else None
    fresh = documents(platform, draw, roots)
    diag.require((directory / "case.json").read_bytes() == fresh["case.json"], "case.json differs from a fresh build")
    jobs = sorted(name for name in fresh if name != "case.json")
    present = sorted(p.name for p in directory.iterdir() if p.is_dir())
    diag.require(present == jobs, f"job directories differ: {sorted(set(present) ^ set(jobs))}")
    for job in jobs:
        files = fresh[job]
        diag.require(isinstance(files, dict), f"{job}: not a job")
        if isinstance(files, dict):
            diag.require(
                (directory / job / "circuit.json").read_bytes() == files["circuit.json"], f"{job}/circuit.json"
            )
            cert.close(json.loads(files["cases.json"]), json.loads((directory / job / "cases.json").read_bytes()), job)
    print(f"bdsc diagnostic ({platform}): the case record and {len(jobs)} job directories match a fresh build")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", type=Path, metavar="DIR")
    parser.add_argument("--platform", choices=PLATFORMS, help="platform the built request admits")
    parser.add_argument(
        "--out", type=Path, help="tree directory for --build, outside results/quandela/cases/bdsc_diagnostic"
    )
    parser.add_argument("--draw", type=Path, help="ANU QRNG draw record that seeds the build")
    args = parser.parse_args()
    if args.build:
        if args.platform is None or args.out is None:
            parser.error("--build requires --platform and --out")
        write(args.out, args.platform, args.draw)
        check(args.out, args.draw)
    else:
        check(args.check, args.draw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
