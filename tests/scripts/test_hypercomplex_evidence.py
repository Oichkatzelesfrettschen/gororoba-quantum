"""The probability renderer rejects unsupported hardware and phase claims."""

from typing import Any

import pytest
from hypercomplex_evidence import render, replay_matches, validate


def test_hardware_frames_require_counts_and_raw_identity() -> None:
    record: dict[str, Any] = {
        "evidence_kind": "hardware-measurement",
        "provenance": "test acquisition",
        "frames": [{"time": 0, "probabilities": [0.5, 0.5]}],
    }
    with pytest.raises(ValueError, match="counts"):
        validate(record)
    record["frames"][0].update({"counts": [5, 5], "raw_sha256": "a" * 64, "job_id": "test-job"})
    validate(record)
    text = render(record)
    if "hardware-measurement" not in text or "Wilson" not in text:
        raise RuntimeError("the renderer must retain the evidence and uncertainty labels")


def test_untrusted_provenance_stays_data() -> None:
    record = {
        "evidence_kind": "local-simulation",
        "provenance": "</script><script>bad()</script>",
        "frames": [{"time": 0, "probabilities": [1.0]}],
    }
    if "</script><script>bad()" in render(record):
        raise RuntimeError("provenance text must not terminate the JSON script")


def test_replay_preserves_exact_claims_and_tolerates_roundoff() -> None:
    import copy

    record: dict[str, Any] = {
        "algebra": {"dimension": 14},
        "frames": [{"time": 0, "probabilities": [1.0, 0.0], "representative_residual": 0.0}],
    }
    fresh = copy.deepcopy(record)
    fresh["frames"][0]["representative_residual"] = 1e-15
    if not replay_matches(record, fresh):
        raise RuntimeError("floating roundoff must fit the declared tolerance")
    fresh["algebra"]["dimension"] = 13
    if replay_matches(record, fresh):
        raise RuntimeError("integer algebra claims must remain exact")
