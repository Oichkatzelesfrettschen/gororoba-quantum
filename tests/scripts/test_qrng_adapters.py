"""Each QRNG adapter rejects its own mutations and admits every retained draw of its source."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import anu_qrng
import outshift_qrng
import pytest
import quandela_qrng

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("self_test", [anu_qrng.self_test, outshift_qrng.self_test, quandela_qrng.self_test])
def test_adapter_self_test(self_test: Callable[[], int]) -> None:
    if self_test() != 0:
        raise AssertionError(f"{self_test.__module__} self-test failed")


@pytest.mark.parametrize(("check", "directory"), [(anu_qrng.check, "anu_qrng"), (outshift_qrng.check, "outshift_qrng")])
def test_retained_draws_are_admitted(check: Callable[[Path], int], directory: str) -> None:
    if check(ROOT / "docs" / "evidence" / directory) < 1:
        raise AssertionError(f"docs/evidence/{directory} holds no admitted draw")


def test_keyed_requests_refuse_redirects() -> None:
    """A 302 from the service surfaces as an error, and the key header never reaches the redirect target."""
    import http.server
    import threading
    import urllib.error
    import urllib.request

    reached: list[str | None] = []

    class Target(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            reached.append(self.headers.get("x-api-key"))
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args: object) -> None:
            pass

    target = http.server.HTTPServer(("127.0.0.1", 0), Target)

    class Redirect(Target):
        def do_GET(self) -> None:
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{target.server_port}/")
            self.end_headers()

    origin = http.server.HTTPServer(("127.0.0.1", 0), Redirect)
    for server in (target, origin):
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        request = urllib.request.Request(f"http://127.0.0.1:{origin.server_port}/", headers={"x-api-key": "k"})
        with pytest.raises(urllib.error.HTTPError) as refused:
            anu_qrng.OPENER.open(request, timeout=5)
        if refused.value.code != 302 or reached:
            raise AssertionError(f"redirect followed: status {refused.value.code}, target saw {reached}")
    finally:
        for server in (target, origin):
            server.shutdown()
            server.server_close()
