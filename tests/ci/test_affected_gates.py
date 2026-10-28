"""The pull-request gates lane selects every gate a diff reaches and leaves the rest to the audit."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import gate_inputs
import pytest
import run_gates

PRODUCER = """import hashlib
import json
import sys
from pathlib import Path

import helper

record = json.loads((Path(sys.argv[1]) / "proposal.json").read_text())
if record["source_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
    raise SystemExit("record differs; retain a separately named successor")
"""


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """A checkout whose proposal record binds its producer's digest, plus one unrelated gate."""
    (tmp_path / "ci").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "results/proposal").mkdir(parents=True)
    (tmp_path / "scripts/producer.py").write_text(PRODUCER)
    (tmp_path / "scripts/helper.py").write_text("VALUE = 1\n")
    (tmp_path / "scripts/other.py").write_text("print('other')\n")
    (tmp_path / "results/proposal/proposal.json").write_text("{}\n")
    gates = [
        {"name": "proposal", "cwd": ".", "cmd": '"$PYTHON" scripts/producer.py results/proposal'},
        {"name": "other", "cwd": ".", "cmd": '"$PYTHON" scripts/other.py'},
        {"name": "scoped", "cwd": ".", "cmd": '"$PYTHON" scripts/other.py --full', "tier": "full"},
    ]
    (tmp_path / "ci/gates.json").write_text(json.dumps({"gates": gates}))
    (tmp_path / "ci/full_gate_inputs.json").write_text(json.dumps({"gates": {"scoped": ["data/**"]}}))
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


def reached(root: Path, changed: list[str], listed: list[str] = [], traced: Any = None) -> set[str]:  # noqa: B006
    gates = json.loads((root / "ci/gates.json").read_text())["gates"]
    return gate_inputs.affected(root, gates, changed, listed, traced)


@pytest.mark.parametrize(
    ("changed", "expected"),
    [
        # An edit of the producer that a retained record binds reaches the record's check.
        (["scripts/producer.py"], {"proposal"}),
        # So does an edit of a module the producer imports.
        (["scripts/helper.py"], {"proposal"}),
        # The record and its directory are command operands.
        (["results/proposal/proposal.json"], {"proposal"}),
        (["results/proposal/batch-00/witness.cq"], {"proposal"}),
        (["data/table.csv"], {"scoped"}),
        (["docs/unrelated.md"], set()),
    ],
)
def test_a_change_reaches_the_gates_that_check_it(tree: Path, changed: list[str], expected: set[str]) -> None:
    if reached(tree, changed) != expected:
        raise AssertionError(f"{changed} reached {reached(tree, changed)}, expected {expected}")


def test_a_name_imported_from_a_module_is_no_module(tree: Path) -> None:
    (tree / "scripts/helper.py").write_text("import leaf\nfrom leaf import collect\n")
    (tree / "scripts/leaf.py").write_text("def collect() -> None: ...\n")
    (tree / "evidence").mkdir()
    (tree / "evidence/collect.py").write_text("")
    if reached(tree, ["evidence/collect.py"]):
        raise AssertionError("a function imported from a module must not match a file of the same stem")
    if reached(tree, ["scripts/leaf.py"]) != {"proposal"}:
        raise AssertionError("the imported module itself stays a dependency")


@pytest.mark.parametrize("statement", ["from pkg import sub", "from . import sub"])
def test_a_name_imported_from_a_package_or_relatively_is_a_submodule(tree: Path, statement: str) -> None:
    (tree / "scripts/helper.py").write_text(f"{statement}\n")
    (tree / "scripts/pkg").mkdir()
    (tree / "scripts/pkg/__init__.py").write_text("")
    (tree / "scripts/pkg/sub.py").write_text("")
    if reached(tree, ["scripts/pkg/sub.py"]) != {"proposal"}:
        raise AssertionError(f"{statement!r} names a submodule, which must stay a dependency")


@pytest.mark.parametrize("pin", ["requirements.txt", "ci/requirements-replay.txt", "ci/patches/fix.patch"])
def test_a_runtime_pin_change_reaches_every_gate(tree: Path, pin: str) -> None:
    if reached(tree, [pin]) != {"proposal", "other", "scoped"}:
        raise AssertionError(f"{pin} must reach every gate, since it changes their interpreter")


def test_a_new_or_changed_manifest_entry_reaches_its_gate(tree: Path) -> None:
    gates = json.loads((tree / "ci/gates.json").read_text())["gates"]
    base = [dict(gate, cmd=gate["cmd"] + " --old") if gate["name"] == "other" else gate for gate in gates]
    base = [gate for gate in base if gate["name"] != "scoped"]
    if gate_inputs.affected(tree, gates, ["ci/gates.json"], [], None, base) != {"other", "scoped"}:
        raise AssertionError("a changed command and a new gate must each be reached")
    if gate_inputs.affected(tree, gates, ["ci/gates.json"], [], None, gates):
        raise AssertionError("an unchanged manifest reaches no gate")


def test_a_checksum_manifest_binds_each_listed_file(tree: Path) -> None:
    (tree / "proofs").mkdir()
    (tree / "proofs/Witness.v").write_text("Lemma w : True.\n")
    (tree / "results/sums").mkdir()
    (tree / "results/sums/SHA256SUMS").write_text(f"{'0' * 64}  ../../proofs/Witness.v\n{'1' * 64} *local.bin\n")
    gates = json.loads((tree / "ci/gates.json").read_text())["gates"]
    gates.append({"name": "sums", "cwd": "results/sums", "cmd": "sha256sum -c SHA256SUMS"})
    for changed in (["proofs/Witness.v"], ["results/sums/local.bin"]):
        if gate_inputs.affected(tree, gates, changed, []) != {"sums"}:
            raise AssertionError(f"{changed} is bound by the checksum manifest and must reach its gate")


def test_a_traced_read_set_reaches_an_unnamed_input(tree: Path) -> None:
    reads = {
        "files": ["docs/catalogue.json"],
        "dirs": ["docs/runs"],
        "globs": [[0, "docs/cases/*.json"]],
        "stats": [[0, "docs/marker"]],
        "links": [],
    }
    traced = {"other": {"key": "k", "reads": reads}}
    cases = [
        (["docs/catalogue.json"], [], True),
        (["docs/marker"], ["docs/marker"], True),
        # An added or removed entry changes a listing or a glob; an edit inside does not.
        (["docs/runs/run-2.json"], ["docs/runs/run-2.json"], True),
        (["docs/runs/run-1.json"], [], False),
        (["docs/cases/new.json"], ["docs/cases/new.json"], True),
        # A new module reaches its importers through the import closure, never through a listing.
        (["docs/runs/tool.py"], ["docs/runs/tool.py"], False),
    ]
    for changed, listed, expected in cases:
        if ("other" in reached(tree, changed, listed, traced)) is not expected:
            raise AssertionError(f"{changed} added {listed}: expected reach {expected}")
    if "other" not in reached(tree, ["docs/catalogue.json"], [], {"other--case": {"key": "k", "reads": reads}}):
        raise AssertionError("a case entry's read set must reach its parent gate")


def test_an_added_directory_changes_its_parent_listing(tree: Path) -> None:
    reads = {"files": [], "dirs": ["docs/runs"], "globs": [], "stats": [], "links": []}
    traced = {"other": {"key": "k", "reads": reads}}
    gates = json.loads((tree / "ci/gates.json").read_text())["gates"]
    (tree / "docs/runs/old").mkdir(parents=True)
    (tree / "docs/runs/new").mkdir()
    (tree / "docs/runs/new/cases.json").write_text("{}\n")
    (tree / "docs/runs/old/extra.json").write_text("{}\n")
    before = {"docs/runs/old/cases.json"}
    # Git lists docs/runs/new/cases.json; the entry docs/runs gains is docs/runs/new.
    added = ["docs/runs/new/cases.json"]
    if "other" not in gate_inputs.affected(tree, gates, added, added, traced, None, before):
        raise AssertionError("a new directory under a listed directory must reach the gate that listed it")
    # A file added inside a directory that already existed changes only that directory's listing.
    added = ["docs/runs/old/extra.json"]
    if "other" in gate_inputs.affected(tree, gates, added, added, traced, None, before):
        raise AssertionError("an addition below an existing entry leaves the listed directory unchanged")
    # A removed directory leaves its parent's listing too.
    removed = ["docs/runs/gone/cases.json"]
    if "other" not in gate_inputs.affected(tree, gates, removed, removed, traced, None, before | set(removed)):
        raise AssertionError("a removed directory under a listed directory must reach the gate that listed it")


def test_name_status_separates_added_and_removed_paths() -> None:
    diff = b"M\0scripts/a.py\0A\0results/new.json\0D\0results/old.json\0"
    if run_gates.name_status(diff) != (
        ["scripts/a.py", "results/new.json", "results/old.json"],
        ["results/new.json", "results/old.json"],
    ):
        raise AssertionError("name-status pairs misparsed")
    with pytest.raises(SystemExit, match="--no-renames"):
        run_gates.name_status(b"R100\0old.py\0")
    with pytest.raises(SystemExit, match="status and path pairs"):
        run_gates.name_status(b"M\0")
