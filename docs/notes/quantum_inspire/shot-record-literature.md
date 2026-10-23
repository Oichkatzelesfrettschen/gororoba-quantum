# Tuna-17 shot-record literature

The retained per-shot raw outcome lists of Tuna-17 jobs raise two questions
that the source library has to ground. First, CZ-ladder circuits show a sharp
periodic line at about 0.0200 cycles per shot (period about 49.95 shots, third
harmonic present) whose amplitude grows with the CZ count and appears
common-mode across distant qubit pairs; readout and single-qubit circuits show
no line. Second, one qubit's |1> misassignment differs between an
all-qubits-excited calibration and the witness circuit. The sources below are
the ones registered for these questions. Each has a note in `docs/notes/`
that binds its bytes and reading scope in [SOURCES.json](../../SOURCES.json).
This note claims no mechanism for the line. It lists what each candidate
predicts and which measurement would test the prediction.

Tag convention: [P] marks a statement the source makes; [I] marks inference
from the sources combined with the retained records.

## Converting cycles per shot to hertz

A line at f cycles per shot is f / T_shot hertz for a constant shot interval
T_shot, and a record of N shots resolves frequency steps of 1 / N cycles per
shot ([Proctor et al.](../papers/1907.13608.md) state that conversion to hertz needs
the actual sample timing and that a transform index is only a basis-function
index).

- [I] At N = 16384 shots the resolution is 6.1e-5 cycles per shot, so a period
  of 49.95 shots and a period of exactly 50 shots are not separated by one
  record.
- [I] A source locked to wall-clock time moves in cycles per shot when T_shot
  changes, and a source locked to the shot count does not. The retained
  readout ring-down arms already vary T_shot: they differ only in a wait of
  tau cycles of 20 ns. Their peak frequency rises with tau at 50.4 +- 4.0 Hz
  over 31 jobs with one intercept per batch, 12.6 standard errors from the
  shot-locked 0 Hz and 0.1 from 50 Hz ([tuna-17.md](tuna-17.md), claim
  `qi-tuna17-shot-record-50hz-line`). At 50 Hz the observed 0.0200 to 0.0202
  cycles per shot puts one shot at 402.9 to 404.6 us in the ring-down circuits
  and 400.7 us in the follow series. The fitted 0.51 ms per
  shot of [usage.md](usage.md) therefore prices job execution time, about
  0.1 ms per shot beyond the repetition period, and does not measure the
  interval between shots.

## 1. Flux-pulsed CZ gates and their sensitivity to flux amplitude and noise

Sources: [Rol et al. 2019, arXiv 1903.02492](../papers/1903.02492.md),
[Negirneac et al. 2021, arXiv 2008.07411](../papers/2008.07411.md),
[Marques et al. 2022, arXiv 2102.13071](../papers/2102.13071.md).

What they establish:

- [P] A CZ gate displaces one transmon 0.5-1 GHz below its flux sweetspot so
  that |11> reaches the |02> avoided crossing; away from the sweetspot a small
  amplitude change changes the qubit frequency strongly, so the acquired phase
  is very sensitive to flux-line distortions (Rol).
- [P] The Net Zero bipolar pulse makes the conditional phase first-order
  insensitive to a DC flux offset (second-order sensitive, Rol Fig. 3) and
  adds an echo against low-frequency flux noise; predistortion plus Net Zero
  removes history dependence on the timescales tested (Rol Fig. 2). Residual
  fidelity loss is attributed to high-frequency flux noise.
- [P] The sudden Net Zero pulse has a regular conditional-phase and leakage
  landscape in two amplitudes A and B, and the AWG time resolution (about 1 ns)
  against a 0.5-1 GHz detuning quantizes the phase increments (Negirneac).
- [P] The Surface-7 processor of the same lab runs 60 ns CZ layers interleaved
  with 540 ns ancilla readout for up to 15 cycles, with a flux line per
  transmon (Marques).
- [I] A periodic amplitude or flux disturbance of relative size e on the
  pulse produces a conditional-phase change of about (d phi / dA) A e per
  gate. The slope d phi / dA is read from the (A, B) landscape at the operating
  point. If the per-gate errors add coherently along a ladder, the induced
  population modulation grows with the CZ count; if they add incoherently, it
  grows with the square root. Both forms are testable on the ladder family.
- [I] Idle qubits at the sweetspot are second-order sensitive to flux, so a
  flux-line disturbance leaves readout and single-qubit circuits nearly
  untouched. This matches the absence of the line there and does not by
  itself identify the source.

What the literature does not settle:

- Whether Tuna-17 uses a Net Zero or sudden Net Zero pulse, its pulse
  amplitudes, its detuning or its sweetspot bias is not stated in any
  registered paper. Those values live in the Quantum Inspire pages the repository
  retains ([tuna-17.md](tuna-17.md)) and in the unpublished calibration.
- No source measures the conditional phase against a periodic amplitude
  modulation, and none reports a periodic line in shot order.
- A common-mode line across distant pairs needs a shared source. The sources
  describe one flux line per transmon, so a shared source would sit in a common
  supply, reference clock or ground; the papers do not say which.

## 2. Quantum Inspire platform and Tuna device sources

Sources: [Fu et al. 2017, arXiv 1708.07677](../papers/1708.07677.md),
[Fu et al. 2019, arXiv 1808.02449](../papers/1808.02449.md),
[van der Schoot et al. 2023, arXiv 2310.01120](../papers/2310.01120.md), with
[Marques et al.](../papers/2102.13071.md) above for the lab's device lineage.

What they establish:

- [P] The QuTech control microarchitecture QuMA attaches events to timing
  labels on a timeline with a 5 ns cycle time and fires them when the timer
  reaches the label; eQASM specifies timing points explicitly (QWAIT, QWAITR).
  Intra-shot timing is hardware-timed by design.
- [P] A third-party study ran component, system and application metrics on the
  Starmon-5 backend through the Quantum Inspire cloud API, reporting qubit
  coherence, readout fidelity and a 25 x 25 assignment matrix, and noting that
  the device drifts and is retuned (van der Schoot).
- [I] A hardware-timed sequencer places a line at a fixed wall-clock offset
  only through something outside the intra-shot timeline. The interval between
  shots is set by the shot loop (repetition scheduling, initialization time
  and any host-side wait), which none of the papers characterizes for Quantum
  Inspire.

What the literature does not settle:

- The arXiv search run for this registration (title and abstract queries for
  Quantum Inspire, Tuna-5, Tuna-9, Tuna-17 and Starmon) found no QuTech paper
  describing the platform or any Tuna chip. Search recall is limited, so this
  is an absence of retrieval and not a proof that no such paper exists. The
  Tuna facts the repository relies on come from Quantum Inspire's own pages
  ([knowledge-base.md](knowledge-base.md), [tuna-17.md](tuna-17.md)), which
  are mutable.
- The relation of the Tuna-17 chip to the lab's 17-qubit surface-code layout
  is an inference from the device name and the lineage above. The registered
  surface-code paper uses 7 transmons.
- The control hardware of the Tuna systems, its clock and its shot-loop
  implementation are not described in a registered source.

## 3. Noise spectroscopy from time-ordered measurement records

Sources: [Klimov et al. 2018, arXiv 1809.01043](../papers/1809.01043.md),
[Schloer et al. 2019, arXiv 1901.05352](../papers/1901.05352.md),
[Sung et al. 2019, arXiv 1903.01043](../papers/1903.01043.md); already registered:
[Proctor et al., arXiv 1907.13608](../papers/1907.13608.md) (time-ordered outcome
spectra and drift tests) and [Rudinger et al., arXiv 1810.05651](../papers/1810.05651.md)
(context-dependent errors).

What they establish:

- [P] T1 of a transmon fluctuates by up to an order of magnitude in time, and
  the largest fluctuations trace to individual two-level-system defects whose
  frequencies diffuse (2.5 MHz per square-root hour) or switch between
  discrete values; spectroscopic T1 traces take about 15 minutes and show
  abrupt change on that scale (Klimov).
- [P] Long-term interleaved measurement of T1, dephasing and qubit frequency
  on one transmon shows telegraphic burst noise, a spectrum consistent with a
  few single fluctuators on a 1/f background at millihertz frequencies and
  correlations that identify defects near the film edge (Schloer).
- [P] Discrete noise sources leave non-Gaussian signatures, and a flux-qubit
  sensor under control modulation reconstructs both the power spectrum and the
  bispectrum of engineered non-Gaussian dephasing (Sung).
- [P] Klimov assigns weak periodic features of the T1 spectrum to modes of the
  qubit control lines; those features are periodic in qubit frequency and
  not in time.
- [P] The time-ordered outcome spectra of Proctor et al. test for significant
  variation with a discrete cosine transform and multiple-testing control;
  the highest resolvable frequency is set by the sampling rate and the lowest
  by the record length.

What the literature does not settle:

- No registered source reports a sharp periodic line, with harmonics, in the
  shot order of a superconducting-qubit job, and none ties a qubit-record line
  to mains or to a pulse-tube cryocooler. A single arXiv abstract query for
  50 Hz lines in transmon data returned nothing; the absence is a search
  result and not a negative finding.
- The TLS and 1/f literature covers hours to millihertz. A line at 0.02 cycles
  per shot lies at tens of hertz for shot intervals near half a millisecond,
  five orders of magnitude above the Schloer band.

### Candidate mechanisms and the measurement each invites

The table lists predictions as they follow from the sources and the retained
observation; it does not rank the candidates.

| Candidate | Predicts | Measurement that tests it |
| --- | --- | --- |
| Mains pickup on flux lines (wall-clock line) | Line frequency in Hz fixed; in cycles per shot proportional to 1 / T_shot; odd harmonics for a distorted or clipped waveform; amplitude proportional to the flux sensitivity d phi / dA of the CZ; phase random from job to job unless the shot loop locks to the line | Repeat the ladder with deliberate `wait` padding to change T_shot and track the line in cycles per shot; compare phase across jobs; measured: the ring-down wait ladder gives 50.4 +- 4.0 Hz in wall-clock time |
| Control-stack sequencer or shot-loop timing (shot-count line) | Line at an exact integer period in shots, independent of T_shot and of the circuit; harmonics at exact multiples; may follow a batch or buffer size | Same wait-padding scan (line stays at the same cycles per shot); vary shots per job and per batch and check whether the period follows a count; check for a line in circuits of equal duration with no flux pulse (the readout and single-qubit circuits already show none) |
| Pulse-tube or other mechanical vibration | Line fixed in Hz with a frequency near the cryocooler stroke and its harmonics; coupling through flux-line or wire motion, so amplitude depends on the sensitivity of each gate's phase and not on the CZ count alone | Convert the line to Hz using T_shot and compare with the cooler frequency of the installation, which the platform pages do not publish; look for a line in idle (wait-only) circuits, where Klimov-type frequency noise would show |
| TLS telegraph noise and 1/f flux noise | Lorentzian or 1/f spectrum at millihertz to hertz, qubit-specific, present in idle and readout circuits as frequency or T1 jumps, not a sharp line with a third harmonic and not common-mode across distant pairs | Spectrum of the idle-circuit record; cross-spectrum between distant qubits; the shape of the peak against a Lorentzian |

[I] A third harmonic with a sharp fundamental indicates a periodic but
non-sinusoidal drive; the table's first two rows can each produce it, and the
third harmonic alone does not discriminate between them.

## 4. Readout crosstalk and context-dependent assignment error

Sources: [Bravyi et al. 2021, arXiv 2006.14044](../papers/2006.14044.md),
[Nation et al. 2021, arXiv 2108.12518](../papers/2108.12518.md),
[Heinsoo et al. 2018, arXiv 1801.07904](../papers/1801.07904.md),
[Geller 2020, arXiv 2002.01471](../papers/2002.01471.md),
[Sank et al. 2016, arXiv 1606.05721](../papers/1606.05721.md), and the
Starmon-5 study [van der Schoot et al.](../papers/2310.01120.md); already
registered: [Sarovar et al., arXiv 1908.09855](../papers/1908.09855.md) (crosstalk
detection) and [Rudinger et al.](../papers/1810.05651.md).

What they establish:

- [P] A tensor-product noise model carries 2n single-qubit rates; a
  continuous-time Markov (CTMP) model captures readout cross-talk, which the
  paper attributes in part to frequency multiplexing (Bravyi).
- [P] The M3 method corrects in the subspace of observed bit strings and
  returns error bounds (Nation). Its calibration grows at most linearly in the
  qubit count for the tensored single-qubit matrices; the reduced-subspace
  solver can also take correlated assignment elements, but those need their own
  correlated channel and calibration circuits, whose cost the tensored figure
  does not cover.
- [P] On a multiplexed device with Purcell filters, simultaneous and
  individual readout errors differ by under 1 percent for five qubits
  (Heinsoo).
- [P] In a biased measurement model the nonideal readout equals an ideal
  projective measurement followed by a classical Markov matrix Gamma. The
  prepare-and-measure transition matrix T equals Gamma only when the
  classical basis states are prepared with negligible error (Geller).
- [P] Readout photon number above a threshold drives resonant transitions out
  of the qubit subspace (Sank).
- [P] A published all-qubits-excited calibration on a Quantum Inspire device
  (|11111> on Starmon-5) returns per-qubit fidelities of 96.4-98.4 percent,
  conflates preparation and measurement error by the paper's own statement, and
  varies from repetition to repetition more than a stable system would
  (van der Schoot).
- [I] An all-excited calibration therefore folds the preparation error of
  every X gate, any residual excitation of neighbors and the readout of n
  excited qubits into one apparent |1> misassignment per qubit. A witness
  circuit that ends in a different state pattern, or after CZ gates that leak
  with about 0.1 percent probability per gate (Rol, Negirneac) and read leaked
  |2> as |1>, has a different composite error. The sources support the
  existence of each term and quantify none of them for Tuna-17.

What the literature does not settle:

- None of the registered papers compares the |1> misassignment of one qubit
  between an all-excited calibration and an algorithm circuit on the same
  device in one batch. The size of the Tuna-17 difference against these
  references is therefore not predicted by any source.
- Readout power, resonator detuning and multiplexing layout of Tuna-17 are
  not published in the registered sources, so Sank-type transitions and
  Heinsoo-type crosstalk cannot be bounded for it from the literature.
- Time-dependence enters as drift between calibration and witness; Proctor
  and van der Schoot make it plausible and do not give a Tuna-17 drift rate.

Candidate contributions to the difference and the check for each:

| Candidate | Predicts | Measurement that tests it |
| --- | --- | --- |
| Preparation error in the all-excited state | Calibration error for state 1 larger than the single-qubit error for state 1 with the other qubits idle | Calibrate each qubit alone and with graded numbers of neighbors excited, same batch |
| Readout crosstalk or multiplexing | Misassignment depends on the neighbors' states in a pattern that the 2^n assignment matrix on a qubit subset shows (Bravyi CTMP) | Assignment matrix on the witness's neighborhood, in random state patterns |
| Leakage from the CZ ladder read as state 1 | Excess state-1 counts grows with CZ count and vanishes in circuits without CZ | Same witness with the CZ count varied; a calibration that applies CZ pairs and returns to the ground state |
| Drift between calibration and witness | Difference changes sign or size with the delay between them | Interleave calibration and witness circuits within one batch |
| Measurement-induced transitions | Error depends on readout power and the number of simultaneously read qubits | Not accessible if readout power is not user-set; compare one-qubit and n-qubit simultaneous readout |

## Registered sources

| arXiv | Source | Registry class |
| --- | --- | --- |
| 1903.02492 | Rol et al., Net Zero flux-pulsed CZ | external |
| 2008.07411 | Negirneac et al., sudden Net Zero CZ | external |
| 2102.13071 | Marques et al., Surface-7 error-detecting code | external |
| 1708.07677 | Fu et al., QuMA | external |
| 1808.02449 | Fu et al., eQASM | external |
| 2310.01120 | van der Schoot et al., Starmon-5 metrics on Quantum Inspire | published, CC BY 4.0 |
| 1809.01043 | Klimov et al., T1 fluctuations | external |
| 1901.05352 | Schloer et al., single-fluctuator burst noise | external |
| 1903.01043 | Sung et al., non-Gaussian noise spectroscopy | external |
| 2006.14044 | Bravyi et al., readout mitigation | external |
| 2108.12518 | Nation et al., M3 | published, CC BY 4.0 |
| 1801.07904 | Heinsoo et al., multiplexed readout | external |
| 2002.01471 | Geller, rigorous measurement correction | external |
| 1606.05721 | Sank et al., measurement-induced transitions | external |

Heinsoo et al. is an ETH Zurich paper and is registered for the readout
crosstalk benchmark only; Klimov, Sank, Bravyi, Nation, Schloer, Sung and
Geller come from other labs and describe devices that differ from the Tuna
chips.
