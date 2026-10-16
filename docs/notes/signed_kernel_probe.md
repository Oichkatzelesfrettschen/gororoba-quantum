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
costs 110 CZ and the signed probe 272 CZ. Both readouts are priced at one
criterion, a z = 3 resolution:

- dark counting estimates the rate `b + p` above a background `b`, needing
  `z^2 (b + p)(1 - b - p) / p^2` shots;
- the signed readout needs `z^2 (1 - V^2 s^2) / (V s)^2` shots with
  `s = t / (2 + |t|)`.

Because `p = s^2`, the two agree exactly at `b = 0` and `V = 1`. The
separate `ln 20 / p` column is the number of shots for a 95 percent chance
of at least one dark count at `b = 0`, a detection probability rather than a
precision.

The hardware scenario reads its anchor from the ibm_kingston zero-divisor
fringe run (`results/live/2026-10-15T070853.550532Z`), with `collect.json`
and `record.json` pinned by digest:

- dark floor `b = 0.1818` and visibility `V = 0.6781` from the collection;
- 42 CZ for the dark member, from the record.

The signed visibility multiplies `V` by `(1 - e)^(272 - 42)` at the median
FakeFez CZ error, giving 0.282. The dark count keeps `b`, which is a lower
bound for a probe with more CZ than the anchor, so the table favors dark
counting.

| t | Scenario | Dark shots | One dark count (95%) | Signed shots | Dark resolves sign |
| ---: | --- | ---: | ---: | ---: | --- |
| 0.05 | ideal | 15,120 | 5,036 | 15,120 | no |
| 0.05 | Kingston fringe anchor | 3,792,959 | -- | 190,895 | no |
| 0.1 | ideal | 3,960 | 1,322 | 3,961 | no |
| 0.1 | Kingston fringe anchor | 262,903 | -- | 50,074 | no |
| 0.2 | ideal | 1,080 | 363 | 1,080 | no |
| 0.2 | Kingston fringe anchor | 20,287 | -- | 13,733 | no |

At zero background and unit visibility, the signed readout costs what dark
counting costs and adds the sign. Above the measured floor, dark counting
scales as `t^-4` and the signed readout as `t^-2`, so the signed readout is
about 20 times cheaper at `t = 0.05`, 5 times at `t = 0.1` and 1.5 times at
`t = 0.2`. No universal speedup follows: the advantage requires a background,
and at small `t` the shot count is large. At about 0.27 ms per shot, the
13,733 shots at `t = 0.2` take about 3.7 s of QPU time per sign, and the
190,895 shots at `t = 0.05` about 52 s.

## What this establishes

It establishes the following:

- an exact certificate of the kernel and of both laws;
- statevector conformance of both circuits;
- block-encoding equality;
- mutation sensitivity;
- a compiled cost and a shot price under stated scenarios.

It establishes no hardware performance. A hardware case at `t = +-0.2` is
affordable, and it would need its own written case and approval.

## Under the noise model

[signed_kernel_noise](../evidence/signed_kernel_noise/README.md) evaluates
both readouts under live_run's noise model for the Kingston calibration. It
adds structure-matched probes (`matched_dark_probe`, `matched_signed_probe`)
that compile once with parameters, so every `t` runs the same gates, and the
bright control `(e4 + e15)/sqrt2` of both dark forms.

- **Gate factor.** The signed visibility is 0.60, within 10 percent of the
  `(1 - e)^CZ` factor the price above uses.
- **Sign-phase offset.** Under noise, the sign phase itself shifts
  `<Z_c>`. Two null arms at `t = 0`, which ideally both read 0, differ by
  0.037 between `phi = 0` and `phi = pi`. That exceeds the signal at
  `t = 0.05`, and it inflates the raw differential `<Z_c>(t) - <Z_c>(-t)` by
  a factor of 2.3 there. Term arms trace the offset to the e1 and e10 terms,
  whose ideal overlap is 0.
- **Null subtraction.** Subtracting each sign's null arm restores a
  constant visibility of 0.601 to 0.602 at every `t`. The signed readout
  therefore needs four arms: `+t`, `-t` and both nulls. The price above
  assumes two arms with no sign-dependent offset, so it understates the
  cost.
- **Dark count.** At the evaluated `t`, its contrast against a `t = 0` control is inverted: its
  background falls with `|t|` faster than `p(t)` rises, so a resolved
  contrast (about 404,000 equal-arm shots at `t = 0.05`) measures that
  background rather than `p(t)`. The bright control keeps its ideal
  direction at a transmission of 0.81 to 0.83, so the inversion belongs to
  the dark witness, not to the whole success channel.
