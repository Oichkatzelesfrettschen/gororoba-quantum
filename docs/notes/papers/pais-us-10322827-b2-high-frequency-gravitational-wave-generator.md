# Pais, US 10,322,827 B2 -- High frequency gravitational wave generator

## Source copy and license

The [official patent PDF](https://patentimages.storage.googleapis.com/21/5a/a6/c9ad768eb3a443/US10322827.pdf) stays
external to the published library. Its reading copy is `docs/local_source_cache/pais-us-10322827-b2.pdf`, and the
owner's private documents repository receives the same bytes. The patent names the United States Department of the
Navy as assignee (PDF p. 1, item 73). The [USPTO statement](https://www.uspto.gov/terms-use-uspto-websites) that
patent text and drawings are typically not subject to copyright, and the registry's decision not to rehost on a
US-only statement, are recorded in
[the US 10,135,366 B2 note](pais-us-10135366-b2-electromagnetic-field-generator.md); this PDF carries no copyright
or mask-work notice either.

Tag convention: [P] marks a patent statement with its locator (column and line); [I] marks repository
interpretation; [E] marks a number recomputed here.

## Citation and provenance

- Inventor: Salvatore Cezar Pais. Application 15/431,823, filed 2017-02-14; granted 2019-06-18. 5 claims.
  [P, PDF p. 1]
- Source URL: the patentimages PDF above, linked from `https://patents.google.com/patent/US10322827B2/en`.
  9 PDF pages (front matter pp. 1-2, drawings pp. 3-4, description and claims pp. 5-9 as columns 1-10).
  891879 bytes, retrieved 2026-10-26T01:39:10Z.
- SHA-256: `f45b488099eebd2172d85a6b82e739b1696e55c847b5a4846d458a259aa13238`
- Reading scope: description from col. 3 through the claims, equations and claims read in full from rendered
  pages; cols. 1-2 and the drawings not read.

## Equations and numbers

- [P] Eq. 1, col. 5, ll. 34-36: `S_max = f_G (sigma^2/eps0) [(R_v nu^2) t_op]`, "the maximum EM energy flux (time
  rate of change of EM energy transfer per unit surface area)" of an electrically charged system in accelerated
  vibration or spin; `f_G` equals 1 for a disc, `R_v` is the vibration amplitude, `nu` the vibration angular
  frequency in Hz, `t_op` the time at maximum acceleration. This form has no `gamma^2` factor.
- [P] Eq. 2, col. 5, ll. 52-54: for a non-zero time differential of acceleration,
  `S_max = f_G (sigma^2/eps0) [(R_v nu^3) t_op^2]`. Col. 5, ll. 56-65: with the controllable parameters of unit
  order, "energy flux values on the order of 10^33 W/m^2" with "low end microwave frequencies on the order of
  10^7 Hz".
- [P] Eq. 3, col. 6, ll. 10-11: `E_T = m R_v^2 Omega^2 [exp(2 Omega t)]`, the total energy of a vibrating mass given
  a "momentum/energy-pumping (negative damping) term {bv}" (col. 6, ll. 1-9), `Omega` the angular frequency of
  vibration, valid under `(b/2m) >> Omega_0`. The patent concludes "exponential growth in energy flux with
  accelerating vibration" (col. 6, ll. 13-16).
- [P] Eq. 4, col. 6, ll. 24-26: `P_GW(out) = [(4 pi G/c^4) B_0^2 L^2] P_EM(in)`, obtained "by combining equations
  3-13 and 3-14 on page 10 of the JASON report" (col. 6, ll. 17-23); `B_0` is the static magnetic flux density over
  the distance `L`. The patent adds that "a simple dimensional analysis shows that there is a factor missing in
  Equation 4, as written in the JASON Report, equal to the inverse of the magnetic permeability of free space,
  namely a factor on the order of 10^6" (col. 6, ll. 33-38).
- [P] Inputs and outputs, col. 6, ll. 39-49: a "high frequency/high intensity electromagnetic generator" can give
  "power levels on the order of 10^10 watts, for an input EM energy flux on the order of 10^33 W/m^2", with `B_0`
  "on the order of 10^10 Tesla"; and "10^35 gravitons/sec production rates" from equation 3-25 of the JASON
  report.
- [P] Col. 6, ll. 58-62: the energy "capable of annihilating a planet such as the Earth is on the order of
  10^32 Joules", `E_annihil = (3/5)(G M_P^2 / R_P)`.
- [P] The JASON discussion, col. 3, ll. 26-47: a report "written for the Office of the Director of National
  Intelligence (Defense Intelligence Agency), prepared by the MITRE Corporation in October 2008" concludes that
  high-frequency gravitational waves are no national-security concern; the patent states that the report
  "considers relatively low EM energy fluxes" and that its conclusions "must be revisited, are incorrect". The
  references list (PDF p. 2) names Eardley et al., "High Frequency Gravitational Waves", October 2008.
- [P] The description reports no measurement. It also describes room-temperature superconducting wiring
  (col. 5, ll. 24-27 and FIG. 3).

## Claim 1 (PDF p. 9, col. 9, l. 2 to col. 10, l. 7)

[P] "A high frequency gravitational wave generator comprising: a gas-filled shell, the gas-filled shell comprising
of microwave emitters, the gas filled shell has an outer shell surface and an inner shell surface, the outer shell
surface is able to be electrically charged by an electrical source and is able to be vibrated by the microwave
emitters, such that it generates a first electromagnetic field; at least two sound generators for generating
sound, the at least two sound generators disposed within the gas-filled shell; two acoustic vibration resonant
gas-filled cavities for propagation of sound created by the at least two sound generators, the two acoustic
vibration resonant gas-filled cavities are disposed within the gas-filled shell and each resonant gas-filled
cavity has one cavity surface that can be electrically charged, the acoustic energy from the at least two sound
generators causing each of the electrically charged cavity surfaces to vibrate such that a second
electromagnetic field is generated; the two acoustic vibration resonant gas-filled cavities being able to counter
spin relative to each other to provide stability, propagating gravitational field fluctuations are generated when
the second electromagnetic field propagates through the first electromagnetic field." Claims 2 to 5 add
room-temperature superconducting wiring, an inert-gas fill, xenon and wedge-shaped cavities.

## Relation to the topic note and the web-source row

[I] The web-source row's Eq. 2 (`nu^3 t_op^2`), Eq. 3, Eq. 4, the 1e33 W/m^2 input, the 1e10 T field, the 1e10 W
output and the omitted `1/mu0` statement match the locators above. The
[topic note](../topics/pais-claims-falsification.md) writes the vibrating case as `R_v nu^2 t_op`: that is this
patent's Eq. 1, and the second equation of US 10,135,366 B2 with its `gamma^2` factor removed.
