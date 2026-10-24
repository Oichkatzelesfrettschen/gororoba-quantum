# Ashby, Parker and Patla 2018 -- A null test of general relativity based on a long-term comparison of atomic transition frequencies

## Source copy and license

The [NIST-hosted PDF](https://tf.nist.gov/general/pdf/2916.pdf) of the Nature Physics article remains
external to the published library. Its optional personal reading copy is
`docs/local_source_cache/ashby-2018-null-test-lpi.pdf`. The acknowledgments (PDF p. 5) state "This work is
a contribution of NIST and is not subject to US copyright", and the same page carries the Springer Nature
reprints notice. The statement speaks of US copyright only and grants no worldwide rehosting right, so
[SOURCES.json](../../SOURCES.json) records `LicenseRef-NIST-not-subject-to-US-copyright` with an
external-only decision, the SHA-256 and the reading scope.

Tag convention: [P] marks paper statements; [I] marks repository interpretation.

## Citation and provenance

- Authors: Neil Ashby; Thomas E. Parker; Bijunath R. Patla.
- Journal reference: Nature Physics 14(8), 822-826 (2018), DOI 10.1038/s41567-018-0156-2 (Crossref
  receipt below).
- Source URL: https://tf.nist.gov/general/pdf/2916.pdf, 6 PDF pages, retrieved 2026-10-24.
- SHA-256: `4a17d7f1fc2ab689a062ca492bdd493ae6fd8a64188d49e655d311220ce7a7e2`
- Reading scope: the abstract, the introduction, the data description, Eqs. 1 to 7 and Figs. 1 to 2
  (PDF pp. 1-3). The Methods (the data analysis, the maser corrections and the comparison with other
  pairs of atoms) were not read.

| Source | URL | SHA-256 of retrieved bytes | Read for |
|---|---|---|---|
| Crossref record of the version of record | https://api.crossref.org/works/10.1038/s41567-018-0156-2 | `f6d5859242742ed0252105b94ff73671b471abaee3e1111e6775d244f68d1e90` | Bibliographic identity |

## Transcribed statements

Read from the PDF above; page numbers are PDF page indices.

- [P] Abstract (p. 1): the paper studies the change in clock rates on Earth with the spatial change of the
  solar potential and constrains the variation of a non-gravitational interaction, the hyperfine
  splitting in hydrogen and cesium atoms, to `beta = (2.2 +- 2.5) x 10^-7`, "a factor of two improvement
  over previous estimates". The data compare the long-term fractional frequency of four hydrogen masers of
  the NIST ensemble with primary frequency standards of laboratories in the United States, France,
  Germany, Italy and the United Kingdom over more than 14 years.
- [P] Eq. 1 (p. 1): "a change in the gravitational potential at the location of a clock, according to
  various alternatives to general relativity, causes a fractional frequency shift
  `Delta f / f = (1 + beta) Delta Phi / c^2`", with `Delta Phi` the change of gravitational potential;
  `beta` measures the violation of local position invariance and is zero in general relativity. The
  eccentricity of Earth's orbit, `e = 0.0167`, supplies the variation of the Earth-Sun distance.
- [P] Fig. 1 caption (p. 2): the Earth is an "Einstein elevator" in free fall in the Sun's field with an
  acceleration `g_sun ~ 0.006 m s^-2`; the clocks on Earth are local, so local position invariance needs to hold
  only locally, and the solar redshift between two clocks at different places on Earth cancels in general relativity
  through free fall.
- [P] Eq. 2 (p. 2): the non-gravitational difference between two clock types is
  `Delta f/f|_H - Delta f/f|_Cs = beta Delta Phi / c^2`, with `beta = beta_H - beta_Cs`.
- [P] Eq. 3 (p. 2): `beta|_(H-Cs) = (2.24 +- 2.48) x 10^-7`, "an improvement in the uncertainty in beta by
  more than a factor of five" over the authors' 2007 study with H and Cs. The Jupiter potential changes the
  third significant digit, by of the order of a percent.
- [P] Data (pp. 2-3): the eight cesium fountains are IEN-CsF1, NIST-F1, PTB-CsF1 and -CsF2, NPL-CsF1 and
  -CsF2 and SYRTE-CsFO1 and -CsFO2; the four NIST hydrogen masers are S2 to S5; Fig. 2 spans MJD 51508
  (11 November 1999) to MJD 56959 (29 October 2014).
- [P] Eqs. 4 to 7 (p. 3): `dln(f_A/f_B) = DeltaK_alpha dln(alpha) + DeltaK_q dln(X_q)`, with `alpha` the
  fine-structure constant and `X_q = m_q/Lambda_QCD`; `dln(f_H/f_Cs) = beta Delta Phi / c^2`;
  `delta alpha/alpha = k_alpha delta(Phi/c^2)` and `delta X_q/X_q = k_q delta(Phi/c^2)`; and
  `beta|_(H-Cs) = DeltaK_alpha k_alpha + DeltaK_q k_q`.

## Mapping to this repository

- [I] Size: the Earth-Sun potential at 1 AU is `G M_sun / (a c^2) = 9.87 x 10^-9`, and the eccentricity of
  0.0167 makes its annual variation `1.6 x 10^-10`. With `beta = 2.2 x 10^-7` the coupling shifts a
  fractional frequency by `3.7 x 10^-17`, and by at most `7.8 x 10^-17` at the upper edge of the
  quoted interval. The repository's Heron r2 calibration moves and Tuna-17 readout shifts
  ([ibm_heron_platform.md](../ibm_heron_platform.md), [tuna-17.md](../quantum_inspire/tuna-17.md)) are order-one
  fractions, 16 orders larger.
- [I] Signature: a violation of local position invariance in the repository's records would appear as a
  line at one cycle per year, in phase with the Earth-Sun distance, that is
  common to all devices of one atomic species; a 24 h or sidereal line is excluded.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The note transcribes the abstract, the introduction, Eqs. 1 to 7 and the figure captions. The Methods
(PDF pp. 4-6) were not read, and the interpretation lines are order-of-magnitude arguments.
