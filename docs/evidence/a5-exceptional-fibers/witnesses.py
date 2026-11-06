"""Identity and transport witnesses for the fiber registry.

Usage: witnesses.py OUT.jsonl   (run from any directory; Singular on PATH or in $SINGULAR)

Two kinds of row:
- `header-pair`: a legacy input that a certificate names, against the canonical producer header of the same fiber and
  prime. Mutual normal forms of J against std(J') and of G against std(J' + G') (and back) are all zero exactly when
  the two inputs define the same germ k[t]/J and the same ideal I. h_d and HF(k[y]/K2, d) depend only on I once G
  is a minimal generating set (h_1 = #G), so a pair row lets a legacy record certify the canonical fiber.
- `sign-isomorphism`: negating the variables `flip` carries each J and G generator of the `to` header to plus or minus
  the generator of the same index in the `from` header. The substitution is a ring automorphism of k[t] that fixes
  the point, maps J(to) onto J(from) and I(to) onto I(from), so y_i -> c_i y_i (c_i the G sign) carries L(from) onto
  L(to): the two fiber cones are isomorphic graded rings and h_d agrees in every degree. Where both K2 files exist,
  their mutual remainders after the y signs are a consistency check of that identity.
- `k2-span`: a degree-2 receipt certifies that its own relation file lies in L and spans L_2 (rank equals h_2 and
  every listed relation passes membership). The Hilbert counts of `k2-hilbert.jsonl` come from a K2 source file
  that may sit elsewhere, so each source is compared with the receipt's relation file by mutual normal forms in the
  same ring; zero both ways means the same span in the same generator order, and only then does the receipt bound
  HF of that source from above.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE / "working"
sys.path.insert(0, str(HERE / "replay" / "engine"))
import fiber_rank_v8 as eng  # noqa: E402

CANON = {32009: W / "build/inputs/p32009-r10754", 32029: W / "build/inputs/p32029-r9115"}
STEM = {"Iso": "iso-np", "W8 -> N-": "w8-nm", "E8-bar -> N-": "e8-nm", "E8-bar -> N+": "e8-np", "X-": "xm-nm",
        "E8-bar -> VB": "e8-vb"}  # fmt: skip
STEM_NAME = {"xm-nm": "X-", "xp-np": "X+", "e8-nm": "E8-bar -> N-", "e8-np": "E8-bar -> N+", "w8-nm": "W8 -> N-",
             "w8-np": "W8 -> N+"}  # fmt: skip


def singular(script: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp, "w.sing")
        path.write_text(script)
        res = subprocess.run(
            [os.environ.get("SINGULAR", "Singular"), "-q", "--no-rc", str(path)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True, timeout=900,
        )  # fmt: skip
    if any(ln.startswith("? ") for ln in res.stdout.splitlines()):
        raise RuntimeError(res.stdout[-400:])
    return res.stdout


def header_pair(legacy: Path, fiber: str, prime: int) -> dict:
    canon = CANON[prime] / f"{STEM[fiber]}.sing"
    p, names, j, g = eng.parse_header(str(legacy))
    q, names2, k, h = eng.parse_header(str(canon))
    if (p, names) != (q, names2):
        return {"kind": "header-pair", "legacy": str(legacy.relative_to(HERE)), "ok": False, "reason": "ring differs"}
    out = singular(
        f"ring r={p},({','.join(names)}),dp;\nideal J={','.join(j)};\nideal K={','.join(k)};\n"
        f"ideal G={','.join(g)};\nideal H={','.join(h)};\nideal sJ=std(J); ideal sK=std(K);\n"
        '"RESULT J",size(reduce(J,sK)),size(reduce(K,sJ));\n'
        "ideal sJG=std(J+G); ideal sKH=std(K+H);\n"
        '"RESULT I",size(reduce(G,sKH)),size(reduce(H,sJG));\nquit;\n'
    )
    vals = [int(x) for ln in out.splitlines() if ln.startswith("RESULT") for x in ln.split()[2:]]
    return {
        "kind": "header-pair", "fiber": fiber, "prime": prime, "legacy": str(legacy.relative_to(HERE)),
        "canonical": str(canon.relative_to(HERE)), "mutual_remainders": vals, "ok": vals == [0, 0, 0, 0],
    }  # fmt: skip


def sign_iso(prime: int, src: str, dst: str, flip: tuple[str, ...], k2_dst: Path | None, k2_src: Path | None) -> dict:
    _, names, jd, gd = eng.parse_header(str(CANON[prime] / f"{dst}.sing"))
    _, names_s, js_, gs_ = eng.parse_header(str(CANON[prime] / f"{src}.sing"))
    idx = [names.index(v) for v in flip]

    def signs(left: list[str], right: list[str]) -> list[int]:
        if names != names_s or len(left) != len(right):
            return [0]
        out = []
        for a, b in zip(left, right, strict=True):
            poly, target = eng.parse_poly(a, names, prime), eng.parse_poly(b, names, prime)
            moved = {m: (-c) % prime if sum(m[i] for i in idx) % 2 else c for m, c in poly.items()}
            neg = {m: (-c) % prime for m, c in target.items()}
            out.append(1 if moved == target else -1 if moved == neg else 0)
        return out

    jsg, gsg = signs(jd, js_), signs(gd, gs_)
    vals: list[int] | None = None
    if k2_dst is not None and k2_src is not None:
        subs = "".join(f"A=subst(A,y({i + 1}),-y({i + 1}));\n" for i, s in enumerate(gsg) if s == -1)
        out = singular(
            f"ring r={prime},(y(1..{len(gsg)})),dp;\n"
            f'execute("ideal A="+read("{k2_dst}")+";");\nexecute("ideal B="+read("{k2_src}")+";");\n{subs}'
            'ideal sA=std(A); ideal sB=std(B);\n"RESULT K2",size(reduce(A,sB)),size(reduce(B,sA));\nquit;\n'
        )
        vals = [int(x) for ln in out.splitlines() if ln.startswith("RESULT") for x in ln.split()[2:]]
    ok = 0 not in jsg and 0 not in gsg and vals in (None, [0, 0])
    return {
        "kind": "sign-isomorphism", "prime": prime, "from": STEM_NAME[src], "to": STEM_NAME[dst], "flip": list(flip),
        "J_signs": jsg, "G_signs": gsg, "k2_to": str(k2_dst.relative_to(HERE)) if k2_dst else None,
        "k2_from": str(k2_src.relative_to(HERE)) if k2_src else None,
        "k2_to_sha256": digest(k2_dst) if k2_dst else None, "k2_from_sha256": digest(k2_src) if k2_src else None,
        "k2_mutual_remainders": vals, "ok": ok,
    }  # fmt: skip


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def k2_span(fiber: str, prime: int, ngens: int, source: Path, receipt: Path) -> dict:
    r = json.loads(receipt.read_text())
    # Legacy receipts record relation_file relative to the repository root; the file sits beside the receipt.
    rel = receipt.parent / Path(str(r.get("relation_file", "relations-d2.rel"))).name
    out = singular(
        f"ring r={prime},(y(1..{ngens})),dp;\n"
        f'execute("ideal A="+read("{source}")+";");\nexecute("ideal B="+read("{rel}")+";");\n'
        'ideal sA=std(A); ideal sB=std(B);\n"RESULT K2",size(reduce(A,sB)),size(reduce(B,sA));\nquit;\n'
    )
    vals = [int(x) for ln in out.splitlines() if ln.startswith("RESULT") for x in ln.split()[2:]]
    return {
        "kind": "k2-span", "fiber": fiber, "prime": prime, "k2_source": str(source.relative_to(HERE)),
        "receipt": str(receipt.relative_to(HERE)), "receipt_relations": str(rel.relative_to(HERE)),
        "k2_source_sha256": digest(source), "receipt_relations_sha256": digest(rel),
        "mutual_remainders": vals, "ok": vals == [0, 0],
    }  # fmt: skip


def run(task: tuple) -> dict:
    """One witness row; a module-level dispatcher so parallel.ordered_map can pickle the work items."""
    kind, args = task
    fns: dict[str, Callable[..., dict]] = {"header-pair": header_pair, "sign-isomorphism": sign_iso, "k2-span": k2_span}
    fn = fns[kind]
    return fn(*args)


def main() -> int:
    sys.path.insert(0, str(HERE))
    for parent in HERE.parents:
        if (parent / "gororoba_quantum" / "parallel.py").is_file():
            sys.path.insert(0, str(parent / "gororoba_quantum"))
            break
    import build_registry as reg
    import k2_hilbert

    import parallel

    e8 = W / "distribute/out/a5-e8-d2"
    small = W / "distribute/out/a5-p2-small"
    tasks: list[tuple] = [
        ("header-pair", (reg.header_file(inp), fiber, prime))
        for _sha, (fiber, prime, inp) in sorted(reg.LEGACY_HEADERS.items())
    ]
    tasks += [
        ("sign-isomorphism", (32009, "e8-nm", "e8-np", ("t8", "t9"), W / "runs/e8_a2/e8_k2.rel",
                              e8 / "e8nm_p1/d2/relations-upto-d2.rel")),
        ("sign-isomorphism", (32029, "e8-nm", "e8-np", ("t8", "t9"), e8 / "e8np_p2/d2/relations-upto-d2.rel",
                              e8 / "e8nm_p2/d2/relations-upto-d2.rel")),
        ("sign-isomorphism", (32009, "xm-nm", "xp-np", ("t9",), None, None)),
        ("sign-isomorphism", (32029, "xm-nm", "xp-np", ("t9",), small / "xp_p2/d2/relations-upto-d2.rel",
                              small / "xm_p2/d2/relations-upto-d2.rel")),
        ("sign-isomorphism", (32009, "w8-nm", "w8-np", ("t9",), None, None)),
        ("sign-isomorphism", (32029, "w8-nm", "w8-np", ("t9",), None, None)),
    ]  # fmt: skip
    rows = parallel.ordered_map(run, tasks, min_items=1)
    # Receipts validate against the witnessed headers, so the k2-span rows wait for the header-pair rows.
    witnessed = {w["legacy"] for w in rows if w["kind"] == "header-pair" and w["ok"]}
    good, _ = reg.receipts(reg.known_headers(witnessed))
    spans = [
        ("k2-span", (fib, prime, ngens, W / src, HERE / g["path"]))
        for g in good
        if g["d"] == 2
        for fib, prime, ngens, src in k2_hilbert.SOURCES
        if fib == g["fiber"] and prime == g["prime"]
    ]
    rows += parallel.ordered_map(run, spans, min_items=1)
    Path(sys.argv[1]).write_text("".join(json.dumps(r) + "\n" for r in rows))
    for r in rows:
        print(
            r["kind"],
            r.get("fiber", r.get("to")),
            r["prime"],
            r.get("legacy", r.get("receipt", "")),
            "ok" if r["ok"] else "FAIL",
        )
    return 0 if all(r["ok"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
