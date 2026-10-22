#!/bin/sh
# Run COMMAND... from the repository root inside the ubuntu-26.04 runner's
# userland (ci/runner-image/Containerfile) under the pins of ci/install_pins.sh
# and the gate environment of ci/run_gates.py (ci/gate_env.py), with $PYTHON
# naming the pin venv's interpreter:
#   sh ci/runner_image.sh sh -c '"$PYTHON" scripts/ANALYZER.py RUN --out FILE'
#
# A fitted float depends on the libm, the numpy and OpenBLAS kernels and the
# Python build that compute it. The gate environment fixes the kernels for
# every x86-64-v3 CPU, and this image supplies the runner's libm and Python,
# so a record written here byte-replays on the runners. The image and its pin
# venv live under ${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/runner-image/.
set -eu
cd "$(dirname "$0")/.."
cache=${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/runner-image
tarball=python-3.14.7-linux-26.04-x64.tar.gz
url=https://github.com/actions/python-versions/releases/download/3.14.7-31064857500/$tarball
digest=789b87fbfc52339c3fd619e732a5d2c4926f9ae0a7cefbc34644dcfbdb3a7150
mkdir -p "$cache"
if [ ! -f "$cache/$tarball" ]; then
    curl -sSfL -o "$cache/$tarball.part" "$url"
    mv "$cache/$tarball.part" "$cache/$tarball"
fi
echo "$digest  $cache/$tarball" | sha256sum -c --quiet
cp ci/runner-image/Containerfile "$cache/Containerfile"
# The tag names the whole build context, the Containerfile and the Python
# archive's digest, so a changed archive builds a new image.
tag=localhost/gororoba-runner:$({ cat ci/runner-image/Containerfile; echo "$digest"; } | sha256sum | cut -c1-12)
if ! podman image exists "$tag"; then
    podman build --quiet -t "$tag" "$cache" >/dev/null
fi
# The venv key reads the requirement lines alone, as pip does, so a comment
# edit reuses the installed pins.
pins=$({ sed -e 's/#.*//' -e 's/[[:space:]]*$//' -e '/^[[:space:]]*$/d' requirements.txt ci/requirements-ci.txt
    cat ci/install_pins.sh ci/patches/*; } | sha256sum | cut -c1-16)
venv=/cache/pins-$pins
run_in() {
    network=$1
    shift
    podman run --rm --network "$network" -v "$PWD:/work" -v "$cache:/cache" -w /work \
        -e PYTHON="$venv/bin/python" -e PIP_DISABLE_PIP_VERSION_CHECK=1 "$tag" "$@"
}
if [ ! -x "$cache/pins-$pins/bin/python" ]; then
    run_in host sh -c 'python3 -m venv "${PYTHON%/bin/python}" && sh ci/install_pins.sh >/dev/null'
fi
# The command reaches no network: a record depends on the tree alone.
run_in none "$venv/bin/python" ci/gate_env.py "$@"
