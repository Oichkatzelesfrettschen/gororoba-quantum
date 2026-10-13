"""Render the finite Cayley-Dickson evidence as a portable offline explorer.

The renderer checks the shape and internal consistency of the supplied evidence.
The scientific generator supplies the independent algebra and circuit checks.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).resolve().parents[1] / "gororoba_quantum/visualizations/cayley_dickson_ripples.html"
DATA_MARKER = "__RIPPLE_EVIDENCE_JSON__"


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context}: expected an object")
    return value


def _array(value: Any, size: int, context: str) -> list[Any]:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{context}: expected {size} entries")
    return value


def _integer(value: Any, minimum: int, maximum: int, context: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{context}: expected an integer in [{minimum}, {maximum}]")
    return value


def _label(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f"{context}: expected a nonempty label of at most 256 characters")
    return value


def _probability(value: Any, context: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{context}: expected a finite probability in [0, 1]")
    return float(value)


def _fraction(value: Any, context: str) -> Fraction:
    if not isinstance(value, str) or len(value) > 128:
        raise ValueError(f"{context}: expected a rational probability string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{context}: invalid rational probability") from error
    if not 0 <= result <= 1:
        raise ValueError(f"{context}: rational probability outside [0, 1]")
    return result


def _matching_probability(number: Any, exact: Any, context: str) -> Fraction:
    probability = _probability(number, context)
    fraction = _fraction(exact, context)
    if not math.isclose(probability, float(fraction), rel_tol=0, abs_tol=1e-12):
        raise ValueError(f"{context}: numeric and exact probabilities disagree")
    return fraction


def _frame(value: Any, depth: int, context: str) -> dict[str, Any]:
    frame = _object(value, context)
    if _integer(frame.get("depth"), 0, 30, context) != depth:
        raise ValueError(f"{context}: frames must cover depths 0 through 30 in order")
    probabilities = _array(frame.get("probabilities"), 16, context)
    exact_values = _array(frame.get("exact_probabilities"), 16, context)
    exact = [
        _matching_probability(number, fraction, f"{context}.state[{basis}]")
        for basis, (number, fraction) in enumerate(zip(probabilities, exact_values, strict=True))
    ]
    if sum(exact) != 1:
        raise ValueError(f"{context}: exact state probabilities must sum to one")
    return_exact = _matching_probability(frame.get("return_probability"), frame.get("return_exact"), context)
    collision_exact = _matching_probability(frame.get("collision_K"), frame.get("collision_exact"), context)
    if return_exact != exact[0] or collision_exact != sum(probability**2 for probability in exact):
        raise ValueError(f"{context}: return or collision probability disagrees with the state probabilities")
    return {
        "depth": depth,
        "probabilities": [float(probability) for probability in exact],
        "exact_probabilities": [str(probability) for probability in exact],
        "return_probability": float(return_exact),
        "return_exact": str(return_exact),
        "collision_K": float(collision_exact),
        "collision_exact": str(collision_exact),
    }


def _kite(value: Any, context: str) -> dict[str, Any]:
    kite = _object(value, context)
    constant = _integer(kite.get("strutConstant"), 1, 7, context)
    vertices = []
    identifiers: dict[int, int] = {}
    for index, value in enumerate(_array(kite.get("vertices"), 6, context)):
        vertex = _object(value, context)
        identifier = _integer(vertex.get("id"), 1, 7, context)
        low = _integer(vertex.get("low"), 1, 7, context)
        high = _integer(vertex.get("high"), 9, 15, context)
        if identifier in identifiers or identifier != low or low == constant or low ^ high != 8 ^ constant:
            raise ValueError(f"{context}: inconsistent or repeated assessor identifier")
        identifiers[identifier] = index
        vertices.append({"id": identifier, "low": low, "high": high})

    def endpoints(source: Any, target: Any) -> tuple[int, int]:
        source = _integer(source, 1, 7, context)
        target = _integer(target, 1, 7, context)
        if source not in identifiers or target not in identifiers or source == target:
            raise ValueError(f"{context}: edge endpoint must name a distinct existing assessor")
        source_index, target_index = sorted((identifiers[source], identifiers[target]))
        return source_index, target_index

    edges = []
    signs: dict[tuple[int, int], int] = {}
    for value in _array(kite.get("edges"), 12, context):
        edge = _object(value, context)
        source, target = endpoints(edge.get("source"), edge.get("target"))
        sign = _integer(edge.get("sign"), -1, 1, context)
        if sign == 0 or (source, target) in signs:
            raise ValueError(f"{context}: expected unique edges with signs +1 or -1")
        signs[source, target] = sign
        edges.append({"source": source, "target": target, "sign": sign})
    struts = []
    for value in _array(kite.get("struts"), 3, context):
        strut = _array(value, 2, context)
        source, target = endpoints(*strut)
        if vertices[source]["low"] ^ vertices[target]["low"] != constant:
            raise ValueError(f"{context}: opposite assessors must match the strut constant")
        struts.append((source, target))
    all_pairs = set(combinations(range(6), 2))
    if len(set(struts)) != 3 or set(signs) & set(struts) or set(signs) | set(struts) != all_pairs:
        raise ValueError(f"{context}: edges and struts must partition all assessor pairs")
    if sorted(endpoint for strut in struts for endpoint in strut) != list(range(6)):
        raise ValueError(f"{context}: each assessor must belong to exactly one strut")
    for face in combinations(range(6), 3):
        face_edges = list(combinations(face, 2))
        if all(edge in signs for edge in face_edges) and math.prod(signs[edge] for edge in face_edges) != -1:
            raise ValueError(f"{context}: triangular face has inconsistent edge-sign product")
    return {"label": f"Strut constant {constant}", "vertices": vertices, "edges": edges, "struts": struts}


def visualization_data(value: Any) -> dict[str, Any]:
    """Validate generated evidence and select the fields consumed by the explorer."""
    evidence = _object(value, "evidence")
    depths = _array(evidence.get("proposed_hardware_depths"), 5, "proposed_hardware_depths")
    if [_integer(depth, 0, 4, "proposed_hardware_depths") for depth in depths] != list(range(5)):
        raise ValueError("proposed_hardware_depths: expected depths 0 through 4")
    dynamics = []
    for index, value in enumerate(_array(evidence.get("pairs"), 2, "pairs")):
        context = f"pairs[{index}]"
        pair = _object(value, context)
        _integer(pair.get("qubits"), 4, 4, context)
        frames = _array(pair.get("frames"), 31, context)
        dynamics.append(
            {
                "label": _label(pair.get("label"), context),
                "depths": [_frame(frame, depth, f"{context}.frames[{depth}]") for depth, frame in enumerate(frames)],
            }
        )
    box_kites = [
        _kite(kite, f"boxkites[{index}]") for index, kite in enumerate(_array(evidence.get("boxkites"), 7, "boxkites"))
    ]
    if len({kite["label"] for kite in box_kites}) != 7:
        raise ValueError("boxkites: expected all seven distinct strut constants")
    return {"dynamics": dynamics, "box_kites": box_kites, "proposed_hardware_depths": depths}


def render(evidence: Any) -> str:
    """Embed validated data without allowing JSON text to close the script element."""
    data = json.dumps(visualization_data(evidence), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(DATA_MARKER) != 1:
        raise ValueError("visualization template must contain exactly one evidence marker")
    return template.replace(DATA_MARKER, data)


def validate_output_path(evidence: Path, output: Path) -> None:
    """Protect both renderer inputs before reading evidence or writing HTML."""
    for source in (evidence, TEMPLATE):
        if output.resolve() == source.resolve() or (output.exists() and source.exists() and output.samefile(source)):
            raise ValueError("output must differ from the evidence and template paths")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, required=True, help="JSON written by the finite ripple evidence generator"
    )
    parser.add_argument("--out", type=Path, required=True, help="standalone HTML destination")
    parser.add_argument(
        "--check", action="store_true", help="compare existing output with a fresh render; leave files intact"
    )
    arguments = parser.parse_args()
    try:
        validate_output_path(arguments.evidence, arguments.out)
        evidence = json.loads(arguments.evidence.read_text(encoding="utf-8"))
        html = render(evidence)
        if arguments.check:
            if arguments.out.read_text(encoding="utf-8") != html:
                raise ValueError("HTML differs from the current evidence and template")
        else:
            arguments.out.parent.mkdir(parents=True, exist_ok=True)
            arguments.out.write_text(html, encoding="utf-8")
    except (OSError, ValueError) as error:
        parser.exit(1, f"ripple visualization: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
