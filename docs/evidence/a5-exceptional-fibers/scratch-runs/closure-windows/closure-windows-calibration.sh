#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
export PYTHON="$HOME/a5env/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 MALLOC_ARENA_MAX=2
trap 'run_status=$?; printf "%s\n" "$run_status" > docs/local/windows-closure-calibration.done' EXIT
exec 9>"$HOME/a5/engine/.mem.lock"
flock -n 9 || exit 75
available_kib=$(sed -n 's/^MemAvailable:[[:space:]]*\([0-9]*\).*/\1/p' /proc/meminfo)
if test "$available_kib" -lt 8388608; then
    printf 'The eight-GiB calibration reservation exceeds the observed available WSL memory.\n' >&2
    exit 75
fi
printf 'WSL MemAvailable at admission: %s KiB\n' "$available_kib" > docs/local/windows-closure-calibration-admission.txt
/usr/bin/time -v -o docs/local/windows-closure-calibration.time \
    timeout -k 10 1020 "$PYTHON" -B -W error docs/local/closure-windows-calibration.py --run \
    > docs/local/windows-closure-calibration.log 2>&1
