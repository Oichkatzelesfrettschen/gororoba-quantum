# A_5 kernel bundles: exact transport and symmetry evidence

This evidence directory executes the
[kernel-bundle program](../../design/a5-kernel-bundles-program.md). The current result corrects the complex transport
used to represent the real annihilator kernel and fixes the action of the canonical complex structure. The Lie-algebra
solve, closed-form frames, transition atlas, unit-section topology, and characteristic classes remain open.

Every computation uses rational or Gaussian-rational arithmetic. [`result.json`](result.json) is the output of
[`kernel_symmetry.py`](kernel_symmetry.py) `--out`. The focused contracts and both mutation controls run without random
input.

## Conventions

Write a doubly pure element of A_5 as `y = (p, q)` and put `z = p + i q` in C^15. For `x = (r, s)` in A_5, define

`phi(x) = r + i conjugate(s)` and `psi(x) = conjugate(phi(x))`.

The bordered complex matrix is

`A(z, t) = [[0, -t^T], [t, C_z]]`,

where `C_z` is the imaginary block of left multiplication by `z` in the complexified sedenions. The representative
names `B9`, `V`, `VB`, `Vap`, `Vam`, `Np`, and `Nm` are the open-orbit representatives B9, V, V intersect B9,
V^a_+, V^a_-, N_+, and N_- from the
[regularity record](../a5-strata-regularity/README.md#conventions).

## The transport uses the conjugated input

The Pfaffian record proves the real-linear identity

`phi(y x) = A(z, conjugate(z)) conjugate(phi(x))`.

Consequently,

`ker_R L_y = psi^-1(ker_C A(z, conjugate(z)))`

and equivalently

`phi(ker_R L_y) = conjugate(ker_C A(z, conjugate(z)))`.

The formula without the outer input conjugation is false. Exact right-kernel bases of `L_y` refute
`A(z, conjugate(z)) phi(x) = 0` at every one of the seven representatives of nullity at least 12. The real kernel
dimensions are 12 on B9, V, VB, V^a_+, and V^a_-, and 16 on N_+ and N_-; the bordered-matrix complex kernel
dimensions are respectively 6 and 8. Inclusion under `psi` plus equality of these real dimensions proves equality of
the kernels at each representative.

The falsifier was a representative whose exact `L_y` kernel either escaped `ker A` under `psi`, or whose real
nullity differed from twice the complex nullity. No such representative occurred. The control removes the input
conjugation; all seven representatives then fail. The exact rows are in
[`result.json`](result.json), and [`test_kernel_symmetry.py`](test_kernel_symmetry.py) fixes the expected nullities.

## The canonical complex structure is explicit

Let `J = L_(e_16)`. Direct Cayley-Dickson multiplication gives

`J(r, s) = (-conjugate(s), conjugate(r))`,

so `phi(J x) = i phi(x)` and `psi(J x) = -i psi(x)`. The anticommutation `J L_y = -L_y J` therefore makes `J` preserve
every real kernel, while the identification with `ker A` through `psi` carries `J` to multiplication by `-i`. The
identification through `phi` is complex-linear but lands in the coefficientwise conjugate of `ker A`. This conjugate
bundle distinction affects the sign convention for odd Chern classes and must remain explicit in the transition and
invariant deliverables.

The falsifier was any exact kernel vector for which `J x` left the kernel, `phi(J x)` differed from `i phi(x)`, or
`psi(J x)` differed from `-i psi(x)`. The seven representatives supply 92 exact real kernel basis vectors; none
falsified the identities. The control reverses `J` and the phase check fails.

## Scope

The finite representative computation establishes the corrected transport and `J` action at the points required by
the first sub-step. The computation does not yet establish a kernel-transporting Lie group over an entire orbit, a
second anticommuting complex structure, a closed-form frame, or a bundle invariant. In particular, the complex orbit
symmetry of the rank locus remains distinct from a real symmetry of the kernel pencil.

## Replay

```sh
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=4
export PYTHON="${PYTHON:-python3}"
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/test_kernel_symmetry.py
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_symmetry.py --self-test
"$PYTHON" -B -W error -O docs/evidence/a5-kernel-bundles/kernel_symmetry.py --self-test
"$PYTHON" -B -W error docs/evidence/a5-kernel-bundles/kernel_symmetry.py \
    --out docs/evidence/a5-kernel-bundles/result.json
```
