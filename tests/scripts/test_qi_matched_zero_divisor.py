"""Matched response proposals retain routing and cancel batch offsets."""

import json

import numpy as np
import pytest


@pytest.mark.parametrize(
    "mutation",
    [
        "CZ q[0], q[2]\nCZ q[1], q[4]\nb = measure q\n",
        "b = measure q\nCZ q[0], q[1]\nCZ q[2], q[4]\n",
        "CZ q[0], q[1]\nCZ q[2], q[4]\nRz(1.0) q[0]\nb = measure q\n",
    ],
)
def test_compiler_rejects_partner_order_and_angle_mutations(mutation: str) -> None:
    from qi_matched_zero_divisor import _compiler_angle_error

    source = "CZ q[0], q[1]\nCZ q[2], q[4]\nb = measure q\n"
    with pytest.raises(ValueError):
        _compiler_angle_error(source, mutation)


def test_compiler_accepts_only_bounded_angle_rounding() -> None:
    from qi_matched_zero_divisor import _compiler_angle_error

    source = "Rz(1.570796326794897) q[0]\nb = measure q\n"
    error = _compiler_angle_error(source, source.replace("1.570796326794897", "1.5707963"))
    if not 0 < error < 5e-8:
        raise AssertionError("the compiler must report its bounded serialization difference")
    with pytest.raises(ValueError):
        _compiler_angle_error(source, source.replace("1.570796326794897", "1.5707"))


@pytest.mark.parametrize(
    "probabilities,covariance",
    [
        ([0.0] * 5, np.eye(6).tolist()),
        ([float("nan")] * 6, np.eye(6).tolist()),
        ([0.0] * 6, (-np.eye(6)).tolist()),
        ([0.0] * 6, np.zeros((6, 6)).tolist()),
        ([0.0] * 6, (np.eye(6) + np.triu(np.ones((6, 6)), 1)).tolist()),
    ],
)
def test_matched_response_rejects_invalid_inputs(probabilities: list[float], covariance: list[list[float]]) -> None:
    from qi_matched_zero_divisor import matched_response_contrast

    with pytest.raises(ValueError):
        matched_response_contrast(probabilities, covariance)


def test_matched_response_cancels_batch_and_region_offsets() -> None:
    from qi_matched_zero_divisor import matched_response_contrast

    probabilities = [0.2, 0.65, 0.72, 0.57, 0.41, 0.26]
    covariance = np.eye(6) * 0.001
    result = matched_response_contrast(probabilities, covariance.tolist())
    if abs(result["residual"]) > 1e-12:
        raise AssertionError("the primary contrast must cancel batch and fixed region offsets")
    probabilities[3] += 0.1
    if matched_response_contrast(probabilities, covariance.tolist())["z"] < 1:
        raise AssertionError("a fixture shift must survive the drift-cancelling contrast")


def test_proposal_contains_nine_matched_unsubmitted_jobs() -> None:
    from qi_matched_zero_divisor import build

    files = build()
    proposal = json.loads(files["proposal.json"])
    if proposal["jobs"] != 9 or proposal["total_shots"] != 147456 or proposal["provider_execution_authorized"]:
        raise AssertionError("the written proposal must carry the bounded unsubmitted nine-job budget")
    for batch in range(3):
        manifest = json.loads(files[f"batch-{batch:02d}/cases.json"])
        if len(manifest["circuits"]) != 3 or manifest["shots"] != 16384:
            raise AssertionError("every calibration batch must contain one witness and two readout controls")
    for region in proposal["regions"]:
        if region["ideal_probabilities"] != {"dark": 0.0, "bright": 1.0, "fixture": 0.5}:
            raise AssertionError("the fixed routing must preserve all three exact ideal endpoints")
        if region["case_shapes_equal"] is not True:
            raise AssertionError("every case must retain the same routed operation and timing shape")
