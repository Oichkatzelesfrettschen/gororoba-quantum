#!/bin/sh
# Usage: install_rocq.sh
# Build the opam switch named by ci/rocq_toolchain.pin: the compiler and the
# Rocq packages resolved against the opam-repository commit the pin records.
# The opam root is $OPAMROOT (default ~/.opam); an existing switch with every
# package installed is left unchanged, so a restored cache makes a second run a
# no-op. Prints the installed package list and the rocq executable path.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
pin="$here/rocq_toolchain.pin"
field() {
  sed -n "s/^$1=//p" "$pin"
}
switch=$(field switch)
compiler=$(field compiler)
packages=$(field packages)
repo=$(field opam_repository)
for value in "$switch" "$compiler" "$packages" "$repo"; do
  [ -n "$value" ] || {
    echo "install_rocq: $pin lacks a field" >&2
    exit 2
  }
done
case "$repo" in
*[!0-9a-f]* | "")
  echo "install_rocq: opam_repository is not a hex commit" >&2
  exit 2
  ;;
esac
command -v opam >/dev/null || {
  echo "install_rocq: opam is not installed" >&2
  exit 2
}

export OPAMYES=1 OPAMROOTISOK=1
PYTHON=${PYTHON:-python3}
OPAMJOBS=$("$PYTHON" -c 'import sys; sys.path.insert(0, sys.argv[1]); import parallel; print(parallel.available_cpus())' "$here/../gororoba_quantum")
export OPAMJOBS
root=${OPAMROOT:-$HOME/.opam}
if [ ! -f "$root/config" ]; then
  opam init --bare --disable-sandboxing -n default \
    "https://github.com/ocaml/opam-repository.git#$repo"
fi
if ! opam switch list --short | grep -qx "$switch"; then
  opam switch create "$switch" "$compiler"
fi
# shellcheck disable=SC2086 # packages is a space-separated list
opam install --switch "$switch" $packages
opam list --switch "$switch" --installed
echo "rocq $(opam var --switch "$switch" bin)/rocq"
