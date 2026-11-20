#!/bin/sh
# Run fiber_rank at increasing N until r_N equals the K2 count. Usage: ladder-engine.sh HEADER D TARGET OUT N...
set -eu
h=$1; d=$2; target=$3; out=$4; shift 4
for N in "$@"; do
  /usr/bin/time -f "N=$N wall %e s maxrss %M KiB" -a -o "$out.time" "$PYTHON" "$HOME/a5/engine/fiber_rank_v4.py" "$h" "$d" "$N" >> "$out" 2>> "$out.err" || { echo "N=$N exit $?" >> "$out.err"; continue; }
  r=$(tail -1 "$out" | sed -n 's/.*"r_N": \([0-9]*\), "per_block".*/\1/p')
  echo "N=$N r_N=$r target=$target" >> "$out.err"
  [ "$r" = "$target" ] && break
done
