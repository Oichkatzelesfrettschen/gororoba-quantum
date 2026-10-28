#!/bin/sh
# Wait for a backend to publish a new calibration: run scripts/calibration_watch.py every INTERVAL seconds, each
# poll a fresh process bounded by timeout, until it reports a change. Chain the binding run after it, so the plan
# starts within one interval of the publication:
#
#   sh scripts/wait_calibration.sh --deadline 86400 -- ibm_kingston --baseline B.json --qubits 0,1,5-9 \
#     && sh scripts/approved_run.sh --check CMD -- FLAGS
#
# The first poll writes the baseline when B.json is absent, so the wait measures change from its own start; a
# baseline written earlier measures change from that read instead.
#
# Usage: sh scripts/wait_calibration.sh [--interval S] [--deadline S] [--log FILE] -- WATCH_ARGS...
#        (from the repository root). Exit 0 changed, 2 usage or deadline, 3 five consecutive failed reads.
set -eu

PYTHON=${PYTHON:-python3}
export PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096

usage() {
	echo "usage: sh scripts/wait_calibration.sh [--interval S] [--deadline S] [--log FILE] -- WATCH_ARGS..." >&2
	exit 2
}
interval=60
deadline=86400
log=/dev/null
while [ $# -gt 0 ]; do
	case $1 in
	--interval) [ $# -ge 2 ] || usage; interval=$2; shift ;;
	--deadline) [ $# -ge 2 ] || usage; deadline=$2; shift ;;
	--log) [ $# -ge 2 ] || usage; log=$2; shift ;;
	--) shift; break ;;
	*) usage ;;
	esac
	shift
done
[ $# -gt 0 ] || usage
end=$(($(date +%s) + deadline))
fails=0
child=
out=$(mktemp)
cleanup() {
	if [ -n "$child" ]; then kill "$child" 2>/dev/null || true; fi
	rm -f "$out"
}
trap cleanup EXIT
trap 'exit 130' INT TERM HUP

while :; do
	status=0
	timeout -k 10 120 "$PYTHON" scripts/calibration_watch.py "$@" >"$out" 2>&1 &
	child=$!
	wait "$child" || status=$?
	child=
	echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $(tail -n 1 "$out")" >>"$log"
	case $status in
	0) tail -n 1 "$out"; exit 0 ;;
	1) fails=0 ;;
	2) cat "$out" >&2; exit 2 ;;
	*) fails=$((fails + 1)); [ "$fails" -lt 5 ] || { tail -n 1 "$out" >&2; exit 3; } ;;
	esac
	[ "$(date +%s)" -lt "$end" ] || { echo "deadline: $(tail -n 1 "$out")" >&2; exit 2; }
	sleep "$interval" &
	child=$!
	wait "$child"
	child=
done
