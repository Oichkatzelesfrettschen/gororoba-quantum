#!/bin/sh
# Replay of the arc certificate of the opposite-sign X fibers at one prime.
# Usage: sh replay.sh PRIME [--root ROOT] [--header-dir DIR]
# The prime and the root of -1 come from the first two lines of the headers xp-nm.sing and xm-np.sing under
# working/build/inputs/pPRIME-r*/. Every Singular and Python process runs under the 8 GiB address-space cap set below,
# and a Singular step that exits nonzero or exceeds its timeout stops the replay. The Singular steps and the
# certificate loops use GOROROBA_WORKERS processes (default 3).
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON
GLIBC_TUNABLES=${GLIBC_TUNABLES:-glibc.rtld.optional_static_tls=4096}
export GLIBC_TUNABLES
GOROROBA_WORKERS=${GOROROBA_WORKERS:-3}
export GOROROBA_WORKERS
ulimit -v 8388608
here=$(cd "$(dirname "$0")" && pwd)
if [ "$#" -lt 1 ]; then
  echo "usage: sh replay.sh PRIME [--root ROOT] [--header-dir DIR]" >&2
  exit 2
fi
prime=$1
shift
exec "$PYTHON" "$here/xarc_run.py" --prime "$prime" "$@"
