#!/bin/sh
# qd_schedule_tick.sh MODE [SCHEDULE]: one tick of scripts/qd_schedule.py over
# every enabled schedule, or the one SCHEDULE names. MODE run steps each
# schedule until it waits or stops; MODE plan-only plans its next job and
# writes nothing. Code runs from this checkout (main); each schedule's state
# and run directories live on the branch quandela-runs/NAME, which this script
# checks out as data, syncs before and after every step, commits and pushes
# before the next step, so an intent reaches the remote before its submit.
# Requires QUANDELA_TOKEN_FILE, DEADLINE (UTC epoch seconds), RUNNER_TEMP,
# GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT and GITHUB_REPOSITORY; GH_TOKEN opens the
# pull request of a new results branch.
set -eu
PYTHON=${PYTHON:-python3}
mode=$1
only=${2:-}
: "${QUANDELA_TOKEN_FILE:?}" "${DEADLINE:?}" "${RUNNER_TEMP:?}"
: "${GITHUB_RUN_ID:?}" "${GITHUB_RUN_ATTEMPT:?}" "${GITHUB_REPOSITORY:?}"
case $mode in run | plan-only) ;; *) echo "mode must be run or plan-only" >&2; exit 2 ;; esac
work=$RUNNER_TEMP/qd-schedule
mkdir -p "$work"
run_id=$GITHUB_RUN_ID.$GITHUB_RUN_ATTEMPT
schedule=
branch=
res=

publish() {
	"$PYTHON" -B scripts/qd_schedule.py sync "$schedule" --source . --target "$res"
	git -C "$res" add -A results/quandela
	if ! git -C "$res" diff --cached --quiet; then
		git -C "$res" commit -q -m "quandela: $(basename "$schedule" .json) state after workflow run $run_id"
		# A commit pushed to the data branch during a long collection (a registry
		# edit) rejects this push; the scheduler's paths stay disjoint from such
		# edits, so one rebase onto the remote tip publishes the checkpoint.
		if ! git -C "$res" push -q origin "HEAD:refs/heads/$branch"; then
			git -C "$res" fetch -q origin "refs/heads/$branch"
			git -C "$res" rebase -q FETCH_HEAD
			git -C "$res" push -q origin "HEAD:refs/heads/$branch"
		fi
	fi
}

# A step that fails after writing a checkpoint still publishes it, so the next
# tick reads the job as interrupted rather than unsent.
on_exit() {
	status=$?
	if [ "$status" -ne 0 ] && [ "$mode" = run ] && [ -n "$res" ]; then
		publish || echo "::error::publishing $schedule after a failed step failed" >&2
	fi
	exit "$status"
}
trap on_exit EXIT

if [ -n "$only" ]; then
	schedules=$only
else
	schedules=$("$PYTHON" -B scripts/qd_schedule.py list)
fi
# The schedule paths carry no whitespace (qd_schedule.py NAME), so they split as words.
# shellcheck disable=SC2086
"$PYTHON" -B scripts/qd_schedule.py check $schedules
git worktree prune

for schedule in $schedules; do
	name=$(basename "$schedule" .json)
	branch=quandela-runs/$name
	res=$work/res-$name
	# A detached worktree leaves no local branch behind, so a repeated tick in one checkout adds it again.
	if git ls-remote --exit-code --heads origin "$branch" >/dev/null; then
		git fetch -q origin "refs/heads/$branch"
		git worktree add -q --detach "$res" FETCH_HEAD
	else
		git worktree add -q --detach "$res" HEAD
	fi
	"$PYTHON" -B scripts/qd_schedule.py sync "$schedule" --source "$res" --target .
	if [ "$mode" = plan-only ]; then
		"$PYTHON" -B scripts/qd_schedule.py step "$schedule" --run-id "$run_id" --deadline "$DEADLINE" \
			--work "$work" --plan-only
		git worktree remove "$res"
		res=
		continue
	fi
	while :; do
		out=$("$PYTHON" -B scripts/qd_schedule.py step "$schedule" --run-id "$run_id" --deadline "$DEADLINE" \
			--work "$work")
		printf '%s\n' "$out"
		publish
		outcome=$(printf '%s' "$out" | "$PYTHON" -c 'import json, sys; print(json.load(sys.stdin)["outcome"])')
		case $outcome in continue | prepared) ;; *) break ;; esac
	done
	if git ls-remote --exit-code --heads origin "$branch" >/dev/null; then
		owner=${GITHUB_REPOSITORY%%/*}
		open=$(gh api "repos/$GITHUB_REPOSITORY/pulls?state=open&head=$owner:$branch" --jq length)
		ahead=$(gh api "repos/$GITHUB_REPOSITORY/compare/main...$branch" --jq .ahead_by)
		if [ "$open" = 0 ] && [ "$ahead" -gt 0 ]; then
			gh api -X POST "repos/$GITHUB_REPOSITORY/pulls" -f head="$branch" -f base=main \
				-f title="quandela: scheduled runs of $name" \
				-f body="Run directories and scheduler state that .github/workflows/quandela-schedule.yml wrote for results/quandela/schedules/$name.json. Before merge, register each run in docs/state/research_state.json (docs/runbooks/quandela-scheduled-runs.md)." \
				--jq .html_url ||
				echo "::warning::opening the pull request of $branch failed; open it by hand" >&2
		fi
	fi
	git worktree remove "$res"
	res=
done
