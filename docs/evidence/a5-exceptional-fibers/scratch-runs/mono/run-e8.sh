#!/bin/sh
set -u
cd ~/a5/gq-main
export PATH="$HOME/a5env/lib/python3.13/site-packages/sage_wheels/bin:$HOME/a5env/bin:$PATH" GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
out=~/a5/mono
for spec in "2 10" "2 12" "3 12" "3 14" "4 14" "4 16"; do
  set -- $spec
  name=e8-nm-p32009-d$1-n$2
  /usr/bin/time -v systemd-run --user --scope -q -p MemoryMax=30G -p MemorySwapMax=0 \
    ~/a5env/bin/python docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_ladder.py \
    --slug e8-nm --prime 32009 --degree "$1" --order "$2" --out "$out/$name.json" > "$out/$name.log" 2>&1
  echo "$name rc=$?" >> "$out/summary"
done
