#!/bin/sh
# Run one job under an address-space cap with a 30 s RSS and MemAvailable trace; writes NAME.exit when done.
# Usage: remote-run.sh NAME AS_BYTES COMMAND [ARGS...]
set -eu
name=$1; as=$2; shift 2
cd "$HOME/work"
date -u +%s > "$name.started"
prlimit --as="$as" "$@" > "$name.log" 2>&1 < /dev/null & pid=$!
(
  printf 'elapsed_s\trss_kib\tmem_available_kib\n'
  start=$(cat "$name.started")
  while kill -0 "$pid" 2>/dev/null; do
    rss=$(awk '/^VmRSS:/ {print $2}' "/proc/$pid/status" 2>/dev/null || echo 0)
    avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    printf '%s\t%s\t%s\n' $(( $(date -u +%s) - start )) "${rss:-0}" "$avail"
    sleep 30
  done
) > "$name.samples.tsv" &
status=0; wait "$pid" || status=$?
echo "$status" > "$name.exit"
