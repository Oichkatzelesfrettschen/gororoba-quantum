# Ledgers behind the Ascella CZ tomography conjectures

This note records the sources and the workspace lineages that the preregistered conjectures of
[ascella-cz-tomography-reference-case.md](../../design/ascella-cz-tomography-reference-case.md) rest on, and which
of them predict a rate of a two-photon postselected CZ process tomography. A source is cited by the first 12 hex of
its `manifest.tsv` sha256 in the documents repository named beside it (pub: gororoba-documents-public, priv:
gororoba-documents-private). A private work appears by digest, bibliographic data and a paraphrase with its section
number only.

## Photonic sources

| Digest | Repository | Work | Claim used | Observable |
|---|---|---|---|---|
| 0ee7b47bd723 | pub | Maring et al. 2024, A versatile single-photon-based quantum computing platform, Nat. Photon. 18, 603 | Ascella paragraph: set-up efficiency about 8 %, purity above 99 %, on-chip visibility 91 to 94 % across the 15 source pairs; Table 1: postselected CNOT success 1/9; Methods: compiled matrix fidelity 99.7 % | F rises with overlap; the pair-to-pair spread of 3 points maps to about 0.035 in F |
| 3c845c21a16f | pub | Pont et al. 2022, High-fidelity generation of four-photon GHZ states on-chip | Supplement S-II A, Eq. S9: source as master Fock state, distinguishable subsidiary photons and noise photons; Table S1: pair overlap 0.88 to 0.92 depending on emission delay | The overlap of the pair on chip modes 0 and 2 can differ from the dashboard HOM (hypothesis for Ascella) |
| 8d34bd0f8e4e | pub | Maring et al. 2023, One nine availability of a photonic quantum computer on the cloud | Sec. III.A: hourly automated calibration; Sec. III.D: published HOM, transmittance and 1 - g2 | The HOM at run time can differ from the plan read |
| 163c7542c11b | pub | Heurtel et al. 2023, Perceval, Quantum 7, 931 | Sec. 3.2.4: source model with transmittance, multiphoton probability and indistinguishability, the two-photon mean wavepacket overlap | The forecast is affine in the overlap at fixed g2 |
| 153d6b6de3ef | pub | Galetsky, Kohl, Notzel 2025, Photonic processor benchmarking for variational quantum process tomography | Sec. II: phase-shifter thermal noise dominates mode mismatch and dark counts on the processors they test | A HOM-independent deficit of F against the overlap law |
| 1291df4cd86b | priv | Ollivier et al. 2021, Hong-Ou-Mandel interference with imperfect single photon sources, PRL 126, 063602 | Eq. (1) and (2): the overlap behind a HOM visibility read is V + g2 for identical noise photons and (V + g2)/(1 - g2) for distinguishable ones | The g2-corrected conjectures |
| efcbeed55085 | priv | Ollivier et al. 2020, Reproducibility of high-performance quantum dot single-photon sources | Sec. II: indistinguishability scatters by about 2.8 points across fifteen sources | A source change between calibrations moves F by more than the design spread |
| 963b9cb57403 | priv | Pont et al. 2022, Quantifying n-photon indistinguishability with a cyclic integrated interferometer, PRX 12, 031033 | Eq. (5) and (8): an n-photon state is a convex mixture of the indistinguishable and distinguishable components; Sec. III.A: visibility falls with emission separation | For two photons one parameter, the overlap, carries all of it |
| b38e20cbc6d4 | priv | Loredo et al. 2016, Boson sampling with single-photon Fock states from a bright solid-state source | Eq. (1): two-photon coincidence probability ((1+I)/2)|per|^2 + ((1-I)/2)|det|^2 | The overlap law and the rail ratio |
| 992b62a7676a | priv | Scheel 2004, Permanents in linear optical networks | Eq. (10): Fock-state amplitudes of a linear network are permanents of submatrices | Coincidence amplitudes of the CZ block |
| 7b49383c4375 | priv | Tully, Washburn, Simons 2026, Fixed-order postselected CHSH reference acquisition on a cloud photonic processor | Eq. (17): outputs as v P_coherent + (1 - v) P_distinguishable with fitted v near but not equal to the dashboard HOM; Sec. IV: within one session the dashboard HOM and the fitted v moved apart; Sec. V: excess pass-to-pass dispersion | Overlap estimates from the data need not equal the plan HOM; overdispersion has a precedent |
| 01508c79f85b | priv | van Enk, Blume-Kohout 2013, When quantum tomography goes wrong | Sec. I.B and II: drift correlated with setting order voids a single-process model; overcomplete data detect it | The overdispersion statistic |
| 3815aaaae28b | priv | Sanz et al. 2026, Exponential improvement in benchmarking multiphoton interference | Eq. (1): twirling to partition states; Sec. II | For two photons the mixture law is exact, so structure beyond it is not distinguishability |
| fcd85cfb34e3 | priv | Mezher, Mansfield 2022, Assessing the quality of near-term photonic quantum devices | Sec. 2.3, A1 and A2: uniform loss commutes to the input | Setting-independent click chance |
| bc7bdf8a6a29 | priv | Knill, Laflamme, Milburn 2000, Efficient linear optics quantum computation | Eq. (6): the c-sign target diag(1, 1, 1, -1) | Lineage of the gate |

Searched and absent from all three manifests: Ralph, Langford, Bell and White on the 1/9 postselected CZ;
Hofmann and Takeuchi; Kiesel; O'Brien 2003; Tichy; Shchesnovich; Menssen; Renema. The overlap law is derived here
from Loredo Eq. (1) and the case's own photon model, so no conjecture rests on an absent work.

## Workspace lineages against this measurement

The tomography reads two matrix functions of the interferometer, the 2 x 2 permanent and determinant. A lineage
predicts a rate only through them.

| Lineage | Where the workspace holds it | Verdict for this tomography |
|---|---|---|
| Permanent and determinant (Gram expansion) | `scripts/ascella_cz_tomography_case.py` photon model; `docs/design/ascella-two-photon-associator-case.md` | Reaches rates: the overlap law F = (1 + M)/(2(2 - M)) and the rail ratio D = 5 - 4M. Hafnians need Gaussian states, and with two photons the only immanants are the permanent and the determinant |
| Pfaffian (Moreno's Stiefel reduction, Pfaffian kernel ideals) | `docs/evidence/moreno_stiefel/`; gororoba-open claim C-1776 | No observable in this measurement: Pf(L_a + iR_b) acts on algebra multiplication matrices, and the photonic expansion carries a determinant, not a Pfaffian |
| de Marrais box-kites | gororoba-open `crates/de_marrais_2000`, claims C-003, C-013; `scripts/box_kite_census.py` | No observable here. Box-kite sign blocks do set two-photon rates in the Belenos box-kite circuits; the CZ mesh is not such a block |
| Hurwitz, Dickson, Schafer, Brown 1967 (composition and doubling) | gororoba-open `crates/hurwitz_1898`, `HurwitzTheorem.v`; `gororoba_quantum/cd_core.py` | No observable: the CZ unitary is symmetric with a non-constant diagonal, so it is no left multiplication L_v |
| Brown 1972, Moreno, Biss-Dugger-Isaksen, Levratti (zero divisors, sign parity) | gororoba-open `ZD_Criterion.v`; `docs/notes/papers/levratti-2026-*.md` | No observable: the CZ block diag(1, 1, 1, -1)/3 has full rank |
| Hilbert-Samuel multiplicity, Rees algebras, fiber cones | `docs/evidence/a5-exceptional-fibers/` | No observable: commutative-algebra data about orbit closures |
| Wilmot, Jordan and exceptional algebras, A-infinity | gororoba-open `crates/wilmot_2025`, `E8CartanDerivation.v` | No observable |

## Findings this note carries

- The overlap law and its two estimators are derived results checked in the case's tests. Prior art for using the
  rail ratio as an in-situ overlap estimator was not searched; the Ralph-gate mode-mismatch papers are not held.
- The retained 2026-10-31 pair gives M_F = 0.888 from its fidelity and M_R = 0.914 from its rail rates, both above
  the platform's HOM read of 0.8756; the rail estimate excludes the read after widening for overdispersion.
- The retained counts scatter about 1.9 times beyond their Poisson-only reference, so every verdict widens its
  interval by the square root of the pair's own ratio.
- Registry flags met on the way: gororoba-open C-004 (a 168-element action on the box-kites) is Refuted and C-1471
  (the automorphism group of the sedenions) is Provisional; neither enters this case.
