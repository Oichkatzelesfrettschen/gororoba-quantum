"""The split, persisted quotient export of fiber-rank engine v9 against the serial export of engine v8."""

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "docs" / "evidence" / "a5-exceptional-fibers" / "replay" / "engine")
)

import fiber_rank_v8 as v8  # noqa: E402
import fiber_rank_v9 as v9  # noqa: E402

P = 32009
NAMES = ["t1", "t2", "t3"]
HEADER = {"J": "t1^2-t2*t3,t2^3-t1*t3^2", "G": "t1+t2^2,t2-t3,t3^2"}
SINGULAR = shutil.which("Singular")
needs_singular = pytest.mark.skipif(SINGULAR is None, reason="Singular is not installed")


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _serial(tmp: Path) -> tuple:
    """Engine v8's serial export script, run once and parsed with the shared reader."""
    tmp.mkdir()
    script = v8.QUOTIENT_SCRIPT.format(p=P, names=",".join(NAMES), J=HEADER["J"], G=HEADER["G"], N=6, d=2, out=tmp)
    v9.run_singular((str(SINGULAR), script, str(tmp / "q.sing"), str(tmp / "qG.txt"), str(tmp / "qG.txt")))
    basis = [next(iter(q)) for q in v9.read_list(str(tmp / "qB.txt"), NAMES, P)]
    tables = [v9.read_list(str(tmp / f"qM{k}.txt"), NAMES, P) for k in range(1, len(NAMES) + 1)]
    return basis, tables, v9.read_list(str(tmp / "qG.txt"), NAMES, P)


def test_manifest_mismatch_refuses(tmp_path: Path) -> None:
    (tmp_path / v9.EXPORT_MANIFEST).write_text(json.dumps({**v9.export_identity(HEADER, NAMES, P, 6), "N": 7}))
    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, "Singular", str(tmp_path))


def test_unmanifested_files_need_adoption(tmp_path: Path) -> None:
    (tmp_path / "qB.txt").write_text("1")
    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, "Singular", str(tmp_path))


def test_adoption_checks_the_serial_script(tmp_path: Path) -> None:
    script = v8.QUOTIENT_SCRIPT.format(p=P, names=",".join(NAMES), J=HEADER["J"], G=HEADER["G"], N=6, d=2, out="x")
    (tmp_path / "q.sing").write_text(script)
    v9.adopt_serial_export(str(tmp_path), HEADER, NAMES, P, 6)
    with pytest.raises(SystemExit):
        v9.adopt_serial_export(str(tmp_path), HEADER, NAMES, P, 7)


@needs_singular
@pytest.mark.parametrize("chunks", [1, 3])
def test_split_export_equals_serial(tmp_path: Path, chunks: int) -> None:
    serial = _serial(tmp_path / "serial")
    out = tmp_path / "split"
    split = v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out), chunks=chunks)
    _check(split[:3] == serial)
    again = v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out), chunks=chunks)
    _check(again[:3] == serial and not again[3]["computed_seconds"])


@needs_singular
def test_adopted_partial_export_completes(tmp_path: Path) -> None:
    serial = _serial(tmp_path / "serial")
    adopted = tmp_path / "adopted"
    adopted.mkdir()
    for name in ("q.sing", "qB.txt", "qM1.txt"):
        shutil.copy(tmp_path / "serial" / name, adopted / name)
    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted))
    split = v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted), adopt=True)
    _check(split[:3] == serial)
    _check("qM1.txt" in split[3]["reused"] and "qM1.txt" not in split[3]["computed_seconds"])


def test_flags_need_quotient(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    header = tmp_path / "h.sing"
    header.write_text(f"ring r={P},({','.join(NAMES)}),dp;\nideal J={HEADER['J']};\nideal G={HEADER['G']};\n")
    monkeypatch.setattr(sys, "argv", ["v9", str(header), "2", "6", "--export-chunks", "2"])
    with pytest.raises(SystemExit):
        v9.main()
