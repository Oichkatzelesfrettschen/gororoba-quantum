"""qrng_seeds parses the three seed spellings and refuses a bare non-default integer, against a retained ANU draw."""

from __future__ import annotations

import qrng_seeds


def test_self_test_passes_on_the_retained_draws() -> None:
    if qrng_seeds.self_test() != 0:
        raise AssertionError("qrng_seeds self-test failed")
