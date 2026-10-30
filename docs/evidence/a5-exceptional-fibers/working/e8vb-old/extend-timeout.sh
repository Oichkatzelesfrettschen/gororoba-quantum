#!/bin/sh
# Hold a running `timeout` process stopped so its alarm stays pending, and resume it at a new deadline or as soon
# as its child exits. A stopped timeout cannot reap its child, which then stays a zombie that kill -0 still finds,
# so the child's state comes from /proc. Exit 0 child ended, 2 new deadline reached.
# Usage: extend-timeout.sh TIMEOUT_PID CHILD_PID DEADLINE_EPOCH
set -eu
tpid=$1; cpid=$2; deadline=$3; child=
resume() { kill -CONT "$tpid" 2>/dev/null || :; [ -n "$child" ] && kill "$child" 2>/dev/null || :; }
trap resume EXIT
trap 'exit 130' INT TERM HUP
kill -STOP "$tpid"
while :; do
  state=$(awk '{print $3}' "/proc/$cpid/stat" 2>/dev/null || echo X)
  case "$state" in Z|X) echo "child $cpid ended; timeout resumed"; exit 0;; esac
  if [ "$(date +%s)" -ge "$deadline" ]; then echo "deadline reached; timeout resumed and ends the child"; exit 2; fi
  sleep 20 & child=$!; wait "$child"; child=
done
