"""Response geometry of the Ascella signed-coherence runs: what a uniform gain explains and what it does not.

docs/design/ascella-signed-coherence-conformance.md holds the registered analysis
of job-00 and the permuted repeat job-01; ascella_coherence_repeat.py holds the
preregistered comparison and the first diagnostics. This module writes one
exploratory record over both runs, with analytic references only:

- gain relations: a setting-independent complex gain g maps the ideal
  coherence C(theta) = (1 - exp(-2i theta))/2 to g C(theta), so the sign-odd
  coefficients obey X0 + Xc2 = 0, Y0 + Yc2 = 0, X0 - Ys2 = 0, Xs2 + Y0 = 0 and
  Xc2 + Ys2 = 0. Each relation is projected onto the job's simultaneous
  registered coefficient intervals, which keeps their joint coverage;
- weighted contrast: z = V ideal + c, and with the matched other-quadrature
  ideal, by inverse-variance least squares under the multinomial variance of
  the block-conditioned statistic, so the residual sum is a chi-square on the
  stated degrees of freedom;
- dilution: the share of each sign-odd shortfall (X constant, Y sin(2 theta))
  that the block-conditioned denominator removes;
- outside profile: the pooled modes 4..11 composition against the plan-time
  catalogue dark profile (Pearson and likelihood-ratio statistics, total
  variation distance, and the largest catalogue share alpha <= min_m p_m/d_m the
  composition admits), and the shared-profile model n_jm = e_j d_m with one
  profile for every iteration: homogeneity tests of the pooled profiles of the
  four quartiles of per-iteration outside total and of the even and odd
  execution positions. Pooling keeps every expected cell above five, where a
  test of the full iteration-by-mode table would have expected cells near one;
- background components: the Poisson fit n_jm = a_j f_m + b_j d_m, catalogue
  profile d held fixed and one profile f fitted, with each component's total,
  median and lag-1 autocorrelation of log(count + 1/2) in execution order, the
  deviance, and the Pearson statistic of the quartile-pooled table against
  the fit, and the dark-component totals and lag-1 autocorrelations at both
  ends of the flat likelihood ridge the factorization admits. The fit is
  descriptive: per-iteration amplitudes leave the deviance without an
  asymptotic reference, and the catalogue profile enters as exact;
- configurations: settings grouped by their returned computed circuit and
  input; the settings sharing one configuration, under any readout label,
  tested against each other within a job, and each readout's pooled
  configuration statistic tested between jobs, which is also the held-out
  prediction of job-01 from job-00's configuration values;
- held-out prediction: job-01's pooled configuration statistics against the
  ideal and against the job-00 gain-and-offset fit, as the quadratic form in
  the full residual covariance: job-01's multinomial variances plus the
  covariance the two shared fitted parameters give every prediction.

Usage:
  "$PYTHON" scripts/ascella_response_geometry.py A B OUT [--check]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_coherence_analysis as analysis  # noqa: E402
import ascella_coherence_repeat as repeat  # noqa: E402
from bdsc_certificate import close  # noqa: E402

from parallel import ordered_map  # noqa: E402

LOGICAL = repeat.LOGICAL
READOUTS = ("x", "y")
IDEAL_SHORTFALL = {"X_odd constant": 0.5, "Y_odd sin(2 theta)": 0.5}
GAIN_RELATIONS = (
    ("X0 + Xc2", ((1, "X_odd constant"), (1, "X_odd cos(2 theta)"))),
    ("Y0 + Yc2", ((1, "Y_odd constant"), (1, "Y_odd cos(2 theta)"))),
    ("X0 - Ys2", ((1, "X_odd constant"), (-1, "Y_odd sin(2 theta)"))),
    ("Xs2 + Y0", ((1, "X_odd sin(2 theta)"), (1, "Y_odd constant"))),
    ("Xc2 + Ys2", ((1, "X_odd cos(2 theta)"), (1, "Y_odd sin(2 theta)"))),
)
# The multinomial variance floor keeps a statistic at the edge of its range finite.
VARIANCE_FLOOR = 1e-12
# The two-component background fit runs a fixed EM step count, so every userland performs the same arithmetic,
# and its last step must raise the Poisson log-likelihood by less than the tolerance.
EM_TOLERANCE = 1e-9
EM_STEPS = 20000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def chi_square(statistic: float, dof: int) -> dict[str, float]:
    return {"statistic": float(statistic), "dof": int(dof), "p": float(chi2.sf(statistic, dof))}


def gain_relations(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each gain relation's value and its projection of the simultaneous registered intervals."""
    rows = {row["name"]: row for row in endpoints}
    out = []
    for label, terms in GAIN_RELATIONS:
        value = sum(sign * rows[name]["value"] for sign, name in terms)
        low = sum(sign * rows[name]["interval"][0 if sign > 0 else 1] for sign, name in terms)
        high = sum(sign * rows[name]["interval"][1 if sign > 0 else 0] for sign, name in terms)
        out.append(
            {
                "relation": label,
                "value": float(value),
                "interval": [float(low), float(high)],
                "excludes_zero": bool(high < 0 or low > 0),
            }
        )
    return out


def statistic(block: np.ndarray, readout: str) -> tuple[np.ndarray, np.ndarray]:
    """Block-conditioned statistic of each row of modes 0..3 counts and its multinomial variance."""
    total = block.sum(axis=-1)
    if readout == "direct":
        value = (block[..., 2] + block[..., 3]) / total
        return value, np.clip(value * (1 - value), VARIANCE_FLOOR, None) / total
    # z = (n0 - n3)/N takes +1, -1 and 0, so its variance is ((n0 + n3)/N - z^2)/N.
    value = (block[..., 0] - block[..., 3]) / total
    signed = (block[..., 0] + block[..., 3]) / total
    return value, np.clip(signed - value * value, VARIANCE_FLOOR, None) / total


def weighted_fit(design: np.ndarray, y: np.ndarray, variance: np.ndarray) -> dict[str, Any]:
    weight = 1 / variance
    normal = design.T @ (design * weight[:, None])
    coefficients = np.linalg.solve(normal, design.T @ (weight * y))
    residual = y - design @ coefficients
    covariance = np.linalg.inv(normal)
    return {
        "coefficients": [float(value) for value in coefficients],
        "se": [float(math.sqrt(covariance[i, i])) for i in range(len(coefficients))],
        **chi_square(float((weight * residual * residual).sum()), len(y) - design.shape[1]),
    }


def weighted_contrast(item: tuple[list[dict[str, Any]], np.ndarray, str]) -> dict[str, Any]:
    """z = V ideal + c and z = V ideal + W quadrature + c by inverse-variance least squares."""
    settings, counts, readout = item
    ideals = analysis.registered_ideals(settings)
    own = [i for i, s in enumerate(settings) if s["readout"] == readout and s["block"] != "mutation"]
    other = {"x": "y", "y": "x"}[readout]
    partner = {
        (s["theta_index"], s["arm"]): i
        for i, s in enumerate(settings)
        if s["readout"] == other and s["block"] != "mutation"
    }
    quadrature = np.array([ideals[partner[(settings[i]["theta_index"], settings[i]["arm"])]] for i in own])
    y, variance = statistic(counts[own, :LOGICAL], readout)
    x = ideals[own]
    gain = weighted_fit(np.column_stack([x, np.ones_like(x)]), y, variance)
    full = weighted_fit(np.column_stack([x, quadrature, np.ones_like(x)]), y, variance)
    return {
        "terms": ["visibility", "offset"],
        "gain_offset": gain,
        "quadrature_terms": ["visibility", "quadrature", "offset"],
        "quadrature": full,
    }


def dilution(registered: list[dict[str, Any]], block: list[dict[str, Any]]) -> dict[str, Any]:
    reg = {row["name"]: row["value"] for row in registered}
    con = {row["name"]: row["value"] for row in block}
    return {
        name: {
            "registered": float(reg[name]),
            "block_conditioned": float(con[name]),
            "ideal": ideal,
            "removed_fraction": float((con[name] - reg[name]) / (ideal - reg[name])),
        }
        for name, ideal in IDEAL_SHORTFALL.items()
    }


def likelihood_ratio(observed: np.ndarray, expected: np.ndarray) -> float:
    positive = observed > 0
    return float(2 * (observed[positive] * np.log(observed[positive] / expected[positive])).sum())


def homogeneity(table: np.ndarray) -> dict[str, Any]:
    """Likelihood-ratio test that every row of a count table shares one profile."""
    table = table[table.sum(axis=1) > 0]
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.sum()
    rows, columns = table.shape
    return {
        **chi_square(likelihood_ratio(table, expected), (rows - 1) * (columns - 1)),
        "min_expected": float(expected.min()),
        "cells_below_five": int((expected < 5).sum()),
        "cells": int(expected.size),
    }


def outside_profile(counts: np.ndarray, dark: np.ndarray) -> dict[str, Any]:
    table = counts[:, LOGICAL:]
    observed = table.sum(axis=0)
    catalogue = dark[LOGICAL:] / dark[LOGICAL:].sum()
    profile = observed / observed.sum()
    expected = catalogue * observed.sum()
    totals = table.sum(axis=1)
    even, odd = table[0::2].sum(axis=0), table[1::2].sum(axis=0)
    # Quartiles of the per-iteration outside total, ties broken by execution position.
    quartiles = np.array_split(np.argsort(totals, kind="stable"), 4)
    return {
        "modes": list(range(LOGICAL, analysis.MODES)),
        "observed": [int(value) for value in observed],
        "catalogue_profile": [float(value) for value in catalogue],
        "observed_profile": [float(value) for value in profile],
        "total_variation": float(0.5 * np.abs(profile - catalogue).sum()),
        "catalogue_pearson": chi_square(float(((observed - expected) ** 2 / expected).sum()), len(observed) - 1),
        "catalogue_likelihood_ratio": chi_square(likelihood_ratio(observed, expected), len(observed) - 1),
        "catalogue_share_upper_bound": float((profile / catalogue).min()),
        "quartile_profiles": {
            "mean_per_iteration": [float(totals[group].mean()) for group in quartiles],
            **homogeneity(np.vstack([table[group].sum(axis=0) for group in quartiles])),
        },
        "parity_profiles": {
            "even_total": int(even.sum()),
            "odd_total": int(odd.sum()),
            "even_mean_per_iteration": float(totals[0::2].mean()),
            "odd_mean_per_iteration": float(totals[1::2].mean()),
            **homogeneity(np.vstack([even, odd])),
        },
    }


def background_components(counts: np.ndarray, dark: np.ndarray) -> dict[str, Any]:
    """Poisson fit n_jm = a_j f_m + b_j d_m of modes 4..11: catalogue dark profile d, one fitted profile f.

    The EM updates of a Poisson non-negative factorization with one column held at d raise the likelihood at every
    step from the even start a_j = b_j = n_j/2, f uniform, so the fit is deterministic."""
    table = counts[:, LOGICAL:]
    catalogue = dark[LOGICAL:] / dark[LOGICAL:].sum()
    columns = table.shape[1]
    profile = np.full(columns, 1 / columns)
    first = table.sum(axis=1) / 2
    second = first.copy()
    positive = table > 0

    def likelihood() -> float:
        mean = np.outer(first, profile) + np.outer(second, catalogue)
        return float((table[positive] * np.log(mean[positive])).sum() - mean.sum())

    previous = -math.inf
    for _ in range(EM_STEPS):
        previous = likelihood()
        ratio = table / (np.outer(first, profile) + np.outer(second, catalogue))
        first, second, profile = first * (ratio @ profile), second * (ratio @ catalogue), profile * (first @ ratio)
        profile = profile / profile.sum()
    require(likelihood() - previous < EM_TOLERANCE, "the background fit did not converge")
    mean = np.outer(first, profile) + np.outer(second, catalogue)
    deviance = 2 * float((table[positive] * np.log(table[positive] / mean[positive])).sum() - (table - mean).sum())
    quartiles = np.array_split(np.argsort(table.sum(axis=1), kind="stable"), 4)
    observed = np.vstack([table[group].sum(axis=0) for group in quartiles])
    fitted = np.vstack([mean[group].sum(axis=0) for group in quartiles])

    def lag_one(values: np.ndarray) -> float:
        return float(repeat.autocorrelation(np.log(values + repeat.LOG_OFFSET), 1))

    # The likelihood is flat along f' = (f - t d)/(1 - t), a' = (1 - t) a, b' = b + t a while every term stays
    # non-negative: t <= min_m f_m/d_m and t >= -min_j b_j/a_j, so only these end points are identified. An
    # amplitude a_j that EM drives toward zero bounds t by -b_j/a_j, far below the binding bound, so amplitudes
    # under 1e-12 of the table's events carry no constraint.
    carried = first > 1e-12 * table.sum()
    ends = (-float((second[carried] / first[carried]).min()), float((profile / catalogue).min()))
    return {
        "admissible_dark_totals": [float((second + t * first).sum()) for t in ends],
        "admissible_dark_lag1": [lag_one(second + t * first) for t in ends],
        "fitted_profile": [float(value) for value in profile],
        "fitted_component": {
            "total": float(first.sum()),
            "median": float(np.median(first)),
            "lag1_log_autocorrelation": lag_one(first),
        },
        "dark_component": {
            "total": float(second.sum()),
            "median": float(np.median(second)),
            "lag1_log_autocorrelation": lag_one(second),
        },
        "deviance": deviance,
        "cells": int(table.size),
        "parameters": int(2 * table.shape[0] + columns - 1),
        "quartile_pearson": float(((observed - fitted) ** 2 / fitted).sum()),
    }


def configurations(record: dict[str, Any]) -> dict[str, list[int]]:
    """Setting indices grouped by returned computed circuit and input, in first-appearance order."""
    groups: dict[str, list[int]] = {}
    for index, entry in enumerate(record["results"]["iterations"]):
        fields = entry["result_fields"]
        groups.setdefault(fields["computed_circuit"] + "\n" + fields["computed_input"], []).append(index)
    return groups


def kind(setting: dict[str, Any]) -> str:
    """The statistic a setting's counts enter: the analyzer z for X and Y, the dark share for direct readouts."""
    return "direct" if setting["readout"] == "direct" else "analyzer"


def pooled(record: dict[str, Any], readout: str) -> dict[tuple[str, ...], tuple[float, float]]:
    """A readout's non-mutation settings grouped by configuration, keyed by sorted names: pooled statistic, variance."""
    settings = record["manifest"]["settings"]
    ideals = analysis.registered_ideals(settings)
    out = {}
    for members in configurations(record).values():
        chosen = [i for i in members if settings[i]["readout"] == readout and settings[i]["block"] != "mutation"]
        if not chosen:
            continue
        require(len({float(ideals[i]) for i in chosen}) == 1, "settings sharing a configuration differ in ideal")
        value, variance = statistic(record["counts"][chosen, :LOGICAL].sum(axis=0), readout)
        out[tuple(sorted(settings[i]["name"] for i in chosen))] = (float(value), float(variance))
    return out


def duplicates(record: dict[str, Any], statistic_kind: str) -> dict[str, Any]:
    """Within-job test that the settings sharing one configuration share one statistic, across readout labels."""
    settings = record["manifest"]["settings"]
    statistic_total = 0.0
    dof = 0
    for members in configurations(record).values():
        if len(members) < 2:
            continue
        kinds = {kind(settings[i]) for i in members}
        require(len(kinds) == 1, "a configuration serves both the analyzer and the direct statistic")
        if kinds != {statistic_kind}:
            continue
        values, variances = statistic(record["counts"][members, :LOGICAL], settings[members[0]]["readout"])
        weight = 1 / variances
        mean = float((weight * values).sum() / weight.sum())
        statistic_total += float((weight * (values - mean) ** 2).sum())
        dof += len(members) - 1
    return chi_square(statistic_total, dof)


def configuration_summary(record: dict[str, Any]) -> dict[str, Any]:
    settings = record["manifest"]["settings"]
    groups = configurations(record)
    shared = [sorted(settings[i]["name"] for i in members) for members in groups.values() if len(members) > 1]
    arm_pairs = all(
        {settings[i]["arm"] for i in members} <= {0, 3} or {settings[i]["arm"] for i in members} <= {1, 2}
        for members in groups.values()
    )
    return {
        "distinct": len(groups),
        "shared": sorted(shared),
        "arms_pair_as_0_3_or_1_2": bool(arm_pairs),
        "duplicates": {statistic_kind: duplicates(record, statistic_kind) for statistic_kind in ("analyzer", "direct")},
    }


def between_jobs(a: dict[str, Any], b: dict[str, Any], readout: str) -> dict[str, Any]:
    """Equality of each pooled configuration statistic between the jobs, and held-out prediction of job-01."""
    pa, pb = pooled(a, readout), pooled(b, readout)
    require(sorted(pa) == sorted(pb), f"{readout}: the jobs group settings into other configurations")
    keys = sorted(pa)
    za, va = np.array([pa[k][0] for k in keys]), np.array([pa[k][1] for k in keys])
    zb, vb = np.array([pb[k][0] for k in keys]), np.array([pb[k][1] for k in keys])
    settings = {s["name"]: s for s in a["manifest"]["settings"]}
    ideal = np.array([analysis.registered_ideals([settings[k[0]]])[0] for k in keys])
    equality = chi_square(float(((za - zb) ** 2 / (va + vb)).sum()), len(keys))
    centered_a, centered_b = za - ideal, zb - ideal
    out: dict[str, Any] = {
        "configurations": [list(k) for k in keys],
        "equality": equality,
        "pooled_residual_correlation": float(np.corrcoef(centered_a, centered_b)[0, 1]),
        "held_out": {
            "ideal": chi_square(float(((zb - ideal) ** 2 / vb).sum()), len(keys)),
        },
    }
    if readout != "direct":
        weight = 1 / va
        design = np.column_stack([ideal, np.ones_like(ideal)])
        normal = design.T @ (design * weight[:, None])
        coefficients = np.linalg.solve(normal, design.T @ (weight * za))
        residual = zb - design @ coefficients
        # Every prediction shares the two fitted parameters, so the residuals carry their full covariance.
        covariance = np.diag(vb) + design @ np.linalg.inv(normal) @ design.T
        out["held_out"]["job_00_gain_offset"] = {
            "visibility": float(coefficients[0]),
            "offset": float(coefficients[1]),
            **chi_square(float(residual @ np.linalg.solve(covariance, residual)), len(keys)),
        }
    return out


def job_record(item: tuple[Path, dict[str, Any]]) -> dict[str, Any]:
    directory, record = item
    manifest, counts = record["manifest"], record["counts"]
    registered = repeat.load(directory / "analysis.json")["analysis"]
    recomputed = analysis.analyze(manifest, counts.tolist())
    close(
        [row["value"] for row in recomputed["endpoints"]],
        [row["value"] for row in registered["endpoints"]],
        f"{directory.name}: endpoints recomputed from counts against analysis.json",
    )
    block = counts.copy()
    block[:, LOGICAL:] = 0
    conditioned = analysis.analyze(manifest, block.tolist())["endpoints"]
    return {
        "job": manifest["job"],
        "registered_ideal_excluded": registered["ideal_excluded"],
        "gain_relations": gain_relations(registered["endpoints"]),
        "gain_relations_block_conditioned": gain_relations(conditioned),
        "dilution": dilution(registered["endpoints"], conditioned),
        "outside_profile": outside_profile(counts, record["dark"]),
        "background_components": background_components(counts, record["dark"]),
        "configurations": configuration_summary(record),
    }


def build(a_dir: Path, b_dir: Path) -> dict[str, Any]:
    records = []
    for directory in (a_dir, b_dir):
        record = repeat.run_record(directory)
        record["results"] = repeat.load(directory / "results.json")
        records.append(record)
    a, b = records
    require(a["manifest"]["job"] == "job-00" and b["manifest"]["job"] == "job-01", "reads job-00 then job-01")
    jobs = ordered_map(job_record, list(zip((a_dir, b_dir), records, strict=True)), min_items=1)
    fits = ordered_map(
        weighted_contrast,
        [(record["manifest"]["settings"], record["counts"], readout) for record in records for readout in READOUTS],
        min_items=1,
    )
    for index, job in enumerate(jobs):
        job["weighted_contrast"] = dict(
            zip(READOUTS, fits[index * len(READOUTS) : (index + 1) * len(READOUTS)], strict=True)
        )
    readouts = ("x", "y", "direct")
    compared = ordered_map(between_item, [(a, b, readout) for readout in readouts], min_items=1)
    return {
        "schema": "ascella-signed-coherence-response-geometry-v1",
        "runs": [a_dir.relative_to(ROOT).as_posix(), b_dir.relative_to(ROOT).as_posix()],
        "jobs": {job["job"]: job for job in jobs},
        "between_jobs": dict(zip(readouts, compared, strict=True)),
    }


def between_item(item: tuple[dict[str, Any], dict[str, Any], str]) -> dict[str, Any]:
    return between_jobs(*item)


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    out = Path(args[2]).resolve()
    repeat.emit(build(Path(args[0]).resolve(), Path(args[1]).resolve()), out, check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
