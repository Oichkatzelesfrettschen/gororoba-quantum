# Pais, US 10,135,366 B2 -- Electromagnetic field generator and method to generate an electromagnetic field

## Source copy and license

The [official patent PDF](https://patentimages.storage.googleapis.com/5d/18/ae/8b518ca57f8b27/US10135366.pdf) stays
external to the published library. Its reading copy is `docs/local_source_cache/pais-us-10135366-b2.pdf`, and the
owner's private documents repository receives the same bytes. The patent names "The United States of America as
represented by the Secretary of the Navy" as assignee (PDF p. 1, item 73) and carries a government-interest
statement (col. 1, ll. 4-10). The USPTO states that, "subject to limited exceptions reflected in 37 CFR 1.71(d) &
(e) and 1.84(s), the text and drawings of a patent are typically not subject to copyright restrictions"
([USPTO terms of use](https://www.uspto.gov/terms-use-uspto-websites), retrieved 2026-10-26, sha256
`ab095d05c48cb65cb89542db49503c8f8675d72ae5c004b13b542964754c2740`). The PDF carries no copyright or mask-work
notice under 37 CFR 1.71(d) or (e) (text layer searched). Those statements concern US copyright and grant no
worldwide rehosting right, the position that [SOURCES.json](../../SOURCES.json) already takes for a NIST work, so
the registry records `LicenseRef-US-Government-work-patent-document` with an external-only decision, the SHA-256
and the reading scope.

Tag convention: [P] marks a patent statement with its locator (column and line of the printed patent, or PDF
page); [I] marks repository interpretation; [E] marks a number recomputed here. Column and line numbers come from
the margin line numbers of the rendered pages.

## Citation and provenance

- Inventor: Salvatore Pais, Leonardtown, MD. Application 14/807,943, filed 2015-07-24; granted 2018-11-20;
  12 claims, 2 drawing sheets. [P, PDF p. 1]
- Source URL: the patentimages PDF above, linked from `https://patents.google.com/patent/US10135366B2/en`
  (`citation_pdf_url`). 9 PDF pages (front matter pp. 1-2, drawings pp. 3-4, description and claims pp. 5-9 as
  columns 1-10). 1061436 bytes, retrieved 2026-10-26T01:39:07Z.
- SHA-256: `f40c612ea1ef94cc8c5ab51434137a86bce0b371b7458a548fc9c9e1349e341d`
- Reading scope: front page, description, equations and claims read in full; equations read from rendered
  pages, not from the text layer; drawings not read.

## Equations and numbers

- [P] Eq. 1, col. 6, ll. 16-17: `S_max = f_G gamma^2 (sigma^2/eps0) [R_r omega + R_v nu + v_R]`, "the magnitude of the
  Poynting vector, and in relativistic form". Definitions, col. 6, ll. 17-27: `f_G` the geometric shape factor
  (2/3 spherical shell, 1/6 hemispherical shell, 1 disc), `gamma` the relativistic "stretch" factor, `sigma` the
  surface charge density, `R_r` the radius of rotation, `omega` the rotation frequency in rad/s, `R_v` the
  vibration amplitude, `nu` the vibration frequency in Hz, `v_R` the curvilinear translation speed.
- [P] Worked example, col. 6, ll. 27-34: rotation only, sigma = 50,000 C/m^2, sphere radius 2 m, 30,000 RPM,
  gives `S_max` = 1e24 W/m^2 "(this value does not account for any QVP interactions which would amplify it)".
  Col. 6, ll. 34-40: coupled to vibration at 1e9 to 1e18 Hz, "values in the range 1e24 to 1e28 Watts/m^2 (and
  beyond)". [E] Eq. 1 with gamma = 1, f_G = 2/3, R_r = 2 m and omega = 2 pi x 500 rad/s gives 1.18e24 W/m^2.
- [P] Eq. 2, col. 6, ll. 49-51: `S_max = f_G gamma^2 (sigma^2/eps0) [(R_v nu^2) t_op]`, the case of "an accelerating
  angular frequency of vibration (a_max = R_v nu^2), neglecting rotation and curvilinear translation", with `t_op`
  "the operational time for which the charged electrical system is accelerating".
- [P] Eq. 3, col. 7, ll. 9-11: `(M_A + M_KI) Delta v = k (M_KI)(u_KI)`, the momentum balance of a kinetic impactor
  on an asteroid. Col. 7, ll. 5-19: M_A of order 1e10 kg (Apophis), spacecraft M_KI of order 1e3 kg, u_KI 10 km/s,
  `k` = 1, `Delta v` = 0.001 m/s. Col. 7, ll. 19-26: replacing the right-hand side by `(S_max/c^2) Vol_S` with
  `S_max` = 1e24 W/m^2 and `Vol_S` = 1e3 m^3 gives 1 m/s, "a three orders of magnitude improvement".
- [P] Field limits, col. 9, ll. 14-18: the field in dry air "must be kept below 3x10^6 V/m (in the vacuum of space
  this value climbs to 10^9 V/m)". Capacitance, col. 9, ll. 19-23: `C = 4 pi eps0 eps_r R`, with `eps_r` of the
  epoxy-ceramic "C-ply" material "on the order of 10^18".
- [P] Mossbauer amplification by Co-57 or Fe-57 doping and a resonant-cavity oscillating source, col. 9, ll. 38-52.
- [P] The description reports no measurement; its figures are computed from Eq. 1 and Eq. 2.

## Claim 1 (PDF p. 9, col. 10, ll. 10-33)

[P] "A high energy electromagnetic field generator, comprising: a shell, the shell having embedded
polycrystalline ferroelectric ceramic material, the material being polarized such that the ceramic material
exhibits strong Piezoelectric Effect properties thus inducing high frequency vibrations; an electrostatic
generator for charging up the shell, the electrostatic generator disposed within the shell; a power plant to
generate thermal power; a thermoelectric generator to convert the thermal power generated by the power plant to
electrical energy; an electric motor powered by the electrical energy generated by the thermoelectric generator,
the electric motor supplying input voltage such that the shell spins at high angular speeds, vibrates at high
frequencies, and generates an electromagnetic field." Claims 2 to 5 narrow the shell (spherical, two
electrostatic generators, embedded radioactive elements); claim 6 and 7 the hemispherical shell; claims 9 to 11
the disc; claim 12 is the method.

## Relation to the topic note

[I] The [topic note](../topics/pais-claims-falsification.md) states Eq. 1 with `gamma^2` and the 1e24 W/m^2
example, the 1e9 V/m vacuum limit and Eq. 2; each matches the locators above. The topic note's Eq. 2 omits the
`gamma^2` factor that this patent prints in its Eq. 2.
