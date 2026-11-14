#!/bin/sh
# Usage: fetch_gororoba_math.sh DEST PATH...
# Check out the gororoba-math commit named by ci/gororoba_math.pin into DEST,
# materializing only the cone directories PATH... (blobs outside them are never
# downloaded). The checkout is detached at the pin and `git rev-parse HEAD` must
# equal it, so a moved branch or a truncated fetch fails the step. Writes only
# under DEST; a second run on the same DEST fetches and re-checks out. DEST is
# a directory this script created (it leaves the marker file
# .git/gororoba-math-pin-fetch there) or a path that does not exist yet: the
# script resets and cleans DEST, so it refuses any other repository, a
# working checkout of gororoba-math included. Exit status: 0 fetched, 1 the
# fetch or the pin comparison failed, 2 a usage, pin-file or DEST error.
set -eu

REPO_URL=${GOROROBA_MATH_URL:-https://github.com/Oichkatzelesfrettschen/gororoba-math.git}
here=$(cd "$(dirname "$0")" && pwd)
pin=$(tr -d ' \t\r\n' < "$here/gororoba_math.pin")
case "$pin" in
*[!0-9a-f]* | "")
  echo "fetch_gororoba_math: $here/gororoba_math.pin is not 40 hex digits" >&2
  exit 2
  ;;
esac
[ "${#pin}" -eq 40 ] || {
  echo "fetch_gororoba_math: pin length ${#pin}, expected 40" >&2
  exit 2
}
[ "$#" -ge 2 ] || {
  echo "usage: fetch_gororoba_math.sh DEST PATH..." >&2
  exit 2
}
dest=$1
shift

retry() {
  n=1
  until "$@"; do
    [ "$n" -lt 3 ] || return 1
    n=$((n + 1))
    sleep $((n * 5))
  done
}

marker=.git/gororoba-math-pin-fetch
if [ -e "$dest/.git" ]; then
  [ -f "$dest/$marker" ] || {
    echo "fetch_gororoba_math: $dest is a repository this script did not create; it would be reset and cleaned" >&2
    exit 2
  }
elif [ -e "$dest" ] && [ -n "$(ls -A "$dest")" ]; then
  echo "fetch_gororoba_math: $dest exists and is not empty" >&2
  exit 2
else
  mkdir -p "$dest"
  git -C "$dest" init -q
  git -C "$dest" remote add origin "$REPO_URL"
  : >"$dest/$marker"
fi
git -C "$dest" sparse-checkout init --cone
git -C "$dest" sparse-checkout set "$@"
retry git -C "$dest" fetch -q --filter=blob:none origin "$pin"
git -C "$dest" checkout -q --detach "$pin"
# A reused DEST can hold edited tracked files or stray untracked ones; the
# reset and clean leave exactly the pinned tree in the sparse paths.
git -C "$dest" reset -q --hard "$pin"
git -C "$dest" clean -q -ffdx
head=$(git -C "$dest" rev-parse HEAD)
[ "$head" = "$pin" ] || {
  echo "fetch_gororoba_math: HEAD $head differs from pin $pin" >&2
  exit 1
}
echo "gororoba_math $head in $dest"
