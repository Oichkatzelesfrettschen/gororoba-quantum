#!/bin/sh
# Snapshot the provider allotments, then print the alert lines; notify-send announces them.
# PYTHON names the interpreter that holds qiskit-ibm-runtime; the script lives beside the repository's scripts/.
set -eu
here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo=$(CDPATH='' cd -- "$here/../../.." && pwd)
PYTHON=${PYTHON:-python3}
export PYTHON
GLIBC_TUNABLES=${GLIBC_TUNABLES:-glibc.rtld.optional_static_tls=4096}
export GLIBC_TUNABLES

"$PYTHON" "$repo/scripts/provider_credits.py" snapshot
status=0
out=$("$PYTHON" "$repo/scripts/provider_credits.py" check-alerts) || status=$?
if [ -n "$out" ]; then
	printf '%s\n' "$out"
fi
if [ "$status" -ne 0 ] && command -v notify-send >/dev/null 2>&1; then
	notify-send -u normal "Quantum credits" "$out" || true
fi
exit "$status"
