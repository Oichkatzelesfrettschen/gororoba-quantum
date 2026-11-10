#!/bin/sh
# Watch one pushed Kaggle kernel version and commit what
# scripts/kaggle_run.py collect returns, for .github/workflows/kaggle-collect.yml.
#
#   kaggle_collect.sh watch BUDGET_SECONDS   poll until the version ends, the
#                                            pull time passes or BUDGET runs out
#   kaggle_collect.sh collect                collect, verify, commit, notify
#
# Environment: RUN_DIR (a results/kaggle run directory whose submission.json
# names the version), RESULT_PATH (the entry's output file, copied to the same
# path in the repository), PULL_AFTER and HARD_AFTER (seconds after the push's
# pushed_utc), POLL_SECONDS, PYTHON, BRANCH, and GH_TOKEN for the notice.
#
# Kaggle serves a version's output only after its session ends, and a session
# it ends at --timeout or at the 12-hour limit returns /kaggle/working/output
# without kaggle_kernel/kernel_main.py's exit.json, which collect then records
# as a PARTIAL capture. The pull at PULL_AFTER (11 h 52 min) therefore takes
# whatever the version serves before the limit, and collect keeps watching to
# HARD_AFTER for the terminal state and the output that follows it.
set -eu

: "${RUN_DIR:?}" "${RESULT_PATH:?}" "${PULL_AFTER:?}" "${HARD_AFTER:?}" "${POLL_SECONDS:?}" "${PYTHON:?}"

pushed_epoch() {
	"$PYTHON" -c 'import json, sys
from datetime import UTC, datetime
stamp = json.load(open(sys.argv[1]))["pushed_utc"]
print(int(datetime.strptime(stamp, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=UTC).timestamp()))' "$RUN_DIR/submission.json"
}

# One bounded status read; prints live, terminal or unreadable, and the raw line on stderr.
read_state() {
	line=$(timeout 120 "$PYTHON" scripts/kaggle_run.py status "$RUN_DIR" 2>&1 | tail -n 1) || true
	printf '%s\n' "$line" >&2
	case $line in
	*RUNNING* | *QUEUED* | *NEW_SCRIPT*) echo live ;;
	*COMPLETE* | *ERROR* | *CANCEL*) echo terminal ;;
	*) echo unreadable ;;
	esac
}

# poll UNTIL_EPOCH: prints terminal or timeup; fails after five unreadable reads in a row.
poll() {
	until_epoch=$1
	failures=0
	last=
	while :; do
		state=$(read_state 2>"$RUNNER_TEMP/status.txt")
		line=$(cat "$RUNNER_TEMP/status.txt")
		if [ "$state" = unreadable ]; then
			failures=$((failures + 1))
			echo "::warning::unreadable status ($failures of 5): $line" >&2
			if [ "$failures" -ge 5 ]; then
				echo "::error::five status reads in a row failed: $line" >&2
				return 1
			fi
		else
			failures=0
			[ "$line" = "$last" ] || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $line" >&2
			last=$line
		fi
		if [ "$state" = terminal ]; then
			echo terminal
			return 0
		fi
		if [ "$(date +%s)" -ge "$until_epoch" ]; then
			echo timeup
			return 0
		fi
		sleep "$POLL_SECONDS"
	done
}

watch() {
	budget=$1
	pull_epoch=$(($(pushed_epoch) + PULL_AFTER))
	stop=$(($(date +%s) + budget))
	until_epoch=$((stop < pull_epoch ? stop : pull_epoch))
	result=$(poll "$until_epoch")
	if [ "$result" = terminal ]; then
		state=terminal
	elif [ "$(date +%s)" -ge "$pull_epoch" ]; then
		state=pull
	else
		state=waiting
	fi
	echo "state=$state" >>"$GITHUB_OUTPUT"
	echo "watch ended: $state"
}

# The state of the newest receipt: the primary collect.json, else the last capture.
receipt_state() {
	"$PYTHON" -c 'import json, sys
from pathlib import Path
run = Path(sys.argv[1])
paths = [run / "collect.json"] if (run / "collect.json").is_file() else sorted(run.glob("captures/*/collect.json"))
print(json.loads(paths[-1].read_text())["state"] if paths else "NONE")' "$RUN_DIR"
}

# collect_attempts N: up to N collects 300 s apart until the primary receipt exists.
collect_attempts() {
	n=$1
	i=1
	while :; do
		if "$PYTHON" scripts/kaggle_run.py collect "$RUN_DIR" >"$RUNNER_TEMP/collect.txt" 2>&1; then
			tail -n 3 "$RUNNER_TEMP/collect.txt"
		else
			echo "::warning::collect attempt $i: $(tail -n 1 "$RUNNER_TEMP/collect.txt")"
		fi
		[ -f "$RUN_DIR/collect.json" ] && return 0
		[ "$i" -ge "$n" ] && return 0
		i=$((i + 1))
		sleep 300
	done
}

# commit_and_push LABEL: commit the run directory and the copied result, push to BRANCH.
commit_and_push() {
	label=$1
	git add -f -- "$RUN_DIR"
	found=$(find "$RUN_DIR/output" -type f -path "*/$RESULT_PATH" 2>/dev/null | sed -n 1p)
	if [ -n "$found" ]; then
		cp "$found" "$RESULT_PATH"
		git add -f -- "$RESULT_PATH"
	fi
	if git diff --cached --quiet; then
		echo "nothing new to commit"
		return 0
	fi
	git -c user.name='github-actions[bot]' \
		-c user.email='41898282+github-actions[bot]@users.noreply.github.com' \
		commit -q -m "results/kaggle: collect $(basename "$RUN_DIR") ($label)" \
		-m "kaggle_run.py collect wrote the receipt and kaggle_run.py verify
accepted every retained receipt in workflow run $GITHUB_RUN_ID."
	for _ in 1 2 3; do
		git push -q origin "HEAD:$BRANCH" && return 0
		git pull -q --rebase origin "$BRANCH"
	done
	echo "::error::push to $BRANCH failed three times"
	return 1
}

# notify STATE: one comment per state on the open pull request whose head is BRANCH.
notify() {
	state=$1
	number=$(gh pr list --head "$BRANCH" --state open --json number --jq '.[0].number // empty')
	if [ -z "$number" ]; then
		echo "no open pull request has head $BRANCH; the run summary carries the result"
		return 0
	fi
	marker="<!-- kaggle-collect:$(basename "$RUN_DIR"):$state -->"
	seen=$(MARKER="$marker" gh api --paginate "repos/$GITHUB_REPOSITORY/issues/$number/comments?per_page=100" \
		--jq '[.[] | select((.body // "") | contains(env.MARKER))] | length' | awk '{n += $1} END {print n + 0}')
	[ "$seen" -gt 0 ] && return 0
	printf '%s\nThe Kaggle collector recorded `%s` for `%s` at %s (workflow run %s/%s/actions/runs/%s).\n\ncc @%s\n' \
		"$marker" "$state" "$RUN_DIR" "$(git rev-parse --short HEAD)" "$GITHUB_SERVER_URL" "$GITHUB_REPOSITORY" \
		"$GITHUB_RUN_ID" "$GITHUB_REPOSITORY_OWNER" >"$RUNNER_TEMP/notice.md"
	gh api "repos/$GITHUB_REPOSITORY/issues/$number/comments" -F "body=@$RUNNER_TEMP/notice.md" --jq .html_url
}

collect() {
	pushed=$(pushed_epoch)
	state=$(read_state 2>/dev/null)
	if [ "$state" != terminal ]; then
		# The pull time passed with the version still live: take what it serves now.
		collect_attempts 1
		"$PYTHON" scripts/kaggle_run.py verify
		commit_and_push "pull at $(date -u +%H:%MZ), $(receipt_state)"
		notify "pull-$(receipt_state)"
		[ "$(poll $((pushed + HARD_AFTER)))" = terminal ] || {
			echo "::error::the version was still live at the hard deadline"
			return 1
		}
	fi
	# A session's output files appear a short while after its terminal status.
	sleep 180
	collect_attempts 4
	"$PYTHON" scripts/kaggle_run.py verify
	final=$(receipt_state)
	commit_and_push "$final"
	notify "$final"
	echo "### Kaggle collect: $final" >>"$GITHUB_STEP_SUMMARY"
	[ "$final" = COMPLETE ]
}

case ${1:-} in
watch) watch "${2:?budget seconds}" ;;
collect) collect ;;
*)
	echo "usage: kaggle_collect.sh watch BUDGET_SECONDS | collect" >&2
	exit 2
	;;
esac
