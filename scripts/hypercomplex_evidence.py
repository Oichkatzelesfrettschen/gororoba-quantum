"""Retain and replay finite algebra, local evolution and probability-art evidence.

The generated animation labels simulator predictions. Measured records enter
through --render only after their provenance and probability fields validate.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from hypercomplex_operators import algebra_certificate, grouped_probabilities, periodic_generator  # noqa: E402
from parallel import ordered_map  # noqa: E402


def _frame(index: int) -> dict[str, Any]:
    time = index / 8
    operator = expm(time * periodic_generator(4, 1))
    return {
        "time": time,
        "probabilities": grouped_probabilities(operator[:, 0]).tolist(),
        "representative_residual": float(
            np.max(np.abs(grouped_probabilities(operator[:, 0]) - grouped_probabilities(operator[:, 1])))
        ),
    }


def certificate() -> dict[str, Any]:
    from fractions import Fraction
    from itertools import product

    sectors: dict[str, int] = {}
    anomalies = {
        "gravitational_U1": Fraction(0),
        "U1_cubed": Fraction(0),
        "SU3_squared_U1": Fraction(0),
        "SU2_squared_U1": Fraction(0),
    }
    for bits in product((0, 1), repeat=5):
        color, weak = sum(bits[:3]), sum(bits[3:])
        if (color + weak) % 2 == 0:
            hypercharge = -Fraction(color, 3) + Fraction(weak, 2)
            key = f"Nc={color};Nw={weak};Y={hypercharge}"
            sectors[key] = sectors.get(key, 0) + 1
            anomalies["gravitational_U1"] += hypercharge
            anomalies["U1_cubed"] += hypercharge**3
    # Dynkin indices of the left-handed Q, u^c, d^c and L sectors.
    anomalies["SU3_squared_U1"] = Fraction(1, 2) * (2 * Fraction(1, 6) - Fraction(2, 3) + Fraction(1, 3))
    anomalies["SU2_squared_U1"] = Fraction(1, 2) * (3 * Fraction(1, 6) - Fraction(1, 2))
    source_names = [
        "gororoba_quantum/cd_core.py",
        "gororoba_quantum/hypercomplex_operators.py",
        "gororoba_quantum/hypercomplex_dynamics.py",
        "scripts/hypercomplex_evidence.py",
    ]
    return {
        "schema": "hypercomplex-operator-evidence-v1",
        "evidence_kind": "local-simulation",
        "provenance": "exact finite algebra and NumPy/SciPy matrix propagation; provider jobs excluded",
        "sources_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_names},
        "algebra": algebra_certificate(),
        "spinor_reference": sectors,
        "spinor_anomaly_sums": {name: str(value) for name, value in anomalies.items()},
        "frames": ordered_map(_frame, list(range(17))),
        "phase_measured": False,
    }


def validate(record: dict[str, Any]) -> None:
    if record.get("phase_measured", False) is not False:
        raise ValueError("probability frames do not establish measured phase")
    if record.get("evidence_kind") not in {"local-simulation", "hardware-measurement"}:
        raise ValueError("an explicit simulation or hardware evidence kind is required")
    if not isinstance(record.get("provenance"), str) or not record["provenance"]:
        raise ValueError("evidence provenance is required")
    frames = record.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("at least one probability frame is required")
    width = len(frames[0]["probabilities"])
    previous = -float("inf")
    for frame in frames:
        values = np.asarray(frame["probabilities"], dtype=float)
        time = frame["time"]
        if values.shape != (width,) or width < 1 or not np.isfinite(values).all() or np.any(values < 0):
            raise ValueError("probability frames need matching finite nonnegative distributions")
        if not np.isclose(values.sum(), 1, atol=1e-12, rtol=0) or not np.isfinite(time) or time < previous:
            raise ValueError("frames need normalized probabilities and ordered finite times")
        previous = time
        if record["evidence_kind"] == "hardware-measurement":
            counts = frame.get("counts")
            if (
                not isinstance(counts, list)
                or len(counts) != width
                or any(type(count) is not int or count < 0 for count in counts)
            ):
                raise ValueError("hardware frames require nonnegative integer counts for each displayed bin")
            shots = sum(counts)
            if shots < 1 or not np.allclose(values, np.asarray(counts) / shots, atol=1e-12, rtol=0):
                raise ValueError("hardware probabilities must equal their retained counts")
            if not re.fullmatch(r"[0-9a-f]{64}", str(frame.get("raw_sha256", ""))) or not frame.get("job_id"):
                raise ValueError("hardware frames require raw digest and job identity")


def replay_matches(retained: dict[str, Any], fresh: dict[str, Any]) -> bool:
    """Compare exact claims exactly and floating propagation within its tolerance."""
    left, right = dict(retained), dict(fresh)
    left_frames, right_frames = left.pop("frames", []), right.pop("frames", [])
    if left != right or len(left_frames) != len(right_frames):
        return False
    for old, new in zip(left_frames, right_frames, strict=True):
        if old.keys() != new.keys() or old["time"] != new["time"]:
            return False
        if np.shape(old["probabilities"]) != np.shape(new["probabilities"]) or not np.allclose(
            old["probabilities"], new["probabilities"], atol=1e-12, rtol=0
        ):
            return False
        if (
            not math.isfinite(old["representative_residual"])
            or abs(old["representative_residual"] - new["representative_residual"]) > 1e-12
        ):
            return False
    return True


def render(record: dict[str, Any]) -> str:
    validate(record)
    payload = json.dumps(record).replace("<", "\\u003c")
    label = html.escape(record["evidence_kind"])
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8"><title>Quaternion probability evolution</title>
<style>body{background:#101725;color:#e7edf7;font:17px system-ui;max-width:950px;margin:2em auto}
canvas{width:100%;background:#142033}input{width:100%}small{display:block;line-height:1.5}</style>
<h1>Quaternion probability evolution</h1><p>Evidence: """
        + label
        + """</p>
<canvas id="plot" width="950" height="420"></canvas><input id="frame" type="range" min="0" value="0">
<p id="caption"></p><small>Adjacent encoding channels are summed into quaternion-site probabilities.
Color and height encode probability. The rendering claims no measured phase or chaos.
Hardware bars show nominal IID Wilson 95% sensitivity intervals.
Temporal independence and interval coverage remain unestablished; these bars do not establish measured coverage.</small>
<script>const data="""
        + payload
        + """;
const slider=document.getElementById('frame'), canvas=document.getElementById('plot'),ctx=canvas.getContext('2d');
slider.max=data.frames.length-1;
function draw(){const f=data.frames[Number(slider.value)],n=f.probabilities.length;ctx.clearRect(0,0,950,420);
f.probabilities.forEach((p,k)=>{const x=30+k*890/n,w=850/n,h=p*350;ctx.fillStyle=`hsl(${190+90*p} 75% ${30+35*p}%)`;
ctx.fillRect(x,380-h,w,h);ctx.fillStyle='#e7edf7';ctx.fillText(`site ${k}: ${p.toFixed(4)}`,x,400);
if(f.counts){const N=f.counts.reduce((a,b)=>a+b,0),z=1.96,d=1+z*z/N,c=(p+z*z/(2*N))/d;
const r=z*Math.sqrt(p*(1-p)/N+z*z/(4*N*N))/d;ctx.strokeStyle='#fff';ctx.beginPath();
ctx.moveTo(x+w/2,380-350*(c-r));ctx.lineTo(x+w/2,380-350*(c+r));ctx.stroke();}});
document.getElementById('caption').textContent=`t=${f.time}; ${data.provenance}`;}
slider.addEventListener('input',draw);draw();</script></html>"""
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--render", type=Path)
    arguments = parser.parse_args()
    if arguments.check:
        retained = json.loads(arguments.check.read_text())
        fresh = certificate()
        if not replay_matches(retained, fresh):
            raise SystemExit("hypercomplex evidence differs from its source-bound replay")
        validate(retained)
        print("hypercomplex exact algebra and local wave evidence replayed")
        return 0
    if arguments.out is None:
        parser.error("--out is required when retaining or rendering evidence")
    record = json.loads(arguments.render.read_text()) if arguments.render else certificate()
    validate(record)
    arguments.out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(record, indent=1) + "\n"
    path = arguments.out / "certificate.json"
    if path.exists() and path.read_text() != text:
        raise SystemExit("retained certificate differs; use a new evidence directory")
    path.write_text(text)
    (arguments.out / "probability-evolution.html").write_text(render(record))
    print("retained source-bound certificate and explicitly labeled probability explorer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
