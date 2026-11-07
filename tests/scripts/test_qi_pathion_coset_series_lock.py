"""Contract of the series lock of the coset-block and coset-coin series gates.

submit_next reads the submitted batches only after it holds the exclusive lock on the series case directory: a call
that reads them first and then waits for another call to submit and release acts on a stale list, and for the first
batch a new timestamp names a new run directory, so the batch is submitted twice. The test runs the second call from
inside the first call's read of the submitted batches, which is the interleaving with the smaller window made
deterministic.
"""

from __future__ import annotations

import datetime
import types
from pathlib import Path
from typing import Any

import pytest
import qi_pathion_coset_block_series as block_series
import qi_pathion_coset_coin_series as coin_series
import qi_platform

SERIES = [
    pytest.param(block_series, block_series.QX_SERIES, id="block"),
    pytest.param(coin_series, coin_series.QX_SERIES, id="coin"),
]


class _Clock:
    """datetime.datetime whose now() advances one second per call, so two submissions never share a run directory."""

    ticks = 0

    @classmethod
    def now(cls, tz: datetime.tzinfo | None = None) -> datetime.datetime:
        cls.ticks += 1
        return datetime.datetime(2026, 11, 7, 0, 0, cls.ticks, tzinfo=tz)


@pytest.mark.parametrize(("module", "series"), SERIES)
def test_a_call_that_waited_for_another_submission_does_not_submit_the_batch_again(
    module: Any, series: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    series_dir = block_series.CASES_ROOT / series
    submitted: list[Path] = []

    def submit(run_dir: Path, backend_type_id: int, approval: str, **_: Any) -> dict[str, Any]:
        submitted.append(run_dir)
        (run_dir / "submission-state.json").write_text("{}\n", encoding="utf-8")
        return {"batch_job": "batch", "jobs": []}

    monkeypatch.setattr(qi_platform, "submit", submit)
    monkeypatch.setattr(module, "datetime", types.SimpleNamespace(datetime=_Clock, UTC=datetime.UTC))
    original = block_series.series_runs
    refusals: list[str] = []
    entered: list[bool] = []

    def interleaved(name: str, runs: Path) -> dict[str, Path]:
        snapshot = original(name, runs)
        if not entered:
            entered.append(True)
            try:
                module.submit_next(series_dir, runs, "approval")
            except SystemExit as refusal:
                refusals.append(str(refusal))
        return snapshot

    monkeypatch.setattr(block_series, "series_runs", interleaved)
    module.submit_next(series_dir, tmp_path, "approval")
    batches = sorted(path.name.rpartition("-")[2] for path in submitted)
    if batches != ["00"]:
        raise AssertionError(f"batch-00 was submitted {len(batches)} times: {sorted(p.name for p in submitted)}")
    if len(refusals) != 1 or "another --submit-next holds" not in refusals[0]:
        raise AssertionError(f"the overlapping call was not refused by the series lock: {refusals}")
