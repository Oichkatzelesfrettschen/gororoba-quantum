#!/bin/sh
# Run the replicated Tuna-17 matched-response series as one approved series.
#
# Usage: qi_replicated_series_run.sh --approval QUOTE --submit-replicated-q11 --deadline SECONDS [--stamp STAMP]
#            [--runs-dir DIR] [--state-dir DIR] [--proposal DIR]
#        qi_replicated_series_run.sh --dry-run --runs-dir DIR --state-dir DIR [--deadline SECONDS] [--stamp STAMP]
#
# The script does nothing without --approval QUOTE (the owner's approval, quoted, recorded in each
# submission.json) and the exact arming argument --submit-replicated-q11. --dry-run walks the same control flow
# against scripts/qi_replicated_series_fake.py, takes neither argument, needs an explicit --runs-dir other than the
# retained runs directory, and never reaches a provider.
#
# Sequence. Pre-flight (lease command named, backend status read, free disk) -> rep-00 (the profile unit: copy,
# submit under the account's submit lease, collect, binding check; the series stops with a marker on any failure)
# -> rep-01 .. rep-11, each with its binding check -> the stage-1 gate (qi_replicated_response_analysis.py
# --stage1) -> when the verdict is continue, the replicates up to the rule's N -> --final. Both stages are one
# series: a gap of hours between them would break the exchangeability the t test assumes. A submit refused for the
# hardware pause is retried after the reported remainder plus one second, at most ten refusals per replicate, so the
# gap between batches is the pause ladder step (120 s) and nothing longer.
#
# Restart. A second call with the same --stamp resumes: a run directory that holds results.json is checked again and
# left alone; one that holds submission.json and no results.json is collected without a submit; one that holds
# submission-state.json and no submission.json stops the series (only qi_platform.py reconcile can tell whether the
# batch reached the service); one with neither is submitted. A run directory of the series under another stamp stops
# the series; QI_REPEAT_SERIES set to the series name arms a repeat. A run directory whose copy differs from the
# proposal's stops the series before any submit.
#
# State directory: series.log, marker (the terminal marker: done, or failed REASON), RESUME.md, stage1.json and
# final.json.
#
# Environment: QI_PYTHON (the Quantum Inspire interpreter, real runs), PYTHON (analysis; default python3),
# QI_SUBMIT_LEASE_COMMAND (the lease command qi_submit_lease.py appends take HOLDER or release NONCE to),
# QI_COLLECT_TIMEOUT (seconds one collection waits, default 3600), QI_PAUSE_SLEEP=0 (print the wait, no sleep).
set -eu

series_name=tuna17-replicated-q11
root=$(cd "$(dirname "$0")/.." && pwd)
approval=
armed=
dry=
deadline=
stamp=
runs=
state=
proposal=$root/results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11

usage() {
	echo "usage: $0 --approval QUOTE --submit-replicated-q11 --deadline SECONDS [--stamp STAMP] [--runs-dir DIR] [--state-dir DIR]" >&2
	echo "       $0 --dry-run --runs-dir DIR --state-dir DIR [--deadline SECONDS] [--stamp STAMP]" >&2
	exit 2
}

while [ "$#" -gt 0 ]; do
	case $1 in
	--approval)
		[ "$#" -ge 2 ] || usage
		approval=$2
		shift 2
		;;
	--submit-replicated-q11)
		armed=1
		shift
		;;
	--dry-run)
		dry=1
		shift
		;;
	--deadline)
		[ "$#" -ge 2 ] || usage
		deadline=$2
		shift 2
		;;
	--stamp)
		[ "$#" -ge 2 ] || usage
		stamp=$2
		shift 2
		;;
	--runs-dir)
		[ "$#" -ge 2 ] || usage
		runs=${2%/}
		shift 2
		;;
	--state-dir)
		[ "$#" -ge 2 ] || usage
		state=${2%/}
		shift 2
		;;
	--proposal)
		[ "$#" -ge 2 ] || usage
		proposal=${2%/}
		shift 2
		;;
	*) usage ;;
	esac
done

retained=$root/results/quantum_inspire/runs
if [ -n "$dry" ]; then
	{ [ -z "$armed" ] && [ -z "$approval" ]; } || {
		echo "--dry-run takes neither --approval nor --submit-replicated-q11" >&2
		exit 2
	}
	{ [ -n "$runs" ] && [ -n "$state" ]; } || usage
	[ "$runs" != "$retained" ] || {
		echo "--dry-run refuses the retained runs directory" >&2
		exit 2
	}
	[ -n "$deadline" ] || deadline=3600
	approval="dry-run"
else
	{ [ "$armed" = 1 ] && [ -n "$approval" ]; } || usage
	[ -n "$deadline" ] || usage
	[ -n "$runs" ] || runs=$retained
fi
case $deadline in
'' | *[!0-9]*)
	echo "--deadline must be a whole number of seconds" >&2
	exit 2
	;;
esac
case $stamp in
*[!A-Za-z0-9-]*)
	echo "--stamp holds letters, digits and hyphens" >&2
	exit 2
	;;
esac
[ -n "$stamp" ] || stamp=$(date -u +%Y-%m-%dT%H%M%SZ)
[ -n "$state" ] || state=$root/docs/local/replicated-series/$stamp
collect_timeout=${QI_COLLECT_TIMEOUT:-3600}
case $collect_timeout in
'' | *[!0-9]*)
	echo "QI_COLLECT_TIMEOUT must be a whole number of seconds" >&2
	exit 2
	;;
esac

py=${PYTHON:-python3}
analysis=$root/scripts/qi_replicated_response_analysis.py
if [ -n "$dry" ]; then
	qipy=$py
	submit_script=$root/scripts/qi_replicated_series_fake.py
	collect_script=$submit_script
else
	: "${QI_PYTHON:?QI_PYTHON must name the Quantum Inspire interpreter}"
	qipy=$QI_PYTHON
	submit_script=$root/scripts/qi_platform_leased.py
	collect_script=$root/scripts/qi_platform.py
fi
GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GLIBC_TUNABLES
QI_HARDWARE_PAUSE_SECONDS=120
export QI_HARDWARE_PAUSE_SECONDS

mkdir -p "$runs" "$state"
rm -f "$state/marker"
start=$(date +%s)
reason=
max_refusals=10

log() {
	printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$state/series.log" >&2
}

write_resume() {
	collected=0
	for d in "$runs"/"$stamp-$series_name"-rep-*; do
		[ -e "$d/results.json" ] && collected=$((collected + 1))
	done
	cat >"$state/RESUME.md" <<EOF
# Replicated Tuna-17 series RESUME

Stamp: $stamp. Replicates collected when this note was written: $collected. Terminal marker: $state/marker.

Resume (same stamp, same approval quote):
$0 --stamp $stamp --runs-dir $runs --state-dir $state --deadline SECONDS [--approval QUOTE --submit-replicated-q11 | --dry-run]

State claims, each with its check:
- Run directories of this stamp: ls -d $runs/$stamp-$series_name-rep-*
- Collected replicates (results.json present): ls $runs/$stamp-$series_name-rep-*/results.json
- A submit checkpoint without a receipt stops the series: for d in $runs/$stamp-$series_name-rep-*; do [ -e \$d/submission-state.json ] && [ ! -e \$d/submission.json ] && echo \$d; done  (then qi_platform.py reconcile on it)
- Stage-1 verdict and N: cat $state/stage1.json
- Final analysis: cat $state/final.json
- Series log: tail $state/series.log

Failure modes: a refused pause (retried up to ten times), a failed or timed-out collection (rerun collects without a
second submit), a binding or readout failure (series stops; the run directory stays as evidence), the deadline.
Done means: marker reads done and final.json exists.
EOF
}

finish() {
	rc=$?
	trap - EXIT
	if [ "$rc" -eq 0 ]; then
		printf 'done\n' >"$state/marker"
	else
		printf 'failed %s\n' "${reason:-exit $rc}" >"$state/marker"
	fi
	write_resume
	exit "$rc"
}
trap finish EXIT

fail() {
	reason=$*
	log "FAILED $reason"
	exit 1
}

remaining() {
	echo $((deadline - ($(date +%s) - start)))
}

# --- pre-flight ---------------------------------------------------------------------------------------------
log "series $series_name stamp $stamp (dry-run: ${dry:-no})"
backend_id=$("$py" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["backend_type_id"])' "$proposal/rep-00/cases.json")
if [ -n "$dry" ]; then
	log "pre-flight: lease, backend status and disk are not read in a dry run"
else
	[ -n "${QI_SUBMIT_LEASE_COMMAND:-}" ] || fail "QI_SUBMIT_LEASE_COMMAND names no submit lease command"
	log "pre-flight: submit lease through qi_platform_leased.py (command set, holder ${QI_SUBMIT_LEASE_HOLDER:-host name})"
	status=$("$qipy" -c 'import sys
sys.path.insert(0, sys.argv[1])
import qi_platform
rows = [r for r in qi_platform.Client().pages("/backend_types/") if r["id"] == int(sys.argv[2])]
print(rows[0]["status"] if rows else "missing")' "$root/scripts" "$backend_id") || fail "the backend status read failed"
	log "pre-flight: backend type $backend_id status $status"
	free_kib=$(df -Pk "$runs" | awk 'NR == 2 { print $4 }')
	[ "$free_kib" -ge 2097152 ] || fail "free disk under 2 GiB on the runs directory"
	log "pre-flight: free disk $free_kib KiB on the runs directory"
fi

# --- one series per stamp -----------------------------------------------------------------------------------
for other in "$runs"/*-"$series_name"-rep-*; do
	[ -e "$other" ] || continue
	held=$(basename "$other")
	held=${held%-"$series_name"-rep-*}
	if [ "$held" != "$stamp" ] && [ "${QI_REPEAT_SERIES:-}" != "$series_name" ]; then
		fail "$other holds this series under stamp $held; resume with --stamp $held, or arm a repeat with QI_REPEAT_SERIES=$series_name"
	fi
done
for src in "$proposal"/rep-*; do
	[ -d "$src" ] || continue
	run=$runs/$stamp-$series_name-$(basename "$src")
	[ -e "$run" ] || continue
	for file in "$src"/*; do
		[ -f "$file" ] || continue
		cmp -s "$file" "$run/$(basename "$file")" || fail "$run/$(basename "$file") differs from $file: the series changed after this copy; run it under a new stamp"
	done
done
write_resume

run_of() {
	printf '%s/%s-%s-rep-%02d' "$runs" "$stamp" "$series_name" "$1"
}

check_binding() {
	"$py" "$analysis" --binding "$1" --proposal "$proposal" >"$state/binding-$(basename "$1").json" || fail "binding check of $(basename "$1") failed"
	log "$(basename "$1"): binding and readout checks passed"
}

do_replicate() {
	i=$1
	run=$(run_of "$i")
	rep=$(printf 'rep-%02d' "$i")
	if [ "$(remaining)" -le 0 ]; then
		fail "the deadline of $deadline s passed before $rep"
	fi
	if [ -e "$run/results.json" ]; then
		log "$rep: collected; skipped"
		check_binding "$run"
		return 0
	fi
	if [ -e "$run/submission-state.json" ] && [ ! -e "$run/submission.json" ]; then
		fail "$rep: $run holds a submit checkpoint and no receipt; run qi_platform.py reconcile on it"
	fi
	[ -e "$run" ] || cp -R "$proposal/$rep" "$run"
	refused=0
	while [ ! -e "$run/submission.json" ]; do
		if out=$("$qipy" "$submit_script" submit "$run" --backend-type-id "$backend_id" --approval "$approval" 2>&1); then
			log "$rep: submitted: $out"
			break
		fi
		left=$(printf '%s\n' "$out" | sed -n 's/.*wait \([0-9][0-9]*\) more seconds.*/\1/p' | head -n 1)
		refused=$((refused + 1))
		if [ -z "$left" ] || [ "$refused" -ge "$max_refusals" ]; then
			printf '%s\n' "$out" >&2
			fail "$rep: stopped after $refused refusal(s)"
		fi
		[ "$(remaining)" -gt $((left + 1)) ] || fail "$rep: the deadline leaves no room for the pause"
		log "$rep: sleep $((left + 1))"
		if [ "${QI_PAUSE_SLEEP:-}" != "0" ]; then
			sleep $((left + 1))
		fi
	done
	timeout=$(remaining)
	[ "$timeout" -le "$collect_timeout" ] || timeout=$collect_timeout
	[ "$timeout" -gt 0 ] || fail "$rep: the deadline passed before collection"
	"$qipy" "$collect_script" collect "$run" --poll 15 --timeout "$timeout" >>"$state/series.log" 2>&1 || fail "$rep: collection failed; a restart collects without a second submit"
	log "$rep: collected"
	check_binding "$run"
}

analyze_series() {
	# analyze_series MODE COUNT [OPTION...]: the analysis over the run directories of rep-00 .. rep-(COUNT-1)
	mode=$1
	count=$2
	shift 2
	k=$count
	while [ "$k" -gt 0 ]; do
		k=$((k - 1))
		set -- "$(run_of "$k")" "$@"
	done
	"$py" "$analysis" "$mode" "$@"
}

# --- stage 1 (rep-00 is the profile unit) --------------------------------------------------------------------
i=0
while [ "$i" -lt 12 ]; do
	do_replicate "$i"
	i=$((i + 1))
done
out=$(analyze_series --stage1 12 --proposal "$proposal" --out "$state/stage1.json") || fail "the stage-1 analysis refused"
verdict=$(printf '%s\n' "$out" | sed -n 's/^verdict: //p')
total=$(printf '%s\n' "$out" | sed -n 's/^N: //p')
log "stage 1: verdict $verdict, N $total"
case $verdict in
continue)
	case $total in
	'' | *[!0-9]*) fail "the stage-1 gate printed no total" ;;
	esac
	{ [ "$total" -gt 12 ] && [ "$total" -le 60 ]; } || fail "the stage-1 total $total lies outside 13 .. 60"
	;;
final | undecided-at-cap) total=12 ;;
*) fail "the stage-1 gate printed no verdict" ;;
esac

# --- stage 2 ------------------------------------------------------------------------------------------------
i=12
while [ "$i" -lt "$total" ]; do
	do_replicate "$i"
	i=$((i + 1))
done
analyze_series --final "$total" --proposal "$proposal" --stage1-decision "$state/stage1.json" --out "$state/final.json" >"$state/final.out" || fail "the final analysis refused"
log "final: $(tr '\n' ' ' <"$state/final.out")(analysis in $state/final.json)"
