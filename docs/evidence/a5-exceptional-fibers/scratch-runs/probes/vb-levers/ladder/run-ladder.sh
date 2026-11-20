#!/bin/sh
# E8-bar -> VB, p = 32009: std and slimgb of J + m^N for N = 1 to 17, twelve Singular processes at a time on the
# Windows workstation; each writes its reduced basis (.s), kbase and exit status, stdin from /dev/null.
set -eu
S=${SINGULAR:-Singular}
export S
cd "$(dirname "$0")"
ls ladder-n*-*.sing | sort -t n -k 2 -n | xargs -P 12 -I{} sh -c '
  t=$(basename {} .sing); rc=0
  /usr/bin/time -v -o "$t.time" "$S" -q --no-rc {} < /dev/null > "$t.log" 2>&1 || rc=$?
  echo "$rc" > "$t.status"'
echo "ladder done"
