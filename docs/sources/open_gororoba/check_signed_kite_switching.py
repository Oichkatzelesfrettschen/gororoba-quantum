"""Verify switching and characteristic polynomials of the retained ripple graphs.

Only the supplied finite graph data enter the calculation. Exact integer
matrix arithmetic certifies the characteristic polynomial; quantum circuits,
backend services, and floating-point eigensolvers are outside the checker.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

Matrix = list[list[int]]
EXPECTED_POLYNOMIAL = [1, 0, -12, 16, 0, 0, 0]


def characteristic_polynomial(matrix: Matrix) -> list[int]:
    """Return descending coefficients using exact Faddeev-LeVerrier steps."""
    size = len(matrix)
    accumulator = [[int(row == column) for column in range(size)] for row in range(size)]
    coefficients = [1]
    for degree in range(1, size + 1):
        product = [
            [sum(matrix[row][inner] * accumulator[inner][column] for inner in range(size)) for column in range(size)]
            for row in range(size)
        ]
        trace = sum(product[index][index] for index in range(size))
        coefficient, remainder = divmod(-trace, degree)
        if remainder:
            raise ValueError("integer characteristic-polynomial recurrence failed")
        coefficients.append(coefficient)
        accumulator = [
            [product[row][column] + coefficient * int(row == column) for column in range(size)] for row in range(size)
        ]
    return coefficients


def verify_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Check octahedral support, negative switching, and exact signed spectrum."""
    vertex_ids = [vertex["id"] for vertex in graph["vertices"]]
    if len(vertex_ids) != 6 or len(set(vertex_ids)) != 6:
        raise ValueError("a kite requires six distinct vertices")
    indices = {vertex: index for index, vertex in enumerate(vertex_ids)}
    adjacency = [[0] * 6 for _ in range(6)]
    for edge in graph["edges"]:
        source, target, sign = edge["source"], edge["target"], edge["sign"]
        if (
            source not in indices
            or target not in indices
            or source == target
            or type(sign) is not int
            or sign not in (-1, 1)
        ):
            raise ValueError("invalid signed edge")
        first, second = indices[source], indices[target]
        if adjacency[first][second]:
            raise ValueError("duplicate signed edge")
        adjacency[first][second] = adjacency[second][first] = sign
    if any(sum(abs(entry) for entry in row) != 4 for row in adjacency):
        raise ValueError("six-vertex support must have exactly one off-diagonal nonneighbor per vertex")
    switching = [1, 0, 0, 0, 0, 0]
    frontier = [0]
    while frontier:
        first = frontier.pop()
        for second, sign in enumerate(adjacency[first]):
            if sign and switching[second] == 0:
                switching[second] = -sign * switching[first]
                frontier.append(second)
    if any(sign == 0 for sign in switching):
        raise ValueError("signed graph must be connected")
    if any(
        switching[first] * sign * switching[second] != -abs(sign)
        for first, row in enumerate(adjacency)
        for second, sign in enumerate(row)
    ):
        raise ValueError("signed graph fails D*S*D=-abs(S)")
    coefficients = characteristic_polynomial(adjacency)
    if coefficients != EXPECTED_POLYNOMIAL:
        raise ValueError("signed graph characteristic polynomial differs from (lambda+4)*lambda^3*(lambda-2)^2")
    return {
        "strut_constant": graph["strutConstant"],
        "vertex_ids": vertex_ids,
        "switching_diagonal": switching,
        "integer_switching_residual": 0,
        "characteristic_polynomial_descending": coefficients,
    }


def verify_evidence(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    graphs = evidence["boxkites"]
    if len(graphs) != 7 or sorted(graph["strutConstant"] for graph in graphs) != list(range(1, 8)):
        raise ValueError("evidence must contain the seven distinct strut constants")
    return [verify_graph(graph) for graph in graphs]


def check_controls(evidence: dict[str, Any]) -> list[str]:
    """Reject damaged signs/support and preserve invariance under vertex switching."""
    for field, value in (("sign", 0), ("sign", -evidence["boxkites"][0]["edges"][0]["sign"])):
        mutated = copy.deepcopy(evidence)
        mutated["boxkites"][0]["edges"][0][field] = value
        try:
            verify_evidence(mutated)
        except ValueError:
            continue
        raise ValueError("damaged edge sign survived the checker")
    mutated = copy.deepcopy(evidence)
    mutated["boxkites"][0]["edges"].pop()
    try:
        verify_evidence(mutated)
    except ValueError:
        pass
    else:
        raise ValueError("missing edge survived the checker")
    switched = copy.deepcopy(evidence)
    for graph in switched["boxkites"]:
        vertex = graph["vertices"][0]["id"]
        for edge in graph["edges"]:
            if vertex in (edge["source"], edge["target"]):
                edge["sign"] *= -1
    verify_evidence(switched)
    return ["invalid sign rejected", "single sign flip rejected", "missing edge rejected", "vertex switching preserved"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, default=Path(__file__).resolve().parents[3] / "results/ripple/evidence.json"
    )
    arguments = parser.parse_args()
    evidence_bytes = arguments.evidence.read_bytes()
    evidence = json.loads(evidence_bytes)
    result = {
        "schema": "signed-kite-switching-evidence-v1",
        "evidence_class": "exact finite graph calculation; standard signed-graph deduction",
        "input_sha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "graphs": verify_evidence(evidence),
        "controls": check_controls(evidence),
        "characteristic_polynomial": "(lambda+4)*lambda^3*(lambda-2)^2",
        "spectrum_with_multiplicity": [[-4, 1], [0, 3], [2, 2]],
        "hardware_claim": "Retained mathematical graphs are checked; hardware observations remain separate.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
