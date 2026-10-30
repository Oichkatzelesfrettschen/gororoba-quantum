"""Check a one-job provider source-to-result association without provider access.

The caller must authenticate and retain the observations and bind the checkpoint
to the approved case. The association predicate alone does not validate raw
shots, acquisition time, or the physical execution schedule. The caller must
prevent concurrent mutation of the supplied records while validation runs.
"""

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping
from typing import Any

from qi_tuna_sequential_score import decode_counts


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON object has duplicate keys")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant {value}")


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite JSON number")
    return parsed


def _json_object(data: bytes) -> dict[str, Any]:
    if type(data) is not bytes or not 0 < len(data) <= 2 * 1024 * 1024:
        raise ValueError("JSON bytes are empty, oversized or invalid")
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("JSON bytes are malformed") from error
    if type(value) is not dict:
        raise ValueError("JSON root must be an object")
    return value


def validate_slot_binding(
    catalogue_bytes: bytes,
    expected_catalogue_sha256: str,
    slot: int,
    arm: str,
    manifest_bytes: bytes,
    source: bytes,
) -> None:
    """Bind one supplied slot and arm to catalogue, manifest and source bytes.

    The caller must authenticate the catalogue digest and assignment release.
    This function does not establish concealment, fairness or authorization.
    """
    if type(expected_catalogue_sha256) is not str or type(catalogue_bytes) is not bytes:
        raise ValueError("catalogue digest or bytes have invalid types")
    if hashlib.sha256(catalogue_bytes).hexdigest() != expected_catalogue_sha256:
        raise ValueError("catalogue digest differs")
    if type(slot) is not int or not 1 <= slot <= 24 or type(arm) is not str or arm not in ("baseline", "rotated"):
        raise ValueError("slot or arm is invalid")
    catalogue = _json_object(catalogue_bytes)
    slot_count = catalogue.get("slots")
    if (
        catalogue.get("schema") != "qi-tuna-destination-slot-alternatives-v1"
        or type(slot_count) is not int
        or slot_count != 24
    ):
        raise ValueError("catalogue schema or slot count differs")
    alternatives = catalogue.get("alternatives")
    if type(alternatives) is not list:
        raise ValueError("catalogue alternatives are invalid")
    matches = [row for row in alternatives if type(row) is dict and row.get("slot") == slot and row.get("arm") == arm]
    if len(matches) != 1 or type(matches[0].get("slot")) is not int:
        raise ValueError("catalogue needs exactly one selected alternative")
    selected = matches[0]
    if selected.get("directory") != f"slot-{slot:02d}/{arm}":
        raise ValueError("selected catalogue directory differs")
    if type(manifest_bytes) is not bytes or hashlib.sha256(manifest_bytes).hexdigest() != selected.get("cases_sha256"):
        raise ValueError("selected manifest differs from catalogue")
    manifest = _json_object(manifest_bytes)
    if (
        manifest.get("schema") != "qi-tuna-destination-slot-alternative-v1"
        or type(manifest.get("slot")) is not int
        or manifest["slot"] != slot
        or manifest.get("comparison_arm") != arm
        or manifest.get("backend") != "tuna_17"
        or type(manifest.get("backend_type_id")) is not int
        or manifest["backend_type_id"] != 7
        or type(manifest.get("shots")) is not int
        or manifest["shots"] != 4096
    ):
        raise ValueError("selected manifest case identity differs")
    circuits = manifest.get("circuits")
    if type(circuits) is not list or len(circuits) != 1 or type(circuits[0]) is not dict:
        raise ValueError("selected manifest needs one circuit")
    if type(source) is not bytes or hashlib.sha256(source).hexdigest() != circuits[0].get("sha256"):
        raise ValueError("selected source differs from manifest")


def _positive_integer(record: Mapping[str, object], name: str) -> int:
    if type(record) is not dict:
        raise ValueError("record must be a plain JSON object")
    value = record.get(name)
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _single_page(page: Mapping[str, object]) -> Mapping[str, object]:
    if type(page) is not dict:
        raise ValueError("page must be a plain JSON object")
    for field in ("total", "page", "pages"):
        value = page.get(field)
        if type(value) is not int or value != 1:
            raise ValueError("page must describe exactly one complete page")
    size = _positive_integer(page, "size")
    if size > 100:
        raise ValueError("page size exceeds the endpoint limit")
    items = page.get("items")
    if type(items) is not list or len(items) != 1:
        raise ValueError("page must contain exactly one mapping")
    item = items[0]
    if type(item) is not dict:
        raise ValueError("page must contain exactly one mapping")
    return item


def validate_batch_page(page: Mapping[str, object], *, expected_batch_id: int) -> Mapping[str, object]:
    """Check one batch page; the caller authenticates the query and read."""
    if type(expected_batch_id) is not int or expected_batch_id < 1:
        raise ValueError("expected batch identity must be a positive integer")
    batch = _single_page(page)
    if _positive_integer(batch, "id") != expected_batch_id:
        raise ValueError("batch page identity differs from the checkpoint")
    return batch


def validate_result_page(
    page: Mapping[str, object], *, expected_job_id: int, expected_result_id: int
) -> Mapping[str, object]:
    """Check one complete, single-result page; the caller authenticates the read."""
    if type(expected_job_id) is not int or expected_job_id < 1:
        raise ValueError("expected job identity must be a positive integer")
    if type(expected_result_id) is not int or expected_result_id < 1:
        raise ValueError("expected result identity must be a positive integer")
    result = _single_page(page)
    if _positive_integer(result, "id") != expected_result_id or _positive_integer(result, "job_id") != expected_job_id:
        raise ValueError("result page identity differs from the checkpoint")
    return result


def validate_association(
    checkpoint: Mapping[str, object],
    source: bytes,
    job: Mapping[str, object],
    batch: Mapping[str, object],
    provider_file: Mapping[str, object],
    result_page: Mapping[str, object],
) -> None:
    """Require exact IDs and source text for one checkpointed job."""
    job_id = _positive_integer(checkpoint, "job")
    file_id = _positive_integer(checkpoint, "file")
    commit_id = _positive_integer(checkpoint, "commit")
    batch_id = _positive_integer(checkpoint, "batch")
    backend_type = _positive_integer(checkpoint, "backend_type")
    shots = _positive_integer(checkpoint, "shots")
    language_id = _positive_integer(checkpoint, "language_id")
    result_id = _positive_integer(checkpoint, "result")
    validate_result_page(result_page, expected_job_id=job_id, expected_result_id=result_id)
    digest = checkpoint.get("source_sha256")
    if type(source) is not bytes or type(digest) is not str or hashlib.sha256(source).hexdigest() != digest:
        raise ValueError("source does not match checkpoint digest")
    try:
        source_text = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("source is not UTF-8") from error
    expected_fields = (
        (job, "id", job_id),
        (job, "file_id", file_id),
        (job, "batch_job_id", batch_id),
        (job, "number_of_shots", shots),
        (batch, "id", batch_id),
        (batch, "backend_type_id", backend_type),
        (provider_file, "id", file_id),
        (provider_file, "commit_id", commit_id),
        (provider_file, "language_id", language_id),
    )
    for record, field, expected in expected_fields:
        if _positive_integer(record, field) != expected:
            raise ValueError(f"provider {field} differs from checkpoint")
    if job.get("raw_data_enabled") is not True:
        raise ValueError("job does not enable raw data")
    job_ids = batch.get("job_ids")
    if type(job_ids) is not list or len(job_ids) != 1:
        raise ValueError("batch does not contain exactly the checkpointed job")
    only_job = job_ids[0]
    if type(only_job) is not int or only_job != job_id:
        raise ValueError("batch does not contain exactly the checkpointed job")
    content = provider_file.get("content")
    if type(content) is not str or content != source_text:
        raise ValueError("provider source content differs from checked bytes")
    compile_stage = provider_file.get("compile_stage")
    compile_properties = provider_file.get("compile_properties")
    if type(compile_stage) is not str or compile_stage != "none":
        raise ValueError("provider compile stage differs")
    if type(compile_properties) is not dict or compile_properties:
        raise ValueError("provider compile properties differ")


def validate_slot_association(
    catalogue_bytes: bytes,
    expected_catalogue_sha256: str,
    slot: int,
    arm: str,
    manifest_bytes: bytes,
    source: bytes,
    checkpoint: Mapping[str, object],
    job: Mapping[str, object],
    batch_page: Mapping[str, object],
    provider_file: Mapping[str, object],
    result_page: Mapping[str, object],
) -> None:
    """Bind a released slot's supplied source to its supplied provider readbacks."""
    validate_slot_binding(catalogue_bytes, expected_catalogue_sha256, slot, arm, manifest_bytes, source)
    if _positive_integer(checkpoint, "slot") != slot:
        raise ValueError("checkpoint slot differs from the released slot")
    for field, expected in (
        ("arm", arm),
        ("cases_sha256", hashlib.sha256(manifest_bytes).hexdigest()),
        ("catalogue_sha256", expected_catalogue_sha256),
    ):
        value = checkpoint.get(field)
        if type(value) is not str or value != expected:
            raise ValueError(f"checkpoint {field} differs from the released slot")
    if _positive_integer(checkpoint, "backend_type") != 7 or _positive_integer(checkpoint, "shots") != 4096:
        raise ValueError("checkpoint differs from the selected Tuna case envelope")
    batch = validate_batch_page(batch_page, expected_batch_id=_positive_integer(checkpoint, "batch"))
    validate_association(checkpoint, source, job, batch, provider_file, result_page)


def decode_associated_complete(
    catalogue_bytes: bytes,
    expected_catalogue_sha256: str,
    slot: int,
    arm: str,
    manifest_bytes: bytes,
    source: bytes,
    checkpoint: Mapping[str, object],
    job: Mapping[str, object],
    batch_page: Mapping[str, object],
    provider_file: Mapping[str, object],
    result_page: Mapping[str, object],
) -> dict[str, Any]:
    """Decode a source-associated complete record without admitting its timing or origin."""
    validate_slot_association(
        catalogue_bytes,
        expected_catalogue_sha256,
        slot,
        arm,
        manifest_bytes,
        source,
        checkpoint,
        job,
        batch_page,
        provider_file,
        result_page,
    )
    status = job.get("status")
    if type(status) is not str or status != "completed":
        raise ValueError("job is not completed")
    result = validate_result_page(
        result_page,
        expected_job_id=_positive_integer(checkpoint, "job"),
        expected_result_id=_positive_integer(checkpoint, "result"),
    )
    if _positive_integer(result, "shots_requested") != 4096 or _positive_integer(result, "shots_done") != 4096:
        raise ValueError("result shot counts do not match the complete case")
    raw = result.get("raw_data")
    if (
        type(raw) is not list
        or len(raw) != 4096
        or any(type(shot) is not str or len(shot) != 20 or bool(set(shot) - {"0", "1"}) for shot in raw)
    ):
        raise ValueError("complete result needs 4096 ordered 20-bit binary shots")
    manifest = _json_object(manifest_bytes)
    metadata = manifest["circuits"][0].get("analysis_metadata")
    if type(metadata) is not dict or type(metadata.get("width")) is not int or metadata["width"] != 20:
        raise ValueError("manifest decoder width differs")
    expected_early = [17, 18, 19] if arm == "baseline" else [19, 17, 18]
    for field, expected_text in (
        ("bit_order", "classical bit zero is the rightmost character"),
        ("index_convention", "zero-based string offsets from the left"),
        ("decoder_rule", "Read qubits through declared destinations; inverse-permute the rotated arm."),
    ):
        value = metadata.get(field)
        if type(value) is not str or value != expected_text:
            raise ValueError(f"manifest decoder {field} differs")
    for field, expected_bits in (
        ("canonical_early_qubit_order", [4, 11, 6]),
        ("canonical_early_classical_bits", expected_early),
        ("canonical_early_string_offsets", [19 - bit for bit in expected_early]),
        ("terminal_classical_bits", list(range(17))),
    ):
        value = metadata.get(field)
        if type(value) is not list or any(type(item) is not int for item in value) or value != expected_bits:
            raise ValueError(f"manifest decoder {field} differs")
    mapping = manifest["circuits"][0].get("measurement_to_bit_map")
    expected_map = [
        {"qubit": qubit, "classical_bit": bit} for qubit, bit in zip((4, 11, 6), expected_early, strict=True)
    ] + [{"qubit": bit, "classical_bit": bit} for bit in range(17)]
    if (
        type(mapping) is not list
        or any(
            type(item) is not dict
            or set(item) != {"qubit", "classical_bit"}
            or any(type(value) is not int for value in item.values())
            for item in mapping
        )
        or mapping != expected_map
    ):
        raise ValueError("manifest measurement-to-bit map differs")
    counts = decode_counts(arm, raw)
    expected_counts = {
        "early_ones": sum(shot[19 - expected_early[2]] == "1" for shot in raw),
        "terminal_ones": sum(shot[19 - 6] == "1" for shot in raw),
    }
    if (
        type(counts) is not dict
        or any(type(value) is not int for value in counts.values())
        or counts != expected_counts
    ):
        raise ValueError("decoder output differs from manifest destination counts")
    histogram = result.get("results")
    if type(histogram) is not dict or any(
        type(key) is not str or len(key) != 20 or bool(set(key) - {"0", "1"}) or type(value) is not int or value < 0
        for key, value in histogram.items()
    ):
        raise ValueError("result histogram is malformed")
    if type(raw) is not list or Counter(raw) != Counter(histogram):
        raise ValueError("result histogram differs from ordered raw shots")
    return {"slot": slot, "arm": arm, "kind": "complete", **counts}


def decode_associated_complete_bytes(
    catalogue_bytes: bytes,
    expected_catalogue_sha256: str,
    slot: int,
    arm: str,
    manifest_bytes: bytes,
    source: bytes,
    checkpoint_bytes: bytes,
    job_bytes: bytes,
    batch_page_bytes: bytes,
    provider_file_bytes: bytes,
    result_page_bytes: bytes,
) -> dict[str, Any]:
    """Decode owned JSON snapshots; the caller authenticates and retains the bytes."""
    return decode_associated_complete(
        catalogue_bytes,
        expected_catalogue_sha256,
        slot,
        arm,
        manifest_bytes,
        source,
        _json_object(checkpoint_bytes),
        _json_object(job_bytes),
        _json_object(batch_page_bytes),
        _json_object(provider_file_bytes),
        _json_object(result_page_bytes),
    )
