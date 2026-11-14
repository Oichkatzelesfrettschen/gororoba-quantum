"""Build the Ascella target-slot request for a chosen platform under the qd_platform.job_billing rule.

ascella_predecessor_case_v2.documents() rebuilds the frozen request with billing_rule_v2.RULE as its credit basis and
the admission billing_rule_v2.ADMISSION, which qd_platform.submit refuses because no analyzer admits that record.
This builder pairs the request with scripts/ascella_predecessor_acquisition_analysis.py: it replaces the admission
with billing_rule_v2.READY, names the job after the platform, admits one platform, and binds its own sources and
the analyzer's in `preregistered.current_case_sources`, which qd_platform.acquisition_sources verifies before a
review packet or a submission. The analyzer admits a run only when its cases.json equals `documents(platform)` byte
for byte, so the request's sha256 is the admission key.

The frozen request keeps its settings, circuit, budgets and decision rule. qpu:ascella is the qualifying platform;
sim:ascella carries the same request as a rehearsal of the record, the receipt and the analyzer, and its returned
compilation need not reproduce the QPU's (docs/design/quandela-successor-acquisition-rehearsal.md).

Usage:
  "$PYTHON" scripts/ascella_predecessor_acquisition_case.py --build --platform sim:ascella --out DIR
  "$PYTHON" scripts/ascella_predecessor_acquisition_case.py --check DIR
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import ascella_predecessor_case as original
import ascella_predecessor_case_v2 as rule_v2
import qd_platform as qd
from billing_rule_v2 import admit_ready

PLATFORMS = ("qpu:ascella", "sim:ascella")
BUILDER = "scripts/ascella_predecessor_acquisition_case.py"


def job_name(platform: str) -> str:
    """The case job of one platform, qpu-ascella-billing-rule for qpu:ascella."""
    if platform not in PLATFORMS:
        raise ValueError(f"{platform!r} is not an admitted platform of this request: {PLATFORMS}")
    return f"{platform.replace(':', '-')}-billing-rule"


def sources(platform: str) -> tuple[str, ...]:
    """The builder, analyzer and shared modules that preregistered.current_case_sources binds for `platform`."""
    return qd.CURRENT_CASE_SOURCES[job_name(platform)]


def documents(platform: str) -> dict[str, bytes]:
    payload = rule_v2.documents()
    manifest = json.loads(payload["cases.json"])
    admit_ready(manifest)
    manifest["job"] = job_name(platform)
    manifest["platforms"] = [platform]
    manifest["preregistered"]["current_case_sources"] = {
        name: original.sha256_bytes((original.ROOT / name).read_bytes()) for name in sources(platform)
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": payload["circuit.json"]}


def check(directory: Path) -> dict:
    """The request under `directory`, equal byte for byte to a fresh build for the platform it names."""
    retained = directory / "cases.json"
    original.require(retained.is_file(), f"{retained} is missing; build the case first")
    named = json.loads(retained.read_bytes()).get("platforms")
    if not isinstance(named, list) or len(named) != 1 or not isinstance(named[0], str):
        raise ValueError(f"{retained} does not name exactly one platform")
    rebuilt = documents(named[0])
    for name, data in rebuilt.items():
        if (directory / name).read_bytes() != data:
            raise ValueError(f"{directory / name} differs from the source-derived request for {named[0]}")
    return json.loads(rebuilt["cases.json"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build", action="store_true")
    group.add_argument("--check", type=Path, metavar="DIR")
    parser.add_argument("--platform", choices=PLATFORMS, help="platform the built request admits")
    parser.add_argument("--out", type=Path, help="new request directory for --build, a run directory")
    args = parser.parse_args()
    if args.build:
        if args.platform is None or args.out is None:
            parser.error("--build requires --platform and --out")
        directory = args.out
        original.publish_case(directory, documents(args.platform))
    else:
        directory = args.check
    print(original.summary(check(directory)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
