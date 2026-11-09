"""Contracts of the Walsh-spectral N_hat reading (docs/evidence/pathion-kernel-map/nhat-bias/nhat_spectral.py).

N_hat equals N lambda_0 / lambda_bar on the Walsh spectrum, a symmetric flip channel leaves one-character blocks at 0
and all-aligned blocks at 4, and every nullity-12 two-term operand has its misaligned pairs on a linear 2-plane, so
the profile over all 35 admissible tilings is one signature for V, VB, V^a+ and V^a-. The retained
result_spectral.json, which holds the 252-operand census, is an on-demand gate (ci/gates.json, nhat-spectral entry).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "docs/evidence/pathion-kernel-map/nhat-bias"
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location("nhat_spectral", DIRECTORY / "nhat_spectral.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("nhat_spectral.py is not importable")
nhat_spectral = importlib.util.module_from_spec(SPEC)
sys.modules["nhat_spectral"] = nhat_spectral
SPEC.loader.exec_module(nhat_spectral)


def test_self_test_passes() -> None:
    lines = nhat_spectral.self_test()
    if len(lines) < 6:
        raise AssertionError(lines)


def test_block_prediction() -> None:
    value = nhat_spectral.block_spectrum_prediction(3, 0.02)
    if abs(value - 3.0909) > 1e-3:
        raise AssertionError(value)
