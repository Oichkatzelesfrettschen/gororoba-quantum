# Cayley-Dickson geometry, measured interference, and shared-shot visuals

The campaign asks how reliably a calibrated quantum processor realizes
specified interference structures while several circuits share an execution
row. The Cayley-Dickson algebra supplies exact predictions and controlled
contrasts. The processor supplies physical counts, joint errors, and model
residuals. The visualization exposes those observations on a mathematical
geometry whose construction is independently checked.

The [packed acquisition](../../gororoba_quantum/PACKED_ALGEBRA.md) keeps the
ripple/atlas, rank-sector, and folded-QPE families independently admitted.
The five connections below reuse their planned observations and add zero
execution rows. Adding physical qubits can improve simultaneous coverage,
but row count, shots, circuit duration, repetition delay, and job overhead
determine the relevant time costs. Readiness and final seconds belong to
the fresh, source-bound preparation records.

## What a reality ripple means here

A physical ripple is an intervention whose outcome distribution changes
relative to a specified reference. Phase, walk depth, or rank-path parameter
changes the prepared circuit. A measurable probability redistribution is the
operational consequence. The word "reality" identifies the measured
processor response; the word supplies no claim about modifying spacetime or
demonstrating a new fundamental interaction.

Four layers remain visible: exact mathematics, ideal simulation,
calibration-derived noise predictions, and hardware observations. Artistic
interpolation is a fifth presentation layer. A smooth animation may connect
separately prepared points, but its intermediate frames are rendered
interpolation. Computational-basis counts supply probabilities and compatible
joint statistics; complex amplitudes require additional measurement settings.

The scientific result is a bounded statement about implementation fidelity,
model adequacy, or context sensitivity. The exact rank and zero-divisor
identities can already be checked classically. Hardware tests whether the
specified observables survive physical execution. Computational advantage
would require an additional task definition and full resource comparison.

## Five connections that reuse the acquisition

| Mathematical connection and prior work | Reused observations | Scientific question and visual encoding |
| --- | --- | --- |
| Primitive zero divisors form seven signed octahedral graphs. De Marrais's [box-kite construction](math-0403113.md) predates this campaign; the repository independently enumerates its finite corpus. | Eight phase points on each of 84 edges, plus matched readout and representative isolated controls. | Show measured edge probabilities, uncertainty, dark leakage, and descriptive fringe fits. Color the exact edge sign separately. Determine which cancellation contrasts survive hardware execution and which differ from the noise prediction. |
| The seven strut labels index the Fano plane `PG(2,2)`, with lines `{a,b,a XOR b}`. The [source survey](open_gororoba_survey.md) already records the projective organization. | Seven atlas outcomes within each physical shot, together with the row's kite-to-patch assignment. | Arrange residual summaries in Fano coordinates and inspect joint failure patterns or covariance. Compare algebra labels and physical patch labels. A geometric arrangement does not establish causal coupling between its points. |
| Multiplication kernels are dark directions of `L_a^T L_a`; published [eigentheory](0905.2987.md) and [annihilator theory](math-0511691.md) constrain the spectrum. The [rank-path ledger](cayley_dickson_rank_topology_sources.md) states the path-specific deductions. | Eight four-qubit sectors, four probes per sector, five parameter values, and isolated references. | Display `p_success` and the derived norm `alpha(t)^2*p_success`, with `alpha=sum(abs(a_s))` explicit. Compare persistent darkness, exceptional suppression, and fixed versus rotating Gram frames. Finite frequencies constrain the norm predictions; exact rank and topology remain mathematical conclusions. |
| Associator phases arise from a sign cochain, and Walsh spectra retain more information than degree alone. [Kirshtein](1207.4230.md), [Albuquerque-Majid](math-9802116.md), and the [prior-work ledger](prior_work_synthesis.md) establish the relevant boundaries. | Original Design C spectra and the two four-qubit walk distributions at prepared depths zero through four. | Plot labeled outcomes, return probability, and the preregistered crossover. The depth-two complemented-Walsh identity connects static spectrum to the walk. Test whether the distinct distributions remain distinguishable after physical compilation and simultaneous execution. |
| Shared measurements reveal joint error structure. [Parallel-experiment literature](quantum_experiment_parallelism.md) establishes simultaneous characterization and context effects as prior work. | The lossless shot-ordered registers, packed and isolated conditions, matched A/B exchanges, and folded-QPE controls. | Show covariance, joint failure patterns, temporal blocks, hardware-minus-model residuals, and packed-minus-isolated differences. Identify deviations that a product of marginal noise models misses, subject to drift and control limitations. |

Each hardware question concerns a specified compiled experiment. A repeated
pattern across mathematically equivalent kites can reflect shared circuitry,
readout, scheduling, or calibration error. The physical mapping and controls
must accompany any interpretation attributed to the algebra.

## Signed-kite spectral deduction

Let `S` be the six-by-six symmetric adjacency with the ripple graph's
cancellation signs on edges and zero elsewhere. Let `A=abs(S)` be the
unsigned `K(2,2,2)` adjacency. The current exact graphs admit a diagonal sign
matrix `D` satisfying `D*S*D=-A`. A breadth-first traversal assigns the vertex
signs; checking every edge verifies the identity without numerical tolerance.

For the vertex order returned by `ripple_dynamics.box_kites()`, the diagonal
entries are:

| Strut constant | Diagonal entries of D |
| ---: | --- |
| 1 | `1,-1,1,-1,-1,1` |
| 2 | `1,-1,-1,-1,1,1` |
| 3 | `1,-1,1,-1,1,-1` |
| 4 | `1,1,1,-1,-1,-1` |
| 5 | `1,-1,1,-1,-1,1` |
| 6 | `1,1,-1,-1,1,-1` |
| 7 | `1,-1,-1,1,1,-1` |

The unsigned spectrum is `4,0,0,0,-2,-2`, so the signed spectrum is
`-4,0,0,0,2,2`. On vectors constant within each strut pair, `A` reduces to
the three-by-three matrix with off-diagonal entries 2. The three within-pair
antisymmetric vectors span its zero eigenspace. Conjugation by `D` preserves
the spectrum and converts the signed problem to the negative unsigned one.

The local audit checked all seven integer matrix identities on 2026-10-12.
The deduction is a standard consequence of signed-graph antibalance, without
a novelty claim. A common sign convention makes measured edge contrasts
easier to compare. The four-qubit associator walk uses a different operator;
the campaign does not implement time evolution under this six-node adjacency.

The [executable witness](../sources/open_gororoba/check_signed_kite_switching.py)
reads the existing `results/ripple/evidence.json`, reconstructs each matrix
and switching by traversal, and independently computes the exact
characteristic polynomial `(lambda+4)*lambda^3*(lambda-2)^2`. Integer
Faddeev-LeVerrier steps avoid a floating-point spectral tolerance. The checker
rejects a single flipped sign and damaged support; arbitrary switching of
one vertex preserves the result. Its
[retained output](../sources/open_gororoba/signed_kite_switching.json) binds
both input and checker SHA-256 values.

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
  literature/sources/open_gororoba/check_signed_kite_switching.py
```

The source repository also defines a sign-imbalance field
`eta(u,v)=psi(u_low,v_high) XOR psi(u_high,v_low)`. That field differs from
the cancellation signs used here. Its dimension-16 imbalance value and its
higher-dimensional asymptotic conjecture describe another calculation.

## Descriptive visual and uncertainty contract

The display should let an observed change move the corresponding graphic:
edge color follows a probability or residual, its uncertainty band follows
the interval, node area follows the declared marginal probability, and a
matrix cell follows a measured covariance. A legend fixes those mappings
across views and keeps mathematical coordinates separate from physical
qubit coordinates. Missing hardware observations remain explicitly unmeasured.

The supplied screenshot is a circuit schedule: INIT/FINI blocks, native-gate
clusters, and measurement/reset intervals occupy hardware-qubit lanes.
The schedule describes physical occupancy and waiting intervals. It supplies
timing context for the distribution views; outcome counts supply their data.
An unlabeled cycle scale needs the backend's `dt` and scheduler metadata
before conversion into seconds.

| View | Data mapping | Boundary |
| --- | --- | --- |
| Seven-kite atlas | Small multiples with common phase and probability scales; raw estimates, model curves, and uncertainty remain individually selectable. | The fitted fringe `c+a*cos(phi)+b*sin(phi)` is descriptive. Readout errors and gate errors both affect its visibility and phase. |
| Joint-error matrix | Compute each covariance from aligned outcomes in the same execution row, then retain row identity when summarizing compatible conditions. | Raw pooling over unlike rows can create covariance from changing means. A shared shot index exists within a PUB, not across independently executed PUBs. |
| Residual field | Separate `hardware-ideal`, `hardware-noise-model`, and `packed-isolated` panels with signed color scales centered at zero. | Each difference keeps its own uncertainty and model error. Representative isolated conditions qualify their own contrasts. |
| Rank-sector sheet | Eight panels share parameter coordinates; show all acquisition points, exact curves, observed intervals, and the alpha normalization. | Interval scaling by `alpha^2` assumes alpha is an exact declared design value. Sparse probabilities do not reconstruct every singular vector. |
| Walk distribution | Sixteen outcome coordinates, depth slices, return probability, and the declared A/B contrast. | Separate prefix preparations support a sequence of snapshots rather than a continuously observed trajectory. |

Retain complete shared-shot vectors when resampling within a row. Shuffle or
bootstrap the entire vector together so the analysis preserves joint errors.
Cross-row or temporal-block resampling needs an explicit exchangeability or
stationarity assumption. Distinguish uncertainty from finite hardware shots,
finite model samples, and calibration-model misspecification. The inferential
endpoints remain those in the family admission contract; supplementary fits,
covariances, and attractive patterns remain descriptive until independently
qualified. Additional descriptive plots do not create additional scientific
discoveries through repeated significance searches.

## Source audit, novelty, and retained documents

The bounded audit read the relevant open_gororoba sources at
`abbf13cada78d9b106fc610a36f6eea54567ecfc` and the existing IBMQuantum primary
notes. It compared proposed connections with the source registry, exact graph
construction, rank-path ledger, and earlier literature synthesis. The audit
does not establish exhaustive literature novelty.

The [retained evidence contract](../sources/open_gororoba/cayley_dickson_evidence_contracts.txt)
preserves the source's corrections and claim boundaries. Its
[manifest and license record](../sources/open_gororoba/README.md) bind the
copied bytes and source revision. The following locators support the
connections and their limitations:

| Source locator at the declared revision | Use |
| --- | --- |
| `docs/engineering/cayley_dickson_evidence_contracts.txt`, lines 25-81 and 143-157 | Sign-code structure, relative controlled phase, cochain terminology, and limits of degree-based claims. |
| Same document, lines 83-141 and 224-229 | Sedenion membership, exact annihilator certificates, alpha versus unit normalization, rank charts, and finite flag-complex scope. |
| `crates/algebra_analysis/src/boxkites/face_sign_census.rs`, lines 24-71; `boxkites/tests.rs`, lines 1324-1365 | Exact edge-sign classification and the 42/14 triangular-face census. The census test is an ignored research test, not evidence that this audit executed it. |
| `crates/algebra_analysis/src/boxkites/tests.rs`, lines 1008-1023 | Unsigned octahedron spectrum. |
| `crates/algebra_analysis/src/projective_geometry.rs`, lines 1-17, 44-50, 108-119 | Fano labels and projective-space organization. |
| `crates/algebra_analysis/src/boxkites/imbalance.rs`, lines 1-17 | The separate imbalance sign field and its finite sequence. |
| `registry/claims.toml`, C-020, lines 177-184 | Refuted legacy adjacency: visually plausible structure requires an independent algebraic check. |
| `registry/claims.toml`, C-1632 and C-1633, lines 5058-5071 | A different application illustrates the need for matched controls: sign scrambling degrades an associator detector, while matched temporal-support rotation controls outperform it. Those observations provide methodological context for the QPU campaign. |

Established mathematics supplies the geometry, spectra, and normalizations.
Repository-specific finite deductions supply the exact chosen paths and
circuits. Candidate new measurements concern their physical realization,
joint error structure, and model residuals. The measured outcomes will decide
those claims after an approved execution and analysis.
