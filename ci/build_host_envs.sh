#!/bin/sh
# Build the host environments ci/pins.py falls back to (pins.HOST_ENVS) under
# ${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/: the current runtime's venv
# from requirements.txt and ci/requirements-ci.txt, and the qiskit-2.5 replay
# venv from ci/requirements-replay.txt. Each sits on the setup-python version
# of .github/workflows/ci.yml (pins.PYTHON_VERSION, which uv provides) and
# installs through ci/install_pins.sh, the installer CI's jobs run, so a local
# gate sees the packages a hosted one does. A rerun installs into the existing
# venvs and so repairs one whose packages drifted from the pins; a venv whose
# pin inputs changed since it was built (its .pin-inputs stamp) is recreated,
# so a dependency the pins dropped leaves it as it leaves a fresh CI venv.
set -eu
cd "$(dirname "$0")/.."
python_version=3.14.7
cache=${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum
# Gate runs hold host-envs.lock shared (pins.hold_host_envs, ci/pr_checks.sh); the exclusive hold waits for
# them, so no admitted interpreter loses its packages mid-run, and runs that start meanwhile wait for the rebuild.
mkdir -p "$cache"
exec 9>"$cache/host-envs.lock"
if ! flock -n -x 9; then
    echo "waiting for running gate checks to release $cache/host-envs.lock" >&2
    flock -x 9
fi
for spec in "ci-py$python_version:requirements.txt" "replay-py$python_version:ci/requirements-replay.txt"; do
    venv=$cache/${spec%%:*}
    inputs=$(cat "${spec#*:}" ci/requirements-ci.txt ci/install_pins.sh ci/patches/* | sha256sum | cut -c1-64)
    if [ ! -x "$venv/bin/python3" ] || [ "$(cat "$venv/.pin-inputs" 2>/dev/null)" != "$inputs" ]; then
        uv venv --quiet --clear --seed --python "$python_version" "$venv"
    fi
    PYTHON=$venv/bin/python3 REQUIREMENTS_FILE=${spec#*:} sh ci/install_pins.sh
    echo "$inputs" > "$venv/.pin-inputs"
done
