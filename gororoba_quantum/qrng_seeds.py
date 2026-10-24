"""Seed flags that take a quantum random value, the CLI's reproduction default, or an explicit reproduction.

Every CLI flag that sets a random seed is declared through add_seed_argument.
The flag accepts three spellings per value:

- ``qrng:<source directory>/draw-<UTC>.json#<index>`` names one value of a
  retained QRNG draw; the record must pass its source's admit function
  (SOURCES) and the index must lie inside it;
- the flag's own default (an integer the code already holds, listed in
  ci/reproduction_seeds.json), which reproduces the runs made with it;
- ``repro:<integer>``, an explicit reproduction of an earlier run that used a
  seed the code does not hold; the record marks it for review.

Any other integer is refused when the arguments are parsed. The parsed
namespace carries the plain integer (or list of integers) under the flag's
dest and, under ``<dest>_source``, the spelling of each value. seed_record
turns that into the ``seed_source`` entry a CLI writes into its run record:
``{"script", "flag", "experiment", "sources"}``, where ``experiment`` names
the run's stable identity (its case, sample or run directory) so a dry run, a
submission and a collection of one experiment share their QRNG values. The
ledger row that consumes a value, in docs/evidence/qrng_seeds/allocations.json,
lands in the change that retains the record, and ci/seed_provenance.py
requires every retained qrng reference to match exactly one ledger row.

The registry of sources lives here, so the CLIs and ci/seed_provenance.py
admit draws through one table.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
# The draw adapters live with the other provider scripts.
sys.path.insert(0, str(ROOT / "scripts"))

import anu_qrng  # noqa: E402
import outshift_qrng  # noqa: E402
import quandela_qrng  # noqa: E402

# Each QRNG source's retained draw directory and the function that admits one of its records.
SOURCES: dict[str, Callable[[dict[str, Any]], None]] = {
    "docs/evidence/anu_qrng": anu_qrng.admit,
    "docs/evidence/outshift_qrng": outshift_qrng.admit,
    "docs/evidence/quandela_qrng": quandela_qrng.admit,
}
DRAW_NAME = re.compile(r"draw-\d{4}-\d{2}-\d{2}T\d{6}Z\.json")
REF = re.compile(r"qrng:(docs/evidence/[a-z_]+/draw-\d{4}-\d{2}-\d{2}T\d{6}Z\.json)#(\d+)")
REPRO = re.compile(r"repro:(-?\d+)")


class SeedSourceError(ValueError):
    pass


def source_directory(record_path: str) -> str:
    """The registered directory of a canonically spelled draw path."""
    directory, _, name = record_path.rpartition("/")
    if not DRAW_NAME.fullmatch(name) or directory not in SOURCES:
        raise SeedSourceError(f"record {record_path!r} is not spelled <source directory>/draw-<UTC>.json")
    return directory


def read_record(record_path: str, root: Path = ROOT) -> dict[str, Any]:
    directory = source_directory(record_path)
    record: dict[str, Any] = json.loads((root / record_path).read_text(encoding="utf-8"))
    SOURCES[directory](record)
    return record


def resolve(ref: str, root: Path = ROOT) -> tuple[int, str, int]:
    """(value, record path, index) of a ``qrng:`` reference to an admitted draw."""
    match = REF.fullmatch(ref)
    if match is None:
        raise SeedSourceError(f"{ref!r} is not qrng:<source directory>/draw-<UTC>.json#<index>")
    record_path, index = match.group(1), int(match.group(2))
    values = read_record(record_path, root)["values"]
    if index >= len(values):
        raise SeedSourceError(f"{ref}: the draw holds {len(values)} values")
    return values[index], record_path, index


def parse_value(text: str, defaults: Sequence[int], root: Path = ROOT) -> tuple[int, str]:
    """(seed, spelling) of one flag value."""
    if text.startswith("qrng:"):
        return resolve(text, root)[0], text
    if match := REPRO.fullmatch(text):
        return int(match.group(1)), text
    try:
        value = int(text)
    except ValueError:
        raise SeedSourceError(f"{text!r} is neither qrng:<draw>#<index>, repro:<integer> nor an integer") from None
    if value not in defaults:
        raise SeedSourceError(
            f"{value} is no default of this flag; take a new seed as qrng:<draw>#<index> "
            "(docs/notes/qrng/README.md) or mark a reproduction as repro:<integer>"
        )
    return value, "default"


class SeedAction(argparse.Action):
    """Stores plain integers under dest and each value's spelling under dest_source."""

    def __init__(self, *args: Any, seed_defaults: Sequence[int] = (), **kwargs: Any) -> None:
        self.seed_defaults = tuple(seed_defaults)
        super().__init__(*args, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        texts = values if isinstance(values, list) else [values]
        try:
            parsed = [parse_value(text, self.seed_defaults) for text in texts]
        except SeedSourceError as error:
            parser.error(f"{option_string}: {error}")
        seeds = [seed for seed, _ in parsed]
        sources = [source for _, source in parsed]
        setattr(namespace, self.dest, seeds if isinstance(values, list) else seeds[0])
        setattr(namespace, f"{self.dest}_source", sources if isinstance(values, list) else sources[0])


def add_seed_argument(parser: argparse.ArgumentParser, *flags: str, default: Any = None, **kwargs: Any) -> None:
    """Declare a seed flag; default is the integer (or list of integers) the code already holds, or None."""
    if "type" in kwargs or "action" in kwargs:
        raise SeedSourceError("a seed flag parses its own values")
    defaults = list(default) if isinstance(default, list | tuple) else ([] if default is None else [default])
    action = parser.add_argument(*flags, action=SeedAction, default=default, seed_defaults=defaults, **kwargs)
    is_list = kwargs.get("nargs") in ("+", "*")
    source = ["default"] * len(defaults) if is_list else (None if default is None else "default")
    parser.set_defaults(**{f"{action.dest}_source": source})


def seed_record(script: str, flag: str, experiment: str, source: str | list[str] | None) -> dict[str, Any]:
    """The seed_source entry of a run record."""
    sources = source if isinstance(source, list) else [source]
    return {"script": script, "flag": flag, "experiment": experiment, "sources": sources}


def spellings(seeds: Sequence[int], sources: Sequence[str]) -> list[str]:
    """Command-line spellings of parsed seeds: a default value as its integer, any other as the spelling given."""
    return [str(seed) if source == "default" else source for seed, source in zip(seeds, sources, strict=True)]


def repo_relative(path: Path | str) -> str:
    """The repository-relative POSIX spelling of a path; outside the tree, its file name alone, since a record
    carries no local absolute path."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.name


def self_test() -> int:
    draw = sorted((ROOT / "docs/evidence/anu_qrng").glob("draw-*.json"))[-1]
    record_path = draw.relative_to(ROOT).as_posix()
    values = json.loads(draw.read_text(encoding="utf-8"))["values"]
    # The flag defaults are values of the retained draw, so the fixture holds no hand-picked seed.
    single, pair, value = values[0], values[3:5], values[2]
    parser = argparse.ArgumentParser(exit_on_error=False)
    add_seed_argument(parser, "--seed", default=single)
    add_seed_argument(parser, "--seeds", nargs="+", default=pair)
    args = parser.parse_args([])
    if (args.seed, args.seed_source, args.seeds, args.seeds_source) != (single, "default", pair, ["default"] * 2):
        raise SystemExit(f"self-test: defaults parsed as {vars(args)}")
    ref = f"qrng:{record_path}#2"
    repro = f"repro:{single + 1}"
    args = parser.parse_args(["--seed", ref, "--seeds", str(pair[0]), repro])
    if (args.seed, args.seed_source) != (value, ref) or (args.seeds, args.seeds_source) != (
        [pair[0], single + 1],
        ["default", repro],
    ):
        raise SystemExit(f"self-test: values parsed as {vars(args)}")
    refusals = {
        "a bare non-default integer": str(single + 1),
        "an unregistered directory": "qrng:docs/evidence/elsewhere/draw-2026-01-01T000000Z.json#0",
        "an index past the draw": f"qrng:{record_path}#{len(values)}",
        "a malformed reference": f"qrng:./{record_path}#0",
    }
    for name, text in refusals.items():
        try:
            parse_value(text, [single])
        except SeedSourceError:
            continue
        raise SystemExit(f"self-test: {name} was admitted")
    if (
        repo_relative(ROOT / "results" / "x") != "results/x"
        or repo_relative(ROOT.parent / "elsewhere.json") != "elsewhere.json"
    ):
        raise SystemExit("self-test: repo_relative leaked a path outside the tree")
    record = seed_record("scripts/x.py", "--seed", "case-a", ref)
    if record["sources"] != [ref]:
        raise SystemExit(f"self-test: seed_record wrote {record}")
    print(f"qrng_seeds self-test: three spellings parsed, {len(refusals)} refusals")
    return 0


if __name__ == "__main__":
    sys.exit(self_test())
