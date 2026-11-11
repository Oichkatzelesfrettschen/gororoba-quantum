"""Add exact scope and explicit event denominators to the retained Ascella slice analysis."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from a5_photonic_scope import (  # noqa: E402
    branch_accounting,
    check_recorded_operator,
    check_selected_columns,
    embedded_slice_scope,
)
from parallel import ordered_map  # noqa: E402

OPERATOR_TOLERANCE = Fraction(1, 10**12)


def setting_scope(task: tuple[tuple[str, int, int, int], dict[str, Any]]) -> dict[str, Any]:
    """Bind the retained optical request and check both declared unprepared success columns."""
    import ascella_a5_kernel_slice as case
    import sympy as sym

    specification, recorded_operator = task
    name, second, coefficient, preparation = specification
    left = [0] * 32
    left[1], left[second] = 1, coefficient
    optical = case.exact_operator(second, coefficient, preparation)
    requested = sym.eye(12)
    requested[:8, :8] = optical
    check_recorded_operator(recorded_operator, requested, tolerance=OPERATOR_TOLERANCE)
    inverse_preparation = sym.Matrix([[1, preparation], [1, -preparation]]) / sym.sqrt(2)
    success = sym.simplify(optical[:4, :2] * inverse_preparation)
    columns = [[Fraction(0) for _ in case.INPUT_BASIS] for _ in range(32)]
    for port, output in enumerate(case.OUTPUT_BASIS):
        for column in range(len(case.INPUT_BASIS)):
            value = success[port, column]
            if value.is_Rational is not True:
                raise ValueError("unprepared optical success columns must be rational")
            columns[output][column] = Fraction(int(value.p), int(value.q))
    check_selected_columns(columns, 32, left, case.INPUT_BASIS, scale=2)
    return {
        "name": name,
        "requested_optical_operator_matches_exact_builder": True,
        "optical_componentwise_tolerance": str(OPERATOR_TOLERANCE),
        "selected_success_operator_checked_exactly": True,
        "scope": embedded_slice_scope(32, left, case.INPUT_BASIS, reference_dimension=16, scale=2),
    }


def extend_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Reuse the admitted reader's counts and retain both denominator conventions."""
    accounting = branch_accounting(
        observation["port_counts"],
        observation["invalid_events"],
        success_modes=(0, 1, 2, 3),
        failure_modes=(4, 5, 6, 7),
    )
    for retained, recomputed in (
        ("returned_events", "returned_events"),
        ("success", "success_events"),
        ("failure", "failure_events"),
        ("sentinel", "excluded_mode_events"),
    ):
        if observation[retained] != accounting[recomputed]:
            raise ValueError(f"{observation['name']}: retained {retained} differs from its counts")
    fraction = accounting["success_given_eligible"]
    expected = fraction["numerator"] / fraction["denominator"] if fraction["defined"] else None
    if observation["conditional_success"] != expected:
        raise ValueError(f"{observation['name']}: retained conditional fraction differs from its counts")
    counts = {key: value for key, value in observation.items() if key != "conditional_success"}
    return {**counts, "event_accounting": accounting}


def _bound_json(directory: Path, name: str, digest: str) -> dict[str, Any]:
    payload = (directory / name).read_bytes()
    if hashlib.sha256(payload).hexdigest() != digest:
        raise ValueError(f"{name} changed after the original analyzer read it")
    result: dict[str, Any] = json.loads(payload, parse_float=Fraction)
    return result


def describe(directory: Path) -> dict[str, Any]:
    """Read an existing run through its original analyzer and add a versioned scope report."""
    import ascella_a5_kernel_analysis as historical
    import ascella_a5_kernel_slice as case

    original = historical.describe(directory)
    observations = original["observations"]
    manifest = _bound_json(directory, "cases.json", original["artifact_sha256"]["cases.json"])
    circuit = _bound_json(directory, "circuit.json", original["artifact_sha256"]["circuit.json"])
    if circuit["modes"] != 12 or circuit["input_state"] != [1] + [0] * 11:
        raise ValueError("the kernel-slice case requires a single photon in input mode zero")
    names = [setting[0] for setting in case.SETTINGS]
    if [row["name"] for row in observations] != names or [row["name"] for row in manifest["settings"]] != names:
        raise ValueError("returned setting order differs from the kernel-slice specification")
    if [row["ideal_success"] for row in manifest["settings"]] != [str(value) for value in case.EXPECTED]:
        raise ValueError("retained ideal probabilities differ from the kernel-slice specification")
    tasks = [
        (specification, setting["operator"])
        for specification, setting in zip(case.SETTINGS, manifest["settings"], strict=True)
    ]
    return {
        "schema": "ascella-a5-kernel-slice-scope-analysis-v1",
        "source_analysis_schema": original["schema"],
        "job_id": original["job_id"],
        "platform": original["platform"],
        "recorded_charge": str(original["charge"]),
        "artifact_sha256": original["artifact_sha256"],
        "analysis_sources": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            for path in (
                "gororoba_quantum/a5_photonic_scope.py",
                "gororoba_quantum/cd_core.py",
                "scripts/ascella_a5_kernel_scope_analysis.py",
                "scripts/ascella_a5_kernel_analysis.py",
                "scripts/ascella_a5_kernel_slice.py",
            )
        },
        "observations": ordered_map(extend_observation, observations, min_items=1),
        "operator_scope": ordered_map(setting_scope, tasks, min_items=1),
        "interpretation": (
            "Selected two-column operator conformance and descriptive returned-event fractions. "
            "The selected actions also agree exactly with embedded A4 actions; "
            "full A5 nullity, dimension discrimination and physical nonassociativity remain untested."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, help="write the versioned analysis record")
    parser.add_argument("--check", action="store_true", help="recompute and require the exact retained --out bytes")
    args = parser.parse_args(argv)
    if args.check and args.out is None:
        parser.error("--check requires --out")
    payload = (json.dumps(describe(args.run), indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    if args.check:
        if args.out.read_bytes() != payload:
            raise ValueError("retained scope analysis differs from the source-bound replay")
        print("scope analysis replay matches")
    elif args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(payload)
    else:
        sys.stdout.write(payload.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
