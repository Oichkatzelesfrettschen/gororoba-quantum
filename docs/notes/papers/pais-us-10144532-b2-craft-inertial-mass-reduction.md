# Pais, US 10,144,532 B2 -- Craft using an inertial mass reduction device

## Source copy and license

The [official patent PDF](https://patentimages.storage.googleapis.com/de/4c/43/62c585ccc936cc/US10144532.pdf) stays
external to the published library. Its reading copy is `docs/local_source_cache/pais-us-10144532-b2.pdf`, and
the owner's private documents repository receives the same bytes. The patent names the Secretary of the Navy's
United States of America as assignee (PDF p. 1, item 73) and carries the same government-interest statement as
[US 10,135,366 B2](pais-us-10135366-b2-electromagnetic-field-generator.md) (col. 1, ll. 4-9). The
[USPTO statement](https://www.uspto.gov/terms-use-uspto-websites) that patent text and drawings are typically not
subject to copyright, and the registry's decision not to rehost on a US-only statement, are recorded in that note;
this PDF carries no copyright or mask-work notice either.

Tag convention: [P] marks a patent statement with its locator (column and line); [I] marks repository
interpretation; [E] marks a number recomputed here.

## Citation and provenance

- Inventor: Salvatore Cezar Pais. Application 15/141,270, filed 2016-04-28; granted 2018-12-04. 4 claims.
  [P, PDF p. 1]
- Source URL: the patentimages PDF above, linked from `https://patents.google.com/patent/US10144532B2/en`.
  6 PDF pages (front page p. 1, drawings p. 2, description and claims pp. 3-6 as columns 1-8). 810530 bytes,
  retrieved 2026-10-26T01:39:09Z.
- SHA-256: `0d7e5472d871d5e7465041c19f7c8b05f5f2703eaa14726698dc7a00bfb7abf5`
- Reading scope: description, equations and claims read in full from rendered pages; drawings not read.

## Equations and numbers

- [P] Mechanism, col. 2, ll. 10-21: inertial and gravitational mass reduction "by an abrupt perturbation of the
  non-linear background of local spacetime (the local vacuum energy state)", driven by "the negative pressure
  (hence repulsive gravity) exhibited by the polarized local vacuum energy state".
- [P] Eq. 1, col. 2, ll. 41-44: `S_max = f_G (sigma^2/eps0) [R_r omega + R_v nu + v_R]`, introduced as the Poynting
  vector magnitude "in non-relativistic form (accounting for all three modes of motion)"; `f_G` equals 1 for a
  disc; `v_R` is the curvilinear translation speed acquired through a propulsive unit. This equation carries no
  `gamma^2` factor.
- [P] Example, col. 2, ll. 57-65 and col. 3, ll. 1-3: sigma = 50,000 C/m^2, disc radius 2 m, 30,000 RPM gives about
  1e24 W/m^2; vibration at 1e9 to 1e18 Hz gives 1e24 to 1e28 W/m^2. [E] `f_G` = 1 gives 1.77e24 W/m^2 for the
  rotation-only case.
- [P] Eq. 2, col. 3, ll. 8-10: `S_max = f_G (sigma^2/eps0) [(R_v nu^2) t_op]`. Col. 3, ll. 22-27: a microwave
  frequency of 1e11 Hz, sigma of 1 C/m^2 and "an operational time on the order of the inverse of the vibrational
  amplitude" give 1e33 W/m^2. [E] `sigma^2/eps0` = 1.13e11 W s/m^2 times `nu^2` = 1e22 gives 1.13e33 with
  `R_v t_op` set numerically to 1 (metres times seconds).
- [P] Eq. 3, col. 3, ll. 41-43: `2 gamma (dm/dt)_pp c^2 = S_max A_S`, the pair-production mass rate for energy
  flux through area `A_S`. Preceding it, col. 3, ll. 36-40: "Schwinger value of the electric field (E) on the
  order of 1e18 V/m". Col. 4, ll. 1-5: the pair-production frequency `nu_v` "on the order of 1e22 Hertz", with
  annihilation gamma rays at 1e19 Hz and above.
- [P] Eq. 4, col. 3, ll. 60-63: `S_max/c = [h* nu_v^4]/(8 pi^2 c^3)`, from the boundary condition that the
  artificial field's energy density equals the local zero-point density, "on the order of 1e-15 Joules/cm^3"
  (col. 3, ll. 56-58), with `h*` Planck's constant over 2 pi.
- [P] Eq. 5, col. 5, ll. 36-37: `Delta W_R(omega) = -2 x 10^-10 M r_eq omega` kg m s^-2, "the Hayasaka et al.
  expression" for gyro weight reduction (Hayasaka and Takeuchi, Phys. Rev. Lett., December 1989, col. 5,
  ll. 9-13). The patent calls the later null results "flawed" in their ability "to entirely duplicate the
  Hayasaka et al. experimental procedure" (col. 5, ll. 13-20) and reads the non-zero intercept
  (2e-10 per second) as of the order of the Fokker-Planck electron-proton thermal equilibrium rate for about
  40 hydrogen atoms per cubic meter (col. 5, ll. 21-30).
- [P] Eq. 6, col. 5, ll. 49-50: `Delta W_R(nu) = -f_ep M A_v nu` kg m s^-2 by "a simple dimensional analysis" for a
  vibrating rotor, `f_ep` the Fokker-Planck rate and `A_v` the vibration amplitude.
- [P] Gertsenshtein effect named as a possible mechanism, col. 5, ll. 4-6 (production of high-frequency
  gravitational waves by high-frequency electromagnetic radiation).
- [P] Cavity Q-factor 1e4 to 1e9 for a metal or superconducting outer wall, col. 7, ll. 15-20.
- [P] The description reports no measurement of any mass change.

## Claim 1 (PDF p. 6, col. 8, ll. 33-47)

[P] "A craft using an inertial mass reduction device comprising: an inner resonant cavity wall; an outer resonant
cavity wall, the inner resonant cavity wall and the outer resonant cavity wall forming a resonant cavity; and,
microwave emitters such that the microwave emitters create high frequency electromagnetic waves throughout the
resonant cavity causing the outer resonant cavity wall to vibrate in an accelerated mode and create a local
polarized vacuum outside the outer resonant cavity wall." Claims 2 to 4 add a noble-gas fill, an electrically
charged outer wall and accelerated axial rotation.

## Relation to the topic note and the web-source row

[I] The [web-source note](pais-patent-web-sources.md) row for this patent says it carries "the same Eq. 1 and 2"
as the field-generator patent. Its Eq. 1 and Eq. 2 omit `gamma^2` (Eq. 1 is stated as the non-relativistic form),
so the equations are the same except for that factor. Eq. 3 to Eq. 5 match the row and the
[topic note](../topics/pais-claims-falsification.md): the pair-production balance, the zero-point equation and
the Hayasaka weight law.
