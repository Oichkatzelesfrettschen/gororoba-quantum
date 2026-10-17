#!/bin/sh
# Usage: fetch_open_gororoba.sh DEST PATH...
# Check out the open_gororoba commit named by ci/open_gororoba.pin into DEST,
# materializing only the cone directories PATH... (blobs outside them are never
# downloaded). The checkout is detached at the pin and `git rev-parse HEAD` must
# equal it, so a moved branch or a truncated fetch fails the step. Writes only
# under DEST; a second run on the same DEST fetches and re-checks out.
set -eu

REPO_URL=${OPEN_GOROROBA_URL:-https://github.com/Oichkatzelesfrettschen/open_gororoba.git}
here=$(cd "$(dirname "$0")" && pwd)
pin=$(tr -d ' \t\r\n' < "$here/open_gororoba.pin")
case "$pin" in
*[!0-9a-f]* | "")
  echo "fetch_open_gororoba: $here/open_gororoba.pin is not 40 hex digits" >&2
  exit 2
  ;;
esac
[ "${#pin}" -eq 40 ] || {
  echo "fetch_open_gororoba: pin length ${#pin}, expected 40" >&2
  exit 2
}
[ "$#" -ge 2 ] || {
  echo "usage: fetch_open_gororoba.sh DEST PATH..." >&2
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

if [ ! -d "$dest/.git" ]; then
  mkdir -p "$dest"
  git -C "$dest" init -q
  git -C "$dest" remote add origin "$REPO_URL"
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
  echo "fetch_open_gororoba: HEAD $head differs from pin $pin" >&2
  exit 1
}
echo "open_gororoba $head in $dest"
