"""Write open_gororoba's git-ignored data/csv files from its registry records.

Each TOML record under ROOT/registry/data/project_csv names its CSV in
`source_csv`, pins the bytes in `source_sha256` and `source_size_bytes`, and
stores the content as `original_header` plus `rows`. csv.writer with
lineterminator "\\n" reproduces those bytes. A CSV is written only when every
record naming it yields identical bytes whose sha256 and size equal the pins;
files are staged in a temporary directory beside the target and renamed, so a
mismatch leaves ROOT/data/csv unchanged. `--only NAME...` limits the run to
CSVs whose file stem equals a NAME; the default covers every record that
carries `rows`.

    materialize_gororoba_csv.py ROOT [--only NAME...]
    materialize_gororoba_csv.py --self-test
"""

import argparse
import csv
import hashlib
import io
import sys
import tempfile
import tomllib
from pathlib import Path

REGISTRY = Path("registry/data/project_csv")
CSV_PREFIX = "data/csv/"


class MaterializeError(Exception):
    """A record whose rows cannot reproduce its pinned bytes."""


def render(record: dict[str, object], label: str) -> tuple[str, bytes]:
    """The (source_csv, bytes) one record pins, checked against its digest and size."""
    dataset = record.get("dataset")
    if not isinstance(dataset, dict):
        raise MaterializeError(f"{label}: no [dataset] table")
    source = dataset.get("source_csv")
    header = dataset.get("original_header")
    rows = dataset.get("rows")
    sha256 = dataset.get("source_sha256")
    size = dataset.get("source_size_bytes")
    if not isinstance(source, str) or not source.startswith(CSV_PREFIX):
        raise MaterializeError(f"{label}: source_csv {source!r} is not under {CSV_PREFIX}")
    if not isinstance(header, list) or not isinstance(rows, list):
        raise MaterializeError(f"{label}: original_header or rows missing")
    if not isinstance(sha256, str) or not isinstance(size, int):
        raise MaterializeError(f"{label}: source_sha256 or source_size_bytes missing")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    digest = hashlib.sha256(data).hexdigest()
    if digest != sha256:
        raise MaterializeError(f"{label}: rows give sha256 {digest}, pinned {sha256}")
    if len(data) != size:
        raise MaterializeError(f"{label}: rows give {len(data)} bytes, pinned {size}")
    return source, data


def collect(root: Path, only: list[str] | None) -> dict[str, bytes]:
    """The bytes of every selected CSV, keyed by source_csv, agreeing across records."""
    registry = root / REGISTRY
    if not registry.is_dir():
        raise MaterializeError(f"{registry} is not a directory")
    out: dict[str, bytes] = {}
    owner: dict[str, str] = {}
    for path in sorted(registry.rglob("*.toml")):
        with path.open("rb") as handle:
            record = tomllib.load(handle)
        dataset = record.get("dataset")
        if not isinstance(dataset, dict):
            continue
        source = dataset.get("source_csv")
        if not isinstance(source, str) or not source.startswith(CSV_PREFIX):
            continue
        if only is not None and Path(source).stem not in only:
            continue
        if "rows" not in dataset:
            if only is None:
                continue
            raise MaterializeError(f"{path.name}: record of {source} has no rows")
        label = path.name
        source, data = render(record, label)
        if source in out and out[source] != data:
            raise MaterializeError(f"{label} and {owner[source]} disagree on {source}")
        out[source] = data
        owner.setdefault(source, label)
    if only is not None:
        found = {Path(source).stem for source in out}
        missing = sorted(set(only) - found)
        if missing:
            raise MaterializeError(f"no record for {missing}")
    return out


def write_all(root: Path, files: dict[str, bytes]) -> None:
    """Stage every file in one temporary directory under root/data/csv, then rename."""
    target = root / "data" / "csv"
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target, prefix=".stage-") as tmp:
        staged = []
        for source, data in sorted(files.items()):
            stage = Path(tmp) / Path(source).name
            stage.write_bytes(data)
            staged.append((stage, root / source))
        for stage, dest in staged:
            stage.replace(dest)


def _record(
    source: str, header: list[str], rows: list[list[str]], *, sha: str | None = None, with_rows: bool = True
) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    data = buffer.getvalue().encode("utf-8")
    digest = sha if sha is not None else hashlib.sha256(data).hexdigest()
    lines = [
        "[dataset]",
        f'source_csv = "{source}"',
        f'source_sha256 = "{digest}"',
        f"source_size_bytes = {len(data)}",
        "original_header = [" + ", ".join(f'"{h}"' for h in header) + "]",
    ]
    if with_rows:
        lines.append("rows = [" + ", ".join("[" + ", ".join(f'"{c}"' for c in r) + "]" for r in rows) + "]")
    return "\n".join(lines) + "\n"


def _check(condition: bool, message: object = "self-test check failed") -> None:
    """Fail under python -O as well, where assert statements vanish."""
    if not condition:
        raise AssertionError(message)


def _expect_failure(root: Path, only: list[str] | None, text: str) -> None:
    try:
        collect(root, only)
    except MaterializeError as error:
        if text not in str(error):
            raise AssertionError(f"wrong rejection: {error}") from error
        return
    raise AssertionError(f"accepted a record that must fail ({text})")


def self_test() -> int:
    """Byte-exact output, digest mismatch, missing rows and duplicate disagreement."""
    header = ["", "1", "e1"]
    rows = [["1", "1", "e1"], ["e1", "e1", "-1"]]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        reg = root / REGISTRY
        (reg / "a").mkdir(parents=True)
        (reg / "a" / "r1.toml").write_text(_record("data/csv/t.csv", header, rows))
        (reg / "a" / "r2.toml").write_text(_record("data/csv/t.csv", header, rows))
        (reg / "a" / "r3.toml").write_text(_record("data/csv/u.csv", ["x"], [["y"]]))
        (reg / "a" / "norows.toml").write_text(_record("data/csv/n.csv", ["x"], [["y"]], with_rows=False))
        files = collect(root, None)
        _check(sorted(files) == ["data/csv/t.csv", "data/csv/u.csv"], sorted(files))
        _check(files["data/csv/t.csv"] == b",1,e1\n1,1,e1\ne1,e1,-1\n", files["data/csv/t.csv"])
        only = collect(root, ["u"])
        _check(sorted(only) == ["data/csv/u.csv"])
        write_all(root, files)
        _check((root / "data/csv/t.csv").read_bytes() == files["data/csv/t.csv"])
        _check(sorted(p.name for p in (root / "data/csv").iterdir()) == ["t.csv", "u.csv"])
        _expect_failure(root, ["n"], "no rows")
        _expect_failure(root, ["absent"], "no record for")

        bad = root / "bad"
        (bad / REGISTRY).mkdir(parents=True)
        (bad / REGISTRY / "x.toml").write_text(_record("data/csv/t.csv", header, rows, sha="0" * 64))
        _expect_failure(bad, None, "pinned")
        _check(not (bad / "data").exists())

        dup = root / "dup"
        (dup / REGISTRY).mkdir(parents=True)
        (dup / REGISTRY / "x.toml").write_text(_record("data/csv/t.csv", header, rows))
        (dup / REGISTRY / "y.toml").write_text(_record("data/csv/t.csv", header, [["z", "z", "z"]]))
        _expect_failure(dup, None, "disagree")
    print("materialize_gororoba_csv self-test ok")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", nargs="?", type=Path, help="open_gororoba checkout")
    parser.add_argument("--only", nargs="+", metavar="NAME", help="CSV file stems to write")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.root is None:
        parser.error("ROOT is required")
    try:
        files = collect(args.root, args.only)
        write_all(args.root, files)
    except MaterializeError as error:
        print(f"materialize_gororoba_csv: {error}", file=sys.stderr)
        return 1
    for source in sorted(files):
        print(f"wrote {source} ({len(files[source])} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
