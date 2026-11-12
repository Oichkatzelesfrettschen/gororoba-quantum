"""Checkpoint manifest of the block ladder: a matching resume reproduces a fresh run, every mismatch is refused."""

from __future__ import annotations

import json
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("scipy")
pytest.importorskip("flint")

ROOT = Path(__file__).resolve().parents[1]
LADDER = ROOT / "docs/evidence/a5-exceptional-fibers/monomial-ladder"
sys.path.insert(0, str(LADDER))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs/evidence/a5-exceptional-fibers/kernel-limits"))

import fast_ladder_blocks as fixed  # noqa: E402
import fast_ladder_blocks_resumable as resumable  # noqa: E402
import ladder_checkpoint as ck  # noqa: E402

# The smallest cell of the same-sign X slice: orders 5 and 8, 330 columns at the top degree.
CELL = ("xm-nm", 32009, 2, 8, 256)


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _run(checkpoint: Path | None, batch: int = CELL[4]) -> dict[str, Any]:
    slug, prime, degree, order, _ = CELL
    with warnings.catch_warnings():
        # torch.sparse_csr_tensor warns once per process (beta state, invariant checks off).
        warnings.filterwarnings("ignore", message="Sparse", category=UserWarning)
        return resumable.ladder(ROOT, slug, prime, degree, order, batch, None, checkpoint)


def _ranks(record: dict[str, Any]) -> list[tuple[int, int, int, int]]:
    return [(r["degree"], r["A"], r["B"], r["r"]) for r in record["rows"]]


def _manifest(checkpoint: Path) -> tuple[Path, dict[str, Any]]:
    (path,) = checkpoint.glob("*-manifest.json")
    return path, json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def complete(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, Any]]:
    """A finished run with a checkpoint, and the ranks of the fixed engine on the same cell."""
    checkpoint = tmp_path_factory.mktemp("complete")
    record = _run(checkpoint)
    slug, prime, degree, order, batch = CELL
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Sparse", category=UserWarning)
        reference = fixed.ladder(ROOT, slug, prime, degree, order, batch, None, None)
    _check(_ranks(record) == _ranks(reference))
    return checkpoint, record


@pytest.fixture
def copy_of(complete: tuple[Path, dict[str, Any]], tmp_path: Path) -> Path:
    target = tmp_path / "checkpoint"
    shutil.copytree(complete[0], target)
    return target


def test_manifest_binds_producers_parameters_and_each_array(complete: tuple[Path, dict[str, Any]]) -> None:
    _, manifest = _manifest(complete[0])
    header = manifest["header"]
    _check(set(header["source_sha256"]) == set(complete[1]["source_sha256"]))
    _check(all(len(v) == 64 for v in header["source_sha256"].values()))
    _check(
        (header["slug"], header["prime"], header["degree"], header["order"], header["batch"]) == CELL[:2] + (2, 8, 256)
    )
    _check(set(header["model"]["initial_sha256"]) == {"A", "B"})
    _check([len(manifest["degrees"][d]["rows"]) for d in ("1", "2")] == [1, 2])
    for d in ("1", "2"):
        for key in ("A", "B"):
            meta = manifest["degrees"][d][key]
            array = np.load(complete[0] / meta["file"], allow_pickle=False)
            _check(meta["dtype"] == "uint16" and meta["shape"] == list(array.shape))
            _check(meta["sha256"] == ck.array_sha256(array))


def test_resume_with_matching_manifest_reproduces_the_fresh_run(
    complete: tuple[Path, dict[str, Any]], copy_of: Path
) -> None:
    path, manifest = _manifest(copy_of)
    del manifest["degrees"]["2"]
    path.write_text(json.dumps(manifest), encoding="utf-8")
    record = _run(copy_of)
    _check(record["resumed_after_degree"] == 1)
    _check(_ranks(record) == _ranks(complete[1]))
    _check(record["complete"] is True)


def test_resume_after_the_last_degree_returns_the_saved_rows(
    complete: tuple[Path, dict[str, Any]], copy_of: Path
) -> None:
    record = _run(copy_of)
    _check(record["resumed_after_degree"] == 2)
    _check(_ranks(record) == _ranks(complete[1]))


def test_changed_source_digest_is_refused(copy_of: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    real = resumable.producer_digests

    def altered(root: Path, name: str) -> dict[str, str]:
        digests = real(root, name)
        digests["fast_ladder.py"] = "0" * 64
        return digests

    monkeypatch.setattr(resumable, "producer_digests", altered)
    with pytest.raises(SystemExit, match=r"header\.source_sha256\.fast_ladder\.py differs"):
        _run(copy_of)


def test_changed_parameter_is_refused(copy_of: Path) -> None:
    with pytest.raises(SystemExit, match=r"header\.batch differs"):
        _run(copy_of, batch=128)


def test_changed_generator_terms_are_refused(copy_of: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(resumable, "generators_sha256", lambda *_: "f" * 64)
    with pytest.raises(SystemExit, match=r"header\.model\.generators_sha256 differs"):
        _run(copy_of)


def test_corrupted_array_is_refused(copy_of: Path) -> None:
    _, manifest = _manifest(copy_of)
    victim = copy_of / manifest["degrees"]["2"]["A"]["file"]
    array = np.load(victim)
    array[0, 0] = (int(array[0, 0]) + 1) % 32009
    np.save(victim, array)
    with pytest.raises(SystemExit, match=r"d2-A\.npy sha256 is"):
        _run(copy_of)
