"""Check the Albuquerque-Majid cochain convention against cd_core from the paper's own recursion.

Albuquerque and Majid, arXiv math/9802116v1, Corollary 4.3 doubles a cochain F = (-1)^f on (Z_2)^n to
(Z_2)^(n+1) by

    f-bar((x, x'), (y, y')) = f(x, y)(1 - x') + f(y, x) x' + y' f(x, x) + x' y'   (mod 2),

starting from the complex numbers, G = Z_2 with f(x, y) = xy. The new coordinate x' is the highest index bit,
which is cd_core's convention (bit n - 1 is the last doubling). This script builds F_AM from that recursion
alone and uses cd_core only as the comparison target. It requires

- F_AM(a, b) = cd_sign(n, b, a) on every basis pair, n = 2 to 64 (the declared transposed convention);
- the untransposed comparison F_AM(a, b) = cd_sign(n, a, b) to fail with the recorded disagreement counts,
  starting at n = 4, so the check detects an omitted transpose;
- the paper's associator phi(x, y, z) = F(x, y) F(x + y, z) / (F(y, z) F(x, y + z)), its Eq. (11), to equal the
  product of cd_core.triple_sign and to vanish exactly where cd_core.associator of three basis units is zero,
  n = 2 to 32. The associator is blind to the transpose, so this comparison stands beside the raw-cochain one.

derivation.json records the source identity, the bit convention, the coverage and the counts; --check
recomputes it and compares the bytes.

Usage: "$PYTHON" docs/evidence/albuquerque-majid-convention/am_convention_replay.py [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import associator, cd_sign, triple_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

BUNDLE = Path(__file__).resolve().parent
DERIVATION = BUNDLE / "derivation.json"
SOURCES = ROOT / "docs/SOURCES.json"
SOURCE_URL = "https://arxiv.org/pdf/math/9802116v1"
COCHAIN_DIMENSIONS = (2, 4, 8, 16, 32, 64)
ASSOCIATOR_DIMENSIONS = (2, 4, 8, 16, 32)
# Disagreements of the untransposed comparison: zero at n = 2, where the algebra is commutative.
UNTRANSPOSED_DISAGREEMENTS = {2: 0, 4: 6, 8: 42, 16: 210, 32: 930, 64: 3906}

Cochain = list[list[int]]


def doubled(f: Cochain) -> Cochain:
    """Corollary 4.3: the exponent table of F-bar on (Z_2)^(n+1), the new bit on top."""
    size = len(f)
    table = [[0] * (2 * size) for _ in range(2 * size)]
    for xt in (0, 1):
        for yt in (0, 1):
            for x in range(size):
                for y in range(size):
                    value = f[x][y] * (1 - xt) + f[y][x] * xt + yt * f[x][x] + xt * yt
                    table[x + xt * size][y + yt * size] = value % 2
    return table


def am_cochains() -> dict[int, Cochain]:
    """F_AM exponents for every dimension, from G = Z_2 with f(x, y) = xy."""
    f: Cochain = [[x * y for y in (0, 1)] for x in (0, 1)]
    tables = {2: f}
    while len(f) < max(COCHAIN_DIMENSIONS):
        f = doubled(f)
        tables[len(f)] = f
    return tables


def cochain_row(task: tuple[int, int, list[int]]) -> tuple[int, int]:
    """Disagreements of one F_AM row with the transposed and the untransposed repository sign."""
    n, a, row = task
    transposed = untransposed = 0
    for b, exponent in enumerate(row):
        sign = -1 if exponent else 1
        transposed += sign != cd_sign(n, b, a)
        untransposed += sign != cd_sign(n, a, b)
    return transposed, untransposed


def associator_row(task: tuple[int, int, Cochain]) -> tuple[int, int, int]:
    """For one x: triples, mismatches against triple_sign, and mismatches against the associator's support."""
    n, x, f = task
    units = [[float(i == k) for i in range(n)] for k in range(n)]
    sign_mismatches = support_mismatches = 0
    for y in range(n):
        for z in range(n):
            phi = (f[x][y] + f[x ^ y][z] + f[y][z] + f[x][y ^ z]) % 2
            left, right = triple_sign(n, x, y, z)
            sign_mismatches += (-1 if phi else 1) != left * right
            nonzero = any(value != 0.0 for value in associator(n, units[x], units[y], units[z]))
            support_mismatches += nonzero != bool(phi)
    return n * n, sign_mismatches, support_mismatches


def source_identity() -> dict[str, object]:
    """The registry record of the PDF the recursion was read from; the PDF itself stays outside the tree."""
    records = [
        record
        for record in json.loads(SOURCES.read_text(encoding="utf-8"))["external_pdfs"]
        if record.get("source_url") == SOURCE_URL
    ]
    if len(records) != 1:
        raise SystemExit(f"albuquerque-majid convention: {SOURCES.name} holds {len(records)} records of {SOURCE_URL}")
    return {"url": SOURCE_URL, "sha256": records[0]["sha256"], "bytes": records[0]["bytes"]}


def derivation() -> dict[str, object]:
    tables = am_cochains()
    cochain_tasks = [(n, a, tables[n][a]) for n in COCHAIN_DIMENSIONS for a in range(n)]
    cochain_counts = ordered_map(cochain_row, cochain_tasks)
    associator_tasks = [(n, x, tables[n]) for n in ASSOCIATOR_DIMENSIONS for x in range(n)]
    associator_counts = ordered_map(associator_row, associator_tasks)

    cochain: dict[str, dict[str, int]] = {}
    for (n, _, _), (transposed, untransposed) in zip(cochain_tasks, cochain_counts, strict=True):
        entry = cochain.setdefault(str(n), {"pairs": 0, "transposed_disagreements": 0, "untransposed_disagreements": 0})
        entry["pairs"] += n
        entry["transposed_disagreements"] += transposed
        entry["untransposed_disagreements"] += untransposed
    associators: dict[str, dict[str, int]] = {}
    for (n, _, _), (triples, sign_mismatches, support_mismatches) in zip(
        associator_tasks, associator_counts, strict=True
    ):
        entry = associators.setdefault(
            str(n), {"triples": 0, "triple_sign_disagreements": 0, "associator_support_disagreements": 0}
        )
        entry["triples"] += triples
        entry["triple_sign_disagreements"] += sign_mismatches
        entry["associator_support_disagreements"] += support_mismatches

    failures = [
        f"n = {n}: F_AM differs from transposed cd_sign" for n, e in cochain.items() if e["transposed_disagreements"]
    ]
    failures += [
        f"n = {n}: untransposed control gives {e['untransposed_disagreements']} disagreements, "
        f"expected {UNTRANSPOSED_DISAGREEMENTS[int(n)]}"
        for n, e in cochain.items()
        if e["untransposed_disagreements"] != UNTRANSPOSED_DISAGREEMENTS[int(n)]
    ]
    failures += [
        f"n = {n}: the Eq. (11) associator differs from cd_core"
        for n, e in associators.items()
        if e["triple_sign_disagreements"] or e["associator_support_disagreements"]
    ]
    # The first pair that separates the two conventions while their associators agree.
    witness = {"n": 4, "a": 1, "b": 2, "F_AM": -1 if tables[4][1][2] else 1, "cd_sign_a_b": cd_sign(4, 1, 2)}
    if (witness["F_AM"], witness["cd_sign_a_b"]) != (-1, 1):
        failures.append(f"the n = 4 witness reads {witness}")
    if failures:
        raise SystemExit("albuquerque-majid convention: " + "; ".join(failures))

    return {
        "schema": "albuquerque-majid-convention-v1",
        "source": {
            **source_identity(),
            "statements": ["Corollary 4.3 (cochain doubling)", "Eq. (11) (coboundary associator)"],
        },
        "convention": {
            "base": "G = Z_2, f(x, y) = xy",
            "new_generator": "highest index bit, cd_core's last doubling",
            "declared_map": "F_AM(a, b) = cd_sign(n, b, a)",
        },
        "cochain": cochain,
        "untransposed_witness": witness,
        "associator": associators,
        "totals": {
            "pairs": sum(e["pairs"] for e in cochain.values()),
            "triples": sum(e["triples"] for e in associators.values()),
        },
    }


def main(argv: list[str]) -> int:
    if argv not in ([], ["--check"]):
        raise SystemExit(
            'usage: "$PYTHON" docs/evidence/albuquerque-majid-convention/am_convention_replay.py [--check]'
        )
    text = json.dumps(derivation(), indent=1, sort_keys=True) + "\n"
    if argv == ["--check"]:
        if DERIVATION.read_text(encoding="utf-8") != text:
            raise SystemExit(f"albuquerque-majid convention: {DERIVATION.name} differs from the replay")
        return 0
    DERIVATION.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
