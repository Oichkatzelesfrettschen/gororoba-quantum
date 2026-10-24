"""Contract for scripts/provider_credits.py: the snapshot table renders, a failed reader is isolated and reported
as `read failed: <reason>`, and the alert thresholds fire, all with fake readers and no network.
"""

from __future__ import annotations

import provider_credits
import pytest


def test_self_test_with_fake_readers() -> None:
    provider_credits.self_test()


@pytest.mark.parametrize("secret", ["a@b.example", "crn:v1:x:y", "123456789012"])
def test_scrub_removes_identifiers(secret: str) -> None:
    text = provider_credits.scrub(f"denied for {secret} here")
    if secret in text:
        raise AssertionError(f"scrub kept {secret}")
