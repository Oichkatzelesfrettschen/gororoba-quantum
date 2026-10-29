#!/bin/sh
# Run every byte-replay gate (each ci/gates.json gate whose command runs
# ci/replay_check.py) on a CPU that advertises avx512f, passing ARGS to
# ci/run_gates.py:
#   sh ci/avx512_replay.sh [--replay-python PATH]
#
# numpy's dispatched loops above x86-64-v3 round differently from its AVX2
# loops, and NPY_DISABLE_CPU_FEATURES caps the dispatch at x86-64-v3; only an
# AVX-512 CPU exercises that cap, so only one tests that the runner-image
# records replay there. A CPU without avx512f reports the check as not run and
# exits 0, and under GitHub Actions also writes a notice and a step summary.
set -eu
cd "$(dirname "$0")/.."
PYTHON=${PYTHON:-python3}
export PYTHON
report() {
    echo "avx512 replay: $1"
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        echo "::notice title=AVX-512 replay::$1"
        [ -n "${GITHUB_STEP_SUMMARY:-}" ] && echo "AVX-512 replay: $1" >> "$GITHUB_STEP_SUMMARY"
    fi
    return 0
}
model=$(sed -n 's/^model name[[:space:]]*: //p' /proc/cpuinfo 2>/dev/null | head -n 1)
if ! grep -qw avx512f /proc/cpuinfo 2>/dev/null; then
    report "not run; the CPU flags lack avx512f ($model)"
    exit 0
fi
gates=$("$PYTHON" -B -c '
import json
names = [gate["name"] for gate in json.load(open("ci/gates.json"))["gates"] if "ci/replay_check.py" in gate["cmd"]]
print(",".join(names))
')
if [ -z "$gates" ]; then
    echo "avx512 replay: ci/gates.json names no ci/replay_check.py gate" >&2
    exit 1
fi
if "$PYTHON" ci/run_gates.py --gates "$gates" "$@"; then
    report "ran $gates on an avx512f CPU ($model); every record replayed bit for bit"
else
    status=$?
    report "ran $gates on an avx512f CPU ($model); a replay gate failed (run_gates exit $status)"
    exit "$status"
fi
