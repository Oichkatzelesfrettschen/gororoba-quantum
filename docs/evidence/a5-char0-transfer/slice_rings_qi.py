"""The same-sign X and E8-bar slices over Q(i): kernel of the parametrization, and the E8-bar ideal closure.

Two checks that the modular records of `../a5-exceptional-fibers/monomial-ladder` make at the split primes are
repeated over Q(i) with the J and G of the Q(i) producer (`reduction_check._script`).

kernel: the kernel of the parametrization of the slice, computed by eliminating the parameters from its graph, equals
the producer's J together with the variables the presolve removed. Cases: xm-nm, xp-np, e8-nm, e8-np.

closure: in S = (P + P b) localized at 1 + w, with m_R S of colength 2, the module I S / (m_R S) I S has dimension
21 and the 21 generators span it over Q(i), so I = I S by Nakayama's lemma. Cases: e8-nm, e8-np. The script prints
the normal form of each unit vector modulo the relation module and takes the rank of their coefficient matrix over
Q(i).

Writes one slice-rings-qi-CHECK-SLUG.json per case as it finishes and slice-rings-qi.json at the end, beside this
file. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/slice_rings_qi.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import sympy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reduction_check as rc  # noqa: E402

import parallel  # noqa: E402

SIGN = {"xm-nm": 1, "xp-np": -1, "e8-nm": 1, "e8-np": -1}
X_NAMES = "pa,pr,ps,pw,pu"
X_IMAGES = {
    "t1": "pa+pw^2*pu/2",
    "t2": "pa*pw*(pw+2)*pu/2",
    "t4": "((1+pw)*pr+ps)/2",
    "t5": "((1+pw)*pr-ps)/2",
    "t6": "((1+pw)*ps+pr)/2",
    "t7": "(pr-(1+pw)*ps)/2",
    "t9": "{sign}*(-pw^2*pu/2)",
}
E8_NAMES = "qw,qr,qs,qz,qa,qb,qu"
E8_IMAGES = {
    "t1": "(-(qw*(qw+2))*qa+((1+qw)^2+1)*qz+qw^2)*qu/2",
    "t2": "qa",
    "t3": "qz",
    "t4": "((1+qw)*qr+qs)/2",
    "t5": "((1+qw)*qr-qs)/2",
    "t6": "((1+qw)*qs+qr)/2",
    "t7": "(qr-(1+qw)*qs)/2",
    "t8": "-I*qb",
    "t9": "-({sign})*qw^2*qu/2",
}
E8_REL = "qu*(1+qw)-1, qb^2-EA*(EA-qw*(qw+2))*qu^2"
E8_A = "poly EA=(((1+qw)^2+1)*qa-((1+qw)^2-1)*qz)/2;"
TIMEOUT = 40000


def producer(slug: str) -> tuple[str, list[str]]:
    body = rc._script(slug, None, rc.rees.MODULAR_PRIME, extra=False).replace("\nquit;\n", "\n")
    probe = rc.rees._run_singular(body + '"RESULT vs",varstr(basering);\nquit;\n', "slice_qi_vars", rc.TIMEOUT_SECONDS)
    rc._require(probe.status == "completed", f"{slug} variable probe: {probe.status} {probe.diagnostic}")
    return body, probe.results["vs"].split(",")


def kernel(slug: str) -> dict[str, Any]:
    body, variables = producer(slug)
    e8 = slug.startswith("e8")
    names, images = (E8_NAMES, E8_IMAGES) if e8 else (X_NAMES, X_IMAGES)
    # A producer variable outside the parametrization is zero on the slice.
    graph = ",".join(f"{v}-({images.get(v, '0').format(sign=SIGN[slug])})" for v in variables)
    relation = E8_REL if e8 else "pu*(1+pw)-1"
    # The producer ring keeps the variables its presolve removed; J does not involve them and they vanish on the slice.
    unused = ",".join(v for v in variables if v not in images) or "0"
    blocks = f"(dp({names.count(',') + 1}),dp({len(variables)}))"
    lines = (
        'LIB "primdec.lib";',
        f"def R0=basering; ideal SJ=std(ReducedJ+ideal({unused}));",
        f"ring GraphRing=(0,I),({names},{','.join(variables)}),{blocks};minpoly=I2+1;",
        E8_A if e8 else "",
        f"ideal Z={relation},{graph};",
        f"ideal E=eliminate(Z,{names.replace(',', '*')});",
        "setring R0; ideal K=std(imap(GraphRing,E));",
        '"RESULT kernel_generators",size(K); "RESULT kernel_dim",dim(K); "RESULT kernel_mult",mult(K);',
        '"RESULT j_dim",dim(SJ); "RESULT j_mult",mult(SJ);',
        '"RESULT j_in_kernel",size(simplify(reduce(ReducedJ,K),2))==0;',
        '"RESULT kernel_in_j",size(simplify(reduce(K,SJ),2))==0;',
        "quit;",
    )
    outcome = rc.rees._run_singular(body + "\n".join(lines) + "\n", "slice_qi_kernel", TIMEOUT)
    rc._require(outcome.status == "completed", f"{slug} kernel: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    row: dict[str, Any] = {
        key: int(res[key]) for key in ("kernel_generators", "kernel_dim", "kernel_mult", "j_dim", "j_mult")
    }
    row.update(
        {
            "check": "kernel",
            "slug": slug,
            "j_in_kernel": res["j_in_kernel"] == "1",
            "kernel_in_j": res["kernel_in_j"] == "1",
            "unused_variables": [v for v in variables if v not in images],
            "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
            "peak_rss_kib": outcome.peak_rss_kib,
        }
    )
    row["verdict"] = "kernel_equals_j" if row["j_in_kernel"] and row["kernel_in_j"] else "failed"
    return row


def closure(slug: str) -> dict[str, Any]:
    body, variables = producer(slug)
    images = ",".join(E8_IMAGES.get(v, "0").format(sign=SIGN[slug]) for v in variables)
    lines = (
        "def R0=basering; ideal MX=maxideal(1);",
        f"ring G0=(0,I),({E8_NAMES}),dp;minpoly=I2+1;",
        E8_A,
        f"ideal Rel={E8_REL};",
        "qring S=std(Rel);",
        f"map phi=R0,{images};",
        '"RESULT j_nonzero",size(simplify(reduce(phi(ReducedJ),std(0)),2));',
        "ideal It=reduce(phi(ReducedG),std(0)); ideal Am=reduce(phi(MX),std(0)); ideal SA=std(Am);",
        "ideal Ms=qw,qr,qs,qz,qa,qb;",
        '"RESULT colength",vdim(SA); "RESULT generators",ncols(It);',
        "module Mq=std(modulo(It,Am*It));",
        '"RESULT quotient_dimension",vdim(Mq);',
        '"RESULT s_generators",vdim(std(Mq+Ms*freemodule(ncols(It))));',
        "module NFm=reduce(freemodule(ncols(It)),Mq); int i; int j;",
        "for(j=1;j<=ncols(It);j++){ for(i=1;i<=ncols(It);i++){ if(NFm[j][i]!=0){"
        ' "RESULT nf_"+string(j)+"_"+string(i),NFm[j][i]; } } }',
        "quit;",
    )
    outcome = rc.rees._run_singular(body + "\n".join(lines) + "\n", "slice_qi_closure", TIMEOUT)
    rc._require(outcome.status == "completed", f"{slug} closure: {outcome.status} {outcome.diagnostic}")
    res = outcome.results
    symbols = sympy.symbols(E8_NAMES)
    imaginary = sympy.I
    columns: dict[tuple[int, tuple[int, ...]], int] = {}
    entries: dict[tuple[int, int], Any] = {}
    for key, text in res.items():
        match = re.fullmatch(r"nf_(\d+)_(\d+)", key)
        if not match:
            continue
        expression = sympy.parse_expr(text.replace("^", "**"), local_dict={"I": imaginary})
        for exponents, coefficient in sympy.Poly(expression, *symbols).terms():
            column = columns.setdefault((int(match[2]), tuple(int(e) for e in exponents)), len(columns))
            entries[int(match[1]) - 1, column] = coefficient
    count = int(res["generators"])
    matrix = sympy.zeros(count, len(columns))
    for (r, c), value in entries.items():
        matrix[r, c] = value
    row: dict[str, Any] = {
        "check": "closure",
        "slug": slug,
        "j_nonzero": int(res["j_nonzero"]),
        "colength_of_m_r_s": int(res["colength"]),
        "generators": count,
        "quotient_dimension": int(res["quotient_dimension"]),
        "minimal_s_generators": int(res["s_generators"]),
        "rank_of_generators": int(matrix.rank()),
        "wall_seconds": round(outcome.wall_nanoseconds / 1e9, 1),
        "peak_rss_kib": outcome.peak_rss_kib,
    }
    closed = row["j_nonzero"] == 0 and row["rank_of_generators"] == row["quotient_dimension"] == count
    row["verdict"] = "ideal_of_s" if closed else "failed"
    return row


def run(job: tuple[str, str]) -> dict[str, Any]:
    """One case; its row is written at once, so a later case that fails or stalls keeps the finished ones."""
    row = (kernel if job[0] == "kernel" else closure)(job[1])
    (HERE / f"slice-rings-qi-{job[0]}-{job[1]}.json").write_text(json.dumps(row, indent=1) + "\n", encoding="utf-8")
    return row


def main() -> None:
    jobs = [("kernel", slug) for slug in SIGN] + [("closure", slug) for slug in ("e8-nm", "e8-np")]
    rows = parallel.ordered_map(run, jobs, min_items=2)
    record = {"schema": "a5-slice-rings-qi-v1", "field": "Q(i)", "cases": rows}
    (HERE / "slice-rings-qi.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    for row in rows:
        print(json.dumps(row))
    failed = [f"{row['check']} {row['slug']}" for row in rows if row["verdict"] == "failed"]
    if failed:
        raise SystemExit(f"over Q(i): {', '.join(failed)}")


if __name__ == "__main__":
    main()
