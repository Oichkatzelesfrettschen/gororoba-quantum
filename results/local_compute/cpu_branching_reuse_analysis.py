"""Bound noisy distribution differences while preserving the retained failure."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    sys.path.insert(0, str(arguments.repo / "gororoba_quantum"))
    from diagnostic_experiments import family_contracts

    filenames = ("cpu_branching_qualification.json", "cpu_branching_reuse_probe.json")
    inputs = {name: (arguments.out / name).read_bytes() for name in filenames}
    retained, replay = (json.loads(inputs[name]) for name in filenames)
    if replay["state"] != "completed":
        raise RuntimeError("The reuse probe must finish before analysis")
    if replay["qualification_input_sha256"] != hashlib.sha256(inputs[filenames[0]]).hexdigest():
        raise RuntimeError("Qualification bytes differ from the reuse probe's input")
    if retained["qpy_sha256"] != replay["qpy_sha256"]:
        raise RuntimeError("Compiled circuit archives differ")
    archive_digest = hashlib.sha256((arguments.out / "cpu_branching_inputs.qpy").read_bytes()).hexdigest()
    if archive_digest != retained["qpy_sha256"]:
        raise RuntimeError("Compiled circuit archive changed")

    pairs: list[tuple[str, str, dict[str, Any], dict[str, Any]]] = []
    for family, baseline_shots in (("folded-qpe", 2048), ("n21-feedback", 256)):
        baseline = next(
            case
            for case in retained["cases"]
            if case["family"] == family and case["shots"] == baseline_shots and not case["shot_branching_enable"]
        )
        fresh = [case for case in replay["cases"] if case["family"] == family and case["mode"].startswith("fresh_")]
        if len(fresh) != 3:
            raise RuntimeError("Expected three completed fresh trials per family")
        for trial in fresh:
            pairs.append(("retained_baseline_vs_fresh", family, baseline, trial))
        for left, right in itertools.combinations(fresh, 2):
            pairs.append(("fresh_vs_fresh", family, left, right))
        if family == "folded-qpe":
            original = next(
                case
                for case in retained["cases"]
                if case["family"] == family and case["shots"] == 2048 and case["shot_branching_enable"]
            )
            reused = next(
                case
                for case in replay["cases"]
                if case["family"] == family and case["shots"] == 2048 and case["shot_branching_enable"]
            )
            pairs.append(("retained_baseline_vs_reused", family, baseline, reused))
            for trial in fresh:
                pairs.append(("retained_failed_vs_fresh", family, original, trial))

    alpha = 1e-6
    bin_count = sum(len(values) for _kind, _family, left, _right in pairs for values in left["distributions"].values())
    term_count = sum(
        2 * sum(len(contract.terms) for contract in family_contracts(family, 0.08, 0.05, 0.8))
        for _kind, family, _left, _right in pairs
    )
    comparisons = []
    contrast_comparisons = []
    for kind, family, left, right in pairs:
        if left["distributions"].keys() != right["distributions"].keys():
            raise RuntimeError("Paired circuit labels differ")
        radius = sum(math.sqrt(math.log(8 * bin_count / alpha) / (2 * row["shots"])) for row in (left, right))
        differences = {
            name: [abs(first - second) for first, second in zip(values, right["distributions"][name], strict=True)]
            for name, values in left["distributions"].items()
        }
        maximum = max(value for values in differences.values() for value in values)
        identity = {
            "kind": kind,
            "family": family,
            "left_shots": left["shots"],
            "right_shots": right["shots"],
            "left_seed": left["seed"],
            "right_seed": right["seed"],
        }
        comparisons.append(
            {
                **identity,
                "bin_differences": differences,
                "max_absolute_bin_difference": maximum,
                "simultaneous_radius": radius,
                "compatible": maximum <= radius,
            }
        )
        for contract in family_contracts(family, 0.08, 0.05, 0.8):
            estimates = [
                sum(
                    term.sign
                    * sum(
                        value * probability
                        for value, probability in zip(term.values, row["distributions"][term.member], strict=True)
                    )
                    for term in contract.terms
                )
                for row in (left, right)
            ]
            contrast_radius = sum(
                math.sqrt(math.log(4 * term_count / alpha) / (2 * row["shots"])) for row in (left, right)
            ) * sum(max(term.values) - min(term.values) for term in contract.terms)
            difference = abs(estimates[0] - estimates[1])
            contrast_comparisons.append(
                {
                    **identity,
                    "contrast": contract.name,
                    "estimates": estimates,
                    "absolute_difference": difference,
                    "simultaneous_radius": contrast_radius,
                    "compatible": difference <= contrast_radius,
                }
            )

    all_counts_complete = all(
        count == case["shots"] for case in replay["cases"] for count in case["counts_total"].values()
    )
    all_qpy_unchanged = all(case["qpy_before"] == case["qpy_after"] for case in replay["cases"])
    all_modes_match = all(
        metadata["device"] == "CPU"
        and metadata["method"] == "density_matrix"
        and (
            not case["shot_branching_enable"]
            or metadata.get("shot_branching_enabled") is True
            or metadata.get("measure_sampling") is True
        )
        for case in replay["cases"]
        for metadata in case["metadata"]
    )
    report = {
        "state": "failed_fresh_instance_repair_falsified",
        "production_shot_branching_qualified": False,
        "source_input_sha256": {name: hashlib.sha256(value).hexdigest() for name, value in inputs.items()},
        "qpy_sha256": archive_digest,
        "familywise_alpha": alpha,
        "total_bin_comparisons": bin_count,
        "total_contrast_term_estimates": term_count,
        "bound_scope": (
            "Hoeffding union bounds allocate alpha/2 to all listed bin comparisons and alpha/2 to all listed "
            "contrast comparisons. Each estimate assumes stationary independent shots; comparisons and runs "
            "need not be independent. Compatibility does not establish numerical equivalence."
        ),
        "residuals": [
            "A fresh32768 trial fails on qpe_no_feed_forward_s3; fresh-instance construction fails as a repair.",
            "The retained noisy folded2048 failure on qpe_archived_s1 remains unexplained.",
            "The reuse probe starts from QPY-loaded circuits; the original used in-memory compiled circuit objects.",
            "N21 branch-off baseline has 256 shots; a full32768 paired baseline was not measured.",
            "Repeated branch-enabled draws test stability and do not independently validate noisy probabilities.",
            "Nearby seeds may share pseudorandom streams; independence between repeat runs is unclaimed.",
            "Serialized channel identity excludes delay-noise passes; fixture reconstruction supplies those passes.",
        ],
        "all_count_totals_complete": all_counts_complete,
        "all_qpy_before_after_identical": all_qpy_unchanged,
        "all_execution_modes_match": all_modes_match,
        "execution_mode_boundary": (
            "Every result reports CPU density_matrix. Enabled batches report shot_branching_enabled=true "
            "for dynamic members and measure_sampling=true for eligible static members."
        ),
        "comparisons": comparisons,
        "contrast_comparisons": contrast_comparisons,
    }
    (arguments.out / "cpu_branching_reuse_analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {key: value for key, value in report.items() if key not in ("comparisons", "contrast_comparisons")},
            indent=2,
        )
    )
    for kind in dict.fromkeys(row["kind"] for row in comparisons):
        selected = [row for row in comparisons if row["kind"] == kind]
        print(kind, sum(row["compatible"] for row in selected), "/", len(selected))


if __name__ == "__main__":
    main()
