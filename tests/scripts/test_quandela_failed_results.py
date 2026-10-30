"""Failed static jobs retain service diagnostics without inventing counts."""

import base64
import json
import zlib

import pytest
from qd_platform import PlatformError, parse_counts, result_summary


def test_zipped_counts_require_exactly_one_complete_stream() -> None:
    payload = zlib.compress(b":PCVL:BSCount:{|1,0>=7}")

    def encoded(data: bytes) -> str:
        return ":PCVL:zip:" + base64.b64encode(data).decode("ascii")

    if parse_counts(encoded(payload)) != {"1,0": 7}:
        raise AssertionError("the complete compressed histogram must decode")
    for malformed in (payload[:-1], payload[:-5], payload + b"trailing", payload + zlib.compress(b"other")):
        with pytest.raises(PlatformError, match="stream"):
            parse_counts(encoded(malformed))


def test_static_instrument_error_is_retained_only_for_failed_job() -> None:
    message = "RuntimeError: hardware_info.circuit_input_ports must be defined"
    raw = json.dumps({"job_id": "static-job", "shots": 0, "results": json.dumps({"results": message})}).encode()
    summary = result_summary(raw, "static-job", {"shots": 0}, complete=False)
    if summary["counts"] != {} or summary["samples"] != 0 or summary.get("partial") is not True:
        raise RuntimeError("a failed instrument call must remain a count-less partial result")
    if summary.get("error") != message:
        raise RuntimeError("the error summary must retain the provider diagnostic")
    with pytest.raises(PlatformError, match="BSCount"):
        result_summary(raw, "static-job", {"shots": 0}, complete=True)


def test_static_partial_counts_still_validate_the_count_encoding() -> None:
    raw = json.dumps(
        {"job_id": "static-job", "shots": 2, "results": json.dumps({"results": ":PCVL:BSCount:{|1,0>=2}"})}
    ).encode()
    summary = result_summary(raw, "static-job", {"shots": 2}, complete=False)
    if summary["samples"] != 2 or summary["counts"] != {"1,0": 2}:
        raise RuntimeError("a failed job's valid partial counts must survive")
    changed = raw.replace(b"BSCount", b"unknown")
    with pytest.raises(PlatformError):
        result_summary(changed, "static-job", {"shots": 2}, complete=False)
