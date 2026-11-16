"""Verdict of the modular Rees fiber certificates of E8-bar -> N-, E8-bar -> N+ and Iso -> N- at p = 32009.

No Singular runs. The check reads the four retained Singular logs of this directory and decides, for each, that the
run ended with exit 0 and printed every certificate line the script prints, that the fiber-cone ideal it computed is
the quadric ideal K of its own relations, and that the Hilbert numerator it printed has the dimension and multiplicity
the FIBER line states. It then ties the logs to the retained weight-slice record: the relation lines of the N- log
hash to the digest of the record's cell at 32009, and the selection, generator weights and Hilbert numerator of both
E8-bar logs and the Iso numerator equal the record's. Each log's relations are linearly independent over F_32009.
Run from docs/evidence/a5-exceptional-fibers:

    python -B working/runs/e8-rees-fibers-v2-p32009/check_rees_fibers.py [--self-test]

`--self-test` feeds known-bad variants of the retained Iso log to the same verdict and requires each to fail.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PRIME = 32009
SINGULAR_VERSION = "Singular for x86_64-Linux version 4.4.1 (44105, 64 bit) Dec  6 2025 11:10:58"
WEIGHT_SLICE = ROOT / "docs" / "evidence" / "a5-kernel-attachments" / "weight-slice-fiber-relations-result.json"
# name: (ambient variables y, bound of the FIBER line, quadric count, dimension, multiplicity)
RUNS: dict[str, tuple[int, int, int, int, int]] = {
    "e8-nm-p.v2-u-full": (21, 0, 148, 5, 11),
    "e8-np-p.v2-u-full": (21, 0, 148, 5, 11),
    "e8-nm-p.v2-u-y2": (21, 2, 148, 5, 11),
    "iso-nm-p.v2-u-full": (17, 0, 68, 5, 23),
}
FAIL_MARKERS = ("CERT FAIL", "ELIM FAIL", "error", "Error", "** Error")


def _ints(text: str) -> list[int]:
    return [int(token) for token in text.split(",") if token.strip()]


def _single(lines: list[str], prefix: str) -> list[str]:
    found = [line[len(prefix) :].split() for line in lines if line.startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"{len(found)} lines start with {prefix!r}, expected one")
    return found[0]


def hilbert_valuation(numerator: list[int]) -> tuple[int, int]:
    """The multiplicity of the root t = 1 of the polynomial and the value of the cofactor there."""
    poly = list(numerator)
    order = 0
    while True:
        value = sum(poly)
        if value != 0:
            return order, value
        # synthetic division by (1 - t): q_k = sum of the first k + 1 coefficients, exact when the sum vanishes
        quotient: list[int] = []
        running = 0
        for coefficient in poly[:-1]:
            running += coefficient
            quotient.append(running)
        poly = quotient
        order += 1
        if not poly:
            raise ValueError("the numerator is zero")


def relation_lines(text: str) -> list[str]:
    return sorted("RELATION" + line[3:] for line in text.split("\n") if line.startswith("REL "))


def relations_digest(text: str) -> str:
    return hashlib.sha256(("\n".join(relation_lines(text)) + "\n").encode()).hexdigest()


def log_vectors(text: str) -> list[dict[tuple[int, int], int]]:
    rows: list[dict[tuple[int, int], int]] = []
    for line in text.split("\n"):
        if not line.startswith("REL "):
            continue
        row: dict[tuple[int, int], int] = {}
        for token in line[4:].split():
            monomial, coefficient = token.split(":")
            first, second = (int(x) for x in monomial.split(","))
            key = (min(first, second), max(first, second))
            row[key] = row.get(key, 0) + int(coefficient) % PRIME
        rows.append({key: value % PRIME for key, value in row.items() if value % PRIME})
    return rows


def reduced_rows(rows: list[dict[tuple[int, int], int]]) -> list[tuple[tuple[tuple[int, int], int], ...]]:
    """The reduced row echelon form over F_p, as sorted tuples; equal forms mean equal row spaces."""
    basis: dict[tuple[int, int], dict[tuple[int, int], int]] = {}
    for original in rows:
        row = dict(original)
        for pivot in sorted(basis):
            if pivot in row:
                factor = row[pivot]
                for key, value in basis[pivot].items():
                    row[key] = (row.get(key, 0) - factor * value) % PRIME
                    if row[key] == 0:
                        del row[key]
        if not row:
            continue
        pivot = min(row)
        inverse = pow(row[pivot], -1, PRIME)
        row = {key: value * inverse % PRIME for key, value in row.items()}
        for other in basis:
            if pivot in basis[other]:
                factor = basis[other][pivot]
                for key, value in row.items():
                    basis[other][key] = (basis[other].get(key, 0) - factor * value) % PRIME
                    if basis[other][key] == 0:
                        del basis[other][key]
        basis[pivot] = row
    return [tuple(sorted(basis[pivot].items())) for pivot in sorted(basis)]


def masked(text: str) -> list[str]:
    """The log lines with the Singular timer (the last integer of a STAGE line and of the colon certificate) masked."""
    return [
        line.rsplit(" ", 1)[0] + " T" if line.startswith(("STAGE ", "CERT colon_equal_after_iterations")) else line
        for line in text.split("\n")
    ]


def replay_problems() -> list[str]:
    """The replay on a second host: equal logs up to the timers and equal basis digests, and the X- calibration pair."""
    problems: list[str] = []
    replay = HERE / "replay"
    for name in ("iso-nm-p.v2-u-full", "e8-nm-p.v2-u-y2"):
        if masked((replay / f"{name}.log").read_text()) != masked((HERE / f"{name}.log").read_text()):
            problems.append(f"{name}: the replay log differs from the retained log beyond the timers")
        if "Exit status: 0" not in (replay / f"{name}.time").read_text():
            problems.append(f"{name}: the replay time record lacks Exit status: 0")
    original = {
        parts[1]: parts[0] for parts in (line.split() for line in (HERE / "bases.sha256").read_text().splitlines())
    }
    again = {
        parts[1]: parts[0] for parts in (line.split() for line in (replay / "ssi.sha256").read_text().splitlines())
    }
    compared = sorted(name for name in again if name in original)
    if compared != sorted(n for n in original if n.startswith(("iso-", "e8-nm-p.v2-u-y2"))):
        problems.append("the replay does not reproduce the basis files of the Iso and bounded runs")
    for name in compared:
        if original[name] != again[name]:
            problems.append(f"{name}: the replayed basis differs from the original digest")
    good = (replay / "xm-nm-p.v2-u-full.log").read_text().split("\n")
    bad = (replay / "xm-nm-p.v2-u-full-badcontrol.log").read_text().split("\n")
    if (
        "FIBER bound 0 minimal generators 69 dim 4 mult 12" not in good
        or "FIBER outside_K 0 K_outside_fiber 0" not in good
    ):
        problems.append("the X- calibration run does not read 69 generators, dimension 4, multiplicity 12, K equal")
    if "FIBER outside_K 0 K_outside_fiber 0" in bad or not any(line.startswith("FIBER outside_K") for line in bad):
        problems.append("the X- known-bad control is not rejected by the fiber comparison")
    return problems


def log_verdict(name: str, text: str, sing_sha256: str) -> list[str]:
    """The problems of one log against the expectations of RUNS; an empty list is a pass."""
    ambient, bound, quadrics, dimension, multiplicity = RUNS[name]
    problems: list[str] = []
    lines = text.split("\n")
    if lines[0] != SINGULAR_VERSION:
        problems.append("the first line is not the Singular 4.4.1 banner")
    if lines[1] != f"{sing_sha256}  {name}.sing":
        problems.append("the second line does not bind the retained script digest")
    if [line for line in lines if line.startswith("EXIT ")] != ["EXIT 0"] or [x for x in lines if x][-1] != "EXIT 0":
        problems.append("the log does not end with exactly one EXIT 0")
    for marker in FAIL_MARKERS:
        if any(marker in line and "redefining" not in line for line in lines):
            problems.append(f"the log holds {marker!r}")
    try:
        unit = _single(lines, "CERT unit_identity_bad")
        if unit != ["0", "all_positive_degree", "1"]:
            problems.append(f"unit certificate reads {unit}")
        if _single(lines, "CERT pivot_nonzerodivisor_mod_J") != ["1"]:
            problems.append("the pivot is not certified a nonzerodivisor")
        saturation = _single(lines, "CERT satstd_isSB")
        if saturation[0] != "1" or saturation[1] != "leading_u_bad":
            problems.append(f"saturation certificate reads {saturation}")
        leading_u = int(saturation[2])
        colon = [line for line in lines if line.startswith("CERT colon_equal_after_iterations")]
        if leading_u > 0 and len(colon) != 1:
            problems.append("a basis with u in a leading term lacks its colon certificate")
        if leading_u == 0 and colon:
            problems.append("a colon certificate follows a basis with no u in a leading term")
        known = _single(lines, "K quadrics")
        if (
            int(known[0]) != quadrics
            or known[1] != "dim"
            or int(known[2]) != dimension
            or int(known[4]) != multiplicity
        ):
            problems.append(f"K reads {known}")
        relations = _single(lines, "RELATIONS")
        if int(relations[0]) != quadrics or len([x for x in lines if x.startswith("REL ")]) != quadrics:
            problems.append(f"relation count reads {relations}")
        if len(reduced_rows(log_vectors(text))) != quadrics:
            problems.append("the relations are linearly dependent")
        fiber = _single(lines, "FIBER bound")
        if (
            int(fiber[0]) != bound
            or fiber[1:3] != ["minimal", "generators"]
            or int(fiber[3]) != quadrics
            or int(fiber[5]) != dimension
            or int(fiber[7]) != multiplicity
        ):
            problems.append(f"FIBER reads {fiber}")
        degrees = _ints(_single(lines, "generator degrees")[0])
        if degrees != [2] * quadrics:
            problems.append("a minimal generator of the fiber ideal is not of degree 2")
        if _single(lines, "FIBER outside_K") != ["0", "K_outside_fiber", "0"]:
            problems.append("the fiber ideal and K differ")
        _single(lines, "STAGE rees_done")
    except (ValueError, IndexError) as error:
        problems.append(str(error))
        return problems
    if bound == 0:
        try:
            numerator = _ints(lines[lines.index("hilb") + 1])
        except (ValueError, IndexError):
            problems.append("no Hilbert numerator")
            return problems
        if numerator[-1] != 0:
            problems.append("the numerator lacks the trailing marker")
        numerator = numerator[:-1]
        order, cofactor = hilbert_valuation(numerator)
        if order != ambient - dimension or cofactor != multiplicity:
            problems.append(f"numerator gives dimension {ambient - order} and multiplicity {cofactor}")
        if numerator[:3] != [1, 0, -quadrics]:
            problems.append("the numerator does not start 1, 0, minus the quadric count")
    return problems


def check() -> list[str]:
    problems: list[str] = []
    record = json.loads(WEIGHT_SLICE.read_text())
    cell = next(c for c in record["cells"] if c["incidence"] == "E8bar->N-" and c["field"] == "GF(32009), i = 10754")
    texts: dict[str, str] = {}
    for name in RUNS:
        sing = HERE / f"{name}.sing"
        text = (HERE / f"{name}.log").read_text()
        texts[name] = text
        problems += [f"{name}: {p}" for p in log_verdict(name, text, hashlib.sha256(sing.read_bytes()).hexdigest())]
        if "Exit status: 0" not in (HERE / f"{name}.time").read_text():
            problems.append(f"{name}: the time record lacks Exit status: 0")
    if relations_digest(texts["e8-nm-p.v2-u-full"]) != cell["relations_sha256"]:
        problems.append("N- relations differ from the weight-slice record cell at 32009")
    selected = ",".join(str(x) for x in cell["selected_pfaffians_one_based"])
    weights = ",".join(str(x) for x in cell["generator_weights"])
    for name in ("e8-nm-p.v2-u-full", "e8-np-p.v2-u-full", "e8-nm-p.v2-u-y2"):
        if f"selected {selected}" not in texts[name] or f"generator weights {weights}" not in texts[name]:
            problems.append(f"{name}: selection or generator weights differ from the weight-slice record")
    numerators = [texts[n].split("\nhilb\n")[1].split("\n")[0] for n in ("e8-nm-p.v2-u-full", "e8-np-p.v2-u-full")]
    if numerators[0] != numerators[1]:
        problems.append("the N- and N+ Hilbert numerators differ")
    if numerators[0] != ",".join(str(x) for x in cell["hilbert"]["first_numerator"]) + ",0":
        problems.append("the Hilbert numerator differs from the weight-slice record")
    iso = next(c for c in record["cells"] if c["incidence"] == "Iso->N-" and c["field"] == "Q(i)")
    iso_numerator = texts["iso-nm-p.v2-u-full"].split("\nhilb\n")[1].split("\n")[0]
    if iso_numerator != ",".join(str(x) for x in iso["hilbert"]["first_numerator"]) + ",0":
        problems.append("the Iso Hilbert numerator differs from the weight-slice record")
    problems += replay_problems()
    listed = {}
    for line in (HERE / "sha256.txt").read_text().splitlines():
        digest, _, path = line.partition("  ")
        listed[path.removeprefix("./")] = digest
    retained = sorted(
        str(p.relative_to(HERE))
        for p in HERE.rglob("*")
        if p.is_file() and p.name != "sha256.txt" and "__pycache__" not in p.parts
    )
    if sorted(listed) != retained:
        problems.append("sha256.txt does not list exactly the retained files")
    for path, digest in listed.items():
        if hashlib.sha256((HERE / path).read_bytes()).hexdigest() != digest:
            problems.append(f"{path}: digest differs from sha256.txt")
    return problems


def self_test() -> list[str]:
    """Known-bad variants of the retained Iso run; each must fail the verdict that the retained run passes."""
    name = "iso-nm-p.v2-u-full"
    text = (HERE / f"{name}.log").read_text()
    digest = hashlib.sha256((HERE / f"{name}.sing").read_bytes()).hexdigest()
    problems = [f"known-good rejected: {p}" for p in log_verdict(name, text, digest)]
    mutants = {
        "outside_K": text.replace("FIBER outside_K 0 K_outside_fiber 0", "FIBER outside_K 1 K_outside_fiber 0"),
        "exit": text.replace("EXIT 0", "EXIT 1"),
        "pivot": text.replace("CERT pivot_nonzerodivisor_mod_J 1", "CERT pivot_nonzerodivisor_mod_J 0"),
        "unit": text.replace("CERT unit_identity_bad 0", "CERT unit_identity_bad 2"),
        "saturation": text.replace("CERT satstd_isSB 1", "CERT satstd_isSB 0"),
        "colon": text.replace("CERT colon_equal_after_iterations 0 14\n", ""),
        "multiplicity": text.replace(
            "FIBER bound 0 minimal generators 68 dim 5 mult 23", "FIBER bound 0 minimal generators 68 dim 5 mult 22"
        ),
        "numerator": text.replace("1,0,-68,452,", "1,0,-68,453,"),
        "generator degree": text.replace("generator degrees 2,2", "generator degrees 2,3"),
        "relation": text.replace("REL 1,5:-1 2,4:1\n", ""),
        "duplicate relation": text.replace("REL 1,5:-1 2,4:1\n", "REL 1,8:-2 2,5:1\n"),
        "script digest": text.replace(digest, "0" * 64),
        "failure line": text.replace("EXIT 0", "CERT FAIL saturation\nEXIT 0"),
    }
    for label, mutant in mutants.items():
        if mutant == text:
            problems.append(f"mutation {label!r} changed nothing")
        elif not log_verdict(name, mutant, digest):
            problems.append(f"mutation {label!r} was accepted")
    print("RESULT self_test mutations", len(mutants))
    return problems


def main(argv: list[str]) -> int:
    problems = self_test() if argv == ["--self-test"] else check()
    for problem in problems:
        print("PROBLEM", problem)
    print("RESULT", "fail" if problems else "pass")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
