#!/bin/sh
# Run one case of the C30 bounded check inside a cgroup memory scope and a wall-time limit, from any directory.
#   sh run.sh CASE [LIMIT_S]      CASE names sing/CASE.sing; the limit defaults to 900 s, the memory cap is 8 GiB
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
SINGULAR=${SINGULAR:-$(ls "$HOME"/.cache/gororoba-quantum/venv-passagemath-singular/lib/python3*/site-packages/sage_wheels/bin/Singular)}
log="$here/logs/$case_name"
mkdir -p "$here/logs"
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
systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 \
    timeout -k 10 "$limit_s" /usr/bin/time -v -o "$log.time" \
    "$SINGULAR" -q --no-rc "$here/sing/$case_name.sing" < /dev/null > "$log.log" 2> "$log.err" || rc=$?
printf 'exit %s\n' "$rc" >> "$log.result"
for f in "$log.log" "$log.time" "$log.err" "$log.result"; do
    sed -i -e "s|$root/||g" -e "s|$HOME|~|g" "$f"
done
exit 0
