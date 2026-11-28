"""Zero-dimensional linear sections of the E8-bar closure ideal modulo 32009 with a Frobenius-orbit test (A5-673).

Y is the 37-generator E8-bar closure ideal in the 15 split coordinates (dimension 11, multiplicity 24 modulo 32009,
root of -1 = 10754), taken from the line "ideal Y=" that the retained producer
pfaffian-boost-derivation-stability/derivation_stability.py emits in its rad mode, which is run, not edited. A section
substitutes z = b + A w for a random 15 x 4 matrix A and 15-vector b over F_p, so Y(b + A w) is an ideal in four
variables w. Singular 4.4.1 computes its dimension, vdim, the vdim of its radical, and the eliminant of a random linear
form ell(w) (eliminate on (Y(b + A w), t - ell)), whose factorization over F_p gives the Frobenius orbits of the
points: an irreducible factor of degree d is one orbit of length d.

Prediction and decision rule, written before the first run: K = 5 sections. The test supports the claim when every
section has dimension 0, vdim 24, radical vdim 24 and a squarefree eliminant of degree 24, the proper sub-sums
(1..23) of the orbit lengths have an empty intersection over the five sections, and the orbit lengths have gcd 1.
Any other outcome is inconclusive, not a refutation. Inference: if the top-dimensional part of V(Y) were a union of
two F_p-defined pieces of degrees d and 24 - d, every section in general position would have d as a sub-sum; an empty
intersection excludes that. If it were F_p-irreducible but split into m > 1 conjugate geometric components, every
Frobenius orbit of a general section would have length divisible by m; gcd 1 excludes that. Radical vdim = vdim = 24
on a section in general position excludes a top component along which Y is not reduced. The inference rests on the
sections being in general position (a random choice over F_p, not a proof of genericity); embedded and lower-dimensional
components are outside its reach, and characteristic 0 is not addressed.

Seeds: docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json, indices 16, 17, 18, 19, 20 in order, one per section,
each seeding random.Random for that section's A, b and ell.

Control (recorded and in --self-test): the same sections of Y * (z_1, z_2, z_3, z_4), whose top-dimensional part adds a
linear 11-space of degree 1, read 25 points with an orbit of length 1 in every section, so 1 is a common sub-sum and the
rule rejects irreducibility.

Usage:
    "$PYTHON" -B -W error scripts/a5_e8bar_sections.py --self-test
    "$PYTHON" -B -W error scripts/a5_e8bar_sections.py --out docs/evidence/a5-e8bar-sections/result.json
    "$PYTHON" -B -W error scripts/a5_e8bar_sections.py --check docs/evidence/a5-e8bar-sections/result.json
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import tempfile
from functools import cache, reduce
from math import gcd
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

PRIME = 32009
ROOT_OF_MINUS_ONE = 10754
DEGREE = 24
PRODUCER = (
    ROOT
    / "docs/evidence/a5-exceptional-fibers/working/runs/pfaffian-boost-derivation-stability/derivation_stability.py"
)
ATTACHMENTS = ROOT / "docs/evidence/a5-kernel-attachments"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json"
SECTION_SEEDS = (44408, 9137, 10742, 16920, 9989)
SEED_INDICES = (16, 17, 18, 19, 20)
MUTANT_FACTOR = "z(1),z(2),z(3),z(4)"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


@cache
def closure_ideal() -> str:
    """The generator list of the E8-bar closure ideal, as the producer's rad mode prints it."""
    out = subprocess.run(
        [sys.executable, "-B", str(PRODUCER), str(ATTACHMENTS), str(PRIME), str(ROOT_OF_MINUS_ONE), "rad"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    lines = [line for line in out.splitlines() if line.startswith("ideal Y=")]
    require(len(lines) == 1, "the producer printed no single ideal Y line")
    return lines[0][len("ideal Y=") : -1]


def section(seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    a = [[rng.randrange(PRIME) for _ in range(4)] for _ in range(15)]
    b = [rng.randrange(PRIME) for _ in range(15)]
    ell = [rng.randrange(PRIME) for _ in range(4)]
    return {"a": a, "b": b, "ell": ell}


def singular_script(gens: str, sec: dict[str, Any]) -> str:
    images = ",".join(f"{sec['b'][r]}" + "".join(f"+{sec['a'][r][c]}*w({c + 1})" for c in range(4)) for r in range(15))
    ell = "+".join(f"{sec['ell'][c]}*w({c + 1})" for c in range(4))
    return "\n".join(
        [
            'LIB "primdec.lib";',
            f"ring R={PRIME},(z(1..15)),dp; number I={ROOT_OF_MINUS_ONE};",
            f"ideal Y={gens};",
            f"ring S={PRIME},(w(1..4)),dp;",
            f"map phi=R,{images};",
            "ideal Ys=phi(Y); ideal G=std(Ys);",
            '"RESULT dim",dim(G); "RESULT vdim",vdim(G);',
            'ideal Rd=radical(Ys); "RESULT rad_vdim",vdim(std(Rd));',
            f"ring T={PRIME},(t,w(1..4)),dp;",
            f"ideal E=eliminate(imap(S,Ys)+ideal(t-({ell})),w(1)*w(2)*w(3)*w(4));",
            'poly f=E[1]; "RESULT eliminant",size(E),deg(f);',
            "list F=factorize(f); int k;",
            'for(k=2;k<=size(F[1]);k++){ "RESULT factor",deg(F[1][k]),F[2][k]; }',
            '"RESULT done"; quit;',
        ]
    )


def run_section(job: tuple[int, str]) -> dict[str, Any]:
    """One section: Singular on Y (or the mutant ideal) at the section drawn from the seed."""
    seed, gens = job
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "section.sing"
        path.write_text(singular_script(gens, section(seed)), encoding="utf-8")
        out = subprocess.run(
            ["Singular", "-q", "--no-warn", "--no-rc", str(path)],
            check=True,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        ).stdout
    vals: dict[str, list[list[int]]] = {}
    for line in out.splitlines():
        m = re.match(r"^RESULT (\w+)\s*(.*)$", line.strip())
        if m:
            vals.setdefault(m.group(1), []).append([int(x) for x in m.group(2).split()])
    require("done" in vals, "Singular did not finish the section")
    factors = sorted(vals.get("factor", []))
    return {
        "seed": seed,
        "dim": vals["dim"][0][0],
        "vdim": vals["vdim"][0][0],
        "rad_vdim": vals["rad_vdim"][0][0],
        "eliminant_generators": vals["eliminant"][0][0],
        "eliminant_degree": vals["eliminant"][0][1],
        "orbits": sorted(d for d, mult in factors for _ in range(mult)),
        "squarefree": all(mult == 1 for _, mult in factors),
    }


def sub_sums(parts: list[int]) -> set[int]:
    sums = {0}
    for p in parts:
        sums |= {s + p for s in sums}
    total = sum(parts)
    return {s for s in sums if 0 < s < total}


def decide(rows: list[dict[str, Any]], degree: int) -> dict[str, Any]:
    """The rule of the docstring on a list of section rows."""
    clean = all(
        r["dim"] == 0
        and r["vdim"] == degree
        and r["rad_vdim"] == degree
        and r["eliminant_generators"] == 1
        and r["eliminant_degree"] == degree
        and r["squarefree"]
        and sum(r["orbits"]) == degree
        for r in rows
    )
    common = sorted(set.intersection(*[sub_sums(r["orbits"]) for r in rows])) if rows else []
    lengths_gcd = reduce(gcd, [d for r in rows for d in r["orbits"]], 0)
    return {
        "clean_sections": clean,
        "common_sub_sums": common,
        "orbit_gcd": lengths_gcd,
        "supports_irreducible_reduced": clean and not common and lengths_gcd == 1,
    }


def compute() -> dict[str, Any]:
    gens = closure_ideal()
    mutant = f"ideal({gens})*ideal({MUTANT_FACTOR})"
    jobs = [(s, gens) for s in SECTION_SEEDS] + [(s, mutant) for s in SECTION_SEEDS]
    rows = parallel.ordered_map(run_section, jobs, min_items=1)
    sections, controls = rows[: len(SECTION_SEEDS)], rows[len(SECTION_SEEDS) :]
    return {
        "ideal_generators": gens.count(",") + 1,
        "prime": PRIME,
        "seed_draw": DRAW,
        "seed_indices": list(SEED_INDICES),
        "sections": sections,
        "decision": decide(sections, DEGREE),
        "mutant_factor": MUTANT_FACTOR,
        "mutant_sections": controls,
        "mutant_decision": decide(controls, DEGREE + 1),
    }


def validate(result: dict[str, Any]) -> None:
    require(result["ideal_generators"] == 37, f"generator count {result['ideal_generators']}")
    require(len(result["sections"]) == 5, "section count")
    d = result["decision"]
    require(d["clean_sections"], "a section is not zero-dimensional, reduced and of length 24")
    require(not d["common_sub_sums"], f"common sub-sums {d['common_sub_sums']}")
    require(d["orbit_gcd"] == 1 and d["supports_irreducible_reduced"], "the rule does not support the claim")
    m = result["mutant_decision"]
    require(m["clean_sections"] and 1 in m["common_sub_sums"], "the reducible mutant passes the rule")
    require(not m["supports_irreducible_reduced"], "the reducible mutant is read as irreducible")


def self_test() -> None:
    def control(baseline: bool, mutant: bool, name: str) -> None:
        require(baseline and not mutant, f"control {name}: baseline {baseline}, mutant {mutant}")

    def row(orbits: list[int]) -> dict[str, Any]:
        n = sum(orbits)
        return {
            "dim": 0,
            "vdim": n,
            "rad_vdim": n,
            "eliminant_generators": 1,
            "eliminant_degree": n,
            "orbits": orbits,
            "squarefree": True,
        }

    good = [row([4, 20]), row([1, 3, 5, 7, 8]), row([2, 9, 13])]
    split = [row([1, 4, 20]), row([1, 1, 3, 5, 7, 8]), row([1, 2, 9, 13])]
    even = [row([2, 22]), row([4, 20]), row([6, 18])]
    control(
        decide(good, 24)["supports_irreducible_reduced"],
        decide(split, 25)["supports_irreducible_reduced"],
        "a common sub-sum",
    )
    control(decide(good, 24)["orbit_gcd"] == 1, decide(even, 24)["orbit_gcd"] == 1, "orbit gcd 2")
    gens = closure_ideal()
    base = run_section((SECTION_SEEDS[0], gens))
    mut = run_section((SECTION_SEEDS[0], f"ideal({gens})*ideal({MUTANT_FACTOR})"))
    control(base["vdim"] == DEGREE, mut["vdim"] == DEGREE, "the mutant section has 24 points")
    control(base["rad_vdim"] == DEGREE, 1 not in mut["orbits"], "the mutant section has a rational point")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("self-test: 4 paired controls pass")
        return 0
    result = compute()
    validate(result)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print("record differs from its recomputation", file=sys.stderr)
        return 1
    print("record matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
