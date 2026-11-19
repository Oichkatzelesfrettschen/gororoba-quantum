#!/bin/sh
# Monomial-span probe of the same-sign X slice: four (slug, prime, order) cases, two at a time.
set -u
cd ~/a5/gq-main/docs/evidence/a5-exceptional-fibers/monomial-ladder
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/mprobe
mkdir -p "$out"
run() { n=monomial-probe-$1-p$2-n$3; systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 ~/a5env/bin/python monomial_probe.py --slug "$1" --prime "$2" --order "$3" --out "$out/$n.json" > "$out/$n.log" 2>&1; echo "$n rc=$?" >> "$out/summary"; }
run xm-nm 32009 12 & run xm-nm 32029 12 & wait
run xp-np 32009 12 & run xp-np 32029 12 & wait
run xm-nm 32009 14
touch "$out/done"
