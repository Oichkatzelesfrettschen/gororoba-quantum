#!/bin/sh
# post-check of the degree-2 receipt of E8-bar -> N+ at (32009, 21255); run from the repository root after the driver.
# Usage: post_check.sh RECEIPT_DIRECTORY. Exits nonzero unless the receipt is degree-certified with 148 relations and
# 0 failures, the Singular check prints its PASS verdict and both map searches print map_found.
set -eu
D=${1:?receipt directory}
W=docs/evidence/a5-exceptional-fibers/working
K=$W/runs/e8-rees-fibers-v2-kcompare-p32009
B=$W/runs/e8-slice-equivalence-p32009
PYTHON=${PYTHON:-python3}
export PYTHON PYTHONDONTWRITEBYTECODE=1
REL="$D/receipt/relations-upto-d2.rel"
{ printf 'ideal KH=\n'; cat "$REL"; printf ';\n'; } > "$D/KH-e8-np-r21255.sing"
cat > "$D/post.sing" <<EOF
ring r=32009,(y(1..21)),dp; option(redSB);
execute("ideal A0="+read("$REL")+";");
execute("ideal KP="+read("$W/runs/e8_a2/e8_k2.rel")+";");
execute("ideal KM="+read("$W/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel")+";");
ideal sA=std(A0); ideal sP=std(KP); ideal sM=std(KM);
"RESULT receipt generators",size(minbase(A0)),"dim",dim(sA),"mult",mult(sA);
"RESULT hilb",hilb(sA,2);
"RESULT against N+ K2 at root 10754",size(reduce(A0,sP)),size(reduce(KP,sA));
"RESULT against N- relations at root 10754",size(reduce(A0,sM)),size(reduce(KM,sA));
ideal C=A0; C[1]=C[1]+y(1)^2; ideal sC=std(C); int c1=size(reduce(A0,sC)); int c2=size(reduce(C,sA));
"RESULT control receipt with y(1)^2 added: dim mult",dim(sC),mult(sC),"receipt modulo it",c1,"it modulo receipt",c2;
def hv=hilb(sA,2); "RESULT hilb type",typeof(hv);
int good=(size(minbase(A0))==148 and dim(sA)==5 and mult(sA)==11 and hv[1]==1 and hv[2]==16 and hv[3]==-12 and hv[4]==10 and hv[5]==-5 and hv[6]==1 and (c1>0 or c2>0));
if (good) { "POST VERDICT PASS"; } else { "POST VERDICT FAIL"; }
"EXIT 0"; quit;
EOF
{
  Singular --version < /dev/null | head -n 1
  sha256sum "$REL" "$W/runs/e8_a2/e8_k2.rel" "$W/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel" "$B/slice_bridge.py"
} > "$D/post.log" 2>&1
"$PYTHON" -c 'import json,sys; r=json.load(open(sys.argv[1])); print("receipt status", r["status"], "generators", r["generator_count"], "relations", r["relation_count"], "rank_h_d", r.get("rank_h_d")); print("membership_check", r.get("membership_check")); sys.exit(0 if r["status"] == "degree-certified" and r["relation_count"] == 148 and r["generator_count"] == 21 and r["membership_check"] == {"checked": 148, "failures": 0} else 1)' "$D/receipt/receipt-d2.json" >> "$D/post.log" 2>&1
Singular -q --no-warn "$D/post.sing" < /dev/null >> "$D/post.log" 2>&1
grep -q '^POST VERDICT PASS$' "$D/post.log"
for c in np nm; do
  "$PYTHON" "$B/slice_bridge.py" "e8-$c-weight-vs-np-r21255" "$K/KA-e8-$c.sing" "$D/KH-e8-np-r21255.sing" "$D/bridge-weight-$c.json" >> "$D/post.log" 2>&1
  grep -q "^BRIDGE e8-$c-weight-vs-np-r21255 .* verdict map_found$" "$D/post.log"
done
echo "post_check: PASS" >> "$D/post.log"
