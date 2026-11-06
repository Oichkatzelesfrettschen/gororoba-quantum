#!/bin/sh
# Replay of the arc certificates: every target when called without arguments, else the targets named.
# Usage: sh replay.sh [e8nm-p32009 e8nm-p32029 e8np-p32009 e8np-p32029]
# Each Singular and Python process runs under the 8 GiB address-space cap set below and under the timeouts inside
# run_target.py. The family scans use GOROROBA_WORKERS single-threaded Singular processes (default 3); scratch goes
# to $ARCS_WORK (default $TMPDIR/a5-arcs-work). The N- target of a prime runs before its N+ target, which compares
# against the N- ideals.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON
GOROROBA_WORKERS=${GOROROBA_WORKERS:-3}
export GOROROBA_WORKERS
ulimit -v 8388608
here=$(cd "$(dirname "$0")" && pwd)
if [ "$#" -eq 0 ]; then
  set -- e8nm-p32009 e8nm-p32029 e8np-p32009 e8np-p32029
fi
exec "$PYTHON" "$here/run_target.py" "$@"
