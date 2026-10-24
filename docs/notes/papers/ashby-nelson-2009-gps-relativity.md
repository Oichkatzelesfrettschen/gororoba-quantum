# Ashby and Nelson 2009 -- The global positioning system, relativity, and extraterrestrial navigation (IAU Symposium 261)

## Source copy and license

The [author PDF](https://tf.nist.gov/general/pdf/2444.pdf) from the NIST Time and Frequency Division
publication list remains external to the published library. Its optional personal reading copy is
`docs/local_source_cache/ashby-nelson-2009-gps-relativity.pdf`. PDF page 1 prints the line "c 2009
International Astronomical Union" and a placeholder DOI ("00.0000/X000000000000000X"), so the file is the
authors' typeset manuscript for the IAU Symposium No. 261 proceedings. The inspected evidence supplies
no repository rehosting grant, and [SOURCES.json](../../SOURCES.json) records the license identifier
`LicenseRef-IAU-copyright-notice`, the SHA-256 and the reading scope.

Tag convention: [P] marks paper statements; [I] marks repository interpretation.

## Citation and provenance

- Authors: Neil Ashby (University of Colorado Boulder, NIST affiliate); Robert A. Nelson (Satellite
  Engineering Research Corporation).
- Venue: Proceedings of the International Astronomical Union 5(S261), 22-30 (2009), IAU Symposium No.
  261, "Relativity in Fundamental Astronomy", eds. P. K. Seidelmann, S. Klioner and M. Soffel, DOI
  10.1017/S174392130999010X (Crossref receipt below).
- Source URL: https://tf.nist.gov/general/pdf/2444.pdf, 9 pages, retrieved 2026-10-24.
- SHA-256: `62683fbc2d741ed86688253b01c2c595d3288068ab489d6cdaf5513dd154a909`
- Reading scope: the abstract, Section 1 (Eq. 1.1), Section 6 (solar and lunar tidal potentials, Eqs.
  6.1 to 6.3, PDF pp. 5-6) and Section 7 (the barycentric coordinate time transformation, Eqs. 7.5 to
  7.10, PDF pp. 8-9). The Mars-navigation sections and the Earth-quadrupole correction (Eq. 7.4) were
  not read in detail.

| Source | URL | SHA-256 of retrieved bytes | Read for |
|---|---|---|---|
| Crossref record of the version of record | https://api.crossref.org/works/10.1017/S174392130999010X | `dd286cabd85af844c25ac34281023273b3cd48023210adb86f84a0d7d3936367` | Bibliographic identity |

## Transcribed statements

Read from the PDF above; page numbers are PDF page indices.

- [P] Section 1 (p. 1): the Earth and its satellites are in free fall, and by the principle of equivalence
  the field of external bodies is cancelled over a region near the Earth's center of mass; in the local
  freely falling frame external bodies "can be ignored approximately". Eq. 1.1 is the GPS metric
  `ds^2 = -(1 + 2V/c^2)(c dt)^2 + (1 - 2V/c^2)(dx^2 + dy^2 + dz^2)`, which neglects external bodies and
  keeps the Earth's monopole and quadrupole potential.
- [P] Section 6 (pp. 5-6), "Solar and lunar tidal potentials": at the origin of a locally inertial,
  freely falling frame (the ECI frame), the field strength of external bodies is cancelled by the
  induced field of the acceleration. A time transformation with the resynchronization term `v . r / c^2`
  (Eq. 6.1, `v` the velocity of the frame origin and `r` the displacement of the observation point)
  contributes `-(1 + d(v . r / c^2)/dt)^2 = -2 a . r / c^2 + ...` to `g_00` (Eq. 6.2), the external
  potential contributes `-2 grad V . r / c^2`, and the two cancel, `-(2/c^2)(a + grad V) . r = 0`
  (Eq. 6.3), because in free fall `a = -grad V`.
- [P] Section 6 (p. 6): "The cancellation does not arise from second-order Doppler effects as some have
  claimed. The first terms that contribute are tidal terms, second derivatives of the external potential
  evaluated at the origin of the local frame." The net fractional frequency shift of orbiting GPS clocks
  from the moon has an amplitude of only `7 x 10^-16`, and the sun contributes about half that amount.
- [P] Section 7 (pp. 8-9): the elapsed Barycentric Coordinate Time on a moving clock is
  `Delta t_TCB = integral d tau (1 - V(r)/c^2 + (1/2) v^2/c^2)` (Eq. 7.5). Splitting the position and the
  potential into Earth-centered and external parts (Eqs. 7.6, 7.7) gives Eq. 7.8, whose last term is
  the relativity of simultaneity of the ECI frame; "Only tidal terms from the external potential
  survive, because of the principle of equivalence." The principal terms of the first integral
  (Eq. 7.9) are `3 G M_sun / (2 c^2 a_earth) + (2 sqrt(G M_sun a_earth) / c^2) e_earth sin(E_earth)`, and the
  second integral is the geocentric coordinate time `t_TCG = (1 + L_G) t_TT` (Eq. 7.10).

## Mapping to this repository

- [I] Size: a laboratory clock comparison on Earth sees the solar potential only through tidal terms, with
  the order of `7 x 10^-16` for the moon and half that for the sun on orbiting GPS clocks; the paper
  gives amplitudes for orbiting GPS clocks only. A calibration cycle of IBM Heron r2 (hourly,
  [ibm_heron_platform.md](../ibm_heron_platform.md)) or a Belenos transmittance move of 2.89 % to 6.06 %
  ([platform-specifications.md](../quandela/platform-specifications.md)) is more than 15 orders larger,
  so the solar gravitational potential contributes nothing to those records.
- [I] Signature: the tidal terms follow the lunar and solar orbital phases and the annual eccentricity
  term of Eq. 7.9; a record that shows them needs a frequency resolution near `10^-16`, and a 24 h or
  sidereal line without a tidal partner has a different source.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] The note covers the free-fall cancellation and the tidal terms. The PDF is an author manuscript of the
proceedings paper, and its pagination differs from the published one. The Mars-navigation sections were
not read in detail.
