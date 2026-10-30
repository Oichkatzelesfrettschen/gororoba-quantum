#!/bin/sh
# Start W8 degree-3 method A once the X- or Iso method-B job has ended (frees its 16G), within 12 h.
set -eu
cd "$(dirname "$0")"
end=$(( $(date +%s) + 43200 ))
while [ ! -f ../s2/rc ] && [ ! -f ../iso_b/rc ]; do
  [ "$(date +%s)" -ge "$end" ] && { echo "queue deadline"; exit 2; }
  sleep 120
done
date -u +%FT%TZ > started
systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 env MALLOC_ARENA_MAX=2 \
  timeout -k 30 43200 nice Singular -q --no-rc --cpus=1 input.sing > out.log 2>&1 && st=0 || st=$?
echo "exit=$st" > rc
