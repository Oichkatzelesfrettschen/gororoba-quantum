#!/bin/sh
# Run fiber_rank_v7 at increasing N until r_N equals TARGET. Usage: ladder-v7.sh OUT TARGET HEADER D FLAGS -- N...
# Each run writes a fresh stdout file; gate_record.py binds it to the engine, header, d and N before it joins OUT.
set -u
PYTHON=${PYTHON:-python3}
here=$(dirname "$0")
out=$1; target=$2; h=$3; d=$4; shift 4
flags=""
while [ "$1" != "--" ]; do flags="$flags $1"; shift; done
shift
tmp=$(mktemp -d) || exit 1
trap 'rm -rf "$tmp"' EXIT INT TERM
for N in "$@"; do
  : > "$tmp/run.out"
  # shellcheck disable=SC2086
  if ! /usr/bin/time -f "N=$N wall %e s maxrss %M KiB" -a -o "$out.resources" "$PYTHON" "$here/fiber_rank_v7.py" "$h" "$d" "$N" $flags > "$tmp/run.out" 2>> "$out.err"; then
    echo "N=$N exit $?" >> "$out.err"; continue
  fi
  rec=$("$PYTHON" "$here/gate_record.py" "$tmp/run.out" "$here/fiber_rank_v7.py" "$h" "$d" "$N" any 2>> "$out.err") || { echo "N=$N record rejected" >> "$out.err"; continue; }
  printf '%s\n' "$rec" >> "$out"
  r=$(printf '%s\n' "$rec" | "$PYTHON" -c 'import json,sys; print(json.load(sys.stdin)["r_N"])')
  echo "N=$N r_N=$r target=$target" >> "$out.err"
  [ "$r" = "$target" ] && exit 0
done
echo "target $target not reached" >> "$out.err"
exit 3
