"""C2: the single-qubit over-rotation that reproduces each measured null selector contrast, and what IBM says about it.

Each compile's simulated response of the null block's selector contrast to an X90 over-rotation (c2_mech.json for
the ibm_fez replica circuits, c2_tuna_mech.txt for the Tuna-17 coin compile, c2_stopped.txt for the independent
stopped-series compile) is inverted piecewise-linearly through the points (-eps, s-), (0, 0), (+eps, s+) at the
measured selector contrast of its own device: the Tuna-17 values from the retained analysis and the pinned stopped-series
reference, the IBM values from c2_scale.txt. Run after c2_mech,
c2_scale, c2_stopped and c2_tuna_mech.
"""

import importlib
import json
import math
import re
from pathlib import Path

from c2_data import ROOT

cc = importlib.import_module("qi_pathion_coset_coin_cases")
HERE = Path(__file__).resolve().parent


def last_float(pattern: str, text: str) -> float:
    found = re.search(pattern, text)
    if found is None:
        raise ValueError(f"pattern {pattern!r} not found")
    return float(found.group(1))


def angle(selector: float, eps: float, minus: float, plus: float) -> float:
    """Over-rotation (rad) whose simulated selector contrast is `selector`, by piecewise-linear inversion."""
    if selector >= 0:
        return selector / plus * eps
    return selector / minus * -eps


def with_error(selector: float, se: float, eps: float, minus: float, plus: float) -> tuple[float, float]:
    centre = angle(selector, eps, minus, plus)
    spread = abs(angle(selector + se, eps, minus, plus) - angle(selector - se, eps, minus, plus)) / 2
    return centre, spread


mech = json.loads((HERE / "c2_mech.json").read_text())["rows"]
scale = (HERE / "c2_scale.txt").read_text()
tuna_mech = (HERE / "c2_tuna_mech.txt").read_text()
stopped = (HERE / "c2_stopped.txt").read_text()

ibm_plus = mech["sx over-rotation +0.03 rad"]["k0"]["sel"]
ibm_minus = mech["sx over-rotation -0.03 rad"]["k0"]["sel"]
coin_plus = last_float(r"X90 over-rotation \+0\.03\s+V \S+\s+selector contrast ([+-]\d\.\d+)", tuna_mech)
coin_minus = last_float(r"X90 over-rotation -0\.03\s+V \S+\s+selector contrast ([+-]\d\.\d+)", tuna_mech)
stop_plus = last_float(r"over-rotation \+0\.029 rad\s+V \S+\s+selector contrast ([+-]\d\.\d+)", stopped)
stop_minus = last_float(r"over-rotation -0\.029 rad\s+V \S+\s+selector contrast ([+-]\d\.\d+)", stopped)
print("response of the selector contrast (rad -> contrast), 1-CZ blocks 0 for any angle (c2_mech.json k4 to k12):")
print(f"  ibm_fez k0 compile  +0.030 {ibm_plus:+.4f}  -0.030 {ibm_minus:+.4f}")
print(f"  Tuna-17 coin compile +0.030 {coin_plus:+.4f}  -0.030 {coin_minus:+.4f}")
print(f"  Tuna-17 stopped compile +0.029 {stop_plus:+.4f}  -0.029 {stop_minus:+.4f}")

coin = json.loads((ROOT / "results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json").read_text())["templates"][
    "b0"
]
measured = {
    "Tuna-17 coin b0": (coin["selector_contrast"], coin["selector_se"], (0.03, coin_minus, coin_plus)),
    "Tuna-17 stopped b0": (*cc.STOPPED_B0_SELECTOR, (0.029, stop_minus, stop_plus)),
}
for device in ("fez", "marrakesh"):
    line = next(row for row in scale.splitlines() if row.startswith(f"{device:9s} k0 "))
    sel = last_float(r"selector contrast ([+-]\d\.\d+) \+- ", line)
    se = last_float(r"selector contrast [+-]\d\.\d+ \+- (\d\.\d+)", line)
    measured[f"ibm_{device} k0"] = (sel, se, (0.03, ibm_minus, ibm_plus))

implied: dict[str, tuple[float, float]] = {}
for name, (sel, se, (eps, minus, plus)) in measured.items():
    implied[name] = with_error(sel, se, eps, minus, plus)
    print(
        f"{name:20s} selector contrast {sel:+.4f} +- {se:.4f} -> over-rotation {implied[name][0]:+.4f} +- {implied[name][1]:.4f} rad"
    )

tuna = implied["Tuna-17 coin b0"]
for device in ("fez", "marrakesh"):
    ibm = implied[f"ibm_{device} k0"]
    fixed = (tuna[0] - ibm[0]) / ibm[1]
    both = (tuna[0] - ibm[0]) / math.hypot(tuna[1], ibm[1])
    print(
        f"Tuna coin angle minus ibm_{device}: {tuna[0] - ibm[0]:+.4f} rad; {fixed:.1f} sigma of the IBM error alone, "
        f"{both:.1f} sigma of both errors"
    )
