"""Contracts of the repeat decisions on synthetic reports: admission, replication, visibility and pair pattern."""

from __future__ import annotations

import copy
from typing import Any

import idle_penalty_repeat_decisions as rd
import pytest

PAIRS = [(10, 11), (21, 20), (40, 41), (50, 51)]
SHIFTS = [-1.0, -3.0, -0.5, -6.0]


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _contrast(mean: float, t: float, verdict: str) -> dict[str, Any]:
    return {"n": len(PAIRS), "mean": mean, "t": t, "verdict": verdict}


def _report(t1: float = 200.0, t2: float = 150.0, shift_scale: float = 1.0, vis_t: float = -2.3) -> dict[str, Any]:
    qubits = {}
    for target, spectator in PAIRS:
        for qubit in (target, spectator):
            qubits[str(qubit)] = {"t1_reported_us": t1 + qubit, "t2_reported_us": t2 + qubit}
    return {
        "identity": {"run": "results/live/RUN"},
        "qubits": qubits,
        "pairs": [
            {"target": t, "spectator": s, "shift_khz": shift_scale * v} for (t, s), v in zip(PAIRS, SHIFTS, strict=True)
        ],
        "pooled": {
            "optimistic_t1": "absent or unresolved",
            "echo_gain": "present",
            "readout_shift": {
                "decision": "present",
                "vs_after": _contrast(-2.7, -5.1, "present"),
                "vs_quiet": _contrast(-2.7, -5.1, "present"),
                "null": _contrast(0.0, 0.1, "absent"),
            },
            "readout_dephasing": {
                "decision": "present",
                "vs_after": _contrast(-0.03, vis_t, "present"),
                "vs_quiet": _contrast(-0.02, vis_t, "present"),
                "null": _contrast(0.007, 2.2, "absent"),
            },
        },
    }


def test_admission_needs_t1_and_t2_refreshed() -> None:
    first = _report()
    _expect(rd.admission(first, _report(t1=210.0, t2=160.0))["admitted"], "a full refresh was refused")
    _expect(not rd.admission(first, _report(t1=210.0))["admitted"], "a T1-only refresh was admitted")
    _expect(not rd.admission(first, _report(t2=160.0))["admitted"], "a T2-only refresh was admitted")
    _expect(not rd.admission(first, copy.deepcopy(first))["admitted"], "carried-forward values were admitted")


def test_replication_reads_verdicts_and_shift_sign() -> None:
    first = _report()
    out = rd.replication(first, _report())
    _expect(out["readout_shift"]["replicated"] and out["echo_gain"]["replicated"], "identical verdicts differ")
    flipped = _report()
    for key in ("vs_after", "vs_quiet"):
        flipped["pooled"]["readout_shift"][key]["mean"] = 2.7
    _expect(not rd.replication(first, flipped)["readout_shift"]["replicated"], "a sign flip replicated")


@pytest.mark.parametrize(
    ("vis_t", "null", "expected"),
    [
        (-2.3, "absent", "pairwise heterogeneity"),
        (-12.0, "absent", "mean loss present"),
        (-12.0, "present", "pairwise heterogeneity"),
    ],
)
def test_mean_visibility_loss_needs_both_t_statistics(vis_t: float, null: str, expected: str) -> None:
    pooled = _report(vis_t=vis_t)["pooled"]
    pooled["readout_dephasing"]["null"]["verdict"] = null
    reading = rd.mean_visibility_loss(pooled)
    _expect(reading == expected, f"t {vis_t}, null {null}: {reading}")


def test_pair_pattern_correlation() -> None:
    first = _report()
    scaled = rd.pair_pattern(first, _report(shift_scale=0.5))["verdict"]
    _expect(scaled == "pair pattern stable", f"a scaled pattern reads {scaled}")
    shuffled = _report()
    for pair, value in zip(shuffled["pairs"], [-6.0, -0.5, -3.0, -1.0], strict=True):
        pair["shift_khz"] = value
    reordered = rd.pair_pattern(first, shuffled)["verdict"]
    _expect(reordered == "effect stable, pattern not", f"a reordered pattern reads {reordered}")
