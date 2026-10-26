"""Diagnostics and the preregistered between-job comparison of the Ascella signed-coherence runs.

docs/design/ascella-signed-coherence-conformance.md registers the permuted
repeat (job-01): the 64 settings of job-00 at 16,384 samples per iteration in
the order an ANU QRNG draw fixes. Four subcommands serve it.

--analyze RUN writes RUN/analysis.json for a collected run of a registered job
other than job-00 (whose analysis ascella_coherence_run.py owns): its
cases.json must equal the case directory's bytes, iterations are attributed
through ascella_coherence_run.attributed, and ascella_coherence_analysis
decides the 27 endpoints. A rerun reproduces the record; --check compares it
within the certificate tolerance, less the digests that name the analyzing
scripts.

--diagnose RUN OUT writes the exploratory reading of one collected run:

- outside-block counts per iteration (modes 4..11) and their pooled mode
  composition against the plan-time detector dark rates of submission.json
  (chi-square over modes 4..11);
- serial structure of log(count + 1/2) outside-block counts in execution order: the lag
  1..4 autocorrelations against a shuffled-position null, and the Spearman
  rank correlation with the L1 size of each iteration's compiled-phase change
  from its predecessor;
- the compiled circuit of every iteration, decoded from its computed_circuit
  and propagated from its computed_input, against the registered ideal
  statistic (largest deviation and largest probability outside modes 0..3);
- analyzer contrast: per readout, the least-squares fit of the
  block-conditioned statistic (denominator modes 0..3) against the ideal,
  z = V ideal + c, and for X and Y the fit with the matched other-quadrature
  ideal, with each setting's residual and the residual chi-square under
  binomial standard errors;
- the 27 endpoints under two exploratory denominators: block-conditioned
  counts, and block-conditioned counts less each mode's dark-rate share of
  the iteration's outside-block counts.

--compare A B OUT applies the preregistered comparison of runs A (job-00) and
B (job-01), matched by setting name:

- identity: Spearman rank correlation between the jobs' per-setting log
  outside-block counts; a fixed per-setting cause predicts it positive;
- sequence: the lag-1 autocorrelation of B's log outside-block counts in B's
  execution order; an alternation between iterations predicts it negative;
- transition: B's Spearman correlation between log outside-block counts and
  compiled-phase change from the predecessor;
- budget: log2 of the ratio of B's to A's median outside-block count at twice
  the samples; acquisition-proportional exposure predicts 1, a per-iteration
  burst 0, decided at the midpoint 0.5;
- residual reproduction: Pearson correlation of the per-setting contrast
  residuals of the two jobs, separately on X and Y settings; a static
  per-configuration error predicts it positive, drift between jobs predicts 0;
- contrast stability: V_B - V_A per readout with its regression standard error.

Each correlation's p-value is two-sided against NULL_DRAWS permutations of one
argument drawn from a generator seeded with NULL_SEED, batched in numpy; a
hypothesis reads supported at p < ALPHA. --self-test builds synthetic B runs
under each outside-block hypothesis and each residual hypothesis, scaled from
job-00's retained counts, and requires the comparison to classify each.

Usage:
  "$PYTHON" scripts/ascella_coherence_repeat.py --analyze RUN
  "$PYTHON" scripts/ascella_coherence_repeat.py --diagnose RUN OUT [--check]
  "$PYTHON" scripts/ascella_coherence_repeat.py --compare A B OUT [--check]
  "$PYTHON" scripts/ascella_coherence_repeat.py --self-test
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_coherence_analysis as analysis  # noqa: E402
import ascella_coherence_run as run_analysis  # noqa: E402
import qd_belenos_mesh as mesh  # noqa: E402
from bdsc_certificate import close  # noqa: E402
from photonic_compilation_audit import _elements  # noqa: E402

from parallel import ordered_map  # noqa: E402

CASES = ROOT / "results/quandela/cases/ascella_signed_coherence"
JOB_00 = ROOT / "results/quandela/runs/2026-10-24T091642Z-qpu_ascella-ascella_signed_coherence-job-00"
LOGICAL = 4
NULL_DRAWS = 20000
# The permutation-null seed of the preregistered comparison: repeat-comparison.json and both diagnostics records
# replay from it, so it is an identifier of those records and keeps its value.
NULL_SEED = 20261024
# The synthetic runs of --self-test draw their seeds from values 0, 1 and 2 of this ANU QRNG draw, in index order.
SELF_TEST_DRAW = "docs/evidence/anu_qrng/draw-2026-10-24T154953Z.json"
ALPHA = 0.01
LAGS = (1, 2, 3, 4)
BUDGET_MIDPOINT = 0.5
# Log outside-block counts carry half a count, so a setting with none stays finite.
LOG_OFFSET = 0.5


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def ranks(values: np.ndarray) -> np.ndarray:
    """Average ranks along the last axis, so ties share their mean rank."""
    return np.asarray(rankdata(values, axis=-1), dtype=float)


def log_counts(values: np.ndarray) -> np.ndarray:
    return np.log(np.asarray(values, dtype=float) + LOG_OFFSET)


def correlation(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pearson correlation of a against every row of b."""
    a0 = a - a.mean()
    b0 = b - b.mean(axis=-1, keepdims=True)
    return np.asarray((b0 * a0).sum(axis=-1) / np.sqrt((a0 * a0).sum() * (b0 * b0).sum(axis=-1)))


def permutation_test(a: np.ndarray, b: np.ndarray, *, rank: bool) -> dict[str, float]:
    """Pearson (rank=False) or Spearman (rank=True) correlation with its two-sided permutation p-value."""
    rng = np.random.default_rng(NULL_SEED)
    shuffled = rng.permuted(np.tile(b, (NULL_DRAWS, 1)), axis=1)
    if rank:
        a, b, shuffled = ranks(a), ranks(b), ranks(shuffled)
    value = float(correlation(a, b[None, :])[0])
    null = correlation(a, shuffled)
    return {"value": value, "p": float((1 + np.sum(np.abs(null) >= abs(value) - 1e-12)) / (1 + NULL_DRAWS))}


def autocorrelation(series: np.ndarray, lag: int) -> np.ndarray:
    """Lag autocorrelation along the last axis."""
    centered = series - series.mean(axis=-1, keepdims=True)
    return np.asarray((centered[..., :-lag] * centered[..., lag:]).sum(axis=-1) / (centered * centered).sum(axis=-1))


def autocorrelation_test(series: np.ndarray, lag: int) -> dict[str, float]:
    rng = np.random.default_rng(NULL_SEED + lag)
    shuffled = rng.permuted(np.tile(series, (NULL_DRAWS, 1)), axis=1)
    value = float(autocorrelation(series, lag))
    null = autocorrelation(shuffled, lag)
    return {"value": value, "p": float((1 + np.sum(np.abs(null) >= abs(value) - 1e-12)) / (1 + NULL_DRAWS))}


def null_test(item: tuple[str, np.ndarray, Any]) -> dict[str, float]:
    """One permutation test: ("lag", series, lag), ("spearman", a, b) or ("pearson", a, b)."""
    kind, first, second = item
    if kind == "lag":
        return autocorrelation_test(first, second)
    return permutation_test(first, second, rank=kind == "spearman")


def contrast_item(item: tuple[list[dict[str, Any]], np.ndarray, str]) -> dict[str, Any]:
    return contrast_fit(*item)


def variant_item(item: tuple[dict[str, Any], np.ndarray]) -> dict[str, Any]:
    return endpoint_variant(*item)


def compiled(entry: dict[str, Any]) -> tuple[list[float], list[float]]:
    """(twelve output probabilities, compiled phases) of one returned iteration's computed circuit and input."""
    fields = entry["result_fields"]
    match = re.fullmatch(r":PCVL:BasicState:\|([01](?:,[01])*)>", fields["computed_input"])
    if match is None:
        raise ValueError("computed_input is not a basic state")
    occupation = [int(value) for value in match[1].split(",")]
    require(len(occupation) == analysis.MODES and sum(occupation) == 1, "computed_input is not one photon on 12")
    elements = _elements(fields["computed_circuit"])
    phases = [value for kind, _, value in elements if kind == "ps"]
    unitary = mesh.unitary(elements, phases)
    probabilities = np.abs(unitary[: analysis.MODES, occupation.index(1)]) ** 2
    require(abs(float(probabilities.sum()) - 1) <= 1e-9, "compiled probabilities fail normalization")
    return [float(value) for value in probabilities], [float(value) for value in phases]


def phase_change(phases: np.ndarray) -> np.ndarray:
    """L1 size of each iteration's wrapped compiled-phase change from its predecessor; NaN for the first."""
    step = np.diff(phases, axis=0)
    wrapped = (step + math.pi) % (2 * math.pi) - math.pi
    return np.concatenate(([math.nan], np.abs(wrapped).sum(axis=1)))


def contrast_fit(settings: list[dict[str, Any]], counts: np.ndarray, readout: str) -> dict[str, Any]:
    """z = V ideal + c on the readout's non-mutation settings with block-conditioned counts, and the quadrature fit."""
    block = counts[:, :LOGICAL]
    total = block.sum(axis=1)
    values = (block[:, 0] - block[:, 3]) / total
    ideals = analysis.registered_ideals(settings)
    own = [i for i, s in enumerate(settings) if s["readout"] == readout and s["block"] != "mutation"]
    other = {"x": "y", "y": "x"}[readout]
    partner = {
        (s["theta_index"], s["arm"]): i
        for i, s in enumerate(settings)
        if s["readout"] == other and s["block"] != "mutation"
    }
    quadrature = np.array([ideals[partner[(settings[i]["theta_index"], settings[i]["arm"])]] for i in own])
    x, y = ideals[own], values[own]
    # z = (n0 - n3) / N takes the values +1, -1 and 0 (modes 1 and 2), so its multinomial variance is
    # ((n0 + n3) / N - z^2) / N.
    signed = (block[own, 0] + block[own, 3]) / total[own]
    se = np.sqrt(np.clip(signed - y * y, 1e-12, None) / total[own])
    design = np.column_stack([x, np.ones_like(x)])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    residual = y - design @ coefficients
    covariance = np.linalg.inv(design.T @ design) * float(residual @ residual) / (len(y) - 2)
    full = np.column_stack([x, quadrature, np.ones_like(x)])
    full_coefficients, *_ = np.linalg.lstsq(full, y, rcond=None)
    full_residual = y - full @ full_coefficients
    return {
        "readout": readout,
        "settings": [settings[i]["name"] for i in own],
        "visibility": float(coefficients[0]),
        "visibility_se": float(math.sqrt(covariance[0, 0])),
        "offset": float(coefficients[1]),
        "residuals": [float(value) for value in residual],
        "residual_chi2": float(((residual / se) ** 2).sum()),
        "dof": len(y) - 2,
        "quadrature_fit": {
            "own": float(full_coefficients[0]),
            "quadrature": float(full_coefficients[1]),
            "offset": float(full_coefficients[2]),
            "residual_chi2": float(((full_residual / se) ** 2).sum()),
            "dof": len(y) - 3,
        },
    }


def endpoint_variant(manifest: dict[str, Any], counts: np.ndarray) -> dict[str, Any]:
    result = analysis.analyze(manifest, counts.tolist())
    return {
        "verdicts": result["verdicts"],
        "ideal_excluded": result["ideal_excluded"],
        "values": {row["name"]: row["value"] for row in result["endpoints"]},
    }


def attributed_rows(manifest: dict[str, Any], results: dict[str, Any]) -> list[list[int] | None]:
    """Each manifest setting's twelve-mode eligible counts, None where results.json returns none for it.

    ascella_coherence_run.attribute attributes every entry, so a request of any iteration count reads as the
    64-iteration design does. Settings that share circuit_params differ only by compilation_seed, so an entry with
    counts must echo its setting's seed; a reordered answer would otherwise exchange anchors and new meshes."""
    entries = results.get("iterations")
    if entries is None and results.get("partial"):
        entries = []
    settings = manifest["settings"]
    if not isinstance(entries, list) or len(entries) > len(settings):
        raise ValueError(f"results.json carries {type(entries).__name__} iterations, not up to {len(settings)}")
    items = [(position, entry, settings[position]) for position, entry in enumerate(entries)]
    for position, entry, setting in items:
        echoed = entry.get("iteration", {}).get("compilation_seed")
        if "counts" in entry and echoed != setting["compilation_seed"]:
            raise ValueError(f"iteration {position}: compilation_seed {echoed!r}, not {setting['name']}'s")
    rows: list[list[int] | None] = [None] * len(settings)
    for (position, _, _), (row, _, _) in zip(items, ordered_map(run_analysis.attribute, items), strict=True):
        rows[position] = row
    return rows


def run_record(directory: Path) -> dict[str, Any]:
    """The collected counts, compiled circuits and plan-time dark rates of one run, in execution order."""
    manifest = load(directory / "cases.json")
    results = load(directory / "results.json")
    rows = attributed_rows(manifest, results)
    require(all(row is not None for row in rows), f"{directory}: not every iteration carries counts")
    decoded = ordered_map(compiled, results["iterations"])
    dark = load(directory / "submission.json")["perfs_at_plan"]["Dark counts (detection/s)"]
    return {
        "manifest": manifest,
        "counts": np.asarray(rows, dtype=float),
        "probabilities": np.asarray([p for p, _ in decoded]),
        "phases": np.asarray([phases for _, phases in decoded]),
        "dark": np.asarray(dark, dtype=float),
    }


def diagnose(directory: Path) -> dict[str, Any]:
    """The exploratory reading of one collected run."""
    record = run_record(directory)
    manifest, counts, dark = record["manifest"], record["counts"], record["dark"]
    settings = manifest["settings"]
    outside = counts[:, LOGICAL:].sum(axis=1)
    observed = counts[:, LOGICAL:].sum(axis=0)
    expected = dark[LOGICAL:] / dark[LOGICAL:].sum() * observed.sum()
    logs = log_counts(outside)
    change = phase_change(record["phases"])
    ideal_values, _ = analysis.statistics(settings, record["probabilities"].tolist())
    block = counts.copy()
    block[:, LOGICAL:] = 0
    subtracted = block.copy()
    share = dark[:LOGICAL] / dark[LOGICAL:].sum()
    subtracted[:, :LOGICAL] = np.clip(block[:, :LOGICAL] - np.outer(outside, share), 0, None)
    tests = ordered_map(
        null_test, [("lag", logs, lag) for lag in LAGS] + [("spearman", change[1:], logs[1:])], min_items=1
    )
    readouts = ("x", "y")
    fits = ordered_map(contrast_item, [(settings, counts, readout) for readout in readouts], min_items=1)
    variants = ("registered", "block_conditioned", "block_less_dark_share")
    variant_rows = ordered_map(
        variant_item, [(manifest, counts), (manifest, block), (manifest, subtracted)], min_items=1
    )
    return {
        "schema": "ascella-signed-coherence-diagnostics-v1",
        "run": directory.relative_to(ROOT).as_posix(),
        "job": manifest["job"],
        "settings": [s["name"] for s in settings],
        "outside_logical_block": [int(value) for value in outside],
        "outside_composition": {
            "modes": list(range(LOGICAL, analysis.MODES)),
            "observed": [int(value) for value in observed],
            "dark_rate_expectation": [float(value) for value in expected],
            "chi2": float(((observed - expected) ** 2 / expected).sum()),
            "dof": analysis.MODES - LOGICAL - 1,
        },
        "serial": {
            "autocorrelation": {str(lag): test for lag, test in zip(LAGS, tests, strict=False)},
            "transition_spearman": tests[-1],
        },
        "compiled": {
            "max_statistic_deviation": float(np.max(np.abs(ideal_values - analysis.registered_ideals(settings)))),
            "max_outside_probability": float(record["probabilities"][:, LOGICAL:].sum(axis=1).max()),
        },
        "contrast": dict(zip(readouts, fits, strict=True)),
        "direct_fit": direct_fit(settings, counts),
        "endpoint_variants": dict(zip(variants, variant_rows, strict=True)),
    }


def direct_fit(settings: list[dict[str, Any]], counts: np.ndarray) -> dict[str, float]:
    """p = a ideal + c on the direct-readout settings with block-conditioned counts."""
    block = counts[:, :LOGICAL]
    total = block.sum(axis=1)
    values = (block[:, 2] + block[:, 3]) / total
    ideals = analysis.registered_ideals(settings)
    own = [i for i, s in enumerate(settings) if s["readout"] == "direct" and s["block"] != "mutation"]
    design = np.column_stack([ideals[own], np.ones(len(own))])
    coefficients, *_ = np.linalg.lstsq(design, values[own], rcond=None)
    return {"slope": float(coefficients[0]), "offset": float(coefficients[1])}


def by_name(record: dict[str, Any], values: np.ndarray) -> dict[str, float]:
    return {s["name"]: float(v) for s, v in zip(record["manifest"]["settings"], values, strict=True)}


def compare_records(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """The preregistered between-job statistics and decisions of runs a (job-00) and b (job-01)."""
    names = [s["name"] for s in a["manifest"]["settings"]]
    require(sorted(names) == sorted(s["name"] for s in b["manifest"]["settings"]), "the runs hold other settings")
    outside_a = by_name(a, a["counts"][:, LOGICAL:].sum(axis=1))
    outside_b = by_name(b, b["counts"][:, LOGICAL:].sum(axis=1))
    log_a = log_counts(np.array([outside_a[n] for n in names]))
    log_b = log_counts(np.array([outside_b[n] for n in names]))
    b_series = log_counts(b["counts"][:, LOGICAL:].sum(axis=1))
    identity, sequence, transition = ordered_map(
        null_test,
        [("spearman", log_a, log_b), ("lag", b_series, 1), ("spearman", phase_change(b["phases"])[1:], b_series[1:])],
        min_items=1,
    )
    budget = math.log2(float(np.median(list(outside_b.values()))) / float(np.median(list(outside_a.values()))))
    readouts = ("x", "y")
    compared = ordered_map(
        readout_comparison,
        [(a["manifest"]["settings"], a["counts"], b["manifest"]["settings"], b["counts"], r) for r in readouts],
        min_items=1,
    )
    residuals = {readout: result["residuals"] for readout, result in zip(readouts, compared, strict=True)}
    contrast = {readout: result["contrast"] for readout, result in zip(readouts, compared, strict=True)}
    return {
        "identity": {**identity, "supported": identity["value"] > 0 and identity["p"] < ALPHA},
        "sequence": {**sequence, "supported": sequence["value"] < 0 and sequence["p"] < ALPHA},
        "transition": {**transition, "supported": transition["value"] > 0 and transition["p"] < ALPHA},
        "budget": {
            "log2_median_ratio": budget,
            "reading": "acquisition-proportional" if budget >= BUDGET_MIDPOINT else "per-iteration",
        },
        "residuals": residuals,
        "contrast": contrast,
    }


def readout_comparison(
    item: tuple[list[dict[str, Any]], np.ndarray, list[dict[str, Any]], np.ndarray, str],
) -> dict[str, Any]:
    """One readout's residual reproduction test and contrast difference between runs a and b."""
    settings_a, counts_a, settings_b, counts_b, readout = item
    fit_a = contrast_fit(settings_a, counts_a, readout)
    fit_b = contrast_fit(settings_b, counts_b, readout)
    res_b = dict(zip(fit_b["settings"], fit_b["residuals"], strict=True))
    matched = np.array([res_b[n] for n in fit_a["settings"]])
    test = permutation_test(np.array(fit_a["residuals"]), matched, rank=False)
    return {
        "residuals": {**test, "reproduces": test["value"] > 0 and test["p"] < ALPHA},
        "contrast": {
            "visibility_a": fit_a["visibility"],
            "visibility_b": fit_b["visibility"],
            "difference": fit_b["visibility"] - fit_a["visibility"],
            "se": math.hypot(fit_a["visibility_se"], fit_b["visibility_se"]),
        },
    }


def compare(a_dir: Path, b_dir: Path) -> dict[str, Any]:
    a, b = run_record(a_dir), run_record(b_dir)
    require(a["manifest"]["job"] == "job-00" and b["manifest"]["job"] == "job-01", "compare reads job-00 then job-01")
    return {
        "schema": "ascella-signed-coherence-comparison-v1",
        "runs": [a_dir.relative_to(ROOT).as_posix(), b_dir.relative_to(ROOT).as_posix()],
        "null_draws": NULL_DRAWS,
        "null_seed": NULL_SEED,
        "alpha": ALPHA,
        **compare_records(a, b),
    }


def analyze(directory: Path) -> dict[str, Any]:
    """The registered analysis of a collected run of a registered job other than job-00."""
    manifest = load(directory / "cases.json")
    job = manifest.get("job")
    require(job != "job-00", "ascella_coherence_run.py owns job-00's analysis")
    frozen = CASES / str(job) / "cases.json"
    require(frozen.is_file(), f"{directory}: job {job!r} has no case directory")
    require((directory / "cases.json").read_bytes() == frozen.read_bytes(), f"{directory}: cases.json is not {job}'s")
    results = load(directory / "results.json")
    rows, exclusions = run_analysis.attributed(manifest, results)
    return {
        "schema": "ascella-signed-coherence-analysis-v1",
        "job": job,
        "job_id": results.get("job_id"),
        "status": (results.get("status") or {}).get("status"),
        "partial": results.get("partial"),
        "mode_counts": rows,
        "eligible": [None if row is None else sum(row) for row in rows],
        "exclusions": exclusions,
        "outside_logical_block": [None if row is None else sum(row[LOGICAL:]) for row in rows],
        "analysis": analysis.analyze(manifest, rows),
        "source_sha256": {
            name: run_analysis.sha256_file(directory / name)
            for name in ("cases.json", "results.json", "submission.json")
        }
        | {
            "scripts/ascella_coherence_repeat.py": run_analysis.sha256_file(Path(__file__)),
            "scripts/ascella_coherence_run.py": run_analysis.sha256_file(Path(run_analysis.__file__)),
            "scripts/ascella_coherence_analysis.py": run_analysis.sha256_file(Path(analysis.__file__)),
        },
    }


def synthetic(a: dict[str, Any], outside: str, residual: str, seed: int) -> dict[str, Any]:
    """A synthetic job-01 run from job-00's retained counts in job-01's order at twice the samples.

    outside picks the outside-block law: "identity" keeps each setting's job-00 rate, "sequence" alternates high
    and low by execution position with job-00's magnitudes, "transition" scales with the compiled-phase change.
    residual picks the analyzer law: "static" keeps job-00's block distribution per setting, "drift" draws from
    a contrast-0.97 ideal with fresh per-setting phase errors."""
    rng = np.random.default_rng(seed)
    b_manifest = load(CASES / "job-01" / "cases.json")
    position = {s["name"]: i for i, s in enumerate(a["manifest"]["settings"])}
    order = [position[s["name"]] for s in b_manifest["settings"]]
    counts_a = a["counts"][order]
    outside_a = counts_a[:, LOGICAL:].sum(axis=1)
    high, low = np.sort(a["counts"][:, LOGICAL:].sum(axis=1))[32:], np.sort(a["counts"][:, LOGICAL:].sum(axis=1))[:32]
    if outside == "identity":
        rates = 2 * outside_a
    elif outside == "sequence":
        rates = np.where(np.arange(64) % 2 == 0, 2 * rng.choice(high, 64), 2 * rng.choice(low, 64))
    else:
        change = phase_change(a["phases"][order])
        change[0] = np.nanmedian(change)
        rates = 2 * np.median(outside_a) * (change / np.median(change)) ** 3
    dark = a["dark"][LOGICAL:] / a["dark"][LOGICAL:].sum()
    block_a = counts_a[:, :LOGICAL] / counts_a[:, :LOGICAL].sum(axis=1, keepdims=True)
    if residual == "static":
        law = block_a
    else:
        law = synthetic_law(b_manifest["settings"], rng)
    samples = 2 * a["counts"].sum(axis=1)[order]
    counts = np.zeros((64, analysis.MODES))
    for i in range(64):
        out = rng.multinomial(int(rng.poisson(rates[i])), dark)
        counts[i, :LOGICAL] = rng.multinomial(int(samples[i] - out.sum()), law[i])
        counts[i, LOGICAL:] = out
    return {**a, "manifest": b_manifest, "counts": counts, "phases": a["phases"][order]}


def synthetic_law(settings: list[dict[str, Any]], rng: np.random.Generator) -> np.ndarray:
    """Block laws at contrast 0.97 with fresh 0.05 rad-scale analyzer residuals per setting."""
    laws = np.zeros((64, LOGICAL))
    for i, setting in enumerate(settings):
        column = np.array([complex(*entry) for entry in setting["column"]])[:LOGICAL]
        probabilities = np.abs(column) ** 2
        if setting["readout"] != "direct":
            z = 0.97 * (probabilities[0] - probabilities[3]) + rng.normal(0, 0.02)
            middle = probabilities[1] + probabilities[2]
            edge = 1 - middle
            probabilities[0], probabilities[3] = edge * (1 + z / edge) / 2, edge * (1 - z / edge) / 2
        laws[i] = np.clip(probabilities, 0, None) / np.clip(probabilities, 0, None).sum()
    return laws


def classify(item: tuple[dict[str, Any], str, str, int, str]) -> dict[str, Any]:
    """The comparison readings of one synthetic job-01 run; mode "burst" halves its outside-block counts."""
    a, outside, residual, seed, mode = item
    b = synthetic(a, outside, residual, seed)
    if mode == "burst":
        b["counts"][:, LOGICAL:] = np.round(b["counts"][:, LOGICAL:] / 2)
    result = compare_records(a, b)
    return {
        "identity": result["identity"]["supported"],
        "sequence": result["sequence"]["supported"],
        "transition": result["transition"]["supported"],
        "reading": result["budget"]["reading"],
        "reproduces": result["residuals"]["x"]["reproduces"],
    }


def self_test() -> int:
    """Synthetic job-01 runs under each hypothesis must be classified as the hypothesis that generated them."""
    a = run_record(JOB_00)
    first, second, third = load(ROOT / SELF_TEST_DRAW)["values"][:3]
    cases: list[tuple[tuple[str, str, int, str], dict[str, Any]]] = [
        (
            ("identity", "static", first, "plain"),
            {"identity": True, "sequence": False, "reproduces": True, "reading": "acquisition-proportional"},
        ),
        (
            ("sequence", "drift", first, "plain"),
            {"identity": False, "sequence": True, "reproduces": False, "reading": "acquisition-proportional"},
        ),
        (("transition", "static", first, "plain"), {"identity": False, "transition": True, "reproduces": True}),
        (("identity", "static", second, "burst"), {"reading": "per-iteration"}),
        (("sequence", "drift", third, "plain"), {"identity": False}),
    ]
    observed = ordered_map(classify, [(a, *key) for key, _ in cases], min_items=1)
    for (key, expected), reading in zip(cases, observed, strict=True):
        for name, value in expected.items():
            require(reading[name] == value, f"synthetic {key}: {name} reads {reading[name]}, not {value}")
    print("ascella coherence repeat: every synthetic hypothesis classified as generated")
    return 0


def without_analyzer(record: Any) -> Any:
    """The record less the digests that name an analyzing script, which a replay by a later revision differs in."""
    if not isinstance(record, dict):
        return record
    trimmed = {key: without_analyzer(value) for key, value in record.items()}
    if isinstance(trimmed.get("source_sha256"), dict):
        trimmed["source_sha256"] = {
            name: digest for name, digest in trimmed["source_sha256"].items() if not name.startswith("scripts/")
        }
    return trimmed


def emit(record: dict[str, Any], out: Path, check: bool) -> None:
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        close(without_analyzer(json.loads(text)), without_analyzer(load(out)), out.relative_to(ROOT).as_posix())
        return
    require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed record")
    out.write_text(text, encoding="utf-8")


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if args == ["--self-test"]:
        return self_test()
    if len(args) == 2 and args[0] == "--analyze":
        directory = Path(args[1]).resolve()
        record = analyze(directory)
        emit(record, directory / "analysis.json", check)
        print(f"{directory.name}: complete {record['analysis']['complete']}, {record['analysis'].get('verdicts')}")
        return 0
    if len(args) == 3 and args[0] == "--diagnose":
        emit(diagnose(Path(args[1]).resolve()), Path(args[2]).resolve(), check)
        return 0
    if len(args) == 4 and args[0] == "--compare":
        emit(compare(Path(args[1]).resolve(), Path(args[2]).resolve()), Path(args[3]).resolve(), check)
        return 0
    raise ValueError(f"usage: see the module docstring, not {argv}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
