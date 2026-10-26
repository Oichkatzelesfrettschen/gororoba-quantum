"""Every integer seed literal in the code directories and tracked docs probes is a reproduction seed or QRNG value.

The scan parses each Python file under ci/, tests/, gororoba_quantum/, scripts/
and kaggle_kernel/, and each git-tracked Python file under docs/ (retained
probes and replays; git ls-files leaves ignored scratch out), and collects every
integer literal in a seed position:

- a keyword argument, a function parameter default, a dict entry or an
  assignment whose name is a seed name (``seed``, ``*_seed``, ``seed_*``,
  ``random_state``; a ``*seeds`` name assigned a tuple or list contributes each
  element);
- the first argument of a generator constructor or seeding call
  (``default_rng``, ``seed``, ``Random``, ``RandomState``, ``SeedSequence``,
  ``PCG64``, ``MT19937``, ``Philox``, ``SFC64``);
- the ``default`` of an argparse option whose flag carries ``seed``.

Each literal is keyed by (file, seed name, value). ci/reproduction_seeds.json
lists the keys that reproduce retained records, approved plans and known
meshes, with their counts; --shrink refuses a row it adds or raises over the
baseline origin/main holds. docs/evidence/qrng_seeds/allocations.json
lists each key a new seed took from a retained QRNG draw, with the draw record
and the value's index. The check requires, per key, the tree's count to equal
the baseline count plus the allocation count; each allocation's record to pass
its source's admit function (SOURCES: the ANU, Outshift and Quandela adapters
under scripts/) and hold the value at its index; each (record, index) to be
allocated once, under the canonical path docs/evidence/<source>/draw-<UTC>.json; and no
allocation to take a record that a case manifest under
results/ names, by file name, since such a case owns its whole draw.

The ``reserved`` section of allocations.json lists consumers the scan cannot key,
such as a value a helper alias seeds (``RNG(20108)``) or a mapping the seed
positions omit: rows {path, value, record, index, reason}. The check requires
the record to pass its source's admit function and hold the value at the index;
the path to be a tracked file that holds the value as an integer token and
names the record's file name; each (record, index) to appear once across
allocations, runtime and reserved together; and the scan to detect none of a
reserved row's values in its file, since a detectable literal belongs in
allocations. --shrink also accepts a baseline row whose (file, name, value)
literal the base tree already holds in that file at the same or a higher count,
because such a literal predates the change; a literal the base lacks stays
refused.

Usage: "$PYTHON" ci/seed_provenance.py (--check | --shrink | --runtime | --add-runtime | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import zlib
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(1, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402
import qrng_seeds  # noqa: E402

CODE_DIRS = ("ci", "tests", "gororoba_quantum", "scripts", "kaggle_kernel")
DOCS_DIR = "docs"
BASELINE = ROOT / "ci" / "reproduction_seeds.json"
ALLOCATIONS = ROOT / "docs" / "evidence" / "qrng_seeds" / "allocations.json"
MANIFEST_ROOT = ROOT / "results"
SOURCES = qrng_seeds.SOURCES
# Flags that carry "seed" yet set no seed value: counts of transpiler or QX seeds, a recompile switch and the
# retained comparison whose job rows a rewrite reuses.
PLAIN_SEED_FLAGS = frozenset(
    {
        ("gororoba_quantum/live_run.py", "--seeds"),
        ("scripts/n21_qx_conformance.py", "--seeds"),
        ("scripts/n21_conjugation_noise.py", "--all-seeds"),
        ("scripts/compare_submitted_circuits.py", "--seed"),
    }
)
# The shrink-only comparison reads the baseline main holds; pr.yml fetches this ref before the tests.
BASE_REF = "origin/main"
DRAW_NAME = qrng_seeds.DRAW_NAME
ARGUMENT_CALLS = ("add_argument", "add_seed_argument")
# A seed_ name with one of these suffixes counts or spaces seeds rather than seeding.
NOT_SEED_SUFFIXES = ("count", "stride", "offset", "step")
SEEDING_CALLS = frozenset(
    {"default_rng", "seed", "Random", "RandomState", "SeedSequence", "PCG64", "MT19937", "Philox", "SFC64"}
)
# Every seed position names one of these, so a file without any holds no seed literal and skips the parse.
SEED_TOKEN = re.compile("seed|random|default_rng|PCG64|MT19937|Philox|SFC64", re.IGNORECASE)
# The pull-request tests split the tree into this many shards by crc32 of each path, so a shard keeps
# its files across additions and deletions and each test stays inside the per-test budget.
SHARDS = 8

Key = tuple[str, str, int]


class SeedError(ValueError):
    pass


def seed_name(name: str) -> bool:
    lower = name.lower()
    if lower.startswith("seed_") and lower.endswith(NOT_SEED_SUFFIXES):
        return False
    return lower in ("seed", "random_state") or lower.endswith("_seed") or lower.startswith("seed_")


def seeds_name(name: str) -> bool:
    lower = name.lower()
    return lower == "seeds" or lower.endswith("_seeds")


def integer(node: ast.AST | None) -> int | None:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = integer(node.operand)
        return None if inner is None else -inner
    return None


def target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def call_name(node: ast.Call) -> str | None:
    return target_name(node.func)


def literals(tree: ast.AST) -> Iterator[tuple[str, int]]:
    """(seed name, value) for every integer literal in a seed position."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name in SEEDING_CALLS and node.args and (value := integer(node.args[0])) is not None:
                yield name, value
            for keyword in node.keywords:
                if keyword.arg and seed_name(keyword.arg) and (value := integer(keyword.value)) is not None:
                    yield keyword.arg, value
            if name in ARGUMENT_CALLS:
                flags = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                flag = next((f for f in flags if "seed" in f.lower()), None)
                for keyword in node.keywords:
                    if flag and keyword.arg == "default" and (value := integer(keyword.value)) is not None:
                        yield flag, value
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            arguments = node.args
            positional = arguments.posonlyargs + arguments.args
            pairs = list(zip(positional[len(positional) - len(arguments.defaults) :], arguments.defaults, strict=True))
            pairs += [(a, d) for a, d in zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True) if d]
            for argument, default in pairs:
                if seed_name(argument.arg) and (value := integer(default)) is not None:
                    yield argument.arg, value
        elif isinstance(node, ast.Dict):
            for key, item in zip(node.keys, node.values, strict=True):
                if isinstance(key, ast.Constant) and isinstance(key.value, str) and seed_name(key.value):
                    if (value := integer(item)) is not None:
                        yield key.value, value
        elif isinstance(node, ast.Assign | ast.AnnAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                name = target_name(target)
                if name is None:
                    continue
                if seed_name(name) and (value := integer(node.value)) is not None:
                    yield name, value
                elif seeds_name(name) and isinstance(node.value, ast.Tuple | ast.List):
                    for element in node.value.elts:
                        if (value := integer(element)) is not None:
                            yield name, value


def shard_of(relative: str) -> int:
    return zlib.crc32(relative.encode()) % SHARDS


def plain_seed_flags(tree: ast.AST) -> Iterator[str]:
    """Flags carrying "seed" that a bare add_argument declares instead of add_seed_argument."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and call_name(node) == "add_argument":
            for argument in node.args:
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str) and "seed" in argument.value:
                    yield argument.value


def file_literals(relative: str) -> tuple[list[Key], list[tuple[str, str]]]:
    return text_literals(relative, (ROOT / relative).read_text(encoding="utf-8"))


def text_literals(relative: str, text: str) -> tuple[list[Key], list[tuple[str, str]]]:
    """The seed literals and bare seed flags of one file's text, keyed under its repository path."""
    if not SEED_TOKEN.search(text):
        return [], []
    tree = ast.parse(text, filename=relative)
    keys = [(relative, name, value) for name, value in literals(tree)]
    return keys, [(relative, flag) for flag in plain_seed_flags(tree)]


def tracked_files() -> frozenset[str]:
    """Every git-tracked path, so ignored scratch under docs/ never enters the scan."""
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True)
    if listed.returncode != 0:
        raise SeedError(f"git ls-files failed: {listed.stderr.strip()}")
    return frozenset(path for path in listed.stdout.split("\0") if path)


def scan(shard: int | None = None) -> tuple[Counter[Key], list[tuple[str, str]]]:
    """Seed literal counts and bare seed flags over the code directories and the tracked docs probes, or over
    one shard of their files."""
    tracked_docs = sorted(path for path in tracked_files() if path.startswith(f"{DOCS_DIR}/") and path.endswith(".py"))
    paths = [
        path.relative_to(ROOT).as_posix()
        for directory in CODE_DIRS
        for path in sorted((ROOT / directory).rglob("*.py"))
    ] + [path for path in tracked_docs if (ROOT / path).is_file()]
    selected = [path for path in paths if shard is None or shard_of(path) == shard]
    results = parallel.ordered_map(file_literals, selected)
    return Counter(key for keys, _ in results for key in keys), [flag for _, flags in results for flag in flags]


def baseline_counts(rows: list[dict[str, Any]]) -> Counter[Key]:
    counts: Counter[Key] = Counter()
    for row in rows:
        key = (row["path"], row["name"], row["value"])
        if key in counts:
            raise SeedError(f"reproduction seed {key} is listed twice")
        counts[key] = row["count"]
    return counts


def file_claims(path: str) -> list[str]:
    """Draw file names one retained file names without an index. A file that references a draw by index (a run
    record, or a scripts/kaggle_run.py manifest whose bundle inventory also names the draw file) consumes indices,
    not the whole draw."""
    text = Path(path).read_text(encoding="utf-8")
    indexed = {Path(match.group(1)).name for match in qrng_seeds.REF.finditer(text)}
    return sorted(set(DRAW_NAME.findall(qrng_seeds.REF.sub("", text))) - indexed)


def manifest_files(manifest_root: Path) -> list[str]:
    return [str(path) for path in sorted(manifest_root.rglob("*.json"))] if manifest_root.is_dir() else []


def claimed_records(manifest_root: Path) -> set[str]:
    """File names of the draw records that retained case files name without an index; such a case owns its
    whole draw, while a qrng:<draw>#<index> reference consumes that one index."""
    return {name for names in parallel.ordered_map(file_claims, manifest_files(manifest_root)) for name in names}


def seed_sources(node: Any) -> Iterator[dict[str, Any]]:
    """Every seed_source entry (qrng_seeds.seed_record) inside a parsed record."""
    if isinstance(node, dict):
        if {"script", "flag", "experiment", "sources"} <= set(node) and isinstance(node["sources"], list):
            yield node
        for value in node.values():
            yield from seed_sources(value)
    elif isinstance(node, list):
        for value in node:
            yield from seed_sources(value)


Consumer = tuple[str, str, str]


def file_references(path: str) -> tuple[list[tuple[str, int]], list[tuple[str, int, Consumer]]]:
    """One retained file's qrng references, and the (record, index, consumer) its seed_source entries declare."""
    text = Path(path).read_text(encoding="utf-8")
    found = sorted({(match.group(1), int(match.group(2))) for match in qrng_seeds.REF.finditer(text)})
    if not found:
        return [], []
    declared = []
    for entry in seed_sources(json.loads(text)):
        for source in entry["sources"]:
            if isinstance(source, str) and (match := qrng_seeds.REF.fullmatch(source)):
                consumer = (entry["script"], entry["flag"], entry["experiment"])
                declared.append((match.group(1), int(match.group(2)), consumer))
    return found, declared


def runtime_consumption(manifest_root: Path) -> tuple[dict[tuple[str, int], set[Consumer]], list[str]]:
    """(record, index) -> the (script, flag, experiment) keys of every retained qrng reference, and the
    files that carry a qrng reference no seed_source entry under the root declares."""
    paths = manifest_files(manifest_root)
    consumed: dict[tuple[str, int], set[Consumer]] = {}
    mentions: dict[str, set[tuple[str, int]]] = {}
    for path, (found, declared) in zip(paths, parallel.ordered_map(file_references, paths), strict=True):
        if found:
            mentions[Path(path).relative_to(manifest_root.parent).as_posix()] = set(found)
        for record_path, index, consumer in declared:
            consumed.setdefault((record_path, index), set()).add(consumer)
    # A replay command, a wrapper manifest (scripts/kaggle_run.py submission.json args) or a copy may repeat a
    # reference; a reference that no seed_source under the root declares is stray.
    stray = [path for path, found in mentions.items() if found - set(consumed)]
    return consumed, stray


def check_runtime(
    consumed: dict[tuple[str, int], set[Consumer]],
    stray: list[str],
    runtime: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    claimed: set[str],
    read_record: Callable[[str], dict[str, Any]],
) -> None:
    """Every retained qrng reference has one consumer and one ledger row, and every ledger row one reference."""
    problems = [f"{path}: a qrng reference outside a seed_source entry" for path in stray]
    code = {(row["record"], row["index"]) for row in allocations}
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for row in runtime:
        slot = (row["record"], row["index"])
        if slot in rows:
            problems.append(f"runtime ledger: index {slot[1]} of {slot[0]} is listed twice")
            continue
        rows[slot] = row
        if slot in code:
            problems.append(f"runtime ledger: index {slot[1]} of {slot[0]} also seeds a code literal")
        if Path(slot[0]).name in claimed:
            problems.append(f"runtime ledger: {slot[0]} belongs to a case manifest under results/")
        qrng_seeds.source_directory(slot[0])
        values = read_record(slot[0])["values"]
        if not 0 <= slot[1] < len(values) or values[slot[1]] != row["value"]:
            problems.append(f"runtime ledger: value {row['value']} is not index {slot[1]} of {slot[0]}")
    for slot, consumers in sorted(consumed.items()):
        if len(consumers) > 1:
            problems.append(f"index {slot[1]} of {slot[0]} seeds {len(consumers)} experiments: {sorted(consumers)}")
        ledger_row = rows.get(slot)
        if ledger_row is None:
            problems.append(
                f"index {slot[1]} of {slot[0]} has no runtime ledger row; run ci/seed_provenance.py --add-runtime"
            )
        elif {(ledger_row["script"], ledger_row["flag"], ledger_row["experiment"])} != consumers:
            problems.append(f"runtime ledger: index {slot[1]} of {slot[0]} names another consumer than its records")
    problems += [
        f"runtime ledger: index {i} of {r} has no retained reference" for r, i in sorted(set(rows) - set(consumed))
    ]
    if problems:
        raise SeedError("\n".join(problems))


def admit_row(
    key: Any,
    row: dict[str, Any],
    claimed: set[str],
    records: dict[str, dict[str, Any]],
    read_record: Callable[[str], dict[str, Any]],
) -> None:
    """One ledger row's record is canonically spelled, free of a case manifest, admitted by its source and
    holds the row's value at the row's index."""
    record_path = row["record"]
    name = Path(record_path).name
    directory = record_path.rpartition("/")[0]
    if not DRAW_NAME.fullmatch(name) or directory not in SOURCES or record_path != f"{directory}/{name}":
        raise SeedError(f"{key}: record {record_path!r} is not spelled <source directory>/draw-<UTC>.json")
    if name in claimed:
        raise SeedError(f"{key}: {record_path} belongs to a case manifest under results/")
    if record_path not in records:
        record = read_record(record_path)
        SOURCES[directory](record)
        records[record_path] = record
    index = row["index"]
    values = records[record_path]["values"]
    if not 0 <= index < len(values) or values[index] != row["value"]:
        raise SeedError(f"{key}: value {row['value']} is not index {index} of {record_path}")


def value_token(value: int) -> re.Pattern[str]:
    """The integer ``value`` as a whole token, so 7190 never matches inside 71900 or a longer name."""
    return re.compile(rf"(?<![\w.]){value}(?![\w.])")


def check_reserved(
    reserved: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    runtime: list[dict[str, Any]],
    claimed: set[str],
    read_record: Callable[[str], dict[str, Any]],
    files: dict[str, tuple[str, frozenset[int]]],
) -> None:
    """Admit every reserved row. files maps each tracked path to its text and the values the scan detects in
    it; an untracked path is absent."""
    records: dict[str, dict[str, Any]] = {}
    owners: dict[tuple[str, int], str] = {}
    for section, rows in (("allocations", allocations), ("runtime", runtime)):
        for row in rows:
            owners.setdefault((row["record"], row["index"]), section)
    for row in reserved:
        key = (row["path"], row["value"])
        slot = (row["record"], row["index"])
        admit_row(key, row, claimed, records, read_record)
        if not str(row.get("reason", "")).strip():
            raise SeedError(f"reserved {key}: reason is empty")
        if slot in owners:
            raise SeedError(f"reserved {key}: index {slot[1]} of {slot[0]} is already taken in {owners[slot]}")
        owners[slot] = "reserved"
        if row["path"] not in files:
            raise SeedError(f"reserved {key}: {row['path']} is not a tracked file")
        text, detected = files[row["path"]]
        if row["value"] in detected:
            raise SeedError(f"reserved {key}: the scan detects {row['value']} in {row['path']}; list it in allocations")
        if not value_token(row["value"]).search(text):
            raise SeedError(f"reserved {key}: {row['path']} holds no integer token {row['value']}")
        if Path(row["record"]).name not in text:
            raise SeedError(f"reserved {key}: {row['path']} does not cite {Path(row['record']).name}")


def reserved_file(path: str) -> tuple[str, tuple[str, frozenset[int]]] | None:
    """One tracked reserved row's file as (path, (text, detected values)), or None when it is absent on disk."""
    if not (ROOT / path).is_file():
        return None
    text = (ROOT / path).read_text(encoding="utf-8")
    return path, (text, frozenset(value for _, _, value in text_literals(path, text)[0]))


def check(
    found: Counter[Key],
    baseline: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    claimed: set[str],
    read_record: Callable[[str], dict[str, Any]],
    shard: int | None = None,
    plain_flags: list[tuple[str, str]] | None = None,
) -> None:
    """Admit every allocation; compare counts and bare seed flags for every file, or for one shard's files."""
    expected = baseline_counts(baseline)
    taken: set[tuple[str, int]] = set()
    records: dict[str, dict[str, Any]] = {}
    for row in allocations:
        key = (row["path"], row["name"], row["value"])
        record_path = row["record"]
        admit_row(key, row, claimed, records, read_record)
        index = row["index"]
        if (record_path, index) in taken:
            raise SeedError(f"{key}: index {index} of {record_path} is allocated twice")
        taken.add((record_path, index))
        expected[key] += 1
    problems = []
    flags = set(plain_flags or [])
    in_shard = {item for item in PLAIN_SEED_FLAGS if shard is None or shard_of(item[0]) == shard}
    problems += [
        f"{path}: {flag} is declared by add_argument; declare it with qrng_seeds.add_seed_argument"
        for path, flag in sorted(flags - PLAIN_SEED_FLAGS)
    ]
    if plain_flags is not None:
        problems += [
            f"{path}: {flag} is listed in PLAIN_SEED_FLAGS and no longer exists"
            for path, flag in sorted(in_shard - flags)
        ]
    for key in sorted(set(found) | set(expected)):
        if shard is not None and shard_of(key[0]) != shard:
            continue
        if found[key] > expected[key]:
            problems.append(
                f"{key[0]}: seed {key[1]}={key[2]} appears {found[key]} times, {expected[key]} accounted; "
                "draw it from a QRNG source (docs/notes/qrng/README.md) and add its index to "
                "docs/evidence/qrng_seeds/allocations.json, "
                "or import the existing seed constant when the job reproduces its result"
            )
        elif found[key] < expected[key]:
            problems.append(
                f"{key[0]}: seed {key[1]}={key[2]} appears {found[key]} times, {expected[key]} listed; "
                "lower the stale count in ci/reproduction_seeds.json or allocations.json"
            )
    if problems:
        raise SeedError("\n".join(problems))


def raised_rows(base: list[dict[str, Any]], head: list[dict[str, Any]]) -> list[tuple[Key, int, int]]:
    """(key, head count, base count) for every row the head baseline adds or raises over the base baseline."""
    before = baseline_counts(base)
    return [(key, count, before[key]) for key, count in sorted(baseline_counts(head).items()) if count > before[key]]


def shrink_problems(
    base: list[dict[str, Any]], head: list[dict[str, Any]], base_literals: dict[str, Counter[Key]]
) -> list[str]:
    """Rows the head baseline adds or raises over the base baseline; an exemption only ever goes away. A row
    whose literal base_literals (the base tree's literals of that file) already holds at the row's count
    predates the change and is no new seed."""
    return [
        f"ci/reproduction_seeds.json: {key} count {count} exceeds {before} on {BASE_REF}; "
        "a new seed takes a QRNG value through docs/evidence/qrng_seeds/allocations.json"
        for key, count, before in raised_rows(base, head)
        if base_literals.get(key[0], Counter())[key] < count
    ]


def base_file_literals(path: str) -> Counter[Key]:
    """The seed literal counts of one file as BASE_REF holds it; empty when BASE_REF lacks the file."""
    shown = subprocess.run(["git", "show", f"{BASE_REF}:{path}"], cwd=ROOT, capture_output=True, text=True)
    if shown.returncode != 0:
        return Counter()
    return Counter(text_literals(path, shown.stdout)[0])


def base_allocated() -> Counter[Key]:
    """Allocation counts per literal key in BASE_REF's allocations.json; empty when BASE_REF lacks the file."""
    relative = ALLOCATIONS.relative_to(ROOT).as_posix()
    shown = subprocess.run(["git", "show", f"{BASE_REF}:{relative}"], cwd=ROOT, capture_output=True, text=True)
    if shown.returncode != 0:
        return Counter()
    return Counter(
        (row["path"], row["name"], row["value"]) for row in parse_rows(shown.stdout, relative, "allocations")
    )


def unaccounted(literals: dict[str, Counter[Key]], allocated: Counter[Key]) -> dict[str, Counter[Key]]:
    """Base-tree literals less the ones a base allocation already accounts for: a QRNG consumer allocated on the
    base never becomes a reproduction seed, since dropping its allocation would free an index it still uses."""
    return {path: Counter({key: n - allocated[key] for key, n in counts.items()}) for path, counts in literals.items()}


def base_baseline() -> list[dict[str, Any]] | None:
    """The baseline at BASE_REF, or None when BASE_REF predates the file."""
    relative = BASELINE.relative_to(ROOT).as_posix()
    resolved = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{BASE_REF}^{{commit}}"], cwd=ROOT, capture_output=True, text=True
    )
    if resolved.returncode != 0:
        raise SeedError(f"{BASE_REF} is absent; fetch it (git fetch origin main) for the shrink-only comparison")
    shown = subprocess.run(["git", "show", f"{BASE_REF}:{relative}"], cwd=ROOT, capture_output=True, text=True)
    if shown.returncode != 0:
        return None
    return parse_rows(shown.stdout, relative, "seeds")


def check_shrink() -> int:
    base = base_baseline()
    head = load(BASELINE, "seeds")
    paths = [] if base is None else sorted({key[0] for key, _, _ in raised_rows(base, head)})
    literals = dict(zip(paths, parallel.ordered_map(base_file_literals, paths), strict=True))
    base_literals = unaccounted(literals, base_allocated() if paths else Counter())
    problems = [] if base is None else shrink_problems(base, head, base_literals)
    if problems:
        raise SeedError("\n".join(problems))
    print(f"seed provenance: reproduction seeds only shrink against {BASE_REF}")
    return 0


def parse_rows(text: str, path: Path | str, field: str) -> list[dict[str, Any]]:
    data = json.loads(text)
    rows = data[field]
    if not isinstance(rows, list):
        raise SeedError(f"{path}: {field} is not a list")
    return rows


def load(path: Path, field: str) -> list[dict[str, Any]]:
    return parse_rows(path.read_text(encoding="utf-8"), path, field)


def read_tree_record(record_path: str) -> dict[str, Any]:
    return qrng_seeds.read_record(record_path, ROOT)


def check_tree(shard: int | None = None) -> int:
    found, flags = scan(shard)
    claimed = claimed_records(MANIFEST_ROOT)
    allocations = load(ALLOCATIONS, "allocations")
    check(found, load(BASELINE, "seeds"), allocations, claimed, read_tree_record, shard, flags)
    if shard in (None, 0):
        reserved = load(ALLOCATIONS, "reserved")
        tracked = tracked_files()
        paths = sorted({row["path"] for row in reserved if row["path"] in tracked})
        files = {item[0]: item[1] for item in parallel.ordered_map(reserved_file, paths) if item is not None}
        check_reserved(reserved, allocations, load(ALLOCATIONS, "runtime"), claimed, read_tree_record, files)
    print(f"seed provenance: {sum(found.values())} seed literals accounted")
    return 0


def check_runtime_tree() -> int:
    consumed, stray = runtime_consumption(MANIFEST_ROOT)
    allocations = load(ALLOCATIONS, "allocations")
    runtime = load(ALLOCATIONS, "runtime")
    allocations = allocations + load(ALLOCATIONS, "reserved")
    check_runtime(consumed, stray, runtime, allocations, claimed_records(MANIFEST_ROOT), read_tree_record)
    print(f"seed provenance: {len(consumed)} retained qrng references match the runtime ledger")
    return 0


def add_runtime() -> int:
    """Append a ledger row for every retained qrng reference that lacks one; the check then runs as usual."""
    consumed, _ = runtime_consumption(MANIFEST_ROOT)
    ledger = json.loads(ALLOCATIONS.read_text(encoding="utf-8"))
    present = {(row["record"], row["index"]) for row in ledger["runtime"]}
    added = 0
    for (record_path, index), consumers in sorted(consumed.items()):
        if (record_path, index) in present or len(consumers) != 1:
            continue
        script, flag, experiment = next(iter(consumers))
        value = read_tree_record(record_path)["values"][index]
        ledger["runtime"].append(
            {
                "record": record_path,
                "index": index,
                "value": value,
                "script": script,
                "flag": flag,
                "experiment": experiment,
            }
        )
        added += 1
    ledger["runtime"].sort(key=lambda row: (row["record"], row["index"]))
    ALLOCATIONS.write_text(json.dumps(ledger, indent=1) + "\n", encoding="utf-8")
    print(f"seed provenance: {added} runtime ledger rows added")
    return check_runtime_tree()


def self_test() -> int:
    source = (
        "import numpy as np\n"
        "SEED = 5\n"
        "SEEDS = 8\n"
        "rng = np.random.default_rng(3)\n"
        "def f(seed_simulator=4):\n"
        "    run(seed_transpiler=-1, shots=9, options={'seed': 2}, seed=SEED)\n"
        "parser.add_argument('--seed', type=int, default=6)\n"
        "TRIAL_SEEDS = (10, 11)\n"
    )
    missed = [name for name in SEEDING_CALLS if not SEED_TOKEN.search(name)]
    if missed:
        raise SystemExit(f"self-test: the file prefilter skips {missed}")
    got = sorted(literals(ast.parse(source)))
    want = sorted(
        [
            ("SEED", 5),
            ("default_rng", 3),
            ("seed_simulator", 4),
            ("seed_transpiler", -1),
            ("seed", 2),
            ("--seed", 6),
            ("TRIAL_SEEDS", 10),
            ("TRIAL_SEEDS", 11),
        ]
    )
    if got != want:
        raise SystemExit(f"self-test: scan found {got}, expected {want}")
    record = json.loads(sorted((ROOT / "docs/evidence/anu_qrng").glob("draw-*.json"))[-1].read_text(encoding="utf-8"))
    record_path = "docs/evidence/anu_qrng/draw-2000-01-01T000000Z.json"
    value = record["values"][0]
    good = Counter({("a.py", "SEED", 5): 1, ("b.py", "seed", value): 1})
    baseline = [{"path": "a.py", "name": "SEED", "value": 5, "count": 1}]
    allocation = {"path": "b.py", "name": "seed", "value": value, "record": record_path, "index": 0}

    def run(found: Counter[Key], base: list[dict[str, Any]], allocs: list[dict[str, Any]], claimed: set[str]) -> None:
        check(found, base, allocs, claimed, lambda path: record if path == record_path else {})

    run(good, baseline, [allocation], set())
    # Every registered source admits a retained draw of its own.
    for directory, admit_record in SOURCES.items():
        for draw_path in sorted((ROOT / directory).glob("draw-*.json"))[:1]:
            admit_record(json.loads(draw_path.read_text(encoding="utf-8")))
    # Each mutation and the fragment of the refusal it must raise.
    mutations = {
        "accounted": (good + Counter({("c.py", "seed", 7): 1}), baseline, [allocation], set()),
        "listed": (Counter({("b.py", "seed", value): 1}), baseline, [allocation], set()),
        "is not index": (good, baseline, [dict(allocation, index=len(record["values"]))], set()),
        "allocated twice": (
            good + Counter({("d.py", "seed", value): 1}),
            baseline,
            [allocation, dict(allocation, path="d.py")],
            set(),
        ),
        "belongs to a case": (good, baseline, [allocation], {Path(record_path).name}),
        "<source directory>": (
            good,
            baseline,
            [dict(allocation, record="docs/evidence/unregistered/draw-2000-01-01T000000Z.json")],
            set(),
        ),
        "is not spelled": (
            good + Counter({("d.py", "seed", value): 1}),
            baseline,
            [allocation, dict(allocation, path="d.py", record="./" + record_path)],
            set(),
        ),
    }
    for fragment, (found, base, allocs, claimed) in mutations.items():
        try:
            run(found, base, allocs, claimed)
        except SeedError as error:
            if fragment in str(error):
                continue
            raise SystemExit(f"self-test: the {fragment!r} mutation raised {error}") from None
        raise SystemExit(f"self-test: the {fragment!r} mutation was admitted")
    raised = dict(baseline[0], count=2)
    added = {"path": "c.py", "name": "SEED", "value": 12345, "count": 1}
    if shrink_problems(baseline, [], {}) or shrink_problems(baseline, baseline, {}):
        raise SystemExit("self-test: a kept or removed reproduction seed was refused")
    # A base tree holding the literal at the row's count admits the row; a new literal or higher count stays refused.
    held = {"a.py": Counter({("a.py", "SEED", 5): 1}), "c.py": Counter({("c.py", "SEED", 12345): 1})}
    for name, head, literals_held in (
        ("a raised count", [raised], held),
        ("an added row", [*baseline, added], {}),
        ("an added row over another file's literal", [*baseline, added], {"a.py": held["a.py"]}),
        ("an added row over a lower base count", [*baseline, dict(added, count=2)], held),
    ):
        if not shrink_problems(baseline, head, literals_held):
            raise SystemExit(f"self-test: {name} in ci/reproduction_seeds.json was admitted")
    if not shrink_problems(baseline, [*baseline, added], unaccounted(held, Counter({("c.py", "SEED", 12345): 1}))):
        raise SystemExit("self-test: a base-allocated QRNG literal entered ci/reproduction_seeds.json")
    held_twice = {"a.py": Counter({("a.py", "SEED", 5): 2})}
    for name, head, literals_held in (
        ("an added row", [*baseline, added], held),
        ("a raised count", [raised], held_twice),
    ):
        if shrink_problems(baseline, head, literals_held):
            raise SystemExit(f"self-test: {name} over a base-tree literal was refused")
    runtime_refusals = runtime_self_test(record_path, record) + reserved_self_test(record_path, record) + 1
    flag_tree = ast.parse(
        "p.add_argument('--seed', type=int)\n"
        "p.add_argument('--seeds', type=int)\n"
        "add_seed_argument(p, '--x-seed', default=4)\n"
    )
    flags = [("x.py", flag) for flag in plain_seed_flags(flag_tree)]
    if flags != [("x.py", "--seed"), ("x.py", "--seeds")]:
        raise SystemExit(f"self-test: bare seed flags read as {flags}")
    if ("--x-seed", 4) not in list(literals(flag_tree)):
        raise SystemExit("self-test: an add_seed_argument default escaped the literal scan")
    try:
        check(Counter(), [], [], set(), lambda path: {}, None, flags)
    except SeedError as error:
        if "add_seed_argument" not in str(error):
            raise SystemExit(f"self-test: a bare seed flag raised {error}") from None
    else:
        raise SystemExit("self-test: a bare seed flag was admitted")
    total = len(mutations) + 5 + runtime_refusals + 1
    print(f"seed_provenance self-test: scan matched, {total} mutations rejected")
    return 0


def reserved_self_test(record_path: str, record: dict[str, Any]) -> int:
    """The reserved section admits one alias consumer per index and refuses each defect; returns the refusal count."""
    value = record["values"][2]
    name = Path(record_path).name
    row = {"path": "p.py", "value": value, "record": record_path, "index": 2, "reason": "RNG alias"}
    text = f"# {name}\nrng = RNG({value})\n"
    files: dict[str, tuple[str, frozenset[int]]] = {"p.py": (text, frozenset())}
    taken = {"record": record_path, "index": 2}

    def run(
        rows: list[dict[str, Any]],
        allocs: list[dict[str, Any]] | None = None,
        runtime: list[dict[str, Any]] | None = None,
        tracked: dict[str, tuple[str, frozenset[int]]] | None = None,
    ) -> None:
        check_reserved(
            rows, allocs or [], runtime or [], set(), lambda path: record, files if tracked is None else tracked
        )

    run([row])
    refusals: dict[str, Any] = {
        "is not index": ([dict(row, value=value + 1)], None, None, None),
        "is not a tracked file": ([row], None, None, {}),
        "already taken in allocations": ([row], [taken], None, None),
        "already taken in runtime": ([row], None, [taken], None),
        "already taken in reserved": ([row, dict(row, path="q.py")], None, None, {**files, "q.py": files["p.py"]}),
        "the scan detects": ([row], None, None, {"p.py": (text, frozenset({value}))}),
        "holds no integer token": ([row], None, None, {"p.py": (f"# {name}\nrng = RNG({value}0)\n", frozenset())}),
        "does not cite": ([row], None, None, {"p.py": (f"rng = RNG({value})\n", frozenset())}),
        "reason is empty": ([dict(row, reason=" ")], None, None, None),
    }
    for fragment, (rows, allocs, runtime, tracked) in refusals.items():
        try:
            run(rows, allocs, runtime, tracked)
        except SeedError as error:
            if fragment in str(error):
                continue
            raise SystemExit(f"self-test: the {fragment!r} reserved mutation raised {error}") from None
        raise SystemExit(f"self-test: the {fragment!r} reserved mutation was admitted")
    detected = frozenset(
        value for _, _, value in text_literals("p.py", f"# {name}\nrng = np.random.default_rng({value})\n")[0]
    )
    if detected != {value}:
        raise SystemExit("self-test: the scan misses a default_rng literal that a reserved row would hide")
    return len(refusals)


def runtime_self_test(record_path: str, record: dict[str, Any]) -> int:
    """The runtime ledger admits one consumer per index and refuses each defect; returns the refusal count."""
    value = record["values"][1]
    consumer = ("scripts/x.py", "--seed", "case-a")
    consumed = {(record_path, 1): {consumer}}
    row = {
        "record": record_path,
        "index": 1,
        "value": value,
        "script": "scripts/x.py",
        "flag": "--seed",
        "experiment": "case-a",
    }

    def run(
        consumed: dict[tuple[str, int], set[Consumer]],
        stray: list[str],
        rows: list[dict[str, Any]],
        code: list[dict[str, Any]],
        claimed: set[str],
    ) -> None:
        check_runtime(consumed, stray, rows, code, claimed, lambda path: record)

    run(consumed, [], [row], [], set())
    refusals = {
        "outside a seed_source": (consumed, ["results/x.json"], [row], [], set()),
        "experiments": ({(record_path, 1): {consumer, ("scripts/x.py", "--seed", "case-b")}}, [], [row], [], set()),
        "no runtime ledger row": (consumed, [], [], [], set()),
        "is not index": (consumed, [], [dict(row, value=value + 1)], [], set()),
        "also seeds a code literal": (consumed, [], [row], [{"record": record_path, "index": 1}], set()),
        "belongs to a case": (consumed, [], [row], [], {Path(record_path).name}),
        "no retained reference": ({}, [], [row], [], set()),
        "another consumer": (consumed, [], [dict(row, experiment="case-b")], [], set()),
    }
    for fragment, arguments in refusals.items():
        try:
            run(*arguments)
        except SeedError as error:
            if fragment in str(error):
                continue
            raise SystemExit(f"self-test: the {fragment!r} runtime mutation raised {error}") from None
        raise SystemExit(f"self-test: the {fragment!r} runtime mutation was admitted")
    text = json.dumps(
        {
            "seed_source": qrng_seeds.seed_record(
                "scripts/x.py", "--seed", "case-a", [f"qrng:{record_path}#1", "default"]
            )
        }
    )
    if [entry["experiment"] for entry in seed_sources(json.loads(text))] != ["case-a"]:
        raise SystemExit("self-test: a seed_source entry was not found")
    if Path(record_path).name in DRAW_NAME.findall(qrng_seeds.REF.sub("", text)):
        raise SystemExit("self-test: an indexed reference claimed its whole draw")
    return len(refusals) + 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--shrink", action="store_true")
    group.add_argument("--runtime", action="store_true")
    group.add_argument("--add-runtime", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.shrink:
            return check_shrink()
        if args.runtime:
            return check_runtime_tree()
        if args.add_runtime:
            return add_runtime()
        return self_test() if args.self_test else check_tree()
    except SeedError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    sys.exit(main())
