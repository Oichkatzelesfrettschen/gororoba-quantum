import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_stray_mode_veto as veto  # noqa: E402


def pattern(*modes: int) -> str:
    return ",".join("1" if m in modes else "0" for m in range(24))


def test_detector_absent_drops_the_stray_detector_before_the_one_click_rule() -> None:
    counts = {
        pattern(veto.STRAY): 7,  # a lone stray click leaves the eligible set
        pattern(0, veto.STRAY): 3,  # a stray click beside mode 0 becomes a mode-0 one-click sample
        pattern(12): 5,
        pattern(0, 12): 11,  # a genuine two-click pattern stays excluded
        pattern(3): 2,  # off support, unselected
        pattern(): 13,
    }
    tally = veto.detector_absent(counts, selected={0}, support=[0, 12])
    expected = {"selected": 3, "eligible": 10, "selected_on_support": 3, "on_support": 8}
    if tally != expected:
        raise AssertionError(tally)


def test_retained_readout_vetoes_agree_and_remove_most_block_heterogeneity() -> None:
    import json

    read = json.loads(veto.OUT.read_text())
    stats = [read["vetoed"][name]["block_change"]["statistic"] for name in ("subtract", "detector_absent")]
    if not (read["raw"]["block_change"]["statistic"] > 5 * max(stats) and abs(stats[0] - stats[1]) < 1.0):
        raise AssertionError(stats)
