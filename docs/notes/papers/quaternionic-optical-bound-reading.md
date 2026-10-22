# Quaternionic optical bound: exact-version reading addendum

The addendum extends the abstract-level notes without replacing their recorded
reading scopes. [P] identifies the authors' statements; [I] identifies repository
interpretation. The readings inspect the indicated pages and equations rather
than independently proving scattering theory or reproducing optical data.

## Source identities and reading scope

| Source note and version | SHA-256 of inspected PDF | Body scope |
|---|---|---|
| [Procopio et al.](1602.01624.md), arXiv 1602.01624v2 | `9c70f81417e0316018e4fbf5f156a62da07ea1c794958d2fff21a6af130a509f` | PDF pages 6, 9–10: measured ratio, interferometer model, insensitive case, conversion and uncertainty method |
| [Adler](1604.04950.md), arXiv 1604.04950v3 | `2ed4217f6df910fa828ea19509dd2a393eaa8de96340761f7d3fa4ac7f60d86f` | PDF pages 3–4: refractive-index/scattering map, localized interaction, Møller argument and decay conjecture |
| [Authors' reply](1607.01648.md), arXiv 1607.01648v1 | `b7cdea5d739b3c53240ff0114fd4cf7e117ad56651eaece2d7116e22eb1a7dd3` | PDF pages 1–2 and 5: operational defense, indefinite-metric qualification, transmitted Klein–Gordon term, equations 21–24 |

The [existing Crossref records](hypercomplex_quantum_crossref_records.md) verify
the published identities: Nature Communications 8, 15044 (2017), DOI
10.1038/ncomms15044; Physical Review A 95, 060101 (2017), DOI
10.1103/PhysRevA.95.060101; Physical Review A 96, 036101 (2017), DOI
10.1103/PhysRevA.96.036101. The registered preprints and published articles remain
distinct versions. [SOURCES.json](../../SOURCES.json) retains their PDF identities
and external-only distribution decisions. The addendum introduces source notes,
rather than republishing restricted PDF bytes.

## Observable, number and blind spot

[P] Procopio et al. report `Gamma_BOTH/Gamma_NIM = 0.99999999 +/- 2e-7` on
PDF page 6. PDF page 9, equations 16–20, defines the ratio from measured
Mach–Zehnder visibilities with both phases and with the negative-index material
alone. PDF page 10, equation 23, converts the ratio into an effective phase:

```text
theta = arccos(sqrt((1 - V_BOTH**2)/(1 - V_NIM**2)))
      = arccos(Gamma_BOTH/Gamma_NIM)
```

[P] The paragraph after equation 23 states Gaussian error propagation and
`theta < 0.03 degrees`. [I] The inspected passages supply neither a named 95%
nor 99% confidence construction. The repository therefore quotes the authors'
reported precision and method without assigning frequentist coverage.

[P] Immediately after equation 20 on PDF page 9, the authors identify an
insensitive case: `|i alpha beta - beta alpha i| = |[i,beta]| != 0` gives a
ratio of one. [I] A ratio near one bounds the specified observable under its
model; a ratio near one fails to establish universal phase commutativity.
The effective optical phase bound supplies neither a universal quaternionic
coupling constant nor a hardware-independent exclusion of quaternionic QM.

## Why the scattering disagreement stays bounded

[P] Adler uses refractive-index/forward-scattering relations on PDF page 3.
PDF page 4 assumes an anti-self-adjoint Hamiltonian comprising an asymptotic
part and a spatially localized interaction, within quaternionic Hilbert space
and the Møller formalism. Equations 6–7 give a complex on-energy-shell
S matrix at nonzero energy. Adler argues that asymptotic optical scattering
under those assumptions fails to test quaternionic effects and calls for
near-zone access. The final paragraph labels exponential decay for photons a
conjecture that needs an interaction-model calculation.

[P] The authors' reply defends operational black-box tests on PDF pages 1–2.
PDF page 5, equations 21–24, gives a surviving transmitted quaternionic term
in a Klein–Gordon potential example. PDF page 2 explicitly states that the
example does not contradict Adler's calculation: its Hamiltonian formulation
has an indefinite metric outside Adler's assumptions. The reply describes
full quaternionic relativistic field quantization as an open issue.

[I] The two arguments use different assumptions. The retained readings support
neither a general refutation of Adler's theorem nor a universal QQM exclusion.
The repository's ordinary complex operator encodings test implementation and
noise; their order sensitivity supplies a positive control for the observable,
rather than evidence of fundamental quaternionic scalars.

## Relevance and remaining obligations

[I] Calibration-aware compilation: none. Cayley-Dickson structure: interpretive
boundary. Factoring resource estimates: none. A new scalar-field discrimination
case needs an explicit physical model, accessible observable, nuisance controls
and uncertainty construction. A new confidence bound needs raw-data admission
and a specified statistical method. The [foundational review](quaternionic-foundational-source-review.md)
keeps metadata-only theorem and historical-experiment references separate.
