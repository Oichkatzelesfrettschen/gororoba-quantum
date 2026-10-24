"""Contract for qd_platform.observe: every observed route lands in observation.json as scrubbed JSON, digested text,
or a recorded refusal, and every Explorer platform's processor record follows.
"""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch

import qd_platform


class Answer(io.BytesIO):
    status = 200

    def __init__(self, data: bytes, content_type: str) -> None:
        super().__init__(data)
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> Answer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def fake_open(call: Any, timeout: float) -> Answer:
    url = call.full_url
    if url.endswith("/api/rss-feed"):
        return Answer(b"<rss>feed</rss>", "application/rss+xml")
    if url in (qd_platform.API + "/", qd_platform.ACCOUNT_API + "/"):
        raise urllib.error.HTTPError(url, 302, "Found", {}, io.BytesIO(b""))  # type: ignore[arg-type]
    if url.endswith("/api/platforms/public/explorer"):
        return Answer(json.dumps([{"name": "qpu:ascella", "user_id": "secret"}]).encode(), "application/json")
    return Answer(json.dumps({"route": url, "email": "someone@example.org"}).encode(), "application/json")


def test_observe_records_every_route_scrubbed() -> None:
    with TemporaryDirectory() as directory, patch.object(qd_platform, "token", return_value="t"):
        with patch.object(qd_platform.OPENER, "open", side_effect=fake_open):
            qd_platform.observe(Path(directory))
        record = json.loads((Path(directory) / "observation.json").read_text(encoding="utf-8"))
    routes = [entry["route"] for entry in record["routes"]]
    expected = [route for _, route, _ in qd_platform.OBSERVED_ROUTES] + ["/api/platforms/qpu%3Aascella/processor"]
    if routes != expected:
        raise AssertionError(routes)
    text = json.dumps(record)
    if "secret" in text or "someone@example.org" in text:
        raise AssertionError("a forbidden key survived the scrub")
    feed = next(entry for entry in record["routes"] if entry["route"] == "/api/rss-feed")
    homes = [entry for entry in record["routes"] if entry["route"] == "/"]
    if feed.get("text") != "<rss>feed</rss>" or "sha256" not in feed:
        raise AssertionError(feed)
    if [entry.get("http_status") for entry in homes] != [302, 302] or not all(entry["refused"] for entry in homes):
        raise AssertionError(homes)
