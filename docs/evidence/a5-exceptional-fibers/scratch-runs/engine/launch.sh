#!/bin/sh
set -eu
cd "$HOME/a5/engine"
launch() {
  u=$1; shift
  systemd-run --user --unit="$u" -p MemoryMax=22G -p MemorySwapMax=0 --working-directory="$HOME/a5/engine" \
    --setenv=PYTHON="$HOME/a5env/bin/python" --setenv=GOROROBA_PARALLEL_DIR="$HOME/a5/gq" --setenv=GOROROBA_WORKERS=12 \
    /bin/sh "$HOME/a5/engine/ladder-engine.sh" "$@"
}
launch a5-iso-d5 iso_d4/input.sing 5 1316 iso_d5.jsonl 15 16 17
launch a5-w8-d4 w8_d3/input.sing 4 1725 w8_d4.jsonl 12 13 14
