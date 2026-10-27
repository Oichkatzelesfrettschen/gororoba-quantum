"""scripts/kaggle_run.py dataset: the record lands in its own file and every archived input keeps its bytes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts")]

import kaggle_run  # noqa: E402


def test_dataset_record_leaves_its_inputs_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "data").mkdir(parents=True)
    inputs = {"data/first.json": b'{"a": 1}\n', "data/second.json": b'{"b": 2}\n'}
    for name, content in inputs.items():
        (repo / name).write_bytes(content)
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "inputs"], check=True)
    real_run = subprocess.run

    def run(command: list[str], *args: Any, **kwargs: Any) -> Any:
        if command[:2] == ["kaggle", "datasets"]:
            return subprocess.CompletedProcess(command, 1, "", "")
        return real_run(command, *args, **kwargs)

    records = tmp_path / "datasets"
    with (
        patch.object(kaggle_run, "ROOT", repo),
        patch.object(kaggle_run, "DATASETS", records),
        patch.object(kaggle_run, "username", lambda: "owner"),
        patch.object(kaggle_run, "kaggle", lambda *_: "Upload successful"),
        patch.object(kaggle_run.subprocess, "run", run),
    ):
        kaggle_run.dataset(argparse.Namespace(slug="probe", include=list(inputs)))
    for name, content in inputs.items():
        if (repo / name).read_bytes() != content:
            raise AssertionError(f"dataset rewrote its input {name}")
    if not (records / "probe.json").is_file():
        raise AssertionError("the dataset record is missing from its own path")
