"""The parallel successors of kcompare.py and qi_reduction_compare.py against a fake Singular.

A fake Singular on PATH answers each regenerated producer script with a canned output built from the retained v2 run
logs, so the successors run their whole pipeline (producer scripts, worker pool, parsing, digest ties, rank analysis,
file writes) without Singular. The first Singular process to start sleeps, so the cell that is first in the list
finishes last and the cell order of the output is the order of the list and not of completion.

Each test runs once on the smallest cell, which the pull-request lane keeps, and once on every cell, which the audit
lane keeps: the three-cell runs take over 10 s on a hosted runner.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence" / "a5-exceptional-fibers"
DIRECTORY = EVIDENCE / "working" / "runs" / "e8-rees-fibers-v2-kcompare-p32009"
RUNS = EVIDENCE / "working" / "runs" / "e8-rees-fibers-v2-p32009"
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(EVIDENCE.parent / "a5-kernel-attachments"))
sys.path.insert(0, str(DIRECTORY))

import kcompare_v2  # noqa: E402
import qi_reduction_compare_v2 as qi_v2  # noqa: E402
import weight_slice_fiber_relations as producer  # noqa: E402

import parallel  # noqa: E402

FAKE = """#!/bin/sh
# argv: -q --no-warn --no-rc SCRIPT; the answer is FAKE_SINGULAR_DIR/<sha256 of SCRIPT>.out
if mkdir "$FAKE_SINGULAR_DIR/first" 2>/dev/null; then sleep "${FAKE_SINGULAR_DELAY:-0}"; fi
digest=$(sha256sum "$4" | cut -d' ' -f1)
[ -f "$FAKE_SINGULAR_DIR/$digest.out" ] || { echo "no canned answer for $digest" >&2; exit 3; }
cat "$FAKE_SINGULAR_DIR/$digest.out"
"""


def _canned(stem: str, generators: int, count: int, relations: list[str] | None = None) -> str:
    """The RESULT and RELATION lines of a producer run whose relations are the REL lines of a retained v2 log."""
    log = (RUNS / f"{stem}.log").read_text(encoding="utf-8")
    lines = relations or ["RELATION" + line[3:] for line in log.split("\n") if line.startswith("REL ")]
    head = [
        "RESULT germ_before 5 2 4",
        "RESULT component 5 2 1",
        "RESULT germ_after 5 2 4",
        "RESULT germ_inhomogeneous 0",
        "RESULT pfaffian_nonzero 84",
        "RESULT pfaffian_max_weight 8",
        "RESULT pfaffian_inhomogeneous",
        f"RESULT generators {generators}",
        "RESULT selected 1,2",
        "RESULT generator_weights 1,1",
        "RESULT products 3 4",
        f"RESULT relations {count}",
        "RESULT done 1",
    ]
    return "\n".join([*head, *lines]) + "\n"


CELL_SETS = [
    pytest.param("iso-nm", id="iso-nm"),
    pytest.param(None, id="all-cells", marks=pytest.mark.audit),
]


def _restrict(module: Any, only: str | None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Limit the module to one cell and that cell's orbit, and drop the start delay of the fake; or leave every cell,
    every orbit and the delay."""
    if only is not None:
        monkeypatch.setattr(module, "CELLS", [cell for cell in module.CELLS if cell[0] == only])
        if hasattr(module, "ORBITS"):
            monkeypatch.setattr(module, "ORBITS", tuple(dict.fromkeys(cell[2] for cell in module.CELLS)))
        monkeypatch.setenv("FAKE_SINGULAR_DELAY", "0")


@pytest.fixture
def fake_singular(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """A Singular on PATH that serves canned answers; the worker pool restarts so its processes inherit the setup."""
    missing = [tool for tool in ("prlimit", "sha256sum") if shutil.which(tool) is None]
    if missing:
        pytest.skip(f"the producer needs prlimit and the fake Singular sha256sum; absent: {', '.join(missing)}")
    binary = tmp_path / "bin"
    answers = tmp_path / "answers"
    binary.mkdir()
    answers.mkdir()
    executable = binary / "Singular"
    executable.write_text(FAKE, encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    parallel._shutdown()
    monkeypatch.setenv("PATH", f"{binary}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("FAKE_SINGULAR_DIR", str(answers))
    monkeypatch.setenv("FAKE_SINGULAR_DELAY", "1.5")
    monkeypatch.setenv("GOROROBA_WORKERS", "3")
    yield answers
    parallel._shutdown()


def _serve(answers: Path, orbit: str, source: str, characteristic: int, root: int, text: str) -> None:
    script = producer.fiber_script(producer.orbit_task(orbit), source, characteristic, root)
    (answers / f"{hashlib.sha256(script.encode('utf-8')).hexdigest()}.out").write_text(text, encoding="utf-8")


def _serve_modular(answers: Path) -> None:
    for _cell, stem, orbit, source, generators, count in kcompare_v2.CELLS:
        _serve(answers, orbit, source, 32009, 10754, _canned(stem, generators, count))


@pytest.mark.parametrize("only", CELL_SETS)
def test_kcompare_successor_writes_the_retained_files_in_cell_order(
    only: str | None,
    fake_singular: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _restrict(kcompare_v2, only, monkeypatch)
    _serve_modular(fake_singular)
    work = tmp_path / "work"
    work.mkdir()
    shutil.copy(DIRECTORY / "kcompare-tail.sing", work / "kcompare-tail.sing")
    monkeypatch.setattr(kcompare_v2, "HERE", work)
    kcompare_v2.prepare()
    names = {cell for cell, *_rest in kcompare_v2.CELLS} | {f"kcmp-{cell}.sing" for cell, *_rest in kcompare_v2.CELLS}
    retained_lines = (DIRECTORY / "prepare.log").read_text(encoding="utf-8").splitlines(keepends=True)
    expected = "".join(line for line in retained_lines if line.split()[1] in names | {"DONE"})
    if capsys.readouterr().out != expected:
        raise AssertionError("the printed lines differ from those of the retained prepare.log")
    for cell, *_rest in kcompare_v2.CELLS:
        for prefix in ("KA", "KH", "kcmp"):
            retained = DIRECTORY / f"{prefix}-{cell}.sing"
            if retained.exists() and (work / retained.name).read_bytes() != retained.read_bytes():
                raise AssertionError(f"{retained.name} differs from the retained file")
    if (work / "KH-iso-nm.sing").exists():
        raise AssertionError("a cell without a header file wrote a KH file")


@pytest.mark.parametrize("only", CELL_SETS)
def test_kcompare_successor_stops_on_a_digest_that_is_not_the_runs(
    only: str | None,
    fake_singular: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _restrict(kcompare_v2, only, monkeypatch)
    _serve_modular(fake_singular)
    spoiled = min(1, len(kcompare_v2.CELLS) - 1)
    cell, stem, orbit, source, generators, count = kcompare_v2.CELLS[spoiled]
    relations = ["RELATION" + line[3:] for line in (RUNS / f"{stem}.log").read_text().split("\n") if line[:4] == "REL "]
    _serve(
        fake_singular,
        orbit,
        source,
        32009,
        10754,
        _canned(stem, generators, count, ["RELATION 1,1:1", *relations[1:]]),
    )
    work = tmp_path / "work"
    work.mkdir()
    shutil.copy(DIRECTORY / "kcompare-tail.sing", work / "kcompare-tail.sing")
    monkeypatch.setattr(kcompare_v2, "HERE", work)
    with pytest.raises(SystemExit) as stopped:
        kcompare_v2.prepare()
    if not str(stopped.value).startswith(f"FAIL {cell}: producer digest"):
        raise AssertionError(stopped.value)
    printed = capsys.readouterr().out.splitlines()
    done = [name for name, *_rest in kcompare_v2.CELLS[:spoiled]]
    expected = [item for name in done for item in (name, f"kcmp-{name}.sing")]
    if [line.split()[1] for line in printed if line.startswith(("TIE", "WROTE"))] != expected:
        raise AssertionError(printed)


def _serve_qi(answers: Path, spoil: str | None = None) -> dict[tuple[str, str], str]:
    """Canned Q(i) answers equal to the modular ones; returns the digest of each cell, which the test patches in."""
    digests: dict[tuple[str, str], str] = {}
    for cell, stem, orbit, source, generators, count in qi_v2.CELLS:
        text = _canned(stem, generators, count)
        _serve(answers, orbit, source, 32009, 10754, text)
        lines = [line for line in text.split("\n") if line.startswith("RELATION ")]
        digests[(orbit, source)] = hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode()).hexdigest()
        if cell == spoil:
            text = _canned(stem, generators, count, ["RELATION 1,1:1", *lines[1:]])
        _serve(answers, orbit, source, 0, 0, text)
    return digests


@pytest.mark.parametrize("only", CELL_SETS)
def test_qi_successor_prints_cells_in_order_with_controls_unequal(
    only: str | None, fake_singular: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _restrict(qi_v2, only, monkeypatch)
    digests = _serve_qi(fake_singular)
    monkeypatch.setattr(qi_v2, "record_digests", lambda: (digests, digests))
    if qi_v2.main() != 0:
        raise AssertionError("the comparison did not finish")
    printed = capsys.readouterr().out.splitlines()
    results = [line for line in printed if line.startswith("QIRED RESULT")]
    expected = [
        f"QIRED RESULT cell {cell} spaces_equal 1 control_drop_qi_unequal 1 control_drop_modular_unequal 1 pass 1"
        for cell, *_ in qi_v2.CELLS
    ]
    if results != expected or printed[-1] != "QIRED ALL DONE":
        raise AssertionError(printed)
    if [line.split()[1] for line in printed if " full " in line] != [cell for cell, *_ in qi_v2.CELLS]:
        raise AssertionError("the full lines are not in cell order")


@pytest.mark.parametrize("only", CELL_SETS)
def test_qi_successor_stops_at_the_cell_whose_relations_are_not_the_records(
    only: str | None, fake_singular: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _restrict(qi_v2, only, monkeypatch)
    names = [cell for cell, *_rest in qi_v2.CELLS]
    spoil = names[min(1, len(names) - 1)]
    digests = _serve_qi(fake_singular, spoil=spoil)
    monkeypatch.setattr(qi_v2, "record_digests", lambda: (digests, digests))
    with pytest.raises(SystemExit) as stopped:
        qi_v2.main()
    if str(stopped.value) != f"FAIL {spoil}: Q(i) digest is not that of the records":
        raise AssertionError(stopped.value)
    printed: list[Any] = [line.split()[1] for line in capsys.readouterr().out.splitlines() if line.startswith("QIRED")]
    position = names.index(spoil)
    if (
        any(printed.count(name) < 4 for name in names[:position])
        or printed.count(spoil) != 1
        or any(name in printed for name in names[position + 1 :])
    ):
        raise AssertionError(printed)
