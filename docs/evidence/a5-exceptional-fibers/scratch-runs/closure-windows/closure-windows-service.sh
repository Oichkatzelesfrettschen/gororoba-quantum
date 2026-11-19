#!/bin/sh
set -eu
slug=$1
mode=$2
unit=$3
case "$slug:$mode" in
    e8-nm:write|e8-np:write) workers=4; budget_gib=24 ;;
    e8-nm:check|e8-np:check) workers=1; budget_gib=8 ;;
    *) exit 64 ;;
esac
cd "$(dirname "$0")/../.."
export PYTHON="$HOME/a5env/bin/python"
export PYTHONDONTWRITEBYTECODE=1 GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS="$workers" MALLOC_ARENA_MAX=2
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
solver_directory=$("$PYTHON" -B -c 'import sysconfig; print(sysconfig.get_paths()["purelib"] + "/sage_wheels/bin")')
export PATH="$solver_directory:$PATH"
exec 9>"$HOME/a5/engine/.mem.lock"
flock -n 9 || exit 75
admission="docs/local/windows-full-$slug-$mode-admission.txt"
systemctl --user show "$unit" --property=MemoryMax --property=MemorySwapMax --property=MemoryHigh \
    --property=RuntimeMaxUSec --property=KillMode --property=TimeoutStopUSec > "$admission"
for property in MemoryMax MemorySwapMax MemoryHigh; do
    value=$(systemctl --user show "$unit" --property="$property" --value)
    test "$value" = infinity || exit 75
done
available_kib=$(sed -n 's/^MemAvailable:[[:space:]]*\([0-9]*\).*/\1/p' /proc/meminfo)
native_kib=$(powershell.exe -NoProfile -NonInteractive \
    -Command '(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory' | tr -d '\r\n ')
case "$native_kib" in ''|*[!0-9]*) exit 75 ;; esac
required_kib=$((budget_gib * 1024 * 1024))
printf 'Admission UTC: ' >> "$admission"
date -u '+%Y-%m-%dT%H:%M:%SZ' >> "$admission"
printf 'WSL MemAvailable: %s KiB\nNative Windows FreePhysicalMemory: %s KiB\nPlanning budget: %s GiB\n' \
    "$available_kib" "$native_kib" "$budget_gib" >> "$admission"
test "$available_kib" -ge "$required_kib" && test "$native_kib" -ge "$required_kib" || exit 75
/usr/bin/time -v -o "docs/local/windows-full-$slug-$mode.time" \
    "$PYTHON" -B -W error docs/local/closure-windows-stage.py --slug "$slug" --mode "$mode"
