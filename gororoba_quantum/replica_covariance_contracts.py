"""Check that collection tests a declared replica covariance bound before it applies it.

qpu_planning.measured_family runs n21_exact_planning.covariance_falsifier on
the shot-ordered replica registers. Planted independent replicas take the
declared-covariance branch and reproduce analyze_observations with the
declared bounds; planted correlated replicas, a single failing PUB, absent
registers and registers that disagree with the collected marginals each take
the Hoeffding branch and reproduce analyze_observations without them. At the
n21-feedback-encoded allocation (118,784 shots per PUB, two replicas) the
declared branch meets the planned power condition and the Hoeffding branch
reports the endpoint underpowered. Explicit failures remain active under
optimized Python. live_run.main refuses the model flags outside the N21
families before any planning.
"""

from __future__ import annotations

import copy
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
    outcomes: dict[str, np.ndarray],
) -> tuple[dict[str, list[np.ndarray]], dict[str, Any], dict[str, dict[str, list[str]]]]:
    distributions = {
        member: [np.bincount(values[:, k], minlength=4) / SHOTS for k in range(REPLICAS)]
        for member, values in outcomes.items()
    }
    executed = {member: {"pub": f"pub_{member}", "shots": SHOTS} for member in outcomes}
    registers = {
        f"pub_{member}": {f"g0_r{k}_phase": [format(int(v), "02b") for v in values[:, k]] for k in range(REPLICAS)}
        for member, values in outcomes.items()
    }
    return distributions, executed, registers


def _reference(distributions: dict[str, list[np.ndarray]], record: dict[str, Any], declared: bool) -> dict[str, Any]:
    pubs = tuple(
        ObservedPub(f"pub_{member}", {member: tuple(tuple(map(float, d)) for d in rows)}, SHOTS)
        for member, rows in sorted(distributions.items())
    )
    bounds = tuple(
        CovarianceBound(
            bound["observable_name"],
            bound["pub_name"],
            tuple(bound["labels"]),
            tuple(tuple(row) for row in bound["matrix"]),
            bound["assumption"],
        )
        for bound in record["covariance_bounds"]
    )
    return analyze_observations(pubs, (_contract(),), bounds if declared else ()).as_dict()


def _check_branch(
    label: str,
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    registers: dict[str, dict[str, list[str]]] | None,
    *,
    declared: bool,
    reason: str | None = None,
) -> dict[str, Any]:
    result = qpu_planning.measured_family(record, distributions, executed, RUNTIME, replica_registers=registers)
    _require("withheld" not in result, f"{label}: analysis withheld: {result}")
    test = result.pop("replica_covariance")
    branch = "declared_covariance" if declared else "hoeffding_fallback"
    _require(test["branch"] == branch and test["holds"] is declared, f"{label}: took {test['branch']}, not {branch}")
    _require(result == _reference(distributions, record, declared), f"{label}: analysis differs from the {branch}")
    methods = {method for row in result["observables"] for method in row["bound_methods"]}
    expected = (
        "minimum_of_hoeffding_and_declared_covariance_cantelli_or_chebyshev"
        if declared
        else "hoeffding_arbitrary_within_shot"
    )
    _require(methods == {expected}, f"{label}: bound methods {methods}")
    _require(reason is None or reason in test["reason"], f"{label}: reason {test['reason']!r} lacks {reason!r}")
    _require(test["specification"]["tail"] == 1e-3, f"{label}: falsifier specification missing")
    (power,) = test["power"]
    _require(power["planned_effect"] == PLANNED_EFFECT, f"{label}: planned effect not read from the record")
    _require(
        power["underpowered"] is (power["detection_radius"] + power["power_radius"] > PLANNED_EFFECT),
        f"{label}: underpowered flag disagrees with its radii",
    )
    _require(power["underpowered"] is not declared, f"{label}: power status {power}")
    return test


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


def _verify() -> None:
    _verify_model_flags()
    generator = np.random.default_rng(20261017)
    record = _record()
    independent = {member: _outcomes(generator, law, 0.0) for member, law in LAWS.items()}
    correlated = {member: _outcomes(generator, law, 0.8) for member, law in LAWS.items()}
    mixed = {"feedback": independent["feedback"], "no_feedback": correlated["no_feedback"]}

    distributions, executed, registers = _measurement(independent)
    passed = _check_branch("independent", record, distributions, executed, registers, declared=True)
    _check_branch(
        "absent registers",
        record,
        distributions,
        executed,
        None,
        declared=False,
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
        declared=False,
        reason="differ from the collected marginal",
    )
    partial = {name: rows for name, rows in registers.items() if name != "pub_no_feedback"}
    _check_branch(
        "one PUB unretained", record, distributions, executed, partial, declared=False, reason="pub_no_feedback"
    )

    distributions, executed, registers = _measurement(correlated)
    failed = _check_branch("correlated", record, distributions, executed, registers, declared=False, reason="exceeds")
    _require(not any(row["holds"] for row in failed["bounds"]), "correlated replicas passed a bound")

    distributions, executed, registers = _measurement(mixed)
    split = _check_branch("mixed", record, distributions, executed, registers, declared=False, reason="pub_no_feedback")
    _require([row["holds"] for row in split["bounds"]] == [True, False], f"mixed verdicts {split['bounds']}")

    unbounded = {key: value for key, value in record.items() if key != "covariance_bounds"}
    plain = qpu_planning.measured_family(unbounded, distributions, executed, RUNTIME, replica_registers=registers)
    _require("replica_covariance" not in plain, "a record without declared bounds gained a falsifier")
    _require(plain == _reference(distributions, record, False), "unbounded analysis changed")
    rows = passed["bounds"]
    print(
        "replica covariance contracts: independent replicas apply the declared bound (statistics "
        + ", ".join(f"{row['statistic']:.4f}" for row in rows)
        + f" <= {rows[0]['threshold']:.4f}); correlated, mixed, absent and misjoined registers fall back to "
        "Hoeffding and report the endpoint underpowered"
    )


if __name__ == "__main__":
    _verify()
