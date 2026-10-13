"""Exercise report output admission before retained folded-job evidence is read."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import review_folded_jobs


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def snapshot(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*")
        if path.is_file()
    }


def fixture(directory: Path) -> Path:
    run = directory / "run"
    (run / "raw" / "job").mkdir(parents=True)
    for filename in (
        "record.json",
        "collect.json",
        "isa.qpy",
        "settled-account-usage.json",
        "raw/job/pub_00.json",
        "raw/job/index.json",
        "raw/job/notes.md",
    ):
        (run / filename).write_text(f"retained bytes: {filename}\n")
    return run


def invoke(arguments: list[str]) -> str:
    output = io.StringIO()
    with patch.object(sys, "argv", ["review_folded_jobs.py", *arguments]), contextlib.redirect_stdout(output):
        review_folded_jobs.main()
    return output.getvalue()


def rejected_output(directory: Path, name: str) -> None:
    run = fixture(directory)
    report = directory / "report"
    if name == "record":
        report = run / "record"
    elif name == "raw":
        report = run / "raw" / "job" / "pub_00"
    elif name == "suffix":
        report = run / "record.unused"
    elif name == "traversal":
        (directory / "outside").mkdir()
        report = directory / "outside" / ".." / "run" / "record"
    elif name == "run_symlink":
        (directory / "run_alias").symlink_to(run, target_is_directory=True)
        run = directory / "run_alias"
        report = directory / "run" / "record"
    elif name == "parent_symlink":
        (directory / "alias").symlink_to(run / "raw" / "job", target_is_directory=True)
        report = directory / "alias" / "pub_00"
    elif name == "new_leaf":
        report = run / "new" / "report"
    elif name in {"json_symlink", "markdown_symlink", "dangling_symlink"}:
        suffix = ".md" if name == "markdown_symlink" else ".json"
        target = run / ("missing.json" if name == "dangling_symlink" else "record.json")
        report.with_suffix(suffix).symlink_to(target)
    elif name in {"pair_symlink", "pair_dangling_symlink", "pair_hardlink"}:
        markdown_path = report.with_suffix(".md")
        if name != "pair_dangling_symlink":
            markdown_path.write_text("existing report bytes\n")
        if name == "pair_hardlink":
            report.with_suffix(".json").hardlink_to(markdown_path)
        else:
            report.with_suffix(".json").symlink_to(markdown_path)
    elif name in {"json_hardlink", "markdown_hardlink", "qpy_hardlink", "raw_hardlink", "linked_raw_hardlink"}:
        suffix = ".md" if name == "markdown_hardlink" else ".json"
        retained_name = {"qpy_hardlink": "isa.qpy", "raw_hardlink": "raw/job/pub_00.json"}.get(name, "record.json")
        if name == "linked_raw_hardlink":
            external_job = directory / "external_job"
            external_job.mkdir()
            (external_job / "pub_00.json").write_text("retained external shot bytes\n")
            (run / "raw" / "linked_job").symlink_to(external_job, target_is_directory=True)
            retained_name = "raw/linked_job/pub_00.json"
        report.with_suffix(suffix).hardlink_to(run / retained_name)
    else:
        raise RuntimeError(f"Unknown rejection case: {name}")
    before = snapshot(directory)
    arguments = ["--run-dir", str(run), "--out", str(report)]
    for mode in ([], ["--check"]):
        with patch.object(review_folded_jobs, "audit", side_effect=RuntimeError("Audit ran before admission")):
            try:
                invoke([*arguments, *mode])
            except ValueError as error:
                require("Report output" in str(error), f"{name}: unexpected error: {error}")
            else:
                raise RuntimeError(f"{name}: unsafe output was accepted")
        require(snapshot(directory) == before, f"{name}: rejected output changed fixture bytes")
    result = subprocess.run(
        [sys.executable, "-B", str(Path(review_folded_jobs.__file__).resolve()), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    require(result.returncode != 0 and "Report output" in result.stderr, f"{name}: CLI admission failed")
    require(snapshot(directory) == before, f"{name}: CLI rejection changed fixture bytes")


def accepted_output(directory: Path) -> None:
    run = fixture(directory)
    before = snapshot(run)
    report = {"fixture": "folded-job audit"}
    markdown = "# Folded-job audit\n"
    stem = Path("results/ripple/folded-job-review")
    run_argument = ["--run-dir", str(run)]
    with contextlib.chdir(directory), patch.object(review_folded_jobs, "audit", return_value=(report, markdown)):
        require("wrote JSON and Markdown" in invoke(run_argument), "Default output did not write the pair")
        require(stem.with_suffix(".json").read_text() == json.dumps(report, indent=2) + "\n", "JSON differs")
        require(stem.with_suffix(".md").read_text() == markdown, "Markdown differs")
        retained_pair = {
            path: (path.read_bytes(), path.stat().st_mtime_ns)
            for path in (stem.with_suffix(".json"), stem.with_suffix(".md"))
        }
        require("retained outputs match" in invoke([*run_argument, "--check"]), "Check mode did not compare")
        for path, identity in retained_pair.items():
            require((path.read_bytes(), path.stat().st_mtime_ns) == identity, "Check mode wrote a report")
        stem.with_suffix(".md").write_text("different\n")
        before_difference = snapshot(directory)
        try:
            invoke([*run_argument, "--check"])
        except ValueError as error:
            require("Retained audit differs" in str(error), f"Unexpected check failure: {error}")
        else:
            raise RuntimeError("Check mode accepted changed output")
        require(snapshot(directory) == before_difference, "Failed check mode changed files")
    require(snapshot(run) == before, "Supported output changed retained run evidence")


def main() -> None:
    cases = (
        "record",
        "raw",
        "suffix",
        "traversal",
        "run_symlink",
        "parent_symlink",
        "new_leaf",
        "json_symlink",
        "markdown_symlink",
        "dangling_symlink",
        "json_hardlink",
        "markdown_hardlink",
        "qpy_hardlink",
        "raw_hardlink",
        "linked_raw_hardlink",
        "pair_symlink",
        "pair_dangling_symlink",
        "pair_hardlink",
    )
    with tempfile.TemporaryDirectory(prefix="folded-review-output-check-") as temporary:
        directory = Path(temporary)
        for name in cases:
            rejected_output(directory / name, name)
        accepted_output(directory / "accepted")
    print(f"Folded-job output admission: {len(cases)} rejected paths preserve fixture bytes; write/check modes pass")


if __name__ == "__main__":
    main()
