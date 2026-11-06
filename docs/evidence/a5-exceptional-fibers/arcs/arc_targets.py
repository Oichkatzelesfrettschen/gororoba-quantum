"""Targets of the arc certificates: prime, root of -1, sign of t9, header and K2 relation file, all repository-relative.

A target names one E8-bar -> N-/N+ fiber at one prime. Every input is read in place from the tracked working record;
the K2 relation file is bound to its digest in `k2-hilbert.jsonl` and the generator order of the relation run to the
header, so the coordinates y(1..21) of K2 are the generators G_1..G_21 of the header.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKAGE = Path(__file__).resolve().parent
EVIDENCE = PACKAGE.parent
ROOT = PACKAGE.parents[3]
WORKING = "docs/evidence/a5-exceptional-fibers/working"
NGEN = 21
NVAR = 9


@dataclass(frozen=True)
class Target:
    """One fiber at one prime.

    `sign9` multiplies the N- parametrization of t9: t9 = -sign9 (m-1)^2 / (2m), so +1 is the N- slice and -1 the N+
    slice. `root` satisfies root^2 = -1 modulo `prime`. `generators` names the file whose generator order the K2
    relation run used: a `gens.txt` list or the `input.sing` of the run.
    """

    name: str
    fiber: str
    prime: int
    root: int
    sign9: int
    header: str
    k2_relations: str
    generators: str

    @property
    def directory(self) -> Path:
        return PACKAGE / self.name

    @property
    def sign_label(self) -> str:
        return "-" if self.sign9 == 1 else "+"


def _target(name: str, fiber: str, prime: int, header: str, k2: str, gens: str) -> Target:
    root = {32009: 10754, 32029: 9115}[prime]
    if (root * root + 1) % prime:
        raise ValueError(f"{root} is not a square root of -1 modulo {prime}")
    inputs = {32009: "p32009-r10754", 32029: "p32029-r9115"}[prime]
    d2 = f"{WORKING}/distribute/out/a5-e8-d2"
    return Target(
        name=name,
        fiber=fiber,
        prime=prime,
        root=root,
        sign9=1 if fiber.endswith("N-") else -1,
        header=f"{WORKING}/build/inputs/{inputs}/{header}",
        k2_relations=k2.replace("D2", d2),
        generators=gens.replace("D2", d2),
    )


TARGETS: dict[str, Target] = {
    t.name: t
    for t in (
        _target(
            "e8nm-p32009",
            "E8-bar -> N-",
            32009,
            "e8-nm.sing",
            "D2/e8nm_p1/d2/relations-upto-d2.rel",
            "D2/e8nm_p1/d2/gens.txt",
        ),
        _target(
            "e8nm-p32029",
            "E8-bar -> N-",
            32029,
            "e8-nm.sing",
            "D2/e8nm_p2/d2/relations-upto-d2.rel",
            "D2/e8nm_p2/d2/gens.txt",
        ),
        _target(
            "e8np-p32009",
            "E8-bar -> N+",
            32009,
            "e8-np.sing",
            f"{WORKING}/runs/e8_a2/e8_k2.rel",
            f"{WORKING}/runs/e8_a2/input.sing",
        ),
        _target(
            "e8np-p32029",
            "E8-bar -> N+",
            32029,
            "e8-np.sing",
            "D2/e8np_p2/d2/relations-upto-d2.rel",
            "D2/e8np_p2/d2/gens.txt",
        ),
    )
}


def minus_partner(target: Target) -> Target | None:
    """The E8-bar -> N- target at the same prime for an N+ target, else None."""
    if target.sign9 == 1:
        return None
    return TARGETS[f"e8nm-p{target.prime}"]


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text()


def ideal_list(text: str, name: str) -> list[str]:
    """Generators of `ideal NAME=...;` in a Singular source, whitespace removed."""
    found = re.search(rf"ideal {name}=(.*?);", text, re.S)
    if found is None:
        raise ValueError(f"no ideal {name} in the source")
    return [g.replace(" ", "").replace("\n", "") for g in found.group(1).split(",")]


def header_ideals(target: Target) -> tuple[list[str], list[str]]:
    """The generators of J (16) and G (21) in the header, as strings."""
    text = read_text(target.header)
    return ideal_list(text, "J"), ideal_list(text, "G")


def k2_ideal(target: Target) -> str:
    """The 148 quadrics of K2 on one line, whitespace and the closing semicolon removed.

    Raises when the file's sha256 differs from `relations_sha256` of the matching row in `k2-hilbert.jsonl`.
    """
    path = ROOT / target.k2_relations
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = [json.loads(line) for line in (EVIDENCE / "k2-hilbert.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["fiber"] == target.fiber and r["prime"] == target.prime]
    if len(rows) != 1:
        raise ValueError(f"k2-hilbert.jsonl holds {len(rows)} rows for {target.name}")
    row = rows[0]
    if f"{WORKING}/{row['relations']}" != target.k2_relations:
        raise ValueError(f"{target.name}: relation path differs from k2-hilbert.jsonl")
    if row["relations_sha256"] != digest:
        raise ValueError(f"{target.name}: relation file digest {digest} differs from k2-hilbert.jsonl")
    return re.sub(r"\s", "", path.read_text()).rstrip(";")


def k2_hilbert_function(target: Target) -> dict[str, int]:
    """HF(k[y]/K2, d) for d = 1..6 from `k2-hilbert.jsonl`."""
    for line in (EVIDENCE / "k2-hilbert.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row["fiber"] == target.fiber and row["prime"] == target.prime:
            return dict(row["h"])
    raise ValueError(f"no k2-hilbert.jsonl row for {target.name}")


def check_generator_order(target: Target) -> str:
    """Raise unless the relation run lists G in the header's order; returns the provenance sentence."""
    _, g_header = header_ideals(target)
    text = read_text(target.generators)
    if target.generators.endswith("gens.txt"):
        listed = "".join(text.split()).rstrip(";").split(",")
        kind = "generator list"
    else:
        listed = ideal_list(text, "G")
        if ideal_list(text, "J") != header_ideals(target)[0]:
            raise ValueError(f"{target.name}: the J list of the relation run differs from the header")
        kind = "input"
    if listed != g_header:
        raise ValueError(f"{target.name}: the G list of the relation run differs from the header")
    return (
        f"the {kind} `{target.generators.removeprefix(WORKING + '/')}` of the relation run equals the header's G list"
    )


def load_primes(target: Target) -> tuple[str, str, str]:
    """(P1, P2, K2) generator lists as retained in the target directory and tracked inputs."""
    p1 = (target.directory / "P1.txt").read_text().strip()
    p2 = (target.directory / "P2.txt").read_text().strip()
    return p1, p2, k2_ideal(target)


def ordered_map(function: Callable[[Any], Any], items: Sequence[Any], min_items: int = 64) -> list[Any]:
    """parallel.ordered_map of the repository: results in input order; fewer than `min_items` run in this process."""
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    import parallel

    return list(parallel.ordered_map(function, items, min_items=min_items))
