"""Check a caller-anchored sparse projection receipt against raw bytes and QPY.

The verifier establishes internal consistency only. The caller must obtain the
receipt anchor through an independent trusted channel and separately validate
provider provenance, approval, layout, preparation and same-shot alignment.
QPY decoding requires trusted, resource-bounded input: the encoded byte limit
and post-decode checks cannot bound the decoder's peak memory or runtime.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import json
import re
from typing import Any

from qiskit import qpy
from readout_sparse_projection import project_pub

RECEIPT_FIELDS = {
    "schema",
    "family",
    "job_id",
    "pub_index",
    "pub_name",
    "circuit_name",
    "raw_pub_filename",
    "raw_pub_sha256",
    "raw_index_sha256",
    "qpy_sha256",
    "manifest_sha256",
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_collection_sources(collection: dict[str, Any]) -> None:
    """Validate newer collector identities while accepting v1 records without either field."""
    has_sources = "collection_source_sha256" in collection
    has_digest = "collection_digest" in collection
    if not has_sources and not has_digest:
        return
    if not has_sources or not has_digest:
        raise ValueError("collector source identity is incomplete")
    sources = collection["collection_source_sha256"]
    if (
        type(sources) is not dict
        or not sources
        or any(
            type(name) is not str or not name or type(value) is not str or not SHA256_PATTERN.fullmatch(value)
            for name, value in sources.items()
        )
    ):
        raise ValueError("collector source identity is malformed")
    encoded = (json.dumps(sources, sort_keys=True, indent=1, allow_nan=False) + "\n").encode()
    if collection["collection_digest"] != _digest(encoded):
        raise ValueError("collector source digest differs")


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON numbers are unsupported")


def _json_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_object, parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{label} is not a UTF-8 JSON object") from error
    if type(value) is not dict:
        raise ValueError(f"{label} must be a JSON object")
    return value


def _check_bytes(data: bytes, maximum: int, label: str) -> None:
    if type(data) is not bytes or not 0 < len(data) <= maximum:
        raise ValueError(f"{label} must be nonempty bounded bytes")


def _check_hash(expected: Any, data: bytes, label: str) -> None:
    if type(expected) is not str or SHA256_PATTERN.fullmatch(expected) is None:
        raise ValueError(f"{label} digest must be lowercase SHA-256")
    if not hmac.compare_digest(expected, _digest(data)):
        raise ValueError(f"{label} digest differs from supplied bytes")


def _measurement_count(qpy_bytes: bytes, circuit_name: str, manifest: dict[str, Any]) -> int:
    try:
        circuits = qpy.load(io.BytesIO(qpy_bytes))
    except Exception as error:
        raise ValueError("QPY cannot be decoded") from error
    if len(circuits) > 1024 or any(
        circuit.num_qubits > 4096 or circuit.num_clbits > 4096 or len(circuit.data) > 100_000 for circuit in circuits
    ):
        raise ValueError("decoded QPY exceeds the circuit resource limits")
    candidates = [circuit for circuit in circuits if circuit.name == circuit_name]
    if len(candidates) != 1:
        raise ValueError("QPY must contain exactly one circuit with the declared name")
    circuit = candidates[0]
    widths = manifest.get("registers")
    bits = manifest.get("bits")
    if type(widths) is not dict or type(bits) is not list:
        raise ValueError("manifest must declare registers and bit mappings")
    registers = {register.name: len(register) for register in circuit.cregs}
    if len(registers) != len(circuit.cregs) or registers != widths:
        raise ValueError("QPY classical registers differ from the manifest")
    destinations: dict[Any, tuple[str, int]] = {}
    for register in circuit.cregs:
        for index, bit in enumerate(register):
            if bit in destinations:
                raise ValueError("QPY classical registers overlap")
            destinations[bit] = (register.name, index)
    expected: dict[tuple[str, int], int] = {}
    for bit in bits:
        if type(bit) is not dict or not {"register", "index", "physical"} <= set(bit):
            raise ValueError("manifest measurement mapping is incomplete")
        if type(bit["register"]) is not str or type(bit["index"]) is not int or type(bit["physical"]) is not int:
            raise ValueError("manifest measurement mapping has invalid types")
        key = (bit["register"], bit["index"])
        if key in expected:
            raise ValueError("manifest has duplicate measurement destinations")
        expected[key] = bit["physical"]
    measured: dict[tuple[str, int], int] = {}
    for instruction in circuit.data:
        name = instruction.operation.name
        if name not in {"x", "delay", "barrier", "measure"}:
            raise ValueError(f"unsupported QPY instruction for actor-reporter family: {name}")
        if name != "measure":
            continue
        if len(instruction.qubits) != 1 or len(instruction.clbits) != 1 or instruction.clbits[0] not in destinations:
            raise ValueError("QPY measurement has an invalid destination")
        destination = destinations[instruction.clbits[0]]
        if destination in measured:
            raise ValueError("QPY repeats a measurement destination")
        measured[destination] = circuit.find_bit(instruction.qubits[0]).index
    if measured != expected:
        raise ValueError("QPY measurement wire-to-register mapping differs from the manifest")
    return len(measured)


def verify_and_project(
    raw_pub_bytes: bytes,
    raw_index_bytes: bytes,
    qpy_bytes: bytes,
    manifest_bytes: bytes,
    receipt_bytes: bytes,
    receipt_sha256_anchor: str,
) -> dict[str, Any]:
    """Verify byte bindings and QPY wire mapping before descriptive projection."""
    for data, maximum, label in (
        (raw_pub_bytes, 256 * 1024 * 1024, "raw PUB"),
        (raw_index_bytes, 4 * 1024 * 1024, "raw index"),
        (qpy_bytes, 32 * 1024 * 1024, "QPY"),
        (manifest_bytes, 4 * 1024 * 1024, "projection manifest"),
        (receipt_bytes, 1024 * 1024, "receipt"),
    ):
        _check_bytes(data, maximum, label)
    _check_hash(receipt_sha256_anchor, receipt_bytes, "receipt anchor")
    receipt = _json_object(receipt_bytes, "receipt")
    if set(receipt) != RECEIPT_FIELDS or receipt["schema"] != "readout-sparse-receipt-v1":
        raise ValueError("a complete supported receipt is required")
    if receipt["family"] != "actor-reporter":
        raise ValueError("unsupported experiment family")
    if any(
        type(receipt[field]) is not str or not receipt[field] or len(receipt[field]) > 256
        for field in ("job_id", "pub_name", "circuit_name")
    ):
        raise ValueError("receipt job, PUB and circuit identities must be bounded strings")
    if receipt["circuit_name"] != receipt["pub_name"]:
        raise ValueError("QPY circuit name must match the raw PUB name")
    if type(receipt["pub_index"]) is not int or not 0 <= receipt["pub_index"] <= 1_000_000:
        raise ValueError("receipt PUB index is invalid")
    expected_filename = f"pub_{receipt['pub_index']:02d}.json"
    if receipt["raw_pub_filename"] != expected_filename:
        raise ValueError("raw PUB filename differs from its declared index")
    for field, data in (
        ("raw_pub_sha256", raw_pub_bytes),
        ("raw_index_sha256", raw_index_bytes),
        ("qpy_sha256", qpy_bytes),
        ("manifest_sha256", manifest_bytes),
    ):
        _check_hash(receipt[field], data, field)
    index = _json_object(raw_index_bytes, "raw index")
    if index.get("job_id") != receipt["job_id"] or type(index.get("files")) is not dict:
        raise ValueError("raw index job identity or file listing is invalid")
    if index["files"].get(expected_filename) != receipt["raw_pub_sha256"]:
        raise ValueError("raw index does not bind the expected PUB bytes")
    manifest = _json_object(manifest_bytes, "projection manifest")
    raw_pub = _json_object(raw_pub_bytes, "raw PUB")
    if manifest.get("pub_name") != receipt["pub_name"] or manifest.get("pub_index") != receipt["pub_index"]:
        raise ValueError("projection manifest PUB identity differs from the receipt")
    if (
        raw_pub.get("pub_name") != receipt["pub_name"]
        or type(raw_pub.get("pub_index")) is not int
        or raw_pub["pub_index"] != receipt["pub_index"]
    ):
        raise ValueError("raw PUB identity differs from the receipt")
    measurements = _measurement_count(qpy_bytes, receipt["circuit_name"], manifest)
    return {
        "schema": "readout-sparse-receipt-verification-v1",
        "receipt_sha256": receipt_sha256_anchor,
        "manifest_bytes_sha256": receipt["manifest_sha256"],
        "verified_measurements": measurements,
        "projection": project_pub(raw_pub, manifest),
        "boundary": (
            "Internal byte and QPY wire consistency only; independent receipt provenance, approval, physical layout, "
            "preparation semantics, provider same-shot alignment and statistical admission remain unverified."
        ),
    }
