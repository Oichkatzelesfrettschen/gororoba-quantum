"""Offline model of the A5-242 orientation-bit plan: device tables, region scores and region placement.

Reads the retained JSON next to this file (collect.py writes it) and the retained dry-run records of
results/live. No network, no qiskit: the score model re-derives live_run.layout_score (esp x coherence) from the
properties, and the placement model re-derives live_run.place_replicas (packing.candidate_replicas, then greedy
disjoint selection with a one-coupler guard). Each is checked against the records before it predicts anything.
"""

from __future__ import annotations

import json
import math
from functools import cache
from pathlib import Path
from typing import Any

import rustworkx as rx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BACKENDS = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
QUALITY = {"max_readout_error": 0.08, "max_cz_error": 0.03, "max_sx_error": 0.01, "min_t1_us": 20.0, "min_t2_us": 20.0}
FLOOR = 0.7
OPERATOR = {"ibm_fez": [2, 3, 4, 16], "ibm_kingston": [0, 1, 2, 3, 4, 16], "ibm_marrakesh": []}


@cache
def patterns() -> dict[str, Any]:
    return json.loads((HERE / "patterns.json").read_text())


@cache
def device(backend: str, tag: str) -> dict[str, Any]:
    return json.loads((HERE / f"device_{backend}_{tag}.json").read_text())


class Dev:
    """One backend at one calibration, read from a device_*.json."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.n = raw["num_qubits"]
        self.q = {int(k): v for k, v in raw["qubits"].items()}
        self.cz: dict[tuple[int, int], Any] = {
            (int(k.split("-")[0]), int(k.split("-")[1])): v for k, v in raw["cz"].items()
        }

    def op(self, name: str, qs: tuple[int, ...]) -> tuple[float, float]:
        """(error, length in s) of one operation; the Target's error is 0 for an op it lists without one."""
        if name == "cz":
            v = self.cz.get((qs[0], qs[1]))
            return (0.0, 0.0) if v is None else (v["error"], v["length"])
        if name == "measure":
            q = self.q[qs[0]]
            return (q["readout_error"] or 0.0, q["readout_length"] or 0.0)
        if name in ("sx", "x", "rz"):
            v = self.q[qs[0]][name]
            return (0.0, 0.0) if v is None else (v["error"], v["length"])
        return (0.0, 0.0)

    def exclusions(self, operator: list[int]) -> tuple[dict[int, str], dict[tuple[int, int], str]]:
        """live_run.take_snapshot's exclusion rules applied to the properties (operational flag not stored)."""
        raw = self.raw
        faulty_gate_q = {q for g in raw["faulty_other"] for q in g[1:]}
        qs: dict[int, str] = {}
        for q in range(self.n):
            e = self.q[q]
            t1, t2, ro = e["t1"], e["t2"], e["readout_error"]
            sx = e["sx"]["error"] if e["sx"] else None
            reason = None
            if q in raw["faulty_qubits"]:
                reason = "faulty"
            elif q in faulty_gate_q:
                reason = "faulty gate"
            elif t1 is None or t2 is None or ro is None or sx is None:
                reason = "missing calibration"
            elif t1 * 1e6 < QUALITY["min_t1_us"] or t2 * 1e6 < QUALITY["min_t2_us"]:
                reason = "T1/T2"
            elif ro > QUALITY["max_readout_error"]:
                reason = "readout"
            elif sx > QUALITY["max_sx_error"]:
                reason = "sx"
            if reason is None and q in operator:
                reason = "operator"
            if reason:
                qs[q] = reason
        faulty_edges = {tuple(x) for x in raw["faulty_cz"]}
        es: dict[tuple[int, int], str] = {}
        for edge, v in self.cz.items():
            err = None if v is None else v["error"]
            if edge in faulty_edges or edge[::-1] in faulty_edges:
                es[edge] = "faulty"
            elif err is None or err > QUALITY["max_cz_error"]:
                es[edge] = "cz error"
        return qs, es

    def graph(self) -> rx.PyGraph:
        g = rx.PyGraph()
        g.add_nodes_from(range(self.n))
        g.add_edges_from_no_data(sorted({(min(e), max(e)) for e in self.cz}))
        return g


def pattern_graph(members: dict[str, Any]) -> tuple[list[int], set[tuple[int, int]]]:
    qubits: set[int] = set()
    edges: set[tuple[int, int]] = set()
    for m in members.values():
        for _name, qs in m["ops"]:
            qubits.update(qs)
            if len(qs) == 2:
                edges.add((min(qs), max(qs)))
    return sorted(qubits), edges


def moved_ops(ops: list[list[Any]], mapping: dict[int, int]) -> list[tuple[str, tuple[int, ...]]]:
    return [(name, tuple(mapping[q] for q in qs)) for name, qs in ops]


def log_terms(ops: list[tuple[str, tuple[int, ...]]], dev: Dev) -> dict[str, float]:
    """ln of ESP split by operation kind (live_run.esp: product of 1 - error over every operation)."""
    out: dict[str, float] = {"cz": 0.0, "sx": 0.0, "x": 0.0, "rz": 0.0, "measure": 0.0}
    for name, qs in ops:
        if name in ("barrier", "delay"):
            continue
        err = dev.op(name, qs)[0]
        out[name] = out.get(name, 0.0) + math.log1p(-min(err, 1.0 - 1e-15))
    return out


def duration(ops: list[tuple[str, tuple[int, ...]]], dev: Dev) -> float:
    """As-soon-as-possible critical path of the Target gate lengths (QuantumCircuit.estimate_duration)."""
    free: dict[int, float] = {}
    end = 0.0
    for name, qs in ops:
        if name == "barrier":
            continue
        length = dev.op(name, qs)[1] if name != "delay" else 0.0
        start = max((free.get(q, 0.0) for q in qs), default=0.0)
        for q in qs:
            free[q] = start + length
        end = max(end, start + length)
    return end


def coherence_term(ops: list[tuple[str, tuple[int, ...]]], dev: Dev, seconds: float) -> tuple[float, list[int]]:
    used = sorted({q for name, qs in ops if name not in ("barrier", "delay") for q in qs})
    rate = sum(1.0 / dev.q[q]["t2"] for q in used)
    return -seconds * rate, used


def score_terms(ops: list[list[Any]], mapping: dict[int, int], dev: Dev) -> dict[str, float]:
    moved = moved_ops(ops, mapping)
    terms = log_terms(moved, dev)
    seconds = duration(moved, dev)
    coh, used = coherence_term(moved, dev, seconds)
    terms["coherence"] = coh
    terms["ln_score"] = sum(terms.values())
    terms["seconds"] = seconds
    return terms


def candidates(
    ops: list[list[Any]],
    qubits: list[int],
    edges: set[tuple[int, int]],
    dev: Dev,
    ex_q: dict[int, str],
    ex_e: dict[tuple[int, int], str],
    floor: float,
) -> list[tuple[float, dict[int, int]]]:
    """Every admissible embedding of the pattern at score >= floor x best, best first (packing.candidate_replicas)."""
    graph = dev.graph()
    graph.remove_nodes_from(sorted(ex_q))
    small = rx.PyGraph()
    small.add_nodes_from(qubits)
    index = {q: i for i, q in enumerate(qubits)}
    small.add_edges_from_no_data([(index[a], index[b]) for a, b in sorted(edges)])
    scored: list[tuple[float, tuple[tuple[int, int], ...]]] = []
    for found in rx.vf2_mapping(graph, small, subgraph=True, induced=False, id_order=True):
        mapping = {qubits[s]: b for b, s in found.items()}
        moved = moved_ops(ops, mapping)
        bad = False
        for name, qs in moved:
            if name == "cz" and (qs in ex_e or qs[::-1] in ex_e or qs not in dev.cz):
                bad = True
                break
        if bad:
            continue
        scored.append((score_terms(ops, mapping, dev)["ln_score"], tuple(sorted(mapping.items()))))
    scored.sort(key=lambda item: (-item[0], item[1]))
    if not scored:
        return []
    cut = -math.inf if floor <= 0.0 else math.log(floor) + scored[0][0]
    return [(math.exp(v), dict(m)) for v, m in scored if v >= cut]


def place(
    cands: list[tuple[float, dict[int, int]]], dev: Dev, guard: int = 1, max_regions: int | None = None
) -> list[tuple[float, dict[int, int]]]:
    """Greedy disjoint selection; guard 1 blocks the neighbors of every taken qubit (place_replicas)."""
    graph = dev.graph()
    chosen: list[tuple[float, dict[int, int]]] = []
    blocked: set[int] = set()
    for score, mapping in cands:
        if max_regions is not None and len(chosen) >= max_regions:
            break
        qs = set(mapping.values())
        if qs & blocked:
            continue
        chosen.append((score, mapping))
        zone = set(qs)
        for _ in range(guard):
            zone |= {n for q in zone for n in graph.neighbors(q)}
        blocked |= zone
    return chosen


def max_packing(cands: list[tuple[float, dict[int, int]]], dev: Dev, guard: int = 1) -> int:
    """Largest set of candidates that are pairwise disjoint and guard-separated (exact, 0-1 program)."""
    import numpy as np
    from scipy.optimize import LinearConstraint, milp

    graph = dev.graph()
    zones = []
    for _, mapping in cands:
        zone = set(mapping.values())
        for _ in range(guard):
            zone |= {n for q in zone for n in graph.neighbors(q)}
        zones.append(zone)
    sets = [set(m.values()) for _, m in cands]
    n = len(cands)
    # candidates a and b conflict when set(a) meets zone(b) or the reverse
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if sets[a] & zones[b] or sets[b] & zones[a]]
    if not pairs:
        return n
    a_mat = np.zeros((len(pairs), n))
    for r, (a, b) in enumerate(pairs):
        a_mat[r, a] = a_mat[r, b] = 1
    res = milp(c=-np.ones(n), constraints=LinearConstraint(a_mat, ub=1), integrality=np.ones(n), bounds=(0, 1))
    return int(round(-res.fun))
