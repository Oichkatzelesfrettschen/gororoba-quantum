#!/bin/sh
# E8-bar -> VB at p = 32009: std of J + m^N in the local ordering ds (the quotient is Artinian, so Singular finds its
# highest corner from m^N) at N = 15 to 18, one process each; owner-approved test, no record uses it.
set -eu
S=${SINGULAR:-Singular}
cd "$(dirname "$0")"
for N in 15 16 17 18; do
  ( rc=0; /usr/bin/time -v -o "ds-n$N.time" timeout 14400 "$S" -q --no-rc "ds-n$N.sing" < /dev/null > "ds-n$N.log" 2>&1 || rc=$?
    [ "$rc" -ne 0 ] || grep -q "^RESULT kbase_size" "ds-n$N.log" || rc=3
    echo "$rc" > "ds-n$N.status"; exit "$rc" ) &
  pids="${pids:-} $!"
done
fail=0
for pid in $pids; do wait "$pid" || fail=1; done
exit "$fail"
