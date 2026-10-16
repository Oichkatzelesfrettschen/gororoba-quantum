#!/bin/sh
# Install the CI pins into $PYTHON: requirements.txt and ci/requirements-ci.txt,
# then the mpmath and sympy pair the retained SymPy evidence ran with.
# .github/workflows/ci.yml and the Kaggle shard kernels both run this file, so
# the two environments install the same set.
set -eu
PYTHON=${PYTHON:-python3}
"$PYTHON" -m pip install -r requirements.txt -r ci/requirements-ci.txt
# sympy 1.14.0's metadata caps mpmath below 1.4, and the retained evidence ran
# on mpmath 1.4.1; --no-deps reproduces that pair.
"$PYTHON" -m pip install --no-deps mpmath==1.4.1
# sympy 1.14.0 on PyPI still calls mpmath APIs that 1.4 deprecates or renames;
# the distribution patch the evidence ran with replaces them.
site=$("$PYTHON" -c 'import pathlib, sympy; print(pathlib.Path(sympy.__file__).parents[1])')
patch -s -p1 -d "$site" < ci/patches/sympy-1.14.0-mpmath-1.4.patch
