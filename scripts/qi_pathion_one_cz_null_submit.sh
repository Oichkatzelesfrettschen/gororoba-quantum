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
# A second call with the same STAMP resumes the series: a run directory that holds results.json is checked again and
# left as it is, and one that holds submission.json and no results.json is collected without a submit. One that holds
# submission-state.json and no submission.json stops the script: submit writes that checkpoint before its first
# remote write, so only qi_platform.py reconcile can tell whether the batch reached the service. A run directory with
# none of these files saw only refused submits, which write nothing, and is submitted.
#
# A run directory of the same series under another stamp stops the script before any submit, so a lost or changed
# STAMP cannot submit the series a second time. QI_REPEAT_SERIES set to the series directory's name arms a repeat of
# the series under a new stamp, which needs its own approval.
#
# QI_PYTHON names the Quantum Inspire interpreter, QI_PLATFORM the runner (default scripts/qi_platform.py),
# SANITY_COMMAND the per-batch check that takes the run directory last (default: the case generator's --sanity under
# PYTHON), QI_COLLECT_TIMEOUT the seconds one collection waits for its batch (default 3600; a batch still queued at
# the timeout stops the script and stays queued for the resuming call), and QI_PAUSE_SLEEP=0 prints the wait without
# sleeping (tests).
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
collect_timeout=${QI_COLLECT_TIMEOUT:-3600}
case $collect_timeout in
'' | *[!0-9]*)
	echo "QI_COLLECT_TIMEOUT must be a whole number of seconds" >&2
	exit 2
	;;
esac
name=$(basename "$series")

mkdir -p "$runs"
for other in "$runs"/*-"$name"-batch-*; do
	[ -e "$other" ] || continue
	held=$(basename "$other")
	held=${held%-"$name"-batch-*}
	if [ "$held" != "$stamp" ] && [ "${QI_REPEAT_SERIES:-}" != "$name" ]; then
		echo "$other holds this series under stamp $held; resume with STAMP=$held, or arm a repeat with QI_REPEAT_SERIES=$name" >&2
		exit 1
	fi
done
for batch_dir in "$series"/batch-*; do
	batch=$(basename "$batch_dir")
	run="$runs/$stamp-$name-$batch"
	if [ -e "$run/results.json" ]; then
		# shellcheck disable=SC2086
		$sanity "$run"
		continue
	fi
	if [ -e "$run/submission-state.json" ] && [ ! -e "$run/submission.json" ]; then
		echo "$run holds a submit checkpoint and no receipt; run qi_platform.py reconcile on it" >&2
		exit 1
	fi
	[ -e "$run" ] || cp -R "$batch_dir" "$run"
	refused=0
	while [ ! -e "$run/submission.json" ]; do
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
	"$QI_PYTHON" "$platform" collect "$run" --poll 15 --timeout "$collect_timeout"
	# shellcheck disable=SC2086
	$sanity "$run"
done
