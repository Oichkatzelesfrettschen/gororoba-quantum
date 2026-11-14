"""Contract for ci/fetch_gororoba_math.sh: it accepts only an https:// URL or an existing absolute directory, and
it resets and cleans only a DEST that is absent, empty or a repository the script created.

Each test copies the script beside its own pin into tmp_path and fetches from a repository built there, so no test
reaches a network or another repository.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "ci/fetch_gororoba_math.sh"
IDENTITY = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]


def git(directory: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), "-c", "core.fsmonitor=false", *IDENTITY, *arguments],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


@pytest.fixture
def world(tmp_path: Path) -> tuple[Path, Path]:
    """The script with a pin file, and a source repository whose HEAD the pin names."""
    ci = tmp_path / "ci"
    ci.mkdir()
    shutil.copyfile(SCRIPT, ci / "fetch_gororoba_math.sh")
    source = tmp_path / "source"
    (source / "rocq/quantum").mkdir(parents=True)
    (source / "rocq/quantum/One.v").write_text("Definition one := 1.\n", encoding="utf-8")
    git(source, "init", "-q")
    git(source, "add", ".")
    git(source, "commit", "-q", "-m", "fixture")
    (ci / "gororoba_math.pin").write_text(git(source, "rev-parse", "HEAD") + "\n", encoding="utf-8")
    return ci / "fetch_gororoba_math.sh", source


def fetch(script: Path, url: str, destination: Path) -> subprocess.CompletedProcess[str]:
    environment = {"PATH": "/usr/bin:/bin:/usr/local/bin", "GOROROBA_MATH_URL": url, "HOME": str(script.parent)}
    return subprocess.run(
        ["sh", str(script), str(destination), "rocq/quantum"],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


@pytest.mark.parametrize(
    "url", ["ext::sh -c true", "relative/source", "file:///tmp/x", "http://example.invalid/x", "/a b"]
)
def test_a_url_that_is_not_https_or_an_absolute_directory_is_refused(
    world: tuple[Path, Path], tmp_path: Path, url: str
) -> None:
    script, _source = world
    result = fetch(script, url, tmp_path / "dest")
    if result.returncode != 2 or (tmp_path / "dest").exists():
        raise AssertionError((url, result.returncode, result.stderr))


def test_an_absolute_directory_that_does_not_exist_is_refused(world: tuple[Path, Path], tmp_path: Path) -> None:
    script, _source = world
    if fetch(script, str(tmp_path / "absent"), tmp_path / "dest").returncode != 2:
        raise AssertionError("a missing directory passed as a URL")


def test_a_local_directory_fetches_and_a_second_run_reuses_the_checkout(
    world: tuple[Path, Path], tmp_path: Path
) -> None:
    script, source = world
    destination = tmp_path / "dest"
    first = fetch(script, str(source), destination)
    if first.returncode != 0 or not (destination / "rocq/quantum/One.v").is_file():
        raise AssertionError(first.stderr)
    (destination / "stray.txt").write_text("x", encoding="utf-8")
    second = fetch(script, str(source), destination)
    if second.returncode != 0 or (destination / "stray.txt").exists():
        raise AssertionError("the reuse did not clean the checkout it created")


def test_a_reused_destination_with_another_origin_is_refused(world: tuple[Path, Path], tmp_path: Path) -> None:
    script, source = world
    destination = tmp_path / "dest"
    fetch(script, str(source), destination)
    (destination / "stray.txt").write_text("x", encoding="utf-8")
    other = tmp_path / "other"
    shutil.copytree(source, other)
    result = fetch(script, str(other), destination)
    if result.returncode != 2 or not (destination / "stray.txt").exists():
        raise AssertionError("a destination with a different remote.origin.url was reset")


def test_a_foreign_repository_with_a_forged_marker_and_a_branch_is_refused(
    world: tuple[Path, Path], tmp_path: Path
) -> None:
    script, source = world
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    git(foreign, "init", "-q")
    git(foreign, "commit", "-q", "--allow-empty", "-m", "foreign")
    git(foreign, "remote", "add", "origin", str(source))
    (foreign / ".git/gororoba-math-pin-fetch").write_text("", encoding="utf-8")
    (foreign / "untracked.txt").write_text("keep", encoding="utf-8")
    result = fetch(script, str(source), foreign)
    if result.returncode != 2 or (foreign / "untracked.txt").read_text(encoding="utf-8") != "keep":
        raise AssertionError(result.stderr)
    if not git(foreign, "for-each-ref", "refs/heads"):
        raise AssertionError("the foreign branch vanished")


def test_a_non_empty_directory_that_is_no_repository_is_refused(world: tuple[Path, Path], tmp_path: Path) -> None:
    script, source = world
    destination = tmp_path / "dest"
    destination.mkdir()
    (destination / "file.txt").write_text("keep", encoding="utf-8")
    if fetch(script, str(source), destination).returncode != 2 or not (destination / "file.txt").exists():
        raise AssertionError("a non-empty directory was used")
