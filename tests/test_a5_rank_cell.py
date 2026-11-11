# ruff: noqa: S101
"""Atomic fiber-rank cell publication and validation."""

from __future__ import annotations

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path

import pytest

RUNNER = Path(__file__).parents[1] / "docs/evidence/a5-exceptional-fibers/replay/engine/rank_cell.py"
SPEC = importlib.util.spec_from_file_location("a5_rank_cell_test", RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {RUNNER}")
rank_cell = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rank_cell
SPEC.loader.exec_module(rank_cell)


def _engine(path: Path, exit_code: int = 0) -> None:
    path.write_text(
        """import hashlib,json,sys
from pathlib import Path
engine,header,d,N=Path(sys.argv[0]),Path(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
p=int(header.read_text().split('ring r=',1)[1].split(',',1)[0])
print(json.dumps({'check':'fiber-rank-linear-algebra','engine_sha256_16':hashlib.sha256(engine.read_bytes()).hexdigest()[:16],
'header_sha256_16':hashlib.sha256(header.read_bytes()).hexdigest()[:16],'prime':p,'d':d,'N':N,'r_N':7}))
raise SystemExit(EXIT)
""".replace("EXIT", str(exit_code))
    )


def _args(tmp_path: Path, engine: Path, output: Path) -> Namespace:
    header = tmp_path / "header.sing"
    header.write_text("ring r=32009,(x),dp; ideal J=x; ideal G=x;\n")
    return Namespace(
        engine=str(engine),
        header=str(header),
        degree=2,
        order=7,
        output=str(output),
        python=sys.executable,
        poll_seconds=0.01,
        engine_args=[],
    )


def test_success_publishes_and_validates_existing_record(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    assert rank_cell.run_cell(args) == 0
    assert output.exists() and not output.with_suffix(".json.part").exists()
    assert output.with_suffix(".resources.json").exists()
    assert rank_cell.run_cell(args) == 0


def test_failure_keeps_partial_record_and_propagates_status(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine, 9)
    assert rank_cell.run_cell(_args(tmp_path, engine, output)) == 9
    assert not output.exists() and output.with_suffix(".json.part").exists()


def test_nonempty_stale_record_is_not_skipped(tmp_path: Path) -> None:
    engine, output = tmp_path / "engine.py", tmp_path / "cell.json"
    _engine(engine)
    args = _args(tmp_path, engine, output)
    output.write_text("{}\n")
    with pytest.raises(ValueError, match="identity mismatch"):
        rank_cell.run_cell(args)
