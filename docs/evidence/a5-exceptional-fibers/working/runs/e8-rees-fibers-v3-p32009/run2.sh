#!/bin/sh
# Usage: run2.sh SINGULAR LIMIT_SECONDS NAME...  One Singular process per script, at once. A log is never
# overwritten; each gets the tool version, the script digest, a timing file and an EXIT line.
set -eu
cd "$(dirname "$0")"
bin=$1; limit=$2; shift 2
for n in "$@"; do
  [ -e "$n.log" ] && { echo "refuse: $n.log exists" >&2; continue; }
  ( { "$bin" --version | head -n 1; sha256sum "$n.sing"; } > "$n.log" 2>&1
    rc=0; /usr/bin/time -v -o "$n.time" timeout -k 30 "$limit" "$bin" -q --no-rc "$n.sing" </dev/null >>"$n.log" 2>&1 || rc=$?
    echo "EXIT $rc" >>"$n.log" ) &
done
wait
