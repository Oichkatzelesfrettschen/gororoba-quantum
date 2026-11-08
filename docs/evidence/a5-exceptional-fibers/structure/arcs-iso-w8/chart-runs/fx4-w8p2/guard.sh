#!/bin/sh
# Extension of the Iso chart past its 22 h timeout: Singular pid 5374 runs on under the original 55 GB scope.
# Samples RSS every 60 s, writes an "ended" marker when the pid exits, and kills it at the 24 h extension deadline.
set -u
cd "$HOME/a5iso"
pid=5374; end=$(( $(date +%s) + 86400 ))
while kill -0 "$pid" 2>/dev/null; do
  echo "$(date -u +%FT%TZ) $(ps -o rss= -p "$pid")" >> rss.txt
  if [ "$(date +%s)" -ge "$end" ]; then kill -TERM "$pid"; sleep 30; kill -KILL "$pid" 2>/dev/null; echo "$(date -u +%FT%TZ) iso slice-junk extension deadline kill" >> events; fi
  sleep 60
done
echo "$(date -u +%FT%TZ) iso slice-junk ended (last RESULT: $(grep -a RESULT chart.log | tail -1 | cut -c1-120))" >> events
