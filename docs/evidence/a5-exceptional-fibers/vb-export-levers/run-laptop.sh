#!/bin/sh
# E8-bar -> VB std(J + m^N) at p = 32009 on the Windows workstation under WSL: the std baseline at N = 18 beside slimgb
# at N = 18, 19 and 20, all at once, one core and about 2 GiB each; each stops at 10,800 s, the limit in force at launch.
# Singular takes stdin from /dev/null; each child's exit status lands in laptop-vb-<tag>.status.
set -eu
S=${SINGULAR:-Singular}
cd "$(dirname "$0")"
for t in n18-base n18-slimgb n19-slimgb n20-slimgb; do
  (
    rc=0
    /usr/bin/time -v -o "laptop-vb-$t.time" timeout -k 30 10800 "$S" -q --no-rc "laptop-vb-$t.sing" \
      < /dev/null > "laptop-vb-$t.log" 2>&1 || rc=$?
    echo "$rc" > "laptop-vb-$t.status"
    exit "$rc"
  ) &
  pids="${pids:-} $!"
done
fail=0
for pid in $pids; do wait "$pid" || fail=1; done
for f in laptop-vb-*.status; do printf '%s %s\n' "$f" "$(cat "$f")"; done
exit "$fail"
