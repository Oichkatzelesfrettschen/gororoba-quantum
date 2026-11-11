# Casimir geometry, warp metrics, and local stress: primary sources

[P] marks a source result or statement. [I] marks a repository inference or
implementation requirement. [E] is reserved for retained execution evidence;
reading a theoretical paper does not create experimental evidence.

The [evidence audit](../topics/casimir-warp-evidence.md) owns the interpretation
and implementation boundary. This note owns the five source identities and
reading scopes. The registry entries are in [SOURCES.json](../../SOURCES.json).
The audit date is 2026-11-11.

## Identity and inspected material

| Source | Publication and exact inspected source | Reading scope |
|---|---|---|
| White, Vera, Han, Bruccoleri and MacArthur (2021) | *Worldline numerics applied to custom Casimir geometry generates unanticipated intersection with Alcubierre warp metric*, European Physical Journal C 81, 677; published online 2021-07-31; [DOI 10.1140/epjc/s10052-021-09484-z](https://doi.org/10.1140/epjc/s10052-021-09484-z); [publisher article](https://link.springer.com/article/10.1140/epjc/s10052-021-09484-z) | Abstract; sections 1, 3 and 4; figures 2, 7, 9 and 10; conclusion and data statement. The public PDF's pages 8-9 were also rendered to inspect the contour comparison and proposed experiment. |
| White, Vera, Sylvester and Dudzinski (2025) | *Interior-flat cylindrical nacelle warp bubbles: derivation and comparison with Alcubierre model*, Classical and Quantum Gravity 42(23), 235022; [DOI 10.1088/1361-6382/ae237a](https://doi.org/10.1088/1361-6382/ae237a); [Crossref publisher-deposited record](https://api.crossref.org/works/10.1088/1361-6382/ae237a) | This receipt binds bibliographic metadata, license metadata and the deposited abstract. It does not bind the article body. Crossref distinguishes the issue date 2025-12-05 from online publication 2025-12-08. |
| Alcubierre (1994) | *The warp drive: hyper-fast travel within general relativity*, Classical and Quantum Gravity 11, L73-L77; [DOI 10.1088/0264-9381/11/5/001](https://doi.org/10.1088/0264-9381/11/5/001); [arXiv gr-qc/0009013v1 HTML](https://arxiv.org/html/gr-qc/0009013v1) | Abstract; the ADM metric, equations (1)-(8); Eulerian observer and energy-density equations (18)-(19); concluding energy-condition discussion. The arXiv posting is 2000-09-05; that is not the journal publication year. |
| Gies and Klingmuller (2006) | *Worldline algorithms for Casimir configurations*, Physical Review D 74, 045002; [DOI 10.1103/PhysRevD.74.045002](https://doi.org/10.1103/PhysRevD.74.045002); [arXiv quant-ph/0605141v1 HTML](https://arxiv.org/html/quant-ph/0605141v1), posted 2006-05-16 | Abstract; sections 2.1 and 2.2, equations (11)-(15) and footnote 3; sphere/plate intersection criterion in section 3.1.2. Other geometry benchmarks were not independently reproduced. |
| Schafer, Huet and Gies (2015 preprint) | *Worldline Numerics for Energy-Momentum Tensors in Casimir Geometries*; [arXiv 1509.03509v1 HTML](https://arxiv.org/html/1509.03509v1), posted 2015-09-11 | Abstract; section II's point-split Green-function and common-point worldline construction; section V's conclusions and distinction between statistical and discretization errors. Later HTML conversion dates are not publication dates. |

The publisher HTML and arXiv HTML are response snapshots. Their bytes are
not added to this repository. SHA-256 identifies the retrieved representation,
not the scientific validity of a paper or a claim that every section was read.

| Retrieved source | Bytes | SHA-256 | Retrieval UTC |
|---|---:|---|---|
| White 2021 publisher HTML | 355078 | `7212d7a1f4d2d07c708d7254625a4feadcb47bd43271248d6e60495800efd6a9` | 2026-11-11T20:46:24.882213+00:00 |
| White 2025 Crossref JSON | 14708 | `5a84d285ce4c6bf9a5b79cf15d40355a3439819f149bf2b6abc163e6a5128fc0` | 2026-11-11T20:44:53.909933+00:00 |
| Alcubierre arXiv v1 HTML | 92784 | `7e61f9ec3c638caf7a7618b7d276ad3b62b2cc2153a026edc0ea0565b74b2ebd` | 2026-11-11T20:44:05.956220+00:00 |
| Gies and Klingmuller arXiv v1 HTML | 302002 | `4523e8eb599c6ef7fe08b3b71bb7e3b8d9b2a08b23ce0a53cb218d613e7eaf72` | 2026-11-11T20:44:06.568194+00:00 |
| Schafer, Huet and Gies arXiv v1 HTML | 694775 | `80ea88392586cced398ed5461d7698cb1b639f6fbd67b2e15a53df42e3ded89b` | 2026-11-11T20:44:06.380202+00:00 |

The unchanged White 2021 PDF already lives in
[gororoba-documents-public](https://github.com/Oichkatzelesfrettschen/gororoba-documents-public/blob/12ce560fbd70e1922f2df91c83a4ab57c01a52e4/physics/field-theory/White_2021_Casimir_Warp.pdf).
This audit fetched that copy and independently obtained SHA-256
`1580be671a957993b796344cb55cfd9b99ea2dbdb37cb57327c4205f005732b5`,
2,024,021 bytes, matching its existing document manifest. Its CC BY 4.0
grant is printed in the article. No duplicate reading copy is introduced.
The arXiv responses label their licenses as nonexclusive or assumed
nonexclusive; this note does not interpret those labels as downstream PDF
rehosting permission.
The White 2025 metadata identifies CC BY 4.0 for the version of record.
Its direct publisher retrieval returned a CAPTCHA during receipt acquisition;
that response is excluded, and the registered JSON is explicitly
metadata/abstract-only.

[I] Relevance: calibration-aware compilation low; Cayley-Dickson structure
none; factoring resource estimates none. The direct relevance is the
boundary between a numerical vacuum model, a local stress tensor, a metric
construction, and a physical gravitational measurement.

## What the White papers establish

[P] White 2021 reports numerical worldline calculations for custom Casimir
geometries. Its preliminary fabrication images concern cavity structures.
Figure 9 compares calculated contours with an Alcubierre energy-density
section. The paper acknowledges the distinction between the extruded
pillar geometry and a toroidal distribution, then considers a 1 micrometre
sphere within a 4 micrometre cylinder. Figure 10's transit-time apparatus
is proposed conditionally; it is not a reported transit-time or curvature
measurement. The data statement describes theoretical work.

[I] Thus the defensible historical description is a modeled resemblance
that motivated a proposed experiment. The paper does not report an
accidentally measured spacetime bubble. A future transit-time residual
would also require electromagnetic propagation and instrument controls
before attribution to a metric perturbation.

[P] White 2025's deposited abstract describes a family of chosen shift
geometries and ADM calculations of extrinsic curvature, York time, energy
density and momentum densities, with Gaussian cylindrical profiles and
an Alcubierre comparison. [I] The abstract supports classifying that work
as a theoretical metric construction. It supplies no experimental
validation of the 2021 Casimir proposal. This receipt does not support
claims about uninspected equations, figure-generation code or an
independently reproduced solution.

## Why a plotted scalar is insufficient

[P] Alcubierre specifies a metric and computes the stress it would require
through Einstein's equation. Equation (19) gives the Eulerian energy
density and its negative sign where the shape gradient contributes.
[I] Reversing this reasoning requires a compatible full source tensor,
boundary conditions and dynamics. A negative scalar density or a visually
similar contour does not solve that inverse problem.

[P] Gies and Klingmuller treat a real scalar field with Dirichlet boundaries.
The interaction counts worldlines intersecting both disconnected bodies
for the two-body case. Footnote 3 distinguishes the centre-of-mass
integrand's static effective-action density from the local interaction
`T00`; they differ by a total-derivative contribution. [I] Integrated
interaction-energy agreement therefore does not by itself identify a
pointwise gravitational source. This is a source-identification obligation,
not a claim that every result in White 2021 has been disproved.

[P] Schafer, Huet and Gies construct local scalar energy-momentum components
from a subtracted point-split Green function. Their worldlines have common
endpoints in the coincidence limit, and derivative terms enter the local
operators. They separately discuss statistical and discretization error.
[I] This supplies a method boundary for any future local-tensor calculation;
it does not turn the scalar model into electromagnetic fields with material
dispersion or provide the finite sphere/cylinder source tensor automatically.

The already registered
[real-material Casimir review](0902.4022.md) supplies ideal plane-plane
energy and pressure formulas and the calibration chain for an actual
force measurement. Its material-response requirements remain applicable.
The full electromagnetic tensor and local curvature counterexample in the
[audit](../topics/casimir-warp-evidence.md) are explicitly ideal reference
calculations with their own assumptions.
