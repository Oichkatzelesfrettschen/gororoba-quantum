#!/bin/sh
cd "$(dirname "$0")" || exit 1
for N in 7 8 9; do
  /usr/bin/time -v Singular -q --no-rc "sing$N.sing" < /dev/null > "sing$N.log" 2> "sing$N.time"
  systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 /usr/bin/time -v msolve -t 4 -g 1 -v 2 -f "jm$N.ms" -o "msolve$N.lead" > "msolve$N.log" 2> "msolve$N.time" || echo "msolve N=$N rc=$?" >> events
done
echo done >> events
