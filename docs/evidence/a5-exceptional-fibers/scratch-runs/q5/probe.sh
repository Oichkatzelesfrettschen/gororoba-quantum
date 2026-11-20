#!/bin/sh
# Truncated method A: r = vdim std(J + m^N + m S) - vdim std(J + m^N + m S + S), S = the K2-standard degree-d products
# of G cut at order N.  It equals the engine's r_N; the cost under test is one std of an ideal that holds m S.
# Usage: probe.sh P D N  (writes out/qP-dD-nN.{log,time})
set -eu
p=$1 d=$2 n=$3
cd "$(dirname "$0")"
SINGULAR="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin/Singular"
hdr="$HOME/a5/engine/v9m/e8-nm-p$p.sing"
rel="$HOME/a5/engine/v10/k2/p$p/relations-d2.rel"
mkdir -p out
s=out/q$p-d$d-n$n.sing
{
    cat "$hdr"
    echo "int N=$n; int d=$d; int t0=timer; system(\"--ticks-per-sec\",1);"
    echo "ring Y=$p,(y(1..size(G))),dp; ideal K="
    sed '$ s/,[[:space:]]*$//' "$rel"
    echo "; K=std(K); ideal kb=kbase(K,d); \"standard\", size(kb);"
    echo "setring r; map f=Y,G; ideal S=jet(f(kb),N-1);"
    echo "ideal Q=J+maxideal(N)+maxideal(1)*S; ideal Qs=std(Q); int a=vdim(Qs); \"vdimQ\", a, \"std_s\", timer-t0;"
    echo "ideal Qp=std(Qs+S); int b=vdim(Qp); \"r\", a-b, \"total_s\", timer-t0; quit;"
} > "$s"
/usr/bin/time -f "wall %e s maxrss %M KiB" -o "out/q$p-d$d-n$n.time" "$SINGULAR" -q "$s" > "out/q$p-d$d-n$n.log" 2>&1
