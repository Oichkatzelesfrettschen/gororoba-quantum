#!/bin/sh
# Usage: fetch_gororoba_math.sh DEST PATH...
# Check out the gororoba-math commit named by ci/gororoba_math.pin into DEST,
# materializing only the cone directories PATH... (blobs outside them are never
# downloaded). The checkout is detached at the pin and `git rev-parse HEAD` must
# equal it, so a moved branch or a truncated fetch fails the step. Writes only
# under DEST; a second run on the same DEST fetches and re-checks out.
# GOROROBA_MATH_URL (default: the public repository) is an https:// URL or the
# absolute path of an existing directory; any other value, `ext::` command URLs
# included, ends the run with status 2, and every git command runs with
# protocol.ext.allow=never.
# DEST is accepted in exactly three states: a path that does not exist, an
# empty directory, or a repository this script created, which passes all of:
# the file .git/gororoba-math-pin-fetch exists, `git for-each-ref refs/heads`
# prints nothing (the script only detaches), and remote.origin.url equals the
# validated URL. The script resets and cleans DEST, so any other DEST ends the
# run with status 2 and stays untouched. Exit status: 0 fetched, 1 the fetch or
# the pin comparison failed, 2 a usage, pin-file, URL or DEST error.
set -eu

REPO_URL=${GOROROBA_MATH_URL:-https://github.com/Oichkatzelesfrettschen/gororoba-math.git}
bad_url() {
  echo "fetch_gororoba_math: GOROROBA_MATH_URL must be an https:// URL or an absolute directory without '::' or whitespace" >&2
  exit 2
}
case "$REPO_URL" in
*::* | *[[:space:]]*) bad_url ;;
https://?*) ;;
/*) [ -d "$REPO_URL" ] || bad_url ;;
*) bad_url ;;
esac
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

git_safe() {
  git -c protocol.ext.allow=never "$@"
}

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
  branches=$(git_safe -C "$dest" for-each-ref refs/heads)
  [ -z "$branches" ] || {
    echo "fetch_gororoba_math: $dest holds a branch, which this script never creates" >&2
    exit 2
  }
  origin=$(git_safe -C "$dest" config --get remote.origin.url || true)
  [ "$origin" = "$REPO_URL" ] || {
    echo "fetch_gororoba_math: remote.origin.url of $dest is not $REPO_URL" >&2
    exit 2
  }
elif [ -e "$dest" ] && [ -n "$(ls -A "$dest")" ]; then
  echo "fetch_gororoba_math: $dest exists and is not empty" >&2
  exit 2
else
  mkdir -p "$dest"
  git_safe -C "$dest" init -q
  git_safe -C "$dest" remote add origin "$REPO_URL"
  : >"$dest/$marker"
fi
git_safe -C "$dest" sparse-checkout init --cone
git_safe -C "$dest" sparse-checkout set "$@"
retry git_safe -C "$dest" fetch -q --filter=blob:none origin "$pin"
git_safe -C "$dest" checkout -q --detach "$pin"
# A reused DEST can hold edited tracked files or stray untracked ones; the
# reset and clean leave exactly the pinned tree in the sparse paths.
git_safe -C "$dest" reset -q --hard "$pin"
git_safe -C "$dest" clean -q -ffdx
head=$(git_safe -C "$dest" rev-parse HEAD)
[ "$head" = "$pin" ] || {
  echo "fetch_gororoba_math: HEAD $head differs from pin $pin" >&2
  exit 1
}
echo "gororoba_math $head in $dest"
