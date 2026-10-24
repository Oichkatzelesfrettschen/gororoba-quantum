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
