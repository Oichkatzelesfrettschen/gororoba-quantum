#!/bin/sh
# usage: run.sh LOG cmd...
log=$1; shift
MALLOC_ARENA_MAX=2 systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 timeout -k 10 1800 "$@" > "$log" 2>&1
echo "exit $?" >> "$log"
