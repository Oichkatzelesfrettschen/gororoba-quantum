"""Checkpoint manifest of the block ladder on synthetic arrays: a matching resume returns what was saved, and every
mismatch of header, dtype, shape, digest or manifest is refused."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs/evidence/a5-exceptional-fibers/monomial-ladder"))

import ladder_checkpoint as ck  # noqa: E402

STEM = ck.stem_of("xm-nm", 32009, 8, 2)
HEADER: dict[str, Any] = {
    "slug": "xm-nm",
    "prime": 32009,
    "order": 8,
    "degree": 2,
    "batch": 256,
    "source_sha256": {"fast_ladder.py": "a" * 64, "parallel.py": "b" * 64},
    "model": {"generators": 15, "generators_sha256": "c" * 64, "initial_sha256": {"A": "d" * 64, "B": "e" * 64}},
}


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _spaces(seed: int) -> dict[str, np.ndarray]:
    grid = np.arange(12, dtype=np.uint16).reshape(3, 4) + seed
    return {"A": grid, "B": grid[:2] * 2}


def _saved(directory: Path) -> dict[str, Any]:
    manifest: dict[str, Any] = {"schema": ck.MANIFEST_SCHEMA, "header": copy.deepcopy(HEADER), "degrees": {}}
    ck.save_degree(directory, STEM, manifest, 1, _spaces(0), [{"degree": 1, "A": 3}])
    ck.save_degree(directory, STEM, manifest, 2, _spaces(5), [{"degree": 1, "A": 3}, {"degree": 2, "A": 2}])
    return manifest


def test_matching_resume_returns_the_highest_degree_and_its_rows(tmp_path: Path) -> None:
    _saved(tmp_path)
    degree, spaces, rows, _ = ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))
    _check(degree == 2)
    _check(all(np.array_equal(spaces[k], v) for k, v in _spaces(5).items()))
    _check([r["degree"] for r in rows] == [1, 2])


def test_saved_rows_do_not_alias_the_running_record(tmp_path: Path) -> None:
    rows: list[Any] = [{"degree": 1}]
    manifest: dict[str, Any] = {"schema": ck.MANIFEST_SCHEMA, "header": HEADER, "degrees": {}}
    ck.save_degree(tmp_path, STEM, manifest, 1, _spaces(0), rows)
    rows.append({"degree": 2})
    _check(len(manifest["degrees"]["1"]["rows"]) == 1)


def test_empty_directory_starts_fresh(tmp_path: Path) -> None:
    degree, spaces, rows, manifest = ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))
    _check((degree, spaces, rows, manifest["degrees"]) == (0, {}, [], {}))


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("source_sha256", "fast_ladder.py"), "0" * 64),
        (("batch",), 128),
        (("prime",), 32029),
        (("model", "generators_sha256"), "f" * 64),
        (("model", "initial_sha256", "B"), "f" * 64),
    ],
)
def test_changed_header_field_is_refused_by_name(tmp_path: Path, path: tuple[str, ...], value: Any) -> None:
    _saved(tmp_path)
    header = copy.deepcopy(HEADER)
    target = header
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(SystemExit, match="header." + r"\.".join(path) + " differs"):
        ck.resume_point(tmp_path, STEM, header)


def test_corrupted_array_is_refused(tmp_path: Path) -> None:
    _saved(tmp_path)
    victim = ck.array_file(tmp_path, STEM, 2, "A")
    array = np.load(victim)
    array[0, 0] += 1
    np.save(victim, array)
    with pytest.raises(SystemExit, match=r"d2-A\.npy sha256 is"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))


def test_array_of_another_dtype_or_shape_is_refused(tmp_path: Path) -> None:
    _saved(tmp_path)
    victim = ck.array_file(tmp_path, STEM, 2, "B")
    np.save(victim, np.load(victim).astype(np.float64))
    with pytest.raises(SystemExit, match=r"d2-B\.npy dtype is float64"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))
    np.save(victim, np.zeros((3, 3), dtype=np.uint16))
    with pytest.raises(SystemExit, match=r"d2-B\.npy shape is \[3, 3\]"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))


def test_missing_array_is_refused(tmp_path: Path) -> None:
    _saved(tmp_path)
    ck.array_file(tmp_path, STEM, 2, "A").unlink()
    with pytest.raises(SystemExit, match=r"d2-A\.npy is missing"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))


def test_checkpoint_without_manifest_is_refused(tmp_path: Path) -> None:
    _saved(tmp_path)
    (tmp_path / f"{STEM}-manifest.json").unlink()
    with pytest.raises(SystemExit, match="has no manifest"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))


def test_manifest_of_another_schema_is_refused(tmp_path: Path) -> None:
    _saved(tmp_path)
    path = tmp_path / f"{STEM}-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["schema"] = "other"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SystemExit, match="manifest.schema"):
        ck.resume_point(tmp_path, STEM, copy.deepcopy(HEADER))


def test_differing_field_names_the_first_difference() -> None:
    _check(ck.differing_field({"a": 1, "b": {"c": 2}}, {"a": 1, "b": {"c": 3}}) == "header.b.c")
    _check(ck.differing_field({"a": 1}, {"a": 1, "z": 0}) == "header.z")
    _check(ck.differing_field({"a": [1, 2]}, {"a": [1, 2]}) is None)
