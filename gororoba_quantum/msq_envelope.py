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

import measurement_sequence_scatter as scatter

ENVELOPE_SCHEMA = "msq-envelope-v1"
SNAPSHOT_SCHEMA = "ibm-canonical-snapshot-v1"
ENVELOPE_FILE = "envelope.json"
ENVELOPE_BACKEND = "ibm_kingston"

# The layout rule keeps the scatter-floor qubit screen (measurement_sequence_scatter.eligible) and adds
# prob_meas1_prep0, the calibration's ground-state readout error: a readout-channel screen, while the shot-history
# bound comes from the in-job reset controls.
RULE_MAX_PROB_MEAS1_PREP0 = 0.02
# Kept qubits are at least this many edges apart in the CZ coupling graph: neither adjacent nor sharing a neighbor.
RULE_MIN_GRAPH_DISTANCE = 3
WIDTH_TIERS = (32, 24, 16)

# A plan whose digest changes this many times between consecutive snapshots refuses on the next change.
MAX_REPLANS = 3

# Retained Kingston failures all report 1305 (results/live/REP_DELAY_ZERO_CONTROL_FINDINGS.md): a delay that never
# executed reports no circuit time and bills at most the job overhead, an overrun ceiling bills executed shots.
FALLBACK_REP_DELAY_S = 50e-6
FALLBACK_TIMEOUT_CODE = 1305
FALLBACK_DELAY_CODES = (1602, 8030)
FALLBACK_MAX_BILLED_S = 3.0


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
