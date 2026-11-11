"""Validate portable quantum observations without changing retained acquisitions.

Counts, same-PUB moments, model predictions and exact references remain distinct.
Optional raw replay checks bitstrings and bytes, not QPY circuit semantics, device
chronology, or the scientific assumptions of a retained inference contract.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import re
import tempfile
from collections.abc import Callable, Iterable, Sequence
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any

from parallel import ordered_map

EXTRACTION_SCHEMA = "measured-static-algebra-extraction-v1"
SCHEMA = "gororoba-evidence-workbench-v1"
MAX_BYTES = 64 * 1024 * 1024
MAX_INTEGER = 2**53 - 1
MAX_RAW_SHOTS = 2_000_000
# The extractor rounds preparation probabilities to six decimals, so each entry moves by at most
# PROBABILITY_ROUNDING. Accumulated rounding is capped at MAX_MASS_ERROR whatever the histogram width: a wider vector
# whose mass leaves 1 by more than the cap is rejected, never renormalized. The retained records stay within 3e-6.
# Rank-sector members carry the acquired path parameters t in {0, 1/2, 1, 3/2, 2} and eight sectors; the viewer selects
# members by role, sector and probe, so each must be present.
RANK_PARAMETERS = frozenset(Fraction(v) for v in ("0", "1/2", "1", "3/2", "2"))
RANK_SECTORS = 8
PROBABILITY_ROUNDING = 0.5e-6
MAX_MASS_ERROR = 1e-5


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def integer(value: Any, label: str, minimum: int = 0) -> int:
    require(type(value) is int and minimum <= value <= MAX_INTEGER, f"{label}: invalid integer")
    return int(value)


def number(value: Any, label: str) -> float:
    require(type(value) in (int, float) and math.isfinite(value), f"{label}: non-finite or nonnumeric value")
    return float(value)


def sha256(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def canonical(value: Any) -> bytes:
    """Match the retained extractor's JSON hashing convention, including newline."""
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(contents: bytes) -> Any:
    require(len(contents) <= MAX_BYTES, "input exceeds the 64 MiB limit")

    def reject_constant(value: str) -> Any:
        raise ValueError(f"non-finite JSON constant: {value}")

    return json.loads(contents, object_pairs_hook=_pairs, parse_constant=reject_constant)


def read_bytes(path: Path) -> bytes:
    require(path.is_file() and path.stat().st_size <= MAX_BYTES, "missing or oversized input")
    before = path.stat()
    with path.open("rb") as stream:
        contents = stream.read(MAX_BYTES + 1)
    after = path.stat()
    require(
        (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
        "input changed during read",
    )
    require(len(contents) <= MAX_BYTES, "input exceeds the 64 MiB limit")
    return contents


def source_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and "\\" not in relative, "invalid source path")
    part = PurePosixPath(relative)
    require(
        not part.is_absolute() and bool(part.parts) and all(p not in (".", "..") for p in part.parts),
        "unsafe source path",
    )
    base = root.resolve(strict=True)
    path = base.joinpath(*part.parts).resolve(strict=True)
    require(path.is_relative_to(base) and path.is_file(), "source escapes its retained root")
    return path


def _digest(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid SHA-256")
    return str(value)


def _probabilities(values: Any, width: int, label: str) -> list[float]:
    require(isinstance(values, list) and len(values) == width, f"{label}: wrong histogram width")
    result = [number(value, label) for value in values]
    require(all(0 <= value <= 1 for value in result), f"{label}: value outside probability support")
    envelope = min(width * PROBABILITY_ROUNDING, MAX_MASS_ERROR) + 1e-12
    require(abs(math.fsum(result) - 1) <= envelope, f"{label}: mass exceeds rounding envelope")
    return result


def _count(probability: Any, shots: int) -> int:
    value = number(probability, "empirical probability")
    require(0 <= value <= 1, "empirical probability outside support")
    count = round(value * shots)
    require(abs(value * shots - count) <= 1e-7, "empirical probability has no integer count")
    return count


def positive_semidefinite(matrix: list[list[int]]) -> bool:
    """Exact rational LDL test, including singular zero-pivot constraints."""
    a = [[Fraction(value) for value in row] for row in matrix]
    for k in range(len(a)):
        pivot = a[k][k]
        if pivot < 0:
            return False
        if pivot == 0:
            if any(a[k][j] != 0 for j in range(k + 1, len(a))):
                return False
            continue
        for i in range(k + 1, len(a)):
            for j in range(i, len(a)):
                a[i][j] -= a[i][k] * a[k][j] / pivot
                a[j][i] = a[i][j]
    return True


def validate_dependence(
    group: dict[str, Any], pub: dict[str, Any], members: dict[str, Any], event: str
) -> dict[str, Any]:
    names = group["members"]
    require(isinstance(names, list) and len(names) <= 128 and len(set(names)) == len(names), "invalid moment members")
    n = integer(pub["shots"], "PUB shots", 1)
    means: list[int] = []
    for name in names:
        require(name in members, "unknown moment member")
        member = members[name]
        require((member["job_id"], member["pub"]) == (pub["job_id"], pub["name"]), "cross-PUB moment pairing")
        require(member["shots"] == n, "moment shot denominator differs")
        if event == "event_zero":
            means.append(member["counts"][0])
        else:
            certain = [i for i, p in enumerate(member["ideal_probabilities"]) if p == 1.0]
            require(len(certain) == 1, "error event requires a deterministic ideal outcome")
            means.append(n - member["counts"][certain[0]])
    joint, covariance = group["joint_probabilities"], group["covariance"]
    size = len(names)
    for value in (joint, covariance):
        require(isinstance(value, list) and len(value) == size, "invalid moment matrix size")
        require(all(isinstance(row, list) and len(row) == size for row in value), "nonsquare moment matrix")
    joint_counts = [[_count(v, n) for v in row] for row in joint]
    exact: list[list[int]] = []
    correlation: list[list[float | None]] = []
    for i in range(size):
        require(joint_counts[i][i] == means[i], "moment diagonal differs from marginal")
        exact_row: list[int] = []
        corr_row: list[float | None] = []
        for j in range(size):
            k = joint_counts[i][j]
            require(k == joint_counts[j][i], "asymmetric joint counts")
            require(max(0, means[i] + means[j] - n) <= k <= min(means[i], means[j]), "Frechet bound violation")
            numerator = n * k - means[i] * means[j]
            expected = numerator / n**2
            require(abs(number(covariance[i][j], "covariance") - expected) <= 1e-12, "covariance identity differs")
            denominator = means[i] * (n - means[i]) * means[j] * (n - means[j])
            corr_row.append(numerator / math.sqrt(denominator) if denominator else None)
            exact_row.append(numerator)
        exact.append(exact_row)
        correlation.append(corr_row)
    require(positive_semidefinite(exact), "covariance matrix is not positive semidefinite")
    return {"members": names, "joint_counts": joint_counts, "correlation": correlation}


def _validate_member(task: tuple[str, Any, str]) -> None:
    """Check one member's histogram, probability vectors, rank identity and shot blocks."""
    name, member, family = task
    require(isinstance(name, str) and 0 < len(name) <= 512 and isinstance(member, dict), "invalid member identity")
    n = integer(member["shots"], "member shots", 1)
    counts = member["counts"]
    require(isinstance(counts, list) and 1 <= len(counts) <= 65536, "invalid histogram width")
    require(len(counts) & (len(counts) - 1) == 0, "register histogram width is not a power of two")
    require(sum(integer(c, "histogram count") for c in counts) == n, "histogram mass differs from shots")
    observed = _probabilities(member["probabilities"], len(counts), "observations")
    require(
        all(abs(p - k / n) <= 1e-12 for p, k in zip(observed, counts, strict=True)),
        "counts and probabilities differ",
    )
    _probabilities(member["ideal_probabilities"], len(counts), "ideal")
    prep = member.get("preparation_model", {})
    _probabilities(prep.get("probabilities"), len(counts), "preparation")
    replay = member.get("execution_replay", {})
    if replay.get("probabilities") is not None:
        require(replay.get("status") == "calibration_bound", "unqualified replay probabilities")
        _probabilities(replay["probabilities"], len(counts), "execution replay")
    require(isinstance(member.get("metadata"), dict), "missing member metadata")
    metadata = member["metadata"]
    if family == "rank-sector":
        for field in (
            "parameter_exact",
            "alpha_exact",
            "unit_probe_norm_factor_exact",
            "unnormalized_probe_norm_factor_exact",
            "ideal_success_exact",
        ):
            require(isinstance(metadata.get(field), str) and len(metadata[field]) <= 128, "invalid exact norm metadata")
        require(metadata.get("kind") == family, "invalid rank kind")
        require(metadata.get("role") in ("packed", "isolated"), "invalid rank role")
        integer(metadata.get("execution_row"), "execution row")
        require(integer(metadata.get("sector"), "sector") < RANK_SECTORS, "invalid rank sector")
        probe = metadata.get("probe")
        require(isinstance(probe, str) and 0 < len(probe) <= 2048, "invalid rank probe label")
        parameter = Fraction(metadata["parameter_exact"])
        require(parameter in RANK_PARAMETERS, "rank parameter outside the acquired path set")
        alpha = Fraction(2) if parameter <= 1 else parameter * parameter - parameter + 2
        coordinates = metadata.get("probe_coordinates")
        require(isinstance(coordinates, list) and len(coordinates) == 4, "invalid rank probe")
        require(all(type(c) is int and abs(c) <= MAX_INTEGER for c in coordinates), "invalid probe coefficient")
        norm = sum(c * c for c in coordinates)
        require(norm > 0, "zero rank probe")
        require(Fraction(metadata["alpha_exact"]) == alpha, "rank LCU normalization differs")
        require(Fraction(metadata["unit_probe_norm_factor_exact"]) == alpha * alpha, "unit-probe factor differs")
        require(
            Fraction(metadata["unnormalized_probe_norm_factor_exact"]) == alpha * alpha * norm,
            "unnormalized-probe factor differs",
        )
        ideal = Fraction(metadata["ideal_success_exact"])
        require(0 <= ideal <= 1 and abs(float(ideal) - member["ideal_probabilities"][0]) <= 1e-12, "rank ideal differs")
    blocks = member.get("shot_order_blocks")
    require(isinstance(blocks, list) and bool(blocks), "missing shot-order blocks")
    cursor, zero_count = 0, 0
    for block in blocks:
        start = integer(block["start_shot"], "block start")
        stop = integer(block["stop_shot_exclusive"], "block stop", 1)
        require(start == cursor and start < stop <= n, "block gap, overlap, or out-of-range stop")
        require(integer(block["shots"], "block shots", 1) == stop - start, "block denominator differs")
        zero_count += _count(block["event_zero_probability"], stop - start)
        cursor = stop
    require(cursor == n and zero_count == counts[0], "block totals differ from full histogram")


def validate_acquisition(value: Any) -> dict[str, Any]:
    require(isinstance(value, dict) and value.get("schema") == EXTRACTION_SCHEMA, "unsupported extraction schema")
    expected = _digest(value.get("payload_sha256"))
    require(
        sha256(canonical({k: v for k, v in value.items() if k != "payload_sha256"})) == expected, "payload hash differs"
    )
    require(value.get("evidence_kind") in ("collected_hardware", "synthetic_fixture"), "unsupported evidence kind")
    require(value.get("family") in ("ripple", "rank-sector"), "unsupported acquisition family")
    members, pubs = value.get("members"), value.get("pubs")
    require(isinstance(members, dict) and 0 < len(members) <= 6000, "invalid member dictionary")
    require(isinstance(pubs, list) and 0 < len(pubs) <= 4096, "invalid PUB list")
    family = value["family"]
    ordered_map(_validate_member, [(name, member, family) for name, member in members.items()])
    seen: set[tuple[str, str]] = set()
    covered: set[str] = set()
    diagnostics = []
    for pub in pubs:
        key = (pub["job_id"], pub["name"])
        require(all(isinstance(k, str) and k for k in key) and key not in seen, "duplicate or invalid PUB identity")
        seen.add(key)
        selected = {name for name, member in members.items() if (member["job_id"], member["pub"]) == key}
        require(bool(selected) and not covered.intersection(selected), "invalid PUB membership")
        covered.update(selected)
        event = validate_dependence(pub["event_zero"], pub, members, "event_zero")
        require(set(event["members"]) == selected, "event moments omit PUB members")
        errors = validate_dependence(pub["deterministic_error"], pub, members, "deterministic_error")
        expected_errors = {name for name in selected if 1.0 in members[name]["ideal_probabilities"]}
        require(set(errors["members"]) == expected_errors, "deterministic-error coverage differs")
        diagnostics.append({"job_id": key[0], "pub": key[1], "event_zero": event, "deterministic_error": errors})
    require(covered == set(members), "orphaned acquisition member")
    for relative, expected in value.get("source_files", {}).items():
        require(isinstance(relative, str) and bool(relative), "invalid source identity")
        _digest(expected)
    return {"payload": value, "dependence": diagnostics, "verification": "payload_digest_and_internal_consistency"}


def _raw_pub(task: tuple[dict[str, Any], dict[str, Any], str]) -> dict[str, Any]:
    """Replay one independent PUB; callers can map these tasks through parallel.py."""
    pub, members, root_text = task
    first = next(iter(members.values()))
    index = integer(first["pub_index"], "PUB index")
    relative = f"raw/{pub['job_id']}/pub_{index:02d}.json"
    contents = read_bytes(source_path(Path(root_text), relative))
    require(sha256(contents) == _digest(pub["raw_sha256"]), "raw PUB hash differs")
    raw = decode(contents)
    require(raw["pub_name"] == pub["name"] and raw["pub_index"] == index, "raw PUB identity differs")
    n = integer(pub["shots"], "PUB shots", 1)
    require(n <= MAX_RAW_SHOTS, "raw replay shot budget exceeded")
    events: dict[str, int] = {}
    errors: dict[str, int] = {}
    for name, member in members.items():
        require(member["pub_index"] == index, "member PUB index differs")
        values, offset = [0] * n, 0
        registers = member["registers"]
        require(
            isinstance(registers, list) and bool(registers) and len(set(registers)) == len(registers),
            "invalid register list",
        )
        for register_name in registers:
            register = raw["registers"][register_name]
            width = integer(register["num_bits"], "register width", 1)
            require(offset + width <= 16 and register["num_shots"] == n, "register shape differs")
            bits = register["bitstrings"]
            require(isinstance(bits, list) and len(bits) == n, "raw vector length differs")
            for i, text in enumerate(bits):
                require(
                    isinstance(text, str) and re.fullmatch(rf"[01]{{{width}}}", text) is not None, "invalid bitstring"
                )
                values[i] |= int(text, 2) << offset
            offset += width
        require(1 << offset == len(member["counts"]), "register width differs from histogram")
        histogram = [0] * (1 << offset)
        zero_bits, error_bits = bytearray((n + 7) // 8), bytearray((n + 7) // 8)
        ideal = member["ideal_probabilities"]
        target = ideal.index(1.0) if 1.0 in ideal else None
        for i, value in enumerate(values):
            histogram[value] += 1
            if value == 0:
                zero_bits[i >> 3] |= 1 << (i & 7)
            if target is not None and value != target:
                error_bits[i >> 3] |= 1 << (i & 7)
        require(histogram == member["counts"], "raw histogram differs")
        events[name] = int.from_bytes(zero_bits, "little")
        if target is not None:
            errors[name] = int.from_bytes(error_bits, "little")
        for block in member["shot_order_blocks"]:
            start, stop = block["start_shot"], block["stop_shot_exclusive"]
            require(
                values[start:stop].count(0) == _count(block["event_zero_probability"], stop - start),
                "raw block differs",
            )
    for event, masks in (("event_zero", events), ("deterministic_error", errors)):
        group = pub[event]
        for i, left in enumerate(group["members"]):
            for j, right in enumerate(group["members"]):
                require(
                    (masks[left] & masks[right]).bit_count() == _count(group["joint_probabilities"][i][j], n),
                    "raw joint count differs",
                )
    return {"job_id": pub["job_id"], "pub": pub["name"], "shots": n, "members": len(members), "raw_path": relative}


def verify_sources(
    checked: dict[str, Any],
    root: Path,
    mapper: Callable[[Callable[..., Any], Iterable[Any]], Iterable[Any]] = map,
) -> dict[str, Any]:
    payload = checked["payload"]
    bindings = payload.get("source_files")
    require(isinstance(bindings, dict) and bool(bindings), "no bound source files")
    for relative, expected in bindings.items():
        require(
            sha256(read_bytes(source_path(root, relative))) == _digest(expected), f"source hash differs: {relative}"
        )
    tasks = []
    for pub in payload["pubs"]:
        members = {
            name: member
            for name, member in payload["members"].items()
            if (member["job_id"], member["pub"]) == (pub["job_id"], pub["name"])
        }
        index = next(iter(members.values()))["pub_index"]
        relative = f"raw/{pub['job_id']}/pub_{index:02d}.json"
        require(bindings.get(relative) == pub["raw_sha256"], "raw PUB not covered by source manifest")
        tasks.append((pub, members, str(root.resolve())))
    replays = list(mapper(_raw_pub, tasks))
    for relative, expected in bindings.items():
        require(sha256(read_bytes(source_path(root, relative))) == expected, "bound source changed during replay")
    return {
        **checked,
        "verification": "source_files_and_raw_statistics",
        "source_files_checked": len(bindings),
        "raw_replays": replays,
        "boundary": (
            "QPY bytes are hash-checked when bound; circuit semantics, approval and physical shot chronology "
            "are not re-adjudicated."
        ),
    }


def bloch_region(x: Sequence[float], y: Sequence[float]) -> dict[str, Any]:
    """Project a rectangular X/Y set intersected with the physical Bloch ball."""
    for interval in (x, y):
        require(len(interval) == 2 and all(math.isfinite(v) for v in interval), "invalid coordinate interval")
        require(-1 <= interval[0] <= interval[1] <= 1, "coordinate interval outside expectation support")

    def nearest(interval: Sequence[float]) -> float:
        return max(interval[0], min(0.0, interval[1]))

    rmin = math.hypot(nearest(x), nearest(y))
    if rmin > 1:
        return {"empty": True, "z": None, "minimum_transverse_radius": rmin}
    extent = math.sqrt(max(0.0, (1 - rmin) * (1 + rmin)))
    return {"empty": False, "z": [-extent, extent], "minimum_transverse_radius": rmin}


def load_ramsey(contents: bytes) -> dict[str, Any]:
    rows = list(csv.DictReader(io.StringIO(contents.decode("utf-8"), newline="")))
    require(0 < len(rows) <= 10000, "invalid Ramsey row count")
    seen: set[tuple[str, int, float]] = set()
    out = []
    family_size = 2 * len(rows)
    for row in rows:
        q, t = int(row["physical_qubit"]), float(row["executed_idle_us"])
        integer(q, "physical qubit")
        require(bool(row["condition"]) and len(row["condition"]) <= 512, "invalid condition label")
        key = row["condition"], q, t
        require(key not in seen and math.isfinite(t) and t >= 0, "duplicate or invalid Ramsey setting")
        require(row["timing_qualified"] == "True", "unqualified X/Y timing")
        seen.add(key)
        kx, nx, ky, ny = (int(row[k]) for k in ("x_zero", "x_shots", "y_zero", "y_shots"))
        for k, n in ((kx, nx), (ky, ny)):
            integer(n, "shots", 1)
            require(0 <= k <= n, "count outside support")
        x, y = 2 * kx / nx - 1, 2 * ky / ny - 1
        for value, field in (
            (x, "x_exp"),
            (y, "y_exp"),
            (math.hypot(x, y), "observed_radius"),
            (math.atan2(y, x), "observed_principal_phase_rad"),
        ):
            require(abs(value - float(row[field])) <= 1e-12, "Ramsey count-coordinate mismatch")
        hx, hy = (math.sqrt(2 * math.log(2 * family_size / 0.05) / n) for n in (nx, ny))
        bx, by = [max(-1, x - hx), min(1, x + hx)], [max(-1, y - hy), min(1, y + hy)]
        out.append(
            {
                "condition": key[0],
                "qubit": q,
                "t": t,
                "kx": kx,
                "nx": nx,
                "ky": ky,
                "ny": ny,
                "x": x,
                "y": y,
                "r": math.hypot(x, y),
                "phi": math.atan2(y, x),
                "z": None,
                "simultaneous_x": bx,
                "simultaneous_y": by,
                "compatible_region": bloch_region(bx, by),
            }
        )
    return {"rows": out, "coordinate_family_size": family_size, "alpha": 0.05, "source_sha256": sha256(contents)}


def load_ascella(value: Any, label: str) -> dict[str, Any]:
    schemas = {"ascella-fixed-mesh-confirmation-v1", "ascella-new-mesh-score-v1", "ascella-replication-score-v1"}
    require(isinstance(value, dict) and value.get("schema") in schemas, "unsupported optical cohort schema")
    rows = value.get("rows")
    require(isinstance(rows, list) and 0 < len(rows) <= 10000, "invalid optical cohort rows")
    predictions: set[str] = set()
    for row in rows:
        number(row["observed"], "observed optical statistic")
        fields = {key for key in row if key == "predicted" or key.startswith("predicted_")}
        require(bool(fields), "no frozen predictions")
        predictions.update(fields)
        for key in fields:
            number(row[key], key)
        for key in ("counting_variance", "prediction_variance"):
            if key in row:
                require(number(row[key], key) >= 0, "negative optical variance")
    require(all(all(key in row for key in predictions) for row in rows), "incomplete prediction coverage")
    kind = value.get("evidence_kind", "retained_analysis")
    require(kind in ("synthetic_fixture", "retained_analysis"), "unsupported optical evidence marker")
    return {
        "label": label,
        "prediction_fields": sorted(predictions),
        "payload": value,
        "evidence_kind": kind,
        "scope": "retained_frozen_predictions_no_refit",
    }


def write_new(output: Path, contents: bytes, protected: list[Path]) -> None:
    destination = output.resolve()
    for source in protected:
        path = source.resolve()
        require(
            destination != path and not (source.is_dir() and destination.is_relative_to(path)),
            "output aliases protected input",
        )
        if output.exists() and source.is_file():
            require(not output.samefile(source), "hard-link output alias")
    require(not output.exists() and not output.is_symlink(), "output already exists; choose a successor path")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".evidence-workbench-", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, output)
    finally:
        Path(name).unlink(missing_ok=True)
