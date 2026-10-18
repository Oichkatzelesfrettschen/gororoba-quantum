#!/bin/sh
# Install the CI pins into $PYTHON: requirements.txt and ci/requirements-ci.txt,
# then the mpmath and sympy pair the retained SymPy evidence ran with.
# .github/workflows/ci.yml and the Kaggle shard kernels both run this file, so
# the two environments install the same set. AER_PINS, a space-separated pin
# list, replaces requirements.txt's qiskit-aer in the same resolve: the GPU
# wheel and the CPU wheel both install qiskit_aer/, so only one of them may
# enter the environment.
set -eu
PYTHON=${PYTHON:-python3}
if [ -n "${AER_PINS:-}" ]; then
    requirements=$(mktemp)
    trap 'rm -f "$requirements"' EXIT
    grep -v '^qiskit-aer==' requirements.txt >"$requirements"
    # AER_PINS splits into one argument per pin.
    # shellcheck disable=SC2086
    "$PYTHON" -m pip install -r "$requirements" -r ci/requirements-ci.txt $AER_PINS
else
    "$PYTHON" -m pip install -r requirements.txt -r ci/requirements-ci.txt
fi
# sympy 1.14.0's metadata caps mpmath below 1.4, and the retained evidence ran
# on mpmath 1.4.1; --no-deps reproduces that pair.
"$PYTHON" -m pip install --no-deps mpmath==1.4.1
# sympy 1.14.0 on PyPI still calls mpmath APIs that 1.4 deprecates or renames;
# the distribution patch the evidence ran with replaces them.
site=$("$PYTHON" -c 'import pathlib, sympy; print(pathlib.Path(sympy.__file__).parents[1])')
patch -s -p1 -d "$site" < ci/patches/sympy-1.14.0-mpmath-1.4.patch
