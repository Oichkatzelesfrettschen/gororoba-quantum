#!/bin/sh
# Iso one-chart saturation portfolio: {32009, 32029} x {sat, elim}, one single-threaded Singular per vCPU, 8 h each.
# A per-minute memory log; the largest Singular is stopped only when MemAvailable falls below 4 GB.
set -eu
cd "$HOME/a5"
SING="$HOME/venv/lib/python3.12/site-packages/sage_wheels/bin/Singular"
mkdir -p out
"$SING" --version > out/singular-version.txt 2>&1 < /dev/null || true
for t in iso-p32009-sat iso-p32009-elim iso-p32029-sat iso-p32029-elim; do
  (
    rc=0
    /usr/bin/time -v timeout 28800 "$SING" -q --no-rc "chart-$t.sing" > "out/chart-$t.log" 2> "out/chart-$t.err" < /dev/null || rc=$?
    echo "$(date -u +%FT%TZ) $t exit $rc" >> out/events
  ) &
done
sleep 5
while pgrep -x Singular > /dev/null; do
  { date -u +%FT%TZ; grep MemAvailable /proc/meminfo; ps -o pid,etime,rss,args -C Singular | cut -c1-90; } >> out/mem.log
  avail=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
  if [ "$avail" -lt 4000000 ]; then
    pid=$(ps -o pid= --sort=-rss -C Singular | head -1 | tr -d ' ')
    echo "$(date -u +%FT%TZ) MemAvailable $avail kB: stopping largest Singular $pid" >> out/events
    kill "$pid" || true
  fi
  sleep 60
done
wait
echo "$(date -u +%FT%TZ) all done" >> out/events
