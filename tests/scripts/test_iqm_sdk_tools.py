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


def test_propagated_estimates_keep_ratios_and_unresolved_visibility() -> None:
    # Both arms read (597, 1000, 500, 1000): D = 0.097 each, V = 0.194; the spread is binomial times PHI = 1.54.
    d, variance = 0.097, 1.54 * (0.597 * 0.403 / 1000 + 0.25 / 1000)
    se_v = (2 * variance) ** 0.5
    require(0.194 < 5.0 * se_v, "the observed counts leave the visibility unresolved")
    observed = {
        "d_real": d,
        "d_complex": d,
        "dd": 0.0,
        "se_dd": se_v,
        "visibility": 2 * d,
        "se_visibility": se_v,
        "ratio": None,
        "se_ratio": None,
        "n_c": None,
        "se_n_c": None,
    }
    e01, e10 = 0.001, 0.02
    gap = 1.0 - e01 - e10
    inverted = rem.propagate_rem(observed, e01, e10)
    require(inverted["n_c"] is None, "inversion leaves an unresolved N_c unresolved")
    require(abs(inverted["visibility"] - 2 * d / gap) < 1e-15, "a difference scales by 1 / gap")
    require(abs(inverted["se_visibility"] - se_v / gap) < 1e-15, "a standard error scales by 1 / gap")
    require(
        abs(inverted["visibility"] / inverted["se_visibility"] - 2 * d / se_v) < 1e-12,
        "the resolution z is the same before and after inversion",
    )


def test_propagated_ratio_estimates_are_unchanged() -> None:
    observed = {
        "d_real": 0.2,
        "d_complex": 0.5,
        "dd": 0.3,
        "se_dd": 0.01,
        "visibility": 0.7,
        "se_visibility": 0.01,
        "ratio": 3 / 7,
        "se_ratio": 0.02,
        "n_c": 16 * 0.5 / 0.7,
        "se_n_c": 0.16,
    }
    inverted = rem.propagate_rem(observed, 0.01, 0.03)
    for key in ("ratio", "se_ratio", "n_c", "se_n_c"):
        require(inverted[key] == observed[key], f"{key} keeps its value")
    with pytest.raises(ValueError, match="no contrast"):
        rem.propagate_rem(observed, 0.5, 0.5)


def test_native_compile_rejects_duplicate_circuit_names() -> None:
    entries = [{"file": "a.json"}, {"file": "b.json"}]
    with pytest.raises(ValueError, match="duplicate circuit name"):
        nc.row_keys(entries, ["c0", "c0"])
    require(nc.row_keys(entries, ["c0", "c1"]) == ["c0", "c1"], "distinct names pass")
