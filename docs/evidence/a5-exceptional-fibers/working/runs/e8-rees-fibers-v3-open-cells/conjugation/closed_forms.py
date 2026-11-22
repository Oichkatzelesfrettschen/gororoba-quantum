"""Compare the detB and UNIT lines of the eight E8-bar logs with the closed forms of ledger row A5-592.

Run from docs/evidence/a5-exceptional-fibers:

    python -B working/runs/e8-rees-fibers-v3-open-cells/conjugation/closed_forms.py working/runs
"""

import re
import sys
from pathlib import Path

CELLS = [
    ("nm", 32009, 10754),
    ("np", 32009, 10754),
    ("nm", 32009, 21255),
    ("np", 32009, 21255),
    ("nm", 32029, 9115),
    ("np", 32029, 9115),
    ("nm", 32029, 22914),
    ("np", 32029, 22914),
]


def parse(text: str, p: int) -> list[int]:
    out: dict[int, int] = {}
    for sign, term in re.findall(r"([+-]?)([^+-]+)", text.replace(" ", "")):
        m = re.fullmatch(r"(\d+)?\*?(s2)?(?:\^(\d+))?", term)
        if m is None:
            raise ValueError(term)
        c = int(m.group(1)) if m.group(1) else 1
        e = (int(m.group(3)) if m.group(3) else 1) if m.group(2) else 0
        out[e] = (out.get(e, 0) + (-c if sign == "-" else c)) % p
    return [out.get(e, 0) for e in range(max(out) + 1)]


def mul(a: list[int], b: list[int], p: int) -> list[int]:
    r = [0] * (len(a) + len(b) - 1)
    for x, u in enumerate(a):
        for y, v in enumerate(b):
            r[x + y] = (r[x + y] + u * v) % p
    return r


def power(a: list[int], n: int, p: int) -> list[int]:
    r = [1]
    for _ in range(n):
        r = mul(r, a, p)
    return r


def main(root: Path) -> int:
    bad = 0
    for sign, p, r in CELLS:
        name = f"e8-{sign}-p.v2-u-full" if r == 10754 else f"e8-{sign}-p{p}-r{r}.v3-u-full"
        d = "e8-rees-fibers-v2-p32009" if r == 10754 else "e8-rees-fibers-v3-open-cells"
        lines = (root / d / f"{name}.log").read_text().splitlines()
        lin = [(-r) % p, 1] if sign == "nm" else [r % p, 1]
        q = [p - 1, 0, 1]
        det = [(-1024 * c) % p for c in mul(power(q, 2, p), power(lin, 2, p), p)]
        got = [parse(line[5:], p) for line in lines if line.startswith("detB ")]
        ok_det = got == [det]
        units = [line for line in lines if re.match(r"UNIT \d+ c\(0\)=", line)]
        miss = []
        for line in units:
            k = int(line.split()[1])
            want = mul(power(q, 4 if k in (10, 16) else 3, p), power(lin, 3, p), p)
            if parse(line.split(" c=")[1], p) != want:
                miss.append(k)
        print(f"{sign} p={p} r={r}: detB {'match' if ok_det else 'DIFFER'}; UNIT lines {len(units)}, differing {miss}")
        bad += (not ok_det) + len(miss) + (len(units) != 21)
    print("A5-592 closed forms:", "match on all eight logs" if bad == 0 else f"{bad} deviations")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
