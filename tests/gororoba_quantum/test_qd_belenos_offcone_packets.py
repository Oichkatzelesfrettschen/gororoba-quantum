"""The off-cone packet reading: its arithmetic on small cells and its paired self-test controls."""

from __future__ import annotations

import math

import pytest
import qd_belenos_offcone_packets as packets


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_self_test_passes(capsys: pytest.CaptureFixture[str]) -> None:
    _check(packets.self_test() == 0, "the packet self-test returns 0")
    _check("passed" in capsys.readouterr().out, "the packet self-test reports its pass")


def test_exposures_separate_on_their_own_law() -> None:
    for law, winner, loser in (
        ("time", "acquisition_s_estimate", "samples"),
        ("samples", "samples", "acquisition_s_estimate"),
    ):
        y, exposure = packets.synthetic(law)
        won = packets.fit(y, exposure[winner])["deviance"]
        lost = packets.fit(y, exposure[loser])["deviance"]
        _check(lost - won > 20, f"{law}: the {winner} exposure wins by {lost - won}")


def test_deviance_and_likelihood_of_a_known_fit() -> None:
    y, mu = [2, 0, 4], [1.0, 1.0, 5.0]
    expected = 2 * (2 * math.log(2) - 1 + 1 + 4 * math.log(0.8) + 1)
    _check(abs(packets.deviance(y, mu) - expected) < 1e-12, "deviance of 2,0,4 against 1,1,5")
    _check(abs(packets.log_likelihood([0], [1.0]) + 1.0) < 1e-12, "P(0 | mean 1) = e^-1")
    fitted = packets.fit([3, 3], [1.0, 3.0])
    _check(fitted["df"] == 1 and abs(fitted["rate"] - 1.5) < 1e-12, "one rate over the pooled exposure")


def test_packets_skip_the_hot_mode_and_count_at_least_one() -> None:
    cell = {"off_cone_by_mode": {"0": 47, "1": 95, "5": 4000, "9": 3}}
    _check(packets.packets_of(cell) == 1 + 2 + 1, "mode 5 is skipped; 47 -> 1, 95 -> 2, 3 -> 1")
    _check(packets.bins_of([0, 1, 31, 32, 99, 100]) == [1, 2, 2, 1], "bin edges at 1, 32 and 100")
    _check([packets.perf_class(p) for p in (0.001, 0.003, 0.009, 0.05)] == [0, 1, 2, 3], "four physical_perf classes")


def test_presence_counts_modes_other_than_the_hot_mode() -> None:
    cell = {"off_cone_by_mode": {"0": 47, "1": 95, "5": 4000, "9": 0}}
    _check(packets.presence_of(cell) == 2, "modes 0 and 1 are present; mode 5 is skipped; a zero count is absent")


def test_duration_fit_recovers_an_entry_law() -> None:
    cells = [
        {"run": f"r{k}", "job_duration_s": 8.0 + 6.0 * n, "samples": 1000 * (k + 1)}
        for k, n in enumerate((1, 3, 5, 7))
        for _ in range(n)
    ]
    fitted = packets.duration_fit(cells)
    _check(abs(fitted["per_entry_s"] - 6.0) < 1e-3 and abs(fitted["constant_s"] - 8.0) < 1e-3, f"fit {fitted}")
    _check(fitted["per_10000_samples_s"] <= 1e-3, "no positive slope in samples")
