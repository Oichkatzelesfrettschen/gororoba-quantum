#!/bin/sh
# Plan the N=21 orbit window-dose sweep on the calibration in force now, check the plan against the reviewed
# design, and with --submit submit that plan at once.
#
# live_run.py fetches each backend's Target and properties in the planning process, and --submit compares the
# fresh plan with the approved record, so a plan made minutes before submission carries the current calibration.
# The 20 us repetition delay is tried first and the 50 us one when no admitted plan comes back at 20 us;
# --delay 5e-05 plans at 50 us only, the envelope's single retry after a 20 us job that ends in error 1305 with no
# circuit execution time. scripts/n21_dose_decisions.py --preflight requires the approved envelope of
# docs/design/n21-orbit-window-dose-envelope.md and a plan made at the checked-out commit from a clean tree.
#
# Usage: sh scripts/n21_dose_run.sh [--delay 2e-05|5e-05] [--submit]   (from the repository root)
set -eu

PYTHON=${PYTHON:-python3}
export PYTHON
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_IBM_ACCOUNT=backup-ibm-quantum-platform

usage() {
	echo "usage: sh scripts/n21_dose_run.sh [--delay 2e-05|5e-05] [--submit]" >&2
	exit 2
}
submit=0
delays="2e-05 5e-05"
while [ $# -gt 0 ]; do
	case $1 in
	--submit) submit=1 ;;
	--delay)
		[ $# -ge 2 ] || usage
		case $2 in 2e-05 | 5e-05) delays=$2 ;; *) usage ;; esac
		shift
		;;
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
draw=docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json
head=$(git rev-parse HEAD)

plan_args() {
	printf '%s\n' --family n21-orbit-rca --shot-allocation uniform --objective minimum_charge --optimize \
		--backends ibm_fez,ibm_kingston,ibm_marrakesh --shots 8192 --seeds 8 --max-pending 200 \
		--min-remaining-seconds 60.0 --max-execution-seconds 30 --rep-delay "$1" --no-isolated-reference \
		--cross-group-buffer --shot-tiers 8192 --replica-tiers 24 --replica-floor 0.45 --optimizer-candidates 6 --model-shots 131072 \
		--precision 0.08 --alpha 0.05 --power 0.8 --simulation-alpha 0.01 --job-overhead-seconds 2.3 \
		--classical-latency-us 20.0 --reserve-seconds 0.0 --max-total-execution-seconds 30.0 --init-herald \
		--window-doses-dt 0,1752,3500,5252,7000,10500,14000 --seed-transpiler "qrng:$draw#0" --seed-simulator "qrng:$draw#1" \
		--out ../results/live
}

record=
delay=
for candidate in $delays; do
	log=$logs/n21-dose-plan-$candidate.log
	# shellcheck disable=SC2046
	if (cd "$root/gororoba_quantum" && "$PYTHON" live_run.py $(plan_args "$candidate")) >"$log" 2>&1; then
		path=$(sed -n 's|^unapproved written case: \.\./\(results/live/[^/]*\)/UNAPPROVED_CASE\.md$|\1|p' "$log" | tail -n 1)
		if [ -n "$path" ] && "$PYTHON" scripts/n21_dose_decisions.py --preflight "$path" --head "$head" \
			>"$logs/n21-dose-preflight.json"; then
			record=$path
			delay=$candidate
			break
		fi
	fi
	echo "no admitted plan at rep delay $candidate s (log $log)" >&2
done
[ -n "$record" ] || {
	echo "no admitted plan at rep delay $delays s" >&2
	exit 1
}
digest=$(sha256sum "$record/record.json" | cut -d ' ' -f 1)
echo "planned $record at rep delay $delay s: $(cat "$logs/n21-dose-preflight.json")"
if [ "$submit" -eq 0 ]; then
	echo "plan only; rerun with --submit to submit it"
	exit 0
fi
status=0
# shellcheck disable=SC2046
(cd "$root/gororoba_quantum" && "$PYTHON" live_run.py $(plan_args "$delay") \
	--approved-record "../$record" --approved-record-sha256 "$digest" --submit) \
	>"$logs/n21-dose-submit.log" 2>&1 || status=$?
tail -n 5 "$logs/n21-dose-submit.log"
# live_run.py writes the submitted run to its own directory; the dry run it compared against stays unsubmitted.
run=$(sed -n 's|^audit record: \.\./\(results/live/[^/]*\)$|\1|p' "$logs/n21-dose-submit.log" | tail -n 1)
if [ "$status" -ne 0 ] || [ -z "$run" ]; then
	echo "submission of $record failed with status $status (log $logs/n21-dose-submit.log)" >&2
	exit 1
fi
echo "submitted $run against $record; collect with: (cd gororoba_quantum && \"\$PYTHON\" live_run.py --collect ../$run)"
