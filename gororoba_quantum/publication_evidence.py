"""Offline content binding for the retained teleportation/QET publication plates.

Source blob identities bind the historical snapshot, not a live backend.
Parsing/typography checks and a source-consistency receipt never certify an
acquisition, the physics of an instrument, or the completeness of a model.
"""

from __future__ import annotations

import hashlib
import json
import math
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from teleportation_contract import require

SVG = "{http://www.w3.org/2000/svg}"
SAFE_TAGS = {
    SVG + name for name in ("svg", "defs", "circle", "line", "path", "polygon", "polyline", "rect", "text", "tspan")
}


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise ValueError(f"nonfinite JSON constant: {value}")


def read_json(data: bytes) -> Any:
    return json.loads(data, object_pairs_hook=_object, parse_constant=_constant)


def blob_id(data: bytes) -> str:
    """Git blob identity, used only for integrity of already pinned public bytes."""
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data, usedforsecurity=False).hexdigest()


def within(root: Path, relative: str) -> Path:
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, "source path must be repository relative")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "source path escapes its root")
    return resolved


def source_documents(root: Path, manifest: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Read only manifest-bound files, refusing replacements rather than relabelling them."""
    documents: dict[str, Any] = {}
    receipts: list[dict[str, Any]] = []
    require(manifest.get("schema") == "teleportation-publication-sources-v1", "unsupported publication manifest")
    for item in manifest["sources"]:
        name = item["role"]
        require(name not in documents, "duplicate source role")
        data = within(root, item["path"]).read_bytes()
        require(blob_id(data) == item["git_blob_sha1"], f"source drift: {item['path']}")
        documents[name] = read_json(data)
        receipts.append(
            {
                "role": name,
                "path": item["path"],
                "bytes": len(data),
                "git_blob_sha1": blob_id(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return documents, receipts


def _finite(value: Any) -> float:
    require(type(value) in (int, float) and math.isfinite(value), "endpoint must be a finite real number")
    return float(value)


def _interval(value: Mapping[str, Any]) -> tuple[float, float, float]:
    lo, mean, hi = (_finite(value[key]) for key in ("lo", "mean", "hi"))
    require(lo <= mean <= hi, "endpoint lies outside its interval")
    return lo, mean, hi


MEASURED_SUMMARY = ("measured_statistics", "summary_interval")


def _summaries(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], dict[str, Any]]]:
    """Every selected-endpoint summary node with its key path from the record root."""
    found: list[tuple[tuple[str, ...], dict[str, Any]]] = []
    if isinstance(value, dict):
        if all(
            isinstance(value.get(key), dict) and "mean" in value[key] for key in ("selected_excess", "selected_margin")
        ):
            found.append((path, value))
        for key, child in value.items():
            found.extend(_summaries(child, (*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_summaries(child, (*path, str(index))))
    return found


def measured_summary(collect: Any) -> dict[str, Any]:
    """The measured-statistics summary node; replayed statistics are never displayed.

    The collect record carries one summary per measured and per replayed
    statistics block. The plate shows the measured block, so the node is
    selected by its `measured_statistics/summary_interval` key path and must
    occur exactly once.
    """
    chosen = [node for path, node in _summaries(collect) if path[-len(MEASURED_SUMMARY) :] == MEASURED_SUMMARY]
    require(len(chosen) == 1, "Kingston measured-statistics summary must resolve uniquely")
    return chosen[0]


def display_values(documents: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    """Derive the displayed routes, percentages and endpoint intervals from records."""
    analysis, cases = documents["tuna_analysis"], documents["tuna_cases"]
    require(analysis["backend"] == cases["backend"] == "tuna_17", "unexpected Tuna source backend")
    rows = analysis["teleport"]
    require(len(rows) == 4 and {r["input"] for r in rows} == {"0", "1", "+", "+i"}, "unexpected historical input rows")
    tuna: dict[str, str] = {}
    for index, label in enumerate(("0", "1", "+", "+i")):
        row = next(r for r in rows if r["input"] == label)
        score = _finite(row["corrected_fidelity"])
        lo, hi = map(_finite, row["corrected_ci95"])
        require(0 <= lo <= score <= hi <= 1, "invalid probability interval")
        route = [row[key] for key in ("I", "P1", "P2", "D")]
        require(
            all(type(q) is int and 0 <= q < cases["nqubits"] for q in route) and len(set(route)) == 4,
            "invalid historical route",
        )
        tuna[f"tuna_row_{index}_route"] = "\u2013".join(map(str, route))
        tuna[f"tuna_row_{index}_match"] = f"{100 * score:.1f}%"
        tuna[f"tuna_row_{index}_interval"] = f"{100 * lo:.1f}\u2013{100 * hi:.1f}%"
    shots = cases["shots"]
    require(type(shots) is int and shots > 0, "invalid shot count")
    tuna["tuna_shots"] = f"{shots:,} shots per circuit  \u00b7  four routes, not one channel."
    summary = measured_summary(documents["kingston_collect"])
    king: dict[str, str] = {}
    for key, prefix in (("selected_excess", "kingston_information"), ("selected_margin", "kingston_margin")):
        item = summary[key]
        require(item.get("method") == "student_t_over_14_replicas", "Kingston interval definition changed")
        lo, mean, hi = _interval(item)
        king[f"{prefix}_mean"] = f"{mean:+.3f}".replace("-", "\u2212")
        king[f"{prefix}_interval"] = f"{lo:+.3f} to {hi:+.3f}".replace("-", "\u2212")
    return {"tuna17.svg": tuna, "kingston.svg": king}


def svg_nodes(data: bytes) -> tuple[ET.Element, dict[str, ET.Element]]:
    require(
        b"<!DOCTYPE" not in data.upper() and b"<!ENTITY" not in data.upper(), "SVG document declarations are forbidden"
    )
    root = ET.fromstring(data)
    require(root.tag == SVG + "svg" and root.get("viewBox") == "0 0 2560 1440", "unexpected SVG root or viewBox")
    nodes: dict[str, ET.Element] = {}
    for node in root.iter():
        require(node.tag in SAFE_TAGS, "unsupported SVG element")
        for key, value in node.attrib.items():
            require(
                not key.lower().startswith("on")
                and not key.endswith("href")
                and key not in {"style", "class", "src"}
                and "url(" not in value.lower(),
                "SVG active/external reference or CSS is forbidden",
            )
        if ident := node.get("id"):
            require(ident not in nodes, "duplicate SVG id")
            nodes[ident] = node
    return root, nodes


def validate_display(data: bytes, expected: Mapping[str, str]) -> None:
    root, nodes = svg_nodes(data)
    require(float(root.get("opacity", "1")) > 0 and root.get("display") != "none", "hidden SVG root")
    for ident, text in expected.items():
        require(ident in nodes and nodes[ident].tag == SVG + "text", f"missing endpoint node: {ident}")
        require(nodes[ident] in list(root), f"endpoint must be direct text: {ident}")
        require("".join(nodes[ident].itertext()) == text, f"display/source mismatch: {ident}")
        require(
            float(nodes[ident].get("opacity", "1")) > 0 and nodes[ident].get("display") != "none",
            f"hidden endpoint node: {ident}",
        )


def validate_layout(data: bytes, plate: str) -> None:
    """Required notation and semantic IDs; visual bounds remain a renderer check."""
    root, nodes = svg_nodes(data)
    text = "\n".join("".join(node.itertext()) for node in root.iter(SVG + "text"))
    require(
        "U\u2020" not in text and "\u03b2" not in text and "\u1d66" not in text, "ambiguous basis/subscript notation"
    )
    if plate == "tuna17.svg":
        for phrase in ("B_D", "d \u2295 a \u2295 b", "P2: readout unused", "four routes, not one channel"):
            require(phrase in text, f"missing Tuna qualification: {phrase}")
        require("d \u2295 a \u2295 b \u2295 1" not in text, "incorrect Y inversion")
        require(
            all(ident in nodes for ident in ("tuna_decoder_box", "tuna_decoder_ideal", "tuna_decoder_note")),
            "decoder bounds IDs are missing",
        )
    else:
        require(plate == "kingston.svg", "unknown plate")
        for phrase in (
            "mA = 0: RY(\u2212\u03b8*)",
            "mA = 1: RY(+\u03b8*)",
            "BOTH if/else branches",
            "record-independent unitary",
            "r = \u221a(h\u00b2 + k\u00b2)",
        ):
            require(phrase in text, f"missing Kingston qualification: {phrase}")
        require("r = 0:" not in text and "r-independent" not in text, "measurement-bit/normalizer collision")
        for node in root.iter(SVG + "text"):
            size = float(node.attrib["font-size"])
            for span in node.iter(SVG + "tspan"):
                if span.get("baseline-shift") == "sub":
                    require(math.isclose(float(span.attrib["font-size"]), 0.75 * size), "subscript size drift")
