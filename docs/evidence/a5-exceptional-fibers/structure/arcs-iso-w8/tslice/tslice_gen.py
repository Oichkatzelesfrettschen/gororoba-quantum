"""Write the Singular scripts of the t-space slice ladder: does the origin lie on the closure of a slice of the graph?

For the blowup center I = (G) of a fiber slice V(J) in the t-variables and k linear forms l_1..l_k with QRNG
coefficients, Q_k = (J, l_1(G), ..., l_k(G)) cuts V(J) where G(t) lies in a codimension-k linear subspace of the
G-space. The saturation of Q_k by a function s that vanishes on V(I) near the origin is the ideal of the closure of
V(Q_k) minus V(s). The origin lies on that closure exactly when every generator of the saturation vanishes at 0
("on"); for generic forms that happens exactly when the fiber E0 of the blowup over the origin meets a generic
linear space of codimension k, that is, when dim E0 >= k. Three saturating functions are available:

    t2   the coordinate t2 (valid where V(I) lies in {t2 = 0} near the origin: Iso -> N- by A5-068)
    G    the whole ideal I = (G) (removes V(I) everywhere; the fallback where V(I) leaves {t2 = 0})
    a0   the QRNG form a0 = l0(G) of the blowup chart (chart-iso-pP-coefficients.json), a member of I

Forms come from docs/evidence/anu_qrng/draw-2026-11-06T113431Z.json: values below the prime, in index order, zero-
based, 17 per Iso form (l1..l5) and 3 per X form. The index lists are written to forms.json; the Iso l1..l4 at
p = 32009 equal those of chart-iso-p32009-slice-coefficients.json (and of the sliced chart script in
chart-runs/fx4-w8p2/). The cross-check function a0 of Iso is that chart's l0 from the draw 2026-11-05T235924Z. The X
forms continue in the same draw after the Iso forms at p = 32009 and serve both X incidences.

    $PYTHON tslice_gen.py            # writes forms.json and sing/CASE.sing for every case, from the repository root
"""

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
W = "docs/evidence/a5-exceptional-fibers/working"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-06T113431Z.json"
ISO_DIR = "docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8"
TS = f"{ISO_DIR}/tslice"
HEADERS = {
    ("iso", 32009): f"{W}/build/inputs/p32009-r10754/iso-nm.sing",
    ("iso", 32029): f"{W}/build/inputs/p32029-r9115/iso-nm.sing",
    ("xpnm", 32009): f"{W}/build/inputs/p32009-r10754/xp-nm.sing",
    ("xmnp", 32009): f"{W}/build/inputs/p32009-r10754/xm-np.sing",
}
NGEN = {"iso": 17, "xpnm": 3, "xmnp": 3}
SAT_LABEL = {
    "t2": "t2",
    "t2h": "t2 (homogenized standard basis, t2 last, then division by powers of t2)",
    "G": "ideal(G)",
    "a0": "a0",
}
# case: fiber, prime, k, saturating function, wall-time limit in seconds, whether the case is run (False: preregistered)
CASES: list[tuple[str, int, int, str, int, bool]] = []
for _fib in ("xpnm", "xmnp"):
    for _k in (2, 3):
        for _s in ("t2", "t2h", "a0"):
            CASES.append((_fib, 32009, _k, _s, 900, True))
CASES += [
    ("xpnm", 32009, 2, "G", 300, True),
    ("iso", 32009, 5, "t2", 3600, True),
    ("iso", 32009, 5, "t2h", 3600, True),
    ("iso", 32009, 5, "a0", 3600, True),
    ("iso", 32009, 3, "t2h", 7200, True),
    ("iso", 32009, 3, "t2", 7200, True),
    ("iso", 32009, 3, "a0", 7200, True),
    ("iso", 32009, 4, "t2h", 0, False),
    ("iso", 32029, 4, "t2h", 0, False),
    ("iso", 32009, 4, "t2", 0, False),
    ("iso", 32029, 4, "t2", 0, False),
]
JUNK_CASES = [(32009, 3), (32029, 0)]


def case_name(fiber: str, prime: int, k: int, sat: str) -> str:
    return f"{fiber}-p{prime}-k{k}-sat{sat}"


def take(values: list[int], prime: int, count: int, start: int) -> tuple[list[tuple[int, int]], int]:
    """The next `count` draw values below the prime at index >= start, as (index, value), and the next start."""
    out: list[tuple[int, int]] = []
    pos = start
    while len(out) < count:
        if values[pos] < prime:
            out.append((pos, values[pos]))
        pos += 1
    return out, pos


def build_forms() -> dict[str, dict[str, list[list[int]]]]:
    values = json.loads((ROOT / DRAW).read_text())["values"]
    forms: dict[str, dict[str, list[list[int]]]] = {}
    for prime in (32009, 32029):
        pos = 0
        entry: dict[str, list[list[int]]] = {}
        for f in range(1, 6):
            got, pos = take(values, prime, NGEN["iso"], pos)
            entry[f"iso-l{f}"] = [list(p) for p in got]
        if prime == 32009:
            for f in (1, 2, 3, 0):
                got, pos = take(values, prime, NGEN["xpnm"], pos)
                entry[f"x-l{f}"] = [list(p) for p in got]
        forms[str(prime)] = entry
    retained = json.loads((ROOT / ISO_DIR / "chart-iso-p32009-slice-coefficients.json").read_text())["coefficients"]
    mine = [p for f in range(1, 5) for p in forms["32009"][f"iso-l{f}"]]
    if mine != retained:
        raise SystemExit("Iso l1..l4 at p = 32009 differ from chart-iso-p32009-slice-coefficients.json")
    return forms


def a0_coefficients(prime: int) -> list[list[int]]:
    rec = json.loads((ROOT / ISO_DIR / f"chart-iso-p{prime}-coefficients.json").read_text())
    return [list(p) for p in rec["coefficients"]]


def lin(coeffs: list[int], var: str) -> str:
    return "+".join(f"{c}*{var}[{j + 1}]" for j, c in enumerate(coeffs))


def header_vars(header: str) -> list[str]:
    match = re.search(r"ring r=\d+,\((.*?)\)", (ROOT / header).read_text())
    if match is None:
        raise SystemExit(f"{header}: no ring line")
    return match.group(1).split(",")


def bayer(src: str, dst: str, ex_name: str, tvars: list[str], prime: int) -> str:
    """Singular code for dst = src : t2^infinity in ring r, by a standard basis of the homogenization with t2 last.

    For a homogeneous ideal and a degree-reverse-lexicographic order whose last variable is t2, dividing every
    standard-basis element by the highest power of t2 that it contains gives the saturation by t2; the dehomogenization
    h = 1 commutes with it because h and t2 are independent variables. The dp standard basis of src is homogenized
    generator by generator, which generates the homogenization of src because dp is degree-compatible.
    """
    order = ",".join([v for v in tvars if v != "t2"] + ["h", "t2"])
    return (
        f"ideal Qs_{src}=std({src});\n"
        f"ring rh_{src}={prime},({order}),dp;\n"
        f"ideal Qh=homog(imap(r,Qs_{src}),h);\n"
        "ideal Sh=std(Qh);\n"
        f"int {ex_name}=0; int ii; poly gg; int ee; for (ii=1;ii<=ncols(Sh);ii++) {{ gg=Sh[ii]; ee=0;"
        " while (gg!=0 && subst(gg,t2,0)==0) { gg=gg/t2; ee++; }"
        f" Sh[ii]=gg; if (ee>{ex_name}) {{ {ex_name}=ee; }} }}\n"
        "ideal Sd=subst(Sh,h,1);\n"
        f"setring r; ideal {dst}=imap(rh_{src},Sd);\n"
        f"kill rh_{src};"
    )


def script(fiber: str, prime: int, k: int, sat: str, forms: dict[str, dict[str, list[list[int]]]]) -> str:
    name = case_name(fiber, prime, k, sat)
    header = HEADERS[(fiber, prime)]
    digest = hashlib.sha256((ROOT / header).read_bytes()).hexdigest()
    fam = "iso" if fiber == "iso" else "x"
    entry = forms[str(prime)]
    lines: list[str] = []

    def emit(text: str) -> None:
        lines.append(text)

    def res(expr: str) -> None:
        emit(f'rl="RESULT {name} "+{expr}; print(rl); write(":a {TS}/logs/{name}.result", rl);')

    emit(f"// t-space slice {name}: k = {k} forms, saturation by {SAT_LABEL[sat]}; header {header} (sha256 {digest})")
    emit(f"// forms l1..l{k}: {DRAW}, key {fam}-l1..{fam}-l{k} of forms.json (values below {prime}, index order)")
    if sat == "a0":
        emit(
            f"// a0 = l0(G): {ISO_DIR}/chart-iso-p{prime}-coefficients.json"
            if fam == "iso"
            else "// a0 = x-l0 of forms.json"
        )
    emit('LIB "elim.lib"; LIB "general.lib"; system("--ticks-per-sec",1); int t0=rtimer; string rl;')
    if fam == "iso":
        emit("option(prot);")
    emit(f'< "{header}";')
    for f in range(1, k + 1):
        emit(f"poly l{f}={lin([v for _, v in entry[f'{fam}-l{f}']], 'G')};")
    forms_list = ",".join(f"l{f}" for f in range(1, k + 1))
    emit(f"ideal Q=J,{forms_list};")
    if sat == "a0":
        coeffs = [v for _, v in (a0_coefficients(prime) if fam == "iso" else entry["x-l0"])]
        emit(f"poly a0={lin(coeffs, 'G')};")
        emit("ideal S0=a0;")
    elif sat in ("t2", "t2h"):
        emit("ideal S0=t2;")
    else:
        emit("ideal S0=G;")
    res(f'"start: variables "+string(nvars(basering))+", forms {k}, size(Q) "+string(size(Q))+", s "+string(rtimer-t0)')
    if sat == "t2h":
        emit(bayer("Q", "S", ex_name="ex", tvars=header_vars(header), prime=prime))
    else:
        emit("def SS=sat_with_exp(Q,S0); ideal S=SS[1]; int ex=SS[2];")
    res('"saturation done: generators "+string(size(S))+", exponent "+string(ex)+", s "+string(rtimer-t0)')
    emit("S=std(S);")
    res('"standard basis of the saturation: generators "+string(size(S))+", s "+string(rtimer-t0)')
    emit("int dm=dim(S); int dg=0; if (dm>=0) { dg=mult(S); }")
    res('"dim "+string(dm)+" degree "+string(dg)+" s "+string(rtimer-t0)')
    emit("int on=(size(reduce(S,std(maxideal(1))))==0);")
    res('"origin on the closure (all generators vanish at 0) "+string(on)+" s "+string(rtimer-t0)')
    emit("quit;")
    return "\n".join(lines) + "\n"


def junk_script(prime: int, k: int, forms: dict[str, dict[str, list[list[int]]]]) -> str:
    """Iso only: split the saturation of Q_k by t2 into the junk over V(J + G) and the part outside it.

    V(J, G) minus V(t2) has its own closure Jk; the saturation S of Q_k contains it (every l_i(G) vanishes there). The
    saturation S : Jk^infinity is the closure of V(Q_k) minus V(t2) minus V(Jk), the slice proper. The script reports
    whether the origin lies on Jk, and the dimension, degree and origin membership of S : Jk^infinity.
    """
    name = f"iso-p{prime}-k{k}-junkcheck" if k else f"iso-p{prime}-junk"
    header = HEADERS[("iso", prime)]
    digest = hashlib.sha256((ROOT / header).read_bytes()).hexdigest()
    entry = forms[str(prime)]
    tvars = header_vars(header)
    lines = [
        f"// junk split of the saturation by t2: k = {k} forms, header {header} (sha256 {digest})"
        if k
        else f"// closure of V(J, G) minus V(t2) and the origin test, header {header} (sha256 {digest})",
        f"// forms l1..l{k}: {DRAW}, key iso-l1..iso-l{k} of forms.json (values below {prime}, index order)"
        if k
        else "// no forms: the check does not depend on k",
        'LIB "elim.lib"; LIB "general.lib"; system("--ticks-per-sec",1); int t0=rtimer; string rl;',
        f'< "{header}";',
    ]
    for f in range(1, k + 1):
        lines.append(f"poly l{f}={lin([v for _, v in entry[f'iso-l{f}']], 'G')};")
    if k:
        lines.append(f"ideal Q=J,{','.join(f'l{f}' for f in range(1, k + 1))};")
    lines.append("ideal QJ=J,G;")

    def res(expr: str) -> None:
        lines.append(f'rl="RESULT {name} "+{expr}; print(rl); write(":a {TS}/logs/{name}.result", rl);')

    if k:
        lines.append(bayer("Q", "S", "ex", tvars, prime))
        lines.append("S=std(S);")
        res('"slice: dim "+string(dim(S))+" degree "+string(mult(S))+" s "+string(rtimer-t0)')
    lines.append(bayer("QJ", "JK", "exj", tvars, prime))
    lines.append("JK=std(JK);")
    res('"junk V(J,G) minus V(t2): dim "+string(dim(JK))+" degree "+string(mult(JK))+" s "+string(rtimer-t0)')
    lines.append("int onj=(size(reduce(JK,std(maxideal(1))))==0);")
    res('"origin on the junk "+string(onj)+" s "+string(rtimer-t0)')
    if k:
        lines.append("def SP=sat_with_exp(S,JK); ideal R=std(SP[1]);")
        lines.append("int dr=dim(R); int gr=0; if (dr>=0) { gr=mult(R); }")
        res('"slice proper (saturation by the junk): dim "+string(dr)+" degree "+string(gr)+" s "+string(rtimer-t0)')
        lines.append("int onr=(size(reduce(R,std(maxideal(1))))==0);")
        res('"origin on the slice proper "+string(onr)+" s "+string(rtimer-t0)')
    lines.append("quit;")
    return "\n".join(lines) + "\n"


def main() -> None:
    forms = build_forms()
    ledger = {
        "draw": DRAW,
        "rule": "uint16 values below the prime in index order, zero-based; [index, value] per coefficient",
        "forms": forms,
        "a0": {str(p): a0_coefficients(p) for p in (32009, 32029)},
    }
    (HERE / "forms.json").write_text(json.dumps(ledger, indent=1) + "\n")
    (HERE / "sing").mkdir(exist_ok=True)
    for fiber, prime, k, sat, _limit, _run in CASES:
        (HERE / "sing" / f"{case_name(fiber, prime, k, sat)}.sing").write_text(script(fiber, prime, k, sat, forms))
        print(f"sing/{case_name(fiber, prime, k, sat)}.sing")
    for prime, k in JUNK_CASES:
        junk_name = f"iso-p{prime}-k{k}-junkcheck" if k else f"iso-p{prime}-junk"
        (HERE / "sing" / f"{junk_name}.sing").write_text(junk_script(prime, k, forms))
        print(f"sing/{junk_name}.sing")


if __name__ == "__main__":
    main()
