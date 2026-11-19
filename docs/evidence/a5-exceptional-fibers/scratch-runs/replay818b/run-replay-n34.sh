#!/bin/sh
# After the running replays end, replay the
# same-sign X degree-8 cell at order 34 with the source-hashing fast_ladder.py under a 40 GB cap.
set -u
until [ -e ~/a5/replay818/done ]; do sleep 60; done
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/replay818b; mkdir -p "$out"
name=float64-xm-nm-p32009-d8-n34
/usr/bin/time -v systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 \
  ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/monomial-ladder/fast_ladder.py --slug xm-nm --prime 32009 \
  --degree 8 --order 34 --threads 24 --out "$out/$name.json" > "$out/$name.log" 2> "$out/time.err"
echo "$name rc=$?" >> "$out/summary"; touch "$out/done"
