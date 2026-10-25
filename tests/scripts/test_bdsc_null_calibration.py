import functools
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

import bdsc_diagnostic as diag  # noqa: E402
import bdsc_null_calibration as nc  # noqa: E402

# Draw indices of the seed's first 400 replicates: eight leading ones, and two (81 and 349) whose block-change
# statistics differ between libm pow and x * x, which a square taken in numpy changes.
DRAWS = 400
CHOSEN = [0, 1, 2, 3, 4, 5, 6, 7, 81, 349]


@functools.cache
def counts() -> Any:
    return nc.draw_counts(DRAWS, nc.NULL_SEED)[CHOSEN]


@functools.cache
def scalar() -> list[dict[str, float]]:
    return [nc.scalar_statistics(row) for row in counts()]


def mismatches(batched: dict[str, Any]) -> list[str]:
    """Keys and replicates where the batched statistics differ in bits from the scalar analyse."""
    reference = scalar()
    if set(batched) != set(reference[0]):
        raise AssertionError(set(batched) ^ set(reference[0]))
    return [
        f"{n} {key}"
        for n, row in enumerate(reference)
        for key, value in row.items()
        if float(value).hex() != float(batched[key][n]).hex()
    ]


def test_the_batched_statistics_equal_the_scalar_analyse_bit_for_bit() -> None:
    found = mismatches(nc.batch_statistics(counts()))
    if found:
        raise AssertionError(found[:10])


def test_the_degrees_of_freedom_equal_those_of_the_scalar_analyse() -> None:
    read = diag.analyse(nc.scalar_observed(counts()[0]))
    if {name: test["df"] for name, test in read["tests"].items()} != nc.batch_degrees():
        raise AssertionError(nc.batch_degrees())


def naive_rows(terms: list[Any]) -> Any:
    total = 0.0 + terms[0]
    for term in terms[1:]:
        total = total + term
    return total


def numpy_hypot(function: Any, first: Any, second: Any) -> Any:
    return np.hypot(first, second)


def numpy_square(values: Any) -> Any:
    return values**2


@pytest.mark.parametrize(
    ("name", "mutation"),
    [("fsum_rows", naive_rows), ("square", numpy_square), ("pair_map", numpy_hypot)],
)
def test_a_mutated_batched_path_differs_from_the_scalar_analyse(
    name: str, mutation: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(nc, name, mutation)
    if not mismatches(nc.batch_statistics(counts())):
        raise AssertionError(f"the {name} mutant reads equal to the scalar analyse")


def test_the_replicate_inputs_do_not_depend_on_the_block_size() -> None:
    whole = nc.calibrate(18, nc.NULL_SEED, block=18)
    cut = nc.calibrate(18, nc.NULL_SEED, block=5)
    if any(whole[key].tolist() != cut[key].tolist() for key in whole):
        raise AssertionError("blocks change the bytes")


def test_the_bound_flags_a_rate_outside_alpha_and_passes_alpha() -> None:
    def statistics(resolved: int) -> dict[str, Any]:
        p = np.where(np.arange(3000) < resolved, 0.0, 0.5)
        return {"tests.x.p_value": p, "residuals_beyond_margin": np.zeros(3000, dtype=np.int64)}

    ok = nc.rate_record(statistics(30), 3000, nc.NULL_SEED, "default")
    bad = nc.rate_record(statistics(60), 3000, nc.NULL_SEED, "default")
    if nc.bound_failures(ok) or len(nc.bound_failures(bad)) != 1:
        raise AssertionError((nc.bound_failures(ok), nc.bound_failures(bad)))
