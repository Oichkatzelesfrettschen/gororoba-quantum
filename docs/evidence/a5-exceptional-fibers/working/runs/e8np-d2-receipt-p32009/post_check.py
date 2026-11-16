"""Post-check of the direct E8-bar -> N+ degree-2 receipt at 32009.

Usage: post_check.py RELATIONS.rel [receipt-d2.json]   (run from the repository root)
Two comparisons in F_32009 on the y(1..21) coordinates of the e8-np header:
  direct span: the receipt relations against the retained N+ K2 file (working/runs/e8_a2/e8_k2.rel), no substitution;
  sign transport: the receipt relations with the y signs of the t8, t9 flip against the retained N- receipt relations
  (working/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel), the witnesses.py sign-isomorphism row.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "docs/evidence/a5-exceptional-fibers")
import witnesses as wit

rel = Path(sys.argv[1]).resolve()
if len(sys.argv) > 2:
    r = json.loads(Path(sys.argv[2]).read_text())
    print("receipt status", r["status"], "generators", r["generator_count"], "relations", r["relation_count"], "rank_h_d", r.get("rank_h_d"))
    print("membership_check", r.get("membership_check"), "stage_seconds", r.get("stage_seconds_not_cumulative"))
    print("stages", json.dumps(r.get("stages"))[:3000])
    assert r["status"] == "degree-certified" and r["relation_count"] == 148 and r["generator_count"] == 21
prime = 32009
n_plus_k2 = (wit.W / "runs/e8_a2/e8_k2.rel").resolve()
n_minus = (wit.W / "distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel").resolve()
print("relations", rel.name, wit.digest(rel))
print("retained N+ K2", n_plus_k2.name, wit.digest(n_plus_k2))
print("retained N- receipt relations", n_minus.name, wit.digest(n_minus))
_, names, jd, gd = wit.eng.parse_header(str(wit.CANON[prime] / "e8-np.sing"))
_, names_s, js_, gs_ = wit.eng.parse_header(str(wit.CANON[prime] / "e8-nm.sing"))
assert names == names_s
idx = [names.index(v) for v in ("t8", "t9")]
def signs(left, right):
    out = []
    for a, b in zip(left, right, strict=True):
        poly, target = wit.eng.parse_poly(a, names, prime), wit.eng.parse_poly(b, names, prime)
        moved = {m: (-c) % prime if sum(m[i] for i in idx) % 2 else c for m, c in poly.items()}
        neg = {m: (-c) % prime for m, c in target.items()}
        out.append(1 if moved == target else -1 if moved == neg else 0)
    return out
jsg, gsg = signs(jd, js_), signs(gd, gs_)
print("J signs", jsg)
print("G signs", gsg)
assert 0 not in jsg and 0 not in gsg
subs = "".join(f"A=subst(A,y({i + 1}),-y({i + 1}));\n" for i, s in enumerate(gsg) if s == -1)
script = (
    f"ring r={prime},(y(1..{len(gsg)})),dp;\n"
    f'execute("ideal A0="+read("{rel}")+";");\nexecute("ideal K="+read("{n_plus_k2}")+";");\n'
    f'execute("ideal B="+read("{n_minus}")+";");\nideal A=A0;\n{subs}'
    'ideal sA0=std(A0); ideal sK=std(K); ideal sA=std(A); ideal sB=std(B);\n'
    '"RESULT direct",size(reduce(A0,sK)),size(reduce(K,sA0));\n'
    '"RESULT transport",size(reduce(A,sB)),size(reduce(B,sA));\n'
    '"RESULT dims",dim(sA0),mult(sA0),size(minbase(sA0));\n"RESULT hilb",hilb(sA0,2);\n'
    'ideal C=K; C[1]=C[1]+y(1)^2; ideal sC=std(C);\n'
    '"RESULT control_direct",size(reduce(A0,sC)),size(reduce(C,sA0));\n'
    'ideal D=B; D[1]=D[1]+y(1)^2; ideal sD=std(D);\n'
    '"RESULT control_transport",size(reduce(A,sD)),size(reduce(D,sA));\nquit;\n'
)
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp, "post.sing")
    p.write_text(script)
    res = subprocess.run(["Singular", "-q", "--no-rc", str(p)], stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True, timeout=900)
print(res.stdout.strip())
def pair(tag):
    return [l.split()[2:] for l in res.stdout.splitlines() if l.startswith("RESULT " + tag + " ")]
good = pair("direct") == [["0", "0"]] and pair("transport") == [["0", "0"]]
bad = pair("control_direct") != [["0", "0"]] and pair("control_transport") != [["0", "0"]]
print("POST RESULT direct", pair("direct"), "transport", pair("transport"), "controls_reject", int(bad), "pass", int(good and bad))
sys.exit(0 if good and bad else 1)
