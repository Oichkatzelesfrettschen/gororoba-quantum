"""Check the empirical-Bernstein confidence and detection rule and its opt-in boundary.

experiment_optimizer composes, for an endpoint whose plan carries an
EmpiricalBernsteinDesign, the Maurer-Pontil empirical-Bernstein radius
(arXiv:0907.3740 Theorem 4) with the data-free Hoeffding or declared
covariance radius at an equal split of the endpoint's alpha. Four sections,
each a gate:

- ``--coverage``: seeded collections of planted endpoints at low and high
  per-shot variance, small and large shot counts, through parallel.py. The
  composed two-sided interval and one-sided detection bound, and the
  empirical-Bernstein radius alone at the full alpha on one PUB, must each
  miss in at most alpha of the runs: the one-sided Clopper-Pearson lower
  limit of the miss rate at level 1 - 1e-3 stays at or below alpha. A
  negative control, the same radius at a tenth of its width, must exceed
  alpha by that test, so the check can fail.
- ``--methods``: the empirical-Bernstein radius undercuts Hoeffding at low
  variance and Hoeffding wins at the maximal variance, through the radius
  functions and through analyze_observations; the per-PUB Minkowski variance
  bound equals the shot-level sample variance for one replica and bounds it
  for correlated replicas; collection composes with declared covariance
  bounds, falsifier tails included, and every alpha split sums to alpha.
- ``--planner``: the planner reads the modeled variance raised by Theorem 10
  (4) and spends the variance tail from the power miss probability; an
  inflated plan needs more shots than the bare model variance would admit,
  and the optimizer picks the inflated tier. qpu_planning.prepare and
  live_run.main refuse the opt-in outside the N21 families or without the
  exact model, and an opted-in plan records the rule, its designs and the
  planned radii.
- ``--default-identity``: every default-path output of the optimizer,
  collection, power radii, planner settings and a mocked
  qpu_planning.prepare serializes to the digests pinned below, which the
  revision without the opt-in produced. A change to any default path fails
  here.

Explicit failures remain active under optimized Python.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from collections.abc import Mapping
from contextlib import redirect_stderr
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import numpy as np
from scipy.stats import beta

import experiment_optimizer
import qpu_planning
import replica_covariance_contracts as rcc
from experiment_optimizer import (
    BudgetContract,
    CandidatePlan,
    CostScenario,
    CovarianceBound,
    EmpiricalBernsteinDesign,
    JobCandidate,
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    PubPrediction,
    analyze_observations,
    empirical_bernstein_radius,
    evaluate_candidate,
    observation_power_radii,
    observed_empirical_bernstein,
    optimize,
    planned_empirical_bernstein,
    sample_deviation_allowance,
)

SIGNED = (0.0, 1.0, 0.0, -1.0)
MEMBERS = ("feedback", "no_feedback")
ALPHA = 0.05
# Planted endpoints: (label, feedback law, no-feedback law, shots per PUB).
# The low-variance laws put most mass on the zero-score labels; the maximal
# laws split it between +1 and -1, the largest variance a span-2 score has.
COVERAGE_CONFIGURATIONS = (
    ("low_variance_256", (0.9, 0.06, 0.0, 0.04), (0.92, 0.04, 0.0, 0.04), 256),
    ("low_variance_4096", (0.9, 0.06, 0.0, 0.04), (0.92, 0.04, 0.0, 0.04), 4096),
    ("maximal_variance_1024", (0.0, 0.5, 0.0, 0.5), (0.0, 0.52, 0.0, 0.48), 1024),
    ("n21_laws_4096", tuple(rcc.LAWS["feedback"]), tuple(rcc.LAWS["no_feedback"]), 4096),
)
COVERAGE_RUNS = 1500
# One-sided Clopper-Pearson level at which a miss rate above alpha is declared.
COVERAGE_LEVEL = 1e-3
NEGATIVE_CONTROL_SCALE = 0.1


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _contract(**overrides: Any) -> ObservableContract:
    return ObservableContract(
        "contrast",
        (ObservableTerm("feedback", SIGNED), ObservableTerm("no_feedback", SIGNED, sign=-1)),
        minimum_effect=0.0,
        **overrides,
    )


DESIGN = (EmpiricalBernsteinDesign("contrast"),)


def _true_contrast(laws: tuple[tuple[float, ...], ...]) -> float:
    return float(sum(np.dot(law, SIGNED) * sign for law, sign in zip(laws, (1, -1), strict=True)))


def _observed(distributions: Mapping[str, Any], shots: int) -> tuple[ObservedPub, ...]:
    return tuple(ObservedPub(f"{member}_pub", {member: distributions[member]}, shots) for member in MEMBERS)


def _clopper_pearson_lower(misses: int, runs: int) -> float:
    return 0.0 if misses == 0 else float(beta.ppf(COVERAGE_LEVEL, misses, runs - misses + 1))


def _coverage_run(item: tuple[int, int]) -> tuple[bool, bool, bool, bool, int]:
    """One planted collection: composed two-sided and one-sided cover, EB-alone and shrunk cover, PUBs read by EB."""
    configuration, seed = item
    _label, first, second, shots = COVERAGE_CONFIGURATIONS[configuration]
    laws = (first, second)
    generator = np.random.default_rng(seed)
    distributions = {
        member: (tuple(float(count) / shots for count in generator.multinomial(shots, law)),)
        for member, law in zip(MEMBERS, laws, strict=True)
    }
    pubs = _observed(distributions, shots)
    contract = _contract()
    (row,) = analyze_observations(pubs, (contract,), (), DESIGN).observables
    truth = _true_contrast(laws)
    two_sided = row.lo <= truth <= row.hi
    _require(row.detection_radius is not None, "a directional endpoint lost its detection radius")
    one_sided = row.estimate - float(row.detection_radius or 0.0) <= truth
    (detail,) = observed_empirical_bernstein(pubs, (contract,), (), DESIGN)
    read = sum(1 for pub in detail["pubs"] if pub["detection"]["method"] == "empirical_bernstein")
    # The empirical-Bernstein radius alone, one-sided at the full alpha, on the
    # feedback PUB's mean score: Theorem 4's constants without the union.
    values = np.asarray(SIGNED)
    frequencies = np.asarray(distributions["feedback"][0])
    mean = float(frequencies @ values)
    variance = shots / (shots - 1) * float(frequencies @ (values - mean) ** 2)
    radius = empirical_bernstein_radius(variance, 2.0, shots, ALPHA, two_sided=False)
    true_mean = float(np.dot(first, SIGNED))
    alone = mean - radius <= true_mean
    shrunk = mean - NEGATIVE_CONTROL_SCALE * radius <= true_mean
    return two_sided, one_sided, alone, shrunk, read


def verify_coverage() -> list[dict[str, Any]]:
    """Every configuration's composed and empirical-Bernstein-alone bounds cover at alpha; the shrunk control fails."""
    import parallel

    seeds = np.random.default_rng(20261018).integers(0, 2**63, size=COVERAGE_RUNS * len(COVERAGE_CONFIGURATIONS))
    items = [
        (configuration, int(seeds[configuration * COVERAGE_RUNS + run]))
        for configuration in range(len(COVERAGE_CONFIGURATIONS))
        for run in range(COVERAGE_RUNS)
    ]
    outcomes = parallel.ordered_map(_coverage_run, items)
    rows = []
    for configuration, (label, _first, _second, shots) in enumerate(COVERAGE_CONFIGURATIONS):
        runs = outcomes[configuration * COVERAGE_RUNS : (configuration + 1) * COVERAGE_RUNS]
        misses = {
            name: sum(1 for run in runs if not run[index])
            for index, name in enumerate(("two_sided", "one_sided", "bernstein_alone", "shrunk_control"))
        }
        lower = {name: _clopper_pearson_lower(count, COVERAGE_RUNS) for name, count in misses.items()}
        for name in ("two_sided", "one_sided", "bernstein_alone"):
            _require(
                lower[name] <= ALPHA,
                f"{label}: {name} misses {misses[name]} of {COVERAGE_RUNS}, Clopper-Pearson lower limit "
                f"{lower[name]:.4f} above alpha {ALPHA}",
            )
        _require(
            lower["shrunk_control"] > ALPHA,
            f"{label}: the radius at {NEGATIVE_CONTROL_SCALE} of its width passed coverage "
            f"({misses['shrunk_control']} misses)",
        )
        read = sum(run[4] for run in runs)
        rows.append({"configuration": label, "shots": shots, "misses": misses, "bernstein_reads": read})
    by_label = {row["configuration"]: row for row in rows}
    _require(
        by_label["low_variance_4096"]["bernstein_reads"] == 2 * COVERAGE_RUNS,
        "low-variance collections did not read the empirical-Bernstein radius on every PUB",
    )
    _require(
        by_label["maximal_variance_1024"]["bernstein_reads"] == 0,
        "maximal-variance collections read the empirical-Bernstein radius",
    )
    return rows


def _hoeffding(span: float, shots: int, tail: float, two_sided: bool) -> float:
    return min(span * math.sqrt(math.log((2.0 if two_sided else 1.0) / tail) / (2 * shots)), span)


def verify_methods() -> dict[str, float]:
    """Method choice at low and maximal variance, the variance statistic, and composition with covariance bounds."""
    # Theorem 4 at one PUB: one-sided ln(2 / d), two-sided ln(4 / d).
    shots, span, tail = 4096, 2.0, 0.0125
    low = empirical_bernstein_radius(0.05, span, shots, tail, two_sided=False)
    expected = math.sqrt(2 * 0.05 * math.log(2 / tail) / shots) + 7 * span * math.log(2 / tail) / (3 * (shots - 1))
    _require(math.isclose(low, expected, rel_tol=1e-15), f"one-sided radius {low} differs from Theorem 4 {expected}")
    two = empirical_bernstein_radius(0.05, span, shots, tail, two_sided=True)
    expected_two = math.sqrt(2 * 0.05 * math.log(4 / tail) / shots) + 7 * span * math.log(4 / tail) / (3 * (shots - 1))
    _require(math.isclose(two, expected_two, rel_tol=1e-15), "the two-sided radius does not spend tail / 2 per side")
    _require(low < _hoeffding(span, shots, 2 * tail, False), "EB at half the tail lost to Hoeffding at low variance")
    high = empirical_bernstein_radius(1.0, span, shots, tail, two_sided=False)
    _require(high > _hoeffding(span, shots, tail, False), "EB beat Hoeffding at the maximal variance")
    _require(empirical_bernstein_radius(0.0, span, 1, tail, False) == span, "one shot must leave the range")
    _require(
        math.isclose(sample_deviation_allowance(span, 101, 0.01), span * math.sqrt(2 * math.log(100) / 100)),
        "Theorem 10 (4) allowance",
    )

    contract = _contract()
    shots = 8192
    low_laws = {"feedback": ((0.9, 0.06, 0.0, 0.04),), "no_feedback": ((0.92, 0.04, 0.0, 0.04),)}
    high_laws = {"feedback": ((0.0, 0.5, 0.0, 0.5),), "no_feedback": ((0.0, 0.52, 0.0, 0.48),)}
    for label, laws, method in (("low", low_laws, "empirical_bernstein"), ("maximal", high_laws, "data_free")):
        pubs = _observed(laws, shots)
        (opted,) = analyze_observations(pubs, (contract,), (), DESIGN).observables
        (plain,) = analyze_observations(pubs, (contract,)).observables
        (detail,) = observed_empirical_bernstein(pubs, (contract,), (), DESIGN)
        _require(
            all(pub[kind]["method"] == method for pub in detail["pubs"] for kind in ("confidence", "detection")),
            f"{label} variance read {[pub['detection']['method'] for pub in detail['pubs']]}, not {method}",
        )
        _require(
            opted.bound_methods == ("minimum_of_hoeffding_and_empirical_bernstein_split_alpha",) * 2,
            f"{label}: bound methods {opted.bound_methods}",
        )
        _require(
            math.isclose(opted.detection_radius or 0.0, detail["radii"]["detection"]["used"], rel_tol=1e-15)
            and math.isclose(
                plain.detection_radius or 0.0, detail["radii"]["detection"]["without_empirical_bernstein"]
            ),
            f"{label}: detail radii differ from the analysis",
        )
        opted_radius, plain_radius = float(opted.detection_radius or 0.0), float(plain.detection_radius or 0.0)
        if label == "low":
            _require(opted_radius < plain_radius, "low variance: EB failed to tighten detection")
            low_ratio = opted_radius / plain_radius
        else:
            # Opting in at the maximal variance pays ln(2 / alpha) for ln(1 / alpha).
            half = math.fsum(_hoeffding(2.0, shots, ALPHA / 2 / 2, False) for _ in MEMBERS)
            _require(math.isclose(opted_radius, half, rel_tol=1e-12), "maximal variance: not Hoeffding")
            _require(opted_radius > plain_radius, "the split costs nothing at maximal variance")
            high_ratio = opted_radius / plain_radius
    for share, tail in ((0.0, 1e-3), (1.0, 1e-3), (0.5, 0.2), (0.5, 0.0)):
        try:
            analyze_observations(
                _observed(low_laws, shots), (contract,), (), (EmpiricalBernsteinDesign("contrast", share, tail),)
            )
        except ValueError:
            continue
        raise RuntimeError(f"share {share} and variance tail {tail} passed validation")
    for designs in ((EmpiricalBernsteinDesign("absent"),), DESIGN * 2):
        try:
            analyze_observations(_observed(low_laws, shots), (contract,), (), designs)
        except ValueError:
            continue
        raise RuntimeError(f"designs {designs} passed validation")

    # The Minkowski bound on two correlated replicas' averaged score against
    # the shot-level sample variance, and equality for one replica.
    generator = np.random.default_rng(20261019)
    outcomes = rcc._outcomes(generator, rcc.LAWS["feedback"], 0.8)
    scores = np.asarray(SIGNED)[outcomes]
    exact = float(np.var(scores.mean(axis=1), ddof=1))
    single = float(np.var(scores[:, 0], ddof=1))
    rows = tuple(tuple(np.bincount(outcomes[:, k], minlength=4) / outcomes.shape[0]) for k in range(2))
    for replicas, statistic in ((rows, exact), (rows[:1], single)):
        pub = ObservedPub("feedback_pub", {"feedback": replicas}, outcomes.shape[0])
        mean_contract = ObservableContract("mean", (ObservableTerm("feedback", SIGNED),), precision_half_width=0.1)
        (detail,) = observed_empirical_bernstein((pub,), (mean_contract,), (), (EmpiricalBernsteinDesign("mean"),))
        bound = detail["pubs"][0]["variance"]
        if len(replicas) == 1:
            _require(math.isclose(bound, statistic, rel_tol=1e-12), f"one replica: {bound} != {statistic}")
        else:
            _require(statistic <= bound + 1e-12, f"Minkowski bound {bound} below the sample variance {statistic}")

    # Composition with declared covariance bounds through measured_family:
    # falsifier tails, then the data-free and empirical-Bernstein halves.
    record = rcc._record()
    record["empirical_bernstein"] = {
        "specification": dict(experiment_optimizer.EMPIRICAL_BERNSTEIN),
        "designs": [{"observable_name": "contrast", "share": 0.5, "variance_tail": 1e-3}],
        "planned": [],
    }
    generator = np.random.default_rng(20261020)
    low_law = np.array([0.7, 0.1, 0.1, 0.1])
    planted = {member: rcc._outcomes(generator, low_law, 0.0) for member in rcc.LAWS}
    distributions, executed, registers = rcc._measurement(planted)
    result = qpu_planning.measured_family(record, distributions, executed, rcc.RUNTIME, replica_registers=registers)
    _require("withheld" not in result, f"opted-in collection withheld: {result}")
    block = result.pop("empirical_bernstein")
    covariance = result.pop("replica_covariance")
    bounds = rcc._bounds(record, covariance)
    designs = (EmpiricalBernsteinDesign("contrast"),)
    reference = analyze_observations(
        tuple(
            ObservedPub(f"pub_{member}", {member: tuple(tuple(map(float, d)) for d in rows_)}, rcc.SHOTS)
            for member, rows_ in sorted(distributions.items())
        ),
        (rcc._contract(),),
        bounds,
        designs,
    ).as_dict()
    _require(result == reference, "opted-in collection differs from analyze_observations under its bounds")
    (detail,) = block["endpoints"]
    _require(
        math.isclose(
            detail["falsifier_tail"] + detail["data_free_tail"] + detail["empirical_bernstein_tail"], detail["alpha"]
        )
        and math.isclose(detail["falsifier_tail"], 1e-3),
        f"alpha split {detail}",
    )
    (power,) = block["power"]
    _require(
        math.isclose(power["power_radius"], detail["power_radius"]) and math.isclose(detail["power_tail"], 0.199),
        "collection power radius left the variance-tail rule",
    )
    unopted_record = rcc._record()
    unopted = qpu_planning.measured_family(
        unopted_record, distributions, executed, rcc.RUNTIME, replica_registers=registers
    )
    _require("empirical_bernstein" not in unopted, "a record without designs gained the empirical-Bernstein block")
    return {"low_variance_detection_ratio": low_ratio, "maximal_variance_detection_ratio": high_ratio}


def _plan(name: str, shots: int, laws: tuple[tuple[float, ...], ...], replicas: int = 1) -> CandidatePlan:
    pubs = tuple(
        PubPrediction(
            f"{member}_pub",
            {member: (law,) * replicas},
            0.0001,
            0.00025,
            "fixture duration",
            simulation_shots=None,
            classical_stage_count=1,
        )
        for member, law in zip(MEMBERS, laws, strict=True)
    )
    return CandidatePlan(name, (JobCandidate("job", pubs, shots, 2.3, 400.0, "fixture overhead"),))


def _smallest_admitted(laws: tuple[tuple[float, ...], ...], designs: tuple[EmpiricalBernsteinDesign, ...]) -> int:
    contract = _contract()
    budget = BudgetContract(1e6, 0.0, 1e6)
    for shots in range(1024, 400_000, 1024):
        plan = replace(_plan("search", shots, laws), empirical_bernstein=designs)
        if evaluate_candidate(plan, (contract,), budget).feasible:
            return shots
    raise RuntimeError("no admitted shot count below 400,000")


def verify_planner() -> dict[str, Any]:
    """Planned variances, the power tail, tier choice under the inflation, and the planner's opt-in boundary."""
    laws = tuple(tuple(map(float, rcc.LAWS[member])) for member in MEMBERS)
    contract = _contract()
    shots = 98304
    for replicas in (1, 2):
        plan = replace(_plan("planned", shots, laws, replicas), empirical_bernstein=DESIGN)
        (detail,) = planned_empirical_bernstein(plan, (contract,))
        for row, law in zip(detail["pubs"], laws, strict=True):
            values = np.asarray(SIGNED)
            sigma = math.sqrt(float(np.dot(law, (values - np.dot(law, values)) ** 2)))
            tail = 1e-3 / (2 * replicas)
            expected = (sigma + 2.0 * math.sqrt(2 * math.log(1 / tail) / (shots - 1))) ** 2
            _require(
                math.isclose(row["variance"], expected, rel_tol=1e-12) and row["variance"] > sigma * sigma,
                f"R={replicas}: planned variance {row['variance']} != {expected}",
            )
        (observable,) = evaluate_candidate(plan, (contract,), BudgetContract(1e6, 0.0, 1e6)).observables
        _require(
            math.isclose(observable.detection_radius or 0.0, detail["radii"]["detection"]["used"], rel_tol=1e-15)
            and math.isclose(observable.power_radius or 0.0, detail["power_radius"], rel_tol=1e-15)
            and math.isclose(detail["power_tail"], 1 - 0.8 - 1e-3),
            f"R={replicas}: the admitted radii differ from the planned detail",
        )
    with patch.object(experiment_optimizer, "sample_deviation_allowance", lambda *_args: 0.0):
        bare = _smallest_admitted(laws, DESIGN)
    inflated = _smallest_admitted(laws, DESIGN)
    hoeffding = _smallest_admitted(laws, ())
    _require(bare < inflated < hoeffding, f"shots: bare {bare}, inflated {inflated}, Hoeffding {hoeffding}")
    tiers = tuple(replace(_plan(f"tier-{n}", n, laws), empirical_bernstein=DESIGN) for n in (bare, inflated))
    selected = optimize(tiers, (contract,), BudgetContract(1e6, 0.0, 1e6)).selected
    _require(selected == f"tier-{inflated}", f"the optimizer selected {selected}, not the inflated tier")

    import live_run

    metadata = prepared(empirical_bernstein=True)
    block = metadata["empirical_bernstein"]
    _require(
        block["specification"] == experiment_optimizer.EMPIRICAL_BERNSTEIN
        and block["designs"] == [{"observable_name": "contrast", "share": 0.5, "variance_tail": 0.001}]
        and metadata["optimizer_settings"]["empirical_bernstein"] is True,
        "the opted-in record lacks its rule, designs or setting",
    )
    selected_row = next(
        candidate
        for candidate in metadata["optimization"]["candidates"]
        if candidate["name"] == metadata["optimization"]["selected"]
    )
    (planned,) = block["planned"]
    _require(
        math.isclose(planned["radii"]["detection"]["used"], selected_row["observables"][0]["detection_radius"]),
        "the recorded planned radius differs from the selected candidate",
    )
    for overrides, label in (
        ({"model_method": "sampled"}, "sampled model"),
        ({"family": "folded-qpe", "model_method": "sampled"}, "family"),
    ):
        try:
            prepared(empirical_bernstein=True, **overrides)
        except RuntimeError as error:
            _require("--empirical-bernstein" in str(error), f"{label}: refused for another reason: {error}")
        else:
            raise RuntimeError(f"prepare accepted the opt-in with a {label} outside its scope")
    ceilings = ["--max-execution-seconds", "9", "--max-total-execution-seconds", "18"]
    for arguments in (
        ["--family", "folded-qpe", "--empirical-bernstein"],
        ["--family", "n21-feedback-encoded", "--empirical-bernstein"],
    ):
        stderr = io.StringIO()
        try:
            with redirect_stderr(stderr):
                live_run.main([*ceilings, *arguments])
        except SystemExit as error:
            _require(error.code == 2, f"{arguments}: CLI status {error.code}")
        else:
            raise RuntimeError(f"{arguments}: the CLI accepted the opt-in")
        _require("--empirical-bernstein applies" in stderr.getvalue(), f"{arguments}: refusal lacks its reason")
    return {"bare_shots": bare, "inflated_shots": inflated, "hoeffding_shots": hoeffding}


def prepared(**overrides: Any) -> dict[str, Any]:
    """qpu_planning.prepare on two mocked N21 candidates under exact laws: the planner's record metadata."""
    law = np.array([0.25, 0.25, 0.25, 0.25])
    laws = {member: tuple(float(v) for v in values) for member, values in rcc.LAWS.items()}
    backend = SimpleNamespace(
        configuration=lambda: SimpleNamespace(
            dynamic_reprate_enabled=True, default_rep_delay=0.00025, rep_delay_range=[0.0, 0.001]
        ),
        target=object(),
    )
    snapshot = SimpleNamespace(name="backend", backend=backend, properties=object(), capabilities=object())

    def candidate(seed: int) -> tuple[list[Any], dict[str, Any]]:
        entries = [SimpleNamespace(name=member, replicas=[object()], ideal=law) for member in laws]
        choice = SimpleNamespace(
            group=SimpleNamespace(name="n21_feedback_encoded"),
            entries=entries,
            snap=snapshot,
            seed=seed,
            replicas=[object()],
            joint_score=0.9,
        )
        return [choice], {"name": "n21-feedback-encoded", "seed": seed}

    candidates = [candidate(1), candidate(2)]
    pubs = {
        id(choices[0]): [
            SimpleNamespace(
                name=f"pub_{entry.name}",
                circuit=object(),
                components=(SimpleNamespace(entry=entry),),
                manifest=lambda: {"sequential_stage_count": 0},
            )
            for entry in choices[0].entries
        ]
        for choices, _configuration in candidates
    }
    runtime = SimpleNamespace(
        LiveRunError=RuntimeError,
        group_admission_violations=lambda _group, _capabilities: [],
        noise_simulator=lambda *_args: SimpleNamespace(options=SimpleNamespace(noise_model=None)),
        simulate=lambda choice, *_args: {entry.name: [entry.ideal] for entry in choice.entries},
        submission_batches=lambda selected, kind, _shots: [pubs[id(selected[0])]] if kind == "dynamic" else [],
        duration_s=lambda *_args: 0.0001,
        _scrub_instances=lambda value: value,
        _jsonable=lambda value: value,
    )
    settings: dict[str, Any] = dict(
        family="n21-feedback-encoded",
        optimize=True,
        shot_allocation="uniform",
        shot_tiers=[32768, 65536, 98304, 131072],
        shots=65536,
        model_shots=65536,
        model_method="exact",
        replica_variance_bound=None,
        max_execution_seconds=1e6,
        max_total_execution_seconds=1e6,
        reserve_seconds=0.0,
        job_overhead_seconds=2.3,
        classical_latency_us=20.0,
        precision=0.08,
        alpha=0.05,
        power=0.8,
        simulation_alpha=0.01,
        cost_scenarios=[],
    )
    args = SimpleNamespace(**(settings | overrides))
    effective = {member: (values,) for member, values in laws.items()}
    evidence = {"passed": True, "failures": [], "max_gap": 0.0, "arms": {}, "contrasts": {}, "replicas": []}
    contracts = (rcc._contract(),)
    with (
        patch.object(qpu_planning, "family_candidates", return_value=candidates),
        patch.object(qpu_planning, "family_contracts", return_value=contracts),
        patch.object(qpu_planning, "ideal_compiled_probabilities", return_value=law),
        patch.object(qpu_planning.n21_exact_planning, "exact_predictions", return_value=(effective, dict(evidence))),
    ):
        _choices, metadata = qpu_planning.prepare(runtime, [snapshot], args, {"usage_remaining_seconds": 1e9}, {})
    return metadata


def surfaces() -> dict[str, Any]:
    signed = (0.0, 1.0, 0.0, -1.0)
    terms = (ObservableTerm("feedback", signed), ObservableTerm("no_feedback", signed, sign=-1))
    directional = ObservableContract("contrast", terms, minimum_effect=0.0)
    fixed = ObservableContract("fixed_effect", terms, minimum_effect=0.02, alpha=0.01, power=0.9)
    precision = ObservableContract("precision", (terms[0],), precision_half_width=0.01)
    budget = BudgetContract(1000.0, 10.0, 800.0)
    laws = tuple(tuple(map(float, rcc.LAWS[member].tolist())) for member in MEMBERS)
    plans = tuple(_plan(f"shots-{shots}", shots, laws) for shots in (32768, 65536, 131072))
    two = _plan("replicas-2", 98304, laws, replicas=2)
    bounds = tuple(
        CovarianceBound(
            "contrast",
            f"{member}_pub",
            (f"{member}/r0", f"{member}/r1"),
            ((0.55, 0.0), (0.0, 0.55)),
            "fixture independence",
            variance_allowance=0.03,
            falsifier_tail=5e-4,
        )
        for member in ("feedback", "no_feedback")
    )
    bounded = replace(two, name="replicas-2-bounded", covariance_bounds=bounds)
    contracts = (directional, fixed, precision)
    out: dict[str, Any] = {}
    out["optimize"] = optimize((*plans, two, bounded), contracts, budget).as_dict()
    out["optimize_scenario"] = optimize(
        plans, contracts, budget, cost_scenarios=(CostScenario("slow", 4.0, 100.0),)
    ).as_dict()
    out["evaluate_bounded"] = repr(evaluate_candidate(bounded, contracts, budget))
    observed = tuple(
        ObservedPub(f"{member}_pub", {member: (law,)}, 65536) for member, law in zip(MEMBERS, laws, strict=True)
    )
    observed_two = tuple(
        ObservedPub(f"{member}_pub", {member: (law, law)}, 98304) for member, law in zip(MEMBERS, laws, strict=True)
    )
    out["analyze"] = analyze_observations(observed, contracts).as_dict()
    out["analyze_bounded"] = analyze_observations(observed_two, contracts, bounds).as_dict()
    out["power_radii"] = observation_power_radii(observed, contracts)
    out["power_radii_bounded"] = observation_power_radii(observed_two, contracts, bounds)
    generator = np.random.default_rng(20261017)
    outcomes = {member: rcc._outcomes(generator, law, 0.0) for member, law in rcc.LAWS.items()}
    distributions, executed, registers = rcc._measurement(outcomes)
    record = rcc._record()
    out["measured_bounded"] = qpu_planning.measured_family(
        record, distributions, executed, rcc.RUNTIME, replica_registers=registers
    )
    unbounded = {key: value for key, value in record.items() if key != "covariance_bounds"}
    out["measured_unbounded"] = qpu_planning.measured_family(unbounded, distributions, executed, rcc.RUNTIME)
    out["settings"] = {
        family: qpu_planning.settings(SimpleNamespace(family=family))
        for family in ("n21-feedback-encoded", "folded-qpe", "ripple")
    }
    out["prepare"] = prepared()
    return out


# sha256 of json.dumps(value, sort_keys=True) for each default-path surface,
# pinned from the revision without the empirical-Bernstein opt-in.
DEFAULT_DIGESTS = {
    "analyze": "b355d8cf04c4a977a5f44a96d2fb7bc9796d6fe4db7331534b57bb7d49ff79d7",
    "analyze_bounded": "5170787e8798f5240b8761ea2a65adc37a09571a01a47fc0ee415287fe885ed6",
    "evaluate_bounded": "57ba556ba1e3b04eefbf7edec23ebc3ef51d36e06ea790afc1757a8cef816d9d",
    "measured_bounded": "c5dc4c189ee8660f6364fea63aa97f63674bfafb3b7cac22f36eb9fff204080e",
    "measured_unbounded": "c04750d123b50aefa6e6a74c879640f62383fcc1a65a8b5fbcc37c0b9676ca72",
    "optimize": "5620f431a154e114e172598ab7695241a4d01341e4e59b2d094159ae3bf8defb",
    "optimize_scenario": "51b8856f1af05860465c691f313ee9fd45e2434f1b6341680c407de93014fa12",
    "power_radii": "be24b823812f6a6ddbcdeaa463457235413cc9a8e65c358c5eaebab6d38b3c32",
    "power_radii_bounded": "6d5605d513f0ca2e45cac07e783b9edb5a2e1d83f4e8f98dd66d3b7ebe9d5a9e",
    "prepare": "c136180ebd4d471131fe9bcfe434bdf2628603be16411396f03c3e7c25ab4975",
    "settings": "9c4b948876933045289de49de881d1a30567447a7dab34af46f031214dc9dc80",
}


def verify_default_identity() -> int:
    """Every default-path surface reproduces its pinned digest; replay arguments omit the flag."""
    import qpu_cases

    digests = {
        name: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
        for name, value in surfaces().items()
    }
    changed = sorted(name for name in DEFAULT_DIGESTS if digests.get(name) != DEFAULT_DIGESTS[name])
    _require(not changed and digests.keys() == DEFAULT_DIGESTS.keys(), f"default surfaces changed: {changed}")
    record = qpu_cases._fixture()
    path = "results/live/fixture/record.json"
    _require(
        "--empirical-bernstein" not in qpu_cases._reproduction_arguments(record, Path(path)),
        "a record without the opt-in replays it",
    )
    record["policy"]["design"]["empirical_bernstein"] = True
    _require(
        "--empirical-bernstein" in qpu_cases._reproduction_arguments(record, Path(path)),
        "an opted-in record replays without the flag",
    )
    return len(digests)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    for name in ("coverage", "methods", "planner", "default-identity"):
        group.add_argument(f"--{name}", action="store_true")
    parsed = parser.parse_args()
    if parsed.coverage:
        rows = verify_coverage()
        print(
            f"empirical Bernstein coverage: {COVERAGE_RUNS} seeded collections per configuration; misses "
            + "; ".join(
                f"{row['configuration']} two-sided {row['misses']['two_sided']}, one-sided "
                f"{row['misses']['one_sided']}, EB alone {row['misses']['bernstein_alone']}, shrunk control "
                f"{row['misses']['shrunk_control']}"
                for row in rows
            )
            + f"; every bound within alpha {ALPHA} at Clopper-Pearson level {COVERAGE_LEVEL}, the control above it"
        )
    elif parsed.methods:
        ratios = verify_methods()
        print(
            "empirical Bernstein methods: detection radius "
            f"{ratios['low_variance_detection_ratio']:.4f} x the Hoeffding radius at low variance and "
            f"{ratios['maximal_variance_detection_ratio']:.4f} x at the maximal variance (Hoeffding read at the "
            "split tail); one-replica variance exact, correlated replicas bounded; composition with covariance "
            "falsifier tails sums to alpha"
        )
    elif parsed.planner:
        shots = verify_planner()
        print(
            "empirical Bernstein planner: N=21 laws admit at "
            f"{shots['bare_shots']} shots on the bare model variance, {shots['inflated_shots']} on its Theorem 10 "
            f"(4) upper limit and {shots['hoeffding_shots']} under Hoeffding; the optimizer takes the inflated tier; "
            "prepare and the CLI refuse the opt-in outside the N21 exact plans"
        )
    else:
        count = verify_default_identity()
        print(f"empirical Bernstein default identity: {count} default-path surfaces reproduce their pinned digests")


if __name__ == "__main__":
    # The coverage runs pickle _coverage_run by module name for parallel.py's spawn workers.
    import empirical_bernstein_contracts

    empirical_bernstein_contracts.main()
