# Casimir geometry and the nanoscale warp claim

The 2021 result behind the nanoscale warp-bubble reports is a numerical
Casimir-geometry calculation and a proposed experiment. The inspected
paper does not report a measured spacetime bubble. Its fabrication images,
modeled scalar contours and proposed transit-time test are different
evidence categories. The 2025 follow-up is a theoretical metric
construction. The [primary-source note](../papers/casimir-warp-primary-sources.md)
records the exact sources and reading scopes supporting those statements.

[P] denotes source statements, [I] deductions or implementation choices,
and [E] retained execution evidence. This reconciliation is dated
2026-11-11. Completion and numerical validation belong to the
[active plan](../../state/plans/casimir-warp-evidence.json); file presence
alone does not establish a successful replay.

## Evidence categories and the remaining software gap

| Layer | Status within the inspected work | Required interpretation |
|---|---|---|
| Scalar Casimir interaction model | [P] White 2021 and the worldline literature supply numerical/theoretical results. | Declare field, boundary conditions, subtraction and the computed observable. |
| Local electromagnetic stress tensor | [I] The ideal infinite-plate tensor is a useful analytic reference. The finite material sphere/cylinder tensor is not supplied by a scalar contour. | Identify all components in one frame, including momentum flux and stresses. |
| Warp metric | [P] Alcubierre and White 2025 specify metric families and derive required source quantities. | A prescribed metric does not establish an available material source. |
| Self-consistent metric/source pairing | [I] Matching energy density is only one component of the field equation. | Check the complete tensor equation and the source's physical assumptions. |
| Laboratory spacetime measurement | The inspected 2021 paper proposes a measurement; the inspected 2025 abstract reports theoretical calculations. | A gravitational claim requires an actual calibrated observable and discrimination from ordinary electromagnetic effects. |
| Encoded circuit or QPU model | Existing repository work estimates observables of declared finite Hamiltonians. | A model-force derivative or encoded negative energy is not a physical force or curvature measurement. |

The bounded missing implementation is a source-aware, dimensionally explicit
audit connecting the ideal Casimir benchmark to a complete-tensor
counterexample. It belongs in the Rust numerical workspace, with source and
interpretation reconciliation here. It does not require another QET
pipeline or a provider acquisition.

## Existing work and historical findings

The audit read `gororoba-quantum` at
`d5ff68e283ca26b12dc07bf95a48cc515a3c6145` and the Rust baseline at
`b73ca1050ace1c5c6f8a25564879f70bacdbf80b`.

| Existing item | Reused boundary |
|---|---|
| [Persona corpus results](persona-corpus-verified-results.md) and `scripts/persona_corpus_checks.py` | Existing ideal/Lifshitz, material and gravitational-scale calculations. |
| [Vacuum model evidence](../../evidence/vacuum_models/README.md) | Declared finite models, cutoffs and conditional force derivatives. |
| [Vacuum endpoint information](../../evidence/vacuum_endpoint_information/README.md) | Existing model and information endpoints. |
| [Vacuum run opportunities](../vacuum_field_run_opportunities.md) | Distinguishes device sensing, encoded models and physical force/radiation observations. |
| [Pais claim analysis](pais-claims-falsification.md), `scripts/qet_two_qubit_reference.py`, and `scripts/qet_passivity_controls.py` | Existing QET and passivity controls; no new circuit evidence is needed for this tensor question. |
| [Relativistic metrology scale](relativistic-metrology-scale.md) | Distinguishes a photonic mode-reachability cone from spacetime geometry and calibrated proper time. |
| [Historical Rust handoff](open_gororoba_handoff.md) and [Casimir claim audit](../../../results/live/local-audit-provenance/central-dispatch-handback/casimir-claim-audit.json) | Preserve the earlier audit's revision-bound observations and unresolved claim/evidence links. |

The historical Casimir handoff identified numerical and provenance defects
against earlier Rust revisions. The current baseline already uses the
scalar prefactor `-1/(32*pi^2)`, requires both bodies for the two-body
interaction and returns a nonnegative standard error. It also separates
the scalar and electromagnetic parallel-plate benchmarks. Those corrected
defects are not a new backlog. The historical handoff bytes remain intact.

[E] The owner-tool receipt at Rust path
`data/output/audit/casimir-warp-evidence/registry_mutation_receipt.json`
records a subsequent canonical database correction. The binary registry
retains its 393 entries and adds `casimir-warp-audit`, with no removals or
owner changes. Claim `C-871` is narrowed to the analytic electromagnetic
ideal-plate oracle; its statement, locator and interpretation revisions
are 998-1000. The associated theorem title now describes the analytic
formula, and its status remains `source_only`, without new kernel
admission. `E-044` drops the unrelated `C-740`/`C-741` links; `E-081`
drops the analytic-oracle claim link and describes the real-scalar
diagnostic and its distinct outputs and error limits. `E-081` still has
no retained output artifact, and this correction asserts no replay of it.
The receipt records canonical mutations only. Registry export completion,
admission checks and publication of that receipt remain pending at this
observation; this note does not infer those outcomes from the mutation.

[I] A separate current Alcubierre baseline issue concerns an axial taper in
the zero-nacelle branch. The Rust change removes that taper from the pure
Alcubierre case and adds a regression. That implementation correction is
distinct from the full-tensor counterexample below.

## Observable and unit boundaries

[P] Gies and Klingmuller's centre-of-mass worldline integrand is a static
effective-action density; its footnote 3 identifies a total-derivative
difference from local interaction `T00`. The local-operator construction
of Schafer, Huet and Gies uses point splitting and common-point paths.
The [source note](../papers/casimir-warp-primary-sources.md#why-a-plotted-scalar-is-insufficient)
records both locators. [I] A successful integrated-energy benchmark alone
does not license pointwise substitution of that integrand into Einstein's
equation.

For a zero-temperature electromagnetic field between perfectly conducting,
infinite parallel plates separated by `a`, define

\[
K=\frac{\pi^2\hbar c}{720a^4}>0,\qquad
u=-K,\qquad E/A=-Ka,\qquad P_\perp=-3K.
\]

The [registered review](../papers/0902.4022.md) gives the ideal energy and
pressure reference. [I] With plate normal along `x`, tangential Lorentz
symmetry and the traceless ideal electromagnetic stress give, in an
orthonormal frame with signature `(-,+,+,+)`,

\[
T_{\hat a\hat b}=K\,\mathrm{diag}(-1,-3,+1,+1).
\]

Energy density and stress have SI units `J/m^3 = Pa`; energy per area has
units `J/m^2`. The conversion
`kappa = 8*pi*G/c^4` makes `kappa*T` a curvature quantity with units
`m^-2`. Its magnitude alone is not a metric, a propagation prediction or a
measured change in transit time. The familiar factor of two between one
Dirichlet scalar and the ideal electromagnetic parallel-plate energy is
specific to that benchmark; it is not a general conversion for custom
curved material geometries.

## A full-tensor counterexample

[I] The Rust audit uses the local stationary metric

\[
ds^2=-(dx^0)^2+[dx-B(y)dx^0]^2+dy^2+dz^2,\qquad x^0=ct,
\]

where `B` is dimensionless, `q=dB/dy` has units `m^-1`, and
`r=d^2B/dy^2` has units `m^-2`. In the Eulerian orthonormal frame
`e_hat0 = partial_0 + B partial_x`, `e_hat1 = partial_x`,
`e_hat2 = partial_y`, `e_hat3 = partial_z`, the exact covariant Einstein
tensor is

\[
G_{\hat a\hat b}=
\begin{pmatrix}
-q^2/4&r/2&0&0\\
r/2&-3q^2/4&0&0\\
0&0&q^2/4&0\\
0&0&0&-q^2/4
\end{pmatrix}.
\]

Choose `r=0` and `q^2/4=kappa*K`. The `00`, `xx` and `yy` components
match the ideal plate tensor above, but

\[
G_{\hat z\hat z}-\kappa T_{\hat z\hat z}=-2\kappa K\ne0.
\]

This exact local construction is a counterexample to the implication
"matching negative energy density establishes a matching spacetime
source." It supplies no finite bubble, material cylinder solution or
apparatus prediction. Finite boundaries, plate/support stresses,
conservation, a realizable quantum state and dynamical response remain
separate obligations. The full derivation belongs to the
[Rust engineering note](https://github.com/Oichkatzelesfrettschen/gororoba-open/blob/10aa093345e5fc2b0281fe602c174250d61b3685/docs/engineering/casimir_warp_evidence_audit.txt).

## Native implementation and replay binding

The initial cross-repository implementation is published at
[revision 10aa093345e5fc2b0281fe602c174250d61b3685](https://github.com/Oichkatzelesfrettschen/gororoba-open/tree/10aa093345e5fc2b0281fe602c174250d61b3685).
The plan remains active until validation receipts bind the final source
revision, actual outputs and canonical registry exports. The initial
source pin does not represent admission of subsequently generated evidence.

| Rust path | Responsibility |
|---|---|
| `crates/casimir_core/src/stress_energy.rs` | Checked SI ideal electromagnetic plate tensor and scalar reference quantities. |
| `crates/gr_core/src/warp_stress_energy.rs` | `planar_shift_curvature(q, r)`, exact Eulerian curvature and full-component residual checks. |
| `crates/gr_core/src/warp_metric.rs` | Pure Alcubierre zero-nacelle baseline and its axial-profile regression. |
| `crates/gororoba_cli_physics/src/bin/casimir_warp_audit.rs` | `casimir-warp-audit` command and audit artifact production. |
| `data/output/audit/casimir-warp-evidence/` | `reference_scalars.tsv`, `tensor_residuals.tsv`, `summary.json` and reproduction manifest, once generated and validated. |

Use the Rust engineering note for the exact invocation, constants,
component order and output contract. Numerical outputs become [E] only
when their actual bytes and generating revision are retained. This note
records neither a new provider run nor a laboratory result.

The remaining physical work lies beyond these software checks: a local
renormalized electromagnetic tensor for specified finite materials,
self-consistent source and metric with boundary/support contributions,
and a calibrated experiment that distinguishes gravitational propagation
from electrodynamics and instrument response. The counterexample settles
the scalar-matching inference; it does not settle whether every conceivable
warp geometry is physically realizable.
