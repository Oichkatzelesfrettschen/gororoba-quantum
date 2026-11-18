"""Verdict of the zero-generator guard run of the Iso -> N- Rees fiber at p = 32009, and of its toy run.

No Singular runs. The check reads the retained logs of this directory. `iso-nm-p.v3-u-full.sing` is the v2 Iso script
with three changes in four textual edits (a guard that prints `CERT FAIL unit_zero_generator` and quits on a zero
generator, the loop condition `uc!=0`, and a count line of generators with c(0) = 0); the check rebuilds it from the
retained v2 script and compares bytes. The Iso log must hold one `UNIT k c(0)=...` line per generator, the count line
`UNIT zero_constant_term_count 0`, and the results lines that the v2 verdict decides (the v2 verdict runs on the log
with line 2 renamed to the v2 script). The log must also equal the retained v2 Iso log beyond the script digest, the
script name, the Singular timers and the count line. The toy script (generators 0 and s1^2) must end with the failure
marker and no result line, and its control with the v2 loop must end with the timeout status 124 and no marker.
Run from docs/evidence/a5-exceptional-fibers:

    python -B working/runs/e8-rees-fibers-v3-p32009/check_rees_fibers_v3.py [--self-test]

`--self-test` feeds known-bad variants of the Iso log and of the toy log to the same verdict and requires each to fail.
"""

import hashlib
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
V2_DIR = HERE.parent / "e8-rees-fibers-v2-p32009"
ISO = "iso-nm-p.v3-u-full"
ISO_V2 = "iso-nm-p.v2-u-full"
TOY = "toy-zero-generator.v3"
CONTROL = "toy-zero-generator.v2-loop"
GENERATORS = 17
MARKER = "CERT FAIL unit_zero_generator"
COUNT = "UNIT zero_constant_term_count"
UNIT_LINE = re.compile(r"UNIT (\d+) c\(0\)=(-?\d+) c=\S+")
WALL = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\d+):(\d+\.\d+)")
# The four edits of the v2 Iso script, each (old, new) matching exactly once.
EDITS = [
    (
        "uc=gcd(uc,ucf[2,um]); }\n  while(subst(uc,s2,0)==0){ uc=uc/s2; }",
        'uc=gcd(uc,ucf[2,um]); }\n  if(uc==0){ "CERT FAIL unit_zero_generator"; quit; } '
        "while(uc!=0 and subst(uc,s2,0)==0){ uc=uc/s2; }",
    ),
    ("int ubadn=0; int upos=1;", "int ubadn=0; int upos=1; int uzero=0;"),
    (
        'if(deg(UCr[a])<=0){upos=0;} print("UNIT "',
        'if(deg(UCr[a])<=0){upos=0;} if(subst(UCr[a],s2,0)==0){uzero++;} print("UNIT "',
    ),
    ('"CERT unit_identity_bad",ubadn,', '"UNIT zero_constant_term_count",uzero; "CERT unit_identity_bad",ubadn,'),
]


def _load_v2() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_rees_fibers", V2_DIR / "check_rees_fibers.py")
    if spec is None or spec.loader is None:
        raise ImportError("check_rees_fibers.py of the v2 directory does not load")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v2 = _load_v2()


def _single(lines: list[str], prefix: str) -> list[str]:
    found = [line[len(prefix) :].split() for line in lines if line.startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"{len(found)} lines start with {prefix!r}, expected one")
    return found[0]


def successor_script(v2_script: str) -> str:
    """The v3 Iso script: the v2 script with each of the EDITS applied once."""
    text = v2_script
    for old, new in EDITS:
        if text.count(old) != 1:
            raise ValueError(f"{old!r} occurs {text.count(old)} times in the v2 script")
        text = text.replace(old, new)
    return text


def unit_problems(lines: list[str]) -> list[str]:
    """One UNIT line per generator with c(0) nonzero, and a count line that equals the number of zero c(0)."""
    rows = [match for match in (UNIT_LINE.fullmatch(line) for line in lines) if match]
    problems: list[str] = []
    if [int(match[1]) for match in rows] != list(range(1, GENERATORS + 1)):
        problems.append(f"the log lacks one UNIT line with c(0) for each of the {GENERATORS} generators")
    zero = [int(match[1]) for match in rows if int(match[2]) % v2.PRIME == 0]
    if zero:
        problems.append(f"generators {zero} have c(0) = 0")
    try:
        count = _single(lines, COUNT)
    except ValueError as error:
        problems.append(str(error))
    else:
        if count != [str(len(zero))]:
            problems.append(f"the count line reads {count}, the UNIT lines hold {len(zero)} generators with c(0) = 0")
        if count != ["0"]:
            problems.append("the count of generators with c(0) = 0 is not 0")
    return problems


def log_verdict(text: str, sing_sha256: str) -> list[str]:
    """The problems of the Iso log; an empty list is a pass."""
    lines = text.split("\n")
    if len(lines) < 3:
        return ["the log is shorter than its two header lines"]
    problems: list[str] = []
    if lines[1] != f"{sing_sha256}  {ISO}.sing":
        problems.append("the second line does not bind the retained script digest")
    if MARKER in lines:
        problems.append(f"a generator reduces to zero modulo J ({MARKER})")
    problems += unit_problems(lines)
    renamed = "\n".join([lines[0], f"{sing_sha256}  {ISO_V2}.sing", *lines[2:]])
    problems += v2.log_verdict(ISO_V2, renamed, sing_sha256)
    return problems


def _banner_problems(lines: list[str], name: str, sing_sha256: str) -> list[str]:
    problems: list[str] = []
    if lines[0] != v2.SINGULAR_VERSION:
        problems.append("the first line is not the Singular 4.4.1 banner")
    if lines[1] != f"{sing_sha256}  {name}.sing":
        problems.append("the second line does not bind the retained script digest")
    if any(line.startswith("FIBER") for line in lines):
        problems.append("the log holds a FIBER line")
    if "STAGE rees_start 0" not in lines:
        problems.append("the log lacks STAGE rees_start")
    return problems


def toy_problems(text: str, sing_sha256: str) -> list[str]:
    """The guarded toy run: the marker, then quit, with exit 0 and no result line."""
    lines = text.split("\n")
    problems = _banner_problems(lines, TOY, sing_sha256)
    if [line for line in lines if line.startswith("EXIT ")] != ["EXIT 0"] or [x for x in lines if x][-2:] != [
        MARKER,
        "EXIT 0",
    ]:
        problems.append("the toy log does not end with the failure marker and one EXIT 0")
    return problems


def control_problems(text: str, sing_sha256: str) -> list[str]:
    """The v2 loop on the toy ring: no marker, no result, and the timeout status 124."""
    lines = text.split("\n")
    problems = _banner_problems(lines, CONTROL, sing_sha256)
    if MARKER in lines:
        problems.append("the control log holds the failure marker")
    ends = [line for line in lines if line]
    if [line for line in lines if line.startswith("EXIT ")] != ["EXIT 124"] or ends[-1] != "EXIT 124":
        problems.append("the control log does not end with exactly one EXIT 124")
    return problems


def wall_seconds(time_record: str) -> float:
    match = WALL.search(time_record)
    if match is None:
        raise ValueError("the time record lacks the wall-clock line")
    return int(match[1]) * 60 + float(match[2])


def _compared(text: str, with_v2_name: bool) -> list[str]:
    lines = v2.masked(text)
    lines = [line for line in lines if not line.startswith(COUNT)]
    return [line.replace(ISO, ISO_V2) if with_v2_name else line for line in lines][2:]


def check() -> list[str]:
    problems: list[str] = []
    sing = {n: (HERE / f"{n}.sing").read_bytes() for n in (ISO, TOY, CONTROL)}
    digest = {n: hashlib.sha256(b).hexdigest() for n, b in sing.items()}
    v2_script = (V2_DIR / f"{ISO_V2}.sing").read_text()
    if successor_script(v2_script).encode() != sing[ISO]:
        problems.append(f"{ISO}.sing is not the v2 script with the listed edits")
    text = (HERE / f"{ISO}.log").read_text()
    problems += [f"{ISO}: {p}" for p in log_verdict(text, digest[ISO])]
    if _compared(text, True) != _compared((V2_DIR / f"{ISO_V2}.log").read_text(), False):
        problems.append(f"{ISO}: the log differs from the v2 Iso log beyond digest, name, timers and the count line")
    toy = (HERE / f"{TOY}.log").read_text()
    problems += [f"{TOY}: {p}" for p in toy_problems(toy, digest[TOY])]
    if not any(MARKER in p for p in log_verdict(toy, digest[TOY])):
        problems.append(f"{TOY}: the Iso verdict does not name the failure marker")
    problems += [f"{CONTROL}: {p}" for p in control_problems((HERE / f"{CONTROL}.log").read_text(), digest[CONTROL])]
    for name in (ISO, TOY, CONTROL):
        record = (HERE / f"{name}.time").read_text()
        wanted = "Exit status: 124" if name == CONTROL else "Exit status: 0"
        if wanted not in record:
            problems.append(f"{name}: the time record lacks {wanted}")
    if wall_seconds((HERE / f"{TOY}.time").read_text()) >= 1.0:
        problems.append(f"{TOY}: the toy run took one second or more")
    listed = {}
    for line in (HERE / "sha256.txt").read_text().splitlines():
        value, _, path = line.partition("  ")
        listed[path.removeprefix("./")] = value
    retained = sorted(
        str(p.relative_to(HERE))
        for p in HERE.rglob("*")
        if p.is_file() and p.name != "sha256.txt" and "__pycache__" not in p.parts
    )
    if sorted(listed) != retained:
        problems.append("sha256.txt does not list exactly the retained files")
    for path, value in listed.items():
        if hashlib.sha256((HERE / path).read_bytes()).hexdigest() != value:
            problems.append(f"{path}: digest differs from sha256.txt")
    return problems


def self_test() -> list[str]:
    """Known-bad variants of the retained logs; each must fail the verdict that the retained run passes."""
    text = (HERE / f"{ISO}.log").read_text()
    digest = hashlib.sha256((HERE / f"{ISO}.sing").read_bytes()).hexdigest()
    toy = (HERE / f"{TOY}.log").read_text()
    toy_digest = hashlib.sha256((HERE / f"{TOY}.sing").read_bytes()).hexdigest()
    problems = [f"known-good rejected: {p}" for p in log_verdict(text, digest)]
    problems += [f"known-good toy rejected: {p}" for p in toy_problems(toy, toy_digest)]
    toy_verdict = log_verdict(toy, toy_digest)
    if not any(MARKER in p for p in toy_verdict):
        problems.append("the toy log is not rejected with the marker named")
    mutants = {
        "no per-generator lines": re.sub(r"^UNIT \d+ c\(0\)=.*\n", "", text, flags=re.MULTILINE),
        "one per-generator line lost": text.replace("UNIT 17 c(0)=", "UNIT 18 c(0)="),
        "count line removed": text.replace(f"{COUNT} 0\n", ""),
        "count line nonzero": text.replace(f"{COUNT} 0", f"{COUNT} 1"),
        "zero constant term": text.replace("UNIT 1 c(0)=-10754", "UNIT 1 c(0)=0"),
        "marker": text.replace("EXIT 0", f"{MARKER}\nEXIT 0"),
        "outside_K": text.replace("FIBER outside_K 0 K_outside_fiber 0", "FIBER outside_K 1 K_outside_fiber 0"),
        "multiplicity": text.replace("dim 5 mult 23", "dim 5 mult 22"),
        "exit": text.replace("EXIT 0", "EXIT 1"),
        "script digest": text.replace(digest, "0" * 64),
        "truncated before FIBER, EXIT 0": text[: text.index("FIBER bound")] + "EXIT 0\n",
        "terminal FIBER line removed": text.replace("FIBER outside_K 0 K_outside_fiber 0\n", ""),
    }
    for label, mutant in mutants.items():
        if mutant == text:
            problems.append(f"mutation {label!r} changed nothing")
        elif not log_verdict(mutant, digest):
            problems.append(f"mutation {label!r} was accepted")
    toy_mutants = {
        "marker removed": toy.replace(f"{MARKER}\n", ""),
        "FIBER line": toy.replace("EXIT 0", "FIBER bound 0 minimal generators 1 dim 1 mult 1\nEXIT 0"),
        "exit": toy.replace("EXIT 0", "EXIT 124"),
    }
    for label, mutant in toy_mutants.items():
        if mutant == toy:
            problems.append(f"toy mutation {label!r} changed nothing")
        elif not toy_problems(mutant, toy_digest):
            problems.append(f"toy mutation {label!r} was accepted")
    print("RESULT self_test mutations", len(mutants) + len(toy_mutants))
    return problems


def main(argv: list[str]) -> int:
    problems = self_test() if argv == ["--self-test"] else check()
    for problem in problems:
        print("PROBLEM", problem)
    print("RESULT", "fail" if problems else "pass")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
