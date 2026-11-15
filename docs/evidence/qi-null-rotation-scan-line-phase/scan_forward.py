"""The null rotation scan's circuit bound to the elementary-error model of gororoba_quantum/elementary_error_laws.py.

`laws(arm, items)` takes the retained b0 instruction list, the arm's injected pulse angles and the logical bit
order of scripts/qi_pathion_null_rotation_scan_cases.py and returns the arm's laws under the (candidate, values)
pairs of `items`. It equals `forward_laws` of the scan module where both apply."""

# ruff: noqa: E402  (repository modules are imported after the path insertions that locate them)
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
for extra in (ROOT / "scripts", ROOT / "gororoba_quantum"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))
import qi_pathion_null_rotation_scan_cases as rs

import elementary_error_laws

HERE = Path(__file__).resolve().parent
cc = rs.cc
ref = rs.retained()
region = ref["region"]
pairs = sorted({tuple(sorted(q)) for g, a, q in ref["ops"] if g == "CZ"})
OUTCOME_QUBITS = [ref["roles"][k] for k in reversed(rs.KEYS)]


def laws(arm: str, items: list[tuple[tuple[str, Any, Any], np.ndarray]]) -> np.ndarray:
    pulse, scope, steps = rs.ARMS[arm]
    injected = () if scope is None or pulse != "Rx" else rs.SCOPES[scope]
    angles = {q: math.pi / 2 + steps * rs.STEP for q in injected}
    return elementary_error_laws.error_laws(ref["ops"], region, OUTCOME_QUBITS, angles, items)
