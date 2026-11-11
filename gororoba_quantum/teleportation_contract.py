"""Pauli-frame readout and fixed-route six-state experiment contracts.

Frame convention: X**b Z**a, a=m(I), b=m(P1); outcome 0 means the
positive Pauli eigenvalue. Basis alignment is not inverse preparation.
The six-state bound applies to one input-independent instrument, not six
state-labelled routes. A design manifest and finite-count bound do not by
themselves establish that physical-instrument assumption.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

Basis = Literal["X", "Y", "Z"]
SCHEMA = "qi-fixed-route-six-state-v1"


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: Any, name: str, minimum: int = 0) -> int:
    require(type(value) is int and value >= minimum, f"{name} must be an integer >= {minimum}")
    return int(value)


def bit(value: Any, name: str) -> int:
    value = integer(value, name)
    require(value <= 1, f"{name} must be a bit")
    return value


@dataclass(frozen=True)
class State:
    label: str
    basis: Basis
    expected: int
    prepare: tuple[str, ...]


STATES = (
    State("0", "Z", 0, ()),
    State("1", "Z", 1, ("X",)),
    State("+", "X", 0, ("H",)),
    State("-", "X", 1, ("X", "H")),
    State("+i", "Y", 0, ("H", "S")),
    State("-i", "Y", 1, ("X", "H", "S")),
)
BY_LABEL = {state.label: state for state in STATES}
ALIGN: dict[Basis, tuple[str, ...]] = {"Z": (), "X": ("H",), "Y": ("Sdag", "H")}


def decode(basis: Basis, raw: int, a: int, b: int) -> int:
    """Relabel one terminal outcome, retaining every Bell branch.

    This is not post-selection and does not apply a physical correction.
    Y uses a XOR b, with no constant inversion.
    """
    require(basis in ALIGN, "readout basis must be X, Y or Z")
    raw, a, b = bit(raw, "raw"), bit(a, "a"), bit(b, "b")
    flip = {"Z": b, "X": a, "Y": a ^ b}[basis]
    return raw ^ flip


def validate_route(route: Sequence[int], nqubits: int, edges: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Check ordered roles I,P1,P2,D against an undirected coupling graph."""
    nqubits = integer(nqubits, "nqubits", 4)
    require(len(route) == 4, "a route has four roles I,P1,P2,D")
    r = tuple(integer(q, "route qubit") for q in route)
    require(len(set(r)) == 4 and max(r) < nqubits, "route qubits must be distinct and in range")
    graph: set[frozenset[int]] = set()
    for edge in edges:
        require(len(edge) == 2, "each coupling has two endpoints")
        pair = tuple(integer(q, "edge qubit") for q in edge)
        require(pair[0] != pair[1] and max(pair) < nqubits, "invalid coupling endpoint")
        graph.add(frozenset(pair))
    require(all(frozenset(pair) in graph for pair in zip(r, r[1:], strict=False)), "route has an absent coupling")
    return r


def circuit(nqubits: int, route: Sequence[int], label: str) -> str:
    """Emit logical cQASM, with barriers separating preparation/channel/readout.

    The caller validates topology. Barriers mark the logical boundary;
    compiler/native-channel conformance still needs its own receipt.
    """
    require(label in BY_LABEL, "unknown six-state input")
    r = validate_route(route, nqubits, list(zip(route, route[1:], strict=False)))
    i, p1, p2, d = r
    state = BY_LABEL[label]
    lines = ["version 3.0", "", f"qubit[{nqubits}] q", f"bit[{nqubits}] b", ""]
    lines.extend(f"{gate} q[{i}]" for gate in state.prepare)
    lines.extend(
        [
            "barrier q",
            f"H q[{p1}]",
            f"CNOT q[{p1}], q[{p2}]",
            f"SWAP q[{p2}], q[{d}]",
            f"CNOT q[{i}], q[{p1}]",
            f"H q[{i}]",
            "barrier q",
        ]
    )
    lines.extend(f"{gate} q[{d}]" for gate in ALIGN[state.basis])
    lines.extend(["barrier q", "b = measure q", ""])
    return "\n".join(lines)


def make_plan(
    backend: str,
    backend_type_id: int,
    nqubits: int,
    edges: Sequence[Sequence[int]],
    routes: Sequence[Sequence[int]],
    shots: int,
    orders: Sequence[Sequence[int]],
    batch_size: int,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Cross all six inputs with each route in each supplied complete block.

    Orders permute the route-by-input cells. This function draws no random
    values. The CLI obtains ordering randomness through qrng_seeds and
    retains both seed provenance and the complete generated order.
    """
    require(isinstance(backend, str) and bool(backend.strip()), "backend is required")
    integer(backend_type_id, "backend_type_id")
    shots = integer(shots, "shots", 1)
    batch_size = integer(batch_size, "batch_size", 1)
    checked = [validate_route(route, nqubits, edges) for route in routes]
    require(bool(checked) and len(set(checked)) == len(checked), "routes must be nonempty and unique")
    require(bool(orders), "at least one acquisition block is required")
    cells = [(index, state.label) for index in range(len(checked)) for state in STATES]
    ordered: list[tuple[int, int, str]] = []
    for block, order in enumerate(orders):
        indices = [integer(index, "order index") for index in order]
        require(sorted(indices) == list(range(len(cells))), "each block must permute every route/input cell")
        ordered.extend((block, *cells[index]) for index in indices)
    files: dict[str, str] = {}
    batches: list[dict[str, Any]] = []
    for offset in range(0, len(ordered), batch_size):
        name = f"batch-{offset // batch_size:04d}"
        rows = []
        for block, route_index, label in ordered[offset : offset + batch_size]:
            state_index = tuple(BY_LABEL).index(label)
            filename = f"block-{block:04d}-route-{route_index:03d}-state-{state_index}.cq"
            text = circuit(nqubits, checked[route_index], label)
            files[f"{name}/{filename}"] = text
            rows.append(
                {
                    "file": filename,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "kind": "fixed-route-teleport",
                    "block": block,
                    "route_index": route_index,
                    "input": label,
                    "basis": BY_LABEL[label].basis,
                    "expected": BY_LABEL[label].expected,
                }
            )
        batches.append({"batch": name, "circuits": rows})
    plan = {
        "schema": SCHEMA,
        "backend": backend,
        "backend_type_id": backend_type_id,
        "nqubits": nqubits,
        "topology": [list(e) for e in edges],
        "routes": [list(r) for r in checked],
        "shots": shots,
        "orders": [list(o) for o in orders],
        "batch_size": batch_size,
        "batches": batches,
        "status": "prospective_unsubmitted",
        "readout": "full_register_terminal",
        "correction": "all_shot_basis_dependent_pauli_frame",
        "postselection": False,
        "live_output_demonstrated": False,
    }
    return plan, files


def validate_plan(plan: Mapping[str, Any]) -> dict[str, str]:
    """Regenerate every circuit and structural field; extra provenance is retained."""
    require(plan.get("schema") == SCHEMA, "unsupported plan schema")
    expected, files = make_plan(
        plan["backend"],
        plan["backend_type_id"],
        plan["nqubits"],
        plan["topology"],
        plan["routes"],
        plan["shots"],
        plan["orders"],
        plan["batch_size"],
    )
    require(
        all(plan.get(key) == value for key, value in expected.items()), "plan disagrees with its regenerated design"
    )
    return files


def score_histogram(
    counts: Mapping[str, int],
    nqubits: int,
    route: Sequence[int],
    label: str,
) -> dict[str, Any]:
    """Score full-register strings with Q0 rightmost; retain branch denominators."""
    integer(nqubits, "nqubits", 4)
    r = validate_route(route, nqubits, list(zip(route, route[1:], strict=False)))
    require(label in BY_LABEL, "unknown six-state input")
    state = BY_LABEL[label]
    branches = {f"{a}{b}": {"shots": 0, "correct": 0} for a in range(2) for b in range(2)}
    for outcome, count in counts.items():
        require(
            isinstance(outcome, str) and len(outcome) == nqubits and set(outcome) <= {"0", "1"},
            "outcome must be a full-width binary register string",
        )
        count = integer(count, "histogram count")
        a, b, d = (int(outcome[-1 - q]) for q in (r[0], r[1], r[3]))
        row = branches[f"{a}{b}"]
        row["shots"] += count
        row["correct"] += count * (decode(state.basis, d, a, b) == state.expected)
    n = sum(row["shots"] for row in branches.values())
    correct = sum(row["correct"] for row in branches.values())
    require(n > 0, "empty acquisition has no fidelity")
    return {
        "input": label,
        "basis": state.basis,
        "expected": state.expected,
        "shots": n,
        "correct": correct,
        "match": correct / n,
        "branches": branches,
    }


def six_state_estimate(rows: Sequence[Mapping[str, Any]], alpha: float = 0.05) -> dict[str, Any]:
    """Equal-input-weight mean and fixed-horizon one-sided Hoeffding bound.

    Independent bounded trials, fixed stopping, a common instrument and
    trusted preparation/readout are assumptions, not inferred facts. Counts
    are not pooled across unequal input allocations, routes or calibrations.
    The bound covers sampling only, not SPAM, drift or selection bias.
    """
    require(type(alpha) in (int, float) and math.isfinite(alpha) and 0 < alpha < 1, "alpha must be in (0,1)")
    labels = [row["input"] for row in rows]
    require(len(rows) == 6 and set(labels) == set(BY_LABEL), "exactly one row for each of the six states is required")
    routes = {tuple(row["route"]) for row in rows}
    channels = {row["channel_id"] for row in rows}
    epochs = {row["calibration_id"] for row in rows}
    require(len(routes) == len(channels) == len(epochs) == 1, "cannot pool routes, channels or calibration epochs")
    require(
        all(isinstance(v, str) and v.strip() for v in channels | epochs),
        "channel and calibration identities are required",
    )
    validate_route(
        next(iter(routes)),
        max(next(iter(routes))) + 1,
        list(zip(next(iter(routes)), next(iter(routes))[1:], strict=False)),
    )
    sizes: list[int] = []
    matches: list[float] = []
    for row in rows:
        require(row.get("selection") == "all_shots", "accepted-only or unspecified selection is not this estimator")
        n = integer(row["shots"], "shots", 1)
        k = integer(row["correct"], "correct")
        require(k <= n, "correct exceeds shots")
        sizes.append(n)
        matches.append(k / n)
    mean = math.fsum(matches) / 6
    radius = math.sqrt(-math.log(alpha) * math.fsum(1 / n for n in sizes) / 72)
    lower = max(0.0, mean - radius)
    return {
        "mean": mean,
        "lower": lower,
        "alpha": alpha,
        "sampling_radius": radius,
        "method": "equal_weight_six_state_one_sided_fixed_horizon_hoeffding",
        "classical_bound": 2 / 3,
        "lower_exceeds_classical_bound": lower > 2 / 3,
        "benchmark_status": "conditional_on_common_instrument_and_sampling_assumptions",
        "live_output_demonstrated": False,
    }
