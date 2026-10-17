"""Check that collection reads a replica covariance bound only through its variance upper confidence limit.

qpu_planning.measured_family runs n21_exact_planning.covariance_falsifier on
the shot-ordered replica registers and reads, per bound, the declared
projection when the variance upper confidence limit (UCL) stays at or below
it and the UCL otherwise, spending the falsifier tail from the endpoint's
alpha. Planted cases: replicas whose true weighted variance sits just above
the declared projection but inside the allowance, which the earlier
accept-unless-rejected rule admitted, read their UCL; low-variance replicas
read the declared projection; strongly correlated replicas read their UCL;
one PUB of each reads its own; absent, partial or misjoined registers leave
every endpoint on the Hoeffding radius at the full alpha. Each analysis
equals analyze_observations under the bounds it reports. A seeded coverage
run of many planted collections at the boundary variance, through
parallel.py, requires the two-sided interval to cover the true contrast at
its stated level. qpu_planning.prepare drops a candidate whose exact model
fails, keeps its evidence and reason, and refuses only when every candidate
fails; live_run.main refuses the model flags outside the N21 families before
any planning. Explicit failures remain active under optimized Python.
"""

from __future__ import annotations

import copy
import math
from dataclasses import asdict
from types import SimpleNamespace
from typing import Any

import numpy as np

import qpu_planning
from experiment_optimizer import (
    CovarianceBound,
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    analyze_observations,
)

SIGNED = (0.0, 1.0, 0.0, -1.0)
SHOTS = 118784
REPLICAS = 2
VARIANCE_BOUND = 0.55
# The modeled effect the n21-feedback-encoded dry run admitted at this allocation.
PLANNED_EFFECT = 0.0251524664576
LAWS = {
    "feedback": np.array([0.27, 0.2626, 0.2374, 0.23]),
    "no_feedback": np.array([0.27, 0.2374, 0.2374, 0.2552]),
}
RUNTIME = SimpleNamespace(_comparisons_withheld=lambda _required, _executed: None)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _contract() -> ObservableContract:
    return ObservableContract(
        "contrast",
        (ObservableTerm("feedback", SIGNED), ObservableTerm("no_feedback", SIGNED, sign=-1)),
        minimum_effect=0.0,
    )


def _record() -> dict[str, Any]:
    contract = _contract()
    bounds = [
        CovarianceBound(
            contract.name,
            f"pub_{member}",
            tuple(f"{member}/r{k}" for k in range(REPLICAS)),
            tuple(tuple(VARIANCE_BOUND if i == j else 0.0 for j in range(REPLICAS)) for i in range(REPLICAS)),
            "independent replicas",
        )
        for member in LAWS
    ]
    return {
        "shots": SHOTS,
        "observable_contracts": [asdict(contract)],
        "execution_pubs": [
            {
                "name": f"pub_{member}",
                "components": [
                    {"member": member, "registers_by_replica": [[f"g0_r{k}_phase"] for k in range(REPLICAS)]}
                ],
            }
            for member in LAWS
        ],
        "covariance_bounds": [asdict(bound) for bound in bounds],
        "optimization": {
            "selected": "candidate",
            "candidates": [
                {"name": "candidate", "observables": [{"name": contract.name, "effect_used_for_power": PLANNED_EFFECT}]}
            ],
        },
    }


def _outcomes(generator: np.random.Generator, law: np.ndarray, shared: float) -> np.ndarray:
    """(SHOTS, REPLICAS) outcome indices; replica k > 0 copies replica 0 on a shared fraction of shots."""
    outcomes = generator.choice(law.size, size=(SHOTS, REPLICAS), p=law)
    if shared:
        copied = generator.random(SHOTS) < shared
        for replica in range(1, REPLICAS):
            outcomes[copied, replica] = outcomes[copied, 0]
    return outcomes


def _measurement(
    outcomes: dict[str, np.ndarray], shots: int = SHOTS
) -> tuple[dict[str, list[np.ndarray]], dict[str, Any], dict[str, dict[str, list[str]]]]:
    distributions = {
        member: [np.bincount(values[:, k], minlength=4) / shots for k in range(REPLICAS)]
        for member, values in outcomes.items()
    }
    executed = {member: {"pub": f"pub_{member}", "shots": shots} for member in outcomes}
    registers = {
        f"pub_{member}": {f"g0_r{k}_phase": [format(int(v), "02b") for v in values[:, k]] for k in range(REPLICAS)}
        for member, values in outcomes.items()
    }
    return distributions, executed, registers


def _bounds(record: dict[str, Any], test: dict[str, Any]) -> tuple[CovarianceBound, ...]:
    """The bounds a collection reads: each declared matrix with its UCL excess and falsifier tail."""
    if test["branch"] == "hoeffding_fallback":
        return ()
    return tuple(
        CovarianceBound(
            bound["observable_name"],
            bound["pub_name"],
            tuple(bound["labels"]),
            tuple(tuple(row) for row in bound["matrix"]),
            bound["assumption"],
            variance_allowance=row["variance_used"] - row["declared_projection"],
            falsifier_tail=row["tail"],
        )
        for bound, row in zip(record["covariance_bounds"], test["bounds"], strict=True)
    )


def _reference(
    distributions: dict[str, list[np.ndarray]], bounds: tuple[CovarianceBound, ...], shots: int = SHOTS
) -> dict[str, Any]:
    pubs = tuple(
        ObservedPub(f"pub_{member}", {member: tuple(tuple(map(float, d)) for d in rows)}, shots)
        for member, rows in sorted(distributions.items())
    )
    return analyze_observations(pubs, (_contract(),), bounds).as_dict()


def _check_branch(
    label: str,
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    registers: dict[str, dict[str, list[str]]] | None,
    *,
    branch: str,
    sources: list[str] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    result = qpu_planning.measured_family(record, distributions, executed, RUNTIME, replica_registers=registers)
    _require("withheld" not in result, f"{label}: analysis withheld: {result}")
    test = result.pop("replica_covariance")
    _require(test["branch"] == branch, f"{label}: took {test['branch']}, not {branch}")
    bounds = _bounds(record, test)
    _require(result == _reference(distributions, bounds), f"{label}: analysis differs from the {branch} bounds")
    if sources is not None:
        _require([row["source"] for row in test["bounds"]] == sources, f"{label}: sources {test['bounds']}")
    for row in test["bounds"]:
        if "ucl" in row:
            _require(
                row["variance_used"] == max(row["declared_projection"], row["ucl"]),
                f"{label}: a radius reads less than max(declared, UCL)",
            )
    (split,) = test["alpha_split"]
    charged = 1e-3 if bounds else 0.0
    _require(
        math.isclose(split["falsifier_tail"], charged) and math.isclose(split["confidence_tail"], 0.05 - charged),
        f"{label}: alpha split {split}",
    )
    _require(reason is None or reason in test["reason"], f"{label}: reason {test['reason']!r} lacks {reason!r}")
    (power,) = test["power"]
    _require(power["planned_effect"] == PLANNED_EFFECT, f"{label}: planned effect not read from the record")
    _require(
        power["underpowered"] is (power["detection_radius"] + power["power_radius"] > PLANNED_EFFECT),
        f"{label}: underpowered flag disagrees with its radii",
    )
    return test


TRUE_CONTRAST = float((LAWS["feedback"][1] - LAWS["feedback"][3]) - (LAWS["no_feedback"][1] - LAWS["no_feedback"][3]))
COVERAGE_SHOTS = 4096
COVERAGE_RUNS = 400
# Replica 1 copies replica 0 on this fraction of shots, which puts the
# replica-average score variance near 0.284, above the declared 0.275 and
# inside the allowance: the boundary the earlier rule admitted.
BOUNDARY_SHARED = 0.16


def _coverage_run(seed: int) -> tuple[bool, float, float]:
    """One planted boundary collection: (interval covers the true contrast, UCL excess, half-width)."""
    generator = np.random.default_rng(seed)
    outcomes = {}
    for member, law in LAWS.items():
        values = generator.choice(law.size, size=(COVERAGE_SHOTS, REPLICAS), p=law)
        copied = generator.random(COVERAGE_SHOTS) < BOUNDARY_SHARED
        values[copied, 1] = values[copied, 0]
        outcomes[member] = values
    distributions, executed, registers = _measurement(outcomes, COVERAGE_SHOTS)
    record = _record() | {"shots": COVERAGE_SHOTS}
    result = qpu_planning.measured_family(record, distributions, executed, RUNTIME, replica_registers=registers)
    (row,) = result["observables"]
    excess = min(
        bound["variance_used"] - bound["declared_projection"] for bound in result["replica_covariance"]["bounds"]
    )
    return bool(row["lo"] <= TRUE_CONTRAST <= row["hi"]), excess, float(row["confidence_half_width"])


def _verify_coverage() -> tuple[int, float]:
    """Misses of the two-sided interval over planted boundary collections stay within its alpha."""
    import parallel

    seeds = [int(value) for value in np.random.default_rng(20261018).integers(0, 2**63, size=COVERAGE_RUNS)]
    runs = parallel.ordered_map(_coverage_run, seeds, min_items=2)
    misses = sum(not covered for covered, _excess, _width in runs)
    _require(all(excess > 0 for _covered, excess, _width in runs), "a boundary collection read the declared variance")
    # Reject the stated 0.95 coverage only on a binomial upper tail below 1e-3.
    tail = math.fsum(
        math.comb(COVERAGE_RUNS, k) * 0.05**k * 0.95 ** (COVERAGE_RUNS - k) for k in range(misses, COVERAGE_RUNS + 1)
    )
    _require(tail >= 1e-3, f"{misses} misses in {COVERAGE_RUNS} runs reject 0.95 coverage (tail {tail})")
    return misses, float(np.mean([width for _covered, _excess, width in runs]))


def _verify_model_flags() -> None:
    """live_run.main refuses --model-method exact and --replica-variance-bound outside the N21 families."""
    import io
    from contextlib import redirect_stderr
    from unittest.mock import patch

    import live_run

    class _Parsed(Exception):
        pass

    ceilings = ["--max-execution-seconds", "9", "--max-total-execution-seconds", "18"]
    for arguments in (
        ["--family", "folded-correction", "--model-method", "exact"],
        ["--family", "folded-qpe", "--replica-variance-bound", "0.55"],
        ["--model-method", "exact"],
        ["--replica-variance-bound", "0.55"],
    ):
        stderr = io.StringIO()
        try:
            with redirect_stderr(stderr):
                live_run.main([*ceilings, *arguments])
        except SystemExit as error:
            _require(error.code == 2, f"{arguments}: CLI status {error.code}")
        else:
            raise RuntimeError(f"{arguments}: model flags outside the N21 families passed")
        _require("N21 families only" in stderr.getvalue(), f"{arguments}: refusal lacks its reason")
    with patch.object(live_run.local_compute, "settings", side_effect=_Parsed):
        try:
            live_run.main(
                [
                    *ceilings,
                    "--family",
                    "n21-feedback-encoded",
                    "--model-method",
                    "exact",
                    "--replica-variance-bound",
                    "0.55",
                ]
            )
        except _Parsed:
            pass


def _verify_candidate_rejection() -> None:
    """prepare drops a candidate whose exact model fails and refuses only when every candidate fails."""
    from unittest.mock import patch

    import n21_exact_planning

    law = np.array([0.25, 0.25, 0.25, 0.25])
    backend = SimpleNamespace(
        configuration=lambda: SimpleNamespace(
            dynamic_reprate_enabled=True, default_rep_delay=0.00025, rep_delay_range=[0.0, 0.001]
        ),
        target=object(),
    )
    snapshot = SimpleNamespace(name="backend", backend=backend, properties=object(), capabilities=object())

    def candidate(seed: int) -> tuple[list[Any], dict[str, Any]]:
        entries = [SimpleNamespace(name=member, replicas=[object()], ideal=law) for member in LAWS]
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
    contracts = (_contract(),)
    args = SimpleNamespace(
        family="n21-feedback-encoded",
        optimize=True,
        shot_allocation="uniform",
        shot_tiers=[65536],
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
    effective = {member: (tuple(float(v) for v in law),) for member, law in LAWS.items()}
    planted = {"passed": False, "failures": ["planted failure"], "max_gap": 0.0, "arms": {}, "contrasts": {}}
    planted |= {"replicas": [], "radius": 1.0}

    def plan(rejected_seeds: set[int]) -> tuple[Any, dict[str, Any], dict[str, Any]]:
        trace: dict[str, Any] = {}

        def exact(choices: list[Any], *_args: Any) -> tuple[Any, dict[str, Any]]:
            if choices[0].seed in rejected_seeds:
                raise n21_exact_planning.ExactModelRejected(dict(planted))
            return effective, dict(planted, passed=True, failures=[])

        with (
            patch.object(qpu_planning, "family_candidates", return_value=candidates),
            patch.object(qpu_planning, "family_contracts", return_value=contracts),
            patch.object(qpu_planning, "ideal_compiled_probabilities", return_value=law),
            patch.object(qpu_planning.n21_exact_planning, "exact_predictions", side_effect=exact),
        ):
            choices, metadata = qpu_planning.prepare(runtime, [snapshot], args, {"usage_remaining_seconds": 1e9}, trace)
        return choices, metadata, trace

    choices, metadata, trace = plan({1})
    names = [candidate["name"] for candidate in metadata["optimization"]["candidates"]]
    _require(names == ["candidate-001-shots-65536"], f"a rejected candidate reached the optimizer: {names}")
    _require(
        trace.get("model_rejections")
        == [{"candidate": "candidate-000", "reason": str(n21_exact_planning.ExactModelRejected(planted))}],
        f"the rejection left no trace entry: {trace}",
    )
    _require(choices[0].seed == 2, "the surviving candidate was not retained")
    _require(
        metadata["exact_model"]["candidates"]["candidate-000"]["passed"] is False,
        "the rejected candidate's evidence left the record",
    )
    try:
        plan({1, 2})
    except RuntimeError as error:
        _require("every candidate failed" in str(error), f"total rejection raised the wrong error: {error}")
    else:
        raise RuntimeError("prepare planned with every candidate rejected")


def _verify() -> None:
    _verify_model_flags()
    _verify_candidate_rejection()
    generator = np.random.default_rng(20261017)
    record = _record()
    low_law = np.array([0.7, 0.1, 0.1, 0.1])
    low = {member: _outcomes(generator, low_law, 0.0) for member in LAWS}
    boundary = {member: _outcomes(generator, law, BOUNDARY_SHARED) for member, law in LAWS.items()}
    correlated = {member: _outcomes(generator, law, 0.8) for member, law in LAWS.items()}
    mixed = {"feedback": low["feedback"], "no_feedback": correlated["no_feedback"]}

    distributions, executed, registers = _measurement(boundary)
    edge = _check_branch(
        "boundary", record, distributions, executed, registers, branch="ucl_covariance", sources=["ucl", "ucl"]
    )
    for row in edge["bounds"]:
        # The earlier rule accepted any sample variance within the allowance of
        # the declared projection; these rows pass it and still read their UCL.
        _require(
            row["declared_projection"] < row["statistic"] <= row["declared_projection"] + row["allowance"],
            f"boundary row left the band between declared and declared plus allowance: {row}",
        )

    distributions, executed, registers = _measurement(low)
    below = _check_branch(
        "low variance",
        record,
        distributions,
        executed,
        registers,
        branch="declared_covariance",
        sources=["declared"] * 2,
    )
    _check_branch(
        "absent registers",
        record,
        distributions,
        executed,
        None,
        branch="hoeffding_fallback",
        reason="registers are unavailable",
    )
    swapped = copy.deepcopy(registers)
    swapped["pub_feedback"]["g0_r0_phase"] = [bits[::-1] for bits in swapped["pub_feedback"]["g0_r0_phase"]]
    _check_branch(
        "misjoined registers",
        record,
        distributions,
        executed,
        swapped,
        branch="hoeffding_fallback",
        reason="differ from the collected marginal",
    )
    partial = {name: rows for name, rows in registers.items() if name != "pub_no_feedback"}
    _check_branch(
        "one PUB unretained",
        record,
        distributions,
        executed,
        partial,
        branch="hoeffding_fallback",
        reason="pub_no_feedback",
    )

    distributions, executed, registers = _measurement(correlated)
    _check_branch(
        "correlated", record, distributions, executed, registers, branch="ucl_covariance", sources=["ucl"] * 2
    )

    distributions, executed, registers = _measurement(mixed)
    _check_branch(
        "mixed", record, distributions, executed, registers, branch="ucl_covariance", sources=["declared", "ucl"]
    )

    unbounded = {key: value for key, value in record.items() if key != "covariance_bounds"}
    plain = qpu_planning.measured_family(unbounded, distributions, executed, RUNTIME, replica_registers=registers)
    _require("replica_covariance" not in plain, "a record without declared bounds gained a falsifier")
    _require(plain == _reference(distributions, ()), "unbounded analysis changed")
    misses, width = _verify_coverage()
    print(
        "replica covariance contracts: boundary replicas (sample variance "
        + ", ".join(f"{row['statistic']:.4f}" for row in edge["bounds"])
        + " > declared 0.275) read their UCL; low-variance replicas read the declared bound (UCL "
        + f"{below['bounds'][0]['ucl']:.4f}); correlated and mixed read their UCL; absent, partial and misjoined "
        + f"registers fall back to Hoeffding at the full alpha; {COVERAGE_RUNS} planted boundary collections of "
        + f"{COVERAGE_SHOTS} shots miss the true contrast {misses} times (two-sided alpha 0.049, mean half-width "
        + f"{width:.4f}); a failing exact model drops one candidate, not the run"
    )


if __name__ == "__main__":
    # The coverage runs pickle _coverage_run by module name for parallel.py's spawn workers.
    import replica_covariance_contracts

    replica_covariance_contracts._verify()
