"""Replay exact package-table encodings of Tuna joint disagreement data."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import algebra_package_tables
import qi_tuna_joint_response
from qi_tuna_destination_one_analysis import ROOT, SHOTS, digest, json_bytes, ordered_map

JOINT = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
PACKAGE_TABLES = ROOT / "docs/evidence/algebra_packages/tables.json"
ORDINARY_PACKAGES = ("hypercomplex", "hypercomplex-engine", "hyprat")


def associator_values(signs: list[list[int]], counts: list[int]) -> tuple[str, str]:
    """Evaluate an associator sign average and the exact coefficient-associator norm."""
    if len(counts) != 8 or any(type(count) is not int or count < 0 for count in counts) or sum(counts) != SHOTS:
        raise ValueError("disagreement counts must be eight nonnegative integers summing to 4096")
    norm_numerator = 0
    sign_numerator = 0
    for index, count in enumerate(counts):
        left = signs[1][6] * signs[1 ^ 6][index]
        right = signs[6][index] * signs[1][6 ^ index]
        sign_numerator += count * left * right
        norm_numerator += (count * (left - right)) ** 2
    return str(Fraction(sign_numerator, SHOTS)), str(Fraction(norm_numerator, SHOTS * SHOTS))


def job_algebra(task: tuple[dict[str, Any], list[list[list[int]]]]) -> dict[str, Any]:
    """Check four retained multiplication tables against the same outcome vector."""
    job, tables = task
    values = [associator_values(signs, job["disagreement_counts"]) for signs in tables]
    if any(value != values[0] for value in values[1:]):
        raise ValueError("ordinary and split associator summaries disagree")
    if Fraction(values[0][0]) != Fraction(job["parity_numerators"][54], SHOTS):
        raise ValueError("octonion sign average differs from the measured disagreement parity")
    return {
        "batch": job["batch"],
        "job": job["job"],
        "raw_sha256": job["raw_sha256"],
        "associator_sign_mean": values[0][0],
        "associator_norm_squared": values[0][1],
    }


def analyze() -> dict[str, Any]:
    """Revalidate upstream joint evidence and mapped package tables before calculation."""
    joint = qi_tuna_joint_response.analyze()
    if json_bytes(joint) != JOINT.read_bytes():
        raise ValueError("joint-response evidence differs from its complete fresh replay")
    package_data = json.loads(PACKAGE_TABLES.read_bytes())
    checked = algebra_package_tables.check(package_data)
    packages = package_data["packages"]
    ordinary = [packages[name]["tables"]["8"]["signs"] for name in ORDINARY_PACKAGES]
    split = packages["splitoct"]["tables"]["8"]["signs"]
    split_control = {
        "associator_triples_checked": 512,
        "ordinary_e4_square": ordinary[0][4][4],
        "split_e4_square": split[4][4],
    }
    if split_control["ordinary_e4_square"] != -1 or split_control["split_e4_square"] != 1:
        raise ValueError("split negative control must differ on the e4 square")
    tables = [*ordinary, split]
    cases = {
        name: ordered_map(job_algebra, [(job, tables) for job in case["jobs"]]) for name, case in joint["cases"].items()
    }
    return {
        "schema": "qi-tuna-joint-algebra-table-replay-v1",
        "cases": cases,
        "split_control": split_control,
        "package_table_checks": checked,
        "recorded_release_pins": {
            name: {
                "version": packages[name]["version"],
                "release_sha256": packages[name]["release_sha256"],
                "installed_at_original_extraction": packages[name]["installed"],
            }
            for name in (*ORDINARY_PACKAGES, "splitoct")
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in (
                JOINT,
                PACKAGE_TABLES,
                ROOT / "scripts/algebra_package_tables.py",
                ROOT / "scripts/qi_tuna_joint_response.py",
                ROOT / "gororoba_quantum/cd_core.py",
            )
        },
        "producer_sha256": digest(Path(__file__)),
        "boundary": (
            "Exact algebraic summaries of a chosen classical encoding of binary labels. The retained package "
            "tables represent their original source-bound extraction; replay does not inspect current installed "
            "packages. Agreement does not identify a physical non-associative process or causal readout effect."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    content = json_bytes(analyze())
    if arguments.check:
        if arguments.check.read_bytes() != content:
            raise SystemExit("retained joint-algebra analysis differs from exact replay")
    else:
        with arguments.out.open("xb") as destination:
            destination.write(content)
    print("Retained package tables replay exact joint-data associator summaries and the split control.")


if __name__ == "__main__":
    main()
