"""Contracts for math_sources: the Rocq sources of gororoba-math resolve only at the pin with their retained
digests.

Each test builds a repository root and a gororoba-math checkout in tmp_path, so no check reads another repository.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import math_sources

SOURCES = {
    "CdOne.v": b"Definition one := 1.\n",
    "CdTwo.v": b"Require CdOne.\n",
    "Standalone.v": b"Definition s := 0.\n",
}
LOCAL = {"Kept.v": b"Definition kept := 2.\n"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *arguments],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def build_math(directory: Path, sources: dict[str, bytes]) -> str:
    quantum = directory / "rocq/quantum"
    quantum.mkdir(parents=True)
    (quantum / "_RocqProject").write_text('-Q . ""\n' + "".join(f"{name}\n" for name in sources), encoding="utf-8")
    for name, data in sources.items():
        (quantum / name).write_bytes(data)
    git(directory, "init", "-q")
    git(directory, "add", ".")
    git(directory, "commit", "-q", "-m", "fixture")
    return git(directory, "rev-parse", "HEAD")


def build_root(directory: Path, pin: str) -> None:
    (directory / "ci").mkdir(parents=True)
    (directory / "ci/gororoba_math.pin").write_text(pin + "\n", encoding="utf-8")
    bundle = directory / "docs/evidence/bundle"
    bundle.mkdir(parents=True)
    rows = "".join(f"{sha(SOURCES[name])}  proofs/{name}\n" for name in ("CdOne.v", "CdTwo.v"))
    (bundle / "source_hashes.sha256").write_text(rows, encoding="utf-8")
    (bundle / "replay_rocq.sh").write_text("# bundle script\n", encoding="utf-8")
    (directory / "docs/state").mkdir(parents=True)
    evidence = [{"path": "proofs/Standalone.v", "sha256": sha(SOURCES["Standalone.v"])}]
    (directory / "docs/state/research_state.json").write_text(json.dumps({"claims": [{"evidence": evidence}]}))
    (directory / "proofs").mkdir()
    for name, data in LOCAL.items():
        (directory / "proofs" / name).write_bytes(data)
    (directory / "results").mkdir()
    (directory / "results/record.json").write_text("{}", encoding="utf-8")


@pytest.fixture
def fixture(tmp_path: Path) -> tuple[Path, Path]:
    math = tmp_path / "math"
    math.mkdir()
    pin = build_math(math, SOURCES)
    root = tmp_path / "root"
    build_root(root, pin)
    return root, math


def test_checkout_resolves_the_pinned_commit(fixture: tuple[Path, Path]) -> None:
    root, math = fixture
    found = math_sources.checkout({"GOROROBA_MATH": str(math)}, root)
    if found != math or math_sources.moved_names(math) != sorted(SOURCES, key=list(SOURCES).index):
        raise AssertionError((found, math_sources.moved_names(math)))


def test_unset_variable_fails_with_a_message(fixture: tuple[Path, Path]) -> None:
    root, _math = fixture
    for environ in ({}, {"GOROROBA_MATH": ""}):
        with pytest.raises(math_sources.MathSourcesError, match="GOROROBA_MATH is unset"):
            math_sources.checkout(environ, root)


def test_head_off_the_pin_fails(fixture: tuple[Path, Path]) -> None:
    root, math = fixture
    (math / "rocq/quantum/Extra.v").write_bytes(b"x\n")
    git(math, "add", ".")
    git(math, "commit", "-q", "-m", "second")
    with pytest.raises(math_sources.MathSourcesError, match="names"):
        math_sources.checkout({"GOROROBA_MATH": str(math)}, root)
    math_sources.checkout({"GOROROBA_MATH": str(math)}, root, verify_pin=False)


def test_path_without_project_file_fails(fixture: tuple[Path, Path], tmp_path: Path) -> None:
    root, _math = fixture
    with pytest.raises(math_sources.MathSourcesError, match="holds no rocq/quantum/_RocqProject"):
        math_sources.checkout({"GOROROBA_MATH": str(tmp_path)}, root)


def test_recorded_digests_join_ledgers_and_registry(fixture: tuple[Path, Path]) -> None:
    root, _math = fixture
    recorded = math_sources.recorded_digests(root)
    if recorded != {name: sha(data) for name, data in SOURCES.items()}:
        raise AssertionError(recorded)


def test_conflicting_digests_fail(fixture: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    root, _math = fixture
    other = root / "docs/evidence/other"
    other.mkdir()
    (other / "source_hashes.sha256").write_text(f"{sha(b'x')}  proofs/CdOne.v\n", encoding="utf-8")
    with pytest.raises(math_sources.MathSourcesError, match="CdOne.v has 2 recorded digests"):
        math_sources.recorded_digests(root)
    monkeypatch.setattr(math_sources, "STALE_MANIFESTS", frozenset({"docs/evidence/other/source_hashes.sha256"}))
    if math_sources.recorded_digests(root)["CdOne.v"] != sha(SOURCES["CdOne.v"]):
        raise AssertionError("a ledger named stale leaves the other records in force")


def test_a_flipped_byte_fails_the_digest_check(fixture: tuple[Path, Path]) -> None:
    root, math = fixture
    math_sources.verified_sources(math, root)
    path = math / "rocq/quantum/CdTwo.v"
    path.write_bytes(path.read_bytes().replace(b"One", b"Ond"))
    with pytest.raises(math_sources.MathSourcesError, match="CdTwo.v differs from the retained digest"):
        math_sources.verified_sources(math, root)


def test_a_source_without_a_recorded_digest_fails(fixture: tuple[Path, Path]) -> None:
    root, math = fixture
    (math / "rocq/quantum/_RocqProject").write_text('-Q . ""\nCdOne.v\nNew.v\n', encoding="utf-8")
    (math / "rocq/quantum/New.v").write_bytes(b"x\n")
    with pytest.raises(math_sources.MathSourcesError, match="no retained record holds a digest of New.v"):
        math_sources.verified_sources(math, root)


def test_reference_names_a_source_of_the_project_file(fixture: tuple[Path, Path]) -> None:
    _root, math = fixture
    if math_sources.resolve_reference("gororoba-math:rocq/quantum/CdOne.v", math) != math / "rocq/quantum/CdOne.v":
        raise AssertionError("reference resolves to the checkout file")
    for bad in ("proofs/CdOne.v", "gororoba-math:rocq/quantum/Missing.v", "gororoba-math:rocq/quantum/a/CdOne.v"):
        with pytest.raises(math_sources.MathSourcesError):
            math_sources.resolve_reference(bad, math)


def test_shadow_root_holds_moved_and_kept_sources(fixture: tuple[Path, Path], tmp_path: Path) -> None:
    root, math = fixture
    shadow = math_sources.shadow_root(tmp_path / "shadow", math, root)
    expected = {**SOURCES, **LOCAL}
    found = {path.name: path.read_bytes() for path in (shadow / "proofs").iterdir()}
    if found != expected:
        raise AssertionError(sorted(found))
    if not (shadow / "results/record.json").is_file() or not (shadow / "docs/state/research_state.json").is_file():
        raise AssertionError("top-level entries of the repository stay reachable")
    if (shadow / ".git").exists():
        raise AssertionError("the shadow root carries no git directory")


def test_shadow_root_with_a_bundle_resolves_three_levels_up(fixture: tuple[Path, Path], tmp_path: Path) -> None:
    root, math = fixture
    shadow = math_sources.shadow_root(tmp_path / "shadow", math, root, bundle="bundle")
    script = shadow / "docs/evidence/bundle/replay_rocq.sh"
    if script.is_symlink() or script.read_bytes() != (root / "docs/evidence/bundle/replay_rocq.sh").read_bytes():
        raise AssertionError("the bundle is a byte-identical copy")
    if (script.parent / "../../..").resolve() != shadow.resolve():
        raise AssertionError("repository_root of the script is the shadow root")
    if (shadow / "proofs/CdOne.v").read_bytes() != SOURCES["CdOne.v"]:
        raise AssertionError("the bundle reads the moved source")


def test_a_kept_source_that_the_project_file_lists_resolves_to_the_checkout(
    fixture: tuple[Path, Path], tmp_path: Path
) -> None:
    root, math = fixture
    (root / "proofs/CdOne.v").write_bytes(b"stale local copy\n")
    shadow = math_sources.shadow_root(tmp_path / "shadow", math, root)
    if (shadow / "proofs/CdOne.v").read_bytes() != SOURCES["CdOne.v"]:
        raise AssertionError("a name in the project file comes from gororoba-math")
