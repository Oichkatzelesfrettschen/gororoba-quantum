"""repository_archive bundles every ref and accepts a bundle only when it restores."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import repository_archive


def _repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    for args in (
        ["init", "-q", "-b", "main"],
        ["config", "user.email", "t@example.invalid"],
        ["config", "user.name", "t"],
    ):
        subprocess.run(["git", *args], cwd=repo, check=True)
    (repo / "a.txt").write_text("one\n")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "one"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "side"], cwd=repo, check=True)
    subprocess.run(["git", "tag", "v1"], cwd=repo, check=True)
    return repo


def _fails(action: object, fragment: str) -> None:
    with pytest.raises((SystemExit, subprocess.CalledProcessError)) as caught:
        action()  # type: ignore[operator]
    if isinstance(caught.value, SystemExit) and fragment not in str(caught.value):
        raise RuntimeError(f"{caught.value} lacks {fragment!r}")


def test_bundle_restores_and_rejects_every_defect(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path)
    monkeypatch.setattr(repository_archive, "ROOT", repo)
    _fails(lambda: repository_archive.bundle(repo / "inside"), "inside the repository")
    manifest = repository_archive.bundle(tmp_path / "copies")
    path = tmp_path / "copies" / manifest["bundle"]
    if sorted(line.split()[1] for line in manifest["refs"]) != ["refs/heads/main", "refs/heads/side", "refs/tags/v1"]:
        raise RuntimeError(f"bundle refs: {manifest['refs']}")
    if repository_archive.verify(path)["restored_refs"] != 3:
        raise RuntimeError("the restore must recreate every ref")

    original = path.read_bytes()
    path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    _fails(lambda: repository_archive.verify(path), "differs from its manifest")
    path.write_bytes(original)

    manifest_path = path.with_suffix(".json")
    saved = manifest_path.read_text()
    edited = json.loads(saved)
    edited["refs"] = edited["refs"][:-1]
    manifest_path.write_text(json.dumps(edited))
    _fails(lambda: repository_archive.verify(path), "restored refs differ")
    manifest_path.write_text(saved)
    repository_archive.verify(path)


def test_bundle_of_a_detached_historical_head_restores(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _repo(tmp_path)
    first = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True).stdout
    (repo / "a.txt").write_text("two\n")
    subprocess.run(["git", "commit", "-q", "-am", "two"], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "-q", "--detach", first.strip()], cwd=repo, check=True)
    monkeypatch.setattr(repository_archive, "ROOT", repo)
    manifest = repository_archive.bundle(tmp_path / "copies")
    path = tmp_path / "copies" / manifest["bundle"]
    if manifest["head"] != first.strip():
        raise RuntimeError("the manifest records the detached head")
    repository_archive.verify(path)
    edited = dict(manifest, head="0" * 40)
    path.with_suffix(".json").write_text(json.dumps(edited))
    _fails(lambda: repository_archive.verify(path), "lacks head commit")
