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
meshes, with their counts; it only shrinks. docs/evidence/anu_qrng/allocations.json
lists each key a new seed took from a retained ANU draw, with the draw record
and the value's index. The check requires, per key, the tree's count to equal
the baseline count plus the allocation count; each allocation's record to pass
anu_qrng.admit and hold the value at its index; each (record, index) to be
allocated once; and no allocation to take a record that a case manifest under
results/ names, by file name, since such a case owns its whole draw.

Usage: "$PYTHON" ci/seed_provenance.py (--check | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import anu_qrng  # noqa: E402

CODE_DIRS = ("ci", "tests", "gororoba_quantum", "scripts", "kaggle_kernel")
BASELINE = ROOT / "ci" / "reproduction_seeds.json"
ALLOCATIONS = ROOT / "docs" / "evidence" / "anu_qrng" / "allocations.json"
MANIFEST_ROOT = ROOT / "results"
DRAW_NAME = re.compile(r"draw-\d{4}-\d{2}-\d{2}T\d{6}Z\.json")
# A seed_ name with one of these suffixes counts or spaces seeds rather than seeding.
NOT_SEED_SUFFIXES = ("count", "stride", "offset", "step")
SEEDING_CALLS = frozenset(
    {"default_rng", "seed", "Random", "RandomState", "SeedSequence", "PCG64", "MT19937", "Philox", "SFC64"}
)

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
            if name == "add_argument":
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


def scan(root: Path = ROOT) -> Counter[Key]:
    found: Counter[Key] = Counter()
    for directory in CODE_DIRS:
        for path in sorted((root / directory).rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            for name, value in literals(tree):
                found[(relative, name, value)] += 1
    return found


def baseline_counts(rows: list[dict[str, Any]]) -> Counter[Key]:
    counts: Counter[Key] = Counter()
    for row in rows:
        key = (row["path"], row["name"], row["value"])
        if key in counts:
            raise SeedError(f"reproduction seed {key} is listed twice")
        counts[key] = row["count"]
    return counts


def claimed_records(manifest_root: Path) -> set[str]:
    """File names of the draw records that retained case files name; such a case owns its whole draw."""
    claimed: set[str] = set()
    for path in sorted(manifest_root.rglob("*.json")) if manifest_root.is_dir() else []:
        claimed.update(DRAW_NAME.findall(path.read_text(encoding="utf-8")))
    return claimed


def check(
    found: Counter[Key],
    baseline: list[dict[str, Any]],
    allocations: list[dict[str, Any]],
    claimed: set[str],
    read_record: Callable[[str], dict[str, Any]],
) -> None:
    expected = baseline_counts(baseline)
    taken: set[tuple[str, int]] = set()
    records: dict[str, dict[str, Any]] = {}
    for row in allocations:
        key = (row["path"], row["name"], row["value"])
        record_path = row["record"]
        if Path(record_path).name in claimed:
            raise SeedError(f"{key}: {record_path} belongs to a case manifest under results/")
        if record_path not in records:
            record = read_record(record_path)
            anu_qrng.admit(record)
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
    for key in sorted(set(found) | set(expected)):
        if found[key] > expected[key]:
            problems.append(
                f"{key[0]}: seed {key[1]}={key[2]} appears {found[key]} times, {expected[key]} accounted; "
                "draw it with scripts/anu_qrng.py and add its index to docs/evidence/anu_qrng/allocations.json, "
                "or import the existing seed constant"
            )
        elif found[key] < expected[key]:
            problems.append(
                f"{key[0]}: seed {key[1]}={key[2]} appears {found[key]} times, {expected[key]} listed; "
                "lower the stale count in ci/reproduction_seeds.json or allocations.json"
            )
    if problems:
        raise SeedError("\n".join(problems))


def load(path: Path, field: str) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data[field]
    if not isinstance(rows, list):
        raise SeedError(f"{path}: {field} is not a list")
    return rows


def read_tree_record(record_path: str) -> dict[str, Any]:
    record: dict[str, Any] = json.loads((ROOT / record_path).read_text(encoding="utf-8"))
    return record


def check_tree() -> int:
    found = scan()
    claimed = claimed_records(MANIFEST_ROOT)
    check(found, load(BASELINE, "seeds"), load(ALLOCATIONS, "allocations"), claimed, read_tree_record)
    print(f"seed provenance: {sum(found.values())} seed literals accounted")
    return 0


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
    record_path = "docs/evidence/anu_qrng/self-test.json"
    value = record["values"][0]
    good = Counter({("a.py", "SEED", 5): 1, ("b.py", "seed", value): 1})
    baseline = [{"path": "a.py", "name": "SEED", "value": 5, "count": 1}]
    allocation = {"path": "b.py", "name": "seed", "value": value, "record": record_path, "index": 0}

    def run(found: Counter[Key], base: list[dict[str, Any]], allocs: list[dict[str, Any]], claimed: set[str]) -> None:
        check(found, base, allocs, claimed, lambda path: record if path == record_path else {})

    run(good, baseline, [allocation], set())
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
    }
    for fragment, (found, base, allocs, claimed) in mutations.items():
        try:
            run(found, base, allocs, claimed)
        except SeedError as error:
            if fragment in str(error):
                continue
            raise SystemExit(f"self-test: the {fragment!r} mutation raised {error}") from None
        raise SystemExit(f"self-test: the {fragment!r} mutation was admitted")
    print(f"seed_provenance self-test: scan matched, {len(mutations)} mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        return self_test() if args.self_test else check_tree()
    except SeedError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    sys.exit(main())
