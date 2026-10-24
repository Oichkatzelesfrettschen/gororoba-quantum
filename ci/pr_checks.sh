#!/bin/sh
# Pull-request checks, one command for .github/workflows/pr.yml and local runs:
#   sh ci/pr_checks.sh lint            Ruff check and format over the code directories
#   sh ci/pr_checks.sh types           mypy over the same directories
#   sh ci/pr_checks.sh tests [ARG...]  pytest without the audit marker, over tests/ or the
#                                      given paths; -m audit PATH selects the marked tests
# PYTHON names an interpreter holding the pins (sh ci/build_host_envs.sh builds
# one locally). The environment below is the one the hosted jobs run under.
set -eu
PYTHON=${PYTHON:-python3}
export PYTHON
# ci/pinned_tool.py takes ruff and mypy from PATH, so the interpreter's own
# bin directory, a venv's, leads it.
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

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
code_dirs="ci tests gororoba_quantum scripts kaggle_kernel"

[ $# -ge 1 ] || { echo "usage: sh ci/pr_checks.sh lint|types|tests [PATH...]" >&2; exit 2; }
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
*)
	echo "pr_checks.sh: unknown check $check" >&2
	exit 2
	;;
esac
