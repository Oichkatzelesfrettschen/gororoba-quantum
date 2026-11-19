#!/bin/sh
# Replay of the monomial-ladder float64 cells with the source-hashing fast_ladder.py of the gq-main copy.
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/replay818
mkdir -p "$out"
for spec in "e8-nm 32009 3 14" "xm-nm 32009 8 32" "xm-nm 32009 8 34" "xm-nm 32029 7 29" "xm-nm 32029 7 31"; do
  set -- $spec
  name=float64-$1-p$2-d$3-n$4
  systemd-run --user --scope -q -p MemoryMax=20G -p MemorySwapMax=0 \
    ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/monomial-ladder/fast_ladder.py --slug "$1" --prime "$2" \
    --degree "$3" --order "$4" --threads 16 --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$?" >> "$out/summary"
done
touch "$out/done"
