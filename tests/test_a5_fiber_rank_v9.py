"""The split, persisted quotient export of fiber-rank engine v9 against the serial export of engine v8."""

import fcntl
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
    tmp.mkdir(parents=True)
    script = v8.QUOTIENT_SCRIPT.format(p=P, names=",".join(NAMES), J=HEADER["J"], G=HEADER["G"], N=6, d=2, out=tmp)
    v9.run_singular(v9.Step(str(SINGULAR), script, str(tmp / "q.sing"), str(tmp / "qG.txt"), None, "RESULT quotient"))
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
    adopted.mkdir(parents=True)
    for name in ("q.sing", "qB.txt", "qM1.txt"):
        shutil.copy(tmp_path / "serial" / name, adopted / name)
    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted))
    split = v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted), adopt=True)
    _check(split[:3] == serial)
    _check("qM1.txt" in split[3]["reused"] and "qM1.txt" not in split[3]["computed_seconds"])


def _adopted(tmp_path: Path, basis: str | None = None, table: str | None = None) -> Path:
    """A directory holding a v8 script, its basis and first table, optionally with the basis or table replaced."""
    _serial(tmp_path / "serial")
    adopted = tmp_path / "adopted"
    adopted.mkdir(parents=True)
    for name in ("q.sing", "qB.txt", "qM1.txt"):
        shutil.copy(tmp_path / "serial" / name, adopted / name)
    if basis is not None:
        (adopted / "qB.txt").write_text(basis)
    if table is not None:
        (adopted / "qM1.txt").write_text(table)
    return adopted


def _entries(path: Path) -> list[str]:
    return path.read_text().replace("\n", "").split(",")


@needs_singular
def test_basis_mismatch_refuses_every_retry(tmp_path: Path) -> None:
    entries = _entries(_adopted(tmp_path / "probe") / "qB.txt")
    entries[0], entries[1] = entries[1], entries[0]
    adopted = _adopted(tmp_path / "run", basis=",".join(entries))
    for _ in range(2):
        with pytest.raises(SystemExit):
            v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted), adopt=True)
    _check((adopted / "qB.rejected.txt").exists() and not (adopted / "s.txt").exists())


@needs_singular
def test_permuted_adopted_table_fails_its_spot_rows(tmp_path: Path) -> None:
    entries = _entries(_adopted(tmp_path / "probe") / "qM1.txt")
    adopted = _adopted(tmp_path / "run", table=",".join(reversed(entries)))
    for _ in range(2):
        with pytest.raises(SystemExit, match="recomputed rows"):
            v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted), adopt=True)


@needs_singular
def test_chunk_parts_with_other_bounds_are_ignored(tmp_path: Path) -> None:
    serial = _serial(tmp_path / "serial")
    D = len(serial[0])
    out = tmp_path / "split"
    out.mkdir()
    stale = out / f"qM1.r1-{D // 3}.txt"
    stale.write_text(",".join(["0"] * (D // 3)))
    ident = v9.identity_sha256(v9.export_identity(HEADER, NAMES, P, 6))
    (out / (stale.name + ".sha256")).write_text(f"{v9.file_sha256(str(stale))} {ident}")
    split = v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out), chunks=4)
    _check(split[:3] == serial)


@needs_singular
def test_records_survive_an_interrupted_run(tmp_path: Path) -> None:
    out = tmp_path / "split"
    v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out))

    def refuse(_basis: list) -> None:
        raise SystemExit("preflight")

    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out), preflight=refuse)
    _check("qM2.txt" in json.loads((out / v9.EXPORT_MANIFEST).read_text())["files"])
    table = out / "qM2.txt"
    table.write_text(table.read_text().replace("1", "2", 1))
    with pytest.raises(SystemExit):
        v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(out))


@needs_singular
def test_kbase_order_and_indented_errors_block_publication(tmp_path: Path) -> None:
    (tmp_path / "qB.txt").write_text("1,x")
    ring = 'ring r=32009,(x),dp; ideal B=x,1; short=0; write(":w {f}",B);'
    swapped = v9.Step(str(SINGULAR), ring.format(f=tmp_path / "b") + ring.format(f=tmp_path / "o") + '"RESULT t";',
                      str(tmp_path / "s1.sing"), str(tmp_path / "o"), str(tmp_path / "out"), "RESULT t",
                      str(tmp_path / "b"), str(tmp_path / "qB.txt"))  # fmt: skip
    with pytest.raises(RuntimeError):
        v9.run_singular(swapped)
    broken = v9.Step(str(SINGULAR), ring.format(f=tmp_path / "o") + 'missing_name;"RESULT t";',
                     str(tmp_path / "s2.sing"), str(tmp_path / "o"), str(tmp_path / "out"), "RESULT t")  # fmt: skip
    with pytest.raises(RuntimeError):
        v9.run_singular(broken)
    _check(not (tmp_path / "out").exists())


def test_sidecar_from_another_export_refuses(tmp_path: Path) -> None:
    (tmp_path / "qB.txt").write_text("1")
    other = v9.identity_sha256(v9.export_identity(HEADER, NAMES, P, 7))
    (tmp_path / "qB.txt.sha256").write_text(f"{v9.file_sha256(str(tmp_path / 'qB.txt'))} {other}")
    with pytest.raises(SystemExit, match="another header"):
        v9.quotient_data(HEADER, NAMES, P, 6, "Singular", str(tmp_path), adopt=True)


@needs_singular
def test_adoption_refuses_unrecorded_row_ranges(tmp_path: Path) -> None:
    adopted = _adopted(tmp_path)
    (adopted / "qM2.r1-1.txt").write_text("0")
    with pytest.raises(SystemExit, match="row-range"):
        v9.quotient_data(HEADER, NAMES, P, 6, str(SINGULAR), str(adopted), adopt=True)


def test_failed_step_returns_instead_of_raising(tmp_path: Path) -> None:
    step = v9.Step(str(tmp_path / "no-singular"), "", str(tmp_path / "s.sing"), str(tmp_path / "o"), None, "RESULT t")
    name, _, error = v9.run_step(step)
    _check(name == "o" and error is not None)


@pytest.mark.parametrize("mode", [fcntl.LOCK_EX, fcntl.LOCK_SH])
def test_one_writer_per_export_dir(tmp_path: Path, mode: int) -> None:
    """An exclusive holder (a running coordinator) or a shared holder (a step outliving its coordinator) refuses."""
    with open(tmp_path / ".lock", "a") as lock:
        fcntl.flock(lock, mode | fcntl.LOCK_NB)
        with pytest.raises(SystemExit, match="another process holds"):
            v9.quotient_data(HEADER, NAMES, P, 6, "Singular", str(tmp_path))


def test_flags_need_quotient(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    header = tmp_path / "h.sing"
    header.write_text(f"ring r={P},({','.join(NAMES)}),dp;\nideal J={HEADER['J']};\nideal G={HEADER['G']};\n")
    for extra in (["--export-chunks", "2"], ["--quotient", "--export-only"]):
        monkeypatch.setattr(sys, "argv", ["v9", str(header), "2", "6", *extra])
        with pytest.raises(SystemExit):
            v9.main()
