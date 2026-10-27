#!/bin/sh
# Plan the N=21 orbit detuning-sign test on the calibration in force now, check the plan against the approved
# envelope (docs/design/n21-orbit-detuning-sign-envelope.md), and with --submit submit that plan at once.
#
# live_run.py fetches each backend's Target and properties in the planning process. --submit first checks the
# approved isa.qpy against the fresh calibration values and writes an approval_required record within seconds
# when any value changed; when every value matches, it reuses the dry run's predictions and its single routed
# design (live_run.reuse_approved_predictions, approved_family_design) instead of simulating again. A refusal
# that sent nothing leaves the approval unconsumed (approval-consumed.json absent), so the runner plans again on
# the new calibration, up to ATTEMPTS times.
#
# The plan tries the 20 us repetition delay first and falls back to 50 us when no plan at 20 us is admitted.
# --preflight requires the envelope's bounds and a plan made at the checked-out commit; the runner refuses to
# plan while any file under the directories that build, seed, check or submit the plan differs from that commit.
#
# Usage: sh scripts/n21_detuning_sign_run.sh [--submit]   (from the repository root)
set -eu

PYTHON=${PYTHON:-python3}
export PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform
ATTEMPTS=4

usage() {
	echo "usage: sh scripts/n21_detuning_sign_run.sh [--submit]" >&2
	exit 2
}
submit=0
delays="2e-05 5e-05"
while [ $# -gt 0 ]; do
	case $1 in
	--submit) submit=1 ;;
	*) usage ;;
	esac
	shift
done

root=$(pwd)
[ -f "$root/gororoba_quantum/live_run.py" ] || {
	echo "run from the repository root" >&2
	exit 2
}
logs=$root/docs/local
mkdir -p "$logs"
draw=docs/evidence/outshift_qrng/draw-2026-10-27T154654Z.json
head=$(git rev-parse HEAD)
# Every tracked input that builds, seeds, checks or submits the plan; re-read before each plan, preflight and submit.
clean() {
	[ "$(git rev-parse HEAD)" = "$head" ] || {
		echo "HEAD moved from $head" >&2
		exit 1
	}
	dirty=$(git status --porcelain -- gororoba_quantum scripts ci docs/design docs/evidence/outshift_qrng \
		docs/evidence/qrng_seeds requirements.txt)
	if [ -n "$dirty" ]; then
		echo "the tree differs from $head where the plan is built, seeded, checked or submitted:" >&2
		echo "$dirty" >&2
		exit 1
	fi
}
clean
plan_args() {
	printf '%s\n' --family n21-orbit-rca --shot-allocation uniform --objective minimum_charge --optimize \
		--backends ibm_fez,ibm_kingston,ibm_marrakesh --shots 4096 --seeds 8 --max-pending 200 \
		--min-remaining-seconds 60.0 --max-execution-seconds 40 --rep-delay "$1" --no-isolated-reference \
		--cross-group-buffer --shot-tiers 4096 --replica-tiers 24 --replica-floor 0.45 --optimizer-candidates 1 \
		--model-shots 32768 --precision 0.09 --alpha 0.05 --power 0.8 --simulation-alpha 0.01 \
		--job-overhead-seconds 2.3 --classical-latency-us 20.0 --reserve-seconds 0.0 \
		--max-total-execution-seconds 40.0 --init-herald \
		--window-doses-dt 0,1752,3504,5256,7008,8760,10512,12264,14016 --detuning-sign \
		--seed-transpiler "qrng:$draw#0" --seed-simulator "qrng:$draw#1" --out ../results/live
}

# plan TAG: sets record and delay to the first admitted, preflighted plan over $delays, or returns 1.
plan() {
	record=
	delay=
	for candidate in $delays; do
		clean
		log=$logs/n21-detuning-sign-plan-$1-$candidate.log
		# shellcheck disable=SC2046
		if (cd "$root/gororoba_quantum" && "$PYTHON" live_run.py $(plan_args "$candidate")) >"$log" 2>&1; then
			path=$(sed -n 's|^unapproved written case: \.\./\(results/live/[^/]*\)/UNAPPROVED_CASE\.md$|\1|p' "$log" |
				tail -n 1)
			clean
			if [ -n "$path" ] && "$PYTHON" scripts/n21_detuning_sign.py --preflight "$path" --head "$head" \
				>"$logs/n21-detuning-sign-preflight.json"; then
				record=$path
				delay=$candidate
				return 0
			fi
		fi
		echo "no admitted plan at rep delay $candidate s (log $log)" >&2
	done
	return 1
}

state_of() {
	"$PYTHON" -c 'import json, sys; print(json.load(open(sys.argv[1]))["state"])' "$1/record.json"
}

job_ids() {
	"$PYTHON" -c 'import json, sys
jobs = json.load(open(sys.argv[1])).get("submission", {}).get("jobs", [])
print(" ".join(job["job_id"] for job in jobs if job.get("job_id")))' "$1/record.json"
}

attempt=1
while :; do
	started=$(date +%s)
	plan "$attempt" || {
		echo "no admitted plan at rep delay $delays s" >&2
		exit 1
	}
	digest=$(sha256sum "$record/record.json" | cut -d ' ' -f 1)
	echo "attempt $attempt: planned $record at rep delay $delay s in $(($(date +%s) - started)) s:" \
		"$(cat "$logs/n21-detuning-sign-preflight.json")"
	if [ "$submit" -eq 0 ]; then
		echo "plan only; rerun with --submit to submit it"
		exit 0
	fi
	clean
	submit_log=$logs/n21-detuning-sign-submit-$attempt.log
	status=0
	# shellcheck disable=SC2046
	(cd "$root/gororoba_quantum" && "$PYTHON" live_run.py $(plan_args "$delay") \
		--approved-record "../$record" --approved-record-sha256 "$digest" --submit) \
		>"$submit_log" 2>&1 || status=$?
	tail -n 5 "$submit_log"
	# live_run.py writes the submission to its own directory; the dry run it compared against stays unsubmitted.
	run=$(sed -n 's|^audit record: \.\./\(results/live/[^/]*\)$|\1|p' "$submit_log" | tail -n 1)
	if [ -e "$record/approval-consumed.json" ]; then
		ids=
		[ -z "$run" ] || ids=$(job_ids "$run")
		if [ -n "$ids" ]; then
			echo "submitted $run (jobs $ids) against $record (exit $status) in $(($(date +%s) - started)) s;" \
				"collect with: (cd gororoba_quantum && \"\$PYTHON\" live_run.py --collect ../$run)"
			exit "$status"
		fi
		echo "outcome unknown: $record's approval is consumed and ${run:-no run directory} records no job id" \
			"(log $submit_log)" >&2
		exit 1
	fi
	if [ -n "$run" ] && [ "$(state_of "$run")" = approval_required ] && [ "$attempt" -lt "$ATTEMPTS" ]; then
		echo "attempt $attempt: $run refused the plan with nothing sent; planning again" >&2
		attempt=$((attempt + 1))
		continue
	fi
	echo "submission of $record failed with status $status and nothing sent (log $submit_log)" >&2
	exit 1
done
