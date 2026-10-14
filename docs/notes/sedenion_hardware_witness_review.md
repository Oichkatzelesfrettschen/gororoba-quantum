# Sedenion hardware witnesses: review of an external proposal

An external proposal argued that a gate-model device can "realize" sedenionic
quantum states, against the conjecture that no experiment can. A qubit
register encodes sedenion arithmetic, not sedenion amplitudes: the device
composes complex unitaries associatively, and each basis left multiplication
L_{e_m} is a signed permutation on four qubits,
L_{e_m} e_x = cd_sign(m, x) e_{m xor x}. Hardware measures where that
encoding fails to be an algebra homomorphism (the associator, through
W = L_{e_i e_j}^{-1} L_{e_i} L_{e_j}) and where L_a has a kernel (zero
divisors). Those two failures are the operational content of a sedenion
witness; neither "realized" nor "cannot be realized" has a meaning beyond
them.

[scripts/octonion_structure_checks.py](../../scripts/octonion_structure_checks.py)
(`left_multiplication_products`) gates every exact value below, and
[scripts/design_c_hardware_verdict.py](../../scripts/design_c_hardware_verdict.py)
gates the measured Design C verdicts.

## Proposal components against the repository

| Component | Status | Repository artifact |
|---|---|---|
| Associator interferometer on three 4-qubit registers | exists in a smaller form | Design A ([DESIGN_NOTES.md](../../gororoba_quantum/DESIGN_NOTES.md)): three qubits, no ancilla, all 21 octonion pairs read as Fano Z-strings; Design C: Walsh spectra of the associator phase at D = 8, 16, 32 |
| Zero-divisor annihilation circuit | exists as a one-ancilla LCU | Design B: (L_{e_i} + L_{e_j}) / 2 on (e_k + s e_l) / sqrt(2), P(anc = 0) = &#124;ab&#124;^2 / 8; Design D: the phase-resolved fringe (1 - s cos phi) / 2, checked for all 168 zero-divisor pairs |
| Branch-signed coherence estimator | exists | [coherence_window.py](../../gororoba_quantum/coherence_window.py): (-1)^b0-weighted rho_{01,10} after the N = 21 orbit round |
| Multiplication gate as a CZ network | refuted | the bivariate sign (i, j) -> cd_sign(i, j) has algebraic degree log2(D), 4 at D = 16; Design B compiles its degree-4 sign diagonal through DiagonalGate |
| Classical-shadow associator estimation | not adopted | a random-Pauli shadow's variance grows as 3^w with observable weight w; Designs A to D read each associator or annihilator observable from one circuit |
| Box-kite frustration gap as a contextuality witness | refuted | F is a classical function of the vertex phases; the [structure note](octonion_structure_checks.md) states that the 4-versus-3 gap is a shared-parameter benchmark and no Bell or contextuality inequality |

## Corrections

| Proposal statement | Exact value |
|---|---|
| (e1 + e10)(e2 - e13) = 0 | (e1 + e10)(e2 - e13) = e3 + e7 + e8 - e12, norm squared 4 |
| Ann(e1 + e10) = span{e2 - e13, e3 + e12, e4 - e15, e5 + e14} | Ann(e1 + e10) = span{e4 - e15, e5 + e14, e6 - e13, e7 + e12}, its four corpus partners; e2 - e13 and e3 + e12 are not annihilated |
| U_CD &#124;X>&#124;Y>&#124;0> = 0 for a zero divisor | a unitary preserves norm; the product appears as an amplitude only after post-selection, which Design B's ancilla supplies |
| R_ZD = sum_k P(B = k) for the zero-divisor pair over the same sum for an octonion pair | both sums equal 1 for every input, so R_ZD = 1 identically; the discriminating quantity is Design B's P(anc = 0), 0 for (e1 + e10)(e4 - e15) and 1 for the sign-flipped (e1 + e10)(e4 + e15) |
| octonion pair (e1 + e2), (e3 - e4) as the control | its product norm is multiplicative (4 = 2 x 2), but it uses other indices and another circuit; Design B's bright control flips one sign on the same indices and shares the compiled circuit, so the ratio compares one set of qubits |
| Heron native basis {ECR, RZ, SX, X}, readout error about 11 percent | ibm_fez and ibm_kingston list cz, rz, sx and x; median readout error 0.0106 (ibm_fez) and 0.0085 (ibm_kingston) at their 2026-10-13 22:29 and 22:42 PDT calibrations |

The proposal's correct statements are gated or recorded already: 84
elements e_i + t e_j are zero divisors (42 index pairs, both signs); the
associator is nonzero on 1848 of the 4096 ordered basis triples at D = 16
and 168 of 512 at D = 8 (the open_gororoba cocycle-defect count); L_(e1 + e10)
has rank 12 of 16; Delta is invariant under the pure embedding; and the
associator slices span RM(1, 3), whose Construction A is E8.

## Associator spectra measured on ibm_fez

Design C ran inside the ripple campaign on ibm_fez (calibration 2026-10-12
19:20 PDT, 4096 shots per spectrum,
[measured-ripple.json](../../results/ripple/measured-ripple.json)). Its
falsifier asks that the measured Walsh distribution sit closer in total
variation distance to the true prediction than to the flip and omit
controls by more than the shot-noise TVD (99th percentile of 2000 seeded
resamples):

| D, pair | TVD to true | to flip | to omit | shot noise | verdict |
|---|---|---|---|---|---|
| 8, (1, 4) | 0.127 | 0.310 | 0.936 | 0.015 | resolved |
| 16, (1, 8) | 0.194 | 0.218 | 0.863 | 0.032 | not resolved |
| 32, (1, 16) | 0.268 | 0.334 | 0.842 | 0.039 | resolved |

Both distances move with the sample, so twice the shot-noise TVD bounds the
margin conservatively; under that bound only the octonion spectrum at D = 8
is resolved. The sedenion spectrum at D = 16 does not separate from its flip
control on this device. That makes the sedenion-specific evidence on
hardware incomplete: the D = 32 margin of 0.066 and the zero-divisor
witness below are the open measurements.

## Hardware test and price

The `zero_divisor_fringe` group carries Design B's dark and bright witnesses,
Design D's eight-phase sweep and their mirror twins: 14 static PUBs on five
qubits. A submit-free dry run at ibm_fez calibration 2026-10-13 22:42 PDT
placed three replicas on layout [3, 16, 2, 4, 23] at 40 to 42 CZ. The
calibration noise model predicts P(anc = 0) = 0.084 dark and 0.920 bright,
ratio 0.092 (0.008 after mirror rescaling), and a fringe visibility of 0.843
(0.997 rescaled) at phase -0.002 rad. The planner's cost model (shots times
the 250 us repetition delay, plus 2.3 s per job) prices one static job at
about 17 s at 4096 shots and about 9.6 s at 2048.

A dark-to-bright ratio not significantly below 1, or a fringe phase away
from zero, refutes the zero-divisor witness on that device; a ratio near the
model's 0.09 with the fringe intact shows the zero-divisor interference the
sedenion product predicts, through the encoding above. No zero-divisor
circuit in this repository has run on hardware: the written static case
(results/live/2026-10-11T203535.690679Z) awaits approval, and a fresh dry run
and case precede any submission.

## Provenance

The proposal reached this repository as pasted text from another agent.
Registry items it lists for open_gororoba (claims, experiment identifiers,
upstream issues) belong to that repository.
