"""Bounded experiment design under explicit statistical and charge assumptions.

The optimizer compares supplied plans; it neither compiles circuits nor contacts
a service. A plan must meet every named observable contract. Signed contrasts
retain their own admission requirements. The objective selects either minimum
modeled charge or minimum worst normalized precision radius within the budget.

Hoeffding bounds assume independent repetitions of stationary, bounded outcomes.
Replicas and components within one PUB shot may be arbitrarily dependent. A
declared covariance upper bound can tighten the bound through Cantelli or
Chebyshev. An endpoint that opts in through EmpiricalBernsteinDesign also takes
the Maurer-Pontil empirical-Bernstein radius, read from the sample variance,
on its own share of the endpoint's alpha. Union bounds require no independence
between PUBs. Finite-shot noise
predictions receive a separate simultaneous Hoeffding error allowance across the
entire candidate search. These guarantees concern the supplied noise model;
hardware-model discrepancy remains unquantified.

Run the module directly for deterministic, service-free self-tests.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ObservableTerm:
    """One member's bounded score vector, added or subtracted from a contrast."""

    member: str
    values: tuple[float, ...]
    sign: int = 1


@dataclass(frozen=True)
class ObservableContract:
    """A named endpoint with precision or one-sided effect/power requirements.

    A positive minimum_effect specifies an alternative that far above null_value.
    The prediction must clear that alternative, and the experiment must detect
    the declared minimum effect with the requested conditional power. Zero uses
    the positive modeled gap after the simulation allowance as the alternative;
    the result names that effect explicitly. alpha is
    per endpoint; the model-simulation confidence is a separate search-wide
    allowance. precision_half_width requests a two-sided confidence interval.
    """

    name: str
    terms: tuple[ObservableTerm, ...]
    null_value: float = 0.0
    minimum_effect: float | None = None
    alpha: float = 0.05
    power: float = 0.8
    precision_half_width: float | None = None


@dataclass(frozen=True)
class PubPrediction:
    """Predicted replica marginals and the cost of repeating one exact PUB.

    A member name occurs in exactly one PUB across a plan. simulation_shots
    records the samples behind every marginal; None asserts exact deterministic
    model probabilities. scheduled_seconds contains the supplied circuit
    duration. reset_seconds and classical_latency_seconds add only components
    absent from that duration. duration_assumption states that accounting
    boundary, including uncertainty such as an unmeasured scheduler residual.
    classical_stage_count supplies the explicit count needed to replace the
    added classical latency under a cost-sensitivity scenario; static PUBs use 0.
    """

    name: str
    member_distributions: dict[str, tuple[tuple[float, ...], ...]]
    scheduled_seconds: float
    repetition_delay_seconds: float
    duration_assumption: str
    reset_seconds: float = 0.0
    classical_latency_seconds: float = 0.0
    simulation_shots: int | None = None
    classical_stage_count: int | None = None


@dataclass(frozen=True)
class JobCandidate:
    """One actual backend/kind batch, with its own execution ceiling."""

    name: str
    pubs: tuple[PubPrediction, ...]
    shots: int
    overhead_seconds: float
    max_execution_seconds: float
    overhead_assumption: str
    minimum_shots: int = 1
    shot_granularity: int = 1


@dataclass(frozen=True)
class CovarianceBound:
    """Explicit PSD upper bound on one observable's same-shot score covariance.

    labels lists member/rN in observable term order and replica order. matrix
    bounds the covariance of the unsigned per-replica score variables in PSD
    order; the optimizer applies each term's sign and replica-average weight.
    The bound must include cross-member covariance when the PUB fuses members.
    assumption records the evidence or modeling assumption supporting the bound.

    variance_allowance adds to the weighted projection w' matrix w the radius
    reads: a plan adds the falsifier allowance its collection will add to the
    sample variance, and a collection whose variance upper confidence limit
    exceeds the projection adds the excess, so the radius takes that limit.
    falsifier_tail is the probability that limit misses the true variance; an
    endpoint that reads the bound spends it from its alpha, so its confidence
    and detection radii run at alpha minus the summed falsifier tails.
    """

    observable_name: str
    pub_name: str
    labels: tuple[str, ...]
    matrix: tuple[tuple[float, ...], ...]
    assumption: str
    variance_allowance: float = 0.0
    falsifier_tail: float = 0.0


@dataclass(frozen=True)
class EmpiricalBernsteinDesign:
    """Opt-in empirical-Bernstein confidence and detection radii for one endpoint.

    Each PUB's per-shot score Y is bounded by its span and i.i.d. over shots,
    the conditions Hoeffding's radius already requires. Maurer and Pontil
    (arXiv:0907.3740, Theorem 4, scaled from [0, 1] to span R) bound the
    one-sided deviation at tail d by
    sqrt(2 V_n ln(2 / d) / n) + 7 R ln(2 / d) / (3 (n - 1)), with V_n the
    sample variance (n - 1 denominator); the two-sided radius takes d / 2 per
    side, ln(4 / d). That radius reads the data, so it spends its own tail:
    share of the endpoint's confidence tail (alpha minus any covariance
    falsifier tails) goes to it and the rest to the Hoeffding radius and any
    declared covariance radius, and each PUB reads the smaller. The true mean
    leaves the smaller interval only when it leaves one of the two, so the
    union bound keeps coverage at alpha.

    Collection bounds sqrt(V_n(Y)) by sum_k |w_k| sqrt(V_n(s_k)) over the
    PUB's replica scores s_k, exact for one replica and valid for any
    within-shot dependence because the sample standard deviation is a norm.
    Planning, before data, raises each replica's modeled standard deviation
    by Maurer and Pontil's Theorem 10 (4) allowance
    R_k sqrt(2 ln(K / t) / (n - 1)), t = variance_tail over the PUBs, K the
    PUB's replica scores: the sample variance exceeds the planned value with
    probability at most variance_tail under the model. That event can only
    widen the collected radius, so the plan spends variance_tail from its
    power miss probability and coverage stays at alpha.
    """

    observable_name: str
    share: float = 0.5
    variance_tail: float = 1e-3


@dataclass(frozen=True)
class CandidatePlan:
    name: str
    jobs: tuple[JobCandidate, ...]
    covariance_bounds: tuple[CovarianceBound, ...] = ()
    proxy_metadata: dict[str, float | str] = field(default_factory=dict)
    empirical_bernstein: tuple[EmpiricalBernsteinDesign, ...] = ()


@dataclass(frozen=True)
class BudgetContract:
    remaining_seconds: float
    reserve_seconds: float
    max_total_execution_seconds: float


@dataclass(frozen=True)
class CostScenario:
    """Declared per-job overhead and per-stage latency sensitivity assumptions.

    Each scenario replaces both cost inputs together and applies to every job
    and PUB. The supplied scenarios carry no uncertainty-coverage guarantee.
    """

    name: str
    job_overhead_seconds: float
    classical_latency_us: float


@dataclass(frozen=True)
class PubCost:
    name: str
    shots: int
    scheduled_seconds: float
    repetition_delay_seconds: float
    reset_seconds: float
    classical_latency_seconds: float
    estimated_execution_seconds: float
    duration_assumption: str
    classical_stage_count: int | None = None


@dataclass(frozen=True)
class JobCost:
    name: str
    pubs: tuple[PubCost, ...]
    overhead_seconds: float
    estimated_charge_seconds: float
    max_execution_seconds: float
    overhead_assumption: str


@dataclass(frozen=True)
class CostScenarioResult:
    name: str
    feasible: bool
    estimated_charge_seconds: float
    jobs: tuple[JobCost, ...]
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ObservableResult:
    name: str
    predicted_value: float
    simulation_error_radius: float
    modeled_value_lower_bound: float
    modeled_value_upper_bound: float
    confidence_half_width: float
    detection_radius: float | None
    power_radius: float | None
    effect_used_for_power: float | None
    minimum_effect: float | None
    precision_half_width: float | None
    alpha: float
    power: float | None
    null_value: float
    bound_methods: tuple[str, ...]
    covariance_assumptions: tuple[str, ...]
    feasible: bool
    rejection_reasons: tuple[str, ...]


@dataclass(frozen=True)
class CandidateResult:
    name: str
    feasible: bool
    estimated_charge_seconds: float | None
    total_execution_ceiling_seconds: float | None
    jobs: tuple[JobCost, ...]
    observables: tuple[ObservableResult, ...]
    rejection_reasons: tuple[str, ...]
    proxy_metadata: dict[str, float | str]
    cost_scenarios: tuple[CostScenarioResult, ...] = ()
    worst_case_charge_seconds: float | None = None
    normalized_precision_radius: float | None = None


@dataclass(frozen=True)
class OptimizationResult:
    selected: str | None
    candidates: tuple[CandidateResult, ...]
    pareto_frontier: tuple[str, ...]
    rejection_reasons: tuple[str, ...]
    simulation_alpha: float
    simulation_comparisons: int
    assumptions: tuple[str, ...]
    objective: str = "minimum_charge"
    selected_objective_value: float | None = None
    cost_scenarios: tuple[CostScenario, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ObservedPub:
    """Measured replica marginals from one immutable PUB identity."""

    name: str
    member_distributions: dict[str, tuple[tuple[float, ...], ...]]
    shots: int


@dataclass(frozen=True)
class ObservationResult:
    name: str
    estimate: float
    lo: float
    hi: float
    confidence_half_width: float
    alpha: float
    null_value: float
    detection_radius: float | None
    reject_null: bool | None
    bound_methods: tuple[str, ...]


@dataclass(frozen=True)
class ObservationAnalysis:
    observables: tuple[ObservationResult, ...]
    method: str
    assumptions: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


EMPIRICAL_BERNSTEIN = {
    "source": (
        "A. Maurer and M. Pontil, Empirical Bernstein Bounds and Sample Variance Penalization, COLT 2009, "
        "arXiv:0907.3740v1, Theorem 4 (i.i.d. scores in [0, 1], n >= 2) and Theorem 10 (4)"
    ),
    "inequality": (
        "one-sided at tail d: mean - sample mean <= sqrt(2 V_n ln(2 / d) / n) + 7 R ln(2 / d) / (3 (n - 1)), "
        "V_n the sample variance with denominator n - 1 and R the per-shot score range; the two-sided radius "
        "takes d / 2 per side, ln(4 / d)"
    ),
    "alpha_split": (
        "each opted-in endpoint's confidence tail (alpha minus any covariance falsifier tails) splits equally: "
        "half to the data-free radius (Hoeffding, or the declared covariance radius where smaller), half to "
        "the empirical-Bernstein radius; each PUB reads the smaller, and the union bound over the two methods "
        "and over PUBs keeps coverage at alpha"
    ),
    "collection_variance": (
        "each PUB score Y = sum_k w_k s_k reads V_n(Y) <= n / (n - 1) (sum_k |w_k| sigma_k)^2 with sigma_k the "
        "plug-in standard deviation of replica score s_k from its outcome frequencies: exact for one replica, "
        "valid for any within-shot dependence"
    ),
    "planning_variance": (
        "each modeled replica standard deviation rises by Theorem 10 (4)'s allowance "
        "R_k sqrt(2 ln(K / t) / (n - 1)) at t = variance tail / PUBs, K replica scores per PUB; the plan "
        "spends the variance tail from its power miss probability, so a variance above plan costs power and "
        "never coverage"
    ),
    "scope": (
        "endpoints whose per-shot scores are bounded and i.i.d. over shots within a PUB, the conditions the "
        "Hoeffding radius already requires; power radii stay data-free"
    ),
}

ASSUMPTIONS = (
    "independent stationary repetitions; arbitrary dependence within each PUB shot unless explicitly bounded",
    "union bounds across PUBs; no independence assumption between PUBs",
    "observable alpha and power are per endpoint, conditional on the supplied outcome model",
    "finite simulation error is controlled simultaneously across all supplied candidate-observable marginals",
    "hardware-model discrepancy and cost-model error remain unquantified",
    "charge estimates include every PUB, control, repetition delay, declared duration addition, and job overhead",
    "execution ceilings apply per job; their aggregate must preserve the declared reserve",
    "explicit cost scenarios are sensitivity assumptions; their coverage of cost uncertainty is unquantified",
)


def _finite(value: float) -> bool:
    return not isinstance(value, bool) and math.isfinite(value)


def _positive_integer(value: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _validate_observable_contracts(contracts: tuple[ObservableContract, ...]) -> None:
    _require(bool(contracts), "at least one observable contract is required")
    _require(len({contract.name for contract in contracts}) == len(contracts), "observable names must be unique")
    for contract in contracts:
        _require(bool(contract.name.strip()) and bool(contract.terms), "each observable needs a name and terms")
        _require(_finite(contract.null_value), f"{contract.name}: null value must be finite")
        _require(_finite(contract.alpha) and 0 < contract.alpha < 1, f"{contract.name}: alpha must lie in (0, 1)")
        _require(_finite(contract.power) and 0 < contract.power < 1, f"{contract.name}: power must lie in (0, 1)")
        _require(
            contract.minimum_effect is not None or contract.precision_half_width is not None,
            f"{contract.name}: specify minimum_effect or precision_half_width",
        )
        _require(
            contract.minimum_effect is None or (_finite(contract.minimum_effect) and contract.minimum_effect >= 0),
            f"{contract.name}: minimum_effect must be finite and nonnegative",
        )
        _require(
            contract.precision_half_width is None
            or (_finite(contract.precision_half_width) and contract.precision_half_width > 0),
            f"{contract.name}: precision_half_width must be finite and positive",
        )
        members = [term.member for term in contract.terms]
        _require(len(set(members)) == len(members), f"{contract.name}: each member may occur once")
        for term in contract.terms:
            _require(bool(term.member.strip()), f"{contract.name}: member name is required")
            _require(type(term.sign) is int and term.sign in (-1, 1), f"{contract.name}: term sign must be -1 or +1")
            _require(
                bool(term.values) and all(_finite(value) and -1 <= value <= 1 for value in term.values),
                f"{contract.name}/{term.member}: score values must be finite and lie in [-1, 1]",
            )


def _validate_contracts(contracts: tuple[ObservableContract, ...], budget: BudgetContract) -> None:
    _validate_observable_contracts(contracts)
    for label, value in asdict(budget).items():
        _require(_finite(value) and value >= 0, f"budget {label} must be finite and nonnegative")
    _require(budget.max_total_execution_seconds > 0, "aggregate execution ceiling must be positive")
    _require(budget.reserve_seconds <= budget.remaining_seconds, "budget reserve exceeds remaining seconds")


def _validate_cost_scenarios(scenarios: tuple[CostScenario, ...]) -> None:
    _require(len({scenario.name for scenario in scenarios}) == len(scenarios), "cost scenario names must be unique")
    for scenario in scenarios:
        _require(
            bool(scenario.name.strip()) and scenario.name != "nominal",
            "each cost scenario needs a name distinct from nominal",
        )
        for label, value in (
            ("job_overhead_seconds", scenario.job_overhead_seconds),
            ("classical_latency_us", scenario.classical_latency_us),
        ):
            _require(_finite(value) and value >= 0, f"{scenario.name}: {label} must be finite and nonnegative")


def _validate_plan(plan: CandidatePlan, contracts: tuple[ObservableContract, ...]) -> None:
    _require(bool(plan.name.strip()) and bool(plan.jobs), "each candidate needs a name and jobs")
    _require(len({job.name for job in plan.jobs}) == len(plan.jobs), f"{plan.name}: job names must be unique")
    pub_names: set[str] = set()
    member_names: set[str] = set()
    for job in plan.jobs:
        _require(bool(job.name.strip()) and bool(job.pubs), f"{plan.name}: each job needs a name and PUBs")
        _require(_positive_integer(job.shots), f"{job.name}: shots must be a positive integer")
        _require(_positive_integer(job.minimum_shots), f"{job.name}: minimum_shots must be a positive integer")
        _require(_positive_integer(job.shot_granularity), f"{job.name}: shot_granularity must be a positive integer")
        _require(job.shots >= job.minimum_shots, f"{job.name}: shots are below the required minimum")
        _require(job.shots % job.shot_granularity == 0, f"{job.name}: shots violate the declared granularity")
        _require(
            _finite(job.overhead_seconds) and job.overhead_seconds >= 0,
            f"{job.name}: overhead must be finite and nonnegative",
        )
        _require(
            _finite(job.max_execution_seconds) and job.max_execution_seconds > 0,
            f"{job.name}: execution ceiling must be finite and positive",
        )
        _require(bool(job.overhead_assumption.strip()), f"{job.name}: overhead assumption is required")
        for pub in job.pubs:
            _require(bool(pub.name.strip()) and pub.name not in pub_names, f"{job.name}: PUB names must be unique")
            pub_names.add(pub.name)
            _require(bool(pub.member_distributions), f"{pub.name}: member predictions are required")
            _require(bool(pub.duration_assumption.strip()), f"{pub.name}: duration assumption is required")
            _require(
                pub.simulation_shots is None or _positive_integer(pub.simulation_shots),
                f"{pub.name}: simulation_shots must be positive or None for exact probabilities",
            )
            _require(
                pub.classical_stage_count is None
                or (type(pub.classical_stage_count) is int and pub.classical_stage_count >= 0),
                f"{pub.name}: classical_stage_count must be a nonnegative integer or None",
            )
            for label, value in (
                ("scheduled_seconds", pub.scheduled_seconds),
                ("repetition_delay_seconds", pub.repetition_delay_seconds),
                ("reset_seconds", pub.reset_seconds),
                ("classical_latency_seconds", pub.classical_latency_seconds),
            ):
                _require(_finite(value) and value >= 0, f"{pub.name}: {label} must be finite and nonnegative")
            _require(_repetition_seconds(pub) > 0, f"{pub.name}: total repetition duration must be positive")
            for member, replicas in pub.member_distributions.items():
                _require(bool(member.strip()) and member not in member_names, f"{member}: member names must be unique")
                member_names.add(member)
                _require(bool(replicas), f"{member}: at least one replica prediction is required")
                for distribution in replicas:
                    _require(
                        bool(distribution)
                        and all(_finite(value) and 0 <= value <= 1 for value in distribution)
                        and math.isclose(math.fsum(distribution), 1.0, rel_tol=0.0, abs_tol=1e-9),
                        f"{member}: every distribution must be finite, nonnegative, and normalized",
                    )
    for contract in contracts:
        for term in contract.terms:
            _require(term.member in member_names, f"{contract.name}: member {term.member!r} is absent")
    keys = [(bound.observable_name, bound.pub_name) for bound in plan.covariance_bounds]
    _require(len(set(keys)) == len(keys), f"{plan.name}: covariance bounds must have unique observable/PUB keys")
    for bound in plan.covariance_bounds:
        _require(
            bound.observable_name in {contract.name for contract in contracts} and bound.pub_name in pub_names,
            f"{plan.name}: covariance bound names an unknown observable or PUB",
        )
    _validate_bernstein(plan.empirical_bernstein, contracts)


def _validate_bernstein(
    designs: tuple[EmpiricalBernsteinDesign, ...], contracts: tuple[ObservableContract, ...]
) -> None:
    names = [design.observable_name for design in designs]
    _require(len(set(names)) == len(names), "empirical-Bernstein designs must name distinct observables")
    powers = {contract.name: contract.power for contract in contracts}
    for design in designs:
        _require(
            design.observable_name in powers, f"{design.observable_name}: empirical-Bernstein design names no contract"
        )
        _require(
            _finite(design.share) and 0 < design.share < 1,
            f"{design.observable_name}: empirical-Bernstein share must lie in (0, 1)",
        )
        _require(
            _finite(design.variance_tail) and 0 < design.variance_tail < 1 - powers[design.observable_name],
            f"{design.observable_name}: variance tail must lie in (0, 1 - power)",
        )


def _repetition_seconds(pub: PubPrediction) -> float:
    return math.fsum(
        (pub.scheduled_seconds, pub.repetition_delay_seconds, pub.reset_seconds, pub.classical_latency_seconds)
    )


def _costs(plan: CandidatePlan, budget: BudgetContract) -> tuple[tuple[JobCost, ...], list[str]]:
    jobs: list[JobCost] = []
    reasons: list[str] = []
    for job in plan.jobs:
        pubs = tuple(
            PubCost(
                pub.name,
                job.shots,
                pub.scheduled_seconds,
                pub.repetition_delay_seconds,
                pub.reset_seconds,
                pub.classical_latency_seconds,
                job.shots * _repetition_seconds(pub),
                pub.duration_assumption,
                pub.classical_stage_count,
            )
            for pub in job.pubs
        )
        charge = math.fsum([job.overhead_seconds, *(pub.estimated_execution_seconds for pub in pubs)])
        _require(math.isfinite(charge), f"{job.name}: estimated charge overflowed")
        jobs.append(
            JobCost(job.name, pubs, job.overhead_seconds, charge, job.max_execution_seconds, job.overhead_assumption)
        )
        if charge > job.max_execution_seconds:
            reasons.append(f"{job.name}: estimated charge exceeds the per-job execution ceiling")
    ceiling = math.fsum(job.max_execution_seconds for job in plan.jobs)
    _require(math.isfinite(ceiling), f"{plan.name}: aggregate execution ceiling overflowed")
    if ceiling > budget.max_total_execution_seconds:
        reasons.append("aggregate per-job ceilings exceed max_total_execution_seconds")
    if ceiling > budget.remaining_seconds - budget.reserve_seconds:
        reasons.append("aggregate per-job ceilings consume the declared budget reserve")
    return tuple(jobs), reasons


def _scenario_costs(plan: CandidatePlan, budget: BudgetContract, scenario: CostScenario) -> CostScenarioResult:
    jobs = []
    for job in plan.jobs:
        pubs = []
        for pub in job.pubs:
            stage_count = pub.classical_stage_count
            if stage_count is None:
                raise ValueError(
                    f"{scenario.name}/{pub.name}: cost scenarios require an explicit classical_stage_count"
                )
            latency = stage_count * scenario.classical_latency_us * 1e-6
            _require(math.isfinite(latency), f"{scenario.name}/{pub.name}: classical latency overflowed")
            _require(
                math.fsum((pub.scheduled_seconds, pub.repetition_delay_seconds, pub.reset_seconds, latency)) > 0,
                f"{scenario.name}/{pub.name}: total repetition duration must be positive",
            )
            pubs.append(
                replace(
                    pub,
                    classical_latency_seconds=latency,
                    duration_assumption=(
                        f"{pub.duration_assumption}; scenario {scenario.name} replaces added classical latency "
                        f"with {stage_count} stages at {scenario.classical_latency_us} us per stage"
                    ),
                )
            )
        jobs.append(
            replace(
                job,
                pubs=tuple(pubs),
                overhead_seconds=scenario.job_overhead_seconds,
                overhead_assumption=f"declared sensitivity scenario {scenario.name}; uncertainty coverage unquantified",
            )
        )
    costs, reasons = _costs(replace(plan, jobs=tuple(jobs)), budget)
    charge = math.fsum(job.estimated_charge_seconds for job in costs)
    _require(math.isfinite(charge), f"{scenario.name}: aggregate estimated charge overflowed")
    return CostScenarioResult(scenario.name, not reasons, charge, costs, tuple(reasons))


@dataclass(frozen=True)
class _PubObservable:
    name: str
    shots: int
    span: float
    variance_bound: float | None
    covariance_assumption: str | None
    falsifier_tail: float = 0.0
    # The variance the empirical-Bernstein radius reads (the sample variance's
    # Minkowski bound at collection, its planned upper limit before data) and
    # the share of the tail that radius spends; zero share leaves it unused.
    sample_variance: float | None = None
    bernstein_share: float = 0.0


def _covariance_variance(bound: CovarianceBound, labels: list[str], weights: list[float]) -> float:
    _require(tuple(labels) == bound.labels, f"{bound.pub_name}: covariance labels differ from the observable vector")
    _require(bool(bound.assumption.strip()), f"{bound.pub_name}: covariance assumption is required")
    size = len(labels)
    _require(
        len(bound.matrix) == size
        and all(len(row) == size and all(_finite(value) for value in row) for row in bound.matrix),
        f"{bound.pub_name}: covariance bound must be a finite square matrix",
    )
    matrix = np.asarray(bound.matrix, dtype=float)
    _require(
        np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-12), f"{bound.pub_name}: covariance bound must be symmetric"
    )
    matrix = (matrix + matrix.T) / 2
    _require(float(np.linalg.eigvalsh(matrix).min()) >= 0, f"{bound.pub_name}: covariance bound must be PSD")
    _require(
        _finite(bound.variance_allowance) and bound.variance_allowance >= 0,
        f"{bound.pub_name}: variance allowance must be finite and nonnegative",
    )
    _require(
        _finite(bound.falsifier_tail) and 0 <= bound.falsifier_tail < 1,
        f"{bound.pub_name}: falsifier tail must lie in [0, 1)",
    )
    vector = np.asarray(weights, dtype=float)
    variance_bound = float(vector @ matrix @ vector) + bound.variance_allowance
    _require(math.isfinite(variance_bound), f"{bound.pub_name}: covariance projection overflowed")
    _require(variance_bound >= 0, f"{bound.pub_name}: covariance projection must be nonnegative")
    return variance_bound


def _observable_inputs(
    pubs: tuple[ObservedPub, ...],
    contract: ObservableContract,
    simulation_tail: float,
    covariance_bounds: tuple[CovarianceBound, ...] = (),
    simulation_shots: dict[str, int | None] | None = None,
    bernstein: EmpiricalBernsteinDesign | None = None,
    planning: bool = False,
) -> tuple[float, float, tuple[_PubObservable, ...]]:
    """The endpoint's predicted or observed value, simulation allowance and per-PUB score streams.

    With a bernstein design each stream also carries the variance its
    empirical-Bernstein radius reads: from the supplied distributions as
    observed frequencies at collection, or as the modeled law raised to its
    planned upper limit when planning.
    """
    covariance = {(bound.observable_name, bound.pub_name): bound for bound in covariance_bounds}
    predictions: list[float] = []
    simulation_errors: list[float] = []
    streams: list[_PubObservable] = []
    deviations: list[tuple[float, int]] = []
    for pub in pubs:
        labels: list[str] = []
        weights: list[float] = []
        spans: list[float] = []
        deviation = 0.0
        scored = 0
        samples = (simulation_shots or {}).get(pub.name)
        for term in contract.terms:
            replicas = pub.member_distributions.get(term.member)
            if replicas is None:
                continue
            weight = term.sign / len(replicas)
            span = max(term.values) - min(term.values)
            for replica_index, distribution in enumerate(replicas):
                _require(
                    len(distribution) == len(term.values),
                    f"{contract.name}/{term.member}: score and distribution dimensions differ",
                )
                mean = math.fsum(p * value for p, value in zip(distribution, term.values, strict=True))
                predictions.append(weight * mean)
                if bernstein is not None and span:
                    spread = math.fsum(
                        p * (value - mean) ** 2 for p, value in zip(distribution, term.values, strict=True)
                    )
                    deviation += abs(weight) * math.sqrt(max(spread, 0.0))
                    scored += 1
                labels.append(f"{term.member}/r{replica_index}")
                weights.append(weight)
                spans.append(abs(weight) * span)
                if samples is not None and span:
                    radius = span * math.sqrt(math.log(2.0 / simulation_tail) / (2 * samples))
                    simulation_errors.append(abs(weight) * min(radius, span))
        if labels:
            bound = covariance.get((contract.name, pub.name))
            variance_bound = _covariance_variance(bound, labels, weights) if bound is not None else None
            streams.append(
                _PubObservable(
                    pub.name,
                    pub.shots,
                    math.fsum(spans),
                    variance_bound,
                    bound.assumption if bound is not None else None,
                    bound.falsifier_tail if bound is not None else 0.0,
                )
            )
            deviations.append((deviation, scored))
        else:
            _require(
                (contract.name, pub.name) not in covariance,
                f"{contract.name}/{pub.name}: covariance bound has no observable terms",
            )
    if bernstein is not None:
        streams = _bernstein_streams(streams, deviations, bernstein, planning)
    return math.fsum(predictions), math.fsum(simulation_errors), tuple(streams)


def empirical_bernstein_radius(variance: float, span: float, shots: int, tail: float, two_sided: bool) -> float:
    """Maurer-Pontil Theorem 4 radius of the mean of shots scores of range span and sample variance variance.

    One-sided: sqrt(2 V_n ln(2 / tail) / n) + 7 span ln(2 / tail) / (3 (n - 1)); the
    two-sided radius spends tail / 2 per side. The score range clips it, and
    fewer than two shots leave only the range.
    """
    if shots < 2:
        return span
    log = math.log((4.0 if two_sided else 2.0) / tail)
    return min(math.sqrt(2 * variance * log / shots) + 7 * span * log / (3 * (shots - 1)), span)


def sample_deviation_allowance(span: float, shots: int, tail: float) -> float:
    """Maurer-Pontil Theorem 10 (4) scaled to range span: sqrt(V_n) exceeds sqrt(E V_n) by more w.p. at most tail."""
    return span * math.sqrt(2 * math.log(1.0 / tail) / (shots - 1))


def _bernstein_streams(
    streams: list[_PubObservable],
    deviations: list[tuple[float, int]],
    design: EmpiricalBernsteinDesign,
    planning: bool,
) -> list[_PubObservable]:
    """Attach each stream's empirical-Bernstein variance and tail share.

    deviations holds sum_k |w_k| sigma_k of the stream's replica scores under
    the supplied laws and the count K of scored replica scores. Collection
    reads n / (n - 1) times its square, the Minkowski bound on the PUB score's
    sample variance. Planning adds Theorem 10 (4)'s allowance to every
    sigma_k at tail variance_tail / (PUBs x K), whose weighted sum is the
    stream span times the allowance factor. The bound on any sample variance,
    n / (n - 1) x span^2 / 4, caps both.
    """
    active = sum(1 for stream in streams if stream.span > 0)
    attached = []
    for stream, (deviation, scored) in zip(streams, deviations, strict=True):
        variance = None
        if stream.span > 0 and stream.shots >= 2:
            inflation = stream.shots / (stream.shots - 1)
            if planning:
                tail = design.variance_tail / (active * max(scored, 1))
                deviation += sample_deviation_allowance(stream.span, stream.shots, tail)
                variance = deviation * deviation
            else:
                variance = inflation * deviation * deviation
            variance = min(variance, inflation * stream.span * stream.span / 4)
            _require(math.isfinite(variance), f"{stream.name}: empirical-Bernstein variance overflowed")
        attached.append(replace(stream, sample_variance=variance, bernstein_share=design.share))
    return attached


def _confidence_tail(contract: ObservableContract, streams: tuple[_PubObservable, ...]) -> float:
    """The endpoint's alpha after the falsifier tails of the covariance bounds its streams read."""
    remaining = contract.alpha - math.fsum(stream.falsifier_tail for stream in streams)
    _require(remaining > 0, f"{contract.name}: covariance falsifier tails exhaust alpha")
    return remaining


def _stream_radii(stream: _PubObservable, tail: float, two_sided: bool, empirical: bool) -> tuple[float, float | None]:
    """One PUB's data-free radius (Hoeffding, or the declared covariance radius where smaller) and its
    empirical-Bernstein radius, each at its share of tail; None where the stream reads no empirical radius."""
    variance = stream.sample_variance if empirical else None
    share = stream.bernstein_share if variance is not None else 0.0
    fixed_tail = tail * (1.0 - share)
    hoeffding = stream.span * math.sqrt(math.log((2.0 if two_sided else 1.0) / fixed_tail) / (2 * stream.shots))
    radius = min(hoeffding, stream.span)
    if stream.variance_bound is not None:
        multiplier = 1.0 / fixed_tail if two_sided else (1.0 - fixed_tail) / fixed_tail
        covariance_radius = math.sqrt(stream.variance_bound / stream.shots * multiplier)
        radius = min(radius, covariance_radius)
    if variance is None or not share:
        return radius, None
    return radius, empirical_bernstein_radius(variance, stream.span, stream.shots, tail * share, two_sided)


def _bernstein_detail(
    contract: ObservableContract,
    streams: tuple[_PubObservable, ...],
    design: EmpiricalBernsteinDesign,
    planning: bool,
) -> dict[str, Any]:
    """Every radius an opted-in endpoint composes: per PUB, both methods at their tails and the one it reads."""
    alpha = _confidence_tail(contract, streams)
    active = [stream for stream in streams if stream.span > 0]
    kinds = [("confidence", True)] + ([("detection", False)] if contract.minimum_effect is not None else [])
    pubs: list[dict[str, Any]] = []
    totals: dict[str, dict[str, float]] = {}
    for stream in active:
        row: dict[str, Any] = {
            "pub": stream.name,
            "shots": stream.shots,
            "score_span": stream.span,
            "variance": stream.sample_variance,
        }
        for kind, two_sided in kinds:
            fixed, bernstein = _stream_radii(stream, alpha / len(active), two_sided, True)
            used = fixed if bernstein is None else min(fixed, bernstein)
            row[kind] = {
                "data_free": fixed,
                "empirical_bernstein": bernstein,
                "used": used,
                "method": "empirical_bernstein" if bernstein is not None and bernstein < fixed else "data_free",
            }
            total = totals.setdefault(kind, {"data_free": 0.0, "empirical_bernstein": 0.0, "used": 0.0})
            total["data_free"] += fixed
            total["empirical_bernstein"] += stream.span if bernstein is None else bernstein
            total["used"] += used
        pubs.append(row)
    for kind, two_sided in kinds:
        totals.setdefault(kind, {"data_free": 0.0, "empirical_bernstein": 0.0, "used": 0.0})
        totals[kind]["without_empirical_bernstein"] = _radius(streams, alpha, two_sided)
    detail: dict[str, Any] = {
        "observable": contract.name,
        "alpha": contract.alpha,
        "falsifier_tail": contract.alpha - alpha,
        "confidence_tail": alpha,
        "share": design.share,
        "data_free_tail": alpha * (1 - design.share),
        "empirical_bernstein_tail": alpha * design.share,
        "variance": (
            "planned upper limit: modeled replica standard deviations, each raised by the Theorem 10 (4) "
            f"allowance at total tail {design.variance_tail}"
            if planning
            else "observed: n / (n - 1) (sum_k |w_k| sigma_k)^2 over the PUB's replica score frequencies"
        ),
        "pubs": pubs,
        "radii": totals,
    }
    if contract.minimum_effect is not None:
        detail |= {
            "variance_tail": design.variance_tail,
            "power_tail": _power_tail(contract, design),
            "power_radius": _radius(streams, _power_tail(contract, design), two_sided=False),
            "power_radius_without_empirical_bernstein": _radius(streams, 1 - contract.power, two_sided=False),
        }
    return detail


def planned_empirical_bernstein(plan: CandidatePlan, contracts: tuple[ObservableContract, ...]) -> list[dict[str, Any]]:
    """_bernstein_detail of every opted-in endpoint at the plan's shots and planned variances."""
    _validate_plan(plan, contracts)
    pubs = tuple(ObservedPub(pub.name, pub.member_distributions, job.shots) for job in plan.jobs for pub in job.pubs)
    details = []
    for contract in contracts:
        design = _design(plan.empirical_bernstein, contract)
        if design is None:
            continue
        _, _, streams = _observable_inputs(pubs, contract, 1.0, plan.covariance_bounds, None, design, planning=True)
        details.append(_bernstein_detail(contract, streams, design, planning=True))
    return details


def observed_empirical_bernstein(
    pubs: tuple[ObservedPub, ...],
    contracts: tuple[ObservableContract, ...],
    covariance_bounds: tuple[CovarianceBound, ...],
    designs: tuple[EmpiricalBernsteinDesign, ...],
) -> list[dict[str, Any]]:
    """_bernstein_detail of every opted-in endpoint at the observed shots and sample variances."""
    _validate_observable_contracts(contracts)
    _validate_bernstein(designs, contracts)
    details = []
    for contract in contracts:
        design = _design(designs, contract)
        if design is None:
            continue
        _, _, streams = _observable_inputs(pubs, contract, 1.0, covariance_bounds, None, design)
        details.append(_bernstein_detail(contract, streams, design, planning=False))
    return details


def _radius(streams: tuple[_PubObservable, ...], probability: float, two_sided: bool, empirical: bool = False) -> float:
    """Union-bound radius over the PUB streams at total tail probability.

    empirical marks a confidence or detection radius, which the collected
    data set and which may read a stream's empirical-Bernstein radius; a
    power radius describes the alternative's lower tail and reads the
    data-free radius only.
    """
    active = [stream for stream in streams if stream.span > 0]
    if not active:
        return 0.0
    tail = probability / len(active)
    if tail == 0:
        # The total score range remains valid when a subnormal probability
        # underflows during the union-bound allocation.
        return math.fsum(stream.span for stream in active)
    radii: list[float] = []
    for stream in active:
        radius, bernstein = _stream_radii(stream, tail, two_sided, empirical)
        radii.append(radius if bernstein is None else min(radius, bernstein))
    return math.fsum(radii)


def _power_tail(contract: ObservableContract, design: EmpiricalBernsteinDesign | None) -> float:
    """The power radius's tail: the miss probability less the planned sample-variance excursion it covers."""
    return 1 - contract.power - (design.variance_tail if design is not None else 0.0)


def _bound_methods(streams: tuple[_PubObservable, ...]) -> tuple[str, ...]:
    methods = []
    for stream in streams:
        method = (
            "hoeffding_arbitrary_within_shot"
            if stream.variance_bound is None
            else "minimum_of_hoeffding_and_declared_covariance_cantelli_or_chebyshev"
        )
        if stream.bernstein_share:
            method = (
                "minimum_of_hoeffding_and_empirical_bernstein_split_alpha"
                if stream.variance_bound is None
                else "minimum_of_hoeffding_declared_covariance_and_empirical_bernstein_split_alpha"
            )
        methods.append(method)
    return tuple(methods)


def _evaluate_observable(plan: CandidatePlan, contract: ObservableContract, simulation_tail: float) -> ObservableResult:
    pubs = tuple(ObservedPub(pub.name, pub.member_distributions, job.shots) for job in plan.jobs for pub in job.pubs)
    samples = {pub.name: pub.simulation_shots for job in plan.jobs for pub in job.pubs}
    design = _design(plan.empirical_bernstein, contract)
    predicted, model_radius, streams = _observable_inputs(
        pubs, contract, simulation_tail, plan.covariance_bounds, samples, design, planning=True
    )
    alpha = _confidence_tail(contract, streams)
    confidence = _radius(streams, alpha, two_sided=True, empirical=True)
    reasons: list[str] = []
    detection = power = effect_used = None
    if contract.minimum_effect is not None:
        detection = _radius(streams, alpha, two_sided=False, empirical=True)
        power = _radius(streams, _power_tail(contract, design), two_sided=False)
        modeled_gap = predicted - model_radius - contract.null_value
        effect_used = modeled_gap if contract.minimum_effect == 0 else contract.minimum_effect
        if modeled_gap <= 0 or modeled_gap < contract.minimum_effect:
            reasons.append("model contrast after simultaneous simulation allowance is below the minimum effect")
        if detection + power > effect_used:
            reasons.append("shot tier cannot detect the reported alternative effect at the declared alpha and power")
    if contract.precision_half_width is not None and confidence > contract.precision_half_width:
        reasons.append("shot tier exceeds the declared confidence half-width")
    return ObservableResult(
        contract.name,
        predicted,
        model_radius,
        predicted - model_radius,
        predicted + model_radius,
        confidence,
        detection,
        power,
        effect_used,
        contract.minimum_effect,
        contract.precision_half_width,
        contract.alpha,
        contract.power if contract.minimum_effect is not None else None,
        contract.null_value,
        _bound_methods(streams),
        tuple(stream.covariance_assumption for stream in streams if stream.covariance_assumption is not None),
        not reasons,
        tuple(reasons),
    )


def _design(
    designs: tuple[EmpiricalBernsteinDesign, ...], contract: ObservableContract
) -> EmpiricalBernsteinDesign | None:
    return next((design for design in designs if design.observable_name == contract.name), None)


def analyze_observations(
    pubs: tuple[ObservedPub, ...],
    contracts: tuple[ObservableContract, ...],
    covariance_bounds: tuple[CovarianceBound, ...] = (),
    empirical_bernstein: tuple[EmpiricalBernsteinDesign, ...] = (),
) -> ObservationAnalysis:
    """Apply the planner's grouped bounds and directional test to measured data.

    No cost or model-prediction fields are needed. The two-sided confidence
    interval describes precision; reject_null applies the same one-sided alpha
    threshold used by the planner's power contract. Dependence within a PUB shot
    remains arbitrary unless the plan declared a covariance bound for that
    observable and PUB; the collector then applies the same bound the planner
    did. An endpoint the plan opted into empirical_bernstein takes, per PUB,
    the smaller of that radius and the Hoeffding radius at their alpha split,
    with the variance read from the observed frequencies. Invalid identities
    or marginal distributions raise ValueError so a collector can withhold the
    analysis explicitly.
    """
    _validate_observable_contracts(contracts)
    _validate_bernstein(empirical_bernstein, contracts)
    _require(bool(pubs), "at least one observed PUB is required")
    _require(len({pub.name for pub in pubs}) == len(pubs), "observed PUB names must be unique")
    members: set[str] = set()
    for pub in pubs:
        _require(bool(pub.name.strip()), "observed PUB name is required")
        _require(_positive_integer(pub.shots), f"{pub.name}: observed shots must be a positive integer")
        _require(bool(pub.member_distributions), f"{pub.name}: observed members are required")
        for member, replicas in pub.member_distributions.items():
            _require(bool(member.strip()) and member not in members, "observed member identities must be unique")
            members.add(member)
            _require(bool(replicas), f"{member}: at least one measured replica is required")
            for distribution in replicas:
                _require(
                    bool(distribution)
                    and all(_finite(value) and 0 <= value <= 1 for value in distribution)
                    and math.isclose(math.fsum(distribution), 1.0, rel_tol=0.0, abs_tol=1e-9),
                    f"{member}: observed distributions must be finite, nonnegative, and normalized",
                )
    rows: list[ObservationResult] = []
    for contract in contracts:
        for term in contract.terms:
            _require(term.member in members, f"{contract.name}: observed member {term.member!r} is absent")
        estimate, _, streams = _observable_inputs(
            pubs, contract, 1.0, covariance_bounds, None, _design(empirical_bernstein, contract)
        )
        alpha = _confidence_tail(contract, streams)
        confidence = _radius(streams, alpha, two_sided=True, empirical=True)
        detection = (
            _radius(streams, alpha, two_sided=False, empirical=True) if contract.minimum_effect is not None else None
        )
        rows.append(
            ObservationResult(
                contract.name,
                estimate,
                estimate - confidence,
                estimate + confidence,
                confidence,
                contract.alpha,
                contract.null_value,
                detection,
                estimate - detection > contract.null_value if detection is not None else None,
                _bound_methods(streams),
            )
        )
    return ObservationAnalysis(
        tuple(rows),
        "shared planning/collection Hoeffding bounds grouped by immutable PUB identity"
        + ("; declared covariance bounds where the plan carried them" if covariance_bounds else "")
        + ("; empirical-Bernstein radii at their alpha split where the plan opted in" if empirical_bernstein else ""),
        (
            "independent stationary repetitions; arbitrary dependence among replicas and members within each PUB shot"
            + (" unless a declared covariance bound applies" if covariance_bounds else ""),
            "union bounds across PUBs; no independence assumption between PUBs or jobs",
            "directional rejection uses the one-sided alpha radius; displayed intervals use the two-sided alpha radius",
            *sorted({bound.assumption for bound in covariance_bounds}),
            *(
                (
                    "empirical-Bernstein radii (Maurer-Pontil Theorem 4) read each PUB score's sample variance "
                    "through the Minkowski bound over its replica scores and spend their share of alpha",
                )
                if empirical_bernstein
                else ()
            ),
        ),
    )


def observation_power_radii(
    pubs: tuple[ObservedPub, ...],
    contracts: tuple[ObservableContract, ...],
    covariance_bounds: tuple[CovarianceBound, ...] = (),
    empirical_bernstein: tuple[EmpiricalBernsteinDesign, ...] = (),
) -> dict[str, float]:
    """The planner's one-sided power radius at tail 1 - power for each directional contract, at the observed shots.

    Detection plus this radius covering the planned effect is the power
    condition evaluate_candidate admits; collection reports it for the bound
    family its analysis applied.
    """
    _validate_observable_contracts(contracts)
    _validate_bernstein(empirical_bernstein, contracts)
    radii: dict[str, float] = {}
    for contract in contracts:
        if contract.minimum_effect is None:
            continue
        _, _, streams = _observable_inputs(pubs, contract, 1.0, covariance_bounds)
        radii[contract.name] = _radius(
            streams, _power_tail(contract, _design(empirical_bernstein, contract)), two_sided=False
        )
    return radii


def _simulation_comparisons(plans: tuple[CandidatePlan, ...], contracts: tuple[ObservableContract, ...]) -> int:
    return sum(
        len(pub.member_distributions.get(term.member, ()))
        for plan in plans
        for job in plan.jobs
        for pub in job.pubs
        if pub.simulation_shots is not None
        for contract in contracts
        for term in contract.terms
        if max(term.values) > min(term.values)
    )


def evaluate_candidate(
    plan: CandidatePlan,
    contracts: tuple[ObservableContract, ...],
    budget: BudgetContract,
    *,
    simulation_alpha: float = 0.01,
    simulation_comparisons: int | None = None,
    cost_scenarios: tuple[CostScenario, ...] = (),
) -> CandidateResult:
    """Evaluate one plan; malformed or infeasible plans produce diagnostic results.

    optimize supplies the search-wide comparison count. Calling this function
    alone bounds the simulation error for the single plan only.
    """
    jobs: tuple[JobCost, ...] = ()
    observables: tuple[ObservableResult, ...] = ()
    scenario_results: tuple[CostScenarioResult, ...] = ()
    estimated_charge = ceiling = worst_charge = normalized_radius = None
    try:
        _validate_contracts(contracts, budget)
        _validate_cost_scenarios(cost_scenarios)
        _validate_plan(plan, contracts)
        _require(_finite(simulation_alpha) and 0 < simulation_alpha < 1, "simulation_alpha must lie in (0, 1)")
        own_comparisons = _simulation_comparisons((plan,), contracts)
        comparisons = own_comparisons if simulation_comparisons is None else simulation_comparisons
        _require(
            type(comparisons) is int and comparisons >= own_comparisons,
            "simulation_comparisons must cover every scored finite-shot marginal",
        )
        jobs, reasons = _costs(plan, budget)
        estimated_charge = math.fsum(job.estimated_charge_seconds for job in jobs)
        ceiling = math.fsum(job.max_execution_seconds for job in jobs)
        _require(math.isfinite(estimated_charge), f"{plan.name}: aggregate estimated charge overflowed")
        scenario_results = tuple(
            _scenario_costs(plan, budget, scenario) for scenario in sorted(cost_scenarios, key=lambda item: item.name)
        )
        worst_charge = max([estimated_charge, *(scenario.estimated_charge_seconds for scenario in scenario_results)])
        reasons.extend(
            f"cost scenario {scenario.name}: {reason}"
            for scenario in scenario_results
            for reason in scenario.rejection_reasons
        )
        simulation_tail = simulation_alpha / max(comparisons, 1)
        _require(simulation_tail > 0, "simulation probability underflows at the supplied comparison count")
        observables = tuple(_evaluate_observable(plan, contract, simulation_tail) for contract in contracts)
        reasons.extend(f"{result.name}: {reason}" for result in observables for reason in result.rejection_reasons)
        precision_ratios = [
            result.confidence_half_width / result.precision_half_width
            for result in observables
            if result.precision_half_width is not None
        ]
        if len(precision_ratios) == len(observables):
            _require(all(math.isfinite(ratio) for ratio in precision_ratios), "normalized precision radius overflowed")
            normalized_radius = max(precision_ratios)
    except (ValueError, OverflowError, np.linalg.LinAlgError) as error:
        reasons = [str(error)]
    return CandidateResult(
        plan.name,
        not reasons,
        estimated_charge,
        ceiling,
        jobs,
        observables,
        tuple(reasons),
        dict(plan.proxy_metadata),
        scenario_results,
        worst_charge,
        normalized_radius,
    )


def _dominates(first: CandidateResult, second: CandidateResult) -> bool:
    if first.worst_case_charge_seconds is None or second.worst_case_charge_seconds is None:
        return False
    if not first.observables or len(first.observables) != len(second.observables):
        return False
    # Each named endpoint retains its own precision and effect coordinate.
    first_axes = [first.worst_case_charge_seconds]
    second_axes = [second.worst_case_charge_seconds]
    for left, right in zip(first.observables, second.observables, strict=True):
        first_axes.append(left.confidence_half_width)
        second_axes.append(right.confidence_half_width)
        if left.minimum_effect is not None:
            first_axes.append(-left.modeled_value_lower_bound)
            second_axes.append(-right.modeled_value_lower_bound)
    return all(left <= right for left, right in zip(first_axes, second_axes, strict=True)) and any(
        left < right for left, right in zip(first_axes, second_axes, strict=True)
    )


def optimize(
    plans: tuple[CandidatePlan, ...],
    contracts: tuple[ObservableContract, ...],
    budget: BudgetContract,
    *,
    simulation_alpha: float = 0.01,
    objective: str = "minimum_charge",
    cost_scenarios: tuple[CostScenario, ...] = (),
) -> OptimizationResult:
    """Rank feasible plans by charge or worst endpoint radius relative to its target.

    Every candidate must pass its statistical contracts and all declared cost
    scenarios. Charge ranking uses the largest estimate across nominal inputs
    and explicit scenarios. Precision ranking uses the maximum normalized
    endpoint radius, followed by that charge and the candidate name.
    """
    try:
        _validate_contracts(contracts, budget)
        _validate_cost_scenarios(cost_scenarios)
        _require(objective in ("minimum_charge", "precision_at_budget"), f"unknown objective {objective!r}")
        _require(
            objective != "precision_at_budget"
            or all(
                contract.precision_half_width is not None and contract.minimum_effect is None for contract in contracts
            ),
            "precision_at_budget requires precision-only contracts with positive precision_half_width",
        )
        _require(bool(plans), "at least one candidate plan is required")
        _require(len({plan.name for plan in plans}) == len(plans), "candidate plan names must be unique")
        _require(_finite(simulation_alpha) and 0 < simulation_alpha < 1, "simulation_alpha must lie in (0, 1)")
        comparisons = _simulation_comparisons(plans, contracts)
    except (ValueError, OverflowError) as error:
        return OptimizationResult(
            None, (), (), (str(error),), simulation_alpha, 0, ASSUMPTIONS, objective, None, cost_scenarios
        )
    results = tuple(
        evaluate_candidate(
            plan,
            contracts,
            budget,
            simulation_alpha=simulation_alpha,
            simulation_comparisons=comparisons,
            cost_scenarios=cost_scenarios,
        )
        for plan in sorted(plans, key=lambda item: item.name)
    )
    feasible = [result for result in results if result.feasible]

    def rank(result: CandidateResult) -> tuple[float, float, str]:
        charge = result.worst_case_charge_seconds
        score = charge if objective == "minimum_charge" else result.normalized_precision_radius
        assert charge is not None and score is not None
        return score, charge, result.name

    selected = min(feasible, key=rank) if feasible else None
    frontier = tuple(result.name for result in feasible if not any(_dominates(other, result) for other in feasible))
    reasons = () if feasible else ("every supplied candidate failed at least one contract",)
    return OptimizationResult(
        selected.name if selected else None,
        results,
        frontier,
        reasons,
        simulation_alpha,
        comparisons,
        ASSUMPTIONS,
        objective,
        rank(selected)[0] if selected else None,
        tuple(sorted(cost_scenarios, key=lambda item: item.name)),
    )


def _verify() -> None:
    """Finite regression cases exercise scientific and budget admission boundaries."""
    terms = (ObservableTerm("signal", (0.0, 1.0)), ObservableTerm("null", (0.0, 1.0), -1))
    contract = ObservableContract("signal_above_null", terms, minimum_effect=0.2)
    budget = BudgetContract(100.0, 10.0, 80.0)

    def candidate(name: str, proxy: float = 0.9, duration: float = 0.001, shots: int = 4096) -> CandidatePlan:
        pubs = (
            PubPrediction(
                "signal_pub",
                {"signal": ((0.2, 0.8),)},
                duration,
                0.00025,
                "full scheduled duration",
                classical_stage_count=1,
            ),
            PubPrediction(
                "null_pub",
                {"null": ((0.8, 0.2),)},
                duration,
                0.00025,
                "full scheduled duration",
                classical_stage_count=1,
            ),
        )
        return CandidatePlan(
            name, (JobCandidate("job", pubs, shots, 2.0, 40.0, "fixed overhead model"),), (), {"esp": proxy}
        )

    expensive = candidate("high_proxy", 0.99, 0.003)
    cheap = candidate("low_proxy", 0.75)
    result = optimize((expensive, cheap), (contract,), budget)
    assert result.selected == "low_proxy", result
    assert result.pareto_frontier == ("low_proxy",), result
    assert result == optimize((cheap, expensive), (contract,), budget)
    noisier_pub = replace(cheap.jobs[0].pubs[0], member_distributions={"signal": ((0.35, 0.65),)})
    noisier = replace(cheap, jobs=(replace(cheap.jobs[0], pubs=(noisier_pub, cheap.jobs[0].pubs[1])),))
    tradeoff = optimize((expensive, noisier), (contract,), budget)
    assert tradeoff.selected == "low_proxy" and tradeoff.pareto_frontier == ("high_proxy", "low_proxy")
    tied = optimize((replace(cheap, name="zeta"), replace(cheap, name="alpha")), (contract,), budget)
    assert tied.selected == "alpha" and tied.pareto_frontier == ("alpha", "zeta")

    weaker_pub = replace(cheap.jobs[0].pubs[0], member_distributions={"signal": ((0.7, 0.3),)})
    weak = replace(cheap, jobs=(replace(cheap.jobs[0], pubs=(weaker_pub, cheap.jobs[0].pubs[1])),))
    assert not evaluate_candidate(weak, (contract,), budget).feasible
    assert optimize((weak,), (contract,), budget).selected is None
    assert not evaluate_candidate(candidate("too_few", shots=16), (contract,), budget).feasible
    model_effect = evaluate_candidate(cheap, (replace(contract, minimum_effect=0.0),), budget)
    assert model_effect.feasible
    assert math.isclose(model_effect.observables[0].effect_used_for_power or 0.0, 0.6)

    precision = ObservableContract("precision", (terms[0],), precision_half_width=0.03)
    assert evaluate_candidate(cheap, (precision,), budget).feasible
    assert not evaluate_candidate(candidate("imprecise", shots=64), (precision,), budget).feasible

    precise = candidate("more_precise", shots=8192)
    assert optimize((cheap, precise), (precision,), budget).selected == cheap.name
    precision_search = optimize((cheap, precise), (precision,), budget, objective="precision_at_budget")
    assert precision_search.selected == precise.name
    assert precision_search.objective == "precision_at_budget"
    assert precision_search.selected_objective_value == precision_search.candidates[1].normalized_precision_radius
    assert precision_search == optimize((precise, cheap), (precision,), budget, objective="precision_at_budget")
    assert precision_search.pareto_frontier == (cheap.name, precise.name)
    limited = tuple(
        replace(plan, jobs=(replace(plan.jobs[0], max_execution_seconds=20.0),)) for plan in (cheap, precise)
    )
    assert optimize(limited, (precision,), budget, objective="precision_at_budget").selected == cheap.name
    quota_limited = replace(precise, jobs=(replace(precise.jobs[0], max_execution_seconds=80.0),))
    assert (
        optimize(
            (cheap, quota_limited), (precision,), BudgetContract(70.0, 10.0, 80.0), objective="precision_at_budget"
        ).selected
        == cheap.name
    )
    for invalid_contracts in ((contract,), (precision, contract), (replace(precision, minimum_effect=0.0),)):
        invalid = optimize((cheap,), invalid_contracts, budget, objective="precision_at_budget")
        assert invalid.selected is None and "precision-only" in invalid.rejection_reasons[0]
    assert optimize((cheap,), (precision,), budget, objective="unknown").selected is None
    precision_tied = optimize(
        (replace(cheap, name="zeta"), replace(cheap, name="alpha"), expensive),
        (precision,),
        budget,
        objective="precision_at_budget",
    )
    assert precision_tied.selected == "alpha"

    # Different endpoint targets distinguish the minimax rule from raw radii
    # and a summed normalized radius. Explicit covariance bounds control each axis.
    precision_endpoints = (
        ObservableContract("wide_target", (terms[0],), precision_half_width=0.08),
        ObservableContract("narrow_target", (replace(terms[1], sign=1),), precision_half_width=0.04),
    )

    def endpoint_candidate(name: str, radii: tuple[float, float]) -> CandidatePlan:
        plan = candidate(name, shots=1024)
        return replace(
            plan,
            jobs=(
                replace(
                    plan.jobs[0],
                    pubs=tuple(
                        replace(
                            pub, member_distributions={member: ((1.0, 0.0),) for member in pub.member_distributions}
                        )
                        for pub in plan.jobs[0].pubs
                    ),
                ),
            ),
            covariance_bounds=tuple(
                CovarianceBound(
                    endpoint.name,
                    pub.name,
                    (f"{endpoint.terms[0].member}/r0",),
                    ((radius * radius * 1024 * endpoint.alpha,),),
                    "declared covariance upper bound for objective regression",
                )
                for endpoint, pub, radius in zip(precision_endpoints, plan.jobs[0].pubs, radii, strict=True)
            ),
        )

    uneven = endpoint_candidate("smaller_sum_and_raw_radius", (0.008, 0.024))
    balanced = endpoint_candidate("smaller_worst_normalized_radius", (0.032, 0.016))
    normalized_search = optimize((uneven, balanced), precision_endpoints, budget, objective="precision_at_budget")
    assert normalized_search.selected == balanced.name
    assert math.isclose(normalized_search.selected_objective_value or 0.0, 0.4)

    sensitivity = CostScenario("higher_overhead_and_latency", 4.0, 1000.0)
    scenario_search = optimize(
        (cheap, precise), (precision,), budget, objective="precision_at_budget", cost_scenarios=(sensitivity,)
    )
    assert scenario_search.selected == cheap.name
    accepted, rejected = scenario_search.candidates
    assert accepted.jobs[0].overhead_seconds == cheap.jobs[0].overhead_seconds
    assert accepted.jobs[0].pubs[0].classical_latency_seconds == 0
    assert accepted.cost_scenarios[0].jobs[0].pubs[0].classical_latency_seconds == 0.001
    assert accepted.cost_scenarios[0].jobs[0].pubs[0].classical_stage_count == 1
    assert math.isclose(accepted.worst_case_charge_seconds or 0.0, 4 + 2 * 4096 * 0.00225)
    assert not rejected.cost_scenarios[0].feasible
    assert any("cost scenario higher_overhead_and_latency" in reason for reason in rejected.rejection_reasons)
    alternate = candidate("costlier_nominal", duration=0.0013)
    alternate = replace(
        alternate,
        jobs=(
            replace(
                alternate.jobs[0], pubs=tuple(replace(pub, classical_stage_count=0) for pub in alternate.jobs[0].pubs)
            ),
        ),
    )
    assert optimize((cheap, alternate), (precision,), budget).selected == cheap.name
    assert optimize((cheap, alternate), (precision,), budget, cost_scenarios=(sensitivity,)).selected == alternate.name
    optimistic = CostScenario("zero_additions", 0.0, 0.0)
    nominal_envelope = evaluate_candidate(cheap, (precision,), budget, cost_scenarios=(optimistic,))
    assert nominal_envelope.worst_case_charge_seconds == nominal_envelope.estimated_charge_seconds
    assert optimize((cheap,), (precision,), budget, cost_scenarios=(optimistic, sensitivity)) == optimize(
        (cheap,), (precision,), budget, cost_scenarios=(sensitivity, optimistic)
    )
    missing_stages = replace(
        cheap,
        jobs=(
            replace(
                cheap.jobs[0], pubs=(replace(cheap.jobs[0].pubs[0], classical_stage_count=None), cheap.jobs[0].pubs[1])
            ),
        ),
    )
    assert not evaluate_candidate(missing_stages, (precision,), budget, cost_scenarios=(sensitivity,)).feasible
    for scenarios in (
        (sensitivity, sensitivity),
        (replace(sensitivity, name="nominal"),),
        (replace(sensitivity, job_overhead_seconds=-1.0),),
        (replace(sensitivity, classical_latency_us=float("nan")),),
    ):
        assert optimize((cheap,), (precision,), budget, cost_scenarios=scenarios).selected is None
    assert scenario_search.as_dict()["cost_scenarios"][0]["name"] == sensitivity.name

    observed_pubs = tuple(
        ObservedPub(pub.name, pub.member_distributions, job.shots) for job in cheap.jobs for pub in job.pubs
    )
    observed = analyze_observations(observed_pubs, (contract, precision))
    planned = evaluate_candidate(cheap, (contract, precision), budget)
    for measured, predicted in zip(observed.observables, planned.observables, strict=True):
        assert measured.confidence_half_width == predicted.confidence_half_width
        assert measured.detection_radius == predicted.detection_radius
    assert observed.observables[0].reject_null is True
    assert observed.observables[1].reject_null is None
    assert observed.observables[1].detection_radius is None
    fused_pub = replace(
        cheap.jobs[0].pubs[0],
        name="fused_pub",
        member_distributions={
            member: distributions
            for pub in cheap.jobs[0].pubs
            for member, distributions in pub.member_distributions.items()
        },
    )
    fused = replace(cheap, jobs=(replace(cheap.jobs[0], pubs=(fused_pub,)),))
    fused_planned = evaluate_candidate(fused, (contract,), budget).observables[0]
    fused_observed = analyze_observations(
        (ObservedPub(fused_pub.name, fused_pub.member_distributions, cheap.jobs[0].shots),), (contract,)
    ).observables[0]
    assert fused_observed.confidence_half_width == fused_planned.confidence_half_width
    assert fused_observed.detection_radius == fused_planned.detection_radius
    assert fused_observed.confidence_half_width < observed.observables[0].confidence_half_width
    assert fused_observed.detection_radius is not None
    assert observed.observables[0].detection_radius is not None
    assert fused_observed.detection_radius < observed.observables[0].detection_radius
    directional_estimate = (fused_observed.detection_radius + fused_observed.confidence_half_width) / 2
    directional = analyze_observations(
        (
            ObservedPub(
                "fused_pub",
                {"signal": ((0.5 - directional_estimate, 0.5 + directional_estimate),), "null": ((0.5, 0.5),)},
                cheap.jobs[0].shots,
            ),
        ),
        (contract,),
    ).observables[0]
    assert directional.reject_null is True and directional.lo <= contract.null_value
    for invalid_observed in (
        (),
        observed_pubs + (observed_pubs[0],),
        (replace(observed_pubs[0], shots=0), observed_pubs[1]),
        (replace(observed_pubs[0], member_distributions={"signal": ((0.5, 0.4),)}), observed_pubs[1]),
        (observed_pubs[0],),
    ):
        try:
            analyze_observations(invalid_observed, (contract,))
        except ValueError:
            pass
        else:
            raise AssertionError("invalid observation data passed admission")

    for duration in (-1.0, float("nan"), float("inf")):
        assert not evaluate_candidate(candidate("invalid_cost", duration=duration), (contract,), budget).feasible
    ceiling = replace(cheap, jobs=(replace(cheap.jobs[0], max_execution_seconds=1.0),))
    assert not evaluate_candidate(ceiling, (contract,), budget).feasible
    granularity = replace(cheap, jobs=(replace(cheap.jobs[0], shot_granularity=3),))
    assert not evaluate_candidate(granularity, (contract,), budget).feasible
    assert not evaluate_candidate(cheap, (contract,), BudgetContract(45.0, 10.0, 80.0)).feasible
    split = replace(
        cheap,
        jobs=(
            replace(cheap.jobs[0], name="signal_job", pubs=cheap.jobs[0].pubs[:1]),
            replace(cheap.jobs[0], name="null_job", pubs=cheap.jobs[0].pubs[1:]),
        ),
    )
    assert not evaluate_candidate(split, (contract,), BudgetContract(100.0, 10.0, 70.0)).feasible
    assert evaluate_candidate(split, (contract,), budget).total_execution_ceiling_seconds == 80.0
    mixed_shots = replace(split, jobs=(split.jobs[0], replace(split.jobs[1], shots=2048)))
    mixed_result = evaluate_candidate(mixed_shots, (contract,), budget)
    assert mixed_result.feasible
    assert [pub.shots for job in mixed_result.jobs for pub in job.pubs] == [4096, 2048]
    assert math.isclose(mixed_result.estimated_charge_seconds or 0.0, 4.0 + (4096 + 2048) * 0.00125)
    mixed_observed = analyze_observations(
        tuple(
            ObservedPub(pub.name, pub.member_distributions, job.shots) for job in mixed_shots.jobs for pub in job.pubs
        ),
        (contract,),
    )
    assert mixed_result.observables[0].confidence_half_width == mixed_observed.observables[0].confidence_half_width
    assert (
        mixed_result.observables[0].confidence_half_width
        > evaluate_candidate(split, (contract,), budget).observables[0].confidence_half_width
    )
    with_additions = replace(
        cheap,
        jobs=(
            replace(
                cheap.jobs[0],
                pubs=tuple(
                    replace(pub, reset_seconds=0.00001, classical_latency_seconds=0.00002) for pub in cheap.jobs[0].pubs
                ),
            ),
        ),
    )
    priced = evaluate_candidate(with_additions, (contract,), budget)
    assert math.isclose(priced.estimated_charge_seconds or 0.0, 2.0 + 2 * 4096 * 0.00128)

    simulated = replace(
        cheap,
        jobs=(replace(cheap.jobs[0], pubs=tuple(replace(pub, simulation_shots=16) for pub in cheap.jobs[0].pubs)),),
    )
    simulated_result = evaluate_candidate(simulated, (contract,), budget)
    assert not simulated_result.feasible and simulated_result.observables[0].simulation_error_radius > 0
    search = optimize((simulated, replace(simulated, name="another")), (contract,), budget)
    assert search.simulation_comparisons == 4
    assert (
        search.candidates[0].observables[0].simulation_error_radius
        >= simulated_result.observables[0].simulation_error_radius
    )

    replicas = 16
    replicated_pub = replace(cheap.jobs[0].pubs[0], member_distributions={"signal": ((0.2, 0.8),) * replicas})
    replicated = replace(cheap, jobs=(replace(cheap.jobs[0], pubs=(replicated_pub, cheap.jobs[0].pubs[1])),))
    assert (
        evaluate_candidate(replicated, (precision,), budget).observables[0].confidence_half_width
        == evaluate_candidate(cheap, (precision,), budget).observables[0].confidence_half_width
    )
    covariance = CovarianceBound(
        "precision",
        "signal_pub",
        tuple(f"signal/r{index}" for index in range(replicas)),
        tuple(tuple(0.16 if row == column else 0.0 for column in range(replicas)) for row in range(replicas)),
        "independent replica-score model, covariance bounded by diagonal 0.16",
    )
    independent = replace(replicated, covariance_bounds=(covariance,))
    assert (
        evaluate_candidate(independent, (precision,), budget).observables[0].confidence_half_width
        < evaluate_candidate(replicated, (precision,), budget).observables[0].confidence_half_width
    )
    correlated = replace(
        covariance,
        matrix=tuple(tuple(0.16 if row == column else 0.15 for column in range(replicas)) for row in range(replicas)),
    )
    assert (
        evaluate_candidate(replace(replicated, covariance_bounds=(correlated,)), (precision,), budget)
        .observables[0]
        .confidence_half_width
        == evaluate_candidate(replicated, (precision,), budget).observables[0].confidence_half_width
    )
    planned_half_width = evaluate_candidate(independent, (precision,), budget).observables[0].confidence_half_width
    observed_replicas = (ObservedPub("signal_pub", {"signal": ((0.2, 0.8),) * replicas}, independent.jobs[0].shots),)
    collected = analyze_observations(observed_replicas, (precision,), (covariance,)).observables[0]
    assert math.isclose(collected.confidence_half_width, planned_half_width, rel_tol=1e-12)
    assert collected.bound_methods == ("minimum_of_hoeffding_and_declared_covariance_cantelli_or_chebyshev",)
    assert (
        analyze_observations(observed_replicas, (precision,)).observables[0].confidence_half_width
        > collected.confidence_half_width
    )
    invalid_covariance = replace(covariance, matrix=((-1.0,),))
    assert not evaluate_candidate(
        replace(replicated, covariance_bounds=(invalid_covariance,)), (precision,), budget
    ).feasible
    non_psd = replace(
        covariance,
        matrix=tuple(tuple(-0.16 if row == column else 0.0 for column in range(replicas)) for row in range(replicas)),
    )
    assert not evaluate_candidate(replace(replicated, covariance_bounds=(non_psd,)), (precision,), budget).feasible
    nearly_psd = replace(covariance, labels=("signal/r0",), matrix=((-1e-13,),))
    assert not evaluate_candidate(replace(cheap, covariance_bounds=(nearly_psd,)), (precision,), budget).feasible
    assert optimize((), (contract,), budget).selected is None
    assert optimize((cheap,), (), budget).selected is None
    print("experiment optimizer: statistical, cost, covariance, simulation, and deterministic-selection checks passed")


if __name__ == "__main__":
    _verify()
