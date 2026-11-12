"""Falsify the per-variable split of the engine v8 quotient export.

Runs the engine's own serial export script at a small N, then the split: one Singular process computes std(J + m^N)
and writes it; one process per variable reads that basis back, marks it a standard basis and writes its
multiplication table; one extra pair of processes writes the first table in two index halves of kbase. Every file is
compared against the serial export after newline removal. Any difference falsifies the split.
"""

import hashlib
import re
import subprocess
import sys
import time
from pathlib import Path

ENGINE = Path("docs/evidence/a5-exceptional-fibers/replay/engine/fiber_rank_v8.py")


def found(pattern: str, text: str, flags: int = 0) -> re.Match[str]:
    """The match of `pattern` in `text`; a missing match stops the run."""
    m = re.search(pattern, text, flags)
    if m is None:
        raise ValueError(f"no match for {pattern}")
    return m


src = ENGINE.read_text()
SERIAL = found(r'QUOTIENT_SCRIPT = """(.*?)"""', src, re.S).group(1)


def hdr(path: str) -> dict[str, str]:
    t = Path(path).read_text().replace("\n", "")
    p, names = found(r"ring r=(\d+),\(([^)]*)\)", t).groups()
    return {"p": p, "names": names, "J": found(r"ideal J=([^;]*);", t).group(1),
            "G": found(r"ideal G=([^;]*);", t).group(1)}  # fmt: skip


def run(script: str, path: Path) -> subprocess.Popen:
    path.write_text(script)
    return subprocess.Popen(["Singular", "-q", "--no-rc", str(path)], stdin=subprocess.DEVNULL,
                            stdout=open(str(path) + ".out", "w"), stderr=subprocess.STDOUT)  # fmt: skip


def norm(path: Path) -> str:
    return hashlib.sha256(path.read_text().replace("\n", "").encode()).hexdigest()


def main() -> int:
    header, N, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]).resolve()
    h = hdr(header)
    nv = len(h["names"].split(","))
    for sub in ("serial", "split"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    pre = f"ring r={h['p']},({h['names']}),dp;\noption(redSB);\n"
    t0 = time.time()
    serial = run(SERIAL.format(N=N, out=out / "serial", **{k: h[k] for k in ("p", "names", "J", "G")}),
                 out / "serial" / "q.sing")  # fmt: skip
    sp = out / "split"
    std = run(pre + f"ideal J={h['J']};\nint t0=rtimer;\nideal s=std(J+maxideal({N}));\n"
              f'short=0; write(":w {sp}/s.txt",s);\nideal B=kbase(s);\nshort=0; write(":w {sp}/qB.txt",B);\n'
              f'"RESULT std", ncols(s), ncols(B), rtimer-t0;\nquit;\n', sp / "std.sing")  # fmt: skip
    std.wait()
    t_std = time.time() - t0
    load = (f'execute("ideal s=" + read("{sp}/s.txt") + ";");\nattrib(s,"isSB",1);\n'
            "ideal B=kbase(s);\n")  # fmt: skip
    jobs = []
    for k in range(1, nv + 1):
        jobs.append(run(pre + load + f'ideal Mk=reduce(var({k})*B,s);\nshort=0; write(":w {sp}/qM{k}.txt",Mk);\n'
                        '"RESULT table", ncols(Mk);\nquit;\n', sp / f"t{k}.sing"))  # fmt: skip
    for half, rng in ((1, "1..m"), (2, "m+1..ncols(B)")):
        jobs.append(run(pre + load + "int m=ncols(B) div 2;\n"
                        f'ideal Bh=B[{rng}];\nideal Mk=reduce(var(1)*Bh,s);\n'
                        f'short=0; write(":w {sp}/qM1.h{half}.txt",Mk);\nquit;\n', sp / f"h{half}.sing"))  # fmt: skip
    jobs.append(run(pre + load + f"ideal G={h['G']};\nG=reduce(jet(G,{N}-1),s);\n"
                    f'short=0; write(":w {sp}/qG.txt",G);\nquit;\n', sp / "g.sing"))  # fmt: skip
    for j in jobs:
        j.wait()
    t_split = time.time() - t0
    serial.wait()
    t_serial = time.time() - t0
    names = ["qB.txt", "qG.txt"] + [f"qM{k}.txt" for k in range(1, nv + 1)]
    bad = [n for n in names if norm(out / "serial" / n) != norm(sp / n)]
    halves = ((sp / "qM1.h1.txt").read_text() + "," + (sp / "qM1.h2.txt").read_text()).replace("\n", "")
    if hashlib.sha256(halves.encode()).hexdigest() != norm(out / "serial" / "qM1.txt"):
        bad.append("qM1 halves")
    print(f"N={N} serial {t_serial:.1f} s; split std {t_std:.1f} s, split total {t_split:.1f} s; "
          f"files {len(names)}; mismatches {bad}")  # fmt: skip
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
