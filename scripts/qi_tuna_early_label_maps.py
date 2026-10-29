"""Explore fixed early-label maps against retained Tuna joint responses."""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Any

import numpy as np
import qi_tuna_joint_response
from qi_tuna_destination_one_analysis import ROOT, SHOTS, digest, json_bytes

JOINT = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"


def compare(before: list[int], rotated: list[int], after: list[int]) -> dict[str, Any]:
    """Evaluate all early-bit permutation and polarity maps without moving terminal bits."""
    for histogram in (before, rotated, after):
        if len(histogram) != 64 or any(type(count) is not int or count < 0 for count in histogram):
            raise ValueError("histograms must contain 64 nonnegative integer counts")
        if sum(histogram) != SHOTS:
            raise ValueError("each retained histogram must contain 4096 shots")
    maps = [(permutation, flip) for permutation in itertools.permutations(range(3)) for flip in range(8)]
    coordinates = np.arange(64, dtype=np.int64)
    permutation = np.asarray([row[0] for row in maps], dtype=np.int64)
    polarity = np.asarray([row[1] for row in maps], dtype=np.int64)
    early = coordinates & 7
    mapped = np.zeros((48, 64), dtype=np.int64)
    for bit in range(3):
        mapped |= (((early[None, :] >> permutation[:, bit, None]) & 1) ^ ((polarity[:, None] >> bit) & 1)) << bit
    mapped |= coordinates[None, :] & 56
    transformed = np.zeros((48, 64), dtype=np.int64)
    np.add.at(transformed, (np.arange(48, dtype=np.int64)[:, None], mapped), np.asarray(rotated, dtype=np.int64))
    baseline = np.asarray(before, dtype=np.int64) + np.asarray(after, dtype=np.int64)
    differences = 2 * transformed - baseline[None, :]
    totals = np.abs(differences).sum(axis=1)
    terminal = int(np.abs(differences.reshape(48, 8, 8).sum(axis=2)).sum(axis=1)[0])
    if not np.all(np.abs(differences.reshape(48, 8, 8).sum(axis=2)).sum(axis=1) == terminal):
        raise ValueError("early-label maps must preserve every terminal marginal")
    if np.any(totals < terminal):
        raise ValueError("joint total variation must dominate the terminal projection")
    return {
        "maps": [
            {"output_bit_sources": list(row[0]), "polarity_mask": row[1], "tv_numerator": int(totals[index])}
            for index, row in enumerate(maps)
        ],
        "minimum_tv_numerator": int(totals.min()),
        "terminal_tv_numerator": terminal,
        "tv_denominator": 4 * SHOTS,
    }


def analyze() -> dict[str, Any]:
    """Revalidate the underlying frozen joint analysis before computing map distances."""
    joint = qi_tuna_joint_response.analyze()
    if json_bytes(joint) != JOINT.read_bytes():
        raise ValueError("joint response record differs from a full fresh replay")
    return {
        "schema": "qi-tuna-early-label-map-exploration-v1",
        "cases": {
            name: compare(*(job["joint_counts"] for job in case["jobs"])) for name, case in joint["cases"].items()
        },
        "inputs": {
            JOINT.relative_to(ROOT).as_posix(): digest(JOINT),
            "scripts/qi_tuna_joint_response.py": digest(ROOT / "scripts/qi_tuna_joint_response.py"),
        },
        "producer_sha256": digest(Path(__file__)),
        "boundary": (
            "Post-acquisition empirical distances under fixed early-label permutations and polarity flips. "
            "Terminal projection is invariant under those maps. Separate jobs and a stopped nominal-zero "
            "case do not establish a causal destination effect or identify a physical mechanism."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    result = json_bytes(analyze())
    if arguments.check:
        if arguments.check.read_bytes() != result:
            raise SystemExit("retained early-label map analysis differs from exact replay")
    else:
        with arguments.out.open("xb") as destination:
            destination.write(result)
    print("Early-label maps preserve terminal projections in both retained preparation cases.")


if __name__ == "__main__":
    main()
