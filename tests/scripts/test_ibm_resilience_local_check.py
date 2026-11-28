"""ibm_resilience_local_check: the extrapolation recovers a planted law and folding scales the gate count."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

pytest.importorskip("qiskit_ibm_runtime")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import ibm_dd_compare as dd  # noqa: E402
import ibm_resilience_local_check as rc  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_extrapolation_recovers_a_planted_exponential() -> None:
    values = [-math.exp(-0.2 * lam) for lam in rc.NOISE_FACTORS]
    out = rc.extrapolate(rc.NOISE_FACTORS, values)
    require(abs(out["exponential"] + 1.0) < 1e-9, "the exponential fit returns the planted zero-noise value")
    require(out["linear"] > -1.0, "the linear fit undershoots a convex decay")


def test_folding_triples_the_body_and_keeps_the_measurement() -> None:
    _, target, _ = dd.load_target("fake:fez")
    case = dd.idle_fixture()
    isa = dd.compile_cases([case], target, None, [0, 1])[0]
    once = rc.fold(isa, target, 1)
    thrice = rc.fold(isa, target, 3)
    gates = lambda c: sum(v for k, v in c.count_ops().items() if k not in {"barrier", "measure", "delay"})  # noqa: E731
    require(gates(thrice) >= 3 * gates(once) - 2, "factor 3 plays the body three times")
    require(thrice.count_ops().get("measure") == 1, "the measurement stays single and last")


def test_even_factor_is_refused() -> None:
    _, target, _ = dd.load_target("fake:fez")
    isa = dd.compile_cases([dd.idle_fixture()], target, None, [0, 1])[0]
    with pytest.raises(ValueError, match="odd"):
        rc.fold(isa, target, 2)


def test_an_unfolded_affine_readout_biases_the_exponential_fit() -> None:
    gate_only = [-math.exp(-0.2 * lam) for lam in rc.NOISE_FACTORS]
    through_readout = [0.9 * z + 0.03 for z in gate_only]
    require(abs(rc.extrapolate(rc.NOISE_FACTORS, gate_only)["exponential"] + 1.0) < 1e-9, "gate attenuation alone fits")
    biased = rc.extrapolate(rc.NOISE_FACTORS, through_readout)["exponential"]
    require(abs(biased + 1.0) > 0.05, "a fixed readout channel moves the zero-noise value off the ideal")


def test_report_separates_folding_fits_and_scheduled_duration() -> None:
    name, target, props = dd.load_target("fake:fez")
    report = rc.run_check(name, target, props, shots=200, seed_transpiler=None, seed_simulator=None)
    require("qpu_cost_ratio" not in report, "the duration ratio carries its own name")
    require(report["repetition_delay_included"] is False, "the ratio omits the repetition delay")
    require("not folded" in report["folding"], "the report states that the readout stays unfolded")
    require("exponential" in report["fit_assumptions"], "the report states the fit assumptions")
    require(report["scheduled_duration_ratio"] > 3.0, "the ratio sums the three scheduled circuits")
