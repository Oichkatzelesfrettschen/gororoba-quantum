# Ascella order-coherence coefficient derivation

The [science plan](../../design/ascella-signed-coherence-conformance.md) asks
whether hardware preserves commutator/anticommutator interference. This bundle
supplies local mathematical evidence and a theoretical artwork preview.
It contains no new hardware acquisition.

[replay.py](replay.py) checks nine exact identities with SymPy (the coherence
circle and its intensity links, the complex form `C=(1-exp(-2i theta))/2`, the
complex-gain coefficients, cancellation of a common phase, and the rotated
coefficient relations), compares source-state and coherence formulas with the
repository operator at 51 points, and extracts all five discrete harmonic
coefficients at each of five planned angles. It also computes the
17-endpoint Hoeffding radii, their scale against 16 and 27 endpoints, the
pointwise envelope of the 0.05 coefficient tolerance, the projected
simultaneous X/Y radius at each planned angle, and the equal-contrast and
sign-even counterexamples, checking the latter for positivity. [derivation.json](derivation.json) records residuals,
source and pilot-analysis digests, tool versions and the pilot's dark counts.
The pilot counts come from the retained analysis; the curve is theoretical.

![Theoretical coefficient atlas](coefficient-atlas.svg)

The four panels show the sign-odd coherence circle with angle labels,
traversal direction and projected simultaneous radii; the sign-even response
the primary endpoints cancel, with the replay's counterexample; the angle
harmonics; and the two coherence branches that direct intensity cannot
distinguish. The black
points mark planned angles; they are not measurements. The final measured
artwork uses new retained counts and simultaneous uncertainty.

Run from the repository root with the intended interpreter:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
"$PYTHON" docs/evidence/ascella-order-coefficients/replay.py
```

The default invocation recomputes and prints its checks without writing files.
The `--write` option generates the report and SVG in the script directory;
use a separate successor location for any later retained revision. Numerical
residuals use an absolute 1e-12 bound. Exact identities must reduce to zero.
The checks establish these finite formulas; they do not verify a future native
payload, a physical analyzer or a continuous experimental response.
