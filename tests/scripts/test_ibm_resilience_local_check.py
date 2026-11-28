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
