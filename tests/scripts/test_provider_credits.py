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


def test_anu_counts_only_keyed_draws(tmp_path, monkeypatch) -> None:
    import datetime as dt
    import json

    import provider_credit_readers as readers

    month = dt.datetime.now(dt.UTC).strftime("%Y-%m")
    evidence = tmp_path / "docs/evidence/anu_qrng"
    evidence.mkdir(parents=True)
    sources = ["https://api.quantumnumbers.anu.edu.au?length=8", "https://qrng.anu.edu.au/API/jsonI.php?length=8"]
    for index, source in enumerate(sources):
        (evidence / f"draw-{month}-0{index}T000000Z.json").write_text(json.dumps({"source": source}))
    monkeypatch.setattr(readers, "ROOT", tmp_path)
    (row,) = readers.read_anu()
    if row["used"] != 1.0:
        raise AssertionError(f"keyless draw counted against the keyed month: {row}")
