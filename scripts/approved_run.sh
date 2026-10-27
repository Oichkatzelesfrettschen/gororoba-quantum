#!/bin/sh
# Binding dry run and --submit of an approved case in one invocation: plan on the calibration in force now, run
# the case's mechanical checks on that plan, and submit it at once with the identical flags.
#
# --submit compares the fresh plan with the approved record by calibration value
# (docs/notes/ibm_quantum/qpu-submission.md): a changed value touching the packed circuits writes an
# approval_required record and sends nothing, so every second between the plan and the submit is exposure to a
# recalibration. A refusal leaves the approval unconsumed (approval-consumed.json absent), and the runner plans
# again, up to ATTEMPTS times. A consumed approval ends the run: it succeeds only when the submit exits zero and
# its record reads `submission.complete`, and a failed or partial submission exits 4 without a retry, because the
# approval is spent.
#
# CHECK runs from gororoba_quantum/ with RUN set to the dry run's directory; a nonzero exit stops the run before
# the submit. LIVE_RUN_ARGS are the case's live_run.py flags without --submit; GOROROBA_IBM_ACCOUNT selects the
# account as for live_run.py.
#
# Usage: sh scripts/approved_run.sh [--attempts N] [--check CMD] [--log DIR] -- LIVE_RUN_ARGS...
#        (from the repository root). Exit 0 submitted, 1 dry run or check failed, 2 usage, 3 every attempt
#        refused, 4 approval consumed with a failed or incomplete submission.
set -eu

PYTHON=${PYTHON:-python3}
export PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096

usage() {
	echo "usage: sh scripts/approved_run.sh [--attempts N] [--check CMD] [--log DIR] -- LIVE_RUN_ARGS..." >&2
	exit 2
}
attempts=3
check=
log=
while [ $# -gt 0 ]; do
	case $1 in
	--attempts) [ $# -ge 2 ] || usage; attempts=$2; shift ;;
	--check) [ $# -ge 2 ] || usage; check=$2; shift ;;
	--log) [ $# -ge 2 ] || usage; log=$2; shift ;;
	--) shift; break ;;
	*) usage ;;
	esac
	shift
done
[ $# -gt 0 ] || usage
for arg in "$@"; do
	case $arg in --submit | --approved-record | --approved-record-sha256) usage ;; esac
done
root=$(pwd)
[ -n "$log" ] || log=$(mktemp -d)
mkdir -p "$log"
log=$(cd "$log" && pwd)
cd "$root/gororoba_quantum"

attempt=1
while [ "$attempt" -le "$attempts" ]; do
	"$PYTHON" live_run.py "$@" > "$log/dry-$attempt.log" 2>&1 || {
		tail -n 3 "$log/dry-$attempt.log"
		echo "approved_run: dry run failed (attempt $attempt)"
		exit 1
	}
	run=$(sed -n 's/^audit record: //p' "$log/dry-$attempt.log" | tail -n 1)
	[ -n "$run" ] && [ -f "$run/record.json" ] || { echo "approved_run: no audit record"; exit 1; }
	if [ -n "$check" ]; then
		RUN=$run sh -c "$check" > "$log/check-$attempt.log" 2>&1 || {
			tail -n 3 "$log/check-$attempt.log"
			echo "approved_run: check failed on $run"
			exit 1
		}
	fi
	sha=$(sha256sum "$run/record.json" | cut -c1-64)
	status=0
	"$PYTHON" live_run.py "$@" --submit --approved-record "$run" --approved-record-sha256 "$sha" \
		> "$log/submit-$attempt.log" 2>&1 || status=$?
	if [ -f "$run/approval-consumed.json" ]; then
		submitted=$(sed -n 's/^audit record: //p' "$log/submit-$attempt.log" | tail -n 1)
		if [ "$status" -eq 0 ] && [ -n "$submitted" ] && "$PYTHON" -c \
			'import json, sys; sys.exit(json.load(open(sys.argv[1])).get("submission", {}).get("complete") is not True)' \
			"$submitted/record.json" 2>/dev/null; then
			echo "approved_run: submitted dry_run=$run sha256=$sha run=$submitted"
			exit 0
		fi
		tail -n 3 "$log/submit-$attempt.log"
		echo "approved_run: approval consumed, submission failed or incomplete (exit $status) run=${submitted:-none}"
		exit 4
	fi
	echo "approved_run: attempt $attempt sent nothing: $(tail -n 1 "$log/submit-$attempt.log")"
	attempt=$((attempt + 1))
done
echo "approved_run: no submission after $attempts attempts; logs in $log"
exit 3
