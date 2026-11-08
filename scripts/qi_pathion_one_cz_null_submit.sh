#!/bin/sh
# Submit the batches of one case series in order, each after the previous collection and sanity check.
#
# Usage: qi_pathion_one_cz_null_submit.sh BACKEND_TYPE_ID SERIES_DIR RUNS_DIR STAMP APPROVAL
#
# qi_platform.py submit refuses while the account's last hardware job finished less than the pause ago and reports
# "wait N more seconds"; this script sleeps that remainder plus one second and retries, at most ten refusals per batch,
# and stops at the first refusal that names no remainder, the first failed collection or sanity check, and the tenth
# refusal. One batch is submitted at a time and collected before the next, so at most one batch of the account is
# queued. A refused submit writes nothing on the service, so a retry reuses the copied run directory.
#
# QI_PYTHON names the Quantum Inspire interpreter, QI_PLATFORM the runner (default scripts/qi_platform.py),
# SANITY_COMMAND the per-batch check that takes the run directory last (default: the case generator's --sanity under
# PYTHON), and QI_PAUSE_SLEEP=0 prints the wait without sleeping (tests).
set -eu

[ "$#" -eq 5 ] || {
	echo "usage: $0 BACKEND_TYPE_ID SERIES_DIR RUNS_DIR STAMP APPROVAL" >&2
	exit 2
}
backend=$1
series=${2%/}
runs=$3
stamp=$4
approval=$5
: "${QI_PYTHON:?QI_PYTHON must name the Quantum Inspire interpreter}"
platform=${QI_PLATFORM:-scripts/qi_platform.py}
sanity=${SANITY_COMMAND:-"${PYTHON:-python3} scripts/qi_pathion_one_cz_null_cases.py --sanity"}
max_refusals=10
name=$(basename "$series")

mkdir -p "$runs"
for batch_dir in "$series"/batch-*; do
	batch=$(basename "$batch_dir")
	run="$runs/$stamp-$name-$batch"
	if [ -e "$run" ]; then
		echo "$run exists; a submitted batch is never resubmitted" >&2
		exit 1
	fi
	cp -R "$batch_dir" "$run"
	refused=0
	while :; do
		if out=$("$QI_PYTHON" "$platform" submit "$run" --backend-type-id "$backend" --approval "$approval" 2>&1); then
			break
		fi
		left=$(printf '%s\n' "$out" | sed -n 's/.*wait \([0-9][0-9]*\) more seconds.*/\1/p' | head -n 1)
		refused=$((refused + 1))
		if [ -z "$left" ] || [ "$refused" -ge "$max_refusals" ]; then
			printf '%s\n' "$out" >&2
			echo "$batch: stopped after $refused refusal(s)" >&2
			exit 1
		fi
		echo "sleep $((left + 1))" >&2
		if [ "${QI_PAUSE_SLEEP:-}" != "0" ]; then
			sleep $((left + 1))
		fi
	done
	"$QI_PYTHON" "$platform" collect "$run" --poll 15 --timeout 3600
	# shellcheck disable=SC2086
	$sanity "$run"
done
