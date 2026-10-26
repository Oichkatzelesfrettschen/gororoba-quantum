# Pais, US 2019/0058105 A1 -- Piezoelectricity-induced room temperature superconductor

## Source copy and license

The [official application publication PDF](https://patentimages.storage.googleapis.com/45/e7/c7/8b24799e606f93/US20190058105A1.pdf)
stays external to the published library. Its reading copy is
`docs/local_source_cache/pais-us-2019-0058105-a1.pdf`, and the owner's private documents repository receives the
same bytes. The publication names the United States of America as represented by the Secretary of the Navy as
assignee (PDF p. 1, item 73). The [USPTO statement](https://www.uspto.gov/terms-use-uspto-websites) that patent
text and drawings are typically not subject to copyright, and the registry's decision not to rehost on a US-only
statement, are recorded in [the US 10,135,366 B2 note](pais-us-10135366-b2-electromagnetic-field-generator.md);
this PDF carries no copyright or mask-work notice either.

Tag convention: [P] marks a statement with its locator (paragraph number `[00xx]`, or PDF page); [I] marks
repository interpretation; [E] marks a number recomputed here.

## Citation and provenance

- Inventor: Salvatore Cezar Pais, Callaway, MD. Application 15/678,672, filed 2017-08-16; published 2019-02-21;
  8 claims. [P, PDF p. 1 and p. 7]
- Source URL: the patentimages PDF above, linked from `https://patents.google.com/patent/US20190058105A1/en`.
  7 PDF pages (front page p. 1, drawings p. 2, description and claims pp. 3-7). 872542 bytes, retrieved
  2026-10-26T01:39:10Z.
- SHA-256: `a3cd3f7a6aa52205d0e6983e428f4a64cde0a6a390214f7d50cb975ee288cb4d`
- Reading scope: paragraphs [0015] to [0037] and the claims read from rendered pages; paragraphs [0001] to
  [0014] and the drawings not read.

## Equations and numbers

- [P] Mechanism, [0016] (PDF pp. 3-4): "independent of physical mechanism, the key to observed superconductivity
  is the strong electron-lattice (phonon) coupling"; a composite wire "can become superconductive (SC) at room
  temperature, if you make it abruptly vibrate, while running a pulsed current through it, just like 'plucking'
  a guitar string intermittently".
- [P] Wire, [0017] (PDF p. 4): an insulator core (Teflon or another non-conductive polymer) with a thin coating of a
  normal metal (aluminum) or poor metal (PZT ceramic), the coating of a thickness of the order of the London
  penetration depth, in an externally applied magnetic field.
- [P] Eq. 1, [0018] (PDF p. 4): `lambda_L = [m_s / (mu0 n_s q_s^2)]^(1/2)`. [0019]: `n_s` "on the order of
  10^20/cm^3", so the coating thickness "is on the order of micron(s)". [E] `n_s` = 1e26 m^-3 gives
  `lambda_L` = 0.53 um.
- [P] [0020] (PDF p. 4): the wire is vibrated by a Teflon pick, an electromagnetic plucking coil, or a PZT coating
  driven by an electrical potential; "the mechanically-plucked Al-coated composite wire may fail the Meissner effect
  test"; micrometer-size PZT films "can excite high vibration frequencies, exceeding 100 MHz".
- [P] [0021] (PDF p. 4): the three superconductor characteristics named are perfect diamagnetism (Meissner
  effect), zero electrical resistance and macroscopic quantum coherence.
- [P] Eq. 2, [0022] (PDF p. 4): `[(mu0 I / 2 pi R) + (mu0 sigma A_v omega_v^2 Delta t)] >= (B_E)_MAX`, the claimed
  condition for the Meissner effect, with `I` the time-independent wire current, `R` the wire radius, `sigma` the
  wire surface charge density, `A_v` the accelerated vibration amplitude, `omega_v` its frequency, `Delta t` the
  vibration interval and `(B_E)_MAX` the maximum induction of the external field. The patent notes that the
  expression "is not a function of temperature" and that `omega_v` enters as a second power (PDF p. 5).
- [P] [0023]: zero resistance follows from `dB/dt = 0` in the insulator core by the London-equation argument with
  Faraday's law and Ohm's law. [0024]: electron-phonon coupling creates Cooper pairs. [0028] cites Mitrano et
  al., Nature 530, 461-464 (2016), on light-induced superconductivity in K3C60.
- [P] Eq. 3, [0029] (PDF p. 5): `alpha = e / (Phi_0 eps0 c)`, with `Phi_0` the quantum of magnetic flux, and
  [0030] (PDF p. 6) "the term `Phi_0` may be written as `h*/(2e)`, where `h*` is Planck's constant divided by
  2 pi". [E] With `Phi_0 = h/(2e)` the printed right-hand side equals 4 alpha, and with `Phi_0 = hbar/(2e)`, as the
  text defines it, 25.13 alpha (8 pi alpha); neither equals alpha.
- [P] [0035] (PDF p. 6-7): a two-electron lattice model in which the pair forms at energies "much higher than
  Cooper pair formation (>10^-3 eV)". [E] `k_B T` at 300 K is 25.9 meV, larger than that figure.
- [P] The description gives no resistance, magnetization, current or temperature measurement. The experiments it
  names ([0020], [0028]) are described as set-ups to consider or replacements to try.

## Claim 1 (PDF p. 7)

[P] "A room temperature superconductor comprising: a wire comprising an insulator core and a metal coating, the
metal coating disposed around the insulator core, the metal coating deposited on the core, and, when a pulsed
current is passed through the wire while the wire is vibrated, room temperature superconductivity is induced."
Claim 2 is the independent PZT-coating form (poled PZT coating, pulsed current, vibration); claim 3 adds vacuum
evaporation of the PZT coating, claims 4 and 8 a coating thickness of the order of the London penetration depth,
claim 5 a coating material in which the piezoelectric effect can be induced, claim 6 an electromagnetic coil
around the wire and claim 7 an aluminum coating.

## Relation to the topic note

[I] The [topic note](../topics/pais-claims-falsification.md) records that the filing describes no resistance or
magnetization measurement; the locators above confirm it. The note leaves Eq. 1 to Eq. 3 undecomposed.
