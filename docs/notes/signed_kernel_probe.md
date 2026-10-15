# Signed perturbation of a certified kernel

A zero-product probability tests cancellation well, but near a dark point it
loses the sign of a perturbation. A matched interference reference turns that
sign-blind, second-order response into a signed, first-order one.
`gororoba_quantum/signed_kernel_probe.py` certifies the construction, builds
both readouts, applies the mutations that must break the signed law, and
prices both readouts. The evidence is
[result.json](../evidence/signed_kernel_probe/result.json), re-derived by gate
core-273 in normal and optimized modes.

## Construction

All in the sedenions (D = 16, `cd_core.cd_sign`); algebra bit b sits on qubit b.

- **Exact certificate.** The integer vector `e4 - e15` satisfies
  `(L_e1 + L_e10)(e4 - e15) = 0`. With `v = L_e2 u`, the vector `v` has the
  norm of `u` and is orthogonal to it. For
  `L(t) = L_e1 + L_e10 + t L_e2`, `alpha = 2 + |t|` and `B = L / alpha`, the
  kernel identity gives `B(t) u = t v / alpha`. Hence:
  - `p(t) = ||B u||^2 = t^2 / (2 + |t|)^2`;
  - `Re<v|B|u> = t / (2 + |t|)`.

  The laws are checked in exact rationals at `t` in {-1/5, -1/20, 0, 1/20, 1/5}.
  At `t = +-1/20` they give 1/1681 and +-1/41.
- **Block encoding.** The block encoding is PREP, then SELECT, then PREP^dagger.
  - PREP puts amplitudes `sqrt(|t|/alpha)`, `sqrt(1/alpha)` and `sqrt(1/alpha)` on selector values 0, 1, 2.
  - SELECT applies `sign(t) L_e2`, `L_e1` and `L_e10`.
  - The selector-00 block of the full unitary equals `B(t)` entry by entry, to 1e-12.

  Mapping selector value `s` to the unit `m(s) = 2 xor s0*3 xor s1*8` makes the
  label map affine over GF(2), since the zero-amplitude value 3 is free. Every
  term's basis permutation is then X on bit 1 plus three CX, and every sign
  goes into one diagonal.
- **Dark readout.** Load `u` with `sparse_pair_prep`, apply the block
  encoding, and read the selector. `P(00) = p(t)`, which is even in `t`.
- **Signed readout.** A control qubit in `|+>` selects SELECT (control 0) or
  `L_e2` (control 1). Both branches share the prepared selector
  `|s> = sum_k a_k |k>`, so `<X_c> = sum_k a_k^2 <v|L_k|u> = Re<v|B(t)|u>`
  with no PREP^dagger. The X on bit 1 is common to both branches, so only the
  diagonal and the three selector CX are controlled. `sign(t)` sits on the e2
  entries of the diagonal inside branch 0, which makes it a relative phase
  between the branches.

## Mutations

| Mutation | Signed readout at t = -1/20 | Required |
| --- | --- | --- |
| none | -1/41 | the signed law |
| `|t| L_e2` in place of `t L_e2` | +1/41 | sign flips |
| selector prepared in branch 0 only | -0.156 | the overlap changes |

The second mutation leaves the branches with different selector states at
recombination, the workspace failure the algebra circuit rules name. The dark
readout cannot distinguish the first mutation, because `p(t) = p(-t)`.

## Price

Compiled on FakeFez (optimization level 3, seed 20261015), the dark probe
costs 110 CZ and the signed probe 272 CZ. The table gives the shots needed to
resolve the perturbation at z = 3:

- dark counting needs `ln 20 / p` shots at zero background, and
  `z^2 b(1-b) / p^2` above a background `b`;
- the signed readout needs `z^2 (1 - V^2 s^2) / (V s)^2` with
  `s = t / (2 + |t|)`.

The hardware scenario takes the ibm_kingston Design B fringe, a 46-CZ
circuit: dark floor `b = 0.182` and visibility `V = 0.678`. The signed
visibility is further multiplied by `(1 - e)^(272 - 46)` at the median
FakeFez CZ error, giving 0.286. The dark count keeps `b` unchanged, which is
a lower bound for a probe with more CZ than Design B, so the table favors
dark counting.

| t | Scenario | Dark shots | Signed shots | Dark resolves sign |
| ---: | --- | ---: | ---: | --- |
| 0.05 | ideal | 5,036 | 15,120 | no |
| 0.05 | Kingston Design B fringe | 3,786,192 | 185,212 | no |
| 0.1 | ideal | 1,322 | 3,961 | no |
| 0.1 | Kingston Design B fringe | 260,582 | 48,583 | no |
| 0.2 | ideal | 363 | 1,080 | no |
| 0.2 | Kingston Design B fringe | 19,618 | 13,324 | no |

At zero background, dark counting detects `|t|` in about three times fewer
shots and never yields its sign. Above the measured floor, the cost of dark
counting grows as `t^-4` and that of the signed readout as `t^-2`. The signed
readout is about 20 times cheaper at `t = 0.05` and about 1.5 times cheaper
at `t = 0.2`, and it gives the sign. No universal speedup follows: the
advantage requires a background, and at small `t` the shot count is large.
At about 0.27 ms per shot, the 13,324 shots at `t = 0.2` take about 3.6 s of
QPU time per sign; the 185,212 shots at `t = 0.05` take about 50 s.

## What this establishes

It establishes the following:

- an exact certificate of the kernel and of both laws;
- statevector conformance of both circuits;
- block-encoding equality;
- mutation sensitivity;
- a compiled cost and a shot price under stated scenarios.

It establishes no hardware performance, and it carries no noise-model
prediction of the signed visibility beyond the scenario arithmetic. A
hardware case at `t = +-0.2` is affordable, and it would need its own written
case and approval.
