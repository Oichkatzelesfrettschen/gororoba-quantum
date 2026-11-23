"""Successor of the Tuna-17 matched zero-divisor proposal with the region-2 selector on q11.

The first proposal routes region 2 with the selector on q13, whose readout
misassignment depends on the neighbors' prepared state. This producer keeps
region 1, the witnesses, shots, weights and rejection rule of
scripts/qi_matched_zero_divisor.py, which stays byte-identical because the
earlier proposals bind its digest, and changes two inputs of its build: the
initial layout of region 2, whose routing leaves the selector on q11 with the
data roles of the retained zero-divisor runs, and the retained catalogue
digest. Generation, the check against the written directory and the compiler
receipt follow the earlier producer's modes; none contacts a provider.

Certification: the build reuses qi_zero_divisor_cases.certify() (every product
of the three cases from cd_core and the four retained packages, the dark
pair's membership in the sedenion zero-divisor corpus, and SELECT equal to
cd_sign(16, m, q)|m XOR q> on all 32 inputs) and the build of the earlier
producer (the exact split-real ideals 0, 1 and 1/2, and the routed selector
probability of every case against its ideal).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_matched_zero_divisor as matched  # noqa: E402
from qi_zero_divisor_cases import certify  # noqa: E402

import qi_stack  # noqa: E402

CATALOGUE_SHA256 = "d717a785d1500e926a0f738480ba0e92326a3e7f0772d3a0717bf451a7725ace"
# Region 2 lists its initial layout: logical qubit i starts on the i-th entry. Of the 120 layouts of
# {10, 11, 13, 14, 16}, those whose routing leaves the selector on q11 and the data roles of the retained
# runs (d0 q13, d1 q16, d2 q10, d3 q14) route with 96 to 111 CZ; this is the first of the 96-CZ layouts.
REGIONS = ((1, 2, 4, 8, 12), (11, 13, 16, 14, 10))
SELECTOR_QUBITS = (4, 11)
SELECTOR_ROLES = {"d0": 13, "d1": 16, "d2": 10, "d3": 14, "selector": 11}
EARLIER = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-ordered-map-cancel"
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11"
TOOLCHAIN_RECORD = ROOT / "docs/evidence/quantum_inspire/matched-zero-divisor-toolchain-region2-selector-q11.json"
SELF = "scripts/qi_matched_zero_divisor_selector_q11.py"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@contextlib.contextmanager
def _successor_inputs() -> Iterator[None]:
    """Give the earlier producer's build and receipt functions this producer's regions and catalogue digest."""
    saved = (matched.REGIONS, matched.CATALOGUE_SHA256)
    matched.REGIONS, matched.CATALOGUE_SHA256 = REGIONS, CATALOGUE_SHA256
    try:
        yield
    finally:
        matched.REGIONS, matched.CATALOGUE_SHA256 = saved


def build() -> dict[str, str]:
    certify()
    with _successor_inputs():
        files = matched.build()
    proposal = json.loads(files["proposal.json"])
    earlier = json.loads((EARLIER / "proposal.json").read_text())
    rows = proposal["regions"]
    if rows[0] != earlier["regions"][0]:
        raise ValueError("region 1 differs from the earlier proposal")
    if [row["roles"]["selector"] for row in rows] != list(SELECTOR_QUBITS) or rows[1]["roles"] != SELECTOR_ROLES:
        raise ValueError("region 2 routes with other selector or data roles than the retained runs")
    if abs(rows[1]["cz"] - earlier["regions"][1]["cz"]) > 0.2 * earlier["regions"][1]["cz"]:
        raise ValueError("region 2 routes with more than 20 percent different CZ count")
    proposal["source_sha256"] = _digest(Path(__file__))
    proposal["gates_from"] = "scripts/qi_matched_zero_divisor.py"
    proposal["supersedes"] = EARLIER.relative_to(ROOT).as_posix()
    files["proposal.json"] = json.dumps(proposal, indent=1) + "\n"
    return files


def compiler_sources() -> dict[str, str]:
    return {**matched.compiler_sources(), SELF: _digest(Path(__file__))}


def toolchain_record(directory: Path) -> dict[str, Any]:
    with _successor_inputs():
        record = matched.toolchain_record(directory)
    record["source_sha256"] = _digest(Path(__file__))
    record["producer_sources_sha256"] = compiler_sources()
    return record


def validate_toolchain_record(directory: Path, record: dict[str, Any]) -> None:
    if record.get("source_sha256") != _digest(Path(__file__)):
        raise ValueError("successor toolchain receipt producer source differs")
    sources = record.get("producer_sources_sha256")
    if not isinstance(sources, dict) or sources != compiler_sources():
        raise ValueError("successor toolchain receipt producer dependency sources differ")
    if record.get("catalogue_sha256") != CATALOGUE_SHA256 or _digest(matched.CATALOGUE) != CATALOGUE_SHA256:
        raise ValueError("successor toolchain receipt catalogue differs")
    inherited = {name: digest for name, digest in sources.items() if name != SELF}
    matched.validate_toolchain_record(
        directory,
        {**record, "source_sha256": _digest(Path(matched.__file__)), "producer_sources_sha256": inherited},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--check-toolchain", type=Path)
    mode.add_argument("--write-toolchain", type=Path)
    mode.add_argument("--emit-toolchain", type=Path)
    parser.add_argument("--toolchain-record", type=Path, default=TOOLCHAIN_RECORD)
    arguments = parser.parse_args()
    if arguments.emit_toolchain or arguments.write_toolchain:
        directory = arguments.emit_toolchain or arguments.write_toolchain
        rendered = json.dumps(toolchain_record(directory), indent=1) + "\n"
        if arguments.emit_toolchain:
            print(rendered, end="")
        else:
            destination = arguments.toolchain_record
            if destination.exists() and destination.read_text() != rendered:
                raise ValueError("retain a separately named successor toolchain receipt")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered)
        return 0
    if arguments.check_toolchain:
        record = json.loads(arguments.toolchain_record.read_text())
        validate_toolchain_record(arguments.check_toolchain, record)
        if qi_stack.live("successor matched compiler", "checked the retained operand/control-order receipt"):
            rebuilt = json.loads(
                qi_stack.run(
                    [
                        "-B",
                        "-W",
                        "error",
                        str(Path(__file__).resolve()),
                        "--emit-toolchain",
                        str(arguments.check_toolchain.resolve()),
                    ]
                )
            )
            if rebuilt != record:
                raise ValueError("live successor compiler differs from its retained receipt")
            print("all nine live compiler rows match the retained operand/control-order receipt")
        return 0
    files = build()
    destination = arguments.write if arguments.write is not None else arguments.check
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()}
    if actual - set(files):
        raise ValueError("successor proposal directory contains unexpected files")
    for name, text in files.items():
        path = destination / name
        if arguments.check or path.exists():
            if not path.is_file() or path.read_text() != text:
                raise ValueError(f"successor proposal differs at {name}; retain a separately named successor")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print("validated nine unsubmitted successor jobs and their exact ideal endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
