#!/bin/sh
# Ends the first VB queue (tmux session vb) when it reaches the p = 32029 degree-6 cells, which session vbp2 owns.
set -eu
cd "$HOME/a5/engine/v11"
while tmux has-session -t vb 2>/dev/null; do
    if grep -q "start e8vb_d6_n20_p32029" out/cells.events; then
        tmux kill-session -t vb
        echo "$(date -u +%FT%TZ) guard ended session vb before its duplicate p32029 cells" >> out/cells.events
        exit 0
    fi
    sleep 20
done
