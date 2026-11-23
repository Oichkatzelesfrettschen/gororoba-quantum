#!/bin/sh
# post-check of the degree-2 receipt of E8-bar -> N+ at (32009, 21255); run from the repository root after the driver.
set -u
D=${1:?receipt directory}
W=docs/evidence/a5-exceptional-fibers/working
K=$W/runs/e8-rees-fibers-v2-kcompare-p32009
B=$W/runs/e8-slice-equivalence-p32009
PYTHON=${PYTHON:-python3}
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
ideal C=A0; C[1]=C[1]+y(1)^2; ideal sC=std(C);
"RESULT control receipt with y(1)^2 added: dim mult",dim(sC),mult(sC),"receipt modulo it",size(reduce(A0,sC)),"it modulo receipt",size(reduce(C,sA));
"EXIT 0"; quit;
EOF
{
  Singular --version < /dev/null | head -n 1
  sha256sum "$REL" "$W/runs/e8_a2/e8_k2.rel" "$W/distribute/out/a5-e8-d2/e8nm_p1/d2/relations-upto-d2.rel"
  "$PYTHON" -c 'import json,sys; r=json.load(open(sys.argv[1])); print("receipt status", r["status"], "generators", r["generator_count"], "relations", r["relation_count"], "rank_h_d", r.get("rank_h_d")); print("membership_check", r.get("membership_check"))' "$D/receipt/receipt-d2.json"
  Singular -q "$D/post.sing" < /dev/null
  echo "RC $?"
} > "$D/post.log" 2>&1
for c in np nm; do
  "$PYTHON" "$B/slice_bridge.py" "e8-$c-weight-vs-np-r21255" "$K/KA-e8-$c.sing" "$D/KH-e8-np-r21255.sing" "$D/bridge-weight-$c.json" >> "$D/post.log" 2>&1
  echo "BRIDGE RC $?" >> "$D/post.log"
done
