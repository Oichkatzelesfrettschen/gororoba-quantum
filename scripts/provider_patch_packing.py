"""Construct disjoint connected four-qubit witnesses from retained provider graphs.

Two graph matchings join disjoint edges into connected four-vertex patches.
If that construction misses the width bound, a connected-set integer program
also admits three-leaf stars, which need not contain two disjoint edges.
Attaining floor(usable width / 4) proves maximal patch count for this template;
otherwise the result is only a lower bound. Connectivity proves neither pulse
concurrency, calibrated quality, statistical independence nor billing feasibility.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import networkx as nx
import numpy as np
import scipy
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import parallel  # noqa: E402


def connected_sets(graph: nx.Graph) -> list[tuple[str, ...]]:
    groups = set()
    for center in graph:
        for leaves in itertools.combinations(sorted(graph.neighbors(center)), 3):
            groups.add(tuple(sorted((center, *leaves))))
        for second in graph.neighbors(center):
            for third in graph.neighbors(second):
                for fourth in graph.neighbors(third):
                    nodes = {center, second, third, fourth}
                    if len(nodes) == 4:
                        groups.add(tuple(sorted(nodes)))
    return sorted(groups)


def complete_packing(graph: nx.Graph, upper: int) -> list[list[str]]:
    groups = connected_sets(graph)
    if not groups:
        return []
    nodes = sorted(graph)
    incidence = csc_matrix([[int(node in group) for group in groups] for node in nodes], dtype=float)
    result = milp(
        -np.ones(len(groups)),
        integrality=np.ones(len(groups)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(incidence, 0, 1),
        options={"time_limit": 30},
    )
    if result.x is None:
        return []
    selected = [list(group) for group, value in zip(groups, result.x, strict=True) if value > 0.5][:upper]
    if len({node for group in selected for node in group}) != 4 * len(selected):
        raise ValueError("integer solver returned overlapping patches")
    return selected


def pack(name: str, qubits: list[Any], edges: list[Any], max_qubits: int) -> dict[str, Any]:
    graph = nx.Graph()
    graph.add_nodes_from(sorted(map(str, qubits)))
    available = set(graph.nodes)
    graph.add_edges_from(sorted((str(a), str(b)) for a, b in edges if str(a) in available and str(b) in available))
    pairs = sorted(tuple(sorted(pair)) for pair in nx.max_weight_matching(graph, maxcardinality=True))
    contracted = nx.Graph()
    contracted.add_nodes_from(range(len(pairs)))
    for first in range(len(pairs)):
        for second in range(first + 1, len(pairs)):
            if any(graph.has_edge(a, b) for a in pairs[first] for b in pairs[second]):
                contracted.add_edge(first, second)
    joined = sorted(tuple(sorted(pair)) for pair in nx.max_weight_matching(contracted, maxcardinality=True))
    upper = min(len(qubits), max_qubits) // 4
    selected = [sorted((*pairs[first], *pairs[second])) for first, second in joined[:upper]]
    method = "two matchings"
    if len(selected) < upper:
        completed = complete_packing(graph, upper)
        if len(completed) > len(selected):
            selected = completed
            method = "connected four-vertex set integer program"
    patches = []
    for nodes in selected:
        center = next(node for node in nodes if len(set(graph.neighbors(node)) & set(nodes)) >= 2)
        leaves = sorted(set(graph.neighbors(center)) & set(nodes))[:2]
        sector = next(node for node in nodes if node not in (center, *leaves))
        patches.append(
            {
                "qubits": nodes,
                "roles": {"q3": center, "q1": leaves[0], "q0": leaves[1], "q2": sector},
                "preparation_edges": [[center, leaves[0]], [center, leaves[1]]],
            }
        )
    return {
        "backend": name,
        "physical_width": len(qubits),
        "max_qubits_per_job": max_qubits,
        "dimension_upper_bound": upper,
        "patches": patches,
        "attains_dimension_bound": len(patches) == upper,
        "method": method,
        "scope": "connected disjoint template; physical independence and timing remain unqualified",
    }


def worker(task: tuple[str, list[Any], list[Any], int]) -> dict[str, Any]:
    return pack(*task)


def source_tasks(root: Path) -> list[tuple[str, list[Any], list[Any], int]]:
    iqm_path = root / "iqm.json"
    oq_path = root / "open-quantum/catalogue.json"
    iqm = json.loads(iqm_path.read_text())
    tasks = []
    for alias in ("emerald", "garnet"):
        device = iqm["devices"][alias]
        gates = device["architecture"]["gates"]
        qubits = sorted(
            {
                locus[0]
                for implementation in gates["prx"]["implementations"].values()
                for locus in implementation["loci"]
            }
        )
        edges = [
            locus for implementation in gates["cz"]["implementations"].values() for locus in implementation["loci"]
        ]
        tasks.append(("iqm:" + alias, qubits, edges, device["details"]["number_of_qubits"]))
    for backend in json.loads(oq_path.read_text())["backend_classes"]:
        if backend["short_code"] in ("ionq:forte-1", "rigetti:cepheus-1-108q", "aqt:ibex-q1"):
            constraint = backend["constraint_data"]
            tasks.append(
                (
                    backend["short_code"],
                    list(range(constraint["n_qubits"])),
                    constraint["topology"]["coupling_map"],
                    constraint["limits"]["max_qubits_per_job"],
                )
            )
    return tasks


def produce(root: Path) -> dict[str, Any]:
    iqm_path = root / "iqm.json"
    oq_path = root / "open-quantum/catalogue.json"
    rows = parallel.ordered_map(worker, source_tasks(root))
    return {
        "schema": "provider-four-qubit-packing-v1",
        "networkx_version": nx.__version__,
        "scipy_version": scipy.__version__,
        "sources_sha256": {
            "iqm.json": hashlib.sha256(iqm_path.read_bytes()).hexdigest(),
            "open-quantum/catalogue.json": hashlib.sha256(oq_path.read_bytes()).hexdigest(),
        },
        "rows": rows,
    }


def validate(root: Path, value: dict[str, Any]) -> None:
    """Check the retained certificate without depending on solver tie selection."""
    if value.get("schema") != "provider-four-qubit-packing-v1":
        raise ValueError("invalid packing schema")
    sources = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in ("iqm.json", "open-quantum/catalogue.json")
    }
    if value.get("sources_sha256") != sources:
        raise ValueError("packing source digests differ")
    tasks = source_tasks(root)
    rows = value["rows"]
    if [row["backend"] for row in rows] != [task[0] for task in tasks]:
        raise ValueError("packing backend membership differs")
    for row, (_, qubits, edges, maximum) in zip(rows, tasks, strict=True):
        available = set(map(str, qubits))
        graph = nx.Graph()
        graph.add_nodes_from(available)
        graph.add_edges_from((str(first), str(second)) for first, second in edges)
        upper = min(len(available), maximum) // 4
        patches = row["patches"]
        if (
            row["physical_width"] != len(available)
            or row["max_qubits_per_job"] != maximum
            or row["dimension_upper_bound"] != upper
            or len(patches) > upper
            or row["attains_dimension_bound"] != (len(patches) == upper)
        ):
            raise ValueError("packing width certificate differs")
        used: set[str] = set()
        for patch in patches:
            nodes = set(patch["qubits"])
            if used & nodes:
                raise ValueError("packing patches overlap")
            used.update(nodes)
            roles = patch["roles"]
            if (
                len(patch["qubits"]) != 4
                or len(nodes) != 4
                or not nodes <= available
                or set(roles) != {"q0", "q1", "q2", "q3"}
                or set(roles.values()) != nodes
                or not nx.is_connected(graph.subgraph(nodes))
            ):
                raise ValueError("invalid packing patch or roles")
            expected = [[roles["q3"], roles["q1"]], [roles["q3"], roles["q0"]]]
            if patch["preparation_edges"] != expected or any(not graph.has_edge(*edge) for edge in expected):
                raise ValueError("packing preparation edges differ from the source graph")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check is not None:
        validate(args.audit, json.loads(args.check.read_text()))
    elif args.out is not None:
        if args.out.exists():
            raise ValueError("a retained packing witness already exists")
        args.out.write_text(json.dumps(produce(args.audit), indent=1, sort_keys=True) + "\n")
    else:
        print(json.dumps(produce(args.audit), indent=1))


if __name__ == "__main__":
    main()
