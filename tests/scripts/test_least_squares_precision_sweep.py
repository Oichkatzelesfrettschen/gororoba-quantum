"""The portable least-squares precision sweep keeps host rows public and skips only the configurations a host cannot
run (docs/evidence/least-squares-precision/fp_host.py, fp_sweep.py)."""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs/evidence/least-squares-precision"))

import fp_host  # noqa: E402
import fp_sweep  # noqa: E402

PUBLIC_OS_KEYS = {"system", "wsl"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_os_record_holds_the_family_only() -> None:
    keys = set(fp_host.os_info())
    require(keys <= PUBLIC_OS_KEYS, f"os_info records {sorted(keys - PUBLIC_OS_KEYS)} beyond the OS family")


@pytest.mark.parametrize("label", ["", "-lead", "a/b", "a b", socket.gethostname().split(".")[0]])
def test_label_error_refuses_unpublishable_labels(label: str) -> None:
    if label == socket.gethostname().split(".")[0] and len(label) < 3:
        pytest.skip("hostname shorter than the three characters label_error matches")
    require(fp_host.label_error(label) is not None, f"label {label!r} accepted")


def test_label_error_admits_a_plain_label() -> None:
    require(fp_host.label_error("zen4-wsl") is None, "a plain label refused")


@pytest.mark.parametrize("quick", [False, True])
def test_disabled_quadblas_skips_exactly_the_quaddtype_configurations(quick: bool) -> None:
    configs = fp_sweep.configs(4, quick)
    status: dict[str, str | None] = {"x87": None, "quad": None, "quadblas": "QuadBLAS is disabled", "scipy": None}
    skipped = {c.label for c in configs if fp_sweep.skip_reason(c, status)}
    quaddtype = {c.label for c in configs if "FP_QUAD_BACKEND" in c.env}
    require(skipped == quaddtype, f"skipped {sorted(skipped ^ quaddtype)} differ from the quaddtype configurations")
    require(len(quaddtype) == (4 if quick else 12), f"{len(quaddtype)} quaddtype configurations at four CPUs")
