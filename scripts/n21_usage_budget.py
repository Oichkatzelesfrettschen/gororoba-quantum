"""QPU-second budget of the n21-feedback-encoded run, derived from retained records.

gororoba_quantum/N21_USAGE_BUDGET.md carries the tables this script renders
between its ``n21-usage-budget`` markers; ``--check`` fails when the note and
the retained inputs disagree, ``--write`` refreshes the block.

Inputs and what each fixes:

- every retained raw job under results/live/*/raw/: per job, the executions
  (sum of PUB shots), the repetition delay, the scheduler circuit duration
  per PUB, the metered ``circuits_execution_time_ns`` and the integer
  ``qpu_charge_time_seconds``. The execution time equals
  sum(shots x (rep_delay + scheduler duration)), and the charge equals
  ceil(execution + c) for one constant c whose admissible interval the
  script intersects over all jobs.
- the same jobs' records: the scheduler duration minus the Target gate-time
  lower bound per PUB, on ibm_kingston, without and with one feed-forward
  stage.
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
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from diagnostic_experiments import family_contracts  # noqa: E402
from experiment_optimizer import (  # noqa: E402
    BudgetContract,
    CandidatePlan,
    CovarianceBound,
    JobCandidate,
    ObservableContract,
    PubPrediction,
    evaluate_candidate,
)

REFERENCE = ROOT / "results/live/2026-10-17T101105.548987Z/record.json"
TARGETS = ROOT / "docs/evidence/heron_platform/targets.json"
# Exact-model dry runs of the same family, oldest calibration first, and the
# Kaggle validation record of the retained 2026-10-17T003834Z ISA.
DRIFT_RECORDS = (
    ROOT / "results/live/2026-10-17T091514.662497Z/record.json",
    ROOT / "results/live/2026-10-17T094344.639211Z/record.json",
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


def retained_jobs() -> list[Job]:
    jobs = []
    for index_path in sorted((ROOT / "results/live").glob("*/raw/*/index.json")):
        directory = index_path.parent
        index = json.loads(index_path.read_text())
        metrics_name = index.get("metrics_latest") or sorted(index["metrics"])[-1]
        metrics = json.loads((directory / metrics_name).read_text())
        metadata = json.loads((directory / "result_metadata.json").read_text())
        rep_delay = metadata["options"]["execution"].get("rep_delay")
        # A job submitted without an explicit rep_delay ran at the backend default.
        rep_delay = 250e-6 if rep_delay is None else float(rep_delay)
        executions = 0
        modeled = 0.0
        for name in index["files"]:
            if not name.startswith("pub_"):
                continue
            pub = json.loads((directory / name).read_text())
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


def kingston_scheduler_excess() -> dict[int, list[int]]:
    """Scheduler circuit duration minus the Target gate-time bound (dt), by feed-forward stage count."""
    excess: dict[int, list[int]] = {}
    for index_path in sorted((ROOT / "results/live").glob("*/raw/*/index.json")):
        run = index_path.parent.parent.parent
        record_path = run / "record.json"
        if not record_path.exists():
            continue
        record = json.loads(record_path.read_text())
        bounds = {
            pub["name"]: (pub.get("target_gate_lower_bound_dt"), pub.get("sequential_stage_count"))
            for pub in record.get("execution_pubs", [])
            if pub.get("backend") == "ibm_kingston"
        }
        for name in json.loads(index_path.read_text())["files"]:
            if not name.startswith("pub_"):
                continue
            pub = json.loads((index_path.parent / name).read_text())
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
    # Exact laws of every replica of each replicated candidate, keyed by replica count.
    replica_sets: dict[int, dict[str, tuple[tuple[float, ...], ...]]]


def reference() -> Reference:
    record = json.loads(REFERENCE.read_text())
    pubs_by_name = {pub["name"]: pub for pub in record["execution_pubs"]}
    candidate = next(
        c for c in record["optimization"]["candidates"] if c["name"] == record["optimization"]["retained_candidate"]
    )
    rows = []
    replica_sets: dict[int, dict[str, tuple[tuple[float, ...], ...]]] = {}
    for pub in candidate["jobs"][0]["pubs"]:
        member = pubs_by_name[pub["name"]]["components"][0]["member"]
        rows.append((pub["name"], member, float(pub["scheduled_seconds"]), int(pub["classical_stage_count"])))
    group = record["groups"][0]
    laws = {member["name"]: tuple(member["replicas"][0]["noisy"]) for member in group["members"]}
    exact = record.get("exact_model")
    if exact is not None:
        laws = {row["entry"]: tuple(row["exact"]) for row in exact["replicas"] if row["replica"] == 0}
        counts = {
            c["name"].rsplit("-shots-", 1)[0]: int(c["proxy_metadata"]["replicas"])
            for c in record["optimization"]["candidates"]
        }
        for name, evidence in sorted(exact.get("candidates", {}).items()):
            members: dict[str, list[tuple[float, ...]]] = {}
            for row in evidence["replicas"]:
                members.setdefault(row["entry"], []).append(tuple(row["exact"]))
            replica_sets.setdefault(counts[name], {k: tuple(v) for k, v in members.items()})
    else:
        # A sampled record retains the optimizer's predicted contrast, not its
        # marginals; the group's laws, mixed toward uniform to that contrast,
        # stand in for them.
        ratio = candidate["observables"][0]["predicted_value"] / contrast(laws)
        laws = {name: toward_uniform(law, ratio) for name, law in laws.items()}
    replica_sets.setdefault(1, {name: (law,) for name, law in laws.items()})
    return Reference(tuple(rows), laws, group["calibration"], group["backend"], replica_sets)


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


def plan(ref: Reference, design: Design, shots: int) -> tuple[CandidatePlan, tuple[ObservableContract, ...]]:
    contracts = family_contracts("n21-feedback-encoded", 0.08, 0.05, 0.8)
    pubs = []
    bounds = []
    for name, member, seconds, stages in ref.pubs:
        replicas = (ref.laws[member],) * design.replicas if design.equal else ref.replica_sets[design.replicas][member]
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
        if design.variance_bound is not None and len(replicas) > 1:
            size = len(replicas)
            bounds.append(
                CovarianceBound(
                    contracts[0].name,
                    name,
                    tuple(f"{member}/r{k}" for k in range(size)),
                    tuple(tuple(design.variance_bound if i == j else 0.0 for j in range(size)) for i in range(size)),
                    "independent replicas",
                )
            )
    job = JobCandidate("kingston/dynamic/1", tuple(pubs), shots, OVERHEAD_SECONDS, 1e9, "declared 2.3 s")
    return CandidatePlan("sizing", (job,), tuple(bounds)), contracts


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


def measured_charge(ref: Reference, shots: int, rep_delay: float, excess: dict[int, list[int]], c_high: float) -> int:
    """ceil(executions x (Target bound + measured scheduler excess + rep_delay) + c) at the interval's top."""
    seconds = 0.0
    for _name, _member, target, stages in ref.pubs:
        seconds += shots * (target + statistics.median(excess[stages]) * DT_SECONDS + rep_delay)
    return math.ceil(seconds + c_high)


def designs(ref: Reference) -> list[Design]:
    sampled = 65536
    return [
        Design("as dry-run: sampled 65,536, 24 plans, Hoeffding, R=1", sampled, 48),
        Design("sampled 65,536, one plan, Hoeffding, R=1", sampled, 2),
        Design("sampled 589,824 (the Kaggle validation's size), one plan, Hoeffding, R=1", 589824, 2),
        Design("exact model, Hoeffding, R=1", None, None),
        *(
            Design(
                f"exact, Cantelli V=0.55, R={count} {replica_label(ref, count)}",
                None,
                None,
                count,
                False,
                VARIANCE_BOUND,
            )
            for count in sorted(ref.replica_sets)
            if count > 1
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


def assumption_text(design: Design) -> str:
    parts = ["exact model" if design.model_shots is None else f"sampled model, {design.model_shots:,} shots"]
    if design.variance_bound is not None and design.replicas > 1:
        parts.append(f"independent replicas, variance <= {design.variance_bound}")
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
    jobs = retained_jobs()
    low, high = ceil_interval(jobs)
    worst = max(abs(job.metered_seconds - job.modeled_seconds) / job.executions for job in jobs)
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
        f"- Jobs: {len(jobs)}, one sub-job each; executions {min(j.executions for j in jobs):,} to "
        f"{max(j.executions for j in jobs):,}.",
        f"- `circuits_execution_time_ns` equals sum(shots x (rep_delay + scheduler circuit duration)) within "
        f"{worst * 1e6:.2f} us per execution on every job.",
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
        assumptions = assumption_text(design)
        if n is None:
            lines.append(
                f"| {design.label} | infeasible | - | - | - | - | {assumptions} | "
                f"{observable.simulation_error_radius:.4f} | - |"
            )
            continue
        planner = result.estimated_charge_seconds
        measured = measured_charge(ref, n, design.rep_delay, excess, high)
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
            f"| {label} | 2 x {shots:,} | {planner:.1f} | {measured_charge(ref, shots, 250e-6, excess, high)} | "
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
        if count not in ref.replica_sets:
            continue
        design = Design(
            candidate["name"],
            None if exact else int(design_settings["model_shots"]),
            None if exact else int(record["optimization"]["simulation_comparisons"]),
            count,
            False,
            design_settings.get("replica_variance_bound") if count > 1 else None,
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
    print(f"n21 usage budget: sizing reproduces {checked} reference candidates' radii and charges")


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
