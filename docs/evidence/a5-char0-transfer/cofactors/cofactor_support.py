"""Compare the supports of two modular lift cofactor matrices of the X- -> N- degree-2 relations.

Conjecture: lift(Q, Rel) at the split primes 32009 and 32029 follows one computation over Q(i), so every entry of
the cofactor matrix T has the same monomial support at both primes, and the coefficients can be reconstructed over
Z[i]. Falsifier: an entry whose supports differ at the two primes; a reconstruction route then needs a canonical
solution (the reduced row echelon form of a degree-bounded linear system). Mutation: removing one term from one entry
of the first matrix must be detected. Singular writes T row by row as comma-separated polynomials (`short=0`).
Run from the repository root: "$PYTHON" docs/evidence/a5-char0-transfer/cofactors/cofactor_support.py
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TERM = re.compile(r"(?=[+-])")


def _supports(path: Path) -> list[frozenset[str]]:
    entries = path.read_text(encoding="utf-8").replace("\n", "").split(",")
    supports = []
    for entry in entries:
        monomials = set()
        for term in TERM.split(entry.strip()):
            if not term or term == "0":
                continue
            match = re.match(r"^[+-]?\d*\*?(.*)$", term)
            if match is None:
                raise SystemExit(f"unparsed term {term!r} in {path}")
            monomials.add(match.group(1) or "1")
        supports.append(frozenset(monomials))
    return supports


def main() -> None:
    first = _supports(HERE / "cofactors-xm-nm-p32009.txt")
    second = _supports(HERE / "cofactors-xm-nm-p32029.txt")
    if len(first) != len(second):
        raise SystemExit(f"entry counts differ: {len(first)} against {len(second)}")
    differing = [index for index, (a, b) in enumerate(zip(first, second, strict=True)) if a != b]
    nonzero = next(index for index, support in enumerate(first) if support)
    mutated = list(first)
    mutated[nonzero] = frozenset(sorted(first[nonzero])[1:])
    record = {
        "conjecture": "the modular lift cofactors of X- -> N- have one support at 32009 and 32029",
        "entries": len(first),
        "terms_32009": sum(len(s) for s in first),
        "terms_32029": sum(len(s) for s in second),
        "differing_entries": len(differing),
        "first_differing": differing[:10],
        "mutation_detected": mutated[nonzero] != second[nonzero],
        "verdict": "survives" if not differing else "refuted",
    }
    (HERE / "cofactor-support-xm-nm.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    json.dump(record, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
