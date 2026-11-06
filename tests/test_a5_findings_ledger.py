"""The A_5 exceptional-fiber claim ledger stays well formed: every row passes `ledger.py`'s check."""

import importlib.util
from pathlib import Path
from types import ModuleType

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
