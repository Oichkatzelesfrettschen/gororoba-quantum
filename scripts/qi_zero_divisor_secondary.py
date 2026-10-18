"""Secondary covariance-aware replay of the retained Tuna-17 Design B witness.

This audit complements the retained common-response bootstrap without
rewriting it. It uses complete same-shot selector vectors, preserves the
fixed Latin square strata, and propagates shared readout calibration with
a delta method. It checks the pooled secondary H = fixture - (dark + bright)/2
and adds corrected regional estimates with their selector/depth confounds.
It does not acquire data, simulate a circuit, or identify a noise mechanism.

Usage: "$PYTHON" scripts/qi_zero_divisor_secondary.py --write results/quantum_inspire/secondary
       "$PYTHON" scripts/qi_zero_divisor_secondary.py --check results/quantum_inspire/secondary --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

RUN = Path("results/quantum_inspire/runs/2026-10-16T221133Z-zero_divisor_tuna_17")
NAMES = ("dark", "bright", "fixture")
STEM = "zero_divisor_tuna_17"
Z95 = 1.959963984540054


def moments(observations: list[list[int]]) -> dict[str, Any]:
    """Unbiased sample covariance of a mean, retaining same-shot dependence."""
    n = len(observations)
    if n < 2:
        raise ValueError("a covariance block needs at least two shots")
    width = len(observations[0])
    counts = [0] * width
    joint = [[0] * width for _ in range(width)]
    for row in observations:
        if len(row) != width or any(value not in (0, 1) for value in row):
            raise ValueError("each observation must be a fixed-width binary vector")
        for i, value in enumerate(row):
            counts[i] += value
            for j, other in enumerate(row):
                joint[i][j] += value * other
    means = [k / n for k in counts]
    covariance = [[(joint[i][j] / n - means[i] * means[j]) / (n - 1) for j in range(width)] for i in range(width)]
    return {"shots": n, "counts": counts, "means": means, "covariance_of_mean": covariance}


def read_block(task: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / task["path"]
    payload = path.read_bytes()
    shots = json.loads(payload)
    if len(shots) != task["shots"]:
        raise ValueError(f"{task['path']}: shot count differs from cases.json")
    if any(not isinstance(s, str) or len(s) != task["nqubits"] or set(s) - {"0", "1"} for s in shots):
        raise ValueError(f"{task['path']}: malformed shot string")
    # Qubit zero is the rightmost character on Tuna; retain each complete shot.
    observations = [
        [int(int(shot[-1 - q]) == value) for q, value in zip(task["selectors"], task["values"], strict=True)]
        for shot in shots
    ]
    return {**task, **moments(observations), "sha256": hashlib.sha256(payload).hexdigest()}


def quadratic(left: list[float], covariance: list[list[float]], right: list[float]) -> float:
    return sum(a * sum(c * b for c, b in zip(row, right, strict=True)) for a, row in zip(left, covariance, strict=True))


def corrected(p: float, alpha: float, beta: float) -> tuple[float, tuple[float, float, float]]:
    """Invert p_observed = beta + (1-alpha-beta) p_true and differentiate."""
    denominator = 1 - alpha - beta
    if denominator <= 0:
        raise ValueError("the retained readout assignment is singular or reversed")
    value = (p - beta) / denominator
    return value, (1 / denominator, value / denominator, (value - 1) / denominator)


def estimate(
    value: float, gradient: list[float], covariance: list[list[float]], calibration_start: int
) -> dict[str, Any]:
    witness_gradient = gradient[:calibration_start] + [0.0] * (len(gradient) - calibration_start)
    calibration_gradient = [0.0] * calibration_start + gradient[calibration_start:]
    witness_variance = quadratic(witness_gradient, covariance, witness_gradient)
    calibration_variance = quadratic(calibration_gradient, covariance, calibration_gradient)
    variance = witness_variance + calibration_variance
    if variance < -1e-14:
        raise ValueError("negative propagated variance")
    se = math.sqrt(max(variance, 0.0))
    return {
        "estimate": value,
        "standard_error": se,
        "ci95_normal": [value - Z95 * se, value + Z95 * se],
        "z_against_zero": value / se if se else (0.0 if value == 0 else None),
        "variance_witness_shots": witness_variance,
        "variance_readout_calibration": calibration_variance,
    }


def summarize(
    values: list[float], gradients: list[list[float]], covariance: list[list[float]], nreplicas: int
) -> dict[str, Any]:
    summaries = {
        name: estimate(value, gradient, covariance, nreplicas)
        for name, value, gradient in zip(NAMES, values, gradients, strict=True)
    }
    specifications = (
        ("endpoint_contrast", (-1.0, 1.0, 0.0), 0.0),
        ("endpoint_sum_residual", (1.0, 1.0, 0.0), -1.0),
        ("fixture_minus_half", (0.0, 0.0, 1.0), -0.5),
        ("fixture_midpoint_residual", (-0.5, -0.5, 1.0), 0.0),
    )
    metrics = {}
    for name, weights, offset in specifications:
        gradient = [sum(w * g[i] for w, g in zip(weights, gradients, strict=True)) for i in range(len(covariance))]
        value = offset + sum(w * p for w, p in zip(weights, values, strict=True))
        metrics[name] = estimate(value, gradient, covariance, nreplicas)
    return {
        "by_case": summaries,
        "covariance_order": list(NAMES),
        "covariance_of_case_means": [[quadratic(a, covariance, b) for b in gradients] for a in gradients],
        "metrics": metrics,
    }


def compare_upstream(
    pooled: dict[str, Any], regions: list[dict[str, Any]], secondary: dict[str, Any], shots: int
) -> dict[str, Any]:
    """Check the independent raw replay and compare two uncertainty methods."""
    variance_factor = shots / (shots - 1)
    for i, first in enumerate(NAMES):
        for j, second in enumerate(NAMES):
            reference = secondary["raw_covariance"][f"{first},{second}"] * variance_factor
            actual = pooled["raw"]["covariance_of_case_means"][i][j]
            if not math.isclose(actual, reference, rel_tol=1e-10, abs_tol=1e-18):
                raise ValueError("independent raw covariance differs from the upstream secondary analysis")
    names = {
        "endpoint_contrast": "contrast_B_minus_D",
        "endpoint_sum_residual": "sum_residual_D_plus_B_minus_1",
        "fixture_midpoint_residual": "fixture_minus_endpoint_midpoint_H",
        "fixture_minus_half": "fixture_minus_half",
    }
    comparison = {}
    for name, upstream_name in names.items():
        row = pooled["raw"]["metrics"][name]
        reference = secondary["raw"][upstream_name]
        if not math.isclose(row["estimate"], reference["value"], abs_tol=1e-14):
            raise ValueError(f"raw {name} differs from the upstream secondary analysis")
        if not math.isclose(row["standard_error"], reference["se"] * math.sqrt(variance_factor), rel_tol=1e-10):
            raise ValueError(f"raw {name} uncertainty differs after the covariance denominator adjustment")
        corrected_row = pooled["readout_corrected"]["metrics"][name]
        bootstrap = secondary["readout_corrected_bootstrap"][upstream_name]
        comparison[name] = {
            "analytic_point_estimate": corrected_row["estimate"],
            "analytic_delta_standard_error": corrected_row["standard_error"],
            "analytic_delta_ci95": corrected_row["ci95_normal"],
            "upstream_bootstrap": bootstrap,
            "relative_standard_error_difference": corrected_row["standard_error"] / bootstrap["se"] - 1,
        }
    for region in regions:
        reference = secondary["by_region_raw"][str(region["region"])]
        metrics = region["raw"]["metrics"]
        for name, upstream_name in (("endpoint_contrast", "contrast"), ("fixture_midpoint_residual", "H")):
            if not math.isclose(metrics[name]["estimate"], reference[upstream_name], abs_tol=1e-14):
                raise ValueError("regional raw estimates differ from the upstream secondary analysis")
    return {
        "registry_claim": "qi-tuna17-zero-divisor-common-response",
        "source": str(RUN / "analysis.json"),
        "bootstrap": secondary["bootstrap"],
        "raw_point_estimates_and_covariance_reproduced": True,
        "raw_variance_unbiased_to_upstream_ratio": variance_factor,
        "raw_denominator_note": (
            "upstream uses the empirical multinomial covariance divided by n; "
            "this audit uses the unbiased covariance of the mean divided by n-1"
        ),
        "corrected_uncertainty_comparison": comparison,
        "scope": (
            "independent analytic covariance audit and corrected regional extension of the existing "
            "secondary claim; the bootstrap is retained, not rerun or promoted to preregistration"
        ),
    }


def analyze() -> dict[str, Any]:
    cases = json.loads((ROOT / RUN / "cases.json").read_text())
    original = json.loads((ROOT / RUN / "analysis.json").read_text())
    replicas = cases["replicas"]
    nr = len(replicas)
    selectors = sorted({row["roles"]["selector"] for row in replicas})
    ns = len(selectors)
    width = nr + 2 * ns
    tasks = []
    for circuit in cases["circuits"]:
        name = circuit["file"]
        indices = [i for i, row in enumerate(replicas) if row["file"] == name]
        if circuit["kind"] == "witness":
            selected = [replicas[i]["roles"]["selector"] for i in indices]
            values = [0] * len(indices)
        else:
            selected = selectors
            if name == "readout-0.cq":
                indices, values = list(range(nr, nr + ns)), [1] * ns
            elif name == "readout-1.cq":
                indices, values = list(range(nr + ns, width)), [0] * ns
            else:
                raise ValueError(f"unknown readout circuit {name}")
        tasks.append(
            {
                "file": name,
                "path": str(RUN / "raw" / f"{name}.json"),
                "indices": indices,
                "selectors": selected,
                "values": values,
                "shots": cases["shots"],
                "nqubits": cases["nqubits"],
            }
        )
    # Independent acquisition parsing and moment calculation use the repository pool.
    blocks = ordered_map(read_block, tasks, min_items=1)
    means = [0.0] * width
    covariance = [[0.0] * width for _ in range(width)]
    hashes = {}
    for block in blocks:
        hashes[block["path"]] = block["sha256"]
        for i, target in enumerate(block["indices"]):
            means[target] = block["means"][i]
            for j, other in enumerate(block["indices"]):
                covariance[target][other] = block["covariance_of_mean"][i][j]
    raw_gradients, corrected_gradients, corrected_values = [], [], []
    replica_records = []
    for i, row in enumerate(replicas):
        selector_index = selectors.index(row["roles"]["selector"])
        ai, bi = nr + selector_index, nr + ns + selector_index
        value, derivatives = corrected(means[i], means[ai], means[bi])
        raw_gradient, correction_gradient = [0.0] * width, [0.0] * width
        raw_gradient[i] = 1.0
        for index, derivative in zip((i, ai, bi), derivatives, strict=True):
            correction_gradient[index] = derivative
        raw_gradients.append(raw_gradient)
        corrected_gradients.append(correction_gradient)
        corrected_values.append(value)
        replica_records.append(
            {
                **row,
                "shots": cases["shots"],
                "selector_zero_count": round(means[i] * cases["shots"]),
                "raw": estimate(means[i], raw_gradient, covariance, nr),
                "readout_corrected": estimate(value, correction_gradient, covariance, nr),
            }
        )

    def aggregate(indices_by_case: list[list[int]], readout_corrected: bool) -> dict[str, Any]:
        source_values = corrected_values if readout_corrected else means[:nr]
        source_gradients = corrected_gradients if readout_corrected else raw_gradients
        values = [sum(source_values[i] for i in group) / len(group) for group in indices_by_case]
        gradients = [
            [sum(source_gradients[i][j] for i in group) / len(group) for j in range(width)] for group in indices_by_case
        ]
        return summarize(values, gradients, covariance, nr)

    groups = [[i for i, row in enumerate(replicas) if row["case"] == name] for name in NAMES]
    if any(len(group) != 3 for group in groups):
        raise ValueError("this replay requires the retained three-replica Latin square")
    pooled = {"raw": aggregate(groups, False), "readout_corrected": aggregate(groups, True)}
    counts = {
        name: {
            "successes": sum(replica_records[i]["selector_zero_count"] for i in group),
            "attempts": len(group) * cases["shots"],
        }
        for name, group in zip(NAMES, groups, strict=True)
    }
    for name in NAMES:
        if pooled["raw"]["by_case"][name]["estimate"] != original["by_case"][name]["p_selector_zero"]:
            raise ValueError(f"raw {name} disagrees with the original analysis")
        if not math.isclose(
            pooled["readout_corrected"]["by_case"][name]["estimate"],
            original["by_case"][name]["readout_corrected"],
            abs_tol=1e-14,
        ):
            raise ValueError(f"corrected {name} disagrees with the original analysis")
    regions = []
    for region in cases["regions"]:
        groups = [
            [i for i, row in enumerate(replicas) if row["region"] == region and row["case"] == name] for name in NAMES
        ]
        if any(len(group) != 1 for group in groups):
            raise ValueError("each region must contain one acquisition per case")
        indices = [group[0] for group in groups]
        regions.append(
            {
                "region": region,
                "case_order": list(NAMES),
                "selectors": [replicas[i]["roles"]["selector"] for i in indices],
                "cz_counts": [replicas[i]["cz"] for i in indices],
                "raw": aggregate(groups, False),
                "readout_corrected": aggregate(groups, True),
            }
        )
    calibration = []
    for j, selector in enumerate(selectors):
        calibration.append(
            {
                "selector": selector,
                "alpha_read_1_given_prepared_0": means[nr + j],
                "beta_read_0_given_prepared_1": means[nr + ns + j],
                "shots_per_preparation": cases["shots"],
            }
        )
    # Bind the retained inputs without rewriting any preregistered artifact.
    for name in ("cases.json", "analysis.json", "submission.json", "results.json"):
        path = RUN / name
        hashes[str(path)] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    return {
        "schema": "qi-zero-divisor-secondary-v1",
        "claim_kind": "secondary hardware reanalysis",
        "run": str(RUN),
        "input_sha256": hashes,
        "method": {
            "bit_order": "qubit zero is the rightmost character",
        "normalization": (
            "Design B fixed-operand LCU: P(s=0) = ||x y||^2 / 2 for normalized x = (e_i + t e_j)/sqrt2 "
            "and normalized y, so the ideal reads 0 dark, 1 bright and 1/2 fixture"
        ),
            "raw_covariance": "unbiased covariance of each acquisition's mean: (E[Xi Xj]-E[Xi]E[Xj])/(n-1)",
            "pooling": "equal-weight average of three fixed regions, each with the same shot count",
            "readout_correction": "(p-beta)/(1-alpha-beta), alpha=P(read 1|prepared 0), beta=P(read 0|prepared 1)",
            "readout_uncertainty": (
                "first-order delta method; shared selectors and same-shot calibration covariance retained"
            ),
            "intervals": "pointwise normal 95% intervals; secondary tests have no multiplicity adjustment",
            "assumptions": [
                "shots are independent within each acquisition; different jobs are independent",
                ("readout assignment is stationary and the all-zero/all-one preparations represent witness readout"),
                "calibration includes preparation error; these data do not isolate assignment error alone",
                "between-job drift and calibration-model misspecification are outside these intervals",
            ],
            "secondary_test": "H = fixture - (dark+bright)/2; it was not specified in the retained preregistration",
        },
        "preregistered_estimators": cases["preregistered"],
        "original_point_estimates_reproduced": True,
        "original_contraction_statistics": original["contraction"],
        "upstream_secondary_comparison": compare_upstream(pooled, regions, original["secondary"], cases["shots"]),
        "counts": counts,
        "calibration": calibration,
        "acquisition_blocks": blocks,
        "replicas": replica_records,
        "pooled": pooled,
        "regions": regions,
        "interpretation_limits": [
            "dark and bright use 66 CZ and the same selector in each region; fixture uses 70 CZ",
            "the corner fixture uses Q4, while corner dark and bright use Q2",
            "one Latin square does not independently replicate treatment-by-region-by-time interactions",
            "endpoint asymmetry rejects a common symmetric contraction, not every depolarizing channel",
            ("a circuit-dependent effective contraction is a mathematical alternative, not an identified mechanism"),
            ("the raw pooled fixture is near one half partly because regional deviations have opposite signs"),
            ("corrected inference is conditional on the retained readout model, not a model-free device probability"),
            "compatibility with H=0 does not establish that one affine response generated every preparation",
        ],
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Tuna-17 Design B: secondary covariance-aware analysis",
        "",
        (
            "Claim kind: **secondary hardware reanalysis**. This independent analytic audit complements "
            "the retained common-response bootstrap and adds corrected regional estimates."
        ),
        "",
        f"Run: `{report['run']}`. The JSON sidecar binds every input by SHA256.",
        "",
        f"Normalization: {report['method']['normalization']}.",
        "",
        "## Counts and case estimates",
        "",
        (
            "Each Latin-square circuit and each readout calibration contains 16,384 shots. Each "
            "case appears once in each of the three Latin-square circuits, totaling 49,152 attempts"
            " per case. The estimates below pool three fixed regions; the same-shot covariance is "
            "retained between cases."
        ),
        "",
        "| Case | Selector-zero successes / attempts | Raw P(s=0) | Readout-corrected P(s=0) |",
        "|---|---:|---:|---:|",
    ]
    for name in NAMES:
        count = report["counts"][name]
        raw = report["pooled"]["raw"]["by_case"][name]
        corr = report["pooled"]["readout_corrected"]["by_case"][name]
        lines.append(
            f"| {name} | {count['successes']} / {count['attempts']} | {raw['estimate']:.9f} | {corr['estimate']:.9f} |"
        )
    lines += [
        "",
        (
            "All six pooled point estimates reproduce the original analysis. Bright is above 0.5; "
            "it is the endpoint midpoint that lies below 0.5."
        ),
        "",
        "## Joint uncertainty",
        "",
        (
            "The intervals are pointwise normal 95% intervals. The corrected rows include the "
            "shared calibration's finite-shot uncertainty and cross-selector covariance. These "
            "secondary tests have no multiplicity adjustment."
        ),
        "",
        "| Scale | Observable | Estimate | Standard error | 95% interval | z against zero |",
        "|---|---|---:|---:|---|---:|",
    ]
    titles = {
        "endpoint_contrast": "B-D",
        "endpoint_sum_residual": "D+B-1",
        "fixture_minus_half": "F-0.5",
        "fixture_midpoint_residual": "H = F-(D+B)/2",
    }
    for scale in ("raw", "readout_corrected"):
        for name, row in report["pooled"][scale]["metrics"].items():
            low, high = row["ci95_normal"]
            lines.append(
                f"| {scale.replace('_', ' ')} | {titles[name]} | {row['estimate']:+.9f} | "
                f"{row['standard_error']:.9f} | [{low:+.6f}, {high:+.6f}] | {row['z_against_zero']:+.3f} |"
            )
    lines += [
        "",
        (
            "The approximately 13-standard-error ordering survives covariance and calibration "
            "propagation. The original raw fixture consistency result also reproduces. However, "
            "fixture consistency is **raw-only**: under the retained correction model, the pooled "
            "fixture is below 0.5 by about 6.7 standard errors. The correction therefore does not "
            "preserve that conclusion."
        ),
        "",
        (
            "H tests a common affine response in the ideal selector probability. Its raw z is about"
            " 2.72 and its corrected z about 1.61, below the preregistration's absolute-z benchmark"
            " of 3. H itself was not preregistered, so this comparison does not convert it into a "
            "preregistered test. Corrected H is compatible with a common affine probability response "
            "at this precision; this non-rejection does not establish that response or a mechanism."
        ),
        "",
        "## Comparison with the retained bootstrap",
        "",
        (
            "The upstream secondary analysis belongs to the existing "
            "`qi-tuna17-zero-divisor-common-response` claim. Its raw point estimates and complete "
            "case covariance independently reproduce after the explicit n/(n-1) variance adjustment: "
            "the upstream empirical covariance uses n, while this audit uses n-1. The bootstrap "
            "resamples whole same-shot selector vectors and the shared readout calibrations."
        ),
        "",
        "| Corrected observable | Analytic estimate | Analytic SE | Bootstrap mean | Bootstrap SE | "
        "Bootstrap 95% interval |",
        "|---|---:|---:|---:|---:|---|",
    ]
    comparison = report["upstream_secondary_comparison"]
    for name, row in comparison["corrected_uncertainty_comparison"].items():
        bootstrap = row["upstream_bootstrap"]
        low, high = bootstrap["ci95"]
        lines.append(
            f"| {titles[name]} | {row['analytic_point_estimate']:+.9f} | {row['analytic_delta_standard_error']:.9f} | "
            f"{bootstrap['mean']:+.9f} | {bootstrap['se']:.9f} | [{low:+.6f}, {high:+.6f}] |"
        )
    largest = max(
        abs(row["relative_standard_error_difference"])
        for row in comparison["corrected_uncertainty_comparison"].values()
    )
    lines += [
        "",
        f"The retained bootstrap uses {comparison['bootstrap']['draws']:,} draws with seed "
        f"{comparison['bootstrap']['seed']}. The standard errors differ by at most {largest:.1%}. "
        "These methods give the same substantive pooled conclusions. Their numerical difference "
        "also includes finite bootstrap sampling and first-order versus nonlinear propagation; "
        "this is a method comparison, not an independent hardware replication.",
        "",
        "## Regions, selectors and circuit costs",
        "",
        ("| Region | Selectors D / B / F | CZ D / B / F | Raw B-D (95% interval) | Corrected B-D (95% interval) |"),
        "|---|---|---|---|---|",
    ]
    for region in report["regions"]:
        cells = []
        for scale in ("raw", "readout_corrected"):
            row = region[scale]["metrics"]["endpoint_contrast"]
            cells.append(f"{row['estimate']:.6f} [{row['ci95_normal'][0]:+.6f}, {row['ci95_normal'][1]:+.6f}]")
        lines.append(
            f"| {region['region']} | {' / '.join(map(str, region['selectors']))} | "
            f"{' / '.join(map(str, region['cz_counts']))} | {' | '.join(cells)} |"
        )
    lines += [
        "",
        (
            "The corner has **no resolved contrast**, not an established exact zero. All dark and "
            "bright replicas use 66 CZ. A difference of four CZ between dark and bright does not "
            "explain their endpoint asymmetry: those four additional gates belong to the fixtures."
        ),
        "",
        (
            "The corner fixture is measured on Q4, while its dark and bright witnesses use Q2. The "
            "other regions keep the same selector for all three cases. H therefore also compares "
            "different selector responses in the corner, and every fixture differs in state "
            "preparation and depth from the endpoints. It is a descriptive model check, not a "
            "controlled isolation of one noise channel."
        ),
        "",
        "| Region | Raw fixture P(s=0) | Corrected fixture P(s=0) | Raw H (z) | Corrected H (z) |",
        "|---|---:|---:|---:|---:|",
    ]
    for region in report["regions"]:
        raw, corr = region["raw"], region["readout_corrected"]
        rh, ch = raw["metrics"]["fixture_midpoint_residual"], corr["metrics"]["fixture_midpoint_residual"]
        lines.append(
            f"| {region['region']} | {raw['by_case']['fixture']['estimate']:.6f} | "
            f"{corr['by_case']['fixture']['estimate']:.6f} | {rh['estimate']:+.6f} ({rh['z_against_zero']:+.3f}) | "
            f"{ch['estimate']:+.6f} ({ch['z_against_zero']:+.3f}) |"
        )
    lines += [
        "",
        (
            "The raw fixture's regional deviations have opposite signs, so pooled agreement with "
            "0.5 does not establish agreement in every region. The corner's H is largest, including"
            " after correction, but it is also where the selector changes. A single Latin square "
            "balances additive region and row effects without independently replicating all "
            "interactions or drift."
        ),
        "",
        "## Noise interpretation and assumptions",
        "",
        (
            "D+B-1 tests a common symmetric contraction around 0.5. Allowing different effective "
            "contractions for the two circuits can reproduce both endpoints with depolarizing-form "
            "maps. Equal CZ counts constrain a gate-count-only explanation but do not establish "
            "equal effective channels. The measurements do not identify coherent, non-unital or "
            "coupler error uniquely."
        ),
        "",
        (
            "The readout inversion is p_corrected=(p_raw-beta)/(1-alpha-beta), where alpha=P(read "
            "1|prepared 0) and beta=P(read 0|prepared 1). Its derivatives with respect to (p_raw, "
            "alpha, beta) are (1/d, p_corrected/d, (p_corrected-1)/d), with d=1-alpha-beta. "
            "Combining these gradients before covariance propagation retains cancellation and "
            "correlation when multiple estimates share calibration shots."
        ),
        "",
        (
            "The intervals assume independent shots within each acquisition and independence "
            "between jobs. They include same-shot dependence among selectors, but not between-job "
            "drift. They also assume the all-zero/all-one calibration represents readout after the "
            "witness. Those preparations include preparation error and do not establish a pure "
            "assignment channel; model misspecification is outside the reported intervals."
        ),
        "",
        "## Reproduction",
        "",
        "```sh",
        ('"$PYTHON" scripts/qi_zero_divisor_secondary.py --check results/quantum_inspire/secondary --self-test'),
        "```",
        "",
        (
            "The self-test uses exactly correlated and anticorrelated selector samples, and "
            "verifies that shared readout offsets cancel in the appropriate contrasts. The "
            "acquisition blocks retain covariance matrices and input hashes in the JSON sidecar. "
            "This analysis submits no hardware job."
        ),
        "",
    ]
    return "\n".join(lines)


def self_test() -> None:
    positive = [[0, 0], [0, 0], [1, 1], [1, 1]]
    negative = [[0, 1], [0, 1], [1, 0], [1, 0]]
    results = ordered_map(moments, [positive, negative], min_items=1)
    for result, difference, total in zip(results, (0.0, 1 / 3), (1 / 3, 0.0), strict=True):
        covariance = result["covariance_of_mean"]
        if not math.isclose(quadratic([-1, 1], covariance, [-1, 1]), difference, abs_tol=1e-14):
            raise AssertionError("same-shot covariance was lost from a difference")
        if not math.isclose(quadratic([1, 1], covariance, [1, 1]), total, abs_tol=1e-14):
            raise AssertionError("same-shot covariance has the wrong sign in a sum")
    values, derivatives = zip(*(corrected(p, 0.1, 0.2) for p in (0.2, 0.8, 0.5)), strict=True)
    # Only alpha and beta are uncertain, and all three estimates share them.
    gradients = [[0.0, *gradient[1:]] for gradient in derivatives]
    covariance = [[0.0, 0.0, 0.0], [0.0, 0.002, 0.0], [0.0, 0.0, 0.003]]
    summary = summarize(list(values), gradients, covariance, 1)
    h = summary["metrics"]["fixture_midpoint_residual"]
    if abs(h["estimate"]) > 1e-14 or h["standard_error"] > 1e-14:
        raise AssertionError("a shared affine calibration failed to cancel in H")
    expected_variance = ((values[1] - values[0]) / 0.7) ** 2 * 0.005
    actual = summary["metrics"]["endpoint_contrast"]["variance_readout_calibration"]
    if not math.isclose(actual, expected_variance, rel_tol=1e-12):
        raise AssertionError("shared readout covariance is not propagated in the contrast")
    try:
        corrected(0.5, 0.5, 0.5)
    except ValueError:
        pass
    else:
        raise AssertionError("singular readout assignment was accepted")
    print("qi zero-divisor secondary self-test: covariance signs, shared calibration and singularity pass")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not (args.write or args.check or args.self_test):
        parser.error("choose --write, --check or --self-test")
    if args.self_test:
        self_test()
    if args.write or args.check:
        report = analyze()
        files = {f"{STEM}.json": json.dumps(report, indent=1, allow_nan=False) + "\n", f"{STEM}.md": render(report)}
        destination = args.write or args.check
        if args.write:
            destination.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            path = destination / name
            if args.write:
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its secondary replay")
        print(f"qi zero-divisor secondary analysis: {len(files)} files {'written' if args.write else 'reproduced'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
