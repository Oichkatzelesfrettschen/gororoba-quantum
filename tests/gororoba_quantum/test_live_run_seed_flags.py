"""live_run's --seed-transpiler and --seed-simulator: QRNG spellings, global rebinding, policy and seed_source."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path

import pytest

import live_run
import qpu_cases
import qrng_seeds

ROOT = Path(__file__).resolve().parents[2]


def qrng_reference(index: int) -> tuple[str, int]:
    """A qrng: reference into the newest retained ANU draw that holds the index, and the value it names."""
    draws = sorted((ROOT / "docs/evidence/anu_qrng").glob("draw-*.json"))
    draw = next(path for path in reversed(draws) if len(json.loads(path.read_text(encoding="utf-8"))["values"]) > index)
    reference = f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}"
    return reference, qrng_seeds.resolve(reference)[0]


def run_until_parsed(argv: list[str]) -> None:
    """Run main up to its first argument check: --submit without --out stops right after the seeds rebind."""
    with contextlib.redirect_stderr(io.StringIO()), pytest.raises(SystemExit):
        live_run.main([*argv, "--submit"])


def test_main_rebinds_the_seed_globals_and_restores_the_defaults() -> None:
    transpiler, transpiler_value = qrng_reference(0)
    simulator, simulator_value = qrng_reference(1)
    try:
        run_until_parsed(["--seed-transpiler", transpiler, "--seed-simulator", simulator])
        if (live_run.SEED_TRANSPILER, live_run.SEED_SIMULATOR) != (transpiler_value, simulator_value):
            raise AssertionError((live_run.SEED_TRANSPILER, live_run.SEED_SIMULATOR))
    finally:
        run_until_parsed([])
    if (live_run.SEED_TRANSPILER, live_run.SEED_SIMULATOR) != (
        live_run.REPRODUCTION_SEED_TRANSPILER,
        live_run.REPRODUCTION_SEED_SIMULATOR,
    ):
        raise AssertionError("a default invocation left a previous run's seeds in place")


def test_a_plain_integer_other_than_the_default_is_refused() -> None:
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr), pytest.raises(SystemExit):
        live_run.main(["--seed-transpiler", "12345"])
    if "qrng:<draw>#<index>" not in stderr.getvalue():
        raise AssertionError(stderr.getvalue())
    run_until_parsed([])


def namespace(**sources: str) -> argparse.Namespace:
    args = argparse.Namespace(seed_experiment="2026-10-25T000000.000000Z")
    for dest, _ in live_run.SEED_FLAGS:
        setattr(args, f"{dest}_source", sources.get(dest, "default"))
    return args


def test_default_seeds_add_no_policy_key_and_no_seed_source() -> None:
    args = namespace()
    if live_run.seed_source_entries(args):
        raise AssertionError("default seeds wrote a seed_source")
    if any(source != "default" for source in live_run.seed_spellings(args).values()):
        raise AssertionError(live_run.seed_spellings(args))


def test_a_qrng_seed_records_its_spelling_and_experiment() -> None:
    reference, _ = qrng_reference(2)
    args = namespace(seed_transpiler=reference)
    entries = live_run.seed_source_entries(args)
    flags = [entry["flag"] for entry in entries]
    if flags != ["--seed-transpiler", "--seed-simulator"]:
        raise AssertionError(flags)
    if entries[0]["sources"] != [reference] or entries[1]["sources"] != ["default"]:
        raise AssertionError(entries)
    if {entry["experiment"] for entry in entries} != {"2026-10-25T000000.000000Z"}:
        raise AssertionError(entries)
    args.seed_experiment = None
    with pytest.raises(live_run.LiveRunError):
        live_run.seed_source_entries(args)


def test_the_replay_passes_a_seed_spelling_and_refuses_a_bare_integer() -> None:
    reference, _ = qrng_reference(3)
    record = qpu_cases._fixture()
    record["policy"]["seed_transpiler"] = reference
    arguments = qpu_cases._reproduction_arguments(record, Path("results/live/fixture/record.json"))
    if f"--seed-transpiler {reference}" not in " ".join(arguments):
        raise AssertionError(arguments)
    record["policy"]["seed_transpiler"] = 12345
    with pytest.raises(ValueError):
        qpu_cases._reproduction_arguments(record, Path("results/live/fixture/record.json"))
