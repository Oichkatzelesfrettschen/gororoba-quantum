"""Typed provider counters: each quantity carries its value, population, scope, status and source.

A provider result mixes counters of different populations: a requested cap, a billing basis and an observed count
can share a field name (``shots``) while counting different things. A Counter names its population, so arithmetic
that would mix populations raises instead of returning a number.

Photonic populations nest. A source trigger may launch no photon; a detection event is a trigger with at least one
detected photon, which is what Perceval 1.3.1 calls a shot (``perceval/runtime/simulated_computer.py``, ``max_shots``:
"A shot is any event with at least 1 photon"); a photon-filtered sample is a detection event that passes
``min_detected_photons``; a logically accepted outcome is a sample that also passes the experiment's postselection
or heralds. Gate-model populations nest the same way: a circuit execution writes one classical record, and IQM
all-zeros heralding keeps the subset whose pre-circuit measurement reads all zeros. A ratio is defined only from an
inner population to one that contains it, so ``accepted / detected`` is an acceptance fraction and never a per-trial
rate. Incident photons count photons rather than trials and sit outside both chains; they are available only as a
modeled quantity whose assumptions travel with it.

A missing counter stays ``unavailable`` with value None. A requested cap or billing quantity never stands in for
an observed count, and an observed count reached at its cap carries ``terminated_by`` so a censored value reads as
censored.

The Quandela adapter follows the retained-run census of docs/evidence/provider-counter-audit/: per iteration,
``nb_shots_used`` counts detection events and equals the returned samples whenever ``min_detected_photons`` is 1
and the sample budget ends the iteration, and equals ``max_shots`` when the shot budget ends it; an iterated job's
top-level ``shots`` is the job-level ``max_shots`` request, not a total, wherever it equals that request.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Population(StrEnum):
    SOURCE_TRIGGER = "source_trigger"
    INCIDENT_PHOTON = "incident_photon"
    DETECTION_EVENT = "detection_event"
    PHOTON_FILTERED_SAMPLE = "photon_filtered_sample"
    LOGICAL_ACCEPTED = "logical_accepted"
    CIRCUIT_EXECUTION = "circuit_execution"
    HERALDED_EXECUTION = "heralded_execution"
    REQUESTED_CAP = "requested_cap"
    BILLING = "billing"
    TIME_SECONDS = "time_seconds"


class Status(StrEnum):
    OBSERVED = "observed"
    REQUESTED = "requested"
    MODELED = "modeled"
    UNAVAILABLE = "unavailable"


# Each chain lists populations outermost first; a population contains every later member of its chain.
CHAINS: tuple[tuple[Population, ...], ...] = (
    (
        Population.SOURCE_TRIGGER,
        Population.DETECTION_EVENT,
        Population.PHOTON_FILTERED_SAMPLE,
        Population.LOGICAL_ACCEPTED,
    ),
    (Population.CIRCUIT_EXECUTION, Population.HERALDED_EXECUTION, Population.LOGICAL_ACCEPTED),
)
COUNTING = frozenset(p for chain in CHAINS for p in chain) | {Population.INCIDENT_PHOTON}


class CounterError(ValueError):
    pass


@dataclass(frozen=True)
class Counter:
    """One provider quantity. scope names the unit it covers (``iteration:3``, ``job``, ``circuit:0``) so a sum can
    prove its terms disjoint; source names the field or file it came from."""

    name: str
    value: int | float | None
    population: Population
    scope: str
    status: Status
    source: str
    assumptions: tuple[str, ...] = ()
    terminated_by: str | None = None

    def __post_init__(self) -> None:
        if self.status is Status.UNAVAILABLE:
            if self.value is not None:
                raise CounterError(f"{self.name}: an unavailable counter carries no value")
            return
        if self.value is None:
            raise CounterError(f"{self.name}: a {self.status.value} counter needs a value")
        if isinstance(self.value, bool) or not isinstance(self.value, int | float):
            raise CounterError(f"{self.name}: value {self.value!r} is not a number")
        if not math.isfinite(self.value) or self.value < 0:
            raise CounterError(f"{self.name}: value {self.value!r} must be finite and non-negative")
        integral = self.population in COUNTING or self.population is Population.REQUESTED_CAP
        if integral and self.status is not Status.MODELED and not isinstance(self.value, int):
            raise CounterError(f"{self.name}: an {self.status.value} count must be an integer")
        if self.status is Status.MODELED and not self.assumptions:
            raise CounterError(f"{self.name}: a modeled quantity must state its assumptions")
        if self.population is Population.REQUESTED_CAP and self.status is not Status.REQUESTED:
            raise CounterError(f"{self.name}: a requested cap has status requested")
        if self.status is Status.REQUESTED and self.population is not Population.REQUESTED_CAP:
            raise CounterError(f"{self.name}: only a requested cap has status requested")

    @property
    def available(self) -> bool:
        return self.status is not Status.UNAVAILABLE

    def record(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "name": self.name,
            "value": self.value,
            "population": self.population.value,
            "scope": self.scope,
            "status": self.status.value,
            "source": self.source,
        }
        if self.assumptions:
            out["assumptions"] = list(self.assumptions)
        if self.terminated_by is not None:
            out["terminated_by"] = self.terminated_by
        return out


def unavailable(name: str, population: Population, scope: str, source: str) -> Counter:
    return Counter(name, None, population, scope, Status.UNAVAILABLE, source)


def contains(outer: Population, inner: Population) -> bool:
    """True when every member of inner is a member of outer."""
    return any(outer in chain and inner in chain and chain.index(outer) <= chain.index(inner) for chain in CHAINS)


@dataclass(frozen=True)
class Ratio:
    """numerator / denominator with both populations and the selection that maps one onto the other."""

    value: float | None
    numerator: Counter
    denominator: Counter
    selection: str
    reason: str | None = None

    def record(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "value": self.value,
            "numerator": self.numerator.record(),
            "denominator": self.denominator.record(),
            "selection": self.selection,
        }
        if self.reason is not None:
            out["reason"] = self.reason
        return out


def ratio(numerator: Counter, denominator: Counter, selection: str) -> Ratio:
    """The fraction of denominator's members that numerator keeps under selection.

    An unavailable or zero denominator, or an unavailable numerator, gives value None with a reason. A requested
    cap, billing quantity, time or incident-photon count is never a denominator of a population fraction, and the
    numerator's population must lie inside the denominator's; both raise.
    """
    for counter in (numerator, denominator):
        if counter.population not in COUNTING or counter.population is Population.INCIDENT_PHOTON:
            raise CounterError(f"{counter.name}: {counter.population.value} is not a trial population")
    if not contains(denominator.population, numerator.population):
        raise CounterError(
            f"{numerator.population.value} is not a subset of {denominator.population.value}; "
            f"{numerator.name} / {denominator.name} is not a population fraction"
        )
    if numerator.scope != denominator.scope:
        raise CounterError(f"{numerator.name} covers {numerator.scope} and {denominator.name} {denominator.scope}")
    if not numerator.available or not denominator.available:
        return Ratio(None, numerator, denominator, selection, "a counter is unavailable")
    if denominator.value == 0:
        return Ratio(None, numerator, denominator, selection, "the denominator is zero")
    if numerator.value is None or denominator.value is None:  # narrowed for mypy; available implies a value
        raise CounterError("an available counter lacks its value")
    if numerator.value > denominator.value:
        raise CounterError(f"{numerator.name} {numerator.value} exceeds {denominator.name} {denominator.value}")
    return Ratio(numerator.value / denominator.value, numerator, denominator, selection)


def total(counters: Sequence[Counter], name: str, scope: str) -> Counter:
    """The sum of counters that share one population and status over disjoint scopes.

    Any unavailable term makes the total unavailable. A modeled total keeps the union of the terms' assumptions; a
    total of requested caps stays a requested cap, so cap and billing arithmetic never merges with observed counts.
    """
    if not counters:
        raise CounterError(f"{name}: a total needs at least one term")
    populations = {c.population for c in counters}
    statuses = {c.status for c in counters if c.available}
    if len(populations) != 1:
        raise CounterError(f"{name}: terms mix populations {sorted(p.value for p in populations)}")
    if len(statuses) > 1:
        raise CounterError(f"{name}: terms mix statuses {sorted(s.value for s in statuses)}")
    scopes = [c.scope for c in counters]
    if len(set(scopes)) != len(scopes):
        raise CounterError(f"{name}: terms repeat a scope, so they are not disjoint")
    (population,) = populations
    source = "sum of " + ", ".join(sorted({c.source for c in counters}))
    if any(not c.available for c in counters) or not statuses:
        return unavailable(name, population, scope, source)
    (status,) = statuses
    values = [c.value for c in counters if c.value is not None]
    value: int | float = sum(values) if all(isinstance(v, int) for v in values) else math.fsum(values)
    assumptions = tuple(sorted({a for c in counters for a in c.assumptions}))
    return Counter(name, value, population, scope, status, source, assumptions)


# --- Quandela ------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class IterationCounters:
    """The counters of one Quandela result entry and the request that bounded it."""

    detection_events: Counter
    samples: Counter
    max_shots: Counter
    max_samples: Counter
    source_triggers: Counter
    accepted: Counter | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    def acceptance(self) -> Ratio:
        """Samples per detection event: the photon-number filter's acceptance, not a per-trial rate."""
        return ratio(self.samples, self.detection_events, "min_detected_photons filter")

    def logical_acceptance(self) -> Ratio | None:
        if self.accepted is None:
            return None
        return ratio(self.accepted, self.samples, "logical postselection of the samples")

    def record(self) -> dict[str, Any]:
        out = {
            key: getattr(self, key).record()
            for key in ("detection_events", "samples", "max_shots", "max_samples", "source_triggers")
        }
        out["acceptance"] = self.acceptance().record()
        if self.accepted is not None:
            out["accepted"] = self.accepted.record()
            logical = self.logical_acceptance()
            if logical is not None:
                out["logical_acceptance"] = logical.record()
        return out


def _count(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def quandela_iteration(
    entry: Mapping[str, Any],
    samples: int,
    scope: str,
    *,
    max_shots: int | None,
    max_samples: int | None,
    accepted: int | None = None,
) -> IterationCounters:
    """Counters of one results_list entry (or a single result) of a Quandela job.

    samples is the entry's returned BSCount total; max_shots and max_samples are the iteration's request (None when
    the request does not state one). accepted, when given, counts the samples a logical postselection keeps.
    nb_shots_used is the detection-event count, censored at max_shots: an iteration that reports its whole
    max_shots ended by the shot budget, one that returned max_samples ended by the sample budget, and one that
    reached both reads "both".
    """
    reported = _count(entry.get("nb_shots_used"))
    returned = _count(samples)
    if returned is None:
        raise CounterError(f"{scope}: samples {samples!r} is not a count")
    shot_cap = reported is not None and max_shots is not None and reported >= max_shots
    sample_cap = max_samples is not None and returned >= max_samples
    # An iteration that reaches both caps at once does not say which one stopped it.
    terminated = {(True, True): "both", (True, False): "max_shots", (False, True): "max_samples"}.get(
        (shot_cap, sample_cap)
    )
    detection = (
        Counter(
            "nb_shots_used",
            reported,
            Population.DETECTION_EVENT,
            scope,
            Status.OBSERVED,
            "result entry nb_shots_used",
            terminated_by=terminated,
        )
        if reported is not None
        else unavailable("nb_shots_used", Population.DETECTION_EVENT, scope, "result entry nb_shots_used (absent)")
    )
    if reported is not None and returned > reported:
        raise CounterError(f"{scope}: {returned} samples exceed {reported} detection events")

    def cap(name: str, value: int | None) -> Counter:
        if value is None:
            return unavailable(name, Population.REQUESTED_CAP, scope, f"iteration request {name} (absent)")
        return Counter(name, value, Population.REQUESTED_CAP, scope, Status.REQUESTED, f"iteration request {name}")

    logical = None
    if accepted is not None:
        logical = Counter(
            "accepted", accepted, Population.LOGICAL_ACCEPTED, scope, Status.OBSERVED, "analysis postselection"
        )
    return IterationCounters(
        detection_events=detection,
        samples=Counter(
            "samples", returned, Population.PHOTON_FILTERED_SAMPLE, scope, Status.OBSERVED, "result entry BSCount"
        ),
        max_shots=cap("max_shots", max_shots),
        max_samples=cap("max_samples", max_samples),
        source_triggers=unavailable(
            "source_triggers", Population.SOURCE_TRIGGER, scope, "no Quandela result field counts source pulses"
        ),
        accepted=logical,
        extra={key: entry.get(key) for key in ("physical_perf", "logical_perf", "global_perf") if key in entry},
    )


def quandela_top_level_shots(outer: Mapping[str, Any], iterated: bool, job_max_shots: int | None) -> Counter:
    """The top-level ``shots`` of a Quandela job answer.

    A single job's top-level shots is that job's detection-event count. An iterated job's top-level shots equals
    the job body's job-level max_shots on every retained iterated job but one, a one-iteration list whose value
    equals that iteration's nb_shots_used instead; so an iterated value is a requested cap only when it equals
    job_max_shots, and otherwise its population is unidentified and the counter is unavailable.
    """
    value = _count(outer.get("shots"))
    if not iterated:
        if value is None:
            return unavailable("shots", Population.DETECTION_EVENT, "job", "job answer shots (absent)")
        return Counter("shots", value, Population.DETECTION_EVENT, "job", Status.OBSERVED, "job answer shots")
    if value is None or job_max_shots is None or value != job_max_shots:
        return unavailable(
            "shots", Population.REQUESTED_CAP, "job", "job answer shots differs from the job body's max_shots"
        )
    return Counter("shots", value, Population.REQUESTED_CAP, "job", Status.REQUESTED, "job answer shots")


@dataclass(frozen=True)
class QuandelaRecord:
    """Typed counters of one collected Quandela record (qd_platform.collect's results.json).

    iterations holds one IterationCounters per result entry that carries counts, in result order, and None for an
    entry a partial answer left uncounted; top_level is the answer's top-level shots; detection_events totals the
    counted iterations' detection events, unavailable unless every iteration was counted.
    """

    iterated: bool
    partial: bool
    iterations: tuple[IterationCounters | None, ...]
    top_level: Counter
    detection_events: Counter

    def record(self) -> dict[str, Any]:
        return {
            "iterated": self.iterated,
            "partial": self.partial,
            "iterations": [None if i is None else i.record() for i in self.iterations],
            "top_level": self.top_level.record(),
            "detection_events": self.detection_events.record(),
        }


def quandela_record(results: Mapping[str, Any], budgets: Sequence[tuple[int, int]]) -> QuandelaRecord:
    """The typed view of a collected Quandela record, leaving the record's verbatim fields untouched.

    budgets lists each iteration's (max_samples, max_shots), qd_platform.iteration_budgets of the run's cases.json.
    The job body's job-level max_shots equals the largest of them on every retained iterated job, so that value
    classifies the top-level shots. A single job reports its detection events as the top-level shots. An answer
    whose payload carried no counts (a provider error or a partial job) leaves every sample counter unavailable
    rather than zero, although the collected record writes samples 0 for it.
    """
    partial = results.get("partial") is True
    entries = results.get("iterations")
    iterated = isinstance(entries, list)
    caps = [shots for _, shots in budgets]
    job_max_shots = max(caps) if caps else None
    top = quandela_top_level_shots(results, iterated, job_max_shots)
    if not iterated:
        (max_samples, max_shots) = budgets[0] if budgets else (None, None)
        counted = "counts" in results and isinstance(results.get("samples"), int) and bool(results.get("counts"))
        if partial and not counted:
            # A partial answer without counts reports shots 0 as a default, not as an observed detection count.
            top = unavailable("shots", Population.DETECTION_EVENT, "job", "partial answer without counts")
            iteration: IterationCounters | None = None
        else:
            # A single answer's result fields carry no nb_shots_used; the top-level shots is its detection count.
            entry = {"nb_shots_used": top.value} if top.available else {}
            iteration = quandela_iteration(
                entry, int(results["samples"]), "iteration:0", max_shots=max_shots, max_samples=max_samples
            )
        iterations: tuple[IterationCounters | None, ...] = (iteration,)
    else:
        if len(entries or []) > len(budgets) or (not partial and len(entries or []) != len(budgets)):
            raise CounterError(f"{len(entries or [])} result entries for {len(budgets)} iteration budgets")
        built: list[IterationCounters | None] = []
        for index, entry in enumerate(entries or []):
            if "counts" not in entry:
                built.append(None)
                continue
            max_samples, max_shots = budgets[index]
            fields = entry.get("result_fields") if isinstance(entry.get("result_fields"), Mapping) else {}
            built.append(
                quandela_iteration(
                    fields, int(entry["samples"]), f"iteration:{index}", max_shots=max_shots, max_samples=max_samples
                )
            )
        iterations = tuple(built)
    terms = [
        i.detection_events
        if i is not None
        else unavailable("nb_shots_used", Population.DETECTION_EVENT, f"iteration:{k}", "uncounted entry")
        for k, i in enumerate(iterations)
    ]
    detection = (
        total(terms, "detection_events", "job")
        if terms
        else unavailable("detection_events", Population.DETECTION_EVENT, "job", "no result entry")
    )
    return QuandelaRecord(iterated, partial, iterations, top, detection)


def exposure_seconds(
    samples: int, physical_perf: Any, clock_mhz: Any, duration_s: Any, scope: str
) -> dict[str, Counter]:
    """Detector-exposure scenarios for a dark-count expectation.

    No Quandela document defines the exposure that multiplies a catalogue dark rate. ``physical_perf_model`` is
    samples / (physical_perf x clock), which takes one trial per source pulse at the catalogue clock;
    ``job_duration`` is the job's wall time, an upper bound that includes compilation and overhead; ``none``
    is zero exposure. Each is a modeled quantity, and a conclusion counts as exposure-robust only when it
    holds under all three.
    """
    out = {
        "none": Counter(
            "exposure_s", 0.0, Population.TIME_SECONDS, scope, Status.MODELED, "scenario", ("no dark exposure",)
        )
    }
    if isinstance(physical_perf, int | float) and isinstance(clock_mhz, int | float) and physical_perf > 0:
        out["physical_perf_model"] = Counter(
            "exposure_s",
            samples / (float(physical_perf) * float(clock_mhz) * 1e6),
            Population.TIME_SECONDS,
            scope,
            Status.MODELED,
            "samples / (physical_perf x clock)",
            ("one trial per source pulse at the catalogue clock", "physical_perf is the per-trial sample fraction"),
        )
    else:
        out["physical_perf_model"] = unavailable(
            "exposure_s", Population.TIME_SECONDS, scope, "physical_perf or clock missing"
        )
    if isinstance(duration_s, int | float) and not isinstance(duration_s, bool) and duration_s >= 0:
        out["job_duration"] = Counter(
            "exposure_s",
            float(duration_s),
            Population.TIME_SECONDS,
            scope,
            Status.MODELED,
            "job answer duration",
            ("the detectors integrate dark counts over the whole job wall time",),
        )
    else:
        out["job_duration"] = unavailable("exposure_s", Population.TIME_SECONDS, scope, "job duration missing")
    return out


def robust(verdicts: Iterable[Any]) -> bool:
    """True when every scenario's verdict is available and they agree."""
    values = list(verdicts)
    return bool(values) and None not in values and all(v == values[0] for v in values)
