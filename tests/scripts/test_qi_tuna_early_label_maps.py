"""Ensure early-bit relabeling cannot alter observed terminal differences."""

from __future__ import annotations

import itertools
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/qi_tuna_early_label_maps.py"


def test_retained_counts_expose_terminal_lower_bound(tmp_path: Path) -> None:
    """Catch a permutation, polarity, decoding or total-variation denominator error."""
    output = tmp_path / "early-label-maps.json"
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise AssertionError(f"early-label replay failed: {process.stderr}")
    cases = json.loads(output.read_bytes())["cases"]
    if cases["nominal_zero_prefix"]["minimum_tv_numerator"] != 6310:
        raise AssertionError("nominal-zero minimum total variation numerator differs")
    if cases["nominal_zero_prefix"]["terminal_tv_numerator"] != 6286:
        raise AssertionError("nominal-zero terminal lower bound differs")
    if cases["nominal_one"]["minimum_tv_numerator"] != 600:
        raise AssertionError("nominal-one minimum total variation numerator differs")
    for case in cases.values():
        if len(case["maps"]) != 48 or case["tv_denominator"] != 16384:
            raise AssertionError("the replay must retain all 48 maps and the correct denominator")


def test_early_remapping_never_hides_terminal_change() -> None:
    """Reject implementations that move terminal bits while permuting early labels."""
    import qi_tuna_early_label_maps as label_maps

    baseline = [0] * 64
    baseline[0] = 4096
    rotated = [0] * 64
    rotated[9] = 4096
    result = label_maps.compare(baseline, rotated, baseline)
    if result["terminal_tv_numerator"] != 16384 or result["minimum_tv_numerator"] != 16384:
        raise AssertionError("disjoint terminal labels must keep total variation exactly one")
    if any(row["tv_numerator"] != 16384 for row in result["maps"]):
        raise AssertionError("an early-label map changed a disjoint terminal distribution")


def test_maps_can_repair_a_pure_early_polarity_change() -> None:
    """Reject an implementation that cannot find an allowed early-label inversion."""
    import qi_tuna_early_label_maps as label_maps

    baseline = [0] * 64
    baseline[0] = 4096
    rotated = [0] * 64
    rotated[1] = 4096
    result = label_maps.compare(baseline, rotated, baseline)
    if result["minimum_tv_numerator"] != 0 or result["terminal_tv_numerator"] != 0:
        raise AssertionError("a pure early-label inversion must be recoverable")
    if result["maps"][0]["tv_numerator"] != 16384:
        raise AssertionError("the identity mapping must preserve the original mismatch")


def test_record_replay_rejects_mutation_and_existing_output(tmp_path: Path) -> None:
    """Catch altered conclusions and prevent replacement of an existing evidence file."""
    retained = ROOT / "docs/evidence/tuna-projector-geometry/early-label-map-analysis.json"
    for options in ([], ["-O"]):
        process = subprocess.run(
            [sys.executable, *options, str(SCRIPT), "--check", str(retained)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if process.returncode != 0:
            raise AssertionError(f"retained replay failed: {process.stderr}")
    target = tmp_path / "existing.json"
    original = retained.read_bytes()
    target.write_bytes(original)
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(target)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if process.returncode == 0 or target.read_bytes() != original:
        raise AssertionError("an existing evidence file must remain unchanged")
    changed = json.loads(original)
    changed["cases"]["nominal_zero_prefix"]["terminal_tv_numerator"] = 0
    target.write_text(json.dumps(changed, indent=2, sort_keys=True) + "\n")
    process = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(target)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if process.returncode == 0:
        raise AssertionError("a mutated terminal bound must fail exact replay")


def test_each_retained_map_score_matches_scalar_reconstruction() -> None:
    """Catch an incorrect map score even when the minimum and terminal bound stay fixed."""
    joint_path = ROOT / "docs/evidence/tuna-projector-geometry/joint-response-analysis.json"
    record_path = ROOT / "docs/evidence/tuna-projector-geometry/early-label-map-analysis.json"
    joint = json.loads(joint_path.read_bytes())
    result = json.loads(record_path.read_bytes())
    for name, case in joint["cases"].items():
        before, rotated, after = [job["joint_counts"] for job in case["jobs"]]
        for mapping in result["cases"][name]["maps"]:
            scalar_counts = [0] * 64
            for index, count in enumerate(rotated):
                early = index % 8
                mapped_early = sum(
                    ((((early >> source) & 1) ^ ((mapping["polarity_mask"] >> bit) & 1)) << bit)
                    for bit, source in enumerate(mapping["output_bit_sources"])
                )
                scalar_counts[(index // 8) * 8 + mapped_early] += count
            numerator = sum(abs(2 * scalar_counts[index] - before[index] - after[index]) for index in range(64))
            if numerator != mapping["tv_numerator"]:
                raise AssertionError(f"scalar score differs for {name}: {mapping}")


def validate_signed_permutation_family(rows: list[dict[str, Any]]) -> None:
    """Validate the complete signed-permutation family as distinct terminal-preserving bijections."""
    expected = {(permutation, polarity) for permutation in itertools.permutations(range(3)) for polarity in range(8)}
    observed: set[tuple[tuple[int, ...], int]] = {
        (tuple(row["output_bit_sources"]), row["polarity_mask"]) for row in rows
    }
    if len(rows) != 48 or observed != expected:
        raise ValueError("the signed-permutation family is incomplete or duplicated")
    transformations = set()
    for sources, polarity in expected:
        mapped = tuple(
            (index & 56)
            | sum(((((index >> source) & 1) ^ ((polarity >> bit) & 1)) << bit) for bit, source in enumerate(sources))
            for index in range(64)
        )
        if len(set(mapped)) != 64 or any((source & 56) != (target & 56) for source, target in enumerate(mapped)):
            raise ValueError("a map is not a terminal-preserving bijection")
        transformations.add(mapped)
    if len(transformations) != 48:
        raise ValueError("the maps are not 48 distinct transformations")
    for mapped in transformations:
        inverse = tuple(mapped.index(index) for index in range(64))
        if inverse not in transformations:
            raise ValueError("the transformation family is not closed under inverse")


def test_recorded_signed_maps_are_complete_bijections() -> None:
    """Catch coherent regeneration with a duplicated or incomplete transformation family."""
    import pytest

    record = json.loads((ROOT / "docs/evidence/tuna-projector-geometry/early-label-map-analysis.json").read_bytes())
    for case in record["cases"].values():
        rows = case["maps"]
        validate_signed_permutation_family(rows)
        duplicate = [dict(row, output_bit_sources=[0, 1, 2]) for row in rows]
        with pytest.raises(ValueError, match="incomplete or duplicated"):
            validate_signed_permutation_family(duplicate)
