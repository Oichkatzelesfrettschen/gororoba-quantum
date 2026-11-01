"""Contract for ci/check_rocq_ci_pins.py: the repository passes its own check, and each mutation of a
pin, a toolchain banner, a trigger's path list, the workflow, the replay driver or the gate exclusions fails it.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from check_rocq_ci_pins import FIXED_FILES, ROOT, WORKFLOW, bundles, check, read_pin


def checked_files() -> list[str]:
    files = list(FIXED_FILES)
    for name in bundles(ROOT):
        files += [f"docs/evidence/{name}/{leaf}" for leaf in ("toolchain.txt", "replay_rocq.sh")]
        if (ROOT / f"docs/evidence/{name}/source_hashes.sha256").exists():
            files.append(f"docs/evidence/{name}/source_hashes.sha256")
    return files


def mutations() -> list[tuple[str, str, str]]:
    names = bundles(ROOT)
    workflow = (ROOT / WORKFLOW).read_text(encoding="utf-8")
    some_crate = next(line.strip() for line in workflow.splitlines() if line.strip().startswith("crates/"))
    pin = read_pin(ROOT)
    core_package = next(package for package in pin["packages"].split() if package.startswith("rocq-core."))
    core_version = core_package.split(".", 1)[1]
    edits = {
        "ci/rocq_toolchain.pin": [
            (pin["compiler"], "ocaml-base-compiler.0.0.0"),
            (core_package, "rocq-core.0.0.0"),
            (f"switch={pin['switch']}", f"switch={pin['switch']}-altered"),
            (f"opam_repository={pin['opam_repository']}", "opam_repository=z" + pin["opam_repository"][1:]),
        ],
        "ci/open_gororoba.pin": [("7", "x")],
        f"docs/evidence/{names[0]}/toolchain.txt": [(core_version, "0.0.0")],
        WORKFLOW: [
            ("command -v rg", "command -v grep"),
            ("formal_certificates ", ""),
            (some_crate, "crates/elsewhere"),
            # Both events list the path, so the first occurrence is the pull_request list.
            ("      - docs/evidence/stiefel_witness/**\n", ""),
            # folding_proofs/** holds proofs/** as a substring, so only a whole-pattern match rejects this.
            ("      - proofs/**\n", "      - proof/**\n"),
            # The push list is checked apart from the pull_request list.
            ("branches: [main]\n    paths:\n      - proofs/**\n", "branches: [main]\n    paths:\n      - proof/**\n"),
        ],
        "scripts/rocq_kaggle_replay.py": [(f'"{pin["compiler"]}"', '"ocaml-base-compiler.0.0.0"')],
        "ci/gates.json": [("the proofs.yml job rocq on proof paths", "a manual step on proof paths")],
    }
    return [(target, old, new) for target, pairs in edits.items() for old, new in pairs]


def test_repository_passes() -> None:
    if errors := check(ROOT):
        raise AssertionError("the repository fails its own check:\n" + "\n".join(errors))


@pytest.mark.parametrize(("target", "old", "new"), mutations())
def test_mutation_fails_the_check(tmp_path: Path, target: str, old: str, new: str) -> None:
    for rel in checked_files():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, tmp_path / rel)
    text = (tmp_path / target).read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"mutation {old!r} is absent from {target}")
    (tmp_path / target).write_text(text.replace(old, new, 1), encoding="utf-8")
    if not check(tmp_path):
        raise AssertionError(f"mutation {old!r} -> {new!r} in {target} passed the check")
