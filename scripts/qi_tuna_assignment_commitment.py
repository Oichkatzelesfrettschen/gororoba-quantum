"""Offline commitment arithmetic for a prospective, unapproved Tuna assignment.

The functions establish byte consistency only. They do not authenticate a QRNG
response, prove entropy or fairness, witness a commitment time, protect secrets,
enforce release deadlines, or grant provider execution authority.
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import re
from typing import Any

import anu_qrng

DOMAIN = b"gororoba-qi-tuna-assignment-v1\0"
DRAW_LIMIT_BYTES = 1024 * 1024
SLOTS = 24


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Refuse JSON objects whose interpretation depends on duplicate-key policy."""
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("duplicate JSON key in draw")
        result[name] = value
    return result


def reject_constant(value: str) -> None:
    """Refuse nonstandard JSON number constants."""
    raise ValueError(f"nonstandard JSON constant: {value}")


def draw_values(record_bytes: bytes) -> list[int]:
    """Validate the exact 24-value ANU record without asserting origin or fairness."""
    if type(record_bytes) is not bytes or not 0 < len(record_bytes) <= DRAW_LIMIT_BYTES:
        raise ValueError("draw record bytes are missing or oversized")
    try:
        record = json.loads(
            record_bytes.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant
        )
        if not isinstance(record, dict) or set(record) != {
            "schema",
            "source",
            "retrieved_utc",
            "raw",
            "raw_sha256",
            "type",
            "values",
        }:
            raise ValueError("draw record shape differs")
        if record["source"] not in {f"{endpoint}?length=24&type=uint16" for endpoint in anu_qrng.ENDPOINTS.values()}:
            raise ValueError("draw endpoint or requested length differs")
        if type(record["retrieved_utc"]) is not str:
            raise ValueError("draw timestamp is not a string")
        timestamp = datetime.datetime.strptime(record["retrieved_utc"], "%Y-%m-%dT%H%M%SZ")
        if timestamp.strftime("%Y-%m-%dT%H%M%SZ") != record["retrieved_utc"]:
            raise ValueError("draw timestamp is not in the adapter's canonical form")
        if record["type"] != "uint16" or not isinstance(record["raw"], str):
            raise ValueError("draw type or raw JSON differs")
        raw_answer = json.loads(record["raw"], object_pairs_hook=unique_object, parse_constant=reject_constant)
        if (
            not isinstance(raw_answer, dict)
            or not isinstance(raw_answer.get("data"), list)
            or any(type(value) is not int or not 0 <= value <= 65535 for value in raw_answer["data"])
        ):
            raise ValueError("raw ANU data must be an array of uint16 integers")
        anu_qrng.admit(record)
        values = record["values"]
        if not isinstance(values, list) or len(values) != SLOTS or any(type(value) is not int for value in values):
            raise ValueError("draw must hold exactly 24 integer values")
        return values
    except (UnicodeError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("draw record is malformed") from error


def commitment(record_bytes: bytes, salt: bytes, catalogue_sha256: bytes) -> str:
    """Commit to exact draw bytes and catalogue using a caller-supplied 32-byte salt."""
    draw_values(record_bytes)
    if type(salt) is not bytes or len(salt) != 32 or type(catalogue_sha256) is not bytes or len(catalogue_sha256) != 32:
        raise ValueError("salt and catalogue digest must each be exactly 32 bytes")
    payload = DOMAIN + salt + catalogue_sha256 + len(record_bytes).to_bytes(8, "big") + record_bytes
    return hashlib.sha256(payload).hexdigest()


def verify_opening(
    record_bytes: bytes, salt: bytes, catalogue_sha256: bytes, expected: str, releases: list[dict[str, Any]]
) -> None:
    """Verify a post-stop opening and its contiguous released prefix, without returning future arms."""
    if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
        raise ValueError("commitment must be a lowercase SHA-256 digest")
    if not hmac.compare_digest(commitment(record_bytes, salt, catalogue_sha256), expected):
        raise ValueError("opening differs from commitment")
    values = draw_values(record_bytes)
    if not isinstance(releases, list) or len(releases) > SLOTS:
        raise ValueError("released assignment prefix is invalid")
    for slot, release in enumerate(releases, start=1):
        if (
            not isinstance(release, dict)
            or set(release) != {"slot", "arm"}
            or type(release.get("slot")) is not int
            or release["slot"] != slot
            or release.get("arm") != ("rotated" if values[slot - 1] & 1 else "baseline")
        ):
            raise ValueError("released assignment differs from committed prefix")
