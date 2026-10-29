# What the failed Tuna readouts identify

The [qualification](tuna-qualification.md) establishes a failure of a particular
binary measurement path, not a unique physical cause. The path measures q4, q11 and q6,
then measures all 17 qubits, with a barrier and zero programmed settling wait.
The two calibration jobs prepare all-zero and all-one nominal states. Preparation,
spectator occupancy, measurement context, acquisition index and elapsed time therefore
enter the comparison together. Further hardware acquisition has stopped.

## Reconstructed evidence

The [raw-bound diagnostic](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/readout-diagnostics.json)
reconstructs all three 4096-shot histograms, the early/final 2-by-2 tables, all classical-bit
contrasts, within-shot covariance counts, contiguous 256-shot blocks, and lag counts.
The original qualification and its raw bytes keep their original identities.

| Channel | Nominal-zero one count | Nominal-one one count | Empirical contrast |
|---|---:|---:|---:|
| Early q4 | 1694 | 3246 | 0.378906 |
| Terminal q4 | 59 | 3821 | 0.918457 |
| Early q11 | 4039 | 1510 | -0.617432 |
| Terminal q11 | 113 | 3795 | 0.898926 |
| Early q6 | 3353 | 2845 | -0.124023 |
| Terminal q6 | 2470 | 3858 | 0.338867 |

Each count has denominator 4096. A reported one is a thresholded binary label, not an
independently measured excited-state population. In particular, 2470/4096 for nominal-zero
terminal q6 must not be called a 60.3% excitation probability without a qualified assignment
model. The negative early q11 contrast is strong anticorrelation with the nominal
whole-register preparation label, rather than simple random erasure. Flipping that bit
would give empirical balanced classification accuracy (1+0.617432)/2 = 0.808716, but a
post-hoc flip neither verifies the physical state nor clears the frozen qualification.

All 48 fixed early-bit permutations and polarity choices were checked. The best possible
minimum contrast remains 508/4096 = 0.124023. Optimizing early/final consistency instead
still leaves a worst disagreement of 1773/4096 = 43.29%. A fixed permutation/polarity
repair alone is therefore excluded for the retained screen. Arbitrary provider-side
packing or acquisition errors remain a larger hypothesis class.

The failure is distributed across the sampled record. In each corresponding 256-shot
block, the terminal-q6 contrast count lies between 70 and 100; early q4 lies between
82 and 116; early q11 between -175 and -143; early q6 between -41 and -19. Every block
misses the 128-count contrast threshold. These are comparisons of block positions in
separate jobs, not simultaneous paired trials. They exclude an explanation confined to
one short observed block; they establish neither stationarity nor independent shots.

## Where the data path has been checked

The [authenticated source readback](readout-server-source-observation.json) fetched the
stored file attached to each completed job. Every stored cQASM SHA-256 equals its
submitted and retained source SHA-256. The responses expose `compile_stage=none` and empty
`compile_properties`; they do not expose the served pulse program or acquisition settings.
The unchanged source is established through provider storage, while executed analog
identity remains outside the observation. A [log-availability probe](readout-job-log-availability.json)
received HTTP 200 from the completed-job endpoint, while the corresponding log endpoint
timed out on both the normal 60-second request and a bounded 15-second retry. The
probe therefore supplied no served schedule or acquisition log.

The local OpenSquirrel 0.9.1 exporter matches upstream commit
[`9e1fdc7a71f5f7387d671999d8241811ef35d2f1`](https://github.com/QuTech-Delft/OpenSquirrel/blob/9e1fdc7a71f5f7387d671999d8241811ef35d2f1/opensquirrel/passes/exporter/quantify_scheduler_exporter.py),
SHA-256 `7e7776f5af8d310123e57fd45e31416454603d880d02eb458e935c167b0270ce`.
Its writer preserves each `Measure.bit`; `Circuit.measurement_to_bit_map` yields
q4:[17,4], q11:[18,11], q6:[19,6], and qi:[i] for every other qubit. The exporter emits
physical-qubit acquisition channels and per-qubit acquisition indices, with classical
reconstruction supplied through the separate map. Compact destinations are supported by
that interface; their use is not itself a documented protocol violation.

The researched Quantify Scheduler implementation at
[`dcd2405f812e4cca8b625307584234ec8f9b7d12`](https://github.com/quantify-os/quantify-scheduler/tree/dcd2405f812e4cca8b625307584234ec8f9b7d12)
separates measurement pulse duration, acquisition delay and integration duration in
`operations/measurement_factories.py`. Its `backends/qblox/analog.py` requires a unique
threshold and rotation across acquisitions on a sequencer. An independently selected
threshold for each acquisition index is therefore not standard behavior in that researched
implementation. Provider deployment and configuration were not identified, so those source
facts neither prove a served defect nor certify the served path.

The [refreshed monitoring receipt](readout-diagnosis-monitoring.json) records a public notice
that performance reporting is suspended, and the readout query still fails connecting to
the provider's Prometheus endpoint. The dated 300 ns notice states a nominal readout duration; its relation to pulse length,
integration window and complete operation duration remains unspecified. A Mozilla user
agent or a local Prometheus installation cannot supply the unavailable provider state.

## First-principles inference boundary

Let S denote the nominal preparation label, X the actual binary state, and Y the returned
readout label. Under a *fixed* assignment context,

    p_s = P(Y=1|S=s) = a + (b-a) x_s,
    a = P(Y=1|X=0), b = P(Y=1|X=1), x_s = P(X=1|S=s),
    Delta = p_1 - p_0 = (b-a)(x_1-x_0).

A negative Delta identifies neither factor. The present all-zero/all-one preparations
also change every spectator, so a and b may depend on S; even this factorization then
requires an extra assumption. The observed contrasts cannot uniquely estimate fidelity,
T1, excited population, or a discriminator threshold.

For repeated measurements, the appropriate quantum model is an outcome-indexed instrument:

    P(E=e,F=f|S=s,c) = tr[F_f^(c) E_c(M_e^(c)(sigma_s))].

Here sigma_s and the maps act on the qubits together with relevant apparatus memory.
The label c includes controlled spectator, readout-channel and timing settings. M_e is the
first measurement's completely positive map, E_c is intervening evolution, and F_f is the
terminal effect. A qubit-only composition would impose an additional Markov assumption;
a classical context label alone cannot represent arbitrary hidden cavity correlations. Each observed binary joint table supplies only three
independent numbers per nominal preparation. Preparation, conditional state disturbance,
assignment, memory and terminal effects remain unknown. Retaining both bits preserves
useful instrument information, but two nominal preparations are not informationally
complete tomography. [Rudinger et al.](../../notes/papers/2103.03008.md) explicitly use
informationally complete fiducials and joint outcomes to estimate that larger object.

Two simple physical models can be excluded as sufficient explanations under their stated
premises:

- Pure dispersive residual-photon Stark evolution has H proportional to n(t) Z, so
  [H,Z]=0. Pure Z dephasing also preserves Z populations. With fixed preparation and
  positive, context-independent assignment, neither alone reverses Z-basis contrast.
  A residual-photon effect on the resonator signal or classifier is a different mechanism.
- A time-homogeneous two-state relaxation/excitation process gives
  x_1(t)-x_0(t) = exp[-(Gamma_up+Gamma_down)t] [x_1(0)-x_0(0)]. With positive initial
  preparation and assignment contrasts, the observed contrast stays nonnegative.
  Ordinary T1 loss alone is insufficient. Context changes, driven multilevel transitions,
  coherent population transfer, or failed preparation lie outside that restricted model.

Causality supplies another discriminator. A later pulse cannot change a first result
whose acquisition and processing have already closed. The first-readout anomaly cannot
be explained solely by photons remaining *after* that closure. First-pulse dynamics,
integration overlapping a later pulse, electronics memory, prior-shot carryover,
reconstruction, or a different served schedule can still affect the returned first bit.
The current cQASM does not locate the served acquisition-window closure.

## A useful post-hoc response model

The [joint-response sensitivity](../../../results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/readout-response-mixture.json)
asks whether each geometry early/final table lies near the line segment joining its two
control tables. It fits one scalar t per ancilla using exact rational least squares:

    P_geometry approximately (1-t) P_nominal-zero + t P_nominal-one.

| Ancilla | Fitted t | Residual total variation distance |
|---|---:|---:|
| q4 | 0.470621 | 0.009298 |
| q11 | 0.486096 | 0.004415 |
| q6 | 0.556752 | 0.003045 |

The fit uses only each ancilla's two reported bits, not the data-qubit/ancilla joint
projector observable. It uses the same data it describes and has no significance verdict. Its t is a
mixture coefficient, not an identified excited population. Nevertheless, the small
empirical residuals show why large raw disagreement does not by itself establish large
state disturbance: an empirical asymmetric joint-response segment describes these tables
closely. Inverting early and terminal control marginals separately also gives similar
coefficients for each ancilla. That agreement motivates testing response-context transfer.

The controls change spectator states, while geometry adds gates and superpositions. Their
response laws are not qualified transferable calibrations. This sensitivity neither
rescues the frozen screen nor establishes the projector prediction, independent errors,
QND behavior, or a physical cause. The fixed t=1/2 residual is retained separately from
the fitted value to expose the distinction between prediction and fit.

## Competing causes and decisive information

| Candidate | What remains compatible | Discriminating information or intervention |
|---|---|---|
| Stored/uploaded wrong circuit | Stored bytes match every submitted source | Executed program identity would extend the checked boundary beyond storage |
| Fixed early-bit permutation/polarity | Ruled out as a complete repair by all 48 alternatives | Physical-operation-identical destination permutation tests a broader reconstruction boundary |
| Sparse-versus-multiplexed assignment | First layer addresses three channels; final layer addresses 17 | Hold preparation, gap and mapping fixed; vary addressed readout set; obtain per-context IQ/threshold calibration |
| Acquisition overlap or electronics recovery | Pulse and integration duration differ; zero explicit gap | First-only versus repeated readout, verified windows, and later-pulse/gap intervention with matching first history |
| Prior-shot carryover | Per-shot timestamps and reset/readout history absent | Repetition/reset history or provider traces; independently varied shot spacing if exposed |
| Population transitions/leakage | Binary labels cannot exclude these mechanisms | Independent state calibration, multilevel IQ or qualified leakage protocol; pulse-power/context intervention |
| Pure Stark/dephasing or simple T1 only | Insufficient under fixed positive preparation/assignment | Ramsey quadratures can test phase dynamics only after readout qualification |
| Drift or stale calibration | Fixed job order and unavailable current calibration | Executed-order records, repeated bracketing, calibration identities and independent treatment blocks |

[Heinsoo et al.](../../notes/papers/1801.07904.md) distinguish multiplexed assignment and
physical dephasing, and characterize preparation-dependent joint assignment rather than
using one scalar error rate. [Sank et al.](../../notes/papers/1606.05721.md) identify
measurement-induced multilevel transitions through power/frequency dependence and
multilevel sensing. Those studies supply mechanisms and instruments, not Tuna parameters.
A decay with programmed gap alone would not identify a resonator lifetime.

## What another hardware run needs

The [destination-invariance candidate](../../design/tuna-readout-destination-invariance.md)
provides a concrete first diagnostic that changes classical destinations while preserving
all local physical instructions. It is generated and locally compiled, but remains
unapproved and statistically unadmitted. It tests a measurement-chain boundary before
assuming that a longer settling gap is a repair.

If destination semantics qualify, isolate q11 with spectators fixed in zero and cross
nominal preparations 0/1 with five schedules: first-only, short-delay terminal-only,
short-gap repeated, long-delay terminal-only, and long-gap repeated. This is ten distinct
circuits before replication. Replace an omitted first measurement with an idle matching
its verified served duration; a guessed 300 or 800 ns value is insufficient. The historical
100-cycle wait requests 2 microseconds and supplies a comparison point, not a proven cure.

Then vary sparse-three versus all-17 readout context independently of spectator excitation.
Only after positive, stable assignment and known timing should Ramsey quadratures, a gap
ladder, and leakage-sensitive measurements test physical mechanisms. Each stage needs its
own source-bound case, qualified precision/dependence model, frozen stopping rules, current
backend/queue/pause/credit checks, and explicit execution approval. The existing authorization
was consumed by the completed qualification; this investigation submits no additional jobs.

Replay diagnostics with `scripts/qi_tuna_readout_diagnostics.py --check` and the linked JSON;
replay the response sensitivity with `scripts/qi_tuna_readout_response_mixture.py --check`
and its linked JSON. The gate ledger binds both artifacts. Primary reading scopes in this
investigation cover Rudinger pp. 2–4, Heinsoo sections IV–V and appendix E, and Sank pp. 1–3.
Private source PDFs remain in the partner document repository.

The [verification receipt](readout-diagnosis-verification.json) records focused checks and
byte comparisons of the original acquired files against the base revision.
