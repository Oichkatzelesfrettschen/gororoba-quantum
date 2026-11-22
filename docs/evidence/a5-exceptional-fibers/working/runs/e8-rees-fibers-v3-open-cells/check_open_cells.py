"""Verdict of the E8-bar modular Rees fiber runs of the open cells (ledger rows A5-576 and A5-578).

No Singular runs. The check reads the retained scripts and logs of this directory and of ../e8-rees-fibers-v2-p32009:

- the six v3 scripts equal the render of render_cells.py, and each modulo-colon script equals its v3 script with the
  one colon call replaced (COLON_OLD, COLON_NEW) and its basis file names renamed;
- every run log names the sha256 of its script and holds, each exactly once, the certificate lines, the unit guard
  line, the FIBER lines 148, 5, 11 with outside_K 0 and K_outside_fiber 0, 148 generator degrees equal to 2 and the
  Hilbert numerator of the retained (32009, 10754) run; EXIT 0 is its last line, and it has no FAIL or Singular
  error line;
- every file named in sha256.txt has the digest recorded there;
- the two replays of the retained v2 full runs equal the retained logs beyond the timers, and their basis digests
  equal the retained bases.sha256 (A5-578);
- the first-stage and saturated basis digests of each modulo-colon run equal those of the quotient run of its cell
  (the saturated basis is written after the colon loop, the first-stage basis before it);
- the 148 distinct relation lines of N- at root -r equal those of N+ at root r, at both primes.

Run from docs/evidence/a5-exceptional-fibers:

    python -B working/runs/e8-rees-fibers-v3-open-cells/check_open_cells.py [--self-test]

`--self-test` feeds known-bad variants of one log to the same verdict and requires each to fail.
"""

import hashlib
import re
import sys
from pathlib import Path

import render_cells

HERE = Path(__file__).resolve().parent
V2_DIR = HERE.parent / "e8-rees-fibers-v2-p32009"
MOD = HERE / "modulo-colon"
REPLAY = HERE / "replay-v2-full"
COLON_OLD = "QU=quotient(HS,ideal(u));"
COLON_NEW = "module MQ=modulo(ideal(u),HS); QU=ideal(matrix(MQ)); kill MQ;"
# Modulo-colon cells with a retained full run; the N- cell at (32029, 9115) has the resumed run RESUMED instead.
MOD_CELLS = [
    ("np", 32029, 9115),
    ("np", 32009, 21255),
    ("np", 32029, 22914),
    ("nm", 32009, 21255),
    ("nm", 32029, 22914),
]
RESUMED = "e8-nm-p32029-r9115.fiber-from-modsat"
REQUIRED = [
    "UNIT zero_constant_term_count 0",
    "CERT unit_identity_bad 0 all_positive_degree 1",
    "K quadrics 148 dim 5 mult 11",
    "CERT pivot_nonzerodivisor_mod_J 1",
    "FIBER bound 0 minimal generators 148 dim 5 mult 11",
    "generator degrees " + "2," * 147 + "2",
    "FIBER outside_K 0 K_outside_fiber 0",
    "EXIT 0",
]
# Each certified line family occurs once, so a contradicting second line fails the log.
ONCE = [
    "UNIT zero_constant_term_count",
    "CERT unit_identity_bad",
    "K quadrics",
    "CERT pivot_nonzerodivisor_mod_J",
    "FIBER bound",
    "generator degrees",
    "FIBER outside_K",
    "hilb",
    "EXIT ",
]
ONCE_FULL = ["CERT satstd_isSB", "CERT colon_equal_after_iterations"]
TIMER = re.compile(r"^(STAGE .*?|CERT colon_equal_after_iterations \d+) \d+$")


def numerator() -> str:
    lines = (V2_DIR / "e8-nm-p.v2-u-full.log").read_text().splitlines()
    return lines[lines.index("hilb") + 1]


def verdict(log: str, script: Path | None, full: bool) -> list[str]:
    """Reasons the log fails; an empty list is a pass. full=False is the resumed run, which has no satstd lines."""
    lines = [line.rstrip() for line in log.splitlines()]
    bad = [f"missing line: {need[:60]}" for need in REQUIRED if need not in lines]
    for prefix in ONCE + (ONCE_FULL if full else []):
        if sum(line.startswith(prefix) for line in lines) != 1:
            bad.append(f"line count is not 1: {prefix}")
    if any("FAIL" in line for line in lines):
        bad.append("FAIL line")
    if any(line.lstrip().startswith("? ") or "rror" in line for line in lines):
        bad.append("Singular error line")
    at = lines.index("hilb") + 1 if "hilb" in lines else len(lines)
    if at >= len(lines) or lines[at] != numerator():
        bad.append("Hilbert numerator differs from the retained run")
    if not lines or lines[-1] != "EXIT 0":
        bad.append("EXIT 0 is not the last line")
    if full:
        if not any(re.fullmatch(r"CERT satstd_isSB 1 leading_u_bad \d+", line) for line in lines):
            bad.append("no CERT satstd_isSB 1 line")
        if not any(re.fullmatch(r"CERT colon_equal_after_iterations \d+ \d+", line) for line in lines):
            bad.append("no CERT colon_equal_after_iterations line")
    elif "CERT H_outside_HS 0" not in lines:
        bad.append("no CERT H_outside_HS 0 line")
    if script is not None:
        digest = hashlib.sha256(script.read_bytes()).hexdigest()
        if len(lines) < 2 or lines[1] != f"{digest}  {script.name}":
            bad.append("line 2 does not name the script digest")
    return bad


def masked(text: str) -> list[str]:
    return [TIMER.sub(r"\1", line.rstrip()) for line in text.splitlines()]


def digests(path: Path) -> dict[str, str]:
    return {name: digest for digest, name in (line.split() for line in path.read_text().splitlines())}


def relations(path: Path) -> list[str]:
    return sorted(line for line in path.read_text().splitlines() if line.startswith("REL "))


def recorded_digests() -> list[str]:
    bad = []
    for name, digest in digests(HERE / "sha256.txt").items():
        path = HERE / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            bad.append(f"sha256.txt: {name} is missing or has another digest")
    return bad


def check() -> list[str]:
    bad = recorded_digests()
    v3 = render_cells.scripts()
    for name, text in v3.items():
        if (HERE / f"{name}.sing").read_text() != text:
            bad.append(f"{name}.sing differs from its render")
        bad += [f"{name}: {why}" for why in verdict((HERE / f"{name}.log").read_text(), HERE / f"{name}.sing", True)]
    base, mod_base = digests(HERE / "bases.sha256"), digests(MOD / "bases.sha256")
    for sign, prime, root in MOD_CELLS:
        name = render_cells.cell_name(sign, prime, root)
        mod_name = name.replace(".v3-", ".v4m-")
        if v3[name].count(COLON_OLD) != 1:
            bad.append(f"{name}: colon call count")
        want = v3[name].replace(COLON_OLD, COLON_NEW).replace(f"{name}.", f"{mod_name}.")
        if (MOD / f"{mod_name}.sing").read_text() != want:
            bad.append(f"{mod_name}.sing differs from its v3 script with the colon call replaced")
        log = MOD / f"{mod_name}.log"
        bad += [f"{mod_name}: {why}" for why in verdict(log.read_text(), MOD / f"{mod_name}.sing", True)]
        for part in ("hs.ssi", "sat.ssi"):
            if mod_base.get(f"{mod_name}.{part}") != base[f"{name}.{part}"]:
                bad.append(f"{mod_name}.{part}: digest differs from the quotient run")
    bad += [f"{RESUMED}: {why}" for why in verdict((MOD / f"{RESUMED}.log").read_text(), None, False)]
    if mod_base.get("e8-nm-p32029-r9115.modsat.ssi") != base["e8-nm-p32029-r9115.v3-u-full.sat.ssi"]:
        bad.append("resumed saturated basis: digest differs from the quotient run")
    retained, replayed = digests(V2_DIR / "bases.sha256"), digests(REPLAY / "bases.sha256")
    for stem in ("e8-nm-p.v2-u-full", "e8-np-p.v2-u-full"):
        if masked((REPLAY / f"{stem}.log").read_text()) != masked((V2_DIR / f"{stem}.log").read_text()):
            bad.append(f"{stem}: replayed log differs from the retained log beyond the timers")
        for part in ("hs.ssi", "sat.ssi"):
            if replayed.get(f"{stem}.{part}") != retained[f"{stem}.{part}"]:
                bad.append(f"{stem}.{part}: replay digest differs from the retained digest")
    pairs = [
        (V2_DIR / "e8-np-p.v2-u-full.log", HERE / "e8-nm-p32009-r21255.v3-u-full.log"),
        (V2_DIR / "e8-nm-p.v2-u-full.log", HERE / "e8-np-p32009-r21255.v3-u-full.log"),
        (HERE / "e8-np-p32029-r9115.v3-u-full.log", HERE / "e8-nm-p32029-r22914.v3-u-full.log"),
        (HERE / "e8-nm-p32029-r9115.v3-u-full.log", HERE / "e8-np-p32029-r22914.v3-u-full.log"),
    ]
    for plus, minus in pairs:
        if len(set(relations(plus))) != 148 or relations(plus) != relations(minus):
            bad.append(f"relation lines differ: {plus.name} and {minus.name}")
    return bad


def self_test() -> list[str]:
    name = "e8-np-p32029-r9115.v3-u-full"
    good = (HERE / f"{name}.log").read_text()
    script = HERE / f"{name}.sing"
    variants = {
        "generator count": good.replace("minimal generators 148", "minimal generators 147"),
        "exit status": good.replace("EXIT 0", "EXIT 124"),
        "failure marker": good.replace("FIBER outside_K", "CERT FAIL saturation\nFIBER outside_K", 1),
        "error line": good + "   ? error occurred in or before STDIN\n",
        "numerator": good.replace("1,0,-148,1562", "1,0,-148,1563"),
        "inclusion": good.replace("K_outside_fiber 0", "K_outside_fiber 3"),
        "script digest": good.replace(hashlib.sha256(script.read_bytes()).hexdigest(), "0" * 64),
        "truncated": good[: good.index("FIBER bound")],
        "truncated after hilb": good[: good.index("\nhilb\n") + 6],
        "second fiber line": good.replace(
            "FIBER outside_K", "FIBER bound 0 minimal generators 999 dim 1 mult 1\nFIBER outside_K", 1
        ),
        "second inclusion line": good.replace("EXIT 0", "FIBER outside_K 9 K_outside_fiber 9\nEXIT 0"),
        "second saturation line": good.replace("FIBER bound", "CERT satstd_isSB 0 leading_u_bad 96\nFIBER bound", 1),
        "unit guard": good.replace("UNIT zero_constant_term_count 0", "UNIT zero_constant_term_count 21"),
        "syntax error": good.replace("EXIT 0", "? syntax error\nEXIT 0"),
        "text after exit": good + "FIBER bound 0 minimal generators 148 dim 5 mult 11\n",
    }
    same = [label for label, text in variants.items() if text == good]
    bad = [f"self-test: the good log fails: {why}" for why in verdict(good, script, True)]
    bad += [f"self-test: variant equals the good log: {label}" for label in same]
    bad += [
        f"self-test: variant passes: {label}" for label, text in variants.items() if not verdict(text, script, True)
    ]
    return bad


def main(argv: list[str]) -> int:
    try:
        bad = self_test() if "--self-test" in argv[1:] else check()
    except (OSError, KeyError, ValueError) as err:
        bad = [f"unreadable or malformed input: {err!r}"]
    for why in bad:
        print(f"FAIL {why}")
    print("verdict: FAIL" if bad else "verdict: PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
