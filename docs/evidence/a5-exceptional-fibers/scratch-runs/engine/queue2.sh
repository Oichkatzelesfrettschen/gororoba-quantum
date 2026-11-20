#!/bin/sh
# Laptop engine queue: second-prime certificates, one ladder at a time under the shared memory lock.
set -eu
cd "$HOME/a5/engine"
export PATH="$HOME/a5env/bin:$PATH"
q() { flock "$HOME/a5/engine/.mem.lock" /bin/sh "$HOME/a5/engine/ladder-v6.sh" "$@" || echo "ladder $1 exit $?" >> queue2.err; }
q "$HOME/a5/engine/w8_d4_p1_v6.jsonl" 1725 w8_p1/input.sing 4 -- 13 14
q "$HOME/a5/engine/iso_d5_p2_v6.jsonl" 1316 iso_p2/input.sing 5 -- 16 17
q "$HOME/a5/engine/e8nm_d3_p2_raw_v6.jsonl" 225 e8nm_p2/input.sing 3 -- 11 12
