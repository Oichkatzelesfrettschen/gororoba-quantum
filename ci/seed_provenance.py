"""Every integer seed literal in the code directories is a reproduction identifier or an ANU QRNG value.

The scan parses each Python file under ci/, tests/, gororoba_quantum/, scripts/
and kaggle_kernel/ and collects every integer literal in a seed position:

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
lists each key a new seed took from a retained ANU draw, with the draw record
and the value's index. The check requires, per key, the tree's count to equal
the baseline count plus the allocation count; each allocation's record to pass
its source's admit function (SOURCES: the ANU, Outshift and Quandela adapters
under scripts/) and hold the value at its index; each (record, index) to be
allocated once, under the canonical path docs/evidence/<source>/draw-<UTC>.json; and no
allocation to take a record that a case manifest under
results/ names, by file name, since such a case owns its whole draw.

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
BASELINE = ROOT / "ci" / "reproduction_seeds.json"
ALLOCATIONS = ROOT / "docs" / "evidence" / "qrng_seeds" / "allocations.json"
MANIFEST_ROOT = ROOT / "results"
SOURCES = qrng_seeds.SOURCES
# Flags that carry "seed" yet set no seed value: counts of transpiler or QX seeds and a recompile switch.
PLAIN_SEED_FLAGS = frozenset(
    {
        ("gororoba_quantum/live_run.py", "--seeds"),
        ("scripts/n21_qx_conformance.py", "--seeds"),
        ("scripts/n21_conjugation_noise.py", "--all-seeds"),
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
    text = (ROOT / relative).read_text(encoding="utf-8")
    if not SEED_TOKEN.search(text):
        return [], []
    tree = ast.parse(text, filename=relative)
    keys = [(relative, name, value) for name, value in literals(tree)]
    return keys, [(relative, flag) for flag in plain_seed_flags(tree)]


def scan(shard: int | None = None) -> tuple[Counter[Key], list[tuple[str, str]]]:
    """Seed literal counts and bare seed flags over the code directories, or over one shard of their files."""
    paths = [
        path.relative_to(ROOT).as_posix()
        for directory in CODE_DIRS
        for path in sorted((ROOT / directory).rglob("*.py"))
    ]
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


def claimed_records(manifest_root: Path) -> set[str]:
    """File names of the draw records that retained case files name without an index; such a case owns its
    whole draw, while a qrng:<draw>#<index> reference consumes that one index."""
    claimed: set[str] = set()
    for path in sorted(manifest_root.rglob("*.json")) if manifest_root.is_dir() else []:
        claimed.update(DRAW_NAME.findall(qrng_seeds.REF.sub("", path.read_text(encoding="utf-8"))))
    return claimed


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


def runtime_consumption(manifest_root: Path) -> tuple[dict[tuple[str, int], set[Consumer]], list[str]]:
    """(record, index) -> the (script, flag, experiment) keys of every retained qrng reference, and the
    files that carry a qrng reference outside a seed_source entry."""
    consumed: dict[tuple[str, int], set[Consumer]] = {}
    stray: list[str] = []
    for path in sorted(manifest_root.rglob("*.json")) if manifest_root.is_dir() else []:
        text = path.read_text(encoding="utf-8")
        mentions = len(qrng_seeds.REF.findall(text))
        if not mentions:
            continue
        placed = 0
        for entry in seed_sources(json.loads(text)):
            for source in entry["sources"]:
                if isinstance(source, str) and (match := qrng_seeds.REF.fullmatch(source)):
                    consumer = (entry["script"], entry["flag"], entry["experiment"])
                    consumed.setdefault((match.group(1), int(match.group(2))), set()).add(consumer)
                    placed += 1
        if placed != mentions:
            stray.append(path.relative_to(manifest_root.parent).as_posix())
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


def shrink_problems(base: list[dict[str, Any]], head: list[dict[str, Any]]) -> list[str]:
    """Rows the head baseline adds or raises over the base baseline; an exemption only ever goes away."""
    before = baseline_counts(base)
    return [
        f"ci/reproduction_seeds.json: {key} count {count} exceeds {before[key]} on {BASE_REF}; "
        "a new seed takes a QRNG value through docs/evidence/qrng_seeds/allocations.json"
        for key, count in sorted(baseline_counts(head).items())
        if count > before[key]
    ]


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
    problems = [] if base is None else shrink_problems(base, load(BASELINE, "seeds"))
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
    print(f"seed provenance: {sum(found.values())} seed literals accounted")
    return 0


def check_runtime_tree() -> int:
    consumed, stray = runtime_consumption(MANIFEST_ROOT)
    allocations = load(ALLOCATIONS, "allocations")
    runtime = load(ALLOCATIONS, "runtime")
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
    if shrink_problems(baseline, []) or shrink_problems(baseline, baseline):
        raise SystemExit("self-test: a kept or removed reproduction seed was refused")
    for name, head in (("a raised count", [raised]), ("an added row", [*baseline, added])):
        if not shrink_problems(baseline, head):
            raise SystemExit(f"self-test: {name} in ci/reproduction_seeds.json was admitted")
    runtime_refusals = runtime_self_test(record_path, record)
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
    total = len(mutations) + 2 + runtime_refusals + 1
    print(f"seed_provenance self-test: scan matched, {total} mutations rejected")
    return 0


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
