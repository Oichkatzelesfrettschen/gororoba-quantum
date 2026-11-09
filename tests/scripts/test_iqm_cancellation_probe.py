"""The kernel cancellation probe reads the zero-divisor sign, and its train fit recovers an over-rotation."""

import json
import math
import platform
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/iqm/runs/2026-10-23T073147Z-garnet-kernel-cancellation-probe-cancellation"
ANALYSIS = ROOT / "results/iqm/kernel_cancellation_probe_analysis-runner-image.json"
# The retained analysis holds the x64 numeric identity of the runner image that wrote it, so an x64 replay matches it
# byte for byte. Another identity rounds the fitted floats differently (2 fields moved by at most 4.7e-15 relative on
# macOS arm64), and its replay keeps every non-float value exact and each float within REPLAY_REL_TOL
# (docs/design/native-numeric-replay.md, contract item 4).
X64 = platform.machine() in {"x86_64", "AMD64"}
REPLAY_REL_TOL = 1e-12


def test_kernel_law_and_sign_mutations() -> None:
    import kernel_cancellation as kc

    kc.check()
    circuit = kc.cancellation_probe()
    for phi in (0.1, 0.3):
        if abs(kc.control_z(circuit, phi) + math.sin(2 * phi)) > 1e-12:
            raise AssertionError(f"the kernel reads {kc.control_z(circuit, phi)} at phi = {phi}")
        if abs(kc.control_z(circuit, phi, bright=True) - 1.0) > 1e-12:
            raise AssertionError(f"the bright vector departs from 1 at phi = {phi}")


def trains(eps: float, e01: float, e10: float, merged: bool = False) -> tuple:
    import iqm_cancellation_probe as probe

    # A train of index k holds 4k + 1 pi/2 pulses (train()), the counts evaluate() fits.
    lengths = [4 * k + 1 for k in probe.AMPLIFY_K]
    factor, offset = 1 - e01 - e10, e10 - e01
    n_read = [lengths[-1]] * len(lengths) if merged else lengths
    rows = [(factor * -math.sin(n * math.pi / 2 * eps) + offset, 1e-3, 4000) for n in n_read]
    ro0 = (1 - 2 * e01, 1e-3, 4000)
    ro1 = (factor * -math.cos(math.pi * eps) + offset, 1e-3, 4000)
    return lengths, rows, ro0, ro1


@pytest.mark.parametrize("eps", [-0.03, -0.003, 0.0, 0.015, 0.027])
def test_train_fit_recovers_the_injected_over_rotation(eps: float) -> None:
    import iqm_cancellation_probe as probe

    got, se, chi2, e01, e10 = probe.fit_train(*trains(eps, 0.02, 0.05))
    if abs(got - eps) > 1e-6 or abs(e01 - 0.02) > 1e-6 or abs(e10 - 0.05) > 1e-6:
        raise AssertionError(f"injected eps {eps}, (0.02, 0.05); fitted {got}, ({e01}, {e10})")
    if not (chi2 < 1e-6 and 0 < se < 1e-2):
        raise AssertionError(f"exact trains fit with chi2 {chi2}, se {se}")


def test_merged_trains_exceed_the_linearity_cutoff() -> None:
    import iqm_cancellation_probe as probe

    _, _, chi2, _, _ = probe.fit_train(*trains(0.027, 0.02, 0.05, merged=True))
    if not chi2 > probe.H5_CHI2_CUTOFF:
        raise AssertionError(f"trains that ignore their pulse count fit with chi2 {chi2}")


def test_retained_garnet_analysis_replays() -> None:
    import iqm_cancellation_probe as probe

    replayed = json.dumps(probe.analyze([RUN]), indent=1, sort_keys=True) + "\n"
    retained = ANALYSIS.read_text(encoding="utf-8")
    if X64:
        if replayed != retained:
            raise AssertionError(f"{ANALYSIS} differs from the replayed analysis")
    else:
        departures = _departures(json.loads(replayed), json.loads(retained), "")
        if departures:
            raise AssertionError(f"{ANALYSIS} departs from the replayed analysis at {departures[:5]}")
    verdict = json.loads(replayed)
    if verdict["h1_zero_divisor_sign"] != {"0.1": "resolved", "0.3": "resolved"}:
        raise AssertionError(f"the retained run reads H1 {verdict['h1_zero_divisor_sign']}")


def _departures(fresh: Any, kept: Any, path: str) -> list[str]:
    """JSON paths where a replay departs from the retained analysis beyond the cross-identity bound."""
    if isinstance(fresh, dict) and isinstance(kept, dict):
        if fresh.keys() != kept.keys():
            return [f"{path}: keys {sorted(fresh.keys() ^ kept.keys())}"]
        return [d for key in fresh for d in _departures(fresh[key], kept[key], f"{path}.{key}")]
    if isinstance(fresh, list) and isinstance(kept, list):
        if len(fresh) != len(kept):
            return [f"{path}: length {len(fresh)} against {len(kept)}"]
        return [d for i, (a, b) in enumerate(zip(fresh, kept, strict=True)) for d in _departures(a, b, f"{path}[{i}]")]
    if isinstance(fresh, float) and isinstance(kept, float):
        return (
            []
            if math.isclose(fresh, kept, rel_tol=REPLAY_REL_TOL, abs_tol=0.0)
            else [f"{path}: {fresh} against {kept}"]
        )
    return [] if fresh == kept and type(fresh) is type(kept) else [f"{path}: {fresh!r} against {kept!r}"]
