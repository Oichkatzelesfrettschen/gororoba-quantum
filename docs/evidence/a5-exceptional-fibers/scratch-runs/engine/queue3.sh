#!/bin/sh
# Laptop engine queue: E8-bar -> N+ degree 3 at 32009, raw mode, under the shared memory lock.
set -eu
cd "$HOME/a5/engine"
export PATH="$HOME/a5env/bin:$PATH"
flock "$HOME/a5/engine/.mem.lock" /bin/sh "$HOME/a5/engine/ladder-v6.sh" "$HOME/a5/engine/e8np_d3_p1_raw_v6.jsonl" 225 e8np_p1/input.sing 3 -- 11 12
