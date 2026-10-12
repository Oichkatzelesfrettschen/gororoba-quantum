"""Render one or both hash-bound static algebra acquisitions as offline HTML.

The standalone renderer depends only on the Python standard library. The
extractor validates raw provenance; the renderer checks the portable payload's
internal consistency. A payload hash provides integrity, not authentication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).resolve().parents[1] / "gororoba_quantum/visualizations/measured_cayley_dickson_ripples.html"
MARKER = "__MEASURED_RIPPLE_JSON__"
SCHEMA = "measured-static-algebra-extraction-v1"
TOTAL_KEYS = (
    "physical_pub_shots",
    "logical_member_shots",
    "unique_active_qubit_shots",
    "unique_reserved_qubit_shots",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def object_value(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label}: expected object")
    return dict(value)


def sequence(value: Any, label: str, size: int | None = None) -> list[Any]:
    require(isinstance(value, list), f"{label}: expected array")
    require(size is None or len(value) == size, f"{label}: width differs")
    return list(value)


def label_value(value: Any, label: str) -> str:
    require(isinstance(value, str) and 0 < len(value) <= 2048, f"{label}: invalid text")
    return str(value)


def integer(value: Any, label: str, minimum: int = 0) -> int:
    require(type(value) is int and minimum <= value <= 2**53 - 1, f"{label}: invalid integer")
    return int(value)


def number(value: Any, label: str, low: float = -math.inf, high: float = math.inf) -> float:
    require(type(value) in (float, int) and math.isfinite(value), f"{label}: expected finite number")
    require(low <= value <= high, f"{label}: number outside bounds")
    return float(value)


def close(left: float, right: float, label: str, tolerance: float = 1e-10) -> None:
    require(math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance), f"{label}: inconsistent values")


def sha(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid SHA-256")
    return str(value)


def probability_vector(value: Any, width: int, label: str, tolerance: float = 1e-9) -> list[float]:
    values = [number(item, label, 0, 1) for item in sequence(value, label, width)]
    require(abs(math.fsum(values) - 1) <= tolerance, f"{label}: probability mass differs")
    return values


def rational(value: Any, label: str) -> Fraction:
    text = label_value(value, label)
    require(len(text) <= 128, f"{label}: rational exceeds supported size")
    try:
        result = Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f"{label}: invalid rational") from error
    number(float(result), label)
    return result


def qubits(value: Any, label: str) -> list[int]:
    values = [integer(item, label) for item in sequence(value, label)]
    require(values == sorted(set(values)) and bool(values), f"{label}: require sorted unique qubits")
    return values


def metadata(item: dict[str, Any], family: str) -> None:
    meta = object_value(item["metadata"], "member metadata")
    role = label_value(meta.get("role"), "member role")
    integer(meta.get("execution_row"), "execution row")
    kind = meta.get("kind")
    if family == "rank-sector":
        require(kind == family and role in ("packed", "isolated"), "invalid rank role or kind")
        require(integer(meta.get("sector"), "sector") < 8, "invalid rank sector")
        label_value(meta.get("probe"), "probe")
        parameter = rational(meta.get("parameter_exact"), "rank parameter")
        require(parameter in map(Fraction, ("0", "1/2", "1", "3/2", "2")), "invalid rank parameter")
        coordinates = [
            integer(abs(value), "coordinate") if type(value) is int else -1
            for value in sequence(meta.get("probe_coordinates"), "probe coordinates", 4)
        ]
        require(all(value >= 0 for value in coordinates), "invalid probe coordinate")
        probe_norm = sum(value**2 for value in coordinates)
        require(probe_norm > 0, "zero rank probe")
        alpha = Fraction(2) if parameter <= 1 else parameter**2 - parameter + 2
        require(rational(meta.get("alpha_exact"), "alpha") == alpha, "rank alpha differs")
        require(
            rational(meta.get("unit_probe_norm_factor_exact"), "unit norm factor") == alpha**2,
            "unit norm factor differs",
        )
        require(
            rational(meta.get("unnormalized_probe_norm_factor_exact"), "probe norm factor") == alpha**2 * probe_norm,
            "probe norm factor differs",
        )
        exact = rational(meta.get("ideal_success_exact"), "exact rank success")
        close(float(exact), item["ideal_probabilities"][0], "rank ideal")
        require(len(item["counts"]) == 4, "rank outcome width differs")
    elif kind == "walk":
        require(len(item["counts"]) == 16, "walk outcome width differs")
        integer(meta.get("lane"), "walk lane")
        if role == "readout":
            require(integer(meta.get("readout_value"), "readout state") <= 1, "invalid readout state")
            return
        require(integer(meta.get("depth"), "walk depth") <= 4, "walk depth exceeds acquired range")
        for index in sequence(meta.get("pair"), "associator pair", 2):
            require(integer(index, "pair index", 1) < 32, "pair index outside dimension-32 associator")
    elif kind == "ladder":
        dimension = integer(meta.get("dimension"), "ladder dimension", 8)
        require(dimension in (8, 16, 32, 64), "unsupported ladder dimension")
        require(len(item["counts"]) == dimension, "ladder outcome width differs")
        require(meta.get("variant") in ("true", "flip", "omit"), "unknown ladder variant")
    else:
        require(kind == "atlas", "unsupported ripple member kind")
        if role == "readout":
            require(len(item["counts"]) == 2, "readout outcome width differs")
            return
        kite = integer(meta.get("kite"), "kite", 1)
        require(kite <= 7, "kite outside atlas")
        low = [index for index in range(1, 8) if index != kite]
        edges = [(left, right) for left, right in combinations(low, 2) if left ^ right != kite]
        edge = integer(meta.get("edge_index"), "edge index")
        require(edge < 12 and (meta.get("source"), meta.get("target")) == edges[edge], "atlas edge identity differs")
        sign = integer(meta.get("sign"), "edge sign", -1)
        require(sign in (-1, 1), "invalid edge sign")
        phase = integer(meta.get("phase_index"), "phase index")
        require(phase < 8 and len(item["counts"]) == 2, "invalid atlas phase or width")
        close(item["ideal_probabilities"][0], (1 - sign * math.cos(phase * math.pi / 4)) / 2, "atlas ideal")


def member(value: Any, family: str) -> dict[str, Any]:
    item = object_value(value, "member")
    shots = integer(item.get("shots"), "shots", 1)
    counts = [integer(value, "count") for value in sequence(item.get("counts"), "counts")]
    require(len(counts) in (2, 4, 8, 16, 32, 64) and sum(counts) == shots, "counts differ from acquired shots")
    width = len(counts)
    measured = probability_vector(item.get("probabilities"), width, "measured probabilities")
    ideal = probability_vector(item.get("ideal_probabilities"), width, "ideal probabilities")
    preparation = object_value(item.get("preparation_model"), "preparation model")
    # Retained preparation marginals round each component to six decimals.
    model = probability_vector(
        preparation.get("probabilities"), width, "preparation probabilities", width * 0.5e-6 + 1e-12
    )
    replay = object_value(item.get("execution_replay"), "execution replay")
    status = label_value(replay.get("status"), "replay status")
    execution = object_value(item.get("execution"), "execution")
    require(integer(execution.get("shots"), "execution shots", 1) == shots, "execution shots differ")
    require(execution.get("pub") == item.get("pub"), "execution PUB differs")
    if replay.get("probabilities") is not None:
        require(status == "calibration_bound" and execution.get("calibration") is not None, "replay lacks calibration")
        require(execution.get("calibration_changed_during_shots") is False, "replay calibration changed")
        replay_values = probability_vector(replay["probabilities"], width, "replay probabilities")
    else:
        require(status != "calibration_bound", "calibration-bound replay is absent")
        replay_values = None
    for index, count in enumerate(counts):
        close(measured[index], count / shots, "count probability")
    for name, values in (("ideal", ideal), ("preparation_model", model), ("execution_replay", replay_values)):
        residual = item.get("hardware_minus_" + name)
        if values is None:
            require(residual is None, "unavailable model has residuals")
        else:
            for index, value in enumerate(sequence(residual, "residuals", width)):
                close(number(value, "residual", -1, 1), measured[index] - values[index], "residual")
    for key in ("group", "job_id", "pub"):
        label_value(item.get(key), key)
    integer(item.get("pub_index"), "PUB index")
    qubits(item.get("physical_qubits"), "member qubits")
    registers = sequence(item.get("registers"), "registers")
    require(bool(registers) and len(set(registers)) == len(registers), "invalid registers")
    for value in registers:
        label_value(value, "register")
    stop = 0
    total_events = 0.0
    blocks = sequence(item.get("shot_order_blocks"), "shot-order blocks")
    require(bool(blocks), "shot blocks absent")
    for block_value in blocks:
        block = object_value(block_value, "shot block")
        require(integer(block.get("start_shot"), "block start") == stop, "shot blocks are not contiguous")
        stop = integer(block.get("stop_shot_exclusive"), "block stop", stop + 1)
        size = integer(block.get("shots"), "block shots", 1)
        require(size == stop - block["start_shot"] and stop <= shots, "shot block size differs")
        events = number(block.get("event_zero_probability"), "block P0", 0, 1) * size
        close(events, round(events), "block integer count")
        total_events += events
    require(stop == shots, "shot blocks omit observations")
    close(total_events, counts[0], "shot-block event count")
    metadata(item, family)
    return item


def dependence(value: Any, members: dict[str, Any], expected: list[str], error: bool) -> None:
    item = object_value(value, "joint observations")
    names = sequence(item.get("members"), "joint member names")
    require(len(names) == len(set(names)) and set(names) == set(expected), "joint member coverage differs")
    means = []
    for name in names:
        measured = members[name]["probabilities"]
        ideal = members[name]["ideal_probabilities"]
        means.append(1 - measured[ideal.index(1.0)] if error else measured[0])
    joint = [
        sequence(row, "joint row", len(names))
        for row in sequence(item.get("joint_probabilities"), "joint matrix", len(names))
    ]
    covariance = [
        sequence(row, "covariance row", len(names))
        for row in sequence(item.get("covariance"), "covariance matrix", len(names))
    ]
    for row, mean in enumerate(means):
        for column, other_mean in enumerate(means):
            probability = number(joint[row][column], "joint probability", 0, 1)
            require(
                max(0, mean + other_mean - 1) - 1e-10 <= probability <= min(mean, other_mean) + 1e-10,
                "joint probability violates marginal bounds",
            )
            close(probability, joint[column][row], "joint symmetry")
            close(
                number(covariance[row][column], "covariance", -0.25, 0.25),
                probability - mean * other_mean,
                "covariance",
            )
        close(joint[row][row], mean, "joint diagonal")


def endpoints(value: Any) -> None:
    analysis = object_value(value, "endpoint analysis")
    if "withheld" in analysis:
        label_value(analysis["withheld"], "inference withholding")
        require("observables" not in analysis, "withheld analysis includes endpoints")
        return
    if not analysis:
        return
    label_value(analysis.get("method"), "endpoint method")
    for assumption in sequence(analysis.get("assumptions"), "endpoint assumptions"):
        label_value(assumption, "endpoint assumption")
    names = set()
    for row in sequence(analysis.get("observables"), "endpoint observables"):
        row = object_value(row, "endpoint observable")
        name = label_value(row.get("name"), "endpoint name")
        require(name not in names, "duplicate endpoint")
        names.add(name)
        estimate = number(row.get("estimate"), "endpoint estimate")
        lower = number(row.get("lo"), "endpoint lower")
        upper = number(row.get("hi"), "endpoint upper")
        require(lower <= estimate <= upper, "endpoint interval ordering differs")
        radius = number(row.get("confidence_half_width"), "endpoint radius", 0)
        close(estimate - lower, radius, "endpoint lower radius")
        close(upper - estimate, radius, "endpoint upper radius")
        number(row.get("alpha"), "endpoint alpha", 0, 1)
        require(row["alpha"] > 0, "endpoint alpha must be positive")
        number(row.get("null_value"), "endpoint null")
        require(row.get("reject_null") is None or type(row.get("reject_null")) is bool, "invalid endpoint decision")
        if row.get("detection_radius") is not None:
            number(row["detection_radius"], "detection radius", 0)
        for method in sequence(row.get("bound_methods"), "endpoint bound methods"):
            label_value(method, "bound method")


def validate(value: Any) -> dict[str, Any]:
    """Check the portable representation without asserting raw-file authenticity."""
    data = object_value(value, "extraction")
    require(data.get("schema") == SCHEMA, "unsupported extraction schema")
    expected = sha(data.get("payload_sha256"))
    require(
        digest(canonical({key: value for key, value in data.items() if key != "payload_sha256"})) == expected,
        "extraction payload hash differs",
    )
    require(data.get("evidence_kind") in ("collected_hardware", "synthetic_fixture"), "unsupported evidence kind")
    family = label_value(data.get("family"), "family")
    require(family in ("ripple", "rank-sector"), "unsupported family")
    sha(data.get("experiment_digest"))
    require(
        re.fullmatch(r"[0-9a-f]{40,64}", label_value(data.get("source_commit"), "source commit")) is not None,
        "invalid source commit",
    )
    sources = object_value(data.get("source_files"), "source files")
    require({"record.json", "collect.json", "isa.qpy"} <= sources.keys(), "required source file hashes absent")
    for name, identity in sources.items():
        path = Path(name)
        require(bool(name) and not path.is_absolute() and ".." not in path.parts, "source identity must be relative")
        sha(identity)
    analysis_sources = object_value(data.get("analysis_sources"), "analysis sources")
    require(
        set(analysis_sources) == {"extractor_sha256", "runtime_experiment_digest"}, "analysis source identities differ"
    )
    for value in analysis_sources.values():
        sha(value)
    members = {name: member(value, family) for name, value in object_value(data.get("members"), "members").items()}
    require(bool(members), "members absent")
    for name in members:
        label_value(name, "member name")
    pubs = sequence(data.get("pubs"), "PUBs")
    seen: set[str] = set()
    rows: set[int] = set()
    totals = dict.fromkeys(TOTAL_KEYS, 0)
    for value in pubs:
        pub = object_value(value, "PUB")
        name = label_value(pub.get("name"), "PUB name")
        require(name not in seen, "duplicate PUB")
        seen.add(name)
        row = integer(pub.get("row"), "PUB row")
        require(row not in rows, "duplicate PUB row")
        rows.add(row)
        shots = integer(pub.get("shots"), "PUB shots", 1)
        selected = {key: item for key, item in members.items() if item["pub"] == name}
        require(bool(selected), "PUB lacks members")
        for item in selected.values():
            require(
                item["job_id"] == pub.get("job_id")
                and item["shots"] == shots
                and item["metadata"]["execution_row"] == row,
                "member PUB binding differs",
            )
        active = qubits(pub.get("active_physical_qubits"), "active PUB qubits")
        reserved = qubits(pub.get("reserved_physical_qubits"), "reserved PUB qubits")
        require(set(active) <= set(reserved), "active qubits outside reservation")
        require(
            set(reserved) == {qubit for item in selected.values() for qubit in item["physical_qubits"]},
            "reserved footprint differs",
        )
        dependence(pub.get("event_zero"), members, list(selected), False)
        deterministic = [key for key, item in selected.items() if 1.0 in item["ideal_probabilities"]]
        dependence(pub.get("deterministic_error"), members, deterministic, True)
        sha(pub.get("raw_sha256"))
        for key, amount in zip(
            TOTAL_KEYS, (shots, shots * len(selected), shots * len(active), shots * len(reserved)), strict=True
        ):
            totals[key] += amount
    require(
        rows == set(range(len(pubs))) and seen == {item["pub"] for item in members.values()}, "PUB coverage differs"
    )
    throughput = object_value(data.get("throughput"), "throughput")
    for key, total in totals.items():
        require(integer(throughput.get(key), key) == total, f"{key}: total differs")
    charge = throughput.get("retained_collector_charge_seconds")
    if charge is not None:
        number(charge, "retained QPU charge", 0)
    if charge is not None and charge > 0:
        rates = object_value(throughput.get("rates_per_charged_second"), "charged rates")
        require(
            set(rates) == set(TOTAL_KEYS) and throughput.get("rates_withheld") is None, "charged rate coverage differs"
        )
        for key, total in totals.items():
            close(number(rates[key], "charged rate", 0), total / charge, "charged rate")
    else:
        require(throughput.get("rates_per_charged_second") is None, "unavailable charge has rates")
        label_value(throughput.get("rates_withheld"), "rate withholding")
    endpoints(data.get("endpoint_analysis"))
    contract_names = set()
    for contract in sequence(data.get("observable_contracts", []), "observable contracts"):
        contract = object_value(contract, "observable contract")
        name = label_value(contract.get("name"), "contract name")
        require(name not in contract_names, "duplicate observable contract")
        contract_names.add(name)
        terms = sequence(contract.get("terms"), "observable terms")
        require(bool(terms), "observable terms absent")
        estimate = 0.0
        for term in terms:
            term = object_value(term, "observable term")
            require(term.get("member") in members, "contract member absent")
            require(type(term.get("sign")) is int and term["sign"] in (-1, 1), "contract sign differs")
            scores = sequence(term.get("values"), "observable score", len(members[term["member"]]["counts"]))
            for value in scores:
                number(value, "observable score")
            estimate += term["sign"] * math.fsum(
                score * probability
                for score, probability in zip(scores, members[term["member"]]["probabilities"], strict=True)
            )
        for result in data["endpoint_analysis"].get("observables", []):
            if result["name"] == name:
                close(result["estimate"], estimate, "endpoint estimate and raw marginal scores")
                close(result["alpha"], number(contract.get("alpha"), "contract alpha", 0, 1), "endpoint alpha")
    analysis_names = {row["name"] for row in data["endpoint_analysis"].get("observables", [])}
    require(
        not contract_names or not analysis_names or contract_names == analysis_names, "endpoint/contract names differ"
    )
    for value in sequence(data.get("interpretation"), "interpretation"):
        label_value(value, "interpretation")
    return data


def render(values: list[Any]) -> str:
    require(1 <= len(values) <= 2, "supply one or both extracted families")
    validated = [validate(value) for value in values]
    require(len({value["family"] for value in validated}) == len(validated), "duplicate acquisition family")
    require(
        len({value["evidence_kind"] for value in validated}) == 1, "synthetic and hardware acquisitions cannot be mixed"
    )
    validated.sort(key=lambda value: value["family"])
    payload = json.dumps(validated, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = TEMPLATE.read_text(encoding="utf-8")
    require(template.count(MARKER) == 1, "template must contain one data marker")
    return template.replace(MARKER, payload)


def validate_output(inputs: list[Path], output: Path, check: bool) -> None:
    for source in (*inputs, TEMPLATE):
        require(
            output.resolve() != source.resolve()
            and not (output.exists() and source.exists() and output.samefile(source)),
            "output aliases an input or template",
        )
    require(not output.is_symlink(), "output must be a regular path")
    require(not output.exists() or output.is_file(), "output must be a file")
    require(check or not output.exists(), "output already exists; choose a new destination or use --check")


def write_new(output: Path, contents: bytes) -> None:
    """Atomically install a new file without overwriting another writer's path."""
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".measured-ripple-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evidence", type=Path, action="append", required=True, help="Extracted ripple or rank JSON; repeat for both"
    )
    parser.add_argument("--out", type=Path, required=True, help="New standalone HTML destination")
    parser.add_argument(
        "--check", action="store_true", help="Compare existing HTML without writing files or creating directories"
    )
    args = parser.parse_args()
    try:
        validate_output(args.evidence, args.out, args.check)
        sources = [path.read_bytes() for path in args.evidence]
        html = render([json.loads(source, object_pairs_hook=pairs) for source in sources]).encode()
        require(
            all(path.read_bytes() == source for path, source in zip(args.evidence, sources, strict=True)),
            "input changed during rendering",
        )
        if args.check:
            require(
                args.out.is_file() and args.out.read_bytes() == html, "HTML differs from validated data and template"
            )
        else:
            validate_output(args.evidence, args.out, False)
            write_new(args.out, html)
    except (OSError, ValueError, TypeError, KeyError, IndexError, OverflowError) as error:
        print(f"measured ripple: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
