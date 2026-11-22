"""Verdict of the E8-bar modular Rees fiber runs of the open cells (ledger rows A5-576 and A5-578).

No Singular runs. The check reads the retained scripts and logs of this directory and of ../e8-rees-fibers-v2-p32009:

- the six v3 scripts equal the render of render_cells.py, and each modulo-colon script equals its v3 script with the
  one colon call replaced (COLON_OLD, COLON_NEW) and its basis file names renamed;
- every run log names the sha256 of its script, holds the certificate lines, the FIBER lines 148, 5, 11 with
  outside_K 0 and K_outside_fiber 0, 148 generator degrees equal to 2, the Hilbert numerator of the retained
  (32009, 10754) run, EXIT 0, no CERT FAIL line and no Singular error line;
- the two replays of the retained v2 full runs equal the retained logs beyond the timers, and their basis digests
  equal the retained bases.sha256 (A5-578);
- the first-stage and saturated basis digests of each modulo-colon run equal those of the quotient run of its cell;
- the relation lines of N- at root -r equal those of N+ at root r, at both primes.

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
MOD_CELLS = [("np", 32029, 9115), ("np", 32009, 21255), ("np", 32029, 22914), ("nm", 32009, 21255)]
RESUMED = "e8-nm-p32029-r9115.fiber-from-modsat"
REQUIRED = [
    "CERT unit_identity_bad 0 all_positive_degree 1",
    "K quadrics 148 dim 5 mult 11",
    "CERT pivot_nonzerodivisor_mod_J 1",
    "FIBER bound 0 minimal generators 148 dim 5 mult 11",
    "generator degrees " + "2," * 147 + "2",
    "FIBER outside_K 0 K_outside_fiber 0",
    "EXIT 0",
]
TIMER = re.compile(r"^(STAGE .*?|CERT colon_equal_after_iterations \d+) \d+$")


def numerator() -> str:
    lines = (V2_DIR / "e8-nm-p.v2-u-full.log").read_text().splitlines()
    return lines[lines.index("hilb") + 1]


def verdict(log: str, script: Path | None, full: bool) -> list[str]:
    """Reasons the log fails; an empty list is a pass. full=False is the resumed run, which has no satstd lines."""
    lines = [line.rstrip() for line in log.splitlines()]
    bad = [f"missing line: {need[:60]}" for need in REQUIRED if need not in lines]
    if any("CERT FAIL" in line for line in lines):
        bad.append("CERT FAIL line")
    if any(line.startswith("   ? ") for line in lines):
        bad.append("Singular error line")
    if "hilb" not in lines or lines[lines.index("hilb") + 1] != numerator():
        bad.append("Hilbert numerator differs from the retained run")
    if sum(line.startswith("EXIT ") for line in lines) != 1:
        bad.append("EXIT line count")
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
    return sorted(line for line in path.read_text().splitlines() if line.startswith("REL"))


def check() -> list[str]:
    bad: list[str] = []
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
        if len(relations(plus)) != 149 or relations(plus) != relations(minus):
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
    }
    bad = [f"self-test: the good log fails: {why}" for why in verdict(good, script, True)]
    bad += [
        f"self-test: variant passes: {label}" for label, text in variants.items() if not verdict(text, script, True)
    ]
    return bad


def main(argv: list[str]) -> int:
    bad = self_test() if "--self-test" in argv[1:] else check()
    for why in bad:
        print(f"FAIL {why}")
    print("verdict: FAIL" if bad else "verdict: PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
