#!/bin/sh
# Run fiber_rank_v6 at increasing N until r_N equals TARGET. Usage: ladder-v6.sh OUT TARGET HEADER D FLAGS -- N...
set -eu
out=$1; target=$2; h=$3; d=$4; shift 4
flags=""
while [ "$1" != "--" ]; do flags="$flags $1"; shift; done
shift
for N in "$@"; do
  # shellcheck disable=SC2086
  /usr/bin/time -f "N=$N wall %e s maxrss %M KiB" -a -o "$out.resources" python3 "$(dirname "$0")/fiber_rank_v6.py" "$h" "$d" "$N" $flags >> "$out" 2>> "$out.err" || { echo "N=$N exit $?" >> "$out.err"; continue; }
  r=$(tail -1 "$out" | sed -n 's/.*"r_N": \([0-9]*\), "per_block".*/\1/p')
  echo "N=$N r_N=$r target=$target" >> "$out.err"
  if [ "$r" = "$target" ]; then exit 0; fi
done
echo "target $target not reached" >> "$out.err"
