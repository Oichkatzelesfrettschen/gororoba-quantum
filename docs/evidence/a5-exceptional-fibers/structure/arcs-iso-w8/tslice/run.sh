#!/bin/sh
# Run one t-space slice case under a virtual-memory cap and a wall-time limit, from any directory.
#   sh run.sh CASE [CAP_GIB [LIMIT_S]]     CASE names sing/CASE.sing; defaults 20 GiB, 900 s
# Writes logs/CASE.log (Singular stdout), logs/CASE.result (RESULT lines, one per stage as it exists), logs/CASE.err,
# logs/CASE.time (/usr/bin/time -v: elapsed and peak resident set), logs/CASE.rss (resident set every 30 s).
# SINGULAR names the binary (default: the passagemath wheel in the repository's host venv).
set -eu
case_name=${1:?usage: run.sh CASE [CAP_GIB [LIMIT_S]]}
cap_gib=${2:-20}
limit_s=${3:-900}
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../../../../.." && pwd)
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
cap_bytes=$((cap_gib * 1073741824))
log="$here/logs/$case_name"
cd "$root"
if [ -e "$log.result" ]; then
    echo "run.sh: $log.result exists; move it aside first" >&2
    exit 2
fi
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
prlimit --as="$cap_bytes" timeout -k 10 "$limit_s" /usr/bin/time -v -o "$log.time" \
    "$SINGULAR" -q --no-rc "$here/sing/$case_name.sing" < /dev/null > "$log.log" 2> "$log.err" || rc=$?
printf 'exit %s\n' "$rc" >> "$log.result"
# The retained log and time file name repository-relative paths and ~ in place of the session's home directory.
for f in "$log.log" "$log.time" "$log.err"; do
    sed -i -e "s|$root/||g" -e "s|$HOME|~|g" "$f"
done
exit 0
