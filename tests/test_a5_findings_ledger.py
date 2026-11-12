"""The A_5 exceptional-fiber claim ledger stays well formed: every row passes `ledger.py`'s check."""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

LEDGER_PY = Path(__file__).resolve().parents[1] / "docs/evidence/a5-exceptional-fibers/ledger.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_ledger", LEDGER_PY)
    if spec is None or spec.loader is None:
        raise ImportError(LEDGER_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_ledger_row_passes_the_check() -> None:
    mod = load()
    problems = mod.check(mod.rows())
    if problems:
        raise AssertionError(problems)


def test_a_row_with_a_missing_evidence_path_or_unknown_status_is_reported() -> None:
    mod = load()
    good = mod.rows()[0]
    bad = dict(good, id="A5-999", status="maybe", evidence="docs/no/such/file.md")
    problems = mod.check([good, bad])
    if not any("status 'maybe'" in p for p in problems) or not any("does not exist" in p for p in problems):
        raise AssertionError(problems)


def test_every_a5_evidence_directory_is_cited_and_an_uncited_one_is_reported() -> None:
    mod = load()
    data = mod.rows()
    directories = mod.a5_directories()
    if len(directories) < 15 or mod.uncited_directories(data, directories):
        raise AssertionError((directories, mod.uncited_directories(data, directories)))
    absent = "docs/evidence/a5-kernel"
    if mod.uncited_directories(data, [*directories, absent]) != [absent]:
        raise AssertionError("a directory that only prefixes cited names passes as cited")


def test_a_supersedes_pointer_runs_from_a_live_successor_to_a_superseded_row() -> None:
    mod = load()
    old = dict(mod.rows()[0], id="A5-901", status="superseded", supersedes="")
    live = dict(old, id="A5-902", status="survives", supersedes="A5-901")
    if mod.check([old, live]):
        raise AssertionError(mod.check([old, live]))
    backward = dict(old, supersedes="A5-902")
    problems = mod.check([backward, live])
    if not any("whose status is survives" in p for p in problems):
        raise AssertionError(problems)
    orphan = mod.check([old])
    if not any("no live row names it" in p for p in orphan):
        raise AssertionError(orphan)
    own = mod.check([dict(old, status="survives", supersedes="A5-901")])
    if not any("supersedes itself" in p for p in own):
        raise AssertionError(own)


def test_registry_binds_the_w8_degree_5_engine_stdout_records() -> None:
    claims = json.loads((LEDGER_PY.parent / "claims.json").read_text())
    cells = {
        (f["fiber"], f["prime"]): next(g for g in f["degrees"] if g["d"] == 5)
        for f in claims["fibers"]
        if f["fiber"].startswith("W8")
    }
    if len(cells) != 4:
        raise AssertionError(sorted(cells))
    for key, cell in cells.items():
        if cell["status"] != "certified" or cell["k2_count"] != 4116:
            raise AssertionError((key, cell["status"], cell["k2_count"]))
    sources = {lb["source"] for (fiber, _), cell in cells.items() if fiber == "W8 -> N-" for lb in cell["lower_bounds"]}
    if not sources or not all(s.startswith("w8-n16-azure/") and s.endswith(".out") for s in sources):
        raise AssertionError(sources)


def test_open_lists_rows_with_an_outstanding_falsifier_and_no_decided_row(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = load()
    base = mod.rows()[0]
    data = [
        dict(base, id=f"A5-9{i:02d}", status=status, supersedes="") for i, status in enumerate(sorted(mod.STATUSES))
    ]
    monkeypatch.setattr(mod, "rows", lambda: data)
    monkeypatch.setattr(mod, "check", lambda _rows: [])
    monkeypatch.setattr(sys, "argv", ["ledger.py", "--open"])
    if mod.main() != 0:
        raise AssertionError("ledger.py --open exited nonzero")
    listed = {line.split("\t")[1] for line in capsys.readouterr().out.splitlines() if line}
    if listed != {"survives", "open", "stalled", "boundary"} or listed != mod.OPEN_STATUSES:
        raise AssertionError(listed)
    if {"proved", "refuted", "certified", "rejected", "superseded"} & listed:
        raise AssertionError(listed)
