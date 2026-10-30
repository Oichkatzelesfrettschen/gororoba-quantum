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


def test_a_campaign_binds_its_sources_as_dependency_rows(repo: tuple[Path, str]) -> None:
    root, _ = repo
    digest = hashlib.sha256(b"frozen\n").hexdigest()
    (root / "campaign.json").write_text(
        json.dumps({"dependencies": [{"file": "shared.py", "sha256": digest}]}), encoding="utf-8"
    )
    revision = commit(root, "campaign")
    (root / "shared.py").write_text("moved on\n", encoding="utf-8")
    commit(root, "main moves")
    if pin.check_case("campaign.json", revision)["changed_on_head"] != ["shared.py"]:
        raise AssertionError("a pinned campaign must report main's drift of its dependency")
    with pytest.raises(ValueError, match="analysis_sources or as dependencies rows"):
        pin.bound_sources({"dependencies": [{"file": "shared.py"}]})


def test_a_pinned_command_runs_at_the_revision_and_leaves_no_worktree(repo: tuple[Path, str], tmp_path: Path) -> None:
    root, revision = repo
    (root / "pins.json").write_text(
        json.dumps({"schema": pin.SCHEMA, "cases": [{"case": "cases.json", "revision": revision}]}), encoding="utf-8"
    )
    commit(root, "pin")
    (root / "shared.py").write_text("moved on\n", encoding="utf-8")
    commit(root, "main moves")
    result = pin.run_at_pin(root / "pins.json", "cases.json", ["cat", "shared.py"], tmp_path / "pinned")
    if result.stdout != "frozen\n" or (tmp_path / "pinned").exists():
        raise AssertionError("the command must read the pinned bytes and the worktree must be removed")
