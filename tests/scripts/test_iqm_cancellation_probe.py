"""The kernel cancellation probe reads the zero-divisor sign, and its train fit recovers an over-rotation."""

import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/iqm/runs/2026-10-23T073147Z-garnet-kernel-cancellation-probe-cancellation"
ANALYSIS = ROOT / "results/iqm/kernel_cancellation_probe_analysis-runner-image.json"


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
    if replayed != ANALYSIS.read_text(encoding="utf-8"):
        raise AssertionError(f"{ANALYSIS} differs from the replayed analysis")
    verdict = json.loads(replayed)
    if verdict["h1_zero_divisor_sign"] != {"0.1": "resolved", "0.3": "resolved"}:
        raise AssertionError(f"the retained run reads H1 {verdict['h1_zero_divisor_sign']}")
