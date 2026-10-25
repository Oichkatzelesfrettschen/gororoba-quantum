#!/bin/sh
# Pull-request checks, one command for .github/workflows/pr.yml and local runs:
#   sh ci/pr_checks.sh lint            Ruff check and format over the code directories
#   sh ci/pr_checks.sh types           mypy over the same directories
#   sh ci/pr_checks.sh tests [ARG...]  pytest without the audit marker, over tests/ or the
#                                      given paths; -m audit PATH selects the marked tests
#   sh ci/pr_checks.sh gates [ARG...]  the ci/gates.json gates the branch's diff from
#                                      origin/main reaches, of at most GATES_MAX_SECONDS
#                                      (default 15) measured seconds; GATES_LEDGER names an
#                                      audit ledger whose read sets widen the selection
# PYTHON names an interpreter holding the pins; left unset, the host
# environment sh ci/build_host_envs.sh builds serves. The environment below is
# the one the hosted jobs run under.
set -eu
[ $# -ge 1 ] || { echo "usage: sh ci/pr_checks.sh lint|types|tests|gates [ARG...]" >&2; exit 2; }
root=$(cd "$(dirname "$0")/.." && pwd)
# The lane holds the host-environment lock shared until it exits, so sh ci/build_host_envs.sh, which takes it
# exclusively, cannot rebuild the interpreter under a verdict, and a lane started during a rebuild waits for it.
lock=${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/host-envs.lock
mkdir -p "$(dirname "$lock")"
exec 9>"$lock"
if ! flock -n -s 9; then
    echo "waiting for sh ci/build_host_envs.sh to release $lock" >&2
    flock -s 9
fi
# ci/pins.py resolve_lane holds the lane to an interpreter carrying its pins:
# an explicit PYTHON as named, else the host environment ci/build_host_envs.sh
# builds, else python3. A drifted interpreter exits 2 naming the differing
# pins, since a verdict under other packages says nothing about the pinned run.
PYTHON=$("${PYTHON:-python3}" "$root/ci/pins.py" lane "$1") || exit 2
# A relative interpreter path names a file from the caller's directory, and
# the checks below change directory; dirname keeps a venv's symlinked python.
case $PYTHON in
/*) ;;
*/*) PYTHON=$(cd "$(dirname "$PYTHON")" && pwd)/$(basename "$PYTHON") ;;
esac
export PYTHON
# The interpreter's own bin directory, a venv's, leads PATH for every tool a
# check starts; ci/pinned_tool.py runs ruff and mypy as its modules.
bin=$(dirname "$(command -v "$PYTHON")")
PATH=$bin:$PATH
export PATH
# Qiskit 2.6 Rust TLS plus late-loaded Aer OpenMP need reserved loader capacity.
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 BLIS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 RAYON_NUM_THREADS=1 QISKIT_NUM_PROCS=1
export OPENBLAS_CORETYPE=Haswell
export NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR"
export GOROROBA_PINS_REQUIRED=1 PYTHONHASHSEED=0 MPLBACKEND=Agg

cd "$root"
code_dirs="ci tests gororoba_quantum scripts kaggle_kernel"

check=$1
shift
case $check in
lint)
	# shellcheck disable=SC2086
	"$PYTHON" ci/pinned_tool.py ruff check $code_dirs
	# shellcheck disable=SC2086
	"$PYTHON" ci/pinned_tool.py ruff format --check --target-version py313 $code_dirs
	;;
types)
	# mypy resolves the bare sibling imports from gororoba_quantum/.
	cd gororoba_quantum
	"$PYTHON" ../ci/pinned_tool.py mypy . ../scripts ../ci ../tests ../kaggle_kernel
	;;
tests)
	[ $# -ge 1 ] || set -- tests
	log=$(mktemp)
	code=$(mktemp)
	trap 'rm -f "$log" "$code"' EXIT
	# The output streams live, so a job killed at its timeout still shows the run.
	{
		status=0
		"$PYTHON" -B -m pytest -n auto --dist loadgroup -m "not audit" --durations=25 "$@" 2>&1 || status=$?
		echo "$status" >"$code"
	} | tee "$log"
	status=$(cat "$code")
	if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
		{
			echo '### Slowest pull-request tests'
			echo '```'
			awk '/slowest 25 durations/ { on = 1 } on { print } on && /^=+ .*(passed|failed|error).* in / { exit }' "$log"
			echo '```'
		} >>"$GITHUB_STEP_SUMMARY"
	fi
	exit "$status"
	;;
gates)
	# A record that binds its producer's digest, or a check whose input a change edits, fails only in
	# the gate that replays it; this lane runs those gates before the merge, and the nightly audit
	# keeps every gate above the seconds bound.
	base=$(git merge-base origin/main HEAD) || {
		echo "pr_checks.sh gates: no merge base with origin/main; fetch main" >&2
		exit 2
	}
	diff=$(mktemp)
	trap 'rm -f "$diff"' EXIT
	git diff --no-renames --name-status -z "$base" HEAD >"$diff"
	"$PYTHON" ci/run_gates.py --affected-by "$diff" --affected-base "$base" \
		${GATES_LEDGER:+--affected-ledger "$GATES_LEDGER"} \
		--max-seconds "${GATES_MAX_SECONDS:-15}" "$@"
	;;
*)
	echo "pr_checks.sh: unknown check $check" >&2
	exit 2
	;;
esac
