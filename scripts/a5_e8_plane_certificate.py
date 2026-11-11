#!/usr/bin/env python3
"""Generate and optionally run an exact Singular certificate for the E8 plane.

The input relation file must be the retained E8 quadric K2 file. The
certificate checks that the two minimal primes of K2 + nilradical generators
meet in an EXACT linear P^2, not just a degree-one top-dimensional cycle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PRIMES = {"p1": 32009, "p2": 32029}
HEADERS = ("nm", "np")
NILPOTENT_COORDINATES = (4, 6, 7, 12, 14)


def make_script(prime: int, relation_file: Path) -> str:
    if prime not in PRIMES.values():
        raise ValueError("Unsupported prime")
    if not relation_file.is_file():
        raise FileNotFoundError(relation_file)
    # Singular requires a quoted path; reject its quoting/control syntax.
    path = relation_file.resolve().as_posix()
    if any(ch in path for ch in ('"', "\\", "\n", "\r")):
        raise ValueError("Unsafe Singular file path")
    nilradical = ",".join(f"y({i})" for i in NILPOTENT_COORDINATES)
    return f'''LIB "primdec.lib";
option(redSB);
ring Y={prime},(y(1..21)),dp;
execute("ideal K="+read("{path}")+";");
ideal N=ideal({nilradical});
list P=minAssChar(std(K+N));
if (size(P)!=2) {{ "RESULT FAIL: expected exactly two minimal primes"; quit; }}
ideal T=std(P[1]+P[2]);
ideal H=std(jet(T,1));
int dimT=dim(T);
int multT=mult(T);
int dimH=dim(H);
int multH=mult(H);
int nlin=size(H);
ideal a=reduce(T,H);
ideal b=reduce(H,T);
int forward=(size(simplify(a,2))==0);
int reverse=(size(simplify(b,2))==0);
int degreeOne=1;
int j;
for(j=1;j<=size(H);j++) {{ if(deg(H[j])!=1) {{degreeOne=0;}} }}
"RESULT intersection_dim",dimT;
"RESULT intersection_mult",multT;
"RESULT linear_dim",dimH;
"RESULT linear_mult",multH;
"RESULT independent_linear_generators",nlin;
"RESULT inclusion_intersection_in_linear",forward;
"RESULT inclusion_linear_in_intersection",reverse;
if(dimT==3 && multT==1 && dimH==3 && multH==1 &&
   nlin==18 && degreeOne==1 && forward==1 && reverse==1)
{{ "RESULT E8_EXACT_PROJECTIVE_PLANE_PASS"; }}
else {{ "RESULT E8_EXACT_PROJECTIVE_PLANE_FAIL"; }}
quit;
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("header", choices=HEADERS)
    parser.add_argument("prime_id", choices=tuple(PRIMES))
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--script-out", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--singular", default="Singular")
    parser.add_argument("--record", type=Path, help="JSON result path; requires --run")
    args = parser.parse_args()

    if args.record and not args.run:
        parser.error("--record requires --run")
    repo = args.repo.resolve()
    name = f"e8{args.header}_{args.prime_id}"
    path = (repo / "docs/evidence/a5-exceptional-fibers/working/distribute/out"
            / "a5-e8-d2" / name / "d2" / "relations-upto-d2.rel")
    try:
        source = path.read_bytes()
        script = make_script(PRIMES[args.prime_id], path)
        if args.script_out:
            args.script_out.write_text(script, encoding="utf-8")
        if not args.run:
            if not args.script_out:
                sys.stdout.write(script)
            return 0
        process = subprocess.run(
            [args.singular, "-q"],
            input=script, text=True, capture_output=True, check=False,
            timeout=3600,
        )
        ok = (process.returncode == 0
              and "RESULT E8_EXACT_PROJECTIVE_PLANE_PASS" in process.stdout
              and "RESULT E8_EXACT_PROJECTIVE_PLANE_FAIL" not in process.stdout)
        result = {
            "header": args.header, "prime": PRIMES[args.prime_id],
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
            "singular_returncode": process.returncode,
            "verified": ok, "stdout": process.stdout, "stderr": process.stderr,
        }
        if args.record:
            args.record.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        else:
            print(json.dumps(result, indent=2))
        return 0 if ok else 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"E8 plane certificate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
