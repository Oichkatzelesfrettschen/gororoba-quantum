"""IQM native-SDK tools: the pure parts of the compile comparison, the offline inversion and the transport capture."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import iqm_native_compile as nc  # noqa: E402
import iqm_rem_offline as rem  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_measure_of_two_qubits_counts_two_and_splits_into_keys() -> None:
    instructions = [
        {"name": "prx", "locus": ["QB1"], "args": {"angle": 1.0, "phase": 0.0}},
        {"name": "measure", "locus": ["QB2", "QB1"], "args": {"key": "m"}},
    ]
    require(nc.native_counts(instructions) == {"measure": 2, "prx": 1}, "one measure of two qubits counts two")
    split = nc.expand_measures(instructions)
    keys = [i["args"]["key"] for i in split if i["name"] == "measure"]
    require(keys == ["m_2_0_0", "m_2_0_1"], "the measured qubits take bits 0 and 1 of one register in locus order")
    require([i["locus"] for i in split if i["name"] == "measure"] == [["QB2"], ["QB1"]], "one qubit per measure")


def test_inversion_undoes_the_readout_channel() -> None:
    e01, e10 = 0.02, 0.05
    p0 = 0.3
    observed = (1 - e01) * p0 + e10 * (1 - p0)
    require(
        abs(rem.invert_zero_fraction(observed, e01, e10) - p0) < 1e-12, "the inversion returns the true zero fraction"
    )
    with pytest.raises(ValueError, match="no contrast"):
        rem.invert_zero_fraction(0.5, 0.5, 0.5)


def test_difference_of_arms_scales_by_the_contrast_and_a_ratio_does_not_move() -> None:
    e01, e10 = 0.001, 0.02
    plus, minus = 0.9, 0.2
    d_raw = plus - minus
    d_inv = rem.invert_zero_fraction(plus, e01, e10) - rem.invert_zero_fraction(minus, e01, e10)
    require(abs(d_inv * (1 - e01 - e10) - d_raw) < 1e-12, "an arm difference scales by 1 / (1 - e01 - e10)")


def test_readout_rates_prefer_the_heralded_variant() -> None:
    base = "metrics.ssro.measure.constant.QB1"
    metrics = {
        "observations": [
            {"dut_field": f"{base}.error_0_to_1", "value": 0.1},
            {"dut_field": f"{base}.error_1_to_0", "value": 0.2},
            {"dut_field": f"{base}.error_0_to_1:herald=measure.constant", "value": 0.01},
            {"dut_field": f"{base}.error_1_to_0:herald=measure.constant", "value": 0.02},
        ]
    }
    require(rem.readout_rates(metrics, "QB1") == (0.01, 0.02), "the heralded rates win")


def test_transport_capture_self_test() -> None:
    pytest.importorskip("iqm.iqm_client")
    import iqm_transport_capture as tc

    require(tc.self_test() == 0, "the capture self-test passes")
