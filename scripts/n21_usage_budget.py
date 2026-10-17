"""QPU-second budget of the n21-feedback-encoded run, derived from retained records.

gororoba_quantum/N21_USAGE_BUDGET.md carries the tables this script renders
between its ``n21-usage-budget`` markers; ``--check`` fails when the note and
the retained inputs disagree, ``--write`` refreshes the block.

Inputs and what each fixes:

- the raw jobs ``BILLING_JOBS`` pins, each by run, job id and its
  index.json sha256: per job, the executions (sum of PUB shots), the
  repetition delay, the scheduler circuit duration per PUB, the metered
  ``circuits_execution_time_ns`` and the integer ``qpu_charge_time_seconds``.
  The execution time equals sum(shots x (rep_delay + scheduler duration)),
  and the charge equals ceil(execution + c) for one constant c whose
  admissible interval the script intersects over all jobs. Every file the
  fit reads matches its digest in the pinned index (metrics through
  ``metrics_sha256``), so a job retained later leaves the fit unchanged and
  an altered input stops it.
- the same jobs' records, pinned by sha256 in ``BILLING_RECORDS``: the
  scheduler duration minus the Target gate-time lower bound per PUB, on
  ibm_kingston, without and with one feed-forward stage.
- docs/evidence/heron_platform/targets.json: each backend's rep_delay_range.
- the reference dry-run record (``REFERENCE``): both PUBs' Target
  durations and the modeled outcome laws.

Shot counts come from experiment_optimizer.evaluate_candidate itself, the
contract live_run applies, by bisection on the uniform per-PUB shots; every
row states its bound, model method, replica set and repetition delay. Rows
below the default 250 us repetition delay and rows marked "extension" are
outside the admitted planning contract; they size levers, not approvals.

Usage:
    "$PYTHON" scripts/n21_usage_budget.py --check gororoba_quantum/N21_USAGE_BUDGET.md
    "$PYTHON" scripts/n21_usage_budget.py --write gororoba_quantum/N21_USAGE_BUDGET.md
    "$PYTHON" scripts/n21_usage_budget.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import statistics
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import n21_exact_planning  # noqa: E402
from diagnostic_experiments import family_contracts  # noqa: E402
from experiment_optimizer import (  # noqa: E402
    BudgetContract,
    CandidatePlan,
    CovarianceBound,
    JobCandidate,
    ObservableContract,
    ObservableTerm,
    PubPrediction,
    evaluate_candidate,
)

REFERENCE = ROOT / "results/live/2026-10-17T130242.718497Z/record.json"
TARGETS = ROOT / "docs/evidence/heron_platform/targets.json"
# Exact-model dry runs of the same family, oldest calibration first, and the
# Kaggle validation record of the retained 2026-10-17T003834Z ISA.
DRIFT_RECORDS = (
    ROOT / "results/live/2026-10-17T091514.662497Z/record.json",
    ROOT / "results/live/2026-10-17T094344.639211Z/record.json",
    ROOT / "results/live/2026-10-17T101105.548987Z/record.json",
    ROOT / "results/live/2026-10-17T111902.183133Z/record.json",
    ROOT / "results/live/2026-10-17T114216.070396Z/record.json",
    REFERENCE,
)
VALIDATION = ROOT / "docs/evidence/n21_exact_model/validation.json"
BEGIN = "<!-- n21-usage-budget:begin -->"
END = "<!-- n21-usage-budget:end -->"
DT_SECONDS = 4e-9
OVERHEAD_SECONDS = 2.3
LATENCY_SECONDS = 20e-6
SIGNED = (0.0, 1.0, 0.0, -1.0)
UNIFORM = (0.25, 0.25, 0.25, 0.25)
VARIANCE_BOUND = 0.55
LIVE = ROOT / "results/live"
# The billing fit's inputs: (run, job id, raw/<job id>/index.json sha256).
# A job retained later stays outside the fit until it is added here and the
# note re-rendered with --write.
BILLING_JOBS = (
    (
        "2026-10-11T152922.787095Z",
        "db5qmqclf4us73c4e1ug",
        "765de1011cdfc314dd0475b319d2beaa35df683968c390e6447f9fd92fd7532a",
    ),
    (
        "2026-10-12T055624.091217Z",
        "db67fqsvf2bc73d0pk4g",
        "a0208a96859cf149a0aad8a1151cfd7ab8affd490d318822708aff199bff8434",
    ),
    (
        "2026-10-12T055624.091217Z",
        "db67frimb58s738bci4g",
        "97f4d3143d560296f3ab68f8ba16ba7f4ec7048c334205bddcdd546c177ad648",
    ),
    (
        "2026-10-13T020454.599853Z",
        "db6p55clf4us73c5nd9g",
        "8ec617c333e73edc6e54bc6cd0858b557fe84b226c0bdc9fd982cd802abf4f82",
    ),
    (
        "2026-10-13T022433.333775Z",
        "db6pepklf4us73c5nqcg",
        "5dcab6316835ffc7a5f76970140ca0156c609113d83e643ae3e2153505a03b1e",
    ),
    (
        "2026-10-13T025444.603480Z",
        "db6q2p2mb58s738c75gg",
        "5052cccdc71534a3e51b2f391ad002419b7c3b30244d1a54d7ec4106552a67b6",
    ),
    (
        "2026-10-13T025444.603480Z",
        "db6q2rklf4us73c5oq90",
        "4976e9881e4b70206b8214ff050d7f55c4f93fa8445d07a40af24a71a5ba1961",
    ),
    (
        "2026-10-13T032011.664435Z",
        "db6q9qo4qg6s73c57020",
        "2b1d9a62f4adfa89c58502933480e14add27614bb895af7f2c16b0cd0dc08712",
    ),
    (
        "2026-10-13T032011.664435Z",
        "db6q9rsvf2bc73d1kpug",
        "fa14060afed78b755744511c93c27b671582868df92c9abcc688cfa63d35244d",
    ),
    (
        "2026-10-13T080216.451663Z",
        "db6ub8svf2bc73d1rc50",
        "31ecb334baf41e3716e2a189ab2011d4a7d8c9f94709d9ed97e63fd618f69794",
    ),
    (
        "2026-10-13T083417.634585Z",
        "db6uqdkvf2bc73d1sc80",
        "099573bc579e0d96902a0bd787e55e4eae0ba8b9b3a031d7fe4bd7b17b9c272d",
    ),
    (
        "2026-10-13T201757.782152Z",
        "db794cmil99s73fnjlk0",
        "f5c83da76aabe5bd2bc2a5d9251513b0bd09a7bed8bab1088f6998cb38818cfb",
    ),
    (
        "2026-10-13T201757.782152Z",
        "db794dor1c5c738k1a50",
        "827b5827d3645de6c156e98deb9cff63dbfced53dc09c17ebd7d28c756d3c0b7",
    ),
    (
        "2026-10-13T201757.782152Z",
        "db794hmr6oqs73871tbg",
        "d159b5dcedd5d51711031883ed9dfe4972ce60be293b8c0591ccc16c0041fdc1",
    ),
    (
        "2026-10-15T030748.903241Z",
        "db847nur6oqs7388nen0",
        "87a51307053ff325d70a2bdebc4dcfb4f89bc136abed22e3468357262e99e1e5",
    ),
    (
        "2026-10-15T030748.903241Z",
        "db847oiraffc73fbmfk0",
        "cea105c5ac92439fd4635b4d496e9b5ca8d2bb031c8ec40f0ca040f492dd5cdc",
    ),
    (
        "2026-10-15T030903.235380Z",
        "db848h6r6oqs7388nfm0",
        "aed6460fb8a05597fd76f141f9e1519abed49a78651ab723163a3bea4301a698",
    ),
    (
        "2026-10-15T030903.235380Z",
        "db848hmil99s73fp99tg",
        "428d447e89b9f68751ced42b471b4d17b4e54a6d2cdf3264eb4a1f916f749f18",
    ),
    (
        "2026-10-15T031229.371738Z",
        "db84dt6il99s73fp9gjg",
        "2c1e68bf0c8eef92d629f10566415a613a84ef30290ff10da37e4a5744ab5cf7",
    ),
    (
        "2026-10-15T031229.371738Z",
        "db84dv2raffc73fbmnag",
        "bbd42b3f39afeaa9f74fa4ccc2c4664e6d9abf7fd59743d49b6724bc8b65475f",
    ),
    (
        "2026-10-15T070847.644554Z",
        "db87o48r1c5c738lu8jg",
        "15910378f2842d8b59b52fb1105ca0c0ae4d26a3b51c7fdb73e238fd73ea43af",
    ),
    (
        "2026-10-15T070853.550532Z",
        "db87o8or1c5c738lu910",
        "6a5a047079a34fa78f4fb1dc3a5453d7f9742b36a9ce568f627bdd62d2cc0d91",
    ),
    (
        "kingston-wide-control-result",
        "db6qe7klf4us73c5pdc0",
        "4eec8b6b5cdd397bfe328333732a596d8add6b7f142e32a307ae3a46b71f3dfa",
    ),
)
# record.json sha256 of each billing run that carries one; the scheduler
# excess reads its execution manifest's Target gate-time bounds.
BILLING_RECORDS = {
    "2026-10-11T152922.787095Z": "3b81e5b3ba59bf5041daeaae911d9c5b62063fe4186544c5ed79e9ef709c1e59",
    "2026-10-12T055624.091217Z": "91145c3456e8670a19eea258416412d020ca5e3fa71aa37b91ce7a5cb7f74670",
    "2026-10-13T020454.599853Z": "d9441a3b8c613c666657f3abdceb7eab9842db5d97310ec3af0319b21ad020ee",
    "2026-10-13T022433.333775Z": "953925600a12666f406e56f7833be4bc2885c3904f5a64e82875ceeba56ffdad",
    "2026-10-13T025444.603480Z": "dfe1e15a1a429c5625acac46a13f51dc4025619273b123ba969122a2a54dc83c",
    "2026-10-13T032011.664435Z": "cde647e53a4a08164f71e474b63b36b60ad1417a850c48adb2907af050dc2368",
    "2026-10-13T080216.451663Z": "c7a5c333f806f412b1966d467743a30828239ad1997fd5be0729dab3015d8b19",
    "2026-10-13T083417.634585Z": "c0e20af610a17db49c41e8a8f979b5ed27ac793dbc5e2eed656897f9af97369d",
    "2026-10-13T201757.782152Z": "5685faab1c278ee1078799612d2b61a97949f891eafde4038e4388f98fcc4868",
    "2026-10-15T030748.903241Z": "c76f608cbf0fb253d5b93045ec47e254e2748182c76bc36a0277b7b5338aaea8",
    "2026-10-15T030903.235380Z": "1e36e27c9e4f10a5fab1e0e37028c89c832717e06822d8bb17e5fd85b3eba1a0",
    "2026-10-15T031229.371738Z": "044dd98ad5483accb0acfe3fa10841c7c06b1cac76f41fefe05fd89cc6645f07",
    "2026-10-15T070847.644554Z": "9bb872bf20dd664489afa2b423aefe102042f4be2747abc60765b6947af45733",
    "2026-10-15T070853.550532Z": "22c078143a9e266123ad0f9acba9f3c234ac1c6522aa3e669eb4a579aee32c65",
}


# ---------------------------------------------------------------- billing


@dataclass(frozen=True)
class Job:
    run: str
    job_id: str
    executions: int
    rep_delay: float
    modeled_seconds: float
    metered_seconds: float
    charge: int
    chunks: int


def _verified(path: Path, digest: str) -> bytes:
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError(f"{path}: sha256 differs from its pinned digest")
    return payload


@dataclass(frozen=True)
class PinnedJob:
    run: Path
    directory: Path
    index: dict[str, Any]

    def read(self, name: str) -> Any:
        """A file of the job, checked against the pinned index's digest for it."""
        if name in self.index["files"]:
            return json.loads(_verified(self.directory / name, self.index["files"][name]))
        position = self.index["metrics"].index(name)
        return json.loads(_verified(self.directory / name, self.index["metrics_sha256"][position]))


def pinned_jobs(live: Path) -> list[PinnedJob]:
    """The BILLING_JOBS raw jobs under live, each index.json checked against its pinned sha256."""
    jobs = []
    for run, job_id, digest in BILLING_JOBS:
        directory = live / run / "raw" / job_id
        index = json.loads(_verified(directory / "index.json", digest))
        if index["job_id"] != job_id:
            raise ValueError(f"{directory}: index names job {index['job_id']}")
        jobs.append(PinnedJob(live / run, directory, index))
    return jobs


def retained_jobs(live: Path = LIVE) -> list[Job]:
    jobs = []
    for pinned in pinned_jobs(live):
        directory, index = pinned.directory, pinned.index
        metrics = pinned.read(index.get("metrics_latest") or sorted(index["metrics"])[-1])
        metadata = pinned.read("result_metadata.json")
        rep_delay = metadata["options"]["execution"].get("rep_delay")
        # A job submitted without an explicit rep_delay ran at the backend default.
        rep_delay = 250e-6 if rep_delay is None else float(rep_delay)
        executions = 0
        modeled = 0.0
        for name in index["files"]:
            if not name.startswith("pub_"):
                continue
            pub = pinned.read(name)
            shots = {register["num_shots"] for register in pub["registers"].values()}
            if len(shots) != 1:
                raise ValueError(f"{directory}/{name}: registers disagree on shots")
            count = shots.pop()
            duration = pub["metadata"]["compilation"]["scheduler_timing"]["circuit_duration"] * DT_SECONDS
            executions += count
            modeled += count * (rep_delay + duration)
        jobs.append(
            Job(
                directory.parent.parent.name,
                index["job_id"],
                executions,
                rep_delay,
                modeled,
                metrics["circuits_execution_time_ns"] * 1e-9,
                int(metrics["usage"]["qpu_charge_time_seconds"]),
                len(metadata["executor"]["chunk_timing"]),
            )
        )
    return jobs


def ceil_interval(jobs: list[Job]) -> tuple[float, float]:
    """The interval (low, high] of c with charge = ceil(metered + c) for every job."""
    low, high = -math.inf, math.inf
    for job in jobs:
        low = max(low, job.charge - 1 - job.metered_seconds)
        high = min(high, job.charge - job.metered_seconds)
    return low, high


def kingston_scheduler_excess(live: Path = LIVE) -> dict[int, list[int]]:
    """Scheduler circuit duration minus the Target gate-time bound (dt), by feed-forward stage count."""
    excess: dict[int, list[int]] = {}
    for pinned in pinned_jobs(live):
        digest = BILLING_RECORDS.get(pinned.run.name)
        if digest is None:
            continue
        record = json.loads(_verified(pinned.run / "record.json", digest))
        bounds = {
            pub["name"]: (pub.get("target_gate_lower_bound_dt"), pub.get("sequential_stage_count"))
            for pub in record.get("execution_pubs", [])
            if pub.get("backend") == "ibm_kingston"
        }
        for name in pinned.index["files"]:
            if not name.startswith("pub_"):
                continue
            pub = pinned.read(name)
            bound, stages = bounds.get(pub["pub_name"], (None, None))
            if bound is None or stages is None:
                continue
            duration = pub["metadata"]["compilation"]["scheduler_timing"]["circuit_duration"]
            excess.setdefault(int(stages), []).append(int(duration) - int(bound))
    return excess


# ---------------------------------------------------------------- sizing


@dataclass(frozen=True)
class Reference:
    pubs: tuple[tuple[str, str, float, int], ...]  # (pub, member, Target seconds, feed-forward stages)
    laws: dict[str, tuple[float, ...]]
    calibration: str
    backend: str
    # Exact laws of every replica of each replicated candidate, keyed by replica count
    # (the first candidate of that count), and every candidate's own PUB rows and laws.
    replica_sets: dict[int, dict[str, tuple[tuple[float, ...], ...]]]
    replica_pubs: dict[int, tuple[tuple[str, str, float, int], ...]]
    candidates: dict[str, tuple[tuple[tuple[str, str, float, int], ...], dict[str, tuple[tuple[float, ...], ...]]]]


def reference() -> Reference:
    record = json.loads(REFERENCE.read_text())
    pubs_by_name = {pub["name"]: pub for pub in record["execution_pubs"]}
    candidate = next(
        c for c in record["optimization"]["candidates"] if c["name"] == record["optimization"]["retained_candidate"]
    )
    replica_sets: dict[int, dict[str, tuple[tuple[float, ...], ...]]] = {}
    replica_pubs: dict[int, tuple[tuple[str, str, float, int], ...]] = {}
    candidates: dict[str, Any] = {}

    def pub_rows(planned: dict[str, Any]) -> tuple[tuple[str, str, float, int], ...]:
        return tuple(
            (
                pub["name"],
                pubs_by_name[pub["name"]]["components"][0]["member"],
                float(pub["scheduled_seconds"]),
                int(pub["classical_stage_count"]),
            )
            for pub in planned["jobs"][0]["pubs"]
        )

    rows = pub_rows(candidate)
    group = record["groups"][0]
    laws = {member["name"]: tuple(member["replicas"][0]["noisy"]) for member in group["members"]}
    exact = record.get("exact_model")
    if exact is not None:
        laws = {row["entry"]: tuple(row["exact"]) for row in exact["replicas"] if row["replica"] == 0}
        counts = {
            c["name"].rsplit("-shots-", 1)[0]: int(c["proxy_metadata"]["replicas"])
            for c in record["optimization"]["candidates"]
        }
        planned_rows = {c["name"].rsplit("-shots-", 1)[0]: pub_rows(c) for c in record["optimization"]["candidates"]}
        for name, evidence in sorted(exact.get("candidates", {}).items()):
            # A candidate rejected by the exact-model falsifier or by its covariance
            # declaration never reached the optimizer.
            if evidence.get("passed") is False or name not in counts:
                continue
            members: dict[str, list[tuple[float, ...]]] = {}
            for row in evidence["replicas"]:
                members.setdefault(row["entry"], []).append(tuple(row["exact"]))
            laws_by_member = {k: tuple(v) for k, v in members.items()}
            candidates[name] = (planned_rows[name], laws_by_member)
            replica_sets.setdefault(counts[name], laws_by_member)
            replica_pubs.setdefault(counts[name], planned_rows[name])
    else:
        # A sampled record retains the optimizer's predicted contrast, not its
        # marginals; the group's laws, mixed toward uniform to that contrast,
        # stand in for them.
        ratio = candidate["observables"][0]["predicted_value"] / contrast(laws)
        laws = {name: toward_uniform(law, ratio) for name, law in laws.items()}
    replica_sets.setdefault(1, {name: (law,) for name, law in laws.items()})
    replica_pubs.setdefault(1, rows)
    return Reference(rows, laws, group["calibration"], group["backend"], replica_sets, replica_pubs, candidates)


def contrast(laws: dict[str, tuple[float, ...]]) -> float:
    feedback, control = (laws[name] for name in sorted(laws))
    return (feedback[1] - feedback[3]) - (control[1] - control[3])


def toward_uniform(law: tuple[float, ...], ratio: float) -> tuple[float, ...]:
    """The law mixed with the uniform law so that its signed contrast scales by ratio."""
    mixed = [ratio * p + (1 - ratio) * u for p, u in zip(law, UNIFORM, strict=True)]
    total = math.fsum(mixed)
    return tuple(value / total for value in mixed)


@dataclass(frozen=True)
class Design:
    label: str
    model_shots: int | None  # None: exact model
    comparisons: int | None  # simulation comparisons the search counts
    replicas: int = 1
    equal: bool = False  # every replica carries replica 0's law
    variance_bound: float | None = None
    rep_delay: float = 250e-6
    admitted: bool = True
    candidate: str | None = None  # a reference candidate's own PUB rows and replica laws
    ucl: bool = True  # False reads the declared projection with no allowance or falsifier tail
    hoeffding_only: bool = False  # keep the bounds' alpha charge, never take Cantelli


def design_inputs(
    ref: Reference, design: Design
) -> tuple[tuple[tuple[str, str, float, int], ...], dict[str, tuple[tuple[float, ...], ...]]]:
    """The PUB rows and per-member replica laws a design sizes."""
    if design.candidate is not None:
        return ref.candidates[design.candidate]
    if design.equal:
        return ref.pubs, {member: (law,) * design.replicas for member, law in ref.laws.items()}
    return ref.replica_pubs[design.replicas], ref.replica_sets[design.replicas]


def plan(ref: Reference, design: Design, shots: int) -> tuple[CandidatePlan, tuple[ObservableContract, ...]]:
    contracts = family_contracts("n21-feedback-encoded", 0.08, 0.05, 0.8)
    pubs = []
    rows, laws = design_inputs(ref, design)
    for name, member, seconds, stages in rows:
        replicas = laws[member]
        pubs.append(
            PubPrediction(
                name,
                {member: replicas},
                seconds,
                design.rep_delay,
                "Target duration; declared per-stage classical latency",
                classical_latency_seconds=stages * LATENCY_SECONDS,
                simulation_shots=design.model_shots,
                classical_stage_count=stages,
            )
        )
    bounds: tuple[CovarianceBound, ...] = ()
    if design.variance_bound is not None and design.replicas > 1:
        # The collection rule: each bound's radius reads the declared projection
        # plus the UCL allowance at these shots, and spends the falsifier tail.
        bounds = n21_exact_planning.replica_covariance_bounds(pubs, contracts, design.variance_bound, shots)
        if not design.ucl:
            bounds = tuple(replace(bound, variance_allowance=0.0, falsifier_tail=0.0) for bound in bounds)
        if design.hoeffding_only:
            # A projection no Cantelli radius undercuts keeps the falsifier's
            # alpha charge while every radius stays Hoeffding's.
            bounds = tuple(replace(bound, variance_allowance=1e12) for bound in bounds)
    job = JobCandidate("kingston/dynamic/1", tuple(pubs), shots, OVERHEAD_SECONDS, 1e9, "declared 2.3 s")
    return CandidatePlan("sizing", (job,), bounds), contracts


def feasible(ref: Reference, design: Design, shots: int) -> tuple[bool, Any]:
    candidate, contracts = plan(ref, design, shots)
    budget = BudgetContract(1e12, 0.0, 1e12)
    result = evaluate_candidate(candidate, contracts, budget, simulation_comparisons=design.comparisons)
    return result.observables[0].feasible, result


def minimum_shots(ref: Reference, design: Design, ceiling: int = 1 << 34) -> tuple[int | None, Any]:
    if not feasible(ref, design, ceiling)[0]:
        return None, feasible(ref, design, ceiling)[1]
    low, high = 1, ceiling
    while low < high:
        middle = (low + high) // 2
        if feasible(ref, design, middle)[0]:
            high = middle
        else:
            low = middle + 1
    return low, feasible(ref, design, low)[1]


def measured_charge(
    rows: tuple[tuple[str, str, float, int], ...],
    shots: int,
    rep_delay: float,
    excess: dict[int, list[int]],
    c_high: float,
) -> int:
    """ceil(executions x (Target bound + measured scheduler excess + rep_delay) + c) at the interval's top."""
    seconds = 0.0
    for _name, _member, target, stages in rows:
        seconds += shots * (target + statistics.median(excess[stages]) * DT_SECONDS + rep_delay)
    return math.ceil(seconds + c_high)


def designs(ref: Reference) -> list[Design]:
    sampled = 65536
    # Each plan scores two finite-shot marginals, one per arm, in a sampled search.
    plans = len(json.loads(REFERENCE.read_text())["optimization"]["candidates"])
    return [
        Design(
            f"sampled 65,536 across the dry run's {plans} plans, Hoeffding, R=1",
            sampled,
            2 * plans,
        ),
        Design("sampled 65,536, one plan, Hoeffding, R=1", sampled, 2),
        Design("sampled 589,824 (the Kaggle validation's size), one plan, Hoeffding, R=1", 589824, 2),
        Design("exact model, Hoeffding, R=1", None, None),
        *(
            Design(
                f"exact, Cantelli V=0.55 through its UCL, R={count} {replica_label(ref, count)}",
                None,
                None,
                count,
                False,
                VARIANCE_BOUND,
            )
            for count in sorted(ref.replica_sets)
            if count > 1
        ),
        Design(
            f"earlier rule: V=0.55 read as declared, no falsifier tail, R=2 {replica_label(ref, 2)}",
            None,
            None,
            2,
            False,
            VARIANCE_BOUND,
            admitted=False,
            ucl=False,
        ),
        Design("exact, Cantelli V=0.55, R=4 equal replicas (hypothetical)", None, None, 4, True, VARIANCE_BOUND),
        Design("exact, Hoeffding, R=1, rep_delay 100 us", None, None, rep_delay=100e-6, admitted=False),
        Design("exact, Hoeffding, R=1, rep_delay 50 us", None, None, rep_delay=50e-6, admitted=False),
    ]


def normal_shots(ref: Reference, alpha: float = 0.05, power: float = 0.8) -> int:
    """Per-arm shots of a one-sided normal-approximation test at the reference contrast (unadmitted)."""
    from statistics import NormalDist

    variance = 0.0
    for law in ref.laws.values():
        mean = law[1] - law[3]
        variance += law[1] + law[3] - mean**2
    z = NormalDist().inv_cdf(1 - alpha) + NormalDist().inv_cdf(power)
    return math.ceil(z * z * variance / contrast(ref.laws) ** 2)


def replica_contrasts(ref: Reference, count: int) -> list[float]:
    feedback, control = (ref.replica_sets[count][name] for name in sorted(ref.replica_sets[count]))
    return [(f[1] - f[3]) - (c[1] - c[3]) for f, c in zip(feedback, control, strict=True)]


def replica_label(ref: Reference, count: int) -> str:
    return "(replica contrasts " + ", ".join(f"{value:.4f}" for value in replica_contrasts(ref, count)) + ")"


def detection_power_constant(alpha: float = 0.05, power: float = 0.8) -> float:
    """K with detection plus power radius K / sqrt(n): Hoeffding, span 2, union over two PUBs."""
    return 2 * sum(2 * math.sqrt(math.log(1 / tail) / 2) for tail in (alpha / 2, (1 - power) / 2))


def drift_rows() -> list[tuple[str, str, str, float]]:
    """The one-replica exact contrast of each retained source, with its calibration and layout."""
    import n21_exact_model_validation

    validation = json.loads(VALIDATION.read_text())
    snapshot = json.loads((ROOT / validation["snapshot"]["path"]).read_text())
    retained = json.loads((ROOT / "results/live/2026-10-17T003834.987727Z/record.json").read_text())
    exact = n21_exact_model_validation.exact_laws(
        ROOT / validation["snapshot"]["path"], ROOT / validation["isa"]["path"]
    )
    feedback, control = (exact[name] for name in sorted(exact))
    qubits = retained["groups"][0]["replicas"][0]["physical_qubits"]
    rows = [
        (
            "calibration snapshot, retained ISA",
            snapshot["calibration"],
            str(qubits),
            (feedback[1] - feedback[3]) - (control[1] - control[3]),
        )
    ]
    for path in DRIFT_RECORDS:
        record = json.loads(path.read_text())
        exact_rows = (
            [row for row in record["exact_model"]["candidates"]["candidate-000"]["replicas"]]
            if "candidates" in record["exact_model"]
            else record["exact_model"]["replicas"]
        )
        laws_by_entry = {row["entry"]: row["exact"] for row in exact_rows if row["replica"] == 0}
        feedback, control = (laws_by_entry[name] for name in sorted(laws_by_entry))
        value = (feedback[1] - feedback[3]) - (control[1] - control[3])
        group = record["groups"][0]
        rows.append(
            (f"dry run {path.parent.name}", group["calibration"], str(group["replicas"][0]["physical_qubits"]), value)
        )
    return rows


def assumption_text(design: Design, radii: dict[str, bool] | None = None) -> str:
    """The model and replica assumptions a row needs; radii names which radius takes the declared covariance."""
    parts = ["exact model" if design.model_shots is None else f"sampled model, {design.model_shots:,} shots"]
    if design.variance_bound is not None and design.replicas > 1:
        bounded = [name for name, uses in (radii or {}).items() if uses]
        plain = [name for name, uses in (radii or {}).items() if not uses]
        parts.append(
            f"{' and '.join(bounded)} radius on independent replicas, variance <= {design.variance_bound}"
            if bounded
            else "declared covariance unused: Hoeffding is tighter"
        )
        if bounded and plain:
            parts.append(f"{' and '.join(plain)} radius Hoeffding")
    if design.equal:
        parts.append("hypothetical equal replicas")
    if design.rep_delay < 250e-6:
        parts.append("state-prep error unmodeled")
    return "; ".join(parts)


def extension_shots(ref: Reference, kind: str, count: int = 1, alpha: float = 0.05) -> int:
    """Per-arm shots of finite-sample bounds experiment_optimizer does not implement (owner sign-off needed).

    "bernstein": Bernstein's inequality per PUB with the declared variance
    bound V and |score - mean| <= 2, radius sqrt(2 V ln(1/t) / n) + 4 ln(1/t) / (3 n);
    "independent": Hoeffding over the n x R independent replica scores of span 2.
    Both keep the contract's union bound over the two PUBs and its sum of
    detection (alpha / 2) and power (0.2 / 2) radii.
    """
    tails = (alpha / 2, 0.2 / 2)
    effect = math.fsum(replica_contrasts(ref, count)) / count

    def radius(n: int) -> float:
        total = 0.0
        for tail in tails:
            log = math.log(1 / tail)
            if kind == "bernstein":
                total += math.sqrt(2 * VARIANCE_BOUND * log / n) + 4 * log / (3 * n)
            else:
                total += 2 * math.sqrt(log / (2 * n * count))
        return 2 * total

    low, high = 1, 1 << 34
    while low < high:
        middle = (low + high) // 2
        if radius(middle) <= effect:
            high = middle
        else:
            low = middle + 1
    return low


def cz_rows(ref: Reference, retentions: tuple[float, float]) -> list[str]:
    """Shots and seconds after removing k routed CZ, contrast c(k) = c0 / rho^k, exact model, Hoeffding R=1."""
    base = Design("exact model, Hoeffding, R=1", None, None)
    n0, _ = minimum_shots(ref, base)
    if n0 is None:
        return []
    rows = []
    for k in (0, 25, 50, 100, 200):
        cells = []
        for rho in retentions:
            scale = rho ** (-k)
            n = math.ceil(n0 / scale**2)
            seconds = OVERHEAD_SECONDS + n * sum(t + s * LATENCY_SECONDS + 250e-6 for _, _, t, s in ref.pubs)
            cells.append(f"{n:,} / {seconds:.1f}")
        rows.append(f"| {k} | " + " | ".join(cells) + " |")
    return rows


def render() -> str:
    jobs = retained_jobs(LIVE)
    low, high = ceil_interval(jobs)
    residuals = [(job.metered_seconds - job.modeled_seconds) * 1e6 for job in jobs]
    rep_delays = {job.rep_delay for job in jobs}
    if len(rep_delays) != 1:
        raise ValueError(f"pinned jobs mix repetition delays {sorted(rep_delays)}")
    (rep_delay_us,) = (value * 1e6 for value in rep_delays)
    chunks = sorted({job.chunks for job in jobs})
    excess = kingston_scheduler_excess()
    targets = json.loads(TARGETS.read_text())
    ref = reference()
    c0 = contrast(ref.laws)
    lines = [
        BEGIN,
        "",
        f"Generated by `scripts/n21_usage_budget.py --write`; reference record "
        f"`{REFERENCE.relative_to(ROOT)}` ({ref.backend}, calibration {ref.calibration}).",
        "",
        "**Metered billing (retained jobs).**",
        "",
        f"- Jobs: {len(jobs)}; the result metadata's executor `chunk_timing` lists "
        f"{' or '.join(map(str, chunks))} chunk(s) per job; executions {min(j.executions for j in jobs):,} to "
        f"{max(j.executions for j in jobs):,}.",
        f"- `circuits_execution_time_ns` minus sum(shots x (rep_delay + scheduler circuit duration)) is a per-job "
        f"constant, {min(residuals):.1f} to {max(residuals):.1f} us across those executions: one {rep_delay_us:.0f} us "
        f"rep_delay plus {-max(residuals) - rep_delay_us:.1f} to {-min(residuals) - rep_delay_us:.1f} us.",
        f"- `qpu_charge_time_seconds` is an integer, equal to ceil(execution + c) on every job for c in "
        f"({low:.3f}, {high:.3f}] s.",
        "- ibm_kingston scheduler duration minus the Target gate-time bound: "
        + "; ".join(
            f"{stages} feed-forward stage(s): {min(values)} to {max(values)} dt (median {statistics.median(values)})"
            for stages, values in sorted(excess.items())
        )
        + ".",
        "- rep_delay_range: "
        + "; ".join(
            f"{name} {entry['rep_delay_range'][0] * 1e6:.0f} to {entry['rep_delay_range'][1] * 1e6:.0f} us, "
            f"default {entry['default_rep_delay'] * 1e6:.0f} us"
            for name, entry in sorted(targets["backends"].items())
        )
        + ".",
        "",
        "**Per-shot cost of the pair (one shot of each arm).**",
        "",
        "| PUB | Target gate time (us) | feed-forward stages |",
        "| --- | --- | --- |",
    ]
    for name, _member, seconds, stages in ref.pubs:
        lines.append(f"| {name} | {seconds * 1e6:.3f} | {stages} |")
    lines += ["", "| rep_delay (us) | planner seconds per pair (us) | measured-model seconds per pair (us) |"]
    lines.append("| --- | --- | --- |")
    for rep in (250e-6, 100e-6, 50e-6, 0.0):
        planner = sum(t + s * LATENCY_SECONDS + rep for _, _, t, s in ref.pubs)
        measured = sum(t + statistics.median(excess[s]) * DT_SECONDS + rep for _, _, t, s in ref.pubs)
        lines.append(f"| {rep * 1e6:.0f} | {planner * 1e6:.1f} | {measured * 1e6:.1f} |")
    lines += [
        "",
        "**Calibration drift of the exact contrast (one replica, Hoeffding, 250 us).**",
        "",
        "| Source | calibration | layout qubits | exact contrast | shots per arm | planner charge (s) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for source, calibration, qubits, value in drift_rows():
        shots = math.ceil((detection_power_constant() / value) ** 2)
        lines.append(
            f"| {source} | {calibration} | {qubits} | {value:.4f} | {shots:,} | "
            f"{OVERHEAD_SECONDS + shots * sum(t + s * LATENCY_SECONDS + 250e-6 for _, _, t, s in ref.pubs):.1f} |"
        )
    lines += [
        "",
        f"**Shots and seconds.** Reference modeled contrast difference {c0:.4f} (ideal 0.25); alpha 0.05, "
        "power 0.8, one-sided, union bound over the two PUBs, as `family_contracts` declares.",
        "",
        "| Configuration | executions | planner charge (s) | measured-model charge (s) | smallest job ceiling (s) | "
        "power | assumptions | simulation allowance | QPU radius |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for design in designs(ref):
        n, result = minimum_shots(ref, design)
        observable = result.observables[0]
        radii = None
        if n is not None and design.variance_bound is not None and design.replicas > 1:
            plain = feasible(ref, replace(design, hoeffding_only=True), n)[1].observables[0]
            radii = {
                "detection": not math.isclose(observable.detection_radius, plain.detection_radius, rel_tol=1e-12),
                "power": not math.isclose(observable.power_radius, plain.power_radius, rel_tol=1e-12),
            }
        assumptions = assumption_text(design, radii)
        if n is None:
            lines.append(
                f"| {design.label} | infeasible | - | - | - | - | {assumptions} | "
                f"{observable.simulation_error_radius:.4f} | - |"
            )
            continue
        planner = result.estimated_charge_seconds
        measured = measured_charge(design_inputs(ref, design)[0], n, design.rep_delay, excess, high)
        radius = (observable.detection_radius or 0.0) + (observable.power_radius or 0.0)
        power = "0.8, admitted contract" if design.admitted else "unverified"
        lines.append(
            f"| {design.label} | 2 x {n:,} | {planner:.1f} | {measured} | {math.ceil(planner)} | {power} | "
            f"{assumptions} | {observable.simulation_error_radius:.4f} | {radius:.4f} |"
        )
    pair = sum(t + s * LATENCY_SECONDS + 250e-6 for _, _, t, s in ref.pubs)
    for label, shots, power, assumptions in (
        (
            "extension: Bernstein with V=0.55, R=1",
            extension_shots(ref, "bernstein"),
            "0.8, contract change",
            "exact model; variance <= 0.55",
        ),
        *(
            (
                f"extension: Hoeffding over independent replicas, R={count} {replica_label(ref, count)}",
                extension_shots(ref, "independent", count),
                "0.8, contract change",
                "exact model; independent replicas",
            )
            for count in sorted(ref.replica_sets)
            if count > 1
        ),
        (
            "normal approximation, one-sided alpha 0.05, pooled variance",
            normal_shots(ref),
            "0.8 asymptotic, contract change",
            "exact model; normal limit",
        ),
    ):
        planner = OVERHEAD_SECONDS + shots * pair
        lines.append(
            f"| {label} | 2 x {shots:,} | {planner:.1f} | {measured_charge(ref.pubs, shots, 250e-6, excess, high)} | "
            f"{math.ceil(planner)} | {power} | {assumptions} | 0.0000 | - |"
        )
    record = json.loads(REFERENCE.read_text())
    selected = next(c for c in record["optimization"]["candidates"] if c["name"] == record["optimization"]["selected"])
    lines += [
        "",
        f"Executions count shots summed over the two PUBs; replicas share a shot. The dry run selected "
        f"`{selected['name']}` ({selected['proxy_metadata']['replicas']} replicas, "
        f"{selected['jobs'][0]['pubs'][0]['shots']:,} shots per arm, {selected['estimated_charge_seconds']:.1f} s) "
        f"under a {record['policy']['max_execution_seconds']} s job ceiling."
        if record["optimization"].get("selected")
        else "The reference dry run selected no candidate.",
    ]
    lines += [
        "",
        "**CZ reduction (exact model, Hoeffding, R=1).** Removing k routed CZ scales the contrast by rho^-k; "
        "the two columns take rho from 1 - 4/3 x the Kingston median CZ error and from the reference contrast's "
        "own decay over its CZ count. Cells: shots per arm / planner seconds at 250 us.",
        "",
    ]
    record = json.loads(REFERENCE.read_text())
    cz_count = record["groups"][0]["members"][0]["cz"]
    median_cz = record["backends"][ref.backend]["medians"]["cz_error"]
    retentions = (1 - 4 * median_cz / 3, (c0 / 0.25) ** (1 / cz_count))
    lines += [
        f"| k removed | rho = {retentions[0]:.5f} | rho = {retentions[1]:.5f} |",
        "| --- | --- | --- |",
        *cz_rows(ref, retentions),
        "",
        END,
    ]
    return "\n".join(lines) + "\n"


def splice(text: str, block: str) -> str:
    start, stop = text.index(BEGIN), text.index(END) + len(END) + 1
    return text[:start] + block + text[stop:]


def self_test() -> None:
    """The sizing path reproduces every candidate of the reference dry run: prediction, radii and charge."""
    record = json.loads(REFERENCE.read_text())
    ref = reference()
    design_settings = record["policy"]["design"]
    exact = record.get("exact_model") is not None
    checked = 0
    for candidate in record["optimization"]["candidates"]:
        count = int(candidate["proxy_metadata"]["replicas"])
        prefix = candidate["name"].rsplit("-shots-", 1)[0]
        if exact and prefix not in ref.candidates or not exact and count not in ref.replica_sets:
            continue
        design = Design(
            candidate["name"],
            None if exact else int(design_settings["model_shots"]),
            None if exact else int(record["optimization"]["simulation_comparisons"]),
            count,
            False,
            design_settings.get("replica_variance_bound") if count > 1 else None,
            candidate=prefix if exact else None,
        )
        shots = candidate["jobs"][0]["pubs"][0]["shots"]
        _ok, result = feasible(ref, design, shots)
        mine, theirs = result.observables[0], candidate["observables"][0]
        for key in ("predicted_value", "simulation_error_radius", "detection_radius", "power_radius"):
            if not math.isclose(getattr(mine, key), theirs[key], rel_tol=1e-9, abs_tol=1e-12):
                raise AssertionError(f"{candidate['name']} {key}: {getattr(mine, key)} != {theirs[key]}")
        if not math.isclose(result.estimated_charge_seconds, candidate["estimated_charge_seconds"], rel_tol=1e-9):
            raise AssertionError(f"{candidate['name']}: charge differs from the record")
        checked += 1
    if checked == 0:
        raise AssertionError("no reference candidate was reproduced")
    unbounded = Design("unbounded", None, None, 4, True)
    single = Design("single", None, None)
    if feasible(ref, unbounded, 8192)[1].observables[0].detection_radius != (
        feasible(ref, single, 8192)[1].observables[0].detection_radius
    ):
        raise AssertionError("replicas without a covariance bound must leave the Hoeffding radius unchanged")
    exact_evidence_replay(record)
    pinned_inputs_test()
    print(
        f"n21 usage budget: sizing reproduces {checked} reference candidates' radii and charges; their retained "
        "exact-model checks replay; the billing fit "
        "ignores an unpinned raw job and refuses an altered pinned index or PUB file"
    )


def exact_evidence_replay(record: dict[str, Any]) -> None:
    """validate_exact rerun on every candidate's retained exact and sampled laws reproduces the record."""
    contracts = tuple(
        ObservableContract(
            **{key: value for key, value in contract.items() if key != "terms"},
            terms=tuple(ObservableTerm(t["member"], tuple(t["values"]), t["sign"]) for t in contract["terms"]),
        )
        for contract in record["observable_contracts"]
    )
    exact = record["exact_model"]
    design = record["policy"]["design"]
    for name, evidence in exact["candidates"].items():
        rows = [{key: row[key] for key in ("entry", "replica", "exact", "sampled")} for row in evidence["replicas"]]
        replay = n21_exact_planning.validate_exact(
            rows, contracts, int(design["model_shots"]), float(design["simulation_alpha"])
        )
        if replay["passed"] != evidence["passed"] or not math.isclose(replay["max_gap"], evidence["max_gap"]):
            raise AssertionError(f"{name}: replayed exact-model verdict differs from the record")
        for group in ("arms", "contrasts"):
            for key, row in evidence[group].items():
                for field, value in row.items():
                    if not math.isclose(replay[group][key][field], value, rel_tol=1e-12, abs_tol=1e-15):
                        raise AssertionError(f"{name} {group}/{key}/{field}: replay differs from the record")


def billing(live: Path) -> tuple[list[Job], tuple[float, float], dict[int, list[int]]]:
    jobs = retained_jobs(live)
    return jobs, ceil_interval(jobs), kingston_scheduler_excess(live)


def _mirror(live: Path, destination: Path) -> None:
    """destination holds every pinned run's record and raw job as symbolic links into live."""
    for run, job_id, _digest in BILLING_JOBS:
        (destination / run / "raw").mkdir(parents=True, exist_ok=True)
        os.symlink(live / run / "raw" / job_id, destination / run / "raw" / job_id)
    for run in BILLING_RECORDS:
        os.symlink(live / run / "record.json", destination / run / "record.json")


def _expect_refusal(live: Path, label: str) -> None:
    try:
        billing(live)
    except ValueError:
        return
    raise AssertionError(f"the billing fit read {label}")


def pinned_inputs_test() -> None:
    """The billing fit reads exactly BILLING_JOBS: an extra raw job leaves it unchanged, altered bytes stop it."""
    reference_fit = billing(LIVE)
    if [(job.run, job.job_id) for job in reference_fit[0]] != [(run, job) for run, job, _ in BILLING_JOBS]:
        raise AssertionError("the billing fit's jobs differ from BILLING_JOBS")
    smallest = min(
        BILLING_JOBS,
        key=lambda item: sum(path.stat().st_size for path in (LIVE / item[0] / "raw" / item[1]).iterdir()),
    )
    run, job_id, _digest = smallest
    with tempfile.TemporaryDirectory(prefix="n21-usage-budget-") as scratch:
        mirror = Path(scratch) / "live"
        _mirror(LIVE, mirror)
        if billing(mirror) != reference_fit:
            raise AssertionError("the mirrored pinned inputs give a different billing fit")
        # A job retained later: an unpinned run and an unpinned job beside a pinned one.
        extra = mirror / "2099-01-01T000000.000000Z"
        (extra / "raw").mkdir(parents=True)
        os.symlink(LIVE / run / "raw" / job_id, extra / "raw" / job_id)
        if BILLING_RECORDS.get(run):
            os.symlink(LIVE / run / "record.json", extra / "record.json")
        os.symlink(LIVE / run / "raw" / job_id, mirror / run / "raw" / "unpinned-job")
        if billing(mirror) != reference_fit:
            raise AssertionError("an unpinned raw job changed the billing fit")
        target = mirror / run / "raw" / job_id
        target.unlink()
        shutil.copytree(LIVE / run / "raw" / job_id, target)
        index = target / "index.json"
        original = index.read_bytes()
        index.write_bytes(original.replace(b'"files"', b'"files" ', 1))
        _expect_refusal(mirror, "an index.json that differs from its pinned sha256")
        index.write_bytes(original)
        pub = target / sorted(json.loads(original)["files"])[0]
        pub.write_bytes(pub.read_bytes() + b" ")
        _expect_refusal(mirror, "a raw file that differs from its indexed digest")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    path = args.check or args.write
    text = path.read_text()
    updated = splice(text, render())
    if args.write is not None:
        path.write_text(updated)
        return 0
    if updated != text:
        raise SystemExit(f"{path}: the n21-usage-budget block differs from the retained inputs; run --write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
