"""Contracts of the N_hat bias audit (docs/evidence/pathion-kernel-map/nhat-bias/nhat_bias.py).

The estimator obeys N_hat - N = |B+||B-|/|B| (Vbar+ - Vbar-)/V_hat on every contrast vector whose bins are all
decided, a block whose pairs are all aligned reads |B+|/2 whatever the data, and the retained result.json records the
identity residual, the forced-block deviation and the headline readings of the audit.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "docs/evidence/pathion-kernel-map/nhat-bias"
SPEC = importlib.util.spec_from_file_location("nhat_bias", DIRECTORY / "nhat_bias.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("nhat_bias.py is not importable")
nhat_bias = importlib.util.module_from_spec(SPEC)
sys.modules["nhat_bias"] = nhat_bias
SPEC.loader.exec_module(nhat_bias)

CLASSES = ((4, 4), (6, 2), (2, 6), (7, 1), (16, 16), (20, 12), (28, 4))


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize(("n_plus", "n_minus"), CLASSES)
@pytest.mark.parametrize("phase", [0.0, 1.1, 2.6])
def test_identity_holds_exactly_and_in_floating_point(n_plus: int, n_minus: int, phase: float) -> None:
    c_obs, sign = nhat_bias.synthetic(n_plus, n_minus, phase)
    _expect(nhat_bias.exact_residual(c_obs, sign) == Fraction(0), "exact residual is not zero")
    est = nhat_bias.estimate(c_obs, sign)
    _expect(abs(est.n_hat - est.n_ideal - est.closed_form_bias()) < 1e-12, "floating-point residual above 1e-12")


@pytest.mark.parametrize("edit", ["swapped arms", "plus shifted by 3", "geometric both", "alternating minus"])
def test_all_aligned_block_reads_four_under_any_edit(edit: str) -> None:
    import pathion_coset_block as pcb

    block = pcb.Block("forced", (1, 18, 1), pcb.default_basis((1, 18, 1)), 4)
    plus, minus = pcb.block_law(pcb.block_circuit(block, True)), pcb.block_law(pcb.block_circuit(block, False))
    sign = np.sign(pcb.output_contrast(plus, minus))
    _expect(bool(np.all(sign == 1.0)), "the block is not all aligned")
    edited_plus, edited_minus = nhat_bias.perturbations(plus, minus)[edit]
    c_obs = pcb.output_contrast(edited_plus, edited_minus)
    if abs(float(np.mean(c_obs * sign))) > nhat_bias.ZERO:
        _expect(abs(nhat_bias.estimate(c_obs, sign).n_hat - 4.0) < 1e-12, f"forced block moved under {edit}")


def test_equalized_classes_carry_no_bias() -> None:
    c_obs, sign = nhat_bias.synthetic(20, 12, 0.3)
    _expect(abs(nhat_bias.estimate(c_obs, sign).n_hat - 8.0) > 1e-3, "the unmutated control carries no bias")
    est = nhat_bias.estimate(nhat_bias.equalize(c_obs, sign), sign)
    _expect(abs(est.n_hat - est.n_ideal) < 1e-12, "equalizing the class means leaves a bias")


def test_undecided_bin_is_refused() -> None:
    with pytest.raises(ValueError, match="ideal contrast"):
        nhat_bias.estimate(np.array([0.5, 0.5, 0.5]), np.array([1.0, 0.0, -1.0]))


def test_self_test_passes() -> None:
    _expect(nhat_bias.self_test() == [], "self-test reports a failure")


def test_retained_result_records_the_audit() -> None:
    record = json.loads((DIRECTORY / "result.json").read_text())
    _expect(record["schema"] == nhat_bias.SCHEMA, "schema differs")
    _expect(record["identity"]["exact_residual_all_zero"] is True, "the exact identity residual is not zero")
    _expect(record["identity"]["float_residual_max"] < 1e-12, "the floating-point residual is above 1e-12")
    _expect(record["forced_blocks"]["max_deviation_from_forced_value"] == 0.0, "a forced block moved")
    readings = {row["key"]: row for row in record["kernel_map"]["readings"]}
    null, deep = readings["kmap_e1pe17"], readings["kmap_e1pe26"]
    _expect(math.isclose(null["n_hat"], 1.399345447032, abs_tol=1e-9), "null operand reading differs")
    _expect(math.isclose(deep["n_hat"], 10.035692168497, abs_tol=1e-9), "nullity-4 operand reading differs")
    _expect(math.isclose(deep["bias"], deep["bias_closed_form"], abs_tol=1e-9), "closed form differs from the bias")
