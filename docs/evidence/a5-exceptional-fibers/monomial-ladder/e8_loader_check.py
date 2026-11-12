"""Loader agreement of the four E8 target records at order 4, written or compared byte for byte.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_loader_check.py --check \
        docs/evidence/a5-exceptional-fibers/monomial-ladder/target-records/loader-check.json
    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_loader_check.py --write PATH

For each registered target (both signs, both primes) the check repeats the input stage of `e8_target_rank.run`
without the Singular export or the rank computation: the registry root and sign agree with e8_ladder, the header's J
and ordered G agree with the ladder module's parser, every input digest binds (`bound_inputs`), and the 21
generators substituted into the quadratic algebra at precision 4 are the ones e8_ladder.generators returns after
checking that all 16 J vanish on the shifted parametrization. A disagreement raises instead of writing a record.
The record names the sha256 of the four sources it ran, and `--check` compares the whole file bytes with a fresh
record, so a change of any source, input or target registry shows as a difference.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e8_target_rank as rank  # noqa: E402

ORDER = 4
SCOPE = "Positive source/loader agreement and shifted generators at order 4; no full rank run."


def check_target(target: Any) -> dict[str, Any]:
    lad = rank.ring_module()
    slug = "e8-nm" if target.sign9 == 1 else "e8-np"
    inputs = rank.bound_inputs(target)
    agree = lad.limits.PRIMES[target.prime] == target.root and lad.SIGN[slug] == target.sign9
    variables, ideal_j, ideal_g = lad.limits.header(slug, target.prime)
    normalized = tuple([[re.sub(r"\s", "", polynomial) for polynomial in ideal] for ideal in (ideal_j, ideal_g)])
    agree = agree and normalized == rank.targets.header_ideals(target)
    ring = lad.Ring(target.prime, ORDER)
    generators = lad.generators(slug, ring)  # raises unless every J vanishes modulo n^ORDER
    return {
        "G_count": len(generators),
        "J_count": len(ideal_j),
        "J_vanishes_on_shifted_parametrization_modulo_n_order": True,
        "bound_input_count": len(inputs),
        "minimum_G_valuation_at_precision": min(rank.valuation(g, ORDER) for g in generators),
        "nonzero_G_count_at_precision": sum(1 for g in generators if g[0] or g[1]),
        "order": ORDER,
        "prime": target.prime,
        "root": target.root,
        "root_sign_ordered_header_agree": agree,
        "sign9": target.sign9,
        "slice_variables": list(variables),
        "slug": slug,
        "status": "passed" if agree else "failed",
        "target": target.name,
    }


def build() -> dict[str, Any]:
    cases = [check_target(rank.targets.TARGETS[name]) for name in sorted(rank.targets.TARGETS)]
    failed = [case["target"] for case in cases if case["status"] != "passed"]
    if failed:
        raise ValueError(f"loader disagreement on {failed}")
    lad = rank.ring_module()
    paths = [Path(rank.targets.__file__), Path(lad.limits.__file__), Path(lad.__file__), Path(rank.__file__)]
    return {
        "cases": cases,
        "python": platform.python_version(),
        "scope": SCOPE,
        "source_sha256": {p.resolve().relative_to(rank.ROOT).as_posix(): rank.digest(p) for p in paths},
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = render(build())
    if args.write:
        args.write.write_text(text, encoding="utf-8")
    elif args.check.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{args.check} differs from a fresh loader check")


if __name__ == "__main__":
    main()
