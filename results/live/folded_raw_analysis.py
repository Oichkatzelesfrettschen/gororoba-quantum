"""Describe ordered folded-ladder shots without fitting a causal or drift model."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, cast

BLOCK_SHOTS = 512
RUNGS = ("archived", "delay", "no_feed_forward", "coherent")
MEMBER_PATTERN = re.compile(r"qpe_(archived|delay|no_feed_forward|coherent)_s([0-3])")
EXPECTED_MEMBERS = {f"qpe_{rung}_s{label}" for rung in RUNGS for label in range(4)}
DIGEST_PATTERN = re.compile(r"[0-9a-f]{64}")
IDENTIFIER_PATTERN = re.compile(r"[A-Za-z0-9_-]+")
SCHEMA_CONTRACT = "live-target-statistical-design-invocation-budget-v1"


class AnalysisError(ValueError):
    """A required identity, digest, shape, or sample count failed validation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AnalysisError(message)


def object_value(value: Any, context: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{context}: expected an object")
    return dict(value)


def list_value(value: Any, context: str) -> list[Any]:
    require(isinstance(value, list), f"{context}: expected an array")
    return list(value)


def string_value(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise AnalysisError(f"{context}: expected a nonempty string")
    return value


def shot_count(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 2:
        raise AnalysisError("record shots must be an integer of at least two")
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"JSON contains duplicate key {key!r}")
        result[key] = value
    return result


def parse_json(data: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(data, object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise AnalysisError(f"{context}: invalid UTF-8 JSON: {error}") from error
    return object_value(value, context)


def safe_child(directory: Path, name: Any) -> Path:
    name = string_value(name, "file name")
    require(name not in (".", ".."), "empty or invalid file name")
    require(Path(name).name == name and "/" not in name and "\\" not in name, f"unsafe file name {name!r}")
    result = directory / str(name)
    require(not result.is_symlink(), f"symbolic link outside supported input domain: {result}")
    require(result.resolve().parent == directory.resolve(), f"path leaves its input directory: {name}")
    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_ledger(submission: dict[str, Any], archive_digest: str) -> None:
    planned_jobs = list_value(submission.get("planned_jobs"), "planned_jobs")
    jobs = list_value(submission.get("jobs"), "jobs")
    require(len(planned_jobs) == len(jobs), "planned/submitted job cardinality differs")
    planned_by_key: dict[tuple[str, str, int, int], dict[str, Any]] = {}
    submitted_keys: set[tuple[str, str, int, int]] = set()
    for entries, destination in ((planned_jobs, "planned"), (jobs, "submitted")):
        for candidate in entries:
            job = object_value(candidate, f"{destination} job")
            backend = string_value(job.get("backend"), "job backend")
            kind = string_value(job.get("kind"), "job kind")
            batch_index, batch_count = job.get("batch_index"), job.get("batch_count")
            require(
                type(batch_index) is int and type(batch_count) is int and 1 <= batch_index <= batch_count,
                "invalid batch identity",
            )
            key = (backend, kind, cast(int, batch_index), cast(int, batch_count))
            require(job.get("qpy_archive_sha256") == archive_digest, "job archive digest differs")
            if destination == "planned":
                require(key not in planned_by_key, "repeated planned job identity")
                planned_by_key[key] = job
            else:
                require(key in planned_by_key and key not in submitted_keys, "unknown or repeated submitted job")
                submitted_keys.add(key)
                for field in (
                    "members",
                    "pubs",
                    "qpy_archive_sha256",
                    "calibrations",
                    "recovery_tags",
                    "options",
                ):
                    require(
                        field in job and field in planned_by_key[key] and job[field] == planned_by_key[key][field],
                        f"submitted job differs from immutable planned ledger in {field}",
                    )


def verify_job_raw(directory: Path, job_id: str, pub_count: int) -> tuple[dict[str, bytes], dict[str, Any], bytes]:
    index_path = safe_child(directory, "index.json")
    index_bytes = index_path.read_bytes()
    index = parse_json(index_bytes, str(index_path))
    require(index.get("job_id") == job_id, f"{job_id}: raw index job identity differs")
    files = object_value(index.get("files"), f"{job_id} index files")
    expected_files = {f"pub_{index:02d}.json" for index in range(pub_count)} | {"result_metadata.json"}
    require(set(files) == expected_files, f"{job_id}: indexed PUB/result files differ from submitted manifest")
    metrics = list_value(index.get("metrics", []), f"{job_id} metrics")
    metric_digests = list_value(index.get("metrics_sha256", []), f"{job_id} metrics_sha256")
    require(len(metrics) == len(metric_digests), f"{job_id}: metric digest cardinality differs")
    require(all(isinstance(name, str) for name in metrics), f"{job_id}: malformed metric file name")
    require(len(set(metrics)) == len(metrics), f"{job_id}: duplicate metric snapshot")
    require(not set(metrics).intersection(files), f"{job_id}: metric and result paths overlap")
    if metrics:
        require(index.get("metrics_latest") in metrics, f"{job_id}: metrics_latest is unindexed")
    else:
        require(index.get("metrics_latest") is None, f"{job_id}: metrics_latest lacks snapshots")
    combined = files | dict(zip(metrics, metric_digests, strict=True))
    payloads: dict[str, bytes] = {}
    for name, digest in combined.items():
        require(
            isinstance(digest, str) and DIGEST_PATTERN.fullmatch(digest) is not None,
            f"{job_id}/{name}: malformed sha256",
        )
        payload = safe_child(directory, name).read_bytes()
        require(sha256(payload) == digest, f"{job_id}/{name}: indexed sha256 mismatch")
        parse_json(payload, f"{job_id}/{name}")
        payloads[name] = payload
    return payloads, {"index_sha256": sha256(index_bytes), "verified_files_sha256": combined}, index_bytes


def lag_one(scores: list[int]) -> tuple[float | None, str | None]:
    require(len(scores) >= 2, "lag-one correlation needs at least two shots")
    earlier, later = scores[:-1], scores[1:]
    count = len(earlier)
    earlier_mean, later_mean = sum(earlier) / count, sum(later) / count
    earlier_variance = math.fsum((score - earlier_mean) ** 2 for score in earlier)
    later_variance = math.fsum((score - later_mean) ** 2 for score in later)
    if earlier_variance == 0 or later_variance == 0:
        return None, "zero variance in at least one lagged vector"
    covariance = math.fsum(
        (left - earlier_mean) * (right - later_mean) for left, right in zip(earlier, later, strict=True)
    )
    correlation = covariance / math.sqrt(earlier_variance * later_variance)
    return max(-1.0, min(1.0, correlation)), None


def decode_member(member: str, register: dict[str, Any], shots: int) -> dict[str, Any]:
    match = MEMBER_PATTERN.fullmatch(member)
    require(match is not None, f"unsupported folded member {member!r}")
    assert match is not None
    rung, label_text = match.groups()
    label = int(label_text)
    width = 1 if rung == "delay" else 2
    terminal_bit = width - 1
    require(type(shots) is int and shots >= 2, "record shots must be an integer of at least two")
    require(
        type(register.get("num_bits")) is int and register["num_bits"] == width,
        f"{member}: register width must equal {width}",
    )
    require(
        type(register.get("num_shots")) is int and register["num_shots"] == shots,
        f"{member}: register shot count differs from record",
    )
    bitstrings = list_value(register.get("bitstrings"), f"{member} bitstrings")
    require(len(bitstrings) == shots, f"{member}: bitstring count differs from record")
    require(
        all(isinstance(bits, str) and re.fullmatch(f"[01]{{{width}}}", bits) is not None for bits in bitstrings),
        f"{member}: malformed bitstring or width",
    )
    outcomes = [int(bits, 2) for bits in bitstrings]
    counts = Counter(outcomes)
    probabilities = [counts[outcome] / shots for outcome in range(1 << width)]
    require(
        sum(counts.values()) == shots and math.isclose(math.fsum(probabilities), 1.0, rel_tol=0, abs_tol=1e-12),
        f"{member}: outcome distribution is not normalized",
    )
    expected_terminal = label // 2
    scores = [int(((outcome >> terminal_bit) & 1) == expected_terminal) for outcome in outcomes]
    midpoint = shots // 2
    earlier_mean = sum(scores[:midpoint]) / midpoint
    later_mean = sum(scores[midpoint:]) / (shots - midpoint)
    correlation, correlation_withheld = lag_one(scores)
    return {
        "member": member,
        "rung": rung,
        "label": label,
        "register_width": width,
        "terminal_bit_index": terminal_bit,
        "expected_terminal_bit": expected_terminal,
        "shots": shots,
        "outcome_counts_by_integer_index": [counts[outcome] for outcome in range(1 << width)],
        "outcome_probabilities_by_integer_index": probabilities,
        "terminal_correct_count": sum(scores),
        "terminal_correct_mean": sum(scores) / shots,
        "blocks": [
            {
                "start_shot_inclusive": start,
                "stop_shot_exclusive": min(start + BLOCK_SHOTS, shots),
                "shots": len(scores[start : start + BLOCK_SHOTS]),
                "terminal_correct_mean": sum(scores[start : start + BLOCK_SHOTS])
                / len(scores[start : start + BLOCK_SHOTS]),
            }
            for start in range(0, shots, BLOCK_SHOTS)
        ],
        "half_comparison": {
            "early_shots": midpoint,
            "late_shots": shots - midpoint,
            "early_mean": earlier_mean,
            "late_mean": later_mean,
            "late_minus_early": later_mean - earlier_mean,
        },
        "lag_one_pearson": correlation,
        "lag_one_withheld": correlation_withheld,
    }


def analyze(run_directory: Path) -> dict[str, Any]:
    source_path = Path(__file__)
    source_bytes = source_path.read_bytes()
    run_directory = run_directory.resolve()
    record_path = safe_child(run_directory, "record.json")
    record_bytes = record_path.read_bytes()
    record = parse_json(record_bytes, "record.json")
    require(
        type(record.get("schema_version")) is int
        and record["schema_version"] == 7
        and record.get("schema_contract") == SCHEMA_CONTRACT,
        "unsupported record schema",
    )
    experiment_digest = string_value(record.get("experiment_digest"), "experiment_digest")
    require(DIGEST_PATTERN.fullmatch(experiment_digest) is not None, "malformed experiment digest")
    family = object_value(record.get("family_configuration"), "family_configuration")
    require(family.get("name") == "folded-qpe", "record must name the folded-qpe family")
    shots = shot_count(record.get("shots"))
    submission = object_value(record.get("submission"), "submission")
    require(submission.get("complete") is True, "submission must be complete")
    archive_digest = string_value(submission.get("qpy_archive_sha256"), "qpy_archive_sha256")
    require(DIGEST_PATTERN.fullmatch(archive_digest) is not None, "malformed archive digest")
    archive_path = safe_child(run_directory, "isa.qpy")
    archive_bytes = archive_path.read_bytes()
    require(sha256(archive_bytes) == archive_digest, "isa.qpy differs from submission archive digest")
    validate_ledger(submission, archive_digest)
    jobs = list_value(submission.get("jobs"), "submission jobs")
    require(bool(jobs), "submission needs recorded jobs")
    planned: dict[str, dict[str, Any]] = {}
    for candidate in list_value(record.get("execution_pubs"), "execution_pubs"):
        pub = object_value(candidate, "planned PUB")
        name = string_value(pub.get("name"), "planned PUB name")
        require(
            isinstance(name, str) and bool(name) and name not in planned,
            "planned PUB names must be unique strings",
        )
        planned[name] = pub
    require(len(planned) == 16, "analysis requires the sixteen separate folded PUBs")
    raw_directory = safe_child(run_directory, "raw")
    seen_jobs: set[str] = set()
    seen_pubs: set[str] = set()
    rows: dict[str, dict[str, Any]] = {}
    job_evidence: dict[str, Any] = {}
    snapshots: list[tuple[Path, bytes]] = [
        (record_path, record_bytes),
        (source_path, source_bytes),
        (archive_path, archive_bytes),
    ]
    for candidate in jobs:
        job = object_value(candidate, "submitted job")
        job_id = string_value(job.get("job_id"), "job_id")
        require(
            isinstance(job_id, str) and IDENTIFIER_PATTERN.fullmatch(job_id) is not None and job_id not in seen_jobs,
            "job identifiers must be unique safe strings",
        )
        seen_jobs.add(job_id)
        pubs = list_value(job.get("pubs"), f"{job_id} pubs")
        require(bool(pubs), f"{job_id}: empty job")
        directory = safe_child(raw_directory, job_id)
        payloads, evidence, index_bytes = verify_job_raw(directory, job_id, len(pubs))
        snapshots.append((directory / "index.json", index_bytes))
        snapshots.extend((directory / name, payload) for name, payload in payloads.items())
        job_evidence[job_id] = evidence
        for pub_index, candidate_pub in enumerate(pubs):
            pub = object_value(candidate_pub, f"{job_id} PUB {pub_index}")
            pub_name = string_value(pub.get("name"), "submitted PUB name")
            require(
                isinstance(pub_name, str) and pub_name in planned and pub_name not in seen_pubs,
                f"{job_id}: unknown or repeated submitted PUB",
            )
            require(pub == planned[pub_name], f"{pub_name}: submitted and planned manifests differ")
            seen_pubs.add(pub_name)
            components = list_value(pub.get("components"), f"{pub_name} components")
            require(len(components) == 1, f"{pub_name}: analysis supports one member per PUB")
            component = object_value(components[0], f"{pub_name} component")
            member = string_value(component.get("member"), "folded member")
            require(
                isinstance(member, str) and member in EXPECTED_MEMBERS and member not in rows,
                f"{pub_name}: unknown or repeated folded member",
            )
            require(
                component.get("reference") is False,
                f"{member}: isolated reference is outside the analysis domain",
            )
            replicas = list_value(component.get("registers_by_replica"), f"{member} registers_by_replica")
            require(len(replicas) == 1, f"{member}: analysis requires exactly one replica")
            registers = list_value(replicas[0], f"{member} replica registers")
            require(
                len(registers) == 1 and isinstance(registers[0], str),
                f"{member}: analysis requires one mapped classical register",
            )
            register_name = registers[0]
            payload = parse_json(payloads[f"pub_{pub_index:02d}.json"], f"{job_id} PUB {pub_index}")
            require(
                type(payload.get("pub_index")) is int
                and payload["pub_index"] == pub_index
                and payload.get("pub_name") == pub_name,
                f"{member}: raw PUB identity differs from manifest",
            )
            raw_registers = object_value(payload.get("registers"), f"{member} raw registers")
            require(set(raw_registers) == {register_name}, f"{member}: raw registers differ from manifest mapping")
            row = decode_member(member, object_value(raw_registers[register_name], f"{member} register"), shots)
            rows[member] = row | {
                "job_id": job_id,
                "pub_name": pub_name,
                "pub_index_within_job": pub_index,
                "register_name": register_name,
            }
    require(
        set(rows) == EXPECTED_MEMBERS and seen_pubs == set(planned),
        "folded member or PUB coverage is incomplete",
    )
    for path, original in snapshots:
        require(
            path.read_bytes() == original,
            f"input changed during analysis; rerun after collection settles: {path}",
        )
    return {
        "analysis_kind": "supplemental exploratory folded-ladder shot-order diagnostics",
        "scientific_boundary": [
            "Descriptive summaries carry neither p-values nor causal or stationarity claims.",
            "Shot indices remain local to each PUB; separate PUBs are neither paired nor assumed simultaneous.",
            "Block indices describe shot order, without reconstructing physical shot times.",
            "The complete preregistered family analysis remains authoritative "
            "for its declared contrasts and intervals.",
        ],
        "block_shots": BLOCK_SHOTS,
        "half_difference_direction": "late minus early; an odd final shot belongs to the late half",
        "lag_one_definition": "Pearson correlation between scores[:-1] and scores[1:], separately centered",
        "record_sha256": sha256(record_bytes),
        "experiment_digest": experiment_digest,
        "qpy_archive_sha256": archive_digest,
        "source_sha256": sha256(source_bytes),
        "jobs": job_evidence,
        "members": [rows[f"qpe_{rung}_s{label}"] for rung in RUNGS for label in range(4)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    arguments = parser.parse_args()
    try:
        result = analyze(arguments.run_directory)
    except (AnalysisError, OSError) as error:
        print(f"analysis failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
