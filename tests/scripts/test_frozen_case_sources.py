"""A source pin holds while main changes a bound file and fails when the case or its pinned sources change."""

import hashlib
import json
import subprocess
from pathlib import Path

import frozen_case_sources as pin
import pytest


def commit(root: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", message], check=True
    )
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str]:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "shared.py").write_text("frozen\n", encoding="utf-8")
    digest = hashlib.sha256(b"frozen\n").hexdigest()
    (tmp_path / "cases.json").write_text(json.dumps({"analysis_sources": {"shared.py": digest}}), encoding="utf-8")
    revision = commit(tmp_path, "freeze")
    monkeypatch.setattr(pin, "ROOT", tmp_path)
    return tmp_path, revision


def test_main_may_change_a_bound_file_after_the_pin(repo: tuple[Path, str]) -> None:
    root, revision = repo
    (root / "shared.py").write_text("evolved\n", encoding="utf-8")
    commit(root, "evolve")
    if pin.check_case("cases.json", revision)["changed_on_head"] != ["shared.py"]:
        raise AssertionError("the pin did not report main's change to the bound file")


def test_a_changed_case_breaks_the_pin(repo: tuple[Path, str]) -> None:
    root, revision = repo
    (root / "cases.json").write_text("{}", encoding="utf-8")
    commit(root, "rewrite")
    with pytest.raises(ValueError, match="case bytes differ"):
        pin.check_case("cases.json", revision)


def test_a_revision_without_the_bound_bytes_breaks_the_pin(repo: tuple[Path, str]) -> None:
    root, _ = repo
    (root / "shared.py").write_text("evolved\n", encoding="utf-8")
    later = commit(root, "evolve")
    with pytest.raises(ValueError, match="does not have the bound sha256"):
        pin.check_case("cases.json", later)


def test_every_bound_case_under_a_scope_is_found(repo: tuple[Path, str]) -> None:
    root, _ = repo
    (root / "cases" / "unbound").mkdir(parents=True)
    (root / "cases" / "unbound" / "cases.json").write_text("{}", encoding="utf-8")
    (root / "cases" / "bound").mkdir()
    (root / "cases" / "bound" / "cases.json").write_text('{"analysis_sources": {}}', encoding="utf-8")
    if pin.bound_cases([Path("cases")]) != ["cases/bound/cases.json"]:
        raise AssertionError("the scope scan missed a bound case or admitted an unbound one")
