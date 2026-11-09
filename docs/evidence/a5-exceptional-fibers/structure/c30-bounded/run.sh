#!/bin/sh
# Run one case of the C30 bounded check inside a cgroup memory scope and a wall-time limit, from any directory.
#   sh run.sh CASE [LIMIT_S]      CASE names sing/CASE.sing; the limit defaults to 900 s, the memory cap is 8 GiB
# The exit status is the Singular status (124 when the wall-time limit ends the run; 3 when Singular printed an error).
# Writes logs/CASE.log (Singular stdout), logs/CASE.result (RESULT lines, one per stage as it exists), logs/CASE.err,
# logs/CASE.time (/usr/bin/time -v: elapsed seconds and peak resident set; empty when `timeout` ends the run) and
# logs/CASE.rss (resident set of the Singular process every 30 s). Exit 124 in logs/CASE.result means the wall-time
# limit ended the run.
# SINGULAR names the binary (default: the passagemath wheel in the repository's host venv).
set -eu
case_name=${1:?usage: run.sh CASE [LIMIT_S]}
limit_s=${2:-900}
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../../../.." && pwd)
if [ -z "${SINGULAR:-}" ]; then
    for candidate in "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular; do
        if [ -x "$candidate" ]; then SINGULAR=$candidate; break; fi
    done
fi
: "${SINGULAR:?run.sh: no Singular found; set SINGULAR}"
log="$here/logs/$case_name"
mkdir -p "$here/logs"
cd "$root"
if [ -e "$log.result" ]; then
    echo "run.sh: $log.result exists; move it aside first" >&2
    exit 2
fi
# capped GIB CMD...: a cgroup scope (MemoryMax, no swap) where the user bus answers, else prlimit --as, which caps
# the process's virtual address space rather than its resident memory.
capped() {
    gib=$1
    shift
    if [ -S "${XDG_RUNTIME_DIR:-/nonexistent}/bus" ]; then
        systemd-run --user --scope -q -p MemoryMax="${gib}G" -p MemorySwapMax=0 "$@"
    else
        prlimit --as=$((gib * 1073741824)) "$@"
    fi
}
export MALLOC_ARENA_MAX=2
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
sampler=
cleanup() {
    if [ -n "$sampler" ]; then kill "$sampler" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM
(
    while :; do
        pid=$(pgrep -f "Singular -q --no-rc .*sing/$case_name.sing" | tail -n 1 || true)
        rss=
        if [ -n "$pid" ]; then rss=$(awk '/VmRSS/ {print $2}' "/proc/$pid/status" 2>/dev/null || true); fi
        if [ -n "$rss" ]; then printf '%s %s\n' "$(date -u +%FT%TZ)" "$rss" >> "$log.rss"; fi
        sleep 30
    done
) &
sampler=$!
rc=0
capped 8 timeout -k 10 "$limit_s" /usr/bin/time -v -o "$log.time" \
    "$SINGULAR" -q --no-rc "$here/sing/$case_name.sing" < /dev/null > "$log.log" 2> "$log.err" || rc=$?
# Singular reports an interpreter error with a line beginning "?" and can still exit 0, so such a line fails the run.
if [ "$rc" -eq 0 ] && grep -q '^ *? ' "$log.log" "$log.err"; then rc=3; fi
printf 'exit %s\n' "$rc" >> "$log.result"
for f in "$log.log" "$log.time" "$log.err" "$log.result"; do
    sed -i -e "s|$root/||g" -e "s|$HOME|~|g" "$f"
done
exit "$rc"
