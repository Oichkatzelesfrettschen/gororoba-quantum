"""E8-bar -> N- slice at a chosen split prime: pull back the nullity-12 closures through N- (B9, V, VB, Va-, Va+), test
F (Schur coordinates) inside each prime through 0, and test every containment between those primes, so the germ of
V(J + F) at 0 is the irredundant union of the primes contained in no other.

    $PYTHON docs/evidence/a5-exceptional-fibers/structure/e8-base-components/e8_base2.py p32009|p32029
"""

import sys
from pathlib import Path

sys.path.insert(0, "docs/evidence/a5-exceptional-fibers/structure")
import base_locus as bl  # noqa: E402

rees = bl.fi.rees
NAMES = ["B9", "V", "VB", "Vam", "Vap"]


def main() -> None:
    field = sys.argv[1]
    p, root = bl.FIELDS[field]
    if field == "q":
        raise SystemExit("finite fields only: p32009 or p32029")
    task, data = bl._task("E8bar->N-")
    ideals = rees.regularity.closure_ideals()
    lines = [*rees._local_germ_lines(root, task, data, p), f"ideal FullF={rees._coordinate_text(data)};", "setring r;"]
    for n in NAMES:
        lines.append(f"ideal C{n}=" + ",".join(str(f) for f in ideals[n]) + ";")
    lines += [
        "setring s;",
        "proc thru(ideal X){ list L=minAssGTZ(X); list T; int c=0; for(int i=1;i<=size(L);i++){"
        " if(size(reduce(L[i],std(maxideal(1))))==0){c++; T[c]=std(L[i]);} } return(T); }",
        f'"RESULT prime", {p};',
        '"RESULT germ_dim", dim(J);',
    ]
    for n in NAMES:
        lines += [
            f"list P{n}=thru(std(J+sliceMap(C{n})));",
            f'"RESULT {n}_primes", size(P{n});',
            f'for(int i=1;i<=size(P{n});i++){{ "RESULT {n}_dim_"+string(i), dim(P{n}[i]); '
            f'"RESULT {n}_deg_"+string(i), mult(P{n}[i]); '
            f'"RESULT {n}_F_inside_"+string(i), size(reduce(FullF,P{n}[i]))==0; }}',
        ]
    # V(P_X[i]) lies in V(P_Y[j]) exactly when the prime P_Y[j] is contained in P_X[i].
    for x in NAMES:
        for y in NAMES:
            if x != y:
                lines.append(
                    f"for(int i=1;i<=size(P{x});i++){{ for(int j=1;j<=size(P{y});j++){{ "
                    f'"RESULT V({x}_"+string(i)+") in V({y}_"+string(j)+")", size(reduce(P{y}[j],P{x}[i]))==0; }} }}'
                )
    lines += ['"RESULT done";', "quit;"]
    out = Path(f"docs/evidence/a5-exceptional-fibers/structure/e8-base-components/e8_base2-{field}.sing")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
