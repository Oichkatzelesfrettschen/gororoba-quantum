#!/bin/sh
# Build the host environments ci/pins.py falls back to (pins.HOST_ENVS) under
# ${XDG_CACHE_HOME:-~/.cache}/gororoba-quantum/: the current runtime's venv
# from requirements.txt and ci/requirements-ci.txt, and the qiskit-2.5 replay
# venv from ci/requirements-replay.txt. Each sits on the setup-python version
# of .github/workflows/ci.yml (pins.PYTHON_VERSION, which uv provides) and
# installs through ci/install_pins.sh, the installer CI's jobs run, so a local
# gate sees the packages a hosted one does. A rerun installs into the existing
# venvs and so repairs one whose packages drifted from the pins.
set -eu
cd "$(dirname "$0")/.."
python_version=3.14.7
cache=${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum
for spec in "ci-py$python_version:requirements.txt" "replay-py$python_version:ci/requirements-replay.txt"; do
    venv=$cache/${spec%%:*}
    if [ ! -x "$venv/bin/python3" ]; then
        uv venv --quiet --seed --python "$python_version" "$venv"
    fi
    PYTHON=$venv/bin/python3 REQUIREMENTS_FILE=${spec#*:} sh ci/install_pins.sh
done
