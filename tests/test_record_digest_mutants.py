"""A record mutant per ``--check`` that binds a measured record by sha256.

Each test copies a retained record, flips one digit inside a numeric value at several depths of the file,
runs the script's ``--check`` through its ``main`` and requires a failure; the unmutated copy passes the
digest binding, so the mutant alone moves the verdict. Rows 0, 8 to 10 and 20 of
tests/test_cli_record_checks.py name these checks.
"""

from __future__ import annotations

import importlib
import re
import shlex
import sys
from pathlib import Path

import pytest

import record_digest

ROOT = Path(__file__).resolve().parents[1]

SNAPSHOT = "docs/evidence/calibration/ibm_kingston.json"
CONFIG_T4 = "results/kaggle/2026-10-17T212551Z-gororoba-aer-gpu-config/output/output/aer_gpu_probe.json"
CONFIG_CU13 = "results/kaggle/2026-10-18T072718Z-gororoba-aer-gpu-cu13-config/output/output/aer_gpu_probe.json"
HOST = "docs/evidence/aer_gpu_configuration/result.json"
GHOST_HOST = "docs/evidence/ghost_error_scale_branching/benchmark-host.json"
GHOST_T4 = "results/kaggle/2026-10-18T041945Z-gororoba-ghost-branching-t4/output/output/ghost_branching_benchmark.json"
UNBOUND = "matches no retained record"
WIDTHS = "--workloads toy,width --widths 7,10"

NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?:e-?\d+)?(?![\w.])", re.IGNORECASE)


def flip_digit(text: str, fraction: float) -> str:
    """TEXT with the last digit of the numeric token nearest FRACTION of the way through it changed."""
    tokens = [m for m in NUMBER.finditer(text) if m.group().lstrip("-")[0].isdigit()]
    token = tokens[int(fraction * (len(tokens) - 1))]
    digits = [i for i, c in enumerate(token.group()) if c.isdigit()]
    at = token.start() + digits[-1]
    return text[:at] + str((int(text[at]) + 1) % 10) + text[at + 1 :]


def run_check(module: str, argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Call MODULE's main as ``MODULE ARGV`` from the repository root; a digest mismatch raises ValueError."""
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(sys, "argv", [module, *argv])
    importlib.import_module(module).main()


def mutants(source: str, tmp_path: Path, name: str) -> list[Path]:
    text = (ROOT / source).read_text(encoding="utf-8")
    paths = []
    for index, fraction in enumerate((0.05, 0.5, 0.95)):
        path = tmp_path / f"{index}-{name}"
        path.write_text(flip_digit(text, fraction), encoding="utf-8")
        paths.append(path)
    return paths


@pytest.mark.parametrize("source", [SNAPSHOT, CONFIG_T4, HOST, CONFIG_CU13, GHOST_HOST, GHOST_T4])
def test_retained_copy_passes_and_mutant_fails_digest(source: str, tmp_path: Path) -> None:
    copy = tmp_path / "copy.json"
    copy.write_bytes((ROOT / source).read_bytes())
    if record_digest.RETAINED[record_digest.require_retained(copy)] != source:
        raise AssertionError(f"{source} binds to another record")
    for mutant in mutants(source, tmp_path, "m.json"):
        with pytest.raises(ValueError, match=UNBOUND):
            record_digest.require_retained(mutant)


def test_calibration_snapshot_check_fails_on_a_changed_reading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for mutant in mutants(SNAPSHOT, tmp_path, "snapshot.json"):
        with pytest.raises(ValueError, match=UNBOUND):
            run_check("calibration_snapshot", ["--check", str(mutant)], monkeypatch)


@pytest.mark.parametrize(
    ("source", "extra"), [(CONFIG_T4, WIDTHS), (HOST, ""), (CONFIG_CU13, WIDTHS)], ids=["config", "host", "cu13"]
)
def test_aer_gpu_probe_check_fails_on_a_changed_value(
    source: str, extra: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for mutant in mutants(source, tmp_path, "aer_gpu_probe.json"):
        argv = ["--check", str(mutant), *shlex.split(extra)]
        with pytest.raises(ValueError, match=UNBOUND):
            run_check("aer_gpu_probe", argv, monkeypatch)


def test_aer_gpu_probe_compare_counts_fails_on_a_changed_other_record(tmp_path: Path) -> None:
    compare_counts = importlib.import_module("aer_gpu_probe").compare_counts
    for mutant in mutants(CONFIG_T4, tmp_path, "other.json"):
        with pytest.raises(ValueError, match=UNBOUND):
            compare_counts(ROOT / CONFIG_CU13, mutant)


@pytest.mark.parametrize("source", [GHOST_HOST, GHOST_T4], ids=["host", "t4"])
def test_ghost_branching_benchmark_check_fails_on_a_changed_value(
    source: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for mutant in mutants(source, tmp_path, "benchmark.json"):
        with pytest.raises(ValueError, match=UNBOUND):
            run_check("ghost_branching_benchmark", ["--check", str(mutant)], monkeypatch)
