"""Unexecuted cancellations remain account records without becoming acquisitions."""

import pytest
import research_state


def test_unexecuted_cancellation_is_not_a_run() -> None:
    provider = research_state.IbmRuns.__new__(research_state.IbmRuns)
    provider.jobs = [
        {
            "job_id": "cancelled",
            "run": None,
            "provenance": "unexecuted_cancellation",
            "status": "CANCELLED",
            "final_qpu_charge_seconds": 0,
        }
    ]
    provider.status = {"cancelled": "CANCELLED"}
    if provider.runs() != {}:
        raise AssertionError("an unexecuted cancellation appeared as an acquisition")
    provider.jobs[0]["final_qpu_charge_seconds"] = 1
    with pytest.raises(ValueError, match="lacks a retained run"):
        provider.runs()
