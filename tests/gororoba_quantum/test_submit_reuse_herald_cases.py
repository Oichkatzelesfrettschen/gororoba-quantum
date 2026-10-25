"""The heralded reuse contract's gate cases run every phase of the whole sequence exactly once."""

from collections import Counter

import qpu_planning_contracts as contracts


def test_herald_cases_partition_the_reuse_phases() -> None:
    selected = Counter(phase for phases in contracts.SUBMIT_REUSE_HERALD_CASES.values() for phase in phases)
    if set(selected) != set(contracts.SUBMIT_REUSE_PHASES) or set(selected.values()) != {1}:
        raise AssertionError(f"the herald cases select {dict(selected)}, not each reuse phase once")
