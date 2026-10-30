"""Calibration-adaptive approval envelope for the measurement-sequence family on ibm_kingston.

An envelope approval binds a constructor, not one calibration's values: the layout is `layout_rule` of the snapshot
the submitting process reads, and the sent plan equals the constructor's output on that snapshot. The design, its
falsifiers and the review history are in docs/design/measurement-sequence-adaptive-envelope.md.

Every function here is pure over its arguments, so a gate replays it from the retained canonical snapshot bytes.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from typing import Any

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

import measurement_sequence_scatter as scatter

ENVELOPE_SCHEMA = "msq-envelope-v2"
ENVELOPE_SCHEMA_V1 = "msq-envelope-v1"
SNAPSHOT_SCHEMA = "ibm-canonical-snapshot-v1"
ENVELOPE_FILE = "envelope.json"
# The Heron r2 backends an envelope plan may run on. The plan records the one it chose in its contract, which the
# approval binds, so a binding dry run on another backend fails the approved-record comparison.
ENVELOPE_BACKENDS = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
# A contract written before the backend became a planned field ran on ibm_kingston.
LEGACY_ENVELOPE_BACKEND = "ibm_kingston"

# The layout rule keeps the scatter-floor qubit screen (measurement_sequence_scatter.eligible) and adds
# prob_meas1_prep0, the calibration's ground-state readout error: a readout-channel screen, while the shot-history
# bound comes from the in-job reset controls.
RULE_MAX_PROB_MEAS1_PREP0 = 0.02
# Kept qubits are at least this many edges apart in the CZ coupling graph: neither adjacent nor sharing a neighbor.
RULE_MIN_GRAPH_DISTANCE = 3
WIDTH_TIERS = (32, 24, 16)
# layout_rule_v2 treats summed readout errors within this many units as equal; a readout error is a probability
# reported to about 1e-5, so no calibration difference below it separates two layouts.
TIE_TOLERANCE = 1e-9

# A plan whose digest changes this many times between consecutive snapshots refuses on the next change.
MAX_REPLANS = 3

# Retained Kingston failures all report 1305 (results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md): a delay that never
# executed reports no circuit time and bills at most the job overhead, an overrun ceiling bills executed shots.
FALLBACK_REP_DELAY_S = 50e-6
FALLBACK_TIMEOUT_CODE = 1305
FALLBACK_DELAY_CODES = (1602, 8030)
FALLBACK_MAX_BILLED_S = 3.0

# Schema v2 replaces the fixed 20 us and 50 us delays with a ladder the plan climbs and derives each attempt's
# execution ceiling from the planner charge. The 20 us floor is IBM's changelog floor for Heron r2;
# configuration().rep_delay_range reads [0, 2 ms] on ibm_kingston and bounds nothing here.
REP_DELAY_MIN_S = 20e-6
REP_DELAY_MAX_S = 60e-6
REP_DELAY_STEP_S = 10e-6
REP_DELAY_LADDER_S = tuple(
    round(REP_DELAY_MIN_S + k * REP_DELAY_STEP_S, 12)
    for k in range(round((REP_DELAY_MAX_S - REP_DELAY_MIN_S) / REP_DELAY_STEP_S) + 1)
)
# The ceiling at a delay is CEILING_FACTOR times the planner charge plus PER_SHOT_RESIDUAL_S per shot, the gap
# between billed charge and planner charge measured on the retained width-32 run.
CEILING_FACTOR = 1.5
PER_SHOT_RESIDUAL_S = 9e-6
# The approved total QPU charge C of an envelope, owner-approved per case.
CAP_MIN_S = 5.0
CAP_MAX_S = 240.0


class EnvelopeError(ValueError):
    """An envelope input violates the envelope contract."""


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, complex):
        return [value.real, value.imag]
    raise TypeError(f"no canonical JSON form for {type(value).__name__}")


def canonical_json(value: Any) -> bytes:
    """Sorted, compact JSON bytes; the one serialization every envelope digest reads."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=_json_default, allow_nan=False).encode()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_snapshot(configuration: Mapping[str, Any], properties: Mapping[str, Any], pending_jobs: int) -> bytes:
    """The canonical bytes of one backend read: configuration and properties as the service returns them."""
    if type(pending_jobs) is not int or pending_jobs < 0:
        raise EnvelopeError(f"pending_jobs must be a nonnegative int, got {pending_jobs!r}")
    return canonical_json(
        {
            "schema": SNAPSHOT_SCHEMA,
            "configuration": configuration,
            "properties": properties,
            "pending_jobs": pending_jobs,
        }
    )


def coupling_distances(edges: Iterable[tuple[int, int]], source: int, limit: int) -> dict[int, int]:
    """Undirected breadth-first distances from source, up to limit edges."""
    adjacency: dict[int, set[int]] = {}
    for a, b in edges:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    distances = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        if distances[node] >= limit:
            continue
        for neighbor in sorted(adjacency.get(node, ())):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances


def calibration_from_snapshot(snapshot: Any) -> dict[str, Any]:
    """The scatter screen's per-qubit calibration with each qubit's prob_meas1_prep0 added."""
    calibration = scatter.calibration_from_snapshot(snapshot)
    for q, row in calibration["qubits"].items():
        value = snapshot.properties.qubit_property(q).get("prob_meas1_prep0", (None,))[0]
        row["prob_meas1_prep0"] = None if value is None else float(value)
    return calibration


def calibration_from_canonical(data: bytes) -> dict[str, Any]:
    """The layout rule's inputs rebuilt from canonical snapshot bytes alone, as the rebuild gate replays them.

    Rows come from the properties (readout error, sx gate error, T1, T2, prob_meas1_prep0), which
    live_run.check_snapshot_matches_properties holds equal to the Target's; the edges are the cz couplers of the
    runtime Target built from the configuration and properties; a qubit is excluded when the properties name it
    faulty or not operational or name one of its single-qubit gates faulty. The live snapshot also excludes qubits
    outside live_run.QUALITY, all of which the rule's tighter thresholds reject, so the rule returns the same layout
    on both.
    """
    from qiskit_ibm_runtime.models import BackendConfiguration, BackendProperties
    from qiskit_ibm_runtime.models.exceptions import BackendPropertyError
    from qiskit_ibm_runtime.utils.backend_converter import convert_to_target

    document = json.loads(data)
    if document.get("schema") != SNAPSHOT_SCHEMA:
        raise EnvelopeError(f"not a {SNAPSHOT_SCHEMA} snapshot")
    properties = BackendProperties.from_dict(document["properties"])
    count = int(document["configuration"]["n_qubits"])
    faulty = set(properties.faulty_qubits())
    faulty |= {q for gate in properties.faulty_gates() if gate.gate != "cz" for q in gate.qubits}

    def error(read: Any) -> float | None:
        # An excluded qubit can lack a value; it never reaches the rule's thresholds.
        try:
            return float(read())
        except BackendPropertyError:
            return None

    rows: dict[int, dict[str, float | None]] = {}
    excluded = []
    for q in range(count):
        if q in faulty or not properties.is_qubit_operational(q):
            excluded.append(q)
        values = properties.qubit_property(q)
        rows[q] = {
            "readout_error": error(lambda q=q: properties.readout_error(q)),
            "sx_error": error(lambda q=q: properties.gate_error("sx", q)),
            "t1_s": values.get("T1", (None,))[0],
            "t2_s": values.get("T2", (None,))[0],
            "prob_meas1_prep0": values.get("prob_meas1_prep0", (None,))[0],
        }
    # The live rule reads its edges from the runtime's Target, which drops the faulty orientations of cz; the replay
    # builds that Target from the same configuration and properties.
    target = convert_to_target(BackendConfiguration.from_dict(document["configuration"]), properties)
    edges = sorted({(min(a, b), max(a, b)) for a, b in target["cz"]})
    return {"qubits": rows, "edges": [list(e) for e in edges], "excluded": sorted(excluded)}


def qubit_eligibility(row: Mapping[str, float | None]) -> str | None:
    """The first rule threshold a qubit's calibration fails, or None when it is eligible; a missing value fails."""
    if not scatter.eligible(dict(row)):
        return "outside the scatter screen (readout, sx, T1, T2)"
    value = row.get("prob_meas1_prep0")
    if value is None or not math.isfinite(value):
        return "missing prob_meas1_prep0"
    if value > RULE_MAX_PROB_MEAS1_PREP0:
        return f"prob_meas1_prep0 {value:.6g}"
    return None


def layout_rule(
    qubits: Mapping[int, Mapping[str, float | None]],
    excluded: Iterable[int],
    edges: Iterable[tuple[int, int]],
    width: int,
) -> list[int]:
    """The layout of width qubits the envelope places on one snapshot, in ascending qubit index.

    Eligible qubits (qubit_eligibility, not excluded by the snapshot's exclusion policy) are scanned in ascending
    readout error with ties by index; a qubit is kept when its CZ-graph distance to every kept qubit is at least
    RULE_MIN_GRAPH_DISTANCE. The kept set returns sorted by index, so a reordering of readout errors among the same
    kept qubits leaves the plan unchanged. Fewer than width keepable qubits raise EnvelopeError.
    """
    if width not in WIDTH_TIERS:
        raise EnvelopeError(f"width {width} is not an envelope tier {WIDTH_TIERS}")
    edge_list = sorted({(min(a, b), max(a, b)) for a, b in edges})
    blocked = set(excluded)
    eligible = sorted(
        (q for q, values in qubits.items() if q not in blocked and qubit_eligibility(values) is None),
        key=lambda q: (float(qubits[q]["readout_error"] or 0.0), q),
    )
    kept: list[int] = []
    near: set[int] = set()
    for q in eligible:
        if q in near:
            continue
        kept.append(q)
        if len(kept) == width:
            return sorted(kept)
        near.update(coupling_distances(edge_list, q, RULE_MIN_GRAPH_DISTANCE - 1))
    raise EnvelopeError(f"only {len(kept)} qubits satisfy the layout rule; width {width} needs {width}")


def _packing(
    eligible: list[int], conflicts: list[tuple[int, int]], cost: np.ndarray, width: int | None, fixed: dict[int, int]
) -> Any:
    """milp over binary x_q: minimize cost.x with no conflict pair both kept; width None maximizes the count."""
    n = len(eligible)
    position = {q: i for i, q in enumerate(eligible)}
    rows = []
    for a, b in conflicts:
        row = np.zeros(n)
        row[position[a]] = row[position[b]] = 1.0
        rows.append(row)
    constraints = [LinearConstraint(np.array(rows), -np.inf, 1.0)] if rows else []
    if width is not None:
        constraints.append(LinearConstraint(np.ones((1, n)), width, width))
    lower, upper = np.zeros(n), np.ones(n)
    for q, value in fixed.items():
        lower[position[q]] = upper[position[q]] = value
    return milp(
        cost if width is not None else -np.ones(n),
        constraints=constraints,
        integrality=np.ones(n),
        bounds=Bounds(lower, upper),
    )


def layout_rule_v2(
    qubits: Mapping[int, Mapping[str, float | None]],
    excluded: Iterable[int],
    edges: Iterable[tuple[int, int]],
    width: int,
) -> list[int]:
    """The width-qubit layout of schema v2, in ascending qubit index: the packing of lowest summed readout error.

    The candidates are the qubits layout_rule screens (qubit_eligibility, exclusions). A subset is admissible when
    every pair sits at CZ-graph distance >= RULE_MIN_GRAPH_DISTANCE; among the admissible width-subsets the rule
    minimizes the summed readout_error, and sums that differ by at most TIE_TOLERANCE tie. A tie resolves to the
    lexicographically smallest sorted index tuple: ascending qubit by qubit, a qubit joins the layout when some
    optimal subset extends the kept prefix with it. No admissible width-subset raises EnvelopeError naming the
    maximum packing size.
    """
    if width not in WIDTH_TIERS:
        raise EnvelopeError(f"width {width} is not an envelope tier {WIDTH_TIERS}")
    return packed_layout(qubits, excluded, edges, width)


def packed_layout(
    qubits: Mapping[int, Mapping[str, float | None]],
    excluded: Iterable[int],
    edges: Iterable[tuple[int, int]],
    width: int,
) -> list[int]:
    """layout_rule_v2's packing for any positive width; the tier check belongs to the rule, not the packing."""
    edge_list = sorted({(min(a, b), max(a, b)) for a, b in edges})
    blocked = set(excluded)
    eligible = sorted(q for q, values in qubits.items() if q not in blocked and qubit_eligibility(values) is None)
    eligible_set = set(eligible)
    conflicts = sorted(
        {
            (min(q, other), max(q, other))
            for q in eligible
            for other in coupling_distances(edge_list, q, RULE_MIN_GRAPH_DISTANCE - 1)
            if other != q and other in eligible_set
        }
    )
    cost = np.array([float(qubits[q]["readout_error"] or 0.0) for q in eligible])
    best = _packing(eligible, conflicts, cost, width, {}) if len(eligible) >= width else None
    if best is None or best.x is None:
        packing = _packing(eligible, conflicts, cost, None, {}) if eligible else None
        size = 0 if packing is None or packing.x is None else int(round(float(packing.x.sum())))
        raise EnvelopeError(f"only {size} qubits satisfy the layout rule; width {width} needs {width}")
    limit = float(best.fun) + TIE_TOLERANCE
    kept: dict[int, int] = {}
    for q in eligible:
        if sum(kept.values()) == width:
            break
        trial = _packing(eligible, conflicts, cost, width, {**kept, q: 1})
        if trial.x is not None and float(trial.fun) <= limit:
            kept[q] = 1
        else:
            kept[q] = 0
    return sorted(q for q, value in kept.items() if value)


def place_layout(
    schema: str,
    qubits: Mapping[int, Mapping[str, float | None]],
    excluded: Iterable[int],
    edges: Iterable[tuple[int, int]],
    width: int,
) -> list[int]:
    """The layout rule the envelope schema names: layout_rule for v1 records, layout_rule_v2 for v2."""
    if schema == ENVELOPE_SCHEMA_V1:
        return layout_rule(qubits, excluded, edges, width)
    if schema == ENVELOPE_SCHEMA:
        return layout_rule_v2(qubits, excluded, edges, width)
    raise EnvelopeError(f"unknown envelope schema {schema!r}")


def plan_digest(plan: Mapping[str, Any]) -> str:
    """sha256 of the full submission plan: layout, QPY digest, PUB and register manifest, options, delay, price."""
    required = {"layout", "qpy_sha256", "execution_pubs", "sampler_options", "rep_delay", "shots", "planner_seconds"}
    missing = sorted(required - set(plan))
    if missing:
        raise EnvelopeError(f"a submission plan needs {missing}")
    return sha256_hex(canonical_json(dict(plan)))


def count_replans(digests: list[str]) -> int:
    """Changes between consecutive plan digests; more than MAX_REPLANS refuses the attempt."""
    changes = sum(1 for before, after in zip(digests, digests[1:], strict=False) if before != after)
    if changes > MAX_REPLANS:
        raise EnvelopeError(f"the plan changed {changes} times between snapshots; the envelope allows {MAX_REPLANS}")
    return changes


def fallback_permitted(
    status: str, error_code: int | None, circuits_execution_time_ns: int | None, billed_seconds: float | None
) -> bool:
    """Whether a terminal attempt-1 job authorizes the 50 us attempt 2.

    A 1602 or 8030 names an unsupported delay. A 1305 authorizes the fallback only when the job executed no circuit
    and billed at most FALLBACK_MAX_BILLED_S, the signature of a delay that never ran; a 1305 with executed circuit
    time is an overrun ceiling. Every other terminal state ends the envelope.
    """
    if status != "ERROR" or error_code is None:
        return False
    if error_code in FALLBACK_DELAY_CODES:
        return True
    if error_code != FALLBACK_TIMEOUT_CODE:
        return False
    if circuits_execution_time_ns not in (None, 0):
        return False
    return billed_seconds is not None and billed_seconds <= FALLBACK_MAX_BILLED_S


def attempt_admission(
    attempt: int,
    remaining_seconds: float,
    reserve_seconds: float,
    envelope_cap: float,
    ceiling: float,
    earlier_attempt_seconds: float = 0.0,
    earlier_unsettled: bool = False,
) -> list[str]:
    """Reasons an attempt is refused under the envelope's aggregate cap; empty admits it.

    Attempt 1 needs the whole cap within the remaining quota minus the reserve. Attempt 2 needs attempt 1's
    attributed final charge (its ceiling while the charge is unattributed, earlier_attempt_seconds) plus its own
    ceiling within the cap. Within the remaining quota minus the reserve it needs its own ceiling, plus attempt 1's
    seconds while that charge is unsettled, since the quota the service reports has not yet deducted it.
    """
    if attempt not in (1, 2):
        return [f"the envelope has attempts 1 and 2, not {attempt!r}"]
    values = (remaining_seconds, reserve_seconds, envelope_cap, ceiling, earlier_attempt_seconds)
    if any(not math.isfinite(v) or v < 0 for v in values):
        return [f"admission inputs must be finite and nonnegative: {values}"]
    if attempt == 1 and earlier_attempt_seconds != 0.0:
        return ["attempt 1 has no earlier attempt"]
    reasons = []
    if earlier_attempt_seconds + ceiling > envelope_cap:
        reasons.append(
            f"earlier {earlier_attempt_seconds:g} s plus ceiling {ceiling:g} s exceeds envelope_cap {envelope_cap:g} s"
        )
    needed = envelope_cap if attempt == 1 else ceiling + (earlier_attempt_seconds if earlier_unsettled else 0.0)
    if remaining_seconds - reserve_seconds < needed:
        reasons.append(
            f"remaining {remaining_seconds:g} s minus reserve {reserve_seconds:g} s is below the {needed:g} s needed"
        )
    return reasons


def delay_key(delay: float) -> str:
    """The contract's spelling of a ladder delay: repr of the float seconds, such as "2e-05" for 20 us."""
    return repr(float(delay))


def attempt_ceiling(planner_seconds: float, total_shots: int) -> int:
    """The execution ceiling of one attempt: ceil(CEILING_FACTOR * (planner charge + PER_SHOT_RESIDUAL_S per shot))."""
    if not math.isfinite(planner_seconds) or planner_seconds < 0 or type(total_shots) is not int or total_shots < 0:
        raise EnvelopeError(f"ceiling inputs must be a finite nonnegative charge and shot count: {planner_seconds!r}")
    return math.ceil(CEILING_FACTOR * (planner_seconds + PER_SHOT_RESIDUAL_S * total_shots))


def ladder_ceilings(planner_seconds: Mapping[str, float], total_shots: int) -> dict[str, int]:
    """Each ladder step's ceiling from its planner charge, keyed by delay_key in ladder order."""
    expected = [delay_key(d) for d in REP_DELAY_LADDER_S]
    if list(planner_seconds) != expected:
        raise EnvelopeError(f"planner charges must cover the ladder {expected}, got {list(planner_seconds)}")
    return {key: attempt_ceiling(planner_seconds[key], total_shots) for key in expected}


def contract_refusals(cap: float | None, ceilings: Mapping[str, int], bound: float | None) -> list[str]:
    """Reasons a v2 contract is refused at the dry run: the total cap C, its first ceiling and the ceiling bound."""
    reasons = []
    first = ceilings[delay_key(REP_DELAY_LADDER_S[0])]
    if cap is None or not math.isfinite(cap) or not CAP_MIN_S <= cap <= CAP_MAX_S:
        reasons.append(f"the total cap {cap!r} s is outside [{CAP_MIN_S:g}, {CAP_MAX_S:g}] s")
    elif first > cap:
        reasons.append(f"the first ceiling {first} s exceeds the total cap {cap:g} s")
    if bound is not None and first > bound:
        reasons.append(f"the first ceiling {first} s exceeds the ceiling bound {bound:g} s")
    return reasons


def attempt_admission_v2(
    attempt: int,
    remaining_seconds: float,
    reserve_seconds: float,
    envelope_cap: float,
    ceiling: float,
    earlier_attempt_seconds: float = 0.0,
    earlier_unsettled: bool = False,
) -> list[str]:
    """Reasons a v2 attempt is refused at its send; empty admits it.

    Attempt 1 needs its ceiling within the cap and within the remaining quota minus the reserve; it reserves nothing
    for attempt 2, which reads the live quota at its own send. Attempt 2 needs attempt 1's attributed charge (its
    ceiling while unattributed, earlier_attempt_seconds) plus its ceiling within the cap, and its ceiling, plus
    attempt 1's seconds while that charge is unsettled, within the remaining quota minus the reserve.
    """
    if attempt not in (1, 2):
        return [f"the envelope has attempts 1 and 2, not {attempt!r}"]
    values = (remaining_seconds, reserve_seconds, envelope_cap, ceiling, earlier_attempt_seconds)
    if any(not math.isfinite(v) or v < 0 for v in values):
        return [f"admission inputs must be finite and nonnegative: {values}"]
    if attempt == 1 and earlier_attempt_seconds != 0.0:
        return ["attempt 1 has no earlier attempt"]
    reasons = []
    if earlier_attempt_seconds + ceiling > envelope_cap:
        reasons.append(
            f"earlier {earlier_attempt_seconds:g} s plus ceiling {ceiling:g} s exceeds envelope_cap {envelope_cap:g} s"
        )
    needed = ceiling + (earlier_attempt_seconds if attempt == 2 and earlier_unsettled else 0.0)
    if remaining_seconds - reserve_seconds < needed:
        reasons.append(
            f"remaining {remaining_seconds:g} s minus reserve {reserve_seconds:g} s is below the {needed:g} s needed"
        )
    return reasons


def select_fallback_step(
    first_delay: float,
    ladder_ceiling_seconds: Mapping[str, float],
    remaining_seconds: float,
    reserve_seconds: float,
    envelope_cap: float,
    earlier_attempt_seconds: float,
    earlier_unsettled: bool,
    ceiling_bound: float | None = None,
) -> tuple[tuple[float, float] | None, dict[str, list[str]]]:
    """Attempt 2's step: the smallest ladder delay above first_delay that attempt_admission_v2 admits.

    Returns ((delay, ceiling), rejected) for the chosen step, or (None, rejected) when none qualifies; rejected maps
    each skipped delay_key to its reasons. A step whose ceiling exceeds ceiling_bound is no candidate.
    """
    rejected: dict[str, list[str]] = {}
    for delay in REP_DELAY_LADDER_S:
        if delay <= first_delay:
            continue
        key = delay_key(delay)
        ceiling = float(ladder_ceiling_seconds[key])
        reasons = attempt_admission_v2(
            2, remaining_seconds, reserve_seconds, envelope_cap, ceiling, earlier_attempt_seconds, earlier_unsettled
        )
        if ceiling_bound is not None and ceiling > ceiling_bound:
            reasons.append(f"ceiling {ceiling:g} s exceeds the ceiling bound {ceiling_bound:g} s")
        if not reasons:
            return (delay, ceiling), rejected
        rejected[key] = reasons
    return None, rejected
