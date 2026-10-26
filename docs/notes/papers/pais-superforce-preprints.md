# Pais, the Superforce preprints: statement-by-statement decomposition

Two OSF preprints by Salvatore Cezar Pais carry the Superforce claim.

| Version | OSF id | Published | Pages | License | Retained bytes (sha256) |
|---|---|---|---|---|---|
| "On the Existence of the Superforce -- the possible fundamental Force of Unification" | yh84c_v1, DOI 10.31219/osf.io/yh84c | 2023-04-11 | 4 | none listed (all rights reserved) | `920d2625e0c940b47c9701dfd020efdeaabfb649e0d2cfdf9922f5d738efa3eb`, reading copy outside this repository |
| "SUPERFORCE -- the Fundamental Force of Unification" | 9kebt_v1 | 2023-07-24 | 3 | CC0 1.0 | `8ea4fecbd504b2dfa73941f856befe5bee23b1ebffa8a6a8bbd19e185a675176` |

The registry records, retrieval times and the falsifier sources are in
[pais-superforce-sources.md](pais-superforce-sources.md). Both versions were read in full. The July version drops
the April version's Planck quotation, the "Mother of All Forces" name, the proton-pressure argument, the
multiverse paragraph and the acknowledgment, and adds Eq. 1, the cosmic energy gradient. The 2024 APS March
Meeting listing "The Superforce -- a Path to Quantum Gravity?" (session LL05) carries the same abstract; its page
answered a browser challenge and was not read.

[P] marks a statement of the preprints, [I] a deduction here, and [E] a value
[scripts/pais_superforce_bounds.py](../../../scripts/pais_superforce_bounds.py) computes from CODATA constants and the
cited measurements. The script raises when a stated inequality fails, and
[its test](../../../tests/scripts/test_pais_superforce_bounds.py) runs in the `tests` check.

## Sec. II: the inverse Einstein coupling as a force

- [P] The field equations couple stress-energy to curvature by "a scalar factor, on the order of (G/c^4)". Its
  inverse c^4/G has units of energy per length, hence of force, and is named the Superforce (SF). The preprints
  write G_uv ~ (1/SF) T_uv.
- [E] c^4/G = 1.2103e44 N. The coupling the field equations carry is 8 pi G/c^4, whose inverse is 4.815e42 N, and
  Gibbons' conjectured maximal tension of classical GR is c^4/(4G) = 3.026e43 N (Found. Phys. 32, 1891 (2002),
  abstract).
- [I] A dimensional constant in a field equation is a conversion between curvature and stress-energy, not a force
  acting on anything. Gibbons' reading of the same constant is a ceiling on any tension GR admits. The Superforce
  is 4 times that ceiling and is said to act at every point, so the preprints invert what the constant expresses.
- [P] c^4/G "does not contain h-bar, therefore it can relate to ... a Macroscopic Quantum Phenomenon". [I] A
  quantity that survives the limit hbar -> 0 is classical by that fact. Its independence of hbar is the reason it
  appears in classical GR, not evidence of a quantum role.

## Sec. III: "strong force equals gravity equals c^4/G at the Planck scale"

- [P] F_SN/F_EM = 1/alpha. Then F_SN = (1/alpha) q^2/(4 pi eps0 L^2) with alpha = q^2/(4 pi eps0 hbar c) gives
  F_SN = c^4/G at L = L_P. Also F_G = G m_P^2/L_P^2 = c^4/G. "The strongest of the known forces equals the
  weakest ... this proves that the Superforce is indeed the Force of Unification."
- [I] The charge cancels: (1/alpha) F_EM = hbar c/L^2 for every q. The step is Coulomb's law with its coupling set
  to 1, and hbar c/L_P^2 = c^4/G is the definition of L_P. [E] The script confirms charge independence to 2e-16 for
  q = e, 2e and 137e.
- [I] G m_P^2 = hbar c is the definition of m_P, so F_G(L_P) = hbar c/L_P^2 is the same identity again. The two
  equalities are one equality written twice, and neither contains a strong-interaction input.
- [I] The premise F_SN/F_EM = 1/alpha is the statement alpha_s = 1. The measured strong coupling runs with scale:
  alpha_s(m_Z) = 0.1180 +- 0.0009 (PDG 2024 QCD review, Eq. 9.25), falling under the one-loop law of Eq. 9.3.
- [E] One-loop running with n_f = 5 below the top mass and 6 above it gives alpha_s(M_Pl) = 0.01906. Buttazzo et al.
  (JHEP 12 (2013) 089, Eq. 61c) give g3(M_Pl) = 0.4873 at three loops, so alpha_s(M_Pl) = 0.01890.
- [E] The strong force at the Planck length is therefore 0.0189 hbar c/L_P^2, which is c^4/G divided by 52.9. The
  unification the preprint "proves" fails by a factor of 53 against the measured coupling. Buttazzo et al. find the
  three gauge couplings "roughly equal in the vicinity of the Planck mass" at g = 0.49 to 0.62 (Eqs. 61a-c), that
  is alpha = g^2/(4 pi) = 0.019 to 0.030, none near the 1 the argument needs.

## Sec. IV: the Superforce "in the Schrodinger and Dirac equations"

- [P] Balancing the kinetic term against V gives V ~ hbar^2/(m L^2). Writing SF ~ V/L_R with L_R = L_P gives
  SF ~ c^4/G.
- [E] V/L = hbar^2/(2 m L^3) equals c^4/(2G) only when both the Planck mass and the Planck length are inserted. The
  equation supplies neither; it is G-free. An electron at its reduced Compton wavelength gives 8.8e-46 of c^4/G,
  and a proton at its charge radius 4.6e-41.
- [I] The Superforce is put into the Schrodinger equation by the substitution; nothing in the equation selects
  that substitution.

## Sec. V: "Engineering the Superforce"

- [P] With c^2 = 1/(mu0 mu eps0 eps) for light in a medium, "by engineering the electric permitivity and the
  magnetic permeability of a given medium, we can engineer the Superforce itself"; the military and commercial
  implications "are unbounded".
- [I] The c of the field equations is the invariant speed of the spacetime metric. The phase velocity c/n of light
  in a material is a property of the material's response, which enters T_uv and leaves the coupling unchanged.
- [E] The substitution would rescale the Einstein coupling inside water by n^4 = 3.26 at 400 nm (n = 1.3436,
  Daimon and Masumura 2007).
- [I] Taken literally, the substitution makes a body's active gravitational mass scale as n^4, so materials of
  different index would gravitate differently at order one. Two measurements bound composition-dependent active
  mass (Will, Living Rev. Relativ. 17, 4 (2014), Sec. 4.4.3):
  - Kreuzer (1968) found fluorine against bromine equal to 5e-5, with solid Teflon in a fluid (arXiv 2503.16198);
  - lunar laser ranging found aluminum against iron equal to 4e-12 (Eq. 72).
- [E] Surviving those bounds requires the compared materials to share n^4 within each bound, that is n to 1.25e-5
  and to 1e-12 respectively.
- [I] Under the substitution, c/n would also be the invariant speed in water, and no massive particle could
  exceed it. [E] An electron above 0.254 MeV of kinetic energy exceeds c/n in water at 400 nm and emits Cherenkov
  light, which is the signal water Cherenkov detectors record. The engineering premise is refuted by the existence
  of Cherenkov radiation and independently by both active-mass nulls.

## Sec. VI, April version: the proton pressure

- [P] Lattice QCD on the Summit supercomputer shows a pressure inside the proton "more than 10 to the power of 35,
  Pascals", which "exemplifies that the Superforce is representative of Real Physics".
- [E] 1e35 Pa is 1.66 times the proton's own energy density m_p c^2/V_p = 6.04e34 Pa, with V_p from the CODATA
  charge radius. It is 2.2e-79 of the Planck pressure c^7/(hbar G^2) = 4.6e113 Pa, and 1e35 Pa times pi r_p^2 is
  2.2e5 N, which is 1.8e-39 of c^4/G.
- [I] The pressure is set by QCD energy over the proton volume and contains no G. It is evidence of the strong
  interaction's scale, 39 decades below the Superforce, not of the Superforce. The measured proton pressure is
  Burkert, Elouadrhiri and Girod (Nature 557, 396 (2018)); the lattice calculation is Shanahan and Detmold (Phys.
  Rev. Lett. 122, 072003 (2019)). Both are metadata here.

## July version, Eq. 1: the cosmic energy gradient

- [P] SF ~ m_P c^2/L_P ~ M_U c^2/R_U, with SF ~ 1e44 ~ (1e53 x 1e17)/1e26. "This fact can not be a mere
  coincidence and shows that indeed the Superforce acts as the Bridge between General Relativity and Quantum
  Mechanics."
- [E] For the critical density rho_c = 3 H^2/(8 pi G) inside the Hubble radius R_H = c/H, M_H = c^3/(2 G H), so
  M_H c^2/R_H = c^4/(2G) exactly, for every H. The script checks this to 1e-12 at H0 = 50, 67.4 and 73 km/s/Mpc.
  At H0 = 67.4 km/s/Mpc, R_H = 1.37e26 m and M_H = 9.2e52 kg. Pais's rounded inputs give 0.74 of c^4/G.
- [I] Eq. 1 is the Friedmann equation of a spatially flat universe. Its "coincidence" is the measured curvature,
  Omega_K = 0.001 +- 0.002 (Planck 2018 VI abstract). It holds with no quantum input, so it cannot bridge GR and
  quantum mechanics.

## Sec. VI: matter creation, the superfluid vacuum and the Eridanus supervoid

- [P] "It is the Superforce that when acting locally on the SpaceTime Geometric Structure gives birth to Energy
  Density, hence generates Matter"; the cosmos "may" be a superfluid. In the April version only: the Eridanus
  supervoid may be a window into a universe whose Superforce acts in the opposite direction.
- [I] The first sentence restates G_uv = (8 pi G/c^4) T_uv with the coupling inverted. It predicts nothing the
  field equations do not already predict, so no measurement distinguishes it from GR. The supervoid and opposite
  Superforce are stated without an equation and admit no test here.

## What a quantum processor can and cannot test

- [I] Every claim above concerns G, the Planck scale or cosmology. A superconducting or photonic processor has no
  measurable gravitational degree of freedom, and the decisive falsifiers are the measured couplings, the
  active-mass nulls and Cherenkov emission, all already in hand.
- [I] The adjacent operational claim, extraction of energy from a local vacuum, is tested on hardware by the
  quantum energy teleportation ladder in [the topic note](../topics/pais-claims-falsification.md).
